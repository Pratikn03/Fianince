"""Test K1 (DRAFT, not registered): does the certified feedback track a feedback whose size is publicly known?

A leveraged or inverse ETF with daily leverage L and net assets A must, by the close, trade A * L * (L - 1) * R dollars of
exposure in the direction of the underlying's return R since the previous close (L(L-1) > 0 for L > 1 and for L < 0, so
bull and bear funds both trade with the move). For single-stock funds the hedge has to be traded in the stock itself.
The rebalancing intensity of a stock is therefore disclosed: Lambda_u = sum over its funds of A * L * (L - 1), and
relative to its trading volume, lambda_u = Lambda_u / ADV_u, it varies by orders of magnitude across stocks.

K1 asks whether the feedback certified from anonymous, tick-rule-signed trades -- the response of flow to the day's
displacement x = log price - log previous close, near the close relative to earlier in the afternoon -- is larger in
stocks with larger disclosed rebalancing intensity, and whether the certified margin falls with it.

Pipeline (each step writes a file and is safe to rerun):
  universe(...)            N-PORT fund net assets + Alpaca daily bars -> K1_universe.json (before any intraday data)
  fetch_windows(...)       Alpaca SIP trades in two windows per day -> minute bars (13:00-14:00 and 15:00-16:00 ET)
  unit_stats(...)          per stock and window: Phi (Primary 1), margin (Primary 2), secondaries
  evaluate(...)            Spearman tests across stocks, Holm, secondaries -> K1_results.json
  simulate_panel(...)      synthetic panel with a known rebalancing share, for the null and power calibration
"""
import io
import json
import re
import time
import urllib.error
import urllib.parse
import urllib.request
import zipfile
from pathlib import Path

import numpy as np
import pandas as pd

NY = "America/New_York"
SAMPLE = ("2025-07-01", "2026-06-30")                 # trading days, full sessions only (12 months)
PRE = ("2025-04-01", "2025-06-30")                    # pre-period: candidate pool and control matching
REPORTS = ("2025-06-30", "2026-06-30")                # N-PORT report dates used for net assets
WINDOWS = {"control": (210, 270), "close": (330, 390)}   # minutes after 09:30: 13:00-14:00 and 15:00-16:00
MIN_DV_POOL = 2e8                                      # candidate stocks: median daily dollar volume >= $200M (pre-period)
MIN_LAMBDA_DOLLARS = 5e7                               # treated: disclosed intensity Lambda_u >= $50M per unit return
N_CONTROLS = 2                                         # matched controls per treated stock
FLOW_LAGS, CERT_LAGS = 5, 12
N_PERM, SEED = 20000, 20261026
# Trades whose conditions include any of these are not continuous-session price-setting trades and are dropped
# (opening/closing/official prints, extended hours, out of sequence, average price, cash, next day, derivatively priced,
# contingent, prior reference, sold last).
DROP_CONDITIONS = set("OQM65TUZ4WCNR7VPHL9")

INDEX_WORDS = r"index|nasdaq|s&p|500|dow|russell|semiconductor|sector|bitcoin|ether|crypto|treasury|bond|gold|silver|oil|" \
              r"china|emerging|financial|biotech|energy|technology|tech |retail|homebuilder|regional|real estate|magnificent|" \
              r"basket|fang|innovation|airline|aerospace|transport|utilities|pharma|healthcare|cloud|cyber|robot|ai |quantum"
INCOME_WORDS = r"income|option|covered|yield|buywrite|premium|dividend|hedged|buffer|floor|cap\b|autocallable"
STOP_TICKERS = {"ETF", "DAILY", "BULL", "BEAR", "LONG", "SHORT", "TARGET", "SHARES", "TRUST", "FUND", "ULTRA", "PRO", "AND",
                "THE", "ON", "ALL", "IT", "INC", "CORP", "CO", "X", "TX", "US", "USA", "NEW", "ONE", "TWO", "MAX", "PLUS",
                "REX", "T", "A", "AI", "DE", "SA", "LP", "II", "III", "ARE", "BY", "FOR", "OF", "GO", "NOW", "SO", "HOOD"}


# --------------------------------------------------------------------------------------------- leverage from fund names
def parse_leverage(name):
    """Daily leverage of a fund from its series name, or None if the name does not state a daily leveraged or inverse
    exposure. '2X Long' -> 2, 'Bull 2X' -> 2, 'Bear 1X' -> -1, '2X Inverse' -> -2, 'UltraPro Short' -> -3,
    'Ultra' -> 2; income, option and buffer funds -> None; plain long single-stock funds (L = 1) -> None."""
    n = name.lower()
    if re.search(INCOME_WORDS, n):
        return None
    neg = bool(re.search(r"\b(bear|short|inverse)\b", n))
    m = re.search(r"(?<![\w.])(\d+(?:\.\d+)?)\s*x\b", n)
    if m:
        mult = float(m.group(1))
    elif "ultrapro" in n:
        mult = 3.0
    elif "ultra" in n:
        mult = 2.0
    elif neg:
        mult = 1.0
    else:
        return None
    lev = -mult if neg else mult
    return None if (lev == 1.0 or abs(lev) < 1.0 or abs(lev) > 5) else lev


def match_underlying(name, aliases):
    """The single candidate stock a fund name refers to, or None if it names none, several, or an index or sector.
    `aliases` maps ticker -> list of name aliases (the ticker itself and the company's first name word)."""
    if re.search(INDEX_WORDS, name.lower()):
        return None
    tokens = set(re.findall(r"[A-Za-z][A-Za-z.&-]*", name))
    upper = {t for t in tokens if t.isupper()}
    lower = {t.lower() for t in tokens}
    hits = set()
    for tic, als in aliases.items():
        if tic in upper and tic not in STOP_TICKERS:
            hits.add(tic)
        elif any(a.lower() in lower for a in als if len(a) >= 4):
            hits.add(tic)
    return hits.pop() if len(hits) == 1 else None


def company_alias(asset_name):
    """First word of the company name ('Tesla, Inc. Common Stock' -> 'Tesla'), or None if it is generic."""
    w = re.split(r"[\s,]+", asset_name.strip())[0] if asset_name else ""
    w = re.sub(r"[^A-Za-z.&-]", "", w)
    generic = {"the", "first", "american", "united", "general", "international", "global", "national", "new", "strategy",
               "target", "advanced", "applied", "digital", "energy", "southern", "western", "eastern", "north", "south"}
    return None if len(w) < 4 or w.lower() in generic else w


# --------------------------------------------------------------------------------------------- N-PORT net assets
def nport_funds(zip_paths, aliases, report_window=REPORTS):
    """Leveraged/inverse single-stock funds from SEC Form N-PORT data sets: one row per (series, report date) with net
    assets, parsed leverage and matched underlying. Keeps the latest amendment of each (series, report date)."""
    rows = []
    for zp in zip_paths:
        with zipfile.ZipFile(zp) as z:
            names = {Path(n).name.upper(): n for n in z.namelist()}
            sub = pd.read_csv(io.BytesIO(z.read(names["SUBMISSION.TSV"])), sep="\t", dtype=str,
                              usecols=lambda c: c in {"ACCESSION_NUMBER", "REPORT_DATE", "FILING_DATE", "SUB_TYPE"})
            fri = pd.read_csv(io.BytesIO(z.read(names["FUND_REPORTED_INFO.TSV"])), sep="\t", dtype=str,
                              usecols=lambda c: c in {"ACCESSION_NUMBER", "SERIES_NAME", "SERIES_ID", "NET_ASSETS"})
            rows.append(fri.merge(sub, on="ACCESSION_NUMBER", how="left"))
    d = pd.concat(rows, ignore_index=True)
    d["REPORT_DATE"] = pd.to_datetime(d["REPORT_DATE"], errors="coerce", format="mixed")
    d["FILING_DATE"] = pd.to_datetime(d.get("FILING_DATE"), errors="coerce", format="mixed")
    d["NET_ASSETS"] = pd.to_numeric(d["NET_ASSETS"], errors="coerce")
    d = d[(d["REPORT_DATE"] >= report_window[0]) & (d["REPORT_DATE"] <= report_window[1]) & (d["NET_ASSETS"] > 0)]
    d = d.sort_values(["SERIES_ID", "REPORT_DATE", "FILING_DATE"]).groupby(["SERIES_ID", "REPORT_DATE"]).tail(1)
    d["L"] = d["SERIES_NAME"].map(lambda s: parse_leverage(str(s)))
    d["underlying"] = d["SERIES_NAME"].map(lambda s: match_underlying(str(s), aliases))
    return d.dropna(subset=["L", "underlying"]).reset_index(drop=True)


def intensity(funds):
    """Lambda_u = sum over funds of mean net assets * L * (L - 1), and the funds behind it."""
    f = funds.groupby(["SERIES_ID", "SERIES_NAME", "underlying", "L"], as_index=False)["NET_ASSETS"].mean()
    f["Lambda"] = f["NET_ASSETS"] * f["L"] * (f["L"] - 1)
    f["side"] = np.where(f["L"] > 0, "bull", "bear")
    lam = f.groupby("underlying").agg(Lambda=("Lambda", "sum"), funds=("SERIES_NAME", list),
                                      Lambda_bull=("Lambda", lambda s: s[f.loc[s.index, "side"] == "bull"].sum()),
                                      Lambda_bear=("Lambda", lambda s: s[f.loc[s.index, "side"] == "bear"].sum()))
    return lam, f


def match_controls(treated, pool_stats, k=N_CONTROLS):
    """For each treated stock (largest Lambda first), the k nearest untreated stocks by standardized log median dollar
    volume and log daily volatility in the pre-period, without replacement."""
    z = pool_stats[["log_dv", "log_vol"]]
    z = (z - z.mean()) / z.std()
    free = [s for s in pool_stats.index if s not in treated]
    out = {}
    for t in treated:
        if t not in z.index:
            continue
        dist = ((z.loc[free] - z.loc[t]) ** 2).sum(1).sort_values()
        out[t] = list(dist.index[:k])
        free = [s for s in free if s not in out[t]]
    return out


# --------------------------------------------------------------------------------------------- Alpaca access
class Alpaca:
    DATA, TRADE = "https://data.alpaca.markets/v2", "https://paper-api.alpaca.markets/v2"

    def __init__(self, key, secret, pause=0.0):
        self.h = {"APCA-API-KEY-ID": key, "APCA-API-SECRET-KEY": secret}
        self.pause = pause

    def get(self, url, params=None, tries=6):
        q = url + ("?" + urllib.parse.urlencode(params) if params else "")
        for i in range(tries):
            try:
                with urllib.request.urlopen(urllib.request.Request(q, headers=self.h), timeout=120) as r:
                    time.sleep(self.pause)
                    return json.loads(r.read())
            except urllib.error.HTTPError as e:
                if e.code == 429:
                    time.sleep(15)
                    continue
                if e.code in (400, 403, 404, 422):
                    return {"_error": e.code, "_body": e.read().decode()[:300]}
                time.sleep(3 * (i + 1))
            except Exception:
                time.sleep(3 * (i + 1))
        return {"_error": "network"}

    def calendar(self, start, end):
        cal = self.get(f"{self.TRADE}/calendar", {"start": start, "end": end})
        return sorted(c["date"] for c in cal if isinstance(c, dict) and c.get("open") == "09:30" and c.get("close") == "16:00")

    def assets(self):
        a = self.get(f"{self.TRADE}/assets", {"status": "active", "asset_class": "us_equity"})
        return [x for x in a if isinstance(x, dict)]

    def daily(self, symbols, start, end, adjustment="raw"):
        out = {}
        for i in range(0, len(symbols), 100):
            tok = None
            while True:
                p = {"symbols": ",".join(symbols[i:i + 100]), "timeframe": "1Day", "start": start, "end": end, "feed": "sip",
                     "adjustment": adjustment, "limit": 10000}
                if tok:
                    p["page_token"] = tok
                r = self.get(f"{self.DATA}/stocks/bars", p)
                for s, bars in (r.get("bars") or {}).items():
                    out.setdefault(s, []).extend(bars)
                tok = r.get("next_page_token")
                if not tok:
                    break
        return {s: pd.DataFrame(b).assign(date=lambda d: pd.to_datetime(d["t"]).dt.tz_convert(NY).dt.strftime("%Y-%m-%d"))
                .set_index("date") for s, b in out.items()}

    def trades(self, sym, start_utc, end_utc):
        rows, tok = [], None
        while True:
            p = {"symbols": sym, "start": start_utc, "end": end_utc, "feed": "sip", "limit": 10000}
            if tok:
                p["page_token"] = tok
            r = self.get(f"{self.DATA}/stocks/trades", p)
            if "_error" in r:
                return None, str(r)[:200]
            rows.extend((t["t"], t["p"], t["s"], "".join(t.get("c") or [])) for t in (r.get("trades") or {}).get(sym, []))
            tok = r.get("next_page_token")
            if not tok:
                return rows, None


# --------------------------------------------------------------------------------------------- universe
def universe(api, nport_zips, out_path, exclusions=None):
    """Fix the treated stocks, their disclosed intensity and the matched controls, before any intraday data. Writes
    out_path (K1_universe.json). `exclusions`: {fund series id: reason} for name matches the author rejects on reading,
    recorded in the file; it may be used only in this step."""
    assets = api.assets()
    common = {a["symbol"]: a.get("name", "") for a in assets if a.get("tradable") and a.get("exchange") in ("NYSE", "NASDAQ", "AMEX")
              and re.fullmatch(r"[A-Z]{1,5}", a["symbol"]) and not re.search(r"\b(etf|fund|trust|shares|index|notes?|warrants?|"
              r"units?|rights?|depositary|preferred)\b", a.get("name", "").lower())}
    pre = api.daily(sorted(common), *PRE)
    stats = {}
    for s, d in pre.items():
        if len(d) >= 40:
            dv = float(np.median(d["c"] * d["v"]))
            stats[s] = {"dv": dv, "log_dv": np.log(dv), "log_vol": np.log(np.std(np.diff(np.log(d["c"].to_numpy()))) + 1e-9)}
    pool = pd.DataFrame(stats).T
    pool = pool[pool["dv"] >= MIN_DV_POOL]
    aliases = {s: [s] + ([company_alias(common[s])] if company_alias(common[s]) else []) for s in pool.index}
    funds = nport_funds(nport_zips, aliases)
    if exclusions:
        funds = funds[~funds["SERIES_ID"].isin(exclusions)]
    lam, fund_rows = intensity(funds)
    smp = api.daily(sorted(pool.index), *SAMPLE)
    adv = {s: float(np.median(d["c"] * d["v"])) for s, d in smp.items() if len(d) >= 60}
    lam = lam[lam.index.isin(adv)]
    treated = [s for s in lam.sort_values("Lambda", ascending=False).index if lam.loc[s, "Lambda"] >= MIN_LAMBDA_DOLLARS]
    dropped_small = [s for s in lam.index if s not in treated]
    controls = match_controls(treated, pool.drop(index=dropped_small, errors="ignore"))
    units = {s: {"role": "treated", "Lambda": float(lam.loc[s, "Lambda"]), "Lambda_bull": float(lam.loc[s, "Lambda_bull"]),
                 "Lambda_bear": float(lam.loc[s, "Lambda_bear"]), "ADV": adv[s], "lambda": float(lam.loc[s, "Lambda"]) / adv[s],
                 "funds": lam.loc[s, "funds"]} for s in treated}
    for t, cs in controls.items():
        for c in cs:
            units[c] = {"role": "control", "matched_to": t, "Lambda": 0.0, "Lambda_bull": 0.0, "Lambda_bear": 0.0,
                        "ADV": adv.get(c, float("nan")), "lambda": 0.0, "funds": []}
    out = {"units": units, "pool_size": int(len(pool)), "funds": fund_rows.to_dict("records"),
           "dropped_small_intensity": dropped_small, "exclusions": exclusions or {}, "sample": SAMPLE, "pre_period": PRE,
           "reports": REPORTS, "days": api.calendar(*SAMPLE)}
    Path(out_path).write_text(json.dumps(out, indent=1, default=str))
    return out


# --------------------------------------------------------------------------------------------- minute bars in two windows
def minute_bars(rows, date, window):
    """Minute bars of one window from (time, price, size, conditions) rows: last price, tick-rule signed dollar flow,
    dollar volume. The tick rule runs over the window's own continuous trades."""
    lo, hi = WINDOWS[window]
    t0 = pd.Timestamp(f"{date} 09:30", tz=NY).tz_convert("UTC")
    T = pd.DataFrame(rows, columns=["t", "p", "s", "c"])
    T = T[~T["c"].map(lambda c: bool(set(c) & DROP_CONDITIONS))]
    if T.empty:
        return None
    T["t"] = pd.to_datetime(T["t"], utc=True, format="ISO8601")
    T = T.sort_values("t", kind="stable")
    px, sz = T["p"].to_numpy(float), T["s"].to_numpy(float)
    sg = np.sign(np.diff(px, prepend=np.nan))
    sg = pd.Series(np.where(~np.isfinite(sg) | (sg == 0), np.nan, sg)).ffill().fillna(0).to_numpy()
    m = ((T["t"] - t0).dt.total_seconds() // 60).astype(int).to_numpy()
    ok = (m >= lo) & (m < hi)
    D = pd.DataFrame({"m": m[ok], "px": px[ok], "f": (sg * px * sz)[ok], "v": (px * sz)[ok]})
    g = D.groupby("m")
    idx = np.arange(lo, hi)
    return pd.DataFrame({"minute": idx, "px": g["px"].last().reindex(idx).to_numpy(), "f": g["f"].sum().reindex(idx).fillna(0).to_numpy(),
                         "v": g["v"].sum().reindex(idx).fillna(0).to_numpy(), "n": g.size().reindex(idx).fillna(0).to_numpy()})


def fetch_windows(api, sym, date, cache_dir):
    """Both windows of one stock-day, cached (parquet + status json). Returns (bars or None, status)."""
    d = Path(cache_dir) / sym
    d.mkdir(parents=True, exist_ok=True)
    pq, js = d / f"{date}.parquet", d / f"{date}.json"
    if js.exists():
        st = json.loads(js.read_text())
        return (pd.read_parquet(pq) if pq.exists() else None), st
    parts, st = [], {"symbol": sym, "date": date}
    for w, (lo, hi) in WINDOWS.items():
        t0 = pd.Timestamp(f"{date} 09:30", tz=NY) + pd.Timedelta(minutes=lo)
        t1 = pd.Timestamp(f"{date} 09:30", tz=NY) + pd.Timedelta(minutes=hi)
        rows, err = api.trades(sym, t0.tz_convert("UTC").isoformat().replace("+00:00", "Z"),
                               t1.tz_convert("UTC").isoformat().replace("+00:00", "Z"))
        if err:
            st.update(error=err, ok=False)
            js.write_text(json.dumps(st))
            return None, st
        b = minute_bars(rows, date, w) if rows else None
        cov = float((b["n"] > 0).mean()) if b is not None else 0.0
        st[f"coverage_{w}"] = cov
        st[f"trades_{w}"] = len(rows)
        if b is not None:
            parts.append(b.assign(window=w))
    st["ok"] = all(st.get(f"coverage_{w}", 0) >= 0.9 for w in WINDOWS)
    if parts:
        pd.concat(parts).to_parquet(pq)
    js.write_text(json.dumps(st))
    return (pd.concat(parts) if parts else None), st


def assemble(bars_by_day, daily_raw, daily_split):
    """Panel of one stock: rows (date, window, minute) with px, f, v, prev_close, close. Days on which a split changes the
    raw/adjusted ratio between the previous and the current day are dropped."""
    out = []
    ratio = (daily_raw["c"] / daily_split["c"]).reindex(daily_raw.index)
    dates = list(daily_raw.index)
    for date, b in bars_by_day.items():
        if b is None or date not in daily_raw.index:
            continue
        i = dates.index(date)
        if i == 0 or abs(np.log(ratio.iloc[i] / ratio.iloc[i - 1])) > 1e-6:
            continue
        out.append(b.assign(date=date, prev_close=float(daily_raw["c"].iloc[i - 1]), close=float(daily_raw["c"].iloc[i])))
    return pd.concat(out, ignore_index=True) if out else None


# --------------------------------------------------------------------------------------------- estimation
WLEN = {w: hi - lo for w, (lo, hi) in WINDOWS.items()}


def _ols(X, y, se=False):
    ok = np.all(np.isfinite(X), 1) & np.isfinite(y)
    if ok.sum() < X.shape[1] + 10:
        nan = np.full(X.shape[1], np.nan)
        return (nan, 0, nan) if se else (nan, 0)
    Xo, yo = X[ok], y[ok]
    b = np.linalg.lstsq(Xo, yo, rcond=None)[0]
    if not se:
        return b, int(ok.sum())
    e = yo - Xo @ b
    s2 = e @ e / (len(yo) - X.shape[1])
    return b, int(ok.sum()), np.sqrt(np.diag(s2 * np.linalg.pinv(Xo.T @ Xo)))


def _shift(M, k):
    """Columns shifted right by k within each row (day); NaN where the lag falls before the window."""
    out = np.full_like(M, np.nan)
    out[:, k:] = M[:, :-k]
    return out


def matrices(panel, window):
    """Days x minutes matrices of one window: log price (bp, carried forward within the day), flow, previous close (bp)."""
    w = panel[panel["window"] == window]
    lo, hi = WINDOWS[window]
    P = w.pivot_table(index="date", columns="minute", values="px", aggfunc="last").reindex(columns=range(lo, hi))
    F = w.pivot_table(index="date", columns="minute", values="f", aggfunc="sum").reindex(index=P.index, columns=range(lo, hi))
    pc = w.groupby("date")["prev_close"].first().reindex(P.index)
    lp = 1e4 * np.log(P.ffill(axis=1).to_numpy(float))
    return lp, F.fillna(0.0).to_numpy(float), 1e4 * np.log(pc.to_numpy(float))[:, None], list(P.index)


def window_stats(mats, norm, state="day", rows=None):
    """Phi (flow response to x_{t-1} with five lagged flows, Primary 1) and the certificate (Primary 2) in one window.
    state 'day': x = log price - log previous close; 'ema': x = p - EMA_12(p) within the window (first 12 minutes dropped).
    `rows`: boolean mask of days to use."""
    lp, F, pc, _ = mats
    if rows is not None:
        lp, F, pc = lp[rows], F[rows], pc[rows]
    f = F / norm
    if state == "day":
        x = lp - pc
    else:
        ema = np.empty_like(lp)
        ema[:, 0] = lp[:, 0]
        a = 2 / 13
        for j in range(1, lp.shape[1]):
            ema[:, j] = np.where(np.isfinite(ema[:, j - 1]), ema[:, j - 1] + a * (lp[:, j] - ema[:, j - 1]), lp[:, j])
        x = lp - ema
        x[:, :12] = np.nan
    r = lp - _shift(lp, 1)
    x1 = _shift(x, 1)
    v = lambda M: M.ravel()
    one = np.ones(f.size)
    c1, n1, se1 = _ols(np.column_stack([one, v(x1)] + [v(_shift(f, j)) for j in range(1, FLOW_LAGS + 1)]), v(f), se=True)
    cp, _ = _ols(np.column_stack([one, v(f), v(x1)]), v(r))
    ck, _ = _ols(np.column_stack([one] + [v(_shift(x, m)) for m in range(1, CERT_LAGS + 1)]), v(f))
    kappa, beta = cp[1], cp[2]
    Phi = float(np.sum(ck[1:])) if np.isfinite(ck).all() else np.nan
    return {"phi": float(c1[1]), "phi_se": float(se1[1]), "n": n1, "kappa": float(kappa), "beta": float(beta), "Phi_cert": Phi,
            "margin": float(-beta - kappa * Phi)}


def auction_slope(panel):
    """Secondary S3: slope of the closing-auction return 1e4 log(close / last pre-close price) on the day displacement then."""
    w = panel[(panel["window"] == "close")].sort_values(["date", "minute"]).dropna(subset=["px"]).groupby("date").last()
    y = 1e4 * np.log(w["close"] / w["px"])
    x = 1e4 * np.log(w["px"] / w["prev_close"])
    c, _ = _ols(np.column_stack([np.ones(len(w)), x.to_numpy()]), y.to_numpy())
    return float(c[1])


def unit_stats(panel, valid_days):
    """All per-stock statistics on the stock's valid days. norm = median per-minute dollar volume over both windows."""
    pn = panel[panel["date"].isin(valid_days)]
    norm = float(np.median(pn["v"]))
    M = {w: matrices(pn, w) for w in WINDOWS}
    s = {w: window_stats(M[w], norm) for w in WINDOWS}
    e = {w: window_stats(M[w], norm, state="ema") for w in WINDOWS}
    lp, _, pc, days = M["close"]
    last = np.array([row[np.isfinite(row)][-1] if np.isfinite(row).any() else np.nan for row in lp])
    move = np.abs(last - pc[:, 0])
    big = {w: move >= np.nanmedian(move) for w in WINDOWS}
    if M["control"][3] != days:
        mv = pd.Series(move, index=days)
        big["control"] = mv.reindex(M["control"][3]).to_numpy() >= np.nanmedian(move)
    sb = {w: window_stats(M[w], norm, rows=big[w]) for w in WINDOWS}
    return {"days": int(pn["date"].nunique()), "norm": norm, "minute_dollar_volume": norm,
            "dPhi": s["close"]["phi"] - s["control"]["phi"],
            "dPhi_se": float(np.hypot(s["close"]["phi_se"], s["control"]["phi_se"])), "dM": s["close"]["margin"] - s["control"]["margin"],
            "dM_ema": e["close"]["margin"] - e["control"]["margin"], "dPhi_ema": e["close"]["phi"] - e["control"]["phi"],
            "dPhi_bigdays": sb["close"]["phi"] - sb["control"]["phi"], "auction_slope": auction_slope(pn),
            "windows": s, "windows_ema": e}


# --------------------------------------------------------------------------------------------- tests
def spearman(a, b):
    ra, rb = pd.Series(a).rank().to_numpy(), pd.Series(b).rank().to_numpy()
    return float(np.corrcoef(ra, rb)[0, 1])


def perm_test(a, b, sign, n=N_PERM, seed=SEED):
    """One-sided permutation p-value for Spearman(a, b) in direction `sign` (+1 or -1)."""
    if np.nanstd(np.asarray(a, float)) == 0 or np.nanstd(np.asarray(b, float)) == 0:
        return float("nan"), 1.0
    rng = np.random.default_rng(seed)
    obs = spearman(a, b)
    rb = pd.Series(b).rank().to_numpy()
    ra = pd.Series(a).rank().to_numpy()
    null = np.array([np.corrcoef(ra, rng.permutation(rb))[0, 1] for _ in range(n)])
    p = float((np.sum(sign * null >= sign * obs) + 1) / (n + 1))
    return obs, p


def wslope_test(y, lam, se, sign, n=N_PERM, seed=SEED):
    """One-sided permutation test of the precision-weighted least-squares slope of y on lambda (weights 1/se^2),
    shuffling lambda across stocks. Returns (slope, p)."""
    y, lam, w = np.asarray(y, float), np.asarray(lam, float), 1 / np.asarray(se, float) ** 2
    if np.nanstd(lam) == 0:
        return float("nan"), 1.0

    def slope(l):
        lm, ym = np.sum(w * l) / w.sum(), np.sum(w * y) / w.sum()
        return np.sum(w * (l - lm) * (y - ym)) / np.sum(w * (l - lm) ** 2)
    rng = np.random.default_rng(seed)
    obs = slope(lam)
    null = np.array([slope(rng.permutation(lam)) for _ in range(n)])
    return float(obs), float((np.sum(sign * null >= sign * obs) + 1) / (n + 1))


def holm(ps, alpha=0.05):
    order = np.argsort(ps)
    passed, ok = [False] * len(ps), True
    for i, j in enumerate(order):
        ok = ok and ps[j] <= alpha / (len(ps) - i)
        passed[j] = ok
    return passed


def evaluate(stats, units, min_day_share=0.8, n_days=None):
    """Primary 1: Spearman(dPhi, lambda) > 0. Primary 2: Spearman(dM, lambda) < 0. One-sided permutation tests, Holm."""
    keep = [s for s in stats if s in units and np.isfinite(stats[s]["dPhi"]) and np.isfinite(stats[s]["dM"])
            and (n_days is None or stats[s]["days"] >= min_day_share * n_days)]
    lam = np.array([units[s]["lambda"] for s in keep])
    dphi = np.array([stats[s]["dPhi"] for s in keep]); dm = np.array([stats[s]["dM"] for s in keep])
    r1, p1 = perm_test(dphi, lam, +1); r2, p2 = perm_test(dm, lam, -1)
    passed = holm([p1, p2])
    tr = [s for s in keep if units[s]["role"] == "treated"]
    share = {s: stats[s]["dPhi"] * stats[s]["minute_dollar_volume"] * WLEN["close"] / (units[s]["Lambda"] * 1e-4) for s in tr}
    se = np.array([stats[s]["dPhi_se"] for s in keep])
    sec = {
        "W_weighted_slope_dPhi": dict(zip(["slope", "p"], wslope_test(dphi, lam, se, +1))),
        "S1_visible_share_of_disclosed_rebalancing": {"median": float(np.median(list(share.values()))) if share else None,
                                                      "by_stock": share},
        "S2_default_monitor_ema12": dict(zip(["rho", "p"], perm_test([stats[s]["dM_ema"] for s in keep], lam, -1))),
        "S2b_default_monitor_phi": dict(zip(["rho", "p"], perm_test([stats[s]["dPhi_ema"] for s in keep], lam, +1))),
        "S3_closing_auction_slope": dict(zip(["rho", "p"], perm_test([stats[s]["auction_slope"] for s in keep], lam, +1))),
        "S4_bull_only": dict(zip(["rho", "p"], perm_test(dphi, [units[s]["Lambda_bull"] / units[s]["ADV"] if units[s]["ADV"] else 0
                                                                for s in keep], +1))),
        "S4_bear_only": dict(zip(["rho", "p"], perm_test(dphi, [units[s]["Lambda_bear"] / units[s]["ADV"] if units[s]["ADV"] else 0
                                                                for s in keep], +1))),
        "S5_large_move_days": dict(zip(["rho", "p"], perm_test([stats[s]["dPhi_bigdays"] for s in keep], lam, +1))),
        "S6_treated_vs_matched_controls_median_dPhi": {
            "treated": float(np.median([stats[s]["dPhi"] for s in tr])) if tr else None,
            "controls": float(np.median([stats[s]["dPhi"] for s in keep if units[s]["role"] == "control"]))},
    }
    return {"n_units": len(keep), "n_treated": len(tr),
            "primary_1": {"rho": r1, "p": p1, "passed_holm": passed[0]},
            "primary_2": {"rho": r2, "p": p2, "passed_holm": passed[1]},
            "secondary": sec, "units_used": keep}


# --------------------------------------------------------------------------------------------- synthetic calibration
def simulate_panel(n_treated=35, n_controls=70, days=250, share=0.0, seed=0, vol_confound=True):
    """Synthetic minute paths for both windows. Every stock has ordinary trend following with a stock-specific response
    to the day displacement (same in both windows), autocorrelated flow (order splitting, stronger near the close for all
    stocks), price impact and noise. Treated stocks have disclosed intensity lambda (lognormal); a fraction `share` of
    their rebalancing, lambda * ADV * R, is executed in continuous trading spread evenly over the close window. With
    vol_confound, high-lambda stocks are also more volatile and have stronger ordinary feedback at all times."""
    rng = np.random.default_rng(seed)
    n = n_treated + n_controls
    lam = np.r_[np.exp(rng.normal(np.log(0.15), 1.0, n_treated)), np.zeros(n_controls)]
    vol = 6.0 * (1 + (np.log1p(10 * lam) if vol_confound else 0)) * np.exp(rng.normal(0, 0.2, n))   # bp per minute
    kappa = np.exp(rng.normal(np.log(3.0), 0.3, n))                                                 # bp per unit flow
    phi0 = 1e-4 * (1 + (np.log1p(lam) if vol_confound else 0)) * np.exp(rng.normal(0, 0.3, n))      # ordinary feedback
    phi0 = np.minimum(phi0, 0.4 * 0.002 * (1 - 0.45) / kappa)        # keep every stock's own loop stable (margin > 0)
    units, panels = {}, {}
    for i in range(n):
        sym = f"S{i:03d}"
        units[sym] = {"role": "treated" if i < n_treated else "control", "lambda": float(lam[i]), "Lambda": float(lam[i] * 1e9),
                      "ADV": 1e9, "Lambda_bull": float(lam[i] * 1e9), "Lambda_bear": 0.0}
        mv = 1e9 / 390                                                                   # minute dollar volume = ADV / 390
        logp = np.log(100.0) * 1e4 + rng.normal(0, 60, days)                               # open after an overnight gap
        base = np.log(100.0) * 1e4
        f_prev = np.zeros(days)
        keep = {}
        for m in range(390):
            x = logp - base
            close_win = m >= WINDOWS["close"][0]
            reb = share * lam[i] * 390 * x * 1e-4 / WLEN["close"] if close_win else 0.0
            f = (0.45 if close_win else 0.3) * f_prev + phi0[i] * x + reb + 0.8 * rng.normal(size=days)
            logp = logp + kappa[i] * f - 0.002 * x + vol[i] * rng.normal(size=days)
            f_prev = f
            if WINDOWS["control"][0] <= m < WINDOWS["control"][1] or close_win:
                keep[m] = (np.exp(logp / 1e4), f * mv, mv * np.exp(rng.normal(0, 0.3, days)))
        auction = np.exp((logp + rng.normal(0, 3, days)) / 1e4)
        dates = np.array([f"D{d:03d}" for d in range(days)])
        df = pd.concat([pd.DataFrame({"date": dates, "window": "close" if m >= WINDOWS["close"][0] else "control", "minute": m, "px": v[0],
                                      "f": v[1], "v": v[2], "n": 1, "prev_close": 100.0, "close": auction})
                        for m, v in keep.items()], ignore_index=True)
        panels[sym] = df
    return panels, units


def calibrate(seeds_null=range(20), seeds_power=range(10), shares=(0.1, 0.25, 0.5), days=250, n_perm=2000):
    """Rejection rates of the two primaries under the null (no rebalancing in continuous trading, but volatility and
    ordinary feedback correlated with lambda, and stronger order splitting near the close) and under power alternatives."""
    global N_PERM
    old, N_PERM = N_PERM, n_perm
    out = {"null": [], "power": {str(s): [] for s in shares}}
    try:
        for seed in seeds_null:
            pan, un = simulate_panel(days=days, share=0.0, seed=seed)
            res = evaluate({s: unit_stats(p, p["date"].unique()) for s, p in pan.items()}, un)
            out["null"].append({"seed": seed, "p1": res["primary_1"]["p"], "p2": res["primary_2"]["p"],
                                "pass1": res["primary_1"]["passed_holm"], "pass2": res["primary_2"]["passed_holm"]})
        for sh in shares:
            for seed in seeds_power:
                pan, un = simulate_panel(days=days, share=sh, seed=1000 + seed)
                res = evaluate({s: unit_stats(p, p["date"].unique()) for s, p in pan.items()}, un)
                out["power"][str(sh)].append({"seed": 1000 + seed, "p1": res["primary_1"]["p"], "p2": res["primary_2"]["p"],
                                              "pass1": res["primary_1"]["passed_holm"], "pass2": res["primary_2"]["passed_holm"],
                                              "S1_median_share": res["secondary"]["S1_visible_share_of_disclosed_rebalancing"]["median"]})
    finally:
        N_PERM = old
    return out
