# ============================================================================
# Part 11R: post hoc robustness checks for Paper 1 Table tab:cot (approved by the author on 2026-10-30).
#
# The registered CFTC test (prereg/P11_cot.json, run once on 2026-10-27) stays the primary result. This script reruns
# the SAME estimators with three changes, each reported separately and never used to re-score the registered test:
#   R1  CME front-month futures prices for the six markets that used spot, index or yield prices
#       (BTC=F, ETH=F, ES=F, ZN=F, 6E=F, 6J=F; crude oil and natural gas already used futures);
#   R2  R1 with contract-roll weeks removed (calendar rule below, fixed before any result was seen);
#   R3  moving-block bootstrap with 26- and 52-week blocks, for the registered prices and for the futures prices.
# Everything else (COT data, end date, classes, regressions, 2,000 draws, seeds) is as registered.
#
# Colab:  !git clone https://github.com/Pratikn03/Fianince.git
#         %cd Fianince/ceiling_suite/p11
#         %run robustness_cot.py
# Output: <BASE>/results/C4R_cot_robustness.json  (BASE = /content/drive/MyDrive/ceiling_suite in Colab)
# ============================================================================
import os, json, copy, datetime
HERE = os.path.dirname(os.path.abspath(__file__)) if "__file__" in globals() else os.getcwd()
exec(open(os.path.join(HERE, "c0_setup.py")).read())        # MARKETS, END_DATE, SEED, record(), caches
exec(open(os.path.join(HERE, "c1_functions.py")).read())    # get_cot, weekly_panel, analyse, ...
REGISTERED = copy.deepcopy(MARKETS)
FUTURES = {"BTC": "BTC=F", "ETH": "ETH=F", "ES": "ES=F", "TY": "ZN=F", "EUR": "6E=F", "JPY": "6J=F"}


def use_prices(kind):
    for m in MARKETS:
        MARKETS[m] = copy.deepcopy(REGISTERED[m])
        if kind == "futures" and m in FUTURES:
            MARKETS[m]["price"] = ("yahoo", FUTURES[m])


def third_friday(y, mo):
    d = datetime.date(y, mo, 15)
    return d + datetime.timedelta(days=(4 - d.weekday()) % 7)


def last_friday(y, mo):
    d = datetime.date(y + (mo == 12), mo % 12 + 1, 1) - datetime.timedelta(days=1)
    return d - datetime.timedelta(days=(d.weekday() - 4) % 7)


def roll_days(mkt, years):
    """Calendar roll windows: equity-index and FX futures, the 9 days up to and including the third Friday of
    Mar/Jun/Sep/Dec; Treasury futures, the last 7 days of Feb/May/Aug/Nov; CME Bitcoin and Ether, the 5 days up to and
    including the last Friday of each month (expiry week). Crude oil and natural gas are not changed by R2."""
    out = set()
    for y in years:
        if mkt in ("ES", "EUR", "JPY"):
            for mo in (3, 6, 9, 12):
                f = third_friday(y, mo); out |= {f - datetime.timedelta(days=k) for k in range(9)}
        elif mkt == "TY":
            for mo in (2, 5, 8, 11):
                e = datetime.date(y, mo + 1, 1) - datetime.timedelta(days=1)
                out |= {e - datetime.timedelta(days=k) for k in range(7)}
        elif mkt in ("BTC", "ETH"):
            for mo in range(1, 13):
                f = last_friday(y, mo); out |= {f - datetime.timedelta(days=k) for k in range(5)}
    return out


_weekly_panel_full = weekly_panel


def run(mkt, block=13, drop_rolls=False):
    D = _weekly_panel_full(mkt)
    dropped = 0
    if drop_rolls and mkt in FUTURES:
        rd = roll_days(mkt, range(D["date"].dt.year.min() - 1, D["date"].dt.year.max() + 1))
        keep = [not any((d.date() - datetime.timedelta(days=k)) in rd for k in range(7)) for d in D["date"]]
        dropped = int(len(D) - sum(keep))
        D = D[keep].reset_index(drop=True)
    globals()["weekly_panel"] = lambda m, _D=D: _D           # analyse() reads the panel through weekly_panel(mkt)
    try:
        out, _ = analyse(mkt, B=int(os.environ.get("ROBUST_B", 2000)), block=block)
    finally:
        globals()["weekly_panel"] = _weekly_panel_full
    out["weeks_dropped_for_roll"] = dropped
    return out


def counts(res):
    h1 = h2 = h3 = 0; w_sign = {}
    for m, a in res.items():
        h1 += bool((a["tagged_width_fast"] < 0.25) and all(a["price_only"][k][1] - a["price_only"][k][0] > 0.25 for k in ("r1_ci", "r2_ci")))
        h2 += bool(a["fast"]["w_ci"][0] > 0)
        h3 += bool(a["fast_minus_slow_r"]["ci"][1] < 0)
        lo, hi = a["fast"]["w_ci"]; w_sign[m] = "+" if lo > 0 else ("-" if hi < 0 else "0")
    return {"H1": h1, "H2": h2, "H3": h3, "of": len(res), "w_fast_sign": w_sign}


VARIANTS = [("registered_prices_block13_rerun", "registered", 13, False),
            ("registered_prices_block26", "registered", 26, False),
            ("registered_prices_block52", "registered", 52, False),
            ("R1_futures_block13", "futures", 13, False),
            ("R1_futures_block26", "futures", 26, False),
            ("R1_futures_block52", "futures", 52, False),
            ("R2_futures_no_roll_weeks_block13", "futures", 13, True)]
out = {"status": "post hoc robustness checks; the registered result (H1 8/8, H2 4/8, H3 6/8) is unchanged",
       "registered_spec_sha256": hashlib.sha256(open(os.path.join(HERE, "..", "p11res", "prereg", "P11_cot.json"), "rb").read()).hexdigest(),
       "futures_tickers": FUTURES, "end_date": END_DATE, "variants": {}}
for name, prices, block, drop in VARIANTS:
    use_prices(prices)
    res = {}
    for mkt in MARKETS:
        try:
            res[mkt] = run(mkt, block=block, drop_rolls=drop)
        except Exception as e:                                # a missing price series is reported, not hidden
            res[mkt] = {"error": repr(e)[:300]}
    ok = {m: a for m, a in res.items() if "error" not in a}
    out["variants"][name] = {"by_market": res, "counts": counts(ok), "errors": [m for m in res if m not in ok]}
    print(name, out["variants"][name]["counts"], "errors:", out["variants"][name]["errors"])
use_prices("registered")
record("C4R_cot_robustness", None, "robustness", out,
       note="Post hoc, approved 2026-10-30. Does not re-score the registered test.")
