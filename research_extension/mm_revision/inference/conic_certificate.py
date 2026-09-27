"""Numerical conic outer relaxation under Contract I0; certification is withheld.

Estimated covariance uses the exact F pivot *conditional on* a Gaussian slope
and an independent, correctly scaled Wishart residual covariance. Known
covariance uses a Gaussian chi-square pivot. Neither assumption is checked here.
Residual-corrected dual objectives describe the represented floating-point LP.
Coordinate bounds, mass caps, envelopes, products and tangent cuts are not
assembled with proven outward rounding, nor is dual arithmetic interval-based.
Consequently these routines return numerical candidates, not structural proofs.
"""
from typing import Dict, Any, List, Tuple, Optional
import time
import numpy as np
from scipy import stats
from scipy.optimize import linprog

from research_extension.mm_revision.decisions import DecisionLabel, classify_interval


def _positive_integer(value: Any, name: str) -> None:
    if isinstance(value, (bool, np.bool_)) or not isinstance(value, (int, np.integer)) or value < 1:
        raise ValueError(f"{name} must be a positive integer")


def _validate_alpha(alpha: float) -> None:
    if not np.isscalar(alpha) or not np.isfinite(alpha) or not 0 < alpha < 1:
        raise ValueError("alpha must be finite and strictly between zero and one")


def _validate_covariance(beta_hat: np.ndarray, covariance: np.ndarray) -> None:
    if beta_hat.ndim != 1 or not np.all(np.isfinite(beta_hat)):
        raise ValueError("beta_hat must be a finite vector")
    if covariance.shape != (beta_hat.size, beta_hat.size) or not np.all(np.isfinite(covariance)):
        raise ValueError("covariance must be finite with shape (p, p)")
    # Do not silently symmetrize or ridge: that would change the calibrated set.
    if not np.array_equal(covariance, covariance.T):
        raise ValueError("covariance must be symmetric")
    try:
        np.linalg.cholesky(covariance)
    except np.linalg.LinAlgError as exc:
        raise ValueError("covariance must be positive definite") from exc


def _prepare_inputs(beta_hat, covariance, df, alpha, eta_floor, bins, a_bar, covariance_mode):
    beta_hat = np.asarray(beta_hat, dtype=float)
    covariance = np.asarray(covariance, dtype=float)
    _validate_covariance(beta_hat, covariance)
    p = beta_hat.size
    if p < 3:
        raise ValueError("at least three response coordinates are required")
    _validate_alpha(alpha)
    _positive_integer(bins, "bins")
    if not np.isscalar(eta_floor) or not np.isfinite(eta_floor) or not 0 < eta_floor <= 1:
        raise ValueError("eta_floor must be finite and in (0, 1]")
    if not np.isscalar(a_bar) or not np.isfinite(a_bar) or a_bar < 0:
        raise ValueError("a_bar must be finite and nonnegative")
    if covariance_mode not in ("estimated", "known"):
        raise ValueError("covariance_mode must be 'estimated' or 'known'")
    if df is not None or covariance_mode == "estimated":
        _positive_integer(df, "df")
    if covariance_mode == "estimated":
        k2, f_crit, df1, df2 = hotelling_f_critical_value(p, df + 2, alpha)
        distribution = "F"
        assumptions = "Gaussian slope independent of correctly scaled Wishart residual covariance"
    else:
        k2 = float(stats.chi2.isf(alpha, p))
        f_crit, df1, df2 = None, p, None
        distribution = "chi2"
        assumptions = "Gaussian slope with known sampling covariance"
    if not np.isfinite(k2) or k2 <= 0:
        raise ValueError("calibrated radius must be finite and positive")
    metadata = dict(covariance_mode=covariance_mode, radius_distribution=distribution,
                    radius_squared=k2, k_alpha_sq=k2, k_alpha=float(np.sqrt(k2)),
                    alpha=float(alpha), df=df, df1=df1, df2=df2, f_critical=f_crit,
                    calibration_assumptions=assumptions)
    return beta_hat, covariance, metadata


def _unverified_result(metadata):
    return dict(**metadata, S_lower=float("nan"), S_upper=float("nan"),
                decision=DecisionLabel.ABSTAIN, numerical_decision=DecisionLabel.ABSTAIN,
                certified=False, certification_status="unverified_constraint_rounding",
                is_definite=False, is_conflict=False, solver_success=False,
                endpoint_bound_status="not_computed", mass_cap_M=None,
                weak_dominance_over_box=None, box_comparison_status="not_computed",
                box_lower=None, box_upper=None)


def hotelling_f_critical_value(p: int, R: int, alpha: float = 0.05) -> Tuple[float, float, int, int]:
    """F radius under Gaussian slope / independent Wishart covariance assumptions."""
    _positive_integer(p, "p")
    _positive_integer(R, "R")
    _validate_alpha(alpha)
    nu = R - 2
    df1 = p
    df2 = nu - p + 1
    if df2 <= 0:
        raise ValueError(f"Insufficient residual degrees of freedom: nu - p + 1 = {df2} <= 0.")
    f_crit = float(stats.f.isf(alpha, df1, df2))
    k_alpha_sq = float((nu * p / df2) * f_crit)
    if not np.isfinite(k_alpha_sq) or k_alpha_sq <= 0:
        raise ValueError("calibrated F radius must be finite and positive")
    return k_alpha_sq, f_crit, df1, df2


def compute_coordinate_bounds_from_ellipsoid(
    beta_hat: np.ndarray, V: np.ndarray, k_alpha: float
) -> Tuple[np.ndarray, np.ndarray]:
    """Compute coordinate enclosure [L, U] from ellipsoid E_alpha."""
    beta_hat = np.asarray(beta_hat, dtype=float)
    V = np.asarray(V, dtype=float)
    _validate_covariance(beta_hat, V)
    if not np.isfinite(k_alpha) or k_alpha < 0:
        raise ValueError("k_alpha must be finite and nonnegative")
    diag_V = np.diag(V)
    half_widths = k_alpha * np.sqrt(diag_V)
    L = np.maximum(0.0, beta_hat - half_widths)
    U = beta_hat + half_widths
    return L, U


def compute_rate_bin_envelopes(
    j: int, bin_edges: List[Tuple[float, float]]
) -> Tuple[np.ndarray, np.ndarray]:
    """Compute continuous rate-bin envelopes [ell_{j, ell}, u_{j, ell}] on bin partitions."""
    ell_list = []
    u_list = []
    eta_star = 1.0 / (j + 1.0)

    for eta_left, eta_right in bin_edges:
        val_left = float(eta_left * ((1.0 - eta_left) ** j))
        val_right = float(eta_right * ((1.0 - eta_right) ** j))
        min_val = min(val_left, val_right)

        candidates = [val_left, val_right]
        if eta_left <= eta_star <= eta_right:
            candidates.append(float(eta_star * ((1.0 - eta_star) ** j)))
        max_val = max(candidates)

        ell_list.append(min_val)
        u_list.append(max_val)

    return np.array(ell_list, dtype=float), np.array(u_list, dtype=float)


def residual_corrected_dual_lower_bound(
    c: np.ndarray,
    A_ub: Optional[np.ndarray],
    b_ub: Optional[np.ndarray],
    A_eq: Optional[np.ndarray],
    b_eq: Optional[np.ndarray],
    bounds: List[Tuple[float, float]],
    y_ub: Optional[np.ndarray],
    y_eq: Optional[np.ndarray],
) -> float:
    """Numerically correct dual stationarity using finite variable bounds.

    Multipliers follow the Lagrangian convention: y_ub >= 0 for A_ub x <= b_ub,
    and unrestricted y_eq. Negate SciPy marginals before passing them here.
    The formula is a lower bound in exact arithmetic, but longdouble evaluation
    is not directed rounding and does not certify the full structural assembly.
    """
    c = np.asarray(c, dtype=np.longdouble)
    r = c.copy()

    term_val = np.longdouble(0.0)

    if A_ub is not None and b_ub is not None and y_ub is not None:
        y_ub_safe = np.maximum(0.0, np.asarray(y_ub, dtype=np.longdouble))
        r += np.asarray(A_ub, dtype=np.longdouble).T @ y_ub_safe
        term_val -= np.asarray(b_ub, dtype=np.longdouble) @ y_ub_safe

    if A_eq is not None and b_eq is not None and y_eq is not None:
        y_eq_safe = np.asarray(y_eq, dtype=np.longdouble)
        r += np.asarray(A_eq, dtype=np.longdouble).T @ y_eq_safe
        term_val -= np.asarray(b_eq, dtype=np.longdouble) @ y_eq_safe

    box_sum = np.longdouble(0.0)
    for i, (l_i, u_i) in enumerate(bounds):
        r_i = r[i]
        b1 = r_i * np.longdouble(l_i)
        b2 = r_i * np.longdouble(u_i)
        box_sum += min(b1, b2)

    return float(term_val + box_sum)


def _dual_from_result(c, A_ub, b_ub, A_eq, b_eq, bounds, result):
    """Use all rows of the LP actually solved, with SciPy's sign convention."""
    value = residual_corrected_dual_lower_bound(
        c, A_ub, b_ub, A_eq, b_eq, bounds,
        -result.ineqlin.marginals if A_ub is not None else None,
        -result.eqlin.marginals if A_eq is not None else None)
    if not np.isfinite(value):
        raise ValueError("dual residual correction produced a nonfinite value")
    return value


def _solve_with_cuts(c, A_ub, b_ub, A_eq, b_eq, bounds,
                     beta_hat, covariance, k2, beta_indices, max_cuts):
    """Solve one objective, retaining the complete last solved LP and its dual.

    max_cuts is the maximum number of LP solves *per endpoint*. At most
    max_cuts - 1 cuts can be added; no final, unsolved cut is reported.
    Convergence is a numerical separation diagnostic, never certification.
    """
    _positive_integer(max_cuts, "max_cuts")
    curr_A = np.asarray(A_ub, dtype=float).copy()
    curr_b = np.asarray(b_ub, dtype=float).copy()
    chol = np.linalg.cholesky(covariance)
    cuts = 0
    for iteration in range(max_cuts):
        res = linprog(c, A_ub=curr_A, b_ub=curr_b, A_eq=A_eq, b_eq=b_eq,
                      bounds=bounds, method="highs")
        info = dict(result=res, A_ub=curr_A, b_ub=curr_b, A_eq=A_eq, b_eq=b_eq,
                    cuts=cuts, lp_solves=iteration + 1, dual_lower_bound=float("nan"),
                    dual_status="not_computed", ellipsoid_violation=None,
                    ellipsoid_distance_squared=None, separation_tolerance=None,
                    termination_status="solver_failure")
        if not res.success:
            return info
        try:
            info['dual_lower_bound'] = _dual_from_result(c, curr_A, curr_b, A_eq, b_eq, bounds, res)
            info['dual_status'] = 'numerically_corrected_dual'
        except (ValueError, AttributeError, TypeError, FloatingPointError) as exc:
            info['dual_status'] = 'dual_repair_failed'
            info['dual_error'] = str(exc)
            # Retain cut diagnostics even if no numerical dual can be recovered.
        diff = res.x[beta_indices] - beta_hat
        whitened = np.linalg.solve(chol, diff)
        d2 = float(whitened @ whitened)
        info['ellipsoid_distance_squared'] = d2
        info['ellipsoid_violation'] = max(0., d2 - k2)
        # Scale-aware stopping tolerance, not outward padding of an endpoint.
        tolerance = 64 * np.finfo(float).eps * max(1., k2, d2)
        info['separation_tolerance'] = tolerance
        if not np.isfinite(d2):
            info['termination_status'] = 'nonfinite_separation'
            return info
        if d2 <= k2 + tolerance:
            info['termination_status'] = 'converged'
            return info
        if iteration + 1 == max_cuts:
            info['termination_status'] = 'max_cuts_reached'
            return info
        # Support plane for the represented ellipsoid, evaluated numerically.
        direction = np.linalg.solve(chol.T, whitened) / np.sqrt(d2)
        row = np.zeros_like(c, dtype=float)
        row[beta_indices] = direction
        rhs = float(direction @ beta_hat + np.sqrt(k2))
        if not np.all(np.isfinite(row)) or not np.isfinite(rhs):
            info['termination_status'] = 'nonfinite_cut'
            return info
        curr_A = np.vstack((curr_A, row))
        curr_b = np.append(curr_b, rhs)
        cuts += 1


def fit_box_lp(
    beta_hat: np.ndarray,
    covariance: np.ndarray,
    df: int,
    alpha: float = 0.05,
    eta_floor: float = 0.002,
    bins: int = 16,
    a_bar: float = 1.0,
    covariance_mode: str = "estimated",
) -> Dict[str, Any]:
    """Numerical coordinate-box comparison using the same calibrated ellipsoid.

    Invalid inputs raise ValueError; successful numerical endpoints do not
    authorize a stability decision. See fit_conic_certificate for calibration.
    """
    t_start = time.time()
    beta_hat, covariance, metadata = _prepare_inputs(
        beta_hat, covariance, df, alpha, eta_floor, bins, a_bar, covariance_mode)
    output = _unverified_result(metadata)
    p = len(beta_hat)
    H = p - 1
    k_alpha = metadata['k_alpha']
    L, U = compute_coordinate_bounds_from_ellipsoid(beta_hat, covariance, k_alpha)

    if L[0] <= 1e-12:
        return dict(output, S_lower=0., S_upper=float("inf"),
                    status="insufficient_initial_impact", runtime=time.time() - t_start)

    if np.any(L > U):
        return dict(output, status="empty_coordinate_box", runtime=time.time() - t_start)

    M = float(U[2] / (eta_floor * L[0]))
    if not np.isfinite(M) or not np.all(np.isfinite(U)):
        return dict(output, status="nonfinite_assembly", runtime=time.time() - t_start)
    output['mass_cap_M'] = M

    # Rate bins
    if eta_floor < 1.0:
        edges = np.geomspace(eta_floor, 1.0, bins + 1)
        bin_edges = [(float(edges[i]), float(edges[i + 1])) for i in range(bins)]
    else:
        bin_edges = [(1.0, 1.0)]
        bins = 1

    ell_env = np.zeros((H - 1, bins))
    u_env = np.zeros((H - 1, bins))
    for j in range(H - 1):
        el, eu = compute_rate_bin_envelopes(j, bin_edges)
        ell_env[j, :] = el
        u_env[j, :] = eu

    A_box = []
    b_box = []

    # t = 0: a * L_0 <= U_1, - a * U_0 <= - L_1
    r_lo = np.zeros(1 + bins); r_lo[0] = L[0]
    A_box.append(r_lo); b_box.append(U[1])
    r_hi = np.zeros(1 + bins); r_hi[0] = -U[0]
    A_box.append(r_hi); b_box.append(-L[1])

    for t in range(1, H):
        r_lo = np.zeros(1 + bins); r_lo[0] = L[t]
        for ell in range(bins):
            for j in range(t):
                r_lo[1 + ell] += ell_env[j, ell] * L[t - 1 - j]
        A_box.append(r_lo); b_box.append(U[t + 1])

        r_hi = np.zeros(1 + bins); r_hi[0] = -U[t]
        for ell in range(bins):
            for j in range(t):
                r_hi[1 + ell] -= u_env[j, ell] * U[t - 1 - j]
        A_box.append(r_hi); b_box.append(-L[t + 1])

    row_m = np.zeros(1 + bins); row_m[1:] = 1.0
    A_box.append(row_m); b_box.append(M)

    bounds_box = [(0.0, a_bar)] + [(0.0, M) for _ in range(bins)]
    c_box = np.ones(1 + bins)

    r_lo = linprog(c_box, A_ub=A_box, b_ub=b_box, bounds=bounds_box, method="highs")
    r_hi = linprog(-c_box, A_ub=A_box, b_ub=b_box, bounds=bounds_box, method="highs")
    output.update(solver_success=bool(r_lo.success and r_hi.success),
                  solver_success_min=bool(r_lo.success), solver_success_max=bool(r_hi.success),
                  solver_status_min=int(r_lo.status), solver_status_max=int(r_hi.status),
                  solver_message_min=r_lo.message, solver_message_max=r_hi.message)

    if not (r_lo.success and r_hi.success):
        return dict(output, status="solver_failure", runtime=time.time() - t_start)
    try:
        s_lo = _dual_from_result(c_box, A_box, b_box, None, None, bounds_box, r_lo)
        negative_hi = _dual_from_result(-c_box, A_box, b_box, None, None, bounds_box, r_hi)
    except (ValueError, AttributeError, TypeError, FloatingPointError) as exc:
        return dict(output, status="dual_repair_failed", dual_error=str(exc), runtime=time.time() - t_start)
    s_hi = -negative_hi
    return dict(output, S_lower=s_lo, S_upper=s_hi,
                numerical_decision=classify_interval(s_lo, s_hi),
                status="numerical_candidate" if s_lo <= s_hi else "numerical_interval_conflict",
                endpoint_bound_status="numerically_corrected_dual", dual_lower_bound=s_lo,
                dual_lower_bound_negative_objective=negative_hi,
                primal_lower=float(r_lo.fun), primal_upper=float(-r_hi.fun),
                runtime=time.time() - t_start)


def fit_conic_certificate(
    beta_hat: np.ndarray,
    covariance: np.ndarray,
    df: int,
    alpha: float = 0.05,
    eta_floor: float = 0.002,
    bins: int = 16,
    a_bar: float = 1.0,
    max_cuts: int = 25,
    covariance_mode: str = "estimated",
) -> Dict[str, Any]:
    """Fit a numerical conic interval over a calibrated response ellipsoid.

    Parameters:
      beta_hat: (p,) estimated price response vector (p = H + 1).
      covariance: (p, p) finite symmetric positive-definite sampling covariance.
      df: residual degrees of freedom nu = R - 2; integer >= p for estimated
          covariance. Known covariance permits None (otherwise positive integer).
      alpha: nominal error probability (default 0.05).
      eta_floor: certified rate floor eta_min > 0.
      bins: number of rate bins for outer envelopes.
      a_bar: upper bound on persistence (default 1.0).
      max_cuts: maximum LP solves per endpoint (at most max_cuts - 1 cuts).
      covariance_mode: 'estimated' (default) uses an exact F radius conditional
          on a Gaussian slope independent of a correctly scaled Wishart residual
          estimate V = Sigma_hat / D. 'known' uses a chi-square radius for a
          Gaussian slope with known V. Unknown modes and invalid inputs raise
          ValueError; no covariance regularization is performed.

    Returns:
      Numerical S_lower/S_upper, numerical_decision, radius metadata, corrected
      dual objectives for c and -c, and separate solver/cut diagnostics.
      decision is ABSTAIN and certified is False until the entire outward
      assembly (including envelopes and cuts) is proved. A converged solve or
      a numerical box comparison does not establish that proof.
    """
    t_start = time.time()
    _positive_integer(max_cuts, "max_cuts")
    beta_hat, covariance, metadata = _prepare_inputs(
        beta_hat, covariance, df, alpha, eta_floor, bins, a_bar, covariance_mode)
    output = _unverified_result(metadata)
    p = len(beta_hat)
    H = p - 1
    k2 = metadata['radius_squared']
    k_alpha = metadata['k_alpha']

    # 3. Coordinate bounds & Mass cap
    L, U = compute_coordinate_bounds_from_ellipsoid(beta_hat, covariance, k_alpha)
    if L[0] <= 1e-12:
        return dict(output, S_lower=0., S_upper=float("inf"),
                    status="insufficient_initial_impact", runtime=time.time() - t_start)

    if np.any(L > U):
        return dict(output, status="empty_coordinate_box", runtime=time.time() - t_start)

    M = float(U[2] / (eta_floor * L[0]))
    if not np.isfinite(M) or not np.all(np.isfinite(U)):
        return dict(output, status="nonfinite_assembly", runtime=time.time() - t_start)
    output['mass_cap_M'] = M

    # 4. Continuous rate bins
    if eta_floor < 1.0:
        edges = np.geomspace(eta_floor, 1.0, bins + 1)
        bin_edges = [(float(edges[i]), float(edges[i + 1])) for i in range(bins)]
    else:
        bin_edges = [(1.0, 1.0)]
        bins = 1

    ell_env = np.zeros((H - 1, bins))
    u_env = np.zeros((H - 1, bins))
    for j in range(H - 1):
        el, eu = compute_rate_bin_envelopes(j, bin_edges)
        ell_env[j, :] = el
        u_env[j, :] = eu

    # 5. Variable indexing
    # x = [a, w_0..w_{B-1}, b_0..b_H, v_0..v_{H-1}, z_{0,0}..z_{B-1, H-2}]
    idx_a = 0
    idx_w = lambda ell: 1 + ell
    idx_b = lambda s: 1 + bins + s
    idx_v = lambda t: 1 + bins + p + t
    idx_z = lambda ell, s: 1 + bins + p + H + ell * (H - 1) + s
    n_vars = 1 + bins + p + H + bins * (H - 1)

    bounds = [None] * n_vars
    bounds[idx_a] = (0.0, a_bar)
    for ell in range(bins):
        bounds[idx_w(ell)] = (0.0, M)
    for s in range(p):
        bounds[idx_b(s)] = (float(L[s]), float(U[s]))
    for t in range(H):
        bounds[idx_v(t)] = (0.0, float(a_bar * U[t]))
    for ell in range(bins):
        for s in range(H - 1):
            bounds[idx_z(ell, s)] = (0.0, float(M * U[s]))

    # 6. Equalities
    A_eq = []
    b_eq = []
    # b_1 == v_0
    row_eq = np.zeros(n_vars)
    row_eq[idx_b(1)] = 1.0
    row_eq[idx_v(0)] = -1.0
    A_eq.append(row_eq)
    b_eq.append(0.0)

    # 7. Inequalities
    A_ub = []
    b_ub = []

    # sum w_ell <= M
    row_w = np.zeros(n_vars)
    for ell in range(bins):
        row_w[idx_w(ell)] = 1.0
    A_ub.append(row_w)
    b_ub.append(M)

    # McCormick for v_t = a * b_t
    for t in range(H):
        # v_t >= L_t a => L_t a - v_t <= 0
        r1 = np.zeros(n_vars); r1[idx_a] = L[t]; r1[idx_v(t)] = -1.0
        A_ub.append(r1); b_ub.append(0.0)
        # v_t >= a_bar b_t + U_t a - a_bar U_t
        r2 = np.zeros(n_vars); r2[idx_b(t)] = a_bar; r2[idx_a] = U[t]; r2[idx_v(t)] = -1.0
        A_ub.append(r2); b_ub.append(a_bar * U[t])
        # v_t <= a_bar b_t + L_t a - a_bar L_t
        r3 = np.zeros(n_vars); r3[idx_v(t)] = 1.0; r3[idx_b(t)] = -a_bar; r3[idx_a] = -L[t]
        A_ub.append(r3); b_ub.append(-a_bar * L[t])
        # v_t <= U_t a
        r4 = np.zeros(n_vars); r4[idx_v(t)] = 1.0; r4[idx_a] = -U[t]
        A_ub.append(r4); b_ub.append(0.0)

    # McCormick for z_{\ell, s} = w_\ell * b_s
    for ell in range(bins):
        for s in range(H - 1):
            r1 = np.zeros(n_vars); r1[idx_w(ell)] = L[s]; r1[idx_z(ell, s)] = -1.0
            A_ub.append(r1); b_ub.append(0.0)
            r2 = np.zeros(n_vars); r2[idx_b(s)] = M; r2[idx_w(ell)] = U[s]; r2[idx_z(ell, s)] = -1.0
            A_ub.append(r2); b_ub.append(M * U[s])
            r3 = np.zeros(n_vars); r3[idx_z(ell, s)] = 1.0; r3[idx_b(s)] = -M; r3[idx_w(ell)] = -L[s]
            A_ub.append(r3); b_ub.append(-M * L[s])
            r4 = np.zeros(n_vars); r4[idx_z(ell, s)] = 1.0; r4[idx_w(ell)] = -U[s]
            A_ub.append(r4); b_ub.append(0.0)

    # Recurrence outer envelopes: t = 1 .. H - 1
    for t in range(1, H):
        # b_{t+1} >= v_t + sum ell_{j, ell} z_{\ell, t-1-j}
        r_lo = np.zeros(n_vars)
        r_lo[idx_v(t)] = 1.0
        r_lo[idx_b(t + 1)] = -1.0
        for ell in range(bins):
            for j in range(t):
                r_lo[idx_z(ell, t - 1 - j)] += ell_env[j, ell]
        A_ub.append(r_lo); b_ub.append(0.0)

        # b_{t+1} <= v_t + sum u_{j, ell} z_{\ell, t-1-j}
        r_hi = np.zeros(n_vars)
        r_hi[idx_b(t + 1)] = 1.0
        r_hi[idx_v(t)] = -1.0
        for ell in range(bins):
            for j in range(t):
                r_hi[idx_z(ell, t - 1 - j)] -= u_env[j, ell]
        A_ub.append(r_hi); b_ub.append(0.0)

    # Linear objective vector c: S = a + sum w_ell
    c_obj = np.zeros(n_vars)
    c_obj[idx_a] = 1.0
    for ell in range(bins):
        c_obj[idx_w(ell)] = 1.0

    # Each objective keeps its own complete solved tangent matrix and dual.
    solve_args = dict(A_ub=np.asarray(A_ub), b_ub=np.asarray(b_ub),
                      A_eq=np.asarray(A_eq), b_eq=np.asarray(b_eq), bounds=bounds,
                      beta_hat=beta_hat, covariance=covariance, k2=k2,
                      beta_indices=np.arange(idx_b(0), idx_b(p - 1) + 1), max_cuts=max_cuts)
    minimum = _solve_with_cuts(c=c_obj, **solve_args)
    maximum = _solve_with_cuts(c=-c_obj, **solve_args)
    for name, endpoint in (("min", minimum), ("max", maximum)):
        res = endpoint['result']
        output.update({
            f"termination_{name}": endpoint['termination_status'],
            f"solver_success_{name}": bool(res.success),
            f"solver_status_{name}": int(res.status),
            f"solver_message_{name}": res.message,
            f"cuts_{name}": endpoint['cuts'],
            f"lp_solves_{name}": endpoint['lp_solves'],
            f"solved_inequalities_{name}": len(endpoint['b_ub']),
            f"ellipsoid_violation_{name}": endpoint['ellipsoid_violation'],
            f"ellipsoid_distance_squared_{name}": endpoint['ellipsoid_distance_squared'],
            f"separation_tolerance_{name}": endpoint['separation_tolerance'],
            f"dual_status_{name}": endpoint['dual_status'],
        })
        if 'dual_error' in endpoint:
            output[f'dual_error_{name}'] = endpoint['dual_error']
    output['solver_success'] = bool(minimum['result'].success and maximum['result'].success)
    output['cut_converged'] = all(e['termination_status'] == 'converged' for e in (minimum, maximum))
    if not output['solver_success']:
        return dict(output, status="solver_failure", runtime=time.time() - t_start)
    if any(e['dual_status'] != 'numerically_corrected_dual' for e in (minimum, maximum)):
        return dict(output, status="dual_repair_failed", runtime=time.time() - t_start)

    s_lo = minimum['dual_lower_bound']
    negative_hi = maximum['dual_lower_bound']
    s_hi = -negative_hi
    output.update(S_lower=s_lo, S_upper=s_hi, dual_lower_bound=s_lo,
                  dual_lower_bound_negative_objective=negative_hi,
                  primal_lower=float(minimum['result'].fun), primal_upper=float(-maximum['result'].fun),
                  endpoint_bound_status="numerically_corrected_dual",
                  numerical_decision=classify_interval(s_lo, s_hi),
                  status="numerical_candidate" if s_lo <= s_hi else "numerical_interval_conflict")

    box_res = fit_box_lp(beta_hat, covariance, df, alpha, eta_floor, bins, a_bar,
                        covariance_mode=covariance_mode)
    output.update(box_lower=box_res['S_lower'], box_upper=box_res['S_upper'],
                  box_status=box_res['status'])
    if output['status'] == box_res['status'] == 'numerical_candidate':
        # This is an observed numerical comparison, not a theorem verification.
        output['weak_dominance_over_box'] = bool(box_res['S_lower'] <= s_lo and s_hi <= box_res['S_upper'])
        output['box_comparison_status'] = 'computed_numerically'
    output['runtime'] = time.time() - t_start
    return output
