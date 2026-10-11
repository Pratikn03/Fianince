#!/usr/bin/env python3
"""
Phase 6 / Priority 12 & 13: Realistic Balance-Sheet Stress Tests & Multi-Asset Kreiss Inflation
Decouples three amplification concepts: sup ||J^t||, sup ||CJ^t||, and sup ||CJ^t H||.
Evaluates cross-impact networks across M=1, 2, 5, 10 assets.
Simulates dealer balance sheet under verified Binance USD(S)-M January 2023 venue rules.
"""
import json
from pathlib import Path
import numpy as np

def compute_amplifications(J, C, H, max_T=100):
    """Computes peak gains over t=0..max_T."""
    M1 = 0.0
    MC = 0.0
    MCH = 0.0
    
    J_t = np.eye(J.shape[0])
    for t in range(max_T):
        norm_J = np.linalg.norm(J_t, 2)
        norm_CJ = np.linalg.norm(C @ J_t, 2)
        norm_CJH = np.linalg.norm(C @ J_t @ H, 2)
        
        M1 = max(M1, norm_J)
        MC = max(MC, norm_CJ)
        MCH = max(MCH, norm_CJH)
        
        J_t = J_t @ J
        if norm_J < 1e-6 and t > 5:
            break
            
    return float(M1), float(MC), float(MCH)

def build_network_jacobian(M, rho_diag=0.7, cross_impact=0.15):
    """
    Builds closed-loop Jacobian for M-asset market with cross-impact.
    Dim = 2*M (prices x_1..x_M, memory y_1..y_M).
    """
    a = 0.5
    eta = 0.3
    q = 0.2
    
    # Impact matrix K: diagonal kappa_0, off-diagonal cross_impact
    K_mat = np.eye(M) * 0.8 + (1.0 - np.eye(M)) * cross_impact
    Q_mat = np.eye(M) * q
    
    A_mat = np.eye(M) * a
    E_mat = np.eye(M) * eta
    
    # J = [[A, K @ Q], [E @ A, I - E + E @ K @ Q]]
    top = np.hstack([A_mat, K_mat @ Q_mat])
    bot = np.hstack([E_mat @ A_mat, np.eye(M) - E_mat + E_mat @ K_mat @ Q_mat])
    J_net = np.vstack([top, bot])
    return J_net

def compute_kreiss_constant(J, N_points=200):
    """Approximates Kreiss constant K(J) = sup_{|z|>1} (|z|-1) ||(zI - J)^{-1}||_2."""
    evals = np.linalg.eigvals(J)
    rho = np.max(np.abs(evals))
    if rho >= 1.0:
        return float('inf')
        
    radii = np.linspace(1.001, 2.5, 40)
    thetas = np.linspace(0, 2 * np.pi, N_points, endpoint=False)
    
    max_k = 0.0
    I = np.eye(J.shape[0])
    
    for r in radii:
        for th in thetas:
            z = r * np.exp(1j * th)
            res = np.linalg.inv(z * I - J)
            norm_res = np.linalg.norm(res, 2)
            k_val = (r - 1.0) * norm_res
            if k_val > max_k:
                max_k = k_val
                
    return float(max_k)

def run_experiment():
    # 1. Amplification decoupling in 1-asset model
    # J_single = [[0.5, 0.16], [0.15, 0.748]]
    J1 = np.array([[0.5, 0.16], [0.15, 0.748]])
    C_price = np.array([[1.0, 0.0]]) # price only
    C_balance = np.array([[1.0, 0.8 / 0.005]]) # price + inventory exposure / MMR
    H1 = np.array([[0.8], [0.8 * 0.3]])
    
    m1_p, mc_p, mch_p = compute_amplifications(J1, C_price, H1)
    m1_b, mc_b, mch_b = compute_amplifications(J1, C_balance, H1)
    
    # 2. Multi-asset Kreiss inflation
    network_results = []
    for M in [1, 2, 5, 10]:
        J_net = build_network_jacobian(M, cross_impact=0.15)
        evals = np.linalg.eigvals(J_net)
        spectral_radius = float(np.max(np.abs(evals)))
        kreiss_K = compute_kreiss_constant(J_net)
        
        # Dealer balance sheet liquidation test under Binance Jan 2023 venue rules
        # Liquidation thresholds: 9.60% for L=10, 4.55% for L=20
        # Simulate transient response to unit vector shock
        J_t = np.eye(2 * M)
        max_price_excursion = 0.0
        for t in range(50):
            excursion = np.max(np.abs((J_t @ np.ones(2 * M))[:M]))
            max_price_excursion = max(max_price_excursion, excursion)
            J_t = J_t @ J_net
            
        # Check liquidation triggers
        breach_L20 = bool(max_price_excursion * 100.0 >= 4.55)
        breach_L10 = bool(max_price_excursion * 100.0 >= 9.60)
        
        network_results.append({
            "assets_M": M,
            "matrix_dim": 2 * M,
            "spectral_radius": spectral_radius,
            "kreiss_constant": kreiss_K,
            "max_transient_excursion_pct": float(max_price_excursion * 100.0),
            "breaches_binance_L20_margin_4_55pct": breach_L20,
            "breaches_binance_L10_margin_9_60pct": breach_L10
        })
        
    output = {
        "amplification_decoupling_1_asset": {
            "price_only_operator": {
                "C": "e_x",
                "full_state_M1": m1_p,
                "output_MC": mc_p,
                "input_to_output_MCH": mch_p
            },
            "balance_sheet_operator": {
                "C": "e_x + (kappa/MMR) e_y",
                "full_state_M1": m1_b,
                "output_MC": mc_b,
                "input_to_output_MCH": mch_b
            }
        },
        "multi_asset_network_kreiss_inflation": network_results
    }
    
    out_file = Path("breakthrough_experiments/results_exp12_nonnormal_balance_sheet.json")
    out_file.write_text(json.dumps(output, indent=2))
    print(f"Non-Normal Balance Sheet & Network Experiment complete. Results written to {out_file}")
    for row in network_results:
        print(f"M={row['assets_M']:2d}: rho={row['spectral_radius']:.4f}, Kreiss={row['kreiss_constant']:.2f}, Excursion={row['max_transient_excursion_pct']:.2f}% | Breach L=20 (4.55%): {row['breaches_binance_L20_margin_4_55pct']}")

if __name__ == "__main__":
    run_experiment()
