"""Independent QR refits and all chronological test predictions on saved states."""
from pathlib import Path
import hashlib,json
import numpy as np
from scipy import linalg,stats
HERE=Path(__file__).resolve().parent
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def run():
 result=HERE/'january_forecast_results.json';d=json.loads(result.read_text());mp=HERE/'january_forecast_segments.json';meta=json.loads(mp.read_text());cache=Path(meta['cache_path'])
 assert sha(cache)==meta['cache_sha256'] and sha(mp)==d['segment_manifest_sha256']
 with np.load(cache) as saved:chunks=[dict(m,z=saved[m['key']]) for m in meta['segments']]
 assert sum(len(c['z'])-1 for c in chunks)==d['baseline_var1_transitions']==844621
 def design(items,p,mean,scale):
  xx=[];yy=[]
  for c in items:
   z=(c['z']-mean)/scale;n=len(z);idx=np.arange(6,n)
   xx.append(np.column_stack([np.ones(len(idx))]+[z[idx-lag] for lag in range(1,p+1)]));yy.append(z[idx])
  return np.concatenate(xx),np.concatenate(yy)
 maximum=0
 for day in d['dates'][6:]:
  training=[c for c in chunks if c['date']<day];testing=[c for c in chunks if c['date']==day]
  z=np.concatenate([c['z'] for c in training]);mean=z.mean(0);scale=z.std(0)
  for p in [1,2,3,6]:
   X,Y=design(training,p,mean,scale);Xt,Yt=design(testing,p,mean,scale)
   for kind in ['AR','VAR']:
    B=np.zeros((X.shape[1],2))
    if kind=='VAR':B=linalg.lstsq(X,Y,lapack_driver='gelsy')[0]
    else:
     for j in range(2):
      cols=[0]+[1+j+2*k for k in range(p)];B[cols,j]=linalg.lstsq(X[:,cols],Y[:,j],lapack_driver='gelsy')[0]
    stored=next(r for r in d['folds'] if r['test_date']==day and r['model']==kind+str(p))
    assert stored['train_last_date']<day and stored['n_train']==len(Y) and stored['n_test']==len(Yt)
    np.testing.assert_allclose(stored['mean'],mean,rtol=1e-10);np.testing.assert_allclose(stored['scale'],scale,rtol=1e-10)
    np.testing.assert_allclose(stored['B'],B,rtol=1e-8,atol=1e-10)
    mse=np.mean((Yt-Xt@B)**2,0);np.testing.assert_allclose(stored['MSE_train_scale'],mse,rtol=1e-9)
    maximum=max(maximum,float(np.max(np.abs(mse-stored['MSE_train_scale']))))
 for lag,ref in d['summary']['paired'].items():
  for j,name in enumerate(['price','flow']):
   values=[]
   for day in d['dates'][6:]:
    losses={r['model']:r['MSE_train_scale'][j] for r in d['folds'] if r['test_date']==day};values.append(losses['AR'+lag]-losses['VAR'+lag])
   mean=np.mean(values);half=stats.t.ppf(.975,5)*np.std(values,ddof=1)/np.sqrt(6)
   np.testing.assert_allclose(ref['variables'][name]['AR_minus_VAR_mean_loss'],mean)
   np.testing.assert_allclose(ref['variables'][name]['date_t95'],[mean-half,mean+half])
 out=dict(status='ALL_48_FORECASTS_INDEPENDENTLY_QR_REFIT_AND_SCORED',result_sha256=sha(result),cache_sha256=sha(cache),folds_checked=48,max_mse_error=maximum,limits=['Existing sample, six serial dates, fixed retrospective lag grid; Student reference is not guaranteed confidence coverage or causal learning identification.','Reconstructed states and fit arithmetic do not supply undocumented exchange/contract metadata.'])
 (HERE/'january_forecast_verification.json').write_text(json.dumps(out,indent=2)+'\n');print(out['status'],maximum)
if __name__=='__main__':run()
