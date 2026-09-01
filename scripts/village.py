#!/usr/bin/env python3
from __future__ import annotations

from pathlib import Path
from datetime import datetime, timezone
import argparse
import subprocess
import sys

from village_core import VillageState

def cmd_validate(root: Path) -> int:
    state = VillageState(root).load()
    errors = state.validate()
    errors.extend(state.generated_view_drift())
    if errors:
        print("FAIL: Village validation")
        for item in sorted(set(errors)):
            print(" -", item)
        return 1
    print(
        f"PASS: Village validation "
        f"({len(state.campaigns)} campaigns, {len(state.tasks)} tasks, "
        f"{len(state.claims)} public claim metadata records)"
    )
    return 0

def cmd_status(root: Path) -> int:
    state = VillageState(root).load()
    errors = state.validate()
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
    return 1 if errors else 0

def cmd_render(root: Path, check: bool) -> int:
    state = VillageState(root).load()
    if state.validate():
        for item in sorted(set(state.errors)):
            print(" -", item)
        return 1
    views = state.rendered_views()
    if check:
        drift = state.generated_view_drift()
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
    return subprocess.call([sys.executable, str(root / "scripts/test_village_acceptance.py")], cwd=root)

def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("command", choices=["validate", "status", "render", "check-views", "test"])
    ap.add_argument("--root", default=".")
    args = ap.parse_args()
    root = Path(args.root).resolve()
    if args.command == "validate":
        return cmd_validate(root)
    if args.command == "status":
        return cmd_status(root)
    if args.command == "render":
        return cmd_render(root, False)
    if args.command == "check-views":
        return cmd_render(root, True)
    if args.command == "test":
        return cmd_test(root)
    return 2

if __name__ == "__main__":
    raise SystemExit(main())
