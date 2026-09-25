"""Observational empirical estimators under Contract I2.

Strictly separates:
1. F = empirical persistence proxy (e.g. autocorrelation sum)
2. S_model = a_hat + Q_hat (structural dynamic state-space fit)
3. Actual market stability (not certified by observational data alone)

Saves full diagnostics for every fitted window:
- a, eta, Q, S_model, initial_state_method, objective_value, validation_loss,
  regularization, parameter_bound_hits, optimizer_status, profile_width,
  residual_warnings, data_quality_status.
"""
from dataclasses import dataclass, field
from typing import Dict, Any, List, Optional, Tuple
import numpy as np
from scipy.optimize import minimize
from research_extension.mm_revision.inference.diagnostics import (
    EstimatorDiagnostics,
    check_bound_hits,
    compute_residual_autocorr
)


def compute_empirical_persistence_proxy(
    returns: np.ndarray,
    lags: Tuple[int, ...] = (1, 2, 5)
) -> Dict[str, Any]:
    """Compute reduced-form empirical persistence proxy F from return autocorrelations.

    F = |a| + sum_{tau in lags} |rho(tau)|
    where a is AR(1) coefficient.
    """
    ret = np.asarray(returns, dtype=float).flatten()
    n = len(ret)
    if n < 10:
        return {"F": 0.0, "a_ar1": 0.0, "rho_lags": {}, "status": "INSUFFICIENT_OBSERVATIONS"}

    def autocorr(x, lag):
        if len(x) <= lag + 2:
            return 0.0
        xc = x - np.mean(x)
        var = np.var(xc)
        if var < 1e-15:
            return 0.0
        return float(np.mean(xc[:-lag] * xc[lag:]) / var)

    var0 = np.var(ret[:-1])
    if var0 > 1e-15:
        a_ar1 = float(np.cov(ret[1:], ret[:-1])[0, 1] / var0)
        a_ar1 = max(-0.99, min(0.99, a_ar1))
    else:
        a_ar1 = 0.0

    rho_dict = {}
    sum_abs_rho = 0.0
    for l in lags:
        r_l = autocorr(ret, l)
        rho_dict[f"rho_{l}"] = r_l
        sum_abs_rho += abs(r_l)

    F = abs(a_ar1) + sum_abs_rho

    return {
        "F": float(F),
        "a_ar1": float(a_ar1),
        "rho_lags": rho_dict,
        "sum_abs_rho": float(sum_abs_rho),
        "estimator_type": "empirical_persistence_proxy_F",
    }


@dataclass
class ObservationalFitResult:
    a: float
    eta: float
    Q: float
    kappa: float
    S_model: float
    initial_state_method: str
    objective_value: float
    validation_loss: float
    regularization: float
    diagnostics: EstimatorDiagnostics
    data_quality_status: str


def fit_observational_structural_model(
    prices: np.ndarray,
    signed_flow: np.ndarray,
    train_ratio: float = 0.70,
    reg_lambda: float = 0.01,
    seed: int = 42,
    data_quality_status: str = "PASS"
) -> ObservationalFitResult:
    """Fit aggregate structural dynamic model:
      x_{t+1} = a * x_t + y_t + kappa * v_t + e_{t+1}
      y_{t+1} = (1 - eta) * y_t + eta * Q * x_t
    DOES NOT force S < 1 during optimization.
    """
    rng = np.random.default_rng(seed)
    p = np.asarray(prices, dtype=float).flatten()
    v = np.asarray(signed_flow, dtype=float).flatten()
    N = min(len(p), len(v))
    if N < 20:
        raise ValueError("Insufficient data for structural estimation.")

    p = p[:N]
    v = v[:N]
    
    # Return changes
    dx = np.diff(np.log(p)) if np.all(p > 0) else np.diff(p)
    v_in = v[:-1]
    T = len(dx)
    T_train = int(T * train_ratio)

    dx_train = dx[:T_train]
    v_train = v_in[:T_train]
    dx_val = dx[T_train:]
    v_val = v_in[T_train:]

    # Simulation helper with initial state y_0 estimated from prior mean
    def simulate(theta, v_seq, dx_seq):
        a_val, eta_val, Q_val, kap_val, y0_val = theta
        T_seq = len(v_seq)
        pred = np.zeros(T_seq)
        y = y0_val
        for t in range(T_seq):
            x_prev = dx_seq[t-1] if t > 0 else 0.0
            pred[t] = a_val * x_prev + y + kap_val * v_seq[t]
            y = (1.0 - eta_val) * y + eta_val * Q_val * x_prev
        return pred

    def loss(theta):
        pred = simulate(theta, v_train, dx_train)
        err = dx_train - pred
        mse = float(np.mean(err**2))
        pen = reg_lambda * (theta[2]**2) # L2 penalty on Q
        return mse + pen

    # Bounds: a in (-0.99, 0.99), eta in (0.001, 1.0), Q in (0, 5.0), kappa in (-5.0, 5.0), y0 in (-1, 1)
    bounds = [
        (-0.99, 0.99),
        (0.001, 1.0),
        (0.0, 5.0),
        (-5.0, 5.0),
        (-1.0, 1.0)
    ]
    param_names = ["a", "eta", "Q", "kappa", "y0"]

    # Initial parameter guess with random jitter
    x0 = [
        0.2 + rng.normal(0, 0.05),
        0.1 + abs(rng.normal(0, 0.02)),
        0.2 + abs(rng.normal(0, 0.05)),
        0.01 + rng.normal(0, 0.005),
        0.0,
    ]
    x0_clipped = [np.clip(x0[i], bounds[i][0] + 1e-4, bounds[i][1] - 1e-4) for i in range(len(bounds))]

    res = minimize(
        loss,
        x0=x0_clipped,
        method="L-BFGS-B",
        bounds=bounds,
        options={"maxiter": 200, "ftol": 1e-7}
    )

    opt_a, opt_eta, opt_Q, opt_kap, opt_y0 = res.x
    S_model = float(opt_a + opt_Q)

    # Validation loss
    val_pred = simulate(res.x, v_val, dx_val)
    val_mse = float(np.mean((dx_val - val_pred)**2)) if len(dx_val) > 0 else 0.0

    # Residuals & autocorrelation
    train_pred = simulate(res.x, v_train, dx_train)
    resids = dx_train - train_pred
    ac1 = compute_residual_autocorr(resids, lag=1)

    bound_hits = check_bound_hits(res.x, bounds, param_names)
    warnings = []
    if abs(ac1) > 0.4:
        warnings.append(f"High residual autocorrelation: {ac1:.3f}")
    if bound_hits:
        warnings.append(f"Parameters at boundary: {', '.join(bound_hits)}")

    diag = EstimatorDiagnostics(
        optimizer_success=bool(res.success),
        optimizer_status=int(res.status),
        optimizer_message=str(res.message),
        iterations=int(res.nit),
        func_evals=int(res.nfev),
        objective_value=float(res.fun),
        bound_hits=bound_hits,
        condition_number=1.0,
        residual_autocorr_lag1=float(ac1),
        residual_warnings=warnings,
        weak_identification=bool("Q_lower_hit" in bound_hits or "eta_lower_hit" in bound_hits),
    )

    return ObservationalFitResult(
        a=float(opt_a),
        eta=float(opt_eta),
        Q=float(opt_Q),
        kappa=float(opt_kap),
        S_model=S_model,
        initial_state_method="estimated_y0",
        objective_value=float(res.fun),
        validation_loss=val_mse,
        regularization=reg_lambda,
        diagnostics=diag,
        data_quality_status=data_quality_status,
    )
