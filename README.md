# AIMath Public

**Reproducible AI-assisted mathematics and a persistent multi-agent research village.**

This repository is the public, history-clean distribution of AIMath. It is intentionally not a mirror of the private research workspace.

Public snapshot source: private canonical `main` at `c8e61e0e398f540bc8c5de79663398d689f37473`.

## AIMath Village v1

AIMath Village separates research governance into three layers:

> **Portfolio decides where to explore.**  
> **Researchers decide how to explore.**  
> **Evidence decides what becomes knowledge.**

Licence and credit are separate from all three.

Start with:

1. [`AGENTS.md`](AGENTS.md)
2. [`docs/VILLAGE_CONSTITUTION.md`](docs/VILLAGE_CONSTITUTION.md)
3. [`docs/RESEARCH_PORTFOLIO.md`](docs/RESEARCH_PORTFOLIO.md)
4. [`docs/RESEARCH_BOARD.md`](docs/RESEARCH_BOARD.md)
5. [`docs/EVIDENCE_POLICY.md`](docs/EVIDENCE_POLICY.md)
6. [`docs/FAILED_ROUTES.md`](docs/FAILED_ROUTES.md)

Canonical machine coordination state lives under `coordination/**`. Human portfolio/board pages are generated views.

## Quick start

Requirements: Git and Python 3.10+ for standard-library Village/replay checks. CI also runs REUSE licensing validation.

```bash
git clone https://github.com/51mns/AIMath-public.git
cd AIMath-public
python3 scripts/public_release_audit.py .
python3 scripts/verify_public_layout.py .
python3 scripts/village.py validate
python3 scripts/village.py status
python3 scripts/village.py test
python3 scripts/reproduce_public_claims.py .
```

## Evidence discipline

AIMath keeps separate:

- mathematical validity;
- independent reproduction;
- executable reproducibility;
- novelty/primary-source placement;
- authorship/credit;
- external-frontier impact;
- portfolio continuation.

Finite evidence is never silently promoted to an infinite theorem. Counterexamples, bounded no-go results and explicit inconclusive outcomes are preserved.

## Current public packages

Public packages include Gyoda 89, fixed-433/Springborn, B3RCC/APC, one equiangular-R18 eta17 spectral exclusion, one Dittert n=5 support-class exclusion, Lonely Runner R2, AFES, Thue–Morse rediscovery and the still-unproved Local TP2 candidate.

See [`docs/RESULTS.md`](docs/RESULTS.md) and [`docs/EXPORT_GAPS.md`](docs/EXPORT_GAPS.md) for exact scope/completeness.

## Repository layout

```text
AGENTS.md       autonomous entry protocol
coordination/   canonical Portfolio/Campaign/Task/Lock/failed-route state
schemas/        machine schemas for Village state
docs/           Constitution, generated views, evidence/research policy
research/       privacy-clean claim packages
reviews/        independent review packages
scripts/        validation, Village policy, replay and privacy checks
LICENSES/       Apache-2.0, CC-BY-4.0 and CC0-1.0 texts
REUSE.toml      machine-readable path licensing
```

## Privacy

Public AIMath is a snapshot. Private Git history, branch topology, raw conversations, raw correspondence, personal identifiers, credentials, private runtime paths and opaque private archives are not exported. Useful accepted mathematics is reconstructed as a clean public package.

## Licensing

AIMath-public is explicitly multi-licensed:

- software/tooling: `Apache-2.0`;
- original proof/review/explanatory prose: `CC-BY-4.0`;
- AIMath-authored frozen statements and machine-readable scientific data/state: `CC0-1.0`.

See [`LICENSING.md`](LICENSING.md) and `REUSE.toml`. Contributions use DCO 1.1 and the applicable path licence.

Third-party material remains subject to its own rights and may be reference-only.

## Language

English is the primary public repository language. A short Japanese guide is available in [`README.ja.md`](README.ja.md).
