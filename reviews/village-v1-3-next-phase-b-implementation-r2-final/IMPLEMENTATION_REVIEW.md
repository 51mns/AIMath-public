# Village v1.3 Phase B fixed Stage-1 independent implementation review

TASK-ID: `AIMATH-VILLAGE-1-3-PHASE-B-STAGE1-R2-INDEPENDENT-REVIEW`

Repository: `51mns/AIMath-public`

Review mode: zero-trust implementation/security review. This reviewer does not merge, does not modify production/tests/docs, and does not treat writer status or green CI as implementation acceptance.

## 1. Fixed identity

```text
CURRENT_MAIN=84a046359b299950403b68bfcb190930ebbc4c3f
TARGET_COMMIT=4c174fdc4b58f59fe132c0238397b95b1ec0ec21
TARGET_PARENT=84a046359b299950403b68bfcb190930ebbc4c3f
TARGET_TREE=307afe89e4401c1b057aaabcb9adb1a03b0cca26
```

Fresh GitHub compare established `ahead_by=1`, `behind_by=0`, `total_commits=1`, with exactly three changed paths:

1. `docs/VILLAGE_ARCHITECTURE_V1_3_PHASE_B.md`
2. `scripts/test_village_v1_3_next_phase_b.py`
3. `scripts/village_next_phase_b.py`

`scripts/village.py` is unchanged.

Exact target blobs:

```text
ARCH=6b97ba453c3df60e4916c1c8e027ba262fafe716
TEST=508b25287a8c21f4dc76b3f59663818ec3f82c55
CORE=25aed74d7e85e8543fc93230968f7b70931b4aee
```

The target commit contains the required DCO trailer.

PR #42 fresh read-back:

```text
base=84a046359b299950403b68bfcb190930ebbc4c3f
head=4c174fdc4b58f59fe132c0238397b95b1ec0ec21
head_ref=ops/village-v1-3-phase-b-core-stage1-r3-chatgpt
```

Verify run fresh read-back:

```text
workflow_id=347191396
name=Verify public release
run_id=33750875636
run_number=115
run_attempt=1
head_sha=4c174fdc4b58f59fe132c0238397b95b1ec0ec21
status=completed
conclusion=success
```

`TARGET_IDENTITY=PASS`.

Important limitation: the workflow checks out GitHub's PR merge ref (`60a1826726ce4d5cb3666e09d88e96d5a88a2eea`, merge of the exact target into the exact base). Stage-1 intentionally does not register the new Phase-B 73-row suite in `scripts/village.py`; Verify #115 therefore does **not** constitute an independent execution of `scripts/test_village_v1_3_next_phase_b.py`.

## 2. Frozen authorities

Fresh reads confirmed:

```text
FROZEN_SPEC_COMMIT=a482d1f4398489753589afe1ef3ed5e593a7e9c4
FROZEN_SPEC_BLOB=2ddc79843cf44bd588dc1a5ff89e996ecd246de9
ORACLE_COMMIT=1e81606b2a059a7ae59ec80aa68f9e9d2f67358b
ORACLE_BLOB=c52bb9cacbf535f224b5256fd5ed44a7fa0a8945
FINAL_SPEC_SECURITY_ACCEPTANCE=3c1be65016eda44f5efe849a6e2c2db273847db2
```

The implementation was reviewed against those frozen authorities before the historical failed review was read.

## 3. Current Ruleset evidence

Fresh GitHub ruleset reads show one active repository ruleset:

```text
id=22089746
name=Village main strict lifecycle safety
target=branch
enforcement=active
include=~DEFAULT_BRANCH
required context=verify
strict_required_status_checks_policy=true
bypass_actors=[]
current_user_can_bypass=never
```

This is evidence about the current repository setting. It is not used as a substitute for reviewing the implementation's own completeness/pagination proof.

## 4. V3 static implementation review

### A. TRUSTED_DERIVATION_FIRST — PASS (static)

The current orchestration path derives post-RELEASE semantics before candidate transport authority. In particular:

- `source_epoch_id` is retained from the source acquisition/release provenance path;
- `_derive_post_release_semantics(...)` derives fresh continuation/selection/acquire-intent semantics;
- `_canonical_continuation_restrictions(...)` obtains the restrictive stop/dependency facts from fresh typed Village state;
- the resulting `SemanticIds` are supplied separately to the candidate/premerge gates;
- premerge first checks candidate-internal consistency and then compares the candidate identity against the independently derived trusted IDs.

The reviewed code does not require candidate `next_binding` values to seed the trusted expected values.

### B. CanonicalAcquireIdentityV3 — PASS (static)

The implementation includes schema version 3, all four semantic IDs, expected base `B`, expected tree `T`, Task/worker/principal/work-ref, sorted collision keys, deterministic lock id, acquired/expires timestamps, and exact lock objects containing path/mode/blob SHA/bytes SHA-256. Duplicate object paths are explicitly rejected before canonical acceptance.

### C. B/H/H2/M semantics — PASS (static)

The gates distinguish transport head from canonical authority. Canonical recognition walks a fresh first-parent history to `B`, requires the immediate child `M`, requires single-parent `parents(M)==[B]`, exact tree `T`, exact lock-only `B->M` delta, current byte-identical active/unexpired canonical lock, and Ruleset proof. The tests include a real-Git object-store squash fixture where `H != M` but the canonical `B/T` content transition still confirms.

### D. Verify lineage — PASS (static)

The implementation filters exact workflow identity/path/name/event/head, performs bounded pagination, fails closed on incomplete/malformed/cap cases, chooses maximum `run_number` rather than run-id magnitude, re-fetches the authoritative `run_id`, and uses the current `run_attempt` state. The highlighted Row 55 fixture uses >100 results and a second page.

### E. Ruleset proof — PASS (static)

The current implementation obtains both effective default-branch rules and Ruleset summaries via a bounded multi-page collector, fetches details for discovered rulesets, and requires active default-branch applicability, strict `verify`, no bypass actors, and `current_user_can_bypass=never`. Unavailable/malformed/truncated/cap-exhausted evidence fails closed. Rows 28/62 exercise later-page/cap/bypass failure modes.

### F. RELEASE provenance — PASS (static)

The RELEASE gate does not use mere lock absence as authentication. It binds the source lock bundle and exact base/tree/delta, exact-head Verify and canonical first-parent transition before retaining source-release provenance.

### G. Continuation restrictions — PASS (static)

The previous literal-False defect is not present in the reviewed target. `_canonical_continuation_restrictions(...)` derives:

- `canonical_stop_condition_reached` from canonical Task/Campaign state;
- `canonical_dependency_followup_unusable` from current derived claim/dependency usability.

The values are passed into `NextRequest` and `derive_continuation_context_v1`, and the test suite checks that they are not hard-coded `False` or sourced from caller `args`. The Row-44 fixture also checks restrictive true values are bound into context and suppress same-campaign scheduling.

### H. Error boundary — PASS (static)

The current-main recursive tree, a repository-wide prerequisite, is observed outside the candidate-local `try` boundary. Candidate malformed rows may be dropped. The Row-33 negative control configures the base-tree read to raise `REPOSITORY_OBSERVATION_INCOMPLETE` and requires that exception to escape globally rather than be swallowed into a candidate-local continuation. The broad candidate-local catch remains, but the reviewed repository-wide substrate read that motivated historical H-02 has been moved outside it.

## 5. 73-row oracle review

Static structure establishes:

```text
SPEC_ROW_TO_TEST keys == 1..73 exactly
unique mapped names == 73
all mapped method names exist
number of test_* methods == 73
Row74 absent
```

Highlighted manual checks:

- **Row 20:** parameterizes all four forged semantic IDs. For each case it rebuilds a self-consistent candidate material, validates candidate blob OIDs and bytes SHA-256, and requires premerge rejection against separately derived trusted IDs with `CANONICAL_ACQUIRE_SEMANTIC_BINDING_MISMATCH`.
- **Rows 28 / 62:** use paged Ruleset clients including a full first page so page 2 is required; later-page/bypass/completeness conditions are represented.
- **Rows 32 / 33:** explicitly separate candidate-local malformed drop from repository-wide base-observation failure escaping globally.
- **Row 44:** checks canonical restrictive facts, `same_campaign_allowed=False`, and AST-inspects production glue so the two facts are passed into `NextRequest` and `derive_continuation_context_v1`, are not literal `False`, and do not originate from caller `args`.
- **Row 55:** uses paged Verify data and proves max `run_number`, not run-id magnitude, controls authority, with current attempt retrieval.
- **Rows 66 / 67:** require exactly `CANONICAL_ACQUIRE_SEMANTIC_BINDING_INCONSISTENT` for the candidate-content inconsistency boundary.
- **Rows 68–73:** include the real-Git squash fixture, duplicate-path rejection, semantic-binding propagation into bytes/OID/tree, canonical post-squash reconstruction, and mandatory `next_binding` failure.

The test file uses `_ExactGitRepo`, which invokes real `git` object construction for the B/H/H2/M oracle rows rather than only mirroring the production tree-OID calculation in Python.

Static evidence therefore shows the historical test-contract weaknesses were materially remediated. However the oracle explicitly requires more than method-count/static correspondence, and this review could not independently execute the exact 73-row suite. Consequently `ORACLE_73_MAPPING` cannot be promoted to an independent dynamic PASS in this review.

## 6. Historical finding closure

The historical FAIL at `6c890bc0e2f9ee8d7898706b01204826c9d29292` was read only after the independent static review above.

### H-01 — CLOSED

Historical defect: Phase-B adapter hard-coded both restrictive facts to `False`.

Current target: canonical restrictions are freshly derived by `_canonical_continuation_restrictions(...)`, propagated through production glue, and Row 44 contains a dedicated anti-hard-code/anti-caller-authority check.

### H-02 — CLOSED

Historical defect: broad candidate-local `PhaseBError` swallowing could hide repository-wide substrate failure.

Current target: current-main recursive tree observation is explicitly outside the candidate-local exception boundary; Row 33 verifies the repository-wide base failure propagates as `REPOSITORY_OBSERVATION_INCOMPLETE` instead of being swallowed.

### M-01 — CLOSED

Historical defect: no adequate Ruleset collection completeness/pagination proof.

Current target: bounded page collection exists for effective branch rules and Ruleset summaries, malformed/truncated/cap cases fail closed, details are fetched for the complete discovered summary set, and Rows 28/62 attack later-page/cap/bypass behavior.

### M-02 — OPEN (independent-evidence closure blocked)

Historical defect: 73 method names alone did not prove 73 frozen contracts.

Current target's fixtures are substantially stronger and the specifically weak rows reviewed above now target their threatened production gates, including real Git objects. Nevertheless this reviewer could not execute the exact suite from a fresh target checkout, so the required independent 73-row implementation evidence is incomplete. This OPEN status is an evidence/STOP-condition status; no new concrete semantic defect in the target test code is asserted here.

### LOW Rows 66/67 — CLOSED

Rows 66/67 now explicitly require the frozen code `CANONICAL_ACQUIRE_SEMANTIC_BINDING_INCONSISTENT`. Row 20 deliberately uses the separate premerge authenticity code `CANONICAL_ACQUIRE_SEMANTIC_BINDING_MISMATCH`, matching the final frozen Row-20 amendment rather than conflating the two boundaries.

## 7. Fresh execution attempt and STOP condition

The reviewer attempted to obtain an exact fresh checkout in the execution container:

```text
command:
  git clone --filter=blob:none --no-checkout https://github.com/51mns/AIMath-public.git /mnt/data/aimath_review_repo
  && git checkout 4c174fdc4b58f59fe132c0238397b95b1ec0ec21

exit code: 128
summary:
  fatal: unable to access 'https://github.com/51mns/AIMath-public.git/':
  Could not resolve host: github.com
```

The available GitHub connector can fresh-read repository objects but does not provide the exact checkout as an executable local working tree. Verify #115 contains no uploaded source/test artifact that can be materialized for a reviewer-side run.

Therefore the mandated independent commands were **not** executed:

```text
PY_COMPILE:        NOT RUN — exact checkout unavailable
PHASE_B_73:        NOT RUN — exact checkout unavailable
PHASE_A:           NOT RUN — exact checkout unavailable
V121:              NOT RUN — exact checkout unavailable
V121_PHASE_B:      NOT RUN — exact checkout unavailable
PUBLIC_RELEASE_AUDIT: NOT RUN independently — exact checkout unavailable
```

For context only, Verify #115 is successful and its log includes successful public audit and existing Village suites, but it does not execute the unregistered Stage-1 73-row Phase-B direct suite. CI therefore cannot be substituted for the missing independent run.

The task's explicit STOP condition says that if required tests cannot be reproduced, the reviewer must not manufacture PASS/FAIL and must return `BLOCKED`. That condition controls the final verdict.

## 8. Severity accounting at stop

```text
CRITICAL=0
HIGH=0
MEDIUM=1
LOW=0
```

The single open MEDIUM is M-02 as an **independent evidence closure gap caused by the blocked fresh execution**, not a newly demonstrated production vulnerability.

## 9. Final verdict

```text
VERDICT=BLOCKED
IMPLEMENTATION_ACCEPTED=NO
STAGE1_READY_FOR_MERGE=NO
```

This report does **not** assert that the target is insecure. The static review found the prior H-01, H-02, M-01, and Rows-66/67 LOW defects closed and found the highlighted new oracle fixtures materially aligned with the frozen contract. The only reason this reviewer does not issue PASS is that the required independent fresh execution cannot be reproduced in the current execution environment, which is an explicit review STOP condition.

No target code, test, documentation, PR, main, workflow, Ruleset, schema, or coordination state was modified by this reviewer.
