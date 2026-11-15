import CurrentProofs.Paper1MergedModel
import Mathlib.Probability.Distributions.Gaussian.Real
import Mathlib.Probability.Moments.Variance
import Mathlib.Probability.Independence.Basic

/-!
# Paper 1, `prop:tagged` / `thm:discvalue`: class-tagged records remove the spacing barrier (reset experiments)

In a reset experiment the flow of cohort `i` at the first period is `q_i y_{i,0} = q_i η_i κ = w_i κ`: it reveals
the merged weight directly, whatever the other cohorts' memory rates. With `N` independent experiments that record
each class's first-period flow with Gaussian noise of variance `v`, the estimator `ŵ_i = (mean of the records)/κ`
satisfies, by Chebyshev's inequality, `P(|ŵ_i - w_i| ≥ ε) ≤ v / (N κ² ε²)` for every class, and all `K` weights are
within `ε` with probability at least `1 - K v / (N κ² ε²)`. The bound does not involve the memory rates or their
spacing, in contrast with the price-only lower bound `N ≳ σ² (Δη)^-(4K-2)` of `Paper1MatchedPair.lean`.
This is the reset-experiment form of the tagged-flow result; the stationary instrumental-variables version with its
martingale central limit theorem (`prop:tagged` as stated in the paper) is not formalized.
-/

namespace CurrentMM

open MeasureTheory ProbabilityTheory Finset
open scoped ENNReal NNReal

/-- The first-period flow of a cohort in a unit reset experiment is its merged weight times the impact. -/
theorem p1_tagged_first_flow {n : ℕ} (a impact : ℝ) (q rate : Fin n → ℝ) (i : Fin n) :
    q i * cohortImpulseMemory a impact q rate i 0 = (q i * rate i) * impact := by
  rw [p1_impulse_memory_zero]; ring

/-- Chebyshev for the mean of `N` independent Gaussian records with mean `m` and variance `v`. -/
theorem p1_tagged_mean_chebyshev (N : ℕ) (hN : 0 < N) (m : ℝ) (v : ℝ≥0) (ε : ℝ) (hε : 0 < ε) :
    (Measure.pi fun _ : Fin N => gaussianReal m v) {x | ε ≤ |(∑ i, x i) / N - m|} ≤
      ENNReal.ofReal (v / (N * ε ^ 2)) := by
  set μ : Measure (Fin N → ℝ) := Measure.pi fun _ : Fin N => gaussianReal m v
  have hNpos : (0 : ℝ) < N := by exact_mod_cast hN
  have hcoord : ∀ i : Fin N, MemLp (fun x : Fin N → ℝ => x i) 2 μ := fun i =>
    (memLp_id_gaussianReal 2).comp_measurePreserving (measurePreserving_eval _ i)
  have hfun : (fun x : Fin N → ℝ => ∑ i, x i) = ∑ i, fun x : Fin N → ℝ => x i := by
    funext x; simp
  have hS : MemLp (fun x : Fin N → ℝ => ∑ i, x i) 2 μ := by
    rw [hfun]; exact memLp_finsetSum' _ (fun i _ => hcoord i)
  have hvar : variance (fun x : Fin N → ℝ => ∑ i, x i) μ = N * v := by
    have h := variance_sum_pi (μ := fun _ : Fin N => gaussianReal m v) (X := fun _ => id)
      (fun _ => memLp_id_gaussianReal 2)
    simp only [id, variance_id_gaussianReal, sum_const, card_univ, Fintype.card_fin, nsmul_eq_mul] at h
    rw [hfun]; exact h
  have hmean : μ[fun x : Fin N → ℝ => ∑ i, x i] = N * m := by
    rw [integral_finsetSum _ (fun i _ => (hcoord i).integrable one_le_two)]
    have : ∀ i : Fin N, ∫ x, x i ∂μ = m := fun i => by
      have hm := measurePreserving_eval (fun _ : Fin N => gaussianReal m v) i
      have h := integral_map (μ := μ) (φ := Function.eval i) (f := fun y : ℝ => y)
        (measurable_pi_apply i).aemeasurable aestronglyMeasurable_id
      rw [hm.map_eq, integral_id_gaussianReal] at h
      exact h.symm
    simp [this]
  have hset : {x : Fin N → ℝ | ε ≤ |(∑ i, x i) / N - m|} =
      {x | N * ε ≤ |(fun x : Fin N → ℝ => ∑ i, x i) x - μ[fun x : Fin N → ℝ => ∑ i, x i]|} := by
    ext x
    simp only [Set.mem_ofPred_eq, hmean]
    have e : (∑ i, x i) / N - m = ((∑ i, x i) - N * m) / N := by field_simp
    rw [e, abs_div, abs_of_pos hNpos, le_div_iff₀ hNpos, mul_comm]
  rw [hset]
  refine le_trans (meas_ge_le_variance_div_sq hS (by positivity)) ?_
  rw [hvar]
  apply ENNReal.ofReal_le_ofReal
  rw [div_le_div_iff₀ (by positivity) (by positivity)]
  ring_nf; exact le_refl _

/-- **Tagged weight recovery for one class.** With `N` reset experiments recording the class's first-period flow
`w κ` with Gaussian noise of variance `v`, the estimator `(mean)/κ` misses `w` by `ε` or more with probability at
most `v / (N κ² ε²)`, whatever the memory rates. -/
theorem p1_tagged_weight_recovery (N : ℕ) (hN : 0 < N) (w κ : ℝ) (hκ : κ ≠ 0) (v : ℝ≥0) (ε : ℝ)
    (hε : 0 < ε) :
    (Measure.pi fun _ : Fin N => gaussianReal (w * κ) v) {x | ε ≤ |(∑ i, x i) / N / κ - w|} ≤
      ENNReal.ofReal (v / (N * κ ^ 2 * ε ^ 2)) := by
  have hk : 0 < |κ| := abs_pos.mpr hκ
  have hset : {x : Fin N → ℝ | ε ≤ |(∑ i, x i) / N / κ - w|} =
      {x | ε * |κ| ≤ |(∑ i, x i) / N - w * κ|} := by
    ext x
    simp only [Set.mem_ofPred_eq]
    have e : (∑ i, x i) / N / κ - w = ((∑ i, x i) / N - w * κ) / κ := by field_simp
    rw [e, abs_div, le_div_iff₀ hk]
  rw [hset]
  refine le_trans (p1_tagged_mean_chebyshev N hN (w * κ) v (ε * |κ|) (by positivity)) ?_
  apply le_of_eq
  congr 1
  rw [mul_pow, sq_abs]; ring

/-- **All `K` merged weights at once (union bound).** Records of every class in `N` reset experiments, with
independent Gaussian noise of variance `v`: all `K` estimators are within `ε` of the merged weights `q_i η_i` except
on an event of probability at most `K v / (N κ² ε²)`, for every cohort economy, whatever its memory rates. -/
theorem p1_thm_tagged_recovery_all_classes {K : ℕ} (N : ℕ) (hN : 0 < N) (a κ : ℝ) (hκ : κ ≠ 0)
    (q rate : Fin K → ℝ) (v : ℝ≥0) (ε : ℝ) (hε : 0 < ε) :
    (Measure.pi fun i : Fin K => Measure.pi fun _ : Fin N =>
        gaussianReal (q i * cohortImpulseMemory a κ q rate i 0) v)
      (⋃ i : Fin K, {x : Fin K → Fin N → ℝ | ε ≤ |(∑ e, x i e) / N / κ - q i * rate i|}) ≤
      K * ENNReal.ofReal (v / (N * κ ^ 2 * ε ^ 2)) := by
  set μ := Measure.pi fun i : Fin K => Measure.pi fun _ : Fin N =>
    gaussianReal (q i * cohortImpulseMemory a κ q rate i 0) v
  refine le_trans (measure_iUnion_fintype_le μ _) ?_
  have hi : ∀ i : Fin K, μ {x : Fin K → Fin N → ℝ | ε ≤ |(∑ e, x i e) / N / κ - q i * rate i|} ≤
      ENNReal.ofReal (v / (N * κ ^ 2 * ε ^ 2)) := by
    intro i
    have hmeas : MeasurableSet {y : Fin N → ℝ | ε ≤ |(∑ e, y e) / N / κ - q i * rate i|} :=
      measurableSet_le measurable_const (by fun_prop)
    have hpre : {x : Fin K → Fin N → ℝ | ε ≤ |(∑ e, x i e) / N / κ - q i * rate i|} =
        (fun x : Fin K → Fin N → ℝ => x i) ⁻¹' {y | ε ≤ |(∑ e, y e) / N / κ - q i * rate i|} := rfl
    rw [hpre, (measurePreserving_eval _ i).measure_preimage hmeas.nullMeasurableSet,
      p1_tagged_first_flow]
    exact p1_tagged_weight_recovery N hN (q i * rate i) κ hκ v ε hε
  calc ∑ i : Fin K, μ {x : Fin K → Fin N → ℝ | ε ≤ |(∑ e, x i e) / N / κ - q i * rate i|}
      ≤ ∑ _i : Fin K, ENNReal.ofReal (v / (N * κ ^ 2 * ε ^ 2)) := sum_le_sum (fun i _ => hi i)
    _ = K * ENNReal.ofReal (v / (N * κ ^ 2 * ε ^ 2)) := by simp

end CurrentMM
