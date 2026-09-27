"""Contract I1 adapter to the primary audited terminal-row implementation.

Each row of the input contains one independent episode's exact deviations
``x_1, ..., x_T`` (the audited initial ``x_0 = m_0 = 0`` is omitted).
Every episode uses the same endpoint T, fixed before observing the data, with
zero terminal probe ``u_(T-1) = 0``. Public rates and the complete channel
inventory are assumed truthful. The model is

    x_T = mu + a*x_(T-1) + sum_k q_k*m_(k,T-1) + e_T.

The Student-t reference requires independent Gaussian terminal innovations of
common unknown variance, independent of all preterminal regressors. Neither
independence nor truthful resets, exact observations, or endpoint assignment
can be established by inspecting a numeric array. Successive transitions of
one trajectory are not independent episode rows and are explicitly rejected.
"""
from typing import Dict, Any, Tuple
import numpy as np
from research_extension.mm_revision.decisions import DecisionLabel, classify_interval
from studies.audited_constraints.src.inference import reconstruct_terminal, terminal_interval


def construct_audited_regressors(
    x_series: np.ndarray,
    eta_vector: np.ndarray
) -> Tuple[np.ndarray, np.ndarray]:
    """Return one terminal row per independent episode, including an intercept.

    ``x_series`` has shape (n_episodes, T), T >= 3, containing x_1 through
    x_T, not x_0. ``eta_vector`` has d finite disclosed rates in (0, 1].
    Returns X of shape (n_episodes, d+2), ordered [1, x_(T-1), m_(T-1)],
    and a copy of Y = x_T. Memory uses only x_1 through x_(T-2).
    A single 1D trajectory is no longer supported by this API.
    """
    try:
        x = np.asarray(x_series, dtype=float)
    except (TypeError, ValueError) as exc:
        raise ValueError("A finite independent-episode price matrix is required.") from exc
    if x.ndim != 2 or x.shape[0] == 0 or x.shape[1] < 3 or not np.isfinite(x).all():
        raise ValueError("A finite episode price matrix of independent episodes (n, T>=3) is required.")
    try:
        eta = np.asarray(eta_vector, dtype=float)
    except (TypeError, ValueError) as exc:
        raise ValueError("Disclosed rates must be a finite nonempty vector in (0, 1].") from exc
    if eta.ndim != 1 or eta.size == 0 or not np.isfinite(eta).all() or np.any((eta <= 0) | (eta > 1)):
        raise ValueError("Disclosed rates must be a finite nonempty vector in (0, 1].")
    return reconstruct_terminal(x, eta)


def _abstain_result(n: int, p: int, status: str) -> Dict[str, Any]:
    """Preserve result fields without reporting an identified estimate or pivot."""
    return {
        "gamma_hat": [float("nan")] * (p - 1),
        "intercept_hat": float("nan"),
        "coefficient_estimates": [float("nan")] * p,
        "a_hat": float("nan"),
        "q_hat": [float("nan")] * (p - 2),
        "S_hat": float("nan"),
        "se_S": float("inf"),
        "S_lower": -float("inf"),
        "S_upper": float("inf"),
        "decision": DecisionLabel.ABSTAIN,
        "df": n - p,
        "sigma_hat": float("inf"),
        "condition_number_scaled": float("inf"),
        "status": status,
        "reference_distribution": None,
        "is_definite": False,
        "is_conflict": False,
    }


def fit_audited_terminal_regression(
    x_series: np.ndarray,
    eta_vector: np.ndarray,
    alpha: float = 0.05,
    *,
    noise_model: str = "iid_gaussian",
) -> Dict[str, Any]:
    """Fit S = a + sum(q) using the primary scaled-QR terminal-row pivot.

    Requires full column rank and n_episodes > d+2, counting the intercept.
    Invalid designs or numerical failures return ABSTAIN with (-inf, inf).
    Malformed inputs and unsupported noise declarations raise ValueError.
    ``noise_model='iid_gaussian'`` declares the maintained terminal innovation
    law; it does not validate that law from data or permit noisy price sensors.

    Legacy ``gamma_hat`` remains [a, q_1, ..., q_d]; ``intercept_hat`` is
    separate. ``coefficient_estimates`` contains the full [mu, a, q] vector.
    S excludes the intercept. The reference degrees of freedom are n-(d+2).
    """
    if np.ndim(alpha) != 0:
        raise ValueError("alpha must be a finite scalar in (0, 1).")
    try:
        alpha = float(alpha)
    except (TypeError, ValueError) as exc:
        raise ValueError("alpha must be a finite scalar in (0, 1).") from exc
    if not np.isfinite(alpha) or not 0 < alpha < 1:
        raise ValueError("alpha must be a finite scalar in (0, 1).")
    if not isinstance(noise_model, str) or noise_model != "iid_gaussian":
        raise ValueError("noise_model must be 'iid_gaussian' for the exact Student-t reference.")

    X, y = construct_audited_regressors(x_series, eta_vector)
    n, p = X.shape
    try:
        with np.errstate(over="raise", invalid="raise", divide="raise"):
            result = terminal_interval(X, y, alpha)
            if result["status"] != "ok":
                return _abstain_result(n, p, "invalid_design")
            beta = np.asarray(result["coefficient_estimates"])
            residual = y - X @ beta
            sigma_hat = float(np.sqrt(residual @ residual / (n - p)))
            scalars = [result[k] for k in ("estimate", "lower", "upper", "se", "condition_number_scaled")]
            if not np.isfinite(beta).all() or not np.isfinite([*scalars, sigma_hat]).all():
                return _abstain_result(n, p, "numerical_failure")
    except (np.linalg.LinAlgError, FloatingPointError):
        return _abstain_result(n, p, "numerical_failure")

    # Match the primary threshold rule; its interval already has a 1e-12 pad.
    decision = classify_interval(result["lower"], result["upper"], threshold=1.0, tol=0.0)

    return {
        "gamma_hat": beta[1:].tolist(),
        "intercept_hat": float(beta[0]),
        "coefficient_estimates": beta.tolist(),
        "a_hat": float(beta[1]),
        "q_hat": beta[2:].tolist(),
        "S_hat": result["estimate"],
        "se_S": result["se"],
        "S_lower": result["lower"],
        "S_upper": result["upper"],
        "decision": decision,
        "df": result["df"],
        "sigma_hat": sigma_hat,
        "condition_number_scaled": result["condition_number_scaled"],
        "status": "ok",
        "reference_distribution": "student_t",
        "is_definite": bool(decision in (DecisionLabel.STABLE, DecisionLabel.UNSTABLE)),
        "is_conflict": bool(decision == DecisionLabel.CONFLICT),
    }
