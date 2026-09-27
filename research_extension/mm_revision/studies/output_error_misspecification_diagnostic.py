"""Workstream 3A: Formal C1-C4 Diagnostic Sequence for Output-Error Misspecification.

Evaluates:
  C1: Matched 1-rate generator, noiseless.
  C2: Matched 1-rate generator, Gaussian noise with known covariance sigma^2/R I.
  C3: Misspecified 2-rate generator, noiseless.
  C4: Misspecified 2-rate generator, Gaussian noise with known covariance sigma^2/R I.

C1/C3 are single deterministic cases, not independent repeated data. Their
interval containment is not sampling coverage; their supplied 1e-4 I covariance
is a working objective scale. C2/C4 use independent Gaussian coefficient draws,
not simulated/estimated episode covariances. R sets the known noise scale only.
All intervals remain local/asymptotic benchmarks. Unavailable fallback intervals
are retained separately and excluded from every valid-interval coverage rate.
"""

import argparse
from dataclasses import asdict
import json
from pathlib import Path
from typing import Dict, Any, List
import numpy as np
from research_extension.mm_revision.inference.covariance_output_error import fit_covariance_output_error


def simulate_impulse_response(
    a: float,
    rates: List[float],
    weights: List[float],
    kappa: float,
    H: int
) -> np.ndarray:
    """Generate exact deterministic impulse response for multi-rate model."""
    beta = np.zeros(H + 1)
    beta[0] = kappa
    beta[1] = a * beta[0]
    for t in range(1, H):
        k_t = sum(
            q * eta * ((1.0 - eta) ** j)
            for q, eta in zip(weights, rates)
            for j in [t - 1]
        )
        # Recurrence: beta_{t+1} = a * beta_t + sum_{j=0}^{t-1} k_j * beta_{t-1-j}
        k_terms = sum(
            sum(q * eta * ((1.0 - eta) ** j) for q, eta in zip(weights, rates)) * beta[t - 1 - j]
            for j in range(t)
        )
        beta[t + 1] = a * beta[t] + k_terms
    return beta


def _json_safe(value):
    """Strict JSON: undefined scalars are null; infinite endpoints stay explicit."""
    if isinstance(value, np.generic):
        value = value.item()
    if isinstance(value, float) and not np.isfinite(value):
        return None if np.isnan(value) else ("Infinity" if value > 0 else "-Infinity")
    if isinstance(value, dict):
        return {key: _json_safe(item) for key, item in value.items()}
    if isinstance(value, (tuple, list)):
        return [_json_safe(item) for item in value]
    return value


def _fit_record(beta, covariance, true_S):
    """Retain every returned diagnostic or exception; never invent coverage."""
    try:
        result = fit_covariance_output_error(beta, covariance, eta_floor=0.002, reg_lambda=0.0)
    except Exception as exc:
        row = {
            "a": None, "eta": None, "Q": None, "kappa": None,
            "S_model": None, "se_S": None, "objective_value": None,
            "ci_type": "unavailable", "inference_status": "unavailable:exception",
            "profile_status": None, "bound_hit": None, "bound_hits": None,
            "optimizer_success": False, "optimizer_status": None,
            "optimizer_message": str(exc), "diagnostics": None,
            "decision_interval": None, "profile_interval": None, "sandwich_interval": None,
            "exception_type": type(exc).__name__, "exception_message": str(exc),
        }
        fit_available = False
    else:
        row = asdict(result)
        for name in ("optimizer_success", "optimizer_status", "optimizer_message", "bound_hits"):
            row[name] = row["diagnostics"][name]
        row.update(exception_type=None, exception_message=None)
        fit_available = bool(row["optimizer_success"] and all(
            np.isfinite(row[name]) for name in ("a", "eta", "Q", "kappa", "S_model", "objective_value")
        ))

    def finite_interval(interval):
        return bool(interval is not None and len(interval) == 2
                    and np.all(np.isfinite(interval)) and interval[0] <= interval[1])

    profile_status = row["profile_status"]
    profile_available = bool(fit_available and finite_interval(row["profile_interval"])
                             and profile_status is not None and len(profile_status) == 2
                             and all(s in ("crossing", "parameter_bound") for s in profile_status))
    sandwich_available = bool(fit_available and finite_interval(row["sandwich_interval"])
                              and row["se_S"] is not None and np.isfinite(row["se_S"]) and row["se_S"] > 0)
    primary_available = bool(finite_interval(row["decision_interval"]) and (
        (row["ci_type"] == "profile" and profile_available)
        or (row["ci_type"] == "sandwich" and sandwich_available)
    ))
    row.update(fit_available=fit_available, primary_interval=row["decision_interval"],
               primary_available=primary_available, profile_available=profile_available,
               sandwich_available=sandwich_available)
    for kind in ("primary", "profile", "sandwich"):
        interval = row[kind + "_interval"]
        available = row[kind + "_available"]
        row[kind + "_covered"] = bool(interval[0] <= true_S <= interval[1]) if available else None
        row[kind + "_width"] = float(interval[1] - interval[0]) if available else None
    row["fallback_interval"] = row["decision_interval"] if not primary_available else None
    row["profile_fallback_interval"] = row["profile_interval"] if not profile_available else None
    fallback = row["fallback_interval"]
    row["fallback_contains_truth"] = (bool(fallback[0] <= true_S <= fallback[1])
                                      if fallback is not None and not np.any(np.isnan(fallback)) else None)
    row["bias"] = float(row["S_model"] - true_S) if fit_available else None
    # Compatibility fields retain their names, with explicit valid denominators.
    row.update(covered=row["primary_covered"], width=row["primary_width"], objective=row["objective_value"])
    return row


def _summarize(rows, deterministic):
    fit_rows = [row for row in rows if row["fit_available"]]

    def mean(values):
        return float(np.mean(values)) if values else None

    summary = {
        "attempted_count": len(rows), "fit_available_count": len(fit_rows),
        "nonconverged_count": sum(not row["optimizer_success"] for row in rows),
        "exception_count": sum(row["exception_type"] is not None for row in rows),
        "fallback_count": sum(row["fallback_interval"] is not None for row in rows),
        "fallback_contains_truth_count": sum(row["fallback_contains_truth"] is True for row in rows),
        "coverage_kind": ("deterministic_containment_not_sampling_coverage" if deterministic
                          else "known_covariance_gaussian_sampling_coverage"),
        "deterministic_case_count": len(rows) if deterministic else 0,
        "stochastic_panel_count": 0 if deterministic else len(rows),
        "mean_S_model": mean([row["S_model"] for row in fit_rows]),
        "mean_bias": mean([row["bias"] for row in fit_rows]),
        "rmse": float(np.sqrt(np.mean([row["bias"] ** 2 for row in fit_rows]))) if fit_rows else None,
        "bias_denominator": len(fit_rows),
        "bound_hit_pct": mean([100.0 * row["bound_hit"] for row in fit_rows]),
        "bound_hit_denominator": len(fit_rows),
        "mean_objective": mean([row["objective_value"] for row in fit_rows]),
        "objective_denominator": len(fit_rows),
    }
    for kind in ("primary", "profile", "sandwich"):
        valid = [row for row in rows if row[kind + "_available"]]
        prefix = "" if kind == "primary" else kind + "_"
        summary.update({
            prefix + "available_count": len(valid),
            prefix + "unavailable_count": len(rows) - len(valid),
            prefix + "covered_count": sum(row[kind + "_covered"] for row in valid),
            prefix + "coverage_denominator": len(valid),
            prefix + "coverage_pct": (100.0 * sum(row[kind + "_covered"] for row in valid) / len(valid)
                                       if valid else None),
            prefix + "mean_width": mean([row[kind + "_width"] for row in valid]),
        })
    return summary


def run_output_error_diagnostic(
    n_panels: int = 100,
    H: int = 24,
    R: int = 1024,
    seed: int = 20260924
) -> Dict[str, Any]:
    """Return 2 + 2*n_panels records, without file I/O or dropped failures.

    Coverage rates condition on available intervals of the named method. For
    C1/C3 the same fields describe only single-case deterministic containment.
    Bias/RMSE use converged finite point fits, even if interval inference fails.
    """
    rng = np.random.default_rng(seed)
    a_true, kappa_true, true_S, sigma_eps = 0.40, 1.0, 0.82, 0.05
    beta_exact_1rate = simulate_impulse_response(a_true, [0.05], [0.42], kappa_true, H)
    beta_exact_2rate = simulate_impulse_response(a_true, [0.20, 0.02], [0.252, 0.168], kappa_true, H)
    conditions = ["C1_matched_noiseless", "C2_matched_noisy", "C3_misspec_noiseless", "C4_misspec_noisy"]
    known_covariance = np.eye(H + 1) * ((sigma_eps ** 2) / R)
    working_covariance = np.eye(H + 1) * 1e-4
    panel_records = []

    def record(condition, panel_index, beta, deterministic):
        covariance = working_covariance if deterministic else known_covariance
        row = _fit_record(beta, covariance, true_S)
        row.update(condition=condition, panel_index=panel_index, attempt_index=len(panel_records),
                   case_kind="deterministic" if deterministic else "noisy_known_covariance",
                   covariance_kind="noiseless_working_covariance" if deterministic else "known_gaussian_covariance",
                   covariance_structure="diagonal", covariance_variance=float(covariance[0, 0]),
                   beta_hat=beta.tolist())
        panel_records.append(row)

    record(conditions[0], 0, beta_exact_1rate, True)
    record(conditions[2], 0, beta_exact_2rate, True)
    for panel_index in range(n_panels):
        # Preserve the original RNG sequence: C2 then C4 within each panel.
        for condition, exact in ((conditions[1], beta_exact_1rate), (conditions[3], beta_exact_2rate)):
            noise = rng.normal(0.0, sigma_eps / np.sqrt(R), size=H + 1)
            record(condition, panel_index, exact + noise, False)

    summary = {condition: _summarize([row for row in panel_records if row["condition"] == condition],
                                    condition in (conditions[0], conditions[2])) for condition in conditions}
    return _json_safe({
        "true_S": true_S, "n_panels": n_panels, "H": H, "R": R, "seed": seed,
        "sigma_eps": sigma_eps, "confidence_level": 0.95, "eta_floor": 0.002, "reg_lambda": 0.0,
        "total_attempted": len(panel_records), "panel_records": panel_records, "summary": summary,
        "inference_scope": "local_asymptotic_benchmark_not_global_or_finite_sample_certificate",
        "noise_model": "independent_Gaussian_coefficients_with_known_covariance_sigma_eps_squared_over_R_I",
        "coverage_denominator_policy": "available intervals of each named method only; unavailable fallbacks excluded",
        "point_summary_denominator_policy": "converged finite point fits; interval availability not required",
        "noiseless_interpretation": "one deterministic case per condition; containment is not sampling coverage; 1e-4 I is working covariance",
        "nonfinite_encoding": "undefined scalars are null; infinite endpoints are strings Infinity or -Infinity",
    })


def main(argv=None):
    """Write only to an explicitly supplied, previously nonexistent path."""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--n-panels", type=int, default=100)
    parser.add_argument("--H", type=int, default=24)
    parser.add_argument("--R", type=int, default=1024)
    parser.add_argument("--seed", type=int, default=20260924)
    args = parser.parse_args(argv)
    if args.output.exists() or args.output.is_symlink():
        parser.error(f"Refusing existing output path: {args.output}")
    if not args.output.parent.is_dir():
        parser.error(f"Output parent directory does not exist: {args.output.parent}")
    result = run_output_error_diagnostic(n_panels=args.n_panels, H=args.H, R=args.R, seed=args.seed)
    payload = json.dumps(result, indent=2, allow_nan=False)
    try:
        # Exclusive creation also prevents overwrite if a path appears during fitting.
        with args.output.open("x", encoding="utf-8") as stream:
            stream.write(payload + "\n")
    except FileExistsError:
        parser.error(f"Refusing existing output path: {args.output}")
    print(f"Output error diagnostic saved to {args.output}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
