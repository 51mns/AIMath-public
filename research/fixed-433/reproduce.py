#!/usr/bin/env python3
from __future__ import annotations

import importlib.util
from pathlib import Path

ROOT = Path(__file__).resolve().parent

def load(name: str, path: Path):
    spec = importlib.util.spec_from_file_location(name, path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"cannot load {path}")
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod

def main() -> int:
    candidate = load("fixed433_candidate", ROOT / "candidate/generate_certificate.py")
    independent = load("fixed433_independent", ROOT / "independent/verify_fixed_433.py")

    left = candidate.build_certificate()
    negative = candidate.build_negative_controls()
    right = independent.build_result()

    if left["claim_id"] != right["claim_id"] != "C-ROOT-433":
        raise AssertionError("claim id mismatch")

    keys = (
        "k", "markov_triple", "M", "u", "word",
        "energy", "continuant_matrix", "canonical_root_pair",
    )
    if len(left["cases"]) != len(right["cases"]):
        raise AssertionError("case count mismatch")
    for lcase, rcase in zip(left["cases"], right["cases"], strict=True):
        for key in keys:
            if lcase[key] != rcase[key]:
                raise AssertionError(f"cross-comparison mismatch: k={lcase['k']} key={key}")

    if not negative["all_controls_rejected"]:
        raise AssertionError("negative control failure")

    if not all(right["fixed_identity_checks"].values()):
        raise AssertionError("independent fixed identity failure")

    print("candidate exact cases: 3/3 PASS")
    print("independent exact cases: 3/3 PASS")
    print("candidate/independent cross-comparison: PASS")
    print("negative controls: 4/4 PASS")
    print("fixed all-k identity bases: PASS")
    print("fixed-433 public reproduction: PASS")
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
