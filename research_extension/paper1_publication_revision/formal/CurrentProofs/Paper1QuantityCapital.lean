import CurrentProofs.Paper1MergedSeparation
import CurrentProofs.ZeroAnchorKernel
import CurrentProofs.Execution
import CurrentProofs.Paper1PassiveRecord

/-!
# Paper 1, Theorem `thm:quantity` (i) and Lemma `thm:capital`: divergence bounds for the known pair

The known pair: one cohort of weight `q` at rate `η̄` against two cohorts of weight `q/2` at `η̄ ± δ`, rates in
`[ε, 1-ε]`, `a ≥ 0`, `κ > 0`, `a + κ q ≤ s < 1`, `K* = 2κ²q / (ε³(1-s)²)`.

* `p1_pair_record_kl_energy`: for any deterministic probe, the divergence of the two `T`-price records is at most
  `K*² δ⁴ ∑ v_t² / (2σ²)`;
* `p1_thm_quantity_kl`: for a probe with `∑ |v_t| ≤ V`, it is at most `K*² V² δ⁴ / (2σ²)` (Theorem `thm:quantity` (i)),
  so a test with both errors at most `1/4` needs `V² ≥ σ² / (2 K*² δ⁴)`;
* `p1_thm_capital_kl`: there is `m > 0`, depending only on the single-cohort economy, such that every probe that
  leaves a trader with cash `B` solvent at the fundamental mark has divergence at most `K*² B δ⁴ / (σ² m)`
  (Lemma `thm:capital`), so a test with both errors at most `1/4` needs `B ≥ σ² m / (4 K*² δ⁴)`.
-/

namespace CurrentMM

open Finset MeasureTheory ProbabilityTheory InformationTheory
open scoped ENNReal NNReal

/-- **Divergence of the two price records, in terms of probe energy.** -/
theorem p1_pair_record_kl_energy (a κ q ηbar δ ε s : ℝ) (ha : 0 ≤ a) (hκ : 0 < κ) (hq : 0 ≤ q)
    (hε : 0 < ε) (hδ : 0 < δ) (hlo : ε ≤ ηbar - δ) (hhi : ηbar + δ ≤ 1 - ε)
    (hs : a + κ * q ≤ s) (hs1 : s < 1) (T : ℕ) (v : ℕ → ℝ) (variance : ℝ≥0) (hv : variance ≠ 0) :
    klDiv (gaussianRecordLaw T (fun t => (controlledCohortRun a κ ![q / 2, q / 2] ![ηbar - δ, ηbar + δ] v
        (t.val + 1)).price) variance)
      (gaussianRecordLaw T (fun t => (controlledCohortRun a κ ![q] ![ηbar] v (t.val + 1)).price) variance) ≤
      ENNReal.ofReal ((2 * κ ^ 2 * q / (ε ^ 3 * (1 - s) ^ 2)) ^ 2 * δ ^ 4 * (∑ t ∈ range T, v t ^ 2) /
        (2 * (variance : ℝ))) := by
  set qδ : Fin 2 → ℝ := ![q / 2, q / 2]
  set rδ : Fin 2 → ℝ := ![ηbar - δ, ηbar + δ]
  set q0 : Fin 1 → ℝ := ![q]
  set r0 : Fin 1 → ℝ := ![ηbar]
  set hδf := actualCohortImpulse a κ qδ rδ with hhδf
  set h0f := actualCohortImpulse a κ q0 r0 with hh0f
  have hkδ : ∀ m, cohortKernel qδ rδ m =
      q / 2 * (ηbar - δ) * (1 - (ηbar - δ)) ^ m + q / 2 * (ηbar + δ) * (1 - (ηbar + δ)) ^ m := by
    intro m; simp [cohortKernel, qδ, rδ, Fin.sum_univ_two]
  have hk0 : ∀ m, cohortKernel q0 r0 m = q * ηbar * (1 - ηbar) ^ m := by
    intro m; simp [cohortKernel, q0, r0]
  have hη0 : 0 ≤ ηbar - δ := by linarith
  have hKδ : ∀ n, ∑ m ∈ range n, |cohortKernel qδ rδ m| ≤ q := by
    intro n
    simp only [hkδ]
    calc ∑ m ∈ range n, |q / 2 * (ηbar - δ) * (1 - (ηbar - δ)) ^ m + q / 2 * (ηbar + δ) * (1 - (ηbar + δ)) ^ m|
        ≤ ∑ m ∈ range n, (|q / 2 * (ηbar - δ) * (1 - (ηbar - δ)) ^ m| +
            |q / 2 * (ηbar + δ) * (1 - (ηbar + δ)) ^ m|) := sum_le_sum (fun m _ => abs_add_le _ _)
      _ ≤ q / 2 + q / 2 := by
          rw [sum_add_distrib]
          exact add_le_add (p1_single_kernel_l1 _ _ (by positivity) hη0 (by linarith) n)
            (p1_single_kernel_l1 _ _ (by positivity) (by linarith) (by linarith) n)
      _ = q := by ring
  have hK0 : ∀ n, ∑ m ∈ range n, |cohortKernel q0 r0 m| ≤ q := by
    intro n; simp only [hk0]
    exact p1_single_kernel_l1 _ _ hq (by linarith) (by linarith) n
  have hstab : |a| + |κ| * q ≤ s := by rw [abs_of_nonneg ha, abs_of_pos hκ]; exact hs
  have hH1 := p1_response_l1 a κ q s (cohortKernel q0 r0) h0f (p1_impulse_zero a κ q0 r0)
    (p1_impulse_closed_loop_recursion a κ q0 r0) hK0 hstab hs1
  have hE : ∀ n, ∑ m ∈ range n, |cohortKernel qδ rδ m - cohortKernel q0 r0 m| ≤ 2 * q * δ ^ 2 / ε ^ 3 := by
    intro n; simp only [hkδ, hk0]
    exact p1_split_kernel_gap q ηbar δ ε hq hε hδ.le hlo hhi n
  have hD := p1_response_diff_l1 a κ q s (2 * q * δ ^ 2 / ε ^ 3) (|κ| / (1 - s)) (cohortKernel qδ rδ)
    (cohortKernel q0 r0) hδf h0f (p1_impulse_zero a κ qδ rδ) (p1_impulse_zero a κ q0 r0)
    (p1_impulse_closed_loop_recursion a κ qδ rδ) (p1_impulse_closed_loop_recursion a κ q0 r0)
    hKδ hstab hs1 hE hH1
  set C := 2 * κ ^ 2 * q / (ε ^ 3 * (1 - s) ^ 2) with hC
  have hs1' : 0 < 1 - s := by linarith
  have hDval : |κ| * (2 * q * δ ^ 2 / ε ^ 3) * (|κ| / (1 - s)) / (1 - s) = C * δ ^ 2 := by
    rw [abs_of_pos hκ, hC]; field_simp
  rw [hDval] at hD
  have hen := p1_conv_energy (fun t => hδf t - h0f t) v (C * δ ^ 2) hD T
  rw [gaussian_record_equal_variance_kl _ _ variance hv]
  have hdiff : ∀ t : Fin T, (controlledCohortRun a κ qδ rδ v (t.val + 1)).price -
      (controlledCohortRun a κ q0 r0 v (t.val + 1)).price =
      ∑ u ∈ range (t.val + 1), v u * (hδf (t.val - u) - h0f (t.val - u)) := by
    intro t
    rw [actual_reset_price_convolution, actual_reset_price_convolution, ← sum_sub_distrib]
    exact sum_congr rfl (fun u _ => by rw [mul_sub])
  simp only [hdiff]
  rw [Fin.sum_univ_eq_sum_range (fun t => (∑ u ∈ range (t + 1), v u * (hδf (t - u) - h0f (t - u))) ^ 2) T]
  have hvpos : (0 : ℝ) < variance := lt_of_le_of_ne variance.2 (by exact_mod_cast hv.symm)
  apply ENNReal.ofReal_le_ofReal
  rw [div_le_div_iff_of_pos_right (by positivity)]
  calc ∑ t ∈ range T, (∑ u ∈ range (t + 1), v u * (hδf (t - u) - h0f (t - u))) ^ 2
      ≤ (C * δ ^ 2) ^ 2 * ∑ t ∈ range T, v t ^ 2 := hen
    _ = C ^ 2 * δ ^ 4 * ∑ t ∈ range T, v t ^ 2 := by ring

/-- **Theorem `thm:quantity` (i), formal.** -/
theorem p1_thm_quantity_kl (a κ q ηbar δ ε s : ℝ) (ha : 0 ≤ a) (hκ : 0 < κ) (hq : 0 ≤ q)
    (hε : 0 < ε) (hδ : 0 < δ) (hlo : ε ≤ ηbar - δ) (hhi : ηbar + δ ≤ 1 - ε)
    (hs : a + κ * q ≤ s) (hs1 : s < 1) (T : ℕ) (v : ℕ → ℝ) (V : ℝ) (hV : ∑ t ∈ range T, |v t| ≤ V)
    (variance : ℝ≥0) (hv : variance ≠ 0) :
    klDiv (gaussianRecordLaw T (fun t => (controlledCohortRun a κ ![q / 2, q / 2] ![ηbar - δ, ηbar + δ] v
        (t.val + 1)).price) variance)
      (gaussianRecordLaw T (fun t => (controlledCohortRun a κ ![q] ![ηbar] v (t.val + 1)).price) variance) ≤
      ENNReal.ofReal ((2 * κ ^ 2 * q / (ε ^ 3 * (1 - s) ^ 2)) ^ 2 * V ^ 2 * δ ^ 4 / (2 * (variance : ℝ))) := by
  refine (p1_pair_record_kl_energy a κ q ηbar δ ε s ha hκ hq hε hδ hlo hhi hs hs1 T v variance hv).trans ?_
  apply ENNReal.ofReal_le_ofReal
  have hvpos : (0 : ℝ) < variance := lt_of_le_of_ne variance.2 (by exact_mod_cast hv.symm)
  rw [div_le_div_iff_of_pos_right (by positivity)]
  have hsq : ∑ t ∈ range T, v t ^ 2 ≤ V ^ 2 := by
    have h1 := p1_sq_sum_le_sq_abs_sum (range T) v
    have h0 : 0 ≤ ∑ t ∈ range T, |v t| := sum_nonneg (fun _ _ => abs_nonneg _)
    exact h1.trans (pow_le_pow_left₀ h0 hV 2)
  have hC : 0 ≤ (2 * κ ^ 2 * q / (ε ^ 3 * (1 - s) ^ 2)) ^ 2 * δ ^ 4 := by positivity
  nlinarith [mul_le_mul_of_nonneg_left hsq hC]

/-- **Quantity needed by a test.** -/
theorem p1_thm_quantity_test (a κ q ηbar δ ε s : ℝ) (ha : 0 ≤ a) (hκ : 0 < κ) (hq : 0 ≤ q)
    (hε : 0 < ε) (hδ : 0 < δ) (hlo : ε ≤ ηbar - δ) (hhi : ηbar + δ ≤ 1 - ε)
    (hs : a + κ * q ≤ s) (hs1 : s < 1) (T : ℕ) (v : ℕ → ℝ) (V : ℝ) (hV : ∑ t ∈ range T, |v t| ≤ V)
    (variance : ℝ≥0) (hv : variance ≠ 0) (A : Set (ObservationRecord T)) (hA : MeasurableSet A)
    (herrδ : (gaussianRecordLaw T (fun t => (controlledCohortRun a κ ![q / 2, q / 2] ![ηbar - δ, ηbar + δ] v
      (t.val + 1)).price) variance).real A ≤ 1 / 4)
    (herr0 : (gaussianRecordLaw T (fun t => (controlledCohortRun a κ ![q] ![ηbar] v
      (t.val + 1)).price) variance).real Aᶜ ≤ 1 / 4) :
    (variance : ℝ) ≤ 2 * (2 * κ ^ 2 * q / (ε ^ 3 * (1 - s) ^ 2)) ^ 2 * V ^ 2 * δ ^ 4 := by
  have hkl := (p1_test_error_kl_lower_bound _ _ hA herrδ herr0).trans
    (p1_thm_quantity_kl a κ q ηbar δ ε s ha hκ hq hε hδ hlo hhi hs hs1 T v V hV variance hv)
  have hvpos : (0 : ℝ) < variance := lt_of_le_of_ne variance.2 (by exact_mod_cast hv.symm)
  rw [ENNReal.ofReal_le_ofReal_iff (by positivity), le_div_iff₀ (by positivity)] at hkl
  linarith

/-- **Lemma `thm:capital`, formal.** There is `m > 0`, depending only on the single-cohort economy, such that every
probe after which a trader starting with cash `B` is solvent at the fundamental mark `P` gives divergence at most
`K*² B δ⁴ / (σ² m)`, and a test with both errors at most `1/4` then needs `B ≥ σ² m / (4 K*² δ⁴)`. -/
theorem p1_thm_capital_kl (a κ q ηbar δ ε s : ℝ) (ha : 0 ≤ a) (hκ : 0 < κ) (hq : 0 ≤ q)
    (hε : 0 < ε) (hδ : 0 < δ) (hlo : ε ≤ ηbar - δ) (hhi : ηbar + δ ≤ 1 - ε)
    (hs : a + κ * q ≤ s) (hs1 : s < 1) :
    ∃ m > 0, ∀ (T : ℕ) (v : Fin T → ℝ) (B P fee : ℝ) (variance : ℝ≥0), variance ≠ 0 → 0 ≤ fee →
      0 ≤ equity (traderCashAfter B P κ fee (actualCohortImpulse a κ ![q] ![ηbar]) v) (∑ i, v i) P →
      klDiv (gaussianRecordLaw T (fun t => (controlledCohortRun a κ ![q / 2, q / 2] ![ηbar - δ, ηbar + δ]
          (extendFiniteProbe v) (t.val + 1)).price) variance)
        (gaussianRecordLaw T (fun t => (controlledCohortRun a κ ![q] ![ηbar] (extendFiniteProbe v)
          (t.val + 1)).price) variance) ≤
        ENNReal.ofReal ((2 * κ ^ 2 * q / (ε ^ 3 * (1 - s) ^ 2)) ^ 2 * B * δ ^ 4 / ((variance : ℝ) * m)) := by
  have hη : 0 < ηbar ∧ ηbar ≤ 1 := ⟨by linarith, by linarith⟩
  obtain ⟨radius, ⟨hr0, hr1⟩, hen⟩ := actual_all_anchor_trader_energy_bound a κ ![q] ![ηbar] ha hκ
    (fun i => by fin_cases i; simpa using hq) (fun i => by fin_cases i; simpa using hη)
    (by simp; linarith)
  set m := κ * ((1 - radius) / (1 + radius)) with hm
  have hm0 : 0 < m := by rw [hm]; apply mul_pos hκ; apply div_pos <;> linarith
  refine ⟨m, hm0, fun T v B P fee variance hv hfee hsolv => ?_⟩
  have hE := hen T v B P fee hfee hsolv
  have hvpos : (0 : ℝ) < variance := lt_of_le_of_ne variance.2 (by exact_mod_cast hv.symm)
  refine (p1_pair_record_kl_energy a κ q ηbar δ ε s ha hκ hq hε hδ hlo hhi hs hs1 T (extendFiniteProbe v)
    variance hv).trans ?_
  apply ENNReal.ofReal_le_ofReal
  have hsum : ∑ t ∈ range T, extendFiniteProbe v t ^ 2 = probeEnergy v := by
    rw [probeEnergy, ← Fin.sum_univ_eq_sum_range (fun t => extendFiniteProbe v t ^ 2) T]
    exact sum_congr rfl (fun i _ => by simp [extendFiniteProbe, i.isLt])
  rw [hsum]
  have hEB : probeEnergy v ≤ 2 * B / m := by rw [hm]; exact hE
  set C2 := (2 * κ ^ 2 * q / (ε ^ 3 * (1 - s) ^ 2)) ^ 2 * δ ^ 4 with hC2
  have hC20 : 0 ≤ C2 := by positivity
  calc (2 * κ ^ 2 * q / (ε ^ 3 * (1 - s) ^ 2)) ^ 2 * δ ^ 4 * probeEnergy v / (2 * (variance : ℝ))
      = C2 * probeEnergy v / (2 * (variance : ℝ)) := by rw [hC2]
    _ ≤ C2 * (2 * B / m) / (2 * (variance : ℝ)) := by gcongr
    _ = (2 * κ ^ 2 * q / (ε ^ 3 * (1 - s) ^ 2)) ^ 2 * B * δ ^ 4 / ((variance : ℝ) * m) := by
        rw [hC2]; field_simp

/-- **Capital needed by a test.** With the margin constant `m` of `p1_thm_capital_kl`, a solvent probe whose test has
both error probabilities at most `1/4` needs `σ² m ≤ 4 K*² B δ⁴`. -/
theorem p1_thm_capital_test (a κ q ηbar δ ε s : ℝ) (ha : 0 ≤ a) (hκ : 0 < κ) (hq : 0 ≤ q)
    (hε : 0 < ε) (hδ : 0 < δ) (hlo : ε ≤ ηbar - δ) (hhi : ηbar + δ ≤ 1 - ε)
    (hs : a + κ * q ≤ s) (hs1 : s < 1) :
    ∃ m > 0, ∀ (T : ℕ) (v : Fin T → ℝ) (B P fee : ℝ) (variance : ℝ≥0), variance ≠ 0 → 0 ≤ fee →
      0 ≤ equity (traderCashAfter B P κ fee (actualCohortImpulse a κ ![q] ![ηbar]) v) (∑ i, v i) P →
      ∀ A : Set (ObservationRecord T), MeasurableSet A →
      (gaussianRecordLaw T (fun t => (controlledCohortRun a κ ![q / 2, q / 2] ![ηbar - δ, ηbar + δ]
          (extendFiniteProbe v) (t.val + 1)).price) variance).real A ≤ 1 / 4 →
      (gaussianRecordLaw T (fun t => (controlledCohortRun a κ ![q] ![ηbar] (extendFiniteProbe v)
          (t.val + 1)).price) variance).real Aᶜ ≤ 1 / 4 →
      (variance : ℝ) * m ≤ 4 * (2 * κ ^ 2 * q / (ε ^ 3 * (1 - s) ^ 2)) ^ 2 * B * δ ^ 4 := by
  obtain ⟨m, hm0, hkl⟩ := p1_thm_capital_kl a κ q ηbar δ ε s ha hκ hq hε hδ hlo hhi hs hs1
  refine ⟨m, hm0, fun T v B P fee variance hv hfee hsolv A hA herrδ herr0 => ?_⟩
  have hvpos : (0 : ℝ) < variance := lt_of_le_of_ne variance.2 (by exact_mod_cast hv.symm)
  have h := (p1_test_error_kl_lower_bound _ _ hA herrδ herr0).trans (hkl T v B P fee variance hv hfee hsolv)
  have hmv : 0 < (variance : ℝ) * m := mul_pos hvpos hm0
  rcases ENNReal.ofReal_le_ofReal_iff'.mp h with h1 | h1
  · rw [le_div_iff₀ hmv] at h1; linarith
  · norm_num at h1

end CurrentMM
