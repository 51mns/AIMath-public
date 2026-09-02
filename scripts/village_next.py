# SPDX-FileCopyrightText: 2026 AIMath contributors
# SPDX-License-Identifier: Apache-2.0
from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from pathlib import Path
from typing import Any

from village_core import load_machine_file
from village_v1_2 import (
    CapabilityProfile,
    abandonment_cooldown_errors,
    capability_eligible,
    load_actor_policy,
    rank_v12,
    read_abandoned_terminal,
    release_terminal_state,
    result_terminal_errors,
    result_terminal_path,
    task_has_pending_claim,
    validate_worker_id,
    PRINCIPAL_RE,
)


OUTCOME_TYPES = frozenset(
    {
        "CLAIM_CANDIDATE",
        "STRUCTURAL_REDUCTION",
        "COUNTEREXAMPLE",
        "FAILED_ROUTE",
        "REPRODUCTION_FAILURE",
        "NO_REUSABLE_PROGRESS",
        "INCONCLUSIVE",
        "LITERATURE_MATCH",
    }
)
ELIGIBLE_FOLLOWUP_RECOMMENDATIONS = frozenset({"CONTINUE", "PIVOT", "REVIEW"})
ELIGIBLE_EVALUATION_ROLES = frozenset({"INDEPENDENT_EVALUATION", "PORTFOLIO_EVALUATION"})
HUMAN_GATE_OUTCOME_TYPES = frozenset({"CLAIM_CANDIDATE", "COUNTEREXAMPLE", "STRUCTURAL_REDUCTION"})

# Phase A has no mutation authority. These constants are deliberately empty and
# are asserted by the v1.3 acceptance tests.
CANONICAL_MUTATIONS = frozenset()
TRUTH_PROMOTIONS = frozenset()
AUTOMATIC_LIFECYCLE_OPERATIONS = frozenset()


class NextPhase(str, Enum):
    ACTIVE_WORK = "ACTIVE_WORK"
    RESULT_RECORDED = "RESULT_RECORDED"
    CONTINUATION_DECISION = "CONTINUATION_DECISION"
    RELEASE_PENDING = "RELEASE_PENDING"
    RELEASED = "RELEASED"
    NEXT_SELECTION = "NEXT_SELECTION"
    ACQUIRE_PENDING = "ACQUIRE_PENDING"
    ACTIVE_NEXT = "ACTIVE_NEXT"


class NextStatus(str, Enum):
    ACTIVE_WORK = "ACTIVE_WORK"
    RELEASE_REQUIRED = "RELEASE_REQUIRED"
    WAITING_PORTFOLIO = "WAITING_PORTFOLIO"
    NO_ELIGIBLE_TASK = "NO_ELIGIBLE_TASK"
    ACQUIRE_REQUIRED = "ACQUIRE_REQUIRED"
    ACTIVE_NEXT = "ACTIVE_NEXT"
    RANK_FAILED = "RANK_FAILED"
    FAIL_CLOSED = "FAIL_CLOSED"


class RequiredAction(str, Enum):
    NONE = "NONE"
    PREPARE_RELEASE = "PREPARE_RELEASE"
    PREPARE_ACQUIRE = "PREPARE_ACQUIRE"


@dataclass(frozen=True)
class TerminalEvidence:
    terminal_class: str
    task_id: str
    worker_id: str | None
    outcome_type: str | None
    review_required: bool
    truth_layer_effect: str | None
    source_path: str


@dataclass(frozen=True)
class ContinuationDecision:
    review_demand: bool
    same_campaign_allowed: bool
    global_fallback_allowed: bool
    waiting_portfolio: bool
    human_decision: str | None
    approved_followup_task_ids: tuple[str, ...]
    evaluation_followup_task_ids: tuple[str, ...]
    reasons: tuple[str, ...]


@dataclass(frozen=True)
class SelectionResult:
    status: NextStatus
    selected_task_id: str | None
    relation: str | None
    ranked_task_ids: tuple[str, ...]
    hard_eligible_task_ids: tuple[str, ...]
    errors: tuple[str, ...] = ()


@dataclass(frozen=True)
class NextRequest:
    task_id: str
    worker_id: str
    principal_id: str
    capabilities: CapabilityProfile | None = None
    pending_records: tuple[dict[str, Any], ...] = ()
    current_main_sha: str | None = None
    continuation_gate_required: bool = False
    continuation_decision_id: str | None = None
    canonical_stop_condition_reached: bool = False
    canonical_dependency_followup_unusable: bool = False
    fresh_observation_valid: bool = True


@dataclass(frozen=True)
class NextResult:
    phase: NextPhase
    status: NextStatus
    trace: tuple[NextPhase, ...]
    terminal: TerminalEvidence | None
    continuation: ContinuationDecision | None
    selected_task_id: str | None
    selected_relation: str | None
    required_action: RequiredAction
    canonical_ownership: bool
    errors: tuple[str, ...] = ()


class _RankStateView:
    """Read-only rank view that hard-blocks candidates before rank_v12 scores them."""

    def __init__(self, state: Any, allowed: set[str]):
        self._state = state
        self._allowed = frozenset(allowed)

    def __getattr__(self, name: str) -> Any:
        return getattr(self._state, name)

    def runtime_state(self, task_id: str) -> str:
        if task_id not in self._allowed:
            return "BLOCKED"
        return self._state.runtime_state(task_id)


def _state_errors(state: Any, book: Any) -> tuple[str, ...]:
    errors = list(getattr(state, "errors", []) or [])
    errors.extend(getattr(book, "errors", []) or [])
    return tuple(dict.fromkeys(str(x) for x in errors if x))


def _canonical_lock_for_task(state: Any, task_id: str) -> tuple[Any | None, tuple[str, ...]]:
    bundles = list(state.lock_for_task(task_id, active_only=False))
    if len(bundles) > 1:
        return None, (f"multiple canonical lock bundles exist for {task_id}",)
    return (bundles[0], ()) if bundles else (None, ())


def _identity_errors(bundle: Any, request: NextRequest) -> tuple[str, ...]:
    payload = bundle.payload
    errors: list[str] = []
    if payload.get("task_id") != request.task_id:
        errors.append("canonical lock Task binding mismatch")
    if payload.get("worker_id") != request.worker_id:
        errors.append("canonical lock worker binding mismatch")
    if payload.get("actor", {}).get("id") != request.principal_id:
        errors.append("canonical lock principal binding mismatch")
    return tuple(errors)


def recognize_terminal_evidence(
    state: Any,
    *,
    task_id: str,
    worker_id: str,
    lock_payload: dict[str, Any] | None = None,
) -> tuple[TerminalEvidence | None, tuple[str, ...]]:
    """Recognize terminal evidence only from canonical repository paths.

    Branches, chats, PR descriptions and caller prose are intentionally absent
    from this API. When a current lock payload is available, the inherited
    v1.2.1 acquisition-time checks are reused for abandonment evidence.
    """

    root = Path(state.root)
    result_ok, result_errors = result_terminal_errors(root, task_id)
    if result_ok:
        try:
            record = load_machine_file(root / result_terminal_path(task_id))
        except Exception as exc:
            return None, (f"canonical RESULT_TERMINAL became unreadable: {exc}",)
        outcome_type = record.get("outcome_type")
        if outcome_type not in OUTCOME_TYPES:
            return None, (f"canonical RESULT_TERMINAL has unsupported outcome_type {outcome_type!r}",)
        return (
            TerminalEvidence(
                terminal_class="RESULT_TERMINAL",
                task_id=task_id,
                worker_id=None,
                outcome_type=outcome_type,
                review_required=record.get("review_required") is True,
                truth_layer_effect=None,
                source_path=result_terminal_path(task_id),
            ),
            (),
        )

    if lock_payload is not None:
        terminal_class, terminal_errors = release_terminal_state(
            root,
            lock_payload,
            now=state.now,
        )
        if terminal_class == "ABANDONED_TERMINAL":
            abandoned, abandoned_errors = read_abandoned_terminal(root, task_id, worker_id)
            if abandoned is None or abandoned_errors:
                return None, tuple(abandoned_errors or ["canonical abandonment disappeared during read"])
            return (
                TerminalEvidence(
                    terminal_class="ABANDONED_TERMINAL",
                    task_id=task_id,
                    worker_id=worker_id,
                    outcome_type=None,
                    review_required=False,
                    truth_layer_effect="NONE",
                    source_path=f"work/{task_id}/{worker_id}/ABANDONED_TERMINAL.yml",
                ),
                (),
            )
        if terminal_class == "NONE":
            only_absence = terminal_errors == [
                "no valid RESULT_TERMINAL or ABANDONED_TERMINAL exists on current main"
            ]
            return None, ("no canonical terminal evidence",) if only_absence else tuple(terminal_errors)

    abandoned, abandoned_errors = read_abandoned_terminal(root, task_id, worker_id)
    if abandoned is not None and not abandoned_errors:
        return (
            TerminalEvidence(
                terminal_class="ABANDONED_TERMINAL",
                task_id=task_id,
                worker_id=worker_id,
                outcome_type=None,
                review_required=False,
                truth_layer_effect="NONE",
                source_path=f"work/{task_id}/{worker_id}/ABANDONED_TERMINAL.yml",
            ),
            (),
        )

    errors: list[str] = []
    if result_errors:
        errors.append("RESULT_TERMINAL invalid: " + "; ".join(result_errors))
    if abandoned_errors:
        errors.append("ABANDONED_TERMINAL invalid: " + "; ".join(abandoned_errors))
    if not errors:
        errors.append("no canonical terminal evidence")
    return None, tuple(errors)


def _human_continuation_decision(state: Any, request: NextRequest) -> dict[str, Any] | None:
    if not request.continuation_decision_id:
        return None
    campaign_id = state.tasks[request.task_id]["campaign_id"]
    for record in state.decisions:
        if (
            record.get("decision_id") == request.continuation_decision_id
            and record.get("campaign_id") == campaign_id
            and record.get("authority") == "HUMAN_MAINTAINER"
        ):
            return record
    return None


def approved_same_campaign_followups(state: Any, source_task_id: str) -> tuple[str, ...]:
    source_campaign = state.tasks[source_task_id]["campaign_id"]
    return tuple(
        sorted(
            task_id
            for task_id, task in state.tasks.items()
            if task_id != source_task_id
            and task.get("campaign_id") == source_campaign
            and task.get("stored_state") == "APPROVED"
        )
    )


def canonical_evaluation_followups(book: Any, source_task_id: str) -> tuple[str, ...]:
    """Return canonical non-self follow-up references for visibility only.

    These references never create Tasks. Candidate authority still requires an
    existing APPROVED Task and the hard eligibility gates below.
    """

    targets: set[str] = set()
    for record in getattr(book, "records", []):
        if record.get("task_id") != source_task_id:
            continue
        if record.get("evaluation_role") not in ELIGIBLE_EVALUATION_ROLES:
            continue
        if record.get("recommendation") not in ELIGIBLE_FOLLOWUP_RECOMMENDATIONS:
            continue
        for task_id in record.get("followup_task_ids", []):
            if isinstance(task_id, str):
                targets.add(task_id)
    return tuple(sorted(targets))


def derive_continuation_decision(
    state: Any,
    book: Any,
    request: NextRequest,
    terminal: TerminalEvidence,
) -> ContinuationDecision:
    campaign = state.campaigns[state.tasks[request.task_id]["campaign_id"]]
    same_campaign_allowed = True
    global_fallback_allowed = True
    waiting_portfolio = False
    reasons: list[str] = []
    human = _human_continuation_decision(state, request)
    human_value = human.get("decision") if human else None

    # Mandatory stop/wait gates come first. They restrict scheduling but never
    # convert a terminal research result into a truth judgement.
    if state.portfolio.get("global_admission") != "OPEN":
        same_campaign_allowed = False
        global_fallback_allowed = False
        waiting_portfolio = True
        reasons.append("global admission is not OPEN")
    if campaign.get("strategic_state") == "CLOSED":
        same_campaign_allowed = False
        reasons.append("source Campaign is CLOSED")
    if request.canonical_dependency_followup_unusable:
        same_campaign_allowed = False
        reasons.append("dependency reevaluation makes source-Campaign follow-up unusable")
    if request.canonical_stop_condition_reached:
        same_campaign_allowed = False
        reasons.append("explicit source Task/Campaign stop condition reached")

    gate_required = request.continuation_gate_required or terminal.outcome_type in HUMAN_GATE_OUTCOME_TYPES
    if gate_required:
        if human is None:
            same_campaign_allowed = False
            reasons.append("required human Continuation Gate decision is absent")
        elif human_value not in {"CONTINUE", "PIVOT"}:
            same_campaign_allowed = False
            reasons.append(f"human Continuation Gate decision is {human_value}")

    approved = approved_same_campaign_followups(state, request.task_id)
    # Canonical non-self evaluations are retained only as bounded ranking/visibility
    # metadata. They never create or expand the approved Task candidate set.
    evaluation_targets = tuple(
        task_id
        for task_id in canonical_evaluation_followups(book, request.task_id)
        if task_id in state.tasks and state.tasks[task_id].get("stored_state") == "APPROVED"
    )

    if not same_campaign_allowed and not global_fallback_allowed:
        waiting_portfolio = True

    return ContinuationDecision(
        review_demand=terminal.review_required,
        same_campaign_allowed=same_campaign_allowed,
        global_fallback_allowed=global_fallback_allowed,
        waiting_portfolio=waiting_portfolio,
        human_decision=human_value,
        approved_followup_task_ids=approved,
        evaluation_followup_task_ids=evaluation_targets,
        reasons=tuple(reasons),
    )


def _worker_exclusive_capacity_error(state: Any, request: NextRequest, task_id: str) -> str | None:
    task = state.tasks[task_id]
    if task.get("parallelism") != "EXCLUSIVE":
        return None
    policy = load_actor_policy(state.root)
    cap = int(policy.get("exclusive_worker_lock_cap_default", 1))
    active = 0
    for bundle in state.active_lock_bundles():
        payload = bundle.payload
        old_task = state.tasks.get(payload.get("task_id"), {})
        if old_task.get("parallelism") != "EXCLUSIVE":
            continue
        if payload.get("actor", {}).get("id") == request.principal_id and payload.get("worker_id") == request.worker_id:
            active += 1
    if active >= cap:
        return f"worker EXCLUSIVE lock cap {cap} already reached"
    return None


def hard_eligible_task_ids(
    state: Any,
    request: NextRequest,
    continuation: ContinuationDecision,
) -> tuple[tuple[str, ...], tuple[str, ...]]:
    """Apply all Phase-A-observable hard gates before calling rank_v12."""

    if not request.fresh_observation_valid:
        return (), ("repository-wide fresh observation is unavailable or malformed",)
    if request.pending_records and not request.current_main_sha:
        return (), ("current_main_sha is required when pending reservations are supplied",)

    source_campaign = state.tasks[request.task_id]["campaign_id"]
    approved_same = set(continuation.approved_followup_task_ids)
    eligible: list[str] = []
    errors: list[str] = []

    for task_id in sorted(state.tasks):
        if task_id == request.task_id:
            continue
        task = state.tasks[task_id]
        if state.runtime_state(task_id) != "READY":
            continue
        if task.get("stored_state") != "APPROVED":
            continue
        capability_ok, _ = capability_eligible(state, task_id, request.capabilities)
        if not capability_ok:
            continue
        if request.pending_records and task_has_pending_claim(
            state,
            task_id,
            request.pending_records,
            current_main_sha=request.current_main_sha or "",
            now=state.now,
        ):
            continue
        cooldown = abandonment_cooldown_errors(state, task_id, request.worker_id)
        if cooldown:
            continue
        cap_error = _worker_exclusive_capacity_error(state, request, task_id)
        if cap_error:
            continue

        same_campaign = task.get("campaign_id") == source_campaign
        if same_campaign:
            if not continuation.same_campaign_allowed or task_id not in approved_same:
                continue
        elif not continuation.global_fallback_allowed:
            continue
        eligible.append(task_id)

    return tuple(eligible), tuple(errors)


def _selection_relation(state: Any, source_task_id: str, target_task_id: str) -> str:
    source = state.tasks[source_task_id]
    target = state.tasks[target_task_id]
    if target.get("campaign_id") != source.get("campaign_id"):
        return "GLOBAL_READY"
    source_route = source.get("route_id")
    target_route = target.get("route_id")
    if source_route and target_route and source_route == target_route:
        return "SAME_ROUTE_TASK"
    if source_route and target_route and source_route != target_route:
        return "ALTERNATIVE_ROUTE_TASK"
    return "SAME_CAMPAIGN_TASK"


def select_next_task(
    state: Any,
    book: Any,
    request: NextRequest,
    continuation: ContinuationDecision,
) -> SelectionResult:
    try:
        hard_ids, hard_errors = hard_eligible_task_ids(state, request, continuation)
        if hard_errors:
            return SelectionResult(
                status=NextStatus.RANK_FAILED,
                selected_task_id=None,
                relation=None,
                ranked_task_ids=(),
                hard_eligible_task_ids=hard_ids,
                errors=hard_errors,
            )
        view = _RankStateView(state, set(hard_ids))
        ranked = rank_v12(
            view,
            book,
            capabilities=request.capabilities,
            pending_records=request.pending_records,
            current_main_sha=request.current_main_sha,
            now=state.now,
        )
    except Exception as exc:
        return SelectionResult(
            status=NextStatus.RANK_FAILED,
            selected_task_id=None,
            relation=None,
            ranked_task_ids=(),
            hard_eligible_task_ids=(),
            errors=(f"rank/eligibility computation failed closed: {type(exc).__name__}: {exc}",),
        )

    ranked_ids = tuple(row.task_id for row in ranked)
    source_campaign = state.tasks[request.task_id]["campaign_id"]
    same_campaign = [
        task_id
        for task_id in ranked_ids
        if state.tasks[task_id].get("campaign_id") == source_campaign
    ]
    global_ready = [
        task_id
        for task_id in ranked_ids
        if state.tasks[task_id].get("campaign_id") != source_campaign
    ]

    selected = same_campaign[0] if same_campaign else (global_ready[0] if global_ready else None)
    if selected is not None:
        return SelectionResult(
            status=NextStatus.ACQUIRE_REQUIRED,
            selected_task_id=selected,
            relation=_selection_relation(state, request.task_id, selected),
            ranked_task_ids=ranked_ids,
            hard_eligible_task_ids=hard_ids,
        )

    if continuation.waiting_portfolio or (
        (request.continuation_gate_required or continuation.human_decision is None)
        and not continuation.same_campaign_allowed and not global_ready
    ):
        return SelectionResult(
            status=NextStatus.WAITING_PORTFOLIO,
            selected_task_id=None,
            relation=None,
            ranked_task_ids=ranked_ids,
            hard_eligible_task_ids=hard_ids,
        )
    return SelectionResult(
        status=NextStatus.NO_ELIGIBLE_TASK,
        selected_task_id=None,
        relation=None,
        ranked_task_ids=ranked_ids,
        hard_eligible_task_ids=hard_ids,
    )


def _canonical_next_lock(state: Any, request: NextRequest) -> tuple[Any | None, tuple[str, ...]]:
    matches = []
    for bundle in state.active_lock_bundles():
        payload = bundle.payload
        if payload.get("task_id") == request.task_id:
            continue
        if payload.get("worker_id") != request.worker_id:
            continue
        if payload.get("actor", {}).get("id") != request.principal_id:
            continue
        matches.append(bundle)
    if len(matches) > 1:
        return None, ("multiple canonical active-next locks match this worker/principal",)
    return (matches[0], ()) if matches else (None, ())


def derive_next_state(state: Any, book: Any, request: NextRequest) -> NextResult:
    """Derive the v1.3 Phase-A `/next` state without performing any mutation."""

    if not validate_worker_id(request.worker_id):
        return NextResult(
            phase=NextPhase.ACTIVE_WORK,
            status=NextStatus.FAIL_CLOSED,
            trace=(NextPhase.ACTIVE_WORK,),
            terminal=None,
            continuation=None,
            selected_task_id=None,
            selected_relation=None,
            required_action=RequiredAction.NONE,
            canonical_ownership=False,
            errors=("invalid worker_id",),
        )
    if request.task_id not in state.tasks:
        return NextResult(
            phase=NextPhase.ACTIVE_WORK,
            status=NextStatus.FAIL_CLOSED,
            trace=(NextPhase.ACTIVE_WORK,),
            terminal=None,
            continuation=None,
            selected_task_id=None,
            selected_relation=None,
            required_action=RequiredAction.NONE,
            canonical_ownership=False,
            errors=("unknown source Task",),
        )
    if PRINCIPAL_RE.fullmatch(request.principal_id or "") is None:
        return NextResult(
            phase=NextPhase.ACTIVE_WORK,
            status=NextStatus.FAIL_CLOSED,
            trace=(NextPhase.ACTIVE_WORK,),
            terminal=None,
            continuation=None,
            selected_task_id=None,
            selected_relation=None,
            required_action=RequiredAction.NONE,
            canonical_ownership=False,
            errors=("invalid principal_id",),
        )

    errors = _state_errors(state, book)
    if errors:
        return NextResult(
            phase=NextPhase.ACTIVE_WORK,
            status=NextStatus.FAIL_CLOSED,
            trace=(NextPhase.ACTIVE_WORK,),
            terminal=None,
            continuation=None,
            selected_task_id=None,
            selected_relation=None,
            required_action=RequiredAction.NONE,
            canonical_ownership=False,
            errors=errors,
        )

    source_lock, lock_errors = _canonical_lock_for_task(state, request.task_id)
    if lock_errors:
        return NextResult(
            phase=NextPhase.ACTIVE_WORK,
            status=NextStatus.FAIL_CLOSED,
            trace=(NextPhase.ACTIVE_WORK,),
            terminal=None,
            continuation=None,
            selected_task_id=None,
            selected_relation=None,
            required_action=RequiredAction.NONE,
            canonical_ownership=False,
            errors=lock_errors,
        )
    if source_lock is not None:
        identity = _identity_errors(source_lock, request)
        if identity:
            return NextResult(
                phase=NextPhase.ACTIVE_WORK,
                status=NextStatus.FAIL_CLOSED,
                trace=(NextPhase.ACTIVE_WORK,),
                terminal=None,
                continuation=None,
                selected_task_id=None,
                selected_relation=None,
                required_action=RequiredAction.NONE,
                canonical_ownership=False,
                errors=identity,
            )

    terminal, terminal_errors = recognize_terminal_evidence(
        state,
        task_id=request.task_id,
        worker_id=request.worker_id,
        lock_payload=source_lock.payload if source_lock is not None else None,
    )

    if source_lock is not None and terminal is None:
        # An exact canonical lock with no repository-recognised terminal evidence
        # remains ordinary active work. Invalid terminal files are surfaced but
        # never terminalise the acquisition.
        nonabsence_errors = tuple(
            error for error in terminal_errors if error != "no canonical terminal evidence"
        )
        return NextResult(
            phase=NextPhase.ACTIVE_WORK,
            status=NextStatus.ACTIVE_WORK if not nonabsence_errors else NextStatus.FAIL_CLOSED,
            trace=(NextPhase.ACTIVE_WORK,),
            terminal=None,
            continuation=None,
            selected_task_id=None,
            selected_relation=None,
            required_action=RequiredAction.NONE,
            canonical_ownership=True,
            errors=nonabsence_errors,
        )

    if terminal is None:
        return NextResult(
            phase=NextPhase.NEXT_SELECTION,
            status=NextStatus.FAIL_CLOSED,
            trace=(NextPhase.RELEASED, NextPhase.NEXT_SELECTION),
            terminal=None,
            continuation=None,
            selected_task_id=None,
            selected_relation=None,
            required_action=RequiredAction.NONE,
            canonical_ownership=False,
            errors=terminal_errors,
        )

    continuation = derive_continuation_decision(state, book, request, terminal)
    terminal_trace = (NextPhase.RESULT_RECORDED, NextPhase.CONTINUATION_DECISION)

    if source_lock is not None:
        return NextResult(
            phase=NextPhase.RELEASE_PENDING,
            status=NextStatus.RELEASE_REQUIRED,
            trace=terminal_trace + (NextPhase.RELEASE_PENDING,),
            terminal=terminal,
            continuation=continuation,
            selected_task_id=None,
            selected_relation=None,
            required_action=RequiredAction.PREPARE_RELEASE,
            canonical_ownership=True,
        )

    active_next, active_next_errors = _canonical_next_lock(state, request)
    if active_next_errors:
        return NextResult(
            phase=NextPhase.NEXT_SELECTION,
            status=NextStatus.FAIL_CLOSED,
            trace=terminal_trace + (NextPhase.RELEASED, NextPhase.NEXT_SELECTION),
            terminal=terminal,
            continuation=continuation,
            selected_task_id=None,
            selected_relation=None,
            required_action=RequiredAction.NONE,
            canonical_ownership=False,
            errors=active_next_errors,
        )
    if active_next is not None:
        task_id = active_next.payload.get("task_id")
        return NextResult(
            phase=NextPhase.ACTIVE_NEXT,
            status=NextStatus.ACTIVE_NEXT,
            trace=terminal_trace + (NextPhase.RELEASED, NextPhase.NEXT_SELECTION, NextPhase.ACQUIRE_PENDING, NextPhase.ACTIVE_NEXT),
            terminal=terminal,
            continuation=continuation,
            selected_task_id=task_id,
            selected_relation=_selection_relation(state, request.task_id, task_id),
            required_action=RequiredAction.NONE,
            canonical_ownership=True,
        )

    selection = select_next_task(state, book, request, continuation)
    base_trace = terminal_trace + (NextPhase.RELEASED, NextPhase.NEXT_SELECTION)
    if selection.status == NextStatus.ACQUIRE_REQUIRED:
        return NextResult(
            phase=NextPhase.ACQUIRE_PENDING,
            status=selection.status,
            trace=base_trace + (NextPhase.ACQUIRE_PENDING,),
            terminal=terminal,
            continuation=continuation,
            selected_task_id=selection.selected_task_id,
            selected_relation=selection.relation,
            required_action=RequiredAction.PREPARE_ACQUIRE,
            canonical_ownership=False,
        )
    return NextResult(
        phase=NextPhase.NEXT_SELECTION,
        status=selection.status,
        trace=base_trace,
        terminal=terminal,
        continuation=continuation,
        selected_task_id=None,
        selected_relation=None,
        required_action=RequiredAction.NONE,
        canonical_ownership=False,
        errors=selection.errors,
    )
