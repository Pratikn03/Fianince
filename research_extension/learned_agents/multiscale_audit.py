"""
Multiscale Perturbation Radius Audit
=====================================
Machine Markets — Supplement Section S14.6

For each of the 10 trained Q-learning policies and each of five perturbation
radii r ∈ {0.05, 0.10, 0.25, 0.50, 1.00}, this script:

  1. Samples 21 evenly-spaced perturbation points δx ∈ [-r, +r]
  2. Queries the trained Q-table for greedy action at each point
     (using the same discretize_state convention as the main audit:
      state = (δx, ret=δx, inv=0, cap_util=0, imb=0))
  3. Computes R²(r) and ∂u/∂x(r) via OLS on those 21 points
  4. Reports support coverage: fraction of points with non-default Q-values

Key scientific question: Do Q-policies exhibit approximately linear,
positive-feedback responses locally near δx≈0, even if globally nonlinear?
If R²(r=0.05) >> R²(r=1.00), the out-of-class verdict at the global scale
reflects sparse-support extrapolation; if R² is uniformly low at all radii,
the policies genuinely fail the structural class requirements even locally.

Output: research_extension/outputs/learned_agents/multiscale_audit_results.json
"""
from __future__ import annotations
import json
from pathlib import Path
from typing import Dict, Any, List

import numpy as np

from research_extension.learned_agents.q_learning_env import (
    discretize_state, ACTIONS,
)
from research_extension.learned_agents.q_learning_agent import QLearningAgent

ROOT = Path(__file__).resolve().parents[2]
CHECKPOINT_DIR = ROOT / "research_extension" / "outputs" / "learned_agents" / "checkpoints"
RESULTS_DIR = ROOT / "research_extension" / "outputs" / "learned_agents"

# Five nested radii (innermost = local near-origin, outermost = full global range)
RADII: List[float] = [0.05, 0.10, 0.25, 0.50, 1.00]
N_POINTS: int = 21          # odd number → includes exact 0.0
Q_NONDEFAULT_THRESHOLD = 1e-6   # Q-table row is "visited" if any |Q[s,a]| > threshold


def audit_policy_at_radius(
    agent: QLearningAgent,
    radius: float,
    n_points: int = N_POINTS,
) -> Dict[str, Any]:
    """
    Evaluate R²(r) and ∂u/∂x(r) at a given perturbation radius.
    Also reports support coverage: how many queried states have
    non-default (visited-and-updated) Q-table entries.
    """
    agent.set_mode("frozen")
    dx_vals = np.linspace(-radius, radius, n_points)
    actions_chosen = []
    support_flags = []   # True if the state appears to have been visited

    for dx in dx_vals:
        s_idx = discretize_state(x=float(dx), ret=float(dx), inv=0.0, cap_util=0.0, imb=0.0)
        a_idx = agent.select_action(s_idx, greedy=True)
        actions_chosen.append(float(ACTIONS[a_idx]))

        # Support check: any Q-value in this state row has magnitude > threshold
        q_row = agent.q_table[s_idx]
        is_supported = bool(np.any(np.abs(q_row) > Q_NONDEFAULT_THRESHOLD))
        support_flags.append(is_supported)

    dx_arr = np.array(dx_vals)
    u_arr = np.array(actions_chosen)
    support_arr = np.array(support_flags)

    # R² over all points at this radius
    if np.std(u_arr) > 1e-8:
        corr = float(np.corrcoef(dx_arr, u_arr)[0, 1])
        r_squared_all = float(corr ** 2) if not np.isnan(corr) else 0.0
    else:
        r_squared_all = 0.0

    # OLS slope (∂u/∂x) over all points
    cov = np.cov(dx_arr, u_arr)
    dq_dx_all = float(cov[0, 1] / (cov[0, 0] + 1e-12))

    # R² and slope restricted to supported points only
    n_supported = int(np.sum(support_arr))
    if n_supported >= 3:
        dx_sup = dx_arr[support_arr]
        u_sup = u_arr[support_arr]
        if np.std(u_sup) > 1e-8:
            corr_sup = float(np.corrcoef(dx_sup, u_sup)[0, 1])
            r_squared_supported = float(corr_sup ** 2) if not np.isnan(corr_sup) else 0.0
        else:
            r_squared_supported = 0.0
        cov_sup = np.cov(dx_sup, u_sup)
        dq_dx_supported = float(cov_sup[0, 1] / (cov_sup[0, 0] + 1e-12))
    else:
        r_squared_supported = None
        dq_dx_supported = None

    return {
        "radius": radius,
        "n_points": n_points,
        "n_supported": n_supported,
        "support_fraction": round(n_supported / n_points, 3),
        "r_squared_all": round(r_squared_all, 4),
        "dq_dx_all": round(dq_dx_all, 4),
        "r_squared_supported": round(r_squared_supported, 4) if r_squared_supported is not None else None,
        "dq_dx_supported": round(dq_dx_supported, 4) if dq_dx_supported is not None else None,
        "actions_at_radius": [float(a) for a in actions_chosen],
    }


def main():
    print("=" * 70)
    print("MACHINE MARKETS — MULTISCALE PERTURBATION RADIUS AUDIT")
    print(f"Radii: {RADII}")
    print(f"Points per radius: {N_POINTS}")
    print(f"Support threshold: |Q[s,a]| > {Q_NONDEFAULT_THRESHOLD}")
    print("=" * 70)

    all_policy_results = []

    for p_id in range(1, 11):
        ckpt_path = CHECKPOINT_DIR / f"policy_{p_id:02d}_best.npz"
        if not ckpt_path.exists():
            ckpt_path = CHECKPOINT_DIR / f"policy_{p_id:02d}_final.npz"
        if not ckpt_path.exists():
            print(f"  [skip] No checkpoint for Policy {p_id:02d}")
            continue

        agent = QLearningAgent(seed=p_id)
        agent.load(ckpt_path)

        # Total non-default Q-table entries (overall support)
        n_visited_states = int(np.sum(np.any(np.abs(agent.q_table) > Q_NONDEFAULT_THRESHOLD, axis=1)))
        n_visited_sa_pairs = int(np.sum(np.abs(agent.q_table) > Q_NONDEFAULT_THRESHOLD))

        policy_radii_results = []
        print(f"\n[Policy {p_id:02d}] Visited states: {n_visited_states}/6125 | SA pairs: {n_visited_sa_pairs}/30625")
        print(f"  {'Radius':>8} | {'R²(all)':>9} | {'∂u/∂x(all)':>11} | {'R²(sup)':>9} | {'∂u/∂x(sup)':>11} | {'Supp%':>6}")
        print(f"  {'-'*8}-+-{'-'*9}-+-{'-'*11}-+-{'-'*9}-+-{'-'*11}-+-{'-'*6}")

        for r in RADII:
            res = audit_policy_at_radius(agent, r)
            policy_radii_results.append(res)
            r2_sup_str = f"{res['r_squared_supported']:.4f}" if res['r_squared_supported'] is not None else "  N/A  "
            dq_sup_str = f"{res['dq_dx_supported']:+.4f}" if res['dq_dx_supported'] is not None else "    N/A   "
            print(f"  {r:>8.2f} | {res['r_squared_all']:>9.4f} | {res['dq_dx_all']:>+11.4f} | {r2_sup_str:>9} | {dq_sup_str:>11} | {res['support_fraction']*100:>5.1f}%")

        all_policy_results.append({
            "policy_id": p_id,
            "checkpoint": str(ckpt_path.relative_to(ROOT)),
            "n_visited_states": n_visited_states,
            "n_visited_sa_pairs": n_visited_sa_pairs,
            "radii_results": policy_radii_results,
        })

    # Cross-policy summary per radius
    print("\n" + "=" * 70)
    print("CROSS-POLICY SUMMARY (mean ± std across 10 policies)")
    print(f"  {'Radius':>8} | {'R²_mean':>9} | {'R²_std':>9} | {'∂u/∂x_mean':>11} | {'Supp%_mean':>11}")
    print(f"  {'-'*8}-+-{'-'*9}-+-{'-'*9}-+-{'-'*11}-+-{'-'*11}")

    summary_by_radius = []
    for i, r in enumerate(RADII):
        r2_vals = [p["radii_results"][i]["r_squared_all"] for p in all_policy_results]
        dq_vals = [p["radii_results"][i]["dq_dx_all"] for p in all_policy_results]
        sup_vals = [p["radii_results"][i]["support_fraction"] for p in all_policy_results]
        mean_r2, std_r2 = float(np.mean(r2_vals)), float(np.std(r2_vals))
        mean_dq = float(np.mean(dq_vals))
        mean_sup = float(np.mean(sup_vals))
        print(f"  {r:>8.2f} | {mean_r2:>9.4f} | {std_r2:>9.4f} | {mean_dq:>+11.4f} | {mean_sup*100:>10.1f}%")
        summary_by_radius.append({
            "radius": r,
            "r_squared_mean": round(mean_r2, 4),
            "r_squared_std": round(std_r2, 4),
            "dq_dx_mean": round(mean_dq, 4),
            "support_fraction_mean": round(mean_sup, 3),
            "per_policy_r2": [round(v, 4) for v in r2_vals],
            "per_policy_dq_dx": [round(v, 4) for v in dq_vals],
        })

    output = {
        "meta": {
            "radii": RADII,
            "n_points_per_radius": N_POINTS,
            "support_threshold": Q_NONDEFAULT_THRESHOLD,
            "n_policies": len(all_policy_results),
            "description": (
                "Multiscale perturbation radius audit: R²(r) and ∂u/∂x(r) evaluated "
                "at five nested radii for each trained Q-learning policy. "
                "R²_supported uses only perturbation points in visited state bins."
            ),
        },
        "summary_by_radius": summary_by_radius,
        "policy_results": all_policy_results,
    }

    out_path = RESULTS_DIR / "multiscale_audit_results.json"
    out_path.write_text(json.dumps(output, indent=2))
    print(f"\nResults saved: {out_path.relative_to(ROOT)}")
    print("=" * 70)


if __name__ == "__main__":
    main()
