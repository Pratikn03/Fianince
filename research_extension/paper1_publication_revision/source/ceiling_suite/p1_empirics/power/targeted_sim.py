"""Targeted specification tests of the class-flow equation, per stock and pooled across stocks.

Augmented equation: u~_t = r u~_{t-1} + w x_t + g u~_{t-2} + d x_{t-1} + e_t,
estimated by two-step GMM with instruments (x_{t-1}, ..., x_{t-5}), Newey-West lag 2.
Under the model g = d = 0. Per stock: Wald chi2(2). Pooled across N stocks: the mean of the N per-stock
t-statistics for g and for d, standardized by sqrt(N) (valid when stocks are independent; the empirical spec
replaces this by a date-block bootstrap of the cross-sectional mean).
"""
import json, sys
import numpy as np
from power_sim import simulate

def gmm(x, u, L=5, nw=2):
    T = len(x); s = L
    y = u[s:]
    X = np.column_stack([u[s-1:-1], x[s:], u[s-2:-2], x[s-1:-1]])
    Z = np.column_stack([x[s-k:T-k] for k in range(1, L + 1)])
    n = len(y)
    def est(W):
        A = X.T @ Z @ W @ Z.T @ X; return np.linalg.solve(A, X.T @ Z @ W @ Z.T @ y)
    b1 = est(np.linalg.inv(Z.T @ Z / n))
    g = Z * (y - X @ b1)[:, None]; S = g.T @ g / n
    for l in range(1, nw + 1):
        G = g[l:].T @ g[:-l] / n; S += (1 - l / (nw + 1)) * (G + G.T)
    W = np.linalg.inv(S); b = est(W)
    D = Z.T @ X / n; V = np.linalg.inv(D.T @ W @ D) / n
    return b, V

def main(reps=300, N=300, Ts=(500, 1000, 1500), seed=7):
    out = []
    for scen in ["null", "null_shock", "alt_mix", "alt_trend"]:
        for T in Ts:
            rng = np.random.default_rng([seed, T, ["null", "null_shock", "alt_mix", "alt_trend"].index(scen)])
            # per-stock power from `reps` stocks; pooled power from repeated panels of N stocks drawn from the
            # per-stock t-statistic distribution (independent stocks)
            tg, td, wald = [], [], []
            for _ in range(reps):
                x, u = simulate(T, rng, scen)
                b, V = gmm(x, u)
                tg.append(b[2] / np.sqrt(V[2, 2])); td.append(b[3] / np.sqrt(V[3, 3]))
                bb = b[2:]; VV = V[2:, 2:]; wald.append(float(bb @ np.linalg.solve(VV, bb)))
            tg, td, wald = map(np.array, (tg, td, wald))
            per_stock = float(np.mean(wald > 5.991))
            pool_rng = np.random.default_rng(seed + T)
            P = 2000; idx = pool_rng.integers(0, reps, size=(P, N))
            zg = tg[idx].mean(1) * np.sqrt(N); zd = td[idx].mean(1) * np.sqrt(N)
            # two-sided 5% on each, Bonferroni over the two (2.5% each)
            pooled = float(np.mean((np.abs(zg) > 2.2414) | (np.abs(zd) > 2.2414)))
            rec = {"scenario": scen, "T": T, "per_stock_wald_reject": per_stock, "pooled_reject_N300": pooled,
                   "mean_t_g": float(tg.mean()), "mean_t_d": float(td.mean()), "reps": reps}
            out.append(rec); print(json.dumps(rec), flush=True)
    json.dump(out, open("targeted_results.json", "w"), indent=1)

if __name__ == "__main__":
    main(int(sys.argv[1]) if len(sys.argv) > 1 else 300)
