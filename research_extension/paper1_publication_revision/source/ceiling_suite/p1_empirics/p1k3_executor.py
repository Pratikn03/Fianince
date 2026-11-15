"""P1K3 executor (spec P1K3_spec.md): is each investor category's memory common across stocks? Downloads nothing.

Input: a long panel with columns 'ticker', 'date' (datetime64), 'close' (adjusted), 'mcap', 'member' (True on days of
an included stock-year) and one column per category with that day's net purchase value. The notebook builds it from
KRX data; validate_p1k3.py builds it from simulated markets. run(panel) returns the full result dictionary.
"""
from __future__ import annotations

import math

import numpy as np
import pandas as pd
from scipy import sparse, stats
from scipy.signal import lfilter

SEED = 20261113
B = 999
DELTA = 0.25
MA_WIN = 60
DROP_DAYS = 20
MIN_OBS = 150
R_GRID = np.round(np.arange(0.0, 0.991, 0.01), 2)
FLOW_START, FLOW_END = "2015-01-01", "2025-12-31"
SIGN_SHARE, SIGN_P = 0.65, 0.001
MIN_YEARS_PER_HALF = 2
WINSOR = (0.005, 0.995)


def categories(panel: pd.DataFrame) -> list[str]:
    return [c for c in panel.columns if c not in ("ticker", "date", "close", "mcap", "member", "year")]


def prepare(panel: pd.DataFrame) -> dict:
    """Wide arrays. x_t = (log close - mean of the previous 60 log closes) / the stock's sd of daily log returns over the
    flow period; u = flow / mcap at t-1, winsorized within stock-year."""
    cats = categories(panel)
    p = panel.sort_values(["ticker", "date"])
    tickers = list(pd.unique(p["ticker"]))
    dates = pd.DatetimeIndex(sorted(pd.unique(p["date"])))
    wide = lambda col: p.pivot(index="ticker", columns="date", values=col).reindex(index=tickers, columns=dates)
    close = wide("close").to_numpy(float)
    mcap = wide("mcap").to_numpy(float)
    member = wide("member").fillna(False).to_numpy(bool)
    lp = np.log(np.where(close > 0, close, np.nan))
    lpdf = pd.DataFrame(lp.T)
    ma = lpdf.shift(1).rolling(MA_WIN, min_periods=MA_WIN).mean().to_numpy().T
    ret = np.diff(lp, axis=1, prepend=np.nan)
    in_flow = (dates >= FLOW_START) & (dates <= FLOW_END)
    sd = np.nanstd(np.where(in_flow[None, :], ret, np.nan), axis=1)
    x = (lp - ma) / sd[:, None]
    lp_prev = np.concatenate([np.full((len(tickers), 1), np.nan), lp[:, :-1]], axis=1)
    kreg = (lp_prev - ma) / sd[:, None]       # x_t without the same-day return: known before day t's trading
    mlag = np.concatenate([np.full((len(tickers), 1), np.nan), mcap[:, :-1]], axis=1)
    mlag = np.where(mlag > 0, mlag, np.nan)
    U = np.stack([wide(c).to_numpy(float) / mlag for c in cats], axis=2)          # S x T x C
    year = dates.year.to_numpy()
    usable = member & in_flow[None, :] & np.isfinite(x) & np.isfinite(kreg) & np.all(np.isfinite(U), axis=2)
    # stock-year groups; drop the first DROP_DAYS usable days of each stock-year; keep stock-years with >= MIN_OBS days
    gid = np.full(usable.shape, -1, int); groups = []
    for s in range(len(tickers)):
        for yv in np.unique(year[usable[s]]):
            idx = np.where(usable[s] & (year == yv))[0][DROP_DAYS:]
            if len(idx) >= MIN_OBS:
                gid[s, idx] = len(groups); groups.append((s, int(yv), len(idx)))
    sel = gid >= 0
    s_idx, t_idx = np.where(sel)
    g = gid[sel]
    Uv = U[s_idx, t_idx, :]
    # winsorize each category's flow within stock-year
    for k in range(len(groups)):
        rows = np.where(g == k)[0]
        lo, hi = np.quantile(Uv[rows], WINSOR, axis=0)
        Uv[rows] = np.clip(Uv[rows], lo, hi)
    return {"cats": cats, "tickers": tickers, "dates": dates, "x": np.nan_to_num(x), "k": kreg, "s_idx": s_idx, "t_idx": t_idx,
            "g": g, "groups": groups, "U": Uv}


def profiles(d: dict):
    """For every stock-year group, category and grid memory: regression of u_t on (1, k_t, m_{t-1}(r)), where
    k_t = x_t minus the same-day return (so every regressor is known before day t's trading and same-day reverse
    causality cannot enter); returns normalized SSE and the coefficient on m_{t-1}(r)."""
    G, C, R = len(d["groups"]), len(d["cats"]), len(R_GRID)
    n_obs = len(d["g"])
    Gm = sparse.csr_matrix((np.ones(n_obs), (np.arange(n_obs), d["g"])), shape=(n_obs, G)).T.tocsr()   # G x n
    xv = d["k"][d["s_idx"], d["t_idx"]]     # the regressor is k_t (past prices only), not the same-day x_t
    U = d["U"]
    n = np.asarray(Gm.sum(1)).ravel()
    Su = Gm @ U; Suu = Gm @ (U * U)
    Sx = Gm @ xv; Sxx = Gm @ (xv * xv); Sxu = Gm @ (U * xv[:, None])
    tss = Suu - Su ** 2 / n[:, None]
    nsse = np.empty((G, C, R)); beta = np.empty((G, C, R))
    for j, r in enumerate(R_GRID):
        acc = lfilter([1.0], [1.0, -r], d["x"], axis=1)
        m_full = np.concatenate([np.zeros((acc.shape[0], 1)), acc[:, :-1]], axis=1)
        mv = m_full[d["s_idx"], d["t_idx"]]
        Sm = Gm @ mv; Smm = Gm @ (mv * mv); Sxm = Gm @ (xv * mv); Smu = Gm @ (U * mv[:, None])
        A = np.empty((G, 3, 3))
        A[:, 0, 0] = n; A[:, 0, 1] = A[:, 1, 0] = Sx; A[:, 0, 2] = A[:, 2, 0] = Sm
        A[:, 1, 1] = Sxx; A[:, 1, 2] = A[:, 2, 1] = Sxm; A[:, 2, 2] = Smm
        rhs = np.stack([Su, Sxu, Smu], axis=1)                                   # G x 3 x C
        b = np.linalg.solve(A + 1e-12 * np.eye(3)[None], rhs)                    # G x 3 x C
        sse = Suu - np.einsum("gkc,gkc->gc", b, rhs)
        nsse[:, :, j] = sse / tss
        beta[:, :, j] = b[:, 2, :]
    return nsse, beta, n


def run(panel: pd.DataFrame, n_boot: int = B, seed: int = SEED) -> dict:
    d = prepare(panel)
    nsse, beta, n = profiles(d)
    cats, groups = d["cats"], d["groups"]
    S = len(d["tickers"])
    gs = np.array([s for s, _, _ in groups]); gy = np.array([y for _, y, _ in groups])
    odd = gy % 2 == 1
    rng = np.random.default_rng(seed)
    out = {"n_stocks_with_groups": int(len(np.unique(gs))), "n_stock_years": int(len(groups)), "delta": DELTA,
           "categories": {}}
    # per-stock profiles: all years, odd years, even years   (S x C x R)
    def stock_sum(mask):
        M = sparse.csr_matrix((np.ones(mask.sum()), (gs[mask], np.where(mask)[0])), shape=(S, len(groups)))
        return np.stack([M @ nsse[:, c, :] for c in range(len(cats))], axis=1), np.asarray(M.sum(1)).ravel()
    P_all, k_all = stock_sum(np.ones(len(groups), bool))
    P_odd, k_odd = stock_sum(odd)
    P_even, k_even = stock_sum(~odd)
    both = (k_odd >= MIN_YEARS_PER_HALF) & (k_even >= MIN_YEARS_PER_HALF)
    has = k_all > 0
    out["n_stocks_both_halves"] = int(both.sum())
    ident = []
    for c, name in enumerate(cats):
        jc = int(np.argmin(P_all[has, c, :].sum(0)))
        rc = float(R_GRID[jc])
        bs = np.zeros(S)
        np.add.at(bs, gs, n * beta[:, c, jc])
        bs = bs[has]
        npos, ntot = int((bs > 0).sum()), int((bs != 0).sum())
        share = max(npos, ntot - npos) / ntot if ntot else 0.0
        p_sign = float(stats.binomtest(npos, ntot, 0.5).pvalue) if ntot else 1.0
        identified = bool((0 < jc < len(R_GRID) - 1) and share >= SIGN_SHARE and p_sign < SIGN_P)
        # pooled log memory speed and its stock bootstrap interval (S1)
        idx_has = np.where(has)[0]
        cnt = rng.multinomial(len(idx_has), np.full(len(idx_has), 1 / len(idx_has)), size=n_boot)
        jb = np.argmin(cnt @ P_all[idx_has, c, :], axis=1)
        lb = np.log(1 - R_GRID[jb])
        row = {"r_pooled": rc, "l_pooled": float(math.log(1 - rc)), "l_pooled_ci95": [float(np.quantile(lb, 0.025)), float(np.quantile(lb, 0.975))],
               "sign_share": float(share), "sign_p": p_sign, "identified": identified}
        # between-stock spread (split-half covariance)
        lo = np.log(1 - R_GRID[np.argmin(P_odd[both, c, :], axis=1)])
        le = np.log(1 - R_GRID[np.argmin(P_even[both, c, :], axis=1)])
        nb = len(lo)
        if nb >= 10:
            tau2 = float(np.cov(lo, le)[0, 1])
            ib = rng.integers(0, nb, size=(n_boot, nb))
            a, e = lo[ib], le[ib]
            cb = ((a - a.mean(1, keepdims=True)) * (e - e.mean(1, keepdims=True))).sum(1) / (nb - 1)
            tb = np.sqrt(np.maximum(cb, 0))
            row.update({"tau2": tau2, "tau": float(math.sqrt(max(tau2, 0))), "L": float(np.quantile(tb, 0.05)),
                        "U": float(np.quantile(tb, 0.95)), "n_stocks": nb,
                        "split_half_corr": float(np.corrcoef(lo, le)[0, 1]) if np.std(lo) > 0 and np.std(le) > 0 else None})
            row["common"] = bool(row["U"] < DELTA); row["heterogeneous"] = bool(row["L"] > DELTA)
        else:
            row.update({"tau2": None, "common": False, "heterogeneous": False, "n_stocks": nb})
        out["categories"][name] = row
        if identified:
            ident.append(name)
    k = len(ident)
    n_common = sum(out["categories"][c]["common"] for c in ident)
    n_het = sum(out["categories"][c]["heterogeneous"] for c in ident)
    if k < 4:
        verdict = "not testable"
    elif n_common >= math.ceil(2 * k / 3):
        verdict = "supportive"
    elif n_het > k / 2:
        verdict = "inconsistent"
    else:
        verdict = "inconclusive"
    pairs = []
    for i, a in enumerate(ident):
        for b_ in ident[i + 1:]:
            ia, ib_ = out["categories"][a]["l_pooled_ci95"], out["categories"][b_]["l_pooled_ci95"]
            if ia[1] < ib_[0] or ib_[1] < ia[0]:
                pairs.append([a, b_])
    out.update({"identified": ident, "n_identified": k, "n_common": int(n_common), "n_heterogeneous": int(n_het),
                "verdict": verdict, "S1_disjoint_pairs": pairs})
    return out
