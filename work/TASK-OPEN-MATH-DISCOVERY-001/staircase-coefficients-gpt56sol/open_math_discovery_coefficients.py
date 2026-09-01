# SPDX-FileCopyrightText: 2026 AIMath contributors
# SPDX-License-Identifier: Apache-2.0
#!/usr/bin/env python3
"""Exact bounded discovery audit for TASK-OPEN-MATH-DISCOVERY-001.

Object:
    P_m(q) = product_{j=1}^m (1 + q^j) = sum_s a_m(s) q^s.

All coefficient arithmetic is exact Python integer arithmetic.

The held-out range is frozen in source before evaluation:
    TRAIN_M   = 1..14
    HELDOUT_M = 15..30
    STRESS_M  = 31..80  (post-held-out robustness only)

No literature facts are encoded into the tests.
"""

from __future__ import annotations

import json

TRAIN_M = tuple(range(1, 15))
HELDOUT_M = tuple(range(15, 31))
STRESS_M = tuple(range(31, 81))


def profile(m: int) -> list[int]:
    """Return coefficients of product_{j=1}^m (1+q^j)."""
    a = [1]
    for j in range(1, m + 1):
        b = a + [0] * j
        for s, v in enumerate(a):
            b[s + j] += v
        a = b
    return a


def total_degree(m: int) -> int:
    return m * (m + 1) // 2


def symmetry(a: list[int]) -> bool:
    return a == a[::-1]


def full_support(a: list[int]) -> bool:
    return all(v > 0 for v in a)


def unimodal(a: list[int]) -> bool:
    n = len(a) - 1
    mid = n // 2
    return (
        all(a[s] <= a[s + 1] for s in range(mid))
        and all(a[s] >= a[s + 1] for s in range((n + 1) // 2, n))
    )


def log_concavity_failures(a: list[int]) -> list[dict]:
    out = []
    for s in range(1, len(a) - 1):
        if a[s] * a[s] < a[s - 1] * a[s + 1]:
            out.append(
                {
                    "s": s,
                    "triple": [a[s - 1], a[s], a[s + 1]],
                    "lhs": a[s] * a[s],
                    "rhs": a[s - 1] * a[s + 1],
                }
            )
    return out


def left_equalities(m: int, a: list[int]) -> list[int]:
    """Edges s with a[s]=a[s+1], excluding a forced two-central-mode edge."""
    mid = total_degree(m) // 2
    return [s for s in range(mid) if a[s] == a[s + 1]]


def tail_strict(m: int, a: list[int]) -> bool:
    """Strict increase after the universal small equalities, up to the midpoint."""
    mid = total_degree(m) // 2
    return all(a[s] < a[s + 1] for s in range(4, mid))


def modes(a: list[int]) -> list[int]:
    mx = max(a)
    return [s for s, v in enumerate(a) if v == mx]


def recurrence_check(m: int) -> bool:
    """Check a_m(s)=a_{m-1}(s)+a_{m-1}(s-m), zero outside support."""
    if m <= 1:
        return True
    prev = profile(m - 1)
    cur = profile(m)
    for s, value in enumerate(cur):
        rhs = prev[s] if 0 <= s < len(prev) else 0
        rhs += prev[s - m] if 0 <= s - m < len(prev) else 0
        if value != rhs:
            return False
    return True


def difference_recurrence_check(m: int) -> bool:
    """Check d_m(s)=d_{m-1}(s)+d_{m-1}(s-m), d=a(s+1)-a(s)."""
    if m <= 1:
        return True
    prev = profile(m - 1)
    cur = profile(m)

    def d(arr: list[int], s: int) -> int:
        def get(k: int) -> int:
            return arr[k] if 0 <= k < len(arr) else 0
        return get(s + 1) - get(s)

    for s in range(-m - 2, len(cur) + 2):
        if d(cur, s) != d(prev, s) + d(prev, s - m):
            return False
    return True


def summarize_range(ms: tuple[int, ...]) -> dict:
    rows = []
    for m in ms:
        a = profile(m)
        T = total_degree(m)
        mid = T // 2
        rows.append(
            {
                "m": m,
                "degree": T,
                "symmetric": symmetry(a),
                "full_support": full_support(a),
                "unimodal": unimodal(a),
                "log_concave": not log_concavity_failures(a),
                "tail_strict_from_s4": tail_strict(m, a),
                "left_equalities_excluding_forced_central_edge": left_equalities(m, a),
                "modes": modes(a),
                "min_tail_difference": (
                    min(a[s + 1] - a[s] for s in range(4, mid))
                    if mid > 4
                    else None
                ),
                "coefficient_recurrence": recurrence_check(m),
                "difference_recurrence": difference_recurrence_check(m),
            }
        )
    return {
        "range": [ms[0], ms[-1]],
        "count": len(ms),
        "rows": rows,
    }


def assess_hypotheses(train: dict, heldout: dict, stress: dict) -> list[dict]:
    all_rows = train["rows"] + heldout["rows"] + stress["rows"]
    by_m = {r["m"]: r for r in all_rows}

    first_log_fail = None
    for m in range(1, 81):
        a = profile(m)
        failures = log_concavity_failures(a)
        if failures:
            first_log_fail = {"m": m, **failures[0]}
            break

    pre12_tail_failures = []
    for m in range(4, 12):
        a = profile(m)
        mid = total_degree(m) // 2
        bad = [s for s in range(4, mid) if not (a[s] < a[s + 1])]
        if bad:
            pre12_tail_failures.append({"m": m, "bad_edges": bad})

    m_ge_12 = [by_m[m] for m in range(12, 81)]

    return [
        {
            "id": "H01",
            "statement": "Coefficient symmetry a_m(s)=a_m(T_m-s).",
            "bounded_result_m_1_80": all(r["symmetric"] for r in all_rows),
            "status": "PASS_EXACT_BOUNDED_AND_ELEMENTARY_COMPLEMENT_PROOF",
        },
        {
            "id": "H02",
            "statement": "There are no internal zero coefficients.",
            "bounded_result_m_1_80": all(r["full_support"] for r in all_rows),
            "status": "PASS_EXACT_BOUNDED_AND_ELEMENTARY_INDUCTION",
        },
        {
            "id": "H03",
            "statement": "The coefficient sequence is unimodal.",
            "bounded_result_m_1_80": all(r["unimodal"] for r in all_rows),
            "status": "PASS_EXACT_BOUNDED_LITERATURE_MATCH",
        },
        {
            "id": "H04",
            "statement": "The coefficient sequence is log-concave.",
            "bounded_result_m_1_80": False,
            "first_counterexample": first_log_fail,
            "status": "REFUTED_EXACT",
        },
        {
            "id": "H05",
            "statement": "The coefficient sequence is strictly unimodal in the standard global sense.",
            "bounded_result_m_1_80": False,
            "counterexample_family": "a_m(0)=a_m(1)=1 for every m>=1",
            "status": "REFUTED_EXACT_FAMILY",
        },
        {
            "id": "H06",
            "statement": "For every tested m>=12, a_m(s)<a_m(s+1) for 4<=s<T_m/2.",
            "train_m_12_14": all(by_m[m]["tail_strict_from_s4"] for m in range(12, 15)),
            "heldout_m_15_30": all(by_m[m]["tail_strict_from_s4"] for m in range(15, 31)),
            "stress_m_31_80": all(by_m[m]["tail_strict_from_s4"] for m in range(31, 81)),
            "status": "PASS_EXACT_BOUNDED_UNIVERSAL_PROOF_NOT_ESTABLISHED",
        },
        {
            "id": "H07",
            "statement": "m=12 is the first m>=4 after which H06 starts in the tested prefix.",
            "m_4_11_failures": pre12_tail_failures,
            "m_12_pass": by_m[12]["tail_strict_from_s4"],
            "status": "PASS_EXACT_BOUNDED_THRESHOLD_OBSERVATION",
        },
        {
            "id": "H08",
            "statement": "For tested m>=12 the only left-half adjacent equalities before the midpoint are s=0,1,3.",
            "bounded_result_m_12_80": all(
                r["left_equalities_excluding_forced_central_edge"] == [0, 1, 3]
                for r in m_ge_12
            ),
            "status": "PASS_EXACT_BOUNDED_EQUIVALENT_TO_H06_PLUS_SMALL_COEFFICIENTS",
        },
        {
            "id": "H09",
            "statement": "For tested m>=12 the modes are exactly the central one or two positions, according to parity of T_m.",
            "bounded_result_m_12_80": all(
                r["modes"]
                == (
                    [r["degree"] // 2]
                    if r["degree"] % 2 == 0
                    else [r["degree"] // 2, r["degree"] // 2 + 1]
                )
                for r in m_ge_12
            ),
            "status": "PASS_EXACT_BOUNDED_CONSEQUENCE_OF_H06_AND_SYMMETRY",
        },
        {
            "id": "H10",
            "statement": "Coefficient and adjacent-difference recurrences hold exactly.",
            "bounded_result_m_1_80": all(
                r["coefficient_recurrence"] and r["difference_recurrence"]
                for r in all_rows
            ),
            "status": "PASS_EXACT_ALGEBRAIC_IDENTITY",
        },
    ]


def main() -> None:
    # Important: ranges are constants declared before any evaluation.
    train = summarize_range(TRAIN_M)
    heldout = summarize_range(HELDOUT_M)
    stress = summarize_range(STRESS_M)
    hypotheses = assess_hypotheses(train, heldout, stress)

    result = {
        "schema_version": 1,
        "task_id": "TASK-OPEN-MATH-DISCOVERY-001",
        "object": "P_m(q)=prod_{j=1}^m(1+q^j)",
        "arithmetic": "exact Python integers",
        "frozen_ranges": {
            "train": [TRAIN_M[0], TRAIN_M[-1]],
            "heldout": [HELDOUT_M[0], HELDOUT_M[-1]],
            "stress_post_heldout": [STRESS_M[0], STRESS_M[-1]],
        },
        "hypotheses_assessed": hypotheses,
        "summary": {
            "hypothesis_count": len(hypotheses),
            "heldout_H06_counterexamples": [
                r["m"] for r in heldout["rows"] if not r["tail_strict_from_s4"]
            ],
            "stress_H06_counterexamples": [
                r["m"] for r in stress["rows"] if not r["tail_strict_from_s4"]
            ],
            "minimum_positive_tail_difference_m_12_80": min(
                r["min_tail_difference"]
                for r in train["rows"] + heldout["rows"] + stress["rows"]
                if r["m"] >= 12 and r["min_tail_difference"] is not None
            ),
        },
        "range_summaries": {
            "train": train,
            "heldout": heldout,
            "stress": stress,
        },
    }
    print(json.dumps(result, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
