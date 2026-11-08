"""Runs the holdout notebook's analysis code (make_holdout_notebook.ANALYSIS) end to end on simulated TWSE responses
with real calendar dates 2013-2023 and the three T86 eras at their real switch dates. Checks: gate passes on clean
data and stops on an unknown schema; fit window ends 2018-12-27; the primary is computed once and a rerun loads it.
Simulated data only; no download."""
import gzip, json, os, sys, tempfile, zipfile, datetime
import numpy as np
import p1t_executor as ex
import validate_executor as v
import make_holdout_notebook as mk


def fake(N=40, w=0.1, seed=7):
    rng = np.random.default_rng(seed)
    d0, d1 = datetime.date(2013, 1, 2), datetime.date(2023, 12, 29)
    cal = [d0 + datetime.timedelta(k) for k in range((d1 - d0).days + 1)]
    cal = [d.strftime("%Y%m%d") for d in cal if d.weekday() < 5]
    cal = [d for d in cal if rng.random() > 0.055 or d in ("20130102", "20231229")]
    T = len(cal)
    logp, mkt, uF, uO, vol = v.simulate_market(N, T, w, seed)
    close = np.round(np.exp(logp), 2)
    codes = [f"{1101 + i}" for i in range(N)]
    store = {}
    for t, d in enumerate(cal):
        era = 0 if d < "20141201" else (1 if d < "20171218" else 2)
        fields = v.ERA_FIELDS[era]
        t86 = {"fields": fields, "data": []}; q = []
        for i, c in enumerate(codes):
            fF = int(round(uF[i, t] * vol[i, t] / 10)); fO = int(round(uO[i, t] * vol[i, t] / 10))
            row = [c, "x"] + ["0"] * (len(fields) - 2)
            if era == 2:
                fd = int(round(0.05 * fF))
                row[fields.index("外陸資買賣超股數(不含外資自營商)")] = f"{fF - fd:,}"
                row[fields.index("外資自營商買賣超股數")] = f"{fd:,}"
            else:
                row[fields.index("外資買賣超股數")] = f"{fF:,}"
            row[fields.index("投信買賣超股數")] = f"{fO:,}"
            row[fields.index("三大法人買賣超股數")] = f"{fF + fO:,}"
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


def run(cal, store, root, B_patch=True):
    import p1t_executor as exm
    if B_patch:   # speed only: fewer bootstrap draws in this test
        rp = exm.run_period
        exm_run = lambda *a, **k: rp(*a, **{**k, "B": 199})
        exm.run_period = exm_run
    import gzip as _g, zipfile as _z, datetime as _dt
    g = {"np": np, "json": json, "os": os, "zipfile": _z, "gzip": _g, "ex": exm, "days": cal, "ev": set(), "ROOT": root,
         "END": "20231229", "DEV_END": "20161230", "HOLDOUT_START": "20190102", "MIN_QUOTES": 10,
         "HOLD_MIN": 1150, "HOLD_MAX": 1300, "KNOWN_T86_SCHEMAS": v.ERA_FIELDS, "EXECUTOR_SHA256": "test",
         "MAN": os.path.join(root, "manifest.jsonl"),
         "now": lambda: _dt.datetime.now(_dt.timezone.utc).isoformat(), "load": lambda sub, d: store[(sub, d)]}
    cwd = os.getcwd(); work = tempfile.mkdtemp(); os.chdir(work)   # Colab: cwd /content, ROOT on Drive
    try:
        exec(mk.ANALYSIS, g)
    finally:
        os.chdir(cwd)
        if B_patch:
            exm.run_period = rp
    return g


if __name__ == "__main__":
    out = {}
    cal, store = fake()
    out["n_days"] = len(cal); out["n_holdout"] = sum(d >= "20190102" for d in cal)
    with tempfile.TemporaryDirectory() as root:
        g = run(cal, store, root)
        p = g["primary"]
        out["fit_window"] = p["fit_window"]; out["holdout_window"] = p["holdout_window"]
        out["primary_w01"] = p["primary"]
        out["fit_window_ok"] = p["fit_window"][1] == max(d for d in cal if d < "20190102" and d != max(x for x in cal if x < "20190102"))
        g2 = run(cal, store, root)
        out["rerun_loads_not_recomputes"] = g2["primary"]["computed_utc"] == p["computed_utc"]
        out["reverse_causality"] = g["res"]["diagnostics"]["reverse_causality"]
        out["stability_keys"] = sorted(g["res"]["diagnostics"]["stability"])
    with tempfile.TemporaryDirectory() as root:
        bad = dict(store); d = "20200302"
        t = dict(bad[("T86", d)]); t["fields"] = t["fields"][:-1] + ["新欄位"]; bad[("T86", d)] = t
        try:
            run(cal, bad, root); out["unknown_schema_stops_before_statistic"] = False
        except SystemExit as e:
            out["unknown_schema_stops_before_statistic"] = (not os.path.exists(os.path.join(root, "p1t_holdout_primary.json"))
                                                            and not os.path.exists(os.path.join(root, "p1t_holdout_OPENED.json")))
    print(json.dumps(out, indent=1, default=float))
    json.dump(out, open("test_holdout_notebook_results.json", "w"), indent=1, default=float)
