import Mathlib

/-!
# Paper 1, 21 November 2026: Theorem 6.1 end to end, the disclosure-game case analysis, comparative statics

Part 1 assembles Theorem 6.1 (pairwise detection and forecast mismatch) from three probability facts that enter as
explicit hypotheses: the per-step Gaussian divergence `(m - m')² / (2σ²)`, the chain rule over the record, and
Pinsker's inequality `KL ≥ 2 TV²`. Everything else is checked here.

Part 2 checks the case analysis of Proposition `n:relabel` (the optimal class-tag value in each of the four cases,
and that policies inducing complete pooling are dominated).

Part 3 checks the comparative statics of Corollary `cor:relabelstatics`.
-/
namespace Paper1Revision4

open Finset

/-! ## Part 1: Theorem 6.1 -/

/-- Excess forecast error: with truth `m + ε`, `E ε = 0`, `E ε² = σ²`, the alternative mean `m'` has expected
squared error `σ² + (m - m')²`; the excess over the true mean is `(m - m')²`. Expectation enters through
linearity: `E[(m - m' + ε)²] = (m - m')² + 2 (m - m') E ε + E ε²`. -/
theorem excess_forecast_error (m m' Eε Eε2 σ2 : ℝ) (h0 : Eε = 0) (h2 : Eε2 = σ2) :
    ((m - m') ^ 2 + 2 * (m - m') * Eε + Eε2) - (0 ^ 2 + 2 * 0 * Eε + Eε2) = (m - m') ^ 2 := by
  subst h0; subst h2; ring

/-- Theorem 6.1 assembled. Hypotheses: per-step Gaussian divergence `kl t = V t / (2σ²)` (`hstep`), the chain
rule `KL = Σ kl t` (`hchain`), Pinsker `2 TV² ≤ KL` (`hpinsker`), and the testing inequality
`1 - TV ≤ α + β` (`htest`). Conclusions: `KL = Λ / 2` with `Λ = Σ V t / σ²`, and both errors below `1/4`
force `Λ > 1`. -/
theorem dual_end_to_end {T : ℕ} (σ2 : ℝ) (hσ : 0 < σ2) (V kl : Fin T → ℝ) (KL tv α β : ℝ)
    (hstep : ∀ t, kl t = V t / (2 * σ2)) (hchain : KL = ∑ t, kl t)
    (hpinsker : 2 * tv ^ 2 ≤ KL) (htest : 1 - tv ≤ α + β) (hα : α < 1 / 4) (hβ : β < 1 / 4) :
    KL = (∑ t, V t / σ2) / 2 ∧ 1 < ∑ t, V t / σ2 := by
  have hKL : KL = (∑ t, V t / σ2) / 2 := by
    rw [hchain, Finset.sum_div]
    apply Finset.sum_congr rfl
    intro t _
    rw [hstep t]
    field_simp
  refine ⟨hKL, ?_⟩
  have htv : 1 / 2 < tv := by linarith
  have h1 : (1 : ℝ) / 4 < tv ^ 2 := by nlinarith
  linarith

/-- The Bayesian mixture loses at most `log (1/π)` against the true candidate. -/
theorem mixture_bound (q p π : ℝ) (hp : 0 < p) (hπ : 0 < π) (hq : π * p ≤ q) :
    Real.log p - Real.log q ≤ Real.log (1 / π) := by
  have hq0 : 0 < q := lt_of_lt_of_le (mul_pos hπ hp) hq
  have h1 : Real.log (π * p) ≤ Real.log q := Real.log_le_log (mul_pos hπ hp) hq
  rw [Real.log_mul hπ.ne' hp.ne', one_div, Real.log_inv] at *
  linarith

/-! ## Part 2: the disclosure game, case analysis

Welfare under class tags with interior hiding is `φ x d = m x + θ (a d - d²/(2g))`, with `0 ≤ d ≤ x ≤ 1`,
`m = s - θ a` (Paper1Revision3.tag_welfare_identity). -/

/-- Case `m ≥ 0`, `a g ≤ 1`: the value is at most `m + θ a² g / 2`. -/
theorem case_mnonneg_inner (m θ a g x d : ℝ) (hm : 0 ≤ m) (hθ : 0 ≤ θ) (hg : 0 < g)
    (hx1 : x ≤ 1) :
    m * x + θ * (a * d - d ^ 2 / (2 * g)) ≤ m + θ * (a ^ 2 * g / 2) := by
  have h1 : m * x ≤ m := by nlinarith
  have h2 : a * d - d ^ 2 / (2 * g) ≤ a ^ 2 * g / 2 := by
    have key : a ^ 2 * g / 2 - (a * d - d ^ 2 / (2 * g)) = (d - a * g) ^ 2 / (2 * g) := by
      field_simp; ring
    have : 0 ≤ (d - a * g) ^ 2 / (2 * g) := by positivity
    linarith
  nlinarith

/-- Case `m ≥ 0`, `a g ≥ 1`: the value is at most `m + θ (a - 1/(2g))`. -/
theorem case_mnonneg_outer (m θ a g x d : ℝ) (hm : 0 ≤ m) (hθ : 0 ≤ θ) (hg : 0 < g)
    (hag : 1 ≤ a * g) (hd0 : 0 ≤ d) (hdx : d ≤ x) (hx1 : x ≤ 1) :
    m * x + θ * (a * d - d ^ 2 / (2 * g)) ≤ m + θ * (a - 1 / (2 * g)) := by
  have h1 : m * x ≤ m := by nlinarith
  have hd1 : d ≤ 1 := le_trans hdx hx1
  have key : (a - 1 / (2 * g)) - (a * d - d ^ 2 / (2 * g)) = (1 - d) * (a - (1 + d) / (2 * g)) := by
    field_simp; ring
  have h3 : (1 + d) / (2 * g) ≤ a := by
    rw [div_le_iff₀ (by positivity)]
    nlinarith
  have h4 : 0 ≤ (1 - d) * (a - (1 + d) / (2 * g)) := mul_nonneg (by linarith) (by linarith)
  nlinarith

/-- Case `m < 0` (so `s < θ a`), `s g ≤ θ`: the value is at most `s² g / (2θ)`. -/
theorem case_mneg_inner (s θ a g x d : ℝ) (hθ : 0 < θ) (hg : 0 < g) (hm : s - θ * a < 0)
    (hdx : d ≤ x) :
    (s - θ * a) * x + θ * (a * d - d ^ 2 / (2 * g)) ≤ s ^ 2 * g / (2 * θ) := by
  have h1 : (s - θ * a) * x ≤ (s - θ * a) * d := by nlinarith
  have h2 : s * d - θ * (d ^ 2 / (2 * g)) ≤ s ^ 2 * g / (2 * θ) := by
    have key : s ^ 2 * g / (2 * θ) - (s * d - θ * (d ^ 2 / (2 * g)))
        = θ * (d - s * g / θ) ^ 2 / (2 * g) := by
      field_simp; ring
    have : 0 ≤ θ * (d - s * g / θ) ^ 2 / (2 * g) := by positivity
    linarith
  nlinarith

/-- Case `m < 0`, `s g ≥ θ`: the value is at most `s - θ/(2g)`. -/
theorem case_mneg_outer (s θ a g x d : ℝ) (hθ : 0 < θ) (hg : 0 < g) (hm : s - θ * a < 0)
    (hsg : θ ≤ s * g) (hd0 : 0 ≤ d) (hdx : d ≤ x) (hx1 : x ≤ 1) :
    (s - θ * a) * x + θ * (a * d - d ^ 2 / (2 * g)) ≤ s - θ / (2 * g) := by
  have h1 : (s - θ * a) * x ≤ (s - θ * a) * d := by nlinarith
  have hd1 : d ≤ 1 := le_trans hdx hx1
  have key : (s - θ / (2 * g)) - (s * d - θ * (d ^ 2 / (2 * g))) = (1 - d) * (s - θ * (1 + d) / (2 * g)) := by
    field_simp; ring
  have h3 : θ * (1 + d) / (2 * g) ≤ s := by
    rw [div_le_iff₀ (by positivity)]
    nlinarith
  have h4 : 0 ≤ (1 - d) * (s - θ * (1 + d) / (2 * g)) := mul_nonneg (by linarith) (by linarith)
  nlinarith

/-- Complete pooling (`z = 1`) is dominated: it yields `m x - θγ/2`, below the gap-free policy's `m x`. -/
theorem pooling_dominated (m x θ γ : ℝ) (hθ : 0 ≤ θ) (hγ : 0 ≤ γ) : m * x - θ * γ / 2 ≤ m * x := by
  nlinarith

/-! ## Part 3: comparative statics -/

/-- The optimal label gap `a γ / (b (2a + b))` falls as the restricted traders' private gain `b` rises. -/
theorem gap_antitone_gain (a γ b b' : ℝ) (ha : 0 < a) (hγ : 0 < γ) (hb : 0 < b) (hbb : b < b') :
    a * γ / (b' * (2 * a + b')) < a * γ / (b * (2 * a + b)) := by
  apply div_lt_div_of_pos_left (by positivity) (by positivity)
  nlinarith

/-- The equilibrium hiding share `a / (2a + b)` falls as `b` rises. -/
theorem hiding_share_antitone_gain (a b b' : ℝ) (ha : 0 < a) (hb : 0 < b) (hbb : b < b') :
    a / (2 * a + b') < a / (2 * a + b) := by
  apply div_lt_div_of_pos_left ha (by positivity) (by linarith)

/-- The hiding share `a / (2a + b)` rises with the harm `a`. -/
theorem hiding_share_monotone_harm (a a' b : ℝ) (ha : 0 < a) (hb : 0 < b) (haa : a < a') :
    a / (2 * a + b) < a' / (2 * a' + b) := by
  have ha' : 0 < a' := by linarith
  rw [div_lt_div_iff₀ (by positivity) (by positivity)]
  nlinarith

/-- Interior value of class tags `θ a² γ / (2 b (2a + b))` (case `m ≥ 0`) falls as `b` rises. -/
theorem tag_value_antitone_gain (θ a γ b b' : ℝ) (hθ : 0 < θ) (ha : 0 < a) (hγ : 0 < γ) (hb : 0 < b)
    (hbb : b < b') :
    θ * a ^ 2 * γ / (2 * b' * (2 * a + b')) < θ * a ^ 2 * γ / (2 * b * (2 * a + b)) := by
  apply div_lt_div_of_pos_left (by positivity) (by positivity)
  nlinarith

/-- Interior value of class tags (case `m ≥ 0`) rises with the harm `a`. -/
theorem tag_value_monotone_harm (θ a a' γ b : ℝ) (hθ : 0 < θ) (ha : 0 < a) (hγ : 0 < γ) (hb : 0 < b)
    (haa : a < a') :
    θ * a ^ 2 * γ / (2 * b * (2 * a + b)) < θ * a' ^ 2 * γ / (2 * b * (2 * a' + b)) := by
  have ha' : 0 < a' := by linarith
  rw [div_lt_div_iff₀ (by positivity) (by positivity)]
  have hk : 0 < θ * γ * (2 * b) := by positivity
  have hp : 0 < (a' - a) * (2 * a * a' + b * (a + a')) := mul_pos (by linarith) (by positivity)
  have : a ^ 2 * (2 * a' + b) < a' ^ 2 * (2 * a + b) := by nlinarith [hp]
  have h2 : θ * a ^ 2 * γ * (2 * b * (2 * a' + b)) = (θ * γ * (2 * b)) * (a ^ 2 * (2 * a' + b)) := by ring
  have h3 : θ * a' ^ 2 * γ * (2 * b * (2 * a + b)) = (θ * γ * (2 * b)) * (a' ^ 2 * (2 * a + b)) := by ring
  rw [h2, h3]
  exact mul_lt_mul_of_pos_left this hk

end Paper1Revision4
