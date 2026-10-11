"""Retrospective fixed-lag forecasts on the existing authenticated January CSV.

Retains the existing gap EMA, burn, date/session and quote-OFI construction.
The protocol is written before outcomes are computed; this is not preregistration.
"""
from pathlib import Path
import sys,json,hashlib,datetime
import numpy as np
import pandas as pd
HERE=Path(__file__).resolve().parent;ROOT=HERE.parents[2];BASE=HERE.parent
sys.path.insert(0,str(ROOT));sys.path.insert(0,str(ROOT/'research_extension/paper_revision_20261006'))
sys.path.insert(0,str(BASE/'model_diagnostics'))
from holdout_reanalysis import quote_ofi
from predictive_diagnostics import fit,predict,summarize
from empirical_pipeline.feedback_var import var1
def sha(p):
 h=hashlib.sha256()
 with p.open('rb') as stream:
  for block in iter(lambda:stream.read(8*1024*1024),b''):h.update(block)
 return h.hexdigest()
def run():
 path=ROOT/'empirical_pipeline/data/1-09-1-20.csv'
 protocol=dict(written_utc=datetime.datetime.now(datetime.timezone.utc).isoformat(),status='RETROSPECTIVE_FIXED_EXISTING_SAMPLE_PROTOCOL_NOT_PREREGISTRATION',lags_seconds=[1,2,3,6],common_max_lag_seconds=6,initial_train_dates=6,ema_span_seconds=120,gap_burn_seconds=600,min_date_segment_states=500,flow='Top quote OFI carried across CSV chunks; positive/noncrossed prices; last price and summed flow in occupied seconds; no gap filling',date_rule='Regression lags split by UTC date and gap; EMA resets by gap and continues across contiguous dates',reference='Equal-date paired AR-minus-VAR loss; Student with five df for six consecutive dates; serial dependence and retrospective selection remain open',source_sha256=sha(path))
 (HERE/'january_forecast_protocol.json').write_text(json.dumps(protocol,indent=2)+'\n')
 assert protocol['source_sha256']==json.loads((HERE/'january_authentication.json').read_text())['local_csv_sha256']
 blocks=[];previous=None;raw=0
 for c in pd.read_csv(path,usecols=[1,3,4,23,24],chunksize=250000):
  c.columns=['ms','bp','bs','ap','az'];raw+=len(c)
  bp,bs,ap,az=[c[k].to_numpy(float) for k in ['bp','bs','ap','az']]
  ofi,previous=quote_ofi(bp,bs,ap,az,previous)
  f=pd.DataFrame(dict(sec=c.ms.to_numpy(np.int64)//1000,price=(bp+ap)/2,flow=ofi))
  f=f[(f.price>0)&(bp<=ap)]
  blocks.append(f.groupby('sec').agg(price=('price','last'),flow=('flow','sum')).reset_index())
  print('Read',raw,'snapshots',flush=True)
 panel=pd.concat(blocks).groupby('sec').agg(price=('price','last'),flow=('flow','sum')).reset_index().sort_values('sec')
 panel['segment']=panel.sec.diff().ne(1).cumsum();retained=[]
 for _,f in panel.groupby('segment'):
  f=f.copy();p=10000*np.log(f.price.to_numpy());f['x']=p-pd.Series(p).ewm(span=120,adjust=False).mean().to_numpy();retained.append(f.iloc[600:])
 panel=pd.concat(retained);panel['date']=pd.to_datetime(panel.sec,unit='s',utc=True).dt.strftime('%Y-%m-%d');chunks=[];saved=[];daily=[]
 for (date,segment),f in panel.groupby(['date','segment']):
  if len(f)<500:continue
  z=f[['x','flow']].to_numpy();chunks.append(dict(date=date,segment=int(segment),z=z));saved.append((date,int(segment),z))
  d=var1(z[:,0],z[:,1]);daily.append(dict(date=date,**d))
 existing=pd.read_csv(ROOT/'research_extension/paper_revision_20261006/results/depth_daily_estimates.csv')
 assert len(daily)==len(existing)==152
 for a,b in zip(daily,existing.to_dict('records')):
  assert a['date']==b['date'];np.testing.assert_allclose([a[k] for k in ['Q','S','rho','n']],[b[k] for k in ['Q','S','rho','n']],rtol=1e-8,atol=1e-10)
 data=Path('/Volumes/T9/machine_markets_data/january_forecast_20261008');data.mkdir(parents=True,exist_ok=True)
 cache=data/'january_segments.npz';np.savez_compressed(cache,**{f'z{i}':v[2] for i,v in enumerate(saved)})
 (HERE/'january_forecast_segments.json').write_text(json.dumps(dict(cache_path=str(cache),cache_sha256=sha(cache),segments=[dict(key=f'z{i}',date=d,segment=s,n_states=len(z)) for i,(d,s,z) in enumerate(saved)]),indent=2)+'\n')
 dates=sorted({c['date'] for c in chunks});folds=[]
 for i in range(6,len(dates)):
  training=[c for c in chunks if c['date']<dates[i]];testing=[c for c in chunks if c['date']==dates[i]]
  for lag in [1,2,3,6]:
   for kind in ['AR','VAR']:
    fitted=fit(training,lag,kind);score=predict(fitted,testing,lag)
    folds.append(dict(test_date=dates[i],train_last_date=dates[i-1],model=kind+str(lag),p=lag,n_train=fitted['n_train'],rho=fitted['rho'],condition=fitted['condition'],mean=fitted['mean'].tolist(),scale=fitted['scale'].tolist(),B=fitted['B'].tolist(),**score))
  print('Forecast date',dates[i],'complete',flush=True)
 out=dict(status='COMPLETED_EXISTING_SAMPLE_RETROSPECTIVE_FORECASTS',protocol=protocol,raw_snapshots=raw,eligible_segments=len(chunks),baseline_var1_transitions=sum(len(c['z'])-1 for c in chunks),dates=dates,folds=folds,summary=summarize(folds,['price','flow']),segment_manifest_sha256=sha(HERE/'january_forecast_segments.json'),limits=['Previously examined sample, six serial consecutive evaluation dates; no untouched holdout, prospective coverage or causal interpretation.','Quote-currency/exchange/contract metadata remain unauthenticated; state is log-price EMA and flow is quote OFI.'])
 (HERE/'january_forecast_results.json').write_text(json.dumps(out,indent=2)+'\n');print(json.dumps(out['summary']['paired'],indent=2),flush=True)
if __name__=='__main__':run()
