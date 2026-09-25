"""Inference diagnostics: convergence, bound hits, residual autocorrelations, and condition numbers."""
from dataclasses import dataclass, field
from typing import Optional, List, Dict, Any
import numpy as np


@dataclass
class EstimatorDiagnostics:
    optimizer_success: bool
    optimizer_status: int
    optimizer_message: str
    iterations: int
    func_evals: int
    objective_value: float
    bound_hits: List[str] = field(default_factory=list)
    condition_number: float = 1.0
    residual_autocorr_lag1: float = 0.0
    residual_warnings: List[str] = field(default_factory=list)
    weak_identification: bool = False


def check_bound_hits(
    params: np.ndarray,
    bounds: List[tuple],
    param_names: List[str],
    tol: float = 1e-4
) -> List[str]:
    """Identify which parameters hit lower or upper bounds."""
    hits = []
    for p, b, name in zip(params, bounds, param_names):
        lower, upper = b
        if lower is not None and abs(p - lower) < tol:
            hits.append(f"{name}_lower_hit")
        if upper is not None and abs(p - upper) < tol:
            hits.append(f"{name}_upper_hit")
    return hits


def compute_residual_autocorr(residuals: np.ndarray, lag: int = 1) -> float:
    """Compute autocorrelation of residuals at given lag."""
    r = np.asarray(residuals, dtype=float).flatten()
    if len(r) <= lag + 2:
        return 0.0
    rc = r - np.mean(r)
    var = np.var(rc)
    if var < 1e-15:
        return 0.0
    return float(np.mean(rc[:-lag] * rc[lag:]) / var)
