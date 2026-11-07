"""P1T executor: Taiwan tagged-flow forecast-gain test (registered spec P1T_taiwan_spec.md).

Layers
------
1. Core (pure numpy): per-stock forecast losses, the primary statistic D, and the stationary date bootstrap.
2. Data: parse stored TWSE T86 and MI_INDEX JSON responses into a panel, apply the universe and exclusion rules,
   and build u (class flows), x (market-reference basis) and the limit indicator.
3. Run: one period at a time ("validation" or "holdout"), writing a results JSON.

The executor never downloads. Downloads are done by the Colab notebook, which stores raw responses with SHA-256.
"""
from __future__ import annotations

import json
import math
import os
import re
from dataclasses import dataclass

import numpy as np

D_STAR = 0.0035
SEED = 20261107


# ----------------------------------------------------------------------------------------------------------------
# 1. Core
# ----------------------------------------------------------------------------------------------------------------

def _design(u, x, lim, rows, with_x):
    """Rows index the forecast origin t; target is u[t+1]."""
    cols = [np.ones(len(rows)), u[rows], u[rows - 1], lim[rows]]
    if with_x:
        cols += [x[rows], x[rows - 1]]
    return np.column_stack(cols)


def stock_losses(u, x, lim, usable, fit_mask, eval_mask):
    """Per-date loss differential for one stock.

    u, x, lim, usable: arrays over the full date axis. usable[t] means day t may serve as a forecast origin
    (t-1, t, t+1 valid and x_t, x_{t-1} defined). fit_mask / eval_mask select origins for fitting / evaluation.
    Returns (ell, var_fit) where ell[t] = (e0^2 - e1^2) / var_fit on evaluation origins and NaN elsewhere.
    """
    T = len(u)
    t_all = np.arange(1, T - 1)
    ok = usable[1:T - 1]
    fit = t_all[ok & fit_mask[1:T - 1]]
    ev = t_all[ok & eval_mask[1:T - 1]]
    ell = np.full(T, np.nan)
    if len(fit) < 50 or len(ev) < 50:
        return ell, np.nan
    y_fit = u[fit + 1]
    var_fit = float(np.var(y_fit))
    if not np.isfinite(var_fit) or var_fit <= 0:
        return ell, np.nan
    b0 = np.linalg.lstsq(_design(u, x, lim, fit, False), y_fit, rcond=None)[0]
    b1 = np.linalg.lstsq(_design(u, x, lim, fit, True), y_fit, rcond=None)[0]
    e0 = u[ev + 1] - _design(u, x, lim, ev, False) @ b0
    e1 = u[ev + 1] - _design(u, x, lim, ev, True) @ b1
    ell[ev] = (e0 ** 2 - e1 ** 2) / var_fit
    return ell, var_fit


def panel_D(L):
    """L: stocks x dates, NaN where not an evaluation origin. D = mean over stocks of each stock's mean loss gain."""
    per = np.nanmean(L, axis=1)
    per = per[np.isfinite(per)]
    return float(per.mean()), per


def stationary_indices(n, mean_block, rng):
    p = 1.0 / mean_block
    idx = np.empty(n, dtype=np.int64)
    idx[0] = rng.integers(n)
    for i in range(1, n):
        idx[i] = rng.integers(n) if rng.random() < p else (idx[i - 1] + 1) % n
    return idx


def bootstrap_D(L, mean_block=20, B=9999, seed=SEED):
    """Stationary bootstrap over dates, the same resampled dates for every stock."""
    cols = np.where(np.isfinite(L).any(axis=0))[0]
    Lc = L[:, cols]
    rng = np.random.default_rng(seed)
    n = Lc.shape[1]
    S = np.nan_to_num(Lc)
    C = np.isfinite(Lc).astype(float)
    out = np.empty(B)
    for b in range(B):
        idx = stationary_indices(n, mean_block, rng)
        num = S[:, idx].sum(1)
        cnt = C[:, idx].sum(1)
        per = num[cnt > 0] / cnt[cnt > 0]
        out[b] = per.mean()
    return out


def decide(D, boot):
    """Registered criteria. One-sided p for D > 0 from the bootstrap distribution centred at D."""
    lo, hi = np.percentile(boot, [2.5, 97.5])
    p = float(np.mean(boot - D >= D)) if D > 0 else 1.0
    if p < 0.05 and D > 0 and lo > 0:
        verdict = "supportive"
    elif hi < D_STAR:
        verdict = "inconsistent"
    else:
        verdict = "inconclusive"
    return {"D": D, "p_one_sided": p, "ci95": [float(lo), float(hi)], "D_star": D_STAR, "verdict": verdict}


# ----------------------------------------------------------------------------------------------------------------
# 2. Data
# ----------------------------------------------------------------------------------------------------------------

T86_FIELDS = {
    "foreign_ex": "外陸資買賣超股數(不含外資自營商)",
    "foreign_dealer": "外資自營商買賣超股數",
    "trust": "投信買賣超股數",
    "dealer_own": "自營商買賣超股數(自行買賣)",
    "dealer_hedge": "自營商買賣超股數(避險)",
}
QUOTE_TITLE_SUFFIX = "權證、牛熊證、可展延牛熊證))"
INDEX_NAME = "發行量加權股價指數"


def _num(s):
    s = str(s).replace(",", "").strip()
    if s in ("", "--", "---", "X"):
        return math.nan
    try:
        return float(s)
    except ValueError:
        return math.nan


def parse_t86(j):
    f = j["fields"]
    pos = {k: f.index(v) for k, v in T86_FIELDS.items()}
    out = {}
    for row in j.get("data", []):
        code = row[0].strip()
        if len(code) == 4 and code.isdigit():
            out[code] = {k: _num(row[i]) for k, i in pos.items()}
    return out


def parse_mi_index(j):
    quotes, index = {}, math.nan
    for t in j.get("tables", []):
        title = t.get("title") or ""
        fields = t.get("fields") or []
        if title.endswith(QUOTE_TITLE_SUFFIX) and "證券代號" in fields:
            ic, iv, ival = fields.index("證券代號"), fields.index("成交股數"), fields.index("成交金額")
            icl, isg = fields.index("收盤價"), fields.index("漲跌(+/-)")
            for row in t.get("data", []):
                code = row[ic].strip()
                if len(code) == 4 and code.isdigit():
                    sign = re.sub(r"<[^>]+>", "", str(row[isg])).strip()
                    quotes[code] = {"vol": _num(row[iv]), "value": _num(row[ival]), "close": _num(row[icl]),
                                    "event": sign == "X"}
        if fields and t.get("data") and any(str(r[0]).strip() == INDEX_NAME for r in t["data"]):
            for r in t["data"]:
                if str(r[0]).strip() == INDEX_NAME:
                    index = _num(r[1])
    return quotes, index


def parse_twt49u(j):
    """Ex-rights / ex-dividend calculation table. Returns a set of (YYYYMMDD, code). Field names are matched by
    content because probe 2 returned no rows; unparsed tables are reported, not guessed."""
    out = set()
    f = j.get("fields") or []
    idate = next((i for i, x in enumerate(f) if "日期" in x), None)
    icode = next((i for i, x in enumerate(f) if "代號" in x), None)
    if idate is None or icode is None:
        return out
    for row in j.get("data", []):
        digits = re.sub(r"[^0-9]", "", str(row[idate]))
        if len(digits) == 7:
            digits = str(int(digits[:3]) + 1911) + digits[3:]
        code = str(row[icode]).strip()
        if len(digits) == 8 and len(code) == 4 and code.isdigit():
            out.add((digits, code))
    return out


@dataclass
class Panel:
    dates: list
    codes: list
    vol: np.ndarray       # stocks x dates
    value: np.ndarray
    close: np.ndarray
    event: np.ndarray     # bool
    flows: dict           # class -> stocks x dates
    index: np.ndarray     # dates


def build_panel(day_files, extra_events=None):
    """day_files: list of (date 'YYYYMMDD', t86_json, mi_json) in calendar order (trading days only).
    extra_events: optional set of (YYYYMMDD, code) from TWT49U, united with the X change-sign flag."""
    parsed = []
    codes = set()
    for d, t86, mi in day_files:
        fl = parse_t86(t86)
        q, idx = parse_mi_index(mi)
        parsed.append((d, fl, q, idx))
        codes |= set(q)
    codes = sorted(codes)
    ci = {c: i for i, c in enumerate(codes)}
    N, T = len(codes), len(parsed)
    nan = lambda: np.full((N, T), np.nan)
    vol, value, close = nan(), nan(), nan()
    event = np.zeros((N, T), bool)
    flows = {k: nan() for k in T86_FIELDS}
    index = np.full(T, np.nan)
    for t, (d, fl, q, idx) in enumerate(parsed):
        index[t] = idx
        for c, rec in q.items():
            i = ci[c]
            vol[i, t], value[i, t], close[i, t], event[i, t] = rec["vol"], rec["value"], rec["close"], rec["event"]
            if rec["vol"] and rec["vol"] > 0:
                f = fl.get(c)
                for k in T86_FIELDS:
                    flows[k][i, t] = 0.0 if f is None else f[k]
    x_only = int(event.sum())
    if extra_events:
        di = {p[0]: t for t, p in enumerate(parsed)}
        for d, c in extra_events:
            if d in di and c in ci:
                event[ci[c], di[d]] = True
    P = Panel([p[0] for p in parsed], codes, vol, value, close, event, flows, index)
    P.event_counts = {"x_flag": x_only, "union_with_twt49u": int(event.sum())}
    return P


def class_flows(P):
    F = P.flows
    out = {
        "Foreign": F["foreign_ex"] + F["foreign_dealer"],
        "Trust": F["trust"],
        "DealerOwn": F["dealer_own"],
        "Hedge": F["dealer_hedge"],
    }
    out["Residual"] = -(out["Foreign"] + out["Trust"] + out["DealerOwn"] + out["Hedge"])
    return out


def prepare(P, dev_mask, top_n=300, min_share=0.95, trail=60, post_listing=60):
    """Universe, flow scaling, beta, market-reference basis x, limit indicator and usable-origin masks."""
    N, T = P.close.shape
    traded = np.isfinite(P.vol) & (P.vol > 0) & np.isfinite(P.close)
    logc = np.log(P.close)
    ret = np.full((N, T), np.nan)
    ret[:, 1:] = logc[:, 1:] - logc[:, :-1]
    prev_close = np.full((N, T), np.nan)
    prev_close[:, 1:] = P.close[:, :-1]
    limit = np.abs(P.close - prev_close) >= 0.095 * prev_close
    limit &= np.isfinite(prev_close)
    ri = np.full(T, np.nan)
    ri[1:] = np.diff(np.log(P.index))
    excl = P.event.copy()
    excl[:, 1:] |= P.event[:, :-1]
    # first `post_listing` traded days of a stock that starts trading after the first date
    first = np.argmax(traded, axis=1)
    for i in range(N):
        if first[i] > 0:
            excl[i, first[i]:first[i] + post_listing] = True
    # universe on development days
    dev = dev_mask[None, :]
    usable_share = (traded & ~excl & dev).sum(1) / max(dev_mask.sum(), 1)
    turnover = np.where(dev & traded, P.value, np.nan)
    mean_turn = np.nanmean(turnover, axis=1)
    elig = np.where((usable_share >= min_share) & np.isfinite(mean_turn))[0]
    order = elig[np.lexsort((np.array(P.codes)[elig], -mean_turn[elig]))]
    U = order[:top_n]
    res = {"universe_codes": [P.codes[i] for i in U]}
    # beta on development days
    beta = np.full(N, np.nan)
    for i in U:
        m = dev_mask & traded[i] & ~excl[i] & ~limit[i] & np.isfinite(ret[i]) & np.isfinite(ri)
        if m.sum() > 100:
            X = ri[m]
            beta[i] = float(np.dot(X - X.mean(), ret[i, m] - ret[i, m].mean()) / np.dot(X - X.mean(), X - X.mean()))
    # adjusted log level: event-day return replaced by beta * index return; missing returns count as 0
    adj = np.where(P.event, beta[:, None] * ri[None, :], ret)
    adj = np.where(np.isfinite(adj), adj, 0.0)
    level = np.cumsum(adj, axis=1)
    logI = np.log(P.index)
    basis = level - beta[:, None] * (logI[None, :] - logI[0])
    x = np.full((N, T), np.nan)
    for t in range(trail, T):
        x[:, t] = basis[:, t] - basis[:, t - trail:t].mean(1)
    flows = class_flows(P)
    scale = np.nanmean(np.where(dev & traded, P.vol, np.nan), axis=1)
    u = {k: v / scale[:, None] for k, v in flows.items()}
    valid = traded & ~excl
    usable = np.zeros((N, T), bool)
    usable[:, 1:-1] = valid[:, :-2] & valid[:, 1:-1] & valid[:, 2:]
    usable[:, 1:-1] &= np.isfinite(x[:, 1:-1]) & np.isfinite(x[:, :-2])
    res.update({"U": U, "x": x, "u": u, "limit": limit.astype(float), "usable": usable, "beta": beta})
    return res


# ----------------------------------------------------------------------------------------------------------------
# 3. Run
# ----------------------------------------------------------------------------------------------------------------

def run_period(prep, fit_mask, eval_mask, cls="Foreign", min_share=0.95, B=9999, mean_block=20, seed=SEED):
    U = prep["U"]
    rows = []
    for i in U:
        if prep["usable"][i][eval_mask].mean() < min_share:
            continue
        ell, _ = stock_losses(prep["u"][cls][i], prep["x"][i], prep["limit"][i], prep["usable"][i], fit_mask, eval_mask)
        if np.isfinite(ell).any():
            rows.append(ell)
    L = np.vstack(rows)
    D, per = panel_D(L)
    boot = bootstrap_D(L, mean_block=mean_block, B=B, seed=seed)
    out = decide(D, boot)
    out.update({"class": cls, "n_stocks": int(L.shape[0]), "share_stocks_positive": float((per > 0).mean()),
                "mean_block": mean_block, "B": B})
    return out


if __name__ == "__main__":
    print("P1T executor. Use the Colab notebook or validate_executor.py.")
