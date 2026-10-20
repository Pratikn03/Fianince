# ============================================================================
# CELL Q7 — OCTOBER 10, 2025 (descriptive; NOT a test: the event was chosen after the fact, and Oct 10 was a test day
# in Parts 4-5). Hourly six-hour estimates for the 20 thin symbols and BTC/ETH from Oct 3 to Oct 11, 2025.
# ============================================================================
EV_DAYS = [f"2025-10-{d:02d}" for d in range(3, 12)]
EV_SYMS = THIN + ["BTCUSDT", "ETHUSDT"]
with ThreadPoolExecutor(THREADS) as ex:
    res = list(ex.map(lambda sd: (sd, get_day(*sd)), [(s, d) for s in EV_SYMS for d in EV_DAYS]))
for (s, d), (df, st) in res:
    if df is not None:
        PANEL[(s, d)] = df
for s in ["BTCUSDT", "ETHUSDT"] + [x for x in THIN if x not in FLOW_SCALE]:
    v = [np.nanmedian(np.abs(PANEL[(s, d)]["flow"].to_numpy())) for d in EV_DAYS[:7] if (s, d) in PANEL]
    FLOW_SCALE[s] = float(np.nanmedian(v)) if v and np.nanmedian(v) > 0 else 1.0
erows = []
for s in EV_SYMS:
    for d in EV_DAYS:
        if (s, d) in PANEL:
            erows += day_blocks9(s, d, FLOW_SCALE[s])
EV = pd.DataFrame(erows)
btc = EV[(EV["symbol"] == "BTCUSDT") & (EV["date"] == "2025-10-10")]
crash_hour = int(btc.loc[btc["MAE_60"].idxmax(), "hour"])
pre = EV[EV["date"] < "2025-10-10"]
def pct(s, col, v):
    ref = pre.loc[pre["symbol"] == s, col].dropna()
    return float((ref < v).mean()) if len(ref) > 20 and np.isfinite(v) else np.nan
ev = EV[EV["date"] == "2025-10-10"].copy()
for col in ("S60", "C3_hat", "rv_360"):
    ev[col + "_pct"] = [pct(s, col, v) for s, v in zip(ev["symbol"], ev[col])]
path = ev[ev["symbol"].isin(THIN)].groupby("hour")[["S60_pct", "C3_hat_pct", "rv_360_pct", "MAE_60"]].median()
at = ev[(ev["hour"] == crash_hour) & ev["symbol"].isin(THIN)]
rho_s = float(stats.spearmanr(at["S60"], at["MAE_60"], nan_policy="omit")[0]) if len(at) > 5 else np.nan
rho_v = float(stats.spearmanr(at["rv_360"], at["MAE_60"], nan_policy="omit")[0]) if len(at) > 5 else np.nan
print("crash hour (largest BTC next-hour excursion on Oct 10):", crash_hour, "UTC")
print(path.round(3).to_string())
print(f"cross-section of thin symbols at the crash hour: Spearman(S60, MAE) = {rho_s:.2f}; Spearman(rv_6h, MAE) = {rho_v:.2f}")
try:
    import matplotlib; matplotlib.use("Agg"); import matplotlib.pyplot as plt
    fig, ax = plt.subplots(figsize=(7, 3.2))
    ax.plot(path.index, path["S60_pct"], marker="o", label="summed response $S_{60}$ (6-hour estimate)")
    ax.plot(path.index, path["rv_360_pct"], marker="s", label="6-hour realized volatility")
    ax.axvline(crash_hour, color="k", ls=":", lw=1); ax.set_xlabel("hour of Oct 10, 2025 (UTC)")
    ax.set_ylabel("median percentile vs Oct 3-9"); ax.set_ylim(0, 1); ax.legend(fontsize=8, frameon=False)
    fig.tight_layout(); fig.savefig(os.path.join(RESULTS, "fig_oct10.pdf")); fig.savefig(os.path.join(RESULTS, "fig_oct10.png"), dpi=150)
except Exception as e:
    print("figure skipped:", e)
record("Q7_oct10_event", None, "real-data", {"crash_hour_utc": crash_hour, "median_by_hour_thin": path.to_dict(),
       "spearman_S60_MAE_at_crash": rho_s, "spearman_rv6h_MAE_at_crash": rho_v,
       "by_symbol_at_crash": at[["symbol", "S60", "S60_pct", "C3_hat", "rv_360", "MAE_60"]].to_dict("records")},
       note="descriptive event study, chosen after the fact; not a test")
zp12 = os.path.join(BASE, "p12_results.zip")
with zipfile.ZipFile(zp12, "w", zipfile.ZIP_DEFLATED) as z:
    for fp in [os.path.join(RESULTS, f) for f in ("E1_economic_size.json", "Q4_build.json", "Q5_blocks.json", "Q6_certified_guard.json",
               "Q7_oct10_event.json", "fig_oct10.pdf", "fig_oct10.png", "p12_manifest_sha256.csv")] + [p12_path, pth12]:
        if os.path.exists(fp):
            z.write(fp, os.path.relpath(fp, BASE))
print("zipped ->", zp12)
if IN_COLAB:
    from google.colab import files
    files.download(zp12)
