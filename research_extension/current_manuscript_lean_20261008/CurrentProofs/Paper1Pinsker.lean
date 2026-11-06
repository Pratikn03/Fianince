import CurrentProofs.Paper1Testing
import Mathlib.Analysis.Calculus.MeanValue
import Mathlib.Analysis.SpecialFunctions.Log.Deriv

/-!
# Paper 1: Pinsker's inequality for events, and testing bounds at every error level

Mathlib has no Pinsker inequality. This file proves the form the paper uses:
for probability measures `P, Q` and every measurable event `A`,

  `2 (P(A) - Q(A))² ≤ KL(P ‖ Q)`.

The proof has two steps:
1. **Binary Pinsker** (`p1_binary_pinsker`): for Bernoulli laws,
   `2 (p - q)² ≤ p log(p/q) + (1-p) log((1-p)/(1-q))`. It is proved by monotonicity, since the derivative in `q`
   is `(q-p)(2q-1)²/(q(1-q))`.
2. **Data processing to one event** (`p1_kl_ge_binary`): `KL(P ‖ Q)` is at least the binary divergence of
   `(P(A), Q(A))`, by Jensen's inequality on `A` and on `Aᶜ` (`Paper1Testing.lean`).

Consequences: any test whose two error probabilities are `α` and `β` with `α + β ≤ 1` forces
`KL ≥ 2(1 - α - β)²` (`p1_test_error_kl_lower_bound_general`). With a divergence bound `KL ≤ c`, the worst error is
at least `(1 - √(c/2))/2` (`p1_worst_error_ge`). These replace the error-`1/4` form used so far.
-/

namespace CurrentMM

open MeasureTheory InformationTheory Real Set
open scoped ENNReal

/-- The function whose monotonicity gives binary Pinsker. -/
noncomputable def p1BinPinskerAux (p t : ℝ) : ℝ :=
  p * log p - p * log t + (1 - p) * log (1 - p) - (1 - p) * log (1 - t) - 2 * (t - p) ^ 2

theorem p1_binPinskerAux_self (p : ℝ) : p1BinPinskerAux p p = 0 := by
  unfold p1BinPinskerAux; ring

theorem p1_binPinskerAux_hasDerivAt (p x : ℝ) (hx0 : 0 < x) (hx1 : x < 1) :
    HasDerivAt (p1BinPinskerAux p) (-(p * x⁻¹) + (1 - p) * (1 - x)⁻¹ - 4 * (x - p)) x := by
  have h1 : HasDerivAt (fun t => p * log t) (p * x⁻¹) x := (hasDerivAt_log hx0.ne').const_mul p
  have h2 : HasDerivAt (fun t => log (1 - t)) (-1 / (1 - x)) x :=
    ((hasDerivAt_id x).const_sub 1).log (by simp; linarith)
  have h3 : HasDerivAt (fun t => (1 - p) * log (1 - t)) ((1 - p) * (-1 / (1 - x))) x := h2.const_mul (1 - p)
  have h4 : HasDerivAt (fun t => 2 * (t - p) ^ 2) (2 * ((2 : ℕ) * (x - p) ^ (2 - 1) * 1)) x :=
    (((hasDerivAt_id x).sub_const p).pow 2).const_mul 2
  have h := ((((hasDerivAt_const x (p * log p)).sub h1).add (hasDerivAt_const x ((1 - p) * log (1 - p)))).sub
    h3).sub h4
  unfold p1BinPinskerAux
  convert h using 1
  have hx1' : (1 - x) ≠ 0 := by linarith
  field_simp
  ring

theorem p1_binPinskerAux_deriv_nonneg (p x : ℝ) (hpx : p ≤ x) (hx0 : 0 < x) (hx1 : x < 1) :
    0 ≤ -(p * x⁻¹) + (1 - p) * (1 - x)⁻¹ - 4 * (x - p) := by
  have hx1' : 0 < 1 - x := by linarith
  have e : -(p * x⁻¹) + (1 - p) * (1 - x)⁻¹ - 4 * (x - p) = (x - p) * (2 * x - 1) ^ 2 / (x * (1 - x)) := by
    field_simp
    ring
  rw [e]
  apply div_nonneg
  · exact mul_nonneg (by linarith) (sq_nonneg _)
  · exact (mul_pos hx0 hx1').le

theorem p1_binPinskerAux_continuousOn (p q : ℝ) (hp0 : 0 ≤ p) (hq1 : q < 1) :
    ContinuousOn (p1BinPinskerAux p) (Icc p q) := by
  have hc1 : ContinuousOn (fun t => p * log t) (Icc p q) := by
    rcases hp0.eq_or_lt with h | h
    · subst h; simp only [zero_mul]; exact continuousOn_const
    · exact continuousOn_const.mul (continuousOn_log.mono (fun t ht => by
        simp only [mem_compl_iff, mem_singleton_iff]; exact ne_of_gt (lt_of_lt_of_le h ht.1)))
  have hc2 : ContinuousOn (fun t => log (1 - t)) (Icc p q) :=
    (continuousOn_const.sub continuousOn_id).log (fun t ht => by
      have : t ≤ q := ht.2; simp only [id]; linarith)
  unfold p1BinPinskerAux
  exact ((((continuousOn_const.sub hc1).add continuousOn_const).sub (continuousOn_const.mul hc2)).sub
    (continuousOn_const.mul ((continuousOn_id.sub continuousOn_const).pow 2)))

/-- Binary Pinsker when `p ≤ q < 1`. -/
theorem p1_binary_pinsker_le (p q : ℝ) (hp0 : 0 ≤ p) (hpq : p ≤ q) (hq1 : q < 1) :
    2 * (q - p) ^ 2 ≤ p * log (p / q) + (1 - p) * log ((1 - p) / (1 - q)) := by
  have hmono : MonotoneOn (p1BinPinskerAux p) (Icc p q) := by
    apply monotoneOn_of_deriv_nonneg (convex_Icc p q) (p1_binPinskerAux_continuousOn p q hp0 hq1)
    · intro x hx
      rw [interior_Icc] at hx
      exact (p1_binPinskerAux_hasDerivAt p x (lt_of_le_of_lt hp0 hx.1) (lt_trans hx.2 hq1)).differentiableAt
        |>.differentiableWithinAt
    · intro x hx
      rw [interior_Icc] at hx
      rw [(p1_binPinskerAux_hasDerivAt p x (lt_of_le_of_lt hp0 hx.1) (lt_trans hx.2 hq1)).deriv]
      exact p1_binPinskerAux_deriv_nonneg p x hx.1.le (lt_of_le_of_lt hp0 hx.1) (lt_trans hx.2 hq1)
  have hge := hmono (left_mem_Icc.mpr hpq) (right_mem_Icc.mpr hpq) hpq
  rw [p1_binPinskerAux_self] at hge
  have hlog1 : p * log (p / q) = p * log p - p * log q := by
    rcases hp0.eq_or_lt with h | h
    · subst h; simp
    · rw [log_div h.ne' (by linarith : q ≠ 0)]; ring
  have hlog2 : (1 - p) * log ((1 - p) / (1 - q)) = (1 - p) * log (1 - p) - (1 - p) * log (1 - q) := by
    rw [log_div (by linarith : (1 - p) ≠ 0) (by linarith : (1 - q) ≠ 0)]; ring
  rw [hlog1, hlog2]
  unfold p1BinPinskerAux at hge
  linarith

/-- **Binary Pinsker.** For `0 ≤ p ≤ 1` and `0 < q < 1`. -/
theorem p1_binary_pinsker (p q : ℝ) (hp0 : 0 ≤ p) (hp1 : p ≤ 1) (hq0 : 0 < q) (hq1 : q < 1) :
    2 * (p - q) ^ 2 ≤ p * log (p / q) + (1 - p) * log ((1 - p) / (1 - q)) := by
  rcases le_total p q with h | h
  · have := p1_binary_pinsker_le p q hp0 h hq1
    nlinarith [this]
  · have := p1_binary_pinsker_le (1 - p) (1 - q) (by linarith) (by linarith) (by linarith)
    simp only [sub_sub_cancel] at this
    nlinarith [this]

variable {α : Type*} [MeasurableSpace α]

/-- **Data processing to one event.** `KL(P ‖ Q)` is at least the binary divergence of `(P(A), Q(A))`. -/
theorem p1_kl_ge_binary (P Q : Measure α) [IsProbabilityMeasure P] [IsProbabilityMeasure Q]
    {A : Set α} (hA : MeasurableSet A) (hac : P ≪ Q) (hQA : Q A ≠ 0) (hQAc : Q Aᶜ ≠ 0) :
    ENNReal.ofReal (P.real A * log (P.real A / Q.real A) + P.real Aᶜ * log (P.real Aᶜ / Q.real Aᶜ)) ≤
      klDiv P Q := by
  have hQApos : 0 < Q.real A := ENNReal.toReal_pos hQA (measure_ne_top _ _)
  have hQAcpos : 0 < Q.real Aᶜ := ENNReal.toReal_pos hQAc (measure_ne_top _ _)
  rw [klDiv_eq_lintegral_klFun_of_ac hac, ← lintegral_add_compl _ hA]
  have h1 := p1_setLIntegral_klFun_ge P Q hac hQA
  have h2 := p1_setLIntegral_klFun_ge P Q hac hQAc
  have hn1 : 0 ≤ Q.real A * klFun (P.real A / Q.real A) :=
    mul_nonneg hQApos.le (klFun_nonneg (div_nonneg measureReal_nonneg hQApos.le))
  have hn2 : 0 ≤ Q.real Aᶜ * klFun (P.real Aᶜ / Q.real Aᶜ) :=
    mul_nonneg hQAcpos.le (klFun_nonneg (div_nonneg measureReal_nonneg hQAcpos.le))
  refine le_trans ?_ (add_le_add h1 h2)
  rw [← ENNReal.ofReal_add hn1 hn2]
  apply ENNReal.ofReal_le_ofReal
  rw [p1_mul_klFun_div _ _ hQApos, p1_mul_klFun_div _ _ hQAcpos]
  have hP : P.real A + P.real Aᶜ = 1 := by rw [measureReal_compl hA]; simp
  have hQ : Q.real A + Q.real Aᶜ = 1 := by rw [measureReal_compl hA]; simp
  linarith

/-- **Pinsker's inequality for an event.** `2 (P(A) - Q(A))² ≤ KL(P ‖ Q)`. -/
theorem p1_set_pinsker (P Q : Measure α) [IsProbabilityMeasure P] [IsProbabilityMeasure Q]
    {A : Set α} (hA : MeasurableSet A) :
    ENNReal.ofReal (2 * (P.real A - Q.real A) ^ 2) ≤ klDiv P Q := by
  by_cases hac : P ≪ Q
  swap
  · rw [klDiv_of_not_ac hac]; exact le_top
  have hPc : P.real Aᶜ = 1 - P.real A := by rw [measureReal_compl hA]; simp
  have hQc : Q.real Aᶜ = 1 - Q.real A := by rw [measureReal_compl hA]; simp
  by_cases hQA : Q A = 0
  · have hPA : P A = 0 := hac hQA
    have e1 : P.real A = 0 := by simp [measureReal_def, hPA]
    have e2 : Q.real A = 0 := by simp [measureReal_def, hQA]
    rw [e1, e2]; simp
  by_cases hQAc : Q Aᶜ = 0
  · have hPAc : P Aᶜ = 0 := hac hQAc
    have e1 : P.real Aᶜ = 0 := by simp [measureReal_def, hPAc]
    have e2 : Q.real Aᶜ = 0 := by simp [measureReal_def, hQAc]
    have : P.real A - Q.real A = 0 := by linarith
    rw [this]; simp
  refine le_trans ?_ (p1_kl_ge_binary P Q hA hac hQA hQAc)
  apply ENNReal.ofReal_le_ofReal
  have hQApos : 0 < Q.real A := ENNReal.toReal_pos hQA (measure_ne_top _ _)
  have hQAcpos : 0 < Q.real Aᶜ := ENNReal.toReal_pos hQAc (measure_ne_top _ _)
  rw [hPc, hQc]
  exact p1_binary_pinsker _ _ measureReal_nonneg measureReal_le_one hQApos (by linarith)

/-- **Testing at every error level.** If `P(A) ≤ a`, `Q(Aᶜ) ≤ b` and `a + b ≤ 1`, then `KL(P ‖ Q) ≥ 2(1 - a - b)²`. -/
theorem p1_test_error_kl_lower_bound_general (P Q : Measure α) [IsProbabilityMeasure P] [IsProbabilityMeasure Q]
    {A : Set α} (hA : MeasurableSet A) (a b : ℝ) (hab : a + b ≤ 1)
    (hP : P.real A ≤ a) (hQ : Q.real Aᶜ ≤ b) :
    ENNReal.ofReal (2 * (1 - a - b) ^ 2) ≤ klDiv P Q := by
  refine le_trans ?_ (p1_set_pinsker P Q hA)
  apply ENNReal.ofReal_le_ofReal
  have hQc : Q.real Aᶜ = 1 - Q.real A := by rw [measureReal_compl hA]; simp
  have h1 : 1 - a - b ≤ Q.real A - P.real A := by linarith
  have h0 : 0 ≤ 1 - a - b := by linarith
  nlinarith [mul_le_mul h1 h1 h0 (le_trans h0 h1)]

/-- **Worst error under a divergence budget.** If `KL(P ‖ Q) ≤ c` (as a real number `c ≥ 0`), then for every event
`A`, `max(P(A), Q(Aᶜ)) ≥ (1 - √(c/2))/2`. -/
theorem p1_worst_error_ge (P Q : Measure α) [IsProbabilityMeasure P] [IsProbabilityMeasure Q]
    {A : Set α} (hA : MeasurableSet A) (c : ℝ) (hc : 0 ≤ c) (hkl : klDiv P Q ≤ ENNReal.ofReal c) :
    (1 - sqrt (c / 2)) / 2 ≤ max (P.real A) (Q.real Aᶜ) := by
  have hpin := (p1_set_pinsker P Q hA).trans hkl
  rw [ENNReal.ofReal_le_ofReal_iff hc] at hpin
  have hQc : Q.real Aᶜ = 1 - Q.real A := by rw [measureReal_compl hA]; simp
  have hd : |P.real A - Q.real A| ≤ sqrt (c / 2) := by
    rw [← sqrt_sq_eq_abs]
    exact sqrt_le_sqrt (by nlinarith)
  have hm1 : P.real A ≤ max (P.real A) (Q.real Aᶜ) := le_max_left _ _
  have hm2 : Q.real Aᶜ ≤ max (P.real A) (Q.real Aᶜ) := le_max_right _ _
  have := neg_abs_le (P.real A - Q.real A)
  linarith

end CurrentMM
