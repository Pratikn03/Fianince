#!/usr/bin/env python3
"""
Institutional Dollar Calibration & Break-Even Spacing for Supplement S12 & Prop S27.3.
Verifies the dollar translation of the normalized supervisory loss model (4,608 grid).
"""

import json
import math
from pathlib import Path

def compute_dollar_calibration():
    # Normalized primitives from Supplement Section S12 (p. S-53)
    L_T_norm = 1.449219        # No-data uniform throttle loss (surplus units)
    L_tag_norm = 1.305132      # Disclosure loss inclusive of F + N*c at N=32
    bill_tag_norm = 0.066000   # F + N*c = 0.05 + 32 * 0.0005
    F_norm = 0.05
    c_norm = 0.0005
    N_tag = 32
    N_lecam_010 = 5927.6       # Table S1 Le Cam 95% resets at Delta_eta = 0.10, K=2

    # Physical dollar anchor: 1 normalized unit (H * b) = $1,250,000
    # (b = $250,000/day per active class * H = 5 trading days)
    unit_usd = 1_250_000.0
    L_T_usd = L_T_norm * unit_usd
    L_tag_usd = L_tag_norm * unit_usd
    net_gain_usd = L_T_usd - L_tag_usd
    F_usd = F_norm * unit_usd
    c_usd = c_norm * unit_usd
    gross_benefit_usd = (L_T_norm - (L_tag_norm - bill_tag_norm)) * unit_usd

    # Price-only cost at Delta_eta = 0.10
    cost_price_010_usd = F_usd + N_lecam_010 * c_usd

    # Break-even upper spacing \overline{\Delta\eta} where price-only variable cost = gross_benefit
    delta_eta_upper = 0.10 * ((N_lecam_010 * c_usd) / gross_benefit_usd) ** (1.0 / 6.0)

    # Break-even lower spacing \underline{\Delta\eta} for rate-scaled tagged cost ~ (Delta_eta)^(-2)
    delta_eta_lower = 0.10 * ((N_tag * c_usd) / (gross_benefit_usd - F_usd)) ** (1.0 / 2.0)

    # Minimum number of markets M_min to amortize a $200M/yr CAT budget across 8 episodes/yr
    cat_annual_budget_usd = 200_000_000.0
    episodes_per_year = 8
    net_variable_saving_per_ep = gross_benefit_usd - (N_tag * c_usd)
    M_min = math.ceil(cat_annual_budget_usd / (episodes_per_year * net_variable_saving_per_ep))

    results = {
        "unit_surplus_Hb_usd": round(unit_usd, 2),
        "uniform_throttle_loss_usd": round(L_T_usd, 2),
        "tagged_disclosure_total_loss_usd": round(L_tag_usd, 2),
        "net_disclosure_advantage_per_episode_usd": round(net_gain_usd, 2),
        "gross_action_benefit_usd": round(gross_benefit_usd, 2),
        "price_only_cost_at_010_usd": round(cost_price_010_usd, 2),
        "breakeven_delta_eta_lower": round(delta_eta_lower, 4),
        "breakeven_delta_eta_upper": round(delta_eta_upper, 4),
        "min_markets_to_amortize_CAT": M_min,
        "calibration_basis": {
            "CAT_budget_annual_usd": cat_annual_budget_usd,
            "episodes_per_year": episodes_per_year,
            "daily_surplus_b_usd": 250_000.0,
            "holding_horizon_days": 5,
            "K_classes": 2,
            "LeCam_constant_010": N_lecam_010
        }
    }
    
    out_path = Path(__file__).resolve().parent / "dollar_calibration_results.json"
    with open(out_path, "w") as f:
        json.dump(results, f, indent=2)
    print(f"Results written to {out_path}")
    print(json.dumps(results, indent=2))
    return results

if __name__ == "__main__":
    compute_dollar_calibration()
