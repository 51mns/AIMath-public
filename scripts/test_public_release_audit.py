#!/usr/bin/env python3
# SPDX-FileCopyrightText: 2026 AIMath contributors
# SPDX-License-Identifier: Apache-2.0

from __future__ import annotations

from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

AUDIT = Path(__file__).with_name("public_release_audit.py")


class PublicReleaseAuditLeanTests(unittest.TestCase):
    def run_audit(self, files: dict[str, str | bytes]) -> subprocess.CompletedProcess[str]:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            for rel, content in files.items():
                path = root / rel
                path.parent.mkdir(parents=True, exist_ok=True)
                if isinstance(content, bytes):
                    path.write_bytes(content)
                else:
                    path.write_text(content, encoding="utf-8")
            return subprocess.run(
                [sys.executable, str(AUDIT), str(root)],
                check=False,
                capture_output=True,
                text=True,
            )

    def test_lean_source_is_allowed_and_scanned_as_text(self) -> None:
        result = self.run_audit({"Proof.lean": "theorem safe : True := by trivial\n"})
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)

    def test_lean_source_does_not_bypass_secret_scan(self) -> None:
        secret = "sk-" + ("A" * 20)
        result = self.run_audit({"Proof.lean": f'def accidental := "{secret}"\n'})
        self.assertEqual(result.returncode, 1)
        self.assertIn("OpenAI-style secret: Proof.lean", result.stdout)

    def test_lean_toolchain_pin_is_allowed_and_scanned_as_text(self) -> None:
        result = self.run_audit({"lean-toolchain": "leanprover/lean4:v4.33.1\n"})
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)

    def test_unknown_file_type_remains_fail_closed(self) -> None:
        result = self.run_audit({"proof.unknown-format": "safe text\n"})
        self.assertEqual(result.returncode, 1)
        self.assertIn("unknown file type requires manual review", result.stdout)


if __name__ == "__main__":
    unittest.main(verbosity=2)
