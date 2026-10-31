import CurrentProofs.Paper1PassiveRecord
import Mathlib.InformationTheory.KullbackLeibler.DataProcessing

/-!
# Paper 1, Theorem 5.8 (`prop:passive`) (i): passive data cost `T = Ω(δ^{-4})`

The market of Theorem 3.1 (ii) (a single cohort at `η̄` against two at `η̄ ± δ`, same total weight, all rates in
`[ε, 1-ε]`, `a ≥ 0`, `κ > 0`, `a + κ q ≤ s < 1`) is driven by i.i.d. `N(0, v)` price innovations and has run for any
number `M` of periods from rest before the observer starts. The observer records the next `T` prices, without
trading and without observation noise. Any test whose two error probabilities are at most `1/4` needs
`T ≥ 1 / (2 (1+s)² C² δ⁴)` with `C = 2 κ q / (ε³ (1 - s)²)`, whatever `M`.

* `p1_passive_record_kl`: the divergence of the observed prices is at most `½ ‖r‖₁² T ‖g₁ - g₀‖₁²`
  (data processing, the factorization `A₀ B = A₁`, and `p1_kl_triangular_gaussian`);
* `p1_closed_loop_reciprocal`: the closed loop's response has reciprocal series `1, -(a + κ k₀), -κ k₁, …`, so
  `‖r‖₁ ≤ 1 + |a| + |κ| ‖k‖₁` (no separate minimum-phase argument is needed);
* `p1_thm_passive_cost`: the sample bound.
-/

namespace CurrentMM

open MeasureTheory ProbabilityTheory InformationTheory Finset Matrix
open scoped ENNReal NNReal

/-- The observer sees the last `T` coordinates of the record. -/
def obsMap (M T : ℕ) (y : Fin (M + T) → ℝ) : Fin T → ℝ := fun t => y ⟨M + t, by omega⟩

theorem p1_measurable_obsMap (M T : ℕ) : Measurable (obsMap M T) :=
  measurable_pi_iff.mpr (fun _ => measurable_pi_apply _)

/-- Law of the `T` observed prices of a market started from rest `M` periods earlier. -/
noncomputable def obsLaw (M T : ℕ) (v : ℝ≥0) (g : ℕ → ℝ) : Measure (Fin T → ℝ) :=
  ((iidGauss (M + T) v).map (recMat M T g).mulVec).map (obsMap M T)

instance (M T : ℕ) (v : ℝ≥0) (g : ℕ → ℝ) : IsProbabilityMeasure (obsLaw M T v g) := by
  unfold obsLaw; infer_instance

/-- The observed price at time `t` is `∑_{σ ≤ M + t} g(M + t - σ) ξ_σ`: the response of a market at rest to the
innovations. -/
theorem p1_obsMap_recMat (M T : ℕ) (g : ℕ → ℝ) (ξ : Fin (M + T) → ℝ) (t : Fin T) :
    obsMap M T ((recMat M T g).mulVec ξ) t = ∑ σ : Fin (M + T), (if (σ : ℕ) ≤ M + t then g (M + t - σ) else 0) * ξ σ := by
  simp [obsMap, recMat, recN, Matrix.mulVec, dotProduct]

/-- **Divergence of the observed prices.** -/
theorem p1_passive_record_kl (M T : ℕ) (v : ℝ≥0) (hv : v ≠ 0) (g0 g1 r : ℕ → ℝ) (D E1 : ℝ)
    (hrg : IsReciprocal r g0) (hg0 : g0 0 = 1) (hg1 : g1 0 = 1)
    (hD : ∀ N, ∑ m ∈ range N, |r m| ≤ D) (hE : ∀ N, ∑ m ∈ range N, |g1 m - g0 m| ≤ E1) :
    klDiv (obsLaw M T v g1) (obsLaw M T v g0) ≤ ENNReal.ofReal (1 / 2 * (D ^ 2 * T * E1 ^ 2)) := by
  set P := iidGauss (M + T) v
  have hdg0 : (fun j => g1 j - g0 j) 0 = 0 := by simp [hg0, hg1]
  have hfac := p1_recording_factor M T g0 g1 r hrg hg0 hg1
  have hmap : P.map (recMat M T g1).mulVec =
      (P.map (corrMat M T r (fun j => g1 j - g0 j)).mulVec).map (recMat M T g0).mulVec := by
    rw [Measure.map_map (p1_measurable_mulVec _) (p1_measurable_mulVec _)]
    congr 1
    funext x
    simp only [Function.comp, Matrix.mulVec_mulVec]
    rw [hfac]
  calc klDiv (obsLaw M T v g1) (obsLaw M T v g0)
      ≤ klDiv (P.map (recMat M T g1).mulVec) (P.map (recMat M T g0).mulVec) :=
        klDiv_map_le _ _ (p1_measurable_obsMap M T)
    _ = klDiv ((P.map (corrMat M T r (fun j => g1 j - g0 j)).mulVec).map (recMat M T g0).mulVec)
          (P.map (recMat M T g0).mulVec) := by rw [hmap]
    _ ≤ klDiv (P.map (corrMat M T r (fun j => g1 j - g0 j)).mulVec) P := klDiv_map_le _ _ (p1_measurable_mulVec _)
    _ = ENNReal.ofReal (1 / 2 * ∑ i, ∑ j, (corrMat M T r (fun j => g1 j - g0 j) - 1) i j ^ 2) :=
        p1_kl_triangular_gaussian v hv _ (p1_corrMat_lower M T r _ hdg0) (p1_corrMat_diag M T r _ hdg0)
    _ ≤ ENNReal.ofReal (1 / 2 * (D ^ 2 * T * E1 ^ 2)) := by
        apply ENNReal.ofReal_le_ofReal
        apply mul_le_mul_of_nonneg_left _ (by norm_num)
        have hentry : ∀ i j : Fin (M + T), (corrMat M T r (fun j => g1 j - g0 j) - 1) i j =
            corrN M r (fun j => g1 j - g0 j) i j := by
          intro i j
          simp only [corrMat, Matrix.sub_apply, Matrix.one_apply]
          ring
        simp only [hentry]
        rw [Fin.sum_univ_eq_sum_range (fun i => ∑ j : Fin (M + T), corrN M r (fun j => g1 j - g0 j) i j ^ 2)]
        have hin : ∀ i : ℕ, ∑ j : Fin (M + T), corrN M r (fun j => g1 j - g0 j) i j ^ 2 =
            ∑ j ∈ range (M + T), corrN M r (fun j => g1 j - g0 j) i j ^ 2 := fun i =>
          Fin.sum_univ_eq_sum_range (fun j => corrN M r (fun j => g1 j - g0 j) i j ^ 2) _
        simp only [hin]
        rw [sum_comm]
        exact p1_recording_frobenius_N M T r _ D E1 hdg0 hD hE

/-- Reciprocal series of a closed-loop response with first tap `1`. -/
noncomputable def clRecip (a κ : ℝ) (k : ℕ → ℝ) : ℕ → ℝ
  | 0 => 1
  | 1 => -(a + κ * k 0)
  | m + 2 => -(κ * k (m + 1))

/-- **The closed loop's response is invertible with an explicit reciprocal.** -/
theorem p1_closed_loop_reciprocal (a κ : ℝ) (k g : ℕ → ℝ) (hg0 : g 0 = 1)
    (hrec : ∀ t, g (t + 1) = a * g t + κ * ∑ j ∈ range (t + 1), k j * g (t - j)) :
    IsReciprocal (clRecip a κ k) g := by
  intro m
  rcases m with _ | t
  · simp [clRecip, hg0]
  · rw [sum_range_succ', sum_range_succ']
    simp only [clRecip, Nat.sub_zero, add_tsub_cancel_right, if_neg (Nat.succ_ne_zero t)]
    have hs : ∑ i ∈ range t, -(κ * k (i + 1)) * g (t + 1 - (i + 1 + 1)) =
        -κ * ∑ i ∈ range t, k (i + 1) * g (t - (i + 1)) := by
      rw [mul_sum]; exact sum_congr rfl (fun i _ => by rw [show t + 1 - (i + 1 + 1) = t - (i + 1) by omega]; ring)
    rw [hs, hrec t, sum_range_succ' (fun j => k j * g (t - j))]
    simp only [Nat.sub_zero]
    ring

theorem p1_clRecip_l1 (a κ K1 : ℝ) (k : ℕ → ℝ) (hK1 : ∀ N, ∑ m ∈ range N, |k m| ≤ K1) :
    ∀ N, ∑ m ∈ range N, |clRecip a κ k m| ≤ 1 + |a| + |κ| * K1 := by
  have hK10 : 0 ≤ K1 := by simpa using hK1 0
  intro N
  rcases N with _ | _ | N
  · simp only [range_zero, sum_empty]; positivity
  · rw [zero_add, sum_range_one]
    simp only [clRecip, abs_one]
    linarith [abs_nonneg a, mul_nonneg (abs_nonneg κ) hK10]
  · rw [sum_range_succ', sum_range_succ']
    simp only [clRecip, abs_neg, abs_one]
    have h1 : |a + κ * k 0| ≤ |a| + |κ| * |k 0| := by
      rw [← abs_mul]; exact abs_add_le _ _
    have h2 : ∑ i ∈ range N, |κ * k (i + 1)| = |κ| * ∑ i ∈ range N, |k (i + 1)| := by
      rw [mul_sum]; exact sum_congr rfl (fun i _ => abs_mul _ _)
    have h3 : |k 0| + ∑ i ∈ range N, |k (i + 1)| ≤ K1 := by
      have := hK1 (N + 1)
      rw [sum_range_succ'] at this
      linarith
    rw [h2]
    nlinarith [abs_nonneg κ]

/-- `ℓ₁` gap between the responses of the split pair and the single cohort (as in Theorem 3.1 (ii)). -/
theorem p1_split_response_gap (a κ q ηbar δ ε s : ℝ) (ha : 0 ≤ a) (hκ : 0 < κ) (hq : 0 ≤ q)
    (hε : 0 < ε) (hδ : 0 < δ) (hlo : ε ≤ ηbar - δ) (hhi : ηbar + δ ≤ 1 - ε)
    (hs : a + κ * q ≤ s) (hs1 : s < 1) :
    (∀ n, ∑ m ∈ range n, |cohortKernel ![q] ![ηbar] m| ≤ q) ∧
    ∀ n, ∑ t ∈ range n, |actualCohortImpulse a κ ![q / 2, q / 2] ![ηbar - δ, ηbar + δ] t -
      actualCohortImpulse a κ ![q] ![ηbar] t| ≤ 2 * κ ^ 2 * q / (ε ^ 3 * (1 - s) ^ 2) * δ ^ 2 := by
  have hkδ : ∀ m, cohortKernel ![q / 2, q / 2] ![ηbar - δ, ηbar + δ] m =
      q / 2 * (ηbar - δ) * (1 - (ηbar - δ)) ^ m + q / 2 * (ηbar + δ) * (1 - (ηbar + δ)) ^ m := by
    intro m; simp [cohortKernel, Fin.sum_univ_two]
  have hk0 : ∀ m, cohortKernel ![q] ![ηbar] m = q * ηbar * (1 - ηbar) ^ m := by
    intro m; simp [cohortKernel]
  have hη0 : 0 ≤ ηbar - δ := by linarith
  have hKδ : ∀ n, ∑ m ∈ range n, |cohortKernel ![q / 2, q / 2] ![ηbar - δ, ηbar + δ] m| ≤ q := by
    intro n
    simp only [hkδ]
    calc ∑ m ∈ range n, |q / 2 * (ηbar - δ) * (1 - (ηbar - δ)) ^ m + q / 2 * (ηbar + δ) * (1 - (ηbar + δ)) ^ m|
        ≤ ∑ m ∈ range n, (|q / 2 * (ηbar - δ) * (1 - (ηbar - δ)) ^ m| +
            |q / 2 * (ηbar + δ) * (1 - (ηbar + δ)) ^ m|) := sum_le_sum (fun m _ => abs_add_le _ _)
      _ ≤ q / 2 + q / 2 := by
          rw [sum_add_distrib]
          exact add_le_add (p1_single_kernel_l1 _ _ (by positivity) hη0 (by linarith) n)
            (p1_single_kernel_l1 _ _ (by positivity) (by linarith) (by linarith) n)
      _ = q := by ring
  have hK0 : ∀ n, ∑ m ∈ range n, |cohortKernel ![q] ![ηbar] m| ≤ q := by
    intro n; simp only [hk0]
    exact p1_single_kernel_l1 _ _ hq (by linarith) (by linarith) n
  refine ⟨hK0, ?_⟩
  have hstab : |a| + |κ| * q ≤ s := by rw [abs_of_nonneg ha, abs_of_pos hκ]; exact hs
  have hH1 := p1_response_l1 a κ q s (cohortKernel ![q] ![ηbar]) _ (p1_impulse_zero a κ ![q] ![ηbar])
    (p1_impulse_closed_loop_recursion a κ ![q] ![ηbar]) hK0 hstab hs1
  have hE : ∀ n, ∑ m ∈ range n, |cohortKernel ![q / 2, q / 2] ![ηbar - δ, ηbar + δ] m -
      cohortKernel ![q] ![ηbar] m| ≤ 2 * q * δ ^ 2 / ε ^ 3 := by
    intro n; simp only [hkδ, hk0]
    exact p1_split_kernel_gap q ηbar δ ε hq hε hδ.le hlo hhi n
  have hD := p1_response_diff_l1 a κ q s (2 * q * δ ^ 2 / ε ^ 3) (|κ| / (1 - s))
    (cohortKernel ![q / 2, q / 2] ![ηbar - δ, ηbar + δ]) (cohortKernel ![q] ![ηbar]) _ _
    (p1_impulse_zero a κ _ _) (p1_impulse_zero a κ _ _)
    (p1_impulse_closed_loop_recursion a κ _ _) (p1_impulse_closed_loop_recursion a κ _ _)
    hKδ hstab hs1 hE hH1
  have hs1' : 0 < 1 - s := by linarith
  intro n
  refine (hD n).trans (le_of_eq ?_)
  rw [abs_of_pos hκ]; field_simp

/-- **Theorem 5.8 (i), formal version.** Passive observation of `T` prices of the market of Theorem 3.1 (ii),
started from rest any number `M` of periods earlier and driven by i.i.d. `N(0, v)` innovations: any test with both
error probabilities at most `1/4` needs `1 ≤ 2 (1+s)² C² δ⁴ T`, `C = 2 κ q / (ε³ (1-s)²)`; that is,
`T ≥ 1 / (2 (1+s)² C² δ⁴) = Ω(δ^{-4})`, uniformly in `M`. -/
theorem p1_thm_passive_cost (a κ q ηbar δ ε s : ℝ) (ha : 0 ≤ a) (hκ : 0 < κ) (hq : 0 ≤ q)
    (hε : 0 < ε) (hδ : 0 < δ) (hlo : ε ≤ ηbar - δ) (hhi : ηbar + δ ≤ 1 - ε)
    (hs : a + κ * q ≤ s) (hs1 : s < 1) (M T : ℕ) (v : ℝ≥0) (hv : v ≠ 0)
    (A : Set (Fin T → ℝ)) (hA : MeasurableSet A)
    (herrδ : (obsLaw M T v (fun j => actualCohortImpulse a κ ![q / 2, q / 2] ![ηbar - δ, ηbar + δ] j / κ)).real A ≤ 1 / 4)
    (herr0 : (obsLaw M T v (fun j => actualCohortImpulse a κ ![q] ![ηbar] j / κ)).real Aᶜ ≤ 1 / 4) :
    1 ≤ 2 * (1 + s) ^ 2 * (2 * κ * q / (ε ^ 3 * (1 - s) ^ 2)) ^ 2 * δ ^ 4 * T := by
  set g1 : ℕ → ℝ := fun j => actualCohortImpulse a κ ![q / 2, q / 2] ![ηbar - δ, ηbar + δ] j / κ
  set g0 : ℕ → ℝ := fun j => actualCohortImpulse a κ ![q] ![ηbar] j / κ
  obtain ⟨hK0, hgap⟩ := p1_split_response_gap a κ q ηbar δ ε s ha hκ hq hε hδ hlo hhi hs hs1
  have hκ0 : κ ≠ 0 := hκ.ne'
  have hg0 : g0 0 = 1 := by simp [g0, p1_impulse_zero, hκ0]
  have hg1 : g1 0 = 1 := by simp [g1, p1_impulse_zero, hκ0]
  have hrec0 : ∀ t, g0 (t + 1) = a * g0 t + κ * ∑ j ∈ range (t + 1), cohortKernel ![q] ![ηbar] j * g0 (t - j) := by
    intro t
    simp only [g0]
    rw [p1_impulse_closed_loop_recursion, add_div, mul_sum, mul_sum, sum_div]
    congr 1
    · ring
    · exact sum_congr rfl (fun j _ => by field_simp)
  have hrg := p1_closed_loop_reciprocal a κ _ g0 hg0 hrec0
  have hD := p1_clRecip_l1 a κ q (cohortKernel ![q] ![ηbar]) hK0
  set C := 2 * κ * q / (ε ^ 3 * (1 - s) ^ 2) with hC
  have hE : ∀ N, ∑ m ∈ range N, |g1 m - g0 m| ≤ C * δ ^ 2 := by
    intro N
    have h := hgap N
    have e : ∀ m, |g1 m - g0 m| = |actualCohortImpulse a κ ![q / 2, q / 2] ![ηbar - δ, ηbar + δ] m -
        actualCohortImpulse a κ ![q] ![ηbar] m| / κ := by
      intro m; simp only [g1, g0]; rw [← sub_div, abs_div, abs_of_pos hκ]
    simp only [e, ← sum_div]
    rw [div_le_iff₀ hκ]
    calc _ ≤ 2 * κ ^ 2 * q / (ε ^ 3 * (1 - s) ^ 2) * δ ^ 2 := h
      _ = C * δ ^ 2 * κ := by rw [hC]; field_simp
  have hkl := p1_passive_record_kl M T v hv g0 g1 _ (1 + |a| + |κ| * q) (C * δ ^ 2) hrg hg0 hg1 hD hE
  have hlow := p1_test_error_kl_lower_bound _ _ hA herrδ herr0
  have h14 : ENNReal.ofReal (1 / 4) ≤ ENNReal.ofReal (1 / 2 * ((1 + |a| + |κ| * q) ^ 2 * T * (C * δ ^ 2) ^ 2)) :=
    hlow.trans hkl
  rw [ENNReal.ofReal_le_ofReal_iff (by positivity)] at h14
  have hDs : 1 + |a| + |κ| * q ≤ 1 + s := by rw [abs_of_nonneg ha, abs_of_pos hκ]; linarith
  have hD0 : 0 ≤ 1 + |a| + |κ| * q := by positivity
  have hsq : (1 + |a| + |κ| * q) ^ 2 ≤ (1 + s) ^ 2 := pow_le_pow_left₀ hD0 hDs 2
  have hT : (0 : ℝ) ≤ T := Nat.cast_nonneg T
  nlinarith [mul_le_mul_of_nonneg_right hsq (by positivity : (0 : ℝ) ≤ T * (C * δ ^ 2) ^ 2)]

end CurrentMM
