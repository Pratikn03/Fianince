"""Test C2 (DRAFT, NOT REGISTERED): certify the safety margin versus identify the memories, on symbols never used.

Designed after Tests E1v2 and D1 failed, from the exploratory pilot on their spent days (Chapter 5, Exploration after the
tests). It will be registered only after the author approves the specification; until then gate() refuses to run.

Universe (fixed before any data are downloaded and written to C2_universe.json):
    Binance USD-M USDT perpetuals listed in the public archive whose symbol string appears in no text file of the
    repository; klines must exist on 2025-01-04 and 2026-09-23; 30 drawn in a seeded random order (seed 20261101).
Dates: the 4th, 5th, 18th, 19th and 23rd of each month, January 2025 to September 2026 (105 dates; fresh for these symbols).

Estimators (five-minute marks, pooled over days with day-demeaning; day bootstrap, 200 draws, seed 20261101 + 101 j):
    price:   ret_t = kappa flow_t + beta x_{t-1},  x = p - EWMA(p, span 12 bars)
    kernel:  flow_t = sum_{m=1..12} k_m x_{t-m},   Phi = sum k_m
    margin:  M = 1 - a - kappa Phi = -beta - kappa Phi        DECIDED if its 95% interval excludes zero
    memories: two exponentials fitted to the return kernel (flow on 12 lagged returns, as in E1v2), rates in [0, 0.99];
              IDENTIFIED if the interval of r_slow - r_fast excludes zero and no rate interval reaches 0.005 or 0.985
Primary 1: the margin is decided in at least 75% of evaluable symbols, one-sided binomial p (null 1/2) below 0.05.
Primary 2: certification beats identification symbol by symbol: with b = #(decided, not identified) and
           c = #(identified, not decided), b > c and the exact one-sided McNemar p = P(Bin(b + c, 1/2) >= b) below 0.05.
Primary 3 (horizon-matched disclosure, added after Pilot 3): the class-tagged memories are estimated more precisely
           than the price-only slow memory when the price-only kernel is long enough to see them (96 five-minute lags,
           eight hours; two exponentials, rates in [0, 0.9995]). Width of the 95% interval of log10 half-life: tagged
           (mean over the three Binance classes, n_t = r n_{t-1} + w ret_t with n = (R-1)/(R+1)) below price-only in at
           least 75% of symbols with 30 valid tagged days; one-sided binomial p (null 1/2) below 0.05.
Holm across the three at 0.05. A symbol is evaluable with at least 30 valid days; void if fewer than 20 are evaluable.
What is mechanical: in the pilot the decision rests mainly on the reversion term (with feedback removed the decision was the
same in 28 of 30 symbols). A pass shows that the theory's safety question is decidable from public data while the memories
are not; it does not show that the feedback term is measured precisely. The no-feedback decision is a registered secondary.
What Primary 3 does not show: the tagged series is the persistence of class positioning, not of class order flow, and slow
position turnover would produce persistence without any learning memory. A pass shows that positioning data restrict a
persistence parameter that prices leave unbounded at a matched horizon; it does not show that the two estimate one object.
"""
import argparse
import hashlib
import json
import math
import re
import subprocess
import sys
import urllib.request
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import datetime, timezone
from pathlib import Path

import numpy as np
import pandas as pd
from scipy import optimize, stats

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import binance_vision as bv  # noqa: E402

THESIS = HERE.parent
ROOT = THESIS.parent
SPEC = THESIS / "checks/prereg/C2_margin_vs_identify.json"
COUNTER = THESIS / "checks/prereg/C2_unlock.json"
RESULT = HERE / "C2_results.json"
NUMBERS = THESIS / "checks/C2_numbers.tex"
DLLOG = HERE / "C2_download_log.json"
UNIVERSE = HERE / "C2_universe.json"

SEED, N_SYMBOLS, L, SPAN, B_BOOT = 20261101, 30, 12, 12, 200
DAYS_OF_MONTH, START, END = (4, 5, 18, 19, 23), "2025-01-01", "2026-09-30"
MIN_DAYS, MIN_SYMBOLS, SHARE, ALPHA = 30, 20, 0.75, 0.05
BLO, BHI = 0.005, 0.985
L_LONG, RHI_LONG, BHI_LONG = 96, 0.9995, 0.999
CLASSES = {"top_position": "top_pos_ratio", "top_account": "top_acc_ratio", "all_accounts": "acc_ratio"}
S3 = "https://s3-ap-northeast-1.amazonaws.com/data.binance.vision?delimiter=/&prefix=data/futures/um/daily/klines/"


def dates():
    return [d.strftime("%Y-%m-%d") for d in pd.date_range(START, END, freq="D") if d.day in DAYS_OF_MONTH]


# ---------------------------------------------------------------------------------------------------
# universe
def list_archive_symbols():
    syms, marker = [], ""
    while True:
        url = S3 + (f"&marker={marker}" if marker else "")
        xml = urllib.request.urlopen(urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"}), timeout=60).read().decode()
        got = re.findall(r"<Prefix>data/futures/um/daily/klines/([^/<]+)/</Prefix>", xml)
        syms += got
        if "<IsTruncated>true</IsTruncated>" not in xml or not got:
            break
        nm = re.search(r"<NextMarker>([^<]+)</NextMarker>", xml)
        marker = nm.group(1) if nm else f"data/futures/um/daily/klines/{got[-1]}/"
    return sorted(set(syms))


def repo_text():
    files = subprocess.check_output(["git", "ls-files"], cwd=ROOT, text=True).split()
    chunks = []
    for f in files:
        p = ROOT / f
        if p.suffix.lower() in (".zip", ".pdf", ".png", ".jpg", ".pkl", ".npy", ".npz", ".parquet", ".gz", ".olean"):
            continue
        try:
            chunks.append(p.read_text(errors="ignore").upper())
        except Exception:
            pass
    return "\n".join(chunks)


def universe():
    allsyms = list_archive_symbols()
    cand = [s for s in allsyms if s.endswith("USDT") and "_" not in s and s.isalnum()]
    text = repo_text()
    unused = [s for s in cand if s not in text]
    order = np.random.default_rng(SEED).permutation(len(unused))
    chosen, checked = [], []
    for i in order:
        s = unused[i]
        ok = all(bv._http(bv.ds_url("klines", s, d), method="HEAD")[0] == 200 for d in ("2025-01-04", "2026-09-23"))
        checked.append({"symbol": s, "files_on_both_dates": ok})
        if ok:
            chosen.append(s)
        if len(chosen) == N_SYMBOLS:
            break
    u = {"rule": "USDT perpetuals in the archive, absent from every repository text file, klines on 2025-01-04 and "
                 "2026-09-23, seeded random order", "seed": SEED, "n_archive": len(allsyms), "n_candidates": len(cand),
         "n_unused": len(unused), "checked_in_order": checked, "symbols": chosen,
         "written_utc": datetime.now(timezone.utc).isoformat()}
    UNIVERSE.write_text(json.dumps(u, indent=1) + "\n")
    return chosen


# ---------------------------------------------------------------------------------------------------
# estimators (the pilot's, restricted to the registered choices)
def ss(X, y):
    ok = np.all(np.isfinite(X), 1) & np.isfinite(y)
    if ok.sum() < X.shape[1] + 10:
        return None
    Xo, yo = X[ok] - X[ok].mean(0), y[ok] - y[ok].mean()
    return Xo.T @ Xo, Xo.T @ yo


def lags(z, n):
    return np.column_stack([np.r_[np.full(k, np.nan), z[:-k]] for k in range(1, n + 1)])


def day_stats(df):
    p1 = np.log(df["close"].to_numpy(float)) * 1e4
    fl = np.nan_to_num(df["flow"].to_numpy(float)); cf = np.concatenate([[0.0], np.cumsum(fl)])
    m = np.arange(5, 1440, 5)
    p, ret, flow = p1[m], p1[m] - p1[m - 5], cf[m + 1] - cf[m - 4]
    if not np.isfinite(p).all():
        return None
    x = p - pd.Series(p).ewm(span=SPAN, adjust=False).mean().to_numpy(); x[:SPAN] = np.nan
    out = {"k_ret": ss(lags(ret, L), flow), "price": ss(np.column_stack([flow, np.r_[np.nan, x[:-1]]]), ret),
           "k_x": ss(lags(x, L), flow)}
    if any(v is None for v in out.values()):
        return None
    # Primary 3 (optional per day): horizon-matched price-only kernel and class-tagged persistence
    out["k_ret96"] = ss(lags(ret, L_LONG), flow)
    tag_ok = "top_pos_ratio" in df and int(np.isfinite(df["top_pos_ratio"].to_numpy(float)[m]).sum()) >= 100
    for c, col in CLASSES.items():
        if tag_ok and col in df:
            R = df[col].to_numpy(float)[m]; n = (R - 1) / (R + 1)
            X = np.column_stack([np.r_[np.nan, n[:-1]], ret]); h = len(n) // 2
            out[f"tag_{c}"] = ss(X, n)
            out[f"tagA_{c}"], out[f"tagB_{c}"] = ss(X[:h], n[:h]), ss(X[h:], n[h:])   # half-days, for the jackknife
        else:
            out[f"tag_{c}"] = out[f"tagA_{c}"] = out[f"tagB_{c}"] = None
    out["tag_day"] = bool(tag_ok and out["k_ret96"] is not None)
    return out


def stack(days, keys=None):
    out = {}
    for k in keys or [k for k in days[0] if k != "tag_day"]:
        first = next((d[k] for d in days if d.get(k) is not None), None)
        if first is None:
            continue
        A = np.zeros((len(days),) + first[0].shape); b = np.zeros((len(days),) + first[1].shape)
        for i, d in enumerate(days):
            if d.get(k) is not None:
                A[i], b[i] = d[k]
        out[k] = (A, b)
    return out


def solve_w(S, name, W):
    A = np.einsum("bd,dij->bij", W, S[name][0]); b = W @ S[name][1]
    try:
        return np.linalg.solve(A, b[..., None])[..., 0]
    except np.linalg.LinAlgError:
        return (np.linalg.pinv(A) @ b[..., None])[..., 0]


def exp_fit(k, rhi=0.99, starts=((0.2, 0.8), (0.1, 0.6), (0.4, 0.95), (0.05, 0.3))):
    m = np.arange(len(k))

    def resid(th):
        w1, r1, w2, r2 = th
        return w1 * r1 ** m + w2 * r2 ** m - k
    if not np.all(np.isfinite(k)):
        return np.nan, np.nan
    best = None
    for r1, r2 in starts:
        try:
            sol = optimize.least_squares(resid, [k[0] / 2, r1, k[0] / 2, r2],
                                         bounds=([-np.inf, 0, -np.inf, 0], [np.inf, rhi, np.inf, rhi]))
            if best is None or sol.cost < best.cost:
                best = sol
        except Exception:
            pass
    if best is None:
        return np.nan, np.nan
    _, r1, _, r2 = best.x
    return (r1, r2) if r1 <= r2 else (r2, r1)


def half_life_h(r):
    r = np.asarray(r, float)
    with np.errstate(divide="ignore", invalid="ignore"):
        return np.where((r > 0) & (r < 1), 5 * np.log(0.5) / np.log(r) / 60, np.nan)


def ci(v):
    v = np.asarray(v, float); v = v[np.isfinite(v)]
    return [float(np.quantile(v, .025)), float(np.quantile(v, .975))] if len(v) > 20 else [np.nan, np.nan]


def symbol_eval(days, j):
    rng = np.random.default_rng(SEED + 101 * j); n = len(days); S = stack(days, ["k_ret", "price", "k_x"])
    W = np.vstack([np.ones(n)] + [np.bincount(rng.integers(0, n, n), minlength=n) for _ in range(B_BOOT)]).astype(float)
    pr, kx, kr = solve_w(S, "price", W), solve_w(S, "k_x", W), solve_w(S, "k_ret", W)
    kappa, beta = pr[:, 0], pr[:, 1]; Phi = kx.sum(1)
    M, M0 = -beta - kappa * Phi, -beta
    rr = np.array([exp_fit(k) for k in kr])
    rf, rs, dr = ci(rr[1:, 0]), ci(rr[1:, 1]), ci(rr[1:, 1] - rr[1:, 0])
    inside = all(np.isfinite(v) and BLO < v < BHI for v in rf + rs)
    m_ci, m0_ci = ci(M[1:]), ci(M0[1:])
    return {"n_days": n, "M": float(M[0]), "M_ci": m_ci, "decided": bool(m_ci[0] > 0 or m_ci[1] < 0),
            "sign": "safe" if m_ci[0] > 0 else "unsafe" if m_ci[1] < 0 else "undecided",
            "M_nofeedback": float(M0[0]), "M_nofeedback_ci": m0_ci,
            "decided_nofeedback": bool(m0_ci[0] > 0 or m0_ci[1] < 0),
            "kappa_Phi": float(kappa[0] * Phi[0]), "beta": float(beta[0]),
            "r_fast_ci": rf, "r_slow_ci": rs, "delta_r_ci": dr, "inside_bounds": inside,
            "identified": bool(np.isfinite(dr[0]) and (dr[0] > 0 or dr[1] < 0) and inside),
            "horizon_matched": horizon_matched([d for d in days if d.get("tag_day")], j)}


def horizon_matched(days, j):
    """Primary 3 for one symbol: tagged versus price-only (96 lags) widths of the log10 half-life interval."""
    n = len(days)
    if n < MIN_DAYS:
        return {"n_tag_days": n, "evaluable": False}
    rng = np.random.default_rng(SEED + 7 + 101 * j)
    S = stack(days, ["k_ret96"] + [f"{t}_{c}" for c in CLASSES for t in ("tag", "tagA", "tagB")])
    W = np.vstack([np.ones(n)] + [np.bincount(rng.integers(0, n, n), minlength=n) for _ in range(B_BOOT)]).astype(float)
    tagged = {}
    for c in CLASSES:
        if f"tag_{c}" in S:
            r = solve_w(S, f"tag_{c}", W)[:, 0]; hl = half_life_h(r); c_ = ci(np.log10(hl[1:]))
            if np.isfinite(c_[0]):
                tagged[c] = {"half_life_h": float(hl[0]), "log10_hl_ci": c_, "width": c_[1] - c_[0]}
                if f"tagA_{c}" in S and f"tagB_{c}" in S:
                    # split-panel jackknife (Dhaene and Jochmans 2015) against the within-day (Nickell) bias
                    rj = 2 * r - 0.5 * (solve_w(S, f"tagA_{c}", W)[:, 0] + solve_w(S, f"tagB_{c}", W)[:, 0])
                    hj = half_life_h(rj)
                    tagged[c].update({"r": float(r[0]), "r_jackknife": float(rj[0]), "r_jackknife_ci": ci(rj[1:]),
                                      "half_life_h_jackknife": float(hj[0]) if np.isfinite(hj[0]) else None,
                                      "log10_hl_jackknife_ci": ci(np.log10(hj[1:]))})
    rr = np.array([exp_fit(k, RHI_LONG, ((0.2, 0.8), (0.4, 0.95), (0.6, 0.99), (0.1, 0.998))) for k in solve_w(S, "k_ret96", W)])
    hl = half_life_h(rr[:, 1]); rs_ci = ci(rr[1:, 1]); c_ = ci(np.log10(hl[1:]))
    if not tagged or not np.isfinite(c_[0]):
        return {"n_tag_days": n, "evaluable": False}
    tag_w = float(np.mean([v["width"] for v in tagged.values()]))
    return {"n_tag_days": n, "evaluable": True, "tagged": tagged, "tagged_mean_width": tag_w,
            "price_only": {"half_life_h": float(hl[0]), "r_slow_ci": rs_ci, "log10_hl_ci": c_, "width": c_[1] - c_[0],
                           "reaches_bound": bool(rs_ci[0] <= BLO or rs_ci[1] >= BHI_LONG)},
            "width_ratio": float((c_[1] - c_[0]) / tag_w) if tag_w > 0 else float("inf"),
            "tagged_tighter": bool(tag_w < c_[1] - c_[0])}


def holm(p):
    order = np.argsort(p); m = len(p); adj = np.empty(m); run = 0.0
    for rank, i in enumerate(order):
        run = max(run, min(1.0, (m - rank) * p[i])); adj[i] = run
    return adj.tolist()


def evaluate(per):
    ev = {s: v for s, v in per.items() if v.get("n_days", 0) >= MIN_DAYS}
    n = len(ev); out = {"n_evaluable": n, "void": n < MIN_SYMBOLS}
    if out["void"]:
        return out
    dec = sum(v["decided"] for v in ev.values())
    b = sum(v["decided"] and not v["identified"] for v in ev.values())
    c = sum(v["identified"] and not v["decided"] for v in ev.values())
    p1 = float(stats.binom.sf(dec - 1, n, 0.5))
    p2 = float(stats.binom.sf(b - 1, b + c, 0.5)) if b + c > 0 else 1.0
    hm = [v["horizon_matched"] for v in ev.values() if v.get("horizon_matched", {}).get("evaluable")]
    n3 = len(hm); t3 = sum(h["tagged_tighter"] for h in hm); need3 = math.ceil(SHARE * n3)
    p3 = float(stats.binom.sf(t3 - 1, n3, 0.5)) if n3 >= MIN_SYMBOLS else 1.0
    adj = holm([p1, p2, p3]); need = math.ceil(SHARE * n)
    out.update({"threshold_count": need, "decided": dec, "identified": sum(v["identified"] for v in ev.values()),
                "mcnemar_b": b, "mcnemar_c": c, "p_raw": [p1, p2], "p_holm": adj,
                "P1_pass": bool(dec >= need and adj[0] < ALPHA), "P2_pass": bool(b > c and adj[1] < ALPHA),
                "P3_evaluable": n3, "P3_threshold_count": need3, "P3_tagged_tighter": t3,
                "P3_void": n3 < MIN_SYMBOLS,
                "P3_pass": bool(n3 >= MIN_SYMBOLS and t3 >= need3 and adj[2] < ALPHA),
                "secondary": {"decided_nofeedback": sum(v["decided_nofeedback"] for v in ev.values()),
                              "same_decision_without_feedback": sum(v["sign"] == ("safe" if v["M_nofeedback_ci"][0] > 0 else
                                                                                   "unsafe" if v["M_nofeedback_ci"][1] < 0 else "undecided")
                                                                    for v in ev.values()),
                              "feedback_negative": sum(v["kappa_Phi"] < 0 for v in ev.values()),
                              "safe": sum(v["sign"] == "safe" for v in ev.values()),
                              "unsafe": sum(v["sign"] == "unsafe" for v in ev.values()),
                              "P3_median_width_ratio": float(np.median([h["width_ratio"] for h in hm])) if hm else None,
                              "P3_ratio_at_least_3": sum(h["width_ratio"] >= 3 for h in hm),
                              "P3_price_only_reaches_bound": sum(h["price_only"]["reaches_bound"] for h in hm),
                              "P3_median_price_only_half_life_h": float(np.median([h["price_only"]["half_life_h"] for h in hm])) if hm else None,
                              "P3_median_tagged_half_life_h": float(np.median([np.median([c["half_life_h"] for c in h["tagged"].values()])
                                                                               for h in hm])) if hm else None,
                              "P3_median_tagged_r_jackknife": float(np.median([np.median([c.get("r_jackknife", np.nan) for c in h["tagged"].values()])
                                                                               for h in hm])) if hm else None,
                              "P3_price_only_overlaps_jackknife_tagged": sum(
                                  any(np.isfinite(c.get("log10_hl_jackknife_ci", [np.nan])[0]) and
                                      h["price_only"]["log10_hl_ci"][0] <= c["log10_hl_jackknife_ci"][1] and
                                      h["price_only"]["log10_hl_ci"][1] >= c["log10_hl_jackknife_ci"][0]
                                      for c in h["tagged"].values()) for h in hm)}})
    return out


def numbers_tex(e):
    if e["void"]:
        return "% generated by c2_margin_vs_identify.py\n\\newcommand{\\CtwoVoid}{void}\n"
    L_ = ["% generated by c2_margin_vs_identify.py; do not edit",
          f"\\newcommand{{\\CtwoSymbols}}{{{e['n_evaluable']}}}\\newcommand{{\\CtwoNeed}}{{{e['threshold_count']}}}",
          f"\\newcommand{{\\CtwoDecided}}{{{e['decided']}}}\\newcommand{{\\CtwoIdentified}}{{{e['identified']}}}",
          f"\\newcommand{{\\CtwoB}}{{{e['mcnemar_b']}}}\\newcommand{{\\CtwoC}}{{{e['mcnemar_c']}}}",
          f"\\newcommand{{\\CtwoPoneVerdict}}{{{'passed' if e['P1_pass'] else 'failed'}}}",
          f"\\newcommand{{\\CtwoPtwoVerdict}}{{{'passed' if e['P2_pass'] else 'failed'}}}",
          f"\\newcommand{{\\CtwoPthreeSymbols}}{{{e['P3_evaluable']}}}\\newcommand{{\\CtwoPthreeNeed}}{{{e['P3_threshold_count']}}}",
          f"\\newcommand{{\\CtwoPthreeTighter}}{{{e['P3_tagged_tighter']}}}",
          f"\\newcommand{{\\CtwoPthreeVerdict}}{{{'void' if e['P3_void'] else 'passed' if e['P3_pass'] else 'failed'}}}"]
    return "\n".join(L_) + "\n"


def gate(skip=False):
    if skip:
        return None, None, None
    assert SPEC.exists(), "Test C2 is a draft and is not registered; it cannot be run"
    sha = hashlib.sha256(SPEC.read_bytes()).hexdigest()
    assert sha == SPEC.with_suffix(".sha256").read_text().strip(), "specification hash mismatch"
    spec = json.loads(SPEC.read_text())
    for key, f in (("c2_sha256", "c2_margin_vs_identify.py"), ("binance_vision_sha256", "binance_vision.py")):
        assert hashlib.sha256((HERE / f).read_bytes()).hexdigest() == spec[key], f"{f} changed after registration"
    reg = subprocess.check_output(["git", "log", "-1", "--format=%H", "--", str(SPEC.relative_to(ROOT))], cwd=ROOT, text=True).strip()
    assert reg, "the specification is not committed"
    return spec, sha, reg


def run(cache_dir=None, threads=16, resume=False, skip_gate=False, symbols=None, day_list=None):
    spec, sha, reg = gate(skip_gate)
    if not skip_gate:
        c = json.loads(COUNTER.read_text())
        if resume:
            assert c["opens"] == 1, "nothing to resume"
        else:
            assert c["opens"] == 0, "Test C2 was already opened; it runs once"
            COUNTER.write_text(json.dumps({"opens": 1, "spec_sha256": sha, "registration_commit": reg,
                                           "opened_utc": datetime.now(timezone.utc).isoformat()}, indent=2) + "\n")
    syms = symbols or (json.loads(UNIVERSE.read_text())["symbols"] if (resume and UNIVERSE.exists()) else universe())
    ds = day_list or dates()
    frames = {}
    with ThreadPoolExecutor(max_workers=threads) as ex:
        futs = {ex.submit(bv.get_day, s, d, cache_dir, False): (s, d) for s in syms for d in ds}
        for i, f in enumerate(as_completed(futs)):
            s, d = futs[f]
            df, _ = f.result()
            if df is not None:
                st = day_stats(df)
                if st is not None:
                    frames.setdefault(s, []).append((d, st))
            if (i + 1) % 300 == 0:
                print(f"  {i + 1}/{len(futs)} symbol-days", flush=True)
    per = {}
    for j, s in enumerate(syms):
        days = [st for _, st in sorted(frames.get(s, []), key=lambda t: t[0])]
        per[s] = symbol_eval(days, j) if len(days) >= MIN_DAYS else {"n_days": len(days), "excluded": "fewer than 30 valid days"}
        if "M" in per[s]:
            print(f"  {s}: days={len(days)} margin={per[s]['sign']} identified={per[s]['identified']}", flush=True)
    res = {"test": "C2", "spec_sha256": sha, "registration_commit": reg, "run_utc": datetime.now(timezone.utc).isoformat(),
           "symbols": syms, "dates": ds, "per_symbol": per, "evaluation": evaluate(per)}
    RESULT.write_text(json.dumps(res, indent=1, default=float) + "\n")
    NUMBERS.write_text(numbers_tex(res["evaluation"]))
    DLLOG.write_text(json.dumps(bv.DL_LOG, indent=0) + "\n")
    print(json.dumps(res["evaluation"], indent=1))
    return res


def selftest():
    rng = np.random.default_rng(2)
    per = {}
    for j in range(25):
        days = []
        for _ in range(40):
            T = 1440; p = np.cumsum(rng.normal(0, 3, T)); fl = rng.normal(0, 1, T) * 0.01
            p = p - 0.5 * (p - pd.Series(p).ewm(span=60, adjust=False).mean().to_numpy())  # reversion
            n5 = np.zeros(288)
            for t in range(1, 288):
                n5[t] = 0.985 * n5[t - 1] + rng.normal(0, 0.02)
            R = np.repeat((1 + n5) / (1 - n5), 5)
            st = day_stats(pd.DataFrame({"close": 100 * np.exp(p / 1e4), "flow": fl, "top_pos_ratio": R,
                                         "top_acc_ratio": R, "acc_ratio": R}))
            if st is not None:
                days.append(st)
        per[f"S{j}"] = symbol_eval(days, j)
    e = evaluate(per)
    print(json.dumps({k: e[k] for k in ("n_evaluable", "decided", "identified", "mcnemar_b", "mcnemar_c", "P1_pass", "P2_pass",
                                        "P3_evaluable", "P3_tagged_tighter", "P3_pass")}))
    print(json.dumps({k: v for k, v in e["secondary"].items() if k.startswith("P3")}))
    # within-day demeaning biases a day-pooled AR(1) rate down by about (1 + 3r)/T (Nickell); check against that value
    hl = e["secondary"]["P3_median_tagged_half_life_h"]; r_b = 0.985 - (1 + 3 * 0.985) / 287
    hl_b = 5 * np.log(0.5) / np.log(r_b) / 60
    assert e["n_evaluable"] == 25 and e["P3_evaluable"] == 25 and abs(hl / hl_b - 1) < 0.25, (hl, hl_b)
    rj = e["secondary"]["P3_median_tagged_r_jackknife"]
    assert abs(rj - 0.985) < abs(0.5 ** (5 / (60 * hl)) - 0.985), ("jackknife should move the rate toward the truth", rj)
    assert numbers_tex(e).startswith("%")
    try:
        gate()
        raise SystemExit("gate should refuse an unregistered draft")
    except AssertionError as err:
        print("gate refuses as expected:", err)
    print("selftest: PASS")


if __name__ == "__main__":
    ap = argparse.ArgumentParser(); ap.add_argument("--selftest", action="store_true")
    if ap.parse_args().selftest:
        selftest()
