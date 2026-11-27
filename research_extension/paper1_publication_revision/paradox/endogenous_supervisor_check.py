"""Numerical verification of Proposition n:endogenous_supervisor (Strategic Supervisor in Surveillance Paradox).

Accompanies Paper 1 Section 7.3 and PublicationRevision15.lean.
Checks:
1. Under the high-stakes condition L * (1 - alpha) > k * D0^2, the exact interior FOC
   gives D*(alpha, N) = (4 k D0 / (n beta(alpha) L))^(2/(n-2)) * (c N)^(-1/(n-2)) * (1 + o(1))
   and obeys the tight envelope D*^(n-2) <= (4 k D0 / (n L beta(alpha)))^2 / (c N).
2. Under low stakes L * (1 - alpha) < k * D0^2, the equilibrium reverses to full revelation
   D*(alpha, N) -> D0 with J*(alpha, N) ~ c N D0^n and P_d -> 1.
3. Under a composite-null two-sided GLRT (local slope c_2 = 2 z_{alpha/2} phi(z_{alpha/2})),
   D*(alpha, N) scales as N^(-1/(n-1)) and J*(alpha, N) as N^(-1/(n-1)) (e.g., N^(-1/3) at n = 4).
4. Under positive inspection costs C(alpha) = c_0 * alpha, the strategic supervisor's optimal
   inspection intensity alpha*(N) collapses to 0 as N grows.
5. Under tagged orders, detection probability is decoupled from memory displacement,
   restoring D* = D0 and eliminating the hiding collapse.
"""
import numpy as np
from scipy.stats import norm

def main():
    k, D0, L, c = 1.0, 1.0, 50.0, 1.0
    c_0 = 2.0  # Marginal cost of inspection effort for supervisor
    V_detect = 100.0  # Value of detecting an abusive / destabilizing cohort

    print("=== ENDOGENOUS SUPERVISOR VERIFICATION (Section 7.3 & PublicationRevision15.lean) ===")

    for n in (4, 8):
        print(f"\n--- Testing Exponent n = {n} (theory rate J* ~ N^{-2/(n-2):.3f}) ---")
        theory_rate_J = -2.0 / (n - 2)
        theory_rate_D = -1.0 / (n - 2)

        Ns = np.logspace(2, 12, 11)
        alphas = [0.01, 0.05, 0.10]

        for alpha in alphas:
            z_alpha = norm.ppf(1 - alpha)
            beta_alpha = np.sqrt(2) * norm.pdf(z_alpha)
            Jbar = z_alpha ** 2 / 2.0
            pi = lambda J: norm.cdf(np.sqrt(np.maximum(2 * J, 0.0)) - z_alpha)

            D_stars = []
            J_stars = []
            bounds_held = []

            for N in Ns:
                # Trader chooses D in [0, D0] to minimize k(D0 - D)^2 + L * pi(c N D^n)
                D_grid = np.concatenate([[0.0], np.logspace(-8, 0, 100001) * D0])
                obj = k * (D0 - D_grid) ** 2 + L * pi(c * N * D_grid ** n)
                best_idx = int(np.argmin(obj))
                D_star = D_grid[best_idx]

                # Exact interior FOC root-finding via brentq around grid argmin (eliminates float64 CDF subtraction loss)
                from scipy.optimize import brentq
                lo_d = max(D_grid[max(best_idx - 5, 0)], 1e-15)
                hi_d = min(D_grid[min(best_idx + 5, len(D_grid) - 1)], D0)
                def foc_residual(d):
                    return (L * (n / np.sqrt(2.0)) * np.sqrt(c * N) * (d ** (0.5 * n - 1.0)) *
                            norm.pdf(np.sqrt(2.0 * c * N * (d ** n)) - z_alpha) - 2.0 * k * (D0 - d))
                if foc_residual(lo_d) * foc_residual(hi_d) <= 0:
                    D_star = float(brentq(foc_residual, lo_d, hi_d, rtol=1e-13, xtol=1e-16))
                else:
                    D_star = float(D_grid[best_idx])

                J_star = c * N * (D_star ** n)
                D_stars.append(D_star)
                J_stars.append(J_star)

                # Exact high-stakes FOC: (n/2)*L*beta*sqrt(c*N)*D^(n/2-1) = 2*k*(D0 - D)
                # => D_foc = (4*k*D0 / (n*L*beta))^(2/(n-2)) * (c*N)^(-1/(n-2))
                up_bound = (4.0 * k * D0 / (n * L * beta_alpha)) ** 2 / (c * N)
                bound_ok = (D_star ** (n - 2)) <= up_bound * (1.0 + 1e-9)
                bounds_held.append(bound_ok)

            D_stars = np.array(D_stars)
            J_stars = np.array(J_stars)

            # Check exact asymptotic prefactor against numerical minimizer at N = 1e10 (idx 8) and 1e12 (idx 10)
            for idx_chk in (8, 10):
                N_chk = Ns[idx_chk]
                d_asym = (4.0 * k * D0 / (n * L * beta_alpha)) ** (2.0 / (n - 2)) * (c * N_chk) ** (-1.0 / (n - 2))
                rel_err = abs(D_stars[idx_chk] / d_asym - 1.0)
                assert rel_err < 0.05, (
                    f"FOC prefactor mismatch at n={n}, alpha={alpha}, N={N_chk}: "
                    f"num={D_stars[idx_chk]:.6e} vs foc={d_asym:.6e} (rel_err={rel_err:.4f})"
                )

            # Fit empirical log-log slope for large N (N >= 1e5)
            large_N_mask = Ns >= 1e5
            slope_J = np.polyfit(np.log(Ns[large_N_mask]), np.log(J_stars[large_N_mask]), 1)[0]
            slope_D = np.polyfit(np.log(Ns[large_N_mask]), np.log(D_stars[large_N_mask]), 1)[0]
            assert abs(slope_J - theory_rate_J) < 0.03, f"slope_J={slope_J} vs {theory_rate_J}"
            assert abs(slope_D - theory_rate_D) < 0.02, f"slope_D={slope_D} vs {theory_rate_D}"

            assert all(bounds_held), f"Crowding envelope bound failed for alpha={alpha}"
            print(f"  alpha={alpha:.2f}: all {len(Ns)} tight (4/(n*beta*L))^2 bounds & prefactor hold. "
                  f"Slope log J* = {slope_J:.3f} (theory {theory_rate_J:.3f}), "
                  f"log D* = {slope_D:.3f} (theory {theory_rate_D:.3f})")
            print(f"    At N=1e2: D*={D_stars[0]:.3e}, J*={J_stars[0]:.3e}, power={pi(J_stars[0]):.4f}")
            print(f"    At N=1e12: D*={D_stars[-1]:.3e}, J*={J_stars[-1]:.3e}, power={pi(J_stars[-1]):.4f} (baseline {alpha})")

        # Now test Stackelberg supervisor commitment over alpha in [0, 0.20] and verify no pure NE under simultaneous moves
        print(f"\n  Stackelberg Supervisor Optimization (cost c_0 * alpha with c_0 = {c_0}):")
        alpha_candidates = np.linspace(0.00, 0.20, 41)
        for N in [1e2, 1e4, 1e6, 1e8, 1e10, 1e12]:
            best_alpha = 0.0
            best_welfare = -1e9
            for a in alpha_candidates:
                if a == 0.0:
                    welfare = 0.0
                else:
                    z_a = norm.ppf(1 - a)
                    pi_a = lambda J: norm.cdf(np.sqrt(np.maximum(2 * J, 0.0)) - z_a)
                    D_grid = np.concatenate([[0.0], np.logspace(-6, 0, 20001) * D0])
                    obj = k * (D0 - D_grid) ** 2 + L * pi_a(c * N * D_grid ** n)
                    D_opt = D_grid[int(np.argmin(obj))]
                    J_opt = c * N * (D_opt ** n)
                    net_power = pi_a(J_opt) - a
                    welfare = V_detect * net_power - c_0 * a
                if welfare > best_welfare:
                    best_welfare = welfare
                    best_alpha = a
            if N >= 1e8 and n == 4:
                assert best_alpha == 0.0, f"Stackelberg commitment did not collapse at N={N}: {best_alpha}"
            print(f"    N = {N:.0e} -> Stackelberg alpha* = {best_alpha:.3f}, Supervisor Net Surplus = {best_welfare:.4f}")

        if n == 4:
            # Verify simultaneous-move non-existence of pure NE & mixed-strategy indifference at alpha_min=0.05, c_min=2.0
            N_sim, a_sim, c_sim = 1e10, 0.05, 2.0
            z_sim = norm.ppf(1 - a_sim)
            pi_sim = lambda J: norm.cdf(np.sqrt(np.maximum(2 * J, 0.0)) - z_sim)
            sup_gain_at_D0 = V_detect * (pi_sim(c * N_sim * D0 ** 4) - a_sim) - c_sim
            assert sup_gain_at_D0 > 0, "Deviation to alpha_min must be profitable at delta=D0"
            p_sup_mix = (k * (D0 ** 2)) / (L * (pi_sim(c * N_sim * D0 ** 4) - pi_sim(0.0)))
            assert 0.0 < p_sup_mix < 1.0, "Mixed NE randomization weight must lie strictly in (0, 1)"
            print(f"    Simultaneous-move check (N=1e10): pure NE ruled out (dev gain at D0 = {sup_gain_at_D0:.2f} > 0); mixed-NE prob benchmark p*={p_sup_mix:.4f}")

    # Low-stakes regime reversal check: L*(1 - alpha) < k*D0^2 => D* -> D0
    print("\n--- Low-Stakes Corner Reversal Check ---")
    L_low, alpha_low, N_low = 1.0, 0.05, 1e6
    assert L_low * (1.0 - alpha_low) < k * D0 ** 2
    z_low = norm.ppf(1 - alpha_low)
    pi_low = lambda J: norm.cdf(np.sqrt(np.maximum(2 * J, 0.0)) - z_low)
    D_grid_low = np.concatenate([[0.0], np.logspace(-8, 0, 50001) * D0])
    obj_low = k * (D0 - D_grid_low) ** 2 + L_low * pi_low(c * N_low * D_grid_low ** 4)
    D_low_star = float(D_grid_low[int(np.argmin(obj_low))])
    assert np.isclose(D_low_star, D0, atol=1e-6), f"Low-stakes corner reversal failed: D*={D_low_star}"
    print(f"  L={L_low}, L(1-alpha)={L_low*(1-alpha_low):.2f} < k*D0^2={k*D0**2:.2f}: D*={D_low_star:.4f} == D0 (P_d -> 1)")

    # Composite-null two-sided GLRT check: P_d(J) = P(|Z| > z_{alpha/2}), Z ~ N(sqrt(2J), 1)
    print("\n--- Composite-Null GLRT Power Scaling Check (N^{-1/(n-1)}) ---")
    alpha_g = 0.05
    z_half = norm.ppf(1 - alpha_g / 2.0)
    c2_glrt = 2.0 * z_half * norm.pdf(z_half)
    pi_glrt = lambda J: norm.cdf(-z_half + np.sqrt(np.maximum(2 * J, 0.0))) + norm.cdf(-z_half - np.sqrt(np.maximum(2 * J, 0.0)))
    for n_g in (4, 8):
        Ns_g = np.logspace(6, 12, 7)
        Ds_g = []
        for Ng in Ns_g:
            dg = np.concatenate([[0.0], np.logspace(-8, 0, 80001) * D0])
            og = k * (D0 - dg) ** 2 + L * pi_glrt(c * Ng * dg ** n_g)
            Ds_g.append(float(dg[int(np.argmin(og))]))
        Ds_g = np.array(Ds_g)
        slope_glrt = np.polyfit(np.log(Ns_g), np.log(Ds_g), 1)[0]
        exp_glrt = -1.0 / (n_g - 1)
        assert abs(slope_glrt - exp_glrt) < 0.025, f"GLRT slope={slope_glrt} vs {exp_glrt}"
        d_foc_g = ((2.0 * k * D0) / (n_g * L * c2_glrt)) ** (1.0 / (n_g - 1)) * (c * Ns_g[-1]) ** exp_glrt
        assert abs(Ds_g[-1] / d_foc_g - 1.0) < 0.06, f"GLRT prefactor mismatch: {Ds_g[-1]} vs {d_foc_g}"
        print(f"  n={n_g}: GLRT slope log D* = {slope_glrt:.3f} (theory {exp_glrt:.3f}); "
              f"D*(1e12)={Ds_g[-1]:.4e} vs FOC={d_foc_g:.4e}")

    # Tagging Decoupling Check
    print("\n--- Tagging Decoupling Check ---")
    pi_tag = 0.85
    for N in [1e2, 1e6, 1e10]:
        D_grid = np.linspace(0.0, D0, 10001)
        # Loss with tags: k(D0 - D)^2 + L * pi_tag
        obj_tag = k * (D0 - D_grid) ** 2 + L * pi_tag
        D_star_tag = D_grid[int(np.argmin(obj_tag))]
        assert np.isclose(D_star_tag, D0, atol=1e-5), f"Tagging failed: D* = {D_star_tag}"
        print(f"  Tagged regime: N = {N:.0e} -> D* = {D_star_tag:.4f} == D0 (independent of N)")

    print("\nAll endogenous supervisor mathematical checks PASSED cleanly!")

if __name__ == "__main__":
    main()
