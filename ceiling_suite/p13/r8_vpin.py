# ============================================================================
# CELL R8 — HEAD-TO-HEAD WITH VPIN (post hoc; Part 9 days, split and baseline)
# VPIN (Easley, Lopez de Prado and O'Hara, 2012): mean absolute buy-sell imbalance over equal-volume buckets. Binance
# klines report taker buy volume, so the imbalance in each bucket is measured, not classified. For each hour we use the
# previous six hours (same window as C3), 50 buckets. We ask (a) does VPIN forecast beyond the Part 9 baseline, and
# (b) does C3 still forecast once VPIN is added to the baseline?
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
UB8 = pd.read_parquet(os.path.join(XDATA, "blocks_p9_30sym.parquet"))
UB8["group"] = UB8["symbol"].map(GROUP); UB8["split"] = np.where(UB8["date"] <= TRAIN_END, "train", "test")
UB8["kappa_sq"] = UB8["kappa_hat"] ** 2
UB8 = winsor_train(UB8, IMPACT + ["rv_15", "rv_day", "ewma_vol", "mae_lag60"])
TH8 = UB8[UB8["group"] == "thin"].copy()
vrows = []
for (s, d) in sorted(set(map(tuple, TH8[["symbol", "date"]].drop_duplicates().to_numpy()))):
    df, st = get_day(s, d)
    if df is None:
        continue
    vol, flow = df["vol"].to_numpy(), df["flow"].to_numpy()
    for hr in range(6, 24):
        t = hr * 60
        vrows.append({"symbol": s, "date": d, "hour": hr, "vpin": vpin_window(vol[t - 360:t], flow[t - 360:t])})
TH8 = TH8.merge(pd.DataFrame(vrows), on=["symbol", "date", "hour"], how="left")
lo, hi = TH8.loc[TH8["split"] == "train", "vpin"].quantile([0.01, 0.99]); TH8["vpin_w"] = TH8["vpin"].clip(lo, hi)
BASE9 = CTRL + IMPACT + VOLBENCH
ev_vpin = evaluate_g(TH8, "MAE_60", "vpin", BASE9)
ev_c3_given_vpin = evaluate_g(TH8, "MAE_60", "C3_hat", BASE9 + ["vpin_w"])
ev_c3 = evaluate_g(TH8, "MAE_60", "C3_hat", BASE9)
sh = lambda v: {k: v.get(k) for k in ["n_test", "delta_r2", "delta_r2_ci", "clark_west_t", "clark_west_p"]}
print("VPIN beyond the Part 9 baseline:", sh(ev_vpin))
print("C3 beyond the Part 9 baseline + VPIN:", sh(ev_c3_given_vpin))
print("C3 beyond the Part 9 baseline (reproduction):", sh(ev_c3))
print("Spearman(C3_hat, VPIN) =", round(float(TH8[["C3_hat", "vpin"]].dropna().corr(method="spearman").iloc[0, 1]), 3))
record("R8_vpin", None, "real-data", {"vpin_beyond_baseline": ev_vpin, "c3_beyond_baseline_plus_vpin": ev_c3_given_vpin,
       "c3_beyond_baseline": ev_c3, "spearman_c3_vpin": float(TH8[["C3_hat", "vpin"]].dropna().corr(method="spearman").iloc[0, 1])},
       note="post hoc; Part 9 thin-book split, already opened")
