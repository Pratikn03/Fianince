"""Mathematical identities, exact witnesses, identification maps, and conditioning fixtures.

Implements:
1. Proposition 8.1: Positive feedback boundary S = a + Q < 1 <=> rho(J) < 1, and the numerical distinction fixture.
2. Theorem 8.2 / Table 8.1: Retained rational witness of finite-window ambiguity.
3. Proposition G.1: Swapped-feedback non-identifiability under symmetric decay.
4. Theorem G.2: Channel experiment measurement map b = eta * U * q, rank conditions, and unknown-rate partial identification.
5. Definition G.3: Group intervention notation Delta Q_k = q_k and Delta G = q_k / (1 - a).
6. Boundary conditions: S = 1, zero feedback Q = 0, duplicate rates, and weak probes.
"""
from fractions import Fraction
from typing import Dict, Any, Tuple, Optional, Union
import numpy as np
from research_extension.mm_revision.states import (
    build_transition_matrix,
    spectral_radius,
    total_feedback_gain,
    steady_state_multiplier,
    compute_impulse_response,
)


def verify_spectral_vs_gain_distinction() -> Dict[str, Any]:
    """Verify that S = a + Q is not numerically equal to rho(J) for the audited baseline.

    Configuration:
      a = 0.4, q = (0.252, 0.168), eta = (0.5, 0.02)
    """
    a = 0.4
    q = np.array([0.252, 0.168], dtype=float)
    eta = np.array([0.5, 0.02], dtype=float)

    J = build_transition_matrix(a, eta, q)
    rho = spectral_radius(J)
    S = total_feedback_gain(a, q)
    G = steady_state_multiplier(a, q)

    diff = abs(S - rho)
    both_stable = (S < 1.0) and (rho < 1.0)

    return {
        "a": a,
        "q": q.tolist(),
        "eta": eta.tolist(),
        "S": float(S),
        "rho": float(rho),
        "G": float(G),
        "difference": float(diff),
        "both_stable": bool(both_stable),
        "is_numerically_equal": bool(diff < 1e-6),
        "correct_statement": f"S = {S:.2f} < 1 indicates stability, with rho(J) = {rho:.8f} < 1.",
    }


def get_rational_finite_window_witness() -> Dict[str, Any]:
    """Return the exact rational witness of finite-window ambiguity (Table 8.1).

    Both stable and unstable members have a = 2/5 and share rates (1, 1/2, 1/20).
    Stable member: q+ = (0, 12/65, 0)
    Unstable member: q- = (54/1235, 0, 240/247)

    They yield identical initial impulse responses:
      h_0 = 1
      h_1 = 2/5 = 0.4
      h_2 = 82/325 = 0.25230769...
      h_3 = 23/125 = 0.184
    First difference occurs at h_4:
      h_4^+ = 0.138428...
      h_4^- = 0.159198...
    """
    # Rational parameters
    a_rat = Fraction(2, 5)
    eta_rat = [Fraction(1, 1), Fraction(1, 2), Fraction(1, 20)]
    q_plus_rat = [Fraction(0, 1), Fraction(12, 65), Fraction(0, 1)]
    q_minus_rat = [Fraction(54, 1235), Fraction(0, 1), Fraction(240, 247)]

    # Float representations for simulation
    a = float(a_rat)
    eta = [float(e) for e in eta_rat]
    q_plus = [float(qp) for qp in q_plus_rat]
    q_minus = [float(qm) for qm in q_minus_rat]

    h_plus, _ = compute_impulse_response(a, eta, q_plus, kappa=1.0, H=5)
    h_minus, _ = compute_impulse_response(a, eta, q_minus, kappa=1.0, H=5)

    S_plus = total_feedback_gain(a, q_plus)
    S_minus = total_feedback_gain(a, q_minus)

    J_plus = build_transition_matrix(a, eta, q_plus)
    J_minus = build_transition_matrix(a, eta, q_minus)
    rho_plus = spectral_radius(J_plus)
    rho_minus = spectral_radius(J_minus)

    # Verify matching up to lag 3
    matches_up_to_lag3 = np.allclose(h_plus[:4], h_minus[:4], atol=1e-12)
    diff_at_lag4 = abs(h_plus[4] - h_minus[4])

    return {
        "stable_member": {
            "a": a,
            "q": q_plus,
            "eta": eta,
            "S": S_plus,
            "rho": rho_plus,
            "h": h_plus[:5].tolist(),
        },
        "unstable_member": {
            "a": a,
            "q": q_minus,
            "eta": eta,
            "S": S_minus,
            "rho": rho_minus,
            "h": h_minus[:5].tolist(),
        },
        "matches_up_to_lag3": bool(matches_up_to_lag3),
        "diverges_at_lag4": bool(diff_at_lag4 > 0.01),
        "h4_difference": float(diff_at_lag4),
    }


def verify_swapped_feedback_ambiguity(
    a: float = 0.4,
    eta_common: float = 0.05,
    q_pair: Tuple[float, float] = (0.3, 0.1),
    kappa: float = 0.02,
    H: int = 50
) -> Dict[str, Any]:
    """Verify Proposition G.1: Two economies with swapped feedback weights have identical aggregate price responses.

    Economy A: q = (q1, q2)
    Economy B: q = (q2, q1)
    Common rate: eta_1 = eta_2 = eta_common
    """
    q_A = [q_pair[0], q_pair[1]]
    q_B = [q_pair[1], q_pair[0]]
    eta = [eta_common, eta_common]

    h_A, beta_A = compute_impulse_response(a, eta, q_A, kappa=kappa, H=H)
    h_B, beta_B = compute_impulse_response(a, eta, q_B, kappa=kappa, H=H)

    max_price_diff = float(np.max(np.abs(beta_A - beta_B)))
    is_identical = bool(max_price_diff < 1e-15)

    # Policy suppression of Group 1
    # Delta Q_1 = q1
    delta_Q1_A = q_pair[0]
    delta_Q1_B = q_pair[1]

    # Delta G_1 = q1 / (1 - a)
    delta_G1_A = q_pair[0] / (1.0 - a)
    delta_G1_B = q_pair[1] / (1.0 - a)

    return {
        "max_price_diff": max_price_diff,
        "is_observationally_identical": is_identical,
        "economy_A": {
            "q": q_A,
            "delta_Q1": delta_Q1_A,
            "delta_G1": delta_G1_A,
        },
        "economy_B": {
            "q": q_B,
            "delta_Q1": delta_Q1_B,
            "delta_G1": delta_G1_B,
        },
        "suppression_effect_ratio": float(delta_Q1_A / delta_Q1_B),
    }


def recover_unknown_eta_and_q(
    U: np.ndarray,
    b: np.ndarray,
    Q: float
) -> Tuple[float, np.ndarray]:
    """Recover both unknown learning rate eta and weight vector q when aggregate Q is known.

    Model: b = eta * U * q
    When U has full column rank and Q = 1^T q > 0 is known:
      v = U^dagger b = eta * q
      1^T v = eta * (1^T q) = eta * Q
      eta = (1^T v) / Q
      q = v / eta = Q * v / (1^T v)

    Requires finite inputs, compatible b, nonnegative q, and 0 < eta <= 1.
    Compatibility and boundary checks allow only scale-relative floating-point
    roundoff (64 * max(U.shape) * machine epsilon). Tiny negative weights within
    that tolerance are clipped to zero; this is not a noisy-data estimator.
    """
    U = np.asarray(U, dtype=float)
    b = np.asarray(b, dtype=float).flatten()
    if U.ndim != 2 or 0 in U.shape:
        raise ValueError("U must be a nonempty two-dimensional matrix.")
    if b.size != U.shape[0]:
        raise ValueError("b must contain one response per row of U (matching rows).")
    if not np.isfinite(Q) or Q <= 0:
        raise ValueError("Q must be finite and strictly positive.")
    if not np.all(np.isfinite(U)) or not np.all(np.isfinite(b)):
        raise ValueError("U and b must be finite.")
    
    # Pseudo-inverse solution v = eta * q
    v, _, rank, _ = np.linalg.lstsq(U, b, rcond=None)
    if rank != U.shape[1]:
        raise ValueError("U must have full column rank to recover eta and q.")
    tol = 64.0 * max(U.shape) * np.finfo(float).eps
    response_scale = max(float(np.linalg.norm(b, ord=np.inf)),
                         float(np.linalg.norm(U, ord=np.inf) * np.linalg.norm(v, ord=np.inf)))
    if np.linalg.norm(U @ v - b, ord=np.inf) > tol * response_scale:
        raise ValueError("b must be compatible with the column space of U.")
    if np.any(v < -tol * np.linalg.norm(v, ord=np.inf)):
        raise ValueError("Recovered q must be nonnegative.")
    v = np.maximum(v, 0.0)
    sum_v = float(np.sum(v))
    eta_est = sum_v / float(Q)
    if not np.isfinite(eta_est) or eta_est <= 0 or eta_est > 1.0 + tol:
        raise ValueError("Recovered eta must lie in (0, 1].")
    eta_est = min(eta_est, 1.0)
    q_est = (v / eta_est)
    return eta_est, q_est


def analyze_channel_experiment_map(
    U: np.ndarray,
    eta: Optional[float] = None,
    aggregate_Q_known: bool = False
) -> Dict[str, Any]:
    """Analyze uniform/generic rank conditions for b = eta * U * q (Theorem G.2).

    This design-only analysis has no observed b or numeric Q, and does not decide
    pointwise uniqueness on the nonnegative boundary. Rank deficiency can coexist
    with a singleton feasible fiber (e.g. U=[1,1], b=0, known positive eta).
    ``unique_identification`` denotes the stated uniform rank guarantee, not a
    pointwise verdict; cases using unknown eta and known Q assume Q > 0.

    Delineates five distinct information cases:
      1. Known eta, full-rank U: unique componentwise recovery of q.
      2. Known eta, known aggregate Q, augmented full-rank [1^T; U]: unique recovery with n-1 probes.
      3. Unknown eta, full-rank U, known aggregate Q > 0: unique recovery of both eta and q.
      4. Unknown eta, full-rank U, lag-2 measurements only, no scale-fixing information:
         q lies on a scale ray {U^dagger b / eta : 0 < eta <= 1} for compatible nonzero data.
      5. Rank-deficient U with insufficient auxiliary constraints:
         possible nullspace ambiguity; feasible-set dimension depends on data and boundaries.

    Parameters:
      U: shape (m, n) measurement matrix specifying channel excitation weights across m experiments.
      eta: scalar common learning rate (if known), or None if unknown.
      aggregate_Q_known: bool, whether aggregate Q = 1^T q is already known from public probing.
    """
    U = np.asarray(U, dtype=float)
    if eta is not None and (not np.isfinite(eta) or not 0 < eta <= 1):
        raise ValueError("Known eta must be finite and lie in (0, 1].")
    m, n = U.shape

    rank_U = int(np.linalg.matrix_rank(U))
    
    # Augmented matrix if Q is known: [1^T; U]
    ones_row = np.ones((1, n), dtype=float)
    U_aug = np.vstack([ones_row, U])
    rank_aug = int(np.linalg.matrix_rank(U_aug))

    # Identifiability status across the 5 cases
    if eta is None:
        if aggregate_Q_known and rank_U == n:
            # Case 3: Unknown eta, full-rank U, known Q > 0 -> recovers both eta and q
            unique_identification = True
            status_reason = "Case 3: Unknown eta, but full-rank U and known aggregate Q > 0 uniquely identify both eta and q."
            min_probes_needed = n
        elif not aggregate_Q_known and rank_U == n:
            # Case 4: Unknown eta, full-rank U, no scale-fixing information -> ray ambiguity
            unique_identification = False
            status_reason = "Case 4: Unknown eta without aggregate Q: q is partially identified on a scale ray (U^dagger b / eta) for compatible nonzero data."
            min_probes_needed = None
        else:
            # Case 5: No uniform guarantee; pointwise feasible dimension is data-dependent.
            unique_identification = False
            status_reason = f"Case 5: Rank-deficient U (rank {rank_U}/{n}) permits possible nullspace ambiguity; pointwise uniqueness and dimension depend on data, nonnegativity, and auxiliary constraints."
            min_probes_needed = None
    else:
        if aggregate_Q_known:
            # Case 2: Known eta and known Q -> rank([1^T; U]) = n suffices
            unique_identification = (rank_aug == n)
            min_probes_needed = n - 1
            status_reason = f"Case 2: Known eta and known Q: rank([1^T; U]) = {rank_aug}/{n}. Identified: {unique_identification}."
        else:
            # Case 1: Known eta, unknown Q -> rank(U) = n needed
            unique_identification = (rank_U == n)
            min_probes_needed = n
            status_reason = f"Case 1: Known eta: rank(U) = {rank_U}/{n}. Identified: {unique_identification}."

    # Conditioning
    cond_U = float(np.linalg.cond(U)) if rank_U == n else float("inf")
    cond_aug = float(np.linalg.cond(U_aug)) if rank_aug == n else float("inf")

    return {
        "n_channels": n,
        "n_experiments": m,
        "rank_U": rank_U,
        "rank_augmented": rank_aug,
        "aggregate_Q_known": aggregate_Q_known,
        "eta_known": bool(eta is not None),
        "unique_identification": bool(unique_identification),
        "identification_scope": "uniform_generic_rank_not_pointwise_boundary",
        "condition_number_U": cond_U,
        "condition_number_aug": cond_aug,
        "status_reason": status_reason,
    }


def compute_group_intervention(
    a: float,
    q: Union[float, np.ndarray, list],
    suppressed_indices: list
) -> Dict[str, Any]:
    """Compute exact group suppression changes:
      Delta Q_k = sum_{i in suppressed} q_i
      Delta G = Delta Q_k / (1 - a)
    """
    q_arr = np.asarray(q, dtype=float)
    Q_full = float(np.sum(q_arr))
    S_full = float(a + Q_full)
    G_full = float(Q_full / (1.0 - a))

    delta_Q = float(np.sum(q_arr[suppressed_indices]))
    delta_G = float(delta_Q / (1.0 - a))

    Q_post = Q_full - delta_Q
    S_post = float(a + Q_post)
    G_post = float(Q_post / (1.0 - a))

    return {
        "a": a,
        "Q_full": Q_full,
        "S_full": S_full,
        "G_full": G_full,
        "delta_Q": delta_Q,
        "delta_G": delta_G,
        "Q_post": Q_post,
        "S_post": S_post,
        "G_post": G_post,
    }
