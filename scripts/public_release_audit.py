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

# Standard third-party licence texts and machine scanners legitimately contain
# detector examples/addresses. Do not suppress scanning of project-authored docs.
SCAN_EXEMPT_PREFIXES = ("LICENSES/",)
SCAN_EXEMPT_FILES = {"scripts/public_release_audit.py", "scripts/test_village_acceptance.py"}

def norm(path: Path, root: Path) -> str:
    return path.relative_to(root).as_posix()

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
        if path.suffix.lower() not in TEXT_SUFFIX_ALLOW and path.name not in TEXT_NAMES_ALLOW:
            findings.append(f"unknown file type requires manual review: {rel}")
            continue
        try:
            text = path.read_text(encoding="utf-8")
        except UnicodeDecodeError:
            findings.append(f"non-UTF8 file requires manual review: {rel}")
            continue
        exempt = rel in SCAN_EXEMPT_FILES or any(rel.startswith(p) for p in SCAN_EXEMPT_PREFIXES)
        if not exempt:
            for label, rx in PATTERNS.items():
                if rx.search(text):
                    findings.append(f"{label}: {rel}")
    if findings:
        print("FAIL: public release audit found:")
        for item in sorted(set(findings)):
            print(" -", item)
        return 1
    print(
        "PASS: no blocked private paths, opaque payloads, obvious credentials, "
        "emails, home/runtime paths, connector file ids, or private ChatGPT "
        "conversation URLs detected"
    )
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
