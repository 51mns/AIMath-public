# Village v1.3 `/next` ACTIVE_WORK live mismatch — independent review

TASK-ID: `AIMATH-VILLAGE-V1-3-NEXT-ACTIVE-WORK-LIVE-MISMATCH-REVIEW`

Review branch: `review/village-v1-3-next-active-work-live-mismatch-final`

Fixed review base:

```text
b01bf39c2387d8e1f0dc4cfd60d6e1bb56b0a10d
```

Parent:

```text
7dc8541c0a9e19f37910e06bc4738375c4c7af00
```

Disposition:

```text
ROOT_CAUSE = PRODUCTION_INTEGRATION_BUG
VERDICT    = PASS_REMEDIATION_DIRECTION
```

This is a zero-trust contract/integration review. Production code, tests, `main`, the source lock, workflows, Rulesets, settings, Task/Campaign state, Truth/review state, and cleanup state were not modified by this review.

## 1. Fixed evidence

### 1.1 Current canonical main

Fresh remote read before the review branch was created established:

```text
main   b01bf39c2387d8e1f0dc4cfd60d6e1bb56b0a10d
parent 7dc8541c0a9e19f37910e06bc4738375c4c7af00
```

The current source lock is present at:

```text
coordination/locks/eq18/general-structural-obstruction.yml
```

with exact Git blob:

```text
6604acaf8c458a4893fc746fd689326b0d5d3722
```

and exact identity:

```text
lock_id      LOCK-FIELDTEST-EQUIANGULAR-R18-001-0BEBFD2FD11CB67F
task_id      TASK-EQUIANGULAR-R18-001
worker_id    w-0bebfd2fd11cb67f
principal    gh:51mns
base_main    7dc8541c0a9e19f37910e06bc4738375c4c7af00
acquired_at  2026-09-04T01:04:54Z
expires_at   2026-09-11T01:04:54Z
work_ref     research/TASK-EQUIANGULAR-R18-001/w-0bebfd2fd11cb67f
collision    eq18/general-structural-obstruction
renewals     0
```

At the review time, the lease is unexpired. No current-main result terminal exists at `coordination/outcomes/TASK-EQUIANGULAR-R18-001.yml`, and no current-main abandonment terminal exists at `work/TASK-EQUIANGULAR-R18-001/w-0bebfd2fd11cb67f/ABANDONED_TERMINAL.yml`.

Therefore the live source state is exactly:

```text
exact canonical source acquisition = PRESENT
exact source ownership             = ACTIVE
canonical terminal                 = ABSENT
```

### 1.2 Live execution evidence

The fixed live execution report is:

```text
commit 7cc9519e0c3b4c65d78dedb3f09772c86d245f83
blob   9449099d5444b04092c2986b36021b5bb4a4cf05
```

It records the exact production invocation after canonical M1 and the result:

```text
FAIL: SOURCE_TERMINAL_UNPROVEN: no canonical terminal evidence
exit = 2
```

It also records that the abort created none of the following:

- terminal evidence;
- RELEASE ref/PR;
- next ACQUIRE ref/PR;
- retained Phase-B state;
- Truth/Claim/Review effect;
- cleanup mutation.

The source lock was deliberately left canonical and active.

### 1.3 Frozen parent `/next` contract

Fixed parent contract:

```text
commit 5eed8cc40243eba166afee651104f3c4a79d99ac
path   reviews/village-v1-3-next-preflight/NEXT_FROZEN_SPEC.md
blob   ad851bd4fece0f3f45126ae12da3b54a3a7a5832
```

Section 2.2 says terminal evidence is required **before RELEASE can become eligible**. It does not say that calling `/next` before terminalisation is invalid.

Section 3 explicitly defines:

```text
ACTIVE_WORK
  authority/input: current canonical lock + retained worker + current Task
  precondition:    exact active work is still owned
  output:          continue work, or proceed only when a terminal record is ready
```

Section 5.2 makes the intended boundary even more explicit: a worker that has not yet terminalised may simply remain in `ACTIVE_WORK`; after terminalisation, literal reacquisition of the completed Task is not automatic.

The parent contract is therefore not terminal-only.

### 1.4 Phase-B frozen contract

Fixed Phase-B V3 contract:

```text
commit a482d1f4398489753589afe1ef3ed5e593a7e9c4
path   reviews/village-v1-3-next-phase-b-transport-preflight/PHASE_B_FROZEN_SPEC.md
blob   2ddc79843cf44bd588dc1a5ff89e996ecd246de9
```

Phase B is explicitly orchestration/transport layered on accepted Phase A, not a replacement state machine and not a new canonical mutation authority.

Its V3 Section 21.17 states that accepted Phase A remains exactly its accepted boundary and that V3 changes the Phase-B acquisition identity only. The V3 acceptance matrix is explicitly frozen at exactly 73 mandatory rows, with no padding rows.

Nothing in V3 supersedes the parent `ACTIVE_WORK` pre-terminal phase with a terminal-only entry contract.

## 2. Accepted Phase-A contract

Current Phase-A production core:

```text
scripts/village_next.py
blob 39efe7efddc46ff43315e04b06df0baf4601327b
```

The accepted core first distinguishes three source-lock conditions:

1. no canonical lock artifact;
2. an exact active canonical lock;
3. a stale/expired canonical lock artifact.

It uses `active_only=False` to notice stale artifacts and then `active_only=True` to establish live ownership. A stale/expired artifact is fail-closed; it is not treated as active work and is not silently treated as clean absence.

For an exact active source lock, Phase A independently checks exact Task/worker/principal binding, then reads terminal evidence.

The load-bearing branch is:

```text
source_lock is present
AND terminal is absent
AND there are no malformed-terminal errors
=> phase              = ACTIVE_WORK
=> status             = ACTIVE_WORK
=> canonical_ownership = True
=> required_action    = NONE
```

Malformed terminal evidence changes the result to fail-closed. It is never converted to `ACTIVE_WORK` success merely because a lock exists.

This behavior is explicitly pinned by current test:

```text
test_01_active_exact_worker_without_terminal_is_active_work
```

which requires:

```text
phase               == ACTIVE_WORK
status              == ACTIVE_WORK
canonical_ownership == True
required_action     == NONE
```

The same Phase-A test suite separately requires malformed terminal evidence to fail closed.

Conclusion:

```text
PHASE_A_CONTRACT = ACTIVE_WORK_REQUIRED
```

## 3. Current Phase-B production behavior

Current Phase-B production core:

```text
scripts/village_next_phase_b.py
blob 25aed74d7e85e8543fc93230968f7b70931b4aee
```

The top-level `cli_next()` correctly performs substantial security/freshness gates before source orchestration, including:

- `--github-write yes` requirement;
- fresh remote main read;
- asserted-main equality when supplied;
- authenticated GitHub principal observation;
- asserted-principal equality;
- exact local-main equality with fresh remote main;
- complete recursive-tree observation;
- complete bounded open-PR observation;
- repository observation gate;
- Ruleset proof;
- fresh Village-state validation;
- worker-lock policy validation;
- EvaluationBook validation;
- Task/worker/principal input-shape validation.

The mismatch occurs **after** those gates.

### 3.1 Source-bundle adapter

`_source_bundle_from_state()` currently uses:

```text
state.lock_for_task(task_id, active_only=False)
```

and selects an exact Task/worker/principal bundle.

That means both active and expired/stale canonical source artifacts can enter the Phase-B source branch. This is not itself necessarily wrong; it can be useful for detecting stale state. But it means the adapter must preserve Phase-A's active/stale distinction before returning success.

### 3.2 Terminal adapter

`_terminal_from_phase_a()` calls only Phase A's terminal recognizer:

```text
recognize_terminal_evidence(...)
```

and then converts every `terminal is None` result into:

```text
PhaseBError("SOURCE_TERMINAL_UNPROVEN", ...)
```

It does **not** invoke accepted `derive_next_state()` and therefore does not reproduce Phase A's semantic distinction between:

```text
exact active ownership + ordinary terminal absence => ACTIVE_WORK
```

and:

```text
malformed terminal / stale ownership / identity failure => FAIL_CLOSED
```

### 3.3 Top-level bypass

In current `cli_next()`:

```text
source_bundle = _source_bundle_from_state(...)
...
if source_bundle is not None:
    source_record, source_id, _terminal = _source_record_from_fresh_main(...)
    ...
    _prepare_release_transport(...)
```

`_source_record_from_fresh_main()` immediately requires `_terminal_from_phase_a()` to succeed before `SourceAcquisitionV1` can be constructed.

Thus the production control flow is currently:

```text
exact source bundle exists
-> require terminal
-> terminal absent
-> SOURCE_TERMINAL_UNPROVEN
```

instead of the accepted control flow:

```text
exact active source bundle exists
-> accepted Phase-A derivation
-> no valid terminal and no terminal error
-> ACTIVE_WORK read-back
-> success / no mutation / no retained Phase-B state
```

This is a production integration bypass of accepted Phase-A state semantics.

## 4. Root-cause decision

### Option A — plan correction

Rejected.

Making production `/next` terminal-only would contradict:

- parent Section 2.2's “Before RELEASE can become eligible” boundary;
- the explicit parent `ACTIVE_WORK` state-machine row;
- parent Section 5.2;
- the accepted Phase-A implementation;
- the accepted Phase-A regression test;
- Phase-B V3's statement that accepted Phase A remains the inherited boundary.

### Option B — production integration correction

Accepted.

Production Phase B must consume/reproduce accepted Phase-A pre-terminal semantics before it attempts to construct a terminal-bound `SourceAcquisitionV1`.

### Option C

No alternative contract change is needed. A narrow adapter correction is sufficient.

Final root cause:

```text
ROOT_CAUSE = PRODUCTION_INTEGRATION_BUG
PLAN_BUG   = NO
```

## 5. Required production remediation

The safest minimal remediation is to make `cli_next()` actually evaluate accepted Phase-A source state **after all existing authentication/fresh-main/local-main/repository-completeness/Ruleset/state-validation gates and before SourceAcquisitionV1 construction or any transport/state write**.

A recommended control shape is:

```text
fresh authenticated production gates
-> accepted Phase-A derive_next_state for current source Task/worker/principal

if exact active source + ordinary no-terminal:
    require Phase-A phase/status ACTIVE_WORK
    print ACTIVE_WORK
    return success
    write no retained Phase-B state
    derive no source_epoch_id
    create no RELEASE
    create no ACQUIRE

if Phase-A fails closed:
    propagate fail closed
    do not reinterpret as ACTIVE_WORK

if Phase-A establishes a valid terminal while source lock is active:
    continue the existing Phase-B SourceAcquisitionV1 / source_epoch / RELEASE path

if source lock is canonically absent after RELEASE:
    continue the existing retained exact-source-epoch / release-provenance / post-RELEASE selection path
```

### 5.1 Important non-fix

Do **not** fix this solely by changing `_source_bundle_from_state()` from `active_only=False` to `active_only=True`.

That isolated change would hide an expired/stale canonical lock artifact from the source branch and could misclassify it as source absence, potentially sending it into the post-RELEASE retained/provenance branch. Accepted Phase A already has the correct active-versus-stale distinction. Reusing that distinction is safer than recreating a partial version in Phase B.

### 5.2 ACTIVE_WORK is status only

The repaired branch must remain read-back only:

```text
ACTIVE_WORK => no canonical mutation authority
ACTIVE_WORK => no retained Phase-B epoch creation
ACTIVE_WORK => no source_epoch_id
ACTIVE_WORK => no RELEASE transport
ACTIVE_WORK => no ACQUIRE transport
ACTIVE_WORK => no Truth/review authority
```

It must never become a shortcut around terminalisation.

## 6. Security regression assessment

### 6.1 Expired/stale source lock

Recommended remediation: **PASS**, provided it consumes accepted Phase-A state rather than merely checking source-bundle existence.

Phase A already detects a canonical lock artifact with no active lock and returns fail-closed. Therefore an expired source lock cannot become `ACTIVE_WORK` merely because `_source_bundle_from_state(active_only=False)` can observe it.

The production integration regression must exercise the top-level `cli_next()` path, not only the V3 post-ACQUIRE active-lock gate.

### 6.2 Malformed terminal

Recommended remediation: **PASS**.

Phase A already distinguishes ordinary terminal absence from malformed terminal evidence. Only ordinary absence under exact active ownership may return `ACTIVE_WORK`. Malformed terminal evidence remains fail-closed and must never reach RELEASE preparation.

### 6.3 Wrong worker/principal

Recommended remediation: **PASS**.

The authenticated-principal equality gate remains before Phase-A invocation, and Phase A independently checks source lock worker/principal identity. A mismatch must remain fail-closed with no mutation.

### 6.4 Existing transport/security gates

The fix does not require weakening or moving any of:

- authenticated principal check;
- fresh remote main check;
- exact local-main check;
- complete repository observations;
- Ruleset proof;
- exact terminal evidence requirements for RELEASE;
- source-epoch construction requirements;
- release provenance;
- post-RELEASE fresh-main barrier;
- exact V3 ACQUIRE transport identity;
- canonical ACTIVE_NEXT confirmation;
- Truth/review separation;
- RENEW/TAKEOVER prohibition.

No unauthorized-mutation vulnerability was demonstrated by the live mismatch. The observed production behavior failed closed before mutation.

## 7. Why 73/73 passed

Current Phase-B test file:

```text
scripts/test_village_v1_3_next_phase_b.py
blob 508b25287a8c21f4dc76b3f59663818ec3f82c55
```

The test class maps exactly 73 unique methods to rows 1..73 and asserts that no extra/missing mapped method exists.

The gap is not row count; it is integration depth.

Examples:

- Row 1 is named as the happy-path release/select/acquire/ACTIVE_NEXT flow, but it directly exercises lower-level `premerge_transport_gate()` and `canonical_transition_gate()`. It does not invoke production `cli_next()` from a pre-terminal exact source lock.
- Row 50 proves an expired **next-acquisition V3 lock** cannot satisfy `canonical_transition_gate()`, but it does not exercise the source-side top-level `cli_next()` branch where `_source_bundle_from_state(active_only=False)` is followed by unconditional terminal construction.
- Other rows strongly cover transport identity, Verify lineage, Ruleset proof, exact trees/objects, source/release provenance, wrong worker/principal bindings, and post-canonical ACTIVE_NEXT semantics, but the adapter edge from accepted Phase A to production Phase B is not executed.

Therefore 73/73 can pass while the production mismatch remains.

Conclusion:

```text
PHASE_B_TEST_COVERAGE_GAP = YES
```

## 8. 73-row-compatible regression remediation

Do not create Row 74.

Safest method: strengthen existing mapped methods while preserving exactly 73 unique mapped methods.

At minimum, strengthen **Row 1** so the same mapped test method contains a pre-terminal production-integration subcase that invokes actual `cli_next()` through a controlled production-client/temp-repository fixture and proves:

```text
exact active source lock
+ exact worker/principal
+ no terminal files
=> stdout/status ACTIVE_WORK
=> exit 0
=> retained Phase-B state absent
=> no RELEASE preparation call
=> no ACQUIRE preparation call
=> no source epoch created
```

Within that same existing method, retain its existing terminal/release/select/acquire/ACTIVE_NEXT positive checks.

For stronger regression closure without changing row count, also strengthen existing **Row 50** to drive the production source-side adapter with an expired source lock and prove that top-level `cli_next()` fails closed rather than returning `ACTIVE_WORK` or entering post-RELEASE selection.

Malformed-terminal and wrong-worker/principal production-integration subcases may be included as parameterized/subtest cases inside an existing relevant mapped method; they do not require new mapped test names.

This preserves:

```text
SPEC_ROW_TO_TEST = 1..73
unique mapped methods = 73
Row 74 = absent
```

while adding the missing actual production adapter coverage.

## 9. Live M1 recovery

### 9.1 May the current M1 acquisition remain canonical during remediation?

Yes.

The canonical M1 acquisition is not invalidated by the Phase-B adapter bug:

- M1 introduced only the expected source lock;
- the source lock is exact and active;
- no terminal has been created;
- no RELEASE or next ACQUIRE transport was created;
- no retained Phase-B source epoch was written;
- no Truth/review state changed;
- the failed invocation did not mutate canonical state.

Under the parent/Phase-A contract, this is ordinary `ACTIVE_WORK` ownership.

There is therefore no need to delete/recreate the source lock merely to obtain a clean production test.

### 9.2 Post-fix resume policy

The preferred policy is:

```text
RESUME_SAME_M1_WITH_SUPPLEMENT
```

Here “same M1” means the same exact source acquisition introduced at M1, not that the post-fix process must execute from detached commit M1 after remediation changes main.

A recovery supplement should freeze and prove, immediately before resumed live validation:

1. the remediation/current main SHA;
2. the original M1 acquisition identity;
3. the exact source lock path/blob is still unchanged from M1;
4. the lease is still active;
5. the exact worker/principal/work-ref/collision binding is unchanged;
6. no source terminal exists before the pre-terminal rerun;
7. no retained Phase-B state/RELEASE/next-ACQUIRE artifact from the aborted run exists;
8. the repaired production command returns `ACTIVE_WORK` with no mutation;
9. only after later valid canonical terminal evidence exists may the same source acquisition proceed to source-epoch construction and RELEASE.

A completely new epoch is not required merely because the old production invocation failed closed.

If the lock expires before remediation/resumption, this conclusion no longer grants ACTIVE_WORK. The run must fail closed and be reassessed. Automatic renewal or takeover is forbidden.

## 10. Severity

### Contract / production defect

**MEDIUM — 1 finding.**

Accepted Phase-A pre-terminal semantics are bypassed by the production Phase-B adapter, making a valid `/next` state unreachable and aborting the live workflow. The defect is real production behavior, but it fails closed before transport/canonical mutation.

### Security impact

**No separate security finding.**

No unauthorized release, acquire, ownership, Truth, review, Ruleset/settings, RENEW, or TAKEOVER authority was observed. The failure is conservative rather than permissive.

### Availability impact

**MEDIUM impact, part of the production finding.**

A legitimate exact active worker cannot obtain the required pre-terminal `/next` `ACTIVE_WORK` status from production and the live Phase-B validation stops.

### Test coverage gap

**LOW — 1 finding.**

The 73-row matrix has strong primitive/security coverage but does not exercise the actual `cli_next()` pre-terminal source integration edge. The frozen row count can be preserved while closing the gap.

Counts:

```text
CRITICAL 0
HIGH     0
MEDIUM   1
LOW      1
```

## 11. Final decision matrix

```text
CURRENT_MAIN:
b01bf39c2387d8e1f0dc4cfd60d6e1bb56b0a10d

SOURCE_LOCK_PRESENT:
YES

SOURCE_LOCK_ACTIVE:
YES

FROZEN_PARENT_CONTRACT:
ACTIVE_WORK_REQUIRED

PHASE_A_CONTRACT:
ACTIVE_WORK_REQUIRED

PHASE_B_CURRENT_BEHAVIOUR:
Exact Task/worker/principal source bundle is discovered with active_only=False; cli_next then constructs SourceAcquisitionV1 via _source_record_from_fresh_main(), whose _terminal_from_phase_a() raises SOURCE_TERMINAL_UNPROVEN whenever terminal evidence is absent. Accepted Phase-A ACTIVE_WORK derivation is bypassed.

ROOT_CAUSE:
PRODUCTION_INTEGRATION_BUG

PRODUCTION_FIX_REQUIRED:
YES

PLAN_FIX_REQUIRED:
NO

RECOMMENDED_FIX:
After existing authenticated-principal, fresh-main, exact-local-main, complete-observation, Ruleset and Village-state validation gates, invoke/reproduce accepted Phase-A derive_next_state semantics before SourceAcquisitionV1 construction. Exact active current acquisition + ordinary no-terminal => ACTIVE_WORK/read-only/success/no retained state/no transport. Valid terminal => continue existing source-epoch/RELEASE path. Malformed terminal, stale/expired ownership, or identity mismatch => fail closed.

EXPIRED_LOCK_REGRESSION_RISK:
PASS

MALFORMED_TERMINAL_REGRESSION_RISK:
PASS

WRONG_WORKER_REGRESSION_RISK:
PASS

PHASE_B_TEST_COVERAGE_GAP:
YES

73_ROW_COMPATIBLE_REMEDIATION:
YES

METHOD:
Strengthen existing Row 1 with an actual cli_next() pre-terminal ACTIVE_WORK integration subcase while retaining its existing end-to-end positive checks; optionally strengthen existing Row 50 with top-level expired-source cli_next() coverage. Add parameterized malformed-terminal/wrong-identity integration subcases inside existing mapped methods. Preserve exactly 73 unique mapped methods and do not create Row 74.

LIVE_M1_CAN_REMAIN_DURING_REMEDIATION:
YES

LIVE_EXECUTION_RESUME_POLICY:
RESUME_SAME_M1_WITH_SUPPLEMENT

CRITICAL:
0

HIGH:
0

MEDIUM:
1

LOW:
1

VERDICT:
PASS_REMEDIATION_DIRECTION
```

## 12. Review limits

The review attempted a clean local clone for direct test execution, but this chat runtime had no DNS/network path to `github.com`; therefore no claim is made that the reviewer reran the test suite locally. This did not block the contract decision because the exact current production/spec/test blobs and the fixed live execution evidence were independently read from GitHub, and the mismatch is visible directly in the accepted Phase-A and production Phase-B control flow.

No production/test/source-lock change is included in this review commit.
