<!-- SPDX-FileCopyrightText: 2026 AIMath contributors -->
<!-- SPDX-License-Identifier: CC-BY-4.0 -->

# Outcome — TASK-FIXED-433-001 / w-f29341f2a4973b71

## State

**WAITING_REVIEW**

## Classification

`INCONCLUSIVE` — bounded primary-source placement audit closed with a documented unresolved comparison.

Truth Layer effect: `NONE`. Claim promotion: `NONE`. Novelty: `NOT_ESTABLISHED`.

## Fixed source locations

Primary source: J. O. Button, *Markoff Numbers, Principal Ideals and Continued Fraction Expansions*, Journal of Number Theory 87 (2001), 77–95, DOI `10.1006/jnth.2000.2578`, publisher/version-of-record PDF exposed by Oxford University Research Archive.

Source-local material recovered:

- **p.81, Lemma 5(1):** principality via the continued-fraction tail `[3c-2,1]` after specializing to `D=9c^2-4`;
- **p.82, Lemma 5(2)–(3):** symmetry / anti-symmetry of the periodic continued-fraction part characterizes when `A^2` is principal with negative-/positive-norm generator;
- **pp.83–84, Lemmas 6–7:** targeted, but complete source-local statements were not stably recovered by the indexed-text interface;
- **p.85, immediately before Theorem 7:** choose an inverse `alpha` of `a (mod c)`, set `x=3c-2b alpha`, and verify `x^2 ≡ D (mod 4c)`;
- **p.85, Theorem 7:** for `C_+=cZ+((x+sqrt(D))/2)Z`, `C_+^2` is principal; the displayed generator is OCR-degraded in this runtime and was not transcribed as load-bearing evidence;
- **p.85, Lemma 8:** introduced to compute the square of an ideal in Hermite normal form; complete formula not stably recovered in the visible indexed snippet.

## Exact correspondence decision

No exact source-local match was located in the frozen Button-2001 audit window for any of:

`U_k/M_k = 4/5 - mu((9k+8)/(15k+13))`,

`5 p_k + 5 U_k = 4 M_k`,

`U_k = r_k - M_k/5`.

The closest exact algebraic bridge is Button's p.85 congruence. Since `D=9c^2-4`,

`x^2 ≡ D (mod 4c)` implies `x^2 ≡ -4 (mod c)`.

On an odd specialization, scaling by `2^{-1}` gives a square-root-of-`-1` type representative modulo `c`. This is only structural adjacency. Button's `x` is an ideal/congruence representative; it is **not** identified here with AIMath's Markov-fraction numerator `p_k`, fixed modular representative `r_k`, or continuant entry `U_k`.

No source-local factor-5 CRT shift, `4/5` transform, or affine relation with coefficients `4,5,5` was recovered.

## Frozen search boundary

The continuation audit on 2026-09-02 used 24 exact recorded web queries against the ORA/indexed publisher text, plus one direct PDF-open attempt, four `find` attempts, and one screenshot attempt. The exact query manifest is preserved in `LITERATURE_AUDIT.md`.

The PDF open returned a cache miss, and the screenshot call could not resolve an `application/pdf` view. Therefore no complete visual page-by-page PDF audit is claimed.

## Remaining uncertainty

- Lemmas 6–7 remain the main uninspected source-local gap.
- The exact typography of the Theorem 7 generator and full Lemma 8 formula was not visually cross-checked.
- An equivalent formula could exist elsewhere in the article or older literature under different notation.
- Search non-detection is not novelty evidence.

## Reviewer target

A reviewer with reliable PDF visual access should inspect pp.83–85 only, with special attention to Lemmas 6–8 and Theorem 7, and test whether any source representative normalization specializes exactly to the AIMath `4/5`, `5p+5U=4M`, or `U=r-M/5` formulas.

## Artifact

- `LITERATURE_AUDIT.md` — frozen query manifest, page/lemma/theorem locations, object-role firewall, exact-match table, and residual uncertainty.
