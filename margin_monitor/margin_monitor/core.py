"""Certify the stability margin of a market from public prices and anonymous signed order flow.

The market is read as a closed loop: order flow moves the price, and traders' flow responds to the price's displacement
from its recent level. In the linear model of the thesis "From Human Markets to Machine Markets" (Niroula, 2026),

    r_k = c  + kappa * f_k + beta * x_{k-1} + e_k          (price equation)
    f_k = c' + sum_{m=1..L} k_m * x_{k-m} + w_k            (flow equation, the traders' aggregate response)

with r the bar return, f the signed flow, x = p - EMA(p) the displacement. The stability margin is

    M = -beta - kappa * sum_m k_m   ( = 1 - a - kappa * Phi )

reversion (-beta) minus feedback (kappa * Phi). M > 0: shocks die out; M <= 0: the loop amplifies them. The margin
depends on the traders only through their total feedback, so it can be certified without identifying anyone, provided
their memory is bounded (here: L lags of bars); feedback with longer memory is invisible to any finite record.

Everything here is ordinary least squares on sufficient statistics with block-bootstrap intervals; no traders are
identified and no account data are needed.
"""
from dataclasses import dataclass, asdict

import numpy as np
import pandas as pd

__all__ = ["bars_from_trades", "bars_from_klines", "add_displacement", "Certificate", "certify", "rolling_margin",
           "warnings", "throttle"]


# ------------------------------------------------------------------------------------------------------------- bars
def _times(col):
    """Timestamps from epoch milliseconds or anything pandas parses, as UTC."""
    if pd.api.types.is_numeric_dtype(col):
        return pd.to_datetime(col, unit="ms", utc=True)
    return pd.to_datetime(col, utc=True)


def bars_from_trades(trades, freq="5min", time="time", price="price", size="size", side="side", notional=True):
    """Bars from trades. `side` is +1/-1, or 'B'/'S' (also 'A' for sell), the aggressor's side. Returns a DataFrame
    indexed by bar end with columns p (log price in basis points at the last trade), f (signed taker flow; notional
    if `notional`) and n (trades). Bars without trades carry the last price forward and zero flow."""
    t = trades.copy()
    ts = _times(t[time])
    sgn = t[side]
    if not pd.api.types.is_numeric_dtype(sgn):
        sgn = sgn.map(lambda s: 1.0 if str(s).upper().startswith("B") else -1.0)
    q = t[size].astype(float) * (t[price].astype(float) if notional else 1.0)
    df = pd.DataFrame({"px": t[price].astype(float).to_numpy(), "f": (sgn.astype(float) * q).to_numpy()}, index=ts).sort_index()
    g = df.resample(freq, label="right", closed="left")
    out = pd.DataFrame({"px": g["px"].last(), "f": g["f"].sum(), "n": g["f"].count()})
    out["px"] = out["px"].ffill()
    out = out.dropna(subset=["px"])
    out["p"] = np.log(out["px"]) * 1e4
    return out[["p", "f", "n"]]


def bars_from_klines(klines, time="open_time", close="close", volume="quote_volume", taker_buy="taker_buy_quote_volume",
                     freq="5min"):
    """Bars from candles that report taker-buy volume (for example Binance klines): signed flow = 2*taker_buy - volume."""
    k = klines.copy()
    ts = _times(k[time])
    df = pd.DataFrame({"px": k[close].astype(float).to_numpy(),
                       "f": (2 * k[taker_buy].astype(float) - k[volume].astype(float)).to_numpy()}, index=ts).sort_index()
    g = df.resample(freq, label="right", closed="left")
    out = pd.DataFrame({"px": g["px"].last(), "f": g["f"].sum(), "n": g["f"].count()}).dropna(subset=["px"])
    out["p"] = np.log(out["px"]) * 1e4
    return out[["p", "f", "n"]]


def add_displacement(bars, span=12, max_gap=None):
    """Adds r (return) and x (displacement p - EMA_span(p)); the EMA restarts after a gap in the bar index larger than
    `max_gap` (default: twice the median bar spacing), and its first `span` bars are left undefined."""
    b = bars.copy().sort_index()
    dt = b.index.to_series().diff()
    max_gap = max_gap or 2 * dt.median()
    seg = (dt > max_gap).cumsum()
    b["r"] = b["p"].diff().where(dt <= max_gap)
    x = pd.Series(np.nan, index=b.index)
    for _, part in b.groupby(seg):
        xs = part["p"] - part["p"].ewm(span=span, adjust=False).mean()
        xs.iloc[:span] = np.nan
        x.loc[part.index] = xs
    b["x"] = x
    b["seg"] = seg
    return b


# ------------------------------------------------------------------------------------------------------------- estimation
def _design(b, lags):
    x = b["x"].to_numpy(); r = b["r"].to_numpy(); f = b["f"].to_numpy(float)
    seg = b["seg"].to_numpy()
    lag = lambda z, m: np.r_[np.full(m, np.nan), z[:-m]]
    same = lambda m: np.r_[np.full(m, False), seg[m:] == seg[:-m]]
    xl = [np.where(same(m), lag(x, m), np.nan) for m in range(1, lags + 1)]
    one = np.ones(len(b))
    Xp, yp = np.column_stack([one, f, xl[0]]), r
    Xk, yk = np.column_stack([one] + xl), f
    return Xp, yp, Xk, yk


def _blockstats(X, y, block):
    ok = np.all(np.isfinite(X), 1) & np.isfinite(y)
    ids, inv = np.unique(block[ok], return_inverse=True)
    XX = np.zeros((len(ids), X.shape[1], X.shape[1])); Xy = np.zeros((len(ids), X.shape[1]))
    np.add.at(XX, inv, np.einsum("ti,tj->tij", X[ok], X[ok])); np.add.at(Xy, inv, X[ok] * y[ok][:, None])
    return ids, XX, Xy


def _solve(A, b):
    try:
        return np.linalg.solve(A, b)
    except np.linalg.LinAlgError:
        return np.full(b.shape, np.nan)


@dataclass
class Certificate:
    margin: float                 # M = reversion - feedback
    ci: tuple                     # block-bootstrap interval for M
    reversion: float              # -beta
    feedback: float               # kappa * Phi
    kappa: float
    phi: float
    decided: bool                 # interval excludes zero
    sign: str                     # "safe", "unsafe" or "undecided"
    n_bars: int
    n_blocks: int

    def to_dict(self):
        return asdict(self)


def certify(bars, lags=12, block="1D", n_boot=200, level=0.95, seed=0, span=12):
    """Certify the margin on all bars, with an interval from a bootstrap over blocks of time (default: days).
    `bars` has columns p and f (see bars_from_trades / bars_from_klines), or already r and x."""
    b = bars if {"r", "x", "seg"} <= set(bars.columns) else add_displacement(bars, span=span)
    Xp, yp, Xk, yk = _design(b, lags)
    blk = b.index.floor(block).asi8
    ip, Ap, bp = _blockstats(Xp, yp, blk); ik, Ak, bk = _blockstats(Xk, yk, blk)
    common = np.intersect1d(ip, ik)
    Ap, bp = Ap[np.isin(ip, common)], bp[np.isin(ip, common)]; Ak, bk = Ak[np.isin(ik, common)], bk[np.isin(ik, common)]
    n = len(common)
    if n == 0:
        raise ValueError("no complete rows: too few bars or too many gaps")

    def margin(w):
        cp = _solve(np.tensordot(w, Ap, 1), np.tensordot(w, bp, 1)); ck = _solve(np.tensordot(w, Ak, 1), np.tensordot(w, bk, 1))
        kap, beta, phi = cp[1], cp[2], ck[1:].sum()
        return -beta - kap * phi, -beta, kap * phi, kap, phi
    M, rev, fb, kap, phi = margin(np.ones(n))
    rng = np.random.default_rng(seed)
    boots = np.array([margin(np.bincount(rng.integers(0, n, n), minlength=n).astype(float))[0] for _ in range(n_boot)])
    boots = boots[np.isfinite(boots)]
    a = (1 - level) / 2
    lo, hi = (np.quantile(boots, [a, 1 - a]) if len(boots) > 20 else (np.nan, np.nan))
    sign = "safe" if lo > 0 else "unsafe" if hi < 0 else "undecided"
    return Certificate(float(M), (float(lo), float(hi)), float(rev), float(fb), float(kap), float(phi),
                       bool(lo > 0 or hi < 0), sign, int(np.isfinite(yp).sum()), n)


def rolling_margin(bars, window="24h", step="1h", lags=12, n_boot=100, level=0.95, seed=0, span=12, min_share=0.9):
    """The certificate on a rolling window: one row per step with the margin, its interval (bootstrap over the steps
    inside the window), reversion and feedback. A window is used only if at least `min_share` of its bars are complete."""
    b = bars if {"r", "x", "seg"} <= set(bars.columns) else add_displacement(bars, span=span)
    Xp, yp, Xk, yk = _design(b, lags)
    blk = b.index.floor(step).asi8
    ip, Ap, bp = _blockstats(Xp, yp, blk); ik, Ak, bk = _blockstats(Xk, yk, blk)
    steps = pd.date_range(b.index.min().floor(step), b.index.max().ceil(step), freq=step, tz=b.index.tz)
    pos = {v: i for i, v in enumerate(steps.asi8)}
    S = len(steps); P = Ap.shape[1]; K = Ak.shape[1]
    SA = np.zeros((S, P, P)); Sb = np.zeros((S, P)); KA = np.zeros((S, K, K)); Kb = np.zeros((S, K))
    for i, v in enumerate(ip):
        SA[pos[v]], Sb[pos[v]] = Ap[i], bp[i]
    for i, v in enumerate(ik):
        KA[pos[v]], Kb[pos[v]] = Ak[i], bk[i]
    cnt = np.zeros(S)
    for v, c in zip(*np.unique(blk[np.all(np.isfinite(Xk), 1) & np.isfinite(yk)], return_counts=True)):
        cnt[pos[v]] = c
    per_step = pd.Timedelta(step) / b.index.to_series().diff().median()
    w = int(pd.Timedelta(window) / pd.Timedelta(step))
    rng = np.random.default_rng(seed); a = (1 - level) / 2
    rows = []
    for e in range(w, S + 1):
        sl = slice(e - w, e)
        if cnt[sl].sum() < min_share * w * per_step:
            continue

        def margin(wt):
            cp = _solve(np.tensordot(wt, SA[sl], 1), np.tensordot(wt, Sb[sl], 1))
            ck = _solve(np.tensordot(wt, KA[sl], 1), np.tensordot(wt, Kb[sl], 1))
            return -cp[2] - cp[1] * ck[1:].sum(), -cp[2], cp[1] * ck[1:].sum()
        M, rev, fb = margin(np.ones(w))
        bs = np.array([margin(np.bincount(rng.integers(0, w, w), minlength=w).astype(float))[0] for _ in range(n_boot)]) if n_boot else np.array([])
        bs = bs[np.isfinite(bs)]
        lo, hi = (np.quantile(bs, [a, 1 - a]) if len(bs) > 20 else (np.nan, np.nan))
        rows.append({"time": steps[e - 1] + pd.Timedelta(step), "margin": M, "lo": lo, "hi": hi, "reversion": rev, "feedback": fb})
    return pd.DataFrame(rows).set_index("time") if rows else pd.DataFrame(columns=["margin", "lo", "hi", "reversion", "feedback"])


# ------------------------------------------------------------------------------------------------------------- decisions
def warnings(rolling, buffer=0.1, trend_steps=5, horizon=10):
    """Three warning rules on a rolling certificate (the rules of the thesis's Test B1):
    lost       the interval's lower end is at or below zero;
    buffer     the lower end is at or below `buffer`;
    t2z        time to zero: the margin is falling over `trend_steps` steps and margin / (-slope) < `horizon` steps.
    In simulation the trend rule (t2z) warned ahead of instability without false alarms; the level alone did not."""
    r = rolling.copy()
    r["lost"] = r["lo"] <= 0
    r["buffer"] = r["lo"] <= buffer
    slope = (r["margin"] - r["margin"].shift(trend_steps)) / trend_steps
    r["t2z"] = (slope < 0) & (r["margin"] / (-slope) < horizon)
    return r


def throttle(margin_lo, m_min=0.02, m_max=0.10):
    """A continuous admission rule: the share of algorithmic flow to admit given a lower bound on the margin; 0 at or
    below the buffer m_min, 1 above m_max, linear between. A continuous rule with a buffer keeps every strategy profile
    of the agents above the buffer and has equilibria; a rule that switches at a threshold can leave the agents' game
    without one (thesis, Proposition prop:throttle and Remark rem:strategic_counterexample)."""
    return float(np.clip((margin_lo - m_min) / (m_max - m_min), 0.0, 1.0))
