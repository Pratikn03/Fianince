# Paper 1 — internal adversarial review (30 October 2026)

Two passes: (1) a line-by-line audit with computations by the AI assistant that helped write the paper;
(2) a second review in a fresh context that saw only the PDF and source text, none of the project's notes
(section 3). Neither is independent review; see `REVIEWER_GUIDE.md`.

Severity: **CRITICAL** = a central result false or unproven; **MAJOR** = a stated result needed a correction or
an added assumption; **MINOR** = wording, constants, references.

## 1. Findings from the line-by-line audit

| # | Severity | Result | Problem | Evidence | Fix (status) |
|---|---|---|---|---|---|
| 1 | MAJOR | resolvent identity (3 places) | H₁ − H₀ = H₁H₀ΔG missed a factor z⁻¹; the passive theorem's non-vanishing step used the wrong function | `phase7_checks.json`: error 1e−3 without z⁻¹, 4e−16 with | fixed; bounds unchanged since \|z\| = 1 |
| 2 | MAJOR | `prop:choice`(ii) | "G is unimodal" is false: in the negative tail G rises back toward zero | `prop_choice_check.json`: 9,229 of 19,814 cases violate whole-domain unimodality, 0 violate the corrected statement | statement and proof corrected; conclusions unchanged |
| 3 | MAJOR | `prop:passive` | sample lower bound relied on KL_T = TD + O(1), not shown uniform in the separation; attainment claimed uniformly | derivation | nonasymptotic Toeplitz bound KL_T ≤ C·T·ε²; attainment stated pointwise only; Gaussian assumptions stated |
| 4 | MAJOR | abstract, introduction, tables | dollar bounds read as applying to any observer; tagging saving compressed to one exponent; passive "same order" claimed as attained | consistency check | scoped to the probing observer; both savings stated; passive claims lower-bound only |
| 5 | MINOR | text after `thm:uniformw1` | "impossible as rates collide, at any sample size" mixes non-identification with cost | — | rewritten |
| 6 | MINOR | proof of `thm:uniformw1` | Lipschitz step holds only near the class; small-N case unaddressed | — | note added (bound trivial after enlarging C) |
| 7 | MINOR (priority) | `prop:esprit` | Katz, Diab and Batenkov (2023) show Prony attains the min-max bound for clustered exponents; the paper's upper bound adapts this | literature search | cited in text and in the comparison table; contribution restated as an adaptation |
| 8 | MINOR | `thm:merged`(ii) | constant K clashed with the number of cohorts | — | renamed C_F |
| 9 | MINOR | results map | CAT-budget row contradicted its table | table 16 | fixed |
| 10 | MINOR | code | grid put a memory rate at 1.006 (`disclosure_value.py`) | — | grid restricted; paper numbers unchanged |
| 11 | MINOR | provenance | Table 5 rows L = 320, 480 had no producing script; finite-horizon appendix missing from the map | — | `hardening/rh_quad.py` reproduces all six values to 5e−14; map rows added |

## 2. Checked and found correct (audit)
- `thm:merged`: transfer function from (1)–(2), partial fractions, no cancellation, degree for a > 0 and a = 0;
  (ii) bound including the ΔG formula and |ΔG| ≤ 2qδ²/ε³ (re-derived symbolically).
- `thm:quantity`: d₂ = −κ²qδ²; exact minimax error and pulse attainment; quantity bound from (10).
- `thm:cap`: every entry of A_t ≤ κ/2 (the off-diagonal bound uses monotonicity of h); nonnegative probes give
  vᵀA_tv ≤ (κ/2)U_t².
- `thm:capital`: coercivity constant m = κ(1 − r)/(1 + r); KL and Pinsker steps.
- `thm:spectral`: Toeplitz symbol 2Re H − κ; Parseval bound. `thm:adaptive`: pathwise Parseval bound and the
  factor kl(0.05, 0.95)/(2z²) = 0.4897.
- `thm:kcohort`: Gauss and Gauss–Radau moments; response-difference orders 2.98, 5.02, 7.05, 9.07 against
  3, 5, 7, 9 for K = 2–5 (`edge_case_search.json`); positive Radau weights.
- `prop:esprit`: Lipschitz kernel map, confluent Vandermonde determinant, Δη-scaling of the moment errors.
- `thm:general`: full line-by-line check of both bounds (Jackson constant, Chebyshev coefficient bound
  B(ρ)^{L+1}, kernel-recovery Neumann series, choice of L, Le Cam/Bretagnolle–Huber step, c* = 1/4).
- `prop:tagged`: IV moment matrix, determinant formula, long-run variance with MA(1) errors.
- `lem:micro`: Kalman gain formula. `lem:cm`: nonnegative, nonincreasing response with peak κ and
  Re H ≥ κ/2 in 3,000 random positive economies, also at a = 0 (`edge_case_search.json`).
- Finite-horizon appendix `fhc:pair`: moment structure (first two moments match, third differs by 1.5δ³).
- Citations: Tsybakov (2009) Lemma 2.6 and Theorem 2.2; Wu and Yang (2020) rate n^{−1/(4k−2)} and moment
  comparison; Bernstein's constant 0.2802 (Varga and Carpenter 1985).

## 3. Fresh-context second review
(added when it completes)
