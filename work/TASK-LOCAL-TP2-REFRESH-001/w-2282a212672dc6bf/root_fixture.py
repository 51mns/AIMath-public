#!/usr/bin/env python3
# SPDX-FileCopyrightText: 2026 AIMath contributors
# SPDX-License-Identifier: Apache-2.0
"""Exact integer sanity fixture for the frozen Local TP2 root.

This script is deliberately narrow.  It verifies only the canonical root data
used while triaging a new continuant/LGV proof architecture.  It does not prove
Local TP2 at any positive depth.
"""


def add_poly(a, b, scale_b=1):
    n = max(len(a), len(b))
    out = [0] * n
    for i in range(n):
        out[i] = (a[i] if i < len(a) else 0) + scale_b * (b[i] if i < len(b) else 0)
    while len(out) > 1 and out[-1] == 0:
        out.pop()
    return out


def laurent_mul(a, b):
    out = {}
    for i, ai in a.items():
        for j, bj in b.items():
            out[i + j] = out.get(i + j, 0) + ai * bj
    return {k: v for k, v in out.items() if v}


def x_power_laurent(power):
    out = {0: 1}
    x_laurent = {-1: 1, 1: 1}
    for _ in range(power):
        out = laurent_mul(out, x_laurent)
    return out


def xpoly_to_laurent(coeffs):
    """coeffs[i] is the coefficient of x**i."""
    out = {}
    for power, coeff in enumerate(coeffs):
        if coeff == 0:
            continue
        for exponent, multiplicity in x_power_laurent(power).items():
            out[exponent] = out.get(exponent, 0) + coeff * multiplicity
    return {k: v for k, v in out.items() if v}


def h_profile(coeffs):
    laurent = xpoly_to_laurent(coeffs)
    degree = len(coeffs) - 1
    assert all(laurent.get(n, 0) == laurent.get(-n, 0) for n in range(degree + 1))
    return [laurent.get(n, 0) for n in range(degree + 1)]


def main():
    # Canonical root: C=G_(1/2), U=G_(1/3), V=G_(2/3).
    # Coefficients are stored low degree -> high degree.
    C = [5, 6, 2]
    U = [13, 26, 18, 4]
    V = [29, 74, 74, 34, 6]

    S = add_poly(U, C, scale_b=-1)
    D = add_poly(V, U, scale_b=-1)

    assert S == [8, 20, 16, 4]
    assert D == [16, 48, 56, 30, 6]

    hs = h_profile(S)
    hd = h_profile(D)
    assert hs == [40, 32, 16, 4]
    assert hd == [164, 138, 80, 30, 6]

    f = []
    for n in range(len(hs)):
        hs_next = hs[n + 1] if n + 1 < len(hs) else 0
        f.append(hd[n + 1] * hs[n] - hd[n] * hs_next)

    assert f == [272, 352, 160, 24]
    assert all(value > 0 for value in f)

    print("ROOT_FIXTURE_PASS")
    print("H(S)=", hs)
    print("H(D)=", hd)
    print("F=", f)


if __name__ == "__main__":
    main()
