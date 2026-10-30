"""Optional observational forecast check; never a structural safety certificate."""
import hashlib
from pathlib import Path
import numpy as np
import pandas as pd


def features(frame):
    frame=frame.sort_values('timestamp').reset_index(drop=True)
    dt=pd.to_datetime(frame.timestamp,utc=True)
    seconds=dt.diff().dropna().dt.total_seconds().to_numpy()
    if not len(seconds) or not np.all(seconds==seconds[0]) or seconds[0] not in [60,300]:
        raise ValueError('each market needs strictly regular 1-minute or 5-minute rows; no silent filling')
    bar=int(seconds[0]/60);H=60//bar;L=360//bar
    p=frame.price.to_numpy(float);flow=frame.signed_flow.to_numpy(float)
    if (p<=0).any() or not np.isfinite(p).all() or not np.isfinite(flow).all():
        raise ValueError('invalid prices or flow')
    lp=np.log(p);ret=np.r_[0.,np.diff(lp)];out=[]
    for t in range(L,len(frame)-H,H):
        past=lp[t-L:t+1];f=flow[t-L+1:t+1];r=ret[t-L+1:t+1]
        centered=past-past.mean()
        ar=np.dot(centered[:-1],centered[1:])/max(np.dot(centered[:-1],centered[:-1]),1e-12)
        impact=np.dot(f,r)/max(np.dot(f,f),1e-12)
        out.append(dict(timestamp=str(dt.iloc[t]),row=t,target_end_row=t+H,bar_minutes=bar,
          vol_hour=float(np.std(r[-H:])),vol_six_hour=float(np.std(r)),
          abs_return_hour=abs(lp[t]-lp[t-H]),flow_imbalance=float(f.sum()/max(abs(f).sum(),1e-12)),
          persistence_proxy=float(np.clip(ar,-.999,.999)),impact_proxy=float(impact),
          target=float(np.max(abs(lp[t+1:t+H+1]-lp[t])))))
    return pd.DataFrame(out)


def evaluate(csv,out):
    raw=Path(csv).read_bytes();df=pd.read_csv(csv)
    required={'timestamp','market','price','signed_flow'}
    if not required.issubset(df):raise ValueError('CSV requires '+str(sorted(required)))
    df.timestamp=pd.to_datetime(df.timestamp,utc=True)
    if df.duplicated(['market','timestamp']).any():raise ValueError('duplicate timestamp')
    if df.timestamp.max()>pd.Timestamp.now(tz='UTC'):raise ValueError('future timestamp in market input')
    summaries=[];preds=[]
    for name,d in df.groupby('market'):
        f=features(d);n=len(f);i,j=int(.6*n),int(.8*n)
        # Forecasts are hourly/nonoverlapping; omit one complete target interval at each split.
        tr,va,te=f.iloc[:i-1],f.iloc[i:j-1],f.iloc[j:]
        if min(len(tr),len(va),len(te))<30:raise ValueError('need at least 30 hourly forecasts in each split')
        def fit(cols):
            X=tr[cols].to_numpy();lo,hi=np.quantile(X,[.01,.99],axis=0)
            mu=np.clip(X,lo,hi).mean(0);sd=np.clip(X,lo,hi).std(0);sd[sd<1e-12]=1
            def tx(d):return np.c_[np.ones(len(d)),(np.clip(d[cols],lo,hi)-mu)/sd]
            A,V,T=tx(tr),tx(va),tx(te);best=None
            for lam in [.001,.1,10,1000]:
                pen=np.eye(A.shape[1]);pen[0,0]=0
                b=np.linalg.solve(A.T@A+lam*pen,A.T@tr.target)
                loss=np.mean((V@b-va.target)**2)
                if best is None or loss<best[0]:best=(loss,b,lam)
            return T@best[1],best[2]
        cols=['vol_hour','vol_six_hour','abs_return_hour','flow_imbalance']
        base,bl=fit(cols);aug,al=fit(cols+['persistence_proxy','impact_proxy'])
        te=te.copy();te['market']=name;te['baseline_prediction']=base;te['augmented_prediction']=aug
        te['paired_squared_error_difference']=(base-te.target)**2-(aug-te.target)**2
        preds.append(te)
        summaries.append(dict(market=name,training_forecasts=len(tr),validation_forecasts=len(va),
          test_forecasts=len(te),baseline_ridge=bl,augmented_ridge=al,
          paired_mse_improvement=float(te.paired_squared_error_difference.mean()),
          interpretation='exploratory observational proxy check; no structural identification or account safety'))
    pd.DataFrame(summaries).to_csv(out/'market_summary.csv',index=False)
    pd.concat(preds).to_csv(out/'market_predictions.csv',index=False)
    return dict(status='COMPLETED_EXPLORATORY',input_sha256=hashlib.sha256(raw).hexdigest(),
                rows=len(df),markets=len(summaries),primary_ofi_benchmark='NOT_AVAILABLE_WITH_REQUIRED_MINIMAL_COLUMNS',
                source_and_prior_sample_use='AUTHOR_MUST_DOCUMENT_SEPARATELY')
