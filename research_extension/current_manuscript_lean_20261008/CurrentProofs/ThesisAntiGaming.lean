import Mathlib.Basic.Real.Basic
import Mathlib.Topology.Order.IntermediateValue
import Mathlib.Topology.Instances.Real.Lemmas
import Mathlib.Tactic.Linarith
import Mathlib.Tactic.Ring
import Mathlib.Tactic.Positivity

/-!
# A continuous throttle: unique admission, safe in every strategy profile (thesis, Proposition `prop:throttle`)

The monitor admits a fraction `α = g(M)` of the agents' flow, where `M = 1 - a - κ α Q` is the margin of the admitted
loop and `Q ≥ 0` the agents' total intensity; `g` is continuous, non-decreasing, with values in `[0,1]`, and zero at
or below a buffer `Mmin`.
* `thesis_throttle_fixed_point_exists`: a fixed point `α ∈ [0,1]` exists (intermediate value theorem).
* `thesis_throttle_fixed_point_unique`: it is unique when `g` is monotone and `κ Q ≥ 0`.
* `thesis_throttle_safe`: whenever admission is positive the margin exceeds the buffer.
* `thesis_throttle_margin_floor`: in every case the margin is at least `min Mmin (1 - a)`.
* `thesis_throttle_cap`: positive admission caps admitted feedback, `κ α Q < 1 - a - Mmin`.
-/

namespace CurrentMM

theorem thesis_throttle_fixed_point_exists (g : ℝ → ℝ) (hg : Continuous g) (h0 : ∀ m, 0 ≤ g m) (h1 : ∀ m, g m ≤ 1)
    (a κ Q : ℝ) : ∃ α ∈ Set.Icc (0 : ℝ) 1, α = g (1 - a - κ * α * Q) := by
  set h : ℝ → ℝ := fun α => α - g (1 - a - κ * α * Q) with hh
  have hc : ContinuousOn h (Set.Icc 0 1) := by
    apply Continuous.continuousOn
    exact continuous_id.sub (hg.comp (by continuity))
  have hlo : h 0 ≤ 0 := by simp [hh, h0]
  have hhi : 0 ≤ h 1 := by simp only [hh]; linarith [h1 (1 - a - κ * 1 * Q)]
  obtain ⟨α, hα, hz⟩ := intermediate_value_Icc (show (0 : ℝ) ≤ 1 by norm_num) hc ⟨hlo, hhi⟩
  exact ⟨α, hα, by simp only [hh] at hz; linarith⟩

theorem thesis_throttle_fixed_point_unique (g : ℝ → ℝ) (hm : Monotone g) (a κ Q : ℝ) (hκQ : 0 ≤ κ * Q)
    (α₁ α₂ : ℝ) (h₁ : α₁ = g (1 - a - κ * α₁ * Q)) (h₂ : α₂ = g (1 - a - κ * α₂ * Q)) : α₁ = α₂ := by
  by_contra hne
  rcases lt_or_gt_of_ne hne with hlt | hlt
  · have hM : 1 - a - κ * α₂ * Q ≤ 1 - a - κ * α₁ * Q := by nlinarith
    have := hm hM
    linarith
  · have hM : 1 - a - κ * α₁ * Q ≤ 1 - a - κ * α₂ * Q := by nlinarith
    have := hm hM
    linarith

theorem thesis_throttle_safe (g : ℝ → ℝ) (Mmin : ℝ) (hzero : ∀ m, m ≤ Mmin → g m = 0) (α M : ℝ)
    (hα : α = g M) (hpos : 0 < α) : Mmin < M := by
  by_contra hle
  have := hzero M (le_of_not_gt hle)
  linarith

theorem thesis_throttle_margin_floor (g : ℝ → ℝ) (Mmin : ℝ) (hzero : ∀ m, m ≤ Mmin → g m = 0) (h0 : ∀ m, 0 ≤ g m)
    (a κ Q α : ℝ) (hα : α = g (1 - a - κ * α * Q)) : min Mmin (1 - a) ≤ 1 - a - κ * α * Q := by
  rcases eq_or_lt_of_le (show 0 ≤ α by rw [hα]; exact h0 _) with h | h
  · rw [← h]; simp
  · exact le_trans (min_le_left _ _) (le_of_lt (thesis_throttle_safe g Mmin hzero α _ hα h))

theorem thesis_throttle_cap (g : ℝ → ℝ) (Mmin : ℝ) (hzero : ∀ m, m ≤ Mmin → g m = 0) (a κ Q α : ℝ)
    (hα : α = g (1 - a - κ * α * Q)) (hpos : 0 < α) : κ * α * Q < 1 - a - Mmin := by
  have := thesis_throttle_safe g Mmin hzero α _ hα hpos
  linarith

end CurrentMM
