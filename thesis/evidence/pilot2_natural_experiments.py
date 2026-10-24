"""EXPLORATORY Pilot 2: natural reset experiments (not a registered test; nothing here is confirmatory evidence).

Idea. The theorems of Chapter 4 concern reset experiments: a known shock, then the market's response. Passive
order-flow data contain none. In a small Binance perpetual, a BTC move is a shock from outside: the altcoin's
traders did not cause it and cannot move BTC. Its fair value moves with BTC at once, but its price catches up
over minutes. The remaining gap is a price displacement in the sense of the theory, so its path after the shock is
the displacement response, and its area is the summed response.

Formula. With x_t = a x_{t-1} + kappa f_t and f_t = sum_m k_m x_{t-m} (Paper 2, Theorem sum), a unit displacement
decays along h_0 = 1, h_{t+1} = a h_t + kappa sum_{m<=t} k_m h_{t-m}, and sum_t h_t = 1 / (1 - a - kappa Phi).
Writing b_j for the cumulative altcoin response j minutes after a BTC shock and beta for its long-run plateau, the
displacement j minutes after a shock e is x_j = (beta - b_j) e, so x_j / x_0 = h_j / h_0 and

        sum_j x_j / x_0 = 1 / M,      M = 1 - a - kappa Phi        (Chapter 4, Proposition natural)

In the normalization used below, G_j = 1 - b_j / beta (the share of the long-run move still missing), the area
A = sum_j G_j is the horizon-limited amplification per unit of long-run move, and M = (1 - p_0) / A with
p_0 = b_0 / beta the share that passes through within the shock minute. A is what a position exposed to the lag
loses in the worst case over the horizon; M is the stability margin. Splitting G into exponential modes is the
identification problem the theory says is hard.

Estimation (per symbol, pooled over days with day-demeaning; local projections; day bootstrap with weights):
    p^A_{t+j} - p^A_{t-1} = b_j r^B_t + controls (5 lags of r^B and of r^A) + e,  j = 0..90 minutes
    beta = mean of b_j over j in [60, 90];  G_j = 1 - b_j / beta;  S = sum_{j=0}^{59} G_j (minutes);  M = 1 / S
The same at five-minute resolution (horizons 0..18 bars, plateau 12..18, S5 over 0..11) for comparison with Pilot 1.

Pilot questions:
  A. Does the gap close (tail of G near zero), so that S is finite?
  B. Certification: relative width of the S interval; scaling of its width with the number of days (theory: -1/2).
  C. Identification: two exponentials fitted to G (bounds [0, 0.999]); identified only if the rate-difference
     interval excludes zero and neither rate interval touches the bounds.
  D. Placebos: (i) reverse direction, r^B_t on lags of r^A (the altcoin must not lead BTC); (ii) a BTC shock must not
     explain the altcoin's move over the five minutes before it.
  E. Invariance: across symbols, the five-minute margin from BTC shocks against Pilot 1's margin from the altcoin's own
     order flow (same 5-minute units): one functional seen through two different experiments.

Data: the E1v2 and D1 caches (already-opened days) for the 30 altcoins; BTCUSDT one-minute klines for the same dates
(downloaded once from data.binance.vision, checksum verified, cached on Drive).

Usage (Colab):  pilot2_natural_experiments.run(alt_caches, btc_cache, pilot1_json, out_json, part_dir)
Local test:     python pilot2_natural_experiments.py --selftest
"""
import argparse
import json
import os
from concurrent.futures import ProcessPoolExecutor, ThreadPoolExecutor
from datetime import datetime, timezone
from pathlib import Path

import numpy as np
import pandas as pd
from scipy import optimize, stats

SYMBOLS = ("ACHUSDT ALICEUSDT API3USDT ARPAUSDT CELRUSDT CHRUSDT CVXUSDT GTCUSDT HOTUSDT ICXUSDT "
           "IOSTUSDT IOTXUSDT LITUSDT OGNUSDT QNTUSDT RLCUSDT SPELLUSDT TUSDT WOOUSDT ZENUSDT "
           "DASHUSDT IMXUSDT IOTAUSDT NEOUSDT ONEUSDT ROSEUSDT STGUSDT VETUSDT XMRUSDT ZRXUSDT").split()
NL = 5                      # control lags (1-minute)
J1, PL1, SH1 = 90, (60, 90), 60        # 1-minute horizons, plateau window, area horizon
NL5, J5, PL5, SH5 = 3, 18, (12, 18), 12  # 5-minute versions
B = 200
SEED = 20261025
CURVE_N = (10, 20, 40, 80)
RHO_HI, BLO, BHI = 0.999, 0.005, 0.995
CERT_REL = 0.25             # pilot reading: S certified to +-12.5%


# ---------------------------------------------------------------------------------------------------
# per-day sufficient statistics
def _lagmat(z, lags):
    n = len(z)
    return np.column_stack([np.r_[np.full(k, np.nan), z[:n - k]] for k in lags])


def _fwd(p, J):
    """Y[t, j] = p[t+j] - p[t-1], j = 0..J (NaN past the end)."""
    n = len(p); Y = np.full((n, J + 1), np.nan)
    base = np.r_[np.nan, p[:-1]]
    for j in range(J + 1):
        Y[:n - j, j] = p[j:] - base[:n - j]
    return Y


def _ss(X, Y):
    ok = np.all(np.isfinite(X), 1) & np.all(np.isfinite(Y), 1)
    if ok.sum() < 200:
        return None
    Xo, Yo = X[ok] - X[ok].mean(0), Y[ok] - Y[ok].mean(0)
    return Xo.T @ Xo, Xo.T @ Yo, int(ok.sum())


def _lp(X, pA, pB, J):
    """Local projections with later BTC moves as controls (they are independent of the shock at t and remove most
    of the noise): for horizon j, regress p^A_{t+j} - p^A_{t-1} on [X_t, p^B_{t+j} - p^B_t, p^B_{t+j} - p^B_{t+j-5}].
    Returns per-horizon day-demeaned systems A (J+1, k, k) and c (J+1, k)."""
    n = len(pA); Y = _fwd(pA, J)
    k = X.shape[1] + 2; A = np.zeros((J + 1, k, k)); c = np.zeros((J + 1, k)); rows = []
    for j in range(J + 1):
        f1 = np.full(n, np.nan); f2 = np.full(n, np.nan)
        f1[:n - j] = pB[j:] - pB[:n - j]
        lagj = max(j - 5, 0)
        f2[:n - j] = pB[j:] - pB[lagj:n - j + lagj]
        Z = np.column_stack([X, f1, f2]); y = Y[:, j]
        ok = np.all(np.isfinite(Z), 1) & np.isfinite(y)
        if ok.sum() < 200:
            return None
        Zo = Z[ok] - Z[ok].mean(0); yo = y[ok] - y[ok].mean()
        if j <= 5:
            Zo[:, -1] = 0.0                                   # f2 equals f1 for the first five horizons
        A[j] = Zo.T @ Zo + np.diag(np.r_[np.zeros(k - 1), 1e-9 if j <= 5 else 0.0]); c[j] = Zo.T @ yo
        rows.append(int(ok.sum()))
    return A, c, min(rows)


def day_stats(pA, pB):
    """pA, pB: log prices (bp) per minute, length 1440."""
    out = {}
    rA, rB = np.diff(pA, prepend=np.nan), np.diff(pB, prepend=np.nan)
    lagsB, lagsA = _lagmat(rB, range(1, NL + 1)), _lagmat(rA, range(1, NL + 1))
    X = np.column_stack([rB, lagsB, lagsA])
    out["lp1"] = _lp(X, pA, pB, J1)
    # placebo (ii): the altcoin's move over the 5 minutes before t, on the shock at t (BTC lags as controls only)
    pre = np.r_[np.nan, pA[:-1]] - np.r_[np.full(6, np.nan), pA[:-6]]
    out["pre"] = _ss(np.column_stack([rB, lagsB]), pre[:, None])
    # placebo (i): reverse direction, r^B_t on lags of r^B and r^A
    out["rev"] = _ss(np.column_stack([lagsB, lagsA]), rB[:, None])
    # five-minute resolution
    m = np.arange(4, 1440, 5); qA, qB = pA[m], pB[m]
    sA, sB = np.diff(qA, prepend=np.nan), np.diff(qB, prepend=np.nan)
    X5 = np.column_stack([sB, _lagmat(sB, range(1, NL5 + 1)), _lagmat(sA, range(1, NL5 + 1))])
    out["lp5"] = _lp(X5, qA, qB, J5)
    return out


# ---------------------------------------------------------------------------------------------------
def stack(days):
    out = {}
    for k in days[0]:
        first = next((d[k] for d in days if d[k] is not None), None)
        if first is None:
            continue
        A = np.zeros((len(days),) + first[0].shape); C = np.zeros((len(days),) + first[1].shape)
        for i, d in enumerate(days):
            if d[k] is not None:
                A[i], C[i] = d[k][0], d[k][1]
        out[k] = (A, C)
    return out


def coef_w(S, name, W):
    """Coefficients for each row of the day-weight matrix W.
    Plain systems (A[d,p,p], C[d,p,q]) give (draws, p, q); per-horizon systems (A[d,h,k,k], c[d,h,k]) give
    (draws, k, h), so that [:, 0, :] is the shock coefficient at every horizon in both cases."""
    A0, C0 = S[name]
    if A0.ndim == 4:
        A = np.einsum("bd,dhij->bhij", W, A0); c = np.einsum("bd,dhi->bhi", W, C0)
        try:
            x = np.linalg.solve(A, c[..., None])[..., 0]
        except np.linalg.LinAlgError:
            x = (np.linalg.pinv(A) @ c[..., None])[..., 0]
        return np.transpose(x, (0, 2, 1))
    A = np.einsum("bd,dij->bij", W, A0); C = np.einsum("bd,dij->bij", W, C0)
    try:
        return np.linalg.solve(A, C)
    except np.linalg.LinAlgError:
        return np.linalg.pinv(A) @ C


def gap_quantities(b, plateau, horizon):
    """b: (draws, J+1) cumulative responses. Returns beta, G, S, M, tail."""
    beta = b[:, plateau[0]:plateau[1] + 1].mean(1)
    G = 1 - b / beta[:, None]
    Sa = G[:, :horizon].sum(1)
    tail = G[:, int(0.75 * horizon):horizon].mean(1)
    with np.errstate(divide="ignore", invalid="ignore"):
        M = np.where(Sa > 0, (1 - b[:, 0] / beta) / Sa, np.nan)    # M = (1 - p_0) / A
    return beta, G, Sa, M, tail


def exp_fit(g, hi=RHO_HI):
    """Two exponentials fitted to the gap curve (rates in [0, hi])."""
    m = np.arange(len(g))

    def resid(th):
        w1, r1, w2, r2 = th
        return w1 * r1 ** m + w2 * r2 ** m - g

    def jac(th):
        w1, r1, w2, r2 = th
        d1 = np.where(m > 0, m * np.power(max(r1, 1e-300), np.maximum(m - 1, 0)), 0.0)
        d2 = np.where(m > 0, m * np.power(max(r2, 1e-300), np.maximum(m - 1, 0)), 0.0)
        return np.column_stack([r1 ** m, w1 * d1, r2 ** m, w2 * d2])
    if not np.all(np.isfinite(g)):
        return np.nan, np.nan
    best = None
    for r1, r2 in [(0.3, 0.9), (0.1, 0.7), (0.5, 0.97), (0.05, 0.5)]:
        try:
            sol = optimize.least_squares(resid, [g[0] / 2, r1, g[0] / 2, r2], jac=jac,
                                         bounds=([-np.inf, 0, -np.inf, 0], [np.inf, hi, np.inf, hi]))
            if best is None or sol.cost < best.cost:
                best = sol
        except Exception:
            pass
    if best is None:
        return np.nan, np.nan
    _, r1, _, r2 = best.x
    return (r1, r2) if r1 <= r2 else (r2, r1)


def ci(v):
    v = np.asarray(v, float); v = v[np.isfinite(v)]
    return [float(np.quantile(v, .025)), float(np.quantile(v, .975))] if len(v) > 20 else [np.nan, np.nan]


def boot_weights(n, rng, nb):
    return np.stack([np.bincount(rng.integers(0, n, n), minlength=n) for _ in range(nb)]).astype(float)


def weights(nd, idx, rng, nb):
    P = np.zeros((1, nd)); P[0, idx] = 1
    W = np.zeros((nb, nd)); W[:, idx] = boot_weights(len(idx), rng, nb)
    return P, W


def evaluate(S, idx, rng, nb, with_id=True):
    nd = len(S["lp1"][0]); P, W = weights(nd, idx, rng, nb)
    out = {}
    for tag, plateau, horizon in (("1m", PL1, SH1), ("5m", PL5, SH5)):
        name = "lp1" if tag == "1m" else "lp5"
        bp, bw = coef_w(S, name, P)[:, 0, :], coef_w(S, name, W)[:, 0, :]
        beta_p, G_p, S_p, M_p, tail_p = gap_quantities(bp, plateau, horizon)
        beta_w, G_w, S_w, M_w, tail_w = gap_quantities(bw, plateau, horizon)
        s_ci, m_ci = ci(S_w), ci(M_w)
        rel = (s_ci[1] - s_ci[0]) / S_p[0] if np.isfinite(S_p[0]) and S_p[0] > 0 else np.nan
        d = {"beta": float(beta_p[0]), "beta_ci": ci(beta_w), "S": float(S_p[0]), "S_ci": s_ci, "S_rel_width": float(rel),
             "M": float(M_p[0]), "M_ci": m_ci, "tail": float(tail_p[0]), "tail_ci": ci(tail_w),
             "pass_through_0": float(bp[0, 0] / beta_p[0]),
             "certified": bool(np.isfinite(rel) and rel <= CERT_REL and s_ci[0] > 0),
             "G": [float(x) for x in G_p[0, :horizon]],
             "variants": ({f"H{H}": (lambda q: {"S": float(q[0][0]), "S_ci": ci(q[1]),
                                                 "S_rel_width": float((ci(q[1])[1] - ci(q[1])[0]) / q[0][0]) if q[0][0] > 0 else None})(
                              (gap_quantities(bp, (H, min(int(1.5 * H), J1)), H)[2], gap_quantities(bw, (H, min(int(1.5 * H), J1)), H)[2]))
                           for H in (10, 15, 30)} if tag == "1m" else {}),
             "G_ci": [ci(G_w[:, j]) for j in range(horizon)]}
        if with_id and tag == "1m":
            rr = np.array([exp_fit(g) for g in G_w[:, :horizon]]); rp = exp_fit(G_p[0, :horizon])
            rf, rs, dr = ci(rr[:, 0]), ci(rr[:, 1]), ci(rr[:, 1] - rr[:, 0])
            inside = all(np.isfinite(v) and BLO < v < BHI for v in rf + rs)
            d["identification"] = {"rho_fast": float(rp[0]), "rho_slow": float(rp[1]), "rho_fast_ci": rf, "rho_slow_ci": rs,
                                   "delta_ci": dr, "delta_excludes_zero": bool(np.isfinite(dr[0]) and dr[0] > 0),
                                   "inside_bounds": inside,
                                   "identified": bool(np.isfinite(dr[0]) and dr[0] > 0 and inside)}
        out[tag] = d
    # placebos
    pre_p, pre_w = coef_w(S, "pre", P)[:, 0, 0], coef_w(S, "pre", W)[:, 0, 0]
    rev_p, rev_w = coef_w(S, "rev", P)[:, NL:, 0].sum(1), coef_w(S, "rev", W)[:, NL:, 0].sum(1)
    beta1 = out["1m"]["beta"]
    out["placebo"] = {"pre_coef": float(pre_p[0]), "pre_ci": ci(pre_w), "pre_over_beta": float(pre_p[0] / beta1),
                      "reverse_sum": float(rev_p[0]), "reverse_ci": ci(rev_w)}
    return out


def slope(ns, ws):
    ns, ws = np.asarray(ns, float), np.asarray(ws, float); ok = np.isfinite(ws) & (ws > 0)
    return float(np.polyfit(np.log(ns[ok]), np.log(ws[ok]), 1)[0]) if ok.sum() >= 3 else np.nan


def symbol_pilot(days, j):
    rng = np.random.default_rng(SEED + 101 * j); n = len(days); S = stack(days)
    res = {"n_days": n, "full": evaluate(S, np.arange(n), rng, B)}
    order = rng.permutation(n); curve = {}; ns, ws = [], []
    for m in [k for k in CURVE_N if k < n] + [n]:
        e = res["full"] if m == n else evaluate(S, order[:m], rng, 150, with_id=False)
        w = e["1m"]["S_ci"][1] - e["1m"]["S_ci"][0]
        curve[str(m)] = {"S": e["1m"]["S"], "S_width": float(w), "certified": e["1m"]["certified"],
                         "identified": e["1m"].get("identification", {}).get("identified")}
        ns.append(m); ws.append(w)
    res["curve"] = curve; res["width_slope"] = slope(ns, ws)
    return res


# ---------------------------------------------------------------------------------------------------
# data
def btc_close(date, btc_cache):
    """BTCUSDT 1-minute closes for one date (cached on disk); None if missing."""
    import binance_vision as bv
    f = Path(btc_cache) / "BTCUSDT" / f"{date}.npy"
    if f.exists():
        return np.load(f)
    raw = bv.fetch("klines", "BTCUSDT", date)
    if raw is None:
        return None
    k = bv.read_zip_csv(raw, bv.KL_COLS)
    t0 = int(pd.Timestamp(f"{date} 00:00:00", tz="UTC").timestamp())
    k = k.assign(m=(bv.to_utc_seconds(k["open_time"]) - t0) // 60).drop_duplicates("m").set_index("m").reindex(np.arange(1440))
    c = k["close"].astype(float).ffill().bfill().to_numpy()
    f.parent.mkdir(parents=True, exist_ok=True); np.save(f, c)
    return c


def alt_dates(alt_caches, sym):
    out = {}
    for cd in alt_caches:
        for f in sorted((Path(cd) / sym).glob("*_nodepth.pkl")):
            out[f.name.split("_")[0]] = f
    return out


def prefetch_btc(alt_caches, btc_cache, threads=8):
    dates = sorted({d for s in SYMBOLS for d in alt_dates(alt_caches, s)})
    with ThreadPoolExecutor(max_workers=threads) as ex:
        got = list(ex.map(lambda d: btc_close(d, btc_cache) is not None, dates))
    import binance_vision as bv
    print(f"BTCUSDT: {sum(got)}/{len(dates)} dates available", flush=True)
    return bv.DL_LOG


def load_symbol(alt_caches, btc_cache, sym):
    days = []
    for date, f in sorted(alt_dates(alt_caches, sym).items()):
        try:
            obj = pd.read_pickle(f)
        except Exception:
            continue
        df = obj[0] if isinstance(obj, tuple) else obj
        if df is None:
            continue
        cb = np.load(Path(btc_cache) / "BTCUSDT" / f"{date}.npy") if (Path(btc_cache) / "BTCUSDT" / f"{date}.npy").exists() else None
        if cb is None:
            continue
        ca = df["close"].to_numpy(float)
        if not (np.all(np.isfinite(ca)) and np.all(ca > 0) and np.all(cb > 0)):
            continue
        st = day_stats(np.log(ca) * 1e4, np.log(cb) * 1e4)
        if st["lp1"] is None or st["lp5"] is None:
            continue
        days.append(st)
    return days


def _one(args):
    alt_caches, btc_cache, s, j, part_dir = args
    part = Path(part_dir) / f"{s}.json" if part_dir else None
    if part is not None and part.exists():
        return s, json.loads(part.read_text())
    days = load_symbol(alt_caches, btc_cache, s)
    r = {"n_days": len(days), "excluded": "fewer than 30 valid days"} if len(days) < 30 else symbol_pilot(days, j)
    r = json.loads(json.dumps(r, default=lambda o: None if o is None else float(o)))
    if part is not None:
        part.write_text(json.dumps(r))
    return s, r


def summarize(per, pilot1):
    ev = {s: v for s, v in per.items() if "full" in v}
    n = len(ev); f1 = {s: v["full"]["1m"] for s, v in ev.items()}; f5 = {s: v["full"]["5m"] for s, v in ev.items()}
    out = {"n_symbols": n,
           "gap_closes_tail_ci_covers_0_or_small": int(sum(abs(v["tail"]) < 0.05 for v in f1.values())),
           "median_beta": float(np.median([v["beta"] for v in f1.values()])),
           "median_pass_through_0": float(np.median([v["pass_through_0"] for v in f1.values()])),
           "median_S_minutes": float(np.median([v["S"] for v in f1.values()])),
           "median_S_rel_width_1m": float(np.median([v["S_rel_width"] for v in f1.values()])),
           "certified_1m": int(sum(v["certified"] for v in f1.values())),
           "certified_5m": int(sum(v["certified"] for v in f5.values())),
           "M_positive_decided_1m": int(sum(v["M_ci"][0] > 0 for v in f1.values() if np.isfinite(v["M_ci"][0]))),
           "identified": int(sum(v["identification"]["identified"] for v in f1.values())),
           "delta_excludes_zero": int(sum(v["identification"]["delta_excludes_zero"] for v in f1.values())),
           "median_width_slope": float(np.nanmedian([v["width_slope"] for v in ev.values()])),
           "width_slope_in_[-0.75,-0.25]": int(sum(-0.75 <= v["width_slope"] <= -0.25 for v in ev.values() if v["width_slope"] is not None)),
           "placebo_pre_ci_covers_0": int(sum(v["full"]["placebo"]["pre_ci"][0] <= 0 <= v["full"]["placebo"]["pre_ci"][1] for v in ev.values())),
           "median_abs_pre_over_beta": float(np.median([abs(v["full"]["placebo"]["pre_over_beta"]) for v in ev.values()])),
           "placebo_reverse_ci_covers_0": int(sum(v["full"]["placebo"]["reverse_ci"][0] <= 0 <= v["full"]["placebo"]["reverse_ci"][1] for v in ev.values())),
           "e1v2_median_I_cert_for_comparison": 2.67}
    curve = {}
    for m in [str(k) for k in CURVE_N] + ["all"]:
        rows = [v["curve"].get(m) if m != "all" else v["curve"][max(v["curve"], key=int)] for v in ev.values()]
        rows = [r for r in rows if r]
        curve[m] = {"n": len(rows), "certified": int(sum(bool(r["certified"]) for r in rows)),
                    "identified": int(sum(bool(r["identified"]) for r in rows if r["identified"] is not None))}
    out["curve"] = curve
    if pilot1:
        a, b = [], []
        for s in ev:
            p1 = pilot1.get("per_symbol", {}).get(s, {}).get("full", {}).get("M_x_12", {}).get("point")
            if p1 is not None and np.isfinite(f5[s]["M"]):
                a.append(f5[s]["M"]); b.append(p1)
        if len(a) >= 10:
            rho, p = stats.spearmanr(a, b)
            out["invariance"] = {"n": len(a), "spearman": float(rho), "p_one_sided": float(p / 2 if rho > 0 else 1 - p / 2),
                                 "median_M5_natural": float(np.median(a)), "median_M5_own_flow": float(np.median(b))}
    return out


def run(alt_caches, btc_cache, pilot1_json, out_json, part_dir=None, symbols=SYMBOLS, workers=None, dl_log=None):
    alt_caches = [str(c) for c in alt_caches]
    log = prefetch_btc(alt_caches, btc_cache)
    if dl_log:
        Path(dl_log).write_text(json.dumps(log, indent=0) + "\n")
    if part_dir:
        Path(part_dir).mkdir(parents=True, exist_ok=True)
    jobs = [(alt_caches, str(btc_cache), s, j, str(part_dir) if part_dir else None) for j, s in enumerate(symbols)]
    per = {}
    with ProcessPoolExecutor(max_workers=workers or os.cpu_count()) as ex:
        for s, r in ex.map(_one, jobs):
            per[s] = r
            if "full" in r:
                f = r["full"]["1m"]
                print(f"  {s}: days={r['n_days']} beta={f['beta']:.2f} S={f['S']:.1f}min (+-{f['S_rel_width'] / 2:.0%}) "
                      f"M={f['M']:.3f} tail={f['tail']:.3f} certified={f['certified']} "
                      f"identified={f['identification']['identified']} slope={r['width_slope']:.2f}", flush=True)
            else:
                print(f"  {s}: {r['n_days']} days, excluded", flush=True)
    pilot1 = json.loads(Path(pilot1_json).read_text()) if pilot1_json and Path(pilot1_json).exists() else None
    per = {s: per[s] for s in symbols}
    res = {"kind": "EXPLORATORY Pilot 2 (natural reset experiments); not a registered test",
           "run_utc": datetime.now(timezone.utc).isoformat(), "per_symbol": per, "summary": summarize(per, pilot1)}
    Path(out_json).write_text(json.dumps(res, indent=1, default=lambda o: None if o is None else float(o)) + "\n")
    print(json.dumps(res["summary"], indent=1))
    return res


# ---------------------------------------------------------------------------------------------------
def _fake_pair(rng, beta=0.8, a=0.85, fb=0.05):
    """Synthetic BTC and altcoin minute prices: the altcoin's gap to beta*BTC decays at rate a + fb."""
    T = 1440
    rB = rng.standard_t(4, T) * 3.0
    pB = np.cumsum(rB)
    fair = beta * pB + np.cumsum(rng.normal(0, 1.0, T))
    gap = np.zeros(T); pA = np.zeros(T)
    for t in range(T):
        prev = gap[t - 1] if t else 0.0
        gap[t] = (a + fb) * prev + 0.6 * beta * rB[t]       # 40% passes through at once, the rest lags
        pA[t] = fair[t] - gap[t] + rng.normal(0, 0.5)
    return 100 * np.exp(pA / 1e4), 30000 * np.exp(pB / 1e4)


def selftest():
    import tempfile
    rng = np.random.default_rng(3)
    with tempfile.TemporaryDirectory() as td:
        dates = [f"{d:%Y-%m-%d}" for d in pd.date_range("2025-01-01", periods=60, freq="5D")]
        for s in SYMBOLS[:3]:
            os.makedirs(f"{td}/alt/{s}")
        for d in dates:
            ca, cb = _fake_pair(rng)
            os.makedirs(f"{td}/btc/BTCUSDT", exist_ok=True); np.save(f"{td}/btc/BTCUSDT/{d}.npy", cb)
            for s in SYMBOLS[:3]:
                pd.to_pickle((pd.DataFrame({"close": ca * (1 + 0.0 * rng.random()), "flow": np.zeros(1440)}), {}),
                             f"{td}/alt/{s}/{d}_nodepth.pkl")
        r = run([f"{td}/alt"], f"{td}/btc", None, f"{td}/p2.json", part_dir=f"{td}/parts", symbols=SYMBOLS[:3])
        s1 = r["per_symbol"][SYMBOLS[0]]["full"]["1m"]
        # truth: gap fraction after the shock decays at 0.9 per minute from G_0 = 0.6 -> S = 0.6 / (1 - 0.9) = 6 minutes
        assert abs(s1["S"] - 6.0) < 1.0, s1["S"]
        assert abs(s1["beta"] - 0.8) < 0.05, s1["beta"]
    print("selftest: PASS (recovers S = 6 minutes and beta = 0.8 on synthetic data)")


if __name__ == "__main__":
    ap = argparse.ArgumentParser(); ap.add_argument("--selftest", action="store_true")
    if ap.parse_args().selftest:
        selftest()
