"""Worst-case two-market pair for the calibration: minimize the total information over pairs that (a) match
moments of order 0 and 1 in both markets (the most a two-market pair can match generically), (b) differ in the
largest market-1 weight by at least 0.25, with no shared node, (as the one-market Gauss/Radau pair does), (c) keep every weight at least 0.2 and the two memories of each
population at least 1.0 apart in rescaled units (the Gauss/Radau pair: weights >= 0.25, gaps 1.15 and 1.33), (d) have market
participation patterns that differ by at least 0.2 in the first algorithm's share. Rates in rc +/- d."""
import json
import numpy as np
from scipy.optimize import minimize
import pooling_calibration as _pc
from pooling_calibration import kl_rate, years, RC, D_ETA, WTOT


def unpack(x):
    sA = np.tanh(x[0:2]); sB = np.tanh(x[2:4]); a1 = 1 / (1 + np.exp(-x[4])); a2 = 1 / (1 + np.exp(-x[5]))
    WA = np.array([[a1, 1 - a1], [a2, 1 - a2]])
    WB = np.array([np.linalg.solve(np.array([[1, 1], sB]), [w.sum(), w @ sA]) for w in WA])
    return sA, sB, WA, WB


def objective(x, n=60001):
    sA, sB, WA, WB = unpack(x)
    pen = 0.0
    pen += 1e3 * max(0, 0.25 - abs(WA[0].max() - WB[0].max())) + 1e3 * max(0, 0.2 - abs(WA[0, 0] - WA[1, 0]))
    pen += 1e3 * max(0, 0.1 - np.min(np.abs(sA[:, None] - sB[None, :])))
    pen += 1e3 * np.sum(np.maximum(0, 0.2 - WB)) + 1e3 * np.sum(np.maximum(0, 0.2 - WA)) + 1e3 * max(0, 1.0 - abs(sA[0] - sA[1])) + 1e3 * max(0, 1.0 - abs(sB[0] - sB[1]))
    if not np.all(np.isfinite(WB)) or (WB <= 0).any():
        return 1e3 + pen
    kl = sum(kl_rate(RC + D_ETA * sA, WTOT * WA[j], RC + D_ETA * sB, WTOT * WB[j], n=n) for j in range(2))
    return np.log(kl) + pen


rng = np.random.default_rng(0)
best = None
for k in range(25):
    x0 = rng.normal(0, 1, 6)
    r = minimize(objective, x0, method="Nelder-Mead", options={"maxiter": 600, "xatol": 1e-4, "fatol": 1e-6})
    if best is None or r.fun < best.fun:
        best = r
sA, sB, WA, WB = unpack(best.x)
kls = [kl_rate(RC + D_ETA * sA, WTOT * WA[j], RC + D_ETA * sB, WTOT * WB[j]) for j in range(2)]
res = {"sA": sA.tolist(), "sB": sB.tolist(), "WA": WA.tolist(), "WB": WB.tolist(), "kl": kls,
       "years_two_markets": years(sum(kls)), "constraint_weight_gap": abs(WA[0].max() - WB[0].max()),
       "constraint_diversity": abs(WA[0, 0] - WA[1, 0])}
print(json.dumps(res, indent=1))
json.dump(res, open("pooling_worstcase_results.json", "w"), indent=1)
