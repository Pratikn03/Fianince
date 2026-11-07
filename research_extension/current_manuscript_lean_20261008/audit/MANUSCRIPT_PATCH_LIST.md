# Manuscript patch list (formalization status only; no economic claim changes)

1. Prop S7.1 (`prop:crb`). Done in the 6 Nov Phase 0 edit:
   - (i) the variance bound for unbiased estimators, with `T ≥ 2K` and full column rank;
   - (ii) `N_CR` is a benchmark, not a coverage bound;
   - (iii) the Θ(Δη⁻⁶) scaling of the diagonal entry, with attainment from Thm 5.2 stated separately.
   New: say that (i) is machine-checked for the averaged record (`p1_thm_gaussian_cramer_rao`), with no regularity
   condition. Say that (iii) for the actual Jacobian is not machine-checked.
2. Thm 5.4 (`thm:minphase`) (ii). Replace "factorization formal only for two cohorts" with: the spectrum determines
   the set of memory rates for every K (`p1_thm_minphase_spectrum_rates`). The determination of `σ²κ²` and `H/h₀`
   remains written-only.
3. Thm 5.5 (`prop:passive`).
   - Lean covers finite records started from rest after any warm-up, which is not the stationary law.
   - Part (iii) is formal for a binomial moment-matched pair, which is not the Gauss/Gauss–Radau pair.
   - Part (ii) and the Θ divergence rates are written-only.
4. Prop 6.1 (`prop:tagged`). Only the instrument-determinant bound is machine-checked. The stationary LLN/CLT is
   written-only. Keep the corrected (Phase 0) assumptions: whole-process independence, centred errors, causal
   solution.
5. Prop S3.2 (`prop:passive0`). The finite-sample midpoint-test theorem is machine-checked for the explicit block
   model with general moments (m₄ ≤ 3s²).
6. Lemma S24.4. The converse (pulse test errors and margin solvency) is machine-checked.
