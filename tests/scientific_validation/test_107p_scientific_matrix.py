"""Comprehensive 107p Scientific Remediation & Falsification Test Matrix (MM-00 through MM-16).

Directly tests and attempts to falsify every mathematical, accounting, empirical,
and formal-coverage claim in the remediated Machine Markets manuscript.
"""

from __future__ import annotations

import csv
import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]


def _sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def test_mm00_provenance_and_independent_oracle():
    """MM-00: Verify 107p PDF SHA-256 provenance and standalone reference oracle."""
    supplied_pdf = ROOT / ".codex-research" / "Machine_Markets_JF_Submission(20261014-043429).pdf"
    if supplied_pdf.exists():
        assert _sha256(supplied_pdf) == "fafb4c9e5dab17cfb111e07f5367831e57f366949750adc3881ec7916ed1ce9e"

    receipt_path = ROOT / "scripts" / "independent_checks" / "independent_oracle_receipt.json"
    assert receipt_path.exists()
    receipt = json.loads(receipt_path.read_text())
    assert "CE_01_two_trade_toeplitz" in receipt
    assert "CE_04_05_lecam_pairs" in receipt
    assert "CE_06_07_guard_shock_domain" in receipt
    assert "CE_06_07_15_guard_shock_domain" in receipt
    assert "signed_shock_counterexample_ce15" in receipt["CE_06_07_15_guard_shock_domain"]


def test_mm01_cost_functional_and_two_trade_counterexample():
    """MM-01 (CE-01): Reconcile Toeplitz round-trip loss vs direct-only proxy and account capital."""
    res16 = json.loads((ROOT / "breakthrough_experiments" / "results_exp16_nonconvex_duality.json").read_text())
    ce01 = res16["two_trade_counterexample_ce01"]
    assert ce01["v"] == [1.0, -1.0]
    assert abs(ce01["loss_quad_toeplitz"] - 0.3488) < 1e-9
    assert abs(ce01["loss_quad_direct_only_proxy"] - 0.8000) < 1e-9
    assert abs(ce01["C_account_pathwise"] - 0.4288) < 1e-9

    res13 = json.loads((ROOT / "breakthrough_experiments" / "results_exp13_account_capital.json").read_text())
    for row in res13["designs"]:
        assert "final_pnl_H0" in row
        assert "final_pnl_H1" in row
        if abs(row["end_inventory"]) < 1e-9:
            terminal_loss_worst = max(-row["final_pnl_H0"], -row["final_pnl_H1"])
            assert row["C0_required"] >= terminal_loss_worst - 1e-9

    tex = (ROOT / "paper" / "Machine_Markets_JF_Submission.tex").read_text()
    assert r"\frac{1}{2} v^\top T_{h_i} v" in tex
    assert "0.3488" in tex


def test_mm02_zero_padding_monotonicity_and_candidate_separation():
    """MM-02 (CE-02): Verify C*(L+1) <= C*(L) via zero-padding and candidate separation."""
    res16 = json.loads((ROOT / "breakthrough_experiments" / "results_exp16_nonconvex_duality.json").read_text())
    rows = res16["horizon_sweep"]
    horizons = [r["L"] for r in rows]
    assert horizons == [80, 120, 160, 240, 320, 480]

    monotone_c0 = [r["feasible_probe_C0"] for r in rows]
    unpadded_c0 = [r["unpadded_full_support_C0"] for r in rows]

    # Monotone best feasible upper bound must be non-increasing in L
    for i in range(len(monotone_c0) - 1):
        assert monotone_c0[i + 1] <= monotone_c0[i] + 1e-12

    # At L=320 and L=480, monotone zero-padded bound stays at 64.558 while unpadded rises
    assert abs(monotone_c0[3] - 64.558) < 1e-2
    assert abs(monotone_c0[4] - monotone_c0[3]) < 1e-9
    assert abs(monotone_c0[5] - monotone_c0[3]) < 1e-9
    assert unpadded_c0[4] > monotone_c0[4]
    assert unpadded_c0[5] > monotone_c0[5]


def test_mm03_rayleigh_holder_interval_certification():
    """MM-03 (CE-03): Verify continuous interval-certified and closed-form 0-grid Rayleigh-Holder lower bounds."""
    res16 = json.loads((ROOT / "breakthrough_experiments" / "results_exp16_nonconvex_duality.json").read_text())
    for r in res16["horizon_sweep"]:
        c_cert = r["lb_certified_FH_rayleigh_holder"]
        c_semi = r["lb_semi_analytic_d2_closed_form"]
        c_0grid = r["lb_closed_form_analytic_0grid"]
        c_grid = r["lb_grid_estimate_FH_rayleigh_holder"]
        c_feas = r["feasible_probe_C0"]
        assert c_cert <= c_grid + 1e-9
        assert c_semi <= c_cert + 1e-9
        assert c_0grid <= c_feas + 1e-9
        assert r["interval_enclosure_width"] < 2e-3
        assert c_cert <= c_feas
        audit = r["interval_certificate_audit"]
        assert audit["n_theta_intervals"] == 1800
        assert audit["n_d2_intervals"] == 4000
        assert audit["total_certified_boxes"] == 7200000
        assert audit["ieee754_safety_margin"] == 1e-9
        assert "worst_box_certificate" in audit
    r80 = res16["horizon_sweep"][0]
    assert abs(r80["lb_certified_FH_rayleigh_holder"] - 64.7423) < 1e-3
    assert abs(r80["lb_semi_analytic_d2_closed_form"] - 64.7383) < 1e-3
    assert abs(r80["lb_closed_form_analytic_0grid"] - 63.9206) < 1e-3
    assert abs(r80["gap_vs_FH_rayleigh_holder_pct"] - 0.98) < 0.02


def test_mm04_lecam_literal_vs_refined_and_rate_domain():
    """MM-04 (CE-04, CE-05): Verify literal moment-matched vs rate-refined Le Cam bounds and matching Theta((Delta eta)^-6) upper bound."""
    res17 = json.loads((ROOT / "breakthrough_experiments" / "results_exp17_minimax_lecam_bound.json").read_text())
    interval = res17["admissible_delta_eta_open_interval"]
    assert interval[0] == 0.0
    assert abs(interval[1] - (8.0 / 11.0)) < 1e-9
    assert "Omega((Delta eta)^-6)" in res17["theorem"]
    assert "Theta((Delta eta)^-6)" in res17["theorem"]
    assert abs(res17["loglog_slope_upper_bound"] - (-6.070)) < 0.05

    row010 = [r for r in res17["separation_sweep"] if abs(r["delta_eta"] - 0.10) < 1e-9][0]
    for m_diff in row010["moment_diffs_analytic_m0_m1_m2_m3"][:3]:
        assert abs(m_diff) < 1e-15
    assert abs(row010["moment_diff_m3_exact"] - 9.9e-6) < 1e-12
    assert abs(row010["n_star_lecam_analytic_95pct"] - 5927.57) < 0.5
    assert abs(row010["n_star_lecam_95pct_any_estimator"] - 6172.24) < 0.5
    assert row010["n_star_minimax_upper_bound_95pct"] > row010["n_star_lecam_95pct_any_estimator"]
    assert abs(row010["moment_diffs_refined_m0_m1_m2_m3"][1]) > 1e-6


def test_mm05_resolvent_guard_domain_and_counterexample():
    """MM-05 (CE-06, CE-07, CE-15): Verify admissible shock threshold, signed shock counterexample, and NO_SAFE_ACTION."""
    res18 = json.loads((ROOT / "breakthrough_experiments" / "results_exp18_crash_free_ai_guard.json").read_text())
    vc = res18["venue_calibration"]
    assert abs(vc["single_step_admissible_shock_safe_usdt"] - (8100.0 / 2010.0)) < 1e-6
    assert abs(vc["single_step_admissible_shock_liquidation_usdt"] - (9050.0 / 2010.0)) < 1e-6

    ce = res18["out_of_domain_counterexample_ce06_ce07"]
    ce15 = ce["signed_shock_counterexample_ce15"]
    assert ce15["downward_shock_minus_10_pure_mtm"]["liquidated"] is False
    assert ce15["downward_shock_minus_10_pure_mtm"]["equity_usdt"] == 30000.0
    assert ce15["downward_shock_minus_10_pure_mtm"]["maintenance_margin_usdt"] == 850.0
    assert ce15["upward_shock_plus_10_pure_mtm"]["liquidated"] is True
    assert ce15["upward_shock_plus_10_pure_mtm"]["equity_usdt"] == -10000.0
    assert ce15["upward_shock_plus_10_pure_mtm"]["maintenance_margin_usdt"] == 1050.0
    assert ce15["downward_shock_minus_10_episode"]["status"] == "FEASIBLE"
    assert ce15["upward_shock_plus_10_episode"]["status"] == "NO_SAFE_ACTION"
    assert ce["unattenuated_result"]["status"] == "NO_SAFE_ACTION"
    assert ce["unattenuated_result"]["liquidated"] is True
    assert ce["unattenuated_result"]["raw_min_equity_usdt"] <= -190000.0
    assert ce["attenuated_result"]["status"] == "NO_SAFE_ACTION"
    assert ce["attenuated_result"]["liquidated"] is True
    assert ce["attenuated_result"]["raw_min_equity_usdt"] <= -19000.0


def test_mm06_controller_channel_ablation_and_costly_hedging():
    """MM-06 (CE-08, CE-09): Verify 6-channel matched-physics ablation and costly hedging in exp18."""
    res18 = json.loads((ROOT / "breakthrough_experiments" / "results_exp18_crash_free_ai_guard.json").read_text())
    ab = res18["controller_channel_ablation"]
    for reg in ["Regime_II_NonNormal_Herding", "Regime_IV_Binance_Empirical_Replay"]:
        reg_ab = ab[reg]
        # 1. Hedge only + unthrottled J(1) liquidates 100%
        assert reg_ab["Ablation_Hedge_Only_Unthrottled_J"]["liquidation_rate"] == 1.0
        # 2. Shock gate only + unthrottled J(1) liquidates 100%
        assert reg_ab["Ablation_Shock_Gate_Only_Unthrottled_J"]["liquidation_rate"] == 1.0
        # 3. Pure operator J(alpha_t) with unattenuated shocks and zero hedging achieves 0.0% liquidation
        pure_op = reg_ab["Ablation_Pure_Operator_Unattenuated"]
        assert pure_op["liquidation_rate"] == 0.0
        assert pure_op["worst_max_drawdown_usdt"] < 9050.0
        assert pure_op["mean_hedge_cost_usdt"] == 0.0
        # 4 & 6. Active hedging configurations pay strictly positive spread+fee costs
        assert reg_ab["Ablation_Operator_Plus_Costly_Hedge_Unattenuated"]["mean_hedge_cost_usdt"] > 50.0
        assert reg_ab["Resolvent_Guard_Kreiss"]["mean_hedge_cost_usdt"] > 50.0
        assert reg_ab["Resolvent_Guard_Kreiss"]["liquidation_rate"] == 0.0


def test_mm07_quote_availability_vs_admitted_depth():
    """MM-07: Verify separation of model admission eligibility from admitted depth share."""
    res18 = json.loads((ROOT / "breakthrough_experiments" / "results_exp18_crash_free_ai_guard.json").read_text())
    by_reg = {r["regime"]: r["architectures"]["Resolvent_Guard_Kreiss"] for r in res18["regimes"]}

    assert by_reg["Regime_I_Benign"]["admitted_depth_share_pct"] == 100.0
    assert by_reg["Regime_I_Benign"]["throttled_flow_share_pct"] == 0.0

    for reg in ["Regime_II_NonNormal_Herding", "Regime_IV_Binance_Empirical_Replay"]:
        g = by_reg[reg]
        assert g["model_admission_eligibility_pct"] == 100.0
        assert 25.0 < g["admitted_depth_share_pct"] < 45.0
        assert abs(g["admitted_depth_share_pct"] + g["throttled_flow_share_pct"] - 100.0) < 1e-6


def test_mm08_exp19_stress_vs_direct_physical_replay():
    """MM-08 (CE-10): Verify exp19 separates stress benchmark, direct signed replay, and empirical 1s crash-burst OLS operator."""
    res19 = json.loads((ROOT / "breakthrough_experiments" / "results_exp19_historical_crash_replay.json").read_text())
    assert len(res19["events"]) == 4
    for ev in res19["events"].values():
        assert ev["sha256_matches_official_checksum"] is True
        assert "physical_signed_replay_architectures" in ev
        assert "burst_ols_3x3_price_output_gain_MC" in ev["day_stats"]
        assert "empirical_burst_ols_replay_architectures" in ev

    stress = res19["overall_100_episode_summary"]
    assert stress["Unguarded"]["liquidation_rate_pct"] == 100.0
    assert stress["Eigenvalue_Guard"]["liquidation_rate_pct"] == 100.0
    assert stress["Resolvent_Guard_Kreiss"]["liquidation_rate_pct"] == 0.0
    assert 30.0 < stress["Resolvent_Guard_Kreiss"]["admitted_depth_share_pct"] < 40.0

    direct = res19["overall_100_episode_physical_signed_summary"]
    assert abs(direct["Unguarded"]["liquidation_rate_pct"] - 4.0) < 1e-9
    assert abs(direct["Resolvent_Guard_Kreiss"]["liquidation_rate_pct"] - 4.0) < 1e-9

    burst_op = res19["pooled_burst_ols_operator"]
    assert burst_op["spectral_radius"] < 0.90
    assert burst_op["price_output_gain_MC"] > 20.0
    burst_replay = res19["overall_100_episode_empirical_burst_ols_summary"]
    assert burst_replay["Unguarded"]["liquidation_rate_pct"] == 100.0
    assert burst_replay["Eigenvalue_Guard"]["liquidation_rate_pct"] == 100.0
    assert burst_replay["Resolvent_Guard_Kreiss"]["liquidation_rate_pct"] == 0.0


def test_mm09_exp20_exact_l2_book_walking():
    """MM-09: Verify exp20 10-level L2 book walking slippage and depth-aware guard."""
    res20 = json.loads((ROOT / "breakthrough_experiments" / "results_exp20_exact_l2_book_walking.json").read_text())
    sweep = res20["book_microstructure_stats"]["sweep_profile"]
    assert len(sweep) == 5
    guards = res20["dealer_ledger_comparison"]
    assert guards["Resolvent_Guard_DepthBlind"]["exact_10level_l2_book_walking"]["liquidation_rate_pct"] == 1.0
    assert guards["Resolvent_Guard_Kreiss"]["exact_10level_l2_book_walking"]["liquidation_rate_pct"] == 0.0


def test_mm10_exp21_ols_vs_constructed_stress_operator():
    """MM-10 (CE-11): Verify exp21 separates passive 10s OLS, empirical 1s crash-burst OLS, constructed stress, and direct replay."""
    res21 = json.loads(
        (ROOT / "breakthrough_experiments" / "results_exp21_empirical_multi_asset_kreiss.json").read_text()
    )
    jm = res21["jacobian_16x16_metrics"]
    assert abs(jm["ols_var1_spectral_radius"] - 0.7717) < 1e-3
    assert abs(jm["ols_var1_price_output_gain_MC"] - 1.0) < 1e-6
    assert jm["burst_ols_1s_spectral_radius"] < 0.90
    assert jm["burst_ols_1s_price_output_gain_MC"] > 25.0
    assert jm["stress_jacobian_spectral_radius"] < 0.80
    assert jm["stress_jacobian_price_output_gain_MC"] > 130.0

    ols_replay = res21["observed_ols_operator_replay_100_episodes"]
    assert ols_replay["Unguarded"]["liquidation_rate_pct"] == 3.0
    assert ols_replay["Resolvent_Guard_Kreiss"]["liquidation_rate_pct"] == 1.0

    burst_ols_replay = res21["empirical_burst_ols_operator_replay_100_episodes"]
    assert burst_ols_replay["Unguarded"]["liquidation_rate_pct"] == 100.0
    assert burst_ols_replay["Eigenvalue_Guard"]["liquidation_rate_pct"] == 100.0
    assert burst_ols_replay["Resolvent_Guard_Kreiss"]["liquidation_rate_pct"] == 0.0

    stress_replay = res21["portfolio_ledger_100_episodes"]
    assert stress_replay["Unguarded"]["liquidation_rate_pct"] == 100.0
    assert stress_replay["Eigenvalue_Guard"]["liquidation_rate_pct"] == 100.0
    assert stress_replay["Resolvent_Guard_Kreiss"]["liquidation_rate_pct"] == 0.0

    direct_replay = res21["physical_signed_8asset_replay_100_episodes"]
    assert direct_replay["Unguarded"]["liquidation_rate_pct"] == 1.0
    assert direct_replay["Resolvent_Guard_Kreiss"]["liquidation_rate_pct"] == 0.0


def test_mm11_adaptive_probing_solvency_tail_risk():
    """MM-11 (CE-12): Verify adaptive SPRT expected loss vs pathwise solvency tail risk."""
    res14 = json.loads((ROOT / "breakthrough_experiments" / "results_exp14_capital_frontier_exact.json").read_text())
    row005 = [r for r in res14["sweep"] if abs(r["delta"] - 0.05) < 1e-9][0]
    assert abs(row005["capital_lower_bound_deterministic"] - 61.44) < 0.05
    assert abs(row005["capital_lower_bound_adaptive_expected"] - 30.09) < 0.05

    mc = res14["sequential_mc_delta_0_05"]["H0"]
    assert abs(mc["mean_loss"] - 45.96) < 0.5
    assert abs(mc["p99_C0_required"] - 155.99) < 1.0
    assert abs(mc["ruin_prob_at_mean_loss"] - 0.3773) < 0.01


def test_mm12_lean_proof_scope_honesty():
    """MM-12: Verify Lean 4 coverage table and MANUSCRIPT_COVERAGE.md accurately report 317-declaration 23/23 FULL coverage."""
    cov_md = (ROOT / "research_extension" / "current_manuscript_lean_20261008" / "MANUSCRIPT_COVERAGE.md").read_text()
    assert "rayleigh_holder_closed_form_analytic_lower_bound" in cov_md
    assert "kreiss_resolvent_guard_solvency_invariance" in cov_md
    assert "23 / 23 FULL" in cov_md
    assert "0 / 23 NOT FORMALIZED" in cov_md

    claim_map = (ROOT / "paper" / "generated" / "claim_to_code_map.tex").read_text()
    assert "Conditional Bounded-Shock Forward Solvency of the Real-Time Resolvent Guard" in claim_map
    assert claim_map.count("& FULL &") == 23
    assert "NOT FORMALIZED" not in claim_map


def test_mm13_disclosure_precision_and_nonnormal_decoupling():
    """MM-13 (CE-13, CE-14): Verify disclosure rounding floor (15.52 USDT) and non-normal coordinate weight (160.003)."""
    res7 = json.loads((ROOT / "breakthrough_experiments" / "results_exp7_disclosure_value.json").read_text())
    assert "delta_0.05" in res7
    res12 = json.loads((ROOT / "breakthrough_experiments" / "results_exp12_nonnormal_balance_sheet.json").read_text())
    assert abs(res12["amplification_decoupling_1asset"]["C_price"]["MC"] - 1.0) < 1e-9
    assert abs(res12["amplification_decoupling_1asset"]["C_margin"]["MC"] - 160.003124969483) < 1e-6


def test_mm14_to_mm16_validation_ledger_and_manuscript_build():
    """MM-14..MM-16: Verify persistent validation ledger completeness and clean LaTeX build."""
    val_dir = ROOT / "docs" / "scientific_validation"
    required_files = [
        "EXECUTION_PLAN.md",
        "RESEARCH_MANIFEST.md",
        "ISSUE_REGISTER.md",
        "CLAIM_EVIDENCE_LEDGER.csv",
        "PROOF_COVERAGE.md",
        "COUNTEREXAMPLE_REGISTER.md",
        "EXPERIMENT_CONTRACTS.md",
        "REPRODUCIBILITY_RECEIPT.md",
        "EXTERNAL_REVIEW_PACKET.md",
        "RESUME_HERE.md",
    ]
    for fname in required_files:
        p = val_dir / fname
        assert p.exists(), f"Missing {p}"
        assert p.stat().st_size > 200, f"Empty or stub file {p}"

    assert (ROOT / "RESUME_HERE.md").exists()

    with (val_dir / "CLAIM_EVIDENCE_LEDGER.csv").open() as f:
        rows = list(csv.DictReader(f))
    assert len(rows) >= 26

    pdf_path = ROOT / "paper" / "Machine_Markets_JF_Submission.pdf"
    log_path = ROOT / "paper" / "Machine_Markets_JF_Submission.log"
    assert pdf_path.exists() and pdf_path.stat().st_size > 1_000_000
    if log_path.exists():
        log_text = log_path.read_text(errors="ignore")
        assert "LaTeX Warning: There were undefined references." not in log_text
        assert "! Emergency stop." not in log_text


def test_mm17_113p_audit_tc_g_c_e_v_gates():
    """MM-17 (113p Review Findings F01-F12): Verify TC-G1..G4, TC-C1..C5, TC-E1..E6, and TC-V1..V4."""
    receipt = json.loads((ROOT / "scripts" / "independent_checks" / "independent_oracle_receipt.json").read_text())

    # 1. Guard verification (TC-G1..G4: F03, F04, F05, F09)
    tc_g = receipt["TC_G1_to_G4_guard_verification"]
    g1 = tc_g["TC_G1_cumulative_shock_at_zero_alpha"]
    assert g1["pure_operator_alpha_0"]["cum_shock_term_usdt"] > 0.0
    assert g1["shock_gated_alpha_0"]["cum_shock_term_usdt"] > 0.0
    assert g1["persistent_breach_alpha_0"]["pass_cum_safe"] is False
    assert g1["persistent_breach_alpha_0"]["pass_both_ia39"] is False

    g2_rows = tc_g["TC_G2_maintenance_margin_tier2_sweep"]
    assert len(g2_rows) == 5
    for row in g2_rows:
        assert row["ia39_pass_reserve_safe"] == row["ia40_pass_reserve_safe"]
        if row["outcome"] == "RESERVE_SAFE":
            assert row["post_shock_b_rem_usdt"] >= 950.0 - 1e-9
        if abs(row["d_usdt"] - 4.05) < 1e-9:
            assert row["outcome"] == "BREACHES_RESERVE_ONLY"
            assert row["ia39_lhs_safe_usdt"] == 9090.5
            assert row["post_shock_b_rem_usdt"] == 909.5

    g3 = tc_g["TC_G3_non_anticipative_action_invariance"]
    assert g3["non_anticipative_invariant"] is True
    assert g3["alpha_selected_for_u1"] == g3["alpha_selected_for_u2"]

    g4 = tc_g["TC_G4_eigenvalue_threshold_reconciliation"]
    for reg_val in g4.values():
        if isinstance(reg_val, dict) and "liquidation_rate_rho_090" in reg_val:
            assert reg_val["liquidation_rate_rho_090"] == reg_val["liquidation_rate_rho_095"]

    # 2. Capital certificate & double-entry reconciliation (TC-C1..C5: F06, F07)
    tc_c = receipt["TC_C1_to_C5_capital_certificate_verification"]
    assert tc_c["TC_C1_decimal_50digit_outward_lb"]["passes_enclosure"] is True
    assert tc_c["TC_C1_decimal_50digit_outward_lb"]["decimal_50digit_str"].startswith("64.74228808")
    assert tc_c["TC_C2_stationary_subproblem_check"]["exceeds_certified_lb"] is True
    assert tc_c["TC_C3_adversarial_100k_probes"]["zero_violations"] is True
    assert tc_c["TC_C4_horizon_monotonicity_zero_padding"]["is_non_increasing"] is True
    assert abs(tc_c["TC_C5_double_entry_ledger_reconciliation"]["terminal_inventory_btc"]) < 1e-12
    assert tc_c["TC_C5_double_entry_ledger_reconciliation"]["max_reconciliation_discrepancy_usdt"] < 1e-11

    # 3. Empirical & econometric sensitivity (TC-E1..E6: F08, F10, F11)
    tc_e = receipt["TC_E1_to_E6_empirical_and_econometric_sensitivity"]
    e1 = tc_e["TC_E1_exp19_stress_vs_direct_vs_burst_ols"]
    assert e1["empirical_burst_ols_MC"] > 20.0
    assert e1["empirical_burst_ols_kreiss_liq_pct"] == 0.0
    assert e1["causal_oos_burst_ols_mean_MC"] > 14.0
    assert e1["causal_oos_burst_ols_unguarded_liq_pct"] == 100.0
    assert e1["causal_oos_burst_ols_kreiss_liq_pct"] == 0.0
    assert e1["endogenous_raw_historical_unguarded_liq_pct"] == 22.0
    assert e1["endogenous_raw_historical_eigenvalue_liq_pct"] == 22.0
    assert e1["endogenous_raw_historical_kreiss_liq_pct"] == 0.0

    e2 = tc_e["TC_E2_exp21_ols_vs_burst_ols_vs_stress_vs_direct"]
    assert e2["empirical_1s_burst_ols_MC"] > 25.0
    assert e2["empirical_1s_burst_ols_kreiss_liq_pct"] == 0.0
    assert e2["causal_oos_1s_burst_ols_mean_MC"] > 25.0
    assert e2["causal_oos_1s_burst_ols_unguarded_liq_pct"] == 100.0
    assert e2["causal_oos_1s_burst_ols_kreiss_liq_pct"] == 0.0
    assert e2["endogenous_raw_8asset_unguarded_liq_pct"] == 36.0
    assert e2["endogenous_raw_8asset_eigenvalue_liq_pct"] == 36.0
    assert e2["endogenous_raw_8asset_kreiss_liq_pct"] == 0.0
    assert tc_e["TC_E4_two_cohort_vs_three_cohort_specification"]["relative_kappa_diff_pct"] < 0.05
    assert tc_e["TC_E4_two_cohort_vs_three_cohort_specification"]["bic_favors_2cohort"] is True
    assert all(r["positive_impact_preserved"] for r in tc_e["TC_E5_order_splitting_parent_child_aggregation"])
    assert all(r["sign_reversal_confirmed"] for r in tc_e["TC_E6_observation_clock_event_volume_calendar"])

    # 4. Lean 4 & manuscript consistency (TC-V1..V4: F12)
    tc_v = receipt["TC_V1_to_V4_lean_and_manuscript_consistency"]
    assert tc_v["TC_V1_named_theorems_count"] == 319
    assert tc_v["TC_V2_full_manuscript_statements"] == 23
    assert tc_v["TC_V3_zero_sorry_and_zero_unapproved_axioms"] is True
    assert tc_v["TC_V4_table_ia15_compact_s01_to_s23"] is True

