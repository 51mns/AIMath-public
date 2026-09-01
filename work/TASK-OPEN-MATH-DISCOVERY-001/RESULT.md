<!-- SPDX-FileCopyrightText: 2026 Shoma Nakabayashi -->
<!-- SPDX-License-Identifier: CC-BY-4.0 -->

# TASK-OPEN-MATH-DISCOVERY-001 — threshold-graph independence-polynomial gate

## Fixed task contract

- **Task:** `TASK-OPEN-MATH-DISCOVERY-001`
- **Public base:** `5a36b1d413a05400120d25946e0acf71bce20a30`
- **Private canonical snapshot:** `c8e61e0e398f540bc8c5de79663398d689f37473`
- **Branch:** `research/TASK-OPEN-MATH-DISCOVERY-001-51mns`
- **Owned path:** `work/TASK-OPEN-MATH-DISCOVERY-001/**`
- **Stage:** E0 exploration, with one E1-worthy finite/structural result candidate below
- **Claim-promotion boundary:** writer-only; nothing here is `INDEPENDENTLY_REPRODUCED`
- **Material AI assistance:** GPT-5.6 Sol performed the bounded search, exact derivation, literature triage, and verifier drafting under the authenticated maintainer session; DCO responsibility remains with the GitHub submitter.

Goal: search natural mathematical objects for a reusable theorem/counterexample/structural reduction, with exact arithmetic, bounded search, and an honest literature/held-out boundary.

## Discovery route

The initial object was the coefficient sequence of the independence polynomial

\[
I(G;x)=\sum_j s_jx^j,
\]

where \(s_j\) is the number of independent \(j\)-sets.

A broad exploratory search found that log-concavity is not automatic.  The route was then narrowed to the natural class of **threshold graphs**, represented by a binary building word beginning with `0`, where `0` appends an isolated vertex and `1` appends a dominating vertex.

The recurrence used for the independence polynomial is exact:

- append `0`: \(I\mapsto (1+x)I\);
- append `1`: \(I\mapsto I+x\).

A second implementation constructs the graph itself and counts every independent subset directly.

## Result 1 — exact minimal order inside threshold graphs

The verifier exhausts every threshold building word through order 10.

| order \(n\) | words checked | non-log-concave |
|---:|---:|---:|
| 1 | 1 | 0 |
| 2 | 2 | 0 |
| 3 | 4 | 0 |
| 4 | 8 | 0 |
| 5 | 16 | 0 |
| 6 | 32 | 0 |
| 7 | 64 | 0 |
| 8 | 128 | 0 |
| 9 | 256 | 0 |
| 10 | 512 | 2 |

For every one of the \(1023\) words through \(n=10\), the recurrence result is cross-checked against direct subset enumeration.

Thus, under the standard binary-building characterization of threshold graphs:

\[
\boxed{\text{the minimum order of a threshold graph with a non-log-concave independence polynomial is }10.}
\]

The two order-10 failing words are

\[
0001111111,\qquad 0000111111.
\]

Their coefficient sequences are respectively

\[
(1,10,3,1),\qquad (1,10,6,4,1).
\]

The first fails at index 2 because

\[
3^2=9<10\cdot1,
\]

and the second because

\[
6^2=36<10\cdot4=40.
\]

This is a **finite exhaustive result**.  It does not rely on sampling.

## Result 2 — closed two-block threshold criterion

Let

\[
T_{n,k}=kK_1+K_{n-k},
\]

where \(+\) is the Zykov join, \(1\le k\le n\).  Its threshold building word is

\[
0^k1^{n-k}.
\]

Every independent set lies wholly in one side of the join, hence

\[
I(T_{n,k};x)
=(1+x)^k+(n-k)x.
\]

Therefore

\[
a_0=1,\qquad a_1=n,\qquad
a_j=\binom{k}{j}\quad(2\le j\le k).
\]

For \(j\ge3\), log-concavity is inherited from the binomial coefficients.  At \(j=1\), \(n^2\ge\binom{k}{2}\) is automatic because \(n\ge k\).  Thus, for \(k\ge3\), the only nontrivial gate is \(j=2\):

\[
\binom{k}{2}^2\ge n\binom{k}{3}.
\]

Equivalently,

\[
\boxed{
T_{n,k}\text{ has a log-concave independence polynomial}
\iff
n\le \frac{3k(k-1)}{2(k-2)}
}
\qquad(k\ge3).
\]

For \(k\le2\), it is always log-concave.

In particular, taking \(k=3\),

\[
I(T_{n,3};x)=1+nx+3x^2+x^3,
\]

so

\[
\boxed{T_{n,3}\text{ is non-log-concave for every }n\ge10.}
\]

The verifier checks the formula and the iff criterion for all \(1\le k\le n\le30\) using integer arithmetic.

## Held-out boundary

The exploratory scratch work had already inspected threshold orders through \(n=18\), so those orders are **not** described as held-out.

After the two-block formula and its log-concavity gate were frozen, orders \(n=19,20\) for the \(k=3\) family were reserved as implementation held-out checks.  A direct graph/subset counter independently recovered

- \(n=19:\ (1,19,3,1)\), failure \(9<19\);
- \(n=20:\ (1,20,3,1)\), failure \(9<20\).

This held-out check tests the implementation/generalization path; the all-\(n\) family statement itself is justified by the algebra above, not by held-out finite agreement.

## Literature triage

The order-10 witness itself is **known**.

Levit and Mandrescu, *On the independence polynomial of an antiregular graph* (arXiv:1007.0880; Carpathian J. Math. 28 (2012), 279–288) define threshold graphs by the same isolated/dominating binary construction and explicitly note a threshold graph

\[
3K_1+K_7
\]

with building string `3[0]7[1]` whose independence polynomial is unimodal but non-log-concave.

Primary/preprint reference:

- https://arxiv.org/abs/1007.0880
- DOI: `10.37193/CJM.2012.02.08`

The same paper closes by proposing the study of binary-pattern threshold graphs whose independence polynomials are unimodal, log-concave, or real-rooted.  The two-block criterion above lies naturally inside that program.

A bounded search also found a 2024 note by Chikh and Mihoubi giving binomial-coefficient formulae for independence polynomials of general threshold graphs.  No retrieved source in this bounded triage stated the exact **minimum order 10** result or the exact iff criterion above.  That absence is not novelty evidence.

**Publication novelty status:** `NOT_ESTABLISHED`.

## Evaluation

Outcome type:

- `USEFUL_KNOWN_THEORY_REDISCOVERY` for the known `3K1+K7` counterexample;
- `STRUCTURAL_REDUCTION / FINITE_EXHAUSTIVE_CANDIDATE` for the two-block iff criterion and exact minimum-order-10 threshold classification.

This clears the task's reusable-output gate, but the minimum-order statement and two-block criterion should receive a deeper literature audit before any novelty wording, and independent review before canonical claim promotion.

## Reproduce

From the repository root:

```bash
python3 work/TASK-OPEN-MATH-DISCOVERY-001/verify_threshold_logconcavity.py
```

Expected final line:

```text
PASS
```

The verifier uses only the Python standard library.
