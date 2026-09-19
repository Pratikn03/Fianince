#!/usr/bin/env python3
"""Internal alternate implementation. Imports NO project modules.

This verifier is not an external reviewer and does not establish novelty.
"""
from pathlib import Path
import json
import numpy as np,pandas as pd
from scipy.stats import t,binomtest
from scipy.optimize import linprog
ROOT=Path(__file__).resolve().parents[1]


def regress(X,y,c=None,alpha=.05):
    b=np.linalg.lstsq(X,y,rcond=None)[0];n,d=X.shape
    residual=y-X@b;variance=(residual@residual)/(n-d)
    u,s,vh=np.linalg.svd(X,full_matrices=False)
    if c is None:c=np.r_[0.,np.ones(d-1)]
    c=np.asarray(c,float)
    se=np.sqrt(variance*np.sum(((vh@c)/s)**2));hat=c@b
    radius=t.isf(alpha/2,n-d)*se+1e-12
    lo=hat-radius;hi=hat+radius
    return hat,lo,hi,'stable' if hi<1 else ('unstable' if lo>1 else 'inconclusive')


def public_rows(P,rates,T):
    X=[];y=[]
    for i,stop in enumerate(T):
        # Closed-form convolution, not the project's recursive implementation.
        values=[]
        for eta in rates:
            weights=eta*(1-eta)**np.arange(stop-3,-1,-1)
            values.append(P[i,:stop-2]@weights)
        X.append([1.,P[i,stop-2],*values]);y.append(P[i,stop-1])
    return np.array(X),np.array(y)


def main():
    total=0;maxdiff=0;labels=0;public_checks=0
    for datafile,csv in [('linear_terminal_rows.npz','linear_panels.csv'),('endpoint_terminal_rows.npz','endpoint_confirmation.csv')]:
        z=np.load(ROOT/'data'/datafile);rows=pd.read_csv(ROOT/'results'/csv)
        allX=z['X'];ally=z['y'];offsets=z['offsets']
        for i,row in rows.iterrows():
            a,b=offsets[i];ans=regress(allX[a:b],ally[a:b]);expected=row[['estimate','lower','upper']].to_numpy(float)
            maxdiff=max(maxdiff,float(np.max(np.abs(expected-np.array(ans[:3])))))
            assert np.allclose(expected,ans[:3],atol=1e-8,rtol=1e-8)
            assert ans[3]==row['label'];labels+=1;total+=1
    print('Regression rows checked:',total,flush=True)
    for f in sorted((ROOT/'data').glob('linear_public_*.npz')):
        z=np.load(f);X,y=public_rows(z['prices'],z['rates'],np.full(len(z['prices']),64));ans=regress(X,y)
        mid=int(f.stem.split('_')[2]);design=f.stem.split('_',3)[3]
        rows=pd.read_csv(ROOT/'results/linear_panels.csv');row=rows[(rows.model_id==mid)&(rows.design==design)&(rows.steps==64)&(rows.episodes==128)&(rows.replicate==0)].iloc[0]
        assert np.allclose(ans[:3],row[['estimate','lower','upper']].to_numpy(float),atol=1e-8)
        public_checks+=1
    tails=pd.read_csv(ROOT/'results/measured_tail.csv');raw=np.load(ROOT/'data/linear_terminal_rows.npz');TX=raw['X'];Ty=raw['y'];TO=raw['offsets'];tail_checks=0
    for i,row in tails.iterrows():
        a,b=TO[i];eta=np.array([.5,row.slow]);ans=regress(TX[a:b],Ty[a:b],np.r_[0.,0.,(1-eta)**64],.025)
        lo=max(0,ans[1]);hi=min((1-row.slow)**64,ans[2])
        assert np.allclose([lo,hi],[row.lower,row.upper],atol=1e-8,rtol=1e-8);tail_checks+=1
    interval_checks=0;maxcidiff=0
    rows=pd.read_csv(ROOT/'results/financial_budget_panels.csv')
    for sid,group in rows.groupby('setting_id'):
        ev=np.load(ROOT/f'data/finance_episodes_{sid}.npz')['event'].reshape(40,512)
        for _,row in group.iterrows():
            k=int(ev[int(row.panel),:int(row.episodes)].sum());assert k==row.events
            ci=binomtest(k,int(row.episodes)).proportion_ci(1-.05/3,method='exact')
            diff=max(abs(ci.low-row.lower),abs(ci.high-row.upper));maxcidiff=max(maxcidiff,diff);assert diff<1e-9;interval_checks+=1
    inputs=np.load(ROOT/'replication/constraint_inputs.npz');qref=np.load(ROOT/'replication/constraint_reference.npz')['fill'];max_fill=0.
    for i in range(len(qref)):
        C,I,P,D,E=(float(inputs[k][i]) for k in ['cash','inventory','price','desired','equity0']);s=1 if D>=0 else -1
        A=np.array([[1.],[-1.],[P+.01*s],[P+2*.01*s],[-P+2*.01*s]])
        b=np.array([10-I,10+I,C+E,2*E-P*I,2*E+P*I])
        opt=linprog([-s],A_ub=A,b_ub=b,bounds=[(min(0,D),max(0,D))],method='highs')
        assert opt.success
        max_fill=max(max_fill,abs(opt.x[0]-qref[i]));assert abs(opt.x[0]-qref[i])<1e-7
    casherr=shareerr=markerr=0.;ledger_paths=0
    for f in (ROOT/'data').glob('finance_ledger_example_*.npz'):
        z=np.load(f);L=z['ledger'];cash=L[:,:,0,:];inv=L[:,:,1,:];marked=L[:,:,2,:]
        casherr=max(casherr,float(np.abs(cash.sum(axis=2)-cash[0].sum(axis=1)).max()))
        shareerr=max(shareerr,float(np.abs(inv.sum(axis=2)).max()))
        markerr=max(markerr,float(np.abs(marked-(cash+inv*(100+z['prices'].T[:,:,None]))).max()))
        ledger_paths+=L.shape[1]
    assert casherr<1e-7 and shareerr<1e-8 and markerr<1e-8
    report={'regression_rows_recomputed':total,'matching_labels':labels,'max_regression_difference':maxdiff,'public_path_filter_checks':public_checks,'binomial_rows_recomputed':interval_checks,'max_binomial_difference':maxcidiff,'independent_LP_fill_checks':len(qref),'max_fill_difference':max_fill,'ledger_paths_checked':ledger_paths,'ledger_cash_error':casherr,'ledger_share_error':shareerr,'ledger_mark_error':markerr,'tail_intervals_recomputed':tail_checks,'uses_project_imports':False,'outside_replication':False}
    (ROOT/'results/standalone_verification.json').write_text(json.dumps(report,indent=2));print(json.dumps(report,indent=2))

if __name__=='__main__':main()
