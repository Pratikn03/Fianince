import Mathlib
namespace CurrentMM

/-- Conditional equilibrium sensitivity. The hypotheses are substantive:
neither uniqueness nor contraction follows from anonymous flow alone. -/
theorem p1_endogenous_contraction_sensitivity
    (x y Lk Lg epsilon : ℝ) (hk : 0 ≤ Lk) (hg : 0 ≤ Lg)
    (he : 0 ≤ epsilon) (hContract : Lk * Lg < 1)
    (hResponse : |x-y| ≤ Lk * (Lg * |x-y| + epsilon)) :
    |x-y| ≤ Lk * epsilon / (1-Lk*Lg) := by
  apply (le_div_iff₀ (by linarith : 0 < 1-Lk*Lg)).2
  nlinarith

/-- A fixed lower bound on all account shares rules out an unbounded number
of subaccounts; it is not robustness to unrestricted Sybil splitting. -/
theorem p1_sybil_share_count_bound {M : ℕ} (shares : Fin M → ℝ)
    (alpha : ℝ) (hShares : ∀ i, alpha ≤ shares i)
    (hTotal : ∑ i, shares i = 1) : (M : ℝ) * alpha ≤ 1 := by
  have hs := Finset.sum_le_sum (fun i (_ : i ∈ (Finset.univ : Finset (Fin M))) => hShares i)
  simpa [hTotal] using hs

/-- Camouflage is unprofitable only once its lower cost exceeds a specified
uniform profit bound. Pointwise finiteness of profit is insufficient. -/
theorem p1_camouflage_unprofitable (cost profit lower upper : ℝ)
    (hCost : lower ≤ cost) (hProfit : profit ≤ upper) (hGap : upper < lower) :
    profit-cost < 0 := by linarith

end CurrentMM
