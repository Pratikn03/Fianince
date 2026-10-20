"""Monte Carlo coverage, width and abstention of the certificate (Theorem thm:certcost; tests T04 and T09, blueprint E03, E09)."""
import numpy as np
from model_contracts import impulse
from uncertainty_calibration import certificate, T_for
from robust_admission import alpha_star, Phi_from_S
from price_response import imp_t6


def run_coverage():
    rng = np.random.default_rng(4); cov = []
    for (rho, sbar) in [(0.6, 0.7), (0.9, 0.8), (0.97, 0.85)]:
        for N in [20, 200, 2000]:
            for gamma in [0.05, 0.10]:
                miss = 0; widths = []; abst = 0; reps = 1000
                for rep in range(reps):
                    K = rng.integers(1, 4); eta = rng.uniform(1 - rho, 0.95, K); aa = rng.uniform(0.1, 0.6); kk = rng.uniform(0.3, 1.2)
                    Phi_ = rng.uniform(0.05, 1.0) * (sbar - aa) / kk
                    if Phi_ <= 0:
                        continue
                    q = rng.dirichlet(np.ones(K)) * Phi_
                    h = impulse(aa, kk, q, eta, 800); S = h.sum(); sig_ = 0.05 * kk
                    T = T_for(0.05 * S, kk, rho, sbar); T = min(T, 800)
                    hb = h + rng.normal(0, sig_ / np.sqrt(N), 800)
                    Sup = certificate(hb, sig_, N, kk, rho, sbar, T, gamma)
                    miss += Sup < S; widths.append(Sup / S - 1)
                    abst += alpha_star(aa, kk, Phi_from_S(aa, kk, Sup) if Sup > 0 else np.inf, 1.0, 0.2 * (1 - aa) / kk, 1.0) in (None, 0.0)
                cov.append({"rho": rho, "sbar": sbar, "N": N, "gamma": gamma, "coverage": 1 - miss / reps,
                            "median_rel_excess": float(np.median(widths)), "abstain_rate": abst / reps})
    return {"rows": cov, "pass": all(r["coverage"] >= 1 - r["gamma"] - 0.02 for r in cov)}



def run_misspecification():
    rng = np.random.default_rng(9); t9 = {}
    def run_cov(gen, reps=600, N=500, gamma=0.05, rho=0.9, sbar=0.8):
        miss = 0; viol = 0
        for rep in range(reps):
            h, kk, aa = gen()
            S_abs = np.abs(h).sum(); sig_ = 0.05 * kk
            T = min(T_for(0.05 * S_abs, kk, rho, sbar), len(h))
            hb = h + rng.normal(0, sig_ / np.sqrt(N), len(h))
            Sup = certificate(np.abs(hb), sig_, N, kk, rho, sbar, T, gamma)   # sum of |hbar| bounds sum |h| only up to noise
            miss += Sup < S_abs
        return 1 - miss / reps
    def g_ok():
        K = rng.integers(1, 4); eta = rng.uniform(0.1, 0.95, K); aa = rng.uniform(0.1, 0.5); kk = rng.uniform(0.3, 1.2)
        q = rng.dirichlet(np.ones(K)) * rng.uniform(0.05, 1) * (0.8 - aa) / kk
        return impulse(aa, kk, q, eta, 3000), kk, aa
    def g_longmem():          # memory longer than the declared bound (rates up to 0.995 vs declared 0.9)
        K = 2; eta = np.array([rng.uniform(0.005, 0.03), rng.uniform(0.3, 0.9)]); aa = rng.uniform(0.1, 0.5); kk = rng.uniform(0.3, 1.2)
        q = rng.dirichlet(np.ones(K)) * rng.uniform(0.3, 1) * (0.8 - aa) / kk
        return impulse(aa, kk, q, eta, 6000), kk, aa
    def g_signed():           # contrarian cohorts (negative weights)
        K = 2; eta = rng.uniform(0.1, 0.95, K); aa = rng.uniform(0.1, 0.5); kk = rng.uniform(0.3, 1.2)
        q = np.array([rng.uniform(0.05, 0.3), -rng.uniform(0.05, 0.3)]) * (0.8 - aa) / kk
        return impulse(aa, kk, q, eta, 3000), kk, aa
    def g_depth():            # depth channel (Paper 2 three-state book), amplifying
        aa = rng.uniform(0.5, 0.9); kk = 1.0; r = rng.uniform(0.05, 0.3); ph = rng.uniform(0.2, 1); ep = rng.uniform(0, 0.3)
        return imp_t6(aa, ph, kk, r, ep, 0.3, 0.05, L=3000), kk, aa
    def g_drift():            # rates drift: certified on one economy, used on one with 20% more feedback
        h, kk, aa = g_ok(); return h * 1.0, kk, aa
    def g_delay():            # feedback acts with a two-period execution delay
        K = rng.integers(1, 3); eta = rng.uniform(0.1, 0.95, K); aa = rng.uniform(0.1, 0.5); kk = rng.uniform(0.3, 1.2)
        q = rng.dirichlet(np.ones(K)) * rng.uniform(0.05, 1) * (0.8 - aa) / kk
        L = 3000; x = np.zeros(L); y = np.zeros((L, K))
        for t in range(L):
            fb = kk * np.dot(q, y[t - 2]) if t >= 2 else 0.0
            x[t] = (aa * x[t - 1] if t else 0) + fb + (kk if t == 0 else 0)
            y[t] = (1 - eta) * (y[t - 1] if t else 0) + eta * x[t]
        return x, kk, aa
    for name, gen in [("as_assumed", g_ok), ("delayed_feedback", g_delay), ("memory_longer_than_declared", g_longmem), ("contrarian_cohorts", g_signed),
                      ("depth_channel", g_depth)]:
        t9[name] = {"coverage_at_95": run_cov(gen)}
    # nonstationarity: certificate from economy theta, risk under theta' with Phi' = 1.2 Phi
    miss = 0; reps = 600
    for rep in range(reps):
        K = rng.integers(1, 4); eta = rng.uniform(0.1, 0.95, K); aa = rng.uniform(0.1, 0.5); kk = rng.uniform(0.3, 1.2)
        q = rng.dirichlet(np.ones(K)) * rng.uniform(0.05, 0.8) * (0.8 - aa) / kk
        h = impulse(aa, kk, q, eta, 3000); h2 = impulse(aa, kk, 1.2 * q, eta, 3000); sig_ = 0.05 * kk
        T = min(T_for(0.05 * h.sum(), kk, 0.9, 0.8), 3000)
        Sup = certificate(h + rng.normal(0, sig_ / np.sqrt(500), 3000), sig_, 500, kk, 0.9, 0.8, T, 0.05)
        miss += Sup < h2.sum()
    t9["feedback_rises_20pct_after_certification"] = {"coverage_at_95": 1 - miss / reps}
    return t9

