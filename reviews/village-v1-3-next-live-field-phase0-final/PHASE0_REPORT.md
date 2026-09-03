# Village v1.3 `/next` live-field Phase 0 final report

## Disposition

**Verdict: `BLOCKED`**

This Phase-0 lane remained read-only with respect to production state. No source ACQUIRE, terminal marker, RELEASE, next ACQUIRE, canonical lock, lifecycle PR, Ruleset/settings change, claim/outcome/research mutation, Truth Layer mutation, Task/Campaign mutation, evaluation, failed route, or main mutation was performed.

The sole blocker is the preregistered effective-Ruleset read requirement. The detailed active Ruleset is positively readable and has the expected strict settings, but the authenticated interface available to this Phase-0 lane cannot positively read the effective branch-rules endpoint for `main`. The accepted Phase-B implementation itself requires that effective observation and fails closed when it is unavailable. Substituting the detailed Ruleset record for the missing effective branch-rules observation would weaken the preregistered gate, so production mutation must not begin.

## 1. Current main and accepted implementation

Fresh canonical main:

- `M0 = 7dc8541c0a9e19f37910e06bc4738375c4c7af00`
- root tree: `8ea11092584142fb1b0dcc724a50e0e635e26eea`

Expected Phase-B/Stage-2 implementation objects are exact on M0:

- `docs/VILLAGE_ARCHITECTURE_V1_3_PHASE_B.md` -> `6b97ba453c3df60e4916c1c8e027ba262fafe716`
- `scripts/test_village_v1_3_next_phase_b.py` -> `508b25287a8c21f4dc76b3f59663818ec3f82c55`
- `scripts/village_next_phase_b.py` -> `25aed74d7e85e8543fc93230968f7b70931b4aee`
- `scripts/village.py` -> `425f1c9ce6dbd684cd497818920de55e49440da6`

Additional current operator/security objects recorded:

- `scripts/village_next.py` -> `39efe7efddc46ff43315e04b06df0baf4601327b`
- `scripts/test_village_v1_3_next.py` -> `c95642a2fefbf3deb5f9c7f160f182d69a959b2e`
- `scripts/lock_auto_activate.py` -> `3d1b7187404df7a7174f1dd774a8d447eb68dcd5`
- `.github/workflows/lock-auto-activate.yml` -> `c20bedb63687bf581ae54f7488ae15c84f7766c9`
- `.github/workflows/verify.yml` -> `44d858e06d8334574acc8480731049ce5372d110`

Historical accepted inputs were also positively identified at their fixed commits/blobs:

- live plan commit `705bd7c5250103e74118381106d422d50c677bb7`, blob `05848a5d2998e42e5e02443f331194c61486f3b6`
- V3 supplement commit `95edc35b9e54e91bd3d11ab58160f159508df2c7`, blob `0b3059736d8b78ac9f511edffd05def19fa3a651`
- frozen V3 spec commit `a482d1f4398489753589afe1ef3ed5e593a7e9c4`, blob `2ddc79843cf44bd588dc1a5ff89e996ecd246de9`
- Stage-1 acceptance `406c0335d9a9fc0c278ee54a61e4018aa57d55ef`
- Stage-2 independent acceptance `b6c4c2d44268b204ba68479cd1a1fc643394e281`

## 2. Final Verify #119

Fresh workflow-run observation:

- workflow: `Verify public release`
- workflow id: `347191396`
- run id: `33771288534`
- run number: `119`
- run attempt: `1`
- head SHA: `7dc8541c0a9e19f37910e06bc4738375c4c7af00`
- status: `completed`
- conclusion: `success`

Result: **PASS**.

## 3. Ruleset / trusted lifecycle server gate

Detailed Ruleset evidence is positive:

- Ruleset id: `22089746`
- name: `Village main strict lifecycle safety`
- enforcement: `active`
- target condition includes `~DEFAULT_BRANCH`
- required status context includes exact `verify`
- `strict_required_status_checks_policy = true`
- `bypass_actors = []`
- `current_user_can_bypass = "never"`

The trusted lifecycle workflow remains the accepted narrow boundary:

- current workflow blob `.github/workflows/lock-auto-activate.yml` = `c20bedb63687bf581ae54f7488ae15c84f7766c9`
- the same blob is present at the accepted pre-Phase-B boundary checked in this review
- a fresh post-M0 trusted-lifecycle workflow run was observed completed/successfully, confirming the workflow remains enabled in practice

However, preregistration requires a **positive fresh read of effective rules for `main`**, and the accepted Phase-B implementation's `prove_ruleset` path explicitly obtains `/repos/51mns/AIMath-public/rules/branches/main` in addition to the Ruleset collection/details. The authenticated GitHub connector available to this lane rejected that effective-rules endpoint as unsupported; the branch-protection read also returned `403 Resource not accessible by integration`.

Because the effective branch-rules observation cannot be positively established, this gate is **FAIL / BLOCKED**. The detailed Ruleset record is not substituted for the missing effective observation.

## 4. Authenticated principal boundary

The connected authenticated GitHub account independently resolved to login `51mns` (GitHub user id `199666487`), yielding principal `gh:51mns` independently of caller-supplied principal text.

No token/secret was requested, read into the report, or exposed.

Result: **PASS**.

## 5. Complete bounded lifecycle queue

The complete open-PR observation for base `main` fit within one page; page 2 was empty. Eight open PRs were observed: `#15`, `#16`, `#24`, `#25`, `#26`, `#27`, `#39`, `#40`.

Per-file read-back established:

- `#39` and `#40` contain Phase-B implementation/docs changes, not lock transport;
- `#15`, `#16`, `#24`, `#25`, `#26`, `#27` contain worker-scoped `work/**` changes;
- none modifies `coordination/locks/**`;
- none is a frozen-worker source RELEASE transport;
- none is a frozen-worker expected-next ACQUIRE transport;
- no observed open PR can create an unrelated eligible RELEASE/ACQUIRE ordering ambiguity for this frozen epoch.

The complete branch observation also fit within one page; page 2 was empty. Historical lock/release branches for other workers exist, but there is no branch containing either frozen field-test worker id `w-0bebfd2fd11cb67f` or wrong-worker id `w-e8912c097a3288e1`, and no deterministic frozen source RELEASE ref exists.

Result: **PASS**.

## 6. Worker-history sentinel

Frozen worker identities were preserved exactly:

- worker: `w-0bebfd2fd11cb67f`
- wrong worker: `w-e8912c097a3288e1`

Current canonical `coordination/locks/**` tree is:

- `86a2a96c64d100ea9ca7628bf68429183a9e2acf`

It contains only `coordination/locks/README.md`; therefore there are no canonical active locks at all, including none for either frozen worker.

The complete M0 tree contains no:

- `work/TASK-EQUIANGULAR-R18-001/w-0bebfd2fd11cb67f/ABANDONED_TERMINAL.yml`
- equivalent wrong-worker field-test terminal/history
- frozen-worker field-test work tree

A historical abandonment terminal exists for a different worker (`w-fae1dfc5fac514d0`); it is not the preregistered field-test epoch and does not alter the frozen identities. The relevant current `work/**` identity is unchanged from the V3 compatibility snapshot.

Result: **PASS**.

## 7. Source Task substrate

Fresh source Task:

- Task: `TASK-EQUIANGULAR-R18-001`
- Task blob: `c20cb270cce728b60cd82fa1b10c8cc99eb21485`
- Campaign: `CAM-EQUIANGULAR-R18`
- Campaign blob: `7b5c8f35f86d52a9345f2dda840e8e184a806828`
- stored state: `APPROVED`
- kind: `RESEARCH`
- parallelism: `EXCLUSIVE`
- collision key: exactly `eq18/general-structural-obstruction`
- lease TTL: `168` hours
- frontier-sensitive: true

Campaign state is `ACTIVE`; the recorded public frontier observation remains within its 90-day TTL at this Phase-0 date. The required source assumption `C-EQUIANGULAR-R18-ETA17-SINGLETON-EXCLUSION` is `INDEPENDENTLY_REPRODUCED`, `CURRENT`, and `dependency_use = ALLOWED`.

Canonical source conditions at M0:

- no active source lock
- source collision key unowned
- zero canonical active locks, hence global/campaign capacity available
- no canonical outcome under `coordination/outcomes/**`
- no `PENDING_CLAIM` observed in the complete canonical tree
- source Task/Campaign/substrate blobs match the V3 compatibility snapshot

Frozen future execution identities were not substituted or created:

- source lock path: `coordination/locks/eq18/general-structural-obstruction.yml`
- source work ref: `research/TASK-EQUIANGULAR-R18-001/w-0bebfd2fd11cb67f`
- source lock id: `LOCK-FIELDTEST-EQUIANGULAR-R18-001-0BEBFD2FD11CB67F`
- terminal class/reason to be used later: `ABANDONED_TERMINAL` / `SCOPE_STOP`
- Truth effect: `NONE`

Result: **PASS**.

## 8. Expected-next Task substrate

Fresh expected-next Task:

- Task: `TASK-DITTERT-N5-001`
- Task blob: `fea6e3ea616aea46e819eba8e2983eaa2b332bef`
- Campaign: `CAM-DITTERT-N5`
- Campaign blob: `4b635bc817c3a6f5065422f7e943860ac10b5aab`
- stored state: `APPROVED`
- kind: `RESEARCH`
- parallelism: `EXCLUSIVE`
- collision key: exactly `dittert-n5/broader-zero-pattern`
- lease TTL: `168` hours

Campaign state is `ACTIVE`. Required assumption `C-DITTERT-N5-Z2-MATCHING-EXCLUSION` is `INDEPENDENTLY_REPRODUCED`, `CURRENT`, and `dependency_use = ALLOWED`.

Current portfolio gate:

- portfolio blob: `c395a9eb7c9147d0bea0339b1f6f213f75ea895a`
- `global_admission = OPEN`
- global active-lane cap: `12`
- zero canonical active locks at M0

Current expected-next conditions:

- no active expected-next lock
- collision key unowned
- campaign/global capacity available
- assumptions usable
- evaluations tree contains only its README; no fresh evaluation changes the preregistered hypothesis
- Task/Campaign/evaluation/portfolio substrate identities match the V3 compatibility snapshot

Therefore the preregistered hypothesis `TASK-DITTERT-N5-001 / CAM-DITTERT-N5 / GLOBAL_READY` remains compatible with the current pre-RELEASE substrate.

This report **does not** claim that `TASK-DITTERT-N5-001` will necessarily be selected after a real RELEASE; Phase B must recompute selection from fresh post-RELEASE state.

Result: **PASS**; preregistration compatible: **YES**.

## 9. Frozen no-side-effect baseline sentinels

All identities below are from canonical M0 and are sufficient for later post-field-test comparison.

Top-level / coordination tree sentinels:

- M0 root tree: `8ea11092584142fb1b0dcc724a50e0e635e26eea`
- `research/**`: `726e437601ccd8340b81306af42b22c6e2696d96`
- `reviews/**`: `4a5af3f6a83454f53b44b80cdec9de5cc3266d5d`
- `coordination/**`: `1cd29a9946aa82077e19beb1ef40532f7cbd7b47`
- `coordination/campaigns/**`: `57fcda768f3063680846b9077e3672b64215fc28`
- `coordination/evaluations/**`: `5a9d4b135e725df61278935acae656c32ba69564`
- `coordination/failed-routes/**`: `51b333be021706ffa71b238859b1d27f1e566065`
- `coordination/outcomes/**`: `8fb2f95611bda59996be25c3df330192590a9f09`
- `coordination/portfolio/**`: `aef2eb9421c52399a95c0f8cd235dd399c1240fe`
- `coordination/tasks/**`: `7b86a2aa4145b9f670f21b9b09701bf49af9080a`
- `coordination/locks/**`: `86a2a96c64d100ea9ca7628bf68429183a9e2acf`
- `work/**`: `2defda901c875e0cb5c856ce9bcb63fb2d6e119b`

Canonical `research/**/CLAIM.yml` manifest:

- `research/433-existing-theory-identification/CLAIM.yml` -> `cfb0e7bf7a29e98ab7f7760ebe55e680c6a860b8`
- `research/433-springborn-obstruction/CLAIM.yml` -> `3a55b6ffa1bea36864ca70c7e9788d6352ab7b6a`
- `research/afes-bounded/CLAIM.yml` -> `4238c50bc27852e06a7197d1da32f56ca95d4418`
- `research/b3rcc-apc/CLAIM.yml` -> `9f91d32aa19dad1ea71454582ea92285cc6cc3d4`
- `research/dittert-n5-z2/CLAIM.yml` -> `8185e9d31970a64181b4f5c9ff362bf21fa041cb`
- `research/equiangular-r18-eta17/CLAIM.yml` -> `0e6f5da3fcf4b13054b32ea32d26fa59d3e673cb`
- `research/fixed-433/CLAIM.yml` -> `6116a577517bcd644fe48471fab0ad5ee1338b95`
- `research/gyoda-89/CLAIM.yml` -> `d587451839a14989415c1f73aedb99b01ce229d1`
- `research/local-tp2/CLAIM.yml` -> `4311816053974af0c8ab1151e976a195596bcf4c`
- `research/lonely-runner-r2/CLAIM.yml` -> `12400f60486f961e26b72f595e43e9c5e07fecc1`
- `research/thue-morse-rediscovery/CLAIM.yml` -> `ed91494280c924fe502b27a249b079c86029f99e`

Canonical `reviews/**/REVIEW.yml` manifest:

- `reviews/equiangular-r18-eta17/REVIEW.yml` -> `056946d89f680542c8f81ad239cb5c0de4746096`

Result: **PASS**.

## 10. Observability

The accepted M0 Phase-B core exposes deterministic evidence for the preregistered live test:

- `derive_source_acquisition_v1` / `source_epoch_id`
- `derive_continuation_context_v1` / `continuation_context_id`
- `derive_selection_v1` / `selection_id`
- `derive_acquire_intent_v1` / `acquire_intent_id`
- exact `next_binding` parsing and cross-link validation
- `CanonicalAcquireIdentityV3` / `canonical_acquire_id`
- exact base `B` and expected canonical tree `T`
- exact lock objects with path, mode, Git blob OID, and bytes SHA-256
- deterministic RELEASE and ACQUIRE transport refs / transport head `H`
- canonical first-parent transition proof for canonical `M` and fresh current `C`
- authoritative Verify lineage by highest matching run number plus current attempt
- fresh Ruleset proof object and fail-closed Ruleset observation
- retained-state chain recomputation rather than trusting retry-state text

The implementation is therefore observability-capable. The current verdict is not `FIELD_TEST_OBSERVABILITY_INSUFFICIENT`; it is `BLOCKED` because this Phase-0 execution environment cannot positively obtain the separately required effective branch-rules observation.

Result: **PASS**.

## 11. Phase-0 result matrix

- CURRENT_MAIN: `7dc8541c0a9e19f37910e06bc4738375c4c7af00`
- FINAL_VERIFY_119: `PASS`
- FINAL_BLOBS: `PASS`
- RULESET_GATE: `FAIL`
- LIFECYCLE_QUEUE: `PASS`
- PRINCIPAL_BOUNDARY: `PASS`
- WORKER_HISTORY: `PASS`
- SOURCE_TASK: `PASS`
- EXPECTED_NEXT_TASK: `PASS`
- EXPECTED_NEXT_PREREGISTRATION_COMPATIBLE: `YES`
- BASELINE_SENTINELS: `PASS`
- OBSERVABILITY: `PASS`
- PRODUCTION_MUTATION_PERFORMED: `NO`
- VERDICT: `BLOCKED`

## 12. Stop condition and coordinator action

Do **not** open or run the production live-execution lane from this report.

A retry may proceed only when the Phase-0 executor can positively fresh-read the effective `main` rules observation required by the accepted Phase-B `prove_ruleset` contract, in addition to the already-positive detailed Ruleset evidence. On retry, all other mutable preconditions must also be freshly re-read; this report must not be treated as a future current-state substitute.
