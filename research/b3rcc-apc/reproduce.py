#!/usr/bin/env python3
from pathlib import Path
import subprocess,sys
ROOT=Path(__file__).resolve().parents[2]
cmds=[
 [sys.executable,str(ROOT/'research/b3rcc-apc/verify_rank4_witness.py')],
 [sys.executable,str(ROOT/'reviews/b3rcc-apc/exact_controls.py')],
]
for cmd in cmds:
 print('+',' '.join(cmd),flush=True); subprocess.run(cmd,check=True,cwd=ROOT)
print('B3RCC/APC public controls: PASS')
