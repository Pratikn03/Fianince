# ============================================================================
# CELL Q3 — PRE-REGISTRATION (run BEFORE Q4 downloads anything). E-mail P12_certified_guard.json to yourself.
# ============================================================================
PREREG_P12 = {
    "question": "Does a guard whose operator is certified from the previous three days lower tail loss per unit of position "
                "in thin books, compared with a volatility limit? (Part 6 estimated the operator from six hours and failed.)",
    "data": "Binance USD-M futures, the 20 thin symbols of Parts 6 and 9; evaluation days = the 28th of each month "
            "(train 2024, test 2025-01 to 2026-09); certification window = the 25th-27th of the same month; none of these "
            "days was used in Parts 1-11; validation V1-V5 unchanged",
    "certification": "T6 model fitted by pooled within-day OLS on the minutes of the valid window days (at least 2 of 3); "
                     "S60_cert = summed |impulse response| over 60 minutes, GM_cert = S60_cert/|h0|, U_cert = 95th percentile "
                     "of |normalized flow| over the window; fixed for the whole evaluation day",
    "unit": "symbol-hour, hours 6-23 UTC of the evaluation day; loss = position x next-hour MAE",
    "rules": {"vol": "R = six-hour realized volatility (as Part 6)",
              "amp_cert (primary)": "R = rv_360 * GM_cert^theta, theta in {0, .25, .5, .75, 1} chosen on training TLR",
              "guard_cert": "R = U_cert * S60_cert", "guard_6h": "R = U6 * S60 (six-hour estimate, as Part 6)",
              "combined": "R = max(rv_360 / median_train(rv_360), U_cert*S60_cert / median_train(U_cert*S60_cert))",
              "static": "R = 1"},
    "sizing": "q = c_s / R with c_s setting the training mean of q to 1 per symbol and rule; risk winsorized at training 1%/99%",
    "score": "TLR = ES95(loss) / mean(q) on the test hours",
    "primary": "log TLR(amp_cert) - log TLR(vol) < 0 with the 95% date-block bootstrap interval below 0",
    "secondary": ["guard_cert vs vol", "combined vs vol", "guard_cert vs guard_6h (does certification improve the guard?)"],
    "inference": "2,000 date-block bootstrap draws; secondary Holm-adjusted (bootstrap share of draws >= 0 as one-sided p)",
    "runs": "Q6 is run once; every run is counted in prereg/test_set_unlocks_p12.json",
    "previous_hashes": {"part6": "65acda36186147bd6e959ce8c56b9958b7a7f94a01f8784bc82f2b1512360215",
                        "part9": "71983f1a9d2ca23cafe5ce4de5d5d9ddb406529ceaf5aec57a7dee81a75f846d"},
}
spec12 = json.dumps(PREREG_P12, indent=2, sort_keys=True); P12_HASH = hashlib.sha256(spec12.encode()).hexdigest()
p12_path = os.path.join(PREREG, "P12_certified_guard.json")
if not os.path.exists(p12_path):
    open(p12_path, "w").write(spec12); print("pre-registration written:", p12_path)
    if IN_COLAB:
        from google.colab import files
        files.download(p12_path)
elif hashlib.sha256(open(p12_path).read().encode()).hexdigest() != P12_HASH:
    raise RuntimeError("The spec differs from the registered file. Do not edit the spec after registering it.")
print("spec SHA-256:", P12_HASH)
