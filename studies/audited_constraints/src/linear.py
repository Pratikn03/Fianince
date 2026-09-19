"""Audited linear source: no account-based feedback, exact observable prices."""
from __future__ import annotations
import numpy as np


def probe_orders(rng,episodes:int,steps:int,design:str,gross:float=4.):
    if steps<16 or episodes<4 or gross<=0:raise ValueError('invalid probe specification')
    u=np.zeros((episodes,steps))
    if design=='impulse':
        u[:,0]=rng.choice([-1.,1.],episodes)*gross
    elif design=='single_roundtrip':
        s=rng.choice([-1.,1.],episodes)*gross/2
        u[:,0]=s;u[:,steps-3]=-s
    elif design=='roundtrips':
        times=np.linspace(0,steps-3,8,dtype=int)
        for j in range(4):
            s=rng.choice([-1.,1.],episodes)*gross/8
            u[:,times[2*j]]=s;u[:,times[2*j+1]]=-s
    else:raise ValueError('unknown design')
    return u


def simulate_linear(a,q,rates,impact,episodes,steps,seed,design,noise_sd=.002,
                    reset_sd=0.,sensor_sd=0.,extra_inventory=0.):
    rng=np.random.default_rng(seed);eta=np.asarray(rates);q=np.asarray(q)
    if not 0<=a<1 or impact<=0 or q.shape!=eta.shape or q.ndim!=1 or np.any(q<0) or q.sum()>1.0 or np.any((eta<=0)|(eta>1)):
        raise ValueError('audited positive memory class: 0<=a<1, sum(q)<=1, 0<rates<=1')
    u=probe_orders(rng,episodes,steps,design);noise=rng.normal(0,noise_sd,(episodes,steps))
    mem=rng.normal(0,reset_sd,(episodes,len(eta))) if reset_sd else np.zeros((episodes,len(eta)))
    x=np.zeros(episodes);p=np.empty((episodes,steps));inventory=np.zeros(episodes)
    for t in range(steps):
        new=a*x+mem@q+impact*u[:,t]+noise[:,t]+extra_inventory*inventory
        inventory+=mem@q
        mem=(1-eta)*mem+eta*x[:,None]
        x=new;p[:,t]=x
    if sensor_sd:p=p+rng.normal(0,sensor_sd,p.shape)
    return {'prices':p,'probes':u,'gross_volume':np.abs(u).sum(axis=1),
            'squared_energy':(u*u).sum(axis=1),'peak_probe_inventory':np.abs(np.cumsum(u,axis=1)).max(axis=1)}
