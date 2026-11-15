import CurrentProofs.PositiveDynamics
import CurrentProofs.ProbeGeometry

namespace CurrentMM
noncomputable section
open scoped BigOperators

def stateAbsBound {n : ℕ} (state : CohortState n) (M : ℝ) : Prop :=
  |state.price| ≤ M ∧ ∀ i, |state.memory i| ≤ M

def cohortEuclideanState {n : ℕ} (state : CohortState n) : EuclideanSpace ℝ (Option (Fin n)) :=
  WithLp.toLp 2 (fun i => i.elim state.price state.memory)

theorem positive_cohort_signed_price_bound {n : ℕ} (a impact M : ℝ)
    (q rate : Fin n → ℝ) (state : CohortState n)
    (ha : 0 ≤ a) (hk : 0 ≤ impact) (hM : 0 ≤ M) (hq : ∀ i, 0 ≤ q i)
    (hfeedback : a + impact * ∑ i, q i ≤ 1) (hstate : stateAbsBound state M) :
    |(cohortStep a impact q rate 0 state).price| ≤ M := by
  have hsum : |∑ i, q i * state.memory i| ≤ ∑ i, q i * |state.memory i| := by
    calc
      _ ≤ ∑ i, |q i * state.memory i| := by
        simpa only [Real.norm_eq_abs] using norm_sum_le Finset.univ (fun i : Fin n => q i * state.memory i)
      _ = _ := by
        apply Finset.sum_congr rfl
        intro i hi
        rw [abs_mul, abs_of_nonneg (hq i)]
  have hupper : (∑ i, q i * |state.memory i|) ≤ (∑ i, q i) * M := by
    rw [Finset.sum_mul]
    exact Finset.sum_le_sum fun i _ => mul_le_mul_of_nonneg_left (hstate.2 i) (hq i)
  have htriangle : |a * state.price + impact * ∑ i, q i * state.memory i| ≤
      a * |state.price| + impact * |∑ i, q i * state.memory i| := by
    simpa only [Real.norm_eq_abs, abs_mul, abs_of_nonneg ha, abs_of_nonneg hk] using
      norm_add_le (a * state.price) (impact * ∑ i, q i * state.memory i)
  change |a * state.price + impact * (∑ i, q i * state.memory i) + impact * 0| ≤ M
  simp only [mul_zero, add_zero]
  calc
    _ ≤ a * |state.price| + impact * |∑ i, q i * state.memory i| := htriangle
    _ ≤ a * M + impact * ((∑ i, q i) * M) :=
      add_le_add (mul_le_mul_of_nonneg_left hstate.1 ha)
        (mul_le_mul_of_nonneg_left (le_trans hsum hupper) hk)
    _ = (a + impact * ∑ i, q i) * M := by ring
    _ ≤ M := by nlinarith [mul_le_mul_of_nonneg_right hfeedback hM]

theorem positive_cohort_step_preserves_abs_bound {n : ℕ} (a impact M : ℝ)
    (q rate : Fin n → ℝ) (state : CohortState n)
    (ha : 0 ≤ a) (hk : 0 ≤ impact) (hM : 0 ≤ M) (hq : ∀ i, 0 ≤ q i)
    (hrate : ∀ i, 0 ≤ rate i ∧ rate i ≤ 1)
    (hfeedback : a + impact * ∑ i, q i ≤ 1) (hstate : stateAbsBound state M) :
    stateAbsBound (cohortStep a impact q rate 0 state) M := by
  have hp := positive_cohort_signed_price_bound a impact M q rate state ha hk hM hq hfeedback hstate
  refine ⟨hp, ?_⟩
  intro i
  have hi : 0 ≤ 1 - rate i := by linarith [(hrate i).2]
  have htriangle : |(1 - rate i) * state.memory i + rate i *
      (cohortStep a impact q rate 0 state).price| ≤
      (1 - rate i) * |state.memory i| + rate i * |(cohortStep a impact q rate 0 state).price| := by
    simpa only [Real.norm_eq_abs, abs_mul, abs_of_nonneg hi, abs_of_nonneg (hrate i).1] using
      norm_add_le ((1 - rate i) * state.memory i)
        (rate i * (cohortStep a impact q rate 0 state).price)
  have h0 := mul_le_mul_of_nonneg_left (hstate.2 i) hi
  have h1 := mul_le_mul_of_nonneg_left hp (hrate i).1
  change |(1 - rate i) * state.memory i + rate i *
    (cohortStep a impact q rate 0 state).price| ≤ M
  linarith

theorem signed_cohort_trajectory_abs_bound {n : ℕ} (a impact M : ℝ)
    (q rate : Fin n → ℝ) (initial : CohortState n)
    (ha : 0 ≤ a) (hk : 0 ≤ impact) (hM : 0 ≤ M) (hq : ∀ i, 0 ≤ q i)
    (hrate : ∀ i, 0 ≤ rate i ∧ rate i ≤ 1)
    (hfeedback : a + impact * ∑ i, q i ≤ 1) (hinitial : stateAbsBound initial M)
    (t : ℕ) : stateAbsBound (autonomousState a impact q rate initial t) M := by
  induction t with
  | zero => exact hinitial
  | succ t ih =>
      exact positive_cohort_step_preserves_abs_bound a impact M q rate _
        ha hk hM hq hrate hfeedback ih

theorem euclidean_state_bounds_components {n : ℕ} (initial : CohortState n) :
    stateAbsBound initial ‖cohortEuclideanState initial‖ := by
  constructor
  · simpa [cohortEuclideanState, Real.norm_eq_abs] using
      PiLp.norm_apply_le (cohortEuclideanState initial) none
  · intro i
    simpa [cohortEuclideanState, Real.norm_eq_abs] using
      PiLp.norm_apply_le (cohortEuclideanState initial) (some i)

theorem price_only_euclidean_gain_bound {n : ℕ} (a impact exposure : ℝ)
    (q rate : Fin n → ℝ) (initial : CohortState n)
    (ha : 0 ≤ a) (hk : 0 ≤ impact) (hq : ∀ i, 0 ≤ q i)
    (hrate : ∀ i, 0 ≤ rate i ∧ rate i ≤ 1)
    (hfeedback : a + impact * ∑ i, q i ≤ 1) (t : ℕ) :
    |exposure * (autonomousState a impact q rate initial t).price| ≤
      |exposure| * ‖cohortEuclideanState initial‖ := by
  rw [abs_mul]
  exact mul_le_mul_of_nonneg_left
    (signed_cohort_trajectory_abs_bound a impact _ q rate initial ha hk (norm_nonneg _) hq
      hrate hfeedback (euclidean_state_bounds_components initial) t).1 (abs_nonneg _)

theorem pure_price_unit_state_norm (n : ℕ) :
    ‖cohortEuclideanState (⟨1, fun _ => 0⟩ : CohortState n)‖ = 1 := by
  have heq : cohortEuclideanState (⟨1, fun _ => 0⟩ : CohortState n) =
      PiLp.single (β := fun _ : Option (Fin n) => ℝ) 2 none 1 := by
    ext i
    cases i with
    | none =>
        change 1 = (Pi.single none (1 : ℝ) : Option (Fin n) → ℝ) none
        simp
    | some i =>
        change 0 = (Pi.single none (1 : ℝ) : Option (Fin n) → ℝ) (some i)
        simp
  rw [heq, PiLp.norm_single, norm_one]

theorem price_only_exact_peak_gain {n : ℕ} (a impact exposure : ℝ) (q rate : Fin n → ℝ)
    (ha : 0 ≤ a) (hk : 0 ≤ impact) (hq : ∀ i, 0 ≤ q i)
    (hrate : ∀ i, 0 ≤ rate i ∧ rate i ≤ 1)
    (hfeedback : a + impact * ∑ i, q i ≤ 1) :
    IsGreatest ((fun pair : CohortState n × ℕ =>
      |exposure * (autonomousState a impact q rate pair.1 pair.2).price|) ''
      {pair | ‖cohortEuclideanState pair.1‖ ≤ 1}) |exposure| := by
  refine ⟨?_, ?_⟩
  · refine ⟨(⟨1, fun _ => 0⟩, 0), ?_, ?_⟩
    · exact (pure_price_unit_state_norm n).le
    · simp [autonomousState]
  · rintro value ⟨⟨initial, t⟩, hnorm, rfl⟩
    have h := price_only_euclidean_gain_bound a impact exposure q rate initial ha hk hq hrate hfeedback t
    have hcap := mul_le_mul_of_nonneg_left hnorm (abs_nonneg exposure)
    simpa only [mul_one] using le_trans h hcap

end
end CurrentMM
