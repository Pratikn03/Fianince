"""Retrospective full-coverage reconstruction of the same ten equity files.

Four largest finite price gaps define five anonymous blocks; an explicit endpoint
retains every source event. The rule does not authenticate company identities.
Preserved decimal conversion is applied to each block, so unit effects remain
part of this representation sensitivity rather than a physical-volume claim.
"""
from pathlib import Path
import sys,json,hashlib
import numpy as np
import pandas as pd
from scipy import stats
HERE=Path(__file__).resolve().parent;ROOT=HERE.parents[3]
sys.path.insert(0,str(ROOT));sys.path.insert(0,str(ROOT/'research_extension/paper_revision_20261006'))
from replay_equity_representation import load_needed,TARGET
from holdout_reanalysis import quote_ofi
from empirical_pipeline.feedback_var import var1
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def run():
 protocol=dict(status='RETROSPECTIVE_EXISTING_SOURCE_REPRESENTATION_SENSITIVITY',partition='Four largest finite first-ask price gaps; zero and explicit source endpoint; no company-label authentication',state='Log top midpoint x10000 minus gap/block-reset event EMA100',burn_events=500,minimum_raw_block_events=600,flow='Top-quote OFI under the preserved per-column decimal reconstruction; currency and volume normalization denominators unverified',inference='Equal-weight ten-day Student references with nine df, exploratory serial/reference limitations',source_receipt_sha256=sha(HERE/'fi_mirror_acquisition.json'))
 (HERE/'equity_source_sensitivity_protocol.json').write_text(json.dumps(protocol,indent=2)+'\n')
 rows=[];coverage=[]
 for day in range(1,11):
  name='Train_Dst_NoAuction_DecPre_CF_1.txt' if day==1 else f'Test_Dst_NoAuction_DecPre_CF_{day-1}.txt';p=TARGET/name;a=load_needed(p);n=len(a[0])
  gaps=np.abs(np.diff(a[0]));idx=np.argsort(gaps)[-4:]+1;boundaries=np.sort(np.r_[0,idx,n]);selected=np.sort(gaps[idx-1]);fifth=np.partition(gaps,-5)[-5]
  coverage.append(dict(day=day,source_states=n,boundaries=boundaries.tolist(),selected_price_gaps=selected.tolist(),largest_unselected_price_gap=float(fifth),smallest_boundary_to_largest_internal_gap=float(selected[0]/fifth),source_sha256=sha(p)))
  for block,(start,end) in enumerate(zip(boundaries[:-1],boundaries[1:]),1):
   raw=np.column_stack([a[k][start:end] for k in range(40)]);v=np.rint(raw*1e8).astype(np.int64);powers=[]
   for j in range(40):
    power=0
    while np.all(v[:,j]%10==0):
     if np.all(v[:,j]==0):raise ValueError('All-zero reconstructed column')
     v[:,j]//=10;power+=1
    powers.append(power)
   ap,az,bp,bs=[v[:,j].astype(float) for j in [0,1,2,3]];ofi,_=quote_ofi(bp,bs,ap,az)
   price=1e4*np.log((bp+ap)/2);x=price-pd.Series(price).ewm(span=100,adjust=False).mean().to_numpy()
   assert len(x)>=600 and np.all(bp<=ap)
   estimate=var1(x[500:],ofi[500:]);rows.append(dict(day=day,block=block,n_raw=int(end-start),n_states=int(end-start-500),price_decimal_powers=[powers[j] for j in range(0,40,2)],top_bid_ask_volume_powers=[powers[3],powers[1]],**estimate))
 f=pd.DataFrame(rows);summaries={}
 for block,g in f.groupby('block'):
  summary=dict(n_raw=int(g.n_raw.sum()),n_sessions=len(g),n_transitions=int(g.n.sum()),max_rho=float(g.rho.max()))
  for key in ['Q','S']:
   values=g[key].to_numpy();mean=float(values.mean());half=float(stats.t.ppf(.975,9)*values.std(ddof=1)/np.sqrt(10));summary[key]=dict(mean=mean,date_t95=[mean-half,mean+half])
  summaries[str(block)]=summary
 out=dict(status='FULL_COVERAGE_FIVE_PRICE_BLOCK_DIAGNOSTIC_NOT_COMPANY_AUTHENTICATION',protocol=protocol,source_events=sum(r['source_states'] for r in coverage),retained_events=int(f.n_raw.sum()),retained_sessions=len(f),fitted_transitions=int(f.n.sum()),coverage=coverage,rows=rows,by_block=summaries,limits=['Same independently retrieved normalized benchmark files, not a new market dataset.','Inferred anonymous price-gap blocks and per-block decimal conversion; not verified stock identities or physical flow/currency units.','Retrospective ten-day references are not causal or guaranteed serial confidence coverage.'])
 assert out['source_events']==out['retained_events']==394337 and len(f)==50
 (HERE/'equity_source_sensitivity.json').write_text(json.dumps(out,indent=2)+'\n');f.to_csv(HERE/'equity_source_sensitivity_rows.csv',index=False)
 print(json.dumps({k:v for k,v in out.items() if k in ['status','source_events','retained_sessions','fitted_transitions','by_block']},indent=2),flush=True)
if __name__=='__main__':run()
