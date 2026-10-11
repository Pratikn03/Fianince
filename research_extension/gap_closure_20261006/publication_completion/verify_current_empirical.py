"""Independent aggregation/inference and current-source field verification.

Does not import the manuscript generator. Rejects stale fields and distinguishes
arithmetic/rendering checks from data rights, causality and specialist review.
"""
from pathlib import Path
import json,hashlib,re
import numpy as np
import pandas as pd
from scipy import stats,linalg
HERE=Path(__file__).resolve().parent;ROOT=HERE.parents[2];BASE=HERE.parent
REV=ROOT/'research_extension/paper_revision_20261006/results'
def load(p):return json.loads(p.read_text())
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def close(a,b):np.testing.assert_allclose(a,b,rtol=1e-9,atol=1e-12)
def date_ci(vals):
 v=np.array(vals);m=v.mean();h=stats.t.ppf(.975,len(v)-1)*v.std(ddof=1)/np.sqrt(len(v));return [m-h,m+h]
def cluster(y,X,groups=None):
 # Independent QR solve and sandwich, rather than the generator's lstsq routine.
 q,r=linalg.qr(X,mode='economic');beta=linalg.solve_triangular(r,q.T@y)
 e=y-X@beta;bread=linalg.inv(r)@linalg.inv(r).T;n,k=X.shape
 if groups is None:cov=bread*(e@e)/(n-k);df=n-k
 else:
  labels=np.unique(groups);scores=np.array([X[groups==g].T@e[groups==g] for g in labels])
  cov=bread@(scores.T@scores)@bread*len(labels)/(len(labels)-1)*(n-1)/(n-k);df=len(labels)-1
 se=np.sqrt(np.diag(cov));return beta,se,df
def table_body(source,label):
 p=source.index('\\label{'+label+'}');a=source.rfind('\\begin{table}',0,p);b=source.index('\\end{table}',p)
 return source[a:b]
def verify():
 source=ROOT/'paper/Machine_Markets_JF_Submission.tex';text=source.read_text();checks=[]
 panel=load(BASE/'cross_venue/restored_panel_summary.json');rows=load(BASE/'cross_venue/original_panel_reproduction.json')['rows']
 assert len(rows)==768 and len({(r['symbol'],r['date']) for r in rows})==768
 assert all(r['status']=='RAW_REPRODUCED' for r in rows)
 for var in ['legacy','observed','raw_return']:
  f=pd.DataFrame([dict(date=r['date'],symbol=r['symbol'],Q=r[var]['Q'],S=r[var]['S']) for r in rows])
  for key in ['Q','S']:
   vals=f.groupby('date')[key].mean().to_numpy();close(vals.mean(),panel['summaries'][var][key]['mean']);close(date_ci(vals),panel['summaries'][var][key]['date_t95'])
  close(float((f.Q>0).mean()),panel['summaries'][var]['share_Q_positive'])
  for asset,g in f.groupby('symbol'):
   close(g.Q.mean(),panel['summaries'][var]['by_asset'][asset]['Q'])
 checks.append('All768 raw-reproduced units: independently recomputed panel means/intervals/shares')
 # New lag grid must agree with two independently preserved observed diagnostics.
 lagrows=load(HERE/'panel_lag_reproduction.json')['rows'];lookup={(r['symbol'],r['date']):r for r in rows}
 derived=load(HERE/'panel_lag_summary.json')
 for r in lagrows:
  old=lookup[r['symbol'],r['date']]['observed']['segments'];assert len(old)==len(r['segments'])
  for seg,ref in zip(r['segments'],old):
   close(seg['fits']['1']['Q_L'],ref['Q']);close(seg['fits']['30']['Q_L'],ref['Q30'])
 for d in derived:
  vals=[]
  for r in lagrows:
   if r['symbol']!=d['asset']:continue
   vals.append(sum(s['n']*s['fits'][str(d['L'])]['Q_L'] for s in r['segments'])/sum(s['n'] for s in r['segments']))
  assert len(vals)==96;close(np.mean(vals),d['mean']);close(date_ci(vals),d['ci95'])
 checks.append('Full768-unit six-horizon lag grid: L1/L30 independent checks and all48 date summaries')
 # Independently reconstruct fee inference and references.
 f=pd.DataFrame([dict(symbol=r['symbol'],date=r['date'],Q=r['observed']['Q'],S=r['observed']['S']) for r in rows if r['year']==2022])
 treat=(f.symbol=='BTCUSDT').to_numpy(float);post=(f.date>='2022-07-08').to_numpy(float);X=np.column_stack([np.ones(len(f)),treat,post,treat*post])
 for dep in ['Q','S']:
  for kind,groups in [('classical',None),('asset_cluster',f.symbol.to_numpy()),('date_cluster',f.date.to_numpy())]:
   b,se,df=cluster(f[dep].to_numpy(),X,groups);saved=panel['fee_observed'][dep][kind]
   close(b[3],saved['beta']);close(se[3],saved['se']);assert df==saved['df'];close(2*stats.t.sf(abs(b[3]/se[3]),df),saved['p_t'])
   close([b[3]-stats.t.ppf(.975,df)*se[3],b[3]+stats.t.ppf(.975,df)*se[3]],saved['ci95'])
 checks.append('Corrected192-row fee coefficients, independent QR and allthree covariance references')
 # Replayed funded results must equal historical seed outputs, not just its table.
 fresh=load(HERE/'high_power_table16_results.json');saved=load(ROOT/'research_extension/outputs/high_power_table16_results.json')
 assert len(fresh['cells'])==len(saved['cells'])==22
 for a,b in zip(fresh['cells'],saved['cells']):
  for k in a:close(a[k],b[k])
  for event in ['halt','fail']:
   k=a[event+'_count'];n=a['n_reps'];lo=0 if k==0 else stats.beta.ppf(.025,k,n-k+1);hi=1 if k==n else stats.beta.ppf(.975,k+1,n-k)
   close(100*np.array([lo,hi]),a[event+'_ci_95'])
 audit=load(HERE/'funded_accounting_audit.json');assert all(r['default_count']==0 and r['max_accounting_residual']<1e-8 for r in audit['independent_legacy_replay'])
 checks.append('All22 funded seed-replay cells, exactbinomial intervals and independentcash identities')
 # Session summary arithmetic from separately saved equity estimates.
 sessions=pd.read_csv(REV/'equity_session_estimates.csv');equity=load(REV/'equity_reanalysis.json')
 for stock,g in sessions.groupby('stock'):
  ref=equity['per_stock'][str(stock)];assert len(g)==ref['n_sessions'];close(g.Q.mean(),ref['Q_mean']);close(g.S.mean(),ref['S_mean']);close(g.rho.max(),ref['max_rho'])
 checks.append('All49 equity-session aggregate means and maximal radii')
 # Completeness sensitivity retains different samples; verify their date aggregation.
 strict=load(HERE/'recorder_bin_completeness.json');seg=pd.read_csv(HERE/'strict_recorder_segment_estimates.csv')
 for asset,d in strict['assets'].items():
  assert sha(ROOT/'empirical_pipeline/cache'/f'{asset}_1sec_core_v2dedup.pkl')==d['cache_sha256']
  assert sum(d['occupied_second_histogram'].values())==d['occupied_bins']
  for name,v in d['strict_variants'].items():
   state,alignment=name.split('_');f=seg[(seg.asset==asset)&(seg.state==state)&(seg.alignment==alignment)]
   dates=np.array([np.average(g.Q,weights=g.n) for _,g in f.groupby('date')]);close(dates.mean(),v['mean_Q']);close(date_ci(dates),v['date_reference_interval'])
   assert len(dates)==v['n_dates'] and int(f.n.sum())==v['n_transitions']
 checks.append('Allnine strict recorder constructions and their source/date/count/interval chain')
 # Independent scalar-loop HAC sum on actual calendar spacings.
 calendar=load(HERE/'calendar_inference_sensitivity.json')
 for ref in calendar['rows']:
  groups={}
  for r in rows:groups.setdefault(r['date'],[]).append(r[ref['variant']][ref['metric']])
  names=sorted(groups);vals=np.array([np.mean(groups[d]) for d in names]);times=pd.to_datetime(names).to_numpy(dtype='datetime64[D]').astype(int);e=vals-vals.mean();score=float(e@e)
  for i in range(len(e)):
   for j in range(i+1,len(e)):
    w=max(0,1-(times[j]-times[i])/ref['calendar_bandwidth_days']);score+=2*w*e[i]*e[j]
  se=np.sqrt(score/(len(e)*(len(e)-1)));close(se,ref['se']);close([vals.mean()-stats.norm.ppf(.975)*se,vals.mean()+stats.norm.ppf(.975)*se],ref['normal_reference_interval'])
 checks.append('All32 calendar HAC references independently summed by elapsed-day pairs')
 # Recompute the new figure directly from economic recursions, without its matrix factory.
 witness=load(HERE/'capital_witness.json');p=witness['params']
 def impulse(delta):
  rates=[p['rate']] if delta==0 else [p['rate']-delta,p['rate']+delta];weights=[p['total_weight']] if delta==0 else [p['total_weight']/2]*2
  y=np.zeros(len(rates));x=0.;h=[]
  for t in range(p['horizon']):
   new=p['anchor']*x+p['impact']*sum(q*yi for q,yi in zip(weights,y))+p['impact']*(t==0)
   y=np.array([(1-rate)*yi+rate*new for yi,rate in zip(y,rates)]);x=new;h.append(x)
  return np.array(h)
 h0=impulse(0)
 for r in witness['separation_curve']:
  norm=np.linalg.norm(impulse(r['delta'])-h0);close(norm,r['impulse_difference_norm']);V=r['quantity_for_alpha']
  close(stats.norm.cdf(-V*norm/(2*p['observation_sd'])),p['alpha'])
  close((1+p['margin']-p['execution_fraction'])*p['impact']*V**2+(p['cost']+p['margin']*p['reference_price'])*V,r['capital_inside_robust_quantity_contract'])
 for r in witness['capital_error_time']:
  norms=np.sqrt(np.cumsum((impulse(.05)-h0)**2));close(stats.norm.cdf(-r['quantity_cap']*norms/(2*p['observation_sd'])),r['worst_error'])
 assert sha(ROOT/'paper/figures/fig_capital_information_20261008.pdf')==witness['plot_sha256']
 checks.append('Constructed capital/information figure independently recomputed from price-first recursions')
 # Quantitative body values from every listed generated field must resolve to actual outputs.
 ledger=load(HERE/'generated_field_ledger.json');field_counts={}
 bodies={};row_maps={}
 for table in {v['table'] for v in ledger['fields']}:
  body=table_body(text,table).split('\\midrule',1)[1].split('\\bottomrule',1)[0]
  actual=[line for line in body.splitlines() if '&' in line and line.rstrip().endswith('\\\\')]
  bodies[table]=actual
  keys=list(dict.fromkeys(v['row'] for v in ledger['fields'] if v['table']==table))
  assert len(keys)==len(actual),(table,len(keys),len(actual))
  row_maps[table]=dict(zip(keys,actual))
 for f in ledger['fields']:
  p=ROOT/f['source'];assert sha(p)==f['source_sha256'];v=load(p)
  for step in f['pointer']:v=v[step]
  if f['key']=='positive_share':v*=100
  close(v,f['value']);body=row_maps[f['table']][f['row']]
  assert re.search(r'(?<![\d.])'+re.escape(f['rendered'])+r'(?![\d.])',body),(f['table'],f['row'],f['rendered'])
  field_counts[f['table']]=field_counts.get(f['table'],0)+1
 # The main table universe is exact, including qualitative and preserved tables.
 labels=re.findall(r'\\label\{(tab:[^}]+)\}',text)
 expected={'tab:lit_comparison','tab:measurement_sensitivity','tab:datasets','tab:binance_panel','tab:cross_asset_panel','tab:natural_experiment_did','tab:dynamic_event_study','tab:threshold_var','tab:equity_benchmark','tab:funded_risk_surface','tab:dealer_drawdown_stats','tab:falsification','tab:lag_memory_controls','tab:empirical_grid'}
 assert set(labels)==expected and len(labels)==14
 # Prevent numerical/structural regressions that led to this revision.
 for bad in ['p < 10^{-100}','t > 18.0','7.4125','NASDQ','935{,}199','66.3 \\times 10^6$ one-second transitions','Q_{\\text{Rig}} = \\PanelQRig']:
  assert bad not in text,bad
 out=dict(status='SCOPED_ARITHMETIC_AND_DISPLAY_VERIFIED_SEMANTIC_LEDGER_REQUIRED',source_sha256=sha(source),checks=checks,generated_fields=len(ledger['fields']),field_counts=field_counts,main_tables=labels,
          limits=['Field membership checks are supplemented by separate exact row checks for the preserved recorder/monthly tables.','Not provider-rights, serial confidence coverage, causal identification, global novelty or independent specialist review certification.'])
 (HERE/'independent_empirical_verification.json').write_text(json.dumps(out,indent=2)+'\n')
 print('Independent empirical aggregation/inference passed;',len(ledger['fields']),'rendered field records;14-table universe')
if __name__=='__main__':verify()
