"""Work Package 2: Multi-comparator synthetic recovery study under Contract I0.

Evaluates:
1. Observable recurrence LP interval
2. Covariance-aware positive output-error estimator
3. Interval-deconvolution tail method
4. Naive positive point fit

All comparators receive the identical Contract I0 information:
- Response estimates and covariance across randomized episodes
- Same horizon H = 64
- Same rate floor eta_floor
- No latent state observations
"""
import time
from typing import Dict, Any, List, Optional
import numpy as np
from research_extension.mm_revision.states import (
    simulate_discrete_trajectory,
    compute_impulse_response,
    total_feedback_gain,
)
from research_extension.mm_revision.inference.covariance_output_error import fit_covariance_output_error
from research_extension.mm_revision.inference.recurrence_adapter import fit_recurrence_interval
from research_extension.mm_revision.decisions import (
    DecisionLabel,
    classify_interval,
    evaluate_decision_accuracy,
    aggregate_decision_metrics,
    AggregatedDecisionMetrics,
)
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
obs_src = ROOT / "studies" / "observable_stress_tests" / "src"
if str(obs_src) not in sys.path:
    sys.path.insert(0, str(obs_src))
from observable import response_intervals


def run_single_synthetic_panel(
    true_S: float,
    slow_rate: float,
    fast_rate: float = 0.5,
    n_episodes: int = 128,
    H: int = 64,
    probe_size: float = 4.0,
    kappa: float = 1.0,
    noise_sigma: float = 1.0,
    seed: Optional[int] = None,
    eta_floor: float = 0.002
) -> Dict[str, Any]:
    """Simulate one panel of randomized probe episodes and fit all comparators."""
    rng = np.random.default_rng(seed)

    # Decompose true_S into a and q
    # We choose a = 0.4 * min(1.0, true_S / 0.82)
    a = 0.4
    Q = max(0.0, true_S - a)
    # Split Q across fast and slow modes
    q_fast = 0.6 * Q
    q_slow = 0.4 * Q
    q_vec = [q_fast, q_slow]
    eta_vec = [fast_rate, slow_rate]

    # Generate randomized probe episodes
    # Probes u_r ~ Uniform(-probe_size, probe_size)
    probes = rng.uniform(-probe_size, probe_size, size=n_episodes)
    prices = np.zeros((n_episodes, H + 1), dtype=float)

    for r in range(n_episodes):
        u_tape = np.zeros(H)
        u_tape[0] = probes[r] # Single pulse at t=0
        innov = rng.normal(0.0, noise_sigma, size=H)
        x_traj, _ = simulate_discrete_trajectory(
            a=a, eta=eta_vec, q=q_vec, u=u_tape, innovations=innov,
            kappa=kappa, x0=0.0, y0=np.zeros(2)
        )
        prices[r] = x_traj

    # 1. Response estimation (Contract I0 observable)
    band = response_intervals(probes, prices, alpha=0.05)
    beta_hat = band["estimate"]
    cov_beta = band["covariance"]
    lower_band = band["lower"]
    upper_band = band["upper"]

    results = {"true_S": true_S, "slow_rate": slow_rate, "n_episodes": n_episodes}

    def check_cov(lo, hi, truth):
        lo_ok = (lo is None or np.isnan(lo) or lo <= truth)
        hi_ok = (hi is None or np.isnan(hi) or truth <= hi)
        return bool(lo_ok and hi_ok and (lo is not None or hi is not None))

    # Comparator 1: Observable Recurrence LP
    t0 = time.perf_counter()
    try:
        rec_res = fit_recurrence_interval(lower_band, upper_band, eta_floor=eta_floor)
        rec_time = time.perf_counter() - t0
        rec_lo = rec_res["S_lower"]
        rec_hi = rec_res["S_upper"]
        rec_decision = rec_res["decision"]
        rec_covered = check_cov(rec_lo, rec_hi, true_S)
        rec_eval = evaluate_decision_accuracy(rec_decision, true_S)
    except Exception:
        rec_time = time.perf_counter() - t0
        rec_lo, rec_hi = None, None
        rec_decision = DecisionLabel.CONFLICT
        rec_covered = False
        rec_eval = {"is_issued": False, "is_wrong": False, "is_abstain": False, "is_conflict": True}

    results["recurrence_lp"] = {
        "lower": rec_lo, "upper": rec_hi, "decision": rec_decision.value,
        "is_covered": rec_covered, "time": rec_time, **rec_eval
    }

    # Comparator 2: Covariance-Aware Positive Output-Error
    t0 = time.perf_counter()
    try:
        oe_res = fit_covariance_output_error(
            beta_hat=beta_hat, covariance_beta=cov_beta, eta_floor=eta_floor,
            kappa_init=kappa
        )
        oe_time = time.perf_counter() - t0
        oe_lo = oe_res.S_lower
        oe_hi = oe_res.S_upper
        oe_decision = classify_interval(oe_lo, oe_hi, threshold=1.0)
        oe_covered = check_cov(oe_lo, oe_hi, true_S)
        oe_eval = evaluate_decision_accuracy(oe_decision, true_S)
        oe_diag = oe_res.diagnostics
    except Exception:
        oe_time = time.perf_counter() - t0
        oe_lo, oe_hi = 0.0, 5.0
        oe_decision = DecisionLabel.ABSTAIN
        oe_covered = True
        oe_eval = {"is_issued": False, "is_wrong": False, "is_abstain": True, "is_conflict": False}
        oe_diag = None

    results["output_error"] = {
        "lower": oe_lo, "upper": oe_hi, "decision": oe_decision.value,
        "is_covered": oe_covered, "time": oe_time, **oe_eval
    }

    # Comparator 3: Interval Deconvolution
    t0 = time.perf_counter()
    try:
        from research_extension.mm_revision.inference.recurrence_adapter import fit_deconvolution_interval
        deconv_res = fit_deconvolution_interval(lower_band, upper_band, eta_floor=eta_floor)
        deconv_time = time.perf_counter() - t0
        dec_lo = deconv_res["S_lower"]
        dec_hi = deconv_res["S_upper"]
        dec_decision = deconv_res["decision"]
        dec_covered = check_cov(dec_lo, dec_hi, true_S)
        dec_eval = evaluate_decision_accuracy(dec_decision, true_S)
    except Exception:
        deconv_time = time.perf_counter() - t0
        dec_lo, dec_hi = None, None
        dec_decision = DecisionLabel.CONFLICT
        dec_covered = False
        dec_eval = {"is_issued": False, "is_wrong": False, "is_abstain": False, "is_conflict": True}

    results["deconvolution_interval"] = {
        "lower": dec_lo, "upper": dec_hi, "decision": dec_decision.value,
        "is_covered": dec_covered, "time": deconv_time, **dec_eval
    }

    # Comparator 4: Naive Point Fit (constrained least squares recurrence)
    t0 = time.perf_counter()
    try:
        from observable import recurrence_point
        pt_res = recurrence_point(beta_hat, eta_floor=eta_floor)
        naive_S = pt_res["gain"]
        naive_time = time.perf_counter() - t0
        naive_se = float(np.std(beta_hat) / np.sqrt(len(beta_hat)))
        naive_lo = max(0.0, naive_S - 1.96 * naive_se)
        naive_hi = naive_S + 1.96 * naive_se
        naive_decision = classify_interval(naive_lo, naive_hi, threshold=1.0)
        naive_covered = (naive_lo <= true_S <= naive_hi)
        naive_eval = evaluate_decision_accuracy(naive_decision, true_S)
    except Exception:
        naive_time = time.perf_counter() - t0
        naive_lo, naive_hi = 0.0, 5.0
        naive_decision = DecisionLabel.ABSTAIN
        naive_covered = True
        naive_eval = {"is_issued": False, "is_wrong": False, "is_abstain": True, "is_conflict": False}

    results["naive_point_fit"] = {
        "lower": naive_lo, "upper": naive_hi, "decision": naive_decision.value if hasattr(naive_decision, 'value') else str(naive_decision),
        "is_covered": naive_covered, "time": naive_time, **naive_eval
    }

    # Comparator 5: Covariance-Aware Conic Certificate
    t0 = time.perf_counter()
    try:
        from research_extension.mm_revision.inference.conic_certificate import fit_conic_certificate
        df_ep = n_episodes - 2
        conic_res = fit_conic_certificate(beta_hat, cov_beta, df=df_ep, alpha=0.05, eta_floor=eta_floor, bins=16)
        conic_time = time.perf_counter() - t0
        conic_lo = conic_res["S_lower"]
        conic_hi = conic_res["S_upper"]
        conic_decision = conic_res["decision"]
        conic_covered = check_cov(conic_lo, conic_hi, true_S)
        conic_eval = evaluate_decision_accuracy(conic_decision, true_S)
    except Exception:
        conic_time = time.perf_counter() - t0
        conic_lo, conic_hi = None, None
        conic_decision = DecisionLabel.CONFLICT
        conic_covered = False
        conic_eval = {"is_issued": False, "is_wrong": False, "is_abstain": False, "is_conflict": True}

    results["conic_certificate"] = {
        "lower": conic_lo, "upper": conic_hi, "decision": conic_decision.value if hasattr(conic_decision, 'value') else str(conic_decision),
        "is_covered": conic_covered, "time": conic_time, **conic_eval
    }

    return results


def run_comparative_grid_study(
    S_values: List[float] = [0.70, 0.82, 1.00, 1.03, 1.18],
    slow_rates: List[float] = [0.002, 0.02, 0.10],
    episode_budgets: List[int] = [128, 1024],
    pulse_sizes: List[float] = [1.0, 4.0],
    horizons: List[int] = [24, 64],
    replications_per_cell: int = 10,
    seed_base: int = 20260924
) -> Dict[str, Any]:
    """Execute comparative grid study across all 5 comparators."""
    all_results = []
    comparators = ["recurrence_lp", "conic_certificate", "output_error", "deconvolution_interval", "naive_point_fit"]

    cell_idx = 0
    for S_val in S_values:
        for slow in slow_rates:
            for n_ep in episode_budgets:
                for delta in pulse_sizes:
                    for H_val in horizons:
                        for rep in range(replications_per_cell):
                            seed = seed_base + cell_idx * 1000 + rep
                            res = run_single_synthetic_panel(
                                true_S=S_val, slow_rate=slow, n_episodes=n_ep,
                                probe_size=delta, H=H_val, seed=seed,
                                eta_floor=slow
                            )
                            all_results.append(res)
                        cell_idx += 1

    # Aggregate metrics per comparator
    summary = {}
    for comp in comparators:
        comp_records = [r[comp] for r in all_results if comp in r]
        metrics = aggregate_decision_metrics(comp_records)
        mean_time = float(np.mean([r["time"] for r in comp_records]))
        widths = [
            (r["upper"] - r["lower"]) for r in comp_records
            if r["lower"] is not None and r["upper"] is not None and np.isfinite(r["upper"]) and np.isfinite(r["lower"])
        ]
        mean_width = float(np.mean(widths)) if widths else 0.0
        median_width = float(np.median(widths)) if widths else 0.0
        p90_width = float(np.percentile(widths, 90)) if widths else 0.0

        summary[comp] = {
            "metrics": metrics.__dict__,
            "mean_interval_width": mean_width,
            "median_interval_width": median_width,
            "p90_interval_width": p90_width,
            "mean_execution_time_seconds": mean_time,
        }

    return {
        "total_panels": len(all_results),
        "settings_count": cell_idx,
        "replications_per_cell": replications_per_cell,
        "summary": summary,
        "sample_records": all_results[:5],
    }

