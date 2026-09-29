"""Differential checks and complete clean-copy reproduction, without overwrites."""
import argparse
from decimal import Decimal as D,localcontext
from fractions import Fraction as F
from itertools import product
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
from .model import PAIRS,states,rules,contains
from .run import (HERE,digest,write_json,decode_number,compatible,rule_id,
                  preservation,source_hashes,check_protocol)


def literal_history(state,profile,mask,tau,epsilon=F(1,10)):
    """Separate scalar-Decimal 100-digit enumeration of all 2,916 histories.

    Does not call production policy, settlement, update, stage or evaluator.
    This comparison is a numerical cross-check, not an independent proof of
    interval arithmetic or external human replication.
    """
    with localcontext() as context:
        context.prec=100
        def num(q):
            return D(q.numerator)/D(q.denominator)
        eps=num(epsilon);temperature=num(tau)
        active=[[num(x) for x in q] for q in state['active']]
        shadow=[[num(x) for x in q] for q in state['shadow']]
        def choose(q):
            w=[((x-max(q))/temperature).exp() for x in q]
            return [eps/3+(1-eps)*x/sum(w) for x in w]
        def pay(actions,v,z):
            quotes=[2+2*a for a in actions]; ask=min(quotes);c=v+z
            if c<ask:
                return [D(0)]*5
            fill=[D(1)/quotes.count(ask) if q==ask else D(0) for q in quotes]
            return [fill[i]*(ask-v) for i in (0,1)]+[D(c-ask),D(z),D(1)]
        events=[(v,z,D(n)/8) for v in (0,4) for z,n in ((-2,1),(2,2),(6,1))]
        initial=[choose(shadow[i] if profile[i] else active[i]) for i in (0,1)]
        result=[D(0)]*5
        for a,b in product(range(3),repeat=2):
            for v,z,p in events:
                first=pay((a,b),v,z)
                new=[q[:] for q in shadow]
                for i,action in enumerate((a,b)):
                    if mask[i]:
                        new[i][action]=(new[i][action]+first[i])/2
                later=[choose(q) for q in new]
                for aa,bb in product(range(3),repeat=2):
                    for vv,zz,pp in events:
                        weight=initial[0][a]*initial[1][b]*p*later[0][aa]*later[1][bb]*pp
                        second=pay((aa,bb),vv,zz)
                        for j in range(5):
                            result[j]+=weight*(first[j]+second[j])
        return tuple(result)


def require(condition,message='verification condition failed'):
    if not condition:
        raise AssertionError(message)


def validate_precision(data,expected):
    if type(expected) is not int or expected not in (40,60):
        raise RuntimeError('unexpected precision')
    if isinstance(data,dict):
        if 'precision' in data and data['precision']!=expected:
            raise RuntimeError('wrong or mixed precision')
        for value in data.values():
            validate_precision(value,expected)
    elif isinstance(data,list):
        for value in data:
            validate_precision(value,expected)


def compare_numeric(a,b):
    """Recursively compare data structure, requiring every enclosure to overlap."""
    if isinstance(a,dict) and ('rational' in a or {'lo','hi','precision'}<=a.keys()):
        require(compatible(decode_number(a),decode_number(b)),(a,b))
        return 1
    if isinstance(a,dict):
        require(isinstance(b,dict) and a.keys()==b.keys(),'different keys')
        return sum(compare_numeric(a[k],b[k]) for k in a)
    if isinstance(a,list):
        require(isinstance(b,list) and len(a)==len(b),'different list sizes')
        return sum(compare_numeric(x,y) for x,y in zip(a,b))
    require(a==b,(a,b))
    return 0


def read_checked(root,expected_precision=None):
    report=json.loads((root/'summary.json').read_text())
    require(report['cells']==10464 and report['states']==109,'wrong grid size')
    require(report['source_sha256']==source_hashes(),'different current source')
    expected_precision=report['precision'] if expected_precision is None else expected_precision
    validate_precision(report,expected_precision)
    expected={rule_id(n,t)+'.json' for n,t in rules()}
    require(set(report['files_sha256'])==expected,'missing result blocks')
    records=[]
    for name,h in report['files_sha256'].items():
        require(digest(root/name)==h,name)
        block=json.loads((root/name).read_text())
        require(len(block)==109,'incomplete state block')
        validate_precision(block,expected_precision)
        for row,s in zip(block,states()):
            require(row['state']['id']==s['id'],'state identity mismatch')
            require(len(row['cells'])==16,'incomplete cell block')
            require({(tuple(c['profile']),tuple(c['mask'])) for c in row['cells']}==set(product(PAIRS,repeat=2)),'profile/mask mismatch')
        records.extend(block)
    return report,records


def verify(p40,p60,output,evidence_root,clean=True):
    output.mkdir(parents=True,exist_ok=False)
    report={'passed':False,'external_replication':False}
    try:
        lock=json.loads((HERE/'protocol.lock.json').read_text())
        check_protocol(HERE,lock)
        report['preserved']=preservation(evidence_root,lock)
        require(p40.resolve()!=p60.resolve(),'distinct 40/60 result inputs required')
        forty,data40=read_checked(p40,40);sixty,data60=read_checked(p60,60)
        require(forty['rows']==sixty['rows'],'classification differs by precision')
        report['cross_precision_numeric_values']=compare_numeric(data40,data60)
        from research_extension.mechanism_dossier_20260926.exact_audit import evaluate as exact
        reference_count=0
        for row in data40:
            if row['rule']!='greedy':
                continue
            state=next(s for s in states() if s['id']==row['state']['id'])
            for cell in row['cells']:
                expected=exact(state['active'],state['shadow'],tuple(cell['profile']),tuple(cell['mask']))
                for key in ('total','minimum_ask2'):
                    require(all(decode_number(x)==y for x,y in zip(cell[key],expected[key])),'exact reference mismatch')
                require(all(decode_number(x)==y for xs,ys in zip(cell['periods'],expected['periods']) for x,y in zip(xs,ys)),'exact period mismatch')
                reference_count+=1
        report['exact_reference_cells']=reference_count
        require(reference_count==1744,'reference count mismatch')
        literal_rows=[]
        for s in (states()[0],states()[1],states()[-1]):
            for name,tau in rules()[1:]:
                row=next(r for r in data60 if r['state']['id']==s['id'] and r['rule']==rule_id(name,tau))
                for p in PAIRS:
                    got=literal_history(s,p,(False,True),tau)
                    cell=next(c for c in row['cells'] if tuple(c['profile'])==p and c['mask']==[False,True])
                    require(all(contains(decode_number(x),F(y)) for x,y in zip(cell['total'],got)),'literal history mismatch')
                    literal_rows.append(dict(state=s['id'],rule=row['rule'],profile=p,total=[str(x) for x in got]))
        write_json(output/'literal_histories.json',literal_rows)
        report['literal_cells']=len(literal_rows)
        report['histories_per_literal_cell']=2916
        report['clean_copy_reproduction']=False
        if clean:
            copied_files=sorted(p for p in HERE.glob('*.py'))+[HERE/'PROTOCOL.md',HERE/'protocol.lock.json']
            hashes={p.name:digest(p) for p in copied_files}
            # Context-managed temporary directory; only our temporary checkout is removed.
            with tempfile.TemporaryDirectory(prefix='mm-robustness-') as tmp:
                root=Path(tmp);dest=root/'research_extension'/'mechanism_robustness_v1'
                dest.mkdir(parents=True)
                for p in copied_files:
                    shutil.copy2(p,dest/p.name)
                require({p.name:digest(dest/p.name) for p in copied_files}==hashes,'copy hash mismatch')
                target=output/'clean_p40'
                env=dict(os.environ,PYTHONDONTWRITEBYTECODE='1')
                env.pop('PYTHONPATH',None)
                command=[sys.executable,'-m','research_extension.mechanism_robustness_v1.run',
                         '--output',str(target.resolve()),'--precision','40','--evidence-root',str(evidence_root)]
                proc=subprocess.run(command,cwd=root,env=env,capture_output=True,text=True)
                with (output/'clean_run.log').open('x') as f:
                    f.write(proc.stdout+proc.stderr)
                require(proc.returncode==0,proc.stderr)
                require({p.name:digest(dest/p.name) for p in copied_files}==hashes,'executed copy changed')
                require({p.name:digest(p) for p in copied_files}==hashes,'original source changed')
                reproduced,_=read_checked(target,40)
                require(reproduced==forty,'clean-copy output differs')
                report['clean_copy_reproduction']=True
                report['executed_copy_sha256']=hashes
        report['preserved_after']=preservation(evidence_root,lock)
        report['source_sha256']=source_hashes()
        report['verifier_sha256']=digest(Path(__file__))
        report['result_summaries_sha256']={str(p):digest(p/'summary.json') for p in (p40,p60)}
        report['passed']=True
    except BaseException as e:
        report['error']=repr(e)
        raise
    finally:
        write_json(output/'report.json',report)
    print(json.dumps(report,indent=2))


def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--p40',type=Path,default=HERE/'results/reviewed_p40')
    p.add_argument('--p60',type=Path,default=HERE/'results/reviewed_p60')
    p.add_argument('--output',type=Path,required=True)
    p.add_argument('--evidence-root',type=Path,default=HERE.parents[1])
    p.add_argument('--skip-clean',action='store_true')
    args=p.parse_args()
    verify(args.p40.resolve(),args.p60.resolve(),args.output.resolve(),args.evidence_root.resolve(),not args.skip_clean)


if __name__=='__main__':
    main()
