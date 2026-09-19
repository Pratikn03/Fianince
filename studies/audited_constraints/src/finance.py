"""Binding synthetic balance sheets and explicit bilateral dealer settlement.

This is NOT an exchange order book, calibrated economy or a deployment tool.
"""
from __future__ import annotations
import numpy as np


def feasible_orders(cash,inventory,price,desired,equity0,leverage,inventory_cap,credit_multiple,spread):
    C,I,P,D,E0=np.broadcast_arrays(np.asarray(cash,float),np.asarray(inventory,float),np.asarray(price,float),np.asarray(desired,float),np.asarray(equity0,float))
    L=np.asarray(leverage,float);cap=np.asarray(inventory_cap,float);credit=np.asarray(credit_multiple,float)*E0
    if np.any(P<=L*spread) or np.any(P<=0) or np.any(E0<=0) or spread<0:raise ValueError('positive prices/capital and small positive spread required')
    E=C+I*P;default=E<=0
    forced=(np.abs(I)*P>L*np.maximum(E,0)+1e-9)|(np.abs(I)>cap+1e-9)|(C<-credit-1e-9)|default
    sgn=np.where(D>=0,1.,-1.)
    upper=np.minimum(cap-I,(L*E-P*I)/(P+L*spread*sgn))
    upper=np.minimum(upper,(C+credit)/(P+spread*sgn))
    lower=np.maximum(-cap-I,-(L*E+P*I)/(P-L*spread*sgn))
    # For previously feasible accounts, zero lies in this interval. Avoid epsilon trades.
    upper=np.maximum(0,upper);lower=np.minimum(0,lower)
    out=np.minimum(upper,np.maximum(lower,D))
    out=np.where(forced,-I,out) # liquidation debt is preserved, not written off
    return out,forced,default


def settle(cash,inventory,orders,price,spread):
    C=np.asarray(cash,float).copy();I=np.asarray(inventory,float).copy();O=np.asarray(orders,float);P=np.asarray(price,float)
    transfer=O*P[:,None]+spread*np.abs(O)
    C[:,:-1]-=transfer;C[:,-1]+=transfer.sum(axis=1)
    I[:,:-1]+=O;I[:,-1]-=O.sum(axis=1)
    return C,I


def market_panel(gain:float,slow:float,regime:str,shock:float,episodes:int,seed:int,
                 steps:int=64,save_paths:bool=False,preloaded_dealer:bool=False,shock_jitter:float=0.):
    if regime not in ('unlimited','ample','tight'):raise ValueError('unknown funding regime')
    if episodes<1 or steps<17:raise ValueError('invalid episode count/horizon')
    rng=np.random.default_rng(seed);a=.4;impact=.02;eta=np.array([.5,slow]);q=.6*gain*np.array([.6,.4]);spread=.005
    capital=np.array([100.,100.,600.,300.,600.,2000.])
    if regime=='ample':capital*=20
    if preloaded_dealer:
        if regime!='tight':raise ValueError('preloaded stress extension requires tight regime')
        capital[-1]=1000.
    # Four-share round trip: buy/sell +/-2, gross=4, reversal at t=8.
    signs=rng.choice([-1.,1.],episodes);flow=rng.normal(0,.1,(episodes,steps))
    C=np.broadcast_to(capital,(episodes,6)).copy();I=np.zeros_like(C);mem=np.zeros((episodes,2));x=np.zeros(episodes)
    if preloaded_dealer:
        initial_inventory=np.array([0.,0.,-9.,0.,-10.,19.]);I[:]=initial_inventory;C-=100*I
    jumps=shock+rng.normal(0,shock_jitter,episodes) if shock_jitter else np.full(episodes,shock)
    L=np.array([2.,2.,2.,2.,2.,2.]);caps=np.array([3.,3.,15.,10.,10.,30.]);credit=np.ones(6)
    if regime=='ample':caps*=20
    halt=np.zeros(episodes,bool);default=np.zeros(episodes,bool);ever_clip=np.zeros(episodes,bool);ever_margin=np.zeros(episodes,bool)
    peak_eq=C[:,:2].copy();drawdown=np.zeros(episodes);max_disp=np.zeros(episodes);gross=np.zeros(episodes);probe_filled=np.zeros(episodes)
    peak_lev=np.zeros(episodes);liquidations=np.zeros(episodes,int);rejected=np.zeros(episodes);max_cash=max_shares=max_mark=max_fill_violation=0.;nclip=0;nmargin=0;nhalt=0
    paths=[];ledgers=[];initial_cash=float(capital.sum())
    for t in range(steps):
        P=100+x
        if np.any(P<=1):halt|=P<=1
        E=C+I*P[:,None]
        default|=np.any(E<=0,axis=1)
        desired=np.column_stack([mem*q/impact,-(1-a)/impact*x,flow[:,t],np.zeros(episodes)])
        if t==0:desired[:,-1]=2*signs
        if t==8:desired[:,-1]=-2*signs
        if regime=='unlimited':
            orders=desired;forced=np.zeros_like(orders,dtype=bool)
        else:
            orders,forced,df=feasible_orders(C[:,:-1],I[:,:-1],P[:,None],desired,capital[:-1],L[:-1],caps[:-1],credit[:-1],spread)
            # Defaulted non-dealer accounts may liquidate but may not open a new position.
            orders=np.where(E[:,:-1]<=0,-I[:,:-1],orders)
            desired_abs=np.abs(desired);clipped=np.abs(orders-desired)>1e-8
            ever_clip|=np.any(clipped,axis=1);ever_margin|=np.any(forced,axis=1)
            nclip+=int(clipped.sum());nmargin+=int(forced.sum());liquidations+=forced.sum(axis=1)
            net=orders.sum(axis=1)
            dealer_cap,df_forced,df_default=feasible_orders(C[:,-1],I[:,-1],P,-net,np.full(episodes,capital[-1]),L[-1],caps[-1],credit[-1],0.)
            newly=df_forced & (~halt);nhalt+=int(newly.sum());halt|=df_forced
            fraction=np.ones(episodes);nz=np.abs(net)>1e-14
            fraction[nz]=np.clip(dealer_cap[nz]/(-net[nz]),0,1)
            rejected+=np.abs(orders).sum(axis=1)*(1-fraction)
            orders=orders*fraction[:,None]
        orders=np.where(halt[:,None],0,orders)
        oldE=E[:,:-1];oldC=C.copy();oldI=I.copy()
        C,I=settle(C,I,orders,P,spread)
        if regime!='unlimited':
            fresh=C[:,:-1]+I[:,:-1]*P[:,None]
            safe_before=(np.abs(oldI[:,:-1])*P[:,None]<=L[:-1]*np.maximum(oldE,0)+1e-8)&(oldC[:,:-1]>=-credit[:-1]*capital[:-1]-1e-8)&(np.abs(oldI[:,:-1])<=caps[:-1]+1e-8)&(oldE>0)
            violation=np.maximum(np.abs(I[:,:-1])*P[:,None]-L[:-1]*np.maximum(fresh,0),0)
            violation=np.maximum(violation,np.maximum(-credit[:-1]*capital[:-1]-C[:,:-1],0))
            violation=np.where(safe_before,violation,0)
            max_fill_violation=max(max_fill_violation,float(violation.max()))
        net=orders.sum(axis=1);new=x+impact*net
        if t==16:new=new+jumps # exogenous repricing, shared across funding counterfactuals
        invalid=(100+new<=1);halt|=invalid;new=np.where(invalid,x,new)
        mem=(1-eta)*mem+eta*x[:,None];x=new
        marked=C+I*(100+x)[:,None]
        default|=np.any(marked<=0,axis=1)
        peak_eq=np.maximum(peak_eq,marked[:,:2])
        drawdown=np.maximum(drawdown,((peak_eq-marked[:,:2])/capital[:2]).max(axis=1))
        max_disp=np.maximum(max_disp,np.abs(x));gross+=np.abs(orders).sum(axis=1);probe_filled+=np.abs(orders[:,-1])
        positive=marked>0
        lev=np.where(positive,np.abs(I)*(100+x)[:,None]/np.maximum(marked,1e-15),0)
        peak_lev=np.maximum(peak_lev,lev.max(axis=1))
        max_cash=max(max_cash,float(np.abs(C.sum(axis=1)-initial_cash).max()))
        max_shares=max(max_shares,float(np.abs(I.sum(axis=1)).max()))
        max_mark=max(max_mark,float(np.abs(marked.sum(axis=1)-initial_cash).max()))
        if save_paths:
            paths.append(x.copy());ledgers.append(np.stack([C,I,marked],axis=1))
    adverse=default|halt|(drawdown>.20)
    return {'event':adverse,'default':default,'halt':halt,'margin':ever_margin,'clipped':ever_clip,
            'drawdown':drawdown,'displacement':max_disp,'gross_volume':gross,'probe_filled':probe_filled,
            'peak_leverage':peak_lev,'liquidations':liquidations,'rejected_volume':rejected,
            'prices':np.array(paths).T if save_paths else None,
            'ledger':np.array(ledgers) if save_paths else None,
            'audit':{'max_cash_error':max_cash,'max_share_error':max_shares,'max_marked_error':max_mark,
                     'max_fresh_trade_violation':max_fill_violation,'clipped_orders':nclip,'margin_calls':nmargin,
                     'new_dealer_halts':nhalt,'episodes':episodes,'steps':steps,'regime':regime,'preloaded_dealer':preloaded_dealer,'shock_jitter':shock_jitter}}
