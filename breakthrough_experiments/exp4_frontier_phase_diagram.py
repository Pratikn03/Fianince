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
    
    # Session limit on number of pulses (e.g. max 5,000 execution cycles in a surveillance window)
    N_max_session = 5000
    
    for j, delta in enumerate(deltas):
        # 1. Single-pulse required volume (based on 3rd observation mean difference kappa^2 * q * delta^2):
        # Under H0 vs H1, d_2 = -kappa^2 * q * delta^2.
        # Single-pulse KL = A^2 * d_2^2 / (2 * sigma^2) >= 2 * z_alpha^2
        diff_obs3 = kappa**2 * q * (delta**2)
        A_req = (2.0 * sigma * z_alpha) / diff_obs3
        
        # Single-pulse capital (if feasible within effective depth V_eff):
        B_req_pulse = 0.5 * kappa * (A_req**2) + (c_fee + mu) * P_star * A_req
        
        # 2. Sequential bounded probing (if A_req > V_eff):
        # When each pulse is bounded by |v_t| <= V_eff = min(V_max, D_max / kappa) = 6.25,
        # each independent pulse cycle provides Fisher information / KL divergence:
        # KL_pulse = (V_eff^2 * d_2^2) / (2 * sigma^2).
        # To accumulate target KL >= 2 * z_alpha^2, the required number of pulses is:
        # N_pulses = ceil( (2 * z_alpha^2) / KL_pulse ) = ceil( (A_req / V_eff)^2 ) ~ Theta(delta^-4).
        kl_per_pulse = (V_eff**2 * (diff_obs3**2)) / (2.0 * sigma**2)
        target_kl = 2.0 * (z_alpha**2)
        N_pulses = int(max(1, np.ceil(target_kl / kl_per_pulse)))
        v_sub = V_eff if N_pulses > 1 else min(A_req, V_eff)
        
        # Peak inventory on each pulse cycle is v_sub <= V_eff <= I_max
        inv_peak = v_sub
        
        # Cumulative capital cost of sequential probing:
        # Each pulse pays impact (0.5 * kappa * v_sub^2) + taker fees (c_fee * P_star * v_sub).
        # Total capital scales strictly as Theta(delta^-4):
        cost_per_pulse = 0.5 * kappa * (v_sub**2) + c_fee * P_star * v_sub
        B_req_seq = float(N_pulses * cost_per_pulse + mu * P_star * inv_peak)
        
        for i, B in enumerate(B_grid):
            if delta >= delta_min and B >= B_req_pulse and A_req <= V_eff:
                # Regime 1: Feasible Single-Pulse Probing (Theta(1) horizon, Theta(delta^-4) capital)
                regime = 1
            elif B >= B_req_seq and N_pulses <= N_max_session and inv_peak <= I_max:
                # Regime 2: Sequential Multi-Pulse Probing (Theta(delta^-4) horizon, Theta(delta^-4) capital)
                regime = 2
            else:
                # Regime 3: Infeasible (B < B_req_seq or session horizon N_pulses > N_max_session)
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
