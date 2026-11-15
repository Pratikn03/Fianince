"""Sizing of the evaluation (holdout) period for the pooled predictive test.

Weak-feedback scenario: structural flow shocks, small reporting noise (exchange tallies), w in {0.02, 0.05, 0.1}.
Cross-sectional dependence is represented conservatively by an effective number of independent stocks N_eff.
"""
import json
import numpy as np
from power_sim import simulate
from predictive_sim import gain

rows = []
for w in [0.0, 0.02, 0.05, 0.1]:
    for T_fit, T_eval in [(750, 250), (750, 500), (750, 750), (1000, 1000)]:
        rng = np.random.default_rng([31, int(w * 1000), T_eval])
        d = np.array([gain(*simulate(T_fit + T_eval, rng, "null_shock", w=w, noise=0.1, kappa=-0.6), T_fit)
                      for _ in range(300)])
        mu, sd = d.mean(), d.std(ddof=1)
        rec = {"w": w, "T_fit": T_fit, "T_eval": T_eval, "mean_gain": float(mu), "sd_gain": float(sd)}
        for N_eff in [20, 50, 300]:
            prng = np.random.default_rng(N_eff + T_eval)
            idx = prng.integers(0, len(d), size=(4000, N_eff))
            z = d[idx].mean(1) / (d[idx].std(1, ddof=1) / np.sqrt(N_eff))
            rec[f"power_Neff{N_eff}"] = float((z > 1.645).mean())
        rows.append(rec); print(json.dumps(rec), flush=True)
json.dump(rows, open("sizing_results.json", "w"), indent=1)
