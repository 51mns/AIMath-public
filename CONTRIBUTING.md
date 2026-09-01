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

Read [`docs/FAILED_ROUTES.md`](docs/FAILED_ROUTES.md). If your proposal resembles a route marked `REFUTED`, `BOUNDED NO-GO`, `BLOCKED`, `INCONCLUSIVE`, or `HOLD`, explain what materially new ingredient changes the old obstruction.

Do not reopen a closed architecture merely by increasing a finite search depth, polynomial degree, ansatz order, or compute budget unless the failure ledger explicitly says that is a meaningful unresolved direction.

## Before opening a pull request

Run:

```bash
python3 scripts/public_release_audit.py .
python3 scripts/verify_public_layout.py .
```

For mathematical changes, include:

- Claim ID;
- old statement;
- proposed statement;
- proof vs computation distinction;
- exact reproduction command;
- changed hashes;
- novelty claim, if any, with primary sources;
- relevant failed-route entry and reopening justification, when applicable.

## When a route fails

Failure is part of the research output. Update `docs/FAILED_ROUTES.md` when the result establishes a reusable blocker, bounded no-go, refutation, or strong inconclusive lesson. Record the exact scope, decisive obstruction, what remains open, and a clear reopening condition.

Do not turn a bounded failure into a claim that an entire mathematical area is impossible.

## Status promotion

A writer does not self-promote their own result to `INDEPENDENTLY_REPRODUCED`. A materially independent review is required.

## Scope discipline

Keep one mathematical objective per pull request when possible. Do not mix a theorem rewrite, unrelated refactor, and novelty audit in the same change.

## Style

Prefer plain mathematical statements, exact commands, machine-readable certificates, and explicit failure conditions over narrative confidence.
