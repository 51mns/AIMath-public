#!/usr/bin/env python3
# SPDX-FileCopyrightText: 2026 AIMath contributors
# SPDX-License-Identifier: Apache-2.0
from __future__ import annotations

import json
import math
from pathlib import Path

ROOT = Path(__file__).resolve().parent
C = json.loads((ROOT / "AFRD_EXPERIMENT_CONTRACT.json").read_text(encoding="utf-8"))


def fail(msg: str) -> None:
    raise SystemExit(f"FAIL: {msg}")


def main() -> None:
    if C.get("schema_version") != 1:
        fail("schema_version")
    if C.get("task_id") != "TASK-AIMATH-ND-AFRD-001":
        fail("task_id")
    if C.get("candidate_input_rule") != "N_AND_PUBLIC_CONSTANTS_ONLY":
        fail("N-only rule")
    train = C["visible_training"]
    expected_train = len(train["factor_bit_pairs"]) * train["instances_per_pair"]
    if expected_train != train["total_instances"] or expected_train != 12288:
        fail("visible training count")
    hidden = C["hidden_splits"]
    expected = {
        "H0_INTERPOLATION": 3 * 512,
        "H1_SCALE": 3 * 384,
        "H2_BALANCE": 3 * 384,
        "H3_ARITHMETIC": 4 * 256,
        "H4_GENERATOR": 3 * 512,
        "H5_TEMPORAL": 1024,
    }
    got = {k: v["total_instances"] for k, v in hidden.items()}
    if got != expected:
        fail(f"hidden counts {got!r}")
    if sum(got.values()) != C["hidden_total_instances"] or sum(got.values()) != 7424:
        fail("hidden total")
    if hidden["H4_GENERATOR"]["generator"] == train["generator"]:
        fail("H4 generator must differ")
    if hidden["H5_TEMPORAL"].get("generated_after_candidate_freeze") is not True:
        fail("H5 temporal gate")
    forbidden = set(C["factor_labels_forbidden_for"])
    required_forbidden = {
        "candidate_encoding_at_evaluation_time",
        "candidate_readout_at_evaluation_time",
        "feature_generation_on_hidden_instances",
    }
    if not required_forbidden <= forbidden:
        fail("factor-label firewall")
    iface = C["representation_interface"]
    if iface["max_serialized_bytes_per_instance"] > 65536:
        fail("representation size cap")
    if set(iface["evaluation_readouts"]) != {"LOCALISE", "FACTOR"}:
        fail("readout set")
    gate = C["paired_signal_gate"]
    if not (0 < gate["minimum_absolute_net_win_fraction"] <= 0.05):
        fail("net-win threshold")
    if gate["exact_two_sided_binomial_p_max"] > 0.01:
        fail("H0 statistical threshold")
    if set(gate["replication_required_on"]) != {"H4_GENERATOR", "H5_TEMPORAL"}:
        fail("replication splits")
    loc = C["localisation_metric"]
    if loc["trivial_full_interval_bits_saved"] != 0:
        fail("trivial localisation baseline")
    if loc.get("width_budget_fractions") != ["1/2", "1/4", "1/16", "1/256"]:
        fail("localisation width budgets")
    if hidden["H3_ARITHMETIC"].get("factor_bit_pair") != [24, 24]:
        fail("H3 factor-bit freeze")
    strata = hidden["H5_TEMPORAL"].get("strata", {})
    temporal_total = strata.get("BALANCED_24_24", 0) + strata.get("UNBALANCED_20_28", 0) + strata.get("ARITHMETIC_H3_FAMILIES", {}).get("total", 0)
    if temporal_total != 1024:
        fail("H5 strata total")
    if set(C.get("generators", {})) != {"GEN-A", "GEN-B_INDEPENDENT_IMPLEMENTATION_AND_RANDOMNESS"}:
        fail("generator contract")
    # Sanity check the stated metric on a toy interval: odds 3..11 => M=5.
    M, W = 5, 1
    if not math.isclose(math.log2(M / W), math.log2(5.0)):
        fail("bits_saved metric")
    order = C["post_signal_order"]
    if order.index("candidate_specific_literature_search") < order.index("freeze_hidden_results_and_candidate_artifacts"):
        fail("post-signal audit ordering")
    print("PASS: AFRD E0 contract invariants")
    print(f"visible_training={expected_train}")
    print(f"hidden_total={sum(got.values())}")
    print("hidden_splits=" + ",".join(f"{k}:{got[k]}" for k in sorted(got)))


if __name__ == "__main__":
    main()
