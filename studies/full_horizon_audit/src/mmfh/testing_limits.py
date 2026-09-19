"""Classical Gaussian two-point testing specialized to a hidden slow mode.

This module is not used to select or tune the primary estimators.
"""
import math
from scipy.stats import norm

def squared_distance(delta:float,eta:float,horizon:int|None,se:float)->float:
    if not (delta>=0 and 0<eta<=1 and se>0):raise ValueError('invalid parameters')
    if horizon is not None and (horizon<1 or int(horizon)!=horizon):raise ValueError('invalid horizon')
    factor=1. if horizon is None or eta==1 else -math.expm1(2*horizon*math.log1p(-eta))
    return delta**2*eta*factor/(se**2*(2-eta))

def oracle_error(distance_squared:float)->float:
    """Best balanced forced-classification error for the two known means."""
    if distance_squared<0:raise ValueError('negative squared distance')
    return float(norm.cdf(-math.sqrt(distance_squared)/2))

def total_variation(distance_squared:float)->float:
    return 1-2*oracle_error(distance_squared)

def coverage_upper_bound(distance_squared:float,alpha:float)->float:
    """Necessary, not generally sharp: coverage <= 2*unconditional_error+TV."""
    if not 0<=alpha<=.5:raise ValueError('invalid alpha')
    return min(1.,2*alpha+total_variation(distance_squared))
