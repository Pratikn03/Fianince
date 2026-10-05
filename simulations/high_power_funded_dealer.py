"""
High-Power Funded Dealer Solvency Monte Carlo Simulation (N = 1,000)
===================================================================
Machine Markets — High-Precision Solvency Risk Surface

Replaces the N = 30 legacy runs in Table 16 with high-power N = 1,000 Monte Carlo
replications per cell, shrinking confidence intervals from ±18.5% down to ±1.5%.

Evaluates exact Clopper-Pearson 95% confidence intervals for all failure and halt
probabilities, and computes mean dislocation and minimum dealer equity.

Outputs:
  - /Volumes/T9/machine_markets_data/high_power_simulations/high_power_table16_results.json
  - research_extension/outputs/high_power_table16_results.json
"""
from __future__ import annotations
import os
import json
from pathlib import Path
from typing import Dict, Any, List, Tuple
import numpy as np
from scipy.stats import beta

from research_extension.mm_revision.studies.funded_stress import FundedScenarioMarket

ROOT = Path(__file__).resolve().parents[1]
T9_OUTPUT_DIR = Path("/Volumes/T9/machine_markets_data/high_power_simulations")
LOCAL_OUTPUT_DIR = ROOT / "research_extension" / "outputs"


def clopper_pearson_ci(k: int, n: int, alpha: float = 0.05) -> Tuple[float, float]:
    """Exact Clopper-Pearson two-sided binomial confidence interval."""
    if k == 0:
        lo = 0.0
    else:
        lo = float(beta.ppf(alpha / 2.0, k, n - k + 1))
    if k == n:
        hi = 1.0
    else:
        hi = float(beta.ppf(1.0 - alpha / 2.0, k + 1, n - k))
    return lo, hi


def run_high_power_table16(n_reps: int = 1000, seed_base: int = 20260924) -> Dict[str, Any]:
    """Execute high-power N = 1,000 replications for every cell in Table 16."""
    # Define exact Table 16 cells (S, capacity_mult, shock_mu)
    cells_spec = [
        # S = 0.70
        (0.70, 0.5, -0.2),
        (0.70, 0.5, -0.6),
        (0.70, 1.0, -0.2),
        (0.70, 1.0, -0.6),
        (0.70, 2.0, -0.6),
        (0.70, 2.0, -2.0),
        # S = 0.82
        (0.82, 0.5, -0.2),
        (0.82, 0.5, -0.4),
        (0.82, 1.0, -0.2),
        (0.82, 1.0, -0.4),
        (0.82, 1.0, -0.6), # The legacy 43.3% cell
        (0.82, 1.0, -0.8),
        (0.82, 2.0, -0.6),
        (0.82, 2.0, -1.0),
        (0.82, 2.0, -2.0),
        # S = 1.18
        (1.18, 0.5, -0.2),
        (1.18, 0.5, -0.4),
        (1.18, 1.0, -0.2),
        (1.18, 1.0, -0.6),
        (1.18, 1.0, -0.8),
        (1.18, 2.0, -1.0),
        (1.18, 2.0, -2.0),
    ]

    rng = np.random.default_rng(seed_base)
    results = []

    print(f"Starting High-Power Monte Carlo (N = {n_reps} replications per cell, {len(cells_spec)} cells)...")

    for idx, (S_val, cap_mult, m_shock) in enumerate(cells_spec):
        a = 0.40
        Q = max(0.0, S_val - a)
        q_f = 0.6 * Q
        q_s = 0.4 * Q
        init_u = 0.20 # 20% initial utilization from Table 16 spec
        s_rate = 0.02 # eta_slow = 0.02 from Table 16 spec

        fail_count = 0
        halt_count = 0
        default_count = 0
        dislocations = []
        min_equities = []

        for rep in range(n_reps):
            shock_tape = rng.normal(0.0, 0.05, size=64)
            market = FundedScenarioMarket(
                a=a,
                q_fast=q_f,
                q_slow=q_s,
                eta_slow=s_rate,
                dealer_capital_multiplier=cap_mult,
                initial_utilization=init_u
            )
            res = market.run_trajectory(
                shock_tape=shock_tape,
                mean_repricing_shock=m_shock,
                learning_regime="adaptive"
            )
            if res["composite_failure"]:
                fail_count += 1
            if res["dealer_halt"]:
                halt_count += 1
            if res["dealer_default"]:
                default_count += 1
            dislocations.append(res["mean_dislocation"])
            min_equities.append(res["min_equity"])

        fail_pct = (fail_count / n_reps) * 100.0
        halt_pct = (halt_count / n_reps) * 100.0
        fail_ci_lo, fail_ci_hi = clopper_pearson_ci(fail_count, n_reps)
        halt_ci_lo, halt_ci_hi = clopper_pearson_ci(halt_count, n_reps)
        mean_disloc = float(np.mean(dislocations))
        mean_min_eq = float(np.mean(min_equities))

        cell_res = {
            "cell_idx": idx,
            "S": S_val,
            "capital_multiplier": cap_mult,
            "mean_shock": m_shock,
            "initial_utilization": init_u,
            "slow_rate": s_rate,
            "n_reps": n_reps,
            "fail_count": fail_count,
            "fail_rate_pct": fail_pct,
            "fail_ci_95": (fail_ci_lo * 100.0, fail_ci_hi * 100.0),
            "halt_count": halt_count,
            "halt_rate_pct": halt_pct,
            "halt_ci_95": (halt_ci_lo * 100.0, halt_ci_hi * 100.0),
            "default_count": default_count,
            "default_rate_pct": (default_count / n_reps) * 100.0,
            "mean_dislocation": mean_disloc,
            "std_dislocation": float(np.std(dislocations)),
            "mean_min_equity": mean_min_eq,
            "std_min_equity": float(np.std(min_equities)),
        }
        results.append(cell_res)
        print(f"[{idx+1:02d}/{len(cells_spec)}] S={S_val:.2f}, Cap={cap_mult:.1f}x, Shock={m_shock:+.1f} -> "
              f"Halt={halt_pct:.1f}% (CI [{halt_ci_lo*100:.1f}%, {halt_ci_hi*100:.1f}%]), "
              f"Mean Disloc={mean_disloc:.4f}, Mean Min Eq=${mean_min_eq:.2f}")

    output_data = {
        "metadata": {
            "description": "High-Power Monte Carlo Simulation for Table 16",
            "n_replications_per_cell": n_reps,
            "total_trajectories": n_reps * len(cells_spec),
            "seed_base": seed_base,
            "confidence_level": 0.95,
            "ci_method": "Clopper-Pearson exact binomial",
        },
        "cells": results,
    }

    # Save to T9 and local output directory
    T9_OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    LOCAL_OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    t9_path = T9_OUTPUT_DIR / "high_power_table16_results.json"
    local_path = LOCAL_OUTPUT_DIR / "high_power_table16_results.json"

    with open(t9_path, "w") as f:
        json.dump(output_data, f, indent=2)
    with open(local_path, "w") as f:
        json.dump(output_data, f, indent=2)

    print(f"\nSuccessfully wrote high-power results to:")
    print(f"  - {t9_path}")
    print(f"  - {local_path}")
    return output_data


if __name__ == "__main__":
    run_high_power_table16(n_reps=1000)
