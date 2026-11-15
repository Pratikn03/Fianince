import Mathlib.InformationTheory.KullbackLeibler.Basic
import Mathlib.Analysis.Convex.Integral
import Mathlib.Analysis.SpecialFunctions.Log.NegMulLog
import Mathlib.Analysis.SpecialFunctions.Exponential
import Mathlib.Analysis.Complex.ExponentialBounds

/-!
# Paper 1: the two-point testing step (Le Cam form, with KL divergence)

If a test separates two probability laws `P` and `Q` with both error probabilities at most `1/4`, then
`KL(P ‖ Q) ≥ 1/4`. This is the step that turns a small divergence between two candidate markets into a lower bound on
the data needed to tell them apart (`thm:twocohort`, `thm:kcohort`). The proof uses Jensen's inequality for the
convex function `klFun x = x log x + 1 - x` on the rejection region and on its complement.
-/

namespace CurrentMM

open MeasureTheory InformationTheory Real Set
open scoped ENNReal

variable {α : Type*} [MeasurableSpace α]

/-- Jensen on one set: `ν(A) · klFun(μ(A)/ν(A)) ≤ ∫_A klFun(dμ/dν) dν`. -/
theorem p1_klFun_set_jensen (μ ν : Measure α) [IsFiniteMeasure μ] [IsFiniteMeasure ν] (hμν : μ ≪ ν)
    {A : Set α} (hνA : ν A ≠ 0)
    (hint : IntegrableOn (fun x => klFun (μ.rnDeriv ν x).toReal) A ν) :
    ν.real A * klFun (μ.real A / ν.real A) ≤ ∫ x in A, klFun (μ.rnDeriv ν x).toReal ∂ν := by
  have hfi : IntegrableOn (fun x => (μ.rnDeriv ν x).toReal) A ν :=
    Measure.integrableOn_toReal_rnDeriv (measure_ne_top _ _)
  have J := convexOn_klFun.map_set_average_le continuous_klFun.continuousOn isClosed_Ici hνA
    (measure_ne_top _ _) (ae_of_all _ (fun x => (ENNReal.toReal_nonneg : (0 : ℝ) ≤ _))) hfi hint
  rw [setAverage_eq, setAverage_eq, Measure.setIntegral_toReal_rnDeriv hμν A, smul_eq_mul,
    smul_eq_mul] at J
  have hpos : 0 < ν.real A := by
    rw [measureReal_def]
    exact ENNReal.toReal_pos hνA (measure_ne_top _ _)
  have e : (ν.real A)⁻¹ * μ.real A = μ.real A / ν.real A := by rw [inv_mul_eq_div]
  rw [e] at J
  have := mul_le_mul_of_nonneg_left J hpos.le
  rwa [← mul_assoc, mul_inv_cancel₀ hpos.ne', one_mul] at this

/-- Lower-integral version of the Jensen step (also true when the integrand is not integrable). -/
theorem p1_setLIntegral_klFun_ge (μ ν : Measure α) [IsFiniteMeasure μ] [IsFiniteMeasure ν]
    (hμν : μ ≪ ν) {A : Set α} (hνA : ν A ≠ 0) :
    ENNReal.ofReal (ν.real A * klFun (μ.real A / ν.real A)) ≤
      ∫⁻ x in A, ENNReal.ofReal (klFun (μ.rnDeriv ν x).toReal) ∂ν := by
  have hnn : ∀ᵐ x ∂(ν.restrict A), 0 ≤ klFun (μ.rnDeriv ν x).toReal :=
    ae_of_all _ (fun x => klFun_nonneg ENNReal.toReal_nonneg)
  by_cases hint : IntegrableOn (fun x => klFun (μ.rnDeriv ν x).toReal) A ν
  · rw [← ofReal_integral_eq_lintegral_ofReal hint hnn]
    exact ENNReal.ofReal_le_ofReal (p1_klFun_set_jensen μ ν hμν hνA hint)
  · have htop : ∫⁻ x in A, ENNReal.ofReal (klFun (μ.rnDeriv ν x).toReal) ∂ν = ∞ := by
      by_contra h
      exact hint ((lintegral_ofReal_ne_top_iff_integrable
        (Measurable.aestronglyMeasurable (by fun_prop)) hnn).mp h)
    rw [htop]; exact le_top

/-- `ν(A) klFun(μ(A)/ν(A)) = μ(A) log(μ(A)/ν(A)) + ν(A) - μ(A)` when `ν(A) > 0`. -/
theorem p1_mul_klFun_div (p q : ℝ) (hq : 0 < q) :
    q * klFun (p / q) = p * log (p / q) + q - p := by
  rw [klFun_apply]
  field_simp

/-- `x log x ≥ -exp(-1)` for `x ≥ 0`. -/
theorem p1_mul_log_ge_neg_exp (x : ℝ) (hx : 0 ≤ x) : -exp (-1) ≤ x * log x := by
  rcases hx.eq_or_lt with h | h
  · rw [← h]; simp; positivity
  · have hy := self_sub_one_le_mul_log (x := exp 1 * x) (by positivity)
    rw [log_mul (exp_pos 1).ne' h.ne', log_exp] at hy
    have he : 0 < exp 1 := exp_pos 1
    have h1 : -1 ≤ exp 1 * (x * log x) := by nlinarith
    have h2 : exp (-1) * exp 1 = 1 := by rw [← exp_add]; simp
    have h3 : -exp (-1) = exp (-1) * (-1) := by ring
    rw [h3]
    calc exp (-1) * (-1) ≤ exp (-1) * (exp 1 * (x * log x)) :=
          mul_le_mul_of_nonneg_left h1 (exp_pos _).le
      _ = x * log x := by rw [← mul_assoc, h2, one_mul]

/-- **Two-point testing step.** If a measurable rejection region `A` has `P(A) ≤ 1/4` and `Q(Aᶜ) ≤ 1/4`, then
`KL(P ‖ Q) ≥ 1/4`. -/
theorem p1_test_error_kl_lower_bound (P Q : Measure α) [IsProbabilityMeasure P] [IsProbabilityMeasure Q]
    {A : Set α} (hA : MeasurableSet A) (hP : P.real A ≤ 1 / 4) (hQ : Q.real Aᶜ ≤ 1 / 4) :
    ENNReal.ofReal (1 / 4) ≤ klDiv P Q := by
  by_cases hac : P ≪ Q
  swap
  · rw [klDiv_of_not_ac hac]; exact le_top
  have hPc : P.real Aᶜ = 1 - P.real A := by rw [measureReal_compl hA]; simp
  have hQc : Q.real Aᶜ = 1 - Q.real A := by rw [measureReal_compl hA]; simp
  have hPA0 : 0 ≤ P.real A := measureReal_nonneg
  have hQAc0 : 0 ≤ Q.real Aᶜ := measureReal_nonneg
  have hQA_le : Q.real A ≤ 1 := measureReal_le_one
  -- both pieces of `Q` are nonzero
  have hQA : Q A ≠ 0 := by
    intro h
    have : Q.real A = 0 := by simp [measureReal_def, h]
    linarith
  have hQAc : Q Aᶜ ≠ 0 := by
    intro h
    have hP0 : P Aᶜ = 0 := hac h
    have : P.real Aᶜ = 0 := by simp [measureReal_def, hP0]
    linarith
  have hQApos : 0 < Q.real A := ENNReal.toReal_pos hQA (measure_ne_top _ _)
  have hQAcpos : 0 < Q.real Aᶜ := ENNReal.toReal_pos hQAc (measure_ne_top _ _)
  -- split the divergence over `A` and `Aᶜ`
  rw [klDiv_eq_lintegral_klFun_of_ac hac, ← lintegral_add_compl _ hA]
  have h1 := p1_setLIntegral_klFun_ge P Q hac hQA
  have h2 := p1_setLIntegral_klFun_ge P Q hac hQAc
  have hn1 : 0 ≤ Q.real A * klFun (P.real A / Q.real A) :=
    mul_nonneg hQApos.le (klFun_nonneg (div_nonneg hPA0 hQApos.le))
  have hn2 : 0 ≤ Q.real Aᶜ * klFun (P.real Aᶜ / Q.real Aᶜ) :=
    mul_nonneg hQAcpos.le (klFun_nonneg (div_nonneg measureReal_nonneg hQAcpos.le))
  refine le_trans ?_ (add_le_add h1 h2)
  rw [← ENNReal.ofReal_add hn1 hn2]
  apply ENNReal.ofReal_le_ofReal
  rw [p1_mul_klFun_div _ _ hQApos, p1_mul_klFun_div _ _ hQAcpos]
  -- the rejection-region term is at least `-exp(-1) ≥ -1/2`
  have hexp1 : 2 ≤ exp 1 := by have := add_one_le_exp (1 : ℝ); linarith
  have hexpm : exp (-1) ≤ 1 / 2 := by
    have h := exp_pos (-1)
    have e : exp (-1) * exp 1 = 1 := by rw [← exp_add]; simp
    nlinarith
  have tA : -(1 / 2) ≤ P.real A * log (P.real A / Q.real A) := by
    rcases hPA0.eq_or_lt with h | h
    · rw [← h]; simp
    · have hle : log (P.real A) ≤ log (P.real A / Q.real A) := by
        apply log_le_log h
        rw [le_div_iff₀ hQApos]
        nlinarith
      have := p1_mul_log_ge_neg_exp (P.real A) hPA0
      nlinarith
  -- the acceptance-region term is at least `3/4 · log 3 ≥ 3/4`
  have hratio : 3 ≤ P.real Aᶜ / Q.real Aᶜ := by
    rw [le_div_iff₀ hQAcpos]; rw [hPc]; linarith
  have hlog3 : 1 ≤ log (P.real Aᶜ / Q.real Aᶜ) := by
    have he : exp 1 ≤ 3 := Real.exp_one_lt_three.le
    rw [← log_exp 1]
    exact log_le_log (exp_pos 1) (le_trans he hratio)
  have tAc : 3 / 4 ≤ P.real Aᶜ * log (P.real Aᶜ / Q.real Aᶜ) := by
    have hPc34 : 3 / 4 ≤ P.real Aᶜ := by rw [hPc]; linarith
    nlinarith
  have hmass : Q.real A - P.real A + (Q.real Aᶜ - P.real Aᶜ) = 0 := by rw [hPc, hQc]; ring
  nlinarith

end CurrentMM
