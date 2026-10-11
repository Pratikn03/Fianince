#!/usr/bin/env python3
"""
Phase 4 / Priority 7: Quantitative Value of Financial Disclosure
Quantifies how financial disclosures (I0 to I5) substitute for costly active probing.
Calculates required volume V and capital B to achieve error alpha under each contract.
"""
import json
from pathlib import Path
import numpy as np
from scipy.stats import norm

def evaluate_disclosure_contracts():
    alpha = 0.05
    z_alpha = norm.ppf(1.0 - alpha) # 1.645
    
    kappa = 0.8
    q = 0.2
    mu = 0.005 # MMR
    c_fee = 0.0004
    P_star = 100.0
    
    # Separation levels
    deltas = [0.03, 0.05, 0.08, 0.12]
    
    contracts = {
        "I0_Prices_Only": {
            "desc": "Public noisy prices only (sigma_p = 0.02)",
            "sigma_eff": 0.02,
            "scaling_V": lambda d: (2.0 * 0.02 * z_alpha) / (kappa**2 * q * (d**2)),
            "disclosure_type": "None"
        },
        "I1_Prices_and_Flow": {
            "desc": "Prices plus recorded executed order flow (sigma_eff = 0.01)",
            "sigma_eff": 0.01,
            "scaling_V": lambda d: (2.0 * 0.01 * z_alpha) / (kappa**2 * q * (d**2)),
            "disclosure_type": "Public Aggregates"
        },
        "I2_Noisy_Equity": {
            "desc": "Prices plus noisy dealer marked equity (sigma_E = 0.5)",
            "sigma_eff": 0.005,
            # Equity difference: Delta E = V^2 * kappa^2 * q * delta^2
            # Direct measurement gives V ~ delta^{-1}
            "scaling_V": lambda d: np.sqrt((2.0 * 0.5 * z_alpha) / (kappa**2 * q * (d**2))),
            "disclosure_type": "Financial Reporting"
        },
        "I3_Exact_Equity": {
            "desc": "Prices plus exact marked equity disclosure (Proposition 2.8)",
            "sigma_eff": 0.0001,
            # Proposition 2.8: exact two-step identification with fixed small V
            "scaling_V": lambda d: 1.0, # fixed minimal probe suffices
            "disclosure_type": "Exact Account Disclosure"
        },
        "I4_Update_Timestamps": {
            "desc": "Verified algorithmic policy update timestamps (event study)",
            "sigma_eff": 0.002,
            "scaling_V": lambda d: 0.5 / d,
            "disclosure_type": "Audit Trail"
        },
        "I5_Full_Audit_Trail": {
            "desc": "Complete authenticated regulatory audit registry (no probing needed)",
            "sigma_eff": 0.0,
            "scaling_V": lambda d: 0.0,
            "disclosure_type": "Supervisory Tagging"
        }
    }
    
    results = []
    for delta in deltas:
        delta_res = {"delta": delta, "contracts": {}}
        for c_key, c_info in contracts.items():
            req_V = float(c_info["scaling_V"](delta))
            # Required capital B = (mu + 0.5) * kappa * V^2 + (c_fee + mu * P_star) * V
            if req_V > 0:
                req_B = float((mu + 0.5) * kappa * (req_V**2) + (c_fee + mu * P_star) * req_V)
            else:
                req_B = 0.0
                
            delta_res["contracts"][c_key] = {
                "required_volume_V": req_V,
                "required_capital_B": req_B,
                "disclosure_type": c_info["disclosure_type"]
            }
        results.append(delta_res)
        
    out_file = Path("breakthrough_experiments/results_exp7_disclosure_value.json")
    out_file.write_text(json.dumps(results, indent=2))
    print(f"Disclosure Value Experiment complete. Results written to {out_file}")
    
    # Print comparison at delta = 0.05
    d5 = [r for r in results if r["delta"] == 0.05][0]["contracts"]
    print(f"\n--- Value of Disclosure at delta = 0.05 ---")
    for k, v in d5.items():
        print(f"[{k:22s}] Volume V = {v['required_volume_V']:8.2f} | Capital B = {v['required_capital_B']:12.2f} USDT")

if __name__ == "__main__":
    evaluate_disclosure_contracts()
