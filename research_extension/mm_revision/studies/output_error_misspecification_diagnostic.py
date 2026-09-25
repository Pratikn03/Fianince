"""Workstream 3A: Formal C1-C4 Diagnostic Sequence for Output-Error Misspecification.

Evaluates:
  C1: Matched 1-rate generator, noiseless.
  C2: Matched 1-rate generator, noisy (R=1024 episodes).
  C3: Misspecified 2-rate generator, noiseless.
  C4: Misspecified 2-rate generator, noisy (R=1024 episodes).

Demonstrates the exact structural misspecification mechanism that causes
unregularized output-error to fail in heterogeneous multi-rate markets.
"""

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


def run_output_error_diagnostic(
    n_panels: int = 100,
    H: int = 24,
    R: int = 1024,
    seed: int = 20260924
) -> Dict[str, Any]:
    """Run full C1-C4 diagnostic suite."""
    rng = np.random.default_rng(seed)
    a_true = 0.40
    kappa_true = 1.0
    true_S = 0.82

    # 1-rate parameters
    eta_1rate = [0.05]
    q_1rate = [0.42]

    # 2-rate parameters
    eta_2rate = [0.20, 0.02]
    q_2rate = [0.252, 0.168]

    beta_exact_1rate = simulate_impulse_response(a_true, eta_1rate, q_1rate, kappa_true, H)
    beta_exact_2rate = simulate_impulse_response(a_true, eta_2rate, q_2rate, kappa_true, H)

    conditions = ["C1_matched_noiseless", "C2_matched_noisy", "C3_misspec_noiseless", "C4_misspec_noisy"]
    results = {c: [] for c in conditions}

    # Synthetic covariance for noise scale
    # Episode noise var = sigma^2 / R
    sigma_eps = 0.05
    cov_mock = np.eye(H + 1) * ((sigma_eps ** 2) / R)

    for p_idx in range(n_panels):
        # C1: Matched noiseless
        res_c1 = fit_covariance_output_error(beta_exact_1rate, np.eye(H + 1) * 1e-4, eta_floor=0.002, reg_lambda=0.0)
        results["C1_matched_noiseless"].append({
            "S_model": float(res_c1.S_model),
            "bias": float(res_c1.S_model - true_S),
            "bound_hit": bool(res_c1.bound_hit),
            "covered": bool(res_c1.S_lower <= true_S <= res_c1.S_upper),
            "width": float(res_c1.S_upper - res_c1.S_lower),
            "objective": float(res_c1.objective_value)
        })

        # C2: Matched noisy
        noise_c2 = rng.normal(0.0, sigma_eps / np.sqrt(R), size=H + 1)
        res_c2 = fit_covariance_output_error(beta_exact_1rate + noise_c2, cov_mock, eta_floor=0.002, reg_lambda=0.0)
        results["C2_matched_noisy"].append({
            "S_model": float(res_c2.S_model),
            "bias": float(res_c2.S_model - true_S),
            "bound_hit": bool(res_c2.bound_hit),
            "covered": bool(res_c2.S_lower <= true_S <= res_c2.S_upper),
            "width": float(res_c2.S_upper - res_c2.S_lower),
            "objective": float(res_c2.objective_value)
        })

        # C3: Misspecified noiseless
        res_c3 = fit_covariance_output_error(beta_exact_2rate, np.eye(H + 1) * 1e-4, eta_floor=0.002, reg_lambda=0.0)
        results["C3_misspec_noiseless"].append({
            "S_model": float(res_c3.S_model),
            "bias": float(res_c3.S_model - true_S),
            "bound_hit": bool(res_c3.bound_hit),
            "covered": bool(res_c3.S_lower <= true_S <= res_c3.S_upper),
            "width": float(res_c3.S_upper - res_c3.S_lower),
            "objective": float(res_c3.objective_value)
        })

        # C4: Misspecified noisy
        noise_c4 = rng.normal(0.0, sigma_eps / np.sqrt(R), size=H + 1)
        res_c4 = fit_covariance_output_error(beta_exact_2rate + noise_c4, cov_mock, eta_floor=0.002, reg_lambda=0.0)
        results["C4_misspec_noisy"].append({
            "S_model": float(res_c4.S_model),
            "bias": float(res_c4.S_model - true_S),
            "bound_hit": bool(res_c4.bound_hit),
            "covered": bool(res_c4.S_lower <= true_S <= res_c4.S_upper),
            "width": float(res_c4.S_upper - res_c4.S_lower),
            "objective": float(res_c4.objective_value)
        })

    summary = {}
    for c in conditions:
        rows = results[c]
        summary[c] = {
            "mean_S_model": float(np.mean([r["S_model"] for r in rows])),
            "mean_bias": float(np.mean([r["bias"] for r in rows])),
            "rmse": float(np.sqrt(np.mean([r["bias"] ** 2 for r in rows]))),
            "bound_hit_pct": float(np.mean([1.0 if r["bound_hit"] else 0.0 for r in rows]) * 100.0),
            "coverage_pct": float(np.mean([1.0 if r["covered"] else 0.0 for r in rows]) * 100.0),
            "mean_width": float(np.mean([r["width"] for r in rows])),
            "mean_objective": float(np.mean([r["objective"] for r in rows]))
        }

    return {
        "true_S": true_S,
        "n_panels": n_panels,
        "H": H,
        "R": R,
        "summary": summary
    }


if __name__ == "__main__":
    out_dir = Path("research_extension/outputs")
    out_dir.mkdir(parents=True, exist_ok=True)
    res = run_output_error_diagnostic(n_panels=100)
    out_file = out_dir / "output_error_diagnostic_results.json"
    with open(out_file, "w") as f:
        json.dump(res, f, indent=2)
    print(f"Output error diagnostic saved to {out_file}")
    for k, v in res["summary"].items():
        print(f"{k}: S_mean={v['mean_S_model']:.4f}, bias={v['mean_bias']:.4f}, bounds={v['bound_hit_pct']:.1f}%, cov={v['coverage_pct']:.1f}%")
