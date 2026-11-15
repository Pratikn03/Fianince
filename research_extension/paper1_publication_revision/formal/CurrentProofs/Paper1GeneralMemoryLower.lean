import CurrentProofs.Paper1PassiveKCohort
import CurrentProofs.Paper1LowerBound
import Mathlib.Analysis.SpecialFunctions.Trigonometric.Bounds

/-!
# Paper 1, Theorem 5.6 (i): with general memory no estimator beats `1 / log(N/σ²)`

General memory: the feedback kernel is `k_m = ∫_{[0,ρ]} r^m dμ(r)` for a nonnegative measure `μ` of mass `W`.
The lower bound uses two finite members of the class, so the whole argument is finite-dimensional.

* `p1_gm_kernel_gap_l1`: two populations whose rates `c + d s` (`c, d ≥ 0`, `ρ = c + d < 1`) have equal weighted
  moments below order `J` have equal kernels below lag `J` and kernels within `2 W ρ^J / (1 - ρ)` in `ℓ₁` over all
  lags (raw-moment bound, no binomial factor);
* `gmWitness`, `p1_gmWitness_lipschitz`, `p1_gmWitness_node`: on the grid `r_k = h k` the scaled cosine
  `f(r) = (h/π)(1 - cos(π r / h))` is 1-Lipschitz, vanishes at `0`, and equals `0` on even nodes and `2h/π` on odd
  nodes. It replaces the best approximation of `|x|` (Bernstein's constant) in the paper's Lemma `lem:altpair`;
* `p1_thm_general_memory_lower_L`: the binomial moment-matched pair with `L + 1` cohorts each, placed at the rates
  `ρ k/(2L+1)` of `[0, ρ]`, has separation `∫ f dμ_A - ∫ f dμ_B = 2 ρ W / (π (2L+1))`. Any estimator whose
  integrals of every 1-Lipschitz `f` with `f(0) = 0` are within half of that, with probability `≥ 3/4` under both
  economies, forces `σ² ≤ 2 N (C ρ^(2L+1))²` with `C = 2 κ² W / ((1-ρ)(1-s)²)`, uniformly in the horizon `T`;
* `p1_thm_general_memory_lower`: choosing `L = ⌈Λ / (4 log(1/ρ))⌉` with `Λ = log(2 N C² / σ²) > 0`, no estimator
  attains accuracy `2 ρ W log(1/ρ) / (π (Λ + 6 log(1/ρ)))` with probability `≥ 3/4` under both economies: the
  paper's `1 / log(N/σ²)` lower bound with explicit constants.

An estimator `μ̂` of the memory measure enters through `est x f = ∫ f dμ̂(x)`; the paper's distance
`d(μ̂, μ) = sup_f |∫ f d(μ̂ - μ)|` below `ε` implies the accuracy event used here, so the bound applies to it.
-/

namespace CurrentMM

open MeasureTheory ProbabilityTheory InformationTheory Finset Real
open scoped ENNReal NNReal

/-- A population with rates `c + d s_i`, `|s_i| ≤ 1`, has `|k_m| ≤ W (c + d)^m`. -/
theorem p1_gm_pop_abs_le {ι : Type*} [Fintype ι] (w s : ι → ℝ) (c d W : ℝ) (hc : 0 ≤ c) (hd : 0 ≤ d)
    (hw : ∀ i, 0 ≤ w i) (hW : ∑ i, w i ≤ W) (hs : ∀ i, |s i| ≤ 1) (m : ℕ) :
    |∑ i, w i * (c + d * s i) ^ m| ≤ W * (c + d) ^ m := by
  have hr : ∀ i, |c + d * s i| ≤ c + d := fun i => by
    calc |c + d * s i| ≤ |c| + |d * s i| := abs_add_le _ _
      _ = c + d * |s i| := by rw [abs_of_nonneg hc, abs_mul, abs_of_nonneg hd]
      _ ≤ c + d * 1 := by gcongr; exact hs i
      _ = c + d := by ring
  calc |∑ i, w i * (c + d * s i) ^ m| ≤ ∑ i, w i * (c + d) ^ m := by
        refine (abs_sum_le_sum_abs _ _).trans (sum_le_sum (fun i _ => ?_))
        rw [abs_mul, abs_of_nonneg (hw i), abs_pow]
        exact mul_le_mul_of_nonneg_left (pow_le_pow_left₀ (abs_nonneg _) (hr i) m) (hw i)
    _ = (∑ i, w i) * (c + d) ^ m := by rw [sum_mul]
    _ ≤ W * (c + d) ^ m := mul_le_mul_of_nonneg_right hW (by positivity)

/-- **Raw-moment kernel gap.** Equal moments below order `J` give equal kernels below lag `J`, and an `ℓ₁` gap of at
most `2 W ρ^J / (1 - ρ)` over every horizon. -/
theorem p1_gm_kernel_gap_l1 {ι κι : Type*} [Fintype ι] [Fintype κι] (w s : ι → ℝ) (w' s' : κι → ℝ)
    (c d W : ℝ) (J : ℕ) (hc : 0 ≤ c) (hd : 0 ≤ d) (hcd : c + d < 1) (hw : ∀ i, 0 ≤ w i) (hw' : ∀ i, 0 ≤ w' i)
    (hW : ∑ i, w i ≤ W) (hW' : ∑ i, w' i ≤ W) (hs : ∀ i, |s i| ≤ 1) (hs' : ∀ i, |s' i| ≤ 1)
    (hmom : ∀ j, j < J → ∑ i, w i * s i ^ j = ∑ i, w' i * s' i ^ j) (N : ℕ) :
    ∑ m ∈ range N, |∑ i, w i * (c + d * s i) ^ m - ∑ i, w' i * (c + d * s' i) ^ m| ≤
      2 * W * (c + d) ^ J / (1 - (c + d)) := by
  set ρ := c + d with hρ
  have hρ0 : 0 ≤ ρ := by positivity
  have hW0 : 0 ≤ W := le_trans (sum_nonneg (fun i _ => hw i)) hW
  have hpt : ∀ m, |∑ i, w i * (c + d * s i) ^ m - ∑ i, w' i * (c + d * s' i) ^ m| ≤
      if J ≤ m then 2 * W * ρ ^ m else 0 := by
    intro m
    split_ifs with hJm
    · calc _ ≤ |∑ i, w i * (c + d * s i) ^ m| + |∑ i, w' i * (c + d * s' i) ^ m| := abs_sub _ _
        _ ≤ W * ρ ^ m + W * ρ ^ m :=
            add_le_add (p1_gm_pop_abs_le w s c d W hc hd hw hW hs m)
              (p1_gm_pop_abs_le w' s' c d W hc hd hw' hW' hs' m)
        _ = 2 * W * ρ ^ m := by ring
    · have h := p1_matched_kernel_gap w s w' s' c d W J hd hw hw' hW hW' hs hs' hmom m
      rwa [if_neg hJm] at h
  refine (sum_le_sum (fun m _ => hpt m)).trans ?_
  have hgeom := p1_geom_partial_le ρ hρ0 hcd (N - J)
  have h1ρ : 0 < 1 - ρ := by linarith
  by_cases hNJ : J ≤ N
  · rw [← sum_range_add_sum_Ico _ hNJ]
    have hz : ∑ m ∈ range J, (if J ≤ m then 2 * W * ρ ^ m else 0) = 0 :=
      sum_eq_zero (fun m hm => by rw [if_neg (by have := mem_range.mp hm; omega)])
    rw [hz, zero_add, sum_Ico_eq_sum_range]
    have e : ∑ n ∈ range (N - J), (if J ≤ J + n then 2 * W * ρ ^ (J + n) else 0) =
        2 * W * ρ ^ J * ∑ n ∈ range (N - J), ρ ^ n := by
      rw [mul_sum]
      exact sum_congr rfl (fun n _ => by rw [if_pos (by omega), pow_add]; ring)
    rw [e, mul_div_assoc]
    calc 2 * W * ρ ^ J * ∑ n ∈ range (N - J), ρ ^ n ≤ 2 * W * ρ ^ J * (1 / (1 - ρ)) :=
          mul_le_mul_of_nonneg_left hgeom (by positivity)
      _ = 2 * W * (ρ ^ J / (1 - ρ)) := by ring
  · rw [sum_eq_zero (fun m hm => by rw [if_neg (by have := mem_range.mp hm; omega)])]
    exact div_nonneg (by positivity) h1ρ.le

/-- The binomial grid placed on `[0, ρ]`: node `k` sits at rate `ρ k / (2L+1)`. -/
theorem p1_gm_rate_node (ρ : ℝ) (L k : ℕ) : ρ / 2 + ρ / 2 * gridNode L k = ρ * k / (2 * L + 1) := by
  unfold gridNode
  have hpos : (2 * (L : ℝ) + 1) ≠ 0 := by positivity
  field_simp
  ring

/-- The separating test function: a cosine with half-period equal to the node spacing `h`. -/
noncomputable def gmWitness (h r : ℝ) : ℝ := h / π * (1 - cos (π * r / h))

theorem p1_gmWitness_zero (h : ℝ) : gmWitness h 0 = 0 := by
  simp [gmWitness]

theorem p1_gmWitness_lipschitz (h : ℝ) (hh : 0 < h) : LipschitzWith 1 (gmWitness h) := by
  refine LipschitzWith.of_dist_le_mul (fun x y => ?_)
  rw [Real.dist_eq, Real.dist_eq, NNReal.coe_one, one_mul]
  unfold gmWitness
  have hπ : 0 < π := pi_pos
  have e : h / π * (1 - cos (π * x / h)) - h / π * (1 - cos (π * y / h)) =
      h / π * (cos (π * y / h) - cos (π * x / h)) := by ring
  rw [e, abs_mul, abs_of_pos (div_pos hh hπ)]
  calc h / π * |cos (π * y / h) - cos (π * x / h)| ≤ h / π * |π * y / h - π * x / h| :=
        mul_le_mul_of_nonneg_left (abs_cos_sub_cos_le _ _) (div_pos hh hπ).le
    _ = h / π * (π / h * |x - y|) := by
        congr 1
        rw [show π * y / h - π * x / h = π / h * (y - x) by ring, abs_mul, abs_of_pos (div_pos hπ hh),
          abs_sub_comm]
    _ = |x - y| := by field_simp

theorem p1_gmWitness_node (h : ℝ) (hh : h ≠ 0) (k : ℕ) : gmWitness h (h * k) = h / π * (1 - (-1) ^ k) := by
  unfold gmWitness
  rw [show π * (h * k) / h = k * π by field_simp, cos_nat_mul_pi]

/-- Total weight of each half of the binomial pair. -/
theorem p1_gm_pair_mass (L : ℕ) (W : ℝ) :
    ∑ i : Fin (L + 1), W * ((2 * L + 1).choose (2 * (i : ℕ) + 1) : ℝ) / 2 ^ (2 * L) = W ∧
      ∑ i : Fin (L + 1), W * ((2 * L + 1).choose (2 * (i : ℕ)) : ℝ) / 2 ^ (2 * L) = W := by
  have hpow : (0 : ℝ) < 2 ^ (2 * L) := by positivity
  obtain ⟨hodd, heven⟩ := p1_grid_half_weight L
  constructor
  · rw [Fin.sum_univ_eq_sum_range (fun i => W * ((2 * L + 1).choose (2 * i + 1) : ℝ) / 2 ^ (2 * L)),
      ← sum_div, ← mul_sum, hodd, mul_div_assoc, div_self hpow.ne', mul_one]
  · rw [Fin.sum_univ_eq_sum_range (fun i => W * ((2 * L + 1).choose (2 * i) : ℝ) / 2 ^ (2 * L)),
      ← sum_div, ← mul_sum, heven, mul_div_assoc, div_self hpow.ne', mul_one]

/-- Equal weighted grid moments of every order `≤ 2L` for the binomial pair. -/
theorem p1_gm_pair_moments (L : ℕ) (W : ℝ) (j : ℕ) (hj : j < 2 * L + 1) :
    ∑ i : Fin (L + 1), W * ((2 * L + 1).choose (2 * (i : ℕ) + 1) : ℝ) / 2 ^ (2 * L) *
        gridNode L (2 * i + 1) ^ j =
      ∑ i : Fin (L + 1), W * ((2 * L + 1).choose (2 * (i : ℕ)) : ℝ) / 2 ^ (2 * L) * gridNode L (2 * i) ^ j := by
  rw [Fin.sum_univ_eq_sum_range (fun i => W * ((2 * L + 1).choose (2 * i + 1) : ℝ) / 2 ^ (2 * L) *
      gridNode L (2 * i + 1) ^ j),
    Fin.sum_univ_eq_sum_range (fun i => W * ((2 * L + 1).choose (2 * i) : ℝ) / 2 ^ (2 * L) *
      gridNode L (2 * i) ^ j)]
  have hm := p1_grid_matched_moments L j hj
  have e : ∀ (f : ℕ → ℝ) (g : ℕ → ℕ), ∑ i ∈ range (L + 1), W * f i / 2 ^ (2 * L) * gridNode L (g i) ^ j =
      W / 2 ^ (2 * L) * ∑ i ∈ range (L + 1), f i * gridNode L (g i) ^ j := by
    intro f g; rw [mul_sum]; exact sum_congr rfl (fun i _ => by ring)
  rw [e (fun i => ((2 * L + 1).choose (2 * i + 1) : ℝ)) (fun i => 2 * i + 1),
    e (fun i => ((2 * L + 1).choose (2 * i) : ℝ)) (fun i => 2 * i), hm]

/-- **Theorem 5.6 (i), formal, for a fixed number `L + 1` of cohorts.**
Economy `A` puts merged weight `W C(2L+1, 2i+1) / 2^(2L)` at memory rate `ρ (2i+1)/(2L+1)`, economy `B` puts
`W C(2L+1, 2i) / 2^(2L)` at `ρ (2i)/(2L+1)` (`i = 0, …, L`); both lie in the class `𝓜(ρ, W)` and the closed loop
is stable, `|a| + κ W/(1-ρ) ≤ s < 1`. From `N` reset experiments of `T` taps with noise variance `σ²`, any
estimator whose integrals of every 1-Lipschitz `f` with `f(0) = 0` are within `ρ W / (π (2L+1))` of the truth with
probability at least `3/4` under both economies forces `σ² ≤ 2 N (C ρ^(2L+1))²`, `C = 2 κ² W / ((1-ρ)(1-s)²)`. -/
theorem p1_thm_general_memory_lower_L (L : ℕ) (a κ ρ W s : ℝ) (hκ : 0 < κ) (hρ0 : 0 < ρ) (hρ1 : ρ < 1)
    (hW0 : 0 ≤ W) (hs : |a| + κ * (W / (1 - ρ)) ≤ s) (hs1 : s < 1)
    (q rate q' rate' : Fin (L + 1) → ℝ)
    (hr : ∀ i : Fin (L + 1), 1 - rate i = ρ * (2 * ((i : ℕ) : ℝ) + 1) / (2 * L + 1))
    (hr' : ∀ i : Fin (L + 1), 1 - rate' i = ρ * (2 * ((i : ℕ) : ℝ)) / (2 * L + 1))
    (hq : ∀ i : Fin (L + 1), q i * rate i = W * ((2 * L + 1).choose (2 * (i : ℕ) + 1) : ℝ) / 2 ^ (2 * L))
    (hq' : ∀ i : Fin (L + 1), q' i * rate' i = W * ((2 * L + 1).choose (2 * (i : ℕ)) : ℝ) / 2 ^ (2 * L))
    (N T : ℕ) (v : ℝ≥0) (hv : v ≠ 0)
    (est : ObservationRecord (N * T) → (ℝ → ℝ) → ℝ) (hest : ∀ f, Measurable (fun x => est x f))
    (hsuccA : 3 / 4 ≤ (gaussianRecordLaw (N * T) (p1RepeatedMean N T (actualCohortImpulse a κ q rate)) v).real
      {x | ∀ f : ℝ → ℝ, LipschitzWith 1 f → f 0 = 0 →
        |est x f - ∑ i, q i * rate i * f (1 - rate i)| < ρ * W / (π * (2 * L + 1))})
    (hsuccB : 3 / 4 ≤ (gaussianRecordLaw (N * T) (p1RepeatedMean N T (actualCohortImpulse a κ q' rate')) v).real
      {x | ∀ f : ℝ → ℝ, LipschitzWith 1 f → f 0 = 0 →
        |est x f - ∑ i, q' i * rate' i * f (1 - rate' i)| < ρ * W / (π * (2 * L + 1))}) :
    (v : ℝ) ≤ 2 * N * (2 * κ ^ 2 * W / ((1 - ρ) * (1 - s) ^ 2) * ρ ^ (2 * L + 1)) ^ 2 := by
  -- the two populations on the grid
  set w : Fin (L + 1) → ℝ := fun i => q i * rate i with hwdef
  set w' : Fin (L + 1) → ℝ := fun i => q' i * rate' i with hw'def
  set sn : Fin (L + 1) → ℝ := fun i => gridNode L (2 * i + 1)
  set sn' : Fin (L + 1) → ℝ := fun i => gridNode L (2 * i)
  obtain ⟨hmA, hmB⟩ := p1_gm_pair_mass L W
  have hw : ∀ i, 0 ≤ w i := fun i => by simp only [w]; rw [hq i]; positivity
  have hw' : ∀ i, 0 ≤ w' i := fun i => by simp only [w']; rw [hq' i]; positivity
  have hsumE : ∑ i, w i = W := by simp only [w, hq]; exact hmA
  have hsumE' : ∑ i, w' i = W := by simp only [w', hq']; exact hmB
  have hsn : ∀ i, |sn i| ≤ 1 := fun i => p1_gridNode_abs_le L _ (by omega)
  have hsn' : ∀ i, |sn' i| ≤ 1 := fun i => p1_gridNode_abs_le L _ (by omega)
  have hmom : ∀ j, j < 2 * L + 1 → ∑ i, w i * sn i ^ j = ∑ i, w' i * sn' i ^ j := by
    intro j hj
    simp only [w, w', sn, sn', hq, hq']
    exact p1_gm_pair_moments L W j hj
  have hnode : ∀ i : Fin (L + 1), 1 - rate i = ρ / 2 + ρ / 2 * sn i := fun i => by
    simp only [sn]; rw [p1_gm_rate_node, hr i]; push_cast; ring
  have hnode' : ∀ i : Fin (L + 1), 1 - rate' i = ρ / 2 + ρ / 2 * sn' i := fun i => by
    simp only [sn']; rw [p1_gm_rate_node, hr' i]; push_cast; ring
  have hk : ∀ m, cohortKernel q rate m = ∑ i, w i * (ρ / 2 + ρ / 2 * sn i) ^ m := fun m => by
    simp only [cohortKernel, w]
    exact sum_congr rfl (fun i _ => by rw [hnode i])
  have hk' : ∀ m, cohortKernel q' rate' m = ∑ i, w' i * (ρ / 2 + ρ / 2 * sn' i) ^ m := fun m => by
    simp only [cohortKernel, w']
    exact sum_congr rfl (fun i _ => by rw [hnode' i])
  have hρ2 : (0 : ℝ) ≤ ρ / 2 := by positivity
  have hcd : ρ / 2 + ρ / 2 < 1 := by linarith
  have hhalf : ρ / 2 + ρ / 2 = ρ := by ring
  -- kernel bounds
  set K1 := W / (1 - ρ) with hK1def
  have hK1 : ∀ n, ∑ m ∈ range n, |cohortKernel q rate m| ≤ K1 := fun n => by
    simp only [hk]
    have := p1_population_kernel_l1 w sn (ρ / 2) (ρ / 2) W hρ2 hρ2 hcd hw hsumE.le hsn n
    rwa [hhalf] at this
  have hK1' : ∀ n, ∑ m ∈ range n, |cohortKernel q' rate' m| ≤ K1 := fun n => by
    simp only [hk']
    have := p1_population_kernel_l1 w' sn' (ρ / 2) (ρ / 2) W hρ2 hρ2 hcd hw' hsumE'.le hsn' n
    rwa [hhalf] at this
  set E := 2 * W * ρ ^ (2 * L + 1) / (1 - ρ) with hEdef
  have hE : ∀ n, ∑ m ∈ range n, |cohortKernel q rate m - cohortKernel q' rate' m| ≤ E := fun n => by
    simp only [hk, hk']
    have := p1_gm_kernel_gap_l1 w sn w' sn' (ρ / 2) (ρ / 2) W (2 * L + 1) hρ2 hρ2 hcd hw hw'
      hsumE.le hsumE'.le hsn hsn' hmom n
    rwa [hhalf] at this
  -- closed-loop responses
  have hstab : |a| + |κ| * K1 ≤ s := by rw [abs_of_pos hκ]; exact hs
  have hH1 := p1_response_l1 a κ K1 s (cohortKernel q' rate') _ (p1_impulse_zero a κ q' rate')
    (p1_impulse_closed_loop_recursion a κ q' rate') hK1' hstab hs1
  have hD := p1_response_diff_l1 a κ K1 s E (|κ| / (1 - s)) (cohortKernel q rate) (cohortKernel q' rate') _ _
    (p1_impulse_zero a κ _ _) (p1_impulse_zero a κ _ _)
    (p1_impulse_closed_loop_recursion a κ _ _) (p1_impulse_closed_loop_recursion a κ _ _)
    hK1 hstab hs1 hE hH1
  set hA := actualCohortImpulse a κ q rate
  set hB := actualCohortImpulse a κ q' rate'
  set C := 2 * κ ^ 2 * W / ((1 - ρ) * (1 - s) ^ 2) with hCdef
  have h1s : 0 < 1 - s := by linarith
  have h1ρ : 0 < 1 - ρ := by linarith
  have hDval : |κ| * E * (|κ| / (1 - s)) / (1 - s) = C * ρ ^ (2 * L + 1) := by
    rw [abs_of_pos hκ, hEdef, hCdef]; field_simp
  have hC0 : 0 ≤ C * ρ ^ (2 * L + 1) := by rw [hCdef]; positivity
  have hsq : ∑ t ∈ range T, (hB t - hA t) ^ 2 ≤ (C * ρ ^ (2 * L + 1)) ^ 2 := by
    refine (p1_sq_sum_le_sq_abs_sum _ _).trans (pow_le_pow_left₀ (sum_nonneg (fun _ _ => abs_nonneg _)) ?_ 2)
    have := hD T
    rw [hDval] at this
    refine le_trans (le_of_eq (sum_congr rfl (fun t _ => abs_sub_comm _ _))) this
  -- the separating functional
  set hh := ρ / (2 * L + 1) with hhdef
  have hhpos : 0 < hh := by positivity
  set ε := ρ * W / (π * (2 * L + 1)) with hεdef
  set f := gmWitness hh
  have hfL := p1_gmWitness_lipschitz hh hhpos
  have hf0 := p1_gmWitness_zero hh
  have hΦA : ∑ i, q i * rate i * f (1 - rate i) = 2 * ε := by
    have e : ∀ i : Fin (L + 1), q i * rate i * f (1 - rate i) = w i * (2 * (hh / π)) := fun i => by
      have hpt : 1 - rate i = hh * ((2 * (i : ℕ) + 1 : ℕ) : ℝ) := by rw [hr i, hhdef]; push_cast; ring
      simp only [w, f]
      rw [hpt, p1_gmWitness_node hh hhpos.ne', pow_succ, pow_mul]
      rw [neg_one_sq, one_pow]; ring
    rw [sum_congr rfl (fun i _ => e i), ← sum_mul, hsumE, hεdef, hhdef]
    field_simp
  have hΦB : ∑ i, q' i * rate' i * f (1 - rate' i) = 0 := by
    refine sum_eq_zero (fun i _ => ?_)
    have hpt : 1 - rate' i = hh * ((2 * (i : ℕ) : ℕ) : ℝ) := by rw [hr' i, hhdef]; push_cast; ring
    simp only [f]
    rw [hpt, p1_gmWitness_node hh hhpos.ne', pow_mul]
    simp
  -- the test
  set PA := gaussianRecordLaw (N * T) (p1RepeatedMean N T hA) v
  set PB := gaussianRecordLaw (N * T) (p1RepeatedMean N T hB) v
  set Rej := {x : ObservationRecord (N * T) | |est x f - 2 * ε| < ε} with hRej
  have hRejm : MeasurableSet Rej :=
    measurableSet_lt (continuous_abs.measurable.comp ((hest f).sub measurable_const)) measurable_const
  have hAsub : {x | ∀ g : ℝ → ℝ, LipschitzWith 1 g → g 0 = 0 →
      |est x g - ∑ i, q i * rate i * g (1 - rate i)| < ε} ⊆ Rej := by
    intro x hx
    have := hx f hfL hf0
    rw [hΦA] at this
    exact this
  have hBsub : {x | ∀ g : ℝ → ℝ, LipschitzWith 1 g → g 0 = 0 →
      |est x g - ∑ i, q' i * rate' i * g (1 - rate' i)| < ε} ⊆ Rejᶜ := by
    intro x hx hxR
    have h1 := hx f hfL hf0
    rw [hΦB, sub_zero] at h1
    have h2 : |est x f - 2 * ε| < ε := hxR
    have := abs_sub_abs_le_abs_sub (2 * ε) (est x f)
    rw [abs_sub_comm] at h2
    have hε0 : 0 ≤ ε := by rw [hεdef]; positivity
    rw [abs_of_nonneg (by linarith : (0 : ℝ) ≤ 2 * ε)] at this
    linarith
  have hPA : PA.real Rejᶜ ≤ 1 / 4 := by
    have h1 : 3 / 4 ≤ PA.real Rej := hsuccA.trans (measureReal_mono hAsub)
    rw [measureReal_compl hRejm, probReal_univ]
    linarith
  have hPB : PB.real Rej ≤ 1 / 4 := by
    have h1 : 3 / 4 ≤ PB.real Rejᶜ := hsuccB.trans (measureReal_mono hBsub)
    rw [measureReal_compl hRejm, probReal_univ] at h1
    linarith
  have htest := p1_test_error_kl_lower_bound PB PA hRejm hPB hPA
  rw [p1_repeated_record_kl N T hB hA v hv] at htest
  have hvpos : 0 < (v : ℝ) := by positivity
  have hle := (ENNReal.ofReal_le_ofReal_iff (by positivity)).mp htest
  rw [le_div_iff₀ (by positivity)] at hle
  have hN : (0 : ℝ) ≤ N := Nat.cast_nonneg N
  nlinarith [mul_le_mul_of_nonneg_left hsq hN]

/-- **Theorem 5.6 (i), formal, logarithmic form.** Let `C = 2 κ² W / ((1-ρ)(1-s)²)`,
`Λ = log(2 N C² / σ²) > 0` and `ℓ = log(1/ρ)`, and use `L + 1` cohorts with `L = ⌈Λ / (4ℓ)⌉`. For the pair of
`p1_thm_general_memory_lower_L`, no estimator attains accuracy `2 ρ W ℓ / (π (Λ + 6ℓ))` (in every 1-Lipschitz test
function vanishing at `0`) with probability at least `3/4` under both economies. The accuracy is of order
`ρ W log(1/ρ) / log(N/σ²)`, the paper's lower bound, uniformly in the horizon `T`. -/
theorem p1_thm_general_memory_lower (a κ ρ W s : ℝ) (hκ : 0 < κ) (hρ0 : 0 < ρ) (hρ1 : ρ < 1)
    (hW : 0 < W) (hs : |a| + κ * (W / (1 - ρ)) ≤ s) (hs1 : s < 1) (N T : ℕ) (v : ℝ≥0) (hv : v ≠ 0)
    (hΛ : 0 < Real.log (2 * N * (2 * κ ^ 2 * W / ((1 - ρ) * (1 - s) ^ 2)) ^ 2 / v))
    (L : ℕ) (hL : L = ⌈Real.log (2 * N * (2 * κ ^ 2 * W / ((1 - ρ) * (1 - s) ^ 2)) ^ 2 / v) /
      (4 * Real.log ρ⁻¹)⌉₊)
    (q rate q' rate' : Fin (L + 1) → ℝ)
    (hr : ∀ i : Fin (L + 1), 1 - rate i = ρ * (2 * ((i : ℕ) : ℝ) + 1) / (2 * L + 1))
    (hr' : ∀ i : Fin (L + 1), 1 - rate' i = ρ * (2 * ((i : ℕ) : ℝ)) / (2 * L + 1))
    (hq : ∀ i : Fin (L + 1), q i * rate i = W * ((2 * L + 1).choose (2 * (i : ℕ) + 1) : ℝ) / 2 ^ (2 * L))
    (hq' : ∀ i : Fin (L + 1), q' i * rate' i = W * ((2 * L + 1).choose (2 * (i : ℕ)) : ℝ) / 2 ^ (2 * L))
    (est : ObservationRecord (N * T) → (ℝ → ℝ) → ℝ) (hest : ∀ f, Measurable (fun x => est x f)) :
    ¬ (3 / 4 ≤ (gaussianRecordLaw (N * T) (p1RepeatedMean N T (actualCohortImpulse a κ q rate)) v).real
        {x | ∀ f : ℝ → ℝ, LipschitzWith 1 f → f 0 = 0 →
          |est x f - ∑ i, q i * rate i * f (1 - rate i)| <
            2 * ρ * W * Real.log ρ⁻¹ /
              (π * (Real.log (2 * N * (2 * κ ^ 2 * W / ((1 - ρ) * (1 - s) ^ 2)) ^ 2 / v) +
                6 * Real.log ρ⁻¹))} ∧
      3 / 4 ≤ (gaussianRecordLaw (N * T) (p1RepeatedMean N T (actualCohortImpulse a κ q' rate')) v).real
        {x | ∀ f : ℝ → ℝ, LipschitzWith 1 f → f 0 = 0 →
          |est x f - ∑ i, q' i * rate' i * f (1 - rate' i)| <
            2 * ρ * W * Real.log ρ⁻¹ /
              (π * (Real.log (2 * N * (2 * κ ^ 2 * W / ((1 - ρ) * (1 - s) ^ 2)) ^ 2 / v) +
                6 * Real.log ρ⁻¹))}) := by
  set C := 2 * κ ^ 2 * W / ((1 - ρ) * (1 - s) ^ 2) with hCdef
  set Λ := Real.log (2 * N * C ^ 2 / v) with hΛdef
  set ℓ := Real.log ρ⁻¹ with hℓdef
  have hℓ : 0 < ℓ := Real.log_pos (one_lt_inv₀ hρ0 |>.mpr hρ1)
  have hℓρ : Real.log ρ = -ℓ := by rw [hℓdef, Real.log_inv, neg_neg]
  have hvpos : 0 < (v : ℝ) := by positivity
  have hx1 : 1 < 2 * N * C ^ 2 / v := by
    by_contra hcon
    push Not at hcon
    have hx0 : 0 ≤ 2 * N * C ^ 2 / v := by positivity
    have := Real.log_nonpos hx0 hcon
    linarith
  have hNC : (v : ℝ) < 2 * N * C ^ 2 := by rwa [one_lt_div hvpos] at hx1
  have hNC0 : 0 < 2 * N * C ^ 2 := lt_trans hvpos hNC
  -- the choice of `L`
  have harg : 0 ≤ Λ / (4 * ℓ) := div_nonneg hΛ.le (by positivity)
  have hL1 : Λ / (4 * ℓ) ≤ L := by rw [hL]; exact Nat.le_ceil _
  have hL2 : (L : ℝ) < Λ / (4 * ℓ) + 1 := by rw [hL]; exact Nat.ceil_lt_add_one harg
  have hL1' : Λ ≤ 4 * L * ℓ := by
    rw [div_le_iff₀ (by positivity)] at hL1; linarith
  have hL2' : 4 * L * ℓ < Λ + 4 * ℓ := by
    have := (lt_div_iff₀ (by positivity : (0 : ℝ) < 4 * ℓ)).mp (by linarith : (L : ℝ) - 1 < Λ / (4 * ℓ))
    nlinarith
  -- `2 N C² ρ^(4L+2) < σ²`
  have hpowL : ρ ^ (4 * L) ≤ v / (2 * N * C ^ 2) := by
    have e1 : ρ ^ (4 * L) = Real.exp ((4 * L : ℕ) * Real.log ρ) := by
      rw [← Real.log_pow, Real.exp_log (by positivity)]
    have e2 : (v : ℝ) / (2 * N * C ^ 2) = Real.exp (-Λ) := by
      rw [Real.exp_neg, hΛdef, Real.exp_log (by positivity), inv_div]
    rw [e1, e2, Real.exp_le_exp, hℓρ]
    push_cast
    nlinarith
  have hρsq : ρ ^ 2 < 1 := by nlinarith
  have hpow : ρ ^ (4 * L + 2) < v / (2 * N * C ^ 2) := by
    rw [pow_add]
    have : 0 < ρ ^ (4 * L) := by positivity
    calc ρ ^ (4 * L) * ρ ^ 2 < ρ ^ (4 * L) * 1 := mul_lt_mul_of_pos_left hρsq this
      _ ≤ v / (2 * N * C ^ 2) := by rw [mul_one]; exact hpowL
  have hcontra : 2 * N * (C * ρ ^ (2 * L + 1)) ^ 2 < v := by
    have e : 2 * N * (C * ρ ^ (2 * L + 1)) ^ 2 = 2 * N * C ^ 2 * ρ ^ (4 * L + 2) := by
      rw [mul_pow, ← pow_mul]; ring_nf
    rw [e]
    calc 2 * N * C ^ 2 * ρ ^ (4 * L + 2) < 2 * N * C ^ 2 * (v / (2 * N * C ^ 2)) :=
          mul_lt_mul_of_pos_left hpow hNC0
      _ = v := by
          have hN0 : (N : ℝ) ≠ 0 := by rintro h; rw [h] at hNC0; simp at hNC0
          have hCne : C ≠ 0 := by rintro h; rw [h] at hNC0; simp at hNC0
          field_simp
  -- the target accuracy is at most the pair's half-separation
  have hεle : 2 * ρ * W * ℓ / (π * (Λ + 6 * ℓ)) ≤ ρ * W / (π * (2 * L + 1)) := by
    have hπ : 0 < π := pi_pos
    rw [div_le_div_iff₀ (by positivity) (by positivity)]
    have hρW : 0 < ρ * W * π := by positivity
    nlinarith [mul_lt_mul_of_pos_left hL2' hρW]
  rintro ⟨hA, hB⟩
  have hA' := hA.trans (measureReal_mono (fun x hx g hg hg0 => lt_of_lt_of_le (hx g hg hg0) hεle))
  have hB' := hB.trans (measureReal_mono (fun x hx g hg hg0 => lt_of_lt_of_le (hx g hg hg0) hεle))
  have := p1_thm_general_memory_lower_L L a κ ρ W s hκ hρ0 hρ1 hW.le hs hs1 q rate q' rate' hr hr' hq hq'
    N T v hv est hest hA' hB'
  linarith

end CurrentMM
