"""Test E1v2: certify versus identify on fresh data (registered in checks/prereg/E1v2_certify_vs_identify.json).

Replaces the withdrawn E1 run, whose "results" came from archived files and hard-coded intervals.

For each of the 30 Binance USD-M perpetuals of Paper 1 and each of the 105 fresh dates (the 4th, 5th,
18th, 19th and 23rd of every month, January 2025 - September 2026; no file of these symbols on
these days was used before), the pipeline builds five-minute returns, signed taker flow and the
three published trader-class long/short ratios, and estimates, with the Paper 1 code:

  * the price-and-flow kernel: five-minute flow on twelve lagged five-minute returns. Its sum
    Phi_hat = sum_m k_m is the certificate quantity (a linear functional of the merged measure);
    two exponentials fitted to the kernel give the price-only memory rates r_fast < r_slow
    (identification);
  * the class-tagged memory rates: n_{c,t} = r_c n_{c,t-1} + w_c ret_t for each class c.

Intervals are day-bootstrap percentile intervals (200 draws, fixed seed).

Per symbol:
  I_cert = width(CI Phi) / |Phi_hat|                     relative imprecision of the certificate
  I_id   = width(CI Delta r) / |Delta r_hat|,  Delta r = r_slow - r_fast   relative imprecision of
                                                        memory separation from prices and flow
  P1 holds if I_id >= 10 I_cert   (certifying is at least ten times cheaper than identifying)
  P2 holds if mean price-only rate-interval width >= 10 x mean class-tagged rate-interval width
A primary passes if it holds in at least 75% of evaluable symbols and its Holm-adjusted one-sided
binomial p-value (null rate 1/2) is below 0.05. A symbol is evaluable with at least 30 valid days;
the test is void if fewer than 20 symbols are evaluable.

Run once, in Google Colab, with  E1v2_Certify_vs_Identify.ipynb  (or:  python e1v2_pipeline.py --run).
"""

import argparse
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import datetime, timezone
import hashlib
import json
import math
import os
from pathlib import Path
import subprocess
import sys

import numpy as np
import pandas as pd
from scipy import optimize, stats

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import binance_vision as bv  # noqa: E402

THESIS = HERE.parent
ROOT = THESIS.parent
SPEC = THESIS / "checks/prereg/E1v2_certify_vs_identify.json"
COUNTER = THESIS / "checks/prereg/E1v2_unlock.json"
RESULT = HERE / "E1v2_results.json"
NUMBERS = THESIS / "checks/E1v2_numbers.tex"
DLLOG = HERE / "E1v2_download_log.json"

SYMBOLS = ("ACHUSDT ALICEUSDT API3USDT ARPAUSDT CELRUSDT CHRUSDT CVXUSDT GTCUSDT HOTUSDT ICXUSDT "
           "IOSTUSDT IOTXUSDT LITUSDT OGNUSDT QNTUSDT RLCUSDT SPELLUSDT TUSDT WOOUSDT ZENUSDT "
           "DASHUSDT IMXUSDT IOTAUSDT NEOUSDT ONEUSDT ROSEUSDT STGUSDT VETUSDT XMRUSDT ZRXUSDT").split()
DAYS_OF_MONTH = (4, 5, 18, 19, 23)
START, END = "2025-01-01", "2026-09-30"
CLASSES = {"top_position": "top_pos_ratio", "top_account": "top_acc_ratio", "all_accounts": "acc_ratio"}
B_BOOT, SEED, MIN_DAYS, MIN_SYMBOLS = 200, 20261024, 30, 20
RATIO, SHARE, ALPHA = 10.0, 0.75, 0.05


def dates():
    return [d.strftime("%Y-%m-%d") for d in pd.date_range(START, END, freq="D") if d.day in DAYS_OF_MONTH]


# ---- Paper 1 estimators (Part 6, cell Z1), unchanged except FLOW_SCALE = 1 ($M) ----------------
def five_min(df):
    m = df.index[df["top_pos_ratio"].notna() | df["acc_ratio"].notna()].to_numpy()
    m = m[m >= 5]
    if len(m) < 100:
        return None
    p = np.log(df["close"].to_numpy()) * 1e4; fl = df["flow"].to_numpy()
    cf = np.concatenate([[0.0], np.cumsum(fl)])
    out = pd.DataFrame({"m": m, "ret": p[m] - p[m - 5], "flow": cf[m + 1] - cf[m - 4]})
    for c, col in CLASSES.items():
        R = df[col].to_numpy()[m]
        out[c] = (R - 1) / (R + 1)
    return out


def tagged_fit(days5, c):
    Y, X = [], []
    for g in days5:
        n = g[c].to_numpy(); r = g["ret"].to_numpy()
        y, x1, x2 = n[1:], n[:-1], r[1:]
        ok = np.isfinite(y) & np.isfinite(x1) & np.isfinite(x2)
        if ok.sum() < 30:
            continue
        Y.append(y[ok] - y[ok].mean()); X.append(np.column_stack([x1[ok] - x1[ok].mean(), x2[ok] - x2[ok].mean()]))
    if not Y:
        return np.nan, np.nan
    b = np.linalg.lstsq(np.vstack(X), np.concatenate(Y), rcond=None)[0]
    return float(b[0]), float(b[1])


def kernel_fit(days5, L=12):
    """Price-only model: 5-min flow on 12 lagged 5-min returns; kernel fitted by two exponentials."""
    Y, X = [], []
    for g in days5:
        f, r = g["flow"].to_numpy(), g["ret"].to_numpy()
        if len(f) <= L + 10:
            continue
        Xl = np.column_stack([r[L - m:len(r) - m] for m in range(1, L + 1)]); y = f[L:]
        ok = np.all(np.isfinite(Xl), 1) & np.isfinite(y)
        Y.append(y[ok] - y[ok].mean()); X.append(Xl[ok] - Xl[ok].mean(0))
    k = np.linalg.lstsq(np.vstack(X), np.concatenate(Y), rcond=None)[0]
    m = np.arange(L)

    def resid(th):
        w1, r1, w2, r2 = th
        return w1 * r1 ** m + w2 * r2 ** m - k
    best = None
    for r1, r2 in [(0.2, 0.8), (0.1, 0.6), (0.4, 0.95), (0.05, 0.3)]:
        try:
            sol = optimize.least_squares(resid, [k[0] / 2, r1, k[0] / 2, r2],
                                         bounds=([-np.inf, 0, -np.inf, 0], [np.inf, 0.99, np.inf, 0.99]))
            if best is None or sol.cost < best.cost:
                best = sol
        except Exception:
            pass
    w1, r1, w2, r2 = best.x
    if r1 > r2:
        w1, r1, w2, r2 = w2, r2, w1, r1
    return {"k": k, "r_fast": float(r1), "r_slow": float(r2), "Phi": float(k.sum())}


def q95(v):
    v = np.asarray(v, float); v = v[np.isfinite(v)]
    return [float(np.quantile(v, .025)), float(np.quantile(v, .975))] if len(v) > 10 else [np.nan, np.nan]


def ident_symbol(days5, seed):
    rng = np.random.default_rng(seed); n = len(days5)
    point = {c: tagged_fit(days5, c) for c in CLASSES}; kp = kernel_fit(days5)
    bt = {c: [] for c in CLASSES}; bk = []
    for _ in range(B_BOOT):
        pick = [days5[i] for i in rng.integers(0, n, n)]
        for c in CLASSES:
            bt[c].append(tagged_fit(pick, c)[0])
        try:
            kk = kernel_fit(pick); bk.append((kk["r_fast"], kk["r_slow"], kk["Phi"]))
        except Exception:
            bk.append((np.nan, np.nan, np.nan))
    bk = np.array(bk)
    tag = {c: {"r": point[c][0], "r_ci": q95(bt[c])} for c in CLASSES}
    w_tag = float(np.mean([tag[c]["r_ci"][1] - tag[c]["r_ci"][0] for c in CLASSES]))
    rf_ci, rs_ci, phi_ci = q95(bk[:, 0]), q95(bk[:, 1]), q95(bk[:, 2])
    dr_ci = q95(bk[:, 1] - bk[:, 0])
    w_pr = float(np.mean([rf_ci[1] - rf_ci[0], rs_ci[1] - rs_ci[0]]))
    dr = kp["r_slow"] - kp["r_fast"]
    I_cert = (phi_ci[1] - phi_ci[0]) / abs(kp["Phi"]) if kp["Phi"] != 0 else math.inf
    I_id = (dr_ci[1] - dr_ci[0]) / abs(dr) if abs(dr) > 1e-9 else math.inf
    diff = np.array(bt["top_position"]) - np.array(bt["all_accounts"])
    return {"n_days": n, "tagged": tag, "price_only": {"r_fast": kp["r_fast"], "r_slow": kp["r_slow"],
            "r_fast_ci": rf_ci, "r_slow_ci": rs_ci, "delta_r": dr, "delta_r_ci": dr_ci,
            "Phi": kp["Phi"], "Phi_ci": phi_ci},
            "I_cert": I_cert, "I_id": I_id, "P1_holds": bool(I_id >= RATIO * I_cert),
            "width_tagged": w_tag, "width_price_only": w_pr,
            "width_ratio": w_pr / w_tag if np.isfinite(w_tag) and w_tag > 0 else float("nan"),
            "P2_holds": bool(np.isfinite(w_tag) and w_tag > 0 and w_pr >= RATIO * w_tag),
            "Phi_identified": bool(phi_ci[0] > 0 or phi_ci[1] < 0),
            "classes_differ": bool(q95(diff)[0] > 0 or q95(diff)[1] < 0)}


def holm(pvals):
    order = np.argsort(pvals); m = len(pvals); adj = np.empty(m); run = 0.0
    for rank, i in enumerate(order):
        run = max(run, min(1.0, (m - rank) * pvals[i])); adj[i] = run
    return adj.tolist()


def evaluate(per):
    ev = {s: v for s, v in per.items() if v.get("n_days", 0) >= MIN_DAYS}
    n = len(ev)
    out = {"n_symbols_registered": len(SYMBOLS), "n_evaluable": n, "void": n < MIN_SYMBOLS}
    if out["void"]:
        return out
    c1 = sum(v["P1_holds"] for v in ev.values()); c2 = sum(v["P2_holds"] for v in ev.values())
    p = [float(stats.binom.sf(c - 1, n, 0.5)) for c in (c1, c2)]
    adj = holm(p); need = math.ceil(SHARE * n)
    out.update({"threshold_count": need, "P1_count": c1, "P2_count": c2, "p_raw": p, "p_holm": adj,
                "P1_pass": bool(c1 >= need and adj[0] < ALPHA), "P2_pass": bool(c2 >= need and adj[1] < ALPHA),
                "secondary": {"Phi_identified": sum(v["Phi_identified"] for v in ev.values()),
                              "classes_differ": sum(v["classes_differ"] for v in ev.values()),
                              "median_I_cert": float(np.median([v["I_cert"] for v in ev.values()])),
                              "median_I_id": float(np.median([min(v["I_id"], 1e6) for v in ev.values()])),
                              "median_width_ratio": float(np.nanmedian([v["width_ratio"] for v in ev.values()]))}})
    return out


def numbers_tex(res):
    e = res["evaluation"]
    if e["void"]:
        return "% generated by e1v2_pipeline.py\n\\newcommand{\\EoneVoid}{void}\n"
    L = ["% generated by e1v2_pipeline.py; do not edit",
         f"\\newcommand{{\\EoneSymbols}}{{{e['n_evaluable']}}}",
         f"\\newcommand{{\\EoneNeed}}{{{e['threshold_count']}}}",
         f"\\newcommand{{\\EonePone}}{{{e['P1_count']}}}",
         f"\\newcommand{{\\EonePtwo}}{{{e['P2_count']}}}",
         f"\\newcommand{{\\EonePoneVerdict}}{{{'passed' if e['P1_pass'] else 'failed'}}}",
         f"\\newcommand{{\\EonePtwoVerdict}}{{{'passed' if e['P2_pass'] else 'failed'}}}",
         f"\\newcommand{{\\EonePhiIdentified}}{{{e['secondary']['Phi_identified']}}}",
         f"\\newcommand{{\\EoneMedianIcert}}{{{e['secondary']['median_I_cert']:.2f}}}",
         f"\\newcommand{{\\EoneMedianIid}}{{{e['secondary']['median_I_id']:.2f}}}",
         f"\\newcommand{{\\EoneMedianRatio}}{{{e['secondary']['median_width_ratio']:.1f}}}"]
    return "\n".join(L) + "\n"


def gate(allow_unregistered=False):
    spec = json.loads(SPEC.read_text())
    sha = hashlib.sha256(SPEC.read_bytes()).hexdigest()
    assert sha == SPEC.with_suffix(".sha256").read_text().strip(), "specification hash mismatch"
    for key, path in (("pipeline_sha256", HERE / "e1v2_pipeline.py"), ("binance_vision_sha256", HERE / "binance_vision.py")):
        assert hashlib.sha256(path.read_bytes()).hexdigest() == spec[key], f"{path.name} changed after registration"
    registered = None
    if not allow_unregistered:
        rel = str(SPEC.relative_to(ROOT))
        registered = subprocess.check_output(["git", "log", "-1", "--format=%H", "--", rel], cwd=ROOT, text=True).strip()
        assert registered, "the specification is not committed"
        st = json.loads(COUNTER.read_text())
        assert st["opens"] == 0, "the test set was already opened; E1v2 is run once"
    return spec, sha, registered


def run(cache_dir=None, threads=16, allow_unregistered=False, symbols=None, day_list=None):
    spec, sha, registered = gate(allow_unregistered)
    syms = symbols or SYMBOLS; ds = day_list or dates()
    for d in ds:
        assert int(d[8:]) in DAYS_OF_MONTH and START <= d <= END, d
    if not allow_unregistered:
        COUNTER.write_text(json.dumps({"opens": 1, "spec_sha256": sha, "registration_commit": registered,
                                       "opened_utc": datetime.now(timezone.utc).isoformat()}, indent=2) + "\n")
    jobs = [(s, d) for s in syms for d in ds]
    frames = {}
    with ThreadPoolExecutor(max_workers=threads) as ex:
        futs = {ex.submit(bv.get_day, s, d, cache_dir, False): (s, d) for s, d in jobs}
        for i, f in enumerate(as_completed(futs)):
            s, d = futs[f]
            df, _ = f.result()
            if df is not None:
                g = five_min(df)
                if g is not None:
                    frames.setdefault(s, []).append((d, g))
            if (i + 1) % 300 == 0:
                print(f"  {i + 1}/{len(jobs)} symbol-days", flush=True)
    per = {}
    for j, s in enumerate(syms):
        days5 = [g for d, g in sorted(frames.get(s, []), key=lambda t: t[0])]
        if len(days5) < MIN_DAYS:
            per[s] = {"n_days": len(days5), "excluded": "fewer than 30 valid days"}
            continue
        per[s] = ident_symbol(days5, SEED + j)
        print(f"  {s}: days={len(days5)} I_cert={per[s]['I_cert']:.3g} I_id={per[s]['I_id']:.3g} "
              f"ratio={per[s]['width_ratio']:.3g}", flush=True)
    res = {"test": "E1v2", "spec_sha256": sha, "registration_commit": registered,
           "run_utc": datetime.now(timezone.utc).isoformat(), "dates": ds, "symbols": syms,
           "per_symbol": per, "evaluation": evaluate(per)}
    RESULT.write_text(json.dumps(res, indent=1, default=float) + "\n")
    NUMBERS.write_text(numbers_tex(res))
    DLLOG.write_text(json.dumps(bv.DL_LOG, indent=0) + "\n")
    print(json.dumps(res["evaluation"], indent=1))
    return res


def check():
    """Verify a committed result without reopening: hashes, counter, evaluation and numbers."""
    spec = json.loads(SPEC.read_text())
    res = json.loads(RESULT.read_text())
    assert res["spec_sha256"] == hashlib.sha256(SPEC.read_bytes()).hexdigest()
    assert json.loads(COUNTER.read_text())["opens"] == 1
    assert hashlib.sha256((HERE / "e1v2_pipeline.py").read_bytes()).hexdigest() == spec["pipeline_sha256"]
    again = evaluate(res["per_symbol"])
    assert again == res["evaluation"], "evaluation does not reproduce from per-symbol results"
    assert NUMBERS.read_text() == numbers_tex(res)
    print("E1v2 result check: PASS", {k: again.get(k) for k in ("n_evaluable", "P1_count", "P2_count", "P1_pass", "P2_pass")})


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--run", action="store_true"); ap.add_argument("--check", action="store_true")
    ap.add_argument("--cache", default=None); ap.add_argument("--threads", type=int, default=16)
    a = ap.parse_args()
    if a.run:
        run(a.cache, a.threads)
    elif a.check:
        check()
