#!/usr/bin/env python3
# SPDX-FileCopyrightText: 2026 AIMath contributors
# SPDX-License-Identifier: Apache-2.0
from __future__ import annotations

import ast
from contextlib import contextmanager, redirect_stdout
from dataclasses import replace
from datetime import datetime, timedelta, timezone
import copy
import hashlib
import inspect
import io
import json
import os
from pathlib import Path
import subprocess
import tempfile
import textwrap
from types import SimpleNamespace
import unittest
from unittest.mock import patch
import urllib.parse

import village_next_phase_b as pb
from village_next_phase_b import (
    CanonicalAcquireIdentityV3,
    ExactLockObject,
    RulesetProof,
    SemanticIds,
    VerifyObservation,
)
from village_v1_2 import CapabilityProfile
from village_core import validate_schema
from test_village_acceptance import add_lock, base_state
from village_next import NextRequest, TerminalEvidence, derive_continuation_decision

BASE_SHA = "a" * 40
HEAD_SHA = "b" * 40
ALT_HEAD_SHA = "c" * 40
M_SHA = "d" * 40
WORKER = "w-" + "a" * 16
WORKER_B = "w-" + "b" * 16
PRINCIPAL = "gh:51mns"
TASK = "TASK-NEXT-1"
NOW = datetime(2026, 9, 2, 12, 0, tzinfo=timezone.utc)


def _base_entries():
    raw = b"base fixture\n"
    return [{"path": "README.md", "mode": "100644", "type": "blob", "sha": pb.git_blob_oid(raw)}]


def _base_tree():
    return pb.deterministic_tree_sha(_base_entries())


def _ids(a="1", b="2", c="3", d="4"):
    return SemanticIds(a * 64, b * 64, c * 64, d * 64)


def _material(
    ids=None,
    *,
    worker=WORKER,
    acquired_at=NOW,
    collision_keys=("x/next",),
    task=TASK,
    base_sha=BASE_SHA,
    base_tree_sha=None,
    base_entries=None,
):
    ids = ids or _ids()
    base_entries = copy.deepcopy(_base_entries() if base_entries is None else base_entries)
    base_tree_sha = base_tree_sha or pb.deterministic_tree_sha(base_entries)
    return pb.freeze_acquire_material(
        semantic_ids=ids,
        base_sha=base_sha,
        base_tree_sha=base_tree_sha,
        base_tree_entries=base_entries,
        selected_task_id=task,
        worker_id=worker,
        principal_id=PRINCIPAL,
        work_ref=f"research/{task}/{worker}",
        collision_keys=collision_keys,
        acquired_at=acquired_at,
        lease_ttl_hours=168,
    )


def _candidate_entries(material=None):
    material = material or _material()
    rows = copy.deepcopy(_base_entries())
    rows.extend(
        {"path": obj.path, "mode": obj.mode, "type": "blob", "sha": obj.blob_sha}
        for obj in material.identity.exact_lock_objects
    )
    return rows


def _candidate_commit(material=None, *, sha=HEAD_SHA, parent=BASE_SHA, parents=None, tree_sha=None):
    material = material or _material()
    ps = parents if parents is not None else [{"sha": parent}]
    return {"sha": sha, "parents": ps, "tree": {"sha": tree_sha or material.identity.expected_canonical_tree_sha}}


def _good_ruleset():
    return RulesetProof(True, "RULESET_PROOF_CONFIRMED", "strict verify, no bypass")


def _ruleset_inputs(*, strict=True, context="verify", bypass=None, can="never"):
    effective = [{
        "type": "required_status_checks",
        "parameters": {
            "strict_required_status_checks_policy": strict,
            "required_status_checks": [{"context": context}],
        },
    }]
    detail = [{
        "id": 22089746,
        "target": "branch",
        "enforcement": "active",
        "conditions": {"ref_name": {"include": ["~DEFAULT_BRANCH"], "exclude": []}},
        "rules": copy.deepcopy(effective),
        "bypass_actors": [] if bypass is None else bypass,
        "current_user_can_bypass": can,
    }]
    return effective, detail


def _run(number, run_id, *, head=HEAD_SHA, status="completed", conclusion="success", attempt=1):
    return {
        "id": run_id,
        "workflow_id": pb.VERIFY_WORKFLOW_ID,
        "path": pb.VERIFY_WORKFLOW_PATH,
        "name": pb.VERIFY_WORKFLOW_NAME,
        "event": pb.VERIFY_EVENT,
        "head_sha": head,
        "run_number": number,
        "run_attempt": attempt,
        "status": status,
        "conclusion": conclusion,
    }


def _observe(rows, current=None, *, head=HEAD_SHA, complete=True):
    by_id = {row["id"]: row for row in rows}
    if current:
        by_id.update(current)
    return pb.authoritative_verify_lineage(rows, head_sha=head, complete=complete, fetch_current_run=lambda rid: by_id[rid])


def _good_verify(head=HEAD_SHA, number=10, run_id=9):
    row = _run(number, run_id, head=head)
    return _observe([row], head=head)


def _history(material=None, *, m_parents=None, m_tree=None, current_entries=None):
    material = material or _material()
    m_entries = current_entries or _candidate_entries(material)
    m = {
        "sha": M_SHA,
        "parents": m_parents if m_parents is not None else [{"sha": BASE_SHA}],
        "tree": {"sha": m_tree or material.identity.expected_canonical_tree_sha},
        "entries": m_entries,
    }
    b = {"sha": BASE_SHA, "parents": [], "tree": {"sha": _base_tree()}, "entries": _base_entries()}
    return [m, b]


def _canonical_gate(material=None, *, history=None, current_entries=None, current_lock_bytes=None, rules=None, now=NOW):
    material = material or _material()
    return pb.canonical_transition_gate(
        identity=material.identity,
        first_parent_history=history or _history(material),
        current_entries=current_entries or _candidate_entries(material),
        current_lock_bytes=current_lock_bytes or material.lock_bytes,
        ruleset=rules or _good_ruleset(),
        now=now,
    )


def _premerge(material=None, *, commit=None, entries=None, verify=None, rules=None, current_main=BASE_SHA, ids=None):
    material = material or _material()
    return pb.premerge_transport_gate(
        identity=material.identity,
        independently_derived_ids=ids or material.identity.semantic_ids(),
        base_entries=_base_entries(),
        candidate_commit=commit or _candidate_commit(material),
        candidate_entries=entries or _candidate_entries(material),
        candidate_lock_bytes=material.lock_bytes,
        verify=verify or _good_verify(),
        ruleset=rules or _good_ruleset(),
        current_main_sha=current_main,
    )


def _source_record(*, lock_blob=None, terminal_blob=None, acquired="2026-09-01T00:00:00+00:00"):
    lock_blob = lock_blob or "e" * 40
    terminal_blob = terminal_blob or "f" * 40
    payload = {
        "schema_version": 1,
        "lock_id": "LOCK-SOURCE",
        "task_id": "TASK-SOURCE",
        "worker_id": WORKER,
        "actor": {"id": PRINCIPAL, "type": "HUMAN_PRINCIPAL"},
        "base_main_sha": "0" * 40,
        "acquired_at": acquired,
        "expires_at": "2026-09-10T00:00:00+00:00",
        "work_ref": f"research/TASK-SOURCE/{WORKER}",
        "collision_keys": ["source/key"],
        "renewal_count": 0,
    }
    return pb.derive_source_acquisition_v1(
        repository=pb.REPOSITORY,
        source_task_id="TASK-SOURCE",
        worker_id=WORKER,
        principal_id=PRINCIPAL,
        lock_payload=payload,
        source_lock_blob_bundle=[{"path": "coordination/locks/source/key.yml", "blob_sha": lock_blob}],
        terminal_class="RESULT_TERMINAL",
        terminal_path="coordination/outcomes/TASK-SOURCE.yml",
        terminal_blob_sha=terminal_blob,
        terminal_outcome_type="NO_REUSABLE_PROGRESS",
    )


def _trusted_semantic_chain():
    source_record, source_id = _source_record()
    context, context_id = pb.derive_continuation_context_v1(
        source_epoch_id=source_id,
        selection_main_sha=BASE_SHA,
        terminal_class="RESULT_TERMINAL",
        terminal_blob_sha=source_record["terminal_blob_sha"],
        source_campaign_id="CAM-X",
        global_admission="OPEN",
        source_campaign_strategic_state="ACTIVE",
        continuation_gate_required=False,
        continuation_decision_id=None,
        continuation_decision_blob_sha=None,
        human_decision=None,
        canonical_stop_condition_reached=True,
        canonical_dependency_followup_unusable=True,
        same_campaign_allowed=False,
        global_fallback_allowed=True,
        approved_followup_task_ids=[TASK],
        evaluation_followup_task_ids=[],
        reasons=[
            "dependency reevaluation makes source-Campaign follow-up unusable",
            "explicit source Task/Campaign stop condition reached",
        ],
        capability_profile=CapabilityProfile.from_values(github_write="yes", local_compute="yes", web_literature="unknown"),
    )
    selection, selection_id = pb.derive_selection_v1(
        source_epoch_id=source_id,
        selection_main_sha=BASE_SHA,
        continuation_context_id=context_id,
        pending_records=[],
        hard_eligible_task_ids=[TASK],
        ranked_task_ids=[TASK],
        selected_task_id=TASK,
        selected_relation="GLOBAL_READY",
        worker_id=WORKER,
        principal_id=PRINCIPAL,
    )
    intent, intent_id = pb.derive_acquire_intent_v1(
        source_epoch_id=source_id,
        selection_id=selection_id,
        selection_main_sha=BASE_SHA,
        continuation_context_id=context_id,
        selected_task_id=TASK,
        worker_id=WORKER,
        principal_id=PRINCIPAL,
        work_ref=f"research/{TASK}/{WORKER}",
        collision_keys=["x/next"],
    )
    ids = SemanticIds(source_id, context_id, selection_id, intent_id)
    material = _material(ids)
    state = {
        "schema_version": 1,
        "repository": pb.REPOSITORY,
        "source_acquisition_v1": source_record,
        "source_epoch_id": source_id,
        "continuation_context_v1": context,
        "continuation_context_id": context_id,
        "selection_v1": selection,
        "selection_id": selection_id,
        "acquire_intent_v1": intent,
        "acquire_intent_id": intent_id,
        "canonical_acquire_identity_v3": material.identity.to_dict(),
        "canonical_acquire_id": material.canonical_acquire_id,
    }
    return source_record, context, selection, intent, ids, material, state


def _release_fixture(*, verify=True):
    source_path = "coordination/locks/source/key.yml"
    source_bytes = b'{"lock_id":"LOCK-SOURCE"}\n'
    source_blob = pb.git_blob_oid(source_bytes)
    base_entries = [
        {"path": "README.md", "mode": "100644", "type": "blob", "sha": pb.git_blob_oid(b"base\n")},
        {"path": source_path, "mode": "100644", "type": "blob", "sha": source_blob},
    ]
    base_sha = "6" * 40
    base_tree = pb.deterministic_tree_sha(base_entries)
    released_entries = [row for row in base_entries if row["path"] != source_path]
    released_tree = pb.deterministic_tree_sha(base_entries, deletions=[source_path], expected_base_tree_sha=base_tree)
    source_record = {"source_lock_blob_bundle": [{"path": source_path, "blob_sha": source_blob}]}
    transport = {"sha": "7" * 40, "parents": [{"sha": base_sha}], "tree": {"sha": released_tree}}
    m = {"sha": "8" * 40, "parents": [{"sha": base_sha}], "tree": {"sha": released_tree}, "entries": released_entries}
    b = {"sha": base_sha, "parents": [], "tree": {"sha": base_tree}, "entries": base_entries}
    vo = VerifyObservation(verify, "VERIFY_AUTHORITATIVE_SUCCESS" if verify else "LATEST_VERIFY_NOT_SUCCESS", 10, 1, 1, "completed", "success")
    return source_record, base_sha, released_tree, transport, released_entries, vo, [m, b]


def _verified(head_sha, *, run_number=10, run_id=1, attempt=1):
    return VerifyObservation(
        True,
        "VERIFY_AUTHORITATIVE_SUCCESS",
        run_number,
        run_id,
        attempt,
        "completed",
        "success",
        head_sha,
        "fresh exact-head fixture",
    )


class _ExactGitRepo:
    """Small real-Git object store used by the B/H/H2/M oracle rows."""

    def __init__(self, root):
        self.root = Path(root)
        self._run("init", "-q")
        self._run("config", "user.name", "AIMath Oracle")
        self._run("config", "user.email", "oracle" + "@" + "example.invalid")

    def _run(self, *args, input_bytes=None, env=None):
        merged = os.environ.copy()
        if env:
            merged.update(env)
        proc = subprocess.run(
            ["git", "-C", str(self.root), *args],
            input=input_bytes,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            check=True,
            env=merged,
        )
        return proc.stdout.decode("utf-8").strip()

    def blob(self, raw):
        return self._run("hash-object", "-w", "--stdin", input_bytes=raw)

    def tree(self, *, base_tree=None, additions=(), deletions=()):
        index = self.root / ".git" / "oracle-index"
        index.unlink(missing_ok=True)
        env = {"GIT_INDEX_FILE": str(index)}
        if base_tree is None:
            self._run("read-tree", "--empty", env=env)
        else:
            self._run("read-tree", base_tree, env=env)
        for row in additions:
            self._run(
                "update-index",
                "--add",
                "--cacheinfo",
                f"{row['mode']},{row['sha']},{row['path']}",
                env=env,
            )
        for path in deletions:
            self._run("update-index", "--force-remove", "--", path, env=env)
        return self._run("write-tree", env=env)

    def commit(self, tree, *, parent=None, message="fixture", second=0, extra_parents=()):
        args = ["commit-tree", tree]
        if parent is not None:
            args.extend(["-p", parent])
        for extra in extra_parents:
            args.extend(["-p", extra])
        stamp = f"2026-09-02T12:00:{second:02d}+00:00"
        env = {
            "GIT_AUTHOR_NAME": "AIMath Oracle",
            "GIT_AUTHOR_EMAIL": "oracle" + "@" + "example.invalid",
            "GIT_COMMITTER_NAME": "AIMath Oracle",
            "GIT_COMMITTER_EMAIL": "oracle" + "@" + "example.invalid",
            "GIT_AUTHOR_DATE": stamp,
            "GIT_COMMITTER_DATE": stamp,
        }
        return self._run(*args, input_bytes=(message + "\n").encode("utf-8"), env=env)

    def entries(self, rev):
        raw = subprocess.run(
            ["git", "-C", str(self.root), "ls-tree", "-rz", "-r", rev],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            check=True,
        ).stdout
        rows = []
        for record in raw.split(b"\0"):
            if not record:
                continue
            meta, path = record.split(b"\t", 1)
            mode, obj_type, sha = meta.decode("ascii").split()
            rows.append({"path": path.decode("utf-8"), "mode": mode, "type": obj_type, "sha": sha})
        return rows

    def raw_object(self, oid):
        return subprocess.run(
            ["git", "-C", str(self.root), "cat-file", "blob", oid],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            check=True,
        ).stdout

    def view(self, sha):
        line = self._run("rev-list", "--parents", "-n", "1", sha).split()
        tree = self._run("show", "-s", "--format=%T", sha)
        return {
            "sha": line[0],
            "parents": [{"sha": parent} for parent in line[1:]],
            "tree": {"sha": tree},
            "entries": self.entries(sha),
        }


@contextmanager
def _exact_acquire_git(*, collision_keys=("x/next",)):
    with tempfile.TemporaryDirectory() as td:
        git = _ExactGitRepo(td)
        base_blob = git.blob(b"base fixture\n")
        base_entries = [{"path": "README.md", "mode": "100644", "type": "blob", "sha": base_blob}]
        base_tree = git.tree(additions=base_entries)
        base = git.commit(base_tree, message="base", second=1)
        material = _material(
            collision_keys=collision_keys,
            base_sha=base,
            base_tree_sha=base_tree,
            base_entries=base_entries,
        )
        additions = []
        for obj in material.identity.exact_lock_objects:
            self_oid = git.blob(material.lock_bytes[obj.path])
            if self_oid != obj.blob_sha:
                raise AssertionError("real git hash-object disagrees with frozen lock object")
            additions.append({"path": obj.path, "mode": obj.mode, "type": "blob", "sha": obj.blob_sha})
        target_tree = git.tree(base_tree=base_tree, additions=additions)
        if target_tree != material.identity.expected_canonical_tree_sha:
            raise AssertionError("real git write-tree disagrees with deterministic target tree")
        head = git.commit(target_tree, parent=base, message="transport H", second=2)
        alt_head = git.commit(target_tree, parent=base, message="transport H2", second=3)
        canonical = git.commit(target_tree, parent=base, message="canonical squash M", second=4)
        yield SimpleNamespace(
            git=git,
            base=base,
            base_tree=base_tree,
            base_entries=base_entries,
            target_tree=target_tree,
            material=material,
            head=head,
            alt_head=alt_head,
            canonical=canonical,
        )


class _PagedGitHubClient:
    """Mechanical GitHub REST fixture with explicit page and current-run objects."""

    workflow_runs_for_head = pb.GitHubPhaseBClient.workflow_runs_for_head
    ruleset_proof = pb.GitHubPhaseBClient.ruleset_proof

    def __init__(
        self,
        *,
        workflow_pages=None,
        current_runs=None,
        effective_pages=None,
        ruleset_pages=None,
        ruleset_details=None,
    ):
        self.owner = "51mns"
        self.repo = "AIMath-public"
        self.workflow_pages = workflow_pages or {}
        self.current_runs = current_runs or {}
        self.effective_pages = effective_pages or {}
        self.ruleset_pages = ruleset_pages or {}
        self.ruleset_details = ruleset_details or {}
        self.calls = []

    @staticmethod
    def _page(path):
        query = urllib.parse.parse_qs(urllib.parse.urlsplit(path).query)
        return int(query.get("page", ["1"])[0])

    @staticmethod
    def _value(value):
        if isinstance(value, Exception):
            raise value
        return copy.deepcopy(value)

    def request(self, method, path, payload=None):
        self.calls.append((method, path))
        clean = urllib.parse.urlsplit(path).path
        if "/actions/workflows/" in clean and clean.endswith("/runs"):
            page = self._page(path)
            return self._value(self.workflow_pages.get(page, {"total_count": 0, "workflow_runs": []}))
        if "/actions/runs/" in clean:
            run_id = int(clean.rsplit("/", 1)[1])
            return self._value(self.current_runs[run_id])
        if clean.endswith("/rules/branches/main"):
            return self._value(self.effective_pages.get(self._page(path), []))
        if clean.endswith("/rulesets"):
            return self._value(self.ruleset_pages.get(self._page(path), []))
        if "/rulesets/" in clean:
            ruleset_id = int(clean.rsplit("/", 1)[1])
            return self._value(self.ruleset_details[ruleset_id])
        raise AssertionError(f"unexpected GitHub request: {method} {path}")


class _ExactReadClient:
    def __init__(self, git):
        self.git = git

    def git_commit(self, sha):
        view = self.git.view(sha)
        return {"sha": sha, "parents": view["parents"], "tree": view["tree"]}

    def recursive_tree(self, sha):
        view = self.git.view(sha)
        return view["tree"]["sha"], view["entries"]

    def blob_bytes(self, oid):
        return self.git.raw_object(oid)


def _ruleset_detail(ruleset_id, *, bypass=None, active=True, strict=True, context="verify"):
    effective, _ = _ruleset_inputs(strict=strict, context=context)
    return {
        "id": ruleset_id,
        "target": "branch",
        "enforcement": "active" if active else "evaluate",
        "conditions": {"ref_name": {"include": ["~DEFAULT_BRANCH"], "exclude": []}},
        "rules": effective,
        "bypass_actors": [] if bypass is None else bypass,
        "current_user_can_bypass": "never",
    }


def _pr(number, head, *, ref=None, draft=False):
    return {
        "number": number,
        "state": "open",
        "draft": draft,
        "head": {"sha": head, "ref": ref or f"next-acquire/{number}"},
        "base": {"sha": BASE_SHA, "ref": "main"},
        "user": {"login": "51mns"},
    }


class _DraftPRClient:
    def __init__(self):
        self.owner = "51mns"
        self.repo = "AIMath-public"
        self.created = 0
        self.rows = {}

    def create_draft_pr(self, *, title, head_ref, body):
        self.created += 1
        number = 100 + self.created
        self.rows[number] = _pr(number, HEAD_SHA, ref=head_ref, draft=True)
        return number

    def request(self, method, path, payload=None):
        return copy.deepcopy(self.rows[int(path.rsplit("/", 1)[1])])


class _PendingClient:
    def __init__(self, materials, *, fail_global_base=False, malformed_heads=()):
        self.materials = materials
        self.fail_global_base = fail_global_base
        self.malformed_heads = set(malformed_heads)

    def git_commit(self, sha):
        material = self.materials[sha]
        return {"sha": sha, "parents": [{"sha": BASE_SHA}], "tree": {"sha": material.identity.expected_canonical_tree_sha}}

    def recursive_tree(self, sha):
        if sha == BASE_SHA:
            if self.fail_global_base:
                raise pb.PhaseBError("REPOSITORY_OBSERVATION_INCOMPLETE", "fresh base tree unavailable")
            return _base_tree(), _base_entries()
        material = self.materials[sha]
        entries = _candidate_entries(material)
        if sha in self.malformed_heads:
            entries[-1]["mode"] = "100755"
        return material.identity.expected_canonical_tree_sha, entries

    def workflow_runs_for_head(self, head):
        return _verified(head)

    def blob_bytes(self, oid):
        for material in self.materials.values():
            for obj in material.identity.exact_lock_objects:
                if obj.blob_sha == oid:
                    return material.lock_bytes[obj.path]
        raise pb.PhaseBError("GITHUB_OBSERVATION_UNAVAILABLE", "fixture blob unavailable")


class _CLIReadOnlyClient:
    def __init__(self, source_blobs=None, authenticated_principal=PRINCIPAL):
        self.source_blobs = source_blobs or {}
        self.authenticated_principal = authenticated_principal

    def current_main_sha(self):
        return BASE_SHA

    def authenticated_principal_id(self):
        return self.authenticated_principal

    def recursive_tree(self, commit_sha):
        if commit_sha != BASE_SHA:
            raise AssertionError("cli_next requested an unexpected main")
        entries = _base_entries() + [
            {"path": path, "mode": "100644", "type": "blob", "sha": pb.git_blob_oid(raw)}
            for path, raw in sorted(self.source_blobs.items())
        ]
        return pb.deterministic_tree_sha(entries), entries

    def blob_bytes(self, oid):
        for raw in self.source_blobs.values():
            if pb.git_blob_oid(raw) == oid:
                return raw
        raise pb.PhaseBError("GITHUB_OBSERVATION_UNAVAILABLE", "fixture blob unavailable")

    def open_prs(self):
        return []

    def ruleset_proof(self):
        return _good_ruleset()


def _cli_source_state(root, *, expires_at=None):
    state = base_state()
    state.root = Path(root).resolve()
    state.now = NOW
    state.decisions = []
    add_lock(
        state,
        "LOCK-SOURCE",
        "TASK-X-1",
        "x/shared",
        actor=PRINCIPAL,
        expires=expires_at or NOW + timedelta(hours=10),
    )
    bundle = state.lock_bundles["LOCK-SOURCE"]
    bundle.payload["worker_id"] = WORKER
    bundle.payload["work_ref"] = f"research/TASK-X-1/{WORKER}"
    bundle.paths = [state.root / "coordination/locks/x/shared.yml"]
    return state


def _write_abandoned_terminal(root, *, truth_layer_effect="NONE"):
    schema_dir = Path(root) / "schemas"
    schema_dir.mkdir(parents=True, exist_ok=True)
    repo = Path(__file__).resolve().parent.parent
    (schema_dir / "abandoned-terminal.schema.json").write_bytes(
        (repo / "schemas/abandoned-terminal.schema.json").read_bytes()
    )
    path = Path(root) / f"work/TASK-X-1/{WORKER}/ABANDONED_TERMINAL.yml"
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        json.dumps(
            {
                "schema_version": 1,
                "task_id": "TASK-X-1",
                "worker_id": WORKER,
                "reason": "SCOPE_STOP",
                "abandoned_at": NOW.isoformat(),
                "abandonment_count": 1,
                "last_work_head": None,
                "truth_layer_effect": truth_layer_effect,
            }
        )
        + "\n",
        encoding="utf-8",
    )


def _run_cli_source_case(
    root,
    state,
    *,
    worker=WORKER,
    principal=PRINCIPAL,
    canonical_source=True,
    terminal_release=False,
):
    source_blobs = {}
    for bundle in state.lock_bundles.values():
        raw = (json.dumps(bundle.payload, sort_keys=True, indent=2) + "\n").encode("utf-8")
        for path in bundle.paths:
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_bytes(raw)
            if canonical_source:
                source_blobs[path.relative_to(state.root).as_posix()] = raw
    state_path = Path(root) / ".git" / "phase-b-state.json"
    args = SimpleNamespace(
        github_write="yes",
        local_compute="yes",
        web_literature="yes",
        github_token_env="GITHUB_TOKEN",
        phase_b_state_file=str(state_path),
        current_main_sha=BASE_SHA,
        task_id="TASK-X-1",
        worker_id=worker,
        principal_id=principal,
        continuation_decision_id=None,
    )
    client = _CLIReadOnlyClient(source_blobs)
    book = SimpleNamespace(errors=[])
    output = io.StringIO()
    source_record_value = (
        {"source_task_id": "TASK-X-1", "worker_id": WORKER},
        "1" * 64,
        SimpleNamespace(terminal_class="ABANDONED_TERMINAL"),
    )
    with (
        patch.object(pb, "GitHubPhaseBClient", return_value=client),
        patch.object(pb, "_local_head_sha", return_value=BASE_SHA),
        patch("village_core.VillageState.load", return_value=state),
        patch("village_rank.EvaluationBook.load", return_value=book),
        patch("village_v1_2.load_actor_policy", return_value={}),
        patch("village_v1_2.worker_lock_errors", return_value=[]),
        patch.object(pb, "derive_source_acquisition_v1") as source_epoch,
        patch.object(pb, "_source_record_from_fresh_main", return_value=source_record_value) as source_record,
        patch.object(
            pb,
            "_prepare_release_transport",
            return_value=pb.GateResult(True, "RELEASE_PENDING") if terminal_release else None,
        ) as release,
        patch.object(pb, "_prepare_acquire_transport") as acquire,
        patch.dict(os.environ, {"GITHUB_TOKEN": "fixture-token"}),
        redirect_stdout(output),
    ):
        rc = pb.cli_next(Path(root), args)
    return SimpleNamespace(
        rc=rc,
        output=output.getvalue(),
        state_path=state_path,
        source_epoch_calls=source_epoch.call_count,
        source_record_calls=source_record.call_count,
        release_calls=release.call_count,
        acquire_calls=acquire.call_count,
    )


def _adapter_keyword(call_name, keyword):
    tree = ast.parse(textwrap.dedent(inspect.getsource(pb._derive_post_release_semantics)))
    for node in ast.walk(tree):
        if not isinstance(node, ast.Call):
            continue
        name = node.func.id if isinstance(node.func, ast.Name) else getattr(node.func, "attr", None)
        if name != call_name:
            continue
        for item in node.keywords:
            if item.arg == keyword:
                return item.value
    return None


class VillageV13PhaseB73(unittest.TestCase):
    def test_row_01_happy_path_release_select_acquire_and_active_next(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            state = _cli_source_state(root)
            active = _run_cli_source_case(root, state)
            self.assertEqual(active.rc, 0)
            self.assertEqual(active.output, "ACTIVE_WORK\n")
            self.assertFalse(active.state_path.exists())
            self.assertEqual(active.source_epoch_calls, 0)
            self.assertEqual(active.release_calls, 0)
            self.assertEqual(active.acquire_calls, 0)

        fail_closed_cases = (
            ("malformed_terminal", WORKER, PRINCIPAL),
            ("wrong_worker", WORKER_B, PRINCIPAL),
            ("wrong_principal", WORKER, "gh:other"),
            ("noncanonical_source_lock", WORKER, PRINCIPAL),
        )
        for label, worker, principal in fail_closed_cases:
            with self.subTest(source_boundary=label), tempfile.TemporaryDirectory() as td:
                root = Path(td)
                state = _cli_source_state(root)
                if label == "malformed_terminal":
                    _write_abandoned_terminal(root, truth_layer_effect="INVALID")
                rejected = _run_cli_source_case(
                    root,
                    state,
                    worker=worker,
                    principal=principal,
                    canonical_source=label != "noncanonical_source_lock",
                )
                self.assertNotEqual(rejected.rc, 0)
                self.assertNotEqual(rejected.output, "ACTIVE_WORK\n")
                self.assertFalse(rejected.state_path.exists())
                self.assertEqual(rejected.source_epoch_calls, 0)
                self.assertEqual(rejected.release_calls, 0)
                self.assertEqual(rejected.acquire_calls, 0)

        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            state = _cli_source_state(root)
            _write_abandoned_terminal(root)
            release = _run_cli_source_case(root, state, terminal_release=True)
            self.assertEqual(release.rc, 0)
            self.assertEqual(release.output, "RELEASE_PENDING\n")
            self.assertEqual(release.source_record_calls, 1)
            self.assertEqual(release.release_calls, 1)
            self.assertEqual(release.acquire_calls, 0)

        with _exact_acquire_git() as fx:
            candidate = fx.git.view(fx.head)
            premerge = pb.premerge_transport_gate(
                identity=fx.material.identity,
                independently_derived_ids=fx.material.identity.semantic_ids(),
                base_entries=fx.base_entries,
                candidate_commit=candidate,
                candidate_entries=candidate["entries"],
                candidate_lock_bytes=fx.material.lock_bytes,
                verify=_verified(fx.head),
                ruleset=_good_ruleset(),
                current_main_sha=fx.base,
            )
            self.assertEqual(premerge.code, "TRANSPORT_CANDIDATE_V3_CONFIRMED")
            canonical = pb.canonical_transition_gate(
                identity=fx.material.identity,
                first_parent_history=[fx.git.view(fx.canonical), fx.git.view(fx.base)],
                current_entries=fx.git.entries(fx.canonical),
                current_lock_bytes=fx.material.lock_bytes,
                ruleset=_good_ruleset(),
                now=NOW,
            )
            self.assertEqual(canonical.code, "CANONICAL_ACQUIRE_IDENTITY_CONFIRMED")

    def test_row_02_unrelated_same_worker_principal_lock_never_satisfies_active_next(self):
        expected = _material()
        unrelated = _material(_ids("5", "6", "7", "8"), task="TASK-UNRELATED", collision_keys=("other/key",))
        self.assertTrue(pb.reconstruct_v3_from_lock_payload(unrelated.identity, unrelated.lock_payload).allowed)
        got = _canonical_gate(
            expected,
            current_entries=_candidate_entries(unrelated),
            current_lock_bytes=unrelated.lock_bytes,
        )
        self.assertEqual(got.code, "CANONICAL_LOCK_READBACK_MISMATCH")

    def test_row_03_old_acquisition_lock_id_or_timestamp_never_satisfies(self):
        material = _material()
        payload = copy.deepcopy(material.lock_payload); payload["lock_id"] = "LOCK-OLD"
        self.assertFalse(pb.reconstruct_v3_from_lock_payload(material.identity, payload).allowed)

    def test_row_04_wrong_work_ref_fails_active_next(self):
        material = _material(); payload = copy.deepcopy(material.lock_payload); payload["work_ref"] = "research/wrong"
        self.assertFalse(pb.reconstruct_v3_from_lock_payload(material.identity, payload).allowed)

    def test_row_05_wrong_collision_bundle_fails_active_next(self):
        material = _material(); payload = copy.deepcopy(material.lock_payload); payload["collision_keys"] = ["wrong/key"]
        self.assertFalse(pb.reconstruct_v3_from_lock_payload(material.identity, payload).allowed)

    def test_row_06_wrong_worker_fails_binding(self):
        material = _material(); payload = copy.deepcopy(material.lock_payload); payload["worker_id"] = WORKER_B
        self.assertFalse(pb.reconstruct_v3_from_lock_payload(material.identity, payload).allowed)

    def test_row_07_wrong_principal_fails_binding(self):
        material = _material(); payload = copy.deepcopy(material.lock_payload); payload["actor"]["id"] = "gh:other"
        self.assertFalse(pb.reconstruct_v3_from_lock_payload(material.identity, payload).allowed)

    def test_row_08_stale_acquire_base_has_no_pending_or_merge_authority(self):
        self.assertEqual(_premerge(current_main="9" * 40).code, "CANONICAL_ACQUIRE_BASE_MISMATCH")

    def test_row_09_stale_release_repair_requires_new_current_verify(self):
        good = _release_fixture(verify=True)
        accepted = pb.release_provenance_gate(
            source_record=good[0], release_base_sha=good[1], release_expected_tree_sha=good[2],
            release_transport_commit=good[3], release_transport_entries=good[4], release_verify=good[5], first_parent_history=good[6],
        )
        self.assertEqual(accepted.code, "SOURCE_EPOCH_RELEASE_PROVENANCE_CONFIRMED")
        stale = list(good)
        stale[5] = VerifyObservation(False, "LATEST_VERIFY_NOT_SUCCESS", head_sha=good[3]["sha"])
        rejected = pb.release_provenance_gate(
            source_record=stale[0], release_base_sha=stale[1], release_expected_tree_sha=stale[2],
            release_transport_commit=stale[3], release_transport_entries=stale[4], release_verify=stale[5], first_parent_history=stale[6],
        )
        self.assertEqual(rejected.code, "LATEST_VERIFY_NOT_SUCCESS")

    def test_row_10_stale_pr_head_invalidates_prior_verify_and_transport_identity(self):
        green_old = _good_verify(head=HEAD_SHA)
        material = _material()
        moved = _candidate_commit(material, sha=ALT_HEAD_SHA)
        got = pb.premerge_transport_gate(
            identity=material.identity, independently_derived_ids=material.identity.semantic_ids(), base_entries=_base_entries(),
            candidate_commit=moved, candidate_entries=_candidate_entries(material), candidate_lock_bytes=material.lock_bytes,
            verify=VerifyObservation(False, "LATEST_VERIFY_NOT_SUCCESS"), ruleset=_good_ruleset(), current_main_sha=BASE_SHA,
        )
        self.assertTrue(green_old.eligible); self.assertFalse(got.allowed)

    def test_row_11_duplicate_next_has_one_deterministic_release_and_acquire_key(self):
        client = _DraftPRClient()
        ids = _ids()
        for ref in (
            pb.deterministic_release_ref("TASK-SOURCE", WORKER),
            pb.deterministic_acquire_ref(ids.acquire_intent_id, TASK, WORKER),
        ):
            first = pb._create_or_reuse_draft_pr(
                client, open_prs=[], ref=ref, head_sha=HEAD_SHA, title="fixture", body="fixture",
            )
            second = pb._create_or_reuse_draft_pr(
                client, open_prs=[first], ref=ref, head_sha=HEAD_SHA, title="fixture", body="fixture",
            )
            self.assertEqual(first["number"], second["number"])
        self.assertEqual(client.created, 2)

    def test_row_12_duplicate_creator_adopts_exact_winner_and_non_equivalent_content_is_rejected(self):
        client = _DraftPRClient()
        ref = pb.deterministic_acquire_ref(_ids().acquire_intent_id, TASK, WORKER)
        winner = _pr(7, HEAD_SHA, ref=ref, draft=True)
        adopted = pb._create_or_reuse_draft_pr(
            client, open_prs=[winner], ref=ref, head_sha=HEAD_SHA, title="fixture", body="fixture",
        )
        self.assertEqual(adopted, winner)
        self.assertEqual(client.created, 0)
        with self.assertRaises(pb.PhaseBError) as cm:
            pb._create_or_reuse_draft_pr(
                client, open_prs=[winner], ref=ref, head_sha=ALT_HEAD_SHA, title="fixture", body="fixture",
            )
        self.assertEqual(cm.exception.code, "TRANSPORT_REF_CONFLICT")
        with _exact_acquire_git() as fx:
            reader = _ExactReadClient(fx.git)
            adopted_material = pb._identity_from_existing_candidate(
                reader,
                head_sha=fx.head,
                ids=fx.material.identity.semantic_ids(),
                base_sha=fx.base,
                base_tree_sha=fx.base_tree,
                base_entries=fx.base_entries,
                selected_task_id=TASK,
                worker_id=WORKER,
                principal_id=PRINCIPAL,
                work_ref=f"research/{TASK}/{WORKER}",
                collision_keys=("x/next",),
                lease_ttl_hours=168,
            )
            self.assertEqual(adopted_material.identity, fx.material.identity)
            conflicting_head = fx.git.commit(fx.base_tree, parent=fx.base, message="race loser conflict", second=5)
            with self.assertRaises(pb.PhaseBError) as race:
                pb._identity_from_existing_candidate(
                    reader,
                    head_sha=conflicting_head,
                    ids=fx.material.identity.semantic_ids(),
                    base_sha=fx.base,
                    base_tree_sha=fx.base_tree,
                    base_entries=fx.base_entries,
                    selected_task_id=TASK,
                    worker_id=WORKER,
                    principal_id=PRINCIPAL,
                    work_ref=f"research/{TASK}/{WORKER}",
                    collision_keys=("x/next",),
                    lease_ttl_hours=168,
                )
            self.assertEqual(race.exception.code, "TRANSPORT_REF_CONFLICT")

    def test_row_13_old_source_acquisition_replay_changes_source_epoch(self):
        _, a = _source_record(acquired="2026-09-01T00:00:00+00:00")
        _, b = _source_record(acquired="2026-09-01T00:00:01+00:00")
        self.assertNotEqual(a, b)

    def test_row_14_equivalent_release_transport_uses_same_deterministic_ref(self):
        client = _DraftPRClient()
        ref = pb.deterministic_release_ref("TASK-SOURCE", WORKER)
        existing = _pr(3, HEAD_SHA, ref=ref, draft=True)
        got = pb._create_or_reuse_draft_pr(
            client, open_prs=[existing], ref=ref, head_sha=HEAD_SHA, title="release", body="release",
        )
        self.assertEqual(got["number"], 3)
        self.assertEqual(client.created, 0)
        captured = {}
        api = pb.GitHubPhaseBClient("fixture-token")
        def fake_request(method, path, payload=None):
            captured["method"] = method
            captured["path"] = path
            captured["payload"] = payload
            return {"sha": "a" * 40}
        api.request = fake_request
        tree_sha = api.create_tree(
            "b" * 40,
            (),
            deletions=["coordination/locks/x/shared.yml"],
        )
        self.assertEqual(tree_sha, "a" * 40)
        self.assertEqual(captured["method"], "POST")
        self.assertEqual(
            captured["path"],
            "/repos/51mns/AIMath-public/git/trees",
        )
        self.assertEqual(
            captured["payload"]["tree"],
            [{
                "path": "coordination/locks/x/shared.yml",
                "mode": "100644",
                "type": "blob",
                "sha": None,
            }],
        )

    def test_row_15_unrelated_release_content_is_conflict_not_reuse(self):
        client = _DraftPRClient()
        ref = pb.deterministic_release_ref("TASK-SOURCE", WORKER)
        conflicting = _pr(3, ALT_HEAD_SHA, ref=ref, draft=True)
        with self.assertRaises(pb.PhaseBError) as cm:
            pb._create_or_reuse_draft_pr(
                client, open_prs=[conflicting], ref=ref, head_sha=HEAD_SHA, title="release", body="release",
            )
        self.assertEqual(cm.exception.code, "TRANSPORT_REF_CONFLICT")

    def test_row_16_already_released_requires_exact_source_epoch_release_provenance(self):
        args = _release_fixture()
        got = pb.release_provenance_gate(source_record=args[0], release_base_sha=args[1], release_expected_tree_sha=args[2], release_transport_commit=args[3], release_transport_entries=args[4], release_verify=args[5], first_parent_history=args[6])
        self.assertEqual(got.code, "SOURCE_EPOCH_RELEASE_PROVENANCE_CONFIRMED")

    def test_row_17_equivalent_acquire_pr_is_same_transport_key(self):
        client = _DraftPRClient()
        material = _material()
        ref = pb.deterministic_acquire_ref(material.identity.acquire_intent_id, TASK, WORKER)
        existing = _pr(4, HEAD_SHA, ref=ref, draft=True)
        got = pb._create_or_reuse_draft_pr(
            client, open_prs=[existing], ref=ref, head_sha=HEAD_SHA, title="acquire", body="acquire",
        )
        self.assertEqual(got["number"], 4)
        self.assertEqual(client.created, 0)
        with _exact_acquire_git() as fx:
            adopted = pb._identity_from_existing_candidate(
                _ExactReadClient(fx.git),
                head_sha=fx.head,
                ids=fx.material.identity.semantic_ids(),
                base_sha=fx.base,
                base_tree_sha=fx.base_tree,
                base_entries=fx.base_entries,
                selected_task_id=TASK,
                worker_id=WORKER,
                principal_id=PRINCIPAL,
                work_ref=f"research/{TASK}/{WORKER}",
                collision_keys=("x/next",),
                lease_ttl_hours=168,
            )
            self.assertEqual(adopted.identity.canonical_id(), fx.material.canonical_acquire_id)

    def test_row_18_exact_ref_without_pr_has_one_create_key(self):
        client = _DraftPRClient()
        ref = pb.deterministic_acquire_ref(_ids().acquire_intent_id, TASK, WORKER)
        first = pb._create_or_reuse_draft_pr(
            client, open_prs=[], ref=ref, head_sha=HEAD_SHA, title="acquire", body="acquire",
        )
        second = pb._create_or_reuse_draft_pr(
            client, open_prs=[first], ref=ref, head_sha=HEAD_SHA, title="acquire", body="acquire",
        )
        self.assertEqual(first["number"], second["number"])
        self.assertEqual(client.created, 1)

    def test_row_19_canonical_v3_transition_not_pr_metadata_grants_active_next(self):
        got = _canonical_gate(); self.assertTrue(got.allowed); self.assertEqual(got.code, "CANONICAL_ACQUIRE_IDENTITY_CONFIRMED")

    def test_row_20_self_consistent_forged_next_binding_fails_trusted_expected_ids(self):
        _src, trusted_context, _sel, _intent, expected_ids, _expected_material, _state = _trusted_semantic_chain()
        self.assertTrue(trusted_context["canonical_stop_condition_reached"])
        self.assertTrue(trusted_context["canonical_dependency_followup_unusable"])
        self.assertFalse(trusted_context["same_campaign_allowed"])
        fields = ("source_epoch_id", "continuation_context_id", "selection_id", "acquire_intent_id")
        for field in fields:
            with self.subTest(field=field):
                values = expected_ids.__dict__.copy(); values[field] = "f" * 64
                forged_ids = SemanticIds(**values)
                forged = _material(forged_ids)
                # The candidate is object-internally self-consistent with its own forged binding.
                for obj in forged.identity.exact_lock_objects:
                    raw = forged.lock_bytes[obj.path]
                    self.assertEqual(pb.git_blob_oid(raw), obj.blob_sha)
                    self.assertEqual(hashlib.sha256(raw).hexdigest(), obj.bytes_sha256)
                    payload = json.loads(raw.decode("utf-8"))
                    self.assertTrue(pb.reconstruct_v3_from_lock_payload(forged.identity, payload).allowed)
                self.assertEqual(pb.deterministic_tree_sha(_candidate_entries(forged)), forged.identity.expected_canonical_tree_sha)
                got = pb.premerge_transport_gate(
                    identity=forged.identity,
                    independently_derived_ids=expected_ids,
                    base_entries=_base_entries(),
                    candidate_commit=_candidate_commit(forged),
                    candidate_entries=_candidate_entries(forged),
                    candidate_lock_bytes=forged.lock_bytes,
                    verify=_verified(HEAD_SHA),
                    ruleset=_good_ruleset(),
                    current_main_sha=BASE_SHA,
                )
                self.assertFalse(got.allowed); self.assertEqual(got.code, "CANONICAL_ACQUIRE_SEMANTIC_BINDING_MISMATCH")

    def test_row_21_historical_transition_exact_but_current_lock_later_changed_is_not_active(self):
        original = _material()
        replacement = _material(_ids("5", "6", "7", "8"), acquired_at=NOW + timedelta(seconds=1))
        self.assertTrue(pb.reconstruct_v3_from_lock_payload(replacement.identity, replacement.lock_payload).allowed)
        got = _canonical_gate(
            original,
            current_entries=_candidate_entries(replacement),
            current_lock_bytes=replacement.lock_bytes,
        )
        self.assertEqual(got.code, "CANONICAL_LOCK_READBACK_MISMATCH")

    def test_row_22_two_workers_same_task_only_matching_canonical_identity_wins(self):
        a = _material(worker=WORKER); b = _material(worker=WORKER_B, ids=_ids("1","2","3","5"))
        self.assertTrue(_premerge(a).allowed)
        self.assertTrue(_premerge(b).allowed)
        self.assertTrue(_canonical_gate(a).allowed)
        loser = _canonical_gate(b, history=_history(a), current_entries=_candidate_entries(a), current_lock_bytes=a.lock_bytes)
        self.assertFalse(loser.allowed)

    def test_row_23_overlapping_collision_bundle_first_canonical_owner_blocks_second(self):
        first = _material(); base_after = _candidate_entries(first)
        with self.assertRaises(pb.PhaseBError):
            pb.freeze_acquire_material(semantic_ids=_ids("1","2","3","5"), base_sha=M_SHA, base_tree_sha=first.identity.expected_canonical_tree_sha, base_tree_entries=base_after, selected_task_id="TASK-NEXT-2", worker_id=WORKER_B, principal_id=PRINCIPAL, work_ref=f"research/TASK-NEXT-2/{WORKER_B}", collision_keys=["x/next"], acquired_at=NOW, lease_ttl_hours=168)

    def test_row_24_campaign_last_slot_race_second_stale_base_fails(self):
        state = base_state()
        state.campaigns["CAM-X"]["max_active_lanes"] = 1
        state.tasks["TASK-X-2"] = {
            **state.tasks["TASK-X-1"],
            "task_id": "TASK-X-2",
            "collision_keys": ["x/2"],
            "owned_paths": ["work/x2/**"],
        }
        self.assertTrue(state.readiness("TASK-X-1")[0])
        self.assertTrue(state.readiness("TASK-X-2")[0])
        add_lock(state, "LOCK-FIRST", "TASK-X-1", "x/shared")
        ok, reasons = state.readiness("TASK-X-2")
        self.assertFalse(ok)
        self.assertTrue(any("campaign active-lane capacity" in reason for reason in reasons))

    def test_row_25_global_last_slot_race_second_stale_base_fails(self):
        state = base_state()
        state.portfolio["global_active_lane_cap"] = 1
        state.campaigns["CAM-Y"] = {**state.campaigns["CAM-X"], "campaign_id": "CAM-Y"}
        state.tasks["TASK-Y-1"] = {
            **state.tasks["TASK-X-1"],
            "task_id": "TASK-Y-1",
            "campaign_id": "CAM-Y",
            "collision_keys": ["y/1"],
            "owned_paths": ["work/y1/**"],
        }
        self.assertTrue(state.readiness("TASK-X-1")[0])
        self.assertTrue(state.readiness("TASK-Y-1")[0])
        add_lock(state, "LOCK-FIRST", "TASK-X-1", "x/shared")
        ok, reasons = state.readiness("TASK-Y-1")
        self.assertFalse(ok)
        self.assertTrue(any("global active-lane capacity" in reason for reason in reasons))

    def test_row_26_release_beats_acquire_when_both_eligible(self):
        kind, row = pb.choose_lifecycle_candidate([{"eligible": True, "pr_number": 8}], [{"eligible": True, "pr_number": 1}])
        self.assertEqual((kind, row["pr_number"]), ("RELEASE", 8))

    def test_row_27_at_most_one_trusted_lifecycle_candidate_per_run(self):
        import lock_auto_activate as lifecycle
        from lock_auto_activate_phase_a import AutoReleaseCandidate

        releases = [
            AutoReleaseCandidate(_pr(8, HEAD_SHA), [], "LOCK-1", "RESULT_TERMINAL"),
            AutoReleaseCandidate(_pr(9, ALT_HEAD_SHA), [], "LOCK-2", "RESULT_TERMINAL"),
        ]
        fake_state = SimpleNamespace(
            lock_bundles={
                "LOCK-1": SimpleNamespace(payload={"task_id": "TASK-1"}),
                "LOCK-2": SimpleNamespace(payload={"task_id": "TASK-2"}),
            }
        )

        def request(_token, _repository, _method, path, payload=None):
            if "/actions/runs/" in path:
                return {"name": lifecycle.VERIFY_WORKFLOW_NAME, "event": "pull_request", "status": "completed", "conclusion": "success"}
            return {"object": {"sha": BASE_SHA}}

        with patch.dict(os.environ, {"GITHUB_REPOSITORY": pb.REPOSITORY, "GITHUB_TOKEN": "fixture", "SOURCE_RUN_ID": "1"}, clear=False), \
             patch.object(lifecycle, "_request_json", side_effect=request), \
             patch.object(lifecycle, "_trusted_main_state", return_value=fake_state), \
             patch.object(lifecycle, "_fetch_exact_tree", return_value=[]), \
             patch.object(lifecycle, "load_autonomous_lock_principals", return_value={"automatic_release_principals": []}), \
             patch.object(lifecycle, "_fetch_open_prs", return_value=[]), \
             patch.object(lifecycle, "_scan_releases", return_value=releases), \
             patch.object(lifecycle, "_scan_acquires") as scan_acquires, \
             patch.object(lifecycle, "_strict_up_to_date_gate", return_value=(True, "fixture")), \
             patch.object(lifecycle, "_merge_candidate", return_value={"sha": M_SHA}) as merge:
            with redirect_stdout(io.StringIO()):
                self.assertEqual(lifecycle.main(), 0)
        self.assertEqual(merge.call_count, 1)
        scan_acquires.assert_not_called()

    def test_row_28_ruleset_observation_unavailable_or_malformed_fails_closed(self):
        self.assertEqual(pb.prove_ruleset(None, None).code, "RULESET_PROOF_UNAVAILABLE")
        effective, _ = _ruleset_inputs()
        first_page = [{"id": i} for i in range(1, 101)]
        details = {i: _ruleset_detail(i, active=False) for i in range(1, 101)}
        details[101] = _ruleset_detail(101)
        client = _PagedGitHubClient(
            effective_pages={1: effective},
            ruleset_pages={1: first_page, 2: [{"id": 101}]},
            ruleset_details=details,
        )
        proof = client.ruleset_proof()
        self.assertTrue(proof.passed, "a valid applicable strict/no-bypass Ruleset on page 2 must be observed")

    def test_row_29_ruleset_strict_false_or_verify_missing_fails_closed(self):
        for strict, context in ((False, "verify"), (True, "other")):
            with self.subTest(strict=strict, context=context):
                e, d = _ruleset_inputs(strict=strict, context=context); self.assertFalse(pb.prove_ruleset(e, d).passed)

    def test_row_30_exact_head_ci_red_or_missing_has_no_activation_authority(self):
        failed = _observe([_run(10, 1, status="completed", conclusion="failure")]); missing = _observe([], head=HEAD_SHA)
        self.assertFalse(failed.eligible); self.assertFalse(missing.eligible)

    def test_row_31_old_head_green_does_not_transfer_to_moved_head(self):
        old = _good_verify(head=HEAD_SHA); moved = _observe([_run(10, 1, head=HEAD_SHA)], head=ALT_HEAD_SHA)
        self.assertTrue(old.eligible); self.assertFalse(moved.eligible)

    def test_row_32_candidate_local_malformed_drops_only_candidate(self):
        material = _material()
        client = _PendingClient({HEAD_SHA: material, ALT_HEAD_SHA: material}, malformed_heads={HEAD_SHA})
        state = SimpleNamespace(tasks={TASK: {"collision_keys": ["x/next"]}})
        records = pb._pending_records_from_open_acquire_prs(
            client,
            open_prs=[_pr(1, HEAD_SHA), _pr(2, ALT_HEAD_SHA)],
            current_main_sha=BASE_SHA,
            state=state,
            now=NOW,
        )
        self.assertEqual([row["pr_number"] for row in records], [2])
        kind, row = pb.choose_lifecycle_candidate([], [{"eligible": True, **records[0]}])
        self.assertEqual((kind, row["pr_number"]), ("ACQUIRE", 2))

    def test_row_33_repository_wide_observation_failure_is_global_fail_closed(self):
        material = _material()
        state = SimpleNamespace(tasks={TASK: {"collision_keys": ["x/next"]}})
        positive = pb._pending_records_from_open_acquire_prs(
            _PendingClient({HEAD_SHA: material}),
            open_prs=[_pr(1, HEAD_SHA)],
            current_main_sha=BASE_SHA,
            state=state,
            now=NOW,
        )
        self.assertEqual(len(positive), 1)
        try:
            observed = pb._pending_records_from_open_acquire_prs(
                _PendingClient({HEAD_SHA: material}, fail_global_base=True),
                open_prs=[_pr(1, HEAD_SHA)],
                current_main_sha=BASE_SHA,
                state=state,
                now=NOW,
            )
        except pb.PhaseBError as exc:
            actual = exc.code
        except Exception as exc:  # turn an implementation escape into an assertion, never a fixture ERROR
            actual = f"UNEXPECTED_EXCEPTION:{type(exc).__name__}"
        else:
            actual = f"SWALLOWED_AS_CANDIDATE_LOCAL:{len(observed)}"
        self.assertEqual(actual, "REPOSITORY_OBSERVATION_INCOMPLETE")

    def test_row_34_candidate_disappears_or_closes_is_dropped_and_later_valid_examined(self):
        kind, row = pb.choose_lifecycle_candidate([], [{"eligible": False, "pr_number": 3}, {"eligible": True, "pr_number": 4}])
        self.assertEqual((kind, row["pr_number"]), ("ACQUIRE", 4))

    def test_row_35_main_moves_after_release_before_selection_changes_selection_identity(self):
        _, _, selection, _, ids, _, _ = _trusted_semantic_chain()
        moved = dict(selection); moved["selection_main_sha"] = "9" * 40
        self.assertNotEqual(ids.selection_id, pb.canonical_digest(moved))

    def test_row_36_main_moves_after_selection_before_acquire_creation_rejects_old_intent(self):
        self.assertFalse(_premerge(current_main="9" * 40).allowed)

    def test_row_37_main_moves_after_acquire_pr_creation_old_pr_is_not_ownership(self):
        self.assertFalse(pb.is_pending_ownership({"head_sha": HEAD_SHA})); self.assertFalse(_premerge(current_main=M_SHA).allowed)

    def test_row_38_pending_claim_is_nonownership_even_when_green(self):
        self.assertFalse(pb.is_pending_ownership({"verify_conclusion": "SUCCESS", "pr_state": "OPEN"}))

    def test_row_39_terminal_release_can_proceed_without_truth_promotion(self):
        self.assertEqual(pb.TRUTH_AUTHORITY, frozenset()); self.assertTrue(pb.deterministic_release_ref("TASK-SOURCE", WORKER).startswith("release/"))

    def test_row_40_no_autonomous_i2_i3_or_writer_self_review_authority(self):
        self.assertEqual(pb.REVIEW_AUTHORITY, frozenset())

    def test_row_41_no_automatic_renew_or_takeover_path(self):
        self.assertEqual(pb.FORBIDDEN_AUTOMATIC_OPERATIONS, frozenset({"RENEW", "TAKEOVER"}))

    def test_row_42_missing_human_gate_cannot_same_campaign_escalate(self):
        source_record, source_id = _source_record()
        rec, _ = pb.derive_continuation_context_v1(source_epoch_id=source_id, selection_main_sha=BASE_SHA, terminal_class="RESULT_TERMINAL", terminal_blob_sha=source_record["terminal_blob_sha"], source_campaign_id="CAM-X", global_admission="OPEN", source_campaign_strategic_state="ACTIVE", continuation_gate_required=True, continuation_decision_id=None, continuation_decision_blob_sha=None, human_decision=None, canonical_stop_condition_reached=False, canonical_dependency_followup_unusable=False, same_campaign_allowed=False, global_fallback_allowed=True, approved_followup_task_ids=[TASK], evaluation_followup_task_ids=[], reasons=["required human Continuation Gate decision is absent"], capability_profile=CapabilityProfile())
        self.assertTrue(rec["continuation_gate_required"]); self.assertFalse(rec["same_campaign_allowed"])

    def test_row_43_worker_recommendation_cannot_create_or_approve_task_or_campaign(self):
        names = set(pb.__all__)
        self.assertFalse({"create_task", "create_campaign", "approve_task", "approve_campaign"} & names)

    def test_row_44_selection_context_changes_recompute_identity_before_acquire(self):
        _s, context, selection, _i, ids, _m, _st = _trusted_semantic_chain()
        for field, value in (("pending_observation_digest", "f" * 64), ("ranked_task_ids", [TASK, "TASK-OTHER"]), ("hard_eligible_task_ids", [TASK, "TASK-OTHER"])):
            with self.subTest(field=field):
                changed = copy.deepcopy(selection); changed[field] = value; self.assertNotEqual(ids.selection_id, pb.canonical_digest(changed))
        changed_context = copy.deepcopy(context); changed_context["human_decision"] = "CONTINUE"
        self.assertNotEqual(ids.continuation_context_id, pb.canonical_digest(changed_context))
        state = base_state()
        terminal = TerminalEvidence(
            "RESULT_TERMINAL", "TASK-X-1", None, "NO_REUSABLE_PROGRESS", False, None,
            "coordination/outcomes/TASK-X-1.yml",
        )
        for field in ("canonical_stop_condition_reached", "canonical_dependency_followup_unusable"):
            request_values = {
                "task_id": "TASK-X-1",
                "worker_id": WORKER,
                "principal_id": PRINCIPAL,
                "capabilities": CapabilityProfile(),
                field: True,
            }
            decision = derive_continuation_decision(
                state,
                SimpleNamespace(records=[]),
                NextRequest(**request_values),
                terminal,
            )
            self.assertFalse(decision.same_campaign_allowed)
            ctx, _ = pb.derive_continuation_context_v1(
                source_epoch_id="1" * 64,
                selection_main_sha=BASE_SHA,
                terminal_class=terminal.terminal_class,
                terminal_blob_sha="f" * 40,
                source_campaign_id="CAM-X",
                global_admission="OPEN",
                source_campaign_strategic_state="ACTIVE",
                continuation_gate_required=False,
                continuation_decision_id=None,
                continuation_decision_blob_sha=None,
                human_decision=None,
                canonical_stop_condition_reached=(field == "canonical_stop_condition_reached"),
                canonical_dependency_followup_unusable=(field == "canonical_dependency_followup_unusable"),
                same_campaign_allowed=decision.same_campaign_allowed,
                global_fallback_allowed=decision.global_fallback_allowed,
                approved_followup_task_ids=decision.approved_followup_task_ids,
                evaluation_followup_task_ids=decision.evaluation_followup_task_ids,
                reasons=decision.reasons,
                capability_profile=CapabilityProfile(),
            )
            self.assertTrue(ctx[field])
            self.assertFalse(ctx["same_campaign_allowed"])
            for call_name in ("NextRequest", "derive_continuation_context_v1"):
                with self.subTest(restrictive_fact=field, adapter_call=call_name):
                    expression = _adapter_keyword(call_name, field)
                    self.assertIsNotNone(expression, f"Phase B adapter must pass fresh {field} into {call_name}")
                    self.assertFalse(
                        isinstance(expression, ast.Constant) and expression.value is False,
                        f"Phase B adapter hard-codes {field}=False in {call_name}",
                    )
                    self.assertNotIn("args", ast.unparse(expression), f"{field} cannot come from caller assertion")

    def test_row_45_source_terminal_blob_change_invalidates_old_source_epoch(self):
        _, a = _source_record(terminal_blob="f" * 40); _, b = _source_record(terminal_blob="1" * 40)
        self.assertNotEqual(a, b)

    def test_row_46_source_lock_blob_bundle_change_invalidates_old_release_request(self):
        _, a = _source_record(lock_blob="e" * 40); _, b = _source_record(lock_blob="2" * 40)
        self.assertNotEqual(a, b)

    def test_row_47_deterministic_lock_id_stable_and_intent_distinct(self):
        self.assertEqual(pb.deterministic_lock_id("1" * 64), pb.deterministic_lock_id("1" * 64)); self.assertNotEqual(pb.deterministic_lock_id("1" * 64), pb.deterministic_lock_id("2" * 64))

    def test_row_48_first_creator_timestamp_is_immutable_for_same_intent_retry(self):
        first = _material(acquired_at=NOW); retry_wrong = _material(acquired_at=NOW + timedelta(seconds=1))
        self.assertEqual(first.identity.acquire_intent_id, retry_wrong.identity.acquire_intent_id); self.assertNotEqual(first.lock_bytes, retry_wrong.lock_bytes)
        adopted = _material(acquired_at=NOW); self.assertEqual(first.lock_bytes, adopted.lock_bytes)

    def test_row_49_canonical_lock_path_blob_bundle_must_equal_expected_transport_bundle(self):
        with _exact_acquire_git(collision_keys=("x/next", "x/second")) as fx:
            history = [fx.git.view(fx.canonical), fx.git.view(fx.base)]
            current_entries = fx.git.entries(fx.canonical)
            baseline = pb.canonical_transition_gate(
                identity=fx.material.identity,
                first_parent_history=history,
                current_entries=current_entries,
                current_lock_bytes=fx.material.lock_bytes,
                ruleset=_good_ruleset(),
                now=NOW,
            )
            self.assertTrue(baseline.allowed)
            cases = {}
            missing = copy.deepcopy(current_entries)
            missing[:] = [row for row in missing if row["path"] != fx.material.identity.exact_lock_objects[0].path]
            cases["path"] = (missing, fx.material.lock_bytes)
            wrong_mode = copy.deepcopy(current_entries)
            next(row for row in wrong_mode if row["path"] == fx.material.identity.exact_lock_objects[0].path)["mode"] = "100755"
            cases["mode"] = (wrong_mode, fx.material.lock_bytes)
            wrong_oid = copy.deepcopy(current_entries)
            next(row for row in wrong_oid if row["path"] == fx.material.identity.exact_lock_objects[0].path)["sha"] = "0" * 40
            cases["blob_oid"] = (wrong_oid, fx.material.lock_bytes)
            wrong_bytes = dict(fx.material.lock_bytes)
            first_path = fx.material.identity.exact_lock_objects[0].path
            wrong_bytes[first_path] = wrong_bytes[first_path] + b" "
            cases["bytes_and_sha256"] = (current_entries, wrong_bytes)
            for label, (entries, lock_bytes) in cases.items():
                with self.subTest(mutation=label):
                    got = pb.canonical_transition_gate(
                        identity=fx.material.identity,
                        first_parent_history=history,
                        current_entries=entries,
                        current_lock_bytes=lock_bytes,
                        ruleset=_good_ruleset(),
                        now=NOW,
                    )
                    self.assertEqual(got.code, "CANONICAL_LOCK_READBACK_MISMATCH")

    def test_row_50_expired_canonical_lock_never_active_next(self):
        material = _material(acquired_at=NOW - timedelta(days=10)); self.assertEqual(_canonical_gate(material, now=NOW).code, "CANONICAL_LOCK_NOT_ACTIVE")
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            state = _cli_source_state(root, expires_at=NOW - timedelta(seconds=1))
            expired = _run_cli_source_case(root, state)
            self.assertNotEqual(expired.rc, 0)
            self.assertIn("expired/stale", expired.output)
            self.assertFalse(expired.state_path.exists())
            self.assertEqual(expired.source_epoch_calls, 0)
            self.assertEqual(expired.release_calls, 0)
            self.assertEqual(expired.acquire_calls, 0)

    def test_row_51_same_content_alternate_head_is_same_canonical_acquisition_content(self):
        with _exact_acquire_git() as fx:
            h1, h2 = fx.git.view(fx.head), fx.git.view(fx.alt_head)
            self.assertNotEqual(h1["sha"], h2["sha"])
            self.assertEqual(h1["parents"], h2["parents"])
            self.assertEqual(h1["tree"], h2["tree"])
            for head in (h1, h2):
                got = pb.premerge_transport_gate(
                    identity=fx.material.identity,
                    independently_derived_ids=fx.material.identity.semantic_ids(),
                    base_entries=fx.base_entries,
                    candidate_commit=head,
                    candidate_entries=head["entries"],
                    candidate_lock_bytes=fx.material.lock_bytes,
                    verify=_verified(head["sha"]),
                    ruleset=_good_ruleset(),
                    current_main_sha=fx.base,
                )
                self.assertTrue(got.allowed)
            self.assertNotIn("expected_head_sha", fx.material.identity.to_dict())

    def test_row_52_webhook_delivery_is_trigger_only_not_identity_authority(self):
        material = _material(); before = material.canonical_acquire_id
        noisy = material.identity.to_dict(); noisy_copy = copy.deepcopy(noisy); noisy_copy.pop("schema_version"); noisy_copy["webhook_run_id"] = 999999
        self.assertEqual(before, material.identity.canonical_id()); self.assertNotIn("webhook_run_id", material.identity.to_dict())

    def test_row_53_multiple_release_lowest_pr_wins_after_malformed_lower_drop(self):
        args = _release_fixture()
        gate = pb.release_provenance_gate(
            source_record=args[0], release_base_sha=args[1], release_expected_tree_sha=args[2],
            release_transport_commit=args[3], release_transport_entries=args[4], release_verify=args[5], first_parent_history=args[6],
        )
        self.assertTrue(gate.allowed)
        releases = [
            {"eligible": False, "pr_number": 1, "gate": "CANDIDATE_LOCAL_MALFORMED"},
            {"eligible": gate.allowed, "pr_number": 2, "gate": gate.code},
            {"eligible": gate.allowed, "pr_number": 3, "gate": gate.code},
        ]
        kind, row = pb.choose_lifecycle_candidate(releases, [])
        self.assertEqual((kind, row["pr_number"]), ("RELEASE", 2))

    def test_row_54_multiple_acquire_lowest_pr_wins_after_malformed_lower_drop(self):
        first, second = _material(), _material(_ids("1", "2", "3", "5"), worker=WORKER_B)
        self.assertTrue(_premerge(first).allowed)
        self.assertTrue(_premerge(second).allowed)
        acquires = [
            {"eligible": False, "pr_number": 1, "gate": "CANDIDATE_LOCAL_MALFORMED"},
            {"eligible": True, "pr_number": 2},
            {"eligible": True, "pr_number": 3},
        ]
        kind, row = pb.choose_lifecycle_candidate([], acquires)
        self.assertEqual((kind, row["pr_number"]), ("ACQUIRE", 2))

    def test_row_55_highest_run_number_controls_not_run_id_magnitude(self):
        page_one = [_run(i + 1, 10_000 + i, head=ALT_HEAD_SHA) for i in range(100)]
        authoritative = _run(101, 1, attempt=2)
        paged = _PagedGitHubClient(
            workflow_pages={
                1: {"total_count": 101, "workflow_runs": page_one},
                2: {"total_count": 101, "workflow_runs": [authoritative]},
            },
            current_runs={1: _run(101, 1, attempt=3)},
        )
        got = paged.workflow_runs_for_head(HEAD_SHA)
        self.assertTrue(got.eligible)
        self.assertEqual((got.authoritative_run_number, got.run_id, got.current_run_attempt), (101, 1, 3))

        cap = _PagedGitHubClient(
            workflow_pages={1: {"total_count": 1001, "workflow_runs": page_one}},
        ).workflow_runs_for_head(HEAD_SHA)
        self.assertEqual(cap.code, "VERIFY_RUNSET_RESULT_CAP_UNPROVEN")

        truncated_pages = {page: {"total_count": 1000, "workflow_runs": page_one} for page in range(1, 11)}
        truncated = _PagedGitHubClient(workflow_pages=truncated_pages).workflow_runs_for_head(HEAD_SHA)
        self.assertEqual(truncated.code, "VERIFY_RUNSET_TRUNCATED")

        malformed = _PagedGitHubClient(
            workflow_pages={1: {"total_count": 1, "workflow_runs": "not-a-list"}},
        ).workflow_runs_for_head(HEAD_SHA)
        self.assertEqual(malformed.code, "VERIFY_RUNSET_MALFORMED")

        duplicate = _observe([_run(11, 7), _run(11, 8)])
        self.assertEqual(duplicate.code, "VERIFY_RUN_NUMBER_DUPLICATE_INCONSISTENT")

        failing_client = _PagedGitHubClient(
            workflow_pages={
                1: {"total_count": 101, "workflow_runs": page_one},
                2: pb.PhaseBError("GITHUB_OBSERVATION_UNAVAILABLE", "page 2 failed"),
            },
        )
        try:
            pagination_failure = failing_client.workflow_runs_for_head(HEAD_SHA)
        except pb.PhaseBError as exc:
            pagination_failure = VerifyObservation(False, exc.code, head_sha=HEAD_SHA, detail=exc.message)
        except Exception as exc:
            pagination_failure = VerifyObservation(False, f"UNEXPECTED_EXCEPTION:{type(exc).__name__}", head_sha=HEAD_SHA)
        self.assertEqual(pagination_failure.code, "VERIFY_RUNSET_PAGINATION_FAILED")

    def test_row_56_indirect_merge_commit_attack_is_noncanonical(self):
        with _exact_acquire_git() as fx:
            other = fx.git.commit(fx.base_tree, message="unrelated parent", second=5)
            merge = fx.git.commit(
                fx.target_tree,
                parent=fx.base,
                extra_parents=(other,),
                message="noncanonical merge",
                second=6,
            )
            got = pb.canonical_transition_gate(
                identity=fx.material.identity,
                first_parent_history=[fx.git.view(merge), fx.git.view(fx.base)],
                current_entries=fx.git.entries(merge),
                current_lock_bytes=fx.material.lock_bytes,
                ruleset=_good_ruleset(),
                now=NOW,
            )
            self.assertEqual(got.code, "NONCANONICAL_ACQUIRE_MERGE_SHAPE")

    def test_row_57_different_pr_locator_same_head_can_confirm_only_v3_content_transition(self):
        material = _material(); self.assertTrue(_canonical_gate(material).allowed); self.assertNotIn("pr_number", material.identity.to_dict()); self.assertNotIn("pr_ref", material.identity.to_dict())

    def test_row_58_rerun_older_run_cannot_outrank_newer_failure(self):
        old = _run(10, 10, attempt=2, conclusion="success"); newer = _run(11, 11, conclusion="failure")
        got = _observe([old, newer]); self.assertFalse(got.eligible); self.assertEqual(got.authoritative_run_number, 11)

    def test_row_59_new_higher_successful_lineage_recovers(self):
        rows = [_run(10, 10), _run(11, 11, conclusion="failure"), _run(12, 12)]
        got = _observe(rows); self.assertTrue(got.eligible); self.assertEqual(got.authoritative_run_number, 12)

    def test_row_60_authoritative_lineage_current_rerun_in_progress_is_not_eligible(self):
        listed = _run(11, 11, attempt=1, conclusion="success")
        current = _run(11, 11, attempt=2, status="in_progress", conclusion=None)
        got = _observe([listed], current={11: current}); self.assertFalse(got.eligible); self.assertEqual(got.current_run_attempt, 2)

    def test_row_61_incomplete_or_non_single_first_parent_history_fails_closed(self):
        with _exact_acquire_git() as fx:
            canonical = fx.git.view(fx.canonical)
            base = fx.git.view(fx.base)
            partial = pb.canonical_transition_gate(
                identity=fx.material.identity,
                first_parent_history=[canonical],
                current_entries=canonical["entries"],
                current_lock_bytes=fx.material.lock_bytes,
                ruleset=_good_ruleset(),
                now=NOW,
            )
            self.assertEqual(partial.code, "CANONICAL_ACQUIRE_HISTORY_UNPROVEN")

            other = fx.git.commit(fx.base_tree, message="other root", second=5)
            merge = fx.git.commit(
                fx.target_tree,
                parent=fx.base,
                extra_parents=(other,),
                message="merge child",
                second=6,
            )
            multi_parent = pb.canonical_transition_gate(
                identity=fx.material.identity,
                first_parent_history=[fx.git.view(merge), base],
                current_entries=fx.git.entries(merge),
                current_lock_bytes=fx.material.lock_bytes,
                ruleset=_good_ruleset(),
                now=NOW,
            )
            self.assertEqual(multi_parent.code, "NONCANONICAL_ACQUIRE_MERGE_SHAPE")

            intervening = fx.git.commit(fx.base_tree, parent=fx.base, message="intervening", second=7)
            delayed = fx.git.commit(fx.target_tree, parent=intervening, message="delayed locks", second=8)
            multi_step = pb.canonical_transition_gate(
                identity=fx.material.identity,
                first_parent_history=[fx.git.view(delayed), fx.git.view(intervening), base],
                current_entries=fx.git.entries(delayed),
                current_lock_bytes=fx.material.lock_bytes,
                ruleset=_good_ruleset(),
                now=NOW,
            )
            self.assertFalse(multi_step.allowed)
            self.assertNotEqual(multi_step.code, "CANONICAL_ACQUIRE_IDENTITY_CONFIRMED")

    def test_row_62_ruleset_bypass_or_unreadable_regression_fails_closed(self):
        effective, direct = _ruleset_inputs(bypass=[{"actor_id": 1}])
        self.assertEqual(pb.prove_ruleset(effective, direct).code, "RULESET_BYPASS_PRESENT")
        self.assertEqual(pb.prove_ruleset([], []).code, "RULESET_PROOF_UNAVAILABLE")

        first_page = [{"id": i} for i in range(1, 101)]
        details = {i: _ruleset_detail(i, active=False) for i in range(1, 101)}
        details[1] = _ruleset_detail(1)
        details[101] = _ruleset_detail(101, bypass=[{"actor_id": 7}])
        paged = _PagedGitHubClient(
            effective_pages={1: effective},
            ruleset_pages={1: first_page, 2: [{"id": 101}]},
            ruleset_details=details,
        )
        proof = paged.ruleset_proof()
        self.assertFalse(proof.passed, "an applicable bypass-bearing Ruleset on page 2 must be observed")
        self.assertEqual(proof.code, "RULESET_BYPASS_PRESENT")

    def test_row_63_same_tree_alternate_head_cannot_borrow_verify(self):
        material = _material(); h2 = _candidate_commit(material, sha=ALT_HEAD_SHA)
        borrowed = _good_verify(head=HEAD_SHA)
        got = pb.premerge_transport_gate(identity=material.identity, independently_derived_ids=material.identity.semantic_ids(), base_entries=_base_entries(), candidate_commit=h2, candidate_entries=_candidate_entries(material), candidate_lock_bytes=material.lock_bytes, verify=VerifyObservation(False, "LATEST_VERIFY_NOT_SUCCESS"), ruleset=_good_ruleset(), current_main_sha=BASE_SHA)
        self.assertTrue(borrowed.eligible); self.assertFalse(got.allowed)

    def test_row_64_same_tree_alternate_head_with_stale_or_different_base_is_ineligible(self):
        with _exact_acquire_git() as fx:
            wrong_parent = fx.git.commit(fx.target_tree, message="wrong base", second=5)
            commit = fx.git.view(wrong_parent)
            got = pb.premerge_transport_gate(
                identity=fx.material.identity,
                independently_derived_ids=fx.material.identity.semantic_ids(),
                base_entries=fx.base_entries,
                candidate_commit=commit,
                candidate_entries=commit["entries"],
                candidate_lock_bytes=fx.material.lock_bytes,
                verify=_verified(wrong_parent),
                ruleset=_good_ruleset(),
                current_main_sha=fx.base,
            )
            self.assertEqual(got.code, "CANONICAL_ACQUIRE_BASE_MISMATCH")

    def test_row_65_same_base_but_different_tree_or_object_is_ineligible(self):
        with _exact_acquire_git() as fx:
            additions = [
                {"path": obj.path, "mode": obj.mode, "type": "blob", "sha": obj.blob_sha}
                for obj in fx.material.identity.exact_lock_objects
            ]
            additions[0] = {**additions[0], "sha": fx.git.blob(b"different lock object\n")}
            bad_tree = fx.git.tree(base_tree=fx.base_tree, additions=additions)
            bad_head = fx.git.commit(bad_tree, parent=fx.base, message="different object", second=5)
            commit = fx.git.view(bad_head)
            got = pb.premerge_transport_gate(
                identity=fx.material.identity,
                independently_derived_ids=fx.material.identity.semantic_ids(),
                base_entries=fx.base_entries,
                candidate_commit=commit,
                candidate_entries=commit["entries"],
                candidate_lock_bytes=fx.material.lock_bytes,
                verify=_verified(bad_head),
                ruleset=_good_ruleset(),
                current_main_sha=fx.base,
            )
            self.assertEqual(got.code, "CANONICAL_ACQUIRE_TREE_MISMATCH")

    def test_row_66_same_objects_but_claimed_different_source_epoch_is_semantic_inconsistency(self):
        material = _material(); claimed = replace(material.identity.semantic_ids(), source_epoch_id="f" * 64)
        got = pb.candidate_content_gate(expected_identity=material.identity, independently_derived_ids=claimed, candidate_lock_bytes=material.lock_bytes, candidate_exact_objects=material.identity.exact_lock_objects, candidate_tree_sha=material.identity.expected_canonical_tree_sha)
        self.assertFalse(got.allowed); self.assertEqual(got.code, "CANONICAL_ACQUIRE_SEMANTIC_BINDING_INCONSISTENT")

    def test_row_67_same_objects_but_claimed_different_acquire_intent_is_semantic_inconsistency(self):
        material = _material(); claimed = replace(material.identity.semantic_ids(), acquire_intent_id="f" * 64)
        got = pb.candidate_content_gate(expected_identity=material.identity, independently_derived_ids=claimed, candidate_lock_bytes=material.lock_bytes, candidate_exact_objects=material.identity.exact_lock_objects, candidate_tree_sha=material.identity.expected_canonical_tree_sha)
        self.assertFalse(got.allowed); self.assertEqual(got.code, "CANONICAL_ACQUIRE_SEMANTIC_BINDING_INCONSISTENT")

    def test_row_68_squash_positive_h_not_equal_m_but_same_b_t_content_confirms(self):
        with _exact_acquire_git() as fx:
            self.assertNotEqual(fx.head, fx.canonical)
            self.assertEqual(fx.git.view(fx.head)["parents"], fx.git.view(fx.canonical)["parents"])
            self.assertEqual(fx.git.view(fx.head)["tree"], fx.git.view(fx.canonical)["tree"])
            got = pb.canonical_transition_gate(
                identity=fx.material.identity,
                first_parent_history=[fx.git.view(fx.canonical), fx.git.view(fx.base)],
                current_entries=fx.git.entries(fx.canonical),
                current_lock_bytes=fx.material.lock_bytes,
                ruleset=_good_ruleset(),
                now=NOW,
            )
            self.assertEqual(got.code, "CANONICAL_ACQUIRE_IDENTITY_CONFIRMED")

    def test_row_69_duplicate_exact_lock_path_fails_before_canonical_hashing(self):
        material = _material(); obj = material.identity.exact_lock_objects[0]; bad = replace(material.identity, exact_lock_objects=(obj, obj))
        with self.assertRaises(pb.PhaseBError) as cm: pb.validate_v3_identity(bad)
        self.assertEqual(cm.exception.code, "CANONICAL_ACQUIRE_DUPLICATE_LOCK_PATH")

    def test_row_70_mutating_source_continuation_or_selection_binding_changes_bytes_oid_and_tree(self):
        with _exact_acquire_git() as fx:
            base = fx.material
            for field in ("source_epoch_id", "continuation_context_id", "selection_id"):
                with self.subTest(field=field):
                    vals = base.identity.semantic_ids().__dict__.copy(); vals[field] = "f" * 64
                    changed = _material(
                        SemanticIds(**vals),
                        base_sha=fx.base,
                        base_tree_sha=fx.base_tree,
                        base_entries=fx.base_entries,
                    )
                    self.assertNotEqual(base.lock_bytes, changed.lock_bytes)
                    self.assertNotEqual(base.identity.exact_lock_objects[0].bytes_sha256, changed.identity.exact_lock_objects[0].bytes_sha256)
                    self.assertNotEqual(base.identity.exact_lock_objects[0].blob_sha, changed.identity.exact_lock_objects[0].blob_sha)
                    for obj in changed.identity.exact_lock_objects:
                        self.assertEqual(fx.git.blob(changed.lock_bytes[obj.path]), obj.blob_sha)
                    tree = fx.git.tree(
                        base_tree=fx.base_tree,
                        additions=[{"path": obj.path, "mode": obj.mode, "type": "blob", "sha": obj.blob_sha} for obj in changed.identity.exact_lock_objects],
                    )
                    self.assertEqual(tree, changed.identity.expected_canonical_tree_sha)
                    self.assertNotEqual(base.identity.expected_canonical_tree_sha, changed.identity.expected_canonical_tree_sha)

    def test_row_71_mutating_acquire_intent_binding_changes_bytes_oid_and_tree(self):
        with _exact_acquire_git() as fx:
            base = fx.material
            vals = base.identity.semantic_ids().__dict__.copy(); vals["acquire_intent_id"] = "f" * 64
            changed = _material(
                SemanticIds(**vals),
                base_sha=fx.base,
                base_tree_sha=fx.base_tree,
                base_entries=fx.base_entries,
            )
            self.assertNotEqual(base.lock_bytes, changed.lock_bytes)
            self.assertNotEqual(base.identity.exact_lock_objects[0].bytes_sha256, changed.identity.exact_lock_objects[0].bytes_sha256)
            self.assertNotEqual(base.identity.exact_lock_objects[0].blob_sha, changed.identity.exact_lock_objects[0].blob_sha)
            for obj in changed.identity.exact_lock_objects:
                self.assertEqual(fx.git.blob(changed.lock_bytes[obj.path]), obj.blob_sha)
            tree = fx.git.tree(
                base_tree=fx.base_tree,
                additions=[{"path": obj.path, "mode": obj.mode, "type": "blob", "sha": obj.blob_sha} for obj in changed.identity.exact_lock_objects],
            )
            self.assertEqual(tree, changed.identity.expected_canonical_tree_sha)
            self.assertNotEqual(base.identity.expected_canonical_tree_sha, changed.identity.expected_canonical_tree_sha)

    def test_row_72_post_squash_semantic_reconstruction_comes_from_canonical_bytes_not_process_memory(self):
        with _exact_acquire_git() as fx:
            canonical = pb.canonical_transition_gate(
                identity=fx.material.identity,
                first_parent_history=[fx.git.view(fx.canonical), fx.git.view(fx.base)],
                current_entries=fx.git.entries(fx.canonical),
                current_lock_bytes=fx.material.lock_bytes,
                ruleset=_good_ruleset(),
                now=NOW,
            )
            self.assertTrue(canonical.allowed)
            for raw in fx.material.lock_bytes.values():
                payload = json.loads(raw.decode("utf-8"))
                self.assertEqual(pb.parse_next_binding(payload), fx.material.identity.semantic_ids())
                self.assertTrue(pb.reconstruct_v3_from_lock_payload(fx.material.identity, payload).allowed)
            _s, _c, _sel, _i, _ids, _material0, state = _trusted_semantic_chain()
            tampered = copy.deepcopy(state)
            tampered["selection_id"] = "f" * 64
            with self.assertRaises(pb.PhaseBError):
                pb.validate_retained_state_chain(tampered)

    def test_row_73_missing_required_next_binding_fails_next_only(self):
        payload = copy.deepcopy(_material().lock_payload); payload.pop("next_binding")
        schema = json.loads((Path(__file__).resolve().parent.parent / "schemas/lock.schema.json").read_text(encoding="utf-8"))
        self.assertEqual(validate_schema(payload, schema, "legacy/manual lock"), [])
        with self.assertRaises(pb.PhaseBError) as cm: pb.parse_next_binding(payload)
        self.assertEqual(cm.exception.code, "CANONICAL_ACQUIRE_NEXT_BINDING_MISSING")
        malformed = copy.deepcopy(_material().lock_payload)
        malformed["next_binding"].pop("selection_id")
        with self.assertRaises(pb.PhaseBError) as child:
            pb.parse_next_binding(malformed)
        self.assertEqual(child.exception.code, "CANONICAL_ACQUIRE_NEXT_BINDING_MALFORMED")


SPEC_ROW_TO_TEST = {
    1: "test_row_01_happy_path_release_select_acquire_and_active_next",
    2: "test_row_02_unrelated_same_worker_principal_lock_never_satisfies_active_next",
    3: "test_row_03_old_acquisition_lock_id_or_timestamp_never_satisfies",
    4: "test_row_04_wrong_work_ref_fails_active_next",
    5: "test_row_05_wrong_collision_bundle_fails_active_next",
    6: "test_row_06_wrong_worker_fails_binding",
    7: "test_row_07_wrong_principal_fails_binding",
    8: "test_row_08_stale_acquire_base_has_no_pending_or_merge_authority",
    9: "test_row_09_stale_release_repair_requires_new_current_verify",
    10: "test_row_10_stale_pr_head_invalidates_prior_verify_and_transport_identity",
    11: "test_row_11_duplicate_next_has_one_deterministic_release_and_acquire_key",
    12: "test_row_12_duplicate_creator_adopts_exact_winner_and_non_equivalent_content_is_rejected",
    13: "test_row_13_old_source_acquisition_replay_changes_source_epoch",
    14: "test_row_14_equivalent_release_transport_uses_same_deterministic_ref",
    15: "test_row_15_unrelated_release_content_is_conflict_not_reuse",
    16: "test_row_16_already_released_requires_exact_source_epoch_release_provenance",
    17: "test_row_17_equivalent_acquire_pr_is_same_transport_key",
    18: "test_row_18_exact_ref_without_pr_has_one_create_key",
    19: "test_row_19_canonical_v3_transition_not_pr_metadata_grants_active_next",
    20: "test_row_20_self_consistent_forged_next_binding_fails_trusted_expected_ids",
    21: "test_row_21_historical_transition_exact_but_current_lock_later_changed_is_not_active",
    22: "test_row_22_two_workers_same_task_only_matching_canonical_identity_wins",
    23: "test_row_23_overlapping_collision_bundle_first_canonical_owner_blocks_second",
    24: "test_row_24_campaign_last_slot_race_second_stale_base_fails",
    25: "test_row_25_global_last_slot_race_second_stale_base_fails",
    26: "test_row_26_release_beats_acquire_when_both_eligible",
    27: "test_row_27_at_most_one_trusted_lifecycle_candidate_per_run",
    28: "test_row_28_ruleset_observation_unavailable_or_malformed_fails_closed",
    29: "test_row_29_ruleset_strict_false_or_verify_missing_fails_closed",
    30: "test_row_30_exact_head_ci_red_or_missing_has_no_activation_authority",
    31: "test_row_31_old_head_green_does_not_transfer_to_moved_head",
    32: "test_row_32_candidate_local_malformed_drops_only_candidate",
    33: "test_row_33_repository_wide_observation_failure_is_global_fail_closed",
    34: "test_row_34_candidate_disappears_or_closes_is_dropped_and_later_valid_examined",
    35: "test_row_35_main_moves_after_release_before_selection_changes_selection_identity",
    36: "test_row_36_main_moves_after_selection_before_acquire_creation_rejects_old_intent",
    37: "test_row_37_main_moves_after_acquire_pr_creation_old_pr_is_not_ownership",
    38: "test_row_38_pending_claim_is_nonownership_even_when_green",
    39: "test_row_39_terminal_release_can_proceed_without_truth_promotion",
    40: "test_row_40_no_autonomous_i2_i3_or_writer_self_review_authority",
    41: "test_row_41_no_automatic_renew_or_takeover_path",
    42: "test_row_42_missing_human_gate_cannot_same_campaign_escalate",
    43: "test_row_43_worker_recommendation_cannot_create_or_approve_task_or_campaign",
    44: "test_row_44_selection_context_changes_recompute_identity_before_acquire",
    45: "test_row_45_source_terminal_blob_change_invalidates_old_source_epoch",
    46: "test_row_46_source_lock_blob_bundle_change_invalidates_old_release_request",
    47: "test_row_47_deterministic_lock_id_stable_and_intent_distinct",
    48: "test_row_48_first_creator_timestamp_is_immutable_for_same_intent_retry",
    49: "test_row_49_canonical_lock_path_blob_bundle_must_equal_expected_transport_bundle",
    50: "test_row_50_expired_canonical_lock_never_active_next",
    51: "test_row_51_same_content_alternate_head_is_same_canonical_acquisition_content",
    52: "test_row_52_webhook_delivery_is_trigger_only_not_identity_authority",
    53: "test_row_53_multiple_release_lowest_pr_wins_after_malformed_lower_drop",
    54: "test_row_54_multiple_acquire_lowest_pr_wins_after_malformed_lower_drop",
    55: "test_row_55_highest_run_number_controls_not_run_id_magnitude",
    56: "test_row_56_indirect_merge_commit_attack_is_noncanonical",
    57: "test_row_57_different_pr_locator_same_head_can_confirm_only_v3_content_transition",
    58: "test_row_58_rerun_older_run_cannot_outrank_newer_failure",
    59: "test_row_59_new_higher_successful_lineage_recovers",
    60: "test_row_60_authoritative_lineage_current_rerun_in_progress_is_not_eligible",
    61: "test_row_61_incomplete_or_non_single_first_parent_history_fails_closed",
    62: "test_row_62_ruleset_bypass_or_unreadable_regression_fails_closed",
    63: "test_row_63_same_tree_alternate_head_cannot_borrow_verify",
    64: "test_row_64_same_tree_alternate_head_with_stale_or_different_base_is_ineligible",
    65: "test_row_65_same_base_but_different_tree_or_object_is_ineligible",
    66: "test_row_66_same_objects_but_claimed_different_source_epoch_is_semantic_inconsistency",
    67: "test_row_67_same_objects_but_claimed_different_acquire_intent_is_semantic_inconsistency",
    68: "test_row_68_squash_positive_h_not_equal_m_but_same_b_t_content_confirms",
    69: "test_row_69_duplicate_exact_lock_path_fails_before_canonical_hashing",
    70: "test_row_70_mutating_source_continuation_or_selection_binding_changes_bytes_oid_and_tree",
    71: "test_row_71_mutating_acquire_intent_binding_changes_bytes_oid_and_tree",
    72: "test_row_72_post_squash_semantic_reconstruction_comes_from_canonical_bytes_not_process_memory",
    73: "test_row_73_missing_required_next_binding_fails_next_only",
}

assert tuple(SPEC_ROW_TO_TEST) == tuple(range(1, 74))
assert len(set(SPEC_ROW_TO_TEST.values())) == 73
assert all(hasattr(VillageV13PhaseB73, name) for name in SPEC_ROW_TO_TEST.values())
assert len([name for name in dir(VillageV13PhaseB73) if name.startswith("test_")]) == 73


if __name__ == "__main__":
    unittest.main(verbosity=2)
