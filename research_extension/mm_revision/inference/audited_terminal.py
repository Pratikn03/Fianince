"""Audited terminal-row regression pivot under Contract I1.

Under Contract I1:
- Verified memory reset y_0 = 0
- Disclosed learning rates eta = (eta_1, ..., eta_n)
- Exhaustive channel inventory
- Exact prices x_t
Regressor construction:
  w_{k, t} = eta_k * sum_{s=0}^{t-1} (1 - eta_k)^{t-1-s} * x_s
OLS model:
  x_{t+1} = a * x_t + sum_{k=1}^n q_k * w_{k,t} + e_{t+1}
Total feedback gain:
  S = a + sum_{k=1}^n q_k = 1^T gamma
"""
from typing import Dict, Any, Tuple, Optional
import numpy as np
from scipy.stats import t as student_t
from research_extension.mm_revision.decisions import DecisionLabel, classify_interval


def construct_audited_regressors(
    x_series: np.ndarray,
    eta_vector: np.ndarray
) -> Tuple[np.ndarray, np.ndarray]:
    """Construct regressors Z and dependent variable Y for audited terminal regression.

    Parameters:
      x_series: shape (T+1,) observed price trajectory
      eta_vector: shape (n,) disclosed learning rates
    Returns:
      Z: shape (T, 1+n) regressor matrix [x_t, w_{1,t}, ..., w_{n,t}]
      Y: shape (T,) dependent variable x_{t+1}
    """
    x = np.asarray(x_series, dtype=float)
    eta = np.asarray(eta_vector, dtype=float)
    n = len(eta)
    T = len(x) - 1

    Z = np.zeros((T, 1 + n), dtype=float)
    Y = x[1:]

    # Memory states w_{k, t} initialized at 0 (verified reset)
    w = np.zeros(n, dtype=float)
    for t in range(T):
        Z[t, 0] = x[t]
        Z[t, 1:] = w
        w = (1.0 - eta) * w + eta * x[t]

    return Z, Y


def fit_audited_terminal_regression(
    x_series: np.ndarray,
    eta_vector: np.ndarray,
    alpha: float = 0.05
) -> Dict[str, Any]:
    """Fit OLS terminal-row regression and compute confidence interval for S = a + sum(q)."""
    Z, Y = construct_audited_regressors(x_series, eta_vector)
    T, p = Z.shape

    if T <= p:
        raise ValueError(f"Insufficient observations (T={T}) for {p} parameters.")

    # OLS estimation via SVD / pseudoinverse
    gamma_hat, residuals, rank, s = np.linalg.lstsq(Z, Y, rcond=None)
    resid = Y - Z @ gamma_hat
    df = T - p
    sigma2_hat = float(np.sum(resid**2) / df)

    # Covariance of gamma_hat
    ZtZ_inv = np.linalg.pinv(Z.T @ Z)
    cov_gamma = sigma2_hat * ZtZ_inv

    # Linear combination S = 1^T gamma
    ones_vec = np.ones(p, dtype=float)
    S_hat = float(np.sum(gamma_hat))
    var_S = float(ones_vec @ cov_gamma @ ones_vec)
    se_S = float(np.sqrt(max(0.0, var_S)))

    # Critical Student-t value
    tcrit = float(student_t.ppf(1.0 - alpha / 2.0, df))
    S_lower = S_hat - tcrit * se_S
    S_upper = S_hat + tcrit * se_S

    decision = classify_interval(S_lower, S_upper, threshold=1.0)

    return {
        "gamma_hat": gamma_hat.tolist(),
        "a_hat": float(gamma_hat[0]),
        "q_hat": gamma_hat[1:].tolist(),
        "S_hat": S_hat,
        "se_S": se_S,
        "S_lower": float(S_lower),
        "S_upper": float(S_upper),
        "decision": decision,
        "df": df,
        "sigma_hat": float(np.sqrt(sigma2_hat)),
        "is_definite": bool(decision in (DecisionLabel.STABLE, DecisionLabel.UNSTABLE)),
        "is_conflict": bool(decision == DecisionLabel.CONFLICT),
    }
