"""Core estimators for the October 2026 Binance tests (P1O). No data access here; pure functions on arrays."""
import numpy as np


def nw_cov(X, u, lags):
    """Newey-West (Bartlett) covariance of OLS coefficients."""
    n = len(u)
    XtX_inv = np.linalg.inv(X.T @ X)
    Xu = X * u[:, None]
    S = Xu.T @ Xu
    for L in range(1, lags + 1):
        w = 1 - L / (lags + 1)
        G = Xu[L:].T @ Xu[:-L]
        S += w * (G + G.T)
    return XtX_inv @ S @ XtX_inv


def lagmat(x, lags, start=1):
    """Columns x_{t-start}, ..., x_{t-start-lags+1}; rows with missing history are NaN."""
    n = len(x); out = np.full((n, lags), np.nan)
    for j in range(lags):
        s = start + j
        if s == 0:
            out[:, j] = x
        else:
            out[s:, j] = x[:-s]
    return out


def dm_test(e_restricted, e_full, lags=12):
    """One-sided Diebold-Mariano test that the full model has lower squared error. Returns (stat, p)."""
    from math import erf, sqrt
    d = e_restricted ** 2 - e_full ** 2
    d = d[np.isfinite(d)]
    n = len(d); dbar = d.mean(); dc = d - dbar
    v = dc @ dc / n
    for L in range(1, lags + 1):
        v += 2 * (1 - L / (lags + 1)) * (dc[L:] @ dc[:-L]) / n
    stat = dbar / np.sqrt(v / n) if v > 0 else 0.0
    p = 0.5 * (1 - erf(stat / sqrt(2)))
    return float(stat), float(p)


def feedback_oos(dy, r, train_mask, test_mask, p_own=6, p_ret=6, dm_lags=12):
    """Test N2. dy: change in log class position ratio; r: bar return (r_t ends at the snapshot time t).
    Restricted: dy_t on const + dy_{t-1..t-p_own}. Full: adds r_t, ..., r_{t-p_ret+1}.
    Fit on train rows, evaluate one-step squared errors on test rows."""
    Y = lagmat(dy, p_own, 1); Rr = lagmat(r, p_ret, 0)
    one = np.ones((len(dy), 1))
    Xr = np.hstack([one, Y]); Xf = np.hstack([one, Y, Rr])
    ok = np.isfinite(dy) & np.isfinite(Xf).all(axis=1)
    tr = ok & train_mask; te = ok & test_mask
    br = np.linalg.lstsq(Xr[tr], dy[tr], rcond=None)[0]
    bf = np.linalg.lstsq(Xf[tr], dy[tr], rcond=None)[0]
    er = dy[te] - Xr[te] @ br; ef = dy[te] - Xf[te] @ bf
    stat, p = dm_test(er, ef, dm_lags)
    sst = np.sum((dy[te] - dy[tr].mean()) ** 2)
    return {"n_train": int(tr.sum()), "n_test": int(te.sum()), "dm_stat": stat, "dm_p": p,
            "oos_r2_restricted": float(1 - er @ er / sst), "oos_r2_full": float(1 - ef @ ef / sst),
            "oos_r2_gain": float((er @ er - ef @ ef) / sst), "mse_ratio": float((ef @ ef) / (er @ er)),
            "cum_response_train": float(bf[1 + p_own:].sum())}


def combined_response(x, r, mask, lags=12, nw_lags=24):
    """Test N3. x: taker-flow imbalance over the bar ending at t; r: bar returns.
    x_t = c + sum_{m=1..lags} k_m r_{t-m}; returns Psi = sum k_m with a Newey-West 95% interval."""
    R = lagmat(r, lags, 1)
    X = np.hstack([np.ones((len(x), 1)), R])
    ok = mask & np.isfinite(x) & np.isfinite(X).all(axis=1)
    b = np.linalg.lstsq(X[ok], x[ok], rcond=None)[0]
    u = x[ok] - X[ok] @ b
    V = nw_cov(X[ok], u, nw_lags)
    g = np.r_[0.0, np.ones(lags)]
    psi = float(g @ b); se = float(np.sqrt(g @ V @ g))
    return {"n": int(ok.sum()), "psi": psi, "se": se, "ci": [psi - 1.96 * se, psi + 1.96 * se],
            "halfwidth": 1.96 * se, "rel_halfwidth": float(1.96 * se / abs(psi)) if psi != 0 else None}
