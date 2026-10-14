import CurrentProofs.Accounts
import Mathlib.Algebra.BigOperators.Fin
import Mathlib.Data.Nat.Dist

namespace CurrentMM
noncomputable section
open scoped BigOperators

def baselineDisplacement {n : ℕ} (kernel : ℕ → ℝ) (trades : Fin n → ℝ)
    (i : Fin n) : ℝ := ∑ j, if j < i then kernel (i.val - j.val) * trades j else 0

def traderCashAfter {n : ℕ} (B P impact fee : ℝ) (kernel : ℕ → ℝ)
    (trades : Fin n → ℝ) : ℝ :=
  B - ∑ i, trades i * (P + baselineDisplacement kernel trades i + impact * trades i / 2)
    - fee * ∑ i, |trades i|

def quadraticExecutionCost {n : ℕ} (kernel : ℕ → ℝ) (trades : Fin n → ℝ) : ℝ :=
  (∑ i, ∑ j, trades i * trades j * kernel (Nat.dist i.val j.val)) / 2

theorem kernel_cost_entry_split {n : ℕ} (kernel : ℕ → ℝ) (trades : Fin n → ℝ)
    (i j : Fin n) :
    trades i * trades j * kernel (Nat.dist i.val j.val) =
      (if j < i then trades i * (kernel (i.val - j.val) * trades j) else 0) +
      (if i < j then trades j * (kernel (j.val - i.val) * trades i) else 0) +
      (if i = j then kernel 0 * trades i ^ 2 else 0) := by
  rcases lt_trichotomy i j with hij | heq | hji
  · have hn : i.val ≤ j.val := le_of_lt hij
    simp [hij, not_lt_of_ge (le_of_lt hij), ne_of_lt hij, Nat.dist_eq_sub_of_le hn]
    ring
  · subst j
    simp
    ring
  · have hn : j.val ≤ i.val := le_of_lt hji
    simp [hji, not_lt_of_ge (le_of_lt hji), ne_of_gt hji,
      Nat.dist_eq_sub_of_le_right hn]
    ring

theorem quadratic_execution_cost_triangular {n : ℕ} (kernel : ℕ → ℝ)
    (trades : Fin n → ℝ) :
    quadraticExecutionCost kernel trades =
      (∑ i, trades i * baselineDisplacement kernel trades i) +
        kernel 0 / 2 * ∑ i, trades i ^ 2 := by
  have hsplit : (∑ i, ∑ j, trades i * trades j * kernel (Nat.dist i.val j.val)) =
      (∑ i, ∑ j, if j < i then trades i * (kernel (i.val - j.val) * trades j) else 0) +
      (∑ i, ∑ j, if i < j then trades j * (kernel (j.val - i.val) * trades i) else 0) +
      ∑ i, kernel 0 * trades i ^ 2 := by
    simp_rw [kernel_cost_entry_split, Finset.sum_add_distrib]
    simp
  have hswap : (∑ i, ∑ j, if i < j then trades j *
        (kernel (j.val - i.val) * trades i) else 0) =
      (∑ i, ∑ j, if j < i then trades i *
        (kernel (i.val - j.val) * trades j) else 0) := by
    rw [Finset.sum_comm]
  have hbase : (∑ i, trades i * baselineDisplacement kernel trades i) =
      (∑ i, ∑ j, if j < i then trades i *
        (kernel (i.val - j.val) * trades j) else 0) := by
    simp [baselineDisplacement, Finset.mul_sum, mul_ite]
  unfold quadraticExecutionCost
  rw [hsplit, hswap, ← hbase, ← Finset.mul_sum]
  ring

theorem actual_trader_fundamental_equity {n : ℕ} (B P impact fee : ℝ)
    (kernel : ℕ → ℝ) (trades : Fin n → ℝ) (himpact : kernel 0 = impact) :
    equity (traderCashAfter B P impact fee kernel trades) (∑ i, trades i) P =
      B - quadraticExecutionCost kernel trades - fee * ∑ i, |trades i| := by
  rw [quadratic_execution_cost_triangular, himpact]
  unfold equity traderCashAfter
  have hsum : (∑ i, trades i *
        (P + baselineDisplacement kernel trades i + impact * trades i / 2)) =
      (∑ i, trades i) * P + (∑ i, trades i * baselineDisplacement kernel trades i) +
        impact / 2 * ∑ i, trades i ^ 2 := by
    simp_rw [mul_add, Finset.sum_add_distrib]
    rw [Finset.sum_mul]
    congr 1
    rw [Finset.mul_sum]
    apply Finset.sum_congr rfl
    intro i hi
    ring
  rw [hsum]
  ring

theorem solvent_trader_energy_bound (B cost fees energy spectralFloor : ℝ)
    (hsolvent : 0 ≤ B - cost - fees) (hfees : 0 ≤ fees)
    (hcoercive : spectralFloor / 2 * energy ≤ cost) (hm : 0 < spectralFloor) :
    energy ≤ 2 * B / spectralFloor := by
  apply (le_div_iff₀ hm).2
  nlinarith

/-- Theorem 2.9: Full No-Free-Identification bridge from binary KL requirement and spectral coercivity to minimum execution loss. -/
theorem no_free_identification_kl_to_execution_loss_bridge
    (loss_exec energy c_coer sigma_sq kl_req kl_obs dH_sup_sq : ℝ)
    (hcoer_pos : 0 < c_coer) (hsigma : 0 < sigma_sq) (hdH : 0 < dH_sup_sq)
    (hcoer : c_coer / 2 * energy ≤ loss_exec)
    (hdpi : kl_req ≤ kl_obs)
    (hkl_ub : kl_obs ≤ dH_sup_sq * energy / (2 * sigma_sq)) :
    c_coer * sigma_sq * kl_req / dH_sup_sq ≤ loss_exec := by
  have h1 : kl_req ≤ dH_sup_sq * energy / (2 * sigma_sq) := le_trans hdpi hkl_ub
  have h2sig : 0 < 2 * sigma_sq := by positivity
  have h2 : 2 * sigma_sq * kl_req ≤ energy * dH_sup_sq := by
    have h := (le_div_iff₀ h2sig).mp h1
    linarith
  have h3 : 2 * sigma_sq * kl_req / dH_sup_sq ≤ energy := (div_le_iff₀ hdH).mpr h2
  have h4 : (c_coer / 2) * (2 * sigma_sq * kl_req / dH_sup_sq) ≤ (c_coer / 2) * energy :=
    mul_le_mul_of_nonneg_left h3 (by positivity)
  have h5 : (c_coer / 2) * (2 * sigma_sq * kl_req / dH_sup_sq) =
      c_coer * sigma_sq * kl_req / dH_sup_sq := by
    field_simp [ne_of_gt hdH]
  linarith

end
end CurrentMM

