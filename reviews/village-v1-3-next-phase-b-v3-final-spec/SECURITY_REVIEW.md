# Village v1.3 Phase B V3 final independent security review

TASK-ID: `AIMATH-VILLAGE-V1-3-NEXT-PHASE-B-V3-FINAL-SECURITY-REVIEW`

Repository: `51mns/AIMath-public`

Target: `3dfefb87fad1d788bdb0ae6f58ec1c6d13ced3aa`

Target parent: `e322b021de758eccba2045471bd97eb7accd42dc`

Target spec: `reviews/village-v1-3-next-phase-b-transport-preflight/PHASE_B_FROZEN_SPEC.md`

Target blob: `037677fa3f17a2c813253faa81d67d41be9b8e52`

## Final implementation gate

**VERDICT: PASS_WITH_REQUIRED_CHANGES**

```text
PHASE_B_IMPLEMENTATION_ALLOWED = NO
```

The V3 authority model itself is coherent and closes historical H-02 without reintroducing PR-number causality or requiring the transport head SHA to survive squash. `CanonicalAcquireIdentityV3` binds authority to exact semantic primitives, base, deterministic canonical tree and exact canonical lock objects; the selected transport head remains a separate pre-merge object with its own non-transferable Verify lineage.

The mandatory semantic-authenticity challenge also passes at the design level. Sections 3–7 derive `SourceAcquisitionV1`, `ContinuationContextV1`, `SelectionV1` and `AcquireIntentV1` from canonical/fresh trusted evidence before candidate authority is considered; Section 21 then requires the candidate's persisted `next_binding` to equal those frozen expected primitives. Candidate lock bytes therefore cannot define their own expected semantic IDs.

However, the frozen **73-row implementation test contract has one blocking MEDIUM coverage gap**. No single row exactly exercises the required end-to-end attack in which a candidate supplies syntactically valid, internally self-consistent forged `next_binding` IDs, recomputes its own lock bytes/blobs/tree consistently, yet differs from independently re-derived trusted upstream records. Rows 20, 66, 67, 70 and 71 collectively constrain pieces of this problem, but none explicitly requires independent fresh upstream re-derivation and rejection of a candidate-controlled self-consistent binding, especially for `continuation_context_id` and `selection_id`.

The safest minimal contract repair is to **revise row 20 without changing the total of 73 tests**. Row 20 should be parameterized over all four primitive IDs and require:

```text
fresh canonical/release evidence
-> derive SourceAcquisitionV1/source_epoch_id
-> derive ContinuationContextV1/continuation_context_id
-> derive SelectionV1/selection_id
-> derive AcquireIntentV1/acquire_intent_id
-> only then parse candidate next_binding
-> require exact equality
```

and use an attacker fixture whose forged 64-hex binding is syntactically valid and internally consistent with its own lock bytes, Git blobs and candidate tree. Any mismatch must fail before trusted merge eligibility and must never reach `ACTIVE_NEXT`.

Because the task's PASS gate explicitly requires this negative test and classifies an implementation ambiguity requiring a contract change as blocking MEDIUM minimum, implementation remains blocked until that frozen test-row wording is repaired and independently accepted.

---

## 1. Fresh integrity gate

Fresh remote reads established:

```text
current main = 84a046359b299950403b68bfcb190930ebbc4c3f
V3 target    = 3dfefb87fad1d788bdb0ae6f58ec1c6d13ced3aa
target parent= e322b021de758eccba2045471bd97eb7accd42dc
target blob  = 037677fa3f17a2c813253faa81d67d41be9b8e52
design head  = 3dfefb87fad1d788bdb0ae6f58ec1c6d13ced3aa
```

Compare `e322b021... -> 3dfefb87...` is exactly:

```text
ahead_by  = 1
behind_by = 0
total commits = 1
changed paths = 1
+767 / -0
```

Only changed path:

```text
reviews/village-v1-3-next-phase-b-transport-preflight/PHASE_B_FROZEN_SPEC.md
```

The target commit carries the required DCO `Signed-off-by` trailer. `TARGET_MATCH = YES`; `SCOPE_MATCH = YES`; no target drift was observed before this verdict.

---

## 2. Historical finding disposition

### H-01 — CLOSED

V3 preserves V2's removal of PR number/ref and `merged`, `merged_at`, `merge_commit_sha` from post-canonical `ACTIVE_NEXT` authority. Canonical confirmation proves exact content, not which PR caused it. Indirect-merge metadata therefore cannot grant ownership.

### M-02 — CLOSED

V3 preserves V2's documented workflow lineage rule:

```text
authoritative_run_number = max(run_number among the complete exact matching set)
```

`run_id` is lookup identity only. The current attempt of the highest lineage must be fresh completed-success; older green attempts cannot override a newer failed/in-progress lineage.

### H-02 — CLOSED

V3 makes the previously unobservable transport commit SHA non-authoritative after squash. H and H2 with the same frozen base B, deterministic canonical tree T, exact lock objects and persisted semantic identity intentionally denote the same canonical acquisition content even if Git commit metadata differs. This matches what canonical Git state can actually prove after squash.

### L-01 — CLOSED

V3 explicitly requires path uniqueness before hashing:

```text
len(exact_lock_objects) == len(set(object.path for object in exact_lock_objects))
```

Duplicate paths fail `CANONICAL_ACQUIRE_DUPLICATE_LOCK_PATH`; no dedupe or last-write-wins normalization is permitted.

---

## 3. CanonicalAcquireIdentityV3 and semantic authenticity

The V3 record contains the security-relevant semantic identity and canonical Git content:

- `source_epoch_id`
- `continuation_context_id`
- `selection_id`
- `acquire_intent_id`
- `expected_base_sha`
- `expected_canonical_tree_sha`
- Task / worker / principal
- work ref / sorted collision keys
- lock id / acquisition and expiry timestamps
- exact lock paths, `100644` modes, blob OIDs and exact-byte SHA-256

It deliberately excludes transport head SHA, PR locator/merge metadata, commit message/author/committer/time and numeric `run_id` magnitude.

The canonical ID is external and non-recursive:

```text
canonical_acquire_id = SHA256(canonical(CanonicalAcquireIdentityV3))
```

`canonical_acquire_id` is not serialized into the lock bytes that are inputs to the identity.

### Independent derivation is load-bearing

The design does not permit `next_binding` to authenticate itself. The required direction is:

```text
canonical source acquisition + terminal evidence
-> SourceAcquisitionV1
-> source_epoch_id

fresh canonical continuation inputs + human gate
-> ContinuationContextV1
-> continuation_context_id

fresh post-RELEASE main/PENDING/eligibility/rank state
-> SelectionV1
-> selection_id

those frozen records
-> AcquireIntentV1
-> acquire_intent_id

expected IDs
-> serialize candidate lock next_binding
-> exact bytes/OIDs/tree
```

A malicious candidate that invents X/Y/Z/Q and makes its own bytes/tree internally consistent is ineligible because its values do not equal the independently frozen trusted records. Candidate bytes are evidence of what the candidate says, not evidence that the upstream records legitimately produced those IDs.

This semantic direction is coherent in the frozen design. The remaining defect is test-contract explicitness, not the authority definition itself.

---

## 4. Canonical bytes/tree coupling and squash transition

For each primitive semantic ID, changing the persisted value changes deterministic lock bytes; that changes `bytes_sha256`, Git blob OID and therefore the exact intended root tree T. A claim of the same exact bytes/tree with a different semantic primitive is internally contradictory and must return `CANONICAL_ACQUIRE_SEMANTIC_BINDING_INCONSISTENT`.

T is frozen independently from the candidate:

```text
Tree(B) + exact intended lock object additions only = T
```

Then any candidate H must prove `parents(H)=[B]`, `tree(H)=T` and exact B->H lock-only delta. A candidate changing an unrelated repository path cannot match precomputed T and fails.

Post-canonical proof uses the immediate first-parent child M after B and requires:

```text
parents(M) == [B]
tree(M) == T
B -> M == exact expected lock-only delta
exact objects/modes/bytes match
fresh lock payload parses exact V3 binding
M remains on current main first-parent ancestry
current exact lock remains active/unexpired
```

This proves exact canonical acquisition **content** in one permitted transition and does not claim source-PR or source-head causality. Squash therefore does not recreate H-02.

---

## 5. Schema / current implementation compatibility

Canonical `schemas/lock.schema.json` has root `additionalProperties: true`, so a `next_binding` extension does not invalidate legacy/manual lock payloads. The generic schema need not globally require it. Phase B must enforce `next_binding` as a `/next`-specific semantic requirement; a legacy/manual lock without it may remain generically valid but cannot certify v1.3 `/next ACTIVE_NEXT`.

No Ruleset weakening or global schema weakening is required. If implementation discovers a protected schema/policy change is actually needed, V3 correctly requires returning to governance/security review.

Current Phase A remains read-only and stops at `ACQUIRE_PENDING`; `ACTIVE_NEXT` is not emitted by the pure core. Current trusted lifecycle retains RELEASE > ACQUIRE, candidate-local malformed isolation, global fail-closed prerequisite handling, and one canonical lifecycle mutation per trusted run. V3 does not move Task selection, ranking, Truth or review authority into `lock_auto_activate.py`.

The current production Verify helper still reflects pre-Phase-B numeric-run-ID behaviour; that is not accepted as the Phase B implementation. M-02 explicitly requires the Phase B implementation to replace that observation semantics with complete `run_number` lineage logic.

---

## 6. Effective Ruleset gate

Fresh Ruleset read:

```text
name = Village main strict lifecycle safety
enforcement = active
target = branch
include = ~DEFAULT_BRANCH
required status context = verify
strict_required_status_checks_policy = true
bypass_actors = []
current_user_can_bypass = never
```

`RULESET_GATE = PASS`.

---

## 7. Preregistered 73-row matrix audit

Each frozen row was reviewed exactly once below. `PASS` means the row states an appropriate required regression. `GAP` means wording is insufficient for the mandatory threat contract.

| Row | Review |
|---:|---|
| 1 | PASS — positive full source/release/fresh-selection/acquire/canonical-readback path. |
| 2 | PASS — unrelated same worker/principal lock cannot grant. |
| 3 | PASS — old acquisition epoch / lock identity cannot grant. |
| 4 | PASS — wrong work ref rejected. |
| 5 | PASS — wrong collision bundle rejected. |
| 6 | PASS — wrong worker rejected. |
| 7 | PASS — wrong principal rejected. |
| 8 | PASS — stale ACQUIRE base rejected. |
| 9 | PASS — stale RELEASE base requires bounded same-epoch repair/new CI. |
| 10 | PASS — moved PR head invalidates old Verify/transport. |
| 11 | PASS — duplicate `/next` is idempotent, not authority duplication. |
| 12 | PASS — creator race adopts exact winner, no overwrite. |
| 13 | PASS — old source epoch replay after reacquisition stops. |
| 14 | PASS — equivalent RELEASE reuse. |
| 15 | PASS — unrelated RELEASE ref/PR conflicts. |
| 16 | PASS — already released state needs exact source-epoch provenance and fresh main. |
| 17 | PASS — equivalent ACQUIRE reuse. |
| 18 | PASS — deterministic ACQUIRE ref without PR creates at most one. |
| 19 | PASS — revised exact V3 canonical transition, not PR merged metadata, grants. |
| 20 | **GAP** — revised wrong-V3-identity case is too generic; it does not explicitly require the syntactically valid, internally self-consistent forged-binding attack to be checked against independently re-derived upstream IDs. |
| 21 | PASS — later current lock change invalidates old current authority. |
| 22 | PASS — two-worker canonical winner only. |
| 23 | PASS — collision bundle winner only. |
| 24 | PASS — Campaign capacity race. |
| 25 | PASS — global capacity race. |
| 26 | PASS — RELEASE priority preserved. |
| 27 | PASS — at most one canonical lifecycle mutation. |
| 28 | PASS — Ruleset observation unavailable/malformed fails closed. |
| 29 | PASS — strict=false or verify missing fails closed. |
| 30 | PASS — exact-head CI red/missing rejects. |
| 31 | PASS — moved head cannot reuse older green CI. |
| 32 | PASS — malformed candidate-local observation isolates candidate. |
| 33 | PASS — repository-wide prerequisite failure is globally closed. |
| 34 | PASS — disappeared candidate is dropped/re-ranked. |
| 35 | PASS — main movement after RELEASE invalidates old selection snapshot. |
| 36 | PASS — main movement after selection recomputes before branch creation. |
| 37 | PASS — stale base after ACQUIRE PR creation cannot own. |
| 38 | PASS — PENDING remains non-ownership. |
| 39 | PASS — terminal/release does not Truth-promote pending review. |
| 40 | PASS — no autonomous I2/I3 or self-review promotion. |
| 41 | PASS — no automatic RENEW/TAKEOVER. |
| 42 | PASS — missing human continuation gate cannot escalate same Campaign. |
| 43 | PASS — worker recommendation cannot create/approve governance objects. |
| 44 | PASS — continuation/selection inputs changing recomputes selection identity. |
| 45 | PASS — terminal blob mutation invalidates source epoch reuse. |
| 46 | PASS — changed source lock blob bundle blocks old RELEASE authority. |
| 47 | PASS — deterministic lock ID stability/distinctness. |
| 48 | PASS — first creator timestamp frozen and reused. |
| 49 | PASS — canonical lock path/blob readback exact. |
| 50 | PASS — expired readback never ACTIVE_NEXT. |
| 51 | PASS — V3 same-content H/H2 equivalence is explicit and metadata-only differences are non-semantic. |
| 52 | PASS — stale webhook/workflow delivery is trigger-only. |
| 53 | PASS — multiple RELEASE ordering + malformed lower candidate isolation. |
| 54 | PASS — multiple ACQUIRE ordering + malformed lower candidate isolation. |
| 55 | PASS — highest documented run_number lineage controls. |
| 56 | PASS — indirect merge / multi-parent shape cannot grant. |
| 57 | PASS — alternate locator is non-authoritative; exact canonical content transition controls. |
| 58 | PASS — rerun of older lineage cannot outrank newer failure. |
| 59 | PASS — genuinely higher successful lineage can recover. |
| 60 | PASS — currently rerunning/in-progress highest lineage cannot use stale success. |
| 61 | PASS — incomplete/ambiguous/multi-parent/multi-step canonical history rejects. |
| 62 | PASS — Ruleset bypass/unreadable rejects. |
| 63 | PASS — H2 cannot borrow H Verify. |
| 64 | PASS — different/stale base alternate head rejects. |
| 65 | PASS — same base but different tree/object rejects. |
| 66 | PASS but partial for M-03 — process/observation source-epoch mismatch is rejected; does not by itself prove fresh trusted upstream re-derivation. |
| 67 | PASS but partial for M-03 — acquire-intent mismatch is rejected; does not cover continuation/selection or end-to-end candidate self-authentication. |
| 68 | PASS — positive squash H != M control. |
| 69 | PASS — duplicate path fail-closed before hashing. |
| 70 | PASS but orthogonal to M-03 — source/continuation/selection mutation must alter bytes/OID/tree. |
| 71 | PASS but orthogonal to M-03 — acquire-intent mutation must alter bytes/OID/tree. |
| 72 | PASS — post-squash identity reconstructed from canonical bytes without process memory. |
| 73 | PASS — missing required `/next` binding fails while legacy compatibility remains. |

### Required row-20 repair

Keep total `73`. Replace/strengthen row 20 with an explicit parameterized negative fixture equivalent to:

> Independently fresh-derive expected `source_epoch_id`, `continuation_context_id`, `selection_id`, and `acquire_intent_id` from the authoritative source/release/continuation/post-RELEASE-selection records **before trusting candidate binding**. Construct a candidate whose `next_binding` contains syntactically valid forged 64-hex values, whose lock bytes/blob OIDs/tree are internally recomputed and self-consistent, and whose Task/worker/principal/base/path shape otherwise looks valid. For each primitive ID mutation, exact comparison with the independently derived expected record must make the candidate pre-merge ineligible and must never yield `ACTIVE_NEXT`.

This directly covers the required threat 29 and closes the implementation ambiguity without increasing the test total.

---

## 8. Mandatory threat-model results

1. **PASS** — H/H2 same B/T/content, metadata-only difference: same canonical acquisition content.
2. **PASS** — H2 cannot borrow H's Verify; exact chosen H2 needs its own current authoritative lineage.
3. **PASS** — forged `source_epoch_id` in valid lock bytes is rejected against independently derived expected source epoch by the design; matrix needs M-03 explicit end-to-end fixture.
4. **PASS** — forged `acquire_intent_id` similarly rejected; matrix needs M-03 explicit end-to-end fixture.
5. **PASS** — missing `next_binding` is not `/next ACTIVE_NEXT`.
6. **PASS** — inconsistent binding across collision bundle fails closed.
7. **PASS** — different base, same-looking lock, is non-equivalent.
8. **PASS** — different tree/object content is non-equivalent.
9. **PASS** — duplicate lock object path fails before hashing.
10. **PASS** — unrelated repo file changes cannot match precomputed T / exact delta.
11. **PASS** — a claimed source epoch that never existed cannot be derived from canonical source acquisition evidence; `SOURCE_EPOCH_UNPROVEN`.
12. **PASS** — stale old source epoch after newer reacquisition is replay and stops.
13. **PASS** — human Continuation Gate denying continuation constrains independent ContinuationContext/selection; candidate binding cannot override it.
14. **PASS** — global `PAUSED` disables eligible continuation/selection; candidate binding cannot declare authority.
15. **PASS** — stale selection after main or relevant state movement loses authority and is recomputed.
16. **PASS** — older green/newer failed `run_number` lineage: newer failure controls.
17. **PASS** — highest lineage currently rerunning/in-progress is not eligible.
18. **PASS** — incomplete workflow pagination/result envelope fails closed.
19. **PASS** — indirect merge marking expected PR merged is non-authoritative; canonical shape/content controls.
20. **PASS** — multi-parent canonical merge fails exact single-parent transition.
21. **PASS** — multi-step canonicalisation fails exact immediate B->M single transition.
22. **PASS** — exact permitted squash transition H != M with B/T/content exact may confirm.
23. **PASS** — later lock renewal/current bytes change invalidates old current acquisition identity.
24. **PASS** — later release/reacquire changes current identity and old acquisition cannot certify ownership.
25. **PASS** — current active lock differing by one semantic ID changes bytes/OID/tree and mismatches old V3 identity.
26. **PASS** — Ruleset unreadable, bypass actor or bypass-capable user fails closed.
27. **PASS** — main moves before merge invalidates stale base and requires fresh derivation/revalidation.
28. **PASS** — main may advance after canonical acquisition only if M remains first-parent ancestral and current exact semantic lock is unchanged/active; otherwise old ACTIVE_NEXT proof fails.
29. **HOLE IN TEST CONTRACT, SAFE IN DESIGN** — an internally self-consistent candidate-controlled forged `next_binding` is rejected by the semantic derivation rules, but the 73-row matrix lacks one exact end-to-end regression requiring independent upstream re-derivation before candidate equality. This is blocking M-03 until row 20 is strengthened.

---

## 9. Findings

### CRITICAL

None.

### HIGH

None. In particular, no candidate-controlled semantic ID becomes self-authenticating under the frozen authority definition, and no canonical acquisition substitution remains once exact head SHA is removed from post-canonical identity.

### MEDIUM

#### M-03 — blocking — forged self-consistent `next_binding` negative test is not explicit

The design text is safe, but the implementation contract is incomplete under the task's explicit acceptance rule. The test matrix must prove that expected semantic IDs are independently re-derived from trusted authoritative inputs, not taken from candidate bytes, and must reject a fully internally consistent forged candidate. Existing rows are not an exact substitute:

- row 20 says wrong persisted V3 semantic identity, but not how the expected identity is obtained;
- rows 66–67 compare candidate/canonical bytes with another claim but cover only source epoch/acquire intent and can be implemented against process copies without proving upstream derivation;
- rows 70–71 prove bytes/tree coupling, not semantic authenticity.

**Required change:** strengthen row 20 as specified above, parameterized across all four IDs, while retaining total 73. No production authority change is required.

### LOW

None blocking. Historical L-01 is explicitly closed.

---

## 10. Final status

```text
CURRENT_MAIN: 84a046359b299950403b68bfcb190930ebbc4c3f
TARGET: 3dfefb87fad1d788bdb0ae6f58ec1c6d13ced3aa
TARGET_MATCH: YES
TARGET_PARENT: e322b021de758eccba2045471bd97eb7accd42dc
TARGET_BLOB: 037677fa3f17a2c813253faa81d67d41be9b8e52
SCOPE_MATCH: YES

H01: CLOSED
M02: CLOSED
H02: CLOSED
L01: CLOSED

CANONICAL_ACQUIRE_IDENTITY_V3: PASS
HEAD_SHA_POST_CANONICAL_AUTHORITY: REMOVED
NEXT_BINDING_CANONICAL: PASS
NEXT_BINDING_INDEPENDENT_DERIVATION: PASS
NEXT_BINDING_SELF_AUTHENTICATION: SAFE
SOURCE_EPOCH_PROVENANCE: PASS
CONTINUATION_AUTHENTICITY: PASS
SELECTION_AUTHENTICITY: PASS
ACQUIRE_INTENT_AUTHENTICITY: PASS
H_H2_EQUIVALENCE: PASS
TRANSPORT_VERIFY_SEPARATION: PASS
EXPECTED_TREE_DERIVATION: PASS
CANONICAL_TRANSITION: PASS
SQUASH_COMPATIBILITY: PASS
DUPLICATE_LOCK_PATH: PASS
COLLISION_BUNDLE_BINDING: PASS
RUN_NUMBER_POLICY: PASS
WORKFLOW_PAGINATION: PASS
RULESET_GATE: PASS
PHASE_A_BOUNDARY: PASS
PREREGISTERED_73_TESTS: FAIL

CRITICAL: 0
HIGH: 0
MEDIUM: 1 blocking (M-03)
LOW: 0 open

VERDICT: PASS_WITH_REQUIRED_CHANGES
PHASE_B_IMPLEMENTATION_ALLOWED: NO
```

Do not implement Phase B from this review target. Return to the Village coordinator, revise only the frozen test-contract wording needed to close M-03, then run a focused independent rereview of that exact amended commit/blob.