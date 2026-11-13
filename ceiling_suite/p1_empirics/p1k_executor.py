"""P1K executor: Korea multi-class tagged flows (spec P1K_spec.md). Computes everything from a panel; downloads
nothing. The notebook builds the panel from KRX data; validate_p1k.py builds it from simulated markets.

Panel (pandas DataFrame, one row per stock-day): columns 'ticker', 'date' (datetime64), 'close' (adjusted),
'mcap' (market capitalization), and one column per investor class with that day's net purchase value.

Pipeline
  1. x_t  = (log close - mean of the previous 60 log closes) / trailing 250-day sd of daily log returns.
     u_i,t = net purchase of class i / market cap at t-1.
  2. For each stock-year with at least MIN_OBS usable days and each class: IV of u_t on (1, u_{t-1}, x_t) with
     instruments (1, x_{t-2}, x_{t-3}). r_i is clipped to [0, 0.99].
  3. Kernel features k_m = sum_i w_i r_i^m, m = 0..9. Composition features: each class's share of sum_i |w_i|.
     Outcome Y: the stock-year's daily log-return autocorrelations at lags 1..10.
  4. Baseline features: log mean market cap, log return volatility, and the leave-one-out cross-sectional mean
     of Y in the same year. Models: B0 = baseline; A = baseline + kernel; B = A + composition.
     Ridge regressions, one per lag, fitted on development stock-years; penalty by 5-fold CV grouped by stock.
     Features winsorized at development 1st/99th percentiles and standardized with development moments.
  5. Holdout gains: G_A = MSE(B0) - MSE(A), G_BA = MSE(A) - MSE(B), MSE averaged over lags and stock-years.
     Stock-cluster bootstrap (B draws, seed SEED) for intervals.
  6. H1: Kruskal-Wallis across classes of holdout r_i. H2 supportive if the 95% interval of G_A excludes zero
     from above and the 90% interval of G_BA lies inside (-E, E), E = E_FRAC * G_A. Inconsistent if the 90%
     interval of G_BA lies above E. Otherwise inconclusive. H3 (descriptive): correlation across holdout
     stock-years between a price-only memory estimate (the decay rate of a one-exponential fit to the return
     autocorrelations at lags 1..10) and the weight-averaged tagged memory.
"""
from __future__ import annotations

import numpy as np
import pandas as pd
from scipy import stats

SEED = 20261111
B_DEFAULT = 999
MIN_OBS = 200
MA_WIN = 60
VOL_WIN = 250
LAGS = 10
KERNEL_M = 10
E_FRAC = 0.10
DEV_YEARS = range(2012, 2019)
HOLD_YEARS = range(2019, 2026)
RIDGE_GRID = np.logspace(-3, 3, 13)
OUTCOME = "ret"   # "ret": return autocorrelations at lags 1..10; "x": autocorrelations of x at lags 1, 2, 5, 10, 20


def class_columns(panel: pd.DataFrame) -> list[str]:
    return [c for c in panel.columns if c not in ("ticker", "date", "close", "mcap", "year")]


def prepare(panel: pd.DataFrame) -> pd.DataFrame:
    """Adds x, ret, and the scaled class flows (prefixed 'u:'). Causal transformations only."""
    out = []
    classes = class_columns(panel)
    for _, g in panel.sort_values(["ticker", "date"]).groupby("ticker", sort=False):
        g = g.copy()
        lp = np.log(g["close"].astype(float).where(g["close"] > 0))
        ret = lp.diff()
        ma = lp.shift(1).rolling(MA_WIN, min_periods=MA_WIN).mean()
        sd = ret.shift(1).rolling(VOL_WIN, min_periods=120).std()
        g["x"] = (lp - ma) / sd
        g["ret"] = ret
        mcap_lag = g["mcap"].astype(float).shift(1).where(lambda s: s > 0)
        for c in classes:
            g["u:" + c] = g[c].astype(float) / mcap_lag
        g["year"] = g["date"].dt.year
        out.append(g)
    return pd.concat(out, ignore_index=True)


def _iv(y: np.ndarray, X: np.ndarray, Z: np.ndarray):
    """Just-identified IV: beta = (Z'X)^{-1} Z'y. Returns None if Z'X is ill-conditioned."""
    zx = Z.T @ X
    if not np.all(np.isfinite(zx)) or np.linalg.cond(zx) > 1e10:
        return None
    return np.linalg.solve(zx, Z.T @ y)


def _acf(r: np.ndarray, lags: int = LAGS) -> np.ndarray:
    r = r - r.mean()
    v = np.dot(r, r)
    return np.array([np.dot(r[k:], r[:-k]) / v for k in range(1, lags + 1)])


def stock_years(prep: pd.DataFrame) -> pd.DataFrame:
    """One row per usable stock-year: tagged estimates, kernel, composition, outcome and baseline inputs."""
    classes = [c[2:] for c in prep.columns if c.startswith("u:")]
    rows = []
    for (tk, yr), g in prep.groupby(["ticker", "year"], sort=False):
        g = g.sort_values("date")
        x = g["x"].to_numpy(); ret = g["ret"].to_numpy()
        rec = {"ticker": tk, "year": int(yr)}
        rs, ws = {}, {}
        for c in classes:
            u = g["u:" + c].to_numpy()
            y_, u1, x0, x2, x3 = u[3:], u[2:-1], x[3:], x[1:-2], x[:-3]
            ok = np.isfinite(y_) & np.isfinite(u1) & np.isfinite(x0) & np.isfinite(x2) & np.isfinite(x3)
            if ok.sum() < MIN_OBS:
                rs[c] = np.nan; ws[c] = np.nan; continue
            one = np.ones(ok.sum())
            b = _iv(y_[ok], np.column_stack([one, u1[ok], x0[ok]]), np.column_stack([one, x2[ok], x3[ok]]))
            if b is None:
                rs[c] = np.nan; ws[c] = np.nan; continue
            rs[c] = float(np.clip(b[1], 0.0, 0.99)); ws[c] = float(b[2])
        okr = np.isfinite(ret)
        if okr.sum() < MIN_OBS or sum(np.isfinite(v) for v in ws.values()) < 2:
            continue
        r_ok = ret[okr]
        if OUTCOME == "x":
            xx = x[np.isfinite(x)]
            if len(xx) < MIN_OBS:
                continue
            rec["Y"] = _acf(xx, 20)[[0, 1, 4, 9, 19]]
        else:
            rec["Y"] = _acf(r_ok)
        rec["vol"] = float(np.std(r_ok))
        rec["log_mcap"] = float(np.log(g["mcap"].astype(float).where(g["mcap"] > 0).mean()))
        w = np.array([ws[c] if np.isfinite(ws[c]) else 0.0 for c in classes])
        r = np.array([rs[c] if np.isfinite(rs[c]) else 0.0 for c in classes])
        rec["kernel"] = np.array([np.sum(w * r ** m) for m in range(KERNEL_M)])
        tot = np.sum(np.abs(w))
        rec["comp"] = np.abs(w) / tot if tot > 0 else np.zeros_like(w)
        rec["r"] = r; rec["w"] = w; rec["r_valid"] = np.array([np.isfinite(rs[c]) for c in classes])
        rec["mem_tagged"] = float(np.sum(np.abs(w) * r) / tot) if tot > 0 else np.nan
        rows.append(rec)
    sy = pd.DataFrame(rows)
    sy.attrs["classes"] = classes
    return sy


def _design(sy: pd.DataFrame, which: str) -> np.ndarray:
    Y = np.stack(sy["Y"].to_numpy())
    loo = np.zeros_like(Y)
    for yr, idx in sy.groupby("year").groups.items():
        idx = np.asarray([sy.index.get_loc(i) for i in idx])
        s = Y[idx].sum(0)
        n = len(idx)
        loo[idx] = (s - Y[idx]) / max(n - 1, 1)
    base = np.column_stack([sy["log_mcap"], np.log(sy["vol"])])
    parts = {"B0": [base], "A": [base, np.stack(sy["kernel"].to_numpy())],
             "B": [base, np.stack(sy["kernel"].to_numpy()), np.stack(sy["comp"].to_numpy())]}[which]
    return np.column_stack(parts), loo


def _fit_predict(Xd, Yd, Ld, Xh, Lh, groups_d, rng):
    """Ridge per lag on standardized, winsorized features; target is Y minus the leave-one-out year mean."""
    lo = np.nanpercentile(Xd, 1, axis=0); hi = np.nanpercentile(Xd, 99, axis=0)
    Xd = np.clip(Xd, lo, hi); Xh = np.clip(Xh, lo, hi)
    mu = Xd.mean(0); sd = Xd.std(0); sd[sd == 0] = 1.0
    Xd = (Xd - mu) / sd; Xh = (Xh - mu) / sd
    Td = Yd - Ld
    ug = np.unique(groups_d); rng.shuffle(ug)
    fold = {g: k % 5 for k, g in enumerate(ug)}
    f = np.array([fold[g] for g in groups_d])
    best, best_err = RIDGE_GRID[0], np.inf
    for lam in RIDGE_GRID:
        err = 0.0
        for k in range(5):
            tr, te = f != k, f == k
            A = Xd[tr]; m = Td[tr].mean(0)
            beta = np.linalg.solve(A.T @ A + lam * len(A) * np.eye(A.shape[1]), A.T @ (Td[tr] - m))
            err += np.sum((Td[te] - m - Xd[te] @ beta) ** 2)
        if err < best_err:
            best, best_err = lam, err
    m = Td.mean(0)
    beta = np.linalg.solve(Xd.T @ Xd + best * len(Xd) * np.eye(Xd.shape[1]), Xd.T @ (Td - m))
    return Lh + m + Xh @ beta, float(best)


def evaluate(sy: pd.DataFrame, B: int = B_DEFAULT, seed: int = SEED, e_frac: float = E_FRAC) -> dict:
    dev = sy[sy["year"].isin(DEV_YEARS)].reset_index(drop=True)
    hold = sy[sy["year"].isin(HOLD_YEARS)].reset_index(drop=True)
    if len(dev) < 50 or len(hold) < 50:
        return {"status": "not_evaluable", "reason": f"too few stock-years (development {len(dev)}, holdout {len(hold)})"}
    rng = np.random.default_rng(seed)
    Yh = np.stack(hold["Y"].to_numpy())
    preds, lams = {}, {}
    for which in ("B0", "A", "B"):
        Xd, Ld = _design(dev, which); Xh, Lh = _design(hold, which)
        preds[which], lams[which] = _fit_predict(Xd, np.stack(dev["Y"].to_numpy()), Ld, Xh, Lh,
                                                 dev["ticker"].to_numpy(), np.random.default_rng(seed))
    se = {k: ((Yh - p) ** 2).mean(1) for k, p in preds.items()}          # per stock-year MSE over lags
    gA = se["B0"] - se["A"]; gBA = se["A"] - se["B"]
    G_A, G_BA = float(gA.mean()), float(gBA.mean())
    tick = hold["ticker"].to_numpy(); ut = np.unique(tick)
    idx_by = {t: np.where(tick == t)[0] for t in ut}
    bA, bBA = np.empty(B), np.empty(B)
    for b in range(B):
        pick = rng.choice(ut, size=len(ut), replace=True)
        ii = np.concatenate([idx_by[t] for t in pick])
        bA[b] = gA[ii].mean(); bBA[b] = gBA[ii].mean()
    ciA95 = [float(x) for x in np.percentile(bA, [2.5, 97.5])]
    ciBA90 = [float(x) for x in np.percentile(bBA, [5, 95])]
    E = e_frac * G_A
    if ciA95[0] > 0 and E > 0 and -E < ciBA90[0] and ciBA90[1] < E:
        verdict = "supportive"
    elif E > 0 and ciBA90[0] > E:
        verdict = "inconsistent"
    else:
        verdict = "inconclusive"
    # H1
    classes = sy.attrs.get("classes", [])
    R = np.stack(hold["r"].to_numpy()); V = np.stack(hold["r_valid"].to_numpy())
    groups = [R[V[:, j], j] for j in range(R.shape[1]) if V[:, j].sum() >= 20]
    h1_p = float(stats.kruskal(*groups).pvalue) if len(groups) >= 2 else np.nan
    med = {classes[j]: float(np.median(R[V[:, j], j])) for j in range(R.shape[1]) if V[:, j].sum() >= 20} if classes else {}
    # H3 (descriptive)
    def price_memory(y):
        y = np.clip(y, 1e-6, None) if np.all(y > 0) else None
        if y is None:
            return np.nan
        k = np.arange(1, len(y) + 1)
        slope = np.polyfit(k, np.log(y), 1)[0]
        return float(np.exp(slope))
    pm = np.array([price_memory(y) for y in Yh]); tm = hold["mem_tagged"].to_numpy()
    ok = np.isfinite(pm) & np.isfinite(tm)
    h3 = {"n": int(ok.sum()), "spearman": float(stats.spearmanr(pm[ok], tm[ok]).correlation) if ok.sum() > 10 else None}
    return {"status": "evaluated", "n_dev_stock_years": int(len(dev)), "n_hold_stock_years": int(len(hold)),
            "n_hold_stocks": int(len(ut)), "ridge_penalties": lams,
            "mse": {k: float(v.mean()) for k, v in se.items()},
            "G_A": G_A, "G_A_ci95": ciA95, "G_BA": G_BA, "G_BA_ci90": ciBA90, "E": float(E), "E_frac": e_frac,
            "H1_kruskal_p": h1_p, "H1_median_r_by_class": med, "H3_price_vs_tagged_memory": h3,
            "verdict": verdict, "B": B, "seed": seed}


def readout(r: dict) -> str:
    if r.get("status") != "evaluated":
        return "The registered Korea test could not be evaluated: " + r.get("reason", "")
    a = (r["G_A"], *r["G_A_ci95"]); b = (r["G_BA"], *r["G_BA_ci90"])
    nums = (f"(gain from the kernel {a[0]:.3g}, 95% interval [{a[1]:.3g}, {a[2]:.3g}]; further gain from "
            f"composition {b[0]:.3g}, 90% interval [{b[1]:.3g}, {b[2]:.3g}], margin {r['E']:.3g})")
    if r["verdict"] == "supportive":
        return ("In a pre-specified out-of-sample test on Korea's tagged investor-class flows (2019-2025), the "
                "feedback kernel estimated from tagged flows predicted stocks' return dynamics, and the composition "
                "behind the kernel added no predictive power beyond a pre-set margin " + nums + ". This is the "
                "pattern the sufficiency theorem predicts, at daily frequency.")
    if r["verdict"] == "inconsistent":
        return ("In a pre-specified out-of-sample test on Korea's tagged investor-class flows (2019-2025), the "
                "composition behind the kernel predicted return dynamics beyond the kernel " + nums + ". This is "
                "against the sufficiency prediction at daily frequency.")
    return ("A pre-specified out-of-sample test on Korea's tagged investor-class flows (2019-2025) was inconclusive "
            + nums + ". It neither supports nor contradicts the sufficiency prediction.")
