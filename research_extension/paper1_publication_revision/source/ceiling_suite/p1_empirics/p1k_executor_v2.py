"""P1K executor, design 2 (DRAFT, not approved, not registered). Downloads nothing.

Design 1 (p1k_executor.py) estimated 11 memories and 11 weights per stock-year and failed its simulation check:
no power, and one false 'supportive' (P1K_spec_DRAFT.md section 8). Design 2 changes three things.

  1. Pooled memories. Each investor class has one memory rate r_i, estimated on development years by pooling all
     stocks: a grid search for the r minimizing the pooled residuals of the stock-year regressions of u_t on
     (1, x_t, m_{t-1}(r)), where m_{t-1}(r) = sum_{j>=1} r^(j-1) x_{t-j}. Same-day reverse causality (flow moving
     the same day's price) biases only the x_t coefficient, so r is identified from the lagged part. Only the
     weights vary by stock-year, estimated with r_i held fixed (one parameter per class and stock-year).
  2. Outcome the kernel moves: autocorrelations of the pricing-error proxy x at lags 1, 2, 5, 10, 20.
  3. Stock baseline: every model includes the stock's own mean outcome over its other development years, so the
     kernel is credited only with predicting how a stock's dynamics differ from its own history.

Panel layout, x, u, the ridge fits, the bootstrap and the decision rule are those of design 1 (imported).
"""
from __future__ import annotations

import numpy as np
import pandas as pd
from scipy import stats
from scipy.signal import lfilter

import p1k_executor as v1

SEED = v1.SEED
MIN_OBS = v1.MIN_OBS
KERNEL_M = v1.KERNEL_M
DEV_YEARS, HOLD_YEARS = v1.DEV_YEARS, v1.HOLD_YEARS
ACF_LAGS = [1, 2, 5, 10, 20]
prepare = v1.prepare


def _acf_x(x: np.ndarray) -> np.ndarray:
    a = v1._acf(x, max(ACF_LAGS))
    return a[[k - 1 for k in ACF_LAGS]]


R_GRID = np.round(np.arange(0.0, 0.991, 0.01), 2)


def _lagfilter(x: np.ndarray, r: float) -> np.ndarray:
    """m_{t-1}(r) = sum_{j>=1} r^(j-1) x_{t-j}, started at zero; NaN inputs count as zero."""
    acc = lfilter([1.0], [1.0, -r], np.nan_to_num(x))
    out = np.empty_like(acc); out[0] = 0.0; out[1:] = acc[:-1]
    return out


def _fit_r(u: np.ndarray, x: np.ndarray, r: float):
    """OLS of u_t on (1, x_t, m_{t-1}(r)) within one stock-year. Under the model u_t = r u_{t-1} + w x_t,
    u_t = w x_t + w r m_{t-1}(r) + start-up terms; same-day reverse causality biases only the x_t coefficient,
    so the memory is identified by the lagged part. Returns (SSE, coefficient on m) or None."""
    m = _lagfilter(x, r)
    ok = np.isfinite(u) & np.isfinite(x)
    ok[:20] = False                                          # drop the filter's start-up
    if ok.sum() < MIN_OBS:
        return None
    X = np.column_stack([np.ones(ok.sum()), x[ok], m[ok]])
    b, *_ = np.linalg.lstsq(X, u[ok], rcond=None)
    e = u[ok] - X @ b
    return float(e @ e), float(b[2])


def pooled_memories(prep: pd.DataFrame, years=DEV_YEARS) -> dict:
    """One memory rate per class from development years, pooled across stocks: the grid value of r minimizing the
    pooled sum of squared residuals of the stock-year regressions in _fit_r (each stock-year scaled by its flow
    variance, so that large stocks do not dominate)."""
    classes = [c[2:] for c in prep.columns if c.startswith("u:")]
    d = prep[prep["year"].isin(years)]
    out = {}
    sy = [(g["x"].to_numpy(), {c: g["u:" + c].to_numpy() for c in classes}) for _, g in d.groupby(["ticker", "year"], sort=False)]
    for c in classes:
        sse = np.zeros(len(R_GRID)); n_used = 0
        for x, us in sy:
            u = us[c]; v = np.nanvar(u)
            if not np.isfinite(v) or v <= 0:
                continue
            fits = [_fit_r(u, x, r) for r in R_GRID]
            if any(f is None for f in fits):
                continue
            sse += np.array([f[0] for f in fits]) / v; n_used += 1
        out[c] = float(R_GRID[int(np.argmin(sse))]) if n_used else np.nan
    return out


def stock_years(prep: pd.DataFrame, r_pooled: dict) -> pd.DataFrame:
    classes = [c for c in r_pooled if np.isfinite(r_pooled[c])]
    rows = []
    for (tk, yr), g in prep.groupby(["ticker", "year"], sort=False):
        g = g.sort_values("date")
        x = g["x"].to_numpy(); ret = g["ret"].to_numpy()
        ws = {}
        for c in classes:
            f = _fit_r(g["u:" + c].to_numpy(), x, r_pooled[c])
            # coefficient on m_{t-1}(r) is w r; with r = 0 the memory term is absent and w is not identified here
            ws[c] = (f[1] / r_pooled[c]) if (f is not None and r_pooled[c] > 0) else np.nan
        xx = x[np.isfinite(x)]; r_ok = ret[np.isfinite(ret)]
        if len(xx) < MIN_OBS or sum(np.isfinite(v) for v in ws.values()) < 2:
            continue
        w = np.array([ws[c] if np.isfinite(ws[c]) else 0.0 for c in classes])
        rr = np.array([r_pooled[c] for c in classes])
        tot = np.sum(np.abs(w))
        rows.append({"ticker": tk, "year": int(yr), "Y": _acf_x(xx), "vol": float(np.std(r_ok)),
                     "log_mcap": float(np.log(g["mcap"].astype(float).where(g["mcap"] > 0).mean())),
                     "kernel": np.array([np.sum(w * rr ** m) for m in range(KERNEL_M)]),
                     "comp": np.abs(w) / tot if tot > 0 else np.zeros_like(w), "w": w})
    sy = pd.DataFrame(rows)
    sy.attrs["classes"] = classes
    return sy


def _stock_baseline(sy: pd.DataFrame) -> np.ndarray:
    """Each stock-year's stock mean outcome over the stock's development years other than its own year."""
    Y = np.stack(sy["Y"].to_numpy()); out = np.full_like(Y, np.nan)
    dev = sy["year"].isin(DEV_YEARS).to_numpy()
    for tk, idx in sy.groupby("ticker").indices.items():
        idx = np.asarray(idx); d = idx[dev[idx]]
        for i in idx:
            use = d[d != i]
            if len(use):
                out[i] = Y[use].mean(0)
    return out


def evaluate(sy: pd.DataFrame, B: int = v1.B_DEFAULT, seed: int = SEED, e_frac: float = v1.E_FRAC) -> dict:
    sb = _stock_baseline(sy)
    keep = np.all(np.isfinite(sb), axis=1)
    sy = sy[keep].reset_index(drop=True); sb = sb[keep]
    # the stock baseline enters as an offset: every model predicts Y minus the stock's own development mean
    sy = sy.assign(Y=list(np.stack(sy["Y"].to_numpy()) - sb))
    r = v1.evaluate(sy.assign(r=[np.zeros(len(sy.attrs.get("classes", [])))] * len(sy),
                              r_valid=[np.zeros(len(sy.attrs.get("classes", [])), bool)] * len(sy),
                              mem_tagged=np.nan), B=B, seed=seed, e_frac=e_frac)
    for k in ("H1_kruskal_p", "H1_median_r_by_class", "H3_price_vs_tagged_memory"):
        r.pop(k, None)
    r["design"] = 2
    return r
