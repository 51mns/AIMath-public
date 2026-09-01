#!/usr/bin/env python3
from pathlib import Path
import subprocess, sys
ROOT=Path(__file__).resolve().parents[2]
cmds=[
 [sys.executable,str(ROOT/'research/433-existing-theory-identification/verify_identification.py')],
 [sys.executable,str(ROOT/'reviews/433-existing-theory-identification/independent_verify.py')],
]
for cmd in cmds:
 print('+',' '.join(cmd),flush=True); subprocess.run(cmd,check=True,cwd=ROOT)
print('existing-theory identification public reproduction: PASS')
