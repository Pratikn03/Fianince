"""Optional observational L1 quote-event evaluation. NOT a safety certificate."""
from pathlib import Path
import json,hashlib
import numpy as np
import pandas as pd

REQUIRED=['timestamp','market','bid','ask','bid_size','ask_size']
FEATURES={'EWMA':['ewma'], 'HAR_intraday':['rv5','rv30','rv120','clock_sin','clock_cos'],
 'OFI_depth':['rv5','rv30','rv120','ewma','abs_return','ofi_scaled','abs_ofi','log_depth','spread','imbalance','clock_sin','clock_cos']}
FEATURES['Response_augmented']=FEATURES['OFI_depth']+['response_score','var_radius']

def event_ofi(g):
    b=g.bid.to_numpy();a=g.ask.to_numpy();qb=g.bid_size.to_numpy();qa=g.ask_size.to_numpy()
    out=np.zeros(len(g))
    out[1:]=(b[1:]>=b[:-1])*qb[1:]-(b[1:]<=b[:-1])*qb[:-1]-(a[1:]<=a[:-1])*qa[1:]+(a[1:]>=a[:-1])*qa[:-1]
    return out

def read_events(csv,metadata):
    meta=json.loads(Path(metadata).read_text())
    if meta.get('data_kind')!='best_quote_events':raise ValueError('Complete event-level best-quote states are required; klines/snapshots are not OFI events')
    for key in ['source','venue','instrument_type','previous_use','fee_bps']:
        if key not in meta:raise ValueError('Missing metadata '+key)
    g=pd.read_csv(csv)
    if any(x not in g for x in REQUIRED):raise ValueError('Required CSV columns: '+','.join(REQUIRED))
    if pd.api.types.is_numeric_dtype(g.timestamp):raise ValueError('Use ISO-8601 timestamps with explicit timezone, not ambiguous numeric epochs')
    if not g.timestamp.astype(str).str.contains(r'Z|[+-]\d\d:\d\d$',regex=True).all():raise ValueError('Every timestamp must declare timezone')
    g['timestamp']=pd.to_datetime(g.timestamp,utc=True,errors='raise')
    if g[REQUIRED].isna().any().any():raise ValueError('Missing required quote values')
    for _,x in g.groupby('market',sort=False):
        if not x.timestamp.is_monotonic_increasing:raise ValueError('Quote rows must already be ordered; file order is preserved for ties')
        if x.timestamp.duplicated().any() and meta.get('tie_order')!='file_order':raise ValueError('Declare tie_order=file_order for equal-timestamp events')
    q=g[['bid','ask','bid_size','ask_size']].to_numpy(float)
    if not np.isfinite(q).all() or (q<=0).any() or (g.ask<g.bid).any():raise ValueError('Nonfinite, nonpositive or crossed quotes')
    if not np.isfinite(float(meta['fee_bps'])) or float(meta['fee_bps'])<0:raise ValueError('Finite nonnegative taker fee required')
    if not np.isfinite(float(meta.get('annual_carry',0))) or float(meta.get('annual_carry',0))<0:raise ValueError('Finite nonnegative carry required')
    return g,meta

def minute_features(events,H=60,var_window=180):
    chunks=[]
    for market,e in events.groupby('market',sort=False):
        e=e.copy();e['ofi']=event_ofi(e)
        b=e.set_index('timestamp').resample('1min',label='right',closed='left').agg({'bid':'last','ask':'last','bid_size':'last','ask_size':'last','ofi':'sum'}).dropna()
        b['market']=market;b['mid']=(b.bid+b.ask)/2
        b['segment']=(b.index.to_series().diff()!=pd.Timedelta(minutes=1)).cumsum().to_numpy()
        outputs=[]
        for _,s in b.groupby('segment',sort=False):
            s=s.copy();ret=np.log(s.mid).diff();s['abs_return']=ret.abs()
            s['ofi_scaled']=s.ofi/((s.bid_size+s.ask_size)/2)
            s['abs_ofi']=s.ofi_scaled.abs();s['log_depth']=np.log(s.bid_size+s.ask_size)
            s['spread']=(s.ask-s.bid)/s.mid;s['imbalance']=(s.bid_size-s.ask_size)/(s.bid_size+s.ask_size)
            for w in [5,30,120]:s[f'rv{w}']=ret.pow(2).rolling(w,min_periods=w).mean().pow(.5)
            s['ewma']=ret.pow(2).ewm(span=60,adjust=False,min_periods=60).mean().pow(.5)
            minute=s.index.hour*60+s.index.minute;s['clock_sin']=np.sin(2*np.pi*minute/1440);s['clock_cos']=np.cos(2*np.pi*minute/1440)
            X=np.column_stack([ret.to_numpy(),s.ofi_scaled.to_numpy()]);score=np.full(len(s),np.nan);radius=score.copy()
            last=(np.nan,np.nan)
            for i in range(var_window,len(s)):
                if (i-var_window)%30==0:
                    z=X[i-var_window:i+1]
                    if np.isfinite(z).all():
                        xx=np.column_stack([np.ones(len(z)-1),z[:-1]])
                        J=np.linalg.solve(xx.T@xx+np.diag([0.,1e-5,1e-5]),xx.T@z[1:])[1:].T
                        r=float(max(abs(np.linalg.eigvals(J))));v=np.array([0.,1.]);a=0.
                        for _ in range(H):a+=abs(v[0]);v=J@v
                        last=(min(float(a),1e6),r) if np.isfinite(a) else (np.nan,r)
                score[i],radius[i]=last
            s['response_score']=score;s['var_radius']=radius
            mx=s.mid.shift(-1).iloc[::-1].rolling(H,min_periods=H).max().iloc[::-1]
            mn=s.mid.shift(-1).iloc[::-1].rolling(H,min_periods=H).min().iloc[::-1]
            s['target']=np.maximum(np.log(mx/s.mid),np.log(s.mid/mn))
            s['future_min_bid']=s.bid.shift(-1).iloc[::-1].rolling(H,min_periods=H).min().iloc[::-1]
            s['exit_bid']=s.bid.shift(-H);s['label_end']=s.index+pd.Timedelta(minutes=H)
            outputs.append(s)
        if outputs:chunks.append(pd.concat(outputs))
    if not chunks:return pd.DataFrame()
    return pd.concat(chunks).reset_index().rename(columns={'index':'timestamp'})

def ridge_predict(train,val,test,columns,alpha):
    x=train[columns].to_numpy(float);mu=x.mean(0);sd=np.maximum(x.std(0),1e-10)
    a=np.column_stack([np.ones(len(x)),(x-mu)/sd]);y=np.log(np.maximum(train.target.to_numpy(),1e-10))
    penalty=np.eye(a.shape[1])*alpha;penalty[0,0]=0.
    w=np.linalg.solve(a.T@a+penalty+np.eye(a.shape[1])*1e-10,a.T@y)
    def pred(g):return np.exp(np.clip(np.column_stack([np.ones(len(g)),(g[columns].to_numpy()-mu)/sd])@w,-25,2))
    return pred(val),pred(test)

def split_masks(frame,val_start,test_start,test_end):
    tr=(frame.timestamp<val_start)&(frame.label_end<val_start)
    va=(frame.timestamp>=val_start)&(frame.timestamp<test_start)&(frame.label_end<test_start)
    te=(frame.timestamp>=test_start)&(frame.timestamp<test_end)
    return tr,va,te

def trade_account(row,units,fee_bps,annual_carry,H):
    fee=fee_bps/1e4;entry=units*row['ask']*(1+fee)
    carry=units*row['ask']*annual_carry*H/(365*1440)
    pnl=units*row['exit_bid']*(1-fee)-entry-carry
    worst=max(0.,entry+carry-units*row['future_min_bid']*(1-fee))
    return dict(net_pnl=float(pnl),sampled_max_loss=float(worst),entry_cash=float(entry+carry))

def evaluate(csv,metadata,out,H=60,bootstrap=2000):
    out=Path(out);out.mkdir(parents=True,exist_ok=True);events,meta=read_events(csv,metadata)
    frame=minute_features(events,H);status=dict(status='NOT_ENOUGH_DATA',formal_certificate=False,market_safety_proved=False,
        synthetic_fixture=bool(meta.get('synthetic',False)),metadata=meta,
        input_sha256=hashlib.sha256(Path(csv).read_bytes()).hexdigest(),H_minutes=H,
        score_definition='Past-only reduced-form return/flow VAR score, NOT the theorem impulse response',
        quote_limitations='Top-of-book prices, supplied fees/carry; no latency, queue fills, hidden liquidity or causal identification')
    if frame.empty:
        (out/'status.json').write_text(json.dumps(status,indent=2));return status
    common=sorted(set(sum(FEATURES.values(),[])))+['target','exit_bid','future_min_bid']
    frame=frame.dropna(subset=common);predictions=[];trades=[];folds=[]
    for market,g in frame.groupby('market'):
      g=g.sort_values('timestamp').reset_index(drop=True);n=len(g);initial=max(400,int(.5*n));vlen=max(2*H,int(.15*n));tlen=max(2*H,int(.15*n))
      for fold in range(5):
        v=initial+fold*tlen;tstart=v+vlen;tend=min(tstart+tlen,n)
        if tend-tstart<max(30,H) or tstart>=n:break
        vs=g.timestamp.iloc[v];ts=g.timestamp.iloc[tstart];end=g.timestamp.iloc[tend-1]+pd.Timedelta(minutes=1)
        tr,va,te=split_masks(g,vs,ts,end);train=g[tr];val=g[va];test=g[te]
        if len(train)<200 or len(val)<30 or len(test)<30:continue
        folds.append(dict(market=market,fold=fold,train=len(train),validation=len(val),test=len(test),train_label_end=str(train.label_end.max()),validation_start=str(vs),validation_label_end=str(val.label_end.max()),test_start=str(ts)))
        fit={}
        for name,cols in FEATURES.items():
            best=None
            for alpha in [.1,1.,10.,100.]:
                pv,pt=ridge_predict(train,val,test,cols,alpha);loss=float(np.mean((val.target-pv)**2))
                if best is None or loss<best[0]:best=(loss,alpha,pv,pt)
            _,alpha,pv,pt=best
            multiplier=float(np.quantile(val.target.to_numpy()/np.maximum(pv,1e-10),.95))
            fit[name]=(pv,pt,multiplier)
            for (_,row),prediction in zip(test.iterrows(),pt):
                predictions.append(dict(market=market,fold=fold,timestamp=str(row.timestamp),date=str(row.timestamp.date()),policy=name,target=row.target,prediction=float(prediction),training_mean=float(train.target.mean()),alpha=alpha))
        # Exposure replay is diagnostic, with NON-overlapping 60-minute entries.
        fee=float(meta['fee_bps']);carry=float(meta.get('annual_carry',0.));wealth=1000.;B=1.
        def units(data,pred,mul):
            price=data.ask.to_numpy();reserve=price*pred*mul+(data.ask-data.bid).to_numpy()+2*price*fee/1e4+price*carry*H/(365*1440)
            return np.minimum(np.minimum(B/np.maximum(reserve,1e-8),wealth/(price*(1+fee/1e4)+price*carry*H/(365*1440))),.1*np.minimum(data.ask_size,data.bid_size).to_numpy())
        val_units={name:units(val,pv,mul) for name,(pv,pt,mul) in fit.items()}
        val_means={name:float((x*val.ask.to_numpy()).mean()) for name,x in val_units.items()};target_notional=min(val_means.values())
        for name,(pv,pt,mul) in fit.items():
            ui=units(test,pt,mul);scale=min(1.,target_notional/max(val_means[name],1e-12))
            for mode,k in [('raw',1.),('matched_validation_notional',scale)]:
                for (_,row),I in zip(test.iterrows(),ui*k):
                    if int(row.timestamp.timestamp()//60)%H:continue
                    a=trade_account(row,float(I),fee,carry,H)
                    trades.append(dict(market=market,fold=fold,policy=name,mode=mode,timestamp=str(row.timestamp),holding_minutes=H,units=float(I),entry_notional=float(I*row.ask),validation_scale=k,**a))
    if not predictions:
        status['retained_common_rows']=len(frame);(out/'status.json').write_text(json.dumps(status,indent=2));return status
    p=pd.DataFrame(predictions);p.to_csv(out/'walk_forward_predictions.csv.gz',index=False,compression={'method':'gzip','mtime':0})
    pd.DataFrame(trades).to_csv(out/'isolated_round_trip_replay.csv',index=False);pd.DataFrame(folds).to_csv(out/'purged_fold_audit.csv',index=False)
    metrics=[]
    for name,g in p.groupby('policy'):
        sse=float(((g.target-g.prediction)**2).sum());den=float(((g.target-g.training_mean)**2).sum())
        metrics.append(dict(policy=name,observations=len(g),out_of_sample_R2=1-sse/max(den,1e-20),MAE=float(abs(g.target-g.prediction).mean())))
    pd.DataFrame(metrics).to_csv(out/'forecast_metrics.csv',index=False)
    base=p[p.policy=='OFI_depth'];new=p[p.policy=='Response_augmented'];a=base.merge(new,on=['market','fold','timestamp','date','target','training_mean'],suffixes=('_base','_new'),validate='one_to_one')
    a['improvement']=(a.target-a.prediction_base)**2-(a.target-a.prediction_new)**2;a['denominator']=(a.target-a.training_mean)**2
    daily=a.groupby('date')[['improvement','denominator']].sum();rng=np.random.default_rng(20261030);values=[]
    for _ in range(bootstrap):
        b=daily.iloc[rng.integers(0,len(daily),len(daily))].sum();values.append(b.improvement/max(b.denominator,1e-20))
    status.update(status='COMPLETED_SYNTHETIC_FIXTURE' if meta.get('synthetic') else 'COMPLETED_OBSERVATIONAL',
        folds=len(folds),test_rows=len(a),date_clusters=len(daily),delta_R2=float(a.improvement.sum()/max(a.denominator.sum(),1e-20)),
        date_bootstrap_interval=[float(np.quantile(values,.025)),float(np.quantile(values,.975))],
        interval_warning='Exploratory date-cluster bootstrap; very few dates do not establish reliable market evidence')
    (out/'status.json').write_text(json.dumps(status,indent=2)+'\n');return status
