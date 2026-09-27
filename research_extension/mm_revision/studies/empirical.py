"""Exploratory cross-sectional associations of Period-A features with Period B.

Feature/outcome windows are separated in time, but slopes and residual losses use
the same assets' Period-B outcomes. These are in-sample explanatory comparisons.
Structural S is unavailable when flow alignment/fitting fails, never replaced by F.
"""
from dataclasses import asdict
from typing import Dict, Any

import numpy as np
from scipy import stats
from research_extension.mm_revision.inference.observational import (
    compute_empirical_persistence_proxy,
    fit_observational_structural_model,
)


def run_ols_regression(X: np.ndarray, y: np.ndarray) -> Dict[str, Any]:
    """Full-rank OLS with conventional homoskedastic Student-t diagnostics.

    Reject inadequate/nonfinite designs instead of fabricating zero statistics.
    Scaled-column SVD avoids squaring the design's condition number.
    """
    X = np.asarray(X, dtype=float)
    y = np.asarray(y, dtype=float)
    if X.ndim != 2 or y.ndim != 1 or len(X) != len(y):
        raise ValueError("OLS expects an N-by-p design and matching 1-D outcome.")
    n, p = X.shape
    if p == 0 or n <= p:
        raise ValueError("OLS requires more observations than parameters.")
    if not np.all(np.isfinite(X)) or not np.all(np.isfinite(y)):
        raise ValueError("OLS inputs must be finite.")
    scales = np.linalg.norm(X, axis=0)
    if np.any(scales == 0):
        raise ValueError("OLS design is rank deficient.")
    scaled = X / scales
    u, singular, vt = np.linalg.svd(scaled, full_matrices=False)
    if singular[-1] <= np.finfo(float).eps * max(X.shape) * singular[0]:
        raise ValueError("OLS design is rank deficient.")
    beta = (vt.T @ ((u.T @ y) / singular)) / scales
    pred = X @ beta
    resid = y - pred
    df = n - p
    sigma2 = float(resid @ resid / df)
    inverse_design = (vt.T / singular) / scales[:, None]
    se = np.sqrt(sigma2 * np.sum(inverse_design**2, axis=1))
    ss_tot = float(np.sum((y - np.mean(y))**2))
    if ss_tot == 0 or np.any(se == 0):
        raise ValueError("OLS inference is undefined for constant outcomes or zero residual variance.")
    t_stats = beta / se
    p_values = 2 * stats.t.sf(np.abs(t_stats), df)
    return {
        "beta": beta.tolist(), "se": se.tolist(), "t_stats": t_stats.tolist(),
        "p_values": p_values.tolist(), "r2": float(1 - resid @ resid / ss_tot),
        "df": df, "n_obs": n, "sigma": float(np.sqrt(sigma2)),
        "predictions": pred.tolist(), "residuals": resid.tolist(),
        "condition_number_scaled": float(singular[0] / singular[-1]),
        "standard_errors": "conventional_homoskedastic; exploratory, cross-asset independence unverified",
    }


def evaluate_explanatory_records(records):
    """Fit each declared specification and identify its complete-case sample."""
    definitions = {
        "bivariate_F": ["F"], "historical_persistence": ["rho1_A"],
        "conventional_controls": ["spread_bps", "vol_bps"],
        "full_model_F": ["F", "spread_bps", "vol_bps"],
        "full_model_S_model": ["S_model", "spread_bps", "vol_bps"],
    }
    specifications, samples = {}, {}
    for name, predictors in definitions.items():
        sample = [r for r in records if all(r.get(k) is not None and np.isfinite(r[k])
                                           for k in predictors + ["rho1_B"])]
        samples[name] = sample
        result = {
            "evaluation_type": "in_sample_explanatory", "out_of_sample": False,
            "predictors": ["intercept"] + predictors, "outcome": "rho1_B",
            "symbols": [r["symbol"] for r in sample], "n_obs": len(sample),
            "excluded_symbols": [r["symbol"] for r in records if r not in sample],
        }
        x = np.array([[1.] + [r[k] for k in predictors] for r in sample]).reshape(-1, len(predictors) + 1)
        try:
            result.update(run_ols_regression(x, np.array([r["rho1_B"] for r in sample])))
            result["status"] = "ok"
            for i, key in enumerate(predictors, 1):
                prefix = {"S_model": "S", "rho1_A": "rho1"}.get(key, key)
                result.update({f"{prefix}_beta": result["beta"][i], f"{prefix}_tstat": result["t_stats"][i],
                               f"{prefix}_pvalue": result["p_values"][i]})
        except ValueError as exc:
            result.update(status="unavailable", reason=str(exc))
        specifications[name] = result

    comparisons = {}
    for label, name in (("F", "full_model_F"), ("S_model", "full_model_S_model")):
        augmented, sample = specifications[name], samples[name]
        if augmented["status"] != "ok":
            comparisons[label] = {"status": "unavailable", "reason": augmented["reason"]}
            continue
        y = np.array([r["rho1_B"] for r in sample])
        # Refit the baseline on the same sample, including when some S fits failed.
        base = run_ols_regression(np.array([[1, r["spread_bps"], r["vol_bps"]] for r in sample]), y)
        reductions = np.square(base["residuals"]) - np.square(augmented["residuals"])
        comparisons[label] = {
            "status": "ok", "interpretation": "descriptive_nested_model_residual_reduction",
            "symbols": [r["symbol"] for r in sample],
            "mean_residual_loss_reduction": float(np.mean(reductions)),
            "residual_loss_reduction_by_asset": reductions.tolist(),
            "baseline_mse": float(np.mean(np.square(base["residuals"]))),
            "augmented_mse": float(np.mean(np.square(augmented["residuals"]))),
            "limitation": "Nested OLS reduces training SSE mechanically; no forecast-gain inference.",
        }
    return {
        "n_markets": len(records), "records": records,
        "evaluation_type": "in_sample_explanatory", "out_of_sample": False,
        "outcome_used_to_fit_slopes": True, "cross_asset_holdout": False,
        "specifications": specifications, "in_sample_loss_comparison": comparisons,
    }


def evaluate_two_layer_temporal_split(
    asset_panels: Dict[str, Dict[str, Any]], train_ratio: float = 0.70
) -> Dict[str, Any]:
    """Separate feature windows, then fit explanatory regressions on outcome B.

    signed_flow_alignment='closes' is required to use flow with candle prices;
    equal array lengths alone cannot establish shared observation times.
    """
    if not np.isfinite(train_ratio) or not 0 < train_ratio < 1:
        raise ValueError("train_ratio must lie strictly between 0 and 1.")
    records, exclusions = [], []
    for symbol, data in asset_panels.items():
        try:
            closes = np.asarray(data.get("closes", []), dtype=float)
            if closes.ndim != 1 or not np.all(np.isfinite(closes)) or np.any(closes <= 0):
                raise ValueError("Closes must be finite, positive, and one dimensional.")
            returns = np.diff(np.log(closes))
            n_a = int(len(returns) * train_ratio)
            if n_a < 10 or len(returns) - n_a < 10:
                raise ValueError("Each return window must contain at least ten observations.")
            ret_a, ret_b = returns[:n_a], returns[n_a:]
            if min(np.var(ret_a), np.var(ret_b)) < 1e-15:
                raise ValueError("Degenerate return window: persistence outcome/proxy is undefined.")
        except (TypeError, ValueError) as exc:
            exclusions.append({"symbol": symbol, "reason": str(exc)})
            continue
        proxy_a = compute_empirical_persistence_proxy(ret_a)
        proxy_b = compute_empirical_persistence_proxy(ret_b)
        spread = data.get("rel_spread_bps")
        spread = float(spread) if spread is not None else None
        if spread is not None and (not np.isfinite(spread) or spread < 0):
            spread = None
        row = {
            "symbol": symbol, "F": proxy_a["F"], "rho1_A": proxy_a["rho_lags"]["rho_1"],
            "rho1_B": proxy_b["rho_lags"]["rho_1"], "vol_bps": float(np.std(ret_a) * 10000),
            "spread_bps": spread, "spread_timing": "snapshot; membership in Period A unverified",
            "S_model": None, "S_model_status": "unavailable_unaligned_flow",
            "structural_fit_diagnostics": None,
            "temporal_split": {
                "index_convention": "zero-based, half-open return indices",
                "n_closes": len(closes), "n_returns": len(returns),
                "period_A_return_indices": [0, n_a], "period_B_return_indices": [n_a, len(returns)],
                "period_A_close_indices": [0, n_a + 1], "period_B_close_indices": [n_a, len(closes)],
            },
        }
        if data.get("signed_flow_alignment") == "closes":
            try:
                flow = np.asarray(data.get("signed_flow", []), dtype=float)
                if flow.shape != closes.shape or not np.all(np.isfinite(flow)):
                    raise ValueError("Declared aligned flow must be finite and match all closes.")
                fit = fit_observational_structural_model(closes[:n_a + 1], flow[:n_a + 1], train_ratio=.7)
                row["structural_fit_diagnostics"] = asdict(fit.diagnostics)
                if not fit.diagnostics.optimizer_success:
                    raise ValueError(f"Optimizer failure: {fit.diagnostics.optimizer_message}")
                if not np.all(np.isfinite([fit.a, fit.eta, fit.Q, fit.kappa, fit.S_model,
                                          fit.objective_value, fit.validation_loss])):
                    raise ValueError("Non-finite structural fit.")
                if fit.diagnostics.weak_identification:
                    row["S_model_status"] = "unavailable_weak_identification"
                else:
                    row.update(S_model=float(fit.S_model), S_model_status="ok")
            except (ValueError, RuntimeError, FloatingPointError) as exc:
                row.update(S_model_status="fit_failed", structural_fit_error=str(exc))
        records.append(row)
    result = evaluate_explanatory_records(records)
    result.update(excluded_assets=exclusions, n_requested_markets=len(asset_panels), train_ratio=train_ratio)
    return result
