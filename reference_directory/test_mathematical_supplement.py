"""21 Unit tests for Machine Markets mathematical supplement.

Discovered via:
  python -m unittest discover -v
"""
import unittest
from fractions import Fraction
import numpy as np
from scipy import stats, linalg

try:
    from reference_directory.continuous import (
        build_continuous_matrix,
        is_metzler,
        is_hurwitz,
        spectral_radius,
        spectral_abscissa,
        hurwitz_threshold_spectral_radius,
        common_rate_spectral_abscissa_formula,
        forward_euler_parameters,
        forward_euler_matrix,
        max_admissible_euler_step,
        exact_sampled_matrix,
        euler_error_theoretical_bound,
        continuous_tail_bound,
    )
    from reference_directory.group import (
        verify_known_rate_identifiability,
        recover_unknown_rate_and_q,
        four_tap_aggregate_recovery,
        heterogeneous_vandermonde_recovery,
    )
    from reference_directory.ellipsoid import (
        hotelling_f_critical_value,
        estimate_ols_response_and_covariance,
        is_in_ellipsoid,
        linear_contrast_support,
        get_four_coefficient_witness,
    )
    from reference_directory.conic import (
        compute_coordinate_bounds_from_ellipsoid,
        compute_data_derived_mass_cap,
        compute_rate_bin_envelopes,
        mccormick_envelopes,
        verify_conic_lift_containment,
        residual_corrected_dual_lower_bound,
    )
    from reference_directory.decisions import (
        classify_interval,
        compute_two_world_abstention_bound,
        simulate_solvency_shock,
    )
except ImportError:
    from continuous import (
        build_continuous_matrix,
        is_metzler,
        is_hurwitz,
        spectral_radius,
        spectral_abscissa,
        hurwitz_threshold_spectral_radius,
        common_rate_spectral_abscissa_formula,
        forward_euler_parameters,
        forward_euler_matrix,
        max_admissible_euler_step,
        exact_sampled_matrix,
        euler_error_theoretical_bound,
        continuous_tail_bound,
    )
    from group import (
        verify_known_rate_identifiability,
        recover_unknown_rate_and_q,
        four_tap_aggregate_recovery,
        heterogeneous_vandermonde_recovery,
    )
    from ellipsoid import (
        hotelling_f_critical_value,
        estimate_ols_response_and_covariance,
        is_in_ellipsoid,
        linear_contrast_support,
        get_four_coefficient_witness,
    )
    from conic import (
        compute_coordinate_bounds_from_ellipsoid,
        compute_data_derived_mass_cap,
        compute_rate_bin_envelopes,
        mccormick_envelopes,
        verify_conic_lift_containment,
        residual_corrected_dual_lower_bound,
    )
    from decisions import (
        classify_interval,
        compute_two_world_abstention_bound,
        simulate_solvency_shock,
    )


class TestMathematicalSupplement(unittest.TestCase):
    """21 Unit tests verifying all formal propositions and theorems in the supplement."""

    def test_01_metzler_hurwitz_equivalence(self):
        """Lemma 3.1: A Metzler matrix is Hurwitz <=> exists v > 0 such that A v < 0."""
        # Stable Metzler matrix
        A_stable = np.array([[-2.0, 1.0], [0.5, -3.0]])
        self.assertTrue(is_metzler(A_stable))
        self.assertTrue(is_hurwitz(A_stable))
        v_cand = np.array([1.0, 0.5])
        self.assertTrue(np.all(A_stable @ v_cand < 0))

        # Unstable Metzler matrix
        A_unstable = np.array([[-1.0, 2.0], [2.0, -1.0]])
        self.assertTrue(is_metzler(A_unstable))
        self.assertFalse(is_hurwitz(A_unstable))

    def test_02_continuous_time_boundary_heterogeneous(self):
        """Theorem 3.3: A_c is Hurwitz <=> rho(Gamma^{-1} * g * B * C) < 1 under heterogeneous rates."""
        Gamma = np.diag([1.5, 2.0])
        E = np.diag([0.5, 0.1, 0.05])
        B = np.array([[1.0, 0.5, 0.2], [0.3, 1.0, 0.8]])
        C = np.array([[0.6, 0.4], [0.2, 0.5], [0.1, 0.3]])

        # Test subcritical g
        g_sub = 0.5
        A_sub = build_continuous_matrix(Gamma, B, C, E, g_sub)
        rho_sub = hurwitz_threshold_spectral_radius(Gamma, B, C, g_sub)
        self.assertLess(rho_sub, 1.0)
        self.assertTrue(is_hurwitz(A_sub))

        # Test supercritical g
        g_super = 2.5
        A_super = build_continuous_matrix(Gamma, B, C, E, g_super)
        rho_super = hurwitz_threshold_spectral_radius(Gamma, B, C, g_super)
        self.assertGreater(rho_super, 1.0)
        self.assertFalse(is_hurwitz(A_super))

    def test_03_continuous_time_boundary_scalar(self):
        """Theorem 3.3: Scalar case g * rho(BC) < gamma <=> A_c is Hurwitz."""
        gamma = 2.0
        Gamma = np.diag([gamma, gamma])
        E = np.diag([0.4, 0.8])
        B = np.array([[1.0, 0.5], [0.2, 1.0]])
        C = np.array([[0.5, 0.3], [0.4, 0.6]])
        nu = spectral_radius(B @ C)

        g_stable = 0.8 * (gamma / nu)
        A_stable = build_continuous_matrix(Gamma, B, C, E, g_stable)
        self.assertTrue(is_hurwitz(A_stable))

        g_unstable = 1.2 * (gamma / nu)
        A_unstable = build_continuous_matrix(Gamma, B, C, E, g_unstable)
        self.assertFalse(is_hurwitz(A_unstable))

    def test_04_spectral_abscissa_formula(self):
        """Proposition 3.5: Closed formula for spectral abscissa sa(A_c) in common-rate setting."""
        gamma = 1.2
        lambda_rate = 0.4
        Gamma = np.diag([gamma, gamma])
        E = np.diag([lambda_rate, lambda_rate])
        B = np.array([[1.2, 0.3], [0.4, 0.8]])
        C = np.array([[0.5, 0.2], [0.1, 0.9]])
        nu = spectral_radius(B @ C)
        g = 0.9

        A_c = build_continuous_matrix(Gamma, B, C, E, g)
        numerical_sa = spectral_abscissa(A_c)
        formula_sa = common_rate_spectral_abscissa_formula(gamma, lambda_rate, nu, g)

        self.assertAlmostEqual(numerical_sa, formula_sa, places=9)

    def test_05_euler_schur_equivalence(self):
        """Theorem 3.6: Forward Euler matrix P_h >= 0 is Schur <=> A_c is Hurwitz for h <= h_max."""
        Gamma = np.array([2.0, 1.5])
        E = np.array([0.5, 0.2])
        B = np.array([[0.5, 0.2], [0.3, 0.4]])
        C = np.array([[0.4, 0.1], [0.2, 0.5]])
        g = 1.0

        A_c = build_continuous_matrix(Gamma, B, C, E, g)
        h_max = max_admissible_euler_step(Gamma, E)
        self.assertAlmostEqual(h_max, 0.5)

        h = 0.25  # h < h_max
        P_h = forward_euler_matrix(A_c, h)
        self.assertTrue(np.all(P_h >= 0.0))

        is_schur = (spectral_radius(P_h) < 1.0)
        self.assertEqual(is_schur, is_hurwitz(A_c))

    def test_06_euler_error_bound(self):
        """Theorem 3.6: Discretization error bound ||(I + h A_c)^k - e^{kh A_c}|| <= 0.5 * T * h * ||A_c||^2 * e^{T ||A_c||}."""
        Gamma = np.array([1.0])
        E = np.array([0.5])
        B = np.array([[0.3]])
        C = np.array([[0.4]])
        g = 0.8
        A_c = build_continuous_matrix(Gamma, B, C, E, g)

        T = 1.0
        h = 0.01
        k = int(T / h)

        P_k = np.linalg.matrix_power(forward_euler_matrix(A_c, h), k)
        exact_exp = exact_sampled_matrix(A_c, T)
        actual_error = float(np.linalg.norm(P_k - exact_exp, ord=2))
        theoretical_bound = euler_error_theoretical_bound(A_c, h, T, ord=2)

        self.assertLessEqual(actual_error, theoretical_bound)

    def test_07_exact_sampling_vs_forward_euler(self):
        """Remark 3.7: Exact sampling e^{h A_c} preserves stability for all h > 0, while forward Euler can diverge."""
        # A_c = -I, h = 3
        A_c = -np.eye(2)
        h = 3.0

        # Exact sampling is Schur
        exact_trans = exact_sampled_matrix(A_c, h)
        self.assertLess(spectral_radius(exact_trans), 1.0)

        # Forward Euler P_h = I - 3I = -2I has rho = 2.0 (unstable!)
        P_euler = forward_euler_matrix(A_c, h)
        self.assertEqual(spectral_radius(P_euler), 2.0)
        self.assertGreater(spectral_radius(P_euler), 1.0)

    def test_08_continuous_hidden_memory_tail(self):
        """Section 3.5: Continuous hidden-memory tail int_T^infty K(t) dt <= Q_max * e^{-lambda_0 * T}."""
        Q_max = 1.0
        lambda_0 = 0.05
        T = 20.0

        tail_bound = continuous_tail_bound(Q_max, lambda_0, T)
        expected = np.exp(-0.05 * 20.0)  # e^{-1} approx 0.367879
        self.assertAlmostEqual(tail_bound, expected, places=7)

    def test_09_known_rate_rank_conditions(self):
        """Theorem 4.1: Known rate rank conditions (rank U == n vs rank [1^T; U] == n)."""
        n = 3
        # Rank-deficient U with 2 probes
        U_2 = np.array([[1.0, 0.0, 0.0], [0.0, 1.0, 0.0]])
        res_no_Q = verify_known_rate_identifiability(U_2, known_Q=False)
        self.assertFalse(res_no_Q["is_uniformly_identifiable"])

        # With known Q, 2 probes suffice because rank([1^T; U]) == 3
        res_with_Q = verify_known_rate_identifiability(U_2, known_Q=True)
        self.assertTrue(res_with_Q["is_uniformly_identifiable"])

    def test_10_unknown_rate_exact_recovery_with_total(self):
        """Theorem 4.2: Exact recovery of eta and q when Q > 0 is known."""
        U = np.eye(2)
        b = np.array([0.06, 0.02])
        Q = 0.4

        rec = recover_unknown_rate_and_q(U, b, known_Q=Q, eta_min=0.01, eta_max=1.0)
        self.assertEqual(rec["status"], "POINT_IDENTIFIED")
        self.assertAlmostEqual(rec["eta"], 0.2, places=6)
        self.assertAlmostEqual(rec["q"][0], 0.3, places=6)
        self.assertAlmostEqual(rec["q"][1], 0.1, places=6)

    def test_11_unknown_rate_ray_identification(self):
        """Theorem 4.2: Without Q, unknown rate admits only ray identification."""
        U = np.eye(2)
        b = np.array([0.06, 0.02])
        rec = recover_unknown_rate_and_q(U, b, known_Q=None, eta_min=0.2, eta_max=0.4)
        self.assertEqual(rec["status"], "RAY_IDENTIFIED")
        self.assertAlmostEqual(rec["q_at_eta_min"][0], 0.3, places=6)  # at eta = 0.2 => s = 5 => 0.3
        self.assertAlmostEqual(rec["q_at_eta_max"][0], 0.15, places=6) # at eta = 0.4 => s = 2.5 => 0.15

    def test_12_four_tap_aggregate_recovery(self):
        """Proposition 4.3: Four-tap aggregate recovery of (a, eta, Q, kappa)."""
        a_true = 0.4
        eta_true = 0.2
        Q_true = 0.35
        kappa_true = 0.02

        # Simulate exact first four lags
        h0 = 1.0
        h1 = a_true
        k0 = eta_true * Q_true
        k1 = (1.0 - eta_true) * k0
        h2 = a_true * h1 + k0 * h0
        h3 = a_true * h2 + k0 * h1 + k1 * h0
        beta = kappa_true * np.array([h0, h1, h2, h3])

        rec = four_tap_aggregate_recovery(beta)
        self.assertEqual(rec["status"], "IDENTIFIED")
        self.assertAlmostEqual(rec["a"], a_true, places=9)
        self.assertAlmostEqual(rec["eta"], eta_true, places=9)
        self.assertAlmostEqual(rec["Q"], Q_true, places=9)
        self.assertAlmostEqual(rec["kappa"], kappa_true, places=9)

    def test_13_heterogeneous_modes_vandermonde(self):
        """Section 4.5: Exact recovery of heterogeneous cohort weights via Vandermonde inversion."""
        eta_vec = np.array([0.8, 0.2, 0.05])
        q_true = np.array([0.25, 0.15, 0.10])

        k_vec = np.zeros(3)
        for j in range(3):
            k_vec[j] = np.sum(q_true * eta_vec * ((1.0 - eta_vec) ** j))

        q_recovered = heterogeneous_vandermonde_recovery(eta_vec, k_vec)
        np.testing.assert_allclose(q_recovered, q_true, atol=1e-10)

    def test_14_hotelling_f_radius_exact_calculation(self):
        """Theorem 5.1: Exact Hotelling squared radius k_alpha^2 = 12.12340136 for R=32, p=4."""
        R = 32
        p = 4
        k_alpha_sq, f_crit, df1, df2 = hotelling_f_critical_value(p, R, alpha=0.05)

        self.assertEqual(df1, 4)
        self.assertEqual(df2, 27)
        self.assertAlmostEqual(k_alpha_sq, 12.12340136, places=7)

    def test_15_linear_contrast_support(self):
        """Proposition 5.2: Linear contrast support over response ellipsoid."""
        beta_hat = np.array([0.5, 0.2, 0.1, 0.05])
        V = 0.01 * np.eye(4)
        k_alpha = 3.0
        c = np.array([1.0, 1.0, 0.0, 0.0])

        min_val, max_val, half_w = linear_contrast_support(c, beta_hat, V, k_alpha)
        expected_center = 0.7
        expected_hw = k_alpha * np.sqrt(0.01 + 0.01)  # 3.0 * sqrt(0.02) approx 0.424264
        self.assertAlmostEqual(min_val, expected_center - expected_hw, places=6)
        self.assertAlmostEqual(max_val, expected_center + expected_hw, places=6)

    def test_16_rational_four_coefficient_witness(self):
        """Proposition 5.3: Rational witness proving no fixed linear contrast gives S."""
        witness = get_four_coefficient_witness()
        self.assertTrue(witness["h_sequences_identical"])
        self.assertEqual(witness["h_seq0"], witness["expected_h"])
        self.assertTrue(witness["is_S0_stable"])
        self.assertFalse(witness["is_S1_stable"])
        self.assertEqual(witness["S0"], "38/65")
        self.assertEqual(witness["S1"], "92/65")

    def test_17_data_derived_mass_cap(self):
        """Lemma 7.1: Data-derived finite mass cap M = U_2 / (eta_min * L_0)."""
        U_2 = 0.08
        L_0 = 0.02
        eta_min = 0.05
        M = compute_data_derived_mass_cap(U_2, L_0, eta_min)
        expected_M = 0.08 / (0.05 * 0.02)  # 80.0
        self.assertAlmostEqual(M, expected_M, places=6)

    def test_18_continuous_rate_bin_envelopes(self):
        """Section 7.2: Continuous rate-bin envelopes cover off-grid rates."""
        bin_edges = [(0.02, 0.1), (0.1, 0.5), (0.5, 1.0)]
        for j in range(4):
            ell, u = compute_rate_bin_envelopes(j, bin_edges)
            # Sample dense points inside bins to verify envelope validity
            for idx, (left, right) in enumerate(bin_edges):
                dense_eta = np.linspace(left, right, 50)
                vals = [e * ((1.0 - e) ** j) for e in dense_eta]
                self.assertLessEqual(ell[idx], min(vals) + 1e-12)
                self.assertGreaterEqual(u[idx], max(vals) - 1e-12)

    def test_19_mccormick_bilinear_lifting(self):
        """Section 7.3: McCormick bilinear product lifting validity."""
        A = 1.0
        L = 0.2
        U = 0.8
        # Test multiple points in the domain
        for x in [0.0, 0.3, 0.7, 1.0]:
            for y in [0.2, 0.4, 0.6, 0.8]:
                res = mccormick_envelopes(x, y, A, L, U)
                self.assertTrue(res["is_valid"])

    def test_20_residual_corrected_dual_lower_bound(self):
        """Proposition 9.1: Residual-corrected conic dual lower bound."""
        # Simple LP: min c^T x s.t. x1 + x2 = 1, x in [0, 2]^2
        c = np.array([2.0, 3.0])
        A = np.array([[1.0, 1.0]])
        b = np.array([1.0])
        G = np.zeros((1, 2))
        h = np.array([0.0])
        ell = np.array([0.0, 0.0])
        u = np.array([2.0, 2.0])

        # Dual variable y = [-2.0]
        y = np.array([-2.0])
        z = np.array([0.0])

        lb = residual_corrected_dual_lower_bound(c, A, b, G, h, ell, u, y, z)
        # Optimal primal value is 2.0 (at x = [1, 0])
        self.assertLessEqual(lb, 2.0 + 1e-12)

    def test_21_two_world_abstention_and_solvency_shock(self):
        """Theorem 10.2 (14.88% abstention bound) and Proposition 11.1 (solvency shock independence)."""
        # Theorem 10.2: d at eta=10^-5 gives p* = 0.47562460, e=0.05 => bound = 14.88%
        bound = compute_two_world_abstention_bound(e=0.05, p_star=0.47562460)
        self.assertAlmostEqual(bound, 0.14875080, places=7)

        # Proposition 11.1: Solvency simulation with stable r = 0.4, pi = 0.15
        sim = simulate_solvency_shock(r=0.4, E_0=100.0, I=10.0, P_0=50.0, pi=0.15, num_paths=10000, seed=42)
        self.assertTrue(sim["is_signal_stable"])
        self.assertAlmostEqual(sim["observed_insolvency_rate"], 0.15, delta=0.015)


if __name__ == "__main__":
    unittest.main()
