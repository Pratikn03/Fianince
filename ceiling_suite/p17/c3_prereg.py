# ============================================================================
# CELL C3 — PRE-REGISTRATION (run BEFORE C4 downloads any trade). E-mail P17_new_venue.json to yourself.
# ============================================================================
PREREG_P17 = {
    "question": "On a venue never used in Parts 1-16 (Coinbase Exchange spot, USD pairs): (1) does the depth-free amplification "
                "margin C3_flow forecast the next hour's maximum adverse excursion beyond a volatility and price-impact baseline "
                "in thin pairs? (2) Is its content the minute-level alignment of flow and prices that the model describes, rather "
                "than the persistence of order flow (order splitting)? Test: the real statistic beats an order-splitting placebo.",
    "data": "Coinbase Exchange public REST trades (no account); minute bars of last trade price, signed taker notional (taker buy "
            "when the maker side is 'sell') and notional volume; a day is valid if >= 60% of its minutes have a trade; days with "
            "more than 400 pages of trades are dropped",
    "universe": {"thin": THIN17, "mid_control": MID17, "rule": "USD pairs online in 2026, excluding stablecoins and wrapped or "
                 "staked tokens, with >= 20 daily candles in Dec 2023 and >= 25 in Jun 2024; thin = median Jun-2024 daily dollar "
                 "volume $0.5M-$5M (up to 20 drawn, seed 20261134); mid control = $15M-$50M (up to 4 drawn)"},
    "days": {"train": TRAIN_DAYS, "test": TEST_DAYS},
    "inclusion": "a pair enters if it has >= 15 valid training days and >= 25 valid test days",
    "unit": "pair x hour t in 06-23 UTC; features from minutes [t-360, t); outcome MAE over (t, t+60] in basis points",
    "flow_scale": "each pair's median |flow| over training minutes with at least one trade",
    "candidate": "C3_flow = kappa^2 eta q - (1-a) kappa, from dp = kappa u - (1-a) x_lag and u = (1-eta) u_lag + eta q x_lag, "
                 "x = 1e4 log price minus EMA(60 minutes), u = signed flow / flow scale (Part 7 and Part 14 definition)",
    "placebo": "C3_placebo = the same statistic with the flow series of the window circularly shifted by 180 minutes inside the "
               "window (prices unchanged): it keeps the window's flow distribution and, apart from one wrap point, its "
               "autocorrelation (order splitting), and breaks the minute alignment between flow and price; it uses no data from "
               "outside the window",
    "baseline": CB_CTRL + ["symbol fixed effects"],
    "primary_1": "thin: MAE_60 | C3_flow beyond the baseline; Clark-West one-sided p and 95% date-block bootstrap CI of dR2",
    "primary_2": "thin: dR2(C3_flow) - dR2(C3_placebo), each beyond the same baseline on the same rows; paired 95% date-block "
                 "bootstrap CI; p = share of bootstrap draws <= 0",
    "success": "fixed-sequence testing, which controls the familywise error at 0.05: primary 1 passes if its p is below 0.05 "
               "and its 95% interval is above zero; primary 2 is tested only if primary 1 passes, and passes if its p is below "
               "0.05 and its 95% interval is above zero (beating a placebo is informative only if the real statistic has content)",
    "secondary": ["thin: S60 beyond the baseline", "thin: C3_placebo beyond the baseline (predicted: no gain)",
                  "thin: VPIN beyond the baseline", "thin: C3_flow beyond the baseline plus VPIN",
                  "mid control: C3_flow beyond the baseline"],
    "inference": "all thin-pair candidates are evaluated on the same rows (hours where C3_flow, C3_placebo, S60 and VPIN all exist) and the same 2,000 date-block bootstrap draws; Clark-West with 6 Newey-West lags; secondary Holm-adjusted",
    "runs": "C6 is run once; every run is counted in prereg/test_set_unlocks_p17.json",
    "not_tested": "no guard test on this venue (a certified operator needs three extra days per evaluation day)",
}
spec17 = json.dumps(PREREG_P17, indent=2, sort_keys=True); P17_HASH = hashlib.sha256(spec17.encode()).hexdigest()
p17_path = os.path.join(PREREG, "P17_new_venue.json")
if not os.path.exists(p17_path):
    open(p17_path, "w").write(spec17); print("pre-registration written:", p17_path)
    if IN_COLAB:
        from google.colab import files
        files.download(p17_path)
elif hashlib.sha256(open(p17_path).read().encode()).hexdigest() != P17_HASH:
    raise RuntimeError("The spec differs from the registered file. Do not edit the spec after registering it.")
print("spec SHA-256:", P17_HASH)
