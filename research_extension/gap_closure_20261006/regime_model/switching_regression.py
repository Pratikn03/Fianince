"""Segmented Gaussian switching regression, with exact posterior transitions.

A conditional scalar regression, not a structural VAR or causal learning test.
Transition matrix convention: rows are previous states, columns next states.
Reference: Rabiner (1989), https://doi.org/10.1109/5.18626, equations 37-40.
"""
import numpy as np
from scipy.special import logsumexp


def forward_backward_python(log_emission, transition, initial):
    e=np.asarray(log_emission,float);P=np.asarray(transition,float);pi=np.asarray(initial,float)
    if e.ndim!=2 or len(e)==0 or P.shape!=(e.shape[1],e.shape[1]):
        raise ValueError('Invalid dimensions')
    if not np.all(np.isfinite(e)) or np.any(P<=0) or np.any(pi<=0):
        raise ValueError('Require finite emissions and strictly positive probabilities')
    if not np.allclose(P.sum(1),1) or not np.isclose(pi.sum(),1):
        raise ValueError('Probabilities must sum to one')
    logP=np.log(P);n,k=e.shape;alpha=np.empty_like(e);beta=np.zeros_like(e)
    alpha[0]=np.log(pi)+e[0]
    for t in range(1,n):alpha[t]=e[t]+logsumexp(alpha[t-1][:,None]+logP,axis=0)
    ll=float(logsumexp(alpha[-1]))
    for t in range(n-2,-1,-1):beta[t]=logsumexp(logP+e[t+1][None,:]+beta[t+1][None,:],axis=1)
    gamma=np.exp(alpha+beta-ll)
    xi=np.empty((n-1,k,k))
    for t in range(n-1):xi[t]=np.exp(alpha[t][:,None]+logP+e[t+1][None,:]+beta[t+1][None,:]-ll)
    return {'log_likelihood':ll,'posterior':gamma,'pair_posterior':xi,
            'filtered':np.exp(alpha-logsumexp(alpha,axis=1)[:,None])}


# Optional compiled two-state implementation; checked against the Python reference.
import ctypes
from pathlib import Path
_BACKEND=None
_backend_path=Path(__file__).with_name('hmm2.so')
if _backend_path.exists():
    _BACKEND=ctypes.CDLL(str(_backend_path))
    _PTR=ctypes.POINTER(ctypes.c_double)
    _BACKEND.hmm2.argtypes=[ctypes.c_long]+[_PTR]*7
    _BACKEND.hmm2.restype=ctypes.c_int

def forward_backward(log_emission,transition,initial):
    e=np.ascontiguousarray(log_emission,dtype=float)
    P=np.ascontiguousarray(transition,dtype=float);pi=np.ascontiguousarray(initial,dtype=float)
    if _BACKEND is None or e.ndim!=2 or e.shape[1]!=2:
        return forward_backward_python(e,P,pi)
    if len(e)==0 or P.shape!=(2,2) or pi.shape!=(2,) or not np.isfinite(e).all() or np.any(P<=0) or np.any(pi<=0) or not np.isfinite(P).all() or not np.isfinite(pi).all() or not np.allclose(P.sum(1),1) or not np.isclose(pi.sum(),1):
        raise ValueError('Invalid emission/probability arrays')
    n=len(e);g=np.empty_like(e);xi=np.empty((n-1,2,2));filtered=np.empty_like(e);ll=np.empty(1)
    arrays=[e,P,pi,g,xi,filtered,ll]
    # n + seven double pointers.
    if _BACKEND.hmm2(n,*[v.ctypes.data_as(_PTR) for v in arrays]):
        raise MemoryError('HMM backend allocation failed')
    return {'log_likelihood':float(ll[0]),'posterior':g,'pair_posterior':xi,'filtered':filtered}

def emissions(X,y,beta,variance):
    residual=np.asarray(y)[:,None]-np.asarray(X)@np.asarray(beta).T
    return -.5*(np.log(2*np.pi*np.asarray(variance))[None,:]+residual**2/variance)


def expectation(segments,beta,variance,transition,initial):
    fits=[forward_backward(emissions(X,y,beta,variance),transition,initial) for X,y in segments]
    return sum(f['log_likelihood'] for f in fits),fits


def fit(segments,seed=0,shared_beta=False,max_iter=300,tol=1e-7,variance_floor=1e-6):
    """EM with independent segment starts; floor is in standardized target units.

    The variance floor prevents unbounded mixture likelihood. It is a declared
    model constraint and needs sensitivity analysis, not a market noise estimate.
    Free segment-start distribution is fitted from initial-state posteriors.
    """
    if not segments or variance_floor<=0:raise ValueError('Require segments and positive variance floor')
    for X,y in segments:
        if X.ndim!=2 or len(y)!=len(X) or len(y)<2 or not np.isfinite(X).all() or not np.isfinite(y).all():
            raise ValueError('Require finite aligned segments of at least two observations')
    X=np.vstack([v[0] for v in segments]);y=np.concatenate([v[1] for v in segments]);p=X.shape[1]
    if np.linalg.matrix_rank(X)!=p:raise ValueError('Regressors must have full column rank')
    rng=np.random.default_rng(seed);ols=np.linalg.lstsq(X,y,rcond=None)[0]
    beta=np.tile(ols,(2,1))
    if not shared_beta:beta+=rng.normal(0,.08,beta.shape)
    var=max(float(np.mean((y-X@ols)**2)),variance_floor)
    variance=var*np.array([rng.uniform(.25,.7),rng.uniform(1.3,2.5)]);variance=np.maximum(variance,variance_floor)
    p0,p1=rng.uniform(.7,.98,size=2);transition=np.array([[p0,1-p0],[1-p1,p1]]);initial=np.array([.5,.5])
    history=[];converged=False
    ll,fits=expectation(segments,beta,variance,transition,initial);history.append(ll)
    for iteration in range(max_iter):
        gamma=np.vstack([v['posterior'] for v in fits])
        counts=sum((v['pair_posterior'].sum(0) for v in fits),start=np.zeros((2,2)))
        if np.any(counts.sum(1)<1e-12) or np.any(gamma.sum(0)<1e-12):
            return {'status':'COLLAPSED_STATE','history':history}
        nextP=counts/counts.sum(1)[:,None]
        nextpi=np.mean([v['posterior'][0] for v in fits],axis=0)
        # Positive machine floor only; no imposed persistence bounds.
        nextP=np.maximum(nextP,1e-300);nextP/=nextP.sum(1)[:,None]
        nextpi=np.maximum(nextpi,1e-300);nextpi/=nextpi.sum()
        nextbeta=np.empty_like(beta)
        if shared_beta:
            weight=np.sum(gamma/variance[None,:],axis=1);w=np.sqrt(weight)
            common=np.linalg.lstsq(X*w[:,None],y*w,rcond=None)[0];nextbeta[:]=common
        else:
            for k in range(2):
                w=np.sqrt(gamma[:,k]);nextbeta[k]=np.linalg.lstsq(X*w[:,None],y*w,rcond=None)[0]
        nextvar=np.maximum(np.sum(gamma*(y[:,None]-X@nextbeta.T)**2,axis=0)/gamma.sum(0),variance_floor)
        nextll,nextfits=expectation(segments,nextbeta,nextvar,nextP,nextpi)
        if nextll<ll-1e-7*(1+abs(ll)):raise ArithmeticError('EM likelihood decreased')
        history.append(nextll)
        gain=nextll-ll;beta,variance,transition,initial=nextbeta,nextvar,nextP,nextpi
        ll,fits=nextll,nextfits
        if gain>=-1e-9 and abs(gain)<tol*(1+abs(ll)):converged=True;break
    order=np.argsort(variance)
    # Final likelihood corresponds to exactly the returned parameter set.
    return {'status':'CONVERGED' if converged else 'ITERATION_LIMIT','log_likelihood':ll,
            'history':history,'beta':beta[order],'variance':variance[order],
            'transition':transition[np.ix_(order,order)],'initial':initial[order],
            'posterior':[f['posterior'][:,order] for f in fits],
            'variance_floor':variance_floor,'shared_beta':shared_beta,'n':len(y),
            'scope':'Conditional Gaussian scalar switching regression; no structural identification'}
