"""Anytime-valid sequential certification by reset probes (blueprint D10; Paper 2, Internet Appendix, Proposition prop:probe).

Each probe returns X_e = sum_{t<T} h_t^(e), independent with mean S_T and a sub-Gaussian proxy sigma_T^2 (under contract O1,
sigma_T^2 = T sigma^2). With the normal-mixture martingale
    M_n = sqrt(rho/(V_n+rho)) exp(D_n^2 / (2 (V_n+rho))),  D_n = sum_e (X_e - S_T),  V_n = n sigma_T^2,
Ville's inequality gives P(exists n: |D_n| >= b_n) <= gamma with
    b_n = sqrt((V_n + rho) (log((V_n + rho)/rho) + 2 log(1/gamma))).
So [Xbar_n - b_n/n, Xbar_n + b_n/n] (+ the tail bound on the upper side) covers S_T SIMULTANEOUSLY for all n: any stopping rule
is valid. The guard probes until it can certify safe (upper <= s_B), certify unsafe (lower > s_B), or reaches n_max (abstain).
"""
import numpy as np
from scipy import stats


def cs_radius(n, sigma_T, gamma, rho=None):
    V = n * sigma_T ** 2
    rho = sigma_T ** 2 * 10 if rho is None else rho                 # tuned for n of order 10
    return np.sqrt((V + rho) * (np.log((V + rho) / rho) + 2 * np.log(1 / gamma))) / n


def sequential_guard(draw, s_budget, sigma_T, gamma=0.05, tail=0.0, n_max=10000):
    """draw() -> one probe's X_e. Returns (decision, n) with decision in {'safe', 'unsafe', 'abstain'}."""
    s = 0.0
    for n in range(1, n_max + 1):
        s += draw(); xb = s / n; r = cs_radius(n, sigma_T, gamma)
        if xb + r + tail <= s_budget:
            return "safe", n
        if xb - r > s_budget:
            return "unsafe", n
    return "abstain", n_max


def fixed_N(eps, sigma_T, gamma=0.05):
    """Fixed design that certifies to precision eps: one-sided z margin <= eps/2 with the same error level."""
    z = stats.norm.ppf(1 - gamma)
    return int(np.ceil((2 * z * sigma_T / eps) ** 2))


def simulate(S_true, s_budget, sigma_T, reps=2000, gamma=0.05, seed=0, n_max=20000):
    R = np.random.default_rng(seed)
    out = {"safe": 0, "unsafe": 0, "abstain": 0}; ns = []
    for _ in range(reps):
        d, n = sequential_guard(lambda: S_true + sigma_T * R.standard_normal(), s_budget, sigma_T, gamma, n_max=n_max)
        out[d] += 1; ns.append(n)
    wrong = out["safe"] if S_true > s_budget else out["unsafe"]
    return {"S_true": S_true, "gap": abs(S_true - s_budget), "mean_probes": float(np.mean(ns)), "p90_probes": float(np.quantile(ns, 0.9)),
            "error_rate": wrong / reps, "abstain_rate": out["abstain"] / reps}


def run_probing():
    """D10 / test T14: sequential (anytime-valid) certification versus a fixed design that must be sized for the smallest
    gap of interest. Probe noise as in the O1' example: per-episode sum sd sigma_T = 0.05 sqrt(12)."""
    sT = 0.05 * np.sqrt(12); sB = 2.0; eps_design = 0.05
    rows = [simulate(S, sB, sT, reps=1000, seed=int(1000 * S)) for S in [1.5, 1.8, 1.9, 1.95, 2.05, 2.2, 2.5]]
    nf = fixed_N(eps_design, sT)
    for r in rows:
        r["fixed_design_N_for_gap_0.05"] = nf
    return {"sigma_T": sT, "s_budget": sB, "rows": rows, "fixed_N": nf,
            "pass": bool(all(r["error_rate"] <= 0.05 for r in rows))}
