#!/usr/bin/env python3
"""Recompute descriptive statistics from complete saved, paired decisions."""
from pathlib import Path
import json
import numpy as np
import pandas as pd
ROOT=Path(__file__).resolve().parents[1]
METHODS=['legacy','budget','nnls','lp','combined']
def score(d,m):
 labels=d[m+'_label'];dec=labels.isin(['stable','unstable']);wrong=dec&(labels!=d.truth)
 out={'method':m,'n':len(d),'decided':int(dec.sum()),'decision_rate':float(dec.mean()),'wrong':int(wrong.sum()),'wrong_rate_unconditional':float(wrong.mean()),'wrong_rate_conditional':float(wrong.sum()/dec.sum()) if dec.sum() else None,'false_stable':int(((labels=='stable')&(d.truth=='unstable')).sum()),'false_unstable':int(((labels=='unstable')&(d.truth=='stable')).sum()),'inconclusive':int((labels=='inconclusive').sum()),'model_conflicts':int((labels=='model_conflict').sum())}
 if m!='nnls':
  lower=d[m+'_lower'];upper=d[m+'_upper'];finite=np.isfinite(lower)&np.isfinite(upper)
  coverage=finite&(lower<=d.true_gain_ratio+1e-8)&(upper>=d.true_gain_ratio-1e-8)
  out|={'intervals_finite':int(finite.sum()),'truth_in_interval':int(coverage.sum()),'interval_coverage_all':float(coverage.mean()),'median_width_finite':float((upper-lower)[finite].median())}
 return out
def main():
 d=pd.read_csv(ROOT/'results/paired_comparison.csv');assert len(d)==86400 and d.dataset_id.nunique()==21600
 rows=[]
 for (H,noise),v in d.groupby(['H','noise_id']):
  for m in METHODS:rows.append({'H':int(H),'noise_id':int(noise)}|score(v,m))
 pd.DataFrame(rows).to_csv(ROOT/'results/aggregate_comparison.csv',index=False)
 families=[]
 for noise,v in d.groupby('noise_id'):
  for m in METHODS:
   dec=v[m+'_label'].isin(['stable','unstable']);wrong=dec&(v[m+'_label']!=v.truth)
   events=wrong.groupby(v.dataset_id).any()
   families.append({'noise_id':int(noise),'method':m,'independent_datasets':len(events),'any_wrong_across_four_horizons':int(events.sum()),'family_wrong_rate':float(events.mean())})
 pd.DataFrame(families).to_csv(ROOT/'results/family_errors.csv',index=False)
 paired=[]
 for noise,v in d[d.H==256].groupby('noise_id'):
  for newer,older in [('lp','legacy'),('lp','budget'),('combined','budget'),('nnls','legacy')]:
   od=v[older+'_label'].isin(['stable','unstable']);nd=v[newer+'_label'].isin(['stable','unstable'])
   good_n=nd&(v[newer+'_label']==v.truth);good_o=od&(v[older+'_label']==v.truth)
   paired.append({'noise_id':int(noise),'newer':newer,'older':older,'n':len(v),'newly_decided':int((nd&~od).sum()),'lost_decisions':int((od&~nd).sum()),'net_more_decisions':int(nd.sum()-od.sum()),'percentage_point_change':float(100*(nd.mean()-od.mean())),'net_more_correct_decisions':int(good_n.sum()-good_o.sum())})
 pd.DataFrame(paired).to_csv(ROOT/'results/paired_changes.csv',index=False)
 x=pd.read_csv(ROOT/'results/resolution_sensitivity.csv');sens=[]
 for (m,res,noise),v in x.groupby(['method','resolution','noise_id']):
  dec=v.label.isin(['stable','unstable']);wrong=dec&(v.label!=v.truth)
  sens.append({'method':m,'resolution':int(res),'noise_id':int(noise),'n':len(v),'decided':int(dec.sum()),'decision_rate':float(dec.mean()),'wrong':int(wrong.sum()),'conflicts':int((v.label=='model_conflict').sum()),'failures':int((~v.status.isin(['ok','model_conflict'])).sum())})
 # Add primary configuration on identical sensitivity subset, not all primary cases.
 sv=d[(d.H==256)&d.repetition_id.isin([0,20,40,60,80])]
 for noise,v in sv.groupby('noise_id'):
  for m,res in [('nnls',129),('lp',64)]:
   s=score(v,m);sens.append({'method':'outer_lp' if m=='lp' else 'nnls','resolution':res,'noise_id':int(noise),'n':len(v),'decided':s['decided'],'decision_rate':s['decision_rate'],'wrong':s['wrong'],'conflicts':s['model_conflicts'],'failures':int((~v['lp_status' if m=='lp' else 'nnls_status'].isin(['ok','model_conflict'])).sum())})
 pd.DataFrame(sens).sort_values(['method','noise_id','resolution']).to_csv(ROOT/'results/sensitivity_summary.csv',index=False)
 summary={'source':'paired_comparison.csv; 108 fixed synthetic configurations, not random real markets','independent_measurement_vectors':21600,'paired_rows':86400,'raw_tap_measurements':21600*256,'primary_H256':[r for r in rows if r['H']==256],'family_errors':families,'paired_H256':paired,'statuses':{'lp':{str(k):int(v) for k,v in d.lp_status.value_counts().items()},'nnls':{str(k):int(v) for k,v in d.nnls_status.value_counts().items()}},'numerical_maxima':{k:float(d[k].max()) for k in ['nnls_kkt_violation','lp_dual_violation','lp_primal_violation','lp_max_gap','lp_max_repair']},'lp_and_combined_labels_identical':bool((d.lp_label==d.combined_label).all()),'claims':{'old_summary_superiority_supported':False,'real_market_validation':False,'independent_external_replication':False,'global_novelty_established':False}}
 (ROOT/'results/summary.json').write_text(json.dumps(summary,indent=2)+'\n')
 print(json.dumps({'H256':summary['primary_H256'],'paired_H256':paired,'statuses':summary['statuses']},indent=2))
if __name__=='__main__':main()
