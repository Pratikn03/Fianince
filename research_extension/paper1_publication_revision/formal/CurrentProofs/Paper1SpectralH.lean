import CurrentProofs.Paper1SpectralID
import Mathlib.Analysis.Complex.Polynomial.Basic

/-!
# Paper 1, Theorem `thm:minphase` (ii) in full, every `K`: the spectrum determines `σ²κ²`, `H/h₀` and, with `κ`
known, the merged measure

From equal spectra `s₁|H₁(e^{iω})|²/(2π) = s₂|H₂(e^{iω})|²/(2π)` at every frequency, for two stable economies satisfying
the hypotheses of part (i), with any numbers of cohorts:

* `p1_thm_minphase_spectrum_H`: `s₁κ₁² = s₂κ₂²`, the rate polynomials `D = ∏(z - rᵢ)` coincide (so `K₁ = K₂` and the
  rates coincide) and the denominators of `H` coincide. Since `H = κ z D / B`, this says the spectrum determines
  `σ²κ²` and the normalized response `H/h₀ = z D / B` (`h₀ = κ`).
* `p1_merged_from_polys`: equal `D` and `B` with a common known impact `κ` give equal anchors and, for each rate,
  equal merged weights.
* `p1_thm_minphase_spectrum_merged`: hence with `κ` known the spectrum determines the anchor and the merged measure.

The argument extends `Paper1SpectralID`: the polynomial identity `L = R` holds on ℂ, so the root multiplicities
of `zD₁·B₂` and `zD₂·B₁` agree at every point of the punctured disk; no cancellation forces equal multiplicities of the
numerators and of the denominators separately; monic polynomials over ℂ with equal multiplicities are equal.
-/

namespace CurrentMM

open Polynomial Complex ComplexConjugate Finset

local notation "φℂ" => (algebraMap ℝ ℂ)

/-- The polynomial identity behind equal spectra. -/
theorem p1_spectral_LR (n1 d1 n2 d2 : ℝ[X]) (s1 s2 : ℝ)
    (hd1 : ∀ z : ℂ, (d1.map φℂ).eval z = 0 → ‖z‖ < 1)
    (hd2 : ∀ z : ℂ, (d2.map φℂ).eval z = 0 → ‖z‖ < 1)
    (hS : ∀ z : ℂ, ‖z‖ = 1 →
      s1 * ‖(n1.map φℂ).eval z / (d1.map φℂ).eval z‖ ^ 2 = s2 * ‖(n2.map φℂ).eval z / (d2.map φℂ).eval z‖ ^ 2) :
    C (s1 : ℂ) * n1.map φℂ * n1.reverse.map φℂ * d2.map φℂ * d2.reverse.map φℂ *
        X ^ (n2.natDegree + d1.natDegree) =
      C (s2 : ℂ) * n2.map φℂ * n2.reverse.map φℂ * d1.map φℂ * d1.reverse.map φℂ *
        X ^ (n1.natDegree + d2.natDegree) := by
  have hcirc : ∀ z : ℂ, ‖z‖ = 1 →
      (C (s1 : ℂ) * n1.map φℂ * n1.reverse.map φℂ * d2.map φℂ * d2.reverse.map φℂ *
        X ^ (n2.natDegree + d1.natDegree)).eval z =
      (C (s2 : ℂ) * n2.map φℂ * n2.reverse.map φℂ * d1.map φℂ * d1.reverse.map φℂ *
        X ^ (n1.natDegree + d2.natDegree)).eval z := by
    intro z hz
    have hd1z : (d1.map φℂ).eval z ≠ 0 := fun h => by have := hd1 z h; rw [hz] at this; exact lt_irrefl _ this
    have hd2z : (d2.map φℂ).eval z ≠ 0 := fun h => by have := hd2 z h; rw [hz] at this; exact lt_irrefl _ this
    have hb1 : ‖(d1.map φℂ).eval z‖ ^ 2 ≠ 0 := pow_ne_zero _ (norm_ne_zero_iff.mpr hd1z)
    have hb2 : ‖(d2.map φℂ).eval z‖ ^ 2 ≠ 0 := pow_ne_zero _ (norm_ne_zero_iff.mpr hd2z)
    have hreal : s1 * ‖(n1.map φℂ).eval z‖ ^ 2 * ‖(d2.map φℂ).eval z‖ ^ 2 =
        s2 * ‖(n2.map φℂ).eval z‖ ^ 2 * ‖(d1.map φℂ).eval z‖ ^ 2 := by
      have h := hS z hz
      rw [norm_div, norm_div, div_pow, div_pow] at h
      have e1 : s1 * ‖(n1.map φℂ).eval z‖ ^ 2 * ‖(d2.map φℂ).eval z‖ ^ 2 =
          s1 * (‖(n1.map φℂ).eval z‖ ^ 2 / ‖(d1.map φℂ).eval z‖ ^ 2) *
            (‖(d1.map φℂ).eval z‖ ^ 2 * ‖(d2.map φℂ).eval z‖ ^ 2) := by
        first
        | (field_simp; ring)
        | field_simp
      have e2 : s2 * ‖(n2.map φℂ).eval z‖ ^ 2 * ‖(d1.map φℂ).eval z‖ ^ 2 =
          s2 * (‖(n2.map φℂ).eval z‖ ^ 2 / ‖(d2.map φℂ).eval z‖ ^ 2) *
            (‖(d1.map φℂ).eval z‖ ^ 2 * ‖(d2.map φℂ).eval z‖ ^ 2) := by
        first
        | (field_simp; ring)
        | field_simp
      rw [e1, e2, h]
    have hc : ((s1 * ‖(n1.map φℂ).eval z‖ ^ 2 * ‖(d2.map φℂ).eval z‖ ^ 2 : ℝ) : ℂ) =
        ((s2 * ‖(n2.map φℂ).eval z‖ ^ 2 * ‖(d1.map φℂ).eval z‖ ^ 2 : ℝ) : ℂ) := by rw [hreal]
    have q1 := p1_circle_sq n1 z hz
    have q2 := p1_circle_sq n2 z hz
    have q3 := p1_circle_sq d1 z hz
    have q4 := p1_circle_sq d2 z hz
    simp only [Complex.ofReal_mul] at hc
    simp only [eval_mul, eval_C, eval_pow, eval_X]
    set A1 := (n1.map φℂ).eval z
    set A2 := (n2.map φℂ).eval z
    set B1 := (d1.map φℂ).eval z
    set B2 := (d2.map φℂ).eval z
    set A1r := (n1.reverse.map φℂ).eval z
    set A2r := (n2.reverse.map φℂ).eval z
    set B1r := (d1.reverse.map φℂ).eval z
    set B2r := (d2.reverse.map φℂ).eval z
    set a1 : ℂ := ((‖A1‖ ^ 2 : ℝ) : ℂ)
    set a2 : ℂ := ((‖A2‖ ^ 2 : ℝ) : ℂ)
    set c1 : ℂ := ((‖B1‖ ^ 2 : ℝ) : ℂ)
    set c2 : ℂ := ((‖B2‖ ^ 2 : ℝ) : ℂ)
    rw [pow_add, pow_add]
    linear_combination (z ^ n1.natDegree * z ^ d2.natDegree * z ^ n2.natDegree * z ^ d1.natDegree) * hc
      - ((s1 : ℂ) * (z ^ n2.natDegree * z ^ d1.natDegree) * (B2 * B2r)) * q1
      - ((s1 : ℂ) * (z ^ n2.natDegree * z ^ d1.natDegree) * z ^ n1.natDegree * a1) * q4
      + ((s2 : ℂ) * (z ^ n1.natDegree * z ^ d2.natDegree) * (B1 * B1r)) * q2
      + ((s2 : ℂ) * (z ^ n1.natDegree * z ^ d2.natDegree) * z ^ n2.natDegree * a2) * q3
  exact Polynomial.eq_of_infinite_eval_eq _ _ (p1_unit_circle_infinite.mono fun z hz => hcirc z hz)

theorem p1_rootMult_six (s : ℂ) (hs : s ≠ 0) (n nr d dr : ℂ[X]) (k : ℕ) (α : ℂ) (hα0 : α ≠ 0)
    (hn : n ≠ 0) (hd : d ≠ 0) (hnr : nr.eval α ≠ 0) (hdr : dr.eval α ≠ 0) :
    rootMultiplicity α (C s * n * nr * d * dr * X ^ k) = rootMultiplicity α n + rootMultiplicity α d := by
  have hC : C s ≠ 0 := by rwa [Ne, C_eq_zero]
  have hnr0 : nr ≠ 0 := fun h => hnr (by rw [h, eval_zero])
  have hdr0 : dr ≠ 0 := fun h => hdr (by rw [h, eval_zero])
  have h1 : C s * n ≠ 0 := mul_ne_zero hC hn
  have h2 : C s * n * nr ≠ 0 := mul_ne_zero h1 hnr0
  have h3 : C s * n * nr * d ≠ 0 := mul_ne_zero h2 hd
  have h4 : C s * n * nr * d * dr ≠ 0 := mul_ne_zero h3 hdr0
  have h5 : C s * n * nr * d * dr * X ^ k ≠ 0 := mul_ne_zero h4 (pow_ne_zero k X_ne_zero)
  have hXk : rootMultiplicity α ((X : ℂ[X]) ^ k) = 0 := by
    apply rootMultiplicity_eq_zero
    intro h
    have h' : ((X : ℂ[X]) ^ k).eval α = 0 := h
    rw [eval_pow, eval_X] at h'
    exact pow_ne_zero k hα0 h'
  have hm1 : rootMultiplicity α nr = 0 := rootMultiplicity_eq_zero (p := nr) (x := α) hnr
  have hm2 : rootMultiplicity α dr = 0 := rootMultiplicity_eq_zero (p := dr) (x := α) hdr
  rw [rootMultiplicity_mul h5, rootMultiplicity_mul h4, rootMultiplicity_mul h3, rootMultiplicity_mul h2,
    rootMultiplicity_mul h1, rootMultiplicity_C, hm1, hm2, hXk]
  omega

/-- **Root multiplicities balance inside the punctured disk.** -/
theorem p1_spectral_mult_eq (n1 d1 n2 d2 : ℝ[X]) (s1 s2 : ℝ) (hs1 : s1 ≠ 0) (hs2 : s2 ≠ 0)
    (hn1ne : n1 ≠ 0) (hn2ne : n2 ≠ 0) (hd1ne : d1 ≠ 0) (hd2ne : d2 ≠ 0)
    (hn1 : ∀ z : ℂ, (n1.map φℂ).eval z = 0 → ‖z‖ < 1)
    (hn2 : ∀ z : ℂ, (n2.map φℂ).eval z = 0 → ‖z‖ < 1)
    (hd1 : ∀ z : ℂ, (d1.map φℂ).eval z = 0 → ‖z‖ < 1)
    (hd2 : ∀ z : ℂ, (d2.map φℂ).eval z = 0 → ‖z‖ < 1)
    (hS : ∀ z : ℂ, ‖z‖ = 1 →
      s1 * ‖(n1.map φℂ).eval z / (d1.map φℂ).eval z‖ ^ 2 = s2 * ‖(n2.map φℂ).eval z / (d2.map φℂ).eval z‖ ^ 2)
    (α : ℂ) (hα0 : α ≠ 0) (hα : ‖α‖ < 1) :
    rootMultiplicity α (n1.map φℂ) + rootMultiplicity α (d2.map φℂ) =
      rootMultiplicity α (n2.map φℂ) + rootMultiplicity α (d1.map φℂ) := by
  have h := congrArg (rootMultiplicity α) (p1_spectral_LR n1 d1 n2 d2 s1 s2 hd1 hd2 hS)
  rw [p1_rootMult_six (s1 : ℂ) (by exact_mod_cast hs1) (n1.map φℂ) (n1.reverse.map φℂ) (d2.map φℂ)
      (d2.reverse.map φℂ) _ α hα0 (Polynomial.map_ne_zero hn1ne) (Polynomial.map_ne_zero hd2ne)
      (p1_rev_ne_zero n1 hn1 α hα0 hα.le) (p1_rev_ne_zero d2 hd2 α hα0 hα.le),
    p1_rootMult_six (s2 : ℂ) (by exact_mod_cast hs2) (n2.map φℂ) (n2.reverse.map φℂ) (d1.map φℂ)
      (d1.reverse.map φℂ) _ α hα0 (Polynomial.map_ne_zero hn2ne) (Polynomial.map_ne_zero hd1ne)
      (p1_rev_ne_zero n2 hn2 α hα0 hα.le) (p1_rev_ne_zero d1 hd1 α hα0 hα.le)] at h
  exact h

/-- Monic complex polynomials with the same root multiplicities are equal. -/
theorem p1_monic_eq_of_rootMult (P Q : ℂ[X]) (hP : P.Monic) (hQ : Q.Monic)
    (h : ∀ x, rootMultiplicity x P = rootMultiplicity x Q) : P = Q := by
  classical
  have hroots : P.roots = Q.roots := Multiset.ext.mpr fun x => by rw [count_roots, count_roots, h]
  calc P = (P.roots.map fun a => X - C a).prod :=
        (prod_multiset_X_sub_C_of_monic_of_roots_card_eq hP IsAlgClosed.card_roots_eq_natDegree).symm
    _ = (Q.roots.map fun a => X - C a).prod := by rw [hroots]
    _ = Q := prod_multiset_X_sub_C_of_monic_of_roots_card_eq hQ IsAlgClosed.card_roots_eq_natDegree

theorem p1_eval_map_real (p : ℝ[X]) (x : ℝ) : (p.map φℂ).eval (x : ℂ) = ((p.eval x : ℝ) : ℂ) := by
  rw [eval_map]
  have e := Polynomial.eval₂_at_apply (algebraMap ℝ ℂ) x (p := p)
  simp only [Complex.coe_algebraMap] at e
  exact e

/-- The normalized numerator `z D(z) = H(z)/κ`. -/
noncomputable def tfMonicTop {K : ℕ} (r : Fin K → ℝ) : ℝ[X] := X * tfDen r

theorem p1_tfMonicTop_monic {K : ℕ} (r : Fin K → ℝ) : (tfMonicTop r).Monic :=
  monic_X.mul (p1_tfDen_monic r)

theorem p1_eval_tfTop {K : ℕ} (κ : ℝ) (r : Fin K → ℝ) (z : ℂ) :
    ((tfTop κ r).map φℂ).eval z = κ * ((tfMonicTop r).map φℂ).eval z := by
  have e : tfTop κ r = C κ * tfMonicTop r := by unfold tfTop tfMonicTop; ring
  rw [e, Polynomial.map_mul, Polynomial.map_C, eval_mul, eval_C, Complex.coe_algebraMap]

theorem p1_tfDen_eval_ne {K : ℕ} (r : Fin K → ℝ) (x : ℝ) (hx : ∀ i, r i ≠ x) : (tfDen r).eval x ≠ 0 := by
  unfold tfDen
  rw [eval_prod]
  exact prod_ne_zero_iff.mpr fun i _ => by
    rw [eval_sub, eval_X, eval_C]
    exact sub_ne_zero.mpr (hx i).symm

theorem p1_tfBottom_eval_zero {K : ℕ} (a κ : ℝ) (w r : Fin K → ℝ) :
    (tfBottom a κ w r).eval 0 = -a * (tfDen r).eval 0 := by
  have hN : (tfNum w r).eval 0 = 0 := by
    unfold tfNum
    rw [eval_finsetSum]
    exact Finset.sum_eq_zero fun i _ => by simp
  unfold tfBottom
  rw [eval_sub, eval_mul, eval_mul, eval_C, hN, eval_sub, eval_X, eval_C]
  ring

theorem p1_rootMult_zero_monicTop {K : ℕ} (r : Fin K → ℝ) (hr : ∀ i, r i ≠ 0) :
    rootMultiplicity 0 ((tfMonicTop r).map φℂ) = 1 := by
  have hD : (tfDen r).map φℂ ≠ 0 := ((p1_tfDen_monic r).map φℂ).ne_zero
  unfold tfMonicTop
  rw [Polynomial.map_mul, Polynomial.map_X, rootMultiplicity_mul (mul_ne_zero X_ne_zero hD)]
  have hX : (X : ℂ[X]) = X - C 0 := by simp
  have h0 : rootMultiplicity 0 ((tfDen r).map φℂ) = 0 := by
    apply rootMultiplicity_eq_zero
    intro h
    have h' : ((tfDen r).map φℂ).eval ((0 : ℝ) : ℂ) = 0 := by rw [Complex.ofReal_zero]; exact h
    rw [p1_eval_map_real] at h'
    exact p1_tfDen_eval_ne r 0 hr (by exact_mod_cast h')
  rw [h0, hX, rootMultiplicity_X_sub_C_self, add_zero]

theorem p1_rootMult_zero_bottom {K : ℕ} (a κ : ℝ) (w r : Fin K → ℝ) (ha : a ≠ 0) (hr : ∀ i, r i ≠ 0) :
    rootMultiplicity 0 ((tfBottom a κ w r).map φℂ) = 0 := by
  apply rootMultiplicity_eq_zero
  intro h
  have h' : ((tfBottom a κ w r).map φℂ).eval ((0 : ℝ) : ℂ) = 0 := by rw [Complex.ofReal_zero]; exact h
  rw [p1_eval_map_real, p1_tfBottom_eval_zero] at h'
  have h'' : -a * (tfDen r).eval 0 = 0 := by exact_mod_cast h'
  rcases mul_eq_zero.mp h'' with h1 | h1
  · exact ha (neg_eq_zero.mp h1)
  · exact p1_tfDen_eval_ne r 0 hr h1

/-- **Theorem `thm:minphase` (ii): the spectrum determines `σ²κ²` and `H/h₀`, every `K`.** -/
theorem p1_thm_minphase_spectrum_H {K1 K2 : ℕ} (a1 κ1 a2 κ2 s1 s2 : ℝ) (w1 r1 : Fin K1 → ℝ)
    (w2 r2 : Fin K2 → ℝ) (ha1 : a1 ≠ 0) (hκ1 : κ1 ≠ 0) (ha2 : a2 ≠ 0) (hκ2 : κ2 ≠ 0)
    (hr1 : Function.Injective r1) (hr2 : Function.Injective r2) (hr10 : ∀ i, 0 < r1 i) (hr11 : ∀ i, r1 i < 1)
    (hr20 : ∀ i, 0 < r2 i) (hr21 : ∀ i, r2 i < 1) (hw1 : ∀ i, w1 i ≠ 0) (hw2 : ∀ i, w2 i ≠ 0)
    (hs1 : 0 < s1) (hs2 : 0 < s2)
    (hstab1 : ∀ z : ℂ, ((tfBottom a1 κ1 w1 r1).map φℂ).eval z = 0 → ‖z‖ < 1)
    (hstab2 : ∀ z : ℂ, ((tfBottom a2 κ2 w2 r2).map φℂ).eval z = 0 → ‖z‖ < 1)
    (hspec : ∀ ω : ℝ,
      s1 * ‖((tfTop κ1 r1).map φℂ).eval (exp (ω * I)) /
          ((tfBottom a1 κ1 w1 r1).map φℂ).eval (exp (ω * I))‖ ^ 2 / (2 * Real.pi) =
      s2 * ‖((tfTop κ2 r2).map φℂ).eval (exp (ω * I)) /
          ((tfBottom a2 κ2 w2 r2).map φℂ).eval (exp (ω * I))‖ ^ 2 / (2 * Real.pi)) :
    s1 * κ1 ^ 2 = s2 * κ2 ^ 2 ∧ tfDen r1 = tfDen r2 ∧ tfBottom a1 κ1 w1 r1 = tfBottom a2 κ2 w2 r2 := by
  have Z1 := p1_thm_minphase_zeros a1 κ1 w1 r1 ha1 hκ1 hr1 hr10 hr11 hw1
  have Z2 := p1_thm_minphase_zeros a2 κ2 w2 r2 ha2 hκ2 hr2 hr20 hr21 hw2
  have hpi : (0 : ℝ) < 2 * Real.pi := by positivity
  -- zeros of the normalized numerators
  have hP1 : ∀ z : ℂ, ((tfMonicTop r1).map φℂ).eval z = 0 → ‖z‖ < 1 := fun z hz =>
    Z1.2.2 z (by rw [p1_eval_tfTop, hz, mul_zero])
  have hP2 : ∀ z : ℂ, ((tfMonicTop r2).map φℂ).eval z = 0 → ‖z‖ < 1 := fun z hz =>
    Z2.2.2 z (by rw [p1_eval_tfTop, hz, mul_zero])
  have hcop1 : ∀ z : ℂ, ((tfMonicTop r1).map φℂ).eval z = 0 → ((tfBottom a1 κ1 w1 r1).map φℂ).eval z ≠ 0 :=
    fun z hz => Z1.2.1 z (by rw [p1_eval_tfTop, hz, mul_zero])
  have hcop2 : ∀ z : ℂ, ((tfMonicTop r2).map φℂ).eval z = 0 → ((tfBottom a2 κ2 w2 r2).map φℂ).eval z ≠ 0 :=
    fun z hz => Z2.2.1 z (by rw [p1_eval_tfTop, hz, mul_zero])
  -- the spectral identity on the circle, for the normalized numerators
  have hnorm : ∀ (κ : ℝ) (u v : ℂ), ‖(κ : ℂ) * u / v‖ ^ 2 = κ ^ 2 * ‖u / v‖ ^ 2 := by
    intro κ u v
    rw [mul_div_assoc, norm_mul, mul_pow, Complex.norm_real, Real.norm_eq_abs, sq_abs]
  have hS : ∀ z : ℂ, ‖z‖ = 1 →
      (s1 * κ1 ^ 2) * ‖((tfMonicTop r1).map φℂ).eval z / ((tfBottom a1 κ1 w1 r1).map φℂ).eval z‖ ^ 2 =
      (s2 * κ2 ^ 2) * ‖((tfMonicTop r2).map φℂ).eval z / ((tfBottom a2 κ2 w2 r2).map φℂ).eval z‖ ^ 2 := by
    intro z hz
    have hzexp : exp (arg z * I) = z := by
      have := Complex.norm_mul_exp_arg_mul_I z
      rw [hz, Complex.ofReal_one, one_mul] at this
      exact this
    have h := hspec (arg z)
    rw [hzexp] at h
    have h2 := (div_left_inj' hpi.ne').mp h
    rw [p1_eval_tfTop, p1_eval_tfTop, hnorm, hnorm] at h2
    linear_combination h2
  have hsκ1 : s1 * κ1 ^ 2 ≠ 0 := mul_ne_zero hs1.ne' (pow_ne_zero 2 hκ1)
  have hsκ2 : s2 * κ2 ^ 2 ≠ 0 := mul_ne_zero hs2.ne' (pow_ne_zero 2 hκ2)
  have hPne1 : tfMonicTop r1 ≠ 0 := (p1_tfMonicTop_monic r1).ne_zero
  have hPne2 : tfMonicTop r2 ≠ 0 := (p1_tfMonicTop_monic r2).ne_zero
  have hBm1 := (p1_tfBottom_monic_natDegree a1 κ1 w1 r1).1
  have hBm2 := (p1_tfBottom_monic_natDegree a2 κ2 w2 r2).1
  have hPm1 : ((tfMonicTop r1).map φℂ) ≠ 0 := Polynomial.map_ne_zero hPne1
  have hPm2 : ((tfMonicTop r2).map φℂ) ≠ 0 := Polynomial.map_ne_zero hPne2
  -- equal multiplicities everywhere
  have hm : ∀ α : ℂ, rootMultiplicity α ((tfMonicTop r1).map φℂ) = rootMultiplicity α ((tfMonicTop r2).map φℂ) ∧
      rootMultiplicity α ((tfBottom a1 κ1 w1 r1).map φℂ) = rootMultiplicity α ((tfBottom a2 κ2 w2 r2).map φℂ) := by
    intro α
    by_cases hα0 : α = 0
    · subst hα0
      rw [p1_rootMult_zero_monicTop r1 (fun i => (hr10 i).ne'), p1_rootMult_zero_monicTop r2 (fun i => (hr20 i).ne'),
        p1_rootMult_zero_bottom a1 κ1 w1 r1 ha1 (fun i => (hr10 i).ne'),
        p1_rootMult_zero_bottom a2 κ2 w2 r2 ha2 (fun i => (hr20 i).ne')]
      exact ⟨rfl, rfl⟩
    by_cases hα1 : ‖α‖ < 1
    · have E := p1_spectral_mult_eq (tfMonicTop r1) (tfBottom a1 κ1 w1 r1) (tfMonicTop r2) (tfBottom a2 κ2 w2 r2)
        (s1 * κ1 ^ 2) (s2 * κ2 ^ 2) hsκ1 hsκ2 hPne1 hPne2 hBm1.ne_zero hBm2.ne_zero hP1 hP2 hstab1 hstab2 hS
        α hα0 hα1
      have c1 : rootMultiplicity α ((tfMonicTop r1).map φℂ) = 0 ∨
          rootMultiplicity α ((tfBottom a1 κ1 w1 r1).map φℂ) = 0 := by
        by_cases h : rootMultiplicity α ((tfMonicTop r1).map φℂ) = 0
        · exact Or.inl h
        · right
          have hroot := (rootMultiplicity_pos hPm1).mp (Nat.pos_of_ne_zero h)
          exact rootMultiplicity_eq_zero (hcop1 α hroot)
      have c2 : rootMultiplicity α ((tfMonicTop r2).map φℂ) = 0 ∨
          rootMultiplicity α ((tfBottom a2 κ2 w2 r2).map φℂ) = 0 := by
        by_cases h : rootMultiplicity α ((tfMonicTop r2).map φℂ) = 0
        · exact Or.inl h
        · right
          have hroot := (rootMultiplicity_pos hPm2).mp (Nat.pos_of_ne_zero h)
          exact rootMultiplicity_eq_zero (hcop2 α hroot)
      omega
    · have z1 := rootMultiplicity_eq_zero (p := (tfMonicTop r1).map φℂ) (x := α) fun h => hα1 (hP1 α h)
      have z2 := rootMultiplicity_eq_zero (p := (tfMonicTop r2).map φℂ) (x := α) fun h => hα1 (hP2 α h)
      have z3 := rootMultiplicity_eq_zero (p := (tfBottom a1 κ1 w1 r1).map φℂ) (x := α) fun h => hα1 (hstab1 α h)
      have z4 := rootMultiplicity_eq_zero (p := (tfBottom a2 κ2 w2 r2).map φℂ) (x := α) fun h => hα1 (hstab2 α h)
      rw [z1, z2, z3, z4]
      exact ⟨rfl, rfl⟩
  have hPC := p1_monic_eq_of_rootMult _ _ ((p1_tfMonicTop_monic r1).map φℂ) ((p1_tfMonicTop_monic r2).map φℂ)
    fun α => (hm α).1
  have hBC := p1_monic_eq_of_rootMult _ _ (hBm1.map φℂ) (hBm2.map φℂ) fun α => (hm α).2
  have hP := Polynomial.map_injective (algebraMap ℝ ℂ) (algebraMap ℝ ℂ).injective hPC
  have hB := Polynomial.map_injective (algebraMap ℝ ℂ) (algebraMap ℝ ℂ).injective hBC
  have hP' : X * tfDen r1 = X * tfDen r2 := hP
  refine ⟨?_, mul_left_cancel₀ X_ne_zero hP', hB⟩
  -- the scale: evaluate at `z = 1`
  have h1 := hS 1 (by simp)
  rw [hPC, hBC] at h1
  have hne1 : ((tfMonicTop r2).map φℂ).eval 1 ≠ 0 := fun h => by
    have := hP2 1 h; simp at this
  have hne2 : ((tfBottom a2 κ2 w2 r2).map φℂ).eval 1 ≠ 0 := fun h => by
    have := hstab2 1 h; simp at this
  have hc : ‖((tfMonicTop r2).map φℂ).eval 1 / ((tfBottom a2 κ2 w2 r2).map φℂ).eval 1‖ ^ 2 ≠ 0 :=
    pow_ne_zero _ (norm_ne_zero_iff.mpr (div_ne_zero hne1 hne2))
  exact mul_right_cancel₀ hc h1

/-- Equal rate polynomials and equal denominators, with a common impact, give equal anchors and equal merged
weights at each rate. -/
theorem p1_merged_from_polys {K1 K2 : ℕ} (a1 a2 κ : ℝ) (hκ : κ ≠ 0) (w1 r1 : Fin K1 → ℝ) (w2 r2 : Fin K2 → ℝ)
    (hr2 : Function.Injective r2) (hr10 : ∀ i, r1 i ≠ 0)
    (hD : tfDen r1 = tfDen r2) (hB : tfBottom a1 κ w1 r1 = tfBottom a2 κ w2 r2) :
    a1 = a2 ∧ ∀ i j, r1 i = r2 j → w1 i = w2 j := by
  constructor
  · have h := congrArg (eval 0) hB
    rw [p1_tfBottom_eval_zero, p1_tfBottom_eval_zero, hD] at h
    have hne : (tfDen r2).eval 0 ≠ 0 := by rw [← hD]; exact p1_tfDen_eval_ne r1 0 hr10
    have := mul_right_cancel₀ hne h
    linarith
  · intro i j hij
    have hD1 : (tfDen r1).eval (r1 i) = 0 := p1_tfDen_eval_self r1 i
    have hD2 : (tfDen r2).eval (r1 i) = 0 := by rw [← hD]; exact hD1
    have hb := congrArg (eval (r1 i)) hB
    unfold tfBottom at hb
    simp only [eval_sub, eval_mul, eval_C, eval_X] at hb
    rw [hD1, hD2] at hb
    have hκN : κ * (tfNum w1 r1).eval (r1 i) = κ * (tfNum w2 r2).eval (r1 i) := by linarith
    have hN := mul_left_cancel₀ hκ hκN
    rw [p1_tfNum_eval_self w1 r1 i, hij, p1_tfNum_eval_self w2 r2 j] at hN
    -- the cofactor products agree
    have hq : ∏ l ∈ univ.erase i, (X - C (r1 l)) = ∏ l ∈ univ.erase j, (X - C (r2 l)) := by
      have e1 : (X - C (r1 i)) * ∏ l ∈ univ.erase i, (X - C (r1 l)) = tfDen r1 :=
        Finset.mul_prod_erase univ (fun l => X - C (r1 l)) (mem_univ i)
      have e2 : (X - C (r2 j)) * ∏ l ∈ univ.erase j, (X - C (r2 l)) = tfDen r2 :=
        Finset.mul_prod_erase univ (fun l => X - C (r2 l)) (mem_univ j)
      apply mul_left_cancel₀ (X_sub_C_ne_zero (r1 i))
      rw [e1, hD, hij]
      exact e2.symm
    have hQ := congrArg (eval (r2 j)) hq
    simp only [eval_prod, eval_sub, eval_X, eval_C] at hQ
    rw [hQ] at hN
    have hP : ∏ l ∈ univ.erase j, (r2 j - r2 l) ≠ 0 :=
      prod_ne_zero_iff.mpr fun l hl => sub_ne_zero.mpr fun h => (mem_erase.mp hl).1 (hr2 h).symm
    have hx : r2 j ≠ 0 := hij ▸ hr10 i
    exact mul_right_cancel₀ hx (mul_right_cancel₀ hP hN)

/-- **With the impact known, the spectrum determines the anchor and the merged measure.** -/
theorem p1_thm_minphase_spectrum_merged {K1 K2 : ℕ} (a1 a2 κ s1 s2 : ℝ) (w1 r1 : Fin K1 → ℝ)
    (w2 r2 : Fin K2 → ℝ) (ha1 : a1 ≠ 0) (ha2 : a2 ≠ 0) (hκ : κ ≠ 0)
    (hr1 : Function.Injective r1) (hr2 : Function.Injective r2) (hr10 : ∀ i, 0 < r1 i) (hr11 : ∀ i, r1 i < 1)
    (hr20 : ∀ i, 0 < r2 i) (hr21 : ∀ i, r2 i < 1) (hw1 : ∀ i, w1 i ≠ 0) (hw2 : ∀ i, w2 i ≠ 0)
    (hs1 : 0 < s1) (hs2 : 0 < s2)
    (hstab1 : ∀ z : ℂ, ((tfBottom a1 κ w1 r1).map φℂ).eval z = 0 → ‖z‖ < 1)
    (hstab2 : ∀ z : ℂ, ((tfBottom a2 κ w2 r2).map φℂ).eval z = 0 → ‖z‖ < 1)
    (hspec : ∀ ω : ℝ,
      s1 * ‖((tfTop κ r1).map φℂ).eval (exp (ω * I)) /
          ((tfBottom a1 κ w1 r1).map φℂ).eval (exp (ω * I))‖ ^ 2 / (2 * Real.pi) =
      s2 * ‖((tfTop κ r2).map φℂ).eval (exp (ω * I)) /
          ((tfBottom a2 κ w2 r2).map φℂ).eval (exp (ω * I))‖ ^ 2 / (2 * Real.pi)) :
    s1 = s2 ∧ a1 = a2 ∧ Set.range r1 = Set.range r2 ∧ ∀ i j, r1 i = r2 j → w1 i = w2 j := by
  obtain ⟨hsc, hD, hB⟩ := p1_thm_minphase_spectrum_H a1 κ a2 κ s1 s2 w1 r1 w2 r2 ha1 hκ ha2 hκ hr1 hr2 hr10 hr11
    hr20 hr21 hw1 hw2 hs1 hs2 hstab1 hstab2 hspec
  obtain ⟨haa, hww⟩ := p1_merged_from_polys a1 a2 κ hκ w1 r1 w2 r2 hr2 (fun i => (hr10 i).ne') hD hB
  have hs : s1 = s2 := mul_right_cancel₀ (pow_ne_zero 2 hκ) hsc
  exact ⟨hs, haa, p1_thm_minphase_spectrum_rates a1 κ a2 κ s1 s2 w1 r1 w2 r2 ha1 hκ ha2 hκ hr1 hr2 hr10 hr11
    hr20 hr21 hw1 hw2 hs1 hs2 hstab1 hstab2 hspec, hww⟩

end CurrentMM
