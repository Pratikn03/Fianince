"""Post hoc (not pre-specified): price data needed to match the precision of the CFTC class reports.

Reads the registered results (C4: original 8 markets; C6R: 12 new markets) and, for each market, converts the
width ratio R = (price-only rate-interval width) / (tagged rate-interval width) into the factor R^2 by which the
price-only sample would have to grow to match the tagged precision if both intervals shrink as T^(-1/2), and into
years of weekly data. The price-only intervals are truncated by the estimation grid ([0, 0.99]), so R and R^2 are
lower bounds. Writes p11res/results/C7_data_equivalence.json."""
import json, os
import numpy as np
HERE = os.path.dirname(os.path.abspath(__file__))
RES = os.path.join(HERE, "..", "p11res", "results")
c4 = json.load(open(os.path.join(RES, "C4_cot_disclosure.json")))["metrics"]["by_market"]
c6p = os.path.join(RES, "C6R_cot_replication.json")
if os.path.exists(c6p):
    bm = json.load(open(c6p))["metrics"]["by_market"]
    c6 = {"weeks": {m: v["weeks"] for m, v in bm.items()}, "width_ratio": {m: v["width_ratio"] for m, v in bm.items()}}
    src6 = "C6R_cot_replication.json"
else:
    c6 = json.load(open(os.path.join(RES, "C6R_extract.json"))); src6 = "C6R_extract.json"
rows = []
for m, v in c4.items():
    rows.append({"market": m, "set": "original", "weeks": v["weeks"], "width_ratio": v["width_ratio"]})
for m in c6["width_ratio"]:
    rows.append({"market": m, "set": "new", "weeks": c6["weeks"][m], "width_ratio": c6["width_ratio"][m]})
for r in rows:
    r["factor"] = r["width_ratio"] ** 2
    r["years_equivalent"] = r["weeks"] * r["factor"] / 52
R = np.array([r["width_ratio"] for r in rows]); F = R ** 2; Y = np.array([r["years_equivalent"] for r in rows])
out = {"kind": "post hoc calculation from registered results (not a test)", "sources": ["C4_cot_disclosure.json", src6],
       "rows": rows, "median_width_ratio": float(np.median(R)), "range_width_ratio": [float(R.min()), float(R.max())],
       "median_factor": float(np.median(F)), "range_factor": [float(F.min()), float(F.max())],
       "median_years": float(np.median(Y)), "range_years": [float(Y.min()), float(Y.max())]}
json.dump(out, open(os.path.join(RES, "C7_data_equivalence.json"), "w"), indent=2)
print(json.dumps({k: v for k, v in out.items() if k != "rows"}, indent=1))
