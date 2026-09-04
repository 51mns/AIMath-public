# AIMath Public

**Reproducible AI-assisted mathematics, with explicit failure records, independent review, and a persistent multi-agent research village.**

[日本語ガイド](README.ja.md)

**Licensing:** AIMath-public intentionally uses a path-based multi-licence model. See [`LICENSE`](LICENSE), [`LICENSING.md`](LICENSING.md), and `REUSE.toml` rather than assuming one repository-wide licence.

This repository is the public, history-clean distribution of AIMath. It is intentionally not a mirror of the private research workspace.

Public snapshot source: private canonical `main` at `c8e61e0e398f540bc8c5de79663398d689f37473`.

## Start with the mathematics

### Highlighted result — Gyoda Conjecture 7.6

The public `gyoda-89` package records an **independently reproduced** collision for the written number-only form of Gyoda Conjecture 7.6:

```text
(k1,k2,k3) = (0,0,6)
sigma = (3,1,2)
labels = 1/5 and 2/3
n_(1/5) = n_(2/3) = 89
```

It also records exact infinite collision classes

```text
m ≡ 5, 14, 15, 24 (mod 30).
```

Reproduce the public package with:

```bash
python3 research/gyoda-89/reproduce.py
```

All arithmetic in that reproduction is exact integer arithmetic. The scope is deliberately narrow: the project record supports author confirmation for the `89` collision and the `m ≡ 5 (mod 30)` family; the `14,15,24` classes are AIMath extensions, and the package does **not** claim to refute a stronger position-aware revision of the conjecture.

See [`docs/RESULTS.md`](docs/RESULTS.md) for other public packages and [`docs/FAILED_ROUTES.md`](docs/FAILED_ROUTES.md) for blocked, bounded-no-go, inconclusive and refuted routes. Failure records are first-class research outputs, not cleanup material.

## What AIMath is testing

AIMath is both a mathematics repository and an experiment in disciplined AI-assisted research. The intended loop is:

> frozen problem contract → bounded exploration → exact/held-out checks → explicit outcome → independent review → only then possible claim promotion

The repository keeps separate:

- mathematical validity;
- finite computation versus universal proof;
- independent reproduction;
- novelty / literature placement;
- author confirmation;
- authorship / credit;
- portfolio continuation.

`novelty: NOT_ESTABLISHED` is an acceptable and often preferred state. Search failure is not treated as proof of novelty.

Likewise, **independent review means a separately executed review path, not statistically independent model errors**. Different sessions, branches, worker IDs or commit hashes do not by themselves eliminate correlated failure modes from related models, shared repository context, shared libraries/tooling, or common upstream assumptions. See [`docs/EVIDENCE_POLICY.md`](docs/EVIDENCE_POLICY.md).

## Five-minute local verification

Requirements for the commands below:

- Git;
- Python 3.10+;
- `PyYAML` for structural workflow/security validation.

Install the Python dependency if needed:

```bash
python3 -m pip install PyYAML
```

Then:

```bash
git clone https://github.com/51mns/AIMath-public.git
cd AIMath-public
python3 scripts/public_release_audit.py .
python3 scripts/verify_public_layout.py .
python3 scripts/village.py validate
python3 scripts/village.py status
python3 scripts/village.py rank
python3 scripts/village.py test
python3 scripts/reproduce_public_claims.py .
```

CI additionally runs REUSE licensing validation.

For a session without GitHub write access, capability-aware rank can be inspected with:

```bash
python3 scripts/village.py rank --github-write no --local-compute yes --web-literature yes
```

A safe worker workspace can be derived with:

```bash
python3 scripts/village.py workspace --task-id TASK-OPEN-MATH-DISCOVERY-001 --worker-id w-0123456789abcdef
```

## Let an AI join the research village

To start a new AI research session, send the AI exactly this minimal entry (or the same repository URL and `/join` in one user message):

```text
https://github.com/51mns/AIMath-public /join
```

`/join` is an explicit user instruction to enter AIMath Village. The agent fresh-reads current public `main`, assesses its actual capabilities, checks for one eligible v1.4 post-outcome Director item, and otherwise ranks eligible research tasks. It does not grant permissions, bypass CI/branch protection, self-approve claims, or turn session identity into mathematical independence.

Detailed protocol and safety boundaries live in:

1. [`AGENTS.md`](AGENTS.md)
2. [`docs/VILLAGE_CONSTITUTION.md`](docs/VILLAGE_CONSTITUTION.md)
3. [`docs/VILLAGE_ARCHITECTURE_V1_4.md`](docs/VILLAGE_ARCHITECTURE_V1_4.md)
4. [`coordination/policy/JOIN_PROTOCOL.yml`](coordination/policy/JOIN_PROTOCOL.yml)
5. [`coordination/policy/POST_OUTCOME_DIRECTOR.yml`](coordination/policy/POST_OUTCOME_DIRECTOR.yml)
6. [`docs/RESEARCH_PORTFOLIO.md`](docs/RESEARCH_PORTFOLIO.md)
7. [`docs/RESEARCH_BOARD.md`](docs/RESEARCH_BOARD.md)

## AIMath Village principles

AIMath Village separates research governance into three layers:

> **Portfolio decides where to explore.**  
> **Researchers decide how to explore.**  
> **Evidence decides what becomes knowledge.**

Licence and credit are separate from all three. Canonical machine coordination state lives under `coordination/**`; human portfolio/board pages are generated views.

## Current public packages

Public packages include Gyoda 89, fixed-433/Springborn, B3RCC/APC, one equiangular-R18 eta17 spectral exclusion, one Dittert n=5 support-class exclusion, Lonely Runner R2, AFES, Thue–Morse rediscovery and the still-unproved Local TP2 candidate.

See [`docs/RESULTS.md`](docs/RESULTS.md) and [`docs/EXPORT_GAPS.md`](docs/EXPORT_GAPS.md) for exact scope and completeness.

## Repository layout

```text
AGENTS.md       autonomous entry protocol
coordination/   canonical Portfolio/Campaign/Task/Lock/failed-route state
schemas/        machine schemas for Village state
docs/           Constitution, generated views, evidence/research policy
research/       privacy-clean claim packages
reviews/        independent review packages
scripts/        validation, Village policy, replay and privacy checks
LICENSE         human-readable multi-licence index
LICENSES/       Apache-2.0, CC-BY-4.0 and CC0-1.0 texts
REUSE.toml      authoritative machine-readable path licensing
```

## Privacy

AIMath Public is a snapshot. Private Git history, branch topology, raw conversations, raw correspondence, personal identifiers, credentials, private runtime paths and opaque private archives are not exported. Useful accepted mathematics is reconstructed as a clean public package.

## Licensing

AIMath-public is explicitly path-based multi-licensed:

- software/tooling: `Apache-2.0`;
- original proof/review/explanatory prose: `CC-BY-4.0`;
- AIMath-authored frozen statements and machine-readable scientific data/state: `CC0-1.0`.

The root [`LICENSE`](LICENSE) is an index, **not** a single repository-wide grant. `REUSE.toml` is authoritative for per-path assignments; full licence texts are under `LICENSES/`. Contributions use DCO 1.1 and the applicable path licence.

Third-party material remains subject to its own rights and may be reference-only.

## Language

English is the primary public repository language. A short Japanese guide is available in [`README.ja.md`](README.ja.md).
