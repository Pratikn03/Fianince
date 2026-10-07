"""Compare restored original-day inputs to saved estimates, independently."""
from pathlib import Path
import json,zipfile
import numpy as np
import pandas as pd
HERE=Path(__file__).resolve().parent;ROOT=HERE.parents[2]
manifest=json.loads((HERE/'restoration_manifest.json').read_text())
legacy=json.loads((ROOT/'results/provenance/binance_panel_results.json').read_text())['results']
lookup={(r['symbol'],r['date']):r for r in legacy};results=[]
for r in manifest['rows']:
 key=(r['symbol'],r['date'])
 if key not in lookup:continue
 with zipfile.ZipFile(r['path']) as z:
  with z.open(z.namelist()[0]) as f:raw=pd.read_csv(f,header=None)
 b=raw[0].to_numpy(np.int64)//1000//10
 frame=pd.DataFrame({'b':b,'p':raw[4].to_numpy(float),'f':(2*raw[10]-raw[7]).to_numpy(float)})
 g=frame.groupby('b').agg(p=('p','last'),f=('f','sum'))
 price=np.log(g.p.to_numpy())*10000
 x=price-pd.Series(price).ewm(alpha=2/31,adjust=False).mean().to_numpy()
 flow=g.f.to_numpy()
 Z=np.column_stack([x[150:-1],flow[151:]])
 X=np.column_stack([np.ones(len(Z)-1),Z[:-1]])
 J=np.linalg.lstsq(X,Z[1:],rcond=None)[0][1:].T
 Q=J[0,1]*J[1,0]/(1-J[1,1]);S=J[0,0]+Q;rho=max(abs(np.linalg.eigvals(J)))
 metrics={'J11':J[0,0],'J12':J[0,1],'J21':J[1,0],'J22':J[1,1],'Q':Q,'S':S,'rho':rho,'n_obs':len(Z),'mean_price':raw[4].mean()}
 old=lookup[key];errors={k:float(metrics[k]-old[k]) for k in metrics}
 results.append({'symbol':key[0],'date':key[1],'archive_sha256':r['sha256'],'metrics':{k:float(v) for k,v in metrics.items()},'saved_minus_recomputed_error':{k:-v for k,v in errors.items()},'all_baseline_metrics_match':all(np.isclose(metrics[k],old[k],atol=1e-10,rtol=1e-10) for k in metrics)})
(HERE/'legacy_overlap_reproduction.json').write_text(json.dumps({'scope':'Only three original-panel rows overlap the restored dates; this is not full 768-row raw reproduction; original download-time hashes were not archived','results':results},indent=2)+'\n')
print(json.dumps(results,indent=2))
