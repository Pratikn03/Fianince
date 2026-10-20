# ============================================================================
# CELL W6 — THE TEST (RUN ONCE; every run is counted)
# ============================================================================
assert hashlib.sha256(open(p15_path).read().encode()).hexdigest() == P15_HASH, "spec changed after registration"
pth15 = os.path.join(PREREG, "test_set_unlocks_p15.json")
n15 = (json.load(open(pth15))["n"] if os.path.exists(pth15) else 0) + 1
json.dump({"n": n15, "utc": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()), "spec_sha256": P15_HASH}, open(pth15, "w"))

# ---- Primary 1: frozen Part 9 model on untouched days ----
BASE9 = CTRL + IMPACT + VOLBENCH
P9 = pd.read_parquet(os.path.join(XDATA, "blocks_p9_30sym.parquet"))
P9 = P9[(P9["symbol"].map(GROUP) == "thin") & (P9["date"] <= TRAIN_END)].copy(); P9["split"] = "train"
NEW = WB[WB["split"] == "test"].copy(); NEW["split"] = "test"
for D_ in (P9, NEW):
    D_["kappa_sq"] = D_["kappa_hat"] ** 2
FZ = pd.concat([P9, NEW], ignore_index=True, sort=False)
FZ = winsor_train(FZ, IMPACT + ["rv_15", "rv_day", "ewma_vol", "mae_lag60"])     # limits from the Part 9 training rows
ev1 = evaluate_g(FZ, "MAE_60", "C3_hat", BASE9, level=0.975)
ev1s = evaluate_g(FZ, "MAE_60", "S60", BASE9, level=0.95, seed=91)
p1 = ev1["clark_west_p"]; ok1_raw = bool(p1 < 0.025 and ev1["delta_r2_ci"][0] > 0)

# ---- Primary 2: guards at matched activity ----
D = WB.dropna(subset=["MAE_60", "rv_360", "U_cert", "S60_cert", "S60_up", "rho_cert", "depth1"]).copy()
D = D[(D["rv_360"] > 0) & (D["U_cert"] > 0) & (D["S60_cert"] > 0) & (D["depth1"] > 0)]
tr = D["split"] == "train"
D["X_robust"] = D["U_cert"] * D["S60_up"]
D["X_point"] = D["U_cert"] * D["S60_cert"]
D["X_depth"] = 1.0 / D["depth1"]
D["X_spec"] = 1.0 / np.maximum(1e-6, 1.0 - np.minimum(D["rho_cert"], 1.0 - 1e-6))
D["X_vol"] = D["rv_360"]
for c in ["X_robust", "X_point", "X_depth", "X_spec", "X_vol"]:
    lo, hi = D.loc[tr, c].quantile([0.01, 0.99]); D[c] = D[c].clip(lo, hi)
def throttle(c):
    k = D[tr].groupby("symbol")[c].median()
    return np.minimum(1.0, D["symbol"].map(k) / D[c])
RAW = {"static": pd.Series(1.0, index=D.index), "robust_guard": throttle("X_robust"), "point_guard": throttle("X_point"),
       "depth_throttle": throttle("X_depth"), "spectral_throttle": throttle("X_spec"), "vol_cap": throttle("X_vol")}
RAW["vol_robust"] = RAW["vol_cap"] * RAW["robust_guard"]
Q = {}
for r, raw in RAW.items():
    c = raw[tr].groupby(D.loc[tr, "symbol"]).mean(); Q[r] = raw / D["symbol"].map(c)
thr = (D.loc[tr, "MAE_60"]).groupby(D.loc[tr, "symbol"]).quantile(0.95)
T = D[~tr].sort_values(["date", "symbol", "hour"]); dd = T["date"].to_numpy(); ud = np.unique(dd)
pos = {d: np.where(dd == d)[0] for d in ud}
def tlr_idx(r, idx):
    q = Q[r].loc[T.index].to_numpy()[idx]; L = q * T["MAE_60"].to_numpy()[idx]; return es95(L) / q.mean()
ALL = np.arange(len(T))
point = {r: {"TLR": tlr_idx(r, ALL), "activity_retained": float(RAW[r].loc[T.index].mean()),
             "share_throttled": float((RAW[r].loc[T.index] < 1).mean()),
             "breach_rate": float(((Q[r].loc[T.index] * T["MAE_60"]) > T["symbol"].map(thr)).mean())} for r in RAW}
pairs = [("robust_guard", "static"), ("robust_guard", "point_guard"), ("robust_guard", "depth_throttle"),
         ("robust_guard", "spectral_throttle"), ("robust_guard", "vol_cap"), ("vol_robust", "vol_cap")]
Rb = rng(151); bs = {pr: [] for pr in pairs}
for _ in range(2000):
    idx = np.concatenate([pos[d] for d in Rb.choice(ud, len(ud))])
    for a_, b_ in pairs:
        bs[(a_, b_)].append(np.log(tlr_idx(a_, idx)) - np.log(tlr_idx(b_, idx)))
cmp = {f"{a_} vs {b_}": {"log_TLR_diff": float(np.log(point[a_]["TLR"]) - np.log(point[b_]["TLR"])),
                         "ci95": [float(np.quantile(v, .025)), float(np.quantile(v, .975))],
                         "ci975": [float(np.quantile(v, .0125)), float(np.quantile(v, .9875))],
                         "p_one_sided": float(np.mean(np.array(v) >= 0))} for (a_, b_), v in bs.items()}
prim2 = cmp["robust_guard vs static"]; p2 = prim2["p_one_sided"]
ok2_raw = bool(prim2["ci975"][1] < 0)

# ---- Holm across the two primaries ----
ps = sorted([(p1, "forecast"), (p2, "guard")]); holm = {}; run = 0.0
for j, (p_, k) in enumerate(ps):
    run = max(run, min(1.0, p_ * (2 - j))); holm[k] = run
ok1 = ok1_raw and holm["forecast"] < 0.05; ok2 = ok2_raw and holm["guard"] < 0.05
sec = {k: v["p_one_sided"] for k, v in cmp.items() if k != "robust_guard vs static"}
sec["frozen model: S60"] = ev1s["clark_west_p"]
items = sorted((v, k) for k, v in sec.items()); hp, run = {}, 0.0
for j, (p_, k) in enumerate(items):
    run = max(run, min(1.0, p_ * (len(items) - j))); hp[k] = run

print("=== PRIMARY 1 (frozen Part 9 model on untouched days):", "PASS" if ok1 else "FAIL",
      {k: ev1.get(k) for k in ["n_test", "n_test_dates", "delta_r2", "delta_r2_ci", "clark_west_t", "clark_west_p"]})
print("=== PRIMARY 2 (robust guard vs static, matched activity):", "PASS" if ok2 else "FAIL", prim2)
for r in RAW:
    print(f"  {r:18s} TLR={point[r]['TLR']:8.1f} activity={point[r]['activity_retained']:.3f} "
          f"throttled={point[r]['share_throttled']:.2f} breach={point[r]['breach_rate']:.3f}")
for k, v in cmp.items():
    print(f"  {k:36s} {v['log_TLR_diff']:+.3f} {np.round(v['ci95'], 3)}")
print("Holm (primaries):", holm, "\nHolm (secondary):", {k: round(v, 4) for k, v in hp.items()})
record("W6_info_safety_test", bool(ok1 and ok2), "real-data",
       {"primary_1_forecast": ev1, "primary_1_pass": ok1, "secondary_S60": ev1s, "primary_2_guard": prim2,
        "primary_2_pass": ok2, "holm_primaries": holm, "rules": point, "comparisons": cmp, "secondary_holm_p": hp,
        "prereg_sha256": P15_HASH, "test_set_unlocks": n15},
       criterion="P1: CW p<0.025 and 97.5% CI>0; P2: 97.5% CI of log TLR(robust) - log TLR(static) below 0; Holm across both")
