import Mathlib.MeasureTheory.Measure.Real
import Mathlib.MeasureTheory.Measure.Typeclasses.Probability
import Mathlib.Analysis.SpecialFunctions.Sqrt
import Mathlib.Analysis.SpecialFunctions.Exp

/-!
# Paper 1: saturating traders, the probabilistic and cost steps (core `thm:stress`(ii)-(iii), `prop:smooth`)

The pathwise parts of the saturating-trader results are formalized in `Paper1SaturatingSufficiency.lean`
(sufficiency, stress invariance, the linear band) and `Paper1StressIdentificationGeneral.lean` (identification).
This file adds the probabilistic and cost steps:

* `p1_coupling_bound`: if two random paths agree outside an event `B`, the probabilities of any event differ by at
  most `P(B)` (the coupling step of `thm:stress`(ii)-(iii): the populations' paths coincide until some trader leaves
  its band).
* `p1_exit_union_bound`: if each of the `T · n` exit events has probability at most `p`, some exit happens with
  probability at most `T n p` (`thm:stress`(iii)).
* `p1_stress_test_cost`: a test with both errors at most `α` then needs `T ≥ (1 - 2α) / (n p)`; with the Gaussian
  tail `p = e^{-1/(2ϑ²)}` this is the bound `T ≥ (1 - 2α) e^{1/(2ϑ²)} / (n + n')` of the paper.
* `p1_smooth_lower_cost`: if the price responses differ by at most `C_D |A|³` and Pinsker's inequality
  `1 - 2α ≤ √(N ‖e‖² / (4σ²))` holds for a test with both errors at most `α`, then
  `N ≥ 4 σ² (1 - 2α)² / (C_D² A⁶)` (`prop:smooth`(i)).
* `p1_smooth_upper_cost`: if the first-tap gap is at least `κ⁴ |ΔM₃| |A|³ / 6` and
  `N ≥ (12 σ z)² / (κ⁸ ΔM₃² A⁶)`, then the averaged first tap separates the two populations by at least `2 σ z / √N`,
  which is what the midpoint test with error `Φ(-z)` needs (`prop:smooth`(ii)).
The Gaussian tail bound, the computation of the first-tap gap and the bound `‖e‖ ≤ C_D |A|³` are proved on paper.
-/

namespace CurrentMM

open MeasureTheory Finset

/-- **Coupling.** If `X = Y` outside `B`, then `P(X ∈ A) ≤ P(Y ∈ A) + P(B)`. -/
theorem p1_coupling_bound {Ω α : Type*} [MeasurableSpace Ω] (P : Measure Ω) [IsProbabilityMeasure P]
    (X Y : Ω → α) (A : Set α) (B : Set Ω) (hXY : ∀ ω, ω ∉ B → X ω = Y ω) :
    P.real {ω | X ω ∈ A} ≤ P.real {ω | Y ω ∈ A} + P.real B := by
  have hsub : {ω | X ω ∈ A} ⊆ {ω | Y ω ∈ A} ∪ B := by
    intro ω hω
    by_cases hB : ω ∈ B
    · exact Or.inr hB
    · left
      simp only [Set.mem_setOf_eq] at hω ⊢
      rw [← hXY ω hB]; exact hω
  exact (measureReal_mono hsub (measure_ne_top _ _)).trans (measureReal_union_le _ _)

/-- **Union bound over dates and traders.** -/
theorem p1_exit_union_bound {Ω : Type*} [MeasurableSpace Ω] (P : Measure Ω) [IsProbabilityMeasure P]
    (T n : ℕ) (E : ℕ → ℕ → Set Ω) (p : ℝ) (hp : ∀ t < T, ∀ g < n, P.real (E t g) ≤ p) :
    P.real (⋃ t ∈ range T, ⋃ g ∈ range n, E t g) ≤ T * n * p := by
  refine (measureReal_biUnion_finset_le _ _).trans ?_
  calc ∑ t ∈ range T, P.real (⋃ g ∈ range n, E t g) ≤ ∑ t ∈ range T, ∑ g ∈ range n, P.real (E t g) :=
        sum_le_sum fun t _ => measureReal_biUnion_finset_le _ _
    _ ≤ ∑ t ∈ range T, ∑ g ∈ range n, p :=
        sum_le_sum fun t ht => sum_le_sum fun g hg => hp t (mem_range.mp ht) g (mem_range.mp hg)
    _ = T * n * p := by simp [sum_const, card_range]; ring

/-- **The cost of a stress-free test.** If total variation is at most `T n p` and a test has both errors at most
`α < 1/2` (so total variation is at least `1 - 2α`), then `T ≥ (1 - 2α) / (n p)`. -/
theorem p1_stress_test_cost (T n p α TV : ℝ) (hn : 0 < n) (hp : 0 < p) (hTV : TV ≤ T * n * p)
    (htest : 1 - 2 * α ≤ TV) : (1 - 2 * α) / (n * p) ≤ T := by
  rw [div_le_iff₀ (by positivity)]
  linarith

/-- With the Gaussian tail `p = e^{-1/(2ϑ²)}`, the bound reads `T ≥ (1 - 2α) e^{1/(2ϑ²)} / n`. -/
theorem p1_stress_test_cost_exp (T n α TV ϑ : ℝ) (hn : 0 < n)
    (hTV : TV ≤ T * n * Real.exp (-(1 / (2 * ϑ ^ 2)))) (htest : 1 - 2 * α ≤ TV) :
    (1 - 2 * α) * Real.exp (1 / (2 * ϑ ^ 2)) / n ≤ T := by
  have h := p1_stress_test_cost T n (Real.exp (-(1 / (2 * ϑ ^ 2)))) α TV hn (Real.exp_pos _) hTV htest
  have e : (1 - 2 * α) / (n * Real.exp (-(1 / (2 * ϑ ^ 2)))) = (1 - 2 * α) * Real.exp (1 / (2 * ϑ ^ 2)) / n := by
    rw [Real.exp_neg]; field_simp
  rwa [e] at h

/-- **`prop:smooth`(i), the cost step.** -/
theorem p1_smooth_lower_cost (N σ α CD A e : ℝ) (hN : 0 ≤ N) (hσ : 0 < σ) (hα : α < 1 / 2) (hCD : 0 < CD)
    (hA : A ≠ 0) (he0 : 0 ≤ e) (he : e ≤ CD * |A| ^ 3)
    (hpinsker : 1 - 2 * α ≤ Real.sqrt (N * e ^ 2 / (4 * σ ^ 2))) :
    4 * σ ^ 2 * (1 - 2 * α) ^ 2 / (CD ^ 2 * A ^ 6) ≤ N := by
  have h0 : 0 ≤ 1 - 2 * α := by linarith
  have hsq : (1 - 2 * α) ^ 2 ≤ N * e ^ 2 / (4 * σ ^ 2) := by
    have := pow_le_pow_left₀ h0 hpinsker 2
    rwa [Real.sq_sqrt (by positivity)] at this
  have hA6 : 0 < A ^ 6 := by positivity
  have he2 : e ^ 2 ≤ CD ^ 2 * A ^ 6 := by
    have h1 : e ^ 2 ≤ (CD * |A| ^ 3) ^ 2 := pow_le_pow_left₀ he0 he 2
    have h2 : (CD * |A| ^ 3) ^ 2 = CD ^ 2 * A ^ 6 := by
      rw [mul_pow, ← pow_mul, show 3 * 2 = 6 by norm_num, show |A| ^ 6 = A ^ 6 by
        rw [show (6 : ℕ) = 2 * 3 by norm_num, pow_mul, sq_abs, ← pow_mul]]
    linarith
  rw [div_le_iff₀ (by positivity)]
  have hσ2 : 0 < 4 * σ ^ 2 := by positivity
  rw [le_div_iff₀ hσ2] at hsq
  nlinarith [mul_le_mul_of_nonneg_left he2 hN]

/-- **`prop:smooth`(ii), the cost step.** If the first-tap gap is at least `G = κ⁴ |ΔM₃| |A|³ / 6 > 0` and
`N ≥ (12 σ z)² / (κ⁸ ΔM₃² A⁶)` with `z ≥ 0`, then `√N · gap ≥ 2 σ z`. -/
theorem p1_smooth_upper_cost (N σ z κ ΔM₃ A gap : ℝ) (hσ : 0 < σ) (hz : 0 ≤ z) (hκ : 0 < κ) (hM : ΔM₃ ≠ 0)
    (hA : A ≠ 0) (hgap : κ ^ 4 * |ΔM₃| * |A| ^ 3 / 6 ≤ |gap|)
    (hN : (12 * σ * z) ^ 2 / (κ ^ 8 * ΔM₃ ^ 2 * A ^ 6) ≤ N) :
    2 * σ * z ≤ Real.sqrt N * |gap| := by
  set G := κ ^ 4 * |ΔM₃| * |A| ^ 3 / 6 with hG
  have hG0 : 0 < G := by positivity
  have hG2 : G ^ 2 = κ ^ 8 * ΔM₃ ^ 2 * A ^ 6 / 36 := by
    rw [hG, div_pow, mul_pow, mul_pow, ← pow_mul, ← pow_mul, sq_abs]
    rw [show |A| ^ (3 * 2) = A ^ 6 by
      rw [show 3 * 2 = 2 * 3 by norm_num, pow_mul, sq_abs, ← pow_mul]]
    norm_num
  have hden : 0 < κ ^ 8 * ΔM₃ ^ 2 * A ^ 6 := by positivity
  have hNG : (2 * σ * z) ^ 2 ≤ N * G ^ 2 := by
    rw [hG2]
    rw [div_le_iff₀ hden] at hN
    nlinarith
  have hN0 : 0 ≤ N := le_trans (by positivity) hN
  have h1 : 2 * σ * z ≤ Real.sqrt N * G := by
    rw [← Real.sqrt_sq (by positivity : 0 ≤ 2 * σ * z), ← Real.sqrt_sq hG0.le, ← Real.sqrt_mul hN0]
    exact Real.sqrt_le_sqrt hNG
  calc 2 * σ * z ≤ Real.sqrt N * G := h1
    _ ≤ Real.sqrt N * |gap| := by gcongr

end CurrentMM
