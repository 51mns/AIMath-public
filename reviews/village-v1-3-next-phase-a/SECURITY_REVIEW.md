# Village v1.3 `/next` Phase A independent security and correctness review

## Review target

- Repository: `51mns/AIMath-public`
- Current main fresh-read: `df7ceb5e685239b936950a0dd01a13e4e38b69eb`
- PR: `#34`
- Fixed target: `5bb2072cec88c6774050aa270aae82e31f46eeec`
- Writer branch: `platform/village-v1-3-next-phase-a-core`
- Frozen specification commit: `5eed8cc40243eba166afee651104f3c4a79d99ac`
- Frozen specification path: `reviews/village-v1-3-next-preflight/NEXT_FROZEN_SPEC.md`
- Frozen specification blob: `ad851bd4fece0f3f45126ae12da3b54a3a7a5832`

Fresh read-back found no target drift or material main drift. PR #34 is open, unmerged, based on the current main, and its head and writer remote branch both resolve to the fixed target.

The exact PR #34 scope is three files only:

- `docs/VILLAGE_ARCHITECTURE_V1_3.md` — blob `d3f6ba6a6c0bbd6adcaf36b87189efdf356c303b`
- `scripts/test_village_v1_3_next.py` — blob `3f2aef79caee3a70f8b35116e759053e785b682f`
- `scripts/village_next.py` — blob `354c95ac2b33c505d0a6ba8fbad77d54ca659fe2`

`scripts/village.py` is not changed by PR #34.

## Verdict

**FAIL — BLOCK integration of PR #34 at fixed head `5bb2072cec88c6774050aa270aae82e31f46eeec`.**

A HIGH-severity state/authority-binding defect exists in `ACTIVE_NEXT` recognition. The frozen contract requires the next active state to be bound to the exact intended next Task and retained identity/transport facts. The implementation instead recognizes any other active canonical lock for the same `worker_id` and principal before running continuation-aware selection. This can bypass the pure-core human/portfolio/selection gates and makes a stale or unrelated lock look like the result of the current `/next` epoch.

Per the task's explicit stop condition, discovery of a HIGH finding stops the review before non-blocking remainder work or writer-file modification. No writer code was changed.

## HIGH findings

### H-01 — `ACTIVE_NEXT` is not bound to the selected next Task / request epoch

**Severity:** HIGH  
**Area:** ownership, continuation gate, deterministic selection, replay/idempotency boundary

`_canonical_next_lock(state, request)` scans `state.active_lock_bundles()` and accepts a match when all of the following hold:

1. lock Task is merely different from the source Task;
2. `worker_id` equals the retained worker;
3. actor principal equals the retained principal.

It does **not** bind that lock to:

- the Task selected by continuation-aware hard filtering and `rank_v12`;
- an expected ACQUIRE transport or request/acquisition epoch;
- the selected Task's exact collision-key bundle;
- the selected worker workspace / `work_ref`;
- the continuation decision that authorised that Task.

`derive_next_state()` then checks `_canonical_next_lock()` **before** `select_next_task()`. Therefore an unrelated existing active lock for the same worker/principal is enough to return:

- phase `ACTIVE_NEXT`;
- status `ACTIVE_NEXT`;
- `canonical_ownership=True`;

without demonstrating that this lock is the result of this `/next` continuation.

This is not a PENDING-vs-ownership confusion: the lock is canonical. The defect is that the implementation converts **unrelated canonical ownership** into **this `/next`'s next-work authority/status** without the frozen exact-next binding.

#### Adversarial control

A reviewer-side temporary control reproduced the exact matching predicate with:

- source Task `TASK-SOURCE`;
- retained worker `w-aaaaaaaaaaaaaaaa`;
- retained principal `gh:alice`;
- one active canonical lock on unrelated `TASK-UNRELATED` with the same worker/principal.

Observed predicate result:

```text
matched_task = TASK-UNRELATED
errors = ()
Would be accepted by predicate despite no selected-task/epoch/collision/work_ref binding = True
```

The code path then returns `ACTIVE_NEXT` before invoking continuation-aware ranking.

#### Security/correctness impact

A stale/replayed `/next` request, or a worker that legitimately owns another active lock, can have that unrelated lock treated as the next acquisition for the completed source Task. In particular, the `ACTIVE_NEXT` fast path does not enforce the `ContinuationDecision` that was just derived. It can therefore skip the same-Campaign human gate and the hard-filter/rank path that would otherwise yield `WAITING_PORTFOLIO`, `NO_ELIGIBLE_TASK`, or a different selected Task.

This violates the frozen semantics that `ACTIVE_NEXT` is reached only after the intended next acquisition is canonically established with exact Task/worker/principal and transport/workspace binding. It also makes the Section 14 replay/idempotency boundary unsafe to defer: Phase A is already making an `ACTIVE_NEXT` claim without sufficient epoch/target binding.

#### Required fix

Do not let “any same-worker/principal active lock” define the next Task.

A corrected design must do one of the following before returning `ACTIVE_NEXT`:

1. derive the expected next Task through the frozen continuation gates + hard eligibility + `rank_v12`, then require the canonical active lock to match that exact Task and exact worker/principal/workspace/collision binding; or
2. if replay/transport binding is intentionally Phase B, provide a trusted Phase-B expected-next/acquisition-epoch binding to the pure core and require exact equality before `ACTIVE_NEXT`.

In either design, unrelated active locks must not short-circuit selection. Add adversarial tests for at least:

- unrelated same-worker/principal active lock;
- missing required HUMAN_MAINTAINER continuation decision plus unrelated active lock;
- global admission `PAUSED` plus unrelated active lock;
- replayed old `/next` epoch after a later independent acquisition;
- exact selected Task but wrong workspace/collision binding.

## MEDIUM findings

### M-01 — expired source lock is treated as canonical ownership / active work

**Severity:** MEDIUM  
**Area:** ownership state correctness

`_canonical_lock_for_task()` calls `state.lock_for_task(task_id, active_only=False)`. In the inherited `VillageState`, `active_only=False` includes expired bundles, while `runtime_state()` distinguishes an expired bundle as `EXPIRED` and only `active_lock_bundles()` represents live ownership.

Consequently, an expired source bundle can enter the same branch as a live source lock. With no terminal evidence, `derive_next_state()` can return `ACTIVE_WORK` with `canonical_ownership=True`; with terminal evidence it can return `RELEASE_REQUIRED` while still reporting ownership.

The frozen Phase A meaning of `ACTIVE_WORK` is that the current canonical lock is still owned. An expired lease is not an active ownership lock under the inherited runtime model.

**Required change:** distinguish active source ownership from an expired/stale lock artifact. Do not report `canonical_ownership=True` or `ACTIVE_WORK` solely because an expired bundle still exists. Preserve any required cleanup/release behavior as a separate fail-closed/transport concern.

## LOW findings

### L-01 — architecture document overstates `village.py test` registration at PR #34 fixed head

The final sentence of `docs/VILLAGE_ARCHITECTURE_V1_3.md` says that `scripts/village.py test` includes the v1.3 direct suite. At PR #34 fixed head, `scripts/village.py` is deliberately unchanged and does **not** register `scripts/test_village_v1_3_next.py`.

The registration exists only in companion PR #35 and is intentionally dependent on PR #34 merging first. The architecture statement should be made phase/PR accurate.

## Frozen-spec correspondence

The Phase A source otherwise preserves several important frozen boundaries:

- exact eight `NextPhase` values are represented;
- `RequiredAction` is intent only;
- no GitHub/network write, branch creation, PR creation, merge, Truth promotion, I2/I3 promotion, automatic RENEW, or automatic TAKEOVER surface is present in `scripts/village_next.py`;
- terminal evidence is restricted to canonical RESULT/ABANDONED paths;
- the eight result `outcome_type` values are preserved rather than collapsed to success/failure;
- `ABANDONED_TERMINAL` is represented with `truth_layer_effect=NONE`;
- `review_required` does not block writer RELEASE intent;
- worker/principal source-lock mismatch fails closed;
- PENDING observations do not directly create `ACTIVE_NEXT`;
- hard candidate filtering is applied before reuse of `rank_v12`;
- rank exceptions return `RANK_FAILED` with no first/random/self-selected fallback;
- source Task is explicitly excluded from ordinary next-task eligibility.

These positives do not cure H-01 because the `ACTIVE_NEXT` shortcut runs outside the selection result it is supposed to certify.

## Frozen Section 14 mapping audit

All 38 frozen tests appear exactly once in the architecture table. Independent recount:

- `IMPLEMENTED_IN_PHASE_A`: **15**
- `DEFERRED_TO_PHASE_B`: **17**
- `DEFERRED_TO_REVIEW_AUTONOMY_PHASE`: **6**
- total: **38**

The coarse decomposition is reasonable for transport/review-autonomy work, but the mapping is **not acceptance-sound at this fixed head** because replay/epoch binding (#7) is marked Phase B while Phase A already returns `ACTIVE_NEXT` using an under-bound canonical-lock shortcut. Deferral is safe only if Phase A does not make an authoritative next-state claim that depends on the deferred binding.

## Tests and CI

### Exact-head CI #102

Fresh GitHub Actions read-back for target `5bb2072cec88c6774050aa270aae82e31f46eeec`:

- workflow: `Verify public release`
- run ID: `33621142169`
- run number: `102`
- conclusion: `SUCCESS`
- verify job: `SUCCESS`

All recorded steps are green, including workflow security, PR policy, DCO, public audit/layout, Village validation, existing Village v1/v1.1/v1.2/v1.2.1 suites, REUSE/SPDX, manifest generation, and public claim reproduction.

As frozen in the task, CI #102 does not execute `scripts/test_village_v1_3_next.py` directly because PR #34 does not modify the governance-only `scripts/village.py` registry.

### Writer direct suite

The target direct suite contains 27 unittest methods/cases by method count (including `test_09b`) and covers many Phase A controls. Its existing writer result is not treated as independent evidence.

### Reviewer fresh direct/regression execution

**NOT COMPLETED after H-01 discovery, by explicit review stop condition.**

The task specifies `CRITICAL/HIGH discovery` as a stop condition. Once H-01 was confirmed from the fixed target and an independent adversarial predicate control, the reviewer did not continue into non-blocking fresh-suite execution and did not modify writer files to add a test. CI #102 was freshly read back but is not represented as a substitute for the requested reviewer-side direct v1.3 execution.

This incompleteness cannot improve the verdict: a confirmed HIGH already violates the PASS conditions and blocks integration.

## Companion PR #35

Read-only verification only; PR #35 was not reviewed as an integration target and was not changed.

- PR #35 head: `ce3c55a918a8c524f3fc3ee58416f8667c1c4aac`
- changed files: exactly `scripts/village.py`
- target blob: `78bad6eebe1cd702420fc5e6902ed90b3e349b8b`
- CI run #103 / run ID `33621187406`: `FAILURE`

The failure is the expected dependency failure: `village.py test` attempts to execute `scripts/test_village_v1_3_next.py`, which is not present on PR #35's current base because PR #34 is not merged. This is not the H-01 core defect and must not be used to excuse or amplify it. PR #35 still requires rebase/recreation and fresh CI after a corrected Phase A core is accepted and merged.

## Integration recommendation

**BLOCK.**

Do not merge PR #34 fixed head `5bb2072cec88c6774050aa270aae82e31f46eeec`.

Required next sequence:

1. writer fixes H-01 (and M-01) on the writer lane or a replacement Phase A branch;
2. add adversarial controls covering exact next-lock/epoch binding and expired source locks;
3. freeze a new writer target SHA;
4. run direct v1.3 + full regressions + exact-head CI;
5. perform a fresh independent review of the new fixed target;
6. only after Phase A acceptance, rebase/recreate companion PR #35 and run fresh CI.
