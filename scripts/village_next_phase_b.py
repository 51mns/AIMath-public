# SPDX-FileCopyrightText: 2026 AIMath contributors
# SPDX-License-Identifier: Apache-2.0
from __future__ import annotations

from dataclasses import asdict, dataclass, fields, is_dataclass
from datetime import datetime, timedelta, timezone
from pathlib import Path, PurePosixPath
from typing import Any, Callable, Iterable, Mapping, Sequence
import base64
import hashlib
import json
import os
import re
import subprocess
import urllib.error
import urllib.parse
import urllib.request

REPOSITORY = "51mns/AIMath-public"
VERIFY_WORKFLOW_ID = 347191396
VERIFY_WORKFLOW_PATH = ".github/workflows/verify.yml"
VERIFY_WORKFLOW_NAME = "Verify public release"
VERIFY_EVENT = "pull_request"
API_ROOT = "https://api.github.com"

TRUTH_AUTHORITY = frozenset()
REVIEW_AUTHORITY = frozenset()
FORBIDDEN_AUTOMATIC_OPERATIONS = frozenset({"RENEW", "TAKEOVER"})

SHA1_RE = re.compile(r"^[0-9a-f]{40}$")
SHA256_RE = re.compile(r"^[0-9a-f]{64}$")
TASK_RE = re.compile(r"^TASK-[A-Z0-9-]+$")
WORKER_RE = re.compile(r"^w-[0-9a-f]{16,32}$")
PRINCIPAL_RE = re.compile(r"^gh:[A-Za-z0-9_.-]+$")
LOCK_RE = re.compile(r"^LOCK-[A-Z0-9-]+$")


class PhaseBError(ValueError):
    def __init__(self, code: str, message: str):
        super().__init__(message)
        self.code = code
        self.message = message


@dataclass(frozen=True)
class GateResult:
    allowed: bool
    code: str
    detail: str = ""


@dataclass(frozen=True)
class SemanticIds:
    source_epoch_id: str
    continuation_context_id: str
    selection_id: str
    acquire_intent_id: str

    def to_dict(self) -> dict[str, str]:
        return asdict(self)


@dataclass(frozen=True)
class ExactLockObject:
    path: str
    mode: str
    blob_sha: str
    bytes_sha256: str

    def to_dict(self) -> dict[str, str]:
        return asdict(self)


@dataclass(frozen=True)
class CanonicalAcquireIdentityV3:
    schema_version: int
    source_epoch_id: str
    continuation_context_id: str
    selection_id: str
    acquire_intent_id: str
    expected_base_sha: str
    expected_canonical_tree_sha: str
    selected_task_id: str
    worker_id: str
    principal_id: str
    work_ref: str
    sorted_collision_keys: tuple[str, ...]
    lock_id: str
    acquired_at: str
    expires_at: str
    exact_lock_objects: tuple[ExactLockObject, ...]

    def semantic_ids(self) -> SemanticIds:
        return SemanticIds(
            self.source_epoch_id,
            self.continuation_context_id,
            self.selection_id,
            self.acquire_intent_id,
        )

    def to_dict(self) -> dict[str, Any]:
        return {
            "schema_version": self.schema_version,
            "source_epoch_id": self.source_epoch_id,
            "continuation_context_id": self.continuation_context_id,
            "selection_id": self.selection_id,
            "acquire_intent_id": self.acquire_intent_id,
            "expected_base_sha": self.expected_base_sha,
            "expected_canonical_tree_sha": self.expected_canonical_tree_sha,
            "selected_task_id": self.selected_task_id,
            "worker_id": self.worker_id,
            "principal_id": self.principal_id,
            "work_ref": self.work_ref,
            "sorted_collision_keys": list(self.sorted_collision_keys),
            "lock_id": self.lock_id,
            "acquired_at": self.acquired_at,
            "expires_at": self.expires_at,
            "exact_lock_objects": [x.to_dict() for x in self.exact_lock_objects],
        }

    @classmethod
    def from_dict(cls, value: Mapping[str, Any]) -> "CanonicalAcquireIdentityV3":
        try:
            objects = tuple(ExactLockObject(**dict(x)) for x in value["exact_lock_objects"])
            return cls(
                schema_version=value["schema_version"],
                source_epoch_id=value["source_epoch_id"],
                continuation_context_id=value["continuation_context_id"],
                selection_id=value["selection_id"],
                acquire_intent_id=value["acquire_intent_id"],
                expected_base_sha=value["expected_base_sha"],
                expected_canonical_tree_sha=value["expected_canonical_tree_sha"],
                selected_task_id=value["selected_task_id"],
                worker_id=value["worker_id"],
                principal_id=value["principal_id"],
                work_ref=value["work_ref"],
                sorted_collision_keys=tuple(value["sorted_collision_keys"]),
                lock_id=value["lock_id"],
                acquired_at=value["acquired_at"],
                expires_at=value["expires_at"],
                exact_lock_objects=objects,
            )
        except (KeyError, TypeError, ValueError) as exc:
            raise PhaseBError("CANONICAL_ACQUIRE_IDENTITY_MISMATCH", f"malformed V3 identity: {exc}") from exc

    def canonical_id(self) -> str:
        validate_v3_identity(self)
        return canonical_digest(self.to_dict())


@dataclass(frozen=True)
class FrozenAcquireMaterial:
    identity: CanonicalAcquireIdentityV3
    canonical_acquire_id: str
    lock_payload: dict[str, Any]
    lock_bytes: dict[str, bytes]


@dataclass(frozen=True)
class VerifyObservation:
    eligible: bool
    code: str
    authoritative_run_number: int | None = None
    run_id: int | None = None
    current_run_attempt: int | None = None
    status: str | None = None
    conclusion: str | None = None
    head_sha: str | None = None
    detail: str = ""


@dataclass(frozen=True)
class RulesetProof:
    passed: bool
    code: str
    detail: str = ""


# ---------- canonical encodings and exact Git identities ----------

def _plain(value: Any) -> Any:
    if is_dataclass(value):
        return {f.name: _plain(getattr(value, f.name)) for f in fields(value)}
    if isinstance(value, Mapping):
        return {str(k): _plain(v) for k, v in value.items()}
    if isinstance(value, (tuple, list)):
        return [_plain(v) for v in value]
    if isinstance(value, (set, frozenset)):
        return sorted(_plain(v) for v in value)
    if isinstance(value, datetime):
        return _format_time(value)
    return value


def canonical_bytes(value: Any) -> bytes:
    return json.dumps(
        _plain(value), sort_keys=True, separators=(",", ":"), ensure_ascii=False
    ).encode("utf-8")


def canonical_digest(value: Any) -> str:
    return hashlib.sha256(canonical_bytes(value)).hexdigest()


def git_blob_oid(raw: bytes) -> str:
    if not isinstance(raw, (bytes, bytearray)):
        raise TypeError("git_blob_oid requires bytes")
    raw = bytes(raw)
    return hashlib.sha1(b"blob " + str(len(raw)).encode("ascii") + b"\0" + raw).hexdigest()


def _git_object_oid(kind: str, raw: bytes) -> str:
    return hashlib.sha1(kind.encode("ascii") + b" " + str(len(raw)).encode("ascii") + b"\0" + raw).hexdigest()


def _safe_repo_path(path: str) -> bool:
    if not isinstance(path, str) or not path or "\\" in path or "\x00" in path:
        return False
    p = PurePosixPath(path)
    return not p.is_absolute() and all(part not in {"", ".", ".."} for part in p.parts)


def _normalise_leaf_entries(entries: Iterable[Mapping[str, Any]]) -> dict[str, tuple[str, str, str]]:
    out: dict[str, tuple[str, str, str]] = {}
    for row in entries:
        if not isinstance(row, Mapping):
            raise PhaseBError("CANONICAL_ACQUIRE_TREE_MISMATCH", "tree entry is not an object")
        path = row.get("path")
        mode = str(row.get("mode", ""))
        typ = str(row.get("type", ""))
        sha = row.get("sha")
        if typ == "tree":
            # Recursive GitHub trees contain directory rows. The root identity is
            # reconstructed from leaf objects, never trusted from those rows.
            continue
        if not isinstance(path, str) or not _safe_repo_path(path):
            raise PhaseBError("CANONICAL_ACQUIRE_TREE_MISMATCH", f"unsafe tree path {path!r}")
        if path in out:
            raise PhaseBError("CANONICAL_ACQUIRE_TREE_MISMATCH", f"duplicate tree path {path}")
        if typ not in {"blob", "commit"} or not isinstance(sha, str) or not SHA1_RE.fullmatch(sha):
            raise PhaseBError("CANONICAL_ACQUIRE_TREE_MISMATCH", f"malformed leaf tree entry {path}")
        if typ == "blob" and mode not in {"100644", "100755", "120000"}:
            raise PhaseBError("CANONICAL_ACQUIRE_TREE_MISMATCH", f"unsupported blob mode {mode}: {path}")
        if typ == "commit" and mode != "160000":
            raise PhaseBError("CANONICAL_ACQUIRE_TREE_MISMATCH", f"unsupported commit mode {mode}: {path}")
        out[path] = (mode, typ, sha)
    return out


def _root_tree_sha_from_leaves(leaves: Mapping[str, tuple[str, str, str]]) -> str:
    root: dict[str, Any] = {}
    for path, meta in leaves.items():
        parts = path.split("/")
        node = root
        for part in parts[:-1]:
            existing = node.get(part)
            if existing is None:
                existing = {"__dir__": True, "children": {}}
                node[part] = existing
            if not isinstance(existing, dict) or not existing.get("__dir__"):
                raise PhaseBError("CANONICAL_ACQUIRE_TREE_MISMATCH", f"path prefix collision at {path}")
            node = existing["children"]
        name = parts[-1]
        if name in node:
            raise PhaseBError("CANONICAL_ACQUIRE_TREE_MISMATCH", f"duplicate tree name at {path}")
        node[name] = {"__dir__": False, "meta": meta}

    def emit(node: dict[str, Any]) -> str:
        prepared: list[tuple[str, bool, str, str]] = []
        for name, item in node.items():
            if item["__dir__"]:
                sha = emit(item["children"])
                prepared.append((name, True, "40000", sha))
            else:
                mode, _typ, sha = item["meta"]
                prepared.append((name, False, mode, sha))
        prepared.sort(key=lambda x: (x[0] + ("/" if x[1] else "")).encode("utf-8"))
        content = bytearray()
        for name, _is_dir, mode, sha in prepared:
            content.extend(mode.encode("ascii"))
            content.extend(b" ")
            content.extend(name.encode("utf-8"))
            content.extend(b"\0")
            content.extend(bytes.fromhex(sha))
        return _git_object_oid("tree", bytes(content))

    return emit(root)


def deterministic_tree_sha(
    entries: Iterable[Mapping[str, Any]],
    *,
    additions: Iterable[Mapping[str, Any]] = (),
    deletions: Iterable[str] = (),
    expected_base_tree_sha: str | None = None,
) -> str:
    leaves = _normalise_leaf_entries(entries)
    before = _root_tree_sha_from_leaves(leaves)
    if expected_base_tree_sha is not None and before != expected_base_tree_sha:
        raise PhaseBError(
            "CANONICAL_ACQUIRE_TREE_MISMATCH",
            f"base tree reconstruction {before} != expected {expected_base_tree_sha}",
        )
    for path in deletions:
        if path not in leaves:
            raise PhaseBError("CANONICAL_ACQUIRE_DELTA_MISMATCH", f"cannot delete absent path {path}")
        del leaves[path]
    for row in additions:
        one = _normalise_leaf_entries([row])
        path, meta = next(iter(one.items()))
        leaves[path] = meta
    return _root_tree_sha_from_leaves(leaves)


# ---------- V3 semantic and lock material ----------

def _format_time(value: datetime) -> str:
    if not isinstance(value, datetime) or value.tzinfo is None:
        raise PhaseBError("CANONICAL_ACQUIRE_IDENTITY_MISMATCH", "timestamp must be timezone-aware")
    value = value.astimezone(timezone.utc)
    if value.microsecond:
        raise PhaseBError("CANONICAL_ACQUIRE_IDENTITY_MISMATCH", "timestamp must have whole-second precision")
    return value.isoformat()


def _parse_time(value: str) -> datetime:
    if not isinstance(value, str):
        raise ValueError("time is not a string")
    s = value[:-1] + "+00:00" if value.endswith("Z") else value
    d = datetime.fromisoformat(s)
    if d.tzinfo is None:
        raise ValueError("time has no timezone")
    return d.astimezone(timezone.utc)


def _validate_semantic_ids(ids: SemanticIds) -> None:
    for name, value in ids.to_dict().items():
        if not isinstance(value, str) or not SHA256_RE.fullmatch(value):
            raise PhaseBError("CANONICAL_ACQUIRE_SEMANTIC_BINDING_INCONSISTENT", f"invalid {name}")


def _lock_path_for_collision(key: str) -> str:
    if not isinstance(key, str) or not key or key.startswith("/") or key.endswith("/"):
        raise PhaseBError("CANONICAL_ACQUIRE_IDENTITY_MISMATCH", f"invalid collision key {key!r}")
    path = f"coordination/locks/{key}.yml"
    if not _safe_repo_path(path):
        raise PhaseBError("CANONICAL_ACQUIRE_IDENTITY_MISMATCH", f"unsafe collision key {key!r}")
    return path


def deterministic_lock_id(acquire_intent_id: str) -> str:
    if not isinstance(acquire_intent_id, str) or not SHA256_RE.fullmatch(acquire_intent_id):
        raise PhaseBError("CANONICAL_ACQUIRE_IDENTITY_MISMATCH", "invalid acquire_intent_id")
    return "LOCK-NEXT-" + acquire_intent_id[:32].upper()


def deterministic_acquire_ref(acquire_intent_id: str, task_id: str, worker_id: str) -> str:
    deterministic_lock_id(acquire_intent_id)
    if not TASK_RE.fullmatch(task_id or "") or not WORKER_RE.fullmatch(worker_id or ""):
        raise PhaseBError("CANONICAL_ACQUIRE_IDENTITY_MISMATCH", "invalid task/worker for acquire ref")
    return f"next-acquire/{acquire_intent_id}/{task_id}/{worker_id}"


def deterministic_release_ref(task_id: str, worker_id: str) -> str:
    if not TASK_RE.fullmatch(task_id or "") or not WORKER_RE.fullmatch(worker_id or ""):
        raise PhaseBError("SOURCE_EPOCH_UNPROVEN", "invalid task/worker for release ref")
    return f"release/{task_id}/{worker_id}"


def _lock_payload_bytes(payload: Mapping[str, Any]) -> bytes:
    return (json.dumps(_plain(payload), sort_keys=True, indent=2, ensure_ascii=False) + "\n").encode("utf-8")


def validate_v3_identity(identity: CanonicalAcquireIdentityV3) -> CanonicalAcquireIdentityV3:
    if not isinstance(identity, CanonicalAcquireIdentityV3) or identity.schema_version != 3:
        raise PhaseBError("CANONICAL_ACQUIRE_IDENTITY_MISMATCH", "V3 schema_version must be 3")
    _validate_semantic_ids(identity.semantic_ids())
    if not SHA1_RE.fullmatch(identity.expected_base_sha or ""):
        raise PhaseBError("CANONICAL_ACQUIRE_BASE_MISMATCH", "invalid expected base SHA")
    if not SHA1_RE.fullmatch(identity.expected_canonical_tree_sha or ""):
        raise PhaseBError("CANONICAL_ACQUIRE_TREE_MISMATCH", "invalid expected tree SHA")
    if not TASK_RE.fullmatch(identity.selected_task_id or ""):
        raise PhaseBError("CANONICAL_ACQUIRE_IDENTITY_MISMATCH", "invalid selected task")
    if not WORKER_RE.fullmatch(identity.worker_id or ""):
        raise PhaseBError("CANONICAL_ACQUIRE_IDENTITY_MISMATCH", "invalid worker")
    if not PRINCIPAL_RE.fullmatch(identity.principal_id or ""):
        raise PhaseBError("CANONICAL_ACQUIRE_IDENTITY_MISMATCH", "invalid principal")
    expected_work_ref = f"research/{identity.selected_task_id}/{identity.worker_id}"
    if identity.work_ref != expected_work_ref:
        raise PhaseBError("CANONICAL_ACQUIRE_IDENTITY_MISMATCH", "work_ref is not deterministic worker workspace")
    collisions = tuple(identity.sorted_collision_keys)
    if not collisions or collisions != tuple(sorted(set(collisions))):
        raise PhaseBError("CANONICAL_ACQUIRE_IDENTITY_MISMATCH", "collision keys must be sorted and unique")
    if identity.lock_id != deterministic_lock_id(identity.acquire_intent_id):
        raise PhaseBError("CANONICAL_ACQUIRE_IDENTITY_MISMATCH", "lock_id does not match acquire intent")
    try:
        acquired = _parse_time(identity.acquired_at)
        expires = _parse_time(identity.expires_at)
    except Exception as exc:
        raise PhaseBError("CANONICAL_ACQUIRE_IDENTITY_MISMATCH", f"invalid lock timestamp: {exc}") from exc
    if expires <= acquired:
        raise PhaseBError("CANONICAL_ACQUIRE_IDENTITY_MISMATCH", "expires_at must follow acquired_at")
    paths = [o.path for o in identity.exact_lock_objects]
    if len(paths) != len(set(paths)):
        raise PhaseBError("CANONICAL_ACQUIRE_DUPLICATE_LOCK_PATH", "exact_lock_objects contains duplicate path")
    if tuple(paths) != tuple(sorted(paths)):
        raise PhaseBError("CANONICAL_ACQUIRE_IDENTITY_MISMATCH", "exact_lock_objects must be path-sorted")
    expected_paths = tuple(_lock_path_for_collision(k) for k in collisions)
    if tuple(paths) != expected_paths:
        raise PhaseBError("CANONICAL_ACQUIRE_IDENTITY_MISMATCH", "lock path set does not equal collision bundle")
    for obj in identity.exact_lock_objects:
        if obj.mode != "100644":
            raise PhaseBError("CANONICAL_ACQUIRE_IDENTITY_MISMATCH", f"lock mode must be 100644: {obj.path}")
        if not SHA1_RE.fullmatch(obj.blob_sha or "") or not SHA256_RE.fullmatch(obj.bytes_sha256 or ""):
            raise PhaseBError("CANONICAL_ACQUIRE_IDENTITY_MISMATCH", f"invalid object digest: {obj.path}")
    return identity


def freeze_acquire_material(
    *,
    semantic_ids: SemanticIds,
    base_sha: str,
    base_tree_sha: str,
    base_tree_entries: Sequence[Mapping[str, Any]],
    selected_task_id: str,
    worker_id: str,
    principal_id: str,
    work_ref: str,
    collision_keys: Iterable[str],
    acquired_at: datetime,
    lease_ttl_hours: int,
) -> FrozenAcquireMaterial:
    _validate_semantic_ids(semantic_ids)
    if not SHA1_RE.fullmatch(base_sha or ""):
        raise PhaseBError("CANONICAL_ACQUIRE_BASE_MISMATCH", "invalid selection base SHA")
    if not isinstance(lease_ttl_hours, int) or isinstance(lease_ttl_hours, bool) or lease_ttl_hours <= 0:
        raise PhaseBError("CANONICAL_ACQUIRE_IDENTITY_MISMATCH", "lease_ttl_hours must be positive integer")
    collisions = tuple(sorted(set(collision_keys)))
    if not collisions:
        raise PhaseBError("CANONICAL_ACQUIRE_IDENTITY_MISMATCH", "collision bundle is empty")
    if len(collisions) > 16:
        raise PhaseBError("ACQUIRE_TRANSPORT_INCOMPATIBLE", "collision bundle exceeds trusted lifecycle 16-lock transport bound")
    if work_ref != f"research/{selected_task_id}/{worker_id}":
        raise PhaseBError("CANONICAL_ACQUIRE_IDENTITY_MISMATCH", "work_ref mismatch")
    # This verifies Tree(B) before any candidate exists.
    deterministic_tree_sha(base_tree_entries, expected_base_tree_sha=base_tree_sha)
    base_paths = set(_normalise_leaf_entries(base_tree_entries))
    lock_paths = tuple(_lock_path_for_collision(k) for k in collisions)
    overlap = base_paths.intersection(lock_paths)
    if overlap:
        raise PhaseBError("CANONICAL_ACQUIRE_DELTA_MISMATCH", f"expected ACQUIRE path already exists at B: {sorted(overlap)}")

    acquired_text = _format_time(acquired_at)
    expires_text = _format_time(acquired_at.astimezone(timezone.utc) + timedelta(hours=lease_ttl_hours))
    binding = {"schema_version": 1, **semantic_ids.to_dict()}
    payload = {
        "schema_version": 1,
        "lock_id": deterministic_lock_id(semantic_ids.acquire_intent_id),
        "task_id": selected_task_id,
        "worker_id": worker_id,
        "actor": {"id": principal_id, "type": "HUMAN_PRINCIPAL"},
        "base_main_sha": base_sha,
        "acquired_at": acquired_text,
        "expires_at": expires_text,
        "work_ref": work_ref,
        "collision_keys": list(collisions),
        "renewal_count": 0,
        "next_binding": binding,
    }
    raw = _lock_payload_bytes(payload)
    raw_sha = hashlib.sha256(raw).hexdigest()
    blob_sha = git_blob_oid(raw)
    lock_bytes = {path: raw for path in lock_paths}
    objects = tuple(
        ExactLockObject(path=path, mode="100644", blob_sha=blob_sha, bytes_sha256=raw_sha)
        for path in lock_paths
    )
    additions = [
        {"path": obj.path, "mode": obj.mode, "type": "blob", "sha": obj.blob_sha}
        for obj in objects
    ]
    tree_sha = deterministic_tree_sha(
        base_tree_entries,
        additions=additions,
        expected_base_tree_sha=base_tree_sha,
    )
    identity = CanonicalAcquireIdentityV3(
        schema_version=3,
        source_epoch_id=semantic_ids.source_epoch_id,
        continuation_context_id=semantic_ids.continuation_context_id,
        selection_id=semantic_ids.selection_id,
        acquire_intent_id=semantic_ids.acquire_intent_id,
        expected_base_sha=base_sha,
        expected_canonical_tree_sha=tree_sha,
        selected_task_id=selected_task_id,
        worker_id=worker_id,
        principal_id=principal_id,
        work_ref=work_ref,
        sorted_collision_keys=collisions,
        lock_id=payload["lock_id"],
        acquired_at=acquired_text,
        expires_at=expires_text,
        exact_lock_objects=objects,
    )
    validate_v3_identity(identity)
    return FrozenAcquireMaterial(identity, identity.canonical_id(), payload, lock_bytes)


def parse_next_binding(payload: Mapping[str, Any]) -> SemanticIds:
    if "next_binding" not in payload:
        raise PhaseBError("CANONICAL_ACQUIRE_NEXT_BINDING_MISSING", "v1.3 /next lock lacks next_binding")
    binding = payload.get("next_binding")
    required = {"schema_version", "source_epoch_id", "continuation_context_id", "selection_id", "acquire_intent_id"}
    if not isinstance(binding, Mapping) or set(binding) != required or binding.get("schema_version") != 1:
        raise PhaseBError("CANONICAL_ACQUIRE_NEXT_BINDING_MALFORMED", "malformed next_binding")
    ids = SemanticIds(
        str(binding.get("source_epoch_id", "")),
        str(binding.get("continuation_context_id", "")),
        str(binding.get("selection_id", "")),
        str(binding.get("acquire_intent_id", "")),
    )
    _validate_semantic_ids(ids)
    return ids


def reconstruct_v3_from_lock_payload(identity: CanonicalAcquireIdentityV3, payload: Mapping[str, Any]) -> GateResult:
    try:
        validate_v3_identity(identity)
        ids = parse_next_binding(payload)
    except PhaseBError as exc:
        return GateResult(False, exc.code, exc.message)
    if ids != identity.semantic_ids():
        return GateResult(False, "CANONICAL_ACQUIRE_SEMANTIC_BINDING_INCONSISTENT", "canonical next_binding differs from expected V3")
    checks = {
        "task_id": identity.selected_task_id,
        "worker_id": identity.worker_id,
        "base_main_sha": identity.expected_base_sha,
        "work_ref": identity.work_ref,
        "lock_id": identity.lock_id,
        "acquired_at": identity.acquired_at,
        "expires_at": identity.expires_at,
        "renewal_count": 0,
    }
    for key, expected in checks.items():
        if payload.get(key) != expected:
            return GateResult(False, "CANONICAL_ACQUIRE_IDENTITY_MISMATCH", f"lock payload {key} mismatch")
    actor = payload.get("actor")
    if not isinstance(actor, Mapping) or actor.get("id") != identity.principal_id:
        return GateResult(False, "CANONICAL_ACQUIRE_IDENTITY_MISMATCH", "lock principal mismatch")
    if tuple(payload.get("collision_keys", ())) != identity.sorted_collision_keys:
        return GateResult(False, "CANONICAL_ACQUIRE_IDENTITY_MISMATCH", "lock collision bundle mismatch")
    return GateResult(True, "CANONICAL_ACQUIRE_SEMANTIC_RECONSTRUCTED", "exact V3 semantics reconstructed from lock payload")


def _objects_as_tuple(objects: Iterable[ExactLockObject | Mapping[str, Any]]) -> tuple[ExactLockObject, ...]:
    out = []
    for obj in objects:
        out.append(obj if isinstance(obj, ExactLockObject) else ExactLockObject(**dict(obj)))
    return tuple(out)


def candidate_content_gate(
    *,
    expected_identity: CanonicalAcquireIdentityV3,
    independently_derived_ids: SemanticIds,
    candidate_lock_bytes: Mapping[str, bytes],
    candidate_exact_objects: Iterable[ExactLockObject | Mapping[str, Any]],
    candidate_tree_sha: str,
) -> GateResult:
    """Validate exact candidate content against one supplied semantic identity.

    Ordering is intentional: the candidate first proves internal bytes/OID/hash
    consistency. Only then are its persisted semantic primitives compared with
    the supplied IDs. A contradiction at this content layer is INCONSISTENT;
    premerge_transport_gate separately compares a proven internal identity with
    independently frozen trusted IDs and reports the Row-20 MISMATCH boundary.
    """
    try:
        validate_v3_identity(expected_identity)
        _validate_semantic_ids(independently_derived_ids)
        objects = _objects_as_tuple(candidate_exact_objects)
        paths = [o.path for o in objects]
        if len(paths) != len(set(paths)):
            raise PhaseBError("CANONICAL_ACQUIRE_DUPLICATE_LOCK_PATH", "candidate object paths duplicate")
        if tuple(paths) != tuple(sorted(paths)):
            raise PhaseBError("CANONICAL_ACQUIRE_IDENTITY_MISMATCH", "candidate object paths unsorted")
        if set(candidate_lock_bytes) != set(paths):
            raise PhaseBError("CANONICAL_ACQUIRE_DELTA_MISMATCH", "candidate bytes/path set mismatch")
        parsed_ids: SemanticIds | None = None
        parsed_payload: Mapping[str, Any] | None = None
        for obj in objects:
            raw = candidate_lock_bytes[obj.path]
            if obj.mode != "100644" or git_blob_oid(raw) != obj.blob_sha or hashlib.sha256(raw).hexdigest() != obj.bytes_sha256:
                raise PhaseBError("CANONICAL_ACQUIRE_TREE_MISMATCH", f"candidate object digest mismatch: {obj.path}")
            try:
                payload = json.loads(raw.decode("utf-8"))
            except Exception as exc:
                raise PhaseBError("CANONICAL_ACQUIRE_NEXT_BINDING_MALFORMED", f"candidate lock JSON invalid: {exc}") from exc
            ids = parse_next_binding(payload)
            if parsed_ids is None:
                parsed_ids, parsed_payload = ids, payload
            elif ids != parsed_ids or payload != parsed_payload:
                raise PhaseBError("CANONICAL_ACQUIRE_SEMANTIC_BINDING_INCONSISTENT", "collision-key lock copies are not semantically identical")
        if parsed_ids is None:
            raise PhaseBError("CANONICAL_ACQUIRE_DELTA_MISMATCH", "candidate has no lock objects")
    except PhaseBError as exc:
        return GateResult(False, exc.code, exc.message)

    if parsed_ids != independently_derived_ids or expected_identity.semantic_ids() != independently_derived_ids:
        return GateResult(
            False,
            "CANONICAL_ACQUIRE_SEMANTIC_BINDING_INCONSISTENT",
            "candidate canonical bytes/identity contradict the supplied semantic IDs",
        )
    if tuple(objects) != expected_identity.exact_lock_objects:
        return GateResult(False, "CANONICAL_ACQUIRE_IDENTITY_MISMATCH", "candidate exact lock objects differ from expected V3")
    if candidate_tree_sha != expected_identity.expected_canonical_tree_sha:
        return GateResult(False, "CANONICAL_ACQUIRE_TREE_MISMATCH", "candidate tree differs from precomputed T")
    recon = reconstruct_v3_from_lock_payload(expected_identity, parsed_payload or {})
    if not recon.allowed:
        return recon
    return GateResult(True, "TRANSPORT_CANDIDATE_CONTENT_CONFIRMED", "candidate content equals independently frozen V3")


# ---------- trusted upstream identity derivation ----------

def _sorted_blob_bundle(rows: Iterable[Mapping[str, Any]]) -> list[dict[str, str]]:
    out: list[dict[str, str]] = []
    seen: set[str] = set()
    for row in rows:
        path = row.get("path")
        sha = row.get("blob_sha")
        if not isinstance(path, str) or not _safe_repo_path(path) or path in seen or not isinstance(sha, str) or not SHA1_RE.fullmatch(sha):
            raise PhaseBError("SOURCE_EPOCH_UNPROVEN", "malformed/duplicate source lock blob bundle")
        seen.add(path)
        out.append({"path": path, "blob_sha": sha})
    return sorted(out, key=lambda x: x["path"])


def derive_source_acquisition_v1(
    *, repository: str, source_task_id: str, worker_id: str, principal_id: str,
    lock_payload: Mapping[str, Any], source_lock_blob_bundle: Iterable[Mapping[str, Any]],
    terminal_class: str, terminal_path: str, terminal_blob_sha: str,
    terminal_outcome_type: str | None,
) -> tuple[dict[str, Any], str]:
    if repository != REPOSITORY:
        raise PhaseBError("SOURCE_EPOCH_UNPROVEN", "repository namespace mismatch")
    if lock_payload.get("task_id") != source_task_id or lock_payload.get("worker_id") != worker_id:
        raise PhaseBError("SOURCE_EPOCH_UNPROVEN", "source Task/worker mismatch")
    actor = lock_payload.get("actor", {})
    if not isinstance(actor, Mapping) or actor.get("id") != principal_id:
        raise PhaseBError("SOURCE_EPOCH_UNPROVEN", "source principal mismatch")
    if terminal_class not in {"RESULT_TERMINAL", "ABANDONED_TERMINAL"}:
        raise PhaseBError("SOURCE_EPOCH_UNPROVEN", "invalid terminal class")
    if not SHA1_RE.fullmatch(terminal_blob_sha or "") or not _safe_repo_path(terminal_path):
        raise PhaseBError("SOURCE_EPOCH_UNPROVEN", "invalid terminal object")
    collisions = tuple(sorted(set(lock_payload.get("collision_keys", []))))
    record = {
        "repository": repository,
        "source_task_id": source_task_id,
        "worker_id": worker_id,
        "principal_id": principal_id,
        "source_lock_id": lock_payload.get("lock_id"),
        "source_lock_acquired_at": lock_payload.get("acquired_at"),
        "source_lock_base_main_sha": lock_payload.get("base_main_sha"),
        "source_work_ref": lock_payload.get("work_ref"),
        "source_collision_keys": list(collisions),
        "source_lock_blob_bundle": _sorted_blob_bundle(source_lock_blob_bundle),
        "terminal_class": terminal_class,
        "terminal_path": terminal_path,
        "terminal_blob_sha": terminal_blob_sha,
        "terminal_outcome_type": terminal_outcome_type,
    }
    return record, canonical_digest(record)


def _capability_dict(profile: Any) -> dict[str, Any]:
    return {
        "github_write": getattr(profile, "github_write", None),
        "local_compute": getattr(profile, "local_compute", None),
        "web_literature": getattr(profile, "web_literature", None),
    }


def derive_continuation_context_v1(
    *, source_epoch_id: str, selection_main_sha: str, terminal_class: str,
    terminal_blob_sha: str, source_campaign_id: str, global_admission: str,
    source_campaign_strategic_state: str, continuation_gate_required: bool,
    continuation_decision_id: str | None, continuation_decision_blob_sha: str | None,
    human_decision: str | None, canonical_stop_condition_reached: bool,
    canonical_dependency_followup_unusable: bool, same_campaign_allowed: bool,
    global_fallback_allowed: bool, approved_followup_task_ids: Iterable[str],
    evaluation_followup_task_ids: Iterable[str], reasons: Iterable[str], capability_profile: Any,
) -> tuple[dict[str, Any], str]:
    if not SHA256_RE.fullmatch(source_epoch_id or "") or not SHA1_RE.fullmatch(selection_main_sha or ""):
        raise PhaseBError("CANONICAL_ACQUIRE_SEMANTIC_BINDING_INCONSISTENT", "invalid source/context base identity")
    record = {
        "source_epoch_id": source_epoch_id,
        "selection_main_sha": selection_main_sha,
        "terminal_class": terminal_class,
        "terminal_blob_sha": terminal_blob_sha,
        "source_campaign_id": source_campaign_id,
        "global_admission": global_admission,
        "source_campaign_strategic_state": source_campaign_strategic_state,
        "continuation_gate_required": bool(continuation_gate_required),
        "continuation_decision_id": continuation_decision_id,
        "continuation_decision_blob_sha": continuation_decision_blob_sha,
        "human_decision": human_decision,
        "canonical_stop_condition_reached": bool(canonical_stop_condition_reached),
        "canonical_dependency_followup_unusable": bool(canonical_dependency_followup_unusable),
        "same_campaign_allowed": bool(same_campaign_allowed),
        "global_fallback_allowed": bool(global_fallback_allowed),
        "approved_followup_task_ids": sorted(set(approved_followup_task_ids)),
        "evaluation_followup_task_ids": sorted(set(evaluation_followup_task_ids)),
        "reasons": list(reasons),
        "capability_profile": _capability_dict(capability_profile),
    }
    return record, canonical_digest(record)


def _normalise_pending_record(row: Mapping[str, Any]) -> dict[str, Any]:
    # Bind all scheduling-relevant direct-GitHub reservation fields without
    # inventing authority for unknown keys.
    keys = (
        "pr_number", "head_sha", "base_main_sha", "task_id", "worker_id",
        "principal_id", "collision_keys", "verify_conclusion", "verify_run_number",
        "verify_run_attempt", "pr_state", "draft",
    )
    out = {k: _plain(row.get(k)) for k in keys if k in row}
    if isinstance(out.get("collision_keys"), list):
        out["collision_keys"] = sorted(out["collision_keys"])
    return out


def derive_selection_v1(
    *, source_epoch_id: str, selection_main_sha: str, continuation_context_id: str,
    pending_records: Iterable[Mapping[str, Any]], hard_eligible_task_ids: Iterable[str],
    ranked_task_ids: Iterable[str], selected_task_id: str, selected_relation: str,
    worker_id: str, principal_id: str,
) -> tuple[dict[str, Any], str]:
    normal_pending = sorted(
        (_normalise_pending_record(x) for x in pending_records),
        key=lambda x: (int(x.get("pr_number", 0)), str(x.get("head_sha", ""))),
    )
    record = {
        "source_epoch_id": source_epoch_id,
        "selection_main_sha": selection_main_sha,
        "continuation_context_id": continuation_context_id,
        "pending_observation_digest": canonical_digest(normal_pending),
        "hard_eligible_task_ids": sorted(set(hard_eligible_task_ids)),
        "ranked_task_ids": list(ranked_task_ids),
        "selected_task_id": selected_task_id,
        "selected_relation": selected_relation,
        "worker_id": worker_id,
        "principal_id": principal_id,
    }
    return record, canonical_digest(record)


def derive_acquire_intent_v1(
    *, source_epoch_id: str, selection_id: str, selection_main_sha: str,
    continuation_context_id: str, selected_task_id: str, worker_id: str,
    principal_id: str, work_ref: str, collision_keys: Iterable[str],
) -> tuple[dict[str, Any], str]:
    record = {
        "repository": REPOSITORY,
        "source_epoch_id": source_epoch_id,
        "selection_id": selection_id,
        "selection_main_sha": selection_main_sha,
        "continuation_context_id": continuation_context_id,
        "selected_task_id": selected_task_id,
        "worker_id": worker_id,
        "principal_id": principal_id,
        "work_ref": work_ref,
        "collision_keys": sorted(set(collision_keys)),
    }
    return record, canonical_digest(record)


def validate_retained_state_chain(state: Mapping[str, Any]) -> bool:
    try:
        if state.get("schema_version") != 1 or state.get("repository") != REPOSITORY:
            raise PhaseBError("RETAINED_STATE_INVALID", "state header mismatch")
        src = state["source_acquisition_v1"]
        src_id = canonical_digest(src)
        if state.get("source_epoch_id") != src_id:
            raise PhaseBError("RETAINED_STATE_INVALID", "source epoch digest mismatch")
        ctx = state["continuation_context_v1"]
        ctx_id = canonical_digest(ctx)
        if ctx.get("source_epoch_id") != src_id or state.get("continuation_context_id") != ctx_id:
            raise PhaseBError("RETAINED_STATE_INVALID", "continuation context chain mismatch")
        sel = state["selection_v1"]
        sel_id = canonical_digest(sel)
        if sel.get("source_epoch_id") != src_id or sel.get("continuation_context_id") != ctx_id or state.get("selection_id") != sel_id:
            raise PhaseBError("RETAINED_STATE_INVALID", "selection chain mismatch")
        intent = state["acquire_intent_v1"]
        intent_id = canonical_digest(intent)
        if (
            intent.get("source_epoch_id") != src_id
            or intent.get("continuation_context_id") != ctx_id
            or intent.get("selection_id") != sel_id
            or state.get("acquire_intent_id") != intent_id
        ):
            raise PhaseBError("RETAINED_STATE_INVALID", "acquire-intent chain mismatch")
        identity = CanonicalAcquireIdentityV3.from_dict(state["canonical_acquire_identity_v3"])
        validate_v3_identity(identity)
        if identity.semantic_ids() != SemanticIds(src_id, ctx_id, sel_id, intent_id):
            raise PhaseBError("RETAINED_STATE_INVALID", "V3 semantic IDs differ from retained trusted chain")
        if state.get("canonical_acquire_id") != identity.canonical_id():
            raise PhaseBError("RETAINED_STATE_INVALID", "canonical_acquire_id mismatch")
        return True
    except KeyError as exc:
        raise PhaseBError("RETAINED_STATE_INVALID", f"retained state missing {exc}") from exc


# ---------- Verify and Ruleset fail-closed proof ----------

def _run_identity_matches(row: Mapping[str, Any], head_sha: str) -> bool:
    return (
        row.get("workflow_id") == VERIFY_WORKFLOW_ID
        and row.get("path") == VERIFY_WORKFLOW_PATH
        and row.get("name") == VERIFY_WORKFLOW_NAME
        and row.get("event") == VERIFY_EVENT
        and row.get("head_sha") == head_sha
    )


def authoritative_verify_lineage(
    rows: Sequence[Mapping[str, Any]], *, head_sha: str, complete: bool,
    fetch_current_run: Callable[[int], Mapping[str, Any]],
) -> VerifyObservation:
    if not complete:
        return VerifyObservation(False, "VERIFY_RUNSET_INCOMPLETE", head_sha=head_sha, detail="workflow observation completeness unproven")
    if not SHA1_RE.fullmatch(head_sha or ""):
        return VerifyObservation(False, "VERIFY_RUNSET_MALFORMED", head_sha=head_sha, detail="invalid exact head SHA")
    matching: list[Mapping[str, Any]] = []
    seen_numbers: dict[int, Mapping[str, Any]] = {}
    try:
        for row in rows:
            if not isinstance(row, Mapping):
                return VerifyObservation(False, "VERIFY_RUNSET_MALFORMED", head_sha=head_sha)
            if not _run_identity_matches(row, head_sha):
                continue
            number = row.get("run_number")
            run_id = row.get("id")
            if not isinstance(number, int) or isinstance(number, bool) or number < 1 or not isinstance(run_id, int) or isinstance(run_id, bool) or run_id < 1:
                return VerifyObservation(False, "VERIFY_RUNSET_MALFORMED", head_sha=head_sha)
            old = seen_numbers.get(number)
            if old is not None and dict(old) != dict(row):
                return VerifyObservation(False, "VERIFY_RUN_NUMBER_DUPLICATE_INCONSISTENT", authoritative_run_number=number, head_sha=head_sha)
            seen_numbers[number] = row
            matching.append(row)
        if not matching:
            return VerifyObservation(False, "LATEST_VERIFY_NOT_SUCCESS", head_sha=head_sha, detail="no matching Verify lineage")
        listed = max(matching, key=lambda x: int(x["run_number"]))
        number = int(listed["run_number"])
        run_id = int(listed["id"])
        current = fetch_current_run(run_id)
        if not isinstance(current, Mapping):
            return VerifyObservation(False, "VERIFY_AUTHORITATIVE_LINEAGE_UNREADABLE", number, run_id, head_sha=head_sha)
        if not _run_identity_matches(current, head_sha) or current.get("id") != run_id or current.get("run_number") != number:
            return VerifyObservation(False, "VERIFY_AUTHORITATIVE_LINEAGE_UNREADABLE", number, run_id, head_sha=head_sha)
        attempt = current.get("run_attempt")
        if not isinstance(attempt, int) or isinstance(attempt, bool) or attempt < 1:
            return VerifyObservation(False, "VERIFY_AUTHORITATIVE_LINEAGE_UNREADABLE", number, run_id, head_sha=head_sha)
        status = current.get("status")
        conclusion = current.get("conclusion")
        eligible = status == "completed" and conclusion == "success"
        return VerifyObservation(
            eligible,
            "VERIFY_AUTHORITATIVE_SUCCESS" if eligible else "LATEST_VERIFY_NOT_SUCCESS",
            number,
            run_id,
            attempt,
            status if isinstance(status, str) else None,
            conclusion if isinstance(conclusion, str) else None,
            head_sha,
            "current state of highest run_number lineage",
        )
    except (KeyError, TypeError, ValueError) as exc:
        return VerifyObservation(False, "VERIFY_RUNSET_MALFORMED", head_sha=head_sha, detail=str(exc))


def prove_ruleset(effective_rules: Any, ruleset_details: Any) -> RulesetProof:
    if not isinstance(effective_rules, list) or not effective_rules or not isinstance(ruleset_details, list) or not ruleset_details:
        return RulesetProof(False, "RULESET_PROOF_UNAVAILABLE", "effective/default-branch rule evidence unavailable")
    effective_ok = False
    for rule in effective_rules:
        if not isinstance(rule, Mapping) or rule.get("type") != "required_status_checks":
            continue
        params = rule.get("parameters")
        if not isinstance(params, Mapping):
            return RulesetProof(False, "RULESET_PROOF_UNAVAILABLE", "malformed required_status_checks parameters")
        checks = params.get("required_status_checks")
        if not isinstance(checks, list):
            return RulesetProof(False, "RULESET_PROOF_UNAVAILABLE", "malformed required status checks")
        contexts = {x.get("context") for x in checks if isinstance(x, Mapping)}
        if params.get("strict_required_status_checks_policy") is True and "verify" in contexts:
            effective_ok = True
    if not effective_ok:
        return RulesetProof(False, "RULESET_PROOF_UNAVAILABLE", "strict required verify context not proven effective")

    applicable = False
    for detail in ruleset_details:
        if not isinstance(detail, Mapping):
            return RulesetProof(False, "RULESET_PROOF_UNAVAILABLE", "malformed ruleset detail")
        bypass = detail.get("bypass_actors")
        if bypass not in ([], ()):  # None is not a positive empty proof.
            return RulesetProof(False, "RULESET_BYPASS_PRESENT", "Ruleset bypass actors are present or unproven")
        if detail.get("current_user_can_bypass") != "never":
            return RulesetProof(False, "RULESET_BYPASS_PRESENT", "current principal may bypass Ruleset")
        conditions = detail.get("conditions")
        include = conditions.get("ref_name", {}).get("include", []) if isinstance(conditions, Mapping) else []
        if detail.get("target") != "branch" or detail.get("enforcement") != "active" or "~DEFAULT_BRANCH" not in include:
            continue
        rules = detail.get("rules")
        if not isinstance(rules, list):
            continue
        for rule in rules:
            if not isinstance(rule, Mapping) or rule.get("type") != "required_status_checks":
                continue
            params = rule.get("parameters")
            checks = params.get("required_status_checks") if isinstance(params, Mapping) else None
            contexts = {x.get("context") for x in checks if isinstance(x, Mapping)} if isinstance(checks, list) else set()
            if isinstance(params, Mapping) and params.get("strict_required_status_checks_policy") is True and "verify" in contexts:
                applicable = True
    if not applicable:
        return RulesetProof(False, "RULESET_PROOF_UNAVAILABLE", "active default-branch no-bypass strict verify Ruleset not proven")
    return RulesetProof(True, "RULESET_PROOF_CONFIRMED", "active default-branch strict verify Ruleset with no bypass")


def repository_observation_gate(*, main_sha: str, tree_complete: bool, open_prs_complete: bool, principal_id: str) -> GateResult:
    if not SHA1_RE.fullmatch(main_sha or "") or not tree_complete or not open_prs_complete or not PRINCIPAL_RE.fullmatch(principal_id or ""):
        return GateResult(False, "REPOSITORY_OBSERVATION_INCOMPLETE", "fresh repository-wide substrate is incomplete or malformed")
    return GateResult(True, "REPOSITORY_OBSERVATION_CONFIRMED", "fresh repository-wide substrate complete")


def is_pending_ownership(_record: Mapping[str, Any]) -> bool:
    return False


def choose_lifecycle_candidate(
    releases: Iterable[Mapping[str, Any]], acquires: Iterable[Mapping[str, Any]]
) -> tuple[str | None, Mapping[str, Any] | None]:
    def eligible(rows: Iterable[Mapping[str, Any]]) -> list[Mapping[str, Any]]:
        out = []
        for row in rows:
            if isinstance(row, Mapping) and row.get("eligible") is True and isinstance(row.get("pr_number"), int):
                out.append(row)
        return sorted(out, key=lambda r: int(r["pr_number"]))
    rs = eligible(releases)
    if rs:
        return "RELEASE", rs[0]
    ac = eligible(acquires)
    if ac:
        return "ACQUIRE", ac[0]
    return None, None


# ---------- pre-merge and canonical transition gates ----------

def _entry_map(entries: Iterable[Mapping[str, Any]]) -> dict[str, Mapping[str, Any]]:
    out = {}
    for row in entries:
        if not isinstance(row, Mapping):
            continue
        path = row.get("path")
        if isinstance(path, str) and row.get("type") != "tree":
            out[path] = row
    return out


def _exact_objects_present(entries: Iterable[Mapping[str, Any]], objects: Iterable[ExactLockObject]) -> bool:
    by_path = _entry_map(entries)
    for obj in objects:
        row = by_path.get(obj.path)
        if row is None or row.get("mode") != obj.mode or row.get("type") != "blob" or row.get("sha") != obj.blob_sha:
            return False
    return True


def premerge_transport_gate(
    *, identity: CanonicalAcquireIdentityV3, independently_derived_ids: SemanticIds,
    base_entries: Sequence[Mapping[str, Any]], candidate_commit: Mapping[str, Any],
    candidate_entries: Sequence[Mapping[str, Any]], candidate_lock_bytes: Mapping[str, bytes],
    verify: VerifyObservation, ruleset: RulesetProof, current_main_sha: str,
) -> GateResult:
    try:
        validate_v3_identity(identity)
    except PhaseBError as exc:
        return GateResult(False, exc.code, exc.message)
    if current_main_sha != identity.expected_base_sha:
        return GateResult(False, "CANONICAL_ACQUIRE_BASE_MISMATCH", "current main moved from frozen selection base")
    parents = candidate_commit.get("parents")
    if not isinstance(parents, list) or len(parents) != 1 or not isinstance(parents[0], Mapping) or parents[0].get("sha") != identity.expected_base_sha:
        return GateResult(False, "CANONICAL_ACQUIRE_BASE_MISMATCH", "candidate is not a single exact child of B")
    tree_sha = candidate_commit.get("tree", {}).get("sha") if isinstance(candidate_commit.get("tree"), Mapping) else None
    if tree_sha != identity.expected_canonical_tree_sha:
        return GateResult(False, "CANONICAL_ACQUIRE_TREE_MISMATCH", "candidate tree != precomputed T")
    try:
        expected_t = deterministic_tree_sha(
            base_entries,
            additions=[{"path": o.path, "mode": o.mode, "type": "blob", "sha": o.blob_sha} for o in identity.exact_lock_objects],
        )
    except PhaseBError as exc:
        return GateResult(False, exc.code, exc.message)
    if expected_t != identity.expected_canonical_tree_sha:
        return GateResult(False, "CANONICAL_ACQUIRE_TREE_MISMATCH", "B + exact_lock_objects does not derive T")
    base_map, cand_map = _entry_map(base_entries), _entry_map(candidate_entries)
    changed = set()
    for path in set(base_map) | set(cand_map):
        a, b = base_map.get(path), cand_map.get(path)
        ident_a = None if a is None else (a.get("mode"), a.get("type"), a.get("sha"))
        ident_b = None if b is None else (b.get("mode"), b.get("type"), b.get("sha"))
        if ident_a != ident_b:
            changed.add(path)
    expected_paths = {o.path for o in identity.exact_lock_objects}
    if changed != expected_paths or not _exact_objects_present(candidate_entries, identity.exact_lock_objects):
        return GateResult(False, "CANONICAL_ACQUIRE_DELTA_MISMATCH", "candidate B->H delta is not exact lock-only set")
    # First prove that the candidate's exact bytes and frozen identity agree
    # internally.  The independently derived trusted chain is compared only
    # after that proof, so a self-consistent forged candidate receives the
    # pre-merge authenticity result rather than the canonical contradiction
    # result used by candidate_content_gate itself.
    content = candidate_content_gate(
        expected_identity=identity,
        independently_derived_ids=identity.semantic_ids(),
        candidate_lock_bytes=candidate_lock_bytes,
        candidate_exact_objects=identity.exact_lock_objects,
        candidate_tree_sha=str(tree_sha),
    )
    if not content.allowed:
        return content
    if identity.semantic_ids() != independently_derived_ids:
        return GateResult(
            False,
            "CANONICAL_ACQUIRE_SEMANTIC_BINDING_MISMATCH",
            "candidate next_binding differs from independently derived trusted semantic IDs",
        )
    if not verify.eligible:
        return GateResult(False, verify.code or "LATEST_VERIFY_NOT_SUCCESS", verify.detail)
    head_sha = candidate_commit.get("sha")
    if verify.head_sha is not None and verify.head_sha != head_sha:
        return GateResult(False, "LATEST_VERIFY_NOT_SUCCESS", "Verify observation belongs to another exact head")
    if not ruleset.passed:
        return GateResult(False, ruleset.code, ruleset.detail)
    return GateResult(True, "TRANSPORT_CANDIDATE_V3_CONFIRMED", "pre-merge H satisfies exact B/T/content/Verify/Ruleset gates")


def _find_canonical_child_of_base(first_parent_history: Sequence[Mapping[str, Any]], base_sha: str) -> tuple[Mapping[str, Any] | None, GateResult | None]:
    if not isinstance(first_parent_history, Sequence) or len(first_parent_history) < 2:
        return None, GateResult(False, "CANONICAL_ACQUIRE_HISTORY_UNPROVEN", "first-parent history does not reach B")
    for i, row in enumerate(first_parent_history):
        if not isinstance(row, Mapping):
            return None, GateResult(False, "CANONICAL_ACQUIRE_HISTORY_UNPROVEN", "malformed history row")
        if row.get("sha") == base_sha:
            if i == 0:
                return None, GateResult(False, "CANONICAL_ACQUIRE_HISTORY_UNPROVEN", "current main equals B; no canonical acquisition transition")
            return first_parent_history[i - 1], None
    return None, GateResult(False, "CANONICAL_ACQUIRE_HISTORY_UNPROVEN", "fresh first-parent chain does not contain B")


def canonical_transition_gate(
    *, identity: CanonicalAcquireIdentityV3, first_parent_history: Sequence[Mapping[str, Any]],
    current_entries: Sequence[Mapping[str, Any]], current_lock_bytes: Mapping[str, bytes],
    ruleset: RulesetProof, now: datetime,
) -> GateResult:
    try:
        validate_v3_identity(identity)
    except PhaseBError as exc:
        return GateResult(False, exc.code, exc.message)
    m, history_error = _find_canonical_child_of_base(first_parent_history, identity.expected_base_sha)
    if history_error is not None:
        return history_error
    assert m is not None
    parents = m.get("parents")
    if not isinstance(parents, list) or len(parents) != 1:
        return GateResult(False, "NONCANONICAL_ACQUIRE_MERGE_SHAPE", "canonical child M is not single-parent")
    if not isinstance(parents[0], Mapping) or parents[0].get("sha") != identity.expected_base_sha:
        return GateResult(False, "CANONICAL_ACQUIRE_HISTORY_UNPROVEN", "canonical child does not have exact parent B")
    m_tree = m.get("tree", {}).get("sha") if isinstance(m.get("tree"), Mapping) else None
    if m_tree != identity.expected_canonical_tree_sha:
        return GateResult(False, "CANONICAL_ACQUIRE_TREE_MISMATCH", "canonical transition tree != T")
    m_entries = m.get("entries")
    if not isinstance(m_entries, list):
        return GateResult(False, "CANONICAL_ACQUIRE_HISTORY_UNPROVEN", "canonical child lacks exact tree entries")
    # The base row immediately after M must expose exact B entries, allowing an
    # independent lock-only delta proof rather than trusting tree equality alone.
    try:
        m_index = first_parent_history.index(m)
    except ValueError:
        return GateResult(False, "CANONICAL_ACQUIRE_HISTORY_UNPROVEN", "canonical child position ambiguous")
    if m_index + 1 >= len(first_parent_history):
        return GateResult(False, "CANONICAL_ACQUIRE_HISTORY_UNPROVEN", "base row unavailable")
    b = first_parent_history[m_index + 1]
    if b.get("sha") != identity.expected_base_sha or not isinstance(b.get("entries"), list):
        return GateResult(False, "CANONICAL_ACQUIRE_HISTORY_UNPROVEN", "exact base tree entries unavailable")
    base_map, m_map = _entry_map(b["entries"]), _entry_map(m_entries)
    changed = set()
    for path in set(base_map) | set(m_map):
        a, c = base_map.get(path), m_map.get(path)
        aa = None if a is None else (a.get("mode"), a.get("type"), a.get("sha"))
        cc = None if c is None else (c.get("mode"), c.get("type"), c.get("sha"))
        if aa != cc:
            changed.add(path)
    expected_paths = {o.path for o in identity.exact_lock_objects}
    if changed != expected_paths or not _exact_objects_present(m_entries, identity.exact_lock_objects):
        return GateResult(False, "CANONICAL_ACQUIRE_DELTA_MISMATCH", "B->M is not exact lock-only transition")
    if not _exact_objects_present(current_entries, identity.exact_lock_objects):
        return GateResult(False, "CANONICAL_LOCK_READBACK_MISMATCH", "current main no longer contains exact V3 lock objects")
    if set(current_lock_bytes) != expected_paths:
        return GateResult(False, "CANONICAL_LOCK_READBACK_MISMATCH", "current lock byte path set differs")
    reconstructed_payload: Mapping[str, Any] | None = None
    for obj in identity.exact_lock_objects:
        raw = current_lock_bytes.get(obj.path)
        if not isinstance(raw, (bytes, bytearray)) or git_blob_oid(bytes(raw)) != obj.blob_sha or hashlib.sha256(bytes(raw)).hexdigest() != obj.bytes_sha256:
            return GateResult(False, "CANONICAL_LOCK_READBACK_MISMATCH", f"current exact bytes changed: {obj.path}")
        try:
            payload = json.loads(bytes(raw).decode("utf-8"))
        except Exception:
            return GateResult(False, "CANONICAL_LOCK_READBACK_MISMATCH", f"current lock JSON unreadable: {obj.path}")
        recon = reconstruct_v3_from_lock_payload(identity, payload)
        if not recon.allowed:
            return GateResult(False, recon.code, recon.detail)
        if reconstructed_payload is None:
            reconstructed_payload = payload
        elif payload != reconstructed_payload:
            return GateResult(False, "CANONICAL_ACQUIRE_SEMANTIC_BINDING_INCONSISTENT", "current collision-key copies differ")
    try:
        now_utc = now.astimezone(timezone.utc)
        expires = _parse_time(identity.expires_at)
    except Exception as exc:
        return GateResult(False, "CANONICAL_LOCK_NOT_ACTIVE", f"cannot establish active lease: {exc}")
    if expires <= now_utc:
        return GateResult(False, "CANONICAL_LOCK_NOT_ACTIVE", "expected V3 canonical lock is expired")
    if not ruleset.passed:
        return GateResult(False, ruleset.code, ruleset.detail)
    return GateResult(True, "CANONICAL_ACQUIRE_IDENTITY_CONFIRMED", "exact V3 B->M content transition and current active canonical read-back confirmed")


# ---------- source RELEASE provenance ----------

def release_provenance_gate(
    *, source_record: Mapping[str, Any], release_base_sha: str, release_expected_tree_sha: str,
    release_transport_commit: Mapping[str, Any], release_transport_entries: Sequence[Mapping[str, Any]],
    release_verify: VerifyObservation, first_parent_history: Sequence[Mapping[str, Any]],
) -> GateResult:
    bundle = source_record.get("source_lock_blob_bundle")
    if not isinstance(bundle, list) or not bundle:
        return GateResult(False, "SOURCE_EPOCH_UNPROVEN", "source lock bundle unavailable")
    try:
        source = _sorted_blob_bundle(bundle)
    except PhaseBError as exc:
        return GateResult(False, exc.code, exc.message)
    if not SHA1_RE.fullmatch(release_base_sha or "") or not SHA1_RE.fullmatch(release_expected_tree_sha or ""):
        return GateResult(False, "SOURCE_EPOCH_RELEASE_PROVENANCE_MISMATCH", "invalid release base/tree")
    parents = release_transport_commit.get("parents")
    if not isinstance(parents, list) or len(parents) != 1 or parents[0].get("sha") != release_base_sha:
        return GateResult(False, "SOURCE_EPOCH_RELEASE_PROVENANCE_MISMATCH", "RELEASE H is not a single child of release base")
    if release_transport_commit.get("tree", {}).get("sha") != release_expected_tree_sha:
        return GateResult(False, "SOURCE_EPOCH_RELEASE_PROVENANCE_MISMATCH", "RELEASE H tree mismatch")
    if not release_verify.eligible:
        return GateResult(False, release_verify.code or "LATEST_VERIFY_NOT_SUCCESS", "RELEASE exact head lacks current Verify success")
    source_paths = {x["path"] for x in source}
    if source_paths.intersection(_entry_map(release_transport_entries)):
        return GateResult(False, "SOURCE_EPOCH_RELEASE_PROVENANCE_MISMATCH", "RELEASE H still contains source lock paths")
    m, err = _find_canonical_child_of_base(first_parent_history, release_base_sha)
    if err is not None:
        return GateResult(False, "SOURCE_EPOCH_RELEASE_PROVENANCE_MISMATCH", err.detail)
    assert m is not None
    parents = m.get("parents")
    if not isinstance(parents, list) or len(parents) != 1 or parents[0].get("sha") != release_base_sha:
        return GateResult(False, "SOURCE_EPOCH_RELEASE_PROVENANCE_MISMATCH", "canonical RELEASE transition shape mismatch")
    if m.get("tree", {}).get("sha") != release_expected_tree_sha or not isinstance(m.get("entries"), list):
        return GateResult(False, "SOURCE_EPOCH_RELEASE_PROVENANCE_MISMATCH", "canonical RELEASE tree mismatch")
    # Locate B row and prove its exact source OIDs, then exact deletion-only delta.
    base = None
    for row in first_parent_history:
        if row.get("sha") == release_base_sha:
            base = row
            break
    if base is None or not isinstance(base.get("entries"), list):
        return GateResult(False, "SOURCE_EPOCH_RELEASE_PROVENANCE_MISMATCH", "RELEASE base entries unavailable")
    bmap, mmap = _entry_map(base["entries"]), _entry_map(m["entries"])
    for item in source:
        row = bmap.get(item["path"])
        if row is None or row.get("mode") != "100644" or row.get("type") != "blob" or row.get("sha") != item["blob_sha"]:
            return GateResult(False, "SOURCE_EPOCH_RELEASE_PROVENANCE_MISMATCH", "source epoch exact lock object not present at RELEASE base")
    changed = set()
    for path in set(bmap) | set(mmap):
        a, z = bmap.get(path), mmap.get(path)
        aa = None if a is None else (a.get("mode"), a.get("type"), a.get("sha"))
        zz = None if z is None else (z.get("mode"), z.get("type"), z.get("sha"))
        if aa != zz:
            changed.add(path)
    if changed != source_paths or source_paths.intersection(mmap):
        return GateResult(False, "SOURCE_EPOCH_RELEASE_PROVENANCE_MISMATCH", "canonical RELEASE delta is not exact source-bundle deletion")
    return GateResult(True, "SOURCE_EPOCH_RELEASE_PROVENANCE_CONFIRMED", "exact source epoch RELEASE transition proven")


# ---------- conservative production GitHub adapter / operator surface ----------
class GitHubPhaseBClient:
    """Narrow GitHub adapter. It may prepare refs/PRs; it never writes canonical main."""

    def __init__(self, token: str, repository: str = REPOSITORY):
        if repository != REPOSITORY:
            raise PhaseBError("REPOSITORY_OBSERVATION_INCOMPLETE", "unexpected repository namespace")
        if not token:
            raise PhaseBError("GITHUB_TOKEN_UNAVAILABLE", "GitHub token is required for Phase B transport")
        self.token = token
        self.repository = repository
        self.owner, self.repo = repository.split("/", 1)

    def request(self, method: str, path: str, payload: Any = None) -> Any:
        url = API_ROOT + path
        data = None if payload is None else json.dumps(payload).encode("utf-8")
        req = urllib.request.Request(
            url,
            data=data,
            method=method,
            headers={
                "Accept": "application/vnd.github+json",
                "Authorization": f"Bearer {self.token}",
                "X-GitHub-Api-Version": "2022-11-28",
                "User-Agent": "AIMath-Village-v1.3-Phase-B",
            },
        )
        try:
            with urllib.request.urlopen(req, timeout=30) as response:
                raw = response.read()
        except urllib.error.HTTPError as exc:
            body = exc.read().decode("utf-8", errors="replace")
            raise PhaseBError("GITHUB_OBSERVATION_UNAVAILABLE", f"GitHub API {method} {path} failed {exc.code}: {body[:500]}") from exc
        except OSError as exc:
            raise PhaseBError("GITHUB_OBSERVATION_UNAVAILABLE", f"GitHub API unavailable: {exc}") from exc
        if not raw:
            return {}
        try:
            return json.loads(raw.decode("utf-8"))
        except Exception as exc:
            raise PhaseBError("GITHUB_OBSERVATION_UNAVAILABLE", f"GitHub returned malformed JSON for {path}") from exc

    def authenticated_principal_id(self) -> str:
        obj = self.request("GET", "/user")
        login = obj.get("login") if isinstance(obj, Mapping) else None
        if not isinstance(login, str) or not login:
            raise PhaseBError("PRINCIPAL_AUTHENTICATION_UNAVAILABLE", "authenticated GitHub login unavailable")
        principal = f"gh:{login}"
        if PRINCIPAL_RE.fullmatch(principal) is None:
            raise PhaseBError("PRINCIPAL_AUTHENTICATION_UNAVAILABLE", "authenticated GitHub login is not a valid Village principal")
        return principal

    def current_main_sha(self) -> str:
        obj = self.request("GET", f"/repos/{self.owner}/{self.repo}/git/ref/heads/main")
        sha = obj.get("object", {}).get("sha") if isinstance(obj, Mapping) else None
        if not isinstance(sha, str) or not SHA1_RE.fullmatch(sha):
            raise PhaseBError("REPOSITORY_OBSERVATION_INCOMPLETE", "current main full SHA unavailable")
        return sha

    def git_commit(self, sha: str) -> dict[str, Any]:
        obj = self.request("GET", f"/repos/{self.owner}/{self.repo}/git/commits/{sha}")
        if not isinstance(obj, dict):
            raise PhaseBError("GITHUB_OBSERVATION_UNAVAILABLE", "malformed Git commit response")
        return obj

    def recursive_tree(self, commit_sha: str) -> tuple[str, list[dict[str, Any]]]:
        commit = self.git_commit(commit_sha)
        tree_sha = commit.get("tree", {}).get("sha")
        if not isinstance(tree_sha, str) or not SHA1_RE.fullmatch(tree_sha):
            raise PhaseBError("REPOSITORY_OBSERVATION_INCOMPLETE", "commit tree SHA unavailable")
        obj = self.request("GET", f"/repos/{self.owner}/{self.repo}/git/trees/{tree_sha}?recursive=1")
        if not isinstance(obj, Mapping) or obj.get("truncated") is True or not isinstance(obj.get("tree"), list):
            raise PhaseBError("REPOSITORY_OBSERVATION_INCOMPLETE", "recursive tree incomplete/truncated")
        return tree_sha, list(obj["tree"])

    def blob_bytes(self, blob_sha: str) -> bytes:
        obj = self.request("GET", f"/repos/{self.owner}/{self.repo}/git/blobs/{blob_sha}")
        if not isinstance(obj, Mapping) or obj.get("encoding") != "base64" or not isinstance(obj.get("content"), str):
            raise PhaseBError("GITHUB_OBSERVATION_UNAVAILABLE", "blob response malformed")
        try:
            raw = base64.b64decode(obj["content"], validate=False)
        except Exception as exc:
            raise PhaseBError("GITHUB_OBSERVATION_UNAVAILABLE", "blob base64 decode failed") from exc
        if git_blob_oid(raw) != blob_sha:
            raise PhaseBError("GITHUB_OBSERVATION_UNAVAILABLE", "blob bytes do not hash to requested Git OID")
        return raw

    def open_prs(self) -> list[dict[str, Any]]:
        out: list[dict[str, Any]] = []
        for page in range(1, 11):
            rows = self.request("GET", f"/repos/{self.owner}/{self.repo}/pulls?state=open&base=main&sort=created&direction=asc&per_page=100&page={page}")
            if not isinstance(rows, list):
                raise PhaseBError("REPOSITORY_OBSERVATION_INCOMPLETE", "open PR response malformed")
            out.extend(rows)
            if len(rows) < 100:
                return out
        raise PhaseBError("REPOSITORY_OBSERVATION_INCOMPLETE", "open PR observation exceeded 1000-row bound")

    def workflow_runs_for_head(self, head_sha: str) -> VerifyObservation:
        rows: list[dict[str, Any]] = []
        complete = False
        for page in range(1, 11):
            try:
                obj = self.request(
                    "GET",
                    f"/repos/{self.owner}/{self.repo}/actions/workflows/{VERIFY_WORKFLOW_ID}/runs?event={VERIFY_EVENT}&head_sha={head_sha}&per_page=100&page={page}",
                )
            except PhaseBError as exc:
                return VerifyObservation(
                    False,
                    "VERIFY_RUNSET_PAGINATION_FAILED",
                    head_sha=head_sha,
                    detail=exc.message,
                )
            if not isinstance(obj, Mapping) or not isinstance(obj.get("workflow_runs"), list):
                return VerifyObservation(False, "VERIFY_RUNSET_MALFORMED", head_sha=head_sha)
            page_rows = list(obj["workflow_runs"])
            rows.extend(page_rows)
            total = obj.get("total_count")
            if isinstance(total, int) and total > 1000:
                return VerifyObservation(False, "VERIFY_RUNSET_RESULT_CAP_UNPROVEN", head_sha=head_sha)
            if len(page_rows) < 100:
                complete = True
                break
        if not complete:
            return VerifyObservation(False, "VERIFY_RUNSET_TRUNCATED", head_sha=head_sha)
        return authoritative_verify_lineage(
            rows,
            head_sha=head_sha,
            complete=True,
            fetch_current_run=lambda rid: self.request("GET", f"/repos/{self.owner}/{self.repo}/actions/runs/{rid}"),
        )

    def ruleset_proof(self) -> RulesetProof:
        def complete_pages(path: str) -> list[Any] | None:
            rows: list[Any] = []
            for page in range(1, 11):
                separator = "&" if "?" in path else "?"
                try:
                    page_rows = self.request("GET", f"{path}{separator}per_page=100&page={page}")
                except PhaseBError:
                    return None
                if not isinstance(page_rows, list) or len(page_rows) > 100:
                    return None
                rows.extend(page_rows)
                if len(page_rows) < 100:
                    return rows
            return None

        effective = complete_pages(f"/repos/{self.owner}/{self.repo}/rules/branches/main")
        summaries = complete_pages(f"/repos/{self.owner}/{self.repo}/rulesets")
        if effective is None or summaries is None:
            return RulesetProof(False, "RULESET_PROOF_UNAVAILABLE", "Ruleset pagination unavailable, malformed, or truncated")

        ids: list[int] = []
        for item in summaries:
            ruleset_id = item.get("id") if isinstance(item, Mapping) else None
            if not isinstance(ruleset_id, int) or isinstance(ruleset_id, bool) or ruleset_id < 1 or ruleset_id in ids:
                return RulesetProof(False, "RULESET_PROOF_UNAVAILABLE", "ruleset summary malformed or duplicated")
            ids.append(ruleset_id)

        details = []
        for ruleset_id in ids:
            try:
                details.append(self.request("GET", f"/repos/{self.owner}/{self.repo}/rulesets/{ruleset_id}"))
            except PhaseBError:
                return RulesetProof(False, "RULESET_PROOF_UNAVAILABLE", "ruleset detail unavailable")
        return prove_ruleset(effective, details)

    def create_blob(self, raw: bytes) -> str:
        obj = self.request("POST", f"/repos/{self.owner}/{self.repo}/git/blobs", {"content": base64.b64encode(raw).decode("ascii"), "encoding": "base64"})
        sha = obj.get("sha") if isinstance(obj, Mapping) else None
        if sha != git_blob_oid(raw):
            raise PhaseBError("GITHUB_TRANSPORT_WRITE_MISMATCH", "server blob OID differs from locally frozen OID")
        return sha

    def create_tree(self, base_tree_sha: str, entries: Iterable[ExactLockObject], *, deletions: Iterable[str] = ()) -> str:
        tree = [{"path": o.path, "mode": o.mode, "type": "blob", "sha": o.blob_sha} for o in entries]
        tree.extend({"path": p, "mode": "100644", "type": "blob", "sha": None} for p in deletions)
        obj = self.request("POST", f"/repos/{self.owner}/{self.repo}/git/trees", {"base_tree": base_tree_sha, "tree": tree})
        sha = obj.get("sha") if isinstance(obj, Mapping) else None
        if not isinstance(sha, str) or not SHA1_RE.fullmatch(sha):
            raise PhaseBError("GITHUB_TRANSPORT_WRITE_MISMATCH", "server tree SHA unavailable")
        return sha

    def create_commit(self, *, message: str, tree_sha: str, parent_sha: str, author: Mapping[str, str] | None = None) -> str:
        payload: dict[str, Any] = {"message": message, "tree": tree_sha, "parents": [parent_sha]}
        if author is not None:
            payload["author"] = dict(author)
            payload["committer"] = dict(author)
        obj = self.request("POST", f"/repos/{self.owner}/{self.repo}/git/commits", payload)
        sha = obj.get("sha") if isinstance(obj, Mapping) else None
        if not isinstance(sha, str) or not SHA1_RE.fullmatch(sha):
            raise PhaseBError("GITHUB_TRANSPORT_WRITE_MISMATCH", "server commit SHA unavailable")
        return sha

    def create_ref_if_absent(self, ref: str, sha: str) -> bool:
        try:
            self.request("POST", f"/repos/{self.owner}/{self.repo}/git/refs", {"ref": f"refs/heads/{ref}", "sha": sha})
            return True
        except PhaseBError as exc:
            if "422" not in exc.message:
                raise
            return False

    def ref_sha(self, ref: str) -> str | None:
        quoted = urllib.parse.quote(ref, safe="/")
        try:
            obj = self.request("GET", f"/repos/{self.owner}/{self.repo}/git/ref/heads/{quoted}")
        except PhaseBError as exc:
            if "404" in exc.message:
                return None
            raise
        sha = obj.get("object", {}).get("sha") if isinstance(obj, Mapping) else None
        return sha if isinstance(sha, str) and SHA1_RE.fullmatch(sha) else None

    def create_draft_pr(self, *, title: str, head_ref: str, body: str) -> int:
        obj = self.request("POST", f"/repos/{self.owner}/{self.repo}/pulls", {"title": title, "head": head_ref, "base": "main", "body": body, "draft": True})
        number = obj.get("number") if isinstance(obj, Mapping) else None
        if not isinstance(number, int):
            raise PhaseBError("GITHUB_TRANSPORT_WRITE_MISMATCH", "created PR number unavailable")
        return number

    def graphql(self, query: str, variables: Mapping[str, Any]) -> Any:
        data = json.dumps({"query": query, "variables": dict(variables)}).encode("utf-8")
        req = urllib.request.Request(
            "https://api.github.com/graphql", data=data, method="POST",
            headers={"Accept": "application/vnd.github+json", "Authorization": f"Bearer {self.token}",
                     "X-GitHub-Api-Version": "2022-11-28", "User-Agent": "AIMath-Village-v1.3-Phase-B"},
        )
        try:
            with urllib.request.urlopen(req, timeout=30) as response:
                obj = json.loads(response.read().decode("utf-8"))
        except (urllib.error.HTTPError, OSError, json.JSONDecodeError) as exc:
            raise PhaseBError("GITHUB_OBSERVATION_UNAVAILABLE", f"GitHub GraphQL request failed: {exc}") from exc
        if not isinstance(obj, Mapping) or obj.get("errors"):
            raise PhaseBError("GITHUB_OBSERVATION_UNAVAILABLE", f"GitHub GraphQL returned errors: {obj.get('errors') if isinstance(obj, Mapping) else 'malformed'}")
        return obj.get("data")

    def mark_pr_ready(self, pr_node_id: str) -> None:
        data = self.graphql(
            "mutation($id:ID!){markPullRequestReadyForReview(input:{pullRequestId:$id}){pullRequest{id isDraft}}}",
            {"id": pr_node_id},
        )
        pr = data.get("markPullRequestReadyForReview", {}).get("pullRequest", {}) if isinstance(data, Mapping) else {}
        if pr.get("isDraft") is not False:
            raise PhaseBError("TRANSPORT_READY_REQUIRES_REVIEWED_ADAPTER", "GitHub did not confirm PR ready-for-review")

    def rerun_workflow_run(self, run_id: int) -> None:
        self.request("POST", f"/repos/{self.owner}/{self.repo}/actions/runs/{run_id}/rerun", {})


def _local_head_sha(root: Path) -> str:
    try:
        return subprocess.check_output(["git", "-C", str(root), "rev-parse", "HEAD"], text=True).strip()
    except Exception as exc:
        raise PhaseBError("STALE_TRUSTED_LOCAL_MAIN", f"cannot read local checkout SHA: {exc}") from exc


def _write_state(path: Path, state: Mapping[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    data = (json.dumps(_plain(state), sort_keys=True, indent=2, ensure_ascii=False) + "\n").encode("utf-8")
    tmp = path.with_suffix(path.suffix + ".tmp")
    tmp.write_bytes(data)
    try:
        os.chmod(tmp, 0o600)
    except OSError:
        pass
    tmp.replace(path)


def _read_state(path: Path) -> dict[str, Any] | None:
    if not path.is_file():
        return None
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
    except Exception as exc:
        raise PhaseBError("RETAINED_STATE_INVALID", f"cannot read Phase B retained state: {exc}") from exc
    if not isinstance(value, dict):
        raise PhaseBError("RETAINED_STATE_INVALID", "Phase B retained state must be an object")
    return value


def _tree_blob_map(entries: Iterable[Mapping[str, Any]]) -> dict[str, dict[str, Any]]:
    return {
        str(row["path"]): dict(row)
        for row in entries
        if isinstance(row, Mapping) and row.get("type") == "blob" and isinstance(row.get("path"), str)
    }


def _git_commit_view(client: GitHubPhaseBClient, sha: str, *, with_entries: bool = True) -> dict[str, Any]:
    commit = client.git_commit(sha)
    parents = commit.get("parents") if isinstance(commit.get("parents"), list) else []
    row: dict[str, Any] = {
        "sha": sha,
        "parents": [{"sha": p.get("sha")} for p in parents if isinstance(p, Mapping)],
        "tree": {"sha": commit.get("tree", {}).get("sha") if isinstance(commit.get("tree"), Mapping) else None},
    }
    if with_entries:
        _tree_sha, entries = client.recursive_tree(sha)
        row["entries"] = entries
    return row


def _first_parent_history(client: GitHubPhaseBClient, current_sha: str, stop_sha: str, *, limit: int = 512) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    sha = current_sha
    seen: set[str] = set()
    for _ in range(limit):
        if sha in seen:
            raise PhaseBError("CANONICAL_ACQUIRE_HISTORY_UNPROVEN", "first-parent history cycle observed")
        seen.add(sha)
        row = _git_commit_view(client, sha, with_entries=True)
        rows.append(row)
        if sha == stop_sha:
            return rows
        parents = row.get("parents", [])
        if not parents:
            break
        nxt = parents[0].get("sha") if isinstance(parents[0], Mapping) else None
        if not isinstance(nxt, str) or not SHA1_RE.fullmatch(nxt):
            break
        sha = nxt
    raise PhaseBError("CANONICAL_ACQUIRE_HISTORY_UNPROVEN", f"first-parent history did not reach {stop_sha} within bound")



def _source_epoch_consumption_gate(
    client: GitHubPhaseBClient,
    *,
    current_main_sha: str,
    release_base_sha: str,
    source_epoch_id: str,
) -> GateResult:
    """Prove from canonical first-parent history that a source epoch is unused."""
    if not SHA1_RE.fullmatch(current_main_sha or "") or not SHA1_RE.fullmatch(release_base_sha or ""):
        raise PhaseBError("CANONICAL_ACQUIRE_HISTORY_UNPROVEN", "source-epoch history boundary malformed")
    if not SHA256_RE.fullmatch(source_epoch_id or ""):
        raise PhaseBError("CANONICAL_ACQUIRE_HISTORY_UNPROVEN", "source-epoch identity malformed")

    history = _first_parent_history(client, current_main_sha, release_base_sha)
    for child, parent in zip(history, history[1:]):
        child_entries = child.get("entries")
        parent_entries = parent.get("entries")
        if not isinstance(child_entries, list) or not isinstance(parent_entries, list):
            raise PhaseBError("CANONICAL_ACQUIRE_HISTORY_UNPROVEN", "first-parent tree entries unavailable")

        cmap, pmap = _entry_map(child_entries), _entry_map(parent_entries)
        changed = {
            path
            for path in set(cmap) | set(pmap)
            if (
                None if pmap.get(path) is None else (
                    pmap[path].get("mode"), pmap[path].get("type"), pmap[path].get("sha")
                )
            ) != (
                None if cmap.get(path) is None else (
                    cmap[path].get("mode"), cmap[path].get("type"), cmap[path].get("sha")
                )
            )
        }
        added_locks = sorted(
            path
            for path in changed
            if path not in pmap
            and path in cmap
            and path.startswith("coordination/locks/")
            and path.endswith(".yml")
        )

        for path in added_locks:
            row = cmap[path]
            if row.get("mode") != "100644" or row.get("type") != "blob":
                raise PhaseBError("CANONICAL_ACQUIRE_HISTORY_UNPROVEN", f"historical lock object malformed: {path}")
            sha = row.get("sha")
            if not isinstance(sha, str) or not SHA1_RE.fullmatch(sha):
                raise PhaseBError("CANONICAL_ACQUIRE_HISTORY_UNPROVEN", f"historical lock OID unavailable: {path}")
            try:
                payload = json.loads(client.blob_bytes(sha).decode("utf-8"))
            except Exception as exc:
                raise PhaseBError("CANONICAL_ACQUIRE_HISTORY_UNPROVEN", f"historical lock bytes unreadable: {path}: {exc}") from exc
            if not isinstance(payload, Mapping) or "next_binding" not in payload:
                continue
            try:
                ids = parse_next_binding(payload)
            except PhaseBError as exc:
                raise PhaseBError(
                    "CANONICAL_ACQUIRE_HISTORY_UNPROVEN",
                    f"historical v1.3 next_binding malformed at {path}: {exc.code}",
                ) from exc
            if ids.source_epoch_id != source_epoch_id:
                continue

            try:
                parents = child.get("parents")
                if (
                    not isinstance(parents, list)
                    or len(parents) != 1
                    or not isinstance(parents[0], Mapping)
                    or parents[0].get("sha") != parent.get("sha")
                ):
                    raise PhaseBError("NONCANONICAL_ACQUIRE_MERGE_SHAPE", "consuming ACQUIRE is not one first-parent transition")
                parent_sha = parent.get("sha")
                parent_tree = parent.get("tree", {}).get("sha") if isinstance(parent.get("tree"), Mapping) else None
                child_tree = child.get("tree", {}).get("sha") if isinstance(child.get("tree"), Mapping) else None
                if not isinstance(parent_sha, str) or not SHA1_RE.fullmatch(parent_sha):
                    raise PhaseBError("CANONICAL_ACQUIRE_HISTORY_UNPROVEN", "historical parent SHA unavailable")
                if not isinstance(parent_tree, str) or not SHA1_RE.fullmatch(parent_tree):
                    raise PhaseBError("CANONICAL_ACQUIRE_HISTORY_UNPROVEN", "historical parent tree unavailable")
                if not isinstance(child_tree, str) or not SHA1_RE.fullmatch(child_tree):
                    raise PhaseBError("CANONICAL_ACQUIRE_HISTORY_UNPROVEN", "historical child tree unavailable")

                acquired = _parse_time(payload.get("acquired_at"))
                expires = _parse_time(payload.get("expires_at"))
                ttl_seconds = int((expires - acquired).total_seconds())
                if ttl_seconds <= 0 or ttl_seconds % 3600:
                    raise PhaseBError("CANONICAL_ACQUIRE_IDENTITY_MISMATCH", "historical lease duration is not whole positive hours")
                actor = payload.get("actor")
                if not isinstance(actor, Mapping):
                    raise PhaseBError("CANONICAL_ACQUIRE_IDENTITY_MISMATCH", "historical actor missing")
                material = freeze_acquire_material(
                    semantic_ids=ids,
                    base_sha=parent_sha,
                    base_tree_sha=parent_tree,
                    base_tree_entries=parent_entries,
                    selected_task_id=payload.get("task_id"),
                    worker_id=payload.get("worker_id"),
                    principal_id=actor.get("id"),
                    work_ref=payload.get("work_ref"),
                    collision_keys=payload.get("collision_keys", ()),
                    acquired_at=acquired,
                    lease_ttl_hours=ttl_seconds // 3600,
                )
                if material.lock_payload != payload:
                    raise PhaseBError("CANONICAL_ACQUIRE_IDENTITY_MISMATCH", "historical lock payload is not exact deterministic V3 material")
                expected_paths = {obj.path for obj in material.identity.exact_lock_objects}
                if changed != expected_paths or child_tree != material.identity.expected_canonical_tree_sha:
                    raise PhaseBError("CANONICAL_ACQUIRE_DELTA_MISMATCH", "historical source-epoch ACQUIRE is not exact lock-only transition")
                for obj in material.identity.exact_lock_objects:
                    current = cmap.get(obj.path)
                    if (
                        obj.path in pmap
                        or current is None
                        or current.get("mode") != obj.mode
                        or current.get("type") != "blob"
                        or current.get("sha") != obj.blob_sha
                        or client.blob_bytes(obj.blob_sha) != material.lock_bytes[obj.path]
                    ):
                        raise PhaseBError("CANONICAL_ACQUIRE_TREE_MISMATCH", f"historical lock object mismatch: {obj.path}")
            except (PhaseBError, TypeError, ValueError) as exc:
                code = exc.code if isinstance(exc, PhaseBError) else "CANONICAL_ACQUIRE_IDENTITY_MISMATCH"
                detail = exc.message if isinstance(exc, PhaseBError) else str(exc)
                raise PhaseBError(
                    "CANONICAL_ACQUIRE_HISTORY_UNPROVEN",
                    f"matching source-epoch acquisition is not fully provable: {code}: {detail}",
                ) from exc

            return GateResult(
                False,
                "OLD_ACQUISITION_REPLAY",
                f"source epoch already consumed by canonical v1.3 ACQUIRE {child.get('sha')}",
            )

    return GateResult(True, "SOURCE_EPOCH_UNCONSUMED", "no canonical v1.3 ACQUIRE consumed this source epoch")

def _find_tree_blob(entries: Sequence[Mapping[str, Any]], path: str) -> str:
    row = _tree_blob_map(entries).get(path)
    sha = row.get("sha") if row else None
    if not isinstance(sha, str) or not SHA1_RE.fullmatch(sha):
        raise PhaseBError("REPOSITORY_OBSERVATION_INCOMPLETE", f"exact blob unavailable at {path}")
    return sha


def _source_bundle_from_state(state: Any, task_id: str, worker_id: str, principal_id: str):
    bundles = list(state.lock_for_task(task_id, active_only=False))
    exact = [
        b for b in bundles
        if b.payload.get("worker_id") == worker_id
        and isinstance(b.payload.get("actor"), Mapping)
        and b.payload.get("actor", {}).get("id") == principal_id
    ]
    if len(exact) > 1:
        raise PhaseBError("SOURCE_EPOCH_UNPROVEN", "multiple source lock bundles match Task/worker/principal")
    return exact[0] if exact else None


def _require_source_bundle_on_fresh_main(
    client: GitHubPhaseBClient,
    *,
    state: Any,
    bundle: Any,
    main_entries: Sequence[Mapping[str, Any]],
) -> None:
    """Bind Phase A's source lock view to exact current-main Git objects."""
    by_path = _tree_blob_map(main_entries)
    if not bundle.paths:
        raise PhaseBError("SOURCE_EPOCH_UNPROVEN", "source lock bundle has no canonical paths")
    for path_obj in bundle.paths:
        try:
            rel = path_obj.relative_to(state.root).as_posix()
            local_raw = path_obj.read_bytes()
        except (OSError, ValueError) as exc:
            raise PhaseBError("SOURCE_EPOCH_UNPROVEN", "source lock local bytes unavailable") from exc
        row = by_path.get(rel)
        if row is None or row.get("mode") != "100644" or row.get("type") != "blob":
            raise PhaseBError("SOURCE_EPOCH_UNPROVEN", f"source lock Git object unavailable: {rel}")
        remote_raw = client.blob_bytes(str(row.get("sha", "")))
        if local_raw != remote_raw:
            raise PhaseBError("SOURCE_EPOCH_UNPROVEN", f"source lock differs from fresh current main: {rel}")


def _terminal_from_phase_a(state: Any, task_id: str, worker_id: str, lock_payload: Mapping[str, Any] | None):
    from village_next import recognize_terminal_evidence
    terminal, errors = recognize_terminal_evidence(
        state,
        task_id=task_id,
        worker_id=worker_id,
        lock_payload=dict(lock_payload) if lock_payload is not None else None,
    )
    if terminal is None:
        raise PhaseBError("SOURCE_TERMINAL_UNPROVEN", "; ".join(errors) or "canonical terminal evidence unavailable")
    return terminal


def _source_record_from_fresh_main(
    client: GitHubPhaseBClient,
    *, state: Any, main_sha: str, main_entries: Sequence[Mapping[str, Any]],
    task_id: str, worker_id: str, principal_id: str,
) -> tuple[dict[str, Any], str, Any]:
    bundle = _source_bundle_from_state(state, task_id, worker_id, principal_id)
    if bundle is None:
        raise PhaseBError("SOURCE_EPOCH_UNPROVEN", "exact current source acquisition is absent")
    terminal = _terminal_from_phase_a(state, task_id, worker_id, bundle.payload)
    by_path = _tree_blob_map(main_entries)
    source_blob_bundle = []
    for path_obj in bundle.paths:
        rel = path_obj.relative_to(state.root).as_posix()
        row = by_path.get(rel)
        if row is None or row.get("mode") != "100644" or row.get("type") != "blob":
            raise PhaseBError("SOURCE_EPOCH_UNPROVEN", f"source lock Git object unavailable: {rel}")
        source_blob_bundle.append({"path": rel, "blob_sha": row["sha"]})
    terminal_blob_sha = _find_tree_blob(main_entries, terminal.source_path)
    record, source_id = derive_source_acquisition_v1(
        repository=REPOSITORY,
        source_task_id=task_id,
        worker_id=worker_id,
        principal_id=principal_id,
        lock_payload=bundle.payload,
        source_lock_blob_bundle=source_blob_bundle,
        terminal_class=terminal.terminal_class,
        terminal_path=terminal.source_path,
        terminal_blob_sha=terminal_blob_sha,
        terminal_outcome_type=terminal.outcome_type,
    )
    return record, source_id, terminal


def _public_user_identity(client: GitHubPhaseBClient, principal_id: str) -> tuple[str, str]:
    login = principal_id.removeprefix("gh:")
    obj = client.request("GET", f"/users/{urllib.parse.quote(login, safe='')}")
    uid = obj.get("id") if isinstance(obj, Mapping) else None
    name = obj.get("name") if isinstance(obj, Mapping) else None
    if not isinstance(uid, int):
        raise PhaseBError("GITHUB_TRANSPORT_WRITE_MISMATCH", "cannot derive GitHub noreply author identity")
    display = name if isinstance(name, str) and name.strip() else login
    return display.strip(), f"{uid}+{login}@users.noreply.github.com"


def _signed_transport_message(client: GitHubPhaseBClient, principal_id: str, subject: str) -> tuple[str, dict[str, str]]:
    name, email = _public_user_identity(client, principal_id)
    message = f"{subject}\n\nSigned-off-by: {name} <{email}>"
    return message, {"name": name, "email": email}


def _pr_head_ref(pr: Mapping[str, Any]) -> str | None:
    head = pr.get("head")
    return head.get("ref") if isinstance(head, Mapping) and isinstance(head.get("ref"), str) else None


def _pr_head_sha(pr: Mapping[str, Any]) -> str | None:
    head = pr.get("head")
    sha = head.get("sha") if isinstance(head, Mapping) else None
    return sha if isinstance(sha, str) and SHA1_RE.fullmatch(sha) else None


def _find_open_pr_by_ref(open_prs: Sequence[Mapping[str, Any]], ref: str) -> Mapping[str, Any] | None:
    rows = [p for p in open_prs if isinstance(p, Mapping) and _pr_head_ref(p) == ref and p.get("state") == "open"]
    if len(rows) > 1:
        raise PhaseBError("TRANSPORT_DUPLICATE_CONFLICT", f"multiple open PRs exist for deterministic ref {ref}")
    return rows[0] if rows else None


def _refresh_pr(client: GitHubPhaseBClient, number: int) -> dict[str, Any]:
    obj = client.request("GET", f"/repos/{client.owner}/{client.repo}/pulls/{number}")
    if not isinstance(obj, dict):
        raise PhaseBError("REPOSITORY_OBSERVATION_INCOMPLETE", f"PR {number} response malformed")
    return obj


def _create_or_reuse_draft_pr(
    client: GitHubPhaseBClient, *, open_prs: Sequence[Mapping[str, Any]], ref: str,
    head_sha: str, title: str, body: str,
) -> dict[str, Any]:
    found = _find_open_pr_by_ref(open_prs, ref)
    if found is not None:
        if _pr_head_sha(found) != head_sha:
            raise PhaseBError("TRANSPORT_REF_CONFLICT", f"open PR for {ref} points to non-equivalent head")
        return dict(found)
    number = client.create_draft_pr(title=title, head_ref=ref, body=body)
    return _refresh_pr(client, number)


def _transport_handoff(
    client: GitHubPhaseBClient,
    *, pr: Mapping[str, Any], head_sha: str, ruleset: RulesetProof,
    retained: dict[str, Any], retained_path: Path,
) -> GateResult:
    if not ruleset.passed:
        return GateResult(False, ruleset.code, ruleset.detail)
    current_pr = _refresh_pr(client, int(pr["number"]))
    if _pr_head_sha(current_pr) != head_sha or current_pr.get("state") != "open":
        return GateResult(False, "TRANSPORT_MOVED_OR_CLOSED", "transport PR head/state changed")
    verify = client.workflow_runs_for_head(head_sha)
    retained["transport_verify"] = _plain(verify)
    if not verify.eligible:
        _write_state(retained_path, retained)
        return GateResult(False, verify.code, "transport awaits exact-head authoritative Verify")

    if current_pr.get("draft") is True:
        node = current_pr.get("node_id")
        if not isinstance(node, str):
            return GateResult(False, "TRANSPORT_READY_REQUIRES_REVIEWED_ADAPTER", "PR node_id unavailable")
        client.mark_pr_ready(node)
        current_pr = _refresh_pr(client, int(current_pr["number"]))
        if current_pr.get("draft") is True:
            return GateResult(False, "TRANSPORT_READY_REQUIRES_REVIEWED_ADAPTER", "PR remained draft after ready mutation")
        # Rerun the same authoritative lineage after readiness. Its run_number
        # stays authoritative; run_attempt must freshly complete successfully.
        if verify.run_id is None:
            return GateResult(False, "VERIFY_AUTHORITATIVE_LINEAGE_UNREADABLE", "authoritative Verify lookup ID unavailable")
        client.rerun_workflow_run(verify.run_id)
        retained["handoff_rerun_requested"] = {
            "run_id": verify.run_id,
            "run_number": verify.authoritative_run_number,
            "previous_run_attempt": verify.current_run_attempt,
        }
        _write_state(retained_path, retained)
        return GateResult(False, "TRANSPORT_HANDOFF_RERUN_REQUESTED", "PR ready; same authoritative Verify lineage rerun requested")

    marker = retained.get("handoff_rerun_requested")
    if isinstance(marker, Mapping) and marker.get("run_number") == verify.authoritative_run_number:
        previous = marker.get("previous_run_attempt")
        if isinstance(previous, int) and isinstance(verify.current_run_attempt, int) and verify.current_run_attempt <= previous:
            return GateResult(False, "LATEST_VERIFY_NOT_SUCCESS", "post-ready rerun current attempt not yet newer")
        if not verify.eligible:
            return GateResult(False, verify.code, "post-ready authoritative rerun not successful")
        retained["trusted_lifecycle_handoff_ready"] = True
        _write_state(retained_path, retained)
        return GateResult(True, "TRANSPORT_READY_FOR_TRUSTED_LIFECYCLE", "fresh post-ready exact-head Verify success established")

    # A pre-existing ready equivalent transport may have been created by an
    # earlier exact invocation. A current exact-head success is sufficient to
    # let the unchanged trusted workflow evaluate it; no ownership is inferred.
    retained["trusted_lifecycle_handoff_ready"] = True
    _write_state(retained_path, retained)
    return GateResult(True, "TRANSPORT_READY_FOR_TRUSTED_LIFECYCLE", "ready transport has current exact-head Verify success")


def _release_expected_tree(
    base_entries: Sequence[Mapping[str, Any]], source_record: Mapping[str, Any], base_tree_sha: str
) -> str:
    deletions = [x["path"] for x in source_record["source_lock_blob_bundle"]]
    return deterministic_tree_sha(base_entries, deletions=deletions, expected_base_tree_sha=base_tree_sha)


def _prepare_release_transport(
    client: GitHubPhaseBClient, *, main_sha: str, main_tree_sha: str,
    main_entries: Sequence[Mapping[str, Any]], source_record: Mapping[str, Any],
    source_epoch_id: str, principal_id: str, open_prs: Sequence[Mapping[str, Any]],
    retained: dict[str, Any], retained_path: Path, ruleset: RulesetProof,
) -> GateResult:
    ref = deterministic_release_ref(source_record["source_task_id"], source_record["worker_id"])
    expected_tree = _release_expected_tree(main_entries, source_record, main_tree_sha)
    existing = client.ref_sha(ref)
    if existing is None:
        server_tree = client.create_tree(main_tree_sha, (), deletions=[x["path"] for x in source_record["source_lock_blob_bundle"]])
        if server_tree != expected_tree:
            return GateResult(False, "SOURCE_EPOCH_RELEASE_PROVENANCE_MISMATCH", "server RELEASE tree != deterministic deletion tree")
        message, author = _signed_transport_message(client, principal_id, f"Release {source_record['source_task_id']} lock")
        head_sha = client.create_commit(message=message, tree_sha=server_tree, parent_sha=main_sha, author=author)
        if not client.create_ref_if_absent(ref, head_sha):
            winner = client.ref_sha(ref)
            if winner != head_sha:
                return GateResult(False, "RELEASE_TRANSPORT_CONFLICT", "concurrent deterministic RELEASE ref winner is non-equivalent")
    else:
        head_sha = existing
        view = _git_commit_view(client, head_sha, with_entries=True)
        parents = view.get("parents")
        if not isinstance(parents, list) or len(parents) != 1 or parents[0].get("sha") != main_sha or view.get("tree", {}).get("sha") != expected_tree:
            return GateResult(False, "RELEASE_TRANSPORT_CONFLICT", "existing deterministic RELEASE ref is stale/non-equivalent; automatic repair refused")
        if {x["path"] for x in source_record["source_lock_blob_bundle"]}.intersection(_entry_map(view["entries"])):
            return GateResult(False, "RELEASE_TRANSPORT_CONFLICT", "existing RELEASE head did not delete exact source bundle")

    retained.update({
        "schema_version": 1,
        "repository": REPOSITORY,
        "source_acquisition_v1": source_record,
        "source_epoch_id": source_epoch_id,
        "release_transport": {
            "base_sha": main_sha,
            "expected_tree_sha": expected_tree,
            "head_ref": ref,
            "head_sha": head_sha,
        },
    })
    pr = _create_or_reuse_draft_pr(
        client, open_prs=open_prs, ref=ref, head_sha=head_sha,
        title=f"Release {source_record['source_task_id']} lock",
        body=f"Deterministic Village v1.3 Phase B RELEASE transport for source epoch `{source_epoch_id}`. PENDING is not ownership.",
    )
    retained["release_transport"]["pr_number"] = pr.get("number")
    _write_state(retained_path, retained)
    return _transport_handoff(client, pr=pr, head_sha=head_sha, ruleset=ruleset, retained=retained, retained_path=retained_path)


def _prove_retained_release(
    client: GitHubPhaseBClient, *, retained: Mapping[str, Any], current_main_sha: str,
    current_entries: Sequence[Mapping[str, Any]],
) -> GateResult:
    source = retained.get("source_acquisition_v1")
    trans = retained.get("release_transport")
    if not isinstance(source, Mapping) or not isinstance(trans, Mapping):
        return GateResult(False, "SOURCE_EPOCH_RELEASE_PROVENANCE_UNAVAILABLE", "retained source/release transport unavailable")
    # The terminal blob must remain exact on current main, while source locks
    # must remain absent. Bare absence is never sufficient.
    by_path = _tree_blob_map(current_entries)
    if by_path.get(source.get("terminal_path"), {}).get("sha") != source.get("terminal_blob_sha"):
        return GateResult(False, "SOURCE_EPOCH_RELEASE_PROVENANCE_MISMATCH", "source terminal object changed after RELEASE")
    for item in source.get("source_lock_blob_bundle", []):
        if item.get("path") in by_path:
            return GateResult(False, "SOURCE_EPOCH_RELEASE_PROVENANCE_MISMATCH", "source lock bundle is present again on current main")
    base_sha = trans.get("base_sha")
    head_sha = trans.get("head_sha")
    expected_tree = trans.get("expected_tree_sha")
    if not all(isinstance(x, str) and SHA1_RE.fullmatch(x) for x in (base_sha, head_sha, expected_tree)):
        return GateResult(False, "SOURCE_EPOCH_RELEASE_PROVENANCE_UNAVAILABLE", "retained RELEASE transport identity malformed")
    head = _git_commit_view(client, head_sha, with_entries=True)
    verify = client.workflow_runs_for_head(head_sha)
    history = _first_parent_history(client, current_main_sha, base_sha)
    return release_provenance_gate(
        source_record=source,
        release_base_sha=base_sha,
        release_expected_tree_sha=expected_tree,
        release_transport_commit=head,
        release_transport_entries=head["entries"],
        release_verify=verify,
        first_parent_history=history,
    )


def _decision_blob_for_id(client: GitHubPhaseBClient, state: Any, entries: Sequence[Mapping[str, Any]], decision_id: str | None) -> tuple[str | None, str | None, str | None]:
    if decision_id is None:
        return None, None, None
    campaign_id = None
    decision_value = None
    for record in state.decisions:
        if record.get("decision_id") == decision_id:
            campaign_id = record.get("campaign_id")
            decision_value = record.get("decision")
            break
    if campaign_id is None:
        raise PhaseBError("CONTINUATION_GATE_UNPROVEN", "requested continuation decision is not canonical")
    # Locate the exact canonical decision object by decoding fresh Git bytes;
    # filenames are not authority for decision identity.
    matches: list[tuple[str, str]] = []
    for path, row in _tree_blob_map(entries).items():
        if not path.startswith(f"coordination/campaigns/{campaign_id}/decisions/") or not path.endswith(".yml"):
            continue
        try:
            obj = json.loads(client.blob_bytes(row["sha"]).decode("utf-8"))
        except Exception as exc:
            raise PhaseBError("CONTINUATION_GATE_UNPROVEN", f"canonical continuation decision bytes unreadable: {exc}") from exc
        if isinstance(obj, Mapping) and obj.get("decision_id") == decision_id:
            matches.append((path, row["sha"]))
    if len(matches) != 1:
        raise PhaseBError("CONTINUATION_GATE_UNPROVEN", "continuation decision exact Git object is missing or ambiguous")
    return decision_id, matches[0][1], decision_value


def _pending_records_from_open_acquire_prs(
    client: GitHubPhaseBClient, *, open_prs: Sequence[Mapping[str, Any]], current_main_sha: str,
    state: Any, now: datetime,
) -> list[dict[str, Any]]:
    records: list[dict[str, Any]] = []
    # This is repository-wide substrate, not a property of any one candidate.
    # Observe it once outside the candidate-local failure boundary so an
    # unavailable current-main tree cannot be swallowed as a malformed PR.
    _, base_entries = client.recursive_tree(current_main_sha)
    bmap = _entry_map(base_entries)
    for pr in open_prs:
        try:
            ref = _pr_head_ref(pr)
            head = _pr_head_sha(pr)
            if not isinstance(ref, str) or not ref.startswith("next-acquire/") or head is None:
                continue
            if pr.get("state") != "open" or pr.get("draft") is True:
                continue
            base = pr.get("base")
            if not isinstance(base, Mapping) or base.get("sha") != current_main_sha or base.get("ref") != "main":
                continue
            commit = _git_commit_view(client, head, with_entries=True)
            if len(commit.get("parents", [])) != 1 or commit["parents"][0].get("sha") != current_main_sha:
                continue
            verify = client.workflow_runs_for_head(head)
            if not verify.eligible:
                continue
            # Find all lock additions and require one byte-identical V3 payload.
            hmap = _entry_map(commit["entries"])
            added = sorted(set(hmap) - set(bmap))
            if not added or any(not p.startswith("coordination/locks/") or not p.endswith(".yml") for p in added):
                continue
            payload = None
            blob_rows = []
            for path in added:
                row = hmap[path]
                if row.get("mode") != "100644" or row.get("type") != "blob":
                    raise PhaseBError("CANDIDATE_LOCAL_MALFORMED", "pending ACQUIRE lock object shape invalid")
                raw = client.blob_bytes(row["sha"])
                parsed = json.loads(raw.decode("utf-8"))
                parse_next_binding(parsed)
                if payload is None:
                    payload = parsed
                elif payload != parsed:
                    raise PhaseBError("CANDIDATE_LOCAL_MALFORMED", "pending collision copies differ")
                blob_rows.append(row)
            if not isinstance(payload, Mapping):
                continue
            task_id = payload.get("task_id")
            if task_id not in state.tasks:
                continue
            collisions = sorted(payload.get("collision_keys", []))
            if collisions != sorted(state.tasks[task_id].get("collision_keys", [])):
                continue
            actor = payload.get("actor")
            principal = actor.get("id") if isinstance(actor, Mapping) else None
            record = {
                "schema_version": 2,
                "reservation_kind": "PENDING_CLAIM",
                "observation_source": "GITHUB_API",
                "repository": REPOSITORY,
                "pr_number": int(pr["number"]),
                "pr_state": "OPEN",
                "draft": False,
                "head_sha": head,
                "base_main_sha": current_main_sha,
                "change_class": "LOCK_ONLY",
                "lock_operation": "ACQUIRE",
                "village_policy": "PASS",
                "verify_conclusion": "SUCCESS",
                "task_id": task_id,
                "worker_id": payload.get("worker_id"),
                "principal_id": principal,
                "collision_keys": collisions,
                "observed_at": _format_time(now.replace(microsecond=0)),
                "lock_expires_at": payload.get("expires_at"),
            }
            records.append(record)
        except (PhaseBError, KeyError, TypeError, ValueError, json.JSONDecodeError):
            # Candidate-local malformed observation is dropped; it never blocks a
            # later valid PENDING observation and never gains reservation authority.
            continue
    return records


def _canonical_continuation_restrictions(state: Any, source_task_id: str) -> tuple[bool, bool]:
    """Derive restrictive continuation facts from fresh typed Village state.

    Free-form stop/continuation prose is deliberately ignored.  Only canonical
    enum states and the existing Claim dependency-validity fields participate.
    These facts can remove same-Campaign scheduling eligibility; they never
    grant Task, Campaign, Truth, review, or mutation authority.
    """
    task = state.tasks[source_task_id]
    campaign_id = task["campaign_id"]
    campaign = state.campaigns[campaign_id]
    stop_reached = task.get("stored_state") == "RETIRED" or campaign.get("strategic_state") == "CLOSED"

    derived_validity = state.derived_claim_validity()

    def reference_usable(reference: Mapping[str, Any]) -> bool:
        claim_id = reference.get("claim_id")
        claim = state.claims.get(claim_id) if isinstance(claim_id, str) else None
        if not isinstance(claim, Mapping) or derived_validity.get(claim_id) != "CURRENT":
            return False
        if claim.get("public_evidence") == "INTENTIONAL_PRIVATE":
            return False
        if claim.get("dependency_use") not in {"ALLOWED", "SCOPED"}:
            return False
        reference_use = reference.get("dependency_use")
        if reference_use is not None and reference_use not in {"ALLOWED", "SCOPED"}:
            return False
        return True

    unusable_dependency = any(
        not reference_usable(assumption)
        for assumption in task.get("assumptions", [])
        if isinstance(assumption, Mapping) and isinstance(assumption.get("claim_id"), str)
    )
    unusable_dependency = unusable_dependency or any(
        not reference_usable(asset)
        for asset in campaign.get("assets", [])
        if isinstance(asset, Mapping) and asset.get("load_bearing") is True
    )
    return stop_reached, unusable_dependency


def _derive_post_release_semantics(
    *, client: GitHubPhaseBClient, root: Path, state: Any, book: Any, entries: Sequence[Mapping[str, Any]], main_sha: str,
    args: Any, source_record: Mapping[str, Any], source_epoch_id: str,
    pending_records: Sequence[Mapping[str, Any]],
):
    from village_next import NextRequest, derive_continuation_decision, recognize_terminal_evidence, select_next_task
    from village_v1_2 import CapabilityProfile

    terminal, errors = recognize_terminal_evidence(
        state,
        task_id=source_record["source_task_id"],
        worker_id=source_record["worker_id"],
        lock_payload=None,
    )
    if terminal is None:
        raise PhaseBError("SOURCE_TERMINAL_UNPROVEN", "; ".join(errors) or "terminal disappeared after RELEASE")
    terminal_blob = _find_tree_blob(entries, terminal.source_path)
    if terminal_blob != source_record.get("terminal_blob_sha"):
        raise PhaseBError("SOURCE_EPOCH_RELEASE_PROVENANCE_MISMATCH", "terminal blob changed after RELEASE")
    capabilities = CapabilityProfile.from_values(
        github_write=getattr(args, "github_write", "unknown"),
        local_compute=getattr(args, "local_compute", "unknown"),
        web_literature=getattr(args, "web_literature", "unknown"),
    )
    canonical_stop_condition_reached, canonical_dependency_followup_unusable = _canonical_continuation_restrictions(
        state,
        source_record["source_task_id"],
    )
    request = NextRequest(
        task_id=source_record["source_task_id"],
        worker_id=source_record["worker_id"],
        principal_id=source_record["principal_id"],
        capabilities=capabilities,
        pending_records=tuple(dict(x) for x in pending_records),
        current_main_sha=main_sha,
        continuation_decision_id=getattr(args, "continuation_decision_id", None),
        canonical_stop_condition_reached=canonical_stop_condition_reached,
        canonical_dependency_followup_unusable=canonical_dependency_followup_unusable,
        fresh_observation_valid=True,
    )
    continuation = derive_continuation_decision(state, book, request, terminal)
    selection_result = select_next_task(state, book, request, continuation)
    if selection_result.selected_task_id is None:
        return None, None, None, None, selection_result

    source_campaign = state.tasks[source_record["source_task_id"]]["campaign_id"]
    decision_id, decision_blob, human_decision = _decision_blob_for_id(client, state, entries, getattr(args, "continuation_decision_id", None))
    context, context_id = derive_continuation_context_v1(
        source_epoch_id=source_epoch_id,
        selection_main_sha=main_sha,
        terminal_class=terminal.terminal_class,
        terminal_blob_sha=terminal_blob,
        source_campaign_id=source_campaign,
        global_admission=state.portfolio.get("global_admission"),
        source_campaign_strategic_state=state.campaigns[source_campaign].get("strategic_state"),
        continuation_gate_required=(terminal.outcome_type in {"CLAIM_CANDIDATE", "COUNTEREXAMPLE", "STRUCTURAL_REDUCTION"}),
        continuation_decision_id=decision_id,
        continuation_decision_blob_sha=decision_blob,
        human_decision=human_decision,
        canonical_stop_condition_reached=canonical_stop_condition_reached,
        canonical_dependency_followup_unusable=canonical_dependency_followup_unusable,
        same_campaign_allowed=continuation.same_campaign_allowed,
        global_fallback_allowed=continuation.global_fallback_allowed,
        approved_followup_task_ids=continuation.approved_followup_task_ids,
        evaluation_followup_task_ids=continuation.evaluation_followup_task_ids,
        reasons=continuation.reasons,
        capability_profile=capabilities,
    )
    selection, selection_id = derive_selection_v1(
        source_epoch_id=source_epoch_id,
        selection_main_sha=main_sha,
        continuation_context_id=context_id,
        pending_records=pending_records,
        hard_eligible_task_ids=selection_result.hard_eligible_task_ids,
        ranked_task_ids=selection_result.ranked_task_ids,
        selected_task_id=selection_result.selected_task_id,
        selected_relation=selection_result.relation,
        worker_id=source_record["worker_id"],
        principal_id=source_record["principal_id"],
    )
    selected_task = state.tasks[selection_result.selected_task_id]
    work_ref = f"research/{selection_result.selected_task_id}/{source_record['worker_id']}"
    intent, intent_id = derive_acquire_intent_v1(
        source_epoch_id=source_epoch_id,
        selection_id=selection_id,
        selection_main_sha=main_sha,
        continuation_context_id=context_id,
        selected_task_id=selection_result.selected_task_id,
        worker_id=source_record["worker_id"],
        principal_id=source_record["principal_id"],
        work_ref=work_ref,
        collision_keys=selected_task.get("collision_keys", []),
    )
    return context, selection, intent, SemanticIds(source_epoch_id, context_id, selection_id, intent_id), selection_result


def _identity_from_existing_candidate(
    client: GitHubPhaseBClient, *, head_sha: str, ids: SemanticIds, base_sha: str,
    base_tree_sha: str, base_entries: Sequence[Mapping[str, Any]], selected_task_id: str,
    worker_id: str, principal_id: str, work_ref: str, collision_keys: Sequence[str], lease_ttl_hours: int,
) -> FrozenAcquireMaterial:
    view = _git_commit_view(client, head_sha, with_entries=True)
    parents = view.get("parents", [])
    if len(parents) != 1 or parents[0].get("sha") != base_sha:
        raise PhaseBError("TRANSPORT_REF_CONFLICT", "existing ACQUIRE ref has wrong base")
    paths = [_lock_path_for_collision(k) for k in sorted(set(collision_keys))]
    hmap = _entry_map(view["entries"])
    payloads = []
    for path in paths:
        row = hmap.get(path)
        if row is None or row.get("mode") != "100644" or row.get("type") != "blob":
            raise PhaseBError("TRANSPORT_REF_CONFLICT", "existing ACQUIRE ref lacks exact lock object")
        raw = client.blob_bytes(row["sha"])
        payloads.append(json.loads(raw.decode("utf-8")))
    if not payloads or any(x != payloads[0] for x in payloads[1:]):
        raise PhaseBError("TRANSPORT_REF_CONFLICT", "existing ACQUIRE lock copies differ")
    existing_ids = parse_next_binding(payloads[0])
    if existing_ids != ids:
        raise PhaseBError("TRANSPORT_REF_CONFLICT", "existing deterministic key has different semantic binding")
    try:
        acquired = _parse_time(payloads[0]["acquired_at"])
    except Exception as exc:
        raise PhaseBError("TRANSPORT_REF_CONFLICT", f"existing first-creator timestamp invalid: {exc}") from exc
    material = freeze_acquire_material(
        semantic_ids=ids,
        base_sha=base_sha,
        base_tree_sha=base_tree_sha,
        base_tree_entries=base_entries,
        selected_task_id=selected_task_id,
        worker_id=worker_id,
        principal_id=principal_id,
        work_ref=work_ref,
        collision_keys=collision_keys,
        acquired_at=acquired,
        lease_ttl_hours=lease_ttl_hours,
    )
    if view.get("tree", {}).get("sha") != material.identity.expected_canonical_tree_sha:
        raise PhaseBError("TRANSPORT_REF_CONFLICT", "existing deterministic ACQUIRE key has non-equivalent tree")
    return material


def _prepare_acquire_transport(
    client: GitHubPhaseBClient, *, main_sha: str, main_tree_sha: str,
    main_entries: Sequence[Mapping[str, Any]], source_record: Mapping[str, Any],
    context: Mapping[str, Any], selection: Mapping[str, Any], intent: Mapping[str, Any], ids: SemanticIds,
    selection_result: Any, state: Any, principal_id: str, open_prs: Sequence[Mapping[str, Any]],
    retained: dict[str, Any], retained_path: Path, ruleset: RulesetProof,
) -> GateResult:
    selected = selection_result.selected_task_id
    task = state.tasks[selected]
    ttl = int(task.get("lease_ttl_hours", 168))
    collisions = tuple(sorted(set(task.get("collision_keys", []))))
    work_ref = f"research/{selected}/{source_record['worker_id']}"
    ref = deterministic_acquire_ref(ids.acquire_intent_id, selected, source_record["worker_id"])
    existing = client.ref_sha(ref)
    if existing is not None:
        material = _identity_from_existing_candidate(
            client, head_sha=existing, ids=ids, base_sha=main_sha, base_tree_sha=main_tree_sha,
            base_entries=main_entries, selected_task_id=selected, worker_id=source_record["worker_id"],
            principal_id=principal_id, work_ref=work_ref, collision_keys=collisions, lease_ttl_hours=ttl,
        )
        head_sha = existing
    else:
        acquired = datetime.now(timezone.utc).replace(microsecond=0)
        material = freeze_acquire_material(
            semantic_ids=ids,
            base_sha=main_sha,
            base_tree_sha=main_tree_sha,
            base_tree_entries=main_entries,
            selected_task_id=selected,
            worker_id=source_record["worker_id"],
            principal_id=principal_id,
            work_ref=work_ref,
            collision_keys=collisions,
            acquired_at=acquired,
            lease_ttl_hours=ttl,
        )
        for obj in material.identity.exact_lock_objects:
            raw = material.lock_bytes[obj.path]
            server_blob = client.create_blob(raw)
            if server_blob != obj.blob_sha:
                raise PhaseBError("GITHUB_TRANSPORT_WRITE_MISMATCH", "created lock blob differs from frozen object")
        server_tree = client.create_tree(main_tree_sha, material.identity.exact_lock_objects)
        if server_tree != material.identity.expected_canonical_tree_sha:
            raise PhaseBError("GITHUB_TRANSPORT_WRITE_MISMATCH", "server ACQUIRE tree differs from precomputed T")
        message, author = _signed_transport_message(client, principal_id, f"Acquire {selected} Village lock")
        head_sha = client.create_commit(message=message, tree_sha=server_tree, parent_sha=main_sha, author=author)
        if not client.create_ref_if_absent(ref, head_sha):
            winner = client.ref_sha(ref)
            if winner is None:
                raise PhaseBError("TRANSPORT_REF_CONFLICT", "deterministic ref creation race lost without readable winner")
            material = _identity_from_existing_candidate(
                client, head_sha=winner, ids=ids, base_sha=main_sha, base_tree_sha=main_tree_sha,
                base_entries=main_entries, selected_task_id=selected, worker_id=source_record["worker_id"],
                principal_id=principal_id, work_ref=work_ref, collision_keys=collisions, lease_ttl_hours=ttl,
            )
            head_sha = winner

    candidate = _git_commit_view(client, head_sha, with_entries=True)
    candidate_lock_bytes = {o.path: client.blob_bytes(o.blob_sha) for o in material.identity.exact_lock_objects}
    verify = client.workflow_runs_for_head(head_sha)
    # Before the first draft PR exists there can be no PR-head Verify. Candidate
    # content is still proven independently here; CI is gated after PR creation.
    content = candidate_content_gate(
        expected_identity=material.identity,
        independently_derived_ids=ids,
        candidate_lock_bytes=candidate_lock_bytes,
        candidate_exact_objects=material.identity.exact_lock_objects,
        candidate_tree_sha=candidate.get("tree", {}).get("sha", ""),
    )
    if not content.allowed:
        return content

    retained.update({
        "schema_version": 1,
        "repository": REPOSITORY,
        "source_acquisition_v1": dict(source_record),
        "source_epoch_id": ids.source_epoch_id,
        "continuation_context_v1": dict(context),
        "continuation_context_id": ids.continuation_context_id,
        "selection_v1": dict(selection),
        "selection_id": ids.selection_id,
        "acquire_intent_v1": dict(intent),
        "acquire_intent_id": ids.acquire_intent_id,
        "canonical_acquire_identity_v3": material.identity.to_dict(),
        "canonical_acquire_id": material.canonical_acquire_id,
        "acquire_transport": {"head_ref": ref, "head_sha": head_sha, "base_sha": main_sha},
    })
    validate_retained_state_chain(retained)
    pr = _create_or_reuse_draft_pr(
        client, open_prs=open_prs, ref=ref, head_sha=head_sha,
        title=f"Acquire {selected} Village lock",
        body=f"Deterministic Village v1.3 Phase B ACQUIRE transport `{ids.acquire_intent_id}`. PENDING is not ownership.",
    )
    if f"gh:{pr.get('user', {}).get('login', '')}" != principal_id:
        return GateResult(False, "CANONICAL_ACQUIRE_PRINCIPAL_MISMATCH", "transport PR principal differs from frozen acquire intent")
    retained["acquire_transport"]["pr_number"] = pr.get("number")
    _write_state(retained_path, retained)

    verify = client.workflow_runs_for_head(head_sha)
    if verify.eligible:
        pre = premerge_transport_gate(
            identity=material.identity,
            independently_derived_ids=ids,
            base_entries=main_entries,
            candidate_commit=candidate,
            candidate_entries=candidate["entries"],
            candidate_lock_bytes=candidate_lock_bytes,
            verify=verify,
            ruleset=ruleset,
            current_main_sha=client.current_main_sha(),
        )
        if not pre.allowed:
            return pre
    return _transport_handoff(client, pr=pr, head_sha=head_sha, ruleset=ruleset, retained=retained, retained_path=retained_path)


def _confirm_retained_acquire(
    client: GitHubPhaseBClient, *, retained: Mapping[str, Any], current_main_sha: str,
    current_entries: Sequence[Mapping[str, Any]], now: datetime, ruleset: RulesetProof,
) -> GateResult:
    raw_identity = retained.get("canonical_acquire_identity_v3")
    if not isinstance(raw_identity, Mapping):
        return GateResult(False, "CANONICAL_ACQUIRE_HISTORY_UNPROVEN", "retained V3 identity unavailable")
    try:
        validate_retained_state_chain(retained)
        identity = CanonicalAcquireIdentityV3.from_dict(raw_identity)
        history = _first_parent_history(client, current_main_sha, identity.expected_base_sha)
        lock_bytes = {o.path: client.blob_bytes(_find_tree_blob(current_entries, o.path)) for o in identity.exact_lock_objects}
    except PhaseBError as exc:
        return GateResult(False, exc.code, exc.message)
    return canonical_transition_gate(
        identity=identity,
        first_parent_history=history,
        current_entries=current_entries,
        current_lock_bytes=lock_bytes,
        ruleset=ruleset,
        now=now,
    )


def cli_next(root: Path, args: Any) -> int:
    """Production Phase B operator orchestration around the accepted Phase A core.

    The function is deliberately rerunnable. Each invocation starts from fresh
    GitHub/current-main evidence. Transport refs/PRs are preparation only; only
    the unchanged trusted lifecycle may canonicalise one RELEASE/ACQUIRE, and
    ACTIVE_NEXT is emitted only after fresh canonical V3 read-back succeeds.
    """
    if getattr(args, "github_write", "unknown") != "yes":
        print("FAIL: Phase B /next transport requires --github-write yes")
        return 2
    token_name = getattr(args, "github_token_env", "GITHUB_TOKEN")
    token = os.environ.get(token_name, "")
    state_file_arg = getattr(args, "phase_b_state_file", ".git/village-next-phase-b.json")
    state_path = Path(state_file_arg)
    if not state_path.is_absolute():
        state_path = root / state_path
    state_path = state_path.resolve()
    now = datetime.now(timezone.utc).replace(microsecond=0)
    try:
        client = GitHubPhaseBClient(token)
        main_sha = client.current_main_sha()
        asserted_main = getattr(args, "current_main_sha", None)
        if asserted_main and asserted_main != main_sha:
            raise PhaseBError("CANONICAL_ACQUIRE_BASE_MISMATCH", f"--current-main-sha assertion {asserted_main} != fresh remote main {main_sha}")
        asserted_principal = getattr(args, "principal_id", "")
        authenticated_principal = client.authenticated_principal_id()
        if asserted_principal != authenticated_principal:
            raise PhaseBError("PRINCIPAL_AUTHENTICATION_MISMATCH", f"--principal-id assertion {asserted_principal!r} != authenticated principal {authenticated_principal!r}")
        local_sha = _local_head_sha(root)
        if local_sha != main_sha:
            raise PhaseBError("STALE_TRUSTED_LOCAL_MAIN", f"local checkout {local_sha} != fresh remote main {main_sha}; update exact main and rerun")
        main_tree_sha, main_entries = client.recursive_tree(main_sha)
        open_prs = client.open_prs()
        observation = repository_observation_gate(
            main_sha=main_sha, tree_complete=True, open_prs_complete=True,
            principal_id=getattr(args, "principal_id", ""),
        )
        if not observation.allowed:
            raise PhaseBError(observation.code, observation.detail)
        ruleset = client.ruleset_proof()
        if not ruleset.passed:
            raise PhaseBError(ruleset.code, ruleset.detail)

        from village_core import VillageState
        from village_next import NextPhase, NextRequest, NextStatus, derive_next_state
        from village_rank import EvaluationBook
        from village_v1_2 import CapabilityProfile, load_actor_policy, worker_lock_errors

        state = VillageState(root, now=now).load()
        errors = list(state.validate()) + worker_lock_errors(state, load_actor_policy(root))
        book = EvaluationBook(root, state).load()
        errors.extend(book.errors)
        if errors:
            raise PhaseBError("REPOSITORY_OBSERVATION_INCOMPLETE", "current main Village state invalid: " + "; ".join(errors[:10]))

        task_id = getattr(args, "task_id", "")
        worker_id = getattr(args, "worker_id", "")
        principal_id = getattr(args, "principal_id", "")
        if task_id not in state.tasks or not WORKER_RE.fullmatch(worker_id or "") or not PRINCIPAL_RE.fullmatch(principal_id or ""):
            raise PhaseBError("SOURCE_EPOCH_UNPROVEN", "invalid Task/worker/principal input")

        source_bundle = _source_bundle_from_state(state, task_id, worker_id, principal_id)
        if source_bundle is not None:
            _require_source_bundle_on_fresh_main(
                client,
                state=state,
                bundle=source_bundle,
                main_entries=main_entries,
            )

        capabilities = CapabilityProfile.from_values(
            github_write=getattr(args, "github_write", "unknown"),
            local_compute=getattr(args, "local_compute", "unknown"),
            web_literature=getattr(args, "web_literature", "unknown"),
        )
        phase_a = derive_next_state(
            state,
            book,
            NextRequest(
                task_id=task_id,
                worker_id=worker_id,
                principal_id=principal_id,
                capabilities=capabilities,
                current_main_sha=main_sha,
                continuation_decision_id=getattr(args, "continuation_decision_id", None),
                fresh_observation_valid=True,
            ),
        )
        if phase_a.phase == NextPhase.ACTIVE_WORK:
            if phase_a.status == NextStatus.ACTIVE_WORK:
                print("ACTIVE_WORK")
                return 0
            raise PhaseBError(
                "SOURCE_EPOCH_UNPROVEN",
                "; ".join(phase_a.errors) or "Phase A rejected current source ownership",
            )

        retained = _read_state(state_path) or {}

        # If a retained acquire exists, canonical current-main reconstruction is
        # checked before considering any transport retry. This can confirm
        # ACTIVE_NEXT even when squash made M != H.
        if retained.get("canonical_acquire_identity_v3") is not None:
            confirmed = _confirm_retained_acquire(
                client, retained=retained, current_main_sha=main_sha,
                current_entries=main_entries, now=now, ruleset=ruleset,
            )
            if confirmed.allowed:
                print("ACTIVE_NEXT")
                print(f"CANONICAL_ACQUIRE_ID={retained['canonical_acquire_id']}")
                print(f"TASK={retained['acquire_intent_v1']['selected_task_id']}")
                print(f"MAIN={main_sha}")
                return 0

            # A retained ACQUIRE transport is retry authority only while its
            # source epoch is still canonically unconsumed. Prove the exact
            # RELEASE and consumption history before any handoff write.
            release = _prove_retained_release(
                client,
                retained=retained,
                current_main_sha=main_sha,
                current_entries=main_entries,
            )
            if not release.allowed:
                raise PhaseBError(release.code, release.detail)
            source_id = retained.get("source_epoch_id")
            release_transport = retained.get("release_transport")
            release_base_sha = release_transport.get("base_sha") if isinstance(release_transport, Mapping) else None
            if not isinstance(source_id, str) or not SHA256_RE.fullmatch(source_id):
                raise PhaseBError("SOURCE_EPOCH_RELEASE_PROVENANCE_UNAVAILABLE", "retained source epoch unavailable")
            if not isinstance(release_base_sha, str) or not SHA1_RE.fullmatch(release_base_sha):
                raise PhaseBError("SOURCE_EPOCH_RELEASE_PROVENANCE_UNAVAILABLE", "retained RELEASE base unavailable")
            consumption = _source_epoch_consumption_gate(
                client,
                current_main_sha=main_sha,
                release_base_sha=release_base_sha,
                source_epoch_id=source_id,
            )
            if not consumption.allowed:
                raise PhaseBError(consumption.code, consumption.detail)

            # A still-open exact transport may simply be awaiting trusted merge.
            trans = retained.get("acquire_transport")
            if isinstance(trans, Mapping):
                ref = trans.get("head_ref"); head = trans.get("head_sha")
                pr = _find_open_pr_by_ref(open_prs, ref) if isinstance(ref, str) else None
                if pr is not None and head == _pr_head_sha(pr):
                    handoff = _transport_handoff(client, pr=pr, head_sha=head, ruleset=ruleset, retained=retained, retained_path=state_path)
                    print(handoff.code)
                    return 0 if handoff.allowed else 3
            # If canonical acquisition cannot be proven and no exact open
            # transport exists, do not silently discard/re-rank the intent.
            raise PhaseBError(confirmed.code, confirmed.detail)

        if source_bundle is not None:
            source_record, source_id, _terminal = _source_record_from_fresh_main(
                client, state=state, main_sha=main_sha, main_entries=main_entries,
                task_id=task_id, worker_id=worker_id, principal_id=principal_id,
            )
            if retained.get("source_epoch_id") not in (None, source_id):
                raise PhaseBError("OLD_ACQUISITION_REPLAY", "retained source epoch differs from fresh current acquisition")
            outcome = _prepare_release_transport(
                client, main_sha=main_sha, main_tree_sha=main_tree_sha, main_entries=main_entries,
                source_record=source_record, source_epoch_id=source_id, principal_id=principal_id,
                open_prs=open_prs, retained=retained, retained_path=state_path, ruleset=ruleset,
            )
            print(outcome.code)
            return 0 if outcome.allowed else 3

        # No source lock now: source RELEASE provenance must be proven from the
        # retained exact epoch and canonical first-parent history before ranking.
        if not retained:
            raise PhaseBError("SOURCE_EPOCH_RELEASE_PROVENANCE_UNAVAILABLE", "source lock absent and no retained exact source epoch exists")
        if retained.get("source_acquisition_v1", {}).get("source_task_id") != task_id or retained.get("source_acquisition_v1", {}).get("worker_id") != worker_id or retained.get("source_acquisition_v1", {}).get("principal_id") != principal_id:
            raise PhaseBError("OLD_ACQUISITION_REPLAY", "retained source identity differs from requested source")
        release = _prove_retained_release(client, retained=retained, current_main_sha=main_sha, current_entries=main_entries)
        if not release.allowed:
            raise PhaseBError(release.code, release.detail)

        source_record = retained["source_acquisition_v1"]
        source_id = retained["source_epoch_id"]
        release_transport = retained.get("release_transport")
        release_base_sha = release_transport.get("base_sha") if isinstance(release_transport, Mapping) else None
        if not isinstance(release_base_sha, str) or not SHA1_RE.fullmatch(release_base_sha):
            raise PhaseBError("SOURCE_EPOCH_RELEASE_PROVENANCE_UNAVAILABLE", "retained RELEASE base unavailable")
        consumption = _source_epoch_consumption_gate(
            client,
            current_main_sha=main_sha,
            release_base_sha=release_base_sha,
            source_epoch_id=source_id,
        )
        if not consumption.allowed:
            raise PhaseBError(consumption.code, consumption.detail)

        pending = _pending_records_from_open_acquire_prs(
            client, open_prs=open_prs, current_main_sha=main_sha, state=state, now=now,
        )
        derived = _derive_post_release_semantics(
            client=client, root=root, state=state, book=book, entries=main_entries, main_sha=main_sha,
            args=args, source_record=source_record, source_epoch_id=source_id,
            pending_records=pending,
        )
        context, selection, intent, ids, selection_result = derived
        if ids is None:
            print(selection_result.status.value)
            return 0

        # If a preexisting retained Selection/Intent does not exactly match fresh
        # post-RELEASE derivation, it is discarded before transport authority.
        for key, fresh in (
            ("continuation_context_id", ids.continuation_context_id),
            ("selection_id", ids.selection_id),
            ("acquire_intent_id", ids.acquire_intent_id),
        ):
            old = retained.get(key)
            if old is not None and old != fresh:
                for drop in (
                    "continuation_context_v1", "continuation_context_id", "selection_v1", "selection_id",
                    "acquire_intent_v1", "acquire_intent_id", "canonical_acquire_identity_v3",
                    "canonical_acquire_id", "acquire_transport", "transport_verify", "handoff_rerun_requested",
                    "trusted_lifecycle_handoff_ready",
                ):
                    retained.pop(drop, None)
                break

        outcome = _prepare_acquire_transport(
            client, main_sha=main_sha, main_tree_sha=main_tree_sha, main_entries=main_entries,
            source_record=source_record, context=context, selection=selection, intent=intent, ids=ids,
            selection_result=selection_result, state=state, principal_id=principal_id,
            open_prs=open_prs, retained=retained, retained_path=state_path, ruleset=ruleset,
        )
        print(outcome.code)
        return 0 if outcome.allowed else 3
    except (PhaseBError, json.JSONDecodeError) as exc:
        code = exc.code if isinstance(exc, PhaseBError) else "RETAINED_STATE_INVALID"
        print(f"FAIL: {code}: {exc}")
        return 2


__all__ = [
    "REPOSITORY", "VERIFY_WORKFLOW_ID", "VERIFY_WORKFLOW_PATH", "VERIFY_WORKFLOW_NAME", "VERIFY_EVENT",
    "TRUTH_AUTHORITY", "REVIEW_AUTHORITY", "FORBIDDEN_AUTOMATIC_OPERATIONS",
    "PhaseBError", "GateResult", "SemanticIds", "ExactLockObject", "CanonicalAcquireIdentityV3",
    "FrozenAcquireMaterial", "VerifyObservation", "RulesetProof",
    "canonical_bytes", "canonical_digest", "git_blob_oid", "deterministic_tree_sha",
    "deterministic_lock_id", "deterministic_acquire_ref", "deterministic_release_ref",
    "freeze_acquire_material", "parse_next_binding", "validate_v3_identity",
    "reconstruct_v3_from_lock_payload", "candidate_content_gate",
    "derive_source_acquisition_v1", "derive_continuation_context_v1", "derive_selection_v1",
    "derive_acquire_intent_v1", "validate_retained_state_chain",
    "authoritative_verify_lineage", "prove_ruleset", "repository_observation_gate",
    "is_pending_ownership", "choose_lifecycle_candidate", "premerge_transport_gate",
    "canonical_transition_gate", "release_provenance_gate", "GitHubPhaseBClient", "cli_next",
]
