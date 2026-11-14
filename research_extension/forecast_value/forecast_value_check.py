"""Forecast value of composition data: exploratory check (14 November 2026).

Conjecture. In the paper's linear market the next price depends on the population only through the kernel, so an
observer who knows the kernel forecasts as well as one who also sees every group's state. Class data can therefore
improve a price forecast only by revealing the current kernel sooner than prices do. If the kernel drifts by at
most v per period, the best price-only forecaster loses at most C (sigma^2 v)^(2/3) in mean squared error, so the
forecast value of composition is zero for a stable population and of order v^(2/3) otherwise, whatever the
spacing of the memories.

Check. Two groups with memories 0.5 and 0.7 (spacing 0.2) or 0.58 and 0.62 (spacing 0.04); their weights follow a
reflected random walk with step v. Forecasters: (O) oracle who sees weights and group states; (P) price-only,
recursive least squares of the next price on 6 lags with the best forgetting factor on a grid. Report the excess
mean squared error of P over O against v.
"""
import json
import numpy as np

def run(v, r=(0.5, 0.7), T=400_000, seed=0, a=0.3, kappa=0.5, L=6):
    rng = np.random.default_rng(seed)
    w = np.array([0.12, 0.12]); r = np.array(r)
    x = np.zeros(T); m = np.zeros(2); fo = np.zeros(T); eps = rng.standard_normal(T)
    for t in range(1, T):
        if v > 0:
            w = np.abs(w + v * rng.standard_normal(2)); w = np.minimum(w, 0.36 - w * 0 ); w = np.clip(w, 0.02, 0.22)
        m = r * m + x[t - 1]                      # group states use prices up to t-1
        fo[t] = a * x[t - 1] + kappa * (w * (1 - r)) @ m   # oracle forecast of x_t
        x[t] = fo[t] + eps[t]
    oracle = np.mean((x[1000:] - fo[1000:]) ** 2)
    best = np.inf
    for lam in (1.0, 0.9999, 0.9997, 0.999, 0.997, 0.99, 0.97):
        P = np.eye(L) * 1e3; b = np.zeros(L); se = 0.0; n = 0
        for t in range(L, T):
            z = x[t - L:t][::-1]
            e = x[t] - b @ z
            if t >= 1000: se += e * e; n += 1
            Pz = P @ z; g = Pz / (lam + z @ Pz); b = b + g * e; P = (P - np.outer(g, Pz)) / lam
        best = min(best, se / n)
    return oracle, best

out = {}
for name, r in (("spacing_0.20", (0.5, 0.7)), ("spacing_0.04", (0.58, 0.62))):
    rows = []
    for v in (0.0, 1e-4, 3e-4, 1e-3, 3e-3):
        o, p = run(v, r)
        rows.append({"v": v, "oracle_mse": o, "price_only_mse": p, "excess": p - o})
    vs = np.array([x["v"] for x in rows[1:]]); ex = np.array([x["excess"] for x in rows[1:]])
    out[name] = {"rows": rows, "slope_excess_in_v": float(np.polyfit(np.log(vs), np.log(ex), 1)[0])}
json.dump(out, open("forecast_value_results.json", "w"), indent=1)
for k, vv in out.items():
    print(k, "slope", round(vv["slope_excess_in_v"], 2))
    for x in vv["rows"]: print("   v=%g  excess MSE=%.5f  (oracle %.4f)" % (x["v"], x["excess"], x["oracle_mse"]))
