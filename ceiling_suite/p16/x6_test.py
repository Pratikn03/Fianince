# ============================================================================
# CELL X6 — THE TEST (RUN ONCE; every run is counted)
# ============================================================================
assert hashlib.sha256(open(p16_path).read().encode()).hexdigest() == P16_HASH, "spec changed after registration"
pth16 = os.path.join(PREREG, "test_set_unlocks_p16.json")
n16 = (json.load(open(pth16))["n"] if os.path.exists(pth16) else 0) + 1
json.dump({"n": n16, "utc": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()), "spec_sha256": P16_HASH}, open(pth16, "w"))
BASE9 = CTRL + IMPACT + VOLBENCH
F = winsor_train(FB.copy(), IMPACT + ["rv_15", "rv_day", "ewma_vol", "mae_lag60"])
lo, hi = F.loc[F["split"] == "train", "vpin"].quantile([0.01, 0.99]); F["vpin_w"] = F["vpin"].clip(lo, hi)
ev1 = evaluate_g(F, "MAE_60", "C3_hat", BASE9)
ev2 = evaluate_g(F, "MAE_60", "C3_hat", BASE9 + ["vpin_w"], seed=89)
ev_v = evaluate_g(F, "MAE_60", "vpin", BASE9, seed=90)
ev_s = evaluate_g(F, "MAE_60", "S60", BASE9, seed=91)

D = GB.dropna(subset=["MAE_60", "rv_360", "U_cert", "S60_cert", "S60_up"]).copy()
D = D[(D["rv_360"] > 0) & (D["U_cert"] > 0) & (D["S60_cert"] > 0)]
tr = D["split"] == "train"
D["X_robust"] = D["U_cert"] * D["S60_up"]; D["X_point"] = D["U_cert"] * D["S60_cert"]; D["X_vol"] = D["rv_360"]
for c in ["X_robust", "X_point", "X_vol"]:
    lo, hi = D.loc[tr, c].quantile([0.01, 0.99]); D[c] = D[c].clip(lo, hi)
def throttle(c):
    k = D[tr].groupby("symbol")[c].median(); return np.minimum(1.0, D["symbol"].map(k) / D[c])
RAW = {"static": pd.Series(1.0, index=D.index), "robust_guard": throttle("X_robust"), "point_guard": throttle("X_point"),
       "vol_cap": throttle("X_vol")}
RAW["vol_robust"] = RAW["vol_cap"] * RAW["robust_guard"]
Q = {r: raw / D["symbol"].map(raw[tr].groupby(D.loc[tr, "symbol"]).mean()) for r, raw in RAW.items()}
T = D[~tr].sort_values(["date", "symbol", "hour"]); dd = T["date"].to_numpy(); ud = np.unique(dd)
pos = {d: np.where(dd == d)[0] for d in ud}
def tlr_idx(r, idx):
    q = Q[r].loc[T.index].to_numpy()[idx]; L = q * T["MAE_60"].to_numpy()[idx]; return es95(L) / q.mean()
ALL = np.arange(len(T))
point = {r: {"TLR": tlr_idx(r, ALL), "activity_retained": float(RAW[r].loc[T.index].mean())} for r in RAW}
pairs = [("robust_guard", "static"), ("robust_guard", "point_guard"), ("vol_robust", "vol_cap")]
Rb = rng(161); bs = {pr: [] for pr in pairs}
for _ in range(2000):
    idx = np.concatenate([pos[d] for d in Rb.choice(ud, len(ud))])
    for a_, b_ in pairs:
        bs[(a_, b_)].append(np.log(tlr_idx(a_, idx)) - np.log(tlr_idx(b_, idx)))
cmp = {f"{a_} vs {b_}": {"log_TLR_diff": float(np.log(point[a_]["TLR"]) - np.log(point[b_]["TLR"])),
                         "ci95": [float(np.quantile(v, .025)), float(np.quantile(v, .975))],
                         "p_one_sided": float(np.mean(np.array(v) >= 0))} for (a_, b_), v in bs.items()}
P = {"P1_forecast": ev1["clark_west_p"], "P2_beyond_vpin": ev2["clark_west_p"], "P3_guard": cmp["robust_guard vs static"]["p_one_sided"]}
items = sorted((v, k) for k, v in P.items()); holm, run = {}, 0.0
for j, (p_, k) in enumerate(items):
    run = max(run, min(1.0, p_ * (3 - j))); holm[k] = run
ok = {"P1_forecast": holm["P1_forecast"] < 0.05 and ev1["delta_r2_ci"][0] > 0,
      "P2_beyond_vpin": holm["P2_beyond_vpin"] < 0.05 and ev2["delta_r2_ci"][0] > 0,
      "P3_guard": holm["P3_guard"] < 0.05 and cmp["robust_guard vs static"]["ci95"][1] < 0}
sec = {"VPIN beyond baseline": ev_v["clark_west_p"], "S60 beyond baseline": ev_s["clark_west_p"],
       "robust vs point guard": cmp["robust_guard vs point_guard"]["p_one_sided"], "vol_robust vs vol_cap": cmp["vol_robust vs vol_cap"]["p_one_sided"]}
items = sorted((v, k) for k, v in sec.items()); hp, run = {}, 0.0
for j, (p_, k) in enumerate(items):
    run = max(run, min(1.0, p_ * (len(items) - j))); hp[k] = run
sh = lambda v: {k: v.get(k) for k in ["n_symbols", "n_test", "n_test_dates", "delta_r2", "delta_r2_ci", "clark_west_t", "clark_west_p"]}
for k in ok:
    print(f"=== {k}:", "PASS" if ok[k] else "FAIL", "Holm p =", round(holm[k], 5))
print("P1", sh(ev1)); print("P2", sh(ev2)); print("VPIN", sh(ev_v)); print("S60", sh(ev_s))
for k, v in cmp.items():
    print(f"  {k:28s} {v['log_TLR_diff']:+.3f} {np.round(v['ci95'], 3)}")
print("secondary Holm:", {k: round(v, 4) for k, v in hp.items()})
record("X6_untouched_symbols_test", bool(all(ok.values())), "real-data",
       {"symbols": THIN16, "P1": ev1, "P2": ev2, "vpin": ev_v, "S60": ev_s, "guard": {"rules": point, "comparisons": cmp},
        "holm_primaries": holm, "pass": ok, "secondary_holm_p": hp, "prereg_sha256": P16_HASH, "test_set_unlocks": n16},
       criterion=PREREG_P16["success"])
