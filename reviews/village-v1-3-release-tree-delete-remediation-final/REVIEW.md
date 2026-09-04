# Village RELEASE tree deletion remediation — independent review

TASK-ID: `AIMATH-VILLAGE-V1-3-RELEASE-TREE-DELETE-INDEPENDENT-REVIEW`

## Fixed review target

- repository: `51mns/AIMath-public`
- current main: `ee5299ed8714c0b8fb0c9149cb544ef89ebbf23b`
- target commit: `8566e432672724bf0f4d210734ba3c60dfd742b7`
- target parent: `ee5299ed8714c0b8fb0c9149cb544ef89ebbf23b`
- target core blob: `25eb397a18eb2913c3a5090255519da7100354f8`
- target test blob: `0fcc38dac057fdfc514f4f3dfd2de9adca95699b`
- PR: `#49`
- exact-head Verify: run number `126`, run id `33835150583`, workflow id `347191396`, head `8566e432672724bf0f4d210734ba3c60dfd742b7`, `completed/success`

## Scope and method

I reviewed the fixed Git objects and PR independently rather than accepting the remediation description as evidence. The target is exactly one commit ahead of the fixed main and changes exactly:

1. `scripts/village_next_phase_b.py`
2. `scripts/test_village_v1_3_next_phase_b.py`

No workflow, schema, lifecycle writer, source lock, terminal, governance state, or other file is changed by the target.

The shell sandbox could not resolve GitHub for a separate local clone, so no claim of an additional local execution is made here. Independent evidence instead consists of fixed-commit/blob reads, target/parent comparison, direct source inspection, the exact-head GitHub Actions record, and fresh canonical Git-tree reads.

## GitHub create-tree deletion contract

GitHub's `Create a tree` REST contract defines each tree entry by `path`, `mode`, `type`, and `sha`; `sha: null` means delete the file. Valid regular-file blob mode is `100644` and type is `blob`.

Primary reference: <https://docs.github.com/en/rest/git/trees?apiVersion=2022-11-28#create-a-tree>

The parent implementation emitted deletion entries as:

```json
{"path": "...", "sha": null}
```

The target emits:

```json
{"path": "...", "mode": "100644", "type": "blob", "sha": null}
```

This is valid for the RELEASE source lock reviewed here. The frozen/public Village contract requires canonical lock objects to be regular `100644` blobs, and fresh main Git-tree observation confirms the live source lock is exactly mode `100644`, type `blob`, blob `6604acaf8c458a4893fc746fd689326b0d5d3722`.

The repair is therefore semantically narrow: it supplies the object metadata GitHub validates while preserving `sha: null` deletion semantics.

## ACQUIRE and authority boundary

`GitHubPhaseBClient.create_tree()` has two production call shapes in the reviewed target:

- RELEASE calls it with no additions and the frozen source-lock paths in `deletions`.
- ACQUIRE calls it with the already-frozen `exact_lock_objects` and no deletions.

Therefore the changed deletion-entry construction does not alter ACQUIRE lock bytes, blob OIDs, V3 semantic identity, expected canonical tree derivation, Task selection, Verify lineage, Ruleset gates, or canonical acquisition semantics.

The target adds no new mutation entry point and changes no lifecycle handoff. `scripts/lock_auto_activate.py` remains unchanged and remains the narrow trusted canonical RELEASE/ACQUIRE mutation primitive. No manual main/lock mutation authority, Truth authority, review authority, `RENEW`, or `TAKEOVER` authority is introduced.

## Row 14 regression coverage

Row 14 still covers deterministic RELEASE transport reuse and now additionally invokes `GitHubPhaseBClient.create_tree()` with a deletion, captures the exact POST request, and requires:

- method `POST`;
- path `/repos/51mns/AIMath-public/git/trees`;
- exact tree payload containing `path`, `mode: 100644`, `type: blob`, and `sha: null`.

The prior implementation would emit only `path` and `sha`, so it cannot satisfy the strengthened exact-payload assertion. The observed `422 Must supply a valid tree.mode` regression is therefore directly covered without adding a new specification row.

## 73-row contract and exact-head verification

The fixed target test file retains `SPEC_ROW_TO_TEST` for rows `1..73` and import-time assertions requiring:

- keys exactly `range(1, 74)`;
- 73 unique mapped test names;
- every mapped method to exist;
- exactly 73 `test_...` methods on the Phase B test class.

There is no Row 74 and no `test_row_74`.

The target `scripts/village.py test` command includes `scripts/test_village_v1_3_next_phase_b.py`. Exact-head Verify #126 completed successfully on the target SHA, including the `Village synthetic acceptance tests` step, so the strengthened Row 14 and the 73-row import/runtime contract passed at that exact head. The same Verify job also passed its DCO 1.1 sign-off check.

## Live source-state preservation

Fresh main Git-tree observation confirms:

- source lock `coordination/locks/eq18/general-structural-obstruction.yml` → `6604acaf8c458a4893fc746fd689326b0d5d3722`, mode `100644`, type `blob`;
- source terminal `work/TASK-EQUIANGULAR-R18-001/w-0bebfd2fd11cb67f/ABANDONED_TERMINAL.yml` → `e4de1a405499907d65cc6ff81c6394ae8442cfe0`, mode `100644`, type `blob`.

The target diff does not touch either path.

## Findings

- CRITICAL: none
- HIGH: none
- MEDIUM: none
- LOW: none

## Verdict

**PASS**

The remediation is accepted for the fixed target. PR #49 is ready for merge from this review's technical scope, subject to the repository's normal protected-branch merge gates. This review does not merge PR #49 and grants no authority beyond that assessment.
