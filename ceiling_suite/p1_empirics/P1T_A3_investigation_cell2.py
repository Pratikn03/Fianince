# P1T: second look at the stocks whose reverse-causality loss explodes (validation period only, exploratory).
# Run in the SAME Colab session (reuses ex, prep, P, dev, val). Never requests or reads holdout data.
import numpy as np, json, zipfile
classes = ("Foreign", "Trust", "DealerOwn", "Residual", "Hedge")
xr, usr = ex.residual_basis(prep, dev)
codes = np.array(P.codes) if hasattr(P, "codes") else None
dates = np.array(P.dates)
out = []
for i in [902, 460, 731, 45, 536, 662, 435, 355]:
    x = prep["x"][i]; T = len(x)
    cols = [np.ones(T), np.r_[np.nan, x[:-1]]]
    for c in classes:
        u = prep["u"][c][i]; cols += [u, np.r_[np.nan, u[:-1]]]
    Xm = np.column_stack(cols); ok = np.isfinite(Xm).all(1) & np.isfinite(x); fit = ok & dev
    b = np.linalg.lstsq(Xm[fit], x[fit], rcond=None)[0]
    names = ["const", "x_lag"] + [f"{c}{s}" for c in classes for s in ("", "_lag")]
    ev = ok & val
    contrib = np.abs(Xm[ev] * b).max(0)                      # largest |regressor * coefficient| in evaluation
    j = int(np.argmax(np.abs(xr[i][ev])))
    tj = np.where(ev)[0][j]
    rec = {"i": i, "code": str(codes[i]) if codes is not None else None,
           "x_sd_fit": float(np.nanstd(x[fit])), "x_sd_eval": float(np.nanstd(x[ev])),
           "flow_sd_fit": {c: float(np.nanstd(prep["u"][c][i][fit])) for c in classes},
           "flow_sd_eval": {c: float(np.nanstd(prep["u"][c][i][ev])) for c in classes},
           "coef": {n: float(v) for n, v in zip(names, b)},
           "max_eval_contribution": {n: float(v) for n, v in zip(names, contrib)},
           "worst_eval_day": str(dates[tj]), "xr_on_worst_day": float(xr[i][tj]), "x_on_worst_day": float(x[tj]),
           "flows_on_worst_day": {c: float(prep["u"][c][i][tj]) for c in classes}}
    ell0, _ = ex.stock_losses(prep["u"]["Foreign"][i], x, prep["limit"][i], prep["usable"][i], dev, val)
    rec["d_primary"] = float(np.nanmean(ell0)) if np.isfinite(ell0).any() else None
    out.append(rec)
json.dump(out, open("p1t_A3_investigation2_validation.json", "w"), indent=1)
with zipfile.ZipFile("p1t_A3_investigation2_validation.zip", "w", zipfile.ZIP_DEFLATED) as z:
    z.write("p1t_A3_investigation2_validation.json")
for r in out:
    print(r["i"], r["code"], "x sd fit/eval", round(r["x_sd_fit"], 4), round(r["x_sd_eval"], 4), "d_primary", r["d_primary"],
          "worst day", r["worst_eval_day"], "xr", round(r["xr_on_worst_day"], 3))
try:
    from google.colab import files; files.download("p1t_A3_investigation2_validation.zip")
except Exception:
    print("saved p1t_A3_investigation2_validation.zip")
