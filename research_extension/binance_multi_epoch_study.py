"""Chronological, cache-only multi-seed fits to the frozen Binance US tick data.

Validation is conditional response replay using observed flow, not a forecast
of future flow. Cross-asset regressions fitted to candle outcomes are explanatory.
"""
import json
from pathlib import Path

import numpy as np
from scipy.optimize import minimize


ROOT = Path(__file__).resolve().parents[1]
BINANCE_ASSETS = [
    "BTCUSDT", "ETHUSDT", "SOLUSDT", "DOGEUSDT", "NEARUSDT",
    "ADAUSDT", "AVAXUSDT", "LTCUSDT", "LINKUSDT", "DOTUSDT",
]
SEEDS = [42, 101, 777, 1234, 2026]
N_EPOCHS = 10
BOUNDS = [(0.01, 0.95), (0.005, 0.90), (0.01, 0.95), (1e-6, 10.0)]
REG_LAMBDA = 0.01


def fetch_binance_asset_data(symbol):
    """Compatibility name: read the frozen local cache only; never acquire data."""
    with (ROOT / "research_extension/data/binance_market_data.json").open() as handle:
        return json.load(handle)[symbol]


def simulate_model_response(
    params, v_series, M=None, *, initial_state=(0.0, 0.0), return_state=False
):
    """Return x[t+1] from x'=a*x+y+kappa*v, y'=(1-eta)*y+eta*Q*x.

    Both updates use the old state. M is accepted for compatibility but no longer
    truncates memory. The returned final (x,y) state continues the same path.
    """
    theta = np.asarray(params, dtype=float)
    flow = np.asarray(v_series, dtype=float)
    state = np.asarray(initial_state, dtype=float)
    if theta.shape != (4,) or state.shape != (2,) or flow.ndim != 1:
        raise ValueError("Expected four parameters, a two-state vector and 1-D flow.")
    if not all(np.all(np.isfinite(v)) for v in (theta, flow, state)):
        raise ValueError("Response inputs must be finite.")
    a, eta, q, kappa = theta
    x, y = state
    pred = np.empty(len(flow))
    with np.errstate(over="raise", invalid="raise"):
        for t, v in enumerate(flow):
            x, y = a * x + y + kappa * v, (1.0 - eta) * y + eta * q * x
            pred[t] = x
    if not np.all(np.isfinite(pred)) or not np.isfinite(y):
        raise ValueError("Non-finite response path.")
    return (pred, (float(x), float(y))) if return_state else pred


def train_single_seed(prices, signed_flow, seed, n_epochs=10, train_ratio=0.70):
    """Fit every epoch on the same contiguous prefix; reject invalid fits.

    target[t] = prices[t+1]-prices[t], input[t] = signed_flow[t].
    The final flow observation is unused. A fixed zero initial state is a model
    assumption, not an observed market reset. No validation-based selection.
    """
    if not np.isfinite(train_ratio) or not 0 < train_ratio < 1:
        raise ValueError("train_ratio must lie strictly between 0 and 1.")
    if not isinstance(n_epochs, (int, np.integer)) or n_epochs < 1:
        raise ValueError("n_epochs must be a positive integer.")
    prices = np.asarray(prices, dtype=float)
    signed_flow = np.asarray(signed_flow, dtype=float)
    if prices.ndim != 1 or prices.shape != signed_flow.shape:
        raise ValueError("Prices and signed flow must be aligned 1-D arrays of equal length.")
    if not np.all(np.isfinite(prices)) or not np.all(np.isfinite(signed_flow)):
        raise ValueError("Prices and signed flow must be finite.")
    if np.any(prices <= 0):
        raise ValueError("Prices must be positive.")
    target, flow = np.diff(prices), signed_flow[:-1]
    n_train = int(len(target) * train_ratio)
    if n_train < 16 or len(target) - n_train < 3:
        raise ValueError("train_ratio must leave at least 16 training and 3 validation transitions.")
    target_train, flow_train = target[:n_train], flow[:n_train]
    if np.var(flow_train) == 0:
        raise ValueError("Constant training flow cannot identify the response fit.")

    rng = np.random.default_rng(seed)
    init_a = float(np.clip(0.35 + rng.normal(0, 0.05), 0.1, 0.7))
    init_eta = float(np.clip(0.05 + rng.normal(0, 0.01), 0.01, 0.3))
    init_q = float(np.clip(0.35 + rng.normal(0, 0.05), 0.05, 0.7))
    cov = np.cov(target_train, flow_train)[0, 1]
    init_kappa = np.clip(abs(cov) / np.var(flow_train), *BOUNDS[3])
    theta = np.array([init_a, init_eta, init_q, init_kappa])

    def loss_fn(p):
        try:
            pred = simulate_model_response(p, flow_train)
            with np.errstate(over="raise", invalid="raise"):
                return float(np.mean((target_train - pred)**2) + REG_LAMBDA * p[2]**2)
        except (FloatingPointError, ValueError):
            return float("inf")

    epochs = []
    for epoch in range(n_epochs):
        result = minimize(
            loss_fn, theta, method="L-BFGS-B", bounds=BOUNDS,
            options={"maxiter": 500, "maxls": 40, "ftol": 1e-12, "gtol": 1e-8},
        )
        if not result.success:
            raise RuntimeError(f"Optimizer failed at epoch {epoch + 1}: {result.message}")
        theta = np.asarray(result.x, dtype=float)
        if theta.shape != (4,) or not np.all(np.isfinite(theta)) or not np.isfinite(result.fun):
            raise RuntimeError(f"Optimizer returned non-finite parameters/objective at epoch {epoch + 1}.")
        if any(p < lo or p > hi for p, (lo, hi) in zip(theta, BOUNDS)):
            raise RuntimeError(f"Optimizer returned parameters outside bounds at epoch {epoch + 1}.")
        objective = loss_fn(theta)
        if not np.isfinite(objective):
            raise RuntimeError(f"Non-finite fitted training path at epoch {epoch + 1}.")
        epochs.append({
            "epoch": epoch + 1, "objective": objective, "optimizer_success": True,
            "optimizer_status": int(result.status), "optimizer_message": str(result.message),
            "iterations": int(result.nit), "function_evaluations": int(result.nfev),
        })

    pred_train, boundary_state = simulate_model_response(theta, flow_train, return_state=True)
    pred_val = simulate_model_response(theta, flow[n_train:], initial_state=boundary_state)
    with np.errstate(over="raise", invalid="raise"):
        train_mse = float(np.mean((target_train - pred_train)**2))
        val_mse = float(np.mean((target[n_train:] - pred_val)**2))
        ss_tot = float(np.sum((target[n_train:] - np.mean(target[n_train:]))**2))
        r2 = float(1 - np.sum((target[n_train:] - pred_val)**2) / ss_tot) if ss_tot > 0 else None
    if not np.isfinite(train_mse) or not np.isfinite(val_mse) or (r2 is not None and not np.isfinite(r2)):
        raise RuntimeError("Non-finite validation metrics.")
    a, eta, q, kappa = map(float, theta)
    return {
        "status": "ok", "seed": int(seed), "a": a, "eta": eta, "Q": q, "kappa": kappa,
        "s_hat": a + q, "oos_r2": r2,
        "r2_interpretation": "conditional_flow_replay; validation-mean denominator; unclipped",
        "r2_undefined_reason": "constant_validation_outcome" if r2 is None else None,
        "train_loss_final": train_mse, "val_loss_final": val_mse,
        "initial_state": [0.0, 0.0], "validation_initial_state": list(boundary_state),
        "temporal_split": {
            "index_convention": "zero-based, half-open, price transitions",
            "n_prices": len(prices), "n_transitions": len(target), "train_ratio": train_ratio,
            "train_transition_indices": [0, n_train],
            "validation_transition_indices": [n_train, len(target)],
            "last_flow_index_unused": len(signed_flow) - 1,
            "validation_outcomes_used_for_training": False,
            "epoch_selection": "fixed final epoch; no validation selection",
        },
        "regularization": {"lambda": REG_LAMBDA, "term": "Q_squared"},
        "parameter_bounds": BOUNDS,
        "bound_hits": [name for name, p, (lo, hi) in zip(("a", "eta", "Q", "kappa"), theta, BOUNDS)
                       if min(abs(p - lo), abs(p - hi)) < 1e-5],
        "spectral_radius": float(max(abs(np.linalg.eigvals([[a, 1], [eta * q, 1 - eta]])))),
        "epochs": epochs, "train_predictions": pred_train.tolist(),
        "validation_predictions": pred_val.tolist(),
    }


def train_asset_multi_seed_multi_epoch(asset_data, seeds=SEEDS, n_epochs=N_EPOCHS):
    """Retain every requested seed, including failures; never average survivors."""
    if not seeds or len(set(seeds)) != len(seeds):
        raise ValueError("Seeds must be a nonempty sequence of unique values.")
    runs = []
    for seed in seeds:
        try:
            runs.append(train_single_seed(asset_data["prices"], asset_data["signed_flow"], seed, n_epochs))
        except (ValueError, RuntimeError, FloatingPointError) as exc:
            runs.append({"seed": int(seed), "status": "failed", "reason": str(exc)})
    complete = all(r["status"] == "ok" for r in runs)
    values = np.array([r["s_hat"] for r in runs]) if complete else None
    r2_values = [r["oos_r2"] for r in runs] if complete else []
    closes = np.asarray(asset_data["closes"], dtype=float)
    if closes.ndim != 1 or len(closes) < 35 or not np.all(np.isfinite(closes)) or np.any(closes <= 0):
        raise ValueError("Invalid candle closes.")
    from research_extension.mm_revision.inference.observational import compute_empirical_persistence_proxy
    returns = np.diff(np.log(closes))
    n_a = int(len(returns) * .70)
    return {
        "symbol": asset_data["symbol"], "status": "ok" if complete else "failed_seed_panel",
        "rel_spread_bps": float(asset_data["rel_spread_bps"]),
        "vol_bps_A": float(np.std(returns[:n_a]) * 10000),
        "rho_1_A": compute_empirical_persistence_proxy(returns[:n_a])["rho_lags"]["rho_1"],
        "rho_1_B": compute_empirical_persistence_proxy(returns[n_a:])["rho_lags"]["rho_1"],
        "candle_split": {"period_A_return_indices": [0, n_a], "period_B_return_indices": [n_a, len(returns)]},
        "tick_candle_temporal_alignment": "unverified: cache omits timestamps",
        "mean_s_hat": float(np.mean(values)) if complete else None,
        "std_s_hat": float(np.std(values)) if complete else None,
        "seed_range_s_hat": [float(min(values)), float(max(values))] if complete else None,
        "seed_dispersion_interpretation": "optimizer initialization sensitivity, not sampling uncertainty",
        "mean_oos_r2": float(np.mean(r2_values)) if r2_values and all(v is not None for v in r2_values) else None,
        "n_seeds": len(seeds), "n_epochs": n_epochs, "seed_runs": runs,
    }


def run_binance_study():
    """Return corrected cache-only results; this function writes no artifacts."""
    from research_extension.mm_revision.studies.empirical import run_ols_regression
    assets = [train_asset_multi_seed_multi_epoch(fetch_binance_asset_data(s)) for s in BINANCE_ASSETS]
    complete = all(a["status"] == "ok" for a in assets)
    regression = {"status": "unavailable", "reason": "At least one requested seed failed; no survivor regression."}
    if complete:
        x = np.array([[1, a["mean_s_hat"], a["rel_spread_bps"], a["vol_bps_A"]] for a in assets])
        try:
            regression = {"status": "ok", **run_ols_regression(x, [a["rho_1_B"] for a in assets])}
        except ValueError as exc:
            regression = {"status": "unavailable", "reason": str(exc)}
    regression.update({
        "evaluation_type": "in_sample_explanatory", "out_of_sample": False,
        "regressors": ["intercept", "mean_s_hat", "rel_spread_bps", "vol_bps_A"],
        "symbols": BINANCE_ASSETS, "outcome": "rho_1_B",
        "limitation": "No timestamp evidence that tick-training observations precede candle Period B.",
    })
    return {
        "exchange": "Binance US", "status": "ok" if complete else "failed_seed_panel",
        "n_assets": len(assets), "seeds": SEEDS, "n_epochs_per_seed": N_EPOCHS,
        "requested_optimization_passes": len(assets) * len(SEEDS) * N_EPOCHS,
        "asset_results": assets, "cross_sectional_regression": regression,
    }


if __name__ == "__main__":
    # The evidence-repair generator writes provenance and results together.
    print(json.dumps(run_binance_study(), indent=2, allow_nan=False))
