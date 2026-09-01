# Local TP2 proof-design invariants

The canonical theorem remains exactly the adjacent determinant inequality in `STATEMENT.md`. The items below are historical proof-design strengthenings/fallbacks, not accepted theorem statements.

## Candidate A — determinant edge growth

Schematic strengthening:

```text
F_child(n) > F_parent(n)
```

across parent/child vertices, including support growth.

Status: **UNPROVED STRENGTHENING**. It is strictly stronger than Local TP2. Failure of edge growth would not refute the target determinant positivity.

## Candidate B — predecessor-guard MLR cone

Retains predecessor state such as

```text
P = C-Y
Q = C-X
S = U-C
D = V-U
```

plus cross-product guards and support/terminal data.

Status: **UNPROVED STRENGTHENING**. Mutation closure was not proved.

## Route W — finite mutation-closed invariant search

A weaker design strategy was to derive successor determinants from exact mutation formulas while retaining only needed sign functionals.

Status: **PROOF-DESIGN FALLBACK / NOT A THEOREM**.

A valid success would need a finite mutation-closed obligation set implying the frozen target, including the terminal determinant. State explosion is a route obstruction, not a theorem failure.

## Current campaign boundary

Later work moved beyond these early designs into QW3/quotient/far-minor architectures. Their accepted blocked/no-go outcomes are summarized in `../../docs/FAILED_ROUTES.md`.

Do not silently promote any historical strengthening into the Local TP2 statement.
