"""Paper 2: translate the thin-book forecasting effect into liquidation probabilities and dollars.

Input: Part 12 result E1_economic_size.json (Part 9 test set, 13,734 symbol-hours): mean and median next-hour
adverse excursion (MAE, bp) by C3-hat quintile, the share of hours beyond the training 95th percentile by quintile,
and the within-volatility-quintile top-minus-bottom difference (25.6 bp, 95% CI [18.6, 32.8]).

Method (illustrative, post hoc; no new data):
 1. Fit a lognormal to each quintile from its mean and median: mu = ln(median), sigma^2 = 2 ln(mean/median).
 2. Validate: choose the single threshold T at which the count-weighted mixture reproduces the observed pooled
    share of test hours beyond the training 95th percentile, then compare predicted and observed shares by quintile.
 3. Translate: baseline = bottom-quintile distribution; alternative = the same shape scaled so that its mean is
    25.6 bp higher (the effect at a given volatility forecast; also the CI ends). A position at leverage L with
    maintenance-margin rate mm is liquidated when the adverse move exceeds 1/L - mm. Expected hourly loss of
    margin per $1M notional = P(liquidation) * $1M / L (whole margin lost; fees and partial liquidation ignored).
Output: recomputed/R_P2_dollar_translation.json
"""
import json, os, math
import numpy as np
from scipy import stats, optimize

HERE = os.path.dirname(os.path.abspath(__file__))
_CANDS = [os.environ.get("E1_JSON", ""),
          os.path.join(HERE, "..", "p12res", "results", "E1_economic_size.json"),            # replication archive
          os.path.join(HERE, "..", "outputs", "p12res", "results", "E1_economic_size.json"),
          os.path.join(HERE, "results", "E1_economic_size.json")]                            # Part 12 Drive folder
E1 = next(p for p in _CANDS if p and os.path.exists(p))
OUT = os.path.join(HERE, "recomputed", "R_P2_dollar_translation.json")
m = json.load(open(E1))["metrics"]
Q = [str(i) for i in range(5)]
mean = np.array([m["MAE_bps_by_C3_quintile"]["mean"][q] for q in Q])
med = np.array([m["MAE_bps_by_C3_quintile"]["median"][q] for q in Q])
cnt = np.array([m["MAE_bps_by_C3_quintile"]["count"][q] for q in Q], float)
obs_tail = np.array([m["share_hours_above_train_p95_MAE_by_C3_quintile"][q] for q in Q])
mu = np.log(med)
sig = np.sqrt(2 * np.log(mean / med))

def sf(x, mu_, s_):
    return stats.norm.sf((np.log(x) - mu_) / s_)

# 2. validation
pooled_obs = float((obs_tail * cnt).sum() / cnt.sum())
f = lambda T: float((sf(T, mu, sig) * cnt).sum() / cnt.sum()) - pooled_obs
T = optimize.brentq(f, 50, 5000)
pred_tail = sf(T, mu, sig)

# 3. translation
eff = m["avg_within_vol_top_minus_bottom_bps"]
lo, hi = m["avg_within_vol_ci"]
mm = 0.01
rows = []
for L in [10, 20, 25]:
    thr = (1.0 / L - mm) * 1e4  # bp
    p0 = float(sf(thr, mu[0], sig[0]))
    row = {"leverage": L, "maint_margin": mm, "liq_distance_bp": thr, "p_liq_baseline": p0,
           "loss_per_hour_per_1M_baseline": p0 * 1e6 / L}
    for tag, d in [("point", eff), ("ci_lo", lo), ("ci_hi", hi)]:
        scale = (mean[0] + d) / mean[0]
        p1 = float(sf(thr, mu[0] + math.log(scale), sig[0]))
        row[f"p_liq_{tag}"] = p1
        row[f"ratio_{tag}"] = p1 / p0
        row[f"extra_loss_per_hour_per_1M_{tag}"] = (p1 - p0) * 1e6 / L
    rows.append(row)

out = {"source": "E1_economic_size.json (Part 12)", "lognormal_mu": mu, "lognormal_sigma": sig,
       "validation": {"pooled_obs_share": pooled_obs, "threshold_bp": T, "obs_share_by_quintile": obs_tail,
                      "pred_share_by_quintile": pred_tail,
                      "max_abs_error_pp": float(np.max(np.abs(pred_tail - obs_tail)) * 100)},
       "effect_bp": eff, "effect_ci": [lo, hi], "baseline_mean_bp": float(mean[0]), "rows": rows}
os.makedirs(os.path.dirname(OUT), exist_ok=True)
json.dump(json.loads(json.dumps(out, default=lambda o: o.tolist())), open(OUT, "w"), indent=2)
print(json.dumps(json.loads(json.dumps(out, default=lambda o: o.tolist())), indent=1))
