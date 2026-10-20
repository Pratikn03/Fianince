# ============================================================================
# CELL R4 — (B) MORE GUARD BASELINES ON THE PART 15 AND PART 16 GUARD SAMPLES (post hoc). About 10-20 minutes.
# ============================================================================
BLOCK_MIN = 60
def window_stats(s, e, fs):
    """Certified point operator from the three days before e (Part 15 definition) -> peak and summed response; and the
    margin-style scanning range (99th percentile of |60-minute return| over the same three days)."""
    days = [e[:8] + f"{d:02d}" for d in (12, 13, 14)]
    blocks, moves = [], []
    for d in days:
        df, ok_ = minute(s, d)
        if not ok_:
            continue
        p, u, dd_, x, _ = prep(df, fs[s])
        for b0 in range(0, len(p) - BLOCK_MIN + 1, BLOCK_MIN):
            blocks.append(tuple(v[b0:b0 + BLOCK_MIN] for v in (p, u, dd_, x)))
        moves.append(np.abs(p[60:] - p[:-60]))
    if len(blocks) < 2 * (1440 // BLOCK_MIN):                      # at least two valid days, as in Part 15
        return None
    cat = [np.concatenate(sum(([b[k], [np.nan]] for b in blocks), [])) for k in range(4)]
    est = fit_t6(*cat)
    if est is None:
        return None
    imp = impulse_t6(est["a"], est["phi"], est["kappa"], est["r"], est["eps"], est["eta"], est["q"], L=H_GUARD)
    if not (np.all(np.isfinite(imp)) and abs(imp[0]) > 1e-12):
        return None
    mv = np.concatenate(moves); mv = mv[np.isfinite(mv)]
    return {"S60_check": float(np.sum(np.abs(imp))), "P60_cert": float(np.max(np.abs(imp))), "SCAN": float(np.quantile(mv, 0.99))}

def add_cols(G, fs):
    G = G.copy()
    for c in ["S60_check", "P60_cert", "SCAN", "V6"]:
        G[c] = np.nan
    for (s, e), idx in G.groupby(["symbol", "date"]).groups.items():
        w = window_stats(s, e, fs)
        if w is not None:
            for c, v in w.items():
                G.loc[idx, c] = v
        df, _ = minute(s, e)
        if df is not None:
            vol = df["vol"].to_numpy()
            for i in idx:
                t = int(G.at[i, "hour"]) * 60; G.at[i, "V6"] = float(np.nansum(vol[t - 360:t]))
    return G

def guard_eval(G, base_filter, ref_published, seed):
    D = G.dropna(subset=base_filter).copy()
    D = D[(D["rv_360"] > 0) & (D["U_cert"] > 0) & (D["S60_cert"] > 0)]
    n_base = len(D)
    D = D.dropna(subset=["P60_cert", "SCAN", "V6", "U6", "P60"])
    D = D[(D["P60_cert"] > 0) & (D["SCAN"] > 0) & (D["V6"] > 0) & (D["U6"] > 0) & (D["P60"] > 0)]
    tr = D["split"] == "train"
    X = {"robust_guard": D["U_cert"] * D["S60_up"], "peak_cert": D["U_cert"] * D["P60_cert"], "peak_6h": D["U6"] * D["P60"],
         "participation": 1.0 / D["V6"], "margin_scan": D["SCAN"]}
    RAW = {"static": pd.Series(1.0, index=D.index)}
    for r, v in X.items():
        lo, hi = v[tr].quantile([0.01, 0.99]); v = v.clip(lo, hi)
        k = v[tr].groupby(D.loc[tr, "symbol"]).median(); RAW[r] = np.minimum(1.0, D["symbol"].map(k) / v)
    Q = {r: raw / D["symbol"].map(raw[tr].groupby(D.loc[tr, "symbol"]).mean()) for r, raw in RAW.items()}
    T = D[~tr].sort_values(["date", "symbol", "hour"]); dd = T["date"].to_numpy(); ud = np.unique(dd)
    pos = {d: np.where(dd == d)[0] for d in ud}; y = T["MAE_60"].to_numpy(); QT = {r: Q[r].loc[T.index].to_numpy() for r in Q}
    tlr = lambda r, idx: es95(QT[r][idx] * y[idx]) / QT[r][idx].mean()
    ALL = np.arange(len(T))
    point = {r: {"TLR": tlr(r, ALL), "activity_retained": float(RAW[r].loc[T.index].mean())} for r in RAW}
    others = ["peak_cert", "peak_6h", "participation", "margin_scan", "static"]
    Rb = rng(seed); bs = {o: [] for o in others}
    for _ in range(2000):
        idx = np.concatenate([pos[d] for d in Rb.choice(ud, len(ud))])
        for o in others:
            bs[o].append(np.log(tlr("robust_guard", idx)) - np.log(tlr(o, idx)))
    cmp = {f"robust_guard vs {o}": {"log_TLR_diff": float(np.log(point["robust_guard"]["TLR"]) - np.log(point[o]["TLR"])),
                                    "ci95": [float(np.quantile(v, .025)), float(np.quantile(v, .975))],
                                    "p_one_sided": float(np.mean(np.array(v) >= 0))} for o, v in bs.items()}
    hp = holm({k: v["p_one_sided"] for k, v in cmp.items() if not k.endswith("static")})
    for k in hp:
        cmp[k]["holm_p"] = hp[k]
    return {"n_rows_published_filter": n_base, "n_rows_used": len(D), "n_test_hours": len(T), "n_test_dates": len(ud),
            "rules": point, "comparisons": cmp, "published_reference": ref_published}

def holm(pd_):
    items = sorted((v, k) for k, v in pd_.items()); out, run = {}, 0.0
    for j, (p_, k) in enumerate(items):
        run = max(run, min(1.0, p_ * (len(items) - j))); out[k] = run
    return out

GRD = {}
for name, G0, fs, filt, ref, sd in [
        ("part15", GB15, FS15, ["MAE_60", "rv_360", "U_cert", "S60_cert", "S60_up", "rho_cert", "depth1"],
         {"static_TLR": 377, "robust_TLR": 347}, 1801),
        ("part16", GB16, FS16, ["MAE_60", "rv_360", "U_cert", "S60_cert", "S60_up"], {"static_TLR": 466, "robust_TLR": 360}, 1802)]:
    t_ = time.time(); G = add_cols(G0, fs)
    chk = G[["S60_cert", "S60_check"]].dropna()
    match = float(np.mean(np.abs(chk["S60_cert"] - chk["S60_check"]) <= 1e-6 * (1 + chk["S60_cert"].abs()))) if len(chk) else np.nan
    res = guard_eval(G, filt, ref, sd); res["certified_operator_match_share"] = match; GRD[name] = res
    print(f"\n{name}: rows {res['n_rows_used']} of {res['n_rows_published_filter']} | operator recompute match {match:.4f} | {time.time()-t_:.0f}s")
    for r, v in res["rules"].items():
        print(f"   {r:14s} TLR {v['TLR']:7.1f}  activity {v['activity_retained']:.3f}")
    for k, v in res["comparisons"].items():
        print(f"   {k:32s} {v['log_TLR_diff']:+.3f} {np.round(v['ci95'], 3)}  p {v['p_one_sided']:.4f}" + (f"  Holm {v['holm_p']:.4f}" if "holm_p" in v else ""))
record("R4_guard_baselines", None, "real-data", {"plan_sha256": P18_HASH, "results": GRD},
       note="post hoc: guard samples opened by Parts 15 and 16")
