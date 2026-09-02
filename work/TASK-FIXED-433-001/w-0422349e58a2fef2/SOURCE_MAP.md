<!--
SPDX-FileCopyrightText: 2026 AIMath contributors
SPDX-License-Identifier: CC-BY-4.0
-->

# TASK-FIXED-433-001 — expanded prior-art source map

- Worker: `w-0422349e58a2fef2`
- Public base: `71547cb5d757afaace54b558f2d0a4a49fad5656`
- Search date: 2026-09-02
- Target: `R_5(x)=4/5-x`, equivalently `U_k/M_k = 4/5 - mu((9k+8)/(15k+13))`
- Novelty: **NOT_ESTABLISHED**
- Truth-layer effect: **NONE**

## Verdict vocabulary

- `SAME_OBJECT_NONMATCH_DISPLAYED`: the primary source treats the same Markov-fraction object, but the displayed canonical formula/action is not the AIMath fixed map.
- `NEAR_DIFFERENT_OBJECT`: a structurally related Markoff/Cohn/ideal object is present, but it is not the AIMath pair `(p_k/M_k,U_k/M_k)`.
- `FOUNDATIONAL_DIFFERENT_OBJECT`: classical background is source-relevant but lives at the level of forms, minima, triples, geodesics, or words rather than the fixed Markov-fraction representative identity.
- `ACCESS_LIMITED`: the primary item was identified, but this runtime did not expose enough page/equation text to adjudicate an exact formula.
- `PRIOR_LANE_ONLY`: retained for context but deliberately not re-audited in this continuation.

## Source-by-source map

| Priority | Primary source | Page / equation inspected | Exact mathematical object in source | Correspondence to AIMath object | Verdict |
|---:|---|---|---|---|---|
| 1 | A. Markoff, *Sur les formes quadratiques binaires indéfinies*, Math. Ann. 15 (1879), 381–406 | p.381 opening formulas | indefinite binary quadratic form `f=ax^2+2bxy+cy^2`, determinant/minimum problem | ancestral Markoff-form problem; neither Springborn Markov fraction `p/q` nor fixed numerator `U/M` is the displayed object | `FOUNDATIONAL_DIFFERENT_OBJECT` |
| 1 | J. W. S. Cassels, *An Introduction to Diophantine Approximation* (1957), Ch. II | contents locate Ch. II “The Markoff Chain” p.18, “A Diophantine equation” p.27, “The Markoff forms” p.31, “The Markoff chain for forms” p.39 | Markoff chain / Markoff forms | relevant classical normalization path, but the accessible primary preview did not expose a formula that can be compared exactly with `R_5`; no absence claim is made | `ACCESS_LIMITED` |
| 1 | H. Cohn, *Approach to Markoff's Minimal Forms Through Modular Functions*, Ann. Math. 61 (1955), 1–12 | bibliographic primary record; article body not exposed by the runtime | Markoff minimal forms via modular functions | predecessor framework to later Cohn matrix/word methods; exact numerator representative comparison not inspectable here | `ACCESS_LIMITED` |
| 1 | H. Cohn, *Representation of Markoff's Binary Quadratic Forms by Geodesics on a Perforated Torus*, Acta Arith. 18 (1971), 125–136 | primary article/PDF located; PDF page rendering/text extraction failed in this runtime | Markoff binary quadratic forms represented by geodesics | geometric representation of Markoff forms, not enough extracted source text to adjudicate the fixed fraction map | `ACCESS_LIMITED` |
| 1 | H. Cohn, *Markoff Forms and Primitive Words*, Math. Ann. 196 (1972), 8–22 | primary full-article record located; content endpoint timed out | Markoff forms / primitive free-group words | direct ancestor of the word/Cohn machinery used by Bombieri, but exact `4/5-x` comparison not inspectable from the retrieved primary text | `ACCESS_LIMITED` |
| 1 | A. Baragar, *On the Unicity Conjecture for Markoff Numbers*, Canad. Math. Bull. 39 (1996), 3–9 | pp.3–4: `x^2+y^2-3mxy=-m^2`, rewritten as `N_{K/Q}(x+omega y)=-m^2`, with discriminant `9m^2-4` | a fixed Markoff number `m`, Markoff-triple coordinates `(x,y,m)`, quadratic-order elements and pairs of principal ideals | very close to the ideal/representative side later used by Button, but it is not a Markov-fraction numerator/reflection statement | `NEAR_DIFFERENT_OBJECT` |
| 2 | E. Bombieri, *Continued fractions and the Markoff tree*, Expo. Math. 25 (2007), 187–213 | publisher abstract and article metadata; full article body was not exposed by the available endpoint | classical continued fractions plus Harvey Cohn's free-group word method for periods of Markov irrationals | strong framework relevance, but the available primary text is insufficient to adjudicate a fixed rational affine representative map | `ACCESS_LIMITED` |
| 3 | B. Springborn, *The worst approximable rational numbers*, JNT 263 (2024), 153–205 | p.155 eq. (4): `x -> +/-x+n`; p.157 eq. (5) tree rule; p.157 text: reflection `x -> 1-x`; Def. 2.1 eqs. (6)–(7) companions | **Markov fractions themselves** and companions | same base object as `mu(t)`. The displayed canonical symmetry group is integer affine; `x -> 4/5-x` is not an element of that displayed action. This does not prove no equivalent specialization occurs elsewhere | `SAME_OBJECT_NONMATCH_DISPLAYED` |
| 4 | A. Srinivasan, *Markoff numbers and ambiguous classes*, JTNB 21 (2009), 757–770 | p.759: discriminant `d=9c^2-4`, ambiguous classes; p.763 Def. 3.1/Lemma 3.3; p.769 discussion of Button criterion | ambiguous binary quadratic-form classes / ideals for fixed Markoff number `c` | explicitly downstream of Button but remains on forms/classes/uniqueness criteria, not the Markov-fraction numerator pair | `NEAR_DIFFERENT_OBJECT` |
| 5 | A. P. Veselov, *Markov fractions and Cohn matrices*, arXiv:2604.17401v1 | p.2 eqs. (3)–(4); p.3 Prop. 2.1 eqs. (6)–(8); p.4 eqs. (12)–(15), Thm. 3.1 | Markov fraction `mu(t)`, Cohn matrix `C_t(a)`, index `I_t(a)=a_t/m_t` | **direct object bridge**: eq. (14) `mu(t)=I_t(0)`. The same page states the fundamental-domain action `x -> +/-x+m`, `m in Z`. This supports the AIMath proof's Cohn-index identification but does not state `R_5` | `SAME_OBJECT_NONMATCH_DISPLAYED` |
| context | J. O. Button, *Markoff Numbers, Principal Ideals and Continued Fraction Expansions*, JNT 87 (2001), 77–95 | prior PR #27 material and parallel PR #26 only; no new Button-centered pass in this continuation | modular/quadratic-order representatives and principal ideals | prior lane found a close constant-`4` representative relation for a distinct pair; deliberately not used as the principal search target here | `PRIOR_LANE_ONLY` |

## Important same-object boundary

The strongest placement obtained in this continuation is not a classical `4/5` precedent. It is a **normalization boundary**:

1. Springborn works directly with the same Markov-fraction object `p/q` and states the natural affine invariance as
   `x -> +/-x+n`, `n in Z`.
2. Veselov identifies that same Markov fraction with a Cohn-matrix index by
   `mu(t)=I_t(0)` and again describes `[0,1/2]` as a fundamental domain for the integer-affine action.
3. AIMath's `R_5(x)=4/5-x` is rational-affine, but its translation part `4/5` is not integral. Therefore it is **not merely one of the displayed canonical integer-affine symmetries** in these sources.

This separates the fixed-433 identity from the standard symmetry framework, but it is not a publication-novelty proof. An algebraically equivalent identity could still occur in a source under a different object or normalization.

## Button-citing downstream boundary

Srinivasan 2009 explicitly cites Button 2001 as an existing Markoff-uniqueness criterion (p.769) and develops ambiguous-form/class-group criteria for discriminant `9c^2-4`. The exact mathematical object remains a binary quadratic form / ideal class. No identification with Springborn's later Markov-fraction numerator is made in the inspected source passages.

This downstream check therefore does not collapse Button's representatives onto the AIMath pair.

## Access gaps that remain genuine

The following are **not negative prior-art findings**:

- Cassels 1949/1957 body-level formula comparison was not available from the primary preview in this runtime.
- Cohn 1955 body text was not available from the primary endpoint.
- Cohn 1971 PDF was located, but the page renderer/text path failed.
- Cohn 1972 primary content endpoint timed out.
- Bombieri 2007 publisher page exposed metadata/abstract but not enough body text for equation-level adjudication.

These sources remain unresolved rather than “checked and absent”.

## Placement decision

Within the frozen bounded source envelope:

- no exact primary-source statement of `R_5(x)=4/5-x` or the fixed-433 representative identity was located;
- Markoff/Cassels/Cohn/Baragar place the result in a classical forms/triples/ideal/word lineage, mostly on different mathematical objects;
- Springborn and Veselov provide the closest **same-object** framework, but their displayed canonical affine action is the integer-affine group, not `R_5`;
- Button remains a close different-object predecessor from the earlier lane, not the basis of this continuation.

**Publication novelty remains `NOT_ESTABLISHED`. Search absence is not converted into novelty.**
