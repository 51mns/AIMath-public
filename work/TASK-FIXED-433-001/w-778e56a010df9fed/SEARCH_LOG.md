<!-- SPDX-FileCopyrightText: 2026 AIMath contributors -->
<!-- SPDX-License-Identifier: Apache-2.0 -->

# Bounded search log

## Contract

- Task: `TASK-FIXED-433-001`
- Worker: `w-778e56a010df9fed`
- Exact base: `279ba9fa98befe3aee37bfd1a98e4f688d333bd4`
- Search date: 2026-09-04
- Focus: exceptional-bundle / Chern-slope / modular-root literature, with the candidate-specific factor-5 search performed only after the geometric placement was frozen.
- Stop rule: stop after primary full-text placement of the exceptional-slope correspondence and a bounded exact/near-exact query family for the residual factor-5 shift; do not expand into an unbounded novelty search.

## Interfaces

- arXiv abstract and primary PDF full text
- Numdam metadata and primary scanned PDF
- general web search for exact/near-exact formula placement
- GitHub public canonical AIMath files for the frozen target identity

PDF visual checks were attempted/performed for the load-bearing Drézet--Le Potier and Veselov sources in addition to indexed text extraction.

## Source discovery queries

Representative discovery queries:

1. `"Markov fractions and the slopes of the exceptional bundles" Veselov arXiv 2501.06779`
2. `"Fibrés stables et fibrés exceptionnels sur P2" Drezet Le Potier 1985 Numdam`
3. `"Unfocused notes on the Markoff equation and T-Singularities" Perling arxiv`
4. `Rudakov Markov numbers exceptional bundles P2 1989`
5. `Markoff weights first Chern classes exceptional bundles Rudakov`

## Candidate-specific factor-5 queries

After freezing

\[
U/M=\mu(E^\vee\otimes O(1))-1/5,
\]

the following exact/near-exact query families were run in multiple punctuation/spacing variants:

1. `"4/5 - p/q" Markov`
2. `"4/5" "Markov fraction"`
3. `"5p" "Markov fraction" M`
4. `"M/5" "Markov fraction"`
5. `"r-M/5" Markov`
6. `"r - M/5" Markov`
7. `"p+M/5" Markov fraction`
8. `"rank/5" "exceptional bundle" Markov`
9. `"c1" "r/5" exceptional bundle Markov`
10. `"1/5" "exceptional slope" Markov`
11. `"1/5" Markov exceptional bundle`
12. `"mod 5" Markov fraction modular root`

## Primary-source read points

### Drézet--Le Potier 1985

URL: https://www.numdam.org/article/ASENS_1985_4_18_2_193_0.pdf

Checked:

- printed p.194: slope `mu(E)=c1/r`; exceptional bundle/rank-denominator normalization;
- printed p.195: dyadic `epsilon` construction;
- printed p.195: `epsilon(-rho)=-epsilon(rho)` and `epsilon(rho+n)=epsilon(rho)+n` for integer `n`;
- printed p.195, Theorem A: image of `epsilon` equals the exceptional slopes.

### Veselov 2025

URL: https://arxiv.org/pdf/2501.06779

Checked:

- Section 2, eq. (5): all Markov fractions are integer-affine translates/reflections of the reduced set;
- Section 3: slope definition `mu(E)=c1/r`;
- Theorem 3.1: exceptional slopes coincide with all Markov fractions;
- immediately after Theorem 3.1: invariance under tensor by `O(n)` and dual, hence `Aff_1(Z)`;
- eqs. (14)--(15): Drézet--Le Potier recursion identified with the Springborn mediant.

### Perling 2022

URL: https://arxiv.org/pdf/2210.12982

Checked:

- Introduction: `r_g^2 ≡ -1 (mod g)`-type Frobenius roots and exceptional-slope connection;
- Section 3.1: exact definitions of weights `r_e,r_g,r_f` and square-root-of-`-1` congruences;
- remark immediately before Lemma 3.1: explicit attribution that Rudakov identifies these weights with first Chern classes and their ratios with exceptional slopes.

## Result of bounded exact-match search

Within this envelope, no source-local statement was found that is explicitly equivalent to any of

- `U_k = r_k - M_k/5`,
- `5 p_k + 5 U_k = 4 M_k`,
- `U_k/M_k = 4/5 - p_k/M_k`,
- `R_5(x)=4/5-x`

for the fixed-433 AIMath objects.

This statement records only the bounded search result.  It is not evidence of global absence and is not a publication-novelty conclusion.

## Access / uncertainty log

- Drézet--Le Potier: primary PDF and machine-readable indexed text available; load-bearing pages inspected.
- Veselov: primary arXiv v2 PDF and indexed text available; load-bearing theorem and symmetry paragraph inspected.
- Perling: primary arXiv v1 PDF and indexed text available; load-bearing weight/Chern attribution inspected.
- Rudakov 1989: bibliographic record/abstract was locatable, but this session did not rely on an unverified exact Rudakov page; the specific weight/Chern statement is attributed through Perling's explicit source-local remark.
- Search-engine non-hits were retained as bounded unresolved evidence only.

## Stop

The frozen objective was met by a source-backed geometric placement plus a bounded negative exact-formula search.  Continuing with more generic Markov/exceptional-bundle queries would enlarge the search volume without a sharper mechanism, so the lane stops here.
