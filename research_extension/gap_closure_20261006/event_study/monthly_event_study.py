"""Monthly event contrasts on the exact original 2022 sample, with fitted covariance.
No pooled-SE substitution; date-saturated failure is reported, not inverted.
"""
from pathlib import Path
import json,hashlib
import numpy as np
import pandas as pd
from scipy import stats
HERE=Path(__file__).resolve().parent;ROOT=HERE.parents[2]
REFERENCE_MONTH=6

def design(frame,period='month'):
    f=frame.sort_values(['date','symbol']).reset_index(drop=True).copy()
    f['month']=pd.to_datetime(f.date).dt.month;assets=sorted(f.symbol.unique());dates=sorted(f.date.unique())
    columns=[np.ones(len(f))];names=['intercept']
    for asset in assets[1:]:columns.append((f.symbol==asset).to_numpy(float));names.append('asset:'+asset)
    for date in dates[1:]:columns.append((f.date==date).to_numpy(float));names.append('date:'+date)
    treated=(f.symbol=='BTCUSDT').to_numpy(float)
    if period=='month':periods=list(range(1,13));reference=6;values=f.month.to_numpy()
    elif period=='date':periods=dates;reference='2022-06-24';values=f.date.to_numpy()
    else:raise ValueError('Unknown event clock')
    event_columns={}
    for value in periods:
        if value==reference:continue
        event_columns[str(value)]=len(columns);columns.append(treated*(values==value));names.append('treated_period:'+str(value))
    X=np.column_stack(columns)
    if np.linalg.matrix_rank(X)!=X.shape[1]:raise ValueError('Design is rank deficient')
    return f,X,names,event_columns,reference

def covariance(y,X,groups=None,hetero=None):
    n,k=X.shape;bread=np.linalg.inv(X.T@X);coef=np.linalg.lstsq(X,y,rcond=None)[0];residual=y-X@coef
    if groups is None:
        df=n-k
        if hetero is None:cov=(residual@residual)/(n-k)*bread
        elif hetero=='HC1':cov=bread@(X.T@(X*residual[:,None]**2))@bread*n/(n-k)
        elif hetero=='HC3':
            leverage=np.einsum('ij,jk,ik->i',X,bread,X)
            if np.any(leverage>=1-1e-10):raise ValueError('HC3 unavailable at unit-leverage observations')
            score=X*(residual/(1-leverage))[:,None];cov=bread@(score.T@score)@bread
        else:raise ValueError('Unknown heteroskedastic covariance')
    else:
        labels=np.unique(groups);scores=np.vstack([X[groups==g].T@residual[groups==g] for g in labels])
        cov=bread@(scores.T@scores)@bread*len(labels)/(len(labels)-1)*(n-1)/(n-k);df=len(labels)-1
    return coef,cov,df,residual

def wald_reference(coef,cov,indices,df,outcome_variance):
    b=coef[indices];V=cov[np.ix_(indices,indices)];V=(V+V.T)/2;eig=np.linalg.eigvalsh(V)
    cutoff=max(float(max(eig))*1e-10,outcome_variance*1e-12);rank=int((eig>cutoff).sum())
    if rank<len(indices):return {'status':'DEGENERATE_COVARIANCE_NO_VALID_REFERENCE','rank':rank,'restrictions':len(indices),'df_denominator':df,'F':None,'p_F':None,'eigenvalues':eig.tolist()}
    F=float(b@np.linalg.solve(V,b)/len(indices))
    return {'status':'CONDITIONAL_REFERENCE','rank':rank,'restrictions':len(indices),'df_denominator':df,'F':F,'p_F':float(stats.f.sf(F,len(indices),df)),'eigenvalues':eig.tolist()}

def analyze(frame,outcome,period='month'):
    f,X,names,event_columns,reference=design(frame,period);y=f[outcome].to_numpy();results={};fits={}
    for kind,groups in [('classical',None),('HC1',None),('HC3',None),('asset_cluster',f.symbol.to_numpy()),('date_cluster',f.date.to_numpy()),('month_cluster',f.month.to_numpy())]:
        try:coef,cov,df,residual=covariance(y,X,groups,kind if kind in ['HC1','HC3'] else None)
        except ValueError as error:
            coef=covariance(y,X)[0];fits[kind]=None
            results[kind]={'status':'UNAVAILABLE_HIGH_LEVERAGE','reason':str(error),'pretrend_joint_test':{'status':'UNAVAILABLE_HIGH_LEVERAGE','rank':None,'restrictions':None,'df_denominator':None,'F':None,'p_F':None}}
            continue
        fits[kind]=(coef,cov,df,residual)
        pre=[idx for key,idx in event_columns.items() if (int(key)<6 if period=='month' else key<'2022-06-24')]
        results[kind]={'pretrend_joint_test':wald_reference(coef,cov,pre,df,float(np.var(y,ddof=1))),'residual_df':len(y)-X.shape[1],'reference_df':df,'covariance':cov.tolist(),'coefficients':coef.tolist(),'max_treated_abs_residual':float(max(abs(residual[f.symbol=='BTCUSDT'])))}
    contrasts=[]
    for value,index in event_columns.items():
        row={'period':value,'event_month':int(value)-7 if period=='month' else None,'references':{}}
        for kind,fit in fits.items():
            if fit is None:
                row['references'][kind]={'beta':float(fits['classical'][0][index]),'se':None,'df':None,'ci95':None,'p_t':None,'status':'UNAVAILABLE_HIGH_LEVERAGE'}
                continue
            coef,cov,df,residual=fit
            variance=float(cov[index,index]);se=np.sqrt(max(0,variance));cut=stats.t.ppf(.975,df)
            degenerate=variance<float(np.var(y,ddof=1))*1e-12
            row['references'][kind]={'beta':float(coef[index]),'se':float(se),'df':df,'ci95':[float(coef[index]-cut*se),float(coef[index]+cut*se)],'p_t':None if degenerate else float(2*stats.t.sf(abs(coef[index]/se),df)),'status':'DEGENERATE_REFERENCE' if degenerate else 'CONDITIONAL_REFERENCE'}
        contrasts.append(row)
    # Independent point check using directly aggregated treated-minus-control gaps.
    group='month' if period=='month' else 'date'
    means=f.groupby([group,'symbol'])[outcome].mean().unstack();gaps=means.BTCUSDT-means.drop(columns='BTCUSDT').mean(axis=1)
    manual={str(key):float(value-gaps.loc[reference]) for key,value in gaps.items() if key!=reference}
    errors=[abs(r['references']['classical']['beta']-manual[r['period']]) for r in contrasts]
    if max(errors)>1e-10:raise ValueError('FE coefficients disagree with manual month/date contrasts')
    return {'outcome':outcome,'period_clock':period,'reference':reference,'n':len(f),'n_assets':f.symbol.nunique(),'n_dates':f.date.nunique(),'design_columns':names,'design_rank':X.shape[1],'fits':results,'contrasts':contrasts,'manual_point_max_error':max(errors),'scope':'Fixed-effects association with one treated asset. Classical/cluster small-sample references are declared approximations; covariance arithmetic does not establish shock assignment, parallel counterfactual trends or no spillovers.'}

def run():
    path=HERE.parent/'cross_venue/original_panel_reproduction.json';d=json.loads(path.read_text())
    if len(d['rows'])!=768 or any(r['status']!='RAW_REPRODUCED' for r in d['rows']):raise ValueError('Require complete raw reproduction')
    results={}
    for variant in ['legacy','observed']:
        frame=pd.DataFrame([dict(symbol=r['symbol'],date=r['date'],Q=r[variant]['Q'],S=r[variant]['S']) for r in d['rows'] if r['year']==2022])
        assert len(frame)==192
        monthly={dep:analyze(frame,dep) for dep in ['Q','S']};saturated={dep:analyze(frame,dep,'date') for dep in ['Q','S']}
        results[variant]={'monthly':monthly,'date_saturated':saturated}
        for dep in ['Q','S']:print(variant,dep,'monthly date-cluster pretrend',monthly[dep]['fits']['date_cluster']['pretrend_joint_test'],'saturated',saturated[dep]['fits']['date_cluster']['pretrend_joint_test']['status'],flush=True)
    out={'input_sha256':hashlib.sha256(path.read_bytes()).hexdigest(),'scope':'Reconstruction of original monthly event-study question on original24 sampled2022 dates; legacy/observed diagnostics separate; no causal validation','monthly_model':'Asset FE, sampled-date FE, BTC-by-calendar-month interactions; June reference; January–May5-restriction pretrend reference','treatment_date':'2022-07-08','event_month_clock':'January=-6,...,June=-1,July=0,...,December=5; two original sampled dates per month','saturated_warning':'Date-level interactions perfectly fit the sole treated observation per date. Date-cluster event covariance is degenerate and cannot supply a valid F/t reference.','variants':results}
    (HERE/'event_results.json').write_text(json.dumps(out,indent=2)+'\n')
if __name__=='__main__':run()
