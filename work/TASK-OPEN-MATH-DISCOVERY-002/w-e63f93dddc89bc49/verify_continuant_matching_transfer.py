#!/usr/bin/env python3
# SPDX-FileCopyrightText: 2026 AIMath contributors
# SPDX-License-Identifier: Apache-2.0

from __future__ import annotations

from fractions import Fraction
from hashlib import sha256
from itertools import product


SEED = "AIMath-TASK-OPEN-MATH-DISCOVERY-002-w-e63f93dddc89bc49-v1"
TRAIN_MAX_LEN = 5
TRAIN_DIGITS = range(1, 5)
HELD_OUT_CASES = 128


def continuant(a: tuple[int, ...]) -> int:
    if not a:
        return 1
    km2, km1 = 1, a[0]
    for x in a[1:]:
        km2, km1 = km1, x * km1 + km2
    return km1


def continued_fraction(a: tuple[int, ...]) -> Fraction:
    if not a:
        raise ValueError("continued fraction word must be nonempty")
    value = Fraction(a[-1], 1)
    for x in reversed(a[:-1]):
        value = Fraction(x, 1) + Fraction(1, value)
    return value


def weighted_path_partition_direct(a: tuple[int, ...], dimer_weight: int = 1) -> int:
    """Enumerate edge subsets directly; selected edges must be a matching."""
    n = len(a)
    total = 0
    for mask in range(1 << max(0, n - 1)):
        if mask & (mask << 1):
            continue
        unmatched = [True] * n
        dimers = 0
        valid = True
        for edge in range(n - 1):
            if (mask >> edge) & 1:
                if not unmatched[edge] or not unmatched[edge + 1]:
                    valid = False
                    break
                unmatched[edge] = False
                unmatched[edge + 1] = False
                dimers += 1
        if not valid:
            continue
        weight = dimer_weight ** dimers
        for i, is_unmatched in enumerate(unmatched):
            if is_unmatched:
                weight *= a[i]
        total += weight
    return total


def transfer_matrix_product(a: tuple[int, ...]) -> tuple[tuple[int, int], tuple[int, int]]:
    # Product of M(x)=[[x,1],[1,0]].
    A, B, C, D = 1, 0, 0, 1
    for x in a:
        A, B, C, D = A * x + B, A, C * x + D, C
    return ((A, B), (C, D))


def perturb(a: tuple[int, ...], j: int, t: int) -> tuple[int, ...]:
    out = list(a)
    out[j] += t
    if out[j] <= 0:
        raise ValueError("perturbation left positive domain")
    return tuple(out)


def finite_sensitivity_prediction(a: tuple[int, ...], j: int, t: int) -> Fraction:
    """Exact predicted change under a_j -> a_j+t, j is zero-based."""
    a2 = perturb(a, j, t)
    q = continuant(a[1:])
    q2 = continuant(a2[1:])
    suffix = continuant(a[j + 1 :])
    return Fraction(((-1) ** j) * t * suffix * suffix, q * q2)


def digest_int(label: str, counter: int) -> int:
    h = sha256(f"{SEED}|{label}|{counter}".encode()).digest()
    return int.from_bytes(h, "big")


def held_out_case(counter: int) -> tuple[tuple[int, ...], int, int]:
    n = 6 + digest_int("n", counter) % 7  # 6..12, outside train lengths
    a = tuple(1 + digest_int(f"a{i}", counter) % 25 for i in range(n))
    j = digest_int("j", counter) % n
    t = 1 + digest_int("t", counter) % 9
    return a, j, t


def check_case(a: tuple[int, ...], j: int, t: int) -> None:
    z = weighted_path_partition_direct(a)
    k = continuant(a)
    if z != k:
        raise AssertionError(("path/continuant mismatch", a, z, k))

    p = k
    q = continuant(a[1:])
    x = continued_fraction(a)
    if x != Fraction(p, q):
        raise AssertionError(("continued-fraction mismatch", a, x, p, q))

    mat = transfer_matrix_product(a)
    if mat[0][0] != p or mat[1][0] != q:
        raise AssertionError(("matrix mismatch", a, mat, p, q))
    det = mat[0][0] * mat[1][1] - mat[0][1] * mat[1][0]
    if det != (-1) ** len(a):
        raise AssertionError(("determinant mismatch", a, det))

    a2 = perturb(a, j, t)
    observed = continued_fraction(a2) - x
    predicted = finite_sensitivity_prediction(a, j, t)
    if observed != predicted:
        raise AssertionError(("sensitivity mismatch", a, j, t, observed, predicted))

    # Matching-cut sensitivity for the numerator itself.
    prefix = continuant(a[:j])
    suffix = continuant(a[j + 1 :])
    if continuant(a2) - p != t * prefix * suffix:
        raise AssertionError(("cut factorisation mismatch", a, j, t))


def main() -> None:
    train_words = 0
    train_perturbations = 0
    for n in range(1, TRAIN_MAX_LEN + 1):
        for a in product(TRAIN_DIGITS, repeat=n):
            a = tuple(a)
            train_words += 1
            for j in range(n):
                for t in (1, 2):
                    check_case(a, j, t)
                    train_perturbations += 1

    held_out = []
    for counter in range(HELD_OUT_CASES):
        a, j, t = held_out_case(counter)
        check_case(a, j, t)
        held_out.append(
            {
                "counter": counter,
                "n": len(a),
                "j_one_based": j + 1,
                "t": t,
                "word_sha256": sha256(",".join(map(str, a)).encode()).hexdigest(),
            }
        )

    # Negative controls: the correspondence is specific, not a vague "graph count".
    neg_word = (2, 3)
    if weighted_path_partition_direct(neg_word, dimer_weight=2) == continuant(neg_word):
        raise AssertionError("negative control dimer_weight=2 unexpectedly passed")
    prefix_den_failures = 0
    for a in ((2, 3), (2, 3, 4), (5, 1, 7, 2)):
        wrong_q = continuant(a[:-1])
        if Fraction(continuant(a), wrong_q) != continued_fraction(a):
            prefix_den_failures += 1
    if prefix_den_failures != 3:
        raise AssertionError("negative control wrong denominator unexpectedly passed")

    print("PASS")
    print(f"seed={SEED}")
    print(f"train_words={train_words}")
    print(f"train_perturbations={train_perturbations}")
    print(f"held_out_cases={len(held_out)}")
    print("held_out_length_range=6..12")
    print("held_out_digit_range=1..25")
    print("negative_control_dimer_weight_2=FAIL_AS_EXPECTED")
    print("negative_control_prefix_denominator_failures=3/3")
    print("held_out_digest=" + sha256(
        "\n".join(
            f"{row['counter']}:{row['n']}:{row['j_one_based']}:{row['t']}:{row['word_sha256']}"
            for row in held_out
        ).encode()
    ).hexdigest())


if __name__ == "__main__":
    main()
