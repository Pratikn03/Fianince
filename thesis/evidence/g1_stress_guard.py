"""Test G1: does the summed-response guard beat a volatility limit in stress hours? (spec checks/prereg/G1_stress_guard.json)

Chapter 3's backtests found that, at matched average exposure, a limit built on the amplification multiple
does not beat a plain volatility limit over all hours. The theory concerns worst-case loss, which matters
when the book is stressed; this test asks the question there, on untouched days.

Data: the 20 thin perpetuals of Chapter 3. Training: the 10th and 24th of each month of 2024 (the training
days of Chapter 3). Test: the 8th, 29th and 31st of every month from January 2025 to September 2026, minus
two dates used before (2026-07-08, 2026-04-29). 1-minute klines, validated order-book depth (bookDepth) and
metrics from data.binance.vision; a symbol-day is valid with depth on at least 80% of minutes.

Hourly blocks (06-23 UTC) and rules are the Chapter 3 code (Part 6, cells Z1, Z5): a dealer sizes its
position as q = c_s / R, with c_s setting the training mean of q to 1 for each symbol and rule; the hour's
loss is q x MAE_60; tail-loss ratio TLR = ES95(loss) / mean(q). Rules:
  vol         R = rv_360 (six-hour volatility)
  amp_vol     R = rv_360 x GM^theta, GM the gain multiple S60 / |h_0|, theta in {0, .25, .5, .75, 1} chosen on
              training data (minimum training TLR)
  guard       R = U6 x S60 (six-hour shock envelope times summed response: the Chapter 3 guard)
Stress hours: test hours whose rv_360 is at least the symbol's training 90th percentile of rv_360.

G1  amp_vol beats vol in stress hours: log TLR(amp_vol) - log TLR(vol) has a 95% date-block bootstrap
    interval below zero and a Holm-adjusted one-sided bootstrap p (share of draws >= 0) below 0.05.
G2  guard beats vol in stress hours: the same with the guard.
Holm across G1 and G2. Secondary: the same comparisons over all test hours.
"""

import argparse
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
import subprocess
import sys

import numpy as np
import pandas as pd

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import binance_vision as bv  # noqa: E402
import e2_analysis as P2  # noqa: E402  (Paper 2 estimators, registered with the E2 addendum)

THESIS = HERE.parent
ROOT = THESIS.parent
SPEC = THESIS / "checks/prereg/G1_stress_guard.json"
COUNTER = THESIS / "checks/prereg/G1_unlock.json"
RESULT = HERE / "G1_results.json"
NUMBERS = THESIS / "checks/G1_numbers.tex"
DLLOG = HERE / "G1_download_log.json"

SYMBOLS = P2.SYMBOLS
EXCLUDE = {"2026-07-08", "2026-04-29"}
SEED = 20261026
H_GUARD = 60
THETA_GRID = [0.0, 0.25, 0.5, 0.75, 1.0]
CTRL = P2.CTRL


def train_dates():
    return [d.strftime("%Y-%m-%d") for d in pd.date_range("2024-01-01", "2024-12-31") if d.day in (10, 24)]


def test_dates():
    return [d.strftime("%Y-%m-%d") for d in pd.date_range("2025-01-01", "2026-09-30")
            if d.day in (8, 29, 31) and d.strftime("%Y-%m-%d") not in EXCLUDE]


def rng(offset=0):
    return np.random.default_rng(SEED + offset)


# ---- Part 6 code: hourly blocks with the guard's inputs ------------------------------------------
def day_blocks(df, s, d, flow_scale):
    p, u, dd_, x, tot = P2.prep(df, flow_scale)
    rows = []
    for hr in range(6, 24):
        t = hr * 60
        w, h, f = slice(t - 360, t), slice(t - 60, t), slice(t, min(t + 61, 1440))
        row = {"symbol": s, "date": d, "hour": hr}
        est = P2.fit_t6(p[w], u[w], dd_[w], x[w])
        if est is not None:
            imp = P2.impulse_t6(est["a"], est["phi"], est["kappa"], est["r"], est["eps"], est["eta"], est["q"], L=H_GUARD)
            ok = np.all(np.isfinite(imp)) and abs(imp[0]) > 1e-12
            S60 = float(np.sum(np.abs(imp))) if ok else np.nan
            row.update({"S60": S60, "gain_multiple": S60 / abs(imp[0]) if ok else np.nan})
        au = np.abs(u[w]); au = au[np.isfinite(au)]
        row.update({"rv_360": np.nanstd(np.diff(p[w])), "U6": float(np.quantile(au, 0.95)) if len(au) > 60 else np.nan,
                    "MAE_60": float(np.nanmax(np.abs(p[f] - p[t - 1])))})
        rows.append(row)
    return rows


def es95(v):
    v = np.asarray(v, float); q = np.quantile(v, 0.95); return float(v[v >= q].mean())


def guard_frame(D, rules):
    G = D[["symbol", "date", "hour", "split", "MAE_60", "stress"]].copy()
    for r, fn in rules.items():
        G["R_" + r] = fn(D).astype(float).where(lambda v: v > 0)
    G = G.dropna(subset=["MAE_60"] + ["R_" + r for r in rules])
    for r in rules:
        lo, hi = G.loc[G["split"] == "train", "R_" + r].quantile([0.01, 0.99])
        G["R_" + r] = G["R_" + r].clip(lo, hi)
        inv = 1.0 / G["R_" + r]
        c = inv[G["split"] == "train"].groupby(G["symbol"]).mean()
        G["q_" + r] = inv / G["symbol"].map(c)
        G["L_" + r] = G["q_" + r] * G["MAE_60"]
    return G[G["symbol"].isin(c.index)]


def tlr(X, r):
    return es95(X["L_" + r]) / X["q_" + r].mean()


def choose_theta(D):
    res = {}
    for th in THETA_GRID:
        G = guard_frame(D, {"amp_vol": (lambda X, th=th: X["rv_360"] * X["gain_multiple"] ** th)})
        res[th] = tlr(G[G["split"] == "train"], "amp_vol")
    return min(res, key=res.get), res


def compare(T, rules, ref="vol", B=2000, seed=77):
    T = T.sort_values(["date", "symbol", "hour"])
    point = {r: tlr(T, r) for r in rules}
    Rb = rng(seed); dd = T["date"].to_numpy(); ud = np.unique(dd); pos = {d: np.where(dd == d)[0] for d in ud}
    bs = {r: [] for r in rules if r != ref}
    for _ in range(B):
        X = T.iloc[np.concatenate([pos[d] for d in Rb.choice(ud, len(ud))])]
        tr = tlr(X, ref)
        for r in bs:
            bs[r].append(np.log(tlr(X, r)) - np.log(tr))
    out = {"n_hours": len(T), "n_dates": len(ud), "TLR": point}
    for r, v in bs.items():
        v = np.array(v)
        out[r] = {"log_TLR_minus_vol": float(np.log(point[r]) - np.log(point[ref])),
                  "ci": [float(np.quantile(v, .025)), float(np.quantile(v, .975))], "p_one_sided": float(np.mean(v >= 0))}
    return out


def evaluate(ZB):
    theta, theta_tr = choose_theta(ZB)
    rules = {"vol": lambda X: X["rv_360"], "amp_vol": lambda X: X["rv_360"] * X["gain_multiple"] ** theta,
             "guard": lambda X: X["U6"] * X["S60"]}
    G = guard_frame(ZB, rules)
    test = G[G["split"] == "test"]
    stress = compare(test[test["stress"]], list(rules), seed=77)
    allh = compare(test, list(rules), seed=78)
    p = [stress["amp_vol"]["p_one_sided"], stress["guard"]["p_one_sided"]]
    adj = P2.holm(p)
    g1 = bool(stress["amp_vol"]["ci"][1] < 0 and adj[0] < 0.05)
    g2 = bool(stress["guard"]["ci"][1] < 0 and adj[1] < 0.05)
    return {"theta": theta, "theta_training_TLR": {str(k): v for k, v in theta_tr.items()}, "stress": stress,
            "all_hours": allh, "p_raw": p, "p_holm": adj, "G1_pass": g1, "G2_pass": g2}


def build(syms, train, test, cache_dir, threads):
    panel = {}
    with ThreadPoolExecutor(max_workers=threads) as ex:
        futs = {ex.submit(bv.get_day, s, d, cache_dir, True): (s, d) for s in syms for d in train + test}
        for i, f in enumerate(as_completed(futs)):
            s, d = futs[f]; df, st = f.result()
            if df is not None and st.get("depth_day_ok"):
                panel[(s, d)] = df
            if (i + 1) % 300 == 0:
                print(f"  {i + 1}/{len(futs)} symbol-days", flush=True)
    tr = set(train)
    scale = {}
    for s in syms:
        v = [np.nanmedian(np.abs(panel[(s, d)]["flow"].to_numpy())) for d in train if (s, d) in panel]
        scale[s] = float(np.nanmedian(v)) if v and np.nanmedian(v) > 0 else 1.0
    rows = []
    for (s, d), df in sorted(panel.items()):
        rows += day_blocks(df, s, d, scale[s])
    ZB = pd.DataFrame(rows)
    ZB["split"] = np.where(ZB["date"].isin(tr), "train", "test")
    q90 = ZB[ZB["split"] == "train"].groupby("symbol")["rv_360"].quantile(0.9)
    ZB["stress"] = (ZB["split"] == "test") & (ZB["rv_360"] >= ZB["symbol"].map(q90))
    return ZB, scale


def numbers_tex(e):
    s = e["stress"]
    f = lambda x: f"{100 * (np.exp(x) - 1):+.1f}"
    return ("% generated by g1_stress_guard.py; do not edit\n"
            f"\\newcommand{{\\GoneVerdictA}}{{{'passed' if e['G1_pass'] else 'failed'}}}"
            f"\\newcommand{{\\GoneVerdictB}}{{{'passed' if e['G2_pass'] else 'failed'}}}\n"
            f"\\newcommand{{\\GoneAmpPct}}{{{f(s['amp_vol']['log_TLR_minus_vol'])}\\%}}"
            f"\\newcommand{{\\GoneGuardPct}}{{{f(s['guard']['log_TLR_minus_vol'])}\\%}}"
            f"\\newcommand{{\\GoneStressHours}}{{{s['n_hours']}}}\n")


def gate():
    spec = json.loads(SPEC.read_text())
    sha = hashlib.sha256(SPEC.read_bytes()).hexdigest()
    assert sha == SPEC.with_suffix(".sha256").read_text().strip(), "specification hash mismatch"
    for key, f in (("g1_sha256", "g1_stress_guard.py"), ("e2_analysis_sha256", "e2_analysis.py"),
                   ("binance_vision_sha256", "binance_vision.py")):
        assert hashlib.sha256((HERE / f).read_bytes()).hexdigest() == spec[key], f"{f} changed after registration"
    rel = str(SPEC.relative_to(ROOT))
    commit = subprocess.check_output(["git", "log", "-1", "--format=%H", "--", rel], cwd=ROOT, text=True).strip()
    assert commit, "specification not committed"
    assert json.loads(COUNTER.read_text())["opens"] == 0, "G1 was already opened"
    return sha, commit


def run(cache_dir=None, threads=12, resume=False, skip_gate=False, syms=None, train=None, test=None):
    if skip_gate:
        sha, commit = "test", None
    elif resume:
        c = json.loads(COUNTER.read_text()); assert c["opens"] == 1, "nothing to resume"
        sha, commit = c["spec_sha256"], c["registration_commit"]
    else:
        sha, commit = gate()
        COUNTER.write_text(json.dumps({"opens": 1, "spec_sha256": sha, "registration_commit": commit,
                                       "opened_utc": datetime.now(timezone.utc).isoformat()}, indent=2) + "\n")
    ZB, scale = build(syms or SYMBOLS, train or train_dates(), test or test_dates(), cache_dir, threads)
    ev = evaluate(ZB)
    res = {"test": "G1", "spec_sha256": sha, "registration_commit": commit, "run_utc": datetime.now(timezone.utc).isoformat(),
           "flow_scale": scale, "blocks": ZB.groupby("split").size().to_dict(), "stress_hours": int(ZB["stress"].sum()),
           "evaluation": ev}
    if not skip_gate:
        RESULT.write_text(json.dumps(res, indent=1, default=float) + "\n")
        NUMBERS.write_text(numbers_tex(ev))
        DLLOG.write_text(json.dumps(bv.DL_LOG, indent=0) + "\n")
    print(json.dumps(ev, indent=1, default=float))
    return res


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--run", action="store_true"); ap.add_argument("--cache", default=None)
    a = ap.parse_args()
    if a.run:
        run(a.cache)
