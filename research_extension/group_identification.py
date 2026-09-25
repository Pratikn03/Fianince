"""Phase 2: Group Identification Theory, Impossibility, and Separation Theorems.

Addresses Reviewer Gap A & Gap B:
1. Proposition G.1 (Swapped-Feedback Non-Identifiability):
   Shows that two economies with swapped agent feedback weights (0.3, 0.1) vs (0.1, 0.3)
   yield identical aggregate price impulse responses at every horizon h >= 0,
   yet have opposite policy suppression consequences Delta_G1 = 0.3 vs 0.1.

2. Theorem G.2 (Minimal Separation Theorem):
   Establishes that group-level parameters (q_1, ..., q_n) are identifiable
   if and only if group-specific excitation (independent channel probes) or
   order-level provenance is available.

3. Definition G.3 (Group Suppression Effect Delta_G):
   Formal counterfactual operator removing group G's feedback elasticity.
"""

import numpy as np


class SwappedFeedbackEconomy:
    """Two-agent adaptive market model with state:
    x_{t+1} = a * x_t + sum_{i=1}^n y_{i,t} + kappa * u_t
    y_{i,t+1} = (1 - eta) * y_{i,t} + eta * q_i * x_t
    """

    def __init__(self, a=0.4, eta=0.05, q=(0.3, 0.1), kappa=0.02):
        self.a = float(a)
        self.eta = float(eta)
        self.q = np.asarray(q, dtype=float)
        self.kappa = float(kappa)
        self.n = len(self.q)
        self.Q = float(np.sum(self.q))
        self.S = self.a + self.Q

    def transition_matrix(self, suppressed_indices=None):
        """Construct (1+n, 1+n) state transition matrix.
        If suppressed_indices is provided, set those q_i to 0.
        """
        dim = 1 + self.n
        J = np.zeros((dim, dim), dtype=float)
        J[0, 0] = self.a
        J[0, 1:] = 1.0

        q_eff = self.q.copy()
        if suppressed_indices is not None:
            for idx in suppressed_indices:
                q_eff[idx] = 0.0

        for i in range(self.n):
            J[1 + i, 0] = self.eta * q_eff[i]
            J[1 + i, 1 + i] = 1.0 - self.eta
        return J

    def aggregate_price_impulse_response(self, H=50):
        """Calculate price response beta_j = kappa * e_1^T J^j e_1 for j = 0, ..., H."""
        J = self.transition_matrix()
        dim = 1 + self.n
        e1 = np.zeros(dim)
        e1[0] = 1.0

        resp = np.zeros(H + 1)
        state = e1.copy()
        for j in range(H + 1):
            resp[j] = self.kappa * state[0]
            state = J @ state
        return resp

    def group_suppression_effect(self, group_indices):
        """Compute Delta_G = S(full) - S(G suppressed)."""
        removed_q = sum(self.q[i] for i in group_indices)
        return float(removed_q)

    def group_specific_impulse_response(self, group_index, H=50):
        """Impulse response to a targeted probe on agent group_index's information input.
        Perturbing agent i's input channel by delta = 1 at t=0 induces:
        Delta y_{i, 1} = eta * q_i * delta.
        Subsequent price displacement is Delta x_2 = Delta y_{i, 1} = eta * q_i.
        """
        dim = 1 + self.n
        J = self.transition_matrix()
        # Input excites group_index's memory scaled by its feedback sensitivity q_i:
        b_target = np.zeros(dim)
        b_target[1 + group_index] = self.eta * self.q[group_index]

        resp = np.zeros(H + 1)
        state = b_target.copy()
        for j in range(H + 1):
            resp[j] = self.kappa * state[0]
            state = J @ state
        return resp


def verify_swapped_feedback_proposition(H=50):
    """Verify Proposition G.1:
    E_A: q = (0.3, 0.1)
    E_B: q = (0.1, 0.3)
    Both have identical aggregate price responses, but Delta_G1 differs.
    """
    ea = SwappedFeedbackEconomy(a=0.4, eta=0.05, q=(0.3, 0.1), kappa=0.02)
    eb = SwappedFeedbackEconomy(a=0.4, eta=0.05, q=(0.1, 0.3), kappa=0.02)

    resp_a = ea.aggregate_price_impulse_response(H=H)
    resp_b = eb.aggregate_price_impulse_response(H=H)

    max_resp_diff = np.max(np.abs(resp_a - resp_b))

    delta_g1_a = ea.group_suppression_effect([0])  # Agent 1 in Economy A: 0.3
    delta_g1_b = eb.group_suppression_effect([0])  # Agent 1 in Economy B: 0.1

    return {
        "proposition": "Proposition G.1 (Swapped-Feedback Non-Identifiability)",
        "H": H,
        "max_aggregate_price_response_diff": float(max_resp_diff),
        "is_observationally_identical": bool(max_resp_diff < 1e-14),
        "economy_A_q": list(ea.q),
        "economy_B_q": list(eb.q),
        "total_Q_A": ea.Q,
        "total_Q_B": eb.Q,
        "delta_G1_economy_A": delta_g1_a,
        "delta_G1_economy_B": delta_g1_b,
        "suppression_effect_difference": float(abs(delta_g1_a - delta_g1_b)),
    }


def verify_separation_theorem(H=50):
    """Verify Theorem G.2 (Separation via Targeted Probing):
    When probes are group-specific, the responses diverge, breaking the equivalence.
    """
    ea = SwappedFeedbackEconomy(a=0.4, eta=0.05, q=(0.3, 0.1), kappa=0.02)
    eb = SwappedFeedbackEconomy(a=0.4, eta=0.05, q=(0.1, 0.3), kappa=0.02)

    # Probe channel 0 (Agent 1)
    resp_target_a = ea.group_specific_impulse_response(group_index=0, H=H)
    resp_target_b = eb.group_specific_impulse_response(group_index=0, H=H)

    max_target_diff = np.max(np.abs(resp_target_a - resp_target_b))

    return {
        "theorem": "Theorem G.2 (Minimal Separation via Targeted Probing)",
        "H": H,
        "max_targeted_response_diff": float(max_target_diff),
        "is_separated": bool(max_target_diff > 1e-4),
        "target_response_peak_A": float(np.max(resp_target_a)),
        "target_response_peak_B": float(np.max(resp_target_b)),
    }


def verify_pbh_unobservability():
    """Verify the Popov-Belevitch-Hautus (PBH) Observability condition:
    The mode lambda = 1 - eta has rank drop in [lambda * I - J; C].
    The unobservable subspace has dimension n - 1 and consists of all v = [0, w] with sum(w) = 0.
    """
    ea = SwappedFeedbackEconomy(a=0.4, eta=0.05, q=(0.3, 0.1), kappa=0.02)
    J = ea.transition_matrix()
    dim = 1 + ea.n
    C = np.zeros((1, dim))
    C[0, 0] = 1.0

    lam = 1.0 - ea.eta
    pbh_matrix = np.vstack([lam * np.eye(dim) - J, C])
    rank_pbh = np.linalg.matrix_rank(pbh_matrix)

    # Test eigenvector condition for v = [0, 1, -1]^T
    v = np.zeros(dim)
    v[1] = 1.0
    v[2] = -1.0

    jv = J @ v
    lam_v = lam * v
    eigen_error = float(np.max(np.abs(jv - lam_v)))
    output_error = float(np.abs(C @ v).item())

    return {
        "lambda": lam,
        "full_dimension": dim,
        "pbh_matrix_shape": list(pbh_matrix.shape),
        "pbh_rank": int(rank_pbh),
        "rank_deficient": bool(rank_pbh < dim),
        "rank_drop": int(dim - rank_pbh),
        "eigenvector_residual": eigen_error,
        "output_residual": output_error,
        "is_unobservable_mode": bool(eigen_error < 1e-15 and output_error < 1e-15 and rank_pbh < dim),
    }


if __name__ == "__main__":
    p_res = verify_swapped_feedback_proposition()
    print("--- PROPOSITION G.1 VERIFICATION ---")
    for k, v in p_res.items():
        print(f"  {k}: {v}")

    t_res = verify_separation_theorem()
    print("\n--- THEOREM G.2 VERIFICATION ---")
    for k, v in t_res.items():
        print(f"  {k}: {v}")

    pbh_res = verify_pbh_unobservability()
    print("\n--- PBH OBSERVABILITY VERIFICATION ---")
    for k, v in pbh_res.items():
        print(f"  {k}: {v}")
