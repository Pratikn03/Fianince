import CurrentProofs.Paper1CRUniform
import CurrentProofs.Paper1CRS71iiiW2

/-!
# Paper 1, Proposition S7.1 (iii), uniformly in `T`: the second weight

`p1_prop_S7_1_iii_two_uniform`: the same `T`-free lower constant `1/p1UnifB` for the entry `[F_T⁻¹]₂₂` of the second
weight, under the small-gain margin of `Paper1CRUniform`. The weak direction `v` is the same; its second coordinate
is `-1`.
-/

namespace CurrentMM

open Finset Matrix

theorem p1_prop_S7_1_iii_two_uniform (a κ κmin κm wm w1 w2 r1 r2 ρ θ : ℝ) (T : ℕ) (hT : 4 ≤ T)
    (hκmin : 0 < κmin) (hκ1 : κmin ≤ |κ|) (hκ2 : |κ| ≤ κm) (hw1 : 0 < w1) (hw1' : w1 ≤ wm) (hw2 : 0 < w2)
    (hw2' : w2 ≤ wm) (hr1 : 0 ≤ r1) (hr12 : r1 < r2) (hr2ρ : r2 ≤ ρ) (hρθ : ρ < θ) (hθ1 : θ < 1)
    (hmar : |a| + κm * (2 * wm) * θ / (θ - ρ) ≤ θ) :
    1 / p1UnifB κm ρ θ / (r2 - r1) ^ 6 ≤
      ((p1TapJac a κ T ![w1, w2, r1, r2])ᵀ * p1TapJac a κ T ![w1, w2, r1, r2])⁻¹ 1 1 ∧
    ((p1TapJac a κ T ![w1, w2, r1, r2])ᵀ * p1TapJac a κ T ![w1, w2, r1, r2])⁻¹ 1 1 ≤
      5 * ((4 * ((1 + 2 * (|a| + κm * (2 * wm)) + (|a| + κm * (2 * wm)) ^ 2 + 2 * (κm * (2 * wm)) +
          2 * (|a| + κm * (2 * wm)) * (κm * (2 * wm))) * 6) / κmin ^ 2) *
        (4 * ((1 + 2 * (|a| + κm * (2 * wm)) + (|a| + κm * (2 * wm)) ^ 2 + 2 * (κm * (2 * wm)) +
          2 * (|a| + κm * (2 * wm)) * (κm * (2 * wm))) * 6) / κmin ^ 2)) / (r2 - r1) ^ 6 := by
  have hr2' : r2 ≤ 1 := by linarith
  have hθ0 : 0 ≤ θ := by linarith
  have hκ0 : κ ≠ 0 := fun h => by rw [h, abs_zero] at hκ1; linarith
  have hd : r2 - r1 ≠ 0 := by linarith
  have hd6 : 0 < (r2 - r1) ^ 6 := pow_pos (by linarith) 6
  have hJ := p1_S71iii_isUnit a κ w1 w2 r1 r2 T hT hκ0 hw1.ne' hw2.ne' hd
  have hB := (p1_prop_S7_1_iii_uniform a κ κmin κm wm w1 w2 r1 r2 ρ θ T hT hκmin hκ1 hκ2 hw1 hw1' hw2 hw2' hr1
    hr12 hr2ρ hρθ hθ1 hmar).1
  have hfix := p1_prop_S7_1_iii_two a κ κmin κm wm w1 w2 r1 r2 T hT hκmin hκ1 hκ2 hw1 hw1' hw2 hw2' hr1 hr12 hr2'
  refine ⟨?_, hfix.2⟩
  have hlow := p1_fisher_entry_lower _ hJ 1 ![1, -1, (r2 - r1) / (2 * w1), (r2 - r1) / (2 * w2)]
  have hnorm := p1_S71iii_weak_norm_uniform a κ κm wm w1 w2 r1 r2 ρ ((ρ + θ) / 2) θ ((1 + θ) / 2) T hκ2
    hw1 hw1' hw2 hw2' hr1 hr12.le hr2ρ (by linarith) (by linarith) (by linarith) (by linarith) hmar
  rw [p1_unifB_eq κm ρ θ hρθ hθ1 hθ0] at hnorm
  have hv : (![1, -1, (r2 - r1) / (2 * w1), (r2 - r1) / (2 * w2)] : Fin 4 → ℝ) 1 ^ 2 = 1 := by simp
  rw [hv] at hlow
  generalize hJdef : p1TapJac a κ T ![w1, w2, r1, r2] = J at hJ hlow hnorm ⊢
  have hF0 : 0 ≤ (Jᵀ * J)⁻¹ 1 1 := by
    rw [← p1_fisher_col_norm J hJ 1]; exact p1_dot_self_nonneg _
  rw [div_div, div_le_iff₀ (mul_pos hB hd6)]
  calc (1 : ℝ) ≤ (Jᵀ * J)⁻¹ 1 1 * ((J *ᵥ ![1, -1, (r2 - r1) / (2 * w1), (r2 - r1) / (2 * w2)]) ⬝ᵥ
        (J *ᵥ ![1, -1, (r2 - r1) / (2 * w1), (r2 - r1) / (2 * w2)])) := hlow
    _ ≤ (Jᵀ * J)⁻¹ 1 1 * (p1UnifB κm ρ θ * (r2 - r1) ^ 6) := mul_le_mul_of_nonneg_left hnorm hF0

end CurrentMM
