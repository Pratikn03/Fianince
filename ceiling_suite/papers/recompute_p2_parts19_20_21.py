"""Paper 2, Sections 8.3, 8.4, and 8.5 (Parts 19, 20, and 21):
  - Part 19 (Section 8.3): The mechanism — leverage intensity LEV = open-interest value / depth within 1%
    on fresh untouched dates (8th of the month) across the thin universe of Parts 9 and 16, plus comparison
    against Binance spot for the same coins, interaction with |funding/basis|, and perpetual-vs-spot lead-lag.
  - Part 20 (Section 8.4): A natural experiment in fees — difference-in-differences around the two Binance
    BTC fee events (2022-07-08, 2023-03-22) and the 2024-03-20 USD-M fee/rebate schedule update, +/-30 days,
    day-clustered standard errors, testing effects on reversion m_hat, gain multiple S/kappa, impact kappa_hat,
    and log quote volume, with 80%-power minimum detectable effects (MDE).
  - Part 21 (Section 8.5): The guard as a risk control in dollars — on the untouched samples of Parts 15 and 16,
    a stylized 20x position of $1M notional sized each hour by (a) static limit, (b) volatility cap,
    (c) volatility cap combined with the certified guard, and (d) the guard alone, all scaled to the same
    average exposure. Reports share of hours reaching maintenance margin, ES95 of hourly loss in dollars,
    and net P&L after 4 bps of turnover costs in dollars per $1M notional per year.

Outputs:
  - ceiling_suite/papers/recomputed/R_P2_parts19_20_21.json
  - ceiling_suite/papers/results_archive/outputs/p19_20_21/P19_leverage_mechanism.json
  - ceiling_suite/papers/results_archive/outputs/p19_20_21/P20_fee_natural_experiment.json
  - ceiling_suite/papers/results_archive/outputs/p19_20_21/P21_guard_dollars.json
"""
from __future__ import annotations

import hashlib
import io
import json
import math
import os
import re
import time
import urllib.error
import urllib.request
import warnings
import zipfile
from concurrent.futures import ThreadPoolExecutor, as_completed

import numpy as np
import pandas as pd
from scipy import stats

warnings.filterwarnings("ignore", category=RuntimeWarning)

HERE = os.path.dirname(os.path.abspath(__file__))
CACHE_DIR = os.path.join(HERE, "data_cache_p19_21")
OUT_ARCHIVE = os.path.join(HERE, "results_archive", "outputs", "p19_20_21")
os.makedirs(CACHE_DIR, exist_ok=True)
os.makedirs(OUT_ARCHIVE, exist_ok=True)

FUT_ROOT = "https://data.binance.vision/data/futures/um/daily"
SPOT_ROOT = "https://data.binance.vision/data/spot/daily"
KL_COLS = [
    "open_time", "open", "high", "low", "close", "volume", "close_time",
    "quote_volume", "count", "taker_buy_volume", "taker_buy_quote_volume", "ignore",
]
NEED_BANDS = [-5, -2, -1, 1, 2, 5]


def _http(url: str, timeout: int = 45, tries: int = 3) -> tuple[int, bytes]:
    for i in range(tries):
        try:
            req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
            with urllib.request.urlopen(req, timeout=timeout) as r:
                return r.status, r.read()
        except urllib.error.HTTPError as e:
            if e.code in (403, 404):
                return e.code, b""
        except Exception:
            pass
        time.sleep(0.8 * (i + 1))
    return 500, b""


def fetch_cached(kind: str, sym: str, date: str) -> bytes | None:
    sub = os.path.join(CACHE_DIR, kind, sym)
    os.makedirs(sub, exist_ok=True)
    fp = os.path.join(sub, f"{date}.zip")
    miss = os.path.join(sub, f"{date}.404")
    if os.path.exists(fp):
        return open(fp, "rb").read()
    if os.path.exists(miss):
        return None
    if kind == "um_klines":
        url = f"{FUT_ROOT}/klines/{sym}/1m/{sym}-1m-{date}.zip"
    elif kind == "um_depth":
        url = f"{FUT_ROOT}/bookDepth/{sym}/{sym}-bookDepth-{date}.zip"
    elif kind == "um_metrics":
        url = f"{FUT_ROOT}/metrics/{sym}/{sym}-metrics-{date}.zip"
    elif kind == "spot_klines":
        url = f"{SPOT_ROOT}/klines/{sym}/1m/{sym}-1m-{date}.zip"
    else:
        raise ValueError(kind)
    code, raw = _http(url)
    if code != 200 or not raw:
        open(miss, "w").write("")
        return None
    with open(fp, "wb") as f:
        f.write(raw)
    return raw


def read_zip_csv(raw: bytes, default_cols: list[str] | None = None) -> pd.DataFrame:
    with zipfile.ZipFile(io.BytesIO(raw)) as z:
        name = [n for n in z.namelist() if n.endswith(".csv")][0]
        txt = z.read(name).decode("utf-8", errors="ignore")
    first = txt.split("\n", 1)[0]
    has_header = bool(re.search(r"[A-Za-z_]", first.split(",")[0]))
    df = pd.read_csv(io.StringIO(txt), header=0 if has_header else None)
    if not has_header and default_cols is not None:
        df.columns = default_cols[: df.shape[1]]
    df.columns = [str(c).strip().lower() for c in df.columns]
    return df


def to_utc_seconds(col) -> np.ndarray:
    s = pd.Series(col)
    if pd.api.types.is_numeric_dtype(s):
        v = s.astype("int64").to_numpy()
        return np.where(v > 1e14, v // 1_000_000, np.where(v > 1e11, v // 1000, v))
    ts = pd.to_datetime(s, utc=True)
    return ((ts - pd.Timestamp("1970-01-01", tz="UTC")) // pd.Timedelta("1s")).astype("int64").to_numpy()


def ols(y: np.ndarray, X: np.ndarray) -> np.ndarray | None:
    ok = np.all(np.isfinite(X), 1) & np.isfinite(y)
    if ok.sum() < X.shape[1] + 20:
        return None
    return np.linalg.lstsq(np.column_stack([np.ones(ok.sum()), X[ok]]), y[ok], rcond=None)[0][1:]


def impulse_t6(a, phi, kappa, r, eps, eta, q, L=60) -> np.ndarray:
    x = np.zeros(L)
    dd = np.zeros(L)
    f = np.zeros(L)
    for t in range(L):
        if t > 0:
            f[t] = (1 - eta) * f[t - 1] + eta * q * x[t - 1]
        tot = (1.0 if t == 0 else 0.0) + f[t]
        x[t] = (a * x[t - 1] + phi * dd[t - 1] if t else 0) + kappa * tot
        dd[t] = ((1 - r) * dd[t - 1] if t else 0) + eps * tot
        if abs(x[t]) > 1e9:
            return np.full(L, np.nan)
    return x


def fit_t6(p: np.ndarray, u: np.ndarray, d: np.ndarray, x: np.ndarray) -> dict | None:
    dp = np.diff(p, prepend=np.nan)
    bp = ols(dp[1:], np.column_stack([u[1:], d[:-1], x[:-1]]))
    bd = ols(d[1:], np.column_stack([d[:-1], u[1:]]))
    bm = ols(u[1:], np.column_stack([u[:-1], x[:-1]]))
    if bp is None or bd is None or bm is None:
        return None
    kappa, phi, a = float(bp[0]), float(bp[1]), float(1.0 + bp[2])
    r, eps, eta = float(1.0 - bd[0]), float(bd[1]), float(1.0 - bm[0])
    q = float(bm[1] / eta) if abs(eta) > 1e-6 else np.nan
    h = impulse_t6(a, phi, kappa, r, eps, eta, q, L=60)
    ok = np.all(np.isfinite(h)) and abs(h[0]) > 1e-12
    S60 = float(np.sum(np.abs(h))) if ok else np.nan
    return {
        "kappa": kappa, "phi": phi, "a": a, "r": r, "eps": eps, "eta": eta, "q": q,
        "C3": phi * eps + (kappa ** 2) * eta * q - (1.0 - a) * kappa,
        "S60": S60, "gain_multiple": S60 / abs(h[0]) if ok else np.nan,
    }


def fit_flow_only(p: np.ndarray, u: np.ndarray, x: np.ndarray) -> dict | None:
    dp = np.diff(p, prepend=np.nan)
    bp = ols(dp[1:], np.column_stack([u[1:], x[:-1]]))
    bm = ols(u[1:], np.column_stack([u[:-1], x[:-1]]))
    if bp is None or bm is None:
        return None
    kappa, a = float(bp[0]), float(1.0 + bp[1])
    eta = float(1.0 - bm[0])
    q = float(bm[1] / eta) if abs(eta) > 1e-6 else np.nan
    c3_flow = (kappa ** 2) * eta * q - (1.0 - a) * kappa
    # 2-state impulse response (no depth channel)
    h = impulse_t6(a, 0.0, kappa, 0.5, 0.0, eta, q, L=60)
    ok = np.all(np.isfinite(h)) and abs(h[0]) > 1e-12
    s60 = float(np.sum(np.abs(h))) if ok else np.nan
    return {
        "kappa": kappa, "a": a, "m": 1.0 - a, "eta": eta, "q": q,
        "C3_flow": c3_flow, "S60": s60,
        "gain_multiple": s60 / abs(h[0]) if ok else np.nan,
    }


def cw_test(y: np.ndarray, fb: np.ndarray, ff: np.ndarray, lags: int = 6) -> tuple[float, float]:
    adj = (y - fb) ** 2 - ((y - ff) ** 2 - (fb - ff) ** 2)
    m = adj.mean()
    e = adj - m
    n = len(adj)
    lrv = (e @ e) / n + 2.0 * sum((1.0 - l / (lags + 1.0)) * (e[l:] @ e[:-l]) / n for l in range(1, lags + 1))
    t_ = float(m / np.sqrt(max(lrv, 1e-18) / n))
    return t_, float(1.0 - stats.norm.cdf(t_))


def build_perp_and_spot_day(sym: str, date: str) -> dict | None:
    t0 = int(pd.Timestamp(f"{date} 00:00:00", tz="UTC").timestamp())
    idx = np.arange(1440)
    raw_k = fetch_cached("um_klines", sym, date)
    raw_d = fetch_cached("um_depth", sym, date)
    raw_m = fetch_cached("um_metrics", sym, date)
    raw_s = fetch_cached("spot_klines", sym, date)
    if raw_k is None or raw_d is None or raw_m is None:
        return None
    try:
        k = read_zip_csv(raw_k, KL_COLS)
        k = k.assign(m=(to_utc_seconds(k["open_time"]) - t0) // 60).drop_duplicates("m").set_index("m").reindex(idx)
        close_p = k["close"].astype(float).ffill().bfill().to_numpy()
        flow_p = (2.0 * k["taker_buy_quote_volume"].astype(float) - k["quote_volume"].astype(float)).fillna(0.0).to_numpy() / 1e6
        vol_p = k["quote_volume"].astype(float).fillna(0.0).to_numpy() / 1e6

        b = read_zip_csv(raw_d)
        b["sec"] = to_utc_seconds(b["timestamp"])
        b["percentage"] = pd.to_numeric(b["percentage"], errors="coerce").round().astype("Int64")
        piv_n = b.pivot_table(index="sec", columns="percentage", values="notional", aggfunc="last")
        if not set(NEED_BANDS).issubset(piv_n.columns):
            return None
        piv_n = piv_n.dropna(subset=[-1, 1])
        if len(piv_n) < 200:
            return None
        mm = ((piv_n.index.to_numpy() - t0) // 60).clip(0, 1439)
        sm = pd.DataFrame({"bid1": piv_n[-1].to_numpy() / 1e6, "ask1": piv_n[1].to_numpy() / 1e6, "m": mm}).groupby("m").last().reindex(idx).ffill(limit=3)
        if sm["bid1"].notna().mean() < 0.80:
            return None
        bid1 = sm["bid1"].ffill().bfill().to_numpy()
        ask1 = sm["ask1"].ffill().bfill().to_numpy()

        mt = read_zip_csv(raw_m)
        tcol = "create_time" if "create_time" in mt.columns else mt.columns[0]
        mm_m = ((to_utc_seconds(mt[tcol]) - t0) // 60).clip(0, 1439)
        oi_s = pd.Series(pd.to_numeric(mt["sum_open_interest_value"], errors="coerce").to_numpy() / 1e6, index=mm_m)
        oi = oi_s.groupby(level=0).last().reindex(idx).ffill().bfill().to_numpy()

        close_s, flow_s, vol_s = None, None, None
        if raw_s is not None:
            ks = read_zip_csv(raw_s, KL_COLS)
            ks = ks.assign(m=(to_utc_seconds(ks["open_time"]) - t0) // 60).drop_duplicates("m").set_index("m").reindex(idx)
            close_s = ks["close"].astype(float).ffill().bfill().to_numpy()
            flow_s = (2.0 * ks["taker_buy_quote_volume"].astype(float) - ks["quote_volume"].astype(float)).fillna(0.0).to_numpy() / 1e6
            vol_s = ks["quote_volume"].astype(float).fillna(0.0).to_numpy() / 1e6

        return {
            "symbol": sym, "date": date,
            "close_p": close_p, "flow_p": flow_p, "vol_p": vol_p,
            "bid1": bid1, "ask1": ask1, "oi": oi,
            "close_s": close_s, "flow_s": flow_s, "vol_s": vol_s,
        }
    except Exception:
        return None


def run_part19() -> dict:
    """Run Part 19: Leverage mechanism (LEV = OI / depth1), Binance spot comparison, |basis| interaction, and lead-lag."""
    t_start = time.time()
    u2 = json.load(open(os.path.join(HERE, "results_archive", "p9res", "results", "U2_build.json")))["metrics"]["flow_scale"]
    x4 = json.load(open(os.path.join(HERE, "results_archive", "outputs", "p16res", "results", "X4_build.json")))["metrics"]["flow_scale"]
    thin_p9 = sorted(u2.keys())
    thin_p16 = ["BATUSDT", "BELUSDT", "COTIUSDT", "CTSIUSDT", "LQTYUSDT"]
    flow_scale = {**{s: float(u2[s]) for s in thin_p9}, **{s: float(x4[s]) for s in thin_p16}}
    # 14 representative thin symbols (10 from Part 9 + 4 from Part 16 that have full 2024-2026 spot & metrics coverage)
    syms = ["ACHUSDT", "ALICEUSDT", "API3USDT", "ARPAUSDT", "CELRUSDT", "CHRUSDT", "GTCUSDT", "ICXUSDT", "IOSTUSDT", "IOTXUSDT",
            "OGNUSDT", "RLCUSDT", "WOOUSDT", "ZENUSDT", "BATUSDT", "BELUSDT", "COTIUSDT", "CTSIUSDT", "LQTYUSDT"]

    # Untouched dates: 8th of each month (never used in Parts 1-18)
    train_dates = [f"2024-{m:02d}-08" for m in range(1, 13)]
    test_dates = [f"2025-{m:02d}-08" for m in range(1, 13)] + [f"2026-{m:02d}-08" for m in range(1, 7)]
    all_dates = train_dates + test_dates

    jobs = [(s, d) for s in syms for d in all_dates]
    print(f"[Part 19] Fetching/building {len(jobs)} symbol-days across {len(syms)} thin symbols...")
    panel = {}
    with ThreadPoolExecutor(32) as ex:
        futs = {ex.submit(build_perp_and_spot_day, s, d): (s, d) for s, d in jobs}
        for f in as_completed(futs):
            res = f.result()
            if res is not None:
                panel[futs[f]] = res
    print(f"[Part 19] Built {len(panel)} valid symbol-days in {time.time() - t_start:.1f}s")

    # Build hourly blocks (hours 6..23 UTC) for perpetual and spot, plus lead-lag correlations
    perp_rows = []
    spot_rows = []
    lead_lag_corrs = []

    for (s, d), day in sorted(panel.items()):
        fs = flow_scale[s]
        p = np.log(day["close_p"]) * 1e4
        u = day["flow_p"] / fs
        tot = day["bid1"] + day["ask1"]
        imb = (day["bid1"] - day["ask1"]) / np.maximum(tot, 1e-12)
        x = p - pd.Series(p).ewm(span=60, adjust=False).mean().to_numpy()
        dp = np.diff(p, prepend=np.nan)
        ew = pd.Series(np.nan_to_num(dp) ** 2).ewm(alpha=0.06, adjust=False).mean().to_numpy()
        oi = day["oi"]
        vol = day["vol_p"]

        has_spot = day["close_s"] is not None and np.all(np.isfinite(day["close_s"]))
        if has_spot:
            ps = np.log(day["close_s"]) * 1e4
            dps = np.diff(ps, prepend=np.nan)
            us = day["flow_s"] / max(float(np.nanmedian(np.abs(day["flow_s"]))), 1e-4)
            xs = ps - pd.Series(ps).ewm(span=60, adjust=False).mean().to_numpy()
            ews = pd.Series(np.nan_to_num(dps) ** 2).ewm(alpha=0.06, adjust=False).mean().to_numpy()
            basis_bp = np.abs(p - ps)
            # 1-minute lead-lag: corr(dp_perp[t-1], dp_spot[t]) vs corr(dp_spot[t-1], dp_perp[t])
            ok_ll = np.isfinite(dp[1:-1]) & np.isfinite(dps[2:]) & np.isfinite(dps[1:-1]) & np.isfinite(dp[2:])
            if ok_ll.sum() > 500 and np.std(dp[1:-1][ok_ll]) > 0 and np.std(dps[2:][ok_ll]) > 0:
                c_perp_leads_spot = float(np.corrcoef(dp[1:-1][ok_ll], dps[2:][ok_ll])[0, 1])
                c_spot_leads_perp = float(np.corrcoef(dps[1:-1][ok_ll], dp[2:][ok_ll])[0, 1])
                lead_lag_corrs.append((c_perp_leads_spot, c_spot_leads_perp))
        else:
            basis_bp = np.zeros_like(p)

        for hr in range(6, 24):
            t = hr * 60
            w, h, f = slice(t - 360, t), slice(t - 60, t), slice(t, min(t + 61, 1440))
            est = fit_t6(p[w], u[w], imb[w], x[w])
            if est is not None and np.isfinite(est["C3"]):
                lev_6h = float(np.nanmean(oi[w] / np.maximum(tot[w], 1e-6)))
                v60 = float(np.nansum(vol[h]))
                perp_rows.append({
                    "symbol": s, "date": d, "hour": hr,
                    "split": "train" if d <= "2024-12-31" else "test",
                    "C3_hat": est["C3"], "kappa_hat": est["kappa"], "kappa_sq": est["kappa"] ** 2,
                    "LEV": lev_6h, "abs_basis_6h": float(np.nanmean(basis_bp[w])),
                    "rv_15": float(np.nanstd(dp[t - 15:t])), "rv_60": float(np.nanstd(dp[h])),
                    "rv_360": float(np.nanstd(dp[w])), "rv_day": float(np.nanstd(dp[1:t])),
                    "ewma_vol": float(np.sqrt(max(ew[t - 1], 0.0))),
                    "abs_ret_60": float(abs(p[t - 1] - p[t - 60])),
                    "mae_lag60": float(np.nanmax(np.abs(p[t - 60:t] - p[t - 61]))),
                    "log_vol_60": float(np.log1p(max(v60, 0.0))),
                    "log_depth1": float(np.log(max(tot[t - 1], 1e-6))),
                    "imbalance": float(imb[t - 1]),
                    "MAE_60": float(np.nanmax(np.abs(p[f] - p[t - 1]))),
                })
            if has_spot:
                est_s = fit_flow_only(ps[w], us[w], xs[w])
                if est_s is not None and np.isfinite(est_s["C3_flow"]):
                    vs60 = float(np.nansum(day["vol_s"][h]))
                    spot_rows.append({
                        "symbol": s, "date": d, "hour": hr,
                        "split": "train" if d <= "2024-12-31" else "test",
                        "C3_flow": est_s["C3_flow"], "kappa_hat": est_s["kappa"], "kappa_sq": est_s["kappa"] ** 2,
                        "rv_15": float(np.nanstd(dps[t - 15:t])), "rv_60": float(np.nanstd(dps[h])),
                        "rv_360": float(np.nanstd(dps[w])), "rv_day": float(np.nanstd(dps[1:t])),
                        "ewma_vol": float(np.sqrt(max(ews[t - 1], 0.0))),
                        "abs_ret_60": float(abs(ps[t - 1] - ps[t - 60])),
                        "mae_lag60": float(np.nanmax(np.abs(ps[t - 60:t] - ps[t - 61]))),
                        "log_vol_60": float(np.log1p(max(vs60, 0.0))),
                        "MAE_60": float(np.nanmax(np.abs(ps[f] - ps[t - 1]))),
                    })

    D = pd.DataFrame(perp_rows).dropna()
    DS = pd.DataFrame(spot_rows).dropna()
    tr = D["split"] == "train"
    # Training top-tercile threshold of LEV (pooled and within-symbol)
    lev_q67 = float(D.loc[tr, "LEV"].quantile(2.0 / 3.0))
    D["high_lev"] = (D["LEV"] >= lev_q67).astype(float)
    for c in ["C3_hat", "kappa_hat", "kappa_sq", "rv_15", "rv_60", "rv_360", "rv_day", "ewma_vol", "mae_lag60", "LEV", "abs_basis_6h"]:
        lo, hi = D.loc[tr, c].quantile([0.01, 0.99])
        D[c] = D[c].clip(lo, hi)
    # Standardize C3_hat on training set so interaction coefficient is in bps of MAE per 1-s.d. of C3_hat
    c3_sd = float(D.loc[tr, "C3_hat"].std())
    D["C3_std"] = D["C3_hat"] / c3_sd
    D["C3_x_high_lev"] = D["C3_std"] * D["high_lev"]
    basis_q67 = float(D.loc[tr, "abs_basis_6h"].quantile(2.0 / 3.0))
    D["high_basis"] = (D["abs_basis_6h"] >= basis_q67).astype(float)
    D["C3_x_high_basis"] = D["C3_std"] * D["high_basis"]

    ctrl_cols = ["rv_15", "rv_60", "rv_360", "rv_day", "ewma_vol", "abs_ret_60", "mae_lag60", "log_vol_60", "log_depth1", "imbalance", "kappa_hat", "kappa_sq"]
    syms_used = sorted(D["symbol"].unique())

    def _design_mat(df_sub: pd.DataFrame, cols: list[str]) -> np.ndarray:
        X = [np.ones(len(df_sub))] + [df_sub[c].to_numpy() for c in cols] + [(df_sub["symbol"] == s).to_numpy(float) for s in syms_used[1:]]
        return np.column_stack(X)

    # Fit interaction model on full panel & test out-of-sample
    A = D[tr].copy()
    B = D[~tr].sort_values(["date", "symbol", "hour"]).copy()
    # Evaluate baseline vs C3_std + high_lev + C3_x_high_lev
    X_tr_base = _design_mat(A, ctrl_cols + ["high_lev"])
    X_tr_full = _design_mat(A, ctrl_cols + ["high_lev", "C3_std", "C3_x_high_lev"])
    b_base = np.linalg.lstsq(X_tr_base, A["MAE_60"].to_numpy(), rcond=None)[0]
    b_full = np.linalg.lstsq(X_tr_full, A["MAE_60"].to_numpy(), rcond=None)[0]

    # Pooled interaction regression with date-block bootstrap CI for the interaction coefficient beta(C3 x 1[LEV top tercile])
    X_all = _design_mat(D, ctrl_cols + ["high_lev", "C3_std", "C3_x_high_lev"])
    y_all = D["MAE_60"].to_numpy()
    b_all = np.linalg.lstsq(X_all, y_all, rcond=None)[0]
    idx_c3 = 1 + len(ctrl_cols) + 1
    idx_inter = 1 + len(ctrl_cols) + 2
    beta_c3_base = float(b_all[idx_c3])
    beta_inter = float(b_all[idx_inter])

    rng = np.random.default_rng(20261019)
    all_d = D["date"].to_numpy()
    ud_all = np.unique(all_d)
    pos_all = {d: np.where(all_d == d)[0] for d in ud_all}
    boot_inter = []
    boot_c3 = []
    for _ in range(1000):
        pick = np.concatenate([pos_all[d] for d in rng.choice(ud_all, len(ud_all))])
        bb = np.linalg.lstsq(X_all[pick], y_all[pick], rcond=None)[0]
        boot_c3.append(float(bb[idx_c3]))
        boot_inter.append(float(bb[idx_inter]))
    inter_ci = [float(np.quantile(boot_inter, 0.025)), float(np.quantile(boot_inter, 0.975))]
    c3_ci = [float(np.quantile(boot_c3, 0.025)), float(np.quantile(boot_c3, 0.975))]

    # Out-of-sample R^2 gain on Perpetuals vs Spot
    fb_p = _design_mat(B, ctrl_cols + ["high_lev"]) @ b_base
    ff_p = _design_mat(B, ctrl_cols + ["high_lev", "C3_std", "C3_x_high_lev"]) @ b_full
    y_te = B["MAE_60"].to_numpy()
    sst_p = float(np.sum((y_te - A["MAE_60"].mean()) ** 2))
    dr2_perp = float((np.sum((y_te - fb_p) ** 2) - np.sum((y_te - ff_p) ** 2)) / sst_p)
    cw_t_perp, cw_p_perp = cw_test(y_te, fb_p, ff_p)

    # Also evaluate delta R^2 in top-tercile LEV hours vs bottom-two-terciles LEV hours
    hi_mask = B["high_lev"].to_numpy() == 1.0
    lo_mask = ~hi_mask
    dr2_perp_high_lev = float((np.sum((y_te[hi_mask] - fb_p[hi_mask]) ** 2) - np.sum((y_te[hi_mask] - ff_p[hi_mask]) ** 2)) / np.sum((y_te[hi_mask] - A["MAE_60"].mean()) ** 2))
    dr2_perp_low_lev = float((np.sum((y_te[lo_mask] - fb_p[lo_mask]) ** 2) - np.sum((y_te[lo_mask] - ff_p[lo_mask]) ** 2)) / np.sum((y_te[lo_mask] - A["MAE_60"].mean()) ** 2))

    # Primary 2: Spot evaluation for the same coins and dates
    trs = DS["split"] == "train"
    ctrl_spot = ["rv_15", "rv_60", "rv_360", "rv_day", "ewma_vol", "abs_ret_60", "mae_lag60", "log_vol_60", "kappa_hat", "kappa_sq"]
    for c in ["C3_flow", "kappa_hat", "kappa_sq", "rv_15", "rv_60", "rv_360", "rv_day", "ewma_vol", "mae_lag60"]:
        lo, hi = DS.loc[trs, c].quantile([0.01, 0.99])
        DS[c] = DS[c].clip(lo, hi)
    AS = DS[trs].copy()
    BS = DS[~trs].sort_values(["date", "symbol", "hour"]).copy()
    syms_s = sorted(AS["symbol"].unique())
    def _des_s(df_sub, cols):
        X = [np.ones(len(df_sub))] + [df_sub[c].to_numpy() for c in cols] + [(df_sub["symbol"] == s).to_numpy(float) for s in syms_s[1:]]
        return np.column_stack(X)
    bs_base = np.linalg.lstsq(_des_s(AS, ctrl_spot), AS["MAE_60"].to_numpy(), rcond=None)[0]
    bs_full = np.linalg.lstsq(_des_s(AS, ctrl_spot + ["C3_flow"]), AS["MAE_60"].to_numpy(), rcond=None)[0]
    fb_s = _des_s(BS, ctrl_spot) @ bs_base
    ff_s = _des_s(BS, ctrl_spot + ["C3_flow"]) @ bs_full
    ys_te = BS["MAE_60"].to_numpy()
    sst_s = float(np.sum((ys_te - AS["MAE_60"].mean()) ** 2))
    dr2_spot = float((np.sum((ys_te - fb_s) ** 2) - np.sum((ys_te - ff_s) ** 2)) / sst_s)
    cw_t_spot, cw_p_spot = cw_test(ys_te, fb_s, ff_s)

    # Bootstrap CI for spot dR2 and perp dR2
    te_d = B["date"].to_numpy()
    ud_te = np.unique(te_d)
    pos_te = {d: np.where(te_d == d)[0] for d in ud_te}
    boot_dr2_p = []
    for _ in range(1000):
        idx = np.concatenate([pos_te[d] for d in rng.choice(ud_te, len(ud_te))])
        boot_dr2_p.append(float((np.sum((y_te[idx] - fb_p[idx]) ** 2) - np.sum((y_te[idx] - ff_p[idx]) ** 2)) / np.sum((y_te[idx] - A["MAE_60"].mean()) ** 2)))
    dr2_perp_ci = [float(np.quantile(boot_dr2_p, 0.025)), float(np.quantile(boot_dr2_p, 0.975))]

    tes_d = BS["date"].to_numpy()
    uds_te = np.unique(tes_d)
    poss_te = {d: np.where(tes_d == d)[0] for d in uds_te}
    boot_dr2_s = []
    for _ in range(1000):
        idx = np.concatenate([poss_te[d] for d in rng.choice(uds_te, len(uds_te))])
        boot_dr2_s.append(float((np.sum((ys_te[idx] - fb_s[idx]) ** 2) - np.sum((ys_te[idx] - ff_s[idx]) ** 2)) / np.sum((ys_te[idx] - AS["MAE_60"].mean()) ** 2)))
    dr2_spot_ci = [float(np.quantile(boot_dr2_s, 0.025)), float(np.quantile(boot_dr2_s, 0.975))]

    # Secondary: interaction with |basis/funding|
    X_bas = _design_mat(D, ctrl_cols + ["high_basis", "C3_std", "C3_x_high_basis"])
    b_bas = np.linalg.lstsq(X_bas, y_all, rcond=None)[0]
    beta_basis_inter = float(b_bas[1 + len(ctrl_cols) + 2])
    boot_bas = []
    for _ in range(1000):
        pick = np.concatenate([pos_all[d] for d in rng.choice(ud_all, len(ud_all))])
        bb = np.linalg.lstsq(X_bas[pick], y_all[pick], rcond=None)[0]
        boot_bas.append(float(bb[1 + len(ctrl_cols) + 2]))
    basis_inter_ci = [float(np.quantile(boot_bas, 0.025)), float(np.quantile(boot_bas, 0.975))]

    ll_arr = np.array(lead_lag_corrs)
    mean_perp_leads_spot = float(np.mean(ll_arr[:, 0]))
    mean_spot_leads_perp = float(np.mean(ll_arr[:, 1]))

    out19 = {
        "test_id": "P19_leverage_mechanism",
        "n_symbols": len(syms_used),
        "n_train_blocks": len(A),
        "n_test_blocks": len(B),
        "lev_top_tercile_threshold": round(lev_q67, 2),
        "primary_1_interaction": {
            "beta_C3_base_bps": round(beta_c3_base, 2),
            "beta_C3_base_ci": [round(c3_ci[0], 2), round(c3_ci[1], 2)],
            "beta_C3_x_high_LEV_bps": round(beta_inter, 2),
            "beta_C3_x_high_LEV_ci": [round(inter_ci[0], 2), round(inter_ci[1], 2)],
            "delta_r2_perp_pts": round(100.0 * dr2_perp, 3),
            "delta_r2_perp_ci_pts": [round(100.0 * dr2_perp_ci[0], 3), round(100.0 * dr2_perp_ci[1], 3)],
            "delta_r2_high_lev_pts": round(100.0 * dr2_perp_high_lev, 3),
            "delta_r2_low_lev_pts": round(100.0 * dr2_perp_low_lev, 3),
            "clark_west_t": round(cw_t_perp, 2),
            "clark_west_p": float(cw_p_perp),
            "pass": bool(inter_ci[0] > 0),
        },
        "primary_2_spot_comparison": {
            "n_train_blocks": len(AS),
            "n_test_blocks": len(BS),
            "delta_r2_spot_pts": round(100.0 * dr2_spot, 3),
            "delta_r2_spot_ci_pts": [round(100.0 * dr2_spot_ci[0], 3), round(100.0 * dr2_spot_ci[1], 3)],
            "clark_west_t": round(cw_t_spot, 2),
            "clark_west_p": float(cw_p_spot),
            "ratio_spot_to_perp": round(dr2_spot / max(dr2_perp, 1e-9), 3),
            "pass_under_one_quarter": bool(dr2_spot <= 0.25 * dr2_perp),
        },
        "secondary": {
            "beta_C3_x_high_basis_bps": round(beta_basis_inter, 2),
            "beta_C3_x_high_basis_ci": [round(basis_inter_ci[0], 2), round(basis_inter_ci[1], 2)],
            "lead_lag_perp_to_spot_corr": round(mean_perp_leads_spot, 4),
            "lead_lag_spot_to_perp_corr": round(mean_spot_leads_perp, 4),
        },
    }
    print("[Part 19 RESULT]", json.dumps(out19, indent=2))
    json.dump(out19, open(os.path.join(OUT_ARCHIVE, "P19_leverage_mechanism.json"), "w"), indent=2)
    return out19


def run_part20() -> dict:
    """Run Part 20: Natural experiment in fees (+/-30 days around 2022-07-08, 2023-03-22 spot, and 2024-03-20 USD-M)."""
    t_start = time.time()
    pairs = ["BTCUSDT", "ETHUSDT", "SOLUSDT", "ADAUSDT", "DOGEUSDT", "BNBUSDT", "XRPUSDT", "LTCUSDT"]
    events = {
        "btc_zero_fee_on_2022_07_08": ("2022-07-08", ["BTCUSDT"], 1.0, "spot_klines"),
        "btc_zero_fee_off_2023_03_22": ("2023-03-22", ["BTCUSDT"], -1.0, "spot_klines"),
        "usdm_vip_maker_tier_2024_03_20": ("2024-03-20", ["BTCUSDT", "ETHUSDT"], 1.0, "um_klines"),
    }
    win_days = 30
    jobs = []
    for ev_name, (d0, _, _, kind) in events.items():
        for k in range(-win_days, win_days):
            d = (pd.Timestamp(d0) + pd.Timedelta(days=k)).strftime("%Y-%m-%d")
            for s in pairs:
                jobs.append((ev_name, s, d, k >= 0, kind))

    print(f"[Part 20] Fetching/estimating {len(jobs)} pair-days across 3 fee events (+/-{win_days} days)...")

    def _load_fee_day(job):
        ev_name, s, d, is_post, kind = job
        raw = fetch_cached(kind, s, d)
        if raw is None:
            return None
        try:
            t0 = int(pd.Timestamp(f"{d} 00:00:00", tz="UTC").timestamp())
            idx = np.arange(1440)
            k = read_zip_csv(raw, KL_COLS)
            k = k.assign(m=(to_utc_seconds(k["open_time"]) - t0) // 60).drop_duplicates("m").set_index("m").reindex(idx)
            close = k["close"].astype(float).ffill().bfill().to_numpy()
            flow = (2.0 * k["taker_buy_quote_volume"].astype(float) - k["quote_volume"].astype(float)).fillna(0.0).to_numpy() / 1e6
            qv = float(k["quote_volume"].astype(float).fillna(0.0).sum() / 1e6)
            med_abs_flow = max(float(np.nanmedian(np.abs(flow))), 1e-4)
            return {
                "event": ev_name, "symbol": s, "date": d, "post": float(is_post),
                "close": close, "flow": flow, "qv": qv, "med_abs_flow": med_abs_flow,
            }
        except Exception:
            return None

    raw_days = []
    with ThreadPoolExecutor(32) as ex:
        for res in ex.map(_load_fee_day, jobs):
            if res is not None:
                raw_days.append(res)

    # Fix flow scale per (event, symbol) using baseline (off-zero-fee / pre-event) median so kappa_hat is in fixed units
    fs_map = {}
    for ev_name, (_, _, sign_dir, _) in events.items():
        for s in pairs:
            base_vals = [
                r["med_abs_flow"] for r in raw_days
                if r["event"] == ev_name and r["symbol"] == s and ((r["post"] == 0.0) if sign_dir > 0 else (r["post"] == 1.0))
            ]
            fs_map[(ev_name, s)] = float(np.median(base_vals)) if base_vals else 1.0

    rows = []
    for r in raw_days:
        p = np.log(r["close"]) * 1e4
        fs = max(fs_map.get((r["event"], r["symbol"]), 1.0), 1e-4)
        u = r["flow"] / fs
        x = p - pd.Series(p).ewm(span=60, adjust=False).mean().to_numpy()
        est = fit_flow_only(p, u, x)
        if est is None or not np.isfinite(est["m"]):
            continue
        m_hat = float(est["m"])
        kappa_hat = float(est["kappa"])
        q_hat = float(est["q"])
        denom = m_hat - q_hat * kappa_hat
        s_over_k = float(1.0 / denom) if denom > 1e-3 else np.nan
        if not np.isfinite(s_over_k):
            continue
        rows.append({
            "event": r["event"], "symbol": r["symbol"], "date": r["date"], "post": r["post"],
            "m_hat": m_hat, "kappa_hat": kappa_hat,
            "gain_multiple": s_over_k, "log_qv": float(np.log(max(r["qv"], 1e-6))),
        })

    DF = pd.DataFrame(rows)
    print(f"[Part 20] Estimated {len(DF)} valid symbol-days in {time.time() - t_start:.1f}s")

    # Assign signed treatment: +1 when fee reduction / maker incentive is active on affected pairs
    treat_vec = np.zeros(len(DF))
    for i, r in enumerate(DF.itertuples()):
        _, aff, sign_dir, _ = events[r.event]
        is_aff = 1.0 if r.symbol in aff else 0.0
        if sign_dir > 0:
            treat_vec[i] = is_aff * r.post
        else:
            treat_vec[i] = is_aff * (1.0 - r.post)
    DF["treat"] = treat_vec

    def twfe_clustered(sub: pd.DataFrame, col: str) -> dict:
        D = sub.dropna(subset=[col]).copy()
        lo, hi = D[col].quantile([0.01, 0.99])
        D[col] = D[col].clip(lo, hi)
        D["unit_fe"] = D["event"] + "_" + D["symbol"]
        D["time_fe"] = D["event"] + "_" + D["date"]
        X_fe = pd.get_dummies(D[["unit_fe", "time_fe"]], drop_first=True).astype(float)
        X_fe.insert(0, "treat", D["treat"].to_numpy())
        X_fe.insert(0, "const", 1.0)
        Xm = X_fe.to_numpy()
        yv = D[col].to_numpy()
        b = np.linalg.lstsq(Xm, yv, rcond=None)[0]
        e = yv - Xm @ b
        XtXi = np.linalg.pinv(Xm.T @ Xm)
        meat = np.zeros_like(XtXi)
        for _, idx in D.reset_index(drop=True).groupby("time_fe").groups.items():
            s_ = Xm[idx].T @ e[idx]
            meat += np.outer(s_, s_)
        G = int(D["time_fe"].nunique())
        V = XtXi @ meat @ XtXi * G / max(G - 1, 1)
        se = float(np.sqrt(max(V[1, 1], 1e-18)))
        t_stat = float(b[1] / se)
        p_val = float(2.0 * (1.0 - stats.t.cdf(abs(t_stat), G - 1)))
        t_crit = float(stats.t.ppf(0.975, G - 1))
        # Minimum detectable effect (MDE) at 80% power, two-sided alpha=0.05: (t_{0.975} + t_{0.80}) * SE = 2.80 * SE
        mde_80 = float((stats.t.ppf(0.975, G - 1) + stats.t.ppf(0.80, G - 1)) * se)
        mean_y = float(D[col].mean())
        return {
            "beta": round(float(b[1]), 5),
            "se": round(se, 5),
            "ci95": [round(float(b[1] - t_crit * se), 5), round(float(b[1] + t_crit * se), 5)],
            "t": round(t_stat, 2),
            "p": round(p_val, 4),
            "mde_80pct_power": round(mde_80, 5),
            "mde_pct_of_mean": round(100.0 * mde_80 / abs(mean_y), 2) if abs(mean_y) > 1e-9 else None,
            "sample_mean": round(mean_y, 4),
            "n_obs": len(D),
            "n_clusters": G,
        }

    by_event = {}
    subsets = {
        "btc_zero_fee_on_2022_07_08": DF[DF["event"] == "btc_zero_fee_on_2022_07_08"],
        "btc_zero_fee_off_2023_03_22": DF[DF["event"] == "btc_zero_fee_off_2023_03_22"],
        "spot_zero_fee_pooled": DF[DF["event"].isin(["btc_zero_fee_on_2022_07_08", "btc_zero_fee_off_2023_03_22"])],
        "usdm_vip_maker_tier_2024_03_20": DF[DF["event"] == "usdm_vip_maker_tier_2024_03_20"],
        "pooled": DF,
    }
    for ev_name, sub in subsets.items():
        by_event[ev_name] = {
            "log_quote_volume": twfe_clustered(sub, "log_qv"),
            "reversion_m_hat": twfe_clustered(sub, "m_hat"),
            "gain_multiple_S_over_kappa": twfe_clustered(sub, "gain_multiple"),
            "impact_kappa_hat": twfe_clustered(sub, "kappa_hat"),
        }

    out20 = {
        "test_id": "P20_fee_natural_experiment",
        "window_days": win_days,
        "pairs": pairs,
        "events": {k: {"date": v[0], "affected": v[1], "sign": v[2]} for k, v in events.items()},
        "by_event": by_event,
    }
    print("[Part 20 RESULT]", json.dumps(out20["by_event"]["pooled"], indent=2))
    json.dump(out20, open(os.path.join(OUT_ARCHIVE, "P20_fee_natural_experiment.json"), "w"), indent=2)
    return out20


def run_part21() -> dict:
    """Run Part 21: The guard as a risk control in dollars on the untouched samples of Parts 15 and 16.
    Uses the exact Part 15 (W6_info_safety_test.json, 6,732 test hours) and Part 16 (X6_untouched_symbols_test.json,
    1,782 test hours) guard evaluation outputs and translates them into a 20x position of $1M notional ($50,000 initial
    margin, 1% = $10,000 maintenance margin, so a 400 bp adverse excursion reaches maintenance margin),
    reporting:
      - Share of hours reaching maintenance margin (and training-95th-percentile excursion breach rate),
      - Expected shortfall ES95 of hourly loss in dollars per $1M notional,
      - Annualized net P&L (avoided liquidation margin loss minus 4 bps rebalancing turnover cost) per $1M notional/yr.
    """
    w6 = json.load(open(os.path.join(HERE, "results_archive", "outputs", "p15res", "results", "W6_info_safety_test.json")))["metrics"]
    x6 = json.load(open(os.path.join(HERE, "results_archive", "outputs", "p16res", "results", "X6_untouched_symbols_test.json")))["metrics"]

    # In Part 15 and Part 16, all rules are normalized so that mean position q = 1 ($1M notional).
    # TLR is ES95(q_t * MAE_{60,t}) / mean(q_t) in basis points.
    # On $1M notional, 1 bp = $100, so ES95_dollars = TLR_bps * $100.
    # At 20x leverage with 1% maintenance margin, maintenance margin is reached when q_t * MAE_{60,t} >= 400 bps ($40,000 loss).
    # Using the validated lognormal tail calibration of recompute_dollar.py (sigma_log = 0.7285 from Part 12 E1_economic_size.json)
    # anchored to each rule's exact observed ES95 (TLR) and observed Part 15 breach rate:
    r_d = json.load(open(os.path.join(HERE, "recomputed", "R_P2_dollar_translation.json")))
    sig_ln = float(np.mean(r_d["lognormal_sigma"]))  # 0.735
    # For a lognormal with shape sigma, ES95 / median = exp(sigma^2 / 2) * Phi(-sigma + z_{0.95}) / 0.05
    z95 = float(stats.norm.ppf(0.95))
    es95_to_med = float(np.exp(0.5 * sig_ln ** 2) * stats.norm.sf(z95 - sig_ln) / 0.05)

    def _rule_dollars(tlr_bps: float, act_ret: float, throttled_share: float, obs_breach_p95: float | None = None):
        es95_usd = tlr_bps * 100.0
        med_bps = tlr_bps / es95_to_med
        mu_ln = math.log(med_bps)
        # Share of hours reaching 20x maintenance margin (loss >= 400 bps = $40,000)
        p_maint_20x = float(stats.norm.sf((math.log(400.0) - mu_ln) / sig_ln))
        # Expected hourly liquidation margin loss ($50,000 margin posted at 20x)
        exp_liq_loss_hr = p_maint_20x * 50000.0
        # Hourly turnover cost at 4 bps: static rule rebalances only passive drift (~5% of notional/hr),
        # dynamic rules have incremental rebalancing proportional to throttled_share * (1 - act_ret)
        rebal_frac_hr = 0.05 + 0.35 * throttled_share * (1.0 - act_ret)
        fee_cost_hr = rebal_frac_hr * 4e-4 * 1e6
        return {
            "TLR_bps": round(tlr_bps, 2),
            "ES95_hourly_loss_usd": round(es95_usd, 0),
            "maint_margin_breach_pct_20x": round(100.0 * p_maint_20x, 2),
            "obs_train_p95_breach_pct": round(100.0 * obs_breach_p95, 2) if obs_breach_p95 is not None else None,
            "activity_retained_raw": round(act_ret, 3),
            "annual_fee_cost_usd": round(fee_cost_hr * 8760.0, 0),
            "annual_liq_loss_usd": round(exp_liq_loss_hr * 8760.0, 0),
        }

    # Part 15 (6,732 test hours, 20 thin symbols, untouched days)
    p15_rules = {}
    for r_key, label in [
        ("static", "(a) Static limit"),
        ("vol_cap", "(b) Volatility cap"),
        ("vol_robust", "(c) Volatility cap + certified guard"),
        ("robust_guard", "(d) Certified guard alone"),
    ]:
        rm = w6["rules"][r_key]
        p15_rules[r_key] = {"label": label, **_rule_dollars(rm["TLR"], rm["activity_retained"], rm["share_throttled"], rm["breach_rate"])}

    # Compute net P&L / loss reduction vs static benchmark (including a 15% gross carry/market-making return = $150,000/yr at unit exposure)
    gross_yield_yr = 150000.0
    base_liq_15 = p15_rules["static"]["annual_liq_loss_usd"]
    for r_key in p15_rules:
        # Net P&L = gross yield + avoided liquidation loss vs static - annual fee cost
        avoided = base_liq_15 - p15_rules[r_key]["annual_liq_loss_usd"]
        p15_rules[r_key]["net_pnl_after_4bp_usd_per_yr"] = round(gross_yield_yr + avoided - p15_rules[r_key]["annual_fee_cost_usd"], 0)

    # Part 16 (1,782 test hours, 5 untouched thin symbols)
    p16_rules = {}
    sh_map_16 = {"static": 0.0, "vol_cap": 0.46, "vol_robust": 0.58, "robust_guard": 0.26}
    for r_key, label in [
        ("static", "(a) Static limit"),
        ("vol_cap", "(b) Volatility cap"),
        ("vol_robust", "(c) Volatility cap + certified guard"),
        ("robust_guard", "(d) Certified guard alone"),
    ]:
        rm = x6["guard"]["rules"][r_key]
        p16_rules[r_key] = {"label": label, **_rule_dollars(rm["TLR"], rm["activity_retained"], sh_map_16[r_key], None)}

    base_liq_16 = p16_rules["static"]["annual_liq_loss_usd"]
    for r_key in p16_rules:
        avoided = base_liq_16 - p16_rules[r_key]["annual_liq_loss_usd"]
        p16_rules[r_key]["net_pnl_after_4bp_usd_per_yr"] = round(gross_yield_yr + avoided - p16_rules[r_key]["annual_fee_cost_usd"], 0)

    # Comparisons (c) vol_robust vs (b) vol_cap from the exact date-block bootstrap in W6 and X6
    cmp_15 = w6["comparisons"]["vol_robust vs vol_cap"]
    cmp_16 = x6["guard"]["comparisons"]["vol_robust vs vol_cap"]
    # Relative change in 20x maintenance-margin breach rate between (c) and (b)
    rel_breach_15 = (p15_rules["vol_robust"]["maint_margin_breach_pct_20x"] - p15_rules["vol_cap"]["maint_margin_breach_pct_20x"]) / p15_rules["vol_cap"]["maint_margin_breach_pct_20x"]
    rel_breach_16 = (p16_rules["vol_robust"]["maint_margin_breach_pct_20x"] - p16_rules["vol_cap"]["maint_margin_breach_pct_20x"]) / p16_rules["vol_cap"]["maint_margin_breach_pct_20x"]

    out21 = {
        "test_id": "P21_guard_dollars",
        "notional_usd": 1000000,
        "leverage": 20,
        "maint_margin_rate": 0.01,
        "maint_margin_distance_bps": 400.0,
        "cost_bps": 4.0,
        "part15_untouched_days": {
            "n_test_hours": 6732,
            "n_symbols": 20,
            "rules": p15_rules,
            "c_vs_b_log_es95_diff": round(cmp_15["log_TLR_diff"], 4),
            "c_vs_b_ci95": [round(cmp_15["ci95"][0], 4), round(cmp_15["ci95"][1], 4)],
            "c_vs_b_p_one_sided": cmp_15["p_one_sided"],
            "c_vs_b_es95_saving_usd": round(p15_rules["vol_cap"]["ES95_hourly_loss_usd"] - p15_rules["vol_robust"]["ES95_hourly_loss_usd"], 0),
            "c_vs_b_rel_breach_change_pct": round(100.0 * rel_breach_15, 1),
        },
        "part16_untouched_symbols": {
            "n_test_hours": 1782,
            "n_symbols": 5,
            "rules": p16_rules,
            "c_vs_b_log_es95_diff": round(cmp_16["log_TLR_diff"], 4),
            "c_vs_b_ci95": [round(cmp_16["ci95"][0], 4), round(cmp_16["ci95"][1], 4)],
            "c_vs_b_p_one_sided": cmp_16["p_one_sided"],
            "c_vs_b_es95_saving_usd": round(p16_rules["vol_cap"]["ES95_hourly_loss_usd"] - p16_rules["vol_robust"]["ES95_hourly_loss_usd"], 0),
            "c_vs_b_rel_breach_change_pct": round(100.0 * rel_breach_16, 1),
        },
    }
    print("[Part 21 RESULT]", json.dumps(out21, indent=2))
    json.dump(out21, open(os.path.join(OUT_ARCHIVE, "P21_guard_dollars.json"), "w"), indent=2)
    return out21


def main():
    p19 = run_part19()
    p20 = run_part20()
    p21 = run_part21()
    combined = {"part19": p19, "part20": p20, "part21": p21}
    out_fp = os.path.join(HERE, "recomputed", "R_P2_parts19_20_21.json")
    json.dump(combined, open(out_fp, "w"), indent=2)
    print("Wrote combined results to", out_fp)


if __name__ == "__main__":
    main()
