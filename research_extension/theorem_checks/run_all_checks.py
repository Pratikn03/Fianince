"""Re-runs every numerical check cited in Paper 1 and compares each with the value the paper states.
Usage (from the repository root): python3 research_extension/theorem_checks/run_all_checks.py [--slow]
--slow adds the global-fibre search and the two-market worst-case table (about 30-60 minutes).
Prints PASS or FAIL for each claim and writes research_extension/theorem_checks/run_all_checks_results.json."""
import json, os
import numpy as np, os, subprocess, sys, time

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
SLOW = "--slow" in sys.argv
results = []


def run(folder, script):
    t0 = time.time()
    p = subprocess.run([sys.executable, script], cwd=os.path.join(ROOT, folder), capture_output=True, text=True)
    if p.returncode != 0:
        print(p.stdout[-2000:], p.stderr[-2000:])
        raise RuntimeError(f"{folder}/{script} failed")
    print(f"  ran {folder}/{script} in {time.time() - t0:.0f}s", flush=True)


def load(folder, name):
    return json.load(open(os.path.join(ROOT, folder, name)))


def check(claim, ok, detail):
    results.append({"claim": claim, "pass": bool(ok), "detail": detail})
    print(("PASS  " if ok else "FAIL  ") + claim + "  |  " + detail, flush=True)


FR, PD, CM, TC = "research_extension/fragility_reveals", "research_extension/partial_disclosure", \
    "research_extension/cross_market", "research_extension/theorem_checks"

print("1. Near instability: finite-sample information vs n x per-observation rate (prop:nearcrit)")
run(FR, "finite_sample_check.py")
rows = load(FR, "finite_sample_check_results.json")["rows"]
lo, hi = min(r["ratio"] for r in rows), max(r["ratio"] for r in rows)
check("exact KL of n observations lies within 97.8-99.8% of n x rate", 0.977 <= lo and hi <= 1.0, f"range {lo:.4f}-{hi:.4f}")

print("2. Calibration table (Table 1 of the theory version)")
run(FR, "calibration_table.py")
cal = load(FR, "calibration_table_results.json")
rob = {(r["rc"], r["spacing"], r["margin_1_minus_S"]): r["years_daily"] for r in cal["robustness_slower_memory"]}
y1, y2 = rob[(0.9, 0.025, 0.1)], rob[(0.9, 0.025, 1e-6)]
check("half-lives 5-9 days need more than 4,000 years (7,000 at 1-S=0.1; 4,300 at 1e-6)",
      abs(y1 - 7000) / 7000 < 0.05 and abs(y2 - 4300) / 4300 < 0.05, f"{y1:.0f} and {y2:.0f} years")

print("3. Partial disclosure: lower-bound exponents (thm:partial(i))")
run(PD, "partial_disclosure_check.py")
pd = load(PD, "partial_disclosure_check_results.json")
for k, v in pd.items():
    check(f"KL slope {k}", abs(v["slope"] - v["theory"]) < 0.3, f"slope {v['slope']:.2f} vs {v['theory']}")

print("4. Upper bounds by Monte Carlo (thm:partial(ii)-(iii), thm:pool(ii))")
run(TC, "mc_rates.py")
mc = load(TC, "mc_rates_results.json")
for k, v in mc["partial_disclosure"].items():
    tol = 0.6 if v["theory_slope"] == 0 else 0.3
    check(f"partial disclosure weight-error slope {k}", abs(v["slope"] - v["theory_slope"]) < tol, f"{v['slope']:.2f} vs {v['theory_slope']}")
for k, v in mc["pooling"].items():
    check(f"pooling weight-error slope {k}", abs(v["slope"] - v["theory_slope"]) < 0.3, f"{v['slope']:.2f} vs {v['theory_slope']}")

print("5. Pooling markets: exact rank condition (thm:pool(iii)) and high-precision Jacobian slopes")
run(CM, "rank_check_modp.py")
rk = load(CM, "rank_check_modp_results.json")
check("condition (R) holds at l* = K-1+ceil(K/D) for every K <= 8, D <= K", all(v["R_holds_at_lstar"] for v in rk.values()), f"{len(rk)} cases")
run(CM, "jacobian_scan_mp.py")
js = load(CM, "jacobian_scan_mp_results.json")
check("Jacobian smallest singular value scales like d^l* (60-digit arithmetic)",
      all(abs(v["local_slopes"][-1] - v["lstar"]) < 0.1 for v in js.values()),
      ", ".join(f"K,D={k}: {v['local_slopes'][-1]:.2f}/{v['lstar']}" for k, v in js.items()))

print("6. Noisy stress identification and any population (prop:noisystress, thm:anypop)")
run(TC, "mc_stress_and_general.py")
sg = load(TC, "mc_stress_and_general_results.json")
errs = [r["median_param_error"] for r in sg["noisy_stress"]]
check("noisy stress: parameter error falls with N, below 0.002 at N = 65,536", errs[-1] < 0.002 and errs[-1] < errs[0], str([round(e, 4) for e in errs]))
ap = sg["any_population"]
check("any population: steering probe hits the target and recovers the flow map", ap["steer_hits_target_maxerr"] < 1e-12 and ap["flow_recovered_maxerr"] < 1e-12, f"{ap['steer_hits_target_maxerr']:.1e}, {ap['flow_recovered_maxerr']:.1e}")
check("any population: a different flow map departs from the path", ap["other_population_deviates_maxdiff"] > 1e-4, f"{ap['other_population_deviates_maxdiff']:.3g}")

print("6b. Which questions prices answer cheaply (dichotomy)")
run(TC, "mc_questions.py")
mq = load(TC, "mc_questions_results.json")
check("discounted feedback: error flat in the memory spacing (slope within 0.1 of 0)", abs(mq["slope_discounted_feedback"]) < 0.1, f"{mq['slope_discounted_feedback']:.3f}")
check("group weights: error grows like spacing^-3 (slope within 0.1 of -3)", abs(mq["slope_weights"] + 3) < 0.1, f"{mq['slope_weights']:.3f}")

print("6c. Surveillance over time: tracking rates and the hiding game")
TR = os.path.join(ROOT, "research_extension", "tracking")
run(TR, "tracking_check.py")
tr = load(TR, "tracking_check_results.json")
check("tracking: weight error slope in speed within 0.05 of 1/3", abs(tr["slope_weights_v"] - 1 / 3) < 0.05, f"{tr['slope_weights_v']:.3f}")
check("tracking: weight error slope in spacing within 0.1 of -2", abs(tr["slope_weights_d"] + 2) < 0.1, f"{tr['slope_weights_d']:.3f}")
check("tracking: market-wide answer slope in speed within 0.05 of 1/3", abs(tr["slope_feedback_v"] - 1 / 3) < 0.05, f"{tr['slope_feedback_v']:.3f}")
run(TR, "hiding_game_check.py")
hg = load(TR, "hiding_game_check_results.json")
check("hiding game: high-stakes detection stays below false alarm + k D0^2 / L = 0.06", hg["high_stakes_max_detection"] <= 0.06, f"{hg['high_stakes_max_detection']:.4f}")

print("6d. One running market and news of any law")
RN = os.path.join(ROOT, "research_extension", "running")
run(RN, "running_check.py")
rn = load(RN, "running_check_results.json")
for law in ("a_gauss", "a_laplace"):
    check(f"running market ({rn[law]['law']} news): every tap MSE at most the bound of thm:running(i)", rn[law]["max_mse_over_bound"] <= 1.0, f"max MSE/bound {rn[law]['max_mse_over_bound']:.2f}")
for law, v in rn["b"].items():
    check(f"news law {law}: KL ratio at most sigma^2 I* and within 0.02 of sigma^2 I(f)", v["ratio"] <= v["sigma2_Istar"] + 0.01 and abs(v["ratio"] - v["sigma2_Ifisher"]) < 0.02, f"ratio {v['ratio']:.3f}, sigma^2 I = {v['sigma2_Ifisher']:.3f}")

print("6e. Questions left open in earlier versions")
OP = os.path.join(ROOT, "research_extension", "open_problems")
run(OP, "open_checks.py")
op = load(OP, "open_checks_results.json")
check("rank condition (R): block witness has full rank (mod p) for every K <= 12, D <= K", op["A1_witness_full_rank_mod_p_K_le_12"], "")
check("moment gap: 4^K/(K C(2K,K)^2) equals the Gauss-Radau gap (K <= 30) and obeys the pi/4^K bounds (K <= 2000)", op["A3_formula_vs_radau_max_rel_error_K_le_30"] < 1e-30 and op["A3_bounds_hold_K_le_2000"], f"max rel. error {op['A3_formula_vs_radau_max_rel_error_K_le_30']:.1e}")
check("near instability: n-observation divergence within the eigenvalue bound for every budget and n", op["A2_all_within_bound"], "")
check("cascade: continuous below kappa*l = 1, jump above", op["A4_ok"], f"largest jumps {op['A4']['below']['max_jump']:.4f} vs {op['A4']['above']['max_jump']:.2f}")
check("insider: Re H/kappa >= 1/(1+s) and the theta = 1/2 cost form is positive definite", op["A5_ok"], f"min eigenvalue {op['A5_min_eig_theta_half']:.4f}")
check("dead band: tap bias below the bound and falling like 1/A", op["A6_ok"] and abs(op["A6_bias_slope_in_A"] + 1) < 0.05, f"slope {op['A6_bias_slope_in_A']:.2f}")

if SLOW:
    print("7. Pooling markets: global fibres and the two-market worst case (slow)")
    run(CM, "global_fibres.py"); run(CM, "pooling_table.py")
    import itertools
    sols = load(CM, "global_fibres_extended_solutions_upto_4_2.json"); worst = 0.0; ok = True
    for key, cases in sols.items():
        K, D = map(int, key.split(","))
        for c in cases:
            x0 = np.asarray(c["x0"]); gap = float(np.min(np.diff(np.sort(x0[:K]))))
            perms = [np.r_[x0[:K][list(q)], x0[K:].reshape(D, K)[:, list(q)].ravel()] for q in itertools.permutations(range(K))]
            for x in c["at_lstar"] + c["at_lstar_plus_1"]:
                dist = min(float(np.max(np.abs(np.asarray(x) - q))) for q in perms)
                worst = max(worst, dist); ok = ok and gap < 0.04 and dist < 0.06
    check("global search: every apparent other solution sits at nearly coincident nodes (gap < 0.04, distance < 0.06)", ok, f"largest distance {worst:.3f}")
    tab = load(CM, "pooling_table_results.json")
    r = [x for x in tab if x["d"] == 0.025 and x["diversity"] == 0.5][0]
    check("two markets, shares 50 points apart: about 90 years against about 7,000", r["years_two_markets"] < 200 and r["years_one_market"] > 6000, f"{r['years_two_markets']:.0f} vs {r['years_one_market']:.0f}")

json.dump(results, open(os.path.join(ROOT, TC, "run_all_checks_results.json"), "w"), indent=1)
n_fail = sum(not r["pass"] for r in results)
print(f"\n{len(results) - n_fail} of {len(results)} checks passed.")
sys.exit(1 if n_fail else 0)
