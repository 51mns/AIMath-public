#!/usr/bin/env python3
from pathlib import Path
import subprocess,sys
ROOT=Path(__file__).resolve().parents[2]
cmd=[sys.executable,str(ROOT/'research/gyoda-89/verify.py')]
print('+',' '.join(cmd),flush=True); subprocess.run(cmd,check=True,cwd=ROOT)
print('Gyoda 89 public reproduction: PASS')
