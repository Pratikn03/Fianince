"""Finite-window quantity gate for an explicit linear monetary-output contract.
No market calibration, stochastic coverage, rolling reset or compliance assertion.
"""
import numpy as np


def response(J,C,H,z0,horizon):
    J=np.asarray(J,float);C=np.asarray(C,float).reshape(-1);H=np.asarray(H,float).reshape(-1);z=np.asarray(z0,float).reshape(-1)
    n=len(z)
    if J.shape!=(n,n) or C.shape!=(n,) or H.shape!=(n,) or not np.isfinite(np.r_[J.ravel(),C,H,z]).all():raise ValueError('Finite, aligned scalar-input/output arrays required')
    if not np.isfinite(horizon) or horizon<1 or int(horizon)!=horizon:raise ValueError('Positive integer horizon required')
    horizon=int(horizon)
    power=np.eye(n);baseline=[];kernel=[]
    for t in range(horizon+1):
        baseline.append(float(C@power@z))
        if t<horizon:kernel.append(float(C@power@H))
        power=power@J
    prefix=np.maximum.accumulate(np.abs(kernel))
    return np.array(baseline),np.array(kernel),prefix


def quantity_gate(J,C,H,z0,horizon,budget,other_reserve=0,cost_per_quantity=0,seconds=1,criterion='absolute'):
    if criterion not in ['absolute','loss']:raise ValueError('Unknown output criterion')
    if not np.isfinite([budget,other_reserve,cost_per_quantity,seconds]).all() or min(budget,other_reserve,cost_per_quantity)<0 or seconds<=0:raise ValueError('Invalid monetary or clock contract')
    baseline,kernel,gains=response(J,C,H,z0,horizon)
    background=np.abs(baseline) if criterion=='absolute' else baseline
    available=budget-other_reserve
    result={'criterion':criterion,'horizon':horizon,'seconds':seconds,'budget':budget,'other_reserve':other_reserve,'cost_per_quantity':cost_per_quantity,'baseline':baseline,'kernel':kernel,'prefix_gains':gains,'initial_condition_included':True}
    if np.any(background>available):
        return dict(result,status='BACKGROUND_ALREADY_EXCEEDS_BUDGET',quantity_cap=None,quantity_rate_cap=None)
    denominators=gains+cost_per_quantity;active=denominators>0
    if not active.any():
        return dict(result,status='UNBOUNDED_BY_THIS_OUTPUT_CONTRACT',quantity_cap=None,quantity_rate_cap=None)
    caps=(available-background[1:][active])/denominators[active];cap=float(caps.min())
    return dict(result,status='FINITE_CONDITIONAL_GATE',quantity_cap=cap,quantity_rate_cap=cap/seconds)


def worst_envelope(baseline,prefix_gains,volume,cost_per_quantity=0,other_reserve=0,criterion='absolute'):
    if volume<0 or cost_per_quantity<0 or other_reserve<0:raise ValueError('Negative budget inputs')
    b=np.asarray(baseline,float);g=np.asarray(prefix_gains,float)
    background=np.abs(b) if criterion=='absolute' else b
    return np.r_[background[0]+other_reserve,background[1:]+other_reserve+(g+cost_per_quantity)*volume]
