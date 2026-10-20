# ============================================================================
# CELL R3 — (A) ORDER-SPLITTING PLACEBO ON BINANCE (post hoc). About 10-30 minutes (minute data come from the Drive cache).
# ============================================================================
SHIFT = 180
def placebo_cols(D, fs):
    D = D.copy(); D["C3_check"] = np.nan; D["C3_placebo"] = np.nan
    for (s, d), idx in D.groupby(["symbol", "date"]).groups.items():
        df, _ = minute(s, d)
        if df is None:
            continue
        p, u, dd_, x, _ = prep(df, fs[s])
        for i in idx:
            t = int(D.at[i, "hour"]) * 60; w = slice(t - 360, t)
            e_r = fit_t6(p[w], u[w], dd_[w], x[w]); e_p = fit_t6(p[w], np.roll(u[w], SHIFT), dd_[w], x[w])
            if e_r is not None:
                D.at[i, "C3_check"] = e_r["C3"]
            if e_p is not None:
                D.at[i, "C3_placebo"] = e_p["C3"]
    return D

def evaluate_set(sub, outcome, cand_sets, ctrl, B=2000, level=0.95, seed=88):
    A0 = sub[sub["split"] == "train"].copy(); B0 = sub[sub["split"] == "test"].copy()
    allc = sorted({c for cs in cand_sets.values() for c in cs})
    for c in allc:
        lo, hi = A0[c].quantile([0.01, 0.99]); A0[c + "_w"] = A0[c].clip(lo, hi); B0[c + "_w"] = B0[c].clip(lo, hi)
    need = ctrl + [c + "_w" for c in allc] + [outcome]
    A = A0.dropna(subset=need); Bt = B0.dropna(subset=need)
    Bt = Bt[Bt["symbol"].isin(set(A["symbol"]))].sort_values(["date", "symbol", "hour"])
    syms = sorted(A["symbol"].unique()); y = Bt[outcome].to_numpy()
    fit = lambda cols: design(Bt, cols, syms) @ np.linalg.lstsq(design(A, cols, syms), A[outcome].to_numpy(), rcond=None)[0]
    fb = fit(ctrl); ff = {k: fit(ctrl + [c + "_w" for c in cs]) for k, cs in cand_sets.items()}
    ybar = A[outcome].mean(); sst = np.sum((y - ybar) ** 2)
    Rb = rng(seed); dd = Bt["date"].to_numpy(); ud = np.unique(dd); pos = {d: np.where(dd == d)[0] for d in ud}
    draws = [np.concatenate([pos[d] for d in Rb.choice(ud, len(ud))]) for _ in range(B)]
    qa = (1 - level) / 2; out = {"n_train": len(A), "n_test": len(Bt), "n_symbols": len(syms), "n_test_dates": len(ud),
                                 "r2_base": float(1 - np.sum((y - fb) ** 2) / sst), "cands": {}, "_boot": {}}
    for k in cand_sets:
        t_, p_ = cw_test(y, fb, ff[k])
        dr = np.array([(np.sum((y[i] - fb[i]) ** 2) - np.sum((y[i] - ff[k][i]) ** 2)) / np.sum((y[i] - ybar) ** 2) for i in draws])
        out["_boot"][k] = dr
        out["cands"][k] = {"delta_r2": float((np.sum((y - fb) ** 2) - np.sum((y - ff[k]) ** 2)) / sst),
                           "delta_r2_ci": [float(np.quantile(dr, qa)), float(np.quantile(dr, 1 - qa))],
                           "clark_west_t": t_, "clark_west_p": p_}
    return out
def paired_diff(ev, a, b, level=0.95):
    d = ev["_boot"][a] - ev["_boot"][b]; qa = (1 - level) / 2
    return {"diff": ev["cands"][a]["delta_r2"] - ev["cands"][b]["delta_r2"],
            "ci": [float(np.quantile(d, qa)), float(np.quantile(d, 1 - qa))], "p_one_sided": float(np.mean(d <= 0))}

PLAC = {}
for name, D0, fs in [("part9_thin", UB9, FS9), ("part16_thin", FB16, FS16)]:
    t_ = time.time(); D = placebo_cols(D0, fs)
    ok_ = D[["C3_hat", "C3_check"]].dropna()
    match = float(np.mean(np.abs(ok_["C3_hat"] - ok_["C3_check"]) <= 1e-6 * (1 + np.abs(ok_["C3_hat"])))) if len(ok_) else np.nan
    ev = evaluate_set(D.dropna(subset=["C3_hat", "C3_placebo"]), "MAE_60", {"real": ["C3_hat"], "placebo": ["C3_placebo"]}, BASE9, seed=181)
    pdf = paired_diff(ev, "real", "placebo")
    PLAC[name] = {"recompute_match_share": match, "eval": {k: v for k, v in ev.items() if k != "_boot"}, "real_minus_placebo": pdf,
                  "spearman_real_placebo": float(D[["C3_hat", "C3_placebo"]].corr(method="spearman").iloc[0, 1])}
    print(f"{name}: recompute match {match:.4f} | real {100*ev['cands']['real']['delta_r2']:+.3f} pts "
          f"{np.round(100*np.array(ev['cands']['real']['delta_r2_ci']), 3)} | placebo {100*ev['cands']['placebo']['delta_r2']:+.3f} "
          f"{np.round(100*np.array(ev['cands']['placebo']['delta_r2_ci']), 3)} | real-placebo {100*pdf['diff']:+.3f} "
          f"{np.round(100*np.array(pdf['ci']), 3)} | {time.time()-t_:.0f}s")
record("R3_placebo_binance", None, "real-data", {"plan_sha256": P18_HASH, "shift_minutes": SHIFT, "results": PLAC},
       note="post hoc: samples opened by Parts 9 and 16")
