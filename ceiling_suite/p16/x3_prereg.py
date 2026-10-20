# ============================================================================
# CELL X3 — PRE-REGISTRATION (run BEFORE X4 downloads anything). E-mail P16_untouched_symbols.json to yourself.
# ============================================================================
PREREG_P16 = {
    "question": "On Binance perpetuals never used in Parts 4-15: (1) does C3_hat forecast the next hour's adverse excursion "
                "beyond the Part 9 volatility baseline? (2) Does it still do so once VPIN is added to the baseline (confirming "
                "the post-hoc Part 13 R8 result)? (3) Does the uncertainty-aware guard of Part 15 lower tail loss per unit of "
                "position compared with a static limit at matched activity?",
    "symbols": "the 30 drawn in X2 (seeded, before analysis); thin = median training depth within 1% below $0.39M "
               "(Part 5 rule); only thin symbols enter the tests; at least 15 valid training and 15 valid test days required",
    "data": "Binance USD-M futures; validation V1-V5 unchanged; flow normalized by each symbol's training median |flow|",
    "forecast_calendar": "train: 10th and 24th of each month 2023-2024; test: 6th and 20th, 2025-01 to 2026-09",
    "guard_calendar": "evaluation day = 15th; certification window = 12th-14th; train 2024; test 2025-01 to 2026-09",
    "primary_1": "thin: MAE_60 | C3_hat beyond CTRL + IMPACT + VOLBENCH (Part 9 specification), hour dummies, symbol fixed "
                 "effects, re-estimated on these symbols' training days",
    "primary_2": "thin: MAE_60 | C3_hat beyond the same baseline plus VPIN (six-hour window, 50 equal-volume buckets, "
                 "measured taker imbalance, winsorized at training 1%/99%)",
    "primary_3": "robust_guard vs static: q = min(1, k_s/(U_cert*S60_up)), S60_up = 90th percentile of 100 block-bootstrap "
                 "refits of the certified T6 operator (Part 15 definitions); k_s = symbol training median; positions "
                 "normalized to training mean 1; score log TLR difference",
    "success": "each primary passes if its Holm-adjusted one-sided p (across the three primaries) is below 0.05 and its "
               "95% date-block bootstrap interval excludes zero in the predicted direction (dR2 > 0 for 1-2; log TLR "
               "difference < 0 for 3). p: Clark-West for 1-2; bootstrap share of draws >= 0 for 3",
    "secondary": ["VPIN beyond the Part 9 baseline", "S60 beyond the Part 9 baseline", "robust_guard vs point_guard",
                  "vol_robust vs vol_cap"],
    "inference": "2,000 date-block bootstrap draws; secondary Holm-adjusted",
    "runs": "X6 is run once; every run is counted in prereg/test_set_unlocks_p16.json",
}
spec16 = json.dumps(PREREG_P16, indent=2, sort_keys=True); P16_HASH = hashlib.sha256(spec16.encode()).hexdigest()
p16_path = os.path.join(PREREG, "P16_untouched_symbols.json")
if not os.path.exists(p16_path):
    open(p16_path, "w").write(spec16); print("pre-registration written:", p16_path)
    if IN_COLAB:
        from google.colab import files
        files.download(p16_path)
elif hashlib.sha256(open(p16_path).read().encode()).hexdigest() != P16_HASH:
    raise RuntimeError("The spec differs from the registered file. Do not edit the spec after registering it.")
print("spec SHA-256:", P16_HASH)
