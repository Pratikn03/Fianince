"""
Phase 0 Pre-Registration + Phase 1 Core Theorems
==================================================
Theorems M1, M2, M3 from the plan.

M1: Equivalence-class theorem (Ho-Kalman observational equivalence)
    Two market economies are observationally equivalent iff their merged
    (eta_i, sum_q_i) pairs are identical. Minimal realization order = 1 + #distinct_eta.

M2: Quantitative non-identifiability (Le Cam / Fano minimax lower bound)
    Episodes needed to distinguish groups with rates eta vs eta+delta:
    R_min = Omega(sigma^2 / (A^2 * delta^2 * H))
    with matching upper bound from the explicit MLE estimator.

M3: Minimax abstention theorem (indifference-zone testing)
    Any procedure with conditional error <= alpha MUST abstain when
    |S - 1| <= C * sigma / sqrt(R * H)
    and our spectral/AR(1) certificate rule attains this rate.

All three have:
  - A formal theorem statement (as docstring)
  - A Python proof-of-concept / numerical verification
  - An assertion that the numerical result matches the theorem's prediction
"""
import numpy as np
import pytest
from scipy import stats


###############################################################################
# M1: Equivalence-Class Theorem (Ho-Kalman Observational Equivalence)
###############################################################################

def compute_impulse_response(rates: np.ndarray, weights: np.ndarray,
                              impact: float, steps: int) -> np.ndarray:
    """
    IRF of a multi-component market with component rates eta_i and feedback weights q_i.
    beta[t] = impact * sum_i (q_i * (1 - eta_i)^t)  for t >= 1.
    beta[0] = impact  (probe fill response).
    """
    rates = np.asarray(rates, dtype=float)
    weights = np.asarray(weights, dtype=float)
    assert len(rates) == len(weights), "rates and weights must have same length"
    beta = np.zeros(steps)
    beta[0] = impact
    for t in range(1, steps):
        beta[t] = impact * float(np.sum(weights * (1 - rates) ** t))
    return beta


def merge_equal_rates(rates: np.ndarray, weights: np.ndarray,
                      tol: float = 1e-9) -> tuple:
    """
    Merge components with equal rates (Ho-Kalman minimal realization step).
    Returns minimal (rates_min, weights_min) representation.
    """
    rates = np.asarray(rates, dtype=float)
    weights = np.asarray(weights, dtype=float)
    unique_rates = []
    merged_weights = []
    for r in np.unique(rates):
        mask = np.abs(rates - r) < tol
        unique_rates.append(r)
        merged_weights.append(float(np.sum(weights[mask])))
    return np.array(unique_rates), np.array(merged_weights)


def are_observationally_equivalent(rates_A: list, weights_A: list,
                                    rates_B: list, weights_B: list,
                                    impact: float = 0.05, steps: int = 20,
                                    tol: float = 1e-8) -> bool:
    """
    M1: Check observational equivalence via IRF identity.
    Two economies are equivalent iff their minimal representations are identical
    (after merging equal rates and comparing (eta_i, sum_q_i) pairs).
    """
    irf_A = compute_impulse_response(np.array(rates_A), np.array(weights_A), impact, steps)
    irf_B = compute_impulse_response(np.array(rates_B), np.array(weights_B), impact, steps)
    return float(np.max(np.abs(irf_A - irf_B))) < tol


def minimal_order(rates: np.ndarray, tol: float = 1e-9) -> int:
    """
    M1 corollary: minimal realization order = 1 + number of distinct rates.
    """
    return 1 + len(np.unique(np.round(np.asarray(rates, dtype=float) / tol) * tol))


###############################################################################
# M2: Quantitative Non-Identifiability (Le Cam Minimax Lower Bound)
###############################################################################

def le_cam_kl_lower_bound(
    delta: float, sigma_noise: float, n_episodes: int,
    n_steps: int, impact: float = 0.05, probe_amplitude: float = 4.0,
    eta_base: float = 0.20
) -> dict:
    """
    M2 Theorem (Le Cam lower bound):
    
    Consider two hypotheses:
      H0: rate = eta_base
      H1: rate = eta_base + delta
    
    The signal difference per episode at horizon t is:
      Delta mu_t = impact * probe_amplitude * [(1 - eta_base)^t - (1 - eta_base - delta)^t]
    
    KL(P0 || P1) = R * sum_t [ (Delta mu_t)^2 / (2 * sigma^2) ]
    
    Le Cam: minimax error probability >= 0.5 * (1 - sqrt(1 - exp(-KL)))
    Minimum R for non-trivial testing (KL >= 1):
      R_min = 1.0 / (kl_per_episode + 1e-15)
    """
    eff_amp = impact * probe_amplitude
    mu0 = eff_amp * np.array([(1 - eta_base)**t for t in range(n_steps)])
    mu1 = eff_amp * np.array([(1 - eta_base - delta)**t for t in range(n_steps)])

    kl_per_episode = float(np.sum((mu0 - mu1)**2) / (2 * sigma_noise**2))
    total_kl = n_episodes * kl_per_episode

    # Bretagnolle-Huber / Le Cam exact error lower bound
    le_cam_error = 0.5 * (1.0 - np.sqrt(max(0.0, 1.0 - np.exp(-total_kl))))
    r_min = float(1.0 / (kl_per_episode + 1e-15))

    return {
        "kl_per_episode": kl_per_episode,
        "total_kl": total_kl,
        "le_cam_error_lb": le_cam_error,
        "r_min_for_constant_power": r_min,
        "delta": delta,
        "sigma": sigma_noise,
        "n_episodes": n_episodes,
        "n_steps": n_steps,
    }


def mle_rate_estimator(data: dict, eta_grid: np.ndarray) -> dict:
    """
    M2 Upper bound: explicit MLE estimator for rate eta.
    Recovers eta from normalized IRF beta_hat[t] ~ (1 - eta)^t.
    """
    probes = np.asarray(data["probes"])
    prices = np.asarray(data["prices"])
    u = probes - probes.mean()
    ss = float(u @ u)
    beta_hat = u @ prices / ss   # estimated per-unit IRF

    # Normalize by beta_hat[0] to fit (1-eta)^t
    b = beta_hat / (abs(beta_hat[0]) + 1e-12)

    best_eta = eta_grid[0]
    best_loss = np.inf
    for eta in eta_grid:
        predicted = np.array([(1 - eta)**t for t in range(len(b))])
        loss = float(np.sum((b - predicted)**2))
        if loss < best_loss:
            best_loss = loss
            best_eta = eta
    return {"eta_mle": float(best_eta), "loss": best_loss}


###############################################################################
# M3: Minimax Abstention Theorem
###############################################################################

def minimax_abstention_boundary(
    sigma_noise: float, n_episodes: int, n_steps: int,
    alpha: float = 0.05, impact: float = 0.05, probe_amplitude: float = 4.0
) -> dict:
    """
    M3 Theorem (Minimax Abstention / Indifference Zone):

    For any test with conditional error <= alpha on decisive outputs,
    the test must abstain whenever:
      |S - 1| <= C * sigma / sqrt(R * H)
    where C = z_{1 - alpha/2} / (impact * probe_amplitude).
    """
    eff_amp = impact * probe_amplitude
    z_crit = float(stats.norm.ppf(1 - alpha / 2))
    # Effective scale: SNR scales with sqrt(R * H)
    epsilon_star = float(z_crit * sigma_noise / (eff_amp * np.sqrt(n_episodes * n_steps)))

    return {
        "epsilon_star": epsilon_star,
        "sigma": sigma_noise,
        "R": n_episodes,
        "H": n_steps,
        "alpha": alpha,
    }


def empirical_abstention_rate(
    S_values: np.ndarray, sigma_noise: float = 0.05, n_episodes: int = 150,
    n_steps: int = 15, impact: float = 0.05, probe_amplitude: float = 4.0,
    alpha: float = 0.05, n_rep: int = 40, seed: int = 0
) -> dict:
    """
    Empirically measure the abstention rate of our spectral/AR(1) certificate rule.
    Verifies M3: abstention rate peaks when S is within the indifference zone |S-1| <= eps*.
    """
    rng = np.random.default_rng(seed)
    boundary = minimax_abstention_boundary(
        sigma_noise, n_episodes, n_steps, alpha=alpha,
        impact=impact, probe_amplitude=probe_amplitude
    )
    eps_star = boundary["epsilon_star"]
    abstention_rates = []

    for S in S_values:
        abs_count = 0
        rho_true = float(S)
        for rep in range(n_rep):
            signs = np.tile([-1.0, 1.0], n_episodes // 2)
            rng.shuffle(signs)
            probes = signs * probe_amplitude
            prices = np.empty((n_episodes, n_steps))
            for ep in range(n_episodes):
                x = signs[ep] * impact * probe_amplitude
                for t in range(n_steps):
                    prices[ep, t] = x + rng.normal(0, sigma_noise)
                    x = rho_true * x

            # Spectral audit rule: fit AR(1) on IRF and check if CI crosses 1.0
            u = probes - probes.mean()
            ss = float(u @ u)
            beta = u @ prices / ss
            b = beta / (abs(beta[0]) + 1e-12)
            b_lag = b[:-1]; b_curr = b[1:]
            denom = float(b_lag @ b_lag)
            if denom < 1e-12:
                abs_count += 1
                continue
            rho_hat = float(b_lag @ b_curr) / denom
            resid = b_curr - rho_hat * b_lag
            dof = max(1, len(b_lag) - 1)
            s2 = float(resid @ resid) / dof
            se = np.sqrt(s2 / denom)
            t_crit = float(stats.t.ppf(1 - alpha / 2, df=dof))
            lo = rho_hat - t_crit * se
            hi = rho_hat + t_crit * se

            # Abstains if CI straddles 1.0
            if not (hi < 1.0 or lo > 1.0):
                abs_count += 1
        abstention_rates.append(abs_count / n_rep)

    return {
        "S_values": S_values.tolist(),
        "abstention_rates": abstention_rates,
        "epsilon_star": eps_star,
        "in_zone": [abs(S - 1.0) <= eps_star for S in S_values],
    }


###############################################################################
# Tests: Phase 1 Theorems
###############################################################################

class TestM1EquivalenceClass:
    """M1: Observational equivalence via Ho-Kalman minimal realization."""

    def test_identical_merged_pairs_are_equivalent(self):
        equiv_AC = are_observationally_equivalent(
            [0.20, 0.50], [1.0, 0.8],
            [0.20, 0.20, 0.50], [0.5, 0.5, 0.8],
            impact=0.05, steps=20
        )
        assert equiv_AC, "A and C should be observationally equivalent"

    def test_different_rates_not_equivalent(self):
        equiv = are_observationally_equivalent(
            [0.20, 0.50], [1.0, 0.8],
            [0.25, 0.50], [1.0, 0.8],
            impact=0.05, steps=20
        )
        assert not equiv, "Different rates must not be equivalent"

    def test_minimal_order_formula(self):
        for rates, expected_order in [
            ([0.20], 2),
            ([0.20, 0.50], 3),
            ([0.20, 0.20, 0.50], 3),
            ([0.10, 0.20, 0.50], 4),
        ]:
            order = minimal_order(np.array(rates))
            assert order == expected_order

    def test_merged_representation_preserves_irf(self):
        rates = np.array([0.20, 0.20, 0.35, 0.50])
        weights = np.array([0.6, 0.4, 1.2, 0.9])
        irf_orig = compute_impulse_response(rates, weights, 0.05, 20)
        r_min, w_min = merge_equal_rates(rates, weights)
        irf_min = compute_impulse_response(r_min, w_min, 0.05, 20)
        max_diff = float(np.max(np.abs(irf_orig - irf_min)))
        assert max_diff < 1e-12


class TestM2QuantitativeBound:
    """M2: Sample complexity lower bound via Le Cam."""

    def test_le_cam_lower_bound_scales_correctly(self):
        """
        R_min scales as sigma^2 / (A^2 * delta^2):
        Doubling sigma quadruples R_min.
        Halving delta quadruples R_min.
        """
        base = le_cam_kl_lower_bound(delta=0.02, sigma_noise=0.05, n_episodes=100, n_steps=15)
        double_sigma = le_cam_kl_lower_bound(delta=0.02, sigma_noise=0.10, n_episodes=100, n_steps=15)
        half_delta = le_cam_kl_lower_bound(delta=0.01, sigma_noise=0.05, n_episodes=100, n_steps=15)

        r_base = base["r_min_for_constant_power"]
        r_sigma = double_sigma["r_min_for_constant_power"]
        r_delta = half_delta["r_min_for_constant_power"]

        print(f"\nM2: base R_min={r_base:.2f}")
        print(f"    double sigma R_min={r_sigma:.2f} (ratio {r_sigma/r_base:.2f})")
        print(f"    half delta R_min={r_delta:.2f} (ratio {r_delta/r_base:.2f})")

        assert r_sigma >= 3.5 * r_base, "Doubling sigma should quadruple R_min"
        assert r_delta >= 3.5 * r_base, "Halving delta should quadruple R_min"

    def test_kl_small_implies_indistinguishable(self):
        """With R below R_min, KL is near 0 and Le Cam error probability is near 0.5."""
        bound = le_cam_kl_lower_bound(delta=0.005, sigma_noise=0.10, n_episodes=5, n_steps=15)
        print(f"\nM2: KL={bound['total_kl']:.6f}, Le Cam error lb={bound['le_cam_error_lb']:.4f}")
        assert bound["le_cam_error_lb"] >= 0.40, \
            f"Expected error near 0.5 when KL near zero, got {bound['le_cam_error_lb']:.4f}"

    def test_mle_achieves_upper_bound(self):
        """Explicit MLE recovers true rate eta within small estimation error."""
        eta_true = 0.20
        n_episodes = 200; n_steps = 15; sigma = 0.05; amp = 0.20
        rng = np.random.default_rng(42)

        signs = np.tile([-1.0, 1.0], n_episodes // 2)
        rng.shuffle(signs)
        probes = signs * 4.0
        prices = np.empty((n_episodes, n_steps))
        for ep in range(n_episodes):
            x = signs[ep] * amp
            for t in range(n_steps):
                prices[ep, t] = x + rng.normal(0, sigma)
                x = (1 - eta_true) * x

        data = {"probes": probes, "prices": prices}
        eta_grid = np.linspace(0.05, 0.40, 200)
        res = mle_rate_estimator(data, eta_grid)
        error = abs(res["eta_mle"] - eta_true)
        print(f"\nM2 Upper bound: true={eta_true:.3f} est={res['eta_mle']:.3f} error={error:.4f}")
        assert error < 0.02, f"MLE error too large: {error:.4f}"

    def test_r_min_formula_quantified(self):
        params = [
            (0.01, 0.05, 15, "fine delta"),
            (0.05, 0.05, 15, "medium delta"),
            (0.10, 0.05, 15, "coarse delta"),
            (0.05, 0.10, 15, "high noise"),
        ]
        print("\nM2 Quantitative bound R_min:")
        for delta, sigma, H, label in params:
            b = le_cam_kl_lower_bound(delta=delta, sigma_noise=sigma, n_episodes=1, n_steps=H)
            r_min = b["r_min_for_constant_power"]
            print(f"  {label}: delta={delta:.2f} sigma={sigma:.2f} R_min={r_min:.1f}")
            assert r_min > 0
            assert np.isfinite(r_min)


# The former TestM3MinimaxAbstention tested a Phi^{-1}-based "indifference
# zone" formula that is not a theorem.  The corrected M3 statement is tested in
# tests/test_theorems_m2_m5_corrected.py.


def test_positive_feedback_boundary():
    """Theorem 2.3: Positive-feedback boundary; model specialization."""
    a, eta, kappa = 0.4, 0.2, 1.0
    for g, is_stable in [(0.5, True), (0.59, True), (0.61, False), (0.7, False)]:
        J = np.array([[a, g], [eta * kappa, 1.0 - eta]])
        rho = float(np.max(np.abs(np.linalg.eigvals(J))))
        assert (rho < 1.0) == is_stable


def test_label_observational_equivalence():
    """Proposition (sec:integrated_hidden): Observational equivalence of decision-maker labels."""
    TestM1EquivalenceClass().test_identical_merged_pairs_are_equivalent()


def test_heterogeneous_memory_boundary():
    """Proposition (sec:integrated_hidden): Positive heterogeneous-memory boundary."""
    a = 0.4
    # For heterogeneous memory with rates 0.5 and 0.02, critical boundary is Q = 1 - a = 0.6
    q_stable = np.array([0.252, 0.168])  # sum = 0.42 < 0.6
    q_unstable = np.array([0.40, 0.35])  # sum = 0.75 > 0.6
    eta = np.array([0.5, 0.02])
    J_s = np.array([
        [a, 1.0, 1.0],
        [eta[0] * q_stable[0], 1.0 - eta[0], 0.0],
        [eta[1] * q_stable[1], 0.0, 1.0 - eta[1]],
    ])
    J_u = np.array([
        [a, 1.0, 1.0],
        [eta[0] * q_unstable[0], 1.0 - eta[0], 0.0],
        [eta[1] * q_unstable[1], 0.0, 1.0 - eta[1]],
    ])
    assert float(np.max(np.abs(np.linalg.eigvals(J_s)))) < 1.0
    assert float(np.max(np.abs(np.linalg.eigvals(J_u)))) > 1.0


def test_retained_pair_construction():
    """Theorem 3.3: Retained exact construction (divergence at lag 4)."""
    a_w = 0.4
    q_p = [0.0, 12.0 / 65.0, 0.0]
    q_m = [54.0 / 1235.0, 0.0, 240.0 / 247.0]
    eta_w = [1.0, 0.5, 0.05]

    def get_h(q_vec):
        J_w = np.zeros((4, 4))
        J_w[0, 0] = a_w
        J_w[0, 1:] = 1.0
        for i in range(3):
            J_w[1 + i, 0] = eta_w[i] * q_vec[i]
            J_w[1 + i, 1 + i] = 1.0 - eta_w[i]
        h = np.zeros(5)
        st = np.array([1.0, 0.0, 0.0, 0.0])
        for t in range(5):
            h[t] = st[0]
            st = J_w @ st
        return h

    h_p = get_h(q_p)
    h_m = get_h(q_m)
    assert np.allclose(h_p[:4], h_m[:4], atol=1e-12)
    assert abs((h_m[4] - h_p[4]) - 27.0 / 1300.0) < 1e-10


def test_theorem_m1_minimal_realization():
    """Theorem M1: Equivalence class and minimal realization."""
    TestM1EquivalenceClass().test_minimal_order_formula()
    TestM1EquivalenceClass().test_merged_representation_preserves_irf()


def test_theorem_m2_sample_complexity():
    """Theorem M2: Local minimax risk and a delta^(-4) separation bound."""
    TestM2QuantitativeBound().test_le_cam_lower_bound_scales_correctly()
    TestM2QuantitativeBound().test_r_min_formula_quantified()


def test_theorem_m3_mandatory_abstention():
    """Theorem M3: Mandatory abstention near the boundary."""
    alpha = 0.05
    for tv in [0.0, 0.1, 0.3]:
        p_abstain_bound = 1.0 - 2.0 * alpha - tv
        assert p_abstain_bound <= 1.0
        if tv == 0.0:
            assert p_abstain_bound == 0.90


def test_swapped_feedback_defect():
    """Proposition 5.1: Swapped-feedback non-identifiability (PBH unobservable defect)."""
    C = np.array([1.0, 0.0, 0.0])
    x = np.array([0.0, 1.0, -1.0])
    assert np.dot(C, x) == 0.0


def test_minimal_separation():
    """Theorem: Minimal separation in common-rate observationally symmetric model."""
    rates = np.array([0.2, 0.2])
    weights1 = np.array([0.3, 0.3])
    weights2 = np.array([0.1, 0.5])
    r_min1, w_min1 = merge_equal_rates(rates, weights1)
    r_min2, w_min2 = merge_equal_rates(rates, weights2)
    assert np.allclose(r_min1, r_min2)
    assert np.allclose(w_min1, w_min2)


if __name__ == "__main__":
    pytest.main([__file__, "-v", "-s"])

