# AIMath Public

**Reproducible AI-assisted mathematics, with proof claims kept separate from computation, novelty, and authorship evidence.**

This repository is the **public, history-clean distribution** of AIMath. It is intentionally not a mirror of the private research workspace.

Public snapshot source: private canonical `main` at `c8e61e0e398f540bc8c5de79663398d689f37473`.

## What AIMath is

AIMath is a long-running mathematics research project in which AI systems are used as active research agents. The project is built around a strict evidence discipline:

- exact arithmetic where feasible;
- explicit statements and claim boundaries;
- independent review separated from the writer;
- reproducible scripts, inputs, outputs, hashes, and negative controls;
- failed/blocked routes are preserved so later researchers do not unknowingly repeat them;
- no promotion from finite evidence to an infinite theorem without proof;
- mathematical validity, reproduction, novelty, and author confirmation are tracked separately.

## Quick start

Requirements: Git and Python 3.10+; the first public replay uses only the Python standard library.

```bash
git clone https://github.com/51mns/AIMath-public.git
cd AIMath-public
python3 research/fixed-433/reproduce.py
```

For a full public-distribution check:

```bash
python3 scripts/public_release_audit.py .
python3 scripts/verify_public_layout.py .
```

The same checks run automatically on pushes and pull requests through GitHub Actions.

## Start here

1. Read [`docs/RESULTS.md`](docs/RESULTS.md) for the current public result index.
2. **Before starting a new proof route, read [`docs/FAILED_ROUTES.md`](docs/FAILED_ROUTES.md)** so that you do not repeat a known blocker or bounded no-go.
3. Read [`docs/CLAIM_LEVELS.md`](docs/CLAIM_LEVELS.md) before interpreting a status label.
4. Read [`docs/REPRODUCIBILITY.md`](docs/REPRODUCIBILITY.md) to reproduce a claim package.
5. Use [`CONTRIBUTING.md`](CONTRIBUTING.md) if you want to check, refute, extend, or contribute a result.
6. Report a mathematical issue with the **Math review** issue template, and a failed replay with the **Reproduction failure** template.

## Public status model

A claim may be mathematically strong while its publication novelty remains unknown. AIMath therefore never treats these as the same question.

| Field | Meaning |
|---|---|
| Mathematical level | How strongly the theorem/certificate has been established inside AIMath |
| Independent reproduction | Whether a separate reviewer reproduced it |
| Novelty | Whether primary-source literature comparison has established publication novelty |
| External frontier | Whether the result actually changes a known published bound/problem frontier |

The public index uses conservative wording by default.

## Repository layout

```text
docs/        Results, failed routes, claim levels, reproducibility, safety and provenance
research/    Public claim packages only
reviews/     Independent public reviews and reproduction evidence
scripts/     Public validation and safety checks
templates/   Standard package skeleton for new claims
```

The private workspace contains additional exploratory branches, coordination records, conversation recovery material, and other internal artifacts. Those are **not** copied here automatically. Privacy-safe summaries of important failed/blocked research routes are exported to `docs/FAILED_ROUTES.md` when they are useful for preventing duplicated work.

## One-command safety check

```bash
python3 scripts/public_release_audit.py .
python3 scripts/verify_public_layout.py .
```

Both commands must pass before a public release.

## Current public-export policy

The initial public edition prioritizes a small number of well-bounded, independently reproduced results. Exploratory work and proof candidates may be listed, but must be visibly separated from verified claims.

See [`docs/PUBLIC_EXPORT_POLICY.md`](docs/PUBLIC_EXPORT_POLICY.md).

For the first GitHub publication, follow [`docs/PUBLISHING.md`](docs/PUBLISHING.md).

## Language

English is the primary language of the public repository so that researchers can use it internationally. A short Japanese guide is available in [`README.ja.md`](README.ja.md).

## Licensing

A reusable public project needs an explicit licence. The mathematical/code material has **not** been assigned a licence in this bootstrap snapshot. See [`LICENSING.md`](LICENSING.md) for the recommended split and the one remaining owner decision before broad reuse.
