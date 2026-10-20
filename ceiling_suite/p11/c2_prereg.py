# ============================================================================
# CELL C2 — PRE-REGISTRATION (before any COT or price data are downloaded). E-mail P11_cot.json to yourself.
# ============================================================================
PREREG_P11 = {
    "question": "Does legally mandated class-tagged disclosure (CFTC Commitments of Traders) pin down trader-class memory "
                "rates that prices alone leave unrestricted, and do the classes behave as the cohort model predicts?",
    "markets": {k: {"code": v["code"], "report": v["report"], "price": list(v["price"])} for k, v in MARKETS.items()},
    "classes": {"TFF": "fast = leveraged funds, slow = asset managers, dealer = dealers",
                "DIS": "fast = managed money, slow = producer/merchant, dealer = swap dealers"},
    "data": "CFTC public reporting API (futures-only reports), all weekly reports through " + END_DATE +
            "; prices: Binance spot daily close (BTC, ETH); Yahoo Finance daily close for the others: S&P 500 index, 10-year yield "
            "(enters as minus the change), EUR/USD, USD/JPY (inverted), and front-month crude-oil and natural-gas futures. "
            "Class position n = (long - short) / open interest; weekly return from the last price on or before the report date "
            "(at most 4 days old); only consecutive weekly reports.",
    "inclusion": "a market enters if it has at least 150 usable weeks",
    "tagged_model": "n_t = alpha + r * n_{t-1} + w * ret_t + e_t by OLS, for each class",
    "price_only_model": "weekly returns on 12 own lags (OLS), then a two-exponential kernel fitted on a 0.02 grid of rates in [0, 0.99]",
    "inference": "moving-block bootstrap, 13-week blocks, 2,000 draws; 95% percentile intervals",
    "H1_primary": "disclosure precision: the fast-class rate interval is narrower than 0.25 AND both price-only rate intervals are "
                  "wider than 0.25; success if this holds in at least 75% of included markets",
    "H2": "trend following: the fast-class response to returns w is positive with interval above 0, in at least 75% of markets",
    "H3": "classes differ: the fast class has a shorter memory than the slow class (interval of r_fast - r_slow below 0), "
          "in at least half of the markets",
    "runs": "C4 is run once; every run is counted in prereg/test_set_unlocks_p11.json",
    "relation": "Paper 1 Table tab:disc (Binance long/short ratios, Part 6) is the first disclosure regime; this is the second.",
}
spec11 = json.dumps(PREREG_P11, indent=2, sort_keys=True); P11_HASH = hashlib.sha256(spec11.encode()).hexdigest()
p11_path = os.path.join(PREREG, "P11_cot.json")
if not os.path.exists(p11_path):
    open(p11_path, "w").write(spec11); print("pre-registration written:", p11_path)
    if IN_COLAB:
        from google.colab import files
        files.download(p11_path)
elif hashlib.sha256(open(p11_path).read().encode()).hexdigest() != P11_HASH:
    raise RuntimeError("The spec differs from the registered file. Do not edit the spec after registering it.")
print("spec SHA-256:", P11_HASH)
