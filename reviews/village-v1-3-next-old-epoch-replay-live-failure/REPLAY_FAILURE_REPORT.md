# Village v1.3 `/next` old-source-epoch replay live failure

Status: **FROZEN LIVE FAILURE EVIDENCE**

Repository: `51mns/AIMath-public`

This branch is review-only evidence. It does not modify `main`, any canonical lock, any Task/Campaign/Truth state, or PR #52.

## 1. Accepted live boundary before replay

The resumed live-field execution reached exact canonical M4 and production `ACTIVE_NEXT`:

```text
M4 = c861bf0aef4d98c52f0792e5761ece27d0524264
ACTIVE_NEXT
CANONICAL_ACQUIRE_ID = 86fd3b3698155eab1c5ed4e14ba9d78aef01bf600ecbb9014e4923b57541032c
TASK = TASK-DITTERT-N5-001
EXIT_CODE = 0
```

Canonical expected-next lock:

```text
path = coordination/locks/dittert-n5/broader-zero-pattern.yml
blob = 042775d7a876b807dda6ed3e67102336ff5e5f8a
lock_id = LOCK-NEXT-88465ECE8293E15A0CBB91974A5FCBAB
source_epoch_id = 730fe029ad2479bcb83f2d5ce9744f6f18578c783c2c8fa84f0d491e4d691065
```

The historical live plan and recovery supplement require an old-source-epoch replay negative control after `ACTIVE_NEXT` and require fail-closed rejection without any new RELEASE/ACQUIRE transport.

## 2. Replay input

The normal retained live state was preserved separately. A replay-only local retained-state file was created from the legitimate retained source epoch and exact RELEASE provenance only:

```text
source_task_id = TASK-EQUIANGULAR-R18-001
worker_id = w-0bebfd2fd11cb67f
principal_id = gh:51mns
source_epoch_id = 730fe029ad2479bcb83f2d5ce9744f6f18578c783c2c8fa84f0d491e4d691065
release_transport.head_sha = 89af6cb927e19c6d744cdbf3c03726b3efff3cae
current_main_sha = c861bf0aef4d98c52f0792e5761ece27d0524264
```

The accepted public production operator surface was invoked once with that separate retained-state path. No second replay invocation was performed.

Observed operator result:

```text
LATEST_VERIFY_NOT_SUCCESS
EXIT_CODE=3
```

This was not `OLD_ACQUISITION_REPLAY` and not an equivalent fail-closed old-epoch rejection.

## 3. Unexpected transport created by replay

Fresh GitHub observation after the single replay invocation found a new deterministic ACQUIRE transport:

```text
PR = #52
state = open
merged = false
draft = true
base_sha = c861bf0aef4d98c52f0792e5761ece27d0524264
head_sha = a178b69e9c6229e5cc1da7d7bcbb3646fa6138e2
head_ref = next-acquire/e41095302836fbc77ccf0a6b2e08278d3fd54f5c9e579dbf3849d07bf815ec1c/TASK-FIXED-433-001/w-0bebfd2fd11cb67f
acquire_intent_id = e41095302836fbc77ccf0a6b2e08278d3fd54f5c9e579dbf3849d07bf815ec1c
selected_task_id = TASK-FIXED-433-001
work_ref = research/TASK-FIXED-433-001/w-0bebfd2fd11cb67f
collision_key = fixed-433/literature-placement
lock_id = LOCK-NEXT-E41095302836FBC77CCF0A6B2E08278D
acquired_at = 2026-09-04T05:40:10+00:00
```

The generated lock payload persisted the same historical source epoch:

```text
next_binding.source_epoch_id = 730fe029ad2479bcb83f2d5ce9744f6f18578c783c2c8fa84f0d491e4d691065
```

Thus the retained old source epoch passed RELEASE provenance, fresh-reranked current state after M4, and prepared a third-task ACQUIRE transport instead of being rejected as stale/consumed.

Exact-head Verify for this unintended transport also completed successfully:

```text
workflow = Verify public release
run_number = 130
run_id = 33841353129
head_sha = a178b69e9c6229e5cc1da7d7bcbb3646fa6138e2
run_attempt = 1
status = completed
conclusion = success
```

The PR remains draft because no second replay invocation was performed. It has not been canonicalised.

## 4. Canonical containment at freeze

Fresh `main` remains exactly:

```text
c861bf0aef4d98c52f0792e5761ece27d0524264
```

The canonical Dittert M4 lock remains unchanged. The unintended `TASK-FIXED-433-001` transport is PR-head/draft-only and has no canonical ownership authority.

No manual Ready transition, merge, lock deletion, branch deletion, RENEW, TAKEOVER, or further `/next` replay was performed after observation.

## 5. Failure classification for independent review

Observed live invariant failure:

```text
OLD_SOURCE_EPOCH_REPLAY_FAIL_CLOSED = NO
UNINTENDED_NEW_ACQUIRE_TRANSPORT_CREATED = YES
CANONICAL_MAIN_MUTATED_BY_REPLAY = NO
UNINTENDED_PR_DRAFT = YES
UNINTENDED_VERIFY_SUCCESS = YES
```

Provisional execution verdict:

```text
LIVE_FIELD_ABORTED_OLD_EPOCH_REPLAY_TRANSPORT_CREATED
```

Independent review must determine root cause, severity, whether the replay construction is a valid realization of the frozen replay control, and the minimal remediation/resume/cleanup policy. Until that review, preserve PR #52 and its ref as evidence and do not advance or merge it.
