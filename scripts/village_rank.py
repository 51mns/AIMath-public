# SPDX-FileCopyrightText: 2026 AIMath contributors
# SPDX-License-Identifier: Apache-2.0
from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
import json
import statistics
from typing import Any

from village_core import VillageState, load_machine_file, validate_schema

RESEARCH_CLASSES = {
    "EXTERNAL_OPEN_PROBLEM",
    "DERIVED_GENERAL_MATH",
    "OPEN_MATH_DISCOVERY",
    "AI_NATIVE_MATH",
    "QUALITY_KNOWLEDGE",
    "PLATFORM",
}
QUALITY_TASK_KINDS = {
    "INDEPENDENT_REVIEW",
    "REPRODUCTION",
    "FRONTIER_REFRESH",
    "LITERATURE_AUDIT",
    "DEPENDENCY_TRIAGE",
}
ELIGIBLE_EVALUATION_ROLES = {"INDEPENDENT_EVALUATION", "PORTFOLIO_EVALUATION"}
FOLLOWUP_RECOMMENDATIONS = {"CONTINUE", "PIVOT", "REVIEW"}
LEGACY_CLASS_BY_KIND = {
    "EXTERNAL_OPEN_PROBLEM": "EXTERNAL_OPEN_PROBLEM",
    "PUBLIC_RESEARCH_THEME": "DERIVED_GENERAL_MATH",
    "FOUNDATIONAL_RESEARCH": "DERIVED_GENERAL_MATH",
    "SOFTWARE_RESEARCH": "PLATFORM",
}
PRIORITY_BASE = {"P0": 75, "P1": 50, "P2": 25, "HOLD": 0}
CONFIDENCE_FACTOR = {"LOW": 0.50, "MEDIUM": 0.75, "HIGH": 1.00}
RECOMMENDATION_FACTOR = {
    "CONTINUE": 1.00,
    "REVIEW": 0.85,
    "PIVOT": 0.60,
    "NO_OPINION": 0.50,
    "HOLD": 0.20,
    "CLOSE": 0.00,
}


@dataclass(frozen=True)
class RankedTask:
    task_id: str
    score: int
    priority: str
    research_class: str
    class_weight_bonus: int
    diversity_bonus: int
    campaign_headroom_bonus: int
    evaluation_bonus: int
    eligible_evaluations: int
    self_evaluations: int
    eligible_followup_expected_value: float | None
    self_followup_expected_value: float | None


def research_class_for_task(state: VillageState, task_id: str) -> str:
    task = state.tasks[task_id]
    if task.get("task_kind") in QUALITY_TASK_KINDS:
        return "QUALITY_KNOWLEDGE"
    campaign = state.campaigns[task["campaign_id"]]
    explicit = campaign.get("research_class")
    if explicit:
        return explicit
    return LEGACY_CLASS_BY_KIND.get(campaign.get("kind"), "DERIVED_GENERAL_MATH")


def discovery_policy_errors(state: VillageState) -> list[str]:
    errors: list[str] = []
    policy = state.portfolio.get("allocation_policy", {})
    if policy.get("mode") != "ADAPTIVE_DIVERSITY":
        errors.append("allocation_policy.mode must be ADAPTIVE_DIVERSITY")
    weights = policy.get("class_weights", {})
    caps = policy.get("soft_class_caps_pct", {})
    for research_class in sorted(RESEARCH_CLASSES):
        weight = weights.get(research_class)
        if not isinstance(weight, int) or isinstance(weight, bool) or weight < 1:
            errors.append(f"allocation_policy.class_weights.{research_class} must be integer >= 1")
        cap = caps.get(research_class)
        if not isinstance(cap, int) or isinstance(cap, bool) or not 0 <= cap <= 100:
            errors.append(f"allocation_policy.soft_class_caps_pct.{research_class} must be integer 0..100")
    eval_cap = policy.get("evaluation_bonus_cap")
    if not isinstance(eval_cap, int) or isinstance(eval_cap, bool) or not 0 <= eval_cap <= 12:
        errors.append("allocation_policy.evaluation_bonus_cap must be integer 0..12")

    for tid, task in state.tasks.items():
        research_class = research_class_for_task(state, tid)
        if research_class == "OPEN_MATH_DISCOVERY" and task.get("task_kind") == "RESEARCH":
            if task.get("research_mode") != "OPEN_THEOREM_DISCOVERY":
                errors.append(f"{tid}: OPEN_MATH_DISCOVERY research requires research_mode OPEN_THEOREM_DISCOVERY")
            if task.get("toy_problem_gate") is not True:
                errors.append(f"{tid}: OPEN_MATH_DISCOVERY research requires toy_problem_gate=true")
            campaign = state.campaigns[task["campaign_id"]]
            if campaign.get("discovery_policy", {}).get("held_out_default") is True and task.get("held_out_required") is not True:
                errors.append(f"{tid}: campaign held_out_default requires held_out_required=true")
            if task.get("post_outcome_evaluation") != "REQUIRED":
                errors.append(f"{tid}: discovery research requires post_outcome_evaluation=REQUIRED")
        if research_class == "AI_NATIVE_MATH" and task.get("task_kind") == "RESEARCH":
            if task.get("research_mode") != "AI_NATIVE_REPRESENTATION":
                errors.append(f"{tid}: AI_NATIVE_MATH research requires research_mode AI_NATIVE_REPRESENTATION")
            if task.get("held_out_required") is not True:
                errors.append(f"{tid}: AI_NATIVE_MATH research requires held_out_required=true")
            if task.get("toy_problem_gate") is not True:
                errors.append(f"{tid}: AI_NATIVE_MATH research requires toy_problem_gate=true")
            if task.get("transfer_test_required") is not True:
                errors.append(f"{tid}: AI_NATIVE_MATH research requires transfer_test_required=true")
            if task.get("post_outcome_evaluation") != "REQUIRED":
                errors.append(f"{tid}: AI-native research requires post_outcome_evaluation=REQUIRED")
        if research_class in {"OPEN_MATH_DISCOVERY", "AI_NATIVE_MATH"} and task.get("task_kind") == "RESEARCH":
            if not task.get("stop_conditions"):
                errors.append(f"{tid}: discovery research requires bounded stop_conditions")
            if not task.get("success_conditions"):
                errors.append(f"{tid}: discovery research requires explicit success_conditions")
    return errors


def _mean_followup(evals: list[dict[str, Any]]) -> float | None:
    vals = [e.get("scores", {}).get("followup_expected_value") for e in evals]
    vals = [float(x) for x in vals if isinstance(x, int) and not isinstance(x, bool)]
    return round(sum(vals) / len(vals), 2) if vals else None


class EvaluationBook:
    def __init__(self, root: Path | str, state: VillageState):
        self.root = Path(root).resolve()
        self.state = state
        self.records: list[dict[str, Any]] = []
        self.errors: list[str] = []

    def load(self) -> "EvaluationBook":
        self.records = []
        self.errors = []
        schema_path = self.root / "schemas/evaluation.schema.json"
        if not schema_path.is_file():
            self.errors.append("missing schemas/evaluation.schema.json")
            return self
        schema = json.loads(schema_path.read_text(encoding="utf-8"))
        seen_ids: set[str] = set()
        seen_evaluator_slots: set[tuple[str, str, str]] = set()
        eval_root = self.root / "coordination/evaluations"
        if not eval_root.exists():
            return self
        for path in sorted(eval_root.glob("**/*.yml")):
            record = load_machine_file(path)
            rel = str(path.relative_to(self.root))
            self.errors.extend(validate_schema(record, schema, rel))
            eid = record.get("evaluation_id")
            if eid in seen_ids:
                self.errors.append(f"duplicate evaluation id {eid}")
            if isinstance(eid, str):
                seen_ids.add(eid)
            tid = record.get("task_id")
            if tid not in self.state.tasks:
                self.errors.append(f"{rel}: unknown task {tid}")
            elif tid not in self.state.outcomes:
                self.errors.append(f"{rel}: evaluation is post-outcome metadata but task {tid} has no canonical outcome")
            role = record.get("evaluation_role")
            actor = record.get("evaluator", {}).get("actor_id")
            if isinstance(tid, str) and isinstance(role, str) and isinstance(actor, str):
                slot = (tid, role, actor)
                if slot in seen_evaluator_slots:
                    self.errors.append(
                        f"{rel}: evaluator {actor} has duplicate {role} for task {tid}"
                    )
                seen_evaluator_slots.add(slot)
            followups = record.get("followup_task_ids", [])
            if len(followups) != len(set(followups)):
                self.errors.append(f"{rel}: followup_task_ids contains duplicates")
            for target in followups:
                if target not in self.state.tasks:
                    self.errors.append(f"{rel}: unknown follow-up task {target}")
                if target == tid:
                    self.errors.append(f"{rel}: evaluated task may not target itself as follow-up")
            if record.get("recommendation") in FOLLOWUP_RECOMMENDATIONS and not followups:
                self.errors.append(f"{rel}: {record.get('recommendation')} requires at least one followup_task_id")
            self.records.append(record)
        return self

    def for_source_task(self, task_id: str) -> list[dict[str, Any]]:
        return [r for r in self.records if r.get("task_id") == task_id]

    def _signals_for_target(self, task_id: str, roles: set[str]) -> list[dict[str, Any]]:
        return [
            r
            for r in self.records
            if r.get("evaluation_role") in roles and task_id in r.get("followup_task_ids", [])
        ]

    def allocation_eligible(self, task_id: str) -> list[dict[str, Any]]:
        return self._signals_for_target(task_id, ELIGIBLE_EVALUATION_ROLES)

    def self_assessments(self, task_id: str) -> list[dict[str, Any]]:
        return self._signals_for_target(task_id, {"SELF_ASSESSMENT"})

    @staticmethod
    def _single_signal(record: dict[str, Any], cap: int) -> float:
        s = record.get("scores", {})
        positive = (
            s.get("information_gain", 0)
            + s.get("mathematical_reusability", 0)
            + s.get("transfer_potential", 0)
            + s.get("external_relevance", 0)
            + 2 * s.get("followup_expected_value", 0)
        )
        positive_fraction = max(0.0, min(1.0, positive / 30.0))
        uncertainty = s.get("uncertainty", 5)
        certainty_fraction = max(0.0, min(1.0, (5 - uncertainty) / 5.0))
        confidence = CONFIDENCE_FACTOR.get(record.get("confidence"), 0.0)
        recommendation = RECOMMENDATION_FACTOR.get(record.get("recommendation"), 0.0)
        return cap * positive_fraction * certainty_fraction * confidence * recommendation

    def allocation_bonus(self, task_id: str, cap: int) -> int:
        eligible = self.allocation_eligible(task_id)
        if not eligible or cap <= 0:
            return 0
        # Median makes the signal bounded and prevents evaluation count itself from
        # becoming an additive popularity/reputation mechanism.
        signals = [self._single_signal(r, cap) for r in eligible]
        return max(0, min(cap, int(round(statistics.median(signals)))))

    def render(self) -> str:
        lines = [
            "# Research Evaluations",
            "",
            "> GENERATED deterministically from canonical `coordination/evaluations/**/*.yml`. Do not hand-edit.",
            "> Evaluation scores are allocation/visibility metadata only. `truth_layer_effect` is always `NONE`.",
            "",
            "| Evaluation | Source task | Role | Info | Reuse | Transfer | External | Follow-up EV | Surprise | Uncertainty | Confidence | Recommendation | Follow-up tasks |",
            "|---|---|---|---:|---:|---:|---:|---:|---:|---:|---|---|---|",
        ]
        for r in sorted(self.records, key=lambda x: x.get("evaluation_id", "")):
            s = r.get("scores", {})
            followups = ", ".join(f"`{x}`" for x in r.get("followup_task_ids", [])) or "—"
            lines.append(
                f"| `{r.get('evaluation_id')}` | `{r.get('task_id')}` | {r.get('evaluation_role')} | "
                f"{s.get('information_gain')} | {s.get('mathematical_reusability')} | "
                f"{s.get('transfer_potential')} | {s.get('external_relevance')} | "
                f"{s.get('followup_expected_value')} | {s.get('surprise')} | {s.get('uncertainty')} | "
                f"{r.get('confidence')} | {r.get('recommendation')} | {followups} |"
            )
        if not self.records:
            lines.append("| — | — | — | — | — | — | — | — | — | — | — | No canonical evaluations yet | — |")
        lines += [
            "",
            "Self-assessment has zero scheduling authority. Independent/Portfolio evaluations contribute only a bounded signal to explicitly named follow-up Tasks after the source Task has a canonical outcome; they never affect mathematical truth, novelty, review independence, or hard readiness gates.",
            "",
        ]
        return "\n".join(lines)

    def view_drift(self) -> list[str]:
        path = self.root / "docs/RESEARCH_EVALUATIONS.md"
        if not path.is_file():
            return ["missing generated view docs/RESEARCH_EVALUATIONS.md"]
        if path.read_text(encoding="utf-8").rstrip() != self.render().rstrip():
            return ["generated view drift: docs/RESEARCH_EVALUATIONS.md"]
        return []


def _class_weight_bonus(state: VillageState, research_class: str) -> int:
    weights = state.portfolio.get("allocation_policy", {}).get("class_weights", {})
    weight = weights.get(research_class, 1)
    if not isinstance(weight, int) or isinstance(weight, bool):
        return 0
    return max(0, min(4, weight - 1))


def _diversity_bonus(state: VillageState, research_class: str) -> int:
    policy = state.portfolio.get("allocation_policy", {})
    caps = policy.get("soft_class_caps_pct", {})
    cap_pct = caps.get(research_class, 100)
    global_cap = max(1, int(state.portfolio.get("global_active_lane_cap", 1)))
    active = 0
    for bundle in state.active_lock_bundles():
        tid = bundle.payload.get("task_id")
        if tid in state.tasks and research_class_for_task(state, tid) == research_class:
            active += 1
    if active == 0:
        return 4
    usage_pct = 100.0 * active / global_cap
    if usage_pct < cap_pct / 3:
        return 3
    if usage_pct < 2 * cap_pct / 3:
        return 2
    if usage_pct < cap_pct:
        return 1
    return 0


def _campaign_headroom_bonus(state: VillageState, task_id: str) -> int:
    task = state.tasks[task_id]
    campaign = state.campaigns[task["campaign_id"]]
    cap = max(1, int(campaign.get("max_active_lanes", 1)))
    active = sum(
        1
        for bundle in state.active_lock_bundles()
        if state.tasks.get(bundle.payload.get("task_id"), {}).get("campaign_id")
        == task["campaign_id"]
    )
    if active == 0:
        return 4
    ratio = active / cap
    if ratio <= 0.25:
        return 3
    if ratio <= 0.50:
        return 2
    if ratio < 1.0:
        return 1
    return 0


def rank_ready_tasks(state: VillageState, book: EvaluationBook) -> list[RankedTask]:
    if not state.portfolio:
        state.load()
    policy = state.portfolio.get("allocation_policy", {})
    eval_cap = int(policy.get("evaluation_bonus_cap", 0))
    rows: list[RankedTask] = []
    for tid in sorted(state.tasks):
        if state.runtime_state(tid) != "READY":
            continue
        task = state.tasks[tid]
        campaign = state.campaigns[task["campaign_id"]]
        priority = campaign.get("priority", "HOLD")
        research_class = research_class_for_task(state, tid)
        class_bonus = _class_weight_bonus(state, research_class)
        diversity = _diversity_bonus(state, research_class)
        headroom = _campaign_headroom_bonus(state, tid)
        evaluation = book.allocation_bonus(tid, eval_cap)
        score = PRIORITY_BASE.get(priority, 0) + class_bonus + diversity + headroom + evaluation
        # By construction bonus components sum to at most 24, so priority bands
        # cannot be crossed by evaluation/diversity signals.
        score = max(0, min(99, score))
        eligible = book.allocation_eligible(tid)
        self_evals = book.self_assessments(tid)
        rows.append(
            RankedTask(
                task_id=tid,
                score=score,
                priority=priority,
                research_class=research_class,
                class_weight_bonus=class_bonus,
                diversity_bonus=diversity,
                campaign_headroom_bonus=headroom,
                evaluation_bonus=evaluation,
                eligible_evaluations=len(eligible),
                self_evaluations=len(self_evals),
                eligible_followup_expected_value=_mean_followup(eligible),
                self_followup_expected_value=_mean_followup(self_evals),
            )
        )
    return sorted(rows, key=lambda r: (-r.score, r.task_id))
