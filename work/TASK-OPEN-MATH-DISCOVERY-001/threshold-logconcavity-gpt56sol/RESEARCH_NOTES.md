<!-- SPDX-FileCopyrightText: 2026 Shoma Nakabayashi -->
<!-- SPDX-License-Identifier: CC-BY-4.0 -->

# Bounded exploration and falsification log

Task: `TASK-OPEN-MATH-DISCOVERY-001`  
Actor: `gh:51mns`  
Public base: `5a36b1d413a05400120d25946e0acf71bce20a30`  
Branch: `research/TASK-OPEN-MATH-DISCOVERY-001-threshold-gpt56sol`

This is the writer's bounded E0 exploration record. It is not a canonical outcome, independent review, or novelty claim.

## Budget used

The task allowed at most 20 hypotheses and at most 3 serious proof routes. This route stopped early after reusable progress, using three explicit hypotheses/targets and one analytic proof route.

## H1 — connected-graph log-concavity

**Candidate.** Independence polynomials of connected graphs might have log-concave coefficient sequences.

**Falsification strategy.** Exact finite graph search, followed by an exact independent-set counter on any witness.

**Outcome.** Falsified. A 10-vertex threshold graph already gives a counterexample, so no larger unrestricted connected-graph search was justified.

**Lesson.** The broad property is false even inside a highly structured graph class; continuing brute-force search over all connected graphs would add little mechanism.

## H2 — threshold-graph log-concavity

**Candidate.** Restricting to threshold graphs might restore log-concavity.

**Falsification strategy.** Enumerate every binary threshold building word of each order, using the exact recurrences

- append isolated vertex `0`: `I -> (1+x) I`;
- append dominating vertex `1`: `I -> I+x`.

Cross-check the recurrence by explicitly building each graph and enumerating all independent subsets.

**Outcome.** Falsified exactly at order 10. Every one of the 1023 threshold words through order 10 was cross-checked by both implementations. Orders 1 through 9 have no failure; order 10 has exactly two failing building words:

- `0001111111`, coefficients `(1,10,3,1)`;
- `0000111111`, coefficients `(1,10,6,4,1)`.

This makes order 10 the exact finite minimum inside the standard binary threshold construction.

## Literature gate after H2

The first witness was then checked against the literature instead of being labelled new. Levit and Mandrescu already record the threshold graph `3K1+K7`, with building string `3[0]7[1]`, as having a unimodal but non-log-concave independence polynomial.

Therefore the witness is a **known-theory rediscovery**, not a novelty claim.

## H3 — two-block threshold family admits a closed criterion

**Target.** For the natural two-block family

`T_(n,k) = k K1 + K_(n-k)`

(Zykov join), derive a complete log-concavity criterion instead of merely listing counterexamples.

**Analytic route.** The join structure gives

`I(T_(n,k);x) = (1+x)^k + (n-k)x`.

Hence `a_0=1`, `a_1=n`, and `a_j=C(k,j)` for `j>=2`. Binomial log-concavity handles every internal index `j>=3`, while the `j=1` inequality is automatic from `n>=k`. The only nontrivial inequality is therefore

`C(k,2)^2 >= n C(k,3)`.

For `k>=3`, this is equivalent to

`n <= 3 k(k-1) / (2(k-2))`.

For `k<=2`, log-concavity is automatic.

**Outcome.** Proof candidate / structural reduction. In particular `k=3` gives `1+n x+3x^2+x^3`, which is non-log-concave for every `n>=10`.

## Finite verifier and held-out gate

The verifier checks the family formula and iff criterion for all `1 <= k <= n <= 30` with exact integer arithmetic.

Orders through 18 had already been inspected during exploration and are not called held-out. After the algebraic criterion was frozen, `n=19` and `n=20` in the `k=3` family were reserved for an independent graph/subset implementation. They returned `(1,19,3,1)` and `(1,20,3,1)` respectively, matching the frozen prediction.

The universal family statement is supported by the algebraic derivation, not inferred from these finite checks.

## Stop decision

Stop this E0 route here rather than enlarge brute force. The task success gate is met by:

1. a useful literature rediscovery;
2. an exact finite minimum-order classification through the complete threshold-word universe up to the first failure;
3. a reusable closed criterion for a natural infinite two-block threshold family.

Publication novelty for items 2–3 remains `NOT_ESTABLISHED`. Independent review is required before any claim promotion.
