# Public export gap audit

This file tracks useful research evidence that exists in the private canonical AIMath workspace but has not yet been exported as a self-contained public package.

It is intentionally **not** a list of everything in the private repository. Private conversations, raw correspondence, personal data, internal coordination logs, and unaccepted exploratory artifacts are excluded on purpose.

Audit basis:

- private canonical `main`: `c8e61e0e398f540bc8c5de79663398d689f37473`
- public baseline inspected before this audit: `a69805ac5b6afd82928c734ed5af4ae1fe03ed68`

## Public-package completeness scale

- **FULL** — statement, proof/certificate, reproduction path, provenance, and independent review are publicly usable.
- **INDEX_ONLY** — the result appears in `docs/RESULTS.md`, but the decisive proof/certificate/review package is not public.
- **PARTIAL** — useful pieces are public, but a contributor still needs private evidence to reconstruct the accepted or frozen research state.
- **MISSING_FROM_INDEX** — a canonical private claim is not even represented in the public result index.
- **INTENTIONAL_PRIVATE** — material should not be exported merely for completeness.

## Current headline

At this snapshot, `C-ROOT-433` is the only major canonical mathematical claim with a substantially self-contained public proof/reproduction/review package under `research/fixed-433/` and `reviews/fixed-433/`.

Most other claims in `docs/RESULTS.md` are currently discovery/index entries rather than complete public research packages.

## P0 — claims already listed publicly but missing their full evidence package

| Claim / area | Public state | Private evidence known to exist | Public export needed |
|---|---|---|---|
| `C-GYODA-89` | `INDEX_ONLY` | exact integer verifier, replay/tests, independent audit and scope records | frozen statement, exact replay, independent audit, provenance; keep raw correspondence private |
| `C-433-SPRINGBORN-OBSTRUCTION` | `INDEX_ONLY` | full writer proof/reproduction/source audit and independent review/verifier | self-contained writer + reviewer package |
| `C-433-EXISTING-THEORY-IDENTIFICATION` | `INDEX_ONLY` | definitions, proof/identification, literature map, novelty audit, exact verifier, independent review | self-contained proof/replay/review + literature status |
| `C-B3RCC-1` | `INDEX_ONLY` | fixed universal proof, independent derivation, finite adversarial controls | statement/proof/independent review/control package |
| `C-B3RCC-RANK-R-CARRY-PATH` | `INDEX_ONLY` | fixed writer and independent verifier/review | proof + exact finite controls + review |
| `C-B3RCC-RANK3-COMPONENT-ATLAS` | `INDEX_ONLY` | exact 24-type atlas, independent reconstruction, controls | atlas data/code, theorem proof, independent review |
| `C-B3RCC-RANK4-PARTIAL-CUBE-BOUNDARY` | `INDEX_ONLY` | explicit counterexample, independent partial-cube obstruction verifier | exact witness + two independent obstruction checks |
| `C-B3RCC-RANK-R-CORE-MASK-REDUCTION` | `INDEX_ONLY` | fixed-rank reduction proof and supporting evidence | theorem/proof/reviewer package |
| `C-B3RCC-RANK3-INTRINSIC-CHARACTERIZATION` | `INDEX_ONLY` | fixed iff proof and independent reconstruction | theorem/proof/reviewer package |
| `C-B3RCC-RANK3-COM-OM-CLASSIFICATION` | `INDEX_ONLY` | atlas classification and independent review | classification data/proof/review |
| `C-B3RCC-RANK-SATURATION-RIGIDITY` | `INDEX_ONLY` | all-m proof independently rederived | theorem/proof/review |
| `C-APC-RANK4-VERTEX-DIMENSION-BOUND` | `INDEX_ONLY` | universal proof, finite controls, independent derivation | proof/review/controls |
| `C-B3RCC-MOVE-RANK5-IDIM7-BOUND` | `INDEX_ONLY` | exact corollary proof and independent review | proof/review |
| `C-APC-RANK-R-VERTEX-DIMENSION-BOUND` | `INDEX_ONLY` | all-rank structural proof, independent Phase-1/final review, supporting-control hashes | full theorem package; high priority because it is a major general result |
| `C-EQUIANGULAR-R18-ETA17-SINGLETON-EXCLUSION` | `INDEX_ONLY` | fixed writer proof/artifacts plus independent Phase-1 and final review | exact spectral/deck proof, verifier/certificate if applicable, independent review |
| `C-DITTERT-N5-Z2-MATCHING-EXCLUSION` | `INDEX_ONLY` | fixed KKT/stationarity proof and independent reviews | self-contained theorem/proof/review package |
| `C-LRC-R2-RESIDUAL-CAPACITY` | `INDEX_ONLY` | structural proof, exact controls, p=71 certificate, independent review | theorem definition, safe-prune proof, controls/certificate/review |
| `C-AFES-BOUNDED-SEMANTICS` | `INDEX_ONLY` | repaired implementation/evidence and narrow independent re-review | exact accepted semantic surface, executable controls and review |
| `C-THUE-MORSE-REDISCOVERY` | `INDEX_ONLY` | exact dyadic certificate, known-object identification and independent review | certificate/replay/review with explicit non-novelty boundary |
| `C-LOCAL-TP2` | `PARTIAL` | frozen statement, invariants, novelty audit, exact finite scans and historical reproduction bundles | exact target statement + finite baseline + novelty/literature map; must remain `PROOF_CANDIDATE` |

## P0 — canonical claims missing from the public result index

The private claims ledger contains independently reproduced claims that are not currently represented as their own public result entries, including at least:

- `C-B3RCC-MOVE-RANK4-APC-BARRIER`
- `C-B3RCC-MOVE-RANK5-APC-TARGET-REDUCTION`
- `C-B3RCC-CORE-MASK-COMPLEMENT-PAIRING`

These should be added either as explicit result entries or as clearly named subclaims inside a complete B3RCC/APC public campaign package. Their scope qualifications are important; none should be advertised as solving a general APC/OM/Las-Vergnas problem.

## P1 — research memory that prevents duplicated work

### B3RCC / APC campaign closeout

The private repository has a campaign closeout report that records:

- which structural theorems were accepted;
- how the programme moved from finite structure to a general APC theorem;
- why the theme was placed on portfolio HOLD despite mathematical success;
- which next-rank/classification directions should not be restarted by default;
- explicit conditions that would justify reopening the campaign;
- fixed writer/reviewer commit pointers.

A privacy-safe public version would save contributors from extending the programme by rank simply because its successful history is visible.

### Literature and novelty work

For some lanes, private packages already contain `NOVELTY_AUDIT.md`, `LITERATURE_MAP.md`, source-normalisation notes, and unresolved-source gaps. Publicly saying only `NOVELTY_NOT_ESTABLISHED` is insufficient: a new contributor cannot tell which primary sources were already checked and may repeat the same search.

Priority examples:

- fixed-433 / Springborn / existing-theory identification;
- Local TP2;
- APC all-rank theorem.

Only source-backed, redistribution-safe summaries should be exported; inaccessible or unverified source claims must stay labelled unresolved.

### Evidence policy

The private `docs/EVIDENCE_POLICY.md` contains reusable rules not fully represented by the current public docs, including durable fixed-commit identity, environment/dependency recording, implementation-independence disclosure, and immutable-artifact handling.

A public adaptation should preserve these research-quality rules while removing private-release-specific details that do not apply to the public repository.

### Open contribution targets

The private roadmap/current status says much more precisely what remains open and what is on HOLD. The public repository currently lacks a concise `OPEN_PROBLEMS.md` / `CONTRIBUTION_TARGETS.md` telling an external researcher:

- the exact unresolved subproblem;
- accepted prerequisites;
- already-failed routes;
- what would count as progress;
- which result would need independent review.

Without this, outsiders can read the archive but cannot easily join the frontier.

## P2 — platform/reproducibility material

The private repository contains a substantial `reproduce/v0.1.2/minimal-g9-g13/` evidence bundle with dependency/runtime locking, environment contract, clean replay, inventory/hashes, mutation controls and CI evidence.

This may be useful to people adopting the AIMath workflow, but it should be exported only after a separate privacy/provenance review and with its exact acceptance status preserved. Partial gate success must not be rewritten as overall release acceptance.

## Material that should remain private by default

These are **not export gaps**:

- raw ChatGPT exports or private conversation recovery bundles;
- raw email/DM/correspondence;
- personal identifiers or credentials;
- private Git history;
- internal coordination/chat routing records when they add no mathematical evidence;
- opaque private attachments;
- unmerged writer branches presented as if canonical;
- exploratory branch results whose current claim level has not been accepted into the canonical ledger.

When a useful theorem lives only on a historical/fixed branch, export a clean self-contained public claim package from the fixed writer/reviewer commits rather than exposing the private branch history.

## Recommended export order

1. `C-433-SPRINGBORN-OBSTRUCTION` and `C-433-EXISTING-THEORY-IDENTIFICATION` — complete evidence is already on private `main`, making these comparatively low-risk exports.
2. `C-GYODA-89` — highly understandable flagship result; export exact mathematics while excluding raw correspondence/chat material.
3. `C-LOCAL-TP2` frozen target + exact finite baseline + literature/novelty state — important for preventing duplicated failed proof work.
4. `C-APC-RANK-R-VERTEX-DIMENSION-BOUND` plus the B3RCC/APC campaign closeout — strongest general theorem/campaign map.
5. Equiangular R18 and Dittert n=5 accepted packages — externally recognisable problems with fixed independent reviews.
6. Remaining B3RCC, Lonely Runner, AFES and Thue–Morse packages.
7. v0.1.2 workflow/reproducibility material after separate software/privacy audit.

## Completion rule

A claim should not be considered fully exported merely because it appears in `docs/RESULTS.md`.

For a mathematical claim whose private acceptance relies on proof, computation, or independent review, the public export is complete only when a third party can determine from the public repository alone:

1. the exact frozen statement and scope;
2. the mathematical proof or decisive certificate;
3. the finite/universal boundary;
4. how to reproduce executable evidence;
5. exact durable provenance/hashes where relevant;
6. what the independent reviewer actually checked;
7. the current novelty/literature status;
8. nearby failed routes or known blockers.
