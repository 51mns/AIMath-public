#!/usr/bin/env python3
"""Run every executable public claim package using the current Python.

This is intentionally a public-snapshot replay suite. Claims whose accepted
public evidence is prose/proof only are checked by layout/review presence, not
invented executable tests.
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
