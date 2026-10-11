"""Audit actual recorder-bin inclusion and compute strict completeness sensitivity."""
from pathlib import Path
import sys,json,hashlib
import pandas as pd
import numpy as np
from scipy import stats
HERE=Path(__file__).resolve().parent;ROOT=HERE.parents[2]
sys.path.insert(0,str(ROOT))
from empirical_pipeline.feedback_var import var1
def summarize(rows):
 f=pd.DataFrame(rows);q=np.array([np.average(g.Q,weights=g.n) for _,g in f.groupby('date')]);m=q.mean();h=stats.t.ppf(.975,len(q)-1)*stats.sem(q)
 return dict(n_dates=len(q),n_segments=len(f),n_transitions=int(f.n.sum()),mean_Q=float(m),date_reference_interval=[float(m-h),float(m+h)])
def run():
 out={};all_rows=[]
 for asset in ['BTC','ETH','ADA']:
  frame=pd.read_pickle(ROOT/'empirical_pipeline/cache'/f'{asset}_1sec_core_v2dedup.pkl');frame['bin']=frame.sec//10
  bins=frame.groupby('bin').agg(price=('mid','last'),flow=('flow','sum'),seconds=('sec','nunique'))
  counts=bins.seconds.value_counts().sort_index().to_dict();complete=bins[bins.seconds==10].copy();complete['segment']=complete.index.to_series().diff().ne(1).cumsum().to_numpy()
  blocks=[]
  for _,g in complete.groupby('segment'):
   g=g.copy();p=np.log(g.price.to_numpy())*1e4;g['x']=p-pd.Series(p).ewm(alpha=2/31,adjust=False).mean().to_numpy();g['return']=np.r_[np.nan,np.diff(p)];blocks.append(g.iloc[150:])
  strict=pd.concat(blocks);strict['day']=pd.to_datetime(strict.index.to_numpy()*10,unit='s',utc=True).floor('D')
  fits={}
  for state,alignment in [('x','observed'),('x','forward'),('return','observed')]:
   rows=[]
   for (day,segment),g in strict.groupby(['day','segment']):
    if len(g)<500:continue
    x=g[state].to_numpy();f=g.flow.to_numpy()
    if alignment=='forward':x,f=x[:-1],f[1:]
    r=var1(x,f);rows.append(dict(date=str(day.date()),**r))
   fits[state+'_'+alignment]=summarize(rows)
   all_rows.extend(dict(asset=asset,state=state,alignment=alignment,**r) for r in rows)
  out[asset]=dict(occupied_bins=len(bins),complete_bins=len(complete),partial_bins=int((bins.seconds<10).sum()),
                 occupied_second_histogram={str(k):int(v) for k,v in counts.items()},strict_variants=fits,
                 cache_sha256=hashlib.sha256((ROOT/'empirical_pipeline/cache'/f'{asset}_1sec_core_v2dedup.pkl').read_bytes()).hexdigest())
  print(asset,'partial bins',out[asset]['partial_bins'],'strict sensitivities complete',flush=True)
 report=dict(scope='Existing recorder baseline series() admits partially observed occupied bins and splits missing whole bins. Strict sensitivity requires ten observed seconds per bin, resets EMA across resulting gaps, continues across contiguous dates, burns150states and estimates date/gap groups>=500 states. Flow remains a constructed recorded feature; completeness does not authenticate an executed-volume window.',assets=out)
 (HERE/'recorder_bin_completeness.json').write_text(json.dumps(report,indent=2)+'\n')
 pd.DataFrame(all_rows).to_csv(HERE/'strict_recorder_segment_estimates.csv',index=False)
if __name__=='__main__':run()
