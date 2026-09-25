"""Group identification, unknown-rate polyhedral sets, and aggregate rate recovery.

Implements:
1. Section 4.1: Aggregate observational equivalence under common learning rates.
2. Theorem 4.1: Uniform identification with known common rate (rank U == n vs rank [1^T; U] == n).
3. Theorem 4.2: Unknown-rate identified set P_b and known-total normalization.
4. Proposition 4.3: Four-tap aggregate recovery of (eta, Q, kappa).
5. Section 4.5: Heterogeneous modes Vandermonde moment separation.
"""
from typing import Dict, Any, Tuple, Optional, Union
import numpy as np


def verify_known_rate_identifiability(
    U: np.ndarray, known_Q: bool = False
) -> Dict[str, Any]:
    """Test uniform identifiability of feedback vector q from channel pulses U (Theorem 4.1).

    Parameters:
      U: (m, n) pulse experiment matrix.
      known_Q: whether total feedback mass Q = 1^T q > 0 is known.

    Returns:
      Dict with rank, required rank, and whether uniform point identification holds.
    """
    U = np.asarray(U, dtype=float)
    m, n = U.shape

    if not known_Q:
        r = int(np.linalg.matrix_rank(U))
        is_identifiable = (r == n)
        return {
            "rank": r,
            "required_rank": n,
            "num_probes": m,
            "known_Q": False,
            "is_uniformly_identifiable": is_identifiable,
        }
    else:
        augmented = np.vstack([np.ones((1, n)), U])
        r = int(np.linalg.matrix_rank(augmented))
        is_identifiable = (r == n)
        return {
            "rank": r,
            "required_rank": n,
            "num_probes": m,
            "known_Q": True,
            "is_uniformly_identifiable": is_identifiable,
            "min_probes_needed": n - 1,
        }


def recover_unknown_rate_and_q(
    U: np.ndarray,
    b: np.ndarray,
    known_Q: Optional[float] = None,
    eta_min: float = 0.001,
    eta_max: float = 1.0,
) -> Dict[str, Any]:
    """Analyze the identified set for unknown rate eta in [eta_min, eta_max] (Theorem 4.2).

    If U has full column rank and known_Q > 0:
      v = U^dagger * b
      eta = (1^T v) / Q
      q = (Q * v) / (1^T v)
    Without known_Q:
      Ray: q(s) = s * v for s in [1/eta_max, 1/eta_min].
    """
    U = np.asarray(U, dtype=float)
    b = np.asarray(b, dtype=float)
    m, n = U.shape
    r = int(np.linalg.matrix_rank(U))

    if r == n:
        # Full column rank: unique v = U^dagger * b
        v = np.linalg.pinv(U) @ b
        sum_v = float(np.sum(v))

        if known_Q is not None and known_Q > 0:
            if sum_v <= 0:
                return {
                    "status": "CONFLICT",
                    "reason": "1^T v <= 0 is incompatible with known Q > 0 and q >= 0.",
                }
            eta_est = sum_v / known_Q
            q_est = (known_Q * v) / sum_v

            is_valid_eta = (eta_min - 1e-9 <= eta_est <= eta_max + 1e-9)
            is_nonneg_q = np.all(q_est >= -1e-9)

            if is_valid_eta and is_nonneg_q:
                return {
                    "status": "POINT_IDENTIFIED",
                    "eta": float(eta_est),
                    "q": np.maximum(0.0, q_est).tolist(),
                    "Q": float(known_Q),
                    "rank": r,
                }
            else:
                return {
                    "status": "CONFLICT",
                    "eta_candidate": float(eta_est),
                    "q_candidate": q_est.tolist(),
                    "reason": "Recovered rate outside declared interval or negative weights.",
                }
        else:
            # Ray identification: q = s * v with s in [1/eta_max, 1/eta_min]
            s_min = 1.0 / eta_max
            s_max = 1.0 / eta_min
            q_lower_ray = s_min * v
            q_upper_ray = s_max * v
            return {
                "status": "RAY_IDENTIFIED",
                "v_base": v.tolist(),
                "s_interval": [float(s_min), float(s_max)],
                "q_at_eta_max": q_lower_ray.tolist(),
                "q_at_eta_min": q_upper_ray.tolist(),
                "rank": r,
            }
    else:
        # Rank-deficient U: nullspace ambiguity (Case 5)
        return {
            "status": "SUBSPACE_AMBIGUOUS",
            "rank": r,
            "num_agents": n,
            "nullity": n - r,
            "reason": "rank(U) < n generates multi-dimensional directional nullspace ambiguity.",
        }


def four_tap_aggregate_recovery(beta: np.ndarray) -> Dict[str, Any]:
    """Recover (a, eta, Q, kappa) from exact first four aggregate impulse responses (Proposition 4.3).

    beta = [beta_0, beta_1, beta_2, beta_3]
    h_j = beta_j / beta_0
    a = h_1
    k_0 = h_2 - a^2
    k_1 = h_3 - 2 * a * h_2 + a^3
    eta = 1 - k_1 / k_0
    Q = k_0 / eta
    kappa = beta_0
    """
    beta = np.asarray(beta, dtype=float)
    if len(beta) < 4:
        raise ValueError("Four-tap recovery requires at least 4 responses (beta_0, beta_1, beta_2, beta_3).")

    beta_0 = float(beta[0])
    if beta_0 <= 0:
        raise ValueError("beta_0 = kappa must be strictly positive.")

    h = beta[:4] / beta_0
    a = float(h[1])
    k_0 = float(h[2] - a ** 2)
    k_1 = float(h[3] - 2.0 * a * h[2] + a ** 3)

    if abs(k_0) < 1e-14:
        return {
            "status": "ZERO_FEEDBACK",
            "a": a,
            "Q": 0.0,
            "kappa": beta_0,
            "eta_identified": False,
        }

    eta = float(1.0 - k_1 / k_0)
    if eta <= 1e-12:
        return {
            "status": "ILL_CONDITIONED",
            "a": a,
            "k_0": k_0,
            "k_1": k_1,
            "eta_candidate": eta,
            "reason": "Recovered eta <= 0 violates positive learning assumption.",
        }

    Q = float(k_0 / eta)
    return {
        "status": "IDENTIFIED",
        "a": a,
        "eta": eta,
        "Q": Q,
        "S": a + Q,
        "kappa": beta_0,
        "k_0": k_0,
        "k_1": k_1,
    }


def heterogeneous_vandermonde_recovery(
    eta_vec: np.ndarray, k_vec: np.ndarray
) -> np.ndarray:
    """Recover feedback weights q across n heterogeneous modes with distinct rates eta_i (Section 4.5).

    k_j = sum_{i=1}^n q_i * eta_i * (1 - eta_i)^j
    System: V_eta * q = k, where (V_eta)_{j+1, i} = eta_i * (1 - eta_i)^j.
    """
    eta_vec = np.asarray(eta_vec, dtype=float)
    k_vec = np.asarray(k_vec, dtype=float)
    n = len(eta_vec)

    V = np.zeros((n, n), dtype=float)
    for j in range(n):
        for i in range(n):
            V[j, i] = eta_vec[i] * ((1.0 - eta_vec[i]) ** j)

    return np.linalg.solve(V, k_vec)
