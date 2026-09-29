"""Post-hoc algebra-to-code diagnostic; not another fitted experiment."""
import argparse
from fractions import Fraction as F
import json
from pathlib import Path
from .model import Engine,states,rules,contains,sign
from .run import HERE,rule_id,decode_number,write_json,digest
from .verify import read_checked,require


def formulas(engine,state):
    active,shadow=state['active'],state['shadow']
    focal=engine.policy(shadow[0]);b=engine.policy(active[1]);q=shadow[1]
    d=focal[2]-focal[1]
    def low(action,reward):
        changed=list(q)
        changed[action]=(1-engine.alpha)*q[action]+engine.alpha*reward
        return engine.policy(tuple(changed))[0]
    rival_low=d*(b[1]/8*(low(1,F(4))-low(1,F(2)))
                +b[2]/8*(low(2,F(3))-low(2,F(0)))
                +3*b[2]/8*(low(2,F(1))-low(2,F(0))))
    return {'t0_profit':d*(b[2]-b[1])/4,
            't1_welfare':(1-focal[0])*rival_low/4}


def main(output):
    _,rows=read_checked(HERE/'results/reviewed_p60',60)
    checks=[]
    for name,tau in rules()[1:]:
        engine=Engine(name,tau,60)
        for s in states():
            row=next(r for r in rows if r['rule']==rule_id(name,tau) and r['state']['id']==s['id'])
            c=next(c for c in row['contrasts'] if not c['own_learning'] and not c['rival_early'] and c['kind']=='learning')
            prediction=formulas(engine,s)
            require(contains(prediction['t0_profit']-decode_number(c['periods'][0][0]),F(0)),'t0 profit mismatch')
            require(contains(prediction['t1_welfare']-decode_number(c['periods'][1][3]),F(0)),'t1 welfare mismatch')
            require(sign(prediction['t1_welfare'])=='negative','welfare sign unresolved')
            checks.append(dict(state=s['id'],rule=row['rule'],**prediction))
    write_json(output,dict(status='passed_posthoc_formula_check_not_formal_proof',
                          states_per_rule=109,rules=5,comparisons=2*len(checks),
                          source_sha256=digest(Path(__file__)),
                          result_summary_sha256=digest(HERE/'results/reviewed_p60/summary.json'),rows=checks))
    print(json.dumps({'states_rules':len(checks),'comparisons':2*len(checks),'passed':True}))


if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--output',required=True,type=Path)
    main(p.parse_args().output)
