"""Calendar-aware HAC sensitivity for the existing original-panel date means.

Retrospective reference intervals under additional mixing/stationarity conditions;
neither a randomized-sample certificate nor a causal learning estimator.
"""
from pathlib import Path
import json
import numpy as np
import pandas as pd
from scipy import stats
HERE=Path(__file__).resolve().parent
def run():
 rows=json.loads((HERE.parent/'cross_venue/original_panel_reproduction.json').read_text())['rows'];result=[]
 for var in ['legacy','observed','raw_return']:
  metrics=['Q','S']+(['Q30'] if var!='raw_return' else [])
  frame=pd.DataFrame([dict(date=r['date'],**{m:r[var][m] for m in metrics}) for r in rows]);d=frame.groupby('date')[metrics].mean().sort_index()
  dates=pd.to_datetime(d.index).to_numpy(dtype='datetime64[D]').astype(int);dist=abs(dates[:,None]-dates[None,:]);n=len(d)
  for metric in metrics:
   y=d[metric].to_numpy();e=y-y.mean()
   for days in [30,90,180,365]:
    weights=np.maximum(0,1-dist/days);mineig=float(np.linalg.eigvalsh(weights).min());assert mineig>-1e-10
    variance=float(e@weights@e/(n*(n-1)));se=np.sqrt(variance);half=stats.norm.ppf(.975)*se
    result.append(dict(variant=var,metric=metric,n_dates=n,calendar_bandwidth_days=days,mean=float(y.mean()),se=float(se),normal_reference_interval=[float(y.mean()-half),float(y.mean()+half)],kernel_min_eigenvalue=mineig))
 out=dict(scope='Calendar Bartlett HAC sensitivity for declared equal-weight date means. Gaussian reference, additional mixing/stationarity requirements, retrospective bandwidth grid; no causal or finite-sample coverage certificate.',rows=result)
 (HERE/'calendar_inference_sensitivity.json').write_text(json.dumps(out,indent=2)+'\n')
 print('Calendar-aware covariance sensitivity complete:',len(result),'references')
 print([(r['variant'],r['calendar_bandwidth_days'],r['normal_reference_interval']) for r in result if r['metric']=='Q'])
if __name__=='__main__':run()
