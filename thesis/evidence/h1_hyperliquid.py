"""Test H1 (DRAFT until registered): do real agents have distinct memories that their own records reveal and prices do not?

Why. Every test so far used anonymous prices and order flow, or class-level positioning ratios published by one venue.
The identification theory is about agents. Hyperliquid, a perpetual-futures exchange whose order book runs on a public
blockchain, publishes every trade with the buyer's and the seller's wallet addresses (WebSocket channel `trades`,
field `users = [buyer, seller]`). That is participant-level data, public and free, the first direct test of the theory
against real agents rather than proxies.

Design: prospective. The specification, this code and the universe rule are registered before any trade is recorded.
COLLECTION (collect): from the first start, the 30 perpetuals ranked 11 to 40 by 24-hour notional volume in
`metaAndAssetCtxs` (ASCII alphanumeric names, not delisted) are written to H1_universe.json before any trade is saved;
every trade on them is then recorded (time, aggressor side, price, size, buyer, seller, trade id) to hourly gzip files,
with the seconds of live connection per minute. Restarts reuse the universe and merge files, deduplicating trades.
VALID DAY (UTC): connection live for at least 95% of the day, and C3's valid-day rule on one-minute last-trade prices
and signed taker notional (at least half of five-minute returns non-zero, flow not identically zero).
EVALUABLE COIN: at least 30 valid days. The analysis opens at the first run on or after 2026-12-10 at which at least 20
coins are evaluable, and on 2027-01-31 in any case (void if fewer than 20 evaluable coins then).

Estimates per coin, on its valid days:
* PRICE-ONLY: C3's estimators, unchanged, on one-minute last-trade prices and signed taker notional: the stability
  margin (decided if its 95% day-bootstrap interval excludes zero) and the price-only identification of two memory rates
  (C2's corrected criterion: separation interval excludes zero, neither rate interval touches a bound of the fit).
* TAGGED (the participant-level contract): for each of the 10 accounts with the largest traded notional, its position
  P (cumulative net base size bought) and the price displacement x at the last minute of each five-minute bar (C3's
  displacement, computed continuously across consecutive days and sampled so that it is known before any trade of the
  next bar), the regression dP_{k+1} = c + (r - 1) P_k + w x_k + e over the bars of valid days, with a 200-draw day-block bootstrap:
  r is the account's memory rate (persistence of its position), w its response to the displacement (w < 0: contrarian).
  A coin is TAG-IDENTIFIED if two of its top-10 accounts have disjoint 95% intervals for r, each interval inside (0, 1).

Primaries (Holm across the two at 0.05):
  P1  real agents are distinct and their records reveal it: the coin is tag-identified in at least 75% of evaluable
      coins (one-sided binomial p against 1/2 below 0.05);
  P2  prices do not reveal what the records do: b = #(tag-identified, price-only not identified) exceeds
      c = #(price-only identified, not tag-identified), exact one-sided McNemar p below 0.05.
Secondary: the notional-weighted share of top accounts that are contrarian (w interval below zero) and momentum (above);
the margin decided and its sign on a new venue; the median ratio of interval widths for the slow memory (tagged slowest
stationary account against price-only slow rate); per coin, the number of top accounts with interval for r inside (0,1);
on the valid day with the largest median adverse excursion, the net taker flow of contrarian and momentum accounts.

Usage. Colab collector: `await h1_hyperliquid.collect(out_dir, hours=11.5)`. Analysis: `h1_hyperliquid.run(out_dir)`.
Local test: `python h1_hyperliquid.py --selftest`.
"""
import argparse
import asyncio
import gzip
import hashlib
import io
import json
import math
import subprocess
import sys
import time
import urllib.request
from collections import defaultdict
from datetime import datetime, timezone
from pathlib import Path

import numpy as np
import pandas as pd
from scipy import stats

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import c2_margin_vs_identify as C2  # noqa: E402
import c3_margin_more_days as C3  # noqa: E402
import pilot4_curve_and_risk as P4  # noqa: E402

THESIS = HERE.parent
ROOT = THESIS.parent
SPEC = THESIS / "checks/prereg/H1_hyperliquid.json"
COUNTER = THESIS / "checks/prereg/H1_unlock.json"
RESULT = HERE / "H1_results.json"
NUMBERS = THESIS / "checks/H1_numbers.tex"

INFO, WS = "https://api.hyperliquid.xyz/info", "wss://api.hyperliquid.xyz/ws"
RANK_LO, RANK_HI = 10, 40              # ranks 11..40 by 24-hour notional volume
COVER_MIN, MIN_DAYS, MIN_COINS = 0.95, 30, 20
OPEN_DATE, FORCE_DATE = "2026-12-10", "2027-01-31"
TOP_K, B_BOOT, SEED, SHARE, ALPHA = 10, 200, 20261108, 0.75, 0.05
COLS = ["time", "side", "px", "sz", "buyer", "seller", "tid"]


# ------------------------------------------------------------------------------------------------------- collector
def http_post(payload, timeout=30):
    req = urllib.request.Request(INFO, data=json.dumps(payload).encode(), headers={"Content-Type": "application/json"})
    return json.loads(urllib.request.urlopen(req, timeout=timeout).read())


def draw_universe(out_dir, fetch=http_post):
    p = Path(out_dir) / "H1_universe.json"
    if p.exists():
        return json.loads(p.read_text())["symbols"]
    meta, ctxs = fetch({"type": "metaAndAssetCtxs"})
    rows = [(u["name"], float(c.get("dayNtlVlm") or 0.0)) for u, c in zip(meta["universe"], ctxs)
            if not u.get("isDelisted") and u["name"].isascii() and u["name"].isalnum()]
    rows.sort(key=lambda r: -r[1])
    chosen = [r[0] for r in rows[RANK_LO:RANK_HI]]
    Path(out_dir).mkdir(parents=True, exist_ok=True)
    p.write_text(json.dumps({"rule": "perpetuals ranked 11-40 by 24h notional volume (metaAndAssetCtxs), ASCII "
                                     "alphanumeric, not delisted", "drawn_utc": datetime.now(timezone.utc).isoformat(),
                             "ranking": rows[:60], "symbols": chosen}, indent=1) + "\n")
    return chosen


def _hour_key(ms):
    d = datetime.fromtimestamp(ms / 1000, tz=timezone.utc)
    return d.strftime("%Y-%m-%d"), d.hour


class Recorder:
    """Buffers trades by coin and UTC hour, deduplicates, and merges into hourly gzip CSV files."""

    def __init__(self, out_dir):
        self.out = Path(out_dir); self.buf = defaultdict(list); self.seen = {}; self.cover = defaultdict(float)

    def add(self, t):
        key = (t["coin"], int(t["time"]), int(t["tid"]))
        if key in self.seen:
            return
        self.seen[key] = t["time"]
        users = t.get("users") or ["", ""]
        date, hour = _hour_key(int(t["time"]))
        self.buf[(t["coin"], date, hour)].append([int(t["time"]), t["side"], float(t["px"]), float(t["sz"]),
                                                  users[0], users[1], int(t["tid"])])

    def credit(self, t0, t1):
        """Seconds of live connection between t0 and t1 (unix seconds), by UTC minute."""
        t = t0
        while t < t1:
            m = math.floor(t / 60) * 60; nxt = min(t1, m + 60)
            self.cover[int(m)] += nxt - t; t = nxt

    def flush(self, now=None, final=False):
        now = now or time.time()
        for key in list(self.buf):
            coin, date, hour = key
            end = datetime.strptime(date, "%Y-%m-%d").replace(tzinfo=timezone.utc).timestamp() + 3600 * (hour + 1)
            if final or now > end + 600:
                self._merge(coin, date, hour, self.buf.pop(key))
        if final or len(self.cover) > 120:
            self._merge_cover()
        cut = (now - 7200) * 1000
        self.seen = {k: v for k, v in self.seen.items() if v >= cut}

    def _merge(self, coin, date, hour, rows):
        f = self.out / "trades" / coin / date / f"{hour:02d}.csv.gz"; f.parent.mkdir(parents=True, exist_ok=True)
        new = pd.DataFrame(rows, columns=COLS)
        if f.exists():
            new = pd.concat([pd.read_csv(f), new])
        new = new.drop_duplicates(["time", "tid"]).sort_values("time")
        tmp = f.with_suffix(".tmp"); new.to_csv(tmp, index=False, compression="gzip"); tmp.replace(f)

    def _merge_cover(self):
        by_date = defaultdict(dict)
        for m, s in self.cover.items():
            by_date[datetime.fromtimestamp(m, tz=timezone.utc).strftime("%Y-%m-%d")][str(m)] = min(60.0, s)
        for date, d in by_date.items():
            f = self.out / "coverage" / f"{date}.json"; f.parent.mkdir(parents=True, exist_ok=True)
            old = json.loads(f.read_text()) if f.exists() else {}
            for k, v in d.items():
                old[k] = max(old.get(k, 0.0), v)          # overlapping collectors: take the max, never the sum
            f.write_text(json.dumps(old))
        self.cover.clear()


async def collect(out_dir, hours=11.5, symbols=None):
    import websockets
    syms = symbols or draw_universe(out_dir)
    rec = Recorder(out_dir); deadline = time.time() + hours * 3600; n = 0
    print(f"collecting {len(syms)} coins until {datetime.fromtimestamp(deadline, tz=timezone.utc)}", flush=True)
    while time.time() < deadline:
        try:
            async with websockets.connect(WS, ping_interval=20, ping_timeout=20, max_size=2 ** 24) as ws:
                for s in syms:
                    await ws.send(json.dumps({"method": "subscribe", "subscription": {"type": "trades", "coin": s}}))
                last = time.time()
                while time.time() < deadline:
                    try:
                        msg = await asyncio.wait_for(ws.recv(), timeout=30)
                    except asyncio.TimeoutError:
                        await ws.send(json.dumps({"method": "ping"}))
                        msg = None
                    now = time.time(); rec.credit(last, now); last = now
                    if msg:
                        d = json.loads(msg)
                        if d.get("channel") == "trades":
                            for t in d.get("data", []):
                                rec.add(t); n += 1
                    rec.flush(now)
                    if n and n % 50000 == 0:
                        print(f"  {n} trades, {datetime.now(timezone.utc):%Y-%m-%d %H:%M} UTC", flush=True)
        except Exception as err:                         # disconnects happen; reconnect (the snapshot refills gaps)
            print("  reconnect after:", repr(err)[:120], flush=True)
            await asyncio.sleep(5)
    rec.flush(final=True)
    print(f"stopped; {n} trades recorded this session", flush=True)
    return n


# ------------------------------------------------------------------------------------------------------- data
def coverage(out_dir, date):
    f = Path(out_dir) / "coverage" / f"{date}.json"
    return sum(json.loads(f.read_text()).values()) / 86400 if f.exists() else 0.0


def load_trades(out_dir, coin, date):
    d = Path(out_dir) / "trades" / coin / date
    fs = sorted(d.glob("*.csv.gz")) if d.exists() else []
    if not fs:
        return None
    t = pd.concat([pd.read_csv(f) for f in fs]).drop_duplicates(["time", "tid"]).sort_values("time")
    return t


def day_frame(tr, date):
    t0 = pd.Timestamp(date, tz="UTC").value // 10 ** 6
    m = ((tr["time"].to_numpy() - t0) // 60000).astype(int)
    ok = (m >= 0) & (m < 1440); tr, m = tr[ok], m[ok]
    if len(tr) == 0:
        return None
    sign = np.where(tr["side"].to_numpy() == "B", 1.0, -1.0)
    close = pd.Series(tr["px"].to_numpy(float)).groupby(m).last().reindex(range(1440)).ffill().bfill()
    flow = pd.Series(sign * tr["px"].to_numpy(float) * tr["sz"].to_numpy(float) / 1e6).groupby(m).sum().reindex(range(1440)).fillna(0)
    return pd.DataFrame({"close": close.to_numpy(), "flow": flow.to_numpy()})


def account_bars(tr, date):
    """Net base size bought per account in each five-minute bar (0..287), and traded notional per account."""
    t0 = pd.Timestamp(date, tz="UTC").value // 10 ** 6
    b = ((tr["time"].to_numpy() - t0) // 300000).astype(int)
    ok = (b >= 0) & (b < 288); tr, b = tr[ok], b[ok]
    sz, ntl = tr["sz"].to_numpy(float), tr["px"].to_numpy(float) * tr["sz"].to_numpy(float)
    net = pd.concat([pd.DataFrame({"acct": tr["buyer"].to_numpy(), "bar": b, "q": sz}),
                     pd.DataFrame({"acct": tr["seller"].to_numpy(), "bar": b, "q": -sz})])
    nt = pd.concat([pd.DataFrame({"acct": tr["buyer"].to_numpy(), "n": ntl}), pd.DataFrame({"acct": tr["seller"].to_numpy(), "n": ntl})])
    return net.groupby(["acct", "bar"])["q"].sum(), nt.groupby("acct")["n"].sum()


def bar_prices(df):
    """Log price (bp) at the last minute of each five-minute bar (minutes 4, 9, ..., 1439)."""
    return np.log(df["close"].to_numpy(float))[np.arange(4, 1440, 5)] * 1e4


def displacements(marks):
    """C3's displacement (price minus its EMA, span 12 bars) computed continuously across consecutive collected days,
    restarting after a day with no data; x[k] is known before any trade of bar k+1, so the account regressions use
    only predetermined regressors. `marks` maps date -> bar prices or None; returns date -> x."""
    out, run, run_dates = {}, [], []
    def close_run():
        if run:
            p = np.concatenate(run); x = p - pd.Series(p).ewm(span=C3.SPAN, adjust=False).mean().to_numpy()
            x[:C3.SPAN] = np.nan
            for i, d in enumerate(run_dates):
                out[d] = x[288 * i:288 * (i + 1)]
        run.clear(); run_dates.clear()
    for d, m in marks.items():
        if m is None:
            close_run()
        else:
            run.append(m); run_dates.append(d)
    close_run()
    return out


def coin_data(out_dir, coin, dates):
    """Valid-day records for C3's estimators and, for every collected day, five-minute account nets."""
    recs, valid, nets, ntl, marks, maes = [], [], {}, defaultdict(float), {}, {}
    for date in dates:
        tr = load_trades(out_dir, coin, date)
        df = day_frame(tr, date) if tr is not None else None
        marks[date] = bar_prices(df) if df is not None else None
        if tr is None:
            continue
        a, n = account_bars(tr, date); nets[date] = a
        if df is None or coverage(out_dir, date) < COVER_MIN:
            continue
        r = P4.day_record(df)
        if r is None:
            continue
        for k, v in n.items():
            ntl[k] += v
        recs.append({k: r[k] for k in ("k_ret", "price", "k_x")}); valid.append(date); maes[date] = r["y"]["mae"]
    xs = displacements(marks)
    return recs, valid, nets, ntl, xs, maes


# ------------------------------------------------------------------------------------------------------- tagged estimates
def tagged_fits(acct, all_dates, nets, valid, xs, j):
    """Day-block bootstrap of dP_{k+1} = c + (r-1) P_k + w x_k + e for one account, on valid days."""
    path, offset, per_day = [], 0.0, {}
    for date in all_dates:
        q = np.zeros(288)
        if date in nets:
            s = nets[date]
            if acct in s.index.get_level_values(0):
                v = s.loc[acct]; q[v.index.to_numpy()] = v.to_numpy()
        P = offset + np.cumsum(q); offset = P[-1]
        per_day[date] = (P, q)
    A, b = [], []
    for date in valid:
        P, q = per_day[date]; x = xs[date]
        k = np.arange(len(x) - 1); ok = np.isfinite(x[k])
        X = np.column_stack([np.ones(ok.sum()), P[k][ok], x[k][ok]]); y = q[k + 1][ok]
        A.append(X.T @ X); b.append(X.T @ y)
    A, b = np.stack(A), np.stack(b); n = len(valid)
    rng = np.random.default_rng(SEED + 31 * j)
    W = np.vstack([np.ones(n)] + [np.bincount(rng.integers(0, n, n), minlength=n) for _ in range(B_BOOT)]).astype(float)
    est = []
    for w in W:
        try:
            est.append(np.linalg.solve(np.tensordot(w, A, 1), np.tensordot(w, b, 1)))
        except np.linalg.LinAlgError:
            est.append(np.full(3, np.nan))
    est = np.array(est); r = 1 + est[:, 1]; wx = est[:, 2]
    rc, wc = C2.ci(r[1:]), C2.ci(wx[1:])
    return {"r": float(r[0]), "r_ci": rc, "w": float(wx[0]), "w_ci": wc,
            "stationary": bool(np.isfinite(rc[0]) and rc[0] > 0 and rc[1] < 1)}


def tag_identified(fits):
    st = [f for f in fits if f["stationary"]]
    return any(a["r_ci"][1] < b["r_ci"][0] or b["r_ci"][1] < a["r_ci"][0] for i, a in enumerate(st) for b in st[i + 1:])


def coin_eval(out_dir, coin, dates, j):
    recs, valid, nets, ntl, xs, maes = coin_data(out_dir, coin, dates)
    if len(valid) < MIN_DAYS:
        return {"n_days": len(valid), "excluded": f"fewer than {MIN_DAYS} valid days"}
    out = C3.symbol_eval(recs, j)
    top = sorted(ntl, key=lambda k: -ntl[k])[:TOP_K]
    fits = {}
    for i, acct in enumerate(top):
        fits[acct] = {**tagged_fits(acct, dates, nets, valid, xs, 1000 * j + i), "notional": float(ntl[acct])}
    tot = sum(f["notional"] for f in fits.values())
    out.update({"valid_days": valid, "top_accounts": fits, "tag_identified": tag_identified(list(fits.values())),
                "n_stationary": sum(f["stationary"] for f in fits.values()),
                "contrarian_share": sum(f["notional"] for f in fits.values() if f["w_ci"][1] < 0) / tot if tot else np.nan,
                "momentum_share": sum(f["notional"] for f in fits.values() if f["w_ci"][0] > 0) / tot if tot else np.nan,
                "daily_mae": maes})
    st = [f for f in fits.values() if f["stationary"]]
    if st and np.isfinite(out["r_slow_ci"][0]):
        slow = max(st, key=lambda f: f["r"])
        hl = lambda r: np.log(np.log(0.5) / np.log(np.clip(r, 1e-6, 1 - 1e-9)))
        out["width_ratio_log_halflife"] = float(abs(hl(out["r_slow_ci"][1]) - hl(out["r_slow_ci"][0])) /
                                               max(abs(hl(slow["r_ci"][1]) - hl(slow["r_ci"][0])), 1e-9))
    return out


def evaluate(per):
    ev = {s: v for s, v in per.items() if "excluded" not in v}
    n = len(ev); out = {"n_evaluable": n, "void": n < MIN_COINS}
    if out["void"]:
        return out
    ti = sum(v["tag_identified"] for v in ev.values())
    b = sum(v["tag_identified"] and not v["identified"] for v in ev.values())
    c = sum(v["identified"] and not v["tag_identified"] for v in ev.values())
    p1 = float(stats.binom.sf(ti - 1, n, 0.5)); p2 = float(stats.binom.sf(b - 1, b + c, 0.5)) if b + c else 1.0
    adj = C2.holm([p1, p2]); need = math.ceil(SHARE * n)
    out.update({"threshold_count": need, "tag_identified": ti, "price_identified": sum(v["identified"] for v in ev.values()),
                "mcnemar_b": b, "mcnemar_c": c, "p_raw": [p1, p2], "p_holm": adj,
                "P1_pass": bool(ti >= need and adj[0] < ALPHA), "P2_pass": bool(b > c and adj[1] < ALPHA),
                "secondary": {
                    "median_contrarian_share": float(np.nanmedian([v["contrarian_share"] for v in ev.values()])),
                    "median_momentum_share": float(np.nanmedian([v["momentum_share"] for v in ev.values()])),
                    "margin_decided": sum(v["decided"] for v in ev.values()),
                    "margin_safe": sum(v["sign"] == "safe" for v in ev.values()),
                    "margin_unsafe": sum(v["sign"] == "unsafe" for v in ev.values()),
                    "median_width_ratio": float(np.nanmedian([v.get("width_ratio_log_halflife", np.nan) for v in ev.values()])),
                    "median_stationary_top_accounts": float(np.median([v["n_stationary"] for v in ev.values()]))}})
    return out


def numbers_tex(e):
    if e["void"]:
        return "% generated by h1_hyperliquid.py\n\\newcommand{\\HoneVoid}{void}\n"
    v = lambda k: "passed" if e[k] else "failed"
    return "\n".join(["% generated by h1_hyperliquid.py; do not edit",
                      f"\\newcommand{{\\HoneCoins}}{{{e['n_evaluable']}}}\\newcommand{{\\HoneNeed}}{{{e['threshold_count']}}}",
                      f"\\newcommand{{\\HoneTag}}{{{e['tag_identified']}}}\\newcommand{{\\HonePrice}}{{{e['price_identified']}}}",
                      f"\\newcommand{{\\HoneB}}{{{e['mcnemar_b']}}}\\newcommand{{\\HoneC}}{{{e['mcnemar_c']}}}",
                      f"\\newcommand{{\\HonePone}}{{{v('P1_pass')}}}\\newcommand{{\\HonePtwo}}{{{v('P2_pass')}}}"]) + "\n"


# ------------------------------------------------------------------------------------------------------- gate and run
PIPELINE = (("h1_sha256", "h1_hyperliquid.py"), ("c3_sha256", "c3_margin_more_days.py"),
            ("c2_sha256", "c2_margin_vs_identify.py"), ("pilot4_sha256", "pilot4_curve_and_risk.py"))


def gate(skip=False):
    if skip:
        return None, None, None
    assert SPEC.exists(), "Test H1 is a draft and is not registered"
    sha = hashlib.sha256(SPEC.read_bytes()).hexdigest()
    assert sha == SPEC.with_suffix(".sha256").read_text().strip(), "specification hash mismatch"
    spec = json.loads(SPEC.read_text())
    for key, f in PIPELINE:
        assert hashlib.sha256((HERE / f).read_bytes()).hexdigest() == spec[key], f"{f} changed after registration"
    reg = subprocess.check_output(["git", "log", "-1", "--format=%H", "--", str(SPEC.relative_to(ROOT))], cwd=ROOT, text=True).strip()
    assert reg, "the specification is not committed"
    return spec, sha, reg


def collected_dates(out_dir):
    d = Path(out_dir) / "coverage"
    return sorted(f.stem for f in d.glob("*.json")) if d.exists() else []


def data_gate(out_dir, today=None):
    """Counts valid days per coin (coverage and C3's rule only) and decides whether the analysis may open."""
    today = today or datetime.now(timezone.utc).strftime("%Y-%m-%d")
    syms = json.loads((Path(out_dir) / "H1_universe.json").read_text())["symbols"]
    dates = [d for d in collected_dates(out_dir) if d < today]
    n_ok = 0
    for s in syms:
        k = 0
        for date in dates:
            if coverage(out_dir, date) < COVER_MIN:
                continue
            tr = load_trades(out_dir, s, date); df = day_frame(tr, date) if tr is not None else None
            k += df is not None and C3.day_stats(df) is not None
        n_ok += k >= MIN_DAYS
    opens = (today >= OPEN_DATE and n_ok >= MIN_COINS) or today >= FORCE_DATE
    return {"today": today, "collected_days": len(dates), "evaluable_coins": n_ok, "opens": bool(opens)}


def run(out_dir, skip_gate=False, today=None):
    spec, sha, reg = gate(skip_gate)
    dg = data_gate(out_dir, today)
    print("data gate:", dg, flush=True)
    assert dg["opens"] or skip_gate, "H1 cannot open yet (see the data gate)"
    if not skip_gate:
        c = json.loads(COUNTER.read_text()); assert c["opens"] == 0, "Test H1 was already opened; it runs once"
        COUNTER.write_text(json.dumps({"opens": 1, "spec_sha256": sha, "registration_commit": reg,
                                       "opened_utc": datetime.now(timezone.utc).isoformat(), "data_gate": dg}, indent=2) + "\n")
    syms = json.loads((Path(out_dir) / "H1_universe.json").read_text())["symbols"]
    dates = [d for d in collected_dates(out_dir) if d < dg["today"]]
    per = {}
    for j, s in enumerate(syms):
        per[s] = coin_eval(out_dir, s, dates, j)
        v = per[s]; print(f"  {s}: valid={v['n_days']} tag={v.get('tag_identified')} price={v.get('identified')} "
                          f"margin={v.get('sign')}", flush=True)
    res = {"test": "H1", "spec_sha256": sha, "registration_commit": reg, "run_utc": datetime.now(timezone.utc).isoformat(),
           "data_gate": dg, "symbols": syms, "per_coin": per, "evaluation": evaluate(per)}
    RESULT.write_text(json.dumps(res, indent=1, default=float) + "\n")
    NUMBERS.write_text(numbers_tex(res["evaluation"]))
    print(json.dumps({k: v for k, v in res["evaluation"].items() if k != "secondary"}, indent=1, default=float))
    return res


# ------------------------------------------------------------------------------------------------------- selftest
def _synthetic(out_dir, n_coins=21, n_days=31, rng=None):
    """Writes trades in the collector's format: three planted accounts with distinct memory, one market maker."""
    rng = rng or np.random.default_rng(3)
    out = Path(out_dir); syms = [f"C{i}" for i in range(n_coins)]
    (out / "H1_universe.json").write_text(json.dumps({"symbols": syms}))
    dates = pd.date_range("2026-11-01", periods=n_days).strftime("%Y-%m-%d")
    for d in dates:
        (out / "coverage").mkdir(parents=True, exist_ok=True)
        (out / "coverage" / f"{d}.json").write_text(json.dumps({"0": 86400.0}))
    agents = [("0xA", 0.30, -40.0), ("0xB", 0.90, 25.0), ("0xC", 0.97, -10.0)]
    for s in syms:
        p, u, xbar = 100.0, np.zeros(3), np.log(100.0) * 1e4
        for d in dates:
            t0 = pd.Timestamp(d, tz="UTC").value // 10 ** 6; rows = []; tid = 0
            for k in range(288):
                lp = np.log(p) * 1e4; x = lp - xbar
                target = np.array([r * u[i] + (1 - r) * w * x / 100 for i, (_, r, w) in enumerate(agents)])
                dq = target - u + rng.normal(0, 3.0, 3); u = u + dq
                for i, (a, _, _) in enumerate(agents):
                    if abs(dq[i]) > 1e-9:
                        side = "B" if dq[i] > 0 else "A"
                        buyer, seller = (a, "0xMM") if dq[i] > 0 else ("0xMM", a)
                        p *= np.exp(dq[i] * 1e-5)               # the agent's own impact, at its trade
                        rows.append([t0 + 300000 * k + 1000 * i, side, p, abs(dq[i]), buyer, seller, tid]); tid += 1
                for mnt in range(5):                       # noise trades every minute so prices move
                    q = rng.exponential(0.2); side = "B" if rng.random() < 0.5 else "A"
                    p *= np.exp((1 if side == "B" else -1) * q * 2e-4 + rng.normal(0, 4e-4))
                    rows.append([t0 + 300000 * k + 60000 * mnt + 30000, side, p, q,
                                 "0xN" if side == "B" else "0xMM", "0xMM" if side == "B" else "0xN", tid]); tid += 1
                xbar = xbar + (2 / 13) * (np.log(p) * 1e4 - xbar)
            df = pd.DataFrame(rows, columns=COLS)
            for h in range(24):
                f = out / "trades" / s / d / f"{h:02d}.csv.gz"; f.parent.mkdir(parents=True, exist_ok=True)
                df[(df.time >= t0 + 3600000 * h) & (df.time < t0 + 3600000 * (h + 1))].to_csv(f, index=False, compression="gzip")
    return syms, list(dates)


def selftest():
    import tempfile
    # 1. recorder: dedupe, hourly merge, coverage by max
    with tempfile.TemporaryDirectory() as td:
        rec = Recorder(td); t = int(pd.Timestamp("2026-11-01 10:15", tz="UTC").value // 10 ** 6)
        msg = {"coin": "X", "side": "B", "px": "1.5", "sz": "2", "time": t, "tid": 7, "users": ["0xb", "0xs"]}
        rec.add(msg); rec.add(msg); rec.credit(t / 1000, t / 1000 + 90); rec.flush(final=True)
        rec2 = Recorder(td); rec2.add({**msg, "tid": 8}); rec2.add(msg); rec2.credit(t / 1000, t / 1000 + 30); rec2.flush(final=True)
        f = pd.read_csv(Path(td) / "trades/X/2026-11-01/10.csv.gz"); assert len(f) == 2 and set(f.buyer) == {"0xb"}
        cov = json.loads((Path(td) / "coverage/2026-11-01.json").read_text()); assert abs(sum(cov.values()) - 90) < 1e-6
        u = draw_universe(td, fetch=lambda _: ({"universe": [{"name": f"A{i}"} for i in range(50)] + [{"name": "哈"}]},
                                               [{"dayNtlVlm": str(100 - i)} for i in range(51)]))
        assert u == [f"A{i}" for i in range(10, 40)]
    # 2. synthetic market with planted accounts: tags identify distinct memories
    with tempfile.TemporaryDirectory() as td:
        syms, dates = _synthetic(td)
        per = {s: coin_eval(td, s, dates, j) for j, s in enumerate(syms)}
        some = per[syms[0]]["top_accounts"]
        print("planted r = 0.30, 0.90, 0.97 at the agent level; estimated:",
              {k: round(v["r"], 3) for k, v in some.items() if k in ("0xA", "0xB", "0xC")})
        e = evaluate(per)
        print(json.dumps({k: e.get(k) for k in ("n_evaluable", "tag_identified", "price_identified", "mcnemar_b",
                                                 "mcnemar_c", "P1_pass", "P2_pass")}))
        assert e["n_evaluable"] == 21 and e["P1_pass"]
        assert abs(some["0xA"]["r"] - 0.30) < 0.1 and abs(some["0xB"]["r"] - 0.90) < 0.05
        dg = data_gate(td, today="2026-12-15"); assert dg["opens"] and dg["evaluable_coins"] == 21
        assert not data_gate(td, today="2026-12-05")["opens"]
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
