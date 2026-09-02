# Village v1.3 `/next` live field-test V3 compatibility supplement

TASK-ID: `AIMATH-VILLAGE-V1-3-NEXT-LIVE-FIELD-TEST-V3-COMPAT`

Status: **READY_AFTER_PHASE_B_MERGE**

Repository: `51mns/AIMath-public`

This document is a review-only supplement to the already accepted live field-test plan. It does not replace, edit, or weaken that plan. It defines the additional evidence that an eventual real live test must collect to validate the final accepted Village v1.3 Phase B V3 canonical acquisition identity.

No live test, lock, lifecycle PR, production mutation, repository setting change, secret change, claim, review promotion, outcome, or Truth Layer mutation is performed by this review lane.

## 1. Fixed authority inputs

The supplement is bound to these exact accepted inputs:

```text
CURRENT_MAIN_AT_COMPAT_REVIEW = 84a046359b299950403b68bfcb190930ebbc4c3f

HISTORICAL_LIVE_PLAN_COMMIT   = 705bd7c5250103e74118381106d422d50c677bb7
HISTORICAL_LIVE_PLAN_PATH     = reviews/village-v1-3-next-live-field-test-preflight/FIELD_TEST_PLAN.md
HISTORICAL_LIVE_PLAN_BLOB     = 05848a5d2998e42e5e02443f331194c61486f3b6

HISTORICAL_PLAN_REVIEW        = beccfe018018c6502fe975430d87a019b766ac60
HISTORICAL_PLAN_VERDICT       = PASS

FINAL_V3_PHASE_B_SPEC         = a482d1f4398489753589afe1ef3ed5e593a7e9c4
FINAL_V3_PHASE_B_SPEC_PATH    = reviews/village-v1-3-next-phase-b-transport-preflight/PHASE_B_FROZEN_SPEC.md
FINAL_V3_PHASE_B_SPEC_BLOB    = 2ddc79843cf44bd588dc1a5ff89e996ecd246de9

FINAL_V3_ACCEPTANCE           = 3c1be65016eda44f5efe849a6e2c2db273847db2
FINAL_V3_ACCEPTANCE_VERDICT   = PASS
PHASE_B_IMPLEMENTATION_ALLOWED= YES
```

The final accepted V3 spec is a design/security authority input. The eventual live execution still MUST wait until a matching independently reviewed Phase B implementation is merged to `main` and freshly revalidated. This supplement does not treat an unmerged design branch as production authority.

## 2. Historical substrate is preserved exactly

The accepted field-test substrate remains unchanged:

```text
principal_id = gh:51mns
worker_id    = w-0bebfd2fd11cb67f
wrong_worker = w-e8912c097a3288e1

SOURCE_TASK       = TASK-EQUIANGULAR-R18-001
SOURCE_CAMPAIGN   = CAM-EQUIANGULAR-R18
SOURCE_COLLISION  = eq18/general-structural-obstruction
SOURCE_LOCK_PATH  = coordination/locks/eq18/general-structural-obstruction.yml
SOURCE_WORK_REF   = research/TASK-EQUIANGULAR-R18-001/w-0bebfd2fd11cb67f
SOURCE_LOCK_ID    = LOCK-FIELDTEST-EQUIANGULAR-R18-001-0BEBFD2FD11CB67F

SOURCE_TERMINAL_CLASS = ABANDONED_TERMINAL
SOURCE_TERMINAL_REASON= SCOPE_STOP
TRUTH_LAYER_EFFECT    = NONE

EXPECTED_NEXT_TASK       = TASK-DITTERT-N5-001
EXPECTED_NEXT_CAMPAIGN   = CAM-DITTERT-N5
EXPECTED_NEXT_RELATION   = GLOBAL_READY
EXPECTED_NEXT_COLLISION  = dittert-n5/broader-zero-pattern
EXPECTED_NEXT_LOCK_PATH  = coordination/locks/dittert-n5/broader-zero-pattern.yml
EXPECTED_NEXT_WORK_REF   = research/TASK-DITTERT-N5-001/w-0bebfd2fd11cb67f
```

The accepted high-level lifecycle remains:

```text
M0 clean accepted Phase B main
M1 source ACQUIRE canonical main
M2 truth-neutral terminal canonical main
M3 trusted source RELEASE canonical main
M4 trusted expected-next ACQUIRE canonical main -> ACTIVE_NEXT proof
```

The historical wrong-worker, duplicate/reuse, old-source-epoch replay, no-Truth/no-claim sentinels, fresh post-RELEASE reranking, and truth-neutral cleanup strategy remain mandatory.

At compatibility-review main `84a046...`, both frozen Tasks still exist as approved EXCLUSIVE RESEARCH Tasks with their exact historical collision keys and 168-hour leases; the canonical lock directory contains no active lock file. Therefore no compatibility-time substrate drift was found.

If any of these frozen identities or semantics differs at actual live-test Phase 0, report `PRECONDITION_DRIFT` and abort. Do not substitute another Task, worker, principal, terminal form, collision bundle, or expected-next Task.

## 3. V3 supersession rule for the historical M4 evidence

The historical plan remains valid except where its M4 evidence language is weaker than V3.

For V3, a merged PR, PR number, PR ref, merge metadata, transport commit identity, or a same-Task/same-worker lock is never sufficient post-canonical evidence for `ACTIVE_NEXT`.

The eventual test MUST distinguish:

```text
H = selected PRE-MERGE transport candidate head
B = expected canonical base
T = expected canonical full-tree SHA
M = exact canonical acquisition transition commit after trusted squash/canonicalisation
C = fresh current main used for ACTIVE_NEXT confirmation
```

`H` remains security-relevant before merge. `M` and current canonical Git content are the post-merge authority-bearing evidence. `H` MAY differ from `M` under accepted squash semantics.

## 4. Trusted semantic derivation and persisted `next_binding`

Before parsing a candidate next-lock bundle as authority-bearing evidence, the execution ledger MUST independently derive and freeze these four records from fresh trusted upstream evidence:

```text
SourceAcquisitionV1
ContinuationContextV1
SelectionV1
AcquireIntentV1
```

Then freeze:

```text
source_epoch_id         = SHA256(canonical(SourceAcquisitionV1))
continuation_context_id = SHA256(canonical(ContinuationContextV1))
selection_id            = SHA256(canonical(SelectionV1))
acquire_intent_id       = SHA256(canonical(AcquireIntentV1))
```

The expected derivation MUST NOT use values first read from the candidate `next_binding`. Candidate values are observations to compare against independently derived expected values, never inputs that may self-authenticate.

Every lock object created specifically by v1.3 `/next` MUST persist this exact semantic binding identically in every collision-key lock object:

```json
"next_binding": {
  "schema_version": 1,
  "source_epoch_id": "<64 lowercase hex>",
  "continuation_context_id": "<64 lowercase hex>",
  "selection_id": "<64 lowercase hex>",
  "acquire_intent_id": "<64 lowercase hex>"
}
```

For this preregistered one-key expected-next bundle, the persisted object must occur in the exact lock bytes at:

```text
coordination/locks/dittert-n5/broader-zero-pattern.yml
```

Missing, malformed, nonidentical, or independently inconsistent `next_binding` is an immediate abort and cannot yield `ACTIVE_NEXT`.

The execution evidence MUST save both:

1. the independently derived canonical JSON inputs and their four expected digests; and
2. the four values freshly parsed from exact candidate/canonical lock bytes.

Exact equality is mandatory.

`canonical_acquire_id` itself MUST NOT be persisted inside the lock bytes. It is computed only after the semantic primitives, lock bytes, object identities, and expected tree are frozen.

## 5. Freeze expected base `B`, exact lock objects, and canonical tree `T`

At the post-RELEASE selection boundary, freeze:

```text
B = SelectionV1.selection_main_sha
```

and require the exact expected next-lock payload to contain:

```text
base_main_sha == B
```

After the four semantic IDs are derived, the expected deterministic next-lock payload is serialized, including exact `next_binding`. Then freeze its exact bytes and define the complete V3 object set:

```text
exact_lock_objects = [
  {
    "path": "coordination/locks/dittert-n5/broader-zero-pattern.yml",
    "mode": "100644",
    "blob_sha": "<exact 40-hex Git blob OID>",
    "bytes_sha256": "<SHA-256 of exact lock bytes>"
  }
]
```

General V3 requirements still apply even though this field-test bundle has one member:

- path set equals the complete frozen collision bundle exactly;
- paths are unique before hashing;
- list is sorted lexicographically by path;
- every object is a regular `100644` blob;
- blob OID and exact byte SHA-256 both match;
- every lock copy parses to the same lock ID, semantic fields and `next_binding`;
- path-derived collision set, Task collision bundle, and lock payload collision set are exactly equal.

Using the exact full repository tree at `B`, deterministically apply only those frozen lock additions and no other mutation. Freeze the resulting root tree SHA as:

```text
T = expected_canonical_tree_sha
```

`T` MUST be computed from `Tree(B) + exact_lock_objects`. It MUST NOT be learned by trusting whichever candidate head later appears.

The execution ledger MUST preserve the exact base commit/tree response, the deterministic tree-construction inputs, the resulting `T`, and all exact lock bytes/OIDs/hashes needed to independently recompute `T`.

## 6. Freeze `CanonicalAcquireIdentityV3`

Only after Section 5 is frozen, construct exactly:

```text
CanonicalAcquireIdentityV3 = {
  "schema_version": 3,

  "source_epoch_id": ...,
  "continuation_context_id": ...,
  "selection_id": ...,
  "acquire_intent_id": ...,

  "expected_base_sha": B,
  "expected_canonical_tree_sha": T,

  "selected_task_id": "TASK-DITTERT-N5-001",
  "worker_id": "w-0bebfd2fd11cb67f",
  "principal_id": "gh:51mns",

  "work_ref": "research/TASK-DITTERT-N5-001/w-0bebfd2fd11cb67f",
  "sorted_collision_keys": ["dittert-n5/broader-zero-pattern"],

  "lock_id": "LOCK-NEXT-<first 32 uppercase hex characters of acquire_intent_id>",
  "acquired_at": ...,
  "expires_at": ...,

  "exact_lock_objects": [...]
}
```

Then compute and save:

```text
canonical_acquire_id = SHA256(canonical(CanonicalAcquireIdentityV3))
```

The canonical JSON bytes used for the digest and their SHA-256 MUST be saved so a later reviewer can recompute the ID without relying on process memory.

The V3 identity MUST NOT contain or derive authority from:

```text
transport head SHA
PR number
PR ref
merged / merged_at
merge_commit_sha as PR metadata
commit message
commit author/committer/timestamp
webhook/event delivery identity
workflow run_id magnitude
```

## 7. PRE-MERGE transport candidate `H` evidence

The selected ACQUIRE transport candidate MUST be logged separately as `TransportCandidateV3` and MUST include at least:

```text
repository = 51mns/AIMath-public
pr_number
head_ref
head_sha = H
head_tree_sha
base_sha

verify.workflow_id = 347191396
verify.workflow_path = .github/workflows/verify.yml
verify.workflow_name = Verify public release
verify.event = pull_request
verify.head_sha = H
verify.authoritative_run_number
verify.run_id                 # lookup identity only
verify.current_run_attempt
verify.status
verify.conclusion
```

Fresh pre-merge evidence for exact `H` MUST prove:

```text
parents(H) == [B]
tree(H) == T
compare B -> H changes exactly exact_lock_objects.path
```

and every expected path at `H` has the frozen mode, blob OID and bytes SHA-256 and parses to the exact frozen V3 semantics including `next_binding`.

### Verify lineage

The test MUST save the complete, pagination-proven matching workflow-run set for the exact accepted workflow identity and exact `head_sha=H`.

The authoritative lineage is chosen by documented `run_number`, not numeric `run_id` order:

```text
authoritative_run_number = max(run_number among the complete exact-workflow/exact-head matching set)
```

The authoritative current run attempt itself must be completed successfully under the accepted V2 policy. A lower/older successful run does not override a higher matching failed/current-nonsuccess lineage. Numeric `run_id` magnitude is never chronology or authority.

If workflow observation is incomplete, truncated, malformed, pagination/result-cap completeness is unproven, workflow identity is ambiguous, or the authoritative higher lineage is failed/non-success, abort before trusted merge.

No successful Verify on `H` is transferable to another head `H2`, even if `tree(H2) == T`.

## 8. H/H2 same-content semantics

Freeze the accepted V3 meaning:

If:

```text
H != H2
parents(H)  == [B]
parents(H2) == [B]
tree(H)  == T
tree(H2) == T
same exact_lock_objects
same exact persisted V3 semantic identity including next_binding
```

then `H` and `H2` are different transport commits representing the **same canonical acquisition content**. Commit message, author, committer, timestamp, PR locator and ref metadata do not make the post-canonical acquisition different.

However, whichever head is actually selected for trusted merge MUST independently satisfy every pre-merge gate and possess its own authoritative current successful Verify lineage.

Different base, different tree, any different lock path/mode/OID/hash, or any different authority-bearing semantic field makes the candidate non-equivalent/ineligible.

## 9. POST-SQUASH canonical transition `M` evidence

After trusted ACQUIRE canonicalises and before accepting `ACTIVE_NEXT`, discard PR-merge metadata as grant authority and perform a fresh GitHub canonical read-back.

Let:

```text
C = fresh refs/heads/main
```

The test MUST save enough fresh commit objects to prove:

1. `C` descends from `B`;
2. following parent index 0 from `C` toward `B` is complete and unambiguous;
3. `M` is the unique child of `B` on that observed first-parent path;
4. exactly:

```text
parents(M) == [B]
```

A multi-parent merge, unrelated intervening first-parent commit, multi-step canonical transition, missing/partial ancestry, or ambiguous parent data is an abort.

Then prove exactly:

```text
tree(M) == T
compare B -> M changes exactly exact_lock_objects.path and no other path
```

At `M`, every expected lock path MUST have exact mode `100644`, exact frozen blob OID, and exact frozen byte SHA-256. Freshly fetch the exact lock bytes and parse all payloads; the V3 semantic payload and `next_binding` must equal the independently frozen expected identity exactly.

This proves the exact V3 acquisition content became canonical in one permitted transition. It deliberately does not prove which PR or transport commit created `M`.

For accepted squash semantics, this positive shape is expected and valid:

```text
H != M
parents(H) == [B]
parents(M) == [B]
tree(H) == tree(M) == T
```

## 10. Current-main persistence and fresh active-lock proof

`ACTIVE_NEXT` also requires the acquisition to remain current, not merely to have existed historically.

At the exact M4 confirmation observation, save fresh evidence that:

- `M` remains on current `C` first-parent ancestry;
- current main contains exactly the frozen V3 lock object bundle at the expected paths;
- current lock bytes/OIDs/hashes still equal `exact_lock_objects`;
- the four semantic IDs are reconstructed from current canonical `next_binding`, not process memory;
- all other V3 fields reconstruct exactly;
- the canonical bundle is active and unexpired at the recorded observation time;
- no renewal, replacement, release/reacquire, changed timestamp, changed binding, changed collision bundle, changed bytes, or changed object identity occurred after acquisition.

A current same-Task/same-worker lock with changed bytes is not evidence for the original V3 acquisition.

## 11. Mandatory fresh Ruleset proof

At the final M4 confirmation boundary, fresh effective Ruleset evidence MUST positively prove:

```text
enforcement = active
target applies to ~DEFAULT_BRANCH
required status context includes "verify"
strict_required_status_checks_policy = true
bypass_actors = []
current_user_can_bypass = "never"
```

The complete raw Ruleset observation and the observed Ruleset ID must be saved.

Ruleset unavailable, malformed, contradictory, weakened, changed so the gate no longer holds, any bypass actor, or `current_user_can_bypass != never` is an immediate abort. The live test MUST NOT change settings to make the gate pass.

Compatibility-review observation only: Ruleset `22089746` currently satisfies these conditions. The actual live test MUST fresh-read it again and must not reuse this review-time observation as execution authority.

## 12. V3 live abort observations

Do not manufacture malicious live state. Instead, freeze the following as immediate fail-closed conditions if any is naturally observed at a live boundary:

```text
A01 missing next_binding
A02 malformed next_binding or any required child missing/non-64-lowercase-hex
A03 candidate/canonical semantic IDs differ from independently derived trusted X/Y/Z/Q
A04 same exact bytes/tree are claimed with different semantic IDs
A05 unexpected candidate or canonical tree != T
A06 any extra changed path outside exact_lock_objects.path
A07 missing/duplicate lock path or incomplete collision bundle
A08 wrong/non-100644 mode
A09 wrong blob OID or wrong exact-byte SHA-256
A10 wrong expected base; base != B or lock base_main_sha != B
A11 candidate parent shape != [B]
A12 incomplete/truncated/malformed/ambiguous Verify workflow observation
A13 authoritative higher run_number lineage is failed/non-success
A14 selected head attempts to borrow Verify from another same-tree head
A15 Ruleset drift/weakening/unavailable/bypass
A16 current first-parent history incomplete or ambiguous
A17 M is multi-parent, not the unique single child of B, or acquisition spans multiple canonical transitions
A18 tree(M) != T or B->M delta is not exact lock-only delta
A19 current lock changed after acquisition (renewal/replacement/reacquire/bytes/timestamps/binding/collision/object)
A20 current lock not active or expired
A21 preregistered Task/worker/principal/collision/selection substrate drift
```

The fail-closed result may use the implementation's accepted machine-readable code family, including the V3 `CANONICAL_ACQUIRE_*`, Verify-lineage, `CANONICAL_LOCK_NOT_ACTIVE`, and Ruleset failure codes. The evidence bundle must record the first violated invariant and stop further field-test mutation rather than repairing the preregistered run.

## 13. Exact M4 `ACTIVE_NEXT` evidence bundle

Before the field-test run may be reported as M4 `ACTIVE_NEXT`, freeze a local/noncanonical audit bundle containing at least all historical-plan evidence plus the following V3 additions.

### 13.1 Trusted semantic inputs

Save canonical JSON serializations and digests for:

```text
SourceAcquisitionV1 + source_epoch_id
ContinuationContextV1 + continuation_context_id
SelectionV1 + selection_id
AcquireIntentV1 + acquire_intent_id
```

Also save the fresh upstream GitHub/canonical observations from which those records were independently derived, including the exact post-RELEASE `selection_main_sha`, complete validated PENDING observation digest inputs, hard-eligible list, deterministic ranked list, selected Task/relation, capability profile, applicable continuation decision/gate evidence, exact source terminal blob, and exact source RELEASE provenance.

### 13.2 Expected canonical acquisition material

Save:

```text
B = expected_base_sha
Tree(B) root SHA and exact base commit metadata needed for reconstruction
exact expected next-lock bytes
SHA-256 of each exact lock byte string
Git blob OID of each exact lock byte string
complete unique sorted exact_lock_objects
T = expected_canonical_tree_sha
CanonicalAcquireIdentityV3 canonical JSON bytes
canonical_acquire_id
```

### 13.3 Transport evidence

Save:

```text
TransportCandidateV3
H commit object and parent list
H tree SHA
exact B->H compare/path delta
candidate lock blobs and fetched exact bytes
PR number/ref as locator-only audit metadata
complete exact-head Verify matching run set
selected authoritative run_number/current run_attempt/status/conclusion
raw/paginated workflow observation metadata proving completeness
```

### 13.4 Canonical transition evidence

Save:

```text
M commit object
parents(M)
tree(M)
exact B->M compare/path delta
all M lock path modes/OIDs
fetched M exact lock bytes and per-object SHA-256
fresh parsing of M next_binding and all V3 lock fields
fresh first-parent commit-object chain from C through M to B
```

The saved records must make `parent(M)=B`, `tree(M)=T`, and exact B->M lock-only delta independently reproducible.

### 13.5 Current-state evidence

Save at the M4 observation time:

```text
C = fresh current main SHA
current tree SHA
current exact expected lock path/mode/OID/bytes/SHA-256
freshly parsed current next_binding
fresh reconstructed CanonicalAcquireIdentityV3
fresh active/unexpired calculation inputs and observation timestamp
fresh effective Ruleset raw response and evaluated gate fields
```

The reviewer must be able to prove that the historical canonical transition still denotes the exact current active acquisition at the measurement stop.

### 13.6 Historical plan controls retained

Also retain the historical plan's M0/M1/M2/M3/M4 SHAs and tree SHAs, every exact transition delta, source/terminal/RELEASE evidence, wrong-worker result, duplicate/reuse controls, old-epoch replay result, final idempotency result, semantic no-Truth/no-claim/review/outcome/evaluation/failed-route sentinels, and any cleanup evidence.

Screenshots or prose are supplemental only. Where Git object/REST evidence exists, save exact identifiers and raw machine-readable observations sufficient for independent replay.

## 14. M4 acceptance rule

The live execution may report `ACTIVE_NEXT` only if all historical plan gates pass and all V3 conditions below pass simultaneously:

```text
independently derived semantic IDs
AND exact persisted next_binding equality
AND exact B
AND exact complete lock objects
AND exact precomputed T
AND selected H has its own successful authoritative Verify lineage
AND H is a single exact B->T lock-only transport
AND canonical M is the unique first-parent child of B
AND parents(M) == [B]
AND tree(M) == T
AND exact B->M lock-only delta
AND fresh semantic reconstruction from M/current exact lock bytes
AND M remains on current first-parent ancestry
AND current exact lock is unchanged, active and unexpired
AND fresh Ruleset gate passes
```

PR number/ref/merge metadata and transport commit SHA remain audit/debug locators only after canonicalisation. Numeric `run_id` magnitude is never ordering authority.

## 15. Cleanup compatibility with V3

The historical truth-neutral cleanup remains the accepted strategy and MUST NOT acquire a third Task.

Only after the full M4 V3 evidence bundle is frozen:

1. fresh-read the current expected-next Dittert lock and require it still equals the exact M4 V3 bundle, including identical `next_binding`, exact bytes/OIDs/hashes, worker/principal/work-ref/collision bundle, and active/unexpired state;
2. create the historical second truth-neutral `ABANDONED_TERMINAL` for `TASK-DITTERT-N5-001/w-0bebfd2fd11cb67f` with `SCOPE_STOP`, `abandonment_count=1`, and `truth_layer_effect=NONE` through ordinary policy;
3. during terminalisation, the V3 lock itself MUST remain byte-for-byte unchanged; do not strip, rewrite, renew, or normalize `next_binding`;
4. invoke the existing exact-worker RELEASE primitive directly against the exact current `NEXT_LOCK_ID` / complete collision bundle;
5. require the RELEASE canonical transition to delete exactly the complete current Dittert lock bundle and no unrelated path;
6. do **not** invoke `/next` again during cleanup;
7. fresh-read main to prove no active field-test lock remains and re-run the no-Truth/no-claim semantic sentinels.

The accepted V3 design keeps legacy schema compatibility and does not broaden RELEASE authority; therefore a persisted `next_binding` extension is expected to coexist with this cleanup. Actual live execution MUST nevertheless verify this on the independently reviewed merged Phase B implementation before cleanup mutation.

If the accepted implementation cannot safely terminalise/release the V3 next-binding lock using the existing truth-neutral strategy, stop and report `CLEANUP_V3_INCOMPATIBLE`. Leave the exact lock untouched for coordinator handling rather than manually deleting it, weakening settings, or calling `/next` into a third Task.

## 16. Phase-B merge and observability gate

This supplement is ready for use only after an independently reviewed Phase B implementation matching the accepted V3 spec is merged to `main`.

At actual Phase 0, abort before live mutation if the merged implementation cannot expose enough machine-readable evidence to populate every required V3 record in Sections 4-13, or if doing so would require any repository settings change, secret change, trusted-token broadening, protected schema/policy change not separately reviewed, or production semantics outside the accepted V3 contract.

The historical status `FIELD_TEST_OBSERVABILITY_INSUFFICIENT` remains appropriate for missing diagnostics. Do not weaken the evidence contract merely to run the test.

## 17. Compatibility verdict

```text
SUBSTRATE                         = PASS_AT_COMPAT_REVIEW
HISTORICAL_PLAN_CHANGED           = NO
V3_SUPPLEMENT_REQUIRED            = YES
NEXT_BINDING_EVIDENCE             = REQUIRED
CANONICAL_TREE_EVIDENCE           = REQUIRED
VERIFY_LINEAGE_EVIDENCE           = REQUIRED_PER_EXACT_SELECTED_HEAD
POST_SQUASH_M_EVIDENCE            = REQUIRED
PR_NUMBER_REF_POST_AUTHORITY       = NO
RUN_ID_ORDERING_AUTHORITY          = NO
FRESH_RULESET_GATE                 = REQUIRED
TRUTH_NEUTRAL_CLEANUP              = COMPATIBLE_BY_DESIGN; REVALIDATE_AFTER_PHASE_B_MERGE
THIRD_TASK_ACQUISITION_IN_CLEANUP  = FORBIDDEN
LIVE_EXECUTION_PERFORMED           = NO
VERDICT                            = READY_AFTER_PHASE_B_MERGE
```

The existing accepted field-test plan plus this supplement is sufficient as the evidence contract for testing the final accepted V3 implementation after that implementation has been independently reviewed and merged. Any future implementation/security review that changes V3 authority or equality semantics supersedes this compatibility verdict and requires a new field-test review before execution.
