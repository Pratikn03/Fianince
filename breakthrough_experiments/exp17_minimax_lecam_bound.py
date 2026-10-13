"""
exp17_minimax_lecam_bound.py
================================================================================
Breakthrough 2: Global Non-Asymptotic Le Cam Two-Point Minimax Lower Bound
for Arbitrary Biased and Shrinkage Estimators (Theorem IA.D.5)

Resolves the open theoretical scope limitation of Proposition IA.D.3 (which
established N* = 40,374 via the local Cramér-Rao bound for regular, unbiased
estimators). Proves and verifies numerically via an exact, closed-form
moment-matched two-point construction that NO measurable estimator — including
arbitrary biased, ridge-regularized, James-Stein shrinkage, or Bayesian MAP
estimators — can circumvent the Theta((Delta eta)^-6) sample-size scaling for
multi-cohort weight recovery:

1. Exact Moment-Matched Two-Point Construction (No Rescaling or Linearization):
   For any baseline total weight q > 0, center rate bar{eta}, cohort spacing
   Delta eta > 0, and target weight accuracy tau in (0, q/2), define p_- = 1/2 - tau/q
   and p_+ = 1/2 + tau/q, and construct the two-point parameter pair:
     theta_0 = ( q p_-,  q p_+,  bar{eta} - p_+ Delta eta,  bar{eta} + p_- Delta eta ),
     theta_1 = ( q p_+,  q p_-,  bar{eta} - p_- Delta eta,  bar{eta} + p_+ Delta eta ).
   Then:
   (a) Both economies have exact cohort rate separation eta_{i,2} - eta_{i,1} = Delta eta.
   (b) Their weight vectors satisfy ||w(theta_1) - w(theta_0)||_infty = 2 * tau.
   (c) Their zeroth, first, and second centered rate moments match IDENTICALLY:
       M_m(theta_0) = M_m(theta_1) for m in {0, 1, 2}, while their third moment
       differs by M_3(theta_1) - M_3(theta_0) = 4 * tau * p_- * p_+ * (Delta eta)^3.
   (d) Consequently, the exact non-linear closed-loop impulse response difference
       satisfies ||h(theta_1) - h(theta_0)||_2 = Theta(tau * (Delta eta)^3).

2. Non-Asymptotic Le Cam Two-Point Minimax Theorem:
   By the triangle inequality on (R^K, ||.||_infty), no measurable estimator hat{w}_N
   (biased or unbiased) can simultaneously achieve < tau error under both theta_0
   and theta_1. By the exact Neyman-Pearson lemma for Gaussian product measures:
     inf_{hat{w}_N} max_{theta in {theta_0, theta_1}} P_theta(||hat{w}_N - w(theta)||_infty >= tau)
       >= Phi( - sqrt(N) ||h(theta_1) - h(theta_0)||_2 / (2 sigma_h(1)) ),
   requiring N >= N*_LeCam(Delta eta; alpha_fail) = Theta((Delta eta)^-6) probes.
================================================================================
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

import numpy as np
from scipy.optimize import minimize
from scipy.stats import norm

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from breakthrough_experiments.exp15_cohort_information import (
    SIGMA_P,
    TOL,
    V_PROBE,
    h_of,
    jacobian,
    probes_needed,
)

SIGMA_H_1 = SIGMA_P / V_PROBE  # 0.01 / 6.25 = 0.0016


def construct_exact_lecam_pair(delta_eta: float, tau: float = TOL, eta_bar: float = 0.40, q_tot: float = 0.20) -> dict:
    """Construct the exact closed-form moment-matched Le Cam two-point pair (theta_0, theta_1)
    and also compute the further rate-refined non-linear pair with eta_{i,2} - eta_{i,1} >= delta_eta.
    """
    p_minus = 0.5 - tau / q_tot  # 0.45
    p_plus = 0.5 + tau / q_tot   # 0.55

    w0 = np.array([q_tot * p_minus, q_tot * p_plus])  # [0.09, 0.11]
    w1 = np.array([q_tot * p_plus, q_tot * p_minus])  # [0.11, 0.09]

    # Analytic moment-matched rates with exact cohort spacing == delta_eta:
    eta0_analytic = np.array([eta_bar - p_plus * delta_eta, eta_bar + p_minus * delta_eta])
    eta1_analytic = np.array([eta_bar - p_minus * delta_eta, eta_bar + p_plus * delta_eta])

    # Verify exact moment identities m = 0, 1, 2, 3:
    m0_diff = float(np.sum(w1) - np.sum(w0))
    m1_diff = float(np.sum(w1 * (eta1_analytic - eta_bar)) - np.sum(w0 * (eta0_analytic - eta_bar)))
    m2_diff = float(np.sum(w1 * (eta1_analytic - eta_bar) ** 2) - np.sum(w0 * (eta0_analytic - eta_bar) ** 2))
    m3_diff = float(np.sum(w1 * (eta1_analytic - eta_bar) ** 3) - np.sum(w0 * (eta0_analytic - eta_bar) ** 3))
    m3_formula = float(4.0 * tau * p_minus * p_plus * (delta_eta ** 3))

    theta0_an = np.concatenate([w0, eta0_analytic])
    theta1_an = np.concatenate([w1, eta1_analytic])
    h0_an = h_of(theta0_an, 2)
    h1_an = h_of(theta1_an, 2)
    dist_an = float(np.linalg.norm(h1_an - h0_an))

    # Also allow symmetric rate-spacing adjustment delta_eta_i >= 0.9 * delta_eta to match the
    # infinite-horizon frequency-response curvature (minimizing ||h(theta1) - h(theta0)||_2
    # while keeping BOTH economies strictly separated by at least delta_eta_min = 0.95 * delta_eta):
    def obj_sym(params):
        d_shift, d_sp = params
        e0 = np.array([eta_bar - d_shift - 0.5 * d_sp, eta_bar - d_shift + 0.5 * d_sp])
        e1 = np.array([eta_bar + d_shift - 0.5 * d_sp, eta_bar + d_shift + 0.5 * d_sp])
        diff = h_of(np.concatenate([w1, e1]), 2) - h_of(np.concatenate([w0, e0]), 2)
        return float(diff @ diff)

    d_shift0 = (tau / q_tot) * delta_eta
    res = minimize(
        obj_sym,
        [d_shift0, delta_eta],
        bounds=[(0.5 * d_shift0, 1.5 * d_shift0), (delta_eta, delta_eta)],
        method="L-BFGS-B",
        options={"ftol": 1e-16, "gtol": 1e-13},
    )
    d_sh_opt, d_sp_opt = res.x
    eta0_opt = np.array([eta_bar - d_sh_opt - 0.5 * d_sp_opt, eta_bar - d_sh_opt + 0.5 * d_sp_opt])
    eta1_opt = np.array([eta_bar + d_sh_opt - 0.5 * d_sp_opt, eta_bar + d_sh_opt + 0.5 * d_sp_opt])
    theta0_opt = np.concatenate([w0, eta0_opt])
    theta1_opt = np.concatenate([w1, eta1_opt])
    h0_opt = h_of(theta0_opt, 2)
    h1_opt = h_of(theta1_opt, 2)
    dist_opt = float(np.linalg.norm(h1_opt - h0_opt))

    # Use the analytic moment-matched pair if dist_an <= dist_opt, otherwise the exact spacing-equalized pair
    if dist_opt < dist_an:
        theta0, theta1, dist_l2 = theta0_opt, theta1_opt, dist_opt
    else:
        theta0, theta1, dist_l2 = theta0_an, theta1_an, dist_an

    z_95 = float(norm.ppf(0.95))    # 1.644854 (5% minimax failure probability)
    z_975 = float(norm.ppf(0.975))  # 1.959964 (2.5% minimax failure probability / 95% two-sided)

    n_lecam_95 = float(4.0 * (SIGMA_H_1 ** 2) * (z_95 ** 2) / (dist_l2 ** 2))
    n_lecam_975 = float(4.0 * (SIGMA_H_1 ** 2) * (z_975 ** 2) / (dist_l2 ** 2))
    n_lecam_an_95 = float(4.0 * (SIGMA_H_1 ** 2) * (z_95 ** 2) / (dist_an ** 2))

    theta_star = np.array([q_tot / 2.0, q_tot / 2.0, eta_bar - 0.5 * delta_eta, eta_bar + 0.5 * delta_eta])
    n_crb, _ = probes_needed(theta_star, 2, tol=tau)

    fail_prob_N1 = float(norm.cdf(-np.sqrt(1.0) * dist_l2 / (2.0 * SIGMA_H_1)))
    fail_prob_N50 = float(norm.cdf(-np.sqrt(50.0) * dist_l2 / (2.0 * SIGMA_H_1)))

    return {
        "delta_eta": float(delta_eta),
        "tau": float(tau),
        "theta0": [float(x) for x in theta0],
        "theta1": [float(x) for x in theta1],
        "theta0_analytic": [float(x) for x in theta0_an],
        "theta1_analytic": [float(x) for x in theta1_an],
        "exact_cohort_spacing_theta0": float(theta0[3] - theta0[2]),
        "exact_cohort_spacing_theta1": float(theta1[3] - theta1[2]),
        "exact_weight_separation_linf": float(np.max(np.abs(theta1[:2] - theta0[:2]))),
        "moment_diffs_m0_m1_m2": [m0_diff, m1_diff, m2_diff],
        "moment_diff_m3_exact": m3_diff,
        "moment_diff_m3_formula": m3_formula,
        "impulse_l2_distance_analytic": dist_an,
        "impulse_l2_distance_exact": dist_l2,
        "n_star_crb_unbiased": float(n_crb),
        "n_star_lecam_analytic_95pct": n_lecam_an_95,
        "n_star_lecam_95pct_any_estimator": n_lecam_95,
        "n_star_lecam_975pct_any_estimator": n_lecam_975,
        "minimax_fail_prob_N1": fail_prob_N1,
        "minimax_fail_prob_N50": fail_prob_N50,
        "minimax_mse_lower_bound_N50": float((tau ** 2) * fail_prob_N50),
    }


def evaluate_biased_and_unbiased_estimators_mc(
    pair_info: dict,
    N_grid=(50, 1000, 10000, 29000, 40374),
    n_mc: int = 1000,
    seed: int = 20261013,
) -> list[dict]:
    """Benchmark 4 estimator classes (Unregularized ML, Ridge/Tikhonov L2-Penalized ML,
    James-Stein Shrinkage, and Heavy Prior Shrinkage) on the TRUE NON-LINEAR impulse
    responses h(theta_0) and h(theta_1) without any linearization or rescaling.
    """
    rng = np.random.default_rng(seed)
    theta0 = np.array(pair_info["theta0"])
    theta1 = np.array(pair_info["theta1"])
    w0 = theta0[:2]
    w1 = theta1[:2]
    tau = pair_info["tau"]

    # True non-linear impulse responses of theta0 and theta1
    h0 = h_of(theta0, 2)
    h1 = h_of(theta1, 2)
    dist_l2 = float(np.linalg.norm(h1 - h0))

    theta_mid = 0.5 * (theta0 + theta1)
    h_mid = h_of(theta_mid, 2)
    J_mid = jacobian(theta_mid, 2)
    JTJ = J_mid.T @ J_mid
    pinv_ml = np.linalg.pinv(JTJ) @ J_mid.T

    reg_ridge = np.diag([2e-6, 2e-6, 2e-7, 2e-7])
    pinv_ridge = np.linalg.solve(JTJ + reg_ridge, J_mid.T)

    w_prior = np.array([0.10, 0.10])
    results = []

    for N in N_grid:
        sigma_N = SIGMA_H_1 / np.sqrt(float(N))
        lecam_lb_fail = float(norm.cdf(-np.sqrt(float(N)) * dist_l2 / (2.0 * SIGMA_H_1)))
        lecam_lb_mse = float((tau ** 2) * lecam_lb_fail)

        noise0 = rng.normal(0.0, sigma_N, size=(n_mc, len(h0)))
        noise1 = rng.normal(0.0, sigma_N, size=(n_mc, len(h1)))
        Y0 = h0[None, :] + noise0
        Y1 = h1[None, :] + noise1

        est_specs = [
            ("Unregularized_ML", pinv_ml, 0.0),
            ("Ridge_Tikhonov_L2", pinv_ridge, 0.0),
            ("James_Stein_Shrinkage_035", pinv_ml, 0.35),
            ("Heavy_Prior_Shrinkage_075", pinv_ml, 0.75),
        ]

        est_rows = {}
        for name, op, shrink_gamma in est_specs:
            dtheta0 = (Y0 - h_mid[None, :]) @ op.T
            w_hat0 = theta_mid[:2][None, :] + dtheta0[:, :2]
            if shrink_gamma > 0.0:
                w_hat0 = (1.0 - shrink_gamma) * w_hat0 + shrink_gamma * w_prior[None, :]

            dtheta1 = (Y1 - h_mid[None, :]) @ op.T
            w_hat1 = theta_mid[:2][None, :] + dtheta1[:, :2]
            if shrink_gamma > 0.0:
                w_hat1 = (1.0 - shrink_gamma) * w_hat1 + shrink_gamma * w_prior[None, :]

            err0_inf = np.max(np.abs(w_hat0 - w0[None, :]), axis=1)
            err1_inf = np.max(np.abs(w_hat1 - w1[None, :]), axis=1)

            fail0 = float(np.mean(err0_inf >= tau))
            fail1 = float(np.mean(err1_inf >= tau))
            worst_fail = max(fail0, fail1)
            avg_fail = 0.5 * (fail0 + fail1)

            mse0 = float(np.mean(err0_inf ** 2))
            mse1 = float(np.mean(err1_inf ** 2))
            worst_mse = max(mse0, mse1)

            est_rows[name] = {
                "fail_prob_theta0": fail0,
                "fail_prob_theta1": fail1,
                "worst_case_fail_prob": worst_fail,
                "bayes_avg_fail_prob": avg_fail,
                "worst_case_linf_mse": worst_mse,
                "obeys_lecam_bound": bool(worst_fail + 0.025 >= lecam_lb_fail),
            }

        results.append({
            "N": int(N),
            "lecam_minimax_fail_prob_lb": lecam_lb_fail,
            "lecam_minimax_mse_lb": lecam_lb_mse,
            "estimators": est_rows,
        })

    return results


def main():
    seps = [0.30, 0.20, 0.14, 0.10, 0.08, 0.06, 0.05, 0.04]
    sweep = []
    for d_eta in seps:
        info = construct_exact_lecam_pair(d_eta, tau=TOL)
        sweep.append(info)
        print(
            f"Delta_eta={d_eta:4.2f} | ||dh||_an={info['impulse_l2_distance_analytic']:.3e} | "
            f"||dh||_exact={info['impulse_l2_distance_exact']:.3e} | "
            f"N*_CRB={info['n_star_crb_unbiased']:10.1f} | "
            f"N*_LeCam(95%)={info['n_star_lecam_95pct_any_estimator']:10.1f} | "
            f"N*_LeCam(97.5%)={info['n_star_lecam_975pct_any_estimator']:10.1f} | "
            f"FailProb(N=50)={100*info['minimax_fail_prob_N50']:5.1f}%"
        )

    xs = np.log([r["delta_eta"] for r in sweep])
    ys_lecam = np.log([r["n_star_lecam_95pct_any_estimator"] for r in sweep])
    ys_lecam_an = np.log([r["n_star_lecam_analytic_95pct"] for r in sweep])
    ys_crb = np.log([r["n_star_crb_unbiased"] for r in sweep])
    slope_lecam, _ = np.polyfit(xs, ys_lecam, 1)
    slope_lecam_an, _ = np.polyfit(xs, ys_lecam_an, 1)
    slope_crb, _ = np.polyfit(xs, ys_crb, 1)

    pair_010 = next(r for r in sweep if abs(r["delta_eta"] - 0.10) < 1e-6)
    n_lecam_exact = int(round(pair_010["n_star_lecam_95pct_any_estimator"]))
    mc_bench = evaluate_biased_and_unbiased_estimators_mc(
        pair_010,
        N_grid=(50, 1000, 10000, n_lecam_exact, 40374),
        n_mc=1000,
    )

    print(f"\nScaling slopes: CRB={slope_crb:.3f}, LeCam_Exact={slope_lecam:.3f}, LeCam_Analytic={slope_lecam_an:.3f}")
    for row in mc_bench:
        N = row["N"]
        lb = row["lecam_minimax_fail_prob_lb"]
        ml_f = row["estimators"]["Unregularized_ML"]["worst_case_fail_prob"]
        rg_f = row["estimators"]["Ridge_Tikhonov_L2"]["worst_case_fail_prob"]
        js_f = row["estimators"]["James_Stein_Shrinkage_035"]["worst_case_fail_prob"]
        hp_f = row["estimators"]["Heavy_Prior_Shrinkage_075"]["worst_case_fail_prob"]
        print(
            f"N={N:6d}: LeCam_LB={100*lb:5.1f}% | ML={100*ml_f:5.1f}% | "
            f"Ridge={100*rg_f:5.1f}% | JS_0.35={100*js_f:5.1f}% | Prior_0.75={100*hp_f:5.1f}%"
        )

    out = {
        "theorem": "Theorem IA.D.5: Global Non-Asymptotic Le Cam Two-Point Minimax Lower Bound for Arbitrary Biased and Shrinkage Estimators",
        "tau": TOL,
        "sigma_h_single_probe": SIGMA_H_1,
        "loglog_slope_lecam_exact": float(slope_lecam),
        "loglog_slope_lecam_analytic": float(slope_lecam_an),
        "loglog_slope_crb": float(slope_crb),
        "separation_sweep": sweep,
        "estimator_benchmark_delta_eta_010": mc_bench,
    }
    out_path = Path(__file__).with_name("results_exp17_minimax_lecam_bound.json")
    out_path.write_text(json.dumps(out, indent=2))
    print(f"Saved {out_path}")


if __name__ == "__main__":
    main()
