import Mathlib

/-!
# Paper 1, 21 November 2026: the general disclosure game (Supplement Theorem `thm:relabelgeneral`)

General primitives: private payoffs `π` with slopes in `[β, B]`, concealment cost `c · C(z)` with `C` nonnegative,
`C(z) ≤ C(1)` on `[0,1]` and `C(z) ≥ κ z²`. The two lemmas below are the per-class steps of the proof; the
welfare bounds then follow by the Lipschitz property of the welfare function, stated in the theorem.
-/
namespace Paper1Revision5

/-- Cheap channels. A class with best reachable gain `D` (at channel cost `cs`) and chosen gain `g = z d ≤ D` at
cost `cz = c C(z) ≥ 0`, whose payoff is at least that of routing everything through the best label
(`πg - cz ≥ πD - cs * C1`), with slope at least `β > 0` (`β (D - g) ≤ πD - πg`), loses at most `cs C1 / β` in
effective retention and pays at most `cs C1`. -/
theorem general_cheap (β D g πD πg cz cs C1 : ℝ) (hβ : 0 < β) (hcz : 0 ≤ cz)
    (hslope : β * (D - g) ≤ πD - πg) (hopt : πD - cs * C1 ≤ πg - cz) (hgD : g ≤ D) :
    D - g ≤ cs * C1 / β ∧ cz ≤ cs * C1 := by
  constructor
  · rw [le_div_iff₀ hβ]
    nlinarith
  · have : πg ≤ πD := by nlinarith
    linarith

/-- Expensive channels. If the chosen share `z ∈ [0,1]` with gap `d ∈ [0,1]` pays at least the no-routing option
(`c C(z) ≤ πg - π0 ≤ B z d`) and `C(z) ≥ κ z²`, then `z ≤ B / (c κ)` and the cost is at most `B² / (c κ)`. -/
theorem general_expensive (B c κ z d Cz : ℝ) (hB : 0 ≤ B) (hc : 0 < c) (hκ : 0 < κ) (hz0 : 0 ≤ z)
    (hd0 : 0 ≤ d) (hd1 : d ≤ 1) (hCz : κ * z ^ 2 ≤ Cz) (hpay : c * Cz ≤ B * z * d) :
    z ≤ B / (c * κ) ∧ c * Cz ≤ B ^ 2 / (c * κ) := by
  have hckpos : 0 < c * κ := mul_pos hc hκ
  have ha : c * (κ * z ^ 2) ≤ c * Cz := mul_le_mul_of_nonneg_left hCz hc.le
  have hBz : 0 ≤ B * z := mul_nonneg hB hz0
  have hb : B * z * d ≤ B * z := by
    have := mul_le_mul_of_nonneg_left hd1 hBz
    linarith
  have h1 : c * κ * z ^ 2 ≤ B * z := by
    have e : c * κ * z ^ 2 = c * (κ * z ^ 2) := by ring
    linarith
  have hz : z ≤ B / (c * κ) := by
    rw [le_div_iff₀ hckpos]
    rcases eq_or_lt_of_le hz0 with h | h
    · rw [← h]; simp; exact hB
    · nlinarith
  refine ⟨hz, ?_⟩
  have h2 : c * Cz ≤ B * z := le_trans hpay hb
  have h3 : B * z ≤ B * (B / (c * κ)) := mul_le_mul_of_nonneg_left hz hB
  have h4 : B * (B / (c * κ)) = B ^ 2 / (c * κ) := by ring
  linarith

/-- Welfare transfer: if each effective retention moves by at most `δ j` and the welfare function is Lipschitz with
weights `L j`, welfare moves by at most `Σ L j δ j`. -/
theorem lipschitz_transfer {K : ℕ} (U : (Fin K → ℝ) → ℝ) (L δ : Fin K → ℝ) (e e' : Fin K → ℝ)
    (hU : |U e - U e'| ≤ ∑ j, L j * |e j - e' j|) (hL : ∀ j, 0 ≤ L j) (hδ : ∀ j, |e j - e' j| ≤ δ j) :
    |U e - U e'| ≤ ∑ j, L j * δ j := by
  refine le_trans hU (Finset.sum_le_sum fun j _ => ?_)
  exact mul_le_mul_of_nonneg_left (hδ j) (hL j)

end Paper1Revision5
