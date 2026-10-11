import CurrentProofs.Recursion

namespace CurrentMM
noncomputable section
open scoped BigOperators

def stateInBox {n : ℕ} (state : CohortState n) (M : ℝ) : Prop :=
  (0 ≤ state.price ∧ state.price ≤ M) ∧ ∀ i, 0 ≤ state.memory i ∧ state.memory i ≤ M

theorem positive_cohort_price_box {n : ℕ} (a impact M : ℝ)
    (q rate : Fin n → ℝ) (state : CohortState n)
    (ha : 0 ≤ a) (hk : 0 ≤ impact) (hM : 0 ≤ M) (hq : ∀ i, 0 ≤ q i)
    (hfeedback : a + impact * ∑ i, q i ≤ 1) (hstate : stateInBox state M) :
    0 ≤ (cohortStep a impact q rate 0 state).price ∧
      (cohortStep a impact q rate 0 state).price ≤ M := by
  dsimp only [cohortStep]
  simp only [mul_zero, add_zero]
  constructor
  · exact add_nonneg (mul_nonneg ha hstate.1.1)
      (mul_nonneg hk (Finset.sum_nonneg fun i _ => mul_nonneg (hq i) (hstate.2 i).1))
  · have hs : (∑ i, q i * state.memory i) ≤ (∑ i, q i) * M := by
      rw [Finset.sum_mul]
      exact Finset.sum_le_sum fun i _ => mul_le_mul_of_nonneg_left (hstate.2 i).2 (hq i)
    calc
      a * state.price + impact * ∑ i, q i * state.memory i ≤
          a * M + impact * ((∑ i, q i) * M) :=
        add_le_add (mul_le_mul_of_nonneg_left hstate.1.2 ha)
          (mul_le_mul_of_nonneg_left hs hk)
      _ = (a + impact * ∑ i, q i) * M := by ring
      _ ≤ M := by nlinarith [mul_le_mul_of_nonneg_right hfeedback hM]

theorem positive_cohort_step_preserves_box {n : ℕ} (a impact M : ℝ)
    (q rate : Fin n → ℝ) (state : CohortState n)
    (ha : 0 ≤ a) (hk : 0 ≤ impact) (hM : 0 ≤ M) (hq : ∀ i, 0 ≤ q i)
    (hrate : ∀ i, 0 ≤ rate i ∧ rate i ≤ 1)
    (hfeedback : a + impact * ∑ i, q i ≤ 1) (hstate : stateInBox state M) :
    stateInBox (cohortStep a impact q rate 0 state) M := by
  have hp := positive_cohort_price_box a impact M q rate state ha hk hM hq hfeedback hstate
  refine ⟨hp, ?_⟩
  intro i
  change 0 ≤ (1 - rate i) * state.memory i + rate i *
      (cohortStep a impact q rate 0 state).price ∧
    (1 - rate i) * state.memory i + rate i *
      (cohortStep a impact q rate 0 state).price ≤ M
  constructor
  · exact add_nonneg (mul_nonneg (by linarith [(hrate i).2]) (hstate.2 i).1)
      (mul_nonneg (hrate i).1 hp.1)
  · have h0 := mul_le_mul_of_nonneg_left (hstate.2 i).2
      (show 0 ≤ 1 - rate i by linarith [(hrate i).2])
    have h1 := mul_le_mul_of_nonneg_left hp.2 (hrate i).1
    nlinarith

def autonomousState {n : ℕ} (a impact : ℝ) (q rate : Fin n → ℝ)
    (initial : CohortState n) : ℕ → CohortState n
  | 0 => initial
  | t + 1 => cohortStep a impact q rate 0 (autonomousState a impact q rate initial t)

theorem positive_cohort_trajectory_box {n : ℕ} (a impact M : ℝ)
    (q rate : Fin n → ℝ) (initial : CohortState n)
    (ha : 0 ≤ a) (hk : 0 ≤ impact) (hM : 0 ≤ M) (hq : ∀ i, 0 ≤ q i)
    (hrate : ∀ i, 0 ≤ rate i ∧ rate i ≤ 1)
    (hfeedback : a + impact * ∑ i, q i ≤ 1) (hstate : stateInBox initial M)
    (t : ℕ) : stateInBox (autonomousState a impact q rate initial t) M := by
  induction t with
  | zero => exact hstate
  | succ t ih =>
      exact positive_cohort_step_preserves_box a impact M q rate _ ha hk hM hq hrate
        hfeedback ih

theorem positive_pulse_initial_box {n : ℕ} (a impact A : ℝ) (q rate : Fin n → ℝ)
    (hk : 0 ≤ impact) (hA : 0 ≤ A) (hrate : ∀ i, 0 ≤ rate i ∧ rate i ≤ 1) :
    stateInBox (pulse1 a impact q rate A) (impact * A) := by
  refine ⟨?_, ?_⟩
  · rw [physical_first_pulse_price]
    exact ⟨mul_nonneg hk hA, le_refl _⟩
  · intro i
    rw [physical_first_pulse_memory]
    constructor
    · exact mul_nonneg (hrate i).1 (mul_nonneg hk hA)
    · have h := mul_le_mul_of_nonneg_right (hrate i).2 (mul_nonneg hk hA)
      nlinarith

theorem physical_positive_pulse_peak {n : ℕ} (a impact A : ℝ) (q rate : Fin n → ℝ)
    (ha : 0 ≤ a) (hk : 0 ≤ impact) (hA : 0 ≤ A) (hq : ∀ i, 0 ≤ q i)
    (hrate : ∀ i, 0 ≤ rate i ∧ rate i ≤ 1)
    (hfeedback : a + impact * ∑ i, q i ≤ 1) (t : ℕ) :
    0 ≤ (autonomousState a impact q rate (pulse1 a impact q rate A) t).price ∧
      (autonomousState a impact q rate (pulse1 a impact q rate A) t).price ≤ impact * A :=
  (positive_cohort_trajectory_box a impact (impact * A) q rate _ ha hk (mul_nonneg hk hA)
    hq hrate hfeedback (positive_pulse_initial_box a impact A q rate hk hA hrate) t).1

theorem funded_trader_positive_trajectory_margin {n : ℕ}
    (a impact A cost margin P : ℝ) (q rate : Fin n → ℝ)
    (ha : 0 ≤ a) (hk : 0 ≤ impact) (hA : 0 ≤ A) (hq : ∀ i, 0 ≤ q i)
    (hrate : ∀ i, 0 ≤ rate i ∧ rate i ≤ 1)
    (hfeedback : a + impact * ∑ i, q i ≤ 1) (hm : margin ≤ 1) (t : ℕ) :
    let mark := P + (autonomousState a impact q rate (pulse1 a impact q rate A) t).price
    margin * |A| * mark ≤
      equity (pulseTraderCapital impact cost margin P A -
        A * averageFill P impact A - cost * A) A mark := by
  dsimp only
  have hp := (physical_positive_pulse_peak a impact A q rate ha hk hA hq hrate hfeedback t).1
  rw [abs_of_nonneg hA]
  unfold equity pulseTraderCapital averageFill
  have hh : 0 ≤ (1 - margin) * A *
      (autonomousState a impact q rate (pulse1 a impact q rate A) t).price := by positivity
  nlinarith

end
end CurrentMM
