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
    ("Leverage interaction, 19 thin", lambda: [p19["primary_1_interaction"]["beta_C3_x_high_LEV_bps"]] + p19["primary_1_interaction"]["beta_C3_x_high_LEV_ci"], 3),
    ("Spot vs.\\ perp $\\Delta R^2$, 19 thin", lambda: [p19["primary_2_spot_comparison"]["delta_r2_spot_pts"]] + p19["primary_2_spot_comparison"]["delta_r2_spot_ci_pts"], 3),
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
                      ("P19 perp delta_r2", "+6.50", p19["primary_1_interaction"]["delta_r2_perp_pts"]),
                      ("P19 spot delta_r2", "+0.99", p19["primary_2_spot_comparison"]["delta_r2_spot_pts"]),
                      ("P19 spot/perp ratio", "0.152", p19["primary_2_spot_comparison"]["ratio_spot_to_perp"]),
                      ("P20 pooled spot kappa", "-0.243", p20["by_event"]["spot_zero_fee_pooled"]["impact_kappa_hat"]["beta"]),
                      ("P21 part15 (c)-(b) saving", "398", p21["part15_untouched_days"]["c_vs_b_es95_saving_usd"]),
                      ("P21 part16 (c)-(b) saving", "2{,}557", p21["part16_untouched_symbols"]["c_vs_b_es95_saving_usd"])]:
    num_key = float(key.replace("{,}", ""))
    ok = abs(num_key - val) < 0.0051 and key in t16; checked += 1; bad += not ok
    print(f"{'OK ' if ok else 'BAD'} {lab:24s} printed {key} json {val:.4f}")
print(f"\n{checked} numbers checked, {bad} mismatches")
sys.exit(1 if bad else 0)
