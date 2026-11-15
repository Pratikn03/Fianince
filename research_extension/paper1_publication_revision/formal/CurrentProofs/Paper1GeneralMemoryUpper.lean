import CurrentProofs.Paper1JacksonPoly
import CurrentProofs.Paper1PronyUpper
import CurrentProofs.Paper1PassiveKCohort

/-!
# Paper 1, Theorem 5.6 (ii): the moment estimator attains the `1 / log(N/σ²)` rate

* `p1_gm_moment_comparison`: for finite measures `μ, ν` on `[0, ρ]` whose moments of order `≤ n` differ by at most
  `δ`, every `f` that is 1-Lipschitz on `[0, ρ]` with `f(0) = 0` satisfies
  `|∫ f dν - ∫ f dμ| ≤ ρπ/(2(n+2)) (ν(ℝ) + μ(ℝ)) + ρ (n+1) B^n δ`, `B = (1 + 2/ρ)(1 + √2)`
  (the explicit Jackson theorem of `Paper1Jackson*.lean` applied to `f(ρ(1+x)/2)`);
* `p1_deconv_error_explicit`: deconvolution of observed taps within `ε ≤ 1` recovers kernel value `t` within
  `α ε (1 + β)^t`, with `α, β` explicit in `(a, κ, ‖k‖₁, ‖h‖_∞)`;
* `p1_thm_general_memory_upper`: with `N` reset experiments and sub-Gaussian noise, with probability at least
  `1 - β`, every measure on `[0, ρ]` that fits the first `L + 1` estimated kernel values at least as well as the
  truth (up to `η`) is within the stated distance of the true memory measure, in every 1-Lipschitz test function
  vanishing at `0`.
-/

namespace CurrentMM

open MeasureTheory ProbabilityTheory Finset Real Polynomial
open scoped ENNReal NNReal

/-! ### Measures supported on `[0, ρ]` -/

theorem p1_ae_mem_Icc (μ : Measure ℝ) (ρ : ℝ) (hμ : μ (Set.Icc 0 ρ)ᶜ = 0) : ∀ᵐ r ∂μ, r ∈ Set.Icc 0 ρ := by
  rw [ae_iff]; exact hμ

theorem p1_integrable_of_supp (μ : Measure ℝ) [IsFiniteMeasure μ] (ρ : ℝ) (hμ : μ (Set.Icc 0 ρ)ᶜ = 0)
    (F : ℝ → ℝ) (hF : ContinuousOn F (Set.Icc 0 ρ)) : Integrable F μ := by
  have h := hF.integrableOn_compact isCompact_Icc (μ := μ)
  rwa [IntegrableOn, Measure.restrict_eq_self_of_ae_mem (p1_ae_mem_Icc μ ρ hμ)] at h

theorem p1_integral_poly (μ : Measure ℝ) [IsFiniteMeasure μ] (ρ : ℝ) (hμ : μ (Set.Icc 0 ρ)ᶜ = 0)
    (q : ℝ[X]) (N : ℕ) (hq : q.natDegree < N) :
    ∫ r, q.eval r ∂μ = ∑ i ∈ range N, q.coeff i * ∫ r, r ^ i ∂μ := by
  simp_rw [eval_eq_sum_range' hq]
  rw [integral_finset_sum]
  · exact sum_congr rfl (fun i _ => integral_const_mul _ _)
  · intro i _
    exact (p1_integrable_of_supp μ ρ hμ _ ((continuous_pow i).continuousOn)).const_mul _

/-- **Moment comparison.** -/
theorem p1_gm_moment_comparison (ρ : ℝ) (hρ : 0 < ρ) (n : ℕ) (μ ν : Measure ℝ) [IsFiniteMeasure μ]
    [IsFiniteMeasure ν] (hμ : μ (Set.Icc 0 ρ)ᶜ = 0) (hν : ν (Set.Icc 0 ρ)ᶜ = 0) (δ : ℝ)
    (hmom : ∀ i < n + 1, |∫ r, r ^ i ∂ν - ∫ r, r ^ i ∂μ| ≤ δ)
    (f : ℝ → ℝ) (hf : LipschitzOnWith 1 f (Set.Icc 0 ρ)) (hf0 : f 0 = 0) :
    |∫ r, f r ∂ν - ∫ r, f r ∂μ| ≤
      ρ * π / (2 * (n + 2)) * (ν.real Set.univ + μ.real Set.univ) +
        ρ * (n + 1) * ((2 / ρ + 1) * (1 + Real.sqrt 2)) ^ n * δ := by
  have hδ : 0 ≤ δ := le_trans (abs_nonneg _) (hmom 0 (by omega))
  set g : ℝ → ℝ := fun x => f (ρ * (1 + x) / 2) with hgdef
  have hmem : ∀ x ∈ Set.Icc (-1 : ℝ) 1, ρ * (1 + x) / 2 ∈ Set.Icc 0 ρ := by
    intro x hx
    constructor
    · have := hx.1; nlinarith
    · have := hx.2; nlinarith
  have hfd : ∀ a ∈ Set.Icc 0 ρ, ∀ b ∈ Set.Icc 0 ρ, |f a - f b| ≤ |a - b| := by
    intro a ha b hb
    have := hf.dist_le_mul a ha b hb
    simpa [Real.dist_eq] using this
  have hgL : ∀ x ∈ Set.Icc (-1 : ℝ) 1, ∀ y ∈ Set.Icc (-1 : ℝ) 1, |g x - g y| ≤ ρ / 2 * |x - y| := by
    intro x hx y hy
    refine (hfd _ (hmem x hx) _ (hmem y hy)).trans (le_of_eq ?_)
    rw [show ρ * (1 + x) / 2 - ρ * (1 + y) / 2 = ρ / 2 * (x - y) by ring, abs_mul, abs_of_pos (by positivity)]
  have hgB : ∀ x ∈ Set.Icc (-1 : ℝ) 1, |g x| ≤ ρ := by
    intro x hx
    have h0 : (0 : ℝ) ∈ Set.Icc 0 ρ := ⟨le_rfl, hρ.le⟩
    have := hfd _ (hmem x hx) 0 h0
    rw [hf0, sub_zero, sub_zero] at this
    refine this.trans ?_
    have hm := hmem x hx
    rw [abs_of_nonneg hm.1]; exact hm.2
  set lin : ℝ[X] := C (2 / ρ) * X + C (-1) with hlin
  set q : ℝ[X] := (jpoly n g).comp lin with hq
  have hqdeg : q.natDegree < n + 1 := by
    have h1 : lin.natDegree ≤ 1 := natDegree_linear_le
    have h2 := p1_jpoly_natDegree n g
    have := (natDegree_comp_le (p := jpoly n g) (q := lin))
    nlinarith
  set E := ρ / 2 * (π / (n + 2)) with hE
  have happrox : ∀ r ∈ Set.Icc 0 ρ, |q.eval r - f r| ≤ E := by
    intro r hr
    have hx : 2 / ρ * r + -1 ∈ Set.Icc (-1 : ℝ) 1 := by
      constructor
      · have : 0 ≤ 2 / ρ * r := by have := hr.1; positivity
        linarith
      · have : 2 / ρ * r ≤ 2 := by rw [div_mul_eq_mul_div, div_le_iff₀ hρ]; nlinarith [hr.2]
        linarith
    have hj := p1_jackson n g (ρ / 2) (by positivity) hgL _ hx
    have hev : q.eval r = (jpoly n g).eval (2 / ρ * r + -1) := by
      simp [q, lin, eval_comp]
    have hgr : g (2 / ρ * r + -1) = f r := by
      simp only [g]; congr 1; field_simp; ring
    rw [hev, ← hgr]; exact hj
  -- integrability
  have hfc : ContinuousOn f (Set.Icc 0 ρ) := hf.continuousOn
  have hqc : ContinuousOn (fun r => q.eval r) (Set.Icc 0 ρ) := (Polynomial.continuous q).continuousOn
  have hIfμ := p1_integrable_of_supp μ ρ hμ f hfc
  have hIfν := p1_integrable_of_supp ν ρ hν f hfc
  have hIqμ := p1_integrable_of_supp μ ρ hμ _ hqc
  have hIqν := p1_integrable_of_supp ν ρ hν _ hqc
  -- the approximation part
  have happ : ∀ (m : Measure ℝ) [IsFiniteMeasure m], m (Set.Icc 0 ρ)ᶜ = 0 →
      |∫ r, (f r - q.eval r) ∂m| ≤ E * m.real Set.univ := by
    intro m _ hm
    have := norm_integral_le_of_norm_le_const (μ := m) (f := fun r => f r - q.eval r) (C := E)
      ((p1_ae_mem_Icc m ρ hm).mono (fun r hr => by
        rw [Real.norm_eq_abs, abs_sub_comm]; exact happrox r hr))
    simpa [Real.norm_eq_abs] using this
  -- the moment part
  have hpoly : |∫ r, q.eval r ∂ν - ∫ r, q.eval r ∂μ| ≤ ρ * (n + 1) * ((2 / ρ + 1) * (1 + Real.sqrt 2)) ^ n * δ := by
    rw [p1_integral_poly ν ρ hν q (n + 1) hqdeg, p1_integral_poly μ ρ hμ q (n + 1) hqdeg, ← sum_sub_distrib]
    have hcl : cl1 (n + 1) q ≤ ρ * (n + 1) * ((2 / ρ + 1) * (1 + Real.sqrt 2)) ^ n := by
      have h := p1_jpoly_comp_cl1 n g ρ hρ.le hgB (2 / ρ) (-1) (by rw [abs_neg, abs_one, abs_of_pos (by positivity)]; linarith [show 0 < 2 / ρ by positivity])
      rwa [abs_neg, abs_one, abs_of_pos (by positivity : (0 : ℝ) < 2 / ρ)] at h
    calc |∑ i ∈ range (n + 1), (q.coeff i * ∫ r, r ^ i ∂ν - q.coeff i * ∫ r, r ^ i ∂μ)|
        ≤ ∑ i ∈ range (n + 1), |q.coeff i| * δ := by
          refine (abs_sum_le_sum_abs _ _).trans (sum_le_sum (fun i hi => ?_))
          rw [← mul_sub, abs_mul]
          exact mul_le_mul_of_nonneg_left (hmom i (mem_range.mp hi)) (abs_nonneg _)
      _ = cl1 (n + 1) q * δ := by rw [cl1, sum_mul]
      _ ≤ _ := mul_le_mul_of_nonneg_right hcl hδ
  have hsplit : ∫ r, f r ∂ν - ∫ r, f r ∂μ =
      ∫ r, (f r - q.eval r) ∂ν - ∫ r, (f r - q.eval r) ∂μ + (∫ r, q.eval r ∂ν - ∫ r, q.eval r ∂μ) := by
    rw [integral_sub hIfν hIqν, integral_sub hIfμ hIqμ]; ring
  rw [hsplit]
  have h1 := happ ν hν
  have h2 := happ μ hμ
  have hEeq : ρ * π / (2 * (n + 2)) = E := by rw [hE]; field_simp
  rw [hEeq]
  calc |∫ r, (f r - q.eval r) ∂ν - ∫ r, (f r - q.eval r) ∂μ + (∫ r, q.eval r ∂ν - ∫ r, q.eval r ∂μ)|
      ≤ |∫ r, (f r - q.eval r) ∂ν| + |∫ r, (f r - q.eval r) ∂μ| + |∫ r, q.eval r ∂ν - ∫ r, q.eval r ∂μ| := by
        refine (abs_add_le _ _).trans ?_
        gcongr
        exact abs_sub _ _
    _ ≤ E * ν.real Set.univ + E * μ.real Set.univ + ρ * (n + 1) * ((2 / ρ + 1) * (1 + Real.sqrt 2)) ^ n * δ := by
        gcongr
    _ = E * (ν.real Set.univ + μ.real Set.univ) + ρ * (n + 1) * ((2 / ρ + 1) * (1 + Real.sqrt 2)) ^ n * δ := by ring

/-! ### Explicit deconvolution error -/

/-- **Deconvolution with explicit constants.** If the true response has `|h_t| ≤ H`, the kernel has `ℓ₁` norm at
most `K₁`, and the observed taps are within `ε ≤ 1` of the truth up to `T + 1`, then kernel value `t ≤ T` is
recovered within `α ε (1 + β)^t`, `α = (1 + |a| + |κ| K₁)/κ²`, `β = |κ|(H + 1)/κ²`. -/
theorem p1_deconv_error_explicit (a κ H K1 : ℝ) (hκ : κ ≠ 0) (k h hh : ℕ → ℝ) (h0 : h 0 = κ)
    (hrec : ∀ t, h (t + 1) = a * h t + κ * ∑ j ∈ range (t + 1), k j * h (t - j))
    (hH : ∀ t, |h t| ≤ H) (hK1 : ∀ n, ∑ m ∈ range n, |k m| ≤ K1) (T : ℕ) (ε : ℝ) (hε0 : 0 ≤ ε) (hε1 : ε ≤ 1)
    (hclose : ∀ t ≤ T + 1, |hh t - h t| ≤ ε) :
    ∀ t ≤ T, |deconv a κ hh t - k t| ≤
      (1 + |a| + |κ| * K1) / κ ^ 2 * ε * (1 + |κ| * (H + 1) / κ ^ 2) ^ t := by
  have hκ2 : 0 < κ ^ 2 := by positivity
  have hH0 : 0 ≤ H := le_trans (abs_nonneg _) (hH 0)
  have hK10 : 0 ≤ K1 := by simpa using hK1 0
  set α := (1 + |a| + |κ| * K1) / κ ^ 2 with hα
  set β := |κ| * (H + 1) / κ ^ 2 with hβ
  have hα0 : 0 ≤ α := by positivity
  have hβ0 : 0 ≤ β := by positivity
  have htrue : ∀ t, k t = (h (t + 1) - a * h t - κ * ∑ j ∈ range t, k j * h (t - j)) / κ ^ 2 := by
    intro t
    rw [hrec t, sum_range_succ, Nat.sub_self, h0]
    field_simp; ring
  intro t ht
  induction t using Nat.strong_induction_on with
  | _ t ih =>
    have hprev : ∀ j ∈ range t, |deconv a κ hh j - k j| ≤ α * ε * (1 + β) ^ j :=
      fun j hj => ih j (mem_range.mp hj) (by have := mem_range.mp hj; omega)
    have hhb : ∀ j ∈ range t, |hh (t - j)| ≤ H + 1 := by
      intro j hj
      have h1 := hclose (t - j) (by omega)
      calc |hh (t - j)| ≤ |h (t - j)| + |hh (t - j) - h (t - j)| := by
            have := abs_add_le (h (t - j)) (hh (t - j) - h (t - j)); simpa using this
        _ ≤ H + 1 := add_le_add (hH _) (h1.trans hε1)
    have hsum : |∑ j ∈ range t, deconv a κ hh j * hh (t - j) - ∑ j ∈ range t, k j * h (t - j)| ≤
        (H + 1) * ∑ j ∈ range t, α * ε * (1 + β) ^ j + K1 * ε := by
      rw [← sum_sub_distrib]
      have hpt : ∀ j ∈ range t, |deconv a κ hh j * hh (t - j) - k j * h (t - j)| ≤
          (H + 1) * (α * ε * (1 + β) ^ j) + |k j| * ε := by
        intro j hj
        have e : deconv a κ hh j * hh (t - j) - k j * h (t - j) =
            (deconv a κ hh j - k j) * hh (t - j) + k j * (hh (t - j) - h (t - j)) := by ring
        rw [e]
        refine (abs_add_le _ _).trans (add_le_add ?_ ?_)
        · rw [abs_mul, mul_comm]
          exact mul_le_mul (hhb j hj) (hprev j hj) (abs_nonneg _) (by positivity)
        · rw [abs_mul]
          exact mul_le_mul_of_nonneg_left (hclose (t - j) (by omega)) (abs_nonneg _)
      calc _ ≤ ∑ j ∈ range t, ((H + 1) * (α * ε * (1 + β) ^ j) + |k j| * ε) :=
            (abs_sum_le_sum_abs _ _).trans (sum_le_sum hpt)
        _ = (H + 1) * ∑ j ∈ range t, α * ε * (1 + β) ^ j + (∑ j ∈ range t, |k j|) * ε := by
            rw [sum_add_distrib, mul_sum, sum_mul]
        _ ≤ (H + 1) * ∑ j ∈ range t, α * ε * (1 + β) ^ j + K1 * ε := by
            gcongr; exact hK1 t
    have hgeom : 1 + β * ∑ j ∈ range t, (1 + β) ^ j = (1 + β) ^ t := by
      have := geom_sum_mul (1 + β) t
      rw [show (1 + β - 1) = β by ring] at this
      linarith [mul_comm β (∑ j ∈ range t, (1 + β) ^ j)]
    rw [p1_deconv_eq, htrue t, ← sub_div, abs_div, abs_of_pos hκ2, div_le_iff₀ hκ2]
    have e : hh (t + 1) - a * hh t - κ * ∑ j ∈ range t, deconv a κ hh j * hh (t - j) -
        (h (t + 1) - a * h t - κ * ∑ j ∈ range t, k j * h (t - j)) =
        (hh (t + 1) - h (t + 1)) - a * (hh t - h t) -
          κ * (∑ j ∈ range t, deconv a κ hh j * hh (t - j) - ∑ j ∈ range t, k j * h (t - j)) := by ring
    rw [e]
    have h1 := hclose (t + 1) (by omega)
    have h2 := hclose t (by omega)
    calc |(hh (t + 1) - h (t + 1)) - a * (hh t - h t) -
          κ * (∑ j ∈ range t, deconv a κ hh j * hh (t - j) - ∑ j ∈ range t, k j * h (t - j))|
        ≤ |hh (t + 1) - h (t + 1)| + |a| * |hh t - h t| +
            |κ| * |∑ j ∈ range t, deconv a κ hh j * hh (t - j) - ∑ j ∈ range t, k j * h (t - j)| := by
          rw [← abs_mul, ← abs_mul]
          have t1 := abs_sub ((hh (t + 1) - h (t + 1)) - a * (hh t - h t))
            (κ * (∑ j ∈ range t, deconv a κ hh j * hh (t - j) - ∑ j ∈ range t, k j * h (t - j)))
          have t2 := abs_sub (hh (t + 1) - h (t + 1)) (a * (hh t - h t))
          linarith
      _ ≤ ε + |a| * ε + |κ| * ((H + 1) * ∑ j ∈ range t, α * ε * (1 + β) ^ j + K1 * ε) := by
          have t3 := mul_le_mul_of_nonneg_left h2 (abs_nonneg a)
          have t4 := mul_le_mul_of_nonneg_left hsum (abs_nonneg κ)
          linarith
      _ = (1 + |a| + |κ| * K1) * ε + |κ| * (H + 1) * (α * ε) * ∑ j ∈ range t, (1 + β) ^ j := by
          rw [← mul_sum]; ring
      _ = α * ε * (1 + β) ^ t * κ ^ 2 := by
          have hακ : α * κ ^ 2 = 1 + |a| + |κ| * K1 := by rw [hα]; field_simp
          have hβκ : β * κ ^ 2 = |κ| * (H + 1) := by rw [hβ]; field_simp
          rw [← hgeom]
          linear_combination (-ε) * hακ + (-(α * ε * ∑ j ∈ range t, (1 + β) ^ j)) * hβκ

/-! ### Theorem 5.6 (ii) -/

/-- Noise level of the averaged taps used in the theorem: `√2 √(log(4(L+1)/β)) √v / √N`. -/
noncomputable def gmNoise (L : ℕ) (β : ℝ) (v : ℝ≥0) (N : ℕ) : ℝ :=
  Real.sqrt 2 * Real.sqrt (Real.log (4 * ((L + 1 : ℕ) : ℝ) / β)) * Real.sqrt v / Real.sqrt N

/-- Kernel error after deconvolution: `α e (1 + β')^L` with `K₁ = W/(1-ρ)` and `H = |κ|/(1-s)`. -/
noncomputable def gmDelta (a κ ρ s W : ℝ) (L : ℕ) (e : ℝ) : ℝ :=
  (1 + |a| + |κ| * (W / (1 - ρ))) / κ ^ 2 * e * (1 + |κ| * (|κ| / (1 - s) + 1) / κ ^ 2) ^ L

/-- The bound of Theorem 5.6 (ii) for `L + 1` moments, kernel error `δ` and fitting slack `η`. -/
noncomputable def gmBound (ρ W : ℝ) (L : ℕ) (δ η : ℝ) : ℝ :=
  ρ * π / (2 * (L + 2)) * (2 * W + 2 * δ + η) + ρ * (L + 1) * ((2 / ρ + 1) * (1 + Real.sqrt 2)) ^ L * (2 * δ + η)

theorem p1_moment_kernel_abs_le (μ : Measure ℝ) [IsFiniteMeasure μ] (ρ : ℝ) (hρ : 0 ≤ ρ)
    (hμ : μ (Set.Icc 0 ρ)ᶜ = 0) (m : ℕ) : |∫ r, r ^ m ∂μ| ≤ ρ ^ m * μ.real Set.univ := by
  have := norm_integral_le_of_norm_le_const (μ := μ) (f := fun r => r ^ m) (C := ρ ^ m)
    ((p1_ae_mem_Icc μ ρ hμ).mono (fun r hr => by
      rw [Real.norm_eq_abs, abs_pow, abs_of_nonneg hr.1]; exact pow_le_pow_left₀ hr.1 hr.2 m))
  simpa [Real.norm_eq_abs] using this

/-- **Theorem 5.6 (ii), formal, finite-sample form.** General memory: the kernel is `k_m = ∫ r^m dμ` for a finite
measure `μ` on `[0, ρ]`, `ρ < 1`, of mass `W`, and the closed loop is stable, `|a| + |κ| W/(1-ρ) ≤ s < 1`. With `N`
reset experiments, independent sub-Gaussian noise of variance proxy `v` on each tap, and `e = gmNoise L β v N ≤ 1`:
with probability at least `1 - β`, every finite measure `ν` on `[0, ρ]` whose first `L + 1` moments fit the
deconvolved kernel values at least as well as `μ` does, up to `η` (in particular the linear-programming estimate),
satisfies `|∫ f dν - ∫ f dμ| ≤ gmBound ρ W L δ η`, `δ = gmDelta a κ ρ s W L e`, for every `f` that is 1-Lipschitz on
`[0, ρ]` with `f(0) = 0`. -/
theorem p1_thm_general_memory_upper (a κ ρ s : ℝ) (hκ : κ ≠ 0) (hρ0 : 0 < ρ) (hρ1 : ρ < 1)
    (μ : Measure ℝ) [IsFiniteMeasure μ] (hμ : μ (Set.Icc 0 ρ)ᶜ = 0)
    (hs : |a| + |κ| * (μ.real Set.univ / (1 - ρ)) ≤ s) (hs1 : s < 1)
    (h : ℕ → ℝ) (h0 : h 0 = κ)
    (hrec : ∀ t, h (t + 1) = a * h t + κ * ∑ j ∈ range (t + 1), (∫ r, r ^ j ∂μ) * h (t - j))
    (L : ℕ) (η : ℝ) (hη : 0 ≤ η)
    {Ω : Type*} [MeasurableSpace Ω] (P : Measure Ω) [IsProbabilityMeasure P]
    {N : ℕ} (hN : 0 < N) (ξ : Fin N → ℕ → Ω → ℝ) (v : ℝ≥0) (hv : 0 < v)
    (hind : ∀ t, iIndepFun (fun n => ξ n t) P) (hsub : ∀ n t, HasSubgaussianMGF (ξ n t) v P)
    (β : ℝ) (hβ : 0 < β) (hβ1 : β < 1) (he1 : gmNoise L β v N ≤ 1) :
    P.real {ω | ¬ ∀ ν : Measure ℝ, IsFiniteMeasure ν → ν (Set.Icc 0 ρ)ᶜ = 0 →
        (∀ i < L + 1, |∫ r, r ^ i ∂ν - deconv a κ (observedTaps κ h (fun t => (∑ n, ξ n t ω) / N)) i| ≤
          (range (L + 1)).sup' nonempty_range_add_one
            (fun i => |∫ r, r ^ i ∂μ - deconv a κ (observedTaps κ h (fun t => (∑ n, ξ n t ω) / N)) i|) + η) →
        ∀ f : ℝ → ℝ, LipschitzOnWith 1 f (Set.Icc 0 ρ) → f 0 = 0 →
          |∫ r, f r ∂ν - ∫ r, f r ∂μ| ≤
            gmBound ρ (μ.real Set.univ) L (gmDelta a κ ρ s (μ.real Set.univ) L (gmNoise L β v N)) η} ≤ β := by
  set W := μ.real Set.univ with hW
  set k : ℕ → ℝ := fun m => ∫ r, r ^ m ∂μ with hk
  set e := gmNoise L β v N with he
  set δ := gmDelta a κ ρ s W L e with hδ
  have hW0 : 0 ≤ W := measureReal_nonneg
  have h1ρ : 0 < 1 - ρ := by linarith
  have hK1 : ∀ n, ∑ m ∈ range n, |k m| ≤ W / (1 - ρ) := by
    intro n
    calc ∑ m ∈ range n, |k m| ≤ ∑ m ∈ range n, ρ ^ m * W :=
          sum_le_sum (fun m _ => p1_moment_kernel_abs_le μ ρ hρ0.le hμ m)
      _ = (∑ m ∈ range n, ρ ^ m) * W := by rw [sum_mul]
      _ ≤ 1 / (1 - ρ) * W := mul_le_mul_of_nonneg_right (p1_geom_partial_le ρ hρ0.le hρ1 n) hW0
      _ = W / (1 - ρ) := by ring
  have hH1 := p1_response_l1 a κ (W / (1 - ρ)) s k h h0 hrec hK1 hs hs1
  have hH : ∀ t, |h t| ≤ |κ| / (1 - s) := by
    intro t
    calc |h t| ≤ ∑ u ∈ range (t + 1), |h u| :=
          single_le_sum (f := fun u => |h u|) (fun _ _ => abs_nonneg _) (mem_range.mpr (Nat.lt_succ_self t))
      _ ≤ _ := hH1 (t + 1)
  have he0 : 0 ≤ e := by rw [he, gmNoise]; positivity
  -- the noise event
  have hunion := p1_noise_union P hN ξ v hv hind hsub (K := L + 1) (by omega) hβ hβ1
  refine le_trans (measureReal_mono ?_) hunion
  intro ω hω
  simp only [Set.mem_setOf_eq] at hω ⊢
  by_contra hgood
  push Not at hgood
  apply hω
  -- on the good event: every tap `1 ≤ t ≤ 2L+2` is within `e`
  set hh := observedTaps κ h (fun t => (∑ n, ξ n t ω) / N) with hhdef
  have hclose : ∀ t ≤ L + 1, |hh t - h t| ≤ e := by
    intro t ht
    simp only [hhdef, observedTaps]
    split_ifs with h0t
    · subst h0t; rw [h0, sub_self, abs_zero]; exact he0
    · have := hgood t (mem_Icc.mpr ⟨by omega, by omega⟩)
      rw [add_sub_cancel_left]
      exact this.le
  have hdec := p1_deconv_error_explicit a κ (|κ| / (1 - s)) (W / (1 - ρ)) hκ k h hh h0 hrec hH hK1 L e he0 he1 hclose
  have hβ' : 0 ≤ |κ| * (|κ| / (1 - s) + 1) / κ ^ 2 := by
    have : 0 < 1 - s := by linarith
    positivity
  have hdelta : ∀ i < L + 1, |deconv a κ hh i - k i| ≤ δ := by
    intro i hi
    refine (hdec i (by omega)).trans ?_
    rw [hδ, gmDelta]
    have h1 : (1 : ℝ) ≤ 1 + |κ| * (|κ| / (1 - s) + 1) / κ ^ 2 := by linarith
    have hpow := pow_le_pow_right₀ h1 (show i ≤ L by omega)
    have h0' : 0 ≤ (1 + |a| + |κ| * (W / (1 - ρ))) / κ ^ 2 * e := by positivity
    exact mul_le_mul_of_nonneg_left hpow h0'
  have hδ0 : 0 ≤ δ := le_trans (abs_nonneg _) (hdelta 0 (by omega))
  intro ν hνfin hν hfit f hf hf0
  have := hνfin
  have hsup : (range (L + 1)).sup' nonempty_range_add_one (fun i => |∫ r, r ^ i ∂μ - deconv a κ hh i|) ≤ δ := by
    refine Finset.sup'_le _ _ (fun i hi => ?_)
    rw [abs_sub_comm]; exact hdelta i (mem_range.mp hi)
  have hmom : ∀ i < L + 1, |∫ r, r ^ i ∂ν - ∫ r, r ^ i ∂μ| ≤ 2 * δ + η := by
    intro i hi
    have h1 := hfit i hi
    have h2 := hdelta i hi
    calc |∫ r, r ^ i ∂ν - ∫ r, r ^ i ∂μ|
        ≤ |∫ r, r ^ i ∂ν - deconv a κ hh i| + |deconv a κ hh i - k i| := by
          have := abs_add_le (∫ r, r ^ i ∂ν - deconv a κ hh i) (deconv a κ hh i - k i)
          simpa [hk] using this
      _ ≤ (δ + η) + δ := add_le_add (h1.trans (by linarith)) h2
      _ = 2 * δ + η := by ring
  have hcmp := p1_gm_moment_comparison ρ hρ0 L μ ν hμ hν (2 * δ + η) hmom f hf hf0
  have hmass : ν.real Set.univ ≤ W + (2 * δ + η) := by
    have h0m := hmom 0 (by omega)
    simp only [pow_zero, integral_const, smul_eq_mul, mul_one] at h0m
    have := le_abs_self (ν.real Set.univ - μ.real Set.univ)
    rw [hW]; linarith
  refine hcmp.trans ?_
  rw [gmBound]
  have hc : 0 ≤ ρ * π / (2 * (L + 2)) := by positivity
  have : ρ * π / (2 * ((L : ℝ) + 2)) * (ν.real Set.univ + W) ≤ ρ * π / (2 * ((L : ℝ) + 2)) * (2 * W + 2 * δ + η) :=
    mul_le_mul_of_nonneg_left (by linarith) hc
  linarith

end CurrentMM
