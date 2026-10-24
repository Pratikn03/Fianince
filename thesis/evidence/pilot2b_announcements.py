"""EXPLORATORY Pilot 2b: scheduled announcements as natural reset experiments, at one-second resolution
(not a registered test; nothing here is confirmatory evidence).

Why. Pilot 2 used every one-minute BTC move as a shock. The altcoins absorbed 90% of a move within the minute, and
both placebos failed: the altcoins slightly lead BTC, so an ordinary BTC move is not an outside shock to them.
Scheduled US macro releases fix the timing in advance: the content is unknown until the release second, so no
altcoin can trade on it before. Each release is one natural experiment (Chapter 4, Proposition natural); the catch-up
path of each altcoin after BTC's release-second jump is the displacement response, measured second by second.

Events (56): every CPI and Employment Situation release (8:30 ET) and every FOMC statement (2:00 ET) from January
2025 to October 2026, from the BLS 2025 and 2026 release calendars (including the revised dates of the 2025 lapse in
appropriations) and the Federal Reserve's FOMC calendar. The August 22, 2025 notation vote has no statement time and is
excluded.

Data. BTCUSDT spot one-second klines (the shock) and each altcoin's USD-M perpetual aggTrades (one-second last price),
from data.binance.vision, checksum verified, for the release dates only; a window of +-30 minutes around each release
is kept (cached on Drive).

Per symbol (event study; bootstrap over events):
    shock        e_k = p^B(tau_k + 10 s) - p^B(tau_k - 1 s)
    response     p^A(tau_k + j) - p^A(tau_k - 1) = c_j + b_j e_k + d_j [p^B(tau_k + j) - p^B(tau_k + 10)] + error,
                 j = 0..900 s (later BTC moves are controlled, as in Pilot 2)
    beta = mean b_j over j in [600, 900];  p_0 = b_10 / beta (share through by the end of the shock window)
    G_j = 1 - b_j / beta;  A_H = sum_{j=10}^{10+H-1} G_j  (seconds; horizon-limited amplification, Proposition horizon)
    finite-horizon margin M_H = (G_10 - G_{10+H}) / A_H (Proposition natural (iv)); M_120 is the margin used below. It
    exceeds the true margin by a memory term that vanishes as H grows; the long-run version (1 - p_0) / A over
    10..599 s is reported as a diagnostic only, because 56 releases cannot pin down a 10-minute tail
  Decisions (pilot readings): horizon-limited amplification certified when the upper 95% bound of A_120 is below 60 s;
  memories identified when two exponential modes fitted to G (10..309 s) have a rate-difference interval excluding
  zero and neither rate interval touching the bounds.
  Placebos: (i) pre-release drift: p^A(tau-1) - p^A(tau-301) on e_k (content unknown before release: must be ~0);
  (ii) pseudo-events 20 minutes before each release: the same design at a time with no news (the BTC 'shock' should be
  much smaller and the pre-drift also ~0).
  Invariance: across symbols, Spearman of M (announcements) against Pilot 1's own-flow margin.

Usage (Colab):  pilot2b_announcements.run(cache_dir, pilot1_json, out_json, part_dir)
Local test:     python pilot2b_announcements.py --selftest
"""
import argparse
import hashlib
import json
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import datetime, timezone
from pathlib import Path
from zoneinfo import ZoneInfo

import numpy as np
import pandas as pd
from scipy import optimize, stats

SYMBOLS = ("ACHUSDT ALICEUSDT API3USDT ARPAUSDT CELRUSDT CHRUSDT CVXUSDT GTCUSDT HOTUSDT ICXUSDT "
           "IOSTUSDT IOTXUSDT LITUSDT OGNUSDT QNTUSDT RLCUSDT SPELLUSDT TUSDT WOOUSDT ZENUSDT "
           "DASHUSDT IMXUSDT IOTAUSDT NEOUSDT ONEUSDT ROSEUSDT STGUSDT VETUSDT XMRUSDT ZRXUSDT").split()

CPI = ["2025-01-15", "2025-02-12", "2025-03-12", "2025-04-10", "2025-05-13", "2025-06-11", "2025-07-15", "2025-08-12",
       "2025-09-11", "2025-10-24", "2025-12-18", "2026-01-13", "2026-02-13", "2026-03-11", "2026-04-10", "2026-05-12",
       "2026-06-10", "2026-07-14", "2026-08-12", "2026-09-11", "2026-10-14"]
NFP = ["2025-01-10", "2025-02-07", "2025-03-07", "2025-04-04", "2025-05-02", "2025-06-06", "2025-07-03", "2025-08-01",
       "2025-09-05", "2025-11-20", "2025-12-16", "2026-01-09", "2026-02-11", "2026-03-06", "2026-04-03", "2026-05-08",
       "2026-06-05", "2026-07-02", "2026-08-07", "2026-09-04", "2026-10-02"]
FOMC = ["2025-01-29", "2025-03-19", "2025-05-07", "2025-06-18", "2025-07-30", "2025-09-17", "2025-10-29", "2025-12-10",
        "2026-01-28", "2026-03-18", "2026-04-29", "2026-06-17", "2026-07-29", "2026-09-16"]
SOURCES = {"CPI and Employment Situation": "https://www.bls.gov/schedule/2025 and https://www.bls.gov/schedule/2026/home.htm "
           "(revised dates: https://www.bls.gov/bls/2025-lapse-revised-release-dates.htm)",
           "FOMC": "https://www.federalreserve.gov/monetarypolicy/fomccalendars.htm (statement at 2:00 p.m. ET)"}

WIN = 1800                   # seconds kept on each side of a release
SHOCK = 10                   # shock window (s)
J = 900                      # horizons (s)
PLATEAU = (600, 900)
AREA_H = (30, 60, 120, 300)
A_INF = 590                  # A over 10..599 s
ID_SPAN = 300
CERT_H, CERT_BOUND = 120, 60.0
PSEUDO = 1200
B = 1000
SEED = 20261026
ROOT_SPOT = "https://data.binance.vision/data/spot/daily/klines"
ROOT_UM = "https://data.binance.vision/data/futures/um/daily"
DL_LOG = []


def events():
    ny = ZoneInfo("America/New_York"); out = []
    for kind, dates, hm in (("CPI", CPI, "08:30"), ("NFP", NFP, "08:30"), ("FOMC", FOMC, "14:00")):
        for d in dates:
            t = datetime.fromisoformat(f"{d} {hm}").replace(tzinfo=ny).astimezone(timezone.utc)
            out.append({"kind": kind, "date_et": d, "utc": t.isoformat(), "ts": int(t.timestamp()), "date_utc": t.strftime("%Y-%m-%d")})
    return sorted(out, key=lambda e: e["ts"])


# ---------------------------------------------------------------------------------------------------
# download (same checks as binance_vision.fetch: Binance .CHECKSUM, SHA-256 logged)
def fetch_url(url):
    import binance_vision as bv
    code, raw = bv._http(url, timeout=300)
    if code != 200:
        return None
    sha = hashlib.sha256(raw).hexdigest()
    c2, chk = bv._http(url + ".CHECKSUM", timeout=60)
    verified = None
    if c2 == 200 and chk:
        if chk.decode().split()[0] != sha:
            raise RuntimeError(f"SHA-256 mismatch {url}")
        verified = True
    DL_LOG.append({"url": url, "sha256": sha, "checksum_verified": verified})
    return raw


def _secs(col):
    import binance_vision as bv
    return bv.to_utc_seconds(col)


def btc_windows(date, evs, cache):
    """One-second BTCUSDT spot closes in +-WIN around each release on this UTC date: {ts: array(2*WIN+1)}."""
    import binance_vision as bv
    out, todo = {}, []
    for e in evs:
        f = Path(cache) / "BTCUSDT" / f"{e['ts']}.npy"
        if f.exists():
            out[e["ts"]] = np.load(f)
        else:
            todo.append(e)
    if not todo:
        return out
    raw = fetch_url(f"{ROOT_SPOT}/BTCUSDT/1s/BTCUSDT-1s-{date}.zip")
    if raw is None:
        return out
    k = bv.read_zip_csv(raw, bv.KL_COLS)
    s = pd.Series(k["close"].astype(float).to_numpy(), index=_secs(k["open_time"]))
    s = s[~s.index.duplicated()]
    for e in todo:
        idx = np.arange(e["ts"] - WIN, e["ts"] + WIN + 1)
        w = s.reindex(idx).ffill().bfill().to_numpy()
        if np.isfinite(w).all():
            f = Path(cache) / "BTCUSDT" / f"{e['ts']}.npy"; f.parent.mkdir(parents=True, exist_ok=True); np.save(f, w)
            out[e["ts"]] = w
    return out


def alt_windows(sym, date, evs, cache):
    """One-second last trade price and trade count of a perpetual in +-WIN around each release on this UTC date."""
    import binance_vision as bv
    out, todo = {}, []
    for e in evs:
        f = Path(cache) / sym / f"{e['ts']}.npz"
        if f.exists():
            z = np.load(f); out[e["ts"]] = (z["p"], z["n"])
        else:
            todo.append(e)
    if not todo:
        return out
    raw = fetch_url(f"{ROOT_UM}/aggTrades/{sym}/{sym}-aggTrades-{date}.zip")
    if raw is None:
        return out
    a = bv.read_zip_csv(raw, ["agg_trade_id", "price", "quantity", "first_trade_id", "last_trade_id", "transact_time",
                              "is_buyer_maker"])
    sec = _secs(a["transact_time"]); px = a["price"].astype(float).to_numpy()
    df = pd.DataFrame({"sec": sec, "px": px})
    last = df.groupby("sec")["px"].last(); cnt = df.groupby("sec")["px"].size()
    for e in todo:
        idx = np.arange(e["ts"] - WIN, e["ts"] + WIN + 1)
        n = cnt.reindex(idx).fillna(0).to_numpy()
        p = last.reindex(idx).ffill()
        prior = last[last.index < e["ts"] - WIN]
        if p.isna().any() and len(prior):
            p = p.fillna(prior.iloc[-1])
        p = p.to_numpy()
        if np.isfinite(p).all() and n[WIN - 60:WIN + 600].sum() > 0:
            f = Path(cache) / sym / f"{e['ts']}.npz"; f.parent.mkdir(parents=True, exist_ok=True)
            np.savez_compressed(f, p=p, n=n)
            out[e["ts"]] = (p, n)
    return out


def download(cache, symbols=SYMBOLS, threads=8):
    evs = events(); by_date = {}
    for e in evs:
        by_date.setdefault(e["date_utc"], []).append(e)
    btc = {}
    for d, es in sorted(by_date.items()):
        btc.update(btc_windows(d, es, cache))
    print(f"BTC windows: {len(btc)}/{len(evs)} releases", flush=True)
    alts = {s: {} for s in symbols}
    jobs = [(s, d, es) for s in symbols for d, es in by_date.items()]
    with ThreadPoolExecutor(max_workers=threads) as ex:
        futs = {ex.submit(alt_windows, s, d, es, cache): (s, d) for s, d, es in jobs}
        for i, f in enumerate(as_completed(futs)):
            s, _ = futs[f]
            try:
                alts[s].update(f.result())
            except Exception as err:
                print("  download error", futs[f], repr(err)[:120], flush=True)
            if (i + 1) % 200 == 0:
                print(f"  {i + 1}/{len(jobs)} symbol-dates", flush=True)
    return evs, btc, alts


# ---------------------------------------------------------------------------------------------------
# event-study estimation
def design(evs, btc, alt, at=0):
    """Arrays over usable events. at = 0 for releases, -PSEUDO for pseudo-events 20 minutes earlier."""
    E, Y, F, PRE, kinds = [], [], [], [], []
    c = WIN + at
    for e in evs:
        if e["ts"] not in btc or e["ts"] not in alt:
            continue
        pb = np.log(btc[e["ts"]]) * 1e4; pa = np.log(alt[e["ts"]][0]) * 1e4
        if c + J >= len(pb) or c - 301 < 0:
            continue
        E.append(pb[c + SHOCK] - pb[c - 1])
        Y.append(pa[c:c + J + 1] - pa[c - 1])
        f = pb[c:c + J + 1] - pb[c + SHOCK]; f[:SHOCK + 1] = 0.0; F.append(f)
        PRE.append(pa[c - 1] - pa[c - 301]); kinds.append(e["kind"])
    return np.array(E), np.array(Y), np.array(F), np.array(PRE), kinds


def lp(E, Y, F, w=None):
    """Per-horizon weighted OLS of Y[:, j] on (1, E, F[:, j]), vectorized over horizons; returns b_j."""
    n = len(E); w = np.ones(n) if w is None else w
    s0 = w.sum(); sE = w @ E; sEE = w @ (E * E)
    sF = w @ F; sEF = (w * E) @ F; sFF = w @ (F * F)
    sY = w @ Y; sEY = (w * E) @ Y; sFY = w @ (F * Y)
    nJ = Y.shape[1]
    A = np.empty((nJ, 3, 3)); c = np.empty((nJ, 3))
    A[:, 0, 0] = s0; A[:, 0, 1] = A[:, 1, 0] = sE; A[:, 1, 1] = sEE
    A[:, 0, 2] = A[:, 2, 0] = sF; A[:, 1, 2] = A[:, 2, 1] = sEF; A[:, 2, 2] = sFF
    c[:, 0] = sY; c[:, 1] = sEY; c[:, 2] = sFY
    flat = np.all(F == 0, axis=0)                     # horizons inside the shock window: no later-move control
    A[flat, 2, :] = 0.0; A[flat, :, 2] = 0.0; A[flat, 2, 2] = 1.0; c[flat, 2] = 0.0
    return np.linalg.solve(A, c[..., None])[..., 0][:, 1]


def curve_stats(b):
    beta = b[PLATEAU[0]:PLATEAU[1] + 1].mean()
    G = 1 - b / beta
    p0 = b[SHOCK] / beta
    A = {H: float(G[SHOCK:SHOCK + H].sum()) for H in AREA_H}
    Ainf = float(G[SHOCK:SHOCK + A_INF].sum())
    M = (1 - p0) / Ainf if Ainf > 0 else np.nan
    return beta, G, p0, A, Ainf, M


def finite_margin(G, H):
    """M_H = (x_0 - x_H) / sum_{t<H} x_t from the start of the catch-up (Chapter 4, Proposition natural (iv))."""
    a = G[SHOCK:SHOCK + H].sum()
    return float((G[SHOCK] - G[SHOCK + H]) / a) if a > 0 else np.nan


def exp_fit(g, hi=0.9999):
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
    for r1, r2 in [(0.8, 0.99), (0.5, 0.95), (0.9, 0.998), (0.3, 0.9)]:
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


def ci(v, q=(0.025, 0.975)):
    v = np.asarray(v, float); v = v[np.isfinite(v)]
    return [float(np.quantile(v, q[0])), float(np.quantile(v, q[1]))] if len(v) > 20 else [np.nan, np.nan]


def symbol_pilot(evs, btc, alt, j, nb=B):
    rng = np.random.default_rng(SEED + 101 * j)
    E, Y, F, PRE, kinds = design(evs, btc, alt)
    n = len(E)
    if n < 20:
        return {"n_events": n, "excluded": "fewer than 20 usable releases"}
    b = lp(E, Y, F); beta, G, p0, A, Ainf, M = curve_stats(b)
    draws = []
    for _ in range(nb):
        w = np.bincount(rng.integers(0, n, n), minlength=n).astype(float)
        bb = lp(E, Y, F, w); be, Gb, pb0, Ab, Ainfb, Mb = curve_stats(bb)
        pre = np.polyfit(E, PRE, 1, w=np.sqrt(w))[0] if w.sum() > 2 else np.nan
        draws.append({"beta": be, "p0": pb0, "Ainf": Ainfb, "M": Mb, "pre": pre, **{f"A{H}": Ab[H] for H in AREA_H},
                      "M120": finite_margin(Gb, 120), "M300": finite_margin(Gb, 300),
                      "G": Gb[SHOCK:SHOCK + ID_SPAN]})
    Dd = pd.DataFrame([{k: v for k, v in d.items() if k != "G"} for d in draws])
    rr = np.array([exp_fit(d["G"]) for d in draws[:300]]); rp = exp_fit(G[SHOCK:SHOCK + ID_SPAN])
    rf, rs, dr = ci(rr[:, 0]), ci(rr[:, 1]), ci(rr[:, 1] - rr[:, 0])
    inside = all(np.isfinite(v) and 1e-3 < v < 0.9995 for v in rf + rs)
    pre_point = float(np.polyfit(E, PRE, 1)[0])
    # pseudo-events 20 minutes before each release
    Ep, Yp, Fp, PREp, _ = design(evs, btc, alt, at=-PSEUDO)
    pseudo = {"n": len(Ep), "shock_sd_ratio": float(np.std(Ep) / np.std(E)) if len(Ep) > 5 else np.nan,
              "pre_over_beta": float(np.polyfit(Ep, PREp, 1)[0] / beta) if len(Ep) > 5 else np.nan}
    # certification precision against the number of events
    widths = []
    ns = [m for m in (14, 28) if m < n] + [n]
    for m in ns:
        idx = rng.permutation(n)[:m]; ws = []
        for _ in range(300):
            w = np.zeros(n); w[idx] = np.bincount(rng.integers(0, m, m), minlength=m)
            ws.append(curve_stats(lp(E, Y, F, w))[3][CERT_H])
        c = ci(ws); widths.append(c[1] - c[0])
    ok = np.isfinite(widths) & (np.array(widths) > 0)
    slope = float(np.polyfit(np.log(np.array(ns)[ok]), np.log(np.array(widths)[ok]), 1)[0]) if ok.sum() >= 3 else np.nan
    a_ci = {H: ci(Dd[f"A{H}"]) for H in AREA_H}
    return {"n_events": n, "kinds": {k: kinds.count(k) for k in set(kinds)},
            "median_abs_shock_bp": float(np.median(np.abs(E))),
            "beta": float(beta), "beta_ci": ci(Dd["beta"]), "p0": float(p0), "p0_ci": ci(Dd["p0"]),
            "A": {str(H): {"point": A[H], "ci": a_ci[H], "upper95": float(np.quantile(Dd[f"A{H}"].dropna(), 0.95))}
                  for H in AREA_H},
            "certified": bool(np.quantile(Dd[f"A{CERT_H}"].dropna(), 0.95) < CERT_BOUND),
            "A_inf": Ainf, "A_inf_ci": ci(Dd["Ainf"]), "M_long_per_s": float(M), "M_long_ci": ci(Dd["M"]),
            "M_per_s": finite_margin(G, 120), "M_ci": ci(Dd["M120"]),
            "M300_per_s": finite_margin(G, 300), "M300_ci": ci(Dd["M300"]),
            "G": [float(x) for x in G[:SHOCK + 300]],
            "identification": {"rho_fast": float(rp[0]), "rho_slow": float(rp[1]), "rho_fast_ci": rf, "rho_slow_ci": rs,
                               "delta_ci": dr, "inside_bounds": inside,
                               "identified": bool(np.isfinite(dr[0]) and dr[0] > 0 and inside)},
            "placebo_pre": {"coef": pre_point, "over_beta": pre_point / beta, "ci": ci(Dd["pre"]),
                            "covers_zero": bool(ci(Dd["pre"])[0] <= 0 <= ci(Dd["pre"])[1])},
            "pseudo": pseudo, "width_ns": ns, "widths": [float(x) for x in widths], "width_slope": slope}


def summarize(per, pilot1):
    ev = {s: v for s, v in per.items() if "beta" in v}
    out = {"n_symbols": len(ev), "events_median": float(np.median([v["n_events"] for v in ev.values()])) if ev else 0}
    if not ev:
        return out
    out.update({
        "median_beta": float(np.median([v["beta"] for v in ev.values()])),
        "median_p0": float(np.median([v["p0"] for v in ev.values()])),
        "median_A120_s": float(np.median([v["A"]["120"]["point"] for v in ev.values()])),
        "certified_A120_below_60s": int(sum(v["certified"] for v in ev.values())),
        "identified": int(sum(v["identification"]["identified"] for v in ev.values())),
        "placebo_pre_covers_zero": int(sum(v["placebo_pre"]["covers_zero"] for v in ev.values())),
        "median_abs_pre_over_beta": float(np.median([abs(v["placebo_pre"]["over_beta"]) for v in ev.values()])),
        "median_pseudo_shock_sd_ratio": float(np.nanmedian([v["pseudo"]["shock_sd_ratio"] for v in ev.values()])),
        "median_width_slope": float(np.nanmedian([v["width_slope"] for v in ev.values()])),
        "overshoot_A120_negative": int(sum(v["A"]["120"]["point"] < 0 for v in ev.values()))})
    if pilot1:
        a, b = [], []
        for s, v in ev.items():
            m1 = pilot1.get("per_symbol", {}).get(s, {}).get("full", {}).get("M_x_12", {}).get("point")
            if m1 is not None and np.isfinite(v["M_per_s"]) and v["M_per_s"] > 0:
                a.append(v["M_per_s"]); b.append(m1)
        if len(a) >= 10:
            rho, p = stats.spearmanr(a, b)
            out["invariance"] = {"n": len(a), "spearman": float(rho), "p_one_sided": float(p / 2 if rho > 0 else 1 - p / 2)}
    return out


def run(cache_dir, pilot1_json, out_json, part_dir=None, symbols=SYMBOLS, threads=8, dl_log=None, nb=B):
    evs, btc, alts = download(cache_dir, symbols, threads)
    if dl_log:
        Path(dl_log).write_text(json.dumps(DL_LOG, indent=0) + "\n")
    per = {}
    for j, s in enumerate(symbols):
        part = Path(part_dir) / f"{s}.json" if part_dir else None
        if part is not None and part.exists():
            per[s] = json.loads(part.read_text()); continue
        r = symbol_pilot(evs, btc, alts[s], j, nb)
        r = json.loads(json.dumps(r, default=lambda o: None if o is None else float(o)))
        if part is not None:
            part.parent.mkdir(parents=True, exist_ok=True); part.write_text(json.dumps(r))
        per[s] = r
        if "beta" in r:
            print(f"  {s}: events={r['n_events']} beta={r['beta']:.2f} p0={r['p0']:.2f} A120={r['A']['120']['point']:.1f}s "
                  f"(upper {r['A']['120']['upper95']:.1f}) M={r['M_per_s']:.3f}/s identified={r['identification']['identified']} "
                  f"pre/beta={r['placebo_pre']['over_beta']:+.3f} (covers 0: {r['placebo_pre']['covers_zero']}) "
                  f"pseudo shock ratio={r['pseudo']['shock_sd_ratio']:.2f}", flush=True)
        else:
            print(f"  {s}: {r}", flush=True)
    pilot1 = json.loads(Path(pilot1_json).read_text()) if pilot1_json and Path(pilot1_json).exists() else None
    res = {"kind": "EXPLORATORY Pilot 2b (scheduled announcements, one-second); not a registered test",
           "run_utc": datetime.now(timezone.utc).isoformat(), "events": evs, "sources": SOURCES,
           "per_symbol": per, "summary": summarize(per, pilot1)}
    Path(out_json).write_text(json.dumps(res, indent=1, default=lambda o: None if o is None else float(o)) + "\n")
    print(json.dumps(res["summary"], indent=1))
    return res


# ---------------------------------------------------------------------------------------------------
def selftest():
    """Synthetic releases: BTC jumps at the release second; the altcoin's fair value moves beta times the jump at once,
    its price passes 60% through within the shock window and closes the rest with persistence 0.97 per second."""
    rng = np.random.default_rng(5)
    evs = events(); btc, alt = {}, {}
    beta, rho, share = 1.2, 0.97, 0.6
    for e in evs:
        T = 2 * WIN + 1
        rb = rng.normal(0, 0.8, T); rb[WIN] += rng.choice([-1, 1]) * rng.uniform(20, 80)
        pb = np.cumsum(rb)
        fair = beta * pb + np.cumsum(rng.normal(0, 0.6, T))
        gap = np.zeros(T)
        for t in range(1, T):
            gap[t] = rho * gap[t - 1] + (1 - share) * beta * rb[t]
        pa = fair - gap + rng.normal(0, 0.3, T)
        btc[e["ts"]] = 60000 * np.exp(pb / 1e4); alt[e["ts"]] = (np.exp(pa / 1e4), np.ones(T))
    r = symbol_pilot(evs, btc, alt, 0, nb=200)
    # truth: G_j = 0.4 rho^j from the shock second; with the 10-s window, p0 = 1 - 0.4 rho^10; A over 10..599 s = 0.4 rho^10 / (1 - rho)
    p0_true = 1 - (1 - share) * rho ** SHOCK; ainf_true = (1 - share) * rho ** SHOCK / (1 - rho); m_true = 1 - rho
    print(json.dumps({"beta": r["beta"], "p0": r["p0"], "p0_true": p0_true, "A_inf": r["A_inf"], "A_inf_true": ainf_true,
                      "M": r["M_per_s"], "M_true": m_true, "pre": r["placebo_pre"], "identified": r["identification"]["identified"],
                      "width_slope": r["width_slope"]}, indent=1))
    assert abs(r["beta"] - beta) < 0.05 and abs(r["p0"] - p0_true) < 0.05
    a120_true = (1 - share) * rho ** SHOCK * (1 - rho ** 120) / (1 - rho)
    print("A120", r["A"]["120"], "true", a120_true)
    assert abs(r["A"]["120"]["point"] - a120_true) / a120_true < 0.15 and abs(r["M_per_s"] - m_true) < 0.01
    assert r["placebo_pre"]["covers_zero"]
    print("selftest: PASS")


if __name__ == "__main__":
    ap = argparse.ArgumentParser(); ap.add_argument("--selftest", action="store_true")
    if ap.parse_args().selftest:
        selftest()
