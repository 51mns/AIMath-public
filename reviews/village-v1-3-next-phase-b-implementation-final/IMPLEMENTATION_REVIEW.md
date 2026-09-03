# Village v1.3 Phase B independent implementation review — persisted FAIL

TASK-ID: `AIMATH-VILLAGE-V1-3-PHASE-B-FAILED-REVIEW-PERSISTENCE`

This file persists the already-completed independent implementation review. It does not re-review the implementation to soften, broaden, or replace the prior findings, and it makes no production change.

## 1. Fixed review identity

- Repository: `51mns/AIMath-public`
- Fresh-read current main: `84a046359b299950403b68bfcb190930ebbc4c3f`
- Fixed reviewed target: `2b6b4329ac58f9fbad319f6629d1dc9d465457c8`
- Target parent: `84a046359b299950403b68bfcb190930ebbc4c3f`
- Target tree: `7ba4b29cbd291956b6578d3e0fd726d5725b7f19`
- Frozen implementation oracle: `1e81606b2a059a7ae59ec80aa68f9e9d2f67358b`
- Accepted/fixed Phase-B V3 spec: `a482d1f4398489753589afe1ef3ed5e593a7e9c4`
- PR: `#40`, fresh-read open, non-draft, unmerged, base `84a046359b299950403b68bfcb190930ebbc4c3f`, head `2b6b4329ac58f9fbad319f6629d1dc9d465457c8`
- Verify: workflow run number `113`, run id `33703255656`, exact head `2b6b4329ac58f9fbad319f6629d1dc9d465457c8`, completed with `success`

Exact target changed paths are only:

1. `docs/VILLAGE_ARCHITECTURE_V1_3_PHASE_B.md`
2. `scripts/test_village_v1_3_next_phase_b.py`
3. `scripts/village_next_phase_b.py`

Fresh-read target blobs:

- `docs/VILLAGE_ARCHITECTURE_V1_3_PHASE_B.md` = `6b97ba453c3df60e4916c1c8e027ba262fafe716`
- `scripts/test_village_v1_3_next_phase_b.py` = `08747160701f857cbd341655bb2fca79a27ae508`
- `scripts/village_next_phase_b.py` = `9a942f087e4ad81d9d5ed599f1433a0162b2fe8d`

`TARGET_MATCH = YES`.

## 2. Evidence limitations preserved from the completed review

This review does **not** claim an independently observed local `73/73 PASS`.

The writer PR body states that the direct Phase-B suite passed 73/73, but that writer assertion is not promoted to independent-review evidence. In the completed independent review, a fresh local execution was not available because the reviewer environment could not complete the required network-dependent setup. No local-test PASS is fabricated here.

Fresh read-back of Verify run number 113 confirms that the exact target head had a successful `Verify public release` run. However, that run's job steps do not include a registered `Village v1.3 Phase B direct acceptance tests` step. The successful CI run therefore does not establish that the frozen 73-row Phase-B direct suite was executed by canonical Verify.

The oracle itself requires more than method count or passing mocks: negative rows must reach the exact intended gate with otherwise-valid fixtures, and live/pagination/Ruleset/history claims require appropriate fresh or exact-Git evidence. The P/F matrix below is the completed review's contract-evidence judgement, **not** a table of runtime unittest outcomes.

Clarification from fresh read-back: `Verify #113` is workflow **run number 113**. A repository Issue `#113` does not exist. This clarification does not alter any review finding or verdict.

## 3. Exact frozen 73-row P/F review matrix

`P = contract row adequately supported in the completed review`  
`F = contract row not adequately supported in the completed review`

Count: **39 P / 34 F**.

| Row | Result |
|---:|:---:|
| 01 | F |
| 02 | F |
| 03 | P |
| 04 | P |
| 05 | P |
| 06 | P |
| 07 | P |
| 08 | P |
| 09 | F |
| 10 | P |
| 11 | F |
| 12 | F |
| 13 | P |
| 14 | F |
| 15 | F |
| 16 | P |
| 17 | F |
| 18 | F |
| 19 | P |
| 20 | F |
| 21 | F |
| 22 | F |
| 23 | P |
| 24 | F |
| 25 | F |
| 26 | P |
| 27 | F |
| 28 | F |
| 29 | P |
| 30 | P |
| 31 | P |
| 32 | F |
| 33 | F |
| 34 | P |
| 35 | P |
| 36 | P |
| 37 | P |
| 38 | P |
| 39 | P |
| 40 | P |
| 41 | P |
| 42 | P |
| 43 | P |
| 44 | F |
| 45 | P |
| 46 | P |
| 47 | P |
| 48 | P |
| 49 | F |
| 50 | P |
| 51 | F |
| 52 | P |
| 53 | F |
| 54 | F |
| 55 | F |
| 56 | F |
| 57 | P |
| 58 | P |
| 59 | P |
| 60 | P |
| 61 | F |
| 62 | F |
| 63 | P |
| 64 | F |
| 65 | F |
| 66 | F |
| 67 | F |
| 68 | F |
| 69 | P |
| 70 | P |
| 71 | P |
| 72 | F |
| 73 | F |

Compact checksum of the same matrix:

`01–02 F, 03–08 P, 09 F, 10 P, 11–12 F, 13 P, 14–15 F, 16 P, 17–18 F, 19 P, 20–22 F, 23 P, 24–25 F, 26 P, 27–28 F, 29–31 P, 32–33 F, 34–43 P, 44 F, 45–48 P, 49 F, 50 P, 51 F, 52 P, 53–56 F, 57–60 P, 61–62 F, 63 P, 64–68 F, 69–71 P, 72–73 F`.

## 4. Findings

### HIGH H-01 — canonical stop/dependency state is not freshly derived

The Phase-B orchestration adapter passes `canonical_stop_condition_reached=False` and `canonical_dependency_followup_unusable=False` as literal values while constructing the continuation context. Those two authority-bearing facts are therefore not freshly derived from the canonical Phase-B observation path in the reviewed target.

This is incompatible with accepting the implementation as a complete V3 orchestration adapter. A fixed `False` value can suppress a canonical stop/dependency condition rather than prove its absence.

**Severity: HIGH. Finding remains open.**

### HIGH H-02 — candidate-local exception handling can swallow repository-wide observation failure

While building PENDING observations, candidate processing is wrapped in a broad catch including `PhaseBError`, followed by `continue`. The same exception family is also used for GitHub/repository observation failures.

The code therefore does not prove the required separation between a malformed **candidate-local** observation, which may be dropped while scanning continues, and a **repository-wide/incomplete observation** failure, which must fail closed globally. A repository-wide error encountered inside candidate processing can be swallowed as though it were merely a bad candidate, leaving later ranking/selection to operate on an incomplete substrate.

This conflicts directly with the oracle's candidate-local versus repository-wide fail-closed boundary.

**Severity: HIGH. Finding remains open.**

### MEDIUM M-01 — Ruleset/effective-rule collection completeness is not proven

The reviewed `ruleset_proof()` obtains the effective main-branch rules and the Ruleset summary collection, then fetches details for the returned summaries. The implementation does not establish a complete pagination/result-set proof for the Ruleset/effective-rule collection comparable to the frozen completeness requirement.

Because the security predicate depends on fresh effective Ruleset state, a bounded/single returned collection without explicit completeness proof is insufficient for implementation acceptance.

**Severity: MEDIUM. Finding remains open.**

### MEDIUM M-02 — 73 test methods do not prove the 73 frozen contracts are exercised

The target contains 73 numbered Phase-B test methods, but the frozen oracle does not accept row-number or method-count correspondence by itself. Multiple rows do not provide fixtures that independently satisfy the frozen setup/negative-control obligations and then reach the exact threatened gate.

In particular, a method that asserts a related helper or a shallower failure is not proof that the oracle row's otherwise-valid fixture exercised the required production path. The completed review therefore did not treat `73 methods` as `73 contracts proven`.

This is also why the writer's stated `73/73 PASS`, even if taken at face value as a unittest result, would not by itself remove M-02.

**Severity: MEDIUM. Finding remains open.**

### LOW — frozen semantic-binding result-code mismatch

The frozen oracle's Rows 66/67 use the semantic-binding inconsistency family, including the exact Row-66 code `CANONICAL_ACQUIRE_SEMANTIC_BINDING_INCONSISTENT`. In the reviewed pre-merge semantic-binding path, the target returns `CANONICAL_ACQUIRE_SEMANTIC_BINDING_MISMATCH` for the independently-derived-ID comparison.

The completed review recorded this as a specific result-code/contract mismatch. It is not promoted above LOW because the broader semantic-binding behavior is already covered by more material row/fixture findings; nevertheless, the exact frozen result family should not be silently rewritten after implementation inspection.

**Severity: LOW. Finding remains open.**

## 5. Finding summary

```text
CRITICAL = 0
HIGH = 2
MEDIUM = 2
LOW = 1

H-01 = OPEN
H-02 = OPEN
M-01 = OPEN
M-02 = OPEN
LOW  = OPEN
```

Fresh re-read did not reveal a transcription error in the previously stated H-01/H-02/M-01/M-02/LOW finding set. The Verify-`#113` run-number clarification above is recorded explicitly rather than silently changing terminology.

## 6. Final independent review verdict

```text
VERDICT=FAIL
IMPLEMENTATION_ACCEPTED=NO
STAGE1_READY_FOR_MERGE=NO
MERGE_ALLOWED=NO
```

PR #40 remains prohibited from merge on the reviewed target `2b6b4329ac58f9fbad319f6629d1dc9d465457c8` under this review.

This persistence artifact does not modify production, does not merge, does not create new findings merely to fill space, and does not convert writer-reported or CI-adjacent evidence into a fabricated independent PASS.