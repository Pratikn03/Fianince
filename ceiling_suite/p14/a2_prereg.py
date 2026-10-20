# ============================================================================
# CELL A2 — PRE-REGISTRATION (before any intraday data are downloaded). E-mail P14_us_equities.json to yourself.
# ============================================================================
cal = aget(f"{TRADE}/calendar", {"start": "2023-01-01", "end": "2026-09-30"})
TD = sorted(c["date"] for c in cal if isinstance(c, dict) and c.get("open") == "09:30" and c.get("close") == "16:00")
def first_on_or_after(days_of_month, start, end):
    out = []
    for m in pd.period_range(start, end, freq="M"):
        for dm in days_of_month:
            tgt = f"{m}-{dm:02d}"; nxt = [d for d in TD if d >= tgt and d[:7] == str(m)]
            if nxt:
                out.append(nxt[0])
    return sorted(set(out))
US_TRAIN = first_on_or_after((10, 24), "2023-01", "2024-12")
US_TEST = first_on_or_after((6, 20), "2025-01", "2026-09")
PREREG_P14 = {
    "question": "Regulated market: in thin US common stocks, does the depth-free amplification margin C3_flow forecast the next "
                "hour's maximum adverse excursion beyond volatility forecasts and price impact?",
    "data": "Alpaca market-data API, consolidated (SIP) trades, regular session 09:30-16:00 ET on full trading days; minute bars of "
            "last trade price, tick-rule signed dollar flow, dollar volume; a day is valid if >= 80% of minutes have a trade",
    "universe": {"thin": US_THIN, "mid_control": US_THICK, "rule": "June 2024 daily bars: thin = price $5-100 and median dollar "
                 "volume $2M-$10M (40 drawn, seed); mid control = price $5-500 and median dollar volume $50M-$200M (10 drawn)"},
    "days": {"train": US_TRAIN, "test": US_TEST},
    "inclusion": "a symbol enters if it has >= 30 valid training days and >= 25 valid test days; tickers listed in 2026 only "
                 "(delisted stocks are not in the asset list), which we report as a survivorship limitation",
    "unit": "symbol x forecast time t in {120, 180, 240, 300} minutes after the open; features from minutes [t-120, t); outcome "
            "MAE over (t, t+60] in basis points",
    "candidate": "C3_flow = kappa^2 eta q - (1-a) kappa from dp = kappa u - (1-a) x_lag and u = (1-eta) u_lag + eta q x_lag, "
                 "x = log price minus EMA(30 minutes), u = signed flow over the symbol's median absolute training-minute flow",
    "baseline": ["rv_60", "rv_120", "abs_ret_60", "flow_imb_60", "log_vol_60", "kappa_hat", "kappa_sq", "kyle_lam", "amihud_60",
                 "rv_15", "rv_day", "ewma_vol", "mae_lag60", "time-of-day dummies", "symbol fixed effects"],
    "primary": {"sample": "thin", "success": "Clark-West one-sided p < 0.05 AND 95% date-block bootstrap CI of dR2 above 0"},
    "secondary": ["thin: MAE | S60 (summed |response| of the depth-free model, 60 minutes)", "thin: MAE | term_momentum",
                  "thin: MAE | term_reversion", "mid control: MAE | C3_flow (predicted: little or no effect)"],
    "inference": "Clark-West (Newey-West 6 lags); 2,000 date-block bootstrap draws; secondary Holm-adjusted",
    "runs": "A5 is run once; every run is counted in prereg/test_set_unlocks_p14.json",
    "relation": "Fifth venue-level test of the thin-book result; first in a regulated market",
}
spec14 = json.dumps(PREREG_P14, indent=2, sort_keys=True); P14_HASH = hashlib.sha256(spec14.encode()).hexdigest()
p14_path = os.path.join(PREREG, "P14_us_equities.json")
if not os.path.exists(p14_path):
    open(p14_path, "w").write(spec14); print("pre-registration written:", p14_path)
    if IN_COLAB:
        from google.colab import files
        files.download(p14_path)
elif hashlib.sha256(open(p14_path).read().encode()).hexdigest() != P14_HASH:
    raise RuntimeError("The spec differs from the registered file. Do not edit the spec after registering it.")
print("spec SHA-256:", P14_HASH, "| train days", len(US_TRAIN), "| test days", len(US_TEST))
