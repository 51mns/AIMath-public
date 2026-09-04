# Village v1.3 `/next` live-field recovery supplement

TASK-ID: `AIMATH-VILLAGE-V1-3-NEXT-LIVE-FIELD-RECOVERY-SUPPLEMENT`

Status: **RESUME_SAME_M1_WITH_SUPPLEMENT**

Repository: `51mns/AIMath-public`

This supplement does not change the frozen live-field plan, parent `/next` specification, Phase-B V3 transport specification, source acquisition identity, expected next Task, or cleanup rules. It freezes the exact recovery boundary after the first live execution failed closed on the now-remediated production `ACTIVE_WORK` adapter mismatch.

## 1. Authorities

Frozen historical live plan:

```text
commit 705bd7c5250103e74118381106d422d50c677bb7
blob   05848a5d2998e42e5e02443f331194c61486f3b6
path   reviews/village-v1-3-next-live-field-test-preflight/FIELD_TEST_PLAN.md
```

V3 compatibility supplement:

```text
commit 95edc35b9e54e91bd3d11ab58160f159508df2c7
blob   0b3059736d8b78ac9f511edffd05def19fa3a651
```

Aborted live execution report:

```text
commit 7cc9519e0c3b4c65d78dedb3f09772c86d245f83
blob   9449099d5444b04092c2986b36021b5bb4a4cf05
verdict LIVE_FIELD_ABORTED_ACTIVE_WORK_OPERATOR_MISMATCH
```

Independent mismatch review:

```text
commit b8a50e6a825f126d697c36751e4135ba772cdb70
blob   d657a053f9d1f09f0368006ed3ccaf4debb4bcb7
ROOT_CAUSE = PRODUCTION_INTEGRATION_BUG
PLAN_BUG   = NO
LIVE_EXECUTION_RESUME_POLICY = RESUME_SAME_M1_WITH_SUPPLEMENT
```

Accepted remediation:

```text
writer target 2848245c3a7daf36a3dd266e8f338ededa956dae
independent review 97efc8a5a46fe1edddc5ef588a76465a3509974d
review blob c174079ed65aa5b3e04bbc30a0102a19a263afd5
verdict PASS
```

Merged remediation/current main at supplement freeze:

```text
M_RECOVERY = e00511a6271381e13ff49e5270033369d64d1938
parent     = b01bf39c2387d8e1f0dc4cfd60d6e1bb56b0a10d
core blob  = dc49ee57505929b4c374cc9595e251953864a41a
test blob  = 10bb80c1d4f3c27b0ce76c86fae0ee43c489e251
post-merge Verify #123 / run 33831546101 = completed/success
```

The remediation merge changed only the Phase-B production core and its existing 73-row test file. It did not change the source lock, Task/Campaign state, Truth/review state, frozen plan/spec, Ruleset, or trusted lifecycle workflow.

## 2. Retained canonical M1 acquisition

The same exact M1 source acquisition remains the live source epoch substrate:

```text
M1                = b01bf39c2387d8e1f0dc4cfd60d6e1bb56b0a10d
SOURCE_TASK       = TASK-EQUIANGULAR-R18-001
SOURCE_CAMPAIGN   = CAM-EQUIANGULAR-R18
SOURCE_WORKER     = w-0bebfd2fd11cb67f
SOURCE_PRINCIPAL  = gh:51mns
SOURCE_COLLISION  = eq18/general-structural-obstruction
SOURCE_LOCK_PATH  = coordination/locks/eq18/general-structural-obstruction.yml
SOURCE_WORK_REF   = research/TASK-EQUIANGULAR-R18-001/w-0bebfd2fd11cb67f
SOURCE_LOCK_ID    = LOCK-FIELDTEST-EQUIANGULAR-R18-001-0BEBFD2FD11CB67F
SOURCE_LOCK_BLOB  = 6604acaf8c458a4893fc746fd689326b0d5d3722
acquired_at       = 2026-09-04T01:04:54Z
expires_at        = 2026-09-11T01:04:54Z
renewal_count     = 0
```

At supplement freeze:

- current main is `M_RECOVERY`;
- the source lock path still resolves to exact blob `6604acaf8c458a4893fc746fd689326b0d5d3722`;
- the source abandonment terminal is absent from current main;
- `coordination/outcomes/TASK-EQUIANGULAR-R18-001.yml` is absent from current main;
- no exact-worker `release/TASK-EQUIANGULAR-R18-001/w-0bebfd2fd11cb67f` branch exists;
- branch search for `w-0bebfd2fd11cb67f` finds only the historical source lock transport branch;
- the aborted execution report records that the retained Phase-B state file was not created and that no RELEASE or `next-acquire/**` ref/PR was created by the aborted invocation.

The M1 acquisition is therefore retained as the same canonical source acquisition. `M_RECOVERY` is the implementation/main snapshot from which resumed production validation executes; it is not a replacement acquisition epoch.

## 3. Mandatory recovery pre-terminal checkpoint

Before any new canonical mutation, execute the actual production operator from an exact clean checkout of fresh current main and require all normal production authentication/freshness/Ruleset/state gates.

Use the frozen capability profile:

```text
github_write   = yes
local_compute  = yes
web_literature = yes
```

Use exact source identity:

```text
task_id      = TASK-EQUIANGULAR-R18-001
worker_id    = w-0bebfd2fd11cb67f
principal_id = gh:51mns
```

The local retained-state path for the resumed live run remains:

```text
.git/village-next-phase-b-live-field.json
```

Immediately before the pre-terminal invocation, this path MUST NOT exist. The old aborted run did not create it. If it exists unexpectedly, stop and freeze evidence rather than deleting or trusting it ad hoc.

The production invocation MUST return exactly the accepted pre-terminal state:

```text
ACTIVE_WORK
exit = 0
```

After this invocation require:

```text
retained Phase-B state file = absent
source_epoch_id             = not derived
RELEASE transport           = absent
next ACQUIRE transport      = absent
canonical mutation          = none
Truth/Claim/Review effect   = NONE
```

If the operator does not return `ACTIVE_WORK`, stop. Do not create terminal evidence and do not adapt the plan.

## 4. Resume after ACTIVE_WORK passes

Only after Section 3 passes may the original frozen sequence resume.

### 4.1 Source terminal / M2

Create only the preregistered truth-neutral abandonment terminal:

```text
work/TASK-EQUIANGULAR-R18-001/w-0bebfd2fd11cb67f/ABANDONED_TERMINAL.yml
work/TASK-EQUIANGULAR-R18-001/w-0bebfd2fd11cb67f/ABANDONED_TERMINAL.yml.license
```

Payload shape remains exactly the frozen plan:

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

Sidecar:

```text
SPDX-FileCopyrightText: 2026 AIMath contributors
SPDX-License-Identifier: CC0-1.0
```

This is an ordinary normal PR. It may merge only through ordinary green-Verify policy. It is not a mathematical outcome and must not create `coordination/outcomes/TASK-EQUIANGULAR-R18-001.yml`.

The canonical main after terminal merge is `M2`.

### 4.2 RELEASE / M3

From fresh `M2`, invoke the actual production `/next` with the same retained-state path and exact frozen identity/capabilities.

Production must derive the terminal-bound source acquisition/source epoch and deterministic RELEASE transport. Do not manually construct or manually merge RELEASE.

Duplicate invocation before canonical RELEASE must reuse the exact deterministic RELEASE transport identity.

Trusted lifecycle alone canonicalises RELEASE. The canonical main after exact source lock removal is `M3`.

### 4.3 Fresh post-RELEASE selection

After canonical `M3`, rerank from fresh current canonical bytes and complete GitHub observations.

The preregistered result remains mandatory:

```text
EXPECTED_NEXT_TASK       = TASK-DITTERT-N5-001
EXPECTED_NEXT_CAMPAIGN   = CAM-DITTERT-N5
EXPECTED_NEXT_RELATION   = GLOBAL_READY
EXPECTED_NEXT_COLLISION  = dittert-n5/broader-zero-pattern
EXPECTED_NEXT_LOCK_PATH  = coordination/locks/dittert-n5/broader-zero-pattern.yml
EXPECTED_NEXT_WORK_REF   = research/TASK-DITTERT-N5-001/w-0bebfd2fd11cb67f
```

If the exact Task/relation differs, stop as `PRECONDITION_DRIFT`. Do not adapt to another Task.

### 4.4 V3 ACQUIRE / M4

Independently derive/freeze the V3 semantic IDs from fresh canonical state:

```text
SOURCE_EPOCH_ID
CONTINUATION_CONTEXT_ID
SELECTION_ID
ACQUIRE_INTENT_ID
NEXT_LOCK_ID
```

Production `/next` alone creates/reuses the deterministic V3 ACQUIRE transport. Do not manually construct or manually merge it.

Duplicate invocation before canonical ACQUIRE must reuse the exact deterministic transport.

Trusted lifecycle alone canonicalises the V3 ACQUIRE. The canonical main after exact expected-next lock addition is `M4`.

### 4.5 ACTIVE_NEXT and replay controls

Reconstruct V3 semantics from fresh canonical current bytes, not process memory, and require:

```text
ACTIVE_NEXT
```

Then execute the preregistered old-source-epoch replay negative control and require fail-closed rejection. Repeated final `/next` must be idempotent and must not create a second acquisition.

## 5. Cleanup remains mandatory

After evidence is frozen, perform only the frozen truth-neutral cleanup:

1. create the expected-next worker's truth-neutral abandonment terminal through ordinary green-Verify policy;
2. use exact-worker production RELEASE transport;
3. trusted lifecycle canonicalises that RELEASE;
4. require zero active field-test locks at final current main.

Do not delete durable abandonment markers. Do not use RENEW, TAKEOVER, manual lock deletion, manual RELEASE construction, manual RELEASE merge, or a substitute worker.

## 6. Stop conditions

Stop and freeze evidence immediately if any of the following occurs:

- source lock differs from blob `6604acaf8c458a4893fc746fd689326b0d5d3722` before its intended RELEASE;
- source lease is expired at the point where active ownership is required;
- authenticated principal is not `gh:51mns`;
- current main moves unexpectedly across an asserted operation boundary;
- Ruleset proof is unreadable/weaker or bypass is available/used;
- pre-terminal production result is not exact `ACTIVE_WORK / exit 0`;
- the retained Phase-B state file exists before the first resumed invocation;
- malformed/foreign terminal evidence appears;
- a conflicting eligible lifecycle transport appears;
- post-RELEASE selection is not exact `TASK-DITTERT-N5-001 / GLOBAL_READY`;
- deterministic transport duplicate behavior differs;
- old-source-epoch replay is accepted;
- Truth/Claim/Review/research acceptance state changes;
- cleanup cannot prove zero active field-test locks.

If the source lock expires before resumed active-state validation, do not renew it automatically. This supplement no longer authorises same-M1 ACTIVE_WORK and the run must be reassessed.

## 7. Execution reporting

Continue using the original symbolic M-labels:

```text
M0 historical clean pre-source main
M1 canonical source ACQUIRE main
M2 canonical truth-neutral source terminal main
M3 canonical source RELEASE main
M4 canonical expected-next V3 ACQUIRE main
```

Record `M_RECOVERY=e00511a6271381e13ff49e5270033369d64d1938` separately as the reviewed implementation snapshot used to resume the same M1 acquisition.

Do not rewrite the aborted live report. Final resumed execution evidence must explicitly cite this supplement, the aborted report, mismatch review, accepted remediation review, merge SHA, and post-merge Verify #123.

Preferred successful final verdict remains:

```text
LIVE_FIELD_PASS_CLEAN
```
