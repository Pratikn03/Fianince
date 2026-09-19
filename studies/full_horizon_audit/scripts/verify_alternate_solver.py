#!/usr/bin/env python3
"""Separate constraint construction + HiGHS interior-point check.
Uses the same solver library with a different algorithm; NOT external replication.
"""
from __future__ import annotations
import os
for name in ('OPENBLAS_NUM_THREADS','OMP_NUM_THREADS','MKL_NUM_THREADS'):os.environ[name]='1'
from pathlib import Path
import json,csv,time
import numpy as np
import pandas as pd
from scipy.stats import norm
from scipy.optimize import linprog
ROOT=Path(__file__).resolve().parents[1]
def build(y,se,floor):
 H=len(y);edges=np.exp(np.linspace(np.log(floor),0.,65));low=[];high=[];means=[];radii=[]
 zt=norm.ppf(1-.025/512);zs=norm.ppf(1-.025/16)
 features=[('tap',j,y[j],zt*se) for j in range(H)]
 for h in [4,16,64,256]:
  if h<=H:features += [('sum',h,float(sum(y[:h])),zs*se*np.sqrt(h))]
 for h in [4,16,64,256]:
  if h<=H:features += [('tap',h-1,y[h-1],zs*se)]
 for kind,j,mean,rad in features:
  if kind=='sum':
   v0=1-(1-edges[:-1])**j;v1=1-(1-edges[1:])**j
  else:
   f=lambda r:r*(1-r)**j
   v0=np.minimum(f(edges[:-1]),f(edges[1:]))
   v1=f(np.maximum(edges[:-1],np.minimum(edges[1:],1./(j+1))))
  low.append(np.maximum(0,v0-1e-13));high.append(v1+1e-13);means.append(mean);radii.append(rad)
 low=np.array(low);high=np.array(high);means=np.array(means);radii=np.array(radii)
 return np.vstack([low,-high]),np.r_[means+radii,-means+radii]
def main():
 a=np.load(ROOT/'data/full_measurements.npz');cases=json.loads((ROOT/'data/configurations.json').read_text())
 main=pd.read_csv(ROOT/'results/paired_comparison.csv');main=main[(main.H==256)&(main.repetition_id==0)].set_index('dataset_id')
 rows=[];start=time.perf_counter()
 for i,r in main.iterrows():
  c=cases[int(r.case_id)];y=a['taps'][i]/(1-c['a']);se=float(a['tap_standard_errors'][i])/(1-c['a']);A,b=build(y,se,c['eta_floor'])
  opts={'primal_feasibility_tolerance':1e-9,'dual_feasibility_tolerance':1e-9,'ipm_optimality_tolerance':1e-10,'time_limit':5.}
  l=linprog(np.ones(64),A_ub=A,b_ub=b,bounds=(0,None),method='highs-ipm',options=opts)
  u=linprog(-np.ones(64),A_ub=A,b_ub=b,bounds=(0,None),method='highs-ipm',options=opts)
  finite=l.success and u.success
  row={'dataset_id':i,'low_status':l.status,'upper_status':u.status,'primary_status':r.lp_status,'ipm_lower':l.fun if finite else None,'ipm_upper':-u.fun if finite else None,'primary_lower':r.lp_lower,'primary_upper':r.lp_upper}
  if finite:
   row['max_bound_difference']=max(abs(l.fun-r.lp_lower),abs(-u.fun-r.lp_upper));assert row['max_bound_difference']<2e-5,row
  else:
   row['unverified_timeout_or_failure'] = not (r.lp_status=='model_conflict' and (l.status==2 or u.status==2))
  rows.append(row)
  if len(rows)%12==0:print('checked',len(rows),'elapsed',round(time.perf_counter()-start,2),flush=True)
  pd.DataFrame(rows).to_csv(ROOT/'results/alternate_solver_rows.csv',index=False)
 pd.DataFrame(rows).to_csv(ROOT/'results/alternate_solver_rows.csv',index=False)
 summary={'datasets':len(rows),'selection':'all 108 cases x 2 noises at repetition 0, H=256','same_solver_library_different_algorithm':True,'separate_feature_construction':True,'all_comparisons_passed':not any(r.get('unverified_timeout_or_failure',False) for r in rows),'unverified':sum(r.get('unverified_timeout_or_failure',False) for r in rows),'max_bound_difference':float(pd.DataFrame(rows).max_bound_difference.max()),'tolerance':2e-5,'seconds':time.perf_counter()-start}
 (ROOT/'results/alternate_solver_summary.json').write_text(json.dumps(summary,indent=2)+'\n');print(json.dumps(summary,indent=2))
if __name__=='__main__':main()
