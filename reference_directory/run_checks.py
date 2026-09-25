"""Executable numerical consistency checks for the Machine Markets mathematical supplement.

Runs:
1. 120 continuous systems with heterogeneous rates, common-rate complex modes, and Euler behavior.
2. Gaussian calibration illustration (R=32, p=4, 10,000 panels, seed 240926):
   - Exact F radius squared = 12.12340136
   - Exact F coverage = 9,476 / 10,000 (94.76%)
   - Chi-squared coverage = 8,946 / 10,000 (89.46%)
   - Monte Carlo SE approx 0.218 percentage points
3. 200 off-grid positive-model fixtures verifying McCormick and rate-bin outer envelopes.
4. Calculation log verification:
   - S = 0.82 vs rho(J) = 0.9900902493
   - Two-sided P(|T_8| >= 2.47) = 0.03871045
   - Decision-coverage bound = 14.88%
   - Proposition 5.3 four-coefficient rational witness

Usage:
  python run_checks.py
"""
import sys
import time
from fractions import Fraction
import numpy as np
from scipy import stats, linalg

# Support running directly from reference_directory or repo root
try:
    from reference_directory.continuous import (
        build_continuous_matrix,
        is_hurwitz,
        spectral_radius,
        spectral_abscissa,
        hurwitz_threshold_spectral_radius,
        common_rate_spectral_abscissa_formula,
        forward_euler_matrix,
        max_admissible_euler_step,
        exact_sampled_matrix,
        euler_error_theoretical_bound,
    )
    from reference_directory.group import (
        verify_known_rate_identifiability,
        recover_unknown_rate_and_q,
        four_tap_aggregate_recovery,
    )
    from reference_directory.ellipsoid import (
        hotelling_f_critical_value,
        linear_contrast_support,
        get_four_coefficient_witness,
    )
    from reference_directory.conic import (
        compute_coordinate_bounds_from_ellipsoid,
        compute_data_derived_mass_cap,
        compute_rate_bin_envelopes,
        mccormick_envelopes,
        verify_conic_lift_containment,
    )
    from reference_directory.decisions import (
        compute_two_world_abstention_bound,
    )
except ImportError:
    from continuous import (
        build_continuous_matrix,
        is_hurwitz,
        spectral_radius,
        spectral_abscissa,
        hurwitz_threshold_spectral_radius,
        common_rate_spectral_abscissa_formula,
        forward_euler_matrix,
        max_admissible_euler_step,
        exact_sampled_matrix,
        euler_error_theoretical_bound,
    )
    from group import (
        verify_known_rate_identifiability,
        recover_unknown_rate_and_q,
        four_tap_aggregate_recovery,
    )
    from ellipsoid import (
        hotelling_f_critical_value,
        linear_contrast_support,
        get_four_coefficient_witness,
    )
    from conic import (
        compute_coordinate_bounds_from_ellipsoid,
        compute_data_derived_mass_cap,
        compute_rate_bin_envelopes,
        mccormick_envelopes,
        verify_conic_lift_containment,
    )
    from decisions import (
        compute_two_world_abstention_bound,
    )


def run_continuous_systems_checks(num_systems: int = 120, seed: int = 240926) -> None:
    """Verify 120 continuous-time systems across heterogeneous and common rates."""
    print(f"\n[1/4] Running {num_systems} continuous-time system fixtures (Theorem 3.3, Prop 3.5, Theorem 3.6)...")
    rng = np.random.default_rng(seed)
    passed_hurwitz_checks = 0
    passed_sa_formula_checks = 0
    passed_euler_checks = 0

    for i in range(num_systems):
        d = int(rng.integers(1, 4))
        n = int(rng.integers(1, 5))

        # Random rates
        Gamma_diag = rng.uniform(0.5, 3.0, size=d)
        E_diag = rng.uniform(0.05, 1.5, size=n)
        B = rng.uniform(0.0, 1.5, size=(d, n))
        C = rng.uniform(0.0, 1.5, size=(n, d))
        g = float(rng.uniform(0.0, 3.0))

        A_c = build_continuous_matrix(Gamma_diag, B, C, E_diag, g)
        rho_thresh = hurwitz_threshold_spectral_radius(Gamma_diag, B, C, g)
        hurwitz_actual = is_hurwitz(A_c)

        # Theorem 3.3 check
        assert (rho_thresh < 1.0) == hurwitz_actual, f"Theorem 3.3 failed for system {i}"
        passed_hurwitz_checks += 1

        # Proposition 3.5 check (when d=1, common gamma, common lambda)
        gamma_scalar = float(Gamma_diag[0])
        lambda_scalar = float(E_diag[0])
        B_comm = rng.uniform(0.1, 1.0, size=(2, 2))
        C_comm = rng.uniform(0.1, 1.0, size=(2, 2))
        nu_comm = spectral_radius(B_comm @ C_comm)
        g_comm = float(rng.uniform(0.1, 2.0))

        A_comm = build_continuous_matrix(
            np.array([gamma_scalar, gamma_scalar]),
            B_comm,
            C_comm,
            np.array([lambda_scalar, lambda_scalar]),
            g_comm,
        )
        sa_num = spectral_abscissa(A_comm)
        sa_formula = common_rate_spectral_abscissa_formula(gamma_scalar, lambda_scalar, nu_comm, g_comm)
        assert abs(sa_num - sa_formula) < 1e-9, f"Prop 3.5 formula error: {abs(sa_num - sa_formula)}"
        passed_sa_formula_checks += 1

        # Theorem 3.6 Euler step check
        h_max = max_admissible_euler_step(Gamma_diag, E_diag)
        h = float(rng.uniform(0.1 * h_max, 0.9 * h_max))
        P_h = forward_euler_matrix(A_c, h)
        assert np.all(P_h >= -1e-12), "Euler matrix has negative entries"
        schur_actual = (spectral_radius(P_h) < 1.0)
        assert schur_actual == hurwitz_actual, f"Euler Schur equivalence failed for system {i}"

        # Euler error bound check for small T
        T = 0.5
        k = max(1, int(T / h))
        P_k = np.linalg.matrix_power(P_h, k)
        exact_exp = exact_sampled_matrix(A_c, k * h)
        err = float(np.linalg.norm(P_k - exact_exp, ord=2))
        bound = euler_error_theoretical_bound(A_c, h, k * h, ord=2)
        assert err <= bound + 1e-10, f"Euler error {err} exceeded bound {bound}"
        passed_euler_checks += 1

    print(f"  -> Passed {passed_hurwitz_checks} Hurwitz small-gain tests.")
    print(f"  -> Passed {passed_sa_formula_checks} spectral abscissa formula tests.")
    print(f"  -> Passed {passed_euler_checks} Euler scaling and discretization error tests.")


def run_gaussian_calibration_illustration(seed: int = 240926, num_panels: int = 10000) -> None:
    """Execute the Gaussian calibration illustration (R=32, p=4, seed 240926)."""
    print(f"\n[2/4] Running Gaussian response ellipsoid calibration illustration ({num_panels} panels, seed={seed})...")
    p = 4
    R = 32
    nu = R - 2
    df1 = p
    df2 = nu - p + 1

    k_alpha_sq, f_crit, _, _ = hotelling_f_critical_value(p, R, alpha=0.05)
    chi2_crit = float(stats.chi2.ppf(0.95, p))

    print(f"  Parameters: R={R}, p={p}, nu={nu}, df1={df1}, df2={df2}")
    print(f"  Exact F critical value: F^inv(0.95, {df1}, {df2}) = {f_crit:.8f}")
    print(f"  Exact response ellipsoid squared radius: k_alpha^2 = {k_alpha_sq:.8f}")
    assert abs(k_alpha_sq - 12.12340136) < 1e-7, f"Radius mismatch: {k_alpha_sq} vs 12.12340136"

    # Pulse design: alternating +-1 shares for 32 episodes
    u = np.tile([1.0, -1.0], 16)
    v = u - np.mean(u)
    D = np.sum(v ** 2)

    rng = np.random.default_rng(seed)
    in_F_count = 0
    in_chi2_count = 0

    t0 = time.time()
    for _ in range(num_panels):
        eps = rng.standard_normal((R, p))
        b_hat = np.sum(v[:, None] * eps, axis=0) / D
        m_hat = np.mean(eps, axis=0) - np.mean(u) * b_hat
        residuals = eps - m_hat - np.outer(u, b_hat)
        Sigma_hat = (residuals.T @ residuals) / nu
        V = Sigma_hat / D

        # Mahalanobis distance T^2
        T_sq = float(b_hat @ np.linalg.solve(V, b_hat))
        if T_sq <= k_alpha_sq:
            in_F_count += 1
        if T_sq <= chi2_crit:
            in_chi2_count += 1

    elapsed = time.time() - t0
    f_coverage_pct = (in_F_count / num_panels) * 100.0
    chi2_coverage_pct = (in_chi2_count / num_panels) * 100.0
    mc_se_pct = float(np.sqrt(0.95 * 0.05 / num_panels) * 100.0)

    print(f"  Results over {num_panels} panels (completed in {elapsed:.2f}s):")
    print(f"    Exact F-calibrated ellipsoid coverage: {in_F_count}/{num_panels} ({f_coverage_pct:.2f}%)")
    print(f"    Nominal Monte Carlo standard error:    {mc_se_pct:.3f} percentage points")
    print(f"    Unjustified chi^2_4 coverage:          {in_chi2_count}/{num_panels} ({chi2_coverage_pct:.2f}%)")

    assert in_F_count == 9476, f"Expected 9,476 inclusions, got {in_F_count}"
    assert in_chi2_count == 8946, f"Expected 8,946 inclusions, got {in_chi2_count}"
    print("  -> EXACT MATCH verified: 9,476 (94.76%) vs 8,946 (89.46%).")


def run_offgrid_model_fixtures(num_fixtures: int = 200, seed: int = 240926) -> None:
    """Verify 200 off-grid positive-model fixtures under McCormick and rate-bin outer envelopes."""
    print(f"\n[3/4] Running {num_fixtures} off-grid positive-model containment fixtures (Theorem 7.2)...")
    rng = np.random.default_rng(seed)

    # 4 bins spanning [0.02, 1.0]
    bin_edges = [(0.02, 0.10), (0.10, 0.30), (0.30, 0.60), (0.60, 1.00)]
    k_alpha = np.sqrt(12.12340136)

    passed_lifts = 0
    for _ in range(num_fixtures):
        a_true = float(rng.uniform(0.1, 0.7))
        num_agents = int(rng.integers(2, 6))

        # Off-grid random rates and weights
        eta_true = rng.uniform(0.025, 0.95, size=num_agents)
        q_true = rng.uniform(0.01, 0.25, size=num_agents)
        kappa_true = 0.02

        # True impulse responses through lag 4
        h = np.zeros(4)
        h[0] = 1.0
        h[1] = a_true
        k = np.zeros(4)
        for j in range(4):
            k[j] = np.sum(q_true * eta_true * ((1.0 - eta_true) ** j))
        h[2] = a_true * h[1] + k[0] * h[0]
        h[3] = a_true * h[2] + k[0] * h[1] + k[1] * h[0]
        b_true = kappa_true * h

        # Synthetic observation center with small noise
        beta_hat = b_true + rng.normal(0.0, 0.0005, size=4)
        beta_hat[0] = max(0.01, beta_hat[0])
        V = 1e-5 * np.eye(4)

        res = verify_conic_lift_containment(
            a_true=a_true,
            q_true=q_true,
            eta_true=eta_true,
            kappa_true=kappa_true,
            beta_hat=beta_hat,
            V=V,
            k_alpha=k_alpha,
            bin_edges=bin_edges,
            a_bar=1.0,
            H=4,
        )

        assert res["is_conic_lift_valid"], f"Conic lift failed for fixture: {res}"
        passed_lifts += 1

    print(f"  -> All {passed_lifts}/{num_fixtures} off-grid fixtures satisfied McCormick and rate-bin outer envelopes.")


def run_calculation_log_verification() -> None:
    """Verify exact calculation log quantities from the manuscript and supplement."""
    print("\n[4/4] Verifying calculation log quantities and exact mathematical witnesses...")

    # 1. Audited baseline S = 0.82 vs rho(J) = 0.9900902493
    a = 0.4
    q = np.array([0.252, 0.168])
    eta = np.array([0.5, 0.02])
    J = np.array([
        [a, 1.0, 1.0],
        [eta[0] * q[0], 1.0 - eta[0], 0.0],
        [eta[1] * q[1], 0.0, 1.0 - eta[1]],
    ])
    S = float(a + np.sum(q))
    rho = float(np.max(np.abs(np.linalg.eigvals(J))))
    print(f"  Baseline total feedback gain: S = {S:.2f}")
    print(f"  Baseline spectral radius:     rho(J) = {rho:.10f}")
    assert abs(S - 0.82) < 1e-9, f"S mismatch: {S}"
    assert abs(rho - 0.9900902493) < 1e-8, f"rho(J) mismatch: {rho}"

    # 2. Conventional two-sided t-distribution p-value at t=2.47 on df=8
    t_stat = 2.47
    p_t8 = float(2.0 * stats.t.sf(t_stat, df=8))
    print(f"  Two-sided p-value P(|T_8| >= 2.47): {p_t8:.8f}")
    assert abs(p_t8 - 0.03871045) < 1e-7, f"T_8 p-value mismatch: {p_t8}"

    # 3. Two-world decision coverage bound at level-noise forced error 47.56%
    p_star = 0.47562460
    e = 0.05
    c_bound = compute_two_world_abstention_bound(e=e, p_star=p_star)
    print(f"  Two-world decision coverage bound (e=0.05, p*=47.56%): {c_bound * 100:.2f}% ({c_bound:.8f})")
    assert abs(c_bound - 0.14875080) < 1e-7, f"Abstention bound mismatch: {c_bound}"

    # 4. Proposition 5.3 rational witness
    witness = get_four_coefficient_witness()
    print(f"  Proposition 5.3 four-coefficient rational witness:")
    print(f"    Stable economy:   S_0 = {witness['S0']} < 1 (stable: {witness['is_S0_stable']})")
    print(f"    Unstable economy: S_1 = {witness['S1']} > 1 (stable: {witness['is_S1_stable']})")
    print(f"    Identical response: {witness['h_seq0']}")
    assert witness["h_sequences_identical"]
    assert witness["is_S0_stable"] and not witness["is_S1_stable"]

    print("  -> All calculation log checks verified successfully.")


def main():
    print("=" * 80)
    print("MACHINE MARKETS / MATHEMATICAL SUPPLEMENT: NUMERICAL CHECKS")
    print("Corrected identification theorems, continuous-time stability, and covariance inference")
    print("=" * 80)

    t_start = time.time()
    run_continuous_systems_checks(num_systems=120)
    run_gaussian_calibration_illustration(seed=240926, num_panels=10000)
    run_offgrid_model_fixtures(num_fixtures=200)
    run_calculation_log_verification()
    t_total = time.time() - t_start

    print("\n" + "=" * 80)
    print(f"ALL NUMERICAL CONSISTENCY CHECKS PASSED SUCCESSFULLY in {t_total:.2f}s.")
    print("=" * 80)


if __name__ == "__main__":
    main()
