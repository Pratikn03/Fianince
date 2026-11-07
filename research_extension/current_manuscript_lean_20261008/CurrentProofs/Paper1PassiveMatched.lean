import CurrentProofs.Paper1PassiveKCohort
import CurrentProofs.Paper1GaussRadau

/-!
# Paper 1, Theorem `prop:passive` (iii): the finite-record passive bound for every moment-matched pair

`p1_thm_passive_cost_every_K` proves the bound for the binomial moment-matched pair. The argument uses only three
facts about a pair of populations:
- nonnegative merged weights with total at most `W`;
- normalized nodes in `[-1, 1]`;
- equal moments below order `J`.

`p1_thm_passive_cost_matched` states it in that generality, for any numbers of cohorts. The paper's `K`-cohort Gauss
and Gauss–Radau economies satisfy these facts with `J = 2K - 1`, because both rules are positive with nodes in
`[-1, 1]` and integrate polynomials of degree `2K - 2` exactly. That is the classical quadrature property, and for
general `K` it enters as the moment hypothesis.

For `K = 2` the Gauss and Gauss–Radau moments are proved in `Paper1GaussRadau.lean`, so
`p1_thm_passive_cost_gauss_radau_two` is unconditional. Records start from rest, after any warm-up `M`.
-/

namespace CurrentMM

open MeasureTheory ProbabilityTheory InformationTheory Finset
open scoped ENNReal NNReal

/-- **Passive cost for any moment-matched pair** (records from rest, after any warm-up `M`). -/
theorem p1_thm_passive_cost_matched {K K' : ℕ} (J : ℕ) (a κ c d W s : ℝ) (hκ : 0 < κ) (hc : 0 ≤ c)
    (hd : 0 ≤ d) (hcd : c + d < 1) (hW0 : 0 ≤ W) (hs : |a| + κ * (W / (1 - (c + d))) ≤ s) (hs1 : s < 1)
    (q rate : Fin K → ℝ) (q' rate' : Fin K' → ℝ) (w sn : Fin K → ℝ) (w' sn' : Fin K' → ℝ)
    (hr : ∀ i, 1 - rate i = c + d * sn i) (hr' : ∀ i, 1 - rate' i = c + d * sn' i)
    (hq : ∀ i, q i * rate i = w i) (hq' : ∀ i, q' i * rate' i = w' i)
    (hw : ∀ i, 0 ≤ w i) (hw' : ∀ i, 0 ≤ w' i) (hsum : ∑ i, w i ≤ W) (hsum' : ∑ i, w' i ≤ W)
    (hsn : ∀ i, |sn i| ≤ 1) (hsn' : ∀ i, |sn' i| ≤ 1)
    (hmom : ∀ j, j < J → ∑ i, w i * sn i ^ j = ∑ i, w' i * sn' i ^ j)
    (M T : ℕ) (v : ℝ≥0) (hv : v ≠ 0) (A : Set (Fin T → ℝ)) (hA : MeasurableSet A)
    (herr1 : (obsLaw M T v (fun j => actualCohortImpulse a κ q rate j / κ)).real A ≤ 1 / 4)
    (herr0 : (obsLaw M T v (fun j => actualCohortImpulse a κ q' rate' j / κ)).real Aᶜ ≤ 1 / 4) :
    1 ≤ 2 * (1 + s) ^ 2 *
      (κ * (2 * W * d ^ J * (1 / (1 - (c + d)) ^ (J + 1))) / (1 - s) ^ 2) ^ 2 * T := by
  have hk : ∀ m, cohortKernel q rate m = ∑ i, w i * (c + d * sn i) ^ m := fun m => by
    simp only [cohortKernel]
    exact sum_congr rfl (fun i _ => by rw [hq i, hr i])
  have hk' : ∀ m, cohortKernel q' rate' m = ∑ i, w' i * (c + d * sn' i) ^ m := fun m => by
    simp only [cohortKernel]
    exact sum_congr rfl (fun i _ => by rw [hq' i, hr' i])
  set K1 := W / (1 - (c + d)) with hK1def
  have hK1 : ∀ N, ∑ m ∈ range N, |cohortKernel q rate m| ≤ K1 := fun N => by
    simp only [hk]; exact p1_population_kernel_l1 w sn c d W hc hd hcd hw hsum hsn N
  have hK1' : ∀ N, ∑ m ∈ range N, |cohortKernel q' rate' m| ≤ K1 := fun N => by
    simp only [hk']; exact p1_population_kernel_l1 w' sn' c d W hc hd hcd hw' hsum' hsn' N
  have hcd' : |c| + d < 1 := by rw [abs_of_nonneg hc]; exact hcd
  set E := 2 * W * d ^ J * (1 / (1 - (c + d)) ^ (J + 1)) with hEdef
  have hE : ∀ N, ∑ m ∈ range N, |cohortKernel q rate m - cohortKernel q' rate' m| ≤ E := fun N => by
    simp only [hk, hk']
    have := p1_matched_kernel_gap_l1 w sn w' sn' c d W J hd hcd' hw hw' hsum hsum' hsn hsn' hmom N
    rwa [abs_of_nonneg hc] at this
  have hstab : |a| + |κ| * K1 ≤ s := by rw [abs_of_pos hκ]; exact hs
  have hH1 := p1_response_l1 a κ K1 s (cohortKernel q' rate') _ (p1_impulse_zero a κ q' rate')
    (p1_impulse_closed_loop_recursion a κ q' rate') hK1' hstab hs1
  have hD := p1_response_diff_l1 a κ K1 s E (|κ| / (1 - s)) (cohortKernel q rate) (cohortKernel q' rate') _ _
    (p1_impulse_zero a κ _ _) (p1_impulse_zero a κ _ _)
    (p1_impulse_closed_loop_recursion a κ _ _) (p1_impulse_closed_loop_recursion a κ _ _)
    hK1 hstab hs1 hE hH1
  -- normalized responses and the passive record
  set g1 : ℕ → ℝ := fun j => actualCohortImpulse a κ q rate j / κ
  set g0 : ℕ → ℝ := fun j => actualCohortImpulse a κ q' rate' j / κ
  have hκ0 : κ ≠ 0 := hκ.ne'
  have hs1' : 0 < 1 - s := by linarith
  have hg0 : g0 0 = 1 := by simp [g0, p1_impulse_zero, hκ0]
  have hg1 : g1 0 = 1 := by simp [g1, p1_impulse_zero, hκ0]
  have hrec0 : ∀ t, g0 (t + 1) = a * g0 t + κ * ∑ j ∈ range (t + 1), cohortKernel q' rate' j * g0 (t - j) := by
    intro t
    simp only [g0]
    rw [p1_impulse_closed_loop_recursion, add_div, mul_sum, mul_sum, sum_div]
    congr 1
    · ring
    · exact sum_congr rfl (fun j _ => by field_simp)
  have hrg := p1_closed_loop_reciprocal a κ _ g0 hg0 hrec0
  have hDr := p1_clRecip_l1 a κ K1 (cohortKernel q' rate') hK1'
  set E1 := κ * E / (1 - s) ^ 2 with hE1def
  have hEg : ∀ N, ∑ m ∈ range N, |g1 m - g0 m| ≤ E1 := by
    intro N
    have e : ∀ m, |g1 m - g0 m| = |actualCohortImpulse a κ q rate m - actualCohortImpulse a κ q' rate' m| / κ := by
      intro m; simp only [g1, g0]; rw [← sub_div, abs_div, abs_of_pos hκ]
    simp only [e, ← sum_div]
    rw [div_le_iff₀ hκ]
    calc _ ≤ |κ| * E * (|κ| / (1 - s)) / (1 - s) := hD N
      _ = E1 * κ := by rw [abs_of_pos hκ, hE1def]; field_simp
  have hkl := p1_passive_record_kl M T v hv g0 g1 _ (1 + |a| + |κ| * K1) E1 hrg hg0 hg1 hDr hEg
  have hlow := p1_test_error_kl_lower_bound _ _ hA herr1 herr0
  have h14 := hlow.trans hkl
  rw [ENNReal.ofReal_le_ofReal_iff (by positivity)] at h14
  have hDs : 1 + |a| + |κ| * K1 ≤ 1 + s := by linarith
  have hK10 : 0 ≤ K1 := div_nonneg hW0 (by linarith)
  have hD0 : 0 ≤ 1 + |a| + |κ| * K1 := by positivity
  have hsq : (1 + |a| + |κ| * K1) ^ 2 ≤ (1 + s) ^ 2 := pow_le_pow_left₀ hD0 hDs 2
  have hT : (0 : ℝ) ≤ T := Nat.cast_nonneg T
  nlinarith [mul_le_mul_of_nonneg_right hsq (by positivity : (0 : ℝ) ≤ T * E1 ^ 2)]


/-- **The paper's two-cohort Gauss and Gauss–Radau economies.** Both have normalized nodes `c + d s` with the Gauss
nodes `∓1/√3` and the Gauss–Radau nodes `-1, 1/3`, and merged weights `W/2, W/2` and `W/4, 3W/4`. Their moments
agree below order three (proved, not assumed), so passive observation needs
`T ≥ 1/(2(1+s)²(C d³)²)`. -/
theorem p1_thm_passive_cost_gauss_radau_two (a κ c d W s : ℝ) (hκ : 0 < κ) (hc : 0 ≤ c) (hd : 0 ≤ d)
    (hcd : c + d < 1) (hW0 : 0 ≤ W) (hs : |a| + κ * (W / (1 - (c + d))) ≤ s) (hs1 : s < 1)
    (q rate q' rate' : Fin 2 → ℝ)
    (hr : ∀ i, 1 - rate i = c + d * grGNode i) (hr' : ∀ i, 1 - rate' i = c + d * grRNode i)
    (hq : ∀ i, q i * rate i = W * grGWeight i) (hq' : ∀ i, q' i * rate' i = W * grRWeight i)
    (M T : ℕ) (v : ℝ≥0) (hv : v ≠ 0) (A : Set (Fin T → ℝ)) (hA : MeasurableSet A)
    (herr1 : (obsLaw M T v (fun j => actualCohortImpulse a κ q rate j / κ)).real A ≤ 1 / 4)
    (herr0 : (obsLaw M T v (fun j => actualCohortImpulse a κ q' rate' j / κ)).real Aᶜ ≤ 1 / 4) :
    1 ≤ 2 * (1 + s) ^ 2 *
      (κ * (2 * W * d ^ 3 * (1 / (1 - (c + d)) ^ (3 + 1))) / (1 - s) ^ 2) ^ 2 * T := by
  obtain ⟨hGpos, hRpos⟩ := p1_gr_positive_weights
  obtain ⟨hGsum, hRsum⟩ := p1_gr_normalized_weights
  obtain ⟨hGb, hRb⟩ := p1_gr_node_bounds
  refine p1_thm_passive_cost_matched 3 a κ c d W s hκ hc hd hcd hW0 hs hs1 q rate q' rate'
    (fun i => W * grGWeight i) grGNode (fun i => W * grRWeight i) grRNode hr hr' hq hq'
    (fun i => mul_nonneg hW0 (hGpos i).le) (fun i => mul_nonneg hW0 (hRpos i).le)
    (by show ∑ i, W * grGWeight i ≤ W; rw [← mul_sum, hGsum, mul_one])
    (by show ∑ i, W * grRWeight i ≤ W; rw [← mul_sum, hRsum, mul_one]) hGb hRb
    (fun j hj => p1_gr_three_matched_moments W j hj) M T v hv A hA herr1 herr0

end CurrentMM
