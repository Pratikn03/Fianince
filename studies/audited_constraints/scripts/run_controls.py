#!/usr/bin/env python3
"""Assumption violations are deliberately fed to ungated inference."""
from pathlib import Path
import sys,json,hashlib
import numpy as np,pandas as pd
from scipy.stats import binom
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT))
from src.linear import simulate_linear
from src.inference import reconstruct_terminal,terminal_interval,binomial_interval
from src.audit import make_contract,validate_contract

cases=[('valid', [.378,.252],[.5,.1],[.5,.1],{}),
       ('omitted_slow_state',[.3,.36],[.5,.002],[.5],{}),
       ('noisy_regressors',[.378,.252],[.5,.1],[.5,.1],{'sensor_sd':.02}),
       ('nonzero_reset',[.378,.252],[.5,.02],[.5,.02],{'reset_sd':.2}),
       ('omitted_inventory_channel',[.252,.168],[.5,.02],[.5,.02],{'extra_inventory':.005})]

def main():
    rows=[]
    for ci,(name,q,eta,reported,extra) in enumerate(cases):
        J=np.zeros((3+(name=='omitted_inventory_channel'),)*2);J[0,0]=.4;J[0,1:3]=q;J[1:3,0]=eta;J[1:3,1:3]=np.diag(1-np.array(eta))
        if name=='omitted_inventory_channel':J[0,3]=extra['extra_inventory'];J[3,1:3]=q;J[3,3]=1
        rho=float(max(abs(np.linalg.eigvals(J))))
        for rep in range(80):
            z=simulate_linear(.4,q,eta,.02,512,64,210000000+ci*10000+rep,'impulse',**extra)
            X,y=reconstruct_terminal(z['prices'],reported);r=terminal_interval(X,y)
            rows.append({'control':name,'replicate':rep,'true_full_rho':rho,'declared_gain_target':.4+sum(q),**{k:v for k,v in r.items() if k not in ['coefficient_estimates']},'wrong_full_system_label':(r['label']=='stable' and rho>1)or(r['label']=='unstable'and rho<1)})
    df=pd.DataFrame(rows);df.to_csv(ROOT/'results/assumption_controls.csv',index=False)
    summary=df.groupby('control').agg(panels=('replicate','size'),wrong=('wrong_full_system_label','sum'),stable=('label',lambda x:(x=='stable').sum()),unstable=('label',lambda x:(x=='unstable').sum())).reset_index();summary.to_csv(ROOT/'results/assumption_control_summary.csv',index=False)
    digest=hashlib.sha256((ROOT/'src/linear.py').read_bytes()).hexdigest();good=make_contract([.5,.02],digest)
    modifications={'wrong_source':{'source_sha256':'forged'},'wrong_reset':{'reset':'unknown'},'inventory_channel':{'other_feedback_channels':['inventory']},'binding_execution':{'execution_regime':'constrained'},'quote_errors':{'observation':'noisy_quote'}}
    audit={'honest_contract':validate_contract(good,digest)}
    for name,change in modifications.items():audit[name]=validate_contract(dict(good,**change),digest)
    # Deliberately self-issued false rates with a correct code digest. A syntax gate cannot establish runtime truth.
    audit['self_issued_false_rates']=validate_contract(make_contract([.5,.1],digest),digest)
    audit['limitation']='Eligibility checks syntax and asserted scope. Truthful configuration and all-channel coverage require authenticated instrumentation or external inspection. A self-issued manifest is not sufficient.'
    (ROOT/'results/audit_controls.json').write_text(json.dumps(audit,indent=2))
    cal=[]
    for n in [32,128,512]:
        C=np.array([binomial_interval(k,n,.05/3) for k in range(n+1)])
        for p in np.linspace(0,1,1001):
            probs=binom.pmf(np.arange(n+1),n,p);ok=(C[:,0]<=p+1e-15)&(C[:,1]>=p-1e-15)
            cal.append({'n':n,'p':p,'exact_coverage':float(probs@ok)})
    pd.DataFrame(cal).to_csv(ROOT/'results/binomial_exact_coverage.csv',index=False)
    (ROOT/'results/control_summary.json').write_text(json.dumps({'control_panels':len(df),'control_episodes':len(df)*512,'binomial_p_grid_checks':len(cal),'min_exact_coverage':min(z['exact_coverage'] for z in cal),'declared_single_look_coverage':1-.05/3,'external_audit_done':False},indent=2))
    print(summary.to_string(index=False))

if __name__=='__main__':main()
