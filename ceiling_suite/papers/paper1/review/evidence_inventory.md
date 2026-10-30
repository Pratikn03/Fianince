# Paper 1 — evidence inventory, dispositions and coverage (plan of 30 Oct, Phases 1 and 5)

Generated from `build_run_inventory.py` (per-file list in `run_inventory.csv`, totals in
`run_inventory_summary.md`). The repository holds **4,429 JSON result files in 18 collections**; 819 of them are
Lean/Mathlib build artifacts (`.lake/`), not results. The authoritative manuscript is
`ceiling_suite/papers/paper1/paper1.tex`; every PDF is built from it.

## 1. Classification

| Class | Files | Meaning |
|---|---|---|
| cited-P1 | 76 | Named in Paper 1 or in a Paper 1 row of `EXPERIMENT_MANIFEST.csv` |
| P1-topic, not cited | 69 (about 20 genuine after removing name-pattern false matches) | Candidates for reanalysis |
| Paper 2 or thesis | 150 | Cited by Paper 2 or the thesis |
| Unclassified | 4,134 (3,315 excluding Lean build files) | Mostly legacy and extension studies; dispositions by folder below |

## 2. Dispositions by collection

| Collection (files) | What it is | Disposition for Paper 1 |
|---|---|---|
| `ceiling_suite/recomputed`, `papers/recomputed`, `theory`, `papers/hardening` (69) | Recomputations behind Paper 1's tables | **Directly supports**; cited |
| `p11res` (4) | Registered CFTC test | **Directly supports**; cited |
| `results_archive/realres` (37) | Parts 1–2 theorem checks and spot tests | Supports; P1.x and R2-x files cited. `R2-T5_merged_invariance` (same measure 3.5e−18, different 3.3e−3) supports C1 and is now listed below |
| `results_archive/p6res`, `p1_disc_oos_res`, `p1_disc_state_res` | Binance fresh-day and out-of-sample tests | **Directly supports**; cited (Z6, OOS) |
| `results_archive/outputs/p10res` (890) and `p7res`, `p12res`–`p18res` | Bybit order book, guard, equities, venues | **Paper 2**; preserved there |
| `studies/hidden_slow_learners`, `studies/full_horizon_audit` (30) | Finite-horizon witnesses: stable and unstable markets with identical early responses | **Valid, mainly thesis / Paper 2** (finite-window monitoring). Possible one-sentence cross-reference in Paper 1's limits on finite records; not incorporated |
| `studies/information_decision_20261029`, `finite_horizon_costs_20261029` (26) | Source of the finite-horizon decision appendix | **Supports the SSRN appendix**; see gap G3 |
| `studies/advanced_cost_separation_20261029`, `advanced_results_revision_20261030` (29) | Cost-aware separation, guard comparisons | **Paper 2** (kept separate by instruction) |
| `studies/audited_constraints`, `observable_stress_tests`, `economic_review`, `next_stage_validation` | Guard, stress and economic reviews | **Paper 2 / thesis** |
| `research_extension/outputs` (1,824) and other `research_extension` folders | September–October extension work (deep RL, hardware, flash crash, gap closure, information safety) | **Not Paper 1.** Some folders were withdrawn on 3 Oct; none is cited; no reanalysis planned |
| `thesis/evidence`, `thesis/checks` (102) | Thesis tests (B1–B3, C1–C3, F1, G1, K1, H1, …) | **Thesis**; not Paper 1 evidence |

## 3. Coverage matrix (headline claims × evidence)

P = proof, X = exact/numerical identity check, S = simulation, E = estimator comparison, R = real data,
F = failure or boundary diagnostic. "Range" lists what has actually been varied.

| Claim | P | X | S | E | R | F | Range covered | Gaps |
|---|---|---|---|---|---|---|---|---|
| C1 merged measure | ✓ | ✓ R2-T5, phase7, Hankel rank | ✓ Test A (5 rules, 4 learners) | – | – | ✓ dead zones, single-bin lookup | a=0.5, κ=0.8; K≤3 | Other (a, κ) |
| C2 known pair δ^−2, δ^−4 | ✓ | ✓ d₂ (R_audit, P1.7-T1), ledger 5.7e−13 | ✓ exact-error MC (200k paths), 4 protocols, SPRT | – | – | ✓ independent training streams break δ^−4 | one calibration (a=0.5, κ=0.8, q=0.2, η=0.4) | Second calibration |
| C3 constant [61.41, 64.48] | ✓ | ✓ theory constants, rh_explicit | ✓ ledger designs | – | – | – | δ ∈ [0.02, 0.15]; L ≤ 480 | G1 |
| C4 K-group order | ✓ | ✓ Radau gaps to 1e−16 | ✓ Le Cam slopes K=2–4; Prony slopes K=2–5 | ✓ ML, ridge, shrinkage, heavy prior (K=2) | – | – | centres 0.4 and 0.7; one noise level | Estimators for K≥3 |
| C5 general memory | ✓ | ✓ 60-digit moment pairs | ✓ LP estimator | – | – | – | ρ=0.9, one distribution, 20 reps | Other ρ and shapes (cheap reanalysis/run) |
| C6 passive | ✓ (now nonasymptotic) | ✓ min-phase in 1,733 economies; Whittle slopes K=2–4 | ✓ passive pair MC | – | – | – | – | Uniform attainment not claimed |
| C7 tagged flow | ✓ | ✓ IV determinant | ✓ flat RMSE in Δη; disclosure-value slopes | – | positions only | – | r_c 0.95, 0.99 | Tagged *flow* in data |
| C8 disclosure choice | ✓ | ✓ `prop_choice_check` (19,814 cases) | – | – | – | – | random parameters | – |
| C9 CAT dollars | – | ✓ recompute_p1_cat_costs | – | – | SEC filings | – | two noise calibrations, weekly renewal | – |
| C10 CFTC | – | – | – | – | ✓ registered | ✓ H2 failed | 8 markets | Flow-based test (needs approval) |
| C11 Binance | – | – | – | – | ✓ registered | ✓ criterion (iii) failed; near unit root | 30 + 29 markets | – |
| C12 OOS forecasts | – | – | – | – | ✓ registered | ✓ failed | 19 thin perpetuals | – |

## 4. Provenance gaps found

- **G1 (closed).** Table 5 values at L = 320 and 480 lived only in `R_P1_cquadL.json`, with no producing script.
  New `papers/hardening/rh_quad.py` reproduces all six archived values to within 5e−14.
- **G2.** The disclosure-choice check reported earlier (18,346 cases) had no saved script. Recreated as
  `review/prop_choice_check.py`. It found that the word "unimodal" in Proposition `prop:choice`(ii) was wrong for
  the negative tail, where G rises back toward zero from below. Statement and proof corrected; the conclusions
  (interval, threshold M*) are unchanged and pass in all 19,814 cases.
- **G3 (closed).** The SSRN build now adds the finite-horizon appendix's sources (`run.py` → `results/final_full_20261030/`,
  and `validation/`) to the reproducibility map.
- **G4.** Lean: 26 of 34 Paper 1 environments have a *name mapping* to existing declarations; the mapping audit
  says no fresh build and no semantic equivalence. The paper correctly claims no formal verification.
- **G5.** Grid with a memory rate of 1.006 in `theory/disclosure_value.py` (r_c = 0.99). Fixed; paper numbers
  unchanged.

## 5. New runs considered (each must justify itself; none launched)

| Candidate | Claim | Outputs examined | Why reanalysis cannot answer | Cost | Recommendation |
|---|---|---|---|---|---|
| Extend `rh_bound.py` to L = 320, 480 | C3 | `R_P1_rh_explicit`, `R_P1_cquadL` | producer missing | minutes, local | **Done** (`rh_quad.py`) |
| LP estimator at ρ ∈ {0.5, 0.8, 0.95, 0.99}, two more shapes | C5 | `general_minimax` output (ρ = 0.9 only) | only one ρ was run | minutes, local | **Do** if time permits |
| Second calibration for the known-pair tables | C2, C3 | all capital outputs use one calibration | not in any archive | minutes, local | Optional |
| Tagged-flow IV on weekly CFTC class flows | C7, C10 | CFTC position results | positions ≠ flows | needs a registered spec | **Only with your approval**, registered first |
