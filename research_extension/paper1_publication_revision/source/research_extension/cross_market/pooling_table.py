"""Worst-case years of daily prices: one market (Gauss/Radau pair) vs two markets with participation diversity div,
at memory spacing d around 0.9 (Table 1 parameters). Same constraints as pooling_worstcase.py."""
import json
import numpy as np
from scipy.optimize import minimize
import pooling_calibration as pc
from fragility_scan import rules


def worst(d, div, restarts=12):
    def unpack(x):
        sA = np.tanh(x[0:2]); sB = np.tanh(x[2:4]); a1 = 1 / (1 + np.exp(-x[4])); a2 = 1 / (1 + np.exp(-x[5]))
        WA = np.array([[a1, 1 - a1], [a2, 1 - a2]])
        WB = np.array([np.linalg.solve(np.array([[1, 1], sB]), [w.sum(), w @ sA]) for w in WA])
        return sA, sB, WA, WB
    def obj(x):
        sA, sB, WA, WB = unpack(x)
        if not np.all(np.isfinite(WB)):
            return 1e6
        pen = 1e3 * (max(0, 0.25 - abs(WA[0].max() - WB[0].max())) + max(0, div - abs(WA[0, 0] - WA[1, 0]))
                     + np.sum(np.maximum(0, 0.2 - WB)) + np.sum(np.maximum(0, 0.2 - WA))
                     + max(0, 1.0 - abs(sA[0] - sA[1])) + max(0, 1.0 - abs(sB[0] - sB[1]))
                     + max(0, 0.1 - np.min(np.abs(sA[:, None] - sB[None, :]))))
        if pen > 0:
            return 50 + pen
        kl = sum(pc.kl_rate(pc.RC + d * sA, pc.WTOT * WA[j], pc.RC + d * sB, pc.WTOT * WB[j], n=60001) for j in range(2))
        return np.log(max(kl, 1e-300))
    rng = np.random.default_rng(1); best = None
    for _ in range(restarts):
        r = minimize(obj, rng.normal(0, 1, 6), method="Nelder-Mead", options={"maxiter": 500})
        if best is None or r.fun < best.fun:
            best = r
    sA, sB, WA, WB = unpack(best.x)
    kl = sum(pc.kl_rate(pc.RC + d * sA, pc.WTOT * WA[j], pc.RC + d * sB, pc.WTOT * WB[j]) for j in range(2))
    return pc.years(kl)


rows = []
(xg, wg), (xr, wr) = rules(2)
for d in (0.025, 0.0125):
    one = pc.years(pc.kl_rate(pc.RC + d * xg, pc.WTOT * wg, pc.RC + d * xr, pc.WTOT * wr))
    for div in (0.2, 0.5):
        two = worst(d, div)
        rows.append({"d": d, "diversity": div, "years_one_market": one, "years_two_markets": two, "ratio": one / two})
        print(f"d={d} diversity={div}: one market {one:.3g} years, two markets {two:.3g} years, ratio {one / two:.3g}", flush=True)
json.dump(rows, open("pooling_table_results.json", "w"), indent=1)
