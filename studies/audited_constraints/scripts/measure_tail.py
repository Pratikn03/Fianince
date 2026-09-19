#!/usr/bin/env python3
from pathlib import Path
import sys,json
import numpy as np,pandas as pd
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT))
from src.inference import contrast_interval
from src.audit import tail_envelope
rows=pd.read_csv(ROOT/'results/linear_panels.csv');z=np.load(ROOT/'data/linear_terminal_rows.npz');X=z['X'];y=z['y'];offset=z['offsets'];ans=[]
for i,r in rows.iterrows():
 a,b=offset[i];eta=np.array([.5,r.slow]);c=np.r_[0,0,(1-eta)**64]
 ci=contrast_interval(X[a:b],y[a:b],c,.025);gain=contrast_interval(X[a:b],y[a:b],[0,1,1,1],.025)
 truth=float((.6*r.normalized_G*np.array([.6,.4])*(1-eta)**64).sum());env=tail_envelope(1,r.slow,64)
 # Intersection with model-implied [0,envelope]; empty intersection = conflict, NOT repaired.
 lo=max(0,ci['lower']);hi=min(env,ci['upper']);conflict=lo>hi
 ans.append({'panel_id':i,'slow':r.slow,'episodes':r.episodes,'steps':r.steps,'design':r.design,'true_tail':truth,'analytic_envelope':env,'lower':lo,'upper':hi,'model_conflict':conflict,'tail_covered':lo<=truth<=hi,'gain_covered':gain['lower']<=r.truth_a_plus_Q<=gain['upper'],'joint_covered':lo<=truth<=hi and gain['lower']<=r.truth_a_plus_Q<=gain['upper']})
a=pd.DataFrame(ans);a.to_csv(ROOT/'results/measured_tail.csv',index=False)
a.groupby(['slow','steps','design','episodes']).agg(panels=('panel_id','size'),median_upper=('upper','median'),envelope=('analytic_envelope','first'),joint_covered=('joint_covered','sum'),conflicts=('model_conflict','sum')).reset_index().to_csv(ROOT/'results/measured_tail_summary.csv',index=False)
(ROOT/'results/measured_tail_checks.json').write_text(json.dumps({'rows':len(a),'joint_covered':int(a.joint_covered.sum()),'tail_covered':int(a.tail_covered.sum()),'conflicts':int(a.model_conflict.sum()),'gain_alpha':.025,'tail_alpha':.025,'tail_horizon':64},indent=2))
