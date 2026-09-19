#!/usr/bin/env python3
"""Independent audit of simultaneous noise events and all saved intervals.
Does not import the primary estimators or derive labels by fitting a model.
"""
from pathlib import Path
import json
import numpy as np
import pandas as pd
from scipy.stats import norm
ROOT=Path(__file__).resolve().parents[1]
def main():
 d=pd.read_csv(ROOT/'results/paired_comparison.csv');a=np.load(ROOT/'data/full_measurements.npz')
 err=(a['taps']-a['true_kernels'][a['case_ids']])/a['tap_standard_errors'][:,None]
 Hs=[4,16,64,256]
 zs=norm.ppf(1-.025/16);zc=norm.ppf(1-.025/(2*256));zold=norm.ppf(1-.05/16)
 sumerrs=np.column_stack([err[:,:h].sum(axis=1)/np.sqrt(h) for h in Hs]);terms=err[:,np.array(Hs)-1]
 coord=np.max(np.abs(err),axis=1)<=zc
 summaries=(np.abs(sumerrs)<=zs).all(axis=1)&(np.abs(terms)<=zs).all(axis=1)
 old=(np.abs(sumerrs)<=zold).all(axis=1)&(np.abs(terms)<=zold).all(axis=1)
 event=coord&summaries;idx=d.dataset_id.to_numpy()
 violations={};wrong_details=[]
 for m in ['lp','combined','legacy','budget']:
  active=event[idx] if m in ['lp','combined','budget'] else old[idx]
  finite=np.isfinite(d[m+'_lower'])&np.isfinite(d[m+'_upper'])
  covers=finite&(d[m+'_lower']<=d.true_gain_ratio+1e-7)&(d[m+'_upper']>=d.true_gain_ratio-1e-7)
  decided=d[m+'_label'].isin(['stable','unstable']);wrong=decided&(d[m+'_label']!=d.truth)
  violations[m]={'rows_on_event':int(active.sum()),'interval_failures_on_event':int((active&~covers).sum()),'wrong_decisions_on_event':int((active&wrong).sum()),'wrong_rows_total':int(wrong.sum())}
  assert not (active&~covers).any(),(m,'interval failure on the confidence event')
  assert not (active&wrong).any(),(m,'wrong decision on confidence event')
  if m=='lp':
   for _,r in d[wrong].iterrows():
    i=int(r.dataset_id);wrong_details.append({'dataset_id':i,'H':int(r.H),'case_id':int(r.case_id),'noise_id':int(r.noise_id),'truth':r.truth,'label':r.lp_label,'lower':r.lp_lower,'upper':r.lp_upper,'true_gain_ratio':r.true_gain_ratio,'simultaneous_event':bool(event[i]),'coordinate_event':bool(coord[i]),'summary_event':bool(summaries[i]),'max_standardized_tap_error':float(np.abs(err[i]).max())})
 result={'independent_datasets':len(event),'simultaneous_event_pass':int(event.sum()),'simultaneous_event_fail':int((~event).sum()),'empirical_event_probability':float(event.mean()),'nominal_lower_probability':.95,'union_bound_not_conditional_error_control':True,'events_use_all_256_taps_and_four_declared_horizons':True,'checks':violations,'lp_wrong_rows':wrong_details,'separate_code_path_no_primary_estimator_import':True}
 (ROOT/'results/confidence_event_audit.json').write_text(json.dumps(result,indent=2)+'\n');print(json.dumps(result,indent=2))
if __name__=='__main__':main()
