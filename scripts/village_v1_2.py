# SPDX-FileCopyrightText: 2026 AIMath contributors
# SPDX-License-Identifier: Apache-2.0
from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone, timedelta
from pathlib import Path, PurePosixPath
import json
import re
import secrets
from typing import Any, Iterable

from village_core import load_machine_file, parse_time, validate_schema
from village_rank import RankedTask, rank_ready_tasks

WORKER_ID_RE = re.compile(r"^w-[0-9a-f]{16,32}$")
TASK_ID_RE = re.compile(r"^TASK-[A-Z0-9-]+$")
SHA_RE = re.compile(r"^[0-9a-f]{40}$")
PRINCIPAL_RE = re.compile(r"^gh:[A-Za-z0-9_.-]+$")
RELEASE_HEAD_RE = re.compile(r"^release/(TASK-[A-Z0-9-]+)/(w-[0-9a-f]{16,32})$")
DEFAULT_PENDING_TTL_MINUTES = 60
PENDING_OBSERVATION_SOURCE = "GITHUB_API"
PENDING_REPOSITORY = "51mns/AIMath-public"
ABANDONED_REACQUIRE_COOLDOWN_HOURS = 24


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
    def from_values(cls, *, github_write=None, local_compute=None, web_literature=None) -> "CapabilityProfile":
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
class ReleaseBinding:
    task_id: str
    worker_id: str
    head_ref: str


@dataclass(frozen=True)
class V12RankedTask:
    base: RankedTask
    capability_fit: int

    @property
    def task_id(self) -> str:
        return self.base.task_id


def generate_worker_id() -> str:
    """Return non-secret session metadata; never use it as an authority credential."""
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


def parse_release_head_ref(head_ref: str | None) -> ReleaseBinding | None:
    if not isinstance(head_ref, str):
        return None
    match = RELEASE_HEAD_RE.fullmatch(head_ref)
    if not match:
        return None
    task_id, worker_id = match.groups()
    if len(task_id) > 96 or not validate_worker_id(worker_id):
        return None
    return ReleaseBinding(task_id=task_id, worker_id=worker_id, head_ref=head_ref)


def abandoned_terminal_path(task_id: str, worker_id: str) -> str:
    workspace = worker_workspace(task_id, worker_id)
    return workspace.owned_path.removesuffix("/**") + "/ABANDONED_TERMINAL.yml"


def result_terminal_path(task_id: str) -> str:
    if not TASK_ID_RE.fullmatch(task_id or "") or len(task_id) > 96:
        raise VillageV12Error(f"invalid/overlong task_id {task_id!r}")
    return f"coordination/outcomes/{task_id}.yml"


def load_actor_policy(root: Path | str) -> dict[str, Any]:
    path = Path(root) / "coordination/policy/ACTOR_POLICY.yml"
    if not path.is_file():
        return {}
    return json.loads(path.read_text(encoding="utf-8"))


def load_autonomous_lock_principals(root: Path | str) -> dict[str, Any]:
    path = Path(root) / "coordination/policy/AUTONOMOUS_LOCK_PRINCIPALS.yml"
    if not path.is_file():
        return {}
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return {}
    return value if isinstance(value, dict) else {}


def _worker_slot_key(payload: dict[str, Any]) -> tuple[str, str]:
    principal = payload.get("actor", {}).get("id", "")
    worker = payload.get("worker_id")
    return principal, worker if isinstance(worker, str) else "__legacy__"


def worker_lock_errors(state, actor_policy: dict[str, Any] | None = None) -> list[str]:
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
            errors.append(f"{principal}/{worker}: active EXCLUSIVE locks {count} exceed worker cap {cap}")
    return errors


def abandoned_terminal_schema_path(root: Path | str) -> Path:
    return Path(root) / "schemas/abandoned-terminal.schema.json"


def validate_abandoned_terminal_record(record: dict[str, Any], *, root: Path | str, expected_task_id=None, expected_worker_id=None) -> list[str]:
    errors: list[str] = []
    try:
        schema = json.loads(abandoned_terminal_schema_path(root).read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        return [f"abandoned terminal schema unavailable/invalid: {exc}"]
    errors.extend(validate_schema(record, schema, "ABANDONED_TERMINAL"))
    if expected_task_id is not None and record.get("task_id") != expected_task_id:
        errors.append("ABANDONED_TERMINAL task_id does not match requested Task")
    if expected_worker_id is not None and record.get("worker_id") != expected_worker_id:
        errors.append("ABANDONED_TERMINAL worker_id does not match requested worker")
    try:
        parse_time(str(record.get("abandoned_at", "")))
    except Exception:
        errors.append("ABANDONED_TERMINAL abandoned_at is invalid")
    last = record.get("last_work_head")
    if last is not None and (not isinstance(last, str) or not SHA_RE.fullmatch(last)):
        errors.append("ABANDONED_TERMINAL last_work_head must be null or a 40-hex SHA")
    if record.get("truth_layer_effect") != "NONE":
        errors.append("ABANDONED_TERMINAL truth_layer_effect must be NONE")
    return list(dict.fromkeys(errors))


def read_abandoned_terminal(root: Path | str, task_id: str, worker_id: str) -> tuple[dict[str, Any] | None, list[str]]:
    try:
        rel = abandoned_terminal_path(task_id, worker_id)
    except VillageV12Error as exc:
        return None, [str(exc)]
    path = Path(root) / rel
    if not path.exists():
        return None, []
    if path.is_symlink() or not path.is_file():
        return None, [f"{rel}: ABANDONED_TERMINAL must be a regular file"]
    try:
        record = load_machine_file(path)
    except Exception as exc:
        return None, [f"{rel}: malformed ABANDONED_TERMINAL: {exc}"]
    if not isinstance(record, dict):
        return None, [f"{rel}: ABANDONED_TERMINAL must be an object"]
    errors = validate_abandoned_terminal_record(record, root=root, expected_task_id=task_id, expected_worker_id=worker_id)
    return record, errors


def abandonment_state(root: Path | str, task_id: str, worker_id: str, *, now: datetime | None = None) -> dict[str, Any]:
    now = (now or datetime.now(timezone.utc)).astimezone(timezone.utc)
    record, errors = read_abandoned_terminal(root, task_id, worker_id)
    if errors:
        return {"state": "MALFORMED", "errors": errors, "abandonment_count": None, "cooldown_active": True}
    if record is None:
        return {"state": "NONE", "errors": [], "abandonment_count": 0, "cooldown_active": False}
    abandoned_at = parse_time(record["abandoned_at"])
    cooldown_until = abandoned_at + timedelta(hours=ABANDONED_REACQUIRE_COOLDOWN_HOURS)
    return {
        "state": "ABANDONED_TERMINAL", "errors": [], "abandonment_count": record["abandonment_count"],
        "reason": record["reason"], "abandoned_at": abandoned_at.isoformat(),
        "cooldown_until": cooldown_until.isoformat(), "cooldown_active": now < cooldown_until,
    }


def abandonment_cooldown_errors(base_state, task_id: str, worker_id: str) -> list[str]:
    state = abandonment_state(base_state.root, task_id, worker_id, now=base_state.now)
    if state["state"] == "MALFORMED":
        return ["same-(worker,task) abandonment state is malformed; reacquisition fails closed", *state["errors"]]
    if state.get("cooldown_active"):
        return ["same-(worker,task) reacquisition cooldown is active until " + str(state.get("cooldown_until"))]
    return []


def result_terminal_artifact_errors(root: Path | str, record: dict[str, Any]) -> list[str]:
    """A RESULT_TERMINAL may only cite evidence that is actually on the branch.

    A terminal outcome record is the gate that permits a lock RELEASE, so it must
    not be able to declare a Task finished by pointing at artifacts that were
    never merged. An empty artifact list stays legal: some terminal outcomes are
    purely scheduling statements.
    """
    errors: list[str] = []
    artifacts = record.get("artifacts")
    if not isinstance(artifacts, list):
        return errors
    base = Path(root)
    for item in artifacts:
        if not isinstance(item, str) or not item.strip():
            errors.append("RESULT_TERMINAL artifact entries must be non-empty strings")
            continue
        rel = PurePosixPath(item)
        if rel.is_absolute() or any(part in ("..", "") for part in rel.parts):
            errors.append(f"RESULT_TERMINAL artifact path must stay inside the repository: {item}")
            continue
        target = base / Path(*rel.parts)
        if target.is_symlink() or not target.is_file():
            errors.append(f"RESULT_TERMINAL cites an artifact missing from this branch: {item}")
    return errors


def result_terminal_errors(root: Path | str, task_id: str) -> tuple[bool, list[str]]:
    try:
        rel = result_terminal_path(task_id)
    except VillageV12Error as exc:
        return False, [str(exc)]
    path = Path(root) / rel
    if not path.exists():
        return False, []
    if path.is_symlink() or not path.is_file():
        return False, [f"{rel}: RESULT_TERMINAL must be a regular file"]
    try:
        record = load_machine_file(path)
        schema = json.loads((Path(root) / "schemas/outcome.schema.json").read_text(encoding="utf-8"))
    except Exception as exc:
        return False, [f"{rel}: malformed RESULT_TERMINAL: {exc}"]
    if not isinstance(record, dict):
        return False, [f"{rel}: RESULT_TERMINAL must be an object"]
    errors = validate_schema(record, schema, "RESULT_TERMINAL")
    if record.get("task_id") != task_id:
        errors.append("RESULT_TERMINAL task_id mismatch")
    errors.extend(result_terminal_artifact_errors(root, record))
    return not errors, list(dict.fromkeys(errors))


def release_terminal_state(root: Path | str, lock_payload: dict[str, Any], *, now: datetime) -> tuple[str, list[str]]:
    task_id = lock_payload.get("task_id")
    worker_id = lock_payload.get("worker_id")
    if not isinstance(task_id, str) or not TASK_ID_RE.fullmatch(task_id):
        return "NONE", ["canonical lock has invalid task_id"]
    if not isinstance(worker_id, str) or not validate_worker_id(worker_id):
        return "NONE", ["canonical lock lacks a valid worker_id for RELEASE"]
    result_ok, result_errors = result_terminal_errors(root, task_id)
    if result_ok:
        return "RESULT_TERMINAL", []
    abandoned, abandoned_errors = read_abandoned_terminal(root, task_id, worker_id)
    if abandoned is not None and not abandoned_errors:
        try:
            abandoned_at = parse_time(abandoned["abandoned_at"])
            acquired_at = parse_time(lock_payload["acquired_at"])
        except Exception as exc:
            return "NONE", [f"terminal timestamp validation failed: {exc}"]
        if abandoned_at < acquired_at:
            abandoned_errors.append("ABANDONED_TERMINAL predates this lock acquisition")
        if abandoned_at > now + timedelta(minutes=5):
            abandoned_errors.append("ABANDONED_TERMINAL is unreasonably in the future")
        if not abandoned_errors:
            return "ABANDONED_TERMINAL", []
    combined: list[str] = []
    if result_errors:
        combined.append("RESULT_TERMINAL invalid: " + "; ".join(result_errors))
    if abandoned_errors:
        combined.append("ABANDONED_TERMINAL invalid: " + "; ".join(abandoned_errors))
    if not combined:
        combined.append("no valid RESULT_TERMINAL or ABANDONED_TERMINAL exists on current main")
    return "NONE", combined


def new_worker_lock_errors(base_state, bundle, *, actor_policy: dict[str, Any] | None = None) -> list[str]:
    policy = actor_policy or {}
    required = bool(policy.get("worker_id_required_for_new_lock", False))
    worker_id = bundle.payload.get("worker_id")
    if required and not isinstance(worker_id, str):
        return ["v1.2 new lock acquisition requires worker_id"]
    if worker_id is None:
        return []
    if not validate_worker_id(str(worker_id)):
        return ["worker_id must match ^w-[0-9a-f]{16,32}$"]
    tid = bundle.payload.get("task_id")
    try:
        workspace = worker_workspace(tid, worker_id)
    except VillageV12Error as exc:
        return [str(exc)]
    errors: list[str] = []
    if bundle.payload.get("work_ref") != workspace.branch:
        errors.append(f"work_ref must equal deterministic worker branch {workspace.branch}")
    errors.extend(abandonment_cooldown_errors(base_state, tid, worker_id))
    cap = int(policy.get("exclusive_worker_lock_cap_default", 1))
    if base_state.tasks.get(tid, {}).get("parallelism") == "EXCLUSIVE":
        principal = bundle.payload.get("actor", {}).get("id")
        active = 0
        for old in base_state.active_lock_bundles():
            otid = old.payload.get("task_id")
            if base_state.tasks.get(otid, {}).get("parallelism") != "EXCLUSIVE":
                continue
            if old.payload.get("actor", {}).get("id") == principal and old.payload.get("worker_id") == worker_id:
                active += 1
        if active >= cap:
            errors.append(f"worker EXCLUSIVE lock cap {cap} already reached")
    return errors


def _pending_ttl_minutes(state) -> int:
    value = state.portfolio.get("governance", {}).get("pending_claim_ttl_minutes", DEFAULT_PENDING_TTL_MINUTES)
    try: value = int(value)
    except (TypeError, ValueError): return DEFAULT_PENDING_TTL_MINUTES
    return max(5, min(240, value))


def pending_schema_path() -> Path:
    return Path(__file__).resolve().parent.parent / "schemas/pending-claim.schema.json"


def validate_pending_claim_schema(record: dict[str, Any], schema_path: Path | None = None) -> list[str]:
    path = schema_path or pending_schema_path()
    try: schema = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc: return [f"pending claim schema unavailable/invalid: {exc}"]
    return validate_schema(record, schema, "PENDING_CLAIM")


def validate_pending_claim(state, record: dict[str, Any], *, current_main_sha: str, now: datetime | None = None) -> tuple[bool, list[str]]:
    now = (now or datetime.now(timezone.utc)).astimezone(timezone.utc)
    errors = validate_pending_claim_schema(record)
    if record.get("observation_source") != PENDING_OBSERVATION_SOURCE: errors.append("pending observation source is not direct GitHub API")
    if record.get("repository") != PENDING_REPOSITORY: errors.append("pending observation repository mismatch")
    if record.get("reservation_kind") != "PENDING_CLAIM": errors.append("reservation_kind must be PENDING_CLAIM")
    if record.get("pr_state") != "OPEN": errors.append("PR is not OPEN")
    if record.get("draft") is not False: errors.append("pending reservation requires draft=false boolean")
    if record.get("change_class") != "LOCK_ONLY": errors.append("change_class is not LOCK_ONLY")
    if record.get("lock_operation") != "ACQUIRE": errors.append("only lock ACQUIRE may reserve selection")
    if record.get("village_policy") != "PASS": errors.append("Village PR policy did not PASS")
    if record.get("verify_conclusion") != "SUCCESS": errors.append("required verify CI is not green")
    if record.get("base_main_sha") != current_main_sha: errors.append("pending PR base is stale")
    if not SHA_RE.fullmatch(str(record.get("head_sha", ""))): errors.append("invalid pending head_sha")
    pr_number = record.get("pr_number")
    if not isinstance(pr_number, int) or isinstance(pr_number, bool) or pr_number < 1: errors.append("invalid pr_number")
    principal_id = record.get("principal_id")
    if not isinstance(principal_id, str) or not PRINCIPAL_RE.fullmatch(principal_id): errors.append("invalid principal_id")
    worker_id = record.get("worker_id")
    if worker_id is not None and not validate_worker_id(str(worker_id)): errors.append("invalid worker_id")
    tid = record.get("task_id"); task = state.tasks.get(tid)
    if not task: errors.append("unknown pending task")
    else:
        if task.get("parallelism") != "EXCLUSIVE": errors.append("PENDING_CLAIM reservation is only for EXCLUSIVE tasks")
        keys = record.get("collision_keys")
        if not isinstance(keys, list) or set(keys) != set(task.get("collision_keys", [])): errors.append("pending collision_keys do not exactly match Task")
        ready, reasons = state.readiness(tid)
        if not ready: errors.append("task is no longer READY: " + "; ".join(reasons))
    try:
        observed = parse_time(record["observed_at"]); age = (now - observed).total_seconds() / 60
        if age < -5: errors.append("pending observation is from the future")
        if age > _pending_ttl_minutes(state): errors.append("pending observation expired; refresh GitHub PR/CI state")
    except Exception: errors.append("invalid observed_at")
    try:
        if parse_time(record["lock_expires_at"]) <= now: errors.append("proposed lock lease already expired")
    except Exception: errors.append("invalid lock_expires_at")
    return not errors, list(dict.fromkeys(errors))


def valid_pending_claims(state, records: Iterable[dict[str, Any]], *, current_main_sha: str, now: datetime | None = None) -> list[dict[str, Any]]:
    return [r for r in records if validate_pending_claim(state, r, current_main_sha=current_main_sha, now=now)[0]]


def task_has_pending_claim(state, task_id: str, records: Iterable[dict[str, Any]], *, current_main_sha: str, now: datetime | None = None) -> bool:
    task_keys = set(state.tasks[task_id].get("collision_keys", []))
    for record in valid_pending_claims(state, records, current_main_sha=current_main_sha, now=now):
        if record.get("task_id") == task_id or task_keys.intersection(record.get("collision_keys", [])): return True
    return False


def load_pending_claims(path: str | Path | None) -> list[dict[str, Any]]:
    if not path: return []
    try: value = json.loads(Path(path).read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc: raise VillageV12Error(f"invalid pending observation cache: {exc}") from exc
    if not isinstance(value, dict): raise VillageV12Error("pending observations require a GitHub API envelope object")
    allowed = {"schema_version", "observation_source", "repository", "reservations"}; extra = set(value) - allowed
    if extra: raise VillageV12Error(f"pending observation envelope has unexpected keys: {sorted(extra)}")
    if value.get("schema_version") != 1: raise VillageV12Error("pending observation envelope schema_version must be 1")
    if value.get("observation_source") != PENDING_OBSERVATION_SOURCE: raise VillageV12Error("pending observation cache must come from direct GitHub API observation")
    if value.get("repository") != PENDING_REPOSITORY: raise VillageV12Error(f"pending observation cache repository must be {PENDING_REPOSITORY}")
    rows = value.get("reservations")
    if not isinstance(rows, list) or not all(isinstance(x, dict) for x in rows): raise VillageV12Error("pending observation envelope requires reservations: [object, ...]")
    for i, record in enumerate(rows):
        errors = validate_pending_claim_schema(record)
        if errors: raise VillageV12Error(f"pending reservation #{i} failed schema: {'; '.join(errors)}")
        if record.get("observation_source") != PENDING_OBSERVATION_SOURCE or record.get("repository") != PENDING_REPOSITORY: raise VillageV12Error(f"pending reservation #{i} provenance mismatch")
    return rows


def capability_eligible(state, task_id: str, profile: CapabilityProfile | None) -> tuple[bool, str]:
    if profile is None or profile.is_unspecified(): return True, "UNSPECIFIED"
    if profile.github_write is False and state.tasks[task_id].get("parallelism") == "EXCLUSIVE": return False, "EXCLUSIVE lock acquisition requires GitHub write capability"
    return True, "ELIGIBLE"


def capability_fit(state, task_id: str, profile: CapabilityProfile | None) -> int:
    if profile is None or profile.is_unspecified(): return 0
    task = state.tasks[task_id]; kind = task.get("task_kind"); parallel = task.get("parallelism"); score = 0
    if profile.github_write is True and parallel == "EXCLUSIVE": score += 3
    if profile.github_write is False and parallel != "EXCLUSIVE": score += 2
    if profile.local_compute is True and kind in {"RESEARCH", "REPRODUCTION"}: score += 1
    if profile.web_literature is True and kind in {"LITERATURE_AUDIT", "FRONTIER_REFRESH"}: score += 2
    if profile.github_write is False and parallel == "PARALLEL_SAFE": score += 1
    return min(4, score)


def rank_v12(state, book, *, capabilities: CapabilityProfile | None = None, pending_records: Iterable[dict[str, Any]] = (), current_main_sha: str | None = None, now: datetime | None = None) -> list[V12RankedTask]:
    pending = list(pending_records)
    if pending and not current_main_sha: raise VillageV12Error("current_main_sha is required when pending reservations are supplied")
    rows: list[V12RankedTask] = []
    for row in rank_ready_tasks(state, book):
        eligible, _ = capability_eligible(state, row.task_id, capabilities)
        if not eligible: continue
        if pending and task_has_pending_claim(state, row.task_id, pending, current_main_sha=current_main_sha or "", now=now): continue
        rows.append(V12RankedTask(row, capability_fit(state, row.task_id, capabilities)))
    priority_order = {"P0": 0, "P1": 1, "P2": 2, "HOLD": 3}
    return sorted(rows, key=lambda x: (priority_order.get(x.base.priority, 9), -x.capability_fit, -x.base.score, x.base.task_id))


def trusted_lock_activation_workflow_errors(text: str) -> list[str]:
    from workflow_security import workflow_text_errors
    return workflow_text_errors(text, trusted_write=True)
