# Continuation Gate

A campaign does not continue merely because another case exists or because the previous task succeeded.

## Required triggers

Submit a Continuation Memo when any of these occur:

- the initial lane budget is exhausted;
- a major claim, counterexample, or structural reduction is fixed;
- two or more meaningful routes have closed;
- the next rank/dimension/parameter is proposed;
- `max_active_lanes` would increase;
- a `HOLD` campaign would reopen;
- the external frontier materially changes.

## Memo fields

Canonical memos use `continuation.schema.json` and record:

- campaign ID and trigger;
- assets gained;
- failed routes;
- external progress;
- information gain;
- transfer value;
- explicit `do_not_continue_for` checks;
- recommended decision: `CONTINUE`, `HOLD`, `CLOSE`, or `PIVOT`.

A recommendation is not the decision. Human Portfolio governance records the decision in the campaign `decisions/` directory.

## Proportional strategy review

Normal continuation:

```text
memo -> human maintainer decision
```

Independent strategy critique is additionally required for:

- `HOLD -> ACTIVE`;
- `max_active_lanes > 3`;
- high-cost or long-running computation;
- material project-wide reprioritization;
- long-term concentration on a major external problem.

Do not create reviewer bureaucracy for every small continuation.

## Continue only for information gain

Good continuation reasons include:

- a reusable structural mechanism;
- a theorem target that removes multiple branches;
- a source theorem that changes the feasible strategy;
- a counterexample that forces a new representation;
- a method that transfers to another important campaign;
- a meaningful external-frontier improvement.

Bad default reasons include:

- “the next case exists”;
- raising finite search depth without a new mechanism;
- increasing ansatz degree/order after a bounded no-go;
- running more agents because capacity is available;
- preserving sunk-cost investment.

## PIVOT

`PIVOT` is a decision, not a campaign state. Put the old campaign into `HOLD` or `CLOSED` and create a separate `PROPOSED` campaign for the new objective/scope.

## Campaign closeout

A mathematical success may still lead to `HOLD`/`CLOSED`. Record mathematical outcome, external-frontier outcome, portfolio decision, reason, and reopen condition separately.
