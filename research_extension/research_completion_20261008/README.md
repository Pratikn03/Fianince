# October 9 proof and evidence delivery

The current review exports are `Machine_Markets_JF_Submission_ProofEvidence_20261009.pdf` (54 pages) and `Machine_Markets_Proof_Evidence_Update_20261009.pdf`. The existing open report source remains `Machine_Markets_Proof_Evidence_Update_20261008.tex`, edited in place and checked with the native compiler. Earlier frozen releases and ZIPs remain preserved.

The current strict Lean audit checks 150 named mathematical declarations. Twelve new sequence-account results establish the dealer account identity, adverse quadratic bound, necessary and sufficient nonnegative quantity allowance for a nonincreasing kernel, its root form and every partial last fill. The kernel's nonincreasing property remains an explicit precondition: composition with the actual physical cohort kernel is unfinished. The full residual list remains in `../current_manuscript_lean_20261008/MANUSCRIPT_COVERAGE.md`, with every object assigned to Codex. Counts are intermediate declarations, not full theorem coverage.

Independent checks pass for 458 main-manuscript fields; 11 supplement tables/243 rows/1,575 cells; author/source-recovery prose; annual/equivalence calculations; all 93,558 scalar displayed-book sweeps; 17 pooled metrics/12 daily summaries; and 12 new numeric manuscript/report fields. The signed-system native verifier previously streamed all original CSV rows and checked every selected minute book. Its receipt is preserved in the October 8 delivery record. The Python independent verifier now also passes. Neither arithmetic agreement nor Lean establishes causal identification, real fills, data rights or novelty.

## Reproduce the current checks

From the project root:

```sh
cd research_extension/current_manuscript_lean_20261008
COPYFILE_DISABLE=1 python3.11 verify_formalization.py
```

From this completion directory:

```sh
python3.11 verify_completion_evidence.py
/usr/bin/perl verify_manuscript_fields.pl
```

From `../gap_closure_20261006/publication_completion/`:

```sh
python3.11 verify_current_empirical.py
python3.11 verify_evidence_supplement.py
python3.11 submission_completion/verify_source_recovery_prose.py
```

T9 data caches and the pinned Lean/mathlib runtime are required. These are existing checks, not new training. The amendment bundle contains sources, PDFs and audit receipts; it does not redistribute private Gemini histories or large source datasets.

## Remaining work

Gaussian minimax/testing, induced L2 gain, the actual positive spectral kernel, Kalman conditional filtering, realization, passive-excitation testing, capacity/Jury, Kreiss/networks and the carried-state gate remain AI proof work. Actual trade/position/funding/margin records, historical calibration authentication and independent specialist assessment remain external inputs. No publication, push, reviewer message or new submission was made.
