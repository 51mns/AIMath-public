#!/usr/bin/env python3
# SPDX-FileCopyrightText: 2026 AIMath contributors
# SPDX-License-Identifier: Apache-2.0
from __future__ import annotations

from pathlib import Path
import argparse
import re
from typing import Any

try:
    import yaml
except Exception as exc:
    yaml = None
    YAML_IMPORT_ERROR = exc
else:
    YAML_IMPORT_ERROR = None

TRUSTED_LIFECYCLE_WORKFLOW = ".github/workflows/lock-auto-activate.yml"
ALLOWED_TRUSTED_WRITE_SCOPES = {"contents"}
SHA40_RE = re.compile(r"^[0-9a-f]{40}$")
SECRET_EXPR_RE = re.compile(r"\$\{\{[^}]*\bsecrets\s*\.\s*[A-Za-z0-9_]+[^}]*\}\}", re.I | re.S)
GITHUB_TOKEN_EXPR_RE = re.compile(r"\$\{\{[^}]*\bgithub\s*\.\s*token\b[^}]*\}\}", re.I | re.S)
PR_HEAD_EXPR_RE = re.compile(r"\$\{\{[^}]*\b(?:pull_request\s*\.\s*head|head_sha)\b[^}]*\}\}", re.I | re.S)
TRUSTED_ACTIVATION_COMMAND = "python3 scripts/lock_auto_activate.py"
TRUSTED_GITHUB_TOKEN_EXPR = "${{ github.token }}"
TRUSTED_SOURCE_RUN_EXPR = "${{ github.event.workflow_run.id }}"


def _load_yaml(text: str, where: str) -> tuple[Any | None, list[str]]:
    if yaml is None:
        return None, [f"{where}: PyYAML is required for structural workflow security parsing: {YAML_IMPORT_ERROR}"]
    try:
        value = yaml.load(text, Loader=yaml.BaseLoader)
    except Exception as exc:
        return None, [f"{where}: invalid YAML: {exc}"]
    if not isinstance(value, dict):
        return None, [f"{where}: workflow/action root must be a mapping"]
    return value, []


def _walk_scalars(value: Any):
    if isinstance(value, str):
        yield value
    elif isinstance(value, dict):
        for key, item in value.items():
            if isinstance(key, str):
                yield key
            yield from _walk_scalars(item)
    elif isinstance(value, list):
        for item in value:
            yield from _walk_scalars(item)


def _github_token_locations(value: Any, path: tuple[str, ...] = ()) -> list[tuple[str, ...]]:
    out: list[tuple[str, ...]] = []
    if isinstance(value, str):
        if GITHUB_TOKEN_EXPR_RE.search(value):
            out.append(path)
    elif isinstance(value, dict):
        for key, item in value.items():
            out.extend(_github_token_locations(item, (*path, str(key))))
    elif isinstance(value, list):
        for index, item in enumerate(value):
            out.extend(_github_token_locations(item, (*path, str(index))))
    return out


def _permissions_errors(value: Any, *, trusted_write: bool, where: str) -> list[str]:
    errors: list[str] = []
    if value is None:
        return [f"{where}: workflow must explicitly declare top-level permissions"]
    if isinstance(value, str):
        low = value.strip().lower()
        if low == "write-all":
            errors.append(f"{where}: permissions: write-all is forbidden")
        elif low not in {"read-all", "{}"}:
            errors.append(f"{where}: unsupported scalar permissions value {value!r}")
        return errors
    if not isinstance(value, dict):
        return [f"{where}: permissions must be a mapping, read-all, or write-all"]
    for scope, access in value.items():
        scope_s = str(scope).strip().lower()
        access_s = str(access).strip().lower()
        if access_s == "write":
            if not trusted_write:
                errors.append(f"{where}: write permission {scope_s!r} is forbidden outside trusted lifecycle workflow")
            elif scope_s not in ALLOWED_TRUSTED_WRITE_SCOPES:
                errors.append(f"{where}: unknown/unapproved write permission {scope_s!r}")
        elif access_s not in {"read", "none"}:
            errors.append(f"{where}: unsupported permission value {scope_s}: {access_s}")
    return errors


def _trigger_errors(doc: dict[str, Any], *, where: str) -> list[str]:
    trigger = doc.get("on")
    if isinstance(trigger, str):
        names = {trigger}
    elif isinstance(trigger, list):
        names = {str(x) for x in trigger}
    elif isinstance(trigger, dict):
        names = {str(x) for x in trigger}
    else:
        names = set()
    return [f"{where}: pull_request_target is forbidden"] if "pull_request_target" in names else []


def _external_uses_errors(uses: str, *, where: str) -> list[str]:
    if uses.startswith("./"):
        return []
    if uses.startswith("docker://"):
        return [f"{where}: docker:// actions are forbidden; use an audited full-SHA GitHub action instead"]
    if "@" not in uses:
        return [f"{where}: external action/reusable workflow must be pinned to a full commit SHA: {uses}"]
    _, ref = uses.rsplit("@", 1)
    if not SHA40_RE.fullmatch(ref):
        return [f"{where}: external action/reusable workflow ref must be a full 40-hex commit SHA: {uses}"]
    return []


def _checkout_errors(step: dict[str, Any], *, trusted_write: bool, where: str) -> list[str]:
    uses = str(step.get("uses", ""))
    if not uses.startswith("actions/checkout@"):
        return []
    errors: list[str] = []
    with_map = step.get("with")
    if not isinstance(with_map, dict):
        with_map = {}
    if str(with_map.get("persist-credentials", "")).strip().lower() != "false":
        errors.append(f"{where}: actions/checkout must explicitly set persist-credentials: false")
    if trusted_write:
        ref = str(with_map.get("ref", "")).strip()
        if ref != "main":
            errors.append(f"{where}: trusted write workflow checkout must use literal ref: main")
        if PR_HEAD_EXPR_RE.search(ref) or "pull_request" in ref.lower():
            errors.append(f"{where}: trusted write workflow must never checkout PR head")
    return errors


def _resolve_local_action(root: Path, uses: str) -> Path | None:
    if not uses.startswith("./"):
        return None
    candidate = (root / uses[2:]).resolve()
    try:
        candidate.relative_to(root.resolve())
    except ValueError:
        return None
    for name in ("action.yml", "action.yaml"):
        manifest = candidate / name
        if manifest.is_file() and not manifest.is_symlink():
            return manifest
    return None


def _local_action_errors(root: Path, manifest: Path, *, seen: set[Path] | None = None) -> list[str]:
    seen = seen or set()
    manifest = manifest.resolve()
    if manifest in seen:
        return [f"{manifest.relative_to(root)}: recursive local action reference"]
    seen.add(manifest)
    rel = manifest.relative_to(root).as_posix()
    try:
        text = manifest.read_text(encoding="utf-8")
    except Exception as exc:
        return [f"{rel}: cannot read local action manifest: {exc}"]
    doc, errors = _load_yaml(text, rel)
    if errors:
        return errors
    assert isinstance(doc, dict)
    runs = doc.get("runs")
    if not isinstance(runs, dict) or str(runs.get("using", "")).lower() != "composite":
        return [f"{rel}: local actions used by workflows must be structurally inspectable composite actions"]
    for scalar in _walk_scalars(doc):
        if SECRET_EXPR_RE.search(scalar):
            errors.append(f"{rel}: local composite action references secrets")
        if GITHUB_TOKEN_EXPR_RE.search(scalar):
            errors.append(f"{rel}: local composite action may not acquire caller github.token")
    steps = runs.get("steps", [])
    if not isinstance(steps, list):
        errors.append(f"{rel}: composite runs.steps must be a list")
        return errors
    for i, step in enumerate(steps):
        if not isinstance(step, dict):
            errors.append(f"{rel}: composite step {i} must be a mapping")
            continue
        uses = step.get("uses")
        if isinstance(uses, str):
            errors.extend(_external_uses_errors(uses, where=f"{rel}: step {i}"))
            if uses.startswith("./"):
                nested = _resolve_local_action(root, uses)
                if nested is None:
                    errors.append(f"{rel}: local action reference is missing/unsafe: {uses}")
                else:
                    errors.extend(_local_action_errors(root, nested, seen=set(seen)))
    return errors


def _trusted_lifecycle_structure_errors(doc: dict[str, Any], *, path: str) -> list[str]:
    """Fail closed unless the write-capable lifecycle workflow matches the audited Phase A shape."""
    errors: list[str] = []
    allowed_top = {"name", "on", "permissions", "concurrency", "jobs"}
    if set(doc) != allowed_top:
        errors.append(f"{path}: trusted lifecycle top-level keys must be exactly {sorted(allowed_top)}")
    if str(doc.get("name", "")) != "Activate validated Village lock":
        errors.append(f"{path}: trusted lifecycle workflow name is not the audited value")

    permissions = doc.get("permissions")
    expected_permissions = {"actions": "read", "contents": "write", "pull-requests": "read"}
    if permissions != expected_permissions:
        errors.append(f"{path}: trusted lifecycle permissions must be exactly actions:read, contents:write, pull-requests:read")

    concurrency = doc.get("concurrency")
    if concurrency != {"group": "village-lock-lifecycle", "cancel-in-progress": "false"}:
        errors.append(f"{path}: trusted lifecycle concurrency must exactly match the audited serialization policy")

    trigger = doc.get("on")
    if trigger != {"workflow_run": {"workflows": ["Verify public release"], "types": ["completed"]}}:
        errors.append(f"{path}: trusted lifecycle workflow must be triggered only by completed Verify public release workflow_run")

    jobs = doc.get("jobs")
    if not isinstance(jobs, dict) or set(jobs) != {"activate"}:
        errors.append(f"{path}: trusted lifecycle workflow must contain exactly the activate job")
        return errors
    job = jobs.get("activate")
    if not isinstance(job, dict):
        errors.append(f"{path}: trusted lifecycle activate job must be a mapping")
        return errors
    allowed_job = {"if", "runs-on", "timeout-minutes", "steps"}
    if set(job) != allowed_job:
        errors.append(f"{path}: trusted lifecycle activate job keys must be exactly {sorted(allowed_job)}")
    if str(job.get("if", "")) != "github.event.workflow_run.conclusion == 'success'":
        errors.append(f"{path}: trusted lifecycle activate condition must require successful source Verify run")
    if str(job.get("runs-on", "")) != "ubuntu-latest":
        errors.append(f"{path}: trusted lifecycle runner must be the audited ubuntu-latest runner")
    if str(job.get("timeout-minutes", "")) != "5":
        errors.append(f"{path}: trusted lifecycle timeout-minutes must be exactly 5")

    steps = job.get("steps")
    if not isinstance(steps, list) or len(steps) != 3:
        errors.append(f"{path}: trusted lifecycle must contain exactly three audited steps")
        return errors
    if not all(isinstance(step, dict) for step in steps):
        errors.append(f"{path}: every trusted lifecycle step must be a mapping")
        return errors

    checkout, setup_python, activation = steps
    if set(checkout) != {"name", "uses", "with"}:
        errors.append(f"{path}: trusted checkout step has unknown/unapproved keys")
    checkout_uses = str(checkout.get("uses", ""))
    if not checkout_uses.startswith("actions/checkout@"):
        errors.append(f"{path}: trusted step 0 must be actions/checkout")
    else:
        errors.extend(_external_uses_errors(checkout_uses, where=f"{path}: trusted checkout"))
    if checkout.get("with") != {"ref": "main", "fetch-depth": "1", "persist-credentials": "false"}:
        errors.append(f"{path}: trusted checkout inputs must be exactly ref:main, fetch-depth:1, persist-credentials:false")

    if set(setup_python) != {"name", "uses", "with"}:
        errors.append(f"{path}: trusted setup-python step has unknown/unapproved keys")
    setup_uses = str(setup_python.get("uses", ""))
    if not setup_uses.startswith("actions/setup-python@"):
        errors.append(f"{path}: trusted step 1 must be actions/setup-python")
    else:
        errors.extend(_external_uses_errors(setup_uses, where=f"{path}: trusted setup-python"))
    if setup_python.get("with") != {"python-version": "3.12"}:
        errors.append(f"{path}: trusted setup-python inputs must be exactly python-version: 3.12")

    if set(activation) != {"name", "env", "run"}:
        errors.append(f"{path}: trusted activation step has unknown/unapproved keys")
    if str(activation.get("run", "")).strip() != TRUSTED_ACTIVATION_COMMAND:
        errors.append(f"{path}: trusted activation command must be exactly {TRUSTED_ACTIVATION_COMMAND}")
    expected_env = {
        "GITHUB_TOKEN": TRUSTED_GITHUB_TOKEN_EXPR,
        "SOURCE_RUN_ID": TRUSTED_SOURCE_RUN_EXPR,
    }
    if activation.get("env") != expected_env:
        errors.append(f"{path}: trusted activation env must contain exactly audited GITHUB_TOKEN and SOURCE_RUN_ID bindings")

    allowed_token_location = ("jobs", "activate", "steps", "2", "env", "GITHUB_TOKEN")
    token_locations = _github_token_locations(doc)
    if token_locations != [allowed_token_location]:
        rendered = [".".join(parts) for parts in token_locations]
        errors.append(f"{path}: github.token may appear only at jobs.activate.steps.2.env.GITHUB_TOKEN; found {rendered}")

    for i, step in enumerate(steps):
        uses = step.get("uses")
        if isinstance(uses, str) and uses.startswith("./"):
            errors.append(f"{path}: trusted lifecycle local composite actions are forbidden in Phase A: step {i}")
        if isinstance(uses, str) and uses.startswith("docker://"):
            errors.append(f"{path}: trusted lifecycle docker:// actions are forbidden in Phase A: step {i}")
    return errors


def workflow_document_errors(doc: dict[str, Any], *, path: str, root: Path | None = None) -> list[str]:
    trusted_write = path == TRUSTED_LIFECYCLE_WORKFLOW
    errors = _trigger_errors(doc, where=path)
    errors.extend(_permissions_errors(doc.get("permissions"), trusted_write=trusted_write, where=path))
    for scalar in _walk_scalars(doc):
        if SECRET_EXPR_RE.search(scalar):
            errors.append(f"{path}: repository/environment secrets expressions are forbidden in contribution workflows")
    jobs = doc.get("jobs")
    if not isinstance(jobs, dict) or not jobs:
        errors.append(f"{path}: jobs must be a non-empty mapping")
        return list(dict.fromkeys(errors))
    for job_name, job in jobs.items():
        if not isinstance(job, dict):
            errors.append(f"{path}: job {job_name} must be a mapping")
            continue
        if "permissions" in job:
            errors.extend(_permissions_errors(job.get("permissions"), trusted_write=trusted_write, where=f"{path}: job {job_name}"))
        if str(job.get("secrets", "")).strip().lower() == "inherit":
            errors.append(f"{path}: job {job_name} uses forbidden reusable-workflow secrets: inherit")
        job_uses = job.get("uses")
        if isinstance(job_uses, str):
            errors.extend(_external_uses_errors(job_uses, where=f"{path}: job {job_name}"))
        steps = job.get("steps", [])
        if job_uses is not None and steps:
            errors.append(f"{path}: job {job_name} may not combine reusable-workflow uses with steps")
        if not isinstance(steps, list):
            errors.append(f"{path}: job {job_name} steps must be a list")
            continue
        for i, step in enumerate(steps):
            if not isinstance(step, dict):
                errors.append(f"{path}: job {job_name} step {i} must be a mapping")
                continue
            uses = step.get("uses")
            if isinstance(uses, str):
                errors.extend(_external_uses_errors(uses, where=f"{path}: job {job_name} step {i}"))
                errors.extend(_checkout_errors(step, trusted_write=trusted_write, where=f"{path}: job {job_name} step {i}"))
                if uses.startswith("./"):
                    if trusted_write:
                        errors.append(f"{path}: trusted lifecycle local composite actions are forbidden in Phase A")
                    elif any(GITHUB_TOKEN_EXPR_RE.search(scalar) for scalar in _walk_scalars(step)):
                        errors.append(f"{path}: job {job_name} step {i} local action may not receive caller github.token")
                    if not trusted_write:
                        if root is None:
                            errors.append(f"{path}: local action {uses} requires repository-root structural inspection")
                        else:
                            manifest = _resolve_local_action(root, uses)
                            if manifest is None:
                                errors.append(f"{path}: local action reference is missing/unsafe: {uses}")
                            else:
                                errors.extend(_local_action_errors(root, manifest))
    if trusted_write:
        errors.extend(_trusted_lifecycle_structure_errors(doc, path=path))
    return list(dict.fromkeys(errors))


def workflow_text_errors(text: str, *, trusted_write: bool = False) -> list[str]:
    path = TRUSTED_LIFECYCLE_WORKFLOW if trusted_write else ".github/workflows/synthetic.yml"
    doc, errors = _load_yaml(text, path)
    if errors:
        return errors
    assert isinstance(doc, dict)
    return workflow_document_errors(doc, path=path, root=None)


def repository_workflow_security_errors(root: Path | str) -> list[str]:
    root = Path(root).resolve()
    errors: list[str] = []
    workflows = root / ".github" / "workflows"
    if not workflows.is_dir():
        return [".github/workflows: missing workflow directory"]
    paths = sorted([*workflows.glob("**/*.yml"), *workflows.glob("**/*.yaml")])
    if not paths:
        return [".github/workflows: no workflows found"]
    for path in paths:
        if path.is_symlink() or not path.is_file():
            errors.append(f"{path.relative_to(root)}: workflow must be a regular file")
            continue
        rel = path.relative_to(root).as_posix()
        try:
            text = path.read_text(encoding="utf-8")
        except Exception as exc:
            errors.append(f"{rel}: cannot read workflow: {exc}")
            continue
        doc, parse_errors = _load_yaml(text, rel)
        errors.extend(parse_errors)
        if doc is not None:
            errors.extend(workflow_document_errors(doc, path=rel, root=root))
    actions_root = root / ".github" / "actions"
    if actions_root.exists():
        for manifest in sorted([*actions_root.glob("**/action.yml"), *actions_root.glob("**/action.yaml")]):
            if manifest.is_symlink() or not manifest.is_file():
                errors.append(f"{manifest.relative_to(root)}: local action manifest must be a regular file")
                continue
            errors.extend(_local_action_errors(root, manifest))
    return list(dict.fromkeys(errors))


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("root", nargs="?", default=".")
    args = ap.parse_args(argv)
    errors = repository_workflow_security_errors(args.root)
    if errors:
        print("FAIL: workflow security")
        for error in errors:
            print(" -", error)
        return 1
    print("PASS: workflow security")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
