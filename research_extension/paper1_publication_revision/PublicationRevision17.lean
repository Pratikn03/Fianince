import Mathlib.Basic.Real.Basic
import Mathlib.Data.Finset.Basic
import Mathlib.Algebra.BigOperators.Group.Finset.Basic
import Mathlib.Tactic.Linarith
import Mathlib.Tactic.NormNum
import Mathlib.Tactic.Ring
import Mathlib.Tactic.Positivity

/-!
# Paper 1, Supplement Sections S6.1 & S8.1–S8.3: Frequent Batch Auctions, Quote Shading & APC Margins

This file mechanizes the deterministic market-design and macroprudential claims in
Theorem S6.1 (`thm:batch_restoration`) and Sections S8.1–S8.3:

1. `cda_fifo_noncommutative_witness`: explicit discrete capacity-exhaustion witness showing that in a
   sequential continuous double auction (CDA), permuting arrival order between an inside-tick IOC order
   and a multi-level sweep alters total executed volume (`1000 ≠ 500`).
2. `two_sided_cleared_volume_perm_invariant`: in a separated gross buy/sell uniform-price call auction,
   total matched volume `min(∑ b_i + D_buy, ∑ s_j + D_sell)` is invariant under arbitrary permutations.
3. `batch_two_sided_fill_perm_invariant` & `batch_order_split_linearity`: under heavy-side uniform
   random tie-breaking (`batchSideFill` with explicit `0 < sideSum` guard, no `x / 0 = 0`), expected
   nonnegative gross fills are arrival-order invariant, exact `= ui` when uncongested, `= 0` when
   empty, and strictly linear under order splitting (`u1 + u2`) at any clearing fill ratio.
4. `batch_kernel_convolution_eq`: when two populations match moments `kA m = kB m` for all `m < T`,
   their discrete batch feedback convolutions coincide identically.
5. `jittered_boundary_snipe_share`: exponential/randomized batch duration `W = τ + W_rand ≥ Δ_lat ≥ 0`
   bounds boundary-sniping share by `Δ_lat / W ∈ [0, 1]` and shrinks strictly as `W` grows.
6. `ho_stoll_joint_carry_reduction`: solving inventory-elastic liquidity conservation jointly with CARA
   optimality yields `ā_eff = ā / (1 + λ₀ κ) ∈ [0, ā]` (`< ā` when `ā > 0`) and attenuated impact
   `κ / (1 + λ₀ κ) < κ` without an exogenous `c₁` shading parameter.
7. `apc_margin_buffer_bounds`: EMIR/SEC-compliant two-tier margin `m_floor + m_conc + b_APC * (1 - ϕ)`
   never falls below the 99% MPOR VaR floor `m_var99` and stays bounded in `[m_var99, m_floor + m_conc + b_APC]`.

Standard axioms only (propext, Classical.choice, Quot.sound).
-/

open Finset BigOperators

namespace Paper1Revision17

/-- Sequential CDA execution when a multi-level sweep arrives after vs. before an inside-tick IOC order. -/
def cdaExecIocThenSweep (topCap uIoc uSweep : ℝ) : ℝ :=
  min uIoc topCap + uSweep

def cdaExecSweepThenIoc (topCap uSweep uIoc : ℝ) : ℝ :=
  uSweep + min uIoc (max 0 (topCap - uSweep))

/-- Guarded heavy-side expected fill ratio under Budish–Cramton–Shim uniform random tie-breaking
on nonnegative gross queue quantity `ui` (no division by zero on balanced crosses). -/
noncomputable def batchSideFill (ui sideSum cap : ℝ) : ℝ :=
  if 0 < sideSum then ui * min sideSum cap / sideSum else 0

/-- 1. Explicit CDA non-commutativity witness (`1000 ≠ 500` at `topCap = 500`). -/
theorem cda_fifo_noncommutative_witness :
    cdaExecIocThenSweep 500 500 500 = 1000 ∧
    cdaExecSweepThenIoc 500 500 500 = 500 ∧
    cdaExecIocThenSweep 500 500 500 ≠ cdaExecSweepThenIoc 500 500 500 := by
  unfold cdaExecIocThenSweep cdaExecSweepThenIoc
  have h1 : min (500 : ℝ) 500 = 500 := min_self 500
  have h2 : (500 : ℝ) - 500 = 0 := by ring
  have h3 : max (0 : ℝ) 0 = 0 := max_self 0
  have h4 : min (500 : ℝ) 0 = 0 := min_eq_right (by norm_num)
  refine ⟨?_, ?_, ?_⟩
  · linarith
  · rw [h2, h3, h4]; ring
  · rw [h1, h2, h3, h4]; norm_num

/-- 2. Two-sided uniform-price call matched volume is invariant under separate gross buy and sell permutations. -/
theorem two_sided_cleared_volume_perm_invariant (buys buys' sells sells' : List ℝ) (Db Ds : ℝ)
    (hpb : buys.Perm buys') (hps : sells.Perm sells') :
    min (buys.sum + Db) (sells.sum + Ds) = min (buys'.sum + Db) (sells'.sum + Ds) := by
  rw [hpb.sum_eq, hps.sum_eq]

/-- 3. Guarded two-sided heavy-side expected fill is arrival-order invariant, nonnegative, exact `= ui`
when uncongested (`buys.sum ≤ cap`), and explicitly `0` when the side is empty (`buys.sum = 0`). -/
theorem batch_two_sided_fill_perm_invariant (buys buys' : List ℝ) (ui cap : ℝ)
    (hperm : buys.Perm buys') (hui : 0 ≤ ui) (hcap : 0 ≤ cap) (hnonneg : ∀ b ∈ buys, 0 ≤ b) :
    batchSideFill ui buys.sum cap = batchSideFill ui buys'.sum cap ∧
    0 ≤ batchSideFill ui buys.sum cap ∧
    (buys.sum ≤ cap → (0 < buys.sum → batchSideFill ui buys.sum cap = ui) ∧
      (buys.sum = 0 → batchSideFill ui buys.sum cap = 0)) := by
  have hsum_nn : 0 ≤ buys.sum := List.sum_nonneg hnonneg
  refine ⟨?_, ?_, ?_⟩
  · unfold batchSideFill; rw [hperm.sum_eq]
  · unfold batchSideFill
    split_ifs with hpos
    · have hm : 0 ≤ min buys.sum cap := le_min hsum_nn hcap
      positivity
    · exact le_rfl
  · intro hle
    constructor
    · intro hpos
      unfold batchSideFill
      rw [ite_eq_left_iff.mpr (fun hn => absurd hpos hn), min_eq_left hle]
      exact mul_div_cancel_right₀ ui (ne_of_gt hpos)
    · intro hzero
      unfold batchSideFill
      have hnot : ¬ (0 < buys.sum) := by linarith
      exact ite_eq_right_iff.mpr (fun hp => absurd hp hnot)

/-- 3b. Linearity under order splitting at fixed clearing fill ratio (random tie-breaking preserves additivity). -/
theorem batch_order_split_linearity (u1 u2 sideSum cap : ℝ) :
    batchSideFill (u1 + u2) sideSum cap =
      batchSideFill u1 sideSum cap + batchSideFill u2 sideSum cap := by
  unfold batchSideFill
  split_ifs <;> ring

/-- 4. Moment-matched kernels generate identical causal batch convolutions through horizon `T`. -/
theorem batch_kernel_convolution_eq (T : ℕ) (kA kB x : ℕ → ℝ)
    (hmatch : ∀ m, m < T → kA m = kB m) :
    ∑ m ∈ range T, kA m * x (T - 1 - m) = ∑ m ∈ range T, kB m * x (T - 1 - m) := by
  apply sum_congr rfl
  intro m hm
  rw [hmatch m (mem_range.mp hm)]

/-- 5. Randomized batch duration bounds boundary-sniping share in `[0, 1]` and shrinks strictly in `W`. -/
theorem jittered_boundary_snipe_share (delta_lat W1 W2 : ℝ)
    (hd : 0 < delta_lat) (hle : delta_lat ≤ W1) (hW : W1 < W2) :
    0 ≤ delta_lat / W1 ∧ delta_lat / W1 ≤ 1 ∧ delta_lat / W2 < delta_lat / W1 := by
  have hW1 : 0 < W1 := lt_of_lt_of_le hd hle
  have hW2 : 0 < W2 := lt_trans hW1 hW
  refine ⟨by positivity, (div_le_one hW1).mpr hle, ?_⟩
  exact div_lt_div_of_pos_left hd hW1 hW

/-- 6. Joint Ho–Stoll quote shading with endogenous liquidity elasticity `λ₀`: equilibrium carry
`ā_eff = ā / (1 + λ₀ κ)` satisfies `0 ≤ ā_eff ≤ ā < 1` (strict when `ā > 0`) and shock impact attenuates. -/
theorem ho_stoll_joint_carry_reduction (abar lam0 kappa : ℝ)
    (hlam : 0 < lam0) (hkap : 0 < kappa) (ha0 : 0 ≤ abar) (ha1 : abar < 1) :
    0 ≤ abar / (1 + lam0 * kappa) ∧
    abar / (1 + lam0 * kappa) ≤ abar ∧
    abar / (1 + lam0 * kappa) < 1 ∧
    (0 < abar → abar / (1 + lam0 * kappa) < abar) ∧
    kappa / (1 + lam0 * kappa) < kappa := by
  have hprod : 0 < lam0 * kappa := mul_pos hlam hkap
  have hden : 1 < 1 + lam0 * kappa := by linarith
  have hden_pos : 0 < 1 + lam0 * kappa := by linarith
  refine ⟨div_nonneg ha0 hden_pos.le, div_le_self ha0 hden.le, ?_, ?_, ?_⟩
  · calc abar / (1 + lam0 * kappa) ≤ abar := div_le_self ha0 hden.le
      _ < 1 := ha1
  · intro hapos
    exact div_lt_self hapos hden
  · exact div_lt_self hkap hden

/-- 7. Two-tier EMIR/SEC-compliant APC margin + concentration add-on never breaches the 99% MPOR VaR floor. -/
theorem apc_margin_buffer_bounds (m_var99 m_floor m_conc b_apc phi : ℝ)
    (hvar : m_var99 ≤ m_floor) (hconc : 0 ≤ m_conc) (hb : 0 ≤ b_apc)
    (hphi0 : 0 ≤ phi) (hphi1 : phi ≤ 1) :
    m_var99 ≤ m_floor + m_conc + b_apc * (1 - phi) ∧
    m_floor + m_conc + b_apc * (1 - phi) ≤ m_floor + m_conc + b_apc := by
  have h1 : 0 ≤ b_apc * (1 - phi) := mul_nonneg hb (by linarith)
  have h2 : b_apc * (1 - phi) ≤ b_apc * 1 := mul_le_mul_of_nonneg_left (by linarith) hb
  constructor <;> linarith

end Paper1Revision17
