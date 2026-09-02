#!/usr/bin/env python3
from __future__ import annotations

from pathlib import Path
import argparse
import json
import subprocess
import tempfile

from village_core import (
    VillageState,
    is_lock_only_paths,
    lock_bundle_active,
    parse_time,
    path_matches,
    workflow_safety_errors,
)
from village_v1_2 import (
    load_actor_policy,
    new_worker_lock_errors,
    trusted_lock_activation_workflow_errors,
    worker_lock_errors,
)

LOCK_PREFIX = "coordination/locks/"
BOOTSTRAP_MAINTAINERS = {"51mns"}
BOOTSTRAP_PROTECTED = [
    "README.md", "README.ja.md", "AGENTS.md", "CONTRIBUTING.md", "LICENSING.md",
    "REUSE.toml", "LICENSES/**", "SECURITY.md",
    "docs/VILLAGE_CONSTITUTION.md", "docs/VILLAGE_ARCHITECTURE.md",
    "docs/VILLAGE_ARCHITECTURE_V1_1.md", "docs/VILLAGE_ARCHITECTURE_V1_2.md",
    "docs/CONTINUATION_GATE.md", "docs/GITHUB_SETTINGS_REQUIRED.md",
    "docs/RESEARCH_PORTFOLIO.md", "docs/RESEARCH_BOARD.md", "docs/DEPENDENCY_GRAPH.md",
    "docs/CAMPAIGN_HISTORY.md", "docs/RESEARCH_EVALUATIONS.md",
    "coordination/portfolio/**", "coordination/policy/**", "coordination/evaluations/README.md",
    "coordination/campaigns/**/CAMPAIGN.yml", "coordination/tasks/**/TASK.yml",
    "research/**/CLAIM.yml", "schemas/**", ".github/workflows/**", ".github/CODEOWNERS",
    "scripts/public_release_audit.py", "scripts/village.py", "scripts/village_core.py",
    "scripts/village_rank.py", "scripts/village_v1_2.py", "scripts/lock_auto_activate.py",
    "scripts/check_dco.py", "scripts/check_village_pr.py", "scripts/test_village_acceptance.py",
    "scripts/test_village_v1_1.py", "scripts/test_village_v1_2.py", "scripts/verify_public_layout.py",
]
BOOTSTRAP_GOVERNANCE_ONLY = list(BOOTSTRAP_PROTECTED)


def git(*args: str) -> str:
    return subprocess.check_output(["git", *args], text=True).strip()


def show_json(ref: str, path: str):
    try:
        text = subprocess.check_output(["git", "show", f"{ref}:{path}"], text=True)
    except subprocess.CalledProcessError:
        return None
    return json.loads(text)


def changed_paths(base: str, head: str) -> list[str]:
    # Disable rename collapsing so deletion/movement of a lock path cannot hide
    # inside a rename to an ordinary research path.
    out = git("diff", "--no-renames", "--name-only", f"{base}..{head}")
    return [x for x in out.splitlines() if x]


def changed_status(base: str, head: str) -> list[tuple[str, str]]:
    out = git("diff", "--no-renames", "--name-status", f"{base}..{head}")
    rows: list[tuple[str, str]] = []
    for line in out.splitlines():
        if line:
            parts = line.split("\t")
            rows.append((parts[0], parts[-1]))
    return rows


def is_lock_path(path: str) -> bool:
    return path.startswith(LOCK_PREFIX)


def lock_change_class_errors(paths: list[str]) -> list[str]:
    """Any lock path change must live in a dedicated exact lock-only PR."""
    has_lock_change = any(is_lock_path(path) for path in paths)
    if has_lock_change and not is_lock_only_paths(paths):
        return [
            "lock lifecycle paths may not be mixed with research/governance/other files; "
            "any coordination/locks/** change requires a dedicated lock-only PR"
        ]
    return []


def git_entry(ref: str, path: str) -> tuple[str, str] | None:
    out = git("ls-tree", ref, "--", path)
    if not out:
        return None
    first = out.splitlines()[0]
    meta, _, returned_path = first.partition("\t")
    parts = meta.split()
    if len(parts) < 3 or returned_path != path:
        return ("INVALID", "INVALID")
    return parts[0], parts[1]


def lock_object_mode_errors(base: str, head: str, paths: list[str]) -> list[str]:
    """Canonical lock files must be ordinary Git blobs, never symlinks/submodules."""
    errors: list[str] = []
    for path in paths:
        if not is_lock_path(path):
            continue
        for label, ref in (("base", base), ("head", head)):
            entry = git_entry(ref, path)
            if entry is None:
                continue
            mode, object_type = entry
            if mode != "100644" or object_type != "blob":
                errors.append(
                    f"{label} lock path must be regular Git blob mode 100644, got {mode}/{object_type}: {path}"
                )
    return errors


def materialize_ref(ref: str) -> tempfile.TemporaryDirectory:
    td = tempfile.TemporaryDirectory(prefix="aimath-village-ref-")
    dest = Path(td.name)
    archive = subprocess.Popen(["git", "archive", ref], stdout=subprocess.PIPE)
    assert archive.stdout is not None
    tar = subprocess.run(["tar", "-x", "-C", str(dest)], stdin=archive.stdout)
    archive.stdout.close()
    rc = archive.wait()
    if rc or tar.returncode:
        td.cleanup()
        raise RuntimeError("failed to materialize git ref")
    return td


def _validate_new_lock(base_state: VillageState, bundle, *, actor: str, base_sha: str) -> list[str]:
    errors: list[str] = []
    tid = bundle.payload.get("task_id")
    expected_actor = f"gh:{actor}"
    if bundle.payload.get("actor", {}).get("id") != expected_actor:
        errors.append(f"lock actor must match PR actor {expected_actor}")
    if bundle.payload.get("base_main_sha") != base_sha:
        errors.append("lock base_main_sha must equal PR base SHA")
    if tid not in base_state.tasks:
        errors.append(f"unknown base task {tid}")
        return errors
    ready, reasons = base_state.readiness(tid)
    if not ready:
        errors.append(f"task {tid} was not READY on base: {'; '.join(reasons)}")
    task = base_state.tasks[tid]
    if set(bundle.payload.get("collision_keys", [])) != set(task.get("collision_keys", [])):
        errors.append("lock collision_keys must exactly match Task collision_keys")
    try:
        ttl = (parse_time(bundle.payload["expires_at"]) - parse_time(bundle.payload["acquired_at"])).total_seconds() / 3600
        if abs(ttl - task.get("lease_ttl_hours", 168)) > 1e-6:
            errors.append("lock lease duration must equal task lease_ttl_hours")
    except Exception:
        errors.append("invalid lock lease timestamps")
    if bundle.payload.get("renewal_count") != 0:
        errors.append("new acquisition renewal_count must be 0")

    # Compatibility principal ceiling is intentionally no stricter than the global
    # active-lane cap in v1.2. Worker-level scheduling is enforced separately.
    cap = base_state.portfolio.get("governance", {}).get("default_actor_exclusive_lock_cap", 12)
    if task.get("parallelism") == "EXCLUSIVE":
        actor_active = sum(
            1
            for b in base_state.active_lock_bundles()
            if b.payload.get("actor", {}).get("id") == expected_actor
            and base_state.tasks.get(b.payload.get("task_id"), {}).get("parallelism") == "EXCLUSIVE"
        )
        if actor_active >= cap:
            errors.append(f"principal compatibility EXCLUSIVE cap {cap} already reached")

    errors.extend(
        new_worker_lock_errors(
            base_state,
            bundle,
            actor_policy=load_actor_policy(base_state.root),
        )
    )
    return errors


def validate_lock_transition(
    base_state: VillageState,
    head_state: VillageState,
    *,
    actor: str,
    base_sha: str,
    maintainers: set[str],
) -> tuple[str, list[str]]:
    """Validate exactly one lock lifecycle operation: acquire/release/renew/takeover."""
    errors: list[str] = []
    before = set(base_state.lock_bundles)
    after = set(head_state.lock_bundles)
    added = after - before
    removed = before - after
    common = before & after
    changed = {
        lid
        for lid in common
        if base_state.lock_bundles[lid].payload != head_state.lock_bundles[lid].payload
        or base_state.lock_bundles[lid].keys != head_state.lock_bundles[lid].keys
    }
    expected_actor = f"gh:{actor}"
    is_maintainer = actor in maintainers

    if changed and (added or removed or len(changed) != 1):
        return "INVALID", ["lock PR must perform exactly one lifecycle operation"]

    if changed:
        lid = next(iter(changed))
        old = base_state.lock_bundles[lid]
        new = head_state.lock_bundles[lid]
        operation = "RENEW"
        if old.payload.get("actor", {}).get("id") != expected_actor and not is_maintainer:
            errors.append("only the lock owner or a maintainer may renew a lock")
        if not lock_bundle_active(old, base_state.now):
            errors.append("expired lock cannot be self-renewed; use takeover or maintainer action")
        immutable = (
            "lock_id", "task_id", "actor", "worker_id", "base_main_sha", "acquired_at",
            "work_ref", "collision_keys",
        )
        for field in immutable:
            if old.payload.get(field) != new.payload.get(field):
                errors.append(f"renewal may not change {field}")
        if old.keys != new.keys:
            errors.append("renewal may not change collision-key file set")
        if new.payload.get("renewal_count") != old.payload.get("renewal_count", 0) + 1:
            errors.append("renewal_count must increment by exactly one")
        limit = base_state.portfolio.get("governance", {}).get("self_renewal_limit", 1)
        if not is_maintainer and new.payload.get("renewal_count", 0) > limit:
            errors.append(f"self-renewal limit {limit} exceeded; maintainer decision required")
        if not new.payload.get("progress_artifact"):
            errors.append("renewal requires progress_artifact")
        tid = old.payload.get("task_id")
        ttl = base_state.tasks.get(tid, {}).get("lease_ttl_hours", 168)
        extension = (parse_time(new.payload["expires_at"]) - parse_time(old.payload["expires_at"])).total_seconds() / 3600
        if abs(extension - ttl) > 1e-6:
            errors.append("renewal must extend expires_at by exactly task lease_ttl_hours")
        return operation, errors

    if len(added) == 0 and len(removed) == 1:
        operation = "RELEASE"
        old = base_state.lock_bundles[next(iter(removed))]
        if old.payload.get("actor", {}).get("id") != expected_actor and not is_maintainer:
            errors.append("only the lock owner or a maintainer may release a lock")
        return operation, errors

    if len(added) == 1:
        new = head_state.lock_bundles[next(iter(added))]
        if removed:
            operation = "TAKEOVER"
            for lid in removed:
                old = base_state.lock_bundles[lid]
                if lock_bundle_active(old, base_state.now):
                    errors.append(f"cannot take over active lock {lid}")
                if not old.keys.intersection(new.keys):
                    errors.append(f"takeover removed unrelated expired lock {lid}")
        else:
            operation = "ACQUIRE"
        errors.extend(_validate_new_lock(base_state, new, actor=actor, base_sha=base_sha))
        return operation, errors

    return "INVALID", [
        "lock-only PR must acquire one lock, release one lock, renew one lock, or replace expired conflicting lock(s)"
    ]


def validate_lock_only(base: str, head: str, actor: str, maintainers: set[str]) -> tuple[str, list[str]]:
    base_td = materialize_ref(base)
    head_td = materialize_ref(head)
    try:
        base_state = VillageState(base_td.name).load()
        base_errors = list(base_state.validate()) + worker_lock_errors(base_state, load_actor_policy(base_td.name))
        if base_errors:
            return "INVALID", ["base Village state is invalid; lock operation cannot proceed", *base_errors[:20]]
        head_state = VillageState(head_td.name).load()
        head_errors = list(head_state.validate()) + worker_lock_errors(head_state, load_actor_policy(head_td.name))
        if head_errors:
            return "INVALID", ["proposed head Village state is invalid", *head_errors[:20]]
        return validate_lock_transition(
            base_state,
            head_state,
            actor=actor,
            base_sha=base,
            maintainers=maintainers,
        )
    finally:
        base_td.cleanup()
        head_td.cleanup()


def _merge_unique(base_patterns: list[str], head_patterns: list[str]) -> list[str]:
    return list(dict.fromkeys([*base_patterns, *head_patterns]))


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--base", required=True)
    ap.add_argument("--head", required=True)
    ap.add_argument("--actor", required=True)
    ap.add_argument("--github-output")
    args = ap.parse_args()
    paths = changed_paths(args.base, args.head)
    lock_only = is_lock_only_paths(paths)

    base_maint = show_json(args.base, "coordination/policy/MAINTAINERS.yml")
    maintainers = set(base_maint.get("maintainers", [])) if base_maint else BOOTSTRAP_MAINTAINERS
    base_protected = show_json(args.base, "coordination/policy/PROTECTED_PATHS.yml")
    protected = base_protected.get("protected_patterns", BOOTSTRAP_PROTECTED) if base_protected else BOOTSTRAP_PROTECTED
    governance_only = base_protected.get("governance_only_patterns", BOOTSTRAP_GOVERNANCE_ONLY) if base_protected else BOOTSTRAP_GOVERNANCE_ONLY

    if args.actor in maintainers:
        head_protected = show_json(args.head, "coordination/policy/PROTECTED_PATHS.yml")
        if head_protected:
            protected = _merge_unique(protected, head_protected.get("protected_patterns", []))
            governance_only = _merge_unique(governance_only, head_protected.get("governance_only_patterns", []))

    bootstrap = show_json(args.base, "coordination/portfolio/PORTFOLIO.yml") is None
    errors: list[str] = []
    errors.extend(lock_change_class_errors(paths))
    errors.extend(lock_object_mode_errors(args.base, args.head, paths))

    protected_changed = [p for p in paths if path_matches(p, protected)]
    if protected_changed and args.actor not in maintainers:
        errors.append("non-maintainer changed protected governance path(s): " + ", ".join(protected_changed))

    gov_changed = [p for p in paths if path_matches(p, governance_only)]
    nongov = [p for p in paths if not path_matches(p, governance_only)]
    if gov_changed and nongov and not (bootstrap and args.actor in maintainers):
        errors.append("governance-only paths must be changed in a dedicated governance PR")

    for status, path in changed_status(args.base, args.head):
        if path.startswith(".github/workflows/") and status != "D":
            try:
                text = git("show", f"{args.head}:{path}")
            except subprocess.CalledProcessError:
                continue
            if path == ".github/workflows/lock-auto-activate.yml":
                errors.extend(f"{path}: {e}" for e in trusted_lock_activation_workflow_errors(text))
            else:
                errors.extend(f"{path}: {e}" for e in workflow_safety_errors(text))

    lock_operation = "NONE"
    if lock_only:
        lock_operation, lock_errors = validate_lock_only(args.base, args.head, args.actor, maintainers)
        errors.extend(lock_errors)

    if args.github_output:
        with Path(args.github_output).open("a", encoding="utf-8") as fh:
            fh.write(f"lock_only={'true' if lock_only else 'false'}\n")
            fh.write(f"lock_operation={lock_operation}\n")
    print("PR_CHANGE_CLASS=" + ("LOCK_ONLY" if lock_only else "NORMAL"))
    if lock_only:
        print("LOCK_OPERATION=" + lock_operation)
    if errors:
        print("FAIL: Village PR policy")
        for e in errors:
            print(" -", e)
        return 1
    print("PASS: Village PR policy")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
