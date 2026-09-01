#!/usr/bin/env python3
# SPDX-FileCopyrightText: 2026 Shoma Nakabayashi
# SPDX-License-Identifier: Apache-2.0
"""Exact verifier for TASK-OPEN-MATH-DISCOVERY-001 threshold-graph result.

No third-party dependencies.  A threshold building word begins with 0.
For each subsequent bit:
  0 = add an isolated vertex
  1 = add a dominating vertex
"""

from __future__ import annotations

from itertools import product
from math import comb


def trim(coeffs: list[int]) -> list[int]:
    out = list(coeffs)
    while len(out) > 1 and out[-1] == 0:
        out.pop()
    return out


def poly_from_word(word: str) -> list[int]:
    if not word or word[0] != "0" or any(ch not in "01" for ch in word):
        raise ValueError("threshold word must be a nonempty binary string starting with 0")
    # First vertex: I(K1;x)=1+x.
    coeffs = [1, 1]
    for bit in word[1:]:
        if bit == "0":
            # Add isolated vertex: multiply by (1+x).
            nxt = [0] * (len(coeffs) + 1)
            for i, a in enumerate(coeffs):
                nxt[i] += a
                nxt[i + 1] += a
            coeffs = nxt
        else:
            # Add dominating vertex: old independent sets plus the new singleton.
            if len(coeffs) < 2:
                coeffs += [0] * (2 - len(coeffs))
            coeffs = list(coeffs)
            coeffs[1] += 1
    return trim(coeffs)


def adjacency_from_word(word: str) -> list[int]:
    """Independent implementation of the threshold construction."""
    n = len(word)
    if not word or word[0] != "0":
        raise ValueError("threshold word must begin with 0")
    adj = [0] * n
    for v, bit in enumerate(word):
        if v == 0:
            continue
        if bit == "1":
            # New dominating vertex is adjacent to every earlier vertex.
            for u in range(v):
                adj[u] |= 1 << v
                adj[v] |= 1 << u
        elif bit != "0":
            raise ValueError("nonbinary threshold word")
    return adj


def poly_by_subset_enumeration(word: str) -> list[int]:
    """Brute-force independent-set counter, separate from the polynomial recurrence."""
    adj = adjacency_from_word(word)
    n = len(adj)
    coeffs = [0] * (n + 1)
    for subset in range(1 << n):
        ok = True
        for v in range(n):
            if (subset >> v) & 1 and (adj[v] & subset):
                ok = False
                break
        if ok:
            coeffs[subset.bit_count()] += 1
    return trim(coeffs)


def log_concavity_failures(coeffs: list[int]) -> list[tuple[int, int, int]]:
    """Return (index, lhs, rhs) for strict failures a_i^2 < a_{i-1}a_{i+1}."""
    failures = []
    for i in range(1, len(coeffs) - 1):
        lhs = coeffs[i] * coeffs[i]
        rhs = coeffs[i - 1] * coeffs[i + 1]
        if lhs < rhs:
            failures.append((i, lhs, rhs))
    return failures


def threshold_words(n: int):
    if n < 1:
        return
    for tail in product("01", repeat=n - 1):
        yield "0" + "".join(tail)


def two_block_formula(n: int, k: int) -> list[int]:
    """I(k K1 + K_{n-k};x) for Zykov join '+' and 1 <= k <= n."""
    if not (1 <= k <= n):
        raise ValueError("need 1 <= k <= n")
    coeffs = [1, n]
    coeffs.extend(comb(k, j) for j in range(2, k + 1))
    return trim(coeffs)


def two_block_log_concave_criterion(n: int, k: int) -> bool:
    """Closed criterion derived from the only non-binomial minor, at index 2."""
    if k <= 2:
        return True
    # C(k,2)^2 >= n*C(k,3), kept in integer arithmetic.
    return comb(k, 2) ** 2 >= n * comb(k, 3)


def main() -> None:
    # Independent implementation check for every threshold building word through n=10.
    cross_checked = 0
    for n in range(1, 11):
        for word in threshold_words(n):
            a = poly_from_word(word)
            b = poly_by_subset_enumeration(word)
            assert a == b, (word, a, b)
            cross_checked += 1

    # Exact exhaustive minimal-order scan.
    scan = []
    first_bad_n = None
    first_bad = []
    for n in range(1, 11):
        bad = []
        for word in threshold_words(n):
            coeffs = poly_from_word(word)
            failures = log_concavity_failures(coeffs)
            if failures:
                bad.append((word, coeffs, failures))
        scan.append((n, 2 ** (n - 1), len(bad)))
        if bad and first_bad_n is None:
            first_bad_n = n
            first_bad = bad

    assert first_bad_n == 10
    assert len(first_bad) == 2
    expected = {
        "0001111111": [1, 10, 3, 1],
        "0000111111": [1, 10, 6, 4, 1],
    }
    assert {w: c for w, c, _ in first_bad} == expected

    # Closed two-block formula and criterion: exact finite stress range.
    family_checks = 0
    for n in range(1, 31):
        for k in range(1, n + 1):
            word = "0" * k + "1" * (n - k)
            coeffs = poly_from_word(word)
            assert coeffs == two_block_formula(n, k), (n, k, coeffs)
            assert (not log_concavity_failures(coeffs)) == two_block_log_concave_criterion(n, k)
            family_checks += 1

    # Post-freeze held-out witnesses, outside the exploratory n<=18 diagnostics.
    held_out = {}
    for n in (19, 20):
        word = "000" + "1" * (n - 3)
        coeffs = poly_by_subset_enumeration(word)
        assert coeffs == [1, n, 3, 1]
        failures = log_concavity_failures(coeffs)
        assert failures == [(2, 9, n)]
        held_out[n] = {"word": word, "coeffs": coeffs, "failure": failures[0]}

    print("TASK-OPEN-MATH-DISCOVERY-001")
    print(f"cross_checked_words_through_n10={cross_checked}")
    for n, total, bad in scan:
        print(f"n={n}: threshold_words={total}, non_log_concave={bad}")
    print("first_bad_n=10")
    for word, coeffs, failures in first_bad:
        print(f"first_bad word={word} coeffs={coeffs} failures={failures}")
    print(f"two_block_formula_and_criterion_checks={family_checks}")
    for n in sorted(held_out):
        print(f"held_out n={n}: {held_out[n]}")
    print("PASS")


if __name__ == "__main__":
    main()
