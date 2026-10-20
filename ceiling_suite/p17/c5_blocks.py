# ============================================================================
# CELL C5 — HOURLY BLOCKS (features, placebo and outcome; no evaluation here). About 10-20 minutes.
# ============================================================================
rows = []
for (s, d), df in sorted(PANEL.items()):
    if s in IN_THIN + IN_MID:
        rows += cb_blocks(df, s, d, FLOW_SCALE17[s])
CB = pd.DataFrame(rows)
CB["group"] = np.where(CB["symbol"].isin(IN_THIN), "thin", "mid")
CB["split"] = np.where(CB["date"] <= TRAIN_END, "train", "test")
CB["kappa_sq"] = CB["kappa_hat"] ** 2
CB = winsor_train(CB, ["kappa_hat", "kappa_sq", "kyle_lam", "amihud_60", "rv_15", "rv_day", "ewma_vol", "mae_lag60"])
CB.to_parquet(os.path.join(CDATA, "blocks_p17.parquet"))
print(CB.groupby(["group", "split"]).size().unstack())
cc = CB[["C3_flow", "C3_placebo"]].dropna()
record("C5_blocks", None, "audit", {"blocks": CB.groupby(["group", "split"]).size().unstack().to_dict(),
       "coverage": {c: float(CB[c].notna().mean()) for c in ["C3_flow", "C3_placebo", "S60", "vpin", "MAE_60"]},
       "corr_real_placebo_training": float(cc.corr(method="spearman").iloc[0, 1]) if len(cc) > 10 else None})
