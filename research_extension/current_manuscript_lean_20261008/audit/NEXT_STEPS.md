# Paper 1 formalization: next steps (status PARTIAL)

Baseline: Lean `leanprover/lean4:v4.34.1`, Mathlib `d13f23b723b8a846827a245b89c10fc7d3f11612`, package
`current_manuscript_lean`, default target `CurrentProofs`. This container cannot fetch the Mathlib cache
(`cache.mathlib.org` and `release.lean-lang.org` are blocked by its proxy), so every build below ran in the PR's GitHub
Actions job "Lean 4 Formal Mechanization Audit". That job runs `lake exe cache get`, `lake build`,
`lake env lean AxiomAudit.lean` and `verify_formalization.py`. The pass/fail record for each commit is in `BUILD_LOG.md`.

Status words follow the handoff: unlocated, statement-only, conditional-support, special-case-checked,
model-theorem-checked, reviewed. Nothing is marked "reviewed": no human specialist has reviewed this work.

## Package C: Gaussian Cramér–Rao (Proposition S7.1)

Done:
- `p1_thm_gaussian_hcr`: the Hammersley–Chapman–Robbins inequality for the Gaussian record. It holds for every L²
  statistic.
- `p1_thm_gaussian_cramer_rao`: `Var_θ₀(T) ≥ σ_h²[(JᵀJ)⁻¹]_kk` for every L² statistic that is unbiased near θ₀, given
  line-differentiability with Jacobian J. The route is HCR followed by a limit along a line, so no regularity condition
  and no differentiation under the integral are needed.
- `p1_impulse_differentiable`, `p1_thm_cramer_rao_actual`: the actual closed-loop response is differentiable in
  θ = (q, rate), and the bound holds with J its true Jacobian (`fderiv`).
- `p1_rawJac_gram`, `p1_thm_cramer_rao_raw_actual`: the bound holds on all N·T raw reset records, not only their
  average. The raw Gram matrix is `N V² JᵀJ`, which gives `σ_p²[(JᵀJ)⁻¹]_kk/(N V²) = σ_h²[(JᵀJ)⁻¹]_kk`.

C4 DONE (7 Nov 2026, CI 42347257874): `p1_prop_S7_1_iii`, `p1_prop_S7_1_iii_two` and `p1_prop_S7_1_iii_eta` give `c d⁻⁶ ≤ [(JᵀJ)⁻¹]_kk ≤ C d⁻⁶` for both weights, fixed `T ≥ 4`. Remaining: a `T`-uniform constant (Parseval route, using `Paper1CRScalingH`). Next package: Proposition 6.1 (IV CLT, steps I1–I9), then Theorem 5.5 (W targets).

Historical note on C4: the size of the actual `[(JᵀJ)⁻¹]_kk`, i.e. two-sided bounds `c d⁻⁶ ≤ [(JᵀJ)⁻¹]_kk ≤ C d⁻⁶`
for the weight coordinate. This needs a fixed horizon, at least 4 informative taps, and a compact stable family.
- Route: factor J = (∂h/∂moments)·(∂moments/∂θ). The second factor is the confluent Vandermonde, whose inverse row is
  computed exactly in `SpectralCapital.lean`.
- Missing: uniform conditioning of the moment-to-tap map on the compact family, and the transfer of the diagonal
  entry through that factorization. A smallest-singular-value bound gives only the upper bound.
- Intended signature:
  `theorem p1_crb_diag_two_sided (K := 2) ... : ∃ c C d₀ > 0, ∀ d ∈ Ioo 0 d₀, c * d^(-6) ≤ ((J d)ᵀ * J d)⁻¹ k k ∧ ... ≤ C * d^(-6)`.

## Package S: general-K spectral identification (Theorem 5.4)

Audit finding: the earlier "spectral factorization" (`p1_thm_minphase_spectral_factorization`) covers K = 2 only, and
its hypothesis equates the numerator polynomials, not the spectrum. That is the shortcut the handoff rejects. It is now
superseded.

Done (`Paper1SpectralID.lean`, `Paper1SpectralH.lean`; full green CI run 42325228369). Every result starts
from equal spectra `s₁|H₁(e^{iω})|²/(2π) = s₂|H₂(e^{iω})|²/(2π)` at every ω, for any K₁, K₂.
- `p1_thm_minphase_spectrum_rates`: the sets of memory rates coincide.
- `p1_thm_minphase_spectrum_H`: `s₁κ₁² = s₂κ₂²`, `∏(z - r₁ᵢ) = ∏(z - r₂ᵢ)` and the denominators of `H` coincide.
  Together these give equal `H/h₀`.
- `p1_thm_minphase_spectrum_merged`: with κ known, `s₁ = s₂`, `a₁ = a₂`, the rates coincide, and `w₁ᵢ = w₂ⱼ` whenever
  `r₁ᵢ = r₂ⱼ`.
- Method:
  - the polynomial identity on the circle extends to all of ℂ;
  - root multiplicities balance in the punctured disk;
  - coprimality, which follows from `p1_thm_minphase_zeros`, separates numerator and denominator;
  - monic complex polynomials with equal multiplicities are equal.

Remaining model links, neither of which is a hypothesis about the conclusion:
- (S1) Prove that the z-transform of the recursion's impulse response (`actualCohortImpulse`) equals
  `tfTop/tfBottom`. The rational function is the paper's stated formula and is not re-derived from recursion (1)–(6).
  First lemma: `∑ k, (tfBottom a κ w r).coeff k * actualCohortImpulse a κ q rate (n + k) = 0` for `n ≥ 1`, with
  `w_i = q_i η_i` and `r_i = 1 - η_i`.
- (S2) Prove that "zeros of `tfBottom` in the open disk" is equivalent to the companion matrix having spectral radius
  below 1.

## Package I: stationary IV limit (Proposition 6.1)

Status: two pieces are done, but neither is the limit theorem. The reset-experiment analogue is a different experiment.
- The determinant bound (conditional-support).
- I3, the exact boundary decomposition (`p1_iv_boundary_decomposition`; algebra only).

Infrastructure checked in the pinned Mathlib:
- Present: i.i.d. CLT `tendstoInDistribution_inv_sqrt_mul_sum`; Lévy continuity
  `tendstoInDistribution_iff_tendsto_charFun`; Cramér–Wold `tendstoInDistribution_iff_tendstoInDistribution_inner`;
  Slutsky `TendstoInDistribution.prodMk_of_tendstoInMeasure_const`; von Neumann mean ergodic
  `ContinuousLinearMap.tendsto_birkhoffAverage_orthogonalProjection`; `iIndepFun_pi`; `variance_sum_pi`.
- Absent: a Lindeberg or martingale CLT; any LLN for stationary linear processes.

Route decision: the conditional characteristic-function route (handoff I4). It uses only Lévy continuity and
Cramér–Wold, which are present.

First unresolved lemma (I4a): a weighted-sum CLT for i.i.d. finite-variance errors with deterministic triangular
weights satisfying Lindeberg-type conditions.
```lean
theorem p1_weighted_iid_clt {ε : Ω → ℕ → ℝ} (hiid : iIndepFun ...) (hmean : ...) (hvar : ...)
    (c : ℕ → ℕ → ℝ) (hQ : Tendsto (fun T => (∑ t < T, c T t ^ 2) / T) atTop (𝓝 q))
    (hmax : Tendsto (fun T => (⨆ t < T, |c T t|) / √T) atTop (𝓝 0)) :
    TendstoInDistribution (fun T ω => (∑ t < T, c T t * ε ω t) / √T) atTop (fun _ => gaussian 0 (σ² q)) P
```
- Needs the second-order characteristic-function expansion `|φ(u) - 1 + σ²u²/2| ≤ u² ε(u)`, with ε → 0, from finite
  variance alone. Mathlib's `charFun` Taylor lemmas need checking at the pinned commit.
- After that: I4b (condition on the price path through a product-space/Fubini construction); I1 (L²-convergent causal
  series with finite-memory truncation); I2 (`Σ̂_T → Σ` in probability); I3 (the boundary identity); I5 (assembly).

## Package W: stationary Gaussian divergence rates (Theorem 5.5)

Status:
- Finite-record parts (i) and (iii): special-case-checked. They hold for records from rest after any warm-up. Part
  (iii) uses a binomial pair, not Gauss/Gauss–Radau.
- Part (ii): unlocated.
- `D = Θ(ε²)` and the Stein/Chernoff exponents: unlocated or statement-only.

First unresolved lemma (W1): the finite-record KL between centred multivariate Gaussians with general covariance.
- `Mathlib/Probability/Distributions/Gaussian/Multivariate.lean` exists but has no `klDiv` formula.
- Route: whiten by a Cholesky factor, then reduce to the existing `p1_kl_triangular_gaussian` and the product KL.
  This needs `KL(N(0,Σ₁)‖N(0,Σ₀)) = ½[tr(Σ₀⁻¹Σ₁) - T + log det Σ₀ - log det Σ₁]`.

Bridge from rest to stationary for the finite-record bound (W5):
- The existing bound is uniform in the warm-up M. Lower semicontinuity of `klDiv` under weak convergence as M → ∞
  would transfer it to the stationary law.
- Lower semicontinuity of `klDiv` under weak convergence is not in the pinned Mathlib.

W2 (entropy-rate limit):
- No Toeplitz or Szegő theory in Mathlib, so prefer the rational innovations route (handoff Route B).
- The first obligation is the finite-past prediction-error convergence for stable rational filters.

## Release checks (R)

- `verify_formalization.py` asserts no `sorry`/`admit`/`native_decide`/`axiom` in any module, and that every named
  theorem's axioms ⊆ {propext, Classical.choice, Quot.sound}. CI runs it.
- `audit/coverage.tsv` lists exact declaration names.
- Independent human review: outstanding.


## Update, 7 November 2026 (evening)

- **Package S model links S1 and S2: done earlier** in `Paper1ModelLink.lean` (CI 42340738038):
  - `p1_eigen_iff_bottom_root`;
  - `p1_schur_stable_iff_poles_in_disk`;
  - the generating-function identity for the recursion's impulse response.

  The "Remaining model links" paragraph above is superseded.
- **Equilibrium section:**
  - `Paper1EquilibriumInvariance.lean` (Theorem 4.5);
  - `Paper1InventoryEquilibrium.lean` (Theorem 4.1 core);
  - `Paper1EquilibriumReducedForm.lean` (Theorem 4.2 pathwise identity and realization; fragility bounds);
  - `Paper1EquilibriumExtras.lean`: multi-cohort stability core, Theorem 4.1 necessity, S28.1(i) optimum and value,
    S28.2(iii).
- **Still open, with the reason:**
  - **Package I** (stationary IV CLT): Mathlib has no Lindeberg or martingale CLT.
  - **The T-uniform constant for S7.1(iii)**: the Parseval route needs uniform conditioning on the compact family.
  - **Theorem 4.1(iv)**: the implicit function theorem in Banach spaces; feasible but long.
  - **The Perron–Frobenius step of Theorem 4.4(iv)**: Mathlib has no Perron–Frobenius theorem for nonnegative
    matrices.
  - **The O(d³) kernel bound of S28.2(i)**: a finite Taylor argument; feasible.
- **CI.** GitHub Actions stopped starting jobs on 7 November at about 23:29 UTC, because of a billing error on the
  account. `Paper1EquilibriumExtras.lean` was therefore built locally from source: Lean v4.34.1, the pinned Mathlib,
  1,056 jobs, no errors, no `sorry`, and every new theorem uses only `propext`, `Classical.choice` and `Quot.sound`.
