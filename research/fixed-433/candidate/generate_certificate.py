#!/usr/bin/env python3
"""Materialize the fixed-433 candidate using exact integer arithmetic.

This is the candidate implementation. The independent verifier deliberately
does not import this module or consume its generated JSON.
"""

from __future__ import annotations

import itertools
from math import isqrt

A = 1299
T = 2_191_930_002
C0 = [2, 1, 1, 2, 2, 1, 1, 2, 4, 1, 1, 3, 3, 1, 1, 4, 2, 1, 1, 2, 2, 1, 1, 2]
BLOCK = [2, 1, 1, 1, 1, 2, 2, 1, 1, 2, 2, 1, 1, 2, 4, 1, 1, 3, 3, 1, 1, 4, 2, 1, 1, 2, 2, 1, 1, 2]
KNOWN_FACTORS = {
    0: [5, 9_785_621],
    1: [5, 29, 45_497, 98_597, 164_881],
}

def matmul(left, right):
    return [
        [left[0][0] * right[0][0] + left[0][1] * right[1][0],
         left[0][0] * right[0][1] + left[0][1] * right[1][1]],
        [left[1][0] * right[0][0] + left[1][1] * right[1][0],
         left[1][0] * right[0][1] + left[1][1] * right[1][1]],
    ]

def continuant(word):
    result = [[1, 0], [0, 1]]
    for digit in word:
        result = matmul(result, [[digit, 1], [1, 0]])
    return result

def determinant(matrix):
    return matrix[0][0] * matrix[1][1] - matrix[0][1] * matrix[1][0]

def regular_cf(numerator, denominator):
    if not numerator > denominator > 0:
        raise ValueError("expected numerator > denominator > 0")
    digits = []
    while denominator:
        quotient, remainder = divmod(numerator, denominator)
        digits.append(quotient)
        numerator, denominator = denominator, remainder
    return digits

def markov_ray(last_index):
    values = [29, 37_666]
    while len(values) <= last_index:
        values.append(A * values[-1] - values[-2])
    return values

def is_prime_trial(number):
    if number < 2:
        return False
    if number % 2 == 0:
        return number == 2
    divisor = 3
    while divisor <= isqrt(number):
        if number % divisor == 0:
            return False
        divisor += 2
    return True

def crt(residues, moduli):
    modulus = 1
    for value in moduli:
        modulus *= value
    total = 0
    for residue, part in zip(residues, moduli, strict=True):
        other = modulus // part
        total += residue * other * pow(other, -1, part)
    return total % modulus

def roots_from_squarefree_factors(factors):
    local_roots = []
    for prime in factors:
        roots = [x for x in range(prime) if (x * x + 1) % prime == 0]
        if len(roots) != 2:
            raise AssertionError((prime, roots))
        local_roots.append(roots)
    return sorted(crt(list(choice), factors) for choice in itertools.product(*local_roots))

def case(k, ray):
    word = C0 + BLOCK * k
    matrix = continuant(word)
    markov_middle = ray[1 + 3 * k]
    markov_number = ray[2 + 3 * k]
    candidate_root = matrix[0][1]
    canonical_reference = (433 * pow(markov_middle, -1, markov_number)) % markov_number
    canonical_pair = sorted({canonical_reference, (-canonical_reference) % markov_number})
    n_part = markov_number // 5
    result = {
        "k": k,
        "markov_triple": [433, markov_middle, markov_number],
        "markov_identity_residual": 433**2 + markov_middle**2 + markov_number**2 - 3 * 433 * markov_middle * markov_number,
        "M": markov_number,
        "u": candidate_root,
        "word": word,
        "word_length": len(word),
        "canonical_finite_cf": regular_cf(markov_number, candidate_root),
        "energy": max(word),
        "palindrome": word == list(reversed(word)),
        "continuant_matrix": matrix,
        "determinant": determinant(matrix),
        "sqrt_minus_one_residual": (candidate_root * candidate_root + 1) % markov_number,
        "canonical_root_pair": canonical_pair,
        "canonical_roots_sqrt_residuals": [(root * root + 1) % markov_number for root in canonical_pair],
        "candidate_not_canonical": candidate_root not in canonical_pair,
        "noncanonical_witness": {
            "u_times_y_mod_5": candidate_root * markov_middle % 5,
            "canonical_times_y_mod_5": 433 % 5,
            "u_times_y_mod_M_over_5": candidate_root * markov_middle % n_part,
            "plus_433_mod_M_over_5": 433 % n_part,
            "minus_433_mod_M_over_5": (-433) % n_part,
        },
        "factorization": None,
        "all_roots_minus_one": None,
        "factorization_status": "not attempted: outside the bounded standard-library fixture",
    }
    if k in KNOWN_FACTORS:
        factors = KNOWN_FACTORS[k]
        if any(not is_prime_trial(factor) for factor in factors):
            raise AssertionError("fixture contains a composite factor")
        product = 1
        for factor in factors:
            product *= factor
        if product != markov_number:
            raise AssertionError("factorization fixture does not multiply to M")
        roots = roots_from_squarefree_factors(factors)
        if any((root * root + 1) % markov_number for root in roots):
            raise AssertionError("CRT root generation failed")
        result["factorization"] = factors
        result["all_roots_minus_one"] = roots
        result["factorization_status"] = "complete squarefree factorization verified by trial primality"
    return result

def universal_checks():
    period = C0 + BLOCK[:6]
    block_matrix = continuant(BLOCK)
    c0_matrix = continuant(C0)
    ray = markov_ray(5)
    m0, m1 = ray[2], ray[5]
    y0, y1 = ray[1], ray[4]
    u0 = c0_matrix[0][1]
    u1 = matmul(c0_matrix, block_matrix)[0][1]
    return {
        "A": A,
        "T": T,
        "trace_identity": T == A**3 - 3 * A,
        "period_length": len(period),
        "block_is_period_rotation": BLOCK == period[24:] + period[:24],
        "reflection_checks": [period[i] == period[(23 - i) % 30] for i in range(30)],
        "block_matrix": block_matrix,
        "block_determinant": determinant(block_matrix),
        "block_trace": block_matrix[0][0] + block_matrix[1][1],
        "c0_matrix": c0_matrix,
        "first_two_M_match": [c0_matrix[0][0] == m0, matmul(c0_matrix, block_matrix)[0][0] == m1],
        "linear_identity_base_residuals": [
            2165 * y0 - 362421 * m0 + 937445 * u0,
            2165 * y1 - 362421 * m1 + 937445 * u1,
        ],
        "modular_bases": {
            "M_mod_25": [m0 % 25, m1 % 25],
            "y_mod_25": [y0 % 25, y1 % 25],
            "M_mod_433": [m0 % 433, m1 % 433],
            "T_mod_433": T % 433,
            "top_row_C0_mod_5": [value % 5 for value in c0_matrix[0]],
            "block_matrix_mod_5": [[value % 5 for value in row] for row in block_matrix],
        },
    }

def build_certificate():
    ray = markov_ray(8)
    cases = [case(k, ray) for k in range(3)]
    if any(not entry["candidate_not_canonical"] for entry in cases):
        raise AssertionError("candidate root collided with canonical pair")
    return {
        "schema_version": 1,
        "claim_id": "C-ROOT-433",
        "scope": "exact first-three-case certificate plus finite checks of fixed identities used by PROOF.md",
        "historical_source_commit": "fe3a5612d91d7c4dc91471436538707a05401604",
        "universal_checks": universal_checks(),
        "cases": cases,
    }

def build_negative_controls():
    ray = markov_ray(5)
    original = C0
    changed = list(C0)
    changed[8] = 3
    changed_matrix = continuant(changed)
    original_matrix = continuant(original)
    terminal_one = original[:-1] + [original[-1] - 1, 1]
    naive_reference = (433 * pow(ray[1], -1, ray[2])) % ray[2]
    complementary_reference = (-naive_reference) % ray[2]
    controls = [
        {
            "name": "mutate_C0_digit_8_from_4_to_3",
            "observed": changed_matrix[0][0] != ray[2],
        },
        {
            "name": "shift_M_subsequence_by_one",
            "observed": original_matrix[0][0] != ray[3],
        },
        {
            "name": "complementary_root_bypasses_one_root_check",
            "observed": complementary_reference != naive_reference
            and complementary_reference in {naive_reference, complementary_reference},
        },
        {
            "name": "accept_terminal_one_expansion_as_canonical",
            "observed": continuant(terminal_one)[0][0] == original_matrix[0][0]
            and continuant(terminal_one)[1][0] == original_matrix[1][0]
            and terminal_one[-1] == 1
            and regular_cf(original_matrix[0][0], original_matrix[0][1]) != terminal_one,
        },
    ]
    return {
        "schema_version": 1,
        "controls": controls,
        "all_controls_rejected": all(item["observed"] for item in controls),
    }
