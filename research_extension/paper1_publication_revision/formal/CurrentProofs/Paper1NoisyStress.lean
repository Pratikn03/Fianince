import Mathlib.Topology.MetricSpace.Basic
import Mathlib.Topology.Order.Compact
import Mathlib.MeasureTheory.Measure.Real
import Mathlib.MeasureTheory.Measure.Typeclasses.Probability
import Mathlib.Analysis.Normed.Group.Basic
import Mathlib.Algebra.Order.BigOperators.Group.Finset

/-!
# Paper 1: noisy stress identification (core `prop:noisystress`)

The proof of `prop:noisystress` is the classical consistency argument for extremum estimators. This file proves it
for an abstract compact parameter set, a continuous criterion `Q ≥ 0` whose zeros are exactly the parameters with the
true answer `μ θ₀`, and any data-based criterion `Q_N` uniformly close to `Q`:

* `p1_identification_margin`: on a compact set, a small criterion forces a close answer.
* `p1_extremum_criterion_small`: a minimizer of `Q_N` has `Q ≤ 2 η` when `|Q_N - Q| ≤ η` uniformly.
* `p1_extremum_consistency`: hence for every `δ > 0` there is `η > 0` such that uniform closeness `η` puts the
  estimated answer within `δ` of the truth.
* `p1_extremum_consistency_prob`: the same in probability: `P(dist ≥ δ) ≤ P(sup |Q_N - Q| > η)`.
* `p1_min_one_lipschitz`, `p1_criterion_uniform_close`: the uniform bound
  `|Q_N(θ) - Q_N^0(θ)| ≤ ∑ w_j ‖ĥ_j - h_j(θ₀)‖` for the truncated criteria with weights `w_j ≥ 0`.
In the paper, `μ` is the signed capacity measure in the weak topology, and the identification hypothesis is Theorem
`thm:satident` (formalized in `Paper1StressIdentificationGeneral.lean` for finite populations).
-/

namespace CurrentMM

open MeasureTheory Finset

section Abstract

variable {Θ M : Type*} [TopologicalSpace Θ] [PseudoMetricSpace M]

/-- **Identification margin.** On a compact set, if `Q` is continuous and nonnegative and vanishes only where the
answer is `μ θ₀`, then for every `δ > 0` some `q > 0` makes `Q θ < q` force `dist (μ θ) (μ θ₀) < δ`. -/
theorem p1_identification_margin {S : Set Θ} (hS : IsCompact S) (μ : Θ → M) (hμ : Continuous μ)
    (Q : Θ → ℝ) (hQ : Continuous Q) (θ₀ : Θ) (hid : ∀ θ ∈ S, Q θ = 0 → μ θ = μ θ₀)
    (hQnn : ∀ θ ∈ S, 0 ≤ Q θ) :
    ∀ δ > 0, ∃ q > 0, ∀ θ ∈ S, Q θ < q → dist (μ θ) (μ θ₀) < δ := by
  intro δ hδ
  set F : Set Θ := S ∩ {θ | δ ≤ dist (μ θ) (μ θ₀)} with hF
  have hFc : IsCompact F :=
    hS.inter_right (isClosed_le continuous_const (hμ.dist continuous_const))
  by_cases hne : F.Nonempty
  · obtain ⟨θ₁, hθ₁, hmin⟩ := hFc.exists_isMinOn hne hQ.continuousOn
    have hq : 0 < Q θ₁ := by
      rcases (hQnn θ₁ hθ₁.1).lt_or_eq with h | h
      · exact h
      · exfalso
        have := hid θ₁ hθ₁.1 h.symm
        have h2 := hθ₁.2
        simp only [Set.mem_setOf_eq, this, dist_self] at h2
        linarith
    refine ⟨Q θ₁, hq, fun θ hθ hQθ => ?_⟩
    by_contra hcon
    push_neg at hcon
    have := isMinOn_iff.mp hmin θ ⟨hθ, hcon⟩
    linarith
  · refine ⟨1, one_pos, fun θ hθ _ => ?_⟩
    by_contra hcon
    push_neg at hcon
    exact hne ⟨θ, hθ, hcon⟩

/-- A minimizer of a criterion uniformly within `η` of `Q`, with `Q θ₀ = 0`, has `Q ≤ 2 η`. -/
theorem p1_extremum_criterion_small (S : Set Θ) (Q QN : Θ → ℝ) (θ₀ θhat : Θ) (hθ₀ : θ₀ ∈ S)
    (hθhat : θhat ∈ S) (hQ0 : Q θ₀ = 0) (hmin : QN θhat ≤ QN θ₀) (η : ℝ)
    (hunif : ∀ θ ∈ S, |QN θ - Q θ| ≤ η) : Q θhat ≤ 2 * η := by
  have h1 := abs_le.mp (hunif θhat hθhat)
  have h2 := abs_le.mp (hunif θ₀ hθ₀)
  rw [hQ0] at h2
  linarith [h1.1, h2.2]

/-- **Consistency of the minimum-distance estimator (deterministic form).** For every `δ > 0` there is `η > 0` such
that any minimizer of any criterion uniformly within `η` of `Q` has its answer within `δ` of the truth. -/
theorem p1_extremum_consistency {S : Set Θ} (hS : IsCompact S) (μ : Θ → M) (hμ : Continuous μ)
    (Q : Θ → ℝ) (hQ : Continuous Q) (θ₀ : Θ) (hθ₀ : θ₀ ∈ S) (hQ0 : Q θ₀ = 0)
    (hid : ∀ θ ∈ S, Q θ = 0 → μ θ = μ θ₀) (hQnn : ∀ θ ∈ S, 0 ≤ Q θ) :
    ∀ δ > 0, ∃ η > 0, ∀ (QN : Θ → ℝ) (θhat : Θ), θhat ∈ S → QN θhat ≤ QN θ₀ →
      (∀ θ ∈ S, |QN θ - Q θ| ≤ η) → dist (μ θhat) (μ θ₀) < δ := by
  intro δ hδ
  obtain ⟨q, hq, hmar⟩ := p1_identification_margin hS μ hμ Q hQ θ₀ hid hQnn δ hδ
  refine ⟨q / 3, by positivity, fun QN θhat hθhat hmin hunif => hmar θhat hθhat ?_⟩
  have := p1_extremum_criterion_small S Q QN θ₀ θhat hθ₀ hθhat hQ0 hmin (q / 3) hunif
  linarith

/-- **Consistency in probability.** With random criteria `QN ω` and minimizers `θhat ω`, for every `δ > 0` there is
`η > 0` with `P(dist(μ θhat, μ θ₀) ≥ δ) ≤ P(some θ ∈ S has |QN θ - Q θ| > η)`. If the uniform distance tends to zero
in probability, so does the error of the estimated answer. -/
theorem p1_extremum_consistency_prob {Ω : Type*} [MeasurableSpace Ω] (P : Measure Ω) [IsProbabilityMeasure P]
    {S : Set Θ} (hS : IsCompact S) (μ : Θ → M) (hμ : Continuous μ)
    (Q : Θ → ℝ) (hQ : Continuous Q) (θ₀ : Θ) (hθ₀ : θ₀ ∈ S) (hQ0 : Q θ₀ = 0)
    (hid : ∀ θ ∈ S, Q θ = 0 → μ θ = μ θ₀) (hQnn : ∀ θ ∈ S, 0 ≤ Q θ) :
    ∀ δ > 0, ∃ η > 0, ∀ (QN : Ω → Θ → ℝ) (θhat : Ω → Θ), (∀ ω, θhat ω ∈ S) →
      (∀ ω, QN ω (θhat ω) ≤ QN ω θ₀) →
      P.real {ω | δ ≤ dist (μ (θhat ω)) (μ θ₀)} ≤ P.real {ω | ¬ ∀ θ ∈ S, |QN ω θ - Q θ| ≤ η} := by
  intro δ hδ
  obtain ⟨η, hη, hcons⟩ := p1_extremum_consistency hS μ hμ Q hQ θ₀ hθ₀ hQ0 hid hQnn δ hδ
  refine ⟨η, hη, fun QN θhat hS' hmin => measureReal_mono (fun ω hω => ?_) (measure_ne_top _ _)⟩
  intro hall
  have := hcons (QN ω) (θhat ω) (hS' ω) (hmin ω) hall
  simp only [Set.mem_setOf_eq] at hω
  linarith

end Abstract

/-! ### The uniform bound for the truncated criteria -/

/-- `t ↦ min 1 t` is `1`-Lipschitz. -/
theorem p1_min_one_lipschitz (a b : ℝ) : |min 1 a - min 1 b| ≤ |a - b| := by
  have := abs_min_sub_min_le_max (1 : ℝ) a 1 b
  simp only [sub_self, abs_zero] at this
  exact this.trans (max_le (abs_nonneg _) le_rfl)

/-- **The uniform bound.** For responses in a normed group, weights `w j ≥ 0`, observed averages `x j`, true
responses `x0 j` and model responses `y j θ`, the data-based criterion `∑ w j min(1, ‖x j - y j θ‖)` is within
`∑ w j ‖x j - x0 j‖` of the population criterion `∑ w j min(1, ‖x0 j - y j θ‖)`, uniformly in `θ`. -/
theorem p1_criterion_uniform_close {V Θ : Type*} [SeminormedAddCommGroup V] (n : ℕ) (w : ℕ → ℝ)
    (hw : ∀ j, 0 ≤ w j) (x x0 : ℕ → V) (y : ℕ → Θ → V) (θ : Θ) :
    |∑ j ∈ range n, w j * min 1 ‖x j - y j θ‖ - ∑ j ∈ range n, w j * min 1 ‖x0 j - y j θ‖| ≤
      ∑ j ∈ range n, w j * ‖x j - x0 j‖ := by
  rw [← sum_sub_distrib]
  refine (abs_sum_le_sum_abs _ _).trans (sum_le_sum fun j _ => ?_)
  rw [← mul_sub, abs_mul, abs_of_nonneg (hw j)]
  refine mul_le_mul_of_nonneg_left ((p1_min_one_lipschitz _ _).trans ?_) (hw j)
  have := abs_norm_sub_norm_le (x j - y j θ) (x0 j - y j θ)
  simpa using this

end CurrentMM
