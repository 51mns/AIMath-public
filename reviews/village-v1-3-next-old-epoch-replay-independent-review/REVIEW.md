# Village v1.3 `/next` old-source-epoch replay independent review

TASK-ID: `AIMATH-VILLAGE-V1-3-OLD-EPOCH-REPLAY-INDEPENDENT-REVIEW`

Status: **FAIL / REMEDIATION REQUIRED**

Repository: `51mns/AIMath-public`

Review base / fresh current main at review start:

```text
c861bf0aef4d98c52f0792e5761ece27d0524264
```

This review is independent and review-only. It changes no production code, no canonical `main`, no current Dittert lock, and no PR #52 state/ref. The only repository mutation made by this lane is this review file on its dedicated review branch.

## 1. Fresh production/evidence snapshot

Fresh GitHub read-back established:

```text
CURRENT_MAIN = c861bf0aef4d98c52f0792e5761ece27d0524264
M4_TASK      = TASK-DITTERT-N5-001
M4_LOCK_PATH = coordination/locks/dittert-n5/broader-zero-pattern.yml
M4_LOCK_BLOB = 042775d7a876b807dda6ed3e67102336ff5e5f8a
M4_LOCK_ID   = LOCK-NEXT-88465ECE8293E15A0CBB91974A5FCBAB
M4_SOURCE_EPOCH_ID = 730fe029ad2479bcb83f2d5ce9744f6f18578c783c2c8fa84f0d491e4d691065
```

The frozen failure evidence exists at:

```text
branch = review/village-v1-3-next-old-epoch-replay-live-failure
commit = f9f0e3acd642ae639bd08d8e92b969434594eb2c
path   = reviews/village-v1-3-next-old-epoch-replay-live-failure/REPLAY_FAILURE_REPORT.md
blob   = 5da0bae4fe3a1bba381bae0dd5407aaa0d3ed181
```

Fresh PR #52 observation:

```text
state  = OPEN
draft  = TRUE
merged = FALSE
base   = c861bf0aef4d98c52f0792e5761ece27d0524264
head   = a178b69e9c6229e5cc1da7d7bcbb3646fa6138e2
ref    = next-acquire/e41095302836fbc77ccf0a6b2e08278d3fd54f5c9e579dbf3849d07bf815ec1c/TASK-FIXED-433-001/w-0bebfd2fd11cb67f
```

Its only lock addition is `coordination/locks/fixed-433/literature-placement.yml`, and the exact payload has:

```text
task_id = TASK-FIXED-433-001
lock_id = LOCK-NEXT-E41095302836FBC77CCF0A6B2E08278D
acquire_intent_id = e41095302836fbc77ccf0a6b2e08278d3fd54f5c9e579dbf3849d07bf815ec1c
next_binding.source_epoch_id = 730fe029ad2479bcb83f2d5ce9744f6f18578c783c2c8fa84f0d491e4d691065
```

Fresh Verify observation for that exact head:

```text
run_number  = 130
run_id      = 33841353129
run_attempt = 1
head_sha    = a178b69e9c6229e5cc1da7d7bcbb3646fa6138e2
status      = completed
conclusion  = success
```

The unintended transport is therefore real and exact-head green, but remains draft/noncanonical. Fresh main is still M4 and the canonical Dittert lock is unchanged.

## 2. Authority/spec comparison

### Historical `FIELD_TEST_PLAN`

The accepted live plan explicitly requires that, after M4 `ACTIVE_NEXT`, replaying the exact original `SOURCE_EPOCH_ID` produce `OLD_ACQUISITION_REPLAY` or an authority-equivalent fail-closed result. It additionally requires **no new RELEASE ref/PR, no new ACQUIRE ref/PR, no second next lock, main unchanged, and the current next lock untouched**.

### V3 live supplement

The V3 compatibility supplement preserves the historical old-source-epoch replay control as mandatory. It does not weaken it when `CanonicalAcquireIdentityV3` is introduced. It also requires the historical replay result to remain in the final M4 evidence bundle.

### Recovery supplement

The accepted recovery supplement again requires: first establish canonical V3 `ACTIVE_NEXT`, then execute the preregistered old-source-epoch replay negative control and require fail-closed rejection. It names acceptance of an old-source-epoch replay as a stop condition.

### Accepted Phase B frozen spec

The frozen Phase B transport contract makes `source_epoch_id` the logical RELEASE epoch, requires exact RELEASE provenance after source-lock absence, and specifies that old acquisition replay has no release/select/acquire authority. Its idempotency table also states that an old acquisition cannot control a later independent acquisition.

The concrete frozen spec is strongest about a *newer source acquisition* and exact expected-acquisition mismatch, but it does not define a durable canonical index/guard saying “this source epoch has already successfully produced a next acquisition”. That omission is a specification-enforcement gap, not permission to rerank a consumed epoch: the accepted live plan and supplements unambiguously require the post-M4 replay to stop.

### Current production architecture

Current `docs/VILLAGE_ARCHITECTURE_V1_3_PHASE_B.md` says the retained `.git/village-next-phase-b.json` file is **continuity only**; canonical bytes/history remain authoritative. Every v1.3 next lock persists `next_binding.source_epoch_id` precisely so the semantic source epoch is present in canonical acquisition bytes.

Therefore a local replay-state file is not allowed to become the sole source of truth for whether the epoch is consumed.

## 3. Replay construction validity

**PASS: the replay construction is a valid realization of the frozen old-source-epoch replay negative control.**

Reasons:

1. The canonical M4 acquisition had already succeeded and remained intact.
2. The ordinary successful M4 retained state was preserved separately rather than corrupted.
3. The replay-only state contained only legitimate historical state already sufficient to prove the exact source acquisition epoch and exact RELEASE transport/provenance: `schema_version`, repository, `source_acquisition_v1`, exact `source_epoch_id`, and `release_transport`.
4. The accepted production operator itself accepts a caller-selected `--phase-b-state-file`; the state file is continuity evidence, not canonical authority.
5. The historical test contract asks to replay the exact old epoch after M4. It does not require the adversarial replay input to help the implementation by carrying the latest successful `canonical_acquire_identity_v3`.
6. If omission of that local V3 record can restore scheduling authority to an already-consumed epoch, the correct production behavior is fail-closed, not rerank.

The observed result `LATEST_VERIFY_NOT_SUCCESS / exit 3` is therefore a genuine negative-control failure, not a malformed-test artifact.

## 4. Root cause

**Root cause: missing canonical source-epoch consumption guard before post-RELEASE reranking.**

The current production flow is:

1. read retained state;
2. **only if** `retained["canonical_acquire_identity_v3"]` exists, run `_confirm_retained_acquire` before retry/rerank;
3. if that field is absent and the source lock is already absent, accept retained source identity and call `_prove_retained_release`;
4. `_prove_retained_release` correctly proves the old source lock was canonically released and its terminal remains exact;
5. after that proof succeeds, immediately collect current PENDING observations and call fresh post-RELEASE selection/ranking;
6. prepare a new ACQUIRE transport from that fresh selection.

There is no intervening check of current canonical lock bytes or canonical first-parent history asking whether the same `source_epoch_id` has **already been consumed by a prior successful v1.3 next acquisition**.

This distinction matters: `_prove_retained_release` proves “this source epoch really was released”; it does **not** prove “this released epoch is still unused for continuation”. Treating the first as the second is the bug.

At M4 the missing fact was directly available in canonical bytes. The Dittert lock already contains:

```text
next_binding.source_epoch_id = 730fe029ad2479bcb83f2d5ce9744f6f18578c783c2c8fa84f0d491e4d691065
```

That equals the replayed historical epoch. Because the replay-only local state omitted `canonical_acquire_identity_v3`, the implementation skipped `_confirm_retained_acquire`, proved RELEASE provenance again, reranked M4, selected `TASK-FIXED-433-001`, and created PR #52 with the *same* historical source epoch in its new `next_binding`.

The generated PR is therefore a direct witness of double consumption of one source epoch at the transport-authority layer.

## 5. Required canonical consumption guard

**YES — `source_epoch_id` needs a canonical “already consumed by a next acquisition” guard before reranking.**

The minimal authority rule should be:

> Once a validated canonical v1.3 ACQUIRE transition has consumed source epoch `S`, later invocations carrying `S` may confirm/re-read that exact acquisition when the full retained V3 identity is available, but `S` may never enter fresh ranking or create a different ACQUIRE intent again.

The guard must execute after exact RELEASE provenance is proven but **before** `_pending_records_from_open_acquire_prs`, `_derive_post_release_semantics`, or any ACQUIRE transport write.

It must be canonical/durable, not dependent on the local retained file. At minimum it must detect a current canonical v1.3 lock bundle with valid `next_binding.source_epoch_id == S`. For durable replay protection after the acquired lock is later released during cleanup, the robust minimal form should also inspect complete canonical first-parent history back through the proven RELEASE boundary and recognize any validated canonical v1.3 ACQUIRE transition whose complete lock bundle carries `next_binding.source_epoch_id == S`.

If such a canonical consumption is found and the exact current acquisition was not already confirmed through the full retained V3 path, return existing `OLD_ACQUISITION_REPLAY` (or a strictly equivalent fail-closed code) and perform zero transport writes.

If the required canonical-history observation is incomplete or ambiguous, fail closed rather than rerank.

A new durable “consumed epoch” ledger could also solve this, but it is more invasive than reusing the canonical `next_binding` plus first-parent history already present in v1.3.

## 6. 73-row oracle gap

**ORACLE GAP: YES.**

The existing row to strengthen is **Row 13**:

```text
test_row_13_old_source_acquisition_replay_changes_source_epoch
```

Despite its replay name, Row 13 currently only constructs two source records one second apart and asserts that their `source_epoch_id` digests differ. It does not invoke the production operator, does not model an already-consumed source epoch, and does not assert zero RELEASE/ACQUIRE transport writes.

No Row 74 is needed.

Strengthen Row 13 into the actual one-shot replay oracle, with subcases if useful:

1. canonical current state contains a validated v1.3 next lock whose `next_binding.source_epoch_id = S`;
2. replay retained state contains only legitimate historical source epoch + RELEASE provenance, deliberately omitting `canonical_acquire_identity_v3`;
3. invoke production `cli_next` once;
4. require `OLD_ACQUISITION_REPLAY` or equivalent fail-closed status;
5. assert no blob/tree/commit/ref/PR/Ready/rerun transport mutation occurs and no fresh ranking reaches ACQUIRE preparation;
6. retain the existing “different acquisition time changes source epoch digest” assertion as a subcase if desired;
7. preferably add a second Row-13 subcase where the consumed acquisition exists only in canonical first-parent history after its lock was later released, proving replay protection survives cleanup.

## 7. Security severity

**HIGH.**

Impact:

- a legitimately historical, already-consumed source epoch can regain continuation authority;
- it can create a new ACQUIRE transport for a different Task after a successful canonical `ACTIVE_NEXT`;
- the first observed invocation already created a deterministic draft PR and its exact head obtained successful Verify;
- the production handoff path can, on a subsequent invocation, move an exact green draft toward Ready/rerun/trusted-lifecycle eligibility, so this is not merely diagnostic output corruption;
- if allowed to complete, the defect can create unintended canonical EXCLUSIVE scheduling ownership from a stale epoch.

Why not CRITICAL:

- the observed one replay invocation did not mutate canonical `main`;
- PR #52 is still draft and PENDING is explicitly not ownership;
- the existing M4 lock was not changed;
- no Truth/claim/review authority is granted by this path;
- exploitation requires legitimate historical epoch/RELEASE evidence plus the authenticated production operator authority, not an unauthenticated arbitrary GitHub user.

Classification:

```text
CRITICAL = NO
HIGH     = YES
MEDIUM   = NO
LOW      = NO
```

## 8. Verdict and minimal remediation

```text
VERDICT = FAIL_REMEDIATION_REQUIRED
```

Minimum remediation before live continuation:

1. add the canonical consumed-source-epoch gate described above before reranking;
2. strengthen existing Row 13 rather than inventing Row 74;
3. make the Row-13 fixture use the production orchestration path and a retained state without `canonical_acquire_identity_v3`;
4. assert **zero transport writes** on consumed-epoch replay;
5. preserve the current full-V3 retained-state `ACTIVE_NEXT` confirmation path and same-intent pending transport reuse behavior;
6. independently review the patch at a fixed commit;
7. merge only after repository validation/CI and remote read-back.

This reviewer does not prescribe unrelated refactors.

## 9. PR #52 / M4 lock / cleanup policy

### PR #52 and replay ref

For now:

```text
KEEP OPEN
KEEP DRAFT
DO NOT READY
DO NOT MERGE
DO NOT DELETE REF
DO NOT REPURPOSE
```

They are frozen evidence until remediation is independently accepted and the failure/review evidence has been read back.

After accepted remediation, before the replay negative control is rerun, the safe cleanup is to **close PR #52 without merge** and then delete only its unintended `next-acquire/e410...` ref under an explicit cleanup step. This review does not perform either action.

### Current Dittert M4 lock

Keep the exact M4 Dittert lock byte-for-byte unchanged during remediation/review. Do not renew, takeover, manually delete, or replace it merely to work around this failure.

### Eventual field-test cleanup

After the remediation is accepted and the old-epoch replay control passes, return to the already frozen V3 cleanup strategy:

1. create only the Dittert worker's truth-neutral `ABANDONED_TERMINAL` through ordinary policy;
2. use the exact-worker RELEASE primitive directly against the exact Dittert lock;
3. let trusted lifecycle canonicalize that RELEASE;
4. **do not call `/next` again during cleanup**;
5. fresh-read main and prove zero active field-test locks and no Truth/claim/review side effect.

If the Dittert lock changes, is replaced, or expires before the resumed replay can establish the exact preserved M4 acquisition, stop and reassess rather than silently renewing it.

## 10. Live-test resume policy

A full M0→M4 restart is **not required** merely because of this failure: the failed replay created only noncanonical transport state, while M4 main/lock remained exact at freeze.

However the live test must not resume immediately.

Safe policy:

```text
STOP_AT_M4
→ patch consumed-epoch guard + strengthen Row 13
→ independent review PASS
→ merge remediation through ordinary policy
→ freeze a narrow recovery supplement binding the remediation merge to the still-exact preserved M4 acquisition
→ clean PR #52/ref without merge after evidence preservation
→ fresh-reconstruct the M4 CanonicalAcquireIdentityV3/current exact lock from canonical Git
→ rerun the old-source-epoch replay negative control once
→ require OLD_ACQUISITION_REPLAY/equivalent + zero transport writes
→ run final idempotency sentinel
→ perform frozen truth-neutral Dittert cleanup
```

Because a remediation merge advances current main beyond literal `c861bf...`, the resumed run must treat `c861bf...` as the preserved M4 acquisition transition, not pretend the remediation commit is the old M4. The V3 current-state proof must show that the exact M4 lock remains current, unchanged, active, and on canonical first-parent ancestry.

If that proof fails or the lease has expired, this resume authorization no longer applies; restart/reassessment is required.

## 11. Final independent determination

```text
REPLAY_TEST_VALID                    = YES
ROOT_CAUSE                           = MISSING_CANONICAL_SOURCE_EPOCH_CONSUMPTION_GUARD_BEFORE_RERANK
SOURCE_EPOCH_CONSUMPTION_GUARD_MISSING = YES
ORACLE_GAP                           = YES
ROW_TO_STRENGTHEN                    = 13
CRITICAL                             = NO
HIGH                                 = YES
MEDIUM                               = NO
LOW                                  = NO
VERDICT                              = FAIL_REMEDIATION_REQUIRED
REMEDIATION_REQUIRED                 = YES
```
