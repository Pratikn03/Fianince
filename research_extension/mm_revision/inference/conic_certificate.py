"""Conic outer relaxation certificate over response ellipsoid under Contract I0.

Implements:
1. Exact Hotelling F-calibrated ellipsoid:
   E_alpha = {b : (b - beta_hat)^T V^{-1} (b - beta_hat) <= k_alpha^2}
   where k_alpha^2 = [nu * p / (nu - p + 1)] * F^{-1}_{p, nu - p + 1}(1 - alpha), nu = R - 2.
2. Data-derived finite mass cap M = U_2 / (eta_min * L_0) (Lemma 7.1).
3. Continuous rate-bin envelopes covering off-grid rates (Section 7.2).
4. McCormick bilinear product lifting for (a * b_t) and (w_ell * b_s) (Section 7.3).
5. Outer cutting planes with HiGHS simplex solver (Theorem 7.2).
6. Dual residual repair for rigorous floating-point outward certification (Proposition 9.1).
7. Weak dominance verification relative to the coordinate box LP (Theorem 7.3).
"""
from typing import Dict, Any, List, Tuple, Optional
import time
import numpy as np
from scipy import stats
from scipy.optimize import linprog

from research_extension.mm_revision.decisions import DecisionLabel, classify_interval


def hotelling_f_critical_value(p: int, R: int, alpha: float = 0.05) -> Tuple[float, float, int, int]:
    """Calculate exact Hotelling F-critical value and squared radius k_alpha^2."""
    nu = R - 2
    df1 = p
    df2 = nu - p + 1
    if df2 <= 0:
        raise ValueError(f"Insufficient residual degrees of freedom: nu - p + 1 = {df2} <= 0.")
    f_crit = float(stats.f.ppf(1.0 - alpha, df1, df2))
    k_alpha_sq = float((nu * p / df2) * f_crit)
    return k_alpha_sq, f_crit, df1, df2


def compute_coordinate_bounds_from_ellipsoid(
    beta_hat: np.ndarray, V: np.ndarray, k_alpha: float
) -> Tuple[np.ndarray, np.ndarray]:
    """Compute coordinate enclosure [L, U] from ellipsoid E_alpha."""
    beta_hat = np.asarray(beta_hat, dtype=float)
    diag_V = np.diag(V)
    half_widths = k_alpha * np.sqrt(np.maximum(0.0, diag_V))
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
    """Compute certified numerical dual lower bound (Proposition 9.1)."""
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


def fit_box_lp(
    beta_hat: np.ndarray,
    covariance: np.ndarray,
    df: int,
    alpha: float = 0.05,
    eta_floor: float = 0.002,
    bins: int = 16,
    a_bar: float = 1.0,
) -> Dict[str, Any]:
    """Fit stability interval using coordinate box LP over the same ellipsoid projection [L, U]."""
    p = len(beta_hat)
    H = p - 1
    R = df + 2
    k2, _, _, _ = hotelling_f_critical_value(p, R, alpha)
    k_alpha = np.sqrt(k2)
    L, U = compute_coordinate_bounds_from_ellipsoid(beta_hat, covariance, k_alpha)

    if L[0] <= 1e-12:
        return {
            "S_lower": 0.0,
            "S_upper": float("inf"),
            "decision": DecisionLabel.ABSTAIN,
            "status": "insufficient_initial_impact",
        }

    M = float(U[2] / (eta_floor * L[0]))

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

    if not (r_lo.success and r_hi.success):
        return {
            "S_lower": float("nan"),
            "S_upper": float("nan"),
            "decision": DecisionLabel.CONFLICT,
            "status": "infeasible_box_lp",
        }

    s_lo = max(0.0, float(r_lo.fun))
    s_hi = max(0.0, float(-r_hi.fun))

    return {
        "S_lower": s_lo,
        "S_upper": s_hi,
        "decision": classify_interval(s_lo, s_hi, threshold=1.0),
        "status": "ok",
        "mass_cap_M": M,
    }


def fit_conic_certificate(
    beta_hat: np.ndarray,
    covariance: np.ndarray,
    df: int,
    alpha: float = 0.05,
    eta_floor: float = 0.002,
    bins: int = 16,
    a_bar: float = 1.0,
    max_cuts: int = 25,
) -> Dict[str, Any]:
    """Fit covariance-aware conic certificate over response ellipsoid under Contract I0.

    Parameters:
      beta_hat: (p,) estimated price response vector (p = H + 1).
      covariance: (p, p) estimated sampling covariance V = Sigma_hat / D.
      df: degrees of freedom nu = R - 2.
      alpha: nominal error probability (default 0.05).
      eta_floor: certified rate floor eta_min > 0.
      bins: number of rate bins for outer envelopes.
      a_bar: upper bound on persistence (default 1.0).
      max_cuts: maximum outer tangent cuts to add to ellipsoid.

    Returns:
      Dict with S_lower, S_upper, decision, mass_cap_M, dual_lower_bound,
      weak_dominance_over_box, runtime, status.
    """
    t_start = time.time()
    beta_hat = np.asarray(beta_hat, dtype=float)
    covariance = np.asarray(covariance, dtype=float)
    p = len(beta_hat)
    H = p - 1
    R = df + 2

    # 1. Hotelling F-calibration
    k2, f_crit, df1, df2 = hotelling_f_critical_value(p, R, alpha)
    k_alpha = np.sqrt(k2)

    # 2. Invert covariance with ridge protection if near-singular
    try:
        V_inv = np.linalg.inv(covariance)
    except np.linalg.LinAlgError:
        ridge = 1e-10 * np.trace(covariance) * np.eye(p)
        V_inv = np.linalg.inv(covariance + ridge)

    # 3. Coordinate bounds & Mass cap
    L, U = compute_coordinate_bounds_from_ellipsoid(beta_hat, covariance, k_alpha)
    if L[0] <= 1e-12:
        return {
            "S_lower": 0.0,
            "S_upper": float("inf"),
            "decision": DecisionLabel.ABSTAIN,
            "is_definite": False,
            "is_conflict": False,
            "status": "insufficient_initial_impact",
            "mass_cap_M": None,
            "k_alpha": k_alpha,
            "runtime": time.time() - t_start,
        }

    M = float(U[2] / (eta_floor * L[0]))

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

    # Solve min and max with outer cutting planes
    def solve_with_cuts(sense: float) -> Tuple[Optional[np.ndarray], Optional[Any], int, str]:
        c = sense * c_obj
        curr_A_ub = list(A_ub)
        curr_b_ub = list(b_ub)
        cuts = 0
        last_res = None

        for it in range(max_cuts):
            res = linprog(
                c,
                A_ub=np.array(curr_A_ub),
                b_ub=np.array(curr_b_ub),
                A_eq=np.array(A_eq),
                b_eq=np.array(b_eq),
                bounds=bounds,
                method="highs",
            )
            last_res = res
            if not res.success:
                return None, res, cuts, "solver_failure"

            b_sol = res.x[idx_b(0):idx_b(p - 1) + 1]
            diff = b_sol - beta_hat
            d2 = float(diff @ V_inv @ diff)

            if d2 <= k2 + 1e-5:
                return res.x, res, cuts, "converged"

            # Add outer tangent hyperplane: d_dir^T b <= d_dir^T beta_hat + k_alpha
            g = V_inv @ diff
            norm_g = np.sqrt(max(1e-16, float(g @ covariance @ g)))
            d_dir = g / norm_g

            row_cut = np.zeros(n_vars)
            for s in range(p):
                row_cut[idx_b(s)] = d_dir[s]
            curr_A_ub.append(row_cut)
            curr_b_ub.append(float(d_dir @ beta_hat + k_alpha))
            cuts += 1

        return last_res.x, last_res, cuts, "max_cuts_reached"

    x_min, res_min, cuts_min, status_min = solve_with_cuts(1.0)
    x_max, res_max, cuts_max, status_max = solve_with_cuts(-1.0)

    if x_min is None or x_max is None:
        return {
            "S_lower": float("nan"),
            "S_upper": float("nan"),
            "decision": DecisionLabel.CONFLICT,
            "is_definite": False,
            "is_conflict": True,
            "status": "model_conflict_or_infeasible",
            "runtime": time.time() - t_start,
        }

    s_lo_raw = float(x_min[idx_a] + sum(x_min[idx_w(ell)] for ell in range(bins)))
    s_hi_raw = float(x_max[idx_a] + sum(x_max[idx_w(ell)] for ell in range(bins)))

    # Dual residual repair for numerical outward guarantee (Proposition 9.1)
    try:
        y_ub_min = -res_min.ineqlin.marginals if hasattr(res_min, "ineqlin") else None
        y_eq_min = -res_min.eqlin.marginals if hasattr(res_min, "eqlin") else None
        dual_lo = residual_corrected_dual_lower_bound(
            c_obj,
            np.array(A_ub),
            np.array(b_ub),
            np.array(A_eq),
            np.array(b_eq),
            bounds,
            y_ub_min[:len(A_ub)] if y_ub_min is not None else None,
            y_eq_min,
        )
        s_lo = max(0.0, min(s_lo_raw, dual_lo))
    except Exception:
        s_lo = max(0.0, s_lo_raw - 1e-6)

    s_hi = max(s_lo, s_hi_raw + 1e-6)

    # Weak dominance check against box LP
    box_res = fit_box_lp(beta_hat, covariance, df, alpha, eta_floor, bins, a_bar)
    weak_dominance = True
    if box_res["status"] == "ok":
        # Conic enclosure must be within box enclosure (Theorem 7.3)
        # S_{box}^- <= S_{soc}^- <= S_{soc}^+ <= S_{box}^+
        s_box_lo = box_res["S_lower"]
        s_box_hi = box_res["S_upper"]
        weak_dominance = bool(s_box_lo <= s_lo + 1e-4 and s_hi <= s_box_hi + 1e-4)

    decision = classify_interval(s_lo, s_hi, threshold=1.0)

    return {
        "S_lower": s_lo,
        "S_upper": s_hi,
        "decision": decision,
        "is_definite": bool(decision in (DecisionLabel.STABLE, DecisionLabel.UNSTABLE)),
        "is_conflict": bool(decision == DecisionLabel.CONFLICT),
        "status": "ok",
        "mass_cap_M": M,
        "cuts_min": cuts_min,
        "cuts_max": cuts_max,
        "box_lower": box_res.get("S_lower"),
        "box_upper": box_res.get("S_upper"),
        "weak_dominance_over_box": weak_dominance,
        "runtime": float(time.time() - t_start),
    }
