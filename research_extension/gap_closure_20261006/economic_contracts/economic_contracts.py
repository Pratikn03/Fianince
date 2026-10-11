"""Explicit conditional dealer contracts; no empirical market calibration."""
import numpy as np
from scipy.optimize import minimize_scalar

def robust_spread(costs,transparent_index=0):
    costs=np.asarray(costs,float)
    if len(costs)==0 or not np.isfinite(costs).all():raise ValueError('Finite nonempty costs required')
    return float(costs.max()),float(costs.max()-costs[transparent_index])

def gaussian_cost(mean,variance,risk_aversion):
    if variance<0 or risk_aversion<=0:raise ValueError('Invalid Gaussian/CARA parameters')
    return mean+risk_aversion*variance/2

def depth_solution(edge,holding_cost,margin_per_quantity,available_capital,minimum=0,maximum=np.inf):
    if edge<0 or holding_cost<=0 or margin_per_quantity<=0 or minimum<0 or maximum<minimum:raise ValueError('Invalid primitives')
    cap=min(maximum,available_capital/margin_per_quantity)
    if cap<minimum:return {'status':'INFEASIBLE_QUOTING_COMMITMENT','quantity':None}
    quantity=float(np.clip(edge/holding_cost,minimum,cap))
    return {'status':'FEASIBLE','quantity':quantity,'capital_cap':cap,'unconstrained_quantity':edge/holding_cost}

def clearing_matrix(impact,anchor,feedback,learning):
    a=1-impact*anchor
    return np.array([[a,impact*feedback],[learning*a,1-learning+learning*impact*feedback]])

def schur_conditions(impact,anchor,feedback,learning):
    if impact<=0 or anchor<=0 or not 0<learning<1:raise ValueError('Require positive impact/anchor and interior learning')
    J=clearing_matrix(impact,anchor,feedback,learning);trace=np.trace(J);det=np.linalg.det(J)
    return np.array([1-trace+det,1+trace+det,1-det])

def equity_step(cash,inventory,price,next_price,aggressive_quantity,half_spread,fees=0,funding=0):
    q=aggressive_quantity
    next_inventory=inventory-q;next_cash=cash+q*price+half_spread*abs(q)-fees-funding
    old_equity=cash+inventory*price;next_equity=next_cash+next_inventory*next_price
    pnl=half_spread*abs(q)+next_inventory*(next_price-price)-fees-funding
    return {'cash':next_cash,'inventory':next_inventory,'equity':next_equity,'pnl':pnl,'equity_change':next_equity-old_equity}

def allocation_loss(b,spread0,marginal_cost,increment):
    # Interior linear inverse demand; resources/CE-cost criterion declared separately.
    return b*(spread0-marginal_cost)*increment+b*increment**2/2
