"""Systematic Binance Panel Pipeline (2021-2024).

Ingests public 1-second klines from data.binance.vision for 8 major USDT pairs
over 48 months (2 pre-registered days per month: 10th and 24th = 768 asset-days),
plus the January 2023 holdout period (1-09-1-20.csv match).

Computes:
  * Baseline VAR(1) feedback: Q_hat, S_hat, L_hat, rho(J)
  * Flow long-memory controlled feedback: Q_30, c_90/c_1
  * Day-lead placebo
  * C1 Structural Minimum-Distance (SMM / Lyapunov) estimator with J-test
  * C2 Rigobon identification through heteroskedasticity
"""
from __future__ import annotations

import io
import json
import logging
import os
import sys
import urllib.request
import zipfile
from concurrent.futures import ThreadPoolExecutor, as_completed
from dataclasses import asdict, dataclass
from pathlib import Path

import numpy as np
import pandas as pd
from scipy.optimize import minimize
from scipy.stats import chi2

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from empirical_pipeline.feedback_var import build_series, var1, c_flow_controlled, q_long_memory_robust

# Storage on T9 if available, else local
T9_DIR = Path("/Volumes/T9/machine_markets_data/binance_1s")
LOCAL_DIR = ROOT / "empirical_pipeline" / "cache" / "binance_1s"
STORAGE_DIR = T9_DIR if Path("/Volumes/T9").exists() else LOCAL_DIR

RESULTS_DIR = ROOT / "results" / "provenance"

ASSETS = ["BTCUSDT", "ETHUSDT", "SOLUSDT", "BNBUSDT", "XRPUSDT", "ADAUSDT", "DOGEUSDT", "LTCUSDT"]
YEARS = [2021, 2022, 2023, 2024]
DAYS_PER_MONTH = [10, 24]


def get_panel_dates() -> list[str]:
    dates = []
    for y in YEARS:
        for m in range(1, 13):
            for d in DAYS_PER_MONTH:
                dates.append(f"{y:04d}-{m:02d}-{d:02d}")
    return sorted(dates)


def get_holdout_dates() -> list[str]:
    return [f"2023-01-{d:02d}" for d in range(10, 21)]


def download_and_preprocess_day(symbol: str, date: str) -> pd.DataFrame | None:
    STORAGE_DIR.mkdir(parents=True, exist_ok=True)
    cache_path = STORAGE_DIR / f"{symbol}_{date}.parquet"
    if cache_path.exists():
        try:
            return pd.read_parquet(cache_path)
        except Exception:
            pass

    url = f"https://data.binance.vision/data/spot/daily/klines/{symbol}/1s/{symbol}-1s-{date}.zip"
    try:
        req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
        with urllib.request.urlopen(req, timeout=15) as resp:
            buf = io.BytesIO(resp.read())
    except Exception:
        return None

    try:
        with zipfile.ZipFile(buf) as z:
            name = z.namelist()[0]
            with z.open(name) as f:
                df = pd.read_csv(f, header=None, usecols=[0, 4, 7, 10])
    except Exception:
        return None

    df.columns = ["open_time", "close", "tot_quote", "buy_quote"]
    sec = (df["open_time"] // 1000).astype("int64")
    flow = (2.0 * df["buy_quote"] - df["tot_quote"]).astype(float)
    mid = df["close"].astype(float)

    # Reindex to full UTC day (86,400 seconds)
    t0 = int(pd.Timestamp(f"{date} 00:00:00", tz="UTC").timestamp())
    full_sec = np.arange(t0, t0 + 86400, dtype="int64")

    s = pd.DataFrame({"sec": sec, "mid": mid, "flow": flow}).drop_duplicates("sec").set_index("sec")
    s = s.reindex(full_sec)
    s["mid"] = s["mid"].ffill().bfill()
    s["flow"] = s["flow"].fillna(0.0)
    out = s.reset_index().rename(columns={"index": "sec"})

    try:
        out.to_parquet(cache_path)
    except Exception:
        pass
    return out


# --------------------------------------------------------------------------
# C1: Structural Minimum-Distance Covariance Matching (SMM / Lyapunov)
# --------------------------------------------------------------------------
def solve_lyapunov(J: np.ndarray, Sigma: np.ndarray) -> np.ndarray | None:
    I = np.eye(4)
    JJ = np.kron(J, J)
    denom = I - JJ
    if abs(np.linalg.det(denom)) < 1e-7:
        return None
    try:
        vec_gamma = np.linalg.solve(denom, Sigma.flatten())
        return vec_gamma.reshape(2, 2)
    except np.linalg.LinAlgError:
        return None


def fit_structural_c1(x: np.ndarray, f: np.ndarray, K: int = 3) -> dict:
    x_sd = float(np.std(x))
    f_sd = float(np.std(f))
    if x_sd < 1e-8 or f_sd < 1e-8:
        return {"success": False, "Q": float("nan"), "S": float("nan"), "J_stat": float("nan"), "p_val": float("nan")}
    x_norm = (x - np.mean(x)) / x_sd
    f_norm = (f - np.mean(f)) / f_sd
    N = len(x)
    Z = np.column_stack([x_norm, f_norm])

    sample_gammas = []
    for k in range(K + 1):
        if k == 0:
            G = (Z.T @ Z) / N
        else:
            G = (Z[k:].T @ Z[:-k]) / (N - k)
        sample_gammas.append(G)

    v = var1(x_norm, f_norm)
    a_init = float(np.clip(v["J11"], 0.5, 0.98))
    lam_init = float(np.clip(v["J12"], -0.4, 0.4))
    eta_init = float(np.clip(1.0 - v["J22"], 0.05, 0.95))
    c_init = float(np.clip(v["J21"], -0.4, 0.4))
    init = [a_init, lam_init, eta_init, c_init, 0.5, 0.5, 0.0]
    bounds = [(0.5, 0.99), (-0.5, 0.5), (0.01, 0.99), (-0.5, 0.5), (0.01, 2.0), (0.01, 2.0), (-0.95, 0.95)]

    def loss(p):
        a, lam, eta, c, sx, sf, rho = p
        J = np.array([[a, lam], [eta * c, 1.0 - eta]])
        eigs = np.abs(np.linalg.eigvals(J))
        if np.max(eigs) >= 0.995:
            return 1e6
        Sigma = np.array([[sx**2, rho * sx * sf], [rho * sx * sf, sf**2]])
        G0 = solve_lyapunov(J, Sigma)
        if G0 is None:
            return 1e6
        err = float(np.sum((G0 - sample_gammas[0])**2))
        Jk = np.eye(2)
        for k in range(1, K + 1):
            Jk = Jk @ J
            err += float(np.sum((Jk @ G0 - sample_gammas[k])**2))
        return err

    opt = minimize(loss, init, method="L-BFGS-B", bounds=bounds)
    a_opt, lam_opt, eta_opt, c_opt = opt.x[:4]
    Q_opt = lam_opt * c_opt
    S_opt = a_opt + Q_opt
    df = 4 * (K + 1) - 7
    J_stat = float(N * opt.fun)
    p_val = float(1.0 - chi2.cdf(J_stat, df=max(1, df))) if np.isfinite(J_stat) else float("nan")
    return {
        "success": bool(opt.success),
        "a": float(a_opt),
        "lambda": float(lam_opt),
        "eta": float(eta_opt),
        "c": float(c_opt),
        "Q": float(Q_opt),
        "S": float(S_opt),
        "J_stat": float(J_stat),
        "p_val": float(p_val),
    }


# --------------------------------------------------------------------------
# C2: Rigobon Identification through Volatility Regimes
# --------------------------------------------------------------------------
def fit_rigobon_c2(x: np.ndarray, f: np.ndarray) -> dict:
    x_sd = float(np.std(x))
    f_sd = float(np.std(f))
    if x_sd < 1e-8 or f_sd < 1e-8:
        return {"success": False, "lambda": float("nan"), "alpha": float("nan"), "Q": float("nan")}
    x_norm = (x - np.mean(x)) / x_sd
    f_norm = (f - np.mean(f)) / f_sd
    rolling_vol = pd.Series(x).rolling(60).std().bfill().to_numpy()
    q33, q67 = np.percentile(rolling_vol, [33.3, 66.7])
    r1 = rolling_vol < q33
    r2 = (rolling_vol >= q33) & (rolling_vol < q67)
    r3 = rolling_vol >= q67

    dx = np.diff(x_norm)
    fl = f_norm[1:]
    r1, r2, r3 = r1[1:], r2[1:], r3[1:]

    Omegas = []
    for reg in [r1, r2, r3]:
        if np.sum(reg) < 50:
            return {"success": False, "lambda": float("nan"), "alpha": float("nan"), "Q": float("nan")}
        d = np.column_stack([dx[reg], fl[reg]])
        d = d - np.mean(d, axis=0)
        Omegas.append((d.T @ d) / len(d))

    def gmm(p):
        lam, alpha, s1p, s1f, s2p, s2f, s3p, s3f = p
        detA = 1.0 - lam * alpha
        if abs(detA) < 1e-4:
            return 1e6
        invA = np.array([[1.0, lam], [alpha, 1.0]]) / detA
        err = 0.0
        for Omg, sp, sf in zip(Omegas, [s1p, s2p, s3p], [s1f, s2f, s3f]):
            sig = np.diag([sp**2, sf**2])
            mO = invA @ sig @ invA.T
            err += float(np.sum((Omg - mO)**2))
        return err

    init = [0.05, 0.05, 0.5, 0.5, 1.0, 1.0, 1.5, 1.5]
    bounds = [(-1.0, 1.0), (-1.0, 1.0)] + [(0.01, 5.0)] * 6
    opt = minimize(gmm, init, method="L-BFGS-B", bounds=bounds)
    lam, alpha = opt.x[0], opt.x[1]
    return {
        "success": bool(opt.success),
        "lambda": float(lam),
        "alpha": float(alpha),
        "Q": float(lam * alpha),
    }


# --------------------------------------------------------------------------
# Asset-Day Worker
# --------------------------------------------------------------------------
def process_asset_day(symbol: str, date: str) -> dict | None:
    df = download_and_preprocess_day(symbol, date)
    if df is None or len(df) < 80000:
        return None

    series = build_series(df, delta=10, window=300)
    x = series["x"].to_numpy()
    f = series["f"].to_numpy()
    if len(x) < 500:
        return None

    # Baseline VAR(1)
    v = var1(x, f)
    # Flow controlled
    c1 = c_flow_controlled(x, f, 1)
    c30 = c_flow_controlled(x, f, 30)
    c90 = c_flow_controlled(x, f, 90)
    q30 = q_long_memory_robust(x, f, 30)

    # C1 Structural fit
    c1_res = fit_structural_c1(x, f, K=3)
    # C2 Rigobon fit
    c2_res = fit_rigobon_c2(x, f)

    return {
        "symbol": symbol,
        "date": date,
        "year": int(date[:4]),
        "month": int(date[5:7]),
        "n_obs": len(x),
        "mean_price": float(np.mean(df["mid"])),
        "J11": float(v["J11"]),
        "J12": float(v["J12"]),
        "J21": float(v["J21"]),
        "J22": float(v["J22"]),
        "Q": float(v["Q"]),
        "S": float(v["S"]),
        "L": float(v["L"]),
        "rho": float(v["rho"]),
        "c1": float(c1),
        "c30": float(c30),
        "c90": float(c90),
        "Q30": float(q30["Q_L"]),
        "c1_structural": c1_res,
        "c2_rigobon": c2_res,
    }


def run_panel(max_workers: int = 8, holdout: bool = True) -> dict:
    dates = get_panel_dates()
    tasks = [(sym, d) for sym in ASSETS for d in dates]
    print(f"Total panel tasks: {len(tasks)} ({len(ASSETS)} assets x {len(dates)} dates)")

    results = []
    completed = 0
    with ThreadPoolExecutor(max_workers=max_workers) as pool:
        futures = {pool.submit(process_asset_day, sym, d): (sym, d) for sym, d in tasks}
        for fut in as_completed(futures):
            sym, d = futures[fut]
            completed += 1
            if completed % 20 == 0 or completed == len(tasks):
                print(f"Progress: {completed}/{len(tasks)} ({(completed/len(tasks))*100:.1f}%)", flush=True)
            res = fut.result()
            if res is not None:
                results.append(res)

    holdout_results = []
    if holdout:
        h_dates = get_holdout_dates()
        print(f"Running holdout for BTCUSDT: {len(h_dates)} dates (Jan 2023)...")
        for hd in h_dates:
            r = process_asset_day("BTCUSDT", hd)
            if r is not None:
                holdout_results.append(r)

    RESULTS_DIR.mkdir(parents=True, exist_ok=True)
    out_file = RESULTS_DIR / "binance_panel_results.json"
    final_payload = {
        "panel_count": len(results),
        "target_count": len(tasks),
        "results": results,
        "holdout_results": holdout_results,
    }
    with open(out_file, "w") as f:
        json.dump(final_payload, f, indent=1)
    print(f"Saved {len(results)} panel results and {len(holdout_results)} holdout results to {out_file}")
    return final_payload


if __name__ == "__main__":
    workers = int(sys.argv[1]) if len(sys.argv) > 1 else 8
    run_panel(max_workers=workers)
