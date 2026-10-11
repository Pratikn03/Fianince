import CurrentProofs.Recursion
import CurrentProofs.CausalConvolution
import CurrentProofs.GaussianRecords
import CurrentProofs.PositiveDynamics
import Mathlib.Algebra.Module.LinearMap.End

namespace CurrentMM
noncomputable section
open scoped BigOperators NNReal ENNReal

def cohortCoordinates {n : ℕ} (state : CohortState n) : Option (Fin n) → ℝ :=
  fun i => i.elim state.price state.memory

def cohortLinearTransition {n : ℕ} (a impact : ℝ) (q rate : Fin n → ℝ) :
    Module.End ℝ (Option (Fin n) → ℝ) where
  toFun z := fun i => i.elim
    (a * z none + impact * ∑ j, q j * z (some j))
    (fun j => (1 - rate j) * z (some j) + rate j *
      (a * z none + impact * ∑ k, q k * z (some k)))
  map_add' z w := by
    funext i
    cases i <;> simp [mul_add, Finset.sum_add_distrib] <;> ring
  map_smul' c z := by
    have hs : (∑ j, q j * (c * z (some j))) = c * ∑ j, q j * z (some j) := by
      rw [Finset.mul_sum]
      apply Finset.sum_congr rfl
      intro j hj
      ring
    funext i
    cases i <;> simp [hs] <;> ring

def cohortInputVector {n : ℕ} (impact : ℝ) (rate : Fin n → ℝ) :
    Option (Fin n) → ℝ := fun i => i.elim impact (fun j => rate j * impact)

theorem actual_step_linear_coordinates {n : ℕ} (a impact quantity : ℝ)
    (q rate : Fin n → ℝ) (state : CohortState n) :
    cohortCoordinates (cohortStep a impact q rate quantity state) =
      cohortLinearTransition a impact q rate (cohortCoordinates state) +
        quantity • cohortInputVector impact rate := by
  funext i
  cases i <;> simp [cohortCoordinates, cohortStep, cohortLinearTransition,
    cohortInputVector] <;> ring

def controlledLinearRun {E : Type*} [AddCommGroup E] [Module ℝ E]
    (A : Module.End ℝ E) (b : E) (v : ℕ → ℝ) : ℕ → E
  | 0 => 0
  | t + 1 => A (controlledLinearRun A b v t) + v t • b

theorem reset_linear_run_convolution {E : Type*} [AddCommGroup E] [Module ℝ E]
    (A : Module.End ℝ E) (b : E) (v : ℕ → ℝ) (t : ℕ) :
    controlledLinearRun A b v t =
      ∑ s ∈ Finset.range t, v s • (A ^ (t - 1 - s)) b := by
  induction t with
  | zero => simp [controlledLinearRun]
  | succ t ih =>
    rw [controlledLinearRun, ih, map_sum, Finset.sum_range_succ]
    congr 1
    · apply Finset.sum_congr rfl
      intro s hs
      have hst : s < t := Finset.mem_range.mp hs
      have hexp : t + 1 - 1 - s = (t - 1 - s) + 1 := by omega
      rw [map_smul, hexp, pow_succ']
      rfl
    · simp

def controlledCohortRun {n : ℕ} (a impact : ℝ) (q rate : Fin n → ℝ)
    (v : ℕ → ℝ) : ℕ → CohortState n
  | 0 => zeroState n
  | t + 1 => cohortStep a impact q rate (v t) (controlledCohortRun a impact q rate v t)

theorem actual_reset_run_linear_coordinates {n : ℕ} (a impact : ℝ)
    (q rate : Fin n → ℝ) (v : ℕ → ℝ) (t : ℕ) :
    cohortCoordinates (controlledCohortRun a impact q rate v t) =
      controlledLinearRun (cohortLinearTransition a impact q rate)
        (cohortInputVector impact rate) v t := by
  induction t with
  | zero => funext i; cases i <;> rfl
  | succ t ih =>
    rw [controlledCohortRun, actual_step_linear_coordinates, ih]
    rfl

def actualCohortImpulse {n : ℕ} (a impact : ℝ) (q rate : Fin n → ℝ) (j : ℕ) : ℝ :=
  ((cohortLinearTransition a impact q rate ^ j) (cohortInputVector impact rate)) none

theorem actual_reset_price_convolution {n : ℕ} (a impact : ℝ)
    (q rate : Fin n → ℝ) (v : ℕ → ℝ) (t : ℕ) :
    (controlledCohortRun a impact q rate v (t + 1)).price =
      ∑ s ∈ Finset.range (t + 1), v s * actualCohortImpulse a impact q rate (t - s) := by
  have h := congrFun (actual_reset_run_linear_coordinates a impact q rate v (t + 1)) none
  rw [reset_linear_run_convolution] at h
  simpa [cohortCoordinates, actualCohortImpulse, Finset.sum_apply] using h

def extendFiniteProbe {T : ℕ} (v : Fin T → ℝ) (s : ℕ) : ℝ :=
  if hs : s < T then v ⟨s, hs⟩ else 0

def actualCohortPriceRecord {n T : ℕ} (a impact : ℝ)
    (q rate : Fin n → ℝ) (v : Fin T → ℝ) : EuclideanSpace ℝ (Fin T) :=
  WithLp.toLp 2 (fun t =>
    (controlledCohortRun a impact q rate (extendFiniteProbe v) (t.val + 1)).price)

theorem actual_cohort_record_is_causal_convolution {n T : ℕ} (a impact : ℝ)
    (q rate : Fin n → ℝ) (v : Fin T → ℝ) :
    actualCohortPriceRecord a impact q rate v =
      causalImpulseConvolution (actualCohortImpulse a impact q rate) v := by
  ext t
  change (controlledCohortRun a impact q rate (extendFiniteProbe v) (t.val + 1)).price = _
  rw [actual_reset_price_convolution]
  let f : ℕ → ℝ := fun s => if s ≤ t.val then
    extendFiniteProbe v s * actualCohortImpulse a impact q rate (t.val - s) else 0
  have hprefix : (∑ s ∈ Finset.range (t.val + 1),
      extendFiniteProbe v s * actualCohortImpulse a impact q rate (t.val - s)) =
      ∑ s ∈ Finset.range (t.val + 1), f s := by
    apply Finset.sum_congr rfl
    intro s hs
    have hst : s ≤ t.val := by have := Finset.mem_range.mp hs; omega
    simp [f, hst]
  have hsub : Finset.range (t.val + 1) ⊆ Finset.range T :=
    Finset.range_mono (by omega)
  have hext : (∑ s ∈ Finset.range (t.val + 1), f s) =
      ∑ s ∈ Finset.range T, f s := by
    apply Finset.sum_subset hsub
    intro s hs hn
    have hst : ¬ s ≤ t.val := by
      have := Finset.mem_range.mp hs
      have : ¬ s < t.val + 1 := by simpa using hn
      omega
    simp [f, hst]
  rw [hprefix, hext, Finset.sum_range]
  simp only [causalImpulseConvolution, causalImpulseColumn, WithLp.ofLp_sum,
    Finset.sum_apply, PiLp.smul_apply, PiLp.toLp_apply, smul_eq_mul]
  apply Finset.sum_congr rfl
  intro s hs
  have hiff : s.val ≤ t.val ↔ s ≤ t := Iff.rfl
  simp only [f, extendFiniteProbe, dif_pos s.is_lt, hiff]
  split_ifs <;> ring

theorem actual_cohort_record_quantity_bound {n T : ℕ} (a impact : ℝ)
    (q rate : Fin n → ℝ) (v : Fin T → ℝ) (V : ℝ)
    (hbudget : ∑ s, |v s| ≤ V) :
    ‖actualCohortPriceRecord a impact q rate v‖ ≤
      V * ‖finiteImpulseVector T (actualCohortImpulse a impact q rate)‖ := by
  rw [actual_cohort_record_is_causal_convolution]
  exact actual_convolution_quantity_bound _ _ _ hbudget

theorem actual_pair_price_record_difference {n m T : ℕ} (a impact : ℝ)
    (q0 rate0 : Fin n → ℝ) (q1 rate1 : Fin m → ℝ) (v : Fin T → ℝ) :
    actualCohortPriceRecord a impact q1 rate1 v -
      actualCohortPriceRecord a impact q0 rate0 v =
      causalImpulseConvolution (fun j => actualCohortImpulse a impact q1 rate1 j -
        actualCohortImpulse a impact q0 rate0 j) v := by
  rw [actual_cohort_record_is_causal_convolution, actual_cohort_record_is_causal_convolution]
  ext t
  simp only [causalImpulseConvolution, causalImpulseColumn, WithLp.ofLp_sum,
    Finset.sum_apply, PiLp.sub_apply, PiLp.smul_apply, PiLp.toLp_apply,
    smul_eq_mul, ← Finset.sum_sub_distrib]
  apply Finset.sum_congr rfl
  intro s hs
  split_ifs <;> ring

theorem actual_pair_observation_kl {n m T : ℕ} (a impact : ℝ)
    (q0 rate0 : Fin n → ℝ) (q1 rate1 : Fin m → ℝ) (v : Fin T → ℝ)
    (variance : ℝ≥0) (hv : variance ≠ 0) :
    InformationTheory.klDiv
      (gaussianRecordLaw T (fun t => actualCohortPriceRecord a impact q0 rate0 v t) variance)
      (gaussianRecordLaw T (fun t => actualCohortPriceRecord a impact q1 rate1 v t) variance) =
      ENNReal.ofReal (‖causalImpulseConvolution
        (fun j => actualCohortImpulse a impact q1 rate1 j -
          actualCohortImpulse a impact q0 rate0 j) v‖ ^ 2 / (2 * (variance : ℝ))) := by
  rw [gaussian_record_kl_euclidean_mean _ _ variance hv]
  have hneg : (WithLp.toLp 2 (fun t => actualCohortPriceRecord a impact q0 rate0 v t -
      actualCohortPriceRecord a impact q1 rate1 v t) : EuclideanSpace ℝ (Fin T)) =
      -(actualCohortPriceRecord a impact q1 rate1 v -
        actualCohortPriceRecord a impact q0 rate0 v) := by
    ext t
    simp
  rw [hneg, norm_neg, actual_pair_price_record_difference]

theorem actual_pair_quantity_kl_bound {n m T : ℕ} (a impact : ℝ)
    (q0 rate0 : Fin n → ℝ) (q1 rate1 : Fin m → ℝ) (v : Fin T → ℝ)
    (V : ℝ) (hV : 0 ≤ V) (hbudget : ∑ i, |v i| ≤ V)
    (variance : ℝ≥0) (hv : variance ≠ 0) :
    InformationTheory.klDiv
      (gaussianRecordLaw T (fun t => actualCohortPriceRecord a impact q0 rate0 v t) variance)
      (gaussianRecordLaw T (fun t => actualCohortPriceRecord a impact q1 rate1 v t) variance) ≤
      ENNReal.ofReal (V ^ 2 * ‖finiteImpulseVector T
        (fun j => actualCohortImpulse a impact q1 rate1 j -
          actualCohortImpulse a impact q0 rate0 j)‖ ^ 2 / (2 * (variance : ℝ))) := by
  rw [actual_pair_observation_kl _ _ _ _ _ _ _ _ hv]
  apply ENNReal.ofReal_le_ofReal
  apply div_le_div_of_nonneg_right _ (by positivity)
  have h := actual_convolution_quantity_bound
    (fun j => actualCohortImpulse a impact q1 rate1 j -
      actualCohortImpulse a impact q0 rate0 j) v V hbudget
  have hsq := (sq_le_sq₀ (norm_nonneg _) (by positivity)).2 h
  simpa only [mul_pow] using hsq

theorem actual_pair_first_pulse_attains_kl {n m T : ℕ} (a impact : ℝ)
    (q0 rate0 : Fin n → ℝ) (q1 rate1 : Fin m → ℝ)
    (hT : 0 < T) (V : ℝ) (hV : 0 ≤ V) (variance : ℝ≥0) (hv : variance ≠ 0) :
    let v : Fin T → ℝ := fun t => if t.val = 0 then V else 0
    InformationTheory.klDiv
      (gaussianRecordLaw T (fun t => actualCohortPriceRecord a impact q0 rate0 v t) variance)
      (gaussianRecordLaw T (fun t => actualCohortPriceRecord a impact q1 rate1 v t) variance) =
      ENNReal.ofReal (V ^ 2 * ‖finiteImpulseVector T
        (fun j => actualCohortImpulse a impact q1 rate1 j -
          actualCohortImpulse a impact q0 rate0 j)‖ ^ 2 / (2 * (variance : ℝ))) := by
  dsimp only
  rw [actual_pair_observation_kl _ _ _ _ _ _ _ _ hv,
    (first_pulse_convolution_attains _ hT V hV).2, mul_pow]

theorem autonomous_coordinates_power {n : ℕ} (a impact : ℝ)
    (q rate : Fin n → ℝ) (initial : CohortState n) (t : ℕ) :
    cohortCoordinates (autonomousState a impact q rate initial t) =
      (cohortLinearTransition a impact q rate ^ t) (cohortCoordinates initial) := by
  induction t with
  | zero => simp [autonomousState]
  | succ t ih =>
    rw [autonomousState, actual_step_linear_coordinates, ih, pow_succ']
    simp

theorem actual_impulse_matches_physical_pulse {n : ℕ} (a impact : ℝ)
    (q rate : Fin n → ℝ) (t : ℕ) :
    actualCohortImpulse a impact q rate t =
      (autonomousState a impact q rate (pulse1 a impact q rate 1) t).price := by
  have hb : cohortCoordinates (pulse1 a impact q rate 1) = cohortInputVector impact rate := by
    funext i
    cases i <;> simp [cohortCoordinates, pulse1, cohortStep, zeroState, cohortInputVector]
  have h := congrFun (autonomous_coordinates_power a impact q rate (pulse1 a impact q rate 1) t) none
  rw [hb] at h
  exact h.symm

theorem actual_positive_impulse_peak {n : ℕ} (a impact : ℝ)
    (q rate : Fin n → ℝ) (ha : 0 ≤ a) (hk : 0 ≤ impact) (hq : ∀ i, 0 ≤ q i)
    (hrate : ∀ i, 0 ≤ rate i ∧ rate i ≤ 1)
    (hfeedback : a + impact * ∑ i, q i ≤ 1) (t : ℕ) :
    0 ≤ actualCohortImpulse a impact q rate t ∧
      actualCohortImpulse a impact q rate t ≤ impact := by
  rw [actual_impulse_matches_physical_pulse]
  simpa using physical_positive_pulse_peak a impact 1 q rate ha hk (by norm_num)
    hq hrate hfeedback t

end
end CurrentMM
