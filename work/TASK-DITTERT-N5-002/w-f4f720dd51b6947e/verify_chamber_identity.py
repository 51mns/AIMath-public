# SPDX-FileCopyrightText: 2026 AIMath contributors
# SPDX-License-Identifier: Apache-2.0

"""Exact regression checks for TASK-DITTERT-N5-002 chamber reduction.

This script is deliberately not a proof of the universal Z2 exclusion.
It checks, with exact Fraction arithmetic and brute-force permanents, the
algebraic identities used by REPRODUCTION.md on several asymmetric inputs.
"""

from fractions import Fraction as F
from itertools import permutations


def permanent(matrix):
    n = len(matrix)
    total = F(0)
    for p in permutations(range(n)):
        term = F(1)
        for i, j in enumerate(p):
            term *= matrix[i][j]
        total += term
    return total


def minor(matrix, i, j):
    return [
        [x for jj, x in enumerate(row) if jj != j]
        for ii, row in enumerate(matrix)
        if ii != i
    ]


def build(a, b, c, d, e, f, g):
    return [
        [F(0), a, b, b, b],
        [c, F(0), d, d, d],
        [e, f, g, g, g],
        [e, f, g, g, g],
        [e, f, g, g, g],
    ]


def row_sums(A):
    return [sum(row, F(0)) for row in A]


def col_sums(A):
    return [sum((A[i][j] for i in range(5)), F(0)) for j in range(5)]


def phi_ij(A, i, j):
    r = row_sums(A)
    c = col_sums(A)
    rp = F(1)
    cp = F(1)
    for k in range(5):
        if k != i:
            rp *= r[k]
        if k != j:
            cp *= c[k]
    return rp + cp - permanent(minor(A, i, j))


def check(params):
    a, b, c, d, e, f, g = params
    A = build(*params)

    m11 = permanent(minor(A, 0, 0))
    m12 = permanent(minor(A, 0, 1))
    m22 = permanent(minor(A, 1, 1))
    m21 = permanent(minor(A, 1, 0))

    assert m11 == 18 * d * f * g**2
    assert m12 == 6 * g**2 * (c * g + 3 * d * e)
    assert m22 == 18 * b * e * g**2
    assert m21 == 6 * g**2 * (a * g + 3 * b * f)

    target = 6 * g**2 * ((a + c) * g + 3 * (d - b) * (e - f))

    col_pair = (
        phi_ij(A, 0, 0)
        - phi_ij(A, 0, 1)
        + phi_ij(A, 1, 1)
        - phi_ij(A, 1, 0)
    )
    row_pair = (
        phi_ij(A, 0, 0)
        - phi_ij(A, 1, 0)
        + phi_ij(A, 1, 1)
        - phi_ij(A, 0, 1)
    )
    assert col_pair == target
    assert row_pair == target

    m13 = permanent(minor(A, 0, 2))
    m31 = permanent(minor(A, 2, 0))
    m32 = permanent(minor(A, 2, 1))
    m23 = permanent(minor(A, 1, 2))
    m33 = permanent(minor(A, 2, 2))

    cycle1_phi = (
        phi_ij(A, 0, 1)
        + phi_ij(A, 2, 2)
        - phi_ij(A, 0, 2)
        - phi_ij(A, 2, 1)
    )
    cycle1_minors = m12 + m33 - m13 - m32
    assert cycle1_phi == -cycle1_minors

    cycle2_phi = (
        phi_ij(A, 1, 0)
        + phi_ij(A, 2, 2)
        - phi_ij(A, 1, 2)
        - phi_ij(A, 2, 0)
    )
    cycle2_minors = m21 + m33 - m23 - m31
    assert cycle2_phi == -cycle2_minors


def main():
    samples = [
        tuple(map(F, (2, 3, 5, 7, 11, 13, 17))),
        (F(1, 2), F(2, 3), F(3, 5), F(5, 7), F(7, 11), F(11, 13), F(13, 17)),
        (F(7, 19), F(5, 23), F(11, 29), F(13, 31), F(17, 37), F(19, 41), F(23, 43)),
        # Deliberately choose both signs for (d-b)(e-f).
        (F(3, 10), F(1, 5), F(2, 7), F(2, 5), F(1, 2), F(1, 4), F(1, 6)),
        (F(3, 10), F(2, 5), F(2, 7), F(1, 5), F(1, 2), F(1, 4), F(1, 6)),
    ]
    for params in samples:
        check(params)
    print("PASS: exact chamber and cycle identities")


if __name__ == "__main__":
    main()
