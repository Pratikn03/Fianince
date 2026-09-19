"""Account-consistent synthetic dealer market, not a calibrated order book.

Only ``public`` (probe fills and noisy prices) is supplied to inference.
Hidden states and analytic responses are reserved for evaluation.
"""
from __future__ import annotations
from dataclasses import dataclass
import numpy as np

@dataclass(frozen=True)
class MarketConfig:
    a: float
    impact: float
    rates: tuple[float,...]
    q: tuple[float,...]
    noise_flow_sd: float=.10
    quote_noise_sd: float=.002
    initial_memory_sd: float=.01
    fundamental_price: float=100.
    half_spread: float=.005
    nonlinear_capacity: float|None=None

    def validate(self):
        eta=np.asarray(self.rates);q=np.asarray(self.q)
        if not 0<=self.a<1 or self.impact<=0 or eta.ndim!=1 or not len(eta) or eta.shape!=q.shape:
            raise ValueError('invalid dimensions or market coefficients')
        if np.any((eta<=0)|(eta>1)) or np.any(q<0):
            raise ValueError('positive-rate, nonnegative-feedback model required')
        if min(self.noise_flow_sd,self.quote_noise_sd,self.initial_memory_sd,self.half_spread)<0:
            raise ValueError('scales cannot be negative')
        if self.nonlinear_capacity is not None and self.nonlinear_capacity<=0:
            raise ValueError('nonlinear capacity must be positive')


def joint_matrix(a:float,q:np.ndarray,rates:np.ndarray)->np.ndarray:
    n=len(rates);J=np.zeros((n+1,n+1));J[0,0]=a;J[0,1:]=1
    J[1:,0]=rates*q;J[1:,1:]=np.diag(1-rates)
    return J


def impulse(a:float,q:np.ndarray,rates:np.ndarray,impact:float,steps:int)->np.ndarray:
    J=joint_matrix(a,np.asarray(q),np.asarray(rates));state=np.zeros(len(q)+1)
    state[0]=impact;b=[]
    for _ in range(steps):
        b.append(state[0]);state=J@state
    return np.asarray(b)


def simulate(cfg:MarketConfig,episodes:int,amplitude:float,steps:int,seed:int,
             audit:bool=False,confounded:bool=False)->dict:
    cfg.validate()
    if episodes<4 or episodes%2 or amplitude<=0 or steps<3:
        raise ValueError('even episode count >=4, positive amplitude, >=3 steps required')
    rng=np.random.default_rng(seed);eta=np.array(cfg.rates);q=np.array(cfg.q);n=len(q)
    memory=rng.normal(0,cfg.initial_memory_sd,(episodes,n))
    flow=rng.normal(0,cfg.noise_flow_sd,(episodes,steps))
    sensor=rng.normal(0,cfg.quote_noise_sd,(episodes,steps))
    signs=np.tile([-1.,1.],episodes//2);rng.shuffle(signs)
    if confounded:
        # Deliberately invalid randomization: assignment depends on disturbances.
        rank=np.argsort(flow[:,:min(8,steps)].sum(axis=1))
        signs=np.ones(episodes);signs[rank[:episodes//2]]=-1.
    probes=amplitude*signs
    x=np.zeros(episodes);prices=np.empty((episodes,steps))
    chi=q/cfg.impact;phi=(1-cfg.a)/cfg.impact
    # Actors: each chartist, fundamentalist, noise trader, probe trader, dealer.
    inventory=np.zeros((episodes,n+4));cash=np.zeros_like(inventory)
    max_cash=max_shares=max_marked=max_inventory=max_order=max_displacement=0.
    total_volume=total_spread=0.
    for t in range(steps):
        qt=memory*chi[None,:]
        qf=-phi*x;qn=flow[:,t];qu=probes if t==0 else np.zeros(episodes)
        orders=np.column_stack((qt,qf,qn,qu));net=orders.sum(axis=1)
        change=cfg.impact*net
        if cfg.nonlinear_capacity is not None:
            change=cfg.impact*cfg.nonlinear_capacity*np.tanh(net/cfg.nonlinear_capacity)
        nxt=x+change
        if audit:
            execution=cfg.fundamental_price+(x+nxt)/2
            spread=cfg.half_spread*np.abs(orders)
            inventory[:,:-1]+=orders;inventory[:,-1]-=net
            transfers=orders*execution[:,None]+spread
            cash[:,:-1]-=transfers;cash[:,-1]+=transfers.sum(axis=1)
            max_cash=max(max_cash,float(np.abs(cash.sum(axis=1)).max()))
            max_shares=max(max_shares,float(np.abs(inventory.sum(axis=1)).max()))
            marked=cash+inventory*(cfg.fundamental_price+nxt)[:,None]
            max_marked=max(max_marked,float(np.abs(marked.sum(axis=1)).max()))
            max_inventory=max(max_inventory,float(np.abs(inventory[:,-1]).max()))
            max_order=max(max_order,float(np.abs(net).max()))
            total_volume+=float(np.abs(orders).sum())
            total_spread+=float(spread.sum())
        # Timing is important: updating uses the old observed deviation x_t.
        memory=(1-eta)[None,:]*memory+eta[None,:]*x[:,None]
        x=nxt;prices[:,t]=x+sensor[:,t]
        max_displacement=max(max_displacement,float(np.abs(x).max()))
    public={'probes':probes,'prices':prices}
    return {'public':public,'probes':probes,'prices':prices,
            'audit':{'max_cash_error':max_cash,'max_share_error':max_shares,
                     'max_marked_wealth_error':max_marked,'max_dealer_inventory':max_inventory,
                     'max_net_order':max_order,'max_price_displacement':max_displacement,
                     'total_absolute_volume':total_volume,'total_spread_transfer':total_spread,
                     'episodes':episodes,'steps':steps}}
