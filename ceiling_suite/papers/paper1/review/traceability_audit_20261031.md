# Paper 1 traceability audit (31 October 2026)

Question asked: is anything never saved to GitHub, are main findings buried or errors missed, and is every link
complete: code -> paper, paper -> code, code -> results, results -> paper, results -> Lean?

## 1. What was never saved to GitHub

Method: content hash of every code, result and text file outside the repository (9,643 files in the working
container) against every blob in the repository's history on all branches.

| Found | Count | Disposition |
|---|---|---|
| Real Colab results (`p5res` ... `p13res`, `realres`, `xres`, `depthres`) | 0 missing | All already in the repository |
| Outputs of local smoke tests on **fake data** (`*/run/ceiling_suite_local`, `depth/`, `eq/`, `ceiling_suite_local/`) | ~3,300 | Deliberately not saved: synthetic debug outputs, not results |
| Notebook builders, local runners, fake-data generators, an unlinked Lean 4 port (InfoSafetyLean, Paper 2), older theory scripts | 177 files, 1 MB | Archived in `archive/unsaved_dev_sources_20261031/` with a README |
| Superseded paper drafts (PDF/LaTeX/text extracts) | ~150 | Not saved (superseded) |
| Unpushed commits, stashes, untracked files in the repository | 0 | - |
| Remote branches with work not merged into main | 2 | `codex/thesis-completion-20261022` (4 commits: Paper 3 draft, thesis multi-asset recovery test, Lean `ThesisSafety`, and a recorded incident in which a concurrent writer overwrote a registered runner and archive; it also changes `.github/workflows/ci.yml`) and `codex/thesis-readiness-20261026` (1 commit: thesis reproducibility). Neither touches Paper 1's claims. Merging needs the author's decision, and the CI change needs explicit approval |

No Paper 1 finding exists only outside GitHub.

## 2. Paper -> code and paper -> results

* The reproducibility map had 42 rows; every script and result identifier in it exists in git. Ten rows were added
  in this audit for sources that the map did not name: the CRB and Le Cam columns (earlier runs `exp15`, `exp17`),
  the finite-horizon probes of Table `tab:rh` (`R_P1_capital_ledger.json`, `R_P1_cquadL.json`), the peak margins of
  Table `tab:ledger` (`exp14`), Table `tab:general` (`theory/R_P1_general_minimax.json`), the estimator columns
  (`R_P1_estimators*.json`), `R2-T5` (numerical check of Theorem `thm:merged`), and the three Binance follow-ups
  plus the exploratory 96-lag refit (`thesis/evidence/C2_results.json`, `E1v2_results.json`, `D1_results.json`,
  `pilot3_horizon_matched_results.json`).
* Automated table trace (`review/table_number_trace.py`): every printed number in every table matched against its
  source files at printed precision. Fully matched: `tab:scorecard`, `ledger`, `crb`, `lecam`, `kcohort`, `kupper`,
  `learners`, `cat_dollars`, `panel`, `assets`, `protocols`, `iv`; near-fully: `capbounds`, `general`, `cot`,
  `disc`, `fee2`, `rh`, `contracts`, `target`. Remaining unmatched entries are inputs (grid values, sample sizes,
  dates), derived arithmetic (percent gaps, kappa*q), or closed forms (quadrature nodes, the capital formula).
* Headline numbers checked by hand against result files: 9-71 (CFTC ratios 9.1-71.4), 333 (333.37), 0.49
  (29.94/61.41), 29 of 29 / 7.3 / 2.6 / 1.0008 (C2), 74.9 / 9 / 10 of 30 (E1v2), 22 and 20 of 29 (D1), 7.5 / 25 of
  30 / 5.6 h / 4.2 h (pilot 3), $15M-$356M (14.74M, 356.44M).

**Errors found and fixed**
1. Table `tab:capital` printed 99,193 and 149,902; the exact values (61.41 x (sigma/0.01)^2 x (0.05/delta)^4 at the
   unrounded medians) are 99,192.2 and 149,901.4, as Table `tab:cat_dollars` prints. Corrected.
2. The CFTC return-source note said no CME futures returns were used; crude oil and natural gas do use front-month
   futures. Corrected (in the previous round).

## 3. Code -> results (re-running every offline script)

| Script | Result |
|---|---|
| `disclosure_value`, `targeted_intervention`, `rh_quad`, `recompute_theory`, `recompute_crb`, `recompute_extra`, `recompute_p1_cat_costs`, `recompute_p1_protocols`, `recompute_p1_sprt`, `recompute_audit`, `recompute_oct20`, `p1_checks`, `general_minimax`, `validate_trained_learners_hardened`, `recompute_p1_estimators` | Reproduce the committed results exactly |
| `rh_bound`, `rh_check` | Reproduce to 3e-14 |
| `recompute_p1_capital` (SQP) | Agrees to 0.01 par units (64.48 vs 64.47); probe details within 1%. Re-run saved as `R_P1_capital_ledger_rerun_20261031.json` |
| `kcohort_upper` (seeded) | K = 2, 3, 4 slopes agree (-5.94, -10.00, -13.92 vs -13.93); **K = 5 gives -17.89 here vs -18.34 committed** (numerical-library dependence at extreme N). Table note now reports both. Re-run saved |

Not re-run, by design: `recompute_prereg_oct21_22nd.py`, `recompute_prereg_oct21_followup.py` and
`recompute_p1_learners.py` are the **executors** of pre-specified tests (they download test data and increment test
unlock counters), not offline recomputations. One was started by mistake during this audit; it downloaded nothing
(no network), computed nothing, and its counter was restored. See `incident_20261031_accidental_test_runner_invocation.json`.

Bug fixed: `theory/general_minimax.py` wrote its result to a hard-coded path outside the repository.

## 4. Results -> paper (buried findings)

Of 68 Paper-1-type result files, the ones not named in the paper or map are: superseded intermediate versions
(`R_P1_general_kernel`), test-unlock counters, Paper 2 / thesis results, and `R2-T5_merged_invariance` (now
cited). No uncited result contradicts the paper. Negative results are all reported (scorecard table).

## 5. A structural hazard found and removed

`build_p1.sh` and the clean-reproduction CI rebuilt `paper1.tex` by concatenating seven split files that had not been
updated since 29 October; the Lean label audit and two verifiers also read stale copies. Running `build_p1.sh`
would have silently reverted every change since then, and the CI "clean reproduction" job has failed on every
push since 29 October (first failing run predates this work) with `TEXT DIFFERS paper1/paper1`. Fix: `paper1.tex` is
now the single source; `split_sources.py` regenerates the split files (and the `ceiling_suite/paper1/` mirror)
from it, `build_p1.sh` calls it, the verifiers read `paper1.tex`, and the delivered PDFs were refreshed.

A second stale duplicate, `ceiling_suite/verify_paper_numbers.py`, fails on missing paths; the working verifier
is `ceiling_suite/papers/verify_paper_numbers.py`. Of its 76 checked numbers only 14 are Paper 1's; the table trace
above is the Paper 1 check.

## 6. Results -> Lean

* CI kernel-checks both Lean projects on every push (`lean-formal-audit` job: success).
* The label audit now reads the current paper: 26 of 31 Paper 1 results have a Lean mapping; 5 do not
  (`prop:primitives`, `prop:tied`, `thm:uniformw1`, `prop:choice`, `prop:target`), plus the 5 `fhc:` results of the
  finite-horizon supplement.
* What the mapped declarations prove (`COVERAGE.md`): 9 full (model facts: Kalman/OGD memory, complete
  monotonicity, KL bound for the known pair, Toeplitz execution, cash/margin cap, disclosure mark, capital order,
  finite-window abstention, passive three-step test), 6 conditional (merged equivalence, spectral bound, RH
  duality, CRB, tagged flow, adaptive probing, re-tagged from full because the KL chain rule is a hypothesis), 11
  arithmetic (scalar identities only), including every central rate theorem (`thm:twocohort`, `thm:kcohort`,
  `prop:esprit`, `thm:general`, `thm:minphase`, `prop:passive`, `thm:discvalue`, `thm:blind`).
* So the paper's statement that its proofs are not formally verified is correct and must stay.

## 7. Open items

1. Merge or close the two unmerged thesis branches (author decision; one changes CI).
2. Lean statements for the central rate theorems would be new formalization work.
3. Executors of pre-specified tests should be renamed (`run_*`) so that nobody mistakes them for recomputations.
4. `Paper1_QE` (journal version built by `versions/build_versions.py`) now builds from the current text but has
   overfull lines in the new tables; it needs a layout pass before any journal use.

## 8. Clean-reproduction check after the fixes

Run locally exactly as CI runs it (fresh copy of `ceiling_suite/papers`, fresh virtual environment): unit tests and
all data-free results identical; **`paper1/paper1` IDENTICAL TEXT**. The check then stops at
`TEXT DIFFERS paper2/paper2`: Paper 2's sources were changed on 29 October (by another session) without refreshing
`pdf_delivered/paper2.pdf` ("Development revision" vs the delivered "Revised preprint"). This is Paper 2 content and
was left for the author: either refresh the delivered Paper 2 PDFs to the current source or restore the source.
Also fixed for the check: `paper1.tex` read two development-log files from outside `ceiling_suite/papers`; they are
now copied into `paper1/dev_register/`, and the journal-version builder drops that development log.
