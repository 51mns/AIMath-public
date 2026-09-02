<!-- SPDX-FileCopyrightText: 2026 AIMath contributors -->
<!-- SPDX-License-Identifier: Apache-2.0 -->
# Village v1.2.1 Phase A — M-01 focused independent rereview

- Task: `AIMATH-VILLAGE-V1-2-1-PHASE-A-M01-FOCUSED-REREVIEW`
- Repository: `51mns/AIMath-public`
- Current public main: `71547cb5d757afaace54b558f2d0a4a49fad5656`
- PR: `#28`, OPEN, not merged
- Previous fixed head: `f03ada7a5d5ee3367daa795d70996c5317b69cef`
- New fixed head: `bb8701f551dbf3c155a4352931aa9f17f4588339`
- Focused verdict: **PASS**
- M-01: **CLOSED**
- Live activation: **SETTING_CONFIRMATION_REQUIRED**
- Phase B started: **NO**

## Fixed boundary

Fresh compare of `f03ada7...` to `bb8701f...` is exactly 2 commits and 2 files:

1. `scripts/workflow_security.py`
2. `scripts/test_village_v1_2_1.py`

No Phase A lifecycle core file changed in the focused fix. Therefore the previously reviewed exact-worker RELEASE, RELEASE isolation, ACQUIRE authority, RENEW/TAKEOVER firewall, terminalisation/cooldown and Truth Layer boundaries have no regression by this diff.

## M-01 closure

The trusted lifecycle parser now fail-closes on an exact Phase A structure. It requires one `activate` job and exactly three steps: pinned `actions/checkout` of literal `main` with `persist-credentials: false`, pinned `actions/setup-python` for Python 3.12, and exact `python3 scripts/lock_auto_activate.py`. Unknown jobs, steps, top/job keys and additional write-capable structure are rejected.

`${{ github.token }}` is structurally located and must occur only at `jobs.activate.steps[2].env.GITHUB_TOKEN`. The activation environment must equal the audited two-key map containing `GITHUB_TOKEN` and `SOURCE_RUN_ID`.

Trusted lifecycle local composite actions (`uses: ./...`) are forbidden in Phase A. Docker actions (`docker://...`) are forbidden by the workflow security policy, including digest-shaped references.

## Independent adversarial fixtures

The rereview did not rely only on the writer regression suite. The fixed parser logic was independently exercised against fresh parsed-YAML mutations derived from the fixed trusted workflow.

Rejected:

- original M-01 arbitrary extra run + `github.token`;
- original M-01 job-level token plus local composite;
- original M-01 mutable `docker://alpine:latest`;
- unknown extra job;
- extra arbitrary run without changing the activation command;
- unexpected workflow-level key;
- unexpected job-level key;
- workflow-level `github.token` env;
- job-level `github.token` env;
- checkout-step `github.token` env;
- setup-python-step `github.token` env;
- unrelated additional-step token env;
- activation token moved to a different env variable name;
- direct `uses: ./.github/actions/x`;
- `docker://alpine`;
- `docker://ghcr.io/example/x:1`;
- `docker://image@sha256:<64hex>`.

Positive controls passed:

- actual trusted lifecycle workflow shape;
- exact allowed activation token position;
- ordinary read-only workflow;
- pinned standard GitHub actions.

No equivalent M-01 bypass was found.

## CI evidence

Fresh exact-head lookup found `Verify public release` run `33601339054` (run #71), completed `success`. The job log identifies PR head `bb8701f551dbf3c155a4352931aa9f17f4588339` and shows:

- `python3 scripts/workflow_security.py .` — PASS / exit 0;
- `python3 scripts/village.py test` — 25/25 PASS / exit 0;
- `python3 scripts/test_village_v1_2.py` — 28/28 PASS / exit 0;
- `python3 scripts/test_village_v1_2_1.py` — 37/37 PASS / exit 0.

The same run also passed DCO, public safety audit, layout validation, REUSE and public-claim replay.

## Strict setting gate

Fresh read of `GET /repos/51mns/AIMath-public/branches/main/protection/required_status_checks` still returns `403 Resource not accessible by integration`. This is separate from M-01. The previously reviewed implementation fails closed when strict status checks cannot be confirmed, so code security may pass while live automatic activation remains blocked pending explicit setting confirmation.

## Conclusion

No CRITICAL, HIGH, MEDIUM or new LOW security finding was found in the focused V2 diff. M-01 is closed. Code is merge-ready from this focused security perspective, with the existing strict-server-setting gate still required before live automatic activation. PR #28 was not merged and Phase B was not started by this review.
