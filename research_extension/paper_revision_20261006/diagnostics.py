"""Segment-aware covariance specification and fixed-spectrum loss diagnostics."""
from pathlib import Path
import json
import sys
import numpy as np
import pandas as pd
from scipy import linalg, stats
from scipy.optimize import minimize

REV=Path(__file__).resolve().parent
ROOT=REV.parents[1]
sys.path.insert(0,str(REV))
sys.path.insert(0,str(ROOT))
from revise_evidence import series
from simulations.feedback_dealer import simulate


def md(segments, bandwidth=10):
    z=np.vstack(segments)
    mu=z.mean(0);sd=z.std(0)
    segments=[(s-mu)/sd for s in segments]
    vectors=[];groups=[]
    for i,s in enumerate(segments):
        a,b,c=s[:-2],s[1:-1],s[2:]
        if len(a)<50:continue
        v0=np.column_stack([a[:,0]**2,a[:,0]*a[:,1],a[:,1]**2])
        v1=(b[:,:,None]*a[:,None,:]).reshape(-1,4)
        v2=(c[:,:,None]*a[:,None,:]).reshape(-1,4)
        vectors.append(np.column_stack([v0,v1,v2]));groups.extend([i]*len(a))
    moments=np.vstack(vectors);groups=np.array(groups);N=len(moments)
    target=moments.mean(0);u=moments-target
    hac=u.T@u/N
    for lag in range(1,bandwidth+1):
        valid=groups[lag:]==groups[:-lag]
        gamma=u[lag:][valid].T@u[:-lag][valid]/N
        hac+=(1-lag/(bandwidth+1))*(gamma+gamma.T)
    W=np.linalg.pinv(hac)
    x=np.vstack([s[:-1] for s in segments]);y=np.vstack([s[1:] for s in segments])
    j=np.linalg.lstsq(x,y,rcond=None)[0].T
    e=y-x@j.T;cov=e.T@e/len(e)
    initial=np.r_[j.ravel(),cov[0,0],cov[0,1],cov[1,1]]
    def theoretical(p):
        J=p[:4].reshape(2,2)
        S=np.array([[p[4],p[5]],[p[5],p[6]]])
        if max(abs(np.linalg.eigvals(J)))>=.9999 or min(np.linalg.eigvalsh(S))<=0:return None
        g0=linalg.solve_discrete_lyapunov(J,S);g1=J@g0;g2=J@g1
        return np.r_[g0[0,0],g0[0,1],g0[1,1],g1.ravel(),g2.ravel()]
    def obj(p):
        pred=theoretical(p)
        if pred is None:return 1e8
        delta=target-pred
        return float(delta@W@delta)
    bounds=[(-.999,.999),(-2,2),(-2,2),(-.999,.999),(.000001,5),(-2,2),(.000001,5)]
    fit=minimize(obj,initial,method='L-BFGS-B',bounds=bounds,options={'maxiter':1000,'ftol':1e-13,'gtol':1e-8})
    pred=theoretical(fit.x)
    if pred is None:return {'success':False,'message':str(fit.message)}
    jac=np.column_stack([(theoretical(fit.x+np.eye(7)[i]*1e-6)-pred)/1e-6 for i in range(7)])
    rank=int(np.linalg.matrix_rank(jac));p=fit.x
    statistic=N*obj(p)
    return {'success':bool(fit.success),'message':str(fit.message),'n_moment_rows':N,'n_segments':len(segments),
            'theta':p.tolist(),'rank':rank,'df':4,'J_stat':statistic,'p_chi2':float(stats.chi2.sf(statistic,4)),
            'Q':float(p[1]*p[2]/(1-p[3])),'S':float(p[0]+p[1]*p[2]/(1-p[3])),
            'rho':float(max(abs(np.linalg.eigvals(p[:4].reshape(2,2))))),
            'inference_scope':'HAC moment-based diagnostic; asymptotic chi-square reference, no independent causal validation'}


def covariance_checks():
    results={}
    for asset in ['BTC','ETH','ADA']:
        s=series(pd.read_pickle(ROOT/'empirical_pipeline/cache'/f'{asset}_1sec_core_v2dedup.pkl'))
        segments=[g[['x','flow']].to_numpy() for _,g in s.groupby(['day','segment']) if len(g)>=500]
        results[asset]=md(segments)
        print(asset,'MD',results[asset],flush=True)
    (REV/'results/md_reanalysis.json').write_text(json.dumps(results,indent=2)+'\n')


def dealer_checks():
    legacy=json.loads((ROOT/'results/provenance/solvency_feedback.json').read_text())
    results={'scope':'fresh seeded paths conditional on preserved flow-moment calibration; flow moment calibration not independently re-estimated',
             'params':legacy['params'],'cells':[],'moments':legacy['moments']}
    lookup={(r['S'],r['L'],r['phi'],r['mode']):r for r in legacy['cells']}
    for S in legacy['S_grid']:
        for L in [10.,20.]:
            for mode in ['feedback','B1','B2','B3']:
                r=simulate(S,L,.05,mode,400,legacy['moments'][str(S)])
                old=lookup[S,L,.05,mode]
                r['legacy_halts']=old['halts'];r['matches_legacy']=r['halts']==old['halts']
                results['cells'].append(r)
        print('dealer S',S,'complete',flush=True)
    (REV/'results/dealer_reproduction.json').write_text(json.dumps(results,indent=2)+'\n')


def transient_checks():
    rows=[];paths={}
    for theta in [0.,.5,2.,8.]:
        J=np.array([[.85,theta],[0,.85]])
        C=np.array([[1.,0.]])
        loss=np.array([np.linalg.norm(C@np.linalg.matrix_power(J,t),2) for t in range(101)])
        peak=int(loss.argmax());M=float(loss[peak]);radius=1/M
        direction=(C@np.linalg.matrix_power(J,peak)).ravel()/M
        values=[float(abs((C@np.linalg.matrix_power(J,t))@direction)[0]) for t in range(101)]
        rows.append({'theta':theta,'rho':.85,'M_C':M,'peak_time':peak,'B':1.,'safe_radius':radius,
                     'unit_shock_peak_loss':max(values),'radius_shock_peak_loss':max(values)*radius,
                     'above_radius_peak_loss':max(values)*(radius+1e-6),
                     'tail_certificate':'both rho^t and t*rho^(t-1) decrease for t>=7; maximum covered by 0..100'})
        paths[str(theta)]=loss.tolist()
    out={'coordinates':'fixed abstract coordinates and C=[1,0], Euclidean initial-shock ball; illustrative, not market calibrated',
         'rows':rows,'paths':paths,'finite_horizon':100}
    (REV/'results/transient_checks.json').write_text(json.dumps(out,indent=2)+'\n')
    return out


def threshold_check():
    cols=['system_time','midpoint','spread','buys','sells','bids_notional_0','asks_notional_0',
          'bids_distance_0','asks_distance_0']
    df=pd.read_csv(ROOT/'empirical_pipeline/data/BTC_1sec.csv',nrows=50000,usecols=cols)
    keys=[c for c in cols if c!='system_time']
    duplicate=df[keys].eq(df[keys].shift()).all(axis=1)
    df['flow']=np.where(duplicate,0,df.buys-df.sells)/df.midpoint
    df['sec']=((pd.to_datetime(df.system_time,utc=True)-pd.Timestamp('1970-01-01',tz='UTC'))
               //pd.Timedelta('1s')).astype('int64')
    df=df.drop_duplicates('sec').sort_values('sec').copy()
    x=df.midpoint.to_numpy()-df.midpoint.ewm(alpha=.01,adjust=False).mean().to_numpy()
    sec=df.sec.to_numpy();gap=sec[1:]-sec[:-1]
    valid=(gap==1)&(np.arange(len(gap))>=500)
    y=np.diff(x)[valid];xlag=x[:-1][valid];f=df.flow.to_numpy()[:-1][valid]
    spread=df.spread.to_numpy()[:-1][valid]
    threshold=float(np.quantile(spread,.9));wide=(spread>threshold).astype(float)
    X=np.column_stack([np.ones(len(y)),xlag,f,wide,wide*xlag,wide*f])
    inv=np.linalg.pinv(X.T@X);beta=np.linalg.lstsq(X,y,rcond=None)[0];e=y-X@beta
    score=X*e[:,None];cov=score.T@score
    times=sec[:-1][valid]
    for lag in range(1,61):
        continuous=(times[lag:]-times[:-lag])==lag
        gamma=score[lag:][continuous].T@score[:-lag][continuous]
        cov+=(1-lag/61)*(gamma+gamma.T)
    cov=inv@cov@inv*len(y)/(len(y)-X.shape[1])
    se=float(np.sqrt(cov[5,5]));z=float(beta[5]/se)
    depth=(df.bids_notional_0+df.asks_notional_0).to_numpy()[:-1][valid]
    result={'sample_rows':len(df),'n_transitions':len(y),'duplicate_renders_corrected':int(duplicate.sum()),
            'model':'USD EMA deviation difference on lagged deviation/observed signed base-unit flow and spread interactions',
            'threshold_usd':threshold,'HAC_bandwidth_seconds':60,'flow_slope_calm':float(beta[2]),
            'flow_slope_wide':float(beta[2]+beta[5]),'flow_slope_difference':float(beta[5]),
            'HAC_se_difference':se,'p_normal_reference':float(2*stats.norm.sf(abs(z))),
            'calm_n':int((wide==0).sum()),'wide_n':int((wide==1).sum()),
            'calm_depth_mean':float(depth[wide==0].mean()),'wide_depth_mean':float(depth[wide==1].mean()),
            'residual_sd_calm':float(e[wide==0].std(ddof=1)),
            'residual_sd_wide':float(e[wide==1].std(ddof=1)),
            'residual_sd_ratio':float(e[wide==1].std(ddof=1)/e[wide==0].std(ddof=1)),
            'scope':'exploratory first-50000-row subsample, selected spread threshold, no causal identification; dimensional slopes are not Q'}
    (REV/'results/threshold_reanalysis.json').write_text(json.dumps(result,indent=2)+'\n')
    print('threshold',result,flush=True)


def figures():
    import matplotlib
    matplotlib.use('Agg')
    import matplotlib.pyplot as plt
    folder=REV/'figures';folder.mkdir(exist_ok=True)
    d=json.loads((REV/'results/coinbase_reanalysis.json').read_text())
    fig,ax=plt.subplots(figsize=(7,3.6),layout='constrained')
    names=['BTC','ETH','ADA'];pos=np.arange(3)
    for off,key,label in [(-.22,'x_observed','EMA, observed flow'),(0,'x_forward','EMA, forward flow'),(.22,'return_observed','Raw return, observed flow')]:
        m=np.array([d[a]['variants'][key]['Q']['mean'] for a in names])
        ci=np.array([d[a]['variants'][key]['Q']['ci95'] for a in names])
        ax.errorbar(pos+off,m,yerr=np.array([m-ci[:,0],ci[:,1]-m]),fmt='o',capsize=3,label=label)
    ax.set_xticks(pos,names);ax.axhline(0,color='gray',lw=.8);ax.set_ylabel('Reduced-form Q');ax.legend(fontsize=8)
    fig.savefig(folder/'timing_comparison.pdf');fig.savefig(folder/'timing_comparison.png',dpi=150);plt.close(fig)
    t=json.loads((REV/'results/transient_checks.json').read_text())
    fig,ax=plt.subplots(figsize=(7,3.5),layout='constrained')
    for theta,path in t['paths'].items():ax.plot(path[:41],label=f'coupling = {theta}')
    ax.set_xlabel('Time step');ax.set_ylabel('Output magnification');ax.legend();fig.savefig(folder/'transient_loss.pdf');fig.savefig(folder/'transient_loss.png',dpi=150);plt.close(fig)


if __name__=='__main__':
    covariance_checks()
    threshold_check()
    dealer_checks()
    transient_checks()
    figures()
