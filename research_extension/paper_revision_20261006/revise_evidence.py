"""Read-only reanalysis of existing inputs; writes only this revision's outputs.

No downloads, training, or modifications of historical result files. The Binance
panel is reanalysed from saved estimates, not claimed to be raw-data reproduced.
"""
from pathlib import Path
import hashlib
import json
import sys
import numpy as np
import pandas as pd
from scipy import stats

ROOT = Path(__file__).resolve().parents[2]
REV = Path(__file__).resolve().parent
OUT = REV / 'results'
sys.path.insert(0, str(ROOT))
from empirical_pipeline.feedback_var import var1, q_long_memory_robust


def digest(path):
    h = hashlib.sha256()
    with open(path, 'rb') as fh:
        for chunk in iter(lambda: fh.read(1024 * 1024), b''):
            h.update(chunk)
    return h.hexdigest()


def series(frame, delta=10, window=300):
    """End-bin price/observed flow. Separate gaps; never insert future prices."""
    f = frame.copy()
    f['bin'] = f.sec // delta
    g = f.groupby('bin').agg(price=('mid', 'last'), flow=('flow', 'sum')).reset_index()
    g['segment'] = g.bin.diff().ne(1).cumsum()
    chunks = []
    for _, s in g.groupby('segment'):
        s = s.copy()
        p = np.log(s.price.to_numpy()) * 1e4
        ema = pd.Series(p).ewm(alpha=2 / (window / delta + 1), adjust=False).mean().to_numpy()
        s['x'] = p - ema
        s['return'] = np.r_[np.nan, np.diff(p)]
        s = s.iloc[int(5 * window / delta):].copy()
        chunks.append(s)
    if not chunks:
        return pd.DataFrame()
    out = pd.concat(chunks)
    out['day'] = pd.to_datetime(out.bin * delta, unit='s', utc=True).dt.floor('D')
    return out


def fit_segments(frame, state='x', alignment='observed'):
    # Fit day segments independently, retaining elapsed-time continuity.
    rows = []
    for (day, segment), s in frame.groupby(['day', 'segment']):
        if len(s) < 500:
            continue
        x = s[state].to_numpy()
        f = s.flow.to_numpy()
        if alignment == 'forward':
            x, f = x[:-1], f[1:]
        good = np.isfinite(x) & np.isfinite(f)
        if not good.all():
            x, f = x[good], f[good]
        e = var1(x, f)
        e['Q30'] = q_long_memory_robust(x, f, 30)['Q_L']
        e['date'] = str(day.date())
        e['alignment'] = alignment
        e['state'] = state
        rows.append(e)
    return rows


def summary(rows, metric_keys=('Q','S','rho','Q30')):
    # A timestamp gap can split one day into multiple segments. These are not
    # independent days; combine segment estimates within each day first.
    df = pd.DataFrame(rows)
    daily = df.groupby('date').apply(lambda g: pd.Series({k: np.average(g[k], weights=g['n'])
                                                       for k in metric_keys}))
    out = {'n_days': len(daily), 'n_segments':len(rows), 'n_transitions': sum(r['n'] for r in rows)}
    for key in metric_keys:
        v = daily[key].to_numpy()
        se = stats.sem(v)
        q = stats.t.ppf(.975, len(v) - 1)
        out[key] = {'mean': float(v.mean()), 'ci95': [float(v.mean()-q*se), float(v.mean()+q*se)]}
    out['share_Q_positive'] = float(np.mean(daily.Q > 0))
    out['max_rho'] = float(max(r['rho'] for r in rows))
    return out


def panel_audit():
    p = ROOT / 'results/provenance/binance_panel_results.json'
    df = pd.DataFrame(json.loads(p.read_text())['results'])
    assert not df.duplicated(['symbol', 'date']).any()
    errors = []
    for r in df.to_dict('records'):
        j = np.array([[r['J11'], r['J12']], [r['J21'], r['J22']]])
        q = j[0,1]*j[1,0]/(1-j[1,1])
        errors.append(max(abs(q-r['Q']), abs(j[0,0]+q-r['S']),
                          abs(max(abs(np.linalg.eigvals(j)))-r['rho'])))
    # Date-level mean treats correlated assets on a date as a block.
    means = df.groupby('date')[['Q','S','Q30']].mean()
    pooled = {k: {'mean': float(means[k].mean()),
                 'ci95_date_block': [float(means[k].mean()-stats.t.ppf(.975,len(means)-1)*stats.sem(means[k])),
                                     float(means[k].mean()+stats.t.ppf(.975,len(means)-1)*stats.sem(means[k]))]}
              for k in means}
    return df, {'input_sha256':digest(p), 'status':'saved-derived-panel only; original 2021–2024 raw lineage not independently reproduced; other dated archives were located during the expanded search',
                'n_asset_days':len(df),'n_dates':len(means),'n_fitted_states':int(df.n_obs.sum()),
                'max_identity_error':float(max(errors)), 'pooled':pooled,
                'share_Q_positive':float((df.Q>0).mean()),'max_rho':float(df.rho.max()),
                'by_asset':df.groupby('symbol')[['Q','S','Q30']].mean().to_dict('index')}


def ols(y, X, groups=None):
    n,k=X.shape
    inv=np.linalg.pinv(X.T@X)
    b=np.linalg.lstsq(X,y,rcond=None)[0]
    e=y-X@b
    if groups is None:
        cov=(e@e)/(n-k)*inv
        dof=n-k
    else:
        unique=np.unique(groups)
        scores=np.array([X[groups==g].T@e[groups==g] for g in unique])
        cov=inv@(scores.T@scores)@inv*len(unique)/(len(unique)-1)*(n-1)/(n-k)
        dof=len(unique)-1
    se=np.sqrt(np.maximum(0,np.diag(cov)))
    return b,se,dof,cov


def intervention(df):
    d=df[df.year==2022].sort_values(['date','symbol']).copy()
    post=(d.date>='2022-07-08').to_numpy(float)
    treat=(d.symbol=='BTCUSDT').to_numpy(float)
    X=np.column_stack([np.ones(len(d)),treat,post,treat*post])
    out={'n':len(d),'claim_scope':'association in saved legacy forward-flow panel; no random treatment assignment'}
    for dep in ['Q','S']:
        fits={}
        for kind,groups in [('classical',None),('asset_cluster',d.symbol.to_numpy()),('date_cluster',d.date.to_numpy())]:
            b,se,nu,cov=ols(d[dep].to_numpy(),X,groups)
            crit=stats.t.ppf(.975,nu)
            fits[kind]={'beta':float(b[3]),'se':float(se[3]),'df':nu,
                        'p_t':float(2*stats.t.sf(abs(b[3]/se[3]),nu)),
                        'ci95':[float(b[3]-crit*se[3]),float(b[3]+crit*se[3])],
                        'coefficients':b.tolist(),'standard_errors':se.tolist()}
        placebo=[]
        for sym in sorted(d.symbol.unique()):
            tr=(d.symbol==sym).to_numpy(float)
            bp=ols(d[dep].to_numpy(),np.column_stack([np.ones(len(d)),tr,post,tr*post]))[0][3]
            placebo.append({'asset':sym,'beta':float(bp)})
        actual=fits['classical']['beta']
        fits['placebo_rank_fraction']=float(np.mean([abs(r['beta'])>=abs(actual)-1e-12 for r in placebo]))
        fits['placebos']=placebo
        out[dep]=fits
    beta=out['Q']['date_cluster']['beta'];se=out['Q']['date_cluster']['se'];nu=out['Q']['date_cluster']['df']
    out['Q']['equivalence_date_cluster']={'margin':.007,'p_tost':float(max(stats.t.sf((beta+.007)/se,nu),stats.t.sf((.007-beta)/se,nu)))}
    # Date-specific gaps are descriptive; do not borrow one global SE for all dates.
    pivot=d.pivot(index='date',columns='symbol',values='Q')
    gap=pivot.BTCUSDT-pivot.drop(columns='BTCUSDT').mean(axis=1)
    base='2022-06-24'
    event=pd.DataFrame({'date':gap.index,'relative_gap_Q':(gap-gap.loc[base]).to_numpy()})
    event.to_csv(OUT/'event_gaps_descriptive.csv',index=False)
    out['event_study_status']='date-specific gaps only; old month coefficients/F-tests not traced to fitted output and withdrawn'
    return out


def empirical():
    result={}
    day_rows=[]
    for asset in ['BTC','ETH','ADA']:
        p=ROOT/'empirical_pipeline/cache'/f'{asset}_1sec_core_v2dedup.pkl'
        frame=pd.read_pickle(p)
        s=series(frame)
        variants={}
        for state,alignment in [('x','observed'),('x','forward'),('return','observed')]:
            rows=fit_segments(s,state,alignment)
            variants[f'{state}_{alignment}']=summary(rows)
            day_rows.extend([dict(asset=asset,**r) for r in rows])
        result[asset]={'input_sha256':digest(p),'first_utc':str(pd.to_datetime(frame.sec.min(),unit='s',utc=True)),
                       'last_utc':str(pd.to_datetime(frame.sec.max(),unit='s',utc=True)),
                       'variants':variants}
    pd.DataFrame(day_rows).to_csv(OUT/'coinbase_daily_estimates.csv',index=False)
    return result


def mechanical_nulls(reps=60,n=6000,seed=20261006):
    result={'repetitions':reps,'raw_seconds':n,'delta_seconds':10,'ema_seconds':300,'seed':seed,'cases':{}}
    for case in ['martingale_independent_flow','persistent_exogenous_flow','order_splitting_with_impact','common_news']:
        rows={k:[] for k in ['observed','forward']}
        rng=np.random.default_rng(seed+len(result['cases']))
        for _ in range(reps):
            e=rng.normal(size=n);u=rng.normal(size=n)
            flow=u.copy()
            if case in ['persistent_exogenous_flow','order_splitting_with_impact']:
                for t in range(1,n):flow[t]=.96*flow[t-1]+.28*u[t]
            elif case=='common_news':
                flow=.7*e+np.sqrt(1-.7**2)*u
            # No price->flow dependence in any case.
            increments=.0001*e + (.00005*flow if case=='order_splitting_with_impact' else 0)
            price=np.exp(np.cumsum(increments))
            s=series(pd.DataFrame({'sec':np.arange(n),'mid':price,'flow':flow}))
            for alignment in rows:
                x=s.x.to_numpy();f=s.flow.to_numpy()
                if alignment=='forward':x,f=x[:-1],f[1:]
                est=var1(x,f)
                rows[alignment].append(est['Q'])
        result['cases'][case]={a:{'mean_Q':float(np.mean(v)),'sd_Q':float(np.std(v,ddof=1)),
                                'range_Q':[float(np.min(v)),float(np.max(v))],
                                'share_Q_positive':float(np.mean(np.array(v)>0))} for a,v in rows.items()}
    return result


def equity():
    path=ROOT/'empirical_pipeline/fi2010/data/data.csv'
    cols=['STOCK','DAY','PRICE_ASK_0','PRICE_BID_0','VOLUME_ASK_0','VOLUME_BID_0']
    d=pd.read_csv(path,usecols=cols)
    rows=[]
    for (stock,day),g in d.groupby(['STOCK','DAY'],sort=True):
        if len(g)<600:continue
        bp=g.PRICE_BID_0.to_numpy();ap=g.PRICE_ASK_0.to_numpy()
        bs=g.VOLUME_BID_0.to_numpy();az=g.VOLUME_ASK_0.to_numpy()
        bid=np.where(bp[1:]>bp[:-1],bs[1:],np.where(bp[1:]==bp[:-1],bs[1:]-bs[:-1],-bs[:-1]))
        ask=np.where(ap[1:]<ap[:-1],az[1:],np.where(ap[1:]==ap[:-1],az[1:]-az[:-1],-az[:-1]))
        f=np.r_[0,bid-ask]
        mid=(bp+ap)/2
        if np.any(mid<=0):continue
        x=np.log(mid)*1e4
        x=x-pd.Series(x).ewm(span=100,adjust=False).mean().to_numpy()
        e=var1(x[500:],f[500:])
        rows.append(dict(stock=int(stock),day=int(day),raw_rows=len(g),**e))
    pd.DataFrame(rows).to_csv(OUT/'equity_session_estimates.csv',index=False)
    # Stock identification is only as trustworthy as the supplied STOCK/DAY metadata.
    out={'input_sha256':digest(path),'n_rows':len(d),'stock_counts':{str(k):int(v) for k,v in d.groupby('STOCK').size().items()},
         'scope':'event-indexed snapshots; supplied STOCK/DAY identifiers, no independently authenticated original identifier map',
         'per_stock':{}}
    for st in sorted(d.STOCK.unique()):
        rs=[r for r in rows if r['stock']==st]
        out['per_stock'][str(st)]={'n_sessions':len(rs),'Q_mean':float(np.mean([r['Q'] for r in rs])),
                                'S_mean':float(np.mean([r['S'] for r in rs])),
                                'max_rho':float(max(r['rho'] for r in rs))}
    return out


def main():
    OUT.mkdir(exist_ok=True)
    df,audit=panel_audit()
    products={'saved_panel_audit':audit,'fee_reanalysis':intervention(df)}
    for name,result in products.items():
        (OUT/f'{name}.json').write_text(json.dumps(result,indent=2)+'\n')
        print(name,'written',flush=True)
    for name,fun in [('coinbase_reanalysis',empirical),('mechanical_nulls',mechanical_nulls),('equity_reanalysis',equity)]:
        result=fun();(OUT/f'{name}.json').write_text(json.dumps(result,indent=2)+'\n');print(name,'written',flush=True)


if __name__=='__main__':
    main()
