"""Amendment A2, case (d): no feedback, Foreign flow with long memory (slow AR 0.98 plus fast AR 0.3 component,
observed exactly), prices impacted by lagged true flow. Two own lags miss the slow component and the price level
proxies for it. The reverse-causality check must remove the gain."""
import json
import sys, numpy as np

import validate_executor as v, p1t_executor as ex
_orig = v.simulate_market
def longmem(N, T, w, seed, a=0.6, kappa=-0.6, burn=300):
    rng = np.random.default_rng(seed); n = T + burn
    mkt = np.cumsum(0.01 * rng.standard_normal(n))
    x = np.zeros((N, n)); s = np.zeros((N, n)); f = np.zeros((N, n)); uO = np.zeros((N, n))
    for t in range(1, n):
        x[:, t] = a * x[:, t-1] + kappa * 0.01 * (s[:, t-1] + f[:, t-1] + uO[:, t-1]) + 0.01 * rng.standard_normal(N)
        s[:, t] = 0.98 * s[:, t-1] + 0.15 * rng.standard_normal(N)
        f[:, t] = 0.3 * f[:, t-1] + 0.5 * rng.standard_normal(N)
        uO[:, t] = 0.5 * uO[:, t-1] + 0.3 * rng.standard_normal(N)
    uF = (s + f)[:, burn:]; x = x[:, burn:]; uO = uO[:, burn:]; mkt = mkt[burn:]
    beta = rng.uniform(0.7, 1.3, N); logp = np.log(50) + beta[:, None] * mkt[None, :] + x
    vol = rng.uniform(5e5, 5e6, N)[:, None] * np.exp(0.2 * rng.standard_normal((N, T)))
    return logp, mkt, uF, uO, vol
res = []
for seed in (1, 2, 3):
    v.simulate_market = longmem
    days = v.fake_days(40, 1475, 0.0, seed); v.simulate_market = _orig
    P = ex.build_panel(days); T = len(P.dates); dev = np.zeros(T, bool); dev[:985] = True
    prep = ex.prepare(P, dev)
    prim = ex.run_period(prep, dev, ~dev, B=499)
    xr, usr = ex.residual_basis(prep, dev)
    rc = ex.summarize_L(ex.panel_L(prep, dev, ~dev, "Foreign", x=xr, usable=usr), B=499)
    res.append({"seed": seed, "primary": prim, "reverse_causality": rc})
    print("long-memory, no feedback, exact flows", seed, "primary", prim["verdict"], round(prim["D"], 5), "| RC", rc["verdict"], round(rc["D"], 5), flush=True)
res = {"runs": res, "passed": all(r["reverse_causality"]["verdict"] != "supportive" for r in res)}
json.dump(res, open("validate_executor_A2_longmemory_results.json", "w"), indent=1, default=float)
print("LONG-MEMORY CASE", "PASSED" if res["passed"] else "FAILED")
