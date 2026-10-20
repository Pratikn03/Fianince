# ============================================================================
# CELL W5 — CERTIFY EACH SYMBOL-DAY'S OPERATOR, BOOTSTRAP ITS UPPER BOUND, BUILD HOURLY BLOCKS (no outcome is used here)
# About 10-20 minutes (100 bootstrap refits per symbol-day).
# ============================================================================
def _m3(est):
    a, ph, ka, r, ep, et, q = (est[k] for k in ("a", "phi", "kappa", "r", "eps", "eta", "q"))
    return np.array([[a + ka * et * q, ph, ka * (1 - et)], [ep * et * q, 1 - r, ep * (1 - et)], [et * q, 0.0, 1 - et]])

def _s60(est):
    imp = impulse_t6(est["a"], est["phi"], est["kappa"], est["r"], est["eps"], est["eta"], est["q"], L=H_GUARD)
    if not (np.all(np.isfinite(imp)) and abs(imp[0]) > 1e-12):
        return None
    return float(np.sum(np.abs(imp)))

def certify_robust(s, days, seed):
    parts = [d for d in days if (s, d) in OK15]
    if len(parts) < 2:
        return None
    blocks = []                                              # (p, u, d, x) arrays of 60 minutes, never spanning two days
    for d in parts:
        p, u, dd_, x, _ = prep(PANEL[(s, d)], FLOW_SCALE[s])
        for b0 in range(0, len(p) - BLOCK_MIN + 1, BLOCK_MIN):
            blocks.append(tuple(v[b0:b0 + BLOCK_MIN] for v in (p, u, dd_, x)))
    def fit_blocks(idx):
        P, U, Dd, X = ([], [], [], [])
        for i in idx:
            for L_, v in zip((P, U, Dd, X), blocks[i]):
                L_ += [v, [np.nan]]
        return fit_t6(*(np.concatenate(v) for v in (P, U, Dd, X)))
    est = fit_blocks(range(len(blocks)))
    if est is None:
        return None
    S = _s60(est)
    if S is None:
        return None
    R = rng(seed); draws = []
    for _ in range(B_BOOT):
        e_b = fit_blocks(R.integers(0, len(blocks), len(blocks)))
        s_b = _s60(e_b) if e_b is not None else None
        if s_b is not None:
            draws.append(s_b)
    if len(draws) < 0.8 * B_BOOT:
        return None
    au = np.concatenate([np.abs(b[1][np.isfinite(b[1])]) for b in blocks])
    imp0 = impulse_t6(est["a"], est["phi"], est["kappa"], est["r"], est["eps"], est["eta"], est["q"], L=2)[0]
    return {"S60_cert": S, "S60_up": float(np.quantile(draws, Q_UP)), "S60_boot_sd": float(np.std(draws)),
            "GM_cert": S / abs(imp0), "C3_cert": est["C3"], "U_cert": float(np.quantile(au, 0.95)),
            "rho_cert": float(max(abs(np.linalg.eigvals(_m3(est))))), "window_days": len(parts), "n_boot": len(draws)}

rows = []
for i, e in enumerate(EVAL_TR + EVAL_TE):
    for j, s in enumerate(THIN):
        if (s, e) not in OK15:
            continue
        cert = certify_robust(s, WIN[e], seed=1000 * i + j)
        if cert is None:
            continue
        for r in day_blocks9(s, e, FLOW_SCALE[s]):
            r.update(cert); r["depth1"] = float(np.exp(r["log_depth1"])) if np.isfinite(r.get("log_depth1", np.nan)) else np.nan
            rows.append(r)
    if i % 6 == 0:
        print(f"   {i + 1}/{len(EVAL_TR) + len(EVAL_TE)} evaluation days")
WB = pd.DataFrame(rows)
WB["group"] = "thin"
WB["split"] = np.where(WB["date"] <= TRAIN_END, "train", "test")
WB.to_parquet(os.path.join(XDATA, "blocks_p15.parquet"))
print(WB.groupby("split").size())
record("W5_blocks", None, "audit", {"blocks": WB.groupby("split").size().to_dict(),
       "symbol_days": WB.groupby("split")["date"].nunique().to_dict(),
       "median_S60_up_over_cert": float((WB["S60_up"] / WB["S60_cert"]).median()),
       "median_rho_cert": float(WB["rho_cert"].median()), "median_window_days": float(WB["window_days"].median())})
