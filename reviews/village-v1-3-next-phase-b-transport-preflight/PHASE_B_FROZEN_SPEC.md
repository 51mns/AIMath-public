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
