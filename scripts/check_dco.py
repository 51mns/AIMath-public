#!/usr/bin/env python3
from __future__ import annotations

import argparse
import subprocess
import sys
from village_core import dco_commit_ok

def git(*args: str) -> str:
    return subprocess.check_output(["git", *args], text=True).strip()

def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("base")
    ap.add_argument("head")
    args = ap.parse_args()
    commits = [x for x in git("rev-list", "--reverse", f"{args.base}..{args.head}").splitlines() if x]
    if not commits:
        print("FAIL: DCO range contains no commits")
        return 1
    failures = []
    for sha in commits:
        author_email = git("show", "-s", "--format=%ae", sha)
        message = git("show", "-s", "--format=%B", sha)
        ok, why = dco_commit_ok(author_email, message)
        if not ok:
            failures.append(f"{sha[:12]}: {why}")
    if failures:
        print("FAIL: DCO check")
        for item in failures:
            print(" -", item)
        return 1
    print(f"PASS: DCO ({len(commits)} commit(s) signed off)")
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
