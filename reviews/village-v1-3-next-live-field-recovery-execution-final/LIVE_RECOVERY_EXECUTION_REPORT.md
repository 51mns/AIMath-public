# Village v1.3 `/next` live-field recovery execution — final

VERDICT: **LIVE_FIELD_PASS_CLEAN**

This report closes the preregistered Village v1.3 `/next` live-field campaign after three production integration defects were found, remediated, independently reviewed where required, and re-tested against the real GitHub lifecycle.

## Frozen lineage

- Original live-field plan: `705bd7c5250103e74118381106d422d50c677bb7`
- V3 supplement: `95edc35b9e54e91bd3d11ab58160f159508df2c7`
- First aborted-run report: `7cc9519e0c3b4c65d78dedb3f09772c86d245f83`
- ACTIVE_WORK mismatch review: `b8a50e6a825f126d697c36751e4135ba772cdb70`
- Recovery supplement: `1286873743877ec58371a0f54ae410bb89aaefd9`
- Old-epoch replay failure report: `f9f0e3acd642ae639bd08d8e92b969434594eb2c`
- Old-epoch replay independent review: `ec1f9f604574e5f37d4804269c4a916314b3e902`
- R2 independent remediation review: `f70f546da5ce9d77949860be1c0b32120f85ffa0`

## Production defects found and fixed

1. **ACTIVE_WORK terminal-ordering mismatch**
   - Live exact active source acquisition incorrectly failed `SOURCE_TERMINAL_UNPROVEN` before accepted Phase-A `ACTIVE_WORK` semantics could apply.
   - Fixed by routing the exact active/no-terminal case through accepted Phase-A derivation while retaining fail-closed behavior for stale, expired, malformed, or wrong-identity cases.

2. **GitHub RELEASE tree deletion payload**
   - Production RELEASE transport used deletion entries without explicit `mode`/`type`, causing GitHub `create-tree` HTTP 422 (`Must supply a valid tree.mode`).
   - Fixed by emitting explicit `mode=100644`, `type=blob`, `sha=null` deletion entries and strengthening the existing acceptance row.

3. **Consumed source-epoch replay**
   - After successful canonical Dittert acquisition, replaying the already-consumed Equiangular source epoch could reach fresh reranking and create an unintended ACQUIRE transport.
   - Initial R1 added canonical first-parent consumption detection before normal PENDING/rerank/ACQUIRE.
   - Independent review then found a residual HIGH path: a stale retained `acquire_transport` could be handed off before that guard.
   - R2 moved the consumption proof ahead of retained transport handoff after failed canonical V3 confirmation, while preserving genuine `ACTIVE_NEXT` and legitimate unconsumed pending retries.
   - Existing Row 13 was strengthened; Phase B remains exactly 73 rows, Rows 1..73 exactly once, no Row 74.

## Canonical lifecycle exercised

### Source acquisition / release

- Source task: `TASK-EQUIANGULAR-R18-001`
- Worker: `w-0bebfd2fd11cb67f`
- Principal: `gh:51mns`
- Original source lock M1: `b01bf39c2387d8e1f0dc4cfd60d6e1bb56b0a10d`
- Truth-neutral source terminal merged at M2: `ee5299ed8714c0b8fb0c9149cb544ef89ebbf23b`
- Canonical source RELEASE M3: `7037fb8794a043267701e46e2aaae7ea99bd808c`
- Source epoch: `730fe029ad2479bcb83f2d5ce9744f6f18578c783c2c8fa84f0d491e4d691065`

### Next acquisition

- Fresh post-release selection resolved exactly to `TASK-DITTERT-N5-001` / `GLOBAL_READY`.
- Canonical V3 ACQUIRE M4: `c861bf0aef4d98c52f0792e5761ece27d0524264`
- Canonical acquire id: `86fd3b3698155eab1c5ed4e14ba9d78aef01bf600ecbb9014e4923b57541032c`
- Dittert canonical lock blob: `042775d7a876b807dda6ed3e67102336ff5e5f8a`

## Replay failure, remediation, and production re-test

The original live replay generated unintended draft ACQUIRE PR #52 for `TASK-FIXED-433-001`, proving that the old source epoch could be reused after canonical consumption. The unintended PR remained noncanonical, was preserved as evidence during remediation, then closed without merge and its replay ref deleted only after remediation acceptance.

Cumulative R1+R2 remediation merged via PR #54. Main after remediation was:

`dd13fd15496bab9325e2520e3d1bfad3390eba2d`

The exact old-epoch replay was then executed once against production and returned:

`FAIL: OLD_ACQUISITION_REPLAY: source epoch already consumed by canonical v1.3 ACQUIRE c861bf0aef4d98c52f0792e5761ece27d0524264`

with exit code `2`.

Fresh GitHub readback after that replay showed:

- main unchanged;
- canonical Dittert lock unchanged;
- no new ACQUIRE PR;
- no new replay ref;
- no transport writes.

The normal retained state was then executed once and returned the expected idempotent result:

- `ACTIVE_NEXT`
- canonical acquire id `86fd3b3698155eab1c5ed4e14ba9d78aef01bf600ecbb9014e4923b57541032c`
- task `TASK-DITTERT-N5-001`
- exit code `0`.

Thus the repaired implementation both blocks the stale epoch and preserves the valid canonical continuation.

## Truth-neutral cleanup

Dittert was terminalised through an ordinary verified PR with:

- reason `SCOPE_STOP`;
- `abandonment_count=1`;
- `last_work_head=null`;
- `truth_layer_effect=NONE`.

Terminal merge main:

`b346ade90006d5591a52a0b55e7a9280a9a3f253`

The Dittert lock remained byte-for-byte unchanged during terminalisation.

Cleanup RELEASE was then prepared using the existing reviewed RELEASE transport primitive directly, not `/next`, so no third task could be acquired.

- PR #56: `Release TASK-DITTERT-N5-001 lock`
- RELEASE head: `c5e6b412e31a3b3be541779ca719617503139485`
- change: exact deletion of `coordination/locks/dittert-n5/broader-zero-pattern.yml` only
- Verify #136: run `33853192519`, authoritative `run_attempt=2`, completed/success
- trusted lifecycle merge: `21675e3fd8011ef9a2edf75e9de7ff6a3338ecc2`

## Final canonical state

Final main:

`21675e3fd8011ef9a2edf75e9de7ff6a3338ecc2`

Fresh readback shows:

- Dittert lock path absent;
- `coordination/locks/` contains only `README.md`;
- active field-test locks: **0**;
- truth-neutral Dittert terminal remains present;
- unintended replay PR #52 remained unmerged;
- no third `/next` acquisition was performed during cleanup.

No mathematical Truth, Claim, Review, result outcome, or failed-route semantic authority was created by the live-field cleanup. Both source and Dittert abandonment markers explicitly carry `truth_layer_effect=NONE`.

## Final result

The full source RELEASE → fresh rerank → V3 ACQUIRE → ACTIVE_NEXT lifecycle was exercised against real GitHub state, including failure injection through an actual old-epoch replay. The replay defect and its retained-transport variant are now blocked in production, normal idempotency is preserved, and all live-field locks have been cleanly released.

**FINAL_VERDICT = LIVE_FIELD_PASS_CLEAN**
