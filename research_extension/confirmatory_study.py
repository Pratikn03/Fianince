"""Phase 7A: Confirmatory Experiment under Pre-Frozen Protocol.

Protocol Freeze Specification:
- Model: TwoGroupMarketSimulator with true parameters:
    q_A = 0.30 (dominant amplifier, q > 0.20)
    q_B = 0.10 (non-dominant amplifier, q < 0.20)
    eta_A = 0.05, eta_B = 0.05, a = 0.40, kappa = 0.02
- Decision threshold: q* = 0.20
- Evaluated strictly on the held-out 30% Evaluation Sample (untouched during discovery).
- Analysis script, parameter choices, and failure controls locked before execution.
"""

import json
import os
import numpy as np
from research_extension.group_market import generate_group_study_dataset
from research_extension.group_inference import (
    estimate_channel_response,
    compute_group_intervals_lp,
    covariance_aware_output_error,
)
from research_extension.economic_mechanism import run_connected_mechanism_experiment


def run_confirmatory_study(seed=20260924):
    print("=== PHASE 7A: EXECUTING PRE-FROZEN CONFIRMATORY STUDY ===")

    # 1. Generate full dataset (70% discovery, 30% evaluation) with locked seed
    dataset = generate_group_study_dataset(
        n_panels=50,
        episodes_per_panel=128,
        T=32,
        delta=4.0,
        seed=seed,
        q_A=0.30,
        q_B=0.10,
    )

    eval_panels = dataset["evaluation_panels"]
    n_eval = len(eval_panels)
    print(f"Loaded {n_eval} held-out evaluation panels (strictly untouched in discovery).")

    records_A = []
    records_B = []

    # 2. Evaluate held-out panels
    for p in eval_panels:
        # Group A
        b_res_A = estimate_channel_response(p["data"]["group_A"])
        int_A = compute_group_intervals_lp(b_res_A, alpha=0.05)
        cov_A = covariance_aware_output_error(b_res_A)

        covered_A = bool(int_A["q_lower"] <= 0.30 <= int_A["q_upper"])
        decisive_A = bool(int_A["q_lower"] > 0.20 or int_A["q_upper"] < 0.20)
        wrong_A = False
        if decisive_A:
            pred_high = int_A["q_lower"] > 0.20
            actual_high = 0.30 > 0.20  # True
            wrong_A = bool(pred_high != actual_high)

        records_A.append({
            "panel_id": p["panel_id"],
            "covered": covered_A,
            "decisive": decisive_A,
            "wrong": wrong_A,
            "q_lower": int_A["q_lower"],
            "q_upper": int_A["q_upper"],
            "q_point": cov_A["q_point"],
        })

        # Group B
        b_res_B = estimate_channel_response(p["data"]["group_B"])
        int_B = compute_group_intervals_lp(b_res_B, alpha=0.05)
        cov_B = covariance_aware_output_error(b_res_B)

        covered_B = bool(int_B["q_lower"] <= 0.10 <= int_B["q_upper"])
        decisive_B = bool(int_B["q_lower"] > 0.20 or int_B["q_upper"] < 0.20)
        wrong_B = False
        if decisive_B:
            pred_high = int_B["q_lower"] > 0.20
            actual_high = 0.10 > 0.20  # False
            wrong_B = bool(pred_high != actual_high)

        records_B.append({
            "panel_id": p["panel_id"],
            "covered": covered_B,
            "decisive": decisive_B,
            "wrong": wrong_B,
            "q_lower": int_B["q_lower"],
            "q_upper": int_B["q_upper"],
            "q_point": cov_B["q_point"],
        })

    def summarize(recs):
        n = len(recs)
        n_cov = sum(1 for r in recs if r["covered"])
        n_dec = sum(1 for r in recs if r["decisive"])
        n_wrg = sum(1 for r in recs if r["wrong"])
        return {
            "n_panels": n,
            "coverage_pct": float(n_cov / n * 100.0) if n > 0 else 0.0,
            "decisiveness_pct": float(n_dec / n * 100.0) if n > 0 else 0.0,
            "unconditional_error_pct": float(n_wrg / n * 100.0) if n > 0 else 0.0,
            "conditional_error_pct": float(n_wrg / n_dec * 100.0) if n_dec > 0 else 0.0,
            "mean_q_point": float(np.mean([r["q_point"] for r in recs])),
        }

    summary_A = summarize(records_A)
    summary_B = summarize(records_B)

    # 3. Confirmatory Economic Mechanism test on 100 fresh seeds
    econ_summary = run_connected_mechanism_experiment(n_replicates=100, seed=seed + 999)

    out = {
        "status": "CONFIRMATORY_COMPLETED",
        "n_held_out_panels": n_eval,
        "group_A_target": {"true_q": 0.30, "threshold": 0.20, "summary": summary_A},
        "group_B_target": {"true_q": 0.10, "threshold": 0.20, "summary": summary_B},
        "economic_mechanism": econ_summary,
    }

    os.makedirs("research_extension/outputs", exist_ok=True)
    out_path = "research_extension/outputs/confirmatory_results.json"
    with open(out_path, "w") as f:
        json.dump(out, f, indent=2)

    print(f"Confirmatory experiment finished. Results saved to {out_path}.")
    return out


if __name__ == "__main__":
    res = run_confirmatory_study()
    print(json.dumps(res, indent=2))
