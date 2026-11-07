import CurrentProofs.Paper1MinPhase
import Mathlib.Analysis.SpecialFunctions.Complex.Arg
import Mathlib.Algebra.Polynomial.Reverse
import Mathlib.Algebra.Polynomial.Roots

/-!
# Paper 1, Theorem `thm:minphase` (ii) for every `K`: the price spectrum determines the memory rates

The starting point is equality of the observed spectra, `s₁ |H₁(e^{iω})|²/(2π) = s₂ |H₂(e^{iω})|²/(2π)` for every
frequency `ω`, with `H_j = tfTop κ_j r_j / tfBottom a_j κ_j w_j r_j` the paper's transfer function and `s_j > 0` the
(possibly unknown, possibly different) innovation variances. Nothing about numerators, roots or rates is assumed equal.

The argument is algebraic. For a real polynomial `p` and `|z| = 1`, `|p(z)|² = p(z) p(z⁻¹) = z^{-deg p} p(z) p^rev(z)`,
so the spectral identity becomes a polynomial identity `L = R` on the unit circle, hence everywhere
(`eq_of_infinite_eval_eq`). At a nonzero zero `α` of `H₁` inside the disk the left side vanishes; on the right the
reversed factors do not vanish (their zeros are the reciprocals `1/β` of zeros inside the disk), the denominator of
`H₁` does not vanish at `α` (no cancellation, `p1_thm_minphase_zeros`), so the numerator of `H₂` vanishes at `α`.

* `p1_spectral_zero_transfer`: the general statement for four real polynomials (stable, minimum-phase, coprime).
* `p1_thm_minphase_spectrum_rates`: for two economies with any numbers `K₁, K₂` of cohorts, equal spectra imply
  `Set.range r₁ = Set.range r₂`.

Stability enters as the hypothesis that all zeros of `tfBottom` lie in the open unit disk (the poles of `H`).
Not covered here: that the spectrum also fixes `s κ²` and `H/h₀` (zero and pole multiplicities), which with known
`κ` and `a` gives the merged measure through Theorem `thm:merged`.
-/

namespace CurrentMM

open Polynomial Complex ComplexConjugate

local notation "φℂ" => (algebraMap ℝ ℂ)

/-- The unit circle in `ℂ` is infinite. -/
theorem p1_unit_circle_infinite : {z : ℂ | ‖z‖ = 1}.Infinite := by
  have hden : ∀ t : ℝ, (1 : ℂ) - (t : ℂ) * I ≠ 0 := by
    intro t h
    have := congrArg Complex.re h
    simp at this
  refine Set.infinite_of_injective_forall_mem (f := fun t : ℝ => (1 + (t : ℂ) * I) / (1 - (t : ℂ) * I))
    ?_ ?_
  · intro t s hts
    have hts' : (1 + (t : ℂ) * I) / (1 - (t : ℂ) * I) = (1 + (s : ℂ) * I) / (1 - (s : ℂ) * I) := hts
    rw [div_eq_div_iff (hden t) (hden s)] at hts'
    have := congrArg Complex.im hts'
    simp at this
    linarith
  · intro t
    simp only [Set.mem_setOf_eq]
    have hc : (1 : ℂ) - (t : ℂ) * I = conj (1 + (t : ℂ) * I) := by simp [map_add, map_mul, conj_ofReal]; ring
    rw [norm_div, hc, norm_conj, div_self]
    rw [Ne, norm_eq_zero]
    intro h
    have := congrArg Complex.re h
    simp at this

theorem p1_conj_eval_map (p : ℝ[X]) (z : ℂ) :
    conj ((p.map (algebraMap ℝ ℂ)).eval z) = (p.map (algebraMap ℝ ℂ)).eval (conj z) := by
  rw [eval_map, eval_map, Polynomial.hom_eval₂]
  congr 1
  exact RingHom.ext fun x => by simp

theorem p1_rev_eval_map (p : ℝ[X]) (z : ℂ) (hz : z ≠ 0) :
    z ^ p.natDegree * (p.map (algebraMap ℝ ℂ)).eval z⁻¹ = (p.reverse.map (algebraMap ℝ ℂ)).eval z := by
  letI : Invertible z⁻¹ := invertibleOfNonzero (inv_ne_zero hz)
  have h := eval₂_reverse_mul_pow (algebraMap ℝ ℂ) z⁻¹ p
  rw [invOf_eq_inv, inv_inv] at h
  rw [eval_map, eval_map, ← h]
  have hk : z⁻¹ ^ p.natDegree * z ^ p.natDegree = 1 := by rw [← mul_pow, inv_mul_cancel₀ hz, one_pow]
  linear_combination (p.reverse.eval₂ (algebraMap ℝ ℂ) z) * hk

/-- If every zero of `p` lies in the open unit disk and `‖α‖ < 1`, `α ≠ 0`, the reversed polynomial does not vanish
at `α`. -/
theorem p1_rev_ne_zero (p : ℝ[X]) (hp : ∀ z : ℂ, (p.map (algebraMap ℝ ℂ)).eval z = 0 → ‖z‖ < 1) (α : ℂ)
    (hα0 : α ≠ 0) (hα : ‖α‖ ≤ 1) : (p.reverse.map (algebraMap ℝ ℂ)).eval α ≠ 0 := by
  rw [← p1_rev_eval_map p α hα0]
  refine mul_ne_zero (pow_ne_zero _ hα0) fun h => ?_
  have h1 := hp _ h
  rw [norm_inv] at h1
  have hpos : 0 < ‖α‖ := norm_pos_iff.mpr hα0
  have h2 := mul_lt_mul_of_pos_right h1 hpos
  rw [inv_mul_cancel₀ hpos.ne', one_mul] at h2
  linarith

/-- On the unit circle, `|p(z)|² = z^{-deg p} p(z) p^rev(z)`, written without inverses. -/
theorem p1_circle_sq (p : ℝ[X]) (z : ℂ) (hz : ‖z‖ = 1) :
    z ^ p.natDegree * (((‖(p.map (algebraMap ℝ ℂ)).eval z‖ ^ 2 : ℝ)) : ℂ) =
      (p.map (algebraMap ℝ ℂ)).eval z * (p.reverse.map (algebraMap ℝ ℂ)).eval z := by
  have hz0 : z ≠ 0 := by rintro rfl; simp at hz
  have hinv : z⁻¹ = conj z := by
    rw [Complex.inv_def, Complex.normSq_eq_norm_sq, hz]; simp
  rw [← p1_rev_eval_map p z hz0, hinv, ← p1_conj_eval_map, ← Complex.normSq_eq_norm_sq, ← Complex.mul_conj]
  ring

/-- **Zeros transfer between economies with equal spectra.** -/
theorem p1_spectral_zero_transfer (n1 d1 n2 d2 : ℝ[X]) (s1 s2 : ℝ) (hs2 : s2 ≠ 0)
    (hn1 : ∀ z : ℂ, (n1.map (algebraMap ℝ ℂ)).eval z = 0 → ‖z‖ < 1)
    (hn2 : ∀ z : ℂ, (n2.map (algebraMap ℝ ℂ)).eval z = 0 → ‖z‖ < 1)
    (hd1 : ∀ z : ℂ, (d1.map (algebraMap ℝ ℂ)).eval z = 0 → ‖z‖ < 1)
    (hd2 : ∀ z : ℂ, (d2.map (algebraMap ℝ ℂ)).eval z = 0 → ‖z‖ < 1)
    (hcop1 : ∀ z : ℂ, (n1.map (algebraMap ℝ ℂ)).eval z = 0 → (d1.map (algebraMap ℝ ℂ)).eval z ≠ 0)
    (hS : ∀ z : ℂ, ‖z‖ = 1 →
      s1 * ‖(n1.map (algebraMap ℝ ℂ)).eval z / (d1.map (algebraMap ℝ ℂ)).eval z‖ ^ 2 =
        s2 * ‖(n2.map (algebraMap ℝ ℂ)).eval z / (d2.map (algebraMap ℝ ℂ)).eval z‖ ^ 2)
    (α : ℂ) (hα0 : α ≠ 0) (hα : (n1.map (algebraMap ℝ ℂ)).eval α = 0) :
    (n2.map (algebraMap ℝ ℂ)).eval α = 0 := by
  set L : ℂ[X] := C (s1 : ℂ) * n1.map φℂ * n1.reverse.map φℂ * d2.map φℂ * d2.reverse.map φℂ *
    X ^ (n2.natDegree + d1.natDegree) with hL
  set R : ℂ[X] := C (s2 : ℂ) * n2.map φℂ * n2.reverse.map φℂ * d1.map φℂ * d1.reverse.map φℂ *
    X ^ (n1.natDegree + d2.natDegree) with hR
  have hcirc : ∀ z : ℂ, ‖z‖ = 1 → L.eval z = R.eval z := by
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
    rw [hL, hR]
    simp only [eval_mul, eval_C, eval_pow, eval_X]
    set A1 := (n1.map (algebraMap ℝ ℂ)).eval z
    set A2 := (n2.map (algebraMap ℝ ℂ)).eval z
    set B1 := (d1.map (algebraMap ℝ ℂ)).eval z
    set B2 := (d2.map (algebraMap ℝ ℂ)).eval z
    set A1r := (n1.reverse.map (algebraMap ℝ ℂ)).eval z
    set A2r := (n2.reverse.map (algebraMap ℝ ℂ)).eval z
    set B1r := (d1.reverse.map (algebraMap ℝ ℂ)).eval z
    set B2r := (d2.reverse.map (algebraMap ℝ ℂ)).eval z
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
  have hLR : L = R := by
    refine Polynomial.eq_of_infinite_eval_eq L R (p1_unit_circle_infinite.mono fun z hz => ?_)
    exact hcirc z hz
  have hαn : ‖α‖ < 1 := hn1 α hα
  have hLα : L.eval α = 0 := by
    rw [hL]; simp only [eval_mul, eval_C, eval_pow, eval_X]; rw [hα]; ring
  rw [hLR, hR] at hLα
  simp only [eval_mul, eval_C, eval_pow, eval_X] at hLα
  by_contra hne
  have hr2 := p1_rev_ne_zero n2 hn2 α hα0 hαn.le
  have hr1 := p1_rev_ne_zero d1 hd1 α hα0 hαn.le
  have hs : (s2 : ℂ) ≠ 0 := by exact_mod_cast hs2
  have := hcop1 α hα
  exact (mul_ne_zero (mul_ne_zero (mul_ne_zero (mul_ne_zero (mul_ne_zero hs hne) hr2) this) hr1)
    (pow_ne_zero _ hα0)) hLα

/-- **Theorem `thm:minphase` (ii), every `K`: the spectrum determines the memory rates.** Two stable economies
(all poles of `H` in the open unit disk) satisfying the hypotheses of part (i), driven by single innovation sequences
with variances `s₁, s₂ > 0`, have equal price spectra at every frequency only if their sets of memory rates coincide.
The numbers of cohorts `K₁, K₂`, the anchors, impacts, weights and innovation variances may all differ. -/
theorem p1_thm_minphase_spectrum_rates {K1 K2 : ℕ} (a1 κ1 a2 κ2 s1 s2 : ℝ) (w1 r1 : Fin K1 → ℝ)
    (w2 r2 : Fin K2 → ℝ) (ha1 : a1 ≠ 0) (hκ1 : κ1 ≠ 0) (ha2 : a2 ≠ 0) (hκ2 : κ2 ≠ 0)
    (hr1 : Function.Injective r1) (hr2 : Function.Injective r2) (hr10 : ∀ i, 0 < r1 i) (hr11 : ∀ i, r1 i < 1)
    (hr20 : ∀ i, 0 < r2 i) (hr21 : ∀ i, r2 i < 1) (hw1 : ∀ i, w1 i ≠ 0) (hw2 : ∀ i, w2 i ≠ 0)
    (hs1 : 0 < s1) (hs2 : 0 < s2)
    (hstab1 : ∀ z : ℂ, ((tfBottom a1 κ1 w1 r1).map (algebraMap ℝ ℂ)).eval z = 0 → ‖z‖ < 1)
    (hstab2 : ∀ z : ℂ, ((tfBottom a2 κ2 w2 r2).map (algebraMap ℝ ℂ)).eval z = 0 → ‖z‖ < 1)
    (hspec : ∀ ω : ℝ,
      s1 * ‖((tfTop κ1 r1).map (algebraMap ℝ ℂ)).eval (exp (ω * I)) /
          ((tfBottom a1 κ1 w1 r1).map (algebraMap ℝ ℂ)).eval (exp (ω * I))‖ ^ 2 / (2 * Real.pi) =
      s2 * ‖((tfTop κ2 r2).map (algebraMap ℝ ℂ)).eval (exp (ω * I)) /
          ((tfBottom a2 κ2 w2 r2).map (algebraMap ℝ ℂ)).eval (exp (ω * I))‖ ^ 2 / (2 * Real.pi)) :
    Set.range r1 = Set.range r2 := by
  have Z1 := p1_thm_minphase_zeros a1 κ1 w1 r1 ha1 hκ1 hr1 hr10 hr11 hw1
  have Z2 := p1_thm_minphase_zeros a2 κ2 w2 r2 ha2 hκ2 hr2 hr20 hr21 hw2
  have hpi : (0 : ℝ) < 2 * Real.pi := by positivity
  have hS : ∀ z : ℂ, ‖z‖ = 1 →
      s1 * ‖((tfTop κ1 r1).map (algebraMap ℝ ℂ)).eval z / ((tfBottom a1 κ1 w1 r1).map (algebraMap ℝ ℂ)).eval z‖ ^ 2 =
      s2 * ‖((tfTop κ2 r2).map (algebraMap ℝ ℂ)).eval z /
        ((tfBottom a2 κ2 w2 r2).map (algebraMap ℝ ℂ)).eval z‖ ^ 2 := by
    intro z hz
    have hzexp : exp (arg z * I) = z := by
      have := Complex.norm_mul_exp_arg_mul_I z
      rw [hz, Complex.ofReal_one, one_mul] at this
      exact this
    have h := hspec (arg z)
    rw [hzexp] at h
    exact (div_left_inj' hpi.ne').mp h
  have transfer12 := p1_spectral_zero_transfer (tfTop κ1 r1) (tfBottom a1 κ1 w1 r1) (tfTop κ2 r2)
    (tfBottom a2 κ2 w2 r2) s1 s2 hs2.ne' Z1.2.2 Z2.2.2 hstab1 hstab2 Z1.2.1 hS
  have transfer21 := p1_spectral_zero_transfer (tfTop κ2 r2) (tfBottom a2 κ2 w2 r2) (tfTop κ1 r1)
    (tfBottom a1 κ1 w1 r1) s2 s1 hs1.ne' Z2.2.2 Z1.2.2 hstab2 hstab1 Z2.2.1 (fun z hz => (hS z hz).symm)
  ext x
  constructor
  · rintro ⟨i, rfl⟩
    have hroot : ((tfTop κ1 r1).map (algebraMap ℝ ℂ)).eval (r1 i : ℂ) = 0 := (Z1.1 _).mpr (Or.inr ⟨i, rfl⟩)
    have hne : (r1 i : ℂ) ≠ 0 := by exact_mod_cast (hr10 i).ne'
    rcases (Z2.1 _).mp (transfer12 _ hne hroot) with h | ⟨j, hj⟩
    · exact absurd h hne
    · exact ⟨j, by exact_mod_cast hj.symm⟩
  · rintro ⟨j, rfl⟩
    have hroot : ((tfTop κ2 r2).map (algebraMap ℝ ℂ)).eval (r2 j : ℂ) = 0 := (Z2.1 _).mpr (Or.inr ⟨j, rfl⟩)
    have hne : (r2 j : ℂ) ≠ 0 := by exact_mod_cast (hr20 j).ne'
    rcases (Z1.1 _).mp (transfer21 _ hne hroot) with h | ⟨i, hi⟩
    · exact absurd h hne
    · exact ⟨i, by exact_mod_cast hi.symm⟩

end CurrentMM
