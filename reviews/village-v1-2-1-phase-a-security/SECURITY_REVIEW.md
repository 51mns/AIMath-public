# Village v1.2.1 Phase A independent security review

## Review identity

- Task: `AIMATH-VILLAGE-V1-2-1-PHASE-A-INDEPENDENT-SECURITY-REVIEW`
- Role: independent security reviewer
- Public main observed at review start and again before review-branch creation: `71547cb5d757afaace54b558f2d0a4a49fad5656`
- Fixed writer target: `f03ada7a5d5ee3367daa795d70996c5317b69cef`
- PR: `#28`
- PR state at review: OPEN, non-draft
- PR base: `main@71547cb5d757afaace54b558f2d0a4a49fad5656`
- PR head: `platform/village-v1-2-1-trusted-lock-lifecycle@f03ada7a5d5ee3367daa795d70996c5317b69cef`
- Target drift: NO
- Fixed base→target changed paths: 14
- Phase B started: NO
- PR #28 merged by reviewer: NO

## Verdict

**PASS_WITH_REQUIRED_CHANGES**

No CRITICAL or HIGH release/acquire authority bypass was found in the fixed target. The automatic RELEASE implementation itself is narrowly bound to current trusted main, exact principal/task/worker/collision/bundle identity, deletion-only transport, terminalisation, exact Git-object checks, final race revalidation and the server strict-status gate.

However, one MEDIUM workflow-governance hardening defect is reproducible in `scripts/workflow_security.py`. The parser accepts trusted write workflows containing additional arbitrary `run` commands with `${{ github.token }}`, accepts caller-token inheritance into a local composite through job-level environment, and treats mutable `docker://...:tag` actions as exempt from external-action pinning. The current fixed trusted lifecycle workflow does **not** contain those dangerous forms, so this is not a direct privilege escalation from an ordinary untrusted PR at `f03ada7...`; workflow/governance paths are protected and the parser is defence in depth. Nevertheless, the target architecture explicitly advertises structural workflow hardening, and the requested security contract says dangerous workflows accepted by the parser are a security finding. Fix this before Phase A integration.

Integration recommendation: **REQUIRES_FIX**.

After the parser fix is independently rechecked, the code can become a `MERGE_READY_AFTER_SETTING_GATE` candidate. Live automatic merge must still remain blocked until `required_status_checks.strict=true` can be confirmed by an audited read path.

## Findings

### CRITICAL

None.

### HIGH

None.

### MEDIUM M-01 — trusted workflow parser is under-constrained

Fresh adversarial fixtures preserving the required `workflow_run` trigger, lifecycle concurrency, literal `main` checkout, full-SHA Actions pins, `contents: write`, and the exact `python3 scripts/lock_auto_activate.py` command were evaluated against the fixed-target parser logic.

The parser returned no errors for all of the following:

1. an additional arbitrary `run` step carrying `GH_TOKEN: ${{ github.token }}`;
2. a job-level `GH_TOKEN: ${{ github.token }}` inherited by a local composite whose shell uses `$GH_TOKEN` without spelling `github.token` in the composite manifest;
3. `uses: docker://alpine:latest` in the trusted write workflow.

Root causes:

- the trusted writer check requires the activation command to be present, but does not require it to be the only write-capable command;
- the global scalar scan rejects `secrets.*`, but `github.token` is only constrained for local-action call sites/manifests, not arbitrary trusted-workflow `run`/`env` locations;
- `_external_uses_errors` explicitly exempts all `docker://` uses from the full-commit-SHA rule.

Impact is bounded at this fixed commit because `.github/workflows/**`, `scripts/workflow_security.py`, `scripts/lock_auto_activate.py`, and related governance files are maintainer-protected, and the actual trusted writer contains none of the malicious extra forms. Thus this is MEDIUM rather than HIGH. It is still a real false-negative in the advertised defence-in-depth boundary.

Required fix before merge:

- make the trusted write workflow structurally allowlisted, not merely presence-checked;
- confine `${{ github.token }}` to the single audited activation step/environment and reject job/global inheritance paths;
- reject mutable `docker://` references in contribution workflows, or require an immutable digest policy that is structurally verified;
- add fresh negative tests for the three fixtures above;
- strongly consider adding `.github/actions/**` to protected/governance/CODEOWNERS coverage before any trusted writer begins to use local composite actions.

### LOW L-01 — bounded release discovery is fail-closed but can sacrifice availability

Open-PR and PR-files discovery are bounded to three pages of 100. Exceeding the bound raises and aborts automation rather than selecting from an incomplete set. This is security-safe/fail-closed, but an unusually large open-PR population can disable automatic lifecycle progress. No authorization bypass results.

## Property-by-property review

### 1. Authority boundary — PASS

- PR-head Verify is a trigger only.
- The write workflow checks out literal current `main` with `persist-credentials: false`.
- The local trusted checkout SHA is compared with the freshly fetched main SHA before state use.
- PR-head Python/workflow code is not executed with the write token.
- `pull_request_target` is absent from the fixed workflows and structurally forbidden.

### 2. RELEASE cannot create ownership — PASS

Automatic RELEASE requires every changed file to have GitHub status `removed` and to be a safe `coordination/locks/**.yml` path. The trusted reconstruction copies current main and unlinks only those paths. The resulting Village transition must classify exactly as `RELEASE`. Addition, replacement, modification, TAKEOVER or RENEW shapes do not enter the automatic RELEASE path.

### 3. Exact worker binding — PASS

Automatic RELEASE independently requires:

- PR principal equals canonical lock principal (`gh:<login>`), with no maintainer override;
- strict release ref binding;
- exact canonical `task_id`;
- exact canonical `worker_id`.

A fresh independent recheck of same-principal/wrong-worker produced `automatic RELEASE worker binding mismatch`.

This guard is session/scheduling separation, not authentication. `worker_id` remains explicitly non-secret and non-credential. A malicious actor controlling the same GitHub principal can impersonate a worker ID; the design does not claim to solve same-principal/Sybil behavior.

### 4. Task/collision/bundle identity — PASS

The trusted release revalidator checks current Task existence, exact collision-key equality, exact removed lock bundle, and finally requires changed deletion paths to equal the complete canonical bundle path set. Partial bundle deletion is rejected.

### 5. Release ref parsing — PASS

`release/<TASK-ID>/<worker-id>` is full-matched before path generation/interpolation. Task IDs are bounded to 96 characters and workers to lowercase `w-` plus 16–32 hex characters.

Fresh boundary controls rejected traversal, percent-encoded traversal text, extra segments, `refs/heads/...`, uppercase worker prefix/hex, short/overlong worker IDs, Unicode Cyrillic confusables, and an overlong Task ID. A canonical ref was accepted.

### 6. Terminalisation — PASS

`RESULT_TERMINAL` is a current-main, regular-file, schema-valid outcome with exact `task_id`.

`ABANDONED_TERMINAL` is schema validated with `additionalProperties: false`, exact task/worker, bounded reason enum, timestamp, positive abandonment count, optional 40-hex `last_work_head`, and `truth_layer_effect: NONE`.

A malformed RESULT does not permanently hostage the lock if a valid abandonment marker exists. A marker older than the current acquisition is rejected as stale.

### 7. Abandonment cooldown — PASS

Same `(task_id, worker_id)` reacquisition is denied while `now < abandoned_at + 24h`. Fresh boundary control confirmed 23:59:59 remains blocked and exactly 24:00:00 is no longer blocked. Marker modification requires strictly increasing timestamp and count increment by exactly one; deletion is rejected. A stale marker predating a later lock acquisition cannot terminalise that later lock.

### 8. RELEASE discovery/order — PASS with availability caveat

Only independently eligible RELEASE candidates are placed in the ordering set, then the minimum PR number is chosen. Invalid/draft/stale/wrong-worker/malformed candidates are filtered before ordering, so an invalid lower-number candidate does not block an eligible higher-number one. Eligible RELEASE is considered before the source-triggered ACQUIRE path.

Pagination is bounded and fail-closed; see L-01.

### 9. ACQUIRE regression — PASS

The Phase A rewrite retains or strengthens the existing v1.2 gates:

- current-main maintainer allowlist;
- exact current base;
- same-repository head;
- added regular `100644` lock blobs only;
- exact Git-tree/blob identity;
- Task READY check;
- exact collision keys;
- worker cap plus existing Village campaign/global readiness/capacity validation;
- trusted-main state revalidation;
- strict server gate;
- final main/head/base re-fetch;
- merge with expected head SHA.

No ordinary contributor was added to the ACQUIRE authority set.

### 10. RENEW/TAKEOVER firewall — PASS

The automatic lifecycle only executes a candidate if trusted transition classification is exactly `RELEASE` or, on the pre-existing source-triggered path, exactly `ACQUIRE`. `RENEW` and `TAKEOVER` have no automatic merge path in Phase A.

### 11. Main/head race — PASS, conditional on strict server gate

Final revalidation aborts if main, PR head, or PR base moves. Fresh base-only movement control was rejected. Lifecycle serialization reduces overlap but is not treated as sufficient race protection. The final GET→merge gap is covered by the required server-side strict status-check setting plus expected head SHA; therefore unreadable strict state blocks merge.

### 12. Git object representation — PASS

Base RELEASE lock objects are checked against the exact current-main recursive Git tree and must be `100644` `blob` with SHA equal to the PR deleted-file SHA. Head tree must not contain the deleted path. Materialisation additionally refuses symlink/non-file deletion targets. Ordinary PR diff classification uses `--no-renames`, so a rename cannot hide a lock move.

### 13. Workflow security parser — REQUIRED FIX

The fixed actual workflows are safe under the reviewed threat model, but M-01 demonstrates parser false-negatives for dangerous trusted workflow forms. The parser is therefore not accepted as fully implementing its documented hardening contract.

### 14. Protected governance — PASS for current Phase A files; future local-action coverage recommended

The fixed target adds the v1.2.1 architecture, workflow parser and Phase A tests to `PROTECTED_PATHS` and CODEOWNERS. `coordination/policy/**` covers the new autonomous-principal allowlist; `schemas/**` covers the abandonment schema. Layout validation requires the new files.

`.github/actions/**` is not presently protected. No fixed trusted workflow uses a local composite action, so this is not a current authority bypass, but it should be protected before local composites become trusted-writer dependencies.

### 15. AUTONOMOUS_LOCK_PRINCIPALS — PASS

The allowlist is loaded from the trusted current-main checkout. Fixed Phase A scope contains only `51mns`, leaves automatic ACQUIRE policy unchanged, and explicitly keeps automatic RENEW/TAKEOVER false. Worker-controlled branch content does not define authority.

### 16. Strict server gate — PASS_FAIL_CLOSED

Fresh read of the branch-protection required-status-check endpoint returned `403 Resource not accessible by integration` in this reviewer environment. The fixed code converts unreadable/OFF/malformed strict state into `AUTO_ACTIVATION_BLOCKED_SETTING_CONFIRMATION` and performs no merge.

This 403 is not a code-security failure. It is a live activation gate.

### 17. Truth firewall — PASS

RELEASE removes scheduling ownership only. Abandonment requires `truth_layer_effect: NONE`. The Phase A changed-path set does not add any claim/review/novelty promotion route, and the architecture explicitly separates GitHub governance from mathematical independence. No I2/I3 or `INDEPENDENTLY_REPRODUCED` promotion is caused by RELEASE/terminalisation/abandonment.

## Fresh negative controls

The writer 32-test suite was inspected first; the following controls were selected so the counted fresh set is not just a rerun of writer cases.

| Fresh control | Result |
|---|---|
| Partial deletion of a three-path canonical bundle | PASS: rejected by exact path-set inequality |
| Abandonment timestamp one second before current lock acquisition | PASS: stale marker rejected |
| Cooldown at 23:59:59 | PASS: still active |
| Cooldown at exactly 24:00:00 | PASS: inactive at boundary |
| Final revalidation with only PR base SHA moved | PASS: rejected (`PR base moved after revalidation`) |
| Release-ref matrix: traversal/encoded text/extra segment/refs prefix/uppercase/Unicode/overlong | PASS: all invalid; canonical ref accepted |
| Trusted workflow extra arbitrary `run` + `${{ github.token }}` | **FAIL EXPECTATION / finding M-01:** parser returned no errors |
| Trusted local composite receiving inherited job-level token | **FAIL EXPECTATION / finding M-01:** parser returned no errors |
| Mutable `docker://alpine:latest` in trusted writer | **FAIL EXPECTATION / finding M-01:** parser returned no errors |

Same-principal/wrong-worker was also independently rechecked and rejected, but is not counted as writer-novel because the writer suite already contains that scenario.

## Regression reproduction / CI evidence

Independent local full-repository execution was not possible in the reviewer runtime because a fresh Git clone/download was not available there. This was not converted into a local PASS.

Instead, the reviewer freshly fetched the exact PR #28 Actions job and decoded logs. GitHub checked out merge ref `195ee7cce603391790b8cb3906be3efcbdf78926`. Its Git tree SHA is `1b6c8a8d7d87c28119c13fc2c7962394aa4872cb`, exactly equal to fixed target `f03ada7...` tree SHA `1b6c8a8d7d87c28119c13fc2c7962394aa4872cb`; therefore the executed bytes equal the fixed-target tree even though GitHub used the synthetic PR merge commit.

Observed successful commands (GitHub step success, shell `bash -e`, no `continue-on-error`; effective exit 0):

- `python3 scripts/workflow_security.py .` -> 0
- `python3 scripts/public_release_audit.py .` -> 0
- `python3 scripts/verify_public_layout.py .` -> 0
- `python3 scripts/village.py validate` -> 0
- `python3 scripts/village.py status` -> 0
- `python3 scripts/village.py rank` -> 0
- `python3 scripts/village.py test` -> 0 (`25` synthetic tests)
- `python3 scripts/test_village_v1_1.py` -> 0 (`15` tests)
- `python3 scripts/test_village_v1_2.py` -> 0 (`28` tests)
- `python3 scripts/test_village_v1_2_1.py` -> 0 (`32` tests)
- `reuse lint` -> 0
- `python3 scripts/reproduce_public_claims.py .` -> 0 (`PUBLIC_REPLAY_SUITE=PASS count=8`)

DCO check also reported all 15 target commits signed off.

## Remote read-back

Fixed target critical blobs were freshly read directly from remote commit `f03ada7a5d5ee3367daa795d70996c5317b69cef`:

- `scripts/check_village_pr.py` -> blob `887f2bf7e57f4888a3985a4f7b432ce0dd2f04c1`
- `scripts/lock_auto_activate.py` -> blob `3e885b728786e253f9906f7d3abc3e176f1b1c91`
- `scripts/village_v1_2.py` -> blob `b11e898af70bfdc013b0bc20a1fd0280ad8b232f`
- `scripts/workflow_security.py` -> blob `faefb79801027d4153af2d2dd6f7e33208b331eb`

The fixed target commit tree is `1b6c8a8d7d87c28119c13fc2c7962394aa4872cb`.

## Required next step

Patch M-01 on the writer side without broadening Phase A:

1. keep Phase A automatic RELEASE only;
2. make the trusted writer workflow structure/steps/token placement allowlisted;
3. reject or immutably pin Docker action references;
4. add the three fresh parser negative controls;
5. if local composites remain supported for trusted writers, protect `.github/actions/**` in governance/CODEOWNERS;
6. rerun exact-head CI and return a new fixed writer SHA for focused independent re-review;
7. after code PASS, separately satisfy the live strict-setting confirmation gate without adding write-admin authority.
