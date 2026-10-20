# ============================================================================
# CELL R3 — WHY DID BYBIT DIFFER? MINUTE-BAR DIAGNOSTICS (post hoc; cached Part 7 and Part 4 minute bars)
# Same coins, same days (10th and 24th of each month, 2023-2024): Bybit bars built from last trades (Part 7) vs Binance
# kline closes (Part 4). Bid-ask bounce shows up as negative first-order autocorrelation of one-minute returns and as
# zero-return or no-trade minutes.
# ============================================================================
BYB = os.path.join(BASE, "data_bybit", "minute")
coins = sorted(d for d in os.listdir(BYB)) if os.path.isdir(BYB) else []
r3 = {}
for s in coins:
    st = {"bybit": [], "binance": []}
    for d in [x for x in panel_dates() if x <= TRAIN_END]:
        fb = os.path.join(BYB, s, f"{d}.parquet"); fn = os.path.join(XDATA, "minute", s, f"{d}.parquet")
        if not (os.path.exists(fb) and os.path.exists(fn)):
            continue
        for venue, fp in (("bybit", fb), ("binance", fn)):
            B = pd.read_parquet(fp); p = np.log(B["close"].to_numpy(float)); r = np.diff(p); v = B["vol"].to_numpy(float)
            ok = np.isfinite(r)
            if ok.sum() < 500 or np.std(r[ok]) == 0:
                continue
            st[venue].append({"ac1": float(np.corrcoef(r[ok][1:], r[ok][:-1])[0, 1]), "zero_ret": float(np.mean(r[ok] == 0)),
                              "no_volume": float(np.mean(v <= 0)), "rv_bp": float(np.std(r[ok]) * 1e4)})
    if st["bybit"] and st["binance"]:
        r3[s] = {vn: {k: float(np.median([x[k] for x in L])) for k in ("ac1", "zero_ret", "no_volume", "rv_bp")} | {"days": len(L)}
                 for vn, L in st.items()}
summ = {vn: {k: float(np.median([r3[s][vn][k] for s in r3])) for k in ("ac1", "zero_ret", "no_volume", "rv_bp")} for vn in ("bybit", "binance")}
print(pd.DataFrame({s: {f"{vn}_{k}": r3[s][vn][k] for vn in ("bybit", "binance") for k in ("ac1", "zero_ret", "no_volume")} for s in r3}).T.round(3).to_string())
print("medians across coins:", json.dumps(summ, indent=1))
record("R3_bybit_bar_diagnostics", None, "real-data", {"by_coin": r3, "median_across_coins": summ, "coins": len(r3)},
       note="post hoc; same coins and days on both venues")
