# ============================================================================
# DRAFT, NOT RUN, NOT REGISTERED. Needs the author's explicit approval before it is run.
#
# Post hoc robustness check for Paper 1 Table tab:cot (Part 11, CFTC Commitments of Traders).
# The registered test (prereg/P11_cot.json, run once on 2026-10-27) used spot/index/yield prices for six markets.
# This check reruns the SAME estimators on CME front-month futures prices for those six markets
# (crude oil and natural gas already used front-month futures and are unchanged). It is reported as a check
# done after the fact; it does not replace or re-score the registered result.
#
# Run in Colab (needs network):
#   !git clone https://github.com/Pratikn03/Fianince.git && cd Fianince/ceiling_suite/p11
#   %run robustness_cme_futures_DRAFT.py
# Output: <BASE>/results/C4R_cot_cme_futures_robustness.json (copy it back to ceiling_suite/p11res/results/).
# ============================================================================
import os, json, datetime
HERE = os.path.dirname(os.path.abspath(__file__)) if "__file__" in globals() else os.getcwd()
exec(open(os.path.join(HERE, "c0_setup.py")).read())
# c0_setup.py defines MARKETS and END_DATE exactly as in the registered run; only the price source changes below.
exec(open(os.path.join(HERE, "c1_functions.py")).read())

FUTURES = {"BTC": "BTC=F", "ETH": "ETH=F", "ES": "ES=F", "TY": "ZN=F", "EUR": "6E=F", "JPY": "6J=F"}
for m, t in FUTURES.items():
    MARKETS[m] = dict(MARKETS[m]); MARKETS[m]["price"] = ("yahoo", t)                 # log price of the continuous front-month contract

def third_friday(y, mo):
    d = datetime.date(y, mo, 15)
    return d + datetime.timedelta(days=(4 - d.weekday()) % 7)

def last_friday(y, mo):
    d = datetime.date(y + (mo == 12), mo % 12 + 1, 1) - datetime.timedelta(days=1)
    return d - datetime.timedelta(days=(d.weekday() - 4) % 7)

def roll_days(mkt, years):
    """Calendar roll windows, fixed before seeing any result: equity-index and FX futures, the 8 days up to the
    third Friday of Mar/Jun/Sep/Dec; Treasury futures, the last 7 days of Feb/May/Aug/Nov; CME Bitcoin and Ether,
    3 days either side of the last Friday of each month."""
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
                f = last_friday(y, mo); out |= {f + datetime.timedelta(days=k) for k in range(-3, 4)}
    return out

def analyse_excluding_rolls(mkt, B=2000, block=13):
    D = weekly_panel(mkt)
    rd = roll_days(mkt, range(D["date"].dt.year.min() - 1, D["date"].dt.year.max() + 1))
    keep = [not any((d.date() - datetime.timedelta(days=k)) in rd for k in range(7)) for d in D["date"]]
    global weekly_panel_orig
    weekly_panel_orig = weekly_panel
    Dk = D[keep].reset_index(drop=True)
    globals()["weekly_panel"] = lambda m, _D=Dk: _D       # analyse() calls weekly_panel(mkt)
    try:
        out, _ = analyse(mkt, B=B, block=block)
    finally:
        globals()["weekly_panel"] = weekly_panel_orig
    out["weeks_dropped_for_roll"] = int(len(D) - len(Dk))
    return out

res = {"status": "post hoc robustness check, not a registered test", "registered_spec_sha256":
       hashlib.sha256(open(os.path.join(HERE, "..", "p11res", "prereg", "P11_cot.json")).read().encode()).hexdigest(),
       "futures_tickers": FUTURES, "end_date": END_DATE, "markets": {}}
for mkt in MARKETS:
    a, _ = analyse(mkt)
    entry = {"all_weeks": a}
    if mkt in FUTURES:
        entry["excluding_roll_weeks"] = analyse_excluding_rolls(mkt)
    res["markets"][mkt] = entry
    f = a["fast"]
    print(mkt, "weeks", a["weeks"], "fast r", round(f["r"], 3), f["r_ci"], "w", round(f["w"], 4), f["w_ci"],
          "ratio", a["width_ratio"])

def counts(key):
    h1 = h2 = h3 = 0
    for m, e in res["markets"].items():
        a = e.get(key, e["all_weeks"])
        h1 += (a["tagged_width_fast"] < 0.25) and all(a["price_only"][k][1] - a["price_only"][k][0] > 0.25 for k in ("r1_ci", "r2_ci"))
        h2 += a["fast"]["w_ci"][0] > 0
        h3 += a["fast_minus_slow_r"]["ci"][1] < 0
    return {"H1": int(h1), "H2": int(h2), "H3": int(h3), "of": len(res["markets"])}
res["counts_all_weeks"] = counts("all_weeks")
res["counts_excluding_roll_weeks"] = counts("excluding_roll_weeks")
res["registered_counts_for_comparison"] = {"H1": 8, "H2": 4, "H3": 6, "of": 8}
json.dump(_clean(res), open(os.path.join(RESULTS, "C4R_cot_cme_futures_robustness.json"), "w"), indent=1)
print(json.dumps({k: res[k] for k in ("counts_all_weeks", "counts_excluding_roll_weeks", "registered_counts_for_comparison")}, indent=1))
