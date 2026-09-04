# Village v1.3 `/next` final live execution report

TASK-ID: `AIMATH-VILLAGE-V1-3-NEXT-FINAL-LIVE-FIELD`

Observed at: `2026-09-04T01:11:34Z`

## Disposition

`FINAL_VERDICT = LIVE_FIELD_ABORTED_ACTIVE_WORK_OPERATOR_MISMATCH`

The authenticated read-only preflight passed and the preregistered source
ACQUIRE was canonicalised by the trusted lifecycle as `M1`. The first mandatory
pre-terminal invocation of the actual reviewed production operator then
returned `SOURCE_TERMINAL_UNPROVEN` with exit code `2`, rather than the frozen
plan's required `ACTIVE_WORK` result. This is the first violated invariant.

The no-adaptation rule was applied. No terminal, RELEASE transport, V3 ACQUIRE
transport, Truth object, Claim object, Review object, research-result acceptance,
or cleanup mutation was created after the mismatch. The exact source lock
remains active for coordinator handling; it was not manually deleted or
substituted with an unreviewed release procedure.

## Fixed authority read-back

- Starting main `M0`: `7dc8541c0a9e19f37910e06bc4738375c4c7af00`
- M0 tree: `8ea11092584142fb1b0dcc724a50e0e635e26eea`
- Historical field plan commit/blob: `705bd7c5250103e74118381106d422d50c677bb7` / `05848a5d2998e42e5e02443f331194c61486f3b6`
- V3 supplement commit/blob: `95edc35b9e54e91bd3d11ab58160f159508df2c7` / `0b3059736d8b78ac9f511edffd05def19fa3a651`
- Phase-0 report: `980e139f8c9dbc3e9d40f4252ca6cfd4f71755c1`
- Phase-0 PASS addendum: `a9f7aadc1757e22d84e3941a074e6fa9d55159bd`
- `scripts/village.py` blob: `425f1c9ce6dbd684cd497818920de55e49440da6`
- `scripts/village_next_phase_b.py` blob: `25aed74d7e85e8543fc93230968f7b70931b4aee`
- `scripts/test_village_v1_3_next_phase_b.py` blob: `508b25287a8c21f4dc76b3f59663818ec3f82c55`

## Authenticated Codex preflight

- Authenticated principal: `gh:51mns`
- Actual production client: `GitHubPhaseBClient`
- Fresh client main: exact `M0`
- Recursive main tree: complete, `292` entries
- Open base-main PR observation: complete, `8` PRs
- Open lock-path lifecycle candidates: none
- Repository viewer permission: `ADMIN`
- Repository permission flags: pull/push/triage/maintain/admin all true
- Verify workflow: id `347191396`, name `Verify public release`, path `.github/workflows/verify.yml`, state `active`
- Exact-head Verify observation through the production client was positively exercised on existing PR heads, including PR #40 run number `113`, run id `33703255656`, attempt `1`, completed/success.
- Ruleset proof: `RULESET_PROOF_CONFIRMED`
- Effective Ruleset id: `22089746`
- Required context: `verify`
- `strict_required_status_checks_policy = true`
- Detailed Ruleset: active, `~DEFAULT_BRANCH`, no bypass actors, `current_user_can_bypass = never`
- `python3 scripts/village.py validate`: PASS (`10` campaigns, `12` tasks, `11` public claim metadata records, `0` research evaluations)
- Frozen worker and wrong-worker current-main history: absent before setup
- Source lock, next lock, source terminal and next terminal: absent before setup
- Token contents were never printed, committed, or written to the retained state file.

## Source ACQUIRE and M1

- Source PR: `#46`
- Source head ref: `lock/TASK-EQUIANGULAR-R18-001/w-0bebfd2fd11cb67f`
- Source head: `dc29efff77ebc200763d4d0e6ca0c2381d986595`
- Source head parent: `M0`
- Changed path only: `A coordination/locks/eq18/general-structural-obstruction.yml`
- Source head policy preflight: `PR_CHANGE_CLASS=LOCK_ONLY`, `LOCK_OPERATION=ACQUIRE`, PASS
- Source head DCO: present
- Verify workflow/run: `Verify public release`, run number `121`, run id `33824485594`, attempt `1`, event `pull_request`, exact head `dc29efff77ebc200763d4d0e6ca0c2381d986595`, completed/success
- Trusted lifecycle run: `33824508025`, completed/success
- Trusted lifecycle result: `AUTO_ACTIVATED_PR=46`
- Trusted lifecycle reported merge SHA: `b01bf39c2387d8e1f0dc4cfd60d6e1bb56b0a10d`
- Canonical `M1`: `b01bf39c2387d8e1f0dc4cfd60d6e1bb56b0a10d`
- M1 parent: `M0`
- M1 tree: `0e6ba3ceaf8539249bd196f44b70f782c2ece273`
- Exact M0-to-M1 delta: only the source lock addition
- Canonical source lock mode/type: `100644` / blob
- Canonical source lock blob: `6604acaf8c458a4893fc746fd689326b0d5d3722`
- Canonical source lock size: `547` bytes
- Runtime status at M1: `TASK-EQUIANGULAR-R18-001 ACTIVE`
- Expected-next runtime status at M1: `TASK-DITTERT-N5-001 READY`

## First violated invariant

The exact production operator was executed from a clean detached checkout of
`M1`, using the authenticated token only through the process environment and the
required retained-state path under `.git`:

```text
python3 scripts/village.py next \
  --root . \
  --task-id TASK-EQUIANGULAR-R18-001 \
  --worker-id w-0bebfd2fd11cb67f \
  --principal-id gh:51mns \
  --github-write yes \
  --local-compute yes \
  --web-literature yes \
  --current-main-sha b01bf39c2387d8e1f0dc4cfd60d6e1bb56b0a10d \
  --github-token-env GITHUB_TOKEN \
  --phase-b-state-file .git/village-next-phase-b-live-field.json
```

Observed exact result:

```text
FAIL: SOURCE_TERMINAL_UNPROVEN: no canonical terminal evidence
```

Exit code: `2`.

The retained state file was not created. No RELEASE ref/PR and no
`next-acquire/**` ref/PR for the frozen worker exists after the abort.

The frozen plan requires this pre-terminal call to prove `ACTIVE_WORK` and
create no transport. The current production CLI instead requires terminal
evidence before it can derive the source record. This mismatch must be resolved
by a separately reviewed production-contract decision; it was not adapted in
the live run.

## State at abort

- Current main: `M1 = b01bf39c2387d8e1f0dc4cfd60d6e1bb56b0a10d`
- Current main tree: `0e6ba3ceaf8539249bd196f44b70f782c2ece273`
- Source lock: present and active
- Source terminal: absent
- Release transport/ref/PR: absent
- Next ACQUIRE transport/ref/PR: absent
- Next lock: absent
- `M2`, `M3`, `M4`: not reached
- `SOURCE_EPOCH_ID`: not derivable before canonical terminal evidence under the accepted implementation
- `CONTINUATION_CONTEXT_ID`: not reached
- `SELECTION_ID`: not reached
- `ACQUIRE_INTENT_ID`: not reached
- `CANONICAL_ACQUIRE_ID`: not reached
- V3 `B`, `T`, `H`, `M`: not reached
- Truth effect: `NONE`
- Claim effect: `NONE`
- Review effect: `NONE`
- Research-result acceptance effect: `NONE`
- Active field-test locks after abort: `1` (the exact source lock)
- Fresh Ruleset proof after abort: PASS
- `GITHUB_TOKEN` in subsequent shell context: unset

## Coordinator action required

Do not continue this retained epoch by pretending the failed pre-terminal result
was `ACTIVE_WORK`. Decide separately whether the frozen live plan or the accepted
production CLI contract must be amended and independently reviewed. The current
source lock should be cleaned only through an explicitly reviewed, truth-neutral,
exact-worker release procedure; this execution lane did not improvise one.
