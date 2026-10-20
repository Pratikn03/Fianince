# ============================================================================
# CELL A4 — BLOCKS (four forecast times per day; no outcome is looked at here)
# ============================================================================
TIMES = [120, 180, 240, 300]
def impulse_2s(a, kappa, eta, q, L=60):
    x = np.zeros(L); f = np.zeros(L)
    for t in range(L):
        if t > 0:
            f[t] = (1 - eta) * f[t - 1] + eta * q * x[t - 1]
        x[t] = (a * x[t - 1] if t else 0) + kappa * ((1.0 if t == 0 else 0.0) + f[t])
        if abs(x[t]) > 1e9:
            return np.full(L, np.nan)
    return x
def us_blocks(s, d):
    df = UPAN[(s, d)]; p = np.log(df["close"].to_numpy()) * 1e4; u = df["flow"].to_numpy() / UFS[s]; vol = df["vol"].to_numpy()
    x = p - pd.Series(p).ewm(span=30, adjust=False).mean().to_numpy(); dp = np.diff(p, prepend=np.nan)
    ew = pd.Series(np.nan_to_num(dp) ** 2).ewm(alpha=0.06, adjust=False).mean().to_numpy()
    rows = []
    for t in TIMES:
        w, h, f = slice(t - 120, t), slice(t - 60, t), slice(t, min(t + 61, 390))
        row = {"symbol": s, "date": d, "t": t}
        bp0 = ols(dp[w][1:], np.column_stack([u[w][1:], x[w][:-1]])); bm0 = ols(u[w][1:], np.column_stack([u[w][:-1], x[w][:-1]]))
        if bp0 is not None and bm0 is not None and abs(1 - bm0[0]) > 1e-6:
            k0, a0, e0 = bp0[0], 1 + bp0[1], 1 - bm0[0]; q0 = bm0[1] / e0
            row.update({"C3_flow": k0 ** 2 * e0 * q0 - (1 - a0) * k0, "term_momentum": k0 ** 2 * e0 * q0, "term_reversion": (1 - a0) * k0,
                        "kappa_hat": k0})
            imp = impulse_2s(a0, k0, e0, q0)
            row["S60"] = float(np.sum(np.abs(imp))) if np.all(np.isfinite(imp)) else np.nan
        uu, yy = u[w][1:], dp[w][1:]; okk = np.isfinite(uu) & np.isfinite(yy)
        v60 = np.nansum(vol[h])
        row.update({"rv_60": np.nanstd(np.diff(p[h])), "rv_120": np.nanstd(np.diff(p[w])), "abs_ret_60": abs(p[t - 1] - p[t - 60]),
                    "flow_imb_60": np.nansum(u[h]) / (np.nansum(np.abs(u[h])) + 1e-12), "log_vol_60": np.log1p(v60),
                    "kyle_lam": float(np.polyfit(uu[okk], yy[okk], 1)[0]) if okk.sum() > 60 and np.std(uu[okk]) > 0 else np.nan,
                    "amihud_60": np.log(abs(p[t - 1] - p[t - 60]) / v60 + 1e-9) if v60 > 0 else np.nan,
                    "rv_15": np.nanstd(dp[t - 15:t]), "rv_day": np.nanstd(dp[1:t]), "ewma_vol": float(np.sqrt(ew[t - 1])),
                    "mae_lag60": float(np.nanmax(np.abs(p[t - 60:t] - p[t - 61]))),
                    "MAE_60": float(np.nanmax(np.abs(p[f] - p[t - 1])))})
        for tt in TIMES[1:]:
            row[f"tod_{tt}"] = float(t == tt)
        rows.append(row)
    return rows
OKU = sorted(k for k in UPAN if k[0] in set(IN_THIN + IN_MID))
UBK = pd.DataFrame([r for k in OKU for r in us_blocks(*k)])
UBK["group"] = np.where(UBK["symbol"].isin(IN_THIN), "thin", "mid")
UBK["split"] = np.where(UBK["date"].isin(US_TRAIN), "train", "test")
UBK["kappa_sq"] = UBK["kappa_hat"] ** 2
UCTRL = ["rv_60", "rv_120", "abs_ret_60", "flow_imb_60", "log_vol_60", "kappa_hat", "kappa_sq", "kyle_lam", "amihud_60",
         "rv_15", "rv_day", "ewma_vol", "mae_lag60"] + [f"tod_{tt}" for tt in TIMES[1:]]
UBK = winsor_train(UBK, ["kappa_hat", "kappa_sq", "kyle_lam", "amihud_60", "rv_15", "rv_day", "ewma_vol", "mae_lag60"])
UBK.to_parquet(os.path.join(UDIR, "blocks_p14.parquet"))
print(UBK.groupby(["group", "split"]).size().unstack())
record("A4_us_blocks", None, "audit", {"blocks": UBK.groupby(["group", "split"]).size().unstack().to_dict(),
       "coverage": {c: float(UBK[c].notna().mean()) for c in ["C3_flow", "S60", "ewma_vol"]}})
