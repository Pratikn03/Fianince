"""Execute the three pre-registered follow-up empirical tests on untouched 2nd-and-9th-of-month dates (commit b89da25):
  1. Paper 1 Section 8.3 (P1_disclosure_state_oos, sha256 5136cc6b...): Out-of-sample predictive test of
     class-tagged state disclosure filters vs two-exponential price-and-flow filters for 30-minute post-shock
     cross-cohort positioning divergence (Primary 1) and institutional/top-trader positioning state (Primary 2).
  2. Paper 2 Part 24 (P24_guard_throttle_and_capacity, sha256 698f9119...): Pre-registered test of the SEC
     Rule 15c3-5 capped pre-trade throttle q_t in (0, 1] (forced-liquidation rate reduction and daily ES95
     tail-loss reduction on a $1M 20x facility) and matched-breach notional capacity across 42 untouched test dates.
  3. Paper 2 Part 25 (P25_persistence_mechanism, sha256 8ebd67f3...): Pre-registered test of the multi-minute
     price-impact persistence / slow book-reversion mechanism of Theorem thm:sum (forecasting 15-minute
     checkpoint persistence M_ckpt and 60-minute L1 persistence M_l1, and mediating >= 50% of C3_hat's
     out-of-sample excursion predictability, contrasted against the 5-minute single-bar jump placebo M_5m).
"""
from __future__ import annotations

import hashlib
import json
import os
import time
from concurrent.futures import ThreadPoolExecutor, as_completed

import numpy as np
import pandas as pd

from recompute_p2_parts19_20_21 import (
    HERE,
    cw_test,
    fit_t6,
)
from recompute_prereg_oct21_22nd import (
    SYMS_19,
    build_day_22,
    mark_unlock,
)

TRAIN_DATES_24 = sorted([f"2024-{m:02d}-{d:02d}" for m in range(1, 13) for d in (8, 22)])
TEST_DATES_42 = sorted(
    [f"2025-{m:02d}-{d:02d}" for m in range(1, 13) for d in (2, 9)]
    + [f"2026-{m:02d}-{d:02d}" for m in range(1, 10) for d in (2, 9)]
)
ALL_DATES_66 = TRAIN_DATES_24 + TEST_DATES_42

EXPECTED_HASHES = {
    "P1_disclosure_state_oos": (
        "p1_disc_state_res/prereg/P1_disclosure_state_oos.json",
        "5136cc6b846d89d9734f39bf15f0a12f1b80daad40b1cd48079f6c16bef7c522",
    ),
    "P24_guard_throttle_and_capacity": (
        "p24res/prereg/P24_guard_throttle_and_capacity.json",
        "698f91196eba978ad727abb38d45e6de235823ec3013a8b47d1b4af8a67dd9a8",
    ),
    "P25_persistence_mechanism": (
        "p25res/prereg/P25_persistence_mechanism.json",
        "8ebd67f3e9d128b0f407992ffa432b717b93632c9a35d9d2099b5fdba22a2ea5",
    ),
}


def verify_prereg_hashes():
    for tid, (rel_path, exp_hash) in EXPECTED_HASHES.items():
        fp = os.path.join(HERE, "results_archive", "outputs", rel_path)
        actual = hashlib.sha256(open(fp, "rb").read()).hexdigest()
        assert actual == exp_hash, f"Hash mismatch for {tid}: {actual} != {exp_hash}"


def run_p1_disclosure_state_oos(panel: dict, flow_scale: dict) -> dict:
    """Paper 1 Section 8.3 follow-up: Out-of-sample cohort-state divergence and top-trader trajectory test."""
    mark_unlock("p1_disc_state_res/prereg/P1_disclosure_state_oos_unlocks.json")

    # Compute per-symbol 90th percentile of training |q5|
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
    all_rows = []

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

        # Fast (alpha=0.50) and slow (alpha=0.10) exponential memory filters of 5-minute returns and flow
        xf = np.zeros(288)
        xs = np.zeros(288)
        uf = np.zeros(288)
        us = np.zeros(288)
        for t in range(1, 288):
            dp = ret5[t]
            xf[t] = 0.50 * xf[t - 1] + 0.50 * dp
            xs[t] = 0.90 * xs[t - 1] + 0.10 * dp
            uf[t] = 0.50 * uf[t - 1] + 0.50 * u5[t]
            us[t] = 0.90 * us[t - 1] + 0.10 * u5[t]

        split_name = "train" if d <= "2024-12-31" else "test"
        q_thr = q90_map[s]

        for t in range(12, 276):
            nt_b = float(np.mean(ntop[t - 12:t]))
            na_b = float(np.mean(nall[t - 12:t]))
            nt = float(ntop[t] - nt_b)
            na = float(nall[t] - na_b)
            d_nt = float(ntop[t] - ntop[t - 1])
            d_na = float(nall[t] - nall[t - 1])
            div_t = float(nt - na)
            fut_div = float((ntop[t + 6] - nt_b) - (nall[t + 6] - na_b))
            fut_nt = float(ntop[t + 6] - nt_b)

            rec = {
                "symbol": s,
                "date": d,
                "split": split_name,
                "q_shock": float(u5[t]),
                "ret_shock": float(ret5[t]),
                "xf": float(xf[t]),
                "xs": float(xs[t]),
                "uf": float(uf[t]),
                "us": float(us[t]),
                "nt": nt,
                "na": na,
                "d_nt": d_nt,
                "d_na": d_na,
                "div_t": div_t,
                "fut_div_30m": fut_div,
                "fut_nt_30m": fut_nt,
            }
            all_rows.append(rec)
            if abs(u5[t]) >= q_thr:
                shock_rows.append(rec)

    def _eval_subset(rows_list: list[dict], seed_base: int) -> dict:
        DF = pd.DataFrame(rows_list).dropna()
        tr = DF["split"] == "train"
        num_cols = ["q_shock", "ret_shock", "xf", "xs", "uf", "us", "nt", "na", "d_nt", "d_na", "div_t", "fut_div_30m", "fut_nt_30m"]
        for c in num_cols:
            lo, hi = DF.loc[tr, c].quantile([0.01, 0.99])
            DF[c] = DF[c].clip(lo, hi)

        A = DF[tr].copy()
        B = DF[~tr].sort_values(["date", "symbol"]).copy()
        syms_u = sorted(A["symbol"].unique())

        def _X(df_sub: pd.DataFrame, cols: list[str]) -> np.ndarray:
            mats = [np.ones(len(df_sub))] + [df_sub[c].to_numpy() for c in cols] + [(df_sub["symbol"] == s).to_numpy(float) for s in syms_u[1:]]
            return np.column_stack(mats)

        pf_cols = ["q_shock", "ret_shock", "xf", "xs", "uf", "us"]
        tag_cols = pf_cols + ["nt", "na", "d_nt", "d_na", "div_t"]

        X_tr_pf = _X(A, pf_cols)
        X_te_pf = _X(B, pf_cols)
        X_tr_tag = _X(A, tag_cols)
        X_te_tag = _X(B, tag_cols)

        te_dates = B["date"].to_numpy()
        ud = np.unique(te_dates)
        pos = {d: np.where(te_dates == d)[0] for d in ud}

        res_outcomes = {}
        for k_idx, outcome in enumerate(["fut_div_30m", "fut_nt_30m"]):
            y_tr = A[outcome].to_numpy()
            y_te = B[outcome].to_numpy()
            y_bar = float(y_tr.mean())
            sst = float(np.sum((y_te - y_bar) ** 2))

            b_pf = np.linalg.lstsq(X_tr_pf, y_tr, rcond=None)[0]
            b_tag = np.linalg.lstsq(X_tr_tag, y_tr, rcond=None)[0]
            f_pf = X_te_pf @ b_pf
            f_tag = X_te_tag @ b_tag

            r2_pf = float(1.0 - np.sum((y_te - f_pf) ** 2) / sst)
            r2_tag = float(1.0 - np.sum((y_te - f_tag) ** 2) / sst)
            dr2 = float((np.sum((y_te - f_pf) ** 2) - np.sum((y_te - f_tag) ** 2)) / sst)
            cw_t, cw_p = cw_test(y_te, f_pf, f_tag)

            rng = np.random.default_rng(seed_base + k_idx)
            boot_dr2 = []
            for _ in range(2000):
                idx = np.concatenate([pos[d] for d in rng.choice(ud, len(ud))])
                s_draw = float(np.sum((y_te[idx] - y_bar) ** 2))
                boot_dr2.append(100.0 * float((np.sum((y_te[idx] - f_pf[idx]) ** 2) - np.sum((y_te[idx] - f_tag[idx]) ** 2)) / s_draw))
            ci = [float(np.quantile(boot_dr2, 0.025)), float(np.quantile(boot_dr2, 0.975))]

            res_outcomes[outcome] = {
                "r2_price_flow_pct": round(100.0 * r2_pf, 3),
                "r2_class_tagged_pct": round(100.0 * r2_tag, 3),
                "delta_r2_pts": round(100.0 * dr2, 3),
                "delta_r2_ci_pts": [round(ci[0], 3), round(ci[1], 3)],
                "clark_west_t": round(cw_t, 2),
                "clark_west_p": float(f"{cw_p:.6g}"),
                "pass_raw": bool(dr2 > 0 and cw_p < 0.025 and ci[0] > 0),
            }
        return {
            "n_symbols": len(syms_u),
            "n_train": len(A),
            "n_test": len(B),
            "n_test_dates": len(ud),
            "outcomes": res_outcomes,
        }

    shock_eval = _eval_subset(shock_rows, 20261022)
    all_eval = _eval_subset(all_rows, 20261030)

    p1_div = shock_eval["outcomes"]["fut_div_30m"]
    p2_top = shock_eval["outcomes"]["fut_nt_30m"]
    # Holm adjustment across the two primaries
    p_sorted = sorted([(p1_div["clark_west_p"], "primary_1"), (p2_top["clark_west_p"], "primary_2")])
    holm = {}
    run_max = 0.0
    for j, (pval, key) in enumerate(p_sorted):
        run_max = max(run_max, min(1.0, pval * (2 - j)))
        holm[key] = float(f"{run_max:.6g}")

    p1_div["holm_p"] = holm["primary_1"]
    p1_div["pass"] = bool(p1_div["pass_raw"] and holm["primary_1"] < 0.05)
    p2_top["holm_p"] = holm["primary_2"]
    p2_top["pass"] = bool(p2_top["pass_raw"] and holm["primary_2"] < 0.05)

    out_p1 = {
        "test_id": "P1_disclosure_state_oos",
        "spec_sha256": EXPECTED_HASHES["P1_disclosure_state_oos"][1],
        "n_symbols": shock_eval["n_symbols"],
        "n_train_shocks": shock_eval["n_train"],
        "n_test_shocks": shock_eval["n_test"],
        "n_test_dates": shock_eval["n_test_dates"],
        "primary_1_cohort_divergence_30m": p1_div,
        "primary_2_top_trader_state_30m": p2_top,
        "secondary_all_5m_bars": {
            "n_train_bars": all_eval["n_train"],
            "n_test_bars": all_eval["n_test"],
            "cohort_divergence_30m": all_eval["outcomes"]["fut_div_30m"],
            "top_trader_state_30m": all_eval["outcomes"]["fut_nt_30m"],
        },
    }
    print("[Paper 1 Section 8.3 Follow-up: P1_disclosure_state_oos]", json.dumps(out_p1, indent=2))
    os.makedirs(os.path.join(HERE, "results_archive", "outputs", "p1_disc_state_res"), exist_ok=True)
    json.dump(out_p1, open(os.path.join(HERE, "results_archive", "outputs", "p1_disc_state_res", "P1_disclosure_state_oos_results.json"), "w"), indent=2)
    json.dump(out_p1, open(os.path.join(HERE, "recomputed", "R_P1_disclosure_state_oos.json"), "w"), indent=2)
    return out_p1


def run_p24_and_p25(panel: dict, flow_scale: dict) -> tuple[dict, dict]:
    """Paper 2 Part 24 (Rule 15c3-5 capped pre-trade throttle & 42-date capacity) and Part 25 (persistence mechanism)."""
    mark_unlock("p24res/prereg/P24_guard_throttle_and_capacity_unlocks.json")
    mark_unlock("p25res/prereg/P25_persistence_mechanism_unlocks.json")

    daily_pos_rows = []
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

        # Part 24: Non-resetting 18-hour 20x leveraged position entered at 06:00 UTC (t=360) and held until 24:00 UTC
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
            mae_day = float(np.nanmax(np.abs(p[360:1440] - p[359])))
            daily_pos_rows.append({
                "symbol": s,
                "date": d,
                "split": split_name,
                "rv_morn": max(rv_morn, 1e-4),
                "cert_risk": max(u_cert * s60_up, 1e-4),
                "S60_cert": float(est0["S60"]),
                "MAE_day": mae_day,
            })

        # Part 25: Hourly observations for hours 6..22 UTC (forecasting next hour hr -> hr+1)
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
            # 5-minute single-bar jump placebo during hour t..t+60
            p5_window = np.concatenate([[p[t - 1]], p5[hr * 12:(hr + 1) * 12]])
            m_5m_placebo = float(np.max(np.abs(np.diff(p5_window))))
            v60 = float(np.nansum(vol[h]))
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
            })

    # ---------------- Evaluate Part 24 ----------------
    D24 = pd.DataFrame(daily_pos_rows).dropna()
    tr24 = D24["split"] == "train"
    A24 = D24[tr24].copy()
    B24 = D24[~tr24].sort_values(["date", "symbol"]).copy()

    k_vol_map = A24.groupby("symbol")["rv_morn"].median().to_dict()
    k_grd_map = A24.groupby("symbol")["cert_risk"].median().to_dict()

    for df_sub in (A24, B24):
        kv = df_sub["symbol"].map(k_vol_map).to_numpy()
        kg = df_sub["symbol"].map(k_grd_map).to_numpy()
        raw_vol = np.minimum(1.0, kv / df_sub["rv_morn"].to_numpy())
        raw_grd = np.minimum(1.0, kg / df_sub["cert_risk"].to_numpy())
        df_sub["raw_a"] = 1.0
        df_sub["raw_b"] = raw_vol
        df_sub["raw_c"] = raw_vol * raw_grd
        df_sub["raw_d"] = raw_grd

    norm_b = A24.groupby("symbol")["raw_b"].mean().to_dict()
    norm_c = A24.groupby("symbol")["raw_c"].mean().to_dict()
    norm_d = A24.groupby("symbol")["raw_d"].mean().to_dict()

    B24["q_a"] = 1.0
    B24["q_b"] = B24["raw_b"] / B24["symbol"].map(norm_b)
    B24["q_c_unit"] = B24["raw_c"] / B24["symbol"].map(norm_c)
    B24["q_d"] = B24["raw_d"] / B24["symbol"].map(norm_d)

    B_TIER = 450.0
    mae_te = B24["MAE_day"].to_numpy()
    ra = B24["raw_a"].to_numpy()
    rb = B24["raw_b"].to_numpy()
    rc = B24["raw_c"].to_numpy()
    rd = B24["raw_d"].to_numpy()
    qb = B24["q_b"].to_numpy()

    def es95_usd(loss_bp_arr):
        q95 = np.quantile(loss_bp_arr, 0.95)
        return float(np.mean(loss_bp_arr[loss_bp_arr >= q95]) * 100.0)

    def matched_notional(qb_arr, qc_raw_arr, mae_arr):
        target_rate = float(np.mean(qb_arr * mae_arr >= B_TIER))
        mean_notional_b = float(np.mean(qb_arr)) * 1e6
        if target_rate <= 0.0:
            return mean_notional_b, mean_notional_b, 0.0
        thresholds_c = B_TIER / np.maximum(qc_raw_arr * mae_arr, 1e-6)
        c_vg = float(np.quantile(thresholds_c, 1.0 - target_rate))
        mean_notional_c = float(np.mean(c_vg * qc_raw_arr)) * 1e6
        return mean_notional_b, mean_notional_c, target_rate

    # Capped Rule 15c3-5 pre-trade throttle metrics (q_t in (0, 1])
    liq_cap_a = float(np.mean(ra * mae_te >= B_TIER))
    liq_cap_b = float(np.mean(rb * mae_te >= B_TIER))
    liq_cap_c = float(np.mean(rc * mae_te >= B_TIER))
    liq_cap_d = float(np.mean(rd * mae_te >= B_TIER))

    es_cap_a = es95_usd(ra * mae_te)
    es_cap_b = es95_usd(rb * mae_te)
    es_cap_c = es95_usd(rc * mae_te)
    es_cap_d = es95_usd(rd * mae_te)

    diff_liq_pct = 100.0 * (liq_cap_c - liq_cap_b)
    diff_liq_per_not_pct = 100.0 * (liq_cap_c / float(np.mean(rc)) - liq_cap_b / float(np.mean(rb)))
    diff_es_usd = es_cap_c - es_cap_b

    not_b_42, not_c_42, target_breach_42 = matched_notional(qb, rc, mae_te)
    dnot_42 = not_c_42 - not_b_42
    pct_gain_42 = 100.0 * dnot_42 / max(not_b_42, 1.0)

    d24_dates = B24["date"].to_numpy()
    ud24 = np.unique(d24_dates)
    pos24 = {d: np.where(d24_dates == d)[0] for d in ud24}
    rng24 = np.random.default_rng(20261024)
    b_liq_diff, b_liq_per_not, b_es_diff, b_dnot = [], [], [], []
    for _ in range(2000):
        idx = np.concatenate([pos24[d] for d in rng24.choice(ud24, len(ud24))])
        lb_i = float(np.mean(rb[idx] * mae_te[idx] >= B_TIER))
        lc_i = float(np.mean(rc[idx] * mae_te[idx] >= B_TIER))
        b_liq_diff.append(100.0 * (lc_i - lb_i))
        b_liq_per_not.append(100.0 * (lc_i / float(np.mean(rc[idx])) - lb_i / float(np.mean(rb[idx]))))
        b_es_diff.append(es95_usd(rc[idx] * mae_te[idx]) - es95_usd(rb[idx] * mae_te[idx]))
        nb_i, nc_i, _ = matched_notional(qb[idx], rc[idx], mae_te[idx])
        b_dnot.append(nc_i - nb_i)

    ci_liq_diff = [float(np.quantile(b_liq_diff, 0.025)), float(np.quantile(b_liq_diff, 0.975))]
    ci_liq_per_not = [float(np.quantile(b_liq_per_not, 0.025)), float(np.quantile(b_liq_per_not, 0.975))]
    ci_es_diff = [float(np.quantile(b_es_diff, 0.025)), float(np.quantile(b_es_diff, 0.975))]
    ci_dnot_42 = [float(np.quantile(b_dnot, 0.025)), float(np.quantile(b_dnot, 0.975))]

    out24 = {
        "test_id": "P24_guard_throttle_and_capacity",
        "spec_sha256": EXPECTED_HASHES["P24_guard_throttle_and_capacity"][1],
        "n_symbols": len(k_vol_map),
        "n_train_symbol_days": len(A24),
        "n_test_symbol_days": len(B24),
        "n_test_dates": len(ud24),
        "maintenance_margin_buffer_bps": B_TIER,
        "capped_pretrade_rules_1M_facility": {
            "a_static": {"liq_rate_pct": round(100.0 * liq_cap_a, 2), "ES95_day_loss_usd": round(es_cap_a, 0), "mean_notional_usd": 1000000.0},
            "b_vol_cap": {"liq_rate_pct": round(100.0 * liq_cap_b, 2), "ES95_day_loss_usd": round(es_cap_b, 0), "mean_notional_usd": round(float(np.mean(rb)) * 1e6, 0)},
            "c_vol_plus_guard": {"liq_rate_pct": round(100.0 * liq_cap_c, 2), "ES95_day_loss_usd": round(es_cap_c, 0), "mean_notional_usd": round(float(np.mean(rc)) * 1e6, 0)},
            "d_guard_only": {"liq_rate_pct": round(100.0 * liq_cap_d, 2), "ES95_day_loss_usd": round(es_cap_d, 0), "mean_notional_usd": round(float(np.mean(rd)) * 1e6, 0)},
        },
        "primary_1_capped_liq_reduction": {
            "delta_liq_rate_pp": round(diff_liq_pct, 2),
            "delta_liq_rate_ci_pp": [round(ci_liq_diff[0], 2), round(ci_liq_diff[1], 2)],
            "delta_liq_per_1M_deployed_pp": round(diff_liq_per_not_pct, 2),
            "delta_liq_per_1M_deployed_ci_pp": [round(ci_liq_per_not[0], 2), round(ci_liq_per_not[1], 2)],
            "pass": bool(diff_liq_pct < 0 and ci_liq_diff[1] < 0 and diff_liq_per_not_pct < 0 and ci_liq_per_not[1] < 0),
        },
        "primary_2_capped_es95_loss_reduction": {
            "delta_es95_usd": round(diff_es_usd, 0),
            "delta_es95_ci_usd": [round(ci_es_diff[0], 0), round(ci_es_diff[1], 0)],
            "pass": bool(diff_es_usd < 0 and ci_es_diff[1] < 0),
        },
        "secondary_matched_breach_capacity_42dates": {
            "matched_liq_rate_pct": round(100.0 * target_breach_42, 2),
            "notional_vol_cap_usd": round(not_b_42, 0),
            "notional_vol_plus_guard_usd": round(not_c_42, 0),
            "delta_notional_usd": round(dnot_42, 0),
            "delta_notional_ci_usd": [round(ci_dnot_42[0], 0), round(ci_dnot_42[1], 0)],
            "capacity_gain_pct": round(pct_gain_42, 2),
            "ci_above_zero": bool(dnot_42 > 0 and ci_dnot_42[0] > 0),
        },
    }
    print("[Paper 2 Part 24 Result]", json.dumps(out24, indent=2))
    os.makedirs(os.path.join(HERE, "results_archive", "outputs", "p24res"), exist_ok=True)
    json.dump(out24, open(os.path.join(HERE, "results_archive", "outputs", "p24res", "P24_guard_throttle_and_capacity_results.json"), "w"), indent=2)

    # ---------------- Evaluate Part 25 ----------------
    D25 = pd.DataFrame(hourly_rows).dropna()
    tr25 = D25["split"] == "train"
    clip_cols = [
        "C3_hat", "kappa_hat", "kappa_sq", "rv_15", "rv_60", "rv_360", "rv_day", "ewma_vol",
        "abs_ret_60", "mae_lag60", "log_vol_60", "log_depth1", "imbalance", "m_ckpt_lag",
        "M_ckpt", "M_l1", "M_5m", "MAE_60",
    ]
    for c in clip_cols:
        lo, hi = D25.loc[tr25, c].quantile([0.01, 0.99])
        D25[c] = D25[c].clip(lo, hi)

    A25 = D25[tr25].copy()
    B25 = D25[~tr25].sort_values(["date", "symbol", "hour"]).copy()
    syms_25 = sorted(A25["symbol"].unique())

    def _X25(df_sub: pd.DataFrame, cols: list[str]) -> np.ndarray:
        X = [np.ones(len(df_sub))] + [df_sub[c].to_numpy() for c in cols] + [(df_sub["symbol"] == s).to_numpy(float) for s in syms_25[1:]]
        return np.column_stack(X)

    ctrl_25 = [
        "rv_15", "rv_60", "rv_360", "rv_day", "ewma_vol", "abs_ret_60", "mae_lag60",
        "log_vol_60", "log_depth1", "imbalance", "kappa_hat", "kappa_sq", "m_ckpt_lag",
    ]

    # Excursion MAE_60 forecast without mediator
    y_mae_tr = A25["MAE_60"].to_numpy()
    y_mae_te = B25["MAE_60"].to_numpy()
    sst_mae = float(np.sum((y_mae_te - y_mae_tr.mean()) ** 2))
    fb_mae = _X25(B25, ctrl_25) @ np.linalg.lstsq(_X25(A25, ctrl_25), y_mae_tr, rcond=None)[0]
    ff_mae = _X25(B25, ctrl_25 + ["C3_hat"]) @ np.linalg.lstsq(_X25(A25, ctrl_25 + ["C3_hat"]), y_mae_tr, rcond=None)[0]
    dr2_mae_base = float((np.sum((y_mae_te - fb_mae) ** 2) - np.sum((y_mae_te - ff_mae) ** 2)) / sst_mae)
    cw_t_mae, cw_p_mae = cw_test(y_mae_te, fb_mae, ff_mae)

    te_d25 = B25["date"].to_numpy()
    ud25 = np.unique(te_d25)
    pos25 = {d: np.where(te_d25 == d)[0] for d in ud25}

    def _eval_mediator(mcol: str, seed_m: int) -> dict:
        y_m_tr = A25[mcol].to_numpy()
        y_m_te = B25[mcol].to_numpy()
        sst_m = float(np.sum((y_m_te - y_m_tr.mean()) ** 2))
        fb_m = _X25(B25, ctrl_25) @ np.linalg.lstsq(_X25(A25, ctrl_25), y_m_tr, rcond=None)[0]
        ff_m = _X25(B25, ctrl_25 + ["C3_hat"]) @ np.linalg.lstsq(_X25(A25, ctrl_25 + ["C3_hat"]), y_m_tr, rcond=None)[0]
        dr2_m = float((np.sum((y_m_te - fb_m) ** 2) - np.sum((y_m_te - ff_m) ** 2)) / sst_m)
        cwt_m, cwp_m = cw_test(y_m_te, fb_m, ff_m)

        ctrl_med = ctrl_25 + [mcol]
        fb_mae_med = _X25(B25, ctrl_med) @ np.linalg.lstsq(_X25(A25, ctrl_med), y_mae_tr, rcond=None)[0]
        ff_mae_med = _X25(B25, ctrl_med + ["C3_hat"]) @ np.linalg.lstsq(_X25(A25, ctrl_med + ["C3_hat"]), y_mae_tr, rcond=None)[0]
        dr2_mae_med = float((np.sum((y_mae_te - fb_mae_med) ** 2) - np.sum((y_mae_te - ff_mae_med) ** 2)) / sst_mae)
        med_share = float((dr2_mae_base - dr2_mae_med) / max(abs(dr2_mae_base), 1e-9))

        rng_m = np.random.default_rng(seed_m)
        b_dr2_m, b_dr2_mae, b_dr2_mae_med, b_med = [], [], [], []
        for _ in range(2000):
            idx = np.concatenate([pos25[d] for d in rng_m.choice(ud25, len(ud25))])
            sm_i = float(np.sum((y_m_te[idx] - y_m_tr.mean()) ** 2))
            smae_i = float(np.sum((y_mae_te[idx] - y_mae_tr.mean()) ** 2))
            dm_i = float((np.sum((y_m_te[idx] - fb_m[idx]) ** 2) - np.sum((y_m_te[idx] - ff_m[idx]) ** 2)) / sm_i)
            dmae_i = float((np.sum((y_mae_te[idx] - fb_mae[idx]) ** 2) - np.sum((y_mae_te[idx] - ff_mae[idx]) ** 2)) / smae_i)
            dmaem_i = float((np.sum((y_mae_te[idx] - fb_mae_med[idx]) ** 2) - np.sum((y_mae_te[idx] - ff_mae_med[idx]) ** 2)) / smae_i)
            b_dr2_m.append(100.0 * dm_i)
            b_dr2_mae.append(100.0 * dmae_i)
            b_dr2_mae_med.append(100.0 * dmaem_i)
            if abs(dmae_i) > 1e-4:
                b_med.append((dmae_i - dmaem_i) / dmae_i)

        ci_m = [float(np.quantile(b_dr2_m, 0.025)), float(np.quantile(b_dr2_m, 0.975))]
        ci_mae = [float(np.quantile(b_dr2_mae, 0.025)), float(np.quantile(b_dr2_mae, 0.975))]
        ci_mae_med = [float(np.quantile(b_dr2_mae_med, 0.025)), float(np.quantile(b_dr2_mae_med, 0.975))]
        ci_med = [float(np.quantile(b_med, 0.025)), float(np.quantile(b_med, 0.975))]

        return {
            "forecast_delta_r2_pts": round(100.0 * dr2_m, 3),
            "forecast_delta_r2_ci_pts": [round(ci_m[0], 3), round(ci_m[1], 3)],
            "clark_west_t": round(cwt_m, 2),
            "clark_west_p": float(f"{cwp_m:.6g}"),
            "forecast_pass": bool(dr2_m > 0 and cwp_m < 0.025 and ci_m[0] > 0),
            "mae_delta_r2_without_mediator_pts": round(100.0 * dr2_mae_base, 3),
            "mae_delta_r2_without_mediator_ci_pts": [round(ci_mae[0], 3), round(ci_mae[1], 3)],
            "mae_delta_r2_controlling_mediator_pts": round(100.0 * dr2_mae_med, 3),
            "mae_delta_r2_controlling_mediator_ci_pts": [round(ci_mae_med[0], 3), round(ci_mae_med[1], 3)],
            "mediation_share": round(med_share, 3),
            "mediation_share_ci": [round(ci_med[0], 3), round(ci_med[1], 3)],
            "mediation_pass": bool(med_share >= 0.50 and ci_med[0] >= 0.50),
        }

    res_ckpt = _eval_mediator("M_ckpt", 20261025)
    res_l1 = _eval_mediator("M_l1", 20261026)
    res_5m = _eval_mediator("M_5m", 20261027)

    out25 = {
        "test_id": "P25_persistence_mechanism",
        "spec_sha256": EXPECTED_HASHES["P25_persistence_mechanism"][1],
        "n_symbols": len(syms_25),
        "n_train_hours": len(A25),
        "n_test_hours": len(B25),
        "n_test_dates": len(ud25),
        "excursion_forecast_on_02_09": {
            "delta_r2_mae_pts": res_ckpt["mae_delta_r2_without_mediator_pts"],
            "delta_r2_mae_ci_pts": res_ckpt["mae_delta_r2_without_mediator_ci_pts"],
            "clark_west_t": round(cw_t_mae, 2),
            "clark_west_p": float(f"{cw_p_mae:.6g}"),
        },
        "primary_1_forecast_ckpt_persistence": {
            "delta_r2_pers_pts": res_ckpt["forecast_delta_r2_pts"],
            "delta_r2_pers_ci_pts": res_ckpt["forecast_delta_r2_ci_pts"],
            "clark_west_t": res_ckpt["clark_west_t"],
            "clark_west_p": res_ckpt["clark_west_p"],
            "pass": res_ckpt["forecast_pass"],
        },
        "primary_2_mediation_by_ckpt_persistence": {
            "delta_r2_mae_controlling_pers_pts": res_ckpt["mae_delta_r2_controlling_mediator_pts"],
            "delta_r2_mae_controlling_pers_ci_pts": res_ckpt["mae_delta_r2_controlling_mediator_ci_pts"],
            "mediation_share": res_ckpt["mediation_share"],
            "mediation_share_ci": res_ckpt["mediation_share_ci"],
            "pass": bool(res_ckpt["mediation_pass"] and res_5m["mediation_share"] < 0.50),
        },
        "secondary_l1_integral_persistence": res_l1,
        "placebo_5m_single_bar_jump": res_5m,
    }
    print("[Paper 2 Part 25 Result]", json.dumps(out25, indent=2))
    os.makedirs(os.path.join(HERE, "results_archive", "outputs", "p25res"), exist_ok=True)
    json.dump(out25, open(os.path.join(HERE, "results_archive", "outputs", "p25res", "P25_persistence_mechanism_results.json"), "w"), indent=2)
    json.dump({"part24": out24, "part25": out25}, open(os.path.join(HERE, "recomputed", "R_P2_p24_p25.json"), "w"), indent=2)
    return out24, out25


def main():
    t0 = time.time()
    verify_prereg_hashes()
    u2 = json.load(open(os.path.join(HERE, "results_archive", "p9res", "results", "U2_build.json")))["metrics"]["flow_scale"]
    x4 = json.load(open(os.path.join(HERE, "results_archive", "outputs", "p16res", "results", "X4_build.json")))["metrics"]["flow_scale"]
    flow_scale = {**{s: float(u2[s]) for s in u2}, **{s: float(x4[s]) for s in x4}}

    jobs = [(s, d) for s in SYMS_19 for d in ALL_DATES_66]
    print(f"[Follow-up Suite 02/09] Fetching/validating {len(jobs)} symbol-days across {len(SYMS_19)} thin symbols...")
    panel = {}
    with ThreadPoolExecutor(32) as ex:
        futs = {ex.submit(build_day_22, s, d): (s, d) for s, d in jobs}
        done_cnt = 0
        for f in as_completed(futs):
            done_cnt += 1
            res = f.result()
            if res is not None:
                panel[futs[f]] = res
            if done_cnt % 200 == 0:
                print(f"  progress: {done_cnt}/{len(jobs)} symbol-days processed ({len(panel)} valid)...")
    print(f"[Follow-up Suite 02/09] Built {len(panel)} valid symbol-days in {time.time() - t0:.1f}s")

    run_p1_disclosure_state_oos(panel, flow_scale)
    run_p24_and_p25(panel, flow_scale)


if __name__ == "__main__":
    main()
