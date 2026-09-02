# Village v1.3 Phase B implementation acceptance oracle

TASK-ID: `AIMATH-VILLAGE-V1-3-NEXT-PHASE-B-IMPLEMENTATION-ACCEPTANCE-ORACLE`

Repository: `51mns/AIMath-public`

Base main fixed before oracle authoring: `84a046359b299950403b68bfcb190930ebbc4c3f`

Accepted Phase B V3 spec: `a482d1f4398489753589afe1ef3ed5e593a7e9c4`

Accepted spec blob: `2ddc79843cf44bd588dc1a5ff89e996ecd246de9`

Final M-03 spec rereview: `3c1be65016eda44f5efe849a6e2c2db273847db2` — `PASS`, `PHASE_B_IMPLEMENTATION_ALLOWED = YES`.

This document is intentionally written **before** any Phase B implementation branch is inspected. It is an acceptance oracle, not an implementation proposal, patch, verdict, or prediction.

## 1. Zero-trust review rule

The eventual implementation reviewer MUST derive the verdict from this oracle plus the fixed V3 spec, fresh canonical repository evidence, and the exact implementation SHA. The reviewer MUST NOT weaken, reinterpret, merge away, or invent acceptance criteria to fit the implementation that happens to exist.

Stop and return to design/security review if implementation requires any schema, workflow, Ruleset/settings, secret/token, trusted-lifecycle authority, Phase A authority, Truth/review authority, or production semantic change not already allowed by the accepted V3 contract.

The implementation review must distinguish:

- deterministic/pure semantic tests;
- exact local Git-object tests;
- mocked API-failure tests;
- fresh read-only GitHub evidence;
- trusted mutation code-path inspection.

Passing mocks alone is never sufficient for claims about GitHub workflow ordering, pagination completeness, Ruleset effectiveness, canonical commit/tree/history shape, or exact current-main read-back.

## 2. Frozen current baseline that implementation must not silently broaden

At the fixed base:

- accepted Phase A pure logic is in `scripts/village_next.py`; `CANONICAL_MUTATIONS`, `TRUTH_PROMOTIONS`, and `AUTOMATIC_LIFECYCLE_OPERATIONS` are empty, and Phase A never emits `ACTIVE_NEXT`;
- the v1.3 direct suite is `scripts/test_village_v1_3_next.py`, using deterministic `unittest`, temporary repositories, exact enum/status assertions, and parameterized `subTest` negative controls;
- `scripts/village.py test` registers the v1.3 direct suite in the canonical Village test command;
- trusted canonical mutation remains in `.github/workflows/lock-auto-activate.yml` plus `scripts/lock_auto_activate.py` / `scripts/lock_auto_activate_phase_a.py`;
- trusted workflow code is checked out from `main`, PR-head Verify is trigger/evidence only, and the trusted workflow currently has `actions: read`, `contents: write`, `pull-requests: read`;
- trusted lifecycle currently fresh-revalidates main/head/base and invokes squash merge; RELEASE is considered before ACQUIRE and a successful mutation returns immediately;
- current Ruleset `22089746`, `Village main strict lifecycle safety`, is active on the default branch, requires status context `verify`, has strict required-status-check policy enabled, has `bypass_actors = []`, and reports `current_user_can_bypass = never`.

These facts are context, not permission to preserve an insecure implementation detail. Where V3 is stricter, V3 controls.

## 3. Surface abbreviations

The row matrix uses these minimum-surface labels only to make the oracle compact. They do **not** prescribe a future file layout.

- `PA`: accepted Phase A pure derivation and its direct tests.
- `PB-CORE`: future Phase B semantic/identity/provenance logic.
- `PB-GH`: future fresh GitHub observation adapter: refs, PRs, commits, trees, blobs, workflow runs, Ruleset/effective rules.
- `PB-TRANS`: future RELEASE/ACQUIRE transport create/reuse/repair logic.
- `TL`: inherited trusted lifecycle and its trusted-main workflow.
- `TEST`: the mandatory Phase B implementation acceptance suite.

For every negative row, “otherwise valid” means the fixture must satisfy all independent prerequisites not under attack. A test that fails earlier because it is malformed, stale for an unrelated reason, unauthorized for an unrelated reason, or missing required baseline evidence does not satisfy the row.

## 4. Frozen 73-row implementation oracle

| Row | Threat frozen | Required setup | Expected observation | Expected result | Minimum likely surface | Fresh GitHub evidence required? | Negative control otherwise valid? |
|---:|---|---|---|---|---|---|---|
| 1 | Happy-path chain can grant ownership without proving every V3 link. | Exact retained source epoch; exact terminal/RELEASE evidence; fresh post-RELEASE main; accepted Phase A selection; deterministic ACQUIRE with valid `next_binding`; exact-head current Verify; trusted canonical single transition; fresh canonical read-back; active lock; Ruleset proof. | Every ID and object is derived in frozen order; B/T/objects/semantic binding all match; current canonical state reconstructs the same V3 identity. | **SUCCESS:** `CANONICAL_ACQUIRE_IDENTITY_CONFIRMED` / `ACTIVE_NEXT`; exactly one acquisition owns. | PA, PB-CORE, PB-GH, PB-TRANS, TL, TEST | **YES:** refs/main, source locks, RELEASE history, candidate commit/tree/blobs, complete Verify lineage, canonical first-parent history/current blobs, effective Ruleset. | N/A positive control; it is the baseline that paired negatives must mutate one property from. |
| 2 | Unrelated old canonical lock with same worker/principal self-authenticates. | Keep an otherwise valid request/selection but expose an unrelated active lock for same worker/principal. | V3 identity/object/binding does not equal expected acquisition. | **FAIL:** never `ACTIVE_NEXT`; deterministic acquisition/read-back mismatch. | PB-CORE, TEST | Canonical current-main evidence is required in integration review; pure fixture allowed for unit layer. | **YES:** unrelated lock itself must be schema-valid, active, unexpired. |
| 3 | Same Task but old epoch/different lock identity is mistaken for current acquisition. | Same Task/worker/principal but different source epoch and/or `lock_id`/`acquired_at`. | Exact V3 semantic identity or timestamps differ. | **FAIL:** never `ACTIVE_NEXT`; old acquisition/replay mismatch. | PB-CORE, TEST | YES for final current-main proof. | **YES:** old lock must otherwise be valid and active. |
| 4 | Human-readable Task match hides wrong workspace binding. | Candidate/canonical bundle is valid except `work_ref` differs from `research/<Task>/<worker>`. | Exact parsed work_ref differs from trusted intent/V3 identity. | **FAIL:** pre-merge ineligible or canonical read-back mismatch; never `ACTIVE_NEXT`. | PB-CORE, PB-TRANS, TEST | Candidate/canonical exact bytes should be read from Git in integration review. | **YES:** Task, worker, principal, base, binding, collision, timestamps and objects remain valid. |
| 5 | Collision bundle can be narrowed/expanded while retaining Task identity. | Valid candidate except collision-key set differs from the current canonical Task set. | Path-derived locks, payload collision keys, Task collision keys and V3 sorted set do not all equal. | **FAIL:** candidate ineligible / canonical identity mismatch. | PA, PB-CORE, PB-TRANS, TEST | Fresh Task/current-main and candidate object evidence required for integration. | **YES:** all non-collision fields remain valid. |
| 6 | Wrong worker can RELEASE or ACQUIRE another worker’s epoch. | Valid source/candidate with only worker binding changed. | Source epoch, ref/payload, intent and canonical binding disagree. | **FAIL:** no RELEASE/ACQUIRE authority and never `ACTIVE_NEXT`. | PA, PB-CORE, PB-TRANS, TL, TEST | Fresh canonical source/candidate evidence required in integration. | **YES:** principal and all other fields valid. |
| 7 | Wrong principal can impersonate acquisition authority. | Valid source/candidate with only actor/principal changed. | Authenticated/expected principal differs from exact payload/V3 identity. | **FAIL:** no RELEASE/ACQUIRE authority and never `ACTIVE_NEXT`. | PB-CORE, PB-TRANS, TL, TEST | **YES:** authenticated principal plus exact Git candidate/current-main evidence. | **YES:** worker and all non-principal fields valid. |
| 8 | Stale ACQUIRE base is treated as a reservation or mergeable acquisition. | Candidate is otherwise exact, but B is no longer current selection/main base. | Fresh main/base revalidation disagrees with `selection_main_sha`/`base_main_sha`; T derivation no longer applies. | **FAIL:** no valid PENDING reservation, merge, or `ACTIVE_NEXT`; recompute selection. | PB-GH, PB-TRANS, TL, TEST | **YES:** fresh refs/main and PR/candidate base. | **YES:** head tree/objects/Verify valid for the stale base. |
| 9 | Stale RELEASE transport is reused across main movement without bounded same-epoch proof. | Same source epoch RELEASE PR/ref exists but base is stale. | Implementation either proves same epoch and compare-before-write repair from new main, or refuses reuse. Any repair changes head and invalidates prior CI. | **FAIL old transport / bounded repair only;** repaired head requires new exact-head Verify. | PB-GH, PB-TRANS, TL, TEST | **YES:** source bundle, current main, old/new head compare, new Verify. | **YES:** stale RELEASE is otherwise exact for the same epoch. |
| 10 | Old green CI floats to a moved PR head. | Valid transport PR whose head changes after previously green Verify. | Current exact head differs from verified head/frozen transport identity. | **FAIL/PENDING:** old Verify invalid; require current exact-head authoritative success. | PB-GH, PB-TRANS, TL, TEST | **YES:** fresh PR head and workflow lineage. | **YES:** moved head is otherwise structurally valid. |
| 11 | Duplicate `/next` creates duplicate equivalent transports. | Repeat same source epoch/request with pre-existing exact RELEASE and/or ACQUIRE transport. | Deterministic identity/ref lookup reuses exact equivalent transport. | **SUCCESS idempotency:** at most one equivalent RELEASE and one equivalent ACQUIRE transport; no duplicate authority. | PB-TRANS, PB-GH, TEST | YES for integration duplicate search/ref state. | N/A positive idempotency control; conflicting object is Row 12/15. |
| 12 | Concurrent creators overwrite the deterministic ACQUIRE key. | Two creators race for same acquire intent; winner creates exact ref/object first. | Loser fresh-reads and adopts exact valid winner; non-equivalent pre-existing content is never overwritten. | **SUCCESS reuse** for exact winner; **FAIL** on non-equivalent deterministic-key collision. | PB-TRANS, PB-GH, TEST | Live write is not required for review; exact local/concurrency fixture plus read-only Git semantics acceptable. Any real write test needs separate safe harness. | **YES:** losing candidate differs only in the tested race/collision condition. |
| 13 | Old source epoch controls a newer reacquisition. | Same Task/worker/principal has a newer canonical acquisition than retained source epoch. | Fresh current source lock identity differs from frozen `SourceAcquisitionV1`. | **FAIL:** `OLD_ACQUISITION_REPLAY`; stop before RELEASE, selection, ACQUIRE. | PB-CORE, PB-GH, PB-TRANS, TEST | **YES:** current canonical lock bundle/source epoch. | **YES:** old request itself was once valid. |
| 14 | Equivalent RELEASE PR is duplicated instead of reused. | Existing open same-epoch RELEASE transport matches exact ref/base/principal/deletion set/object identity. | Fresh inspection proves equivalence. | **SUCCESS reuse:** no second equivalent RELEASE PR/ref. | PB-TRANS, PB-GH, TEST | YES for integration. | N/A positive reuse control. |
| 15 | Unrelated RELEASE at same physical ref is adopted/overwritten. | Existing RELEASE ref/PR conflicts by epoch/content/principal/Task/worker/base or unrelated delta. | Equivalence proof fails. | **FAIL:** `RELEASE_TRANSPORT_CONFLICT`; no overwrite/reuse. | PB-TRANS, PB-GH, TEST | YES for integration. | **YES:** conflicting transport must remain well-formed enough to reach equivalence check. |
| 16 | “Lock absent now” is treated as sufficient proof of RELEASE. | Source bundle absent on current main. | Implementation also proves exact retained source epoch had canonical RELEASE provenance whose base contained exact source objects and whose transition removed exactly them; then performs fresh post-RELEASE observation. | **SUCCESS past RELEASE only with provenance; otherwise FAIL/PENDING.** | PB-CORE, PB-GH, PB-TRANS, TEST | **YES:** source base objects, RELEASE commit/history/current main. | **YES:** absence alone fixture should otherwise be valid so failure is specifically missing provenance. |
| 17 | Equivalent ACQUIRE PR is duplicated. | Existing open deterministic ACQUIRE transport has same intent/base/principal, exact V3 lock bundle/tree. | Fresh inspection proves exact equivalence. | **SUCCESS reuse:** no duplicate ACQUIRE PR/ref. | PB-TRANS, PB-GH, TEST | YES for integration. | N/A positive reuse control. |
| 18 | Deterministic ACQUIRE ref without PR causes repeated PR creation. | Exact valid deterministic ref/head exists; no open equivalent PR. | Fresh duplicate search first; create at most one PR from exact ref; retries reuse. | **SUCCESS idempotency:** at most one PR. | PB-TRANS, PB-GH, TEST | Read-only review may use deterministic API fixture; real creation is not required by reviewer. | **YES:** existing ref/head must be exact and valid. |
| 19 | PR merged metadata or creator attribution becomes the grant predicate. | Exact V3 B→M single canonical content transition exists; fresh current semantic reconstruction, active lock, and Ruleset pass. PR metadata may be absent/irrelevant. | `parents(M)=[B]`, `tree(M)=T`, exact lock-only delta/objects, current canonical binding equals expected V3. | **SUCCESS:** `ACTIVE_NEXT` from canonical V3 proof; **must not require or emit PR-number creator attribution.** | PB-CORE, PB-GH, TEST | **YES:** fresh commit/tree/history/current blobs/Ruleset. | N/A positive canonical proof; PR fields should be varied without changing outcome. |
| 20 | **M-03:** forged candidate `next_binding` self-authenticates because implementation derives “expected” IDs from candidate itself. | Before parsing candidate binding, independently freeze: source epoch from fresh canonical source+exact terminal/RELEASE evidence; continuation context from fresh canonical continuation+human gate; selection from fresh post-RELEASE main+validated PENDING+hard filters+`rank_v12`+capacity; acquire intent from those trusted records. Then parameterize one forged, lowercase-64hex primitive across `source_epoch_id`, `continuation_context_id`, `selection_id`, `acquire_intent_id`; recompute candidate lock bytes/SHA-256/blob OIDs/exact objects/tree so candidate is internally self-consistent. | Candidate parses cleanly and is cryptographically/object-internally valid, but each observed primitive differs from the independently frozen trusted expected value. No expected value may originate from candidate/process-memory copied from candidate. | **FAIL:** deterministic semantic-binding mismatch equivalent to `CANONICAL_ACQUIRE_SEMANTIC_BINDING_MISMATCH`; pre-merge ineligible; no merge eligibility, ACQUIRE authority, ownership, or `ACTIVE_NEXT`. | PA, PB-CORE, PB-GH, PB-TRANS, TEST | **YES:** fresh trusted source/RELEASE, continuation gate, post-RELEASE main/PENDING/selection inputs plus exact candidate Git objects. | **MANDATORY YES:** Task, worker, principal, base, collision, work-ref, paths, schema, all four syntactic bindings, lock bytes/hashes/OIDs/tree and CI-independent structure remain valid. Rows 66/67/70/71 are supporting tests, not substitutes. |
| 21 | Historical exact M is reused after canonical lock changes. | B→M originally matched T, then current lock is renewed/replaced/reacquired or bytes/timestamps/binding/object identity change. | Fresh current-main reconstruction no longer equals original V3 identity. | **FAIL:** old acquisition is not current `ACTIVE_NEXT`. | PB-CORE, PB-GH, TEST | **YES:** historical M plus fresh current main/blob state. | **YES:** later lock must itself be valid; only identity/currentness differs. |
| 22 | Two workers select same Task and both claim ownership from stale snapshots. | Two independently eligible pending transports from same snapshot. | Only first canonical merge consumes availability; loser fresh-revalidates and reranks. | **SUCCESS one owner / FAIL loser:** never dual ownership. | PA, PB-CORE, PB-GH, TL, TEST | Fresh canonical state required at trusted mutation boundary. | **YES:** both candidates independently valid before race. |
| 23 | Overlapping collision bundles both become canonical. | Two otherwise eligible candidates share at least one canonical collision key. | First canonical merge consumes collision; second fails fresh collision revalidation. | **SUCCESS one owner / FAIL loser.** | PA, PB-CORE, TL, TEST | Fresh canonical state required before mutation. | **YES:** candidates differ only by race ordering; both pre-race valid. |
| 24 | Campaign capacity is consumed twice from stale rank snapshots. | Two eligible candidates contend for last Campaign slot. | Fresh pre-mutation capacity sees first winner; second no longer eligible and reranks. | **SUCCESS first / FAIL second.** | PA, PB-CORE, TL, TEST | Fresh current state required before trusted mutation. | **YES:** both candidates valid when slot initially free. |
| 25 | Global capacity is consumed twice from stale snapshots. | Two eligible candidates contend for last global slot. | Fresh capacity revalidation after first mutation makes second ineligible. | **SUCCESS first / FAIL second.** | PA, PB-CORE, TL, TEST | Fresh current state required. | **YES:** both candidates valid initially. |
| 26 | ACQUIRE mutates in same run while an eligible RELEASE exists. | At least one fully eligible RELEASE and at least one fully eligible ACQUIRE. | Trusted ordering evaluates RELEASE class first. | **SUCCESS RELEASE only:** ACQUIRE waits; no same-run ACQUIRE mutation. | PB-CORE, TL, TEST | **YES:** fresh open PR/candidate/current-main evidence in trusted run. | **YES:** both class candidates must be independently fully eligible. |
| 27 | One trusted run performs multiple canonical lifecycle mutations. | Provide multiple fully eligible candidates, including same-class and/or cross-class. | Mutation-call counter and canonical history show no more than one canonical lifecycle mutation. | **SUCCESS invariant:** `mutations_per_run <= 1`; second candidate untouched until future fresh run. | TL, TEST | Live production mutation not required; exact call-count/local harness plus code-path inspection mandatory. | **YES:** at least two candidates must be eligible so the test could expose a second mutation. |
| 28 | Missing/malformed strict-rule evidence silently permits merge/ownership. | Ruleset/effective-rule observation unavailable, malformed, contradictory or incomplete. | No positive proof of active/default-branch/strict `verify`/no-bypass/current-user-never-bypass. | **FAIL CLOSED:** no automatic merge, no ownership/`ACTIVE_NEXT`. | PB-GH, TL, TEST | **YES:** reviewer must fresh-read current Ruleset/effective rules for positive baseline; failure modes can be mocked. | **YES:** candidate/CI/main otherwise valid. |
| 29 | Rules exist but are weak: `strict=false` or `verify` absent. | Otherwise valid active rules response with exactly one weakened required-status property. | Strict policy or required `verify` context not proven. | **FAIL CLOSED:** no automatic merge/ownership. | PB-GH, TL, TEST | YES positive live baseline; weakened variants can be fixture-based. | **YES:** rules object otherwise structurally valid and no unrelated failure. |
| 30 | Red/missing exact-head CI is treated as reservation or activation authority. | Exact candidate head valid but authoritative current Verify is absent or not completed-success. | Verify gate reports ineligible; no finalized acquisition ownership. | **FAIL/PENDING:** no valid reservation/activation/`ACTIVE_NEXT`. | PB-GH, PB-CORE, TL, TEST | **YES:** fresh complete exact-head workflow observation for integration. | **YES:** candidate head/tree/objects/base/Rrules otherwise valid. |
| 31 | Green Verify on old head is transferred after head movement. | PR moved H→H2; H has success, H2 lacks current authoritative success. | Exact selected head is H2 and has no own success. | **FAIL:** no activation until H2 succeeds. | PB-GH, PB-TRANS, TL, TEST | **YES:** fresh PR head and both lineages. | **YES:** H2 otherwise exact/eligible. |
| 32 | Malformed lower-number candidate gains reservation authority by globally aborting scan. | Repository-wide substrate valid; first candidate malformed locally; later candidate valid. | Bad candidate is dropped locally; scan continues. | **SUCCESS later candidate remains examinable/selectable;** bad candidate gets no authority. | PB-GH, TL, TEST | Integration should exercise adapter classification; mocked malformed candidate acceptable with fresh global-baseline read. | **YES:** later candidate fully valid; malformed condition isolated to first candidate. |
| 33 | Repository-wide observation failure falls back to cache and mutates. | Main/tree/open-PR/PENDING envelope unavailable/truncated/malformed globally. | Implementation cannot establish complete fresh substrate. | **FAIL CLOSED globally:** no selection/transport mutation from cached data. | PB-GH, PA, PB-TRANS, TEST | **YES by nature:** this row tests inability to obtain fresh evidence; positive companion proves complete envelope. | **YES:** cached/previous snapshot may look valid but must not be used. |
| 34 | Disappeared/closed candidate remains reserved from old snapshot. | Candidate exists in snapshot A then closes/disappears before snapshot B. | Fresh observation removes it from candidate/PENDING set and reranks. | **SUCCESS recompute:** no ownership or stale reservation. | PB-GH, PA, PB-CORE, TEST | **YES:** fresh second observation. | **YES:** disappearance is sole changed fact. |
| 35 | Pre-RELEASE selection is reused after RELEASE changes main. | Compute/hold candidate set before canonical RELEASE, then RELEASE becomes canonical. | Post-RELEASE fresh-main barrier discards old selection/PENDING inputs. | **FAIL old selection / SUCCESS fresh recompute.** | PA, PB-GH, PB-CORE, TEST | **YES:** post-RELEASE main and source absence/provenance. | **YES:** old selection was valid at old main. |
| 36 | Main moves after selection but before ACQUIRE branch creation, yet old intent is created. | Freeze SelectionV1 at B; main moves before transport creation. | Fresh revalidation detects main != B; selection/acquire intent/ref are discarded. | **FAIL old intent; recompute from fresh main.** | PB-GH, PB-TRANS, TEST | **YES:** fresh main immediately before creation. | **YES:** old intent/candidate otherwise valid. |
| 37 | Open ACQUIRE PR becomes ownership after base stales. | Valid ACQUIRE PR at B; main advances before trusted merge. | Trusted final main/head/base revalidation rejects stale base. | **FAIL/PENDING:** no merge/ownership; fresh rerank if needed. | PB-GH, TL, TEST | **YES:** trusted-run fresh main/head/base. | **YES:** PR remains open/green/object-valid. |
| 38 | `PENDING_CLAIM` or open/green PR is interpreted as ownership. | Provide valid open, green PENDING observation without canonical acquisition. | Pending affects reservation/rank only; canonical lock ownership remains false. | **SUCCESS non-ownership invariant:** never `ACTIVE_NEXT`. | PA, PB-CORE, TEST | Fresh PENDING observation required for integration; pure rank fixture acceptable. | **YES:** PENDING record is fully valid/current. |
| 39 | Review-required result blocks RELEASE or promotes Truth. | Valid terminal result with review pending/required. | Result is terminal for lifecycle; review demand is visibility only; no Truth mutation. | **SUCCESS RELEASE eligibility may proceed;** no Truth promotion. | PA, PB-CORE, TL, TEST | Fresh canonical terminal/source evidence in integration. | N/A positive boundary; review metadata must be valid. |
| 40 | Writer auto-promotes I2/I3 or self-review as continuation authority. | Provide writer/self assessment that recommends follow-up/promotion. | It cannot create trusted review grade or autonomous I2/I3 authority. | **FAIL authority escalation:** no review/Truth promotion. | PA, PB-CORE, TEST | No live GitHub required; canonical record fixture sufficient. | **YES:** self-evaluation record syntactically valid. |
| 41 | Phase B emits automatic RENEW/TAKEOVER. | Reach stale/expired/contention conditions that might tempt renewal/takeover. | No such operation is emitted/handed to trusted lifecycle. | **FAIL any automatic RENEW/TAKEOVER;** stop/fresh reobserve instead. | PA, PB-CORE, PB-TRANS, TL, TEST | No live GitHub required for core negative; trusted workflow/code inspection mandatory. | **YES:** underlying lock/task condition otherwise valid. |
| 42 | Same-Campaign escalation bypasses required human Continuation Gate. | Major/gated terminal outcome; no applicable canonical human `CONTINUE`/`PIVOT`; also provide unrelated eligible global READY task where applicable. | Same-Campaign follow-up remains blocked; accepted Phase A global fallback semantics alone may select unrelated global READY. | **SUCCESS boundary:** no same-Campaign acquire without human gate; no invented human decision. | PA, PB-CORE, TEST | Fresh canonical decision record/current state for integration; pure Phase A fixture acceptable. | **YES:** same-Campaign task is otherwise APPROVED/eligible and global fallback is separately valid. |
| 43 | Worker/self recommendation creates or approves Task/Campaign. | Recommendation references nonexistent or non-approved Task/Campaign. | Candidate universe remains canonical existing APPROVED Tasks only. | **FAIL authority creation:** no Task/Campaign creation/approval. | PA, PB-CORE, TEST | No live GitHub required beyond canonical-state fixture. | **YES:** recommendation/evaluation itself valid. |
| 44 | Selection identity remains stable after an authority-bearing selection input changes. | Freeze selection then mutate one of: human decision blob, global admission, eligible candidate set, PENDING set, capability input, capacity. | Selection is recomputed and `selection_id` changes or acquisition is blocked. | **SUCCESS recomputation:** old intent/ref cannot be created/reused as authority. | PA, PB-CORE, PB-TRANS, TEST | Fresh current inputs required in integration. | **YES:** change one selection input at a time; all others valid. |
| 45 | Source terminal evidence changes after epoch capture but old epoch remains authoritative. | Freeze source epoch; canonical terminal blob then changes. | Fresh source derivation no longer equals old `SourceAcquisitionV1`/terminal evidence. | **FAIL/rederive:** old source epoch not silently reused. | PB-CORE, PB-GH, TEST | **YES:** exact current terminal blob/source bundle. | **YES:** changed terminal blob valid, not malformed. |
| 46 | Same Task/worker/principal but changed source lock bundle is treated as old epoch. | Freeze old source bundle; canonical bundle changes OID/bytes/lock metadata. | Exact source epoch/object identity mismatch. | **FAIL:** old RELEASE request cannot act on newer/different bundle. | PB-CORE, PB-GH, PB-TRANS, TEST | **YES:** exact current lock tree/blobs. | **YES:** new source bundle itself valid/active. |
| 47 | Lock ID is nondeterministic or collides across intents. | Compute same AcquireIntent repeatedly, then a distinct AcquireIntent. | Same intent gives exact same `LOCK-NEXT-<32 upper hex>`; distinct intent gives distinct ID except cryptographic collision assumption. | **SUCCESS determinism/distinction.** | PB-CORE, TEST | No live GitHub required. | N/A deterministic positive/paired variation. |
| 48 | Duplicate creators regenerate timestamps and thereby create divergent equivalent transports. | Same acquire intent creator retry/race after exact first payload exists. | Exact existing `acquired_at` is adopted; `expires_at` derives from it; payload bytes stay identical. | **SUCCESS reuse:** no new timestamp for same deterministic transport. | PB-TRANS, PB-CORE, TEST | No live GitHub required for deterministic fixture; integration read of existing ref may supplement. | **YES:** existing first payload exact and valid. |
| 49 | Canonical path/blob bundle is accepted by human-readable equality only. | Expected transport bundle frozen; canonical read-back has one changed path/OID/mode/byte hash/bytes. | Exact path set, mode 100644, Git OID and SHA-256/bytes equality is checked. | **FAIL:** `CANONICAL_LOCK_READBACK_MISMATCH`; never `ACTIVE_NEXT`. | PB-CORE, PB-GH, TEST | **YES:** fresh canonical tree/blob bytes for integration. | **YES:** vary exactly one object property at a time while rest remains valid. |
| 50 | Expired canonical lock remains ownership. | Exact acquisition canonical but `expires_at <= now`. | Fresh lifecycle/currentness check reports not active/unexpired. | **FAIL:** `CANONICAL_LOCK_NOT_ACTIVE`; never `ACTIVE_NEXT`. | PB-CORE, TEST | Fresh current time/current lock read-back required for integration; deterministic clock fixture acceptable. | **YES:** lock identity/objects otherwise exact. |
| 51 | V3 H/H2 equivalence drifts back to transport-head authority. | Construct H != H2 with same B, same exact T, same exact V3 semantic identity and lock objects; only commit metadata differs. | Canonical identity calculation is independent of head SHA/message/author/committer; both represent the **same canonical acquisition content**. | **SUCCESS equivalence:** same canonical content; no PR/head creator attribution. Each selected transport still needs its own Verify by Row 63. | PB-CORE, PB-GH, TEST | Exact local Git commits are mandatory; live GitHub not necessary to prove SHA-vs-tree algebra, but exact-head CI is separately live-checked under Row 63. | N/A positive equivalence control; metadata-only difference must be proven. |
| 52 | Stale webhook/workflow delivery becomes authority. | Replay old delivery containing once-valid PR/head/base/run/source fields while fresh repository state differs/stales. | Delivery triggers re-evaluation only; all authority fields are re-derived fresh. | **FAIL stale authority / SUCCESS recompute:** stop or recompute from fresh state. | PB-GH, PB-CORE, TL, TEST | **YES:** fresh current state is required to contradict stale payload. | **YES:** delivery payload itself should be syntactically valid and once-plausible. |
| 53 | Multiple eligible RELEASE candidates mutate more than one or lower malformed candidate blocks later valid one. | Case A: 2+ fully eligible RELEASEs. Case B: lower-number RELEASE malformed only candidate-locally, later one valid. | Same-class order is ascending PR number among **eligible** candidates; malformed local candidate is dropped. | **SUCCESS:** lowest eligible RELEASE selected; at most one mutation; later valid survives malformed-lower case. | PB-GH, TL, TEST | Fresh open-PR/current-main/candidate evidence required in integration. | **MANDATORY YES:** positive case candidates fully valid; malformed companion isolates local fault. |
| 54 | Multiple eligible ACQUIRE candidates mutate more than one or malformed lower candidate blocks later valid one. | No eligible RELEASE. Case A: 2+ fully eligible ACQUIREs. Case B: lower-number ACQUIRE malformed locally, later one valid. | Ascending PR among eligible ACQUIREs; local failure does not reserve/block. | **SUCCESS:** lowest eligible ACQUIRE selected; at most one mutation; later valid examinable. | PB-GH, TL, TEST | Fresh open-PR/current-main/candidate evidence required in integration. | **MANDATORY YES:** same as Row 53. |
| 55 | Verify chronology uses numeric `run_id`, incomplete pages, or stale attempt rather than documented lineage. | One exact selected H with multiple matching workflow runs. Complete matching set must be enumerated; authority is max documented `run_number`; `run_id` lookup only; then fresh-read current object/`run_attempt` of that lineage. Include pagination failure/truncation/result-cap-unproven/malformed/duplicate-run-number inconsistency companions. | Highest complete matching `run_number` is selected independent of `run_id` magnitude; incomplete result set cannot establish authority. | **SUCCESS** only if authoritative current lineage is completed-success; otherwise deterministic Verify fail-closed and never `ACTIVE_NEXT`. | PB-GH, PB-CORE, TL, TEST | **MANDATORY YES:** fresh workflow API evidence for implementation integration; pagination/error controls may be mocked but positive live read must show fields used. | **YES:** non-authoritative older runs may be green; candidate/head otherwise valid. |
| 56 | Indirect PR merge metadata grants acquisition despite noncanonical merge shape. | PR A and PR B point to same exact H/B; B is merged via multi-parent merge-commit shape; A may appear indirectly merged. | PR merged metadata ignored; canonical M has non-single-parent shape. | **FAIL:** `NONCANONICAL_ACQUIRE_MERGE_SHAPE`; never `ACTIVE_NEXT`. | PB-CORE, PB-GH, TEST | Exact Git history fixture mandatory; fresh canonical history in live integration if naturally available, no production merge required. | **YES:** H, objects, Verify and semantic identity otherwise valid. |
| 57 | Different PR/ref locator for same exact H is treated as distinct canonical authority. | Different PR/ref points to the exact same H; canonical B→M transition and V3 identity/Verify/Ruleset/current read-back all exact. | Locator does not enter canonical ID or creator attribution. | **SUCCESS:** confirm same canonical acquisition content; no PR-number creator attribution required/emitted. | PB-CORE, PB-GH, TEST | Fresh PR/current canonical evidence required for integration where exercised. | N/A positive locator-equivalence control. |
| 58 | Rerunning old run 10 after newer failed run 11 outranks by recency/run_attempt. | Same H: run_number 10 success, run_number 11 failure; rerun 10 to a newer successful attempt. | Authoritative lineage remains max run_number = 11. | **FAIL:** acquisition ineligible; older lineage rerun cannot outrank 11. | PB-GH, PB-CORE, TEST | Fresh workflow evidence strongly required in integration; deterministic fixture mandatory. | **YES:** run 10 rerun current success and candidate otherwise valid. |
| 59 | System cannot recover after prior failure except by unsafe reuse. | Same H: 10 success, 11 failure, then new matching run_number 12 completed-success. | Complete set selects 12. | **SUCCESS Verify eligibility** if all other gates pass. | PB-GH, PB-CORE, TEST | YES fresh workflow evidence/integration. | N/A positive lineage recovery. |
| 60 | Previous successful attempt remains authoritative while highest lineage is currently rerunning. | Highest run_number had prior success; current `run_attempt` is queued/in-progress or otherwise not completed-success. | Fresh current run object controls; old attempt is stale. | **FAIL/PENDING:** no Verify eligibility until current attempt completed-success. | PB-GH, PB-CORE, TEST | **YES:** fresh current run object. | **YES:** prior attempt success must genuinely exist. |
| 61 | Canonical history is accepted from partial ancestry, unrelated intervening commit, merge commit, or multi-step canonicalisation. | Build each adverse history: incomplete parent[0] chain; child after B unrelated; M multi-parent; multiple first-parent steps to intended tree. | Reviewer can identify no unique exact child M of B with `parents(M)=[B]`, `tree(M)=T`, exact lock-only delta. | **FAIL:** `CANONICAL_ACQUIRE_HISTORY_UNPROVEN` or `NONCANONICAL_ACQUIRE_MERGE_SHAPE`; never `ACTIVE_NEXT`. | PB-CORE, PB-GH, TEST | **YES** for eventual live canonical proof; exact local Git history fixtures mandatory for each negative shape. | **YES:** intended lock content/tree may otherwise be exact, forcing failure on history shape only. |
| 62 | Ruleset bypass/unreadability is ignored once CI is green. | Effective main Ruleset unreadable/malformed; strict verify proof absent; bypass actors nonempty; or current user can bypass. | Positive effective-rule proof fails. | **FAIL CLOSED:** `RULESET_PROOF_UNAVAILABLE` / `RULESET_BYPASS_PRESENT` family; cannot confirm `ACTIVE_NEXT`. | PB-GH, PB-CORE, TL, TEST | **MANDATORY YES:** fresh current Ruleset/effective-rule baseline. | **YES:** acquisition/canonical/CI otherwise exact. |
| 63 | Same-tree H2 borrows H’s successful Verify. | H != H2; same B/T/V3 content; H has authoritative current success; H2 has none/non-success. Select H2 as transport. | Verify query is keyed to exact selected H2; H result is ignored for H2 eligibility. | **FAIL H2 pre-merge eligibility;** cannot borrow CI, though Row 51 still says canonical content is equivalent. | PB-GH, PB-CORE, TEST | **MANDATORY YES:** exact-head workflow evidence. | **YES:** H2 parent/tree/objects/semantic identity otherwise exact. |
| 64 | Similar/same-presented content from stale/different base is considered equivalent to V3 acquisition. | H2 content looks same but `parents(H2) != [B]` or frozen base differs. | Exact base relation fails before merge eligibility. | **FAIL:** non-equivalent/ineligible. | PB-CORE, PB-GH, TEST | Exact Git commit evidence required; local Git fixture acceptable plus live adapter integration. | **YES:** H2 tree/locks may otherwise match. |
| 65 | Same base but different tree/object is normalized into equivalence. | `parents(H2)=[B]` but change T or one lock path/mode/OID/hash. | Candidate no longer equals precomputed T/exact object set. | **FAIL:** candidate ineligible. | PB-CORE, PB-GH, TEST | Exact candidate Git tree/blob evidence required. | **YES:** vary one object/tree property while semantic fields remain valid. |
| 66 | Process-memory `source_epoch_id` can override canonical bytes. | Same B/T/objects claim; canonical `next_binding.source_epoch_id` parses X while observation/process record claims Y. | Contradiction detected; neither side silently preferred. | **FAIL:** `CANONICAL_ACQUIRE_SEMANTIC_BINDING_INCONSISTENT`; never `ACTIVE_NEXT`. | PB-CORE, PB-GH, TEST | Fresh canonical bytes required for integration. | **YES:** both X/Y syntactically valid; all other fields equal. |
| 67 | Process-memory `acquire_intent_id` can override canonical bytes. | Same as Row 66 for acquire intent. | Contradiction detected. | **FAIL:** semantic-binding inconsistency; never `ACTIVE_NEXT`. | PB-CORE, PB-GH, TEST | Fresh canonical bytes required. | **YES:** both IDs syntactically valid; unrelated fields equal. |
| 68 | Squash causes false negative because H != M, or implementation tries to recover H post-merge. | H != canonical M; both parent B and exact tree T; B→M exact lock-only transition; canonical binding/read-back/current lock/Ruleset all pass. | V3 reconstructs authority from canonical content; transport head recovery is not required post-merge. | **SUCCESS:** same canonical acquisition content confirmed. | PB-CORE, PB-GH, TEST | Exact Git commit/tree/history evidence required; local squash-shape fixture mandatory and fresh canonical read adapter must support same proof. | N/A positive squash control. |
| 69 | Duplicate `exact_lock_objects.path` is silently sorted/deduplicated or last-write-wins. | Construct otherwise valid V3 object list with duplicate path. | Uniqueness check occurs before canonical hashing/tree derivation. | **FAIL:** `CANONICAL_ACQUIRE_DUPLICATE_LOCK_PATH`; no normalization repair. | PB-CORE, TEST | No live GitHub required. | **YES:** duplicate entries otherwise valid; ensure failure is duplicate path only. |
| 70 | Mutating persisted source/continuation/selection primitive does not change canonical objects/tree. | Parameterize exactly one mutation of `source_epoch_id`, `continuation_context_id`, `selection_id`; deterministically reserialize all locks. | Exact lock bytes, bytes SHA-256, Git blob OID, and expected canonical tree SHA each change. | **SUCCESS cryptographic binding invariant:** changed semantic primitive cannot retain same canonical object/tree identity. | PB-CORE, TEST | No live GitHub required; **real Git blob/tree hashing**, not mocked hashes, is mandatory. | **YES:** mutation remains valid 64hex and all unrelated payload fields fixed. |
| 71 | Mutating persisted `acquire_intent_id` does not change canonical objects/tree. | Same as Row 70 for acquire intent. | Bytes/hash/blob OID/T all change. | **SUCCESS cryptographic binding invariant.** | PB-CORE, TEST | No live GitHub required; real Git object hashing mandatory. | **YES:** only acquire intent primitive changes. |
| 72 | Post-squash authority survives only in process memory and cannot be reconstructed canonically. | After H→M squash-shaped canonicalisation, delete or deliberately corrupt process-memory `ExpectedAcquire`/temporary copies; re-read exact canonical main locks. | V3 semantic primitives are parsed afresh from `next_binding`; canonical reconstruction alone can match expected trusted identity. Process memory alone cannot satisfy it. | **SUCCESS canonical reconstruction** when bytes are exact; **FAIL** if only stale process memory matches. | PB-CORE, PB-GH, TEST | **YES:** fresh canonical lock bytes/tree in integration; exact local Git fixture mandatory. | **YES:** canonical bytes remain exact in positive half; process-memory corruption is the only change. |
| 73 | Missing `/next` binding is accepted because generic legacy schema allows extra/optional fields. | Evaluate a lock specifically as v1.3 `/next`; remove `next_binding` or one required child. Also retain a separate legacy/manual-lock compatibility control. | `/next` evaluator distinguishes legacy generic validity from V3 acquisition proof. | **FAIL `/next`:** binding missing/malformed, never `ACTIVE_NEXT`; **legacy/manual validity outside `/next` remains unchanged.** | PB-CORE, TEST | No live GitHub required for schema/semantic unit; canonical integration read-back should also reject `/next` candidate. | **YES:** lock is otherwise schema-valid and would remain valid in legacy/manual context. |

## 5. High-risk implementation checks frozen in addition to row assertions

These checks are review gates. They do not add Row 74; they define how the 73 rows must be judged.

### 5.1 Authority drift

Block acceptance if any authority-bearing post-canonical V3 decision depends on:

- transport `head_sha` after canonicalisation;
- PR number/ref, `merged`, `merged_at`, `merge_commit_sha`, PR creator attribution;
- commit message, author, committer or transport timestamp;
- webhook/event delivery contents;
- numeric magnitude of workflow `run_id`;
- cached/noncanonical process state when canonical evidence is required.

`expected_head_sha` remains a **pre-merge exact selected transport** identity only.

### 5.2 Forbidden new write authority

The implementation MUST NOT add another canonical mutation path around the inherited trusted lifecycle. Transport ref/PR preparation is transport activity, not ownership. Canonical lock mutation must remain gated by trusted-main code, fresh revalidation, strict Ruleset proof, and the at-most-one rule.

Any new direct main write, alternate merge actor, write-capable helper outside the reviewed lifecycle boundary, or mutation hidden inside Phase A is a blocker and requires design/security review.

### 5.3 PR-head trusted code

The trusted write context MUST execute trusted default-branch code. PR-head code may be inspected and may produce read-only Verify evidence, but MUST NOT become executable trusted mutation logic through `pull_request_target`, dynamic checkout/import, artifact execution, generated Python/shell, or equivalent indirection.

### 5.4 Token/secret expansion

Block acceptance for:

- a new PAT or secret;
- broader workflow token permissions than the accepted boundary without separate review;
- credential persistence into untrusted checkout;
- a token being passed to PR-head-controlled code;
- reliance on bypass privilege.

### 5.5 Schema drift

No global lock-schema change is required by V3 because generic legacy locks remain compatible. If implementation changes `schemas/lock.schema.json`, makes `next_binding` globally mandatory, weakens lock validation, or introduces another authority-bearing schema, stop and return to governance/security review.

### 5.6 Workflow drift

No workflow change is required by this oracle. Any change to trigger type, trusted checkout source, token permissions, concurrency, Verify identity, or trusted mutation workflow requires explicit scope review. `pull_request_target` is forbidden by the accepted boundary.

### 5.7 Phase A regression

Re-run the accepted Phase A direct suite and preserve these exact boundaries:

```text
Phase A ends at ACQUIRE_PENDING
Phase A never returns ACTIVE_NEXT
CANONICAL_MUTATIONS = empty
TRUTH_PROMOTIONS = empty
AUTOMATIC_LIFECYCLE_OPERATIONS = empty
no network/write side effect in the pure derivation core
```

Phase B may consume Phase A output; it may not rewrite Phase A authority.

### 5.8 Truth/review mutation

Block any implementation that automatically changes Truth state, emits autonomous I2/I3, performs writer self-review promotion, creates/approves Tasks or Campaigns, or converts review demand into ownership continuation authority.

### 5.9 Tests that pass for the wrong reason

Every negative test must prove all of the following:

1. the positive baseline passes before the targeted mutation;
2. only the threat-specific property is changed;
3. candidate-local structure remains valid unless malformed structure is the threat;
4. the expected specific fail-closed family is asserted, not merely “not ACTIVE_NEXT”;
5. no earlier unrelated guard is the actual rejection reason;
6. mutation call count remains zero for unauthorized cases.

Row 20 has the strongest form of this requirement: the forged candidate must rebuild its own exact bytes, Git OIDs, object manifest and T consistently and still fail only on comparison with independently re-derived trusted semantic IDs.

### 5.10 Mock-only false confidence

Mocked API responses are useful for failure branches but insufficient by themselves. Implementation acceptance requires:

- real SHA-256 over exact bytes;
- real Git blob OID computation;
- real Git tree construction/identity for B/T/H/H2/M fixtures;
- exact local commit-parent/history fixtures for single-parent, merge-commit and multi-step cases;
- fresh read-only GitHub confirmation of current main, current Ruleset/effective status baseline, current Verify workflow identity, and actual workflow-run field shapes used by the adapter;
- explicit proof that pagination loops continue to completion and fail closed on page/error/result-cap uncertainty.

### 5.11 Candidate malformed shortcuts

For semantic, authority, race, Verify, Ruleset, history and object-identity negatives, malformed JSON/path/schema is not an acceptable substitute. The candidate must reach the exact gate under test. Parser/schema negatives are acceptable only when malformed structure itself is the frozen threat, such as the missing/malformed `/next` binding branch of Row 73.

## 6. Canonical B/T/M proof oracle

The eventual implementation review MUST positively locate one code path that enforces this exact ordering, with no candidate-derived shortcut:

```text
B := frozen SelectionV1.selection_main_sha
   = exact lock base_main_sha

exact lock bytes and next_binding primitives frozen
-> exact bytes SHA-256 and Git blob OIDs frozen
-> complete unique exact_lock_objects frozen
-> T := deterministic full Tree(B) plus only those exact lock additions
-> CanonicalAcquireIdentityV3 frozen
-> canonical_acquire_id = SHA256(canonical(V3))
```

Pre-merge selected transport H must satisfy:

```text
parents(H) == [B]
tree(H) == T
compare(B,H) changes exactly exact_lock_objects.path
all lock mode/OID/bytes/semantic fields exact
H has its own complete authoritative current Verify success
fresh main/head/base revalidated
fresh Ruleset gate passes
```

Post-canonical proof must satisfy:

```text
C := fresh current main
follow fresh parent[0] history from C to B
M := unique child of B on that path
parents(M) == [B]
tree(M) == T
compare(B,M) changes exactly exact_lock_objects.path
fresh M/current lock bytes reconstruct exact V3 binding
M remains on current first-parent ancestry
current bundle remains exact, active and unexpired
fresh Ruleset gate passes
```

The implementation MUST NOT require `M == H`; the squash positive control Row 68 requires H and M to differ while content identity remains exact.

## 7. Verify/run-number and pagination oracle

For exact selected head H, acceptance requires a complete observation for the exact repository/workflow identity:

```text
repository    = 51mns/AIMath-public
workflow_id   = 347191396
workflow_path = .github/workflows/verify.yml
workflow_name = Verify public release
event         = pull_request
head_sha      = H
```

The adapter must:

1. paginate until completeness is proven;
2. fail closed on pagination error, truncation, malformed envelope, contradictory duplicate lineage, or result-cap uncertainty;
3. choose `max(run_number)` from the complete matching lineage set;
4. use `run_id` only to fresh-read that selected lineage;
5. require its current `run_number` still equals the authoritative number;
6. observe its current `run_attempt`;
7. require current `status=completed` and `conclusion=success`.

A same-tree H2 has a separate exact-head lineage and cannot borrow H’s result.

## 8. Ruleset oracle

A fresh effective/default-branch observation must positively establish all six facts at review/run time:

```text
enforcement = active
target applies to default branch
required status context includes "verify"
strict_required_status_checks_policy = true
bypass_actors = []
current_user_can_bypass = "never"
```

The fixed-base repository Ruleset object currently satisfies these values, but implementation must not pin authority to Ruleset ID `22089746` alone. The security predicate is the fresh effective rule state. Unavailable, malformed, contradictory or weakened observations fail closed.

## 9. Source RELEASE provenance oracle

A retained source epoch may advance past RELEASE only when fresh canonical evidence proves the exact source acquisition and exact terminal eligibility, then one of:

- an exact same-epoch RELEASE transport is currently pending and valid; or
- the source bundle is absent and canonical history proves a RELEASE transition whose base contained the exact retained source lock objects and whose delta removed exactly that bundle.

Same Task/worker/principal is insufficient. Any changed `lock_id`, `acquired_at`, base, work-ref, collision bundle, terminal blob, path set or blob identity means the old source epoch cannot control the new acquisition.

After RELEASE becomes canonical, all pre-RELEASE rank/PENDING/selection evidence is discarded and fresh post-RELEASE main is mandatory.

## 10. Human Continuation Gate oracle

For outcomes that require the human gate, same-Campaign continuation authority exists only through the applicable canonical human decision. Absence cannot be replaced by caller flags, chat prose, worker recommendation, independent evaluation, a high score, or an existing follow-up Task. Evaluation/recommendation may affect bounded visibility/ranking only after canonical Task eligibility is already established.

## 11. Multiple candidates, class priority and one-mutation oracle

Implementation acceptance requires explicit executable coverage of all four statements simultaneously:

```text
eligible RELEASE > eligible ACQUIRE
ascending PR number orders only fully eligible candidates within a class
candidate-local malformed lower PR does not block later valid candidates
at most one trusted canonical lifecycle mutation occurs per run
```

Rows 26, 27, 53 and 54 are jointly load-bearing; none substitutes for another.

## 12. CI requirements for the eventual implementation review

At minimum, the implementation SHA must pass:

- existing `python3 scripts/village.py test` including accepted Phase A v1.3 direct suite;
- existing v1.1/v1.2/v1.2.1 direct suites already run by Verify;
- a new deterministic Phase B acceptance suite with **exactly the 73 frozen row obligations**, where parameterized companions remain part of their numbered row rather than padding new row numbers;
- DCO, workflow structural security, public safety/layout, Village validate/status/rank, REUSE/SPDX, and the rest of current `Verify public release` checks;
- implementation-specific real-Git object/history tests for B/T/H/H2/M;
- tests for workflow pagination/run-number/current-attempt logic;
- tests for effective Ruleset fail-closed semantics;
- tests showing unauthorized canonical mutation call count is zero and authorized trusted-run mutation count is at most one.

A future implementation may organize files differently, but the reviewer must be able to map every test case back to Row 1…73 unambiguously.

## 13. Live GitHub evidence requirements for the eventual fixed-commit review

The reviewer must fresh-read, not trust writer prose, at least:

1. exact implementation target commit and parent/diff;
2. current `refs/heads/main` and whether the implementation was based on the required canonical base;
3. current trusted workflow files and their blob IDs;
4. current Ruleset/effective default-branch rule state;
5. current Verify workflow identity and workflow-run response fields used by the implementation;
6. exact candidate/read adapter endpoint contracts for commit/tree/blob/history observations;
7. exact implementation branch changed-file set to detect schema/workflow/settings/secret/authority drift;
8. CI runs for the exact implementation head and the authoritative current attempt;
9. remote implementation artifact blobs and test blobs after commit, not merely local output pasted by the writer.

No actual production RELEASE/ACQUIRE merge is required merely to review the implementation; dangerous or authority-changing live writes are not justified by this oracle.

## 14. Forbidden implementation acceptance shortcuts

The eventual reviewer must reject any implementation that passes its own tests by:

- deriving expected `next_binding` from the candidate;
- treating internally self-consistent candidate objects as semantic authenticity;
- using one-page workflow results without completeness proof;
- sorting by numeric `run_id`;
- accepting any old green attempt when the authoritative lineage/current attempt is not success;
- letting H2 reuse H’s Verify;
- putting head SHA or PR identity back into post-canonical authority;
- treating canonical lock presence alone as proof of source RELEASE or acquisition provenance;
- trusting process memory instead of fresh canonical `next_binding` read-back;
- trusting a Ruleset ID/name without proving the current effective properties;
- normalizing duplicate lock paths;
- using malformed candidate fixtures to claim semantic negative coverage;
- executing PR-head-controlled code in the trusted write context;
- broadening token/secret/write authority;
- mutating Truth/review/Task/Campaign authority;
- performing more than one trusted canonical lifecycle mutation in one run.

## 15. Oracle readiness decision

The accepted V3 spec is internally sufficient to preregister this implementation oracle. The M-03 rereview explicitly closes the final Row-20 contract gap while preserving the 73-row total and the previously accepted V3 authority model.

```text
ROW_COUNT = 73
ROW_MAPPING_COMPLETE = YES
FUTURE_IMPLEMENTATION_INSPECTED = NO
PRODUCTION_PATCH_WRITTEN = NO
WORKFLOW_CHANGED = NO
SCHEMA_CHANGED = NO
SETTINGS_CHANGED = NO
AUTHORITY_EXPANDED = NO
VERDICT = ORACLE_READY
```

Use this fixed oracle as the acceptance target for the eventual independent Phase B implementation review. Do not edit the criteria after seeing the writer implementation merely to make the implementation pass.
