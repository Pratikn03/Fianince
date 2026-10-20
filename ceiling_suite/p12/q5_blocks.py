# ============================================================================
# CELL Q5 — CERTIFY EACH SYMBOL-DAY'S OPERATOR AND BUILD HOURLY BLOCKS (no outcome is looked at here)
# ============================================================================
def certify(s, days):
    parts = [d for d in days if (s, d) in OK12]
    if len(parts) < 2:
        return None
    P, U, Dd, X = [], [], [], []
    for d in parts:
        p, u, dd_, x, _ = prep(PANEL[(s, d)], FLOW_SCALE[s])
        for L_, v in ((P, p), (U, u), (Dd, dd_), (X, x)):
            L_ += [v, [np.nan]]                                  # NaN separator: no regression row spans two days
    P, U, Dd, X = (np.concatenate(v) for v in (P, U, Dd, X))
    est = fit_t6(P, U, Dd, X)
    if est is None:
        return None
    imp = impulse_t6(est["a"], est["phi"], est["kappa"], est["r"], est["eps"], est["eta"], est["q"], L=H_GUARD)
    if not (np.all(np.isfinite(imp)) and abs(imp[0]) > 1e-12):
        return None
    S = float(np.sum(np.abs(imp))); au = np.abs(U[np.isfinite(U)])
    return {"S60_cert": S, "GM_cert": S / abs(imp[0]), "C3_cert": est["C3"], "U_cert": float(np.quantile(au, 0.95)),
            "window_days": len(parts)}
rows = []
for i, e in enumerate(EVAL_TR + EVAL_TE):
    for s in THIN:
        if (s, e) not in OK12:
            continue
        cert = certify(s, WIN[e])
        if cert is None:
            continue
        for r in day_blocks9(s, e, FLOW_SCALE[s]):
            r.update(cert); rows.append(r)
QB = pd.DataFrame(rows)
QB["split"] = np.where(QB["date"] <= TRAIN_END, "train", "test")
QB.to_parquet(os.path.join(XDATA, "blocks_p12.parquet"))
print(QB.groupby("split").size())
record("Q5_blocks", None, "audit", {"blocks": QB.groupby("split").size().to_dict(),
       "symbol_days": QB.groupby("split")["date"].nunique().to_dict(),
       "median_GM_cert": float(QB["GM_cert"].median()), "median_window_days": float(QB["window_days"].median())})
