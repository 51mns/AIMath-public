# AIMath Village Architecture v1.2.1 — Trusted Lock Lifecycle

**Status:** PHASE-A SECURITY-REVIEWED / PHASE-B IMPLEMENTATION IN PROGRESS  
**Extends:** Village v1.0, v1.1 and v1.2 without weakening their Truth/Portfolio/security boundaries.  
**Phase A scope:** automatic `RELEASE` only.  
**Phase B scope:** broaden trusted automatic `ACQUIRE` activation only; Task selection and lock-PR creation remain worker `/join`/future `/next` responsibilities. `RENEW` and `TAKEOVER` remain nonautomatic.

## Phase A frozen provenance

Phase A is frozen at exact writer commit:

```text
bb8701f551dbf3c155a4352931aa9f17f4588339
```

That boundary received independent security review. The initial review found no CRITICAL/HIGH issue and one MEDIUM workflow-parser finding (M-01), which was fixed without changing the Phase A lifecycle core. The focused rereview then returned **PASS** and **M-01 CLOSED**.

Immutable review evidence:

- initial review artifact: `reviews/village-v1-2-1-phase-a-security/SECURITY_REVIEW.md`
  - review commit: `41db6adafa4cb64465d317264c24b2fa2bd9700a`
  - artifact blob: `21558e8a6781935279a49eb9a15260cb6319258d`
- focused M-01 rereview: `reviews/village-v1-2-1-phase-a-security/M01_FOCUSED_REREVIEW.md`
  - review commit: `71bbc2a9c7e989b6882bae6b78a9ae7a2cd1f430`
  - artifact blob: `472c396ff59615fb555567e25677964b65fe5749`
- exact Phase A CI at frozen head: `Verify public release` run `33601339054` / run #71 / SUCCESS.

Phase A code is accepted as the reviewed baseline for Phase B diff review. This provenance record is a later governance/documentation commit and does not change the frozen Phase A code boundary.

Live automatic mutation remains **SETTING_CONFIRMATION_REQUIRED** until trusted runtime can confirm `required_status_checks.strict=true`. Unreadable/OFF/malformed state must continue to fail closed; this repository change does not alter GitHub security settings or add credentials.

Phase B review range starts at the Phase A frozen writer head above and ends at a separately fixed Phase B head. Phase B must not reopen Phase A properties unless its diff changes a load-bearing Phase A file or creates a regression.

## 1. Authority boundary

A successful PR-head `Verify public release` run is never write authority. It may trigger the trusted lifecycle workflow, but every mutation is rederived by code checked out from current default-branch `main`. PR-head code is never executed with a write token. `pull_request_target` remains forbidden.

A merged canonical lock remains the only source of EXCLUSIVE ownership. `RELEASE` can only remove ownership; it cannot create or transfer it. Lock release has no mathematical, novelty, review, claim, or Truth Layer effect.

## 2. Exact worker RELEASE binding

Phase A binds a RELEASE request in the same-repository PR head ref:

```text
release/<TASK-ID>/<worker-id>
```

Both components are strictly validated before any path/ref interpolation. The ordinary PR lifecycle validator and the trusted automatic RELEASE revalidator both compare the requested `task_id` and `worker_id` to the exact current canonical lock. The changed deletion paths must also equal the complete canonical lock-bundle path set and its collision keys must still match the current Task.

Automatic RELEASE additionally requires the PR GitHub principal to equal the canonical lock principal. A maintainer cannot use automatic RELEASE as a principal override.

`worker_id` remains non-secret scheduling identity, **not** authentication. Multiple Village workers may share one GitHub principal, so this guard prevents accidental cross-worker release but does not solve malicious same-principal/Sybil behaviour. Repository/GitHub principal authorization remains the security identity.

## 3. Terminalisation

An exact-worker RELEASE is eligible only after one of these current-main terminal classes exists:

### `RESULT_TERMINAL`

A schema-valid `coordination/outcomes/<TASK-ID>.yml` whose `task_id` matches the lock. Structural validity is enough for lock release; mathematical correctness, review admission, artifacts, novelty and claim acceptance are not release authority.

### `ABANDONED_TERMINAL`

A schema-valid:

```text
work/<TASK-ID>/<worker-id>/ABANDONED_TERMINAL.yml
```

validated by `schemas/abandoned-terminal.schema.json`. It has `additionalProperties: false`, exact schema version, Task/worker binding, bounded reason enum, timestamp, monotone abandonment count, optional `last_work_head`, and `truth_layer_effect = NONE`.

A malformed RESULT_TERMINAL does not hold capacity forever: a valid ABANDONED_TERMINAL for the same lock acquisition may release it. An abandonment marker older than the current lock acquisition cannot terminalise that newer lock.

ABANDONED_TERMINAL is availability/scheduling state only. It cannot promote evidence or a claim. The marker is durable and its count/timestamp may only advance monotonically; deletion is rejected by PR policy.

## 4. Abandonment churn control

After a valid ABANDONED_TERMINAL, the same `(worker_id, task_id)` cannot ACQUIRE again for **24 hours**. The check runs in ordinary acquisition validation and therefore also in the trusted ACQUIRE revalidation. Malformed same-pair abandonment state fails closed.

The durable marker exposes `abandonment_count`, reason, last abandonment time, cooldown deadline and current cooldown state for Portfolio/operations visibility. This is an availability control, not mathematical judgment; failure remains a valid reportable outcome.

## 5. Automatic lifecycle ordering

The trusted workflow uses one concurrency domain:

```text
village-lock-lifecycle
```

with `cancel-in-progress: false`, so at most one trusted canonical lifecycle merge attempt is active at a time. Serialization reduces overlapping mutation attempts but does not eliminate staleness; main/head/base are still re-fetched immediately before merge.

Phase A behavior on every successful Verify trigger is:

1. discover open RELEASE-shaped PRs;
2. filter to candidates eligible **right now** by exact current-main revalidation;
3. sort simultaneous eligible RELEASE candidates by ascending PR number;
4. attempt at most one RELEASE;
5. only if no eligible RELEASE exists, consider the triggering PR through the v1.2 ACQUIRE path.

Thus Phase A guarantees `eligible RELEASE > triggering eligible ACQUIRE`. Draft, stale, malformed, unfinished or otherwise ineligible lower-number RELEASE PRs are filtered before ordering and cannot block an eligible higher-number RELEASE.

Phase B may broaden only the ACQUIRE side: after RELEASE candidates are exhausted, trusted-main code may discover open ACQUIRE-shaped PRs, independently revalidate each against current main and exact green CI, and deterministically activate at most one currently eligible candidate. Candidate discovery is not ownership and may not trust repository caches or self-reported PENDING_CLAIM data as authority. Task selection and lock-PR creation remain outside this write workflow.

The Phase B tie-break is ascending PR number **only after** each candidate independently passes all current-main eligibility, object, CI, readiness, collision, worker, Campaign and global-capacity checks. An invalid lower-number PR is never reservation or blocking authority.

`RENEW` and `TAKEOVER` remain nonautomatic.

## 6. Race and object gates

Automatic RELEASE requires: same repository; OPEN; non-draft; base `main`; base SHA equal to current main; exact successful Verify head as a trigger condition; strict release ref; deletions only; exact regular `100644` base lock blobs; deleted paths absent from exact PR-head tree; exact principal/worker/Task/collision/bundle identity; current-main terminalisation; and expected PR head SHA at merge.

Automatic ACQUIRE remains subject to the v1.2 authority/object/readiness/capacity gates and the same final current-main/head/base refetch plus expected-head merge. Phase B candidate discovery must not weaken those gates merely because the source Verify run belongs to another PR.

Current main, PR head and PR base are re-fetched immediately before merge. Movement aborts the attempt. A successful merge may stale another pending transport attempt; that is accepted and recoverable by a fresh Verify run.

## 7. Strict server gate

The write workflow remains fail-closed unless GitHub confirms:

```text
Require branches to be up to date before merging = ON
```

The merge API's expected SHA protects the PR head, not the base. Server-side strict status checks therefore remain mandatory. If the setting endpoint is OFF or unreadable, the bot prints `AUTO_ACTIVATION_BLOCKED_SETTING_CONFIRMATION` and performs no merge. v1.2.1 does not alter repository settings, Actions default permissions, secrets, PATs or GitHub Apps.

## 8. Workflow governance hardening

`scripts/workflow_security.py` structurally parses YAML rather than treating substrings/regex as the primary boundary. It scans `.github/workflows/**`, `.github/actions/**` and local `uses: ./...` composite actions; requires explicit workflow permissions; rejects missing/unknown write permissions, `write-all`, `pull_request_target`, secret expressions including whitespace variants, `secrets: inherit`, unsafe checkout credentials/refs, unpinned external actions, PR-head checkout in the trusted writer and local composite token acquisition.

For the trusted lock lifecycle workflow, the reviewed M-01 fix additionally constrains the exact job/step structure and `${{ github.token }}` placement and forbids local composite and Docker actions in that writer. Phase B must preserve that exact structural boundary unless a new independent security review explicitly accepts a change.

The primary security boundary remains GitHub permissions + protected governance/workflow paths + human governance review + trusted-main execution. The parser is defence in depth.

## 9. Phase boundary

Phase A is frozen and independently reviewed at `bb8701f551dbf3c155a4352931aa9f17f4588339`.

Phase B begins only after that PASS. It may broaden automatic `ACQUIRE` candidate discovery/activation, but it may not create Tasks, choose research on behalf of `/join` workers, create worker lock PRs, automate `RENEW`/`TAKEOVER`, change Truth Layer semantics, or weaken Phase A RELEASE security.

The final Phase B fixed commit must receive independent security review over the Phase A frozen-head-to-Phase-B-final diff before PR #28 may merge.

## 10. Frozen v1.3 carry-forward prerequisites

These previously frozen constraints are recorded here so later work cannot silently lose them. v1.2.1 does not implement their full design:

1. `reviews/**/REVIEW.yml` must become protected/governance-controlled before autonomous review launch.
2. Autonomous review files claiming `I2` or `I3` must fail CI.
3. Preregistration liveness `EFFECTIVE` may be established only by objective outcomes: review completion count increased inside the effectiveness window **or** oldest backlog age decreased. Mere heartbeat/activity is `ACTIVE_SUPPLY`, never `EFFECTIVE`.
4. `review-preregistration/**` must receive correct REUSE coverage before that path is introduced.
5. `candidate_id` must have a strict bounded lowercase-hex format before any path/ref interpolation.
6. Review reservation must use the preregistration PR as its observable substrate.
