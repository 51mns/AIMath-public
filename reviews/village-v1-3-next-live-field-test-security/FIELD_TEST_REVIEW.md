# Village v1.3 `/next` live field-test independent security review

TASK-ID: `AIMATH-VILLAGE-V1-3-NEXT-LIVE-FIELD-TEST-INDEPENDENT-REVIEW`

Verdict: **PASS**

This review is preflight-only. No live `/next` test, lock creation, PR creation, Task mutation, repository setting/security change, or target-plan modification was performed.

## Fixed review target

- Repository: `51mns/AIMath-public`
- Fresh current `main` at review time: `df7ceb5e685239b936950a0dd01a13e4e38b69eb`
- Design base: `df7ceb5e685239b936950a0dd01a13e4e38b69eb`
- Target branch: `review/village-v1-3-next-live-field-test-preflight`
- Fixed target commit: `705bd7c5250103e74118381106d422d50c677bb7`
- Target artifact: `reviews/village-v1-3-next-live-field-test-preflight/FIELD_TEST_PLAN.md`
- Target artifact blob: `05848a5d2998e42e5e02443f331194c61486f3b6`
- Related Phase B design commit: `c3532324e9df421afc787aa6cee3d91f8dbaa91e`
- Related Phase B artifact blob: `5c877ec4d9807f285cb2e2c4c3f3ae3380117271`

The fixed target commit and target blob match the preregistered review inputs exactly.

## Fresh-read substrate

At the fresh review-time `main`:

- `TASK-EQUIANGULAR-R18-001` is an approved `RESEARCH`, `EXCLUSIVE` Task under `CAM-EQUIANGULAR-R18`, with collision key `eq18/general-structural-obstruction` and lease TTL 168 hours.
- `TASK-DITTERT-N5-001` is an approved `RESEARCH`, `EXCLUSIVE` Task under `CAM-DITTERT-N5`, with collision key `dittert-n5/broader-zero-pattern` and lease TTL 168 hours.
- `CAM-EQUIANGULAR-R18` is `ACTIVE`, priority `P0`, with `max_active_lanes=2`.
- `CAM-DITTERT-N5` is `ACTIVE`, priority `P1`, with `max_active_lanes=2`.
- The recursive current-main Git tree is complete (`truncated=false`). It contains no active canonical lock other than the `coordination/locks/README.md` placeholder and contains no path for either test worker `w-0bebfd2fd11cb67f` or wrong-worker control `w-e8912c097a3288e1`.
- A prior durable abandonment marker exists for a different source worker (`w-fae1dfc5fac514d0`), which does not collide with the fixed field-test worker.
- The current effective default-branch Ruleset is active, applies to `~DEFAULT_BRANCH`, requires status context `verify`, has `strict_required_status_checks_policy=true`, has no bypass actors, and reports `current_user_can_bypass=never`.

These are review-time observations only. The field test correctly requires a fresh Phase-0 revalidation after accepted Phase B is merged; none of the observations above may be reused as execution authority.

## Safe truth-neutral substrate

The source terminal is safe for this field test.

`ABANDONED_TERMINAL` is a scheduler/lifecycle terminal, not a mathematical outcome. The current schema explicitly permits `reason=SCOPE_STOP` and requires `truth_layer_effect=NONE`. The plan also forbids creating `coordination/outcomes/TASK-EQUIANGULAR-R18-001.yml` and forbids describing the field-test stop as theorem failure, no-go, counterexample, inconclusive mathematical result, review result, or research result.

Therefore the test does **not** fabricate a mathematical result. The durable marker is acceptable audit residue because its semantics are bounded to the worker acquisition epoch and Truth Layer effect is fixed to `NONE`.

Worker uniqueness is adequately protected: Phase 0 requires both fixed worker IDs to be absent from all current canonical lock bundles and from all worker-specific abandonment-marker paths. Reuse/increment is forbidden; any history causes abort.

Source and expected-next collision conflicts are also explicitly rechecked before mutation and again before trusted ACQUIRE.

## M0 -> M1 -> M2 -> M3 -> M4 audit

### M0 — clean accepted Phase B main

PASS as a design requirement.

The test may begin only from a fresh main containing accepted/merged Phase A and Phase B plus their required independent/security acceptance. It requires current validation and the complete accepted v1.3/v1.2.1 suite from the exact M0 checkout. If Phase B does not expose the required machine-readable identities, the test aborts as `FIELD_TEST_OBSERVABILITY_INSUFFICIENT`.

The test is **not executable now merely because this review passes**; current review-time main is still the design base.

### M1 — exact source ACTIVE_WORK

PASS.

M0 -> M1 is constrained to one lock-path addition. Canonical read-back requires exact source Task, worker, principal, work_ref, collision key, lock ID, path, unexpired state, and regular blob. The pre-terminal `/next` control must return `ACTIVE_WORK` and create no transport. This distinguishes a genuine active source epoch from a pre-released or synthetic state.

### M2 — truth-neutral terminal while source lock remains active

PASS.

M1 -> M2 permits only the exact source `ABANDONED_TERMINAL.yml` and its licence sidecar. The source lock must remain exact and active. The terminal must bind exact Task/worker, `abandonment_count=1`, `truth_layer_effect=NONE`, and an `abandoned_at` after source acquisition. Truth/claim/review/outcome/evaluation/failed-route/Campaign/Task/Portfolio state may not change.

`SourceAcquisitionV1` is captured only while the exact source acquisition and exact terminal blob are canonically observable, preventing a caller from manufacturing an old epoch from Task/worker prose alone.

### M3 — trusted RELEASE, old ownership canonically absent

PASS.

The first `/next` may create/reuse only the deterministic source RELEASE transport. Before canonical RELEASE, duplicate `/next` must reuse the same ref and PR and may not create ACQUIRE.

Trusted RELEASE is the only canonical mutation authority. M2 -> M3 is required to delete exactly `coordination/locks/eq18/general-structural-obstruction.yml`. A merged PR status is insufficient: fresh current-main read-back must prove the complete source lock bundle absent and exact source-epoch release provenance present.

This cleanly distinguishes correct RELEASE from stale PR status, unrelated lock activity, old acquisition, wrong worker/principal/work_ref/collision, or a partial deletion.

### M4 — exact expected next acquisition

PASS.

All pre-RELEASE ranking/reservation observations are discarded. On fresh M3, the accepted selector must freshly recompute the complete eligible/ranked sets from current canonical state and fresh validated PENDING observations. The result must be exactly:

- Task: `TASK-DITTERT-N5-001`
- relation: `GLOBAL_READY`
- worker: `w-0bebfd2fd11cb67f`
- principal: `gh:51mns`
- work_ref: `research/TASK-DITTERT-N5-001/w-0bebfd2fd11cb67f`
- collision bundle: exactly `dittert-n5/broader-zero-pattern`

If the repository legitimately changes and another Task becomes the correct deterministic choice, the field test must abort as `PRECONDITION_DRIFT`. It may not silently adapt the preregistered expected Task.

`AcquireIntentV1`, deterministic `next-acquire/<intent>/<Task>/<worker>` ref, deterministic `LOCK-NEXT-...` ID, immutable first-creator timestamp, exact lock blob, exact PR/head/base, and exact-head successful `verify` run are all bound before trusted ACQUIRE.

M3 -> M4 is required to add exactly `coordination/locks/dittert-n5/broader-zero-pattern.yml` and nothing else.

`ACTIVE_NEXT` is accepted only after fresh canonical read-back exactly equals `ExpectedAcquireV1` on Task, worker, principal, work_ref, complete collision set, deterministic lock ID, M3 base, acquired/expires timestamps, path set, and blob bytes. A same-Task/same-worker lock from another epoch is explicitly insufficient.

## Expected-next drift policy

PASS.

The expected next Task is preregistered rather than assumed. The test requires fresh reranking only after canonical RELEASE and treats any legitimate or illegitimate deviation from `TASK-DITTERT-N5-001` as `PRECONDITION_DRIFT`. This is the correct policy for a field test whose purpose is to distinguish one exact transition rather than merely demonstrate that some scheduler output is internally valid.

Selection context drift before ACQUIRE transport creation invalidates the selection/intent and aborts this preregistered run rather than being repaired into a different expected result.

## Negative controls

### Wrong worker, same principal

PASS.

At M1, the explicit `w-e8912c097a3288e1` control under authenticated `gh:51mns` must fail closed, create no RELEASE/ACQUIRE object, leave main unchanged, and preserve the exact source lock. This proves principal identity does not substitute for scheduler worker identity.

### Duplicate during RELEASE_PENDING

PASS.

The duplicate must reuse the exact same RELEASE ref and open PR, create no second equivalent transport, create no ACQUIRE while source ownership is canonical, and leave main at M2.

### Duplicate during ACQUIRE_PENDING

PASS.

The duplicate must preserve the same source epoch, selection ID, acquire-intent ID, deterministic ref, PR, lock payload, and first-creator timestamp. It must not recreate RELEASE or create a second ACQUIRE, and main remains M3.

### Old source epoch replay after M4

PASS.

Replay must return `OLD_ACQUISITION_REPLAY` or an equivalent fail-closed authority result and must not create/reuse transport authority for a different acquisition, mutate the new lock, recreate source RELEASE, or move main.

### Final duplicate after ACTIVE_NEXT

PASS.

The duplicate must re-read the exact `ExpectedAcquireV1` state and return `ACTIVE_NEXT` without creating transport or changing canonical state.

### Unrelated lifecycle PR appearing mid-test

PASS as a fail-closed observational control.

The plan correctly does not fabricate a competing live PR just to test races. Instead, every mutation boundary requires a complete fresh lifecycle-queue observation. If any unrelated eligible RELEASE/ACQUIRE appears such that trusted ordering is ambiguous, the field test aborts before the trusted run. Accepted Phase B is separately required to carry deterministic adversarial tests for simultaneous/competing lifecycle candidates.

### Rank/precondition drift

PASS.

Fresh M3 reranking is mandatory and exact expected Task mismatch aborts. Any selection context change before ACQUIRE transport creation invalidates the intent.

### Ruleset unreadable or weak

PASS.

Ruleset evidence is an execution prerequisite. Unreadable/malformed evidence, `strict=false`, missing `verify`, or bypass use aborts/fails closed; this test does not change settings to manufacture success.

### CI red, missing, or stale-head green

PASS.

Only exact-current-head `Verify public release` success is actionable. Red/missing CI blocks activation; head movement invalidates old success and requires fresh verification.

### Exact lock mismatch

PASS.

M4 is not accepted on approximate identity. Any mismatch in lock ID, Task, worker, principal, work_ref, collision set, base SHA, timestamps, path set, or blob bytes fails `ACTIVE_NEXT`.

## Truth / claim / research-acceptance sentinels

PASS.

The plan freezes semantic sentinels at M0 for:

- full `research/**` tree;
- `research/**/CLAIM.yml`;
- `reviews/**/REVIEW.yml`;
- `coordination/outcomes/**`;
- `coordination/evaluations/**`;
- `coordination/failed-routes/**`;
- `coordination/campaigns/**`;
- `coordination/tasks/**`;
- `coordination/portfolio/**`.

In addition, every M0 -> M4 main transition has an exact narrow path-delta contract. In combination, these checks are stronger than relying on semantic filenames alone: an accidental proof/research/review/governance mutation outside the named semantic files would still violate the exact transition delta and abort the run.

The allowed core-test residue is therefore limited to source lock add/delete, the source truth-neutral terminal marker plus licence, and the exact expected-next lock. The plan adequately proves:

- `TRUTH_EFFECT=NONE`
- `CLAIM_EFFECT=NONE`
- `REVIEW_EFFECT=NONE`
- `RESEARCH_RESULT_ACCEPTANCE_EFFECT=NONE`

No omitted namespace creates a successful-path hole under the required full transition-diff checks.

## Cleanup review

PASS.

Optional cleanup occurs only after M4 evidence is frozen. It terminalises the Dittert field-test worker with another truth-neutral `SCOPE_STOP` abandonment, merges that ordinary terminal through normal policy, then invokes the **existing exact-worker RELEASE primitive directly**.

Cleanup explicitly does **not** call `/next` again, so it cannot legitimately continue into a third Task through the tested continuation path.

If cleanup cannot be safely completed, leaving the exact Dittert lock active and escalating is the safest fail-closed choice. Manual lock deletion, settings bypass, or ad-hoc repair would destroy the acquisition/release provenance the test is intended to validate. The ordinary lease expiry remains governed by existing policy.

## Observability review

PASS.

The execution evidence contract is sufficient to diagnose the requested failure classes. It records at minimum:

- M0, M1, M2, M3, M4 full main SHAs and tree SHAs;
- exact compare/path delta at every transition;
- source/next lock paths, canonical blob OIDs, and decoded payloads;
- terminal path/blob/payload;
- `source_epoch_id` plus canonical `SourceAcquisitionV1` input;
- `ContinuationContextV1` and `continuation_context_id`;
- `SelectionV1` and `selection_id`;
- `AcquireIntentV1` and `acquire_intent_id`;
- `ExpectedAcquireV1` and `expected_acquire_id`;
- RELEASE/ACQUIRE and setup PR numbers, refs, exact head/base SHAs;
- exact-head Verify run IDs and conclusions;
- fresh effective Ruleset evidence;
- complete validated PENDING observation digest;
- complete `hard_eligible_task_ids` and deterministic `ranked_task_ids`;
- wrong-worker, duplicate, replay, and final-idempotency results;
- semantic sentinel comparisons.

If the accepted merged Phase B implementation cannot expose this evidence, the plan requires abort as `FIELD_TEST_OBSERVABILITY_INSUFFICIENT`; therefore lack of diagnostics cannot be misreported as a field-test PASS.

## Findings

### CRITICAL

None.

### HIGH

None.

### MEDIUM

None.

### LOW

None blocking or safety-relevant.

One non-blocking review note: the M0 setup names both `BASE_RESEARCH_TREE` and narrower semantic sentinels, while the later semantic checklist emphasizes the narrower namespaces. This does not create a coverage gap because the plan separately requires exact narrow Git path deltas for every M0 -> M4 transition and the execution evidence bundle records those compares. Recording the full `BASE_RESEARCH_TREE` equality in the final evidence bundle is useful redundancy but does not require a plan change.

## Final assessment

The reviewed plan can conclusively distinguish the exact intended `/next` transition from:

- unrelated locks/lifecycle activity;
- old acquisition replay;
- duplicate transports;
- stale PR/base/head/CI/main;
- wrong Task;
- wrong worker;
- wrong principal;
- wrong work_ref;
- wrong collision bundle;
- non-equivalent lock identity;
- accidental Truth/claim/review/research-result acceptance side effects.

It does so without fabricating mathematical work, without broadening trusted mutation authority, without changing repository security settings, and without using cleanup to trigger another continuation.

**VERDICT: PASS**

**READY_AFTER_ACCEPTED_PHASE_B: YES**

Execution remains gated on a fresh Phase-0 proof that accepted Phase B is merged and that every preregistered repository, Ruleset, worker-history, collision/capacity, lifecycle-queue, rank, CI, and observability precondition still holds.