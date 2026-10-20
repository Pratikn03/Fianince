# ============================================================================
# CELL R2 — EQUILIBRIUM PREDICTION ACROSS LIQUIDITY TERCILES (post hoc; Part 4 training days, cached)
# Reports the unit-free gain multiple S/|h0| = 1/(m - q kappa~) and the summed response in physical units
# (basis points per $1M of flow) by tercile, instead of flow-normalized S.
# ============================================================================
X3 = json.load(open(os.path.join(RESULTS, "X3_T6_cross_section.json")))["metrics"]["by_symbol"]
TERC = {s: v["tercile"] for s, v in X3.items()}
TR_D = [d for d in panel_dates() if d <= TRAIN_END]
jobs = [(s, d) for s in TERC for d in TR_D]
PAN2 = {}
with ThreadPoolExecutor(THREADS) as ex:
    for (s, d), (df, st) in zip(jobs, ex.map(lambda sd: get_day(*sd), jobs)):
        if df is not None and st.get("depth_day_ok"):
            PAN2[(s, d)] = df
FS2 = {}
for s in TERC:
    v = [np.nanmedian(np.abs(PAN2[(s, d)]["flow"].to_numpy())) for d in TR_D if (s, d) in PAN2]
    FS2[s] = float(np.nanmedian(v)) if v and np.nanmedian(v) > 0 else np.nan
rows = []
for (s, d), df in PAN2.items():
    if not np.isfinite(FS2[s]):
        continue
    p, u, dd_, x, tot = prep(df, FS2[s]); est = fit_t6(p, u, dd_, x)
    if est is None:
        continue
    imp = impulse_t6(est["a"], est["phi"], est["kappa"], est["r"], est["eps"], est["eta"], est["q"], L=H_GUARD)
    if not (np.all(np.isfinite(imp)) and abs(imp[0]) > 1e-12):
        continue
    S = float(np.sum(np.abs(imp)))
    rows.append({"symbol": s, "date": d, "tercile": TERC[s], "S60_norm": S, "GM": S / abs(imp[0]),
                 "S60_bp_per_musd": S / FS2[s], "depth1_musd": float(np.nanmedian(tot))})
E2 = pd.DataFrame(rows)
sym = E2.groupby(["symbol", "tercile"])[["S60_norm", "GM", "S60_bp_per_musd", "depth1_musd"]].median().reset_index()
Rb = rng(132); r2 = {"by_tercile": {}, "spearman_with_log_depth": {}}
for t, G in sym.groupby("tercile"):
    r2["by_tercile"][t] = {c: {"median": float(G[c].median()),
                              "ci": boot_ci(G[c].to_numpy(), Rb, stat=np.median)} for c in ["S60_norm", "GM", "S60_bp_per_musd"]}
for c in ["S60_norm", "GM", "S60_bp_per_musd"]:
    r2["spearman_with_log_depth"][c] = float(stats.spearmanr(np.log(sym["depth1_musd"]), sym[c])[0])
print(json.dumps(r2, indent=1))
record("R2_terciles_gain_multiple", None, "real-data", r2, note="post hoc; Part 4 training days; symbol-level medians")
