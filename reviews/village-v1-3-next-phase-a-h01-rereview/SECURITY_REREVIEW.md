# Village v1.3 `/next` Phase A H-01 focused independent rereview

## Review target

- Repository: `51mns/AIMath-public`
- Fresh current `main`: `df7ceb5e685239b936950a0dd01a13e4e38b69eb`
- PR: `#34`, open and unmerged
- Writer branch: `platform/village-v1-3-next-phase-a-core`
- New fixed target: `9eb049a32ffe235e0881a6e8c9c7b20a4ab16ccc`
- Historical rejected target: `5bb2072cec88c6774050aa270aae82e31f46eeec` — **remains NOT ACCEPTED**
- Frozen specification commit: `5eed8cc40243eba166afee651104f3c4a79d99ac`
- Frozen specification path: `reviews/village-v1-3-next-preflight/NEXT_FROZEN_SPEC.md`
- Frozen specification blob: `ad851bd4fece0f3f45126ae12da3b54a3a7a5832`

Fresh start and final drift checks agreed: `main` stayed at the expected SHA; PR #34 and the writer branch both stayed at the new fixed target.

The exact base-to-target scope is three files only:

- `docs/VILLAGE_ARCHITECTURE_V1_3.md`
- `scripts/test_village_v1_3_next.py`
- `scripts/village_next.py`

`scripts/village.py` is not changed.

Exact target blobs independently read from GitHub:

- `scripts/village_next.py` — `39efe7efddc46ff43315e04b06df0baf4601327b`
- `scripts/test_village_v1_3_next.py` — `c95642a2fefbf3deb5f9c7f160f182d69a959b2e`
- `docs/VILLAGE_ARCHITECTURE_V1_3.md` — `04913f96ec79cef20e23b2483d593090ed3b7bdd`

## Decision

**PASS_WITH_REQUIRED_CHANGES — code-level H-01, M-01 and L-01 are CLOSED at the new fixed target, but integration remains BLOCKED until a reviewer can independently execute the exact target from a real fresh checkout/materialisation.**

This environment could read immutable GitHub refs, commits, blobs, PR metadata, code and CI directly, but its shell could not resolve `github.com` for `git clone`. I therefore did not substitute a writer-reconstructed tree or the writer's reported direct-suite result for independent execution. That explicit execution gap prevents an unconditional `PASS` under the rereview contract even though the corrected source and CI evidence are otherwise consistent.

## Historical finding preservation

The original independent review at commit `5fe2d40b100f885109addc2030d4a03f7d169e6b`, artifact blob `b91f14a0cfcba99beec7090c3413337779e1c745`, remains valid historical evidence against fixed target `5bb2072cec88c6774050aa270aae82e31f46eeec`:

- H-01 HIGH: unbound `ACTIVE_NEXT` recognition bypassed continuation/rank.
- M-01 MEDIUM: expired source artifact could be reported as active ownership.
- L-01 LOW: architecture overstated v1.3 registration in `scripts/village.py test`.

Nothing in this rereview rewrites that target to accepted status.

## H-01 focused rereview

**H-01: CLOSED at `9eb049a32ffe235e0881a6e8c9c7b20a4ab16ccc`.**

Independent source inspection found:

1. The old `_canonical_next_lock()` shortcut is absent from the corrected target.
2. `derive_next_state()` has no scan that converts an unrelated same-worker/principal next-task lock into `ACTIVE_NEXT`.
3. The only scan of `state.active_lock_bundles()` in `scripts/village_next.py` is the inherited same-worker EXCLUSIVE-capacity check. It only excludes candidates; it does not create ownership or `ACTIVE_NEXT` authority.
4. After canonical source release/absence with valid terminal evidence, the corrected path is `derive_continuation_decision -> hard eligibility -> rank_v12 -> ACQUIRE_PENDING` when a candidate is selected.
5. `NextPhase.ACTIVE_NEXT` and `NextStatus.ACTIVE_NEXT` remain as frozen Phase-B enum names, but there is no `phase=NextPhase.ACTIVE_NEXT` or `status=NextStatus.ACTIVE_NEXT` return in Phase A.
6. A bare canonical candidate lock is therefore insufficient to establish the current `/next` acquisition epoch.
7. There is no weaker same-task, same-worker, same-principal or same-work-ref replacement shortcut. `work_ref` and exact collision/ACQUIRE binding are explicitly deferred instead of partially reconstructed in Phase A.
8. Major outcomes automatically require the human continuation gate even if the advisory request flag is omitted. Only a matching canonical decision with `authority = HUMAN_MAINTAINER` satisfies that gate.
9. `global_admission != OPEN` disables both same-Campaign and global fallback selection and yields a wait state rather than being bypassed by a canonical lock.

### H-01 adversarial controls

I constructed an independent reviewer oracle directly from the frozen specification, without using the writer remediation report. It exercised the required adversarial states and all produced non-`ACTIVE_NEXT` outcomes:

| Control | Independent expected safe outcome |
|---|---|
| A. major outcome + missing human gate + unrelated same-worker/principal active lock | `WAITING_PORTFOLIO`, never `ACTIVE_NEXT` |
| B. global admission `PAUSED` + unrelated same-worker/principal lock | `WAITING_PORTFOLIO`, never `ACTIVE_NEXT` |
| C. ordinary terminal + unrelated same-worker/principal lock | unrelated lock not interpreted as current `/next` acquisition |
| D. active lock on candidate likely to rank first but no acquisition-epoch binding | not `ACTIVE_NEXT` |
| E. old/replayed same-worker/principal acquisition | not `ACTIVE_NEXT` |
| F. candidate-looking lock with wrong `work_ref` | not `ACTIVE_NEXT` |
| G. candidate-looking lock with wrong collision bundle | not `ACTIVE_NEXT` |

The corrected target's own test source independently read from GitHub contains corresponding executable controls (`test_20`, `test_20b` through `test_20f`) and the source call graph is consistent with the reviewer oracle. I do **not** count the writer-authored tests or writer execution report as independent execution evidence.

### Phase-B binding boundary

The corrected architecture and implementation now place exact `ACTIVE_NEXT` confirmation entirely in Phase B. Before Phase B may return that state it must bind equivalent exact evidence for at least:

- selected Task;
- immutable request/acquisition epoch;
- worker;
- principal;
- deterministic workspace / `work_ref`;
- exact collision-key bundle;
- canonical ACQUIRE transport/lifecycle identity.

This makes frozen test #7's replay/epoch deferral acceptance-sound at the Phase-A boundary: Phase A no longer makes the authority claim whose proof is deferred.

## M-01 focused rereview

**M-01: CLOSED at the new fixed target.**

`_canonical_lock_for_task()` now distinguishes all canonical lock artifacts (`active_only=False`) from actually active locks (`active_only=True`). If an artifact exists but no active lock exists, it reports a stale/expired condition. `derive_next_state()` then fails closed with:

- `canonical_ownership=False`;
- `required_action=NONE`;
- no `PREPARE_RELEASE`;
- no `PREPARE_ACQUIRE`;
- no selected next Task.

The inherited `VillageState` semantics independently confirm the distinction: `active_lock_bundles()` requires unexpired leases, `runtime_state()` reports active lock as `ACTIVE` and a remaining non-active artifact as `EXPIRED`.

Independent expired-source oracle controls therefore give:

1. expired source + no terminal -> `FAIL_CLOSED`, ownership false, action `NONE`;
2. expired source + canonical terminal -> still `FAIL_CLOSED`, ownership false, no RELEASE/ACQUIRE intent;
3. expired artifact + otherwise eligible next work -> still fail closed rather than silently treating the source artifact as clean absence.

The corrected target contains executable tests `test_27` and `test_28` matching these semantics; again, their presence is source evidence, not independent execution evidence.

## L-01 focused rereview

**L-01: CLOSED.**

The corrected architecture is PR-accurate:

- PR #34 contains the direct v1.3 suite;
- PR #34 currently requires explicit `python3 scripts/test_village_v1_3_next.py`;
- `scripts/village.py` registration belongs to companion PR #35;
- PR #35 must be rebased/recreated after corrected #34 merges and then pass fresh exact-head CI;
- `ACTIVE_NEXT` confirmation belongs to Phase B.

## Frozen-boundary spot check

No source-level regression was found in the requested frozen Phase-A boundary:

- canonical RESULT/ABANDONED authority only;
- all eight exact outcome types preserved;
- `ABANDONED_TERMINAL.truth_layer_effect = NONE`;
- review demand does not retain writer ownership;
- self-evaluation has zero authority;
- human Continuation Gate remains human-maintainer authority;
- hard filtering occurs before `rank_v12`;
- `rank_v12` is reused rather than replaced;
- rank exceptions fail closed with no fallback;
- `PENDING_CLAIM` is not ownership;
- no network write, branch creation, PR creation, canonical mutation, Truth promotion, I2/I3, `RENEW`, or `TAKEOVER` authority is added by the Phase-A pure core.

## Frozen 38 mapping

I independently recounted all rows exactly once:

- `IMPLEMENTED_IN_PHASE_A`: **15**
- `DEFERRED_TO_PHASE_B`: **17**
- `DEFERRED_TO_REVIEW_AUTONOMY_PHASE`: **6**
- total: **38**

The four important boundary rows are now sound:

- #1 happy path: Phase A ends at `ACQUIRE_PENDING`; canonical activation is Phase B.
- #6 duplicate `/next`: transport reuse is Phase B.
- #7 old epoch replay: Phase B owns epoch binding; safe because Phase A never emits `ACTIVE_NEXT`.
- #23 `PENDING_CLAIM != ownership`: implemented in Phase A and no premature `ACTIVE_NEXT` exists.

## Execution and CI

### Direct v1.3 suite

**NOT independently executed in this environment.**

Required command:

```text
python3 scripts/test_village_v1_3_next.py
```

The corrected file contains 34 unittest methods/cases, including the H-01 and M-01 controls, but the writer-reported `34/34` is not accepted as reviewer proof.

A fresh shell checkout was attempted and failed before checkout because this runtime could not resolve `github.com`. GitHub connector reads still provided immutable exact-commit file contents and blob IDs, but connector content could not be established as a real executable checkout/materialisation in the shell. Per the rereview contract, reconstructed writer execution is not substituted.

### Required regressions

Independent local execution of the requested regression commands is therefore also **not established**. This is an evidence limitation, not a newly identified code defect.

### Exact-head CI #106

Fresh GitHub Actions read-back confirms:

- workflow: `Verify public release`;
- run number: `106`;
- run ID: `33623715373`;
- exact head: `9eb049a32ffe235e0881a6e8c9c7b20a4ab16ccc`;
- conclusion: `SUCCESS`.

The single `verify` job is successful. Successful steps include structural workflow security, PR policy/change class, DCO, public safety audit, public layout verification, Village validation/status/rank, Village synthetic tests, v1.1, v1.2, v1.2.1 Phase A and Phase B suites, REUSE/SPDX, live SHA-256 manifest generation, and public-claim reproduction.

CI #106 does **not** include the direct v1.3 suite, so it does not cure the independent-execution gap.

## Severity

### CRITICAL

None found.

### HIGH

None open at the new fixed target. Historical H-01 remains a valid HIGH finding against rejected target `5bb2072cec88c6774050aa270aae82e31f46eeec`; it is CLOSED for `9eb049a32ffe235e0881a6e8c9c7b20a4ab16ccc` by the corrected Phase-A authority boundary.

### MEDIUM

No open code-level MEDIUM finding. Historical M-01 is CLOSED at the new target.

The missing independent executable materialisation is a review-evidence blocker, not a product-code severity classification.

### LOW

No open LOW finding. Historical L-01 is CLOSED at the new target.

## Integration recommendation

**BLOCK pending one required verification step, not a writer-code remediation:** obtain a genuine fresh checkout/materialisation of exact target `9eb049a32ffe235e0881a6e8c9c7b20a4ab16ccc` in an independent reviewer environment and run the explicit v1.3 suite plus the required regression commands and REUSE lint. If those pass without target drift, this rereview has no remaining source-level CRITICAL/HIGH/blocking MEDIUM finding and can be promoted to unconditional PASS/MERGE_READY without reopening the historical rejected target.

Do not merge PR #34 from this artifact alone. Do not modify or merge PR #35 as part of this rereview.
