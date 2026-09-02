#!/usr/bin/env python3
from __future__ import annotations

from pathlib import Path
import argparse
import json
import re
import subprocess
import tempfile

from village_core import VillageState, is_lock_only_paths, lock_bundle_active, parse_time, path_matches
from village_v1_2 import ReleaseBinding, load_actor_policy, new_worker_lock_errors, parse_release_head_ref, release_terminal_state, validate_abandoned_terminal_record, worker_lock_errors
from workflow_security import repository_workflow_security_errors

LOCK_PREFIX = "coordination/locks/"
ABANDONED_PATH_RE = re.compile(r"^work/(TASK-[A-Z0-9-]+)/(w-[0-9a-f]{16,32})/ABANDONED_TERMINAL\.yml$")
BOOTSTRAP_MAINTAINERS = {"51mns"}
BOOTSTRAP_PROTECTED = [
    "README.md", "README.ja.md", "AGENTS.md", "CONTRIBUTING.md", "LICENSING.md", "REUSE.toml", "LICENSES/**", "SECURITY.md",
    "docs/VILLAGE_CONSTITUTION.md", "docs/VILLAGE_ARCHITECTURE.md", "docs/VILLAGE_ARCHITECTURE_V1_1.md", "docs/VILLAGE_ARCHITECTURE_V1_2.md", "docs/VILLAGE_ARCHITECTURE_V1_2_1.md", "docs/CONTINUATION_GATE.md", "docs/GITHUB_SETTINGS_REQUIRED.md", "docs/RESEARCH_PORTFOLIO.md", "docs/RESEARCH_BOARD.md", "docs/DEPENDENCY_GRAPH.md", "docs/CAMPAIGN_HISTORY.md", "docs/RESEARCH_EVALUATIONS.md",
    "coordination/portfolio/**", "coordination/policy/**", "coordination/evaluations/README.md", "coordination/campaigns/**/CAMPAIGN.yml", "coordination/tasks/**/TASK.yml", "research/**/CLAIM.yml", "schemas/**", ".github/workflows/**", ".github/CODEOWNERS",
    "scripts/public_release_audit.py", "scripts/village.py", "scripts/village_core.py", "scripts/village_rank.py", "scripts/village_v1_2.py", "scripts/lock_auto_activate.py", "scripts/workflow_security.py", "scripts/check_dco.py", "scripts/check_village_pr.py", "scripts/test_village_acceptance.py", "scripts/test_village_v1_1.py", "scripts/test_village_v1_2.py", "scripts/test_village_v1_2_1.py", "scripts/verify_public_layout.py",
]
BOOTSTRAP_GOVERNANCE_ONLY = list(BOOTSTRAP_PROTECTED)


def git(*args: str) -> str:
    return subprocess.check_output(["git", *args], text=True).strip()


def show_json(ref: str, path: str):
    try:
        text = subprocess.check_output(["git", "show", f"{ref}:{path}"], text=True)
        return json.loads(text)
    except (subprocess.CalledProcessError, json.JSONDecodeError):
        return None


def changed_paths(base: str, head: str) -> list[str]:
    out = git("diff", "--no-renames", "--name-only", f"{base}..{head}")
    return [x for x in out.splitlines() if x]


def changed_status(base: str, head: str) -> list[tuple[str, str]]:
    out = git("diff", "--no-renames", "--name-status", f"{base}..{head}")
    rows = []
    for line in out.splitlines():
        if line:
            parts = line.split("\t")
            rows.append((parts[0], parts[-1]))
    return rows


def is_lock_path(path: str) -> bool:
    return path.startswith(LOCK_PREFIX)


def lock_change_class_errors(paths: list[str]) -> list[str]:
    if any(is_lock_path(path) for path in paths) and not is_lock_only_paths(paths):
        return ["lock lifecycle paths may not be mixed with research/governance/other files; any coordination/locks/** change requires a dedicated lock-only PR"]
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
    errors = []
    for path in paths:
        if not is_lock_path(path):
            continue
        for label, ref in (("base", base), ("head", head)):
            entry = git_entry(ref, path)
            if entry is None:
                continue
            mode, object_type = entry
            if mode != "100644" or object_type != "blob":
                errors.append(f"{label} lock path must be regular Git blob mode 100644, got {mode}/{object_type}: {path}")
    return errors


def abandoned_terminal_transition_errors(base: str, head: str, rows: list[tuple[str, str]]) -> list[str]:
    errors = []
    for status, path in rows:
        match = ABANDONED_PATH_RE.fullmatch(path)
        if not match:
            continue
        task_id, worker_id = match.groups()
        for label, ref in (("base", base), ("head", head)):
            entry = git_entry(ref, path)
            if entry is not None and entry != ("100644", "blob"):
                errors.append(f"{label} ABANDONED_TERMINAL must be regular Git blob mode 100644: {path}")
        if status == "D":
            errors.append(f"ABANDONED_TERMINAL is durable availability state and may not be deleted: {path}")
            continue
        new = show_json(head, path)
        if not isinstance(new, dict):
            errors.append(f"malformed ABANDONED_TERMINAL JSON-subset data: {path}")
            continue
        new_errors = validate_abandoned_terminal_record(new, root=".", expected_task_id=task_id, expected_worker_id=worker_id)
        errors.extend(f"{path}: {item}" for item in new_errors)
        if new_errors:
            continue
        if status == "A":
            if new.get("abandonment_count") != 1:
                errors.append(f"{path}: initial abandonment_count must be 1")
            continue
        if status != "M":
            errors.append(f"{path}: unsupported terminal marker change status {status}")
            continue
        old = show_json(base, path)
        if not isinstance(old, dict):
            errors.append(f"{path}: modified terminal marker lacks a valid base record")
            continue
        old_errors = validate_abandoned_terminal_record(old, root=".", expected_task_id=task_id, expected_worker_id=worker_id)
        errors.extend(f"{path}: base: {item}" for item in old_errors)
        if old_errors:
            continue
        if new.get("abandonment_count") != old.get("abandonment_count", 0) + 1:
            errors.append(f"{path}: abandonment_count must increment by exactly one")
        try:
            if parse_time(new["abandoned_at"]) <= parse_time(old["abandoned_at"]):
                errors.append(f"{path}: abandoned_at must increase on repeated abandonment")
        except Exception:
            pass
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
        td.cleanup(); raise RuntimeError("failed to materialize git ref")
    return td


def _validate_new_lock(base_state: VillageState, bundle, *, actor: str, base_sha: str) -> list[str]:
    errors = []
    tid = bundle.payload.get("task_id"); expected_actor = f"gh:{actor}"
    if bundle.payload.get("actor", {}).get("id") != expected_actor: errors.append(f"lock actor must match PR actor {expected_actor}")
    if bundle.payload.get("base_main_sha") != base_sha: errors.append("lock base_main_sha must equal PR base SHA")
    if tid not in base_state.tasks:
        errors.append(f"unknown base task {tid}"); return errors
    ready, reasons = base_state.readiness(tid)
    if not ready: errors.append(f"task {tid} was not READY on base: {'; '.join(reasons)}")
    task = base_state.tasks[tid]
    if set(bundle.payload.get("collision_keys", [])) != set(task.get("collision_keys", [])): errors.append("lock collision_keys must exactly match Task collision_keys")
    try:
        ttl = (parse_time(bundle.payload["expires_at"]) - parse_time(bundle.payload["acquired_at"])).total_seconds() / 3600
        if abs(ttl - task.get("lease_ttl_hours", 168)) > 1e-6: errors.append("lock lease duration must equal task lease_ttl_hours")
    except Exception: errors.append("invalid lock lease timestamps")
    if bundle.payload.get("renewal_count") != 0: errors.append("new acquisition renewal_count must be 0")
    cap = base_state.portfolio.get("governance", {}).get("default_actor_exclusive_lock_cap", 12)
    if task.get("parallelism") == "EXCLUSIVE":
        actor_active = sum(1 for b in base_state.active_lock_bundles() if b.payload.get("actor", {}).get("id") == expected_actor and base_state.tasks.get(b.payload.get("task_id"), {}).get("parallelism") == "EXCLUSIVE")
        if actor_active >= cap: errors.append(f"principal compatibility EXCLUSIVE cap {cap} already reached")
    errors.extend(new_worker_lock_errors(base_state, bundle, actor_policy=load_actor_policy(base_state.root)))
    return errors


def _release_errors(base_state: VillageState, old, *, actor: str, maintainers: set[str], binding: ReleaseBinding | None) -> list[str]:
    errors = []
    expected_actor = f"gh:{actor}"; is_maintainer = actor in maintainers
    if old.payload.get("actor", {}).get("id") != expected_actor and not is_maintainer: errors.append("only the lock owner or a maintainer may release a lock")
    if binding is None:
        return errors
    if binding.task_id != old.payload.get("task_id"): errors.append("RELEASE request Task does not match canonical lock task_id")
    if binding.worker_id != old.payload.get("worker_id"): errors.append("RELEASE request worker does not match canonical lock worker_id")
    task = base_state.tasks.get(old.payload.get("task_id"))
    if not task: errors.append("canonical RELEASE lock references unknown Task")
    elif set(old.payload.get("collision_keys", [])) != set(task.get("collision_keys", [])): errors.append("canonical RELEASE lock collision_keys do not exactly match current Task")
    terminal, terminal_errors = release_terminal_state(base_state.root, old.payload, now=base_state.now)
    if terminal == "NONE": errors.extend(terminal_errors)
    return errors


def validate_lock_transition(base_state: VillageState, head_state: VillageState, *, actor: str, base_sha: str, maintainers: set[str], release_binding: ReleaseBinding | None = None) -> tuple[str, list[str]]:
    errors = []
    before = set(base_state.lock_bundles); after = set(head_state.lock_bundles)
    added = after - before; removed = before - after; common = before & after
    changed = {lid for lid in common if base_state.lock_bundles[lid].payload != head_state.lock_bundles[lid].payload or base_state.lock_bundles[lid].keys != head_state.lock_bundles[lid].keys}
    expected_actor = f"gh:{actor}"; is_maintainer = actor in maintainers
    if changed and (added or removed or len(changed) != 1): return "INVALID", ["lock PR must perform exactly one lifecycle operation"]
    if changed:
        lid = next(iter(changed)); old = base_state.lock_bundles[lid]; new = head_state.lock_bundles[lid]; operation = "RENEW"
        if old.payload.get("actor", {}).get("id") != expected_actor and not is_maintainer: errors.append("only the lock owner or a maintainer may renew a lock")
        if not lock_bundle_active(old, base_state.now): errors.append("expired lock cannot be self-renewed; use takeover or maintainer action")
        for field in ("lock_id", "task_id", "actor", "worker_id", "base_main_sha", "acquired_at", "work_ref", "collision_keys"):
            if old.payload.get(field) != new.payload.get(field): errors.append(f"renewal may not change {field}")
        if old.keys != new.keys: errors.append("renewal may not change collision-key file set")
        if new.payload.get("renewal_count") != old.payload.get("renewal_count", 0) + 1: errors.append("renewal_count must increment by exactly one")
        limit = base_state.portfolio.get("governance", {}).get("self_renewal_limit", 1)
        if not is_maintainer and new.payload.get("renewal_count", 0) > limit: errors.append(f"self-renewal limit {limit} exceeded; maintainer decision required")
        if not new.payload.get("progress_artifact"): errors.append("renewal requires progress_artifact")
        tid = old.payload.get("task_id"); ttl = base_state.tasks.get(tid, {}).get("lease_ttl_hours", 168)
        extension = (parse_time(new.payload["expires_at"]) - parse_time(old.payload["expires_at"])).total_seconds() / 3600
        if abs(extension - ttl) > 1e-6: errors.append("renewal must extend expires_at by exactly task lease_ttl_hours")
        return operation, errors
    if len(added) == 0 and len(removed) == 1:
        old = base_state.lock_bundles[next(iter(removed))]
        errors.extend(_release_errors(base_state, old, actor=actor, maintainers=maintainers, binding=release_binding))
        return "RELEASE", errors
    if len(added) == 1:
        new = head_state.lock_bundles[next(iter(added))]
        operation = "TAKEOVER" if removed else "ACQUIRE"
        if removed:
            for lid in removed:
                old = base_state.lock_bundles[lid]
                if lock_bundle_active(old, base_state.now): errors.append(f"cannot take over active lock {lid}")
                if not old.keys.intersection(new.keys): errors.append(f"takeover removed unrelated expired lock {lid}")
        errors.extend(_validate_new_lock(base_state, new, actor=actor, base_sha=base_sha))
        return operation, errors
    return "INVALID", ["lock-only PR must acquire one lock, release one lock, renew one lock, or replace expired conflicting lock(s)"]


def validate_lock_only(base: str, head: str, actor: str, maintainers: set[str], *, head_ref: str | None = None) -> tuple[str, list[str]]:
    base_td = materialize_ref(base); head_td = materialize_ref(head)
    try:
        base_state = VillageState(base_td.name).load(); base_errors = list(base_state.validate()) + worker_lock_errors(base_state, load_actor_policy(base_td.name))
        if base_errors: return "INVALID", ["base Village state is invalid; lock operation cannot proceed", *base_errors[:20]]
        head_state = VillageState(head_td.name).load(); head_errors = list(head_state.validate()) + worker_lock_errors(head_state, load_actor_policy(head_td.name))
        if head_errors: return "INVALID", ["proposed head Village state is invalid", *head_errors[:20]]
        binding = parse_release_head_ref(head_ref)
        operation, errors = validate_lock_transition(base_state, head_state, actor=actor, base_sha=base, maintainers=maintainers, release_binding=binding)
        if operation == "RELEASE" and binding is None: errors.append("RELEASE PR head ref must exactly match release/<TASK-ID>/<worker-id>")
        return operation, errors
    finally:
        base_td.cleanup(); head_td.cleanup()


def _merge_unique(base_patterns: list[str], head_patterns: list[str]) -> list[str]:
    return list(dict.fromkeys([*base_patterns, *head_patterns]))


def main() -> int:
    ap = argparse.ArgumentParser(); ap.add_argument("--base", required=True); ap.add_argument("--head", required=True); ap.add_argument("--actor", required=True); ap.add_argument("--head-ref"); ap.add_argument("--github-output"); args = ap.parse_args()
    paths = changed_paths(args.base, args.head); rows = changed_status(args.base, args.head); lock_only = is_lock_only_paths(paths)
    base_maint = show_json(args.base, "coordination/policy/MAINTAINERS.yml"); maintainers = set(base_maint.get("maintainers", [])) if base_maint else BOOTSTRAP_MAINTAINERS
    base_protected = show_json(args.base, "coordination/policy/PROTECTED_PATHS.yml"); protected = base_protected.get("protected_patterns", BOOTSTRAP_PROTECTED) if base_protected else BOOTSTRAP_PROTECTED; governance_only = base_protected.get("governance_only_patterns", BOOTSTRAP_GOVERNANCE_ONLY) if base_protected else BOOTSTRAP_GOVERNANCE_ONLY
    if args.actor in maintainers:
        head_protected = show_json(args.head, "coordination/policy/PROTECTED_PATHS.yml")
        if head_protected:
            protected = _merge_unique(protected, head_protected.get("protected_patterns", [])); governance_only = _merge_unique(governance_only, head_protected.get("governance_only_patterns", []))
    bootstrap = show_json(args.base, "coordination/portfolio/PORTFOLIO.yml") is None; errors = []
    errors.extend(lock_change_class_errors(paths)); errors.extend(lock_object_mode_errors(args.base, args.head, paths)); errors.extend(abandoned_terminal_transition_errors(args.base, args.head, rows)); errors.extend(repository_workflow_security_errors("."))
    protected_changed = [p for p in paths if path_matches(p, protected)]
    if protected_changed and args.actor not in maintainers: errors.append("non-maintainer changed protected governance path(s): " + ", ".join(protected_changed))
    gov_changed = [p for p in paths if path_matches(p, governance_only)]; nongov = [p for p in paths if not path_matches(p, governance_only)]
    if gov_changed and nongov and not (bootstrap and args.actor in maintainers): errors.append("governance-only paths must be changed in a dedicated governance PR")
    lock_operation = "NONE"
    if lock_only:
        lock_operation, lock_errors = validate_lock_only(args.base, args.head, args.actor, maintainers, head_ref=args.head_ref); errors.extend(lock_errors)
    if args.github_output:
        with Path(args.github_output).open("a", encoding="utf-8") as fh:
            fh.write(f"lock_only={'true' if lock_only else 'false'}\n"); fh.write(f"lock_operation={lock_operation}\n")
    print("PR_CHANGE_CLASS=" + ("LOCK_ONLY" if lock_only else "NORMAL"))
    if lock_only: print("LOCK_OPERATION=" + lock_operation)
    if errors:
        print("FAIL: Village PR policy")
        for e in list(dict.fromkeys(errors)): print(" -", e)
        return 1
    print("PASS: Village PR policy"); return 0


if __name__ == "__main__":
    raise SystemExit(main())
