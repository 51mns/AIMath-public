#!/usr/bin/env python3
from __future__ import annotations
from pathlib import Path
import sys

REQUIRED = [
    "README.md",
    "README.ja.md",
    "CONTRIBUTING.md",
    "SECURITY.md",
    "LICENSING.md",
    "docs/RESULTS.md",
    "docs/CLAIM_LEVELS.md",
    "docs/REPRODUCIBILITY.md",
    "docs/PUBLIC_EXPORT_POLICY.md",
    "docs/PRIVACY_AND_SECURITY.md",
    "research/README.md",
    "reviews/README.md",
]

def main() -> int:
    root = Path(sys.argv[1] if len(sys.argv) > 1 else ".").resolve()
    missing = [p for p in REQUIRED if not (root / p).is_file()]
    if missing:
        print("FAIL: missing required public files:")
        for p in missing:
            print(" -", p)
        return 1
    print(f"PASS: public layout ({len(REQUIRED)} required files present)")
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
