# Village v1.3 Phase B Stage-2 governance independent review

TASK-ID: `AIMATH-VILLAGE-V1-3-PHASE-B-STAGE2-GOVERNANCE-INDEPENDENT-REVIEW`

Repository: `51mns/AIMath-public`

Review scope: narrow independent audit of the Stage-2 `scripts/village.py` governance/operator registration only. The already accepted Stage-1 security/authority review is not reopened unless this Stage-2 diff contradicts it. This reviewer does not repair or merge the target.

## 1. Fixed identity

Fresh GitHub reads established:

```text
CURRENT_MAIN=518fea14987eaecdb9361f98527e5ae72c48c68b
TARGET_COMMIT=ae5ded20792ac22d22f4f61c00e6094402b2772a
TARGET_PARENT=518fea14987eaecdb9361f98527e5ae72c48c68b
TARGET_TREE=8ea11092584142fb1b0dcc724a50e0e635e26eea
VILLAGE_BLOB=425f1c9ce6dbd684cd497818920de55e49440da6
```

Fresh compare established `ahead_by=1`, `behind_by=0`, `total_commits=1`, with exactly one changed path:

```text
scripts/village.py
```

The target commit contains the required DCO trailer.

`TARGET_IDENTITY=PASS`.

## 2. PR #44 and exact-head Verify #118

Fresh PR read-back established:

```text
PR=44
state=open
draft=false
base=518fea14987eaecdb9361f98527e5ae72c48c68b
head=ae5ded20792ac22d22f4f61c00e6094402b2772a
head_ref=governance/village-v1-3-next-phase-b-registration-r1-chatgpt
merged_at=null
```

Fresh Actions read-back established:

```text
workflow=Verify public release
workflow_id=347191396
run_id=33754670148
run_number=118
run_attempt=1
head_sha=ae5ded20792ac22d22f4f61c00e6094402b2772a
base_sha=518fea14987eaecdb9361f98527e5ae72c48c68b
status=completed
conclusion=success
job_id=100646094269
job_name=verify
job_status=completed
job_conclusion=success
```

The job log was read directly. It checked out PR #44's merge ref, explicitly recorded the merge of exact target `ae5ded20792ac22d22f4f61c00e6094402b2772a` into exact base `518fea14987eaecdb9361f98527e5ae72c48c68b`, and passed the relevant gates:

- structural workflow security;
- Village PR policy / change class;
- DCO 1.1;
- public safety audit;
- public layout;
- Village validate/status/rank;
- canonical `python3 scripts/village.py test`;
- existing v1.2.1 direct suites;
- REUSE/SPDX and public replay checks.

`VERIFY_118=PASS`.

## 3. Accepted Stage-1 boundary retained

Fresh current-main blob reads confirmed the accepted Stage-1 artifacts are unchanged:

```text
ARCH=6b97ba453c3df60e4916c1c8e027ba262fafe716
PHASE_B_TEST=508b25287a8c21f4dc76b3f59663818ec3f82c55
PHASE_B_CORE=25aed74d7e85e8543fc93230968f7b70931b4aee
```

The Stage-1 final addendum records zero open findings and `VERDICT=PASS`, `IMPLEMENTATION_ACCEPTED=YES`, `STAGE1_READY_FOR_MERGE=YES`. Fresh post-merge Verify #117 also establishes the merged Stage-1 main `518fea14987eaecdb9361f98527e5ae72c48c68b` completed successfully.

`STAGE1_BLOBS_UNCHANGED=PASS`.

## 4. Manual `scripts/village.py` diff review

The complete Stage-2 diff is 19 additions and 1 deletion and performs only the following authority-neutral operator/registration changes.

### A. Canonical test registration — PASS

`cmd_test()` appends exactly:

```text
scripts/test_village_v1_3_next_phase_b.py
```

The pre-existing loop remains:

```python
for test in tests:
    rc = subprocess.call([sys.executable, str(test)], cwd=root)
    if rc:
        return rc
return 0
```

Therefore a non-zero Phase-B suite result propagates directly and cannot be swallowed or ignored.

Verify #118's direct job log independently confirms that `python3 scripts/village.py test` actually reached the newly registered Phase-B suite. Rows 1 through 73 were enumerated and the suite ended with:

```text
Ran 73 tests in 2.458s
OK
```

`TEST_REGISTRATION=PASS`.

### B. Narrow `/next` delegation — PASS

Stage-2 adds only:

```python
def cmd_next(root: Path, args) -> int:
    from village_next_phase_b import cli_next
    return cli_next(root, args)
```

No source-epoch derivation, continuation authority, semantic identity, canonical V3 identity, Verify lineage, Ruleset proof, RELEASE/ACQUIRE canonical gate, Truth authority, review authority, Task/Campaign creation, or lock lifecycle authority is reimplemented in `scripts/village.py`.

The accepted architecture places those responsibilities in `scripts/village_next_phase_b.py`; `scripts/village.py next` is only the operator surface. Stage-2 preserves that split exactly.

`NEXT_DELEGATION=PASS`.

### C. CLI surface — PASS

The command choices gain only `next`. The Phase-B-specific added arguments are exactly:

```text
--principal-id
--continuation-decision-id
--github-token-env
--phase-b-state-file
```

Before delegation, `next` requires all of:

```text
--task-id
--worker-id
--principal-id
```

and returns status 2 rather than invoking the Phase-B core when any is missing.

### D. Lazy import / non-next isolation — PASS

`village_next_phase_b` is not imported at module top level. The import exists only inside `cmd_next()`. Existing validate/status/rank/test paths therefore do not import the Phase-B transport module merely because Stage-2 exists, and importing `scripts/village.py` itself adds no Stage-2 network call.

Verify #118 directly ran `village.py validate`, `status`, and `rank` successfully before canonical tests, providing execution evidence that these established read-only entry points remain operational without invoking `/next`.

`LAZY_IMPORT_BOUNDARY=PASS`.

## 5. Authority non-broadening

The one-file diff contains no implementation of any of the following:

- source epoch authority;
- continuation authority or semantic-ID derivation;
- `CanonicalAcquireIdentityV3` construction/validation;
- authoritative Verify lineage;
- Ruleset proof;
- RELEASE or ACQUIRE canonical recognition/merge authority;
- Truth promotion;
- independent-review grading/promotion;
- Task or Campaign creation;
- automatic `RENEW` or `TAKEOVER`.

All Phase-B authority continues to be delegated to the already independently accepted `scripts/village_next_phase_b.py` and the existing trusted lifecycle primitive. The Stage-2 wrapper does not reinterpret or bypass its return value.

`AUTHORITY_NON_BROADENING=PASS`.

## 6. Execution evidence

A reviewer-side fresh clone was attempted with the fixed target SHA, but the local execution container again failed DNS resolution:

```text
fatal: unable to access 'https://github.com/51mns/AIMath-public.git/':
Could not resolve host: github.com
exit code: 128
```

Per this review task's explicit rule, that known environment limitation is not a blocker when exact-head Verify #118 independently establishes execution after Stage-2 registration.

Accordingly:

```text
PY_COMPILE=NOT RUN LOCALLY — fresh checkout unavailable; target `village.py` nevertheless parsed/executed repeatedly in successful Verify #118
VILLAGE_TEST=PASS — Verify #118 directly ran `python3 scripts/village.py test`, including 73-row Phase B / OK
PUBLIC_RELEASE_AUDIT=PASS — Verify #118 directly ran `python3 scripts/public_release_audit.py .` / PASS
```

No execution contradiction or new Stage-1 authority contradiction was found.

## 7. Findings and verdict

```text
CRITICAL=0
HIGH=0
MEDIUM=0
LOW=0

VERDICT=PASS
STAGE2_ACCEPTED=YES
STAGE2_READY_FOR_MERGE=YES
```

Acceptance is limited to fixed target `ae5ded20792ac22d22f4f61c00e6094402b2772a` on fixed base `518fea14987eaecdb9361f98527e5ae72c48c68b`. The reviewer does not merge PR #44 and does not modify target, main, production, tests, architecture, schemas, workflows, or coordination state.