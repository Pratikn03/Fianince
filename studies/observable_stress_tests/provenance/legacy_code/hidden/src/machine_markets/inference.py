"""Finite-horizon bounds and conventional point-estimation comparators."""
import math
from functools import lru_cache
import numpy as np
from scipy.stats import norm


def feedback_bounds(sum_lower: float, sum_upper: float, last_upper: float,
                    horizon: int, eta_floor: float) -> tuple[float,float]:
    """Bound total nonnegative feedback using a valid learning-rate floor.

    Inputs must cover the true partial sum and terminal tap. This function
    does not assert that intervals computed elsewhere have valid coverage.
    """
    if int(horizon) != horizon or horizon < 1:
        raise ValueError('horizon must be a positive integer')
    if not (0 <= eta_floor <= 1):
        raise ValueError('eta_floor must lie in [0,1]')
    if not all(np.isfinite(v) for v in [sum_lower,sum_upper,last_upper]):
        raise ValueError('measurement endpoints must be finite')
    if sum_lower > sum_upper or sum_upper < 0 or last_upper < 0:
        raise ValueError('measurement interval conflicts with nonnegative model')
    lower = max(0.0,sum_lower)
    if eta_floor == 0:
        return lower, math.inf
    fraction = 1.0 if eta_floor == 1 else -math.expm1(horizon*math.log1p(-eta_floor))
    upper_sum = sum_upper/fraction
    upper_terminal = sum_upper + (1-eta_floor)/eta_floor*last_upper
    return lower, min(upper_sum,upper_terminal)


def classify(a: float, lower: float, upper: float, tolerance: float = 1e-12) -> str:
    if np.isnan(lower) or np.isnan(upper) or lower > upper+tolerance:
        return 'model_conflict'
    if a+upper < 1-tolerance:
        return 'stable'
    if a+lower > 1+tolerance:
        return 'unstable'
    return 'inconclusive'


@lru_cache(maxsize=16)
def gaussian_multiplier(number_horizons: int, alpha: float) -> float:
    """Identical critical values are shared across Monte Carlo repetitions."""
    return float(norm.ppf(1-alpha/(4*number_horizons)))


def gaussian_certificate(a: float, observed_sum: float, observed_last: float,
                         horizon: int, tap_se: float, eta_floor: float,
                         number_horizons: int = 4, alpha: float = .05) -> dict:
    """Simultaneous Gaussian intervals over sum and last tap at all horizons.

    Tap-mean noises are independent with known tap_se. The partial sum and
    terminal tap are correlated; Bonferroni does not assume independence.
    """
    if tap_se < 0 or number_horizons < 1 or not (0 < alpha < 1):
        raise ValueError('invalid standard error, horizon count, or alpha')
    z = gaussian_multiplier(number_horizons,alpha)
    sl = observed_sum-z*tap_se*np.sqrt(horizon)
    su = observed_sum+z*tap_se*np.sqrt(horizon)
    ku = observed_last+z*tap_se
    try:
        lower,upper = feedback_bounds(sl,su,ku,horizon,eta_floor)
        label = classify(a,lower,upper)
    except ValueError:
        lower,upper,label = float('nan'),float('nan'),'model_conflict'
    return {'lower':lower,'upper':upper,'label':label,'z':z}


def single_rate(kernel: np.ndarray) -> float:
    """Two moments fit one exponential; no guarantee for mixed learning rates."""
    k=np.asarray(kernel,dtype=float)
    if len(k) < 2 or k[0] <= 0 or k[1] < 0 or k[1] >= k[0]:
        return float('nan')
    return float(k[0]**2/(k[0]-k[1]))


def matrix_pencil(kernel: np.ndarray, tap_se: float, eta_floor: float) -> float:
    """Conventional Hankel/matrix-pencil moment fit (heuristic under noise).

    A maximum rank of eight, a fixed noise-aware SVD cutoff, positivity
    checks, and the supplied rate floor are used. No automatic safety claim.
    """
    k=np.asarray(kernel,dtype=float)
    if k.ndim != 1 or len(k) < 2 or not np.all(np.isfinite(k)):
        return float('nan')
    p=min(8,len(k)//2)
    H0=np.array([[k[i+j] for j in range(p)] for i in range(p)])
    H1=np.array([[k[i+j+1] for j in range(p)] for i in range(p)])
    U,s,Vt=np.linalg.svd(H0,full_matrices=False)
    cutoff=max(5*tap_se*p, s[0]*1e-10)
    rank=int(np.sum(s>cutoff))
    if rank == 0:
        return float('nan')
    reduced=(U[:,:rank].T @ H1 @ Vt[:rank,:].T)/s[:rank][None,:]
    roots=np.linalg.eigvals(reduced)
    if np.any(np.abs(roots.imag)>1e-7):
        return float('nan')
    r=roots.real
    if np.any(r < -1e-8) or np.any(r > 1-eta_floor+1e-8):
        return float('nan')
    r=np.clip(r,0,1-eta_floor)
    V=r[None,:]**np.arange(len(k))[:,None]
    weights=np.linalg.lstsq(V,k,rcond=None)[0]
    if np.any(weights < -max(5*tap_se,1e-9)):
        return float('nan')
    weights=np.maximum(weights,0)
    if np.any(1-r <= 0):
        return float('nan')
    return float(np.sum(weights/(1-r)))


def point_label(a: float, estimate: float) -> str:
    if not np.isfinite(estimate):
        return 'inconclusive'
    return classify(a,estimate,estimate)
