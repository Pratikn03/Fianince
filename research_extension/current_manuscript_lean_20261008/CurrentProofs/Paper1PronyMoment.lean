import CurrentProofs.Paper1FiniteIdentification
import Mathlib.Analysis.Calculus.ContDiff.Operations
import Mathlib.Analysis.Calculus.Deriv.Pow
import Mathlib.Analysis.Calculus.Deriv.Prod
import Mathlib.Algebra.Polynomial.Derivative
import Mathlib.Algebra.Polynomial.BigOperators
import Mathlib.LinearAlgebra.Vandermonde
import Mathlib.LinearAlgebra.Matrix.NonsingularInverse

/-!
# Paper 1, Theorem 5.4: the moment map of a `K`-atom measure

The algebraic facts behind the Prony step of `prop:esprit`:
* `momentMap K`: nodes and weights `(s, ω)` ↦ the first `2K` power moments `∑ ω_i s_i^m`;
* `p1_momentMap_fderiv_apply`: its derivative, computed;
* `p1_hermite_functional`: if `∑_i (d_i s_i^m + ω_i u_i m s_i^{m-1}) = 0` for all `m < 2K`, distinct nodes and
  nonzero weights force `u = d = 0` (Hermite interpolation; no determinant formula needed);
* `p1_momentMap_fderiv_injective`: hence the Jacobian is injective at every point with distinct nodes and nonzero
  weights (the confluent-Vandermonde step);
* `p1_ordered_representation_unique`: two representations with increasing nodes and nonzero weights and equal
  moments coincide (from the finite identification theorem);
* `p1_prony_hankel_det_ne_zero`, `p1_prony_polynomial`: the Hankel matrix of the moments is nonsingular and the
  unique solution of Prony's linear system is the coefficient vector of `∏ (X - s_i)`, so Prony's method returns
  exactly the nodes, which are real and distinct.
-/

namespace CurrentMM

open Finset Polynomial

/-- Nodes and weights of a `K`-atom measure. -/
abbrev PronyParam (K : ℕ) := (Fin K → ℝ) × (Fin K → ℝ)

/-- The first `2K` power moments of the measure with nodes `x.1` and weights `x.2`. -/
def momentMap (K : ℕ) (x : PronyParam K) : Fin (2 * K) → ℝ :=
  fun m => ∑ i, x.2 i * x.1 i ^ (m : ℕ)

theorem p1_momentMap_contDiff (K : ℕ) : ContDiff ℝ 1 (momentMap K) := by
  refine contDiff_pi.2 fun m => ?_
  show ContDiff ℝ 1 (fun x : PronyParam K => ∑ i, x.2 i * x.1 i ^ (m : ℕ))
  refine ContDiff.sum fun i _ => ?_
  exact ((contDiff_apply ℝ ℝ i).comp contDiff_snd).mul
    (((contDiff_apply ℝ ℝ i).comp contDiff_fst).pow _)

/-- The derivative of the moment map. -/
theorem p1_momentMap_fderiv_apply (K : ℕ) (x v : PronyParam K) (m : Fin (2 * K)) :
    fderiv ℝ (momentMap K) x v m =
      ∑ i, (v.2 i * x.1 i ^ (m : ℕ) + x.2 i * ((m : ℕ) * x.1 i ^ ((m : ℕ) - 1)) * v.1 i) := by
  have hd : DifferentiableAt ℝ (momentMap K) x :=
    (p1_momentMap_contDiff K).differentiable one_ne_zero x
  have hline : HasDerivAt (fun t : ℝ => x + t • v) v 0 := by
    simpa using ((hasDerivAt_id (0 : ℝ)).smul_const v).const_add x
  have hl : HasFDerivAt (momentMap K) (fderiv ℝ (momentMap K) x) (x + (0 : ℝ) • v) := by
    rw [zero_smul, add_zero]; exact hd.hasFDerivAt
  have h1 : HasDerivAt (fun t : ℝ => momentMap K (x + t • v)) (fderiv ℝ (momentMap K) x v) 0 :=
    HasFDerivAt.comp_hasDerivAt (l := momentMap K) (0 : ℝ) hl hline
  have h2 : HasDerivAt (fun t : ℝ => momentMap K (x + t • v) m)
      (∑ i, (v.2 i * x.1 i ^ (m : ℕ) + x.2 i * ((m : ℕ) * x.1 i ^ ((m : ℕ) - 1)) * v.1 i)) 0 := by
    have hfun : (fun t : ℝ => momentMap K (x + t • v) m) =
        fun t => ∑ i, (x.2 i + t * v.2 i) * (x.1 i + t * v.1 i) ^ (m : ℕ) := by
      funext t; simp [momentMap, smul_eq_mul]
    rw [hfun]
    refine HasDerivAt.fun_sum fun i _ => ?_
    have ha : HasDerivAt (fun t : ℝ => x.2 i + t * v.2 i) (v.2 i) 0 := by
      simpa using ((hasDerivAt_id (0 : ℝ)).mul_const (v.2 i)).const_add (x.2 i)
    have hb : HasDerivAt (fun t : ℝ => x.1 i + t * v.1 i) (v.1 i) 0 := by
      simpa using ((hasDerivAt_id (0 : ℝ)).mul_const (v.1 i)).const_add (x.1 i)
    convert ha.mul (hb.pow (m : ℕ)) using 1
    simp; ring
  exact (hasDerivAt_pi.mp h1 m).unique h2

/-- `(X - a)² r` vanishes to second order at `a`. -/
theorem p1_double_root (a : ℝ) (r : ℝ[X]) :
    ((X - C a) ^ 2 * r).eval a = 0 ∧ (derivative ((X - C a) ^ 2 * r)).eval a = 0 := by
  constructor
  · simp
  · simp [derivative_mul, derivative_pow]

/-- **Hermite step.** If the functional `p ↦ ∑_i (d_i p(s_i) + ω_i u_i p'(s_i))` kills every monomial of degree
below `2K`, distinct nodes and nonzero weights force `u = 0` and `d = 0`. -/
theorem p1_hermite_functional {K : ℕ} (s ω u d : Fin K → ℝ) (hs : Function.Injective s)
    (hw : ∀ i, ω i ≠ 0)
    (h : ∀ m : ℕ, m < 2 * K → ∑ i, (d i * s i ^ m + ω i * ((m : ℝ) * s i ^ (m - 1)) * u i) = 0) :
    u = 0 ∧ d = 0 := by
  classical
  set Λ : ℝ[X] → ℝ := fun p => ∑ i, (d i * p.eval (s i) + ω i * u i * (derivative p).eval (s i)) with hΛdef
  set T : ℕ → ℝ := fun m => ∑ i, (d i * s i ^ m + ω i * ((m : ℝ) * s i ^ (m - 1)) * u i) with hTdef
  have hgen : ∀ (n : ℕ) (c : ℕ → ℝ), Λ (∑ m ∈ range n, C (c m) * X ^ m) = ∑ m ∈ range n, c m * T m := by
    intro n c
    simp only [hΛdef, hTdef, eval_finsetSum, derivative_sum, derivative_C_mul_X_pow, eval_C_mul, eval_pow,
      eval_X, mul_sum, ← sum_add_distrib]
    rw [sum_comm]
    refine sum_congr rfl (fun m _ => sum_congr rfl (fun i _ => by ring))
  have hΛ : ∀ p : ℝ[X], p.natDegree < 2 * K → Λ p = 0 := by
    intro p hp
    have e := hgen (p.natDegree + 1) p.coeff
    rw [← p.as_sum_range_C_mul_X_pow] at e
    rw [e]
    refine sum_eq_zero (fun m hm => ?_)
    rw [show T m = 0 from h m (by have := mem_range.mp hm; omega), mul_zero]
  -- the polynomials `q_i = ∏_{j ≠ i} (X - s_j)^2` and `p_i = (X - s_i) q_i`
  set q : Fin K → ℝ[X] := fun i => ∏ j ∈ univ.erase i, (X - C (s j)) ^ 2 with hqdef
  have hq_eval_ne : ∀ i, (q i).eval (s i) ≠ 0 := by
    intro i
    simp only [hqdef, eval_prod, eval_pow, eval_sub, eval_X, eval_C]
    refine prod_ne_zero_iff.mpr (fun j hj => pow_ne_zero _ (sub_ne_zero.mpr ?_))
    intro hij; exact (mem_erase.mp hj).1 (hs hij).symm
  have hq_split : ∀ i j, j ≠ i → ∃ r : ℝ[X], q i = (X - C (s j)) ^ 2 * r := by
    intro i j hji
    exact ⟨_, (mul_prod_erase (univ.erase i) (fun k => (X - C (s k)) ^ 2)
      (mem_erase.mpr ⟨hji, mem_univ j⟩)).symm⟩
  have hq_deg : ∀ i, (q i).natDegree ≤ 2 * (K - 1) := by
    intro i
    refine (natDegree_prod_le _ _).trans ?_
    calc ∑ j ∈ univ.erase i, ((X - C (s j)) ^ 2).natDegree ≤ ∑ j ∈ univ.erase i, 2 := by
          refine sum_le_sum (fun j _ => ?_)
          refine (natDegree_pow_le).trans ?_
          rw [natDegree_X_sub_C]
      _ = 2 * (K - 1) := by
          rw [sum_const, card_erase_of_mem (mem_univ i), card_univ, Fintype.card_fin, smul_eq_mul, mul_comm]
  have hK : ∀ i : Fin K, 1 ≤ K := fun i => by have := i.isLt; omega
  -- step 1: `u = 0`
  have hu : ∀ i, u i = 0 := by
    intro i
    have hdeg : ((X - C (s i)) * q i).natDegree < 2 * K := by
      refine (natDegree_mul_le).trans_lt ?_
      rw [natDegree_X_sub_C]
      have := hq_deg i; have := hK i; omega
    have h0 := hΛ _ hdeg
    have hval : Λ ((X - C (s i)) * q i) = ω i * u i * (q i).eval (s i) := by
      simp only [hΛdef]
      rw [sum_eq_single i]
      · simp [derivative_mul]
      · intro j _ hji
        obtain ⟨r, hr⟩ := hq_split i j hji
        have ⟨e0, e1⟩ := p1_double_root (s j) r
        rw [hr]
        simp only [derivative_mul, eval_mul, eval_add, eval_sub, eval_X, eval_C, derivative_sub,
          derivative_X, derivative_C] at e0 e1 ⊢
        rw [e0, e1]; ring
      · intro hi; exact absurd (mem_univ i) hi
    rw [hval] at h0
    rcases mul_eq_zero.mp h0 with h1 | h1
    · rcases mul_eq_zero.mp h1 with h2 | h2
      · exact absurd h2 (hw i)
      · exact h2
    · exact absurd h1 (hq_eval_ne i)
  -- step 2: `d = 0`
  have hd : ∀ i, d i = 0 := by
    intro i
    have hdeg : (q i).natDegree < 2 * K := by have := hq_deg i; have := hK i; omega
    have h0 := hΛ _ hdeg
    have hval : Λ (q i) = d i * (q i).eval (s i) := by
      simp only [hΛdef, hu, mul_zero, zero_mul, add_zero]
      rw [sum_eq_single i]
      · intro j _ hji
        obtain ⟨r, hr⟩ := hq_split i j hji
        rw [hr, (p1_double_root (s j) r).1, mul_zero]
      · intro hi; exact absurd (mem_univ i) hi
    rw [hval] at h0
    rcases mul_eq_zero.mp h0 with h1 | h1
    · exact h1
    · exact absurd h1 (hq_eval_ne i)
  exact ⟨funext hu, funext hd⟩

/-- **The Jacobian of the moment map is injective** at every point with distinct nodes and nonzero weights. -/
theorem p1_momentMap_fderiv_injective {K : ℕ} (x : PronyParam K) (hs : Function.Injective x.1)
    (hw : ∀ i, x.2 i ≠ 0) : Function.Injective (fderiv ℝ (momentMap K) x) := by
  refine (injective_iff_map_eq_zero _).mpr (fun v hv => ?_)
  have h : ∀ m : ℕ, m < 2 * K →
      ∑ i, (v.2 i * x.1 i ^ m + x.2 i * ((m : ℝ) * x.1 i ^ (m - 1)) * v.1 i) = 0 := by
    intro m hm
    have := congrFun hv ⟨m, hm⟩
    rw [p1_momentMap_fderiv_apply] at this
    simpa using this
  obtain ⟨hu, hd⟩ := p1_hermite_functional x.1 x.2 v.1 v.2 hs hw h
  exact Prod.ext hu hd

theorem p1_mergedWeight_at_node {K : ℕ} (s w : Fin K → ℝ) (hs : Function.Injective s) (i : Fin K) :
    mergedWeight univ s w (s i) = w i := by
  classical
  have : univ.filter (fun j => s j = s i) = {i} := by
    ext j; simp [hs.eq_iff]
  simp [mergedWeight, this]

/-- **Uniqueness of the ordered representation.** Two `K`-atom representations with strictly increasing nodes,
nonzero weights and the same first `2K` moments are equal. -/
theorem p1_ordered_representation_unique {K : ℕ} (x y : PronyParam K) (hx : StrictMono x.1)
    (hy : StrictMono y.1) (hxw : ∀ i, x.2 i ≠ 0) (hyw : ∀ i, y.2 i ≠ 0)
    (h : momentMap K x = momentMap K y) : x = y := by
  classical
  have hmw := p1_thm_measure_from_finitely_many_moments (univ : Finset (Fin K)) (univ : Finset (Fin K))
    x.1 x.2 y.1 y.2 (fun m hm => by
      have hm' : m < 2 * K := by simpa [two_mul] using hm
      have := congrFun h ⟨m, hm'⟩
      simpa [momentMap] using this)
  have hsub : ∀ (a b : PronyParam K), StrictMono a.1 → StrictMono b.1 → (∀ i, b.2 i ≠ 0) →
      (∀ ρ, mergedWeight univ a.1 a.2 ρ = mergedWeight univ b.1 b.2 ρ) →
      Set.range b.1 ⊆ Set.range a.1 := by
    intro a b ha hb hbw hab
    rintro _ ⟨j, rfl⟩
    have e := hab (b.1 j)
    rw [p1_mergedWeight_at_node b.1 b.2 hb.injective] at e
    by_contra hnot
    have hempty : univ.filter (fun i => a.1 i = b.1 j) = ∅ := by
      refine filter_eq_empty_iff.mpr (fun i _ hi => hnot ⟨i, hi⟩)
    simp [mergedWeight, hempty] at e
    exact hbw j e.symm
  have hrange : Set.range x.1 = Set.range y.1 :=
    (hsub y x hy hx hxw (fun ρ => (hmw ρ).symm)).antisymm (hsub x y hx hy hyw hmw)
  have hs : x.1 = y.1 := (hx.range_inj_of_wellFoundedLT hy).mp hrange
  refine Prod.ext hs (funext fun i => ?_)
  have e := hmw (x.1 i)
  rw [p1_mergedWeight_at_node x.1 x.2 hx.injective, hs,
    p1_mergedWeight_at_node y.1 y.2 hy.injective] at e
  exact e

/-! ### Prony's method returns the nodes -/

/-- Hankel matrix `H_{ab} = t_{a+b}` of the first `2K - 1` moments. -/
def pronyHankel {K : ℕ} (t : Fin (2 * K) → ℝ) : Matrix (Fin K) (Fin K) ℝ :=
  fun a b => t ⟨(a : ℕ) + b, by omega⟩

/-- Right-hand side of Prony's system, `-t_{a+K}`. -/
def pronyRhs {K : ℕ} (t : Fin (2 * K) → ℝ) : Fin K → ℝ :=
  fun a => -t ⟨(a : ℕ) + K, by omega⟩

/-- Prony's polynomial from a coefficient vector `c`: `X^K + ∑_{b<K} c_b X^b`. -/
noncomputable def pronyPoly {K : ℕ} (c : Fin K → ℝ) : ℝ[X] :=
  X ^ K + ∑ b : Fin K, C (c b) * X ^ (b : ℕ)

theorem p1_prony_hankel_factor {K : ℕ} (x : PronyParam K) :
    pronyHankel (momentMap K x) =
      (Matrix.vandermonde x.1).transpose * Matrix.diagonal x.2 * Matrix.vandermonde x.1 := by
  ext a b
  simp only [pronyHankel, momentMap, Matrix.mul_apply, Matrix.transpose_apply, Matrix.diagonal_apply,
    Matrix.vandermonde_apply, mul_ite, mul_zero, sum_ite_eq', mem_univ, ite_true]
  refine sum_congr rfl (fun i _ => by rw [pow_add]; ring)

/-- The Hankel matrix of the moments of a measure with distinct nodes and nonzero weights is nonsingular. -/
theorem p1_prony_hankel_det_ne_zero {K : ℕ} (x : PronyParam K) (hs : Function.Injective x.1)
    (hw : ∀ i, x.2 i ≠ 0) : (pronyHankel (momentMap K x)).det ≠ 0 := by
  rw [p1_prony_hankel_factor, Matrix.det_mul, Matrix.det_mul, Matrix.det_transpose, Matrix.det_diagonal]
  have hv : (Matrix.vandermonde x.1).det ≠ 0 := Matrix.det_vandermonde_ne_zero_iff.mpr hs
  exact mul_ne_zero (mul_ne_zero hv (prod_ne_zero_iff.mpr (fun i _ => hw i))) hv

/-- **Prony's method returns the nodes.** For the moments of a measure with distinct nodes `s` and nonzero
weights, every solution `c` of Prony's system `H c = -t_{K+·}` gives the polynomial `∏ (X - s_i)`, so the roots
Prony's method extracts are exactly the nodes: real and distinct. -/
theorem p1_prony_polynomial {K : ℕ} (x : PronyParam K) (hs : Function.Injective x.1)
    (hw : ∀ i, x.2 i ≠ 0) (c : Fin K → ℝ)
    (hc : (pronyHankel (momentMap K x)).mulVec c = pronyRhs (momentMap K x)) :
    pronyPoly c = ∏ i, (X - C (x.1 i)) ∧ ∀ z : ℝ, (pronyPoly c).eval z = 0 ↔ ∃ i, x.1 i = z := by
  classical
  set P : ℝ[X] := ∏ i, (X - C (x.1 i)) with hPdef
  have hmon : P.Monic := monic_prod_of_monic _ _ (fun i _ => monic_X_sub_C _)
  have hdeg : P.natDegree = K := by
    rw [hPdef, natDegree_prod_of_monic _ _ (fun i _ => monic_X_sub_C _)]
    simp
  set c₀ : Fin K → ℝ := fun b => P.coeff b with hc₀
  have hPsum : P = pronyPoly c₀ := by
    conv_lhs => rw [hmon.as_sum, hdeg]
    simp only [pronyPoly, hc₀]
    rw [sum_range (fun b => C (P.coeff b) * X ^ b)]
  have hroot : ∀ i, (pronyPoly c₀).eval (x.1 i) = 0 := by
    intro i
    rw [← hPsum, hPdef, eval_prod]
    exact prod_eq_zero (mem_univ i) (by simp)
  -- `c₀` solves Prony's system
  have hsolve : (pronyHankel (momentMap K x)).mulVec c₀ = pronyRhs (momentMap K x) := by
    funext a
    have hi : ∀ i, ∑ b : Fin K, c₀ b * x.1 i ^ (b : ℕ) = -x.1 i ^ K := by
      intro i
      have := hroot i
      simp only [pronyPoly, eval_add, eval_pow, eval_X, eval_finsetSum, eval_C_mul] at this
      linarith
    simp only [Matrix.mulVec, dotProduct, pronyHankel, pronyRhs, momentMap]
    calc ∑ b : Fin K, (∑ i, x.2 i * x.1 i ^ ((a : ℕ) + b)) * c₀ b
        = ∑ i, x.2 i * x.1 i ^ (a : ℕ) * ∑ b : Fin K, c₀ b * x.1 i ^ (b : ℕ) := by
          simp only [sum_mul, mul_sum]
          rw [sum_comm]
          refine sum_congr rfl (fun i _ => sum_congr rfl (fun b _ => by rw [pow_add]; ring))
      _ = -∑ i, x.2 i * x.1 i ^ ((a : ℕ) + K) := by
          simp only [hi]
          rw [← sum_neg_distrib]
          refine sum_congr rfl (fun i _ => by rw [pow_add]; ring)
  -- uniqueness from the nonsingular Hankel matrix
  have hdet := p1_prony_hankel_det_ne_zero x hs hw
  have hunit : IsUnit (pronyHankel (momentMap K x)).det := isUnit_iff_ne_zero.mpr hdet
  have hceq : c = c₀ := by
    have e1 : c = ((pronyHankel (momentMap K x))⁻¹ * pronyHankel (momentMap K x)).mulVec c := by
      rw [Matrix.nonsing_inv_mul _ hunit, Matrix.one_mulVec]
    have e2 : c₀ = ((pronyHankel (momentMap K x))⁻¹ * pronyHankel (momentMap K x)).mulVec c₀ := by
      rw [Matrix.nonsing_inv_mul _ hunit, Matrix.one_mulVec]
    rw [e1, e2, ← Matrix.mulVec_mulVec, ← Matrix.mulVec_mulVec, hc, hsolve]
  have hpoly : pronyPoly c = P := by rw [hceq, ← hPsum]
  refine ⟨hpoly, fun z => ?_⟩
  rw [hpoly, hPdef, eval_prod, prod_eq_zero_iff]
  simp only [mem_univ, true_and, eval_sub, eval_X, eval_C, sub_eq_zero]
  exact ⟨fun ⟨i, hi⟩ => ⟨i, hi.symm⟩, fun ⟨i, hi⟩ => ⟨i, hi.symm⟩⟩

end CurrentMM
