import CurrentProofs.Paper1PassiveMatched

/-!
# Paper 1, Theorem `thm:kcohort` and Theorem `prop:passive` (iii) for `K = 3`: the three-point Gauss and
Gauss–Radau economies

This file builds the three-point Gauss rule and the three-point Gauss–Radau rule (left endpoint fixed), each
normalized to unit mass on `[-1, 1]`:

* Gauss: nodes `-√(3/5), 0, √(3/5)`, weights `5/18, 8/18, 5/18`;
* Gauss–Radau: nodes `-1, (1 - √6)/5, (1 + √6)/5`, weights `1/9, (16 + √6)/36, (16 - √6)/36`.

It proves the following properties outright, assuming nothing:
- both rules have positive weights summing to one;
- all nodes lie in `[-1, 1]`;
- the moments agree for every order below `2K - 1 = 5`;
- the fifth moments differ by `4W/75`.

With these facts, `p1_thm_passive_cost_matched` gives the passive finite-record bound `T = Ω(d⁻¹⁰)` for the paper's
`K = 3` economies (`p1_thm_passive_cost_gauss_radau_three`).
-/

namespace CurrentMM

open MeasureTheory ProbabilityTheory Finset
open scoped ENNReal NNReal

noncomputable def gr3GNode : Fin 3 → ℝ := ![-Real.sqrt (3 / 5), 0, Real.sqrt (3 / 5)]
noncomputable def gr3GWeight : Fin 3 → ℝ := ![5 / 18, 8 / 18, 5 / 18]
noncomputable def gr3RNode : Fin 3 → ℝ := ![-1, (1 - Real.sqrt 6) / 5, (1 + Real.sqrt 6) / 5]
noncomputable def gr3RWeight : Fin 3 → ℝ := ![1 / 9, (16 + Real.sqrt 6) / 36, (16 - Real.sqrt 6) / 36]

theorem p1_gr3_sqrt_facts :
    Real.sqrt 6 ^ 2 = 6 ∧ Real.sqrt (3 / 5) ^ 2 = 3 / 5 ∧ 0 ≤ Real.sqrt 6 ∧ Real.sqrt 6 ≤ 4 ∧
      0 ≤ Real.sqrt (3 / 5) ∧ Real.sqrt (3 / 5) ≤ 1 := by
  have hs := Real.sq_sqrt (by norm_num : (0 : ℝ) ≤ 6)
  have ht := Real.sq_sqrt (by norm_num : (0 : ℝ) ≤ 3 / 5)
  have hs0 := Real.sqrt_nonneg (6 : ℝ)
  have ht0 := Real.sqrt_nonneg (3 / 5 : ℝ)
  refine ⟨hs, ht, hs0, by nlinarith, ht0, by nlinarith⟩

theorem p1_gr3_node_bounds : (∀ i, |gr3GNode i| ≤ 1) ∧ (∀ i, |gr3RNode i| ≤ 1) := by
  obtain ⟨_, _, hs0, hs4, ht0, ht1⟩ := p1_gr3_sqrt_facts
  constructor
  · intro i
    fin_cases i
    · change |-Real.sqrt (3 / 5 : ℝ)| ≤ 1
      rw [abs_neg, abs_of_nonneg ht0]; exact ht1
    · change |(0 : ℝ)| ≤ 1
      norm_num
    · change |Real.sqrt (3 / 5 : ℝ)| ≤ 1
      rw [abs_of_nonneg ht0]; exact ht1
  · intro i
    fin_cases i
    · change |(-1 : ℝ)| ≤ 1
      norm_num
    · change |(1 - Real.sqrt 6) / 5| ≤ 1
      rw [abs_le]; constructor <;> linarith
    · change |(1 + Real.sqrt 6) / 5| ≤ 1
      rw [abs_le]; constructor <;> linarith

theorem p1_gr3_positive_weights : (∀ i, 0 < gr3GWeight i) ∧ (∀ i, 0 < gr3RWeight i) := by
  obtain ⟨_, _, hs0, hs4, _, _⟩ := p1_gr3_sqrt_facts
  constructor
  · intro i
    fin_cases i
    · change (0 : ℝ) < 5 / 18; norm_num
    · change (0 : ℝ) < 8 / 18; norm_num
    · change (0 : ℝ) < 5 / 18; norm_num
  · intro i
    fin_cases i
    · change (0 : ℝ) < 1 / 9; norm_num
    · change (0 : ℝ) < (16 + Real.sqrt 6) / 36
      exact div_pos (by linarith) (by norm_num)
    · change (0 : ℝ) < (16 - Real.sqrt 6) / 36
      exact div_pos (by linarith) (by norm_num)

theorem p1_gr3_weight_sums (W : ℝ) : (∑ i, W * gr3GWeight i) = W ∧ (∑ i, W * gr3RWeight i) = W := by
  constructor
  · simp only [Fin.sum_univ_three, gr3GWeight, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.cons_val_two,
      Matrix.tail_cons, Matrix.head_cons]
    ring
  · simp only [Fin.sum_univ_three, gr3RWeight, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.cons_val_two,
      Matrix.tail_cons, Matrix.head_cons]
    ring

/-- **The moments agree below order five.** -/
theorem p1_gr3_five_matched_moments (W : ℝ) (j : ℕ) (hj : j < 5) :
    (∑ i, W * gr3GWeight i * gr3GNode i ^ j) = ∑ i, W * gr3RWeight i * gr3RNode i ^ j := by
  obtain ⟨hs, ht, _, _, _, _⟩ := p1_gr3_sqrt_facts
  interval_cases j
  · simp only [Fin.sum_univ_three, gr3GWeight, gr3GNode, gr3RWeight, gr3RNode, Matrix.cons_val_zero,
      Matrix.cons_val_one, Matrix.cons_val_two, Matrix.tail_cons, Matrix.head_cons]
    ring
  · simp only [Fin.sum_univ_three, gr3GWeight, gr3GNode, gr3RWeight, gr3RNode, Matrix.cons_val_zero,
      Matrix.cons_val_one, Matrix.cons_val_two, Matrix.tail_cons, Matrix.head_cons]
    linear_combination (W / 90) * hs
  · simp only [Fin.sum_univ_three, gr3GWeight, gr3GNode, gr3RWeight, gr3RNode, Matrix.cons_val_zero,
      Matrix.cons_val_one, Matrix.cons_val_two, Matrix.tail_cons, Matrix.head_cons]
    linear_combination (-7 * W / 225) * hs + (5 * W / 9) * ht
  · simp only [Fin.sum_univ_three, gr3GWeight, gr3GNode, gr3RWeight, gr3RNode, Matrix.cons_val_zero,
      Matrix.cons_val_one, Matrix.cons_val_two, Matrix.tail_cons, Matrix.head_cons]
    linear_combination (W * (Real.sqrt 6 ^ 2 - 39) / 2250) * hs
  · simp only [Fin.sum_univ_three, gr3GWeight, gr3GNode, gr3RWeight, gr3RNode, Matrix.cons_val_zero,
      Matrix.cons_val_one, Matrix.cons_val_two, Matrix.tail_cons, Matrix.head_cons]
    linear_combination (-2 * W * (3 * Real.sqrt 6 ^ 2 + 41) / 5625) * hs +
      (W * (5 * Real.sqrt (3 / 5) ^ 2 + 3) / 9) * ht

/-- **The fifth moments differ.** -/
theorem p1_gr3_fifth_moment_gap (W : ℝ) :
    (∑ i, W * gr3GWeight i * gr3GNode i ^ 5) - (∑ i, W * gr3RWeight i * gr3RNode i ^ 5) = 4 * W / 75 := by
  obtain ⟨hs, ht, _, _, _, _⟩ := p1_gr3_sqrt_facts
  simp only [Fin.sum_univ_three, gr3GWeight, gr3GNode, gr3RWeight, gr3RNode, Matrix.cons_val_zero,
    Matrix.cons_val_one, Matrix.cons_val_two, Matrix.tail_cons, Matrix.head_cons]
  linear_combination (W * (Real.sqrt 6 ^ 4 - 64 * Real.sqrt 6 ^ 2 - 539) / 56250) * hs

/-- **Theorem `prop:passive` (iii), `K = 3`, for the paper's Gauss and Gauss–Radau economies.** Records start from
rest, after any warm-up. -/
theorem p1_thm_passive_cost_gauss_radau_three (a κ c d W s : ℝ) (hκ : 0 < κ) (hc : 0 ≤ c) (hd : 0 ≤ d)
    (hcd : c + d < 1) (hW0 : 0 ≤ W) (hs : |a| + κ * (W / (1 - (c + d))) ≤ s) (hs1 : s < 1)
    (q rate q' rate' : Fin 3 → ℝ)
    (hr : ∀ i, 1 - rate i = c + d * gr3GNode i) (hr' : ∀ i, 1 - rate' i = c + d * gr3RNode i)
    (hq : ∀ i, q i * rate i = W * gr3GWeight i) (hq' : ∀ i, q' i * rate' i = W * gr3RWeight i)
    (M T : ℕ) (v : ℝ≥0) (hv : v ≠ 0) (A : Set (Fin T → ℝ)) (hA : MeasurableSet A)
    (herr1 : (obsLaw M T v (fun j => actualCohortImpulse a κ q rate j / κ)).real A ≤ 1 / 4)
    (herr0 : (obsLaw M T v (fun j => actualCohortImpulse a κ q' rate' j / κ)).real Aᶜ ≤ 1 / 4) :
    1 ≤ 2 * (1 + s) ^ 2 *
      (κ * (2 * W * d ^ 5 * (1 / (1 - (c + d)) ^ (5 + 1))) / (1 - s) ^ 2) ^ 2 * T := by
  obtain ⟨hGpos, hRpos⟩ := p1_gr3_positive_weights
  obtain ⟨hGsum, hRsum⟩ := p1_gr3_weight_sums W
  obtain ⟨hGb, hRb⟩ := p1_gr3_node_bounds
  exact p1_thm_passive_cost_matched 5 a κ c d W s hκ hc hd hcd hW0 hs hs1 q rate q' rate'
    (fun i => W * gr3GWeight i) gr3GNode (fun i => W * gr3RWeight i) gr3RNode hr hr' hq hq'
    (fun i => mul_nonneg hW0 (hGpos i).le) (fun i => mul_nonneg hW0 (hRpos i).le)
    hGsum.le hRsum.le hGb hRb (fun j hj => p1_gr3_five_matched_moments W j hj) M T v hv A hA herr1 herr0

end CurrentMM
