# Village source-epoch consumption R2 independent review

Task: `AIMATH-VILLAGE-V1-3-SOURCE-EPOCH-CONSUMPTION-R2-INDEPENDENT-REVIEW`

## Verdict

**PASS — REMEDIATION_ACCEPTED**

No unresolved CRITICAL, HIGH, or MEDIUM finding remains in the reviewed cumulative R1+R2 scope. PR #54 is ready for merge from this review's technical perspective, but this review does not merge it.

## Fixed points

- Fresh `main`: `c861bf0aef4d98c52f0792e5761ece27d0524264` (`PRESERVED_M4`).
- Target: `8c5c7b6b7272d2cd22d8fda26f73dc905635d187`.
- Target parent: `ba307883dd74afced832ac8673c78c78b90e86f4` (R1 target).
- M4 -> target: 2 commits ahead, 0 behind.
- Changed files only:
  - `scripts/village_next_phase_b.py`
  - `scripts/test_village_v1_3_next_phase_b.py`
- Target production blob: `9aa52123cfd95f06189bfd56c55c07a5a70da827`.
- Target test blob: `861451d1b44b53487eb6bc45fdbf792c8464d3d4`.
- Both M4->target commits contain `Signed-off-by` trailers; exact-head Verify #132 also passed the repository DCO step.

## Cumulative R1+R2 production review

The R1 source-epoch consumption proof is retained and the R2 ordering closes the residual retained-transport bypass.

For retained `canonical_acquire_identity_v3`:

1. `_confirm_retained_acquire` runs first.
2. A genuine canonical confirmation still returns `ACTIVE_NEXT` directly.
3. If confirmation fails, `_prove_retained_release` runs before transport authority.
4. The retained `source_epoch_id` and RELEASE base are validated.
5. `_source_epoch_consumption_gate` runs before inspecting or handing off `acquire_transport`.
6. A proven prior canonical V3 ACQUIRE of the same source epoch returns `OLD_ACQUISITION_REPLAY`.
7. `_transport_handoff` is reachable only when that source epoch is proven unconsumed.

For the normal no-retained-V3 post-RELEASE path, `_source_epoch_consumption_gate` remains before `_pending_records_from_open_acquire_prs`, post-release derivation/rerank, and `_prepare_acquire_transport`.

Therefore every reviewed stale source-epoch path capable of retained handoff, PENDING authority, rerank, or new ACQUIRE preparation is gated before mutation/authority.

## Canonical history proof

`_first_parent_history` is bounded to 512 transitions, rejects cycles, and fails closed unless the requested stop SHA is reached through first parents.

`_source_epoch_consumption_gate` reads only canonical first-parent tree transitions. It does not use an open/draft PR as consumption authority. An added lock counts only after exact V3 parsing and matching `source_epoch_id`; unrelated locks and unrelated source epochs are ignored. Once the source epoch matches, malformed or non-exact deterministic V3 material, non-single-parent shape, wrong delta/tree/object/bytes, or unprovable history fail closed as `CANONICAL_ACQUIRE_HISTORY_UNPROVEN` rather than being treated as unconsumed.

This also means PR #52 itself, while open/draft/noncanonical, cannot establish canonical source-epoch consumption.

## Row 13 residual-HIGH oracle

Row 13 genuinely models the R1 residual HIGH:

- retained V3 semantic state exists;
- canonical confirmation cannot grant `ACTIVE_NEXT` to the stale alternate identity;
- an exact open draft retained acquire transport is present;
- at consumed M4 the result is `OLD_ACQUISITION_REPLAY` before `_transport_handoff`;
- after later canonical cleanup the same old source epoch is still rejected;
- `_transport_handoff`, PENDING observation, rerank, and `_prepare_acquire_transport` are all asserted not called;
- transport/GitHub writes are asserted zero.

The same Row 13 also includes the required non-regression case at M3: with the source epoch still unconsumed, a legitimate retained pending transport reaches `_transport_handoff` exactly once.

## Test and CI evidence

The target test source enforces exactly 73 Phase B test methods and an exact `SPEC_ROW_TO_TEST` key set `1..73`; the mapped test names are unique. No Row 74 exists.

Exact-head GitHub Actions Verify #132:

- run id: `33848696838`
- workflow id: `347191396`
- job id: `100946330070`
- head SHA: `8c5c7b6b7272d2cd22d8fda26f73dc905635d187`
- result: `completed / success`

The successful job includes the DCO step and Village Phase B acceptance tests on the exact target head.

## Authority boundary

The cumulative two-commit diff changes only the production Phase B implementation and its tests. It does not add Truth or Review authority, does not add Claim-promotion authority, and does not broaden RELEASE or ACQUIRE authority. The R2 change narrows retained ACQUIRE transport retry authority by requiring canonical proof that the source epoch is still unconsumed before handoff.

## Repository state checked during review

- PR #54: OPEN, non-draft, UNMERGED; base preserved M4; head exact target.
- PR #52: OPEN, DRAFT, UNMERGED; head `a178b69e9c6229e5cc1da7d7bcbb3646fa6138e2`.
- PR #53: OPEN, non-draft, UNMERGED; head `ba307883dd74afced832ac8673c78c78b90e86f4`.
- M4 Dittert lock blob: `042775d7a876b807dda6ed3e67102336ff5e5f8a`.

No merge, main update, PR #52/#53 mutation, replay-ref deletion, or M4 lock mutation is part of this review.

## Findings

- CRITICAL: 0
- HIGH: 0
- MEDIUM: 0
- LOW: 0

`REMEDIATION_ACCEPTED=YES`

`PR54_READY_FOR_MERGE=YES` (review conclusion only; PR #54 remains unmerged by this review)
