#!/usr/bin/env python3
from __future__ import annotations

from pathlib import Path
import re
import sys

FORBIDDEN_PATH_PARTS = {".git"}
IGNORED_GENERATED_PARTS = {"__pycache__"}
FORBIDDEN_PREFIXES = (
    "archive/chatgpt/",
    "coordination/private/",
    "coordination/internal/",
)
FORBIDDEN_SUFFIXES = (".pem", ".key", ".p12", ".pfx")
HIGH_RISK_FILENAMES = {
    ".env", "cookies.txt", "credentials.json", "secrets.json",
    "conversations.json", "message_feedback.json",
}
PATTERNS = {
    "generic email": re.compile(r"(?i)\b[A-Z0-9._%+-]+@[A-Z0-9.-]+\.[A-Z]{2,}\b"),
    "OpenAI-style secret": re.compile(r"\bsk-[A-Za-z0-9_-]{16,}\b"),
    "GitHub classic token": re.compile(r"\bgh[pousr]_[A-Za-z0-9]{20,}\b"),
    "GitHub fine-grained token": re.compile(r"\bgithub_pat_[A-Za-z0-9_]{20,}\b"),
    "AWS access key": re.compile(r"\bAKIA[0-9A-Z]{16}\b"),
    "Slack token": re.compile(r"\bxox[baprs]-[A-Za-z0-9-]{10,}\b"),
    "Google OAuth token": re.compile(r"\bya29\.[A-Za-z0-9._-]{20,}\b"),
    "private key block": re.compile(r"-----BEGIN (?:RSA |EC |OPENSSH )?PRIVATE KEY-----"),
    "macOS home path": re.compile(r"/Users/[^/\s]+/"),
    "Linux home path": re.compile(r"/home/[^/\s]+/"),
    "runtime attachment path": re.compile(r"(?:sandbox:)?/mnt/data/"),
    "connector-style private file id": re.compile(r"\bfile_[0-9a-f]{16,}\b"),
    "private ChatGPT conversation URL": re.compile(r"https?://(?:chat\.openai\.com|chatgpt\.com)/c/"),
}
TEXT_SUFFIX_ALLOW = {
    ".md", ".txt", ".py", ".json", ".yml", ".yaml", ".toml", ".cfg",
    ".ini", ".csv", ".tsv", ".sh", ".ps1", ".bat", ".cff", ".lock",
}
TEXT_NAMES_ALLOW = {"Makefile", "LICENSE", "NOTICE", ".gitignore", "CODEOWNERS"}
SCAN_EXEMPT_PREFIXES = ("LICENSES/",)
SCAN_EXEMPT_FILES = {
    "scripts/public_release_audit.py",
    "scripts/test_village_acceptance.py",
    "scripts/test_village_v1_2.py",
}
SIDECAR_MAX_BYTES = 16 * 1024
SPDX_SIDECAR_LINE = re.compile(r"^(SPDX-FileCopyrightText|SPDX-License-Identifier):\s*\S.*$")


def norm(path: Path, root: Path) -> str:
    return path.relative_to(root).as_posix()


def read_utf8(path: Path, rel: str, findings: list[str]) -> str | None:
    try:
        return path.read_text(encoding="utf-8")
    except UnicodeDecodeError:
        findings.append(f"non-UTF8 file requires manual review: {rel}")
        return None


def validate_reuse_sidecar(path: Path, root: Path, findings: list[str]) -> str | None:
    rel = norm(path, root)
    target = Path(str(path)[:-len(".license")])
    if not target.is_file() or target.is_symlink():
        findings.append(f"orphan/unsafe REUSE .license sidecar: {rel}")
        return None
    if path.stat().st_size > SIDECAR_MAX_BYTES:
        findings.append(f"oversized REUSE .license sidecar: {rel}")
        return None
    text = read_utf8(path, rel, findings)
    if text is None:
        return None
    seen_copyright = False
    seen_license = False
    for raw in text.splitlines():
        line = raw.strip()
        if not line:
            continue
        match = SPDX_SIDECAR_LINE.fullmatch(line)
        if not match:
            findings.append(f"malformed/unsafe REUSE .license sidecar line: {rel}")
            return text
        if match.group(1) == "SPDX-FileCopyrightText":
            seen_copyright = True
        elif match.group(1) == "SPDX-License-Identifier":
            seen_license = True
    if not seen_copyright or not seen_license:
        findings.append(f"incomplete REUSE .license sidecar: {rel}")
    return text


def scan_patterns(text: str, rel: str, findings: list[str]) -> None:
    exempt = rel in SCAN_EXEMPT_FILES or any(rel.startswith(p) for p in SCAN_EXEMPT_PREFIXES)
    if exempt:
        return
    for label, rx in PATTERNS.items():
        if rx.search(text):
            findings.append(f"{label}: {rel}")


def main() -> int:
    root = Path(sys.argv[1] if len(sys.argv) > 1 else ".").resolve()
    findings: list[str] = []
    for path in root.rglob("*"):
        rel = norm(path, root)
        rel_parts = path.relative_to(root).parts
        parts = set(rel_parts)
        if rel_parts and rel_parts[0] == ".git":
            continue
        if parts & IGNORED_GENERATED_PARTS:
            continue
        if parts & FORBIDDEN_PATH_PARTS:
            findings.append(f"forbidden path part: {rel}")
            continue
        if any(rel.startswith(p) for p in FORBIDDEN_PREFIXES):
            findings.append(f"forbidden private-workspace prefix: {rel}")
            continue
        # Fail closed before Path.is_file(), because is_file() follows symlinks.
        if path.is_symlink():
            findings.append(f"symlink requires manual review and is forbidden in public release: {rel}")
            continue
        if path.name in HIGH_RISK_FILENAMES:
            findings.append(f"high-risk filename: {rel}")
        if path.suffix.lower() in FORBIDDEN_SUFFIXES:
            findings.append(f"private-key/container suffix: {rel}")
        if not path.is_file():
            continue
        lower = path.name.lower()
        if lower.endswith((".zip", ".7z", ".rar", ".tar", ".tgz", ".gz", ".b64")):
            findings.append(f"opaque archive/encoded payload requires manual review: {rel}")
            continue
        if lower.endswith(".license"):
            text = validate_reuse_sidecar(path, root, findings)
            if text is not None:
                scan_patterns(text, rel, findings)
            continue
        if path.suffix.lower() not in TEXT_SUFFIX_ALLOW and path.name not in TEXT_NAMES_ALLOW:
            findings.append(f"unknown file type requires manual review: {rel}")
            continue
        text = read_utf8(path, rel, findings)
        if text is not None:
            scan_patterns(text, rel, findings)
    if findings:
        print("FAIL: public release audit found:")
        for item in sorted(set(findings)):
            print(" -", item)
        return 1
    print(
        "PASS: no blocked private paths, symlinks, opaque payloads, obvious credentials, emails, "
        "home/runtime paths, connector file ids, private ChatGPT conversation URLs, or unsafe REUSE sidecars detected"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
