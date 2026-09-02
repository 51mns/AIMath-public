#!/usr/bin/env python3
# SPDX-FileCopyrightText: 2026 AIMath contributors
# SPDX-License-Identifier: Apache-2.0
from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
import json
import os

from check_village_pr import validate_lock_transition
from lock_auto_activate_phase_a import (
    API_ROOT,
    SHA_RE,
    VERIFY_WORKFLOW_NAME,
    AutoActivationError,
    AutoReleaseCandidate,
    _eligible_release_candidate,
    _fetch_all_pr_files,
    _fetch_exact_tree,
    _fetch_open_prs,
    _has_successful_verify,
    _materialize_acquire_head,
    _merge_candidate,
    _request_json,
    _trusted_main_state,
    auto_activation_preflight,
    auto_release_preflight,
    automatic_release_identity_errors,
    choose_release_candidate,
    final_revalidation_errors,
    lock_git_object_errors,
    release_head_absence_errors,
)
from village_core import VillageState
from village_v1_2 import (
    abandonment_state,
    load_actor_policy,
    load_autonomous_lock_principals,
    new_worker_lock_errors,
    parse_release_head_ref,
    release_terminal_state,
    worker_lock_errors,
)


# Observation/shape failures for one candidate must never authorize that
# candidate, but they also must not make an invalid lower PR reservation
# authority over later valid work. These exceptions arise while decoding or
# validating untrusted GitHub candidate data; handling them is fail-closed.
_CANDIDATE_LOCAL_OBSERVATION_ERRORS = (
    AutoActivationError,
    AttributeError,
    KeyError,
    TypeError,
    ValueError,
)


def _strict_up_to_date_gate(token: str, repository: str) -> tuple[bool, str]:
    """Compatibility-preserving strict gate using this module's request seam.

    Existing v1.2/v1.2.1 tests patch lock_auto_activate._request_json directly.
    Keeping the gate here preserves that public test seam while retaining the
    exact fail-closed semantics of the frozen Phase A implementation.
    """
    owner, repo = repository.split("/", 1)
    try:
        obj = _request_json(
            token,
            repository,
            "GET",
            f"/repos/{owner}/{repo}/branches/main/protection/required_status_checks",
        )
    except AutoActivationError as exc:
        return False, f"cannot confirm Require branches to be up to date before merging: {exc}"
    if obj.get("strict") is not True:
        return False, "Require branches to be up to date before merging is not confirmed ON"
    return True, "strict status checks confirmed"


@dataclass(frozen=True)
class AutoAcquireCandidate:
    pr: dict
    files: list[dict]
    bundle_id: str
    task_id: str
    worker_id: str


def choose_acquire_candidate(candidates: list[AutoAcquireCandidate]) -> AutoAcquireCandidate | None:
    """Order only ACQUIRE candidates already proven eligible against current main."""
    return min(candidates, key=lambda c: int(c.pr["number"])) if candidates else None


def auto_acquire_preflight(
    pr: dict,
    files: list[dict],
    *,
    repository: str,
    current_main_sha: str,
    maintainers: set[str],
) -> tuple[bool, list[str]]:
    """Reuse the reviewed v1.2 ACQUIRE shape gate without making the source run authority.

    The caller must separately prove that this exact candidate head has a successful
    pull_request Verify public release run. The synthetic run below exists only so
    the frozen Phase A preflight can be reused byte-for-byte for structural checks.
    """
    head_sha = pr.get("head", {}).get("sha", "")
    synthetic_verified_run = {
        "name": VERIFY_WORKFLOW_NAME,
        "event": "pull_request",
        "status": "completed",
        "conclusion": "success",
        "head_sha": head_sha,
    }
    return auto_activation_preflight(
        synthetic_verified_run,
        pr,
        files,
        repository=repository,
        current_main_sha=current_main_sha,
        maintainers=maintainers,
    )


def _eligible_acquire_candidate(
    token: str,
    repository: str,
    pr: dict,
    *,
    current_main_sha: str,
    base_state: VillageState,
    maintainers: set[str],
):
    number = pr.get("number")
    if not isinstance(number, int):
        return None, ["PR lacks numeric number"]

    files = _fetch_all_pr_files(token, repository, number)
    ok, errors = auto_acquire_preflight(
        pr,
        files,
        repository=repository,
        current_main_sha=current_main_sha,
        maintainers=maintainers,
    )
    if not ok:
        return None, errors

    head_sha = pr.get("head", {}).get("sha", "")
    if not _has_successful_verify(token, repository, head_sha):
        return None, ["exact ACQUIRE head has no current successful Verify public release run"]

    head_tree = _fetch_exact_tree(token, repository, head_sha)
    errors.extend(lock_git_object_errors(files, head_tree))
    if errors:
        return None, list(dict.fromkeys(errors))

    td = _materialize_acquire_head(token, repository, head_sha, files)
    try:
        head_root = Path(td.name) / "repo"
        head_state = VillageState(head_root).load()
        head_errors = list(head_state.validate()) + worker_lock_errors(
            head_state, load_actor_policy(head_root)
        )
        if head_errors:
            return None, ["proposed ACQUIRE head Village state is invalid", *head_errors[:10]]

        operation, transition_errors = validate_lock_transition(
            base_state,
            head_state,
            actor=pr.get("user", {}).get("login", ""),
            base_sha=current_main_sha,
            maintainers=maintainers,
        )
        if operation != "ACQUIRE" or transition_errors:
            return None, ["trusted ACQUIRE transition rejected", operation, *transition_errors]

        added = set(head_state.lock_bundles) - set(base_state.lock_bundles)
        if len(added) != 1:
            return None, ["ACQUIRE must add exactly one canonical lock bundle"]

        bundle_id = next(iter(added))
        bundle = head_state.lock_bundles[bundle_id]
        worker_errors = new_worker_lock_errors(
            base_state, bundle, actor_policy=load_actor_policy(".")
        )
        if worker_errors:
            return None, ["worker lock policy failed", *worker_errors]

        expected_paths = {
            p.relative_to(head_state.root).as_posix() for p in bundle.paths
        }
        changed_paths = {item["filename"] for item in files}
        if changed_paths != expected_paths:
            return None, ["ACQUIRE changed paths do not exactly equal added lock bundle identity"]

        return AutoAcquireCandidate(
            pr=pr,
            files=files,
            bundle_id=bundle_id,
            task_id=str(bundle.payload.get("task_id", "")),
            worker_id=str(bundle.payload.get("worker_id", "")),
        ), []
    finally:
        td.cleanup()


def _candidate_number(pr: object) -> object:
    return pr.get("number", "UNKNOWN") if isinstance(pr, dict) else "UNKNOWN"


def _candidate_head_ref(pr: object) -> str | None:
    if not isinstance(pr, dict):
        return None
    head = pr.get("head")
    if not isinstance(head, dict):
        return None
    ref = head.get("ref")
    return ref if isinstance(ref, str) else None


def _scan_releases(
    token: str,
    repository: str,
    open_prs: list[dict],
    *,
    current_main_sha: str,
    current_main_tree: list[dict],
    base_state: VillageState,
    maintainers: set[str],
    release_principals: set[str],
) -> list[AutoReleaseCandidate]:
    """Find RELEASE candidates without letting one bad observation block later work."""
    eligible: list[AutoReleaseCandidate] = []
    for pr in open_prs:
        number = _candidate_number(pr)
        head_ref = _candidate_head_ref(pr)
        if head_ref is None:
            if not isinstance(pr, dict):
                print("LIFECYCLE_PR_UNKNOWN_INELIGIBLE")
                print(" - malformed open PR observation")
            continue
        if parse_release_head_ref(head_ref) is None:
            continue
        try:
            candidate, errors = _eligible_release_candidate(
                token,
                repository,
                pr,
                current_main_sha=current_main_sha,
                current_main_tree=current_main_tree,
                base_state=base_state,
                maintainers=maintainers,
                release_principals=release_principals,
            )
        except _CANDIDATE_LOCAL_OBSERVATION_ERRORS as exc:
            print(f"RELEASE_PR_{number}_INELIGIBLE")
            print(
                " - candidate inspection failed closed:",
                f"{type(exc).__name__}: {exc}",
            )
            continue
        if candidate is not None:
            eligible.append(candidate)
        else:
            print(f"RELEASE_PR_{number}_INELIGIBLE")
            for error in errors:
                print(" -", error)
    return eligible


def _scan_acquires(
    token: str,
    repository: str,
    open_prs: list[dict],
    *,
    current_main_sha: str,
    base_state: VillageState,
    maintainers: set[str],
) -> list[AutoAcquireCandidate]:
    eligible: list[AutoAcquireCandidate] = []
    for pr in open_prs:
        number = _candidate_number(pr)
        head_ref = _candidate_head_ref(pr)
        if head_ref is None:
            if not isinstance(pr, dict):
                print("LIFECYCLE_PR_UNKNOWN_INELIGIBLE")
                print(" - malformed open PR observation")
            continue
        if parse_release_head_ref(head_ref) is not None:
            continue
        try:
            candidate, errors = _eligible_acquire_candidate(
                token,
                repository,
                pr,
                current_main_sha=current_main_sha,
                base_state=base_state,
                maintainers=maintainers,
            )
        except _CANDIDATE_LOCAL_OBSERVATION_ERRORS as exc:
            # Candidate-local observation failure cannot make a lower/invalid PR
            # reservation authority over later valid candidates.
            print(f"ACQUIRE_PR_{number}_INELIGIBLE")
            print(
                " - candidate inspection failed closed:",
                f"{type(exc).__name__}: {exc}",
            )
            continue
        if candidate is not None:
            eligible.append(candidate)
        else:
            print(f"ACQUIRE_PR_{number}_INELIGIBLE")
            for error in errors:
                print(" -", error)
    return eligible


def main() -> int:
    repository = os.environ.get("GITHUB_REPOSITORY", "")
    token = os.environ.get("GITHUB_TOKEN", "")
    run_id = os.environ.get("SOURCE_RUN_ID", "")
    if not repository or not token or not run_id.isdigit():
        raise AutoActivationError(
            "GITHUB_REPOSITORY, GITHUB_TOKEN and numeric SOURCE_RUN_ID are required"
        )

    owner, repo = repository.split("/", 1)
    run = _request_json(
        token, repository, "GET", f"/repos/{owner}/{repo}/actions/runs/{run_id}"
    )
    if run.get("name") != VERIFY_WORKFLOW_NAME or run.get("event") != "pull_request":
        print("SKIP: source run is not a pull_request Verify public release run")
        return 0
    if run.get("status") != "completed" or run.get("conclusion") != "success":
        print("SKIP: source Verify run is not completed/success")
        return 0

    ref = _request_json(
        token, repository, "GET", f"/repos/{owner}/{repo}/git/ref/heads/main"
    )
    current_main_sha = ref.get("object", {}).get("sha", "")
    if not SHA_RE.fullmatch(current_main_sha):
        raise AutoActivationError("current main did not expose a full SHA")

    base_state = _trusted_main_state(current_main_sha)
    current_main_tree = _fetch_exact_tree(token, repository, current_main_sha)
    maintainers_obj = json.loads(
        Path("coordination/policy/MAINTAINERS.yml").read_text(encoding="utf-8")
    )
    maintainers = set(maintainers_obj.get("maintainers", []))
    autonomous = load_autonomous_lock_principals(".")
    release_principals = set(autonomous.get("automatic_release_principals", []))
    open_prs = _fetch_open_prs(token, repository)

    # Frozen Phase A ordering: RELEASE always wins over ACQUIRE, but one invalid
    # RELEASE observation cannot block later valid lifecycle candidates.
    eligible_releases = _scan_releases(
        token,
        repository,
        open_prs,
        current_main_sha=current_main_sha,
        current_main_tree=current_main_tree,
        base_state=base_state,
        maintainers=maintainers,
        release_principals=release_principals,
    )

    release_candidate = choose_release_candidate(eligible_releases)
    if release_candidate is not None:
        strict_ok, strict_reason = _strict_up_to_date_gate(token, repository)
        if not strict_ok:
            print("AUTO_ACTIVATION_BLOCKED_SETTING_CONFIRMATION")
            print(strict_reason)
            return 0

        bundle = base_state.lock_bundles[release_candidate.bundle_id]
        result = _merge_candidate(
            token,
            repository,
            release_candidate.pr,
            current_main_sha=current_main_sha,
            title=f"Release {bundle.payload.get('task_id')} lock",
            message=(
                "Mechanically revalidated exact-worker lock-only RELEASE "
                "from trusted default-branch code."
            ),
        )
        if result is None:
            return 0
        print(f"AUTO_RELEASED_PR={release_candidate.pr['number']}")
        print(f"RELEASE_TERMINAL_CLASS={release_candidate.terminal_class}")
        if release_candidate.terminal_class == "ABANDONED_TERMINAL":
            visibility = abandonment_state(
                base_state.root,
                bundle.payload["task_id"],
                bundle.payload["worker_id"],
                now=base_state.now,
            )
            print(f"ABANDONMENT_COUNT={visibility.get('abandonment_count')}")
            print(f"REACQUIRE_COOLDOWN_UNTIL={visibility.get('cooldown_until')}")
        print(f"MERGE_SHA={result.get('sha')}")
        return 0

    # Phase B: every ACQUIRE candidate must independently be current-main,
    # exact-green-CI, lock-only, object-valid and Village-valid before ordering.
    eligible_acquires = _scan_acquires(
        token,
        repository,
        open_prs,
        current_main_sha=current_main_sha,
        base_state=base_state,
        maintainers=maintainers,
    )
    acquire_candidate = choose_acquire_candidate(eligible_acquires)
    if acquire_candidate is None:
        print("SKIP: no eligible RELEASE or ACQUIRE candidate")
        return 0

    strict_ok, strict_reason = _strict_up_to_date_gate(token, repository)
    if not strict_ok:
        print("AUTO_ACTIVATION_BLOCKED_SETTING_CONFIRMATION")
        print(strict_reason)
        return 0

    result = _merge_candidate(
        token,
        repository,
        acquire_candidate.pr,
        current_main_sha=current_main_sha,
        title=f"Activate {acquire_candidate.task_id} lock",
        message=(
            "Mechanically revalidated discovered lock-only ACQUIRE "
            "from trusted default-branch code."
        ),
    )
    if result is None:
        return 0
    print(f"AUTO_ACTIVATED_PR={acquire_candidate.pr['number']}")
    print(f"ACQUIRE_TASK_ID={acquire_candidate.task_id}")
    print(f"ACQUIRE_WORKER_ID={acquire_candidate.worker_id}")
    print(f"MERGE_SHA={result.get('sha')}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
