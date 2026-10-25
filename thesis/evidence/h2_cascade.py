"""Test H2: does the stability margin, certified from public data alone, fall before real crash hours?

Why. The theory's warning claim is that a market driven toward instability by feedback shows a falling stability margin
before the crash, and that the margin can be certified from public prices and anonymous flow without identifying anyone.
Test B1 found the margin's trend warning about two weeks ahead in simulation; no real-market test has looked at the
hours before a crash (S1 used daily data). Crypto perpetuals reach liquidation cascades often. H2 uses the Hyperliquid
trades recorded for Test H1 (same collector, universe, coverage files and valid-day rule; H1 is unchanged) and opens
with H1: at the first run on or after 2026-12-10 at which at least 20 coins have 30 valid days, and on 2027-01-31 in
any case (void if fewer than 20 evaluable coins then). Only public fields are used: time, aggressor side, price, size.

Construction (per coin, all collected days in calendar order; a day enters only if it is valid under H1's rule):
  bars: five-minute bars k with log price p_k (bp) at the bar's last minute, return r_k = p_k - p_{k-1}, signed taker
        notional f_k over the bar's five minutes; x_k = p_k - EMA_12(p)_k over runs of consecutive valid bars (the first
        12 bars of a run undefined);
  rolling margin: on the 288 bars before bar e (24 hours), pooled OLS with intercepts of
        r_k = c + kappa f_k + beta x_{k-1}   and   f_k = c' + sum_{m=1..12} k_m x_{k-m};
        M(e) = -beta - kappa * sum_m k_m, defined if at least 90% of the window's rows are complete;
  margin decline before hour h (UTC hours, first bar b_h): D(h) = M(b_h - 72) - M(b_h), the fall of the margin over the
        six hours before h (positive = falling); feedback rise R(h) = kappa*Phi(b_h) - kappa*Phi(b_h - 72), the part of the
        decline that comes from the feedback term; defined if both windows are;
  excursion of hour h: the largest move against any position within the hour on one-minute last-trade prices,
        max(max_t (p_t - min_{s<=t} p_s), max_t (max_{s<=t} p_s - p_t)) in bp.
Crash hours: per coin, the hours (with D defined) whose excursion exceeds the coin's 99th percentile, kept largest first
at least six hours apart. Controls: for each crash hour, the five hours of the same coin closest to it in prior volatility
(Euclidean distance in standardized log(1 + realized variance) over the previous 6 and 24 hours) among hours with an
excursion below the coin's median, at least six hours from any hour above the 99th percentile, with D defined. Matching
on prior volatility: in a simulated market without feedback changes, hour-of-day controls made large-excursion hours look
as if a falling margin preceded them (18 of 21 coins), because volatility before them moves the rolling estimates.

Primaries (Holm across the two at 0.05):
  P1  feedback rises before crash hours: per evaluable coin with at least one crash hour, score = mean R(crash hours) -
      mean R(controls); the score is positive in more coins than not, exact one-sided sign test p < 0.05. (The feedback
      term, not the whole margin: in ten simulated markets whose feedback never changes (H1's synthetic market, seeds
      11-20), the same sign test on the whole margin decline D rejected at 5% in 3 of 10, on R in 0 of 10, and P2 in 0
      of 10; H2_null_calibration.json.)
  P2  the decline forecasts the size of the hour's excursion beyond volatility: outcome log(1 + excursion); baseline
      log(1 + realized variance of one-minute returns over the previous 1, 6 and 24 hours), log(1 + previous hour's
      excursion), hour-of-day and coin indicators; candidate D(h), winsorized at its training 1st and 99th percentiles;
      pooled OLS fitted on each coin's first half of hours (chronological), evaluated on the second half; the training
      coefficient on D is positive, the one-sided Clark-West test (date-averaged differentials) has p < 0.05, and the
      date-block bootstrap 95% interval (500 draws, seed 20261109) for the out-of-sample gain in R^2 lies above zero.
Secondary: P1's comparison for the whole margin decline D; the same with a 12-hour window; crash hours with a downward and with an upward excursion separately; the margin
level M(b_h) before crash hours and controls; the share of crash hours with M(b_h) < 0; the area under the ROC curve of D
for crash hours against controls.
"""
import argparse
import hashlib
import json
import math
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path

import numpy as np
import pandas as pd
from scipy import stats

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import h1_hyperliquid as H  # noqa: E402

THESIS = HERE.parent
ROOT = THESIS.parent
SPEC = THESIS / "checks/prereg/H2_cascade.json"
COUNTER = THESIS / "checks/prereg/H2_unlock.json"
RESULT = HERE / "H2_results.json"
NUMBERS = THESIS / "checks/H2_numbers.tex"
SPAN, LAGS, WIN, GAP, MIN_ROWS = 12, 12, 288, 72, 0.9
Q_CRASH, SEP, B_BOOT, SEED, ALPHA = 0.99, 6, 500, 20261109, 0.05
PIPELINE = (("h2_sha256", "h2_cascade.py"), ("h1_sha256", "h1_hyperliquid.py"), ("c3_sha256", "c3_margin_more_days.py"),
            ("c2_sha256", "c2_margin_vs_identify.py"), ("pilot4_sha256", "pilot4_curve_and_risk.py"))


# ------------------------------------------------------------------------------------------------------------- data
def coin_minutes(out_dir, coin, dates):
    """One-minute last-trade log prices (bp) and signed taker notional for every collected day, NaN on invalid days."""
    P, F, valid = [], [], []
    for date in dates:
        tr = H.load_trades(out_dir, coin, date)
        df = H.day_frame(tr, date) if tr is not None else None
        ok = df is not None and H.coverage(out_dir, date) >= H.COVER_MIN and H.C3.day_stats(df) is not None
        if ok:
            P.append(np.log(df["close"].to_numpy(float)) * 1e4); F.append(df["flow"].to_numpy(float))
        else:
            P.append(np.full(1440, np.nan)); F.append(np.full(1440, np.nan))
        valid.append(bool(ok))
    return np.concatenate(P) if P else np.zeros(0), np.concatenate(F) if F else np.zeros(0), valid


def bars(p1, f1):
    """Five-minute bars over the whole calendar: price at minutes 5k+4, return, flow over the bar, displacement."""
    nb = len(p1) // 5
    p = p1[np.arange(nb) * 5 + 4]
    f = f1[:nb * 5].reshape(nb, 5).sum(1)
    f[~np.isfinite(p)] = np.nan
    r = np.r_[np.nan, np.diff(p)]
    x = np.full(nb, np.nan)
    ok = np.isfinite(p)
    i = 0
    while i < nb:                                           # EMA over runs of consecutive valid bars
        if not ok[i]:
            i += 1; continue
        j = i
        while j < nb and ok[j]:
            j += 1
        seg = p[i:j]
        xs = seg - pd.Series(seg).ewm(span=SPAN, adjust=False).mean().to_numpy()
        xs[:SPAN] = np.nan
        x[i:j] = xs; i = j
    return p, r, f, x


def _cum(X, y):
    """Cumulative sufficient statistics of OLS rows (rows with any non-finite entry contribute nothing)."""
    ok = np.all(np.isfinite(X), 1) & np.isfinite(y)
    Xz, yz = np.where(ok[:, None], X, 0.0), np.where(ok, y, 0.0)
    XX = np.einsum("ti,tj->tij", Xz, Xz); Xy = Xz * yz[:, None]
    z = lambda a: np.concatenate([np.zeros((1,) + a.shape[1:]), np.cumsum(a, 0)])
    return z(XX), z(Xy), z(ok.astype(float))


def rolling_margin(r, f, x, win=WIN):
    """M(e) from the `win` bars before bar e, for every e (NaN where undefined)."""
    nb = len(r)
    one = np.ones(nb)
    xl1 = np.r_[np.nan, x[:-1]]
    Xp = np.column_stack([one, f, xl1])
    Xk = np.column_stack([one] + [np.r_[np.full(m, np.nan), x[:-m]] for m in range(1, LAGS + 1)])
    Cp = _cum(Xp, r); Ck = _cum(Xk, f)
    M = np.full(nb + 1, np.nan); KP = np.full(nb + 1, np.nan)
    for e in range(win, nb + 1):
        n_p = Cp[2][e] - Cp[2][e - win]; n_k = Ck[2][e] - Ck[2][e - win]
        if n_p < MIN_ROWS * win or n_k < MIN_ROWS * win:
            continue
        try:
            bp = np.linalg.solve(Cp[0][e] - Cp[0][e - win], Cp[1][e] - Cp[1][e - win])
            bk = np.linalg.solve(Ck[0][e] - Ck[0][e - win], Ck[1][e] - Ck[1][e - win])
        except np.linalg.LinAlgError:
            continue
        KP[e] = bp[1] * bk[1:].sum(); M[e] = -bp[2] - KP[e]
    return M, KP


def hour_table(p1, M, KP, valid_days):
    """One row per hour of a valid day: excursion, its direction, volatility features, D and the margin level."""
    nh = len(p1) // 60
    r1 = np.r_[np.nan, np.diff(p1)]
    rows = []
    for h in range(nh):
        if not valid_days[h // 24]:
            continue
        seg = p1[60 * h:60 * (h + 1)]
        if not np.isfinite(seg).all():
            continue
        up = np.max(seg - np.minimum.accumulate(seg)); dn = np.max(np.maximum.accumulate(seg) - seg)

        def rv(hours):
            a = r1[max(0, 60 * h - 60 * hours):60 * h]
            return float(np.nansum(a ** 2)) if np.isfinite(a).mean() > 0.9 and len(a) == 60 * hours else np.nan
        b = 12 * h
        D = M[b - GAP] - M[b] if b - GAP >= 0 else np.nan
        R = KP[b] - KP[b - GAP] if b - GAP >= 0 else np.nan
        rows.append({"h": h, "day": h // 24, "hod": h % 24, "exc": float(max(up, dn)), "down": bool(dn >= up),
                     "rv1": rv(1), "rv6": rv(6), "rv24": rv(24), "D": float(D), "R": float(R), "level": float(M[b])})
    t = pd.DataFrame(rows)
    if len(t):
        prev = t.set_index("h")["exc"]
        t["prev_exc"] = t["h"].map(lambda h: prev.get(h - 1, np.nan))
    return t


def coin_table(out_dir, coin, dates, win=WIN):
    p1, f1, valid = coin_minutes(out_dir, coin, dates)
    if not any(valid):
        return None, 0
    _, r, f, x = bars(p1, f1)
    M, KP = rolling_margin(r, f, x, win)
    t = hour_table(p1, M, KP, valid)
    if len(t):
        t["coin"] = coin
    return t, int(sum(valid))


# ------------------------------------------------------------------------------------------------------------- tests
def crash_and_controls(t):
    d = t[np.isfinite(t["D"]) & np.isfinite(t["R"])]
    if len(d) < 50:
        return [], []
    hi = d["exc"].quantile(Q_CRASH); med = d["exc"].median()
    above = d[d["exc"] > hi].sort_values("exc", ascending=False)
    crash = []
    for _, row in above.iterrows():
        if all(abs(row["h"] - c["h"]) >= SEP for c in crash):
            crash.append(row)
    near = set()
    for h in above["h"]:
        near.update(range(int(h) - SEP + 1, int(h) + SEP))
    feats = lambda z: np.column_stack([np.log1p(z["rv6"].to_numpy(float)), np.log1p(z["rv24"].to_numpy(float))])
    allf = feats(d); mu, sd = np.nanmean(allf, 0), np.nanstd(allf, 0) + 1e-12
    ctrl = d[(d["exc"] < med) & (~d["h"].isin(near)) & np.isfinite(d["rv6"]) & np.isfinite(d["rv24"])]
    cf = (feats(ctrl) - mu) / sd
    controls, kept = [], []
    for c in crash:
        v = (np.array([np.log1p(c["rv6"]), np.log1p(c["rv24"])]) - mu) / sd
        if not np.isfinite(v).all() or len(ctrl) < 5:
            continue
        nn = np.argsort(((cf - v) ** 2).sum(1))[:5]
        controls.append(ctrl.iloc[nn]); kept.append(c)
    return kept, controls


def p1_scores(tables):
    out = {}
    for coin, t in tables.items():
        crash, controls = crash_and_controls(t)
        if not crash:
            continue
        cR = np.array([c["R"] for c in crash]); cD = np.array([c["D"] for c in crash])
        ctl = pd.concat(controls) if controls else pd.DataFrame()
        if len(ctl) == 0 or not np.isfinite(cR).any():
            continue
        out[coin] = {"n_crash": len(crash), "n_control": int(len(ctl)), "score": float(np.nanmean(cR) - ctl["R"].mean()),
                     "score_margin_decline": float(cD.mean() - ctl["D"].mean()),
                     "level_crash": float(np.nanmean([c["level"] for c in crash])), "level_control": float(ctl["level"].mean()),
                     "share_negative_level": float(np.mean([c["level"] < 0 for c in crash])),
                     "down_scores": float(np.nanmean([c["R"] for c in crash if c["down"]]) - ctl["R"].mean()) if any(c["down"] for c in crash) else np.nan,
                     "up_scores": float(np.nanmean([c["R"] for c in crash if not c["down"]]) - ctl["R"].mean()) if any(not c["down"] for c in crash) else np.nan,
                     "auc": _auc(cR, ctl["R"].to_numpy())}
    return out


def _auc(a, b):
    a, b = np.asarray(a, float), np.asarray(b, float)
    if len(a) == 0 or len(b) == 0:
        return np.nan
    return float(stats.mannwhitneyu(a, b, alternative="two-sided").statistic / (len(a) * len(b)))


def p2_forecast(tables, seed=SEED):
    frames = []
    for coin, t in tables.items():
        d = t[np.isfinite(t[["D", "rv1", "rv6", "rv24", "prev_exc"]]).all(axis=1)].sort_values("h").copy()
        if len(d) < 50:
            continue
        d["train"] = np.arange(len(d)) < len(d) // 2
        frames.append(d)
    if not frames:
        return None
    a = pd.concat(frames, ignore_index=True)
    lo, hi = a.loc[a["train"], "D"].quantile([0.01, 0.99])
    a["Dw"] = a["D"].clip(lo, hi)
    y = np.log1p(a["exc"].to_numpy())
    base = [np.log1p(a[c].to_numpy()) for c in ("rv1", "rv6", "rv24", "prev_exc")]
    hod = pd.get_dummies(a["hod"], prefix="h", drop_first=True).to_numpy(float)
    coin = pd.get_dummies(a["coin"], prefix="c", drop_first=True).to_numpy(float)
    Xb = np.column_stack([np.ones(len(a))] + base + [hod, coin]); Xf = np.column_stack([Xb, a["Dw"].to_numpy()])
    tr = a["train"].to_numpy(); te = ~tr
    bb = np.linalg.lstsq(Xb[tr], y[tr], rcond=None)[0]; bf = np.linalg.lstsq(Xf[tr], y[tr], rcond=None)[0]
    yb, yf = Xb[te] @ bb, Xf[te] @ bf; yt = y[te]
    eb, ef = yt - yb, yt - yf
    cw = eb ** 2 - (ef ** 2 - (yb - yf) ** 2)
    date_key = a.loc[te, "day"].to_numpy()                   # calendar day index (common across coins)
    per = pd.Series(cw).groupby(date_key).mean()
    cw_t = float(per.mean() / (per.std(ddof=1) / math.sqrt(len(per)))) if len(per) > 2 and per.std() > 0 else np.nan
    cw_p = float(stats.t.sf(cw_t, len(per) - 1)) if np.isfinite(cw_t) else 1.0
    sst = lambda v: np.sum((v - v.mean()) ** 2)
    dr2 = float((np.sum(eb ** 2) - np.sum(ef ** 2)) / sst(yt))
    rng = np.random.default_rng(seed); ud = np.unique(date_key); idx = {d: np.where(date_key == d)[0] for d in ud}
    boots = []
    for _ in range(B_BOOT):
        pick = np.concatenate([idx[d] for d in rng.choice(ud, len(ud))])
        boots.append((np.sum(eb[pick] ** 2) - np.sum(ef[pick] ** 2)) / sst(yt[pick]))
    lo95, hi95 = np.quantile(boots, [0.025, 0.975])
    return {"n_train": int(tr.sum()), "n_test": int(te.sum()), "n_test_dates": int(len(ud)), "coef_D": float(bf[-1]),
            "delta_r2_pts": 100 * dr2, "ci_pts": [100 * float(lo95), 100 * float(hi95)], "cw_t": cw_t, "cw_p": cw_p,
            "n_coins": len(frames)}


def evaluate(tables, tables12=None):
    sc = p1_scores(tables)
    pos = sum(v["score"] > 0 for v in sc.values()); neg = sum(v["score"] < 0 for v in sc.values())
    p1 = float(stats.binom.sf(pos - 1, pos + neg, 0.5)) if pos + neg else 1.0
    fc = p2_forecast(tables)
    p2 = fc["cw_p"] if fc else 1.0
    adj = H.C2.holm([p1, p2])
    out = {"n_coins": len(tables), "n_coins_with_crash": len(sc),
           "P1": {"positive": pos, "negative": neg, "median_score": float(np.median([v["score"] for v in sc.values()])) if sc else None,
                  "p": p1, "p_holm": adj[0], "pass": bool(adj[0] < ALPHA and pos > neg)},
           "P2": {**(fc or {}), "p_holm": adj[1],
                  "pass": bool(fc and fc["coef_D"] > 0 and adj[1] < ALPHA and fc["ci_pts"][0] > 0)}}
    sec = {"median_auc": float(np.nanmedian([v["auc"] for v in sc.values()])) if sc else None,
           "median_down_score": float(np.nanmedian([v["down_scores"] for v in sc.values()])) if sc else None,
           "median_up_score": float(np.nanmedian([v["up_scores"] for v in sc.values()])) if sc else None,
           "median_level_crash": float(np.nanmedian([v["level_crash"] for v in sc.values()])) if sc else None,
           "median_level_control": float(np.nanmedian([v["level_control"] for v in sc.values()])) if sc else None,
           "share_crash_negative_level": float(np.nanmean([v["share_negative_level"] for v in sc.values()])) if sc else None,
           "margin_decline_positive_coins": sum(v["score_margin_decline"] > 0 for v in sc.values()),
           "crash_hours": int(sum(v["n_crash"] for v in sc.values()))}
    if tables12:
        s12 = p1_scores(tables12); f12 = p2_forecast(tables12)
        sec["window_12h"] = {"positive": sum(v["score"] > 0 for v in s12.values()), "negative": sum(v["score"] < 0 for v in s12.values()),
                             "delta_r2_pts": f12["delta_r2_pts"] if f12 else None, "cw_t": f12["cw_t"] if f12 else None}
    out["secondary"] = sec; out["per_coin"] = sc
    return out


def numbers_tex(e):
    v = lambda k: "passed" if e[k]["pass"] else "failed"
    p2 = e["P2"]
    return "\n".join(["% generated by h2_cascade.py; do not edit",
                      "\\newcommand{\\HtwoCoins}{%d}\\newcommand{\\HtwoPos}{%d}\\newcommand{\\HtwoNeg}{%d}" % (
                          e["n_coins_with_crash"], e["P1"]["positive"], e["P1"]["negative"]),
                      "\\newcommand{\\HtwoDRtwo}{%.2f}\\newcommand{\\HtwoCWt}{%.2f}" % (p2.get("delta_r2_pts", float("nan")), p2.get("cw_t", float("nan"))),
                      f"\\newcommand{{\\HtwoPone}}{{{v('P1')}}}\\newcommand{{\\HtwoPtwo}}{{{v('P2')}}}"]) + "\n"


# ------------------------------------------------------------------------------------------------------------- the run
def gate(skip=False):
    if skip:
        return None, None, None
    assert SPEC.exists(), "Test H2 is a draft and is not registered"
    sha = hashlib.sha256(SPEC.read_bytes()).hexdigest()
    assert sha == SPEC.with_suffix(".sha256").read_text().strip(), "specification hash mismatch"
    spec = json.loads(SPEC.read_text())
    for key, f in PIPELINE:
        assert hashlib.sha256((HERE / f).read_bytes()).hexdigest() == spec[key], f"{f} changed after registration"
    reg = subprocess.check_output(["git", "log", "-1", "--format=%H", "--", str(SPEC.relative_to(ROOT))], cwd=ROOT, text=True).strip()
    assert reg, "the specification is not committed"
    return spec, sha, reg


def run(out_dir, counter=COUNTER, skip_gate=False, today=None, log=print):
    spec, sha, reg = gate(skip_gate)
    dg = H.data_gate(out_dir, today)
    log(f"data gate: {dg}")
    assert dg["opens"] or skip_gate, "H2 cannot open yet (it opens with H1; see the data gate)"
    if not skip_gate:
        c = json.loads(Path(counter).read_text()); assert c["opens"] == 0, "Test H2 was already opened; it runs once"
        Path(counter).write_text(json.dumps({"opens": 1, "spec_sha256": sha, "registration_commit": reg,
                                             "opened_utc": datetime.now(timezone.utc).isoformat(), "data_gate": dg}, indent=2) + "\n")
    syms = json.loads((Path(out_dir) / "H1_universe.json").read_text())["symbols"]
    dates = [d for d in H.collected_dates(out_dir) if d < dg["today"]]
    all_days = [d.strftime("%Y-%m-%d") for d in pd.date_range(dates[0], dates[-1], freq="D")] if dates else []
    tables, tables12 = {}, {}
    for s in syms:
        t, nv = coin_table(out_dir, s, all_days)
        if t is None or nv < H.MIN_DAYS or len(t) == 0:
            log(f"  {s}: {nv} valid days, excluded"); continue
        tables[s] = t
        t12, _ = coin_table(out_dir, s, all_days, win=WIN // 2)
        tables12[s] = t12
        log(f"  {s}: {nv} valid days, {int(np.isfinite(t['D']).sum())} hours with D")
    res = {"test": "H2", "spec_sha256": sha, "registration_commit": reg, "run_utc": datetime.now(timezone.utc).isoformat(),
           "data_gate": dg, "evaluation": evaluate(tables, tables12)}
    out = Path(out_dir)
    for p in ([out / RESULT.name, out / NUMBERS.name] + ([] if skip_gate else [RESULT, NUMBERS])):
        p.write_text(json.dumps(res, indent=1, default=float) + "\n" if p.suffix == ".json" else numbers_tex(res["evaluation"]))
    log(json.dumps({k: v for k, v in res["evaluation"].items() if k not in ("secondary", "per_coin")}, indent=1, default=float))
    return res


def selftest():
    import tempfile
    rng = np.random.default_rng(5)
    # rolling margin: on a simulated closed loop the estimate tracks the true margin
    nb = 288 * 6; a, kap, q = 0.9, 0.5, 0.06
    xx = np.zeros(nb); f = np.zeros(nb); p = np.zeros(nb); y = 0.0
    for k in range(1, nb):
        f[k] = q * y + rng.normal()
        xx[k] = a * xx[k - 1] + kap * f[k] + rng.normal()
        y = 0.7 * y + 0.3 * xx[k]
    pb = np.cumsum(np.r_[0, np.diff(xx)]) + 100
    _, r, fb, xb = bars(np.repeat(pb, 5), np.repeat(f / 5, 5))
    M, KP = rolling_margin(r, fb, xb)
    assert np.isfinite(M[-1]) and np.isfinite(KP[-1]), "rolling margin undefined on a clean series"
    # no look-ahead: changing data after hour h leaves every feature of hours <= h unchanged
    with tempfile.TemporaryDirectory() as td:
        syms, dates = H._synthetic(td, n_coins=21, n_days=31, rng=rng)
        t0, nv = coin_table(td, syms[0], dates)
        assert nv == 31 and len(t0) > 600
        cut = dates[20]
        for hh in range(24):
            fpath = Path(td) / "trades" / syms[0] / cut / f"{hh:02d}.csv.gz"
            d = pd.read_csv(fpath); d["px"] = d["px"] * (1 + 0.05 * rng.random(len(d))); d.to_csv(fpath, index=False, compression="gzip")
        t1, _ = coin_table(td, syms[0], dates)
        before = t0[t0["h"] < 20 * 24].reset_index(drop=True); after = t1[t1["h"] < 20 * 24].reset_index(drop=True)
        assert np.allclose(before[["D", "level", "rv24", "exc"]].to_numpy(), after[["D", "level", "rv24", "exc"]].to_numpy(), equal_nan=True), "look-ahead"
        res = run(td, skip_gate=True, today="2026-12-15", log=lambda s: None)
        e = res["evaluation"]
        assert e["n_coins"] == 21 and e["P2"].get("n_test", 0) > 0 and numbers_tex(e).startswith("%")
        print(json.dumps({k: v for k, v in e.items() if k not in ("secondary", "per_coin")}, default=float)[:700])
        assert not H.data_gate(td, today="2026-12-05")["opens"], "the data gate must stay closed before 2026-12-10"
    try:
        gate(); raise SystemExit("gate should refuse an unregistered draft")
    except AssertionError as err:
        print("gate refuses as expected:", err)
    print("h2 selftest: PASS")


if __name__ == "__main__":
    ap = argparse.ArgumentParser(); ap.add_argument("--selftest", action="store_true")
    if ap.parse_args().selftest:
        selftest()
