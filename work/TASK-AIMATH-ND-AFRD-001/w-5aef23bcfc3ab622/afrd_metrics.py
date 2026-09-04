#!/usr/bin/env python3
# SPDX-FileCopyrightText: 2026 AIMath contributors
# SPDX-License-Identifier: Apache-2.0
from __future__ import annotations

from fractions import Fraction
from math import comb, isqrt, log2


def odd_count(lo: int, hi: int) -> int:
    """Number of odd integers in inclusive [lo, hi]."""
    if hi < lo:
        return 0
    return (hi + 1) // 2 - lo // 2


def canonicalise_intervals(N: int, intervals: list[tuple[int, int]]) -> list[tuple[int, int]]:
    if len(intervals) > 8:
        raise ValueError("at most 8 intervals")
    top = isqrt(N)
    out: list[tuple[int, int]] = []
    for a, b in sorted(intervals):
        if a > b or a < 3 or b > top:
            raise ValueError("interval outside canonical factor search range")
        if out and a <= out[-1][1] + 1:
            raise ValueError("intervals must be disjoint and non-adjacent")
        out.append((a, b))
    return out


def localisation_score(N: int, p: int, intervals: list[tuple[int, int]]) -> tuple[bool, int, int, float]:
    intervals = canonicalise_intervals(N, intervals)
    M = odd_count(3, isqrt(N))
    W = sum(odd_count(a, b) for a, b in intervals)
    covered = any(a <= p <= b for a, b in intervals)
    bits_saved = log2(M / max(1, W))
    return covered, M, W, bits_saved


def exact_two_sided_sign_p(w: int, l: int) -> Fraction:
    """Exact two-sided p-value for discordant paired binary outcomes.

    Under H0, candidate-only and baseline-only wins are equiprobable. For a
    symmetric Binomial(n, 1/2), the two-sided p-value is twice the lower tail
    through min(w,l), capped at 1.
    """
    if min(w, l) < 0:
        raise ValueError("w,l must be nonnegative")
    n = w + l
    if n == 0:
        return Fraction(1, 1)
    k = min(w, l)
    tail = Fraction(sum(comb(n, i) for i in range(k + 1)), 2**n)
    return min(Fraction(1, 1), 2 * tail)


def paired_gate(w: int, l: int, total_n: int, *, primary: bool) -> tuple[bool, Fraction]:
    if total_n <= 0 or w + l > total_n:
        raise ValueError("invalid paired counts")
    p = exact_two_sided_sign_p(w, l)
    if primary:
        return ((w - l) * 20 >= total_n and p <= Fraction(1, 100)), p
    return (w > l and p <= Fraction(1, 20)), p


def self_test() -> None:
    # Full interval has zero saved bits.
    N = 77  # p=7, q=11; floor(sqrt(N))=8; odds are 3,5,7 => M=W=3.
    covered, M, W, bits = localisation_score(N, 7, [(3, 8)])
    assert covered and M == 3 and W == 3 and bits == 0.0
    # One-point interval can localise p and saves log2(3) bits in this toy case.
    covered, M, W, bits = localisation_score(N, 7, [(7, 7)])
    assert covered and W == 1 and abs(bits - log2(3)) < 1e-15
    # Exact p-value is rational and gate has no floating statistical boundary.
    p = exact_two_sided_sign_p(20, 0)
    assert p == Fraction(1, 2**19)
    ok, _ = paired_gate(100, 20, 1000, primary=True)
    assert ok
    no, _ = paired_gate(50, 20, 1000, primary=True)
    assert not no  # only 3% net wins; below the frozen 5% floor.
    print("PASS: AFRD metric reference tests")


if __name__ == "__main__":
    self_test()
