#!/usr/bin/env python3
from __future__ import annotations

from pathlib import Path
from datetime import datetime, timezone
import argparse
import subprocess
import sys

from village_core import VillageState
from village_rank import EvaluationBook, discovery_policy_errors
from village_v1_2 import (
    CapabilityProfile,
    VillageV12Error,
    load_actor_policy,
    load_pending_claims,
    rank_v12,
    worker_lock_errors,
    worker_workspace,
)


def _state_and_book(root: Path):
    state = VillageState(root).load()
    errors = list(state.validate())
    errors.extend(worker_lock_errors(state, load_actor_policy(root)))
    errors.extend(discovery_policy_errors(state))
    book = EvaluationBook(root, state).load()
    errors.extend(book.errors)
    return state, book, errors


def cmd_validate(root: Path) -> int:
    state, book, errors = _state_and_book(root)
    errors.extend(state.generated_view_drift())
    errors.extend(book.view_drift())
    if errors:
        print("FAIL: Village validation")
        for item in sorted(set(errors)):
            print(" -", item)
        return 1
    print(
        f"PASS: Village validation "
        f"({len(state.campaigns)} campaigns, {len(state.tasks)} tasks, "
        f"{len(state.claims)} public claim metadata records, "
        f"{len(book.records)} research evaluations)"
    )
    return 0


def cmd_status(root: Path) -> int:
    state, book, errors = _state_and_book(root)
    if errors:
        print("WARNING: current state has validation errors:")
        for item in sorted(set(errors)):
            print(" -", item)
    campaigns, tasks = state.status_rows()
    print("LIVE_STATUS_AS_OF_UTC\t" + datetime.now(timezone.utc).isoformat())
    print("CAMPAIGNS")
    for cid, effective, active in campaigns:
        print(f"{cid}\t{effective}\tactive={active}")
    print("TASKS")
    for tid, runtime, reasons in tasks:
        suffix = "" if not reasons else " :: " + "; ".join(reasons)
        print(f"{tid}\t{runtime}{suffix}")
    print(f"EVALUATIONS\t{len(book.records)}")
    return 1 if errors else 0


def cmd_rank(root: Path, args) -> int:
    state, book, errors = _state_and_book(root)
    if errors:
        print("FAIL: cannot rank invalid Village state")
        for item in sorted(set(errors)):
            print(" -", item)
        return 1
    try:
        profile = CapabilityProfile.from_values(
            github_write=args.github_write,
            local_compute=args.local_compute,
            web_literature=args.web_literature,
        )
        pending = load_pending_claims(args.pending_claims)
        rows = rank_v12(
            state,
            book,
            capabilities=profile,
            pending_records=pending,
            current_main_sha=args.current_main_sha,
        )
    except VillageV12Error as exc:
        print("FAIL:", exc)
        return 2
    print("LIVE_RANK_AS_OF_UTC\t" + datetime.now(timezone.utc).isoformat())
    print(
        "CAPABILITIES\t"
        f"github_write={args.github_write}\tlocal_compute={args.local_compute}\t"
        f"web_literature={args.web_literature}"
    )
    print(f"PENDING_OBSERVATIONS\t{len(pending)}")
    print("READY_TASK_RANKING")
    print(
        "rank\ttask\tcapability_fit\tscore\tpriority\tclass\tclass_weight\tdiversity\t"
        "campaign_headroom\teval_bonus\teligible_evals\tself_evals\t"
        "eligible_followup_ev\tself_followup_ev"
    )
    for i, wrapped in enumerate(rows, 1):
        row = wrapped.base
        efv = "—" if row.eligible_followup_expected_value is None else row.eligible_followup_expected_value
        sfv = "—" if row.self_followup_expected_value is None else row.self_followup_expected_value
        print(
            f"{i}\t{row.task_id}\t{wrapped.capability_fit}\t{row.score}\t{row.priority}\t{row.research_class}\t"
            f"{row.class_weight_bonus}\t{row.diversity_bonus}\t"
            f"{row.campaign_headroom_bonus}\t{row.evaluation_bonus}\t"
            f"{row.eligible_evaluations}\t{row.self_evaluations}\t{efv}\t{sfv}"
        )
    if not rows:
        print("NO_ELIGIBLE_READY_TASKS")
    return 0


def cmd_workspace(args) -> int:
    try:
        slot = worker_workspace(args.task_id, args.worker_id)
    except VillageV12Error as exc:
        print("FAIL:", exc)
        return 2
    print(f"SLOT_ID\t{slot.slot_id}")
    print(f"BRANCH\t{slot.branch}")
    print(f"OWNED_PATH\t{slot.owned_path}")
    return 0


def cmd_render(root: Path, check: bool) -> int:
    state, book, errors = _state_and_book(root)
    if errors:
        for item in sorted(set(errors)):
            print(" -", item)
        return 1
    views = dict(state.rendered_views())
    views["docs/RESEARCH_EVALUATIONS.md"] = book.render()
    if check:
        drift = state.generated_view_drift() + book.view_drift()
        if drift:
            print("FAIL: generated view drift")
            for item in drift:
                print(" -", item)
            return 1
        print("PASS: generated views are current")
        return 0
    for rel, content in views.items():
        path = root / rel
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(content.rstrip() + "\n", encoding="utf-8")
        print("wrote", rel)
    return 0


def cmd_test(root: Path) -> int:
    tests = [
        root / "scripts/test_village_acceptance.py",
        root / "scripts/test_village_v1_1.py",
        root / "scripts/test_village_v1_2.py",
    ]
    for test in tests:
        rc = subprocess.call([sys.executable, str(test)], cwd=root)
        if rc:
            return rc
    return 0


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument(
        "command",
        choices=["validate", "status", "rank", "workspace", "render", "check-views", "test"],
    )
    ap.add_argument("--root", default=".")
    ap.add_argument("--github-write", choices=["yes", "no", "unknown"], default="unknown")
    ap.add_argument("--local-compute", choices=["yes", "no", "unknown"], default="unknown")
    ap.add_argument("--web-literature", choices=["yes", "no", "unknown"], default="unknown")
    ap.add_argument("--pending-claims")
    ap.add_argument("--current-main-sha")
    ap.add_argument("--task-id")
    ap.add_argument("--worker-id")
    args = ap.parse_args()
    root = Path(args.root).resolve()
    if args.command == "validate":
        return cmd_validate(root)
    if args.command == "status":
        return cmd_status(root)
    if args.command == "rank":
        return cmd_rank(root, args)
    if args.command == "workspace":
        if not args.task_id or not args.worker_id:
            print("FAIL: workspace requires --task-id and --worker-id")
            return 2
        return cmd_workspace(args)
    if args.command == "render":
        return cmd_render(root, False)
    if args.command == "check-views":
        return cmd_render(root, True)
    if args.command == "test":
        return cmd_test(root)
    return 2


if __name__ == "__main__":
    raise SystemExit(main())
