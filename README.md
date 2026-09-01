# AIMath Public

**Reproducible AI-assisted mathematics, with proof claims kept separate from computation, novelty, and authorship evidence.**

This repository is the **public, history-clean distribution** of AIMath. It is intentionally not a mirror of the private research workspace.

Public snapshot source: private canonical `main` at `c8e61e0e398f540bc8c5de79663398d689f37473`.

## What AIMath is

AIMath is a long-running mathematics research project in which AI systems are used as active research agents. The project uses a strict evidence discipline:

- exact arithmetic where feasible;
- explicit theorem statements and scope boundaries;
- independent review separated from the writer;
- reproducible scripts, inputs, hashes and negative controls when computation is relevant;
- failed/blocked routes preserved so later researchers do not unknowingly repeat them;
- no promotion from finite evidence to an infinite theorem without proof;
- mathematical validity, reproducibility, novelty, author confirmation and external-frontier movement tracked separately.

## Quick start

Requirements: Git and Python 3.10+ for the standard-library public replays.

```bash
git clone https://github.com/51mns/AIMath-public.git
cd AIMath-public
python3 scripts/public_release_audit.py .
python3 scripts/verify_public_layout.py .
python3 scripts/reproduce_public_claims.py .
```

The public replay suite covers the executable claim packages. Some accepted claims are proof/review packages rather than executable calculations; the repository does not invent computational tests for theorem steps that are genuinely mathematical.

## Start here

1. Read [`docs/RESULTS.md`](docs/RESULTS.md) for the current result index and links to public claim packages.
2. Read [`docs/CONTRIBUTION_TARGETS.md`](docs/CONTRIBUTION_TARGETS.md) for bounded tasks where outside work can currently help.
3. **Before starting a proof route, read [`docs/FAILED_ROUTES.md`](docs/FAILED_ROUTES.md)** so you do not repeat a known blocker or bounded no-go.
4. Read [`docs/EVIDENCE_POLICY.md`](docs/EVIDENCE_POLICY.md) and [`docs/CLAIM_LEVELS.md`](docs/CLAIM_LEVELS.md) before interpreting or extending a claim.
5. Read [`docs/EXPORT_GAPS.md`](docs/EXPORT_GAPS.md) for evidence that is still only substantially/partially exported.
6. Read [`docs/REPRODUCIBILITY.md`](docs/REPRODUCIBILITY.md) for the public reproduction contract.
7. Use [`CONTRIBUTING.md`](CONTRIBUTING.md) if you want to check, refute, extend, or contribute a result.

## Public status model

A result can be mathematically correct while its publication novelty is unknown, or can be a useful theorem without changing an external open-problem frontier. AIMath therefore keeps these questions separate.

| Field | Meaning |
|---|---|
| Mathematical level | How strongly the theorem/certificate has been established inside AIMath |
| Independent reproduction | Whether a separate reviewer rederived or independently checked the claim |
| Reproducibility | Whether executable evidence can be replayed from fixed public bytes where relevant |
| Novelty | Whether primary-source comparison establishes publication novelty or priority |
| External frontier | Whether the result changes a published bound or settles part/all of an external problem |

The public index uses conservative wording by default.

## Current highlighted packages

- **Gyoda 7.6 / 89 collision:** exact counterexample plus four infinite residue classes, with author-confirmation scope kept separate.
- **Fixed-433:** root-energy obstruction, Springborn obstruction, and exact existing-theory identification.
- **B3RCC / antipodal partial cubes:** structural theorem campaign and the independently reproduced all-rank vertex/isometric-dimension bound.
- **Equiangular lines in `R^18`:** one accepted eta=17 59-line spectral branch exclusion; not a solution of `N(18)`.
- **Dittert `n=5`:** one accepted two-zero matching support-class exclusion; not a solution of the full conjecture.
- **Lonely Runner:** generic safe R2 pruning theorem, with its performance no-go recorded separately.
- **AFES:** narrow independently reproduced exact-semantics surface; strict canonical encoding remains open.
- **Thue–Morse:** known-constant rediscovery/certification protocol.
- **Local TP2:** public frozen theorem candidate and finite evidence, explicitly still unproved.

See [`docs/RESULTS.md`](docs/RESULTS.md) for exact claim IDs and boundaries.

## Repository layout

```text
docs/        Results, contribution targets, failed routes, evidence policy, claim levels and safety
research/    Privacy-clean public claim packages
reviews/     Independent public reviews and reproduction evidence
scripts/     Public validation, manifest generation, replay and safety checks
templates/   Standard package skeleton for new claims
```

The private workspace contains additional exploratory branches, coordination records, conversation recovery material and other internal artifacts. Those are **not copied here automatically**. Useful mathematics is exported as a clean claim package rather than by mirroring private history.

## Privacy and release checks

Before a public merge/release, run:

```bash
python3 scripts/public_release_audit.py .
python3 scripts/verify_public_layout.py .
python3 scripts/build_public_manifest.py . --output /tmp/AIMath-public-manifest.json
python3 scripts/reproduce_public_claims.py .
```

`scripts/public_release_audit.py` rejects private-workspace paths, opaque archives, obvious credentials, email addresses, private home paths and private ChatGPT conversation URLs. It is a guardrail, not a substitute for review of Git history/commit metadata and the final pull-request diff.

`PUBLIC_MANIFEST.json` is a metadata pointer rather than a live hash inventory. Generate a current worktree manifest with `scripts/build_public_manifest.py`; immutable tagged releases should preserve the manifest generated from the exact release checkout.

## Public-export policy

See [`docs/PUBLIC_EXPORT_POLICY.md`](docs/PUBLIC_EXPORT_POLICY.md). In particular, raw conversations, raw private correspondence, personal identifiers, credentials, private Git history and unaccepted branch results are not exported for completeness.

## Language

English is the primary language of the public repository so researchers can use it internationally. A short Japanese guide is available in [`README.ja.md`](README.ja.md).

## Licensing

A reusable public project needs an explicit licence. The mathematical/code material has **not** yet been assigned a broad reuse licence. See [`LICENSING.md`](LICENSING.md). Choosing the final licence is intentionally left as an owner decision rather than silently changing legal permissions during a research export.
