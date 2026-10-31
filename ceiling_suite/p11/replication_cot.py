# ============================================================================
# P11R: pre-specified replication of the CFTC disclosure test on twelve new markets (Paper 1).
# Specification: prereg_replication/P11R_cot_replication.json (SHA-256 checked below; committed before the run).
#
# Colab:  !git clone https://github.com/Pratikn03/Fianince.git
#         %cd Fianince/ceiling_suite/p11
#         %run replication_cot.py
# Output: <BASE>/results/C6R_cot_replication.json, <BASE>/prereg/P11R_unlocks.json. Run it once.
# Dry run on synthetic data (no network, no unlock counter): set the environment variable P11R_DRYRUN=1.
# ============================================================================
import os, json, time, hashlib
HERE = os.path.dirname(os.path.abspath(__file__)) if "__file__" in globals() else os.getcwd()
DRY = os.environ.get("P11R_DRYRUN") == "1"
_setup = open(os.path.join(HERE, "c0_setup.py")).read()
if DRY:                                    # keep the registered definitions, skip the network checks
    _setup = _setup[:_setup.index('code, _ = _http(SOCRATA["TFF"]')]
exec(_setup)                               # record(), caches, CLASSES, SOCRATA (registered setup)
exec(open(os.path.join(HERE, "c1_functions.py")).read())    # get_cot, weekly_panel, analyse (registered, unchanged)

SPEC_PATH = os.path.join(HERE, "prereg_replication", "P11R_cot_replication.json")
SPEC_SHA256 = "591e71c9e13bda6d68b899337a89de3e9059acc510bfe0f7314b92596c041fe2"
assert hashlib.sha256(open(SPEC_PATH).read().encode()).hexdigest() == SPEC_SHA256, "specification changed"
SPEC = json.load(open(SPEC_PATH))
MARKETS = {k: {"code": v["code"], "report": v["report"], "price": tuple(v["price"])} for k, v in SPEC["markets"].items()}
END_DATE = SPEC["end_date"]

if DRY:                                    # synthetic COT and price data with the registered column layout
    import numpy as _np, pandas as _pd
    def get_cot(mkt):
        R = _np.random.default_rng(sum(map(ord, mkt)))
        d = _pd.date_range("2010-01-05", END_DATE, freq="7D")
        out = _pd.DataFrame({"date": d, "oi": 1e5, "market_name": SPEC["markets"][mkt]["name_must_contain"] + " - TEST"})
        for c, r in (("fast", 0.8), ("slow", 0.97), ("dealer", 0.9)):
            n = _np.zeros(len(d))
            for t in range(1, len(d)):
                n[t] = r * n[t - 1] + R.normal(0, 0.02)
            out[f"{c}_long"] = 5e4 * (1 + n); out[f"{c}_short"] = 5e4 * (1 - n)
        return out
    def get_yahoo(ticker):
        R = _np.random.default_rng(len(ticker))
        d = _pd.bdate_range("2009-01-01", END_DATE)
        return _pd.Series(_np.exp(_np.cumsum(R.normal(0, 0.01, len(d)))), index=d)

unlock = os.path.join(PREREG, "P11R_unlocks.json")
COVER, INCLUDED = {}, []
for mkt in MARKETS:                        # data stage: coverage and market-name check, no estimates
    try:
        cot = get_cot(mkt); D = weekly_panel(mkt)
        name = str(cot["market_name"].iloc[-1])
        ok = len(D) >= 150 and SPEC["markets"][mkt]["name_must_contain"] in name.upper()
        COVER[mkt] = {"market_name": name, "reports": len(cot), "usable_weeks": len(D), "included": bool(ok)}
    except Exception as e:
        COVER[mkt] = {"error": repr(e)[:200], "usable_weeks": 0, "included": False}
    if COVER[mkt]["included"]:
        INCLUDED.append(mkt)
    print(mkt, COVER[mkt])
print("included:", INCLUDED)
assert INCLUDED, "no market passed the data rule; send the console output to Claude"

if not DRY:
    n_runs = json.load(open(unlock))["n"] + 1 if os.path.exists(unlock) else 1
    json.dump({"n": n_runs, "utc": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()), "spec_sha256": SPEC_SHA256},
              open(unlock, "w"), indent=2)
else:
    n_runs = 0
print("unlock count:", n_runs, "(should be 1)" if not DRY else "(dry run: not counted)")

RES = {}
for mkt in INCLUDED:
    t0 = time.time(); RES[mkt], _ = analyse(mkt, B=200 if DRY else 2000)
    r = RES[mkt]
    print(f"{mkt}: {r['weeks']} wks | fast r={r['fast']['r']:.3f} {np.round(r['fast']['r_ci'],3)} w={r['fast']['w']:.3f} "
          f"{np.round(r['fast']['w_ci'],3)} | fast-slow {np.round(r['fast_minus_slow_r']['ci'],3)} | "
          f"price-only width {r['price_only_width']:.2f} vs tagged {r['tagged_width_fast']:.3f} ({time.time()-t0:.0f}s)")
h1 = {m: bool(RES[m]["tagged_width_fast"] < 0.25 and
              all(RES[m]["price_only"][k][1] - RES[m]["price_only"][k][0] > 0.25 for k in ("r1_ci", "r2_ci"))) for m in RES}
h2 = {m: bool(RES[m]["fast"]["w_ci"][0] > 0) for m in RES}
h3 = {m: bool(RES[m]["fast_minus_slow_r"]["ci"][1] < 0) for m in RES}
n = len(RES)
summary = {"H1": {"count": sum(h1.values()), "of": n, "pass": sum(h1.values()) >= 0.75 * n},
           "H2": {"count": sum(h2.values()), "of": n, "pass": sum(h2.values()) >= 0.75 * n},
           "H3": {"count": sum(h3.values()), "of": n, "pass": sum(h3.values()) >= 0.5 * n},
           "unlock_count": n_runs, "spec_sha256": SPEC_SHA256, "dry_run": DRY}
record("C6R_cot_replication" + ("_DRYRUN" if DRY else ""), summary["H1"]["pass"], "real data" if not DRY else "dry run",
       {"summary": summary, "coverage": COVER, "by_market": RES, "H1": h1, "H2": h2, "H3": h3},
       criterion=SPEC["hypotheses"]["H1_primary"])
print(json.dumps(summary, indent=1))
