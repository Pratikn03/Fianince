"""Model-derived reduced-form feedback estimator on the on-disk crypto LOB files.

Estimand (derived from the paper's heterogeneous-memory model, Section 3):

    x_{t+1} = a x_t + lambda f_t + e_{t+1}
    f_{t+1} = (1 - eta) f_t + eta c x_t + u_{t+1}

where x_t is the log-mid deviation (bps) from a trailing EMA reference and
f_t is signed market-order flow (buys - sells) executed over (t, t+1].
Writing y_t = lambda f_t gives the model with Q = lambda c, so

    S_hat = J11 + J12 * J21 / (1 - J22),   Q_hat = J12 * J21 / (1 - J22),

which is invariant to the scale of f.  Also
    1 - S = det(I - J) / (1 - J22),
so S < 1 is the real-root (momentum) boundary of the fitted VAR(1); the
fitted spectral radius rho(J) is reported alongside.

IMPORTANT CAVEATS (reported in the paper):
  * reduced form, not causal: f_t and e_{t+1} share news; lambda is not a
    structural impact coefficient;
  * f aggregates all market orders, not only adaptive/algorithmic traders;
  * x depends on the EMA proxy; under a martingale price the EMA alone
    implies a persistence benchmark a0 = 1 - 2/(W/Delta + 1);
  * three assets, one venue, ~12 days in April 2021.

Data provenance: empirical_pipeline/data/{BTC,ETH,ADA}_1sec.csv from
Martin Søgaard Nielsen, "High Frequency Crypto Limit Order Book Data" (Kaggle
dataset 1567989, v1, CC0, 2021-09-02), recorded from the Coinbase Pro WebSocket
order book feed using crypto-rl. Outputs: results/provenance/empirical_feedback.json
"""
from __future__ import annotations

import json
import os
import sys
from dataclasses import dataclass
from pathlib import Path

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
DATA_DIR = ROOT / "empirical_pipeline" / "data"
CACHE_DIR = ROOT / "empirical_pipeline" / "cache"
OUT_DIR = ROOT / "results" / "provenance"
ASSETS = ("BTC", "ETH", "ADA")


# --------------------------------------------------------------------------
# Loading
# --------------------------------------------------------------------------
CACHE_VERSION = "v2dedup"
# Columns whose joint equality with the previous row identifies a duplicated
# render (crypto-rl repeats the last snapshot, *including* its buys/sells
# totals, once per elapsed second when no tick arrives).
_DUP_KEYS = ["midpoint", "spread", "buys", "sells", "bids_notional_0",
             "asks_notional_0", "bids_distance_0", "asks_distance_0"]


def load_asset(asset: str) -> pd.DataFrame:
    """Return DataFrame indexed by integer UTC second with mid and flow.

    Timing (verified in source and empirically): the row stamped T carries
    the book at ~T and the taker buy/sell *notional* (quote currency) executed
    over (T-1, T].  Duplicated renders have their flow set to zero: with this
    correction the 1-second flow summed over (T-60, T] reproduces the
    dataset's own 1-minute buys exactly for every tested minute; without it
    only 73-90% of minutes match (see results/provenance/timing_check.json).
    """
    CACHE_DIR.mkdir(parents=True, exist_ok=True)
    cache = CACHE_DIR / f"{asset}_1sec_core_{CACHE_VERSION}.pkl"
    if cache.exists():
        return pd.read_pickle(cache)
    csv = DATA_DIR / f"{asset}_1sec.csv"
    df = pd.read_csv(csv, usecols=["system_time"] + _DUP_KEYS)
    ts = pd.to_datetime(df["system_time"], utc=True)
    dup = (df[_DUP_KEYS].shift(1) == df[_DUP_KEYS]).all(axis=1).to_numpy()
    flow = (df["buys"] - df["sells"]).astype(float).to_numpy()
    out = pd.DataFrame(
        {
            "sec": ((ts - pd.Timestamp("1970-01-01", tz="UTC")) // pd.Timedelta("1s")).astype("int64"),
            "mid": df["midpoint"].astype(float),
            "flow": np.where(dup, 0.0, flow),
            "dup": dup,
        }
    )
    out = out.drop_duplicates("sec").sort_values("sec").reset_index(drop=True)
    out.to_pickle(cache)
    return out


def _load_cached(asset: str) -> pd.DataFrame:
    return load_asset(asset)


# --------------------------------------------------------------------------
# Construction of (x_t, f_t)
# --------------------------------------------------------------------------
def build_series(df: pd.DataFrame, delta: int, window: int) -> pd.DataFrame:
    """Bin to `delta` seconds. x_b: log-mid deviation from EMA at end of bin b
    (bps). f_b: flow executed during bin b+1, i.e. over (t_b, t_{b+1}]."""
    b = df["sec"].to_numpy() // delta
    g = pd.DataFrame({"b": b, "mid": df["mid"].to_numpy(), "flow": df["flow"].to_numpy()})
    agg = g.groupby("b").agg(mid=("mid", "last"), flow=("flow", "sum"))
    full = np.arange(agg.index.min(), agg.index.max() + 1)
    agg = agg.reindex(full)
    agg["mid"] = agg["mid"].ffill()
    agg["flow"] = agg["flow"].fillna(0.0)
    p = np.log(agg["mid"].to_numpy()) * 1e4
    span = window / delta
    alpha = 2.0 / (span + 1.0)
    m = pd.Series(p).ewm(alpha=alpha, adjust=False).mean().to_numpy()
    x = p - m
    f_next = np.roll(agg["flow"].to_numpy(), -1)
    out = pd.DataFrame({"b": agg.index.to_numpy(), "x": x, "f": f_next})
    out = out.iloc[int(5 * span): -1]  # burn-in for EMA, drop wrapped last row
    out["day"] = pd.to_datetime(out["b"] * delta, unit="s", utc=True).dt.floor("D")
    return out.reset_index(drop=True)


# --------------------------------------------------------------------------
# Estimators
# --------------------------------------------------------------------------
def _ols(y: np.ndarray, X: np.ndarray) -> np.ndarray:
    return np.linalg.lstsq(X, y, rcond=None)[0]


def var1(x: np.ndarray, f: np.ndarray) -> dict:
    """OLS VAR(1) with intercept on z_t=(x_t,f_t). Returns J and S quantities."""
    Z = np.column_stack([x, f])
    X = np.column_stack([np.ones(len(Z) - 1), Z[:-1]])
    Y = Z[1:]
    B = _ols(Y, X)  # (3,2)
    J = B[1:].T  # rows: equation (x, f); cols: regressor (x, f)
    j11, j12, j21, j22 = J[0, 0], J[0, 1], J[1, 0], J[1, 1]
    Q = j12 * j21 / (1.0 - j22)
    S = j11 + Q
    rho = float(np.max(np.abs(np.linalg.eigvals(J))))
    L = Q / (1.0 - j11)  # loop ratio (eq. loopratio): S - 1 = (1 - a)(L - 1)
    return {"J11": j11, "J12": j12, "J21": j21, "J22": j22, "Q": Q, "S": S, "L": L, "rho": rho,
            "n": int(len(Y))}


def c_flow_controlled(x: np.ndarray, f: np.ndarray, L: int) -> float:
    """Coefficient on x_t in f_{t+1} ~ x_t + f_t + ... + f_{t-L+1}.
    Order-splitting (long memory in f) loads on x_t through past price impact;
    adding L flow lags absorbs that channel up to lag L."""
    n = len(x)
    rows = np.arange(L - 1, n - 1)
    X = np.column_stack([np.ones(len(rows)), x[rows]] + [f[rows - l] for l in range(L)])
    y = f[rows + 1]
    beta = _ols(y, X)
    return float(beta[1])


def q_long_memory_robust(x: np.ndarray, f: np.ndarray, L: int) -> dict:
    """Q_L = J12_hat * c_L / (1 - sum_l phi_l), where (c_L, phi_1..phi_L) are
    the coefficients of x_t and f_t..f_{t-L+1} in the f_{t+1} equation, and
    J12_hat is the flow coefficient in the x_{t+1} equation (VAR(1)).
    c_L / (1 - sum phi) is the long-run response of flow to a sustained
    deviation; with L = 1 this reproduces the VAR(1) Q exactly."""
    n = len(x)
    rows = np.arange(L - 1, n - 1)
    X = np.column_stack([np.ones(len(rows)), x[rows]] + [f[rows - l] for l in range(L)])
    beta = _ols(f[rows + 1], X)
    c_L, phis = beta[1], beta[2:]
    Xx = np.column_stack([np.ones(n - 1), x[:-1], f[:-1]])
    j12 = _ols(x[1:], Xx)[2]
    lr = c_L / (1.0 - phis.sum())
    return {"Q_L": float(j12 * lr), "c_L": float(c_L), "sum_phi": float(phis.sum())}


def distributed_lag(x: np.ndarray, f: np.ndarray, K: int, hac_lags: int = 10) -> tuple[np.ndarray, np.ndarray]:
    """Regress f_t on x_{t-1},...,x_{t-K} (model timing: y_t = sum_j k_j x_{t-1-j}).
    Returns coefficients b (length K) and a Newey-West covariance."""
    n = len(x)
    rows = n - K
    X = np.column_stack([np.ones(rows)] + [x[K - 1 - j: n - 1 - j] for j in range(K)])
    y = f[K:]
    beta = _ols(y, X)
    resid = y - X @ beta
    XtX_inv = np.linalg.pinv(X.T @ X)
    Xe = X * resid[:, None]
    S = Xe.T @ Xe
    for L in range(1, hac_lags + 1):
        w = 1.0 - L / (hac_lags + 1.0)
        G = Xe[L:].T @ Xe[:-L]
        S += w * (G + G.T)
    V = XtX_inv @ S @ XtX_inv
    return beta[1:], V[1:, 1:]


@dataclass
class Config:
    delta: int
    window: int


def day_estimates(series: pd.DataFrame, min_obs: int) -> list[dict]:
    res = []
    for day, g in series.groupby("day"):
        if len(g) < min_obs:
            continue
        est = var1(g["x"].to_numpy(), g["f"].to_numpy())
        est["day"] = str(day.date())
        res.append(est)
    return res


def placebo_estimates(series: pd.DataFrame, min_obs: int) -> list[dict]:
    """Pair x from day d with f from day d+1 (cyclic), aligned by position.
    Breaks any genuine x->f / f->x link while preserving marginal dynamics."""
    days = [g for _, g in series.groupby("day") if len(g) >= min_obs]
    out = []
    for i, g in enumerate(days):
        h = days[(i + 1) % len(days)]
        n = min(len(g), len(h))
        est = var1(g["x"].to_numpy()[:n], h["f"].to_numpy()[:n])
        out.append(est)
    return out


def summarize(vals: list[float]) -> dict:
    from scipy import stats

    a = np.asarray(vals, float)
    n = len(a)
    mean = float(a.mean())
    sd = float(a.std(ddof=1)) if n > 1 else float("nan")
    se = sd / np.sqrt(n) if n > 1 else float("nan")
    tcrit = float(stats.t.ppf(0.975, n - 1)) if n > 1 else float("nan")
    tstat = mean / se if n > 1 and se > 0 else float("nan")
    p = float(2 * stats.t.sf(abs(tstat), n - 1)) if n > 1 else float("nan")
    return {"mean": mean, "sd": sd, "se": se, "ci95": [mean - tcrit * se, mean + tcrit * se],
            "n_days": n, "t": tstat, "p_two_sided": p}


def run(assets=ASSETS, deltas=(1, 10, 60), windows=(60, 300, 900), baseline=(10, 300),
        K=10) -> dict:
    sys.path.insert(0, str(ROOT))
    from empirical_pipeline.cm_test import cm_cone_test

    out = {"estimand": "S_hat = J11 + J12*J21/(1-J22) from OLS VAR(1) on (x_t, f_t)",
           "data": {}, "grid": [], "baseline": {}, "kernel": {}}
    for asset in assets:
        df = _load_cached(asset)
        out["data"][asset] = {
            "first_utc": str(pd.to_datetime(df["sec"].iloc[0], unit="s", utc=True)),
            "last_utc": str(pd.to_datetime(df["sec"].iloc[-1], unit="s", utc=True)),
            "n_seconds": int(len(df)),
        }
        for d in deltas:
            for w in windows:
                if w / d < 3:
                    continue
                s = build_series(df, d, w)
                min_obs = int(0.5 * 86400 / d)
                days = day_estimates(s, min_obs)
                plac = placebo_estimates(s, min_obs)
                a0 = 1.0 - 2.0 / (w / d + 1.0)
                row = {
                    "asset": asset, "delta_s": d, "window_s": w, "a0_martingale_benchmark": a0,
                    "S": summarize([e["S"] for e in days]),
                    "Q": summarize([e["Q"] for e in days]),
                    "L": summarize([e["L"] for e in days]),
                    "a": summarize([e["J11"] for e in days]),
                    "rho": summarize([e["rho"] for e in days]),
                    "lambda_J12": summarize([e["J12"] for e in days]),
                    "c_J21": summarize([e["J21"] for e in days]),
                    "share_days_S_ge_1": float(np.mean([e["S"] >= 1 for e in days])),
                    "share_days_Q_pos": float(np.mean([e["Q"] > 0 for e in days])),
                    "placebo_Q": summarize([e["Q"] for e in plac]),
                }
                out["grid"].append(row)
                if (d, w) == baseline:
                    out["baseline"][asset] = {"days": days, "summary": row}
                    ctrl = {}
                    for L in (1, 30, 90):
                        cs = [c_flow_controlled(g["x"].to_numpy(), g["f"].to_numpy(), L)
                              for _, g in s.groupby("day") if len(g) >= min_obs]
                        ctrl[f"L{L}"] = summarize(cs)
                    out["baseline"][asset]["c_flow_lag_controlled"] = ctrl
                    qrob = {}
                    for L in (30, 90):
                        qs = [q_long_memory_robust(g["x"].to_numpy(), g["f"].to_numpy(), L)["Q_L"]
                              for _, g in s.groupby("day") if len(g) >= min_obs]
                        qrob[f"L{L}"] = summarize(qs)
                    out["baseline"][asset]["Q_long_memory_robust"] = qrob
                    # kernel + CM-cone test on pooled day-average kernel
                    bs, Vs = [], []
                    for _, g in s.groupby("day"):
                        if len(g) < min_obs:
                            continue
                        b, V = distributed_lag(g["x"].to_numpy(), g["f"].to_numpy(), K)
                        scale = np.std(g["f"].to_numpy())  # per-day flow-unit normalisation
                        bs.append(b / scale)
                        Vs.append(V / scale**2)
                    bs = np.array(bs)
                    kbar = bs.mean(0)
                    Vbar = np.mean(Vs, 0) / len(bs)
                    Vrep = np.cov(bs.T) / len(bs)
                    test_pos = cm_cone_test(kbar, Vbar, n_boot=2000, seed=11)
                    test_neg = cm_cone_test(-kbar, Vbar, n_boot=2000, seed=12)
                    out["kernel"][asset] = {
                        "K": K, "k_hat_per_sd_flow": kbar.tolist(),
                        "se_hac": np.sqrt(np.diag(Vbar)).tolist(),
                        "se_replicate": np.sqrt(np.diag(Vrep)).tolist(),
                        "cm_test_k": test_pos, "cm_test_minus_k": test_neg,
                    }
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    with open(OUT_DIR / "empirical_feedback.json", "w") as fh:
        json.dump(out, fh, indent=2, default=float)
    return out


if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "cache":
        for a in ASSETS:
            d = load_asset(a)
            print(a, len(d), d["sec"].iloc[0], d["sec"].iloc[-1])
    else:
        r = run()
        for a, v in r["baseline"].items():
            s = v["summary"]
            print(a, "S", round(s["S"]["mean"], 4), s["S"]["ci95"], "Q", round(s["Q"]["mean"], 5),
                  s["Q"]["ci95"], "a0", round(s["a0_martingale_benchmark"], 4))
