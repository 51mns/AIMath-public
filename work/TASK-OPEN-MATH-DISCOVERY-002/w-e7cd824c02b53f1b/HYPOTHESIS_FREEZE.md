<!-- SPDX-FileCopyrightText: 2026 AIMath contributors -->
<!-- SPDX-License-Identifier: CC-BY-4.0 -->

# Hypothesis freeze — continuant/path transfer

Task: `TASK-OPEN-MATH-DISCOVERY-002`  
Worker: `w-e7cd824c02b53f1b`  
Exact public base: `279ba9fa98befe3aee37bfd1a98e4f688d333bd4`

## Scope frozen before held-out evaluation

We test an explicit three-domain correspondence:

1. finite simple continued fractions and their continuants;
2. weighted monomer-dimer matchings of a path graph;
3. determinants of a signed tridiagonal matrix.

For a finite sequence `a=(a_1,...,a_n)` of positive integers, define

`K()=1`, `K(a_1)=a_1`, and

`K(a_1,...,a_n)=a_n K(a_1,...,a_{n-1}) + K(a_1,...,a_{n-2})`.

The frozen correspondence candidate is

`K(a_1,...,a_n) = Z(P_n;a_1,...,a_n) = det(T_n)`,

where `Z` is the sum over matchings of the path `P_n`, each unmatched vertex `i` contributes weight `a_i`, each matched edge contributes weight `1`, and `T_n` has diagonal `a_i`, superdiagonal `+1`, and subdiagonal `-1`.

For the finite continued fraction

`[a_1;...;a_n] = p/q`,

we use the candidate identification

`p=K(a_1,...,a_n)`, `q=K(a_2,...,a_n)`.

## Transfer lemma candidate

For `1 <= j <= n` (one-based indexing), changing only `a_j` to `a_j+t` should satisfy the exact cut formula

`Delta K = t K(a_1,...,a_{j-1}) K(a_{j+1},...,a_n)`.

For an interior partial quotient `2 <= j <= n-1`, this predicts the complete changed convergent without recomputing the whole continued fraction:

`p' = p + t K(a_1,...,a_{j-1}) K(a_{j+1},...,a_n)`,

`q' = q + t K(a_2,...,a_{j-1}) K(a_{j+1},...,a_n)`.

The intended structural explanation is that differentiating the path matching partition function with respect to the monomer weight at vertex `j` forces `j` to be unmatched, disconnecting the remaining matching problem into independent left and right paths.

## Held-out rule

No held-out values are recorded in this file.

Generate exactly 64 cases indexed `c=0,...,63`. For each case compute

`digest = SHA256("AIMath-transfer-heldout-v1:" + decimal(c)).digest()`.

Set

- `n = 5 + digest[0] mod 8` (so `5 <= n <= 12`),
- `a_i = 1 + digest[i] mod 9` for `i=1,...,n`,
- zero-based perturbation index `j0 = 1 + digest[16] mod (n-2)` (strictly interior),
- `t = 1 + digest[17] mod 7`.

A case passes only if all of the following agree exactly with integer/rational arithmetic:

1. direct continued-fraction recurrence before and after perturbation;
2. the frozen cut prediction for both numerator and denominator;
3. brute-force path-matching enumeration for the continuant values used in the comparison;
4. an independently coded exact determinant of the signed tridiagonal matrix.

No floating-point tolerance is allowed.

## Success / failure boundary

Success is an exact state-operation-invariant mapping with 64/64 held-out agreement and a mathematical derivation of the cut formula. This is not a novelty claim. After the mathematical freeze, literature may be inspected to decide whether the correspondence/lemma is known or near-known.

Any held-out mismatch falsifies the frozen transfer candidate as stated. A literature match remains a valid result if the transfer is useful but known.
