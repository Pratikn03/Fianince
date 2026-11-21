import Mathlib

/-!
# Paper 1, 21 November 2026: the disclosure game with relabeling (Proposition `n:hiding`)

Deterministic steps. H-class traders route a share `z` of their activity through benign labels at
resource cost `γ z²/2`; the supervisor sets label retentions `y ≤ x`; `d = x - y` is the label gap.
Notation: `a = -n_H > 0`, `b = b_H > 0`, `g = γ / (b (2a + b))`.

NOT formalized: the case analysis that assembles these steps into the optimal policy (checked by brute
force in `t6/t6_check.py`).
-/
namespace Paper1Revision3

/-- Hiding best response: with label gap `d`, the H traders' payoff `b d z - γ z²/2` is maximized at
`z = b d / γ` (before the cap `z ≤ 1`). -/
theorem hide_best_response (b d γ z : ℝ) (hγ : 0 < γ) :
    b * d * z - γ * z ^ 2 / 2 ≤ b * d * (b * d / γ) - γ * (b * d / γ) ^ 2 / 2 := by
  have key : b * d * (b * d / γ) - γ * (b * d / γ) ^ 2 / 2 - (b * d * z - γ * z ^ 2 / 2)
      = γ / 2 * (z - b * d / γ) ^ 2 := by
    field_simp
    ring
  nlinarith [sq_nonneg (z - b * d / γ), key]

/-- Welfare under class tags with interior hiding `z = b d / γ`, for `d = x - y`, equals the uniform
retention value `m x` plus `θ (a d - d²/(2g))`, where `m = θ n_H + (1-θ) n_S`. -/
theorem tag_welfare_identity (θ a nS b γ x y : ℝ) (hb : 0 < b) (hγ : 0 < γ) (ha : 0 < a) :
    let z := b * (x - y) / γ
    let g := γ / (b * (2 * a + b))
    θ * ((1 - z) * y + z * x) * (-a) + (1 - θ) * x * nS - θ * γ * z ^ 2 / 2
      = (θ * (-a) + (1 - θ) * nS) * x + θ * (a * (x - y) - (x - y) ^ 2 / (2 * g)) := by
  intro z g
  have h2 : 0 < 2 * a + b := by linarith
  simp only [z, g]
  field_simp
  ring

/-- The label-gap problem `a d - d²/(2g)` has maximum `a² g / 2`, attained at `d = a g`. -/
theorem label_gap_value (a g d : ℝ) (hg : 0 < g) : a * d - d ^ 2 / (2 * g) ≤ a ^ 2 * g / 2 := by
  have key : a ^ 2 * g / 2 - (a * d - d ^ 2 / (2 * g)) = (d - a * g) ^ 2 / (2 * g) := by
    field_simp
    ring
  have : 0 ≤ (d - a * g) ^ 2 / (2 * g) := by positivity
  linarith

theorem label_gap_attained (a g : ℝ) (hg : 0 < g) :
    a * (a * g) - (a * g) ^ 2 / (2 * g) = a ^ 2 * g / 2 := by
  field_simp
  ring

/-- Case `m ≥ 0`, interior gap (`a g ≤ 1`): class tags are worth `θ a² g / 2`, strictly less than the
audit trail's `θ a` (its value over the uniform cut when `m ≥ 0`). -/
theorem tags_below_audit_mnonneg (θ a g : ℝ) (hθ : 0 < θ) (ha : 0 < a) (hg : 0 < g)
    (hint : a * g ≤ 1) : θ * a ^ 2 * g / 2 < θ * a := by
  have : a ^ 2 * g ≤ a := by nlinarith
  nlinarith

/-- Case `m < 0`, interior retention (`x̂ = s g / θ ≤ 1`, `s = (1-θ) n_S > 0`): class tags are worth
`s² g / (2θ) ≤ s / 2`, below the audit trail's `s`. -/
theorem tags_below_audit_mneg (θ s g : ℝ) (hθ : 0 < θ) (hs : 0 < s) (hg : 0 < g)
    (hint : s * g / θ ≤ 1) : s ^ 2 * g / (2 * θ) < s := by
  have h1 : s * g ≤ θ := by
    have := (div_le_one hθ).mp hint
    linarith
  have h2 : s ^ 2 * g / (2 * θ) ≤ s / 2 := by
    rw [div_le_div_iff₀ (by positivity) (by norm_num)]
    nlinarith
  linarith

/-- The value of class tags is increasing in the relabeling cost through `g` (both interior branches
are linear in `g` with positive slope). -/
theorem tag_value_mono (c g g' : ℝ) (hc : 0 < c) (hgg : g < g') : c * g < c * g' := by
  nlinarith

/-- Outer branch (`g` large): value `θ a - θ/(2g)` rises with `g` towards the audit value `θ a`. -/
theorem outer_branch_mono (θ g g' : ℝ) (hθ : 0 < θ) (hg : 0 < g) (hgg : g < g') :
    -(θ / (2 * g)) < -(θ / (2 * g')) := by
  have : θ / (2 * g') < θ / (2 * g) := by
    apply div_lt_div_of_pos_left hθ (by positivity) (by linarith)
  linarith

/-- The equilibrium hiding share at the optimal gap `d = a g` is `a / (2a + b) < 1`: the optimal
tag policy never induces complete pooling. -/
theorem hiding_share_lt_one (a b γ : ℝ) (ha : 0 < a) (hb : 0 < b) (hγ : 0 < γ) :
    b * (a * (γ / (b * (2 * a + b)))) / γ = a / (2 * a + b) ∧ a / (2 * a + b) < 1 := by
  have h2 : 0 < 2 * a + b := by linarith
  constructor
  · field_simp
  · rw [div_lt_one h2]
    linarith

end Paper1Revision3
