# ============================================================================
# CELL R1 — ANALYSIS PLAN (fixed and hashed before anything is computed; the data are NOT untouched, so every result of this
# notebook is reported as post hoc). E-mail P18_posthoc_plan.json to yourself.
# ============================================================================
PLAN18 = {
    "status": "post hoc: all samples below were opened by earlier pre-registered tests; this plan only fixes the analysis before "
              "it is computed",
    "A_placebo": {
        "samples": ["Part 9 thin symbols (20), train 10th/24th 2023-2024, test 6th/20th 2025-2026",
                    "Part 16 thin symbols (5), same calendar"],
        "placebo": "C3_placebo = C3_hat from fit_t6 on the same window with the flow series circularly shifted by 180 minutes "
                   "inside the 360-minute window; prices and depth unchanged",
        "comparison": "dR2(C3_hat) - dR2(C3_placebo), each beyond CTRL + IMPACT + VOLBENCH with symbol fixed effects, on the same "
                      "rows and the same 2,000 date-block bootstrap draws; also each one's own dR2",
        "sanity": "recomputed C3_hat must match the stored value (share of rows within 1e-6 relative)"},
    "B_guards": {
        "samples": ["Part 15 guard sample (20 thin symbols, 15th of each month)", "Part 16 guard sample (5 new thin symbols)"],
        "new_rules": {"peak_cert": "q = min(1, k_s/(U_cert * P60_cert)), P60_cert = max |impulse response| of the certified operator",
                      "peak_6h": "q = min(1, k_s/(U6 * P60)), six-hour estimate (the peak-guard of Paper 2's theory, estimated)",
                      "participation": "q = min(1, V6/k_s), V6 = dollar volume over the previous six hours",
                      "margin_scan": "q = min(1, k_s/SCAN), SCAN = 99th percentile of |60-minute log return| over the three "
                                     "certification days (an exchange-style scanning range, updated daily)"},
        "note": "an inventory-only cap is a fixed position limit, identical to the static rule once activity is matched",
        "comparison": "log TLR(robust_guard) - log TLR(rule) on the test hours, 2,000 date-block bootstrap draws, matched activity "
                      "(positions normalized to training mean 1 per symbol and rule), k_s = symbol training median, risk measures "
                      "winsorized at training 1%/99%; Holm across the four new comparisons within each sample",
        "sanity": "static and robust-guard TLRs must reproduce the published Part 15 and Part 16 values"},
}
spec18 = json.dumps(PLAN18, indent=2, sort_keys=True); P18_HASH = hashlib.sha256(spec18.encode()).hexdigest()
p18_path = os.path.join(PREREG, "P18_posthoc_plan.json")
if not os.path.exists(p18_path):
    open(p18_path, "w").write(spec18); print("plan written:", p18_path)
    if IN_COLAB:
        from google.colab import files
        files.download(p18_path)
elif hashlib.sha256(open(p18_path).read().encode()).hexdigest() != P18_HASH:
    raise RuntimeError("The plan differs from the registered file. Do not edit it after registering it.")
print("plan SHA-256:", P18_HASH)
