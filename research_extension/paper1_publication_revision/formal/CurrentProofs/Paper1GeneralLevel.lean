import CurrentProofs.Paper1MatchedPair
import CurrentProofs.Paper1QuantityCapital
import CurrentProofs.Paper1Pinsker

/-!
# Paper 1: the lower bounds at every error level, and the paper's exact error forms

With Pinsker's inequality for events (`Paper1Pinsker.lean`), the testing step holds for any error probabilities
`α₀, β₀` with `α₀ + β₀ ≤ 1`: `KL ≥ 2(1 - α₀ - β₀)²`. This file restates the lower bounds that previously required
both errors to be at most `1/4`.

* `thm:kcohort`, `thm:twocohort` (finite horizon): `4σ²(1-α₀-β₀)² ≤ N T (ε C_T)²`, i.e.
  `N ≥ 4(1-α₀-β₀)² σ² / (T (ε C_T)²)`, the paper's `N ≥ 4(1-2α)²σ²(Δη)^-(4K-2)/C_K` with `α₀ = β₀ = α`.
* `thm:quantity` (i), exact form of the paper: the worst error of any test is at least `(1 - K* V δ² / (2σ))/2`,
  and error at most `α` on both sides needs `V ≥ 2σ(1-2α)/(K* δ²)`.
* Lemma `thm:capital`, exact form of the paper: error at most `α` on both sides needs
  `B ≥ 2σ² m (1-2α)² / (K*² δ⁴)`.
-/

namespace CurrentMM

open Finset MeasureTheory ProbabilityTheory InformationTheory Real
open scoped ENNReal NNReal

theorem p1_thm_lower_bound_from_kernel_gap_general (a κ B H ε : ℝ) (k k' h h' : ℕ → ℝ) (N T : ℕ)
    (variance : ℝ≥0) (hv : variance ≠ 0)
    (hB : 0 ≤ B) (hH : 0 ≤ H) (hε : 0 ≤ ε)
    (h0 : h 0 = κ) (h0' : h' 0 = κ)
    (hrec : ∀ t, h (t + 1) = a * h t + κ * ∑ j ∈ range (t + 1), k j * h (t - j))
    (hrec' : ∀ t, h' (t + 1) = a * h' t + κ * ∑ j ∈ range (t + 1), k' j * h' (t - j))
    (hkB : ∀ j, |k j| ≤ B) (hh' : ∀ s, s < T → |h' s| ≤ H)
    (hgap : ∀ j, j < T → |k j - k' j| ≤ ε)
    (α₀ β₀ : ℝ) (hab : α₀ + β₀ ≤ 1) (A : Set (ObservationRecord (N * T))) (hA : MeasurableSet A)
    (herr0 : (gaussianRecordLaw (N * T) (p1RepeatedMean N T h) variance).real A ≤ α₀)
    (herr1 : (gaussianRecordLaw (N * T) (p1RepeatedMean N T h') variance).real Aᶜ ≤ β₀) :
    4 * (variance : ℝ) * (1 - α₀ - β₀) ^ 2 ≤ N * T * (ε * p1GapConst a |κ| B H T) ^ 2 := by
  have hvpos : 0 < (variance : ℝ) := by positivity
  have htest := p1_test_error_kl_lower_bound_general _ _ hA α₀ β₀ hab herr0 herr1
  rw [p1_repeated_record_kl N T h h' variance hv] at htest
  have hgapT := p1_impulse_gap_finite_horizon a κ B H ε k k' h h' T hB hH hε h0 h0' hrec hrec' hkB hh' hgap
  have hK0 : 0 ≤ |κ| := abs_nonneg κ
  have hCT : ∀ t, t < T → |h t - h' t| ≤ ε * p1GapConst a |κ| B H T := by
    intro t ht
    have hmono : ∀ u v, u ≤ v → p1GapConst a |κ| B H u ≤ p1GapConst a |κ| B H v := by
      intro u v huv
      induction v with
      | zero => have : u = 0 := by omega
                subst this; exact le_rfl
      | succ v ihv =>
        rcases Nat.lt_or_ge u (v + 1) with h1 | h1
        · exact le_trans (ihv (by omega)) (p1GapConst_mono a |κ| B H hK0 hB hH v)
        · have : u = v + 1 := by omega
          subst this; exact le_rfl
    exact le_trans (hgapT t ht) (mul_le_mul_of_nonneg_left (hmono t T ht.le) hε)
  have hsq : ∑ t ∈ range T, (h t - h' t) ^ 2 ≤ T * (ε * p1GapConst a |κ| B H T) ^ 2 := by
    calc ∑ t ∈ range T, (h t - h' t) ^ 2 ≤ ∑ t ∈ range T, (ε * p1GapConst a |κ| B H T) ^ 2 := by
          refine sum_le_sum (fun t ht => ?_)
          have := hCT t (mem_range.mp ht)
          rw [← sq_abs]
          exact pow_le_pow_left₀ (abs_nonneg _) this 2
      _ = T * (ε * p1GapConst a |κ| B H T) ^ 2 := by rw [sum_const, card_range, nsmul_eq_mul]
  have hle := (ENNReal.ofReal_le_ofReal_iff (by positivity)).mp htest
  rw [le_div_iff₀ (by positivity)] at hle
  have hN : (0 : ℝ) ≤ N := Nat.cast_nonneg N
  nlinarith [mul_le_mul_of_nonneg_left hsq hN]


theorem p1_thm_kcohort_lower_bound_formal_general {n0 n1 : ℕ} (a κ c d W H : ℝ) (nmatch N T : ℕ)
    (q rate s : Fin n0 → ℝ) (q' rate' s' : Fin n1 → ℝ) (variance : ℝ≥0) (hv : variance ≠ 0)
    (hc : 0 ≤ c) (hd : 0 ≤ d) (hcd : c + d ≤ 1) (hH : 0 ≤ H)
    (hr : ∀ i, 1 - rate i = c + d * s i) (hr' : ∀ i, 1 - rate' i = c + d * s' i)
    (hs : ∀ i, |s i| ≤ 1) (hs' : ∀ i, |s' i| ≤ 1)
    (hw : ∀ i, 0 ≤ q i * rate i) (hw' : ∀ i, 0 ≤ q' i * rate' i)
    (hW : ∑ i, q i * rate i ≤ W) (hW' : ∑ i, q' i * rate' i ≤ W)
    (hmom : ∀ j < nmatch, mgMoment univ (fun i => q i * rate i) s j =
      mgMoment univ (fun i => q' i * rate' i) s' j)
    (hh' : ∀ t, t < T → |actualCohortImpulse a κ q' rate' t| ≤ H)
    (α₀ β₀ : ℝ) (hab : α₀ + β₀ ≤ 1) (A : Set (ObservationRecord (N * T))) (hA : MeasurableSet A)
    (herr0 : (gaussianRecordLaw (N * T) (p1RepeatedMean N T (actualCohortImpulse a κ q rate))
      variance).real A ≤ α₀)
    (herr1 : (gaussianRecordLaw (N * T) (p1RepeatedMean N T (actualCohortImpulse a κ q' rate'))
      variance).real Aᶜ ≤ β₀) :
    4 * (variance : ℝ) * (1 - α₀ - β₀) ^ 2 ≤ N * T * ((2 * W * 2 ^ T * d ^ nmatch) * p1GapConst a |κ| W H T) ^ 2 := by
  have hW0 : 0 ≤ W := le_trans (sum_nonneg (fun i _ => hw i)) hW
  refine p1_thm_lower_bound_from_kernel_gap_general a κ W H (2 * W * 2 ^ T * d ^ nmatch)
    (cohortKernel q rate) (cohortKernel q' rate') (actualCohortImpulse a κ q rate)
    (actualCohortImpulse a κ q' rate') N T variance hv hW0 hH (by positivity)
    (p1_impulse_zero a κ q rate) (p1_impulse_zero a κ q' rate')
    (p1_impulse_closed_loop_recursion a κ q rate) (p1_impulse_closed_loop_recursion a κ q' rate')
    (fun j => by
      rw [p1_cohortKernel_eq_mgKernel q rate s c d hr]
      exact p1_mg_kernel_abs_le univ _ s c d W j hc hd hcd (fun i _ => hw i) (fun i _ => hs i) hW)
    hh' (fun j hj => by
      rw [p1_cohortKernel_eq_mgKernel q rate s c d hr, p1_cohortKernel_eq_mgKernel q' rate' s' c d hr']
      exact p1_mg_kernel_gap_uniform univ univ _ s _ s' c d W nmatch T hc hd hcd (fun i _ => hw i)
        (fun i _ => hw' i) (fun i _ => hs i) (fun i _ => hs' i) hW hW' hmom j hj)
    α₀ β₀ hab A hA herr0 herr1


theorem p1_thm_twocohort_lower_bound_formal_general (a κ c d W H : ℝ) (N T : ℕ)
    (q rate q' rate' : Fin 2 → ℝ) (variance : ℝ≥0) (hv : variance ≠ 0)
    (hc : 0 ≤ c) (hd : 0 ≤ d) (hcd : c + d ≤ 1) (hH : 0 ≤ H) (hW : 0 ≤ W)
    (hr : ∀ i, 1 - rate i = c + d * ![-1, 1 / 3] i) (hr' : ∀ i, 1 - rate' i = c + d * ![-1 / 2, 2 / 3] i)
    (hq : ∀ i, q i * rate i = W * ![1 / 4, 3 / 4] i) (hq' : ∀ i, q' i * rate' i = W * ![4 / 7, 3 / 7] i)
    (hh' : ∀ t, t < T → |actualCohortImpulse a κ q' rate' t| ≤ H)
    (α₀ β₀ : ℝ) (hab : α₀ + β₀ ≤ 1) (A : Set (ObservationRecord (N * T))) (hA : MeasurableSet A)
    (herr0 : (gaussianRecordLaw (N * T) (p1RepeatedMean N T (actualCohortImpulse a κ q rate))
      variance).real A ≤ α₀)
    (herr1 : (gaussianRecordLaw (N * T) (p1RepeatedMean N T (actualCohortImpulse a κ q' rate'))
      variance).real Aᶜ ≤ β₀) :
    4 * (variance : ℝ) * (1 - α₀ - β₀) ^ 2 ≤ N * T * ((2 * W * 2 ^ T * d ^ 3) * p1GapConst a |κ| W H T) ^ 2 := by
  have hw : ∀ i, 0 ≤ q i * rate i := fun i => by
    rw [hq i]; fin_cases i <;> simp <;> positivity
  have hw' : ∀ i, 0 ≤ q' i * rate' i := fun i => by
    rw [hq' i]; fin_cases i <;> simp <;> positivity
  have hsum : ∑ i, q i * rate i ≤ W := by
    simp only [hq, Fin.sum_univ_two]; norm_num; linarith
  have hsum' : ∑ i, q' i * rate' i ≤ W := by
    simp only [hq', Fin.sum_univ_two]; norm_num; linarith
  refine p1_thm_kcohort_lower_bound_formal_general a κ c d W H 3 N T q rate ![-1, 1 / 3] q' rate'
    ![-1 / 2, 2 / 3] variance hv hc hd hcd hH hr hr'
    (fun i => by fin_cases i <;> norm_num [abs_le])
    (fun i => by fin_cases i <;> norm_num [abs_le]) hw hw' hsum hsum'
    (fun j hj => by
      have e1 : (fun i => q i * rate i) = (fun i : Fin 2 => W * ![1 / 4, 3 / 4] i) := funext hq
      have e2 : (fun i => q' i * rate' i) = (fun i : Fin 2 => W * ![4 / 7, 3 / 7] i) := funext hq'
      rw [e1, e2]; exact p1_twocohort_matched_pair W j hj)
    hh' α₀ β₀ hab A hA herr0 herr1


theorem p1_thm_kcohort_lower_bound_every_K_general (L : ℕ) (a κ c d W H : ℝ) (N T : ℕ)
    (q rate q' rate' : Fin (L + 1) → ℝ) (variance : NNReal) (hv : variance ≠ 0)
    (hc : 0 ≤ c) (hd : 0 ≤ d) (hcd : c + d ≤ 1) (hH : 0 ≤ H) (hW : 0 ≤ W)
    (hr : ∀ i : Fin (L + 1), 1 - rate i = c + d * gridNode L (2 * i + 1))
    (hr' : ∀ i : Fin (L + 1), 1 - rate' i = c + d * gridNode L (2 * i))
    (hq : ∀ i : Fin (L + 1), q i * rate i = W * ((2 * L + 1).choose (2 * i + 1) : ℝ) / 2 ^ (2 * L))
    (hq' : ∀ i : Fin (L + 1), q' i * rate' i = W * ((2 * L + 1).choose (2 * i) : ℝ) / 2 ^ (2 * L))
    (hh' : ∀ t, t < T → |actualCohortImpulse a κ q' rate' t| ≤ H)
    (α₀ β₀ : ℝ) (hab : α₀ + β₀ ≤ 1) (A : Set (ObservationRecord (N * T))) (hA : MeasurableSet A)
    (herr0 : (gaussianRecordLaw (N * T) (p1RepeatedMean N T (actualCohortImpulse a κ q rate))
      variance).real A ≤ α₀)
    (herr1 : (gaussianRecordLaw (N * T) (p1RepeatedMean N T (actualCohortImpulse a κ q' rate'))
      variance).real Aᶜ ≤ β₀) :
    4 * (variance : ℝ) * (1 - α₀ - β₀) ^ 2 ≤ N * T * ((2 * W * 2 ^ T * d ^ (2 * L + 1)) * p1GapConst a |κ| W H T) ^ 2 := by
  have hpow : (0 : ℝ) < 2 ^ (2 * L) := by positivity
  obtain ⟨hodd, heven⟩ := p1_grid_half_weight L
  have hw : ∀ i, 0 ≤ q i * rate i := fun i => by rw [hq i]; positivity
  have hw' : ∀ i, 0 ≤ q' i * rate' i := fun i => by rw [hq' i]; positivity
  have hsum : ∑ i, q i * rate i ≤ W := by
    simp only [hq]
    rw [Fin.sum_univ_eq_sum_range (fun i => W * ((2 * L + 1).choose (2 * i + 1) : ℝ) / 2 ^ (2 * L)),
      ← sum_div, ← mul_sum, hodd, mul_div_assoc, div_self hpow.ne', mul_one]
  have hsum' : ∑ i, q' i * rate' i ≤ W := by
    simp only [hq']
    rw [Fin.sum_univ_eq_sum_range (fun i => W * ((2 * L + 1).choose (2 * i) : ℝ) / 2 ^ (2 * L)),
      ← sum_div, ← mul_sum, heven, mul_div_assoc, div_self hpow.ne', mul_one]
  refine p1_thm_kcohort_lower_bound_formal_general a κ c d W H (2 * L + 1) N T q rate
    (fun i => gridNode L (2 * i + 1)) q' rate' (fun i => gridNode L (2 * i)) variance hv hc hd hcd hH hr hr'
    (fun i => p1_gridNode_abs_le L _ (by omega)) (fun i => p1_gridNode_abs_le L _ (by omega))
    hw hw' hsum hsum' (fun j hj => ?_) hh' α₀ β₀ hab A hA herr0 herr1
  unfold mgMoment
  simp only [hq, hq']
  rw [Fin.sum_univ_eq_sum_range (fun i => W * ((2 * L + 1).choose (2 * i + 1) : ℝ) / 2 ^ (2 * L) *
      gridNode L (2 * i + 1) ^ j),
    Fin.sum_univ_eq_sum_range (fun i => W * ((2 * L + 1).choose (2 * i) : ℝ) / 2 ^ (2 * L) *
      gridNode L (2 * i) ^ j)]
  have hm := p1_grid_matched_moments L j hj
  have e : ∀ (f : ℕ → ℝ), ∑ i ∈ range (L + 1), W * f i / 2 ^ (2 * L) * gridNode L (2 * i + 1) ^ j =
      W / 2 ^ (2 * L) * ∑ i ∈ range (L + 1), f i * gridNode L (2 * i + 1) ^ j := by
    intro f; rw [mul_sum]; refine sum_congr rfl (fun i _ => by ring)
  have e' : ∀ (f : ℕ → ℝ), ∑ i ∈ range (L + 1), W * f i / 2 ^ (2 * L) * gridNode L (2 * i) ^ j =
      W / 2 ^ (2 * L) * ∑ i ∈ range (L + 1), f i * gridNode L (2 * i) ^ j := by
    intro f; rw [mul_sum]; refine sum_congr rfl (fun i _ => by ring)
  rw [e (fun i => ((2 * L + 1).choose (2 * i + 1) : ℝ)), e' (fun i => ((2 * L + 1).choose (2 * i) : ℝ)), hm]

/-- **Theorem `thm:quantity` (i), the paper's error form.** For any probe with `∑ |v_t| ≤ V` and any test, the worse
of the two error probabilities is at least `(1 - K* V δ² / (2σ)) / 2`. -/
theorem p1_thm_quantity_worst_error (a κ q ηbar δ ε s : ℝ) (ha : 0 ≤ a) (hκ : 0 < κ) (hq : 0 ≤ q)
    (hε : 0 < ε) (hδ : 0 < δ) (hlo : ε ≤ ηbar - δ) (hhi : ηbar + δ ≤ 1 - ε)
    (hs : a + κ * q ≤ s) (hs1 : s < 1) (T : ℕ) (v : ℕ → ℝ) (V : ℝ) (hV : ∑ t ∈ range T, |v t| ≤ V)
    (variance : ℝ≥0) (hv : variance ≠ 0) (A : Set (ObservationRecord T)) (hA : MeasurableSet A) :
    (1 - (2 * κ ^ 2 * q / (ε ^ 3 * (1 - s) ^ 2)) * V * δ ^ 2 / (2 * sqrt (variance : ℝ))) / 2 ≤
      max ((gaussianRecordLaw T (fun t => (controlledCohortRun a κ ![q / 2, q / 2] ![ηbar - δ, ηbar + δ] v
          (t.val + 1)).price) variance).real A)
        ((gaussianRecordLaw T (fun t => (controlledCohortRun a κ ![q] ![ηbar] v (t.val + 1)).price)
          variance).real Aᶜ) := by
  set K := 2 * κ ^ 2 * q / (ε ^ 3 * (1 - s) ^ 2) with hK
  have hvpos : (0 : ℝ) < variance := lt_of_le_of_ne variance.2 (by exact_mod_cast hv.symm)
  have hV0 : 0 ≤ V := le_trans (sum_nonneg (fun _ _ => abs_nonneg _)) hV
  have hK0 : 0 ≤ K :=
    div_nonneg (mul_nonneg (by positivity) hq) (mul_nonneg (pow_nonneg hε.le 3) (sq_nonneg _))
  have hkl := p1_thm_quantity_kl a κ q ηbar δ ε s ha hκ hq hε hδ hlo hhi hs hs1 T v V hV variance hv
  have h := p1_worst_error_ge _ _ hA (K ^ 2 * V ^ 2 * δ ^ 4 / (2 * (variance : ℝ))) (by positivity) hkl
  have hsq : sqrt (K ^ 2 * V ^ 2 * δ ^ 4 / (2 * (variance : ℝ)) / 2) = K * V * δ ^ 2 / (2 * sqrt (variance : ℝ)) := by
    have hs0 : 0 < sqrt (variance : ℝ) := sqrt_pos.mpr hvpos
    have h4 : (2 * sqrt (variance : ℝ)) ^ 2 = 4 * (variance : ℝ) := by
      rw [mul_pow, sq_sqrt hvpos.le]; norm_num
    have e : K ^ 2 * V ^ 2 * δ ^ 4 / (2 * (variance : ℝ)) / 2 = (K * V * δ ^ 2 / (2 * sqrt (variance : ℝ))) ^ 2 := by
      rw [div_pow (K * V * δ ^ 2) (2 * sqrt (variance : ℝ)) 2, h4]; ring
    rw [e, sqrt_sq (div_nonneg (mul_nonneg (mul_nonneg hK0 hV0) (sq_nonneg δ)) (by positivity))]
  rw [hsq] at h
  exact h

/-- **Theorem `thm:quantity` (i): quantity needed at every error level.** Errors at most `α₀` and `β₀` need
`4σ²(1 - α₀ - β₀)² ≤ K*² V² δ⁴`, i.e. `V ≥ 2σ(1-α₀-β₀)/(K* δ²)`. -/
theorem p1_thm_quantity_test_general (a κ q ηbar δ ε s : ℝ) (ha : 0 ≤ a) (hκ : 0 < κ) (hq : 0 ≤ q)
    (hε : 0 < ε) (hδ : 0 < δ) (hlo : ε ≤ ηbar - δ) (hhi : ηbar + δ ≤ 1 - ε)
    (hs : a + κ * q ≤ s) (hs1 : s < 1) (T : ℕ) (v : ℕ → ℝ) (V : ℝ) (hV : ∑ t ∈ range T, |v t| ≤ V)
    (variance : ℝ≥0) (hv : variance ≠ 0) (α₀ β₀ : ℝ) (hab : α₀ + β₀ ≤ 1)
    (A : Set (ObservationRecord T)) (hA : MeasurableSet A)
    (herrδ : (gaussianRecordLaw T (fun t => (controlledCohortRun a κ ![q / 2, q / 2] ![ηbar - δ, ηbar + δ] v
      (t.val + 1)).price) variance).real A ≤ α₀)
    (herr0 : (gaussianRecordLaw T (fun t => (controlledCohortRun a κ ![q] ![ηbar] v
      (t.val + 1)).price) variance).real Aᶜ ≤ β₀) :
    4 * (variance : ℝ) * (1 - α₀ - β₀) ^ 2 ≤ (2 * κ ^ 2 * q / (ε ^ 3 * (1 - s) ^ 2)) ^ 2 * V ^ 2 * δ ^ 4 := by
  have hkl := (p1_test_error_kl_lower_bound_general _ _ hA α₀ β₀ hab herrδ herr0).trans
    (p1_thm_quantity_kl a κ q ηbar δ ε s ha hκ hq hε hδ hlo hhi hs hs1 T v V hV variance hv)
  have hvpos : (0 : ℝ) < variance := lt_of_le_of_ne variance.2 (by exact_mod_cast hv.symm)
  rw [ENNReal.ofReal_le_ofReal_iff (by positivity), le_div_iff₀ (by positivity)] at hkl
  nlinarith

/-- **Lemma `thm:capital`: capital needed at every error level** (paper's form `B ≥ 2σ²m(1-2α)²/(K*²δ⁴)`). -/
theorem p1_thm_capital_test_general (a κ q ηbar δ ε s : ℝ) (ha : 0 ≤ a) (hκ : 0 < κ) (hq : 0 ≤ q)
    (hε : 0 < ε) (hδ : 0 < δ) (hlo : ε ≤ ηbar - δ) (hhi : ηbar + δ ≤ 1 - ε)
    (hs : a + κ * q ≤ s) (hs1 : s < 1) :
    ∃ m > 0, ∀ (T : ℕ) (v : Fin T → ℝ) (B P fee : ℝ) (variance : ℝ≥0), variance ≠ 0 → 0 ≤ fee →
      0 ≤ equity (traderCashAfter B P κ fee (actualCohortImpulse a κ ![q] ![ηbar]) v) (∑ i, v i) P →
      ∀ (α₀ β₀ : ℝ), α₀ + β₀ < 1 → ∀ A : Set (ObservationRecord T), MeasurableSet A →
      (gaussianRecordLaw T (fun t => (controlledCohortRun a κ ![q / 2, q / 2] ![ηbar - δ, ηbar + δ]
          (extendFiniteProbe v) (t.val + 1)).price) variance).real A ≤ α₀ →
      (gaussianRecordLaw T (fun t => (controlledCohortRun a κ ![q] ![ηbar] (extendFiniteProbe v)
          (t.val + 1)).price) variance).real Aᶜ ≤ β₀ →
      2 * (variance : ℝ) * m * (1 - α₀ - β₀) ^ 2 ≤ (2 * κ ^ 2 * q / (ε ^ 3 * (1 - s) ^ 2)) ^ 2 * B * δ ^ 4 := by
  obtain ⟨m, hm0, hkl⟩ := p1_thm_capital_kl a κ q ηbar δ ε s ha hκ hq hε hδ hlo hhi hs hs1
  refine ⟨m, hm0, fun T v B P fee variance hv hfee hsolv α₀ β₀ hab A hA herrδ herr0 => ?_⟩
  have hvpos : (0 : ℝ) < variance := lt_of_le_of_ne variance.2 (by exact_mod_cast hv.symm)
  have h := (p1_test_error_kl_lower_bound_general _ _ hA α₀ β₀ hab.le herrδ herr0).trans
    (hkl T v B P fee variance hv hfee hsolv)
  have hmv : 0 < (variance : ℝ) * m := mul_pos hvpos hm0
  have hpos : 0 < 2 * (1 - α₀ - β₀) ^ 2 := by have : 0 < 1 - α₀ - β₀ := by linarith
                                              positivity
  rcases ENNReal.ofReal_le_ofReal_iff'.mp h with h1 | h1
  · rw [le_div_iff₀ hmv] at h1; nlinarith
  · linarith

end CurrentMM
