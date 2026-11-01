# ============================================================================
# Post hoc check (not a pre-specified test): do the CFTC tagged intervals shrink at the root-T rate that the
# "years of price data" calculation (Table tab:dataequiv) assumes?
#
# For each of the 20 markets of the registered CFTC tests (8 original, 12 replication), the registered tagged
# estimator and bootstrap (c1_functions.py: tagged_fit, block_index; 13-week blocks, 2,000 draws) are run on the
# first half of the sample and on the full sample. Root-T shrinkage predicts width(half) / width(full) = sqrt(2) =
# 1.41. Data already opened by the registered tests; nothing here re-scores them.
#
# Colab:  !git clone https://github.com/Pratikn03/Fianince.git
#         %cd Fianince/ceiling_suite/p11
#         %run sqrtT_check.py
# Output: <BASE>/results/C8_sqrtT_check.json. Dry run (no network): SQRTT_DRYRUN=1.
# ============================================================================
import os, json, time
HERE = os.path.dirname(os.path.abspath(__file__)) if "__file__" in globals() else os.getcwd()
DRY = os.environ.get("SQRTT_DRYRUN") == "1"
_setup = open(os.path.join(HERE, "c0_setup.py")).read()
if DRY:
    _setup = _setup[:_setup.index('code, _ = _http(SOCRATA["TFF"]')]
exec(_setup)
exec(open(os.path.join(HERE, "c1_functions.py")).read())
ORIG = dict(MARKETS)
ORIG_END = END_DATE
REP = json.load(open(os.path.join(HERE, "prereg_replication", "P11R_cot_replication.json")))
NEW = {k: {"code": v["code"], "report": v["report"], "price": tuple(v["price"])} for k, v in REP["markets"].items()}

if DRY:
    import numpy as _np, pandas as _pd
    def get_cot(mkt):
        R = _np.random.default_rng(sum(map(ord, mkt)))
        d = _pd.date_range("2006-06-20", "2026-10-27", freq="7D")
        out = _pd.DataFrame({"date": d, "oi": 1e5, "market_name": mkt})
        for c, r in (("fast", 0.9), ("slow", 0.97), ("dealer", 0.9)):
            n = _np.zeros(len(d))
            for t in range(1, len(d)):
                n[t] = r * n[t - 1] + R.normal(0, 0.02)
            out[f"{c}_long"] = 5e4 * (1 + n); out[f"{c}_short"] = 5e4 * (1 - n)
        return out
    def get_yahoo(ticker):
        R = _np.random.default_rng(len(ticker)); d = _pd.bdate_range("2005-01-01", "2026-10-27")
        return _pd.Series(_np.exp(_np.cumsum(R.normal(0, 0.01, len(d)))), index=d)
    def get_binance_daily(sym):
        return get_yahoo(sym)

def tagged_width(D, seed, B=2000, block=13):
    R = np.random.default_rng(seed); T = len(D); rs = []
    for _ in range(200 if DRY else B):
        Db = D.iloc[block_index(T, block, R)].reset_index(drop=True)
        rs.append(tagged_fit(Db, "fast")[0])
    lo, hi = np.quantile(rs, [0.025, 0.975])
    return float(hi - lo)

out = {}
for group, mk, end in (("original", ORIG, ORIG_END), ("replication", NEW, REP["end_date"])):
    MARKETS = mk; END_DATE = end
    for m in mk:
        t0 = time.time()
        D = weekly_panel(m); T = len(D); H = D.iloc[: T // 2].reset_index(drop=True)
        seed = 20261101 + sum(map(ord, m))
        wf, wh = tagged_width(D, seed), tagged_width(H, seed + 1)
        out[m] = {"group": group, "weeks_full": T, "weeks_half": len(H), "width_full": wf, "width_half": wh,
                  "ratio_half_over_full": wh / wf if wf > 0 else None}
        print(f"{m}: weeks {T} | width half {wh:.4f} full {wf:.4f} | ratio {wh / wf:.2f} (root-T: 1.41) "
              f"({time.time() - t0:.0f}s)")
ratios = np.array([v["ratio_half_over_full"] for v in out.values() if v["ratio_half_over_full"]])
summary = {"median_ratio": float(np.median(ratios)), "range": [float(ratios.min()), float(ratios.max())],
           "share_within_1p0_to_2p0": float(np.mean((ratios >= 1.0) & (ratios <= 2.0))), "root_T_prediction": 2 ** 0.5,
           "kind": "post hoc check on data opened by the registered tests (not a test)", "dry_run": DRY}
record("C8_sqrtT_check" + ("_DRYRUN" if DRY else ""), None, "post hoc", {"summary": summary, "by_market": out},
       note="Checks the root-T assumption behind Table tab:dataequiv.")
print(json.dumps(summary, indent=1))
