#!/usr/bin/env python3
"""Run every executable public claim package using the current Python.

This temporary review-validation branch also executes the otherwise-unregistered
Village v1.3 Phase A direct suite from the exact fixed target blobs before the
normal public replay suite. The branch/PR must never be merged.
"""
from __future__ import annotations

from pathlib import Path
import subprocess
import sys

REPLAYS = [
    "research/fixed-433/reproduce.py",
    "research/433-springborn-obstruction/reproduce.py",
    "research/433-existing-theory-identification/reproduce.py",
    "research/gyoda-89/reproduce.py",
    "research/equiangular-r18-eta17/verify.py",
    "research/b3rcc-apc/reproduce.py",
    "research/afes-bounded/verify.py",
    "research/thue-morse-rediscovery/verify.py",
]


def main() -> int:
    root = Path(sys.argv[1] if len(sys.argv) > 1 else ".").resolve()
    failures: list[str] = []

    v13 = root / "scripts/test_village_v1_3_next.py"
    print("\n=== REVIEW VALIDATION Village v1.3 Phase A direct suite ===", flush=True)
    completed = subprocess.run([sys.executable, str(v13)], cwd=root)
    if completed.returncode != 0:
        print(f"FAIL Village v1.3 direct suite exit={completed.returncode}")
        failures.append("scripts/test_village_v1_3_next.py")
    else:
        print("PASS Village v1.3 direct suite")

    for rel in REPLAYS:
        path = root / rel
        if not path.is_file():
            print(f"FAIL missing replay: {rel}")
            failures.append(rel)
            continue
        print(f"\n=== REPLAY {rel} ===", flush=True)
        completed = subprocess.run([sys.executable, str(path)], cwd=root)
        if completed.returncode != 0:
            print(f"FAIL replay exit={completed.returncode}: {rel}")
            failures.append(rel)
        else:
            print(f"PASS {rel}")

    if failures:
        print("\nPUBLIC_REPLAY_SUITE=FAIL")
        for rel in failures:
            print(" -", rel)
        return 1

    print(f"\nPUBLIC_REPLAY_SUITE=PASS count={len(REPLAYS)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
