import CurrentProofs.CohortConvolution
import Mathlib.Data.Finset.Lattice.Fold

namespace CurrentMM
noncomputable section
open scoped BigOperators

def alignedSign (x : ℝ) : ℝ := if 0 ≤ x then 1 else -1
theorem aligned_sign_abs (x : ℝ) : |alignedSign x| = 1 := by
  unfold alignedSign
  split_ifs <;> norm_num
theorem aligned_sign_product (x : ℝ) : x * alignedSign x = |x| := by
  unfold alignedSign
  split_ifs with hx
  · simp [abs_of_nonneg hx]
  · simp [abs_of_neg (lt_of_not_ge hx)]

def scalarProbeQuantity {T : ℕ} (v : Fin T → ℝ) : ℝ := ∑ i, |v i|
def scalarWindowOutput {T : ℕ} (background : ℝ) (coeff v : Fin T → ℝ) : ℝ :=
  background + ∑ i, coeff i * v i
def scalarWindowLoad {T : ℕ} (background reserve fee : ℝ) (coeff v : Fin T → ℝ) : ℝ :=
  |scalarWindowOutput background coeff v| + reserve + fee * scalarProbeQuantity v

theorem scalar_window_envelope_bound {T : ℕ} (background reserve fee gain V : ℝ)
    (coeff v : Fin T → ℝ) (hg : 0 ≤ gain) (hc : 0 ≤ fee)
    (hcoeff : ∀ i, |coeff i| ≤ gain) (hbudget : scalarProbeQuantity v ≤ V) :
    scalarWindowLoad background reserve fee coeff v ≤
      |background| + reserve + (gain + fee) * V := by
  have hsum : |∑ i, coeff i * v i| ≤ gain * scalarProbeQuantity v := by
    calc
      _ ≤ ∑ i, |coeff i * v i| := Finset.abs_sum_le_sum_abs _ _
      _ ≤ gain * scalarProbeQuantity v := by
        simp only [scalarProbeQuantity, abs_mul, Finset.mul_sum]
        exact Finset.sum_le_sum fun i _ =>
          mul_le_mul_of_nonneg_right (hcoeff i) (abs_nonneg _)
  have htriangle := abs_add_le background (∑ i, coeff i * v i)
  have hcap := mul_le_mul_of_nonneg_left hbudget (add_nonneg hg hc)
  unfold scalarWindowLoad scalarWindowOutput
  linarith

def scalarWorstPulse {T : ℕ} (background V : ℝ) (coeff : Fin T → ℝ) (chosen : Fin T) : Fin T → ℝ :=
  fun i => if i = chosen then V * alignedSign background * alignedSign (coeff chosen) else 0

theorem scalar_worst_pulse_quantity {T : ℕ} (background V : ℝ)
    (coeff : Fin T → ℝ) (chosen : Fin T) (hV : 0 ≤ V) :
    scalarProbeQuantity (scalarWorstPulse background V coeff chosen) = V := by
  have hpoint (i : Fin T) : |scalarWorstPulse background V coeff chosen i| =
      (if i = chosen then V else 0) := by
    unfold scalarWorstPulse
    split_ifs <;> simp [abs_mul, aligned_sign_abs, abs_of_nonneg hV]
  unfold scalarProbeQuantity
  simp_rw [hpoint]
  simp

theorem scalar_worst_pulse_output {T : ℕ} (background V : ℝ)
    (coeff : Fin T → ℝ) (chosen : Fin T) (hV : 0 ≤ V) :
    |scalarWindowOutput background coeff (scalarWorstPulse background V coeff chosen)| =
      |background| + |coeff chosen| * V := by
  have hsum : (∑ i, coeff i * scalarWorstPulse background V coeff chosen i) =
      alignedSign background * |coeff chosen| * V := by
    simp only [scalarWorstPulse, mul_ite, mul_zero, Finset.sum_ite_eq', Finset.mem_univ, if_true]
    calc
      _ = (coeff chosen * alignedSign (coeff chosen)) * alignedSign background * V := by ring
      _ = _ := by rw [aligned_sign_product]; ring
  unfold scalarWindowOutput
  rw [hsum]
  unfold alignedSign
  split_ifs with hb
  · have hp : 0 ≤ background + 1 * |coeff chosen| * V := by positivity
    rw [abs_of_nonneg hp, abs_of_nonneg hb]
    ring
  · have hp : background + -1 * |coeff chosen| * V ≤ 0 := by
      nlinarith [mul_nonneg (abs_nonneg (coeff chosen)) hV]
    rw [abs_of_nonpos hp, abs_of_neg (lt_of_not_ge hb)]
    ring

theorem exact_scalar_window_budget {T : ℕ} (background reserve fee gain V B : ℝ)
    (coeff : Fin T → ℝ) (chosen : Fin T) (hV : 0 ≤ V) (hc : 0 ≤ fee)
    (hcoeff : ∀ i, |coeff i| ≤ gain) (hpeak : |coeff chosen| = gain) :
    (∀ v : Fin T → ℝ, scalarProbeQuantity v ≤ V →
      scalarWindowLoad background reserve fee coeff v ≤ B) ↔
      |background| + reserve + (gain + fee) * V ≤ B := by
  have hg : 0 ≤ gain := hpeak ▸ abs_nonneg (coeff chosen)
  constructor
  · intro hall
    have hp := hall (scalarWorstPulse background V coeff chosen)
      (le_of_eq (scalar_worst_pulse_quantity background V coeff chosen hV))
    unfold scalarWindowLoad at hp
    rw [scalar_worst_pulse_output background V coeff chosen hV,
      scalar_worst_pulse_quantity background V coeff chosen hV, hpeak] at hp
    nlinarith
  · intro hb v hv
    exact le_trans (scalar_window_envelope_bound background reserve fee gain V coeff v hg hc hcoeff hv) hb

theorem positive_window_gain_cap (background reserve fee gain V B : ℝ)
    (hden : 0 < gain + fee) :
    |background| + reserve + (gain + fee) * V ≤ B ↔
      V ≤ (B - reserve - |background|) / (gain + fee) := by
  rw [le_div_iff₀ hden]
  constructor <;> intro h <;> nlinarith

theorem zero_window_gain_feasibility (background reserve fee gain V B : ℝ)
    (hzero : gain + fee = 0) :
    |background| + reserve + (gain + fee) * V ≤ B ↔ |background| + reserve ≤ B := by
  rw [hzero]
  simp

theorem finite_window_minimum_cap {ι : Type*} [DecidableEq ι]
    (times : Finset ι) (hne : times.Nonempty) (background gain : ι → ℝ)
    (B reserve fee V : ℝ) (hden : ∀ t ∈ times, 0 < gain t + fee) :
    (∀ t ∈ times, |background t| + reserve + (gain t + fee) * V ≤ B) ↔
      V ≤ times.inf' hne (fun t => (B - reserve - |background t|) / (gain t + fee)) := by
  rw [Finset.le_inf'_iff]
  constructor <;> intro h t ht
  · exact (positive_window_gain_cap _ _ _ _ _ _ (hden t ht)).1 (h t ht)
  · exact (positive_window_gain_cap _ _ _ _ _ _ (hden t ht)).2 (h t ht)

def carriedLinearRun {E : Type*} [AddCommGroup E] [Module ℝ E]
    (A : Module.End ℝ E) (H z0 : E) (v : ℕ → ℝ) : ℕ → E
  | 0 => z0
  | t + 1 => A (carriedLinearRun A H z0 v t) + v t • H

theorem actual_carried_state_superposition {E : Type*} [AddCommGroup E] [Module ℝ E]
    (A : Module.End ℝ E) (H z0 : E) (v : ℕ → ℝ) (t : ℕ) :
    carriedLinearRun A H z0 v t = (A ^ t) z0 + controlledLinearRun A H v t := by
  induction t with
  | zero => simp [carriedLinearRun, controlledLinearRun]
  | succ t ih =>
    rw [carriedLinearRun, ih, map_add, controlledLinearRun, pow_succ']
    simp only [Module.End.mul_apply]
    abel

theorem actual_carried_monetary_output {E : Type*} [AddCommGroup E] [Module ℝ E]
    (A : Module.End ℝ E) (C : E →ₗ[ℝ] ℝ) (H z0 : E) (v : ℕ → ℝ) (t : ℕ) :
    C (carriedLinearRun A H z0 v t) = C ((A ^ t) z0) +
      ∑ j ∈ Finset.range t, v j * C ((A ^ (t - 1 - j)) H) := by
  rw [actual_carried_state_superposition, map_add, reset_linear_run_convolution, map_sum]
  simp [map_smul]

def transformedTransition {E F : Type*} [AddCommGroup E] [AddCommGroup F]
    [Module ℝ E] [Module ℝ F] (T : E ≃ₗ[ℝ] F) (A : Module.End ℝ E) : Module.End ℝ F :=
  T.toLinearMap.comp (A.comp T.symm.toLinearMap)

theorem actual_coordinate_power_invariance {E F : Type*} [AddCommGroup E] [AddCommGroup F]
    [Module ℝ E] [Module ℝ F] (T : E ≃ₗ[ℝ] F) (A : Module.End ℝ E) (z : E) (t : ℕ) :
    (transformedTransition T A ^ t) (T z) = T ((A ^ t) z) := by
  induction t with
  | zero => simp
  | succ t ih =>
    rw [pow_succ', pow_succ']
    change transformedTransition T A ((transformedTransition T A ^ t) (T z)) =
      T (A ((A ^ t) z))
    rw [ih]
    simp [transformedTransition]

theorem actual_monetary_coordinate_invariance {E F : Type*} [AddCommGroup E] [AddCommGroup F]
    [Module ℝ E] [Module ℝ F] (T : E ≃ₗ[ℝ] F) (A : Module.End ℝ E)
    (C : E →ₗ[ℝ] ℝ) (z : E) (t : ℕ) :
    (C.comp T.symm.toLinearMap) ((transformedTransition T A ^ t) (T z)) = C ((A ^ t) z) := by
  rw [actual_coordinate_power_invariance]
  simp

theorem actual_quantity_unit_state_invariance {E : Type*} [AddCommGroup E] [Module ℝ E]
    (A : Module.End ℝ E) (H z0 : E) (v : ℕ → ℝ) (scale : ℝ) (hs : scale ≠ 0) (t : ℕ) :
    carriedLinearRun A (scale⁻¹ • H) z0 (fun j => scale * v j) t = carriedLinearRun A H z0 v t := by
  induction t with
  | zero => rfl
  | succ t ih =>
    rw [carriedLinearRun, carriedLinearRun, ih, smul_smul]
    congr 1
    congr 1
    field_simp

theorem quantity_unit_budget_invariance {T : ℕ} (v : Fin T → ℝ) (scale : ℝ) (hs : 0 < scale) :
    scalarProbeQuantity (fun j => scale * v j) = scale * scalarProbeQuantity v := by
  simp [scalarProbeQuantity, abs_mul, abs_of_pos hs, Finset.mul_sum]

theorem quantity_unit_envelope_invariance (background reserve fee gain V scale : ℝ)
    (hs : scale ≠ 0) :
    |background| + reserve + (gain / scale + fee / scale) * (scale * V) =
      |background| + reserve + (gain + fee) * V := by
  field_simp [hs] <;> ring

theorem uncarried_window_reset_counterexample :
    (9 / 10 : ℝ) * 1 + 1 = 19 / 10 ∧ (9 / 10 : ℝ) * 1 + (1 / 10) = 1 := by
  norm_num

theorem finite_scalar_maximum_gain {T : ℕ} (coeff : Fin (T + 1) → ℝ) :
    ∃ chosen : Fin (T + 1), ∀ i, |coeff i| ≤ |coeff chosen| := by
  obtain ⟨chosen, hc, hmax⟩ := Finset.exists_max_image Finset.univ (fun i => |coeff i|)
    ⟨0, Finset.mem_univ _⟩
  exact ⟨chosen, fun i => hmax i (Finset.mem_univ _)⟩

theorem prefix_quantity_budget (v : ℕ → ℝ) (t N : ℕ) (V : ℝ)
    (ht : t ≤ N) (hbudget : ∑ j ∈ Finset.range N, |v j| ≤ V) :
    scalarProbeQuantity (fun j : Fin t => v j.val) ≤ V := by
  have hp : (∑ j ∈ Finset.range t, |v j|) ≤ ∑ j ∈ Finset.range N, |v j| :=
    Finset.sum_le_sum_of_subset_of_nonneg (Finset.range_mono ht) (fun _ _ _ => abs_nonneg _)
  rw [Finset.sum_range] at hp
  exact le_trans hp hbudget

theorem actual_monetary_prefix_gate {E : Type*} [AddCommGroup E] [Module ℝ E]
    (A : Module.End ℝ E) (C : E →ₗ[ℝ] ℝ) (H z0 : E) (v : ℕ → ℝ)
    (t N : ℕ) (reserve fee gain V : ℝ) (ht : t ≤ N) (hg : 0 ≤ gain) (hc : 0 ≤ fee)
    (hcoeff : ∀ j : Fin t, |C ((A ^ (t - 1 - j.val)) H)| ≤ gain)
    (hbudget : ∑ j ∈ Finset.range N, |v j| ≤ V) :
    |C (carriedLinearRun A H z0 v t)| + reserve + fee * ∑ j ∈ Finset.range t, |v j| ≤
      |C ((A ^ t) z0)| + reserve + (gain + fee) * V := by
  have hb := prefix_quantity_budget v t N V ht hbudget
  have heq : C (carriedLinearRun A H z0 v t) = scalarWindowOutput (C ((A ^ t) z0))
      (fun j : Fin t => C ((A ^ (t - 1 - j.val)) H)) (fun j => v j.val) := by
    rw [actual_carried_monetary_output, Finset.sum_range]
    simp [scalarWindowOutput, mul_comm]
  rw [heq, Finset.sum_range]
  exact scalar_window_envelope_bound _ reserve fee gain V _ _ hg hc hcoeff hb

end
end CurrentMM
