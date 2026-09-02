# Village v1.3 `/next` Phase B transport specification independent review

TASK-ID: `AIMATH-VILLAGE-V1-3-NEXT-PHASE-B-TRANSPORT-SPEC-INDEPENDENT-REVIEW`

## Review target and fixed evidence

- Repository: `51mns/AIMath-public`
- Fresh current `main`: `df7ceb5e685239b936950a0dd01a13e4e38b69eb`
- Target branch: `design/village-v1-3-next-phase-b-transport-preflight`
- Fixed target commit: `c3532324e9df421afc787aa6cee3d91f8dbaa91e`
- Target artifact: `reviews/village-v1-3-next-phase-b-transport-preflight/PHASE_B_FROZEN_SPEC.md`
- Target blob: `5c877ec4d9807f285cb2e2c4c3f3ae3380117271`
- Parent `/next` frozen spec commit: `5eed8cc40243eba166afee651104f3c4a79d99ac`
- Parent spec blob: `ad851bd4fece0f3f45126ae12da3b54a3a7a5832`
- Historical Phase A review commit: `5fe2d40b100f885109addc2030d4a03f7d169e6b`
- Historical H-01: an unrelated same-worker/principal canonical lock could be mistaken for this `/next` epoch's `ACTIVE_NEXT`.

Fresh read-back found no target drift. The target branch resolves exactly to the fixed target, and the target commit is one commit ahead of the specified current-main base with exactly one changed path: the frozen Phase B design artifact.

## Verdict

**PASS_WITH_REQUIRED_CHANGES**

No CRITICAL or HIGH defect was found in the Phase B design. The design materially closes the historical H-01 class by binding source acquisition, post-RELEASE selection, deterministic ACQUIRE intent, expected lock bytes, and canonical read-back rather than accepting an arbitrary same-worker/principal lock.

However, one blocking MEDIUM specification gap remains: the final `ACTIVE_NEXT` proof stores exact PR/head/base identity in `ExpectedAcquireV1`, but does not freeze an implementation-level predicate proving that the exact expected transport PR/head is the transport that actually produced the canonical acquisition. The phrase `exact transport PR identity/head provenance where needed` is not strong enough for the requested unbroken evidence chain because canonical lock bytes intentionally do not contain `source_epoch_id`, `selection_id`, `continuation_context_id`, or the transport PR number/head SHA.

Phase B implementation therefore remains **NOT READY** after Phase A until this merge-provenance predicate and its adversarial tests are frozen and independently re-reviewed.

## Independent binding audit

### Source acquisition epoch

**PASS.** `SourceAcquisitionV1` binds repository, source Task, worker, authenticated principal, lock ID, acquired time, source lock base SHA, work ref, complete collision-key set, exact canonical lock path/blob bundle, terminal class, terminal path/blob, and terminal outcome type. The blob bundle indirectly binds mutable lock fields such as expiry/renewal state as bytes.

Old-source replay is fail-closed: after RELEASE, the source epoch must be carried or reconstructed and proved against exact RELEASE history; arbitrary historical locks, worker IDs, Task IDs, chat memory, or old PRs cannot manufacture an epoch.

### Terminal binding

**PASS.** Terminal class/path/blob are inside the source epoch. A changed terminal blob is therefore a different epoch. The Phase B test matrix explicitly includes terminal-blob change after epoch capture.

### Fresh post-RELEASE barrier

**PASS.** RELEASE and ACQUIRE are explicitly non-atomic. After canonical RELEASE the old pre-RELEASE snapshot is discarded, and selection requires a fresh main SHA, exact absence of the released source bundle, exact source-epoch RELEASE provenance, no newer source acquisition masquerade, valid current Village state, fresh direct-GitHub PENDING observations, and fresh continuation inputs.

### Continuation context

**PASS.** `ContinuationContextV1` binds the source epoch, selection main, terminal evidence, Campaign/global scheduling state, human continuation decision identity/blob, follow-up sets, deterministic reasons, and capability profile. Grant-capable scheduling state is not accepted from caller prose; the two advisory booleans called out in the design may only restrict scheduling and must be derived from canonical/fresh data.

### Deterministic Task selection

**PASS.** `SelectionV1` binds source epoch, post-RELEASE main, continuation context, validated PENDING observation digest, complete hard-eligible Task set, deterministic ranked order, selected Task/relation, worker, and principal. Main, decision, PENDING, eligibility, or ranking movement invalidates selection authority.

### `selection_id`

**PASS.** Canonical SHA-256 encoding is frozen and set-like inputs are sorted while ranking order is preserved.

### Deterministic ACQUIRE intent

**PASS.** `AcquireIntentV1` binds source epoch, selection, selection main, continuation context, selected Task, worker/principal, deterministic work ref, and exact collision-key set. The physical ref includes the full intent digest, Task, and worker, making equivalent retries converge and different intents diverge.

### Exact work ref / collision bundle

**PASS.** `work_ref = research/<TASK>/<worker>` is frozen to the existing workspace rule. The collision set must equal the selected Task's current canonical collision-key set exactly and must materialize as exactly one canonical lock file per collision key.

### Lock ID / first-creator timestamp

**PASS.** The lock ID is deterministic from the acquire intent. The first successful creator captures one whole-second UTC `acquired_at`, which becomes immutable for retries; duplicate creators must adopt the winner's exact payload. Same deterministic identity with different bytes fails closed.

### Exact PR/head/base / Verify binding

**PARTIAL — blocking MEDIUM below.** The expected record correctly stores PR number, head ref, exact head SHA, transport base SHA, acquire base SHA and exact-head Verify run identity. Head movement invalidates prior CI, and the latest numeric run ID for the exact head controls the observed Verify state.

The unresolved issue is not missing fields; it is the final proof relation from those fields to the canonical merge.

### Canonical lock read-back

**PASS for bytes/object identity.** `ACTIVE_NEXT` requires a new current-main read, exact active canonical path set, exact collision/work-ref/lock identity, acquisition times, and byte/blob equality with the expected transport bundle. A later renewal/replacement/reacquisition with changed blob, lock ID, acquisition time, collision set, or work ref is explicitly a different acquisition.

## MEDIUM findings

### M-01 — Exact expected transport merge provenance is under-specified

**Severity:** MEDIUM, blocking  
**Area:** `ACTIVE_NEXT`, exact PR/head/base binding, replay/substitution

`ExpectedAcquireV1` captures:

- `transport_pr_number`;
- `transport_head_ref`;
- `transport_head_sha`;
- `transport_base_sha`;
- exact expected lock blob bundle;
- exact-head Verify run identity.

Section 11 then requires `exact transport PR identity/head provenance where needed to prove which acquisition the request expected`, but does not freeze a concrete fresh-GitHub predicate proving that the canonical acquisition was introduced by that exact expected PR/head.

This matters because the canonical lock payload intentionally contains no `/next`-specific `source_epoch_id`, `selection_id`, `continuation_context_id`, `acquire_intent_id`, or PR identity. The trusted v1.2.1 lifecycle also accepts any independently valid same-repository lock-only ACQUIRE PR after current-main, exact-head CI, collision, capacity, object and policy revalidation; its authority is deliberately not derived from the `/next` ref name.

A concrete substitution case is therefore left ambiguous by the frozen text:

1. `/next` creates expected transport PR **A** and records exact expected payload **P**.
2. Before A merges, another authorized same-repository ACQUIRE PR **B** is created with byte-identical canonical lock payload P but a different PR/head provenance.
3. The trusted lifecycle may merge B first if B is the eligible candidate selected by its inherited ordering.
4. Current main now contains exactly the expected lock blobs P.
5. A Phase B implementation that interprets `where needed` as blob equality only could return `ACTIVE_NEXT` for A even though A never merged.

The lock bytes are equivalent, but the review task explicitly requires exact PR/head/base binding and an unbroken evidence chain from this `/next` request to the canonical acquisition. The specification must therefore choose and freeze one meaning rather than leave it to implementation.

**Required change:** before `ACTIVE_NEXT`, freeze a concrete merge-provenance predicate that fresh-observes the expected transport PR and proves that the exact expected PR/head was the successful canonical ACQUIRE transport. At minimum the proof must bind the expected PR number, same-repository head ref, exact head SHA, expected base/selection SHA, merged state, and a server-observed merge result/main-history relation sufficient to prove that this exact head produced the canonical expected lock bundle. A different PR/head with byte-identical payload must either be explicitly defined as non-equivalent and rejected (recommended for this task), or the higher-level contract must explicitly relax the requested exact-PR requirement and justify equivalence; the current frozen text does neither.

This can be implemented entirely in the Phase B orchestration/read-back layer. It does **not** require adding `/next` fields to canonical lock payloads, weakening `scripts/lock_auto_activate.py`, adding secrets/PATs, or changing repository settings.

## LOW findings

### L-01 — The 50-test table is not padded, but several requested transport/replay controls are not explicit

The 50 numbered rows are substantively distinct; no duplicate rows were found that merely pad the count. The matrix has a positive end-to-end happy path, negative exact-binding controls, stale-main/head/base controls, fail-closed observation controls, collision/capacity races, PENDING-vs-ownership controls, and H-01-specific old/unrelated acquisition controls.

However, the following should be added to the reviewed Phase B acceptance set:

1. **Byte-identical alternate-PR substitution:** expected PR A exists, different PR/head B carries byte-identical expected lock payload and is merged; A must not obtain `ACTIVE_NEXT` under the exact-PR contract. This is the mandatory regression for M-01.
2. **Webhook replay authority:** replayed/stale webhook payload is trigger-only; a fresh GitHub observation is always rederived, and an old source epoch cannot reuse webhook fields as authority.
3. **Multiple eligible RELEASE candidates:** preserve the inherited deterministic same-class ordering and prove one valid lower/earlier candidate is selected while malformed candidates cannot block later valid candidates. The current v1.2.1 suite already has a RELEASE-order regression, but the Phase B acceptance matrix should pin the inherited behaviour it relies on.
4. **Multiple eligible ACQUIRE candidates:** pin the inherited deterministic same-class ordering independently of RELEASE priority and prove at most one canonical mutation.
5. **Same exact head, later Verify rerun is non-success:** an earlier exact-head green run must not remain authoritative when the latest numeric run ID for the same head is failed/cancelled/in-progress. The prose specifies this, but the 50 rows only cover red/missing CI and moved-head CI generically.

These test additions do not reveal a separate authority flaw beyond M-01, but they are required to make the preregistered security suite match the full threat list in this review task.

## Idempotency and replay

**IDEMPOTENCY: PASS.** Duplicate `/next`, transient retry, equivalent existing RELEASE/ACQUIRE PR, existing deterministic ref, already RELEASED, already ACQUIRE-merged, main movement, candidate disappearance, and head movement all have state-derived reuse/recompute semantics. Equivalent objects are reused; same deterministic identity with inconsistent bytes/identity fails closed rather than overwriting.

**REPLAY: PASS except M-01 exact-transport provenance ambiguity.** Source epoch replay, newer reacquisition, later independent acquisition with changed lock identity, stale terminal/blob and old source lock bundle are explicitly rejected.

## Race model

- **Two workers same Task:** PASS; canonical merge winner owns, loser refreshes/reranks.
- **Two workers same collision:** PASS; first canonical collision owner wins.
- **Campaign last slot:** PASS; canonical merge consumes capacity, later candidate fails fresh revalidation.
- **Global last slot:** PASS.
- **RELEASE + ACQUIRE simultaneously eligible:** PASS; RELEASE wins.
- **At most one canonical mutation per trusted run:** PASS.
- **Multiple eligible RELEASE:** inherited trusted lifecycle deterministically orders eligible releases by PR number; target should add an explicit Phase B regression as L-01.
- **Multiple eligible ACQUIRE:** inherited lifecycle deterministically orders eligible acquires by PR number; target should add an explicit Phase B regression as L-01.
- **Candidate-local malformed observation:** PASS; candidate is dropped without becoming reservation authority.
- **Repository-wide incomplete observation:** PASS; whole orchestration run fails closed.
- **Duplicate deterministic transport creators:** PASS; create-if-absent winner is adopted only when exact; non-equivalent collision is not overwritten.

Canonical merge remains final ownership authority throughout.

## Trust-boundary audit

**PASS.** The design does not move Task selection, strict Ruleset decision, canonical merge authority, canonical ownership, Truth Layer, I2/I3, review promotion, RENEW or TAKEOVER into untrusted PR-head authority.

`scripts/lock_auto_activate.py` remains a narrow trusted-main lifecycle primitive. Current main independently confirms the inherited controls relied on by the design: fresh main/state loading, exact Git object checks, current exact-head Verify, candidate-local observation isolation, RELEASE-before-ACQUIRE ordering, strict effective ruleset proof, final main/head/base revalidation, and one merge attempt followed by return.

No new PAT/secret or repository/workflow setting change is required by the Phase B contract.

## Phase A / Phase B boundary

**PASS.** The frozen Phase B design explicitly refuses to assume that PR #34 or any Phase A remediation has passed. Phase B implementation is gated on a separately accepted fixed Phase A PASS closing H-01 and expired-source-lock handling. Phase A remains read-only/pure and may produce transport intent only; Phase B performs fresh GitHub observation, transport, exact canonical acquisition proof and then `ACTIVE_NEXT`.

The historical rejected shortcut — treating any unrelated same-worker/principal canonical lock as `ACTIVE_NEXT` — is not accepted by this Phase B design.

## Parent frozen-spec compatibility

**PASS.** The parent spec defines `/next` as terminalisation -> RELEASE -> fresh selection -> ACQUIRE -> canonical `ACTIVE_NEXT`, with canonical lock as ownership authority, PENDING as non-ownership, deterministic ranking, fresh GitHub observations, trusted lifecycle handoff, RELEASE priority and one canonical mutation per trusted run.

The Phase B target is a strict refinement of that model: it makes the parent request epoch, transport identity and final active-lock equality substantially more explicit. No parent authority boundary is weakened.

## 50 preregistered tests audit

- Declared rows: **50**.
- Meaningful duplicate/padding rows: **0 found**.
- Positive happy path: **present**.
- Negative `ACTIVE_NEXT` exact-binding controls: **present**.
- Fail-closed repository observation controls: **present**.
- Candidate-local failure isolation: **present**.
- Main/head/base stale controls: **present**.
- Old epoch / newer reacquisition / later independent acquisition replay controls: **present**.
- Collision/capacity/RELEASE-priority/one-mutation races: **present**.
- PENDING != ownership / Truth / I2-I3 / no RENEW-TAKEOVER controls: **present**.
- Missing explicit tests: **5**, listed in L-01; the first is mandatory to close M-01.

## Severity summary

### CRITICAL

None.

### HIGH

None.

### MEDIUM

- **M-01 blocking:** exact expected transport PR/head -> canonical merge provenance is not frozen as a concrete proof predicate.

### LOW

- **L-01:** preregistered 50-test matrix omits several explicit transport/replay regressions required by the threat list; no padding found.

## Final readiness

`READY_FOR_PHASE_B_IMPLEMENTATION_AFTER_PHASE_A = NO` at this fixed design target.

Required sequence:

1. keep Phase A independently gated; do not assume remediation PASS;
2. amend/freeze the Phase B design with an exact expected-PR/head canonical merge-provenance predicate;
3. add the M-01 substitution regression and the remaining L-01 transport/replay regressions to the required acceptance matrix;
4. freeze a new design commit/blob and perform a focused independent re-review;
5. only after both accepted Phase A PASS and accepted revised Phase B spec review may the implementation writer begin.

No production code, workflow, settings, locks, PR lifecycle state, target design artifact, Truth state, or files outside this review lane were modified by this review.

Signed-off-by: Shoma Nakabayashi <199666487+51mns@users.noreply.github.com>
