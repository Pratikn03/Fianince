import CurrentProofs.Paper1Tagged

/-!
# Paper 1, Theorem 6.2 (ii): tagged records recover each memory rate with `N ∝ (Δη)^{-2}` experiments

In a unit reset experiment class `i`'s flow is `w_i κ` in period 0 and `w_i (r_i κ + h_1)` in period 1, where
`r_i = 1 - η_i` is its memory rate and `h_1` the price response in period 1. From `N` experiments with independent
Gaussian noise of variance `v` on each of the three recorded quantities, the plug-in estimator
`r̂ = (f̄₁ κ / f̄₀ - h̄₁) / κ` misses `r_i` by `L e` or more with probability at most `3 v / (N e²)`, for every
`e ≤ ω_min |κ| / 2`, with `L` depending only on `(ω_min, ω_max, κ, B)` where `|h_1| ≤ B`, not on the other classes
or on the rate spacing. So accuracy `c₀ Δη` at confidence `1 - β` needs at most `3 v L² / (β c₀² Δη²)` experiments.
-/

namespace CurrentMM

open MeasureTheory ProbabilityTheory Finset
open scoped ENNReal NNReal

theorem p1_tagged_second_flow {n : ℕ} (a impact : ℝ) (q rate : Fin n → ℝ) (i : Fin n) :
    q i * cohortImpulseMemory a impact q rate i 1 =
      (q i * rate i) * ((1 - rate i) * impact + actualCohortImpulse a impact q rate 1) := by
  rw [p1_impulse_memory_step, p1_impulse_memory_zero]; ring

/-- Deterministic step: three estimates within `e` give a rate estimate within `L e`. -/
theorem p1_tagged_rate_perturb (w κ r h1 ωmin ωmax B e A' F' H' : ℝ) (hκ : κ ≠ 0) (hωmin : 0 < ωmin)
    (hw1 : ωmin ≤ w) (hw2 : w ≤ ωmax) (hr : |r| ≤ 1) (hB : |h1| ≤ B) (he0 : 0 ≤ e) (he : e ≤ ωmin * |κ| / 2)
    (hA : |A' - w * κ| ≤ e) (hF : |F' - w * (r * κ + h1)| ≤ e) (hH : |H' - h1| ≤ e) :
    |(F' * κ / A' - H') / κ - r| ≤
      ((2 * (ωmax * |κ| + ωmax * (|κ| + B)) / (ωmin ^ 2 * |κ|) + 1) / |κ|) * e := by
  have hk : 0 < |κ| := abs_pos.mpr hκ
  set A := w * κ with hAdef
  set F := w * (r * κ + h1) with hFdef
  have hAabs : |A| = w * |κ| := by rw [hAdef, abs_mul, abs_of_pos (by linarith)]
  have hAlo : ωmin * |κ| ≤ |A| := by rw [hAabs]; exact mul_le_mul_of_nonneg_right hw1 hk.le
  have hAhi : |A| ≤ ωmax * |κ| := by rw [hAabs]; exact mul_le_mul_of_nonneg_right hw2 hk.le
  have hA'lo : ωmin * |κ| / 2 ≤ |A'| := by
    have := abs_sub_abs_le_abs_sub A A'
    rw [abs_sub_comm] at this; linarith
  have hFabs : |F| ≤ ωmax * (|κ| + B) := by
    rw [hFdef, abs_mul, abs_of_pos (by linarith)]
    have : |r * κ + h1| ≤ |κ| + B := by
      calc |r * κ + h1| ≤ |r| * |κ| + |h1| := by rw [← abs_mul]; exact abs_add_le _ _
        _ ≤ 1 * |κ| + B := by gcongr
        _ = |κ| + B := by ring
    exact mul_le_mul hw2 this (abs_nonneg _) (by linarith)
  have hA0 : A ≠ 0 := by intro h; rw [h, abs_zero] at hAlo; nlinarith
  have hA'0 : A' ≠ 0 := by intro h; rw [h, abs_zero] at hA'lo; nlinarith
  have hw0 : w ≠ 0 := (by linarith : (0 : ℝ) < w).ne'
  have hrval : r = (F * κ / A - h1) / κ := by rw [hFdef, hAdef]; field_simp; ring
  have hmain : |F' * κ / A' - F * κ / A| ≤ 2 * |κ| * e * (ωmax * |κ| + ωmax * (|κ| + B)) / (ωmin * |κ|) ^ 2 := by
    have e1 : F' * κ / A' - F * κ / A = κ * ((F' - F) * A + F * (A - A')) / (A' * A) := by
      field_simp; ring
    rw [e1, abs_div, abs_mul, abs_mul]
    have hnum : |(F' - F) * A + F * (A - A')| ≤ e * (ωmax * |κ|) + ωmax * (|κ| + B) * e := by
      calc |(F' - F) * A + F * (A - A')| ≤ |F' - F| * |A| + |F| * |A - A'| := by
            rw [← abs_mul, ← abs_mul]; exact abs_add_le _ _
        _ ≤ e * (ωmax * |κ|) + ωmax * (|κ| + B) * e := by
            have hB0 : 0 ≤ B := le_trans (abs_nonneg _) hB
            exact add_le_add (mul_le_mul hF hAhi (abs_nonneg _) he0)
              (mul_le_mul hFabs (by rw [abs_sub_comm]; exact hA) (abs_nonneg _)
                (mul_nonneg (by linarith) (by positivity)))
    have hden : (ωmin * |κ|) ^ 2 / 2 ≤ |A'| * |A| := by
      have := mul_le_mul hA'lo hAlo (by positivity) (abs_nonneg _)
      nlinarith
    rw [div_le_div_iff₀ (by positivity) (by positivity)]
    calc |κ| * |(F' - F) * A + F * (A - A')| * (ωmin * |κ|) ^ 2
        ≤ |κ| * (e * (ωmax * |κ|) + ωmax * (|κ| + B) * e) * (2 * (|A'| * |A|)) := by
          have hωm : 0 ≤ ωmax := by linarith
          have hB0 : 0 ≤ B := le_trans (abs_nonneg _) hB
          exact mul_le_mul (mul_le_mul_of_nonneg_left hnum hk.le) (by linarith) (by positivity) (by positivity)
      _ = 2 * |κ| * e * (ωmax * |κ| + ωmax * (|κ| + B)) * (|A'| * |A|) := by ring
  rw [hrval]
  have e2 : (F' * κ / A' - H') / κ - (F * κ / A - h1) / κ = ((F' * κ / A' - F * κ / A) - (H' - h1)) / κ := by
    field_simp; ring
  rw [e2, abs_div, div_le_iff₀ hk]
  calc |F' * κ / A' - F * κ / A - (H' - h1)| ≤ |F' * κ / A' - F * κ / A| + |H' - h1| := abs_sub _ _
    _ ≤ 2 * |κ| * e * (ωmax * |κ| + ωmax * (|κ| + B)) / (ωmin * |κ|) ^ 2 + e := add_le_add hmain hH
    _ = ((2 * (ωmax * |κ| + ωmax * (|κ| + B)) / (ωmin ^ 2 * |κ|) + 1) / |κ|) * e * |κ| := by
        field_simp

/-- **Theorem 6.2 (ii), upper bound, finite sample.** Class `i`'s merged weight lies in `[ω_min, ω_max]`, its
memory rate `r_i = 1 - η_i` has `|r_i| ≤ 1`, and `|h_1| ≤ B`. The record consists of `N` independent Gaussian
draws (variance `v`) of each of: the period-0 flow, the period-1 flow and the period-1 price. Then the plug-in
rate estimate misses `r_i` by `L e` or more with probability at most `3 v / (N e²)`. -/
theorem p1_thm_tagged_rate_recovery {K : ℕ} (N : ℕ) (hN : 0 < N) (a κ : ℝ) (hκ : κ ≠ 0)
    (q rate : Fin K → ℝ) (i : Fin K) (ωmin ωmax B : ℝ) (hωmin : 0 < ωmin)
    (hw1 : ωmin ≤ q i * rate i) (hw2 : q i * rate i ≤ ωmax) (hr : |1 - rate i| ≤ 1)
    (hB : |actualCohortImpulse a κ q rate 1| ≤ B) (v : ℝ≥0) (e : ℝ) (he0 : 0 < e)
    (he : e ≤ ωmin * |κ| / 2) :
    (Measure.pi fun j : Fin 3 => Measure.pi fun _ : Fin N =>
        gaussianReal (![q i * cohortImpulseMemory a κ q rate i 0, q i * cohortImpulseMemory a κ q rate i 1,
          actualCohortImpulse a κ q rate 1] j) v)
      {x | ((2 * (ωmax * |κ| + ωmax * (|κ| + B)) / (ωmin ^ 2 * |κ|) + 1) / |κ|) * e <
        |((∑ n, x 1 n) / N * κ / ((∑ n, x 0 n) / N) - (∑ n, x 2 n) / N) / κ - (1 - rate i)|} ≤
      3 * ENNReal.ofReal (v / (N * e ^ 2)) := by
  set m : Fin 3 → ℝ := ![q i * cohortImpulseMemory a κ q rate i 0, q i * cohortImpulseMemory a κ q rate i 1,
    actualCohortImpulse a κ q rate 1] with hm
  set μ := Measure.pi fun j : Fin 3 => Measure.pi fun _ : Fin N => gaussianReal (m j) v
  have hsub : {x : Fin 3 → Fin N → ℝ | ((2 * (ωmax * |κ| + ωmax * (|κ| + B)) / (ωmin ^ 2 * |κ|) + 1) / |κ|) * e <
        |((∑ n, x 1 n) / N * κ / ((∑ n, x 0 n) / N) - (∑ n, x 2 n) / N) / κ - (1 - rate i)|} ⊆
      ⋃ j : Fin 3, {x | e ≤ |(∑ n, x j n) / N - m j|} := by
    intro x hx
    by_contra hnot
    simp only [Set.mem_iUnion, Set.mem_ofPred_eq, not_exists, not_le] at hnot
    have h0 := hnot 0; have h1 := hnot 1; have h2 := hnot 2
    simp only [hm, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons, Matrix.cons_val_two,
      Matrix.tail_cons] at h0 h1 h2
    rw [p1_tagged_first_flow] at h0
    rw [p1_tagged_second_flow] at h1
    have := p1_tagged_rate_perturb (q i * rate i) κ (1 - rate i) (actualCohortImpulse a κ q rate 1) ωmin ωmax B e
      _ _ _ hκ hωmin hw1 hw2 hr hB he0.le he h0.le (by rw [show (1 - rate i) * κ = (1 - rate i) * κ from rfl]; exact h1.le) h2.le
    exact absurd this (not_le.mpr hx)
  refine le_trans (measure_mono hsub) (le_trans (measure_iUnion_fintype_le μ _) ?_)
  have hj : ∀ j : Fin 3, μ {x : Fin 3 → Fin N → ℝ | e ≤ |(∑ n, x j n) / N - m j|} ≤
      ENNReal.ofReal (v / (N * e ^ 2)) := by
    intro j
    have hmeas : MeasurableSet {y : Fin N → ℝ | e ≤ |(∑ n, y n) / N - m j|} :=
      measurableSet_le measurable_const (by fun_prop)
    have hpre : {x : Fin 3 → Fin N → ℝ | e ≤ |(∑ n, x j n) / N - m j|} =
        (fun x : Fin 3 → Fin N → ℝ => x j) ⁻¹' {y | e ≤ |(∑ n, y n) / N - m j|} := rfl
    rw [hpre, (measurePreserving_eval _ j).measure_preimage hmeas.nullMeasurableSet]
    exact p1_tagged_mean_chebyshev N hN (m j) v e he0
  calc ∑ j : Fin 3, μ {x : Fin 3 → Fin N → ℝ | e ≤ |(∑ n, x j n) / N - m j|}
      ≤ ∑ _j : Fin 3, ENNReal.ofReal (v / (N * e ^ 2)) := sum_le_sum (fun j _ => hj j)
    _ = 3 * ENNReal.ofReal (v / (N * e ^ 2)) := by simp

end CurrentMM
