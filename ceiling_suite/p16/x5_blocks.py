# ============================================================================
# CELL X5 — HOURLY BLOCKS: forecasting blocks with VPIN (Part 9 calendar) and guard blocks with certified and bootstrap
# upper-bound operators (Part 15 definitions). No outcome is used here. About 20-40 minutes.
# ============================================================================
def vpin_window(vol, flow, nb=50):
    v = np.nan_to_num(vol); f = np.nan_to_num(flow); tot = v.sum()
    if tot <= 0:
        return np.nan
    buy = (v + f) / 2; cum = np.cumsum(v); edges = np.linspace(0, tot, nb + 1)
    k = np.clip(np.searchsorted(edges, cum, side="left") - 1, 0, nb - 1)     # bucket of each minute (minute-level granularity)
    imb = np.zeros(nb); vb = np.zeros(nb)
    np.add.at(imb, k, buy - (v - buy)); np.add.at(vb, k, v)
    return float(np.sum(np.abs(imb)) / tot)
def _m3(est):
    a, ph, ka, r, ep, et, q = (est[k] for k in ("a", "phi", "kappa", "r", "eps", "eta", "q"))
    return np.array([[a + ka * et * q, ph, ka * (1 - et)], [ep * et * q, 1 - r, ep * (1 - et)], [et * q, 0.0, 1 - et]])

def _s60(est):
    imp = impulse_t6(est["a"], est["phi"], est["kappa"], est["r"], est["eps"], est["eta"], est["q"], L=H_GUARD)
    if not (np.all(np.isfinite(imp)) and abs(imp[0]) > 1e-12):
        return None
    return float(np.sum(np.abs(imp)))

def certify_robust(s, days, seed):
    parts = [d for d in days if (s, d) in OK16]
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
for s in THIN16:
    for d in FC_TRAIN + FC_TEST:
        if (s, d) not in OK16:
            continue
        df = PANEL[(s, d)]; vol, flow = df["vol"].to_numpy(), df["flow"].to_numpy()
        for r in day_blocks9(s, d, FLOW_SCALE[s]):
            t = r["hour"] * 60; r["vpin"] = vpin_window(vol[t - 360:t], flow[t - 360:t]); rows.append(r)
FB = pd.DataFrame(rows); FB["group"] = "thin"; FB["split"] = np.where(FB["date"] <= TRAIN_END, "train", "test")
FB["kappa_sq"] = FB["kappa_hat"] ** 2
FB.to_parquet(os.path.join(XDATA, "blocks_p16_forecast.parquet"))
rows = []
for i, e in enumerate(EVAL_TR + EVAL_TE):
    for j, s in enumerate(THIN16):
        if (s, e) not in OK16:
            continue
        cert = certify_robust(s, WIN[e], seed=1000 * i + j)
        if cert is None:
            continue
        for r in day_blocks9(s, e, FLOW_SCALE[s]):
            r.update(cert); rows.append(r)
GB = pd.DataFrame(rows); GB["split"] = np.where(GB["date"] <= TRAIN_END, "train", "test")
GB.to_parquet(os.path.join(XDATA, "blocks_p16_guard.parquet"))
print(FB.groupby("split").size(), GB.groupby("split").size())
record("X5_blocks", None, "audit", {"forecast_blocks": FB.groupby("split").size().to_dict(),
       "guard_blocks": GB.groupby("split").size().to_dict(), "median_vpin": float(FB["vpin"].median())})
