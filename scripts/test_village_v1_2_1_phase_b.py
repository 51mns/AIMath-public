#!/usr/bin/env python3
# SPDX-FileCopyrightText: 2026 AIMath contributors
# SPDX-License-Identifier: Apache-2.0
from __future__ import annotations

from pathlib import Path
import hashlib
import unittest
from unittest.mock import patch

from lock_auto_activate import (
    AutoActivationError,
    AutoAcquireCandidate,
    _has_successful_verify,
    _scan_acquires,
    auto_acquire_preflight,
    choose_acquire_candidate,
)

MAIN_SHA = "a" * 40
HEAD_A = "b" * 40
HEAD_B = "c" * 40
W_A = "w-" + "a" * 16


def _pr(number: int, *, head=HEAD_A, actor="51mns", base=MAIN_SHA, draft=False, repo="51mns/AIMath-public"):
    return {
        "number": number,
        "state": "open",
        "draft": draft,
        "base": {"ref": "main", "sha": base},
        "head": {
            "ref": f"lock/TASK-X-1/{W_A}",
            "sha": head,
            "repo": {"full_name": repo},
        },
        "user": {"login": actor},
    }


def _files(*, status="added", path="coordination/locks/x/shared.yml"):
    return [{"filename": path, "status": status, "sha": "d" * 40}]


class PhaseB(unittest.TestCase):
    def test_01_deterministic_acquire_order(self):
        a = AutoAcquireCandidate(_pr(20), [], "L20", "TASK-X-20", W_A)
        b = AutoAcquireCandidate(_pr(10), [], "L10", "TASK-X-10", W_A)
        self.assertEqual(choose_acquire_candidate([a, b]).pr["number"], 10)

    def test_02_invalid_lower_not_blocking_authority(self):
        valid = AutoAcquireCandidate(_pr(20), [], "L20", "TASK-X-20", W_A)
        self.assertEqual(choose_acquire_candidate([valid]).pr["number"], 20)

    def test_03_discovered_acquire_uses_v12_shape_gate(self):
        ok, errors = auto_acquire_preflight(
            _pr(10),
            _files(),
            repository="51mns/AIMath-public",
            current_main_sha=MAIN_SHA,
            maintainers={"51mns"},
        )
        self.assertTrue(ok, errors)

    def test_04_discovered_acquire_fail_closed_classes(self):
        cases = [
            _pr(10, actor="ordinary"),
            _pr(10, base="e" * 40),
            _pr(10, draft=True),
            _pr(10, repo="fork/example"),
        ]
        for pr in cases:
            ok, _ = auto_acquire_preflight(
                pr,
                _files(),
                repository="51mns/AIMath-public",
                current_main_sha=MAIN_SHA,
                maintainers={"51mns"},
            )
            self.assertFalse(ok)
        for files in (
            _files(status="modified"),
            _files(path="research/x/PROOF.md"),
        ):
            ok, _ = auto_acquire_preflight(
                _pr(10),
                files,
                repository="51mns/AIMath-public",
                current_main_sha=MAIN_SHA,
                maintainers={"51mns"},
            )
            self.assertFalse(ok)

    def test_05_exact_green_ci_latest_run_required(self):
        with patch(
            "lock_auto_activate_phase_a._request_json",
            return_value={
                "workflow_runs": [
                    {"id": 1, "name": "Verify public release", "head_sha": HEAD_A, "status": "completed", "conclusion": "success"},
                    {"id": 2, "name": "Verify public release", "head_sha": HEAD_A, "status": "completed", "conclusion": "failure"},
                ]
            },
        ):
            self.assertFalse(_has_successful_verify("t", "51mns/AIMath-public", HEAD_A))
        with patch(
            "lock_auto_activate_phase_a._request_json",
            return_value={
                "workflow_runs": [
                    {"id": 3, "name": "Verify public release", "head_sha": HEAD_A, "status": "completed", "conclusion": "success"}
                ]
            },
        ):
            self.assertTrue(_has_successful_verify("t", "51mns/AIMath-public", HEAD_A))

    def test_06_candidate_local_failure_does_not_block_later_valid(self):
        bad = _pr(10, head=HEAD_A)
        good = _pr(20, head=HEAD_B)
        valid = AutoAcquireCandidate(good, _files(), "L20", "TASK-X-20", W_A)
        with patch(
            "lock_auto_activate._eligible_acquire_candidate",
            side_effect=[AutoActivationError("bounded candidate failure"), (valid, [])],
        ):
            got = _scan_acquires(
                "t",
                "51mns/AIMath-public",
                [bad, good],
                current_main_sha=MAIN_SHA,
                base_state=object(),
                maintainers={"51mns"},
            )
        self.assertEqual([c.pr["number"] for c in got], [20])

    def test_07_phase_a_frozen_blob_is_preserved_exactly(self):
        root = Path(__file__).resolve().parent.parent
        data = (root / "scripts/lock_auto_activate_phase_a.py").read_bytes()
        oid = hashlib.sha1(f"blob {len(data)}\0".encode() + data).hexdigest()
        self.assertEqual(oid, "3e885b728786e253f9906f7d3abc3e176f1b1c91")

    def test_08_phase_b_wrapper_does_not_create_prs_or_refs(self):
        source = Path(__file__).with_name("lock_auto_activate.py").read_text(encoding="utf-8")
        self.assertNotIn('"POST"', source)
        self.assertNotIn("/git/refs", source)
        self.assertNotIn("create pull", source.lower())

    def test_09_phase_b_architecture_keeps_release_priority(self):
        root = Path(__file__).resolve().parent.parent
        text = (root / "docs/VILLAGE_ARCHITECTURE_V1_2_1.md").read_text(encoding="utf-8")
        self.assertIn("eligible RELEASE > triggering eligible ACQUIRE", text)
        self.assertIn("after RELEASE candidates are exhausted", text)
        self.assertIn("ascending PR number", text)

    def test_10_renew_takeover_remain_nonautomatic(self):
        root = Path(__file__).resolve().parent.parent
        text = (root / "docs/VILLAGE_ARCHITECTURE_V1_2_1.md").read_text(encoding="utf-8")
        self.assertIn("`RENEW` and `TAKEOVER` remain nonautomatic", text)


if __name__ == "__main__":
    unittest.main(verbosity=2)
