# Village v1.2.1 Phase B independent security review

TASK-ID: `AIMATH-VILLAGE-V1-2-1-PHASE-B-INDEPENDENT-SECURITY-REVIEW`

## Boundary

- public main: `71547cb5d757afaace54b558f2d0a4a49fad5656`
- Phase A frozen: `bb8701f551dbf3c155a4352931aa9f17f4588339`
- Phase B fixed: `ac28382c9779883ba9e92170478a325b1ce970fb`
- PR #28: OPEN, non-draft, base `main` at the public-main SHA above, head equal to the fixed Phase B SHA
- Phase A -> B: 12 commits, exactly 9 changed files, no research/claim file
- target drift: none observed

## Verdict

**PASS_WITH_REQUIRED_CHANGES**

**Integration recommendation: `REQUIRES_FIX`.**

No CRITICAL/HIGH authority, ownership, object-identity, race or Truth-Layer bypass was found. One MEDIUM availability finding must be fixed before integration.

## M-01 — RELEASE candidate observation is not candidate-local

Severity: **MEDIUM availability/fairness; no authority bypass**.

The Phase B wrapper scans RELEASE-shaped open PRs before ACQUIRE and calls the frozen Phase A `_eligible_release_candidate` without a per-candidate `AutoActivationError` boundary. The frozen helper enumerates PR files before same-repository/principal rejection, and `_fetch_all_pr_files` raises after three full 100-file pages. GitHub's PR-files API supports responses larger than this bound.

Therefore an oversized invalid RELEASE-shaped PR can abort the trusted lifecycle run before a later eligible RELEASE or ACQUIRE is considered. This is fail-closed: it does not grant ownership, merge authority, or Truth-Layer effect. It is nevertheless contrary to the documented rule that invalid lower candidates cannot block later eligible work.

Required fix: isolate expected RELEASE observation failures per candidate and continue scanning, while retaining the complete trusted revalidation as authority. Add a regression with an oversized/failed lower RELEASE-shaped candidate followed by a valid later lifecycle candidate. Freeze a new target and perform focused rereview.

## L-01 — deeply malformed list elements

Severity: **LOW defensive availability**.

Most malformed top-level GitHub observations become `AutoActivationError` and are candidate-local on ACQUIRE. Some nested list elements are assumed to be mappings; a non-object row can raise a different exception and abort the run. This remains fail-closed. Normalising malformed element types to the expected observation error would complete the candidate-local contract.

## Phase A preservation

**PASS for preservation; M-01 is an inherited baseline availability defect exposed by this review.**

- target `scripts/lock_auto_activate_phase_a.py` blob: `3e885b728786e253f9906f7d3abc3e176f1b1c91`
- frozen Phase A `scripts/lock_auto_activate.py` blob: `3e885b728786e253f9906f7d3abc3e176f1b1c91`
- target and frozen Phase A `scripts/workflow_security.py`: `579f38ec5a1e29feb64682b2dfad48cc055dc7df`
- `.github/workflows/lock-auto-activate.yml` is unchanged by Phase B
- wrapper calls the frozen RELEASE eligibility/object/terminalisation/final-merge functions
- compatibility strict gate remains allow-only for `strict is True`

## ACQUIRE and workflow security

**PASS.** Discovered ACQUIRE candidates are independently checked for OPEN/non-draft/current-main base/same repo/maintainer principal/additions-only safe lock paths/exact-head successful pull-request Verify/exact regular Git blobs/Contents SHA/Village validity/exact ACQUIRE transition/Task readiness/collision-worker-Campaign-global gates/one canonical bundle/exact changed-path identity.

The write workflow remains trusted-main only, has no `pull_request_target`, no repository secrets, pinned external actions, `persist-credentials: false`, exact audited token placement and the unchanged M-01 workflow-structure allowlist. Successful PR-head Verify is evidence/trigger only.

## Ordering / firewalls / race

- eligibility-before-ACQUIRE-ordering: PASS
- invalid lower ACQUIRE not blocking: PASS
- RELEASE priority in the ordinary eligible path: PASS
- at most one mutation per run: PASS
- Task/selection/branch/PR creation firewall: PASS
- automatic RENEW/TAKEOVER firewall: PASS
- final main/head/base revalidation + expected head SHA: PASS
- Truth Layer firewall: PASS
- M-01 is a pre-order RELEASE observation availability failure

## Strict server gate

Code: **PASS_FAIL_CLOSED**.

Fresh branch-protection read through the available integration returned HTTP 403, so `required_status_checks.strict=true` is not confirmed. `LIVE_ACTIVATION = SETTING_CONFIRMATION_REQUIRED`. No setting bypass/change is recommended.

## Protected governance

**PASS.** Both new files are present in CODEOWNERS, `protected_patterns`, `governance_only_patterns`, and `verify_public_layout.REQUIRED`:

- `scripts/lock_auto_activate_phase_a.py`
- `scripts/test_village_v1_2_1_phase_b.py`

## Exact-head CI

Fresh evidence:

- run `33604533286`, run #83
- `Verify public release`
- event `pull_request`
- head `ac28382c9779883ba9e92170478a325b1ce970fb`
- conclusion `SUCCESS`

Its successful steps include workflow security, PR policy, DCO, public audit/layout, Village validate/status/rank/test, v1.1/v1.2/v1.2.1 A/B tests, REUSE, manifest generation and executable public-claim reproduction.

A direct local clone was unavailable in the review runtime because container DNS could not resolve GitHub, so no local clone execution is claimed as PASS. Exact-head CI is used as execution evidence after independent fixed commit/tree/blob read-back.

## Fresh adversarial controls

Independent source-matched controls passed for: newer failed Verify, in-progress/cancelled Verify, unrelated workflow success, tree SHA mismatch, non-100644 object, mixed lock+research, RENEW-like modification, fork/draft/ordinary principal, main/head/base movement, invalid-lower ACQUIRE, simultaneous same-collision eligible ACQUIRE ordering, push Verify rejection, and strict true/false/missing/403 behavior.

The same analysis reproduced M-01's bounded pagination exception before RELEASE candidate isolation.

## Fixed-target blobs

Target tree: `eb2906f1e7ce26f82ba4c24ba67bd78b329ae277` (non-truncated).

- `.github/CODEOWNERS` `c525d847f0eb23c01fd572590e830538178be150`
- `.github/workflows/verify.yml` `44d858e06d8334574acc8480731049ce5372d110`
- `coordination/policy/AUTONOMOUS_LOCK_PRINCIPALS.yml` `6d8360790c6d00f6444f027a337bf8aba32c4f32`
- `coordination/policy/PROTECTED_PATHS.yml` `ad2ffc3ad7ec94ed6f57fbba99c4d3cb5598a9d9`
- `docs/VILLAGE_ARCHITECTURE_V1_2_1.md` `34d4cc280bb3cff986371be11de199bd9c557286`
- `scripts/lock_auto_activate.py` `fb4d9ebe3b99c2100c8f15323d1a075b9f6664dc`
- `scripts/lock_auto_activate_phase_a.py` `3e885b728786e253f9906f7d3abc3e176f1b1c91`
- `scripts/test_village_v1_2_1_phase_b.py` `1bf4ba495886dff7b0e5e226d01ec9b3bedbdcec`
- `scripts/verify_public_layout.py` `b8766bfb6dda9eb740a79c5b0b91ac8774c81a87`

`PHASE_B_ACCEPTED = NO` for this fixed target. Fix M-01, freeze a new target, rerun exact-head CI, then perform focused rereview. The strict setting confirmation remains a separate live-activation gate.