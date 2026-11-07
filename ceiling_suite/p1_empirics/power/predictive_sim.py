"""Power of a pooled out-of-sample predictive test: does yesterday's market-reference basis x_t improve the forecast
of the next-day class flow u~_{t+1} beyond the flow's own two lags?

Per stock: fit OLS on the first T_fit days, evaluate one-step forecasts on the next T_eval days.
Loss differential d_s = MSE(own lags only) - MSE(own lags + x_t, x_{t-1}), relative to Var(u~) on the fit sample.
Pooled statistic over N stocks: mean(d) / (sd(d)/sqrt(N)) (independent stocks; the empirical spec uses a
date-block bootstrap instead). Null: w = 0 (no price feedback into the class flow).
"""
import json, sys
import numpy as np
from power_sim import simulate

def gain(x, u, T_fit):
    y = u[2:]; L1 = u[1:-1]; L2 = u[:-2]; X1 = x[1:-1]; X0 = x[:-2]
    A = np.column_stack([np.ones_like(y), L1, L2]); B = np.column_stack([A, X1, X0])
    f = slice(0, T_fit - 2); e = slice(T_fit - 2, None)
    def mse(M):
        b = np.linalg.lstsq(M[f], y[f], rcond=None)[0]; return np.mean((y[e] - M[e] @ b) ** 2)
    return (mse(A) - mse(B)) / np.var(y[f])

def main(reps=300, N=300):
    out = []
    for w in [0.0, 0.05, 0.1, 0.3]:
        for (T_fit, T_eval) in [(500, 250), (750, 500), (1000, 750), (1250, 1000)]:
            rng = np.random.default_rng([11, int(w * 100), T_fit])
            d = np.array([gain(*simulate(T_fit + T_eval, rng, "null", w=w, noise=0.5), T_fit) for _ in range(reps)])
            prng = np.random.default_rng(T_fit)
            idx = prng.integers(0, reps, size=(2000, N)); m = d[idx].mean(1); s = d[idx].std(1, ddof=1)
            z = m / (s / np.sqrt(N))
            rec = {"w": w, "T_fit": T_fit, "T_eval": T_eval, "mean_gain": float(d.mean()),
                   "share_positive": float((d > 0).mean()), "pooled_power_one_sided_5pct": float((z > 1.645).mean()),
                   "pooled_size_or_power_two_sided": float((np.abs(z) > 1.96).mean())}
            out.append(rec); print(json.dumps(rec), flush=True)
    json.dump(out, open("predictive_results.json", "w"), indent=1)

if __name__ == "__main__":
    main(int(sys.argv[1]) if len(sys.argv) > 1 else 300)
