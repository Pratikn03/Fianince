# ============================================================================
# CELL C3 — DOWNLOAD AND CHECK DATA (no estimate is computed here)
# ============================================================================
assert hashlib.sha256(open(p11_path).read().encode()).hexdigest() == P11_HASH, "run C2 first"
COVER = {}
for mkt in MARKETS:
    try:
        cot = get_cot(mkt); D = weekly_panel(mkt)
        COVER[mkt] = {"market_name": str(cot["market_name"].iloc[-1]), "reports": len(cot),
                      "first_report": str(cot["date"].iloc[0].date()), "usable_weeks": len(D)}
    except Exception as e:
        COVER[mkt] = {"error": repr(e)[:200], "usable_weeks": 0}
    print(mkt, COVER[mkt])
INCLUDED = [m for m in MARKETS if COVER[m].get("usable_weeks", 0) >= 150]
print("included markets:", INCLUDED)
record("C3_cot_data", None, "audit", {"coverage": COVER, "included": INCLUDED})
