# SPDX-FileCopyrightText: 2026 AIMath contributors
# SPDX-License-Identifier: Apache-2.0
from __future__ import annotations

from pathlib import Path
import base64
import json
import os
import shutil
import tempfile
import urllib.error
import urllib.parse
import urllib.request

from check_village_pr import validate_lock_transition
from village_core import VillageState
from village_v1_2 import load_actor_policy, new_worker_lock_errors, worker_lock_errors

API_ROOT = "https://api.github.com"
VERIFY_WORKFLOW_NAME = "Verify public release"


class AutoActivationError(RuntimeError):
    pass


def auto_activation_preflight(
    run: dict,
    pr: dict,
    files: list[dict],
    *,
    repository: str,
    current_main_sha: str,
    maintainers: set[str],
) -> tuple[bool, list[str]]:
    errors: list[str] = []
    if run.get("name") != VERIFY_WORKFLOW_NAME:
        errors.append("source workflow is not Verify public release")
    if run.get("event") != "pull_request":
        errors.append("source workflow was not a pull_request run")
    if run.get("status") != "completed" or run.get("conclusion") != "success":
        errors.append("verify workflow is not completed/success")
    if pr.get("state") != "open":
        errors.append("PR is not open")
    if pr.get("draft"):
        errors.append("draft PR is not auto-activatable")
    if pr.get("base", {}).get("ref") != "main":
        errors.append("PR base is not main")
    if pr.get("base", {}).get("sha") != current_main_sha:
        errors.append("PR base is stale relative to current main")
    if pr.get("head", {}).get("sha") != run.get("head_sha"):
        errors.append("PR head does not match verified workflow head")
    if pr.get("head", {}).get("repo", {}).get("full_name") != repository:
        errors.append("external/fork head is not eligible for v1.2 auto activation")
    if pr.get("user", {}).get("login") not in maintainers:
        errors.append("PR principal is not pre-authorized maintainer")
    if not files:
        errors.append("PR has no changed files")
    if len(files) > 16:
        errors.append("lock-only PR changed too many files")
    for item in files:
        name = item.get("filename", "")
        if item.get("status") != "added":
            errors.append(f"auto activation permits ACQUIRE additions only: {name}")
        if not (name.startswith("coordination/locks/") and name.endswith(".yml")):
            errors.append(f"non-lock path in auto activation candidate: {name}")
    return not errors, errors


def _request_json(token: str, repository: str, method: str, path: str, payload=None):
    url = API_ROOT + path
    data = None if payload is None else json.dumps(payload).encode("utf-8")
    req = urllib.request.Request(
        url,
        data=data,
        method=method,
        headers={
            "Accept": "application/vnd.github+json",
            "Authorization": f"Bearer {token}",
            "X-GitHub-Api-Version": "2022-11-28",
            "User-Agent": "AIMath-Village-lock-activation",
        },
    )
    try:
        with urllib.request.urlopen(req, timeout=20) as response:
            raw = response.read()
    except urllib.error.HTTPError as exc:
        body = exc.read().decode("utf-8", errors="replace")
        raise AutoActivationError(f"GitHub API {method} {path} failed {exc.code}: {body[:500]}") from exc
    return json.loads(raw.decode("utf-8")) if raw else {}


def _fetch_all_pr_files(token: str, repository: str, pr_number: int) -> list[dict]:
    owner, repo = repository.split("/", 1)
    out: list[dict] = []
    for page in range(1, 4):
        rows = _request_json(
            token,
            repository,
            "GET",
            f"/repos/{owner}/{repo}/pulls/{pr_number}/files?per_page=100&page={page}",
        )
        if not isinstance(rows, list):
            raise AutoActivationError("unexpected PR files response")
        out.extend(rows)
        if len(rows) < 100:
            return out
    raise AutoActivationError("PR files pagination exceeded bounded limit")


def _fetch_file_at_sha(token: str, repository: str, path: str, sha: str) -> bytes:
    owner, repo = repository.split("/", 1)
    quoted = urllib.parse.quote(path, safe="/")
    obj = _request_json(
        token,
        repository,
        "GET",
        f"/repos/{owner}/{repo}/contents/{quoted}?ref={sha}",
    )
    if obj.get("type") != "file" or obj.get("encoding") != "base64":
        raise AutoActivationError(f"lock path is not an ordinary base64 file: {path}")
    try:
        return base64.b64decode(obj["content"], validate=False)
    except Exception as exc:
        raise AutoActivationError(f"invalid base64 content for {path}") from exc


def _materialize_lock_head(
    token: str,
    repository: str,
    head_sha: str,
    files: list[dict],
) -> tempfile.TemporaryDirectory:
    td = tempfile.TemporaryDirectory(prefix="aimath-lock-activation-")
    dest = Path(td.name) / "repo"
    shutil.copytree(
        Path(".").resolve(),
        dest,
        ignore=shutil.ignore_patterns(".git", "__pycache__", "*.pyc"),
    )
    for item in files:
        path = item["filename"]
        data = _fetch_file_at_sha(token, repository, path, head_sha)
        if len(data) > 64 * 1024:
            td.cleanup()
            raise AutoActivationError(f"lock file too large: {path}")
        target = dest / path
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_bytes(data)
    return td


def main() -> int:
    repository = os.environ.get("GITHUB_REPOSITORY", "")
    token = os.environ.get("GITHUB_TOKEN", "")
    run_id = os.environ.get("SOURCE_RUN_ID", "")
    if not repository or not token or not run_id.isdigit():
        raise AutoActivationError("GITHUB_REPOSITORY, GITHUB_TOKEN and numeric SOURCE_RUN_ID are required")
    owner, repo = repository.split("/", 1)
    run = _request_json(token, repository, "GET", f"/repos/{owner}/{repo}/actions/runs/{run_id}")
    linked = run.get("pull_requests", [])
    if len(linked) != 1:
        print("SKIP: verified run is not linked to exactly one PR")
        return 0
    pr_number = int(linked[0]["number"])
    pr = _request_json(token, repository, "GET", f"/repos/{owner}/{repo}/pulls/{pr_number}")
    ref = _request_json(token, repository, "GET", f"/repos/{owner}/{repo}/git/ref/heads/main")
    current_main_sha = ref.get("object", {}).get("sha", "")
    maintainers_obj = json.loads(
        Path("coordination/policy/MAINTAINERS.yml").read_text(encoding="utf-8")
    )
    maintainers = set(maintainers_obj.get("maintainers", []))
    files = _fetch_all_pr_files(token, repository, pr_number)
    ok, errors = auto_activation_preflight(
        run,
        pr,
        files,
        repository=repository,
        current_main_sha=current_main_sha,
        maintainers=maintainers,
    )
    if not ok:
        print("SKIP: not a safe lock-only auto-activation candidate")
        for error in errors:
            print(" -", error)
        return 0

    base_state = VillageState(".").load()
    base_errors = list(base_state.validate()) + worker_lock_errors(
        base_state, load_actor_policy(".")
    )
    if base_errors:
        raise AutoActivationError("current main Village state is invalid: " + "; ".join(base_errors[:10]))

    td = _materialize_lock_head(token, repository, pr["head"]["sha"], files)
    try:
        head_root = Path(td.name) / "repo"
        head_state = VillageState(head_root).load()
        head_errors = list(head_state.validate()) + worker_lock_errors(
            head_state, load_actor_policy(head_root)
        )
        if head_errors:
            raise AutoActivationError("proposed lock head is invalid: " + "; ".join(head_errors[:10]))
        operation, transition_errors = validate_lock_transition(
            base_state,
            head_state,
            actor=pr["user"]["login"],
            base_sha=current_main_sha,
            maintainers=maintainers,
        )
        if operation != "ACQUIRE" or transition_errors:
            raise AutoActivationError(
                "trusted revalidation rejected lock acquisition: "
                + "; ".join([operation, *transition_errors])
            )
        added = set(head_state.lock_bundles) - set(base_state.lock_bundles)
        if len(added) != 1:
            raise AutoActivationError("ACQUIRE must add exactly one lock bundle")
        bundle = head_state.lock_bundles[next(iter(added))]
        worker_errors = new_worker_lock_errors(
            base_state,
            bundle,
            actor_policy=load_actor_policy("."),
        )
        if worker_errors:
            raise AutoActivationError("worker lock policy failed: " + "; ".join(worker_errors))
    finally:
        td.cleanup()

    result = _request_json(
        token,
        repository,
        "PUT",
        f"/repos/{owner}/{repo}/pulls/{pr_number}/merge",
        {
            "sha": pr["head"]["sha"],
            "merge_method": "squash",
            "commit_title": f"Activate {bundle.payload.get('task_id')} lock",
            "commit_message": "Mechanically revalidated lock-only acquisition from trusted default-branch code.",
        },
    )
    if not result.get("merged"):
        raise AutoActivationError(f"GitHub refused merge: {result.get('message', 'unknown reason')}")
    print(f"AUTO_ACTIVATED_PR={pr_number}")
    print(f"MERGE_SHA={result.get('sha')}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
