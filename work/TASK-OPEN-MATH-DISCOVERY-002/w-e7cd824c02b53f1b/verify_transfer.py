# SPDX-FileCopyrightText: 2026 AIMath contributors
# SPDX-License-Identifier: Apache-2.0

from __future__ import annotations

from hashlib import sha256
import json
from pathlib import Path


def continuant(seq: list[int]) -> int:
    if not seq:
        return 1
    if len(seq) == 1:
        return seq[0]
    km2 = 1
    km1 = seq[0]
    for a in seq[1:]:
        km2, km1 = km1, a * km1 + km2
    return km1


def continued_fraction_pq(seq: list[int]) -> tuple[int, int]:
    return continuant(seq), continuant(seq[1:])


def matching_partition(seq: list[int]) -> int:
    """Brute-force monomer-dimer partition function on the path P_n."""
    n = len(seq)
    total = 0

    def walk(i: int, weight: int) -> None:
        nonlocal total
        if i >= n:
            total += weight
            return
        # Vertex i is unmatched (a monomer), so it contributes a_i.
        walk(i + 1, weight * seq[i])
        # Or edge (i,i+1) is a dimer of weight 1.
        if i + 1 < n:
            walk(i + 2, weight)

    walk(0, 1)
    return total


def signed_tridiagonal(seq: list[int]) -> list[list[int]]:
    n = len(seq)
    matrix = [[0] * n for _ in range(n)]
    for i, a in enumerate(seq):
        matrix[i][i] = a
        if i + 1 < n:
            matrix[i][i + 1] = 1
            matrix[i + 1][i] = -1
    return matrix


def determinant_bareiss(matrix: list[list[int]]) -> int:
    """Fraction-free exact determinant, independent of continuant recurrence."""
    if not matrix:
        return 1
    a = [row[:] for row in matrix]
    n = len(a)
    sign = 1
    previous = 1

    for k in range(n - 1):
        if a[k][k] == 0:
            swap = next((r for r in range(k + 1, n) if a[r][k] != 0), None)
            if swap is None:
                return 0
            a[k], a[swap] = a[swap], a[k]
            sign = -sign

        pivot = a[k][k]
        for i in range(k + 1, n):
            for j in range(k + 1, n):
                numerator = a[i][j] * pivot - a[i][k] * a[k][j]
                if numerator % previous:
                    raise AssertionError("Bareiss exact division failed")
                a[i][j] = numerator // previous
        for i in range(k + 1, n):
            a[i][k] = 0
        previous = pivot

    return sign * a[-1][-1]


def frozen_case(case_id: int) -> tuple[list[int], int, int]:
    digest = sha256(f"AIMath-transfer-heldout-v1:{case_id}".encode()).digest()
    n = 5 + digest[0] % 8
    seq = [1 + digest[i] % 9 for i in range(1, n + 1)]
    j0 = 1 + digest[16] % (n - 2)
    t = 1 + digest[17] % 7
    return seq, j0, t


def evaluate_case(case_id: int) -> dict:
    seq, j0, t = frozen_case(case_id)
    perturbed = seq[:]
    perturbed[j0] += t

    p, q = continued_fraction_pq(seq)
    direct_p, direct_q = continued_fraction_pq(perturbed)

    suffix = continuant(seq[j0 + 1 :])
    predicted_p = p + t * continuant(seq[:j0]) * suffix
    predicted_q = q + t * continuant(seq[1:j0]) * suffix

    checks = {
        "numerator_cut_prediction": predicted_p == direct_p,
        "denominator_cut_prediction": predicted_q == direct_q,
        "matching_base": matching_partition(seq) == continuant(seq),
        "matching_perturbed": matching_partition(perturbed) == continuant(perturbed),
        "determinant_base": determinant_bareiss(signed_tridiagonal(seq)) == continuant(seq),
        "determinant_perturbed": determinant_bareiss(signed_tridiagonal(perturbed))
        == continuant(perturbed),
    }

    return {
        "case": case_id,
        "n": len(seq),
        "a": seq,
        "j0": j0,
        "t": t,
        "base": {"p": p, "q": q},
        "direct_perturbed": {"p": direct_p, "q": direct_q},
        "cut_prediction": {"p": predicted_p, "q": predicted_q},
        "checks": checks,
        "pass": all(checks.values()),
    }


def main() -> int:
    rows = [evaluate_case(case_id) for case_id in range(64)]
    failures = [row["case"] for row in rows if not row["pass"]]
    output = {
        "schema_version": 1,
        "task_id": "TASK-OPEN-MATH-DISCOVERY-002",
        "worker_id": "w-e7cd824c02b53f1b",
        "exact_public_base": "279ba9fa98befe3aee37bfd1a98e4f688d333bd4",
        "freeze_commit": "a721b416a30c49820bdc4c4ac789782992c25691",
        "heldout_rule": "SHA256('AIMath-transfer-heldout-v1:' + decimal(case_id)), cases 0..63",
        "integer_arithmetic_only": True,
        "case_transcript_sha256": sha256(
            json.dumps(rows, sort_keys=True, separators=(",", ":")).encode()
        ).hexdigest(),
        "summary": {
            "cases": len(rows),
            "checks_per_case": 6,
            "checks_total": 6 * len(rows),
            "failures": failures,
            "all_pass": not failures,
            "n_min": min(row["n"] for row in rows),
            "n_max": max(row["n"] for row in rows),
            "max_abs_perturbed_numerator": max(
                abs(row["direct_perturbed"]["p"]) for row in rows
            ),
            "max_abs_perturbed_denominator": max(
                abs(row["direct_perturbed"]["q"]) for row in rows
            ),
        },
    }
    path = Path(__file__).with_name("heldout_results.json")
    path.write_text(json.dumps(output, indent=2) + "\n", encoding="utf-8")
    print(
        f"PASS: {len(rows) - len(failures)}/{len(rows)} held-out cases; "
        f"{6 * len(rows) - 6 * len(failures)}/{6 * len(rows)} exact checks"
        if not failures
        else f"FAIL: held-out cases {failures}"
    )
    print(f"results={path}")
    return 0 if not failures else 1


if __name__ == "__main__":
    raise SystemExit(main())
