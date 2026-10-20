# ============================================================================
# CELL C2 — UNIVERSE (daily candles only; no intraday data). About 3-5 minutes; after a restart it reloads instantly.
# All USD spot pairs listed and trading on Coinbase, excluding stablecoins and wrapped/staked tokens, that already
# traded in December 2023. Liquidity from June 2024 daily candles (a training-period month):
#   thin = median daily dollar volume $0.5M-$5M;  mid control = $15M-$50M.
# Up to 20 thin and 4 mid pairs are drawn with a fixed seed. No trade data have been downloaded at this point.
# ============================================================================
def candles_daily(pid, start, end):
    c = api(f"/products/{pid}/candles", {"granularity": 86400, "start": start, "end": end})
    if not c:
        return pd.DataFrame(columns=["time", "low", "high", "open", "close", "volume"])
    return pd.DataFrame(c, columns=["time", "low", "high", "open", "close", "volume"])

_u = os.path.join(RESULTS, "C2_universe.json")
if os.path.exists(_u):                                  # after a restart: reuse the universe fixed earlier
    _m = json.load(open(_u))["metrics"]
    THIN17, MID17, OLDER["param"] = _m["thin"], _m["mid"], _m["pagination_param"]
    print("reloaded the universe fixed earlier")
else:
    prods = api("/products")
    cands = sorted(p["id"] for p in prods if p.get("quote_currency") == "USD" and p.get("status") == "online"
                   and not p.get("trading_disabled", False) and p.get("base_currency") not in STABLE)
    print(len(cands), "USD pairs")
    LIQ = {}
    for i, pid in enumerate(cands):
        dec = candles_daily(pid, "2023-12-01T00:00:00Z", "2023-12-31T00:00:00Z")
        jun = candles_daily(pid, "2024-06-01T00:00:00Z", "2024-06-30T00:00:00Z")
        if len(dec) >= 20 and len(jun) >= 25:
            LIQ[pid] = float(np.median(jun["volume"].astype(float) * jun["close"].astype(float)) / 1e6)
        if i % 50 == 0:
            print(f"   {i}/{len(cands)}")
    THIN_POOL = sorted(s for s, v in LIQ.items() if 0.5 <= v <= 5.0)
    MID_POOL = sorted(s for s, v in LIQ.items() if 15.0 <= v <= 50.0)
    R = rng(17)
    THIN17 = sorted(R.choice(THIN_POOL, min(20, len(THIN_POOL)), replace=False).tolist())
    MID17 = sorted(R.choice(MID_POOL, min(4, len(MID_POOL)), replace=False).tolist())
    check_pagination(THIN17[0])
    record("C2_universe", None, "audit", {"n_usd_pairs": len(cands), "eligible": len(LIQ), "liquidity_musd_june2024": LIQ,
           "thin_pool": THIN_POOL, "mid_pool": MID_POOL, "thin": THIN17, "mid": MID17, "pagination_param": OLDER["param"]})
print("pagination: older trades via", OLDER["param"])
print("thin:", THIN17); print("mid:", MID17)
