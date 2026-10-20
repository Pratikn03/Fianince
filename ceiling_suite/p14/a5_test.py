# ============================================================================
# CELL A5 — THE TEST (RUN ONCE; every run is counted). Downloads p14_results.zip.
# ============================================================================
assert hashlib.sha256(open(p14_path).read().encode()).hexdigest() == P14_HASH, "spec changed after registration"
pth14 = os.path.join(PREREG, "test_set_unlocks_p14.json")
n14 = (json.load(open(pth14))["n"] if os.path.exists(pth14) else 0) + 1
json.dump({"n": n14, "utc": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()), "spec_sha256": P14_HASH}, open(pth14, "w"))
UBK["hour"] = UBK["t"]                                   # evaluate_g sorts by (date, symbol, hour)
TH14, MD14 = UBK[UBK["group"] == "thin"], UBK[UBK["group"] == "mid"]
prim14 = evaluate_g(TH14, "MAE_60", "C3_flow", UCTRL)
ok14 = bool(np.isfinite(prim14.get("clark_west_p", np.nan)) and prim14["clark_west_p"] < 0.05 and prim14["delta_r2_ci"][0] > 0)
sec14 = {"thin: MAE | S60": evaluate_g(TH14, "MAE_60", "S60", UCTRL),
         "thin: MAE | term_momentum": evaluate_g(TH14, "MAE_60", "term_momentum", UCTRL),
         "thin: MAE | term_reversion": evaluate_g(TH14, "MAE_60", "term_reversion", UCTRL),
         "mid: MAE | C3_flow": evaluate_g(MD14, "MAE_60", "C3_flow", UCTRL)}
items = sorted((v.get("clark_west_p", 1.0) if np.isfinite(v.get("clark_west_p", np.nan)) else 1.0, k) for k, v in sec14.items())
hp, run = {}, 0.0
for j, (p_, k) in enumerate(items):
    run = max(run, min(1.0, p_ * (len(items) - j))); hp[k] = run
for k in sec14:
    sec14[k]["holm_p"] = hp[k]
sh = lambda v: {k: v.get(k) for k in ["n_train", "n_test", "n_symbols", "n_test_dates", "r2_base", "delta_r2", "delta_r2_ci", "auc_base", "auc_full",
                                      "clark_west_t", "clark_west_p", "holm_p", "coef_candidates_train"]}
print("=== PRIMARY (thin US stocks, C3_flow beyond volatility and impact):", "PASS" if ok14 else "FAIL"); print(sh(prim14))
for k, v in sec14.items():
    print(k, sh(v))
record("A5_us_equity_test", ok14, "real-data", {"primary": prim14, "secondary": sec14, "holm_p": hp, "thin": IN_THIN, "mid": IN_MID,
       "prereg_sha256": P14_HASH, "test_set_unlocks": n14}, criterion=PREREG_P14["primary"]["success"])
zp = os.path.join(BASE, "p14_results.zip")
with zipfile.ZipFile(zp, "w", zipfile.ZIP_DEFLATED) as z:
    for fp in glob.glob(os.path.join(RESULTS, "A[1-5]_*.json")) + [p14_path, pth14]:
        if os.path.exists(fp):
            z.write(fp, os.path.relpath(fp, BASE))
print("zipped ->", zp)
if IN_COLAB:
    from google.colab import files
    files.download(zp)
