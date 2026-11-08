# P1T: locating the two suspected defects found by the amendment A2 diagnostics on the validation period.
# Exploratory, validation period only. Run in the SAME Colab session as P1T_Diagnostics_A2_Colab.ipynb
# (it reuses ex, prep, dev, val). It never requests or reads holdout data.
import numpy as np, json, zipfile
classes = ("Foreign", "Trust", "DealerOwn", "Residual", "Hedge")
xr, usr = ex.residual_basis(prep, dev)
rows = []
for i in prep["U"]:
    x = prep["x"][i]; T = len(x)
    cols = [np.ones(T), np.r_[np.nan, x[:-1]]]
    for c in classes:
        u = prep["u"][c][i]; cols += [u, np.r_[np.nan, u[:-1]]]
    Xm = np.column_stack(cols); ok = np.isfinite(Xm).all(1) & np.isfinite(x); fit = ok & dev
    if fit.sum() < 50:
        continue
    sv = np.linalg.svd(Xm[fit], compute_uv=False)
    flow_sum = sum(prep["u"][c][i] for c in ("Foreign", "Trust", "DealerOwn", "Residual", "Hedge"))
    ell, _ = ex.stock_losses(prep["u"]["Foreign"][i], xr[i], prep["limit"][i], usr[i], dev, val)
    rows.append({"i": int(i), "n_fit": int(fit.sum()), "sv_min_over_max": float(sv[-1] / sv[0]),
                 "max_abs_flow_sum_fit": float(np.nanmax(np.abs(flow_sum[fit]))),
                 "max_abs_flow_sum_eval": float(np.nanmax(np.abs(flow_sum[ok & val]))) if (ok & val).any() else None,
                 "var_xr_fit": float(np.nanvar(xr[i][fit])), "var_xr_eval": float(np.nanvar(xr[i][ok & val])),
                 "d_reverse_causality": float(np.nanmean(ell)) if np.isfinite(ell).any() else None})
d = np.array([r["d_reverse_causality"] for r in rows if r["d_reverse_causality"] is not None])
svr = np.array([r["sv_min_over_max"] for r in rows])
summary = {"n_stocks": len(rows), "d_median": float(np.median(d)), "d_mean": float(d.mean()),
           "n_d_below_minus1": int((d < -1).sum()),
           "sv_min_over_max_quantiles_50_90_99_max": [float(q) for q in np.percentile(svr, [50, 90, 99, 100])],
           "share_sv_ratio_below_1e-8": float(np.mean(svr < 1e-8))}
rows.sort(key=lambda r: (r["d_reverse_causality"] if r["d_reverse_causality"] is not None else 0))
rs, rs_ok = [], 0
for i in prep["U"]:
    f = ex.iv_tagged(prep["u"]["Foreign"][i], prep["x"][i], ex._iv_ok(prep, i, "Foreign", dev))
    if f is not None:
        rs.append(float(f["beta"][1]))
rs = np.array(rs)
summary["S3_inputs"] = {"n_stocks_iv": int(len(rs)), "rF_fit_quantiles_5_25_50_75_95": [float(q) for q in np.percentile(rs, [5, 25, 50, 75, 95])],
                        "share_abs_rF_ge_1": float(np.mean(np.abs(rs) >= 1)), "share_abs_rF_gt_30": float(np.mean(np.abs(rs) > 30))}
out = {"label": "P1T A3 investigation, validation period only (exploratory)", "summary": summary, "worst_12_stocks": rows[:12]}
json.dump(out, open("p1t_A3_investigation_validation.json", "w"), indent=1)
with zipfile.ZipFile("p1t_A3_investigation_validation.zip", "w", zipfile.ZIP_DEFLATED) as z:
    z.write("p1t_A3_investigation_validation.json")
print(json.dumps(summary, indent=1))
try:
    from google.colab import files; files.download("p1t_A3_investigation_validation.zip")
except Exception:
    print("saved p1t_A3_investigation_validation.zip")
