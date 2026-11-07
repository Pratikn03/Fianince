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
- `p1_thm_gaussian_hcr` (`Paper1GaussianHCR.lean`): the Hammersley–Chapman–Robbins inequality for the Gaussian record.
- `p1_thm_gaussian_cramer_rao` (`Paper1GaussianCR.lean`): `Var_θ₀(T) ≥ σ_h² [(JᵀJ)⁻¹]_kk`. It holds for every `L²`
  statistic that is unbiased on a neighbourhood of θ₀. The mean map `h` is abstract and must be differentiable
  along lines with Jacobian `J`.
- Route choice: HCR followed by a limit along a line. This avoids differentiating under the integral, so the
  theorem needs no "regular estimator" condition at all.

First unresolved lemma (C-inst): the actual averaged response map is differentiable along lines.
```lean
theorem p1_actual_response_hasDerivAt {K T : ℕ} (a κ : ℝ) (θ0 a' : Fin (2 * K) → ℝ) (t : Fin T) :
    HasDerivAt (fun s : ℝ => actualCohortImpulse a κ (weights (θ0 + s • a')) (rates (θ0 + s • a')) t)
      (∑ j, a' j * partialImpulse a κ θ0 t j) 0
```
- Prerequisites: `actualCohortImpulse` is a finite recursion (`p1_impulse_closed_loop_recursion`), so each tap is a
  polynomial in the parameters. Proof by induction on `t`, using `HasDerivAt.mul`, `HasDerivAt.sum` and `pow`.
- Still to define: `weights`, `rates` and `partialImpulse`.

C4 (inverse-sixth scaling of the actual `[(JᵀJ)⁻¹]_kk`) remains conditional-support:
- Needed: two-sided bounds `c d⁻⁶ ≤ [(JᵀJ)⁻¹]_kk ≤ C d⁻⁶` for the weight coordinate, with fixed horizon, ≥ 4
  informative taps and a compact stable family.
- Route: J = (∂h/∂moments)·(∂moments/∂θ). The first factor is uniformly well conditioned on the compact family. The
  second is the confluent Vandermonde already computed exactly in `SpectralCapital.lean`.
- Missing: the uniform conditioning of the first factor, and the transfer of the diagonal entry under that
  factorization.

Raw-record reduction (all N·T reset observations, not only their average):
- The CR theorem already applies to any Gaussian record.
- Missing: the stacked Gram identity `J_rawᵀ J_raw = N V² JᵀJ` under the `Fin (N*T)` indexing (`finProdFinEquiv`).

## Package S: general-K spectral identification (Theorem 5.4)

Audit finding: the earlier "spectral factorization" (`p1_thm_minphase_spectral_factorization`) covers K = 2 only. Its
hypothesis equates the numerator polynomials, not the spectrum. That is exactly the shortcut the handoff rejects, so
it is recorded as conditional-support.

New (`Paper1SpectralID.lean`), pending CI: `p1_thm_minphase_spectrum_rates`.
- It starts from equal spectra `s₁|H₁(e^{iω})|²/(2π) = s₂|H₂(e^{iω})|²/(2π)` at every ω.
- It holds for any K₁, K₂, anchors, impacts, weights and innovation variances.
- It concludes `Set.range r₁ = Set.range r₂`.
- Method: the polynomial identity on the circle extends to all of ℂ; reversed polynomials vanish only outside the
  disk; there is no cancellation.

First unresolved lemma (S-B: the spectrum fixes `sκ²` and `H/h₀`):
```lean
theorem p1_spectral_multiplicity (n1 d1 n2 d2 : ℝ[X]) ... (α : ℂ) (hα : ‖α‖ < 1) (hα0 : α ≠ 0) :
    rootMultiplicity α (n1.map φ) + rootMultiplicity α (d2.map φ) =
      rootMultiplicity α (n2.map φ) + rootMultiplicity α (d1.map φ)
```
- Route: take `rootMultiplicity` of `L = R` (`Polynomial.rootMultiplicity_mul`). The reversed factors have
  multiplicity 0 at α (`p1_rev_ne_zero`). Coprimality then splits the equation. Both sides split over ℂ
  (`IsAlgClosed.splits`), which gives `n1 = c n2` and `d1 = d2` (monic).
- Then `H₁ = c H₂`. With `h₀ = κ` known this gives `H₁ = H₂`, and `p1_cor_unknown_primitives_identification` /
  `thm:merged` gives the merged measure.
- Also open: link the stability hypothesis "zeros of `tfBottom` inside the disk" to the paper's definition of a
  stable economy (spectral radius of the companion matrix below 1).

## Package I: stationary IV limit (Proposition 6.1)

Status: determinant bound only, as conditional-support. The reset-experiment analogue is a different experiment.

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
