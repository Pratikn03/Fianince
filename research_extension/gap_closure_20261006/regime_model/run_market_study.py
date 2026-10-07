"""Existing-sample retrospective switching-regression diagnosis; all starts retained."""
from pathlib import Path
import sys,json,hashlib,time
import numpy as np
from scipy import stats
from scipy.special import logsumexp
HERE=Path(__file__).resolve().parent;ROOT=HERE.parents[2]
sys.path.insert(0,str(HERE.parent/'model_diagnostics'))
from predictive_diagnostics import coinbase
from switching_regression import fit,emissions
SEEDS=[7,29,61,103];FLOORS=[1e-6,1e-4]

def serial(v):
    if isinstance(v,np.ndarray):return v.tolist()
    if isinstance(v,np.generic):return v.item()
    raise TypeError(type(v).__name__)

def prepare(chunks,mean=None,scale=None,ym=None,ys=None):
    raw=[(np.column_stack([c['z'][:-1,0],c['z'][:-1,1]]),np.diff(c['z'][:,0]) if c['state']=='x' else c['z'][1:,0]) for c in chunks]
    if mean is None:
        X=np.vstack([v[0] for v in raw]);y=np.concatenate([v[1] for v in raw]);mean=X.mean(0);scale=X.std(0);ym=y.mean();ys=y.std()
    if np.any(scale<=0) or ys<=0:raise ValueError('Degenerate training scale')
    seg=[(np.column_stack([np.ones(len(y)),(X-mean)/scale]),(y-ym)/ys) for X,y in raw]
    return seg,{'mean':mean,'scale':scale,'ym':ym,'ys':ys}

def starts(seg,shared,floor,seeds=SEEDS):
    results=[]
    for seed in seeds:
        f=fit(seg,seed=seed,shared_beta=shared,variance_floor=floor,max_iter=300,tol=1e-8)
        f['seed']=seed;f.pop('posterior',None);results.append(f)
    eligible=[f for f in results if f['status'] in ['CONVERGED','ITERATION_LIMIT']]
    if not eligible:raise ValueError('No usable fit')
    selected=max(eligible,key=lambda r:r['log_likelihood'])
    return selected,results

def score(seg,model,ys):
    mse=[];nll=[]
    for X,y in seg:
        pred=model['initial'].copy();mu=X@model['beta'].T
        e=emissions(X,y,model['beta'],model['variance'])
        for t in range(len(y)):
            forecast=pred@mu[t];mse.append((y[t]-forecast)**2*ys**2)
            joint=np.log(np.maximum(pred,1e-300))+e[t];ll=logsumexp(joint)
            nll.append(-ll+np.log(ys));posterior=np.exp(joint-ll);pred=posterior@model['transition']
    return {'n':len(mse),'mse':float(np.mean(mse)),'negative_log_score':float(np.mean(nll))}

def interval(values):
    a=np.asarray(values);mean=float(a.mean());se=float(stats.sem(a));half=float(stats.t.ppf(.975,len(a)-1)*se)
    return {'mean':mean,'ci95':[mean-half,mean+half],'n_dates':len(a),'scope':'Exploratory date-level t reference, not justified serial independence or external preregistration'}

def run():
    protocol={'created_unix':time.time(),'assets':['BTC','ETH','ADA'],'states':['x','return'],'floors':FLOORS,'seeds':SEEDS,'fold_seeds':SEEDS[:2],'max_iter':300,'tol':1e-8,'initial_train_dates':6,'selection':'Maximum conditional training likelihood within each fixed specification; every start/convergence status retained','measurement':'Same existing causal EMA/gap construction as prior forecast study; scalar next-difference EMA or next raw return, lagged state and observed flow; no structural VAR','uncertainty':'Chronological whole-date forecasts; few dates, exploratory intervals; no regular chi-square switching LR reference','scope':'Retrospective existing-data study, not new learning-agent experiment'}
    (HERE/'market_protocol.json').write_text(json.dumps(protocol,indent=2)+'\n')
    output={'protocol':protocol,'datasets':{}}
    for asset in protocol['assets']:
      for state in protocol['states']:
        chunks,provenance=coinbase(asset,state)
        for c in chunks:c['state']=state
        dates=sorted({c['date'] for c in chunks});seg,scaling=prepare(chunks);specs={}
        for floor in FLOORS:
          for shared in [True,False]:
            key=f'{floor:g}_'+('variance_only' if shared else 'coefficients_and_variance')
            chosen,allstarts=starts(seg,shared,floor)
            coef=np.asarray(chosen['beta']);physical=coef[:,1:]*scaling['ys']/scaling['scale'][None,:]
            specs[key]={'selected':chosen,'starts':allstarts,'physical_slopes':physical,'residual_sd_ratio':float(np.sqrt(chosen['variance'][1]/chosen['variance'][0])),'durations_steps':1/(1-np.diag(chosen['transition']))}
            print(asset,state,key,chosen['status'],chosen['log_likelihood'],flush=True)
        folds=[]
        for i in range(6,len(dates)):
            train=[c for c in chunks if c['date']<dates[i]];test=[c for c in chunks if c['date']==dates[i]]
            tr,sc=prepare(train);te,_=prepare(test,**sc)
            X=np.vstack([v[0] for v in tr]);y=np.concatenate([v[1] for v in tr]);b=np.linalg.lstsq(X,y,rcond=None)[0];variance=np.mean((y-X@b)**2)
            baseline={'initial':np.array([.5,.5]),'beta':np.tile(b,(2,1)),'variance':np.array([variance,variance]),'transition':np.array([[.5,.5],[.5,.5]])}
            row={'date':dates[i],'train_dates':dates[:i],'baseline':score(te,baseline,sc['ys']),'models':{}}
            for shared in [True,False]:
                key='variance_only' if shared else 'coefficients_and_variance';chosen,allstarts=starts(tr,shared,1e-6,seeds=SEEDS[:2])
                row['models'][key]={'score':score(te,chosen,sc['ys']),'selected':chosen,'starts':allstarts}
            folds.append(row);print('fold',asset,state,dates[i],flush=True)
        summary={}
        for key in ['variance_only','coefficients_and_variance']:
            summary[key]={metric:interval([r['baseline'][metric]-r['models'][key]['score'][metric] for r in folds]) for metric in ['mse','negative_log_score']}
        summary['full_minus_variance_only']={metric:interval([r['models']['variance_only']['score'][metric]-r['models']['coefficients_and_variance']['score'][metric] for r in folds]) for metric in ['mse','negative_log_score']}
        output['datasets'][asset+'_'+state]={'provenance':provenance,'dates':dates,'n':sum(len(v[1]) for v in seg),'segments':len(seg),'scaling':scaling,'specifications':specs,'folds':folds,'summary':summary}
        (HERE/'market_results.json').write_text(json.dumps(output,default=serial,indent=2)+'\n')
    output['status']='COMPLETED_FIXED_PROTOCOL';(HERE/'market_results.json').write_text(json.dumps(output,default=serial,indent=2)+'\n')
if __name__=='__main__':run()
