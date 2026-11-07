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
    fin = np.isfinite(u)
    # Amendment A1: an origin needs finite flows at t-1, t, t+1 (a no-op for Foreign; needed for classes that a
    # T86 schema era does not report).
    ok = usable[1:T - 1] & fin[0:T - 2] & fin[1:T - 1] & fin[2:T]
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

# Amendment A1 (7 November 2026, before any statistic was computed). TWSE's T86 report has three schema eras in the
# registered sample (census of every stored response, schema_census.json):
#   E1 2013-01-02 .. 2014-11-28: 外資買賣超股數, 投信買賣超股數, 自營商買賣超股數 (no own/hedging split)
#   E2 2014-12-01 .. 2017-12-15: as E1 plus 自營商買賣超股數(自行買賣) and 自營商買賣超股數(避險)
#   E3 2017-12-18 ..           : 外陸資買賣超股數(不含外資自營商) and 外資自營商買賣超股數 replace 外資買賣超股數
# Each series is read from the first name in its list that the day's schema contains. Foreign is the reported foreign
# total in E1-E2 and the sum of its two parts in E3 (spec: "Foreign (including foreign dealers)"). A series that a
# day's schema does not report is NaN for every stock that day (never zero). An unknown schema stops the run.
T86_FIELDS = {
    "foreign_ex": ["外陸資買賣超股數(不含外資自營商)", "外資買賣超股數"],
    "foreign_dealer": ["外資自營商買賣超股數", None],     # None: contained in the E1-E2 foreign total, read as 0
    "trust": ["投信買賣超股數"],
    "dealer_total": ["自營商買賣超股數"],
    "dealer_own": ["自營商買賣超股數(自行買賣)"],
    "dealer_hedge": ["自營商買賣超股數(避險)"],
    "total3": ["三大法人買賣超股數"],
}
REQUIRED = ("foreign_ex", "trust", "dealer_total")
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


def t86_positions(fields):
    """Column index per series for one schema, None if the series is contained elsewhere (read as 0), -1 if absent."""
    pos = {}
    for k, names in T86_FIELDS.items():
        hit = next((n for n in names if n is not None and n in fields), "absent")
        if hit == "absent" and None in names and any(n in fields for n in T86_FIELDS["foreign_ex"][1:]):
            pos[k] = None
        else:
            pos[k] = fields.index(hit) if hit != "absent" else -1
    for k in REQUIRED:
        if pos[k] is None or pos[k] < 0:
            raise ValueError(f"unknown T86 schema: required series {k} not found in {fields}")
    return pos


def parse_t86(j):
    """Returns (records, unavailable): records[code][series] and the set of series this day's schema lacks."""
    pos = t86_positions(j["fields"])
    unavailable = {k for k, i in pos.items() if i is not None and i < 0}
    out = {}
    for row in j.get("data", []):
        code = row[0].strip()
        if len(code) == 4 and code.isdigit():
            out[code] = {k: (0.0 if i is None else (math.nan if i < 0 else _num(row[i]))) for k, i in pos.items()}
    return out, unavailable


def t86_diagnostics(day_files):
    """Flow-only accounting checks per schema era (no prices, no forecasts). Shares of stock-days on which the
    three-institution total equals the sum of the parts, with and without the foreign dealers, and on which the dealer
    total equals own + hedging; and the foreign dealers' share of absolute foreign net flow."""
    eras = {}
    for d, t86, _ in day_files:
        key = tuple(t86["fields"])
        e = eras.setdefault(key, {"first": d, "last": d, "days": 0, "rows": 0, "total_with_fd": 0, "total_without_fd": 0,
                                  "dealer_rows": 0, "dealer_sum_ok": 0, "abs_fd": 0.0, "abs_foreign": 0.0})
        e["last"] = d; e["days"] += 1
        rec, unavail = parse_t86(t86)
        for r in rec.values():
            vals = [r["foreign_ex"], r["foreign_dealer"], r["trust"], r["dealer_total"], r["total3"]]
            if not all(np.isfinite(v) for v in vals):
                continue
            e["rows"] += 1
            e["total_with_fd"] += abs(r["total3"] - (r["foreign_ex"] + r["foreign_dealer"] + r["trust"] + r["dealer_total"])) < 0.5
            e["total_without_fd"] += abs(r["total3"] - (r["foreign_ex"] + r["trust"] + r["dealer_total"])) < 0.5
            if np.isfinite(r["dealer_own"]) and np.isfinite(r["dealer_hedge"]):
                e["dealer_rows"] += 1
                e["dealer_sum_ok"] += abs(r["dealer_total"] - r["dealer_own"] - r["dealer_hedge"]) < 0.5
            e["abs_fd"] += abs(r["foreign_dealer"]); e["abs_foreign"] += abs(r["foreign_ex"] + r["foreign_dealer"])
    out = []
    for key, e in eras.items():
        n = max(e["rows"], 1)
        out.append({"first": e["first"], "last": e["last"], "days": e["days"], "rows": e["rows"],
                    "share_total_eq_parts_with_foreign_dealers": e["total_with_fd"] / n,
                    "share_total_eq_parts_without_foreign_dealers": e["total_without_fd"] / n,
                    "share_dealer_total_eq_own_plus_hedge": (e["dealer_sum_ok"] / e["dealer_rows"]) if e["dealer_rows"] else None,
                    "foreign_dealer_share_of_abs_foreign_flow": e["abs_fd"] / e["abs_foreign"] if e["abs_foreign"] else None,
                    "fields": list(key)})
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
        fl, unavail = parse_t86(t86)
        q, idx = parse_mi_index(mi)
        parsed.append((d, (fl, unavail), q, idx))
        codes |= set(q)
    codes = sorted(codes)
    ci = {c: i for i, c in enumerate(codes)}
    N, T = len(codes), len(parsed)
    nan = lambda: np.full((N, T), np.nan)
    vol, value, close = nan(), nan(), nan()
    event = np.zeros((N, T), bool)
    flows = {k: nan() for k in T86_FIELDS}
    index = np.full(T, np.nan)
    for t, (d, (fl, unavail), q, idx) in enumerate(parsed):
        index[t] = idx
        for c, rec in q.items():
            i = ci[c]
            vol[i, t], value[i, t], close[i, t], event[i, t] = rec["vol"], rec["value"], rec["close"], rec["event"]
            if rec["vol"] and rec["vol"] > 0:
                f = fl.get(c)
                for k in T86_FIELDS:
                    # absent from the day's report = no institutional trade (0); a series the schema lacks = NaN
                    flows[k][i, t] = math.nan if k in unavail else (0.0 if f is None else f[k])
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
        "DealerTotal": F["dealer_total"],   # amendment A2: the "hedging included in the dealer class" sensitivity
    }
    # Residual = minus all reported institutional flow. The dealer total replaces own + hedging, which it equals
    # wherever the split is reported (checked by t86_diagnostics), and exists in every schema era.
    out["Residual"] = -(out["Foreign"] + out["Trust"] + F["dealer_total"])
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


# ----------------------------------------------------------------------------------------------------------------
# 4. Pre-specified diagnostics and secondary outcomes (amendment A2, P1T_amendment_A2.md)
#    Nothing above this block is changed by A2 except the extra DealerTotal class. The primary statistic is
#    computed only by run_period.
# ----------------------------------------------------------------------------------------------------------------

DIAG_B = 1999


def panel_L(prep, fit_mask, eval_mask, cls="Foreign", x=None, usable=None, min_share=0.95):
    """Stocks x dates loss-gain matrix, as in run_period, with optional replacement basis x and usable mask."""
    X = prep["x"] if x is None else x
    US = prep["usable"] if usable is None else usable
    rows = []
    for i in prep["U"]:
        if US[i][eval_mask].mean() < min_share:
            continue
        ell, _ = stock_losses(prep["u"][cls][i], X[i], prep["limit"][i], US[i], fit_mask, eval_mask)
        if np.isfinite(ell).any():
            rows.append(ell)
    return np.vstack(rows) if rows else np.zeros((0, len(eval_mask)))


def fast_stationary_indices(n, mean_block, rng):
    """Vectorized stationary-bootstrap indices (same law as stationary_indices, different random stream)."""
    restart = rng.random(n) < 1.0 / mean_block
    restart[0] = True
    starts = rng.integers(n, size=n)
    pos = np.arange(n)
    last = np.maximum.accumulate(np.where(restart, pos, 0))
    return (starts[last] + (pos - last)) % n


def bootstrap_D_fast(L, mean_block=20, B=DIAG_B, seed=SEED):
    cols = np.where(np.isfinite(L).any(axis=0))[0]
    Lc = L[:, cols]; rng = np.random.default_rng(seed); n = Lc.shape[1]
    S = np.nan_to_num(Lc); C = np.isfinite(Lc).astype(float)
    out = np.empty(B)
    for b in range(B):
        idx = fast_stationary_indices(n, mean_block, rng)
        num = S[:, idx].sum(1); cnt = C[:, idx].sum(1)
        out[b] = (num[cnt > 0] / cnt[cnt > 0]).mean()
    return out


def summarize_L(L, mean_block=20, B=DIAG_B, seed=SEED):
    if L.shape[0] == 0 or not np.isfinite(L).any():
        return {"D": None, "verdict": "not computable", "n_stocks": int(L.shape[0])}
    D, per = panel_D(L)
    out = decide(D, bootstrap_D_fast(L, mean_block=mean_block, B=B, seed=seed))
    out.update({"n_stocks": int(L.shape[0]), "share_stocks_positive": float((per > 0).mean()), "B": B,
                "mean_block": mean_block})
    return out


def residual_basis(prep, fit_mask, classes=("Foreign", "Trust", "DealerOwn", "Residual", "Hedge")):
    """Spec 7.1. Per stock, OLS of x_t on a constant, x_{t-1} and the reported flows u_{c,t}, u_{c,t-1} of the four
    classes and of dealer hedging, fitted on fit-period days where all are finite; returns x_t minus the fitted value
    (NaN where a regressor is missing). Under the confound (prices reveal past flow) the residual carries no
    information about future flow; under feedback it keeps the price news that flows respond to."""
    x = prep["x"]; N, T = x.shape
    xr = np.full((N, T), np.nan)
    for i in prep["U"]:
        cols = [np.ones(T), np.r_[np.nan, x[i, :-1]]]
        for c in classes:
            u = prep["u"][c][i]
            cols += [u, np.r_[np.nan, u[:-1]]]
        Xm = np.column_stack(cols)
        ok = np.isfinite(Xm).all(1) & np.isfinite(x[i])
        fit = ok & fit_mask
        if fit.sum() < 50:
            continue
        b = np.linalg.lstsq(Xm[fit], x[i, fit], rcond=None)[0]
        xr[i, ok] = x[i, ok] - Xm[ok] @ b
    us = prep["usable"].copy()
    us[:, 1:] &= np.isfinite(xr[:, 1:]) & np.isfinite(xr[:, :-1])
    us[:, 0] = False
    return xr, us


def limit_free_usable(prep):
    """Spec 7.4: limit days and the following day dropped. An origin t is dropped if t-1, t or t+1 is a limit day or
    the day after one."""
    lim = prep["limit"].astype(bool)
    bad = lim.copy(); bad[:, 1:] |= lim[:, :-1]
    us = prep["usable"].copy()
    us[:, 1:-1] &= ~bad[:, :-2] & ~bad[:, 1:-1] & ~bad[:, 2:]
    return us


def aggregate_k(prep, k, fit_mask, eval_mask, cls="Foreign"):
    """Spec 7.4: k-day periods. Non-overlapping blocks of k trading days from the first date; flow = sum over the
    block, basis = x on the block's last day, limit = any limit day in the block. A block is valid if every day is a
    finite in u (missing or excluded days are NaN) and x is finite on the block's last day. A stock enters if at least
    80% of its evaluation blocks are usable. Fit and evaluation blocks are those whose last day is in the mask."""
    u_all = prep["u"][cls]; x = prep["x"]; lim = prep["limit"]
    N, T = x.shape; nb = T // k
    last = np.arange(nb) * k + (k - 1)
    fit_b, ev_b = fit_mask[last], eval_mask[last]
    rows = []
    for i in prep["U"]:
        ub = u_all[i, :nb * k].reshape(nb, k).sum(1)               # NaN if any day missing
        xb = x[i, last]
        lb = lim[i, :nb * k].reshape(nb, k).max(1)
        val = np.isfinite(ub) & np.isfinite(xb)
        usb = np.zeros(nb, bool)
        usb[1:-1] = val[:-2] & val[1:-1] & val[2:]
        if usb[ev_b].mean() < 0.80:   # a block is lost if any of its days is; threshold 80% of evaluation blocks
            continue
        ell, _ = stock_losses(ub, xb, lb, usb, fit_b, ev_b)
        if np.isfinite(ell).any():
            rows.append(ell)
    L = np.vstack(rows) if rows else np.zeros((0, nb))
    return L, max(2, int(round(20 / k)))


def iv_tagged(u, x, ok, hac_lag=None):
    """Proposition 6.1 tagged IV for one stock: u_t = c + r u_{t-1} + w x_t + e_t, instruments (1, x_{t-1}, x_t).
    ok[t] marks usable equations. Returns beta = (c, r, w), Newey-West HAC covariance, residuals and T."""
    t = np.where(ok)[0]
    t = t[t >= 1]
    if len(t) < 60:
        return None
    y = u[t]; X = np.column_stack([np.ones(len(t)), u[t - 1], x[t]]); Z = np.column_stack([np.ones(len(t)), x[t - 1], x[t]])
    ZX = Z.T @ X
    if abs(np.linalg.det(ZX)) < 1e-12:
        return None
    b = np.linalg.solve(ZX, Z.T @ y)
    e = y - X @ b
    n = len(t)
    L = hac_lag if hac_lag is not None else int(np.floor(4 * (n / 100) ** (2 / 9)))
    g = Z * e[:, None]
    S = g.T @ g
    for l in range(1, L + 1):
        G = g[l:].T @ g[:-l]
        S += (1 - l / (L + 1)) * (G + G.T)
    Ainv = np.linalg.inv(ZX)
    V = Ainv @ S @ Ainv.T
    return {"beta": b, "V": V, "resid": e, "T": n, "rows": t}


def _iv_ok(prep, i, cls, mask):
    u = prep["u"][cls][i]; x = prep["x"][i]
    ok = prep["usable"][i] & mask & np.isfinite(u)
    ok[1:] &= np.isfinite(u[:-1]) & np.isfinite(x[:-1])
    ok[0] = False
    return ok


def secondary_S2(prep, fit_mask, eval_mask, classes=("Foreign", "Trust", "DealerOwn")):
    """Spec 8, S2: tagged IV estimates (r_i, w_i) per class with HAC 95% intervals, in the fit and evaluation periods;
    for Foreign, the share of stocks whose evaluation-period r_F lies in its fit-period 95% interval."""
    out = {}
    for c in classes:
        rec = {"fit": [], "eval": []}
        inside = []
        for i in prep["U"]:
            r = {}
            for name, m in (("fit", fit_mask), ("eval", eval_mask)):
                est = iv_tagged(prep["u"][c][i], prep["x"][i], _iv_ok(prep, i, c, m))
                if est is not None:
                    se = np.sqrt(np.diag(est["V"]))
                    r[name] = (est["beta"][1], se[1], est["beta"][2], se[2])
                    rec[name].append(r[name])
            if c == "Foreign" and "fit" in r and "eval" in r:
                rf, sf = r["fit"][0], r["fit"][1]
                inside.append(abs(r["eval"][0] - rf) <= 1.96 * sf)
        summ = {}
        for name in ("fit", "eval"):
            a = np.array(rec[name]) if rec[name] else np.zeros((0, 4))
            if len(a):
                summ[name] = {"n_stocks": int(len(a)), "r_median": float(np.median(a[:, 0])),
                              "r_iqr": [float(np.percentile(a[:, 0], 25)), float(np.percentile(a[:, 0], 75))],
                              "w_median": float(np.median(a[:, 2])),
                              "w_iqr": [float(np.percentile(a[:, 2], 25)), float(np.percentile(a[:, 2], 75))],
                              "share_w_positive_significant": float(np.mean(a[:, 2] - 1.96 * a[:, 3] > 0)),
                              "share_w_negative_significant": float(np.mean(a[:, 2] + 1.96 * a[:, 3] < 0))}
        if c == "Foreign":
            summ["share_eval_rF_in_fit_interval"] = float(np.mean(inside)) if inside else None
        out[c] = summ
    return out


def formula_se_r(beta, resid, x, ok_fit, T_eval, S=200):
    """Eq. (ivvar) evaluated with fit-period estimates: gamma_x from the fit-period basis (demeaned), r, w from the
    fit-period IV, sigma_f^2 = Var(e)/(1 + r^2). Returns the predicted standard error of r_hat for T_eval equations."""
    r, w = beta[1], beta[2]
    xs = x[ok_fit]; xs = xs - xs.mean(); n = len(xs)
    if n < 2 * S:
        S = n // 4
    gam = np.array([np.dot(xs[:n - s], xs[s:]) / n for s in range(S + 2)])
    A = lambda m: sum((r ** s) * gam[s + m] for s in range(S + 1 - m))
    Sig = np.array([[w * A(0), gam[1]], [w * A(1), gam[0]]])
    sf2 = np.var(resid) / (1 + r * r)
    G0 = np.array([[gam[0], gam[1]], [gam[1], gam[0]]])
    G1 = np.array([[gam[1], gam[0]], [gam[2], gam[1]]])
    Om = sf2 * ((1 + r * r) * G0 - r * (G1 + G1.T))
    try:
        Si = np.linalg.inv(Sig)
    except np.linalg.LinAlgError:
        return None
    V = Si @ Om @ Si.T
    return float(np.sqrt(max(V[0, 0], 0) / T_eval))


def secondary_S3(prep, fit_mask, eval_mask, B=199, mean_block=20, seed=SEED):
    """Spec 8, S3: for each stock, the eq. (ivvar) prediction of the evaluation-period standard error of r_F from
    fit-period estimates, against a stationary block bootstrap standard error of r_F over evaluation equations.
    Outcome: the median ratio across stocks, with agreement if it lies in [0.67, 1.5]."""
    rng = np.random.default_rng(seed)
    ratios = []
    for i in prep["U"]:
        okf = _iv_ok(prep, i, "Foreign", fit_mask); oke = _iv_ok(prep, i, "Foreign", eval_mask)
        f = iv_tagged(prep["u"]["Foreign"][i], prep["x"][i], okf)
        e = iv_tagged(prep["u"]["Foreign"][i], prep["x"][i], oke)
        if f is None or e is None:
            continue
        pred = formula_se_r(f["beta"], f["resid"], prep["x"][i], okf, e["T"])
        if pred is None or not np.isfinite(pred) or pred <= 0:
            continue
        t = e["rows"]; u = prep["u"]["Foreign"][i]; x = prep["x"][i]
        y = u[t]; X = np.column_stack([np.ones(len(t)), u[t - 1], x[t]]); Z = np.column_stack([np.ones(len(t)), x[t - 1], x[t]])
        bs = []
        for _ in range(B):
            idx = fast_stationary_indices(len(t), mean_block, rng)
            ZX = Z[idx].T @ X[idx]
            if abs(np.linalg.det(ZX)) < 1e-12:
                continue
            bs.append(np.linalg.solve(ZX, Z[idx].T @ y[idx])[1])
        if len(bs) < B // 2:
            continue
        ratios.append(pred / float(np.std(bs)))
    ratios = np.array(ratios)
    if not len(ratios):
        return {"n_stocks": 0, "verdict": "not computable"}
    med = float(np.median(ratios))
    return {"n_stocks": int(len(ratios)), "median_ratio_formula_to_bootstrap": med,
            "iqr_ratio": [float(np.percentile(ratios, 25)), float(np.percentile(ratios, 75))],
            "share_stocks_in_range": float(np.mean((ratios >= 0.67) & (ratios <= 1.5))),
            "agreement": bool(0.67 <= med <= 1.5), "B_per_stock": B}


def holm(pvals):
    """Holm step-down adjusted p-values for a dict name -> p."""
    items = sorted(pvals.items(), key=lambda kv: kv[1]); m = len(items); out = {}; run = 0.0
    for j, (k, p) in enumerate(items):
        run = max(run, min(1.0, (m - j) * p)); out[k] = run
    return out


def diagnostics(prep, dates, fit_mask, eval_mask, B=DIAG_B, seed=SEED):
    """All pre-specified diagnostics (spec 7) and secondary outcomes (spec 8) for one period. dates: 'YYYYMMDD'."""
    dates = np.array(dates)
    res = {"B": B}
    # 7.1 reverse-causality check
    xr, usr = residual_basis(prep, fit_mask)
    res["reverse_causality"] = summarize_L(panel_L(prep, fit_mask, eval_mask, "Foreign", x=xr, usable=usr), B=B, seed=seed)
    # 7.2 per-stock share (with the primary L)
    L = panel_L(prep, fit_mask, eval_mask, "Foreign")
    per = np.nanmean(L, axis=1)
    res["per_stock"] = {"share_positive": float(np.mean(per > 0)), "median_d": float(np.median(per)),
                        "quartiles_d": [float(np.percentile(per, 25)), float(np.percentile(per, 75))]}
    # 7.3 stability by calendar year, and Feb-Jun 2020 separately
    years = sorted({d[:4] for d in dates[eval_mask]})
    subs = {y: np.array([d[:4] == y for d in dates]) & eval_mask for y in years}
    subs["2020-02_to_2020-06"] = np.array(["20200201" <= d <= "20200630" for d in dates]) & eval_mask
    stab = {}
    for name, m in subs.items():
        if m.sum() < 20:
            continue
        Ls = np.where(m[None, :], L, np.nan)
        keep = np.isfinite(Ls).sum(1) >= 10
        stab[name] = summarize_L(Ls[keep], B=B, seed=seed)
    res["stability"] = stab
    # 7.4 sensitivity
    sens = {}
    sens["hedging_in_dealer_class"] = summarize_L(panel_L(prep, fit_mask, eval_mask, "DealerTotal"), B=B, seed=seed)
    sens["net_value_or_market_cap_scaling"] = {"verdict": "not computable",
                                               "reason": "shares outstanding are not in the registered sources"}
    sens["limit_days_dropped"] = summarize_L(panel_L(prep, fit_mask, eval_mask, "Foreign", usable=limit_free_usable(prep)), B=B, seed=seed)
    for k in (2, 5):
        Lk, mb = aggregate_k(prep, k, fit_mask, eval_mask)
        sens[f"{k}_day_periods"] = summarize_L(Lk, mean_block=mb, B=B, seed=seed)
    res["sensitivity"] = sens
    # 8 secondary outcomes
    S1 = {}
    for c in ("Trust", "DealerOwn"):
        Lc = panel_L(prep, fit_mask, eval_mask, c)
        S1[c] = run_period(prep, fit_mask, eval_mask, c) if Lc.shape[0] else {"D": None, "verdict": "not computable",
                                                                              "p_one_sided": 1.0, "n_stocks": 0}
    pv = {c: S1[c]["p_one_sided"] for c in S1}
    res["S1"] = {"by_class": S1, "holm_adjusted_p": holm(pv)}
    res["S2"] = secondary_S2(prep, fit_mask, eval_mask)
    res["S3"] = secondary_S3(prep, fit_mask, eval_mask)
    return res


if __name__ == "__main__":
    print("P1T executor. Use the Colab notebook or validate_executor.py.")
