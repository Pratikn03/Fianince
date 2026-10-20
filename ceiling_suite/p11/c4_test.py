# ============================================================================
# CELL C4 — THE TEST (RUN ONCE; every run is counted). About 5-15 minutes. Downloads p11_results.zip.
# ============================================================================
assert hashlib.sha256(open(p11_path).read().encode()).hexdigest() == P11_HASH, "spec changed after registration"
pth11 = os.path.join(PREREG, "test_set_unlocks_p11.json")
n11 = (json.load(open(pth11))["n"] if os.path.exists(pth11) else 0) + 1
json.dump({"n": n11, "utc": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()), "spec_sha256": P11_HASH}, open(pth11, "w"))
RES = {}
for mkt in INCLUDED:
    t0 = time.time(); RES[mkt], _ = analyse(mkt)
    r = RES[mkt]
    print(f"{mkt}: {r['weeks']} wks | fast r={r['fast']['r']:.3f} {np.round(r['fast']['r_ci'],3)} w={r['fast']['w']:.3f} "
          f"{np.round(r['fast']['w_ci'],3)} | slow r={r['slow']['r']:.3f} | fast-slow {np.round(r['fast_minus_slow_r']['ci'],3)} | "
          f"price-only widths {r['price_only_width']:.2f} vs tagged {r['tagged_width_fast']:.3f} ({time.time()-t0:.0f}s)")
h1 = {m: bool(RES[m]["tagged_width_fast"] < 0.25 and
              all(RES[m]["price_only"][k][1] - RES[m]["price_only"][k][0] > 0.25 for k in ("r1_ci", "r2_ci"))) for m in RES}
h2 = {m: bool(RES[m]["fast"]["w_ci"][0] > 0) for m in RES}
h3 = {m: bool(RES[m]["fast_minus_slow_r"]["ci"][1] < 0) for m in RES}
n = len(RES)
ok1, ok2, ok3 = sum(h1.values()) >= 0.75 * n, sum(h2.values()) >= 0.75 * n, sum(h3.values()) >= 0.5 * n
print(f"\n=== H1 (primary, disclosure precision): {sum(h1.values())}/{n} ->", "PASS" if ok1 else "FAIL")
print(f"=== H2 (fast class trend-follows):      {sum(h2.values())}/{n} ->", "PASS" if ok2 else "FAIL")
print(f"=== H3 (fast class has shorter memory): {sum(h3.values())}/{n} ->", "PASS" if ok3 else "FAIL")
record("C4_cot_disclosure", ok1, "real-data", {"by_market": RES, "H1": h1, "H2": h2, "H3": h3, "H2_pass": ok2, "H3_pass": ok3,
       "prereg_sha256": P11_HASH, "test_set_unlocks": n11}, criterion=PREREG_P11["H1_primary"])
zp = os.path.join(BASE, "p11_results.zip")
with zipfile.ZipFile(zp, "w", zipfile.ZIP_DEFLATED) as z:
    for fp in [os.path.join(RESULTS, "C3_cot_data.json"), os.path.join(RESULTS, "C4_cot_disclosure.json"), p11_path, pth11]:
        if os.path.exists(fp):
            z.write(fp, os.path.relpath(fp, BASE))
print("zipped ->", zp)
if IN_COLAB:
    from google.colab import files
    files.download(zp)
