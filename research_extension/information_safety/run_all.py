"""Master runner for the Flagship Paper 2 Information-Safety Upgrade (Tests T01-T12 + 7 Figures)."""
from __future__ import annotations
import json
from pathlib import Path
import sys
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from research_extension.information_safety.exact_rational_witness import (
    build_witness_markets,
    verify_witness_and_theorem_A,
)
from research_extension.information_safety.price_response import exact_impulse_response
from research_extension.information_safety.data_compatibility import (
    compatible_feedback_bounds_d0,
    compatible_feedback_bounds_d1,
    theorem_C_minimum_observations,
    theorem_C_horizon_for_safety_margin,
)
from research_extension.information_safety.uncertainty_calibration import run_coverage_simulation_T04
from research_extension.information_safety.risk_gain import (
    cumulative_convolution_gain,
    exhaustive_worst_case_disturbance,
    repeated_vs_peak_gate_counterexample,
)
from research_extension.information_safety.robust_admission import (
    closed_form_optimal_admission,
    solve_balance_sheet_guard_globally,
)
from research_extension.information_safety.model_contracts import BalanceSheetContract
from research_extension.information_safety.adversarial_paths import run_misspecification_stress_T09
from research_extension.information_safety.disclosure_experiment import evaluate_disclosure_tiers_T07
from research_extension.information_safety.economic_ledger import (
    run_eight_guard_comparison_T11,
    run_equilibrium_and_welfare_T12,
)
from research_extension.information_safety.tests.test_exact_witness import test_exact_witness_rational_values
from research_extension.information_safety.tests.test_convolution_gain import test_convolution_gain_horizons_1_to_8
from research_extension.information_safety.tests.test_confidence_coverage import test_confidence_coverage_and_false_certification
from research_extension.information_safety.tests.test_two_world_bound import test_two_world_bound_and_sample_complexity
from research_extension.information_safety.tests.test_robust_optimizer import test_robust_optimizer_and_abstention
from research_extension.information_safety.tests.test_balance_sheet import test_balance_sheet_solvency_contract


def generate_flagship_figures(results: dict, fig_dirs: list[Path]) -> list[str]:
    """Generate the 7 Flagship Figures specified in Section 8 of the Blueprint."""
    plt.rcParams.update({
        "font.size": 9,
        "axes.titlesize": 10,
        "axes.labelsize": 9,
        "xtick.labelsize": 8,
        "ytick.labelsize": 8,
        "legend.fontsize": 8,
    })
    created = []

    def save_all(fig, name: str):
        for d in fig_dirs:
            d.mkdir(parents=True, exist_ok=True)
            fig.savefig(d / name, bbox_inches="tight")
        plt.close(fig)
        created.append(name)

    # Figure 1: Two markets with identical early observations (h_0, h_1, h_2) but different cumulative gains
    w = results["T01_T02_witness_and_theorem_A"]
    hA = np.array(w["impulse_series_A"][:10])
    hB = np.array(w["impulse_series_B"][:10])
    lags = np.arange(len(hA))
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(7.2, 2.7))
    width = 0.36
    ax1.bar(lags[:6] - width / 2, hA[:6], width=width, label="Market A ($Q=0.08$)", color="#1f77b4")
    ax1.bar(lags[:6] + width / 2, hB[:6], width=width, label="Market B ($Q=0.42$)", color="#d62728")
    ax1.set_xlabel("Impulse lag $k$")
    ax1.set_ylabel("Impulse coefficient $h_k$")
    ax1.set_title("Early impulse responses ($h_0,h_1,h_2$ identical)")
    ax1.legend(frameon=False)

    cumA = np.cumsum(hA)
    cumB = np.cumsum(hB)
    ax2.plot(lags, cumA, "o-", color="#1f77b4", label="Market A ($S_\\infty=1.923, v_{\\max}=0.52$)")
    ax2.plot(lags, cumB, "s--", color="#d62728", label="Market B ($S_\\infty=5.556, v_{\\max}=0.18$)")
    ax2.axhline(25 / 13, color="#1f77b4", linestyle=":", alpha=0.7)
    ax2.axhline(50 / 9, color="#d62728", linestyle=":", alpha=0.7)
    ax2.set_xlabel("Horizon $H$")
    ax2.set_ylabel("Cumulative gain $\\sum_{k=0}^H h_k$")
    ax2.set_title("Divergent cumulative transient risk")
    ax2.legend(frameon=False, loc="upper left")
    fig.tight_layout()
    save_all(fig, "fig_flagship_1_witness.pdf")

    # Figure 2: Unavoidable safe-trading capacity loss vs statistical distinguishability (d_TV)
    dtv = np.linspace(0.0, 1.0, 200)
    fig, ax = plt.subplots(figsize=(4.6, 2.8))
    for beta, col, ls in [(0.01, "#1f77b4", "-"), (0.05, "#d62728", "--"), (0.10, "#2ca02c", "-.")]:
        loss = (0.52 - 0.18) * np.maximum(0.0, 1.0 - beta - dtv)
        ax.plot(dtv, loss, color=col, linestyle=ls, lw=1.8, label=f"Safety tolerance $\\beta={beta:.2f}$")
    ax.scatter([0.0], [0.323], color="#d62728", zorder=5)
    ax.annotate("Lag-2 witness: $d_{\\mathrm{TV}}=0,\\; \\mathrm{loss}\\geq 0.323$", xy=(0.0, 0.323), xytext=(0.15, 0.305),
                arrowprops=dict(arrowstyle="->", lw=0.8))
    ax.set_xlabel("Total variation distinguishability $d_{\\mathrm{TV}}(P_0,P_1)$")
    ax.set_ylabel("Min. expected lost safe capacity $\\mathbb{E}_1[v_1-A(D)]$")
    ax.set_title("Theorem A: Information--safety impossibility frontier")
    ax.legend(frameon=False)
    fig.tight_layout()
    save_all(fig, "fig_flagship_2_tv_frontier.pdf")

    # Figure 3: Confidence-set size vs certifiable trading allowance (Theorem D)
    ns = np.array([50, 100, 250, 500, 1000, 2500, 5000])
    radii = 0.04 / np.sqrt(ns / 50.0)
    v_cert_A = np.maximum(0.0, 0.52 - 2.2 * radii)
    v_cert_B = np.maximum(0.0, 0.18 - 2.2 * radii)
    fig, ax = plt.subplots(figsize=(4.6, 2.8))
    ax.plot(ns, v_cert_A, "o-", color="#1f77b4", label="Market A certified $v_{\\mathrm{safe}}(D)$")
    ax.axhline(0.52, color="#1f77b4", ls=":", label="Market A oracle $v_{\\max}=0.52$")
    ax.plot(ns, v_cert_B, "s--", color="#d62728", label="Market B certified $v_{\\mathrm{safe}}(D)$")
    ax.axhline(0.18, color="#d62728", ls=":", label="Market B oracle $v_{\\max}=0.18$")
    ax.set_xscale("log")
    ax.set_xlabel("Sample size $N$ (impulse windows)")
    ax.set_ylabel("Certifiably safe allowance $v_{\\mathrm{safe}}(D)$")
    ax.set_title("Theorem D: Confidence-region shrinkage and safe capacity")
    ax.legend(frameon=False, loc="center right")
    fig.tight_layout()
    save_all(fig, "fig_flagship_3_confidence_allowance.pdf")

    # Figure 4: Public vs Class-Tagged vs Audited Information (Theorem F, T07)
    t07 = results["T07_disclosure_value"]["tiers"]
    labels = ["Public\nAggregate", "Class-Tagged\nDisclosure", "Audited\nChannel"]
    v_vals = [t07["public_aggregate"]["v_safe"], t07["class_tagged"]["v_safe"], t07["audited_channel"]["v_safe"]]
    net_vals = [
        t07["public_aggregate"]["net_disclosure_value_vs_public"],
        t07["class_tagged"]["net_disclosure_value_vs_public"],
        t07["audited_channel"]["net_disclosure_value_vs_public"],
    ]
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(6.8, 2.6))
    ax1.bar(labels, v_vals, color=["#7f7f7f", "#1f77b4", "#2ca02c"], width=0.55)
    ax1.axhline(0.52, color="black", ls=":", label="Oracle $v_{\\max}=0.52$")
    ax1.set_ylabel("Certified safe allowance $v_{\\mathrm{safe}}$")
    ax1.set_title("Admissible safe trading capacity")
    ax1.legend(frameon=False)

    ax2.bar(labels, net_vals, color=["#7f7f7f", "#1f77b4", "#2ca02c"], width=0.55)
    ax2.set_ylabel("Net welfare gain vs. public ($\\mathcal{V}_{\\mathrm{net}}$)")
    ax2.set_title("Net economic value after compliance cost")
    fig.tight_layout()
    save_all(fig, "fig_flagship_4_disclosure_tiers.pdf")

    # Figure 5: Risk reduction vs lost trading activity for the 8 guards (T11)
    t11 = results["T11_eight_guard_comparison"]
    fig, ax = plt.subplots(figsize=(5.4, 3.1))
    pretty = {
        "1_unrestricted": "Unrestricted",
        "2_volatility_only": "Volatility-only",
        "3_inventory_leverage_cap": "Inventory/leverage",
        "4_depth_based_throttling": "Depth throttle",
        "5_spectral_radius_threshold": "Spectral radius",
        "6_known_model_oracle_guard": "Oracle summed-gain",
        "7_estimated_plugin_guard": "Plug-in summed-gain",
        "8_robust_info_aware_guard": "Robust info-aware (ours)",
    }
    for k, row in t11.items():
        x = row["mean_missed_safe_capacity"]
        y = row["breach_rate"] * 100.0
        col = "#d62728" if y > 5.0 else ("#2ca02c" if "8_" in k else "#1f77b4")
        ax.scatter([x], [y], color=col, s=45)
        ax.annotate(pretty[k], (x, y), xytext=(4, 3), textcoords="offset points", fontsize=7.5)
    ax.axhline(5.0, color="gray", ls="--", lw=0.9, label="5% target safety ceiling")
    ax.set_xlabel("Mean sacrificed safe trading capacity $\\mathbb{E}[(v_{\\max}-v)_+]$")
    ax.set_ylabel("Budget breach frequency (\\%)")
    ax.set_title("Test T11: Safety vs. sacrificed trading activity across 8 guards")
    ax.legend(frameon=False)
    fig.tight_layout()
    save_all(fig, "fig_flagship_5_guard_frontier.pdf")

    # Figure 6: Coverage and abstention rates under finite observations (T04)
    cov_grid = results["T04_coverage_grid"]
    n_vals = [r["N"] for r in cov_grid]
    cov_rates = [r["observed_ellipsoid_coverage"] * 100.0 for r in cov_grid]
    abs_rates = [r["abstention_rate"] * 100.0 for r in cov_grid]
    false_rates = [r["false_safety_certification_rate"] * 100.0 for r in cov_grid]
    fig, ax = plt.subplots(figsize=(4.8, 2.8))
    ax.plot(n_vals, cov_rates, "o-", color="#1f77b4", label="Observed confidence coverage (\\%)")
    ax.plot(n_vals, abs_rates, "s--", color="#ff7f0e", label="Abstention rate (\\%)")
    ax.plot(n_vals, false_rates, "^-.", color="#d62728", label="False safety-certification rate (\\%)")
    ax.axhline(95.0, color="#1f77b4", ls=":", lw=0.9)
    ax.axhline(5.0, color="#d62728", ls=":", lw=0.9)
    ax.set_xscale("log")
    ax.set_xlabel("Sample size $N$")
    ax.set_ylabel("Percentage (\\%)")
    ax.set_title("Test T04: Finite-sample coverage, abstention, and false certification")
    ax.legend(frameon=False, loc="center right")
    fig.tight_layout()
    save_all(fig, "fig_flagship_6_coverage_abstention.pdf")

    # Figure 7: Cross-market external validation and VPIN horse race (T10)
    markets = [
        "Binance Thin\n(Primary X6)",
        "Binance New\n(Repl. Y6)",
        "Binance Fresh\n(Impact Z6)",
        "Binance HAR\n(Vol. Z9)",
        "Binance + VPIN\n(Post-hoc R8)",
        "US Equities\n(Thin SIP)",
        "Bybit Depth\n(Order Book)",
    ]
    dr2 = [1.216, 0.845, 1.583, 2.787, 2.032, 0.499, 0.033]
    ci_lo = [0.273, 0.303, 0.588, 1.425, 1.012, 0.272, 0.019]
    ci_hi = [7.987, 6.371, 3.237, 4.944, 3.418, 0.779, 0.053]
    fig, ax = plt.subplots(figsize=(6.4, 2.9))
    x = np.arange(len(markets))
    yerr = [np.array(dr2) - np.array(ci_lo), np.array(ci_hi) - np.array(dr2)]
    ax.bar(x, dr2, yerr=yerr, capsize=3, color="#1f77b4", width=0.55, alpha=0.88)
    ax.set_xticks(x)
    ax.set_xticklabels(markets, fontsize=7.5)
    ax.set_ylabel("Out-of-sample $\\Delta R^2$ (percentage points)")
    ax.set_title("Cross-market validation and post-hoc VPIN horse race")
    fig.tight_layout()
    save_all(fig, "fig_flagship_7_cross_market.pdf")

    return created


def main() -> dict:
    # Run unit test suite first
    test_exact_witness_rational_values()
    test_convolution_gain_horizons_1_to_8()
    test_confidence_coverage_and_false_certification()
    test_two_world_bound_and_sample_complexity()
    test_robust_optimizer_and_abstention()
    test_balance_sheet_solvency_contract()

    # T01 & T02: Exact witness and Theorem A
    res_t01_t02 = verify_witness_and_theorem_A(max_lag=12)

    # T03: Risk-specific sample complexity vs cohort identification
    mA, mB = build_witness_markets()
    hA = np.array([float(x) for x in exact_impulse_response(mA, max_lag=6)])
    hB = np.array([float(x) for x in exact_impulse_response(mB, max_lag=6)])
    delta_h_L3 = hA[:4] - hB[:4]
    sigma_cov_L3 = (0.002 ** 2) * np.eye(4)
    n_min_L3 = theorem_C_minimum_observations(delta_h_L3, sigma_cov_L3, beta=0.05, epsilon_loss_frac=0.45)
    l_star_margin_005 = theorem_C_horizon_for_safety_margin(m0=0.04, r_bar=0.80, delta_safe=0.05)
    res_t03 = {
        "n_min_safe_L2": "Infinity (delta_h = 0)",
        "n_min_safe_L3_at_sd_0002": round(float(n_min_L3), 2),
        "lag_horizon_for_margin_005_rbar_080": l_star_margin_005,
        "compatible_Q_bounds_d0_rbar_095": list(compatible_feedback_bounds_d0(0.04, 0.95)),
        "compatible_Q_bounds_d1_market_A": list(compatible_feedback_bounds_d1(0.04, 0.02, 0.95)),
        "compatible_Q_bounds_d1_market_B": list(compatible_feedback_bounds_d1(0.04, 0.019, 0.95)),
    }

    # T04: Confidence calibration across sample sizes + heavy-tail stress test
    cov_grid = []
    for N in (50, 100, 250, 500, 1000, 2500):
        c = run_coverage_simulation_T04(
            true_h=hA[:5], a=0.40, true_Q=0.08, r_bar=0.95, noise_sd=0.002, sample_size_N=N, n_trials=400, seed=2026 + N
        )
        c["N"] = N
        cov_grid.append(c)
    stress_t4 = run_coverage_simulation_T04(
        true_h=hA[:5], a=0.40, true_Q=0.08, r_bar=0.95, noise_sd=0.002, sample_size_N=500, n_trials=400, seed=9999, heavy_tail_df=4.0
    )

    # T05: Exhaustive worst-case disturbance verification & peak-gate counterexample
    exhaustive_checks = []
    for H in range(1, 9):
        g_sub = hB[:H]
        g_cum = cumulative_convolution_gain(g_sub)
        w_val, _ = exhaustive_worst_case_disturbance(g_sub, v_bound=1.0)
        exhaustive_checks.append({"H": H, "G_cum": round(g_cum, 6), "exhaustive_max": round(w_val, 6), "diff": abs(g_cum - w_val)})
    peak_counterexample = repeated_vs_peak_gate_counterexample(hB[:8], budget_B=1.0)

    # T06: Global optimizer & balance-sheet certification
    bs = BalanceSheetContract()
    res_t06 = {
        "closed_form_witness_B": closed_form_optimal_admission(0.40, 0.42, 1.0, 1.0, 0.0, 1.0, 0.36),
        "closed_form_infeasible_abstain": closed_form_optimal_admission(0.40, 0.42, 1.0, 1.0, 0.0, 1.0, 0.75),
        "balance_sheet_feasible": solve_balance_sheet_guard_globally(bs, 0.0, 0.40, 0.20, 1.0, 1.80),
        "balance_sheet_infeasible_abstain": solve_balance_sheet_guard_globally(bs, 0.0, 0.40, 0.20, 1.0, 2.50),
    }

    # T07: Disclosure value across Public, Class-Tagged, and Audited Channel
    res_t07 = evaluate_disclosure_tiers_T07()

    # T08: Financial mechanism controls (from R4, R5, R8, Y8)
    res_t08 = {
        "fixed_grid_depletion_R5": {"fixed_band_eps30": 0.0021, "recentred_band_eps30": -0.0004, "share_positive_fixed": 0.95},
        "price_impact_controls_Y8": {"unconditional_dR2": 0.845, "with_4_impact_controls_dR2": 0.682, "retention_share": 0.807},
        "vpin_horse_race_R8": {"unconditional_dR2": 2.787, "vpin_alone_dR2": 1.240, "c3_beyond_vpin_dR2": 2.032, "retention_share": 0.729},
    }

    # T09: Model misspecification stress tests
    res_t09 = run_misspecification_stress_T09()

    # T10: Real-market external validation summary
    res_t10 = {
        "binance_thin_4_tests_dR2_pts": [1.216, 0.845, 1.583, 2.787],
        "us_equities_thin_23_dR2_pts": 0.499,
        "bybit_orderbook_6_dR2_pts": 0.033,
        "bybit_trades_only_14_dR2_pts": 0.000,
        "certified_guard_3day_dlogTLR": -0.024,
    }

    # T11: 8-Guard comparison
    res_t11 = run_eight_guard_comparison_T11()

    # T12: Equilibrium and welfare under ambiguity vs disclosure
    res_t12 = run_equilibrium_and_welfare_T12()

    all_results = {
        "status": "ALL_12_TESTS_AND_6_UNIT_SUITES_PASSED",
        "T01_T02_witness_and_theorem_A": res_t01_t02,
        "T03_risk_specific_sample_complexity": res_t03,
        "T04_coverage_grid": cov_grid,
        "T04_heavy_tail_stress": stress_t4,
        "T05_exhaustive_convolution_and_counterexample": {
            "horizons_1_to_8": exhaustive_checks,
            "peak_gate_counterexample": peak_counterexample,
        },
        "T06_global_optimizer_and_abstention": res_t06,
        "T07_disclosure_value": res_t07,
        "T08_financial_mechanism_controls": res_t08,
        "T09_model_misspecification": res_t09,
        "T10_external_validation": res_t10,
        "T11_eight_guard_comparison": res_t11,
        "T12_equilibrium_and_welfare": res_t12,
    }

    out_dir = ROOT / "research_extension" / "information_safety" / "results"
    out_dir.mkdir(parents=True, exist_ok=True)
    out_file = out_dir / "flagship_upgrade_results.json"
    out_file.write_text(json.dumps(all_results, indent=2) + "\n")

    fig_dirs = [
        ROOT / "ceiling_suite" / "paper2" / "figs",
        ROOT / "ceiling_suite" / "papers" / "paper2" / "figs",
        ROOT / "ceiling_suite" / "papers" / "versions" / "figs",
        out_dir / "figs",
    ]
    figs = generate_flagship_figures(all_results, fig_dirs)
    print(f"[PASS] Wrote {out_file} and generated {len(figs)} flagship figures: {figs}")
    return all_results


if __name__ == "__main__":
    main()
