"""Joint reduced-form VAR and FEVD from restored, checksum-verified study inputs.
No calls to the legacy pipeline's downloader and no overwrite of historical fits.
"""
from pathlib import Path
import hashlib,itertools,json,sys,zipfile
import numpy as np
import pandas as pd
HERE=Path(__file__).resolve().parent;ROOT=HERE.parents[2]
if not (ROOT/'empirical_pipeline').is_dir():ROOT=HERE.parents[3]
NAMES=['coinbase_price','coinbase_flow','binance_price','binance_flow']
DELTA=10;WINDOW=300;BURN=5*WINDOW//DELTA;HORIZONS=[1,3,6,10,30,60]

def digest(path):
    h=hashlib.sha256()
    with Path(path).open('rb') as f:
        for b in iter(lambda:f.read(1024*1024),b''):h.update(b)
    return h.hexdigest()

def bin_frame(frame,prefix,offset=0):
    f=frame.copy();f['bin']=(f.sec+offset)//DELTA
    b=f.groupby('bin',sort=True).agg(price=('mid','last'),flow=('flow','sum'),seconds=('sec','nunique'))
    # No filling; require all recorded integer seconds within each nominal bin.
    return b[b.seconds==DELTA][['price','flow']].rename(columns=lambda s:prefix+'_'+s)

def aligned_segments(cb,bn,state='ema',offset=0):
    joint=bin_frame(cb,'coinbase',offset).join(bin_frame(bn,'binance'),how='inner').reset_index()
    joint['day']=joint.bin*DELTA//86400
    joint['segment']=(joint.bin.diff().ne(1)|joint.day.ne(joint.day.shift())).cumsum()
    chunks=[];audit=[]
    for (day,segment),g in joint.groupby(['day','segment'],sort=True):
        g=g.copy()
        for venue in ['coinbase','binance']:
            p=np.log(g[venue+'_price'].to_numpy())*10000
            if state=='ema':v=p-pd.Series(p).ewm(alpha=2/(WINDOW/DELTA+1),adjust=False).mean().to_numpy()
            elif state=='return':v=np.r_[np.nan,np.diff(p)]
            else:raise ValueError('Unknown state')
            g[venue+'_price']=v
        retained=g.iloc[BURN:].copy()
        audit.append({'date':str(pd.Timestamp(day*86400,unit='s',tz='UTC').date()),'segment':int(segment),'complete_joined_bins':len(g),'retained_bins':len(retained),'included':len(retained)>=500})
        if len(retained)>=500:
            chunks.append({'date':audit[-1]['date'],'segment':int(segment),'bins':retained.bin.to_numpy(),'z':retained[NAMES].to_numpy(float)})
    return chunks,{'joined_complete_bins':len(joint),'segments':audit,'retained_segments':len(chunks),'n_transitions':sum(len(c['z'])-1 for c in chunks),'state':state,'coinbase_integer_second_offset':offset}

def fit_joint(chunks):
    if not chunks:raise ValueError('No eligible contiguous segments')
    z=np.vstack([c['z'] for c in chunks]);scale=z.std(axis=0)
    if np.any(scale<=0) or not np.all(np.isfinite(z)):raise ValueError('Degenerate/nonfinite data')
    centered=[];XX=np.zeros((4,4));XY=np.zeros((4,4));YY=np.zeros((4,4));n=0
    for c in chunks:
        raw=c['z']/scale;x=raw[:-1];y=raw[1:];mx=x.mean(0);my=y.mean(0);xc=x-mx;yc=y-my
        XX+=xc.T@xc;XY+=xc.T@yc;YY+=yc.T@yc;n+=len(x)
        centered.append((c,x,y,mx,my))
    if np.linalg.matrix_rank(XX)!=4:raise ValueError('Joint regressors rank deficient')
    B=np.linalg.solve(XX,XY);J=B.T;residuals=[];intercepts=[]
    for c,x,y,mx,my in centered:
        intercept=my-mx@B;e=y-intercept-x@B;residuals.append(e)
        intercepts.append({'date':c['date'],'segment':c['segment'],'normalized_intercept':intercept.tolist()})
    residual=np.vstack(residuals);df=n-4-len(chunks)
    if df<=0:raise ValueError('Insufficient residual degrees of freedom')
    sigma=residual.T@residual/df
    if min(np.linalg.eigvalsh(sigma))<=0:raise ValueError('Innovation covariance not positive definite')
    rawJ=scale[:,None]*J/scale[None,:];rawSigma=scale[:,None]*sigma*scale[None,:]
    eig=np.linalg.eigvals(J);radius=float(max(abs(eig)))
    return {'variables':NAMES,'n_transitions':n,'n_segments':len(chunks),'residual_df':df,'scale':scale.tolist(),'J_normalized':J.tolist(),'J_raw':rawJ.tolist(),'covariance_normalized':sigma.tolist(),'covariance_raw':rawSigma.tolist(),'eigenvalues':[{'real':float(v.real),'imaginary':float(v.imag)} for v in eig],'rho':radius,'Schur_stable':radius<1,'intercepts':intercepts,'residual_lag_correlations':residual_correlations(residuals)},residuals

def residual_correlations(groups):
    out={}
    for lag in [1,2,3,6]:
        left=np.vstack([e[:-lag] for e in groups if len(e)>lag]);right=np.vstack([e[lag:] for e in groups if len(e)>lag])
        out[str(lag)]=[float(np.corrcoef(left[:,j],right[:,j])[0,1]) for j in range(4)]
    return out

def generalized_fevd(J,sigma,horizon):
    if horizon<1:raise ValueError('Horizon must be positive')
    numer=np.zeros_like(sigma);denom=np.zeros(len(J));power=np.eye(len(J))
    for _ in range(horizon):
        transformed=power@sigma
        numer+=transformed**2/np.diag(sigma)[None,:]
        denom+=np.diag(transformed@power.T);power=J@power
    raw=numer/denom[:,None];normalized=raw/raw.sum(axis=1,keepdims=True)
    return raw,normalized

def orthogonal_fevd(J,sigma,horizon,order):
    order=np.array(order);j=J[np.ix_(order,order)];cov=sigma[np.ix_(order,order)];L=np.linalg.cholesky(cov)
    shares=np.zeros_like(cov);power=np.eye(len(J))
    for _ in range(horizon):
        shares+=(power@L)**2;power=j@power
    shares/=shares.sum(axis=1,keepdims=True)
    output=np.empty_like(shares);output[np.ix_(order,order)]=shares
    return output

def decompositions(fit):
    J=np.array(fit['J_normalized']);sigma=np.array(fit['covariance_normalized']);out={}
    for h in HORIZONS:
        raw,norm=generalized_fevd(J,sigma,h);orders=[]
        for order in itertools.permutations(range(4)):
            orders.append({'order':[NAMES[i] for i in order],'shares':orthogonal_fevd(J,sigma,h,order).tolist()})
        allshares=np.array([o['shares'] for o in orders])
        out[str(h)]={'steps':h,'seconds':h*DELTA,'generalized_raw':raw.tolist(),'generalized_row_normalized':norm.tolist(),'orthogonal_order_min':allshares.min(0).tolist(),'orthogonal_order_max':allshares.max(0).tolist(),'orthogonal_all_24_orders':orders}
    # Unit normalized innovation responses are reduced-form, not structural shocks.
    powers=[np.linalg.matrix_power(J,k).tolist() for k in range(max(HORIZONS)+1)]
    return {'horizons':out,'reduced_form_unit_innovation_responses':powers,'generalized_normalization':'Raw generalized shares need not sum to one with correlated residuals; report row-normalized shares and raw shares separately','interpretation':'Predictive decomposition, not causal information transmission; orthogonal results depend on ordering'}

def bootstrap_dates(chunks,repetitions=200,seed=20261006):
    rng=np.random.default_rng(seed);dates=sorted({c['date'] for c in chunks});rows=[]
    for b in range(repetitions):
        draw=rng.choice(dates,len(dates),replace=True);sample=[]
        for occurrence,date in enumerate(draw):
            for c in chunks:
                if c['date']==date:sample.append(dict(c,segment=occurrence*1000+c['segment']))
        fit,_=fit_joint(sample);J=np.array(fit['J_normalized']);sig=np.array(fit['covariance_normalized']);_,shares=generalized_fevd(J,sig,6)
        rows.append([fit['rho'],shares[0,2],shares[2,0]])
    values=np.array(rows)
    return {'n_dates':len(dates),'repetitions':repetitions,'seed':seed,'scope':'Exploratory date-resampling variability; assumes exchangeable date blocks and does not establish independence or causal uncertainty','rho_percentile95':np.quantile(values[:,0],[.025,.975]).tolist(),'bn_price_to_cb_price_60sec_percentile95':np.quantile(values[:,1],[.025,.975]).tolist(),'cb_price_to_bn_price_60sec_percentile95':np.quantile(values[:,2],[.025,.975]).tolist(),'draw_values':rows}

def read_binance(asset,manifest):
    frames=[];audit=[]
    for r in manifest['rows']:
        if r['symbol']!=asset+'USDT':continue
        p=Path(r['path'])
        if digest(p)!=r['sha256']:raise ValueError('Restored input changed')
        with zipfile.ZipFile(p) as z:
            with z.open(z.namelist()[0]) as f:d=pd.read_csv(f,header=None)
        if d.shape[1]!=12:raise ValueError('Unexpected kline schema')
        sec=(d[0].to_numpy(np.int64)//1000)
        expected=int(pd.Timestamp(r['date'],tz='UTC').timestamp())
        if len(d)!=86400 or not np.array_equal(sec,np.arange(expected,expected+86400)):raise ValueError('Missing/duplicate/nonconsecutive bars')
        if not np.all(d[6].to_numpy(np.int64)==d[0].to_numpy(np.int64)+999):raise ValueError('Unexpected availability clock')
        mid=d[4].to_numpy(float);flow=2*d[10].to_numpy(float)-d[7].to_numpy(float)
        if np.any(mid<=0) or np.any(d[10]<0) or np.any(d[10]>d[7]+1e-7):raise ValueError('Invalid price/buy-volume')
        frames.append(pd.DataFrame({'sec':sec,'mid':mid,'flow':flow}))
        audit.append({'date':r['date'],'rows':len(d),'price':'transaction close, not quote midpoint','flow':'2*taker_buy_quote_volume - total_quote_volume','interval':'[open_time, open_time+999ms]; information available at interval close','sha256':r['sha256']})
    return pd.concat(frames,ignore_index=True),audit

def run():
    manifest=json.loads((HERE/'restoration_manifest.json').read_text());results={};panels={};summaries=[]
    for asset in ['BTC','ETH','ADA']:
        bn,raw_audit=read_binance(asset,manifest)
        cb_path=ROOT/'empirical_pipeline/cache'/f'{asset}_1sec_core_v2dedup.pkl';cb=pd.read_pickle(cb_path)
        low=int(pd.Timestamp('2021-04-08',tz='UTC').timestamp());high=int(pd.Timestamp('2021-04-19',tz='UTC').timestamp());cb=cb[(cb.sec>=low)&(cb.sec<high)]
        variants={}
        for state,offset,key in [('ema',0,'primary'),('return',0,'raw_return'),('ema',-1,'cb_offset_minus1'),('ema',1,'cb_offset_plus1')]:
            chunks,join_audit=aligned_segments(cb,bn,state,offset);fit,_=fit_joint(chunks);decomp=decompositions(fit)
            result={'join':join_audit,'fit':fit,'decomposition':decomp}
            if key=='primary':
                result['date_bootstrap']=bootstrap_dates(chunks)
                table=[]
                for c in chunks:
                    for bin_,row in zip(c['bins'],c['z']):table.append([c['date'],c['segment'],int(bin_)]+row.tolist())
                path=HERE/f'{asset}_joint_panel.csv.gz';pd.DataFrame(table,columns=['date','segment','bin']+NAMES).to_csv(path,index=False,compression={'method':'gzip','mtime':0})
                result['panel_path']=str(path);result['panel_sha256']=digest(path)
            variants[key]=result
            print(asset,key,'n',fit['n_transitions'],'rho',fit['rho'],flush=True)
        results[asset]={'coinbase_cache_sha256':digest(cb_path),'binance_raw_audit':raw_audit,'variants':variants,'scope':'Observed-time join of recorder midpoint/flow with authenticated exchange close/flow; recorder provider and subsecond alignment remain unauthenticated; USD versus USDT basis is not eliminated'}
        (HERE/'joint_results.json').write_text(json.dumps({'scope':'New independent reconstruction of the original cross-venue study question; does not restore untraced old Table7/8 numbers','sampling_seconds':DELTA,'ema_seconds':WINDOW,'burn_bins':BURN,'assets':results,'input_manifest_sha256':digest(HERE/'restoration_manifest.json')},indent=2)+'\n')
        for h in HORIZONS:
            d=variants['primary']['decomposition']['horizons'][str(h)];s=np.array(d['generalized_row_normalized']);lo=np.array(d['orthogonal_order_min']);hi=np.array(d['orthogonal_order_max'])
            summaries.append({'asset':asset,'horizon_steps':h,'horizon_seconds':h*DELTA,'rho':variants['primary']['fit']['rho'],'bn_price_to_cb_price_generalized':s[0,2],'cb_price_to_bn_price_generalized':s[2,0],'bn_price_to_cb_price_order_min':lo[0,2],'bn_price_to_cb_price_order_max':hi[0,2],'cb_price_to_bn_price_order_min':lo[2,0],'cb_price_to_bn_price_order_max':hi[2,0]})
    pd.DataFrame(summaries).to_csv(HERE/'joint_fevd_summary.csv',index=False)
if __name__=='__main__':run()
