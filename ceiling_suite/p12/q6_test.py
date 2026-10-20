# ============================================================================
# CELL Q6 — THE TEST (RUN ONCE; every run is counted)
# ============================================================================
assert hashlib.sha256(open(p12_path).read().encode()).hexdigest() == P12_HASH, "spec changed after registration"
pth12 = os.path.join(PREREG, "test_set_unlocks_p12.json")
n12 = (json.load(open(pth12))["n"] if os.path.exists(pth12) else 0) + 1
json.dump({"n": n12, "utc": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()), "spec_sha256": P12_HASH}, open(pth12, "w"))
th, th_res = choose_theta(QB, gm_col="GM_cert")
trq = QB[QB["split"] == "train"]
med_v, med_g = trq["rv_360"].median(), (trq["U_cert"] * trq["S60_cert"]).median()
extra = {"amp_cert": (lambda X, th=th: X["rv_360"] * X["GM_cert"] ** th),
         "guard_cert": (lambda X: X["U_cert"] * X["S60_cert"]),
         "combined": (lambda X: np.maximum(X["rv_360"] / med_v, X["U_cert"] * X["S60_cert"] / med_g))}
G, rules = guard_frame(QB, extra)
cmp_vol = guard_compare(G, rules, ref="vol", level=0.95)
cmp_g6 = guard_compare(G, ["guard_summed", "guard_cert"], ref="guard_summed", level=0.95, seed=78)
prim = cmp_vol["vs_ref"]["amp_cert"]
ok12 = bool(prim["ci"][1] < 0)
secp = {"guard_cert vs vol": 1 - cmp_vol["vs_ref"]["guard_cert"]["share_boot_below_0"],
        "combined vs vol": 1 - cmp_vol["vs_ref"]["combined"]["share_boot_below_0"],
        "guard_cert vs guard_6h": 1 - cmp_g6["vs_ref"]["guard_cert"]["share_boot_below_0"]}
items = sorted((v, k) for k, v in secp.items()); hp, run = {}, 0.0
for j, (p_, k) in enumerate(items):
    run = max(run, min(1.0, p_ * (len(items) - j))); hp[k] = run
print(f"theta chosen on training: {th}  (training TLR by theta: { {k: round(v, 1) for k, v in th_res.items()} })")
for r in rules:
    pt = cmp_vol["point"][r]
    vs = cmp_vol["vs_ref"].get(r)
    print(f"  {r:13s} TLR={pt['TLR']:8.1f} breach={pt['breach_rate']:.3f}" + (f"  vs vol {vs['log_TLR_minus_ref']:+.3f} {np.round(vs['ci'], 3)}" if vs else ""))
print(f"  certified vs six-hour guard: {cmp_g6['vs_ref']['guard_cert']['log_TLR_minus_ref']:+.3f} {np.round(cmp_g6['vs_ref']['guard_cert']['ci'], 3)}")
print("=== PRIMARY (certified amplification-adjusted limit vs volatility limit):", "PASS" if ok12 else "FAIL")
print("Holm-adjusted secondary p:", {k: round(v, 4) for k, v in hp.items()})
record("Q6_certified_guard", ok12, "real-data", {"theta": th, "theta_train_tlr": th_res, "vs_vol": cmp_vol, "cert_vs_6h": cmp_g6,
       "secondary_holm_p": hp, "prereg_sha256": P12_HASH, "test_set_unlocks": n12}, criterion=PREREG_P12["primary"])
