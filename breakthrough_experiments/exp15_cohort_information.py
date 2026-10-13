#!/usr/bin/env python3
"""
Experiment 15: Cramér-Rao Local Sample-Size Benchmark for Multi-Cohort Weight Recovery (closes exp2 gate).

exp2 showed that the ERA/transmission-zero estimator fails to recover per-cohort weights for
K >= 2 under noise, for close rates, and for K = 3 even without noise. This experiment separates
two different causes:

  (i) estimator defect   - does a better estimator succeed when information is sufficient?
 (ii) local CRB benchmark - how many independent reset probes N* are needed for an unbiased /
                            locally asymptotically normal estimator to reach the +/- 0.01 tolerance?

Observation model (same economy as exp2): the observer estimates the closed-loop impulse response
h(theta), t = 0..T, theta = (w_1..w_K, eta_1..eta_K), with iid Gaussian error of standard deviation
sigma_h. With N independent reset probes of size V and price noise sigma_p, sigma_h = sigma_p/(V sqrt N).

Cramér-Rao local benchmark. F(theta) = J^T J / sigma_h^2 with J = d h / d theta. For every locally
unbiased estimator Var(w_k_hat) >= [F^{-1}]_{kk}; asymptotically the same bound holds for regular
estimators (Hájek-Le Cam convolution theorem). We report the local sample-size benchmark N* such that
the CRB standard deviation of every weight is at most tol/1.96 (tol = 0.01, the exp2 tolerance).

Estimator. Maximum likelihood (nonlinear least squares with multi-start over rate grids), with the
number of cohorts either known or chosen blindly by BIC over K in {0, 1, 2, 3, 4}. Monte Carlo
compares its RMSE, max bias, and 95% CI coverage to the CRB.
"""
import itertools
import json
import sys
from pathlib import Path

import numpy as np
from scipy.optimize import least_squares

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from breakthrough_experiments.exp2_unknown_mixture import (  # noqa: E402
    blind_transfer_function_inversion, simulate_closed_loop_impulse,
)

T = 120
TOL = 0.01
SIGMA_P, V_PROBE = 0.01, 6.25


def h_of(theta, K):
    return simulate_closed_loop_impulse(np.asarray(theta[:K]), np.asarray(theta[K:]), T=T)


def jacobian(theta, K, step=1e-6):
    theta = np.asarray(theta, float)
    J = np.empty((T + 1, 2 * K))
    for j in range(2 * K):
        e = np.zeros(2 * K); e[j] = step
        J[:, j] = (h_of(theta + e, K) - h_of(theta - e, K)) / (2 * step)
    return J


def crb_unit(theta, K):
    """Diagonal of F^{-1} for sigma_h = 1 (weights first, then rates)."""
    J = jacobian(theta, K)
    return np.diag(np.linalg.pinv(J.T @ J))


def probes_needed(theta, K, tol=TOL):
    c = crb_unit(theta, K)[:K].max()
    sd_target = tol / 1.96
    return float(c * (SIGMA_P / V_PROBE) ** 2 / sd_target ** 2), float(np.sqrt(c))


def _warm_weights(h_obs, eta0, kappa=0.8, a=0.5):
    """Project implied feedback flow u_t = (x_t - a x_{t-1})/kappa onto cohort filter states y_{k,t-1}."""
    from scipy.optimize import nnls
    K = len(eta0)
    T_len = len(h_obs) - 1
    Y = np.empty((T_len, K))
    for k, ek in enumerate(eta0):
        yk = ek * h_obs[0]
        Y[0, k] = yk
        one_m = 1.0 - ek
        for t in range(1, T_len):
            yk = one_m * yk + ek * h_obs[t]
            Y[t, k] = yk
    u = (h_obs[1:] - a * h_obs[:-1]) / kappa
    w0, _ = nnls(Y, u)
    return np.clip(w0, 0.0, 1.0)


def ml_fit(h_obs, K, n_starts=None):
    if K == 0:
        return np.array([]), float(np.sum((h_obs - simulate_closed_loop_impulse(np.array([]), np.array([]), T=T)) ** 2))
    grid = np.linspace(0.1, 0.85, 6)
    starts = [np.array(c) for c in itertools.combinations(grid, K)]
    lb = np.concatenate([np.zeros(K), np.full(K, 0.01)])
    ub = np.concatenate([np.ones(K), np.full(K, 0.99)])
    scored = []
    for eta0 in starts:
        w_warm = _warm_weights(h_obs, eta0)
        x_warm = np.concatenate([w_warm, eta0])
        c_warm = float(np.sum((h_of(x_warm, K) - h_obs) ** 2))
        x_flat = np.concatenate([np.full(K, 0.2 / K), eta0])
        c_flat = float(np.sum((h_of(x_flat, K) - h_obs) ** 2))
        if c_warm <= c_flat:
            scored.append((c_warm, x_warm))
        else:
            scored.append((c_flat, x_flat))
    scored.sort(key=lambda item: item[0])
    candidates = [x for _, x in scored[:min(5, len(scored))]]
    best = None
    for x0 in candidates:
        r = least_squares(lambda th: h_of(th, K) - h_obs, x0, bounds=(lb, ub), xtol=1e-8, ftol=1e-8,
                          gtol=1e-8, max_nfev=400)
        if best is None or r.cost < best.cost:
            best = r
    th = best.x
    order = np.argsort(th[K:])
    return np.concatenate([th[:K][order], th[K:][order]]), float(2 * best.cost)


def bic_select(h_obs, sigma_h, K_candidates=(1, 2, 3, 4), precomputed=None):
    """
    Model order selection via Bayesian Information Criterion over a fixed prespecified candidate set.
    Evaluates candidate model orders blindly without oracle centering on the true K.
    """
    n = len(h_obs)
    scores, fits = [], []
    for K in K_candidates:
        if precomputed is not None and K in precomputed:
            th, rss = precomputed[K]
        else:
            th, rss = ml_fit(h_obs, K)
        scores.append(rss / sigma_h ** 2 + 2 * K * np.log(n))
        fits.append(th)
    k = int(np.argmin(scores))
    return K_candidates[k], fits[k]


def scenario(name, w, eta):
    return dict(name=name, w=np.array(w, float), eta=np.array(eta, float))


SCENARIOS = [
    scenario("K=1 eta=0.30", [0.20], [0.30]),
    scenario("K=2 d_eta=0.30", [0.10, 0.10], [0.25, 0.55]),
    scenario("K=2 d_eta=0.20", [0.10, 0.10], [0.30, 0.50]),
    scenario("K=2 d_eta=0.10 (delta=0.05 pair)", [0.10, 0.10], [0.35, 0.45]),
    scenario("K=2 d_eta=0.05", [0.10, 0.10], [0.375, 0.425]),
    scenario("K=3 spacing 0.10", [0.2 / 3] * 3, [0.30, 0.40, 0.50]),
    scenario("K=3 spacing 0.20", [0.2 / 3] * 3, [0.20, 0.40, 0.60]),
]


def run_experiment(n_mc=20, seed=7):
    rng = np.random.default_rng(seed)
    rows = []
    for sc in SCENARIOS:
        K = len(sc["w"])
        theta = np.concatenate([sc["w"], sc["eta"]])
        N_star, crb_sd_unit = probes_needed(theta, K)
        h = h_of(theta, K)
        # noiseless recovery: old estimator vs ML
        kE, _, wE = blind_transfer_function_inversion(h.copy())
        old_ok = bool(kE == K and np.all(np.abs(np.sort(wE) - np.sort(sc["w"])) <= TOL)) if K > 0 else kE == 0
        th_ml, _ = ml_fit(h, K)
        ml_noiseless_err = float(np.max(np.abs(th_ml[:K] - sc["w"])))
        # Monte Carlo at noise levels expressed relative to the CRB-critical level
        sd_target = TOL / 1.96
        sigma_crit = sd_target / crb_sd_unit                 # sigma_h at which CRB sd = target
        crb_unit_vec = np.sqrt(crb_unit(theta, K)[:K])
        mc = []
        for f in (0.25, 1.0, 4.0):
            sh = f * sigma_crit
            crb_sd_vec = sh * crb_unit_vec
            errs, succ, succ_bic, kcorrect, cov95 = [], 0, 0, 0, 0
            for _ in range(n_mc):
                y = h + sh * rng.standard_normal(h.shape)
                th, rss = ml_fit(y, K)
                e = th[:K] - sc["w"]
                errs.append(e)
                succ += int(np.all(np.abs(e) <= TOL))
                cov95 += int(np.all(np.abs(e) <= 1.96 * crb_sd_vec))
                kb, thb = bic_select(y, sh, precomputed={K: (th, rss)})
                kcorrect += int(kb == K)
                succ_bic += int(kb == K and np.all(np.abs(thb[:K] - sc["w"]) <= TOL))
            errs = np.array(errs)
            mc.append(dict(noise_over_critical=f, sigma_h=float(sh),
                           equivalent_probes=float((SIGMA_P / V_PROBE / sh) ** 2),
                           crb_sd_weight=float(f * sd_target),
                           ml_rmse_weight=float(np.sqrt((errs ** 2).mean(0)).max()),
                           ml_max_bias_weight=float(np.abs(errs.mean(0)).max()),
                           ml_ci95_coverage=float(cov95 / n_mc),
                           ml_success_known_K=succ / n_mc, bic_K_correct=kcorrect / n_mc,
                           ml_success_bic=succ_bic / n_mc))
        row = dict(scenario=sc["name"], K=K, weights=sc["w"].tolist(), rates=sc["eta"].tolist(),
                   crb_sd_weight_unit_noise=crb_sd_unit, sigma_h_critical=float(sigma_crit),
                   probes_needed_N_star=N_star, single_probe_sigma_h=SIGMA_P / V_PROBE,
                   old_estimator_noiseless_success=old_ok, ml_noiseless_max_weight_error=ml_noiseless_err,
                   monte_carlo=mc)
        rows.append(row)
        print(f"{sc['name']:36s} N*={N_star:12.1f}  sigma_crit={sigma_crit:.2e}  old_noiseless={old_ok}  "
              f"ML_noiseless_err={ml_noiseless_err:.1e}  " +
              "  ".join(f"[f={m['noise_over_critical']}: succ={m['ml_success_known_K']:.2f} "
                        f"rmse/crb={m['ml_rmse_weight'] / m['crb_sd_weight']:.2f} "
                        f"bias={m['ml_max_bias_weight']:.1e} cov95={m['ml_ci95_coverage']:.2f} bicK={m['bic_K_correct']:.2f}]"
                        for m in mc))
    # scaling of N* with rate separation (K=2, equal weights, centre 0.40)
    seps = np.array([0.04, 0.06, 0.08, 0.10, 0.14, 0.20])
    Ns = np.array([probes_needed(np.array([0.1, 0.1, 0.4 - s / 2, 0.4 + s / 2]), 2)[0] for s in seps])
    slope = float(np.polyfit(np.log(seps), np.log(Ns), 1)[0])
    print("N* vs separation:", dict(zip(seps.tolist(), Ns.round(1).tolist())), "log-log slope", round(slope, 3))
    out = dict(T=T, tol=TOL, sigma_p=SIGMA_P, V_probe=V_PROBE, n_mc=n_mc, scenarios=rows,
               separation_scaling=dict(separations=seps.tolist(), probes_needed=Ns.tolist(), loglog_slope=slope))
    Path(ROOT / "breakthrough_experiments/results_exp15_cohort_information.json").write_text(
        json.dumps(out, indent=2, default=float))
    return out


if __name__ == "__main__":
    run_experiment()
