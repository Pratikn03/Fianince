"""Incremental raw reproduction for exactly the original 768 asset-days.
Legacy forward-flow estimates are reproduced, while corrected observed-flow and
raw-return estimates are calculated separately. Historical files are untouched.
"""
from pathlib import Path
import json,zipfile,hashlib,time
import numpy as np
import pandas as pd
HERE=Path(__file__).resolve().parent;ROOT=HERE.parents[2]

def fit_pair(x,flow):
    Z=np.column_stack([x,flow]);X=np.column_stack([np.ones(len(Z)-1),Z[:-1]])
    B=np.linalg.lstsq(X,Z[1:],rcond=None)[0];J=B[1:].T
    Q=J[0,1]*J[1,0]/(1-J[1,1]);S=J[0,0]+Q
    return {'J11':float(J[0,0]),'J12':float(J[0,1]),'J21':float(J[1,0]),'J22':float(J[1,1]),'Q':float(Q),'S':float(S),'rho':float(max(abs(np.linalg.eigvals(J)))),'n_states':len(Z),'n_transitions':len(Z)-1}

def controlled(x,f,L):
    n=len(x);rows=np.arange(L-1,n-1)
    X=np.column_stack([np.ones(len(rows)),x[rows]]+[f[rows-l] for l in range(L)])
    b=np.linalg.lstsq(X,f[rows+1],rcond=None)[0]
    return float(b[1]),float(b[2:].sum())

def process(r,old):
    p=Path(r['path']);h=hashlib.sha256(p.read_bytes()).hexdigest()
    if h!=r['sha256']:raise ValueError('Archive changed')
    with zipfile.ZipFile(p) as z:
        with z.open(z.namelist()[0]) as f:raw=pd.read_csv(f,header=None)
    sec=raw[0].to_numpy(np.int64)//1000;t0=int(pd.Timestamp(r['date'],tz='UTC').timestamp())
    if np.any(sec<t0) or np.any(sec>=t0+86400):raise ValueError('Archive rows outside named UTC day')
    observed_raw=pd.DataFrame({'sec':sec,'p':raw[4].to_numpy(float),'flow':(2*raw[10]-raw[7]).to_numpy(float)}).drop_duplicates('sec').sort_values('sec')
    duplicate_rows=len(raw)-len(observed_raw);missing_seconds=86400-len(observed_raw)
    duplicates=raw[raw.duplicated(0,keep=False)]
    duplicate_conflicts=int((duplicates.groupby(0).nunique().max(axis=1)>1).sum()) if len(duplicates) else 0
    # Preserve the old filling only for its explicit reproduction; primary fits below never fill.
    filled=observed_raw.set_index('sec').reindex(np.arange(t0,t0+86400))
    filled['p']=filled.p.ffill().bfill();filled['flow']=filled.flow.fillna(0.)
    filled['bin']=filled.index//10
    g=filled.groupby('bin').agg(p=('p','last'),flow=('flow','sum'))
    p_log=np.log(g.p.to_numpy())*10000
    state=p_log-pd.Series(p_log).ewm(alpha=2/31,adjust=False).mean().to_numpy()
    flow=g.flow.to_numpy();x=state[150:-1];f=flow[151:]
    legacy=fit_pair(x,f);legacy['n_obs']=legacy.pop('n_states');legacy['mean_price']=float(filled.p.mean())
    controls={}
    for L in [1,30,90]:
        c,phi=controlled(x,f,L);controls[f'c{L}']=c
        if L==30:controls['Q30']=legacy['J12']*c/(1-phi)
    legacy.update(controls)
    checked=[k for k in legacy if k in old];errors={k:float(legacy[k]-old[k]) for k in checked}
    match={k:bool(np.isclose(legacy[k],old[k],atol=1e-10,rtol=1e-10)) for k in checked}
    # Independent session/gap fits for corrected observables.
    observed_raw['bin']=observed_raw.sec//10
    bins=observed_raw.groupby('bin').agg(p=('p','last'),flow=('flow','sum'),count=('sec','nunique'))
    bins=bins[bins['count']==10].copy();bins['segment']=bins.index.to_series().diff().ne(1).cumsum().to_numpy()
    observed_segments=[];return_segments=[]
    for segment,g2 in bins.groupby('segment'):
        price=np.log(g2.p.to_numpy())*10000
        deviation=price-pd.Series(price).ewm(alpha=2/31,adjust=False).mean().to_numpy()
        if len(g2)-150<500:continue
        xv=deviation[150:];fv=g2.flow.to_numpy()[150:]
        obs=fit_pair(xv,fv);c30,phi=controlled(xv,fv,30);obs['Q30']=obs['J12']*c30/(1-phi);obs['segment']=int(segment)
        observed_segments.append(obs)
        ret=fit_pair(np.diff(price)[149:],fv);ret['segment']=int(segment);return_segments.append(ret)
    def aggregate(parts):
        if not parts:raise ValueError('No sufficiently long observed segment')
        weights=np.array([r['n_transitions'] for r in parts])
        out={k:float(np.average([r[k] for r in parts],weights=weights)) for k in ['Q','S']}
        if 'Q30' in parts[0]:out['Q30']=float(np.average([r['Q30'] for r in parts],weights=weights))
        out.update(n_states=sum(r['n_states'] for r in parts),n_transitions=int(weights.sum()),n_segments=len(parts),max_rho=max(r['rho'] for r in parts),segments=parts)
        return out
    return {'estimator_version':3,'symbol':r['symbol'],'date':r['date'],'year':int(r['date'][:4]),'archive_sha256':h,'raw_rows':len(raw),'unique_seconds':len(observed_raw),'missing_seconds':missing_seconds,'duplicate_seconds':duplicate_rows,'conflicting_duplicate_seconds':duplicate_conflicts,'duplicate_rule':'retain first row, as legacy; conflicting duplicates remain a measurement limitation','total_quote_volume_deduplicated':float(raw.loc[~pd.Series(sec).duplicated(),7].sum()),'total_quote_volume':float(raw[7].sum()),'taker_buy_quote_volume':float(raw[10].sum()),'taker_buy_quote_volume_deduplicated':float(raw.loc[~pd.Series(sec).duplicated(),10].sum()),'legacy':legacy,'legacy_errors':errors,'legacy_matches':match,'observed':aggregate(observed_segments),'raw_return':aggregate(return_segments),'status':'RAW_REPRODUCED' if all(match.values()) else 'LEGACY_DISCREPANCY'}

def run():
    manifest=json.loads((HERE/'original_panel_restoration_manifest.json').read_text())
    old=json.loads((ROOT/'results/provenance/binance_panel_results.json').read_text())['results'];lookup={(r['symbol'],r['date']):r for r in old}
    target=HERE/'original_panel_reproduction.json';results={}
    if target.is_file():results={(r['symbol'],r['date']):r for r in json.loads(target.read_text())['rows'] if r['status'] in ['RAW_REPRODUCED','LEGACY_DISCREPANCY'] and r.get('estimator_version')==3}
    selected=[r for r in manifest['rows'] if r['status']=='VERIFIED_ORIGINAL_SAMPLE_RESTORED'];start=time.time()
    for i,r in enumerate(selected):
        key=r['symbol'],r['date']
        if key in results and results[key]['archive_sha256']==r['sha256']:continue
        try:result=process(r,lookup[key])
        except Exception as e:result={'symbol':key[0],'date':key[1],'archive_sha256':r['sha256'],'status':'FAILED','error':f'{type(e).__name__}: {e}'}
        results[key]=result
        report={'scope':'Current official archive reconstruction of exactly the original saved-panel study units, not proof of unchanged historical archive bytes or structural identification','n_target':768,'n_available_at_start':len(selected),'n_processed':len(results),'rows':sorted(results.values(),key=lambda r:(r['symbol'],r['date']))}
        target.write_text(json.dumps(report,indent=2)+'\n')
        if len(results)%12==0 or result['status']!='RAW_REPRODUCED':print(f"Raw reproduction {len(results)}/768: {key} {result['status']}; elapsed {time.time()-start:.0f}s",flush=True)
    print('Current snapshot processed',len(results),'restoration snapshot',len(selected),flush=True)
if __name__=='__main__':run()
