"""Gate 8 audit: every row of Paper 2's ledger of pre-registered tests (Table tab:alltests) and the Part 15/16 tables is
recomputed from the result JSON files the notebooks wrote and compared with the number printed in the LaTeX source.
Usage: python3 verify_paper_numbers.py <dir with result folders> <paper2 tex dir>.  Exit code 1 on any mismatch."""
import json, os, re, sys

_H = os.path.dirname(os.path.abspath(__file__))
ROOT = sys.argv[1] if len(sys.argv) > 1 else os.path.join(_H, "results_archive")
TEX = sys.argv[2] if len(sys.argv) > 2 else os.path.join(_H, "paper2")


def M(rel):
    return json.load(open(os.path.join(ROOT, rel)))["metrics"]


def pts(v):
    return 100 * v


def get(d, *ks):
    for k in ks:
        d = d[k]
    return d


# (row label prefix in the LaTeX ledger, (point, lo, hi) computed from JSON, decimals printed)
p15 = M("outputs/p15res/results/W6_info_safety_test.json"); p16 = M("outputs/p16res/results/X6_untouched_symbols_test.json"); p17 = M("outputs/p17res/results/C6_new_venue_test.json"); p18 = M("outputs/p18res/results/R3_placebo_binance.json")["results"]
p19 = json.load(open(os.path.join(ROOT, "outputs/p19_20_21/P19_leverage_mechanism.json")))
p20 = json.load(open(os.path.join(ROOT, "outputs/p19_20_21/P20_fee_natural_experiment.json")))
p21 = json.load(open(os.path.join(ROOT, "outputs/p19_20_21/P21_guard_dollars.json")))
RECOMP = os.path.join(_H, "recomputed")
TEX1 = os.path.join(_H, "paper1")
p22_23 = json.load(open(os.path.join(RECOMP, "R_P2_p22_p23.json")))
p24_25 = json.load(open(os.path.join(RECOMP, "R_P2_p24_p25.json")))
p2_step2 = json.load(open(os.path.join(RECOMP, "R_P2_step2_theory.json")))
p1_cat = json.load(open(os.path.join(RECOMP, "R_P1_cat_disclosure_dollars.json")))
p1_lrn = json.load(open(os.path.join(RECOMP, "R_P1_learners.json")))
p1_oos = json.load(open(os.path.join(RECOMP, "R_P1_disclosure_oos.json")))
p1_state_oos = json.load(open(os.path.join(RECOMP, "R_P1_disclosure_state_oos.json")))
LEDGER = [
    ("BTCUSDT futures", lambda: [pts(get(M("depthres/results/D8_depth_test_G2.json"), "primary", "delta_r2"))] + [pts(x) for x in get(M("depthres/results/D8_depth_test_G2.json"), "primary", "delta_r2_ci")], 3),
    ("BTCUSDT spot", lambda: [pts(M("realres/results/P2.5_predictive_G2.json")["delta_r2"])] + [pts(x) for x in M("realres/results/P2.5_predictive_G2.json")["delta_r2_ci"]], 3),
    ("Thin books, 10 symbols", lambda: [pts(M("xres/results/X6_xsec_test_G2.json")["primary"]["delta_r2"])] + [pts(x) for x in M("xres/results/X6_xsec_test_G2.json")["primary"]["delta_r2_ci"]], 3),
    ("New thin symbols, 10", lambda: [pts(M("p5res/results/Y6_replication_G2.json")["primary"]["delta_r2"])] + [pts(x) for x in M("p5res/results/Y6_replication_G2.json")["primary"]["delta_r2_ci"]], 3),
    ("Fresh days, 20 thin", lambda: [pts(M("p6res/results/Z6_A_replication3.json")["result"]["delta_r2"])] + [pts(x) for x in M("p6res/results/Z6_A_replication3.json")["result"]["delta_r2_ci"]], 3),
    ("Position sizing, same", lambda: [get(M("p6res/results/Z6_B_guard_backtest.json"), "result", "vs_ref", "amp_vol", "log_TLR_minus_ref")] + get(M("p6res/results/Z6_B_guard_backtest.json"), "result", "vs_ref", "amp_vol", "ci"), 3),
    ("Bybit, 14 coins", lambda: [pts(M("p7res/results/W6_bybit_test.json")["primary"]["delta_r2"])] + [pts(x) for x in M("p7res/results/W6_bybit_test.json")["primary"]["delta_r2_ci"]], 3),
    ("Beyond volatility forecasting", lambda: [pts(M("p9res/results/U6_volbench_test.json")["primary"]["delta_r2"])] + [pts(x) for x in M("p9res/results/U6_volbench_test.json")["primary"]["delta_r2_ci"]], 3),
    ("Certified guard, position sizing", lambda: [get(M("p12res/results/Q6_certified_guard.json"), "vs_vol", "vs_ref", "amp_cert", "log_TLR_minus_ref")] + get(M("p12res/results/Q6_certified_guard.json"), "vs_vol", "vs_ref", "amp_cert", "ci"), 3),
    ("Bybit with order-book depth", lambda: [pts(M("outputs/p10res/results/V6_bybit_ob_test.json")["primary"]["delta_r2"])] + [pts(x) for x in M("outputs/p10res/results/V6_bybit_ob_test.json")["primary"]["delta_r2_ci"]], 3),
    ("Thin US stocks, 23", lambda: [pts(M("outputs/p14res/results/A5_us_equity_test.json")["primary"]["delta_r2"])] + [pts(x) for x in M("outputs/p14res/results/A5_us_equity_test.json")["primary"]["delta_r2_ci"]], 3),
    ("Untouched days, frozen model", lambda: [pts(p15["primary_1_forecast"]["delta_r2"])] + [pts(x) for x in p15["primary_1_forecast"]["delta_r2_ci"]], 3),
    ("Untouched days, guard vs static", lambda: [p15["primary_2_guard"]["log_TLR_diff"]] + p15["primary_2_guard"]["ci975"], 3),
    ("Untouched symbols, 5 thin", lambda: [pts(p16["P1"]["delta_r2"])] + [pts(x) for x in p16["P1"]["delta_r2_ci"]], 3),
    ("Untouched symbols, beyond VPIN", lambda: [pts(p16["P2"]["delta_r2"])] + [pts(x) for x in p16["P2"]["delta_r2_ci"]], 3),
    ("Untouched symbols, guard vs static", lambda: [p16["guard"]["comparisons"]["robust_guard vs static"]["log_TLR_diff"]] + p16["guard"]["comparisons"]["robust_guard vs static"]["ci95"], 3),
    ("New venue, Coinbase", lambda: [pts(p17["thin_eval"]["cands"]["real"]["delta_r2"])] + [pts(x) for x in p17["thin_eval"]["cands"]["real"]["delta_r2_ci"]], 3),
    ("Coinbase, real minus placebo", lambda: [pts(p17["real_minus_placebo"]["diff"])] + [pts(x) for x in p17["real_minus_placebo"]["ci"]], 3),
    ("OI liquidation forecast, 19 thin", lambda: [p22_23["part22"]["primary_1_forecast_liquidation"]["delta_r2_liq_pts"]] + p22_23["part22"]["primary_1_forecast_liquidation"]["delta_r2_liq_ci_pts"], 3),
    ("OI liquidation mediation, 19 thin", lambda: [pts(p22_23["part22"]["primary_2_mediation_by_liquidation"]["mediation_share"])] + [pts(x) for x in p22_23["part22"]["primary_2_mediation_by_liquidation"]["mediation_share_ci"]], 1),
    ("Non-resetting 18h guard capacity", lambda: [p22_23["part23"]["primary_matched_breach_capacity"]["delta_notional_usd"] / 1000.0] + [x / 1000.0 for x in p22_23["part23"]["primary_matched_breach_capacity"]["delta_notional_ci_usd"]], 1),
    ("Capped 18h throttle liq.", lambda: [p24_25["part24"]["primary_1_capped_liq_reduction"]["delta_liq_rate_pp"]] + p24_25["part24"]["primary_1_capped_liq_reduction"]["delta_liq_rate_ci_pp"], 2),
    ("Capped 18h throttle ES", lambda: [p24_25["part24"]["primary_2_capped_es95_loss_reduction"]["delta_es95_usd"] / 1000.0] + [x / 1000.0 for x in p24_25["part24"]["primary_2_capped_es95_loss_reduction"]["delta_es95_ci_usd"]], 1),
    ("Persistence forecast, 19 thin", lambda: [p24_25["part25"]["primary_1_forecast_ckpt_persistence"]["delta_r2_pers_pts"]] + p24_25["part25"]["primary_1_forecast_ckpt_persistence"]["delta_r2_pers_ci_pts"], 3),
    ("Persistence mediation + placebo", lambda: [pts(p24_25["part25"]["primary_2_mediation_by_ckpt_persistence"]["mediation_share"])] + [pts(x) for x in p24_25["part25"]["primary_2_mediation_by_ckpt_persistence"]["mediation_share_ci"]], 1),
]

tex = open(os.path.join(TEX, "p2_thin.tex")).read()
tab = tex[tex.index(r"\caption{All pre-registered tests}"):]
tab = tab[:tab.index(r"\end{tabular}")]
rows = [r for r in tab.split("\\\\") if "&" in r]
num = re.compile(r"[+-]?\d+\.\d+")
bad = 0; checked = 0
for label, fn, dec in LEDGER:
    row = next((r for r in rows if r.replace("\\midrule", "").strip().startswith(label)), None)
    if row is None:
        print("MISSING ROW", label); bad += 1; continue
    printed = [float(x) for x in num.findall(row.split("&")[2])][:3]
    comp = fn()
    ok = all(abs(p - c) <= 0.5 * 10 ** (-dec) + 1e-12 or (abs(p) < 0.0011 and abs(c) < 0.0011) for p, c in zip(printed, comp))
    # the certified-guard upper bound is printed with 4 decimals (-0.0004)
    if label.startswith("Certified guard"):
        ok = abs(printed[0] - comp[0]) < 5e-4 and abs(printed[1] - comp[1]) < 5e-4 and abs(printed[2] - comp[2]) < 5e-5
    checked += 1; bad += not ok
    print(f"{'OK ' if ok else 'BAD'} {label:38s} printed {printed}  json {[round(c, 4) for c in comp]}")

# Part 16 table and text
t16 = open(os.path.join(TEX, "p2_istests.tex")).read()
for lab, key, val in [("P1", "+0.73", pts(p16["P1"]["delta_r2"])), ("P2", "+0.56", pts(p16["P2"]["delta_r2"])),
                      ("vpin", "+0.28", pts(p16["vpin"]["delta_r2"])), ("S60", "+0.42", pts(p16["S60"]["delta_r2"]))]:
    ok = abs(float(key) - val) < 0.005 and key in t16; checked += 1; bad += not ok
    print(f"{'OK ' if ok else 'BAD'} Part 16 {lab:6s} printed {key} json {val:.4f}")
for lab, key, val in [("P18 part9 real-placebo", "+2.74", pts(p18["part9_thin"]["real_minus_placebo"]["diff"])),
                      ("P18 part16 real-placebo", "+0.79", pts(p18["part16_thin"]["real_minus_placebo"]["diff"])),
                      ("P17 primary", "-0.09", pts(p17["thin_eval"]["cands"]["real"]["delta_r2"])),
                      ("P19 perp delta_r2", "+6.495", p19["primary_1_interaction"]["delta_r2_perp_pts"]),
                      ("P19 high-low diff", "+4.495", p19["primary_1_interaction"]["delta_r2_high_minus_low_lev_pts"]),
                      ("P19 spot delta_r2", "+0.987", p19["primary_2_spot_comparison"]["delta_r2_spot_pts"]),
                      ("P19 spot cw_t", "4.96", p19["primary_2_spot_comparison"]["clark_west_t"]),
                      ("P19 spot/perp ratio", "0.152", p19["primary_2_spot_comparison"]["ratio_spot_to_perp"]),
                      ("P19 interaction", "-0.18", p19["primary_1_interaction"]["beta_C3_x_high_LEV_bps"]),
                      ("P20 pooled spot kappa", "-0.2432", p20["by_event"]["spot_zero_fee_pooled"]["impact_kappa_hat"]["beta"]),
                      ("P20 all3 kappa", "+0.0082", p20["by_event"]["all_events_pooled"]["impact_kappa_hat"]["beta"]),
                      ("P20 pooled spot volume", "+1.355", p20["by_event"]["spot_zero_fee_pooled"]["log_quote_volume"]["beta"]),
                      ("P21 part15 (c)vs(b) logdiff", "-0.0118", p21["part15_untouched_days"]["comparisons"]["vol_robust vs vol_cap"]["log_TLR_diff"]),
                      ("P21 part16 (c)vs(b) logdiff", "-0.0722", p21["part16_untouched_symbols"]["comparisons"]["vol_robust vs vol_cap"]["log_TLR_diff"]),
                      ("P21 part15 (c)-(b) saving", "398", p21["part15_untouched_days"]["c_vs_b_es95_saving_usd"]),
                      ("P21 part16 (c)-(b) saving", "2{,}557", p21["part16_untouched_symbols"]["c_vs_b_es95_saving_usd"]),
                      ("P22 excursion 22nd", "+6.516", p22_23["part22"]["excursion_forecast_on_22nds"]["delta_r2_mae_pts"]),
                      ("P22 primary 1 liq", "-0.795", p22_23["part22"]["primary_1_forecast_liquidation"]["delta_r2_liq_pts"]),
                      ("P22 primary 2 share", "-6.8", 100 * p22_23["part22"]["primary_2_mediation_by_liquidation"]["mediation_share"]),
                      ("P23 primary delta N", "332{,}848", p22_23["part23"]["primary_matched_breach_capacity"]["delta_notional_usd"]),
                      ("P23 secondary log es95", "+0.1427", p22_23["part23"]["primary_matched_breach_capacity"]["c_vs_b_log_es95_diff"]),
                      ("P24 primary 1 liq pp", "-7.41", p24_25["part24"]["primary_1_capped_liq_reduction"]["delta_liq_rate_pp"]),
                      ("P24 primary 1 per 1M", "-4.09", p24_25["part24"]["primary_1_capped_liq_reduction"]["delta_liq_per_1M_deployed_pp"]),
                      ("P24 primary 2 es95", "26{,}429", abs(p24_25["part24"]["primary_2_capped_es95_loss_reduction"]["delta_es95_usd"])),
                      ("P24 secondary delta N", "172{,}416", p24_25["part24"]["secondary_matched_breach_capacity_42dates"]["delta_notional_usd"]),
                      ("P25 excursion 02_09", "+3.944", p24_25["part25"]["excursion_forecast_on_02_09"]["delta_r2_mae_pts"]),
                      ("P25 primary 1 pers", "+3.713", p24_25["part25"]["primary_1_forecast_ckpt_persistence"]["delta_r2_pers_pts"]),
                      ("P25 primary 2 share", "97.6", 100 * p24_25["part25"]["primary_2_mediation_by_ckpt_persistence"]["mediation_share"]),
                      ("P25 secondary L1", "+3.809", p24_25["part25"]["secondary_l1_integral_persistence"]["forecast_delta_r2_pts"])]:
    num_key = float(key.replace("{,}", ""))
    ok = abs(num_key - val) < 0.0051 and key in t16; checked += 1; bad += not ok
    print(f"{'OK ' if ok else 'BAD'} {lab:26s} printed {key} json {val:.4f}")

# Paper 2 Step 2 theory checks
t_p2_th = open(os.path.join(TEX, "p2_theory1.tex")).read() + open(os.path.join(TEX, "p2_guard.tex")).read()
for lab, key, val in [("P2 inventory S_with_inv", "2.5000", p2_step2["inventory_proposition"]["worked_example"]["S_with_inventory_closed"]),
                      ("P2 inventory S_no_inv", "2.7778", p2_step2["inventory_proposition"]["worked_example"]["S_no_inventory"]),
                      ("P2 drift alpha_drift", "0.24", p2_step2["drift_guard_proposition"]["alpha_drift"]),
                      ("P2 drift cap cost", "0.06", p2_step2["drift_guard_proposition"]["capacity_cost_closed_form"])]:
    ok = abs(float(key) - val) < 0.001 and key in t_p2_th; checked += 1; bad += not ok
    print(f"{'OK ' if ok else 'BAD'} {lab:26s} printed {key} json {val:.4f}")

# Paper 1 checks (learners, CAT dollars, disclosure OOS, disclosure state OOS)
t_p1 = open(os.path.join(TEX1, "p1_mixture.tex")).read() + open(os.path.join(TEX1, "p1_disclosure.tex")).read()
for lab, key, val in [("P1 learners R2_exp", "0.9448", p1_lrn["trained_online_learners"]["rls_trained"]["pred_a_single_exp_r2"]),
                      ("P1 learners fast gap", "5.31", 100 * p1_lrn["trained_online_learners"]["rls_trained"]["pred_d_nonstationary_rel_gap"]),
                      ("P1 CAT K2 Radau 0.10 roll", "14{,}741{,}376", p1_cat["rows"][4]["annual_loss_weekly_roll_usd"]),
                      ("P1 CAT K3 Radau 0.20 1s", "1{,}011{,}405{,}564", p1_cat["rows"][5]["annual_loss_weekly_1s_usd"]),
                      ("P1 disc OOS delta_r2", "-1.089", p1_oos["delta_r2_tagged_vs_price_only_pts"]),
                      ("P1 disc OOS cw_t", "0.96", p1_oos["clark_west_t"]),
                      ("P1 state OOS P1 delta_r2", "+50.728", p1_state_oos["primary_1_cohort_divergence_30m"]["delta_r2_pts"]),
                      ("P1 state OOS P1 cw_t", "21.27", p1_state_oos["primary_1_cohort_divergence_30m"]["clark_west_t"]),
                      ("P1 state OOS P2 delta_r2", "+50.404", p1_state_oos["primary_2_top_trader_state_30m"]["delta_r2_pts"]),
                      ("P1 state OOS P2 cw_t", "21.85", p1_state_oos["primary_2_top_trader_state_30m"]["clark_west_t"]),
                      ("P1 state OOS S1 delta_r2", "+37.639", p1_state_oos["secondary_all_5m_bars"]["cohort_divergence_30m"]["delta_r2_pts"]),
                      ("P1 state OOS S2 delta_r2", "+46.593", p1_state_oos["secondary_all_5m_bars"]["top_trader_state_30m"]["delta_r2_pts"])]:
    num_key = float(key.replace("{,}", ""))
    ok = abs(num_key - val) < 0.0051 and key in t_p1; checked += 1; bad += not ok
    print(f"{'OK ' if ok else 'BAD'} {lab:26s} printed {key} json {val:.4f}")

print(f"\n{checked} numbers checked, {bad} mismatches")
sys.exit(1 if bad else 0)
