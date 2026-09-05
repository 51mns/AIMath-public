#!/usr/bin/env python3
# SPDX-FileCopyrightText: 2026 AIMath contributors
# SPDX-License-Identifier: Apache-2.0
"""Exact verifier for TASK-EQUIANGULAR-R18-001 structural reduction.

This does not enumerate all hypothetical 59-line spectra and does not prove N(18) <= 58.
It verifies the exact arithmetic in the uniform reduction and checks the already-accepted
eta=17 spectrum as a regression fixture.
"""

from math import comb


def mul(a, b):
    """Multiply integer polynomials stored in ascending coefficient order."""
    out = [0] * (len(a) + len(b) - 1)
    for i, x in enumerate(a):
        for j, y in enumerate(b):
            out[i + j] += x * y
    return out


def ppow(a, n):
    out = [1]
    while n:
        if n & 1:
            out = mul(out, a)
        a = mul(a, a)
        n //= 2
    return out


def shift_plus(p, c):
    """Return p(x+c), with p in ascending coefficient order."""
    out = [0] * len(p)
    for k, pk in enumerate(p):
        for j in range(k + 1):
            out[j] += pk * comb(k, j) * (c ** (k - j))
    return out


def weak_type2(p):
    """Weak type-2 test for a monic polynomial in ascending order."""
    n = len(p) - 1
    assert p[-1] == 1
    desc = list(reversed(p))
    return all(desc[i] % (1 << (i - 1)) == 0 for i in range(1, n + 1))


def exact_theta(R, d):
    """Smallest eta with eta*4^((eta-1)/eta) > R, compared by integers."""
    for eta in range(1, d + 1):
        # Raise both positive sides to eta:
        # eta^eta * 4^(eta-1) > R^eta.
        if eta**eta * 4 ** (eta - 1) > R**eta:
            return eta
    return None


def main():
    n, d, lam0 = 59, 18, -5

    # Closest odd integer to ((d-n)*lam0)/d = 205/18 is 11.
    target_num = (d - n) * lam0
    assert target_num == 205
    assert abs(target_num - d * 11) < abs(target_num - d * 13)
    assert abs(target_num - d * 11) < abs(target_num - d * 9)
    kappa = 11

    R = (
        n * (n - 1)
        - lam0 * lam0 * (n - d)
        + 2 * kappa * lam0 * (n - d)
        + d * kappa * kappa
    )
    assert R == 65

    theta = exact_theta(R, d)
    assert theta == 18
    assert 17**17 * 4**16 <= 65**17
    assert 18**18 * 4**17 > 65**18
    forced_kappa_multiplicity = d + 1 - theta
    assert forced_kappa_multiplicity == 1

    # Remove exactly n-d copies of lambda0=-5. The remaining d eigenvalues
    # have these first two moments, whether or not phi later contains more -5s.
    residual_sum = -(n - d) * lam0
    residual_sumsq = n * (n - 1) - (n - d) * lam0 * lam0
    assert residual_sum == 205
    assert residual_sumsq == 2397

    # Remove one forced kappa=11 root and shift the other 17 roots by -11.
    m = d - 1
    shifted_sum = residual_sum - kappa - m * kappa
    shifted_sumsq = (
        residual_sumsq
        - kappa * kappa
        - 2 * kappa * (residual_sum - kappa)
        + m * kappa * kappa
    )
    assert shifted_sum == 7
    assert shifted_sumsq == 65

    # Newton identity: e2=(p1^2-p2)/2, so the degree-17 polynomial is
    # y^17 - 7 y^16 - 8 y^15 + ...
    e2 = (shifted_sum * shifted_sum - shifted_sumsq) // 2
    assert e2 == -8

    # Uniform terminal-product gate. Weak type 2 makes g(0) divisible by
    # 2^(17-1)=2^16. AM-GM on y_i^2 gives
    # |g(0)|^2 <= (65/17)^17 < 2^34, hence |g(0)| < 2^17.
    # Therefore g(0) can only be 0 or +/-2^16.
    assert 65**17 < (1 << 34) * 17**17
    terminal_step = 1 << 16
    terminal_bound = 1 << 17
    terminal_candidates = (-terminal_step, 0, terminal_step)
    assert terminal_candidates == (-65536, 0, 65536)
    assert all(abs(v) < terminal_bound for v in terminal_candidates)

    # Regression against the accepted eta=17/simple-11 spectrum:
    # phi(x)=(x-9)^6 (x-10) (x-13)^10
    phi = mul(mul(ppow([-9, 1], 6), [-10, 1]), ppow([-13, 1], 10))
    g = shift_plus(phi, kappa)  # g(y)=phi(y+11)
    expected_g = mul(mul(ppow([2, 1], 6), [1, 1]), ppow([-2, 1], 10))
    assert g == expected_g
    assert list(reversed(g))[:3] == [1, -7, -8]
    assert weak_type2(g)
    assert g[0] == 65536
    assert g[0] in terminal_candidates

    eta17_y = [-2] * 6 + [-1] + [2] * 10
    assert sum(eta17_y) == shifted_sum
    assert sum(v * v for v in eta17_y) == shifted_sumsq

    # Negative controls: the top coefficient contract and weak-type-2 gate
    # both detect simple perturbations.
    bad = g[:]
    bad[-2] += 1
    assert list(reversed(bad))[:3] != [1, -7, -8]
    bad2 = g[:]
    bad2[0] += 1
    assert not weak_type2(bad2)

    print("TASK-EQUIANGULAR-R18-001 structural reduction")
    print("kappa=11 R=65 theta=18 forced multiplicity of 11=1")
    print("g(y): degree=17; sum roots=7; sumsq roots=65; top=(1,-7,-8)")
    print("terminal product g(0) in {-65536,0,65536}")
    print("eta17 regression: weak-type2 PASS")
    print("structural reduction verifier: PASS")


if __name__ == "__main__":
    main()
