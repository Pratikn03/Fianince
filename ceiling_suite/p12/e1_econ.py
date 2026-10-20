# ============================================================================
# CELL E1 — ECONOMIC SIZE OF THE PART 9 RESULT (descriptive; uses the Part 9 blocks already in Drive, no new test)
# ============================================================================
BLK9 = os.path.join(XDATA, "blocks_p9_30sym.parquet")
assert os.path.exists(BLK9), "Part 9 blocks not found in Drive (data_xsec/blocks_p9_30sym.parquet); tell Claude."
EB = pd.read_parquet(BLK9)
EB["group"] = EB["symbol"].map(GROUP); EB["split"] = np.where(EB["date"] <= TRAIN_END, "train", "test")
T9 = EB[(EB["group"] == "thin")].dropna(subset=["C3_hat", "MAE_60", "ewma_vol", "S60"])
tr, te = T9[T9["split"] == "train"], T9[T9["split"] == "test"].copy()
def quint(col):
    br = tr[col].quantile([0.2, 0.4, 0.6, 0.8]).to_numpy()
    return np.searchsorted(br, te[col].to_numpy(), side="right")        # 0..4, breakpoints from training only
te["q_c3"] = quint("C3_hat"); te["q_vol"] = quint("ewma_vol"); te["q_s60"] = quint("S60")
by_c3 = te.groupby("q_c3")["MAE_60"].agg(["mean", "median", "count"])
by_s60 = te.groupby("q_s60")["MAE_60"].agg(["mean", "median", "count"])
# double sort: within each volatility quintile, top minus bottom C3 quintile
dbl = te.groupby(["q_vol", "q_c3"])["MAE_60"].mean().unstack()
within = (dbl[4] - dbl[0]).to_dict()
tail = te["MAE_60"] > tr["MAE_60"].quantile(0.95)
tail_by_c3 = tail.groupby(te["q_c3"]).mean().to_dict()
Rb = rng(5); dates = te["date"].unique(); posd = {d: np.where(te["date"].to_numpy() == d)[0] for d in dates}
bs = []
for _ in range(2000):
    X = te.iloc[np.concatenate([posd[d] for d in Rb.choice(dates, len(dates))])]
    g = X.groupby(["q_vol", "q_c3"])["MAE_60"].mean().unstack()
    bs.append(float(np.nanmean(g[4] - g[0])))
econ = {"MAE_bps_by_C3_quintile": by_c3.to_dict(), "MAE_bps_by_S60_quintile": by_s60.to_dict(),
        "top_minus_bottom_C3_within_vol_quintile_bps": within,
        "avg_within_vol_top_minus_bottom_bps": float(np.nanmean(list(within.values()))),
        "avg_within_vol_ci": [float(np.quantile(bs, 0.025)), float(np.quantile(bs, 0.975))],
        "share_hours_above_train_p95_MAE_by_C3_quintile": tail_by_c3,
        "mean_MAE_bps_test": float(te["MAE_60"].mean()), "n_test_hours": len(te)}
print(by_c3.round(1)); print("within volatility quintile, top - bottom C3 quintile (bps):", {k: round(v, 1) for k, v in within.items()})
print("average:", round(econ["avg_within_vol_top_minus_bottom_bps"], 1), "CI", np.round(econ["avg_within_vol_ci"], 1))
print("share of hours above the training 95th percentile, by C3 quintile:", {k: round(v, 3) for k, v in tail_by_c3.items()})
record("E1_economic_size", None, "real-data", econ, note="descriptive; Part 9 test set (already opened once); no new hypothesis")
