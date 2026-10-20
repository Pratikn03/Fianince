# ============================================================================
# CELL V5 — HOURLY BLOCKS (no outcome is looked at here)
# ============================================================================
assert SYMBOLS, "no coin passed the inclusion rule; tell Claude"
rows = []
for i, (s, d) in enumerate(OK):
    rows += day_blocks9(s, d, FLOW_SCALE[s])
    if (i + 1) % 100 == 0:
        print(f"   blocks: {i+1}/{len(OK)}")
TB = pd.DataFrame(rows)
TB["split"] = np.where(TB["date"] <= TRAIN_END, "train", "test")
TB["kappa_sq"] = TB["kappa_hat"] ** 2
TB = winsor_train(TB, IMPACT + ["rv_15", "rv_day", "ewma_vol", "mae_lag60"])
TB.to_parquet(os.path.join(BASE, "data_bybit_ob", "blocks_p10.parquet"))
print(TB.groupby("split").size())
record("V5_blocks", None, "audit", {"blocks": TB.groupby("split").size().to_dict(),
       "coverage": {c: float(TB[c].notna().mean()) for c in ["C3_hat", "S60", "log_depth1", "imbalance", "ewma_vol"]}})
