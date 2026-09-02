# Village v1.3 `/next` frozen preflight specification

TASK-ID: `AIMATH-VILLAGE-V1-3-NEXT-PREFLIGHT`

Status: **READY_FOR_IMPLEMENTATION_AFTER_LIVE_VALIDATION**

Implementation start condition: **`V1_2_1_LIVE_VALIDATED`**

Frozen design base: `aae3b3be4a1da76eb4e1241ae7a366f39ff5f7f2`

This document is a design contract only. It changes no Village production code, governance state, Task, Campaign, lock, claim, review, workflow, ruleset, or GitHub setting.

## 1. Scope and inherited authority

Village v1.3 `/next` is the persistent-worker continuation command after a worker has already entered through `/join` and has a retained `worker_id`.

Its job is strictly:

1. prove that the previous work unit has reached a repository-recognised terminal boundary;
2. preserve that outcome durably;
3. derive the continuation disposition from canonical repository state and deterministic policy;
4. release existing EXCLUSIVE ownership through the existing lock-only RELEASE transport;
5. after canonical release, derive and rank eligible next Tasks from a fresh observation;
6. create or reuse an ordinary worker lock-only ACQUIRE transport for the selected Task;
7. hand that transport to the already-reviewed v1.2.1 trusted lifecycle;
8. recognise `ACTIVE_NEXT` only after the new canonical lock is merged on current `main`.

`/next` is not a new mutation authority. A merged canonical lock remains the only EXCLUSIVE ownership authority. `PENDING_CLAIM` remains a temporary scheduling reservation only. Human Portfolio governance remains the authority for strategic Campaign decisions. Truth Layer acceptance, novelty, review independence, I2/I3, and mathematical promotion remain outside `/next` authority.

The v1.2.1 ordering `eligible RELEASE > eligible ACQUIRE`, trusted-main execution, strict server gate, final main/head/base revalidation, candidate-local failure isolation, and at-most-one lifecycle mutation per trusted run are inherited unchanged.

## 2. Entry prerequisites

A `/next` request is eligible for state-machine execution only when all applicable prerequisites below can be established from fresh repository/GitHub state.

### 2.1 Required identity and repository binding

- The caller retains a schema-valid `worker_id = w-<16..32 lowercase hex>` from its original `/join` session.
- `worker_id` is scheduling identity only, never a credential.
- The authenticated GitHub principal is observed independently as `principal_id = gh:<login>`.
- If an active canonical lock exists for the previous Task, its `worker_id` must equal the retained worker and its actor principal must equal the authenticated principal for automatic exact-worker RELEASE.
- Same principal + different worker is allowed as a scheduling configuration but is not the same worker and does not permit cross-worker `/next` replay.

### 2.2 Previous-work boundary

For an EXCLUSIVE active Task, exactly one current canonical lock bundle for the worker/Task acquisition must be identifiable.

Before RELEASE can become eligible, current `main` must contain one of the existing v1.2.1 terminal classes:

- `RESULT_TERMINAL`: schema-valid `coordination/outcomes/<TASK-ID>.yml` with exact `task_id`; or
- `ABANDONED_TERMINAL`: schema-valid `work/<TASK-ID>/<worker-id>/ABANDONED_TERMINAL.yml`, bound to this worker/Task and not older than the current lock acquisition.

A branch-only result, chat statement, PR comment, issue comment, local file, or unmerged research commit is not terminalisation authority.

A malformed outcome does not authorise continuation. A valid abandonment marker may independently terminalise the current acquisition as already permitted by v1.2.1.

### 2.3 Duplicate/open-transport checks

Before creating anything, `/next` must fresh-observe:

- current `main` full SHA;
- the exact canonical lock bundle, if any;
- open same-repository PRs relevant to this worker;
- exact PR head/base state and CI for any candidate transport it proposes to reuse;
- existing current-main terminal outcome/abandonment state;
- existing pending ACQUIRE reservations from a direct GitHub API observation.

If an equivalent RELEASE or ACQUIRE transport already exists, `/next` reuses/observes it instead of creating a duplicate.

### 2.4 Blocking prerequisites

`/next` must not select/acquire a next Task while:

- the prior EXCLUSIVE canonical lock is still active and not in a valid RELEASE path;
- the previous result has not been durably recorded when a result exists;
- current canonical Village state is invalid;
- repository-wide GitHub observations needed for safe selection are unavailable or malformed;
- global admission is `PAUSED`;
- a required human Continuation Gate decision for the relevant Campaign has not been recorded and the proposed next work depends on that decision.

Review unavailability by itself is **not** a global selection blocker.

## 3. State machine

The names below are **ephemeral `/next` control phases**, not new canonical Task states and not new ownership states. Canonical runtime state continues to be derived by existing Village code.

| Phase | Authority / input | Preconditions | Output | Failure | Retry semantics |
|---|---|---|---|---|---|
| `ACTIVE_WORK` | current canonical lock + retained worker + current Task | exact active work is still owned | continue work, or proceed only when a terminal record is ready | missing/mismatched ownership => reject `/next` for that acquisition | fresh-read; never repair ownership from chat |
| `RESULT_RECORDED` | current-main outcome or abandonment record | schema valid, exact Task/worker where applicable; abandonment not predating acquisition | immutable terminal class + terminal evidence identity | malformed/unmerged record => fail closed | fix/merge record, then retry |
| `CONTINUATION_DECISION` | canonical outcome, Campaign/Task/decision/failed-route/dependency/evaluation state | terminal record fixed; fresh main | one deterministic disposition from Section 5 | required human decision absent => WAITING_PORTFOLIO; malformed state => fail closed | recompute from fresh main; no cached authority |
| `RELEASE_PENDING` | existing lock + exact release ref/PR transport | valid terminalisation; exact worker/principal binding | reuse or create dedicated lock-only RELEASE PR | CI/head/base/shape failure => retryable after repair; identity mismatch => terminal for this request | idempotently reuse equivalent open PR |
| `RELEASED` | current `main` | canonical prior lock is absent | old ownership ended; next selection may begin | release PR merely open/merged status uncertain => remain pending | fresh-read until canonical absence is proven |
| `NEXT_SELECTION` | fresh Village state + fresh direct GitHub reservation observation + capability profile | prior EXCLUSIVE lock released; selection not forbidden by continuation decision | selected eligible Task or `NO_ELIGIBLE_TASK` / `REVIEW_UNAVAILABLE` / `WAITING_PORTFOLIO` | observation/rank failure => fail closed, retryable | recompute whole candidate set from fresh state |
| `ACQUIRE_PENDING` | selected Task + deterministic worker workspace + existing lock-only ACQUIRE primitive | Task still eligible; no valid competing reservation; no cooldown/conflict/capacity/dependency failure | reuse or create one lock-only ACQUIRE PR | stale candidate/CI/main/head movement => abandon this attempt and recompute | duplicate requests reuse same observable transport |
| `ACTIVE_NEXT` | current canonical lock on `main` | exact Task, worker, principal, collision keys/work_ref match | worker resumes research under existing Village rules | PENDING/green PR alone is insufficient | fresh-read; only canonical merge completes transition |

The state machine must never infer a skipped phase from chat memory. In particular, `ACQUIRE_PENDING -> ACTIVE_NEXT` requires a fresh canonical lock observation.

## 4. Outcome preservation

`/next` preserves research information before scheduling convenience.

### 4.1 Existing result vocabulary remains canonical

The outcome schema already distinguishes:

- positive/promotable-looking work: `CLAIM_CANDIDATE`, `STRUCTURAL_REDUCTION`;
- negative information: `COUNTEREXAMPLE`, `FAILED_ROUTE`, `REPRODUCTION_FAILURE`, `NO_REUSABLE_PROGRESS`;
- uncertainty: `INCONCLUSIVE`;
- source placement: `LITERATURE_MATCH`.

No `/next` result classifier may collapse these into a single boolean success/failure flag.

### 4.2 Abandonment remains separate

`ABANDONED_TERMINAL` is availability/scheduling state with `truth_layer_effect = NONE`. It is not a replacement mathematical outcome and must not be represented as a failed theorem or failed review.

The durable monotone abandonment record and 24-hour same `(worker_id, task_id)` reacquisition cooldown remain unchanged.

### 4.3 Truth separation

The existence of a structurally valid `RESULT_TERMINAL` is sufficient for RELEASE eligibility but is not evidence that its mathematics is correct, novel, independently reviewed, or promotable.

Review and claim acceptance may remain pending after the writer has released ownership and moved to unrelated eligible work.

## 5. Continuation policy

The continuation decision is a **scheduling/Portfolio routing decision**, not a Truth decision.

### 5.1 Deterministic decision order

After terminalisation, derive the following in order:

1. **Mandatory stop / wait gates**: Campaign `CLOSED`; global admission `PAUSED`; dependency reevaluation that makes proposed follow-up unusable; missing required Continuation Gate human decision; explicit Task/Campaign stop condition reached.
2. **Review demand**: if the frozen result requires independent review, record that review demand separately. It does not keep the writer lock alive.
3. **Existing approved follow-ups**: only canonical, already-approved Tasks may be automatic next candidates. Worker prose cannot create a Task or activate a Campaign.
4. **Same route / alternative route**: this is represented by selection among approved follow-up Tasks and their canonical route/campaign metadata, not by dynamically expanding the completed Task scope.
5. **Different Task**: if no eligible follow-up in the same Campaign survives hard gates, ordinary global READY selection is allowed unless human Portfolio policy says to stop/wait.
6. **No eligible Task**: return `NO_ELIGIBLE_TASK`; do not manufacture work to consume capacity.

### 5.2 “Continue the same Task” exact meaning

Once `coordination/outcomes/<TASK-ID>.yml` is canonical, that Task has a terminal result and `/next` must not silently erase or overwrite it to obtain another iteration.

Therefore v1.3 does **not** implement automatic literal reacquisition of a completed Task ID as “continue”. A worker that has not yet terminalised may simply remain in `ACTIVE_WORK`; after terminalisation, continued research requires an already-approved bounded successor Task (same route/campaign is allowed) or a human-approved new Task through normal governance.

This prevents next-rank/case scope creep and preserves one durable terminal result per Task identity.

### 5.3 Continuation Gate authority

If the result triggers the existing Continuation Gate (for example major result/counterexample/structural reduction, lane-budget exhaustion, two meaningful route closures, next rank/dimension/parameter, capacity increase, HOLD reopen, or material frontier change), a worker may draft a memo/recommendation but cannot turn it into `CONTINUE`, `PIVOT`, `HOLD`, or `CLOSE` authority.

The recorded human Campaign decision remains authoritative. Until it exists, candidate Tasks that depend on that strategic continuation are excluded. Unrelated eligible work elsewhere may still be selected after RELEASE.

Self-assessment has zero allocation authority. Independent/Portfolio evaluation can only provide the already-bounded ranking signal to explicitly named follow-up Tasks.

## 6. Ranking policy

Reuse existing v1.2 ranking rather than creating a `/next`-specific score.

### 6.1 Hard filtering before rank

The candidate set must first be reduced by current canonical/fresh-observation gates, including:

- Task stored state and derived READY/runtime eligibility;
- effective Campaign state and global admission;
- dependency/public-evidence usability;
- frontier freshness where required;
- actual capability eligibility;
- current canonical Task ownership;
- collision keys;
- explicit conflicts and owned-path overlap;
- same worker EXCLUSIVE cap;
- abandonment cooldown;
- Campaign hard capacity;
- global hard capacity;
- valid fresh `PENDING_CLAIM` reservations;
- any continuation-decision restriction from Section 5.

Only surviving candidates are ranked.

### 6.2 Rank is not authority

The existing deterministic v1.2 order is retained:

`human priority -> capability fit -> existing bounded adaptive score -> stable Task ID tie-break`.

The adaptive score may include existing class diversity, Campaign headroom, and bounded allocation-eligible independent/Portfolio evaluation signals. It may not bypass a hard gate.

A rank computation failure is not permission to take the first Task, random Task, remembered Task, or self-declared favourite.

## 7. ACQUIRE hand-off

`/next` must not call a new canonical mutation path.

### 7.1 `/next` responsibilities

After selection, `/next` may, using already-granted GitHub permissions:

- derive the deterministic worker workspace for the selected Task;
- prepare the exact lock bundle required by the existing ACQUIRE validator;
- create a worker-side branch/ref needed to submit that lock-only change;
- create or reuse **one** dedicated lock-only ACQUIRE PR;
- observe its Verify status and fresh `PENDING_CLAIM` reservation state;
- hand it to the existing v1.2.1 lifecycle.

### 7.2 `/next` must not

- merge the lock directly;
- write canonical lock files to `main` outside the existing lifecycle;
- trust its own PR as ownership;
- relax `100644` regular-blob/object checks;
- bypass exact current-main readiness/collision/capacity revalidation;
- automate `RENEW` or `TAKEOVER`;
- create/approve Campaigns or Tasks;
- merge research/claim/review/governance changes through the lock lifecycle.

`ACTIVE_NEXT` occurs only after a fresh read of the merged canonical lock.

## 8. Persistent identity model

`worker_id` represents persistent scheduling continuity across `/join` -> work -> `/next` -> next work.

It is explicitly **not**:

- authentication;
- a bearer token;
- GitHub authorization;
- a DCO signer;
- evidence of independent review;
- Sybil resistance.

Security-sensitive operations continue to bind to the authenticated GitHub principal and current canonical object state.

### Replay/spoof rules

- Different principal claiming the same `worker_id` cannot automatic-RELEASE a lock owned by another principal and cannot inherit repository authority.
- Same principal using another worker's `worker_id` is not cryptographically prevented by worker identity; canonical worker binding, exact PR/ref semantics, current lock state and principal authorization are the available controls. This is an acknowledged v1.2 Sybil boundary, not solved by `/next`.
- Same principal with two distinct workers is permitted only under ordinary worker/collision/Campaign/global caps.
- A chat transcript or “I am worker X” statement never replaces fresh GitHub/canonical binding.

## 9. Reviewer boundary

Writer continuation and reviewer scheduling are separate resource flows.

### 9.1 Writer cannot self-promote

The writer may mark an outcome as requiring review or create a review request candidate, but it must not create authoritative evidence that its own result is I2/I3. Existing I0/I1/I2/I3 semantics remain Truth-Layer semantics.

### 9.2 Frozen prerequisites for autonomous review launch

Before autonomous review launch is implementation-enabled, all v1.2.1 carry-forward prerequisites must be satisfied:

1. `reviews/**/REVIEW.yml` is protected/governance-controlled;
2. autonomous review output claiming `I2` or `I3` fails CI;
3. preregistration liveness `EFFECTIVE` is based only on objective completion/backlog improvement, not heartbeat;
4. `review-preregistration/**` has correct REUSE coverage before use;
5. `candidate_id` uses a strict bounded lowercase-hex format before path/ref interpolation;
6. the preregistration PR itself is the observable reservation substrate.

### 9.3 Review-candidate binding

For the previously frozen “fixed H tree/path/blob” requirement, this spec uses `H` only as the immutable review-target handle. The review candidate must bind all of:

- exact source tree/full commit SHA containing `H`;
- exact repository-relative `H` path;
- exact regular-blob Git OID for that path;
- claim/result identifier and candidate ID.

A different tree, path, or blob is a different review target and requires fresh preregistration. Chat text and PR descriptions cannot substitute for this binding.

### 9.4 Reviewer supply

Only fresh, mechanically valid reservation/activity observations count as reviewer supply. Stale or malformed supply is dropped.

`ACTIVE_SUPPLY` may reflect a currently valid reservation/activity substrate. `EFFECTIVE` supply requires objective progress under the v1.2.1 rule: review completion count increased in the effectiveness window or oldest backlog age decreased.

If eligible reviewer supply is zero, the review-demand result is `REVIEW_UNAVAILABLE`.

`REVIEW_UNAVAILABLE`:

- does not promote the claim;
- does not count as review completion;
- does not authorise writer self-review;
- does not keep the writer lock alive after terminalisation;
- does not globally stop unrelated READY research;
- leaves the result in the existing `WAITING_REVIEW`/unpromoted Truth state as applicable.

## 10. Concurrency and race model

Canonical lock merge order remains final ownership authority.

### 10.1 Two workers choose the same Task

Both may independently derive the same Task before either owns it. A valid fresh `PENDING_CLAIM` may temporarily reserve selection, but it is not ownership. Ultimately only a merge-compatible lock can become canonical; the loser must refresh and reselect.

### 10.2 Same collision key

All colliding candidates are revalidated against current main. The first canonical lock merge consumes the collision capacity; later stale candidates fail revalidation.

### 10.3 Last Campaign/global slot

No precomputed rank grants a slot. The trusted ACQUIRE revalidator checks capacity against current main. When one merge consumes the final slot, other candidates become ineligible/stale and must recompute.

### 10.4 Main/head movement

Selection snapshots are advisory only. Immediately before any trusted mutation, existing v1.2.1 final current-main/head/base refetch and expected-head merge rules remain authoritative. Movement aborts the attempt.

### 10.5 At-most-one mutation

A trusted lifecycle run may attempt at most one canonical lifecycle mutation, preserving v1.2.1 RELEASE priority. `/next` may require multiple workflow invocations over time (first RELEASE, later ACQUIRE); it must never expect RELEASE+ACQUIRE to become one atomic main mutation.

## 11. Idempotency

Idempotency is derived from canonical state plus observable transport identity; no chat-local “already did it” flag is authoritative.

### 11.1 Request epoch

For a worker leaving an EXCLUSIVE acquisition, the logical `/next` epoch is bound to:

`(task_id, worker_id, canonical lock_id, canonical lock acquired_at, canonical lock blob bundle identity, terminal class, terminal evidence blob identity)`.

The implementation may hash this tuple to an internal bounded lowercase-hex request/candidate identifier, but that hash is not a credential or canonical ownership object.

### 11.2 Duplicate handling

For retry, duplicate webhook, double-click or same-chat resend:

1. fresh-read current main;
2. if prior lock still exists and an equivalent valid RELEASE PR is open, reuse it;
3. if prior lock is already absent, do not recreate RELEASE;
4. recompute next selection from fresh state;
5. if the selected Task already has an equivalent valid ACQUIRE PR for this worker, reuse it;
6. if the canonical next lock already exists, return `ACTIVE_NEXT`;
7. never create a second lock bundle/PR merely because the request was delivered twice.

A replay from an old acquisition epoch cannot terminalise or release a newer reacquisition because the terminal/acquisition time and canonical lock identity must match current state.

## 12. Failure semantics

| Failure | Class | Required behaviour |
|---|---|---|
| GitHub API failure during repository-wide prerequisite observation | retryable fail-closed | no selection/mutation from cache or memory |
| candidate-local PR observation/shape failure | candidate-local fail-closed | candidate ineligible; continue other candidates, matching v1.2.1 |
| Verify/CI failure | retryable candidate failure | no reservation/activation; repair or choose another eligible Task after fresh rank |
| ruleset/strict-status read unavailable or not true | global mutation fail-closed | no trusted merge; keep transport pending/manual path only under existing governance |
| rank computation failure | retryable fail-closed | no fallback random/first/self-selected acquisition |
| candidate disappears/closes | retryable | recompute reservations and rank |
| current main moves | retryable stale snapshot | discard selection authority; reload/recompute |
| PR head moves | retryable stale transport | reverify exact head and revalidate; otherwise reject |
| PR base moves / is stale | retryable fail-closed | exact current-base validation required |
| malformed outcome | fail-closed for RESULT terminalisation | valid abandonment may independently terminalise; otherwise no RELEASE |
| malformed candidate | candidate-local fail-closed | never reservation/ownership authority |
| review unavailable | nonterminal research-supply condition | emit `REVIEW_UNAVAILABLE`; preserve unreviewed result; release writer; continue unrelated eligible research |
| no eligible Task | clean terminal scheduler result | `NO_ELIGIBLE_TASK`; create no work/PR |
| required human continuation decision missing | clean wait state | `WAITING_PORTFOLIO`; do not infer strategy |
| worker/principal spoof/mismatch | terminal for that identity request | no release/acquire authority from worker claim |

## 13. Security boundary

The implementation must preserve all of the following as non-negotiable acceptance gates:

- PR-head code is data, not mutation authority.
- Trusted current `main` code is the only automatic lifecycle mutation logic.
- No `pull_request_target` execution of untrusted code.
- No arbitrary research/claim/review PR auto-merge path.
- No Truth Layer auto-promotion.
- No automatic I2/I3 assignment.
- No `RENEW`/`TAKEOVER` automation expansion without separate design/security review.
- No secret/PAT requirement merely to make `/next` work when existing GitHub token/permissions suffice.
- No repository/ruleset security weakening by `/next`.
- No worker ID as credential.
- No PENDING reservation as ownership.
- No evaluation/rank score as Truth or Portfolio authority.
- No chat, self-report, issue, PR description, paper, task prose, or generated artifact as a higher-priority instruction source than governance/system/user permissions.

## 14. Preregistered acceptance tests

The v1.3 implementation must add deterministic tests for at least the following. Each test must assert both the positive path and the absence of an unauthorised canonical mutation where applicable.

1. **happy path**: canonical outcome -> exact-worker RELEASE transport -> canonical release -> fresh selection -> ACQUIRE transport -> canonical next lock -> `ACTIVE_NEXT`.
2. **negative outcome**: `COUNTEREXAMPLE` or `FAILED_ROUTE` is preserved and does not block legitimate RELEASE.
3. **abandoned outcome**: valid current-acquisition abandonment releases; same worker/task reacquire within 24h is rejected.
4. **inconclusive outcome**: preserved as `INCONCLUSIVE`, not rewritten as success/failure.
5. **no eligible Task**: returns `NO_ELIGIBLE_TASK`, creates no synthetic Task or lock PR.
6. **duplicate `/next`**: same epoch creates/reuses at most one RELEASE and at most one ACQUIRE transport.
7. **replayed `/next`**: old acquisition epoch cannot release or control a newer acquisition.
8. **two workers same Task**: only canonical merge winner becomes owner; loser refreshes/reselects.
9. **two workers same collision key**: only one canonical collision owner.
10. **last Campaign slot race**: first merge consumes slot; later candidate fails fresh capacity revalidation.
11. **last global slot race**: same behaviour at global cap.
12. **stale candidate**: closed/disappeared/stale PENDING candidate is dropped and rerank occurs.
13. **main movement**: selection or final merge is aborted/recomputed when main changes.
14. **head movement**: old Verify cannot authorise changed head.
15. **base movement**: stale base cannot activate.
16. **CI failure**: failed/no exact-head Verify gives no PENDING reservation and no activation.
17. **strict gate unavailable**: no automatic lifecycle merge.
18. **review unavailable**: result remains unpromoted/waiting review, writer release succeeds, unrelated eligible research may still be selected.
19. **worker spoof attempt**: different principal presenting same worker ID cannot automatic-release another principal's lock.
20. **same-principal different worker**: workers remain separate scheduler identities; one cannot use the other's active worker slot; distinct noncolliding work remains possible under caps.
21. **malformed outcome**: no RESULT terminalisation; valid abandonment fallback only if independently valid.
22. **malformed candidate**: candidate cannot reserve/block/own; later valid candidates remain examinable.
23. **PENDING_CLAIM is not ownership**: green open acquire PR does not yield `ACTIVE_NEXT` before canonical merge.
24. **continuation human gate**: worker recommendation cannot activate/reopen Campaign or authorise next-rank/dimension escalation.
25. **self-evaluation has zero authority**: self score cannot make a blocked/non-READY Task selectable.
26. **rank deterministic**: identical canonical/fresh inputs produce same ordered candidates and stable Task-ID final tie-break.
27. **rank failure**: no fallback acquisition.
28. **result before release**: branch-only/chat-only result cannot terminalise current lock.
29. **release independent of review**: valid terminal result can release before I2/I3 review completes.
30. **writer self-review rejected for promotion**: `/next` cannot manufacture I2/I3.
31. **review prereg stale supply**: stale reservation/activity drops from supply.
32. **review supply zero**: exact `REVIEW_UNAVAILABLE`, no global research halt.
33. **review candidate immutable binding**: changed H tree/path/blob requires a new preregistration/candidate identity.
34. **candidate_id sanitation**: malformed/overlong/non-lowercase-hex candidate ID fails before ref/path interpolation.
35. **autonomous review path protection**: review launch remains disabled until all six v1.2.1 carry-forward prerequisites are active.
36. **no RENEW/TAKEOVER expansion**: `/next` cannot produce an automatically authorised renewal/takeover path.
37. **at-most-one trusted mutation per run**: eligible RELEASE prevents same-run ACQUIRE mutation.
38. **candidate-local observation failure isolation**: invalid lower candidate cannot block later valid RELEASE/ACQUIRE, while repository-wide prerequisite failure remains global fail-closed.

## 15. Implementation decomposition after live validation

Once `V1_2_1_LIVE_VALIDATED` is recorded, implementation should be split so the existing trusted lifecycle remains a narrow mutation primitive.

Recommended separation:

1. pure `/next` state derivation and continuation decision;
2. fresh GitHub observation adapter for reservations/transports;
3. deterministic selection wrapper reusing `rank_v12`;
4. idempotent RELEASE/ACQUIRE PR transport creation/reuse;
5. optional review-demand/preregistration subsystem behind the frozen review-autonomy prerequisites;
6. synthetic/adversarial tests;
7. separate independent security review before integration because new branch/PR creation and preregistration surfaces expand orchestration, even though mutation authority is unchanged.

Do not place Task selection, branch creation, PR creation, review selection, or Truth logic inside `scripts/lock_auto_activate.py`'s trusted write path.

## 16. Open questions deliberately not solved here

These are not blockers to the frozen `/next` contract but require implementation-detail choice inside the contract:

- exact CLI/API surface (`village.py next`, webhook, or both);
- exact non-secret hash length/name used for a derived `/next` request epoch/candidate ID, subject to bounded lowercase-hex validation;
- exact branch prefix for worker-created ACQUIRE transport if the current implementation helper does not already freeze one; it must remain separate from canonical ownership and pass existing lock-only policy;
- operational cadence/window constants for reviewer `ACTIVE_SUPPLY`/`EFFECTIVE` metrics, provided they preserve the frozen objective-liveness rule;
- whether `REVIEW_UNAVAILABLE` is emitted only as runtime status or also captured in a future scheduling record. Any canonical record would require its own schema/governance review and must have no Truth promotion effect.

None of these questions authorises weakening an existing gate.

## 17. Stop conditions checked

At base `aae3b3be4a1da76eb4e1241ae7a366f39ff5f7f2`:

- no v1.2.1 CRITICAL/HIGH defect was found by this preflight read;
- the accepted focused Phase B rereview reports M-01/L-01 closed and no new CRITICAL/HIGH/MEDIUM finding;
- this design does not assume the external strict ruleset gate has been live-validated;
- no Truth Layer automation is required;
- no `RENEW`/`TAKEOVER` expansion is required;
- no production-code change is made by this lane.

Therefore the frozen implementation start condition remains exactly:

`V1_2_1_LIVE_VALIDATED`
