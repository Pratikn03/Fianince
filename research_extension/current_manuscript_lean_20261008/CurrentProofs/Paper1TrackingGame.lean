import CurrentProofs.Paper1Pinsker
import Mathlib.Analysis.SpecialFunctions.Sqrt

/-!
# Paper 1: surveillance over time and against strategic traders (core `thm:track`, `prop:observer`, `prop:hidegame`)

* `p1_track_sum_sq_le`, `p1_track_kl_window`: a path that leaves a configuration at speed `v` for `m` periods, with
  `n` experiments per period and per-experiment divergence at most `C (Δc)²`, accumulates divergence at most
  `n C v² m³` (the lower-bound step of `thm:track`).
* `p1_track_two_point`: if two data laws are within divergence `1/2` and the two truths are `2ε` apart, any
  measurable estimator errs by at least `ε` with probability at least `1/4` under one of them (Le Cam).
* `p1_track_tradeoff`: with `ε³ = v B²`, the window `m = ε / v` balances bias `v m` and noise `B / √m`, giving error
  `2ε` (the upper-bound step).
* `p1_observer_floor`: if `n` probes of size `A` per period can move the population at speed `v₀ + γ n A²` while
  each probe's information scales like `A²`, the effective ratio `σ² v / (n A²)` is at least `σ² γ`, whatever the
  probing (`prop:observer`).
* `p1_hiding_detection_bound`: in the hiding game, any optimal spacing has detection probability at most
  `k D₀² / L + π(dev)`, where `π(dev)` is the detection probability of any other spacing; letting that spacing
  shrink gives `lim sup π* ≤ α + k D₀² / L` (`prop:hidegame`(ii)).
* `p1_hiding_tag_no_crowding`: if detection does not depend on the spacing (tags), the preferred spacing `D₀` is
  optimal (`prop:hidegame`(iii)).
-/

namespace CurrentMM

open Finset MeasureTheory Real InformationTheory

/-- `∑_{j=1}^{m} j² ≤ m³`. -/
theorem p1_track_sum_sq_le (m : ℕ) : ∑ j ∈ range m, ((j : ℝ) + 1) ^ 2 ≤ (m : ℝ) ^ 3 := by
  induction m with
  | zero => simp
  | succ m ih =>
      rw [sum_range_succ]
      push_cast
      nlinarith [ih, sq_nonneg (m : ℝ), (Nat.cast_nonneg m : (0 : ℝ) ≤ m)]

/-- **Divergence accumulated by a moving path.** If in the `j`-th period of the window (`j = 1, …, m`) the two
populations are `v j` apart along the family and each of the `n` experiments carries divergence at most
`C (v j)²`, the window carries at most `n C v² m³`. -/
theorem p1_track_kl_window (n C v : ℝ) (hn : 0 ≤ n) (hC : 0 ≤ C) (m : ℕ) (kl : ℕ → ℝ)
    (hkl : ∀ j < m, kl j ≤ n * C * (v * ((j : ℝ) + 1)) ^ 2) :
    ∑ j ∈ range m, kl j ≤ n * C * v ^ 2 * (m : ℝ) ^ 3 := by
  calc ∑ j ∈ range m, kl j ≤ ∑ j ∈ range m, n * C * v ^ 2 * ((j : ℝ) + 1) ^ 2 :=
        sum_le_sum fun j hj => (hkl j (mem_range.mp hj)).trans (le_of_eq (by ring))
    _ = n * C * v ^ 2 * ∑ j ∈ range m, ((j : ℝ) + 1) ^ 2 := by rw [mul_sum]
    _ ≤ n * C * v ^ 2 * (m : ℝ) ^ 3 := by
        apply mul_le_mul_of_nonneg_left (p1_track_sum_sq_le m); positivity

/-- **Le Cam's two-point step.** -/
theorem p1_track_two_point {α : Type*} [MeasurableSpace α] (P Q : Measure α) [IsProbabilityMeasure P]
    [IsProbabilityMeasure Q] (est : α → ℝ) (hm : Measurable est) (u w ε : ℝ) (hsep : 2 * ε ≤ |u - w|)
    (hkl : klDiv P Q ≤ ENNReal.ofReal (1 / 2)) :
    1 / 4 ≤ max (P.real {x | ε ≤ |est x - u|}) (Q.real {x | ε ≤ |est x - w|}) := by
  set A : Set α := {x | ε ≤ |est x - u|} with hA
  have hAm : MeasurableSet A := measurableSet_le measurable_const (continuous_abs.measurable.comp (hm.sub measurable_const))
  have h := p1_worst_error_ge P Q hAm (1 / 2) (by norm_num) hkl
  have hs : sqrt (1 / 2 / 2) = 1 / 2 := by
    rw [show (1 : ℝ) / 2 / 2 = (1 / 2) ^ 2 by norm_num, sqrt_sq (by norm_num)]
  rw [hs] at h
  have hsub : Aᶜ ⊆ {x | ε ≤ |est x - w|} := by
    intro x hx
    simp only [hA, Set.mem_compl_iff, Set.mem_setOf_eq, not_le] at hx
    simp only [Set.mem_setOf_eq]
    have := abs_sub_abs_le_abs_sub (u - w) (est x - w)
    have e : (u - w) - (est x - w) = -(est x - u) := by ring
    rw [e, abs_neg] at this
    linarith
  have hQ : Q.real Aᶜ ≤ Q.real {x | ε ≤ |est x - w|} := measureReal_mono hsub (measure_ne_top _ _)
  calc (1 : ℝ) / 4 = (1 - 1 / 2) / 2 := by norm_num
    _ ≤ max (P.real A) (Q.real Aᶜ) := h
    _ ≤ max (P.real A) (Q.real {x | ε ≤ |est x - w|}) := max_le_max le_rfl hQ

/-- **The bias-noise trade-off.** If `ε > 0` and `ε³ = v B²` with `v > 0`, the window `m = ε / v` gives
`v m + B / √m = 2ε`. -/
theorem p1_track_tradeoff (v B ε : ℝ) (hv : 0 < v) (hB : 0 ≤ B) (hε : 0 < ε) (hcube : ε ^ 3 = v * B ^ 2) :
    v * (ε / v) + B / sqrt (ε / v) = 2 * ε := by
  have hm : 0 < ε / v := div_pos hε hv
  have hsq : sqrt (ε / v) ^ 2 = ε / v := sq_sqrt hm.le
  have hs0 : 0 < sqrt (ε / v) := sqrt_pos.mpr hm
  -- B / √(ε/v) = ε  ⇔  B = ε √(ε/v)  ⇔  B² = ε³ / v
  have hB2 : B ^ 2 = (ε * sqrt (ε / v)) ^ 2 := by
    rw [mul_pow, hsq]
    field_simp
    linarith [hcube]
  have hBe : B = ε * sqrt (ε / v) := by
    have h0 : 0 ≤ ε * sqrt (ε / v) := by positivity
    nlinarith [sq_nonneg (B - ε * sqrt (ε / v)), sq_nonneg (B + ε * sqrt (ε / v))]
  rw [hBe]
  field_simp
  ring

/-- **The observer-effect floor (`prop:observer`).** With `n > 0` probes of size `A ≠ 0` per period, a population
that can move at speed `v₀ + γ n A²` and information scaling like `A²`, the ratio `σ² v / (n A²)` that sets the
tracking error is at least `σ² γ`, for every probing intensity. -/
theorem p1_observer_floor (σ v₀ γ n A : ℝ) (hv₀ : 0 ≤ v₀) (hn : 0 < n) (hA : A ≠ 0) :
    σ ^ 2 * γ ≤ σ ^ 2 * (v₀ + γ * n * A ^ 2) / (n * A ^ 2) := by
  have hnA : 0 < n * A ^ 2 := by positivity
  rw [le_div_iff₀ hnA]
  nlinarith [sq_nonneg σ, mul_nonneg (sq_nonneg σ) hv₀]

/-- **Self-limiting surveillance (`prop:hidegame`(ii)).** If the spacing `Dstar` minimizes
`k (D₀ - D)² + L π(D)` over a set containing `Ddev`, with `k ≥ 0`, `L > 0` and `0 ≤ Ddev ≤ D₀`, then
`π(Dstar) ≤ k D₀² / L + π(Ddev)`. -/
theorem p1_hiding_detection_bound (k L D₀ : ℝ) (hk : 0 ≤ k) (hL : 0 < L) (det : ℝ → ℝ) (Dstar Ddev : ℝ)
    (hdev0 : 0 ≤ Ddev) (hdev1 : Ddev ≤ D₀)
    (hopt : k * (D₀ - Dstar) ^ 2 + L * det Dstar ≤ k * (D₀ - Ddev) ^ 2 + L * det Ddev) :
    det Dstar ≤ k * D₀ ^ 2 / L + det Ddev := by
  have h1 : k * (D₀ - Ddev) ^ 2 ≤ k * D₀ ^ 2 := by
    apply mul_le_mul_of_nonneg_left _ hk
    nlinarith
  have h2 : 0 ≤ k * (D₀ - Dstar) ^ 2 := by positivity
  rw [div_add' _ _ _ hL.ne', le_div_iff₀ hL]
  nlinarith

/-- **Tags remove crowding (`prop:hidegame`(iii)).** If detection does not depend on the spacing, the preferred
spacing minimizes the group's cost. -/
theorem p1_hiding_tag_no_crowding (k L D₀ p : ℝ) (hk : 0 ≤ k) (D : ℝ) :
    k * (D₀ - D₀) ^ 2 + L * p ≤ k * (D₀ - D) ^ 2 + L * p := by
  simp only [sub_self]
  nlinarith [mul_nonneg hk (sq_nonneg (D₀ - D))]

end CurrentMM
