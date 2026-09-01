#!/usr/bin/env python3
from __future__ import annotations
from dataclasses import dataclass
from datetime import datetime, timezone, timedelta
from pathlib import Path
import fnmatch, json, re
from typing import Any, Iterable

MAINTENANCE_TASK_KINDS={"INDEPENDENT_REVIEW","REPRODUCTION","FRONTIER_REFRESH","DEPENDENCY_TRIAGE"}
PASS_REVIEW_DECISIONS={"PASS","PASS_WITH_QUALIFICATIONS"}
class VillageError(ValueError): pass

def load_machine_file(path:Path)->Any:
    try:return json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as e: raise VillageError(f"{path}: canonical .yml must use the YAML 1.2 JSON subset: {e}") from e

def _type_ok(v:Any,k:str)->bool:
    return {"object":lambda:isinstance(v,dict),"array":lambda:isinstance(v,list),"string":lambda:isinstance(v,str),"integer":lambda:isinstance(v,int) and not isinstance(v,bool),"number":lambda:isinstance(v,(int,float)) and not isinstance(v,bool),"boolean":lambda:isinstance(v,bool),"null":lambda:v is None}.get(k,lambda:True)()

def validate_schema(v:Any,s:dict[str,Any],where:str="$" )->list[str]:
    e=[]; t=s.get("type")
    if t is not None:
        ks=t if isinstance(t,list) else [t]
        if not any(_type_ok(v,k) for k in ks): return [f"{where}: expected type {ks}, got {type(v).__name__}"]
    if "const" in s and v!=s["const"]: e.append(f"{where}: expected constant {s['const']!r}")
    if "enum" in s and v not in s["enum"]: e.append(f"{where}: value {v!r} not in enum {s['enum']!r}")
    if isinstance(v,str):
        if len(v)<s.get("minLength",0): e.append(f"{where}: string shorter than minLength")
        if "pattern" in s and re.fullmatch(s["pattern"],v) is None:e.append(f"{where}: string {v!r} does not match {s['pattern']!r}")
    if isinstance(v,int) and not isinstance(v,bool):
        if "minimum" in s and v<s["minimum"]:e.append(f"{where}: {v} < minimum {s['minimum']}")
        if "maximum" in s and v>s["maximum"]:e.append(f"{where}: {v} > maximum {s['maximum']}")
    if isinstance(v,list):
        if len(v)<s.get("minItems",0):e.append(f"{where}: fewer than minItems")
        item=s.get("items")
        if item:
            for i,x in enumerate(v):e+=validate_schema(x,item,f"{where}[{i}]")
    if isinstance(v,dict):
        for k in s.get("required",[]):
            if k not in v:e.append(f"{where}: missing required key {k!r}")
        props=s.get("properties",{})
        for k,x in v.items():
            if k in props:e+=validate_schema(x,props[k],f"{where}.{k}")
            elif s.get("additionalProperties") is False:e.append(f"{where}: unexpected key {k!r}")
    return e

def parse_time(v:str)->datetime:
    s=v.strip()
    if re.fullmatch(r"\d{4}-\d{2}-\d{2}",s):s+="T00:00:00+00:00"
    if s.endswith("Z"):s=s[:-1]+"+00:00"
    d=datetime.fromisoformat(s)
    if d.tzinfo is None:d=d.replace(tzinfo=timezone.utc)
    return d.astimezone(timezone.utc)

def claim_dep_id(d:Any)->str:
    if isinstance(d,str):return d
    if isinstance(d,dict) and isinstance(d.get("claim_id"),str):return d["claim_id"]
    raise VillageError(f"invalid claim dependency entry: {d!r}")

def owned_prefix(p:str)->str:
    out=[]
    for x in p.split('/'):
        if any(c in x for c in '*?['):break
        out.append(x)
    return '/'.join(out).rstrip('/')

def owned_paths_overlap(a:Iterable[str],b:Iterable[str])->bool:
    for x in a:
        x=owned_prefix(x)
        if not x:continue
        for y in b:
            y=owned_prefix(y)
            if y and (x==y or x.startswith(y+'/') or y.startswith(x+'/')):return True
    return False

def workflow_safety_errors(text:str)->list[str]:
    e=[]; low=text.lower()
    if "pull_request_target" in low:e.append("pull_request_target is forbidden for untrusted contribution workflows")
    if re.search(r"(?m)^\s*permissions:\s*write-all\s*$",text):e.append("permissions: write-all is forbidden")
    if re.search(r"(?m)^\s*(contents|actions|checks|pull-requests|issues):\s*write\s*$",text):e.append("write-scoped GITHUB_TOKEN permission is forbidden in public verify workflows")
    if re.search(r"\$\{\{\s*secrets\.",text):e.append("workflow references repository secrets")
    return e

def dco_commit_ok(author_email:str,message:str)->tuple[bool,str]:
    trailers=re.findall(r"(?mi)^Signed-off-by:\s*(.+?)\s*<([^<>]+)>\s*$",message)
    if not trailers:return False,"missing Signed-off-by trailer"
    if author_email.strip().lower() not in {x[1].strip().lower() for x in trailers}:return False,"Signed-off-by email does not match commit author email"
    return True,"ok"

def is_lock_only_paths(paths:Iterable[str])->bool:
    p=list(paths);return bool(p) and all(x.startswith("coordination/locks/") and x.endswith(".yml") for x in p)
def path_matches(path:str,patterns:Iterable[str])->bool:return any(fnmatch.fnmatchcase(path,p) for p in patterns)

def review_grade_valid(r:dict[str,Any])->tuple[bool,str]:
    g=r.get("independence_grade"); impl=bool(r.get("implementation_independent")); method=bool(r.get("method_independent")); frozen=bool(r.get("derivation_frozen_before_comparison")); adv=bool(r.get("adversarial_controls"))
    if g in {"I0","I1"}:return True,g
    if g=="I2":return ((impl or method),"I2" if impl or method else "I2 requires material implementation or method independence")
    if g=="I3":
        if not (impl or method):return False,"I3 requires I2-level material independence"
        if not (frozen or (impl and method) or adv):return False,"I3 requires an additional independence element"
        return True,"I3"
    return False,f"unknown independence grade {g!r}"

def independently_reproduced_eligible(modes:Iterable[str],reviews:Iterable[dict[str,Any]],*,universal_claim:bool=False)->tuple[bool,str]:
    m=set(modes)
    if universal_claim and m and m<={"FINITE_EXACT_REPLAY"}:return False,"finite exact replay alone cannot promote a universal theorem"
    for r in reviews:
        ok,_=review_grade_valid(r)
        if r.get("decision") in PASS_REVIEW_DECISIONS and ok and r.get("independence_grade") in {"I2","I3"}:return True,"materially independent passing review present"
    return False,"no materially independent passing I2/I3 review"

@dataclass
class LockBundle:
    lock_id:str; payload:dict[str,Any]; keys:set[str]; paths:list[Path]
def lock_bundle_active(b:LockBundle,now:datetime)->bool:
    try:return parse_time(b.payload["expires_at"])>now
    except Exception:return False

class VillageState:
    def __init__(self,root:Path|str,*,now:datetime|None=None):
        self.root=Path(root).resolve();self.now=(now or datetime.now(timezone.utc)).astimezone(timezone.utc);self.schemas={};self.portfolio={};self.campaigns={};self.tasks={};self.claims={};self.claim_paths={};self.reviews=[];self.failed_routes={};self.proposals=[];self.outcomes={};self.decisions=[];self.lock_bundles={};self.errors=[]
    def _schema(self,n):
        p=self.root/'schemas'/n
        if n not in self.schemas:self.schemas[n]=json.loads(p.read_text())
        return self.schemas[n]
    def _load(self,p,n):
        d=load_machine_file(p);self.errors+=validate_schema(d,self._schema(n),str(p.relative_to(self.root)));return d
    def load(self):
        self.errors=[];p=self.root/'coordination/portfolio/PORTFOLIO.yml'
        if not p.is_file():self.errors.append("missing coordination/portfolio/PORTFOLIO.yml");return self
        self.portfolio=self._load(p,'portfolio.schema.json')
        for p in sorted((self.root/'coordination/campaigns').glob('*/CAMPAIGN.yml')):
            d=self._load(p,'campaign.schema.json');cid=d.get('campaign_id');self.campaigns[cid]=d
            if p.parent.name!=cid:self.errors.append(f"{p}: directory name must equal campaign_id {cid}")
        for p in sorted((self.root/'coordination/campaigns').glob('*/decisions/*.yml')):self.decisions.append(self._load(p,'decision.schema.json'))
        for p in sorted((self.root/'coordination/tasks').glob('*/TASK.yml')):
            d=self._load(p,'task.schema.json');tid=d.get('task_id');self.tasks[tid]=d
            if p.parent.name!=tid:self.errors.append(f"{p}: directory name must equal task_id {tid}")
            if d.get('campaign_id') not in self.campaigns:self.errors.append(f"{tid}: unknown campaign {d.get('campaign_id')}")
        for p in sorted((self.root/'research').glob('**/CLAIM.yml')):
            d=self._load(p,'claim.schema.json');cid=d.get('claim_id');
            if cid in self.claims:self.errors.append(f"duplicate claim id {cid}")
            self.claims[cid]=d;self.claim_paths[cid]=p
        for p in sorted((self.root/'reviews').glob('**/REVIEW.yml')):
            d=self._load(p,'review.schema.json');self.reviews.append(d);ok,why=review_grade_valid(d)
            if not ok:self.errors.append(f"{p.relative_to(self.root)}: {why}")
            if d.get('claim_id') not in self.claims:self.errors.append(f"{p.relative_to(self.root)}: unknown claim {d.get('claim_id')}")
        for p in sorted((self.root/'coordination/failed-routes').glob('*.yml')):
            d=self._load(p,'failed-route.schema.json');self.failed_routes[d.get('route_id')]=d
        for p in sorted((self.root/'coordination/proposals').glob('**/*.yml')):self.proposals.append(self._load(p,'proposal.schema.json'))
        for p in sorted((self.root/'coordination/outcomes').glob('*.yml')):
            d=self._load(p,'outcome.schema.json');self.outcomes[d.get('task_id')]=d
        self._load_locks();self._validate_claim_graph();self._validate_tasks();self._validate_proposals();self._validate_decisions();return self
    def _load_locks(self):
        root=self.root/'coordination/locks';groups={}
        if not root.exists():return
        for p in sorted(root.glob('**/*.yml')):
            d=self._load(p,'lock.schema.json');key=p.relative_to(root).as_posix()[:-4];lid=d.get('lock_id')
            if key not in d.get('collision_keys',[]):self.errors.append(f"{p.relative_to(self.root)}: path key {key!r} missing from collision_keys")
            if lid not in groups:groups[lid]=LockBundle(lid,d,set(),[])
            b=groups[lid];b.keys.add(key);b.paths.append(p)
        for lid,b in groups.items():
            if b.keys!=set(b.payload.get('collision_keys',[])):self.errors.append(f"lock bundle {lid}: file/key mismatch")
            if b.payload.get('task_id') not in self.tasks:self.errors.append(f"lock {lid}: unknown task {b.payload.get('task_id')}")
            try:
                if parse_time(b.payload['expires_at'])<=parse_time(b.payload['acquired_at']):self.errors.append(f"lock {lid}: expires_at must be after acquired_at")
            except Exception as e:self.errors.append(f"lock {lid}: invalid time: {e}")
        self.lock_bundles=groups
    def _validate_claim_graph(self):
        g={}
        for cid,c in self.claims.items():
            deps=[]
            for x in c.get('depends_on',[]):
                try:d=claim_dep_id(x)
                except VillageError as e:self.errors.append(f"{cid}: {e}");continue
                deps.append(d)
                if d==cid:self.errors.append(f"{cid}: self dependency")
                if d not in self.claims:self.errors.append(f"{cid}: unknown dependency {d}")
                elif self.claims[d].get('dependency_use') in {'NAVIGATION_ONLY','FORBIDDEN'}:self.errors.append(f"{cid}: load-bearing dependency {d} is {self.claims[d].get('dependency_use')}")
            g[cid]=deps
        temp=set();done=set()
        def dfs(n,stack):
            if n in done:return
            if n in temp:self.errors.append('claim dependency cycle: '+' -> '.join(stack+[n]));return
            temp.add(n)
            for x in g.get(n,[]):
                if x in g:dfs(x,stack+[n])
            temp.remove(n);done.add(n)
        for n in g:dfs(n,[])
    def _validate_tasks(self):
        gov=self.portfolio.get('governance',{});lo=gov.get('lease_ttl_min_hours',24);hi=gov.get('lease_ttl_max_hours',336)
        for tid,t in self.tasks.items():
            for a in t.get('assumptions',[]):
                if isinstance(a,dict) and a.get('claim_id') and a['claim_id'] not in self.claims:self.errors.append(f"{tid}: unknown assumption claim {a['claim_id']}")
            ttl=t.get('lease_ttl_hours')
            if isinstance(ttl,int) and not lo<=ttl<=hi:self.errors.append(f"{tid}: lease_ttl_hours outside portfolio bounds")
    def _validate_proposals(self):
        gov=self.portfolio.get('governance',{});cc=gov.get('default_campaign_proposal_cap_per_actor',1);tc=gov.get('default_task_proposal_cap_per_actor',3);m={}
        for p in self.proposals:
            if p.get('status')!='OPEN':continue
            a=p.get('actor_id');k=p.get('proposal_type');b='campaign' if k in {'NEW_CAMPAIGN','REOPEN_CAMPAIGN'} else 'task' if k=='NEW_TASK' else 'portfolio';m.setdefault(a,{});m[a][b]=m[a].get(b,0)+1
            if k=='NEW_CAMPAIGN':
                for f in ('new_ingredient','kill_conditions'):
                    if not p.get(f):self.errors.append(f"{p.get('proposal_id')}: NEW_CAMPAIGN requires {f}")
        for a,c in m.items():
            if c.get('campaign',0)>cc:self.errors.append(f"{a}: open campaign proposals exceed cap {cc}")
            if c.get('task',0)>tc:self.errors.append(f"{a}: open task proposals exceed cap {tc}")
    def _validate_decisions(self):
        for d in self.decisions:
            if d.get('campaign_id') not in self.campaigns:self.errors.append(f"decision {d.get('decision_id')}: unknown campaign {d.get('campaign_id')}")
    def derived_claim_validity(self):
        memo={};vis=set()
        def calc(cid):
            if cid in memo:return memo[cid]
            if cid in vis:return 'NEEDS_REREVIEW'
            vis.add(cid);c=self.claims[cid];r=c.get('validity_state','CURRENT')
            if r=='CURRENT':
                for x in c.get('depends_on',[]):
                    d=claim_dep_id(x)
                    if d not in self.claims or calc(d) in {'REFUTED','NEEDS_REREVIEW'}:r='NEEDS_REREVIEW';break
            vis.remove(cid);memo[cid]=r;return r
        for cid in self.claims:calc(cid)
        return memo
    def frontier_is_stale(self,c):
        f=c.get('frontier');
        if not f:return False
        try:return self.now.date()>parse_time(f['checked_at']).date()+timedelta(days=int(f['ttl_days']))
        except Exception:return False
    def effective_campaign_states(self):
        val=self.derived_claim_validity();out={}
        for cid,c in self.campaigns.items():
            stored=c.get('strategic_state')
            if stored=='CLOSED':out[cid]='CLOSED';continue
            bad=any(a.get('load_bearing') and (a.get('claim_id') not in self.claims or val.get(a.get('claim_id'))!='CURRENT' or a.get('dependency_use') in {'NAVIGATION_ONLY','FORBIDDEN'}) for a in c.get('assets',[]))
            out[cid]='REEVALUATION_REQUIRED' if bad else 'FRONTIER_REFRESH_REQUIRED' if stored=='ACTIVE' and self.frontier_is_stale(c) else stored
        return out
    def active_lock_bundles(self):return [b for b in self.lock_bundles.values() if lock_bundle_active(b,self.now)]
    def lock_for_task(self,tid,*,active_only=True):return [b for b in (self.active_lock_bundles() if active_only else self.lock_bundles.values()) if b.payload.get('task_id')==tid]
    def _claim_usable_for_assumption(self,cid):
        if cid not in self.claims:return False,f"unknown claim {cid}"
        c=self.claims[cid];v=self.derived_claim_validity().get(cid)
        if v!='CURRENT':return False,f"claim {cid} validity is {v}"
        if c.get('public_evidence')=='INTENTIONAL_PRIVATE':return False,f"claim {cid} evidence is INTENTIONAL_PRIVATE"
        if c.get('dependency_use') not in {'ALLOWED','SCOPED'}:return False,f"claim {cid} dependency use is {c.get('dependency_use')}"
        return True,'ok'
    def readiness(self,tid):
        r=[];t=self.tasks[tid];c=self.campaigns[t['campaign_id']];eff=self.effective_campaign_states()[t['campaign_id']];kind=t.get('task_kind')
        if self.portfolio.get('global_admission')!='OPEN':r.append('global admission paused')
        if t.get('stored_state')!='APPROVED':r.append(f"task stored_state is {t.get('stored_state')}")
        if c.get('strategic_state')=='CLOSED':r.append('campaign is CLOSED')
        if kind in MAINTENANCE_TASK_KINDS:
            if kind=='FRONTIER_REFRESH' and eff!='FRONTIER_REFRESH_REQUIRED':r.append('frontier refresh not currently required')
            elif eff=='CLOSED':r.append('campaign is CLOSED')
        elif eff!='ACTIVE':r.append(f"campaign effective_state is {eff}")
        if eff=='FRONTIER_REFRESH_REQUIRED' and t.get('frontier_sensitive') and kind!='FRONTIER_REFRESH':r.append('frontier is stale for frontier-sensitive task')
        for a in t.get('assumptions',[]):
            if isinstance(a,dict) and a.get('claim_id'):
                ok,why=self._claim_usable_for_assumption(a['claim_id']);
                if not ok:r.append(why)
        active=self.active_lock_bundles();ids={b.lock_id for b in active}
        if any(b.payload.get('task_id')==tid for b in active):r.append('task already has an active lock')
        ca={b.lock_id for b in active if self.tasks.get(b.payload.get('task_id'),{}).get('campaign_id')==t['campaign_id']}
        if len(ca)>=c.get('max_active_lanes',1):r.append('campaign active-lane capacity reached')
        if len(ids)>=self.portfolio.get('global_active_lane_cap',1):r.append('global active-lane capacity reached')
        keys=set().union(*(b.keys for b in active)) if active else set();ov=keys.intersection(t.get('collision_keys',[]))
        if ov:r.append('active collision keys: '+', '.join(sorted(ov)))
        at={b.payload.get('task_id') for b in active}
        if set(t.get('explicit_conflicts_with',[])).intersection(at):r.append('explicit task conflict is active')
        for x in at:
            if x in self.tasks and x!=tid and owned_paths_overlap(t.get('owned_paths',[]),self.tasks[x].get('owned_paths',[])):r.append(f"owned path overlap with active task {x}");break
        return not r,r
    def runtime_state(self,tid):
        if tid in self.outcomes:
            o=self.outcomes[tid]
            if o.get('review_required'):
                ids=o.get('claim_ids',[]);good=bool(ids)
                for cid in ids:
                    ok,_=independently_reproduced_eligible(self.claims.get(cid,{}).get('verification_modes',[]),[r for r in self.reviews if r.get('claim_id')==cid],universal_claim=bool(self.claims.get(cid,{}).get('universal_claim')));good&=ok
                if not good:return 'WAITING_REVIEW'
            return 'DONE'
        if self.lock_for_task(tid):return 'ACTIVE'
        if self.readiness(tid)[0]:return 'READY'
        if self.lock_for_task(tid,active_only=False):return 'EXPIRED'
        return 'BLOCKED'
    def validate(self):
        if not self.portfolio:self.load()
        cap=self.portfolio.get('governance',{}).get('default_actor_exclusive_lock_cap',1);counts={};active=self.active_lock_bundles()
        for b in active:
            if self.tasks.get(b.payload.get('task_id'),{}).get('parallelism')=='EXCLUSIVE':a=b.payload.get('actor',{}).get('id');counts[a]=counts.get(a,0)+1
        for a,n in counts.items():
            if n>cap:self.errors.append(f"{a}: active EXCLUSIVE locks {n} exceed cap {cap}")
        if len({b.lock_id for b in active})>self.portfolio.get('global_active_lane_cap',1):self.errors.append('global active-lane cap exceeded')
        return self.errors
    def status_rows(self):
        eff=self.effective_campaign_states();cr=[];tr=[]
        for cid in sorted(self.campaigns):cr.append((cid,eff[cid],len({b.lock_id for b in self.active_lock_bundles() if self.tasks.get(b.payload.get('task_id'),{}).get('campaign_id')==cid})))
        for tid in sorted(self.tasks):tr.append((tid,self.runtime_state(tid),self.readiness(tid)[1]))
        return cr,tr
    def render_portfolio(self):
        p=self.portfolio;lines=['# Research Portfolio','', '> GENERATED deterministically from time-independent canonical Portfolio/Campaign state. Do not hand-edit.','> Runtime effective state, active locks, lease expiry and READY status are intentionally excluded; run `python3 scripts/village.py status` for the live view.','',f"Global admission policy: **{p.get('global_admission')}**  ",f"Global active lane cap: **{p.get('global_active_lane_cap')}**  ",f"Public snapshot private source: `{p.get('source_snapshot',{}).get('private_canonical_main',{}).get('sha','')}`  ",f"Snapshot exported at: **{p.get('source_snapshot',{}).get('exported_at','')}**",'', '| Campaign | Priority | Stored strategic state | Lane cap |','|---|---:|---|---:|']
        for cid in sorted(self.campaigns,key=lambda x:(self.campaigns[x].get('priority',''),x)):
            c=self.campaigns[cid];lines.append(f"| `{cid}` — {c.get('title')} | {c.get('priority')} | **{c.get('strategic_state')}** | {c.get('max_active_lanes')} |")
        lines+=['','This committed view is a pure function of canonical files and contains no generation timestamp or live lease data.','Portfolio state allocates AIMath resources only. It does not restrict outside research or reuse rights.',''];return '\n'.join(lines)
    def render_board(self):
        lines=['# Research Board','', '> GENERATED deterministically from canonical Task specifications. Do not hand-edit.','> Runtime `READY/ACTIVE/BLOCKED/EXPIRED` state is not committed; run `python3 scripts/village.py status` for the live derivation.','', '| Task | Campaign | Kind | Stage | Stored state | Parallelism |','|---|---|---|---|---|---|']
        for tid in sorted(self.tasks):
            t=self.tasks[tid];lines.append(f"| `{tid}` — {t.get('title')} | `{t.get('campaign_id')}` | {t.get('task_kind')} | {t.get('research_stage')} | **{t.get('stored_state')}** | {t.get('parallelism')} |")
        lines+=['','This committed view contains no generation timestamp, lock ownership, lease expiry, or manually stored READY label.',''];return '\n'.join(lines)
    def render_dependency_graph(self):
        v=self.derived_claim_validity();lines=['# Claim Dependency Graph','', '> GENERATED from public `CLAIM.yml` metadata.','', '| Claim | Level | Explicit validity | Derived validity | Dependencies |','|---|---|---|---|---|']
        for cid in sorted(self.claims):
            c=self.claims[cid];deps=[claim_dep_id(x) for x in c.get('depends_on',[])];lines.append(f"| `{cid}` | {c.get('mathematical_level')} | {c.get('validity_state')} | **{v[cid]}** | {', '.join('`'+d+'`' for d in deps) or '—'} |")
        lines.append('');return '\n'.join(lines)
    def render_history(self):
        lines=['# Campaign History','', '> GENERATED append-only view of canonical campaign decision records.','', '| Date | Campaign | Decision | Reason |','|---|---|---|---|']
        for d in sorted(self.decisions,key=lambda x:(x.get('decided_at',''),x.get('campaign_id',''),x.get('decision_id',''))):lines.append(f"| {d.get('decided_at')} | `{d.get('campaign_id')}` | **{d.get('decision')}** | {str(d.get('reason','')).replace('|','\\|')} |")
        lines.append('');return '\n'.join(lines)
    def rendered_views(self):return {'docs/RESEARCH_PORTFOLIO.md':self.render_portfolio(),'docs/RESEARCH_BOARD.md':self.render_board(),'docs/DEPENDENCY_GRAPH.md':self.render_dependency_graph(),'docs/CAMPAIGN_HISTORY.md':self.render_history()}
    def generated_view_drift(self):
        e=[]
        for rel,x in self.rendered_views().items():
            p=self.root/rel
            if not p.is_file():e.append(f"missing generated view {rel}")
            elif p.read_text().rstrip()!=x.rstrip():e.append(f"generated view drift: {rel}")
        return e
