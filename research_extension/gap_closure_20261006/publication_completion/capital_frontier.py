"""Explicit cash/inventory margin contract for controlled, nonnegative probes."""
import numpy as np

def positive_cohort_model(anchor,impact,weights,rates):
    weights=np.asarray(weights,float);rates=np.asarray(rates,float)
    if len(weights)!=len(rates) or not len(weights) or (weights<0).any() or (rates<=0).any() or (rates>=1).any() or not 0<=anchor<1 or impact<=0 or anchor+impact*weights.sum()>=1:
        raise ValueError('Outside the positive stable cohort model')
    J=np.zeros((len(rates)+1,len(rates)+1));J[0]=np.r_[anchor,impact*weights]
    for i,rate in enumerate(rates):J[i+1]=rate*J[0];J[i+1,i+1]+=1-rate
    return J,impact*np.r_[1,rates],np.eye(len(rates)+1)[0]

def robust_quantity_cap(capital,impact,margin,reference_price,cost=0.,execution_fraction=.5):
    if capital<=0 or impact<=0 or margin<=0 or reference_price<=0 or cost<0 or not 0<=execution_fraction<=.5:
        raise ValueError('Outside positive capital/impact/margin/price/nonnegative-cost contract')
    beta=cost+margin*reference_price
    return 2*capital/(beta+np.sqrt(beta*beta+4*(1+margin-execution_fraction)*impact*capital))

def account(J,H,price_selector,probes,capital,reference_price,cost=0.,execution_fraction=.5):
    probes=np.asarray(probes,float)
    if (probes<0).any() or not 0<=execution_fraction<=.5:raise ValueError('Outside nonnegative probe and execution-fraction contract')
    z=np.zeros(len(H));inventory=0.;cash=float(capital);price=reference_price;rows=[]
    for v in probes:
        baseline=J@z
        execution_price=reference_price+price_selector@baseline+execution_fraction*(price_selector@H)*v
        inventory-=v;cash+=v*execution_price-cost*v
        z=baseline+H*v;price=reference_price+price_selector@z
        equity=cash+inventory*price
        rows.append(dict(price=float(price),inventory=float(inventory),cash=float(cash),equity=float(equity)))
    return rows

def probe_trader_account(J,H,price_selector,probes,capital,reference_price,cost=0.):
    """The trading account pays average refreshed book prices; margin loans allowed."""
    z=np.zeros(len(H));inventory=0.;cash=float(capital);rows=[];impact=float(price_selector@H)
    for v in np.asarray(probes,float):
        baseline=J@z;fill=reference_price+price_selector@baseline+.5*impact*v
        inventory+=v;cash-=v*fill+cost*abs(v)
        z=baseline+H*v;price=reference_price+price_selector@z
        rows.append(dict(price=float(price),inventory=float(inventory),cash=float(cash),
                         equity=float(cash+inventory*price),fundamental_equity=float(cash+inventory*reference_price)))
    return rows
