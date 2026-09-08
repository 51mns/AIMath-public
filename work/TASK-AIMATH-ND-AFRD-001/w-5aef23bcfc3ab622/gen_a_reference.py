#!/usr/bin/env python3
# SPDX-FileCopyrightText: 2026 AIMath contributors
# SPDX-License-Identifier: Apache-2.0
"""Reference GEN-A for AFRD E0.

This file defines the visible/public generator family. Hidden experiments reuse
this implementation with evaluator-side seed strings that are not committed
until post-evaluation reveal. It never generates or stores a factorization
candidate representation X(N).
"""
from __future__ import annotations

import hashlib
import random
from dataclasses import dataclass

MR_BASES = (2, 3, 5, 7, 11, 13, 17)
SMALL_PRIMES = (2, 3, 5, 7, 11, 13, 17, 19, 23, 29, 31, 37)


def is_prime(n: int) -> bool:
    if n < 2:
        return False
    for p in SMALL_PRIMES:
        if n == p:
            return True
        if n % p == 0:
            return False
    d = n - 1
    s = 0
    while d % 2 == 0:
        s += 1
        d //= 2
    for a in MR_BASES:
        if a >= n:
            continue
        x = pow(a, d, n)
        if x in (1, n - 1):
            continue
        for _ in range(s - 1):
            x = (x * x) % n
            if x == n - 1:
                break
        else:
            return False
    return True


def rng_from_seed_string(seed: str) -> random.Random:
    digest = hashlib.sha256(seed.encode("utf-8")).digest()
    return random.Random(int.from_bytes(digest, "big"))


def random_prime(bits: int, rng: random.Random, *, residue_mod: int | None = None,
                 residue: int | None = None) -> int:
    if not 2 <= bits <= 36:
        raise ValueError("AFRD E0 GEN-A supports factor bit lengths 2..36")
    lo = 1 << (bits - 1)
    hi = 1 << bits
    while True:
        n = rng.randrange(lo, hi) | 1
        if residue_mod is not None:
            if residue is None:
                raise ValueError("residue required with residue_mod")
            delta = (residue - n) % residue_mod
            n += delta
            if n >= hi:
                continue
            if n % 2 == 0:
                n += residue_mod
                if n >= hi:
                    continue
        if is_prime(n):
            return n


@dataclass(frozen=True)
class Semiprime:
    N: int
    p: int
    q: int


def semiprime(bits_p: int, bits_q: int, rng: random.Random) -> Semiprime:
    while True:
        p = random_prime(bits_p, rng)
        q = random_prime(bits_q, rng)
        if p == q:
            continue
        p, q = sorted((p, q))
        return Semiprime(p * q, p, q)


def demo() -> None:
    rng = rng_from_seed_string("AFRD-E0-v1-GEN-A-demo")
    rows = [semiprime(16, 16, rng) for _ in range(4)]
    assert len({r.N for r in rows}) == len(rows)
    for r in rows:
        assert r.p < r.q and r.N == r.p * r.q and is_prime(r.p) and is_prime(r.q)
    print("PASS: GEN-A deterministic demo")
    for r in rows:
        print(r.N, r.p, r.q)


if __name__ == "__main__":
    demo()
