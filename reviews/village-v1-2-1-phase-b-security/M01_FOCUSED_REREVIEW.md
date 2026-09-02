# Village v1.2.1 Phase B M-01 focused security rereview

TASK-ID: `AIMATH-VILLAGE-V1-2-1-PHASE-B-M01-FOCUSED-REREVIEW`

## Boundary

- public main used to create this review branch: `71547cb5d757afaace54b558f2d0a4a49fad5656`
- old rejected Phase B target: `ac28382c9779883ba9e92170478a325b1ce970fb`
- remediated fixed target: `7bd949d2a8b0ea8a35e4fce97988618735aad483`
- Phase A frozen head: `bb8701f551dbf3c155a4352931aa9f17f4588339`
- preserved Phase A lifecycle blob: `3e885b728786e253f9906f7d3abc3e176f1b1c91`
- first independent Phase B review: `5d64a4c5b22b7dfa21af2810b65ea5787eabe50c`
- PR #28 at rereview: OPEN, non-draft, base `main` at `71547cb5d757afaace54b558f2d0a4a49fad5656`, head `7bd949d2a8b0ea8a35e4fce97988618735aad483`
- writer branch at rereview: `platform/village-v1-2-1-trusted-lock-lifecycle` -> `7bd949d2a8b0ea8a35e4fce97988618735aad483`
- target drift observed: **NO**

The writer's remediation description was not treated as evidence. The old target, new target, first review, source bytes/tree blobs, PR/ref state, CI and security-setting endpoint were independently re-read from GitHub.

## Exact remediation delta

GitHub compare `ac28382c9779883ba9e92170478a325b1ce970fb...7bd949d2a8b0ea8a35e4fce97988618735aad483` is exactly **3 commits ahead / 0 behind / 3 changed files**.

Changed files only:

1. `docs/VILLAGE_ARCHITECTURE_V1_2_1.md`
   - new blob: `651422f1a0e4f553ba2c16be228af4002b7c4b4c`
2. `scripts/lock_auto_activate.py`
   - new blob: `89ca725a955daaeb3aaab8d88c2d32ea03773e4b`
3. `scripts/test_village_v1_2_1_phase_b.py`
   - new blob: `2ab9175b48316c0c984967ac4703e65aeb0876bf`

The three new commits are the candidate-isolation implementation, its regressions, and the remediation provenance freeze. All three changed-file bytes were read back at the fixed target. No workflow, policy, Phase A implementation, research, claim, or Truth-Layer file is in this remediation delta.

## Verdict

**PASS**

**M-01: CLOSED.**  
**L-01: CLOSED.**  
**Integration recommendation: `MERGE_READY_CODE_ONLY_SETTING_GATE_REMAINS`.**

No new CRITICAL, HIGH, equivalent MEDIUM blocking defect, authority regression, ownership bypass, race bypass, or Truth-Layer bypass was found in the remediation delta.

`PHASE_B_ACCEPTED = YES` for the fixed code target, subject to the already-separate live GitHub strict-setting confirmation gate.

## M-01 closure

The remediated wrapper defines a narrow candidate-observation exception set:

- `AutoActivationError`
- `AttributeError`
- `KeyError`
- `TypeError`
- `ValueError`

`_scan_releases()` now calls the frozen Phase A `_eligible_release_candidate()` inside that per-candidate boundary. If inspection fails, the RELEASE candidate is logged as ineligible and the loop `continue`s. It is never appended to the eligible list.

This directly closes the first review's concrete failure: a lower RELEASE-shaped candidate whose bounded PR-file enumeration raises

`AutoActivationError("PR files pagination exceeded bounded limit")`

no longer aborts the lifecycle run. A later valid RELEASE survives the scan; if there is no eligible RELEASE, ACQUIRE discovery can still run.

This is fail-closed isolation, not exception-based authorization. The only path into `eligible_releases` is a non-exceptional `_eligible_release_candidate()` return with a non-`None` candidate after the frozen RELEASE eligibility/object/identity/terminalisation checks.

## L-01 closure

Top-level candidate shape is now decoded through `_candidate_number()` and `_candidate_head_ref()` instead of unconditional nested `.get()` calls. Non-dict PR rows and non-dict/missing `head` maps are skipped as malformed/inapplicable observations rather than escaping the scan.

For candidate internals, the same candidate-local boundary covers the requested ordinary decoding/shape exception classes (`AttributeError`, `KeyError`, `TypeError`, `ValueError`) as well as `AutoActivationError`. The affected candidate is always ineligible and later candidates continue.

The catch is not a blanket `Exception`/`BaseException` authority bypass. Unexpected programmer/invariant failures outside the enumerated observation/shape classes still escape rather than being silently accepted. No caught exception can place a partial candidate into either eligible list.

## RELEASE priority and at-most-one mutation

Ordering remains:

1. globally obtain/validate the source Verify run, current main, trusted-main Village state, exact current-main tree, policy and open PR observations;
2. scan all RELEASE candidates;
3. select from fully eligible RELEASE candidates;
4. if one exists, require the strict setting gate, invoke the frozen merge path, and return from the run;
5. only when no eligible RELEASE exists, scan/select ACQUIRE;
6. require the same strict gate and invoke the same frozen merge path for at most one ACQUIRE.

Therefore:

- eligible RELEASE still wins over eligible ACQUIRE;
- candidate-local RELEASE failure does not demote a later eligible RELEASE;
- a successful/attempted RELEASE path returns before ACQUIRE mutation;
- at most one canonical lifecycle mutation is attempted per run.

## Fail-closed and global-prerequisite distinction

The candidate-local catch does **not** wrap repository-wide prerequisites. These remain outside candidate scanning and therefore global fail-closed boundaries:

- source workflow-run observation and its exact success/event/name checks;
- current `main` ref fetch and full-SHA validation;
- trusted-main state materialisation/validation;
- exact current-main recursive tree fetch and truncation/shape checks;
- maintainer/autonomous-principal policy load;
- open-PR list fetch itself;
- selected-candidate strict server gate;
- frozen final main/head/base race revalidation;
- merge endpoint expected-head SHA.

A failure of those prerequisites cannot be converted into a per-candidate `continue` followed by merge.

## Phase A preservation

The old target and the remediated target both expose:

`scripts/lock_auto_activate_phase_a.py` -> blob `3e885b728786e253f9906f7d3abc3e176f1b1c91`.

Therefore the frozen Phase A implementation bytes are unchanged. The wrapper still delegates RELEASE eligibility, exact-worker identity, terminalisation/object checks and final merge race validation to the preserved Phase A implementation.

The frozen final merge path re-fetches current main and the selected PR immediately before merge, rejects main/head/base movement, and sends the selected PR head SHA to GitHub's merge endpoint. The remediation does not weaken those controls.

## ACQUIRE regression spot-check

The old and remediated `_eligible_acquire_candidate()` authority sequence remains materially unchanged. A candidate must still pass, before becoming eligible:

- numeric PR identity and bounded PR-file observation;
- v1.2 ACQUIRE shape/principal/current-base/same-repository gate;
- exact-head current successful `Verify public release` evidence;
- exact Git tree retrieval;
- regular Git lock-object identity checks;
- materialised proposed-head Village validation;
- exact `ACQUIRE` transition validation against trusted current main;
- Task readiness/collision/capacity policy reached through the canonical transition/new-worker gates;
- exactly one added canonical lock bundle;
- worker-cap/workspace checks;
- changed paths exactly equal the added canonical lock-bundle identity.

Malformed or failed lower ACQUIRE candidates are isolated only as ineligible observations; ordering occurs after eligibility. No ACQUIRE can be admitted by the exception handler.

## Security/firewall preservation

The remediation does not change either workflow. Fresh baseline/workflow inspection and the exact remediation file set confirm:

- trusted-default-branch execution remains the write authority;
- no `pull_request_target`;
- PR-head code is not executed with the write token;
- checkout credentials are not persisted;
- no automatic Task creation;
- no automatic Task selection;
- no branch/ref creation;
- no PR creation;
- `RENEW` remains nonautomatic;
- `TAKEOVER` remains nonautomatic;
- research files are not an auto-merge class;
- lock lifecycle has no Truth-Layer/claim-promotion authority.

## Fresh adversarial controls

Reviewer-side source-matched controls were constructed independently of the writer tests. They exercise the fixed scanner/control-flow contract without treating the writer test assertions as authority.

1. lower RELEASE pagination `AutoActivationError` + higher valid RELEASE -> **PASS**, higher valid RELEASE survives.
2. lower RELEASE observation failure + valid ACQUIRE -> **PASS**, no eligible RELEASE permits ACQUIRE scan.
3. lower RELEASE malformed nested observation (`AttributeError`) + higher valid RELEASE -> **PASS**, later RELEASE survives.
4. malformed open-PR rows + valid ACQUIRE -> **PASS**, malformed rows are skipped and valid ACQUIRE survives.
5. lower ACQUIRE `AttributeError` + higher valid ACQUIRE -> **PASS**, later ACQUIRE survives.
6. eligible RELEASE + eligible ACQUIRE -> **PASS**, RELEASE wins.
7. eligible RELEASE merge path -> **PASS**, control flow returns before ACQUIRE mutation.
8. exception candidate -> **PASS**, never enters an eligible list.
9. strict endpoint observation failure/403 model -> **PASS_FAIL_CLOSED**, no merge authorization.
10. `strict=false` -> **PASS_FAIL_CLOSED**, no merge authorization.
11. main/head/base movement -> **PASS**, frozen final-revalidation logic rejects each movement.
12. Phase A blob mutation -> **PASS as immutable-object control**: old/new target tree read-back both equal the required blob `3e885b...`; any changed bytes would produce a different Git blob OID and fail this equality gate.

The reviewer-runtime scanner controls all returned the expected fail-closed/continuation outcomes. They are independent source-matched controls, not a claim that the GitHub repository was locally cloned/imported.

## Regression execution evidence

A direct local clone was attempted for exact-target replay but the review runtime could not resolve `github.com`. Therefore **no unavailable local command is recorded as a local PASS**.

Instead, GitHub Actions run `33606916878` / run #86 was fresh-read and tied exactly to head `7bd949d2a8b0ea8a35e4fce97988618735aad483`; the job conclusion is SUCCESS. Its successful steps provide exact-head execution evidence for the requested regression suite:

- `python3 scripts/workflow_security.py .` -> exact-head CI **SUCCESS** (`Structural workflow security`)
- `python3 scripts/public_release_audit.py .` -> exact-head CI **SUCCESS** (`Public safety audit`)
- `python3 scripts/verify_public_layout.py .` -> exact-head CI **SUCCESS**
- `python3 scripts/village.py validate` -> exact-head CI **SUCCESS**
- `python3 scripts/village.py status` -> exact-head CI **SUCCESS**
- `python3 scripts/village.py rank` -> exact-head CI **SUCCESS**
- `python3 scripts/village.py test` -> exact-head CI **SUCCESS**
- `python3 scripts/test_village_v1_1.py` -> exact-head CI **SUCCESS**
- `python3 scripts/test_village_v1_2.py` -> exact-head CI **SUCCESS**
- `python3 scripts/test_village_v1_2_1.py` -> exact-head CI **SUCCESS**
- `python3 scripts/test_village_v1_2_1_phase_b.py` -> exact-head CI **SUCCESS**
- `python3 scripts/reproduce_public_claims.py .` -> exact-head CI **SUCCESS**
- `reuse lint` -> exact-head CI **SUCCESS**

The Phase B direct test at this head includes explicit M-01 bounded-pagination continuation, malformed nested-candidate, malformed open-row, Phase A blob-preservation, no-PR/ref-creation, RELEASE-priority and nonautomatic RENEW/TAKEOVER controls. These writer tests are supporting execution evidence only; the verdict also rests on independent source and adversarial-control review above.

## Strict live gate

Fresh read of:

`/branches/main/protection/required_status_checks`

returned HTTP 403 to the available integration.

Therefore:

- `CODE_SECURITY = PASS_FAIL_CLOSED`
- `LIVE_ACTIVATION = SETTING_CONFIRMATION_REQUIRED`

The wrapper passes only when `strict is True`; unreadable, missing or false state blocks mutation. No repository setting change, PAT, App or secret is required or recommended by this review.

## New findings

- CRITICAL: none
- HIGH: none
- MEDIUM: none
- LOW: none new; former L-01 is closed by the bounded candidate-shape/observation isolation.

## Integration recommendation

`MERGE_READY_CODE_ONLY_SETTING_GATE_REMAINS`

The fixed Phase B code target closes M-01 without weakening RELEASE priority, fail-closed semantics, Phase A, ACQUIRE authority, final race checks or Truth-Layer/firewall boundaries. PR #28 may return to the v1.2.1 integration candidate queue **as code**, while live automatic mutation remains blocked until the existing external strict-setting requirement can be confirmed.