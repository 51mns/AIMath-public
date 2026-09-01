# Contributing

Contributions that **disprove** an AIMath claim are as valuable as contributions that extend one.

## Good contributions

- a minimal counterexample;
- a shorter or more transparent proof;
- an independent verifier;
- a clean reproduction on another platform;
- a primary-source literature match;
- a corrected theorem boundary;
- a new exact computation with reproducible inputs and hashes;
- a precise explanation of why a failed route can be reopened with a genuinely new ingredient.

## Before starting a mathematical route

Read, in this order:

1. [`docs/CONTRIBUTION_TARGETS.md`](docs/CONTRIBUTION_TARGETS.md) — current bounded tasks where outside work is useful;
2. [`docs/FAILED_ROUTES.md`](docs/FAILED_ROUTES.md) — known blockers/no-go/HOLD routes;
3. [`docs/EVIDENCE_POLICY.md`](docs/EVIDENCE_POLICY.md) — proof/computation/review/novelty separation;
4. the exact public claim package linked from [`docs/RESULTS.md`](docs/RESULTS.md).

If your proposal resembles a route marked `REFUTED`, `BOUNDED NO-GO`, `BLOCKED`, `INCONCLUSIVE`, or `HOLD`, explain what materially new ingredient changes the old obstruction.

Do not reopen a closed architecture merely by increasing finite search depth, polynomial degree, ansatz order, or compute budget unless the failure ledger explicitly says that remains meaningful.

## Before opening a pull request

Run:

```bash
python3 scripts/public_release_audit.py .
python3 scripts/verify_public_layout.py .
python3 scripts/reproduce_public_claims.py .
```

If your change affects only one claim package, also run its local replay command from that package.

For mathematical changes, include:

- Claim ID;
- exact old statement;
- exact proposed statement;
- proof vs finite computation distinction;
- exact reproduction command when executable evidence exists;
- changed file hashes or deterministic manifest;
- independent-review status;
- novelty claim, if any, with primary sources;
- relevant failed-route entry and reopening justification, when applicable.

Do not submit raw private conversations, private correspondence, personal data, credentials, private Git history, or third-party artifacts whose redistribution rights are unclear.

## When a route fails

Failure is part of the research output. Update `docs/FAILED_ROUTES.md` when the result establishes a reusable blocker, bounded no-go, refutation, or strong inconclusive lesson. Record the exact scope, decisive obstruction, what remains open, and a clear reopening condition.

Do not turn a bounded failure into a claim that an entire mathematical area is impossible.

## Status promotion

A writer does not self-promote their own result to `INDEPENDENTLY_REPRODUCED`. A materially independent review is required. See [`docs/CLAIM_LEVELS.md`](docs/CLAIM_LEVELS.md).

An independent reviewer should not assume the writer conclusion. Where feasible, freeze a fresh derivation or verifier before comparing against the writer artifacts.

## Scope discipline

Keep one mathematical objective per pull request when possible. Do not mix a theorem rewrite, unrelated refactor, and novelty audit in the same change.

## Style

Prefer plain mathematical statements, exact commands, machine-readable certificates, negative controls, and explicit failure conditions over narrative confidence.
