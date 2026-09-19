"""Exact truncated-moment construction. Uses no fitted data or numerical nullspace."""
from fractions import Fraction
from math import prod
import numpy as np
from .model import Market


def construct_pair(a: Fraction, nodes: list[Fraction]) -> dict:
    a = Fraction(a)
    r = [Fraction(x) for x in nodes]
    if not (0 <= a < 1) or len(r) < 2:
        raise ValueError('need a in [0,1) and at least two nodes')
    if r != sorted(r) or len(set(r)) != len(r) or not (0 <= r[0] < r[-1] < 1):
        raise ValueError('nodes must be distinct increasing rationals in [0,1)')
    K = len(r)-1
    w = [Fraction(1)/prod(ri-rj for j,rj in enumerate(r) if i != j)
         for i,ri in enumerate(r)]
    mu_plus = [max(wi, Fraction(0)) for wi in w]
    mu_minus = [max(-wi, Fraction(0)) for wi in w]
    Qp = sum(m/(1-ri) for m,ri in zip(mu_plus,r))
    Qm = sum(m/(1-ri) for m,ri in zip(mu_minus,r))
    if not Qp > Qm > 0:
        raise ArithmeticError('partial-fraction identity failed')
    scale = 2*(1-a)/(Qp+Qm)
    qp = [scale*m/(1-ri) for m,ri in zip(mu_plus,r)]
    qm = [scale*m/(1-ri) for m,ri in zip(mu_minus,r)]
    residuals = [sum(wi*ri**j for wi,ri in zip(w,r)) for j in range(K)]
    assert all(value == 0 for value in residuals)
    assert sum(wi*ri**K for wi,ri in zip(w,r)) == 1
    assert sum(wi/(1-ri) for wi,ri in zip(w,r)) == Fraction(1)/prod(1-ri for ri in r)
    return {
        'K': K, 'a': str(a), 'nodes': list(map(str,r)),
        'weights': list(map(str,w)), 'scale': str(scale),
        'q_minus': list(map(str,qm)), 'q_plus': list(map(str,qp)),
        'Q_minus': str(sum(qm)), 'Q_plus': str(sum(qp)),
        'moment_residuals': list(map(str,residuals)),
        'first_unmatched_kernel_difference': str(scale),
    }


def _active_market(a: float, q: list[Fraction], eta: list[Fraction], target: int) -> Market:
    """Match counts by splitting positive agents into equivalent same-rate copies."""
    active = [(qi,ei) for qi,ei in zip(q,eta) if qi > 0]
    while len(active) < target:
        i = max(range(len(active)), key=lambda index: active[index][0])
        qi,ei=active.pop(i)
        active.extend([(qi/2,ei),(qi/2,ei)])
    return Market(a,np.array([float(qi) for qi,_ in active]),
                  np.array([float(ei) for _,ei in active]))


def to_markets(pair: dict) -> tuple[Market,Market]:
    eta = [1-Fraction(x) for x in pair['nodes']]
    target = len(eta)
    return tuple(_active_market(float(Fraction(pair['a'])),
                                list(map(Fraction,pair[key])),eta,target)
                 for key in ['q_minus','q_plus'])
