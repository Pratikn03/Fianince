"""Tests amendment A4 on simulated TWSE responses (no download). (1) The unamended analysis fails the gate when
2019-04-29 carries the alias label. (2) The A4 analysis passes, applies the alias exactly once, and gives the same
primary as the unaliased data. (3) The alias on any other day stops the run before any statistic."""
import copy, datetime, json, os, tempfile
import numpy as np
import p1t_executor as exm
import validate_executor as v
import test_holdout_notebook as th
import make_holdout_notebook as mk
import make_holdout_A4_notebook as m4

ALIAS = "加權股價指數"

def fake_with_day(day="20190429", **kw):
    cal, store = th.fake(**kw)
    if day not in cal:          # copy the nearest earlier day's responses to create the day
        prev = max(d for d in cal if d < day)
        store[("T86", day)] = copy.deepcopy(store[("T86", prev)]); store[("MI", day)] = copy.deepcopy(store[("MI", prev)])
        cal = sorted(cal + [day])
    return cal, store

def alias(store, day):
    s = dict(store); mi = copy.deepcopy(s[("MI", day)])
    mi["tables"][0]["title"] = "108年04月29日 價格指數(臺灣證券交易所)"
    for row in mi["tables"][0]["data"]:
        if row[0] == exm.INDEX_NAME: row[0] = ALIAS
    s[("MI", day)] = mi; return s

def run(cal, store, a4):
    rp = exm.run_period
    exm.run_period = lambda *a, **k: rp(*a, **{**k, "B": 199})
    root = tempfile.mkdtemp(); work = tempfile.mkdtemp(); cwd = os.getcwd(); os.chdir(work)
    g = {"np": np, "json": json, "os": os, "zipfile": __import__("zipfile"), "gzip": __import__("gzip"), "ex": exm,
         "days": cal, "ev": set(), "ROOT": root, "END": "20231229", "DEV_END": "20161230", "HOLDOUT_START": "20190102",
         "MIN_QUOTES": 10, "HOLD_MIN": 1150, "HOLD_MAX": 1400, "KNOWN_T86_SCHEMAS": v.ERA_FIELDS, "EXECUTOR_SHA256": "test",
         "MAN": os.path.join(root, "manifest.jsonl"), "now": lambda: datetime.datetime.now(datetime.timezone.utc).isoformat()}
    try:
        if a4:
            exec(m4.A4_LOAD, g)
            g["load"] = lambda sub, d: g["a4_relabel"](copy.deepcopy(store[(sub, d)]), d) if sub == "MI" else store[(sub, d)]
            exec(m4.analysis_a4(), g)
        else:
            g["load"] = lambda sub, d: store[(sub, d)]
            exec(mk.ANALYSIS, g)
        return "ok", g
    except SystemExit as e:
        return "stopped: " + str(e)[:90], g
    finally:
        os.chdir(cwd); exm.run_period = rp

if __name__ == "__main__":
    out = {}
    cal, store = fake_with_day()
    st_al = alias(store, "20190429")
    s0, g0 = run(cal, st_al, a4=False)
    out["unamended_with_alias"] = s0; out["unamended_mi_bad_days"] = g0.get("gate", {}).get("mi_bad_days")
    s1, g1 = run(cal, st_al, a4=True)
    s2, g2 = run(cal, store, a4=False)
    out["a4_with_alias"] = s1; out["a4_applied"] = sorted(g1.get("A4_applied", []))
    out["primary_equal_to_unaliased"] = (s1 == "ok" and s2 == "ok" and
        json.dumps(g1["primary"]["primary"], sort_keys=True, default=float) == json.dumps(g2["primary"]["primary"], sort_keys=True, default=float))
    other = max(d for d in cal if "20200101" < d < "20200301")
    s3, g3 = run(cal, alias(store, other), a4=True)
    out["a4_alias_on_other_day"] = s3; out["a4_other_day_primary_written"] = os.path.exists(os.path.join(g3["ROOT"], "p1t_holdout_primary.json"))
    print(json.dumps(out, indent=1, ensure_ascii=False))
    json.dump(out, open("test_holdout_A4_results.json", "w"), indent=1, ensure_ascii=False)
