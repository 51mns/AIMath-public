# AIMath Village Architecture v1.3 — `/next` Phase A pure core

**Status:** PHASE A IMPLEMENTED / PHASE B TRANSPORT DEFERRED / INDEPENDENT REVIEW REQUIRED  
**Frozen specification commit:** `5eed8cc40243eba166afee651104f3c4a79d99ac`  
**Frozen specification path:** `reviews/village-v1-3-next-preflight/NEXT_FROZEN_SPEC.md`  
**Frozen specification blob:** `ad851bd4fece0f3f45126ae12da3b54a3a7a5832`  
**Phase A implementation base:** `df7ceb5e685239b936950a0dd01a13e4e38b69eb`

Phase A adds the deterministic, read-only `/next` state/continuation/selection core. It deliberately does **not** add a production `/next` transport command, GitHub writes, branch creation, pull-request creation, canonical lock mutation, merge authority, Truth Layer promotion, autonomous I2/I3 review, or automatic `RENEW`/`TAKEOVER`.

The writer of this Phase A implementation is not its independent security/code reviewer. The fixed Phase A head is a later review target, not an independently accepted boundary merely because its own tests pass.

## 1. Implemented Phase A boundary

`scripts/village_next.py` is a pure derivation layer over an already-observed repository snapshot. It receives `VillageState`, the canonical `EvaluationBook`, retained worker/principal identity, capability data, optional already-observed `PENDING_CLAIM` rows, and explicit continuation-gate metadata. It returns state and action **intent** only.

The eight frozen ephemeral control phases are represented explicitly:

1. `ACTIVE_WORK`
2. `RESULT_RECORDED`
3. `CONTINUATION_DECISION`
4. `RELEASE_PENDING`
5. `RELEASED`
6. `NEXT_SELECTION`
7. `ACQUIRE_PENDING`
8. `ACTIVE_NEXT`

Intermediate phases appear in the deterministic transition trace even when they are not the final returned phase. They are not new canonical Task states or ownership states.

`RELEASE_PENDING` means only **prepare/reuse a RELEASE transport in Phase B**. `ACQUIRE_PENDING` means only **prepare/reuse an ACQUIRE transport in Phase B**. Neither is canonical ownership. `ACTIVE_NEXT` is returned only when the supplied canonical snapshot already contains the exact active lock for the retained worker/principal on the next Task.

## 2. Terminal evidence authority and outcome preservation

Phase A recognizes terminal evidence only at the inherited canonical paths:

- `coordination/outcomes/<TASK-ID>.yml` → `RESULT_TERMINAL`
- `work/<TASK-ID>/<worker-id>/ABANDONED_TERMINAL.yml` → `ABANDONED_TERMINAL`

The implementation reuses v1.2.1 schema and acquisition-time validation. Chat text, branch-only files, PR text and caller prose are not inputs to the terminal recognizer and therefore cannot terminalise work.

`RESULT_TERMINAL` preserves the exact canonical `outcome_type`:

- `CLAIM_CANDIDATE`
- `STRUCTURAL_REDUCTION`
- `COUNTEREXAMPLE`
- `FAILED_ROUTE`
- `REPRODUCTION_FAILURE`
- `NO_REUSABLE_PROGRESS`
- `INCONCLUSIVE`
- `LITERATURE_MATCH`

No success/failure boolean is introduced. Negative and inconclusive outcomes remain scheduling-valid terminal research information.

`ABANDONED_TERMINAL` remains a separate scheduling record and must retain `truth_layer_effect = NONE`. A malformed result cannot become terminal authority; the inherited v1.2.1 rule still permits an independently valid current-acquisition abandonment record to terminalise instead.

A structurally valid terminal result can move an exact current lock to `RELEASE_PENDING` even when independent review is still required. Review demand is recorded separately and never extends writer ownership.

## 3. Continuation policy

The pure continuation derivation preserves the frozen order.

First, mandatory gates are evaluated: global admission, Campaign closure, explicit stop condition, dependency reevaluation, and any required human Continuation Gate. These are scheduling restrictions, not mathematical judgements.

Second, `review_required` is retained as a separate review-demand bit. It does not block RELEASE.

Third, same-Campaign continuation is restricted to already-existing canonical Tasks whose `stored_state` is `APPROVED`. No worker recommendation can create a Task, reopen a Campaign, or expand the completed Task scope. Canonical independent/Portfolio evaluation `followup_task_ids` are retained only as bounded ranking/visibility metadata; `SELF_ASSESSMENT` is not follow-up authority.

Fourth, same-route and alternative-route continuation are represented by selecting an existing Task and reporting its relation (`SAME_ROUTE_TASK`, `ALTERNATIVE_ROUTE_TASK`, or `SAME_CAMPAIGN_TASK`). No Task identity is rewritten.

Fifth, if no eligible same-Campaign approved Task survives hard gates, ordinary global READY Tasks in other Campaigns may be considered. A missing Continuation Gate blocks only work that depends on that strategic continuation; unrelated eligible work can still be selected when global admission permits it.

Finally, if no candidate survives, Phase A returns `NO_ELIGIBLE_TASK`. If a required human decision is the remaining blocker, it returns `WAITING_PORTFOLIO`. It never manufactures a Task.

The only accepted automatic human-gate evidence is a matching canonical Campaign decision with `authority = HUMAN_MAINTAINER`. `CLAIM_CANDIDATE`, `COUNTEREXAMPLE`, and `STRUCTURAL_REDUCTION` automatically require this gate even if a caller omits an advisory gate flag. Worker prose cannot synthesize `CONTINUE`, `PIVOT`, `HOLD`, or `CLOSED` authority. Any Phase-B inputs stating that a stop condition was reached or a dependency follow-up became unusable must themselves be derived from canonical/fresh observation; in Phase A those inputs can only restrict scheduling, never grant it.

## 4. Hard filtering and deterministic rank reuse

Phase A does not define a `/next` score. It reuses the existing v1.2 `rank_v12` order:

`human priority -> capability fit -> bounded adaptive score -> stable Task ID`.

Before `rank_v12` sees a candidate as rankable, Phase A applies the hard gates that are observable from its inputs:

- runtime READY / canonical readiness
- Task `stored_state = APPROVED`
- Campaign/global/dependency/frontier/collision/conflict/owned-path/capacity gates inherited through `VillageState.runtime_state()` / `readiness()`
- capability eligibility
- valid observed `PENDING_CLAIM` reservation exclusion
- same `(worker_id, task_id)` abandonment cooldown
- same-worker EXCLUSIVE capacity
- continuation-policy restrictions

The hard-eligible set is exposed to `rank_v12` through a read-only state view whose `runtime_state()` returns `BLOCKED` for every excluded Task. Thus an excluded Task is not assigned scheduling authority by score. `rank_v12` still sees the real Campaign/lock state for its existing bounded diversity/headroom calculations.

Any eligibility/rank exception returns `RANK_FAILED` with no fallback Task. There is no first-item, random, remembered, or self-selected fallback.

## 5. Identity and ownership boundary

`worker_id` remains non-secret scheduling identity. Phase A requires exact current canonical lock binding to:

- source `task_id`
- retained `worker_id`
- authenticated `principal_id`

A different principal presenting the same worker ID, or the same principal presenting a different worker ID, cannot derive automatic RELEASE eligibility for that lock.

`PENDING_CLAIM` remains a reservation observation only. An open/green transport cannot produce `ACTIVE_NEXT`. Only a fresh supplied canonical active lock can do so.

## 6. Phase B deferred boundary

Phase B owns every operation that needs fresh GitHub transport state or can create GitHub-side objects. It is not implemented in Phase A:

- GitHub/API observation adapter for open PRs, exact head/base and exact-head Verify
- duplicate RELEASE/ACQUIRE transport discovery and idempotent reuse
- worker-side branch/ref creation
- lock-only RELEASE PR creation
- lock-only ACQUIRE PR creation
- transport repair/retry
- current-main/head/base movement handling at transport time
- strict server/ruleset attestation at mutation time
- two-worker/collision/capacity races at merge time
- candidate-local GitHub observation failure isolation in `/next` transport discovery
- lifecycle handoff to the already-reviewed v1.2.1 trusted writer

Phase B must continue to keep Task selection and PR creation outside `scripts/lock_auto_activate.py`. It must not weaken the inherited `eligible RELEASE > eligible ACQUIRE`, exact object, exact current-main, strict-status, candidate-local failure isolation, or at-most-one trusted mutation gates.

## 7. Review-autonomy phase deferred boundary

The review-demand bit in Phase A is informational scheduling state only. Autonomous reviewer supply/preregistration remains disabled until the frozen carry-forward prerequisites are separately implemented and reviewed:

1. governance protection for `reviews/**/REVIEW.yml`
2. CI rejection of autonomous I2/I3 claims
3. objective-only `EFFECTIVE` reviewer liveness
4. REUSE coverage for `review-preregistration/**`
5. bounded lowercase-hex `candidate_id` before interpolation
6. preregistration PR as the observable reservation substrate

Review-candidate immutable H tree/path/blob binding, exact `REVIEW_UNAVAILABLE`, stale review supply, and candidate-ID/path handling therefore remain outside Phase A.

## 8. Security non-authority table

| Surface | Phase A authority |
|---|---|
| Network writes | **NONE** |
| Branch creation in production code | **NONE** |
| PR creation in production code | **NONE** |
| Canonical lock mutation | **NONE** |
| Merge | **NONE** |
| Truth Layer promotion | **NONE** |
| I2/I3 assignment | **NONE** |
| `RENEW` | **NONE** |
| `TAKEOVER` | **NONE** |
| Worker prose as Portfolio authority | **NONE** |
| `PENDING_CLAIM` as ownership | **NONE** |

The pure core contains no GitHub HTTP client, token handling, ref-write path, PR-write path, merge path, or filesystem write. It uses the snapshot time supplied by `VillageState`; there is no hidden wall-clock or network dependency in Phase A tests.

## 9. Frozen v1.3 preregistered-test mapping

Every one of the 38 frozen Section 14 tests is accounted for exactly once below. `IMPLEMENTED_IN_PHASE_A` means the frozen behaviour is enforced by the pure core and/or an inherited v1.2.1 gate directly reused by it. A deferred row is not silently weakened or replaced by a Phase A approximation.

| # | Frozen test | Disposition | Phase boundary note |
|---:|---|---|---|
| 1 | happy path through RELEASE transport, canonical release, ACQUIRE transport, canonical next lock | `DEFERRED_TO_PHASE_B` | Phase A derives every pure phase/intended action; actual transport and merge observations are Phase B. |
| 2 | negative outcome preserved and legitimate RELEASE allowed | `IMPLEMENTED_IN_PHASE_A` | Exact negative `outcome_type` is preserved and yields `RELEASE_PENDING`. |
| 3 | abandonment release plus 24h same-pair reacquire rejection | `DEFERRED_TO_PHASE_B` | Phase A recognizes truth-neutral abandonment and reuses cooldown filtering; full release/reacquire transport integration remains Phase B. |
| 4 | `INCONCLUSIVE` preserved | `IMPLEMENTED_IN_PHASE_A` | No boolean/result rewrite exists. |
| 5 | no eligible Task | `IMPLEMENTED_IN_PHASE_A` | Returns `NO_ELIGIBLE_TASK`; creates nothing. |
| 6 | duplicate `/next` reuses at most one RELEASE/ACQUIRE transport | `DEFERRED_TO_PHASE_B` | Requires open-PR observation and transport creation/reuse. |
| 7 | replayed old acquisition epoch cannot control newer acquisition | `DEFERRED_TO_PHASE_B` | Requires transport/acquisition-epoch GitHub binding beyond the pure current snapshot. |
| 8 | two workers choose same Task | `DEFERRED_TO_PHASE_B` | Canonical merge race belongs to transport/lifecycle integration. |
| 9 | two workers same collision key | `DEFERRED_TO_PHASE_B` | Merge-time collision race belongs to Phase B; Phase A inherits current-snapshot collision filtering. |
| 10 | last Campaign slot race | `DEFERRED_TO_PHASE_B` | Requires fresh final transport revalidation. |
| 11 | last global slot race | `DEFERRED_TO_PHASE_B` | Requires fresh final transport revalidation. |
| 12 | stale candidate drops and reranks | `DEFERRED_TO_PHASE_B` | GitHub candidate freshness adapter is Phase B; Phase A rank input itself is deterministic/fail-closed. |
| 13 | main movement abort/recompute | `DEFERRED_TO_PHASE_B` | Requires fresh GitHub main observation around transport. |
| 14 | head movement invalidates old Verify | `DEFERRED_TO_PHASE_B` | Existing trusted lifecycle gate remains authoritative; `/next` adapter not yet added. |
| 15 | base movement fails closed | `DEFERRED_TO_PHASE_B` | Transport freshness concern. |
| 16 | CI failure gives no reservation/activation | `DEFERRED_TO_PHASE_B` | CI observation adapter not in pure core. |
| 17 | strict gate unavailable gives no automatic merge | `DEFERRED_TO_PHASE_B` | Existing trusted lifecycle gate remains unchanged; `/next` transport handoff is deferred. |
| 18 | review unavailable does not retain writer/global halt | `DEFERRED_TO_REVIEW_AUTONOMY_PHASE` | Phase A already separates review demand and permits writer RELEASE; exact reviewer-supply/`REVIEW_UNAVAILABLE` half is deferred. |
| 19 | worker spoof attempt | `IMPLEMENTED_IN_PHASE_A` | Exact Task/worker/principal lock binding fails closed before release intent. |
| 20 | same-principal different workers stay separate | `IMPLEMENTED_IN_PHASE_A` | Exact worker binding and inherited worker-cap semantics are retained. |
| 21 | malformed outcome | `IMPLEMENTED_IN_PHASE_A` | Invalid RESULT cannot terminalise; independently valid abandonment fallback is inherited. |
| 22 | malformed GitHub candidate is local failure; later valid candidate continues | `DEFERRED_TO_PHASE_B` | Candidate GitHub observation layer is not present in Phase A. |
| 23 | `PENDING_CLAIM` is not ownership | `IMPLEMENTED_IN_PHASE_A` | `ACTIVE_NEXT` requires canonical active lock, never PENDING input. |
| 24 | continuation human gate | `IMPLEMENTED_IN_PHASE_A` | Only matching canonical `HUMAN_MAINTAINER` decision can satisfy the gate. |
| 25 | self-evaluation has zero authority | `IMPLEMENTED_IN_PHASE_A` | Self-evaluation neither creates candidate Tasks nor bypasses READY/hard gates. |
| 26 | deterministic rank | `IMPLEMENTED_IN_PHASE_A` | Reuses `rank_v12`; stable Task ID remains final tie-break. |
| 27 | rank failure has no fallback | `IMPLEMENTED_IN_PHASE_A` | Returns `RANK_FAILED`, selected Task `None`. |
| 28 | result before release must be canonical | `IMPLEMENTED_IN_PHASE_A` | Terminal recognizer has no chat/branch authority input. |
| 29 | release independent of review | `IMPLEMENTED_IN_PHASE_A` | `review_required=true` is separate and still yields RELEASE intent. |
| 30 | writer self-review cannot promote | `IMPLEMENTED_IN_PHASE_A` | Phase A exposes no Truth/I2/I3 promotion operation. |
| 31 | stale review prereg supply drops | `DEFERRED_TO_REVIEW_AUTONOMY_PHASE` | Reviewer supply subsystem not implemented. |
| 32 | zero review supply gives exact `REVIEW_UNAVAILABLE` | `DEFERRED_TO_REVIEW_AUTONOMY_PHASE` | Phase A carries review demand only. |
| 33 | immutable H tree/path/blob review binding | `DEFERRED_TO_REVIEW_AUTONOMY_PHASE` | Review candidate/preregistration subsystem not implemented. |
| 34 | candidate_id sanitation | `DEFERRED_TO_REVIEW_AUTONOMY_PHASE` | No Phase A candidate-ID/path interpolation exists. |
| 35 | autonomous review path protection | `DEFERRED_TO_REVIEW_AUTONOMY_PHASE` | Review launch remains disabled. |
| 36 | no `RENEW`/`TAKEOVER` expansion | `IMPLEMENTED_IN_PHASE_A` | Pure core has no automatic lifecycle operation set. |
| 37 | at-most-one trusted mutation; RELEASE before ACQUIRE | `DEFERRED_TO_PHASE_B` | Trusted writer remains unchanged; `/next` transport handoff is Phase B. |
| 38 | candidate-local observation failure isolation | `DEFERRED_TO_PHASE_B` | Existing v1.2.1 trusted lifecycle keeps this gate; new `/next` GitHub adapter must reproduce it in Phase B. |

## 10. Phase A direct acceptance coverage

`scripts/test_village_v1_3_next.py` independently checks the Phase A core, including:

- active exact worker + no terminal → `ACTIVE_WORK`
- exact outcome preservation for positive, negative and `INCONCLUSIVE` results
- truth-neutral abandonment and malformed-result fallback
- malformed result fail-closed
- branch/chat-only non-authority
- terminal + lock → `RELEASE_PENDING`
- released snapshot → selection / global fallback / `NO_ELIGIBLE_TASK`
- human Continuation Gate and canonical human decision
- review-demand separation from writer release
- self-evaluation non-authority
- deterministic `rank_v12` reuse and fail-closed rank failure
- PENDING non-ownership and canonical-only `ACTIVE_NEXT`
- worker/principal spoof rejection
- global pause semantics
- absence of mutation/Truth/`RENEW`/`TAKEOVER` authority
- no filesystem/network mutation by pure derivation

`scripts/village.py test` includes this v1.3 direct suite. No production `/next` CLI transport is introduced in Phase A.
