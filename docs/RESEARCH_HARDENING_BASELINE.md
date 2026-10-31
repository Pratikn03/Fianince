# Machine Markets — Research Hardening Baseline Audit (`RESEARCH_HARDENING_BASELINE.md`)

**Audit Timestamp:** 2026-10-21  
**Repository:** `Pratikn03/Fianince`  
**Starting Git HEAD:** `94dc1511d5de13f6d6bd1b81f1100554e08a85cd` (`main` and `paper2-information-safety`)  
**Relevant Git Tags:** `v1.0-master-release`, `preregistration-768panel-20261004`  
**Working Tree Status at Audit Start:** Clean (`0` uncommitted files)

---

## 1. Authoritative Manuscript Locations & Build Pipeline

| Manuscript Version | Authoritative Source Files | Build Script / Command | Delivered PDF Path | Current Page Count & Layout Status |
| :--- | :--- | :--- | :--- | :--- |
| **Paper 1 (Working Paper)**<br>*Auditable Memory and Financial Identification Limits in Electronic Limit Order Books* | Modular sources in `ceiling_suite/papers/paper1/`:<br>`p1_front.tex`, `p1_ident.tex`, `p1_account.tex`, `p1_mixture.tex`, `p1_disclosure.tex`, `p1_empirics.tex`, `p1_appendix.tex` concatenated into `ceiling_suite/papers/paper1/paper1.tex` (mirrored in `ceiling_suite/paper1/`) | `sh ceiling_suite/papers/build_p1.sh` | `ceiling_suite/papers/pdf_delivered/paper1.pdf` (and `Paper1_working.pdf`) | 90 pages, `0 Overfull \hbox`, `0 Undefined references` |
| **Paper 1 (*Quantitative Economics* Format)** | Generated programmatically from `ceiling_suite/papers/paper1/p1_*.tex` into `ceiling_suite/papers/versions/Paper1_QE.tex` | `python3 ceiling_suite/papers/versions/build_versions.py` | `ceiling_suite/papers/pdf_delivered/Paper1_QE.pdf` | 73 pages total (45-page main text + 4 pages references + 23-page Online Supplement `S-1`–`S-23`), `0 Overfull \hbox` |
| **Paper 2 (Working Paper)**<br>*From Human Markets to Machine Markets: Transient Amplification, an Exact Depth Condition, and a Maximal Pre-Trade Guard* | Modular sources in `ceiling_suite/papers/paper2/`:<br>`p2_front.tex`, `p2_theory1.tex`, `p2_t6.tex`, `p2_infosafety.tex`, `p2_guard.tex`, `p2_disclosure.tex`, `p2_equil.tex`, `p2_evidence.tex`, `p2_thin.tex`, `p2_istests.tex`, `p2_close.tex`, `p2_appendix.tex` concatenated into `ceiling_suite/papers/paper2/paper2.tex` (mirrored in `ceiling_suite/paper2/`) | `sh ceiling_suite/papers/build_p2.sh` | `ceiling_suite/papers/pdf_delivered/paper2.pdf` (and `Paper2_working.pdf`) | 130 pages, `0 Overfull \hbox`, `0 Undefined references` |
| **Paper 2 (*Journal of Finance* Format)** | Generated programmatically from `ceiling_suite/papers/paper2/p2_*.tex` into `ceiling_suite/papers/versions/Paper2_JF.tex` | `python3 ceiling_suite/papers/versions/build_versions.py` | `ceiling_suite/papers/pdf_delivered/Paper2_JF.pdf` | 110 pages total (50-page main text + 5 pages references + 53-page Internet Appendix `IA-1`–`IA-53`), `0 Overfull \hbox` |
| **Legacy Unified Submission Manuscript** | `paper/Machine_Markets_JF_Submission.tex` (with `paper/generated/claim_to_code_map.tex`) | `python3 scripts/verify_theorem_code_bridge.py && pdflatex Machine_Markets_JF_Submission.tex` | `paper/Machine_Markets_JF_Submission.pdf` | Maintained for legacy CI theorem-to-code bridge compatibility (23 environments `S01`–`S23`) |

---

## 2. Theorem Inventory & Existing Proof / Formalization Status

### 2.1 Lean 4 Formalization Inventory
- **Primary Real-Analysis Formalization (`research_extension/current_manuscript_lean_20261008/`)**:
  - Toolchain: `leanprover/lean4:v4.34.1` + Mathlib (`d13f23b7`).
  - **571 named declarations** across 56 modules (445 manuscript, 75 thesis, 51 Paper 1 additions of 31 Oct 2026) in `CurrentProofs/`.
  - Strict axiom audit (`AxiomAudit.lean` and `verify_formalization.py`): `0 sorry`, `0 admit`, `0 native_decide`, standard foundations only (`propext`, `Classical.choice`, `Quot.sound`).
  - Explicit machine-readable flag in `formal_verification_receipt.json`: `"complete": false` (passing Lean compilation certifies the formal declarations under their stated hypotheses, not complete semantic formalization of every manuscript theorem).
- **Constructive Rational Formalization (`lean_proofs/`)**:
  - Toolchain: `leanprover/lean4:v4.34.1` (no Mathlib, over `Rat`).
  - **401 audited declarations** in namespace `MachineMarkets` (`0 sorry`).
- **Ceiling Suite Environment Mapping (`ceiling_suite/verify_ceiling_suite_lean_proofs.py`)**:
  - Maps **26 formal environments in Paper 1** + **28 formal environments in Paper 2** + **3 Foundational Bridge theorems** = **57 mapped items** to kernel-checked Lean declarations.

### 2.2 Breakdown of Proof Status Across the 54 Manuscript Environments
- **Paper 1 (26 environments)**:
  - **Full semantic formalization in Lean (`full`)**: 9 environments (`lem:micro`, `lem:cm`, `thm:quantity`, `lem:toeplitz`, `thm:cap`, `prop:disclosure`, `thm:capital`, `thm:adaptive`, `thm:abstain`, `prop:passive0` — 10 rows total).
  - **Conditional formalization in Lean + analytical proof on paper (`conditional`)**: 5 environments (`thm:merged`, `thm:spectral`, `thm:rh`, `prop:crb`, `prop:tagged`).
  - **Arithmetic / scalar core in Lean + analytical proof on paper (`arithmetic`)**: 11 environments (`prop:tri`, `cor:garch`, `thm:twocohort`, `thm:kcohort`, `prop:esprit`, `lem:altpair`, `thm:general`, `thm:minphase`, `prop:passive`, `thm:discvalue`, `thm:blind`).
- **Paper 2 (28 environments)**:
  - **Full semantic formalization in Lean (`full`)**: 13 environments (`prop:jury`, `prop:invariance`, `prop:ambig`, `prop:multi`, `thm:sum`, `ex:witness`, `prop:twoworld`, `thm:guard`, `lem:sound`, `prop:venue`, `thm:forward`, `prop:dominance`, `prop:equil`).
  - **Conditional formalization in Lean + analytical proof on paper (`conditional`)**: 13 environments (`thm:radius`, `thm:peak`, `thm:window`, `lem:certnum`, `thm:certcost`, `prop:hotelling`, `lem:tail`, `thm:robust`, `thm:robustguard`, `thm:venuebb`, `prop:lucas`, `thm:disclosure`, `prop:probe`).
  - **Analytical proof on paper + inequality/algebraic core in Lean**: 2 environments (`prop:inventory_S`, `prop:driftguard`, added to `InfoSafetyExtensions.lean` and `lean_proofs/Proofs/CeilingSuitePaper2.lean` in commit `61bf6d1`; `COVERAGE.md` must be updated from 26 to 28 environments to reflect them).

---

## 3. Experimental & Empirical Evidence Inventory

### 3.1 Data-Free Simulation & Numerical Verification Suite
- **Information–Safety Suite (`ceiling_suite/papers/research_extension/information_safety/`)**:
  - 28 unit tests (`pytest tests`) + 18 reproducible experiments (`T01_witness` through `T15_disclosure_intersection` and `ThmB_window`), verified byte-for-byte against `results_archived/` in `reproduce_clean.sh`.
- **Paper 1 Recomputed Simulation/Calibration Scripts (`ceiling_suite/papers/`)**:
  - `recompute_p1_learners.py` $\to$ `recomputed/R_P1_learners.json`
  - `recompute_p1_cat_costs.py` $\to$ `recomputed/R_P1_cat_disclosure_dollars.json`
- **Paper 2 & Bridge Recomputed Simulation Scripts**:
  - `ceiling_suite/bridge/bridge_check.py` (Parts A–F)
  - `ceiling_suite/bridge/microfoundation_and_baselines.py`
  - `ceiling_suite/papers/recompute_p2_step2_theory.py` $\to$ `recomputed/R_P2_step2_theory.json`

### 3.2 Real-Data & Pre-Registered Empirical Suite
- **Paper 1**:
  - 96-date, 8-pair Binance spot 10s panel (6.63M bars) & 72-date BTCUSDT 1s panel (6.2M bars): clock-alignment and mechanical EMA persistence diagnostics (`Table tab:panel`, `tab:assets`, `tab:feedback`).
  - Zero-fee natural experiment on BTCUSDT spot (`Table tab:fee2`): null effect on reduced-form feedback ($\Delta\hat Q = -0.00016$, $p=0.650$).
  - CFTC Commitments of Traders pre-registered test across 8 futures markets (`Table tab:cot`): all 8 pass interval-ratio criterion ($9.1\times$–$71.4\times$).
  - Pre-registered OOS 30-min post-shock signed return forecast (`P1_disclosure_oos.json`, SHA-256 `f0182ce5`): **FAIL** ($\Delta R^2 = -1.089\text{ pts}$, $t=0.96$).
  - Pre-registered OOS 30-min post-shock cohort-state divergence & top-trader positioning forecast (`P1_disclosure_state_oos.json`, SHA-256 `5136cc6b`): **PASS** ($\Delta R^2 = +50.728\text{ pts}$, $t=21.27$, and $+50.404\text{ pts}$, $t=21.85$).
- **Paper 2**:
  - 25 pre-registered out-of-sample primary tests in `Table tab:alltests` (**15 pass, 9 fail, 1 not tested**), verified by `ceiling_suite/papers/verify_paper_numbers.py` (`74 numbers checked, 0 mismatches`).
  - 3 non-hash-registered advance-specified analyses in Parts 19–21 (`recompute_p2_parts19_20_21.py`).
  - 2 pre-registered 22nd-of-month tests in Parts 22–23 (`recompute_prereg_oct21_22nd.py`: Part 22 OI liquidation mediation **FAIL**; Part 23 uncapped 18h capacity **FAIL**).
  - 2 pre-registered 2nd-and-9th-of-month tests in Parts 24–25 (`recompute_prereg_oct21_followup.py`: Part 24 capped Rule 15c3-5 throttle **PASS** on both primaries; Part 25 persistence forecast **PASS** on Primary 1, **FAIL** on Primary 2 placebo clause).

---

## 4. Reproducibility & CI Status at Baseline

- **Latest GitHub Actions Run (`39690518423` on `94dc151`)**: All 5 jobs passing (`✓ Code Quality & Linting`, `✓ Lean 4 Formal Mechanization Audit`, `✓ Paper Suite Clean Reproduction`, `✓ Pytest Suite`, `✓ Compile Master Publication PDF`).
- **Missing Data Dependencies & Skipped Tests**:
  - Raw tick/kline archives for historical Binance/Bybit/Coinbase/polygon panels are not stored in Git due to size; pre-computed summary JSONs in `ceiling_suite/papers/results_archive/` are committed, and 2024–2026 Binance kline/positioning data for Parts 19–25 are fetched on demand from `data.binance.vision` (cached locally in `/tmp/binance_oct21_cache`).
  - In `pytest tests/`, 14 tests are skipped when optional external tick files or heavy GPU artifacts are absent (documented in Phase 9).
  - Running `tests/test_institutional_hardening.py` locally when `torch` is installed calls `run_institutional_clearing_simulation(n_replications=50, seed=12345)`, which overwrites `results/provenance/institutional_sacr_results.json` unless `save_results=False` is passed.

---

## 5. Known Scientific Errors & Priority-Zero Blockers Identified in This Audit

### Blocker P0-A (Phase 3 — Trained-Learner Checkpoint Bypass in `recompute_p1_learners.py`)
- **Finding**: In `ceiling_suite/papers/recompute_p1_learners.py`, `burn_in_cohort()` trains `theta_rls`, `theta_mlp`, and `theta_q` over $T_{\mathrm{burn}}=5{,}000$ steps and returns `b_info`, but `probe_settled_population()` **never receives `b_info`**—it initializes `gains = np.ones(K, dtype=float)` and uses `W_in * dphi_0` instead of `theta_mlp`. Thus, Panel B of Table `tab:learners` evaluated unit-normalized post-burn-in policies rather than the actual trained parameter checkpoints. Furthermore, `q_profit_trained` is a scalar stochastic gradient ascent rule on immediate quadratic profit rather than a Bellman Q-learner.
- **Required Fix**: Refactor learner state into a serializable checkpoint with SHA-256 verification; evaluate both (i) **actual frozen trained checkpoints** (without unit-gain replacement), (ii) **explicitly unit-normalized tangent policies**, and (iii) **continuing online adaptation during probing**; and add a genuine tabular Bellman Q-learner alongside the profit-gradient learner.

### Blocker P0-B (Phase 4 — Exposure Reduction & Test-Sample Calibration in Part 24 `P24`)
- **Finding**:
  1. In `recompute_prereg_oct21_followup.py` (Part 24), `raw_c = raw_vol * raw_grd` multiplies two numbers in $(0,1]$, reducing average admitted notional from $\$874{,}562$ (`vol_cap`) to $\$697{,}509$ (`vol_plus_guard`, a $-20.2\%$ exposure reduction). Comparing unscaled `(c)` vs. `(b)` conflates information efficiency with simple exposure reduction.
  2. In `matched_notional()` (lines 381–389), the scale factor `c_vg` was chosen using `mae_te` (realized **test-sample** excursions) and allowed multipliers $>1$.
  3. Crossing `q_t * MAE_day >= 450 bp` is a stylized two-sided excursion threshold crossing, not an observed exchange forced liquidation.
- **Required Fix**: Preserve the original registered Part 24 results untouched, rename the event accurately as a *modeled excursion-buffer breach*, and implement a strictly **training-calibrated** fair benchmark suite (`GUARD_FAIR_BENCHMARKS.md`) comparing all 6 policies at matched training-calibrated exposure, matched training-calibrated risk, across the full risk–capacity frontier, and under directional long/short mark-to-market accounting with fees and funding.

### Blocker P0-C (Phase 5 — Information-Set Mismatch in `P1_disclosure_state_oos`)
- **Finding**: In `P1_disclosure_state_oos`, the baseline `pf_cols` omits current trader-class positioning (`nt_t, na_t, div_t`), whereas `tag_cols` includes them to forecast `div_{t+6}` and `nt_{t+6}` 30 minutes ahead. Because positioning levels are highly persistent, most of the $+50.7\text{ pt}$ / $+50.4\text{ pt}$ $\Delta R^2$ comes from observing the current level $y_t$ (level persistence) rather than multi-cohort memory filtering.
- **Required Fix**: Preserve the registered `P1_disclosure_state_oos` result untouched, and run a complete same-information benchmark hierarchy (Random Walk $\hat y_{t+6}=y_t$, AR(1), AR(3), ARX, and structural cohort-memory model) to decompose level-observation value vs. dynamic memory-filtering value (`DISCLOSURE_INFORMATION_VALUE_AUDIT.md`).

### Blocker P0-D (Phase 6 — Contemporaneous Path-Norm Overlap in Part 25 `P25`)
- **Finding**: In `P25_persistence_mechanism`, `M_ckpt` (mean $|p_f|$ at 15, 30, 45, 60 min) and `M_l1` (mean $|p_f|$ over 1..60 min) are computed over the **exact same future 60-minute price path** `p_f` as `MAE_60 = max(|p_f|)`. Conditioning `MAE_60` on `M_ckpt` or `M_l1` measures contemporaneous correlation between the $\ell_1$ and $\ell_\infty$ norms of the same future trajectory rather than sequential causal mediation.
- **Required Fix**: Preserve the registered Part 25 results untouched, replace causal mechanism claims with accurate statistical descriptions, and test a strictly non-overlapping sequential decomposition (early-window displacement $[0,15\text{m}]$ predicting subsequent late-window excursion $[15\text{m},60\text{m}]$) in `ECONOMIC_MECHANISM_VALIDATION.md`.

### Blocker P0-E (Phase 1 & 2 — Proof Status & Novelty Precision)
- **Finding**: `COVERAGE.md` still lists 26 Paper 2 environments and 443 declarations (needs update to 28 environments and 445 declarations), and `simulations/institutional_sacr_clearing_engine.py` overwrites `results/provenance/institutional_sacr_results.json` when called from `tests/test_institutional_hardening.py`. Furthermore, the exact boundary between inherited classical mathematics (Le Cam two-point bounds, Prony/Vandermonde conditioning, Markov–Krein bounds, $\ell_\infty \to \ell_\infty$ induced gain $\|h\|_1$) and the new finance-specific contributions must be documented rigorously.

---

## 6. Completed Tasks vs. Immediate Execution Plan

- **Completed**: Phase 0 repository and baseline audit (`docs/RESEARCH_HARDENING_BASELINE.md`).
- **Next Actions (Executing Now)**:
  1. **Phase 1 & 2**: Execute independent high-precision mathematical verification (`ceiling_suite/papers/independent_math_audit.py`) and produce `docs/CENTRAL_THEOREM_PROOF_AUDIT.md`; update `COVERAGE.md` and fix `institutional_sacr_clearing_engine.py` test side-effect.
  2. **Phase 3**: Implement checkpoint-verified trained-learner experiments (`ceiling_suite/papers/validate_trained_learners_hardened.py`) and produce `docs/TRAINED_AGENT_VALIDATION.md`.
  3. **Phase 4, 5, 6**: Execute fair training-calibrated guard benchmarks, same-information disclosure benchmarks, and non-overlapping persistence/mechanism audits (`ceiling_suite/papers/hardened_empirical_audits.py`), producing `docs/GUARD_FAIR_BENCHMARKS.md`, `docs/DISCLOSURE_INFORMATION_VALUE_AUDIT.md`, and `docs/ECONOMIC_MECHANISM_VALIDATION.md`.
  4. **Phase 7**: Produce `docs/NOVELTY_AND_NEAREST_LITERATURE.md`, `docs/PAPER1_CONTRIBUTION_MEMO.md`, and `docs/PAPER2_CONTRIBUTION_MEMO.md`.
  5. **Phase 8 & 9**: Reconcile Paper 1 and Paper 2 manuscripts, rebuild all 4 PDFs, run all verification/test suites, and produce `docs/MANUSCRIPT_CLAIM_RECONCILIATION.md` and `docs/FINAL_REPRODUCIBILITY_AND_PDF_AUDIT.md`.
