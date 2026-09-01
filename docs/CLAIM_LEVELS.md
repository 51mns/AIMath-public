# Claim levels

AIMath uses evidence labels to stop exploratory work from silently becoming a theorem.

## Core levels

### `EXPLORATORY`

A direction, experiment, heuristic, or candidate pattern. It may be useful without being a mathematical claim.

### `COMPUTATIONALLY_VERIFIED`

A bounded computation or finite certificate has been checked exactly for its stated range. It is **not** automatically an infinite theorem.

### `PROOF_CANDIDATE`

A proof or theorem statement has been produced but has not passed the independent reproduction gate.

### `INDEPENDENTLY_REPRODUCED`

A separate reviewer or independent implementation has reproduced the claim against a fixed artifact/commit under the AIMath protocol.

This means the claim is strong **inside the AIMath evidence system**. It does not imply publication novelty.

### `REFUTED` / `CLOSED`

The frozen claim or route was contradicted, or the route was deliberately closed within a stated scope.

## Orthogonal fields

These are tracked separately:

- **Novelty:** known / near-known / not established / potentially new / source-backed conclusion.
- **Author confirmation:** whether an external author explicitly confirmed a claim, and exactly which part.
- **External frontier impact:** whether a result improves a published bound or resolves a published open problem.
- **Reproduction scope:** exact environment, input range, commit/artifact, and negative controls.

## Public wording rule

Never infer:

```text
INDEPENDENTLY_REPRODUCED => new theorem
finite verification => proof for all cases
search found nothing => novel
one excluded branch => whole problem solved
```
