"""P1KS development-window calibration (2015-2019 only): summary statistics for the power check.

Input: for each stock, a daily DataFrame with columns
    close   adjusted close,
    scale   flow scale (Naver source: trailing 60-day mean trading volume, in shares),
    fnet    foreign net purchases, in the same units as scale (Naver: foreignerPureBuyQuant, shares),
indexed by a DatetimeIndex. Prices may start 2014-09-01; every date must be before 2020-01-01.

Per stock and window (full 2015-2019, and halves split at 2017-07-01):
    x_t   log close minus its trailing 60-day mean, divided by the stock's s.d. of daily log returns (2015-2019),
    u_t   foreign net purchase / scale at t-1, winsorized at the window's 0.5% and 99.5% quantiles,
    tagged rule  u_t = alpha + r u_{t-1} + w x_{t-1} + e            (OLS),
    impact       x_t = const + sum_{j<=5} a_j x_{t-j} + kappa u_{t-1} + e   (OLS),
    c            kappa * w / (1 - r)   (foreign budget contribution; requires |r| < 0.99),
    S_hat        sum of coefficients of an AR(10) in x with constant (prices only).
Output: cross-stock summaries only (no stock-level values).
"""
import numpy as np
import pandas as pd

CUTOFF = pd.Timestamp('2020-01-01')
START = pd.Timestamp('2015-01-01')
SPLIT = pd.Timestamp('2017-07-01')
AR_LAGS = 10
IMPACT_LAGS = 5
MIN_DAYS = 200


def _ols(y, X):
    X = np.column_stack([np.ones(len(y)), X])
    beta, *_ = np.linalg.lstsq(X, y, rcond=None)
    return beta[1:]


def _lags(v, k):
    n = len(v)
    return np.column_stack([v[k - j:n - j] for j in range(1, k + 1)])


def prepare(df):
    df = df.sort_index()
    assert df.index.max() < CUTOFF, 'data after 2019 must not be read'
    lc = np.log(df['close'].astype(float))
    ret = lc.diff()
    sd = ret[ret.index >= START].std()
    x = (lc - lc.rolling(60).mean()) / sd
    u = df['fnet'].astype(float) / df['scale'].astype(float).shift(1)
    out = pd.DataFrame({'x': x, 'u': u}).replace([np.inf, -np.inf], np.nan)
    return out[out.index >= START].dropna()


def window_stats(d):
    if len(d) < MIN_DAYS:
        return None
    u = d['u'].to_numpy().copy()
    lo, hi = np.quantile(u, [0.005, 0.995])
    u = np.clip(u, lo, hi)
    x = d['x'].to_numpy()
    if np.std(u) == 0 or np.std(x) == 0:
        return None
    r, w = _ols(u[1:], np.column_stack([u[:-1], x[:-1]]))
    k = IMPACT_LAGS
    Xi = np.column_stack([_lags(x, k), u[k - 1:-1]])
    coef = _ols(x[k:], Xi)
    kappa = coef[-1]
    ar = _ols(x[AR_LAGS:], _lags(x, AR_LAGS))
    s_hat = float(np.sum(ar))
    c = float(kappa * w / (1 - r)) if abs(r) < 0.99 else np.nan
    return {'r': float(r), 'w': float(w), 'kappa': float(kappa), 'c': c, 'S': s_hat, 'n': int(len(d))}


def stock_stats(df):
    d = prepare(df)
    return {'full': window_stats(d), 'h1': window_stats(d[d.index < SPLIT]), 'h2': window_stats(d[d.index >= SPLIT])}


def _q(v):
    v = np.asarray([a for a in v if np.isfinite(a)])
    if len(v) == 0:
        return None
    qs = np.quantile(v, [0.05, 0.25, 0.5, 0.75, 0.95])
    return {'n': int(len(v)), 'mean': float(v.mean()), 'sd': float(v.std(ddof=1)) if len(v) > 1 else None,
            'q05': float(qs[0]), 'q25': float(qs[1]), 'median': float(qs[2]), 'q75': float(qs[3]), 'q95': float(qs[4])}


def summarize(results, groups):
    """results: ticker -> stock_stats output; groups: ticker -> 'large' or 'other'."""
    out = {'n_stocks_input': len(results)}
    for g in ('large', 'other', 'all'):
        tick = [t for t in results if g == 'all' or groups.get(t) == g]
        full = [results[t]['full'] for t in tick if results[t]['full']]
        both = [(results[t]['h1'], results[t]['h2']) for t in tick
                if results[t]['h1'] and results[t]['h2']
                and np.isfinite(results[t]['h1']['c']) and np.isfinite(results[t]['h2']['c'])]
        s = {'n_full': len(full), 'n_both_halves': len(both)}
        s['c_full'] = _q([f['c'] for f in full])
        s['r_full'] = _q([f['r'] for f in full])
        s['w_full'] = _q([f['w'] for f in full])
        s['kappa_full'] = _q([f['kappa'] for f in full])
        s['S_full'] = _q([f['S'] for f in full])
        s['days_full'] = _q([f['n'] for f in full])
        if len(both) > 5:
            c1 = np.array([a['c'] for a, _ in both]); c2 = np.array([b['c'] for _, b in both])
            S1 = np.array([a['S'] for a, _ in both]); S2 = np.array([b['S'] for _, b in both])
            dS, dc = S2 - S1, c2 - c1
            s['dS_placebo'] = _q(dS)
            s['dc_placebo'] = _q(dc)
            s['corr_dS_dc'] = float(np.corrcoef(dS, dc)[0, 1])
            s['corr_c_h1_h2'] = float(np.corrcoef(c1, c2)[0, 1])
            s['spearman_c_h1_h2'] = float(pd.Series(c1).rank().corr(pd.Series(c2).rank()))
            s['days_h1'] = _q([a['n'] for a, _ in both]); s['days_h2'] = _q([b['n'] for _, b in both])
        out[g] = s
    return out
