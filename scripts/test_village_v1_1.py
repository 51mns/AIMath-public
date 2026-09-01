#!/usr/bin/env python3
# SPDX-FileCopyrightText: 2026 AIMath contributors
# SPDX-License-Identifier: Apache-2.0
from __future__ import annotations

from pathlib import Path
from datetime import timedelta
import copy
import json
import tempfile
import unittest

from test_village_acceptance import NOW, add_lock, base_state
from village_rank import (
    EvaluationBook,
    discovery_policy_errors,
    rank_ready_tasks,
    research_class_for_task,
)


def allocation_policy():
    return {
        "mode": "ADAPTIVE_DIVERSITY",
        "class_weights": {
            "EXTERNAL_OPEN_PROBLEM": 5,
            "DERIVED_GENERAL_MATH": 3,
            "OPEN_MATH_DISCOVERY": 3,
            "AI_NATIVE_MATH": 3,
            "QUALITY_KNOWLEDGE": 2,
            "PLATFORM": 1,
        },
        "soft_class_caps_pct": {
            "EXTERNAL_OPEN_PROBLEM": 60,
            "DERIVED_GENERAL_MATH": 40,
            "OPEN_MATH_DISCOVERY": 40,
            "AI_NATIVE_MATH": 40,
            "QUALITY_KNOWLEDGE": 30,
            "PLATFORM": 20,
        },
        "evaluation_bonus_cap": 12,
    }


def rank_state():
    s = base_state()
    s.portfolio["allocation_policy"] = allocation_policy()
    s.campaigns["CAM-X"].update(
        {
            "priority": "P1",
            "kind": "EXTERNAL_OPEN_PROBLEM",
            "research_class": "EXTERNAL_OPEN_PROBLEM",
        }
    )
    s.tasks["TASK-X-1"].update({"created_at": "2026-09-01"})
    s.tasks["TASK-SOURCE"] = {
        **s.tasks["TASK-X-1"],
        "task_id": "TASK-SOURCE",
        "collision_keys": ["source"],
        "owned_paths": ["work/source/**"],
    }
    s.outcomes["TASK-SOURCE"] = {
        "schema_version": 1,
        "task_id": "TASK-SOURCE",
        "outcome_type": "STRUCTURAL_REDUCTION",
        "summary": "completed source task",
        "artifacts": [],
        "review_required": False,
    }
    return s


def evaluation(
    eid,
    tid="TASK-SOURCE",
    role="INDEPENDENT_EVALUATION",
    actor="gh:evaluator",
    *,
    targets=("TASK-X-1",),
    followup=5,
    surprise=5,
    uncertainty=0,
    confidence="HIGH",
    recommendation="CONTINUE",
):
    return {
        "schema_version": 1,
        "evaluation_id": eid,
        "task_id": tid,
        "evaluation_role": role,
        "evaluator": {"actor_id": actor},
        "scores": {
            "information_gain": 5,
            "mathematical_reusability": 5,
            "transfer_potential": 5,
            "external_relevance": 5,
            "followup_expected_value": followup,
            "surprise": surprise,
            "uncertainty": uncertainty,
        },
        "confidence": confidence,
        "recommendation": recommendation,
        "followup_task_ids": list(targets),
        "rationale": "bounded test evaluation",
        "truth_layer_effect": "NONE",
    }


class VillageV11Acceptance(unittest.TestCase):
    def test_AA_rank_contains_runtime_READY_only(self):
        s = rank_state()
        book = EvaluationBook(".", s)
        self.assertEqual([r.task_id for r in rank_ready_tasks(s, book)], ["TASK-X-1"])
        self.assertEqual(s.runtime_state("TASK-SOURCE"), "DONE")
        self.assertNotIn("TASK-SOURCE", [r.task_id for r in rank_ready_tasks(s, book)])
        s.campaigns["CAM-X"]["strategic_state"] = "HOLD"
        s.campaigns["CAM-X"]["priority"] = "HOLD"
        book.records = [evaluation("EVAL-HIGH")]
        self.assertEqual(rank_ready_tasks(s, book), [])

    def test_AB_self_assessment_has_zero_allocation_bonus(self):
        s = rank_state()
        book = EvaluationBook(".", s)
        book.records = [evaluation("EVAL-SELF", role="SELF_ASSESSMENT")]
        row = rank_ready_tasks(s, book)[0]
        self.assertEqual(row.evaluation_bonus, 0)
        self.assertEqual(row.self_evaluations, 1)
        self.assertEqual(row.eligible_evaluations, 0)

    def test_AC_independent_evaluation_is_bounded(self):
        s = rank_state()
        book = EvaluationBook(".", s)
        book.records = [evaluation("EVAL-I")]
        row = rank_ready_tasks(s, book)[0]
        self.assertEqual(row.evaluation_bonus, 12)
        self.assertLessEqual(row.score, 99)

    def test_AD_priority_band_cannot_be_crossed_by_scores(self):
        s = rank_state()
        s.campaigns["CAM-P0"] = {
            "campaign_id": "CAM-P0",
            "strategic_state": "ACTIVE",
            "max_active_lanes": 2,
            "assets": [],
            "priority": "P0",
            "kind": "SOFTWARE_RESEARCH",
            "research_class": "PLATFORM",
        }
        s.tasks["TASK-P0"] = {
            **s.tasks["TASK-X-1"],
            "task_id": "TASK-P0",
            "campaign_id": "CAM-P0",
            "collision_keys": ["p0"],
            "owned_paths": ["work/p0/**"],
        }
        book = EvaluationBook(".", s)
        book.records = [evaluation("EVAL-P1")]
        rows = rank_ready_tasks(s, book)
        self.assertEqual(rows[0].task_id, "TASK-P0")
        self.assertGreater(rows[0].score, rows[1].score)

    def test_AE_evaluation_count_is_not_additive_popularity(self):
        s = rank_state()
        one = EvaluationBook(".", s)
        one.records = [evaluation("EVAL-1", actor="gh:a")]
        many = EvaluationBook(".", s)
        many.records = [
            evaluation("EVAL-1", actor="gh:a"),
            evaluation("EVAL-2", actor="gh:b"),
            evaluation("EVAL-3", actor="gh:c"),
        ]
        self.assertEqual(one.allocation_bonus("TASK-X-1", 12), many.allocation_bonus("TASK-X-1", 12))

    def test_AF_diversity_favors_less_saturated_class_within_band(self):
        s = rank_state()
        s.campaigns["CAM-Y"] = {
            "campaign_id": "CAM-Y",
            "strategic_state": "ACTIVE",
            "max_active_lanes": 2,
            "assets": [],
            "priority": "P1",
            "kind": "FOUNDATIONAL_RESEARCH",
            "research_class": "AI_NATIVE_MATH",
        }
        s.tasks["TASK-Y"] = {
            **s.tasks["TASK-X-1"],
            "task_id": "TASK-Y",
            "campaign_id": "CAM-Y",
            "collision_keys": ["y"],
            "owned_paths": ["work/y/**"],
        }
        s.tasks["TASK-X-ACTIVE"] = {
            **s.tasks["TASK-X-1"],
            "task_id": "TASK-X-ACTIVE",
            "collision_keys": ["x/active"],
            "owned_paths": ["work/xactive/**"],
        }
        add_lock(s, "LOCK-A", "TASK-X-ACTIVE", "x/active")
        rows = {r.task_id: r for r in rank_ready_tasks(s, EvaluationBook(".", s))}
        self.assertGreater(rows["TASK-Y"].diversity_bonus, rows["TASK-X-1"].diversity_bonus)

    def test_AG_legacy_class_fallback_and_quality_override(self):
        s = rank_state()
        del s.campaigns["CAM-X"]["research_class"]
        s.campaigns["CAM-X"]["kind"] = "FOUNDATIONAL_RESEARCH"
        self.assertEqual(research_class_for_task(s, "TASK-X-1"), "DERIVED_GENERAL_MATH")
        s.tasks["TASK-X-1"]["task_kind"] = "REPRODUCTION"
        self.assertEqual(research_class_for_task(s, "TASK-X-1"), "QUALITY_KNOWLEDGE")

    def test_AH_duplicate_evaluator_slot_is_rejected(self):
        s = rank_state()
        repo_root = Path(__file__).resolve().parent.parent
        schema_text = (repo_root / "schemas/evaluation.schema.json").read_text(encoding="utf-8")
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            (root / "schemas").mkdir()
            (root / "schemas/evaluation.schema.json").write_text(schema_text, encoding="utf-8")
            d = root / "coordination/evaluations"
            d.mkdir(parents=True)
            (d / "a.yml").write_text(json.dumps(evaluation("EVAL-A")), encoding="utf-8")
            (d / "b.yml").write_text(json.dumps(evaluation("EVAL-B")), encoding="utf-8")
            book = EvaluationBook(root, s).load()
            self.assertTrue(any("duplicate INDEPENDENT_EVALUATION" in e for e in book.errors))

    def test_AI_surprise_does_not_change_allocation_signal(self):
        s = rank_state()
        a = EvaluationBook(".", s)
        a.records = [evaluation("EVAL-A", surprise=0)]
        b = EvaluationBook(".", s)
        b.records = [evaluation("EVAL-B", surprise=5)]
        self.assertEqual(a.allocation_bonus("TASK-X-1", 12), b.allocation_bonus("TASK-X-1", 12))

    def test_AJ_evaluation_view_is_clock_independent(self):
        s1 = rank_state()
        b1 = EvaluationBook(".", s1)
        b1.records = [evaluation("EVAL-A")]
        s2 = copy.deepcopy(s1)
        s2.now = NOW + timedelta(days=500)
        b2 = EvaluationBook(".", s2)
        b2.records = copy.deepcopy(b1.records)
        self.assertEqual(b1.render(), b2.render())

    def test_AK_evaluation_requires_canonical_source_outcome(self):
        s = rank_state()
        repo_root = Path(__file__).resolve().parent.parent
        schema_text = (repo_root / "schemas/evaluation.schema.json").read_text(encoding="utf-8")
        del s.outcomes["TASK-SOURCE"]
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            (root / "schemas").mkdir()
            (root / "schemas/evaluation.schema.json").write_text(schema_text, encoding="utf-8")
            d = root / "coordination/evaluations"
            d.mkdir(parents=True)
            (d / "a.yml").write_text(json.dumps(evaluation("EVAL-A")), encoding="utf-8")
            book = EvaluationBook(root, s).load()
            self.assertTrue(any("no canonical outcome" in e for e in book.errors))

    def test_AL_evaluation_affects_only_explicit_followup_target(self):
        s = rank_state()
        s.tasks["TASK-X-2"] = {
            **s.tasks["TASK-X-1"],
            "task_id": "TASK-X-2",
            "collision_keys": ["x/2"],
            "owned_paths": ["work/x2/**"],
        }
        book = EvaluationBook(".", s)
        book.records = [evaluation("EVAL-A", targets=("TASK-X-1",))]
        rows = {r.task_id: r for r in rank_ready_tasks(s, book)}
        self.assertEqual(rows["TASK-X-1"].evaluation_bonus, 12)
        self.assertEqual(rows["TASK-X-2"].evaluation_bonus, 0)

    def test_AM_ai_native_guardrails_are_executable(self):
        s = rank_state()
        s.campaigns["CAM-ND"] = {
            "campaign_id": "CAM-ND",
            "strategic_state": "ACTIVE",
            "max_active_lanes": 2,
            "assets": [],
            "priority": "P1",
            "kind": "FOUNDATIONAL_RESEARCH",
            "research_class": "AI_NATIVE_MATH",
        }
        s.tasks["TASK-ND"] = {
            **s.tasks["TASK-X-1"],
            "task_id": "TASK-ND",
            "campaign_id": "CAM-ND",
            "collision_keys": ["nd"],
            "owned_paths": ["work/nd/**"],
            "research_mode": "AI_NATIVE_REPRESENTATION",
            "held_out_required": True,
            "toy_problem_gate": True,
            "transfer_test_required": False,
            "post_outcome_evaluation": "REQUIRED",
            "success_conditions": ["utility"],
            "stop_conditions": ["bounded stop"],
        }
        self.assertTrue(any("transfer_test_required=true" in e for e in discovery_policy_errors(s)))

    def test_AN_join_protocol_is_minimal_and_non_escalating(self):
        root = Path(__file__).resolve().parent.parent
        policy = json.loads((root / "coordination/policy/JOIN_PROTOCOL.yml").read_text(encoding="utf-8"))
        self.assertEqual(policy["command"], "/join")
        self.assertEqual(
            policy["minimal_invocation"],
            "https://github.com/51mns/AIMath-public /join",
        )
        self.assertIn("current public main", policy["meaning"])
        self.assertIn("select the highest-value eligible bounded task", policy["entry_sequence"])
        denied = " ".join(policy["does_not_grant"]).lower()
        for required_boundary in (
            "permissions",
            "branch protection",
            "merge",
            "promote",
            "destructive",
            "private-data",
        ):
            self.assertIn(required_boundary, denied)
        self.assertIn("not a privilege escalation", policy["write_boundary"]["authenticated_write_available"])

    def test_AO_join_is_user_scoped_and_advertised_consistently(self):
        root = Path(__file__).resolve().parent.parent
        texts = {
            rel: (root / rel).read_text(encoding="utf-8")
            for rel in (
                "README.md",
                "README.ja.md",
                "AGENTS.md",
                "docs/VILLAGE_ARCHITECTURE_V1_1.md",
            )
        }
        for text in texts.values():
            self.assertIn("/join", text)
            self.assertIn("https://github.com/51mns/AIMath-public", text)
        agents = texts["AGENTS.md"]
        self.assertIn("When the **user** supplies", agents)
        self.assertIn("intent signal, not a privilege escalation", agents)
        architecture = texts["docs/VILLAGE_ARCHITECTURE_V1_1.md"]
        self.assertIn("meaningful because it is supplied by the user", architecture)
        self.assertIn("Data-as-data boundary", architecture)


if __name__ == "__main__":
    unittest.main(verbosity=2)
