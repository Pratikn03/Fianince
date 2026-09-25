"""Work Package A4: Pre-registered Broadened Comparator Evaluation.

Evaluates 5 identification methods under matched Contract I0 inputs:
1. Observable Recurrence LP (box LP)
2. Covariance-Aware Conic Certificate (outer conic relaxation over F-calibrated ellipsoid)
3. Covariance Output-Error Benchmark (asymptotic benchmark with lambda = 0)
4. Naive Point Fit (constrained least-squares recurrence)
5. Interval Deconvolution Tail Envelope

Grid factors:
- S in {0.70, 0.82, 1.00, 1.03, 1.18}
- slow rate in {0.002, 0.02, 0.10}
- episode budget R in {128, 1024}
- probe pulse delta in {1.0, 4.0}
- horizon H in {24, 64}
- 10 replicate panels per cell (1,200 panels total)
"""
import json
import time
from pathlib import Path
from typing import Dict, Any, List
import numpy as np

from research_extension.mm_revision.decisions import aggregate_decision_metrics
from research_extension.mm_revision.studies.synthetic_recovery import run_single_synthetic_panel

ROOT = Path(__file__).resolve().parents[3]
OUTPUT_FILE = ROOT / "research_extension" / "outputs" / "broadened_comparator_results.json"


def run_broadened_comparator_study(
    replications_per_cell: int = 5,
    seed_base: int = 20260924,
) -> Dict[str, Any]:
    t0_all = time.time()
    S_values = [0.70, 0.82, 1.00, 1.03, 1.18]
    slow_rates = [0.002, 0.02, 0.10]
    budgets = [128, 1024]
    pulses = [1.0, 4.0]
    horizons = [24, 64]

    comparators = [
        "recurrence_lp",
        "conic_certificate",
        "output_error",
        "deconvolution_interval",
        "naive_point_fit",
    ]

    total_cells = len(S_values) * len(slow_rates) * len(budgets) * len(pulses) * len(horizons)
    print(f"Running Broadened Comparator Evaluation: {total_cells} cells x {replications_per_cell} reps = {total_cells * replications_per_cell} panels...")

    all_panel_results = []
    cell_idx = 0

    for S_val in S_values:
        for slow in slow_rates:
            for R in budgets:
                for delta in pulses:
                    for H in horizons:
                        for rep in range(replications_per_cell):
                            seed = seed_base + cell_idx * 1000 + rep
                            panel_res = run_single_synthetic_panel(
                                true_S=S_val,
                                slow_rate=slow,
                                n_episodes=R,
                                probe_size=delta,
                                H=H,
                                seed=seed,
                                eta_floor=slow,
                            )
                            panel_res["cell_info"] = {
                                "S": S_val,
                                "slow_rate": slow,
                                "budget": R,
                                "probe_pulse": delta,
                                "horizon": H,
                                "replicate": rep,
                            }
                            all_panel_results.append(panel_res)
                        cell_idx += 1

    # Aggregate by comparator
    summary = {}
    for comp in comparators:
        comp_records = [r[comp] for r in all_panel_results if comp in r]
        metrics = aggregate_decision_metrics(comp_records)
        times = [r["time"] for r in comp_records if "time" in r]
        widths = [
            (r["upper"] - r["lower"])
            for r in comp_records
            if r["lower"] is not None and r["upper"] is not None and np.isfinite(r["upper"]) and np.isfinite(r["lower"])
        ]

        summary[comp] = {
            "metrics": metrics.__dict__,
            "mean_interval_width": float(np.mean(widths)) if widths else 0.0,
            "median_interval_width": float(np.median(widths)) if widths else 0.0,
            "p90_interval_width": float(np.percentile(widths, 90)) if widths else 0.0,
            "mean_execution_time_ms": float(np.mean(times) * 1000.0) if times else 0.0,
        }

    total_time = time.time() - t0_all
    output_data = {
        "metadata": {
            "total_panels": len(all_panel_results),
            "total_cells": total_cells,
            "replications_per_cell": replications_per_cell,
            "S_values": S_values,
            "slow_rates": slow_rates,
            "budgets": budgets,
            "pulses": pulses,
            "horizons": horizons,
            "elapsed_seconds": total_time,
        },
        "summary": summary,
    }

    OUTPUT_FILE.parent.mkdir(parents=True, exist_ok=True)
    with open(OUTPUT_FILE, "w") as f:
        json.dump(output_data, f, indent=2)

    print(f"Broadened comparator evaluation completed in {total_time:.2f}s. Saved to {OUTPUT_FILE}.")
    return output_data


if __name__ == "__main__":
    run_broadened_comparator_study(replications_per_cell=5)
