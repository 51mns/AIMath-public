<!-- SPDX-FileCopyrightText: 2026 AIMath contributors -->
<!-- SPDX-License-Identifier: CC-BY-4.0 -->

# TASK-OPEN-MATH-DISCOVERY-001 — bounded staircase-partition coefficient search

## Frozen lane

- **Public base:** `5a36b1d413a05400120d25946e0acf71bce20a30`
- **Task:** `TASK-OPEN-MATH-DISCOVERY-001`
- **This chat's narrowed owned path:** `work/TASK-OPEN-MATH-DISCOVERY-001/staircase-coefficients-gpt56sol/**`
- **Object:** 
  \[
  P_m(q)=\prod_{j=1}^{m}(1+q^j)=\sum_{s=0}^{T_m} a_m(s)q^s,\qquad T_m=\frac{m(m+1)}2.
  \]
- **Interpretation:** `a_m(s)` counts subsets of `{1,...,m}` with sum `s`, equivalently partitions of `s` into distinct parts at most `m`.
- **Train range frozen before candidate selection:** `m=1..14`.
- **Held-out range frozen before inspection:** `m=15..30`.
- **Post-held-out stress range:** `m=31..80`.
- **Budget used:** 10 hypotheses, 2 serious proof/literature routes. This is within the Task caps of at most 20 hypotheses and at most 3 serious routes.
- **Arithmetic:** Python arbitrary-precision integers only.

## Exact bounded results

The executable verifier is `open_math_discovery_coefficients.py`.

| ID | Frozen hypothesis | Result |
|---|---|---|
| H01 | `a_m(s)=a_m(T_m-s)` | exact bounded PASS for `m=1..80`; also has the elementary subset-complement proof |
| H02 | no internal zero coefficient | exact bounded PASS for `m=1..80`; elementary induction |
| H03 | coefficients are unimodal | exact bounded PASS for `m=1..80`; **LITERATURE_MATCH** |
| H04 | coefficients are log-concave | **REFUTED**: first failure `m=3,s=2`, triple `(1,1,2)`, since `1^2<1*2` |
| H05 | standard global strict unimodality | **REFUTED for every `m>=1`** because `a_m(0)=a_m(1)=1` |
| H06 | for `m>=12`, `a_m(s)<a_m(s+1)` whenever `4<=s<T_m/2` | train `12..14` PASS; held-out `15..30` PASS; stress `31..80` PASS; **finite evidence only** |
| H07 | `m=12` is the first threshold in the tested prefix for H06 | exact bounded PASS: every `m=4..11` has at least one failing/equality edge; `m=11` still has equality at `s=31` |
| H08 | for tested `m>=12`, the only pre-midpoint adjacent equalities are `s=0,1,3` | exact bounded PASS `m=12..80`; equivalent to H06 plus the fixed small coefficients |
| H09 | for tested `m>=12`, the modes are exactly the central one or central two positions according to parity of `T_m` | exact bounded PASS `m=12..80`; consequence of H06 and symmetry in the tested scope |
| H10 | coefficient recurrence and adjacent-difference recurrence hold | exact algebraic identity and bounded verifier PASS |

For H06 the held-out counterexample list is empty and the post-held-out stress counterexample list is empty. The minimum positive adjacent difference seen in the H06 region over `m=12..80` is exactly `1`.

These observations **do not prove H06 for all `m>=12`**.

## Exact recurrences

From
\[
P_m(q)=(1+q^m)P_{m-1}(q)
\]
we have, with coefficients outside support interpreted as zero,
\[
a_m(s)=a_{m-1}(s)+a_{m-1}(s-m).
\]

Writing
\[
d_m(s)=a_m(s+1)-a_m(s),
\]
gives
\[
\boxed{d_m(s)=d_{m-1}(s)+d_{m-1}(s-m)}.
\]

The verifier checks both identities exactly.

### Proof route R1 — direct induction on the difference recurrence

**Goal:** prove H06 from positivity of earlier differences.

**Blocker:** for an `s` that is left of the midpoint of `P_m`, the term `d_{m-1}(s)` need not itself lie left of the midpoint of `P_{m-1}`. It can therefore be zero or negative even though the target `d_m(s)` is positive. The recurrence is exact but does not close under the naïve positive-cone induction.

**Outcome:** useful reduction, but no all-`m` proof. Do not promote H06.

## Literature route R2

### Classical staircase-partition identification and unimodality

Stanley and Zanello, *Unimodality of partitions with distinct parts inside Ferrers shapes*, European Journal of Combinatorics 49 (2015), 194–202, DOI `10.1016/j.ejc.2015.03.007`, identify the shifted staircase
\[
\langle m,m-1,\ldots,2,1\rangle
\]
with rank-generating function
\[
\prod_{j=1}^{m}(1+q^j).
\]
They state that its unimodality was essentially first proved by E. B. Dynkin and point to a linear-algebra proof by Proctor. They also state that a constructive combinatorial proof was still open in that paper.

Relevant references listed there include:

- E. B. Dynkin, *Some properties of the weight system of a linear representation of a semisimple Lie group*, Dokl. Akad. Nauk SSSR 71 (1950), 221–224.
- E. B. Dynkin, *The maximal subgroups of the classical groups*, Amer. Math. Soc. Transl. Ser. 2, 6 (1957), 245–378.
- R. Proctor, *Solution of two difficult combinatorial problems using linear algebra*, Amer. Math. Monthly 89 (1982), 721–734.

Thus H03 is a rediscovery / literature match, not a new theorem.

### Nearby general asymptotic/unimodality result

A. M. Odlyzko and L. B. Richmond, *On the Unimodality of some Partition Polynomials*, European Journal of Combinatorics 3(1) (1982), 69–84, DOI `10.1016/S0195-6698(82)80010-3`, prove an "almost unimodality" theorem for a wide class of
\[
\prod_i(1+x^{a_i}),
\]
including polynomial sequences `a_k=f(k)` under their stated condition. The present choice `a_k=k` lies in that broad family.

The accessible abstract/source record does **not** establish the exact finite threshold `m>=12` and exact edge boundary `s>=4` in H06. It therefore cannot be used as a proof of H06.

## Novelty boundary

A targeted web/literature search found strong prior results for ordinary unimodality and nearby almost-unimodality, but did not locate an inspected source stating the exact H06 threshold
\[
m\ge 12,\qquad 4\le s<T_m/2.
\]

**Search absence is not novelty evidence.** H06 remains a bounded computational observation until a universal proof and a proper primary-source novelty audit are completed.

## Outcome

**Outcome type: `LITERATURE_MATCH`.**

Reusable information:

1. the bounded process independently rediscovered a classical staircase-partition unimodality theorem;
2. log-concavity and ordinary strict-unimodality guesses were killed by exact counterexamples/families;
3. the stronger near-strict pattern H06 survived a pre-frozen held-out range and a larger post-held-out stress range;
4. H06 is reduced to positivity of the exact difference recurrence, with a precise reason why the naïve induction does not close.

No mathematical claim is promoted by this writer.

## Reproduction

From repository root:

```bash
python3 work/TASK-OPEN-MATH-DISCOVERY-001/staircase-coefficients-gpt56sol/open_math_discovery_coefficients.py \
  > /tmp/TASK-OPEN-MATH-DISCOVERY-001-results.json
sha256sum work/TASK-OPEN-MATH-DISCOVERY-001/staircase-coefficients-gpt56sol/open_math_discovery_coefficients.py \
  /tmp/TASK-OPEN-MATH-DISCOVERY-001-results.json
```

Expected SHA-256:

```text
7f97962b75576397e6d067fea202ef73b510b0e7d200cc84fd3cff8e21a8b44f  open_math_discovery_coefficients.py
19408f875ad4749f653cf99ee31c6b09822d4179a70f158db68e241cb0a26c00  generated results JSON
```

Local execution in the research session exited successfully and reported:

```text
hypothesis_count: 10
heldout_H06_counterexamples: []
stress_H06_counterexamples: []
minimum_positive_tail_difference_m_12_80: 1
```

Repository-wide validation could not be run in the local Python/container runtime because that runtime had no outbound GitHub network access. The branch/PR CI is therefore the repository-level validation gate.
