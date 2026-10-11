#!/usr/bin/env python3
"""
Phase 3 / Priority 4 & 5: The Financial Identification Frontier & Phase Diagram
Solves the joint program: min B subject to error <= alpha, insolvency <= epsilon,
quantity <= V_max, inventory <= I_max, price displacement <= D_max.
Maps the Tri-Region Phase Diagram: Feasible (Regime 1), Costly Sequential (Regime 2), Infeasible (Regime 3).

Enforces:
- Depth cap: |v_t| <= V_max
- Displacement cap: kappa * |v_t| <= D_max  ==>  |v_t| <= min(V_max, D_max / kappa) = V_eff
- Inventory cap: |I_t| <= I_max
- Solvency capital: B >= C(N, v)
"""
import json
from pathlib import Path
import numpy as np
from scipy.stats import norm

def compute_frontier():
    # Market & Regulatory parameters
    sigma = 0.01          # observation noise
    alpha = 0.05          # max 5% error guarantee
    kappa = 0.8           # price impact
    q = 0.2               # feedback weight
    mu = 0.005           # Binance maintenance margin rate (0.50%)
    c_fee = 0.0004        # Binance taker fee (4 bps)
    P_star = 100.0        # reference price
    V_max = 50.0          # maximum exchange available depth in one pulse
    I_max = 200.0         # regulatory inventory cap
    D_max = 5.0           # max price displacement: kappa * V <= D_max
    
    # Effective single-trade limit from joint depth and displacement bounds:
    # kappa * |v| <= D_max  -->  |v| <= D_max / kappa = 5.0 / 0.8 = 6.25
    V_eff = min(V_max, D_max / kappa) # = 6.25
    
    z_alpha = norm.ppf(1.0 - alpha) # ~1.645
    
    # 1. Physical single-pulse resolution floor delta_min
    # A_req(delta) = (2 * sigma * z_alpha) / (kappa^2 * q * delta^2) <= V_eff
    delta_min = float(np.sqrt((2.0 * sigma * z_alpha) / (kappa**2 * q * V_eff))) # ~0.2028
    
    # Grid of delta and Capital B
    deltas = np.linspace(0.01, 0.25, 100)
    log_B = np.linspace(1.0, 6.0, 100) # B from 10 to 1,000,000
    B_grid = 10.0 ** log_B
    
    phase_matrix = np.zeros((len(log_B), len(deltas)), dtype=int)
    delta_results = []
    
    for j, delta in enumerate(deltas):
        # Required single-pulse volume to achieve alpha under H0 vs H1
        A_req = (2.0 * sigma * z_alpha) / (kappa**2 * q * (delta**2))
        
        # Required capital for single pulse (if feasible)
        B_req_pulse = 0.5 * kappa * (A_req**2) + (c_fee + mu) * P_star * A_req
        
        # Sequential multi-step probing requirement if A_req > V_eff:
        # Probe is partitioned into N_pulses of size at most V_eff
        N_pulses = max(1.0, np.ceil(A_req / V_eff))
        v_sub = A_req / N_pulses # size per pulse <= V_eff
        
        # Round-trip probing ensures inventory returns to zero between pulses:
        # Peak inventory on each pulse is v_sub <= V_eff <= I_max
        inv_peak = v_sub
        
        # Capital cost of sequential probing: cumulative impact + transaction fees + margin lockup
        B_req_seq = N_pulses * (0.5 * kappa * (v_sub**2) + c_fee * P_star * v_sub) + mu * P_star * inv_peak
        
        for i, B in enumerate(B_grid):
            if delta >= delta_min and B >= B_req_pulse and A_req <= V_eff:
                # Regime 1: Feasible Single-Pulse Probing
                regime = 1
            elif B >= B_req_seq and inv_peak <= I_max and v_sub <= V_eff:
                # Regime 2: Feasible Sequential / Multi-Pulse Probing
                regime = 2
            else:
                # Regime 3: Infeasible (insufficient capital B < B_req_seq or exceeds limits)
                regime = 3
                
            phase_matrix[i, j] = regime
            
        delta_results.append({
            "delta": float(delta),
            "A_req": float(A_req),
            "B_req_pulse": float(B_req_pulse),
            "B_req_sequential": float(B_req_seq),
            "N_pulses": int(N_pulses),
            "is_below_single_pulse_floor": bool(delta < delta_min)
        })
        
    summary = {
        "parameters": {
            "sigma": sigma,
            "alpha": alpha,
            "kappa": kappa,
            "q": q,
            "mu": mu,
            "V_max": V_max,
            "D_max": D_max,
            "V_eff": float(V_eff),
            "I_max": I_max,
            "delta_min": float(delta_min)
        },
        "phase_counts": {
            "feasible_count": int(np.sum(phase_matrix == 1)),
            "costly_count": int(np.sum(phase_matrix == 2)),
            "infeasible_count": int(np.sum(phase_matrix == 3))
        },
        "delta_curve": delta_results
    }
    
    out_file = Path("breakthrough_experiments/results_exp4_phase_diagram.json")
    out_file.write_text(json.dumps(summary, indent=2))
    print(f"Frontier Phase Diagram computed. V_eff = {V_eff:.2f}, delta_min = {delta_min:.4f}. Results written to {out_file}")
    print(f"Regime distribution: Feasible={summary['phase_counts']['feasible_count']}, Costly={summary['phase_counts']['costly_count']}, Infeasible={summary['phase_counts']['infeasible_count']}")

if __name__ == "__main__":
    compute_frontier()
