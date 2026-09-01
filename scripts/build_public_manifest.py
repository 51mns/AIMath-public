#!/usr/bin/env python3
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path

PRIVATE_CANON_SOURCE = "c8e61e0e398f540bc8c5de79663398d689f37473"


def sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def should_skip(path: Path, root: Path, output: Path | None) -> bool:
    rel = path.relative_to(root)
    if ".git" in rel.parts or "__pycache__" in rel.parts:
        return True
    if path.name == ".DS_Store":
        return True
    if output is not None and path.resolve() == output.resolve():
        return True
    # This metadata pointer is not itself part of a generated live manifest.
    if rel.as_posix() == "PUBLIC_MANIFEST.json":
        return True
    return False


def build(root: Path, output: Path | None) -> dict:
    files = []
    for path in sorted(root.rglob("*")):
        if not path.is_file() or should_skip(path, root, output):
            continue
        files.append(
            {
                "path": path.relative_to(root).as_posix(),
                "sha256": sha256(path),
                "bytes": path.stat().st_size,
            }
        )
    return {
        "schema_version": 1,
        "public_distribution": "AIMath Public",
        "private_canon_source_commit": PRIVATE_CANON_SOURCE,
        "history_policy": "fresh public Git history; never mirror private .git history",
        "generated_from_worktree": True,
        "files": files,
    }


def main() -> int:
    parser = argparse.ArgumentParser(description="Generate a current AIMath-public SHA-256 manifest")
    parser.add_argument("root", nargs="?", default=".")
    parser.add_argument("--output", help="write JSON to this path instead of stdout")
    args = parser.parse_args()

    root = Path(args.root).resolve()
    output = Path(args.output).resolve() if args.output else None
    payload = build(root, output)
    text = json.dumps(payload, indent=2, ensure_ascii=False) + "\n"

    if output is None:
        print(text, end="")
    else:
        output.parent.mkdir(parents=True, exist_ok=True)
        output.write_text(text, encoding="utf-8")
        print(f"PASS: wrote manifest for {len(payload['files'])} files to {output}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
