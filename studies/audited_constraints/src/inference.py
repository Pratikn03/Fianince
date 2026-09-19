"""Inference receives public observations only. Each row is an independent episode."""
from __future__ import annotations
import numpy as np
from scipy.stats import t as student_t, beta


def reconstruct_terminal(prices,rates):
    """prices[:,t] = deviation x_(t+1); initial x_0=m_0=0 is audited.

    Regression: x_T ~ 1 + x_(T-1) + m_(T-1), with u_(T-1)=0.
    The filters are reconstructed from prices, never read from latent storage.
    """
    p=np.asarray(prices,dtype=float);eta=np.asarray(rates,dtype=float)
    if p.ndim!=2 or p.shape[1]<3 or not np.isfinite(p).all() or eta.ndim!=1 or not len(eta) or np.any((eta<=0)|(eta>1)):
        raise ValueError('finite price matrix and valid rates required')
    mem=np.zeros((len(p),len(eta)))
    # After observing x_(T-2), reconstruct m_(T-1).
    for t in range(p.shape[1]-2):
        mem=(1-eta)*mem+eta*p[:,t,None]
    return np.column_stack([np.ones(len(p)),p[:,-2],mem]),p[:,-1].copy()


def terminal_interval(X,y,alpha:float=.05)->dict:
    X=np.asarray(X,dtype=float);y=np.asarray(y,dtype=float)
    base={'estimate':float('nan'),'lower':-float('inf'),'upper':float('inf'),'label':'inconclusive','status':'invalid_design','se':float('inf')}
    if X.ndim!=2 or y.shape!=(len(X),) or not np.isfinite(X).all() or not np.isfinite(y).all() or not 0<alpha<1:raise ValueError('finite regression arrays required')
    n,d=X.shape
    if n<=d:return base
    # Scale columns before QR to avoid a numeric penalty for slowly updating filters.
    scales=np.linalg.norm(X,axis=0)
    if np.any(scales<=0):return base
    Z=X/scales
    if np.linalg.matrix_rank(Z)<d:return base
    Q,R=np.linalg.qr(Z,mode='reduced')
    coef=np.linalg.solve(R,Q.T@y)/scales
    e=y-X@coef;s2=float(e@e/(n-d))
    contrast=np.ones(d);contrast[0]=0
    v=np.linalg.solve(R.T,contrast/scales)
    se=float(np.sqrt(max(0,s2)*np.dot(v,v)))
    est=float(contrast@coef);critical=float(student_t.ppf(1-alpha/2,n-d))
    rad=critical*se+1e-12;lo=est-rad;hi=est+rad
    label='stable' if hi<1 else ('unstable' if lo>1 else 'inconclusive')
    return {'estimate':est,'lower':lo,'upper':hi,'label':label,'status':'ok','se':se,
            'df':n-d,'coefficient_estimates':coef.tolist(),'condition_number_scaled':float(np.linalg.cond(Z))}


def binomial_interval(successes:int,trials:int,alpha:float=.05)->tuple[float,float]:
    if not isinstance(successes,(int,np.integer)) or not isinstance(trials,(int,np.integer)) or trials<1 or not 0<=successes<=trials or not 0<alpha<1:
        raise ValueError('integer binomial counts and valid alpha required')
    lo=0. if successes==0 else float(beta.ppf(alpha/2,successes,trials-successes+1))
    hi=1. if successes==trials else float(beta.ppf(1-alpha/2,successes+1,trials-successes))
    return lo,hi


def label_probability(lower:float,upper:float,threshold:float=.05)->str:
    if not 0<=lower<=upper<=1 or not 0<threshold<1:raise ValueError('invalid probability interval')
    return 'below_threshold' if upper<threshold else ('above_threshold' if lower>threshold else 'inconclusive')


def variable_terminal(prices,endpoints,rates):
    """One preassigned endpoint per episode. No samples after it are used."""
    p=np.asarray(prices,float);T=np.asarray(endpoints)
    if p.ndim!=2 or T.shape!=(len(p),) or not np.issubdtype(T.dtype,np.integer) or np.any((T<3)|(T>p.shape[1])):
        raise ValueError('valid integer endpoint for every public price path required')
    X=np.empty((len(p),len(rates)+2));y=np.empty(len(p))
    for t in np.unique(T):
        ix=np.flatnonzero(T==t);xx,yy=reconstruct_terminal(p[ix,:int(t)],rates)
        X[ix]=xx;y[ix]=yy
    return X,y


def contrast_interval(X,y,contrast,alpha=.05):
    """Exact Gaussian terminal-row interval for a predeclared linear contrast."""
    X=np.asarray(X,float);y=np.asarray(y,float);c=np.asarray(contrast,float)
    if X.ndim!=2 or y.shape!=(len(X),) or c.shape!=(X.shape[1],) or not np.isfinite(c).all() or not 0<alpha<1:
        raise ValueError('invalid linear contrast')
    n,d=X.shape
    if n<=d or np.linalg.matrix_rank(X)<d:return {'estimate':float('nan'),'lower':-float('inf'),'upper':float('inf')}
    scale=np.linalg.norm(X,axis=0);Q,R=np.linalg.qr(X/scale,mode='reduced')
    b=np.linalg.solve(R,Q.T@y)/scale;e=y-X@b;v=np.linalg.solve(R.T,c/scale)
    se=np.sqrt(max(0,float(e@e/(n-d)))*float(v@v));hat=float(c@b);rad=float(student_t.isf(alpha/2,n-d)*se)+1e-12
    return {'estimate':hat,'lower':hat-rad,'upper':hat+rad,'se':se}
