# ============================================================================
# CELL A1 — UNIVERSE (fixed from June 2024 daily bars, before any intraday data are downloaded)
# Thin: common stocks priced $5-$100 with median daily dollar volume $2M-$10M in June 2024; 40 drawn with a fixed seed.
# Mid (control): median daily dollar volume $50M-$200M; 10 drawn with a fixed seed.
# ============================================================================
assets = aget(f"{TRADE}/assets", {"status": "active", "asset_class": "us_equity"})
cand = sorted(a["symbol"] for a in assets if isinstance(a, dict) and a.get("tradable") and a.get("exchange") in ("NYSE", "NASDAQ", "AMEX")
              and re.fullmatch(r"[A-Z]{1,5}", a["symbol"]))
print(len(cand), "candidate common-stock tickers")
stats_ = {}
for i in range(0, len(cand), 100):
    chunk = cand[i:i + 100]; tok = None
    while True:
        p = {"symbols": ",".join(chunk), "timeframe": "1Day", "start": "2024-06-03", "end": "2024-06-28", "feed": "sip", "adjustment": "raw", "limit": 10000}
        if tok:
            p["page_token"] = tok
        r = aget(f"{DATA}/stocks/bars", p)
        for s, bars in (r.get("bars") or {}).items():
            stats_.setdefault(s, []).extend((b["c"], b["c"] * b["v"]) for b in bars)
        tok = r.get("next_page_token")
        if not tok:
            break
med = {s: (np.median([c for c, _ in v]), np.median([dv for _, dv in v])) for s, v in stats_.items() if len(v) >= 15}
thin_pool = sorted(s for s, (c, dv) in med.items() if 5 <= c <= 100 and 2e6 <= dv <= 1e7)
thick_pool = sorted(s for s, (c, dv) in med.items() if 5 <= c <= 500 and 5e7 <= dv <= 2e8)
R_ = np.random.default_rng(SEED)
US_THIN = sorted(R_.choice(thin_pool, min(40, len(thin_pool)), replace=False).tolist()); US_THICK = sorted(R_.choice(thick_pool, min(10, len(thick_pool)), replace=False).tolist())
print("thin pool", len(thin_pool), "-> 40:", US_THIN); print("thick pool", len(thick_pool), "-> 10:", US_THICK)
record("A1_us_universe", None, "audit", {"thin": US_THIN, "thick": US_THICK, "thin_pool": len(thin_pool), "thick_pool": len(thick_pool),
       "median_price_dollarvol": {s: med[s] for s in US_THIN + US_THICK}})
