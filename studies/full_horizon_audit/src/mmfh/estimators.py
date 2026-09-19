"""Full-horizon positive-mixture estimation and conservative outer intervals.

The public estimators see only normalized noisy taps, their known standard
error, and a rate floor. They never receive true rates, weights, or labels.
"""
from __future__ import annotations
from functools import lru_cache
import math
import numpy as np
from scipy.optimize import nnls, linprog
from scipy.stats import norm

HORIZONS=(4,16,64,256)


def _inputs(k, se, floor):
    k=np.asarray(k,dtype=float)
    if k.ndim!=1 or not k.size or not np.all(np.isfinite(k)):
        raise ValueError('taps must be a nonempty finite one-dimensional array')
    if not np.isfinite(se) or se<0 or not np.isfinite(floor) or not 0<floor<=1:
        raise ValueError('nonnegative standard error and rate floor in (0,1] required')
    return k


def label(lower,upper,tol=1e-8):
    if np.isnan(lower) or np.isnan(upper) or lower>upper+tol:
        return 'model_conflict'
    if upper<1-tol:return 'stable'
    if lower>1+tol:return 'unstable'
    return 'inconclusive'


@lru_cache(maxsize=32)
def rate_grid(floor:float,nodes:int=129):
    if not 0<floor<=1 or nodes<2:raise ValueError('invalid rate grid')
    g=np.geomspace(floor,1.,nodes) if floor<1 else np.array([1.])
    g.setflags(write=False)
    return g


@lru_cache(maxsize=64)
def _dictionary(H,floor,nodes):
    eta=rate_grid(floor,nodes)
    A=eta[None,:]*(1-eta[None,:])**np.arange(H)[:,None]
    scale=np.linalg.norm(A,axis=0)
    D=A/scale[None,:]
    D.setflags(write=False);scale.setflags(write=False)
    return D,scale


def fit_nnls(taps, tap_se:float, eta_floor:float, nodes:int=129,
             maxiter:int=4000):
    """Conventional nonnegative exponential-mixture least squares, all taps.

    Closed-loop stability is NOT imposed. Grid approximation and lack of
    confidence calibration preclude interpreting the point as a certificate.
    """
    k=_inputs(taps,tap_se,eta_floor)
    A,scale=_dictionary(len(k),float(eta_floor),nodes)
    try:
        coef,resid=nnls(A,k,maxiter=maxiter)
    except (RuntimeError,np.linalg.LinAlgError) as err:
        return {'gain':float('nan'),'residual':float('nan'),'label':'inconclusive',
                'status':'solver_failure','message':str(err),'kkt_violation':float('nan')}
    gain=float(np.sum(coef/scale))
    gradient=A.T@(A@coef-k)
    kkt=max(float(max(0,-gradient.min())),float(np.max(np.abs(coef*gradient))))
    return {'gain':gain,'residual':float(resid),'label':label(gain,gain),
            'status':'ok','message':'','kkt_violation':kkt}


def feature_envelopes(edges,indices,kind='tap'):
    """Analytic extrema on continuous learning-rate bins, not a point grid.

    tap j: eta*(1-eta)^j, maximized at eta=1/(j+1).
    sum H: 1-(1-eta)^H, increasing in eta.
    Small outward padding protects ordinary evaluation round-off. This is
    numerical guarding, not an interval-arithmetic proof certificate.
    """
    edges=np.asarray(edges,dtype=float);idx=np.asarray(indices,dtype=int)
    if edges.ndim!=1 or len(edges)<2 or np.any(np.diff(edges)<=0) or edges[0]<=0 or edges[-1]>1:
        raise ValueError('strictly increasing rate edges in (0,1] required')
    if idx.ndim!=1 or np.any(idx<0):raise ValueError('nonnegative feature indices required')
    a=edges[:-1][None,:];b=edges[1:][None,:];j=idx[:,None]
    if kind=='tap':
        va=a*(1-a)**j;vb=b*(1-b)**j
        peak=np.clip(1/(j+1),a,b)
        lower=np.minimum(va,vb);upper=peak*(1-peak)**j
    elif kind=='sum':
        if np.any(idx<1):raise ValueError('sum horizons must be positive')
        with np.errstate(divide='ignore'):
            lower=-np.expm1(j*np.log1p(-a));upper=-np.expm1(j*np.log1p(-b))
    else:raise ValueError('kind must be tap or sum')
    pad=1e-13
    return np.maximum(0.,lower-pad),upper+pad


@lru_cache(maxsize=64)
def _critical_values(alpha,summary_fraction,max_horizon,horizons):
    m=len(horizons)
    zs=float(norm.ppf(1-alpha*summary_fraction/(4*m)))
    zc=float(norm.ppf(1-alpha*(1-summary_fraction)/(2*max_horizon)))
    return zs,zc


def summary_interval(taps,tap_se,eta_floor,alpha=.05,horizons=HORIZONS):
    k=_inputs(taps,tap_se,eta_floor);H=len(k)
    if not 0<alpha<1 or not len(horizons):raise ValueError('invalid confidence parameters')
    z=float(norm.ppf(1-alpha/(4*len(horizons))))
    s=float(k.sum());last=float(k[-1]);sl=s-z*tap_se*np.sqrt(H)
    su=s+z*tap_se*np.sqrt(H);ku=last+z*tap_se
    if su<0 or ku<0:
        return {'lower':float('nan'),'upper':float('nan'),'label':'model_conflict'}
    fraction=1. if eta_floor==1 else -math.expm1(H*math.log1p(-eta_floor))
    lower=max(0.,sl)
    upper=min(su/fraction,su+(1-eta_floor)/eta_floor*ku)
    return {'lower':lower,'upper':upper,'label':label(lower,upper)}


@lru_cache(maxsize=96)
def _outer_matrix(H,floor,bins,horizons):
    if floor==1:
        # Exact single allowed rate; special case handled by a very narrow bin
        # would be an unjustified relaxation. Build exact columns instead.
        bt=np.zeros((H,1));bt[0]=1.
        prefix=np.array([h for h in horizons if h<=H],dtype=int)
        sums=np.ones((len(prefix),1));term=bt[prefix-1]
        A=np.vstack([bt,-bt,sums,-sums,term,-term])
        return A,2*H+len(prefix)-1,prefix
    edges=rate_grid(floor,bins+1)
    tl,tu=feature_envelopes(edges,np.arange(H),'tap')
    prefix=np.array([h for h in horizons if h<=H],dtype=int)
    if not len(prefix) or prefix[-1]!=H:raise ValueError('current horizon must be declared')
    sl,su=feature_envelopes(edges,prefix,'sum')
    kl,ku=feature_envelopes(edges,prefix-1,'tap')
    A=np.vstack([tl,-tu,sl,-su,kl,-ku])
    A.setflags(write=False)
    return A,2*H+len(prefix)-1,prefix


def _dual_bound(A,b,result,c,anchor):
    """Return an upper bound for max c^T w via repaired nonnegative LP dual.

    result solves min -c^T w. A positive sum row allows a small residual to
    be repaired without destroying dual nonnegativity. Validate primal and
    dual residuals; report the repair rather than hide solver tolerances.
    """
    y=np.maximum(0.,-np.asarray(result.ineqlin.marginals))
    longA=A.astype(np.longdouble);longy=y.astype(np.longdouble)
    gap=np.asarray(c,dtype=np.longdouble)-longA.T@longy
    beta=float(A[anchor].min())
    if beta<=0:raise ArithmeticError('dual repair requires a strictly positive row')
    repair=float(max(np.longdouble(0),gap.max())+np.longdouble(2e-10))/beta
    y[anchor]+=repair
    violation=float(max(0.,np.max(np.asarray(c,dtype=np.longdouble)-longA.T@y.astype(np.longdouble))))
    bound=float(np.asarray(b,dtype=np.longdouble)@y.astype(np.longdouble))+1e-9
    primal_violation=float(max(0.,np.max(A@result.x-b)))
    optimal_gap=bound-float(np.asarray(c)@result.x)
    return bound,violation,primal_violation,float(optimal_gap),repair


def moment_interval(taps,tap_se,eta_floor,bins=64,alpha=.05,
                    summary_fraction=.5,horizons=HORIZONS,max_horizon=256,
                    method='highs-ds'):
    """Set-membership positive-mixture outer bounds, using every observed tap.

    The continuum-bin relaxation is an outer feasible set: every genuine
    positive mixture satisfying the simultaneous confidence constraints maps
    to feasible bin masses. Thus finite grid omission cannot falsely narrow
    this interval. Non-identifiable cases may remain inconclusive.
    """
    k=_inputs(taps,tap_se,eta_floor);H=len(k);horizons=tuple(horizons)
    if H>max_horizon or H not in horizons or bins<2 or not 0<summary_fraction<1 or not 0<alpha<1:
        raise ValueError('invalid horizon, grid or confidence allocation')
    zs,zc=_critical_values(alpha,summary_fraction,max_horizon,horizons)
    A,anchor,prefix=_outer_matrix(H,float(eta_floor),bins,horizons)
    sums=np.array([k[:h].sum() for h in prefix]);ser=tap_se*np.sqrt(prefix)
    last=k[prefix-1]
    b=np.r_[k+zc*tap_se,-k+zc*tap_se,sums+zs*ser,-sums+zs*ser,
            last+zs*tap_se,-last+zs*tap_se]
    options={'presolve':True,'primal_feasibility_tolerance':1e-9,
             'dual_feasibility_tolerance':1e-9,'time_limit':10.}
    n=A.shape[1]
    low=linprog(np.ones(n),A_ub=A,b_ub=b,bounds=(0,None),method=method,options=options)
    high=linprog(-np.ones(n),A_ub=A,b_ub=b,bounds=(0,None),method=method,options=options)
    base={'raw_lower':float('nan'),'raw_upper':float('nan'),
          'lower':float('nan'),'upper':float('nan'),'label':'inconclusive',
          'raw_label':'inconclusive','dual_violation':float('nan'),
          'primal_violation':float('nan'),'max_gap':float('nan'),'max_repair':float('nan')}
    if not low.success or not high.success:
        conflict=(low.status==2 or high.status==2)
        base.update(status='model_conflict' if conflict else 'solver_failure',
                    message=f'low:{low.status};high:{high.status}',
                    label='model_conflict' if conflict else 'inconclusive',
                    raw_label='model_conflict' if conflict else 'inconclusive')
        return base
    neg_lower,dv1,pv1,gap1,rep1=_dual_bound(A,b,low,-np.ones(n),anchor)
    upper,dv2,pv2,gap2,rep2=_dual_bound(A,b,high,np.ones(n),anchor)
    lower=max(0.,-neg_lower)
    if max(dv1,dv2)>1e-9 or max(pv1,pv2)>1e-7 or lower>upper+1e-8:
        base.update(status='numerical_failure',message='residual audit failed')
        return base
    budget=summary_interval(k,tap_se,eta_floor,alpha*summary_fraction,horizons)
    combined_lower=max(lower,budget['lower']);combined_upper=min(upper,budget['upper'])
    base.update(raw_lower=lower,raw_upper=upper,lower=combined_lower,upper=combined_upper,
                raw_label=label(lower,upper),label=label(combined_lower,combined_upper),
                status='ok',message='',dual_violation=max(dv1,dv2),
                primal_violation=max(pv1,pv2),max_gap=max(gap1,gap2),max_repair=max(rep1,rep2))
    return base
