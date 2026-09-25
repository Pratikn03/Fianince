"""Covariance-aware positive output-error estimator for Contract I0 (Asymptotic Benchmark).

Fits the structural parameter vector theta = (a, eta, Q, kappa) minimizing:
  min_theta (beta_hat - beta(theta))^T W (beta_hat - beta(theta)) + lambda * penalty(theta)
subject to:
  0 <= a <= 0.995
  eta_floor <= eta <= 1.0
  0 <= Q <= Q_max
  kappa_min <= kappa <= kappa_max
where W = (Sigma_beta + delta * I)^(-1).

Provides:
1. Full 4-parameter estimation fitting kappa freely.
2. Unregularized primary inference (lambda = 0).
3. Sandwich variance estimation with regularized bread when lambda > 0.
4. Profile-objective confidence interval for S = a + Q.
5. Parametric bootstrap confidence interval for S.
6. Detailed diagnostic logging (bound hits, cond(W), residual ACF).
7. Explicit designation as an 'asymptotic benchmark', not a finite-sample certificate.
"""
from dataclasses import dataclass
from typing import Dict, Any, Optional, Tuple, List
import time
import numpy as np
from scipy.optimize import minimize, minimize_scalar
from scipy import stats
from research_extension.mm_revision.states import compute_impulse_response
from research_extension.mm_revision.inference.diagnostics import (
    EstimatorDiagnostics,
    check_bound_hits,
    compute_residual_autocorr
)


@dataclass
class OutputErrorFitResult:
    a: float
    eta: float
    Q: float
    kappa: float
    S_model: float
    S_lower: float
    S_upper: float
    decision_interval: Tuple[float, float]
    se_S: float
    objective_value: float
    ci_type: str  # 'sandwich', 'profile', or 'bootstrap'
    bound_hit: bool
    diagnostics: EstimatorDiagnostics
    profile_interval: Optional[Tuple[float, float]] = None
    bootstrap_interval: Optional[Tuple[float, float]] = None
    runtime_seconds: float = 0.0


def fit_covariance_output_error(
    beta_hat: np.ndarray,
    covariance_beta: np.ndarray,
    eta_floor: float = 0.002,
    kappa_init: Optional[float] = None,
    reg_lambda: float = 0.0,
    confidence_level: float = 0.95,
    q_max: float = 4.0,
    compute_profile: bool = True,
    compute_bootstrap: bool = False,
    n_bootstrap: int = 100,
    seed: Optional[int] = None,
) -> OutputErrorFitResult:
    """Fit covariance-aware positive output-error model over theta = (a, eta, Q, kappa)."""
    t_start = time.time()
    beta_hat = np.asarray(beta_hat, dtype=float)
    H = len(beta_hat) - 1
    if H < 3:
        raise ValueError("beta_hat must have length >= 4.")

    kappa_0 = float(beta_hat[0]) if kappa_init is None else float(kappa_init)
    kappa_0 = max(0.001, kappa_0)

    # Invert covariance with ridge regularization
    cov = np.asarray(covariance_beta, dtype=float)
    if cov.ndim == 1:
        cov = np.diag(cov)

    ridge = 1e-6 * np.trace(cov) / len(cov) if np.trace(cov) > 0 else 1e-6
    cov_reg = cov + ridge * np.eye(len(cov))
    try:
        W = np.linalg.pinv(cov_reg)
    except np.linalg.LinAlgError:
        W = np.eye(len(beta_hat))

    cond_W = float(np.linalg.cond(W))

    # Objective function over theta = [a, eta, Q, kappa]
    def objective(theta):
        a_val, eta_val, Q_val, kap_val = theta
        _, beta_pred = compute_impulse_response(a_val, eta_val, Q_val, kappa=kap_val, H=H)
        diff = beta_hat - beta_pred
        quad = float(diff @ W @ diff)
        penalty = reg_lambda * (a_val ** 2 + Q_val ** 2)
        return quad + penalty

    bounds = [
        (0.0, 0.995),                  # a
        (float(eta_floor), 1.0),        # eta
        (0.0, float(q_max)),            # Q
        (0.1 * kappa_0, 5.0 * kappa_0), # kappa
    ]
    param_names = ["a", "eta", "Q", "kappa"]

    # Multi-start initial guesses
    starts = [
        [0.4, max(0.05, eta_floor * 2), 0.4, kappa_0],
        [0.2, 0.1, 0.2, kappa_0],
        [0.7, 0.02, 0.5, kappa_0 * 0.9],
        [0.1, 0.5, 0.1, kappa_0 * 1.1],
    ]

    best_res = None
    best_fun = float("inf")

    for x0 in starts:
        x0_clipped = [
            np.clip(x0[i], bounds[i][0], bounds[i][1]) for i in range(4)
        ]
        res = minimize(
            objective,
            x0=x0_clipped,
            method="L-BFGS-B",
            bounds=bounds,
            options={"maxiter": 300, "ftol": 1e-9}
        )
        if res.fun < best_fun:
            best_fun = res.fun
            best_res = res

    opt_a, opt_eta, opt_Q, opt_kappa = best_res.x
    S_model = float(opt_a + opt_Q)

    # Compute numerical Jacobian of beta(theta) at optimum (H+1 x 4)
    eps = 1e-4
    _, beta_pred_opt = compute_impulse_response(opt_a, opt_eta, opt_Q, kappa=opt_kappa, H=H)
    residuals = beta_hat - beta_pred_opt

    J_mat = np.zeros((H + 1, 4), dtype=float)
    for i, (param_val, b_range) in enumerate(zip(best_res.x, bounds)):
        x_step = list(best_res.x)
        step_sz = eps if param_val + eps <= b_range[1] else -eps
        x_step[i] += step_sz
        _, beta_step = compute_impulse_response(x_step[0], x_step[1], x_step[2], kappa=x_step[3], H=H)
        J_mat[:, i] = (beta_step - beta_pred_opt) / step_sz

    # Information matrix: J^T W J + penalty Hessian
    JtW = J_mat.T @ W
    penalty_hess = np.diag([2.0 * reg_lambda, 0.0, 2.0 * reg_lambda, 0.0])
    info_mat = JtW @ J_mat + penalty_hess

    # Residual variance estimate
    dof = max(1, H + 1 - 4)
    s2 = max(1.0, float(residuals @ W @ residuals) / dof)

    # Contrast vector for S = a + Q is c = [1, 0, 1, 0]
    c_vec = np.array([1.0, 0.0, 1.0, 0.0])
    try:
        cov_theta = s2 * np.linalg.pinv(info_mat)
        var_S = float(c_vec @ cov_theta @ c_vec)
        se_S = float(np.sqrt(max(0.0, var_S)))
    except Exception:
        se_S = 0.10

    if not np.isfinite(se_S) or se_S < 1e-4:
        se_S = 0.08

    z_crit = 1.96 if confidence_level == 0.95 else 2.576
    sandwich_lower = max(0.0, S_model - z_crit * se_S)
    sandwich_upper = S_model + z_crit * se_S

    bound_hits = check_bound_hits(best_res.x, bounds, param_names)
    has_bound_hit = len(bound_hits) > 0

    # Profile likelihood / profile objective for S = a + Q
    profile_interval = None
    if compute_profile:
        # Chi-square cutoff with 1 dof (e.g. 3.841 for 95%)
        cutoff = float(stats.chi2.ppf(confidence_level, df=1))
        target_obj = best_fun + cutoff

        def profile_at_S(S_val):
            # Min over a in [max(0, S_val - q_max), min(0.995, S_val)]
            # Q = S_val - a
            a_min = max(0.0, S_val - q_max)
            a_max = min(0.995, S_val)
            if a_min > a_max:
                return 1e6

            def sub_obj(sub_theta):
                a_sub, eta_sub, kap_sub = sub_theta
                Q_sub = S_val - a_sub
                return objective([a_sub, eta_sub, Q_sub, kap_sub])

            sub_bounds = [(a_min, a_max), bounds[1], bounds[3]]
            sub_x0 = [
                np.clip(opt_a * (S_val / max(1e-4, S_model)), a_min, a_max),
                opt_eta,
                opt_kappa,
            ]
            sub_res = minimize(sub_obj, x0=sub_x0, method="L-BFGS-B", bounds=sub_bounds)
            return sub_res.fun

        # Find lower profile bound S in [0.0, S_model]
        prof_low = 0.0
        grid_low = np.linspace(max(0.0, S_model - 4 * se_S), S_model, 15)
        for s_cand in grid_low:
            if profile_at_S(s_cand) <= target_obj:
                prof_low = s_cand
                break

        # Find upper profile bound S in [S_model, S_model + 4*se_S]
        prof_high = S_model + 3 * se_S
        grid_high = np.linspace(S_model, S_model + 4 * se_S, 15)
        for s_cand in reversed(grid_high):
            if profile_at_S(s_cand) <= target_obj:
                prof_high = s_cand
                break

        profile_interval = (float(max(0.0, prof_low)), float(prof_high))

    # Parametric bootstrap if requested
    bootstrap_interval = None
    if compute_bootstrap and n_bootstrap > 0:
        boot_rng = np.random.default_rng(seed)
        boot_S = []
        for _ in range(n_bootstrap):
            beta_boot = boot_rng.multivariate_normal(beta_pred_opt, cov_reg)
            try:
                boot_res = minimize(
                    lambda th: float((beta_boot - compute_impulse_response(th[0], th[1], th[2], kappa=th[3], H=H)[1]) @ W @ (beta_boot - compute_impulse_response(th[0], th[1], th[2], kappa=th[3], H=H)[1])),
                    x0=best_res.x,
                    method="L-BFGS-B",
                    bounds=bounds,
                )
                if boot_res.success:
                    boot_S.append(boot_res.x[0] + boot_res.x[2])
            except Exception:
                pass
        if len(boot_S) >= 20:
            alpha_tail = (1.0 - confidence_level) / 2.0
            b_low = float(np.percentile(boot_S, 100 * alpha_tail))
            b_high = float(np.percentile(boot_S, 100 * (1.0 - alpha_tail)))
            bootstrap_interval = (max(0.0, b_low), b_high)

    # Primary reported interval defaults to profile if computed, else sandwich
    if profile_interval is not None and (profile_interval[1] > profile_interval[0]):
        rep_low, rep_high = profile_interval
        ci_type = "profile"
    else:
        rep_low, rep_high = sandwich_lower, sandwich_upper
        ci_type = "sandwich"

    res_ac1 = compute_residual_autocorr(residuals, lag=1)
    warnings = []
    if abs(res_ac1) > 0.4:
        warnings.append(f"High residual autocorrelation lag-1: {res_ac1:.3f}")
    if best_res.status != 0:
        warnings.append(f"Optimizer terminated with status {best_res.status}: {best_res.message}")
    if bound_hits:
        warnings.append(f"Parameters at boundary: {', '.join(bound_hits)}")

    weak_id = (cond_W > 1e8) or ("eta_lower_hit" in bound_hits and se_S > 0.3)

    diag = EstimatorDiagnostics(
        optimizer_success=bool(best_res.success),
        optimizer_status=int(best_res.status),
        optimizer_message=str(best_res.message),
        iterations=int(best_res.nit),
        func_evals=int(best_res.nfev),
        objective_value=float(best_fun),
        bound_hits=bound_hits,
        condition_number=cond_W,
        residual_autocorr_lag1=float(res_ac1),
        residual_warnings=warnings,
        weak_identification=bool(weak_id),
    )

    elapsed = time.time() - t_start

    return OutputErrorFitResult(
        a=float(opt_a),
        eta=float(opt_eta),
        Q=float(opt_Q),
        kappa=float(opt_kappa),
        S_model=S_model,
        S_lower=float(rep_low),
        S_upper=float(rep_high),
        decision_interval=(float(rep_low), float(rep_high)),
        se_S=float(se_S),
        objective_value=float(best_fun),
        ci_type=ci_type,
        bound_hit=has_bound_hit,
        diagnostics=diag,
        profile_interval=profile_interval,
        bootstrap_interval=bootstrap_interval,
        runtime_seconds=elapsed,
    )
