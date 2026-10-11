import CurrentProofs.GaussianQuotes
import Mathlib.InformationTheory.KullbackLeibler.Basic
import Mathlib.Probability.Distributions.Gaussian.HasGaussianLaw.Basic

namespace CurrentMM
noncomputable section
open MeasureTheory ProbabilityTheory InformationTheory
open scoped NNReal ENNReal

theorem gaussian_log_density_ratio_affine (mean0 mean1 x : ℝ) (variance : ℝ≥0)
    (hv : variance ≠ 0) :
    Real.log (gaussianPDFReal mean0 variance x / gaussianPDFReal mean1 variance x) =
      (mean0 - mean1) / (variance : ℝ) * x +
        (mean1 ^ 2 - mean0 ^ 2) / (2 * (variance : ℝ)) := by
  have hvpos : 0 < variance := pos_iff_ne_zero.mpr hv
  have hvreal : 0 < (variance : ℝ) := by exact_mod_cast hvpos
  have hpref : (Real.sqrt (2 * Real.pi * (variance : ℝ)))⁻¹ ≠ 0 := by positivity
  rw [Real.log_div (gaussianPDFReal_pos mean0 variance x hv).ne'
    (gaussianPDFReal_pos mean1 variance x hv).ne']
  unfold gaussianPDFReal
  rw [Real.log_mul hpref (Real.exp_ne_zero _), Real.log_mul hpref (Real.exp_ne_zero _),
    Real.log_exp, Real.log_exp]
  field_simp
  <;> ring

theorem gaussian_actual_llr_affine (mean0 mean1 : ℝ) (variance : ℝ≥0)
    (hv : variance ≠ 0) :
    llr (gaussianReal mean0 variance) (gaussianReal mean1 variance) =ᵐ[gaussianReal mean0 variance]
      fun x => (mean0 - mean1) / (variance : ℝ) * x +
        (mean1 ^ 2 - mean0 ^ 2) / (2 * (variance : ℝ)) := by
  have h0 := gaussianReal_absolutelyContinuous mean0 hv
  have h1 := gaussianReal_absolutelyContinuous mean1 hv
  have h01 := h0.trans (gaussianReal_absolutelyContinuous' mean1 hv)
  filter_upwards [h01.ae_le (Measure.rnDeriv_eq_div h0 h1),
    h0.ae_le (rnDeriv_gaussianReal mean0 variance), h0.ae_le (rnDeriv_gaussianReal mean1 variance)]
    with x hx hpdf0 hpdf1
  unfold llr
  rw [hx, hpdf0, hpdf1, ENNReal.toReal_div]
  simp only [gaussianPDF, ENNReal.toReal_ofReal (gaussianPDFReal_nonneg _ _ _)]
  exact gaussian_log_density_ratio_affine mean0 mean1 x variance hv

theorem gaussian_actual_llr_integrable (mean0 mean1 : ℝ) (variance : ℝ≥0)
    (hv : variance ≠ 0) :
    Integrable (llr (gaussianReal mean0 variance) (gaussianReal mean1 variance))
      (gaussianReal mean0 variance) := by
  have hG : HasGaussianLaw (fun x : ℝ => x) (gaussianReal mean0 variance) := by
    exact ⟨measurable_id.aemeasurable, by simpa using
      (inferInstance : IsGaussian (gaussianReal mean0 variance))⟩
  have hi : Integrable (fun x : ℝ => (mean0 - mean1) / (variance : ℝ) * x +
        (mean1 ^ 2 - mean0 ^ 2) / (2 * (variance : ℝ))) (gaussianReal mean0 variance) :=
    (hG.integrable.const_mul _).add (integrable_const _)
  exact hi.congr (gaussian_actual_llr_affine mean0 mean1 variance hv).symm

theorem gaussian_equal_variance_kl (mean0 mean1 : ℝ) (variance : ℝ≥0)
    (hv : variance ≠ 0) :
    klDiv (gaussianReal mean0 variance) (gaussianReal mean1 variance) =
      ENNReal.ofReal ((mean0 - mean1) ^ 2 / (2 * (variance : ℝ))) := by
  have h0 := gaussianReal_absolutelyContinuous mean0 hv
  have h01 := h0.trans (gaussianReal_absolutelyContinuous' mean1 hv)
  rw [klDiv_of_ac_of_integrable h01 (gaussian_actual_llr_integrable mean0 mean1 variance hv)]
  rw [integral_congr_ae (gaussian_actual_llr_affine mean0 mean1 variance hv)]
  have hG : HasGaussianLaw (fun x : ℝ => x) (gaussianReal mean0 variance) := by
    exact ⟨measurable_id.aemeasurable, by simpa using
      (inferInstance : IsGaussian (gaussianReal mean0 variance))⟩
  rw [integral_add (hG.integrable.const_mul _) (integrable_const _),
    integral_const_mul, integral_id_gaussianReal, integral_const]
  simp only [probReal_univ, smul_eq_mul, one_mul, add_sub_cancel_right]
  congr 1
  ring

end
end CurrentMM
