# ============================================================================
# CELL C6 — THE TEST (RUN ONCE; every run is counted)
# ============================================================================
assert hashlib.sha256(open(p17_path).read().encode()).hexdigest() == P17_HASH, "spec changed after registration"
pth17 = os.path.join(PREREG, "test_set_unlocks_p17.json")
n17 = (json.load(open(pth17))["n"] if os.path.exists(pth17) else 0) + 1
json.dump({"n": n17, "utc": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()), "spec_sha256": P17_HASH}, open(pth17, "w"))
TH, MD = CB[CB["group"] == "thin"], CB[CB["group"] == "mid"]
# all thin-pair candidates on the same rows (rows where real, placebo, S60 and VPIN all exist) and the same bootstrap draws
TH = TH.dropna(subset=["C3_flow", "C3_placebo", "S60", "vpin"])
ev = evaluate_set(TH, "MAE_60", {"real": ["C3_flow"], "placebo": ["C3_placebo"], "S60": ["S60"], "vpin": ["vpin"],
                                 "real_plus_vpin": ["C3_flow", "vpin"]}, CB_CTRL, seed=171)
c_real = ev["cands"]["real"]; pdiff = paired_diff(ev, "real", "placebo")
beyond_vpin = paired_diff(ev, "real_plus_vpin", "vpin")      # C3_flow's gain once VPIN is in the baseline
H = {"P1_new_venue": c_real["clark_west_p"], "P2_beats_placebo": pdiff["p_one_sided"]}     # fixed sequence: no adjustment
ok = {"P1_new_venue": bool(H["P1_new_venue"] < 0.05 and c_real["delta_r2_ci"][0] > 0)}
ok["P2_beats_placebo"] = bool(ok["P1_new_venue"] and H["P2_beats_placebo"] < 0.05 and pdiff["ci"][0] > 0)
if not ok["P1_new_venue"]:
    print("primary 1 failed, so primary 2 is not tested (fixed sequence); its statistics are reported descriptively")
ev_mid = evaluate_set(MD.dropna(subset=["C3_flow"]), "MAE_60", {"real": ["C3_flow"]}, CB_CTRL, seed=172) if len(IN_MID) else None
sec = {"S60": ev["cands"]["S60"]["clark_west_p"], "placebo": ev["cands"]["placebo"]["clark_west_p"],
       "vpin": ev["cands"]["vpin"]["clark_west_p"], "beyond_vpin": beyond_vpin["p_one_sided"]}
if ev_mid:
    sec["mid_control"] = ev_mid["cands"]["real"]["clark_west_p"]
HS = holm(sec)
for k in ok:
    print(f"=== {k}:", "PASS" if ok[k] else "FAIL", "| p =", round(H[k], 5))
print("real    dR2 = %+.3f pts %s  CW t = %.2f" % (100 * c_real["delta_r2"], np.round(100 * np.array(c_real["delta_r2_ci"]), 3), c_real["clark_west_t"]))
print("placebo dR2 = %+.3f pts %s" % (100 * ev["cands"]["placebo"]["delta_r2"], np.round(100 * np.array(ev["cands"]["placebo"]["delta_r2_ci"]), 3)))
print("real - placebo = %+.3f pts %s" % (100 * pdiff["diff"], np.round(100 * np.array(pdiff["ci"]), 3)))
print("beyond VPIN    = %+.3f pts %s" % (100 * beyond_vpin["diff"], np.round(100 * np.array(beyond_vpin["ci"]), 3)))
print("secondary Holm:", {k: round(v, 4) for k, v in HS.items()})
strip = lambda e: {k: v for k, v in e.items() if k != "_boot"} if e else None
record("C6_new_venue_test", bool(all(ok.values())), "real-data",
       {"thin": IN_THIN, "mid": IN_MID, "thin_eval": strip(ev), "real_minus_placebo": pdiff, "beyond_vpin": beyond_vpin,
        "mid_eval": strip(ev_mid), "p_primaries_fixed_sequence": H, "pass": ok, "secondary_holm_p": HS,
        "prereg_sha256": P17_HASH, "test_set_unlocks": n17}, criterion=PREREG_P17["success"])
