# ============================================================================
# CELL V2 — PRE-REGISTRATION (run ONCE, BEFORE you upload any test-day file; V3 refuses to run without it)
# It downloads P10_bybit_ob.json: e-mail it to yourself before uploading data. Never edit this cell afterwards.
# ============================================================================
CTRL10 = ["rv_60", "rv_360", "abs_ret_60", "flow_imb_60", "log_vol_60", "log_depth1", "imbalance"]   # Part 9 minus open interest
BASE10 = CTRL10 + IMPACT + VOLBENCH
PREREG_P10 = {
    "question": "A second venue with real depth: in the 20 thin-set coins on Bybit USDT perpetuals, does C3_hat forecast "
                "next-hour MAE beyond the Part 9 baseline (volatility forecasting, price impact, depth, hour effects)?",
    "relation_to_part7": "Part 7 tested Bybit with trades only (depth-free C3_flow) and failed. This is a new test with "
                         "order-book depth on days Part 7 never used. Both results are reported.",
    "data": "Bybit history-data, Contract, OB Data (daily ob200 files: one snapshot plus every update of the top 200 levels), "
            "rebuilt to the book at the end of each UTC minute; Bybit public trade archive for price, signed taker flow and "
            "volume. Price = last trade (as Binance klines in Parts 4-9). Depth = $ notional within 1% of mid.",
    "day_validity": "trade minutes >= 80%; merged depth minutes >= 80%; <= 5 update-id gaps; a book whose mid is > 3% from the "
                    "last trade is treated as missing",
    "coins": COINS, "train": TRAIN_D, "test": TEST_D,
    "inclusion": "a coin enters if it has >= 8 valid training days and >= 24 valid test days; coins Bybit does not list are excluded",
    "unit": "symbol-hour blocks, hours 6-23 UTC; features from minutes before t on the same day; outcome MAE over (t, t+60]",
    "baseline": BASE10 + ["symbol fixed effects"],
    "primary": {"sample": "all included coins", "outcome": "MAE_60", "candidate": "C3_hat (winsorized at train 1%/99%)",
                "success": "Clark-West one-sided p < 0.05 AND 95% date-block bootstrap CI of dR2 above 0"},
    "secondary": ["MAE | S60", "MAE | gain_multiple", "MAE | log_halflife", "MAE | term_reversion", "MAE | term_momentum",
                  "MAE | C3_flow"],
    "inference": "Clark-West (Newey-West 6 lags); 2,000 date-block bootstrap draws (all symbols on a date together); secondary Holm-adjusted",
    "runs": "V6 is run once; every run is counted in prereg/test_set_unlocks_p10.json",
    "previous_hashes": {"part6": "65acda36186147bd6e959ce8c56b9958b7a7f94a01f8784bc82f2b1512360215",
                        "part9": "71983f1a9d2ca23cafe5ce4de5d5d9ddb406529ceaf5aec57a7dee81a75f846d"},
}
spec_txt10 = json.dumps(PREREG_P10, indent=2, sort_keys=True)
P10_HASH = hashlib.sha256(spec_txt10.encode()).hexdigest()
p10_path = os.path.join(PREREG, "P10_bybit_ob.json")
if not os.path.exists(p10_path):
    open(p10_path, "w").write(spec_txt10); print("pre-registration written:", p10_path)
    if IN_COLAB:
        from google.colab import files
        files.download(p10_path)
elif hashlib.sha256(open(p10_path).read().encode()).hexdigest() != P10_HASH:
    raise RuntimeError("The spec differs from the registered file. Do not edit the spec after registering it.")
print("spec SHA-256:", P10_HASH)
