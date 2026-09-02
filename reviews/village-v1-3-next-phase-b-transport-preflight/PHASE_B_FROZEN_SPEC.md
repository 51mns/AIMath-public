# Village v1.3 `/next` Phase B transport frozen specification

TASK-ID: `AIMATH-VILLAGE-V1-3-NEXT-PHASE-B-TRANSPORT-PREFLIGHT`

Status: **FROZEN DESIGN CONTRACT / IMPLEMENTATION GATED ON ACCEPTED PHASE A PASS**

Repository: `51mns/AIMath-public`

Frozen design base / current-main preflight SHA:

```text
df7ceb5e685239b936950a0dd01a13e4e38b69eb
```

Parent `/next` frozen specification:

```text
commit 5eed8cc40243eba166afee651104f3c4a79d99ac
path   reviews/village-v1-3-next-preflight/NEXT_FROZEN_SPEC.md
blob   ad851bd4fece0f3f45126ae12da3b54a3a7a5832
```

Phase A review input:

```text
review commit 5fe2d40b100f885109addc2030d4a03f7d169e6b
H-01: ACTIVE_NEXT must not be inferred from an arbitrary same-worker/principal lock.
M-01: expired source lock must not be treated as live ownership.
```

This document freezes the Phase B GitHub transport contract only. It changes no production code, workflow, lock, PR, repository setting, Campaign, Task, claim, review, or Truth state.

## 1. Implementation gate and non-assumptions

Phase B implementation MUST NOT start from an assumption that PR #34 or any Phase A remediation has passed.

The implementation writer may start only after a fixed Phase A target has an accepted independent PASS which closes all required Phase A findings. At minimum the accepted boundary must make the following true:

1. an unrelated canonical lock cannot short-circuit continuation selection into `ACTIVE_NEXT`;
2. `ACTIVE_NEXT` can consume the exact expected-acquisition binding defined in this document, or Phase A otherwise proves the same exact binding;
3. expired/stale source lock artifacts are not reported as current ownership;
4. Phase A remains pure/read-only and has no GitHub mutation authority.

If the accepted Phase A interface differs syntactically from PR #34, the Phase B writer may adapt names only. The authority and equality requirements in this document are frozen and MUST NOT be weakened.

## 2. Inherited authority boundary

Phase B is orchestration and transport, not a new canonical mutation authority.

The following v1.2.1 boundaries are inherited unchanged:

- merged canonical lock bundles are the only EXCLUSIVE ownership authority;
- `PENDING_CLAIM` is a temporary scheduling reservation, never ownership;
- trusted current-default-branch code is the only automatic lock merge authority;
- PR-head code/data is never write authority;
- successful PR-head CI is a prerequisite signal, never authority by itself;
- `eligible RELEASE > eligible ACQUIRE`;
- at most one trusted canonical lifecycle mutation per trusted run;
- exact current-main/head/base revalidation is required immediately before merge;
- exact regular Git object mode `100644` / blob identity gates remain required;
- candidate-local observation/shape failures fail that candidate only;
- repository-wide prerequisite observation failures fail the whole orchestration run closed;
- automatic `RENEW` and `TAKEOVER` remain forbidden;
- no Truth promotion, no automatic I2/I3, no writer self-review promotion;
- Task/Campaign creation or strategic continuation remains governance authority, not `/next` authority.

Phase B MUST NOT put Task selection, branch/PR creation, review selection, or Truth logic inside `scripts/lock_auto_activate.py`. The existing trusted lifecycle remains a narrow current-main mutation primitive.

## 3. Canonical encodings and identities

Every digest defined here uses the same encoding:

```text
UTF-8 JSON
sort_keys = true
separators = (",", ":")
ensure_ascii = false
SHA-256 lowercase hexadecimal, 64 characters
```

Digests are non-secret correlation identities, not credentials.

Lists whose semantics are sets, especially collision keys and bundle paths, MUST be sorted lexicographically before hashing. Ordered ranking lists MUST preserve their deterministic ranking order.

### 3.1 Exact Git blob bundle identity

For a canonical lock bundle, define:

```text
lock_blob_bundle = [
  {"path": <repo-relative path>, "blob_sha": <40-hex Git blob OID>},
  ...
]
```

sorted by `path`.

The bundle is exact only when:

- the set of paths equals `coordination/locks/<collision-key>.yml` for the complete canonical collision-key bundle;
- every entry is a regular `100644` Git blob in the exact observed tree;
- every blob decodes to the same lock payload / same `lock_id` bundle;
- the collision-key set in the payload equals the path-derived key set exactly.

### 3.2 Source acquisition identity

A `/next` epoch for an EXCLUSIVE source acquisition is exactly:

```text
SourceAcquisitionV1 = {
  "repository": "51mns/AIMath-public",
  "source_task_id": ...,
  "worker_id": ...,
  "principal_id": "gh:<login>",
  "source_lock_id": ...,
  "source_lock_acquired_at": ...,
  "source_lock_base_main_sha": ...,
  "source_work_ref": ...,
  "source_collision_keys": [...sorted...],
  "source_lock_blob_bundle": [...sorted path/blob pairs...],
  "terminal_class": "RESULT_TERMINAL" | "ABANDONED_TERMINAL",
  "terminal_path": ...,
  "terminal_blob_sha": <40-hex Git blob OID>,
  "terminal_outcome_type": <exact outcome_type or null>
}
```

`source_epoch_id = SHA256(canonical(SourceAcquisitionV1))`.

The source epoch is valid only if it was derived while the exact source acquisition was observable from canonical Git objects. Caller prose, chat memory, a worker ID alone, a Task ID alone, or an old release PR alone cannot manufacture it.

A retry after canonical RELEASE MUST carry or reconstruct this exact source epoch and then prove it against the exact RELEASE transport/history described below. If source ownership is already absent and no exact source-epoch proof is available, `/next` fails closed with `SOURCE_EPOCH_UNPROVEN`; it does not infer an epoch from arbitrary historical locks or PRs.

### 3.3 Continuation decision context

Phase B MUST bind the accepted Phase A result, not merely the selected Task string.

Define `ContinuationContextV1` from the exact accepted Phase A output and the canonical/fresh inputs that can grant or restrict scheduling. It MUST contain at least:

```text
{
  "source_epoch_id": ...,
  "selection_main_sha": ...,
  "terminal_class": ...,
  "terminal_blob_sha": ...,
  "source_campaign_id": ...,
  "global_admission": ...,
  "source_campaign_strategic_state": ...,
  "continuation_gate_required": true|false,
  "continuation_decision_id": <id or null>,
  "continuation_decision_blob_sha": <Git blob OID or null>,
  "human_decision": <CONTINUE/PIVOT/HOLD/CLOSE/etc or null>,
  "canonical_stop_condition_reached": true|false,
  "canonical_dependency_followup_unusable": true|false,
  "same_campaign_allowed": true|false,
  "global_fallback_allowed": true|false,
  "approved_followup_task_ids": [...sorted...],
  "evaluation_followup_task_ids": [...sorted...],
  "reasons": [...exact deterministic Phase A reasons...],
  "capability_profile": {
    "github_write": true|false|null,
    "local_compute": true|false|null,
    "web_literature": true|false|null
  }
}
```

The two advisory-looking booleans `canonical_stop_condition_reached` and `canonical_dependency_followup_unusable` MUST be derived by the transport/orchestration adapter from canonical/fresh data. They MUST NOT be accepted as grant-capable caller assertions. They may only restrict scheduling.

`continuation_context_id = SHA256(canonical(ContinuationContextV1))`.

### 3.4 Selection identity

The selected next Task is bound to the fresh post-RELEASE observation:

```text
SelectionV1 = {
  "source_epoch_id": ...,
  "selection_main_sha": ...,
  "continuation_context_id": ...,
  "pending_observation_digest": ...,
  "hard_eligible_task_ids": [...sorted...],
  "ranked_task_ids": [...deterministic order...],
  "selected_task_id": ...,
  "selected_relation": ...,
  "worker_id": ...,
  "principal_id": ...
}
```

`pending_observation_digest` hashes the validated direct-GitHub reservation rows that were actually supplied to Phase A selection, including PR number, exact head SHA, base main SHA, Task, worker/principal, collision keys and exact CI conclusion fields. Invalid rows are not included as valid reservations.

`selection_id = SHA256(canonical(SelectionV1))`.

If main, applicable canonical decision state, validated pending reservations, candidate eligibility, or deterministic rank changes before ACQUIRE transport creation, the selection loses authority and MUST be recomputed.

## 4. Fresh GitHub observation contract

A Phase B run starts with a fresh direct GitHub observation. No repository cache, previous chat result, locally remembered PR status, or earlier webhook payload is authoritative.

Repository-wide prerequisites include at minimum:

- current `refs/heads/main` full SHA;
- exact current-main Git tree required to validate canonical lock blob identities;
- current canonical Village state from that exact main;
- authenticated GitHub principal;
- complete bounded open-PR observation for base `main` needed for RELEASE/ACQUIRE transport discovery and PENDING reservations;
- exact PR metadata/files for any transport considered for reuse;
- exact-head Verify observations for any transport considered actionable;
- effective strict rules when mutation readiness is being assessed.

If any repository-wide prerequisite response is unavailable, malformed, truncated beyond the reviewed bound, or internally inconsistent, return a retryable fail-closed status and perform no transport creation/update based on cached data.

A failure decoding one candidate PR after the repository-wide open-PR list is valid is candidate-local: mark only that candidate ineligible and continue examining later candidates. Candidate-local failure MUST NOT become reservation authority or block a later valid candidate.

## 5. RELEASE transport contract

### 5.1 Deterministic physical identity

The inherited physical RELEASE ref remains exactly:

```text
release/<SOURCE-TASK-ID>/<worker-id>
```

No epoch suffix is added because the v1.2.1 trusted RELEASE parser already freezes this ref shape.

The logical RELEASE key is `source_epoch_id`, not merely the ref name.

The intended RELEASE tree is exactly `current_main_tree - source_lock_blob_bundle`, with no other change.

### 5.2 Create / reuse / repair

For a source lock still canonically active and exactly equal to `SourceAcquisitionV1`:

1. fresh-read current main and the complete source lock bundle;
2. prove exact source Task/worker/principal/lock-id/acquired-at/work-ref/collision/path/blob equality;
3. prove current terminal evidence still matches the source epoch and is RELEASE-eligible;
4. inspect the deterministic RELEASE ref and relevant open PR;
5. if an open PR already has the exact ref, same repository, expected principal, current base main, exact deletion set, exact base lock blobs and exact intended head tree, REUSE it;
6. if the same ref has a stale PR that is provably the same source epoch but stale only because main moved, it is repairable by rebuilding the ref from the new current main **only after** fresh compare-before-write revalidation of the observed old head; any head change invalidates old CI and requires a new exact-head Verify;
7. if the same ref/PR is unrelated, malformed, belongs to another epoch, changes anything outside the exact source lock bundle, or cannot be proved equivalent, fail `RELEASE_TRANSPORT_CONFLICT` and do not overwrite it;
8. creating or repairing the worker transport ref/PR is not canonical ownership mutation and grants no ownership authority.

An old source-epoch RELEASE PR MUST NEVER be retargeted to delete a newer reacquisition whose `lock_id`, `acquired_at`, base, work-ref, collision bundle or blob bundle differs.

### 5.3 Existing RELEASE PR and already RELEASED

If an equivalent RELEASE PR already exists, duplicate `/next`, retry and webhook replay reuse it.

If current main proves the exact source bundle absent, Phase B does not recreate RELEASE. It may advance past `RELEASED` only when it also has exact provenance that the retained source epoch was released: a merged RELEASE transport/history whose base contained the exact source lock blob bundle and whose change removed exactly that bundle.

If a newer source acquisition is now canonical for the same Task/worker/principal but differs from `source_epoch_id`, the old request is `OLD_ACQUISITION_REPLAY` and stops. It cannot release, select for, or otherwise control the newer acquisition.

## 6. Post-RELEASE fresh-main barrier

RELEASE and ACQUIRE are never one atomic `/next` mutation.

After RELEASE becomes canonical, Phase B MUST perform a new repository-wide observation. The old pre-RELEASE snapshot is discarded for Task selection.

The post-RELEASE barrier requires all of:

- a fresh current main SHA;
- exact absence of the released source lock bundle;
- exact source-epoch RELEASE provenance as above;
- no newer source acquisition masquerading as the old epoch;
- valid current Village state;
- fresh direct GitHub PENDING observations;
- fresh canonical continuation inputs.

Only then may accepted Phase A derivation compute the deterministic next Task.

## 7. Deterministic ACQUIRE transport

### 7.1 Deterministic workspace and collision bundle

For selected Task `T` and retained worker `W`:

```text
work_ref = research/<T>/<W>
```

exactly as v1.2 `worker_workspace()` defines.

The collision-key bundle MUST equal the selected Task's current canonical `collision_keys` set exactly, sorted for hashing and represented by exactly one lock file per collision key.

### 7.2 Acquire intent

Define:

```text
AcquireIntentV1 = {
  "repository": "51mns/AIMath-public",
  "source_epoch_id": ...,
  "selection_id": ...,
  "selection_main_sha": ...,
  "continuation_context_id": ...,
  "selected_task_id": ...,
  "worker_id": ...,
  "principal_id": ...,
  "work_ref": ...,
  "collision_keys": [...sorted...]
}
```

`acquire_intent_id = SHA256(canonical(AcquireIntentV1))`.

The deterministic ACQUIRE transport ref is frozen as:

```text
next-acquire/<acquire_intent_id>/<TASK-ID>/<worker-id>
```

The v1.2.1 trusted ACQUIRE path does not grant authority from the ref name; the ref exists only to make transport creation/reuse idempotent and epoch-specific.

### 7.3 Deterministic lock payload

For a newly materialized intent, the first successful creator captures one UTC `acquired_at` timestamp at whole-second precision. That timestamp is then immutable for retries of the same transport. A competing duplicate creator that finds the deterministic ref already created MUST adopt the existing valid payload; it MUST NOT regenerate a different timestamp.

`expires_at` is deterministically derived from `acquired_at + current canonical Task lease_ttl_hours`.

The lock id is:

```text
LOCK-NEXT-<first 32 uppercase hex characters of acquire_intent_id>
```

The lock payload MUST include at least:

- schema version;
- deterministic `lock_id`;
- selected `task_id`;
- retained `worker_id`;
- authenticated `actor.id = principal_id` and valid actor type;
- `base_main_sha = selection_main_sha`;
- immutable `acquired_at`;
- derived `expires_at`;
- exact deterministic `work_ref`;
- exact collision-key bundle;
- `renewal_count = 0`.

The same payload is serialized in the repository's JSON-subset `.yml` format with deterministic JSON formatting (`sort_keys=true`, indent 2, trailing newline) into every required collision-key lock path.

No `/next` field, score, review grade, Truth state, or chat-derived value is added to canonical lock authority.

### 7.4 ACQUIRE transport create/reuse

Before creating or reusing ACQUIRE transport, fresh-revalidate that the selected Task remains eligible on `selection_main_sha` and that the fresh observation still matches `SelectionV1`.

- If the deterministic ref and an open PR exist and the PR is same-repository, open, non-draft, based on `selection_main_sha`, created by the expected principal, and adds exactly the expected lock blob bundle with the exact payload, REUSE it.
- If the deterministic ref exists with exactly the expected valid head but no PR exists, create at most one PR from that ref after a fresh duplicate search.
- If the deterministic ref/PR exists but content, principal, Task, worker, base, work-ref, collision bundle, lock-id or payload timestamp is inconsistent, fail `ACQUIRE_TRANSPORT_KEY_COLLISION`; do not overwrite or adopt it.
- If main moved before transport creation, discard the selection and recompute. The new `selection_main_sha` produces a new `selection_id` / `acquire_intent_id` / ref.
- A disappeared/closed candidate or newly valid reservation causes rerank/recompute, not repair of an obsolete acquire intent.

An open/green ACQUIRE PR is `ACQUIRE_PENDING`, never ownership.

## 8. Exact-head CI observation

An ACQUIRE or RELEASE transport is CI-valid only when its **current exact head SHA** has a `Verify public release` workflow run with:

```text
name       = "Verify public release"
event      = "pull_request"
head_sha   = exact current PR head SHA
status     = "completed"
conclusion = "success"
```

If multiple matching runs exist for the exact head, the latest run by numeric run ID is authoritative for the observed CI state, matching the inherited lifecycle behaviour.

A green run for an earlier head does not transfer to a moved head. Head movement after observation returns to pending/retry and requires a fresh exact-head successful run.

CI red/missing gives no valid PENDING reservation, no trusted lifecycle eligibility, and no `ACTIVE_NEXT`.

## 9. Trusted lifecycle handoff

Phase B creates/reuses transport only. It does not merge canonical locks itself.

A transport is handed off to the existing v1.2.1 trusted lifecycle. That lifecycle independently rederives current main, Village state, exact Git object identity, PR shape, exact-head CI, readiness, collision, worker, Campaign/global capacity, final head/base/main stability, and strict effective branch rules.

Phase B MUST NOT treat a transport as guaranteed to merge merely because it was locally valid when created.

If strict effective Ruleset evidence is unavailable, malformed, does not prove strict required status checks, or lacks required context `verify`, automatic merge remains globally fail-closed. The transport may remain pending but `/next` does not claim ownership.

`eligible RELEASE > eligible ACQUIRE` and at-most-one trusted canonical lifecycle mutation per run remain global properties. If a RELEASE and this `/next` ACQUIRE are simultaneously eligible, the RELEASE wins; ACQUIRE must wait for a later trusted run and fresh revalidation.

## 10. Expected ACQUIRE identity and canonical read-back

After an ACQUIRE transport exists, Phase B constructs an immutable expected acquisition record from the exact transport head:

```text
ExpectedAcquireV1 = {
  "source_epoch_id": ...,
  "selection_id": ...,
  "continuation_context_id": ...,
  "selected_task_id": ...,
  "worker_id": ...,
  "principal_id": ...,
  "work_ref": ...,
  "collision_keys": [...sorted...],
  "lock_id": ...,
  "acquire_base_main_sha": ...,
  "acquired_at": ...,
  "expires_at": ...,
  "expected_lock_blob_bundle": [...path/blob pairs from exact PR head...],
  "transport_pr_number": ...,
  "transport_head_ref": ...,
  "transport_head_sha": ...,
  "transport_base_sha": ...,
  "verify_run_id": <exact-head successful run id or null until green>
}
```

`expected_acquire_id = SHA256(canonical(ExpectedAcquireV1 without verify_run_id if not yet green; once green, bind the exact successful run separately))`.

The expected record is not ownership. It is the equality target for canonical read-back.

## 11. ACTIVE_NEXT proof — exact binding required

`ACTIVE_NEXT` may be returned **only** after a new fresh read of current `main` proves exactly one active canonical lock bundle satisfying every equality below.

The canonical lock MUST match the expected acquisition on:

1. source acquisition identity / `source_epoch_id` provenance;
2. selected next Task ID;
3. retained `worker_id`;
4. authenticated `principal_id`;
5. deterministic `work_ref`;
6. exact complete collision-key bundle;
7. exact deterministic ACQUIRE `lock_id`;
8. exact ACQUIRE `base_main_sha`;
9. exact `acquired_at` and `expires_at` from the expected transport payload;
10. exact canonical lock path set;
11. exact canonical lock blob contents corresponding to the expected transport lock payload;
12. exact selected continuation decision context / `continuation_context_id` and `selection_id` that generated the transport;
13. exact transport PR identity/head provenance where needed to prove which acquisition the request expected.

The canonical Git blob OIDs on later `main` need not equal the PR-head OIDs only if a separately reviewed canonicalization layer intentionally rewrites bytes. No such layer exists in the frozen v1.2.1 design, so Phase B v1.3 MUST require byte/blob equality with the expected transport lock blobs.

Main may advance after the ACQUIRE merge. `ACTIVE_NEXT` remains valid only while the exact expected active lock bundle is still canonical and active. A later independent acquisition, renewal, replacement, changed blob bundle, changed lock ID, changed acquisition time, or changed collision/work-ref identity is a different acquisition and does not satisfy the old expected record.

An unrelated old canonical lock, even with the same Task, same worker and same principal, MUST NOT satisfy `ACTIVE_NEXT` unless every exact expected-acquisition field above matches.

If a canonical lock exists for the worker/principal but does not exactly match the expected acquisition, return a mismatch/replay/fail-closed result; never reinterpret it as this `/next`'s success.

## 12. Idempotency state table

Idempotency is state-derived, not chat-derived.

| Situation | Frozen behaviour |
|---|---|
| duplicate `/next` same source epoch | reuse exact equivalent RELEASE/ACQUIRE transport; never create a second equivalent PR/bundle |
| retry after transient GitHub failure | fresh repository-wide observation; reuse exact transport if still equivalent |
| webhook replay | payload is only a trigger; rederive everything from GitHub/current main; same epoch reuses, old epoch stops |
| old acquisition replay | exact source epoch mismatch => `OLD_ACQUISITION_REPLAY`; no release/select/acquire authority |
| existing equivalent RELEASE PR | reuse; do not duplicate |
| stale but same-epoch RELEASE after main movement | rebuild only under the bounded same-epoch compare-before-write repair rule; old CI invalidated |
| unrelated/conflicting RELEASE ref/PR | `RELEASE_TRANSPORT_CONFLICT`; no overwrite |
| already RELEASED | do not recreate release; require exact merged release provenance for the retained source epoch, then fresh post-release selection |
| existing equivalent ACQUIRE PR | reuse |
| deterministic ACQUIRE ref exists, PR absent | verify exact payload, fresh duplicate search, create at most one PR |
| ACQUIRE already merged and exact expected lock canonical | exact read-back => `ACTIVE_NEXT` |
| ACQUIRE merged but lock is not expected acquisition | never `ACTIVE_NEXT`; report acquisition mismatch/replay |
| main movement before selection/ACQUIRE creation | discard selection, fresh observe, rerank, new intent/ref |
| main movement after PR creation before merge | trusted lifecycle rejects stale base; rerun from fresh selection if still needed |
| PR head movement | old CI and expected head invalid; fresh-read/reverify; if intent payload changes, reject/recompute |
| CI failure/no exact-head success | no valid reservation, no activation, no `ACTIVE_NEXT` |
| candidate disappears/closes | remove from fresh reservation/candidate set and rerank |
| later independent acquisition after old `/next` | old expected acquisition cannot match new lock; replay stops |

## 13. Race model

### 13.1 Two workers select the same Task

Both may compute the same Task from concurrent snapshots. Their acquire intents differ by worker/principal/source epoch. Neither owns it while pending. The first trusted canonical merge wins. The other transport becomes stale/ineligible on fresh revalidation and must rerank.

### 13.2 Two workers select colliding Tasks

Collision keys are exact lock-bundle authority. First canonical merge consumes the collision. Later candidate fails fresh collision revalidation even if its earlier CI was green.

### 13.3 Campaign/global last slot

No rank or open PR grants capacity. The first canonical merge that consumes the final slot wins. Every later candidate must fail current-main capacity revalidation and rerank.

### 13.4 RELEASE and ACQUIRE simultaneously eligible

RELEASE is selected first by the trusted lifecycle. The run returns after at most one canonical mutation. The ACQUIRE remains pending and must pass all gates again on a later run.

### 13.5 Duplicate creators for one deterministic transport

Deterministic refs plus fresh existence checks provide the idempotency key. Branch/ref creation is create-if-absent. If two creators race, only one creation may succeed; the loser fresh-reads and adopts the exact valid existing object. A pre-existing non-equivalent object at the deterministic key is a fail-closed collision, not something to overwrite.

### 13.6 Main/head races

Selection snapshots are advisory. Transport creation checks main again; trusted merge checks main/head/base again. Any movement removes earlier authority. Exact-head CI never floats across head movement.

## 14. Fail-closed model

Global fail-closed conditions include:

- current-main ref/tree unavailable or malformed;
- canonical Village state invalid;
- authenticated principal unavailable/invalid;
- bounded complete open-PR observation unavailable/truncated;
- fresh PENDING observation envelope cannot be established;
- accepted Phase A derivation unavailable/fails;
- required continuation authority record unavailable/malformed;
- strict effective Ruleset proof unavailable when automatic mutation readiness is assessed;
- selected candidate cannot be revalidated before transport creation;
- final expected acquisition cannot be read back exactly.

Candidate-local fail-closed conditions include malformed candidate PR metadata/files/tree, missing exact-head CI, stale base, unsafe/non-regular lock objects, or an individual disappeared PR. These remove only the candidate when the repository-wide substrate is otherwise trustworthy.

No failure mode authorizes fallback to remembered Task, first Task, random Task, self-selected Task, self-review, direct merge, `RENEW`, or `TAKEOVER`.

## 15. Preregistered Phase B acceptance/adversarial tests

The implementation writer MUST add deterministic tests for every row below. Each mutation-capable scenario asserts the absence of unauthorized canonical mutation as well as the positive result where applicable.

1. happy path: exact source epoch -> equivalent RELEASE create/reuse -> trusted release -> fresh post-release observation -> deterministic Phase A selection -> ACQUIRE create/reuse -> exact-head green -> trusted merge -> exact expected canonical read-back -> `ACTIVE_NEXT`.
2. unrelated same-worker/principal canonical lock never satisfies `ACTIVE_NEXT`.
3. same selected Task but old acquisition epoch / different lock-id or acquired-at never satisfies `ACTIVE_NEXT`.
4. exact selected Task with wrong `work_ref` fails `ACTIVE_NEXT`.
5. exact selected Task with wrong collision-key bundle fails `ACTIVE_NEXT`.
6. wrong worker fails release/acquire binding and `ACTIVE_NEXT`.
7. wrong principal fails release/acquire binding and `ACTIVE_NEXT`.
8. stale ACQUIRE base fails; no PENDING authority / merge / `ACTIVE_NEXT`.
9. stale RELEASE base cannot be reused as current; only same-epoch bounded repair may rebuild it and must require new CI.
10. stale PR head invalidates prior Verify and expected transport identity.
11. duplicate `/next` creates/reuses at most one equivalent RELEASE and one equivalent ACQUIRE transport.
12. duplicate creator race on deterministic ACQUIRE ref adopts the exact winner and never overwrites non-equivalent content.
13. old source acquisition replay after a newer reacquisition stops before release/select/acquire.
14. existing equivalent RELEASE PR is reused.
15. unrelated existing RELEASE ref/PR is conflict, not reused or overwritten.
16. already RELEASED source proceeds only with exact source-epoch release provenance and fresh main.
17. existing equivalent ACQUIRE PR is reused.
18. deterministic ACQUIRE ref with exact payload but no PR creates at most one PR.
19. ACQUIRE already merged with exact expected bundle yields `ACTIVE_NEXT`.
20. exact lock merged but not the expected acquisition does not yield `ACTIVE_NEXT`.
21. replay after a later independent acquisition does not yield `ACTIVE_NEXT`.
22. two workers same Task: only canonical merge winner owns; loser refreshes/reranks.
23. two workers with overlapping collision bundles: only first canonical collision owner succeeds.
24. Campaign last-slot race: first merge wins; second fails fresh capacity.
25. global last-slot race: first merge wins; second fails fresh capacity.
26. RELEASE and ACQUIRE simultaneously eligible: RELEASE wins and same trusted run does not merge ACQUIRE.
27. at-most-one trusted canonical lifecycle mutation per run.
28. strict Ruleset/effective-rule observation unavailable or malformed: no automatic merge and no ownership claim.
29. strict rules present but `strict=false` or required `verify` missing: no automatic merge.
30. exact-head CI red/missing: no valid reservation/activation.
31. older-head CI green + moved head: no activation until new exact-head success.
32. malformed candidate-local observation: candidate dropped; later valid candidate still examinable.
33. repository-wide open-PR/main/tree observation failure: global fail closed; no selection/transport mutation from cache.
34. candidate disappears/closes between observations: drop and rerank.
35. main moves after RELEASE and before selection: old selection not reused.
36. main moves after selection before ACQUIRE branch creation: recompute; old intent not created.
37. main moves after ACQUIRE PR creation: trusted lifecycle rejects stale base; old open PR is not ownership.
38. PENDING_CLAIM remains non-ownership even when open/green.
39. valid terminal result may release while review remains pending; no Truth promotion occurs.
40. no autonomous I2/I3, no writer self-review promotion.
41. no automatic RENEW/TAKEOVER path is emitted or handed to trusted lifecycle.
42. human Continuation Gate missing: no same-Campaign escalation; unrelated global READY selection follows accepted Phase A semantics only.
43. worker/self recommendation cannot create or approve a Task/Campaign.
44. selection context change (human decision blob, global admission, candidate set, PENDING set, capability input) changes/recomputes selection identity before ACQUIRE creation.
45. source terminal blob changes after epoch capture: old source epoch is not silently reused.
46. source lock blob bundle differs while Task/worker/principal are the same: old RELEASE request cannot act on it.
47. deterministic lock-id formula is stable for the same acquire intent and distinct for different acquire intents.
48. first creator timestamp is reused exactly by duplicate creators/retries of the same deterministic ACQUIRE ref.
49. exact canonical lock path/blob bundle read-back must equal the expected transport bundle.
50. canonical lock is expired at read-back: never `ACTIVE_NEXT`.

These Phase B tests supplement, not replace, the parent frozen Section 14 tests and the accepted Phase A test suite.

## 16. Severity review for this preflight

### CRITICAL

None discovered in this design preflight.

### HIGH

No new inherited HIGH discovered beyond the already-known Phase A H-01. H-01 is explicitly treated as an implementation start blocker and is closed architecturally here by making exact expected-acquisition equality the only `ACTIVE_NEXT` proof.

### MEDIUM

The known Phase A M-01 (expired source lock treated as live ownership) is not promoted or ignored here. Phase B requires accepted Phase A PASS and independently requires active canonical read-back for ownership/`ACTIVE_NEXT`.

### LOW

None newly required for this transport contract.

## 17. Writer implementation decomposition

After accepted Phase A PASS, the implementation writer should be able to implement without redesign by separating:

1. fresh GitHub observation adapter;
2. source-epoch / continuation / selection identity builder;
3. RELEASE transport reconciler using the inherited release ref;
4. post-RELEASE fresh-main barrier;
5. deterministic ACQUIRE payload/ref/PR builder;
6. exact-head CI observer and PENDING adapter;
7. handoff-only integration with existing trusted lifecycle;
8. expected-acquisition canonical read-back verifier;
9. adversarial/idempotency/race tests.

Production mutation code MUST remain outside the trusted lifecycle except for already-reviewed lifecycle calls/handoff. Any proposal to move selection or transport creation into the trusted writer, broaden workflow permissions, add a PAT/secret, change Ruleset semantics, or add Truth/review authority requires a new design/security review rather than an implementation shortcut.

## 18. Done / stop boundary

This frozen design is complete when an accepted Phase A PASS exists and a writer can implement the nine components above directly from this contract.

Stop and return to design/security review if implementation would require:

- production semantics outside this contract;
- assuming Phase A remediation rather than consuming an accepted fixed Phase A target;
- a new CRITICAL/HIGH inherited defect;
- Truth/review authority expansion;
- automatic RENEW/TAKEOVER;
- weakening trusted-main, exact-head CI, strict Ruleset, object, collision, capacity, or canonical ownership boundaries.

Frozen implementation readiness result:

```text
READY_FOR_PHASE_B_IMPLEMENTATION_AFTER_PHASE_A = YES
CURRENTLY_ALLOWED_TO_START_PHASE_B_IMPLEMENTATION = NO, UNTIL ACCEPTED PHASE A PASS
```

## 19. Phase B exact ACQUIRE transport-provenance remediation

This section is the frozen remediation overlay for independent Phase B review finding `M-01` and its associated missing acceptance coverage. Where this section is stricter than Sections 1, 8, 10, 11, 12, 13, 15, 16, 17, or 18, **this section controls**. Nothing here weakens the inherited trusted lifecycle or adds authority to lock bytes, PR-head code, webhook payloads, caches, or caller prose.

Remediation evidence anchors:

```text
historical design target       c3532324e9df421afc787aa6cee3d91f8dbaa91e
historical design blob         5c877ec4d9807f285cb2e2c4c3f3ae3380117271
independent spec review        3f5206c5b793cf8b5ecaac5bafcb0313b5e7de0f
independent review blob        404bfd67d44233281e51a8eb7437d28b40c7f2de
Phase A core merge             b46628103642b55512ee244f82b9edc6362881e3
Phase A test-registration/main 84a046359b299950403b68bfcb190930ebbc4c3f
```

The historical Phase A implementation gate is now satisfied by canonical `main` at `84a046359b299950403b68bfcb190930ebbc4c3f`. This writer remediation does **not** self-accept the revised Phase B specification. Phase B implementation remains blocked until a focused independent re-review accepts the fixed remediation commit/blob.

### 19.1 Finalized `ExpectedAcquireV1`

For any path that could return `ACTIVE_NEXT`, the provisional Section 10 record is superseded by the following finalized record. It may be finalized only after the authoritative latest exact-head Verify run is successful.

```text
ExpectedAcquireV1 = {
  "schema_version": 1,

  "source_epoch_id": ...,
  "continuation_context_id": ...,
  "selection_id": ...,
  "acquire_intent_id": ...,

  "expected_repository": "51mns/AIMath-public",
  "expected_pr_number": ...,
  "expected_head_ref": ...,
  "expected_head_sha": ...,
  "expected_base_ref": "main",
  "expected_base_sha": <exact selection_main_sha>,

  "selected_task_id": ...,
  "worker_id": ...,
  "principal_id": ...,
  "work_ref": ...,
  "collision_keys": [...sorted...],
  "lock_id": ...,
  "acquired_at": ...,
  "expires_at": ...,

  "expected_lock_paths": [...sorted...],
  "expected_lock_blob_bundle": [
    {"path": ..., "blob_sha": ...},
    ...
  ],
  "expected_lock_bytes": [
    {
      "path": ...,
      "mode": "100644",
      "blob_sha": ...,
      "bytes_sha256": <SHA-256 of exact blob bytes>,
      "bytes_base64": <base64 of exact blob bytes>
    },
    ...
  ],

  "verify": {
    "workflow_name": "Verify public release",
    "event": "pull_request",
    "run_id": <authoritative latest matching numeric run id>,
    "head_sha": <exact expected_head_sha>,
    "status": "completed",
    "conclusion": "success"
  }
}
```

All path-bearing lists are sorted lexicographically by `path`. `expected_lock_paths`, `expected_lock_blob_bundle`, and `expected_lock_bytes` MUST describe exactly the same path set. Git blob OID, regular mode, SHA-256 and decoded bytes MUST all agree. The exact lock bytes are data for equality/provenance checking only; they do not carry `/next` authority.

`expected_base_sha` MUST equal the `selection_main_sha` bound by `SelectionV1` and the `base_main_sha` serialized in the expected lock payload. `expected_head_ref` MUST equal the deterministic `next-acquire/<acquire_intent_id>/<TASK-ID>/<worker-id>` ref. `acquire_intent_id` MUST be the digest of the exact `AcquireIntentV1` that contains the same source epoch, continuation context, selection, Task, worker, principal, work ref and collision bundle.

The finalized identity is:

```text
expected_acquire_id = SHA256(canonical(ExpectedAcquireV1))
```

There is no nullable/older green Verify shortcut for `ACTIVE_NEXT`. Before the exact latest run is successful, the state remains pending/fail-closed and no finalized expected acquisition can certify ownership.

### 19.2 Exact-head Verify freshness is part of provenance

For the expected head, Phase B MUST fresh-list all workflow runs that match all of:

```text
workflow name = "Verify public release"
event         = "pull_request"
head_sha      = ExpectedAcquireV1.expected_head_sha
```

The matching run with the greatest numeric `run_id` is authoritative. The authoritative run MUST equal `ExpectedAcquireV1.verify.run_id` and MUST currently be `status=completed`, `conclusion=success`.

An older successful run for the same exact head is non-authoritative if a greater matching run ID exists. Therefore any newer matching run that is `failed`, `cancelled`, `in_progress`, `queued`, or otherwise not completed-success removes ACQUIRE eligibility and prevents `ACTIVE_NEXT`, even though the head SHA did not move.

Webhook/workflow delivery data is trigger-only. A delivery may cause re-evaluation, but none of its PR, head, base, run, conclusion, main, source-epoch or lock fields may be used as authority without fresh GitHub rederivation.

### 19.3 `ExactAcquireTransportProvenanceV1` predicate

Canonical lock bytes alone are **never sufficient**. Before `ACTIVE_NEXT`, Phase B MUST evaluate one fresh-GitHub predicate against the finalized expected record. The predicate succeeds only when **every** clause below succeeds for the exact expected PR number/head; no existential search for an equivalent PR is allowed.

#### A. Exact expected PR identity

Fresh-read `expected_repository` / pull request `expected_pr_number` and require:

1. the PR exists in exactly `ExpectedAcquireV1.expected_repository`;
2. `head.repo.full_name == expected_repository`;
3. `head.ref == expected_head_ref`;
4. `head.sha == expected_head_sha`;
5. `base.repo.full_name == expected_repository`;
6. `base.ref == expected_base_ref`;
7. the authenticated/recorded transport principal and immutable expected transport metadata remain consistent with the finalized expected record.

A different PR number is non-equivalent. A different head ref is non-equivalent. A different head SHA is non-equivalent. Matching lock bytes do not relax any of these equalities.

#### B. Exact expected base / head derivation

Fresh-read the expected base commit/tree, expected head commit/tree and their Git relation. Require all of:

1. `expected_base_sha == SelectionV1.selection_main_sha`;
2. `expected_base_sha` is an ancestor/base of `expected_head_sha` under the transport branch relation;
3. comparing `expected_base_sha -> expected_head_sha` changes exactly `expected_lock_paths` and no other repository path;
4. every expected head lock path is a regular `100644` blob with exactly the expected OID and bytes;
5. the expected base does not already contain the newly acquired canonical lock bundle as an active equivalent acquisition.

If the base relation is unavailable or cannot prove the exact selection base, the predicate fails closed. A later current `main` SHA is not substituted for `expected_base_sha`.

#### C. Authoritative exact-head Verify

Recompute Section 19.2 from fresh GitHub workflow-run state. The latest matching numeric run ID MUST equal the finalized expected run identity and MUST still be completed-success.

#### D. Server-observed merge of that exact PR

The fresh expected PR MUST be server-observed as merged:

```text
state            = "closed"
merged           = true
merged_at        = non-null
merge_commit_sha = non-null
```

The merge record belongs to the exact expected PR number already checked in A. Phase B MUST NOT infer this clause from canonical bytes, from another PR, from a closed state alone, from a branch disappearance, or from a webhook payload.

#### E. Positive canonical-main history relation

Let `merge_result_sha` be the fresh server-observed `merge_commit_sha` for the exact expected PR. Fresh GitHub commit/tree/history evidence MUST prove all of:

1. `merge_result_sha` exists;
2. `merge_result_sha` is reachable/ancestral from the fresh current canonical `refs/heads/main`;
3. comparing `expected_base_sha -> merge_result_sha` introduces exactly `expected_lock_paths` and no unrelated path change;
4. the tree at `merge_result_sha` contains every expected lock path as regular `100644` with exactly the expected OID/bytes;
5. the final tree effect of the server-observed expected-PR merge therefore equals the exact expected ACQUIRE transport tree effect.

This rule is merge-strategy neutral: merge-commit, squash, or rebase may produce different commit identities, but GitHub's server-observed merge record for the exact PR plus the exact base-to-merge-result tree relation and current-main reachability must all hold. If the repository's merge strategy or GitHub response shape prevents this positive relation from being proved, Phase B fails closed; it does not downgrade to payload equivalence.

#### F. Fresh canonical lock read-back

Finally, fresh current `main` MUST contain exactly one active canonical lock bundle matching the finalized expected acquisition:

- exact selected Task;
- exact worker/principal;
- exact work ref;
- exact collision-key bundle;
- exact lock ID;
- exact `base_main_sha = expected_base_sha`;
- exact acquired/expires timestamps;
- exact lock path set;
- exact regular `100644` OIDs and bytes;
- unexpired/active lifecycle state.

A later renewal, replacement, reacquisition, different lock bytes, or different acquisition identity does not satisfy this proof even if some human-readable fields remain equal.

The complete predicate is therefore:

```text
ExactAcquireTransportProvenanceV1(ExpectedAcquireV1, FreshGitHubState) =
    exact_expected_pr_identity
AND exact_expected_base_head_derivation
AND authoritative_latest_exact_head_verify_success
AND server_observed_exact_expected_pr_merged
AND exact_expected_merge_result_reachable_from_fresh_main
AND exact_base_to_merge_result_lock_only_tree_effect
AND exact_fresh_canonical_active_lock_readback
```

`ACTIVE_NEXT` is permitted only when the complete predicate is true.

### 19.4 Non-equivalence and fail-closed outcomes

A different ACQUIRE PR/head is **non-equivalent** even if it introduces byte-identical lock contents.

Concrete substitution rule:

```text
expected PR A/head A -> payload P
other    PR B/head B -> byte-identical payload P
B merges first
```

The canonical lock bytes may equal `P`, but A's exact merge predicate is false unless the exact expected PR A/head A itself is server-observed merged and its merge result has the required canonical-main history relation. Therefore the request MUST NOT return `ACTIVE_NEXT` for A.

Observed non-equality in any exact PR/head/base/Verify/merge/history relation returns:

```text
status = ACQUIRE_TRANSPORT_PROVENANCE_MISMATCH
```

with a deterministic machine-readable `reason_code`, including at least:

```text
EXPECTED_PR_NOT_FOUND
EXPECTED_REPOSITORY_MISMATCH
EXPECTED_HEAD_REF_MISMATCH
EXPECTED_HEAD_SHA_MISMATCH
EXPECTED_BASE_REF_MISMATCH
EXPECTED_BASE_SHA_MISMATCH
EXPECTED_BASE_HEAD_RELATION_MISMATCH
LATEST_VERIFY_NOT_SUCCESS
VERIFY_RUN_ID_MISMATCH
EXPECTED_PR_NOT_MERGED
MERGE_RESULT_NOT_ON_CANONICAL_MAIN
MERGE_RESULT_DELTA_MISMATCH
MERGE_RESULT_LOCK_BUNDLE_MISMATCH
CANONICAL_LOCK_READBACK_MISMATCH
CANONICAL_LOCK_NOT_ACTIVE
```

If required fresh GitHub evidence is unavailable, malformed, incomplete, or truncated so the predicate cannot be evaluated, return a retryable fail-closed observation/provenance-unavailable result and do no transport/canonical mutation from cached data. Unavailability is never converted into equality.

### 19.5 Frozen unbroken evidence chain

The `ACTIVE_NEXT` evidence chain is exactly:

```text
SourceAcquisitionV1 / source_epoch_id
-> exact RELEASE transport/history for that source epoch
-> fresh post-RELEASE canonical main
-> ContinuationContextV1 / continuation_context_id
-> SelectionV1 / selection_id
-> AcquireIntentV1 / acquire_intent_id
-> finalized ExpectedAcquireV1
-> exact expected PR number/repository/head/base
-> authoritative latest exact-head successful Verify run
-> server-observed merge of THAT exact PR
-> exact expected base -> merge_result_sha lock-only tree effect
-> merge_result_sha reachable from fresh canonical main
-> exact active canonical lock OIDs/bytes
-> ACTIVE_NEXT
```

No arrow in this chain may be replaced by chat memory, webhook payload, cached PR data, worker/principal similarity, Task similarity, ref-name similarity, or canonical lock bytes alone.

### 19.6 Inherited same-class ordering pinned for Phase B tests

The inherited trusted lifecycle ordering relied on by this design is frozen explicitly for Phase B regression coverage:

1. after repository-wide prerequisites succeed, malformed candidate-local observations are dropped only for that candidate;
2. among fully eligible `RELEASE` candidates, ascending PR number is the deterministic same-class order and the first eligible candidate is the only canonical mutation attempted in that trusted run;
3. only when no eligible `RELEASE` exists are fully eligible `ACQUIRE` candidates considered;
4. among fully eligible `ACQUIRE` candidates, ascending PR number is the deterministic same-class order and the first eligible candidate is the only canonical mutation attempted in that trusted run;
5. a malformed lower-number candidate does not block a later valid candidate after candidate-local rejection;
6. at-most-one trusted canonical lifecycle mutation per run remains unchanged.

This pins inherited behaviour; it does not create a new ordering authority in Phase B orchestration.

### 19.7 Additional mandatory acceptance/adversarial tests

The Section 15 matrix is extended from 50 to **55** mandatory rows:

51. **byte-identical alternate-PR substitution:** expected PR A/head A is finalized; different PR B/head B carries byte-identical expected lock payload and B is merged; A MUST NOT yield `ACTIVE_NEXT`; result is `ACQUIRE_TRANSPORT_PROVENANCE_MISMATCH` unless A itself independently satisfies the complete exact provenance predicate.
52. **stale webhook/workflow delivery is trigger-only:** replay an old delivery containing previously valid PR/head/base/run/source fields; implementation MUST discard those fields as authority, fresh-rederive GitHub/main state, and stop/recompute if fresh state differs or the source epoch is stale.
53. **multiple eligible RELEASE regression:** with two or more fully eligible RELEASE candidates, the lowest PR number is selected and at most one mutation occurs; parameterized companion fixture with a malformed lower-number RELEASE candidate proves candidate-local rejection allows the next valid RELEASE candidate to be examined/selected.
54. **multiple eligible ACQUIRE regression:** when no RELEASE is eligible and two or more ACQUIRE candidates are fully eligible, the lowest PR number is selected and at most one mutation occurs; parameterized companion fixture with a malformed lower-number ACQUIRE candidate proves later valid ACQUIRE remains examinable.
55. **latest Verify on the same exact head controls eligibility:** for one unchanged head SHA, an older successful Verify followed by a greater numeric run ID whose state is failed, cancelled, in-progress/queued, or otherwise non-success MUST make the transport ineligible and MUST prevent `ACTIVE_NEXT`; only when the greatest matching run ID is completed-success may the finalized expected record/provenance pass.

These five rows are required in addition to all original 50 rows; they do not replace or merge away any earlier test obligation.

### 19.8 Remediation severity and readiness

Independent review `3f5206c5b793cf8b5ecaac5bafcb0313b5e7de0f` found zero CRITICAL, zero HIGH, one blocking MEDIUM `M-01`, and missing explicit acceptance coverage. This writer change freezes the requested exact PR/head/base -> server merge -> canonical-main history predicate and adds all five missing regressions.

Writer-side remediation status only:

```text
M-01_SPEC_GAP = REMEDIATED_IN_DESIGN_CANDIDATE
MISSING_ACCEPTANCE_COVERAGE = REMEDIATED_IN_DESIGN_CANDIDATE
INDEPENDENT_REVIEW_STATUS = REQUIRED / NOT SELF-ASSERTED
```

The old Section 18 `CURRENTLY_ALLOWED... UNTIL ACCEPTED PHASE A PASS` line is superseded because Phase A is now accepted/merged/test-registered on canonical main. The current gate is the focused independent Phase B spec re-review of this remediation commit/blob.

Frozen current readiness:

```text
PHASE_A_ACCEPTED = YES
PHASE_B_M01_REMEDIATION_FROZEN = YES
READY_FOR_FOCUSED_PHASE_B_SPEC_REREVIEW = YES
READY_FOR_PHASE_B_IMPLEMENTATION_AFTER_PHASE_A = YES, CONDITIONED_ON ACCEPTED FOCUSED PHASE B SPEC REREVIEW
CURRENTLY_ALLOWED_TO_START_PHASE_B_IMPLEMENTATION = NO, UNTIL ACCEPTED FOCUSED PHASE B SPEC REREVIEW
```

If focused review finds that exact expected transport provenance cannot be established from fresh GitHub PR/commit/tree/history evidence without weakening exactness, implementation MUST stop and return to design review. It MUST NOT fall back to canonical blob equality as a substitute.

## 20. Canonical acquisition identity V2 remediation

This section is the frozen V2 remediation for focused independent rereview commit `7385e592d93987490d1fc91c10ec4c5b65ff4e81`, which found:

```text
H-01 HIGH   GitHub indirect merge prevents positive exact-PR-number causality proof.
M-02 MEDIUM max numeric run_id is not a documented latest-run ordering rule.
```

Focused review blob:

```text
09a1f9c0a7318c22e80c48d8618caa37a52127b2
```

Primary GitHub semantics used by this V2 overlay:

- https://docs.github.com/en/pull-requests/reference/pull-request-merges
- https://docs.github.com/en/actions/reference/workflows-and-actions/contexts
- https://docs.github.com/en/rest/actions/workflow-runs
- https://docs.github.com/en/rest/commits/commits
- https://docs.github.com/en/rest/git/commits

Current implementation/context evidence frozen for this design pass:

```text
canonical main                   84a046359b299950403b68bfcb190930ebbc4c3f
trusted lifecycle merge method   squash
Verify workflow path             .github/workflows/verify.yml
Verify workflow name             Verify public release
fresh-observed workflow_id       347191396
effective Ruleset id             22089746
Ruleset name                     Village main strict lifecycle safety
required status context          verify
strict up-to-date                true
bypass actors                    []
current_user_can_bypass          never
```

The existing trusted lifecycle fresh-revalidates main/head/base immediately before its merge endpoint call and currently calls the endpoint with the expected candidate PR number, exact candidate head SHA, and `merge_method = "squash"`. That is useful implementation context, but **post-canonicalisation authority does not depend on proving which PR number caused the Git transition**.

### 20.1 Supersession rule — PR causality and max-`run_id` are removed from authority

This Section 20 supersedes Sections 8, 10, 11, 12, 14, 15, 18 and 19.1–19.8 wherever they conflict with V2. Historical wording is retained only to preserve the audit trail.

The following older statements are explicitly **NON-AUTHORITATIVE** for any V2 implementation:

1. any requirement or implication that `THIS exact PR number created THIS canonical acquisition`;
2. any use of PR number, PR ref, `merged`, `merged_at`, or `merge_commit_sha` as authority for `ACTIVE_NEXT`;
3. any rule that a different PR/ref is non-equivalent merely because its PR locator differs when it points to the same exact immutable acquisition head;
4. any `merge-strategy neutral` claim for the `ACTIVE_NEXT` proof;
5. any rule that the greatest numeric `run_id` is the latest or authoritative Verify run;
6. Section 19.7 row 55 as written. It is replaced by Section 20.10 row 55 below.

PR metadata remains useful for transport discovery, idempotent reuse, debugging and audit. It is not canonical acquisition security identity.

The V2 security statement is:

> **THIS exact immutable acquisition identity became canonical through the permitted canonical-main transition.**

It is deliberately **not**:

> THIS exact PR number created this acquisition.

GitHub indirect-merge state therefore cannot grant or deny `ACTIVE_NEXT` by itself.

### 20.2 `CanonicalAcquireIdentityV2`

The authority-bearing expected acquisition is immutable Git/acquisition content:

```text
CanonicalAcquireIdentityV2 = {
  "schema_version": 2,

  "source_epoch_id": ...,
  "continuation_context_id": ...,
  "selection_id": ...,
  "acquire_intent_id": ...,

  "expected_base_sha": ...,
  "expected_head_sha": ...,
  "expected_head_tree_sha": ...,

  "selected_task_id": ...,
  "worker_id": ...,
  "principal_id": ...,

  "work_ref": ...,
  "sorted_collision_keys": [...],

  "lock_id": ...,
  "acquired_at": ...,
  "expires_at": ...,

  "exact_lock_objects": [
    {
      "path": ...,
      "mode": "100644",
      "blob_sha": <40-hex Git blob OID>,
      "bytes_sha256": <64 lowercase hex>
    },
    ... sorted lexicographically by path ...
  ]
}
```

The repository namespace is fixed by this frozen contract as `51mns/AIMath-public`; an observation from any other repository fails before identity comparison.

`exact_lock_objects` MUST describe exactly the complete canonical collision-key lock path set. `sorted_collision_keys`, the path-derived collision keys, every decoded lock payload collision bundle, and the Task's frozen collision bundle MUST agree exactly. Every lock object MUST be a regular Git blob mode `100644`; Git OID, exact decoded bytes and `bytes_sha256` MUST agree.

`expected_base_sha` MUST equal both:

```text
SelectionV1.selection_main_sha
expected lock payload base_main_sha
```

The exact head `H = expected_head_sha` is frozen only after the deterministic ACQUIRE transport ref is first materialised. The first valid creator freezes the exact immutable head commit and its exact payload timestamp; all retries and duplicate creators for the same `acquire_intent_id` MUST adopt that exact existing valid head rather than manufacture a second head. Therefore commit metadata that participates in `H` is part of the frozen acquisition once created, not an independently regenerated approximation.

For V2, the expected ACQUIRE head itself MUST be a single exact transport transition from the selection base:

```text
parents(H) == [expected_base_sha]
tree(H).sha == expected_head_tree_sha
compare expected_base_sha -> H changes exactly exact_lock_objects.path
```

No unrelated path may change. Every expected lock object in `tree(H)` MUST equal `CanonicalAcquireIdentityV2.exact_lock_objects` exactly.

The canonical acquisition identity is:

```text
canonical_acquire_id = SHA256(canonical(CanonicalAcquireIdentityV2))
```

PR number, PR ref, PR merge fields, webhook fields, workflow delivery fields and chat/caller data are **not inputs** to `canonical_acquire_id`.

A canonical lock bundle alone is still insufficient: the source epoch, continuation context, selection, acquire intent, exact base/head/tree and the canonical-main transition proof below are all required.

### 20.3 `TransportLocatorV1` is audit/idempotency metadata only

Transport discovery may separately retain:

```text
TransportLocatorV1 = {
  "repository": "51mns/AIMath-public",
  "pr_number": ...,
  "head_ref": ...,
  "head_sha": ...,
  "base_ref": "main",
  "base_sha": ...,
  "observed_principal": ...
}
```

This record may be used only for:

- finding/reusing the deterministic ACQUIRE transport;
- duplicate PR suppression;
- diagnostics and human audit;
- handing a currently eligible transport to the inherited trusted lifecycle.

`TransportLocatorV1.pr_number` and `.head_ref` MUST NOT appear in `CanonicalAcquireIdentityV2` and MUST NOT be predicates that grant `ACTIVE_NEXT`.

Before canonicalisation, transport reuse remains strict: a different head SHA is not reusable as the same frozen acquisition transport. After canonicalisation, PR locator equality is irrelevant to acquisition authority; immutable acquisition identity and canonical history control.

### 20.4 Security equivalence under V2

The equivalence rules are exact:

#### Different head SHA

If another PR/ref points to `H2 != expected_head_sha`, it is **NON-EQUIVALENT** for this acquisition even when its lock bytes are byte-identical. Different immutable commit identity means a different acquisition candidate. It cannot satisfy this `canonical_acquire_id`.

#### Same head SHA, different PR/ref

If another PR/ref points to the exact same `H = expected_head_sha`, its PR identity is different but its immutable Git head is the same. It may represent the same acquisition **only when every other field of `CanonicalAcquireIdentityV2` and every canonical-main condition in Section 20.7 also matches**.

No PR is called the creator. The result is either:

```text
CANONICAL_ACQUIRE_IDENTITY_CONFIRMED
```

or a fail-closed canonical identity/transition mismatch.

#### Same head SHA but any acquisition-field mismatch

Same `H` does not waive Task, worker, principal, source epoch, continuation, selection, acquire intent, work ref, collision bundle, lock id, timestamps, base SHA, tree SHA, blob OIDs or byte hashes. Any mismatch fails closed.

### 20.5 Documented Verify lineage ordering — M-02 replacement

The V2 Verify identity is fixed to the repository/workflow lineage, not to numeric `run_id` chronology:

```text
repository    = "51mns/AIMath-public"
workflow_id   = 347191396
workflow_path = ".github/workflows/verify.yml"
workflow_name = "Verify public release"
event         = "pull_request"
head_sha      = CanonicalAcquireIdentityV2.expected_head_sha
```

The implementation MUST fresh-list the **complete relevant workflow-run set** for that exact workflow identity and exact `head_sha`.

GitHub documents:

- `run_id` is unique for a workflow run and does not change on rerun;
- `run_number` begins at 1 for a workflow's first run and **increments with each new run** of that workflow;
- `run_number` does not change on rerun;
- `run_attempt` begins at 1 for a workflow run and increments with each rerun.

Therefore V2 freezes:

```text
authoritative_run_number = max(run_number among the complete matching run set)
```

`run_id` is retained only as the immutable lookup identifier for the selected lineage. **Its magnitude is never compared for ordering.**

For the unique highest-`run_number` lineage:

1. fresh-read its current run object by `run_id`;
2. require the same repository/workflow_id/path/name/event/head SHA;
3. require the currently observed `run_number == authoritative_run_number`;
4. record the currently observed `run_attempt`;
5. require `status = completed` and `conclusion = success` now.

Any current state other than completed-success, including failure, cancelled, timed_out, action_required, queued, in_progress, requested, waiting, pending, neutral, skipped, stale or malformed/unknown, is **NOT eligible**.

If duplicate rows expose the same `run_number` with inconsistent `run_id`, workflow identity, head SHA, status or other lineage identity, observation fails closed rather than choosing one.

#### Older-run rerun policy

Suppose matching lineages exist:

```text
run_number 10 = success
run_number 11 = failure
```

If run 10 is rerun later and succeeds again, its `run_number` remains 10. It **does not** overtake 11. Run 11 remains the authoritative lineage, so the acquisition remains NOT eligible.

Recovery from rerunning a **non-authoritative older lineage** requires either:

- a new matching workflow run with a higher `run_number`, for example 12, which completes successfully; or
- successful completion of a rerun of the already-authoritative highest lineage itself, in which case that same highest `run_number` remains authoritative and its current `run_attempt` / current status controls.

If the authoritative highest lineage is currently being rerun and the current run object is queued/in-progress, old successful attempts are stale for authority and the acquisition is NOT eligible until that current attempt reaches completed-success.

### 20.6 Workflow-run completeness is a global fail-closed prerequisite

No inherited one-page helper is sufficient for V2.

Fresh pagination MUST continue until the implementation can establish the complete relevant result set for the exact workflow identity/head. The REST API is paginated (maximum 100 rows per page), and GitHub documents that filtered workflow-run searches may be capped at 1,000 results. The implementation MUST therefore fail closed if the query/result envelope cannot prove completeness.

At minimum, any of the following returns a machine-readable Verify observation failure and grants no PENDING/merge/`ACTIVE_NEXT` authority:

```text
VERIFY_WORKFLOW_IDENTITY_AMBIGUOUS
VERIFY_RUNSET_PAGINATION_FAILED
VERIFY_RUNSET_TRUNCATED
VERIFY_RUNSET_RESULT_CAP_UNPROVEN
VERIFY_RUNSET_MALFORMED
VERIFY_RUN_NUMBER_DUPLICATE_INCONSISTENT
VERIFY_AUTHORITATIVE_LINEAGE_UNREADABLE
VERIFY_AUTHORITATIVE_ATTEMPT_NOT_SUCCESS
```

A cached result, webhook payload or old green run cannot substitute for fresh complete observation.

### 20.7 Exact canonical-main transition proof

Let:

```text
B   = CanonicalAcquireIdentityV2.expected_base_sha
H   = CanonicalAcquireIdentityV2.expected_head_sha
T_H = CanonicalAcquireIdentityV2.expected_head_tree_sha
C   = fresh refs/heads/main SHA
```

`ACTIVE_NEXT` may be returned only after fresh GitHub commit/tree/history evidence proves **all** of the following.

#### A. Frozen acquisition derivation

1. `B == SelectionV1.selection_main_sha`.
2. `B == expected lock payload base_main_sha`.
3. `H` is the exact frozen head for the same `acquire_intent_id`.
4. `parents(H) == [B]`.
5. `tree(H) == T_H`.
6. compare `B -> H` changes exactly the expected canonical lock paths and no other path.
7. the lock objects at `H` are exact regular `100644` objects with the frozen OIDs/bytes hashes.

#### B. Fresh canonical first-parent history

8. fresh current main `C` descends from `B`.
9. Starting at `C`, fresh-read Git commit objects and follow **parent index 0** toward `B`. The observation must be complete enough to prove the first-parent chain; cached or partially listed history is not authority.
10. Identify `M` as the unique child of `B` on that observed first-parent path — the canonical transition immediately after `B`.
11. `M` MUST have exactly one parent, and that parent MUST be `B`:

```text
parents(M) == [B]
```

This is the frozen strict canonical shape. A multi-parent merge commit, an unrelated intervening first-parent commit, a multi-step rebase sequence, missing history, ambiguous parent data, or any shape that cannot prove this exact transition fails closed.

#### C. Exact canonical tree transition

12. `tree(M).sha == T_H`.
13. compare `B -> M` changes exactly `CanonicalAcquireIdentityV2.exact_lock_objects.path` and no unrelated path.
14. for every expected path, the object at `M` is mode `100644` and has exactly the expected Git blob OID and byte SHA-256.
15. no expected lock path already existed at `B` as the same active acquisition.

The canonical acquisition transition is therefore an exact single transition from the frozen base to the frozen intended head tree. `M` MAY equal `H`; equality is not required. Commit message, PR number and PR merge metadata are not acquisition authority.

#### D. Current-main persistence and active read-back

16. `M` remains in the fresh first-parent ancestry of current main `C`.
17. fresh current-main tree still contains the exact expected lock object bundle.
18. fresh canonical Village state reports exactly that bundle active and unexpired.
19. Task, worker, principal, work ref, collision keys, lock id, `base_main_sha`, `acquired_at`, `expires_at`, source epoch, continuation context, selection and acquire intent all still equal `CanonicalAcquireIdentityV2`.
20. a later renewal, replacement or reacquisition is a different acquisition and does not satisfy the old `canonical_acquire_id`, even when selected Task/worker/principal remain the same.

#### E. Effective Ruleset proof

21. fresh effective/default-branch rule observation MUST positively prove all of:

```text
enforcement = active
target applies to default branch
required status context includes "verify"
strict_required_status_checks_policy = true
bypass_actors = []
current_user_can_bypass = "never"
```

If effective-rule observation is unavailable, malformed, contradictory, or any bypass actor exists, V2 fails closed. This lane does not change repository settings.

### 20.8 Merge-shape policy — not merge-strategy neutral

V2 does **not** trust a merge method name. It trusts only the observed canonical shape in Section 20.7.

Current trusted lifecycle uses `merge_method = "squash"`, with final main/head/base revalidation immediately before the merge API call. GitHub documents squash merging as producing one combined commit on the base branch; that is compatible with the frozen single-parent/single-transition proof when the observed result actually satisfies `parents(M) == [B]` and `tree(M) == tree(H)`.

Other GitHub merge modes are not automatically accepted:

- a normal merge commit is expected to be multi-parent and therefore fails `parents(M) == [B]`;
- a multi-commit rebase produces multiple canonical first-parent transitions and therefore fails the single-transition proof;
- a one-step result from any mechanism is acceptable only if the **observed immutable Git shape** satisfies every V2 clause. The design never infers safety from the method label.

If GitHub behaviour for a candidate produces a shape that cannot be positively proved, return:

```text
NONCANONICAL_ACQUIRE_MERGE_SHAPE
```

not `ACTIVE_NEXT`.

### 20.9 Indirect merge and same-head/different-locator handling

#### Reviewer H-01 attack — fail closed

Construct:

```text
expected PR A: ref A, head H, base B
other    PR B: ref B, same exact head H, base B
```

If the other PR is merged using a merge-commit path, GitHub may later mark expected PR A indirectly merged. Under V2, `A.merged`, `A.merged_at` and `A.merge_commit_sha` are irrelevant to acquisition authority.

The canonical merge-commit transition has a noncanonical multi-parent shape, so Section 20.7 fails:

```text
status = NONCANONICAL_ACQUIRE_MERGE_SHAPE
ACTIVE_NEXT = false
```

This closes the focused-review H-01 without attempting impossible PR-number causality attribution.

#### Same immutable acquisition through another PR locator — may confirm

If a different PR/ref points to the same exact head `H`, and fresh canonical main instead contains an exact single transition `M` such that:

```text
parents(M) == [B]
tree(M) == tree(H)
compare B -> M == exact expected lock-only object set
all CanonicalAcquireIdentityV2 fields match
Verify lineage policy passes
Ruleset proof passes
fresh active canonical lock read-back passes
```

then the intended immutable acquisition itself became canonical. V2 returns:

```text
CANONICAL_ACQUIRE_IDENTITY_CONFIRMED
```

It does **not** say that PR A or the other PR was proved to be the creator.

### 20.10 Machine-readable V2 boundary and preregistered tests

The positive boundary is exactly:

```text
CANONICAL_ACQUIRE_IDENTITY_CONFIRMED
```

Representative fail-closed codes include:

```text
CANONICAL_ACQUIRE_IDENTITY_MISMATCH
CANONICAL_ACQUIRE_BASE_MISMATCH
CANONICAL_ACQUIRE_HEAD_MISMATCH
CANONICAL_ACQUIRE_HEAD_PARENT_MISMATCH
CANONICAL_ACQUIRE_HEAD_TREE_MISMATCH
CANONICAL_ACQUIRE_TRANSITION_MISMATCH
NONCANONICAL_ACQUIRE_MERGE_SHAPE
CANONICAL_ACQUIRE_TREE_MISMATCH
CANONICAL_ACQUIRE_DELTA_MISMATCH
CANONICAL_ACQUIRE_HISTORY_UNPROVEN
CANONICAL_LOCK_READBACK_MISMATCH
CANONICAL_LOCK_NOT_ACTIVE
RULESET_PROOF_UNAVAILABLE
RULESET_BYPASS_PRESENT
LATEST_VERIFY_NOT_SUCCESS
VERIFY_RUNSET_INCOMPLETE
```

The historical matrix remains mandatory, except that Section 19.7 row 55 is **replaced** by V2 row 55. Rows 56–62 are new non-padding regressions. The exact V2 total is **62 mandatory rows**.

55. **highest documented `run_number` lineage controls exact-head eligibility:** for one unchanged `H`, fresh-complete matching run observation selects the maximum `run_number`, never maximum `run_id`. If that authoritative lineage is failure, cancelled, timed_out, action_required, queued, in-progress or otherwise not current completed-success, the transport/acquisition is NOT eligible and cannot reach `ACTIVE_NEXT`, regardless of any older green lineage.
56. **same head / different ref / indirect merge-commit attack:** expected PR A/ref A and other PR B/ref B point to the same exact `H`; B is merged with a multi-parent merge-commit shape and A may appear indirectly merged. PR merged metadata is ignored; the canonical transition is noncanonical; return `NONCANONICAL_ACQUIRE_MERGE_SHAPE`, NOT `ACTIVE_NEXT`.
57. **same head / different PR locator / exact canonical single transition:** a different PR locator points to exact `H`; canonical main contains one exact `M` with `parents(M) == [B]`, `tree(M) == tree(H)`, exact lock-only delta, exact identity/Verify/Ruleset/read-back. Confirm `CANONICAL_ACQUIRE_IDENTITY_CONFIRMED`; assert no PR-number creator attribution is required or emitted.
58. **older-run rerun cannot outrank newer failure:** run 10 success, run 11 failure, then rerun run 10 and observe its newer attempt succeed. Because rerun keeps `run_number = 10`, run 11 remains authoritative and the acquisition remains NOT eligible.
59. **new higher successful lineage recovers:** run 10 success, run 11 failure, then a new matching run 12 completes success. Run 12 is authoritative and Verify eligibility passes if all other acquisition conditions pass.
60. **authoritative lineage currently rerunning/in-progress:** the highest `run_number` previously had a successful attempt but its current rerun attempt is queued/in-progress. Fresh current run object is not completed-success, so the acquisition is NOT eligible; stale attempt success cannot be reused.
61. **canonical first-parent history incomplete/ambiguous/non-single-transition:** inability to follow fresh parent[0] chain from current main to B, an unrelated first-parent commit immediately after B, a multi-parent M, or a multi-step canonicalisation returns `CANONICAL_ACQUIRE_HISTORY_UNPROVEN` or `NONCANONICAL_ACQUIRE_MERGE_SHAPE`; never `ACTIVE_NEXT`.
62. **Ruleset bypass/unreadable regression:** effective main Ruleset unreadable/malformed, strict verify proof absent, `bypass_actors` nonempty, or `current_user_can_bypass != never` returns Ruleset fail-closed and cannot confirm `ACTIVE_NEXT`.

Rows 51–54 remain mandatory as previously frozen. Row 51 continues to prove that a byte-identical transport with a **different head SHA** is not the same acquisition. V2 rows 56–57 separately cover the same-head/different-locator distinction that focused review exposed.

### 20.11 V2 threat-control reassessment

| Threat | Frozen V2 result |
|---|---|
| different bytes, same PR locator | FAIL CLOSED: head/tree/object identity mismatch |
| different head SHA | NON-EQUIVALENT / NOT `ACTIVE_NEXT` |
| same head SHA, different ref | PR locator irrelevant after canonicalisation; only exact canonical identity/transition can confirm |
| expected PR marked indirectly merged | merged metadata ignored; canonical shape decides |
| merge-commit canonical shape | multi-parent => `NONCANONICAL_ACQUIRE_MERGE_SHAPE` |
| rebase / multi-step canonical shape | multiple first-parent transitions => fail closed |
| single-transition exact tree | may confirm only if every identity/Verify/Ruleset/read-back clause passes |
| direct unrelated main change | tree/delta or first-parent immediate-transition mismatch => fail closed |
| stale expected base | B/selection/lock-base mismatch => fail closed |
| later lock renewal | old identity no longer active => fail closed |
| later lock replacement | OID/bytes/timestamps/identity mismatch => fail closed |
| old acquisition epoch | source/selection/acquire-intent mismatch => fail closed |
| incomplete main history | `CANONICAL_ACQUIRE_HISTORY_UNPROVEN` |
| first-parent ambiguity | fail closed |
| Ruleset unreadable | `RULESET_PROOF_UNAVAILABLE` |
| Ruleset bypass nonempty | `RULESET_BYPASS_PRESENT` |
| old green / newer failure | highest `run_number` failure remains authoritative |
| rerun older run after newer failure | older run_number cannot outrank newer lineage |
| new successful higher run number | highest new lineage may restore Verify eligibility |
| partial workflow pagination | `VERIFY_RUNSET_INCOMPLETE` / fail closed |

### 20.12 Inherited security boundaries remain unchanged

V2 changes the proof identity, not the authority surface.

The following remain frozen:

- accepted Phase A stops at `ACQUIRE_PENDING` and never emits/certifies `ACTIVE_NEXT`;
- no Phase A GitHub mutation authority;
- no Truth authority;
- no review authority or autonomous I2/I3;
- no automatic `RENEW`;
- no automatic `TAKEOVER`;
- no new PAT or secret;
- no Ruleset/settings change;
- no `pull_request_target`;
- no PR-head code in trusted write context;
- worker ID is not a credential;
- `PENDING_CLAIM` and open/green PRs are not ownership;
- RELEASE remains higher priority than ACQUIRE;
- at most one trusted canonical lifecycle mutation occurs per trusted run;
- current-main/head/base revalidation immediately before trusted mutation remains mandatory;
- candidate-local malformed GitHub observations remain candidate-local where the repository-wide substrate is otherwise complete;
- repository-wide incomplete observations remain global fail-closed;
- Task/Campaign creation and strategic continuation authority remain outside Phase B;
- the trusted lifecycle is not broadened by this design.

### 20.13 Writer-side remediation status and focused rereview gate

Focused review H-01 is addressed by removing the unsupported exact-PR creator claim entirely and requiring immutable `CanonicalAcquireIdentityV2` plus a strict canonical-main single-transition proof.

Focused review M-02 is addressed by replacing numeric `run_id` chronology with GitHub's documented workflow `run_number` lineage ordering and current `run_attempt` state, with complete pagination/fail-closed requirements.

Writer-side design assessment:

```text
H-01_INDIRECT_MERGE = REMEDIATED_IN_V2_DESIGN_CANDIDATE
PR_NUMBER_AUTHORITY = REMOVED
M-02_RUN_ORDERING = REMEDIATED_IN_V2_DESIGN_CANDIDATE
CANONICAL_ACQUIRE_IDENTITY_V2 = FROZEN
CANONICAL_MAIN_SINGLE_TRANSITION = REQUIRED
PREREGISTERED_TEST_TOTAL = 62
CRITICAL_KNOWN = 0
HIGH_KNOWN = 0
MEDIUM_KNOWN = 0
INDEPENDENT_FOCUSED_REREVIEW = REQUIRED
PHASE_B_IMPLEMENTATION_ALLOWED_NOW = NO
READY_FOR_FOCUSED_REREVIEW = YES
```

This writer does not self-promote the V2 candidate to accepted. Phase B implementation remains blocked until a new independent focused security review fixes this exact commit/blob and returns PASS with no CRITICAL/HIGH/MEDIUM blocker.

## 21. Canonical acquisition content V3 remediation

This section is the frozen V3 remediation for independent final review commit `2e98d428f20518d2f4cfe8543303a810291688b0` / review blob `be05b885edac35d23ce59c539d84b3443a95fa36`, which accepted the V2 repairs for H-01 and M-02 but found one new blocking HIGH and one LOW hardening item:

```text
H-01 CLOSED   exact PR-number causality is not ACTIVE_NEXT authority
M-02 CLOSED   Verify chronology uses documented run_number lineage, not numeric run_id ordering
H-02 HIGH     exact source-head SHA is not positively observable after squash canonicalisation
L-01 LOW      duplicate exact_lock_objects paths need explicit fail-closed rejection
```

V3 adopts reviewer Option A. It does **not** preserve exact source commit SHA as post-canonical acquisition authority, does **not** change away from the trusted lifecycle's squash merge merely to preserve that SHA, and does **not** reintroduce PR causality.

The V3 security model is:

```text
transport commit identity != canonical acquisition identity
```

A transport commit is an independently verified pre-merge representation of expected canonical content. The canonical acquisition identity is the exact authority-bearing content that can be reconstructed from canonical Git state after squash.

### 21.1 Supersession rule — V3 controls all conflicting older wording

Section 21 supersedes Sections 7.3, 8, 10, 11, 12, 14, 15, 18, 19.1–19.8, and 20.1–20.13 wherever they conflict with V3. All older text remains in this file only as audit history.

The following historical statements are explicitly **NON-AUTHORITATIVE** for Phase B V3 implementation:

1. `expected_head_sha` is part of `canonical_acquire_id` or other post-canonical acquisition authority;
2. `H2 != H` automatically means a different canonical acquisition when both commits have the same frozen base, same expected full tree, and the same exact V3 semantic lock identity;
3. a post-canonical proof must recover or positively identify the transport head SHA that supplied the canonical tree;
4. a PR number/ref or `merged`, `merged_at`, `merge_commit_sha` proves which acquisition caused canonicalisation;
5. maximum numeric `run_id` gives the latest or authoritative Verify run;
6. Section 7.3's old statement that no `/next` field is added to canonical lock authority;
7. Section 19.1's old statement that exact lock bytes do not carry `/next` authority;
8. Section 19.7 / V2 row 51's rule that byte-identical different-head transport commits are automatically different canonical acquisitions.

Items 6–7 are superseded narrowly: a v1.3 `/next` lock MUST persist the primitive `next_binding` fields defined below so that the V3 semantic identity remains independently observable after squash. Canonical lock bytes are still **not sufficient by themselves** to grant ownership: the exact base/tree transition, current active/unexpired read-back, Ruleset proof, and the pre-merge transport Verify gate remain mandatory.

The following V2 repairs remain authoritative and unchanged:

- H-01 indirect-merge control and removal of exact PR-number causality;
- M-02 `run_number` lineage ordering, current `run_attempt`, and complete/fail-closed workflow observation;
- strict current Ruleset proof;
- strict single first-parent canonical transition;
- Phase A's read-only `ACQUIRE_PENDING` boundary;
- RELEASE priority and at-most-one trusted canonical lifecycle mutation per run.

### 21.2 Canonical observability invariant

Every authority-bearing semantic field in V3 MUST satisfy at least one of these conditions:

A. it is serialized in the exact canonical lock bytes themselves; or

B. it is deterministically and uniquely derivable from `expected_base_sha`, the exact canonical lock bytes/tree, and canonical repository data.

No authority-bearing V3 semantic field may exist only in chat state, `/next` process memory, temporary `ExpectedAcquire` / `AcquireIntent` records, PR metadata, branch/ref metadata, webhook/event payloads, transport commit metadata, or a noncanonical cache.

For V3 `/next` acquisition confirmation, the following invariant is mandatory:

```text
same expected_base_sha
AND same expected_canonical_tree_sha
AND same exact_lock_objects
=> same persisted authority-bearing semantic identity
```

Conversely, changing any of:

```text
source_epoch_id
continuation_context_id
selection_id
acquire_intent_id
```

MUST change the persisted canonical lock bytes and therefore at least one lock `blob_sha` / `bytes_sha256`, which necessarily changes the expected canonical tree SHA.

If two observations claim both:

```text
same exact canonical tree / same exact lock bytes
AND different authority-bearing semantic IDs
```

then the evidence is internally inconsistent. Return:

```text
CANONICAL_ACQUIRE_SEMANTIC_BINDING_INCONSISTENT
```

and never `ACTIVE_NEXT`. The implementation MUST NOT silently choose process-memory IDs over canonical bytes or vice versa.

### 21.3 Required persisted `next_binding` for v1.3 `/next` locks

Every lock created specifically through Village v1.3 `/next` MUST serialize an exact binding object equivalent to:

```text
"next_binding": {
  "schema_version": 1,
  "source_epoch_id": <64 lowercase hex>,
  "continuation_context_id": <64 lowercase hex>,
  "selection_id": <64 lowercase hex>,
  "acquire_intent_id": <64 lowercase hex>
}
```

The object is part of the deterministic lock payload serialized in the repository's existing JSON-subset `.yml` representation. It MUST be present identically in every lock object in the collision bundle.

The ordering is load-bearing:

1. derive `source_epoch_id`, `continuation_context_id`, `selection_id`, and `acquire_intent_id` from the already-frozen upstream records;
2. serialize those primitive IDs in `next_binding` together with the existing Task/worker/principal/base/timestamps/work-ref/collision/lock fields;
3. freeze the exact lock bytes;
4. freeze each lock blob OID and exact-byte SHA-256;
5. freeze the exact complete `exact_lock_objects` set;
6. compute/freeze `expected_canonical_tree_sha` from the exact base tree plus those exact lock additions;
7. construct `CanonicalAcquireIdentityV3` from the frozen primitives;
8. compute `canonical_acquire_id` externally.

A process-memory copy of the four IDs is useful while preparing transport, but it is **not** post-canonical evidence. Canonical-main read-back MUST parse the IDs from fresh exact lock bytes and require equality with the V3 record.

#### No self-referential canonical ID

`canonical_acquire_id` MUST NOT itself be serialized into any lock bytes that are inputs to `CanonicalAcquireIdentityV3`. No fixed-point or recursive digest definition is permitted.

The only persisted V3 semantic binding primitive is `next_binding` plus the existing lock payload fields. `canonical_acquire_id` is computed after the lock bytes, object identities, and expected tree are frozen.

### 21.4 Schema compatibility and implementation requirement

Fresh-read canonical `schemas/lock.schema.json` at main `84a046359b299950403b68bfcb190930ebbc4c3f` has root `additionalProperties: true`. The generic schema therefore already permits a `next_binding` extension without invalidating historical/manual lock payloads.

V3 does **not** globally require `next_binding` for legacy/manual locks. Instead, Phase B implementation MUST enforce this invariant for locks created or confirmed specifically as Village v1.3 `/next` acquisitions:

```text
v1.3 /next acquisition => required valid next_binding
```

A legacy lock may remain valid under the generic Village lock schema and existing lifecycle policy, but it cannot satisfy a v1.3 `/next` `ACTIVE_NEXT` proof merely because human-readable Task/worker/principal fields resemble the expected acquisition.

For a `/next` acquisition, missing/malformed/nonidentical `next_binding` is fail closed. At minimum:

```text
CANONICAL_ACQUIRE_NEXT_BINDING_MISSING
CANONICAL_ACQUIRE_NEXT_BINDING_MALFORMED
CANONICAL_ACQUIRE_SEMANTIC_BINDING_INCONSISTENT
```

No schema/settings change is required by this design candidate. If implementation later discovers that a protected schema/policy change is necessary for enforcement, it MUST record the exact proposed production change and return to the appropriate governance/security gate rather than weaken V3 observability.

### 21.5 `CanonicalAcquireIdentityV3`

The post-canonical authority-bearing acquisition record is exactly the following logical structure:

```text
CanonicalAcquireIdentityV3 = {
  "schema_version": 3,

  "source_epoch_id": ...,
  "continuation_context_id": ...,
  "selection_id": ...,
  "acquire_intent_id": ...,

  "expected_base_sha": ...,
  "expected_canonical_tree_sha": ...,

  "selected_task_id": ...,
  "worker_id": ...,
  "principal_id": ...,

  "work_ref": ...,
  "sorted_collision_keys": [...],

  "lock_id": ...,
  "acquired_at": ...,
  "expires_at": ...,

  "exact_lock_objects": [
    {
      "path": ...,
      "mode": "100644",
      "blob_sha": <40-hex Git blob OID>,
      "bytes_sha256": <64 lowercase hex>
    },
    ... sorted lexicographically by path ...
  ]
}
```

The repository namespace is fixed by this frozen contract as `51mns/AIMath-public`; observations from another repository fail before identity comparison.

The canonical ID is:

```text
canonical_acquire_id = SHA256(canonical(CanonicalAcquireIdentityV3))
```

using the canonical encoding frozen in Section 3.

The V3 identity MUST NOT contain or derive identity from any of:

```text
expected_head_sha
PR number
PR ref
merged
merged_at
merge_commit_sha
commit message
author
committer
transport commit timestamp
webhook/event delivery identity
workflow run_id magnitude
```

The exact transport head SHA still exists and remains important **before merge** for candidate inspection and CI; it is simply not a post-canonical acquisition-identity field.

#### Canonical-field observability map

For v1.3 `/next`, every V3 field is post-squash observable as follows:

| V3 field | Canonical source |
|---|---|
| `source_epoch_id` | exact lock bytes `next_binding.source_epoch_id` |
| `continuation_context_id` | exact lock bytes `next_binding.continuation_context_id` |
| `selection_id` | exact lock bytes `next_binding.selection_id` |
| `acquire_intent_id` | exact lock bytes `next_binding.acquire_intent_id` |
| `expected_base_sha` | exact lock payload `base_main_sha`, required equal to frozen B and canonical transition base |
| `expected_canonical_tree_sha` | deterministic full-tree result from B + exact lock objects and fresh canonical Git tree |
| `selected_task_id` | exact lock payload `task_id` |
| `worker_id` | exact lock payload `worker_id`; required for a v1.3 `/next` acquisition even though generic legacy schema keeps it optional |
| `principal_id` | exact lock payload `actor.id` |
| `work_ref` | exact lock payload `work_ref` |
| `sorted_collision_keys` | exact lock payload `collision_keys`, exact path-derived set, and Task collision bundle |
| `lock_id` | exact lock payload `lock_id` |
| `acquired_at` | exact lock payload `acquired_at` |
| `expires_at` | exact lock payload `expires_at` |
| `exact_lock_objects` | fresh canonical tree mode/OID + fetched exact blob bytes and SHA-256 |

Thus no authority-bearing V3 semantic field depends solely on a noncanonical transport record after squash.

### 21.6 `exact_lock_objects` uniqueness — L-01 closure

`exact_lock_objects` is an exact ordered serialization of a mathematical path set. Paths MUST be unique before canonical hashing.

The implementation MUST require, before V3 construction:

```text
len(exact_lock_objects)
==
len(set(object.path for object in exact_lock_objects))
```

and each expected path MUST occur exactly once. The list is then sorted lexicographically by `path`.

A duplicate path is not normalized, deduplicated, or last-write-wins. It fails closed with:

```text
CANONICAL_ACQUIRE_DUPLICATE_LOCK_PATH
```

Missing paths, extra paths, duplicate paths, non-`100644` modes, OID mismatch, or byte-hash mismatch all prevent construction/confirmation of the V3 identity.

### 21.7 Deterministic `expected_canonical_tree_sha`

Let:

```text
B = expected_base_sha
```

and let `Tree(B)` be the exact full repository tree at B. Before any transport candidate can become eligible, Phase B MUST deterministically construct the intended full repository tree by applying exactly the frozen `exact_lock_objects` additions to `Tree(B)` and changing no other path.

Call its root tree SHA:

```text
T = expected_canonical_tree_sha
```

The derivation MUST satisfy all of:

1. every expected lock path is absent/in the exact allowed pre-acquire state at B;
2. each inserted object has mode `100644` and exactly the frozen Git blob OID;
3. the resulting recursive Git tree is computed from B plus only those object replacements/additions;
4. no unrelated path, tree entry, mode, or blob changes;
5. `expected_canonical_tree_sha` equals the root tree SHA of that exact intended full tree;
6. the candidate head and later canonical transition are checked *against this already-frozen T*; T MUST NOT be defined by trusting whichever candidate head happens to appear.

The exact lock bytes are serialized and their blob identities are frozen before T. T is then frozen before transport eligibility and before `canonical_acquire_id` is computed.

### 21.8 Separate `TransportCandidateV3`

Transport-specific state is retained separately:

```text
TransportCandidateV3 = {
  "repository": "51mns/AIMath-public",
  "pr_number": ...,
  "head_ref": ...,
  "head_sha": ...,
  "head_tree_sha": ...,
  "base_sha": ...,

  "verify": {
    "workflow_id": 347191396,
    "workflow_path": ".github/workflows/verify.yml",
    "workflow_name": "Verify public release",
    "event": "pull_request",
    "head_sha": ...,
    "authoritative_run_number": ...,
    "run_id": <lookup identity only>,
    "current_run_attempt": ...,
    "status": ...,
    "conclusion": ...
  }
}
```

This record may be used PRE-MERGE for:

- deterministic PR/ref reuse and duplicate suppression;
- candidate discovery;
- exact candidate commit/tree inspection;
- exact-head Verify gating;
- the trusted merge call;
- debugging/audit.

It MUST NOT be an input to `canonical_acquire_id`, and none of its PR/ref/head/commit metadata is required POST-MERGE to distinguish semantically identical source commits.

Transport-level idempotency may still prefer/reuse the deterministic expected ref and exact known head. That is transport policy only. It does not make transport commit SHA canonical acquisition identity.

### 21.9 Pre-merge transport candidate eligibility

For a candidate transport head `H` to be eligible, fresh evidence MUST prove every condition below for **that exact H**:

```text
parents(H) == [B]
tree(H) == T
```

where `B = CanonicalAcquireIdentityV3.expected_base_sha` and `T = CanonicalAcquireIdentityV3.expected_canonical_tree_sha`.

Additionally:

1. compare `B -> H` changes exactly the `exact_lock_objects.path` set and no unrelated path;
2. every expected path at H is exactly mode `100644`, exact blob OID, and exact byte SHA-256;
3. every lock blob parses successfully and all lock copies have identical V3 semantic payload, including exact `next_binding`;
4. parsed `task_id`, `worker_id`, `actor.id`, `base_main_sha`, timestamps, work-ref, collision bundle, lock ID, and `next_binding` fields equal `CanonicalAcquireIdentityV3` exactly;
5. the complete workflow-run observation for this exact `H` passes the accepted V2 `run_number` / current-`run_attempt` policy;
6. this exact `H` has its own authoritative current completed-success Verify lineage;
7. current main, candidate head and candidate base are fresh-revalidated immediately before trusted merge handoff/call;
8. the fresh Ruleset gate in Section 21.13 passes.

No successful Verify on a different head SHA is transferable to H, even when the two heads have the same tree. A same-tree alternate H2 must independently pass Verify if H2 is the candidate handed to trusted merge.

### 21.10 H/H2 canonical-content equivalence and non-equivalence

#### Same canonical acquisition content

Let H and H2 satisfy:

```text
H != H2
parents(H) = parents(H2) = [B]
tree(H) = tree(H2) = T
```

and let both materialize exactly the same authority-bearing V3 semantic identity and exact lock objects, including identical persisted `next_binding`.

Then:

```text
H and H2 are different transport commits
but
H and H2 represent the SAME canonical acquisition content
```

A difference only in commit message, author, committer, commit timestamp, PR locator, or other transport metadata is non-semantic for post-canonical acquisition identity.

This does **not** let H2 borrow H's pre-merge CI. If H2 is selected for trusted merge, H2 itself must pass every Section 21.9 gate, including its own authoritative successful Verify lineage.

#### Non-equivalence

Different transport commit SHA alone is not a V3 non-equivalence condition. A candidate is non-equivalent/ineligible when any authority-bearing V3 field differs, including:

```text
expected_base_sha
expected_canonical_tree_sha
source_epoch_id
continuation_context_id
selection_id
acquire_intent_id
selected_task_id
worker_id
principal_id
work_ref
sorted_collision_keys
lock_id
acquired_at
expires_at
exact lock path set
blob OIDs
byte hashes
```

Examples:

```text
same-looking lock bytes but different B
=> NON-EQUIVALENT / ineligible

same B but different T
=> NON-EQUIVALENT / ineligible

same B/tree claim but different source_epoch_id
=> impossible if exact canonical bytes genuinely match
=> CANONICAL_ACQUIRE_SEMANTIC_BINDING_INCONSISTENT

same B/tree claim but different acquire_intent_id
=> impossible if exact canonical bytes genuinely match
=> CANONICAL_ACQUIRE_SEMANTIC_BINDING_INCONSISTENT

same human-readable Task/worker but different persisted next_binding
=> different lock bytes / OIDs / T
=> NON-EQUIVALENT
```

### 21.11 Exact canonical-main transition proof V3

Let:

```text
B = CanonicalAcquireIdentityV3.expected_base_sha
T = CanonicalAcquireIdentityV3.expected_canonical_tree_sha
C = fresh refs/heads/main SHA
```

`ACTIVE_NEXT` may be returned only after fresh GitHub commit/tree/history evidence proves every condition below.

#### A. V3 expected-content derivation

1. B equals the frozen `SelectionV1.selection_main_sha` and the exact expected lock `base_main_sha`.
2. Every primitive semantic binding field is already serialized in the exact expected lock bytes, including valid `next_binding`.
3. `exact_lock_objects` is complete, path-unique, lexicographically sorted, regular `100644`, and exact on OID/bytes hash.
4. T was deterministically frozen from the exact tree at B plus exactly those lock additions, with no unrelated path.
5. `CanonicalAcquireIdentityV3` and `canonical_acquire_id` are computed only after those primitives are frozen.

#### B. Fresh canonical first-parent history

6. fresh current main C descends from B.
7. Starting at C, fresh-read Git commit objects and follow parent index 0 toward B; incomplete/partial/cached history is not authority.
8. Identify M as the unique child of B on that observed first-parent path.
9. Require exactly:

```text
parents(M) == [B]
```

A multi-parent merge commit, unrelated intervening first-parent commit, multi-step rebase sequence, missing history, or ambiguous parent data fails closed.

#### C. Exact canonical content transition

10. `tree(M).sha == T`.
11. compare `B -> M` changes exactly `exact_lock_objects.path` and no unrelated path.
12. every expected path at M is mode `100644` with exactly the expected blob OID and exact bytes SHA-256.
13. fresh parsing of those exact M lock bytes yields the exact V3 semantic payload including `next_binding`.
14. no unrelated path/mode/object differs from the precomputed expected full tree.

This proves:

> **THIS exact canonical acquisition content became canonical in one permitted canonical transition.**

It deliberately does **not** attempt to prove which source commit or PR created M.

#### D. Current-main persistence and semantic reconstruction

15. M remains on the fresh first-parent ancestry of current main C.
16. fresh current-main tree still contains exactly the V3 `exact_lock_objects` bundle.
17. fetch and hash the current exact lock bytes; parse all lock payloads afresh.
18. reconstruct `source_epoch_id`, `continuation_context_id`, `selection_id`, and `acquire_intent_id` from current canonical `next_binding`, not process memory.
19. reconstruct/verify all other V3 semantic fields from current lock payload/canonical repository data according to Section 21.5.
20. require the reconstructed V3 semantic identity to equal the expected V3 identity exactly.
21. require the current canonical bundle to be active and unexpired now.
22. any renewal, replacement, release/reacquire, changed current lock bytes, changed timestamps, changed binding, changed collision bundle, or changed object identity makes the old acquisition fail the current `ACTIVE_NEXT` proof.

#### E. Effective Ruleset proof

23. the fresh effective Ruleset proof in Section 21.13 passes now.

The positive result remains:

```text
CANONICAL_ACQUIRE_IDENTITY_CONFIRMED
```

### 21.12 Squash semantics and H-02 closure

The intended trusted lifecycle remains squash-compatible.

A selected transport candidate H and canonical transition M may satisfy:

```text
H != M
parents(H) == [B]
parents(M) == [B]
tree(H) == tree(M) == T
```

This is expected. H's commit-object metadata and exact commit SHA are intentionally discarded from post-canonical security identity.

There is no V3 contradiction because `CanonicalAcquireIdentityV3` does not claim that H's commit SHA is canonical acquisition authority. It claims only the exact semantic/tree/object content that survives and can be independently reconstructed from canonical Git state.

Thus H-02 is remediated in the design candidate by removing the unobservable source-head claim rather than by weakening the canonical transition proof.

### 21.13 Verify separation and mandatory Ruleset gate

V3 separates two security questions.

#### PRE-MERGE transport Verify authority

For whichever `TransportCandidateV3` is selected, its exact `head_sha` MUST have its own authoritative current successful Verify lineage under the accepted V2 rules:

```text
authoritative_run_number = max(run_number among complete exact-workflow/exact-head matching set)
```

`run_id` is lookup identity only; it is never ordered numerically. Rerun semantics, current `run_attempt`, pagination completeness, result-cap fail-closed handling, and workflow identity ambiguity rules remain exactly as V2 froze them.

A same-tree H2 cannot borrow H's CI.

#### POST-MERGE canonical acquisition authority

After canonicalisation, `ACTIVE_NEXT` is determined by:

```text
CanonicalAcquireIdentityV3 semantic identity
AND exact B -> M canonical content transition
AND fresh canonical semantic reconstruction from exact lock bytes
AND fresh active/unexpired current lock
AND fresh effective Ruleset proof
```

It is no longer required to recover the selected transport head SHA from M.

#### Ruleset proof

Fresh effective/default-branch rule observation MUST positively prove all of:

```text
enforcement = active
target applies to default branch
required status context includes "verify"
strict_required_status_checks_policy = true
bypass_actors = []
current_user_can_bypass = "never"
```

Unavailable, malformed, contradictory or weakened rule evidence fails closed. Any bypass actor or `current_user_can_bypass != never` fails closed. This design changes no repository setting.

### 21.14 Alternate-head threat controls

#### Case A — same content, different commit metadata

```text
H != H2
same B
same exact T
same exact V3 semantic identity
same exact lock objects
different commit message/author/committer metadata only
```

Expected result:

```text
SAME canonical acquisition content
```

If H2 is the transport selected for merge, H2 still independently requires its own successful Verify and all fresh pre-merge gates.

#### Case B — same-looking tree/content but different base

```text
H != H2
base(H) = B
base(H2) != B
```

Expected result:

```text
NON-EQUIVALENT / NOT ELIGIBLE
```

Even if a coincidental tree SHA or human-readable lock payload appears similar, the frozen base is authority-bearing and the exact B->candidate derivation must hold.

#### Case C — same base, different tree/object content

```text
same B
but tree(H2) != T
OR any expected object/path/mode/OID/byte hash differs
```

Expected result:

```text
NON-EQUIVALENT / NOT ELIGIBLE
```

#### Case D — same B/tree claim but different semantic IDs

If an observation claims the same B, same T and same exact lock bytes while also claiming a different `source_epoch_id`, `continuation_context_id`, `selection_id`, or `acquire_intent_id`, the observation contradicts the required persisted `next_binding` invariant.

Expected result:

```text
CANONICAL_ACQUIRE_SEMANTIC_BINDING_INCONSISTENT
NOT ACTIVE_NEXT
```

No side of the contradiction is silently preferred.

### 21.15 Machine-readable V3 boundary

Representative V3 fail-closed codes include:

```text
CANONICAL_ACQUIRE_IDENTITY_MISMATCH
CANONICAL_ACQUIRE_BASE_MISMATCH
CANONICAL_ACQUIRE_TREE_MISMATCH
CANONICAL_ACQUIRE_DELTA_MISMATCH
CANONICAL_ACQUIRE_TRANSITION_MISMATCH
CANONICAL_ACQUIRE_HISTORY_UNPROVEN
NONCANONICAL_ACQUIRE_MERGE_SHAPE
CANONICAL_ACQUIRE_DUPLICATE_LOCK_PATH
CANONICAL_ACQUIRE_NEXT_BINDING_MISSING
CANONICAL_ACQUIRE_NEXT_BINDING_MALFORMED
CANONICAL_ACQUIRE_SEMANTIC_BINDING_INCONSISTENT
CANONICAL_LOCK_READBACK_MISMATCH
CANONICAL_LOCK_NOT_ACTIVE
VERIFY_WORKFLOW_IDENTITY_AMBIGUOUS
VERIFY_RUNSET_PAGINATION_FAILED
VERIFY_RUNSET_TRUNCATED
VERIFY_RUNSET_RESULT_CAP_UNPROVEN
VERIFY_RUNSET_MALFORMED
VERIFY_RUN_NUMBER_DUPLICATE_INCONSISTENT
VERIFY_AUTHORITATIVE_LINEAGE_UNREADABLE
VERIFY_AUTHORITATIVE_ATTEMPT_NOT_SUCCESS
LATEST_VERIFY_NOT_SUCCESS
RULESET_PROOF_UNAVAILABLE
RULESET_BYPASS_PRESENT
```

There is intentionally no post-canonical `CANONICAL_ACQUIRE_HEAD_MISMATCH` requirement merely because a transport commit SHA differs. Head mismatch remains a **pre-merge transport** condition when evaluating one selected candidate.

### 21.16 V3 preregistered acceptance/adversarial tests — exact total 73

The historical tests remain audit-visible. V3 does **not** preserve the number 62 artificially. It keeps valid inherited coverage, revises rows whose authority wording changed, and adds only the distinct regressions required by H-02/L-01/canonical observability.

The exact V3 implementation matrix is **73 mandatory rows**.

#### Revised inherited rows

Rows not named below retain their V2 meaning subject to the Section 21 supersession rule.

- **Row 19 revised — canonical V3 confirmation, not PR merge metadata:** an exact V3 acquisition content transition B->M plus fresh semantic reconstruction/active lock/Ruleset proof yields `ACTIVE_NEXT`; PR `merged` metadata is not a grant predicate.
- **Row 20 revised — canonical content present but wrong V3 semantic identity:** matching human-readable lock content without the exact persisted V3 binding does not yield `ACTIVE_NEXT`.
- **Row 21 strengthened — original M exact, current lock later changed:** even when the historical B->M transition exactly matched T, a later renewal/replacement/reacquisition/current lock byte change means the original V3 acquisition is not current `ACTIVE_NEXT`.
- **Row 51 replaced — same-content alternate head:** H != H2, same B, same T, same exact lock objects and exact V3 semantic identity, differing only in commit metadata => H/H2 are the SAME canonical acquisition content; do not emit PR/head creator attribution.
- **Row 55 remains the V2 replacement:** highest complete matching documented `run_number` lineage controls the exact selected head; numeric `run_id` magnitude is never chronology.
- **Row 57 clarified:** a different PR/ref pointing to the same exact transport head may confirm the same acquisition only through the V3 canonical-content transition; PR locator is not authority.

All previously accepted indirect-merge, `run_number`, rerun, workflow completeness, Ruleset, multiple RELEASE, multiple ACQUIRE, RELEASE-before-ACQUIRE, one-mutation-per-run, old-epoch replay, wrong work-ref/collision, and fresh-main barrier tests remain mandatory.

#### New rows 63–73

63. **same-tree alternate head cannot borrow Verify:** H has authoritative success; H2 != H has the same B/T/V3 content but lacks its own current authoritative success. H2 is not pre-merge eligible and cannot borrow H's CI.
64. **same-tree alternate head with stale/different base:** H2 materializes similar final content/tree presentation but `parents(H2) != [B]` or its frozen base differs. It is non-equivalent/ineligible and cannot reach trusted merge from this acquisition.
65. **same base but different canonical tree/object:** `parents(H2) == [B]` but `tree(H2) != T` or any lock path/mode/OID/hash differs. Fail candidate eligibility.
66. **same B/T/objects but claimed different source epoch:** canonical bytes parse one `next_binding.source_epoch_id` while process/observation claims another. Return `CANONICAL_ACQUIRE_SEMANTIC_BINDING_INCONSISTENT`, never `ACTIVE_NEXT`.
67. **same B/T/objects but claimed different acquire intent:** canonical bytes parse one `next_binding.acquire_intent_id` while process/observation claims another. Return semantic-binding inconsistency, never `ACTIVE_NEXT`.
68. **squash positive control:** transport H != canonical M, both have parent B and exact tree T; exact B->M lock-only transition, V3 semantic reconstruction, current active lock and Ruleset proof all pass. Confirm the same canonical acquisition content without recovering H from M.
69. **duplicate exact lock path:** duplicate path entries in `exact_lock_objects` fail before canonical hashing with `CANONICAL_ACQUIRE_DUPLICATE_LOCK_PATH`; no sorting/deduplication repair is allowed.
70. **persisted next-binding primitive mutation changes canonical objects/tree:** parameterize mutation of `source_epoch_id`, `continuation_context_id`, or `selection_id` in persisted `next_binding`; each mutation must change exact lock bytes, byte SHA-256, Git blob OID and expected canonical tree SHA.
71. **persisted acquire-intent mutation changes canonical objects/tree:** changing `next_binding.acquire_intent_id` must change exact lock bytes, byte SHA-256, Git blob OID and expected canonical tree SHA.
72. **post-squash semantic reconstruction is canonical:** after H->M squash canonicalisation, delete/alter process-memory `ExpectedAcquire` copies and re-read canonical main; only the semantic binding reconstructed from fresh exact lock bytes may satisfy the post-canonical identity comparison. Process memory alone is insufficient.
73. **missing required `/next` binding:** a lock being evaluated as a v1.3 `/next` acquisition lacks `next_binding` or one required child field. Fail closed and do not return `ACTIVE_NEXT`; legacy/manual lock validity outside `/next` is not globally changed.

No padding rows are added.

### 21.17 Phase A compatibility and inherited security boundary

V3 changes the Phase B acquisition identity only. Accepted Phase A remains exactly:

```text
ends at ACQUIRE_PENDING
no ACTIVE_NEXT authority
no GitHub mutation
no Truth/review authority
no I2/I3
no RENEW
no TAKEOVER
PENDING != ownership
```

V3 does not introduce or require:

- a new PAT or secret;
- Ruleset weakening or bypass;
- broader trusted token authority;
- `pull_request_target`;
- PR-head code in a trusted write context;
- Task/Campaign creation authority;
- Truth promotion;
- automatic review;
- direct main mutation outside the inherited trusted lifecycle;
- any Phase A authority expansion.

### 21.18 Writer-side H-02/L-01 remediation assessment

The V3 design candidate closes the writer-side contradiction identified by the fixed independent review:

```text
H-01_INDIRECT_MERGE                  = CLOSED / preserved
M-02_RUN_ORDERING                    = CLOSED / preserved
H-02_HEAD_SHA_OBSERVABILITY          = REMEDIATED_IN_V3_DESIGN_CANDIDATE
L-01_DUPLICATE_LOCK_PATH             = REMEDIATED_IN_V3_DESIGN_CANDIDATE
CANONICAL_ACQUIRE_IDENTITY_V3        = FROZEN DESIGN CANDIDATE
HEAD_SHA_POST_CANONICAL_AUTHORITY    = REMOVED
TRANSPORT_HEAD_VERIFY                = REQUIRED PRE-MERGE PER EXACT SELECTED HEAD
CANONICAL_MAIN_SINGLE_TRANSITION     = REQUIRED
CANONICAL_SEMANTIC_READBACK          = REQUIRED FROM FRESH EXACT LOCK BYTES
PR_NUMBER_AUTHORITY                  = REMOVED
RUN_NUMBER_POLICY                    = PRESERVED
SQUASH_COMPATIBILITY                 = PRESERVED
PREREGISTERED_TEST_TOTAL             = 73
CRITICAL_KNOWN                       = 0
HIGH_KNOWN                           = 0
MEDIUM_KNOWN                         = 0
INDEPENDENT_FOCUSED_REREVIEW         = REQUIRED
PHASE_B_IMPLEMENTATION_ALLOWED_NOW   = NO
READY_FOR_FOCUSED_REREVIEW           = YES
```

This is a writer-side design assessment only. It does not self-promote H-02 or L-01 to independently accepted closure. A new independent fixed-commit review MUST verify the V3 semantic observability, H/H2 equivalence, exact-tree transition, Verify separation, duplicate-path rejection, Ruleset gate, and 73-row matrix before Phase B production implementation may begin.

### 21.19 V3 stop conditions

Stop and return to design/security review if implementation discovers any of the following:

- tree/semantic identity cannot safely replace source-head SHA as post-canonical authority;
- a same-tree attacker can alter an authority-bearing V3 semantic field without changing exact canonical lock bytes/objects;
- safe confirmation would require PR-number/PR-merge causality again;
- safe confirmation would require preserving the transport H as canonical M;
- settings/secrets or trusted-token authority must change;
- trusted lifecycle authority must broaden;
- Phase A authority must expand;
- production semantics outside this frozen V3 contract are required;
- a protected schema/policy change becomes necessary but has not received its own required review.

Until the next independent fixed-commit review returns PASS with no CRITICAL/HIGH/MEDIUM blocker:

```text
PHASE_B_IMPLEMENTATION_ALLOWED_NOW = NO
```
