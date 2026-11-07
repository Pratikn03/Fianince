"""Simulation validation of the amendment A2 diagnostics, before they are run on data.

Three simulated TWSE panels in the three census schemas (validate_executor.fake_days):
  (a) feedback   w = 0.1  -> primary supportive, reverse-causality check supportive;
  (b) null       w = 0    -> neither supportive;
  (c) confound   w = 0, strong impact (kappa = -1.2) and heavy reporting noise on the Foreign flow (noise SD equal to
      the flow SD), the case in which the power analysis found x_t predicting flow without feedback ->
      the reverse-causality check must not be supportive.
Every diagnostic must run end to end on (a)-(c)."""
import json
import sys
import numpy as np
import validate_executor as v
import p1t_executor as ex

_orig = v.simulate_market


def confound_market(N, T, w, seed, a=0.6, kappa=-1.2, r=0.8, shock=0.5, burn=300):
    logp, mkt, uF, uO, vol = _orig(N, T, 0.0, seed, a=a, kappa=kappa, r=r, shock=shock, burn=burn)
    rng = np.random.default_rng(seed + 999)
    uF = uF + uF.std(axis=1, keepdims=True) * rng.standard_normal(uF.shape)   # reported = true + noise
    return logp, mkt, uF, uO, vol


def run(kind, seed, N=40, T_dev=985, T_eval=490, B=499):
    if kind == "confound":
        v.simulate_market = confound_market
    try:
        days = v.fake_days(N, T_dev + T_eval, 0.1 if kind == "feedback" else 0.0, seed)
    finally:
        v.simulate_market = _orig
    P = ex.build_panel(days)
    T = len(P.dates); dev = np.zeros(T, bool); dev[:T_dev] = True
    # simulated dates: give the evaluation period real calendar years so the stability split runs
    dates = [f"{2013 + t // 245}{(t % 245) // 21 + 1:02d}{t % 21 + 1:02d}" for t in range(T)]
    prep = ex.prepare(P, dev)
    prim = ex.run_period(prep, dev, ~dev, B=B)
    diag = ex.diagnostics(prep, dates, dev, ~dev, B=B)
    return {"primary": prim, "diagnostics": diag}


if __name__ == "__main__":
    reps = int(sys.argv[1]) if len(sys.argv) > 1 else 2
    res = {k: [] for k in ("feedback", "null", "confound")}
    for k in res:
        for j in range(reps):
            out = run(k, 300 + 17 * j + len(k))
            res[k].append(out)
            d = out["diagnostics"]
            print(k, j, "primary", out["primary"]["verdict"], round(out["primary"]["D"], 5),
                  "| RC", d["reverse_causality"]["verdict"], round(d["reverse_causality"]["D"], 5),
                  "| S2 F r med", d["S2"]["Foreign"]["eval"]["r_median"] if "eval" in d["S2"]["Foreign"] else None,
                  "| S3", d["S3"].get("median_ratio_formula_to_bootstrap"), flush=True)
    ok = (all(r["primary"]["verdict"] == "supportive" and r["diagnostics"]["reverse_causality"]["verdict"] == "supportive"
              for r in res["feedback"])
          and all(r["primary"]["verdict"] != "supportive" and r["diagnostics"]["reverse_causality"]["verdict"] != "supportive"
                  for r in res["null"])
          and all(r["diagnostics"]["reverse_causality"]["verdict"] != "supportive" for r in res["confound"]))
    res["passed"] = bool(ok)
    json.dump(res, open("validate_executor_A2_results.json", "w"), indent=1, default=float)
    print("A2 VALIDATION", "PASSED" if ok else "FAILED")
