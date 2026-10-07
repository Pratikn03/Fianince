"""Stream the existing January depth file, retaining chunk-boundary OFI."""
import json
from pathlib import Path
import numpy as np
import pandas as pd
from revise_evidence import digest, summary
from empirical_pipeline.feedback_var import var1, q_long_memory_robust

REV=Path(__file__).resolve().parent
ROOT=REV.parents[1]


def quote_ofi(bp,bs,ap,az,previous=None):
    """Price-aware top-quote updates, including a carried chunk predecessor."""
    pbp,pbs,pap,paz=[np.roll(v,1) for v in [bp,bs,ap,az]]
    if previous is None:pbp[0],pbs[0],pap[0],paz[0]=bp[0],bs[0],ap[0],az[0]
    else:pbp[0],pbs[0],pap[0],paz[0]=previous
    bid=np.where(bp>pbp,bs,np.where(bp==pbp,bs-pbs,-pbs))
    ask=np.where(ap<pap,az,np.where(ap==pap,az-paz,-paz))
    return bid-ask,(bp[-1],bs[-1],ap[-1],az[-1])


def run():
    path=ROOT/'empirical_pipeline/data/1-09-1-20.csv'
    blocks=[];previous=None;n_raw=0;first_ms=None;last_ms=None
    for c in pd.read_csv(path,header=0,usecols=[1,3,4,23,24],chunksize=250000):
        c.columns=['ms','bp','bs','ap','az'];n_raw+=len(c)
        first_ms=int(c.ms.iloc[0]) if first_ms is None else first_ms
        last_ms=int(c.ms.iloc[-1])
        bp,bs,ap,az=[c[k].to_numpy(float) for k in ['bp','bs','ap','az']]
        ofi,previous=quote_ofi(bp,bs,ap,az,previous)
        t=pd.DataFrame({'sec':c.ms.to_numpy(np.int64)//1000,'price':(bp+ap)/2,'flow':ofi})
        t=t[(t.price>0)&(bp<=ap)]
        blocks.append(t.groupby('sec').agg(price=('price','last'),flow=('flow','sum')).reset_index())
    panel=pd.concat(blocks).groupby('sec').agg(price=('price','last'),flow=('flow','sum')).reset_index().sort_values('sec')
    panel['segment']=panel.sec.diff().ne(1).cumsum()
    chunks=[]
    for _,s in panel.groupby('segment'):
        s=s.copy();p=np.log(s.price.to_numpy())*1e4
        s['x']=p-pd.Series(p).ewm(span=120,adjust=False).mean().to_numpy()
        chunks.append(s.iloc[600:])
    panel=pd.concat(chunks);panel['day']=pd.to_datetime(panel.sec,unit='s',utc=True).dt.floor('D')
    rows=[]
    for (day,segment),g in panel.groupby(['day','segment']):
        if len(g)<500:continue
        e=var1(g.x.to_numpy(),g.flow.to_numpy());e['Q30']=q_long_memory_robust(g.x.to_numpy(),g.flow.to_numpy(),30)['Q_L']
        rows.append(dict(date=str(day.date()),**e))
    pd.DataFrame(rows).to_csv(REV/'results/depth_daily_estimates.csv',index=False)
    out={'input_sha256':digest(path),'n_raw':n_raw,'first_utc':str(pd.to_datetime(first_ms,unit='ms',utc=True)),
         'last_utc':str(pd.to_datetime(last_ms,unit='ms',utc=True)),
         'summary':summary(rows),'delta_seconds':1,'ema_seconds':120,
         'scope':'recorded BTC depth sample, provider attribution not independently authenticated; quote OFI rather than executed flow; secondary previously examined sample, not untouched holdout'}
    (REV/'results/depth_reanalysis.json').write_text(json.dumps(out,indent=2)+'\n')
    print(out,flush=True)


if __name__=='__main__':run()
