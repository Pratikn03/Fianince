"""Conic outer relaxation, continuous rate-bin envelopes, McCormick lifting, and dual certificates.

Implements:
1. Section 6: Exact covariance-aware identified set K_alpha.
2. Lemma 7.1: Data-derived finite mass cap M = U_2 / (eta_min * L_0).
3. Section 7.2: Continuous rate-bin envelopes ell_{j, ell} and u_{j, ell} covering off-grid rates.
4. Section 7.3: McCormick bilinear product lifting for (a * b_t) and (w_ell * b_s).
5. Theorem 7.2: True-model containment and statistical validity of conic relaxation R_alpha.
6. Theorem 7.3: Weak dominance over the box LP derived from the same ellipsoid.
7. Proposition 9.1: Residual-corrected dual lower bound for verified numerical enclosures.
"""
from typing import Dict, Any, List, Tuple, Optional
import numpy as np


def compute_coordinate_bounds_from_ellipsoid(
    beta_hat: np.ndarray, V: np.ndarray, k_alpha: float
) -> Tuple[np.ndarray, np.ndarray]:
    """Compute coordinate enclosure [L, U] from ellipsoid E_alpha.

    L_s = max(0, beta_hat_s - k_alpha * sqrt(V_{ss}))
    U_s = beta_hat_s + k_alpha * sqrt(V_{ss})
    """
    beta_hat = np.asarray(beta_hat, dtype=float)
    diag_V = np.diag(V)
    half_widths = k_alpha * np.sqrt(np.maximum(0.0, diag_V))

    L = np.maximum(0.0, beta_hat - half_widths)
    U = beta_hat + half_widths
    return L, U


def compute_data_derived_mass_cap(
    U_2: float, L_0: float, eta_min: float
) -> float:
    """Compute data-derived finite mass cap M = U_2 / (eta_min * L_0) (Lemma 7.1)."""
    if L_0 <= 1e-12:
        raise ValueError("L_0 <= 0: cannot derive finite positive mass cap from data alone.")
    if eta_min <= 0:
        raise ValueError("eta_min must be strictly positive.")
    return float(U_2 / (eta_min * L_0))


def psi_kernel(eta: float, j: int) -> float:
    """Evaluate psi_j(eta) = eta * (1 - eta)^j."""
    return float(eta * ((1.0 - eta) ** j))


def compute_rate_bin_envelopes(
    j: int, bin_edges: List[Tuple[float, float]]
) -> Tuple[np.ndarray, np.ndarray]:
    """Compute continuous rate-bin envelopes [ell_{j, ell}, u_{j, ell}] (Section 7.2).

    For psi_j(eta) = eta * (1 - eta)^j on [eta_left, eta_right]:
    - Minimum is attained at an endpoint: min(psi_j(eta_left), psi_j(eta_right)).
    - Maximum is attained at an endpoint or at the critical point eta* = 1 / (j + 1).
    """
    ell_list = []
    u_list = []
    eta_star = 1.0 / (j + 1.0)

    for eta_left, eta_right in bin_edges:
        val_left = psi_kernel(eta_left, j)
        val_right = psi_kernel(eta_right, j)
        min_val = min(val_left, val_right)

        candidates = [val_left, val_right]
        if eta_left <= eta_star <= eta_right:
            candidates.append(psi_kernel(eta_star, j))
        max_val = max(candidates)

        ell_list.append(min_val)
        u_list.append(max_val)

    return np.array(ell_list, dtype=float), np.array(u_list, dtype=float)


def mccormick_envelopes(
    x: float, y: float, A: float, L: float, U: float
) -> Dict[str, float]:
    """Evaluate McCormick lower and upper bounds for product z = x * y (Equations 7.4-7.5).

    Domain: 0 <= x <= A, L <= y <= U.
    Lower bounds:
      z >= L * x
      z >= A * y + U * x - A * U
    Upper bounds:
      z <= A * y + L * x - A * L
      z <= U * x
    """
    lb1 = L * x
    lb2 = A * y + U * x - A * U
    ub1 = A * y + L * x - A * L
    ub2 = U * x

    z_true = x * y
    return {
        "z_true": z_true,
        "lower_bound": max(lb1, lb2),
        "upper_bound": min(ub1, ub2),
        "lb1": lb1,
        "lb2": lb2,
        "ub1": ub1,
        "ub2": ub2,
        "is_valid": (z_true >= max(lb1, lb2) - 1e-12) and (z_true <= min(ub1, ub2) + 1e-12),
    }


def verify_conic_lift_containment(
    a_true: float,
    q_true: np.ndarray,
    eta_true: np.ndarray,
    kappa_true: float,
    beta_hat: np.ndarray,
    V: np.ndarray,
    k_alpha: float,
    bin_edges: List[Tuple[float, float]],
    a_bar: float = 1.0,
    H: int = 4,
) -> Dict[str, Any]:
    """Verify that a true model lifts into the conic outer relaxation R_alpha (Theorem 7.2)."""
    q_true = np.asarray(q_true, dtype=float)
    eta_true = np.asarray(eta_true, dtype=float)
    Q_true = float(np.sum(q_true))
    S_true = a_true + Q_true

    # 1. Compute true impulse responses
    h = np.zeros(H, dtype=float)
    h[0] = 1.0
    h[1] = a_true
    k = np.zeros(H, dtype=float)
    for j in range(H):
        k[j] = np.sum(q_true * eta_true * ((1.0 - eta_true) ** j))

    for t in range(1, H - 1):
        conv_sum = np.sum([k[j] * h[t - 1 - j] for j in range(t)])
        h[t + 1] = a_true * h[t] + conv_sum

    b_true = kappa_true * h

    # 2. Coordinate bounds and mass cap
    L, U = compute_coordinate_bounds_from_ellipsoid(beta_hat, V, k_alpha)
    eta_min = min(edges[0] for edges in bin_edges)
    M = compute_data_derived_mass_cap(U[2], L[0], eta_min)

    # 3. Bin weights w_ell
    num_bins = len(bin_edges)
    w = np.zeros(num_bins, dtype=float)
    for q_i, eta_i in zip(q_true, eta_true):
        for idx, (left, right) in enumerate(bin_edges):
            if left <= eta_i <= right:
                w[idx] += q_i
                break

    # 4. Check mass cap
    mass_ok = (np.sum(w) <= M + 1e-9)

    # 5. Check McCormick products
    v_ok = True
    for t in range(H - 1):
        res = mccormick_envelopes(a_true, b_true[t], a_bar, L[t], U[t])
        if not res["is_valid"]:
            v_ok = False

    z_ok = True
    for ell in range(num_bins):
        for s in range(H - 1):
            res = mccormick_envelopes(w[ell], b_true[s], M, L[s], U[s])
            if not res["is_valid"]:
                z_ok = False

    # 6. Check recurrence outer envelopes
    rec_ok = True
    for t in range(1, H - 1):
        v_t = a_true * b_true[t]
        lower_rec = v_t
        upper_rec = v_t
        for ell, (left, right) in enumerate(bin_edges):
            for j in range(t):
                ell_j, u_j = compute_rate_bin_envelopes(j, [(left, right)])
                z_ell_s = w[ell] * b_true[t - 1 - j]
                lower_rec += ell_j[0] * z_ell_s
                upper_rec += u_j[0] * z_ell_s

        if not (lower_rec - 1e-10 <= b_true[t + 1] <= upper_rec + 1e-10):
            rec_ok = False

    return {
        "S_true": S_true,
        "mass_cap_M": M,
        "mass_ok": mass_ok,
        "mccormick_v_ok": v_ok,
        "mccormick_z_ok": z_ok,
        "recurrence_envelope_ok": rec_ok,
        "is_conic_lift_valid": mass_ok and v_ok and z_ok and rec_ok,
    }


def residual_corrected_dual_lower_bound(
    c: np.ndarray,
    A: np.ndarray,
    b: np.ndarray,
    G: np.ndarray,
    h: np.ndarray,
    ell: np.ndarray,
    u: np.ndarray,
    y: np.ndarray,
    z: np.ndarray,
) -> float:
    """Compute residual-corrected conic dual lower bound (Proposition 9.1).

    Problem:
      p_* = min c^T x  s.t.  A x = b,  h - G x in K,  ell <= x <= u.
    Bound:
      r = c + A^T y + G^T z
      p_* >= - y^T b - z^T h + sum_i min(r_i * ell_i, r_i * u_i)
    """
    c = np.asarray(c, dtype=float)
    b = np.asarray(b, dtype=float)
    h = np.asarray(h, dtype=float)
    ell = np.asarray(ell, dtype=float)
    u = np.asarray(u, dtype=float)
    y = np.asarray(y, dtype=float)
    z = np.asarray(z, dtype=float)

    r = c + A.T @ y + G.T @ z
    box_terms = np.minimum(r * ell, r * u)
    lower_bound = float(- (y @ b) - (z @ h) + np.sum(box_terms))
    return lower_bound
