"""Workstream 4D: Fine-Grained Near-Threshold Funded Scenario-Risk Surface.

Evaluates intermediate failure and trading halt probabilities by sweeping shock
magnitude mu smoothly across [-0.1, -2.0] and dealer capital multipliers across
[0.75, 2.0], resolving the 100% saturation critique.
"""

import json
from pathlib import Path
from typing import Dict, Any, List
import numpy as np

from research_extension.mm_revision.studies.funded_stress import FundedScenarioMarket


def run_smooth_funded_surface(
    S_values: List[float] = [0.70, 0.82, 0.97, 1.03, 1.18],
    capital_multipliers: List[float] = [0.5, 0.75, 1.0, 1.5, 2.0, 4.0],
    shocks: List[float] = [-0.1, -0.2, -0.3, -0.4, -0.5, -0.6, -0.7, -0.8, -1.0, -1.5, -2.0],
    n_replications: int = 30,
    seed: int = 20260924
) -> Dict[str, Any]:
    """Execute fine-grained near-threshold factorial design."""
    rng = np.random.default_rng(seed)
    cells = []

    for S_val in S_values:
        a = 0.40
        kappa = 0.02
        phi = (1.0 - a) / kappa  # 30.0: preserves structural unmediated persistence a
        Q = max(0.0, S_val - a)
        q_f = 0.6 * Q
        q_s = 0.4 * Q

        for cap_mult in capital_multipliers:
            for shock in shocks:
                halt_count = 0
                default_count = 0
                composite_count = 0
                dislocations = []
                min_equities = []

                for rep in range(n_replications):
                    shock_tape = rng.normal(0.0, 0.10, size=64)
                    market = FundedScenarioMarket(
                        a=a,
                        kappa=kappa,
                        phi=phi,
                        q_fast=q_f,
                        q_slow=q_s,
                        eta_slow=0.02,
                        dealer_capital_multiplier=cap_mult,
                        initial_utilization=0.20
                    )
                    res = market.run_trajectory(
                        shock_tape=shock_tape,
                        mean_repricing_shock=shock,
                        initial_memory=(0.0, 0.0),
                        learning_regime="adaptive"
                    )

                    if res["dealer_halt"]:
                        halt_count += 1
                    if res["dealer_default"]:
                        default_count += 1
                    if res["composite_failure"]:
                        composite_count += 1

                    dislocations.append(res["mean_dislocation"])
                    min_equities.append(res["min_equity"])

                cells.append({
                    "S": S_val,
                    "capital_multiplier": cap_mult,
                    "shock_mu": shock,
                    "halt_rate_pct": float((halt_count / n_replications) * 100.0),
                    "default_rate_pct": float((default_count / n_replications) * 100.0),
                    "composite_failure_pct": float((composite_count / n_replications) * 100.0),
                    "mean_dislocation": float(np.mean(dislocations)),
                    "mean_min_equity": float(np.mean(min_equities))
                })

    return {
        "n_cells": len(cells),
        "n_replications_per_cell": n_replications,
        "grid_cells": cells
    }


if __name__ == "__main__":
    out_dir = Path("research_extension/outputs")
    out_dir.mkdir(parents=True, exist_ok=True)
    res = run_smooth_funded_surface()
    out_file = out_dir / "funded_smooth_surface_results.json"
    with open(out_file, "w") as f:
        json.dump(res, f, indent=2)
    print(f"Smooth funded surface saved to {out_file} ({res['n_cells']} cells)")

    # Print a sample slice showing smooth probability transition for S=0.82
    print("\nSample Transition Curve (S=0.82, Capital=1.0x):")
    slice_cells = [c for c in res["grid_cells"] if c["S"] == 0.82 and c["capital_multiplier"] == 1.0]
    for c in slice_cells:
        print(f"  shock={c['shock_mu']:4.1f}: Halt={c['halt_rate_pct']:5.1f}%, CompFail={c['composite_failure_pct']:5.1f}%, Disloc={c['mean_dislocation']:.3f}")
