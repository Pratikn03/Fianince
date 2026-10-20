# ============================================================================
# CELL V6 — THE TEST (RUN ONCE; every run is counted). It zips the results and downloads p10_results.zip.
# ============================================================================
assert hashlib.sha256(open(p10_path).read().encode()).hexdigest() == P10_HASH, "spec changed after registration"
pth10 = os.path.join(PREREG, "test_set_unlocks_p10.json")
n_unl10 = (json.load(open(pth10))["n"] if os.path.exists(pth10) else 0) + 1
json.dump({"n": n_unl10, "utc": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()), "spec_sha256": P10_HASH}, open(pth10, "w"))
def holm(pd_):
    items = sorted((v if np.isfinite(v) else 1.0, k) for k, v in pd_.items()); m = len(items); out, run = {}, 0.0
    for j, (p_, k) in enumerate(items):
        run = max(run, min(1.0, p_ * (m - j))); out[k] = run
    return out
prim10 = evaluate_g(TB, "MAE_60", "C3_hat", BASE10)
ok10 = bool(np.isfinite(prim10.get("clark_west_p", np.nan)) and prim10["clark_west_p"] < 0.05 and prim10["delta_r2_ci"][0] > 0)
sec10 = {f"MAE | {c}": evaluate_g(TB, "MAE_60", c, BASE10)
         for c in ["S60", "gain_multiple", "log_halflife", "term_reversion", "term_momentum", "C3_flow"]}
h10 = holm({k: v.get("clark_west_p", np.nan) for k, v in sec10.items()})
for k in sec10:
    sec10[k]["holm_p"] = h10[k]
sh = lambda v: {k: (round(v[k], 5) if isinstance(v.get(k), float) else v.get(k)) for k in
                ["n_train", "n_test", "n_symbols", "n_test_dates", "r2_base", "delta_r2", "delta_r2_ci", "delta_auc_ci",
                 "clark_west_t", "clark_west_p", "holm_p", "coef_candidates_train", "skipped"] if k in v}
print("=== PRIMARY (Bybit thin coins, real depth, beyond the Part 9 baseline):", "PASS" if ok10 else "FAIL"); print(sh(prim10))
for k, v in sec10.items():
    print(k, sh(v))
record("V6_bybit_ob_test", ok10, "real-data", {"primary": prim10, "secondary": sec10, "holm_p": h10, "symbols": SYMBOLS,
       "prereg_sha256": P10_HASH, "test_set_unlocks": n_unl10}, criterion=PREREG_P10["primary"]["success"])
zp10 = os.path.join(BASE, "p10_results.zip")
with zipfile.ZipFile(zp10, "w", zipfile.ZIP_DEFLATED) as z:
    for fp in glob.glob(os.path.join(RESULTS, "V*.json")) + [os.path.join(RESULTS, f) for f in
              ("p10_day_status.csv", "p10_trades_manifest_sha256.csv")] + [p10_path, pth10]:
        if os.path.exists(fp):
            z.write(fp, os.path.relpath(fp, BASE))
    for fp in glob.glob(os.path.join(OBMIN, "*", "*.json")):
        z.write(fp, os.path.relpath(fp, BASE))           # per-day book audit (sha256 of every order-book file)
print("zipped ->", zp10)
if IN_COLAB:
    from google.colab import files
    files.download(zp10)
