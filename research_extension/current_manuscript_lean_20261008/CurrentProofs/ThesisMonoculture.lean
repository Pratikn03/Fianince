import Mathlib.Basic.Real.Basic
import Mathlib.Tactic.Linarith
import Mathlib.Tactic.Ring
import Mathlib.Tactic.Positivity
import Mathlib.Tactic.FieldSimp

/-!
# Monoculture: a shared model lowers the margin linearly in its adoption share (thesis, Proposition `prop:monoculture`)

With `N` agents, a share `s` running a common model with response `q_D` and the rest with mean response `q̄`, the margin
is `M(s) = 1 - a - κ N ((1-s) q̄ + s q_D)`.
* `thesis_mono_margin`: `M(s) = M(0) - s κ N (q_D - q̄)`.
* `thesis_mono_threshold`: with `c = κ N (q_D - q̄) > 0` and `M(0) > 0`, the share `s* = M(0)/c` has `M(s*) = 0`.
* `thesis_mono_below` / `thesis_mono_above`: `M(s) > 0` for `s < s*` and `M(s) < 0` for `s > s*`.
* `thesis_mono_common_noise`: `n` users sharing one decision noise of variance `σ²` contribute variance `n² σ²`, which is
  `n` times the `n σ²` of independent noise.
-/

namespace CurrentMM

theorem thesis_mono_margin (a κ N qbar qD s : ℝ) :
    1 - a - κ * N * ((1 - s) * qbar + s * qD) = (1 - a - κ * N * qbar) - s * (κ * N * (qD - qbar)) := by
  ring

theorem thesis_mono_threshold (M0 c : ℝ) (hc : 0 < c) : M0 - (M0 / c) * c = 0 := by
  field_simp; ring

theorem thesis_mono_below (M0 c s : ℝ) (hc : 0 < c) (hs : s < M0 / c) : 0 < M0 - s * c := by
  have : s * c < M0 / c * c := mul_lt_mul_of_pos_right hs hc
  have e : M0 / c * c = M0 := by field_simp
  linarith

theorem thesis_mono_above (M0 c s : ℝ) (hc : 0 < c) (hs : M0 / c < s) : M0 - s * c < 0 := by
  have : M0 / c * c < s * c := mul_lt_mul_of_pos_right hs hc
  have e : M0 / c * c = M0 := by field_simp
  linarith

theorem thesis_mono_common_noise (n σ2 : ℝ) : n ^ 2 * σ2 = n * (n * σ2) := by
  ring

end CurrentMM
