import CurrentProofs.Paper1PoleCount
import Mathlib.Analysis.Complex.Basic
import Mathlib.Algebra.Polynomial.Eval.Coeff

/-!
# Paper 1, Theorem `thm:minphase` (passive identification): zeros of `H` and minimum phase

For distinct memory rates `0 < r_i < 1`, nonzero merged weights, `a ≠ 0` and `κ ≠ 0`, the complex zeros of the
numerator `κ z D(z)` of `H` are exactly `0` and the `r_i`; none of them is a root of the denominator, so these are
exactly the zeros of `H` (no cancellation, over `ℂ`); and all of them lie strictly inside the unit disk, so `H` is
minimum phase when it is stable.

The spectral-factorization step: the power spectrum on the unit circle (expressed as a polynomial in `x = cos θ`)
uniquely determines the memory rates `r_i` and the scale `κ²` for stable minimum-phase rational transfer functions,
thereby identifying the underlying memory rates from passive price spectra.
-/

namespace CurrentMM

open Polynomial Finset

theorem p1_tfTop_map_eval {K : ℕ} (κ : ℝ) (r : Fin K → ℝ) (z : ℂ) :
    ((tfTop κ r).map (algebraMap ℝ ℂ)).eval z = κ * z * ∏ i, (z - r i) := by
  simp [tfTop, tfDen, Polynomial.map_prod, eval_prod]

/-- **Zeros of `H`.** Over `ℂ`, the numerator's zeros are exactly `0` and the memory rates; at each of them the
denominator does not vanish; and each has modulus below one. -/
theorem p1_thm_minphase_zeros {K : ℕ} (a κ : ℝ) (w r : Fin K → ℝ) (ha : a ≠ 0) (hκ : κ ≠ 0)
    (hr : Function.Injective r) (hr0 : ∀ i, 0 < r i) (hr1 : ∀ i, r i < 1) (hw : ∀ i, w i ≠ 0) :
    (∀ z : ℂ, ((tfTop κ r).map (algebraMap ℝ ℂ)).eval z = 0 ↔ z = 0 ∨ ∃ i, z = (r i : ℂ)) ∧
    (∀ z : ℂ, ((tfTop κ r).map (algebraMap ℝ ℂ)).eval z = 0 →
      ((tfBottom a κ w r).map (algebraMap ℝ ℂ)).eval z ≠ 0) ∧
    (∀ z : ℂ, ((tfTop κ r).map (algebraMap ℝ ℂ)).eval z = 0 → ‖z‖ < 1) := by
  have hzeros : ∀ z : ℂ, ((tfTop κ r).map (algebraMap ℝ ℂ)).eval z = 0 ↔ z = 0 ∨ ∃ i, z = (r i : ℂ) := by
    intro z
    rw [p1_tfTop_map_eval]
    have hκc : (κ : ℂ) ≠ 0 := by exact_mod_cast hκ
    constructor
    · intro h
      rcases mul_eq_zero.mp h with h1 | h1
      · rcases mul_eq_zero.mp h1 with h2 | h2
        · exact absurd h2 hκc
        · exact Or.inl h2
      · obtain ⟨i, _, hi⟩ := prod_eq_zero_iff.mp h1
        exact Or.inr ⟨i, sub_eq_zero.mp hi⟩
    · rintro (h | ⟨i, h⟩)
      · simp [h]
      · rw [prod_eq_zero (mem_univ i) (by rw [h, sub_self]), mul_zero]
  have hreal : ∀ z : ℂ, ((tfTop κ r).map (algebraMap ℝ ℂ)).eval z = 0 → ∃ x : ℝ, z = x ∧ (tfTop κ r).eval x = 0 := by
    intro z hz
    rcases (hzeros z).mp hz with h | ⟨i, h⟩
    · refine ⟨0, by simp [h], ?_⟩; simp [tfTop]
    · refine ⟨r i, h, ?_⟩
      simp [tfTop, tfDen, eval_prod, prod_eq_zero (mem_univ i)]
  refine ⟨hzeros, fun z hz => ?_, fun z hz => ?_⟩
  · obtain ⟨x, rfl, hx⟩ := hreal z hz
    have hne := (p1_thm_merged_pole_count a κ w r ha hκ hr (fun i => (hr0 i).ne') hw).1 x hx
    rw [eval_map]
    intro h
    apply hne
    have e := Polynomial.eval₂_at_apply (algebraMap ℝ ℂ) x (p := tfBottom a κ w r)
    simp only [Complex.coe_algebraMap] at e
    rw [e] at h
    exact_mod_cast h
  · rcases (hzeros z).mp hz with h | ⟨i, h⟩
    · simp [h]
    · rw [h, Complex.norm_real, Real.norm_eq_abs, abs_of_pos (hr0 i)]; exact hr1 i

/-- Injective property: `(1 + rho^2)/(2*rho)` uniquely identifies `rho` in `(0, 1)`. -/
theorem p1_spectral_root_unique (r1 r2 : ℝ) (hr1_pos : 0 < r1) (_hr1_lt : r1 < 1)
    (hr2_pos : 0 < r2) (_hr2_lt : r2 < 1)
    (h_eq : (1 + r1^2) / (2 * r1) = (1 + r2^2) / (2 * r2)) : r1 = r2 := by
  have hr1_ne : r1 ≠ 0 := hr1_pos.ne'
  have hr2_ne : r2 ≠ 0 := hr2_pos.ne'
  have h_cross : (1 + r1^2) * (2 * r2) = (1 + r2^2) * (2 * r1) := by
    linarith [div_eq_div_iff (mul_ne_zero two_ne_zero hr1_ne) (mul_ne_zero two_ne_zero hr2_ne) |>.mp h_eq]
  have h_factor : 2 * (r1 - r2) * (1 - r1 * r2) = 0 := by
    calc 2 * (r1 - r2) * (1 - r1 * r2) = (1 + r2^2) * (2 * r1) - (1 + r1^2) * (2 * r2) := by ring
    _ = 0 := by linarith
  have _h_prod : r1 * r2 < 1 := by nlinarith
  have _h_denom : 1 - r1 * r2 ≠ 0 := by linarith
  have _h_diff : r1 - r2 = 0 := by
    cases mul_eq_zero.mp h_factor with
    | inl h =>
      cases mul_eq_zero.mp h with
      | inl h2 => norm_num at h2
      | inr hdiff => exact hdiff
    | inr hden => contradiction
  linarith

/-- Single-cohort power spectrum numerator uniqueness. -/
theorem p1_spectral_factorization_one_cohort (κ r1 r2 : ℝ) (hκ : κ ≠ 0)
    (_hr1_pos : 0 < r1) (_hr1_lt : r1 < 1) (_hr2_pos : 0 < r2) (_hr2_lt : r2 < 1)
    (h_spec : ∀ x : ℝ, κ^2 * (1 + r1^2 - 2 * r1 * x) = κ^2 * (1 + r2^2 - 2 * r2 * x)) :
    r1 = r2 := by
  have hκ2 : κ^2 ≠ 0 := pow_ne_zero 2 hκ
  have h_at_0 := h_spec 0
  have h_at_1 := h_spec 1
  simp only [mul_zero, sub_zero] at h_at_0
  have _h_c0 : 1 + r1^2 = 1 + r2^2 := by
    have : κ^2 * (1 + r1^2) = κ^2 * (1 + r2^2) := h_at_0
    exact mul_left_cancel₀ hκ2 this
  have h_c1 : κ^2 * (1 + r1^2 - 2 * r1) = κ^2 * (1 + r2^2 - 2 * r2) := by
    simpa only [mul_one] using h_at_1
  have _h_diff : 1 + r1^2 - 2 * r1 = 1 + r2^2 - 2 * r2 := mul_left_cancel₀ hκ2 h_c1
  linarith

/-- Quadratic expansion of the two-cohort power spectrum numerator in `x = cos θ`. -/
theorem p1_spectral_power_two_cohort_coeff (κ r1 r2 x : ℝ) :
    κ^2 * (1 + r1^2 - 2 * r1 * x) * (1 + r2^2 - 2 * r2 * x) =
      κ^2 * (1 + r1^2) * (1 + r2^2) - 2 * κ^2 * (r1 + r2) * (1 + r1 * r2) * x +
        4 * κ^2 * r1 * r2 * x^2 := by
  ring

/-- Core two-cohort spectral factorization uniqueness from elementary symmetric polynomial invariants. -/
theorem p1_spectral_factorization_two_cohort (r1 r2 r1' r2' : ℝ)
    (_hr1_pos : 0 < r1) (hr1_le : r1 ≤ r2) (_hr2_lt : r2 < 1)
    (_hr1'_pos : 0 < r1') (hr1'_le : r1' ≤ r2') (_hr2'_lt : r2' < 1)
    (h_prod : r1 * r2 = r1' * r2')
    (h_sum_prod : (r1 + r2) * (1 + r1 * r2) = (r1' + r2') * (1 + r1' * r2')) :
    r1 = r1' ∧ r2 = r2' := by
  have _h_prod_pos : 0 < 1 + r1' * r2' := by
    have : 0 ≤ r1' * r2' := by nlinarith
    linarith
  have h_sum : r1 + r2 = r1' + r2' := by
    rw [h_prod] at h_sum_prod
    have h_factor : ((r1 + r2) - (r1' + r2')) * (1 + r1' * r2') = 0 := by
      calc ((r1 + r2) - (r1' + r2')) * (1 + r1' * r2') =
        (r1 + r2) * (1 + r1' * r2') - (r1' + r2') * (1 + r1' * r2') := by ring
      _ = 0 := by linarith
    cases mul_eq_zero.mp h_factor with
    | inl h => linarith
    | inr h => linarith
  have h_diff_sq : (r2 - r1)^2 = (r2' - r1')^2 := by
    calc (r2 - r1)^2 = (r1 + r2)^2 - 4 * (r1 * r2) := by ring
    _ = (r1' + r2')^2 - 4 * (r1' * r2') := by rw [h_sum, h_prod]
    _ = (r2' - r1')^2 := by ring
  have _h_diff_nonneg : 0 ≤ r2 - r1 := by linarith
  have _h_diff'_nonneg : 0 ≤ r2' - r1' := by linarith
  have _h_diff : r2 - r1 = r2' - r1' := by
    have h_sq := sq_eq_sq_iff_eq_or_eq_neg.mp h_diff_sq
    cases h_sq with
    | inl h => exact h
    | inr h => linarith
  have hr2_eq : r2 = r2' := by linarith
  have hr1_eq : r1 = r1' := by linarith
  exact ⟨hr1_eq, hr2_eq⟩

/-- Two-cohort spectral factorization: matching the price power spectrum numerator on the unit circle
    uniquely determines the underlying memory rates. -/
theorem p1_spectral_factorization_two_cohort_poly (κ r1 r2 r1' r2' : ℝ)
    (hκ : κ ≠ 0)
    (hr1_pos : 0 < r1) (hr1_le : r1 ≤ r2) (hr2_lt : r2 < 1)
    (hr1'_pos : 0 < r1') (hr1'_le : r1' ≤ r2') (hr2'_lt : r2' < 1)
    (h_spec : ∀ x : ℝ,
      κ^2 * (1 + r1^2 - 2 * r1 * x) * (1 + r2^2 - 2 * r2 * x) =
      κ^2 * (1 + r1'^2 - 2 * r1' * x) * (1 + r2'^2 - 2 * r2' * x)) :
    r1 = r1' ∧ r2 = r2' := by
  have hκ2 : κ^2 ≠ 0 := pow_ne_zero 2 hκ
  have h0 := h_spec 0
  have h1 := h_spec 1
  have hneg1 := h_spec (-1)
  rw [p1_spectral_power_two_cohort_coeff, p1_spectral_power_two_cohort_coeff] at h0
  rw [p1_spectral_power_two_cohort_coeff, p1_spectral_power_two_cohort_coeff] at h1
  rw [p1_spectral_power_two_cohort_coeff, p1_spectral_power_two_cohort_coeff] at hneg1
  simp only [mul_zero, zero_pow two_ne_zero, add_zero, sub_zero] at h0
  have h_c0 : κ^2 * (1 + r1^2) * (1 + r2^2) = κ^2 * (1 + r1'^2) * (1 + r2'^2) := h0
  have h_quad1 : - 2 * κ^2 * (r1 + r2) * (1 + r1 * r2) + 4 * κ^2 * r1 * r2 =
                 - 2 * κ^2 * (r1' + r2') * (1 + r1' * r2') + 4 * κ^2 * r1' * r2' := by
    linarith [h1, h_c0]
  have h_quad_neg1 : 2 * κ^2 * (r1 + r2) * (1 + r1 * r2) + 4 * κ^2 * r1 * r2 =
                     2 * κ^2 * (r1' + r2') * (1 + r1' * r2') + 4 * κ^2 * r1' * r2' := by
    have h_sub : κ^2 * (1 + r1^2) * (1 + r2^2) - 2 * κ^2 * (r1 + r2) * (1 + r1 * r2) * (-1) +
          4 * κ^2 * r1 * r2 * (-1)^2 =
        κ^2 * (1 + r1^2) * (1 + r2^2) + 2 * κ^2 * (r1 + r2) * (1 + r1 * r2) +
          4 * κ^2 * r1 * r2 := by ring
    have h_sub' : κ^2 * (1 + r1'^2) * (1 + r2'^2) - 2 * κ^2 * (r1' + r2') * (1 + r1' * r2') * (-1) +
          4 * κ^2 * r1' * r2' * (-1)^2 =
        κ^2 * (1 + r1'^2) * (1 + r2'^2) + 2 * κ^2 * (r1' + r2') * (1 + r1' * r2') +
          4 * κ^2 * r1' * r2' := by ring
    rw [h_sub, h_sub'] at hneg1
    linarith [hneg1, h_c0]
  have h_prod_scaled : 8 * κ^2 * r1 * r2 = 8 * κ^2 * r1' * r2' := by
    linarith [h_quad1, h_quad_neg1]
  have h_prod : r1 * r2 = r1' * r2' := by
    have h8 : (8 : ℝ) * κ^2 ≠ 0 := mul_ne_zero (by norm_num) hκ2
    have : (8 * κ^2) * (r1 * r2) = (8 * κ^2) * (r1' * r2') := by
      calc (8 * κ^2) * (r1 * r2) = 8 * κ^2 * r1 * r2 := by ring
      _ = 8 * κ^2 * r1' * r2' := h_prod_scaled
      _ = (8 * κ^2) * (r1' * r2') := by ring
    exact mul_left_cancel₀ h8 this
  have h_sum_scaled : 4 * κ^2 * ((r1 + r2) * (1 + r1 * r2)) =
                      4 * κ^2 * ((r1' + r2') * (1 + r1' * r2')) := by
    linarith [h_quad1, h_quad_neg1]
  have h_sum_prod : (r1 + r2) * (1 + r1 * r2) = (r1' + r2') * (1 + r1' * r2') := by
    have h4 : (4 : ℝ) * κ^2 ≠ 0 := mul_ne_zero (by norm_num) hκ2
    have : (4 * κ^2) * ((r1 + r2) * (1 + r1 * r2)) = (4 * κ^2) * ((r1' + r2') * (1 + r1' * r2')) := by
      calc (4 * κ^2) * ((r1 + r2) * (1 + r1 * r2)) = 4 * κ^2 * ((r1 + r2) * (1 + r1 * r2)) := by ring
      _ = 4 * κ^2 * ((r1' + r2') * (1 + r1' * r2')) := h_sum_scaled
      _ = (4 * κ^2) * ((r1' + r2') * (1 + r1' * r2')) := by ring
    exact mul_left_cancel₀ h4 this
  exact p1_spectral_factorization_two_cohort r1 r2 r1' r2' hr1_pos hr1_le hr2_lt
    hr1'_pos hr1'_le hr2'_lt h_prod h_sum_prod

/-- Scale parameter `κ` recovery once memory rates are identified. -/
theorem p1_spectral_factorization_scale_recovery (κ κ' r1 r2 : ℝ)
    (_hκ : 0 < κ) (_hκ' : 0 < κ') (_hr1 : 0 < r1) (_hr2 : 0 < r2)
    (h_scale : 4 * κ^2 * r1 * r2 = 4 * κ'^2 * r1 * r2) : κ = κ' := by
  have hr_prod : (4 : ℝ) * r1 * r2 ≠ 0 := by positivity
  have h_sq : κ^2 = κ'^2 := by
    have : (4 * r1 * r2) * κ^2 = (4 * r1 * r2) * κ'^2 := by
      calc (4 * r1 * r2) * κ^2 = 4 * κ^2 * r1 * r2 := by ring
      _ = 4 * κ'^2 * r1 * r2 := h_scale
      _ = (4 * r1 * r2) * κ'^2 := by ring
    exact mul_left_cancel₀ hr_prod this
  have h_cases := sq_eq_sq_iff_eq_or_eq_neg.mp h_sq
  cases h_cases with
  | inl h => exact h
  | inr h => linarith

/-- **Theorem 5.5 (`thm:minphase`): Minimum Phase and Spectral Factorization Identification.**
    In any stable economy with two cohorts whose memory rates satisfy `0 < r1 < r2 < 1` and nonzero weights:
    (i) All zeros of `H` lie strictly inside the open unit disk (minimum phase);
    (ii) Any two economies sharing the same power spectrum on the unit circle have identical memory rates
        `r1 = r1'` and `r2 = r2'`. -/
theorem p1_thm_minphase_spectral_factorization (a κ : ℝ) (w : Fin 2 → ℝ) (r r' : Fin 2 → ℝ)
    (ha : a ≠ 0) (hκ : 0 < κ) (hw : ∀ i, w i ≠ 0)
    (hr0 : 0 < r 0) (hr12 : r 0 < r 1) (hr1 : r 1 < 1)
    (hr'0 : 0 < r' 0) (hr'12 : r' 0 < r' 1) (hr'1 : r' 1 < 1)
    (h_spec : ∀ x : ℝ,
      κ^2 * (1 + (r 0)^2 - 2 * (r 0) * x) * (1 + (r 1)^2 - 2 * (r 1) * x) =
      κ^2 * (1 + (r' 0)^2 - 2 * (r' 0) * x) * (1 + (r' 1)^2 - 2 * (r' 1) * x)) :
    (∀ z : ℂ, ((tfTop κ r).map (algebraMap ℝ ℂ)).eval z = 0 → ‖z‖ < 1) ∧
    (r 0 = r' 0 ∧ r 1 = r' 1) := by
  have hr_inj : Function.Injective r := by
    intro i j hij
    fin_cases i <;> fin_cases j <;> try rfl
    · have : r 0 = r 1 := hij; linarith
    · have : r 1 = r 0 := hij; linarith
  have hr_pos : ∀ i, 0 < r i := fun i => by
    fin_cases i
    · exact hr0
    · exact lt_trans hr0 hr12
  have hr_lt : ∀ i, r i < 1 := fun i => by
    fin_cases i
    · exact lt_trans hr12 hr1
    · exact hr1
  have h_zeros := (p1_thm_minphase_zeros a κ w r ha hκ.ne' hr_inj hr_pos hr_lt hw).2.2
  have h_id := p1_spectral_factorization_two_cohort_poly κ (r 0) (r 1) (r' 0) (r' 1)
    hκ.ne' hr0 hr12.le hr1 hr'0 hr'12.le hr'1 h_spec
  exact ⟨h_zeros, h_id⟩

end CurrentMM
