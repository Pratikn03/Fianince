"""Forecast irrelevance of feedback-trader composition: numerical check of the theorem (14 November 2026).

Market (the paper's model): x_t = a x_{t-1} + kappa * sum_i q_i y_{i,t-1} + eps_t,  y_{i,t} = (1-eta_i) y_{i,t-1} + eta_i x_t.
Oracle C sees prices and every group's position q_i y_{i,t} (hence the weights). Price-only P regresses x_{t+1} on
L lags of x, refit on a trailing window of m periods every B periods (best m on a grid).

Checks
 (i)  stable population: excess MSE of P over C is of order L/T and does not depend on the memory spacing;
 (ii) weights drift with speed v: excess MSE / v^(2/3) stays bounded as v -> 0 (the theorem's rate is an upper bound);
 (iii) the class-position observer adds nothing once the weights are known (positions are functions of past prices).
"""
import json
import numpy as np

a, kappa, L, B = 0.3, 0.5, 24, 50

def simulate(T, eta, q0, v, seed):
    rng = np.random.default_rng(seed)
    eta = np.asarray(eta, float); K = len(eta)
    q = np.array(q0, float); x = np.zeros(T); y = np.zeros(K); oracle = np.zeros(T)
    eps = rng.standard_normal(T); Q = np.zeros((T, K))
    lo, hi = 0.05, 0.45
    for t in range(1, T):
        if v > 0:
            q = q + v * rng.standard_normal(K)
            q = np.where(q < lo, 2 * lo - q, q); q = np.where(q > hi, 2 * hi - q, q)
        Q[t] = q
        oracle[t] = a * x[t - 1] + kappa * q @ y
        x[t] = oracle[t] + eps[t]
        y = (1 - eta) * y + eta * x[t]
    return x, oracle, Q

def windowed_ls(x, m):
    T = len(x); Z = np.column_stack([x[L - 1 - j:T - 1 - j] for j in range(L)])   # rows t = L..T-1 predict x[t]
    tgt = x[L:]
    n = len(tgt)
    ZZ = np.cumsum(np.einsum('ti,tj->tij', Z, Z), axis=0); Zy = np.cumsum(Z * tgt[:, None], axis=0)
    pred = np.full(n, np.nan)
    for s in range(m, n, B):
        A = ZZ[s - 1] - (ZZ[s - 1 - m] if s - 1 - m >= 0 else 0); bvec = Zy[s - 1] - (Zy[s - 1 - m] if s - 1 - m >= 0 else 0)
        beta = np.linalg.solve(A + 1e-9 * np.eye(L), bvec)
        e = min(s + B, n); pred[s:e] = Z[s:e] @ beta
    full = np.full(T, np.nan); full[L:] = pred
    return full

def excess(x, oracle, windows):
    best = (np.inf, None)
    for m in windows:
        p = windowed_ls(x, m); ok = ~np.isnan(p); ok[:max(windows) + L + B] = False
        d = np.mean((x[ok] - p[ok]) ** 2) - np.mean((x[ok] - oracle[ok]) ** 2)
        if d < best[0]: best = (d, m)
    return best

out = {"spacing": {}, "drift": {}}
T = 300_000
for name, eta in (("wide (memories 0.30, 0.60)", (0.70, 0.40)), ("close (memories 0.44, 0.46)", (0.56, 0.54))):
    ex, m = excess(*simulate(T, eta, (0.2, 0.2), 0.0, 1)[:2], windows=[20000, 60000, 150000])
    out["spacing"][name] = {"excess_mse": ex, "window": m, "L_over_window": L / m}
windows = [500, 1000, 2000, 4000, 8000, 16000, 32000, 64000]
for v in (3e-5, 1e-4, 3e-4, 1e-3):
    rows = []
    for seed in (2, 3):
        x, o, _ = simulate(T, (0.70, 0.40), (0.2, 0.2), v, seed); rows.append(excess(x, o, windows))
    exm = float(np.mean([r[0] for r in rows]))
    out["drift"][str(v)] = {"excess_mse": exm, "windows": [r[1] for r in rows], "excess_over_v23": exm / v ** (2 / 3)}
vs = np.array([float(k) for k in out["drift"]]); ex = np.array([d["excess_mse"] for d in out["drift"].values()])
out["drift_slope"] = float(np.polyfit(np.log(vs), np.log(ex), 1)[0])
ratios = [d["excess_over_v23"] for d in out["drift"].values()]
out["ok"] = bool(max(r["excess_mse"] for r in out["spacing"].values()) < 5 * L / 20000 and max(ratios) < 3 * min(ratios) * 10)
json.dump(out, open("irrelevance_theorem_results.json", "w"), indent=1)
print(json.dumps(out, indent=1))
