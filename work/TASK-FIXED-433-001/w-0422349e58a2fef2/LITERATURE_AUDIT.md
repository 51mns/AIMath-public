<!--
SPDX-FileCopyrightText: 2026 AIMath contributors
SPDX-License-Identifier: CC-BY-4.0
-->

# TASK-FIXED-433-001 — bounded primary-source placement

- Worker: `w-0422349e58a2fef2`
- Public base: `71547cb5d757afaace54b558f2d0a4a49fad5656`
- Search date: 2026-09-02
- Outcome: **BOUNDED_UNRESOLVED_WITH_CLOSE_PRECEDENT**
- Novelty: **NOT_ESTABLISHED**

## Frozen question

The public AIMath claim proves, for every `k >= 0`,

\[
\frac{U_k}{M_k}=\frac45-\mu\!\left(\frac{9k+8}{15k+13}\right),
\]

or, writing the Markov fraction as `p_k/M_k`,

\[
5p_k+5U_k=4M_k.
\]

The literature task is narrower than proving that identity again: determine whether the exact fixed affine map

\[
R_5(z)=\frac45-z
\]

or the equivalent fixed-433 representative relation is explicit in prior primary literature, and record the closest source-backed placement if an exact match is not located.

## Frozen search envelope

The bounded audit inspected the following primary-source neighbourhood and exact-expression variants (`4/5-x`, `4/5`, `5p`, `4M-5U`, the fixed Farey ray, `433`, reflection/affine symmetry, root representatives):

1. J. O. Button, *Markoff Numbers, Principal Ideals and Continued Fraction Expansions*, Journal of Number Theory 87 (2001), 77–95, DOI `10.1006/jnth.2000.2578`. Publisher-version PDF is available from Oxford ORA: `https://ora.ox.ac.uk/objects/uuid%3Afc6f3446-4389-41e2-9cb4-d75505137821`.
2. Enrico Bombieri, *Continued fractions and the Markoff tree*, Expositiones Mathematicae 25 (2007), 187–213, DOI `10.1016/j.exmath.2006.10.002`.
3. Boris Springborn, *The worst approximable rational numbers*, Journal of Number Theory 263 (2024), 153–205, final arXiv `2209.15542v3`.
4. A. P. Veselov, *Markov fractions and Cohn matrices*, arXiv `2604.17401v1` (2026).

This is not claimed to be an exhaustive historical-priority search. Search failure is not novelty evidence.

## Source placement

### Springborn 2024

Section 2.2 explicitly describes the Markov-fraction subtree in `[1/2,1]` as the reflection of the subtree in `[0,1/2]`, replacing each Markov fraction `x` by `1-x`; integer translates `x+n` generate the trees in other integer intervals. Thus the source supplies the natural integer-affine reflection/translation framework for Markov fractions.

No source-canonical `x -> 4/5-x` symmetry was located in the bounded inspection. In particular, the fixed AIMath map is not one of the displayed `x -> 1-x` / integer-translation symmetries.

### Veselov 2026

Proposition 2.1, equations (6)–(9), gives the oriented determinant identities for local Markov-fraction triples. Equations (12)–(15) and Theorem 3.1 identify Springborn's Markov fraction with the index of the corresponding Cohn matrix; equation (14) is the bridge `mu(t)=I_t(0)` used by the public AIMath proof.

The paper also places Markov fractions in a fundamental domain for the natural integer-affine action `x -> ±x+m`. The bounded inspection located no `4/5-x` map and no statement identifying the fixed-433 `U_k/M_k` family with the reflected Markov-fraction ray.

### Button 2001 — closest located predecessor

Button's page 85 construction starts from a Markoff triple `(a,b,c)`, lets `alpha` be the inverse of `a` modulo `c`, and chooses a quadratic-order root representative

\[
x \equiv 3c-2b\alpha \pmod{2c}.
\]

The subsequent symmetric comparison (around p. 87 in the publisher pagination) gives the corresponding swapped representatives with the exact constant-sum relation

\[
x+x'=4c
\]

in the nontrivial range under discussion.

This is a genuinely close predecessor to the *shape* of the AIMath relation: both use a reflection with constant `4` after choosing representatives. However it is not, on the inspected definitions, the same statement. Button's `x,x'` are quadratic-order root representatives attached to a Markoff form/ideal construction; AIMath's `p_k,U_k` are respectively a Markov-fraction numerator and the fixed-433 continuant numerator.

Mechanically dividing Button's relation by `5c` would produce a formal `4/5` constant, but that rescaling is not the source's canonical normalization and does not identify Button's `x` with `5p_k` or `5U_k`.

## Exact finite diagnostic of the possible Button identification

`button_overlap_check.py` evaluates the first three fixed-433 cases using exact integers. For each case it:

- reconstructs `M_k`, `U_k`, the preceding ray value `Y_k`, and the source Cohn numerator `p_k`;
- verifies `(433,Y_k,M_k)` is a Markoff triple;
- constructs Button's representative for `(433,Y_k,M_k)` and for the swapped `(Y_k,433,M_k)`;
- verifies Button's pair sums to `4M_k`;
- verifies AIMath's scaled pair `(5p_k,5U_k)` also sums to `4M_k`;
- checks that the two unordered pairs are different in each tested case.

| k | M | Button pair `(x,x')` | AIMath scaled pair `(5p,5U)` | equal? |
|---:|---:|---|---|---|
| 0 | 48,928,105 | (106,330,881, 89,381,539) | (101,133,585, 94,578,835) | no |
| 1 | 107,246,981,290,506,205 | (233,069,848,202,991,781, 195,918,076,959,033,039) | (221,677,739,171,317,085, 207,310,185,990,707,735) | no |
| 2 | 235,077,875,914,593,228,457,734,305 | (510,872,792,837,723,470,826,982,681, 429,438,710,820,649,443,003,954,539) | (485,902,087,265,140,536,365,550,585, 454,409,416,393,232,377,465,386,635) | no |

These three rows are **finite diagnostics only**. They are not used to prove an all-`k` non-identification. The literature distinction is primarily definitional: the sources attach the two pairs to different mathematical objects.

## Bombieri 2007

Bombieri remains useful classical background for the Markoff tree, continued fractions and Cohn-matrix structure. The bounded exact-expression/source-neighbourhood search did not locate the fixed `R_5` transformation or an equivalent fixed-433 representative identity there.

## Decision

The bounded primary-source audit does **not** support either of the following stronger statements:

- “the AIMath identity is already explicit in the inspected literature”; or
- “the AIMath identity is publication-new”.

The safe placement is:

> Button 2001 contains a close prior constant-`4` reflection relation for a distinct pair of Markoff-form root representatives. Springborn 2024 and Veselov 2026 supply the canonical Markov-fraction tree, integer-affine symmetry, determinant and Cohn-index framework. Within this frozen source/query envelope, the exact fixed map `U_k/M_k = 4/5 - mu((9k+8)/(15k+13))` was not located.

Accordingly this Task closes only as **BOUNDED_UNRESOLVED_WITH_CLOSE_PRECEDENT**. Publication novelty remains **NOT_ESTABLISHED**, and no canonical claim level is changed by this worker result.

## Reproduction

From a repository checkout containing this worker path:

```bash
python3 work/TASK-FIXED-433-001/w-0422349e58a2fef2/button_overlap_check.py
```

The expected top-level result is `BUTTON_ROOT_PAIR_DIFFERS_FROM_AIMATH_SCALED_PAIR_IN_TESTED_CASES`, with `pairs_equal: false` for `k=0,1,2`.
