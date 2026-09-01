# Contributing

Contributions that **disprove** an AIMath claim are as valuable as contributions that extend one.

## Before starting

Read:

1. `AGENTS.md`
2. `docs/VILLAGE_CONSTITUTION.md`
3. `docs/RESEARCH_PORTFOLIO.md`
4. `docs/CONTRIBUTION_TARGETS.md`
5. `docs/FAILED_ROUTES.md`
6. `docs/EVIDENCE_POLICY.md`
7. the exact public claim package you intend to use.

For coordinated exclusive work, choose an approved derived-READY Task and acquire its lock before claiming ownership.

## Good contributions

- a minimal counterexample;
- a shorter or more transparent proof;
- an independent verifier;
- a clean reproduction on another platform;
- a primary-source literature match;
- a corrected theorem boundary;
- a reproducible exact computation;
- a reusable failed-route record;
- a campaign/task/scout proposal with a real new ingredient and kill condition.

## DCO 1.1

AIMath uses the Developer Certificate of Origin 1.1. Read the canonical certificate at:

`https://developercertificate.org/`

Every contribution commit must include a sign-off trailer:

```text
Signed-off-by: <name or pseudonymous Git identity> <the same email used by the commit author>
```

The sign-off certifies that you have the right to submit the contribution under the applicable project licence.

DCO sign-offs become permanent public Git history. GitHub noreply email addresses are accepted and recommended if you do not want to expose a personal email address.

The responsible submitter is the GitHub actor. AI systems may assist with proof search, drafting, code or review, but the AI does not sign the DCO. Record material AI assistance as provenance when useful.

## Inbound equals applicable outbound licence

AIMath is path-licensed.

Unless explicitly and validly stated otherwise before submission, an intentionally submitted contribution is offered under the licence assigned to its target path/file by SPDX/`REUSE.toml` metadata.

- software/tooling paths: normally `Apache-2.0`;
- proof/review/documentation prose: normally `CC-BY-4.0`;
- AIMath-authored frozen statements and machine-readable scientific state/data: normally `CC0-1.0`.

No copyright assignment to AIMath is required.

Do not submit third-party material unless you have the right to redistribute it under the indicated terms. Prefer citation/reference-only treatment when rights are unclear.

## Before opening a PR

Run:

```bash
python3 scripts/public_release_audit.py .
python3 scripts/verify_public_layout.py .
python3 scripts/village.py validate
python3 scripts/village.py test
python3 scripts/reproduce_public_claims.py .
```

CI additionally runs official `reuse lint` and PR-specific DCO/governance/admission checks.

## Mathematical changes

Include:

- Claim/Task/Campaign ID as applicable;
- exact old and proposed statement;
- proof vs finite-computation distinction;
- reproduction command and hashes when executable evidence is load-bearing;
- independent-review status;
- novelty claim only with appropriate primary-source support;
- failed-route/reopen justification where relevant.

A writer does not self-promote to `INDEPENDENTLY_REPRODUCED`.

## Governance changes

Do not mix ordinary research and protected governance changes in one PR. Put proposed strategic changes under `coordination/proposals/` or open a dedicated governance PR.

## Lock-only PRs

A lock acquisition PR must change only the exact required files under `coordination/locks/**`. CI validates the base state, capacity, collision keys, actor limit and task readiness. Ownership begins only when the lock PR is merged.

## When a route fails

Failure is research output. Record exact scope, decisive obstruction, remaining open territory and reopening condition. Do not turn a bounded failure into a universal impossibility statement.
