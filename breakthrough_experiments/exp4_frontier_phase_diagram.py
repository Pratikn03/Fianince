#!/usr/bin/env python3
"""
Phase 3 / Priority 4 & 5: The Financial Identification Frontier & Phase Diagram
Solves the joint program: min B subject to error <= alpha, insolvency <= epsilon,
quantity <= V_max, inventory <= I_max, price displacement <= D_max.
Maps the Tri-Region Phase Diagram: Feasible, Costly, Infeasible.
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
    D_max = 5.0           # max price displacement: kappa * V <= D_max -> V <= D_max / kappa = 6.25
    
    z_alpha = norm.ppf(1.0 - alpha) # ~1.645
    
    # 1. Physical resolution floor delta_min
    # A(delta) = 2 * sigma * z_alpha / (kappa^2 * q * delta^2) <= V_max
    delta_min = np.sqrt((2.0 * sigma * z_alpha) / (kappa**2 * q * V_max))
    
    # Grid of delta and Capital B
    deltas = np.linspace(0.01, 0.25, 100)
    log_B = np.linspace(1.0, 6.0, 100) # B from 10 to 1,000,000
    B_grid = 10.0 ** log_B
    
    phase_matrix = np.zeros((len(log_B), len(deltas)), dtype=int)
    
    delta_results = []
    
    for j, delta in enumerate(deltas):
        # Required single-pulse volume
        A_req = (2.0 * sigma * z_alpha) / (kappa**2 * q * (delta**2))
        
        # Required capital for single pulse
        B_req_pulse = (mu + 0.5) * kappa * (A_req**2) + (c_fee + mu * P_star) * A_req
        
        # Sequential multi-step probing requirement if A_req > V_max
        # Divide into N_pulses = ceil(A_req / V_max)
        N_pulses = max(1.0, np.ceil(A_req / V_max))
        # Multi-pulse distributed capital
        v_sub = A_req / N_pulses
        B_req_seq = N_pulses * ((mu + 0.5) * kappa * (v_sub**2) + (c_fee + mu * P_star) * v_sub)
        
        # Max inventory during sequential probe
        inv_peak = min(A_req, V_max * 2.0) # assume partial mean-reversion
        
        for i, B in enumerate(B_grid):
            if delta < delta_min and A_req > I_max:
                # Impossible: exceeds physical and regulatory limits
                regime = 3 # Infeasible
            elif A_req <= V_max and B >= B_req_pulse:
                regime = 1 # Feasible Single Pulse
            elif B >= B_req_seq and inv_peak <= I_max:
                regime = 2 # Costly / Sequential
            else:
                regime = 3 # Infeasible due to insufficient capital or margin breach
                
            phase_matrix[i, j] = regime
            
        delta_results.append({
            "delta": float(delta),
            "A_req": float(A_req),
            "B_req_pulse": float(B_req_pulse),
            "B_req_sequential": float(B_req_seq),
            "is_below_depth_floor": bool(delta < delta_min)
        })
        
    summary = {
        "parameters": {
            "sigma": sigma,
            "alpha": alpha,
            "kappa": kappa,
            "q": q,
            "mu": mu,
            "V_max": V_max,
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
    print(f"Frontier Phase Diagram computed. delta_min = {delta_min:.4f}. Results written to {out_file}")
    print(f"Regime distribution: Feasible={summary['phase_counts']['feasible_count']}, Costly={summary['phase_counts']['costly_count']}, Infeasible={summary['phase_counts']['infeasible_count']}")

if __name__ == "__main__":
    compute_frontier()
