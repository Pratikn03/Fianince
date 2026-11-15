import CurrentProofs.Paper1QuantityCapital
import CurrentProofs.Accounts

/-!
# Paper 1, Lemma `thm:capital` (S24.4): the converse

The lemma's converse: a single pulse of size `A` at the first input, read off the third observation, separates the
known pair, and a trader who holds `B_A = κA²/2 + (c + μP*)A` stays margin-solvent at every later mark.

* `p1_pair_tap2_gap`: the third taps differ by `-κ²qδ²` (the first two coincide).
* `p1_pulse_record_coord`: under the pulse, observation `t` has mean `A h_t`.
* `p1_record_coord_two`: the third coordinate of the Gaussian record has law `N(mean₂, σ²)`.
* `p1_thm_capital_converse_errors`: with `D = A κ² q δ²` and the midpoint test on the third observation, the error
  under the single cohort is `N(0, σ²)((-∞, -D/2))` and under the pair `N(0, σ²)((-∞, -D/2])`; so a pulse with
  `N(0, σ²)((-∞, -D/2]) ≤ α` has both errors at most `α` (the paper's `Φ(-AΔ/(2σ)) ≤ α`).
* `p1_thm_capital_converse_margin`: in any positive economy (nonnegative taps), the funded trader with capital
  `B_A` and margin fraction `0 ≤ μ ≤ 1` meets the margin requirement at every later mark `P* + A h_t`.
-/

namespace CurrentMM

open Finset MeasureTheory ProbabilityTheory Real Set
open scoped ENNReal NNReal

/-- A single trade of size `A` at the first input. -/
noncomputable def pulseProbe (A : ℝ) : ℕ → ℝ := fun s => if s = 0 then A else 0

theorem p1_pair_tap2_gap (a κ q η δ : ℝ) :
    actualCohortImpulse a κ ![q / 2, q / 2] ![η - δ, η + δ] 2 - actualCohortImpulse a κ ![q] ![η] 2 =
      -(κ ^ 2 * q * δ ^ 2) := by
  have e2 := p1_impulse_closed_loop_recursion a κ ![q / 2, q / 2] ![η - δ, η + δ] 1
  have e1 := p1_impulse_closed_loop_recursion a κ ![q / 2, q / 2] ![η - δ, η + δ] 0
  have f2 := p1_impulse_closed_loop_recursion a κ ![q] ![η] 1
  have f1 := p1_impulse_closed_loop_recursion a κ ![q] ![η] 0
  have z1 := p1_impulse_zero a κ ![q / 2, q / 2] ![η - δ, η + δ]
  have z2 := p1_impulse_zero a κ ![q] ![η]
  simp only [sum_range_succ, sum_range_zero, zero_add, Nat.reduceAdd, Nat.sub_self, Nat.sub_zero,
    Nat.reduceSub] at e2 e1 f2 f1
  rw [e2, f2, e1, f1, z1, z2]
  simp only [cohortKernel, Fin.sum_univ_two, Fin.sum_univ_one, Matrix.cons_val_zero, Matrix.cons_val_one,
    Matrix.head_cons, pow_zero, pow_one, mul_one]
  ring

theorem p1_pulse_record_coord {n : ℕ} (a κ : ℝ) (q rate : Fin n → ℝ) (A : ℝ) (t : ℕ) :
    (controlledCohortRun a κ q rate (pulseProbe A) (t + 1)).price = A * actualCohortImpulse a κ q rate t := by
  rw [actual_reset_price_convolution, sum_range_succ']
  simp [pulseProbe]

/-- The third coordinate of a Gaussian record. -/
theorem p1_record_coord_two (T : ℕ) (mean : Fin (T + 3) → ℝ) (v : ℝ≥0) (S : Set ℝ) :
    (gaussianRecordLaw (T + 3) mean v) {x | x.2.2.1 ∈ S} = gaussianReal (mean 2) v S := by
  have hset : {x : ObservationRecord (T + 3) | x.2.2.1 ∈ S} = univ ×ˢ (univ ×ˢ (S ×ˢ univ)) := by
    ext ⟨x0, x1, x2, r⟩; simp
  rw [hset]
  show ((gaussianReal (mean 0) v).prod ((gaussianReal (mean 1) v).prod ((gaussianReal (mean 2) v).prod
    (gaussianRecordLaw T (fun i => mean i.succ.succ.succ) v)))) (univ ×ˢ (univ ×ˢ (S ×ˢ univ))) = _
  rw [Measure.prod_prod, Measure.prod_prod, Measure.prod_prod]
  simp

theorem p1_gaussian_Iio_shift (μ m : ℝ) (v : ℝ≥0) :
    gaussianReal μ v (Iio m) = gaussianReal 0 v (Iio (m - μ)) := by
  have h := gaussianReal_map_add_const (μ := 0) (v := v) μ
  rw [zero_add] at h
  rw [← h, Measure.map_apply (by fun_prop : Measurable fun x : ℝ => x + μ) measurableSet_Iio]
  congr 1
  ext x; simp only [Set.mem_preimage, Set.mem_Iio]; constructor <;> intro hx <;> linarith

theorem p1_gaussian_Ici_shift (μ m : ℝ) (v : ℝ≥0) :
    gaussianReal μ v (Ici m) = gaussianReal 0 v (Ici (m - μ)) := by
  have h := gaussianReal_map_add_const (μ := 0) (v := v) μ
  rw [zero_add] at h
  rw [← h, Measure.map_apply (by fun_prop : Measurable fun x : ℝ => x + μ) measurableSet_Ici]
  congr 1
  ext x; simp only [Set.mem_preimage, Set.mem_Ici]; constructor <;> intro hx <;> linarith

theorem p1_gaussian_Ici_symm (c : ℝ) (v : ℝ≥0) : gaussianReal 0 v (Ici c) = gaussianReal 0 v (Iic (-c)) := by
  have h := gaussianReal_map_neg (μ := 0) (v := v)
  rw [neg_zero] at h
  rw [← h, Measure.map_apply measurable_neg measurableSet_Iic]
  congr 1
  ext x; simp only [Set.mem_preimage, Set.mem_Iic, Set.mem_Ici]; constructor <;> intro hx <;> linarith

/-- **Converse of Lemma `thm:capital`: the pulse test's errors.** With `μ₀ = A h⁰₂` and `D = A κ² q δ²`, the test that
declares "pair" when the third observation is below `μ₀ - D/2` has error `N(0,σ²)((-∞,-D/2))` under the single cohort
and `N(0,σ²)((-∞,-D/2])` under the pair. -/
theorem p1_thm_capital_converse_errors (a κ q η δ A μ0 D : ℝ) (T : ℕ) (v : ℝ≥0)
    (hμ0 : μ0 = A * actualCohortImpulse a κ ![q] ![η] 2) (hD : D = A * (κ ^ 2 * q * δ ^ 2)) :
    (gaussianRecordLaw (T + 3) (fun t => (controlledCohortRun a κ ![q] ![η] (pulseProbe A) (t.val + 1)).price)
        v) {x | x.2.2.1 ∈ Iio (μ0 - D / 2)} = gaussianReal 0 v (Iio (-(D / 2))) ∧
    (gaussianRecordLaw (T + 3) (fun t => (controlledCohortRun a κ ![q / 2, q / 2] ![η - δ, η + δ] (pulseProbe A)
        (t.val + 1)).price) v) {x | x.2.2.1 ∈ Iio (μ0 - D / 2)}ᶜ = gaussianReal 0 v (Iic (-(D / 2))) := by
  have hR : {x : ObservationRecord (T + 3) | x.2.2.1 ∈ Iio (μ0 - D / 2)}ᶜ =
      {x : ObservationRecord (T + 3) | x.2.2.1 ∈ Ici (μ0 - D / 2)} := by
    ext x; simp
  constructor
  · rw [p1_record_coord_two]
    have hm : (controlledCohortRun a κ ![q] ![η] (pulseProbe A) ((2 : Fin (T + 3)).val + 1)).price = μ0 := by
      rw [Fin.val_two, p1_pulse_record_coord, hμ0]
    beta_reduce
    rw [hm, p1_gaussian_Iio_shift, show μ0 - D / 2 - μ0 = -(D / 2) by ring]
  · rw [hR, p1_record_coord_two]
    have hm : (controlledCohortRun a κ ![q / 2, q / 2] ![η - δ, η + δ] (pulseProbe A)
        ((2 : Fin (T + 3)).val + 1)).price = μ0 - D := by
      rw [Fin.val_two, p1_pulse_record_coord, hμ0, hD]
      have := p1_pair_tap2_gap a κ q η δ
      linear_combination A * this
    beta_reduce
    rw [hm, p1_gaussian_Ici_shift, show μ0 - D / 2 - (μ0 - D) = D / 2 by ring, p1_gaussian_Ici_symm]

/-- **Converse of Lemma `thm:capital`: the funded pulse stays margin-solvent.** In any positive economy, the trader
with capital `B_A = κA²/2 + (c + μP*)A` meets the margin requirement `μ|A| · mark ≤ equity` at every later mark
`P* + A h_t`. -/
theorem p1_thm_capital_converse_margin {n : ℕ} (a κ c μ P A : ℝ) (q rate : Fin n → ℝ)
    (ha : 0 ≤ a) (hκ : 0 ≤ κ) (hq : ∀ i, 0 ≤ q i) (hr : ∀ i, 0 < rate i ∧ rate i ≤ 1)
    (hf : a + κ * ∑ i, q i < 1) (hA : 0 ≤ A) (hμ : μ ≤ 1) (t : ℕ) :
    μ * |A| * (P + A * actualCohortImpulse a κ q rate t) ≤
      equity (pulseTraderCapital κ c μ P A - A * averageFill P κ A - c * A) A
        (P + A * actualCohortImpulse a κ q rate t) := by
  obtain ⟨lam, wts, hlam, hw, _, hrep⟩ := actual_nonnegative_anchor_impulse_mixture a κ q rate ha hκ hq hr hf
  have hh : 0 ≤ actualCohortImpulse a κ q rate t := by
    rw [hrep t]
    exact Finset.sum_nonneg (fun i _ => mul_nonneg (hw i) (pow_nonneg (hlam i).1 t))
  exact funded_trader_pulse_margin κ c μ P A (actualCohortImpulse a κ q rate t) hA hh hμ

end CurrentMM
