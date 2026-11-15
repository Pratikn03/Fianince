import CurrentProofs.Paper1KCohortUniform
import Mathlib.Analysis.SpecialFunctions.ExpDeriv
import Mathlib.Analysis.Calculus.MeanValue

/-!
# Paper 1: news of any law, hiding with many groups, the money value of tags

* `p1_exp_neg_le`, `p1_laplace_location_kl`: the location divergence of Laplace news,
  `|Δ|/b - 1 + exp(-|Δ|/b)`, is at most `Δ²/(2b²)`; with variance `σ² = 2b²` this is twice the Gaussian divergence
  `Δ²/(2σ²)` (`prop:nongauss`, the constant `σ² I* = 2`).
* `p1_newslaw_kl_compare`: if a news law's location divergence is at most `(I*/2) Δ²`, then summing over the
  record, its divergence between two economies is at most `σ² I*` times the Gaussian one (the comparison step of
  `prop:nongauss`; the chain-rule identity that writes each divergence as such a sum is on paper).
* `p1_hiding_nash_bound`: in any profile in which every group's choice is a best response, every group's detection
  probability is at most `k_g Δ_g² / L_g` plus the detection probability of its best tight deviation
  (`prop:hidegame`(iv)).
* `p1_tags_value_money`: any price-only procedure that tells the `K`-group pair of `thm:kcohort` apart with errors
  `α₀, β₀` runs at least `4σ²(1-α₀-β₀)²/C²` experiments, so at cost `c_e` per experiment it costs at least that
  times `c_e`; composed with the machine-checked lower bound `p1_thm_kcohort_lower_bound_uniform`.
-/

namespace CurrentMM

open Real Finset MeasureTheory

/-- `exp(-u) ≤ 1 - u + u²/2` for `u ≥ 0`. -/
theorem p1_exp_neg_le (u : ℝ) (hu : 0 ≤ u) : exp (-u) ≤ 1 - u + u ^ 2 / 2 := by
  set g : ℝ → ℝ := fun x => 1 - x + x ^ 2 / 2 - exp (-x) with hg
  have hd : ∀ x, HasDerivAt g (-1 + x + exp (-x)) x := by
    intro x
    have h1 : HasDerivAt (fun y : ℝ => 1 - y + y ^ 2 / 2) (-1 + x) x := by
      have a := ((hasDerivAt_const x (1 : ℝ)).sub (hasDerivAt_id' x)).add ((hasDerivAt_pow 2 x).div_const 2)
      convert a using 1
      norm_num
    have h2 : HasDerivAt (fun y : ℝ => exp (-y)) (exp (-x) * (-1)) x :=
      (Real.hasDerivAt_exp (-x)).comp x (hasDerivAt_neg x)
    convert h1.sub h2 using 1; ring
  have hcont : Continuous g := by
    simp only [hg]; fun_prop
  have hmono : MonotoneOn g (Set.Ici 0) := by
    apply monotoneOn_of_deriv_nonneg (convex_Ici 0) hcont.continuousOn
    · exact fun x _ => (hd x).differentiableAt.differentiableWithinAt
    · intro x _
      rw [(hd x).deriv]
      have := Real.add_one_le_exp (-x); linarith
  have h := hmono (Set.mem_Ici.mpr le_rfl) (Set.mem_Ici.mpr hu) hu
  simp only [hg] at h
  norm_num at h
  linarith

/-- **Laplace news.** The location divergence of the Laplace law with scale `b` is at most `Δ²/(2b²)`. -/
theorem p1_laplace_location_kl (b Δ : ℝ) (hb : 0 < b) :
    |Δ| / b - 1 + exp (-(|Δ| / b)) ≤ Δ ^ 2 / (2 * b ^ 2) := by
  have hu : 0 ≤ |Δ| / b := div_nonneg (abs_nonneg Δ) hb.le
  have h := p1_exp_neg_le (|Δ| / b) hu
  have e : (|Δ| / b) ^ 2 / 2 = Δ ^ 2 / (2 * b ^ 2) := by
    rw [div_pow, sq_abs]; field_simp
  linarith

/-- With variance `σ² = 2b²`, the Laplace bound is twice the Gaussian divergence `Δ²/(2σ²)`. -/
theorem p1_laplace_vs_gaussian (b Δ : ℝ) (hb : 0 < b) :
    |Δ| / b - 1 + exp (-(|Δ| / b)) ≤ 2 * (Δ ^ 2 / (2 * (2 * b ^ 2))) := by
  have := p1_laplace_location_kl b Δ hb
  have e : 2 * (Δ ^ 2 / (2 * (2 * b ^ 2))) = Δ ^ 2 / (2 * b ^ 2) := by field_simp
  linarith

/-- **The comparison step of `prop:nongauss`.** If a news law's location divergence `g` satisfies
`g x ≤ (I*/2) x²`, then the sum over the record of the expected divergences `E g(Δ_t)` is at most `σ² I*` times the
Gaussian sum `∑ E Δ_t² / (2σ²)`. -/
theorem p1_newslaw_kl_compare {Ω ι : Type*} [MeasurableSpace Ω] (μ : Measure Ω) (s : Finset ι)
    (Δ : ι → Ω → ℝ) (g : ℝ → ℝ) (σ2 Istar : ℝ) (hσ : 0 < σ2)
    (hg : ∀ x, g x ≤ Istar / 2 * x ^ 2)
    (hint_g : ∀ t ∈ s, Integrable (fun ω => g (Δ t ω)) μ)
    (hint_sq : ∀ t ∈ s, Integrable (fun ω => Δ t ω ^ 2) μ) :
    ∑ t ∈ s, ∫ ω, g (Δ t ω) ∂μ ≤ σ2 * Istar * ∑ t ∈ s, ∫ ω, Δ t ω ^ 2 / (2 * σ2) ∂μ := by
  rw [Finset.mul_sum]
  refine Finset.sum_le_sum fun t ht => ?_
  calc ∫ ω, g (Δ t ω) ∂μ ≤ ∫ ω, Istar / 2 * Δ t ω ^ 2 ∂μ :=
        integral_mono (hint_g t ht) ((hint_sq t ht).const_mul _) fun ω => hg (Δ t ω)
    _ = σ2 * Istar * ∫ ω, Δ t ω ^ 2 / (2 * σ2) ∂μ := by
        rw [integral_const_mul, integral_div]
        field_simp

/-- **Hiding with many groups (`prop:hidegame`(iv)).** In any profile in which every group's position is a best
response, each group's detection probability is at most `k_g Δ_g²/L_g` plus the detection probability of any
deviation within `Δ_g` of its preferred position. -/
theorem p1_hiding_nash_bound {G : Type*} (k L : G → ℝ) (hk : ∀ g, 0 ≤ k g) (hL : ∀ g, 0 < L g)
    (pos pref dev : G → ℝ) (det detdev Δ : G → ℝ)
    (hopt : ∀ g, k g * (pos g - pref g) ^ 2 + L g * det g ≤ k g * (dev g - pref g) ^ 2 + L g * detdev g)
    (hdev : ∀ g, |dev g - pref g| ≤ Δ g) :
    ∀ g, det g ≤ k g * Δ g ^ 2 / L g + detdev g := by
  intro g
  have h1 : (dev g - pref g) ^ 2 ≤ Δ g ^ 2 := by
    have := hdev g
    have h0 : 0 ≤ |dev g - pref g| := abs_nonneg _
    calc (dev g - pref g) ^ 2 = |dev g - pref g| ^ 2 := (sq_abs _).symm
      _ ≤ Δ g ^ 2 := by gcongr
  have h2 : 0 ≤ k g * (pos g - pref g) ^ 2 := mul_nonneg (hk g) (sq_nonneg _)
  have h3 : k g * (dev g - pref g) ^ 2 ≤ k g * Δ g ^ 2 := mul_le_mul_of_nonneg_left h1 (hk g)
  rw [div_add' _ _ _ (hL g).ne', le_div_iff₀ (hL g)]
  nlinarith [hopt g]

/-- **The money value of composition (`cor:money`).** For the `K`-group pair of `thm:kcohort` (`K = L + 1`), any
price-only procedure with `N` experiments and test errors `α₀ + β₀ < 1` satisfies
`c_e · 4σ²(1-α₀-β₀)²/C_N² ≤ c_e · N`, with `C_N` the constant of `p1_thm_kcohort_lower_bound_uniform` times
`d^{2K-1}`: at cost `c_e` per experiment, learning composition from prices costs at least of order
`c_e σ² (Δη)^{-(4K-2)}`. -/
theorem p1_tags_value_money (L : ℕ) (a κ c d W s : ℝ) (N T : ℕ)
    (q rate q' rate' : Fin (L + 1) → ℝ) (variance : NNReal) (hv : variance ≠ 0)
    (hc : 0 ≤ c) (hd : 0 ≤ d) (hcd0 : 0 < c + d) (hcd : c + d < 1) (hW : 0 ≤ W)
    (hs : |a| + |κ| * (W / (1 - (c + d))) ≤ s) (hs1 : s < 1)
    (hr : ∀ i : Fin (L + 1), 1 - rate i = c + d * gridNode L (2 * (i : ℕ) + 1))
    (hr' : ∀ i : Fin (L + 1), 1 - rate' i = c + d * gridNode L (2 * (i : ℕ)))
    (hq : ∀ i : Fin (L + 1), q i * rate i = W * ((2 * L + 1).choose (2 * (i : ℕ) + 1) : ℝ) / 2 ^ (2 * L))
    (hq' : ∀ i : Fin (L + 1), q' i * rate' i = W * ((2 * L + 1).choose (2 * (i : ℕ)) : ℝ) / 2 ^ (2 * L))
    (α₀ β₀ : ℝ) (hab : α₀ + β₀ ≤ 1) (A : Set (ObservationRecord (N * T))) (hA : MeasurableSet A)
    (herr0 : (gaussianRecordLaw (N * T) (p1RepeatedMean N T (actualCohortImpulse a κ q rate))
      variance).real A ≤ α₀)
    (herr1 : (gaussianRecordLaw (N * T) (p1RepeatedMean N T (actualCohortImpulse a κ q' rate'))
      variance).real Aᶜ ≤ β₀)
    (hpos : 0 < 2 * κ ^ 2 * W / ((1 - (c + d)) ^ (2 * L + 2) * (1 - s) ^ 2) * d ^ (2 * L + 1))
    (ce : ℝ) (hce : 0 ≤ ce) :
    ce * (4 * (variance : ℝ) * (1 - α₀ - β₀) ^ 2 /
        (2 * κ ^ 2 * W / ((1 - (c + d)) ^ (2 * L + 2) * (1 - s) ^ 2) * d ^ (2 * L + 1)) ^ 2) ≤ ce * N := by
  have hlow := p1_thm_kcohort_lower_bound_uniform L a κ c d W s N T q rate q' rate' variance hv hc hd hcd0 hcd
    hW hs hs1 hr hr' hq hq' α₀ β₀ hab A hA herr0 herr1
  apply mul_le_mul_of_nonneg_left _ hce
  rw [div_le_iff₀ (by positivity)]
  exact hlow

end CurrentMM
