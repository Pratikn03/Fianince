#!/usr/bin/env python3
"""
Hardened Empirical Audits for Phase 4 (Guard Benchmarks), Phase 5 (Disclosure Information Hierarchy),
and Phase 6 (Persistence & Liquidation Mechanism Validation).

Uses the exact 19-symbol, 66-date panel (24 train dates in 2024, 42 test dates in 2025-2026)
from `recompute_prereg_oct21_followup.py` WITHOUT modifying any pre-registered unlock files
or altering the baseline JSON files checked by `verify_paper_numbers.py`.

Outputs:
  ceiling_suite/papers/recomputed/R_hardened_empirical_audits.json
"""

from __future__ import annotations

from concurrent.futures import ThreadPoolExecutor, as_completed
import hashlib
import json
import os
from pathlib import Path
import sys
import time

import numpy as np
import pandas as pd

THIS_DIR = Path(__file__).resolve().parent
if str(THIS_DIR) not in sys.path:
    sys.path.insert(0, str(THIS_DIR))

from recompute_p2_parts19_20_21 import HERE, cw_test, fit_t6
from recompute_prereg_oct21_22nd import SYMS_19, build_day_22
from recompute_prereg_oct21_followup import ALL_DATES_66

OUT_JSON = THIS_DIR / "recomputed" / "R_hardened_empirical_audits.json"


def load_panel_and_scales() -> tuple[dict, dict]:
    t0 = time.time()
    u2 = json.load(open(os.path.join(HERE, "results_archive", "p9res", "results", "U2_build.json")))["metrics"]["flow_scale"]
    x4 = json.load(open(os.path.join(HERE, "results_archive", "outputs", "p16res", "results", "X4_build.json")))["metrics"]["flow_scale"]
    flow_scale = {**{s: float(u2[s]) for s in u2}, **{s: float(x4[s]) for s in x4}}

    jobs = [(s, d) for s in SYMS_19 for d in ALL_DATES_66]
    panel = {}
    with ThreadPoolExecutor(32) as ex:
        futs = {ex.submit(build_day_22, s, d): (s, d) for s, d in jobs}
        for f in as_completed(futs):
            res = f.result()
            if res is not None:
                panel[futs[f]] = res
    print(f"[Hardened Empirical Audit] Loaded {len(panel)}/{len(jobs)} valid symbol-days in {time.time() - t0:.1f}s")
    return panel, flow_scale


def audit_phase_4_guard_benchmarks(panel: dict, flow_scale: dict) -> dict:
    """Phase 4: Fair Financial Guard Benchmarks (Tasks 4.1-4.5)."""
    daily_rows = []
    for (s, d), day in sorted(panel.items()):
        fs = flow_scale[s]
        p = np.log(day["close_1m"]) * 1e4
        u = day["flow_1m"] / fs
        tot = day["bid1"] + day["ask1"]
        imb = (day["bid1"] - day["ask1"]) / np.maximum(tot, 1e-12)
        x = p - pd.Series(p).ewm(span=60, adjust=False).mean().to_numpy()
        dp = np.diff(p, prepend=np.nan)
        split_name = "train" if d <= "2024-12-31" else "test"

        w0 = slice(0, 360)
        est0 = fit_t6(p[w0], u[w0], imb[w0], x[w0])
        if est0 is not None and np.isfinite(est0["S60"]) and est0["S60"] > 0:
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
            var99_morn = float(np.nanquantile(np.abs(dp[1:360]), 0.99))
            # Morning cumulative flow pressure / inventory proxy
            inv_morn = float(np.mean(np.abs(np.cumsum(u[0:360]))))

            path_day = p[360:1440] - p[359]
            mae_abs = float(np.nanmax(np.abs(path_day)))
            mae_long = float(np.nanmax(-path_day))   # adverse move for a long position: price drop -(p_t - p_359)
            mae_short = float(np.nanmax(path_day))   # adverse move for a short position: price rise +(p_t - p_359)
            morn_sign = 1.0 if float(np.nansum(u[0:360])) >= 0.0 else -1.0
            mae_flow_dir = mae_long if morn_sign > 0 else mae_short
            end_pnl_long_bp = float(path_day[-1])
            end_pnl_short_bp = float(-path_day[-1])

            daily_rows.append({
                "symbol": s,
                "date": d,
                "split": split_name,
                "rv_morn": max(rv_morn, 1e-4),
                "var99_morn": max(var99_morn, 1e-4),
                "inv_morn": max(inv_morn, 1e-4),
                "cert_risk": max(u_cert * s60_up, 1e-4),
                "MAE_day": mae_abs,
                "MAE_long": mae_long,
                "MAE_short": mae_short,
                "MAE_flow_dir": mae_flow_dir,
                "end_pnl_long_bp": end_pnl_long_bp,
                "end_pnl_short_bp": end_pnl_short_bp,
            })

    D24 = pd.DataFrame(daily_rows).dropna()
    tr = D24["split"] == "train"
    A = D24[tr].copy()
    B = D24[~tr].sort_values(["date", "symbol"]).copy()

    k_vol = A.groupby("symbol")["rv_morn"].median().to_dict()
    k_var = A.groupby("symbol")["var99_morn"].median().to_dict()
    k_inv = A.groupby("symbol")["inv_morn"].median().to_dict()
    k_grd = A.groupby("symbol")["cert_risk"].median().to_dict()

    for df_sub in (A, B):
        r_vol = np.minimum(1.0, df_sub["symbol"].map(k_vol).to_numpy() / df_sub["rv_morn"].to_numpy())
        r_var = np.minimum(1.0, df_sub["symbol"].map(k_var).to_numpy() / df_sub["var99_morn"].to_numpy())
        r_inv = np.minimum(1.0, df_sub["symbol"].map(k_inv).to_numpy() / df_sub["inv_morn"].to_numpy())
        r_grd = np.minimum(1.0, df_sub["symbol"].map(k_grd).to_numpy() / df_sub["cert_risk"].to_numpy())
        df_sub["static_cap"] = np.ones(len(df_sub), dtype=float)
        df_sub["vol_cap"] = r_vol
        df_sub["margin_rule"] = r_var
        df_sub["inventory_cap"] = r_inv
        df_sub["guard_only"] = r_grd
        df_sub["vol_plus_guard"] = r_vol * r_grd

    policies = ["static_cap", "vol_cap", "margin_rule", "inventory_cap", "guard_only", "vol_plus_guard"]
    B_TIER = 450.0
    FEE_FUNDING_BP = 10.0  # 8 bp round-trip taker fee + 2 bp funding over 18 hours

    def _metrics_for_q(q_arr: np.ndarray, df_eval: pd.DataFrame) -> dict:
        mae_abs = df_eval["MAE_day"].to_numpy()
        mae_long = df_eval["MAE_long"].to_numpy()
        mae_short = df_eval["MAE_short"].to_numpy()
        mae_fdir = df_eval["MAE_flow_dir"].to_numpy()

        loss_abs = q_arr * mae_abs
        loss_long_net = q_arr * (mae_long + FEE_FUNDING_BP)
        loss_short_net = q_arr * (mae_short + FEE_FUNDING_BP)
        loss_fdir_net = q_arr * (mae_fdir + FEE_FUNDING_BP)

        def _es95(arr: np.ndarray) -> float:
            q95 = np.quantile(arr, 0.95)
            return float(np.mean(arr[arr >= q95]) * 100.0)

        def _es99(arr: np.ndarray) -> float:
            q99 = np.quantile(arr, 0.99)
            return float(np.mean(arr[arr >= q99]) * 100.0)

        mean_not = float(np.mean(q_arr)) * 1e6
        breach_abs = float(np.mean(loss_abs >= B_TIER))
        breach_long = float(np.mean(loss_long_net >= B_TIER))
        breach_short = float(np.mean(loss_short_net >= B_TIER))
        breach_fdir = float(np.mean(loss_fdir_net >= B_TIER))
        es95_abs = _es95(loss_abs)

        return {
            "mean_admitted_notional_usd": round(mean_not, 0),
            "median_admitted_notional_usd": round(float(np.median(q_arr)) * 1e6, 0),
            "p10_admitted_notional_usd": round(float(np.quantile(q_arr, 0.10)) * 1e6, 0),
            "p90_admitted_notional_usd": round(float(np.quantile(q_arr, 0.90)) * 1e6, 0),
            "stylized_2sided_breach_rate_pct": round(100.0 * breach_abs, 2),
            "directional_long_breach_rate_pct": round(100.0 * breach_long, 2),
            "directional_short_breach_rate_pct": round(100.0 * breach_short, 2),
            "directional_flow_aligned_breach_rate_pct": round(100.0 * breach_fdir, 2),
            "es95_2sided_loss_usd": round(es95_abs, 0),
            "es99_2sided_loss_usd": round(_es99(loss_abs), 0),
            "es95_long_net_fee_funding_usd": round(_es95(loss_long_net), 0),
            "es95_short_net_fee_funding_usd": round(_es95(loss_short_net), 0),
            "max_drawdown_loss_usd": round(float(np.max(loss_abs)) * 100.0, 0),
            "breach_rate_per_1M_notional_pct": round(100.0 * breach_abs / max(float(np.mean(q_arr)), 1e-6), 2),
            "es95_per_1M_notional_usd": round(es95_abs / max(float(np.mean(q_arr)), 1e-6), 0),
        }

    # Benchmark 4A: Unnormalized Capped Rule 15c3-5 Throttle q_t in (0, 1]
    bench_4a = {pol: _metrics_for_q(B[pol].to_numpy(), B) for pol in policies}

    # Benchmark 4B-i: Capped Rule 15c3-5 where every policy is scaled on the TRAINING set
    # to match the training mean notional of `vol_plus_guard` (remaining strictly inside [0, 1])
    target_train_mean_vg = float(A["vol_plus_guard"].mean())
    bench_4b_capped_to_vg_mean = {}
    for pol in policies:
        pol_tr_mean = float(A[pol].mean())
        scale_tr = target_train_mean_vg / max(pol_tr_mean, 1e-9)
        q_te_scaled = np.minimum(1.0, scale_tr * B[pol].to_numpy())
        bench_4b_capped_to_vg_mean[pol] = _metrics_for_q(q_te_scaled, B)

    # Benchmark 4B-ii: Per-symbol training-mean normalized so every policy has E_train[q_t | symbol] == 1.0 ($1M)
    bench_4b_unit_train_notional = {}
    for pol in policies:
        sym_means = A.groupby("symbol")[pol].mean().to_dict()
        q_te_unit = B[pol].to_numpy() / B["symbol"].map(sym_means).to_numpy()
        bench_4b_unit_train_notional[pol] = _metrics_for_q(q_te_unit, B)

    # Benchmark 4C-i: Strictly TRAINING-CALIBRATED Matched ES95 Risk Budget
    # Choose scalar multiplier c_train on 2024 training set so every policy has training ES95 equal to vol_cap's training ES95
    mae_tr = A["MAE_day"].to_numpy()
    def _es95_raw(arr: np.ndarray) -> float:
        q95 = np.quantile(arr, 0.95)
        return float(np.mean(arr[arr >= q95]) * 100.0)

    target_train_es95 = _es95_raw(A["vol_cap"].to_numpy() * mae_tr)
    bench_4c_train_matched_es95 = {}
    for pol in policies:
        pol_tr_es95 = _es95_raw(A[pol].to_numpy() * mae_tr)
        c_es_train = target_train_es95 / max(pol_tr_es95, 1e-6)
        q_te = c_es_train * B[pol].to_numpy()
        m_dict = _metrics_for_q(q_te, B)
        m_dict["train_calibrated_multiplier"] = round(c_es_train, 4)
        bench_4c_train_matched_es95[pol] = m_dict

    # Benchmark 4C-ii: Strictly TRAINING-CALIBRATED Matched Breach Rate Budget
    # Choose scalar multiplier c_breach_train on 2024 training set so every policy has the same training breach rate as unit-normalized vol_cap
    sym_means_vol = A.groupby("symbol")["vol_cap"].mean().to_dict()
    qb_tr_unit = A["vol_cap"].to_numpy() / A["symbol"].map(sym_means_vol).to_numpy()
    target_train_breach = float(np.mean(qb_tr_unit * mae_tr >= B_TIER))
    bench_4c_train_matched_breach = {}
    for pol in policies:
        raw_tr = A[pol].to_numpy()
        thresholds_tr = B_TIER / np.maximum(raw_tr * mae_tr, 1e-6)
        c_br_train = float(np.quantile(thresholds_tr, 1.0 - target_train_breach))
        q_te = c_br_train * B[pol].to_numpy()
        m_dict = _metrics_for_q(q_te, B)
        m_dict["train_calibrated_multiplier"] = round(c_br_train, 4)
        m_dict["train_target_breach_rate_pct"] = round(100.0 * target_train_breach, 2)
        bench_4c_train_matched_breach[pol] = m_dict

    # Bootstrap CI for difference between vol_plus_guard and vol_cap under training-calibrated matched ES95 and matched notional
    d24_dates = B["date"].to_numpy()
    ud24 = np.unique(d24_dates)
    pos24 = {d: np.where(d24_dates == d)[0] for d in ud24}
    rng = np.random.default_rng(20261030)

    # Compare at Benchmark 4B-ii (unit training notional): ES95(vol_plus_guard) - ES95(vol_cap) and Breach(vol_plus_guard) - Breach(vol_cap)
    q_vol_unit = B["vol_cap"].to_numpy() / B["symbol"].map(A.groupby("symbol")["vol_cap"].mean().to_dict()).to_numpy()
    q_vg_unit = B["vol_plus_guard"].to_numpy() / B["symbol"].map(A.groupby("symbol")["vol_plus_guard"].mean().to_dict()).to_numpy()
    mae_te = B["MAE_day"].to_numpy()

    b_diff_br_unit, b_diff_es_unit = [], []
    for _ in range(2000):
        idx = np.concatenate([pos24[d] for d in rng.choice(ud24, len(ud24))])
        br_v = 100.0 * float(np.mean(q_vol_unit[idx] * mae_te[idx] >= B_TIER))
        br_vg = 100.0 * float(np.mean(q_vg_unit[idx] * mae_te[idx] >= B_TIER))
        es_v = _es95_raw(q_vol_unit[idx] * mae_te[idx])
        es_vg = _es95_raw(q_vg_unit[idx] * mae_te[idx])
        b_diff_br_unit.append(br_vg - br_v)
        b_diff_es_unit.append(es_vg - es_v)

    return {
        "n_train_symbol_days": len(A),
        "n_test_symbol_days": len(B),
        "benchmark_4A_unnormalized_capped_0_1": bench_4a,
        "benchmark_4B_i_capped_matched_to_vg_train_notional": bench_4b_capped_to_vg_mean,
        "benchmark_4B_ii_unit_train_normalized_notional": bench_4b_unit_train_notional,
        "benchmark_4C_i_train_calibrated_matched_es95": bench_4c_train_matched_es95,
        "benchmark_4C_ii_train_calibrated_matched_breach_rate": bench_4c_train_matched_breach,
        "unit_train_notional_vg_minus_vol_inference": {
            "delta_breach_rate_pp": round(
                bench_4b_unit_train_notional["vol_plus_guard"]["stylized_2sided_breach_rate_pct"]
                - bench_4b_unit_train_notional["vol_cap"]["stylized_2sided_breach_rate_pct"], 2
            ),
            "delta_breach_rate_ci_pp": [
                round(float(np.quantile(b_diff_br_unit, 0.025)), 2),
                round(float(np.quantile(b_diff_br_unit, 0.975)), 2),
            ],
            "delta_es95_usd": round(
                bench_4b_unit_train_notional["vol_plus_guard"]["es95_2sided_loss_usd"]
                - bench_4b_unit_train_notional["vol_cap"]["es95_2sided_loss_usd"], 0
            ),
            "delta_es95_ci_usd": [
                round(float(np.quantile(b_diff_es_unit, 0.025)), 0),
                round(float(np.quantile(b_diff_es_unit, 0.975)), 0),
            ],
        },
    }


def audit_phase_5_disclosure_hierarchy(panel: dict, flow_scale: dict) -> dict:
    """Phase 5: Disclosure Information-Value Hierarchy (Tasks 5.1-5.4)."""
    q90_map = {}
    for s in SYMS_19:
        qs = []
        for (sym, d), day in panel.items():
            if sym == s and d <= "2024-12-31":
                f1 = day["flow_1m"] / flow_scale[s]
                q5 = f1.reshape(288, 5).sum(axis=1)
                qs.append(np.abs(q5[12:276]))
        q90_map[s] = float(np.quantile(np.concatenate(qs), 0.90)) if qs else np.inf

    shock_rows = []
    for (s, d), day in sorted(panel.items()):
        fs = flow_scale[s]
        c1 = day["close_1m"]
        f1 = day["flow_1m"] / fs
        p5 = np.log(c1[4::5]) * 1e4
        ret5 = np.diff(p5, prepend=p5[0])
        u5 = f1.reshape(288, 5).sum(axis=1)
        ntop = day["n_top_5m"] * 1e4
        nall = day["n_all_5m"] * 1e4
        if not (np.all(np.isfinite(ntop)) and np.all(np.isfinite(nall))):
            continue

        xf, xs, uf, us = np.zeros(288), np.zeros(288), np.zeros(288), np.zeros(288)
        nt_f, nt_s, na_f, na_s = np.zeros(288), np.zeros(288), np.zeros(288), np.zeros(288)
        for t in range(1, 288):
            dp = ret5[t]
            xf[t] = 0.50 * xf[t - 1] + 0.50 * dp
            xs[t] = 0.90 * xs[t - 1] + 0.10 * dp
            uf[t] = 0.50 * uf[t - 1] + 0.50 * u5[t]
            us[t] = 0.90 * us[t - 1] + 0.10 * u5[t]
            dnt_step = ntop[t] - ntop[t - 1]
            dna_step = nall[t] - nall[t - 1]
            nt_f[t] = 0.50 * nt_f[t - 1] + 0.50 * dnt_step
            nt_s[t] = 0.90 * nt_s[t - 1] + 0.10 * dnt_step
            na_f[t] = 0.50 * na_f[t - 1] + 0.50 * dna_step
            na_s[t] = 0.90 * na_s[t - 1] + 0.10 * dna_step

        split_name = "train" if d <= "2024-12-31" else "test"
        q_thr = q90_map[s]

        for t in range(12, 276):
            if abs(u5[t]) < q_thr:
                continue
            nt_b = float(np.mean(ntop[t - 12:t]))
            na_b = float(np.mean(nall[t - 12:t]))
            nt = float(ntop[t] - nt_b)
            na = float(nall[t] - na_b)
            nt_l1 = float(ntop[t - 1] - nt_b)
            na_l1 = float(nall[t - 1] - na_b)
            nt_l2 = float(ntop[t - 2] - nt_b)
            na_l2 = float(nall[t - 2] - na_b)
            d_nt = float(ntop[t] - ntop[t - 1])
            d_na = float(nall[t] - nall[t - 1])
            div_t = float(nt - na)
            fut_div = float((ntop[t + 6] - nt_b) - (nall[t + 6] - na_b))
            fut_nt = float(ntop[t + 6] - nt_b)

            shock_rows.append({
                "symbol": s,
                "date": d,
                "split": split_name,
                "ret5": float(ret5[t]),
                "u5": float(u5[t]),
                "xf": float(xf[t]),
                "xs": float(xs[t]),
                "uf": float(uf[t]),
                "us": float(us[t]),
                "nt": nt,
                "na": na,
                "div_t": div_t,
                "nt_l1": nt_l1,
                "na_l1": na_l1,
                "nt_l2": nt_l2,
                "na_l2": na_l2,
                "d_nt": d_nt,
                "d_na": d_na,
                "nt_f": float(nt_f[t]),
                "nt_s": float(nt_s[t]),
                "na_f": float(na_f[t]),
                "na_s": float(na_s[t]),
                "fut_div_30m": fut_div,
                "fut_nt_30m": fut_nt,
                "delta_div_30m": fut_div - div_t,
                "delta_nt_30m": fut_nt - nt,
            })

    df = pd.DataFrame(shock_rows).dropna()
    tr = df["split"] == "train"
    clip_cols = [
        "ret5", "u5", "xf", "xs", "uf", "us", "nt", "na", "div_t",
        "nt_l1", "na_l1", "nt_l2", "na_l2", "d_nt", "d_na",
        "nt_f", "nt_s", "na_f", "na_s",
        "fut_div_30m", "fut_nt_30m", "delta_div_30m", "delta_nt_30m",
    ]
    for c in clip_cols:
        lo, hi = df.loc[tr, c].quantile([0.01, 0.99])
        df[c] = df[c].clip(lo, hi)

    A = df[tr].copy()
    B = df[~tr].sort_values(["date", "symbol"]).copy()
    syms = sorted(A["symbol"].unique())

    def _X(df_sub: pd.DataFrame, cols: list[str]) -> np.ndarray:
        X = [np.ones(len(df_sub))] + [df_sub[c].to_numpy() for c in cols] + [(df_sub["symbol"] == s).to_numpy(float) for s in syms[1:]]
        return np.column_stack(X)

    model_specs = {
        "M1_price_flow_2exp_only": ["ret5", "u5", "xf", "xs", "uf", "us"],
        "M3_univariate_class_AR1": ["nt", "na", "div_t"],
        "M4_univariate_class_AR3": ["nt", "na", "div_t", "nt_l1", "na_l1", "nt_l2", "na_l2", "d_nt", "d_na"],
        "M5_class_ARX_price_flow": ["nt", "na", "div_t", "ret5", "u5"],
        "M6_baseline_full_tag_cols": ["ret5", "u5", "xf", "xs", "uf", "us", "nt", "na", "d_nt", "d_na", "div_t"],
        "M7_augmented_cohort_memory_filters": [
            "ret5", "u5", "xf", "xs", "uf", "us", "nt", "na", "d_nt", "d_na", "div_t", "nt_f", "nt_s", "na_f", "na_s"
        ],
    }

    outcomes = {
        "fut_div_30m": "div_t",
        "fut_nt_30m": "nt",
        "delta_div_30m": None,
        "delta_nt_30m": None,
    }

    hierarchy_results = {}
    for ycol, rw_col in outcomes.items():
        y_tr = A[ycol].to_numpy()
        y_te = B[ycol].to_numpy()
        sst = float(np.sum((y_te - y_tr.mean()) ** 2))
        preds = {}
        r2_pts = {}

        if rw_col is not None:
            pred_rw = B[rw_col].to_numpy()
            preds["M2_naive_random_walk"] = pred_rw
            r2_pts["M2_naive_random_walk"] = round(100.0 * (1.0 - float(np.sum((y_te - pred_rw) ** 2)) / sst), 3)

        for mname, cols in model_specs.items():
            beta = np.linalg.lstsq(_X(A, cols), y_tr, rcond=None)[0]
            pred = _X(B, cols) @ beta
            preds[mname] = pred
            r2_pts[mname] = round(100.0 * (1.0 - float(np.sum((y_te - pred) ** 2)) / sst), 3)

        # Pairwise comparisons of interest
        def _comp(m_base: str, m_alt: str) -> dict:
            pb = preds[m_base]
            pa = preds[m_alt]
            dr2 = 100.0 * float((np.sum((y_te - pb) ** 2) - np.sum((y_te - pa) ** 2)) / sst)
            cwt, cwp = cw_test(y_te, pb, pa)
            return {
                "delta_r2_pts": round(dr2, 3),
                "clark_west_t": round(cwt, 2),
                "clark_west_p": float(f"{cwp:.6g}"),
            }

        comps = {
            "total_gain_M6_vs_M1_price_flow": _comp("M1_price_flow_2exp_only", "M6_baseline_full_tag_cols"),
            "level_persistence_gain_M3_AR1_vs_M1_price_flow": _comp("M1_price_flow_2exp_only", "M3_univariate_class_AR1"),
            "dynamic_gain_M6_full_vs_M3_AR1": _comp("M3_univariate_class_AR1", "M6_baseline_full_tag_cols"),
            "dynamic_gain_M6_full_vs_M4_AR3": _comp("M4_univariate_class_AR3", "M6_baseline_full_tag_cols"),
            "dynamic_gain_M7_cohort_filters_vs_M3_AR1": _comp("M3_univariate_class_AR1", "M7_augmented_cohort_memory_filters"),
            "dynamic_gain_M7_cohort_filters_vs_M4_AR3": _comp("M4_univariate_class_AR3", "M7_augmented_cohort_memory_filters"),
        }
        if rw_col is not None:
            comps["AR1_plus_memory_M6_vs_M2_random_walk"] = _comp("M2_naive_random_walk", "M6_baseline_full_tag_cols")

        total_g = comps["total_gain_M6_vs_M1_price_flow"]["delta_r2_pts"]
        ar1_g = comps["level_persistence_gain_M3_AR1_vs_M1_price_flow"]["delta_r2_pts"]
        dyn_g = comps["dynamic_gain_M6_full_vs_M3_AR1"]["delta_r2_pts"]

        hierarchy_results[ycol] = {
            "oos_r2_pts_by_model": r2_pts,
            "nested_comparisons": comps,
            "share_of_total_gain_from_current_state_AR1_pct": round(100.0 * ar1_g / max(abs(total_g), 1e-9), 2),
            "share_of_total_gain_from_dynamic_lags_and_filters_pct": round(100.0 * dyn_g / max(abs(total_g), 1e-9), 2),
        }

    return {
        "n_train_shocks": len(A),
        "n_test_shocks": len(B),
        "outcomes": hierarchy_results,
    }


def audit_phase_6_persistence_mechanism(panel: dict, flow_scale: dict) -> dict:
    """Phase 6: Economic Mechanism Validation (Tasks 6.1-6.4)."""
    hourly_rows = []
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
        split_name = "train" if d <= "2024-12-31" else "test"
        p5 = p[4::5]

        for hr in range(6, 23):
            t = hr * 60
            w, h, f = slice(t - 360, t), slice(t - 60, t), slice(t, t + 60)
            est = fit_t6(p[w], u[w], imb[w], x[w])
            if est is None or not np.isfinite(est["C3"]):
                continue
            p_f = p[f] - p[t - 1]
            p_h = p[h] - p[t - 61]
            m_ckpt_lag = float(np.mean(np.abs(p_h[14::15])))
            m_ckpt_next = float(np.mean(np.abs(p_f[14::15])))
            m_l1_next = float(np.mean(np.abs(p_f)))
            p5_window = np.concatenate([[p[t - 1]], p5[hr * 12:(hr + 1) * 12]])
            m_5m_placebo = float(np.max(np.abs(np.diff(p5_window))))
            v60 = float(np.nansum(vol[h]))

            # Strictly non-overlapping sequential split of future hour:
            # Early window: minutes 1..15 (index 0..14 of p_f)
            # Late window: minutes 16..60 (index 15..59 of p_f)
            m_early_15m_l1 = float(np.mean(np.abs(p_f[:15])))
            m_early_15m_end = float(np.abs(p_f[14]))
            mae_late_from_0 = float(np.max(np.abs(p_f[15:])))
            mae_late_incremental = float(np.max(np.abs(p_f[15:] - p_f[14])))

            hourly_rows.append({
                "symbol": s,
                "date": d,
                "hour": hr,
                "split": split_name,
                "C3_hat": float(est["C3"]),
                "kappa_hat": float(est["kappa"]),
                "kappa_sq": float(est["kappa"] ** 2),
                "rv_15": float(np.nanstd(dp[t - 15:t])),
                "rv_60": float(np.nanstd(dp[h])),
                "rv_360": float(np.nanstd(dp[w])),
                "rv_day": float(np.nanstd(dp[1:t])),
                "ewma_vol": float(np.sqrt(max(ew[t - 1], 0.0))),
                "abs_ret_60": float(abs(p[t - 1] - p[t - 60])),
                "mae_lag60": float(np.nanmax(np.abs(p_h))),
                "log_vol_60": float(np.log1p(max(v60, 0.0))),
                "log_depth1": float(np.log(max(tot[t - 1], 1e-6))),
                "imbalance": float(imb[t - 1]),
                "m_ckpt_lag": m_ckpt_lag,
                "M_ckpt": m_ckpt_next,
                "M_l1": m_l1_next,
                "M_5m": m_5m_placebo,
                "MAE_60": float(np.max(np.abs(p_f))),
                "M_early_15m_l1": m_early_15m_l1,
                "M_early_15m_end": m_early_15m_end,
                "MAE_late_15_60_from_0": mae_late_from_0,
                "MAE_late_15_60_incremental": mae_late_incremental,
            })

    D25 = pd.DataFrame(hourly_rows).dropna()
    tr25 = D25["split"] == "train"
    clip_cols = [
        "C3_hat", "kappa_hat", "kappa_sq", "rv_15", "rv_60", "rv_360", "rv_day", "ewma_vol",
        "abs_ret_60", "mae_lag60", "log_vol_60", "log_depth1", "imbalance", "m_ckpt_lag",
        "M_ckpt", "M_l1", "M_5m", "MAE_60",
        "M_early_15m_l1", "M_early_15m_end", "MAE_late_15_60_from_0", "MAE_late_15_60_incremental",
    ]
    for c in clip_cols:
        lo, hi = D25.loc[tr25, c].quantile([0.01, 0.99])
        D25[c] = D25[c].clip(lo, hi)

    A25 = D25[tr25].copy()
    B25 = D25[~tr25].sort_values(["date", "symbol", "hour"]).copy()
    syms_25 = sorted(A25["symbol"].unique())

    # 1. Contemporaneous correlation matrix on the test sample AND under a pure Gaussian random-walk null simulation
    path_cols = ["MAE_60", "M_ckpt", "M_l1", "M_5m", "M_early_15m_l1", "MAE_late_15_60_from_0", "MAE_late_15_60_incremental"]
    corr_mat_emp = B25[path_cols].corr().round(4).to_dict()

    rng_rw = np.random.default_rng(20261031)
    rw_steps = rng_rw.normal(0.0, 1.0, size=(20000, 60))
    rw_paths = np.cumsum(rw_steps, axis=1)
    rw_mae60 = np.max(np.abs(rw_paths), axis=1)
    rw_mckpt = np.mean(np.abs(rw_paths[:, 14::15]), axis=1)
    rw_ml1 = np.mean(np.abs(rw_paths), axis=1)
    rw_5m = np.max(np.abs( rw_steps.reshape(20000, 12, 5).sum(axis=2) ), axis=1)
    rw_df = pd.DataFrame({"MAE_60": rw_mae60, "M_ckpt": rw_mckpt, "M_l1": rw_ml1, "M_5m": rw_5m})
    corr_mat_rw_null = rw_df.corr().round(4).to_dict()

    # 2. Strictly non-overlapping sequential persistence regressions
    def _X25(df_sub: pd.DataFrame, cols: list[str]) -> np.ndarray:
        X = [np.ones(len(df_sub))] + [df_sub[c].to_numpy() for c in cols] + [(df_sub["symbol"] == s).to_numpy(float) for s in syms_25[1:]]
        return np.column_stack(X)

    ctrl_25 = [
        "rv_15", "rv_60", "rv_360", "rv_day", "ewma_vol", "abs_ret_60", "mae_lag60",
        "log_vol_60", "log_depth1", "imbalance", "kappa_hat", "kappa_sq", "m_ckpt_lag",
    ]

    def _eval_seq(y_col: str, med_col: str) -> dict:
        y_tr = A25[y_col].to_numpy()
        y_te = B25[y_col].to_numpy()
        sst = float(np.sum((y_te - y_tr.mean()) ** 2))
        fb = _X25(B25, ctrl_25) @ np.linalg.lstsq(_X25(A25, ctrl_25), y_tr, rcond=None)[0]
        ff = _X25(B25, ctrl_25 + ["C3_hat"]) @ np.linalg.lstsq(_X25(A25, ctrl_25 + ["C3_hat"]), y_tr, rcond=None)[0]
        dr2_base = 100.0 * float((np.sum((y_te - fb) ** 2) - np.sum((y_te - ff) ** 2)) / sst)
        cwt_b, cwp_b = cw_test(y_te, fb, ff)

        ctrl_m = ctrl_25 + [med_col]
        fb_m = _X25(B25, ctrl_m) @ np.linalg.lstsq(_X25(A25, ctrl_m), y_tr, rcond=None)[0]
        ff_m = _X25(B25, ctrl_m + ["C3_hat"]) @ np.linalg.lstsq(_X25(A25, ctrl_m + ["C3_hat"]), y_tr, rcond=None)[0]
        dr2_med = 100.0 * float((np.sum((y_te - fb_m) ** 2) - np.sum((y_te - ff_m) ** 2)) / sst)
        cwt_m, cwp_m = cw_test(y_te, fb_m, ff_m)
        share = float((dr2_base - dr2_med) / max(abs(dr2_base), 1e-9))

        return {
            "outcome": y_col,
            "early_mediator": med_col,
            "delta_r2_without_early_mediator_pts": round(dr2_base, 3),
            "cw_t_without_mediator": round(cwt_b, 2),
            "cw_p_without_mediator": float(f"{cwp_b:.6g}"),
            "delta_r2_controlling_early_mediator_pts": round(dr2_med, 3),
            "cw_t_controlling_mediator": round(cwt_m, 2),
            "cw_p_controlling_mediator": float(f"{cwp_m:.6g}"),
            "sequential_attenuation_share": round(share, 3),
        }

    # Also test forecasting the early-window persistence M_early_15m_l1 itself from pre-window C3_hat
    y_e_tr = A25["M_early_15m_l1"].to_numpy()
    y_e_te = B25["M_early_15m_l1"].to_numpy()
    sst_e = float(np.sum((y_e_te - y_e_tr.mean()) ** 2))
    fb_e = _X25(B25, ctrl_25) @ np.linalg.lstsq(_X25(A25, ctrl_25), y_e_tr, rcond=None)[0]
    ff_e = _X25(B25, ctrl_25 + ["C3_hat"]) @ np.linalg.lstsq(_X25(A25, ctrl_25 + ["C3_hat"]), y_e_tr, rcond=None)[0]
    dr2_early = 100.0 * float((np.sum((y_e_te - fb_e) ** 2) - np.sum((y_e_te - ff_e) ** 2)) / sst_e)
    cwt_e, cwp_e = cw_test(y_e_te, fb_e, ff_e)

    return {
        "n_train_hours": len(A25),
        "n_test_hours": len(B25),
        "empirical_test_path_norm_correlations": corr_mat_emp,
        "gaussian_random_walk_null_path_norm_correlations": corr_mat_rw_null,
        "early_15m_persistence_forecast_from_C3": {
            "delta_r2_pts": round(dr2_early, 3),
            "clark_west_t": round(cwt_e, 2),
            "clark_west_p": float(f"{cwp_e:.6g}"),
        },
        "non_overlapping_sequential_tests": {
            "late_15_60_from_0_mediated_by_early_15m_l1": _eval_seq("MAE_late_15_60_from_0", "M_early_15m_l1"),
            "late_15_60_from_0_mediated_by_early_15m_end": _eval_seq("MAE_late_15_60_from_0", "M_early_15m_end"),
            "late_15_60_incremental_mediated_by_early_15m_l1": _eval_seq("MAE_late_15_60_incremental", "M_early_15m_l1"),
            "late_15_60_incremental_mediated_by_early_15m_end": _eval_seq("MAE_late_15_60_incremental", "M_early_15m_end"),
        },
    }


def main() -> None:
    panel, flow_scale = load_panel_and_scales()
    res_p4 = audit_phase_4_guard_benchmarks(panel, flow_scale)
    res_p5 = audit_phase_5_disclosure_hierarchy(panel, flow_scale)
    res_p6 = audit_phase_6_persistence_mechanism(panel, flow_scale)

    out = {
        "phase_4_guard_fair_benchmarks": res_p4,
        "phase_5_disclosure_hierarchy": res_p5,
        "phase_6_persistence_mechanism": res_p6,
    }
    OUT_JSON.parent.mkdir(parents=True, exist_ok=True)
    OUT_JSON.write_text(json.dumps(out, indent=2) + "\n")
    print(f"Wrote {OUT_JSON}")
    print("\n--- PHASE 4 SUMMARY ---")
    print("4B-ii (Unit Train Notional):", json.dumps(res_p4["benchmark_4B_ii_unit_train_normalized_notional"], indent=2))
    print("4C-i (Train-Calibrated Matched ES95):", json.dumps(res_p4["benchmark_4C_i_train_calibrated_matched_es95"], indent=2))
    print("4C-ii (Train-Calibrated Matched Breach):", json.dumps(res_p4["benchmark_4C_ii_train_calibrated_matched_breach_rate"], indent=2))
    print("Unit-Notional VG minus Vol Inference:", res_p4["unit_train_notional_vg_minus_vol_inference"])

    print("\n--- PHASE 5 SUMMARY ---")
    for k, v in res_p5["outcomes"].items():
        print(k, "R2 by model:", v["oos_r2_pts_by_model"])
        print(k, "AR1 share (%):", v["share_of_total_gain_from_current_state_AR1_pct"],
              "| Dynamic share (%):", v["share_of_total_gain_from_dynamic_lags_and_filters_pct"])

    print("\n--- PHASE 6 SUMMARY ---")
    print("RW Null Correlations with MAE_60:", res_p6["gaussian_random_walk_null_path_norm_correlations"]["MAE_60"])
    print("Empirical Correlations with MAE_60:", res_p6["empirical_test_path_norm_correlations"]["MAE_60"])
    print("Sequential Non-Overlapping Tests:", json.dumps(res_p6["non_overlapping_sequential_tests"], indent=2))


if __name__ == "__main__":
    main()
