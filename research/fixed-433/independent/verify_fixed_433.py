#!/usr/bin/env python3
"""Independent exact verifier for the fixed-433 first-three cases.

This file is intentionally self-contained. It does not import the candidate
generator, a proof helper, a certificate, or generated expected output.
"""

from __future__ import annotations

PREFIX = (2, 1, 1, 2, 2, 1, 1, 2, 4, 1, 1, 3, 3, 1, 1, 4, 2, 1, 1, 2, 2, 1, 1, 2)
REPEAT = (2, 1, 1, 1, 1, 2, 2, 1, 1, 2, 2, 1, 1, 2, 4, 1, 1, 3, 3, 1, 1, 4, 2, 1, 1, 2, 2, 1, 1, 2)

def multiply(p, q):
    a, b, c, d = p
    e, f, g, h = q
    return a * e + b * g, a * f + b * h, c * e + d * g, c * f + d * h

def word_matrix(word):
    value = (1, 0, 0, 1)
    for digit in word:
        value = multiply(value, (digit, 1, 1, 0))
    return value

def euclid_digits(top, bottom):
    answer = []
    while bottom:
        q, r = divmod(top, bottom)
        answer.append(q)
        top, bottom = bottom, r
    return tuple(answer)

def advance_ray(to_index):
    result = [29, 37_666]
    for _ in range(2, to_index + 1):
        result.append(1299 * result[-1] - result[-2])
    return result

def verify_case(index, ray):
    digits = PREFIX + REPEAT * index
    a, b, c, d = word_matrix(digits)
    y = ray[1 + 3 * index]
    m = ray[2 + 3 * index]
    root = 433 * pow(y, -1, m) % m
    pair = tuple(sorted((root, (-root) % m)))
    n = m // 5
    checks = {
        "ray_numerator_match": a == m,
        "matrix_symmetric": b == c,
        "matrix_determinant_one": a * d - b * c == 1,
        "canonical_cf_match": euclid_digits(m, b) == digits and digits[-1] > 1,
        "palindrome": digits == tuple(reversed(digits)),
        "digits_bounded_with_four": set(digits) <= {1, 2, 3, 4} and 4 in digits,
        "markov_identity": 433**2 + y**2 + m**2 == 3 * 433 * y * m,
        "candidate_sqrt_minus_one": (b * b + 1) % m == 0,
        "canonical_roots_sqrt_minus_one": all((r * r + 1) % m == 0 for r in pair),
        "different_from_both_canonical_roots": b not in pair,
        "exclude_plus_root_mod_5": b * y % 5 != 433 % 5,
        "exclude_minus_root_mod_M_over_5": b * y % n == 433 % n and 433 % n != (-433) % n,
    }
    if not all(checks.values()):
        raise AssertionError({key: value for key, value in checks.items() if not value})
    return {
        "k": index,
        "markov_triple": [433, y, m],
        "M": m,
        "u": b,
        "word": list(digits),
        "energy": max(digits),
        "continuant_matrix": [[a, b], [c, d]],
        "canonical_root_pair": list(pair),
        "checks": checks,
    }

def verify_fixed_identities():
    block = word_matrix(REPEAT)
    initial = word_matrix(PREFIX)
    period = PREFIX + REPEAT[:6]
    next_matrix = multiply(initial, block)
    ray = advance_ray(5)
    assertions = {
        "trace_cube_identity": block[0] + block[3] == 1299**3 - 3 * 1299,
        "block_determinant_one": block[0] * block[3] - block[1] * block[2] == 1,
        "period_reflection": all(period[i] == period[(23 - i) % 30] for i in range(30)),
        "repeat_is_rotation": REPEAT == period[24:] + period[:24],
        "first_two_numerators": (initial[0], next_matrix[0]) == (ray[2], ray[5]),
        "linear_identity_k0": 2165 * ray[1] == 362421 * ray[2] - 937445 * initial[1],
        "linear_identity_k1": 2165 * ray[4] == 362421 * ray[5] - 937445 * next_matrix[1],
        "mod_25_bases": (ray[2] % 25, ray[5] % 25, ray[1] % 25, ray[4] % 25) == (5, 5, 16, 16),
        "mod_433_recurrence": (1299**3 - 3 * 1299) % 433 == 0,
        "mod_5_matrix_action": (initial[0] % 5, initial[1] % 5, block[0] % 5, block[1] % 5, block[2] % 5, block[3] % 5) == (0, 2, 1, 2, 0, 1),
    }
    if not all(assertions.values()):
        raise AssertionError({key: value for key, value in assertions.items() if not value})
    return assertions

def build_result():
    ray = advance_ray(8)
    return {
        "schema_version": 1,
        "claim_id": "C-ROOT-433",
        "independence": "no candidate implementation or generated expected output imported",
        "fixed_identity_checks": verify_fixed_identities(),
        "cases": [verify_case(k, ray) for k in range(3)],
    }
