# Public export gap audit

This file tracks **useful canonical research evidence that is still missing from the public distribution**. It is not an inventory of the private repository. Private conversations, raw correspondence, personal data, internal routing records, opaque attachments, private Git history, and unaccepted exploratory branches are intentionally excluded.

Audit basis:

- private canonical `main`: `c8e61e0e398f540bc8c5de79663398d689f37473`
- public export branch: `public-export-completion`

## Completeness scale

- **FULL** — a third party can determine the exact statement/scope, inspect the decisive proof or certificate, run the public executable evidence when relevant, and see what an independent reviewer checked.
- **SUBSTANTIAL** — theorem/proof/review are public, but some large finite classification data or secondary reproduction machinery remains private.
- **PARTIAL** — useful evidence is public, but a material accepted component is still missing.
- **INTENTIONAL_PRIVATE** — the material is deliberately not exported.

## Current status

| Claim / area | State | Public package | Remaining gap |
|---|---|---|---|
| `C-GYODA-89` | **FULL** | `research/gyoda-89/`, `reviews/gyoda-89/` | raw author correspondence remains intentionally private |
| `C-ROOT-433` | **FULL** | `research/fixed-433/`, `reviews/fixed-433/` | none for accepted public claim |
| `C-433-SPRINGBORN-OBSTRUCTION` | **FULL** | `research/433-springborn-obstruction/`, `reviews/433-springborn-obstruction/` | publication novelty still not established |
| `C-433-EXISTING-THEORY-IDENTIFICATION` | **FULL** | `research/433-existing-theory-identification/`, `reviews/433-existing-theory-identification/` | Button full-body literature comparison remains unresolved; novelty not established |
| B3RCC structural claims | **SUBSTANTIAL** | `research/b3rcc-apc/` | complete rank-3 atlas generation data/code and some individual finite certificates are not yet public |
| `C-APC-RANK-R-VERTEX-DIMENSION-BOUND` | **FULL** | `research/b3rcc-apc/APC_ALL_RANK_THEOREM.md`, `reviews/b3rcc-apc/` | historical novelty/priority not established |
| `C-EQUIANGULAR-R18-ETA17-SINGLETON-EXCLUSION` | **FULL** | `research/equiangular-r18-eta17/`, `reviews/equiangular-r18-eta17/` | only eta=17 is accepted; other eta branches are not silently imported |
| `C-DITTERT-N5-Z2-MATCHING-EXCLUSION` | **SUBSTANTIAL** | `research/dittert-n5-z2/`, `reviews/dittert-n5-z2/` | large symbolic permanental-minor verifier is not yet exported; proof and independent review are public |
| `C-LRC-R2-RESIDUAL-CAPACITY` | **SUBSTANTIAL** | `research/lonely-runner-r2/`, `reviews/lonely-runner-r2/` | full independent small-state control implementation and p=71 replay are not yet public |
| `C-AFES-BOUNDED-SEMANTICS` | **FULL for accepted narrow scope** | `research/afes-bounded/`, `reviews/afes-bounded/` | strict canonical encoding remains a separate `PROOF_CANDIDATE` because of the bool/int edge |
| `C-THUE-MORSE-REDISCOVERY` | **FULL** | `research/thue-morse-rediscovery/`, `reviews/thue-morse-rediscovery/` | none for the accepted rediscovery/certification claim |
| `C-LOCAL-TP2` | **PARTIAL / PROOF_CANDIDATE** | `research/local-tp2/` | universal theorem remains unproved; large exact scan generator/replay is not yet a compact public package |

## B3RCC/APC residual export

The public campaign package now records the accepted all-rank theorem, the rank-3/rank-4 boundary, fixed-rank core-mask reduction, carry path, COM/OM and rank-saturation results, APC bridge claims, and the portfolio-HOLD decision.

A future **data/reproduction export** may still add:

- the complete canonical 24-type rank-3 atlas data;
- an independent atlas generator/reviewer implementation;
- the exact rank-4 search certificate catalogue and the three non-partial-cube unlabeled types.

These are useful reproducibility improvements, but their absence must not be confused with absence of the accepted theorem statements or independent mathematical review.

## Dittert residual export

The public package contains the exact support-class statement, the KKT/stationarity proof, the negative-control explanation, and the independent review. A later software export may add a compact exact symbolic verifier that reconstructs the required permanental minors from the `5 x 5` matrix rather than copying private generated logs.

## Lonely Runner residual export

The public package contains the totalized `R2` theorem, proof of safety and `R2<=R1`, the strict p=71 certificate description, the performance no-go boundary, and the independent review. A later software export may add the independent exhaustive small-state tester and the author-compatible p=71 replay after a separate source/licence review of any imported author code assumptions.

## Local TP2 residual export

Local TP2 deliberately remains `PROOF_CANDIDATE`. The public package freezes:

- the exact adjacent-minor statement and terminal endpoint;
- orientation/zero-extension conventions;
- reviewed proof-design invariants;
- finite baseline counts;
- novelty/literature boundary.

The following are still missing or open:

- a universal proof;
- a compact public exact generator for the full denominator-120/140 scans;
- theorem-native progress beyond the already blocked ansatz families documented in `docs/FAILED_ROUTES.md`.

Finite evidence must not be promoted to an infinite theorem.

## Workflow/platform material intentionally not promoted

The private repository contains a larger v0.1.2 reproduction bundle with several accepted sub-gates but an overall non-accepted release state. It is **not** exported as if it were an accepted release. A later dedicated software/privacy audit may publish selected workflow components with their exact partial acceptance state.

This is not a missing mathematical claim package.

## Material that remains private by design

The following are **not export gaps**:

- raw ChatGPT exports or rendered private conversations;
- raw email, DM, or private correspondence;
- personal identifiers, personal email addresses, credentials, tokens, cookies or keys;
- private Git history or private branch topology;
- internal coordination logs whose only purpose is workflow routing;
- opaque private ZIP/archive attachments;
- unmerged writer results presented as canonical;
- raw source PDFs or third-party copyrighted artifacts when citation is sufficient.

When useful mathematics originated on a private historical branch, the public repository should contain a clean claim package reconstructed from the fixed mathematical evidence, not the private branch history.

## Completion rule

A mathematical public export is complete only when a reader can tell, from public material alone:

1. the exact statement and scope;
2. what is proof and what is finite computation;
3. the decisive proof/certificate;
4. how executable evidence is reproduced when relevant;
5. the durable private-source commit identifiers needed for provenance without exposing private branch history;
6. what the independent reviewer checked;
7. the novelty/literature status;
8. nearby failed routes or explicit open boundaries.
