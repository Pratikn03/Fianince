"""Exact row verification against outputs, without importing document writers."""
from pathlib import Path
import json,re,hashlib
import numpy as np
import pandas as pd
from scipy import stats
HERE=Path(__file__).resolve().parent;BASE=HERE.parent;ROOT=HERE.parents[2]
REV=ROOT/'research_extension/paper_revision_20261006/results'
def load(p):return json.loads(p.read_text())
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def escape(s):return str(s).replace('_',r'\_').replace('%',r'\%').replace('&',r'\&')
def ci(v,places=7):return '['+', '.join(format(x,f'.{places}f') for x in v)+']'
def run():
 source=HERE/'Machine_Markets_Current_Evidence_Supplement_20261008.tex';text=source.read_text();checks=[]
 def check(label,expected,result):
  pos=text.index(r'\label{'+label+'}');a=text.rfind(r'\begin{longtable}',0,pos);b=text.index(r'\end{longtable}',pos)
  body=text[a:b].split(r'\endhead',1)[1].split(r'\bottomrule',1)[0]
  actual=[[re.sub(r'\s+',' ',c).strip() for c in line.rstrip()[:-2].split('&')] for line in body.splitlines() if '&' in line and line.rstrip().endswith(r'\\')]
  expected=[[str(c) for c in row] for row in expected];assert actual==expected,label
  checks.append(dict(label=label,rows=len(actual),cells=sum(map(len,actual)),result=str(result.relative_to(ROOT)),result_sha256=sha(result)))
 p=HERE/'recorder_bin_completeness.json';rows=[]
 for asset,d in load(p)['assets'].items():
  for k,v in d['strict_variants'].items():rows.append([asset,escape(k),v['n_dates'],v['n_segments'],v['n_transitions'],f"{v['mean_Q']:.7f}",ci(v['date_reference_interval'])])
 check('tab:strict_recorder',rows,p)
 p=HERE/'panel_lag_summary.json'
 check('tab:full_lag_intervals',[[r['asset'][:-4],r['L'],10*r['L'],r['n_dates'],f"{r['mean']:.7f}",ci(r['ci95'])] for r in load(p)],p)
 p=HERE/'calendar_inference_sensitivity.json'
 check('tab:calendar_references',[[escape(r['variant']),r['metric'],r['calendar_bandwidth_days'],r['n_dates'],f"{r['mean']:.7f}",ci(r['normal_reference_interval'])] for r in load(p)['rows']],p)
 p=BASE/'cross_venue/restored_panel_summary.json';rows=[]
 for metric in ['Q','S']:
  for kind in ['classical','asset_cluster','date_cluster']:
   r=load(p)['fee_observed'][metric][kind];rows.append([metric,escape(kind),r['df'],f"{r['beta']:.7f}",f"{r['se']:.7f}",f"{r['p_t']:.6f}",ci(r['ci95'])])
 check('tab:fee_reference_intervals',rows,p)
 p=BASE/'model_diagnostics/covariance_complete.json';rows=[]
 for asset,d in load(p)['assets'].items():
  for key,r in d['cases'].items():
   np.testing.assert_allclose(r['p_chi2'],stats.chi2.sf(r['J_stat'],r['df']))
   assert r['df']==r['moment_rank']-r['parameter_jacobian_rank']==4 and r['p_chi2']<.05
   assert len(r['starts'])==6 and r['best_success'] and r['rho']<1
   assert np.linalg.eigvalsh(r['innovation_covariance']).min()>0
   np.testing.assert_allclose(np.array(r['stationary_covariance']),np.array(r['J_normalized'])@np.array(r['stationary_covariance'])@np.array(r['J_normalized']).T+np.array(r['innovation_covariance']),rtol=1e-9,atol=1e-10)
   rows.append([asset,escape(key),r['n_rows'],r['df'],f"{r['J_stat']:.5f}",f"{r['p_chi2']:.4g}",f"{r['Q']:.7f}"])
 check('tab:covariance_all_cases',rows,p)
 p=BASE/'cross_venue/joint_fevd_summary.csv';rows=[]
 for r in pd.read_csv(p).itertuples():rows.append([r.asset,r.horizon_seconds,f'{r.rho:.7f}',f'{r.bn_price_to_cb_price_generalized:.5f}',f'[{r.bn_price_to_cb_price_order_min:.5f}, {r.bn_price_to_cb_price_order_max:.5f}]',f'{r.cb_price_to_bn_price_generalized:.5f}'])
 check('tab:joint_fevd_all_horizons',rows,p)
 p=BASE/'regime_model/market_results.json';rows=[];selected_iteration_limits=0
 for name,d in load(p)['datasets'].items():
  assert [f['date'] for f in d['folds']]==[f'2021-04-{day}' for day in range(13,20)]
  for fold in d['folds']:
   assert max(fold['train_dates'])<fold['date']
   selected_iteration_limits+=sum(v['selected']['status']=='ITERATION_LIMIT' for v in fold['models'].values())
  for key,label in [('variance_only','Var--OLS'),('coefficients_and_variance','Full--OLS'),('full_minus_variance_only','Full--Var')]:
   a=d['summary'][key]['mse'];b=d['summary'][key]['negative_log_score']
   assert a['ci95'][0]<=0<=a['ci95'][1]
   if key=='full_minus_variance_only':assert b['ci95'][0]<=0<=b['ci95'][1]
   rows.append([escape(name),label,f"{a['mean']:.5f}",ci(a['ci95'],5),f"{b['mean']:.5f}",ci(b['ci95'],5)])
 check('tab:all_switching_forecasts',rows,p)
 p=HERE/'high_power_table16_results.json';rows=[]
 for r in load(p)['cells']:rows.append([f"{r['S']:.2f}",f"{r['S']+.4:.2f}",f"{r['capital_multiplier']:.1f}",f"{r['mean_shock']:.1f}",r['halt_count'],r['default_count'],f"{r['mean_min_equity']:.4f}"])
 check('tab:all_funded_replays',rows,p)
 p=REV/'dealer_reproduction.json'
 check('tab:all_lagged_dealer_cells',[[f"{r['S']:.2f}",f"{r['L']:.0f}",r['mode'],r['halts'],r['n'],f"{r['rate']:.4f}",ci(r['ci95_exact'],5)] for r in load(p)['cells']],p)
 p=HERE/'january_forecast_results.json';january=load(p);rows=[]
 for lag,r in january['summary']['paired'].items():
  for target,v in r['variables'].items():
   ar=january['summary']['models']['AR'+lag]['equal_date_mean_MSE'][target]
   rows.append([lag,target,r['n_dates'],f'{ar:.7f}',f"{v['AR_minus_VAR_mean_loss']:.7f}",ci(v['date_t95']),f"{v['relative_mean_improvement_percent']:.5f}"])
 check('tab:january_forecast_all_lags',rows,p)
 p=HERE/'submission_completion/equity_source_sensitivity.json';rows=[]
 for block,v in load(p)['by_block'].items():
  for metric in ['Q','S']:rows.append([block,metric,v['n_raw'],v['n_sessions'],f"{v[metric]['mean']:.7f}",ci(v[metric]['date_t95'])])
 check('tab:equity_full_source',rows,p)
 assert len(checks)==11 and selected_iteration_limits==4
 # Numeric prose is separately checked, rather than inferred from table coverage.
 main=(ROOT/'paper/Machine_Markets_JF_Submission.tex').read_text()
 for r in january['summary']['paired'].values():assert f"{r['variables']['price']['relative_mean_improvement_percent']:.5f}" in main
 panel=load(BASE/'cross_venue/restored_panel_summary.json')['summaries']['observed']
 assert f"{panel['S']['mean']-panel['Q']['mean']:.7f}" in main
 # January summary is independently aggregated from every preserved segment.
 depth=load(REV/'depth_reanalysis.json');frame=pd.read_csv(REV/'depth_daily_estimates.csv')
 assert len(frame)==depth['summary']['n_segments']==152 and int(frame.n.sum())==844621
 for key in ['Q','Q30']:
  vals=np.array([np.average(g[key],weights=g.n) for _,g in frame.groupby('date')]);half=stats.t.ppf(.975,11)*vals.std(ddof=1)/np.sqrt(12)
  np.testing.assert_allclose(depth['summary'][key]['mean'],vals.mean(),rtol=1e-9)
  np.testing.assert_allclose(depth['summary'][key]['ci95'],[vals.mean()-half,vals.mean()+half],rtol=1e-9)
  assert f"{vals.mean():.9f}" in main
 for asset in ['BTC','ETH','ADA']:
  r=load(BASE/'model_diagnostics/covariance_complete.json')['assets'][asset]['cases']['global_10']
  assert f"{r['J_stat']:.4f}" in main
 joint=pd.read_csv(BASE/'cross_venue/joint_fevd_summary.csv')
 for asset in ['BTC','ETH','ADA']:assert f"{joint[joint.asset==asset].rho.iloc[0]:.6f}" in main
 r=joint[(joint.asset=='BTC')&(joint.horizon_seconds==60)].iloc[0]
 assert f'{r.bn_price_to_cb_price_generalized:.6f}' in main
 out=dict(status='ELEVEN_SUPPLEMENT_TABLES_EXACT_ROWS_AND_NAMED_PROSE_MATCH',source_sha256=sha(source),checks=checks,rows=sum(r['rows'] for r in checks),cells=sum(r['cells'] for r in checks),selected_forecast_iteration_limit_count=selected_iteration_limits,limits=['Saved-output arithmetic/display and maintained-matrix identities; not independent raw replication of every historical fit.','No guaranteed serial confidence coverage, causal identification, market calibration, global novelty or specialist-review certification.'])
 (HERE/'evidence_supplement_verification.json').write_text(json.dumps(out,indent=2)+'\n');print(out['status'],out['rows'],out['cells'])
if __name__=='__main__':run()
