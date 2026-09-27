#!/usr/bin/env python3
"""Offline Gate 2--4 proxy analysis and synthetic accounting diagnostics.

Prices are USDT per base unit, flows are base units, and the fitted impact
slope is price change per signed base unit (USDT/base^2). This contemporaneous
association is not a causal execution-impact estimate. Live REST depth is a
separate, noncontemporaneous scale anchor, not historical bookDepth or dealer
capacity. All gates remain pending execution/structural calibration.

New evidence is written exclusively to --output-dir; existing evidence is never
overwritten. This program never downloads data.
"""
from __future__ import annotations

import argparse
import json
import math
from pathlib import Path
import platform
import subprocess
import zipfile
from typing import Any

import numpy as np
from scipy.stats import beta as beta_distribution

if __package__:
    from .download_public_data import audit_cached_file, sha256_bytes
else:
    from download_public_data import audit_cached_file, sha256_bytes

ROOT = Path(__file__).resolve().parents[2]
RAW_KLINES = ROOT / "research_extension/data/raw/binance/spot/klines"
RAW_DEPTH = ROOT / "research_extension/data/raw/binance/spot/depth_snapshots"
OUT = ROOT / "research_extension/outputs/evidence_repair_20260926/gate24"
SYMBOLS = {"BTC": "BTCUSDT", "ETH": "ETHUSDT", "SOL": "SOLUSDT"}
MONTHS = ["2025-01", "2025-02", "2025-03"]


def load_klines(symbol_code: str, months: list[str], raw_dir: Path | None = None) -> np.ndarray:
    """OHLC, base volume, trade count, taker-buy base volume, open timestamp ms.

    Require every requested archive and order by timestamp, not caller month order.
    The first seven columns retain the legacy layout.
    """
    rows = []
    for month in months:
        path = (raw_dir or RAW_KLINES) / f"{symbol_code}-1m-{month}.zip"
        with zipfile.ZipFile(path) as archive:
            names = [name for name in archive.namelist() if name.endswith(".csv")]
            if len(names) != 1:
                raise ValueError(f"Expected one CSV in {path}")
            lines = archive.read(names[0]).decode().strip().splitlines()
        for line in lines:
            parts = line.split(",")
            if parts[0].lower() in {"open_time", "open time"}:
                continue
            if len(parts) < 11:
                raise ValueError(f"Malformed kline in {path}")
            timestamp = int(parts[0])
            if timestamp >= 100_000_000_000_000:
                timestamp //= 1000  # cached 2025 archives use microseconds
            rows.append([*(float(parts[i]) for i in [1, 2, 3, 4, 5]),
                         int(parts[8]), float(parts[9]), timestamp])
    if not rows:
        raise ValueError("No klines")
    data = np.asarray(rows, dtype=float)
    data = data[np.argsort(data[:, 7], kind="stable")]
    if np.any(np.diff(data[:, 7]) <= 0):
        raise ValueError("Duplicate or unordered timestamps")
    return data


def depth_path(symbol_code: str, raw_dir: Path | None = None) -> Path | None:
    for limit in [1000, 100]:
        path = (raw_dir or RAW_DEPTH) / f"{symbol_code}-depth-{limit}.json"
        if path.exists():
            return path
    return None


def load_depth(symbol_code: str, raw_dir: Path | None = None) -> dict[str, Any]:
    path = depth_path(symbol_code, raw_dir)
    return json.loads(path.read_text()) if path else {}


def fit_slope(flow: np.ndarray, changes: np.ndarray) -> tuple[float | None, float | None]:
    """OLS with intercept; preserve sign and abstain on zero regressor variance."""
    centered = flow - np.mean(flow)
    denominator = float(centered @ centered)
    if denominator == 0:
        return None, None
    slope = float(centered @ (changes - np.mean(changes)) / denominator)
    return slope, float(np.mean(changes) - slope * np.mean(flow))


def spectrum(matrix: np.ndarray) -> tuple[list, float]:
    values = np.linalg.eigvals(matrix)
    reported = [float(v.real) if v.imag == 0 else {"real": float(v.real), "imag": float(v.imag)}
                for v in values]
    return reported, float(np.max(np.abs(values)))


def analyze_gate2(symbol_name: str, symbol_code: str, klines: np.ndarray,
                  depth: dict, train_fraction: float = .7) -> dict:
    data = np.asarray(klines, dtype=float)
    if data.ndim != 2 or data.shape[1] < 7 or len(data) < 6:
        raise ValueError("At least six valid kline rows are required")
    if not np.all(np.isfinite(data)) or np.any(data[:, :4] <= 0):
        raise ValueError("Prices must be positive and all inputs finite")
    if np.any(data[:, 4:7] < 0) or np.any(data[:, 6] > data[:, 4]):
        raise ValueError("Invalid volume, trade count or taker-buy volume")
    if not 0 < train_fraction < 1:
        raise ValueError("train_fraction must be inside (0, 1)")
    if data.shape[1] >= 8:
        data = data[np.argsort(data[:, 7], kind="stable")]
        if np.any(np.diff(data[:, 7]) <= 0):
            raise ValueError("Duplicate timestamps")
    closes = data[:, 3]
    changes = np.diff(closes)
    flow = 2 * data[1:, 6] - data[1:, 4]
    split = int(len(changes) * train_fraction)
    if min(split, len(changes) - split) < 2:
        raise ValueError("Each chronological partition needs at least two observations")
    slope, intercept = fit_slope(flow[:split], changes[:split])
    holdout_slope, _ = fit_slope(flow[split:], changes[split:])
    train = data[1:split + 1]
    returns = np.diff(np.log(closes[:split + 1]))
    a_hat, _ = fit_slope(returns[:-1], returns[1:])
    holdout = {"n": len(changes) - split,
               "diagnostic_slope_quote_per_base_squared": holdout_slope,
               "rmse_quote_per_base": None, "r_squared": None,
               "zero_change_rmse_quote_per_base": float(np.sqrt(np.mean(changes[split:] ** 2)))}
    if slope is not None:
        errors = changes[split:] - (intercept + slope * flow[split:])
        denominator = float(np.sum((changes[split:] - np.mean(changes[split:])) ** 2))
        holdout.update(rmse_quote_per_base=float(np.sqrt(np.mean(errors ** 2))),
                       r_squared=float(1 - np.sum(errors ** 2) / denominator) if denominator else None)

    lob: dict[str, Any] = {"source_kind": "missing", "historical_book_depth": False,
                           "dealer_capacity_identified": False, "capture_timestamp": None}
    mid = float(np.median(train[:, 3]))
    spread_bps = None
    if depth.get("bids") and depth.get("asks"):
        bids, asks = np.asarray(depth["bids"], float), np.asarray(depth["asks"], float)
        if (not np.all(np.isfinite(bids)) or not np.all(np.isfinite(asks))
                or np.any(bids <= 0) or np.any(asks <= 0) or asks[0, 0] < bids[0, 0]):
            raise ValueError("Invalid cached depth snapshot")
        mid = float((bids[0, 0] + asks[0, 0]) / 2)
        spread_bps = float((asks[0, 0] - bids[0, 0]) / mid * 10000)
        lob.update(source_kind="live_rest_snapshot", best_bid=float(bids[0, 0]),
                   best_ask=float(asks[0, 0]), mid_price=mid, spread_bps=spread_bps,
                   top5_bid_depth_units=float(np.sum(bids[:5, 1])),
                   top5_ask_depth_units=float(np.sum(asks[:5, 1])),
                   top20_bid_depth_units=float(np.sum(bids[:20, 1])),
                   top20_ask_depth_units=float(np.sum(asks[:20, 1])),
                   available_bid_levels=len(bids), available_ask_levels=len(asks),
                   alignment="Not contemporaneous with historical kline train/holdout")
    times = data[1:, 7] if data.shape[1] >= 8 else None
    partitions = {"train_fraction": train_fraction, "train_observations": split,
                  "holdout_observations": len(changes) - split,
                  "train_start_timestamp_ms": int(times[0]) if times is not None else None,
                  "train_end_timestamp_ms": int(times[split - 1]) if times is not None else None,
                  "holdout_start_timestamp_ms": int(times[split]) if times is not None else None,
                  "holdout_end_timestamp_ms": int(times[-1]) if times is not None else None,
                  "timestamp_verified": times is not None}
    return {
        "symbol": symbol_name, "symbol_code": symbol_code, "n_bars": len(data),
        "status": "PENDING_CALIBRATION", "execution_calibration_validated": False,
        "empirical_channels": {"a_hat": a_hat, "kappa_hat": slope,
                               "kappa_units": "USDT/base^2",
                               "trades_per_min": float(np.median(train[:, 5])),
                               "mid_price": mid, "spread_bps": spread_bps},
        "impact_proxy": {
            "estimator": "OLS with intercept: close_t - close_(t-1) on 2*taker_buy_base_t - volume_base_t",
            "units": "USDT/base^2; price change per signed base unit",
            "slope": slope, "intercept_quote_per_base": intercept,
            "sign": "unidentified" if slope is None else "positive" if slope > 0 else "nonpositive",
            "chronological_split": partitions, "holdout": holdout,
            "causal_execution_impact_identified": False,
            "limitations": ["Contemporaneous observational association, endogenous flow",
                            "One-minute aggregation; no queue, latency, fill or impact-decay validation",
                            "Holdout diagnostics do not establish causal or execution calibration"]},
        "lob_depth_authentication": lob,
        "epistemic_boundary": "Public proxy inputs do not authenticate dealer rules, risk limits, "
                              "internal learning rates, randomized probes or execution.",
    }


def analyze_gate3(symbol_name: str, klines: np.ndarray, g2: dict,
                  fee_bps: float | None = None) -> dict:
    """Conditional round-trip cost scenarios; unknown fees stay unknown.

    Each episode assumes one entry and equal-size unwind at the same reference
    mid. Marginal linear impact k*v is integrated to 0.5*k*v^2 per leg.
    This curve is a scenario assumption, not an execution estimate.
    """
    if fee_bps is not None and (not math.isfinite(fee_bps) or fee_bps < 0):
        raise ValueError("fee_bps must be a finite nonnegative declared assumption")
    channels = g2["empirical_channels"]
    mid, spread, slope = (channels["mid_price"], channels["spread_bps"], channels["kappa_hat"])
    costs = {}
    for size in [1000., 10000.]:
        units = size / mid
        half_spread = None if spread is None else .5 * spread / 10000 * size
        impact = None if slope is None or slope <= 0 else .5 * slope * units ** 2
        fee = None if fee_bps is None else fee_bps / 10000 * size
        friction = None if half_spread is None or impact is None else half_spread + impact
        leg = None if friction is None or fee is None else friction + fee
        costs[f"${int(size):,}"] = {
            "probe_notional_quote": size, "probe_units": units,
            "entry_half_spread_quote": half_spread, "entry_impact_proxy_quote": impact,
            "entry_fee_quote": fee, "unwind_half_spread_quote": half_spread,
            "unwind_impact_proxy_quote": impact, "unwind_fee_quote": fee,
            "entry_cost_proxy_quote": leg, "unwind_cost_proxy_quote": leg,
            "round_trip_friction_excluding_fees_quote": None if friction is None else 2 * friction,
            "round_trip_cost_proxy_quote": None if leg is None else 2 * leg,
            "experiment_1000_round_trips_cost_proxy_quote": None if leg is None else 2000 * leg,
            "fee_sensitivity_1000_round_trips_quote": {
                f"{rate:g}_bps_per_leg": None if friction is None else
                2000 * (friction + rate / 10000 * size) for rate in [0., 1., 10.]},
        }
    arrival_rate = channels["trades_per_min"]
    hours = 50000 / arrival_rate / 60 if arrival_rate > 0 else None
    pending = ["adverse_selection", "queue_and_fill_dynamics", "impact_decay",
               "opportunity_cost", "information_leakage", "independent_randomized_episode_design"]
    if fee_bps is None:
        pending.insert(0, "fees")
    if spread is None:
        pending.append("spread")
    if slope is None or slope <= 0:
        pending.append("positive_execution_impact_proxy")
    return {
        "symbol": symbol_name, "status": "PENDING_CALIBRATION", "quote_currency": "USDT",
        "usd_equivalence_assumed": False, "fee_bps_per_leg_assumption": fee_bps,
        "fee_schedule_verified": False, "probe_cost_protocol": costs,
        "pending_cost_components": pending,
        "timing_protocol": {"trades_per_episode": 50, "hypothetical_episodes": 1000,
                            "total_trade_arrivals": 50000,
                            "arrival_rate_trades_per_minute": arrival_rate,
                            "total_arrival_hours": hours,
                            "minutes_per_50_arrivals": None if hours is None else hours * 60 / 1000,
                            "independent_randomized_episodes_established": False,
                            "complete_protocol_duration_hours": None},
        "verdict": "Conditional proxy costs only. Entry plus unwind, same reference notional and "
                   "symmetric linear impact assumed. Passive arrival time is not protocol duration.",
    }


class IndependentCalibratedMarket:
    """Synthetic dealer with explicit adaptive, fundamentalist, exogenous and fee ledgers.

    x_next = (a - kappa*phi)*x + q*y + kappa*shock while unconstrained.
    y_next = (1-eta)*y + eta*x_next. Flows are base units; prices USDT/base.
    Each party pays/receives its own signed fill at the post-impact mid, pays
    half-spread to the dealer, and pays declared fees to the fee recipient.
    Counterpart credit is unconstrained: this is an accounting model, not a
    validated multi-party solvency/queue model.

    Capacity clipping permits a full inventory reversal. The clipping step may
    fill to the boundary; no transactions occur afterwards. Default also halts
    trading. Price and inventory marks continue to the common terminal horizon.
    """

    def __init__(self, p_star: float, a: float, q: float, eta: float, kappa: float,
                 phi: float, spread_bps: float, max_inventory_units: float,
                 initial_cash: float = 100000., fee_bps: float = 0.):
        values = [p_star, a, q, eta, kappa, phi, spread_bps, max_inventory_units, initial_cash, fee_bps]
        if not all(math.isfinite(v) for v in values):
            raise ValueError("Model parameters must be finite")
        if (p_star <= 0 or kappa <= 0 or max_inventory_units <= 0 or initial_cash <= 0
                or spread_bps < 0 or fee_bps < 0 or not 0 < eta <= 1):
            raise ValueError("Invalid price, impact, capacity, capital, spread, fee or memory")
        self.p_star, self.a, self.q, self.eta = map(float, [p_star, a, q, eta])
        self.kappa, self.phi = float(kappa), float(phi)
        self.half_spread = spread_bps / 10000 * p_star / 2
        self.max_inventory, self.initial_cash = float(max_inventory_units), float(initial_cash)
        self.fee_rate = fee_bps / 10000
        self.S = abs(a) + abs(q)  # retained as a legacy parameter summary, not a certificate

    def jacobian(self) -> np.ndarray:
        alpha = self.a - self.kappa * self.phi
        return np.array([[alpha, self.q],
                         [self.eta * alpha, 1 - self.eta + self.eta * self.q]])

    def run(self, shock_tape: np.ndarray, mean_repricing_shock: float = 0.,
            shock_step: int = 16, unlimited_funding: bool = False,
            initial_x: float = 0., initial_y: float = 0.) -> dict[str, Any]:
        tape = np.asarray(shock_tape, dtype=float)
        if tape.ndim != 1 or not len(tape) or not np.all(np.isfinite(tape)):
            raise ValueError("A finite nonempty one-dimensional shock tape is required")
        if not all(math.isfinite(v) for v in [mean_repricing_shock, initial_x, initial_y]):
            raise ValueError("Initial state and repricing shock must be finite")
        x, y = float(initial_x), float(initial_y)
        previous_price = self.p_star + x
        if previous_price <= 0:
            raise ValueError("Initial price must be positive")
        names = ["dealer", "adaptive", "fundamentalist", "exogenous", "fee_recipient"]
        ledgers = {name: {"cash": 0., "inventory": 0.} for name in names}
        ledgers["dealer"]["cash"] = self.initial_cash
        halted = defaulted = False
        halt_step = default_step = None
        halt_reason = None
        history = []
        max_cash = max_inventory = max_equity = max_accounting = max_normalized = 0.
        for t, noise in enumerate(tape):
            old = {name: ledger.copy() for name, ledger in ledgers.items()}
            old_equity = {name: ledger["cash"] + ledger["inventory"] * previous_price
                          for name, ledger in old.items()}
            if t == shock_step:
                x += mean_repricing_shock
            pre_price = self.p_star + x
            if pre_price <= 0:
                raise ValueError("Shock left the positive-price model domain")
            pre_equity = ledgers["dealer"]["cash"] + ledgers["dealer"]["inventory"] * pre_price
            if pre_equity <= 0 and not defaulted:
                defaulted, default_step = True, t
                if not halted:
                    halted, halt_step, halt_reason = True, t, "default"
            requests = {"adaptive": self.q / self.kappa * y,
                        "fundamentalist": -self.phi * x, "exogenous": float(noise)}
            desired = math.fsum(requests.values())
            actual = 0. if halted else desired
            if not halted and not unlimited_funding:
                inventory = ledgers["dealer"]["inventory"]
                actual = float(np.clip(desired, inventory - self.max_inventory,
                                       inventory + self.max_inventory))
                if actual != desired:
                    halted, halt_step, halt_reason = True, t, "capacity"
            # A capacity event fills now; an earlier halt/default never fills.
            can_fill = not halted or (halt_step == t and halt_reason == "capacity")
            ratio = (actual / desired if desired else 1.) if can_fill else 0.
            fills = {name: flow * ratio for name, flow in requests.items()}
            actual = math.fsum(fills.values())
            x_next = self.a * x + self.kappa * actual
            price = self.p_star + x_next
            if not math.isfinite(price) or price <= 0:
                raise ValueError("Dynamics left the positive-price model domain")
            spread_income = fees = 0.
            transfers = {name: 0. for name in names}
            for name, fill in fills.items():
                spread = abs(fill) * self.half_spread
                fee = abs(fill) * price * self.fee_rate
                settlement = fill * price + spread
                ledgers[name]["inventory"] += fill
                ledgers[name]["cash"] -= settlement + fee
                ledgers["dealer"]["inventory"] -= fill
                ledgers["dealer"]["cash"] += settlement
                ledgers["fee_recipient"]["cash"] += fee
                transfers[name] -= spread + fee
                transfers["dealer"] += spread
                transfers["fee_recipient"] += fee
                spread_income += spread
                fees += fee
            equities = {name: ledger["cash"] + ledger["inventory"] * price
                        for name, ledger in ledgers.items()}
            cash_res = abs(math.fsum(p["cash"] for p in ledgers.values()) - self.initial_cash)
            inventory_res = abs(math.fsum(p["inventory"] for p in ledgers.values()))
            equity_res = abs(math.fsum(equities.values()) - self.initial_cash)
            accounting_res = max(abs(equities[name] - old_equity[name]
                                     - old[name]["inventory"] * (price - previous_price)
                                     - transfers[name]) for name in names)
            cash_scale = max(1., math.fsum(abs(p["cash"]) for p in ledgers.values()),
                             math.fsum(abs(value) for value in equities.values()))
            inv_scale = max(1., math.fsum(abs(p["inventory"]) for p in ledgers.values()))
            normalized = max(cash_res / cash_scale, equity_res / cash_scale,
                             accounting_res / cash_scale, inventory_res / inv_scale)
            # Scaled tolerance is explicit; inventory and cash have different units.
            if (max(cash_res, equity_res, accounting_res) > 1e-10 + 1e-12 * cash_scale
                    or inventory_res > 1e-12 + 1e-12 * inv_scale):
                raise ArithmeticError("All-party accounting conservation failed")
            max_cash, max_inventory = max(max_cash, cash_res), max(max_inventory, inventory_res)
            max_equity, max_accounting = max(max_equity, equity_res), max(max_accounting, accounting_res)
            max_normalized = max(max_normalized, normalized)
            if equities["dealer"] <= 0 and not defaulted:
                defaulted, default_step = True, t
                if not halted:
                    halted, halt_step, halt_reason = True, t, "default"
            y = (1 - self.eta) * y + self.eta * x_next
            x = x_next
            history.append({
                "step": t, "x": x, "y": y, "price": price,
                "pre_trade_price": pre_price, "desired_flow": desired, "actual_flow": actual,
                "fills": fills, "ledgers": {name: p.copy() for name, p in ledgers.items()},
                "dealer_equity": equities["dealer"], "dealer_pre_trade_equity": pre_equity,
                "dealer_revaluation": old["dealer"]["inventory"] * (price - previous_price),
                "spread_income": spread_income, "fees": fees,
                "halted": halted, "defaulted": defaulted,
                "cash_conservation_residual": cash_res,
                "inventory_conservation_residual": inventory_res,
                "equity_conservation_residual": equity_res,
                "accounting_residual": accounting_res,
            })
            previous_price = price
        eigenvalues, radius = spectrum(self.jacobian())
        return {
            "halted": halted, "halt_step": halt_step, "halt_reason": halt_reason,
            "defaulted": defaulted, "default_step": default_step,
            "horizon_steps": len(tape), "final_equity": history[-1]["dealer_equity"],
            "min_equity": min(min(row["dealer_equity"], row["dealer_pre_trade_equity"]) for row in history),
            "max_dislocation": max(max(abs(row["x"]), abs(row["pre_trade_price"] - self.p_star))
                                   for row in history),
            "max_conservation_residual": max(max_cash, max_equity, max_accounting),
            "max_cash_conservation_residual": max_cash,
            "max_inventory_conservation_residual": max_inventory,
            "max_equity_conservation_residual": max_equity,
            "max_accounting_residual": max_accounting,
            "max_normalized_conservation_residual": max_normalized,
            "conservation_verified": True, "S": self.S, "S_stable": radius < 1,
            "S_interpretation": "Legacy |a|+|q| summary; S_stable uses actual Jacobian spectral radius",
            "jacobian": self.jacobian().tolist(), "eigenvalues": eigenvalues, "spectral_radius": radius,
            "local_signal_stable": radius < 1, "final_ledgers": ledgers, "trajectory": history,
        }


def analyze_gate4(symbol_name: str, g2: dict) -> dict:
    channels, lob = g2["empirical_channels"], g2["lob_depth_authentication"]
    slope, spread = channels["kappa_hat"], channels["spread_bps"]
    anchor = lob.get("top5_bid_depth_units")
    if slope is None or slope <= 0 or spread is None or anchor is None:
        return {"symbol": symbol_name, "status": "PENDING_CALIBRATION", "scenarios": {},
                "execution_calibration_validated": False,
                "reason": "Positive signed slope, observed spread and displayed depth required; no abs/floor substitutes"}
    mid = channels["mid_price"]
    calibration = {"p_star": mid, "kappa": slope, "kappa_units": "USDT/base^2",
                   "a": .4, "q": .42, "eta": .05, "phi": .5, "phi_units": "base^2/USDT",
                   "S_legacy_summary": .82, "spread_bps": spread,
                   "max_inventory_units": anchor, "fee_bps_assumption": 0.,
                   "depth_mapping": "Synthetic symmetric capacity = multiplier * snapshot top5 BID depth",
                   "funding_mapping": "Synthetic initial cash = 2 * p_star * capacity",
                   "parameter_status": "a, q, eta, phi, capital, fees and capacity mapping are maintained assumptions"}
    grids = {}
    trials = []
    for multiplier in [.5, 1., 2.]:
        capacity = anchor * multiplier
        sim = IndependentCalibratedMarket(mid, .4, .42, .05, slope, .5, spread,
                                          capacity, initial_cash=mid * capacity * 2)
        scenarios = {}
        for fraction in [0., -.01, -.03, -.05]:
            runs = []
            for rep in range(50):
                seed = rep * 1007 + 42
                tape = np.random.default_rng(seed).normal(0, capacity * .05, size=64)
                result = sim.run(tape, mean_repricing_shock=fraction * mid, shock_step=16)
                result.pop("trajectory")
                trials.append({"capacity_multiplier": multiplier, "shock_fraction": fraction,
                               "rep": rep, "seed": seed, **result})
                runs.append(result)
            halt_count = sum(r["halted"] for r in runs)
            default_count = sum(r["defaulted"] for r in runs)
            low = 0. if halt_count == 0 else float(beta_distribution.ppf(.025, halt_count, 51 - halt_count))
            high = 1. if halt_count == 50 else float(beta_distribution.ppf(.975, halt_count + 1, 50 - halt_count))
            scenarios[f"shock_{abs(fraction)*100:.1f}%"] = {
                "shock_fraction": fraction, "shock_quote_per_base": fraction * mid,
                "n_reps": 50, "halts": halt_count, "halt_rate": halt_count / 50,
                "halt_rate_exact_95pct_ci": [low, high],
                "defaults": default_count, "default_rate": default_count / 50,
                "mean_peak_dislocation_quote_per_base": float(np.mean([r["max_dislocation"] for r in runs])),
                "mean_final_equity_quote": float(np.mean([r["final_equity"] for r in runs])),
                "mean_min_equity_quote": float(np.mean([r["min_equity"] for r in runs])),
                "mean_halt_step_among_halted": float(np.mean([r["halt_step"] for r in runs if r["halted"]])) if halt_count else None,
                "max_cash_residual_quote": max(r["max_cash_conservation_residual"] for r in runs),
                "max_inventory_residual_base": max(r["max_inventory_conservation_residual"] for r in runs),
                "max_equity_residual_quote": max(r["max_equity_conservation_residual"] for r in runs),
                "max_accounting_residual_quote": max(r["max_accounting_residual"] for r in runs),
                "max_normalized_conservation_residual": max(r["max_normalized_conservation_residual"] for r in runs),
            }
        rates = [r["halt_rate"] for r in scenarios.values()]
        grids[f"{multiplier:g}x"] = {
            "capacity_units": capacity, "initial_cash_quote": mid * capacity * 2,
            "noise_std_base": capacity * .05,
            "scenarios": scenarios, "observed_halt_rate_nondecreasing": all(a <= b for a, b in zip(rates, rates[1:])),
        }
    eigenvalues, radius = spectrum(sim.jacobian())
    return {
        "symbol": symbol_name, "status": "PENDING_CALIBRATION",
        "implementation_status": "ACCOUNTING_CHECKS_PASSED",
        "execution_calibration_validated": False, "calibration": calibration,
        "jacobian": sim.jacobian().tolist(), "eigenvalues": eigenvalues,
        "spectral_radius": radius, "local_signal_stable": radius < 1,
        "scenarios": grids["1x"]["scenarios"],
        "joint_scale_diagnostic": {
            "diagnostic_kind": "JOINT_SCALE_DIAGNOSTIC",
            "co_varying_dimensions": ["capacity_units", "initial_cash_quote", "noise_std_base"],
            "causal_capacity_effect_identified": False,
            "intervention_welfare_evaluated": False,
            "interpretation": "Capacity, funding and noise scale together; not an isolated capacity effect",
            "scales": grids,
        },
        "conservation_verified": all(r["conservation_verified"] for r in trials),
        "max_conservation_residual": max(r["max_conservation_residual"] for r in trials),
        "max_normalized_conservation_residual": max(r["max_normalized_conservation_residual"] for r in trials),
        "accounting_tolerances": {"cash_equity_atol_quote": 1e-10, "inventory_atol_base": 1e-12, "rtol": 1e-12},
        "observed_halt_rate_nondecreasing": grids["1x"]["observed_halt_rate_nondecreasing"],
        "solvency_monotonicity_established": False,
        "experiment": {"steps_per_run": 64, "shock_step": 16, "replications_per_cell": 50,
                       "capacity_multipliers": [.5, 1., 2.], "runs": len(trials),
                       "counterpart_credit": "unconstrained", "fee_schedule": "zero, synthetic assumption",
                       "halt_rule": "Capacity clips event fill then absorbs; default stops trading; marks continue",
                       "fundamentalist_orientation": "Negative x produces positive demand (-phi*x), dealer sells",
                       "price_marks": "Common 64-step horizon; no terminal forced unwind",
                       "peak_dislocation": "Includes immediate external repricing and end-step marks"},
        "verdict": "Synthetic diagnostics only; monotone observed halt frequencies are not a solvency theorem "
                   "or external calibration. The scale grid jointly varies capacity, cash and noise; "
                   "no causal capacity effect or intervention welfare is identified. "
                   "No independence or clean-room authorship claim is established.",
        "replications": trials,
    }


def main(argv: list[str] | None = None) -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--offline", action="store_true", help="Explicit offline declaration; analysis is always offline")
    parser.add_argument("--data-dir", type=Path, default=RAW_KLINES.parent)
    parser.add_argument("--output-dir", type=Path, default=OUT)
    parser.add_argument("--symbols", nargs="+", choices=list(SYMBOLS), default=list(SYMBOLS))
    parser.add_argument("--months", nargs="+", default=MONTHS)
    parser.add_argument("--fee-bps", type=float, default=None, help="Assumed per-leg taker fee, not a verified schedule")
    args = parser.parse_args(argv)
    dest = args.output_dir / "gate24_analysis_results.json"
    if dest.exists() or args.output_dir.resolve() == (ROOT / "research_extension/gate24_public_data").resolve():
        parser.error("Refusing to overwrite existing or legacy evidence; use a new output directory")
    provenance = []
    results = {"gate2_authenticated_boundary": {}, "gate3_costed_observations": {},
               "gate4_calibrated_implementation": {}}
    for name in args.symbols:
        code = SYMBOLS[name]
        for month in args.months:
            path = args.data_dir / "klines" / f"{code}-1m-{month}.zip"
            record = audit_cached_file(path, f"https://data.binance.vision/data/spot/monthly/klines/{code}/1m/{path.name}")
            if record["official_checksum_status"] == "mismatch_or_invalid_sidecar":
                raise ValueError(f"Cached checksum mismatch: {path}")
            provenance.append(record)
        path = depth_path(code, args.data_dir / "depth_snapshots")
        if path:
            limit = path.stem.rsplit("-", 1)[1]
            provenance.append(audit_cached_file(path, f"https://data-api.binance.vision/api/v3/depth?symbol={code}&limit={limit}"))
        klines = load_klines(code, args.months, args.data_dir / "klines")
        g2 = analyze_gate2(name, code, klines, load_depth(code, args.data_dir / "depth_snapshots"))
        g3 = analyze_gate3(name, klines, g2, fee_bps=args.fee_bps)
        g4 = analyze_gate4(name, g2)
        results["gate2_authenticated_boundary"][name] = g2
        results["gate3_costed_observations"][name] = g3
        results["gate4_calibrated_implementation"][name] = g4
        print(f"{name}: impact slope={g2['empirical_channels']['kappa_hat']} USDT/base^2; "
              f"holdout R2={g2['impact_proxy']['holdout']['r_squared']}; "
              f"Gate4={g4.get('implementation_status', 'NOT_RUN')}; calibration PENDING", flush=True)
    source_paths = [Path(__file__), Path(__file__).with_name("download_public_data.py"),
                    ROOT / "tests/test_gate24_repairs.py"]
    legacy_paths = [Path(__file__).with_name("gate24_analysis_results.json"),
                    Path(__file__).with_name("data_acquisition_manifest.json")]
    revision = subprocess.run(["git", "rev-parse", "HEAD"], cwd=ROOT, capture_output=True, text=True, check=True)
    results["meta"] = {
        "schema": "machine-markets-gate24-evidence-repair-20260926-v1",
        "status": "PENDING_CALIBRATION", "network_used": False,
        "data_source": "Cached Binance historical klines plus separate live REST depth snapshots",
        "symbols": args.symbols, "months": args.months, "quote_currency": "USDT",
        "total_consumed_input_bytes": sum(r["bytes"] for r in provenance),
        "checksum_verified": all(r["checksum_verified"] for r in provenance),
        "official_checksum_verified_files": sum(r["checksum_verified"] for r in provenance),
        "consumed_input_files": len(provenance), "provenance": provenance,
        "checksum_caveat": "Only matching cached provider sidecars count; local hashes and legacy verified flags do not.",
        "unused_data": "aggTrades, raw trades and DOGE/ADA are not consumed",
        "git_head": revision.stdout.strip(), "python": platform.python_version(), "numpy": np.__version__,
        "source_sha256": {str(p.relative_to(ROOT)): sha256_bytes(p.read_bytes()) for p in source_paths},
        "legacy_evidence_sha256": {str(p.relative_to(ROOT)): sha256_bytes(p.read_bytes()) for p in legacy_paths},
    }
    args.output_dir.mkdir(parents=True, exist_ok=True)
    with dest.open("x") as handle:
        json.dump(results, handle, indent=2, allow_nan=False)
        handle.write("\n")
    print(f"Saved new evidence: {dest}")


if __name__ == "__main__":
    main()
