"""Inference from known probe fills and observed prices only.

Unknown impact, persistence, agent state, weights, component count and noise
variance are never inputs. A valid rate floor remains required side information.
"""
from __future__ import annotations
from functools import lru_cache
import numpy as np
from scipy.optimize import linprog,lsq_linear
from scipy.stats import t as student_t


def _arrays(lower,upper):
    L=np.asarray(lower,dtype=float);U=np.asarray(upper,dtype=float)
    if L.ndim!=1 or len(L)<3 or U.shape!=L.shape or not np.isfinite(L).all() or not np.isfinite(U).all() or np.any(L>U):
        raise ValueError('finite consistent response bounds, length >=3, required')
    return L,U


def label(lo,hi,tol=1e-7):
    if np.isnan(lo) or np.isnan(hi) or lo>hi+tol:return 'model_conflict'
    if hi<1-tol:return 'stable'
    if lo>1+tol:return 'unstable'
    return 'inconclusive'


def response_intervals(probes,prices,alpha:float=.05)->dict:
    u=np.asarray(probes,dtype=float);Y=np.asarray(prices,dtype=float)
    if u.ndim!=1 or len(u)<4 or Y.ndim!=2 or Y.shape[0]!=len(u) or Y.shape[1]<3 or not np.isfinite(Y).all() or not np.isfinite(u).all() or not 0<alpha<1:
        raise ValueError('finite episode-by-horizon prices and scalar inputs required')
    uc=u-u.mean();ss=float(uc@uc)
    if ss<=0:raise ValueError('probe variation required')
    beta=uc@Y/ss;intercept=Y.mean(axis=0)-u.mean()*beta
    resid=Y-intercept[None,:]-u[:,None]*beta[None,:]
    covariance=(resid.T@resid)/(len(u)-2)/ss
    se=np.sqrt(np.maximum(0,np.diag(covariance)))
    z=float(student_t.ppf(1-alpha/(2*Y.shape[1]),len(u)-2))
    # Tiny outward arithmetic guard, unrelated to the statistical uncertainty.
    rad=z*se+1e-14
    return {'estimate':beta,'lower':beta-rad,'upper':beta+rad,'se':se,
            'covariance':covariance,'intercept':intercept,'critical_value':z,
            'episodes':len(u),'df':len(u)-2,'alpha':alpha}


def deconvolve(response)->dict:
    b=np.asarray(response,dtype=float)
    if b.ndim!=1 or len(b)<3 or not np.isfinite(b).all() or b[0]<=0:
        raise ValueError('positive initial response and >=3 coefficients required')
    h=b/b[0];a=h[1];k=[]
    for n in range(len(b)-2):
        k.append(h[n+2]-a*h[n+1]-sum(k[j]*h[n-j] for j in range(n)))
    return {'impact':b[0],'a':a,'kernel':np.array(k)}


@lru_cache(maxsize=64)
def bin_basis(count:int,floor:float,bins:int):
    if not 0<floor<=1 or bins<2:raise ValueError('valid floor and >=2 bins required')
    if floor==1:
        lo=np.zeros((count,1));lo[0,0]=1
        return lo,lo.copy()
    edges=np.geomspace(floor,1,bins+1);l=edges[:-1][None,:];r=edges[1:][None,:]
    j=np.arange(count)[:,None];peak=np.clip(1/(j+1),l,r)
    blo=np.minimum(l*(1-l)**j,r*(1-r)**j)
    bhi=peak*(1-peak)**j
    return np.maximum(0,blo-1e-13),bhi+1e-13


def recurrence_constraints(lower,upper,eta_floor:float,bins:int=64):
    L,U=_arrays(lower,upper)
    if not 0<eta_floor<=1:raise ValueError('floor in (0,1] required')
    if np.any(U<0):return None,'model_conflict'
    if L[0]<=0:return None,'insufficient_impact'
    L=np.maximum(0,L)
    # Normalize the whole rectangle by a known constant, not an estimated ratio.
    scale=max(float(U.max()),float(U[0]),1e-12);L=L/scale;U=U/scale
    n=len(L)-1;tl,tu=bin_basis(n,float(eta_floor),bins);m=tl.shape[1]
    # lower/upper convolution, t=0 has no memory term.
    CL=np.zeros((n,m));CU=np.zeros((n,m))
    for t in range(1,n):
        CL[t]=L[t-1::-1]@tl[:t]
        CU[t]=U[t-1::-1]@tu[:t]
    Mlo=np.column_stack((L[:-1],CL));Mhi=np.column_stack((U[:-1],CU))
    arow=np.zeros(m+1);arow[0]=1
    cap=1+max(0,float(U[2]))/(eta_floor*float(L[0]))
    A=np.vstack((Mlo,-Mhi,arow,np.ones(m+1)))
    rhs=np.r_[U[1:],-L[1:],1.,cap]+1e-13
    return (A,rhs,len(rhs)-1),'ok'


def _guard(A,b,res,c,anchor):
    y=np.maximum(0,-np.asarray(res.ineqlin.marginals))
    Al=A.astype(np.longdouble);yl=y.astype(np.longdouble);cl=c.astype(np.longdouble)
    missing=float(max(0,np.max(cl-Al.T@yl)))+2e-10
    y[anchor]+=missing # Anchor row has all coefficients equal to one.
    upper=float(b.astype(np.longdouble)@y.astype(np.longdouble))+1e-9
    dv=float(max(0,np.max(cl-Al.T@y.astype(np.longdouble))))
    pv=float(max(0,np.max(A@res.x-b)))
    return upper,dv,pv,missing


def recurrence_interval(lower,upper,eta_floor:float,bins:int=64,
                        method:str='highs-ds')->dict:
    prepared,status=recurrence_constraints(lower,upper,eta_floor,bins)
    base={'lower':0.,'upper':float('inf'),'label':'inconclusive','status':status,
          'dual_violation':0.,'primal_violation':0.,'repair':0.}
    if prepared is None:
        if status=='model_conflict':base.update(lower=float('nan'),upper=float('nan'),label='model_conflict')
        return base
    A,b,anchor=prepared;c=np.ones(A.shape[1])
    opt={'presolve':True,'primal_feasibility_tolerance':1e-9,'dual_feasibility_tolerance':1e-9,'time_limit':15.}
    rlo=linprog(c,A_ub=A,b_ub=b,bounds=(0,None),method=method,options=opt)
    rhi=linprog(-c,A_ub=A,b_ub=b,bounds=(0,None),method=method,options=opt)
    if not rlo.success or not rhi.success:
        if rlo.status==2 or rhi.status==2:
            base.update(status='model_conflict',label='model_conflict',lower=float('nan'),upper=float('nan'))
        else:base.update(status='solver_failure')
        return base
    neglo,d1,p1,z1=_guard(A,b,rlo,-c,anchor);hi,d2,p2,z2=_guard(A,b,rhi,c,anchor)
    lo=max(0,-neglo)
    if max(d1,d2)>1e-9 or max(p1,p2)>2e-7:
        base.update(status='numerical_failure');return base
    base.update(lower=lo,upper=hi,label=label(lo,hi),status='ok',
                dual_violation=max(d1,d2),primal_violation=max(p1,p2),repair=max(z1,z2))
    return base


def deconvolution_interval(lower,upper,eta_floor:float)->dict:
    L,U=_arrays(lower,upper)
    if not 0<eta_floor<=1:raise ValueError('invalid rate floor')
    if np.any(U<0):return {'lower':float('nan'),'upper':float('nan'),'label':'model_conflict'}
    if L[0]<=0:return {'lower':0.,'upper':float('inf'),'label':'inconclusive'}
    hl=np.maximum(0,L)/U[0];hu=U/L[0];hl[0]=hu[0]=1
    al=max(0,float(hl[1]));au=min(1.,float(hu[1]))
    if al>au:return {'lower':float('nan'),'upper':float('nan'),'label':'model_conflict'}
    kl=[];ku=[]
    for n in range(len(L)-2):
        low=hl[n+2]-au*hu[n+1]-sum(ku[j]*hu[n-j] for j in range(n))
        high=hu[n+2]-al*hl[n+1]-sum(kl[j]*hl[n-j] for j in range(n))
        if high<-1e-10:return {'lower':float('nan'),'upper':float('nan'),'label':'model_conflict'}
        kl.append(max(0,low-1e-12));ku.append(max(0,high+1e-12))
    M=len(kl);frac=1 if eta_floor==1 else -np.expm1(M*np.log1p(-eta_floor))
    lo=al+sum(kl)
    hi=au+min(sum(ku)/frac,sum(ku)+(1-eta_floor)/eta_floor*ku[-1])
    return {'lower':lo,'upper':hi,'label':label(lo,hi)}


def recurrence_point(response,eta_floor:float,nodes:int=33)->dict:
    """Conventional constrained recurrence least squares; NOT a certificate.

    Measured responses appear on both sides (errors in variables). Stability
    is not imposed. This is not a claim to best nonlinear output-error fitting.
    """
    b=np.asarray(response,dtype=float)
    if len(b)<3 or not 0<eta_floor<=1:raise ValueError('invalid response or floor')
    rates=np.geomspace(eta_floor,1,nodes) if eta_floor<1 else np.array([1.])
    n=len(b)-1;basis=rates[None,:]*(1-rates[None,:])**np.arange(n)[:,None]
    C=np.zeros((n,len(rates)))
    for t in range(1,n):C[t]=b[t-1::-1]@basis[:t]
    A=np.column_stack((b[:-1],C));scale=np.maximum(np.linalg.norm(A,axis=0),1e-15)
    upper=np.full(A.shape[1],np.inf);upper[0]=scale[0]
    fit=lsq_linear(A/scale,b[1:],bounds=(0,upper),method='bvls',tol=1e-10,max_iter=300)
    coef=fit.x/scale;g=float(coef.sum())
    return {'gain':g,'label':label(g,g),'status':'ok' if fit.success else 'solver_failure',
            'residual':float(np.linalg.norm(A@coef-b[1:])), 'a_fit':float(coef[0])}
