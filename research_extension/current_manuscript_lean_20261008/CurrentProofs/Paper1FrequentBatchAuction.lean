import Mathlib.Basic.Real.Basic
import Mathlib.Data.Finset.Basic
import Mathlib.Algebra.BigOperators.Group.Finset.Basic
import Mathlib.Tactic.Linarith
import Mathlib.Tactic.NormNum
import Mathlib.Tactic.Ring
import Mathlib.Tactic.Positivity

/-!
# Paper 1, Supplement Sections S6.1 & S8.1–S8.3: Frequent Batch Auctions, Quote Shading & APC Margins (`CurrentMM` mirror of `PublicationRevision17.lean`)
-/

open Finset BigOperators

namespace CurrentMM

def p1_cdaExecIocThenSweep (topCap uIoc uSweep : ℝ) : ℝ :=
  min uIoc topCap + uSweep

def p1_cdaExecSweepThenIoc (topCap uSweep uIoc : ℝ) : ℝ :=
  uSweep + min uIoc (max 0 (topCap - uSweep))

theorem p1_cda_fifo_noncommutative_witness :
    p1_cdaExecIocThenSweep 500 500 500 = 1000 ∧
    p1_cdaExecSweepThenIoc 500 500 500 = 500 ∧
    p1_cdaExecIocThenSweep 500 500 500 ≠ p1_cdaExecSweepThenIoc 500 500 500 := by
  unfold p1_cdaExecIocThenSweep p1_cdaExecSweepThenIoc
  have h1 : min (500 : ℝ) 500 = 500 := min_self 500
  have h2 : (500 : ℝ) - 500 = 0 := by ring
  have h3 : max (0 : ℝ) 0 = 0 := max_self 0
  have h4 : min (500 : ℝ) 0 = 0 := min_eq_right (by norm_num)
  refine ⟨?_, ?_, ?_⟩
  · linarith
  · rw [h2, h3, h4]; ring
  · rw [h1, h2, h3, h4]; norm_num

noncomputable def p1_batchSideFill (ui sideSum cap : ℝ) : ℝ :=
  if 0 < sideSum then ui * min sideSum cap / sideSum else 0

theorem p1_two_sided_cleared_volume_perm_invariant (buys buys' sells sells' : List ℝ) (Db Ds : ℝ)
    (hpb : buys.Perm buys') (hps : sells.Perm sells') :
    min (buys.sum + Db) (sells.sum + Ds) = min (buys'.sum + Db) (sells'.sum + Ds) := by
  rw [hpb.sum_eq, hps.sum_eq]

theorem p1_batch_two_sided_fill_perm_invariant (buys buys' : List ℝ) (ui cap : ℝ)
    (hperm : buys.Perm buys') (hui : 0 ≤ ui) (hcap : 0 ≤ cap) (hnonneg : ∀ b ∈ buys, 0 ≤ b) :
    p1_batchSideFill ui buys.sum cap = p1_batchSideFill ui buys'.sum cap ∧
    0 ≤ p1_batchSideFill ui buys.sum cap ∧
    (buys.sum ≤ cap → (0 < buys.sum → p1_batchSideFill ui buys.sum cap = ui) ∧
      (buys.sum = 0 → p1_batchSideFill ui buys.sum cap = 0)) := by
  have hsum_nn : 0 ≤ buys.sum := List.sum_nonneg hnonneg
  refine ⟨?_, ?_, ?_⟩
  · unfold p1_batchSideFill; rw [hperm.sum_eq]
  · unfold p1_batchSideFill
    split_ifs with hpos
    · have hm : 0 ≤ min buys.sum cap := le_min hsum_nn hcap
      positivity
    · exact le_rfl
  · intro hle
    constructor
    · intro hpos
      unfold p1_batchSideFill
      rw [ite_eq_left_iff.mpr (fun hn => absurd hpos hn), min_eq_left hle]
      exact mul_div_cancel_right₀ ui (ne_of_gt hpos)
    · intro hzero
      unfold p1_batchSideFill
      have hnot : ¬ (0 < buys.sum) := by linarith
      exact ite_eq_right_iff.mpr (fun hp => absurd hp hnot)

theorem p1_batch_order_split_linearity (u1 u2 sideSum cap : ℝ) :
    p1_batchSideFill (u1 + u2) sideSum cap =
      p1_batchSideFill u1 sideSum cap + p1_batchSideFill u2 sideSum cap := by
  unfold p1_batchSideFill
  split_ifs <;> ring

theorem p1_batch_kernel_convolution_eq (T : ℕ) (kA kB x : ℕ → ℝ)
    (hmatch : ∀ m, m < T → kA m = kB m) :
    ∑ m ∈ range T, kA m * x (T - 1 - m) = ∑ m ∈ range T, kB m * x (T - 1 - m) := by
  apply sum_congr rfl
  intro m hm
  rw [hmatch m (mem_range.mp hm)]

theorem p1_jittered_boundary_snipe_share (delta_lat W1 W2 : ℝ)
    (hd : 0 < delta_lat) (hle : delta_lat ≤ W1) (hW : W1 < W2) :
    0 ≤ delta_lat / W1 ∧ delta_lat / W1 ≤ 1 ∧ delta_lat / W2 < delta_lat / W1 := by
  have hW1 : 0 < W1 := lt_of_lt_of_le hd hle
  refine ⟨by positivity, (div_le_one hW1).mpr hle, div_lt_div_of_pos_left hd hW1 hW⟩

theorem p1_ho_stoll_joint_carry_reduction (abar lam0 kappa : ℝ)
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

theorem p1_apc_margin_buffer_bounds (m_var99 m_floor m_conc b_apc phi : ℝ)
    (hvar : m_var99 ≤ m_floor) (hconc : 0 ≤ m_conc) (hb : 0 ≤ b_apc)
    (hphi0 : 0 ≤ phi) (hphi1 : phi ≤ 1) :
    m_var99 ≤ m_floor + m_conc + b_apc * (1 - phi) ∧
    m_floor + m_conc + b_apc * (1 - phi) ≤ m_floor + m_conc + b_apc := by
  have h1 : 0 ≤ b_apc * (1 - phi) := mul_nonneg hb (by linarith)
  have h2 : b_apc * (1 - phi) ≤ b_apc * 1 := mul_le_mul_of_nonneg_left (by linarith) hb
  constructor <;> linarith

end CurrentMM
