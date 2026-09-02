# Village v1.2.1 Ruleset strict-gate security review

## Review identity

- Task: `AIMATH-VILLAGE-V1-2-1-RULESET-STRICT-GATE-SECURITY-REVIEW`
- Repository: `51mns/AIMath-public`
- PR: `#30`
- Base reviewed: `aae3b3be4a1da76eb4e1241ae7a366f39ff5f7f2`
- Fixed writer target reviewed: `d1c071eb609dc27938223baa48adadb089325665`
- Superseded intermediate head: `4f2827444bb344e2084f7ec13bf7f6feb33844fd`
- Review method: fixed-head, zero-base diff/source/settings/CI review plus independent negative controls. The writer's PR description and conclusions were not treated as authority.

## Verdict

**PASS / MERGE_READY**

No CRITICAL, HIGH, or blocking MEDIUM finding was identified. The patch is scoped to changing the strict-server-invariant attestation source from the Administration-scoped classic branch-protection status-check endpoint to GitHub's effective branch-rules endpoint. It does not broaden automatic RELEASE or ACQUIRE authority.

## Fixed-head and scope verification

At review time:

- current `main` = `aae3b3be4a1da76eb4e1241ae7a366f39ff5f7f2`;
- PR #30 was open, base `main` at that SHA, head branch `platform/village-v1-2-1-ruleset-strict-gate`, head `d1c071eb609dc27938223baa48adadb089325665`;
- writer branch remote ref resolved to the same fixed target;
- base -> target was exactly 5 commits ahead, 0 behind;
- changed-file set was exactly the expected five files:
  - `docs/GITHUB_SETTINGS_REQUIRED.md`
  - `docs/VILLAGE_ARCHITECTURE_V1_2_1.md`
  - `scripts/lock_auto_activate.py`
  - `scripts/test_village_v1_2.py`
  - `scripts/test_village_v1_2_1_phase_b.py`

Target blobs read back from the target tree:

- `docs/GITHUB_SETTINGS_REQUIRED.md`: `d0b964022f0afd9fbb5483105e237e55d8126418`
- `docs/VILLAGE_ARCHITECTURE_V1_2_1.md`: `3585d2a1096f28f51c8ec7656c52f49d5c407667`
- `scripts/lock_auto_activate.py`: `3d1b7187404df7a7174f1dd774a8d447eb68dcd5`
- `scripts/test_village_v1_2.py`: `003883f9704a90cc004778fd7fac2d9e089242fb`
- `scripts/test_village_v1_2_1_phase_b.py`: `ef893109fcb9b99181eae396a38fd6725692aecf`

No scope drift was found.

## Superseded-head delta

`4f2827444bb344e2084f7ec13bf7f6feb33844fd -> d1c071eb609dc27938223baa48adadb089325665` is exactly one commit and exactly one changed file: `scripts/test_village_v1_2.py` (+12/-3). The change updates the old v1.2 test seam from the obsolete classic response shape (`{"strict": ...}`) to the effective-rules list shape. No production file changed in this delta.

The intermediate head's `Verify public release` run #89 (`33614769000`) failed at `Village synthetic acceptance tests`; the final target's run #90 succeeds. The compatibility adjustment did not add a production legacy-response fallback.

## Endpoint authority and positive proof

Production `_strict_up_to_date_gate` now calls exactly:

```text
GET /repos/{owner}/{repo}/rules/branches/main
```

There is no classic branch-protection fallback in the target production gate and Ruleset ID `22089746` is not hard-coded in production code.

The gate grants its positive proof only after decoding a `required_status_checks` rule whose:

- `parameters.strict_required_status_checks_policy` is the Boolean `True`; and
- `parameters.required_status_checks` is a list containing a non-empty string context equal to `verify`.

The code correctly distinguishes the workflow display name `Verify public release` from the required job/check context `verify`.

## Fail-closed review

The target gate fails closed for:

- request/API failure, including 403/404 surfaced through `AutoActivationError`;
- top-level non-list response;
- malformed rule entry;
- missing `required_status_checks` rule;
- malformed/missing/non-dict relevant parameters;
- missing or non-Boolean strict policy;
- `strict=false`;
- missing/non-list required checks;
- malformed check entry;
- missing, non-string, or empty context;
- wrong-context-only responses.

A malformed relevant `required_status_checks` rule returns failure immediately, so a later positive-looking rule cannot mask malformed relevant authority data.

Independent small-harness controls reproduced the production decision logic across positive, false, wrong-context, absent, API-error, non-list, malformed parameter/strict/check/context, layered, and malformed-plus-positive cases. Only the intended positive cases passed.

## Layered Rulesets

GitHub's current official ruleset documentation states that active rules targeting the same branch are aggregated, all applicable rules apply, and when the same rule is configured differently the most restrictive version applies. The official REST documentation for `GET /repos/{owner}/{repo}/rules/branches/{branch}` states that it returns all active rules applicable to the branch and requires only Metadata read permission for a fine-grained token; public resources may also be read without authentication.

Therefore the implementation's behavior for:

```text
strict=false rule
+
separate strict=true + verify rule
```

is consistent with GitHub's all-applicable-rules / most-restrictive layering semantics. The implementation is also conservative when strictness and the `verify` context are not proven together in a well-formed positive rule.

The reviewer transport could not directly capture the live `/rules/branches/main` wire response because that specific URL was rejected by the connector's endpoint allowlist. This is a reviewer-tool transport limitation, not a GitHub/runtime authorization result. The endpoint contract was independently verified against GitHub's official REST documentation, and the currently configured Ruleset was freshly read back through the supported Ruleset API as described below.

## External Ruleset read-back and bypass boundary

Fresh external read-back found repository Ruleset:

- ID: `22089746`
- name: `Village main strict lifecycle safety`
- target: branch / condition `~DEFAULT_BRANCH`
- enforcement: `active`
- required context: `verify`
- `strict_required_status_checks_policy: true`
- `bypass_actors: []`
- `current_user_can_bypass: never`

The repository ruleset collection (including parents) returned this one active Ruleset at review time.

GitHub documentation confirms that Ruleset bypass can be granted to roles, users, teams, or GitHub Apps. Production does not independently attest bypass actors on every mutation. Under the present setup this is acceptable because the external security setting was freshly verified with an empty bypass list, and repository security-setting changes are already an explicit human governance boundary. This does leave a **LOW operational dependency**: a future administrator could weaken the invariant by adding an applicable bypass actor without changing repository code. That is configuration drift, not an authority bypass introduced by PR #30. It should remain part of deployment/read-back governance.

## Credentials and workflow security

The fixed diff changes no `.github/workflows/**` file and introduces no PAT, GitHub App credential, repository secret, environment secret, token-generation action, or workflow-permission change.

The target workflow boundary remains:

- `Verify public release`: `push`/`pull_request`, `contents: read`, job/check name `verify`;
- trusted mutation workflow: `workflow_run` of `Verify public release`, checkout of `ref: main`, `persist-credentials: false`, then execution of trusted-main `scripts/lock_auto_activate.py` with the built-in `github.token`;
- no `pull_request_target` trigger;
- PR-head code is not executed with the write credential.

`scripts/workflow_security.py` is outside the fixed diff and its target blob remains unchanged. Exact-head CI's structural workflow-security step succeeded.

## Phase A preservation and existing authority

Frozen `scripts/lock_auto_activate_phase_a.py` at the target has blob:

`3e885b728786e253f9906f7d3abc3e176f1b1c91`

which exactly matches the required frozen Phase A blob.

The production diff changes only `_strict_up_to_date_gate` plus the `verify` context constant. No RELEASE/ACQUIRE selection, eligibility, candidate-local isolation, object-identity, worker/task/capacity/collision logic, merge primitive, race revalidation, Truth Layer, review authority, RENEW, or TAKEOVER code is changed.

The target source still preserves:

- eligible RELEASE before eligible ACQUIRE;
- candidate-local observation-failure isolation;
- ACQUIRE validation against current main;
- exact successful `Verify public release` requirement for the exact ACQUIRE head;
- Git object identity checks;
- Village/task/worker/collision/capacity checks inherited by the reviewed gates;
- one selected lifecycle mutation followed by return;
- current-main/head/base and expected-head protections through the unchanged merge/revalidation machinery;
- RENEW and TAKEOVER as nonautomatic;
- Truth Layer and review authority unchanged.

## Documentation review

`docs/GITHUB_SETTINGS_REQUIRED.md` and `docs/VILLAGE_ARCHITECTURE_V1_2_1.md` match the implementation:

- they name `verify` as the required check context and distinguish it from `Verify public release`;
- they describe the effective branch-rules endpoint;
- they document fail-closed malformed/unreadable behavior;
- they state the Ruleset ID is provenance only, not runtime authority;
- they preserve the historical record that the original v1.2.1 implementation used the classic endpoint and that the live field test failed closed when that Administration-scoped read returned inaccessible.

The patch does not rewrite history to claim the design was Ruleset-based from the beginning.

## Exact-head CI

Final exact-head CI verified:

- workflow: `Verify public release`
- run ID: `33615003069`
- run number: `90`
- head SHA: `d1c071eb609dc27938223baa48adadb089325665`
- base SHA: `aae3b3be4a1da76eb4e1241ae7a366f39ff5f7f2`
- conclusion: `success`
- job/check name: `verify`

Successful steps included workflow security, PR policy/change class, DCO, public audit/layout, Village validate/status/rank, synthetic acceptance, v1.1, v1.2, v1.2.1 Phase A, v1.2.1 Phase B, REUSE, SHA manifest generation, and public claim reproduction.

## Severity summary

- **CRITICAL:** none.
- **HIGH:** none.
- **MEDIUM:** none.
- **LOW:** external-governance dependency on keeping applicable Ruleset bypass actors empty; current read-back is empty and this is not introduced by the patch.

## Integration recommendation

`MERGE_READY` for fixed target `d1c071eb609dc27938223baa48adadb089325665`, provided the coordinator re-reads PR #30 head and `main` before integration and rejects target drift.