# Paper 1: proofs added on 11-12 November 2026, checklist for the authors

The AI-use disclosure says the authors have verified all proofs. These proofs were written by an AI system on
11-12 November and are not yet covered by that statement. Each line says where the proof is, what is machine-checked,
what is checked numerically, and the step a reader should check by hand. Core = `ceiling_suite/papers/paper1_core`.

| Result | Proof | Machine-checked | Numerical check | Check by hand |
|---|---|---|---|---|
| Theorem `thm:anypop` (any population) | core `src/sat.tex` | (i), (ii) in full for any flow map (`Paper1GeneralIdentification.lean`, `p1_flow_market_invariance`) | steering probe recovers a nonlinear switching flow to 2e-16 | (iii): the transfer of lower bounds to a larger class, and the band-linear embedding with large capacities |
| Theorem `thm:partial` (partial disclosure) | core `src/sup_tail.tex` | (i) in full on joint price and tagged-flow records (`Paper1PartialDisclosureLower.lean`); algebra of (ii), (iii) | KL slopes 10.05/6.02/5.96 vs 10/6/6; estimator slopes -5.07/-3.02/0.36 vs -5/-3/0 | (ii): tagged estimates have Delta-eta-free O_P(N^-1/2) error (uses the proof of `thm:discvalue`); Prony stability with K' nodes |
| Theorem `thm:pool` (pooling markets) | core `src/sup_tail.tex` | lower bound on joint records for any matched pair; explicit pair for K = D = 2; counting (`Paper1PoolingLower.lean`, `Paper1PoolingMarkets.lean`) | rank condition exact for K <= 8; Jacobian slopes in 60 digits; estimator slopes -3.02/-1.98/-4.92/-2.95 vs -3/-2/-5/-3; global search finds no collision at separated configurations | (i): constant-rank step giving matched pairs; (ii): minimum-distance estimator; (iv): the two orders l_c and l_g |
| Proposition `prop:noisystress` | core `src/supp_noisystress.tex` | none (rests on `thm:satident`) | parameter error 0.24 -> 0.0009 as N goes 1 -> 65,536 | uniform convergence of Q_N and the compactness argument |
| Proposition `prop:nearcrit` | core `src/supp_nearcrit.tex` | none | ratio KL/(Delta eta)^(4K-2) bounded; finite-sample ratio 0.978-0.998 | |D_A| >= c(eps + |omega|) by primitivity, uniformly in Delta-eta, and the Whittle bound |
| Hiding with several groups (`prop:hiding` remark) | core `src/sup_tail.tex` | none | none | best-response argument given others' rules |
| Section 4: saturating traders (`thm:satsuff`, `thm:stress`, `thm:satident`, `prop:smooth`, `prop:delever`, `prop:dealers`) | core `src/sat.tex`, `src/supp_sat.tex` | pathwise parts of `thm:satsuff`, `thm:stress`(i), `prop:delever`; `thm:satident` for any number of traders and both shapes (`Paper1SaturatingSufficiency.lean`, `Paper1StressIdentificationGeneral.lean`) | example gaps, kink recovery, first-tap coefficient | `thm:stress`(ii)-(iv): the coupling and the Gaussian tail bound; `prop:smooth`: the constant C_D; `thm:satident`(ii) small probes and (iii) both halves |
| Lemma `lem:everyK`, Proposition `prop:targetK` | core `src/supp_everyK.tex` | counting step of (iii) (`Paper1EveryKHalt.lean`) | K = 2..200 | (i) Christoffel weights; (ii) quasi-orthogonal zeros |
| Restored results (general memory, spectral blindness, primitives, capital, CRB, policy) | full working paper, verbatim | as listed in the machine-check table | as in the full paper | these were in the 5 November paper; re-read only if not already verified |

A first line-by-line pass by the AI system found five gaps and fixed them (`PROOF_CHECK_20261112.md`); it is not
independent verification.

All numerical checks: `python3 research_extension/theorem_checks/run_all_checks.py` (17 checks, all pass on
12 November 2026), or the Colab notebook `research_extension/theorem_checks/Paper1_Theorem_Checks_Colab.ipynb`,
which also builds the whole Lean project with the Mathlib cache and writes the formal-verification receipt.

When the authors have checked these, the disclosure sentence stands as written. Until then it should say which
proofs the authors have verified.
