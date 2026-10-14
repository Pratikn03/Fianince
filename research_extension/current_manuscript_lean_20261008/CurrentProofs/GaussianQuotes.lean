import CurrentProofs.Accounts
import Mathlib.Probability.Distributions.Gaussian.Real

namespace CurrentMM

noncomputable section
open MeasureTheory ProbabilityTheory
open scoped NNReal

def caraCertaintyEquivalent {Ω : Type*} [MeasurableSpace Ω]
    (law : Measure Ω) (loss : Ω → ℝ) (gamma spread : ℝ) : ℝ :=
  -Real.log (∫ ω, Real.exp (-gamma * (spread - loss ω)) ∂law) / gamma

/-- The exponential utility integral is derived from a Gaussian law, not assumed. -/
theorem gaussian_cara_exponential_integral {Ω : Type*} [MeasurableSpace Ω]
    (law : Measure Ω) (loss : Ω → ℝ) (mean : ℝ) (variance : ℝ≥0)
    (gamma spread : ℝ) (hlaw : HasLaw loss (gaussianReal mean variance) law) :
    (∫ ω, Real.exp (-gamma * (spread - loss ω)) ∂law) =
      Real.exp (-gamma * spread + mean * gamma + (variance : ℝ) * gamma ^ 2 / 2) := by
  have hexp : (fun ω => Real.exp (-gamma * (spread - loss ω))) =
      (fun ω => Real.exp (-gamma * spread) * Real.exp (gamma * loss ω)) := by
    funext ω
    rw [← Real.exp_add]
    congr 1
    ring
  rw [hexp, integral_const_mul]
  change Real.exp (-gamma * spread) * mgf loss law gamma = _
  rw [mgf_gaussianReal hlaw, ← Real.exp_add]
  congr 1
  ring

theorem gaussian_cara_certainty_equivalent {Ω : Type*} [MeasurableSpace Ω]
    (law : Measure Ω) (loss : Ω → ℝ) (mean : ℝ) (variance : ℝ≥0)
    (gamma spread : ℝ) (hgamma : gamma ≠ 0)
    (hlaw : HasLaw loss (gaussianReal mean variance) law) :
    caraCertaintyEquivalent law loss gamma spread =
      spread - mean - gamma * (variance : ℝ) / 2 := by
  unfold caraCertaintyEquivalent
  rw [gaussian_cara_exponential_integral law loss mean variance gamma spread hlaw,
    Real.log_exp]
  field_simp <;> ring

theorem gaussian_cara_quote_iff {Ω : Type*} [MeasurableSpace Ω]
    (law : Measure Ω) (loss : Ω → ℝ) (mean : ℝ) (variance : ℝ≥0)
    (gamma spread : ℝ) (hgamma : 0 < gamma)
    (hlaw : HasLaw loss (gaussianReal mean variance) law) :
    0 ≤ caraCertaintyEquivalent law loss gamma spread ↔
      mean + gamma * (variance : ℝ) / 2 ≤ spread := by
  rw [gaussian_cara_certainty_equivalent law loss mean variance gamma spread
    (ne_of_gt hgamma) hlaw]
  constructor <;> intro h <;> linarith

/-- Bounded model costs yield a robust quote; nonemptiness is explicit. -/
theorem robust_quote_iff {Θ : Type*} (models : Set Θ) (cost : Θ → ℝ)
    (hne : models.Nonempty) (hbounded : BddAbove (cost '' models)) (spread : ℝ) :
    (∀ θ ∈ models, cost θ ≤ spread) ↔ sSup (cost '' models) ≤ spread := by
  constructor
  · intro h
    apply csSup_le
    · exact hne.image cost
    · rintro value ⟨θ, hθ, rfl⟩
      exact h θ hθ
  · intro h θ hθ
    exact le_trans (le_csSup hbounded ⟨θ, hθ, rfl⟩) h

theorem robust_quote_dominates_baseline {Θ : Type*} (models : Set Θ) (cost : Θ → ℝ)
    (hbounded : BddAbove (cost '' models)) (baseline : Θ) (hbase : baseline ∈ models) :
    cost baseline ≤ sSup (cost '' models) :=
  le_csSup hbounded ⟨baseline, hbase, rfl⟩

/-- Proposition 2.11: Ambiguity premium `Δ = sup_θ c_θ - c_{θ_0}` is nonnegative and strictly positive iff the supremum exceeds baseline cost. -/
theorem robust_premium_nonneg_and_pos_iff {Θ : Type*} (models : Set Θ) (cost : Θ → ℝ)
    (hbounded : BddAbove (cost '' models)) (baseline : Θ) (hbase : baseline ∈ models) :
    0 ≤ sSup (cost '' models) - cost baseline ∧
      (0 < sSup (cost '' models) - cost baseline ↔ cost baseline < sSup (cost '' models)) := by
  have hle := robust_quote_dominates_baseline models cost hbounded baseline hbase
  exact ⟨sub_nonneg.mpr hle, sub_pos⟩

/-- Proposition 3.1: Under a zero-mean martingale price innovation `∫ Δp dμ = 0`, the expected next-step EMA deviation equals `(1 - α) (p - m)`. -/
theorem ema_filtered_martingale_expectation {Ω : Type*} [MeasurableSpace Ω]
    (μ : Measure Ω) [IsProbabilityMeasure μ] (alpha price oldAnchor : ℝ)
    (increment : Ω → ℝ) (hint : Integrable increment μ) (hmart : ∫ ω, increment ω ∂μ = 0) :
    (∫ ω, ((price + increment ω) -
      ((1 - alpha) * oldAnchor + alpha * (price + increment ω))) ∂μ) =
      (1 - alpha) * (price - oldAnchor) := by
  have hpoint : (fun ω => (price + increment ω) -
      ((1 - alpha) * oldAnchor + alpha * (price + increment ω))) =
      (fun ω => (1 - alpha) * (price - oldAnchor) + (1 - alpha) * increment ω) := by
    funext ω
    ring
  rw [hpoint, integral_add (integrable_const _) (hint.const_mul (1 - alpha)),
    integral_const, integral_const_mul, hmart]
  simp [probReal_univ]

end
end CurrentMM

