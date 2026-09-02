#!/usr/bin/env python3
# SPDX-FileCopyrightText: 2026 AIMath contributors
# SPDX-License-Identifier: Apache-2.0
"""Temporary review-validation runner.

This branch is never mergeable. The fixed Phase A target already has a green
#106 regression run for the real v1.2.1 Phase B suite. This temporary wrapper
reuses the existing GitHub Actions step to execute the otherwise-unregistered
Village v1.3 direct suite from the exact fixed target blobs.
"""
from __future__ import annotations

from pathlib import Path
import runpy

root = Path(__file__).resolve().parent.parent
target = root / "scripts/test_village_v1_3_next.py"
if not target.is_file():
    raise SystemExit("missing exact Village v1.3 direct suite")

runpy.run_path(str(target), run_name="__main__")
