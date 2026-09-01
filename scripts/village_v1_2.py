# SPDX-FileCopyrightText: 2026 AIMath contributors
# SPDX-License-Identifier: Apache-2.0
from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
import json
import re
import secrets
from typing import Any, Iterable

from village_core import parse_time
from village_rank import PRIORITY_BASE, RankedTask, rank_ready_tasks

WORKER_ID_RE = re.compile(r"^w-[0-9a-f]{16,32}$")
TASK_ID_RE = re.compile(r"^TASK-[A-Z0-9-]+$")
SHA_RE = re.compile(r"^[0-9a-f]{40}$")
PRINCIPAL_RE = re.compile(r"^gh:[A-Za-z0-9_.-]+$")
DEFAULT_PENDING_TTL_MINUTES = 60


class VillageV12Error(ValueError):
    pass


@dataclass(frozen=True)
class CapabilityProfile:
    github_write: bool | None = None
    local_compute: bool | None = None
    web_literature: bool | None = None

    @staticmethod
    def _parse(value: str | bool | None) -> bool | None:
        if value is None or value == "unknown":
            return None
        if isinstance(value, bool):
            return value
        low = str(value).strip().lower()
        if low in {"yes", "true", "1", "available"}:
            return True
        if low in {"no", "false", "0", "unavailable"}:
            return False
        raise VillageV12Error(f"invalid capability value {value!r}")

    @classmethod
    def from_values(
        cls,
        *,
        github_write: str | bool | None = None,
        local_compute: str | bool | None = None,
        web_literature: str | bool | None = None,
    ) -> "CapabilityProfile":
        return cls(
            github_write=cls._parse(github_write),
            local_compute=cls._parse(local_compute),
            web_literature=cls._parse(web_literature),
        )

    def is_unspecified(self) -> bool:
        return self.github_write is None and self.local_compute is None and self.web_literature is None


@dataclass(frozen=True)
class WorkerWorkspace:
    task_id: str
    worker_id: str
    slot_id: str
    branch: str
    owned_path: str


@dataclass(frozen=True)
class V12RankedTask:
    base: RankedTask
    capability_fit: int

    @property
    def task_id(self) -> str:
        return self.base.task_id


def generate_worker_id() -> str:
    """Return a non-secret session identifier. It is coordination metadata, not a credential."""
    return "w-" + secrets.token_hex(8)


def validate_worker_id(worker_id: str) -> bool:
    return bool(WORKER_ID_RE.fullmatch(worker_id or ""))


def worker_workspace(task_id: str, worker_id: str) -> WorkerWorkspace:
    if not TASK_ID_RE.fullmatch(task_id or "") or len(task_id) > 96:
        raise VillageV12Error(f"invalid/overlong task_id {task_id!r}")
    if not validate_worker_id(worker_id):
        raise VillageV12Error(f"invalid worker_id {worker_id!r}")
    return WorkerWorkspace(
        task_id=task_id,
        worker_id=worker_id,
        slot_id=f"{task_id}:{worker_id}",
        branch=f"research/{task_id}/{worker_id}",
        owned_path=f"work/{task_id}/{worker_id}/**",
    )


def load_actor_policy(root: Path | str) -> dict[str, Any]:
    path = Path(root) / "coordination/policy/ACTOR_POLICY.yml"
    if not path.is_file():
        return {}
    return json.loads(path.read_text(encoding="utf-8"))


def _worker_slot_key(payload: dict[str, Any]) -> tuple[str, str]:
    principal = payload.get("actor", {}).get("id", "")
    worker = payload.get("worker_id")
    return principal, worker if isinstance(worker, str) else "__legacy__"


def worker_lock_errors(state, actor_policy: dict[str, Any] | None = None) -> list[str]:
    """Validate worker-level EXCLUSIVE capacity without treating worker IDs as trust credentials."""
    policy = actor_policy or {}
    cap = int(policy.get("exclusive_worker_lock_cap_default", 1))
    errors: list[str] = []
    counts: dict[tuple[str, str], int] = {}
    work_refs: dict[str, str] = {}
    for bundle in state.active_lock_bundles():
        payload = bundle.payload
        worker_id = payload.get("worker_id")
        if worker_id is not None and not validate_worker_id(str(worker_id)):
            errors.append(f"lock {bundle.lock_id}: malformed worker_id")
        tid = payload.get("task_id")
        task = state.tasks.get(tid, {})
        if task.get("parallelism") != "EXCLUSIVE":
            continue
        key = _worker_slot_key(payload)
        counts[key] = counts.get(key, 0) + 1
        work_ref = payload.get("work_ref")
        if isinstance(work_ref, str):
            old = work_refs.get(work_ref)
            if old and old != bundle.lock_id:
                errors.append(f"active EXCLUSIVE work_ref reused by {old} and {bundle.lock_id}")
            work_refs[work_ref] = bundle.lock_id
    for (principal, worker), count in counts.items():
        if count > cap:
            errors.append(
                f"{principal}/{worker}: active EXCLUSIVE locks {count} exceed worker cap {cap}"
            )
    return errors


def new_worker_lock_errors(
    base_state,
    bundle,
    *,
    actor_policy: dict[str, Any] | None = None,
) -> list[str]:
    policy = actor_policy or {}
    errors: list[str] = []
    required = bool(policy.get("worker_id_required_for_new_lock", False))
    worker_id = bundle.payload.get("worker_id")
    if required and not isinstance(worker_id, str):
        return ["v1.2 new lock acquisition requires worker_id"]
    if worker_id is None:
        return errors
    if not validate_worker_id(str(worker_id)):
        return ["worker_id must match ^w-[0-9a-f]{16,32}$"]
    tid = bundle.payload.get("task_id")
    try:
        workspace = worker_workspace(tid, worker_id)
    except VillageV12Error as exc:
        return [str(exc)]
    if bundle.payload.get("work_ref") != workspace.branch:
        errors.append(f"work_ref must equal deterministic worker branch {workspace.branch}")
    cap = int(policy.get("exclusive_worker_lock_cap_default", 1))
    if base_state.tasks.get(tid, {}).get("parallelism") == "EXCLUSIVE":
        principal = bundle.payload.get("actor", {}).get("id")
        active = 0
        for old in base_state.active_lock_bundles():
            otid = old.payload.get("task_id")
            if base_state.tasks.get(otid, {}).get("parallelism") != "EXCLUSIVE":
                continue
            if (
                old.payload.get("actor", {}).get("id") == principal
                and old.payload.get("worker_id") == worker_id
            ):
                active += 1
        if active >= cap:
            errors.append(f"worker EXCLUSIVE lock cap {cap} already reached")
    return errors


def _pending_ttl_minutes(state) -> int:
    value = state.portfolio.get("governance", {}).get(
        "pending_claim_ttl_minutes", DEFAULT_PENDING_TTL_MINUTES
    )
    try:
        value = int(value)
    except (TypeError, ValueError):
        return DEFAULT_PENDING_TTL_MINUTES
    return max(5, min(240, value))


def validate_pending_claim(
    state,
    record: dict[str, Any],
    *,
    current_main_sha: str,
    now: datetime | None = None,
) -> tuple[bool, list[str]]:
    """Validate advisory live PR/CI observation. Never creates ownership or Truth state."""
    now = (now or datetime.now(timezone.utc)).astimezone(timezone.utc)
    errors: list[str] = []
    if record.get("reservation_kind") != "PENDING_CLAIM":
        errors.append("reservation_kind must be PENDING_CLAIM")
    if record.get("pr_state") != "OPEN":
        errors.append("PR is not OPEN")
    if record.get("draft") is True:
        errors.append("draft PR is not a reservation")
    if record.get("change_class") != "LOCK_ONLY":
        errors.append("change_class is not LOCK_ONLY")
    if record.get("lock_operation") != "ACQUIRE":
        errors.append("only lock ACQUIRE may reserve selection")
    if record.get("village_policy") != "PASS":
        errors.append("Village PR policy did not PASS")
    if record.get("verify_conclusion") != "SUCCESS":
        errors.append("required verify CI is not green")
    if record.get("base_main_sha") != current_main_sha:
        errors.append("pending PR base is stale")
    if not SHA_RE.fullmatch(str(record.get("head_sha", ""))):
        errors.append("invalid pending head_sha")
    pr_number = record.get("pr_number")
    if not isinstance(pr_number, int) or isinstance(pr_number, bool) or pr_number < 1:
        errors.append("invalid pr_number")
    principal_id = record.get("principal_id")
    if not isinstance(principal_id, str) or not PRINCIPAL_RE.fullmatch(principal_id):
        errors.append("invalid principal_id")
    worker_id = record.get("worker_id")
    if worker_id is not None and not validate_worker_id(str(worker_id)):
        errors.append("invalid worker_id")
    tid = record.get("task_id")
    task = state.tasks.get(tid)
    if not task:
        errors.append("unknown pending task")
    else:
        if task.get("parallelism") != "EXCLUSIVE":
            errors.append("PENDING_CLAIM reservation is only for EXCLUSIVE tasks")
        if set(record.get("collision_keys", [])) != set(task.get("collision_keys", [])):
            errors.append("pending collision_keys do not exactly match Task")
        ready, reasons = state.readiness(tid)
        if not ready:
            errors.append("task is no longer READY: " + "; ".join(reasons))
    try:
        observed = parse_time(str(record["observed_at"]))
        age = (now - observed).total_seconds() / 60
        if age < -5:
            errors.append("pending observation is from the future")
        if age > _pending_ttl_minutes(state):
            errors.append("pending observation expired; refresh GitHub PR/CI state")
    except Exception:
        errors.append("invalid observed_at")
    try:
        if parse_time(str(record["lock_expires_at"])) <= now:
            errors.append("proposed lock lease already expired")
    except Exception:
        errors.append("invalid lock_expires_at")
    return not errors, errors


def valid_pending_claims(
    state,
    records: Iterable[dict[str, Any]],
    *,
    current_main_sha: str,
    now: datetime | None = None,
) -> list[dict[str, Any]]:
    out = []
    for record in records:
        ok, _ = validate_pending_claim(
            state, record, current_main_sha=current_main_sha, now=now
        )
        if ok:
            out.append(record)
    return out


def task_has_pending_claim(
    state,
    task_id: str,
    records: Iterable[dict[str, Any]],
    *,
    current_main_sha: str,
    now: datetime | None = None,
) -> bool:
    task = state.tasks[task_id]
    task_keys = set(task.get("collision_keys", []))
    for record in valid_pending_claims(
        state, records, current_main_sha=current_main_sha, now=now
    ):
        if record.get("task_id") == task_id:
            return True
        if task_keys.intersection(record.get("collision_keys", [])):
            return True
    return False


def load_pending_claims(path: str | Path | None) -> list[dict[str, Any]]:
    if not path:
        return []
    value = json.loads(Path(path).read_text(encoding="utf-8"))
    if isinstance(value, dict):
        value = value.get("reservations", [])
    if not isinstance(value, list) or not all(isinstance(x, dict) for x in value):
        raise VillageV12Error("pending reservation file must contain a JSON list or {reservations:[...]}")
    return value


def capability_eligible(state, task_id: str, profile: CapabilityProfile | None) -> tuple[bool, str]:
    if profile is None or profile.is_unspecified():
        return True, "UNSPECIFIED"
    task = state.tasks[task_id]
    if profile.github_write is False and task.get("parallelism") == "EXCLUSIVE":
        return False, "EXCLUSIVE lock acquisition requires GitHub write capability"
    return True, "ELIGIBLE"


def capability_fit(state, task_id: str, profile: CapabilityProfile | None) -> int:
    if profile is None or profile.is_unspecified():
        return 0
    task = state.tasks[task_id]
    kind = task.get("task_kind")
    parallel = task.get("parallelism")
    score = 0
    if profile.github_write is True and parallel == "EXCLUSIVE":
        score += 3
    if profile.github_write is False and parallel != "EXCLUSIVE":
        score += 2
    if profile.local_compute is True and kind in {"RESEARCH", "REPRODUCTION"}:
        score += 1
    if profile.web_literature is True and kind in {"LITERATURE_AUDIT", "FRONTIER_REFRESH"}:
        score += 2
    if profile.github_write is False and parallel == "PARALLEL_SAFE":
        score += 1
    return min(4, score)


def rank_v12(
    state,
    book,
    *,
    capabilities: CapabilityProfile | None = None,
    pending_records: Iterable[dict[str, Any]] = (),
    current_main_sha: str | None = None,
    now: datetime | None = None,
) -> list[V12RankedTask]:
    pending = list(pending_records)
    if pending and not current_main_sha:
        raise VillageV12Error("current_main_sha is required when pending reservations are supplied")
    rows: list[V12RankedTask] = []
    for row in rank_ready_tasks(state, book):
        if pending and task_has_pending_claim(
            state,
            row.task_id,
            pending,
            current_main_sha=current_main_sha or "",
            now=now,
        ):
            continue
        eligible, _ = capability_eligible(state, row.task_id, capabilities)
        if not eligible:
            continue
        rows.append(V12RankedTask(row, capability_fit(state, row.task_id, capabilities)))
    priority_order = {"P0": 0, "P1": 1, "P2": 2, "HOLD": 3}
    return sorted(
        rows,
        key=lambda x: (
            priority_order.get(x.base.priority, 9),
            -x.capability_fit,
            -x.base.score,
            x.base.task_id,
        ),
    )


def trusted_lock_activation_workflow_errors(text: str) -> list[str]:
    """Strict allow-list for the one trusted default-branch workflow_run writer."""
    errors: list[str] = []
    low = text.lower()
    required = (
        "workflow_run",
        "verify public release",
        "types: [completed]",
        "scripts/lock_auto_activate.py",
        "persist-credentials: false",
        "ref: main",
    )
    for token in required:
        if token not in low:
            errors.append(f"trusted lock activation workflow missing {token!r}")
    if "pull_request_target" in low:
        errors.append("pull_request_target is forbidden")
    if "${{ secrets." in low:
        errors.append("repository secrets are forbidden")
    if "permissions: write-all" in low:
        errors.append("permissions: write-all is forbidden")
    allowed_write = {"contents"}
    for match in re.finditer(r"(?m)^\s*([a-z-]+):\s*write\s*$", low):
        if match.group(1) not in allowed_write:
            errors.append(f"unexpected write permission {match.group(1)}")
    if re.search(r"ref:\s*\$\{\{[^\n]*head_sha", low):
        errors.append("trusted workflow must never checkout PR head")
    return errors
