import Mathlib.Basic.Real.Basic
import Mathlib.Analysis.Real.Sqrt
import Mathlib.Tactic.Linarith
import Mathlib.Tactic.Ring
import Mathlib.Tactic.Positivity

/-!
# Paper 1, Section 7.3: Endogenizing the Supervisor in the Surveillance Paradox (`CurrentMM` mirror of `PublicationRevision15.lean`)
-/

namespace CurrentMM

theorem p1_supervisor_no_test (k delta0 delta : ℝ) (hk : 0 ≤ k) :
    k * (delta0 - delta0) ^ 2 ≤ k * (delta0 - delta) ^ 2 := by
  have : k * (delta0 - delta0) ^ 2 = 0 := by ring
  rw [this]
  positivity

theorem p1_supervisor_no_test_unique (k delta0 delta : ℝ) (hk : 0 < k)
    (h_eq : k * (delta0 - delta) ^ 2 = k * (delta0 - delta0) ^ 2) : delta = delta0 := by
  have h0 : k * (delta0 - delta0) ^ 2 = 0 := by ring
  rw [h0] at h_eq
  have hsq : (delta0 - delta) ^ 2 = 0 := by nlinarith [h_eq]
  have : delta0 - delta = 0 := sq_eq_zero_iff.mp hsq
  linarith

theorem p1_trader_crowding_envelope (L beta c N k delta0 delta : ℝ) (n : ℕ) (hn : 2 ≤ n)
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

theorem p1_high_stakes_regime_gap (L alpha k delta0 : ℝ)
    (hhigh : k * delta0 ^ 2 < L * (1 - alpha)) :
    k * delta0 ^ 2 + L * alpha < L := by
  linarith

theorem p1_low_stakes_regime_dominance (L alpha k delta0 : ℝ)
    (hlow : L * (1 - alpha) < k * delta0 ^ 2) :
    L < k * delta0 ^ 2 + L * alpha := by
  linarith

theorem p1_composite_glrt_envelope (L c2 c N k delta0 delta : ℝ) (n : ℕ) (hn : 2 ≤ n)
    (hL : 0 < L) (hc2 : 0 < c2) (hc : 0 < c) (hN : 0 < N)
    (h : (n : ℝ) * L * c2 * c * N * delta ^ (n - 1) ≤ 2 * k * delta0) :
    delta ^ (n - 1) ≤ (2 * k * delta0 / ((n : ℝ) * L * c2)) / (c * N) := by
  have hn_pos : (0 : ℝ) < (n : ℝ) := by
    exact_mod_cast Nat.lt_of_lt_of_le (by norm_num) hn
  have hden : 0 < ((n : ℝ) * L * c2) * (c * N) := by positivity
  rw [div_div, le_div_iff₀ hden]
  linarith

theorem p1_divergence_collapse_n4 (c N delta B : ℝ) (hc : 0 < c) (hN : 0 < N) (_hdelta : 0 ≤ delta)
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

theorem p1_divergence_collapse_general (c N delta delta0 B : ℝ) (n : ℕ) (hn : 2 ≤ n)
    (hc : 0 < c) (hN : 0 < N) (hdelta : 0 ≤ delta) (hdelta_le : delta ≤ delta0)
    (_hdelta0 : 0 ≤ delta0) (_hB : 0 ≤ B)
    (henv : delta ^ (n - 2) ≤ B ^ 2 / (c * N)) :
    c * N * delta ^ n ≤ B ^ 2 * delta0 ^ 2 := by
  have e : delta ^ n = delta ^ (n - 2) * delta ^ 2 := by
    rw [← pow_add]; congr 1; omega
  rw [e]
  have hdelta2 : delta ^ 2 ≤ delta0 ^ 2 := by nlinarith
  have h_prod : c * N * (delta ^ (n - 2) * delta ^ 2) = (c * N * delta ^ (n - 2)) * delta ^ 2 := by ring
  rw [h_prod]
  have h_cN : 0 < c * N := by positivity
  have h_bound1 : c * N * delta ^ (n - 2) ≤ B ^ 2 := by
    rw [mul_comm]
    exact (le_div_iff₀ h_cN).mp henv
  calc (c * N * delta ^ (n - 2)) * delta ^ 2
      ≤ B ^ 2 * delta ^ 2 := mul_le_mul_of_nonneg_right h_bound1 (by positivity)
    _ ≤ B ^ 2 * delta0 ^ 2 := mul_le_mul_of_nonneg_left hdelta2 (by positivity)

theorem p1_tagging_decoupling (k delta0 delta pi_tag L : ℝ) (hk : 0 ≤ k) (_hL : 0 ≤ L) :
    k * (delta0 - delta0) ^ 2 + L * pi_tag ≤ k * (delta0 - delta) ^ 2 + L * pi_tag := by
  have : k * (delta0 - delta0) ^ 2 ≤ k * (delta0 - delta) ^ 2 :=
    p1_supervisor_no_test k delta0 delta hk
  linarith

theorem p1_supervisor_effort_collapse (c N B4 L_sup c_min J C : ℝ)
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
  linarith

/-- Stackelberg collapse, final step: for any bound `J ≤ J_bound` with `L_sup * J_bound < c_min ≤ C`, net
supervisory surplus is strictly negative. The rate of `J_bound` in `N`, and its dependence on `n`, are on paper. -/
theorem p1_supervisor_effort_collapse_general (L_sup c_min J C J_bound : ℝ)
    (h_J : J ≤ J_bound) (h_C : c_min ≤ C) (h_small : L_sup * J_bound < c_min)
    (hL_sup : 0 ≤ L_sup) :
    L_sup * J - C < 0 := by
  have hret : L_sup * J ≤ L_sup * J_bound := mul_le_mul_of_nonneg_left h_J hL_sup
  linarith

/-- The two payoff inequalities behind the paper's argument that no pure Nash equilibrium exists; the
best-response argument is on paper. -/
theorem p1_simultaneous_no_pure_ne (V_det pd0 pd_best alpha J_sqrt c_min C_alpha : ℝ)
    (hV : 0 ≤ V_det) (hC : c_min ≤ C_alpha) (h_pd0 : C_alpha < V_det * (pd0 - alpha))
    (h_pd_best : pd_best - alpha ≤ J_sqrt) (h_small : V_det * J_sqrt < c_min) :
    0 < V_det * (pd0 - alpha) - C_alpha ∧ V_det * (pd_best - alpha) - C_alpha < 0 := by
  refine ⟨by linarith, ?_⟩
  have h1 : V_det * (pd_best - alpha) ≤ V_det * J_sqrt := mul_le_mul_of_nonneg_left h_pd_best hV
  linarith

end CurrentMM
