<!-- SPDX-FileCopyrightText: 2026 AIMath contributors -->
<!-- SPDX-License-Identifier: Apache-2.0 -->

# AFRD E0 worker freeze

- Task: `TASK-AIMATH-ND-AFRD-001`
- Worker: `w-5aef23bcfc3ab622`
- Principal: `gh:51mns`
- Exact base main: `ba61d1d7acbda8712cc447d19e45969e72e5fcfa`
- Branch: `research/TASK-AIMATH-ND-AFRD-001/w-5aef23bcfc3ab622`
- Owned path: `work/TASK-AIMATH-ND-AFRD-001/w-5aef23bcfc3ab622/**`

## Goal

Freeze a bias-controlled E0 pilot contract for AIMath Factor Representation Discovery (AFRD). The contract must make a future representation `X(N)` testable without allowing hidden factors, hidden instances, candidate-specific novelty hints, or another discovery lane's unpublished representation to influence discovery-time computation.

## Context

This worker is a contract/evaluator-design lane. It does **not** invent `X(N)`, claim a new factorisation method, or perform candidate-specific novelty analysis. General factorisation and prior representation families are used only to define evaluator-side baselines and later reduction checks.

## Constraints

1. Any deployed `X(N)` and its readout must be computable from `N` and public experiment constants alone.
2. `p,q` are labels/evaluator data only and may never be evaluation-time inputs to the candidate.
3. Hidden H0-H5 instances, randomness, factors, and answers are not committed before candidate freeze.
4. Discovery workers must not inspect evaluator baseline detail, another discovery lane's frozen representation, or post-signal audit results before their own freeze.
5. A useful candidate is not automatically novel mathematics. Reduction-to-known-method and literature audits occur only after a candidate passes a predeclared held-out utility gate.
6. Finite held-out success is empirical evidence only, never a theorem.
7. No claim-level or novelty promotion is performed by this worker.

## Done when

The lane contains a machine-readable experiment contract plus human-readable firewall, data-split, representation/evaluation, evaluator-baseline, post-signal audit, follow-up-gate, and worker outcome artifacts; a standalone verifier checks the contract invariants and frozen counts using only the Python standard library.
