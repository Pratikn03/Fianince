import CurrentProofs.Paper1KCohortUniform

/-!
# Paper 1, Theorem `thm:kcohort`: the estimator statements, uniformly in the horizon

`p1_thm_kcohort_lower_bound_uniform` bounds every *test* between the two `K`-cohort economies. The paper states the
bound for *estimators*. This file proves both estimator statements, for `N` reset experiments of any length `T`, under
the paper's stability hypothesis.

* `p1_thm_kcohort_lower_bound_weights`: any estimator of the merged weights (listed in increasing order of memory
  rate) that is within `L W/4^L` of the truth in every coordinate, with probability at least `3/4` under both
  economies, forces `σ² ≤ N (C_U d^(2K-1))²`. The accuracy does not shrink with the spacing `d = Δη`: the two
  economies' smallest-rate weights differ by `2 L W/4^L`.
* `p1_thm_kcohort_lower_bound_W1`: the same for any estimator of the merged memory measure that integrates every
  1-Lipschitz test function vanishing at `0` to within `2 d W/(π (2K - 1))` (so in particular for Wasserstein-1 error
  below that accuracy). The witness is a shifted scaled cosine that is `0` on one economy's nodes and `2h/π` on the
  other's, `h = 2d/(2K - 1)`. This is the paper's `W₁` statement with `c_K = 2/(π (2K - 1))`.

Here `K = L + 1`, memory rates are `c + d s` with `s` on the equally spaced grid, `r_c = c`, `Δη = d`, and
`C_U = 2 κ² W/((1 - (c + d))^(2K) (1 - ς)²)`.
-/

namespace CurrentMM

open Finset MeasureTheory ProbabilityTheory InformationTheory Real
open scoped ENNReal NNReal

theorem p1_kc_witness_lipschitz (h b C : ℝ) (hh : 0 < h) :
    LipschitzWith 1 (fun r => gmWitness h (r - b) - C) := by
  have hf := p1_gmWitness_lipschitz h hh
  refine LipschitzWith.of_dist_le_mul (fun x y => ?_)
  rw [Real.dist_eq, Real.dist_eq, NNReal.coe_one, one_mul]
  have := hf.dist_le_mul (x - b) (y - b)
  rw [Real.dist_eq, Real.dist_eq, NNReal.coe_one, one_mul] at this
  rw [show gmWitness h (x - b) - C - (gmWitness h (y - b) - C) = gmWitness h (x - b) - gmWitness h (y - b) by ring]
  rw [show x - y = x - b - (y - b) by ring]
  exact this

theorem p1_kc_node_shift (L : ℕ) (c d : ℝ) (k : ℕ) :
    c + d * gridNode L k - (c - d) = 2 * d / (2 * L + 1) * (k : ℝ) := by
  unfold gridNode
  have : (2 * (L : ℝ) + 1) ≠ 0 := by positivity
  field_simp
  ring

/-- **`thm:kcohort` for weight estimators, uniformly in the horizon.** -/
theorem p1_thm_kcohort_lower_bound_weights (L : ℕ) (a κ c d W s : ℝ) (N T : ℕ)
    (q rate q' rate' : Fin (L + 1) → ℝ) (v : NNReal) (hv : v ≠ 0)
    (hc : 0 ≤ c) (hd : 0 < d) (hcd : c + d < 1) (hW : 0 ≤ W)
    (hs : |a| + |κ| * (W / (1 - (c + d))) ≤ s) (hs1 : s < 1)
    (hr : ∀ i : Fin (L + 1), 1 - rate i = c + d * gridNode L (2 * (i : ℕ) + 1))
    (hr' : ∀ i : Fin (L + 1), 1 - rate' i = c + d * gridNode L (2 * (i : ℕ)))
    (hq : ∀ i : Fin (L + 1), q i * rate i = W * ((2 * L + 1).choose (2 * (i : ℕ) + 1) : ℝ) / 2 ^ (2 * L))
    (hq' : ∀ i : Fin (L + 1), q' i * rate' i = W * ((2 * L + 1).choose (2 * (i : ℕ)) : ℝ) / 2 ^ (2 * L))
    (est : ObservationRecord (N * T) → Fin (L + 1) → ℝ) (hest : ∀ i, Measurable (fun x => est x i))
    (hsuccA : 3 / 4 ≤ (gaussianRecordLaw (N * T) (p1RepeatedMean N T (actualCohortImpulse a κ q rate)) v).real
      {x | ∀ i, |est x i - q i * rate i| < L * W / 4 ^ L})
    (hsuccB : 3 / 4 ≤ (gaussianRecordLaw (N * T) (p1RepeatedMean N T (actualCohortImpulse a κ q' rate')) v).real
      {x | ∀ i, |est x i - q' i * rate' i| < L * W / 4 ^ L}) :
    (v : ℝ) ≤ N * (2 * κ ^ 2 * W / ((1 - (c + d)) ^ (2 * L + 2) * (1 - s) ^ 2) * d ^ (2 * L + 1)) ^ 2 := by
  set ε : ℝ := L * W / 4 ^ L with hεdef
  have h4 : (2 : ℝ) ^ (2 * L) = 4 ^ L := by rw [pow_mul]; norm_num
  have hA0 : q 0 * rate 0 = W * (2 * L + 1) / 4 ^ L := by
    rw [hq 0, h4]; simp
  have hB0 : q' 0 * rate' 0 = W / 4 ^ L := by
    rw [hq' 0, h4]; simp
  have hgap : q 0 * rate 0 - q' 0 * rate' 0 = 2 * ε := by
    rw [hA0, hB0, hεdef]; ring
  set PA := gaussianRecordLaw (N * T) (p1RepeatedMean N T (actualCohortImpulse a κ q rate)) v
  set PB := gaussianRecordLaw (N * T) (p1RepeatedMean N T (actualCohortImpulse a κ q' rate')) v
  set Rej := {x : ObservationRecord (N * T) | |est x 0 - q 0 * rate 0| < ε} with hRej
  have hRejm : MeasurableSet Rej :=
    measurableSet_lt (continuous_abs.measurable.comp ((hest 0).sub measurable_const)) measurable_const
  have hAsub : {x | ∀ i, |est x i - q i * rate i| < ε} ⊆ Rej := fun x hx => hx 0
  have hBsub : {x | ∀ i, |est x i - q' i * rate' i| < ε} ⊆ Rejᶜ := by
    intro x hx hxR
    have h1 := abs_lt.mp (hx 0)
    have h2 := abs_lt.mp (show |est x 0 - q 0 * rate 0| < ε from hxR)
    linarith
  have hPA : PA.real Rejᶜ ≤ 1 / 4 := by
    have h1 : 3 / 4 ≤ PA.real Rej := hsuccA.trans (measureReal_mono hAsub)
    rw [measureReal_compl hRejm, probReal_univ]
    linarith
  have hPB : PB.real Rejᶜᶜ ≤ 1 / 4 := by
    rw [compl_compl]
    have h1 : 3 / 4 ≤ PB.real Rejᶜ := hsuccB.trans (measureReal_mono hBsub)
    rw [measureReal_compl hRejm, probReal_univ] at h1
    linarith
  have hcd0 : 0 < c + d := by linarith
  have h := p1_thm_kcohort_lower_bound_uniform L a κ c d W s N T q rate q' rate' v hv hc hd.le hcd0 hcd hW hs hs1
    hr hr' hq hq' (1 / 4) (1 / 4) (by norm_num) Rejᶜ hRejm.compl hPA hPB
  have e : (4 : ℝ) * v * (1 - 1 / 4 - 1 / 4) ^ 2 = v := by ring
  rw [e] at h
  exact h

/-- **`thm:kcohort`, Wasserstein statement, uniformly in the horizon.** -/
theorem p1_thm_kcohort_lower_bound_W1 (L : ℕ) (a κ c d W s : ℝ) (N T : ℕ)
    (q rate q' rate' : Fin (L + 1) → ℝ) (v : NNReal) (hv : v ≠ 0)
    (hc : 0 ≤ c) (hd : 0 < d) (hcd : c + d < 1) (hW : 0 ≤ W)
    (hs : |a| + |κ| * (W / (1 - (c + d))) ≤ s) (hs1 : s < 1)
    (hr : ∀ i : Fin (L + 1), 1 - rate i = c + d * gridNode L (2 * (i : ℕ) + 1))
    (hr' : ∀ i : Fin (L + 1), 1 - rate' i = c + d * gridNode L (2 * (i : ℕ)))
    (hq : ∀ i : Fin (L + 1), q i * rate i = W * ((2 * L + 1).choose (2 * (i : ℕ) + 1) : ℝ) / 2 ^ (2 * L))
    (hq' : ∀ i : Fin (L + 1), q' i * rate' i = W * ((2 * L + 1).choose (2 * (i : ℕ)) : ℝ) / 2 ^ (2 * L))
    (est : ObservationRecord (N * T) → (ℝ → ℝ) → ℝ) (hest : ∀ f, Measurable (fun x => est x f))
    (hsuccA : 3 / 4 ≤ (gaussianRecordLaw (N * T) (p1RepeatedMean N T (actualCohortImpulse a κ q rate)) v).real
      {x | ∀ f : ℝ → ℝ, LipschitzWith 1 f → f 0 = 0 →
        |est x f - ∑ i, q i * rate i * f (1 - rate i)| < 2 * d * W / (π * (2 * L + 1))})
    (hsuccB : 3 / 4 ≤ (gaussianRecordLaw (N * T) (p1RepeatedMean N T (actualCohortImpulse a κ q' rate')) v).real
      {x | ∀ f : ℝ → ℝ, LipschitzWith 1 f → f 0 = 0 →
        |est x f - ∑ i, q' i * rate' i * f (1 - rate' i)| < 2 * d * W / (π * (2 * L + 1))}) :
    (v : ℝ) ≤ N * (2 * κ ^ 2 * W / ((1 - (c + d)) ^ (2 * L + 2) * (1 - s) ^ 2) * d ^ (2 * L + 1)) ^ 2 := by
  obtain ⟨h, hhdef⟩ : ∃ h : ℝ, h = 2 * d / (2 * L + 1) := ⟨_, rfl⟩
  have hh : 0 < h := by rw [hhdef]; positivity
  obtain ⟨C0, hC0⟩ : ∃ C0 : ℝ, C0 = gmWitness h (0 - (c - d)) := ⟨_, rfl⟩
  obtain ⟨g, hgdef⟩ : ∃ g : ℝ → ℝ, g = fun r => gmWitness h (r - (c - d)) - C0 := ⟨_, rfl⟩
  have hgL : LipschitzWith 1 g := by rw [hgdef]; exact p1_kc_witness_lipschitz h (c - d) C0 hh
  have hg0 : g 0 = 0 := by rw [hgdef, hC0]; simp
  obtain ⟨hmA, hmB⟩ := p1_gm_pair_mass L W
  have hnode : ∀ k : ℕ, c + d * gridNode L k - (c - d) = h * (k : ℝ) := fun k => by
    rw [hhdef]; exact p1_kc_node_shift L c d k
  have hΦA : ∑ i, q i * rate i * g (1 - rate i) = W * (2 * h / π - C0) := by
    have e : ∀ i : Fin (L + 1), q i * rate i * g (1 - rate i) =
        W * ((2 * L + 1).choose (2 * (i : ℕ) + 1) : ℝ) / 2 ^ (2 * L) * (2 * h / π - C0) := by
      intro i
      have h1 : 1 - rate i - (c - d) = h * ((2 * (i : ℕ) + 1 : ℕ) : ℝ) := by rw [hr i]; exact hnode _
      have hp : ((-1 : ℝ)) ^ (2 * (i : ℕ) + 1) = -1 := by rw [pow_succ, pow_mul]; norm_num
      rw [hgdef]
      simp only []
      rw [h1, p1_gmWitness_node h hh.ne', hp, hq i]
      ring
    rw [sum_congr rfl (fun i _ => e i), ← sum_mul, hmA]
  have hΦB : ∑ i, q' i * rate' i * g (1 - rate' i) = W * (0 - C0) := by
    have e : ∀ i : Fin (L + 1), q' i * rate' i * g (1 - rate' i) =
        W * ((2 * L + 1).choose (2 * (i : ℕ)) : ℝ) / 2 ^ (2 * L) * (0 - C0) := by
      intro i
      have h1 : 1 - rate' i - (c - d) = h * ((2 * (i : ℕ) : ℕ) : ℝ) := by rw [hr' i]; exact hnode _
      have hp : ((-1 : ℝ)) ^ (2 * (i : ℕ)) = 1 := by rw [pow_mul]; norm_num
      rw [hgdef]
      simp only []
      rw [h1, p1_gmWitness_node h hh.ne', hp, hq' i]
      ring
    rw [sum_congr rfl (fun i _ => e i), ← sum_mul, hmB]
  set ε : ℝ := 2 * d * W / (π * (2 * L + 1)) with hεdef
  have hgap : W * (2 * h / π - C0) - W * (0 - C0) = 2 * ε := by
    rw [hεdef, hhdef]; field_simp; ring
  set PA := gaussianRecordLaw (N * T) (p1RepeatedMean N T (actualCohortImpulse a κ q rate)) v
  set PB := gaussianRecordLaw (N * T) (p1RepeatedMean N T (actualCohortImpulse a κ q' rate')) v
  set Rej := {x : ObservationRecord (N * T) | |est x g - W * (2 * h / π - C0)| < ε} with hRej
  have hRejm : MeasurableSet Rej :=
    measurableSet_lt (continuous_abs.measurable.comp ((hest g).sub measurable_const)) measurable_const
  have hAsub : {x | ∀ f : ℝ → ℝ, LipschitzWith 1 f → f 0 = 0 →
      |est x f - ∑ i, q i * rate i * f (1 - rate i)| < ε} ⊆ Rej := by
    intro x hx
    have := hx g hgL hg0
    rw [hΦA] at this
    exact this
  have hBsub : {x | ∀ f : ℝ → ℝ, LipschitzWith 1 f → f 0 = 0 →
      |est x f - ∑ i, q' i * rate' i * f (1 - rate' i)| < ε} ⊆ Rejᶜ := by
    intro x hx hxR
    have h1 := hx g hgL hg0
    rw [hΦB] at h1
    have h2 := abs_lt.mp (show |est x g - W * (2 * h / π - C0)| < ε from hxR)
    have h3 := abs_lt.mp h1
    linarith
  have hPA : PA.real Rejᶜ ≤ 1 / 4 := by
    have h1 : 3 / 4 ≤ PA.real Rej := hsuccA.trans (measureReal_mono hAsub)
    rw [measureReal_compl hRejm, probReal_univ]
    linarith
  have hPB : PB.real Rejᶜᶜ ≤ 1 / 4 := by
    rw [compl_compl]
    have h1 : 3 / 4 ≤ PB.real Rejᶜ := hsuccB.trans (measureReal_mono hBsub)
    rw [measureReal_compl hRejm, probReal_univ] at h1
    linarith
  have hcd0 : 0 < c + d := by linarith
  have hfin := p1_thm_kcohort_lower_bound_uniform L a κ c d W s N T q rate q' rate' v hv hc hd.le hcd0 hcd hW hs
    hs1 hr hr' hq hq' (1 / 4) (1 / 4) (by norm_num) Rejᶜ hRejm.compl hPA hPB
  have e : (4 : ℝ) * v * (1 - 1 / 4 - 1 / 4) ^ 2 = v := by ring
  rw [e] at hfin
  exact hfin

end CurrentMM
