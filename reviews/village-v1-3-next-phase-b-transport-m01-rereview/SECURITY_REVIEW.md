# Village v1.3 Phase B M-01 focused independent security re-review

TASK-ID: `AIMATH-VILLAGE-V1-3-NEXT-PHASE-B-M01-FOCUSED-REREVIEW`

## Binary gate

**VERDICT: FAIL**

**M-01: OPEN**

**PHASE_B_IMPLEMENTATION_ALLOWED: NO**

The remediation closes the historical *different-head, byte-identical payload copy* shortcut by binding the exact expected repository, PR number, head ref/SHA, base, Verify run, merge result and canonical lock read-back. However, it still does not positively prove that the exact expected PR number was the transport that created the canonical acquisition under GitHub's documented **indirect merge** semantics: a different PR/ref can carry the same head commits, be merged first with an allowed merge-commit strategy, and cause the expected PR to be marked merged indirectly. A second blocking ambiguity remains in the definition of "latest Verify": GitHub documents `run_id` as unique, not as a monotonic chronology contract, while the frozen spec makes the greatest numeric `run_id` authoritative.

No CRITICAL finding was found. One HIGH and one MEDIUM blocker remain. Under the requested severity rules the HIGH finding makes the implementation gate FAIL.

## Fixed target and remote integrity

Repository: `51mns/AIMath-public`

Fresh target observations used for the verdict:

- current canonical `main`: `84a046359b299950403b68bfcb190930ebbc4c3f`
- target branch: `design/village-v1-3-next-phase-b-transport-preflight`
- target branch head: `d46395c1ff2d379cd7fab841f090abbdf8bbf8b5`
- target parent: `c3532324e9df421afc787aa6cee3d91f8dbaa91e`
- target artifact: `reviews/village-v1-3-next-phase-b-transport-preflight/PHASE_B_FROZEN_SPEC.md`
- target blob: `6c47e1721383d3a7c8e2e6ba01f3ec846bb23a52`
- historical independent review: `3f5206c5b793cf8b5ecaac5bafcb0313b5e7de0f`
- historical review blob: `404bfd67d44233281e51a8eb7437d28b40c7f2de`

GitHub compare `c3532324e9df421afc787aa6cee3d91f8dbaa91e...d46395c1ff2d379cd7fab841f090abbdf8bbf8b5` reports:

- `ahead_by = 1`
- `behind_by = 0`
- exactly one changed file
- only `reviews/village-v1-3-next-phase-b-transport-preflight/PHASE_B_FROZEN_SPEC.md`
- `+308 / -0`

The remediation commit contains the required DCO `Signed-off-by` trailer.

`TARGET_MATCH = YES` and `SCOPE_MATCH = YES`.

## Evidence read independently

The review fresh-read the historical frozen spec and historical independent review rather than treating the writer's `M-01 CLOSED` statement as evidence. It also checked current accepted Phase A and the inherited trusted lifecycle on canonical main, including:

- `scripts/village_next.py`
- `scripts/test_village_v1_3_next.py`
- `docs/VILLAGE_ARCHITECTURE_V1_3.md`
- `scripts/village.py`
- `scripts/lock_auto_activate.py`
- `scripts/lock_auto_activate_phase_a.py`
- `scripts/test_village_v1_2_1.py`
- `scripts/test_village_v1_2_1_phase_b.py`
- `.github/workflows/lock-auto-activate.yml`
- `.github/workflows/verify.yml`

Current main preserves the Phase A boundary: Phase A is pure/read-only, stops at `ACQUIRE_PENDING`, does not emit/certify `ACTIVE_NEXT`, and has no canonical mutation, Truth, review, merge, RENEW or TAKEOVER authority.

The inherited trusted lifecycle independently confirms: eligible RELEASE precedes eligible ACQUIRE; same-class fully eligible candidates are ordered by lowest PR number; malformed candidate-local observations do not block later valid candidates; and a trusted invocation returns after at most one canonical mutation.

The effective repository Ruleset observed from GitHub is `Village main strict lifecycle safety`: active on the default branch, required status context `verify`, strict up-to-date policy on, no bypass actor, `current_user_can_bypass=never`.

The repository currently allows merge commit, squash merge and rebase merge. Current trusted lifecycle code chooses squash when it itself invokes the merge endpoint, but the target specification claims the provenance predicate is merge-strategy neutral and does not freeze `ACTIVE_NEXT` provenance to only that direct squash invocation path.

## GitHub primary semantics used

Primary references:

- GitHub pull-request merge semantics and **Indirect merges**: <https://docs.github.com/en/pull-requests/reference/pull-request-merges>
- GitHub REST pull-request API / `merge_commit_sha` and merge endpoint: <https://docs.github.com/en/rest/pulls/pulls>
- GitHub Actions contexts (`run_id`, `run_number`, `run_attempt`): <https://docs.github.com/en/actions/reference/workflows-and-actions/contexts>
- GitHub REST workflow-runs endpoint / filtering and pagination: <https://docs.github.com/en/rest/actions/workflow-runs>

GitHub documents that a pull request can be marked merged when its head commits become reachable from the base branch **outside that pull request**, including via another pull request. GitHub calls this an indirect merge. The documentation specifically notes that merging the other PR with **Create a merge commit** can make the first PR be marked merged indirectly.

For Actions chronology, GitHub documents `github.run_id` as a unique number for a workflow run. By contrast, `github.run_number` explicitly begins at 1 and increments with each new run of a workflow, while `github.run_attempt` increments for reruns. The frozen contract's stronger assumption that numeric `run_id` order is an authoritative latest-run chronology is not established by the primary contract read in this review.

## HIGH findings

### H-01 — Indirect merges leave exact PR-number transport provenance unproved

**Severity:** HIGH, blocking  
**Area:** exact PR identity / positive server merge provenance / merge-strategy neutrality

The target is materially stronger than the historical spec. In particular, the explicit historical attack:

- expected PR A / ref A / SHA A / payload P;
- different PR B / ref B / **different SHA B** / byte-identical P;
- B merges first;

is rejected because the target requires the exact finalized expected PR number, expected ref, expected head SHA, expected base relation, exact-head Verify, server merge observation and canonical read-back. **Canonical byte equality alone cannot recover `ACTIVE_NEXT`.** Therefore the requested narrow `BYTE_IDENTICAL_SUBSTITUTION` check passes.

But the stronger positive statement required by M-01 — "THIS expected PR/head created THIS canonical acquisition" — is still not established for all GitHub-observable states allowed by the frozen contract.

Adversarial construction:

1. Expected PR **A** is finalized with expected ref A, head SHA `H`, expected base `B0`, and lock-only tree effect `P`.
2. A different PR **B** uses a different head ref but points to the **same head commits / same head SHA `H`**.
3. B is merged into `main` using the repository's allowed merge-commit strategy.
4. GitHub's documented indirect-merge behaviour can mark A as merged because A's head commits became reachable through B.
5. Fresh A still has the exact expected PR number, repository, ref A and SHA `H`; current main contains the exact expected lock tree effect and bytes.

The target then relies on `merged=true`, non-null `merged_at`, `merge_commit_sha`, current-main reachability and exact tree effect as positive expected-PR provenance. GitHub's primary documentation, however, explicitly says merged state can arise indirectly and does not establish that those fields constitute a proof that PR-number A itself was the merge operation that caused the acquisition rather than B.

Thus the frozen predicate can prove that the expected **commit/tree acquisition** reached canonical main, but it cannot positively prove the stronger exact **PR-number transport attribution** in an indirect-merge state. The rereview instructions explicitly require stopping rather than resolving that GitHub semantic ambiguity in favour of the writer.

This is a HIGH blocker because another PR can be the practical canonical transport while `ACTIVE_NEXT` is attributed to the expected PR identity. The contract must either fail closed on indirect-merge-ambiguous states or use/restrict to a directly provable transport mechanism. This reviewer does not redesign the target.

**Result:** `EXACT_PR_IDENTITY = FAIL`, `SERVER_MERGE_PROVENANCE = FAIL`, historical `M-01 = OPEN`.

## MEDIUM findings

### M-02 — Greatest numeric `run_id` is not a documented latest-run ordering contract

**Severity:** MEDIUM, blocking  
**Area:** latest Verify semantics

Section 19.2 and preregistered test 55 make the matching run with the greatest numeric `run_id` authoritative. GitHub's primary Actions documentation says `run_id` is unique, but does not state that numeric ordering of `run_id` is the supported chronology relation. It explicitly documents increment semantics for `run_number` and separately for `run_attempt`.

The desired policy is correct: if an older exact-head Verify succeeded but a later relevant run failed, was cancelled, is in progress or is queued, the old green must not remain authoritative. The blocker is that the frozen comparator for deciding which run is later is not itself grounded in a documented ordering guarantee.

The target's pagination/completeness rule is otherwise acceptable: if the complete relevant run set cannot be fresh-observed, or rows are malformed/truncated, provenance must fail closed. An implementation must preserve that property and must not silently reuse a bounded one-page inherited helper.

**Result:** `LATEST_VERIFY = FAIL`; `VERIFY_PAGINATION_FAIL_CLOSED = PASS` at the contract level.

## Mandatory review areas A–J

### A. Exact PR/head substitution resistance

**PASS for the specified byte-identical different-head adversary.** Exact expected repository, PR number, head ref, head SHA, base and server observation make PR B with a different head SHA non-equivalent even when P is byte-identical. Canonical lock equality alone cannot restore `ACTIVE_NEXT`.

A separate same-head/different-ref indirect-merge hole remains and is recorded under H-01 / threat #3; this is why the stronger M-01 positive provenance claim remains open.

### B. Positive canonical merge provenance

**FAIL.** The source epoch -> RELEASE proof -> fresh post-RELEASE main -> continuation context -> selection -> acquire intent -> finalized expected acquisition -> exact head/base/Verify -> canonical lock chain is well bound. The failing implication is: "fresh expected PR is reported merged" => "this exact PR number was the transport operation that created the acquisition." GitHub documents indirect merges, so that implication is not established.

### C. GitHub merge semantics feasibility

**FAIL.** The repository allows merge commit, squash and rebase. GitHub documents strategy-dependent merge results and indirect merge behaviour. The target's unconditional merge-strategy-neutral provenance claim is too strong unless indirect-merge ambiguity is explicitly rejected or direct provenance is otherwise proved.

### D. Expected base binding

**PASS.** `ExpectedAcquireV1.expected_base_sha == SelectionV1.selection_main_sha == expected lock payload base_main_sha` is frozen; expected base/head Git ancestry and exact base-to-head lock-only tree effect are required. A later main SHA cannot silently replace the expected base. Strict current-main revalidation remains inherited.

### E. latest Verify semantics

**FAIL.** The desired precedence is safe, but maximum numeric `run_id` is not established by primary documentation as a chronology key. Incomplete workflow-run observation is correctly fail-closed.

### F. stale webhook replay

**PASS.** Delivery/event data is trigger-only. Main, PR, head, base, Verify, lock and source epoch must be fresh-read/rederived; stale payload cannot revive an old epoch.

### G. same-class candidate ordering

**PASS.** Two eligible RELEASEs -> lowest PR; malformed lower RELEASE -> local rejection and later valid candidate continues. Two eligible ACQUIREs -> lowest PR only if no eligible RELEASE. RELEASE + ACQUIRE -> RELEASE wins. Trusted run mutates at most once.

### H. 55-test matrix

**FAIL overall, effective new-area coverage 4/5.** Rows 51–54 are genuine distinct coverage additions: #51 covers the historical byte-identical different-head alternate PR substitution; #52 stale webhook; #53 multiple RELEASE; #54 multiple ACQUIRE. Row #55 encodes the unsupported max-numeric-`run_id` chronology assumption and therefore cannot yet be accepted as a sound security regression. In addition, the newly exposed same-head/different-ref indirect-merge state needs explicit negative regression coverage before positive exact-PR provenance can be accepted.

### I. Phase A compatibility

**PASS.** Accepted Phase A remains pure/read-only and ends at `ACQUIRE_PENDING`. It does not gain GitHub mutation, Truth, review, merge or canonical ownership inference authority.

### J. Trust boundary

**PASS.** The remediation does not require a new PAT/secret, Ruleset weakening, broader `GITHUB_TOKEN`, `pull_request_target`, PR-head trusted execution, worker-as-credential semantics, automatic RENEW/TAKEOVER, Truth promotion, automatic I2/I3, or Task/Campaign creation authority. `scripts/lock_auto_activate.py` remains the narrow trusted-main lifecycle primitive.

## Threat-model challenge

1. **same bytes, wrong PR — PASS for the specified different-head case.** Exact PR/head identity prevents different SHA B from being treated as expected A merely because bytes match. Same-head/ref substitution is separately #3.
2. **same PR number observation but moved head — PASS.** Fresh exact head/ref equality is mandatory.
3. **same head SHA, wrong ref — FAIL.** Different PR/ref B can share expected commit H, merge first with merge-commit, and cause A to be marked merged indirectly; positive exact PR-number transport attribution is not established.
4. **correct expected head but wrong/stale base — PASS.** Exact expected selection base and Git relation are required; later main is not substituted.
5. **old green Verify + newer failure — FAIL.** The intended outcome is NOT eligible, but the target's definition of "newer" as max numeric `run_id` lacks a primary ordering guarantee.
6. **old green Verify + newer in-progress — FAIL.** Same comparator blocker; cancelled/queued have the same issue.
7. **stale webhook after canonical main moved — PASS.** Trigger-only and full fresh rederivation required.
8. **expected PR closed but not merged — PASS.** Closed alone is insufficient; merged fields/history relation are required.
9. **another PR merged exact bytes — PASS when it has a different head SHA, as in the historical substitution case.** Same expected commit/head reached through another PR is the #3 indirect-merge blocker.
10. **expected PR merged but merge result not reachable from fresh main — PASS.** Explicitly rejected.
11. **merge result reachable but delta includes unrelated path — PASS.** Exact expected-base -> merge-result lock-only path/tree effect required.
12. **canonical lock later renewed/replaced — PASS.** Exact active canonical lock bundle/OIDs/bytes/identity/timestamps are fresh-read; replacement is a different acquisition.
13. **same task/worker/principal but old acquisition epoch — PASS.** Source epoch, continuation, selection, intent and deterministic lock identity bind the epoch.
14. **partial/truncated workflow-run observation — PASS.** Contract requires fail-closed provenance-unavailable result if completeness cannot be proved.
15. **two eligible RELEASEs — PASS.** Deterministic lowest PR; malformed lower candidate local; one mutation max.
16. **two eligible ACQUIREs — PASS.** Deterministic lowest PR when no RELEASE eligible; malformed lower candidate local; one mutation max.
17. **RELEASE and ACQUIRE simultaneous — PASS.** RELEASE wins and ACQUIRE waits for a later trusted invocation.

## Acceptance-field summary

```text
CURRENT_MAIN: 84a046359b299950403b68bfcb190930ebbc4c3f
TARGET: d46395c1ff2d379cd7fab841f090abbdf8bbf8b5
TARGET_MATCH: YES
TARGET_PARENT: c3532324e9df421afc787aa6cee3d91f8dbaa91e
TARGET_BLOB: 6c47e1721383d3a7c8e2e6ba01f3ec846bb23a52
SCOPE_MATCH: YES

M01: OPEN
EXACT_PR_IDENTITY: FAIL
BYTE_IDENTICAL_SUBSTITUTION: PASS
BASE_BINDING: PASS
LATEST_VERIFY: FAIL
VERIFY_PAGINATION_FAIL_CLOSED: PASS
STALE_WEBHOOK: PASS
SERVER_MERGE_PROVENANCE: FAIL
CANONICAL_MAIN_REACHABILITY: PASS
CANONICAL_LOCK_READBACK: PASS
PHASE_A_BOUNDARY: PASS
MULTIPLE_RELEASE: PASS
MULTIPLE_ACQUIRE: PASS
RELEASE_BEFORE_ACQUIRE: PASS
AT_MOST_ONE_MUTATION: PASS
PREREGISTERED_55_TESTS: FAIL

CRITICAL: none
HIGH: H-01 indirect-merge semantics prevent positive exact expected-PR-number transport provenance under the frozen merge-strategy-neutral predicate.
MEDIUM: M-02 greatest numeric workflow run_id is not documented as the authoritative latest-run chronology key.
LOW: none independently blocking.

VERDICT: FAIL
PHASE_B_IMPLEMENTATION_ALLOWED: NO
```

## Required next step

Return this fixed review result to the Village coordinator. Do **not** implement Phase B from this target.

A new design remediation must remove/fail-closed the GitHub indirect-merge ambiguity for exact transport provenance and replace or justify the latest-Verify ordering with a primary-documented, deterministic, fail-closed relation. Its acceptance matrix must include the same-head/different-ref indirect-merge negative control and a sound latest-run precedence test, followed by another independent focused review.

No production code, target design file, workflow, lock file, Ruleset, setting, Task/Campaign/Portfolio, Truth/research/outcome file, or other review lane was modified by this review.
