# Village v1.3 Phase B M-03 final independent rereview

TASK-ID: `AIMATH-VILLAGE-V1-3-NEXT-PHASE-B-M03-FINAL-REREVIEW`

Repository: `51mns/AIMath-public`

Review scope: deliberately narrow final rereview of the Row-20 M-03 contract amendment only. This review does not redesign V3 and does not implement Phase B.

Target: `a482d1f4398489753589afe1ef3ed5e593a7e9c4`

Expected parent: `3dfefb87fad1d788bdb0ae6f58ec1c6d13ced3aa`

Target spec: `reviews/village-v1-3-next-phase-b-transport-preflight/PHASE_B_FROZEN_SPEC.md`

Target blob: `2ddc79843cf44bd588dc1a5ff89e996ecd246de9`

Historical V3 independent review: `432bc26d6f107ae1381d1e79282b450280cb5f61`

Historical review blob: `64079097856a04fb27f38b72c2d5ac9864ae4b16`

## Final implementation gate

**VERDICT: PASS**

```text
M-03 = CLOSED
PHASE_B_IMPLEMENTATION_ALLOWED = YES
```

The amendment closes the sole blocking M-03 test-contract gap identified by the prior independent V3 review. It converts Row 20 into one explicit parameterized end-to-end negative fixture for a syntactically valid and cryptographically/object-internally self-consistent forged `next_binding`, while requiring the trusted expected semantic IDs to be independently derived and frozen from fresh authoritative upstream evidence before the candidate binding is parsed as an observation.

No CRITICAL, HIGH, blocking MEDIUM, or new LOW finding was found in this narrow rereview.

---

## 1. Integrity gate

Fresh remote reads independently established:

```text
current main = 84a046359b299950403b68bfcb190930ebbc4c3f
target       = a482d1f4398489753589afe1ef3ed5e593a7e9c4
target parent= 3dfefb87fad1d788bdb0ae6f58ec1c6d13ced3aa
target blob  = 2ddc79843cf44bd588dc1a5ff89e996ecd246de9
design head  = a482d1f4398489753589afe1ef3ed5e593a7e9c4
```

Compare `3dfefb87... -> a482d1f4...` is exactly:

```text
ahead_by      = 1
behind_by     = 0
total_commits = 1
changed_files = 1
additions     = 73
deletions     = 0
```

Only changed path:

```text
reviews/village-v1-3-next-phase-b-transport-preflight/PHASE_B_FROZEN_SPEC.md
```

The target commit message carries a DCO `Signed-off-by` trailer.

Result:

```text
TARGET_MATCH = YES
SCOPE_MATCH  = YES
```

No target drift was observed.

---

## 2. Prior M-03 requirement re-derived from the fixed independent review

The historical V3 independent review accepted the V3 authority model itself and found one remaining blocking MEDIUM contract gap: the 73-row matrix did not require one exact end-to-end attack where a candidate supplies valid forged semantic IDs, recomputes its own lock bytes/blob OIDs/tree consistently, and is rejected only because those semantic IDs differ from fresh independently re-derived trusted records.

That review explicitly required the minimal repair to remain Row 20, preserve the 73-test total, derive all four expected semantic IDs from trusted upstream evidence first, and only then compare a fully self-consistent adversarial candidate.

This rereview treats that prior independent finding, not the writer's remediation status text, as the acceptance target.

---

## 3. Revised Row 20 — mandatory trusted derivation order

The amended Row 20 now requires the implementation to freeze the expected values in the following order before candidate `next_binding` is parsed as an observation:

1. fresh canonical source acquisition plus exact terminal/RELEASE evidence -> construct `SourceAcquisitionV1` -> freeze `source_epoch_id_expected`;
2. fresh canonical continuation state plus the applicable human Continuation Gate -> construct `ContinuationContextV1` -> freeze `continuation_context_id_expected`;
3. fresh post-RELEASE main plus fresh validated PENDING observations, hard filtering, `rank_v12`, fresh candidate eligibility and capacity -> construct `SelectionV1` -> freeze `selection_id_expected`;
4. from those independently frozen trusted records -> construct `AcquireIntentV1` -> freeze `acquire_intent_id_expected`;
5. only after all four expected IDs are frozen may the candidate lock bundle be parsed and compared.

This closes the self-authentication ambiguity. Candidate binding values are explicitly forbidden as inputs to expected-value derivation.

Result:

```text
TRUSTED_DERIVATION_FIRST = PASS
```

---

## 4. Four mandatory forged-ID parameterizations

The revised Row 20 explicitly parameterizes the same negative control over all four semantic primitives:

```text
A. forged source_epoch_id
B. forged continuation_context_id
C. forged selection_id
D. forged acquire_intent_id
```

For every case the forged value must remain a syntactically valid lowercase 64-hex value and must differ from the corresponding independently derived expected value.

The contract therefore closes the exact continuation/selection coverage gap that the prior review identified in Rows 66/67.

Results:

```text
FORGED_SOURCE_EPOCH          = PASS
FORGED_CONTINUATION_CONTEXT  = PASS
FORGED_SELECTION             = PASS
FORGED_ACQUIRE_INTENT        = PASS
```

---

## 5. Internally self-consistent adversarial fixture

The amended fixture cannot succeed merely by becoming malformed. It must remain otherwise valid on Task, worker, principal, base, collision bundle, work-ref, lock paths, JSON/schema shape, and all four `next_binding` child values.

After changing the selected forged semantic primitive, the fixture must recompute its own:

```text
exact lock bytes
bytes SHA-256
Git blob OIDs
exact_lock_objects
candidate Git tree
```

consistently around the forged binding.

Thus the negative test exercises semantic authenticity rather than parser/schema/path/base rejection. The attack candidate is intentionally self-consistent with its own forged representation.

Result:

```text
INTERNALLY_SELF_CONSISTENT_FIXTURE = PASS
CANDIDATE_MALFORMED_SHORTCUT       = REJECTED AS INSUFFICIENT
```

---

## 6. Self-authentication challenge

Question: can an implementation pass revised Row 20 by copying candidate `next_binding` values into process memory, calling those copies "expected", comparing candidate values to their own copies, and accepting?

**NO.** The amended text explicitly forbids adopting candidate X/Y/Z/Q as expected IDs and separately states that a comparison against another process-memory copy originally populated from the candidate does not satisfy Row 20.

Question: can an implementation pass Row 20 without independently constructing `SourceAcquisitionV1`, `ContinuationContextV1`, `SelectionV1`, and `AcquireIntentV1` from the required fresh trusted evidence?

**NO.** The amended contract explicitly states that such an implementation does not satisfy Row 20.

Result:

```text
SELF_AUTHENTICATION = REJECTED
```

---

## 7. Threat 29

The prior review's threat 29 was:

```text
candidate semantic binding is internally self-consistent
but
candidate semantic binding != trusted independently-derived records
```

The revised Row 20 now states this exact attack and requires:

```text
FAIL CLOSED before trusted merge eligibility
```

For every parameterized case the candidate is `PRE-MERGE INELIGIBLE` and receives no trusted merge eligibility, no ACQUIRE authority, no canonical ownership, and no `ACTIVE_NEXT`.

This is one end-to-end adversarial fixture, not four isolated string comparisons.

Result:

```text
THREAT_29 = PASS
```

---

## 8. Rows 66 / 67 / 70 / 71 relationship and exact test total

Rows 66, 67, 70 and 71 remain mandatory supporting regressions only. The amendment explicitly says they are not substitutes for end-to-end revised Row 20.

The original V3 matrix remains 73 rows. Section 21.20 supersedes the old Row-20 wording rather than appending Row 74, and the target diff adds no new numbered acceptance row.

Result:

```text
PREREGISTERED_TEST_COUNT = 73
ROW_74                    = ABSENT
```

---

## 9. V3 authority scope sanity

The target diff is exactly one test-contract-only addition to the frozen spec, with no deletions and no production/workflow/schema/settings file change.

The amendment explicitly leaves unchanged:

- `CanonicalAcquireIdentityV3`;
- post-canonical authority;
- `next_binding` persistence semantics;
- H/H2 equivalence;
- canonical tree identity;
- transport Verify separation;
- `run_number` policy;
- source epoch authority;
- Continuation Gate authority;
- selection/rank authority;
- Ruleset gate;
- canonical transition semantics;
- Phase A boundary.

No newly introduced clause changes those authority definitions. The added requirements constrain only how Row 20 must test the already-frozen semantic-authenticity rule.

Result:

```text
V3_AUTHORITY_UNCHANGED = YES
```

---

## 10. Narrow regression sanity for previously closed findings

No full 73-row re-review was performed because the delta is a single additive Row-20 contract amendment and does not touch the authority sections that closed the historical findings.

### H-01 — CLOSED

The amendment does not reintroduce PR-number/ref/merge-metadata causality as post-canonical authority.

### M-02 — CLOSED

The amendment does not alter the documented `run_number` lineage ordering or current-`run_attempt` policy.

### H-02 — CLOSED

The amendment does not restore exact transport head SHA as post-canonical authority and does not change H/H2 same-content equivalence.

### L-01 — CLOSED

The amendment does not weaken path uniqueness or duplicate `exact_lock_objects` rejection.

Result:

```text
H-01 = CLOSED
M-02 = CLOSED
H-02 = CLOSED
L-01 = CLOSED
```

---

## 11. Phase A boundary

The amended Row 20 does not change Phase A. The accepted boundary remains:

```text
Phase A ends at ACQUIRE_PENDING
no ACTIVE_NEXT
no writes
no Truth/review authority
PENDING != ownership
```

Result:

```text
PHASE_A_BOUNDARY = PASS
```

---

## 12. Findings

### CRITICAL

None.

### HIGH

None.

### MEDIUM

None. Historical blocking M-03 is closed by this amendment.

### LOW

None newly identified in this narrow rereview.

---

## 13. Final result

```text
CURRENT_MAIN: 84a046359b299950403b68bfcb190930ebbc4c3f
TARGET: a482d1f4398489753589afe1ef3ed5e593a7e9c4
TARGET_MATCH: YES
TARGET_PARENT: 3dfefb87fad1d788bdb0ae6f58ec1c6d13ced3aa
TARGET_BLOB: 2ddc79843cf44bd588dc1a5ff89e996ecd246de9
SCOPE_MATCH: YES

M03: CLOSED
ROW20: PASS
TRUSTED_DERIVATION_FIRST: PASS
FORGED_SOURCE_EPOCH: PASS
FORGED_CONTINUATION_CONTEXT: PASS
FORGED_SELECTION: PASS
FORGED_ACQUIRE_INTENT: PASS
INTERNALLY_SELF_CONSISTENT_FIXTURE: PASS
SELF_AUTHENTICATION: REJECTED
THREAT_29: PASS
PREREGISTERED_TEST_COUNT: 73
V3_AUTHORITY_UNCHANGED: YES
H01: CLOSED
M02: CLOSED
H02: CLOSED
L01: CLOSED

CRITICAL: 0
HIGH: 0
MEDIUM: 0
LOW: 0

VERDICT: PASS
PHASE_B_IMPLEMENTATION_ALLOWED: YES
```

This reviewer does not implement Phase B and does not merge this review branch. Return the fixed review result to the Village coordinator for intake.