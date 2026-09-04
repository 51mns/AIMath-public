# Village ACTIVE_WORK production remediation — independent review

TASK-ID: `AIMATH-VILLAGE-V1-3-NEXT-ACTIVE-WORK-REMEDIATION-INDEPENDENT-REVIEW`

Review branch: `review/village-v1-3-next-active-work-remediation-final`

Review base:

```text
b01bf39c2387d8e1f0dc4cfd60d6e1bb56b0a10d
```

Fixed target:

```text
2848245c3a7daf36a3dd266e8f338ededa956dae
```

Disposition:

```text
VERDICT=PASS
REMEDIATION_ACCEPTED=YES
PR47_READY_FOR_MERGE=YES
```

This review does not repair production code, does not modify the target, does not alter the live source lock, and does not merge PR #47. It reviews the fixed production remediation against the frozen `/next` contract, accepted Phase-A semantics, the previous independent root-cause review, exact target Git objects, PR #47, and exact-head Verify run #122.

## 1. Fresh fixed identities

### 1.1 Current main

Fresh remote read at review time:

```text
CURRENT_MAIN=b01bf39c2387d8e1f0dc4cfd60d6e1bb56b0a10d
```

This equals the expected review base.

### 1.2 Live source lock

Canonical path:

```text
coordination/locks/eq18/general-structural-obstruction.yml
```

Exact blob:

```text
6604acaf8c458a4893fc746fd689326b0d5d3722
```

Exact identity:

```text
lock_id=LOCK-FIELDTEST-EQUIANGULAR-R18-001-0BEBFD2FD11CB67F
task_id=TASK-EQUIANGULAR-R18-001
worker_id=w-0bebfd2fd11cb67f
principal_id=gh:51mns
base_main_sha=7dc8541c0a9e19f37910e06bc4738375c4c7af00
acquired_at=2026-09-04T01:04:54Z
expires_at=2026-09-11T01:04:54Z
work_ref=research/TASK-EQUIANGULAR-R18-001/w-0bebfd2fd11cb67f
collision_key=eq18/general-structural-obstruction
renewal_count=0
```

The lock is unexpired at review time. It was not deleted, renewed, replaced, or otherwise modified by this review.

### 1.3 Previous independent root-cause review

Fixed review commit:

```text
b8a50e6a825f126d697c36751e4135ba772cdb70
```

Fixed review blob:

```text
d657a053f9d1f09f0368006ed3ccaf4debb4bcb7
```

The review was read in full. Its accepted direction is:

```text
ROOT_CAUSE=PRODUCTION_INTEGRATION_BUG
PRODUCTION_FIX_REQUIRED=YES
PLAN_FIX_REQUIRED=NO
VERDICT=PASS_REMEDIATION_DIRECTION
```

The load-bearing remediation requirement is that production Phase B must consume accepted Phase-A source-state semantics before terminal-bound `SourceAcquisitionV1` construction. It explicitly rejects a simplistic `active_only=True` source-bundle change because that could hide stale canonical source artifacts.

## 2. Target identity

Target commit:

```text
2848245c3a7daf36a3dd266e8f338ededa956dae
```

Exact parent:

```text
b01bf39c2387d8e1f0dc4cfd60d6e1bb56b0a10d
```

Changed paths are exactly:

```text
scripts/village_next_phase_b.py
scripts/test_village_v1_3_next_phase_b.py
```

Exact blobs:

```text
CORE=dc49ee57505929b4c374cc9595e251953864a41a
TEST=10bb80c1d4f3c27b0ce76c86fae0ee43c489e251
```

Commit message contains the required DCO trailer:

```text
Signed-off-by: Shoma Nakabayashi <199666487+51mns@users.noreply.github.com>
```

No other production, coordination, work, docs, workflow, schema, Truth, review-authority, RENEW, or TAKEOVER path is changed by the target.

## 3. Authoritative contract check

Frozen parent `/next` specification:

```text
commit=5eed8cc40243eba166afee651104f3c4a79d99ac
blob=ad851bd4fece0f3f45126ae12da3b54a3a7a5832
```

The contract says terminal evidence is required before RELEASE becomes eligible. It separately defines `ACTIVE_WORK` for exact active work still owned by the retained worker. Therefore terminal absence under exact active ownership is not itself an invalid `/next` invocation.

Accepted Phase-A production core:

```text
scripts/village_next.py
blob=39efe7efddc46ff43315e04b06df0baf4601327b
```

Accepted semantics are:

```text
exact active canonical source lock
+ exact Task/worker/principal binding
+ ordinary terminal absence
=> ACTIVE_WORK
=> canonical_ownership=True
=> required_action=NONE
```

The same core distinguishes a canonical stale/expired lock artifact using `active_only=False` followed by the active-lock view, and fails closed rather than treating the stale artifact as either active work or clean absence. Malformed terminal evidence and identity mismatches also fail closed.

## 4. Production core review

### 4.1 Existing trusted gates remain before ACTIVE_WORK

The fixed `cli_next()` still performs the following before it can emit `ACTIVE_WORK`:

1. `--github-write yes` requirement;
2. fresh remote `main` observation;
3. asserted-main equality;
4. independently authenticated GitHub principal;
5. asserted-principal equality;
6. exact local-HEAD equality with fresh remote main;
7. recursive current-main tree observation;
8. complete open-PR observation;
9. repository observation gate;
10. Ruleset proof;
11. Village state load and validation;
12. worker-lock validation;
13. EvaluationBook validation;
14. Task/worker/principal input validation.

No one of these gates was moved behind the new ACTIVE_WORK return.

### 4.2 Fresh-main source binding is stronger, not broader

The target adds `_require_source_bundle_on_fresh_main(...)` after exact source-bundle discovery and before Phase-A derivation.

It:

- requires canonical bundle paths;
- resolves each path under the loaded repository root;
- requires the path to exist in the fresh current-main recursive tree as a regular `100644` blob;
- reads the fresh-main blob bytes through the GitHub client;
- requires local source-lock bytes to equal those fresh canonical bytes exactly;
- otherwise fails closed with `SOURCE_EPOCH_UNPROVEN`.

The helper returns no authority object, writes nothing, does not construct a source epoch, and does not reinterpret untrusted bytes. It only strengthens the binding between the Phase-A source view and exact fresh-main Git objects.

Importantly, `_source_bundle_from_state(...)` still observes `active_only=False`. Therefore a stale canonical source artifact is not hidden. It is bound to fresh main and then rejected by accepted Phase-A stale-lock semantics.

### 4.3 Accepted Phase-A semantics are reused before Phase-B authority

After the trusted gates and source fresh-main binding, the fixed code constructs the capability profile and calls accepted:

```text
derive_next_state(...)
```

before any retained Phase-B state is read.

The order is now:

```text
trusted GitHub/local/repository/Ruleset/state gates
-> exact source-bundle fresh-main binding
-> accepted Phase-A derive_next_state
-> ACTIVE_WORK read-only return OR fail-closed OR existing terminal path
-> only then read retained Phase-B state
-> only then source epoch / RELEASE / ACQUIRE machinery
```

This is the requested remediation shape.

### 4.4 ACTIVE_WORK is read-only

When Phase A returns:

```text
phase=ACTIVE_WORK
status=ACTIVE_WORK
```

production prints exactly:

```text
ACTIVE_WORK
```

and returns `0` immediately.

That return occurs before:

- `_read_state(state_path)`;
- `_source_record_from_fresh_main(...)`;
- `derive_source_acquisition_v1(...)`;
- source_epoch_id construction;
- `_prepare_release_transport(...)`;
- `_prepare_acquire_transport(...)`;
- retained Phase-B state writes.

Therefore ACTIVE_WORK does not create retained state, source epoch, RELEASE, ACQUIRE, canonical mutation, Truth authority, or review authority.

### 4.5 Valid terminal RELEASE path is preserved

A valid canonical terminal causes accepted Phase A to return `RELEASE_PENDING / RELEASE_REQUIRED`, not ACTIVE_WORK. The new early-return condition therefore does not fire.

Execution proceeds to the pre-existing source-record and RELEASE path:

```text
_source_record_from_fresh_main(...)
-> exact terminal/source Git binding
-> source epoch
-> _prepare_release_transport(...)
```

No release eligibility rule was weakened.

## 5. Security attack review

### 5.1 Expired/stale lock misreported ACTIVE_WORK

PASS.

The source-bundle adapter still sees stale canonical artifacts. Accepted Phase A then distinguishes artifact presence from active ownership and returns `FAIL_CLOSED` for an expired/stale source lock. The target does not convert that status to ACTIVE_WORK.

### 5.2 Malformed terminal treated as absence

PASS.

Accepted Phase A filters only the ordinary `no canonical terminal evidence` condition. Non-absence terminal errors produce `FAIL_CLOSED`. Production raises instead of emitting ACTIVE_WORK.

### 5.3 Wrong worker / same principal replay

PASS.

An active canonical source lock with a different worker fails the Phase-A exact identity check. A bundle-selection miss does not bypass this because Phase A independently observes the canonical task lock and rejects the worker mismatch.

### 5.4 Wrong principal

PASS.

Authenticated-principal equality is checked before Phase A. Phase A also independently checks the source-lock actor principal. No same-worker or same-task shortcut bypasses the principal binding.

### 5.5 Stale local source file vs fresh canonical blob

PASS.

The new fresh-main binding performs byte-for-byte comparison against the exact fresh-main Git blob and fails closed on drift.

### 5.6 Source lock absent from fresh main but present locally

PASS.

The fresh-main tree must contain the exact source-lock path as a regular blob. Local-only source material fails before Phase A can grant ACTIVE_WORK.

### 5.7 Retained state granting authority before source-state gate

PASS.

The target deliberately moves `retained = _read_state(...)` after accepted Phase-A derivation and the ACTIVE_WORK/fail-closed branch. Old retained state therefore cannot grant authority before current source-state evaluation.

### 5.8 source_epoch_id derived before terminal

PASS.

ACTIVE_WORK returns before source-record/source-epoch construction. A source epoch remains terminal-bound through the existing `_source_record_from_fresh_main(...)` path.

### 5.9 RELEASE prepared on ACTIVE_WORK

PASS.

The ACTIVE_WORK return precedes `_prepare_release_transport(...)`. Row 1 additionally asserts zero RELEASE calls.

### 5.10 ACQUIRE prepared on ACTIVE_WORK

PASS.

The ACTIVE_WORK return precedes retained release provenance, post-release ranking, and `_prepare_acquire_transport(...)`. Row 1 additionally asserts zero ACQUIRE calls.

### 5.11 Main movement

PASS.

ACTIVE_WORK itself is non-mutating and cannot convert a later main movement into authority. Existing RELEASE/ACQUIRE paths retain their current-main/head/base lineage gates and their existing movement regressions. The remediation adds no new mutation path.

### 5.12 Ruleset unavailability

PASS.

Ruleset proof remains before Phase-A invocation. An unavailable or failing Ruleset proof raises before ACTIVE_WORK or transport handling.

### 5.13 Truth/review/RENEW/TAKEOVER authority

PASS.

The target changes no authority constants or lifecycle policy paths. The existing 73-row suite retains the Truth/review separation and no-automatic-RENEW/TAKEOVER checks.

## 6. 73-row regression review

Target test blob:

```text
10bb80c1d4f3c27b0ce76c86fae0ee43c489e251
```

The class-level mapping remains exactly:

```text
rows 1..73 exactly once
73 unique mapped test methods
73 class test_* methods
Row74 absent
```

The file has explicit import-time assertions enforcing all four properties.

### 6.1 Row 1

PASS.

Row 1 now invokes actual production `cli_next()` through a controlled GitHub/read-only fixture.

It proves:

```text
active exact source + no terminal
=> rc 0
=> stdout ACTIVE_WORK
=> no retained Phase-B state file
=> no source epoch call
=> no RELEASE call
=> no ACQUIRE call
```

The same mapped Row 1 also covers:

- malformed terminal => fail closed;
- wrong worker => fail closed;
- wrong principal => fail closed;
- noncanonical/local-only source lock => fail closed;
- valid canonical abandonment terminal => enters the existing RELEASE path.

The old Row-1 positive V3 transport/canonical-transition checks remain after the new integration subcases. The strengthening therefore does not replace or weaken the original Row-1 contract.

### 6.2 Row 50

PASS.

Row 50 retains its original V3 expired canonical-acquisition assertion and adds a top-level production `cli_next()` source-side regression with an expired source lock.

It proves:

```text
expired/stale source != ACTIVE_WORK
nonzero return
no retained state
no source epoch
no RELEASE
no ACQUIRE
```

The original Row-50 contract remains intact.

## 7. PR #47

Fresh PR observation:

```text
number=47
state=open
draft=false
merged_at=null
base_sha=b01bf39c2387d8e1f0dc4cfd60d6e1bb56b0a10d
head_sha=2848245c3a7daf36a3dd266e8f338ededa956dae
changed_files=2
```

The changed filenames are exactly the fixed target paths and no others.

PR #47 was not merged or modified by this review.

## 8. Exact-head Verify #122

Fresh workflow observation:

```text
workflow=Verify public release
workflow_id=347191396
run_number=122
run_id=33830375587
job_id=100891923218
head_sha=2848245c3a7daf36a3dd266e8f338ededa956dae
event=pull_request
status=completed
conclusion=success
```

The run is attached to PR #47 with base `b01bf39...` and exact target head `2848245...`.

The sole `verify` job is completed/success. Its successful steps include:

- PR policy and change class;
- DCO 1.1 sign-off;
- Public safety audit;
- Village state validation;
- Village synthetic acceptance tests;
- v1.1 direct acceptance tests;
- v1.2 direct acceptance tests;
- v1.2.1 Phase A acceptance tests;
- v1.2.1 Phase B acceptance tests;
- REUSE/SPDX compliance;
- reproduction of executable public claims.

The checked workflow runs canonical:

```text
python3 scripts/village.py test
```

and `scripts/village.py test` dispatches the Village acceptance suite, v1.1, v1.2, v1.3 Phase A and v1.3 Phase B suites.

Independent source-count reconstruction at the exact target gives:

```text
v1.3 Phase A: 34 unittest methods
v1.3 Phase B: 73 unittest methods
v1.2.1 Phase A: 37 unittest methods
v1.2.1 Phase B: 23 unittest methods
```

The exact-head CI job reports success for the corresponding canonical/direct test steps. The public-release audit step also reports success; the audit script returns zero only after printing its PASS result.

### Execution-evidence limitation

A clean local clone/test execution was attempted, but this review runtime could not resolve `github.com` by DNS. The GitHub Actions logs archive endpoint was fresh-read as well, but the connector exposed no textual log body. Under the task's explicit fallback rule, the exact-head run/job is therefore used as independent execution evidence. The run identity, job identity, exact target head, successful canonical test steps, workflow commands, and exact checked-in test cardinalities were independently read back from GitHub rather than copied from the remediation author.

This limitation is an evidence-transport limitation of the review runtime, not a target finding.

## 9. Findings

No blocking or nonblocking target defect was found.

```text
CRITICAL=0
HIGH=0
MEDIUM=0
LOW=0
```

The previous production integration defect is repaired at the required boundary: accepted Phase-A source semantics now gate terminal-bound Phase-B authority, while ACTIVE_WORK remains a pure status/read-back result.

## 10. Final decision matrix

```text
CURRENT_MAIN:
b01bf39c2387d8e1f0dc4cfd60d6e1bb56b0a10d

SOURCE_LOCK_BLOB:
6604acaf8c458a4893fc746fd689326b0d5d3722

TARGET_COMMIT:
2848245c3a7daf36a3dd266e8f338ededa956dae

TARGET_PARENT:
b01bf39c2387d8e1f0dc4cfd60d6e1bb56b0a10d

TARGET_CORE_BLOB:
dc49ee57505929b4c374cc9595e251953864a41a

TARGET_TEST_BLOB:
10bb80c1d4f3c27b0ce76c86fae0ee43c489e251

TARGET_IDENTITY:
PASS

PR47:
PASS

VERIFY_122:
PASS

ACTIVE_WORK_RESTORED:
PASS

ACTIVE_WORK_READ_ONLY:
PASS

VALID_TERMINAL_RELEASE_PATH:
PASS

EXPIRED_SOURCE_FAIL_CLOSED:
PASS

MALFORMED_TERMINAL_FAIL_CLOSED:
PASS

WRONG_WORKER_FAIL_CLOSED:
PASS

WRONG_PRINCIPAL_FAIL_CLOSED:
PASS

FRESH_MAIN_SOURCE_BINDING:
PASS

ROW1:
PASS

ROW50:
PASS

PHASE_B_METHOD_COUNT:
73

SPEC_ROWS:
1..73 exactly once

ROW74:
ABSENT

CI_PHASE_A:
Ran 34 tests / OK (exact-head job success; count independently reconstructed from fixed source)

CI_PHASE_B_73:
Ran 73 tests / OK (exact-head job success; exact 73-row assertions independently read)

CI_V121:
Ran 37 tests / OK (exact-head job success; count independently reconstructed from fixed source)

CI_V121_PHASE_B:
Ran 23 tests / OK (exact-head job success; count independently reconstructed from fixed source)

PUBLIC_RELEASE_AUDIT:
PASS

CRITICAL:
0

HIGH:
0

MEDIUM:
0

LOW:
0

VERDICT:
PASS

REMEDIATION_ACCEPTED:
YES

PR47_READY_FOR_MERGE:
YES
```

The review itself changes only this report path on its dedicated review branch. `main`, PR #47, the fixed target, the live source lock, production code, workflows, schemas, work state and canonical coordination state remain untouched.