# Research evaluations

Canonical `EVAL-*.yml` records live here. They are post-outcome scheduling/visibility metadata, not Truth Layer evidence.

Rules:

- The evaluated source Task must already have a canonical outcome.
- `SELF_ASSESSMENT` is visible but has zero allocation authority.
- `INDEPENDENT_EVALUATION` and `PORTFOLIO_EVALUATION` may contribute only a bounded ranking signal to explicitly named `followup_task_ids`.
- Evaluation count is not additive reputation: the scheduler aggregates eligible signals with a bounded median, so more voters do not mechanically create more score.
- Evaluations never activate/reopen Campaigns, override readiness/capacity/collisions, promote claims, establish novelty, or count as I2/I3 review by themselves.
- One evaluator actor may have at most one canonical evaluation of the same role for the same source Task.
- `CONTINUE`, `PIVOT`, and `REVIEW` recommendations must name at least one follow-up Task. The source Task cannot name itself as its own follow-up.
- The deterministic human view is `docs/RESEARCH_EVALUATIONS.md`.
