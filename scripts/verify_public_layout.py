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
    "docs/FAILED_ROUTES.md",
    "docs/EXPORT_GAPS.md",
    "docs/CONTRIBUTION_TARGETS.md",
    "docs/EVIDENCE_POLICY.md",
    "docs/PUBLIC_EXPORT_VALIDATION.md",
    "docs/CLAIM_LEVELS.md",
    "docs/REPRODUCIBILITY.md",
    "docs/PUBLIC_EXPORT_POLICY.md",
    "docs/PRIVACY_AND_SECURITY.md",
    "scripts/build_public_manifest.py",
    "scripts/reproduce_public_claims.py",
    "research/README.md",
    "reviews/README.md",
    "research/fixed-433/README.md",
    "research/433-springborn-obstruction/README.md",
    "reviews/433-springborn-obstruction/INDEPENDENT_REVIEW.md",
    "research/433-existing-theory-identification/README.md",
    "reviews/433-existing-theory-identification/INDEPENDENT_REVIEW.md",
    "research/gyoda-89/README.md",
    "reviews/gyoda-89/INDEPENDENT_REVIEW.md",
    "research/local-tp2/STATEMENT.md",
    "research/b3rcc-apc/README.md",
    "research/b3rcc-apc/APC_ALL_RANK_THEOREM.md",
    "reviews/b3rcc-apc/APC_ALL_RANK_INDEPENDENT_REVIEW.md",
    "research/equiangular-r18-eta17/README.md",
    "reviews/equiangular-r18-eta17/INDEPENDENT_REVIEW.md",
    "research/dittert-n5-z2/README.md",
    "reviews/dittert-n5-z2/INDEPENDENT_REVIEW.md",
    "research/lonely-runner-r2/README.md",
    "reviews/lonely-runner-r2/INDEPENDENT_REVIEW.md",
    "research/afes-bounded/README.md",
    "reviews/afes-bounded/INDEPENDENT_REVIEW.md",
    "research/thue-morse-rediscovery/README.md",
    "reviews/thue-morse-rediscovery/INDEPENDENT_REVIEW.md",
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
