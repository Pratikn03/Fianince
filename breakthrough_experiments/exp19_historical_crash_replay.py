"""
Breakthrough Experiment 19: Exchange-Authenticated Historical Crisis 1-Second Replay
& Real-Time Resolvent Solvency Guarding Across Four Major Market Crashes
=====================================================================================

Resolves the Section 4.2 empirical limitation ("retained historical scripts simulate
synthetic paths rather than calibrated historical interventions") by downloading,
cryptographically authenticating (via official Binance Vision SHA-256 .CHECKSUM files),
and replaying 345,600 1-second (1s) unnormalized BTCUSDT market intervals across four
major historical market crashes:
  1. May 19, 2021 Crypto Flash Crash (2021-05-19, -31.2% intraday drawdown)
  2. May 9, 2022 Terra/LUNA Algorithmic Stablecoin Collapse (2022-05-09)
  3. November 8, 2022 FTX Solvency Crisis & Liquidity Run (2022-11-08)
  4. March 11, 2023 Silicon Valley Bank (SVB) / USDC Depeg Crisis (2023-03-11)

For each historical crash date, we:
  - Verify the exact SHA-256 digest of the official Binance Vision 1s archive;
  - Construct physical unnormalized 1-second price displacements (in USDT) and signed
    taker order flow v_t = 2 * V_taker_buy,t - V_total,t (in BTC);
  - Estimate the event-day empirical feedback coefficient Q_hat, spectral radius rho_hat,
    and empirical price-impact slope kappa_emp (USDT per BTC);
  - Extract the top 25 most extreme 50-second crash windows per historical event
    (100 real historical crash episodes total);
  - Replay all 100 historical crash episodes through the explicit event-sourced
    double-entry dealer cash, physical inventory, linear-book fill, and January 2023
    Binance USD-M Tier-2 maintenance-margin ledger under four architectures:
      (a) Unguarded Market (No Guard)
      (b) Eigenvalue-Only Guard (rho(J) <= 0.95)
      (c) Static Drawdown Trading Halt (G_halt)
      (d) Real-Time Resolvent Solvency Guard (G_Kreiss)
"""

from __future__ import annotations

import csv
import hashlib
import io
import json
import sys
import urllib.request
import zipfile
from pathlib import Path
from typing import Any

import numpy as np

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from breakthrough_experiments.exp18_crash_free_ai_guard import (
    simulate_double_entry_dealer_episode,
)
OUT_JSON = ROOT / "breakthrough_experiments" / "results_exp19_historical_crash_replay.json"
OUT_TEX = ROOT / "breakthrough_experiments" / "tables" / "table_historical_crash_replay.tex"
CACHE_DIR = Path("/Volumes/T9/machine_markets_data/historical_crashes_20261013")
LOCAL_FALLBACK_CACHE = ROOT / "empirical_pipeline" / "data" / "historical_crashes_cache"

HISTORICAL_CRASH_EVENTS = [
    {
        "event_id": "Crash_I_May2021_FlashCrash",
        "label": "May 19, 2021 Crypto Flash Crash",
        "short_label": "May 2021 Flash Crash",
        "date": "2021-05-19",
        "symbol": "BTCUSDT",
        "expected_sha256": "ba1d18916a471276799bbc1f2a86bf51eed7d8d5a0d1d2eb95496335f146b1c3",
    },
    {
        "event_id": "Crash_II_May2022_TerraLuna",
        "label": "May 9, 2022 Terra/LUNA Stablecoin Collapse",
        "short_label": "May 2022 Terra/LUNA",
        "date": "2022-05-09",
        "symbol": "BTCUSDT",
        "expected_sha256": "a266239425ff510f9aa7f6dc555fefbcad8a355897b4db80dcaa169bc19697fe",
    },
    {
        "event_id": "Crash_III_Nov2022_FTXRun",
        "label": "Nov 8, 2022 FTX Solvency & Liquidity Run",
        "short_label": "Nov 2022 FTX Crisis",
        "date": "2022-11-08",
        "symbol": "BTCUSDT",
        "expected_sha256": "4e18212cf5b9d4c2a1162f0e03e20670005c4d5b2f75771680d8c770f97ba9c7",
    },
    {
        "event_id": "Crash_IV_Mar2023_SVBDepeg",
        "label": "Mar 11, 2023 SVB / USDC Stablecoin Depeg",
        "short_label": "Mar 2023 SVB/USDC",
        "date": "2023-03-11",
        "symbol": "BTCUSDT",
        "expected_sha256": "f9468f3f03cce70772fcd11ad9fd6e0d07d843e93fa18d7ba916db97cc522cf3",
    },
]


def get_storage_dir() -> Path:
    if CACHE_DIR.parent.exists():
        CACHE_DIR.mkdir(parents=True, exist_ok=True)
        return CACHE_DIR
    LOCAL_FALLBACK_CACHE.mkdir(parents=True, exist_ok=True)
    return LOCAL_FALLBACK_CACHE


def download_and_verify_1s_kline(symbol: str, date_str: str, expected_sha256: str | None = None) -> tuple[Path, str]:
    """Download 1s klines zip and official .CHECKSUM from data.binance.vision and verify SHA-256."""
    store = get_storage_dir()
    fname = f"{symbol}-1s-{date_str}.zip"
    zip_path = store / fname
    chk_url = f"https://data.binance.vision/data/spot/daily/klines/{symbol}/1s/{fname}.CHECKSUM"
    zip_url = f"https://data.binance.vision/data/spot/daily/klines/{symbol}/1s/{fname}"

    if not zip_path.exists():
        req_chk = urllib.request.Request(chk_url, headers={"User-Agent": "Mozilla/5.0"})
        chk_text = urllib.request.urlopen(req_chk, timeout=30).read().decode().strip()
        remote_sha = chk_text.split()[0]
        if expected_sha256 is not None and remote_sha != expected_sha256:
            raise ValueError(f"Checksum mismatch against expected for {fname}: {remote_sha} != {expected_sha256}")

        req_zip = urllib.request.Request(zip_url, headers={"User-Agent": "Mozilla/5.0"})
        raw_bytes = urllib.request.urlopen(req_zip, timeout=60).read()
        actual_sha = hashlib.sha256(raw_bytes).hexdigest()
        if actual_sha != remote_sha:
            raise ValueError(f"Downloaded zip SHA-256 mismatch for {fname}: {actual_sha} != {remote_sha}")
        zip_path.write_bytes(raw_bytes)
    else:
        actual_sha = hashlib.sha256(zip_path.read_bytes()).hexdigest()
        if expected_sha256 is not None and actual_sha != expected_sha256:
            raise ValueError(f"Cached zip SHA-256 mismatch for {fname}: {actual_sha} != {expected_sha256}")

    return zip_path, actual_sha


def parse_1s_kline_zip(zip_path: Path) -> dict[str, np.ndarray]:
    """Parse Binance 1s klines zip into numpy arrays of prices, volumes, and signed taker flow."""
    with zipfile.ZipFile(zip_path, "r") as zf:
        csv_names = [n for n in zf.namelist() if n.endswith(".csv")]
        raw_csv = zf.read(csv_names[0]).decode("utf-8")

    ts_list = []
    open_list = []
    high_list = []
    low_list = []
    close_list = []
    vol_list = []
    trades_list = []
    taker_buy_list = []

    reader = csv.reader(io.StringIO(raw_csv))
    for row in reader:
        if not row or not row[0][0].isdigit():
            continue
        ts_list.append(int(row[0]))
        open_list.append(float(row[1]))
        high_list.append(float(row[2]))
        low_list.append(float(row[3]))
        close_list.append(float(row[4]))
        vol_list.append(float(row[5]))
        trades_list.append(int(row[8]))
        taker_buy_list.append(float(row[9]))

    close_arr = np.array(close_list, dtype=float)
    open_arr = np.array(open_list, dtype=float)
    high_arr = np.array(high_list, dtype=float)
    low_arr = np.array(low_list, dtype=float)
    vol_arr = np.array(vol_list, dtype=float)
    taker_buy_arr = np.array(taker_buy_list, dtype=float)
    signed_flow = 2.0 * taker_buy_arr - vol_arr  # physical BTC net market order imbalance

    return {
        "timestamp": np.array(ts_list, dtype=np.int64),
        "open": open_arr,
        "high": high_arr,
        "low": low_arr,
        "close": close_arr,
        "volume": vol_arr,
        "trades": np.array(trades_list, dtype=np.int64),
        "taker_buy_volume": taker_buy_arr,
        "signed_flow": signed_flow,
    }


def analyze_crash_day_and_extract_windows(
    data: dict[str, np.ndarray],
    n_windows: int = 25,
    window_len: int = 50,
) -> tuple[dict[str, float], np.ndarray]:
    """Compute event-day microstructure diagnostics and extract top 25 non-overlapping 50s crash windows."""
    close = data["close"]
    flow = data["signed_flow"]
    n_obs = len(close)

    # 120-second EMA fundamental anchor (alpha = 2 / (120 + 1))
    alpha_ema = 2.0 / 121.0
    ema = np.zeros(n_obs, dtype=float)
    ema[0] = close[0]
    for t in range(1, n_obs):
        ema[t] = (1.0 - alpha_ema) * ema[t - 1] + alpha_ema * close[t]
    disp = close - ema  # pricing error x_t in USDT
    dp = np.diff(close, prepend=close[0])

    # Estimate empirical impact kappa_emp (USDT price change per unit signed BTC flow on active seconds)
    active = np.abs(flow) > 1e-3
    if np.sum(active) > 100:
        kappa_emp = float(
            np.abs(np.cov(dp[active], flow[active])[0, 1]) / (np.var(flow[active]) + 1e-12)
        )
    else:
        kappa_emp = 0.05
    kappa_emp = max(kappa_emp, 0.01)

    # Estimate event-day VAR(1) on standardized (x_t, f_t) where f_t is 60s EMA of signed flow
    alpha_f = 2.0 / 61.0
    f_ema = np.zeros(n_obs, dtype=float)
    for t in range(1, n_obs):
        f_ema[t] = (1.0 - alpha_f) * f_ema[t - 1] + alpha_f * flow[t]

    x_std = disp[500:] / (np.std(disp[500:]) + 1e-12)
    f_std = f_ema[500:] / (np.std(f_ema[500:]) + 1e-12)
    X_reg = np.column_stack([x_std[:-1], f_std[:-1]])
    Y_reg = np.column_stack([x_std[1:], f_std[1:]])
    Phi_hat = np.linalg.lstsq(X_reg, Y_reg, rcond=None)[0].T
    rho_hat = float(np.max(np.abs(np.linalg.eigvals(Phi_hat))))
    q_feedback = float(Phi_hat[0, 1] * Phi_hat[1, 0])

    intraday_high = float(np.max(data["high"]))
    intraday_low = float(np.min(data["low"]))
    intraday_drawdown_pct = 100.0 * (intraday_low - intraday_high) / intraday_high

    # Extract top n_windows non-overlapping 50-second crash windows using a common physical
    # cross-event scale (1-second return in bps and signed BTC flow, anchored to physical
    # drawdown and volume intensity rather than homogenizing each day to the same mean).
    ret_bps = 10000.0 * np.abs(dp) / np.maximum(close, 1.0)
    s_ret_phys = ret_bps / 2.20          # physical reference: 2.20 bps per second
    s_fl_phys = np.abs(flow) / 14.0      # physical reference: 14.0 BTC net flow per second
    combined = 0.65 * s_ret_phys + 0.35 * s_fl_phys

    n_avail = len(combined) // window_len
    wins = combined[: n_avail * window_len].reshape(n_avail, window_len)
    energies = np.sum(wins ** 2, axis=1)
    top_idx = np.argsort(energies)[-n_windows:]
    sel = wins[top_idx]

    # Physical severity factor anchored to the event's realized intraday drawdown and 99.9th pct 1s return burst
    p999_ret_bps = float(np.percentile(ret_bps, 99.9))
    dd_frac = abs(intraday_drawdown_pct) / 100.0
    phys_event_amp = float(np.clip(0.25 + 0.52 * dd_frac + 0.0022 * p999_ret_bps, 0.26, 0.48))
    sel = sel / max(float(np.mean(sel)), 1e-8) * phys_event_amp

    out = np.zeros((n_windows, window_len, 3), dtype=float)
    out[:, :, 0] = sel * 0.20
    out[:, :, 1] = sel * 0.35
    out[:, :, 2] = sel * 0.55

    # Local 1-second signed crash-burst state-space matrix Z_burst_1s (no abs() folding!):
    # z1: signed price displacement in 0.50-bp calm-SD units (10 USDT MTM on 200k notional)
    # z2: signed fast order-flow momentum in 50-BTC institutional blocks
    # z3: signed aggressive order-splitting / sweep imbalance: (flow / (vol + 5)) * log1p(trades) / 10
    vol = data["volume"]
    trades = data["trades"].astype(float)
    signed_ret_bps = 10000.0 * dp / np.maximum(close, 1.0)
    signed_sweep = (flow / (vol + 5.0)) * (np.log1p(trades) / 10.0)
    z1_s = np.zeros(n_obs, dtype=float)
    z2_s = np.zeros(n_obs, dtype=float)
    z3_s = np.zeros(n_obs, dtype=float)
    for t in range(1, n_obs):
        z1_s[t] = 0.76 * z1_s[t - 1] + (signed_ret_bps[t] / 0.50)
        z2_s[t] = 0.72 * z2_s[t - 1] + (flow[t] / 50.0)
        z3_s[t] = 0.68 * z3_s[t - 1] + signed_sweep[t]
    Z_all_signed = np.column_stack([z1_s, z2_s, z3_s])
    rows_prev = np.concatenate([np.arange(int(i) * window_len, (int(i) + 1) * window_len - 1) for i in top_idx])
    rows_next = rows_prev + 1
    Zp_ev = Z_all_signed[rows_prev]
    Zn_ev = Z_all_signed[rows_next]
    J_burst_ev_ols = (np.linalg.inv(Zp_ev.T @ Zp_ev + 2.0 * np.eye(3)) @ (Zp_ev.T @ Zn_ev)).T
    rho_b_ev, comm_b_ev, mc_b_ev, cg_b_ev = compute_3state_price_metrics(J_burst_ev_ols)

    # Also extract the unmodified physical signed 1-second price and signed flow windows
    signed_windows = []
    for w_idx in top_idx:
        s = int(w_idx) * window_len
        e = s + window_len
        signed_windows.append({
            "start_sec": s,
            "close_usdt": close[s:e].copy(),
            "open_usdt": float(data["open"][s]),
            "high_usdt": float(np.max(data["high"][s:e])),
            "low_usdt": float(np.min(data["low"][s:e])),
            "signed_flow_btc": flow[s:e].copy(),
            "signed_dp_usdt": dp[s:e].copy(),
            "Zp_ev": Zp_ev,
            "Zn_ev": Zn_ev,
        })

    stats = {
        "n_seconds": int(n_obs),
        "open_price_usdt": float(data["open"][0]),
        "close_price_usdt": float(close[-1]),
        "intraday_high_usdt": intraday_high,
        "intraday_low_usdt": intraday_low,
        "intraday_drawdown_pct": float(intraday_drawdown_pct),
        "total_btc_volume": float(np.sum(data["volume"])),
        "total_trades": int(np.sum(data["trades"])),
        "max_1s_signed_flow_btc": float(np.max(np.abs(flow))),
        "p999_1s_return_bps": p999_ret_bps,
        "physical_event_shock_amplitude": phys_event_amp,
        "empirical_impact_usdt_per_btc": float(kappa_emp),
        "var1_spectral_radius": rho_hat,
        "var1_feedback_product_Q": q_feedback,
        "burst_ols_3x3_spectral_radius": rho_b_ev,
        "burst_ols_3x3_frobenius_nonnormality": comm_b_ev,
        "burst_ols_3x3_price_output_gain_MC": mc_b_ev,
        "burst_ols_3x3_cumulative_gain": cg_b_ev,
        "burst_ols_3x3_matrix": [[float(x) for x in row] for row in J_burst_ev_ols],
    }
    return stats, out, signed_windows


def compute_3state_price_metrics(J: np.ndarray, horizon: int = 25) -> tuple[float, float, float, float]:
    """Compute spectral radius, Frobenius commutator norm, and price-output transient gain M_{C_price}(J)."""
    C_price = np.array([[1.0, 0.0, 0.0]], dtype=float)
    rho = float(np.max(np.abs(np.linalg.eigvals(J))))
    comm = float(np.linalg.norm(J @ J.T - J.T @ J, ord="fro"))
    Jt = np.eye(3, dtype=float)
    mc = 1.0
    cg = 0.0
    for _ in range(horizon):
        bn = float(np.linalg.norm(C_price @ Jt, ord=2))
        mc = max(mc, bn)
        cg += bn
        Jt = Jt @ J
    return rho, comm, mc, cg


def simulate_empirical_burst_ols_episode(
    shocks: np.ndarray,
    J_emp: np.ndarray,
    architecture: str,
) -> dict[str, float | bool]:
    """Replay a 50-second crash window through the empirically estimated signed crash-burst OLS
    operator J_emp(alpha_t) = diag(J_emp) + alpha_t * (J_emp - diag(J_emp)) (estimated directly by
    ridge OLS on the signed 1-second crash windows without synthetic matrix constants).
    """
    C_price = np.array([[1.0, 0.0, 0.0]], dtype=float)
    E0 = 10000.0
    P0 = 100.0
    inv = -2000.0
    cash = E0 - inv * P0
    p_curr = P0

    d_emp = np.diag(np.diag(J_emp))
    off_emp = J_emp - d_emp
    table = []
    for g in np.linspace(0.0, 1.0, 41):
        Jg = d_emp + float(g) * off_emp
        rho_g, comm_g, mc_g, cg_g = compute_3state_price_metrics(Jg)
        table.append((float(g), rho_g, comm_g, mc_g, cg_g, Jg))

    z = np.zeros(3, dtype=float)
    min_eq = E0
    max_dd = 0.0
    liq = False
    halted = False
    gammas = []

    for t in range(len(shocks)):
        eq_curr = cash + inv * p_curr
        mm_curr = max(0.0, 0.005 * abs(inv) * p_curr - 50.0)
        rem_buf = (eq_curr - mm_curr) - 950.0

        if architecture == "Unguarded":
            g_star, _, _, _, _, J_t = table[-1]
        elif architecture == "Eigenvalue_Guard":
            feas = [r for r in table if r[1] <= 0.95]
            g_star, _, _, _, _, J_t = feas[-1]
        elif architecture == "Static_Halt":
            if (E0 - eq_curr) >= 0.55 * 9050.0:
                halted = True
            g_star, _, _, _, _, J_t = table[0] if halted else table[-1]
        elif architecture == "Resolvent_Guard_Kreiss":
            z_norm = float(np.linalg.norm(z))
            chosen = table[0]
            for row in table:
                gv, rhov, _, mcv, cgv, _ = row
                if rhov >= 0.95:
                    continue
                est_h = -0.06 * (1.0 - gv) * inv if gv < 0.99 else 0.0
                est_hc = abs(est_h) * (0.02 + 0.0004 * max(p_curr, P0))
                pred_exc = mcv * z_norm * 0.35 + (cgv - 1.0) * 0.16
                if abs(inv) * pred_exc + est_hc <= max(rem_buf, 250.0):
                    chosen = row
            g_star, _, _, _, _, J_t = chosen
        else:
            raise ValueError(f"Unknown architecture: {architecture}")

        gammas.append(g_star)
        if architecture == "Resolvent_Guard_Kreiss" and g_star < 0.99:
            h_qty = -0.06 * (1.0 - g_star) * inv
            h_cost = abs(h_qty) * (0.02 + 0.0004 * max(p_curr, P0))
            cash -= h_qty * p_curr + h_cost
            inv += h_qty

        s_scale = 1.0 if architecture in ("Unguarded", "Eigenvalue_Guard") else (0.15 + 0.85 * g_star)
        z_next = J_t @ z + s_scale * shocks[t]
        p_next = P0 + float((C_price @ z_next).item())
        flow_q = -18.0 * s_scale * float(shocks[t, 0])
        exec_p = 0.5 * (p_curr + p_next)
        spread_rev = 0.02 * abs(flow_q) * (0.0 if halted else 1.0)
        cash = cash - flow_q * exec_p + spread_rev
        inv = inv + flow_q
        z = z_next
        p_curr = p_next

        eq_next = cash + inv * p_curr
        mm_next = max(0.0, 0.005 * abs(inv) * p_curr - 50.0)
        min_eq = min(min_eq, eq_next)
        max_dd = max(max_dd, max(0.0, E0 - eq_next))
        if eq_next <= mm_next:
            liq = True

    g_mean = float(np.mean(gammas))
    elig_pct = 100.0 * float(np.mean([1.0 if (not halted and g >= 0.05) else 0.0 for g in gammas]))
    return {
        "liquidated": bool(liq),
        "min_equity_usdt": float(max(0.0, min_eq)),
        "max_drawdown_usdt": float(min(E0, max_dd)),
        "mean_admission_gamma": g_mean,
        "admitted_depth_share_pct": 100.0 * g_mean,
        "model_admission_eligibility_pct": elig_pct,
        "two_sided_quote_availability_pct": elig_pct,
    }



def simulate_physical_signed_window(
    win: dict[str, Any],
    kappa_emp: float,
    architecture: str,
) -> dict[str, float | bool]:
    """Replay the unmodified signed 1-second BTCUSDT price changes and signed net taker flow
    on a 200,000 USDT notional dealer account (E_0 = 10,000 USDT, 20x leverage, Tier-2 MM_0 = 950 USDT)
    without abs() magnitude folding or synthetic 3x3 upper-triangular projection.
    """
    close_path = win["close_usdt"]
    flow_path = win["signed_flow_btc"]
    T_steps = len(close_path)
    p0 = float(close_path[0])
    # Position signed against the window's dominant adverse excursion so a 20x leveraged dealer is stress-tested
    net_move = float(close_path[-1] - close_path[0])
    max_up = float(np.max(close_path) - p0)
    max_dn = float(p0 - np.min(close_path))
    adverse_sign = -1.0 if max_up >= max_dn else 1.0  # -1 = short 200k USDT, +1 = long 200k USDT
    inv = adverse_sign * (200000.0 / max(p0, 1.0))
    cash = 10000.0 - inv * p0
    p_curr = p0

    min_eq = 10000.0
    max_dd = 0.0
    liquidated = False
    gammas = []
    halted = False
    desk_share = 0.0025  # 0.25% of global Binance spot flow absorbed by single dealer desk

    for t in range(T_steps):
        eq_curr = cash + inv * p_curr
        mm_curr = max(0.0, 0.005 * abs(inv) * p_curr - 50.0)
        rem_buf = (eq_curr - mm_curr) - 950.0

        if architecture in ("Unguarded", "Eigenvalue_Guard"):
            g_star = 1.0
        elif architecture == "Static_Halt":
            if (10000.0 - eq_curr) >= 0.55 * 9050.0:
                halted = True
            g_star = 0.0 if halted else 1.0
        elif architecture == "Resolvent_Guard_Kreiss":
            recent_vol = float(np.abs(close_path[t] - p_curr)) + kappa_emp * abs(float(flow_path[t]))
            pred_loss = abs(inv) * recent_vol * 2.5
            if pred_loss <= max(rem_buf, 200.0):
                g_star = 1.0
            else:
                g_star = float(np.clip(max(rem_buf, 0.0) / max(pred_loss, 1e-6), 0.05, 1.0))
        else:
            raise ValueError(f"Unknown architecture: {architecture}")

        gammas.append(g_star)

        if architecture == "Resolvent_Guard_Kreiss" and g_star < 0.99:
            hedge_qty = -0.12 * (1.0 - g_star) * inv
            hedge_cost = abs(hedge_qty) * p_curr * 0.0005  # 1 bp half-spread + 4 bp taker fee
            cash -= hedge_qty * p_curr + hedge_cost
            inv += hedge_qty

        # Actual signed historical price plus endogenous transient flow impact from admitted AI flow
        p_next = float(close_path[t]) - adverse_sign * (g_star ** 2) * kappa_emp * 0.35 * abs(float(flow_path[t]))
        flow_abs = desk_share * g_star * float(flow_path[t])
        exec_p = 0.5 * (p_curr + p_next)
        spread_rev = abs(flow_abs) * p_curr * 0.0001 * (0.0 if halted else 1.0)
        cash = cash - flow_abs * exec_p + spread_rev
        inv = inv + flow_abs
        p_curr = p_next

        eq_next = cash + inv * p_curr
        mm_next = max(0.0, 0.005 * abs(inv) * p_curr - 50.0)
        min_eq = min(min_eq, eq_next)
        max_dd = max(max_dd, max(0.0, 10000.0 - eq_next))
        if eq_next <= mm_next:
            liquidated = True

    elig_pct = 100.0 * float(np.mean([1.0 if (not halted and g >= 0.05) else 0.0 for g in gammas]))
    return {
        "liquidated": bool(liquidated),
        "min_equity_usdt": float(max(0.0, min_eq)),
        "max_drawdown_usdt": float(min(10000.0, max_dd)),
        "admitted_depth_share_pct": 100.0 * float(np.mean(gammas)),
        "model_admission_eligibility_pct": elig_pct,
        "two_sided_quote_availability_pct": elig_pct,
    }


def run_experiment() -> dict[str, Any]:
    architectures = ["Unguarded", "Eigenvalue_Guard", "Static_Halt", "Resolvent_Guard_Kreiss"]
    event_summaries: dict[str, Any] = {}
    all_arch_agg: dict[str, list[dict[str, float]]] = {a: [] for a in architectures}
    all_phys_agg: dict[str, list[dict[str, float | bool]]] = {a: [] for a in architectures}
    all_burst_ols_agg: dict[str, list[dict[str, float | bool]]] = {a: [] for a in architectures}

    # First pass: load and verify all 4 historical crashes and pool the 100 signed crash windows for J_burst_pool_ols
    loaded_events = []
    all_Zp = []
    all_Zn = []
    for ev in HISTORICAL_CRASH_EVENTS:
        zip_path, verified_sha = download_and_verify_1s_kline(
            ev["symbol"], ev["date"], ev["expected_sha256"]
        )
        parsed = parse_1s_kline_zip(zip_path)
        day_stats, windows, signed_windows = analyze_crash_day_and_extract_windows(parsed, n_windows=25, window_len=50)
        all_Zp.append(signed_windows[0]["Zp_ev"])
        all_Zn.append(signed_windows[0]["Zn_ev"])
        loaded_events.append((ev, verified_sha, day_stats, windows, signed_windows))

    Zp_pool = np.vstack(all_Zp)
    Zn_pool = np.vstack(all_Zn)
    J_burst_pool_ols = (np.linalg.inv(Zp_pool.T @ Zp_pool + 2.0 * np.eye(3)) @ (Zp_pool.T @ Zn_pool)).T
    rho_pool, comm_pool, mc_pool, cg_pool = compute_3state_price_metrics(J_burst_pool_ols)

    for ev, verified_sha, day_stats, windows, signed_windows in loaded_events:
        ev_arch_results: dict[str, Any] = {}
        ev_phys_results: dict[str, Any] = {}
        ev_burst_ols_results: dict[str, Any] = {}
        for arch in architectures:
            ep_list = []
            phys_list = []
            burst_ols_list = []
            for w, sw in zip(windows, signed_windows):
                res = simulate_double_entry_dealer_episode(
                    shocks=w,
                    regime="Regime_IV_Binance_Empirical_Replay",
                    architecture=arch,
                )
                ep_list.append(res)
                all_arch_agg[arch].append(res)

                pres = simulate_physical_signed_window(
                    win=sw,
                    kappa_emp=day_stats["empirical_impact_usdt_per_btc"],
                    architecture=arch,
                )
                phys_list.append(pres)
                all_phys_agg[arch].append(pres)

                bres = simulate_empirical_burst_ols_episode(
                    shocks=w,
                    J_emp=J_burst_pool_ols,
                    architecture=arch,
                )
                burst_ols_list.append(bres)
                all_burst_ols_agg[arch].append(bres)

            liq_rate = 100.0 * float(np.mean([r["liquidated"] for r in ep_list]))
            min_eq = float(np.mean([r["min_equity_usdt"] for r in ep_list]))
            p05_eq = float(np.percentile([r["min_equity_usdt"] for r in ep_list], 5))
            max_dd = float(np.mean([r["max_drawdown_usdt"] for r in ep_list]))
            uptime = float(np.mean([r["two_sided_quote_availability_pct"] for r in ep_list]))
            gamma_mean = float(np.mean([r["mean_admission_gamma"] for r in ep_list]))

            ev_arch_results[arch] = {
                "liquidation_rate_pct": liq_rate,
                "mean_min_equity_usdt": min_eq,
                "p05_min_equity_usdt": p05_eq,
                "mean_max_drawdown_usdt": max_dd,
                "quote_uptime_pct": uptime,
                "model_admission_eligibility_pct": uptime,
                "two_sided_quote_availability_pct": uptime,
                "admitted_depth_share_pct": 100.0 * gamma_mean,
                "throttled_flow_share_pct": 100.0 * (1.0 - gamma_mean),
                "mean_admission_gamma": gamma_mean,
            }
            phys_elig = float(np.mean([r["two_sided_quote_availability_pct"] for r in phys_list]))
            ev_phys_results[arch] = {
                "liquidation_rate_pct": 100.0 * float(np.mean([r["liquidated"] for r in phys_list])),
                "mean_min_equity_usdt": float(np.mean([r["min_equity_usdt"] for r in phys_list])),
                "mean_max_drawdown_usdt": float(np.mean([r["max_drawdown_usdt"] for r in phys_list])),
                "admitted_depth_share_pct": float(np.mean([r["admitted_depth_share_pct"] for r in phys_list])),
                "model_admission_eligibility_pct": phys_elig,
                "two_sided_quote_availability_pct": phys_elig,
            }
            b_elig = float(np.mean([r["two_sided_quote_availability_pct"] for r in burst_ols_list]))
            ev_burst_ols_results[arch] = {
                "liquidation_rate_pct": 100.0 * float(np.mean([r["liquidated"] for r in burst_ols_list])),
                "mean_min_equity_usdt": float(np.mean([r["min_equity_usdt"] for r in burst_ols_list])),
                "mean_max_drawdown_usdt": float(np.mean([r["max_drawdown_usdt"] for r in burst_ols_list])),
                "admitted_depth_share_pct": float(np.mean([r["admitted_depth_share_pct"] for r in burst_ols_list])),
                "model_admission_eligibility_pct": b_elig,
                "two_sided_quote_availability_pct": b_elig,
            }

        event_summaries[ev["event_id"]] = {
            "label": ev["label"],
            "short_label": ev["short_label"],
            "date": ev["date"],
            "symbol": ev["symbol"],
            "sha256_verified": verified_sha,
            "sha256_matches_official_checksum": verified_sha == ev["expected_sha256"],
            "day_stats": day_stats,
            "architectures": ev_arch_results,
            "physical_signed_replay_architectures": ev_phys_results,
            "empirical_burst_ols_replay_architectures": ev_burst_ols_results,
        }

    overall_summary: dict[str, Any] = {}
    overall_phys_summary: dict[str, Any] = {}
    overall_burst_ols_summary: dict[str, Any] = {}
    for arch in architectures:
        ep_list = all_arch_agg[arch]
        g_mean = float(np.mean([r["mean_admission_gamma"] for r in ep_list]))
        ov_elig = float(np.mean([r["two_sided_quote_availability_pct"] for r in ep_list]))
        overall_summary[arch] = {
            "total_episodes": len(ep_list),
            "liquidation_rate_pct": 100.0 * float(np.mean([r["liquidated"] for r in ep_list])),
            "mean_min_equity_usdt": float(np.mean([r["min_equity_usdt"] for r in ep_list])),
            "p05_min_equity_usdt": float(np.percentile([r["min_equity_usdt"] for r in ep_list], 5)),
            "worst_min_equity_usdt": float(np.min([r["min_equity_usdt"] for r in ep_list])),
            "mean_max_drawdown_usdt": float(np.mean([r["max_drawdown_usdt"] for r in ep_list])),
            "quote_uptime_pct": ov_elig,
            "model_admission_eligibility_pct": ov_elig,
            "two_sided_quote_availability_pct": ov_elig,
            "admitted_depth_share_pct": 100.0 * g_mean,
            "throttled_flow_share_pct": 100.0 * (1.0 - g_mean),
            "mean_admission_gamma": g_mean,
        }
        plist = all_phys_agg[arch]
        p_elig = float(np.mean([r["two_sided_quote_availability_pct"] for r in plist]))
        overall_phys_summary[arch] = {
            "total_episodes": len(plist),
            "liquidation_rate_pct": 100.0 * float(np.mean([r["liquidated"] for r in plist])),
            "mean_min_equity_usdt": float(np.mean([r["min_equity_usdt"] for r in plist])),
            "mean_max_drawdown_usdt": float(np.mean([r["max_drawdown_usdt"] for r in plist])),
            "admitted_depth_share_pct": float(np.mean([r["admitted_depth_share_pct"] for r in plist])),
            "model_admission_eligibility_pct": p_elig,
            "two_sided_quote_availability_pct": p_elig,
        }
        blist = all_burst_ols_agg[arch]
        b_elig = float(np.mean([r["two_sided_quote_availability_pct"] for r in blist]))
        overall_burst_ols_summary[arch] = {
            "total_episodes": len(blist),
            "liquidation_rate_pct": 100.0 * float(np.mean([r["liquidated"] for r in blist])),
            "mean_min_equity_usdt": float(np.mean([r["min_equity_usdt"] for r in blist])),
            "mean_max_drawdown_usdt": float(np.mean([r["max_drawdown_usdt"] for r in blist])),
            "admitted_depth_share_pct": float(np.mean([r["admitted_depth_share_pct"] for r in blist])),
            "model_admission_eligibility_pct": b_elig,
            "two_sided_quote_availability_pct": b_elig,
        }

    results = {
        "experiment": "exp19_historical_crash_replay",
        "methodology_classification": (
            "Three-mode counterfactual evaluation on historical spot series: (1) Historical-Data-Conditioned "
            "Synthetic Non-Normal Stress Benchmark (rho=0.780, M_C=40.79), (2) Direct Physical Signed Historical "
            "Price & Flow Replay on actual BTCUSDT prices and signed net taker volumes, and (3) Empirically Estimated "
            "Signed 1-Second Crash-Burst OLS Operator Replay (J_hat_burst^OLS estimated directly by unconstrained "
            "ridge OLS on the 100 signed 1s crash windows with zero abs() folding and zero synthetic matrix constants: "
            f"rho={rho_pool:.4f} < 1, commutator={comm_pool:.2f}, M_{{C_price}}={mc_pool:.2f})."
        ),
        "transformation_disclosure": {
            "spot_archive_source": "data.binance.vision/data/spot/daily/klines/BTCUSDT/1s/",
            "margin_schedule_paired": "Binance USD(S)-M Futures Tier-2 (Jan 2023, rate=0.5%, fast_amt=50 USDT)",
            "stress_benchmark_abs_folding": True,
            "stress_benchmark_state_projection": [0.20, 0.35, 0.55],
            "physical_signed_replay_included": True,
            "empirical_burst_ols_replay_included": True,
            "empirical_burst_ols_abs_folding": False,
            "empirical_burst_ols_synthetic_constants": False,
            "dealer_account_modeled_counterfactual": True,
        },
        "pooled_burst_ols_operator": {
            "n_1s_burst_transitions": int(Zp_pool.shape[0]),
            "spectral_radius": rho_pool,
            "frobenius_nonnormality": comm_pool,
            "price_output_gain_MC": mc_pool,
            "cumulative_gain": cg_pool,
            "matrix": [[float(x) for x in row] for row in J_burst_pool_ols],
        },
        "total_1s_records_verified": sum(
            event_summaries[k]["day_stats"]["n_seconds"] for k in event_summaries
        ),
        "total_crash_episodes": 100,
        "events": event_summaries,
        "overall_100_episode_summary": overall_summary,
        "overall_100_episode_physical_signed_summary": overall_phys_summary,
        "overall_100_episode_empirical_burst_ols_summary": overall_burst_ols_summary,
    }

    OUT_JSON.write_text(json.dumps(results, indent=2))
    write_latex_table(results)
    return results


def write_latex_table(results: dict[str, Any]) -> None:
    OUT_TEX.parent.mkdir(parents=True, exist_ok=True)
    evs = results["events"]
    ov = results["overall_100_episode_summary"]
    ov_phys = results["overall_100_episode_physical_signed_summary"]
    ov_burst = results["overall_100_episode_empirical_burst_ols_summary"]
    pb = results["pooled_burst_ols_operator"]

    lines = [
        r"\begin{table}[htbp]\centering\scriptsize",
        r"\caption{Exchange-Authenticated Historical Crisis Archives ($345{,}600$ 1-Second Spot BTCUSDT Bars from \texttt{data.binance.vision}, Official SHA-256 Verified) Evaluated Across Three Modes ($E_0 = 10{,}000$~USDT, $200{,}000$~USDT Notional at $L=20$, Paired with January 2023 Binance USD$\circledS$-M Tier-2 Maintenance Margin $B_{\mathrm{rem},0} = 9{,}050$~USDT): Panel~A reports unnormalized physical event diagnostics and event-specific 1s crash-burst OLS transient gain $\mathcal{M}_{\mathcal{C}}(\hat{J}_{\mathrm{burst},e}^{\mathrm{OLS}})$. Panel~B reports the historical-data-conditioned non-normal stress benchmark ($\rho=0.780$, $\mathcal{M}_{\mathcal{C}}=40.79$). Panel~C reports direct unamplified physical signed price/flow replay. Panel~D reports replay under the empirically estimated 1-second signed crash-burst OLS operator $\hat{J}_{\mathrm{burst,pool}}^{\mathrm{OLS}}$ ($\rho = "
        + f"{pb['spectral_radius']:.4f} < 1$, Commutator $= {pb['frobenius_nonnormality']:.2f}$, $\\mathcal{{M}}_{{\\mathcal{{C}}_{{\\mathrm{{price}}}}}}(\\hat{{J}}_{{\\mathrm{{burst,pool}}}}^{{\\mathrm{{OLS}}}}) = {pb['price_output_gain_MC']:.2f}$, estimated directly by unconstrained ridge OLS on the signed 1s crash windows with zero synthetic matrix constants).}}",
        r"\label{iatab:historical_crash_replay}",
        r"\resizebox{\textwidth}{!}{%",
        r"\begin{tabular}{lrrrrrrr}",
        r"\toprule",
        r"\multicolumn{8}{l}{\textbf{Panel A: Authenticated 1-Second Historical Crisis Archives (\texttt{data.binance.vision}, SHA-256 Verified)}} \\",
        r"\midrule",
        r"Historical Crisis Event & UTC Date & 1s Bars & High (USDT) & Low (USDT) & Intraday Drop & Volume (BTC) & Burst OLS $\mathcal{M}_{\mathcal{C}}$ ($\rho$) \\",
        r"\midrule",
    ]

    for ev_meta in HISTORICAL_CRASH_EVENTS:
        eid = ev_meta["event_id"]
        e = evs[eid]
        ds = e["day_stats"]
        lines.append(
            f"{e['short_label']} & {e['date']} & {ds['n_seconds']:,} & "
            f"{ds['intraday_high_usdt']:,.2f} & {ds['intraday_low_usdt']:,.2f} & "
            f"{ds['intraday_drawdown_pct']:.2f}\\% & {ds['total_btc_volume']:,.0f} & "
            f"{ds['burst_ols_3x3_price_output_gain_MC']:.2f} ({ds['burst_ols_3x3_spectral_radius']:.3f}) \\\\"
        )

    lines.extend([
        r"\midrule",
        r"\multicolumn{8}{l}{\textbf{Panel B: Historical-Data-Conditioned Non-Normal Stress Benchmark (100 Crisis Windows, $\rho=0.780$, $\mathcal{M}_{\mathcal{C}_{\mathrm{price}}}=40.79$)}} \\",
        r"\midrule",
        r"Market Safety Architecture & May 2021 Liq.\ & May 2022 Liq.\ & Nov 2022 Liq.\ & Mar 2023 Liq.\ & All-100 Liq.\ & Mean $\min_t E_t$ & Depth $\bar{\alpha}_t$ / Adm.\ Elig. \\",
        r"\midrule",
    ])

    arch_labels = [
        ("Unguarded", "1. Unguarded Market ($\\alpha_t = 1$)"),
        ("Eigenvalue_Guard", "2. Eigenvalue-Only Guard ($\\rho(J) \\le 0.95$)"),
        ("Static_Halt", "3. Static Drawdown Halt ($\\mathcal{G}_{\\mathrm{halt}}$)"),
        ("Resolvent_Guard_Kreiss", "\\textbf{4. Resolvent Guard ($\\mathcal{G}_{\\mathrm{Kreiss}}$, Ours)}"),
    ]

    e_keys = [ev["event_id"] for ev in HISTORICAL_CRASH_EVENTS]
    for akey, alabel in arch_labels:
        l1 = evs[e_keys[0]]["architectures"][akey]["liquidation_rate_pct"]
        l2 = evs[e_keys[1]]["architectures"][akey]["liquidation_rate_pct"]
        l3 = evs[e_keys[2]]["architectures"][akey]["liquidation_rate_pct"]
        l4 = evs[e_keys[3]]["architectures"][akey]["liquidation_rate_pct"]
        po = ov[akey]
        depth_avail = f"{po['admitted_depth_share_pct']:.1f}\\% / {po['model_admission_eligibility_pct']:.1f}\\%"
        if akey == "Resolvent_Guard_Kreiss":
            lines.append(
                f"{alabel} & \\textbf{{{l1:.1f}\\%}} & \\textbf{{{l2:.1f}\\%}} & "
                f"\\textbf{{{l3:.1f}\\%}} & \\textbf{{{l4:.1f}\\%}} & "
                f"\\textbf{{{po['liquidation_rate_pct']:.1f}\\%}} & "
                f"\\textbf{{{po['mean_min_equity_usdt']:,.2f}}} & "
                f"\\textbf{{{depth_avail}}} \\\\"
            )
        else:
            lines.append(
                f"{alabel} & {l1:.1f}\\% & {l2:.1f}\\% & {l3:.1f}\\% & {l4:.1f}\\% & "
                f"{po['liquidation_rate_pct']:.1f}\\% & {po['mean_min_equity_usdt']:,.2f} & "
                f"{depth_avail} \\\\"
            )

    lines.extend([
        r"\midrule",
        r"\multicolumn{8}{l}{\textbf{Panel C: Direct Physical Signed Historical Price \& Order-Flow Replay (Unamplified Counterfactual Dealer Account)}} \\",
        r"\midrule",
        r"Market Safety Architecture & May 2021 Liq.\ & May 2022 Liq.\ & Nov 2022 Liq.\ & Mar 2023 Liq.\ & All-100 Liq.\ & Mean $\min_t E_t$ & Depth $\bar{\alpha}_t$ / Adm.\ Elig. \\",
        r"\midrule",
    ])
    for akey, alabel in arch_labels:
        l1 = evs[e_keys[0]]["physical_signed_replay_architectures"][akey]["liquidation_rate_pct"]
        l2 = evs[e_keys[1]]["physical_signed_replay_architectures"][akey]["liquidation_rate_pct"]
        l3 = evs[e_keys[2]]["physical_signed_replay_architectures"][akey]["liquidation_rate_pct"]
        l4 = evs[e_keys[3]]["physical_signed_replay_architectures"][akey]["liquidation_rate_pct"]
        po = ov_phys[akey]
        depth_avail = f"{po['admitted_depth_share_pct']:.1f}\\% / {po['model_admission_eligibility_pct']:.1f}\\%"
        lines.append(
            f"{alabel} & {l1:.1f}\\% & {l2:.1f}\\% & {l3:.1f}\\% & {l4:.1f}\\% & "
            f"{po['liquidation_rate_pct']:.1f}\\% & {po['mean_min_equity_usdt']:,.2f} & {depth_avail} \\\\"
        )

    lines.extend([
        r"\midrule",
        f"\\multicolumn{{8}}{{l}}{{\\textbf{{Panel D: Empirically Estimated 1-Second Signed Crash-Burst OLS Operator Replay ($\\hat{{J}}_{{\\mathrm{{burst,pool}}}}^{{\\mathrm{{OLS}}}}$, $\\rho={pb['spectral_radius']:.3f}$, $\\mathcal{{M}}_{{\\mathcal{{C}}_{{\\mathrm{{price}}}}}}={pb['price_output_gain_MC']:.2f}$)}}}} \\\\",
        r"\midrule",
        r"Market Safety Architecture & May 2021 Liq.\ & May 2022 Liq.\ & Nov 2022 Liq.\ & Mar 2023 Liq.\ & All-100 Liq.\ & Mean $\min_t E_t$ & Depth $\bar{\alpha}_t$ / Adm.\ Elig. \\",
        r"\midrule",
    ])
    for akey, alabel in arch_labels:
        l1 = evs[e_keys[0]]["empirical_burst_ols_replay_architectures"][akey]["liquidation_rate_pct"]
        l2 = evs[e_keys[1]]["empirical_burst_ols_replay_architectures"][akey]["liquidation_rate_pct"]
        l3 = evs[e_keys[2]]["empirical_burst_ols_replay_architectures"][akey]["liquidation_rate_pct"]
        l4 = evs[e_keys[3]]["empirical_burst_ols_replay_architectures"][akey]["liquidation_rate_pct"]
        po = ov_burst[akey]
        depth_avail = f"{po['admitted_depth_share_pct']:.1f}\\% / {po['model_admission_eligibility_pct']:.1f}\\%"
        if akey == "Resolvent_Guard_Kreiss":
            lines.append(
                f"{alabel} & \\textbf{{{l1:.1f}\\%}} & \\textbf{{{l2:.1f}\\%}} & "
                f"\\textbf{{{l3:.1f}\\%}} & \\textbf{{{l4:.1f}\\%}} & "
                f"\\textbf{{{po['liquidation_rate_pct']:.1f}\\%}} & "
                f"\\textbf{{{po['mean_min_equity_usdt']:,.2f}}} & "
                f"\\textbf{{{depth_avail}}} \\\\"
            )
        else:
            lines.append(
                f"{alabel} & {l1:.1f}\\% & {l2:.1f}\\% & {l3:.1f}\\% & {l4:.1f}\\% & "
                f"{po['liquidation_rate_pct']:.1f}\\% & {po['mean_min_equity_usdt']:,.2f} & "
                f"{depth_avail} \\\\"
            )

    lines.extend([
        r"\bottomrule",
        r"\end{tabular}%",
        r"}",
        r"\end{table}",
        "",
    ])
    OUT_TEX.write_text("\n".join(lines))


if __name__ == "__main__":
    res = run_experiment()
    print("EXP19 COMPLETE:")
    for k, v in res["overall_100_episode_summary"].items():
        print(
            f"  [Stress]    {k:24s}: liq={v['liquidation_rate_pct']:5.1f}%, min_eq={v['mean_min_equity_usdt']:8.2f}, "
            f"depth={v['admitted_depth_share_pct']:5.1f}%, avail={v['two_sided_quote_availability_pct']:5.1f}%"
        )
    for k, v in res["overall_100_episode_empirical_burst_ols_summary"].items():
        print(
            f"  [BurstOLS]  {k:24s}: liq={v['liquidation_rate_pct']:5.1f}%, min_eq={v['mean_min_equity_usdt']:8.2f}, "
            f"depth={v['admitted_depth_share_pct']:5.1f}%, avail={v['two_sided_quote_availability_pct']:5.1f}%"
        )
    for k, v in res["overall_100_episode_physical_signed_summary"].items():
        print(
            f"  [Signed]    {k:24s}: liq={v['liquidation_rate_pct']:5.1f}%, min_eq={v['mean_min_equity_usdt']:8.2f}, "
            f"depth={v['admitted_depth_share_pct']:5.1f}%, avail={v['two_sided_quote_availability_pct']:5.1f}%"
        )


