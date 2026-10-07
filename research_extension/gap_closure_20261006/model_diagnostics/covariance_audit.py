"""Independent covariance MD audit with a complete stable/SPD parameterization.
The moment equations, HAC weights and all fixed bandwidth cases are retained.
"""
from pathlib import Path
import hashlib,json,sys
import numpy as np
import pandas as pd
from scipy import linalg,stats
from scipy.optimize import least_squares
HERE=Path(__file__).resolve().parent;ROOT=HERE.parents[2];REV=ROOT/'research_extension/paper_revision_20261006'
sys.path.insert(0,str(REV));from revise_evidence import series
BANDWIDTHS=[5,10,20,40];SEED=20261007

def moment_rows(segments,centering="global"):
    all_=np.vstack(segments);mean=all_.mean(0);sd=all_.std(0);scaled=[(s-(mean if centering=='global' else s.mean(0)))/sd for s in segments];blocks=[]
    for s in scaled:
        a,b,c=s[:-2],s[1:-1],s[2:]
        blocks.append(np.column_stack([a[:,0]**2,a[:,0]*a[:,1],a[:,1]**2,(b[:,:,None]*a[:,None,:]).reshape(-1,4),(c[:,:,None]*a[:,None,:]).reshape(-1,4)]))
    return scaled,blocks,mean,sd

def parameters(p):
    # Gamma0=L L^T is any SPD stationary covariance.
    L=np.array([[np.exp(p[4]),0],[p[5],np.exp(p[6])]]);G=L@L.T
    values,vectors=np.linalg.eigh(G);sqrt=(vectors*np.sqrt(values))@vectors.T;inv=(vectors/np.sqrt(values))@vectors.T
    M=p[:4].reshape(2,2);U,s,Vt=np.linalg.svd(M);K=(U*(s/np.sqrt(1+s*s)))@Vt
    # I-KK^T is SPD, so J has a positive innovation covariance and is stable.
    J=sqrt@K@inv;Sigma=sqrt@(np.eye(2)-K@K.T)@sqrt
    G1=J@G;G2=J@G1
    moments=np.r_[G[0,0],G[0,1],G[1,1],G1.ravel(),G2.ravel()]
    return moments,J,Sigma,G

def initial(scaled):
    x=np.vstack([s[:-1] for s in scaled]);y=np.vstack([s[1:] for s in scaled]);J=np.linalg.lstsq(x,y,rcond=None)[0].T
    G=np.vstack(scaled).T@np.vstack(scaled)/sum(map(len,scaled));L=np.linalg.cholesky(G)
    values,vectors=np.linalg.eigh(G);sqrt=(vectors*np.sqrt(values))@vectors.T;inv=(vectors/np.sqrt(values))@vectors.T
    K=inv@J@sqrt;U,s,Vt=np.linalg.svd(K);s=np.minimum(s,.999);M=(U*(s/np.sqrt(1-s*s)))@Vt
    return np.r_[M.ravel(),np.log(L[0,0]),L[1,0],np.log(L[1,1])]

def audit(segments,bandwidth=10,starts=6,centering="global"):
    scaled,blocks,mean,sd=moment_rows(segments,centering);moments=np.vstack(blocks);N=len(moments);target=moments.mean(0)
    hac=np.zeros((11,11))
    for block in blocks:
        u=block-target;hac+=u.T@u/N
        for lag in range(1,min(bandwidth+1,len(block))):
            gamma=u[lag:].T@u[:-lag]/N;hac+=(1-lag/(bandwidth+1))*(gamma+gamma.T)
    values,vectors=np.linalg.eigh(hac);cutoff=values.max()*1e-12;good=values>cutoff;W=(vectors[:,good]/np.sqrt(values[good])).T
    p0=initial(scaled);rng=np.random.default_rng(SEED);fits=[]
    for start in range(starts):
        p=p0 if start==0 else p0+rng.normal(size=7)*np.array([.05,.05,.05,.05,.02,.02,.02])
        fit=least_squares(lambda q:W@(target-parameters(q)[0]),p,jac='3-point',max_nfev=2000,ftol=1e-12,xtol=1e-12,gtol=1e-10)
        fits.append(fit)
    best=min(fits,key=lambda f:float(f.fun@f.fun));pred,J,Sigma,G=parameters(best.x)
    jac=np.column_stack([(parameters(best.x+np.eye(7)[i]*1e-6)[0]-parameters(best.x-np.eye(7)[i]*1e-6)[0])/2e-6 for i in range(7)])
    rank=int(np.linalg.matrix_rank(jac));wrank=int(good.sum());df=wrank-rank;stat=N*float(best.fun@best.fun)
    statistic_by_start=[N*float(f.fun@f.fun) for f in fits];Q=J[0,1]*J[1,0]/(1-J[1,1])
    return {'centering':centering,'bandwidth_bins':bandwidth,'n_rows':N,'n_segments':len(segments),'moment_rank':wrank,'parameter_jacobian_rank':rank,'df':df,'J_stat':stat,'p_chi2':float(stats.chi2.sf(stat,df)),'Q':float(Q),'S':float(J[0,0]+Q),'rho':float(max(abs(np.linalg.eigvals(J)))),'J_normalized':J.tolist(),'innovation_covariance':Sigma.tolist(),'stationary_covariance':G.tolist(),'target_moments':target.tolist(),'fitted_moments':pred.tolist(),'raw_moment_differences':(target-pred).tolist(),'HAC_eigenvalues':values.tolist(),'HAC_condition_positive':float(values[good].max()/values[good].min()),'starts':[{'success':bool(f.success),'nfev':f.nfev,'J_stat':v,'optimality':float(f.optimality)} for f,v in zip(fits,statistic_by_start)],'best_success':bool(best.success),'max_start_statistic_spread':float(max(statistic_by_start)-min(statistic_by_start)),'scope':'Stable VAR1 covariance restriction diagnostic with unrestricted SPD innovation covariance; chi-square reference is asymptotic, not a structural/causal certificate'}

def run():
    results={}
    for asset in ['BTC','ETH','ADA']:
        path=ROOT/'empirical_pipeline/cache'/f'{asset}_1sec_core_v2dedup.pkl';s=series(pd.read_pickle(path));segments=[g[['x','flow']].to_numpy() for _,g in s.groupby(['day','segment']) if len(g)>=500]
        r={}
        for bandwidth in BANDWIDTHS:
            r[str(bandwidth)]=audit(segments,bandwidth);print(asset,'bandwidth',bandwidth,'J',r[str(bandwidth)]['J_stat'],'p',r[str(bandwidth)]['p_chi2'],flush=True)
        results[asset]={'input_sha256':hashlib.sha256(path.read_bytes()).hexdigest(),'bandwidth_cases':r}
        (HERE/'covariance_results.json').write_text(json.dumps({'scope':'Independent full-class parameterization and fixed HAC bandwidth/multistart audit; no passing-case selection','parameterization_note':'For any stable J with SPD Sigma, its stationary Gamma0 yields K=Gamma0^(-1/2) J Gamma0^(1/2), with I-KK^T SPD. K=M(I+M^TM)^(-1/2) spans all strict contractions. Thus this removes unnecessary entrywise bounds from the prior implementation.','bandwidths':BANDWIDTHS,'starts_per_case':6,'seed':SEED,'assets':results},indent=2)+'\n')
    print('Covariance audit complete',flush=True)
if __name__=='__main__':run()
