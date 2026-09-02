# Village v1.3 Phase B V2 final independent security review

TASK-ID: `AIMATH-VILLAGE-V1-3-NEXT-PHASE-B-V2-FINAL-SPEC-REREVIEW`

Repository: `51mns/AIMath-public`

Target: `e322b021de758eccba2045471bd97eb7accd42dc`

Target specification: `reviews/village-v1-3-next-phase-b-transport-preflight/PHASE_B_FROZEN_SPEC.md`

## Binary implementation gate

**VERDICT: FAIL**

```text
PHASE_B_IMPLEMENTATION_ALLOWED = NO
```

The V2 remediation **does close the two historical focused-review findings**:

- `H-01` exact-PR-number causality is removed from `ACTIVE_NEXT` authority and is therefore **CLOSED**;
- `M-02` max-numeric-`run_id` chronology is replaced with GitHub's documented workflow `run_number` lineage plus current `run_attempt` state and is therefore **CLOSED**.

However, V2 introduces/leaves a separate authority inconsistency that is blocking at **HIGH** severity:

> V2 declares `expected_head_sha = H` to be part of the authority-bearing immutable acquisition identity and explicitly declares `H2 != H` non-equivalent even when the two heads have identical lock bytes. But the accepted squash-compatible canonical-main proof permits `M != H` and proves only `parents(M) == [B]`, `tree(M) == tree(H)`, the exact lock-only delta, and exact lock objects. Distinct Git commit objects `H` and `H2` can have the same single parent `B` and the same tree while differing only in commit metadata. After a squash-like canonical transition, the canonical Git state required by V2 therefore cannot distinguish whether `H` or such an `H2` was the source acquisition.

This is not PR-number causality. It is an **exact expected-head identity observability failure**. It directly conflicts with V2 Section 20.4's rule that a different head SHA is non-equivalent and with the inherited mandatory different-head substitution regression (row 51).

Because the user-defined severity contract classifies a real canonical acquisition substitution as HIGH or worse, Phase B production implementation remains blocked.

---

## 1. Fresh integrity gate

Fresh GitHub reads established:

```text
current main
84a046359b299950403b68bfcb190930ebbc4c3f

design branch
refs/heads/design/village-v1-3-next-phase-b-transport-preflight
= e322b021de758eccba2045471bd97eb7accd42dc

target
= e322b021de758eccba2045471bd97eb7accd42dc

target parent
= d46395c1ff2d379cd7fab841f090abbdf8bbf8b5

target spec blob
= fcf857204e4d683f7ca17a2f6265d67cdd0fcaa9
```

GitHub compare `d46395c1ff2d379cd7fab841f090abbdf8bbf8b5...e322b021de758eccba2045471bd97eb7accd42dc` reports:

```text
ahead_by  = 1
behind_by = 0
total_commits = 1
changed files = 1
+521 / -0
```

The only changed path is:

```text
reviews/village-v1-3-next-phase-b-transport-preflight/PHASE_B_FROZEN_SPEC.md
```

The target commit message contains the required DCO trailer:

```text
Signed-off-by: Shoma Nakabayashi <199666487+51mns@users.noreply.github.com>
```

`TARGET_MATCH = YES`. `SCOPE_MATCH = YES`. No target drift was observed.

The historical focused review at `7385e592d93987490d1fc91c10ec4c5b65ff4e81` was fresh-read. Its prior `FAIL`, `H-01 HIGH`, and `M-02 MEDIUM` are treated as real findings, not erased by the writer's V2 assertions.

---

## 2. GitHub primary semantics used

Primary documentation checked independently:

- Pull request merge and indirect-merge semantics:  
  <https://docs.github.com/en/pull-requests/reference/pull-request-merges>
- GitHub Actions run variables:  
  <https://docs.github.com/en/actions/reference/workflows-and-actions/variables>
- Workflow-runs REST API, filtering and pagination:  
  <https://docs.github.com/en/rest/actions/workflow-runs>
- Git commit object inputs (`message`, `tree`, `parents`, author/committer metadata):  
  <https://docs.github.com/en/rest/git/commits>

The load-bearing documented semantics are:

1. GitHub may mark a PR indirectly merged when its head commits become reachable from the base branch outside that PR.
2. Squash merge combines PR commits into a single commit on the base branch; the original head commit identity is not preserved as the canonical commit identity merely by squash merging.
3. `GITHUB_RUN_ID` is unique and unchanged on rerun, but GitHub does not document numeric `run_id` ordering as chronology.
4. `GITHUB_RUN_NUMBER` begins at 1 for a workflow and increments with each new run; it does not change on rerun.
5. `GITHUB_RUN_ATTEMPT` increments on rerun.
6. workflow-run listing is paginated with maximum `per_page=100`, and filtered searches using `head_sha`/event/etc. may be capped at 1,000 results.
7. A Git commit object is independently determined by commit-object data including message, tree and parents (plus author/committer/signature fields); therefore two commits may point to the same tree and parent while having different commit SHAs.

---

## 3. Historical H-01 — CLOSED

### PR-number authority removal

**PASS.** Section 20.1 is sufficiently explicit to supersede the historical PR-causality clauses. It declares non-authoritative for V2:

- exact PR-number creator causality;
- PR number/ref as `ACTIVE_NEXT` authority;
- `merged`, `merged_at`, and `merge_commit_sha` as `ACTIVE_NEXT` authority;
- old merge-strategy-neutral provenance wording;
- max numeric `run_id` ordering.

`TransportLocatorV1` remains discovery/idempotency/audit metadata only. PR locator fields are not inputs to `CanonicalAcquireIdentityV2` or `canonical_acquire_id`.

The old Section 19 wording remains visible for audit history, but the V2 supersession rule is explicit enough that an implementation following Section 20 cannot reasonably treat those old PR-causality predicates as authority.

### Indirect merge attack

**PASS.** For expected PR A/ref A/head `H` and other PR B/ref B/same `H`, if B is merged with a normal merge commit, GitHub may mark A indirectly merged. Under V2 that PR metadata is irrelevant. The canonical first-parent child after `B` is a multi-parent merge commit, so `parents(M) == [B]` fails and the correct result is `NONCANONICAL_ACQUIRE_MERGE_SHAPE`, never `ACTIVE_NEXT`.

Therefore:

```text
H01_INDIRECT_MERGE = CLOSED
PR_NUMBER_AUTHORITY = REMOVED
INDIRECT_MERGE_CONTROL = PASS
```

---

## 4. Historical M-02 — CLOSED

**PASS.** V2 no longer orders workflow runs by numeric `run_id`.

It fixes the workflow identity to repository, workflow ID, workflow path/name, `event=pull_request`, and exact `head_sha=H`, then selects:

```text
authoritative_run_number = max(run_number among the complete matching run set)
```

This matches GitHub's documented semantics: `run_number` increments for each new run of a particular workflow; rerunning does not change it; `run_attempt` increments for reruns. `run_id` is used only as a lookup identity.

The rerun policy is sound:

- 10 success -> 11 failure -> rerun 10 success: 11 remains authoritative;
- a new 12 success becomes authoritative;
- if the authoritative highest lineage is currently rerunning and its current run object is queued/in-progress, stale successful attempts cannot grant eligibility;
- rerunning the authoritative lineage itself keeps the same `run_number`; its current attempt/status controls.

The duplicate/inconsistent `run_number` fail-closed rule is appropriate because V2 does not assume more uniqueness than GitHub documents and separately filters exact workflow identity/head.

Therefore:

```text
M02_RUN_ORDERING = CLOSED
RUN_NUMBER_SEMANTICS = PASS
RERUN_POLICY = PASS
```

---

## 5. CanonicalAcquireIdentityV2 field/serialization review

### Field coverage

The V2 identity binds the security-relevant semantic and Git state expected by the task:

- source epoch, continuation context, selection, acquire intent;
- exact base SHA, exact expected head SHA, expected head tree SHA;
- Task, worker, principal, work ref;
- sorted collision bundle;
- lock ID and acquisition/expiry timestamps;
- exact canonical lock paths, regular `100644` mode, Git blob OIDs and exact-byte SHA-256.

Same human-readable lock bytes alone are therefore insufficient. Epoch/selection/intent/base/tree/identity remain bound.

### Canonical serialization

The inherited canonical encoding is deterministic: UTF-8 JSON, sorted keys, fixed separators, `ensure_ascii=false`, lowercase SHA-256. Set-like lists are required to be lexicographically sorted and exact lock objects are sorted by path.

Missing paths fail because `exact_lock_objects` must equal the complete canonical collision-key lock path set and the path-derived/Task/payload collision bundles must agree exactly.

### LOW hardening: duplicate path entries should be explicitly rejected

Section 20.2 says the object list must describe **exactly** the complete path set, which strongly implies uniqueness. However, it does not separately spell out `duplicate path => fail` before hashing. A duplicate list entry would not be a SHA-256 collision, but it could create more than one serialization for the same semantic set if an implementer interpreted only set equality.

This is not the blocking defect. A safe implementation can and should treat the exact-set wording as requiring one entry per path. Still, an explicit uniqueness clause/test should be added in the next spec revision.

---

## 6. Expected head derivation

**PASS before canonicalisation.** V2 requires:

```text
parents(H) == [B]
tree(H) == expected_head_tree_sha
compare B -> H changes exactly expected lock paths
```

and exact mode/OID/byte hashes for each lock object. No unrelated path may change.

The first valid creator freezes the exact `H` and timestamp; duplicate creators/retries for the same `acquire_intent_id` must adopt that exact winner instead of manufacturing another head. This correctly prevents two same-intent creators from silently diverging inside the normal deterministic transport path.

A duplicate creator that manufactures `H2 != H` is therefore not the same frozen expected transport and must be rejected/reused according to the contract.

The problem arises **after canonicalisation**, not in derivation of `H` itself.

---

## 7. HIGH H-02 — exact expected-head identity is not positively observable after squash

**Severity: HIGH, blocking**  
**Area: canonical acquisition substitution / expected-head authority / squash canonicalisation**

V2 makes two simultaneous claims:

1. Section 20.4: if another PR/ref points to `H2 != expected_head_sha`, it is **NON-EQUIVALENT** even if its lock bytes are byte-identical; different immutable commit identity means a different acquisition candidate.
2. Sections 20.7–20.8: after canonicalisation, `M` need not equal `H`; it is enough that the unique first-parent child `M` satisfies:

```text
parents(M) == [B]
tree(M) == tree(H)
compare B -> M == exact expected lock-only delta
exact lock objects match
```

Those two requirements do not compose securely under squash.

### Constructive Git witness

Let `T` be the intended exact lock-only tree and `B` the frozen selection base.

Git permits two distinct commit objects:

```text
H  = commit(message=A, tree=T, parents=[B], ...metadata A...)
H2 = commit(message=B, tree=T, parents=[B], ...metadata B...)
```

with:

```text
H != H2
parents(H)  = parents(H2) = [B]
tree(H)     = tree(H2)    = T
B -> H      = B -> H2     = same exact lock-only final delta
```

Changing commit-object metadata changes the commit SHA without changing the tree or parent relation. This follows directly from Git commit-object semantics and was also reproduced independently with a local synthetic Git construction during this review.

Now let the canonical branch receive a squash-like single transition:

```text
M = squash-result(parent=B, final tree=T)
```

The canonical evidence required by Section 20.7 is identical whether the transport merged was `H` or `H2`:

```text
parents(M) == [B]
tree(M) == T
B -> M == exact lock-only delta
current lock objects == expected objects
```

The canonical state therefore cannot prove which distinct source head supplied that tree.

### Why Verify does not repair this

V2 can prove that `H` had the authoritative successful Verify lineage. That proves CI state for `H`; it does **not** prove that the canonical squash transition `M` was created from `H` rather than a separately verified or separately merged `H2` with the same tree.

### Why PR metadata cannot repair this

Using the expected PR's `merged`/`merge_commit_sha` to bind `H -> M` would reintroduce the exact PR/transport causality assumption that H-01 correctly removed, and GitHub's documented indirect-merge semantics are precisely why that proof was rejected.

### Security consequence

An alternate acquisition candidate `H2` which V2 itself defines as non-equivalent can become canonical, yet the post-canonical V2 predicate evaluated for expected `H` can still pass. This is a canonical acquisition identity substitution under the frozen definition.

Therefore:

```text
CANONICAL_ACQUIRE_IDENTITY_V2 = FAIL
CANONICAL_MAIN_TRANSITION = FAIL
```

The failure is not that the canonical tree transition is unobservable. The failure is that the observed tree transition is **not strong enough to prove the exact head identity that V2 itself declares authoritative**.

### Required design choice before implementation

A revised spec must choose one coherent model:

**Option A — tree/semantic acquisition identity.** Keep `expected_head_sha` as a pre-canonical transport/Verify locator, but remove exact head commit SHA from post-canonical authority/equivalence. Define canonical acquisition identity by the semantic IDs + frozen base + expected tree + exact object bundle. Then `H` and `H2` with exactly the same base/tree/objects intentionally represent the same canonical acquisition, and the current squash proof is observable.

**Option B — exact head commit identity.** Keep `H2 != H` non-equivalent, but require a canonical mechanism that positively preserves/binds source head identity, e.g. `M == H` or another independently documented unambiguous server primitive. The current squash lifecycle does not preserve `H` as the canonical commit, so this option would require a separately reviewed lifecycle/design change.

The reviewer does not select or implement either option here.

---

## 8. Squash compatibility

**PASS for the frozen Git shape, but not for exact-head provenance.**

GitHub documents squash merging as combining PR commits into one commit on the base branch. With an unchanged base `B` and a lock-only head whose final tree is `T_H`, the resulting canonical commit can have one parent `B` and final tree `T_H`. The fact that the squash commit SHA differs from `H` is not itself a problem for tree equality.

Therefore the strict shape:

```text
parents(M) == [B]
tree(M) == tree(H)
```

is compatible with the current trusted lifecycle's `merge_method="squash"`.

This is exactly why H-02 matters: squash compatibility preserves the final tree while losing positive evidence of the source head commit identity.

So:

```text
SQUASH_COMPATIBILITY = PASS   # shape feasibility only
```

but `CANONICAL_MAIN_TRANSITION = FAIL` under V2's stronger exact-head identity claim.

---

## 9. Same head / different locator

**PASS.** If two locators point to the exact same `H`, there is no distinct Git head to substitute. If the same base, semantic identity, tree, exact objects, Verify lineage, Ruleset proof and fresh active-lock read-back all match, confirming the same immutable head acquisition without claiming which PR was the creator is safe.

An attacker cannot retain exact `H` while changing source epoch, intent, Task/worker/principal, lock bytes, tree, parent, or commit metadata: changing the commit content/tree/parent changes `H`, and changing authority-bearing non-Git identity changes `canonical_acquire_id` and must fail the identity comparison.

Thus:

```text
SAME_HEAD_DIFFERENT_LOCATOR = PASS
```

---

## 10. Canonical history shape challenges

The first-parent proof is otherwise conservative and fail-closed:

- multi-parent merge commit immediately after `B`: rejected;
- unrelated `B -> X` before expected lock: rejected because the immediate child is not the expected lock tree/delta;
- multi-step rebase canonicalisation: rejected;
- incomplete first-parent history: rejected;
- malformed/ambiguous parent data: rejected;
- same final lock tree plus an unrelated file delta from `B`: rejected by exact full-tree/delta requirements;
- exact acquisition `B -> M` followed by later unrelated commits: permitted only while `M` remains on current main's first-parent ancestry and the fresh current lock remains exact, active and unexpired.

This is sound for proving **a unique exact tree transition**. It is not enough to prove which non-canonical source commit produced that tree when `M != H` is allowed.

---

## 11. Renewal / replacement / release-reacquire

**PASS.** The current-lock read-back is appropriately strict. A later renewal/replacement/reacquisition changes the active identity (timestamps, lock ID/acquire intent/base and/or object OIDs/bytes) and therefore does not satisfy the old expected acquisition. Same human-readable Task/worker/principal is insufficient.

Automatic `RENEW` and `TAKEOVER` remain forbidden; V2 does not introduce them.

```text
CURRENT_LOCK_READBACK = PASS
```

---

## 12. Workflow pagination / result cap

**PASS at the contract level.** V2 explicitly rejects the inherited first-page-only helper. It requires complete fresh observation for the exact workflow identity/head and fails closed when pagination, truncation or the documented filtered-result cap prevents proof of completeness.

This is implementable with the workflow-specific runs endpoint plus exact workflow/head/event filtering and pagination. If the 1,000-result filtered-search ceiling makes completeness unprovable for an extreme lineage, the correct secure result is the already-specified fail-closed state, not a guessed maximum.

No impossible enumeration is required for success in normal cases; no security weakening is permitted when the envelope is ambiguous.

```text
WORKFLOW_PAGINATION = PASS
```

---

## 13. Current Ruleset state

Fresh repository Ruleset reads show one repository Ruleset:

```text
id                         22089746
name                       Village main strict lifecycle safety
target                     branch
enforcement                active
include                    ~DEFAULT_BRANCH
required status context    verify
strict policy              true
bypass_actors              []
current_user_can_bypass    never
```

This satisfies the frozen positive Ruleset gate. No settings were modified.

```text
RULESET_GATE = PASS
```

---

## 14. Current trusted lifecycle compatibility

Fresh current-main code confirms the inherited lifecycle still provides:

- eligible `RELEASE` scanned/selected before `ACQUIRE`;
- ascending PR number as same-class deterministic ordering after full eligibility;
- candidate-local malformed observations fail that candidate rather than becoming reservation authority;
- current main/head/base fresh-read immediately before merge;
- exact candidate head SHA passed to GitHub's merge endpoint;
- `merge_method = "squash"`;
- return after at most one canonical mutation per trusted run.

The current inherited `_has_successful_verify` helper still uses first-page observation and max numeric run ID; **V2 correctly forbids reusing that helper for the new authority proof**. Phase B implementation would need the reviewed V2 observer, but no production modification was made in this reviewer lane.

---

## 15. Phase A boundary

**PASS.** Current accepted Phase A remains read-only and ends at `ACQUIRE_PENDING`:

- no canonical mutation authority;
- no `ACTIVE_NEXT` emission/certification;
- no GitHub mutation;
- no Truth or review authority;
- no I2/I3;
- no `RENEW`;
- no `TAKEOVER`;
- PENDING is not ownership.

V2 does not require expanding Phase A authority.

```text
PHASE_A_BOUNDARY = PASS
```

---

## 16. Trust/security boundary

**PASS.** The V2 design does not require:

- a new PAT or secret;
- broader token authority;
- Ruleset weakening or bypass;
- `pull_request_target`;
- PR-head code with trusted write authority;
- worker ID as credential authority;
- Truth promotion or automatic review;
- Task/Campaign creation;
- Phase A mutation expansion.

H-02 must be solved by revising the identity contract or canonicalisation semantics, not by adding secrets/bypass authority.

---

## 17. Mandatory 62-test matrix

**FAIL overall.** Rows 55–62 are meaningful and distinct for the intended V2 model:

- 55 validates highest documented `run_number` lineage;
- 56 validates same-H indirect merge-commit rejection;
- 57 validates same-H/different-locator exact single transition;
- 58 validates older rerun cannot outrank newer failure;
- 59 validates a new higher successful lineage;
- 60 validates current authoritative rerun/in-progress fail-closed;
- 61 validates incomplete/ambiguous/non-single canonical transition fail-closed;
- 62 validates Ruleset unreadable/bypass/non-strict fail-closed.

The failure is not padding/counting. It is a substantive incompatibility with inherited row 51:

> row 51 requires a byte-identical **different head SHA** to be non-equivalent.

An explicit fixture must instantiate:

```text
B fixed
H  != H2
parents(H) = parents(H2) = [B]
tree(H) = tree(H2)
exact lock bytes/paths identical
H is the expected frozen head
H2 is canonicalised through a squash-like single-parent result M
parents(M) = [B]
tree(M) = tree(H)
```

Under the current Section 20.7 proof, the expected-H check cannot distinguish this from canonicalisation of H and would incorrectly be able to confirm the expected acquisition. Thus row 51 cannot be satisfied consistently with the current V2 authority model.

The next spec revision should make this attack an explicit regression and resolve the identity model first.

```text
PREREGISTERED_62_TESTS = FAIL
```

---

## 18. Mandatory threat challenges

1. **same PR locator, different head SHA — HOLE.** If `H2 != H` but has the same parent/tree/exact lock bytes and is the source of a squash-like canonical `M`, post-canonical proof cannot distinguish it from H. H-02.
2. **different PR locator, different head SHA but same bytes — HOLE.** Same H-02; different locator is irrelevant, and exact source head SHA is lost under the accepted squash proof.
3. **different locator, same H — PASS.** Same immutable head; locator has no authority.
4. **indirect merge marks expected PR merged — PASS.** Merged metadata ignored; normal merge's multi-parent shape fails.
5. **multi-parent merge commit — PASS.** `parents(M) == [B]` fails.
6. **multi-step rebase canonicalisation — PASS.** Unique immediate single transition fails.
7. **exact squash-like single-parent canonical transition — PASS for shape.** One parent B and final tree equality are compatible with GitHub squash; exact-source-head provenance remains H-02.
8. **B -> unrelated X -> expected lock M — PASS.** Immediate child after B is not the expected exact transition.
9. **expected lock M -> later unrelated commits — PASS.** Allowed only if M remains first-parent ancestor and current exact active lock persists unchanged.
10. **same tree but unrelated path delta — PASS.** Exact B->M full-tree/delta equality excludes unrelated final path changes.
11. **same H but wrong source_epoch_id — PASS.** Authority identity mismatch; acquire-intent/lock binding cannot be waived by H equality.
12. **same H but wrong acquire_intent_id — PASS.** Identity mismatch; deterministic lock identity remains bound.
13. **same Task/worker/principal but old epoch — PASS.** Epoch/selection/intent and current exact lock identity remain required.
14. **later renewal — PASS.** Current identity/timestamps/object read-back no longer equal original.
15. **later release/reacquire — PASS.** New acquisition identity does not satisfy old canonical acquisition.
16. **incomplete first-parent history — PASS.** Fail closed.
17. **ambiguous/malformed commit parent data — PASS.** Fail closed.
18. **old successful run + higher run failure — PASS.** Higher `run_number` authoritative; not eligible.
19. **old successful run rerun after higher failure — PASS.** Older `run_number` stays older; higher failure remains authoritative.
20. **higher new successful run — PASS.** New highest `run_number` may restore Verify eligibility.
21. **highest lineage rerun currently in progress — PASS.** Fresh current object not completed-success; not eligible.
22. **workflow run pagination incomplete — PASS.** Global fail closed.
23. **ambiguous workflow identity — PASS.** Exact repository/workflow ID/path/name/event/head filtering required; ambiguity fails closed.
24. **Ruleset unreadable — PASS.** No positive Ruleset proof, no `ACTIVE_NEXT`.
25. **Ruleset bypass appears — PASS.** Any bypass actor/non-never current-user bypass fails closed.
26. **main moves immediately before trusted merge — PASS.** Inherited final main/head/base revalidation rejects stale mutation.
27. **main moves immediately after canonical acquisition — PASS.** Later unrelated commits are acceptable only if exact M remains first-parent ancestry and current expected lock is still exact, active and unexpired.

Threats 1 and 2 are the blocking new hole.

---

## 19. Findings

### CRITICAL

None found.

### HIGH

#### H-02 — exact expected-head SHA cannot be positively bound by the squash-compatible canonical proof

**Blocking.** V2 says `H2 != H` is a different acquisition, but its post-canonical proof observes only a single-parent canonical commit with the same final tree/object bundle and does not preserve/prove the source head. A non-equivalent H2 with the same base/tree can therefore satisfy the expected-H canonical proof after squash. This is a canonical acquisition substitution under V2's own definition.

### MEDIUM

None found beyond the historical M-02, which V2 closes.

### LOW

#### L-01 — duplicate exact-lock-object paths should be explicitly rejected before canonical hashing

The existing exact-complete-set wording strongly implies uniqueness and missing paths already fail, but an explicit duplicate-path rejection/test would remove avoidable canonical-serialization ambiguity.

---

## 20. Final review matrix

```text
CURRENT_MAIN:
84a046359b299950403b68bfcb190930ebbc4c3f

TARGET:
e322b021de758eccba2045471bd97eb7accd42dc

TARGET_MATCH:
YES

TARGET_PARENT:
d46395c1ff2d379cd7fab841f090abbdf8bbf8b5

TARGET_BLOB:
fcf857204e4d683f7ca17a2f6265d67cdd0fcaa9

SCOPE_MATCH:
YES

H01_INDIRECT_MERGE:
CLOSED

M02_RUN_ORDERING:
CLOSED

PR_NUMBER_AUTHORITY:
REMOVED

CANONICAL_ACQUIRE_IDENTITY_V2:
FAIL

EXPECTED_HEAD_DERIVATION:
PASS

CANONICAL_MAIN_TRANSITION:
FAIL

SQUASH_COMPATIBILITY:
PASS

INDIRECT_MERGE_CONTROL:
PASS

SAME_HEAD_DIFFERENT_LOCATOR:
PASS

CURRENT_LOCK_READBACK:
PASS

RUN_NUMBER_SEMANTICS:
PASS

RERUN_POLICY:
PASS

WORKFLOW_PAGINATION:
PASS

RULESET_GATE:
PASS

PHASE_A_BOUNDARY:
PASS

PREREGISTERED_62_TESTS:
FAIL

CRITICAL:
none

HIGH:
H-02 exact expected-head identity unprovable under squash-compatible tree proof

MEDIUM:
none open

LOW:
L-01 explicit duplicate exact-lock-object path rejection/test recommended

VERDICT:
FAIL

PHASE_B_IMPLEMENTATION_ALLOWED:
NO
```

## 21. Next

Return this fixed reviewer artifact to the Village coordinator.

Do **not** implement Phase B from this reviewer branch. The next action is a design-spec revision resolving H-02, followed by another independent fixed-commit review.