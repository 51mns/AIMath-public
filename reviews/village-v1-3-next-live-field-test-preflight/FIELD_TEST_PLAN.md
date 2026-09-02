# Village v1.3 `/next` live field-test preflight

TASK-ID: `AIMATH-VILLAGE-V1-3-NEXT-LIVE-FIELD-TEST-PREFLIGHT`

Status: **READY_AFTER_PHASE_B_ACCEPTED_AND_MERGED**

Repository: `51mns/AIMath-public`

Preflight base/current-main SHA at design time:

```text
df7ceb5e685239b936950a0dd01a13e4e38b69eb
```

Parent frozen `/next` contract:

```text
commit 5eed8cc40243eba166afee651104f3c4a79d99ac
path   reviews/village-v1-3-next-preflight/NEXT_FROZEN_SPEC.md
blob   ad851bd4fece0f3f45126ae12da3b54a3a7a5832
```

Additional Phase B transport preflight consulted for executable transport identity:

```text
branch design/village-v1-3-next-phase-b-transport-preflight
commit c3532324e9df421afc787aa6cee3d91f8dbaa91e
path   reviews/village-v1-3-next-phase-b-transport-preflight/PHASE_B_FROZEN_SPEC.md
blob   5c877ec4d9807f285cb2e2c4c3f3ae3380117271
```

That Phase B branch is **not current-main authority at design time**. The live test may start only after an accepted Phase B implementation/equivalent contract has been merged to `main`. If the accepted merged implementation changes any authority/equality rule below, stop and return to design/security review rather than adapting this test ad hoc.

This lane designs the test only. It creates no production lock, PR, setting change, claim, outcome, or research result.

---

## 1. Purpose

Run one safe live end-to-end `/next` continuation after Phase B is accepted and merged, proving the complete externally observable chain:

```text
ACTIVE_WORK
  -> canonical ABANDONED_TERMINAL
  -> /next
  -> RELEASE transport
  -> trusted automatic RELEASE
  -> fresh main: old ownership absent
  -> fresh deterministic next selection
  -> ACQUIRE transport
  -> trusted automatic ACQUIRE
  -> fresh main: exact expected new ownership
  -> ACTIVE_NEXT
```

The test is an orchestration/lifecycle test only. It must not create a mathematical claim, pretend that research succeeded or failed, admit a research result, change review grade, or promote Truth Layer state.

The acceptance question is not “did some lock eventually appear?”. It is “did the exact retained worker move from the exact source acquisition epoch to the exact deterministically selected next acquisition, through the reviewed transports, with no other authority or side effect?”.

---

## 2. Frozen safe substrate

### 2.1 Identities

Use these exact non-secret scheduler identities:

```text
principal_id = gh:51mns
worker_id    = w-0bebfd2fd11cb67f
wrong_worker = w-e8912c097a3288e1
```

`worker_id` is deliberately fixed for this one field test so all read-backs are exact and reproducible. It is not a password, token, secret, signature, or GitHub authority credential.

Before Phase 0, both worker IDs must be absent from all canonical current-main locks and from all `work/<TASK>/<worker>/ABANDONED_TERMINAL.yml` paths. If either has prior canonical history, **abort rather than increment/reuse it**. This preserves a single clean acquisition epoch.

### 2.2 Source Task

Freeze the source as:

```text
SOURCE_TASK       = TASK-EQUIANGULAR-R18-001
SOURCE_CAMPAIGN   = CAM-EQUIANGULAR-R18
SOURCE_COLLISION  = eq18/general-structural-obstruction
SOURCE_LOCK_PATH  = coordination/locks/eq18/general-structural-obstruction.yml
SOURCE_WORK_REF   = research/TASK-EQUIANGULAR-R18-001/w-0bebfd2fd11cb67f
SOURCE_WORK_PATH  = work/TASK-EQUIANGULAR-R18-001/w-0bebfd2fd11cb67f/**
SOURCE_LOCK_ID    = LOCK-FIELDTEST-EQUIANGULAR-R18-001-0BEBFD2FD11CB67F
```

Why this source is suitable:

- it is an existing approved real Task, so no fake Task or governance object is introduced;
- current public state at the design base has no active source lock;
- the repository has already live-tested exact-worker RELEASE on the same Task with a different worker, so its one-key lock bundle is operationally understood;
- this test worker is new, so the earlier worker's durable abandonment record does not supply terminal authority for this epoch;
- no mathematical work is required for the field test.

### 2.3 Terminal form

Use **only** truth-neutral abandonment:

```text
work/TASK-EQUIANGULAR-R18-001/w-0bebfd2fd11cb67f/ABANDONED_TERMINAL.yml
work/TASK-EQUIANGULAR-R18-001/w-0bebfd2fd11cb67f/ABANDONED_TERMINAL.yml.license
```

Canonical payload:

```json
{
  "schema_version": 1,
  "task_id": "TASK-EQUIANGULAR-R18-001",
  "worker_id": "w-0bebfd2fd11cb67f",
  "reason": "SCOPE_STOP",
  "abandoned_at": "<UTC whole-second timestamp after SOURCE acquired_at>",
  "abandonment_count": 1,
  "last_work_head": null,
  "truth_layer_effect": "NONE"
}
```

License sidecar:

```text
SPDX-FileCopyrightText: 2026 AIMath contributors
SPDX-License-Identifier: CC0-1.0
```

`SCOPE_STOP` here means only that the deliberately bounded field-test work unit stops without doing mathematics. Do **not** create `coordination/outcomes/TASK-EQUIANGULAR-R18-001.yml`; do not describe this as a theorem failure, no-go result, counterexample, inconclusive mathematical result, or review result.

The marker is intentionally durable audit evidence. Its deletion is not part of cleanup.

### 2.4 Capability profile

Freeze the `/next` capability input as:

```text
github_write   = yes
local_compute  = yes
web_literature = yes
```

Do not change capability values mid-epoch.

### 2.5 Expected next Task

Freeze:

```text
EXPECTED_NEXT_TASK       = TASK-DITTERT-N5-001
EXPECTED_NEXT_CAMPAIGN   = CAM-DITTERT-N5
EXPECTED_NEXT_RELATION   = GLOBAL_READY
EXPECTED_NEXT_COLLISION  = dittert-n5/broader-zero-pattern
EXPECTED_NEXT_LOCK_PATH  = coordination/locks/dittert-n5/broader-zero-pattern.yml
EXPECTED_NEXT_WORK_REF   = research/TASK-DITTERT-N5-001/w-0bebfd2fd11cb67f
```

Rationale at the design base:

- Phase A excludes the completed source Task itself from `hard_eligible_task_ids`;
- `CAM-EQUIANGULAR-R18` has no second approved Task, so selection falls back to global READY work;
- under the fixed capability profile, `TASK-DITTERT-N5-001` is P1 + EXCLUSIVE + RESEARCH and receives the strongest P1 capability fit (`4`), ahead of the other current P1 candidates;
- current canonical evaluations contain no evaluation records that alter the ranking.

**This selection is preregistered, not assumed.** At live execution, the exact post-RELEASE canonical state and fresh direct-GitHub reservation observation must independently reproduce `TASK-DITTERT-N5-001`. If another Task is selected for any reason, even a legitimate new repository state, **abort this field test as PRECONDITION_DRIFT**. Do not silently change the expected Task.

### 2.6 Next ACQUIRE identity

Do not invent a static next lock ID before the post-RELEASE snapshot exists. The Phase B frozen transport contract intentionally binds it to the fresh selection.

At `M3` compute and freeze into the execution log:

```text
source_epoch_id        = SHA256(canonical(SourceAcquisitionV1))
continuation_context_id= SHA256(canonical(ContinuationContextV1))
selection_id           = SHA256(canonical(SelectionV1))
acquire_intent_id      = SHA256(canonical(AcquireIntentV1))
NEXT_ACQUIRE_REF       = next-acquire/<acquire_intent_id>/TASK-DITTERT-N5-001/w-0bebfd2fd11cb67f
NEXT_LOCK_ID           = LOCK-NEXT-<first 32 uppercase hex chars of acquire_intent_id>
```

This formula is the frozen lock-ID rule. The exact runtime hex value is unknown until the fresh post-RELEASE `selection_main_sha` and observation digest exist; recording that value is execution, not redesign.

---

## 3. Phase 0 — mandatory preconditions

No live mutation may begin until every row passes on one fresh observation window.

### 3.1 Accepted implementation boundary

Record:

```text
M0 = fresh refs/heads/main full SHA
```

Require all of:

1. `M0` contains the accepted/merged Village v1.3 Phase A and Phase B implementation and its required independent review/security acceptance.
2. The merged implementation still preserves the parent frozen spec commit `5eed8cc...` authority boundary.
3. The merged Phase B behaviour contains the equivalent of:
   - source epoch exact binding;
   - post-RELEASE fresh-main barrier;
   - deterministic `next-acquire/<intent>/<Task>/<worker>` transport;
   - deterministic `LOCK-NEXT-...` identity;
   - exact expected-acquisition read-back before `ACTIVE_NEXT`;
   - duplicate reuse and `OLD_ACQUISITION_REPLAY` rejection.
4. `scripts/lock_auto_activate.py` remains a narrow trusted-main lifecycle mutation primitive; `/next` selection/transport creation is not moved into untrusted PR-head mutation authority.
5. `python3 scripts/village.py validate` and the complete accepted v1.3/v1.2.1 test suite pass from an exact checkout of `M0`.

If the merged implementation does not expose enough machine-readable diagnostics to record `SourceAcquisitionV1`, `SelectionV1`, `AcquireIntentV1`, transport head/base SHA and `ExpectedAcquireV1`, abort as `FIELD_TEST_OBSERVABILITY_INSUFFICIENT`.

### 3.2 GitHub server gates

Fresh-read and record:

- effective rules for `main`;
- strict required-status policy is true;
- required context includes exact `verify`;
- no bypass used for the test;
- trusted lifecycle workflow is enabled and unchanged from its accepted security boundary;
- authenticated principal resolves independently to `gh:51mns`.

Any unreadable/malformed/weak strict gate is an abort. Do not change settings inside this test.

### 3.3 Clean lifecycle queue

Fresh-observe the complete bounded open-PR set for base `main` and exact-head CI.

Require:

- no currently eligible RELEASE PR unrelated to this test;
- no currently eligible ACQUIRE PR that the trusted Phase B scanner could select ahead of this test;
- no open conflicting deterministic source RELEASE ref;
- no open/ref conflict at the future deterministic ACQUIRE key once that key is known;
- no malformed/truncated repository-wide PR observation.

Because trusted lifecycle orders eligible RELEASE before ACQUIRE and then deterministically considers eligible ACQUIRE candidates, an unrelated eligible lifecycle PR would confound this field test. Abort; do not close somebody else's PR as part of the test.

### 3.4 Canonical Village substrate

On exact `M0` require:

- Village validation PASS;
- `SOURCE_TASK` runtime `READY`;
- `EXPECTED_NEXT_TASK` runtime `READY` before source acquisition;
- no active lock for source or next Task;
- source and next collision keys unowned;
- Campaign/global capacity available;
- source frontier not stale;
- source assumptions and next assumptions usable;
- no same-worker abandonment marker for either source or expected next;
- no current-main outcome for `SOURCE_TASK` created by this test identity;
- no current-main `PENDING_CLAIM` or open lock transport that changes the preregistered post-release ranking.

### 3.5 Baseline side-effect snapshot

Record exact Git tree/OID or complete path+blob manifests for these protected semantic namespaces at `M0`:

```text
BASE_RESEARCH_TREE        = research/**
BASE_CLAIM_BLOBS          = research/**/CLAIM.yml
BASE_REVIEW_BLOBS         = reviews/**/REVIEW.yml
BASE_OUTCOME_TREE         = coordination/outcomes/**
BASE_EVALUATION_TREE      = coordination/evaluations/**
BASE_FAILED_ROUTE_TREE    = coordination/failed-routes/**
BASE_CAMPAIGN_TREE        = coordination/campaigns/**
BASE_TASK_TREE            = coordination/tasks/**
BASE_PORTFOLIO_TREE       = coordination/portfolio/**
```

These exact snapshots are later equality sentinels for “no Truth/claim/research acceptance side effect”.

### 3.6 Audit ledger to fill during execution

Before the first mutation, create a local/non-canonical execution ledger with these symbolic slots:

```text
M0  post-Phase-B clean main
M1  source ACQUIRE canonical main
M2  terminal marker canonical main
M3  trusted source RELEASE canonical main
M4  trusted expected-next ACQUIRE canonical main

PR_SOURCE_ACQUIRE
PR_TERMINAL
PR_RELEASE
PR_NEXT_ACQUIRE

SOURCE_ACQUIRE_HEAD
TERMINAL_HEAD
RELEASE_HEAD
NEXT_ACQUIRE_HEAD

SOURCE_EPOCH_ID
TERMINAL_BLOB
RELEASE_VERIFY_RUN
SELECTION_ID
ACQUIRE_INTENT_ID
NEXT_LOCK_ID
NEXT_VERIFY_RUN
EXPECTED_ACQUIRE_ID
```

PR numbers and runtime SHA/digest values are intentionally filled from GitHub observations. Their **roles, refs, payload equality and allowed path sets are frozen here**.

---

## 4. Stage the disposable ACTIVE_WORK source

This is test setup, not `/next` itself.

### 4.1 Source ACQUIRE object

Create the ordinary existing v1.2-compatible lock-only source transport from exact `M0`:

```text
head ref: lock/TASK-EQUIANGULAR-R18-001/w-0bebfd2fd11cb67f
base:     main @ M0
changed path only:
  coordination/locks/eq18/general-structural-obstruction.yml
```

The payload must be exactly:

```json
{
  "schema_version": 1,
  "lock_id": "LOCK-FIELDTEST-EQUIANGULAR-R18-001-0BEBFD2FD11CB67F",
  "task_id": "TASK-EQUIANGULAR-R18-001",
  "worker_id": "w-0bebfd2fd11cb67f",
  "actor": {
    "id": "gh:51mns",
    "type": "HUMAN_PRINCIPAL"
  },
  "base_main_sha": "<M0>",
  "acquired_at": "<UTC whole-second first-creator timestamp>",
  "expires_at": "<acquired_at + exactly 168 hours>",
  "work_ref": "research/TASK-EQUIANGULAR-R18-001/w-0bebfd2fd11cb67f",
  "collision_keys": [
    "eq18/general-structural-obstruction"
  ],
  "renewal_count": 0
}
```

Open one non-draft lock-only PR, require exact-head `Verify public release = SUCCESS`, and allow only the existing trusted automatic ACQUIRE path to merge it. Record the PR number, head SHA, verify run ID and merge SHA as `M1`.

If any additional path is present, abort before merge.

### 4.2 M1 read-back — prove ACTIVE_WORK

Fresh-read `main` after trusted merge. Require:

```text
main == M1 != M0
active lock set added exactly SOURCE_LOCK_ID
SOURCE_LOCK_PATH exists as 100644 blob
payload.task_id       == SOURCE_TASK
payload.worker_id     == worker_id
payload.actor.id      == principal_id
payload.work_ref      == SOURCE_WORK_REF
payload.collision_keys== [SOURCE_COLLISION]
lock remains unexpired
no other lock path was added/changed/removed
```

Run `/next` **before** terminalisation with the exact worker/principal. Expected state: `ACTIVE_WORK`, no RELEASE/ACQUIRE transport creation.

This is the proof that the test genuinely begins at current active research ownership rather than a pre-released synthetic snapshot.

### 4.3 Principal-versus-worker negative control

Still on `M1`, invoke `/next` under authenticated `gh:51mns` but present:

```text
wrong_worker = w-e8912c097a3288e1
```

Expected:

- fail-closed exact-worker binding mismatch;
- no RELEASE ref/PR;
- no ACQUIRE ref/PR;
- no main mutation;
- source canonical lock unchanged.

This proves the GitHub principal does not substitute for the worker scheduler identity: same principal + wrong worker cannot operate the exact worker's acquisition.

---

## 5. Canonical truth-neutral terminalisation

From fresh `M1`, create the worker research ref:

```text
research/TASK-EQUIANGULAR-R18-001/w-0bebfd2fd11cb67f
```

and a normal non-lock PR containing **only**:

```text
A work/TASK-EQUIANGULAR-R18-001/w-0bebfd2fd11cb67f/ABANDONED_TERMINAL.yml
A work/TASK-EQUIANGULAR-R18-001/w-0bebfd2fd11cb67f/ABANDONED_TERMINAL.yml.license
```

Use the frozen payload in Section 2.3. `abandoned_at` must be after `SOURCE acquired_at` and not unreasonably in the future. `last_work_head` stays `null` to avoid self-referential commit identity.

All commits must pass DCO and ordinary repository policy. This terminal PR is **not** auto-merged by the lock lifecycle; merge it through the ordinary allowed path only after CI passes.

Record the terminal blob SHA and resulting canonical main as `M2`.

Fresh M2 read-back must prove:

- source lock is still exact and active;
- terminal file is exact regular blob;
- schema validation passes;
- task and worker equal the source acquisition;
- `abandonment_count = 1`;
- `truth_layer_effect = NONE`;
- no `coordination/outcomes/**` change;
- no `research/**/CLAIM.yml` change;
- no `reviews/**/REVIEW.yml` change;
- no `coordination/failed-routes/**` change;
- no evaluation/campaign/task/portfolio change.

Capture `SourceAcquisitionV1` from the exact source lock blob bundle plus this terminal blob and record `SOURCE_EPOCH_ID`.

---

## 6. `/next` -> exact RELEASE transport

### 6.1 First `/next`

Invoke the accepted merged `/next` interface using:

```text
source_task_id = TASK-EQUIANGULAR-R18-001
worker_id      = w-0bebfd2fd11cb67f
principal_id   = gh:51mns
capabilities   = yes/yes/yes
source epoch   = exact SOURCE_EPOCH_ID or its accepted reconstructable equivalent
```

Expected Phase A/B derivation:

```text
RESULT_RECORDED
-> CONTINUATION_DECISION
-> RELEASE_PENDING
```

Expected physical RELEASE identity:

```text
release/TASK-EQUIANGULAR-R18-001/w-0bebfd2fd11cb67f
```

The RELEASE PR must:

- be same repository, base `main @ M2`, open, non-draft;
- be authored by expected principal;
- delete exactly `SOURCE_LOCK_PATH` and no other path;
- contain no additions/modifications;
- bind exact source lock ID, worker, principal, acquired_at, work_ref, collision key, path and base blob;
- have exact-head Verify success before lifecycle eligibility.

Record `PR_RELEASE`, its exact head SHA and verify run.

### 6.2 Duplicate `/next` while RELEASE pending

Before trusted RELEASE merges, invoke `/next` again for the same exact source epoch.

Require:

- exact same RELEASE ref reused;
- exact same open PR reused;
- no second release ref;
- no second release PR;
- no ACQUIRE transport created while source lock is still canonical;
- main remains `M2`.

Any duplicate object is test failure.

### 6.3 Trusted automatic RELEASE

Trigger/observe the existing trusted lifecycle. Do not manually merge the RELEASE PR.

Require the trusted current-main code to rederive all release gates and merge at most this one lifecycle mutation.

Fresh-read main and record `M3` only after canonical merge is observed.

M3 must satisfy:

```text
SOURCE_LOCK_PATH absent
SOURCE_LOCK_ID absent from all active/nonexpired canonical bundles
terminal marker still present unchanged
no next lock yet
no unrelated lock added/removed
M3 != M2
```

The exact `M2 -> M3` path delta is only:

```text
D coordination/locks/eq18/general-structural-obstruction.yml
```

This is the canonical proof that old ownership ended. An open/merged PR status without current-main path absence is insufficient.

---

## 7. Fresh post-RELEASE barrier and deterministic next selection

Discard all pre-RELEASE ranking/reservation observations.

On exact fresh `M3`, record:

- new full main SHA/tree;
- exact absence of source lock bundle;
- exact merged RELEASE provenance bound to `SOURCE_EPOCH_ID`;
- fresh current Village validation;
- fresh complete bounded open-PR observation;
- fresh valid PENDING reservation set/digest;
- fixed capability profile;
- canonical continuation inputs.

Require source terminal evidence blob unchanged.

Run the merged Phase A selection through the accepted Phase B adapter. The exact result must be:

```text
phase                = ACQUIRE_PENDING
selected_task_id     = TASK-DITTERT-N5-001
selected_relation    = GLOBAL_READY
worker_id            = w-0bebfd2fd11cb67f
principal_id         = gh:51mns
work_ref             = research/TASK-DITTERT-N5-001/w-0bebfd2fd11cb67f
collision_keys       = ["dittert-n5/broader-zero-pattern"]
```

Record the complete `hard_eligible_task_ids`, complete deterministic `ranked_task_ids`, `ContinuationContextV1`, `SelectionV1`, `continuation_context_id` and `selection_id`.

If `TASK-DITTERT-N5-001` is not selected, abort as preregistered substrate drift. Do not accept a different Task merely because the new rank is internally valid.

This phase is where deterministic next Task selection is proven.

---

## 8. Exact epoch-specific ACQUIRE transport

Construct `AcquireIntentV1` from the exact M3 selection and record `ACQUIRE_INTENT_ID`.

Require the physical ref to be exactly:

```text
next-acquire/<ACQUIRE_INTENT_ID>/TASK-DITTERT-N5-001/w-0bebfd2fd11cb67f
```

Require exactly one lock path:

```text
coordination/locks/dittert-n5/broader-zero-pattern.yml
```

Require lock ID:

```text
LOCK-NEXT-<first 32 uppercase hex chars of ACQUIRE_INTENT_ID>
```

The first successful transport creator captures one whole-second `acquired_at`; duplicates must reuse it exactly. `expires_at = acquired_at + 168 hours` for the current Task TTL.

The expected payload must contain exact:

```text
schema_version  = 1
lock_id         = NEXT_LOCK_ID
task_id         = TASK-DITTERT-N5-001
worker_id       = w-0bebfd2fd11cb67f
actor.id        = gh:51mns
actor.type      = HUMAN_PRINCIPAL
base_main_sha   = M3
work_ref        = research/TASK-DITTERT-N5-001/w-0bebfd2fd11cb67f
collision_keys  = [dittert-n5/broader-zero-pattern]
renewal_count   = 0
```

The PR must be same repository, open, non-draft, exact base `M3`, and add exactly that one regular `100644` lock blob. No other path is permitted.

### 8.1 Duplicate `/next` while ACQUIRE pending

Before trusted ACQUIRE merges, invoke `/next` again for the same source epoch.

Require:

- exact same `source_epoch_id`, `selection_id`, `acquire_intent_id`;
- exact same deterministic ACQUIRE ref reused;
- same PR reused;
- same lock payload and first-creator `acquired_at` reused;
- no second ACQUIRE PR/ref;
- source RELEASE not recreated;
- main remains `M3`.

### 8.2 No unrelated lock accepted

Before allowing trusted ACQUIRE, fresh-read every canonical/open lifecycle object and freeze the expected main lock-set transition:

```text
M3 canonical lock set: no field-test source/next lock
M4 canonical lock set: exactly NEXT_LOCK_ID added at EXPECTED_NEXT_LOCK_PATH
```

The trusted run may not add a second lock path, unrelated lock ID, different collision bundle, or a lock for another Task. If an unrelated eligible RELEASE/ACQUIRE becomes visible, abort before the trusted run rather than letting ordering make the experiment ambiguous.

---

## 9. Trusted automatic ACQUIRE -> ACTIVE_NEXT

Require exact-head `Verify public release = SUCCESS` for `PR_NEXT_ACQUIRE` and record the run ID.

Build `ExpectedAcquireV1` from the exact transport head before trusted merge, including:

- source epoch;
- selection/continuation IDs;
- selected Task;
- exact retained worker and principal;
- exact work_ref;
- exact collision bundle;
- deterministic lock ID;
- exact M3 base;
- exact acquired/expires timestamps;
- exact expected path/blob bundle;
- exact PR number/ref/head/base;
- exact successful Verify run.

Allow only the existing trusted lifecycle to merge ACQUIRE. It must revalidate current main/head/base, readiness, collision, worker/principal, capacity, exact objects, CI and strict server gate.

Fresh-read `main`; call it `M4` only after the merge is canonical.

`ACTIVE_NEXT` succeeds **only if** all of these hold exactly:

```text
canonical task_id       == TASK-DITTERT-N5-001
canonical worker_id     == w-0bebfd2fd11cb67f
canonical actor.id      == gh:51mns
canonical work_ref      == research/TASK-DITTERT-N5-001/w-0bebfd2fd11cb67f
canonical collision set == {dittert-n5/broader-zero-pattern}
canonical lock_id       == NEXT_LOCK_ID
canonical base_main_sha == M3
canonical acquired_at   == ExpectedAcquireV1.acquired_at
canonical expires_at    == ExpectedAcquireV1.expires_at
canonical path set      == {EXPECTED_NEXT_LOCK_PATH}
canonical blob bytes/OID == exact expected transport lock blob
canonical lock is active/unexpired
```

The exact `M3 -> M4` canonical path delta must be only:

```text
A coordination/locks/dittert-n5/broader-zero-pattern.yml
```

A green PR, merged PR status, same Task/worker lock with different lock ID, old lock, wrong work_ref, wrong collision bundle, different timestamp/blob, or unrelated same-worker/principal lock is **not** `ACTIVE_NEXT`.

---

## 10. Replay and idempotency adversarial checks

These checks run after `M4` and must perform no canonical mutation.

### 10.1 Replay the old source epoch

Replay the exact original `SOURCE_EPOCH_ID` through the accepted `/next` interface after `ACTIVE_NEXT` exists.

Expected result:

```text
OLD_ACQUISITION_REPLAY
```

or the accepted equivalent fail-closed status with the same authority meaning.

Require:

- no new RELEASE ref/PR;
- no recreation of the old source lock deletion transport;
- no new ACQUIRE ref/PR;
- no mutation of NEXT_LOCK_ID;
- no second next lock;
- main remains `M4`;
- current exact expected next lock remains untouched.

This proves an old epoch cannot release/acquire again or control a later acquisition.

### 10.2 Final duplicate `/next`

Invoke the same current continuation observation again after `M4`.

Require exact read-back of `ExpectedAcquireV1` and `ACTIVE_NEXT`; no transport creation or canonical mutation.

---

## 11. Truth, claim and research-acceptance non-effects

At `M4`, compare against the Phase-0 semantic snapshots.

All of these must be byte/tree identical to their `M0` sentinels except for unrelated external changes, which themselves are an abort condition for this controlled run:

```text
research/**/CLAIM.yml
reviews/**/REVIEW.yml
coordination/outcomes/**
coordination/evaluations/**
coordination/failed-routes/**
coordination/campaigns/**
coordination/tasks/**
coordination/portfolio/**
```

The only intended canonical semantic additions/deletions during the core test are:

1. source lock add, then source lock delete;
2. source truth-neutral `ABANDONED_TERMINAL.yml` + `.license` add;
3. exact expected next lock add.

Therefore:

```text
TRUTH_EFFECT = NONE
CLAIM_EFFECT = NONE
REVIEW_EFFECT = NONE
RESEARCH_RESULT_ACCEPTANCE_EFFECT = NONE
```

The field-test terminal marker is scheduling/availability evidence only.

---

## 12. Exact expected main transitions

| Main | Required state | Exact field-test lock set | Other allowed field-test canonical changes |
|---|---|---|---|
| `M0` | post-Phase-B clean precondition | none | none |
| `M1` | `ACTIVE_WORK` staged | `SOURCE_LOCK_ID` at `SOURCE_LOCK_PATH` | none |
| `M2` | canonical terminal evidence + source still active | same exact source lock | add only source `ABANDONED_TERMINAL.yml` + `.license` |
| `M3` | source released | neither source nor next lock | delete only `SOURCE_LOCK_PATH`; terminal remains |
| `M4` | exact next acquisition | `NEXT_LOCK_ID` at `EXPECTED_NEXT_LOCK_PATH` | add only expected next lock |

Every transition is fresh-read from `refs/heads/main`. Chat state, local checkout state and PR status are never substitutes.

---

## 13. Success criteria

The live field test is `PASS` only if **all** conditions hold:

1. Phase 0 passes with accepted Phase B merged and strict server gates intact.
2. Exact fixed worker `w-0bebfd2fd11cb67f` appears in both source and next canonical locks.
3. `gh:51mns` remains a separate actor/principal field, not a substitute worker identity.
4. Same principal + `wrong_worker` cannot release or advance the source acquisition.
5. Source begins as a real current active canonical EXCLUSIVE lock.
6. Terminalisation is the exact current-acquisition `ABANDONED_TERMINAL`, `truth_layer_effect=NONE`.
7. First `/next` creates/reuses exactly one correct RELEASE transport.
8. Duplicate `/next` while RELEASE pending reuses it and creates no duplicate/ACQUIRE.
9. Trusted automatic RELEASE is the only source-lock canonical mutation.
10. Fresh `M3` proves complete source lock bundle/path absence.
11. Post-RELEASE selection is recomputed from fresh main + fresh PENDING observation.
12. Selected Task is exactly `TASK-DITTERT-N5-001` with relation `GLOBAL_READY`.
13. Selected work_ref is exactly `research/TASK-DITTERT-N5-001/w-0bebfd2fd11cb67f`.
14. Selected collision bundle is exactly `dittert-n5/broader-zero-pattern` and exactly one corresponding lock path.
15. ACQUIRE ref and `LOCK-NEXT-...` match the Phase B deterministic formulas.
16. Duplicate `/next` while ACQUIRE pending reuses exact intent/ref/PR/payload/timestamp.
17. Trusted automatic ACQUIRE is the only next-lock canonical mutation.
18. Fresh `M4` exact expected-acquisition read-back passes every Task/worker/principal/work_ref/collision/lock-id/time/path/blob equality.
19. No unrelated lock is accepted at any main transition.
20. `ACTIVE_NEXT` is returned only after M4 exact canonical read-back.
21. Old `SOURCE_EPOCH_ID` replay after M4 cannot release/acquire/create transport or mutate main.
22. Final duplicate is idempotent and creates nothing.
23. Claim/review/outcome/evaluation/failed-route/Campaign/Task/Portfolio sentinels remain unchanged.
24. No Truth promotion, claim promotion or research-result acceptance occurs.
25. Full execution ledger contains exact full SHAs, PR numbers, refs, head/base SHAs, workflow run IDs, lock/terminal blob OIDs, epoch/selection/intent IDs and compare results.

Anything less is not a partial PASS.

---

## 14. Abort conditions

Abort before the next mutation if any of the following becomes true:

- current main differs from the snapshot being acted on and the step requires that snapshot;
- accepted Phase A/Phase B implementation or independent security acceptance cannot be positively identified;
- Phase B merged semantics weaken or differ materially from the exact contracts preregistered here;
- effective strict `verify` gate cannot be positively read;
- repository-wide open-PR/main/tree/PENDING observation is incomplete, malformed or beyond reviewed bounds;
- another eligible RELEASE or ACQUIRE could make trusted lifecycle ordering ambiguous;
- source or expected next Task is not READY when required;
- source/next collision or capacity is consumed by unrelated work;
- fixed worker/wrong-worker IDs already have canonical terminal/lock history before setup;
- source acquisition payload/path/blob differs from Section 4;
- terminal timestamp is not after source acquisition or terminal record differs from Section 2.3;
- any semantic Truth/claim/review/outcome/failed-route namespace changes unexpectedly;
- wrong-worker negative control creates any transport or changes main;
- duplicate `/next` creates a second equivalent ref/PR/bundle;
- RELEASE changes any path except exact source lock deletion;
- M3 still contains any source lock blob/path or lacks exact source-epoch release provenance;
- post-release rank does not select exactly `TASK-DITTERT-N5-001`;
- selection context changes before ACQUIRE transport creation;
- deterministic ACQUIRE key already exists with non-equivalent content;
- ACQUIRE PR base/head/CI moves without fresh recomputation/reverification;
- trusted lifecycle accepts any unrelated lock or more than one mutation in a run;
- M4 lock differs from `ExpectedAcquireV1` in any field/path/blob/time;
- replayed old epoch creates/reuses authority for a different acquisition rather than stopping;
- any step would require a settings change, bypass, PAT/secret addition, manual lock merge, RENEW, TAKEOVER, Truth promotion, review promotion, or ad hoc Task selection.

On abort, preserve collected read-back evidence, stop further automatic mutation, and report the first violated invariant to the Village coordinator. Do not “repair” the experiment by changing the preregistered expected Task or worker.

---

## 15. Residual state and safe cleanup

### 15.1 State at the measurement stop

The primary measurement stop is immediately after replay/idempotency checks at `M4`.

Expected residual canonical state:

- durable source `ABANDONED_TERMINAL.yml` + license remain as truth-neutral audit evidence;
- exact `TASK-DITTERT-N5-001` next lock remains active under `w-0bebfd2fd11cb67f`;
- source lock is absent;
- no claim/outcome/review/evaluation/failed-route object was created or promoted;
- merged/closed GitHub transport/terminal PR history remains audit evidence;
- transport refs may remain unless repository operations policy safely deletes merged branches.

### 15.2 Optional cleanup after evidence freeze

Only after the coordinator has frozen the M4 evidence may cleanup begin.

To avoid leaving a 168-hour field-test lock occupying Dittert capacity:

1. add a second truth-neutral `ABANDONED_TERMINAL` for `TASK-DITTERT-N5-001/w-0bebfd2fd11cb67f`, again `SCOPE_STOP`, count `1`, `truth_layer_effect=NONE`;
2. merge that terminal record through ordinary policy;
3. use the existing exact-worker RELEASE primitive directly to release `NEXT_LOCK_ID`;
4. do **not** ask `/next` to continue again during cleanup, because that could legitimately select another Task;
5. fresh-read main to prove no active field-test lock remains;
6. re-run the semantic no-Truth/no-claim sentinel checks.

The two abandonment markers are intentionally durable and are not deleted. They are scheduling audit records, not mathematical outcomes. This is the only permanent canonical residue required by using real existing Tasks without fabricating mathematical results.

If cleanup cannot safely execute, leave the exact next lock untouched and escalate to the coordinator rather than using manual lock-file deletion or settings bypass.

---

## 16. Required execution evidence bundle

The coordinator should return/store, at minimum:

```text
M0 M1 M2 M3 M4 full main SHAs
M0..M4 main tree SHAs
exact compare/path delta for every transition
source and next lock path/blob OIDs and decoded payloads
terminal path/blob OID and decoded payload
SOURCE_EPOCH_ID and its canonical input JSON
ContinuationContextV1 + continuation_context_id
SelectionV1 + selection_id
AcquireIntentV1 + acquire_intent_id
ExpectedAcquireV1 + expected_acquire_id
all four core PR numbers:
  PR_SOURCE_ACQUIRE
  PR_TERMINAL
  PR_RELEASE
  PR_NEXT_ACQUIRE
exact ref/head/base SHA for each PR
exact-head Verify workflow run IDs/conclusions
fresh effective Ruleset read-back used by trusted mutation
complete fresh PENDING observation digest used by selection
complete hard_eligible_task_ids and ranked_task_ids
wrong-worker negative-control result
both duplicate-/next reuse results
old-epoch replay result
semantic namespace before/after tree/blob sentinels
optional cleanup SHAs/evidence, if cleanup is run
```

Do not substitute screenshots or prose for Git object/REST read-back when exact IDs are available.

---

## 17. Coordinator execution checklist

```text
[ ] Phase B accepted/merged and exact fixed boundary recorded
[ ] strict effective verify gate positively read
[ ] no competing eligible lifecycle PRs
[ ] fixed worker IDs pristine
[ ] M0 semantic sentinels frozen
[ ] source lock-only ACQUIRE trusted -> M1
[ ] M1 exact ACTIVE_WORK read-back
[ ] pre-terminal /next = ACTIVE_WORK, no transport
[ ] wrong-worker same-principal negative = fail closed, no transport
[ ] truth-neutral source abandonment canonical -> M2
[ ] SourceAcquisitionV1 + SOURCE_EPOCH_ID frozen
[ ] first /next -> one exact RELEASE transport
[ ] duplicate /next -> same RELEASE only
[ ] trusted RELEASE -> M3
[ ] fresh M3 proves source ownership gone
[ ] fresh rank exactly selects TASK-DITTERT-N5-001
[ ] SelectionV1 / AcquireIntentV1 frozen
[ ] one deterministic next-acquire transport created/reused
[ ] duplicate /next -> same ACQUIRE only
[ ] exact-head Verify green
[ ] ExpectedAcquireV1 frozen
[ ] trusted ACQUIRE -> M4
[ ] exact M4 canonical lock == ExpectedAcquireV1
[ ] ACTIVE_NEXT only now
[ ] replay old SOURCE_EPOCH_ID -> OLD_ACQUISITION_REPLAY/no mutation
[ ] final duplicate -> ACTIVE_NEXT/no mutation
[ ] no unrelated canonical lock accepted
[ ] Truth/claim/review/outcome/evaluation/failed-route sentinels unchanged
[ ] evidence bundle frozen
[ ] optional truth-neutral cleanup executed or residual next lock explicitly handed to coordinator
```

---

## 18. Frozen result

```text
TEST_SUBSTRATE = existing TASK-EQUIANGULAR-R18-001 -> truth-neutral ABANDONED_TERMINAL -> expected TASK-DITTERT-N5-001
WORKER_ID      = w-0bebfd2fd11cb67f
PRINCIPAL_ID   = gh:51mns
SOURCE_LOCK_ID = LOCK-FIELDTEST-EQUIANGULAR-R18-001-0BEBFD2FD11CB67F
NEXT_LOCK_ID   = LOCK-NEXT-<first 32 uppercase hex of runtime acquire_intent_id>
TRUTH_EFFECT   = NONE
CLAIM_EFFECT   = NONE
RESEARCH_RESULT_ACCEPTANCE_EFFECT = NONE
READY          = YES, AFTER ACCEPTED PHASE B IS MERGED AND ALL PHASE-0 PRECONDITIONS PASS
```
