"""Create-only, protocol-bound finite-grid runner. Run as a module."""
import argparse
from collections import Counter
from datetime import datetime, timezone
from decimal import Decimal as D
from fractions import Fraction as F
import hashlib
import json
from pathlib import Path
import platform
import subprocess
import traceback
from .model import Engine, Interval, PAIRS, rules, states, sign

HERE=Path(__file__).resolve().parent
SEALS={
    'mechanism_dossier_20260926':'4421b8aed40305317b205811e45c555f93622d84dbc305e068783c3bbaff4a6b',
    'mechanism_formal_v1':'23bace71af7203e1e9d0713a0de24dedd73a5ce54b92f4d302f9e8da07286be5',
}


def digest(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def encode(x):
    if isinstance(x,F):
        return {'rational':str(x)}
    if isinstance(x,Interval):
        return {'lo':str(x.lo),'hi':str(x.hi),'precision':x.precision}
    raise TypeError(type(x).__name__)


def decode_number(x):
    return F(x['rational']) if 'rational' in x else Interval(D(x['lo']),D(x['hi']),x['precision'])


def write_json(path,data):
    with Path(path).open('x') as f:
        json.dump(data,f,default=encode,sort_keys=True,indent=2,allow_nan=False)
        f.write('\n')


def check_protocol(root,lock):
    if digest(root/'PROTOCOL.md')!=lock['protocol_sha256']:
        raise RuntimeError('locked protocol mismatch')


def check_seal(root,expected):
    if digest(root/'manifest.json')!=expected:
        raise RuntimeError(f'seal mismatch: {root}')
    files=json.loads((root/'manifest.json').read_text()).get('files_sha256')
    if not isinstance(files,dict) or not files:
        raise RuntimeError('empty seal inventory')
    for rel,h in files.items():
        p=(root/rel).resolve()
        if not p.is_relative_to(root.resolve()) or digest(p)!=h:
            raise RuntimeError(f'preserved artifact mismatch: {p}')
    return len(files)


def lock_protocol(evidence_root):
    evidence_root=evidence_root.resolve()
    inventory={k:check_seal(evidence_root/'research_extension'/k,v) for k,v in SEALS.items()}
    manuscript_files=[p for p in (evidence_root/'paper').glob('Machine_Markets*')
                      if p.suffix in ('.tex','.pdf')]
    lock={'created_utc':datetime.now(timezone.utc).isoformat(),
          'protocol_sha256':digest(HERE/'PROTOCOL.md'),
          'evidence_root':str(evidence_root),'sealed_counts':inventory,
          'sealed_manifests':SEALS,'external_preregistration':False,
          'baseline_commit':subprocess.check_output(['git','-C',str(evidence_root),'rev-parse','HEAD'],text=True).strip(),
          'manuscripts_sha256':{str(p.relative_to(evidence_root)):digest(p) for p in manuscript_files}}
    write_json(HERE/'protocol.lock.json',lock)
    return lock


def preservation(evidence_root,lock):
    if lock.get('sealed_manifests')!=SEALS:
        raise RuntimeError('seal anchors changed')
    counts={k:check_seal(evidence_root/'research_extension'/k,v) for k,v in SEALS.items()}
    for rel,h in lock['manuscripts_sha256'].items():
        if digest(evidence_root/rel)!=h:
            raise RuntimeError(f'manuscript changed: {rel}')
    return counts


def compatible(a,b):
    def bounds(x):
        return (x,x) if isinstance(x,F) else (F(x.lo),F(x.hi))
    al,ah=bounds(a);bl,bh=bounds(b)
    return max(al,bl)<=min(ah,bh)


def subtract(a,b):
    return {k:tuple(x-y for x,y in zip(a[k],b[k])) for k in ('total','minimum_ask2')} | {
        'periods':tuple(tuple(x-y for x,y in zip(pa,pb)) for pa,pb in zip(a['periods'],b['periods']))}


def contrasts(cells):
    rows=[]
    for own in (False,True):
        for rival_early in (False,True):
            deltas=[subtract(cells[(True,rival_early),(own,rival)],
                             cells[(False,rival_early),(own,rival)]) for rival in (False,True)]
            for name,data in zip(('frozen','learning','interaction'),
                                 (*deltas,subtract(deltas[1],deltas[0]))):
                rows.append(dict(own_learning=own,rival_early=rival_early,kind=name,**data))
    return rows


def nonnegative(x):
    if isinstance(x,F):
        return x>=0
    if x.lo>=0:
        return True
    if x.hi<0:
        return False
    return None


def game(cells,cost):
    mask=(False,True)
    pay={p:list(cells[p,mask]['total']) for p in PAIRS}
    for p in PAIRS:
        for i in (0,1):
            pay[p][i]-=cost*p[i]
        pay[p][3]-=cost*sum(p)
    ne,une,planner,uplanner=[],[],[],[]
    for p in PAIRS:
        responses=[nonnegative(pay[p][i]-pay[tuple(not p[j] if j==i else p[j] for j in (0,1))][i]) for i in (0,1)]
        welfare=[nonnegative(pay[p][3]-pay[q][3]) for q in PAIRS if q!=p]
        for checks,yes,unknown in ((responses,ne,une),(welfare,planner,uplanner)):
            if all(x is True for x in checks):
                yes.append(p)
            elif not any(x is False for x in checks):
                unknown.append(p)
    return dict(cost=cost,mask=mask,certified_pure_equilibria=ne,
                unresolved_equilibrium_profiles=une,certified_planner_profiles=planner,
                unresolved_planner_profiles=uplanner,
                payoffs=[{'profile':p,'total':pay[p]} for p in PAIRS])


def classify_contrasts(rows):
    pairs=Counter(f"{sign(r['total'][0])}/{sign(r['total'][3])}" for r in rows)
    return {'n':len(rows),'strict_conflict':pairs['positive/negative'],
            'opposite_conflict':pairs['negative/positive'],'sign_pairs':dict(sorted(pairs.items()))}


def rule_id(name,tau):
    return name if tau is None else f'{name}_{str(tau).replace("/","_")}'


def source_hashes():
    return {n:digest(HERE/n) for n in ('model.py','run.py','PROTOCOL.md','protocol.lock.json')}


def run(output,precision,evidence_root):
    lock=json.loads((HERE/'protocol.lock.json').read_text())
    check_protocol(HERE,lock)
    preserved=preservation(evidence_root,lock)
    initial_source=source_hashes()
    output.mkdir(parents=True,exist_ok=False)
    write_json(output/'started.json',dict(utc=datetime.now(timezone.utc).isoformat(),
               precision=precision,python=platform.python_version(),source_sha256=initial_source,
               preserved=preserved,evidence_root=str(evidence_root)))
    summary=[]; count=0
    try:
        for name,tau in rules():
            engine=Engine(name,tau,precision); records=[]
            rid=rule_id(name,tau)
            for s in states():
                cells={(p,m):engine.evaluate(s['active'],s['shadow'],p,m) for p in PAIRS for m in PAIRS}
                records.append(dict(state=s,rule=rid,
                                    cells=[dict(profile=p,mask=m,**v) for (p,m),v in cells.items()],
                                    contrasts=contrasts(cells),game=game(cells,F(1,20))))
                count+=16
            write_json(output/(rid+'.json'),records)
            for family in ('baseline','shadow_only','active_shadow'):
                for kind in ('frozen','learning','interaction'):
                    selected=[c for r in records if r['state']['family']==family for c in r['contrasts']
                              if not c['own_learning'] and not c['rival_early'] and c['kind']==kind]
                    summary.append(dict(rule=rid,family=family,kind=kind,**classify_contrasts(selected)))
            print(json.dumps({'completed_rule':rid,'cells_so_far':count}),flush=True)
        if count!=10464:
            raise RuntimeError('incomplete grid')
        check_protocol(HERE,lock);preservation(evidence_root,lock)
        if source_hashes()!=initial_source:
            raise RuntimeError('source changed during run')
        write_json(output/'summary.json',{'status':'complete_grid_pending_cross_verification',
                    'cells':count,'states':109,'precision':precision,'rows':summary,
                    'source_sha256':initial_source,
                    'files_sha256':{p.name:digest(p) for p in output.glob('*.json') if p.name!='started.json'}})
    except BaseException:
        write_json(output/'failure.json',{'cells_finished':count,'traceback':traceback.format_exc()})
        raise


def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--lock',action='store_true')
    p.add_argument('--evidence-root',type=Path,default=HERE.parents[1])
    p.add_argument('--output',type=Path)
    p.add_argument('--precision',type=int,choices=(40,60),default=40)
    args=p.parse_args()
    if args.lock:
        print(json.dumps(lock_protocol(args.evidence_root),indent=2))
    elif args.output:
        run(args.output,args.precision,args.evidence_root.resolve())
    else:
        p.error('--lock or --output required')


if __name__=='__main__':
    main()
