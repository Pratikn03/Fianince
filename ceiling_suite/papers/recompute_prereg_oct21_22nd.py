"""Execute the three pre-registered empirical tests on untouched 22nd-of-month dates (commit 2cce9fb):
  1. Paper 1 Section 8.3 (P1_disclosure_oos): Out-of-sample predictive test of class-tagged memory
     estimates vs price-only memory estimates for 30-minute post-shock cumulative price responses.
  2. Paper 2 Part 22 (P22_liquidation_mechanism, Gate A): Pre-registered test of whether 6-hour C3_hat
     forecasts next-hour liquidation intensity beyond the Part 9 volatility + impact baseline, and
     whether realized liquidation intensity mediates >= 50% of C3_hat's excursion forecasting gain.
  3. Paper 2 Part 23 (P23_guard_capacity): Pre-registered non-resetting 20x leveraged position capacity
     test on the 22nd-of-month dates (how much more dollar notional the volatility cap + certified guard
     can hold than the volatility cap alone at the exact same out-of-sample liquidation rate).
"""
from __future__ import annotations

import hashlib
import json
import os
import time
from concurrent.futures import ThreadPoolExecutor, as_completed

import numpy as np
import pandas as pd
from scipy import stats

from recompute_p2_parts19_20_21 import (
    HERE,
    KL_COLS,
    NEED_BANDS,
    cw_test,
    fetch_cached,
    fit_flow_only,
    fit_t6,
    impulse_t6,
    read_zip_csv,
    to_utc_seconds,
)

SYMS_19 = [
    "ACHUSDT", "ALICEUSDT", "API3USDT", "ARPAUSDT", "CELRUSDT",
    "CHRUSDT", "GTCUSDT", "ICXUSDT", "IOSTUSDT", "IOTXUSDT",
    "OGNUSDT", "RLCUSDT", "WOOUSDT", "ZENUSDT", "BATUSDT",
    "BELUSDT", "COTIUSDT", "CTSIUSDT", "LQTYUSDT",
]

TRAIN_DATES_22 = [f"2024-{m:02d}-22" for m in range(1, 13)]
TEST_DATES_22 = [f"2025-{m:02d}-22" for m in range(1, 13)] + [f"2026-{m:02d}-22" for m in range(1, 10)]
ALL_DATES_22 = TRAIN_DATES_22 + TEST_DATES_22


def build_day_22(sym: str, date: str) -> dict | None:
    """Load and validate 1-minute klines, 1% bookDepth, and 5-minute metrics (OI + class ratios) for (sym, date)."""
    t0 = int(pd.Timestamp(f"{date} 00:00:00", tz="UTC").timestamp())
    idx_1m = np.arange(1440)
    idx_5m = np.arange(288)
    raw_k = fetch_cached("um_klines", sym, date)
    raw_d = fetch_cached("um_depth", sym, date)
    raw_m = fetch_cached("um_metrics", sym, date)
    if raw_k is None or raw_d is None or raw_m is None:
        return None
    try:
        k = read_zip_csv(raw_k, KL_COLS)
        k = k.assign(m=(to_utc_seconds(k["open_time"]) - t0) // 60).drop_duplicates("m").set_index("m").reindex(idx_1m)
        close_1m = k["close"].astype(float).ffill().bfill().to_numpy()
        flow_1m = (2.0 * k["taker_buy_quote_volume"].astype(float) - k["quote_volume"].astype(float)).fillna(0.0).to_numpy() / 1e6
        vol_1m = k["quote_volume"].astype(float).fillna(0.0).to_numpy() / 1e6

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
        sm = pd.DataFrame({"bid1": piv_n[-1].to_numpy() / 1e6, "ask1": piv_n[1].to_numpy() / 1e6, "m": mm}).groupby("m").last().reindex(idx_1m).ffill(limit=3)
        if sm["bid1"].notna().mean() < 0.80:
            return None
        bid1 = sm["bid1"].ffill().bfill().to_numpy()
        ask1 = sm["ask1"].ffill().bfill().to_numpy()

        mt = read_zip_csv(raw_m)
        tcol = "create_time" if "create_time" in mt.columns else mt.columns[0]
        m5_idx = ((to_utc_seconds(mt[tcol]) - t0) // 300).clip(0, 287)
        mt = mt.assign(b5=m5_idx).drop_duplicates("b5").set_index("b5").reindex(idx_5m)

        # 5-minute open interest in contracts and USD value
        oi_contracts_5m = pd.to_numeric(mt["sum_open_interest"], errors="coerce").ffill().bfill().to_numpy()
        oi_val_5m = pd.to_numeric(mt["sum_open_interest_value"], errors="coerce").ffill().bfill().to_numpy() / 1e6

        # 5-minute trader-class long/short ratios: R -> net position n = (R - 1) / (R + 1)
        r_top = pd.to_numeric(mt.get("sum_toptrader_long_short_ratio", mt.get("topLongShortPositionRatio")), errors="coerce").ffill().bfill().to_numpy()
        r_all = pd.to_numeric(mt.get("count_long_short_ratio"), errors="coerce").ffill().bfill().to_numpy()
        n_top_5m = (r_top - 1.0) / np.maximum(r_top + 1.0, 1e-6)
        n_all_5m = (r_all - 1.0) / np.maximum(r_all + 1.0, 1e-6)

        return {
            "symbol": sym,
            "date": date,
            "close_1m": close_1m,
            "flow_1m": flow_1m,
            "vol_1m": vol_1m,
            "bid1": bid1,
            "ask1": ask1,
            "oi_contracts_5m": oi_contracts_5m,
            "oi_val_5m": oi_val_5m,
            "n_top_5m": n_top_5m,
            "n_all_5m": n_all_5m,
        }
    except Exception:
        return None


def mark_unlock(rel_unlock_path: str):
    fp = os.path.join(HERE, "results_archive", "outputs", rel_unlock_path)
    if os.path.exists(fp):
        obj = json.load(open(fp))
        obj["n"] = int(obj.get("n", 0)) + 1
        obj["utc_unlocked"] = time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())
        obj["status"] = "evaluated_once"
        json.dump(obj, open(fp, "w"), indent=2)


def run_p1_disclosure_oos(panel: dict, flow_scale: dict) -> dict:
    """Paper 1 Step 4: Out-of-sample disclosure test on the 22nd of each month."""
    mark_unlock("p1_disc_oos_res/prereg/P1_disclosure_oos_unlocks.json")

    # Step 1: Build 5-minute bars per symbol-day
    by_sym_train = {s: [] for s in SYMS_19}
    by_sym_test = {s: [] for s in SYMS_19}

    for (s, d), day in sorted(panel.items()):
        fs = flow_scale[s]
        c1 = day["close_1m"]
        f1 = day["flow_1m"] / fs
        # Aggregate to 288 5-minute bars
        c5 = c1[4::5]
        p5 = np.log(c5) * 1e4
        ret5 = np.diff(p5, prepend=p5[0])
        q5 = f1.reshape(288, 5).sum(axis=1)
        ntop = day["n_top_5m"] * 1e4  # in bp scale
        nall = day["n_all_5m"] * 1e4
        if not (np.all(np.isfinite(ntop)) and np.all(np.isfinite(nall))):
            continue
        rec = {"date": d, "p5": p5, "ret5": ret5, "q5": q5, "ntop": ntop, "nall": nall}
        if d <= "2024-12-31":
            by_sym_train[s].append(rec)
        else:
            by_sym_test[s].append(rec)

    # Per symbol on 2024 training days:
    # (a) Estimate class-tagged memory rates r_top, w_top and r_all, w_all from n_{c,t} = alpha + r_c n_{c,t-1} + w_c ret_t
    # (b) Estimate price-only 12-lag flow kernel q_t ~ sum_{k=1}^{12} b_k ret_{t-k} and fit two-exponential memory states
    # (c) Collect top-decile flow shock events (|q_t| >= 90th percentile of training |q_t|) at bars t in [12, 280]
    shock_rows = []
    sym_mem_stats = {}

    for s in SYMS_19:
        tr_days = by_sym_train[s]
        te_days = by_sym_test[s]
        if len(tr_days) < 5 or len(te_days) < 5:
            continue

        # Fit class-tagged ARX on training days
        nt_prev = np.concatenate([d["ntop"][:-1] for d in tr_days])
        nt_curr = np.concatenate([d["ntop"][1:] for d in tr_days])
        na_prev = np.concatenate([d["nall"][:-1] for d in tr_days])
        na_curr = np.concatenate([d["nall"][1:] for d in tr_days])
        rt_curr = np.concatenate([d["ret5"][1:] for d in tr_days])
        q_all_tr = np.concatenate([d["q5"][12:281] for d in tr_days])
        q_thr = float(np.quantile(np.abs(q_all_tr), 0.90))

        X_top = np.column_stack([np.ones_like(nt_prev), nt_prev, rt_curr])
        b_top = np.linalg.lstsq(X_top, nt_curr, rcond=None)[0]
        r_top_hat = float(np.clip(b_top[1], 0.50, 0.999))
        w_top_hat = float(b_top[2])

        X_all = np.column_stack([np.ones_like(na_prev), na_prev, rt_curr])
        b_all = np.linalg.lstsq(X_all, na_curr, rcond=None)[0]
        r_all_hat = float(np.clip(b_all[1], 0.50, 0.999))
        w_all_hat = float(b_all[2])

        # Fit price-only 12-lag kernel on training days: q_t on ret_{t-1..t-12}
        Y_q, X_lags = [], []
        for d in tr_days:
            for t in range(12, 281):
                Y_q.append(d["q5"][t])
                X_lags.append(d["ret5"][t - 12:t][::-1])
        X_lags = np.asarray(X_lags)
        Y_q = np.asarray(Y_q)
        b_kern = np.linalg.lstsq(np.column_stack([np.ones(len(Y_q)), X_lags]), Y_q, rcond=None)[0][1:]

        # Two-exponential basis on lags 1..12 fitted to b_kern on training set (grid search over 0.50 <= r_fast < r_slow <= 0.99)
        r_grid = np.linspace(0.55, 0.99, 23)
        lags_12 = np.arange(1, 13, dtype=float)
        best_err = np.inf
        r_p1, r_p2 = 0.75, 0.95
        for i1 in range(len(r_grid)):
            for i2 in range(i1 + 1, len(r_grid)):
                B_exp = np.column_stack([r_grid[i1] ** lags_12, r_grid[i2] ** lags_12])
                w_exp = np.linalg.lstsq(B_exp, b_kern, rcond=None)[0]
                err = float(np.sum((b_kern - B_exp @ w_exp) ** 2))
                if err < best_err:
                    best_err = err
                    r_p1, r_p2 = float(r_grid[i1]), float(r_grid[i2])

        sym_mem_stats[s] = {
            "r_top_hat": round(r_top_hat, 4),
            "r_all_hat": round(r_all_hat, 4),
            "r_price_1": round(r_p1, 4),
            "r_price_2": round(r_p2, 4),
            "q90_threshold": round(q_thr, 4),
        }

        for split_name, day_list in (("train", tr_days), ("test", te_days)):
            for d in day_list:
                ret5 = d["ret5"]
                q5 = d["q5"]
                p5 = d["p5"]
                ntop = d["ntop"]
                nall = d["nall"]
                # Construct recursive price-only memory states y_{p1,t}, y_{p2,t} from returns and flow
                yp1 = np.zeros(288)
                yp2 = np.zeros(288)
                for t in range(1, 288):
                    yp1[t] = r_p1 * yp1[t - 1] + (1.0 - r_p1) * ret5[t]
                    yp2[t] = r_p2 * yp2[t - 1] + (1.0 - r_p2) * ret5[t]
                for t in range(12, 281):
                    if abs(q5[t]) < q_thr:
                        continue
                    # Cumulative 30-minute post-shock price response (bars t+1..t+6)
                    dp_30m = float(p5[t + 6] - p5[t])
                    # Class-tagged memory state signals at shock time t
                    d_ntop = float(ntop[t] - r_top_hat * ntop[t - 1])
                    d_nall = float(nall[t] - r_all_hat * nall[t - 1])
                    shock_rows.append({
                        "symbol": s,
                        "date": d["date"],
                        "split": split_name,
                        "dp_30m": dp_30m,
                        "abs_dp_30m": abs(dp_30m),
                        "q_shock": float(q5[t]),
                        "ret_shock": float(ret5[t]),
                        "yp1": float(yp1[t]),
                        "yp2": float(yp2[t]),
                        "q_lag1": float(q5[t - 1]),
                        "ntop_level": float(ntop[t]),
                        "nall_level": float(nall[t]),
                        "d_ntop": d_ntop,
                        "d_nall": d_nall,
                    })

    DF = pd.DataFrame(shock_rows).dropna()
    tr = DF["split"] == "train"
    for c in ["dp_30m", "q_shock", "ret_shock", "yp1", "yp2", "q_lag1", "ntop_level", "nall_level", "d_ntop", "d_nall"]:
        lo, hi = DF.loc[tr, c].quantile([0.01, 0.99])
        DF[c] = DF[c].clip(lo, hi)

    A = DF[tr].copy()
    B = DF[~tr].sort_values(["date", "symbol"]).copy()
    syms_u = sorted(A["symbol"].unique())

    def _X(df_sub: pd.DataFrame, cols: list[str]) -> np.ndarray:
        mats = [np.ones(len(df_sub))] + [df_sub[c].to_numpy() for c in cols] + [(df_sub["symbol"] == s).to_numpy(float) for s in syms_u[1:]]
        return np.column_stack(mats)

    base_cols = ["q_shock", "ret_shock"]
    price_mem_cols = base_cols + ["yp1", "yp2", "q_lag1"]
    tagged_mem_cols = base_cols + ["ntop_level", "nall_level", "d_ntop", "d_nall"]

    y_tr = A["dp_30m"].to_numpy()
    y_te = B["dp_30m"].to_numpy()
    sst = float(np.sum((y_te - y_tr.mean()) ** 2))

    b_base = np.linalg.lstsq(_X(A, base_cols), y_tr, rcond=None)[0]
    b_price = np.linalg.lstsq(_X(A, price_mem_cols), y_tr, rcond=None)[0]
    b_tag = np.linalg.lstsq(_X(A, tagged_mem_cols), y_tr, rcond=None)[0]

    f_base = _X(B, base_cols) @ b_base
    f_price = _X(B, price_mem_cols) @ b_price
    f_tag = _X(B, tagged_mem_cols) @ b_tag

    dr2_price_vs_base = float((np.sum((y_te - f_base) ** 2) - np.sum((y_te - f_price) ** 2)) / sst)
    dr2_tag_vs_base = float((np.sum((y_te - f_base) ** 2) - np.sum((y_te - f_tag) ** 2)) / sst)
    dr2_tag_vs_price = float((np.sum((y_te - f_price) ** 2) - np.sum((y_te - f_tag) ** 2)) / sst)
    cw_t, cw_p = cw_test(y_te, f_price, f_tag)

    rng = np.random.default_rng(20261021)
    te_dates = B["date"].to_numpy()
    ud = np.unique(te_dates)
    pos = {d: np.where(te_dates == d)[0] for d in ud}
    boot_diff = []
    for _ in range(2000):
        idx = np.concatenate([pos[d] for d in rng.choice(ud, len(ud))])
        s_draw = float(np.sum((y_te[idx] - y_tr.mean()) ** 2))
        boot_diff.append(100.0 * float((np.sum((y_te[idx] - f_price[idx]) ** 2) - np.sum((y_te[idx] - f_tag[idx]) ** 2)) / s_draw))
    ci_diff = [float(np.quantile(boot_diff, 0.025)), float(np.quantile(boot_diff, 0.975))]

    out = {
        "test_id": "P1_disclosure_oos",
        "spec_sha256": "f0182ce509789cd57a1a6bffe0ba4e89a5fe67905e4d0a247f3b9b8ca1e52415",
        "n_symbols": len(syms_u),
        "n_train_shocks": len(A),
        "n_test_shocks": len(B),
        "delta_r2_price_only_vs_base_pts": round(100.0 * dr2_price_vs_base, 3),
        "delta_r2_tagged_vs_base_pts": round(100.0 * dr2_tag_vs_base, 3),
        "delta_r2_tagged_vs_price_only_pts": round(100.0 * dr2_tag_vs_price, 3),
        "delta_r2_tagged_vs_price_only_ci_pts": [round(ci_diff[0], 3), round(ci_diff[1], 3)],
        "clark_west_t": round(cw_t, 2),
        "clark_west_p": round(cw_p, 4),
        "pass": bool(dr2_tag_vs_price > 0 and cw_p < 0.05 and ci_diff[0] > 0),
        "symbol_memory_estimates": sym_mem_stats,
    }
    print("[Paper 1 Step 4: Disclosure OOS Result]", json.dumps({k: v for k, v in out.items() if k != "symbol_memory_estimates"}, indent=2))
    os.makedirs(os.path.join(HERE, "results_archive", "outputs", "p1_disc_oos_res"), exist_ok=True)
    json.dump(out, open(os.path.join(HERE, "results_archive", "outputs", "p1_disc_oos_res", "P1_disclosure_oos_results.json"), "w"), indent=2)
    json.dump(out, open(os.path.join(HERE, "recomputed", "R_P1_disclosure_oos.json"), "w"), indent=2)
    return out


def run_p22_and_p23(panel: dict, flow_scale: dict) -> tuple[dict, dict]:
    """Paper 2 Part 22 (liquidation mechanism test, Gate A) and Part 23 (non-resetting guard capacity test)."""
    mark_unlock("p22res/prereg/P22_liquidation_mechanism_unlocks.json")
    mark_unlock("p23res/prereg/P23_guard_capacity_unlocks.json")

    hourly_rows = []
    daily_pos_rows = []

    for (s, d), day in sorted(panel.items()):
        fs = flow_scale[s]
        p = np.log(day["close_1m"]) * 1e4
        u = day["flow_1m"] / fs
        vol = day["vol_1m"]
        tot = day["bid1"] + day["ask1"]
        imb = (day["bid1"] - day["ask1"]) / np.maximum(tot, 1e-12)
        x = p - pd.Series(p).ewm(span=60, adjust=False).mean().to_numpy()
        dp = np.diff(p, prepend=np.nan)
        ew = pd.Series(np.nan_to_num(dp) ** 2).ewm(alpha=0.06, adjust=False).mean().to_numpy()

        # 5-minute returns and OI contractions
        p5 = p[4::5]
        dp5 = np.diff(p5, prepend=p5[0])
        med_abs_dp5 = float(np.nanmedian(np.abs(dp5)))
        oi_c = np.maximum(day["oi_contracts_5m"], 1e-6)
        dlog_oi = np.diff(np.log(oi_c), prepend=np.log(oi_c[0]))
        oi_drop_bp = np.maximum(0.0, -dlog_oi) * 1e4
        oi_drop_adverse_bp = oi_drop_bp * (np.abs(dp5) > med_abs_dp5).astype(float)

        # Part 22: Hourly observations for hours 6..22 UTC (forecasting next hour hr -> hr+1)
        for hr in range(6, 23):
            t = hr * 60
            w, h, f = slice(t - 360, t), slice(t - 60, t), slice(t, t + 60)
            est = fit_t6(p[w], u[w], imb[w], x[w])
            if est is None or not np.isfinite(est["C3"]):
                continue
            b5_prev = slice((hr - 1) * 12, hr * 12)
            b5_next = slice(hr * 12, (hr + 1) * 12)
            liq_prev = float(np.nansum(oi_drop_adverse_bp[b5_prev]))
            liq_next = float(np.nansum(oi_drop_adverse_bp[b5_next]))
            liq_all_next = float(np.nansum(oi_drop_bp[b5_next]))
            v60 = float(np.nansum(vol[h]))
            hourly_rows.append({
                "symbol": s,
                "date": d,
                "hour": hr,
                "split": "train" if d <= "2024-12-31" else "test",
                "C3_hat": float(est["C3"]),
                "S60": float(est["S60"]) if np.isfinite(est["S60"]) else 0.0,
                "kappa_hat": float(est["kappa"]),
                "kappa_sq": float(est["kappa"] ** 2),
                "rv_15": float(np.nanstd(dp[t - 15:t])),
                "rv_60": float(np.nanstd(dp[h])),
                "rv_360": float(np.nanstd(dp[w])),
                "rv_day": float(np.nanstd(dp[1:t])),
                "ewma_vol": float(np.sqrt(max(ew[t - 1], 0.0))),
                "abs_ret_60": float(abs(p[t - 1] - p[t - 60])),
                "mae_lag60": float(np.nanmax(np.abs(p[t - 60:t] - p[t - 61]))),
                "log_vol_60": float(np.log1p(max(v60, 0.0))),
                "log_depth1": float(np.log(max(tot[t - 1], 1e-6))),
                "imbalance": float(imb[t - 1]),
                "liq_lag60": liq_prev,
                "LIQ_next": liq_next,
                "LIQ_all_next": liq_all_next,
                "MAE_60": float(np.nanmax(np.abs(p[f] - p[t - 1]))),
            })

        # Part 23: Non-resetting full-day position entered at hour 6 UTC (t=360) and held until hour 24 UTC (t=1440)
        w0 = slice(0, 360)
        est0 = fit_t6(p[w0], u[w0], imb[w0], x[w0])
        if est0 is not None and np.isfinite(est0["S60"]) and est0["S60"] > 0:
            # Bootstrap 90th percentile S60_up over 60-minute blocks of morning window
            rng_b = np.random.default_rng(int(hashlib.md5(f"{s}_{d}".encode()).hexdigest()[:8], 16))
            s60_boots = []
            for _ in range(40):
                b_idx = np.concatenate([np.arange(b0 * 60, (b0 + 1) * 60) for b0 in rng_b.integers(0, 6, size=6)])
                eb = fit_t6(p[b_idx], u[b_idx], imb[b_idx], x[b_idx])
                if eb is not None and np.isfinite(eb["S60"]) and eb["S60"] > 0:
                    s60_boots.append(float(eb["S60"]))
            s60_up = float(np.quantile(s60_boots, 0.90)) if len(s60_boots) >= 5 else float(1.25 * est0["S60"])
            u_cert = float(np.nanquantile(np.abs(u[w0]), 0.95))
            rv_morn = float(np.nanstd(dp[1:360]))
            mae_day = float(np.nanmax(np.abs(p[360:1440] - p[359])))
            daily_pos_rows.append({
                "symbol": s,
                "date": d,
                "split": "train" if d <= "2024-12-31" else "test",
                "rv_morn": max(rv_morn, 1e-4),
                "cert_risk": max(u_cert * s60_up, 1e-4),
                "S60_cert": float(est0["S60"]),
                "MAE_day": mae_day,
            })

    # ---------------- Evaluate Part 22 ----------------
    D22 = pd.DataFrame(hourly_rows).dropna()
    tr22 = D22["split"] == "train"
    clip_cols = ["C3_hat", "kappa_hat", "kappa_sq", "rv_15", "rv_60", "rv_360", "rv_day", "ewma_vol",
                 "abs_ret_60", "mae_lag60", "log_vol_60", "log_depth1", "imbalance", "liq_lag60", "LIQ_next", "LIQ_all_next", "MAE_60"]
    for c in clip_cols:
        lo, hi = D22.loc[tr22, c].quantile([0.01, 0.99])
        D22[c] = D22[c].clip(lo, hi)

    A22 = D22[tr22].copy()
    B22 = D22[~tr22].sort_values(["date", "symbol", "hour"]).copy()
    syms_22 = sorted(A22["symbol"].unique())

    def _X22(df_sub: pd.DataFrame, cols: list[str]) -> np.ndarray:
        X = [np.ones(len(df_sub))] + [df_sub[c].to_numpy() for c in cols] + [(df_sub["symbol"] == s).to_numpy(float) for s in syms_22[1:]]
        return np.column_stack(X)

    ctrl_22 = ["rv_15", "rv_60", "rv_360", "rv_day", "ewma_vol", "abs_ret_60", "mae_lag60", "log_vol_60", "log_depth1", "imbalance", "kappa_hat", "kappa_sq", "liq_lag60"]

    # Primary 1: C3_hat forecasting LIQ_next beyond baseline
    y_liq_tr = A22["LIQ_next"].to_numpy()
    y_liq_te = B22["LIQ_next"].to_numpy()
    sst_liq = float(np.sum((y_liq_te - y_liq_tr.mean()) ** 2))
    b_liq_base = np.linalg.lstsq(_X22(A22, ctrl_22), y_liq_tr, rcond=None)[0]
    b_liq_full = np.linalg.lstsq(_X22(A22, ctrl_22 + ["C3_hat"]), y_liq_tr, rcond=None)[0]
    fb_liq = _X22(B22, ctrl_22) @ b_liq_base
    ff_liq = _X22(B22, ctrl_22 + ["C3_hat"]) @ b_liq_full
    dr2_liq = float((np.sum((y_liq_te - fb_liq) ** 2) - np.sum((y_liq_te - ff_liq) ** 2)) / sst_liq)
    cw_t_liq, cw_p_liq = cw_test(y_liq_te, fb_liq, ff_liq)

    # Also evaluate C3_hat forecasting MAE_60 on the 22nds (without and with realized LIQ_next)
    ctrl_mae = ["rv_15", "rv_60", "rv_360", "rv_day", "ewma_vol", "abs_ret_60", "mae_lag60", "log_vol_60", "log_depth1", "imbalance", "kappa_hat", "kappa_sq"]
    y_mae_tr = A22["MAE_60"].to_numpy()
    y_mae_te = B22["MAE_60"].to_numpy()
    sst_mae = float(np.sum((y_mae_te - y_mae_tr.mean()) ** 2))

    b_mae_base = np.linalg.lstsq(_X22(A22, ctrl_mae), y_mae_tr, rcond=None)[0]
    b_mae_c3 = np.linalg.lstsq(_X22(A22, ctrl_mae + ["C3_hat"]), y_mae_tr, rcond=None)[0]
    fb_mae = _X22(B22, ctrl_mae) @ b_mae_base
    ff_mae = _X22(B22, ctrl_mae + ["C3_hat"]) @ b_mae_c3
    dr2_mae_without_liq = float((np.sum((y_mae_te - fb_mae) ** 2) - np.sum((y_mae_te - ff_mae) ** 2)) / sst_mae)
    cw_t_mae, cw_p_mae = cw_test(y_mae_te, fb_mae, ff_mae)

    # Primary 2: Mediation — add realized LIQ_next and LIQ_all_next to baseline and full MAE_60 models
    ctrl_mae_liq = ctrl_mae + ["LIQ_next", "LIQ_all_next"]
    b_mae_liq_base = np.linalg.lstsq(_X22(A22, ctrl_mae_liq), y_mae_tr, rcond=None)[0]
    b_mae_liq_c3 = np.linalg.lstsq(_X22(A22, ctrl_mae_liq + ["C3_hat"]), y_mae_tr, rcond=None)[0]
    fb_mae_liq = _X22(B22, ctrl_mae_liq) @ b_mae_liq_base
    ff_mae_liq = _X22(B22, ctrl_mae_liq + ["C3_hat"]) @ b_mae_liq_c3
    dr2_mae_with_liq = float((np.sum((y_mae_te - fb_mae_liq) ** 2) - np.sum((y_mae_te - ff_mae_liq) ** 2)) / sst_mae)
    mediation_share = float((dr2_mae_without_liq - dr2_mae_with_liq) / max(abs(dr2_mae_without_liq), 1e-9))

    rng = np.random.default_rng(20261021)
    te_d = B22["date"].to_numpy()
    ud_te = np.unique(te_d)
    pos_te = {d: np.where(te_d == d)[0] for d in ud_te}
    boot_dr2_liq, boot_dr2_mae, boot_dr2_mae_liq, boot_med = [], [], [], []
    for _ in range(2000):
        idx = np.concatenate([pos_te[d] for d in rng.choice(ud_te, len(ud_te))])
        s_l = float(np.sum((y_liq_te[idx] - y_liq_tr.mean()) ** 2))
        s_m = float(np.sum((y_mae_te[idx] - y_mae_tr.mean()) ** 2))
        dl = float((np.sum((y_liq_te[idx] - fb_liq[idx]) ** 2) - np.sum((y_liq_te[idx] - ff_liq[idx]) ** 2)) / s_l)
        dm = float((np.sum((y_mae_te[idx] - fb_mae[idx]) ** 2) - np.sum((y_mae_te[idx] - ff_mae[idx]) ** 2)) / s_m)
        dml = float((np.sum((y_mae_te[idx] - fb_mae_liq[idx]) ** 2) - np.sum((y_mae_te[idx] - ff_mae_liq[idx]) ** 2)) / s_m)
        boot_dr2_liq.append(100.0 * dl)
        boot_dr2_mae.append(100.0 * dm)
        boot_dr2_mae_liq.append(100.0 * dml)
        if abs(dm) > 1e-4:
            boot_med.append((dm - dml) / dm)

    ci_liq = [float(np.quantile(boot_dr2_liq, 0.025)), float(np.quantile(boot_dr2_liq, 0.975))]
    ci_mae = [float(np.quantile(boot_dr2_mae, 0.025)), float(np.quantile(boot_dr2_mae, 0.975))]
    ci_mae_liq = [float(np.quantile(boot_dr2_mae_liq, 0.025)), float(np.quantile(boot_dr2_mae_liq, 0.975))]
    ci_med = [float(np.quantile(boot_med, 0.025)), float(np.quantile(boot_med, 0.975))] if boot_med else [None, None]

    out22 = {
        "test_id": "P22_liquidation_mechanism",
        "spec_sha256": "2b3794e3812f5d153f52fc2445cc28f5c3b89890f9cc2afb8d776151fe2742dd",
        "n_symbols": len(syms_22),
        "n_train_hours": len(A22),
        "n_test_hours": len(B22),
        "primary_1_forecast_liquidation": {
            "delta_r2_liq_pts": round(100.0 * dr2_liq, 3),
            "delta_r2_liq_ci_pts": [round(ci_liq[0], 3), round(ci_liq[1], 3)],
            "clark_west_t": round(cw_t_liq, 2),
            "clark_west_p": round(cw_p_liq, 4),
            "pass": bool(dr2_liq > 0 and cw_p_liq < 0.025 and ci_liq[0] > 0),
        },
        "excursion_forecast_on_22nds": {
            "delta_r2_mae_pts": round(100.0 * dr2_mae_without_liq, 3),
            "delta_r2_mae_ci_pts": [round(ci_mae[0], 3), round(ci_mae[1], 3)],
            "clark_west_t": round(cw_t_mae, 2),
            "clark_west_p": round(cw_p_mae, 6),
        },
        "primary_2_mediation_by_liquidation": {
            "delta_r2_mae_controlling_liq_pts": round(100.0 * dr2_mae_with_liq, 3),
            "delta_r2_mae_controlling_liq_ci_pts": [round(ci_mae_liq[0], 3), round(ci_mae_liq[1], 3)],
            "mediation_share": round(mediation_share, 3),
            "mediation_share_ci": [round(ci_med[0], 3), round(ci_med[1], 3)] if ci_med[0] is not None else None,
            "pass": bool(mediation_share >= 0.50),
        },
    }
    print("[Paper 2 Part 22 Result]", json.dumps(out22, indent=2))
    os.makedirs(os.path.join(HERE, "results_archive", "outputs", "p22res"), exist_ok=True)
    json.dump(out22, open(os.path.join(HERE, "results_archive", "outputs", "p22res", "P22_liquidation_results.json"), "w"), indent=2)

    # ---------------- Evaluate Part 23 ----------------
    D23 = pd.DataFrame(daily_pos_rows).dropna()
    tr23 = D23["split"] == "train"
    A23 = D23[tr23].copy()
    B23 = D23[~tr23].sort_values(["date", "symbol"]).copy()

    # Per-symbol training medians for k_vol and k_guard, plus normalization so training mean position is 1.0
    k_vol_map = A23.groupby("symbol")["rv_morn"].median().to_dict()
    k_grd_map = A23.groupby("symbol")["cert_risk"].median().to_dict()

    for df_sub in (A23, B23):
        kv = df_sub["symbol"].map(k_vol_map).to_numpy()
        kg = df_sub["symbol"].map(k_grd_map).to_numpy()
        raw_vol = np.minimum(1.0, kv / df_sub["rv_morn"].to_numpy())
        raw_grd = np.minimum(1.0, kg / df_sub["cert_risk"].to_numpy())
        df_sub["raw_a"] = 1.0
        df_sub["raw_b"] = raw_vol
        df_sub["raw_c"] = raw_vol * raw_grd
        df_sub["raw_d"] = raw_grd

    # Normalize each rule to unit mean exposure on training days ($1M average notional at scale c=1)
    norm_b = A23.groupby("symbol")["raw_b"].mean().to_dict()
    norm_c = A23.groupby("symbol")["raw_c"].mean().to_dict()
    norm_d = A23.groupby("symbol")["raw_d"].mean().to_dict()

    B23["q_a"] = 1.0
    B23["q_b"] = B23["raw_b"] / B23["symbol"].map(norm_b)
    B23["q_c_unit"] = B23["raw_c"] / B23["symbol"].map(norm_c)
    B23["q_d"] = B23["raw_d"] / B23["symbol"].map(norm_d)

    # Liquidation buffer for 20x position on Binance Tier-1 (0.5% MMR): B_tier = 450 bp
    B_TIER = 450.0
    mae_te = B23["MAE_day"].to_numpy()
    qa = B23["q_a"].to_numpy()
    qb = B23["q_b"].to_numpy()
    qc_raw = B23["raw_c"].to_numpy()
    qd = B23["q_d"].to_numpy()

    # At unit training-normalized scale ($1M facility):
    liq_rate_a = float(np.mean(qa * mae_te >= B_TIER))
    liq_rate_b = float(np.mean(qb * mae_te >= B_TIER))
    liq_rate_c_unit = float(np.mean(B23["q_c_unit"].to_numpy() * mae_te >= B_TIER))
    liq_rate_d = float(np.mean(qd * mae_te >= B_TIER))

    # Primary capacity question: scale c_vg so that rule (c) has the exact same liquidation rate on the test sample as rule (b)
    # A position c_vg * raw_c_i liquidates iff c_vg * raw_c_i * mae_i >= B_TIER, i.e. c_vg >= B_TIER / (raw_c_i * mae_i).
    # So to match liq_rate_b (k_target liquidations out of N), c_vg is the (1 - liq_rate_b) quantile of B_TIER / (raw_c * mae_te)!
    def matched_notional(qb_arr, qc_raw_arr, mae_arr):
        target_rate = float(np.mean(qb_arr * mae_arr >= B_TIER))
        mean_notional_b = float(np.mean(qb_arr)) * 1e6
        if target_rate <= 0.0:
            return mean_notional_b, mean_notional_b, 0.0
        thresholds_c = B_TIER / np.maximum(qc_raw_arr * mae_arr, 1e-6)
        c_vg = float(np.quantile(thresholds_c, 1.0 - target_rate))
        mean_notional_c = float(np.mean(c_vg * qc_raw_arr)) * 1e6
        return mean_notional_b, mean_notional_c, target_rate

    notional_b, notional_c, target_breach = matched_notional(qb, qc_raw, mae_te)
    delta_notional = notional_c - notional_b
    pct_gain = 100.0 * delta_notional / max(notional_b, 1.0)

    # Also compute ES95 of full-day loss (in USD per $1M average position) for the four unit-normalized rules
    def es95_usd(loss_bp_arr):
        q95 = np.quantile(loss_bp_arr, 0.95)
        return float(np.mean(loss_bp_arr[loss_bp_arr >= q95]) * 100.0)

    es95_a = es95_usd(qa * mae_te)
    es95_b = es95_usd(qb * mae_te)
    es95_c = es95_usd(B23["q_c_unit"].to_numpy() * mae_te)
    es95_d = es95_usd(qd * mae_te)

    # Date-block bootstrap (2,000 draws) for delta_notional and log ES95 diff
    d23_dates = B23["date"].to_numpy()
    ud23 = np.unique(d23_dates)
    pos23 = {d: np.where(d23_dates == d)[0] for d in ud23}
    boot_dnot, boot_log_es = [], []
    for _ in range(2000):
        idx = np.concatenate([pos23[d] for d in rng.choice(ud23, len(ud23))])
        nb, nc, _ = matched_notional(qb[idx], qc_raw[idx], mae_te[idx])
        boot_dnot.append(nc - nb)
        eb = es95_usd(qb[idx] * mae_te[idx])
        ec = es95_usd(B23["q_c_unit"].to_numpy()[idx] * mae_te[idx])
        boot_log_es.append(float(np.log(max(ec, 1.0) / max(eb, 1.0))))

    ci_dnot = [float(np.quantile(boot_dnot, 0.025)), float(np.quantile(boot_dnot, 0.975))]
    ci_log_es = [float(np.quantile(boot_log_es, 0.025)), float(np.quantile(boot_log_es, 0.975))]

    out23 = {
        "test_id": "P23_guard_capacity",
        "spec_sha256": "d4169377da0b30116a9adbf684d57ae9695ddfefc34d3bf50faf0609631dd860",
        "n_symbols": len( k_vol_map ),
        "n_train_symbol_days": len(A23),
        "n_test_symbol_days": len(B23),
        "maintenance_margin_buffer_bps": B_TIER,
        "unit_scaled_rules": {
            "a_static": {"liq_rate_pct": round(100.0 * liq_rate_a, 2), "ES95_day_loss_usd": round(es95_a, 0), "activity_retained": 1.0},
            "b_vol_cap": {"liq_rate_pct": round(100.0 * liq_rate_b, 2), "ES95_day_loss_usd": round(es95_b, 0), "activity_retained": round(float(B23["raw_b"].mean()), 3)},
            "c_vol_plus_guard": {"liq_rate_pct": round(100.0 * liq_rate_c_unit, 2), "ES95_day_loss_usd": round(es95_c, 0), "activity_retained": round(float(B23["raw_c"].mean()), 3)},
            "d_guard_only": {"liq_rate_pct": round(100.0 * liq_rate_d, 2), "ES95_day_loss_usd": round(es95_d, 0), "activity_retained": round(float(B23["raw_d"].mean()), 3)},
        },
        "primary_matched_breach_capacity": {
            "matched_liq_rate_pct": round(100.0 * target_breach, 2),
            "notional_vol_cap_usd": round(notional_b, 0),
            "notional_vol_plus_guard_usd": round(notional_c, 0),
            "delta_notional_usd": round(delta_notional, 0),
            "delta_notional_ci_usd": [round(ci_dnot[0], 0), round(ci_dnot[1], 0)],
            "capacity_gain_pct": round(pct_gain, 2),
            "c_vs_b_log_es95_diff": round(float(np.log(es95_c / es95_b)), 4),
            "c_vs_b_log_es95_ci": [round(ci_log_es[0], 4), round(ci_log_es[1], 4)],
            "pass": bool(delta_notional > 0 and ci_dnot[0] > 0),
        },
    }
    print("[Paper 2 Part 23 Result]", json.dumps(out23, indent=2))
    os.makedirs(os.path.join(HERE, "results_archive", "outputs", "p23res"), exist_ok=True)
    json.dump(out23, open(os.path.join(HERE, "results_archive", "outputs", "p23res", "P23_guard_capacity_results.json"), "w"), indent=2)
    json.dump({"part22": out22, "part23": out23}, open(os.path.join(HERE, "recomputed", "R_P2_p22_p23.json"), "w"), indent=2)
    return out22, out23


def main():
    t0 = time.time()
    u2 = json.load(open(os.path.join(HERE, "results_archive", "p9res", "results", "U2_build.json")))["metrics"]["flow_scale"]
    x4 = json.load(open(os.path.join(HERE, "results_archive", "outputs", "p16res", "results", "X4_build.json")))["metrics"]["flow_scale"]
    flow_scale = {**{s: float(u2[s]) for s in u2}, **{s: float(x4[s]) for s in x4}}

    jobs = [(s, d) for s in SYMS_19 for d in ALL_DATES_22]
    print(f"[22nd-of-month Suite] Fetching/validating {len(jobs)} symbol-days across {len(SYMS_19)} thin symbols...")
    panel = {}
    with ThreadPoolExecutor(32) as ex:
        futs = {ex.submit(build_day_22, s, d): (s, d) for s, d in jobs}
        for f in as_completed(futs):
            res = f.result()
            if res is not None:
                panel[futs[f]] = res
    print(f"[22nd-of-month Suite] Built {len(panel)} valid symbol-days in {time.time() - t0:.1f}s")

    run_p1_disclosure_oos(panel, flow_scale)
    run_p22_and_p23(panel, flow_scale)


if __name__ == "__main__":
    main()
