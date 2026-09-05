<!-- SPDX-FileCopyrightText: 2026 AIMath contributors -->
<!-- SPDX-License-Identifier: CC-BY-4.0 -->

# TASK-FIXED-433-001 — Button 2001 primary-source full-text placement audit

- Public base: `71547cb5d757afaace54b558f2d0a4a49fad5656`
- Worker: `w-f29341f2a4973b71`
- Task: `TASK-FIXED-433-001`
- Campaign: `CAM-FIXED-433`
- Role: **Button 2001 primary-source full-text placement audit only**
- Scope: Lemmas 5–8 / Theorem 7 neighbourhood and exact comparison with the accepted fixed affine identity
- Outcome: **BOUNDED UNRESOLVED COMPARISON**
- Novelty effect: **NONE / NOT ESTABLISHED**
- Claim-promotion effect: **NONE**

## Frozen AIMath target

The accepted public package `research/433-existing-theory-identification/PROOF.md` proves, with

\[
\mu\!\left(\frac{9k+8}{15k+13}\right)=\frac{p_k}{M_k},
\]

that

\[
\frac{U_k}{M_k}=\frac45-\mu\!\left(\frac{9k+8}{15k+13}\right),
\]

hence equivalently

\[
5p_k+5U_k=4M_k,
\]

and, for the fixed AIMath modular-root representative `r_k`,

\[
U_k=r_k-\frac{M_k}{5}.
\]

This audit asks only whether Button 2001 explicitly states, or source-locally yields an exact algebraic specialization of, those transformations. It does not re-prove or promote the AIMath identity.

## Primary source and access state

J. O. Button, *Markoff Numbers, Principal Ideals and Continued Fraction Expansions*, **Journal of Number Theory 87 (2001), 77–95**, DOI `10.1006/jnth.2000.2578`.

Oxford University Research Archive exposes the publisher/version-of-record PDF:

- record: `https://ora.ox.ac.uk/objects/uuid:fc6f3446-4389-41e2-9cb4-d75505137821`
- file: `1-s2.0-S0022314X00925782-main.pdf`

The primary PDF is searchable through the public web index and source-local text was recovered at journal pages 81, 82 and 85. Direct PDF opening/rendering in this runtime still failed with a cache miss; a screenshot attempt then failed because no `application/pdf` view was produced. Therefore this is **not** represented as a complete visual page-by-page PDF audit.

## Frozen bounded search procedure

Audit date: **2026-09-02**.

Interfaces used:

1. public web search restricted to `ora.ox.ac.uk` where specified;
2. the indexed text of the ORA publisher-version PDF;
3. direct open/find/render attempts against the returned PDF result.

The continuation audit stopped after **24 exact search queries**, one direct PDF-open attempt, four in-document `find` attempts, and one screenshot attempt. No broader backward/forward citation-history search was admitted after this source window was frozen.

Exact search queries, in execution order:

1. `"Markoff Numbers, Principal Ideals and Continued Fraction Expansions" "Lemma 5" Button`
2. `"Markoff Numbers, Principal Ideals and Continued Fraction Expansions" "Theorem 7" Button`
3. `"Markoff Numbers, Principal Ideals and Continued Fraction Expansions" "Lemma 8" Button`
4. `"Markoff Numbers, Principal Ideals and Continued Fraction Expansions" "Lemma 6" Button`
5. `"Markoff Numbers, Principal Ideals and Continued Fraction Expansions" "Lemma 7" Button`
6. `"MARKOFF NUMBERS" "A^2 is principal" Button "negative norm"`
7. `"MARKOFF NUMBERS" "C+" "x=3c" Button`
8. `"MARKOFF NUMBERS" "Theorem 7" "C+" Button`
9. `"MARKOFF NUMBERS" "Lemma 8" "C+" Button`
10. `"MARKOFF NUMBERS" "Lemma 5." "anti-symmetric" Button`
11. `"MARKOFF NUMBERS" "Lemma 5." "symmetric" "A2" Button`
12. `"MARKOFF NUMBERS" "Lemma 6." "principal" Button`
13. `"MARKOFF NUMBERS" "Lemma 7." "principal" Button`
14. `"82 J. O. BUTTON" "Lemma 5" "A2" "symmetric"`
15. `"83 J. O. BUTTON" "C+" "C-"`
16. `"84 J. O. BUTTON" "C+" "C-"`
17. `"84 MARKOFF NUMBERS" "Lemma 7"`
18. `"Markoff numbers, principal ideals and continued fraction expansions" Button ORA 2001 77 95`
19. `"Markoff Numbers, Principal Ideals and Continued Fraction Expansions" "A2 is principal" "symmetric"`
20. `"Markoff Numbers, Principal Ideals and Continued Fraction Expansions" "anti-symmetric"`
21. `"83" "Lemma 6." "MARKOFF NUMBERS" Button`
22. `"83" "Lemma 7." "J. O. BUTTON"`
23. `"84" "Lemma 6." "J. O. BUTTON"`
24. `"84" "Lemma 7." "MARKOFF NUMBERS" Button`

The direct `find` strings were `Lemma 6`, `Lemma 7`, `Lemma 8`, and `Theorem 7`. Those finds could not operate on a fetched PDF body because direct PDF opening returned a cache miss.

This manifest supersedes the earlier vague phrase “combinations of search terms” and makes the negative-placement boundary reproducible at the query level.

## Source-local findings

### Journal p.81 — Lemma 5(1)

Immediately after Lemma 4, Button specializes to

\[
D=9c^2-4.
\]

For the invertible ideal

\[
A=a\mathbb Z+\frac{b+\sqrt D}{2}\mathbb Z
\]

and its associated quadratic irrational, Lemma 5(1) characterizes principality through the continued-fraction tail `[3c-2,1]`, with parity of removed terms tracking the sign of the norm of a generator.

This is a principality/continued-fraction criterion. No `4/5` affine transform, factor-5 CRT shift, or fixed-433 specialization appears in the source-local Lemma 5(1) text recovered here.

### Journal p.82 — Lemma 5(2)–(3)

The indexed primary text gives:

- Lemma 5(2): `A^2` is principal with a negative-norm generator iff the periodic continued-fraction part is symmetric;
- Lemma 5(3): `A^2` is principal with a positive-norm generator iff the periodic part is “anti-symmetric” in Button's stated sense.

Again, the objects and conclusion concern ideal-class principality and symmetry of a periodic continued fraction. This is structurally relevant background, but it is not the AIMath affine identity.

### Journal pp.83–84 — Lemmas 6–7

The audit explicitly targeted Lemma 6 and Lemma 7 with the exact queries listed above. The search index did **not** return a stable source-local passage containing either complete lemma statement, and the PDF renderer did not yield a visual page view.

Therefore this audit does **not** reconstruct, paraphrase, or infer the statements of Lemmas 6–7 from surrounding arguments. Their exact wording and any potentially hidden representative normalization remain a residual uncertainty of this runtime.

### Journal p.85 — pre-Theorem-7 congruence representative

This is the closest source-local passage to the AIMath modular-root side.

Button works with

\[
x^2\equiv D\pmod{4c},
\]

with `x` defined up to multiples of `2c`. Let `alpha` be an inverse of `a` modulo `c`; the paper then chooses

\[
\boxed{x=3c-2b\,\alpha}
\]

and verifies that this is an appropriate representative satisfying the displayed congruence. The associated ideal is denoted `C_+`.

Because Button has already fixed `D=9c^2-4`, this source equation implies, merely by reduction modulo `c`,

\[
x^2\equiv -4\pmod c.
\]

Thus on an odd specialization one may scale by the inverse of `2` modulo `c` to obtain a square root of `-1`. **This last scaling observation is an AIMath comparison derived from Button's displayed congruence; it is not quoted as a Button theorem and it does not identify Button's `x` with AIMath's `r_k`.**

### Journal p.85 — Theorem 7

With

\[
C_+=c\mathbb Z+\frac{x+\sqrt D}{2}\mathbb Z
\]

and `x` chosen as above, Theorem 7 states that `C_+^2` is principal and displays a generator. The generator formula is degraded in the available OCR/index rendering, so this audit does not transcribe that formula as load-bearing evidence without a visual PDF check.

The proof chooses integers satisfying a Bezout relation with `a` and `c`, adjusts representatives, writes

\[
x^2=D+4lc,
\]

and derives the divisibility condition needed before invoking Lemma 8.

### Journal p.85 — Lemma 8

The indexed primary text shows Lemma 8 beginning with an ideal in Hermite normal form and Theorem 7 explicitly says it will be used to find the square of such an ideal. The complete Lemma 8 formula was not stably recovered in the visible snippet, so no fuller statement is asserted here.

## Object-role firewall

The notation must not be collapsed across the two theories.

Button's `x` in the p.85 passage is a **quadratic-order ideal/congruence representative** satisfying `x^2 ≡ D (mod 4c)` and defined modulo `2c`.

AIMath's fixed package instead has distinct roles:

- `p_k`: numerator of a particular Markov fraction `mu(t_k)=p_k/M_k`;
- `r_k`: the fixed modular representative satisfying `r_k^2 ≡ -1 (mod M_k)` and the accepted normalization `r_k=M_k-p_k`;
- `U_k`: the continuant entry attached to the fixed-433 word, with `U_k=r_k-M_k/5`.

The fact that Button's `x/2` is of square-root-of-`-1` type modulo an odd `c` is **structural adjacency only**. No primary-source equation located in this bounded window identifies `x/2` with the fixed AIMath `r_k`, `p_k`, or `U_k` on the 433 ray.

## Exact-correspondence decision

| AIMath target | Closest Button 2001 source-local material | Exact correspondence in audited window? |
|---|---|---|
| `U_k/M_k = 4/5 - mu(t_k)` | Lemma 5 continued-fraction/ideal criteria; p.85 ideal representative | **NO MATCH LOCATED** |
| `5p_k + 5U_k = 4M_k` | no source-local affine numerator identity with coefficients `4,5,5` recovered | **NO MATCH LOCATED** |
| `U_k = r_k - M_k/5` | p.85 `x^2 ≡ D (mod 4c)`, `x=3c-2b alpha`; after reduction, a scaled sqrt(-1)-type representative | **NO MATCH LOCATED** |
| fixed factor-5 CRT sign flip | general ideal/congruence machinery around Theorem 7 | **NO EXPLICIT FACTOR-5 SPECIALIZATION LOCATED** |

The strongest positive placement statement justified by the source is therefore:

> Button 2001 contains a closely related modular representative / ideal-square construction, and its p.85 representative reduces to a scaled square root of `-1` modulo `c`; however, the bounded source-local audit did not recover the fixed AIMath affine transform, the `4:5` numerator relation, or the `M/5` representative shift.

This is a **nonmatch within a frozen source window**, not a proof of publication novelty or a proof that no algebraically equivalent formulation exists anywhere in Button 2001.

## Remaining uncertainty

1. The complete statements of Lemmas 6–7 were not recoverable from stable source-local indexed snippets in this runtime.
2. Lemma 8 and the Theorem 7 generator formula were only partially readable through OCR/indexed text.
3. Direct PDF rendering and screenshot inspection failed, so typography, signs, and symbols in those passages were not visually cross-checked page-by-page.
4. No backward historical-priority audit (Button 1998, Cassels/Cohn, etc.) or forward citation audit was performed in this continuation.
5. Therefore publication novelty remains **NOT ESTABLISHED**.

## Bounded disposition

The bounded Button-2001 source audit is closed at this point. The previous operational access blocker is removed, the closest exact source locations are frozen, and the remaining uncertainty is explicit.

Task state requested after PR update: **WAITING_REVIEW**.

A reviewer with reliable visual access to the publisher PDF can now focus narrowly on pp.83–85, especially Lemmas 6–8 and the exact Theorem 7 generator typography, rather than repeat the broader search.
