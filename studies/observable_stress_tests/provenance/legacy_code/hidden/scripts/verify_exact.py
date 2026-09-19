#!/usr/bin/env python3
"""Separate standard-library-only exact-arithmetic verifier.

This is a second implementation in the same project, NOT an external researcher.
It neither imports NumPy nor imports the primary simulation package.
"""
import argparse
from fractions import Fraction as F
import json
from math import prod
from pathlib import Path


def impulse(a,q,r,T):
    x=F(1); y=[F(0)]*len(q); h=[x]
    for _ in range(T):
        nx=a*x+sum(y)
        y=[ri*yi+(1-ri)*qi*x for yi,qi,ri in zip(y,q,r)]
        x=nx;h.append(x)
    return h


def verify(p):
    a=F(p['a']);r=list(map(F,p['nodes']));K=len(r)-1
    w=[F(1)/prod(ri-rj for j,rj in enumerate(r) if j!=i) for i,ri in enumerate(r)]
    assert list(map(str,w))==p['weights']
    for j in range(K):assert sum(wi*ri**j for wi,ri in zip(w,r))==0
    assert sum(wi*ri**K for wi,ri in zip(w,r))==1
    assert sum(wi/(1-ri) for wi,ri in zip(w,r))==F(1)/prod(1-ri for ri in r)
    qm=list(map(F,p['q_minus']));qp=list(map(F,p['q_plus']));scale=F(p['scale'])
    assert all(qi>=0 for qi in qm+qp)
    assert all(0<1-ri<=1 for ri in r)
    assert sum(qm)==F(p['Q_minus']) and sum(qp)==F(p['Q_plus'])
    assert a+sum(qm)<1<a+sum(qp)
    for j in range(K):
        km=sum(qi*(1-ri)*ri**j for qi,ri in zip(qm,r))
        kp=sum(qi*(1-ri)*ri**j for qi,ri in zip(qp,r))
        assert km==kp
    hm=impulse(a,qm,r,K+2);hp=impulse(a,qp,r,K+2)
    assert hm[:K+2]==hp[:K+2]
    assert hp[K+2]-hm[K+2]==scale
    # Independent exact characteristic sign at lambda=1 (Schur complement).
    dm=prod(1-ri for ri in r)*(1-a-sum(qm))
    dp=prod(1-ri for ri in r)*(1-a-sum(qp))
    assert dm>0>dp


def main():
    root=Path(__file__).resolve().parents[1]
    parser=argparse.ArgumentParser()
    parser.add_argument('--results',type=Path,default=root/'results')
    args=parser.parse_args()
    pairs=json.loads((args.results/'exact_witnesses.json').read_text())
    for p in pairs:verify(p)
    verify(json.loads((args.results/'readable_witness.json').read_text()))
    print(json.dumps({'status':'PASS','exact_pairs_verified':len(pairs),
                      'additional_readable_witness':1,'arithmetic':'Python fractions.Fraction',
                      'independence':'separate implementation, same environment/authoring process'},indent=2))

if __name__=='__main__':main()
