import Mathlib.Algebra.Polynomial.Monic
import Mathlib.Algebra.Polynomial.BigOperators
import Mathlib.Algebra.Polynomial.Degree.Lemmas
import Mathlib.Basic.Real.Basic
import Mathlib.Tactic.Linarith
import Mathlib.Tactic.FieldSimp

/-!
# Paper 1, Theorem `thm:merged` (i): the pole count

With `K` distinct memory rates `r_i ≠ 0` and nonzero merged weights `w_i`, the paper's transfer function
`H(z) = κ z D(z) / ((z - a) D(z) - κ N(z))`, `D = ∏ (z - r_i)`, `N = ∑_i w_i z ∏_{j ≠ i} (z - r_j)`, is already in
lowest terms when `a ≠ 0` and `κ ≠ 0`: numerator and denominator have no common root, and the denominator is monic of
degree `K + 1`. So the price response has exactly `1 + K` poles, one per distinct memory rate plus the price's own.
(That a SISO transfer function in lowest terms with denominator degree `n` has minimal state dimension `n` is
classical realization theory and is not formalized here.)
-/

namespace CurrentMM

open Polynomial Finset

noncomputable def tfDen {K : ℕ} (r : Fin K → ℝ) : ℝ[X] := ∏ i, (X - C (r i))

noncomputable def tfNum {K : ℕ} (w r : Fin K → ℝ) : ℝ[X] :=
  ∑ i, C (w i) * X * ∏ j ∈ univ.erase i, (X - C (r j))

/-- Numerator of `H`: `κ z D(z)`. -/
noncomputable def tfTop {K : ℕ} (κ : ℝ) (r : Fin K → ℝ) : ℝ[X] := C κ * X * tfDen r

/-- Denominator of `H`: `(z - a) D(z) - κ N(z)`. -/
noncomputable def tfBottom {K : ℕ} (a κ : ℝ) (w r : Fin K → ℝ) : ℝ[X] :=
  (X - C a) * tfDen r - C κ * tfNum w r

theorem p1_tfDen_monic {K : ℕ} (r : Fin K → ℝ) : (tfDen r).Monic :=
  monic_prod_of_monic _ _ (fun i _ => monic_X_sub_C (r i))

theorem p1_tfDen_natDegree {K : ℕ} (r : Fin K → ℝ) : (tfDen r).natDegree = K := by
  unfold tfDen
  rw [natDegree_prod_of_monic _ _ (fun i _ => monic_X_sub_C (r i))]
  simp

theorem p1_tfNum_degree_le {K : ℕ} (w r : Fin K → ℝ) : (tfNum w r).natDegree ≤ K := by
  unfold tfNum
  refine natDegree_sum_le_of_forall_le _ _ (fun i _ => ?_)
  calc (C (w i) * X * ∏ j ∈ univ.erase i, (X - C (r j))).natDegree
      ≤ (C (w i) * X).natDegree + (∏ j ∈ univ.erase i, (X - C (r j))).natDegree := natDegree_mul_le
    _ ≤ 1 + (K - 1) := by
        gcongr
        · exact le_trans natDegree_mul_le (by simp)
        · rw [natDegree_prod_of_monic _ _ (fun j _ => monic_X_sub_C (r j))]
          simp [card_erase_of_mem (mem_univ i)]
    _ ≤ K := by
        have : 0 < K := Fin.pos i
        omega

/-- The denominator is monic of degree `K + 1`. -/
theorem p1_tfBottom_monic_natDegree {K : ℕ} (a κ : ℝ) (w r : Fin K → ℝ) :
    (tfBottom a κ w r).Monic ∧ (tfBottom a κ w r).natDegree = K + 1 := by
  have hm : ((X - C a) * tfDen r).Monic := (monic_X_sub_C a).mul (p1_tfDen_monic r)
  have hd : ((X - C a) * tfDen r).natDegree = K + 1 := by
    rw [(monic_X_sub_C a).natDegree_mul (p1_tfDen_monic r), natDegree_X_sub_C, p1_tfDen_natDegree]; ring
  have hlt : (C κ * tfNum w r).degree < ((X - C a) * tfDen r).degree := by
    rw [degree_eq_natDegree hm.ne_zero, hd]
    calc (C κ * tfNum w r).degree ≤ ((C κ * tfNum w r).natDegree : WithBot ℕ) := degree_le_natDegree
      _ ≤ (K : WithBot ℕ) := by
          exact_mod_cast le_trans natDegree_mul_le (by simp [p1_tfNum_degree_le w r])
      _ < ((K + 1 : ℕ) : WithBot ℕ) := by exact_mod_cast Nat.lt_succ_self K
  refine ⟨hm.sub_of_left hlt, ?_⟩
  unfold tfBottom
  rw [natDegree_sub_eq_left_of_natDegree_lt, hd]
  rw [hd]
  calc (C κ * tfNum w r).natDegree ≤ (tfNum w r).natDegree := natDegree_C_mul_le _ _
    _ ≤ K := p1_tfNum_degree_le w r
    _ < K + 1 := Nat.lt_succ_self K

theorem p1_tfDen_eval_self {K : ℕ} (r : Fin K → ℝ) (k : Fin K) : (tfDen r).eval (r k) = 0 := by
  unfold tfDen
  rw [eval_prod]
  exact prod_eq_zero (mem_univ k) (by simp)

theorem p1_tfNum_eval_self {K : ℕ} (w r : Fin K → ℝ) (k : Fin K) :
    (tfNum w r).eval (r k) = w k * r k * ∏ j ∈ univ.erase k, (r k - r j) := by
  unfold tfNum
  rw [eval_finsetSum, sum_eq_single k]
  · simp [eval_prod]
  · intro i _ hik
    simp only [eval_mul, eval_C, eval_X, eval_prod, eval_sub]
    have : ∏ j ∈ univ.erase i, (r k - r j) = 0 :=
      prod_eq_zero (mem_erase.mpr ⟨Ne.symm hik, mem_univ k⟩) (sub_self _)
    rw [this, mul_zero]
  · intro h; exact absurd (mem_univ k) h

/-- **Pole count of `thm:merged` (i).** With distinct nonzero rates, nonzero weights, `a ≠ 0` and `κ ≠ 0`, the
numerator and denominator of `H` have no common root; the denominator is monic of degree `K + 1`. -/
theorem p1_thm_merged_pole_count {K : ℕ} (a κ : ℝ) (w r : Fin K → ℝ) (ha : a ≠ 0) (hκ : κ ≠ 0)
    (hr : Function.Injective r) (hr0 : ∀ i, r i ≠ 0) (hw : ∀ i, w i ≠ 0) :
    (∀ z : ℝ, (tfTop κ r).eval z = 0 → (tfBottom a κ w r).eval z ≠ 0) ∧
      (tfBottom a κ w r).Monic ∧ (tfBottom a κ w r).natDegree = K + 1 := by
  refine ⟨fun z hz => ?_, p1_tfBottom_monic_natDegree a κ w r⟩
  unfold tfTop at hz
  simp only [eval_mul, eval_C, eval_X] at hz
  rcases mul_eq_zero.mp hz with h1 | h1
  · -- `κ z = 0`, so `z = 0`
    have hz0 : z = 0 := by
      rcases mul_eq_zero.mp h1 with h | h
      · exact absurd h hκ
      · exact h
    subst hz0
    unfold tfBottom
    have hN0 : (tfNum w r).eval 0 = 0 := by
      unfold tfNum; simp [eval_finsetSum]
    simp only [eval_sub, eval_mul, eval_X, eval_C, hN0, mul_zero, sub_zero, zero_sub]
    have hD0 : (tfDen r).eval 0 ≠ 0 := by
      unfold tfDen
      rw [eval_prod]
      exact prod_ne_zero_iff.mpr (fun i _ => by simp [hr0 i])
    exact mul_ne_zero (neg_ne_zero.mpr ha) hD0
  · -- `D(z) = 0`, so `z = r k` for some `k`
    unfold tfDen at h1
    rw [eval_prod] at h1
    obtain ⟨k, _, hk⟩ := prod_eq_zero_iff.mp h1
    have hzk : z = r k := by simpa [sub_eq_zero] using hk
    subst hzk
    unfold tfBottom
    simp only [eval_sub, eval_mul, eval_C, p1_tfDen_eval_self, mul_zero, zero_sub,
      p1_tfNum_eval_self]
    have hprod : ∏ j ∈ univ.erase k, (r k - r j) ≠ 0 :=
      prod_ne_zero_iff.mpr (fun j hj => sub_ne_zero.mpr (fun h => (mem_erase.mp hj).1 (hr h).symm))
    exact neg_ne_zero.mpr (mul_ne_zero hκ (mul_ne_zero (mul_ne_zero (hw k) (hr0 k)) hprod))

end CurrentMM
