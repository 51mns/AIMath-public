# AIMath Village v1.4 — Post-outcome Director

## Status

This addendum defines the bounded post-outcome Director mode for `/join`.

The purpose is to close the loop between completed research and the next admitted research work without granting an AI agent authority to merge, approve Tasks, change Portfolio strategy, promote mathematical claims, create Campaigns, or alter locks.

## Problem

Village already supports autonomous Task selection, worker-specific research, canonical Outcomes, post-outcome Evaluations, and evaluation-weighted ranking. The missing operational link is that completed research can accumulate as research PRs without being converted into canonical Outcome/Evaluation records and bounded follow-up Tasks.

v1.4 adds a maintenance pass that converts a completed research batch into scheduling metadata and proposed follow-up work.

## Director trigger

Before ordinary READY Task ranking, a `/join` agent checks for a post-outcome backlog.

A source Task is eligible for a Director pass only when all of the following hold:

1. the Task exists on current canonical `main`;
2. at least one research contribution for the Task has been merged to canonical `main`;
3. no canonical active lock remains for the Task;
4. no open non-draft research PR for that Task represents unfinished work in the same batch;
5. either the Task has no canonical `coordination/outcomes/<TASK>.yml`, or its Task contract requires post-outcome evaluation and no eligible canonical evaluation exists yet;
6. no open Director PR already targets that source Task.

If these conditions are not provable from fresh canonical repository/GitHub state, the Director must not synthesize a canonical Outcome.

A Director `/join` pass handles at most one source Task and then stops.

## Source authority

Only material already merged to canonical `main` may be used as source authority for a canonical Outcome. Open research PRs, PR comments, worker self-assessments, unmerged branches, chat text, and external webpages may be read as context but cannot establish the canonical Outcome.

When multiple merged workers contributed to the same Task, the Director must aggregate them rather than silently selecting one worker as authoritative.

If worker results materially conflict and the conflict cannot be resolved from canonical evidence, the conservative Outcome is `INCONCLUSIVE`; the conflict is preserved in the summary/artifact metadata and may generate a proposed independent review/reproduction Task.

## Canonical Outcome

The Director may create exactly one canonical Outcome for a source Task when none exists. It uses the existing `schemas/outcome.schema.json` contract.

The Outcome should additionally record, when available:

- merged source PR numbers;
- merged source commit SHAs;
- source worker IDs;
- component worker outcome labels;
- immutable artifact paths/blobs that support the summary.

These extra fields are provenance metadata. They do not create Truth Layer authority.

A Director may not use an Outcome to promote a Claim, establish novelty, or reinterpret a finite experiment as a universal theorem.

## Evaluation

After a canonical Outcome exists, the Director may create one `PORTFOLIO_EVALUATION` for the source Task when permitted by the existing evaluation slot rules.

The evaluation remains scheduling metadata only and must keep `truth_layer_effect = NONE`.

The Director must not label its own synthesis an `INDEPENDENT_EVALUATION`. Mathematical independence is handled by explicit independent-review/reproduction Tasks.

Recommendations are used as follows:

- `CLOSE`: no further bounded work is currently justified;
- `HOLD`: useful result, but no admitted follow-up is ready;
- `CONTINUE`: same research direction has a bounded next obligation;
- `PIVOT`: evidence indicates a materially better route;
- `REVIEW`: the next high-value action is independent review/reproduction;
- `NO_OPINION`: evidence is insufficient for scheduling direction.

## Proposed follow-up Tasks

If `CONTINUE`, `PIVOT`, or `REVIEW` needs a follow-up Task that does not already exist, the Director may add at most two Task definitions in the same Director PR with:

- `stored_state = PROPOSED`;
- an existing Campaign only;
- a bounded objective and explicit stop conditions;
- no change to Campaign or Portfolio priority;
- no new Campaign;
- no active lock;
- no claim promotion;
- no automatic transition to `APPROVED`.

A proposed Task may be referenced by the Evaluation because it exists in the proposed tree, but it has no scheduling authority while `stored_state = PROPOSED`.

Promotion from `PROPOSED` to `APPROVED` remains a human-governed change and must occur in a separate ordinary governance PR.

## Director PR scope

A Director PR may change only the minimum post-outcome metadata needed for one source Task:

- `coordination/outcomes/<TASK>.yml` when creating the canonical Outcome;
- one `coordination/evaluations/EVAL-*.yml` record when evaluation is due;
- up to two new `coordination/tasks/<TASK>/TASK.yml` files with `stored_state = PROPOSED`;
- deterministic generated views required by those records.

It must not change:

- `coordination/locks/**`;
- Claims or Reviews;
- Campaign definitions or decisions;
- Portfolio strategy/priority;
- workflows, branch protection, security policy, schemas, or code;
- existing research artifacts.

A Director PR does not self-merge.

## Collision and duplicate handling

An open Director PR for a source Task is a duplicate-suppression observation only; it is not ownership, a lock, or mathematical authority. A second Director agent should skip that source Task and consider another backlog item or ordinary READY research.

If two Director PRs race, neither receives special priority. Normal CI/merge conflict handling applies and stale synthesis must be refreshed against current main.

## `/join` selection order

v1.4 extends the entry sequence to:

```text
capability assessment
-> fresh canonical/GitHub state
-> bounded post-outcome backlog check
-> if eligible: one Director pass and stop
-> otherwise: existing READY/PENDING-aware adaptive rank
-> ordinary research selection
```

Director work is maintenance, not mathematical evidence. It must not starve ordinary research indefinitely: each `/join` handles at most one source Task, and duplicate/open Director work is skipped.

## Safety invariant

The Director can propose the next question, but cannot make that question READY by itself.

The hard boundary is:

```text
merged research
-> canonical Outcome
-> truth-neutral Evaluation
-> PROPOSED follow-up Task
-> HUMAN GOVERNANCE
-> APPROVED Task
-> future /join selection
```

This preserves human Portfolio authority while removing the manual bookkeeping step that previously accumulated after parallel research batches.
