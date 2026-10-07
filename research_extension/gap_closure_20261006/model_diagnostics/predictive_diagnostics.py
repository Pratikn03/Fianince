"""Fixed-lag, date-block retrospective model diagnosis. No future-fit scaling."""
from pathlib import Path
import hashlib,json,sys
import numpy as np
import pandas as pd
from scipy import stats
HERE=Path(__file__).resolve().parent;ROOT=HERE.parents[2];REV=ROOT/'research_extension/paper_revision_20261006'
sys.path.insert(0,str(REV));from revise_evidence import series
MAX_LAG=6;LAGS=[1,2,3,6];TRAIN_DATES=6

def digest(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def rows(chunks,p):
    X=[];Y=[];groups=[]
    for i,c in enumerate(chunks):
        z=c['z'];idx=np.arange(MAX_LAG,len(z))
        if len(idx)==0:continue
        X.append(np.column_stack([z[idx-k] for k in range(1,p+1)]));Y.append(z[idx]);groups.extend([i]*len(idx))
    return np.vstack(X),np.vstack(Y),np.array(groups)

def fit(chunks,p,kind):
    # Only training observations enter normalization or parameter estimation.
    train=np.vstack([c['z'] for c in chunks]);mean=train.mean(0);scale=train.std(0)
    if np.any(scale<=0):raise ValueError('Degenerate training scale')
    scaled=[dict(c,z=(c['z']-mean)/scale) for c in chunks]
    X,Y,groups=rows(scaled,p);features=np.column_stack([np.ones(len(X)),X]);m=Y.shape[1]
    if kind=='VAR':
        B=np.linalg.lstsq(features,Y,rcond=None)[0];rank=int(np.linalg.matrix_rank(features));condition=float(np.linalg.cond(features))
    elif kind=='AR':
        B=np.zeros((features.shape[1],m));rank=m*(p+1);condition=0
        for j in range(m):
            cols=[0]+[1+j+k*m for k in range(p)];own=features[:,cols];B[cols,j]=np.linalg.lstsq(own,Y[:,j],rcond=None)[0];condition=max(condition,float(np.linalg.cond(own)))
    else:raise ValueError('Unknown model')
    blocks=[B[1+k*m:1+(k+1)*m].T for k in range(p)];companion=np.zeros((m*p,m*p));companion[:m]=np.hstack(blocks)
    if p>1:companion[m:,:-m]=np.eye(m*(p-1))
    residual=Y-features@B
    corr={}
    for lag in [1,2,3,6,12]:
        valid=groups[lag:]==groups[:-lag]
        corr[str(lag)]=[float(np.corrcoef(residual[lag:][valid,j],residual[:-lag][valid,j])[0,1]) for j in range(m)]
    return {'mean':mean,'scale':scale,'B':B,'rho':float(max(abs(np.linalg.eigvals(companion)))),'rank':rank,'condition':condition,'residual_correlations':corr,'n_train':len(Y)}

def predict(fit_,chunks,p):
    scaled=[dict(c,z=(c['z']-fit_['mean'])/fit_['scale']) for c in chunks];X,Y,g=rows(scaled,p)
    prediction=np.column_stack([np.ones(len(X)),X])@fit_['B'];error=Y-prediction
    return {'n_test':len(Y),'MSE_train_scale':np.mean(error**2,axis=0).tolist(),'RMSE_physical':(np.sqrt(np.mean(error**2,axis=0))*fit_['scale']).tolist()}

def mechanical(training,testing,price_columns,state):
    train=np.vstack([c['z'] for c in training]);mean=train.mean(0);scale=train.std(0);X,Y,_=rows(training,1);Xt,Yt,_=rows(testing,1);m=Y.shape[1]
    predictions=np.tile(mean,(len(Yt),1));anchor=1-2/(300/10+1)
    for j in price_columns:
        coefficient=anchor if state=='ema' else 0
        intercept=np.mean(Y[:,j]-coefficient*X[:,j]);predictions[:,j]=intercept+coefficient*Xt[:,j]
    error=Yt-predictions
    return {'n_test':len(Yt),'MSE_train_scale':np.mean((error/scale)**2,axis=0).tolist(),'RMSE_physical':np.sqrt(np.mean(error**2,axis=0)).tolist()}

def summarize(folds,variables):
    summaries={};paired={}
    models=sorted({r['model'] for r in folds})
    for model in models:
        r=[v for v in folds if v['model']==model];loss=np.array([v['MSE_train_scale'] for v in r]);rmse=np.array([v['RMSE_physical'] for v in r])
        summaries[model]={'n_dates':len(r),'equal_date_mean_MSE':dict(zip(variables,loss.mean(0).tolist())),'equal_date_mean_RMSE':dict(zip(variables,rmse.mean(0).tolist())),'max_train_rho':max([v.get('rho',0) for v in r]),'max_train_condition':max([v.get('condition',0) for v in r])}
    for p in LAGS:
        ar={r['test_date']:r for r in folds if r['model']==f'AR{p}'};var={r['test_date']:r for r in folds if r['model']==f'VAR{p}'};dates=sorted(ar)
        differences=np.array([np.array(ar[d]['MSE_train_scale'])-np.array(var[d]['MSE_train_scale']) for d in dates])
        entries={}
        for j,name in enumerate(variables):
            mean=float(differences[:,j].mean());se=float(stats.sem(differences[:,j]));crit=stats.t.ppf(.975,len(dates)-1)
            entries[name]={'AR_minus_VAR_mean_loss':mean,'date_t95':[mean-crit*se,mean+crit*se],'positive_dates':int((differences[:,j]>0).sum()),'relative_mean_improvement_percent':float(100*mean/summaries[f'AR{p}']['equal_date_mean_MSE'][name])}
        paired[str(p)]={'n_dates':len(dates),'variables':entries,'scope':'Exploratory paired date summaries; few serially ordered dates, no multiple-comparison or causal guarantee'}
    return {'models':summaries,'paired':paired}

def coefficient_variation(chunks,variables):
    daily=[]
    for date in sorted({c['date'] for c in chunks}):
        fit_=fit([c for c in chunks if c['date']==date],1,'VAR');s=fit_['scale'];J=fit_['B'][1:].T*s[:,None]/s[None,:]
        daily.append({'date':date,'J_raw':J.tolist(),'rho':fit_['rho'],'n':fit_['n_train']})
    matrices=np.array([r['J_raw'] for r in daily]);return {'daily':daily,'entry_ranges':{'min':matrices.min(0).tolist(),'max':matrices.max(0).tolist()},'scope':'Observed date-level coefficient variation; no formal proof of invariant or varying structural coefficients'}

def evaluate(chunks,variables,price_columns,state):
    dates=sorted({c['date'] for c in chunks});folds=[]
    for i in range(TRAIN_DATES,len(dates)):
        train=[c for c in chunks if c['date']<dates[i]];test=[c for c in chunks if c['date']==dates[i]]
        if not test:continue
        result=mechanical(train,test,price_columns,state);folds.append(dict(test_date=dates[i],train_last_date=dates[i-1],model='Mechanical',**result))
        for p in LAGS:
            for kind in ['AR','VAR']:
                fit_=fit(train,p,kind);result=predict(fit_,test,p)
                folds.append(dict(test_date=dates[i],train_last_date=dates[i-1],model=f'{kind}{p}',p=p,n_train=fit_['n_train'],rho=fit_['rho'],condition=fit_['condition'],residual_correlations=fit_['residual_correlations'],**result))
    return {'dates':dates,'folds':folds,'summary':summarize(folds,variables),'coefficient_variation':coefficient_variation(chunks,variables),'variables':variables}

def coinbase(asset,state):
    path=ROOT/'empirical_pipeline/cache'/f'{asset}_1sec_core_v2dedup.pkl';s=series(pd.read_pickle(path));chunks=[]
    for (day,segment),g in s.groupby(['day','segment']):
        if len(g)<500:continue
        z=g[[state,'flow']].to_numpy()
        if not np.all(np.isfinite(z)):raise ValueError('Nonfinite retained state')
        chunks.append({'date':str(day.date()),'segment':int(segment),'z':z})
    return chunks,{'path':str(path),'sha256':digest(path),'filter_scope':'Uses exact previously reported causal EMA construction; filters reset at data gaps, regressions/lags do not cross UTC dates. EMA itself continues across contiguous UTC dates in this prior construction.'}

def joint(asset):
    path=HERE.parent/'cross_venue'/f'{asset}_joint_panel.csv.gz';frame=pd.read_csv(path);names=['coinbase_price','coinbase_flow','binance_price','binance_flow'];chunks=[]
    for (date,segment),g in frame.groupby(['date','segment']):chunks.append({'date':date,'segment':int(segment),'z':g[names].to_numpy()})
    return chunks,{'path':str(path),'sha256':digest(path),'filter_scope':'Joint panel resets both filters at gaps and UTC dates; previously verified original-overlap construction'}

def run():
    results={};protocol=HERE/'protocol.json'
    for asset in ['BTC','ETH','ADA']:
        data={}
        for state,key in [('x','coinbase_ema_observed'),('return','coinbase_return_observed')]:
            chunks,provenance=coinbase(asset,state);data[key]=dict(evaluate(chunks,['price','flow'],[0],'ema' if state=='x' else 'return'),provenance=provenance)
            print(asset,key,'fold dates',data[key]['summary']['models']['VAR1']['n_dates'],flush=True)
        chunks,provenance=joint(asset);data['joint_ema_observed']=dict(evaluate(chunks,['coinbase_price','coinbase_flow','binance_price','binance_flow'],[0,2],'ema'),provenance=provenance)
        results[asset]=data
        (HERE/'predictive_results.json').write_text(json.dumps({'protocol_sha256':digest(protocol),'scope':'Fixed alternatives, retrospective whole-date backtest; predictive association only','assets':results},indent=2)+'\n')
        print(asset,'joint finished',flush=True)
    print('All diagnostic comparisons finished',flush=True)
if __name__=='__main__':run()
