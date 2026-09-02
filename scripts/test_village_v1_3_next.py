#!/usr/bin/env python3
# SPDX-FileCopyrightText: 2026 AIMath contributors
# SPDX-License-Identifier: Apache-2.0
from __future__ import annotations

from pathlib import Path
import copy
import json
import tempfile
import unittest
from unittest.mock import patch

from test_village_acceptance import NOW, add_lock
from test_village_v1_1 import evaluation, rank_state
from test_village_v1_2 import MAIN_SHA, pending_record
from village_rank import EvaluationBook
from village_v1_2 import CapabilityProfile
import village_next
from village_next import (
    AUTOMATIC_LIFECYCLE_OPERATIONS,
    CANONICAL_MUTATIONS,
    TRUTH_PROMOTIONS,
    NextPhase,
    NextRequest,
    NextStatus,
    RequiredAction,
    canonical_evaluation_followups,
    derive_next_state,
    recognize_terminal_evidence,
    select_next_task,
)

W_A = "w-" + "a" * 16
W_B = "w-" + "b" * 16
PRINCIPAL = "gh:51mns"


def _write_schemas(root: Path) -> None:
    repo = Path(__file__).resolve().parent.parent
    target = root / "schemas"
    target.mkdir(parents=True, exist_ok=True)
    for name in ("outcome.schema.json", "abandoned-terminal.schema.json", "pending-claim.schema.json"):
        (target / name).write_text((repo / "schemas" / name).read_text(encoding="utf-8"), encoding="utf-8")


def _write_outcome(root: Path, outcome_type: str, *, review_required=False, malformed=False) -> Path:
    path = root / "coordination/outcomes/TASK-X-1.yml"
    path.parent.mkdir(parents=True, exist_ok=True)
    if malformed:
        value = {"schema_version": 1, "task_id": "TASK-X-1", "summary": "malformed", "artifacts": []}
    else:
        value = {
            "schema_version": 1,
            "task_id": "TASK-X-1",
            "outcome_type": outcome_type,
            "summary": f"terminal {outcome_type}",
            "artifacts": [],
            "review_required": review_required,
        }
    path.write_text(json.dumps(value) + "\n", encoding="utf-8")
    return path


def _write_abandoned(root: Path, *, worker=W_A, truth="NONE") -> Path:
    path = root / f"work/TASK-X-1/{worker}/ABANDONED_TERMINAL.yml"
    path.parent.mkdir(parents=True, exist_ok=True)
    value = {
        "schema_version": 1,
        "task_id": "TASK-X-1",
        "worker_id": worker,
        "reason": "NO_REUSABLE_PROGRESS",
        "abandoned_at": NOW.isoformat(),
        "abandonment_count": 1,
        "last_work_head": None,
        "truth_layer_effect": truth,
    }
    path.write_text(json.dumps(value) + "\n", encoding="utf-8")
    return path


def _book(state) -> EvaluationBook:
    book = EvaluationBook(".", state)
    book.records = []
    book.errors = []
    return book


def _state(root: Path, *, source_lock=False, source_worker=W_A, source_actor=PRINCIPAL):
    state = rank_state()
    state.root = root.resolve()
    state.now = NOW
    state.errors = []
    state.decisions = []
    if source_lock:
        add_lock(state, "LOCK-SOURCE", "TASK-X-1", "x/shared", actor=source_actor)
        bundle = state.lock_bundles["LOCK-SOURCE"]
        bundle.payload["worker_id"] = source_worker
        bundle.payload["work_ref"] = f"research/TASK-X-1/{source_worker}"
    return state


def _add_same_campaign_task(state, task_id="TASK-X-2", *, stored_state="APPROVED"):
    state.tasks[task_id] = {
        **state.tasks["TASK-X-1"],
        "task_id": task_id,
        "stored_state": stored_state,
        "collision_keys": [f"x/{task_id.lower()}"],
        "owned_paths": [f"work/{task_id.lower()}/**"],
        "route_id": "route-a",
    }
    return task_id


def _add_global_task(state, task_id="TASK-Y-1"):
    state.campaigns["CAM-Y"] = {
        **state.campaigns["CAM-X"],
        "campaign_id": "CAM-Y",
        "strategic_state": "ACTIVE",
        "priority": "P1",
        "max_active_lanes": 2,
        "assets": [],
    }
    state.tasks[task_id] = {
        **state.tasks["TASK-X-1"],
        "task_id": task_id,
        "campaign_id": "CAM-Y",
        "collision_keys": ["y/1"],
        "owned_paths": ["work/y1/**"],
    }
    return task_id


def _request(**overrides) -> NextRequest:
    value = dict(
        task_id="TASK-X-1",
        worker_id=W_A,
        principal_id=PRINCIPAL,
        capabilities=CapabilityProfile.from_values(github_write="yes", local_compute="yes"),
        current_main_sha=MAIN_SHA,
    )
    value.update(overrides)
    return NextRequest(**value)


class VillageV13NextPhaseA(unittest.TestCase):
    def test_01_active_exact_worker_without_terminal_is_active_work(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td); _write_schemas(root)
            state = _state(root, source_lock=True)
            got = derive_next_state(state, _book(state), _request())
            self.assertEqual(got.phase, NextPhase.ACTIVE_WORK)
            self.assertEqual(got.status, NextStatus.ACTIVE_WORK)
            self.assertTrue(got.canonical_ownership)
            self.assertEqual(got.required_action, RequiredAction.NONE)

    def test_02_result_terminal_preserves_exact_outcome_type(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td); _write_schemas(root); _write_outcome(root, "CLAIM_CANDIDATE")
            state = _state(root, source_lock=True)
            evidence, errors = recognize_terminal_evidence(
                state, task_id="TASK-X-1", worker_id=W_A,
                lock_payload=state.lock_bundles["LOCK-SOURCE"].payload,
            )
            self.assertEqual(errors, ())
            self.assertEqual(evidence.outcome_type, "CLAIM_CANDIDATE")
            self.assertEqual(evidence.terminal_class, "RESULT_TERMINAL")

    def test_03_abandoned_terminal_is_truth_neutral(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td); _write_schemas(root); _write_abandoned(root)
            state = _state(root, source_lock=True)
            got = derive_next_state(state, _book(state), _request())
            self.assertEqual(got.phase, NextPhase.RELEASE_PENDING)
            self.assertEqual(got.terminal.terminal_class, "ABANDONED_TERMINAL")
            self.assertIsNone(got.terminal.outcome_type)
            self.assertEqual(got.terminal.truth_layer_effect, "NONE")

    def test_04_malformed_outcome_fails_closed(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td); _write_schemas(root); _write_outcome(root, "INCONCLUSIVE", malformed=True)
            state = _state(root, source_lock=True)
            got = derive_next_state(state, _book(state), _request())
            self.assertEqual(got.status, NextStatus.FAIL_CLOSED)
            self.assertEqual(got.phase, NextPhase.ACTIVE_WORK)
            self.assertNotEqual(got.required_action, RequiredAction.PREPARE_RELEASE)

    def test_05_malformed_result_can_only_fall_back_to_valid_abandonment(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td); _write_schemas(root); _write_outcome(root, "INCONCLUSIVE", malformed=True); _write_abandoned(root)
            state = _state(root, source_lock=True)
            got = derive_next_state(state, _book(state), _request())
            self.assertEqual(got.status, NextStatus.RELEASE_REQUIRED)
            self.assertEqual(got.terminal.terminal_class, "ABANDONED_TERMINAL")

    def test_06_branch_or_chat_only_result_cannot_terminalise(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td); _write_schemas(root)
            path = root / "work/TASK-X-1/w-a/RESULT.md"
            path.parent.mkdir(parents=True); path.write_text("chat says finished\n", encoding="utf-8")
            state = _state(root, source_lock=True)
            got = derive_next_state(state, _book(state), _request())
            self.assertEqual(got.status, NextStatus.ACTIVE_WORK)
            self.assertIsNone(got.terminal)

    def test_07_valid_terminal_plus_lock_derives_release_pending(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td); _write_schemas(root); _write_outcome(root, "STRUCTURAL_REDUCTION")
            state = _state(root, source_lock=True)
            got = derive_next_state(state, _book(state), _request())
            self.assertEqual(got.phase, NextPhase.RELEASE_PENDING)
            self.assertEqual(got.status, NextStatus.RELEASE_REQUIRED)
            self.assertEqual(got.required_action, RequiredAction.PREPARE_RELEASE)
            self.assertIn(NextPhase.RESULT_RECORDED, got.trace)
            self.assertIn(NextPhase.CONTINUATION_DECISION, got.trace)

    def test_08_canonical_absence_of_old_lock_permits_next_selection(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td); _write_schemas(root); _write_outcome(root, "NO_REUSABLE_PROGRESS")
            state = _state(root); _add_same_campaign_task(state)
            got = derive_next_state(state, _book(state), _request())
            self.assertEqual(got.phase, NextPhase.ACQUIRE_PENDING)
            self.assertEqual(got.selected_task_id, "TASK-X-2")
            self.assertIn(NextPhase.RELEASED, got.trace)
            self.assertIn(NextPhase.NEXT_SELECTION, got.trace)
            self.assertFalse(got.canonical_ownership)

    def test_09_missing_required_human_continuation_gate_waits_when_only_same_campaign_remains(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td); _write_schemas(root); _write_outcome(root, "STRUCTURAL_REDUCTION")
            state = _state(root); _add_same_campaign_task(state)
            got = derive_next_state(state, _book(state), _request(continuation_gate_required=True))
            self.assertEqual(got.status, NextStatus.WAITING_PORTFOLIO)
            self.assertIsNone(got.selected_task_id)
            self.assertFalse(got.continuation.same_campaign_allowed)

    def test_09b_major_outcome_cannot_bypass_human_gate_by_omitting_flag(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td); _write_schemas(root); _write_outcome(root, "COUNTEREXAMPLE")
            state = _state(root); _add_same_campaign_task(state)
            got = derive_next_state(state, _book(state), _request())
            self.assertEqual(got.status, NextStatus.WAITING_PORTFOLIO)
            self.assertFalse(got.continuation.same_campaign_allowed)
            self.assertTrue(any("Continuation Gate" in reason for reason in got.continuation.reasons))

    def test_10_canonical_human_continue_can_unlock_existing_approved_followup(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td); _write_schemas(root); _write_outcome(root, "STRUCTURAL_REDUCTION")
            state = _state(root); _add_same_campaign_task(state)
            state.decisions.append({
                "schema_version": 1, "campaign_id": "CAM-X", "decision_id": "DEC-NEXT",
                "decided_at": NOW.isoformat(), "decision": "CONTINUE",
                "authority": "HUMAN_MAINTAINER", "reason": "approved bounded successor",
            })
            got = derive_next_state(
                state, _book(state),
                _request(continuation_gate_required=True, continuation_decision_id="DEC-NEXT"),
            )
            self.assertEqual(got.status, NextStatus.ACQUIRE_REQUIRED)
            self.assertEqual(got.selected_task_id, "TASK-X-2")

    def test_11_no_eligible_approved_or_global_task_returns_no_eligible(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td); _write_schemas(root); _write_outcome(root, "NO_REUSABLE_PROGRESS")
            state = _state(root)
            got = derive_next_state(state, _book(state), _request())
            self.assertEqual(got.status, NextStatus.NO_ELIGIBLE_TASK)
            self.assertEqual(got.phase, NextPhase.NEXT_SELECTION)
            self.assertEqual(got.required_action, RequiredAction.NONE)

    def test_12_no_same_campaign_followup_falls_back_to_ordinary_global_ready(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td); _write_schemas(root); _write_outcome(root, "NO_REUSABLE_PROGRESS")
            state = _state(root); _add_global_task(state)
            got = derive_next_state(state, _book(state), _request())
            self.assertEqual(got.status, NextStatus.ACQUIRE_REQUIRED)
            self.assertEqual(got.selected_task_id, "TASK-Y-1")
            self.assertEqual(got.selected_relation, "GLOBAL_READY")

    def test_13_negative_outcome_preserved_and_can_release(self):
        for outcome in ("COUNTEREXAMPLE", "FAILED_ROUTE", "REPRODUCTION_FAILURE", "NO_REUSABLE_PROGRESS"):
            with self.subTest(outcome=outcome), tempfile.TemporaryDirectory() as td:
                root = Path(td); _write_schemas(root); _write_outcome(root, outcome)
                state = _state(root, source_lock=True)
                got = derive_next_state(state, _book(state), _request())
                self.assertEqual(got.status, NextStatus.RELEASE_REQUIRED)
                self.assertEqual(got.terminal.outcome_type, outcome)

    def test_14_inconclusive_is_not_rewritten(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td); _write_schemas(root); _write_outcome(root, "INCONCLUSIVE")
            state = _state(root, source_lock=True)
            got = derive_next_state(state, _book(state), _request())
            self.assertEqual(got.terminal.outcome_type, "INCONCLUSIVE")
            self.assertEqual(got.status, NextStatus.RELEASE_REQUIRED)

    def test_15_review_demand_does_not_keep_writer_ownership_alive(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td); _write_schemas(root); _write_outcome(root, "CLAIM_CANDIDATE", review_required=True)
            state = _state(root, source_lock=True)
            got = derive_next_state(state, _book(state), _request())
            self.assertTrue(got.continuation.review_demand)
            self.assertEqual(got.phase, NextPhase.RELEASE_PENDING)
            self.assertEqual(got.required_action, RequiredAction.PREPARE_RELEASE)

    def test_16_self_evaluation_cannot_create_or_unblock_candidate(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td); _write_schemas(root); _write_outcome(root, "NO_REUSABLE_PROGRESS")
            state = _state(root); _add_same_campaign_task(state, stored_state="RETIRED")
            book = _book(state)
            book.records = [evaluation("EVAL-SELF-NEXT", role="SELF_ASSESSMENT", targets=("TASK-X-2",))]
            self.assertEqual(canonical_evaluation_followups(book, "TASK-X-1"), ())
            got = derive_next_state(state, book, _request())
            self.assertEqual(got.status, NextStatus.NO_ELIGIBLE_TASK)

    def test_17_rank_is_deterministic_and_task_id_breaks_final_tie(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td); _write_schemas(root); _write_outcome(root, "NO_REUSABLE_PROGRESS")
            state = _state(root)
            _add_same_campaign_task(state, "TASK-X-A")
            _add_same_campaign_task(state, "TASK-X-B")
            book = _book(state)
            terminal, _ = recognize_terminal_evidence(state, task_id="TASK-X-1", worker_id=W_A)
            continuation = village_next.derive_continuation_decision(state, book, _request(), terminal)
            a = select_next_task(state, book, _request(), continuation)
            b = select_next_task(state, book, _request(), continuation)
            self.assertEqual(a, b)
            self.assertEqual(a.selected_task_id, "TASK-X-A")
            self.assertEqual(a.ranked_task_ids[:2], ("TASK-X-A", "TASK-X-B"))

    def test_18_rank_failure_has_no_fallback_selection(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td); _write_schemas(root); _write_outcome(root, "NO_REUSABLE_PROGRESS")
            state = _state(root); _add_same_campaign_task(state)
            with patch("village_next.rank_v12", side_effect=RuntimeError("rank exploded")):
                got = derive_next_state(state, _book(state), _request())
            self.assertEqual(got.status, NextStatus.RANK_FAILED)
            self.assertIsNone(got.selected_task_id)
            self.assertEqual(got.required_action, RequiredAction.NONE)

    def test_19_pending_transport_never_becomes_canonical_ownership(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td); _write_schemas(root); _write_outcome(root, "NO_REUSABLE_PROGRESS")
            state = _state(root); _add_same_campaign_task(state)
            pending = pending_record(
                task_id="TASK-X-2",
                collision_keys=state.tasks["TASK-X-2"]["collision_keys"],
                principal_id=PRINCIPAL,
                worker_id=W_A,
            )
            got = derive_next_state(state, _book(state), _request(pending_records=(pending,)))
            self.assertNotEqual(got.status, NextStatus.ACTIVE_NEXT)
            self.assertFalse(got.canonical_ownership)

    def test_20_active_next_requires_actual_canonical_active_lock(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td); _write_schemas(root); _write_outcome(root, "NO_REUSABLE_PROGRESS")
            state = _state(root); _add_same_campaign_task(state)
            add_lock(state, "LOCK-NEXT", "TASK-X-2", state.tasks["TASK-X-2"]["collision_keys"][0], actor=PRINCIPAL)
            bundle = state.lock_bundles["LOCK-NEXT"]
            bundle.payload["worker_id"] = W_A
            bundle.payload["work_ref"] = f"research/TASK-X-2/{W_A}"
            got = derive_next_state(state, _book(state), _request())
            self.assertEqual(got.phase, NextPhase.ACTIVE_NEXT)
            self.assertEqual(got.status, NextStatus.ACTIVE_NEXT)
            self.assertTrue(got.canonical_ownership)
            self.assertEqual(got.selected_task_id, "TASK-X-2")

    def test_21_worker_or_principal_spoof_fails_closed(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td); _write_schemas(root)
            state = _state(root, source_lock=True, source_actor="gh:other")
            got = derive_next_state(state, _book(state), _request())
            self.assertEqual(got.status, NextStatus.FAIL_CLOSED)
            self.assertTrue(any("principal" in e for e in got.errors))
        with tempfile.TemporaryDirectory() as td:
            root = Path(td); _write_schemas(root)
            state = _state(root, source_lock=True, source_worker=W_A)
            got = derive_next_state(state, _book(state), _request(worker_id=W_B))
            self.assertEqual(got.status, NextStatus.FAIL_CLOSED)
            self.assertTrue(any("worker" in e for e in got.errors))

    def test_22_global_pause_blocks_selection_but_not_terminal_release(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td); _write_schemas(root); _write_outcome(root, "NO_REUSABLE_PROGRESS")
            state = _state(root, source_lock=True); state.portfolio["global_admission"] = "PAUSED"
            got = derive_next_state(state, _book(state), _request())
            self.assertEqual(got.status, NextStatus.RELEASE_REQUIRED)
            self.assertTrue(got.continuation.waiting_portfolio)
        with tempfile.TemporaryDirectory() as td:
            root = Path(td); _write_schemas(root); _write_outcome(root, "NO_REUSABLE_PROGRESS")
            state = _state(root); state.portfolio["global_admission"] = "PAUSED"; _add_global_task(state)
            got = derive_next_state(state, _book(state), _request())
            self.assertEqual(got.status, NextStatus.WAITING_PORTFOLIO)
            self.assertIsNone(got.selected_task_id)

    def test_23_independent_evaluation_is_visibility_signal_not_task_creation(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td); _write_schemas(root); _write_outcome(root, "NO_REUSABLE_PROGRESS")
            state = _state(root); _add_same_campaign_task(state)
            book = _book(state)
            book.records = [evaluation("EVAL-I-NEXT", tid="TASK-X-1", role="INDEPENDENT_EVALUATION", targets=("TASK-X-2",))]
            got = derive_next_state(state, book, _request())
            self.assertEqual(got.continuation.evaluation_followup_task_ids, ("TASK-X-2",))
            self.assertEqual(got.selected_task_id, "TASK-X-2")
            self.assertNotIn("TASK-IMAGINED", state.tasks)

    def test_24_no_truth_promotion_or_renew_takeover_authority_exists(self):
        self.assertEqual(CANONICAL_MUTATIONS, frozenset())
        self.assertEqual(TRUTH_PROMOTIONS, frozenset())
        self.assertEqual(AUTOMATIC_LIFECYCLE_OPERATIONS, frozenset())
        self.assertNotIn("RENEW", AUTOMATIC_LIFECYCLE_OPERATIONS)
        self.assertNotIn("TAKEOVER", AUTOMATIC_LIFECYCLE_OPERATIONS)

    def test_25_pure_core_performs_no_filesystem_or_network_mutation(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td); _write_schemas(root); _write_outcome(root, "NO_REUSABLE_PROGRESS")
            state = _state(root); _add_same_campaign_task(state)
            before = {p.relative_to(root).as_posix(): p.read_bytes() for p in root.rglob("*") if p.is_file()}
            got = derive_next_state(state, _book(state), _request())
            after = {p.relative_to(root).as_posix(): p.read_bytes() for p in root.rglob("*") if p.is_file()}
            self.assertEqual(before, after)
            self.assertEqual(got.required_action, RequiredAction.PREPARE_ACQUIRE)
            source = Path(village_next.__file__).read_text(encoding="utf-8")
            for forbidden in ("urllib", "requests", "subprocess", "socket", "api.github.com", '"POST"', "/git/refs"):
                self.assertNotIn(forbidden, source)

    def test_26_repository_wide_observation_failure_is_global_fail_closed(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td); _write_schemas(root); _write_outcome(root, "NO_REUSABLE_PROGRESS")
            state = _state(root); _add_same_campaign_task(state)
            got = derive_next_state(state, _book(state), _request(fresh_observation_valid=False))
            self.assertEqual(got.status, NextStatus.RANK_FAILED)
            self.assertIsNone(got.selected_task_id)


if __name__ == "__main__":
    unittest.main(verbosity=2)
