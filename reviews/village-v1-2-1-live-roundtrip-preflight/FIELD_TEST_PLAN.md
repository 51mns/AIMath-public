# Village v1.2.1 live round-trip preflight

## Registration

- Task: `AIMATH-VILLAGE-V1-2-1-LIVE-ROUNDTRIP-PREFLIGHT`
- Repository: `51mns/AIMath-public`
- Preflight source main: `aae3b3be4a1da76eb4e1241ae7a366f39ff5f7f2`
- Preflight branch: `review/village-v1-2-1-live-roundtrip-preflight`
- Live mutation in this review: **NONE**
- PR creation / PR merge / repository-settings change in this review: **NONE**
- Truth Layer effect: **NONE**
- claim effect: **NONE**
- research-result acceptance effect: **NONE**

This document preregisters one production lifecycle round-trip to be run only after the strict-gate patch has landed on `main` and all runtime gates below pass.

## Frozen evidence at the preflight base

At `aae3b3be4a1da76eb4e1241ae7a366f39ff5f7f2`:

- `coordination/locks/**` contains no canonical `.yml` lock bundle.
- `coordination/outcomes/**` contains no Task outcome `.yml`.
- no `work/**/ABANDONED_TERMINAL.yml` exists.
- `coordination/portfolio/PORTFOLIO.yml` has `global_admission=OPEN` and global active-lane cap `12`.
- `TASK-EQUIANGULAR-R18-001` is stored `APPROVED`, `EXCLUSIVE`, lease TTL `168` hours, with exactly one collision key: `eq18/general-structural-obstruction`.
- `CAM-EQUIANGULAR-R18` is `ACTIVE`, with `max_active_lanes=2`; its frontier snapshot was checked `2026-09-01` with TTL `90` days.
- its load-bearing assumption `C-EQUIANGULAR-R18-ETA17-SINGLETON-EXCLUSION` is `CURRENT`, `FULL`, and dependency use is `ALLOWED`.
- maintainer / automatic-release principal is `51mns`.
- Field Test #29 used this same Task/collision key as transport-only ACQUIRE data. PR #29 was not merged; Verify run `33609693757` succeeded; trusted lifecycle run `33609727765` reached the strict-setting gate and failed closed on `403 Resource not accessible by integration`; no canonical ownership was created.
- a fresh read of `branches/main/protection/required_status_checks` during this preflight still returned `403 Resource not accessible by integration`. Therefore this plan MUST NOT be executed on the preflight base.

## Field-test substrate

Use existing Task `TASK-EQUIANGULAR-R18-001` with a new disposable worker:

`w-fae1dfc5fac514d0`

Frozen identities:

- principal: `gh:51mns`
- GitHub PR actor: `51mns`
- actor type: `HUMAN_PRINCIPAL`
- Task: `TASK-EQUIANGULAR-R18-001`
- campaign: `CAM-EQUIANGULAR-R18`
- collision key: `eq18/general-structural-obstruction`
- lock id: `LOCK-EQUIANGULAR-R18-001-FAE1DFC5FAC514D0`
- deterministic work ref: `research/TASK-EQUIANGULAR-R18-001/w-fae1dfc5fac514d0`

Why this is safe enough for the field test:

1. Field Test #29 already exercised the exact Task/key through public Verify and trusted candidate discovery without merging it.
2. The preflight base has no canonical ownership, no outcome, no abandonment marker, and no collision on this key.
3. Current campaign/global capacity has headroom.
4. The field test will not create a research outcome or claim artifact.
5. The only durable Task-local residual will be a schema-valid `ABANDONED_TERMINAL` for this disposable worker. It is availability/history evidence, not mathematical evidence, and `truth_layer_effect` is schema-forced to `NONE`.
6. Its 24-hour cooldown is scoped to this exact `(Task, worker)` pair, so other workers remain able to acquire the real Task after the test.

A test-only Task is therefore not required. If coordinator policy changes to forbid any durable field-test marker under a real Task, stop and create a separate proposal for a test-only Task; do not silently substitute another Task.

## Runtime bind-once values

The strict-gate patch has not yet landed, so its future merge SHA cannot truthfully be preregistered as a literal. The following binding rule is frozen instead.

Immediately after the strict-gate patch is integrated:

1. Fresh-read `remote main` full SHA and call it `TEST_BASE_SHA`.
2. Confirm the strict-gate implementation now reports the required setting as readable and true.
3. Confirm the diff from this preflight source base does not change Task/campaign/lock/terminal/release semantics except the reviewed strict-gate repair. If lifecycle semantics changed materially, this preflight is invalid and must be reviewed again.
4. Record `ACQUIRED_AT` as a UTC RFC3339 timestamp at lock creation, second precision, and set `EXPIRES_AT = ACQUIRED_AT + 168 hours` exactly.
5. Once `TEST_BASE_SHA` is bound, any unexpected movement of main before ACQUIRE merge is an abort. Do not rebase the candidate and continue under the same observation.

Expected main transitions are phase boundaries, not races:

`TEST_BASE_SHA -> ACQUIRE_MAIN_SHA -> TERMINAL_MAIN_SHA -> RELEASE_MAIN_SHA`.

Within each phase, any other main movement is an abort.

## Phase 0 — mandatory execution prechecks

Before creating a live ACQUIRE branch/PR, all must hold:

- strict gate: confirmed true and readable by the trusted lifecycle path;
- `python3 scripts/village.py validate` exits `0`;
- `python3 scripts/village.py status` reports `TASK-EQUIANGULAR-R18-001` as `READY`;
- `python3 scripts/test_village_v1_2_1.py` exits `0`;
- `python3 scripts/test_village_v1_2_1_phase_b.py` exits `0`;
- no canonical lock exists for the Task or collision key;
- no `coordination/outcomes/TASK-EQUIANGULAR-R18-001.yml` exists;
- no `work/TASK-EQUIANGULAR-R18-001/w-fae1dfc5fac514d0/ABANDONED_TERMINAL.yml` exists;
- worker `w-fae1dfc5fac514d0` has no active exclusive lock;
- campaign active lanes remain below `2`; global active lanes remain below `12`;
- no active collision / explicit conflict / owned-path conflict has appeared;
- no branch already exists at any of the three field-test refs below;
- no other **eligible** Village RELEASE or ACQUIRE PR is present. Invalid/stale historical PRs are non-authoritative, but an eligible competitor makes candidate selection nondeterministic for this preregistered test and therefore aborts the test.

Run repository commands from a fresh checkout in a macOS/Linux shell or the VS Code integrated terminal. Record command, exact checkout SHA, exit code, and output in the coordinator's field-test evidence.

## Phase 1 — ACQUIRE

Branch:

`lock/TASK-EQUIANGULAR-R18-001/w-fae1dfc5fac514d0`

Create it from exactly `TEST_BASE_SHA`.

The branch changes exactly one path, added as a regular Git mode `100644` blob:

`coordination/locks/eq18/general-structural-obstruction.yml`

Exact object, with only the three runtime-bound values substituted:

```json
{
  "schema_version": 1,
  "lock_id": "LOCK-EQUIANGULAR-R18-001-FAE1DFC5FAC514D0",
  "task_id": "TASK-EQUIANGULAR-R18-001",
  "worker_id": "w-fae1dfc5fac514d0",
  "actor": {
    "id": "gh:51mns",
    "type": "HUMAN_PRINCIPAL"
  },
  "base_main_sha": "<TEST_BASE_SHA>",
  "acquired_at": "<ACQUIRED_AT>",
  "expires_at": "<EXPIRES_AT>",
  "work_ref": "research/TASK-EQUIANGULAR-R18-001/w-fae1dfc5fac514d0",
  "collision_keys": [
    "eq18/general-structural-obstruction"
  ],
  "renewal_count": 0
}
```

The lock bundle contains exactly that one file because the Task has exactly one collision key.

ACQUIRE PR requirements:

- base: `main` at exact `TEST_BASE_SHA`;
- same-repository non-draft PR;
- actor `51mns`;
- lock-only addition; no research/governance/terminal file mixed in;
- all commits DCO signed;
- exact head gets latest `Verify public release = completed/success`;
- before trusted mutation, re-read main and candidate; if either moved, abort;
- expected trusted output includes `AUTO_ACTIVATED_PR=<this PR>`, `ACQUIRE_TASK_ID=TASK-EQUIANGULAR-R18-001`, `ACQUIRE_WORKER_ID=w-fae1dfc5fac514d0`, and a full `MERGE_SHA`.

Expected merge is the trusted lifecycle's squash merge. No human/manual merge is counted as `ACQUIRE_AUTO_MERGED`.

## Phase 2 — ownership read-back

After automatic ACQUIRE merge:

1. Fresh-read `main`; bind it as `ACQUIRE_MAIN_SHA` and require it to equal the trusted lifecycle `MERGE_SHA`.
2. Fetch the canonical lock path at `ACQUIRE_MAIN_SHA`.
3. Fetch the exact recursive Git tree for `ACQUIRE_MAIN_SHA`; require mode `100644`, type `blob`, and tree blob SHA equal to the Contents API blob SHA.
4. Parse and verify exact values for lock id, Task, worker, principal, collision keys, `base_main_sha`, `acquired_at`, `expires_at`, work ref, and renewal count.
5. Fetch the source ACQUIRE PR and require it is merged, its original base SHA was `TEST_BASE_SHA`, its head ref/head SHA are the verified candidate, and its merge SHA is `ACQUIRE_MAIN_SHA`.
6. Record the source PR number from PR metadata. `source_pr` is intentionally not a lock-schema field; provenance is established by the merged PR object + trusted lifecycle run + resulting main commit.
7. Run Village status and require the Task is `ACTIVE` with this canonical lock.

Only then set `OWNERSHIP_CONFIRMED`.

## Phase 3 — terminalisation

### RESULT_TERMINAL vs ABANDONED_TERMINAL

Do **not** use `RESULT_TERMINAL` for this field test. An outcome record under `coordination/outcomes/<TASK-ID>.yml` is a research-result object and can make Task runtime state `DONE` / `WAITING_REVIEW`; manufacturing such an object solely to exercise transport would pollute research semantics.

Use `ABANDONED_TERMINAL` instead. It has schema-enforced `truth_layer_effect: NONE`, is keyed to the exact worker, and exists specifically as durable availability state.

Terminal work branch:

`research/TASK-EQUIANGULAR-R18-001/w-fae1dfc5fac514d0`

Create it from exactly `ACQUIRE_MAIN_SHA`.

Add exactly:

`work/TASK-EQUIANGULAR-R18-001/w-fae1dfc5fac514d0/ABANDONED_TERMINAL.yml`

with:

```json
{
  "schema_version": 1,
  "task_id": "TASK-EQUIANGULAR-R18-001",
  "worker_id": "w-fae1dfc5fac514d0",
  "reason": "SCOPE_STOP",
  "abandoned_at": "<ABANDONED_AT>",
  "abandonment_count": 1,
  "last_work_head": null,
  "truth_layer_effect": "NONE"
}
```

`ABANDONED_AT` must be recorded after ownership confirmation, must not predate `ACQUIRED_AT`, and must not be more than five minutes in the future when current-main release eligibility is evaluated.

`SCOPE_STOP` means only that the preregistered field-test work scope ended after ownership read-back. It MUST NOT be described as a mathematical failure, negative result, or no-go theorem.

The terminalisation PR is an ordinary, manually reviewed transport PR, not an automatic lifecycle merge. It must contain no mathematical result and no lock mutation. Require Verify success, merge it normally, then fresh-read main as `TERMINAL_MAIN_SHA` and fetch/validate the marker from that SHA before opening RELEASE.

The marker is durable and must not be deleted for cleanup. Initial `abandonment_count` is exactly `1`. Its cooldown is:

`COOLDOWN_UNTIL = ABANDONED_AT + 24 hours`.

The cooldown affects only the same `(TASK-EQUIANGULAR-R18-001, w-fae1dfc5fac514d0)` reacquisition pair.

## Phase 4 — RELEASE

Branch:

`release/TASK-EQUIANGULAR-R18-001/w-fae1dfc5fac514d0`

Create it from exactly `TERMINAL_MAIN_SHA`.

The RELEASE branch changes exactly one path and only by deletion:

`coordination/locks/eq18/general-structural-obstruction.yml`

Do not delete or modify the abandonment marker in this PR.

RELEASE PR requirements:

- base `main` at exact `TERMINAL_MAIN_SHA`;
- same-repository, open, non-draft;
- PR actor `51mns`, exactly matching canonical lock principal and automatic-release allowlist;
- head ref exactly the release ref above;
- changed path set exactly equals the full canonical lock bundle;
- every changed file has status `removed`; no replacement/addition/modification;
- deleted base object is regular `100644` blob and its SHA matches the canonical main tree;
- exact PR head tree contains no deleted lock path;
- current-main terminal class is exactly `ABANDONED_TERMINAL` for the same Task/worker;
- latest Verify for the exact head SHA is success;
- no main/head/base movement between final revalidation and merge;
- strict gate remains readable and true.

Expected trusted output includes:

- `AUTO_RELEASED_PR=<this PR>`
- `RELEASE_TERMINAL_CLASS=ABANDONED_TERMINAL`
- `ABANDONMENT_COUNT=1`
- `REACQUIRE_COOLDOWN_UNTIL=<COOLDOWN_UNTIL>`
- `MERGE_SHA=<RELEASE_MAIN_SHA>`

An expired lock is mechanically releasable under v1.2.1, but this field test must not intentionally wait for expiry: if the lease becomes inactive before the planned terminalisation/release sequence, record an abort because the intended live-ownership round-trip was not completed as preregistered.

## Phase 5 — final read-back and cleanup

After automatic RELEASE merge:

1. Fresh-read `main` and bind `RELEASE_MAIN_SHA`; require it equals trusted lifecycle `MERGE_SHA`.
2. Require the canonical lock path is absent from the exact main tree and Contents API.
3. Require no lock bundle with `LOCK-EQUIANGULAR-R18-001-FAE1DFC5FAC514D0`, Task/worker, or collision key remains.
4. Require the exact abandonment marker still exists and validates with count `1`, reason `SCOPE_STOP`, and truth effect `NONE`.
5. Require `coordination/outcomes/TASK-EQUIANGULAR-R18-001.yml` is still absent.
6. Require Task, Campaign, Portfolio and load-bearing claim canonical blobs are unchanged from the post-strict-patch baseline, except for expected generated/runtime views if the strict patch itself intentionally changed them before the test. The field-test PRs themselves must not mutate those files.
7. Run Village validation/status. Campaign/global active-lane counts must return to their pre-test values; the Task remains available to other workers. The disposable same-pair worker is cooldown-blocked until `COOLDOWN_UNTIL`.
8. Record ACQUIRE, terminalisation and RELEASE PR numbers, exact head SHAs, Verify run IDs, trusted lifecycle run IDs, merge SHAs, lock/marker blob SHAs, and timestamps.

Transport branch refs may be deleted after all read-back is complete if normal repository housekeeping permits it. Branch deletion is not evidence deletion: merged PRs/commits and the durable abandonment marker remain. Never delete the marker or rewrite history in the name of cleanup.

Expected residual state:

- canonical lock: **absent**
- canonical ownership: **absent**
- `ABANDONED_TERMINAL`: **present, durable**
- research outcome: **absent**
- claim mutation: **none**
- Truth Layer mutation: **none**
- research-result acceptance mutation: **none**
- same-pair cooldown: **24 hours from ABANDONED_AT**
- other workers on the real Task: not blocked by this marker
- transport PR/commit history: retained

## Success criteria

All seven must be evidenced from remote read-back:

- `ACQUIRE_AUTO_MERGED`
- `OWNERSHIP_CONFIRMED`
- `TERMINAL_STATE_CONFIRMED`
- `RELEASE_AUTO_MERGED`
- `OWNERSHIP_REMOVED`
- `TRUTH_EFFECT_NONE`
- `CLAIM_EFFECT_NONE`

Additionally record `RESEARCH_RESULT_ACCEPTANCE_EFFECT_NONE`.

## Abort / fail-closed conditions

Abort before the next mutation on any of:

- strict gate false;
- strict gate unreadable;
- unexpected strict-gate bypass;
- trusted lifecycle selects a different candidate;
- another worker / eligible PR wins a race;
- unexpected main movement within a phase;
- candidate head movement or base movement;
- Task ceases to be READY before ACQUIRE;
- campaign/global/worker capacity changes;
- collision or explicit conflict appears;
- Verify/CI failure or stale latest Verify;
- wrong lock file set, wrong blob mode/type/SHA, or wrong bundle identity;
- principal, Task, worker, collision key, work ref, TTL, timestamp, or renewal mismatch;
- unexpected research/governance/claim/outcome mutation;
- pre-existing or malformed abandonment state for the disposable pair;
- terminal marker timestamp invalid, wrong count, wrong reason, or truth effect not `NONE`;
- strict patch changes lifecycle semantics beyond the reviewed strict-setting repair;
- any inability to read back exact remote main/PR/tree/blob evidence.

If an unexpected bypass has already merged the ACQUIRE, do not call the test successful and do not perform research. Freeze the lane, create the same truth-neutral `SCOPE_STOP` terminal marker under coordinator supervision, and use an audited cleanup RELEASE path. Preserve all evidence of the bypass; never hide it by history rewrite or marker deletion.

## Acceptance checklist

Before coordinator starts the live round-trip, freeze an execution record containing:

- `TEST_BASE_SHA`
- `ACQUIRED_AT`
- `EXPIRES_AT`
- worker / lock id / collision key
- observed strict-gate result
- zero eligible competing lifecycle candidates
- pre-test active-lane counts
- pre-test canonical Task/Campaign/Portfolio/claim blob SHAs

After each phase, append only remote-observed facts. Do not infer a merge, ownership, terminal state, or cleanup from local branch state.

## Preflight verdict

`READY_FOR_POST_STRICT_PATCH_EXECUTION = YES`

This means the procedure is frozen and executable immediately after the strict patch **if and only if** Phase 0 passes. It does not mean the current preflight base is live-test ready; the current strict-setting read is still fail-closed.