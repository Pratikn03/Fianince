"""Runs the P1M notebook's analysis code end to end on simulated TWSE responses with real 2013-2016 calendar dates,
the E1 and E2 T86 schema eras at their real switch date, and nonzero flows for all three classes. Checks: the run
completes, every run is present, the results file is written, and a rerun loads it without recomputing.
Simulated data only; no download. Speed: fewer bootstrap draws and random starts than the protocol."""
import datetime
import gzip
import json
import os
import tempfile
import time
import zipfile

import numpy as np

import make_p1m_notebook as mk
import p1m_core as pm
import p1t_executor as ex
import validate_executor as v


def fake(N=30, seed=5):
    rng = np.random.default_rng(seed)
    d0, d1 = datetime.date(2013, 1, 2), datetime.date(2016, 12, 30)
    cal = [d0 + datetime.timedelta(k) for k in range((d1 - d0).days + 1)]
    cal = [d.strftime("%Y%m%d") for d in cal if d.weekday() < 5]
    cal = [d for d in cal if rng.random() > 0.05 or d in ("20130102", "20161230")]
    T = len(cal)
    logp, mkt, uF, uO, vol = v.simulate_market(N, T, 0.1, seed)
    uD = np.zeros_like(uF)
    for t in range(1, T):
        uD[:, t] = 0.3 * uD[:, t - 1] + 0.2 * rng.standard_normal(N)
    close = np.round(np.exp(logp), 2)
    codes = [f"{1101 + i}" for i in range(N)]
    store = {}
    for t, d in enumerate(cal):
        era = 0 if d < "20141201" else 1
        fields = v.ERA_FIELDS[era]
        t86 = {"fields": fields, "data": []}; q = []
        for i, c in enumerate(codes):
            fF, fO, fD = (int(round(z[i, t] * vol[i, t] / 10)) for z in (uF, uO, uD))
            row = [c, "x"] + ["0"] * (len(fields) - 2)
            row[fields.index("外資買賣超股數")] = f"{fF:,}"
            row[fields.index("投信買賣超股數")] = f"{fO:,}"
            row[fields.index("自營商買賣超股數")] = f"{fD:,}"
            if era == 1:
                own = int(round(0.7 * fD))
                row[fields.index("自營商買賣超股數(自行買賣)")] = f"{own:,}"
                row[fields.index("自營商買賣超股數(避險)")] = f"{fD - own:,}"
            row[fields.index("三大法人買賣超股數")] = f"{fF + fO + fD:,}"
            t86["data"].append(row)
            prev = close[i, t - 1] if t > 0 else close[i, t]
            sign = "<p style= color:red>+</p>" if close[i, t] >= prev else "<p style= color:green>-</p>"
            q.append([c, "x", f"{int(vol[i, t]):,}", "1", f"{int(vol[i, t] * close[i, t]):,}", "0", "0", "0",
                      f"{close[i, t]:.2f}", sign, "0", "0", "0", "0", "0", "0"])
        mi = {"tables": [{"title": "價格指數(臺灣證券交易所)", "fields": ["指數", "收盤指數"],
                          "data": [[ex.INDEX_NAME, f"{10000 * np.exp(mkt[t]):.2f}"]]},
                         {"title": "每日收盤行情(全部(不含權證、牛熊證、可展延牛熊證))", "fields": v.FIELDS_Q, "data": q}]}
        store[("T86", d)] = t86; store[("MI", d)] = mi
    return cal, store


def run(cal, store, root):
    meas = pm.measure
    pm.measure = lambda *a, **k: meas(*a, **{**k, "B_": 49, "n_random": 3})
    g = {"np": np, "json": json, "os": os, "zipfile": zipfile, "gzip": gzip, "time": time, "ex": ex, "pm": pm,
         "days": cal, "ev": set(), "ROOT": root, "DEV_END": "20161230", "EXECUTOR_SHA256": "test", "CORE_SHA256": "test",
         "now": lambda: datetime.datetime.now(datetime.timezone.utc).isoformat(), "load": lambda sub, d: store[(sub, d)]}
    cwd = os.getcwd(); work = tempfile.mkdtemp(); os.chdir(work)
    try:
        exec(mk.ANALYSIS, g)
    finally:
        os.chdir(cwd); pm.measure = meas
    return g


if __name__ == "__main__":
    t0 = time.time()
    cal, store = fake()
    out = {"n_days": len(cal)}
    with tempfile.TemporaryDirectory() as root:
        g = run(cal, store, root)
        R = g["results"]
        out["runs"] = sorted(R["runs"])
        out["check_runs"] = out["runs"] == sorted(["primary", "dealer_own_account", "same_day_timing", "one_price_lag"])
        out["check_saved"] = os.path.exists(os.path.join(root, "p1m_results.json")) and os.path.exists(os.path.join(root, "p1m_results.zip"))
        stamp = R["computed_utc"]
        g2 = run(cal, store, root)
        out["check_rerun_loads"] = g2["results"]["computed_utc"] == stamp
        prim = R["runs"]["primary"]
        out["primary_theta"] = prim["theta"]
        out["primary_Q1"] = {k: prim["Q1"][k] for k in ("price_rate_per_stock_day", "tag_rate_per_stock_day",
                                                      "years_prices_one_stock_at_least")}
        out["primary_ranges"] = {k: [prim["Q2Q3_whole_panel"][k]["min"], prim["Q2Q3_whole_panel"][k]["max"]] for k in ("H_Foreign", "U")}
        out["dealer_own_rows"] = prim and R["runs"]["dealer_own_account"]["equations"]["Dealers"]["rows"]
        out["primary_dealer_rows"] = prim["equations"]["Dealers"]["rows"]
        out["check_dealer_own_fewer_rows"] = out["dealer_own_rows"] < out["primary_dealer_rows"]
        out["check_finite"] = all(np.isfinite([prim["Q1"]["price_rate_per_stock_day"], prim["Q1"]["tag_rate_per_stock_day"],
                                               prim["Q2Q3_whole_panel"]["U"]["min"], prim["Q2Q3_whole_panel"]["U"]["max"]]))
    mk.build("/tmp/p1m_nb_check.ipynb")
    nb = json.load(open("/tmp/p1m_nb_check.ipynb"))
    compile(nb["cells"][1]["source"], "cell", "exec")
    out["check_notebook_compiles"] = True
    out["seconds"] = time.time() - t0
    out["all_pass"] = all(v for k, v in out.items() if k.startswith("check_"))
    print(json.dumps(out, indent=1, default=float))
    json.dump(out, open("test_p1m_notebook_results.json", "w"), indent=1, default=float)
