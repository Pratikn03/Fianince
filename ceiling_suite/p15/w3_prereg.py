# ============================================================================
# CELL W3 — PRE-REGISTRATION (run BEFORE W4 downloads anything). E-mail P15_info_safety.json to yourself.
# ============================================================================
PREREG_P15 = {
    "question": "On days never used before: (1) does the frozen Part 9 forecasting model still find that C3_hat forecasts the "
                "next hour's adverse excursion beyond the volatility baseline? (2) Does an uncertainty-aware guard (bootstrap "
                "upper bound on the certified summed response, used as a one-sided throttle) lower tail loss per unit of "
                "position compared with standard controls at matched activity?",
    "data": "Binance USD-M futures, the 20 thin symbols of Parts 6, 9 and 12; evaluation day = the 15th of each month "
            "(train 2024, test 2025-01 to 2026-09); certification window = the 12th-14th of the same month; none of these "
            "days was used on Binance in Parts 1-14; validation V1-V5 unchanged; flow normalized by the Part 9 training "
            "flow scale of each symbol (results/U2_build.json), so that features are on the scale of the frozen model",
    "primary_1_forecast": {"model": "Part 9 primary, frozen: MAE_60 | C3_hat beyond CTRL + IMPACT + VOLBENCH, hour dummies, "
                                    "symbol fixed effects; coefficients and winsorization limits estimated on the Part 9 "
                                    "training blocks (2023-2024, blocks_p9_30sym.parquet, thin group) only",
                           "test": "all hours 6-23 UTC of the Part 15 test evaluation days",
                           "success": "Clark-West one-sided p < 0.025 AND 97.5% date-block bootstrap CI of dR2 above 0"},
    "certification": "T6 model fitted by pooled within-day OLS on the minutes of the valid window days (at least 2 of 3); "
                     "S60_cert = summed |impulse response| over 60 minutes; U_cert = 95th percentile of |normalized flow|; "
                     "S60_up = 90th percentile of S60 over 100 bootstrap refits resampling 60-minute blocks of the window "
                     "(blocks never span two days); rho_cert = spectral radius of the certified 3x3 transition matrix",
    "rules": {"static": "q = 1",
              "robust_guard (proposed)": "q = min(1, k_s / (U_cert * S60_up))",
              "point_guard": "q = min(1, k_s / (U_cert * S60_cert))",
              "depth_throttle": "q = min(1, depth1 / k_s)  (depth1 = depth within 1% at the start of the hour)",
              "spectral_throttle": "q = min(1, k_s / (1 / (1 - rho_cert)))  (rho_cert >= 1 -> fully throttled to the "
                                   "training minimum)",
              "vol_cap": "q = min(1, k_s / rv_360)",
              "vol_robust": "q = min(1, k_s / rv_360) * min(1, k'_s / (U_cert * S60_up))"},
    "thresholds": "k_s = the symbol's training median of the throttle variable, so each throttle binds in about half of "
                  "training hours; positions are then normalized so that their training mean is 1 per symbol and rule "
                  "(matched activity)",
    "unit": "symbol-hour, hours 6-23 UTC of the evaluation day; loss = q x next-hour MAE",
    "score": "TLR = ES95(loss) / mean(q) on the test hours; also mean un-normalized q (activity retained), share of hours "
             "throttled, breach rate (loss above the symbol's training 95th percentile of static loss)",
    "primary_2_guard": "log TLR(robust_guard) - log TLR(static) < 0 with the 97.5% date-block bootstrap interval below 0",
    "primaries": "two primaries; the program passes a primary only under Holm at 0.05 across the two",
    "secondary": ["robust_guard vs point_guard (does accounting for estimation uncertainty help?)",
                  "robust_guard vs depth_throttle", "robust_guard vs spectral_throttle", "robust_guard vs vol_cap",
                  "vol_robust vs vol_cap (does the robust guard add to a volatility cap?)",
                  "frozen model: S60 beyond the Part 9 baseline"],
    "inference": "2,000 date-block bootstrap draws; secondary Holm-adjusted (bootstrap share of draws >= 0 as one-sided p "
                 "for guard comparisons; Clark-West p for the forecasting secondary)",
    "runs": "W6 is run once; every run is counted in prereg/test_set_unlocks_p15.json",
    "previous_hashes": {"part9": "71983f1a9d2ca23cafe5ce4de5d5d9ddb406529ceaf5aec57a7dee81a75f846d",
                        "part12": "b9a56af4 (see P12_certified_guard.json)"},
}
spec15 = json.dumps(PREREG_P15, indent=2, sort_keys=True); P15_HASH = hashlib.sha256(spec15.encode()).hexdigest()
p15_path = os.path.join(PREREG, "P15_info_safety.json")
if not os.path.exists(p15_path):
    open(p15_path, "w").write(spec15); print("pre-registration written:", p15_path)
    if IN_COLAB:
        from google.colab import files
        files.download(p15_path)
elif hashlib.sha256(open(p15_path).read().encode()).hexdigest() != P15_HASH:
    raise RuntimeError("The spec differs from the registered file. Do not edit the spec after registering it.")
print("spec SHA-256:", P15_HASH)
