# SPDX-FileCopyrightText: 2026 AIMath contributors
# SPDX-License-Identifier: Apache-2.0
from __future__ import annotations

from fractions import Fraction
from functools import reduce
from math import gcd
import json


TRAIN = {
    "A": [2, 3, 7, 18, 47, 123, 322, 843],
    "B": [2, 5, 23, 110, 527, 2525, 12098, 57965],
}


def primitive_canonical(a: int, b: int, d: int):
    g = reduce(gcd, (abs(a), abs(b), abs(d)))
    if g == 0:
        return None
    triple = [a // g, b // g, d // g]
    for v in triple:
        if v:
            if v < 0:
                triple = [-x for x in triple]
            break
    return tuple(triple)


def constant_quadratic_seals(seq: list[int], bound: int = 8):
    pairs = list(zip(seq[:-1], seq[1:]))
    seals = []
    for a in range(-bound, bound + 1):
        for b in range(-bound, bound + 1):
            for d in range(-bound, bound + 1):
                if (a, b, d) == (0, 0, 0):
                    continue
                if primitive_canonical(a, b, d) != (a, b, d):
                    continue
                values = [a*x*x + b*x*y + d*y*y for x, y in pairs]
                if len(set(values)) == 1:
                    seals.append({"coefficients": [a, b, d], "constant": values[0]})
    return seals


def fit_baseline_c(seq3: list[int]) -> Fraction:
    x, y, z = seq3
    return Fraction(z + x, y)


def fit_seal_c(seq3: list[int]) -> Fraction:
    x, y, z = seq3
    return Fraction(z*z - x*x, y*(z - x))


def predict(c: Fraction, first_two: list[int], count: int) -> list[Fraction]:
    out = [Fraction(first_two[0]), Fraction(first_two[1])]
    while len(out) < count:
        out.append(c*out[-1] - out[-2])
    return out


def pell7_x(count: int) -> list[int]:
    # Generate from multiplication by 8 + 3*sqrt(7), not from a fitted order-2 recurrence.
    x, y = 1, 0
    out = []
    for _ in range(count):
        assert x*x - 7*y*y == 1
        out.append(x)
        x, y = 8*x + 21*y, 3*x + 8*y
    return out


def bell_numbers(count: int) -> list[int]:
    row = [1]
    out = [1]
    for n in range(1, count):
        new = [row[-1]]
        for j in range(1, n + 1):
            new.append(new[-1] + row[j - 1])
        row = new
        out.append(row[0])
    return out


def matmul(A, B):
    return [
        [A[0][0]*B[0][0] + A[0][1]*B[1][0],
         A[0][0]*B[0][1] + A[0][1]*B[1][1]],
        [A[1][0]*B[0][0] + A[1][1]*B[1][0],
         A[1][0]*B[0][1] + A[1][1]*B[1][1]],
    ]


def trace_power_sequence(c: int, count: int) -> list[int]:
    M = [[c, -1], [1, 0]]
    P = [[1, 0], [0, 1]]
    out = []
    for _ in range(count):
        out.append(P[0][0] + P[1][1])
        P = matmul(P, M)
    return out


def first_mismatch(actual: list[int], forecast: list[Fraction], start: int):
    for i in range(start, len(actual)):
        if forecast[i].denominator != 1 or forecast[i].numerator != actual[i]:
            return i
    return None


def main():
    seals = {name: constant_quadratic_seals(seq) for name, seq in TRAIN.items()}
    assert seals["A"] == [{"coefficients": [1, -3, 1], "constant": -5}]
    assert seals["B"] == [{"coefficients": [1, -5, 1], "constant": -21}]

    # Reveal provenance only after representation freeze: exact trace sequences.
    assert trace_power_sequence(3, 8) == TRAIN["A"]
    assert trace_power_sequence(5, 8) == TRAIN["B"]

    pell = pell7_x(10)
    bell = bell_numbers(10)

    pell_cb = fit_baseline_c(pell[:3])
    pell_cs = fit_seal_c(pell[:3])
    assert pell_cb == pell_cs == 16
    pell_base = predict(pell_cb, pell[:2], len(pell))
    pell_seal = predict(pell_cs, pell[:2], len(pell))
    pell_base_mismatch = first_mismatch(pell, pell_base, 3)
    pell_seal_mismatch = first_mismatch(pell, pell_seal, 3)
    assert pell_base_mismatch is None
    assert pell_seal_mismatch is None
    assert pell_base == pell_seal

    bell_cb = fit_baseline_c(bell[:3])
    bell_cs = fit_seal_c(bell[:3])
    assert bell_cb == bell_cs == 3
    bell_base = predict(bell_cb, bell[:2], len(bell))
    bell_seal = predict(bell_cs, bell[:2], len(bell))
    bell_base_mismatch = first_mismatch(bell, bell_base, 3)
    bell_seal_mismatch = first_mismatch(bell, bell_seal, 3)
    assert bell_base_mismatch == bell_seal_mismatch == 4
    assert bell_base == bell_seal

    result = {
        "task_id": "TASK-AIMATH-ND-001",
        "worker_id": "w-5023e0723711",
        "public_base": "71547cb5d757afaace54b558f2d0a4a49fad5656",
        "train_seals": seals,
        "train_provenance_after_freeze": {
            "A": "tr(M_3^n), M_c=[[c,-1],[1,0]], n=0..7",
            "B": "tr(M_5^n), M_c=[[c,-1],[1,0]], n=0..7",
        },
        "held_out": {
            "pell_D7_x": pell,
            "baseline_c": str(pell_cb),
            "seal_c": str(pell_cs),
            "reserved_indices": list(range(3, 10)),
            "baseline_correct": 7,
            "seal_correct": 7,
            "baseline_first_mismatch": pell_base_mismatch,
            "seal_first_mismatch": pell_seal_mismatch,
        },
        "adversarial_control": {
            "bell": bell,
            "baseline_c_from_first3": str(bell_cb),
            "seal_c_from_first3": str(bell_cs),
            "baseline_first_mismatch": bell_base_mismatch,
            "seal_first_mismatch": bell_seal_mismatch,
        },
        "equivalence": {
            "parameter_formula_baseline": "(z+x)/y",
            "parameter_formula_seal": "(z^2-x^2)/(y*(z-x)) = (z+x)/y",
            "forecast_sequences_identical_on_both_transfer_sets": True,
        },
        "metrics": {
            "pell_baseline_correct_of_7": 7,
            "pell_seal_correct_of_7": 7,
            "strict_predictive_gain": False,
            "strict_falsification_gain": False,
            "proof_obligation_compression": False,
            "reusable_non_equivalent_invariant_gain": False,
        },
        "decision": "NO_STRICT_UTILITY_GAIN",
        "claim_level": "EXPLORATORY",
    }
    print(json.dumps(result, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
