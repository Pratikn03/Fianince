"""Statistical certificates for the summed response (Paper 2, Theorem thm:certcost and Proposition prop:hotelling; blueprint
D5, D8, E03).

Contract (O1): N reset experiments, independent Gaussian tap noise with known sd sigma. Class K(rho, sbar): positive cohort
economies with memory rates r_i <= rho and a + kappa*Phi <= sbar < 1. Then h_t <= kappa * lam^t with lam = 1-(1-rho)(1-sbar),
so sum_{t>=T} h_t <= kappa lam^T / (1-lam).  Certificate: S_up = sum_{t<T} hbar_t + z_{1-gamma} sigma sqrt(T/N) + tail.

Contract (O1'): the same, but the noise covariance across taps is UNKNOWN (any within-episode correlation):
  t-certificate:  S_up = mean_e X_e + t_{N-1,1-gamma} sd(X_e)/sqrt(N) + tail,  X_e = sum_{t<T} h_t^(e)   (exact coverage)
  Hotelling:      {m : N (hbar - m)' Shat^{-1} (hbar - m) <= T^2_crit},  T^2_crit = T(N-1)/(N-T) F_{T,N-T}(1-gamma),
                  exact simultaneous coverage for the whole mean window; c'm <= c'hbar + sqrt(T^2_crit c'Shat c / N) for all c.
"""
import numpy as np
from scipy import stats
from scipy.stats import norm
from model_contracts import impulse, summed_response


def lam_bar(rho, sbar):
    return 1.0 - (1.0 - rho) * (1.0 - sbar)


def tail_bound(kappa, rho, sbar, T):
    lam = lam_bar(rho, sbar)
    return kappa * lam ** T / (1 - lam)


def T_for(eps, kappa, rho, sbar):
    lam = lam_bar(rho, sbar)
    return max(1, int(np.ceil(np.log(2 * kappa / ((1 - lam) * eps)) / np.log(1 / lam))))


def certificate(hbar, sigma, N, kappa, rho, sbar, T, gamma=0.05):
    z = norm.ppf(1 - gamma)
    return float(np.sum(hbar[:T]) + z * sigma * np.sqrt(T / N) + tail_bound(kappa, rho, sbar, T))


def N_sufficient(eps, sigma, kappa, rho, sbar, gamma=0.05):
    """Excess S_up - S <= eps with prob >= 1 - gamma (one more gamma for the two-sided normal event)."""
    T = T_for(eps, kappa, rho, sbar); z = norm.ppf(1 - gamma)
    return int(np.ceil(16 * z ** 2 * sigma ** 2 * T / eps ** 2)), T


def lower_bound_N(eps, sigma, dh_per_dS, gamma=0.05):
    """Two-point lower bound: any certificate valid at level 1-gamma on the class that overshoots by less than 2 eps with
    probability >= 1/2 at theta_0 needs TV >= 1/2 - gamma, i.e. N >= ((1-2 gamma) sigma / (dh_per_dS * 2 eps))^2."""
    return ((1 - 2 * gamma) * sigma / (dh_per_dS * 2 * eps)) ** 2


def t_certificate(H, gamma=0.05, tail=0.0):
    X = H.sum(axis=1); N = len(X)
    return float(X.mean() + stats.t.ppf(1 - gamma, N - 1) * X.std(ddof=1) / np.sqrt(N) + tail)


def z_certificate_O1(H, sigma, gamma=0.05, tail=0.0):
    """The Theorem thm:certcost certificate (independent taps, known per-tap sigma)."""
    N, T = H.shape
    return float(H.mean(0).sum() + stats.norm.ppf(1 - gamma) * sigma * np.sqrt(T / N) + tail)


def hotelling_crit(T, N, gamma=0.05):
    if N <= T:
        raise ValueError("Hotelling region needs N > T")
    return T * (N - 1) / (N - T) * stats.f.ppf(1 - gamma, T, N - T)


def hotelling_upper(H, c, gamma=0.05, tail=0.0):
    """Simultaneous upper bound for the linear functional c'm (valid for all c at once)."""
    N, T = H.shape
    hb = H.mean(0); Sh = np.cov(H, rowvar=False)
    return float(c @ hb + np.sqrt(hotelling_crit(T, N, gamma) * (c @ Sh @ c) / N) + tail)


def simulate_coverage(h_true, N, reps, noise, gamma=0.05, sigma_nominal=None, seed=0):
    """Coverage of the three certificates for the finite-horizon sum S_T = sum h_true under a noise generator
    noise(R, N, T) -> (N, T) array. Returns coverage and mean excess for each."""
    R = np.random.default_rng(seed); T = len(h_true); S = float(np.sum(h_true)); c = np.ones(T)
    cov = {"z_O1": 0, "t": 0, "hotelling": 0}; exc = {k: [] for k in cov}
    for _ in range(reps):
        H = h_true[None, :] + noise(R, N, T)
        b = {"z_O1": z_certificate_O1(H, sigma_nominal, gamma), "t": t_certificate(H, gamma),
             "hotelling": hotelling_upper(H, c, gamma) if N > T else np.nan}
        for k, v in b.items():
            if np.isfinite(v):
                cov[k] += v >= S; exc[k].append(v - S)
    return {k: {"coverage": cov[k] / reps if exc[k] else None, "mean_excess": float(np.mean(exc[k])) if exc[k] else None}
            for k in cov}


def noise_iid(sigma):
    return lambda R, N, T: sigma * R.standard_normal((N, T))


def noise_ar_taps(sigma, phi):
    """Within-episode AR(1) correlation across taps (stationary marginal sd sigma)."""
    def g(R, N, T):
        e = R.standard_normal((N, T)); x = np.empty((N, T)); x[:, 0] = e[:, 0]
        for t in range(1, T):
            x[:, t] = phi * x[:, t - 1] + np.sqrt(1 - phi ** 2) * e[:, t]
        return sigma * x
    return g


def noise_heavy(sigma, df=3):
    sc = np.sqrt((df - 2) / df)
    return lambda R, N, T: sigma * sc * R.standard_t(df, (N, T))


def noise_dependent_episodes(sigma, phi_tap, phi_ep):
    """Episodes themselves AR(1)-dependent (violates independence across experiments)."""
    base = noise_ar_taps(sigma, phi_tap)
    def g(R, N, T):
        x = base(R, N, T); y = np.empty_like(x); y[0] = x[0]
        for e in range(1, N):
            y[e] = phi_ep * y[e - 1] + np.sqrt(1 - phi_ep ** 2) * x[e]
        return y
    return g


def run_sample_complexity():
    """Test T03 (Table tab:certvsid): identifying the cohorts versus certifying the risk."""
    # Paper 1 two-cohort family (q = 0.2, etabar = 0.4, tau = 0.01, a = 0.5, kappa = 0.8, sigma_h = 1.6e-3 per tap)
    a3, k3, q3, eb, tau, sg = 0.5, 0.8, 0.20, 0.40, 0.01, 1.6e-3
    pm, pp = 0.5 - tau / q3, 0.5 + tau / q3
    rows3 = []
    for De in [0.30, 0.20, 0.14, 0.10, 0.08, 0.06, 0.05, 0.04]:
        th0 = ([q3 * pm, q3 * pp], [eb - pp * De, eb + pm * De]); th1 = ([q3 * pp, q3 * pm], [eb - pm * De, eb + pp * De])
        h0, h1 = impulse(a3, k3, *th0, 121), impulse(a3, k3, *th1, 121)
        N_id = 4 * sg ** 2 * norm.ppf(0.95) ** 2 / np.sum((h1 - h0) ** 2)
        S0 = summed_response(a3, k3, q3)
        eps = 0.01 * S0                                    # certify S to within 1%
        rmax = max(1 - np.array(th0[1] + th1[1])); sbar = a3 + k3 * q3 + 0.02
        N_cert, Tc = N_sufficient(eps, sg, k3, rmax, sbar)
        rows3.append({"Delta_eta": De, "N_identify_weights_LeCam": N_id, "N_certify_S_1pct_sufficient": N_cert, "T": Tc,
                      "S_theta0": S0, "S_theta1": summed_response(a3, k3, sum(th1[0])), "S_equal": abs(S0 - summed_response(a3, k3, sum(th1[0]))) < 1e-12})
    lD = np.log([r["Delta_eta"] for r in rows3])
    out = {"rows": rows3,
                                  "slope_identify": float(np.polyfit(lD, np.log([r["N_identify_weights_LeCam"] for r in rows3]), 1)[0]),
                                  "slope_certify": float(np.polyfit(lD, np.log([r["N_certify_S_1pct_sufficient"] for r in rows3]), 1)[0])}
    # lower bound constant for certification: single cohort, perturb q
    qq, et = 0.2, 0.4; dq = 1e-6
    hq0, hq1 = impulse(a3, k3, [qq], [et], 400), impulse(a3, k3, [qq + dq], [et], 400)
    dS = summed_response(a3, k3, qq + dq) - summed_response(a3, k3, qq)
    C_lb = np.linalg.norm(hq1 - hq0) / dS
    eps_grid = [0.1, 0.03, 0.01, 0.003]
    out["cert_rates"] = [{"eps": e, "N_lower": lower_bound_N(e, sg, C_lb), "N_upper": N_sufficient(e, sg, k3, 1 - et, a3 + k3 * qq + 0.02)[0]}
                                                for e in eps_grid]
    out["cert_slope_upper_in_eps"] = float(np.polyfit(np.log(eps_grid), np.log([x["N_upper"] for x in out["cert_rates"]]), 1)[0])

    return out


def run_unknown_covariance_coverage():
    """D8 / E03: coverage of the O1 z-certificate, the O1' t-certificate and the Hotelling projection when taps are
    correlated, noise is heavy-tailed, or episodes are dependent (misspecification)."""
    a, k, q, eta = 0.5, 0.8, 0.2, 0.4
    h = np.zeros(12); x = 0.0; y = 0.0
    for t in range(12):
        tot = (1 if t == 0 else 0) + y; x = a * x + k * tot if t else k; h[t] = x; y = (1 - eta) * y + eta * q * x
    sig = 0.05; rows = []
    for name, gen in [("iid_taps", noise_iid(sig)), ("correlated_taps_ar0.8", noise_ar_taps(sig, 0.8)), ("heavy_tails_t3", noise_heavy(sig)),
                      ("dependent_episodes_ar0.5", noise_dependent_episodes(sig, 0.8, 0.5))]:
        for N in [20, 60, 200]:
            r = simulate_coverage(h, N, 2000, gen, sigma_nominal=sig, seed=N)
            rows.append({"noise": name, "N": N, **{f"{k_}_coverage": v["coverage"] for k_, v in r.items()},
                         **{f"{k_}_mean_excess": v["mean_excess"] for k_, v in r.items()}})
    ok = all(r["t_coverage"] >= 0.93 for r in rows if r["noise"] in ("iid_taps", "correlated_taps_ar0.8", "heavy_tails_t3"))
    return {"T": 12, "S_T": float(h.sum()), "nominal": 0.95, "rows": rows, "pass": bool(ok),
            "note": "t-certificate exact under O1' (any tap covariance); the O1 z-certificate undercovers with correlated taps; "
                    "dependence across episodes breaks both, which is why observational data get only a diagnostic"}
