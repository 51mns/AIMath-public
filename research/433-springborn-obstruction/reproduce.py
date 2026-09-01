#!/usr/bin/env python3
from pathlib import Path
import subprocess, sys
ROOT=Path(__file__).resolve().parents[2]
cmds=[
    [sys.executable,str(ROOT/'research/433-springborn-obstruction/verify_springborn_obstruction.py')],
    [sys.executable,str(ROOT/'reviews/433-springborn-obstruction/independent_verify.py')],
]
for cmd in cmds:
    print('+',' '.join(cmd),flush=True)
    subprocess.run(cmd,check=True,cwd=ROOT)
print('springborn obstruction public reproduction: PASS')
