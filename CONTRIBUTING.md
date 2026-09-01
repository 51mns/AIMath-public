# Contributing

Contributions that **disprove** an AIMath claim are as valuable as contributions that extend one.

## Good contributions

- a minimal counterexample;
- a shorter or more transparent proof;
- an independent verifier;
- a clean reproduction on another platform;
- a primary-source literature match;
- a corrected theorem boundary;
- a new exact computation with reproducible inputs and hashes.

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
- novelty claim, if any, with primary sources.

## Status promotion

A writer does not self-promote their own result to `INDEPENDENTLY_REPRODUCED`. A materially independent review is required.

## Scope discipline

Keep one mathematical objective per pull request when possible. Do not mix a theorem rewrite, unrelated refactor, and novelty audit in the same change.

## Style

Prefer plain mathematical statements, exact commands, machine-readable certificates, and explicit failure conditions over narrative confidence.
