"""Builds P1M_Barrier_Colab.ipynb (protocol P1M_measurement_protocol.md).

One code cell. It mounts Drive, reuses the stored TWSE files in P1T_raw for 2013-01-02 to 2016-12-30 (downloading a
development-period file only if it is missing), builds the P1T panel with the unchanged executor, runs the primary
measurement and the three pre-specified sensitivity runs once, and saves p1m_results.json / .zip to Drive.
"""
import hashlib
import json

EX = open("p1t_executor.py").read()
CORE = open("p1m_core.py").read()
EX_SHA = hashlib.sha256(EX.encode()).hexdigest()
CORE_SHA = hashlib.sha256(CORE.encode()).hexdigest()
assert EX_SHA == "8d8a70a36f412591c03dfeaec463a0cb949aa4df565fdad829b984462615b075", "P1T executor changed"

ANALYSIS = r'''
# ---- P1M analysis (protocol P1M_measurement_protocol.md) ----
RES = os.path.join(ROOT, "p1m_results.json")
if os.path.exists(RES):
    results = json.load(open(RES))
    print("P1M was already computed on", results["computed_utc"], "- loaded from Drive, NOT recomputed.")
else:
    assert days and max(days) <= DEV_END, "a date after the development period would be loaded"
    day_files = [(d, load("T86", d), load("MI", d)) for d in days]
    P = ex.build_panel(day_files, ev)
    dates = np.array(P.dates); dev = np.ones(len(dates), bool)
    prep = ex.prepare(P, dev)
    print("panel:", len(P.codes), "codes,", len(dates), "days; universe", len(prep["U"]), flush=True)
    runs = {}
    t0 = time.time()
    runs["primary"] = pm.measure(prep, dev, label="primary")
    print("primary done", round(time.time() - t0), "s", flush=True)
    runs["dealer_own_account"] = pm.measure(prep, dev, dealer="DealerOwn", label="dealer_own_account")
    runs["same_day_timing"] = pm.measure(prep, dev, delay=0, label="same_day_timing")
    runs["one_price_lag"] = pm.measure(prep, dev, p=1, label="one_price_lag")
    print("all runs done", round(time.time() - t0), "s", flush=True)
    results = {"spec": "P1M", "protocol": "P1M_measurement_protocol.md", "period": [days[0], days[-1]],
               "n_days": len(days), "executor_sha256": EXECUTOR_SHA256, "core_sha256": CORE_SHA256,
               "computed_utc": now(), "runs": runs}
    json.dump(results, open("p1m_results.json", "w"), indent=1, ensure_ascii=False, default=float)
    with zipfile.ZipFile("p1m_results.zip", "w", zipfile.ZIP_DEFLATED) as z:
        z.write("p1m_results.json")
    import shutil
    shutil.copy("p1m_results.json", RES)
    shutil.copy("p1m_results.zip", os.path.join(ROOT, "p1m_results.zip"))

def _f(v):
    return f"{v:.3g}" if isinstance(v, (int, float)) and v == v else str(v)
for name, R in results["runs"].items():
    th, ci, q1 = R["theta"], R["bootstrap"]["ci"], R["Q1"]
    print(f"\n=== {name} === stationary={R['stationary']}  N={R['records']['n_stocks']}  stock-days={R['records']['pooled_stock_days']:.0f}")
    print("r:", [_f(v) for v in th["r"]], " w:", [_f(v) for v in th["w"]], " kappa:", _f(th["kappa"]), " sum a:", _f(sum(th["a"])))
    for c in ("Foreign", "Trust", "Dealers"):
        print(f"  H_{c} = {_f(ci['H_'+c]['est'])}  95% [{_f(ci['H_'+c]['ci95'][0])}, {_f(ci['H_'+c]['ci95'][1])}]")
    print(f"  U = {_f(ci['U']['est'])}  95% [{_f(ci['U']['ci95'][0])}, {_f(ci['U']['ci95'][1])}]")
    print("Q1 rates per stock-day: prices", _f(q1["price_rate_per_stock_day"]), " tags", _f(q1["tag_rate_per_stock_day"]),
          " ratio", _f(q1["information_ratio_tags_to_prices"]))
    print("Q1 years (at least): one stock's prices", _f(q1["years_prices_one_stock_at_least"]),
          " whole panel's prices", _f(q1["years_prices_whole_panel_at_least"]), " one stock tagged", _f(q1["years_tags_one_stock_at_least"]))
    for key in ("Q2Q3_whole_panel", "Q2Q3_whole_panel_tight_box", "Q2Q3_one_stock"):
        g = R[key]
        print(f"{key}: H_Foreign in [{_f(g['H_Foreign']['min'])}, {_f(g['H_Foreign']['max'])}]  U in [{_f(g['U']['min'])}, {_f(g['U']['max'])}]  hbar={_f(g['hbar'])}")
    print("relabeling values of H_Foreign:", [_f(v) for v in R["Q2Q3_whole_panel"]["relabeling_values_H_Foreign"]])
try:
    from google.colab import files; files.download("p1m_results.zip")
except Exception:
    print("saved p1m_results.zip (also on Drive in P1T_raw)")
'''

HEAD = r'''
import os, io, json, gzip, time, zipfile, hashlib, datetime, re, sys, calendar
import numpy as np, requests
EXECUTOR_SHA256 = "%(EX_SHA)s"
CORE_SHA256 = "%(CORE_SHA)s"
EXECUTOR_SRC = %(EX_SRC)s
CORE_SRC = %(CORE_SRC)s
assert hashlib.sha256(EXECUTOR_SRC.encode()).hexdigest() == EXECUTOR_SHA256, "executor changed"
assert hashlib.sha256(CORE_SRC.encode()).hexdigest() == CORE_SHA256, "P1M core changed"
open("p1t_executor.py", "w").write(EXECUTOR_SRC); open("p1m_core.py", "w").write(CORE_SRC)
sys.path.insert(0, "."); import p1t_executor as ex, p1m_core as pm

try:
    from google.colab import drive; drive.mount("/content/drive"); ROOT = "/content/drive/MyDrive/P1T_raw"
except Exception: ROOT = "P1T_raw"
for sub in ("T86", "MI", "TWT49U", "FMTQIK"): os.makedirs(os.path.join(ROOT, sub), exist_ok=True)
START, DEV_END = "20130102", "20161230"
H = {"User-Agent": "Mozilla/5.0 (academic research; P1T)"}
MAN = os.path.join(ROOT, "manifest.jsonl")
def now(): return datetime.datetime.now(datetime.timezone.utc).isoformat()
def fetch(path, url, params, want_date=None):
    fn = os.path.join(ROOT, path + ".json.gz")
    if os.path.exists(fn):
        return json.loads(gzip.open(fn).read())
    print("not on Drive, downloading", path, flush=True)
    for attempt in range(6):
        try:
            r = requests.get(url, params=params, headers=H, timeout=60)
            if r.status_code == 200:
                j = r.json()
                if want_date is not None and j.get("stat") == "OK" and j.get("date") != want_date:
                    raise SystemExit(f"DATE MISMATCH {path}: asked {want_date}, got {j.get('date')}")
                gzip.open(fn, "wb").write(r.content)
                with open(MAN, "a") as m:
                    m.write(json.dumps({"path": path, "url": r.url, "sha256": hashlib.sha256(r.content).hexdigest(), "utc": now()}) + "\n")
                time.sleep(3.5)
                return j
        except SystemExit: raise
        except Exception as e: print("retry", path, repr(e))
        time.sleep(30 * (attempt + 1))
    raise RuntimeError("failed " + path)

# 1. development-period trading calendar (2013-2016 only)
days = []
for y in range(2013, 2017):
    for mth in range(1, 13):
        j = fetch(f"FMTQIK/{y}{mth:02d}", "https://www.twse.com.tw/rwd/zh/afterTrading/FMTQIK",
                  {"date": f"{y}{mth:02d}01", "response": "json"})
        for row in j.get("data", []):
            dg = re.sub(r"[^0-9]", "", row[0]); d = str(int(dg[:-4]) + 1911) + dg[-4:]
            if START <= d <= DEV_END: days.append(d)
days = sorted(set(days)); assert days[-1] <= DEV_END
print(len(days), "development trading days", days[0], days[-1])
# 2. daily T86 and MI_INDEX (already on Drive from the P1T runs)
for k, d in enumerate(days):
    fetch(f"T86/{d}", "https://www.twse.com.tw/rwd/zh/fund/T86", {"date": d, "selectType": "ALLBUT0999", "response": "json"}, d)
    fetch(f"MI/{d}", "https://www.twse.com.tw/rwd/zh/afterTrading/MI_INDEX", {"date": d, "type": "ALLBUT0999", "response": "json"}, d)
# 3. ex-rights table
ev = set()
for y in range(2013, 2017):
    for mth in range(1, 13):
        a = f"{y}{mth:02d}01"; b = f"{y}{mth:02d}{calendar.monthrange(y, mth)[1]:02d}"
        j = fetch(f"TWT49U/{y}{mth:02d}", "https://www.twse.com.tw/rwd/zh/exRight/TWT49U", {"startDate": a, "endDate": b, "response": "json"})
        ev |= ex.parse_twt49u(j)
def load(sub, d): return json.loads(gzip.open(os.path.join(ROOT, sub, d + ".json.gz")).read())
'''


def build(path="P1M_Barrier_Colab.ipynb"):
    head = HEAD % {"EX_SHA": EX_SHA, "CORE_SHA": CORE_SHA, "EX_SRC": json.dumps(EX), "CORE_SRC": json.dumps(CORE)}
    cell = head + ANALYSIS
    compile(cell, "cell", "exec")
    md = ("# P1M: the identification barrier in a real market (Taiwan, 2013–2016)\n\n"
          "Measurement fixed before the run in `P1M_measurement_protocol.md`. It reuses the TWSE files already on your "
          "Drive in `P1T_raw` (development period only, 2013-01-02 to 2016-12-30; nothing later is loaded), estimates "
          "each class's feedback rule from its tagged flow, and computes: (Q1) the years of prices alone needed to "
          "separate the classes, (Q2) how much compositions that the whole price record cannot tell apart disagree about "
          "halting foreign feedback, and (Q3) the same for a uniform cut.\n\n"
          "**Run the single code cell once** (Runtime → Run all). Allow Drive access when asked. It takes about 20–40 "
          "minutes. It saves `p1m_results.json` and `p1m_results.zip` to Drive (`P1T_raw`) and downloads the zip. "
          "Send the zip, or paste the printed summary. A rerun loads the saved result and does not recompute.")
    nb = {"nbformat": 4, "nbformat_minor": 5, "metadata": {"kernelspec": {"name": "python3", "display_name": "Python 3"},
                                                             "colab": {"provenance": []}},
          "cells": [{"cell_type": "markdown", "metadata": {}, "source": md, "id": "md0"},
                    {"cell_type": "code", "metadata": {}, "source": cell, "outputs": [], "execution_count": None, "id": "c1"}]}
    json.dump(nb, open(path, "w"), ensure_ascii=False, indent=1)
    return CORE_SHA


if __name__ == "__main__":
    print("core sha256", build())
