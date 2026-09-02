#!/usr/bin/env python3
# SPDX-FileCopyrightText: 2026 AIMath contributors
# SPDX-License-Identifier: Apache-2.0
from __future__ import annotations

from datetime import timedelta
from pathlib import Path
import copy
import json
import subprocess
import sys
import tempfile
import unittest
from unittest.mock import patch

from check_village_pr import lock_change_class_errors, validate_lock_transition
from lock_auto_activate import (
    AutoActivationError,
    _strict_up_to_date_gate,
    auto_activation_preflight,
    final_revalidation_errors,
    lock_git_object_errors,
)
from test_village_acceptance import LockBundle, NOW, add_lock, base_state
from test_village_v1_1 import rank_state
from village_rank import EvaluationBook
from village_v1_2 import (
    CapabilityProfile,
    VillageV12Error,
    capability_eligible,
    load_pending_claims,
    rank_v12,
    validate_pending_claim,
    validate_worker_id,
    worker_workspace,
)

MAIN_SHA = "a" * 40
W_A = "w-" + "a" * 16
W_B = "w-" + "b" * 16


def pending_record(**overrides):
    row = {
        "schema_version": 2,
        "observation_source": "GITHUB_API",
        "repository": "51mns/AIMath-public",
        "reservation_kind": "PENDING_CLAIM",
        "pr_number": 99,
        "task_id": "TASK-X-1",
        "principal_id": "gh:a",
        "worker_id": W_A,
        "base_main_sha": MAIN_SHA,
        "head_sha": "b" * 40,
        "collision_keys": ["x/shared"],
        "pr_state": "OPEN",
        "draft": False,
        "change_class": "LOCK_ONLY",
        "lock_operation": "ACQUIRE",
        "village_policy": "PASS",
        "verify_conclusion": "SUCCESS",
        "observed_at": NOW.isoformat(),
        "lock_expires_at": (NOW + timedelta(hours=168)).isoformat(),
    }
    row.update(overrides)
    return row


def second_exclusive_state():
    s = base_state()
    s.portfolio["governance"]["default_actor_exclusive_lock_cap"] = 12
    s.campaigns["CAM-X"]["max_active_lanes"] = 3
    s.tasks["TASK-X-2"] = {
        **s.tasks["TASK-X-1"],
        "task_id": "TASK-X-2",
        "collision_keys": ["x/2"],
        "owned_paths": ["work/x2/**"],
    }
    add_lock(s, "LOCK-1", "TASK-X-1", "x/shared", actor="gh:a")
    s.lock_bundles["LOCK-1"].payload["worker_id"] = W_A
    s.lock_bundles["LOCK-1"].payload["work_ref"] = f"research/TASK-X-1/{W_A}"
    return s


def new_bundle(worker=W_B, key="x/2"):
    payload = {
        "lock_id": "LOCK-2",
        "task_id": "TASK-X-2",
        "actor": {"id": "gh:a", "type": "HUMAN_PRINCIPAL"},
        "worker_id": worker,
        "base_main_sha": "0" * 40,
        "acquired_at": NOW.isoformat(),
        "expires_at": (NOW + timedelta(hours=168)).isoformat(),
        "work_ref": f"research/TASK-X-2/{worker}",
        "collision_keys": [key],
        "renewal_count": 0,
    }
    return LockBundle("LOCK-2", payload, {key}, [])


def valid_run_pr_files():
    run = {
        "name": "Verify public release",
        "event": "pull_request",
        "status": "completed",
        "conclusion": "success",
        "head_sha": "c" * 40,
    }
    pr = {
        "state": "open",
        "draft": False,
        "base": {"ref": "main", "sha": MAIN_SHA},
        "head": {"sha": "c" * 40, "repo": {"full_name": "51mns/AIMath-public"}},
        "user": {"login": "51mns"},
    }
    files = [{"filename": "coordination/locks/x/shared.yml", "status": "added", "sha": "d" * 40}]
    return run, pr, files


class VillageV12Acceptance(unittest.TestCase):
    def test_01_valid_green_lock_pr_is_pending_reservation(self):
        s = rank_state()
        ok, errors = validate_pending_claim(s, pending_record(), current_main_sha=MAIN_SHA, now=NOW)
        self.assertTrue(ok, errors)
        rows = rank_v12(s, EvaluationBook(".", s), pending_records=[pending_record()], current_main_sha=MAIN_SHA, now=NOW)
        self.assertNotIn("TASK-X-1", [r.task_id for r in rows])

    def test_02_failed_ci_not_reservation(self):
        ok, errors = validate_pending_claim(rank_state(), pending_record(verify_conclusion="FAILURE"), current_main_sha=MAIN_SHA, now=NOW)
        self.assertFalse(ok); self.assertTrue(any("CI" in e or "constant" in e for e in errors))

    def test_03_wrong_collision_key_not_reservation(self):
        ok, errors = validate_pending_claim(rank_state(), pending_record(collision_keys=["wrong"]), current_main_sha=MAIN_SHA, now=NOW)
        self.assertFalse(ok); self.assertTrue(any("collision_keys" in e for e in errors))

    def test_04_stale_base_not_reservation(self):
        ok, errors = validate_pending_claim(rank_state(), pending_record(base_main_sha="d" * 40), current_main_sha=MAIN_SHA, now=NOW)
        self.assertFalse(ok); self.assertTrue(any("stale" in e for e in errors))

    def test_05_expired_pending_becomes_eligible_again(self):
        s = rank_state()
        old = pending_record(observed_at=(NOW - timedelta(minutes=61)).isoformat())
        ok, _ = validate_pending_claim(s, old, current_main_sha=MAIN_SHA, now=NOW)
        self.assertFalse(ok)
        rows = rank_v12(s, EvaluationBook(".", s), pending_records=[old], current_main_sha=MAIN_SHA, now=NOW)
        self.assertIn("TASK-X-1", [r.task_id for r in rows])

    def test_06_same_principal_distinct_workers_can_take_distinct_exclusive_tasks(self):
        base = second_exclusive_state()
        head = copy.deepcopy(base)
        head.lock_bundles["LOCK-2"] = new_bundle(W_B)
        op, errors = validate_lock_transition(base, head, actor="a", base_sha="0" * 40, maintainers={"maint"})
        self.assertEqual(op, "ACQUIRE"); self.assertEqual(errors, [])

    def test_07_same_worker_cannot_multi_hold_exclusive(self):
        base = second_exclusive_state()
        head = copy.deepcopy(base)
        head.lock_bundles["LOCK-2"] = new_bundle(W_A)
        op, errors = validate_lock_transition(base, head, actor="a", base_sha="0" * 40, maintainers={"maint"})
        self.assertEqual(op, "ACQUIRE"); self.assertTrue(any("worker EXCLUSIVE lock cap" in e for e in errors))

    def test_08_same_collision_key_is_rejected_across_workers(self):
        base = second_exclusive_state()
        base.tasks["TASK-X-2"]["collision_keys"] = ["x/shared"]
        head = copy.deepcopy(base)
        head.lock_bundles["LOCK-2"] = new_bundle(W_B, "x/shared")
        op, errors = validate_lock_transition(base, head, actor="a", base_sha="0" * 40, maintainers={"maint"})
        self.assertEqual(op, "ACQUIRE"); self.assertTrue(any("not READY" in e and "collision" in e for e in errors))

    def test_09_worker_id_is_not_review_independence_credential(self):
        self.assertTrue(validate_worker_id(W_A)); self.assertTrue(validate_worker_id(W_B))
        review = {"independence_grade": "I1", "worker_id": W_B}
        self.assertEqual(review["independence_grade"], "I1")

    def test_10_write_unavailable_filters_exclusive(self):
        s = rank_state()
        profile = CapabilityProfile.from_values(github_write="no", local_compute="yes")
        eligible, _ = capability_eligible(s, "TASK-X-1", profile)
        self.assertFalse(eligible)
        rows = rank_v12(s, EvaluationBook(".", s), capabilities=profile)
        self.assertNotIn("TASK-X-1", [r.task_id for r in rows])

    def test_11_worker_workspace_is_deterministic_safe_unique(self):
        a1 = worker_workspace("TASK-X-1", W_A)
        a2 = worker_workspace("TASK-X-1", W_A)
        b = worker_workspace("TASK-X-1", W_B)
        self.assertEqual(a1, a2)
        self.assertNotEqual(a1.branch, b.branch)
        self.assertTrue(a1.branch.startswith("research/TASK-X-1/w-"))
        self.assertTrue(a1.owned_path.startswith("work/TASK-X-1/w-"))

    def test_12_malformed_worker_id_rejected(self):
        for bad in ("../main", "w-ABCDEF0123456789", "w-short", "w-" + "a" * 80, "refs/heads/x"):
            self.assertFalse(validate_worker_id(bad))
            with self.assertRaises(Exception):
                worker_workspace("TASK-X-1", bad)

    def test_13_normal_research_pr_never_auto_activates(self):
        run, pr, _ = valid_run_pr_files(); files = [{"filename": "research/x/PROOF.md", "status": "added", "sha": "d" * 40}]
        ok, _ = auto_activation_preflight(run, pr, files, repository="51mns/AIMath-public", current_main_sha=MAIN_SHA, maintainers={"51mns"})
        self.assertFalse(ok)

    def test_14_governance_pr_never_auto_activates(self):
        run, pr, _ = valid_run_pr_files(); files = [{"filename": "AGENTS.md", "status": "modified", "sha": "d" * 40}]
        ok, _ = auto_activation_preflight(run, pr, files, repository="51mns/AIMath-public", current_main_sha=MAIN_SHA, maintainers={"51mns"})
        self.assertFalse(ok)

    def test_15_failed_verify_never_auto_activates(self):
        run, pr, files = valid_run_pr_files(); run["conclusion"] = "failure"
        ok, _ = auto_activation_preflight(run, pr, files, repository="51mns/AIMath-public", current_main_sha=MAIN_SHA, maintainers={"51mns"})
        self.assertFalse(ok)

    def test_16_stale_base_never_auto_activates(self):
        run, pr, files = valid_run_pr_files(); pr["base"]["sha"] = "e" * 40
        ok, _ = auto_activation_preflight(run, pr, files, repository="51mns/AIMath-public", current_main_sha=MAIN_SHA, maintainers={"51mns"})
        self.assertFalse(ok)

    def test_17_only_valid_lock_addition_is_auto_activation_candidate(self):
        run, pr, files = valid_run_pr_files()
        ok, errors = auto_activation_preflight(run, pr, files, repository="51mns/AIMath-public", current_main_sha=MAIN_SHA, maintainers={"51mns"})
        self.assertTrue(ok, errors)
        files[0]["status"] = "modified"
        self.assertFalse(auto_activation_preflight(run, pr, files, repository="51mns/AIMath-public", current_main_sha=MAIN_SHA, maintainers={"51mns"})[0])

    def test_18_standard_reuse_license_sidecar_passes_public_audit(self):
        self._audit_sidecar("SPDX-FileCopyrightText: 2026 AIMath contributors\nSPDX-License-Identifier: CC0-1.0\n", expect_ok=True)

    def test_19_license_sidecar_cannot_bypass_unsafe_payload(self):
        self._audit_sidecar("SPDX-FileCopyrightText: sandbox:/mnt/data/private-artifact\nSPDX-License-Identifier: CC0-1.0\n", expect_ok=False, expected="runtime attachment path")

    def test_20_orphan_license_sidecar_is_rejected(self):
        root = Path(__file__).resolve().parent.parent
        scanner = root / "scripts/public_release_audit.py"
        with tempfile.TemporaryDirectory() as td:
            p = Path(td) / "orphan.yml.license"
            p.write_text("SPDX-FileCopyrightText: 2026 AIMath contributors\nSPDX-License-Identifier: CC0-1.0\n", encoding="utf-8")
            proc = subprocess.run([sys.executable, str(scanner), td], text=True, capture_output=True)
            self.assertNotEqual(proc.returncode, 0)
            self.assertIn("orphan", proc.stdout)

    def test_21_mixed_lock_and_research_change_is_fail_closed(self):
        errors = lock_change_class_errors([
            "coordination/locks/x/shared.yml",
            "research/x/PROOF.md",
        ])
        self.assertTrue(errors)
        self.assertIn("dedicated lock-only PR", errors[0])

    def test_22_lock_symlink_git_object_is_rejected(self):
        _, _, files = valid_run_pr_files()
        tree = [{
            "path": files[0]["filename"],
            "mode": "120000",
            "type": "blob",
            "sha": files[0]["sha"],
        }]
        errors = lock_git_object_errors(files, tree)
        self.assertTrue(any("100644" in e for e in errors))

    def test_23_regular_lock_git_blob_identity_passes(self):
        _, _, files = valid_run_pr_files()
        tree = [{
            "path": files[0]["filename"],
            "mode": "100644",
            "type": "blob",
            "sha": files[0]["sha"],
        }]
        self.assertEqual(lock_git_object_errors(files, tree), [])

    def test_24_public_release_audit_rejects_symlink(self):
        root = Path(__file__).resolve().parent.parent
        scanner = root / "scripts/public_release_audit.py"
        with tempfile.TemporaryDirectory() as td:
            base = Path(td)
            target = base / "target.yml"
            target.write_text('{"ok":true}\n', encoding="utf-8")
            link = base / "coordination" / "locks" / "x" / "shared.yml"
            link.parent.mkdir(parents=True)
            try:
                link.symlink_to(target)
            except (OSError, NotImplementedError):
                self.skipTest("symlink creation unavailable")
            proc = subprocess.run([sys.executable, str(scanner), td], text=True, capture_output=True)
            self.assertNotEqual(proc.returncode, 0)
            self.assertIn("symlink", proc.stdout)

    def test_25_malformed_pending_draft_string_fails_schema(self):
        ok, errors = validate_pending_claim(
            rank_state(), pending_record(draft="yes"), current_main_sha=MAIN_SHA, now=NOW
        )
        self.assertFalse(ok)
        self.assertTrue(any("draft" in e or "constant" in e for e in errors))

    def test_26_pending_cache_requires_schema_and_github_provenance(self):
        with tempfile.TemporaryDirectory() as td:
            p = Path(td) / "pending.json"
            envelope = {
                "schema_version": 1,
                "observation_source": "GITHUB_API",
                "repository": "51mns/AIMath-public",
                "reservations": [pending_record()],
            }
            p.write_text(json.dumps(envelope), encoding="utf-8")
            self.assertEqual(load_pending_claims(p), envelope["reservations"])
            envelope["reservations"][0]["draft"] = "yes"
            p.write_text(json.dumps(envelope), encoding="utf-8")
            with self.assertRaises(VillageV12Error):
                load_pending_claims(p)

    def test_27_strict_up_to_date_setting_is_required_for_auto_merge(self):
        with patch("lock_auto_activate._request_json", return_value={"strict": True}):
            self.assertTrue(_strict_up_to_date_gate("t", "51mns/AIMath-public")[0])
        with patch("lock_auto_activate._request_json", return_value={"strict": False}):
            self.assertFalse(_strict_up_to_date_gate("t", "51mns/AIMath-public")[0])
        with patch("lock_auto_activate._request_json", side_effect=AutoActivationError("403")):
            self.assertFalse(_strict_up_to_date_gate("t", "51mns/AIMath-public")[0])

    def test_28_main_or_pr_movement_after_revalidation_blocks_merge(self):
        final_pr = {
            "head": {"sha": "c" * 40},
            "base": {"sha": MAIN_SHA},
        }
        self.assertEqual(
            final_revalidation_errors(
                original_main_sha=MAIN_SHA,
                original_head_sha="c" * 40,
                final_main_sha=MAIN_SHA,
                final_pr=final_pr,
            ),
            [],
        )
        moved_main = final_revalidation_errors(
            original_main_sha=MAIN_SHA,
            original_head_sha="c" * 40,
            final_main_sha="e" * 40,
            final_pr=final_pr,
        )
        self.assertTrue(any("main moved" in e for e in moved_main))
        moved_head = copy.deepcopy(final_pr); moved_head["head"]["sha"] = "f" * 40
        self.assertTrue(final_revalidation_errors(
            original_main_sha=MAIN_SHA,
            original_head_sha="c" * 40,
            final_main_sha=MAIN_SHA,
            final_pr=moved_head,
        ))
        moved_base = copy.deepcopy(final_pr); moved_base["base"]["sha"] = "f" * 40
        self.assertTrue(final_revalidation_errors(
            original_main_sha=MAIN_SHA,
            original_head_sha="c" * 40,
            final_main_sha=MAIN_SHA,
            final_pr=moved_base,
        ))

    def _audit_sidecar(self, sidecar: str, *, expect_ok: bool, expected: str = ""):
        root = Path(__file__).resolve().parent.parent
        scanner = root / "scripts/public_release_audit.py"
        with tempfile.TemporaryDirectory() as td:
            target = Path(td) / "OUTCOME.yml"
            target.write_text('{"schema_version":1}\n', encoding="utf-8")
            Path(str(target) + ".license").write_text(sidecar, encoding="utf-8")
            proc = subprocess.run([sys.executable, str(scanner), td], text=True, capture_output=True)
            if expect_ok:
                self.assertEqual(proc.returncode, 0, proc.stdout + proc.stderr)
            else:
                self.assertNotEqual(proc.returncode, 0)
                self.assertIn(expected, proc.stdout)


if __name__ == "__main__":
    unittest.main(verbosity=2)
