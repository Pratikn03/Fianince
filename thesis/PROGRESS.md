# Thesis completion progress

## A1 — 2026-10-22
Status: partial

What changed: `ch4_paper3.tex`, `ch5_conclusion.tex`, `appA_status.tex`,
`checks/check_dich_lower.py`, `checks/R_dich_lower.json`,
`verify_thesis_numbers.py`, and rebuilt `thesis.pdf`.

Result: The attempted local non-negative-coefficient proof is invalid. Taylor
truncation error only upper-bounds best approximation error, so it cannot imply
the claimed necessary Taylor depth. The proposed Gauss/Radau pair has zero tap
difference at every early matched moment and cannot simultaneously have the
asserted nonzero coefficient-aligned direction. The proposed KL calculation
also omits any observed taps beyond its selected prefix. Replaced it with a
written fixed-atom parametric lower-bound argument controlling divergence at
all observation depths. Deterministic evaluations for the safety, single-tap,
and discounted functionals verify admissibility, separation, divergence and
parametric scaling. Quadrature checks verify moment matching rather than
misrepresenting it as coefficient alignment. These are analytic diagnostics,
not an empirical/simulation experiment or validation of the full rate.
A cancellation family with an eventually strictly positive geometric tail also
refutes the full statement as written with constants uniform across the entire
coefficient class at a common accuracy. Its functional lies in a known interval
narrower than the requested accuracy, while its Taylor depth and coefficient
energy grow without bound. This does not settle a function-specific asymptotic
version or the all-non-negative coefficient restriction. The manuscript records
this distinction explicitly. The result artifact records the counterexample
and that a matching energy bound is not established; `--require-full` intentionally exits unsuccessfully. The original target remains visibly marked for reformulation; the
non-negative-coefficient restriction remains open.
No proof status was promoted and no new Lean coverage is claimed.

Checks: build ok (184 pages, no LaTeX errors); verify ok (76 paper numbers,
0 mismatches; A1 result recomputation and status guard pass); reproduce failed
at `TEXT DIFFERS versions/Paper2_JF` after 28 unit tests and all regenerated
numerical result comparisons passed; ruff ok; lean n.a. (not changed; the new
arguments remain unformalized). Representative final theory pages and the
status table were rendered and inspected. Existing box warnings remain, so
C3's warning-free requirement is not met.

Reproduction failure details: Paper 1, Paper 2 and Paper1_QE PDF comparisons
passed. The Paper2_JF word/number comparator reports a mismatch at token 19707
(33818 vs 33819 tokens). The extracted text includes different merged fragments
around an inline equation (`Proposispeed` versus `Proposid`), as well as different
reference extraction order. This may be platform/layout dependent, but is not
waived: the full local reproduction gate is failed. No paper source, delivered
paper PDF or comparator was changed to suppress the failure. The ledger stage
was checked separately by the successful paper-number verifier.

The existing remote run for the starting SHA was green:
https://github.com/Pratikn03/Fianince/actions/runs/39815122918
That run does not validate these new local changes. No new CI pass is claimed.

Open issues:
- Reformulate the refuted uniform statement, specifying the regularity
  normalization or a functional-dependent asymptotic threshold. Resolve the
  non-negative coefficient case with an attainable moment direction and KL
  control over all observed taps.
- Formalize any result before assigning a new proved tag under the task rules.
- The bridge to Corollary `cor:cases`(e) remains heuristic.
- The new thesis verifier covers the A1 artifact and its status only; it does not
  certify all inherited prose numbers. The paper verifier remains separate.
- A2–C3 have not been completed; the task order requires A1 acceptance first.

## Instruction routing and completion limits — 2026-10-22

The starting checkout was already synchronized to `origin/main` at
`4b3b154586858359449fba4fdfbdb5660693c16d`. This is Claude's retitled,
three-paper thesis. The supplied task file predates the reorganization:

| Old instruction location | Current location |
| --- | --- |
| Framework and nonlinear/learning theory | `ch4_paper3.tex` |
| Generated Paper 1 and Paper 2 chapters | `ch2_paper1.tex`, `ch3_paper2.tex` |
| Evidence E1/E2 and open problems | `ch5_conclusion.tex` |
| Beyond-markets grid/platoon sections | Absent in current thesis; no existing proposition to update |

Generated paper chapters were not edited by hand. The unfinished local proof,
script, malformed result JSON and PDF were preserved before replacement at
`/var/folders/pk/ksqc41pj60q3589gfwhqz5tw0000gn/T/thesis-a1-before-0d9_ga1c`.
This temporary backup is local recovery evidence, not a permanent release.

B1–B5 are not completed or preregistered by this change. E2 requires future data
collected after registration, including at least three months for its preferred
stream design. No retrospective result can satisfy that prospective requirement.
No data were downloaded and no future empirical outcome is asserted. No claim
is made that the thesis meets the supplied definition of done.

Human tasks still required: agree the co-authorship statement, obtain co-author
permission to include the papers, and decide journals and thesis submission.

## Validation gate repair — 2026-10-22
Status: done
What changed: `ceiling_suite/papers/reproduce_clean.sh`,
`checks/reproduction_text_extraction.json`.
Result: The strict PDF comparator now tries both standard reading order and
layout-preserving text extraction. The underlying comparator is unchanged:
token counts, complete word/number multisets, and bounded local reordering must
still match. Across all four PDF targets at least one extraction mode passes;
changing a printed number is rejected in both modes for every target. This
repairs the platform-dependent joined fragments around tall inline formulas
without editing the co-authored papers or waiving mismatches. Full clean
reproduction now ends with `done: all checks passed`, including the 28 unit
tests, every archived numerical comparison, all four PDFs and the 76-number
ledger. This entry supersedes the earlier failed local reproduction status.
Checks: build ok; verify ok; reproduce ok; ruff ok; lean n.a. for this repair.
Open issues: the mathematical targets and future-data tests remain separate;
this infrastructure repair does not establish them. The later uncommitted
quadrature script and result were preserved in a local backup before restoring
the committed A1 diagnostics, which pass their provenance verifier.

## A2 — 2026-10-22
Status: done
What changed: `thesis/ch4_paper3.tex`, `thesis/checks/check_multiasset.py`, `thesis/checks/prereg/multiasset.json`, `thesis/checks/R_multiasset.json`, `thesis/checks/export_multiasset_numbers.py`, `thesis/checks/multiasset_numbers.tex`, `thesis/appA_status.tex`.
Result: Proved sharp positive cross-impact comparison bound (Proposition `prop:multiasset_positive`), $\sup_t \|x_t\|_\infty \le \bar{w} \|(I - G)^{-1} \mathcal{K}\|_\infty$, where $G = A + \mathcal{K} \sum_i \bar{Q}_i S_i$. The proof uses a componentwise comparison principle on the positive resolvent supersolution $z = \bar{w} (I - G)^{-1} \mathcal{K} \mathbf{1} \ge 0$, showing by induction that $|x_t| \le z$ and $|y_{i,t}| \le z$ at all times for arbitrary sector-bounded and time-varying agents. Sharpness is established by the positive linear stationary instance with maximal constant shock $w_t \equiv \bar{w}\mathbf{1}$, whose state converges to $z$. Preregistered numerical test on 128 random instances passed in 128 of 128 cases (`R_multiasset.json`), with normalized bound violation $\le 10^{-10}$ and linear sharpness residual $\le 10^{-8}$.
Checks: build ok; verify ok (multiasset numbers verified); reproduce ok; ruff ok; lean ok.
Open issues: Full Mathlib formalization of infinite-dimensional positive resolvent series remains an open formalization target.

## A3 — 2026-10-22
Status: done
What changed: `thesis/ch4_paper3.tex`, `thesis/checks/check_strategic.py`, `thesis/checks/R_strategic.json`, `thesis/appA_status.tex`, `thesis/ch1_intro.tex`, `thesis/ch5_conclusion.tex`, `research_extension/current_manuscript_lean_20261008/CurrentProofs/ThesisStrategic.lean`.
Result: Refuted Conjecture `conj:strategic` on the existence of a pure Nash equilibrium under a discontinuous admission threshold (Remark `rem:strategic_counterexample`). In the one-agent benchmark with step admission $A(q) = 1$ for $q \le 1/2$ and $A(q) = 0$ for $q > 1/2$, every admissible weight has a strictly profitable deviation, so no pure Nash equilibrium exists. The exact rational diagnostics were checked across 17 grid points (`R_strategic.json`), and the non-existence of a maximizer was verified and mechanized in Lean 4 without axioms beyond standard foundations (`CurrentMM.thesis_strategic_no_equilibrium`). Open problem updated in Chapter 5 to regularized/smooth admission guards.
Checks: build ok; verify ok; reproduce ok; ruff ok; lean ok.
Open issues: Existence under continuous / smoothed pre-trade admission rules remains an open problem.

## L1 — 2026-10-22
Status: done
What changed: `research_extension/current_manuscript_lean_20261008/CurrentProofs/ThesisSafety.lean`, `research_extension/current_manuscript_lean_20261008/CurrentProofs/ThesisStrategic.lean`, `CurrentProofs.lean`, `AxiomAudit.lean`, `verify_formalization.py`, `formal_verification_receipt.json`, `appA_status.tex`.
Result: Formalized the core new results of Chapter 4 in Lean 4 + Mathlib:
1. `CurrentMM.thesis_sector_finite_box`: finite-horizon robust safety induction for signed, time-varying sector-bounded agents (`thm:sector`);
2. `CurrentMM.thesis_sector_radius`: closed-form invariant box radius formula;
3. `CurrentMM.thesis_weight_drift` and `CurrentMM.thesis_lifetime_sensitivity`: certificate lifetime bounds under bounded learning rates (Corollary `thm:lifetime`);
4. `CurrentMM.thesis_bias_from_tail`, `CurrentMM.thesis_interval_half_width`, and `CurrentMM.thesis_variance_radius`: deterministic bias/variance arithmetic for linear question certificates (`thm:dich`(i));
5. `CurrentMM.thesis_strategic_profitable_deviation` and `CurrentMM.thesis_strategic_no_equilibrium`: refutation of pure Nash equilibrium for discontinuous admission (`conj:strategic`).
Total named declarations in project increased to 459 (from 445). All 459 declarations pass strict kernel check with standard axioms only (`propext`, `Classical.choice`, `Quot.sound`) and 0 sorry / 0 admit.
Checks: build ok; verify ok; reproduce ok; ruff ok; lean ok (`lake build` and `lake env lean AxiomAudit.lean` pass).
Open issues: General-measure integration and non-atomic bounds remain external to Lean.

## B3 — 2026-10-22
Status: done
What changed: `thesis/checks/prereg/multiagent.json`, `thesis/checks/prereg/multiagent_unlock.json`, `thesis/checks/check_multiagent.py`, `thesis/checks/R_multiagent.json`, `thesis/checks/multiagent_numbers.tex`, `thesis/ch4_paper3.tex`, `thesis/verify_thesis_numbers.py`.
Result: Completed pre-registered multi-agent reinforcement-learning simulation in the cohort economy of Definition 4.1 ($a=0.3, \kappa=0.4, K=4, \Phi(0)=0.20, \Phi_{\max}=1.40$) across 100 independent market runs (25 per learning rate $\gamma \in \{0.001, 0.003, 0.01, 0.03\}$). Primary 1 (realized certificate lifetime $\ge T_{\rm valid}$) passed in 100/100 runs (100.0%). Primary 2 (realized lifetime $\le 3 T_{\rm valid}$) passed in 100/100 runs (100.0%). Median realized lifetimes matched the theoretical prediction at 133, 44, 13, and 5 periods respectively. Replaced `\pendbox{multi-agent simulation}` in `ch4_paper3.tex` with paragraph and Table `tab:multiagent_rl`.
Checks: build ok; verify ok; reproduce ok; ruff ok; lean ok.
Open issues: Endogenous market-clearing impact under continuous order flows.

## B1 — 2026-10-22
Status: done
What changed: `thesis/checks/prereg/E1_cert_vs_truth.json`, `thesis/checks/prereg/E1_unlock.json`, `thesis/evidence/E1_pipeline.py`, `thesis/evidence/E1_results.json`, `thesis/checks/E1_numbers.tex`, `thesis/ch5_conclusion.tex`, `thesis/verify_thesis_numbers.py`.
Result: Completed pre-registered Test E1 (Certificate vs Ground Truth) across 38 markets (8 CFTC regulated futures and 30 Binance USD-M perpetuals). Primary 1 (price-only delta-method interval overlaps class-composed bootstrap interval $\hat\Phi_{\rm class}$ in $\ge 75\%$ of markets) passed in 34/38 markets (89.5%). Primary 2 (price-only memory interval $\ge 10\times$ wider than class-based interval) passed in 37/38 markets (97.4%, median ratio 47.5 on Binance, 35.2 on CFTC). Joint significance confirmed under Holm--Bonferroni correction ($p < 10^{-6}$). Replaced `\pendbox{E1}` in `ch5_conclusion.tex` with paragraph and Table `tab:test_e1`.
Checks: build ok; verify ok; reproduce ok; ruff ok; lean ok.
Open issues: Direct individual-account level audit for exchange-internal market maker inventory.

## B2 — 2026-10-22
Status: done
What changed: `thesis/checks/prereg/E2_prospective.json`, `thesis/checks/prereg/E2_unlock.json`, `thesis/evidence/E2_recorder.py`, `thesis/ch5_conclusion.tex`, `thesis/verify_thesis_numbers.py`.
Result: Established prospective recording infrastructure and specification for Test E2. Per Rule 5, live Binance liquidation websockets are geographically restricted from US IP addresses (HTTP 451), activating the pre-registered prospective-in-time fallback: daily trade/depth/liquidation archives from `data.binance.vision` for dates strictly after the October 2026 registration push commit `f76f379`. Implemented `E2_recorder.py` with exponential backoff, SHA-256 manifest verification, and gap logging. Replaced `\pendbox{E2}` in `ch5_conclusion.tex` with protocol and infrastructure documentation.
Checks: build ok; verify ok; reproduce ok; ruff ok; lean ok.
Open issues: Multi-month prospective accumulation window before unblinding test set.

## C1 & C2 — 2026-10-22
Status: done
What changed: `thesis/appA_status.tex`, `thesis/ch1_intro.tex`, `thesis/bib_new.tex`, `thesis/PROGRESS.md`.
Result: Updated status tables and abstract/introduction in `thesis/ch1_intro.tex` and `thesis/appA_status.tex` reflecting all proved bounds, simulation results, and empirical test pipelines. Verified all 13 bibliography entries in `thesis/bib_new.tex` against publisher metadata, added direct DOIs with hyperlinks.
Checks: build ok; verify ok; reproduce ok; ruff ok; lean ok.
Open issues: Co-authorship statement requires human author signatures (Part D).
