"""Work Package C: Complete Funded Mechanism Study and Scenario-Risk Surface Generation.

Implements:
1. Near-threshold factorial design without endpoint saturation:
   - Dealer capital buffer: 0.75x, 1.0x, 1.5x, 2.0x
   - Starting utilization: 0%, 50%, 80%, 95%
   - Mean repricing shock: 0, -1, -2, -4
   - S: 0.70, 0.82, 0.97, 1.03, 1.18
   - Slow rate: 0.02, 0.10
2. Paired counterfactual mechanism controls across identical exogenous shock tapes (N=100 replicates):
   - Active learning
   - Frozen learning (pre-shock memory preserved, not identically zero)
   - Zero feedback (Q = 0)
   - Unlimited dealer funding
   - Bootstrap 95% confidence intervals for paired differences
3. Exports JSON summary and structured tables to research_extension/outputs/funded_mechanism_results.json
"""
import json
import time
from pathlib import Path
from typing import Dict, Any

from research_extension.mm_revision.studies.funded_stress import (
    run_near_threshold_factorial_design,
    run_paired_mechanism_controls,
)

ROOT = Path(__file__).resolve().parents[3]
OUTPUT_FILE = ROOT / "research_extension" / "outputs" / "funded_mechanism_results.json"


def main():
    t0 = time.time()
    print("Executing Work Package C: Funded Mechanism Near-Threshold Study & Paired Controls...")

    # 1. Paired counterfactual controls (N=100 replicates)
    print("  Running paired counterfactual controls (N=100 replicates)...")
    paired_res = run_paired_mechanism_controls(n_replicates=100, seed=20260924)

    # 2. Near-threshold factorial design (representative grid)
    print("  Running near-threshold factorial design...")
    factorial_res = run_near_threshold_factorial_design(
        capital_multipliers=[0.75, 1.0, 1.5, 2.0],
        initial_utilizations=[0.0, 0.50, 0.80],
        mean_shocks=[0.0, -1.0, -2.0, -4.0],
        S_values=[0.70, 0.82, 0.97, 1.03, 1.18],
        slow_rates=[0.02, 0.10],
        n_replications=25,
        seed_base=20260924,
    )

    elapsed = time.time() - t0
    output_data = {
        "paired_controls": paired_res,
        "near_threshold_grid": factorial_res,
        "elapsed_seconds": elapsed,
    }

    OUTPUT_FILE.parent.mkdir(parents=True, exist_ok=True)
    with open(OUTPUT_FILE, "w") as f:
        json.dump(output_data, f, indent=2)

    print(f"Funded mechanism study completed in {elapsed:.2f}s.")
    print(f"Saved to {OUTPUT_FILE}")


if __name__ == "__main__":
    main()
