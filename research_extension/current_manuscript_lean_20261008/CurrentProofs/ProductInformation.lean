import CurrentProofs.GaussianInformation
import Mathlib.MeasureTheory.Measure.WithDensity
import Mathlib.MeasureTheory.Integral.Prod

namespace CurrentMM
noncomputable section
open MeasureTheory InformationTheory
open scoped ENNReal

theorem actual_product_rn_derivative {α β : Type*} [MeasurableSpace α] [MeasurableSpace β]
    (μ0 ν0 : Measure α) (μ1 ν1 : Measure β)
    [SigmaFinite μ0] [SigmaFinite ν0] [SigmaFinite μ1] [SigmaFinite ν1]
    (h0 : μ0 ≪ ν0) (h1 : μ1 ≪ ν1) :
    (μ0.prod μ1).rnDeriv (ν0.prod ν1) =ᵐ[ν0.prod ν1]
      fun p => μ0.rnDeriv ν0 p.1 * μ1.rnDeriv ν1 p.2 := by
  have hwd : (ν0.prod ν1).withDensity
      (fun p => μ0.rnDeriv ν0 p.1 * μ1.rnDeriv ν1 p.2) = μ0.prod μ1 := by
    rw [← prod_withDensity (Measure.measurable_rnDeriv μ0 ν0)
      (Measure.measurable_rnDeriv μ1 ν1),
      Measure.withDensity_rnDeriv_eq μ0 ν0 h0, Measure.withDensity_rnDeriv_eq μ1 ν1 h1]
  rw [← hwd]
  exact Measure.rnDeriv_withDensity _ (by fun_prop)

theorem actual_product_llr {α β : Type*} [MeasurableSpace α] [MeasurableSpace β]
    (μ0 ν0 : Measure α) (μ1 ν1 : Measure β)
    [SigmaFinite μ0] [SigmaFinite ν0] [SigmaFinite μ1] [SigmaFinite ν1]
    (h0 : μ0 ≪ ν0) (h1 : μ1 ≪ ν1) :
    llr (μ0.prod μ1) (ν0.prod ν1) =ᵐ[μ0.prod μ1]
      fun p => llr μ0 ν0 p.1 + llr μ1 ν1 p.2 := by
  have hprod := h0.prod h1
  have hpos0 := (Measure.quasiMeasurePreserving_fst (μ := μ0) (ν := μ1)).ae
    (Measure.rnDeriv_pos h0)
  have hpos1 := (Measure.quasiMeasurePreserving_snd (μ := μ0) (ν := μ1)).ae
    (Measure.rnDeriv_pos h1)
  have htop0 := (Measure.quasiMeasurePreserving_fst (μ := μ0) (ν := μ1)).ae
    (h0.ae_le (Measure.rnDeriv_lt_top μ0 ν0))
  have htop1 := (Measure.quasiMeasurePreserving_snd (μ := μ0) (ν := μ1)).ae
    (h1.ae_le (Measure.rnDeriv_lt_top μ1 ν1))
  filter_upwards [hprod.ae_le (actual_product_rn_derivative μ0 ν0 μ1 ν1 h0 h1),
    hpos0, hpos1, htop0, htop1] with p hp hp0 hp1 ht0 ht1
  unfold llr
  rw [hp, ENNReal.toReal_mul, Real.log_mul]
  · exact ENNReal.toReal_ne_zero.mpr ⟨hp0.ne', ht0.ne⟩
  · exact ENNReal.toReal_ne_zero.mpr ⟨hp1.ne', ht1.ne⟩

theorem actual_product_kl_additive {α β : Type*} [MeasurableSpace α] [MeasurableSpace β]
    (μ0 ν0 : Measure α) (μ1 ν1 : Measure β)
    [IsProbabilityMeasure μ0] [IsProbabilityMeasure ν0]
    [IsProbabilityMeasure μ1] [IsProbabilityMeasure ν1]
    (h0 : μ0 ≪ ν0) (h1 : μ1 ≪ ν1)
    (hi0 : Integrable (llr μ0 ν0) μ0) (hi1 : Integrable (llr μ1 ν1) μ1) :
    klDiv (μ0.prod μ1) (ν0.prod ν1) = klDiv μ0 ν0 + klDiv μ1 ν1 := by
  have hi : Integrable (llr (μ0.prod μ1) (ν0.prod ν1)) (μ0.prod μ1) :=
    ((hi0.comp_fst μ1).add (hi1.comp_snd μ0)).congr (actual_product_llr μ0 ν0 μ1 ν1 h0 h1).symm
  rw [klDiv_of_ac_of_integrable (h0.prod h1) hi,
    klDiv_of_ac_of_integrable h0 hi0, klDiv_of_ac_of_integrable h1 hi1]
  rw [integral_congr_ae (actual_product_llr μ0 ν0 μ1 ν1 h0 h1),
    integral_add (hi0.comp_fst μ1) (hi1.comp_snd μ0), integral_fun_fst, integral_fun_snd]
  simp only [probReal_univ, smul_eq_mul, one_mul, add_sub_cancel_right]
  rw [ENNReal.ofReal_add]
  · have h := integral_llr_add_sub_measure_univ_nonneg h0 hi0
    simpa only [probReal_univ, add_sub_cancel_right] using h
  · have h := integral_llr_add_sub_measure_univ_nonneg h1 hi1
    simpa only [probReal_univ, add_sub_cancel_right] using h

end
end CurrentMM
