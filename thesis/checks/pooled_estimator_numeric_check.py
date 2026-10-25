"""Numerical check of Theorem thm:pooled (Chapter 4): the pooled price-and-flow estimator of the margin has asymptotic
variance proportional to the margin. Simulated economies; not evidence. Writes pooled_estimator_numeric_check.json."""
import json
from pathlib import Path
import numpy as np

rng = np.random.default_rng(20261026)


def economy(rho, groots=(2.0, -3.0), a=0.6, kappa=0.5):
    g = np.poly1d([1.0])
    for z in groots:
        g = g * np.poly1d([-1 / z, 1.0])
    f = g * np.poly1d([-rho, 1.0]); c = np.real(f.coeffs[::-1]); phi = -c[1:]
    k = phi / kappa; k[0] = (phi[0] - a) / kappa
    return a, kappa, k, float(np.real(g(1.0))), float(np.real(f(1.0)))


def pooled_draws(rho, T=20000, R=300, s_w=1.0, s_e=0.5):
    a, kappa, k, g1, M = economy(rho); L = len(k)
    x = np.zeros((R, T + 1)); fl = np.zeros((R, T + 1))
    for t in range(L - 1, T):
        lagx = x[:, t - np.arange(L)]                       # x_t, x_{t-1}, ...
        fl[:, t + 1] = lagx @ k + s_w * rng.normal(size=R)
        x[:, t + 1] = a * x[:, t] + kappa * fl[:, t + 1] + s_e * rng.normal(size=R)
    Mhat = np.empty(R)
    for i in range(R):
        tt = np.arange(L, T)
        Xb = np.column_stack([fl[i, tt + 1], x[i, tt]]); yb = x[i, tt + 1] - x[i, tt]
        kap, beta = np.linalg.lstsq(Xb, yb, rcond=None)[0]
        Xk = np.column_stack([x[i, tt - j] for j in range(L)]); kk = np.linalg.lstsq(Xk, fl[i, tt + 1], rcond=None)[0]
        Mhat[i] = -beta - kap * kk.sum()
    return {"rho": rho, "M": M, "g1": g1, "mean_Mhat": float(Mhat.mean()), "T_var": float(T * Mhat.var()),
            "T_var_over_M": float(T * Mhat.var() / M), "decided_rate": float(np.mean(Mhat - 1.96 * Mhat.std() > 0))}


out = {"s_w": 1.0, "s_eps": 0.5, "kappa": 0.5, "a": 0.6, "g_roots": [2.0, -3.0],
       "runs": [pooled_draws(r) for r in (0.9, 0.97, 0.99)]}
Path(__file__).with_suffix(".json").write_text(json.dumps(out, indent=1) + "\n")
print(json.dumps(out, indent=1))
