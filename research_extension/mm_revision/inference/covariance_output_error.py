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
3. Gauss--Newton sandwich approximation with regularized bread when lambda > 0.
4. Profile-objective confidence interval for S = a + Q.
5. Parametric bootstrap confidence interval for S.
6. Detailed diagnostic logging (bound hits, cond(W), residual ACF).
7. Explicit designation as an 'asymptotic benchmark', not a finite-sample certificate.

The bread omits residual-weighted second derivatives of the response. Under
persistent model misspecification it is not the full estimating-equation
derivative, and its uncertainty is not generally misspecification robust.
"""
from dataclasses import dataclass
from typing import Optional, Tuple
import time
import numpy as np
from scipy.optimize import minimize
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
    ci_type: str  # 'sandwich', 'profile', or 'unavailable'
    bound_hit: bool
    diagnostics: EstimatorDiagnostics
    profile_interval: Optional[Tuple[float, float]] = None
    bootstrap_interval: Optional[Tuple[float, float]] = None
    runtime_seconds: float = 0.0
    sandwich_interval: Optional[Tuple[float, float]] = None
    inference_status: str = "local_asymptotic"
    profile_status: Optional[Tuple[str, str]] = None
    jacobian_rank: Optional[int] = None


def _profile_interval(profile, center, target, lower_bound, upper_bound,
                      initial_step, atol=1e-7):
    """Bracket local crossings and return the rejected (outward) endpoints.

    This follows the accepted component around ``center``; neither the search
    nor the nuisance optimizer certifies a global, possibly disconnected set.
    No crossing means the parameter bound, not a finite SE-based truncation.
    A nonfinite evaluation cannot establish rejection: return the full domain.
    """
    full_domain = (float(lower_bound), float(upper_bound))
    center_value = profile(center)
    if not np.isfinite(center_value) or center_value > target:
        return full_domain, ("unavailable", "unavailable")

    def endpoint(bound):
        if center == bound:
            return float(bound), "parameter_bound"
        direction = np.sign(bound - center)
        step = max(float(initial_step), atol)
        inside = center
        while True:
            outside = float(np.clip(center + direction * step, lower_bound, upper_bound))
            value = profile(outside)
            if not np.isfinite(value):
                return float(bound), "unavailable"
            if value > target:
                break
            if outside == bound:
                return float(bound), "parameter_bound"
            inside = outside
            step *= 2
        while abs(outside - inside) > atol:
            midpoint = (inside + outside) / 2
            value = profile(midpoint)
            if not np.isfinite(value):
                return float(bound), "unavailable"
            if value > target:
                outside = midpoint
            else:
                inside = midpoint
        return float(outside), "crossing"

    low, low_status = endpoint(lower_bound)
    if low_status == "unavailable":
        return full_domain, ("unavailable", "unavailable")
    high, high_status = endpoint(upper_bound)
    if "unavailable" in (low_status, high_status):
        return full_domain, ("unavailable", "unavailable")
    return (low, high), (low_status, high_status)


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
    """Fit theta=(a, eta, Q, kappa), with local/asymptotic inference only.

    Sandwich uncertainty propagates the supplied coefficient covariance through
    the Gauss-Newton estimating equation. Profiles use the penalized objective
    and a chi-square reference; multistart fitting does not certify global
    minima or finite-sample coverage (especially with penalties/boundary hits).
    Unavailable inference returns a non-informative decision interval [0, inf].
    ``sandwich_interval`` is reported independently from ``profile_interval``.
    If ``profile_status`` is unavailable, the latter may contain the full
    parameter domain as a diagnostic fallback: it is not a confidence interval
    and must not be counted as successful profile coverage. A separately valid
    sandwich interval does not restore the failed profile's coverage claim.
    """
    t_start = time.time()
    beta_hat = np.asarray(beta_hat, dtype=float)
    if beta_hat.ndim != 1 or len(beta_hat) < 4 or not np.all(np.isfinite(beta_hat)):
        raise ValueError("beta_hat must be a finite vector of length >= 4.")
    H = len(beta_hat) - 1
    if not np.isfinite(confidence_level) or not 0 < confidence_level < 1:
        raise ValueError("confidence_level must lie strictly between 0 and 1.")
    if not np.isfinite(reg_lambda) or reg_lambda < 0:
        raise ValueError("reg_lambda must be finite and nonnegative.")
    if not np.isfinite(q_max) or q_max < 0 or not np.isfinite(eta_floor) or not 0 < eta_floor <= 1:
        raise ValueError("Require finite q_max >= 0 and 0 < eta_floor <= 1.")

    kappa_0 = float(beta_hat[0]) if kappa_init is None else float(kappa_init)
    if not np.isfinite(kappa_0):
        raise ValueError("kappa_init must be finite.")
    kappa_0 = max(0.001, kappa_0)

    # Invert covariance with ridge regularization
    cov = np.asarray(covariance_beta, dtype=float)
    if cov.ndim == 1:
        cov = np.diag(cov)
    if cov.shape != (len(beta_hat), len(beta_hat)) or not np.all(np.isfinite(cov)):
        raise ValueError("covariance_beta must be finite and match beta_hat dimensions.")
    scale = float(np.max(np.abs(cov)))
    if scale == 0 or not np.allclose(cov, cov.T, rtol=0, atol=1e-12 * scale):
        raise ValueError("covariance_beta must be nonzero and symmetric.")
    cov = (cov + cov.T) / 2
    if np.linalg.eigvalsh(cov)[0] < -1e-12 * scale or np.trace(cov) <= 0:
        raise ValueError("covariance_beta must be positive semidefinite with positive trace.")

    ridge = 1e-6 * np.trace(cov) / len(cov)
    cov_reg = cov + ridge * np.eye(len(cov))
    W = np.linalg.solve(cov_reg, np.eye(len(cov)))
    W = (W + W.T) / 2

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

    def unavailable(reason, result=None, rank=None):
        theta = np.asarray(result.x) if result is not None else np.full(4, np.nan)
        hits = check_bound_hits(theta, bounds, param_names)
        obj = float(result.fun) if result is not None else float("nan")
        diag = EstimatorDiagnostics(
            optimizer_success=bool(result is not None and result.success
                                   and np.isfinite(obj) and np.all(np.isfinite(theta))),
            optimizer_status=int(result.status) if result is not None else -1,
            optimizer_message=str(result.message) if result is not None else reason,
            iterations=int(result.nit) if result is not None else 0,
            func_evals=int(result.nfev) if result is not None else 0,
            objective_value=obj, bound_hits=hits, condition_number=cond_W,
            residual_warnings=[reason], weak_identification=(rank is not None and rank < 4),
        )
        return OutputErrorFitResult(
            a=float(theta[0]), eta=float(theta[1]), Q=float(theta[2]), kappa=float(theta[3]),
            S_model=float(theta[0] + theta[2]), S_lower=0.0, S_upper=float("inf"),
            decision_interval=(0.0, float("inf")), se_S=float("nan"),
            objective_value=obj, ci_type="unavailable", bound_hit=bool(hits), diagnostics=diag,
            runtime_seconds=time.time() - t_start, inference_status="unavailable:" + reason,
            profile_status=("unavailable", "unavailable") if compute_profile else None,
            jacobian_rank=rank,
        )

    # Multi-start initial guesses
    starts = [
        [0.4, max(0.05, eta_floor * 2), 0.4, kappa_0],
        [0.2, 0.1, 0.2, kappa_0],
        [0.7, 0.02, 0.5, kappa_0 * 0.9],
        [0.1, 0.5, 0.1, kappa_0 * 1.1],
    ]

    best_res = None
    best_fun = float("inf")
    failed_res = None

    for x0 in starts:
        x0_clipped = [
            np.clip(x0[i], bounds[i][0], bounds[i][1]) for i in range(4)
        ]
        try:
            res = minimize(
                objective,
                x0=x0_clipped,
                method="L-BFGS-B",
                bounds=bounds,
                options={"maxiter": 300, "ftol": 1e-9}
            )
        except (np.linalg.LinAlgError, FloatingPointError, ValueError):
            continue
        if not res.success or not np.isfinite(res.fun) or not np.all(np.isfinite(res.x)):
            failed_res = res
            continue
        if res.fun < best_fun:
            best_fun = res.fun
            best_res = res

    if best_res is None:
        return unavailable("optimizer_failure", failed_res)

    opt_a, opt_eta, opt_Q, opt_kappa = best_res.x
    S_model = float(opt_a + opt_Q)

    # Compute numerical Jacobian of beta(theta) at optimum (H+1 x 4)
    eps = np.cbrt(np.finfo(float).eps)
    _, beta_pred_opt = compute_impulse_response(opt_a, opt_eta, opt_Q, kappa=opt_kappa, H=H)
    residuals = beta_hat - beta_pred_opt

    J_mat = np.zeros((H + 1, 4), dtype=float)
    for i, (param_val, b_range) in enumerate(zip(best_res.x, bounds)):
        x_low, x_high = best_res.x.copy(), best_res.x.copy()
        step = eps * max(1.0, abs(param_val))
        x_low[i] = max(b_range[0], param_val - step)
        x_high[i] = min(b_range[1], param_val + step)
        if x_high[i] == x_low[i]:
            continue
        beta_low = compute_impulse_response(*x_low[:3], kappa=x_low[3], H=H)[1]
        beta_high = compute_impulse_response(*x_high[:3], kappa=x_high[3], H=H)[1]
        J_mat[:, i] = (beta_high - beta_low) / (x_high[i] - x_low[i])

    # Check unpenalized, whitened identification; a penalty cannot create it.
    singular_values = np.linalg.svd(np.linalg.cholesky(W).T @ J_mat, compute_uv=False)
    rank = int(np.sum(singular_values > singular_values[0] * 1e-8))
    if rank < 4:
        return unavailable("rank_deficient_jacobian", best_res, rank)

    # Half the GN Hessian of r'Wr + lambda(a^2+Q^2), consistently scaled.
    JtW = J_mat.T @ W
    info_mat = JtW @ J_mat + np.diag([reg_lambda, 0.0, reg_lambda, 0.0])

    # Contrast vector for S = a + Q is c = [1, 0, 1, 0]
    c_vec = np.array([1.0, 0.0, 1.0, 0.0])
    try:
        bread = np.linalg.solve(info_mat, np.eye(4))
        cov_theta = bread @ JtW @ cov @ JtW.T @ bread.T
        var_S = float(c_vec @ cov_theta @ c_vec)
    except np.linalg.LinAlgError:
        return unavailable("singular_bread", best_res, rank)
    if not np.isfinite(var_S) or var_S <= 0:
        return unavailable("invalid_sandwich_variance", best_res, rank)
    se_S = float(np.sqrt(var_S))

    z_crit = float(stats.norm.ppf((1.0 + confidence_level) / 2))
    sandwich_lower = max(0.0, S_model - z_crit * se_S)
    sandwich_upper = min(0.995 + q_max, S_model + z_crit * se_S)

    bound_hits = check_bound_hits(best_res.x, bounds, param_names)
    has_bound_hit = len(bound_hits) > 0

    # Profile likelihood / profile objective for S = a + Q
    profile_interval = None
    profile_status = None
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
                return float("nan")

            def sub_obj(sub_theta):
                a_sub, eta_sub, kap_sub = sub_theta
                Q_sub = S_val - a_sub
                return objective([a_sub, eta_sub, Q_sub, kap_sub])

            sub_bounds = [(a_min, a_max), bounds[1], bounds[3]]
            sub_values = []
            # Multiple starts reduce local-minimum sensitivity; no global guarantee.
            for theta0 in [best_res.x, *starts]:
                sub_x0 = [np.clip(theta0[i], *sub_bounds[j]) for j, i in enumerate([0, 1, 3])]
                try:
                    sub_res = minimize(sub_obj, x0=sub_x0, method="L-BFGS-B", bounds=sub_bounds,
                                       options={"maxiter": 300, "ftol": 1e-12})
                except (np.linalg.LinAlgError, FloatingPointError, ValueError):
                    continue
                if sub_res.success and np.isfinite(sub_res.fun) and np.all(np.isfinite(sub_res.x)):
                    sub_values.append(float(sub_res.fun))
            value = min(sub_values, default=float("nan"))
            # A materially better nuisance fit invalidates the reference minimum.
            if value < best_fun - 1e-6 * max(1.0, abs(best_fun)):
                return float("nan")
            return value

        profile_interval, profile_status = _profile_interval(
            profile_at_S, S_model, target_obj, 0.0, 0.995 + q_max, initial_step=se_S,
        )

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
    if profile_status is not None and "unavailable" in profile_status:
        rep_low, rep_high = 0.0, float("inf")
        ci_type = "unavailable"
    elif profile_interval is not None:
        rep_low, rep_high = profile_interval
        ci_type = "profile"
    else:
        rep_low, rep_high = sandwich_lower, sandwich_upper
        ci_type = "sandwich"

    res_ac1 = compute_residual_autocorr(residuals, lag=1)
    warnings = []
    if profile_status is not None and "unavailable" in profile_status:
        warnings.append("Profile optimization unavailable or inconsistent with the fitted minimum.")
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
        sandwich_interval=(float(sandwich_lower), float(sandwich_upper)),
        inference_status="local_asymptotic" if ci_type != "unavailable" else "unavailable:local_profile",
        profile_status=profile_status,
        jacobian_rank=rank,
    )
