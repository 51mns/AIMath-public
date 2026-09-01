# Failed routes and research memory

AIMath records failed, blocked, inconclusive, and refuted routes because a failed approach is still reusable research knowledge. Before starting a new proof attempt, check this file so that you do not unknowingly repeat an already closed architecture.

This public ledger is a privacy-safe summary exported from the private canonical workspace at `c8e61e0e398f540bc8c5de79663398d689f37473`. It intentionally omits private conversations, correspondence, and coordination logs.

## Status vocabulary

- **REFUTED** — the frozen claim or route is contradicted.
- **BOUNDED NO-GO** — a precisely defined family/architecture is impossible in its stated scope; nearby different approaches may remain open.
- **BLOCKED** — the route reached a specific unresolved gap and cannot currently justify the target theorem.
- **INCONCLUSIVE** — the experiment or structural reduction did not decide the target.
- **HOLD / CLOSED IN SCOPE** — do not spend another lane repeating the same architecture unless a materially new hypothesis, theorem-native structure, external idea, or genuinely different proof mechanism appears.

## Local TP2

**Target claim:** `C-LOCAL-TP2` remains `PROOF_CANDIDATE`. No counterexample to Local TP2 itself is established.

The following proof-design routes have already been investigated:

| Route | Outcome | What failed / what remains |
|---|---|---|
| QW3 individual-sign route | `BLOCKED_QW3_SIGN_GAP` | The fixed-stencil QW3 identity is valid, but the required all-depth interior/boundary sign was not proved. Finite depth checks do not close the gap. |
| all-pair quotient diagnostic | `LOWER_TP2_RESTATEMENT_RISK` | The lower-level condition risked restating the original TP2 difficulty rather than creating an easier invariant. |
| quotient-TP2 structural gate | `ACCEPT_INCONCLUSIVE` | The structural reduction did not yield a universal proof or counterexample. |
| far-minor `FM-REC2-AFFINE` ansatz | `ACCEPT_BOUNDED_NO_GO` | Exact inconsistency for this frozen recurrence/affine family only. |
| far-minor `FM-PAIRKERNEL-SYMD2` ansatz | `ACCEPT_BOUNDED_NO_GO` | Exact inconsistency for this frozen pair-kernel symmetric-degree-2 family only. |

The private canonical roadmap marks the recorded quotient/QW3/far-minor architecture **CLOSED in its recorded scopes** and incremental Local-TP2 proof investment **HOLD**.

Do **not** simply restart these older architectures without a materially new ingredient:

- Candidate-B / direct Route-W;
- fixed-local wedge / Jacobi;
- F-only descent;
- QW3 individual-sign propagation;
- quotient structural reduction;
- higher-order or larger finite-depth variants of the two frozen far-minor ansatz families.

**Reopen condition:** a materially new theorem-native structure, an external mathematical idea, or a genuinely different proof architecture. A successful new proof still requires independent review before promotion.

## Fixed-433 root-energy growth route

**Route:** attempt to prove a growth statement of the form `g(m) -> infinity` and use it as the main obstruction.

**Outcome:** `REFUTED` as an AIMath-internal subroute.

The independently reproduced fixed-433 family gives an infinite sequence with noncanonical root energy at most `4`. Therefore the blanket growth route cannot be used as proposed.

**Important boundary:** this does **not** close root-energy methods as a whole. A different root-energy theorem that is compatible with the fixed-433 family may still be useful.

Public reproduction:

```bash
python3 research/fixed-433/reproduce.py
```

## AIMath v0.1.1 reproducibility route

**Claim:** `C-REPRO-V011`

**Outcome:** `BLOCKED_MISSING_ARTIFACT`.

The reported v0.1.1 test/reproduction claim could not be independently accepted because the canonical artifact bytes were unavailable to the acceptance review. A report of passing tests is not a substitute for the fixed artifact, hash, clean replay, and mutation checks.

**Replacement route:** the private project moved to the v0.1.2 successor path rather than treating v0.1.1 as accepted.

**Lesson:** never promote a reproducibility claim when the exact artifact under review cannot itself be retrieved and hashed.

## AFES strict canonical encoding

**Claim:** `C-AFES-STRICT-CANONICAL-ENCODING`

**Outcome:** still `PROOF_CANDIDATE` because of a concrete scalar-typing defect.

Python `bool` is a subclass of `int`, so JSON `true/false` values can enter rational-pair normalisation where strict JSON-integer typing is intended. This prevents the stronger claim that every accepted scalar payload has a unique strict canonical encoding.

**Do not repeat:** another broad AFES proof pass without first repairing the exact scalar boundary.

**Reopen/promotion condition:** enforce exact integer typing at every rational-valued entry point, add boolean negative controls, and independently re-review that narrow repair surface.

## Thue–Morse "new constant" route

**Claim:** `C-THUE-MORSE-REDISCOVERY`

**Outcome:** the candidate is exactly the known Thue–Morse constant.

The rediscovery/certification experiment is useful evidence about the workflow, but the route **must not** be presented as discovery of a new mathematical constant.

**Lesson:** relation-search failure or unfamiliar decimal output is not novelty evidence. Exact known-object identification and primary-source novelty checks are separate gates.

## Lonely Runner scaling/performance route

**Claim:** `C-LRC-R2-RESIDUAL-CAPACITY` remains a valid independently reproduced pruning theorem.

**Closed route:** the associated scaling/performance campaign did not improve the frozen benchmark and was therefore closed as a performance direction.

**Boundary:** closing the performance route does not invalidate the pruning theorem itself and does not imply an external Lonely Runner frontier improvement.

## How to add a failed route

When a route fails, record at least:

1. the exact target claim;
2. the frozen architecture or hypothesis that was tested;
3. whether the outcome is refutation, bounded no-go, blocker, or inconclusive;
4. the smallest decisive obstruction/counterexample;
5. what nearby territory remains open;
6. the condition under which reopening the route would be justified;
7. exact reproduction commands/certificates when computation is involved.

A failed route should be narrow enough that it does not accidentally declare a whole research area dead.
