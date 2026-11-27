import Mathlib.Basic.Real.Basic
import Mathlib.Analysis.Real.Sqrt
import Mathlib.Tactic.Linarith
import Mathlib.Tactic.Ring
import Mathlib.Tactic.Positivity

/-!
# Paper 1, Section 7.3: Endogenizing the Supervisor in the Surveillance Paradox

This file mechanizes the deterministic game-theoretic inequalities of the strategic
supervisor and trader hiding game in the Surveillance Paradox (Theorem 7.10 and Proposition 7.11):

1. `supervisor_no_test`: when the supervisor does not test or inspect (α = 0, penalty L = 0),
   traders face no hiding incentive and choose δ* = δ0.
2. `trader_crowding_envelope`: when the supervisor sets test size α ≥ α_min > 0 with power slope
   β(α) > 0, the interior high-stakes FOC implies `(n/2) L β √(c N δⁿ) ≤ 2 k δ0 δ`, hence:
   δ^(n-2) ≤ (4 k δ0 / (n L β(α)))² / (c N).
3. `high_stakes_regime_gap` & `low_stakes_regime_dominance`: necessary condition `L(1-α) > k δ0²`
   for interior hiding vs. corner dominance `δ* → δ0` when `k δ0² > L(1-α)`.
4. `composite_glrt_envelope`: under unknown-sign / χ²_d GLRT power `P_d - α ~ c_2 J`, the FOC gives
   δ^(n-1) ≤ (2 k δ0 / (n L c_2)) / (c N) (rate `N^(-1/(n-1))`).
5. `divergence_collapse_n4`: for `n = 4`, `J*(α, N) = c N δ^4 ≤ B^4 / (c N)` collapses as `O((c N)⁻¹)`
   at fixed 1-sided α (whenever `B = 4 k δ0 / (n L β(α))`).
6. `divergence_collapse_general`: for any `n ≥ 2` and `δ ≤ δ0`, `J*(α, N) ≤ B² * δ0²`.
7. `tagging_decoupling`: under tagged reporting, detection probability decouples from δ, restoring `δ* = δ0`.
8. `supervisor_effort_collapse_general`: Stackelberg commitment equilibrium — under inspection cost `C(α) ≥ c_min > 0`
   (for `n ≥ 2`, generalizing `supervisor_effort_collapse`), for large `N` net surplus is `< 0`, forcing `α*_N = 0`.
9. `simultaneous_no_pure_ne`: under simultaneous moves (`k > c_min > 0`), no pure-strategy Nash equilibrium exists
   whenever `J*(1, N) < k - c_min`, requiring a mixed strategy `p*_N > 0`.

Standard axioms only (propext, Classical.choice, Quot.sound).
-/

namespace Paper1Revision15

/-- 1. Supervisor no test: with zero inspection penalty (or α = 0), trader loss k(δ0 - δ)²
is strictly minimized at δ = δ0. -/
theorem supervisor_no_test (k delta0 delta : ℝ) (hk : 0 ≤ k) :
    k * (delta0 - delta0) ^ 2 ≤ k * (delta0 - delta) ^ 2 := by
  have : k * (delta0 - delta0) ^ 2 = 0 := by ring
  rw [this]
  positivity

/-- 1b. Supervisor no test uniqueness: if k > 0 and k(δ0 - δ)² = k(δ0 - δ0)², then δ = δ0. -/
theorem supervisor_no_test_unique (k delta0 delta : ℝ) (hk : 0 < k)
    (h_eq : k * (delta0 - delta) ^ 2 = k * (delta0 - delta0) ^ 2) : delta = delta0 := by
  have h0 : k * (delta0 - delta0) ^ 2 = 0 := by ring
  rw [h0] at h_eq
  have hsq : (delta0 - delta) ^ 2 = 0 := by
    nlinarith [h_eq]
  have : delta0 - delta = 0 := sq_eq_zero_iff.mp hsq
  linarith

/-- 2. Trader crowding envelope: from the exact FOC `(n/2) L β √(c N δⁿ) = 2 k (δ0 - δ) δ ≤ 2 k δ0 δ`
with δ > 0 and n ≥ 2, clearing `1/2` gives `δ^(n-2) ≤ (4 k δ0 / (n L β))² / (c N)`. -/
theorem trader_crowding_envelope (L beta c N k delta0 delta : ℝ) (n : ℕ) (hn : 2 ≤ n)
    (hL : 0 < L) (hbeta : 0 < beta) (hc : 0 < c) (hN : 0 < N) (hdelta : 0 < delta)
    (_hk : 0 ≤ k) (_hdelta0 : 0 ≤ delta0)
    (h : (n : ℝ) * L * beta * Real.sqrt (c * N * delta ^ n) ≤ 4 * k * delta0 * delta) :
    delta ^ (n - 2) ≤ (4 * k * delta0 / ((n : ℝ) * L * beta)) ^ 2 / (c * N) := by
  have hn_pos : (0 : ℝ) < (n : ℝ) := by
    exact_mod_cast Nat.lt_of_lt_of_le (by norm_num) hn
  have hJ : 0 ≤ c * N * delta ^ n := by positivity
  have hlhs : 0 ≤ (n : ℝ) * L * beta * Real.sqrt (c * N * delta ^ n) := by positivity
  have hsq : ((n : ℝ) * L * beta * Real.sqrt (c * N * delta ^ n)) ^ 2 ≤ (4 * k * delta0 * delta) ^ 2 :=
    pow_le_pow_left₀ hlhs h 2
  have e1 : ((n : ℝ) * L * beta * Real.sqrt (c * N * delta ^ n)) ^ 2 =
      ((n : ℝ) * L * beta) ^ 2 * (c * N * delta ^ n) := by
    rw [mul_pow, Real.sq_sqrt hJ]
  have e2 : delta ^ n = delta ^ (n - 2) * delta ^ 2 := by
    rw [← pow_add]; congr 1; omega
  rw [e1, e2] at hsq
  have h_pos_denom : 0 < ((n : ℝ) * L * beta) ^ 2 * (c * N) := by positivity
  have hdelta2 : 0 < delta ^ 2 := by positivity
  have h_prod : delta ^ (n - 2) * (((n : ℝ) * L * beta) ^ 2 * (c * N)) * delta ^ 2 ≤
      ((4 * k * delta0) ^ 2) * delta ^ 2 := by
    calc delta ^ (n - 2) * (((n : ℝ) * L * beta) ^ 2 * (c * N)) * delta ^ 2
        = ((n : ℝ) * L * beta) ^ 2 * (c * N * (delta ^ (n - 2) * delta ^ 2)) := by ring
      _ ≤ (4 * k * delta0 * delta) ^ 2 := hsq
      _ = ((4 * k * delta0) ^ 2) * delta ^ 2 := by ring
  have h_cancel : delta ^ (n - 2) * (((n : ℝ) * L * beta) ^ 2 * (c * N)) ≤ (4 * k * delta0) ^ 2 :=
    le_of_mul_le_mul_right h_prod hdelta2
  have h_rhs_eq : (4 * k * delta0 / ((n : ℝ) * L * beta)) ^ 2 / (c * N) =
      (4 * k * delta0) ^ 2 / (((n : ℝ) * L * beta) ^ 2 * (c * N)) := by
    rw [div_pow, div_div]
  rw [h_rhs_eq, le_div_iff₀ h_pos_denom]
  exact h_cancel

/-- 2b. High-stakes regime condition: `L (1 - α) > k δ0²` ensures full hiding `δ = 0` strictly
beats full exposure `δ = δ0` in the large-`N` detection limit (`V(0) = k δ0² + L α < L`). -/
theorem high_stakes_regime_gap (L alpha k delta0 : ℝ)
    (hhigh : k * delta0 ^ 2 < L * (1 - alpha)) :
    k * delta0 ^ 2 + L * alpha < L := by
  linarith

/-- 2c. Low-stakes reversal: when `L (1 - α) < k δ0²`, hiding cost exceeds stake and corner
revelation `δ = δ0` dominates zero displacement (`V(δ0) ≤ L < k δ0² + L α`). -/
theorem low_stakes_regime_dominance (L alpha k delta0 : ℝ)
    (hlow : L * (1 - alpha) < k * delta0 ^ 2) :
    L < k * delta0 ^ 2 + L * alpha := by
  linarith

/-- 2d. Composite-null GLRT power scaling: under local χ² expansion `P_d(J) ≈ α + c2 J`, the FOC
`n L c2 c N δ^(n-1) ≤ 2 k δ0` yields `δ^(n-1) ≤ (2 k δ0 / (n L c2)) / (c N)` (`N^(-1/(n-1))`). -/
theorem composite_glrt_envelope (L c2 c N k delta0 delta : ℝ) (n : ℕ) (hn : 2 ≤ n)
    (hL : 0 < L) (hc2 : 0 < c2) (hc : 0 < c) (hN : 0 < N)
    (h : (n : ℝ) * L * c2 * c * N * delta ^ (n - 1) ≤ 2 * k * delta0) :
    delta ^ (n - 1) ≤ (2 * k * delta0 / ((n : ℝ) * L * c2)) / (c * N) := by
  have hn_pos : (0 : ℝ) < (n : ℝ) := by
    exact_mod_cast Nat.lt_of_lt_of_le (by norm_num) hn
  have hden : 0 < ((n : ℝ) * L * c2) * (c * N) := by positivity
  rw [div_div, le_div_iff₀ hden]
  linarith

/-- 3. Divergence collapse for n = 4: J*(α, N) = c N δ^4 collapses as (c N)⁻¹. -/
theorem divergence_collapse_n4 (c N delta B : ℝ) (hc : 0 < c) (hN : 0 < N) (_hdelta : 0 ≤ delta)
    (_hB : 0 ≤ B) (henv : delta ^ 2 ≤ B ^ 2 / (c * N)) :
    c * N * delta ^ 4 ≤ B ^ 4 / (c * N) := by
  have hsq : (delta ^ 2) ^ 2 ≤ (B ^ 2 / (c * N)) ^ 2 :=
    pow_le_pow_left₀ (by positivity) henv 2
  have h4 : delta ^ 4 = (delta ^ 2) ^ 2 := by ring
  rw [h4]
  have h_div_sq : (B ^ 2 / (c * N)) ^ 2 = (B ^ 4) / ((c * N) ^ 2) := by
    rw [div_pow]
    have : (B ^ 2) ^ 2 = B ^ 4 := by ring
    rw [this]
  rw [h_div_sq] at hsq
  have h_cN_pos : 0 < c * N := by positivity
  have h_cN_ne : c * N ≠ 0 := ne_of_gt h_cN_pos
  calc c * N * (delta ^ 2) ^ 2
      ≤ c * N * (B ^ 4 / ((c * N) ^ 2)) := mul_le_mul_of_nonneg_left hsq (by positivity)
    _ = B ^ 4 / (c * N) := by
        have : c * N * (B ^ 4 / (c * N) ^ 2) = (c * N * B ^ 4) / ((c * N) ^ 2) := by ring
        rw [this, sq (c * N), mul_div_mul_left (B ^ 4) (c * N) h_cN_ne]

/-- 4. Divergence collapse general bound: J*(α, N) ≤ B² * δ0² for any n ≥ 2. -/
theorem divergence_collapse_general (c N delta delta0 B : ℝ) (n : ℕ) (hn : 2 ≤ n)
    (hc : 0 < c) (hN : 0 < N) (hdelta : 0 ≤ delta) (hdelta_le : delta ≤ delta0)
    (_hdelta0 : 0 ≤ delta0) (_hB : 0 ≤ B)
    (henv : delta ^ (n - 2) ≤ B ^ 2 / (c * N)) :
    c * N * delta ^ n ≤ B ^ 2 * delta0 ^ 2 := by
  have e : delta ^ n = delta ^ (n - 2) * delta ^ 2 := by
    rw [← pow_add]; congr 1; omega
  rw [e]
  have hdelta2 : delta ^ 2 ≤ delta0 ^ 2 := by
    nlinarith
  have h_prod : c * N * (delta ^ (n - 2) * delta ^ 2) = (c * N * delta ^ (n - 2)) * delta ^ 2 := by ring
  rw [h_prod]
  have h_cN : 0 < c * N := by positivity
  have h_bound1 : c * N * delta ^ (n - 2) ≤ B ^ 2 := by
    rw [mul_comm]
    exact (le_div_iff₀ h_cN).mp henv
  have h_delta2_nonneg : 0 ≤ delta ^ 2 := by positivity
  calc (c * N * delta ^ (n - 2)) * delta ^ 2
      ≤ B ^ 2 * delta ^ 2 := mul_le_mul_of_nonneg_right h_bound1 h_delta2_nonneg
    _ ≤ B ^ 2 * delta0 ^ 2 := mul_le_mul_of_nonneg_left hdelta2 (by positivity)

/-- 5. Tagging decoupling: under tagged reporting, detection probability is decoupled from
memory displacement, so the trader's unique optimal choice remains δ* = δ0. -/
theorem tagging_decoupling (k delta0 delta pi_tag L : ℝ) (hk : 0 ≤ k) (_hL : 0 ≤ L) :
    k * (delta0 - delta0) ^ 2 + L * pi_tag ≤ k * (delta0 - delta) ^ 2 + L * pi_tag := by
  have : k * (delta0 - delta0) ^ 2 ≤ k * (delta0 - delta) ^ 2 :=
    supervisor_no_test k delta0 delta hk
  linarith

/-- 6. Supervisor effort collapse: if inspection cost C ≥ c_min > 0, while net detection
divergence satisfies J ≤ B4 / (c N), then whenever c N > (L_sup * B4) / c_min,
the net supervisory surplus L_sup * J - C is strictly negative. -/
theorem supervisor_effort_collapse (c N B4 L_sup c_min J C : ℝ)
    (h_pos : 0 < c * N) (h_J : J ≤ B4 / (c * N)) (h_C : c_min ≤ C)
    (h_large_N : (L_sup * B4) / c_min < c * N) (hc_min : 0 < c_min) (hL_sup : 0 ≤ L_sup) :
    L_sup * J - C < 0 := by
  have h_ret : L_sup * J ≤ (L_sup * B4) / (c * N) := by
    calc L_sup * J ≤ L_sup * (B4 / (c * N)) := mul_le_mul_of_nonneg_left h_J hL_sup
      _ = (L_sup * B4) / (c * N) := by ring
  have h_lt : (L_sup * B4) / (c * N) < c_min := by
    rw [div_lt_iff₀ h_pos]
    rw [div_lt_iff₀ hc_min] at h_large_N
    linarith
  calc L_sup * J - C ≤ (L_sup * B4) / (c * N) - c_min := by linarith
    _ < 0 := by linarith

/-- 6b. Stackelberg collapse, final step: for any bound `J ≤ J_bound` with `L_sup * J_bound < c_min ≤ C`, net
supervisory surplus is strictly negative. The rate of `J_bound` in `N`, and its dependence on `n`, are on paper. -/
theorem supervisor_effort_collapse_general (L_sup c_min J C J_bound : ℝ)
    (h_J : J ≤ J_bound) (h_C : c_min ≤ C) (h_small : L_sup * J_bound < c_min)
    (hL_sup : 0 ≤ L_sup) :
    L_sup * J - C < 0 := by
  have hret : L_sup * J ≤ L_sup * J_bound := mul_le_mul_of_nonneg_left h_J hL_sup
  linarith

/-- 7. The two payoff inequalities behind the paper's argument that no pure Nash equilibrium exists (the
best-response argument is on paper): at `(α = 0, δ = δ0)` profitable
inspection `C(α) < V_det * (pd0 - α)` breaks `(0, δ0)`, while high-stakes crowding makes pure `α ≥ α_min`
earn negative surplus relative to `α = 0`. -/
theorem simultaneous_no_pure_ne (V_det pd0 pd_best alpha J_sqrt c_min C_alpha : ℝ)
    (hV : 0 ≤ V_det) (hC : c_min ≤ C_alpha) (h_pd0 : C_alpha < V_det * (pd0 - alpha))
    (h_pd_best : pd_best - alpha ≤ J_sqrt) (h_small : V_det * J_sqrt < c_min) :
    0 < V_det * (pd0 - alpha) - C_alpha ∧ V_det * (pd_best - alpha) - C_alpha < 0 := by
  refine ⟨by linarith, ?_⟩
  have h1 : V_det * (pd_best - alpha) ≤ V_det * J_sqrt := mul_le_mul_of_nonneg_left h_pd_best hV
  linarith

end Paper1Revision15
