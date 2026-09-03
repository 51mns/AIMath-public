# AIMath Village Architecture v1.3 — `/next` Phase B production orchestration

**Status:** IMPLEMENTATION CANDIDATE — INDEPENDENT IMPLEMENTATION REVIEW REQUIRED  
**Frozen Phase B specification:** `a482d1f4398489753589afe1ef3ed5e593a7e9c4`  
**Frozen specification path:** `reviews/village-v1-3-next-phase-b-transport-preflight/PHASE_B_FROZEN_SPEC.md`  
**Frozen specification blob:** `2ddc79843cf44bd588dc1a5ff89e996ecd246de9`  
**Final implementation gate review:** `3c1be65016eda44f5efe849a6e2c2db273847db2` (`PASS`)  
**Implementation base:** `84a046359b299950403b68bfcb190930ebbc4c3f`

Phase B completes the production orchestration around the already accepted Phase A pure `/next` core. It does **not** replace the trusted canonical lifecycle writer. `scripts/lock_auto_activate.py` remains the only narrow automatic primitive that may merge one canonical `RELEASE` or `ACQUIRE` lock transition.

## 1. Authority boundary

The implementation is split deliberately:

- `scripts/village_next.py` remains the Phase A read-only terminal/continuation/selection core and still stops at `ACQUIRE_PENDING`.
- `scripts/village_next_phase_b.py` performs fresh GitHub observation, deterministic RELEASE/ACQUIRE transport construction/reuse, semantic identity derivation, Verify/Ruleset checks, exact Git-object checks and post-canonical read-back.
- `scripts/lock_auto_activate.py` is unchanged. It remains the only automatic canonical mutation/merge primitive.
- `scripts/village.py next ...` is the reviewed operator surface for Phase B.

Phase B has no Truth Layer promotion authority, no independent-review grading authority, no Task/Campaign creation authority, and no automatic `RENEW` or `TAKEOVER` path. Branch/PR metadata, chat text, worker prose and local retry state are never canonical ownership authority.

## 2. End-to-end operator state flow

The implemented flow is:

`ACTIVE_WORK`
→ canonical terminal recognition
→ `RELEASE_PENDING`
→ deterministic lock-only RELEASE transport
→ exact-head Verify + fresh Ruleset gate
→ handoff to the unchanged trusted RELEASE primitive
→ fresh post-RELEASE canonical barrier
→ continuation derivation
→ deterministic Phase A selection
→ `ACQUIRE_PENDING`
→ deterministic V3 lock-only ACQUIRE transport
→ exact-head Verify + fresh Ruleset + exact candidate gate
→ handoff to the unchanged trusted ACQUIRE primitive
→ fresh canonical first-parent/object/byte read-back
→ `ACTIVE_NEXT`.

A pending RELEASE/ACQUIRE PR is a transport/reservation only. It is never ownership. `ACTIVE_NEXT` is returned only after the canonical V3 transition and the current unexpired lock bytes are reconstructed and verified from fresh main.

## 3. Source epoch and RELEASE barrier

Before RELEASE construction, Phase B freezes `SourceAcquisitionV1` from fresh canonical evidence:

- repository namespace,
- exact source Task/worker/principal,
- source lock id/acquisition/base/work ref/collision bundle,
- exact source lock path→blob-OID bundle,
- exact canonical terminal class/path/blob OID/outcome.

Its SHA-256 is `source_epoch_id`. A changed source lock acquisition, terminal blob or source lock object bundle therefore changes the epoch.

The RELEASE ref remains the inherited deterministic `release/<TASK-ID>/<worker-id>`. Existing same-epoch RELEASE content may be reused; stale content is repairable only after proving that the prior head was itself an exact deletion of the same frozen source bundle. Unrelated content fails closed.

After canonical release, mere absence of the old lock is insufficient. The post-RELEASE barrier fresh-reads first-parent history and proves:

1. the retained RELEASE transport head is a single-parent transition from the retained RELEASE base;
2. that exact head has its own authoritative Verify success;
3. its tree is the deterministic source-bundle-deletion tree;
4. the RELEASE base contained the exact frozen source lock object bundle;
5. its delta removed exactly those source lock paths and nothing else;
6. canonical first-parent history contains the corresponding single-parent base→release transition with the same tree/delta; and
7. the source terminal blob is still the frozen terminal blob and the old source bundle is still absent on fresh current main.

Only then can continuation and selection run.

## 4. Semantic identity chain

Expected semantic IDs are derived from trusted observations in this order:

1. `SourceAcquisitionV1` → `source_epoch_id`
2. `ContinuationContextV1` → `continuation_context_id`
3. `SelectionV1` → `selection_id`
4. `AcquireIntentV1` → `acquire_intent_id`

`ContinuationContextV1` binds fresh post-RELEASE main, canonical terminal evidence, Campaign/global admission state, any canonical human Continuation Gate blob, restrictive stop/dependency flags, Phase A continuation decision and capability profile.

`SelectionV1` binds the fresh selection main, continuation context, complete validated pending-observation digest, hard-eligible set, deterministic rank order, selected Task/relation and worker/principal.

`AcquireIntentV1` binds the selected Task, selection/main/context, worker/principal, deterministic worker `work_ref` and exact collision bundle.

The persisted retry file under `.git/village-next-phase-b.json` is continuity only. On every use its Source/Continuation/Selection/Intent digests and cross-links are recomputed before any stored V3 identity is trusted. The file cannot itself produce ownership; canonical bytes/history are still required for `ACTIVE_NEXT`.

## 5. `next_binding`

Every Phase B `/next` ACQUIRE lock payload persists exactly:

```json
{
  "next_binding": {
    "schema_version": 1,
    "source_epoch_id": "<64 hex>",
    "continuation_context_id": "<64 hex>",
    "selection_id": "<64 hex>",
    "acquire_intent_id": "<64 hex>"
  }
}
```

The four expected values are frozen **before** candidate lock bytes are parsed. Candidate `next_binding` is observation only and can never authenticate or seed its own expected identity.

Changing any binding value changes exact lock bytes, bytes SHA-256, Git blob OID and deterministic canonical tree. All collision-key copies must contain byte-equivalent payloads.

## 6. CanonicalAcquireIdentityV3

`CanonicalAcquireIdentityV3` contains:

- `schema_version = 3`
- the four semantic IDs above
- `expected_base_sha = B`
- deterministic `expected_canonical_tree_sha = T`
- selected Task, worker, principal
- deterministic `work_ref`
- sorted exact collision keys
- deterministic lock id
- first-creator `acquired_at` and derived `expires_at`
- sorted `exact_lock_objects`, each with path, mode `100644`, Git blob OID and SHA-256 of exact bytes.

Duplicate `exact_lock_objects.path` values fail with `CANONICAL_ACQUIRE_DUPLICATE_LOCK_PATH` before canonical identity hashing.

Post-canonical authority intentionally excludes transport and merge locators/metadata: transport head SHA, PR number, PR ref, merged fields, commit message, author/committer/timestamp, webhook delivery and `run_id` magnitude are not V3 identity fields.

## 7. Deterministic ACQUIRE transport

The ACQUIRE transport ref is:

`next-acquire/<acquire_intent_id>/<TASK-ID>/<worker-id>`.

The first creator fixes `acquired_at`; same-intent retries adopt exact existing candidate bytes/timestamp rather than generating a new lease time. Ref collisions are accepted only when the existing head is a single-parent child of B with the exact expected V3 lock bytes/object identities/tree. Otherwise the key collision fails closed.

For a new head H:

- `parents(H) == [B]`
- `tree(H) == T`
- the B→H delta is exactly the expected lock-only path set
- the lock payload and `next_binding` equal independently derived expected semantics
- exact lock bytes hash to the frozen SHA-256 and Git blob OIDs.

H itself is transport identity only. Another head H2 with the same B/T/V3 content represents the same canonical acquisition **content**, but H2 must obtain its own Verify evidence.

## 8. Verify lineage

Phase B does not order workflow runs by `run_id`.

For the exact frozen workflow identity (`Verify public release`, `.github/workflows/verify.yml`, workflow id `347191396`, `pull_request`) and exact candidate head SHA:

1. obtain a complete bounded/paginated workflow-run observation;
2. fail closed if the result set is malformed, incomplete, inconsistent or hits the bounded result cap;
3. choose the highest matching `run_number` as authoritative;
4. use its `run_id` only to fetch the current record for that lineage;
5. require the current `run_attempt` to be `completed/success`.

A lower run's success cannot override a higher failed/in-progress lineage. Re-running an older run cannot outrank the newer `run_number`. A later higher successful run may recover eligibility. If the authoritative run is rerun and its current attempt is in progress or failed, eligibility is lost until the current attempt succeeds.

Transport PRs are initially draft so the unchanged trusted lifecycle cannot act before Phase B completes the full V3/Ruleset gate. After an exact-head success is independently accepted, Phase B marks the PR ready and reruns that **same authoritative exact-head lineage by lookup ID**. This repository's trusted `workflow_run` lifecycle then receives a fresh completion trigger without changing H. The rerun does not make `run_id` an ordering authority.

## 9. Ruleset gate

Mutation readiness requires fresh positive proof that an active default-branch Ruleset:

- targets the default branch,
- requires status context `verify`,
- has `strict_required_status_checks_policy = true`,
- has `bypass_actors = []`, and
- reports `current_user_can_bypass = "never"`.

Both effective branch rules and detailed applicable Ruleset data are checked. Unreadable, weakened, bypassable or malformed observations fail closed. No settings mutation is performed.

## 10. Canonical transition and squash handling

After trusted ACQUIRE, Phase B freezes no merge metadata. It fresh-reads current first-parent history C back to B and locates the canonical child M of B. Confirmation requires:

- `parents(M) == [B]`
- `tree(M) == T`
- exact B→M lock-only delta
- exact path/mode/blob-OID objects
- current main still contains those same exact objects
- current exact bytes still have the frozen SHA-256 and reconstruct the frozen `next_binding`/V3 fields
- the current lock is active/unexpired
- fresh Ruleset proof still passes.

`H != M` is explicitly permitted. A squash-created canonical commit may differ in commit SHA/message/author/timestamp while carrying the same B/T/V3 content. A merge commit or indirect/multi-parent transition is noncanonical and fails closed.

## 11. Idempotency and races

The implementation preserves these fail-closed rules:

- deterministic RELEASE and ACQUIRE refs;
- duplicate creator compare-before-write/adopt-exact-winner behaviour;
- immutable first-creator ACQUIRE timestamp;
- same-intent retry without re-ranking merely because its own pending PR exists;
- source-epoch replay rejection;
- exact worker/principal/work-ref/collision binding;
- RELEASE priority over ACQUIRE in the inherited trusted lifecycle;
- one canonical mutation per trusted lifecycle run;
- fresh main/head/base revalidation before handoff;
- current-main movement invalidates stale selection/acquire transport;
- pending PRs are never ownership;
- no automatic `RENEW`/`TAKEOVER`.

Candidate-local malformed observations remove only that candidate from scheduling observations; repository-wide ambiguity/incompleteness fails the whole Phase B action closed.

## 12. CLI/operator flow

The operator surface is:

```text
python3 scripts/village.py next \
  --task-id TASK-... \
  --worker-id w-... \
  --principal-id gh:<login> \
  --github-write yes
```

The command reads the GitHub token from `GITHUB_TOKEN` by default; `--github-token-env` may name a different already-provided environment variable. The token is not written to repository files or the Phase B retry state.

The local checkout must be exactly fresh remote `main`; otherwise Phase B refuses to derive from stale trusted code/state. After a canonical RELEASE or ACQUIRE advances main, update the local checkout to that exact main commit and rerun the same command. Repeated invocations are expected: one invocation may stage/verify/handoff a transport and a later invocation observes its canonical result.

The operator credential must already be authorized to create repository refs/PRs and to request an Actions rerun. Phase B does not create or modify repository secrets, PATs, Rulesets, settings or workflows.

The retry state defaults to `.git/village-next-phase-b.json` (mode 0600 where supported), outside tracked repository content. It is a deterministic continuity record, not canonical authority.

## 13. Fail-closed categories

Representative stable failure classes include:

- source epoch/terminal/release provenance unavailable or replayed;
- malformed/missing/inconsistent `next_binding`;
- V3 semantic-binding mismatch;
- duplicate exact lock path;
- base/tree/delta/object/byte mismatch;
- stale/moved main or transport head;
- incomplete/ambiguous Verify run observation;
- authoritative Verify current attempt not successful;
- weakened/unreadable/bypassable Ruleset;
- noncanonical first-parent/squash shape;
- current canonical lock changed or expired;
- deterministic transport key collision;
- repository-wide fresh observation unavailable;
- stale trusted local main.

All such failures produce no ownership and no direct Truth/research mutation.

## 14. Explicit non-authorities and deferred work

Phase B does **not** make any of these authoritative:

- PR number/ref or PR body/title;
- transport head SHA after canonical merge;
- merge/squash metadata;
- commit messages/authors/timestamps;
- `run_id` ordering or webhook delivery ordering;
- local retry-state contents by themselves;
- a bare canonical lock without exact V3 semantic reconstruction;
- worker recommendations or chat prose;
- PENDING_CLAIM as ownership;
- review demand as Truth promotion;
- autonomous I2/I3 assignment;
- Task/Campaign creation;
- `RENEW`/`TAKEOVER`.

Review-autonomy and any future Truth/research orchestration remain separate projects. No workflow, schema, `lock_auto_activate.py`, Ruleset, secret or settings mutation is part of this implementation.

## 15. Exact 73-row implementation contract

`scripts/test_village_v1_3_next_phase_b.py` contains exactly 73 `unittest` methods and an explicit `SPEC_ROW_TO_TEST` map from rows 1 through 73, with no padding test. Import-time assertions require all 73 row numbers exactly once and require the class to contain exactly 73 `test_...` methods.

Row 20 is one parameterized semantic-authenticity test. For each forged primitive (`source_epoch_id`, `continuation_context_id`, `selection_id`, `acquire_intent_id`) it first derives and freezes the trusted expected Source→Continuation→Selection→Intent chain, then builds a candidate whose forged binding is internally self-consistent, recomputes exact bytes, SHA-256, Git blob OID, `exact_lock_objects` and candidate tree, and rejects it solely because the candidate binding differs from the independently derived expected ID.

Rows 63–73 cover the accepted V3 additions: per-head Verify non-borrowing, alternate-head base/tree attacks, semantic source/intent inconsistencies, squash-positive H≠M, duplicate-path rejection, binding→bytes/OID/tree propagation, post-squash canonical-byte reconstruction and missing-`next_binding` legacy isolation.
