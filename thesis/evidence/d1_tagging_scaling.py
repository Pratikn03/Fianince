"""Test D1: does class tagging restore the parametric rate as data grow? (spec checks/prereg/D1_tagging_scaling.json)

Theorem discvalue of Chapter 2 says that tagged data turn identification of memory into an ordinary
estimation problem, while from prices and flow alone identification is far more expensive. The
testable consequence is about scaling: as the number of days n grows, class-tagged memory intervals
should shrink like n^(-1/2), while price-only memory intervals should shrink much more slowly, so the
advantage of tagging should grow with n.

No public data tag order flow by trader at the level Proposition tagged assumes; the closest public
analogue is Binance's class-level positions, which Chapter 2 already uses. This test therefore checks a
new prediction (the scaling) on new days, with the same estimators, rather than new kinds of data.

Data: the 30 perpetuals of Paper 1 on fresh dates, the 7th, 21st and 30th of every month from January
2025 to September 2026, minus three dates used before (2025-04-07, 2026-07-21, 2026-09-30).
Nested subsamples of the valid days, drawn once with a fixed seed: n1 = 14, n2 = 28, n3 = all valid days.
For each subsample: class-tagged rate intervals and price-only rate intervals (Paper 1 estimators,
day-bootstrap, 150 draws); width_tag = mean width over the three classes, width_price = mean width of
the two price-only rates. Per symbol, OLS slopes on log n:
  s_tag   = slope of log width_tag;            P1 holds if -0.75 <= s_tag <= -0.25
  s_ratio = slope of log(width_price/width_tag); P2 holds if s_ratio >= 0.20
A primary passes if it holds in at least 75% of evaluable symbols (>= 40 valid days) and its Holm-adjusted
one-sided binomial p-value (null rate 1/2) is below 0.05. Void if fewer than 20 symbols are evaluable.
"""

import argparse
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import datetime, timezone
import hashlib
import json
import math
from pathlib import Path
import subprocess
import sys

import numpy as np
import pandas as pd
from scipy import stats

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import binance_vision as bv  # noqa: E402
import e1v2_pipeline as E  # noqa: E402  (Paper 1 estimators, registered with E1v2)

THESIS = HERE.parent
ROOT = THESIS.parent
SPEC = THESIS / "checks/prereg/D1_tagging_scaling.json"
COUNTER = THESIS / "checks/prereg/D1_unlock.json"
RESULT = HERE / "D1_results.json"
NUMBERS = THESIS / "checks/D1_numbers.tex"
DLLOG = HERE / "D1_download_log.json"

SYMBOLS = E.SYMBOLS
DAYS_OF_MONTH = (7, 21, 30)
EXCLUDE = {"2025-04-07", "2026-07-21", "2026-09-30"}
START, END = "2025-01-01", "2026-09-30"
SEED, B_BOOT, N1, N2, MIN_DAYS, MIN_SYMBOLS = 20261025, 150, 14, 28, 40, 20
SHARE, ALPHA = 0.75, 0.05


def dates():
    return [d.strftime("%Y-%m-%d") for d in pd.date_range(START, END, freq="D")
            if d.day in DAYS_OF_MONTH and d.strftime("%Y-%m-%d") not in EXCLUDE]


def widths(days5, seed):
    rng = np.random.default_rng(seed); n = len(days5)
    bt = {c: [] for c in E.CLASSES}; bk = []
    for _ in range(B_BOOT):
        pick = [days5[i] for i in rng.integers(0, n, n)]
        for c in E.CLASSES:
            bt[c].append(E.tagged_fit(pick, c)[0])
        try:
            kk = E.kernel_fit(pick); bk.append((kk["r_fast"], kk["r_slow"]))
        except Exception:
            bk.append((np.nan, np.nan))
    bk = np.array(bk)
    w_tag = float(np.mean([np.diff(E.q95(bt[c]))[0] for c in E.CLASSES]))
    w_pr = float(np.mean([np.diff(E.q95(bk[:, 0]))[0], np.diff(E.q95(bk[:, 1]))[0]]))
    return w_tag, w_pr


def symbol_scaling(days5, seed):
    rng = np.random.default_rng(seed)
    order = rng.permutation(len(days5))
    ns = [N1, N2, len(days5)]
    rows = []
    for k, n in enumerate(ns):
        sub = [days5[i] for i in order[:n]]
        wt, wp = widths(sub, seed + 1000 * (k + 1))
        rows.append({"n": n, "width_tag": wt, "width_price": wp})
    ln = np.log(ns)
    ok = all(np.isfinite(r["width_tag"]) and r["width_tag"] > 0 and np.isfinite(r["width_price"]) and r["width_price"] > 0
             for r in rows)
    if not ok:
        return {"subsamples": rows, "evaluable": False}
    s_tag = float(np.polyfit(ln, np.log([r["width_tag"] for r in rows]), 1)[0])
    s_ratio = float(np.polyfit(ln, np.log([r["width_price"] / r["width_tag"] for r in rows]), 1)[0])
    return {"subsamples": rows, "evaluable": True, "slope_tag": s_tag, "slope_ratio": s_ratio,
            "P1_holds": bool(-0.75 <= s_tag <= -0.25), "P2_holds": bool(s_ratio >= 0.20)}


def evaluate(per):
    ev = {s: v for s, v in per.items() if v.get("evaluable")}
    n = len(ev)
    out = {"n_evaluable": n, "void": n < MIN_SYMBOLS}
    if out["void"]:
        return out
    c1 = sum(v["P1_holds"] for v in ev.values()); c2 = sum(v["P2_holds"] for v in ev.values())
    p = [float(stats.binom.sf(c - 1, n, 0.5)) for c in (c1, c2)]
    adj = E.holm(p); need = math.ceil(SHARE * n)
    out.update({"threshold_count": need, "P1_count": c1, "P2_count": c2, "p_raw": p, "p_holm": adj,
                "P1_pass": bool(c1 >= need and adj[0] < ALPHA), "P2_pass": bool(c2 >= need and adj[1] < ALPHA),
                "median_slope_tag": float(np.median([v["slope_tag"] for v in ev.values()])),
                "median_slope_ratio": float(np.median([v["slope_ratio"] for v in ev.values()]))})
    return out


def numbers_tex(e):
    if e["void"]:
        return "% generated by d1_tagging_scaling.py\n\\newcommand{\\DoneVoid}{void}\n"
    return ("% generated by d1_tagging_scaling.py; do not edit\n"
            f"\\newcommand{{\\DoneSymbols}}{{{e['n_evaluable']}}}\\newcommand{{\\DoneNeed}}{{{e['threshold_count']}}}\n"
            f"\\newcommand{{\\DonePone}}{{{e['P1_count']}}}\\newcommand{{\\DonePtwo}}{{{e['P2_count']}}}\n"
            f"\\newcommand{{\\DonePoneVerdict}}{{{'passed' if e['P1_pass'] else 'failed'}}}"
            f"\\newcommand{{\\DonePtwoVerdict}}{{{'passed' if e['P2_pass'] else 'failed'}}}\n"
            f"\\newcommand{{\\DoneSlopeTag}}{{{e['median_slope_tag']:.2f}}}"
            f"\\newcommand{{\\DoneSlopeRatio}}{{{e['median_slope_ratio']:.2f}}}\n")


def gate():
    spec = json.loads(SPEC.read_text())
    sha = hashlib.sha256(SPEC.read_bytes()).hexdigest()
    assert sha == SPEC.with_suffix(".sha256").read_text().strip(), "specification hash mismatch"
    for key, f in (("d1_sha256", "d1_tagging_scaling.py"), ("e1v2_pipeline_sha256", "e1v2_pipeline.py"),
                   ("binance_vision_sha256", "binance_vision.py")):
        assert hashlib.sha256((HERE / f).read_bytes()).hexdigest() == spec[key], f"{f} changed after registration"
    rel = str(SPEC.relative_to(ROOT))
    commit = subprocess.check_output(["git", "log", "-1", "--format=%H", "--", rel], cwd=ROOT, text=True).strip()
    assert commit, "specification not committed"
    assert json.loads(COUNTER.read_text())["opens"] == 0, "D1 was already opened"
    return sha, commit


def run(cache_dir=None, threads=16, resume=False, symbols=None, day_list=None, skip_gate=False):
    if skip_gate:
        sha, commit = "test", None
    elif resume:
        c = json.loads(COUNTER.read_text()); assert c["opens"] == 1, "nothing to resume"
        sha, commit = c["spec_sha256"], c["registration_commit"]
    else:
        sha, commit = gate()
        COUNTER.write_text(json.dumps({"opens": 1, "spec_sha256": sha, "registration_commit": commit,
                                       "opened_utc": datetime.now(timezone.utc).isoformat()}, indent=2) + "\n")
    syms = symbols or SYMBOLS; ds = day_list or dates()
    frames = {}
    with ThreadPoolExecutor(max_workers=threads) as ex:
        futs = {ex.submit(bv.get_day, s, d, cache_dir, False): (s, d) for s in syms for d in ds}
        for i, f in enumerate(as_completed(futs)):
            s, d = futs[f]; df, _ = f.result()
            g = E.five_min(df) if df is not None else None
            if g is not None:
                frames.setdefault(s, []).append((d, g))
            if (i + 1) % 300 == 0:
                print(f"  {i + 1}/{len(futs)} symbol-days", flush=True)
    per = {}
    for j, s in enumerate(syms):
        days5 = [g for d, g in sorted(frames.get(s, []), key=lambda t: t[0])]
        if len(days5) < MIN_DAYS:
            per[s] = {"n_days": len(days5), "evaluable": False, "excluded": f"fewer than {MIN_DAYS} valid days"}
            continue
        per[s] = {"n_days": len(days5), **symbol_scaling(days5, SEED + 37 * j)}
        print(f"  {s}: n={len(days5)} slope_tag={per[s].get('slope_tag', float('nan')):.3f} "
              f"slope_ratio={per[s].get('slope_ratio', float('nan')):.3f}", flush=True)
    res = {"test": "D1", "spec_sha256": sha, "registration_commit": commit, "run_utc": datetime.now(timezone.utc).isoformat(),
           "dates": ds, "symbols": syms, "per_symbol": per, "evaluation": evaluate(per)}
    if not skip_gate:
        RESULT.write_text(json.dumps(res, indent=1, default=float) + "\n")
        NUMBERS.write_text(numbers_tex(res["evaluation"]))
        DLLOG.write_text(json.dumps(bv.DL_LOG, indent=0) + "\n")
    print(json.dumps(res["evaluation"], indent=1))
    return res


def check():
    res = json.loads(RESULT.read_text())
    assert res["spec_sha256"] == hashlib.sha256(SPEC.read_bytes()).hexdigest()
    assert json.loads(COUNTER.read_text())["opens"] == 1
    assert evaluate(res["per_symbol"]) == res["evaluation"]
    assert NUMBERS.read_text() == numbers_tex(res["evaluation"])
    print("D1 result check: PASS")


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--run", action="store_true"); ap.add_argument("--check", action="store_true")
    ap.add_argument("--cache", default=None)
    a = ap.parse_args()
    run(a.cache) if a.run else check() if a.check else None
