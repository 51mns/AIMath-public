#!/usr/bin/env python3
# SPDX-FileCopyrightText: 2026 AIMath contributors
# SPDX-License-Identifier: Apache-2.0
from __future__ import annotations

from datetime import timedelta
from pathlib import Path
import copy
import json
import tempfile
import unittest
from unittest.mock import patch

import yaml

from check_village_pr import validate_lock_transition
from lock_auto_activate import AutoActivationError, AutoReleaseCandidate, _strict_up_to_date_gate, auto_activation_preflight, auto_release_preflight, automatic_release_identity_errors, choose_release_candidate, final_revalidation_errors, lock_git_object_errors, release_head_absence_errors
from test_village_acceptance import NOW, add_lock, base_state
from village_core import LockBundle
from village_v1_2 import ABANDONED_REACQUIRE_COOLDOWN_HOURS, ReleaseBinding, abandonment_state, new_worker_lock_errors, parse_release_head_ref, release_terminal_state, validate_abandoned_terminal_record
from workflow_security import repository_workflow_security_errors, workflow_text_errors

MAIN_SHA = "a" * 40
HEAD_SHA = "b" * 40
W_A = "w-" + "a" * 16
W_B = "w-" + "b" * 16


def _policy(): return {"worker_id_required_for_new_lock": True, "exclusive_worker_lock_cap_default": 1}

def _write_schemas(root: Path):
    repo = Path(__file__).resolve().parent.parent; d=root/"schemas"; d.mkdir(parents=True,exist_ok=True)
    for n in ("outcome.schema.json","abandoned-terminal.schema.json"): (d/n).write_text((repo/"schemas"/n).read_text(),encoding="utf-8")

def _result(root: Path, malformed=False):
    p=root/"coordination/outcomes/TASK-X-1.yml"; p.parent.mkdir(parents=True,exist_ok=True)
    obj={"schema_version":1,"task_id":"TASK-X-1","outcome_type":"NO_REUSABLE_PROGRESS","summary":"terminal scheduling output","artifacts":[]}
    if malformed: obj={"schema_version":1,"task_id":"TASK-X-1"}
    p.write_text(json.dumps(obj)+"\n",encoding="utf-8")

def _abandon(root: Path, *, worker=W_A, count=1, at=None, truth="NONE", extra=None):
    p=root/f"work/TASK-X-1/{worker}/ABANDONED_TERMINAL.yml"; p.parent.mkdir(parents=True,exist_ok=True)
    obj={"schema_version":1,"task_id":"TASK-X-1","worker_id":worker,"reason":"NO_REUSABLE_PROGRESS","abandoned_at":(at or NOW).isoformat(),"abandonment_count":count,"last_work_head":None,"truth_layer_effect":truth}
    if extra: obj.update(extra)
    p.write_text(json.dumps(obj)+"\n",encoding="utf-8"); return obj

def _lock_state(root: Path, *, worker=W_A, actor="gh:51mns", expired=False):
    s=base_state(); s.root=root.resolve(); add_lock(s,"LOCK-1","TASK-X-1","x/shared",actor=actor,expires=NOW-timedelta(hours=1) if expired else NOW+timedelta(hours=10)); b=s.lock_bundles["LOCK-1"]; b.payload["worker_id"]=worker; b.payload["work_ref"]=f"research/TASK-X-1/{worker}"; return s

def _release_pr(*, number=10, worker=W_A, task="TASK-X-1", actor="51mns", base=MAIN_SHA, status="removed"):
    pr={"number":number,"state":"open","draft":False,"base":{"ref":"main","sha":base},"head":{"ref":f"release/{task}/{worker}","sha":HEAD_SHA,"repo":{"full_name":"51mns/AIMath-public"}},"user":{"login":actor}}
    return pr,[{"filename":"coordination/locks/x/shared.yml","status":status,"sha":"c"*40}]

def _acquire():
    run={"name":"Verify public release","event":"pull_request","status":"completed","conclusion":"success","head_sha":HEAD_SHA}
    pr={"state":"open","draft":False,"base":{"ref":"main","sha":MAIN_SHA},"head":{"sha":HEAD_SHA,"repo":{"full_name":"51mns/AIMath-public"}},"user":{"login":"51mns"}}
    return run,pr,[{"filename":"coordination/locks/x/shared.yml","status":"added","sha":"c"*40}]


class PhaseA(unittest.TestCase):
    def test_01_valid_exact_worker_release(self):
        with tempfile.TemporaryDirectory() as td:
            r=Path(td); _write_schemas(r); _result(r); b=_lock_state(r); h=copy.deepcopy(b); h.lock_bundles={}; bind=parse_release_head_ref(f"release/TASK-X-1/{W_A}"); self.assertEqual(validate_lock_transition(b,h,actor="51mns",base_sha=MAIN_SHA,maintainers={"51mns"},release_binding=bind),("RELEASE",[]))
    def test_02_same_principal_wrong_worker(self):
        with tempfile.TemporaryDirectory() as td:
            r=Path(td); _write_schemas(r); _result(r); b=_lock_state(r); h=copy.deepcopy(b); h.lock_bundles={}; _,e=validate_lock_transition(b,h,actor="51mns",base_sha=MAIN_SHA,maintainers={"51mns"},release_binding=parse_release_head_ref(f"release/TASK-X-1/{W_B}")); self.assertTrue(any("worker" in x for x in e))
    def test_03_maintainer_no_auto_override(self):
        with tempfile.TemporaryDirectory() as td:
            b=_lock_state(Path(td),actor="gh:other"); pr,_=_release_pr(worker=W_B); e=automatic_release_identity_errors(pr,b.lock_bundles["LOCK-1"],parse_release_head_ref(pr["head"]["ref"])); self.assertTrue(any("override" in x for x in e)); self.assertTrue(any("worker" in x for x in e))
    def test_04_mixed_release_research(self):
        pr,f=_release_pr(); f.append({"filename":"research/x/PROOF.md","status":"modified","sha":"d"*40}); self.assertFalse(auto_release_preflight(pr,f,repository="51mns/AIMath-public",current_main_sha=MAIN_SHA,release_principals={"51mns"})[0])
    def test_05_release_replacement(self):
        pr,f=_release_pr(); f.append({"filename":"coordination/locks/x/new.yml","status":"added","sha":"d"*40}); self.assertFalse(auto_release_preflight(pr,f,repository="51mns/AIMath-public",current_main_sha=MAIN_SHA,release_principals={"51mns"})[0])
    def test_06_modified_masquerade(self):
        pr,f=_release_pr(status="modified"); self.assertFalse(auto_release_preflight(pr,f,repository="51mns/AIMath-public",current_main_sha=MAIN_SHA,release_principals={"51mns"})[0])
    def test_07_nonregular_base_objects(self):
        _,f=_release_pr()
        for mode,typ in (("120000","blob"),("160000","commit"),("040000","tree")): self.assertTrue(lock_git_object_errors(f,[{"path":f[0]["filename"],"mode":mode,"type":typ,"sha":f[0]["sha"]}]))
    def test_08_wrong_task(self):
        with tempfile.TemporaryDirectory() as td:
            r=Path(td); _write_schemas(r); _result(r); b=_lock_state(r); h=copy.deepcopy(b); h.lock_bundles={}; _,e=validate_lock_transition(b,h,actor="51mns",base_sha=MAIN_SHA,maintainers={"51mns"},release_binding=ReleaseBinding("TASK-X-OTHER",W_A,f"release/TASK-X-OTHER/{W_A}")); self.assertTrue(any("Task" in x for x in e))
    def test_09_wrong_collision_key(self):
        with tempfile.TemporaryDirectory() as td:
            r=Path(td); _write_schemas(r); _result(r); b=_lock_state(r); b.tasks["TASK-X-1"]["collision_keys"]=["different"]; h=copy.deepcopy(b); h.lock_bundles={}; _,e=validate_lock_transition(b,h,actor="51mns",base_sha=MAIN_SHA,maintainers={"51mns"},release_binding=parse_release_head_ref(f"release/TASK-X-1/{W_A}")); self.assertTrue(any("collision_keys" in x for x in e))
    def test_10_stale_base(self):
        pr,f=_release_pr(base="d"*40); self.assertFalse(auto_release_preflight(pr,f,repository="51mns/AIMath-public",current_main_sha=MAIN_SHA,release_principals={"51mns"})[0])
    def test_11_head_main_movement(self):
        p={"head":{"sha":HEAD_SHA},"base":{"sha":MAIN_SHA}}; self.assertTrue(final_revalidation_errors(original_main_sha=MAIN_SHA,original_head_sha=HEAD_SHA,final_main_sha="e"*40,final_pr=p)); p["head"]["sha"]="f"*40; self.assertTrue(final_revalidation_errors(original_main_sha=MAIN_SHA,original_head_sha=HEAD_SHA,final_main_sha=MAIN_SHA,final_pr=p))
    def test_12_repeated_release(self):
        s=base_state(); op,e=validate_lock_transition(s,copy.deepcopy(s),actor="51mns",base_sha=MAIN_SHA,maintainers={"51mns"},release_binding=parse_release_head_ref(f"release/TASK-X-1/{W_A}")); self.assertEqual(op,"INVALID"); self.assertTrue(e)
    def test_13_expired_release(self):
        with tempfile.TemporaryDirectory() as td:
            r=Path(td); _write_schemas(r); _result(r); b=_lock_state(r,expired=True); h=copy.deepcopy(b); h.lock_bundles={}; self.assertEqual(validate_lock_transition(b,h,actor="51mns",base_sha=MAIN_SHA,maintainers={"51mns"},release_binding=parse_release_head_ref(f"release/TASK-X-1/{W_A}")),("RELEASE",[]))
    def test_14_result_terminal(self):
        with tempfile.TemporaryDirectory() as td:
            r=Path(td); _write_schemas(r); _result(r); b=_lock_state(r); self.assertEqual(release_terminal_state(r,b.lock_bundles["LOCK-1"].payload,now=NOW)[0],"RESULT_TERMINAL")
    def test_15_malformed_result_fallback(self):
        with tempfile.TemporaryDirectory() as td:
            r=Path(td); _write_schemas(r); _result(r,True); _abandon(r); b=_lock_state(r); self.assertEqual(release_terminal_state(r,b.lock_bundles["LOCK-1"].payload,now=NOW)[0],"ABANDONED_TERMINAL")
    def test_16_abandoned_schema(self):
        with tempfile.TemporaryDirectory() as td:
            r=Path(td); _write_schemas(r); o=_abandon(r); self.assertEqual(validate_abandoned_terminal_record(o,root=r,expected_task_id="TASK-X-1",expected_worker_id=W_A),[]); o["x"]=1; self.assertTrue(validate_abandoned_terminal_record(o,root=r,expected_task_id="TASK-X-1",expected_worker_id=W_A))
    def test_17_truth_effect_mutation(self):
        with tempfile.TemporaryDirectory() as td:
            r=Path(td); _write_schemas(r); o=_abandon(r,truth="PROMOTE"); self.assertTrue(any("truth_layer_effect" in x for x in validate_abandoned_terminal_record(o,root=r,expected_task_id="TASK-X-1",expected_worker_id=W_A)))
    def test_18_cooldown_and_expiry(self):
        with tempfile.TemporaryDirectory() as td:
            r=Path(td); _write_schemas(r); _abandon(r,at=NOW); b=base_state(); b.root=r.resolve(); b.now=NOW+timedelta(hours=1); bundle=LockBundle("L",{"task_id":"TASK-X-1","actor":{"id":"gh:a"},"worker_id":W_A,"work_ref":f"research/TASK-X-1/{W_A}"},{"x/shared"},[]); self.assertTrue(any("cooldown" in x for x in new_worker_lock_errors(b,bundle,actor_policy=_policy()))); b.now=NOW+timedelta(hours=ABANDONED_REACQUIRE_COOLDOWN_HOURS+1); self.assertFalse(any("cooldown" in x for x in new_worker_lock_errors(b,bundle,actor_policy=_policy()))); self.assertEqual(abandonment_state(r,"TASK-X-1",W_A,now=b.now)["abandonment_count"],1)
    def test_19_release_order(self):
        a=AutoReleaseCandidate({"number":20},[],"L2","RESULT_TERMINAL"); b=AutoReleaseCandidate({"number":10},[],"L1","RESULT_TERMINAL"); self.assertEqual(choose_release_candidate([a,b]).pr["number"],10)
    def test_20_invalid_lower_not_block(self):
        v=AutoReleaseCandidate({"number":20},[],"L2","RESULT_TERMINAL"); self.assertEqual(choose_release_candidate([v]).pr["number"],20)
    def test_21_concurrency(self):
        root=Path(__file__).resolve().parent.parent; doc=yaml.load((root/".github/workflows/lock-auto-activate.yml").read_text(),Loader=yaml.BaseLoader); self.assertEqual(doc["concurrency"]["group"],"village-lock-lifecycle"); self.assertEqual(doc["concurrency"]["cancel-in-progress"],"false")
    def test_22_nonrelease_never_auto(self):
        for fn,st in (("research/x/P.md","removed"),("AGENTS.md","removed"),("coordination/locks/x/shared.yml","modified")):
            pr,f=_release_pr(); f[0]={"filename":fn,"status":st,"sha":"c"*40}; self.assertFalse(auto_release_preflight(pr,f,repository="51mns/AIMath-public",current_main_sha=MAIN_SHA,release_principals={"51mns"})[0])
    def test_23_acquire_not_broadened(self):
        run,pr,f=_acquire(); pr["user"]["login"]="ordinary"; self.assertFalse(auto_activation_preflight(run,pr,f,repository="51mns/AIMath-public",current_main_sha=MAIN_SHA,maintainers={"51mns"})[0])
    def test_24_setting_unreadable(self):
        with patch("lock_auto_activate._request_json",side_effect=AutoActivationError("403 Resource not accessible by integration")):
            ok,why=_strict_up_to_date_gate("t","51mns/AIMath-public"); self.assertFalse(ok); self.assertIn("403",why)
    def test_25_deleted_absent(self):
        _,f=_release_pr(); self.assertTrue(release_head_absence_errors(f,[{"path":f[0]["filename"]}]))
    def _wf(self,permissions="contents: read",trigger="pull_request",extra=""): return f"name: t\non: {trigger}\npermissions: {permissions}\njobs:\n  t:\n    runs-on: ubuntu-latest\n    steps:\n      - run: echo ok\n{extra}"
    def test_26_secret_whitespace(self): self.assertTrue(workflow_text_errors(self._wf(extra="      - run: 'echo ${{ secrets   .   TOKEN }}'\n")))
    def test_27_secrets_inherit(self): self.assertTrue(workflow_text_errors("name: t\non: pull_request\npermissions: {contents: read}\njobs:\n  t:\n    uses: owner/repo/.github/workflows/x.yml@aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa\n    secrets: inherit\n"))
    def test_28_flow_permissions_and_omission(self): self.assertEqual(workflow_text_errors(self._wf(permissions="{contents: read}")),[]); self.assertTrue(workflow_text_errors("name: t\non: pull_request\njobs: {t: {runs-on: ubuntu-latest, steps: [{run: echo ok}]}}\n"))
    def test_29_writeall_prtarget(self): self.assertTrue(workflow_text_errors(self._wf(permissions="write-all"))); self.assertTrue(workflow_text_errors(self._wf(trigger="pull_request_target")))
    def test_30_checkout_pr_head(self):
        text="""name: Activate validated Village lock\non:\n  workflow_run:\n    workflows: [Verify public release]\n    types: [completed]\npermissions: {contents: write}\nconcurrency: {group: village-lock-lifecycle, cancel-in-progress: false}\njobs:\n  t:\n    runs-on: ubuntu-latest\n    steps:\n      - uses: actions/checkout@11d5960a326750d5838078e36cf38b85af677262\n        with: {ref: '${{ github.event.workflow_run.head_sha }}', persist-credentials: false}\n      - run: python3 scripts/lock_auto_activate.py\n"""; self.assertTrue(workflow_text_errors(text,trusted_write=True))
    def test_31_misleading_comment(self): self.assertEqual(workflow_text_errors("# permissions: write-all\n# pull_request_target\n"+self._wf()),[])
    def test_32_local_action_token(self):
        with tempfile.TemporaryDirectory() as td:
            r=Path(td); (r/".github/workflows").mkdir(parents=True); (r/".github/actions/x").mkdir(parents=True); (r/".github/workflows/t.yml").write_text("name: t\non: pull_request\npermissions: {contents: read}\njobs:\n  t:\n    runs-on: ubuntu-latest\n    steps:\n      - uses: ./.github/actions/x\n"); (r/".github/actions/x/action.yml").write_text("name: x\nruns:\n  using: composite\n  steps:\n    - shell: bash\n      run: 'echo ${{ github.token }}'\n"); self.assertTrue(repository_workflow_security_errors(r))


if __name__ == "__main__": unittest.main(verbosity=2)
