<!-- SPDX-FileCopyrightText: 2026 AIMath contributors -->
<!-- SPDX-License-Identifier: CC-BY-4.0 -->

# OUTCOME — TASK-EQUIANGULAR-R18-001

- `task_id`: `TASK-EQUIANGULAR-R18-001`
- `worker_id`: `w-ed0e3776898dcc3b`
- `outcome_type`: `STRUCTURAL_REDUCTION`
- `research_stage`: `E0`
- `claim_level_effect`: `NONE`
- `novelty`: `NOT_ESTABLISHED`
- `external_frontier_impact`: `NONE`
- `review_required_for_promotion`: `YES`

## Summary

A source-backed all-branch reduction was obtained for a hypothetical 59-line system in
`R^18`.  Greaves' close-to-relative-bound lemma forces one eigenvalue `11` beyond the
41 forced `-5` eigenvalues.  After removing that `11` and shifting by `11`, all remaining
spectral freedom is a degree-17 monic integral real-rooted weak-type-2 polynomial

\[
g(y)=y^{17}-7y^{16}-8y^{15}+\cdots
\]

whose roots have sum `7` and square-sum `65`.

Combining weak type 2 with AM--GM gives the uniform terminal gate

\[
g(0)\in\{-65536,0,65536\}.
\]

So the complete 59-line spectral problem splits into a repeated-11 regime (`g(0)=0`)
and a simple-11 fixed-terminal-magnitude regime (`|g(0)|=65536`).

This is reusable across multiple spectral branches and avoids isolated eta-by-eta
enumeration.  It does not prove `N(18)<=58`.

## Verification

Run:

```bash
python3 work/TASK-EQUIANGULAR-R18-001/w-ed0e3776898dcc3b/verify_reduction.py
```

Expected final line:

```text
structural reduction verifier: PASS
```

Local pre-upload verifier SHA-256:

```text
840feb0c3e26a5d95d99f4ba86d67e592a186f3744bef2cb5bbd787ff77c75c9
```

The verifier uses Python standard-library integer arithmetic only for the load-bearing
threshold and terminal-product inequalities.

## Evidence boundary

The external ingredients are known Seidel/type-2 structural lemmas.  The specialization
and terminal-product trichotomy have not been independently reviewed here, and publication
novelty is not claimed.  No private/unmerged eta classification is used as a premise.

## Self-assessment

This self-assessment has zero Truth Layer and scheduling authority.

- information gain: 4/5
- mathematical reusability: 5/5
- transfer potential: 3/5
- external relevance: 4/5
- follow-up expected value: 4/5
- surprise: 3/5
- uncertainty: 2/5

The main remaining uncertainty is whether the terminal-product trichotomy already appears
explicitly in the literature or whether it is only an immediate unpublished specialization of
known lemmas.
