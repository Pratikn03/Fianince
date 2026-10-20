# ============================================================================
# CELL R4 — SIMULTANEITY: AN INSTRUMENTED ESTIMATE OF THE AMPLIFICATION MARGIN (post hoc; Part 9 days and split)
# The baseline T6 fit regresses the price change on same-minute flow. Here kappa and the depletion slope are estimated by
# two-stage least squares with last minute's flow as the instrument for this minute's flow, and the resulting C3_iv is
# evaluated out of sample exactly as in Part 9 (same blocks, same baseline, same split).
# ============================================================================
def tsls(y, X, Z):
    ok = np.all(np.isfinite(X), 1) & np.all(np.isfinite(Z), 1) & np.isfinite(y)
    if ok.sum() < X.shape[1] + 30:
        return None, np.nan
    X1 = np.column_stack([np.ones(ok.sum()), X[ok]]); Z1 = np.column_stack([np.ones(ok.sum()), Z[ok]])
    Pz = Z1 @ np.linalg.lstsq(Z1, X1, rcond=None)[0]
    b = np.linalg.lstsq(Pz, y[ok], rcond=None)[0][1:]
    fs = np.corrcoef(X[ok][:, 0], Z[ok][:, 0])[0, 1]
    return b, fs
def fit_t6_iv(p, u, d, x):
    dp = np.diff(p, prepend=np.nan)
    ul = np.r_[np.nan, u[:-1]]
    bp, fs1 = tsls(dp[1:], np.column_stack([u[1:], d[:-1], x[:-1]]), np.column_stack([ul[1:], d[:-1], x[:-1]]))
    bd, fs2 = tsls(d[1:], np.column_stack([u[1:], d[:-1]]), np.column_stack([ul[1:], d[:-1]]))
    bm = ols(u[1:], np.column_stack([u[:-1], x[:-1]]))
    if bp is None or bd is None or bm is None:
        return None
    kappa, phi, a = bp[0], bp[1], 1 + bp[2]; eps, r = bd[0], 1 - bd[1]; eta = 1 - bm[0]
    q = bm[1] / eta if abs(eta) > 1e-6 else np.nan
    return {"C3_iv": phi * eps + kappa ** 2 * eta * q - (1 - a) * kappa, "kappa_iv": kappa, "first_stage_corr": fs1}
UB = pd.read_parquet(os.path.join(XDATA, "blocks_p9_30sym.parquet"))
UB["group"] = UB["symbol"].map(GROUP); UB["split"] = np.where(UB["date"] <= TRAIN_END, "train", "test")
UB["kappa_sq"] = UB["kappa_hat"] ** 2
UB = winsor_train(UB, IMPACT + ["rv_15", "rv_day", "ewma_vol", "mae_lag60"])     # exactly as Part 9 cell U5
TH = UB[UB["group"] == "thin"].copy()
need = sorted(set(map(tuple, TH[["symbol", "date"]].drop_duplicates().to_numpy())))
FS9 = {}
for s in THIN:
    v = []
    for d in [x for x in panel_dates() if x <= TRAIN_END]:
        df, st = get_day(s, d)
        if df is not None:
            v.append(np.nanmedian(np.abs(df["flow"].to_numpy())))
    FS9[s] = float(np.nanmedian(v)) if v and np.nanmedian(v) > 0 else 1.0
ivrows = []
for i, (s, d) in enumerate(need):
    df, st = get_day(s, d)
    if df is None:
        continue
    p, u, dd_, x, tot = prep(df, FS9[s])
    for hr in range(6, 24):
        t = hr * 60; w = slice(t - 360, t)
        e = fit_t6_iv(p[w], u[w], dd_[w], x[w])
        if e is not None:
            ivrows.append({"symbol": s, "date": d, "hour": hr, **e})
    if (i + 1) % 200 == 0:
        print(f"   {i+1}/{len(need)}")
IV = pd.DataFrame(ivrows)
TH = TH.merge(IV, on=["symbol", "date", "hour"], how="left")
BASE9 = CTRL + IMPACT + VOLBENCH
ev_iv = evaluate_g(TH, "MAE_60", "C3_iv", BASE9)
ev_ols = evaluate_g(TH, "MAE_60", "C3_hat", BASE9)
corr = float(TH[["C3_hat", "C3_iv"]].dropna().corr(method="spearman").iloc[0, 1])
sh = lambda v: {k: v.get(k) for k in ["n_test", "delta_r2", "delta_r2_ci", "clark_west_t", "clark_west_p", "coef_candidates_train"]}
print("C3 (OLS, as Part 9):", sh(ev_ols)); print("C3 (IV):", sh(ev_iv)); print("Spearman(C3_hat, C3_iv) =", round(corr, 3),
      "| median first-stage corr(u_t, u_t-1) =", round(float(IV["first_stage_corr"].median()), 3))
record("R4_iv_C3", None, "real-data", {"iv": ev_iv, "ols_reproduction": ev_ols, "spearman_ols_iv": corr,
       "median_first_stage_corr": float(IV["first_stage_corr"].median()), "median_kappa_iv_over_ols": float((TH["kappa_iv"] / TH["kappa_hat"]).median())},
       note="post hoc; Part 9 thin-book split, already opened")
