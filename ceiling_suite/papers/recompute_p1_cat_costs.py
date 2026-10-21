"""Paper 1, Section 8.2 (and Paper 2, Section 9):
Disclosure in dollars — Probing capital avoided by class-tagged disclosure against
official SEC Consolidated Audit Trail (CAT) build and annual operating cost estimates.

Sources for official CAT cost figures:
  1. SEC Rule 613 Adopting Release, Release No. 34-67457 (July 18, 2012):
     Initial aggregate build cost estimated at $4.0B; ongoing annual cost at $2.1B/yr.
  2. CAT NMS Plan Approval Order, Release No. 34-79318 (November 15, 2016):
     Revised aggregate industry build cost $2.4B; industry annual reporting cost $1.7B/yr;
     central processor annual operating bid estimate $55.8M/yr.
  3. CAT LLC 2024-2025 Budgets & SEC Release No. 34-102386 (February 10, 2025,
     Exemptive Relief from Certain CAT Reporting Requirements) and related CAT funding orders:
     Cumulative central-repository (CAT LLC) build/historical cost ~$518M;
     central-repository annual operating budget $248M (2024) to $272M (2025).

Calibration to BTCUSDT dollars (matching Paper 1 Section 5.2 and Table 6, P1.3-T1_sigma_obs.json):
  - At the median Roll observation-noise estimate (sigma_hat = 0.4019 USDT):
    C(sigma, delta) = 61.41 * (sigma / 0.01)^2 * (0.05 / delta)^4
    giving $6,200 (delta = 0.10), $99,193 (delta = 0.05), and $3,874,696 (delta = 0.02) for K = 2.
  - For K unknown cohorts with rate spacing Delta_eta (where K=2 known-pair half-spacing delta corresponds
    to spacing Delta_eta), Theorem 6.4/6.5 and Theorem 8.2 show that price-only identification requires
    N_p ~ (Delta_eta)^{-(4K-2)} experiments while class-tagged flow requires N_t ~ (Delta_eta)^{-2}
    (a sample-size saving factor of (Delta_eta)^{-(4K-4)}). Relative to K = 2, each additional unknown
    cohort multiplies the required experiment count (and hence cumulative probing capital) by the Cauchy-Hankel
    conditioning factor c_step * (Delta_eta)^{-4}, with c_step = 0.25 from the Cauchy determinant ratio.

Outputs:
  - ceiling_suite/papers/recomputed/R_P1_cat_disclosure_dollars.json
"""
from __future__ import annotations

import json
import os

HERE = os.path.dirname(os.path.abspath(__file__))

CAT_COSTS = {
    "rule_613_2012_release_34_67457": {
        "industry_build_usd": 4.0e9,
        "industry_annual_usd": 2.1e9,
    },
    "nms_plan_2016_release_34_79318": {
        "industry_build_usd": 2.4e9,
        "industry_annual_usd": 1.7e9,
        "central_processor_annual_est_usd": 55.8e6,
    },
    "cat_llc_2024_2025_and_release_34_102386": {
        "central_repo_build_usd": 518.0e6,
        "central_repo_annual_2024_usd": 248.0e6,
        "central_repo_annual_2025_usd": 272.0e6,
    },
}


def main():
    # Exact Table 6 (P1.3-T1_sigma_obs.json) K=2 baseline under Roll median noise (0.4019 USDT)
    # and 1-sec price-change s.d. (1.9762 USDT)
    k2_roll = {0.10: 6199.5136, 0.05: 99192.2176, 0.02: 3874696.0}
    k2_sd1s = {0.10: 149901.3888, 0.05: 2398422.22, 0.02: 93688368.0}
    c_step = 0.25

    table_rows = []
    for K in [2, 3, 4]:
        for d in [0.10, 0.05, 0.02]:
            mult_K = (c_step * (d ** -4)) ** (K - 2)
            cap_roll = k2_roll[d] * mult_K
            cap_sd1s = k2_sd1s[d] * mult_K
            be_cat_248m = 248.0e6 / cap_roll
            be_cat_272m = 272.0e6 / cap_roll
            be_ind_1700m = 1.7e9 / cap_roll
            row = {
                "K": K,
                "delta": d,
                "price_only_rate_exponent": 4 * K - 2,
                "disclosure_saving_exponent": 4 * K - 4,
                "probing_capital_roll_usd": round(cap_roll, 2),
                "probing_capital_sd1s_usd": round(cap_sd1s, 2),
                "breakeven_markets_cat_248M": round(be_cat_248m, 3),
                "breakeven_markets_cat_272M": round(be_cat_272m, 3),
                "breakeven_markets_industry_1700M": round(be_ind_1700m, 3),
            }
            table_rows.append(row)
            print(
                f"K={K}, delta={d:.2f} | Roll cap/mkt: ${cap_roll:,.0f} | "
                f"Break-even mkts vs $248M CAT LLC: {be_cat_248m:,.2f} | vs $1.7B industry: {be_ind_1700m:,.2f}"
            )

    p2_companion = {
        "alpha_proxy_eta002": 0.262,
        "alpha_audit_eta002": 0.678,
        "capacity_gain_pp": 41.6,
        "annual_value_per_1M_desk_usd": round(0.416 * 365.0 * 4e-4 * 1e6, 0),
        "annual_value_per_1B_market_notional_usd": round(0.416 * 365.0 * 4e-4 * 1e9, 0),
        "breakeven_active_notional_vs_248M_cat_usd": round(248.0e6 / (0.416 * 365.0 * 4e-4), 0),
    }

    out = {
        "cat_official_costs": CAT_COSTS,
        "rows": table_rows,
        "paper2_companion_audit_value": p2_companion,
    }
    out_path = os.path.join(HERE, "recomputed", "R_P1_cat_disclosure_dollars.json")
    with open(out_path, "w") as f:
        json.dump(out, f, indent=2)
    print("Wrote", out_path)


if __name__ == "__main__":
    main()
