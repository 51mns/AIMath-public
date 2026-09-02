# SPDX-FileCopyrightText: 2026 AIMath contributors
# SPDX-License-Identifier: Apache-2.0
from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path, PurePosixPath
import base64
import json
import os
import re
import shutil
import subprocess
import tempfile
import urllib.error
import urllib.parse
import urllib.request

from check_village_pr import validate_lock_transition
from village_core import VillageState
from village_v1_2 import abandonment_state, load_actor_policy, load_autonomous_lock_principals, new_worker_lock_errors, parse_release_head_ref, release_terminal_state, worker_lock_errors

API_ROOT = "https://api.github.com"
VERIFY_WORKFLOW_NAME = "Verify public release"
SHA_RE = re.compile(r"^[0-9a-f]{40}$")


class AutoActivationError(RuntimeError):
    pass


@dataclass(frozen=True)
class AutoReleaseCandidate:
    pr: dict
    files: list[dict]
    bundle_id: str
    terminal_class: str


def choose_release_candidate(candidates: list[AutoReleaseCandidate]) -> AutoReleaseCandidate | None:
    """Order only candidates already proven eligible right now."""
    return min(candidates, key=lambda c: int(c.pr["number"])) if candidates else None


def automatic_release_identity_errors(pr: dict, bundle, binding) -> list[str]:
    errors = []
    login = pr.get("user", {}).get("login", "")
    if bundle.payload.get("actor", {}).get("id") != f"gh:{login}":
        errors.append("automatic RELEASE does not permit maintainer override of canonical lock principal")
    if binding is None:
        errors.append("automatic RELEASE lacks exact task/worker head-ref binding")
        return errors
    if bundle.payload.get("task_id") != binding.task_id: errors.append("automatic RELEASE Task binding mismatch")
    if bundle.payload.get("worker_id") != binding.worker_id: errors.append("automatic RELEASE worker binding mismatch")
    return errors


def _safe_lock_path(path: str) -> bool:
    if not isinstance(path, str) or not path.startswith("coordination/locks/") or not path.endswith(".yml"):
        return False
    p = PurePosixPath(path)
    return not p.is_absolute() and all(part not in {"", ".", ".."} for part in p.parts) and "\\" not in path


def auto_activation_preflight(run: dict, pr: dict, files: list[dict], *, repository: str, current_main_sha: str, maintainers: set[str]) -> tuple[bool, list[str]]:
    errors = []
    if run.get("name") != VERIFY_WORKFLOW_NAME: errors.append("source workflow is not Verify public release")
    if run.get("event") != "pull_request": errors.append("source workflow was not a pull_request run")
    if run.get("status") != "completed" or run.get("conclusion") != "success": errors.append("verify workflow is not completed/success")
    if pr.get("state") != "open": errors.append("PR is not open")
    if pr.get("draft"): errors.append("draft PR is not auto-activatable")
    if pr.get("base", {}).get("ref") != "main": errors.append("PR base is not main")
    if pr.get("base", {}).get("sha") != current_main_sha: errors.append("PR base is stale relative to current main")
    if pr.get("head", {}).get("sha") != run.get("head_sha"): errors.append("PR head does not match verified workflow head")
    if pr.get("head", {}).get("repo", {}).get("full_name") != repository: errors.append("external/fork head is not eligible for v1.2 auto activation")
    if pr.get("user", {}).get("login") not in maintainers: errors.append("PR principal is not pre-authorized maintainer")
    if not files: errors.append("PR has no changed files")
    if len(files) > 16: errors.append("lock-only PR changed too many files")
    for item in files:
        name = item.get("filename", "")
        if item.get("status") != "added": errors.append(f"auto activation permits ACQUIRE additions only: {name}")
        if not _safe_lock_path(name): errors.append(f"non-lock/unsafe path in auto activation candidate: {name}")
        if not isinstance(item.get("sha"), str) or not SHA_RE.fullmatch(item.get("sha", "")): errors.append(f"PR file is missing exact Git blob SHA: {name}")
    return not errors, list(dict.fromkeys(errors))


def auto_release_preflight(pr: dict, files: list[dict], *, repository: str, current_main_sha: str, release_principals: set[str]) -> tuple[bool, list[str]]:
    errors = []
    if pr.get("state") != "open": errors.append("PR is not open")
    if pr.get("draft"): errors.append("draft PR is not auto-releasable")
    if pr.get("base", {}).get("ref") != "main": errors.append("PR base is not main")
    if pr.get("base", {}).get("sha") != current_main_sha: errors.append("PR base is stale relative to current main")
    if pr.get("head", {}).get("repo", {}).get("full_name") != repository: errors.append("external/fork head is not eligible for automatic RELEASE")
    if pr.get("user", {}).get("login") not in release_principals: errors.append("PR principal is not authorized for automatic RELEASE")
    if parse_release_head_ref(pr.get("head", {}).get("ref")) is None: errors.append("RELEASE head ref must exactly match release/<TASK-ID>/<worker-id>")
    if not files: errors.append("RELEASE PR has no changed files")
    if len(files) > 16: errors.append("RELEASE PR changed too many files")
    for item in files:
        name = item.get("filename", "")
        if item.get("status") != "removed": errors.append(f"automatic RELEASE permits deletions only; replacement/modified lock forbidden: {name}")
        if not _safe_lock_path(name): errors.append(f"non-lock/unsafe path in automatic RELEASE candidate: {name}")
        if not isinstance(item.get("sha"), str) or not SHA_RE.fullmatch(item.get("sha", "")): errors.append(f"PR file is missing exact base Git blob SHA: {name}")
    return not errors, list(dict.fromkeys(errors))


def lock_git_object_errors(files: list[dict], tree_entries: list[dict]) -> list[str]:
    by_path = {entry.get("path"): entry for entry in tree_entries if isinstance(entry, dict)}
    errors = []
    for item in files:
        path = item.get("filename", ""); entry = by_path.get(path)
        if not entry:
            errors.append(f"lock path missing from exact Git tree: {path}"); continue
        if entry.get("mode") != "100644" or entry.get("type") != "blob": errors.append(f"lock path must be regular Git blob mode 100644, got {entry.get('mode')}/{entry.get('type')}: {path}")
        if entry.get("sha") != item.get("sha"): errors.append(f"PR file SHA does not match exact Git tree blob: {path}")
    return errors


def release_head_absence_errors(files: list[dict], head_tree_entries: list[dict]) -> list[str]:
    paths = {entry.get("path") for entry in head_tree_entries if isinstance(entry, dict)}
    return [f"deleted RELEASE lock still exists in exact PR head tree: {item.get('filename')}" for item in files if item.get("filename") in paths]


def final_revalidation_errors(*, original_main_sha: str, original_head_sha: str, final_main_sha: str, final_pr: dict) -> list[str]:
    errors = []
    if final_main_sha != original_main_sha: errors.append("main moved after revalidation; require a fresh Verify run")
    if final_pr.get("head", {}).get("sha") != original_head_sha: errors.append("PR head moved after revalidation")
    if final_pr.get("base", {}).get("sha") != original_main_sha: errors.append("PR base moved after revalidation")
    return errors


def _request_json(token: str, repository: str, method: str, path: str, payload=None):
    url = API_ROOT + path; data = None if payload is None else json.dumps(payload).encode("utf-8")
    req = urllib.request.Request(url, data=data, method=method, headers={"Accept":"application/vnd.github+json", "Authorization":f"Bearer {token}", "X-GitHub-Api-Version":"2022-11-28", "User-Agent":"AIMath-Village-lock-lifecycle"})
    try:
        with urllib.request.urlopen(req, timeout=20) as response: raw = response.read()
    except urllib.error.HTTPError as exc:
        body = exc.read().decode("utf-8", errors="replace"); raise AutoActivationError(f"GitHub API {method} {path} failed {exc.code}: {body[:500]}") from exc
    return json.loads(raw.decode("utf-8")) if raw else {}


def _fetch_all_pr_files(token: str, repository: str, pr_number: int) -> list[dict]:
    owner, repo = repository.split("/", 1); out = []
    for page in range(1, 4):
        rows = _request_json(token, repository, "GET", f"/repos/{owner}/{repo}/pulls/{pr_number}/files?per_page=100&page={page}")
        if not isinstance(rows, list): raise AutoActivationError("unexpected PR files response")
        out.extend(rows)
        if len(rows) < 100: return out
    raise AutoActivationError("PR files pagination exceeded bounded limit")


def _fetch_open_prs(token: str, repository: str) -> list[dict]:
    owner, repo = repository.split("/", 1); out = []
    for page in range(1, 4):
        rows = _request_json(token, repository, "GET", f"/repos/{owner}/{repo}/pulls?state=open&base=main&sort=created&direction=asc&per_page=100&page={page}")
        if not isinstance(rows, list): raise AutoActivationError("unexpected open PR response")
        out.extend(rows)
        if len(rows) < 100: return out
    raise AutoActivationError("open PR pagination exceeded bounded limit")


def _has_successful_verify(token: str, repository: str, head_sha: str) -> bool:
    if not SHA_RE.fullmatch(head_sha or ""): return False
    owner, repo = repository.split("/", 1)
    obj = _request_json(token, repository, "GET", f"/repos/{owner}/{repo}/actions/runs?event=pull_request&head_sha={head_sha}&per_page=100")
    rows = obj.get("workflow_runs") if isinstance(obj, dict) else None
    if not isinstance(rows, list): raise AutoActivationError("unexpected workflow runs response")
    matching = [r for r in rows if r.get("name") == VERIFY_WORKFLOW_NAME and r.get("head_sha") == head_sha]
    if not matching: return False
    latest = max(matching, key=lambda r: int(r.get("id", 0)))
    return latest.get("status") == "completed" and latest.get("conclusion") == "success"


def _fetch_exact_tree(token: str, repository: str, commit_sha: str) -> list[dict]:
    owner, repo = repository.split("/", 1)
    commit = _request_json(token, repository, "GET", f"/repos/{owner}/{repo}/git/commits/{commit_sha}")
    tree_sha = commit.get("tree", {}).get("sha")
    if not isinstance(tree_sha, str) or not SHA_RE.fullmatch(tree_sha): raise AutoActivationError("exact commit did not expose a Git tree SHA")
    tree = _request_json(token, repository, "GET", f"/repos/{owner}/{repo}/git/trees/{tree_sha}?recursive=1")
    if tree.get("truncated"): raise AutoActivationError("exact recursive Git tree was truncated")
    entries = tree.get("tree")
    if not isinstance(entries, list): raise AutoActivationError("unexpected Git tree response")
    return entries


def _fetch_file_at_sha(token: str, repository: str, path: str, sha: str, *, expected_blob_sha: str) -> bytes:
    owner, repo = repository.split("/", 1); quoted = urllib.parse.quote(path, safe="/")
    obj = _request_json(token, repository, "GET", f"/repos/{owner}/{repo}/contents/{quoted}?ref={sha}")
    if obj.get("type") != "file" or obj.get("encoding") != "base64": raise AutoActivationError(f"lock path is not an ordinary base64 file response: {path}")
    if obj.get("sha") != expected_blob_sha: raise AutoActivationError(f"Contents API object SHA does not equal verified regular Git blob SHA: {path}")
    try: return base64.b64decode(obj["content"], validate=False)
    except Exception as exc: raise AutoActivationError(f"invalid base64 content for {path}") from exc


def _copy_trusted_main(prefix: str):
    td = tempfile.TemporaryDirectory(prefix=prefix); dest = Path(td.name) / "repo"
    shutil.copytree(Path(".").resolve(), dest, ignore=shutil.ignore_patterns(".git", "__pycache__", "*.pyc")); return td, dest


def _materialize_acquire_head(token: str, repository: str, head_sha: str, files: list[dict]) -> tempfile.TemporaryDirectory:
    td, dest = _copy_trusted_main("aimath-lock-acquire-")
    for item in files:
        path = item["filename"]; data = _fetch_file_at_sha(token, repository, path, head_sha, expected_blob_sha=item["sha"])
        if len(data) > 64 * 1024: td.cleanup(); raise AutoActivationError(f"lock file too large: {path}")
        target = (dest / path).resolve()
        try: target.relative_to(dest.resolve())
        except ValueError as exc: td.cleanup(); raise AutoActivationError(f"unsafe lock path: {path}") from exc
        target.parent.mkdir(parents=True, exist_ok=True); target.write_bytes(data)
    return td


def _materialize_release_head(files: list[dict]) -> tempfile.TemporaryDirectory:
    td, dest = _copy_trusted_main("aimath-lock-release-")
    for item in files:
        path = item["filename"]; target = (dest / path).resolve()
        try: target.relative_to(dest.resolve())
        except ValueError as exc: td.cleanup(); raise AutoActivationError(f"unsafe RELEASE path: {path}") from exc
        if target.is_symlink() or not target.is_file(): td.cleanup(); raise AutoActivationError(f"current-main RELEASE target is not a regular file: {path}")
        target.unlink()
    return td


def _strict_up_to_date_gate(token: str, repository: str) -> tuple[bool, str]:
    owner, repo = repository.split("/", 1)
    try: obj = _request_json(token, repository, "GET", f"/repos/{owner}/{repo}/branches/main/protection/required_status_checks")
    except AutoActivationError as exc: return False, f"cannot confirm Require branches to be up to date before merging: {exc}"
    if obj.get("strict") is not True: return False, "Require branches to be up to date before merging is not confirmed ON"
    return True, "strict status checks confirmed"


def _trusted_main_state(current_main_sha: str):
    try: local_sha = subprocess.check_output(["git", "rev-parse", "HEAD"], text=True).strip()
    except Exception as exc: raise AutoActivationError(f"cannot determine trusted checkout SHA: {exc}") from exc
    if local_sha != current_main_sha: raise AutoActivationError(f"trusted default-branch checkout {local_sha} does not equal current main {current_main_sha}; rerun on fresh main")
    state = VillageState(".").load(); errors = list(state.validate()) + worker_lock_errors(state, load_actor_policy("."))
    if errors: raise AutoActivationError("current main Village state is invalid: " + "; ".join(errors[:10]))
    return state


def _eligible_release_candidate(token: str, repository: str, pr: dict, *, current_main_sha: str, current_main_tree: list[dict], base_state: VillageState, maintainers: set[str], release_principals: set[str]):
    number = pr.get("number")
    if not isinstance(number, int): return None, ["PR lacks numeric number"]
    files = _fetch_all_pr_files(token, repository, number)
    ok, errors = auto_release_preflight(pr, files, repository=repository, current_main_sha=current_main_sha, release_principals=release_principals)
    if not ok: return None, errors
    head_sha = pr.get("head", {}).get("sha", "")
    if not _has_successful_verify(token, repository, head_sha): return None, ["exact RELEASE head has no current successful Verify public release run"]
    errors.extend(lock_git_object_errors(files, current_main_tree)); head_tree = _fetch_exact_tree(token, repository, head_sha); errors.extend(release_head_absence_errors(files, head_tree))
    if errors: return None, list(dict.fromkeys(errors))
    td = _materialize_release_head(files)
    try:
        head_root = Path(td.name) / "repo"; head_state = VillageState(head_root).load(); head_errors = list(head_state.validate()) + worker_lock_errors(head_state, load_actor_policy(head_root))
        if head_errors: return None, ["proposed RELEASE head Village state is invalid", *head_errors[:10]]
        binding = parse_release_head_ref(pr.get("head", {}).get("ref")); assert binding is not None
        operation, transition_errors = validate_lock_transition(base_state, head_state, actor=pr.get("user", {}).get("login", ""), base_sha=current_main_sha, maintainers=maintainers, release_binding=binding)
        if operation != "RELEASE" or transition_errors: return None, ["trusted RELEASE transition rejected", operation, *transition_errors]
        removed = set(base_state.lock_bundles) - set(head_state.lock_bundles)
        if len(removed) != 1: return None, ["RELEASE must remove exactly one canonical lock bundle"]
        bundle_id = next(iter(removed)); bundle = base_state.lock_bundles[bundle_id]
        identity_errors = automatic_release_identity_errors(pr, bundle, binding)
        if identity_errors: return None, identity_errors
        expected_paths = {p.relative_to(base_state.root).as_posix() for p in bundle.paths}; changed_paths = {item["filename"] for item in files}
        if changed_paths != expected_paths: return None, ["RELEASE changed paths do not exactly equal canonical lock bundle identity"]
        terminal_class, terminal_errors = release_terminal_state(base_state.root, bundle.payload, now=base_state.now)
        if terminal_class == "NONE": return None, terminal_errors
        return AutoReleaseCandidate(pr=pr, files=files, bundle_id=bundle_id, terminal_class=terminal_class), []
    finally: td.cleanup()


def _merge_candidate(token: str, repository: str, candidate_pr: dict, *, current_main_sha: str, title: str, message: str):
    owner, repo = repository.split("/", 1); pr_number = int(candidate_pr["number"])
    final_ref = _request_json(token, repository, "GET", f"/repos/{owner}/{repo}/git/ref/heads/main"); final_pr = _request_json(token, repository, "GET", f"/repos/{owner}/{repo}/pulls/{pr_number}")
    race_errors = final_revalidation_errors(original_main_sha=current_main_sha, original_head_sha=candidate_pr["head"]["sha"], final_main_sha=final_ref.get("object", {}).get("sha", ""), final_pr=final_pr)
    if race_errors:
        print("SKIP: lifecycle state moved after revalidation")
        for error in race_errors: print(" -", error)
        return None
    result = _request_json(token, repository, "PUT", f"/repos/{owner}/{repo}/pulls/{pr_number}/merge", {"sha":candidate_pr["head"]["sha"], "merge_method":"squash", "commit_title":title, "commit_message":message})
    if not result.get("merged"): raise AutoActivationError(f"GitHub refused merge: {result.get('message', 'unknown reason')}")
    return result


def main() -> int:
    repository = os.environ.get("GITHUB_REPOSITORY", ""); token = os.environ.get("GITHUB_TOKEN", ""); run_id = os.environ.get("SOURCE_RUN_ID", "")
    if not repository or not token or not run_id.isdigit(): raise AutoActivationError("GITHUB_REPOSITORY, GITHUB_TOKEN and numeric SOURCE_RUN_ID are required")
    owner, repo = repository.split("/", 1); run = _request_json(token, repository, "GET", f"/repos/{owner}/{repo}/actions/runs/{run_id}")
    if run.get("name") != VERIFY_WORKFLOW_NAME or run.get("event") != "pull_request": print("SKIP: source run is not a pull_request Verify public release run"); return 0
    if run.get("status") != "completed" or run.get("conclusion") != "success": print("SKIP: source Verify run is not completed/success"); return 0
    ref = _request_json(token, repository, "GET", f"/repos/{owner}/{repo}/git/ref/heads/main"); current_main_sha = ref.get("object", {}).get("sha", "")
    if not SHA_RE.fullmatch(current_main_sha): raise AutoActivationError("current main did not expose a full SHA")
    base_state = _trusted_main_state(current_main_sha); current_main_tree = _fetch_exact_tree(token, repository, current_main_sha)
    maintainers_obj = json.loads(Path("coordination/policy/MAINTAINERS.yml").read_text(encoding="utf-8")); maintainers = set(maintainers_obj.get("maintainers", [])); autonomous = load_autonomous_lock_principals("."); release_principals = set(autonomous.get("automatic_release_principals", []))
    eligible_releases = []
    for pr in _fetch_open_prs(token, repository):
        if parse_release_head_ref(pr.get("head", {}).get("ref")) is None: continue
        candidate, errors = _eligible_release_candidate(token, repository, pr, current_main_sha=current_main_sha, current_main_tree=current_main_tree, base_state=base_state, maintainers=maintainers, release_principals=release_principals)
        if candidate is not None: eligible_releases.append(candidate)
        else:
            print(f"RELEASE_PR_{pr.get('number')}_INELIGIBLE")
            for error in errors: print(" -", error)
    candidate = choose_release_candidate(eligible_releases)
    if candidate is not None:
        strict_ok, strict_reason = _strict_up_to_date_gate(token, repository)
        if not strict_ok: print("AUTO_ACTIVATION_BLOCKED_SETTING_CONFIRMATION"); print(strict_reason); return 0
        bundle = base_state.lock_bundles[candidate.bundle_id]
        result = _merge_candidate(token, repository, candidate.pr, current_main_sha=current_main_sha, title=f"Release {bundle.payload.get('task_id')} lock", message="Mechanically revalidated exact-worker lock-only RELEASE from trusted default-branch code.")
        if result is None: return 0
        print(f"AUTO_RELEASED_PR={candidate.pr['number']}"); print(f"RELEASE_TERMINAL_CLASS={candidate.terminal_class}")
        if candidate.terminal_class == "ABANDONED_TERMINAL":
            visibility = abandonment_state(base_state.root, bundle.payload["task_id"], bundle.payload["worker_id"], now=base_state.now); print(f"ABANDONMENT_COUNT={visibility.get('abandonment_count')}"); print(f"REACQUIRE_COOLDOWN_UNTIL={visibility.get('cooldown_until')}")
        print(f"MERGE_SHA={result.get('sha')}"); return 0
    linked = run.get("pull_requests", [])
    if len(linked) != 1: print("SKIP: no eligible RELEASE and source run is not linked to exactly one PR"); return 0
    pr_number = int(linked[0]["number"]); pr = _request_json(token, repository, "GET", f"/repos/{owner}/{repo}/pulls/{pr_number}"); files = _fetch_all_pr_files(token, repository, pr_number)
    ok, errors = auto_activation_preflight(run, pr, files, repository=repository, current_main_sha=current_main_sha, maintainers=maintainers)
    if not ok:
        print("SKIP: no eligible RELEASE and source PR is not a safe ACQUIRE candidate")
        for error in errors: print(" -", error)
        return 0
    head_tree = _fetch_exact_tree(token, repository, pr["head"]["sha"]); object_errors = lock_git_object_errors(files, head_tree)
    if object_errors: raise AutoActivationError("exact Git object validation failed: " + "; ".join(object_errors))
    strict_ok, strict_reason = _strict_up_to_date_gate(token, repository)
    if not strict_ok: print("AUTO_ACTIVATION_BLOCKED_SETTING_CONFIRMATION"); print(strict_reason); return 0
    td = _materialize_acquire_head(token, repository, pr["head"]["sha"], files)
    try:
        head_root = Path(td.name) / "repo"; head_state = VillageState(head_root).load(); head_errors = list(head_state.validate()) + worker_lock_errors(head_state, load_actor_policy(head_root))
        if head_errors: raise AutoActivationError("proposed lock head is invalid: " + "; ".join(head_errors[:10]))
        operation, transition_errors = validate_lock_transition(base_state, head_state, actor=pr["user"]["login"], base_sha=current_main_sha, maintainers=maintainers)
        if operation != "ACQUIRE" or transition_errors: raise AutoActivationError("trusted revalidation rejected lock acquisition: " + "; ".join([operation, *transition_errors]))
        added = set(head_state.lock_bundles) - set(base_state.lock_bundles)
        if len(added) != 1: raise AutoActivationError("ACQUIRE must add exactly one lock bundle")
        bundle = head_state.lock_bundles[next(iter(added))]; worker_errors = new_worker_lock_errors(base_state, bundle, actor_policy=load_actor_policy("."))
        if worker_errors: raise AutoActivationError("worker lock policy failed: " + "; ".join(worker_errors))
    finally: td.cleanup()
    result = _merge_candidate(token, repository, pr, current_main_sha=current_main_sha, title=f"Activate {bundle.payload.get('task_id')} lock", message="Mechanically revalidated lock-only acquisition from trusted default-branch code.")
    if result is None: return 0
    print(f"AUTO_ACTIVATED_PR={pr_number}"); print(f"MERGE_SHA={result.get('sha')}"); return 0


if __name__ == "__main__":
    raise SystemExit(main())
