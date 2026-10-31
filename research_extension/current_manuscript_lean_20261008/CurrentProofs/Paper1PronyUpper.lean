import CurrentProofs.Paper1UniformInverse
import CurrentProofs.Paper1PronyMoment
import CurrentProofs.Paper1PronyDeconv
import Mathlib.Probability.Moments.SubGaussian
import Mathlib.Probability.Distributions.Gaussian.Real
import Mathlib.Analysis.SpecialFunctions.Log.Basic
import Mathlib.Topology.MetricSpace.Pseudo.Pi

/-!
# Paper 1, Theorem 5.4 (`prop:esprit`): the matching Prony upper bound, for every `K`

The class: `K ≥ 1` cohorts with merged weights `ω_i ∈ [ω_min, ω_max]`, `ω_min > 0`, and memory rates
`r_c + Δ s_i` where the rescaled nodes `s` lie in a compact set `S` of `γ`-separated increasing vectors in
`[-1, 1]^K`; `|r_c| < 1` and `0 < Δ ≤ 1 - |r_c|`. Each of `N` reset experiments records the impulse response at
taps `1, …, 2K` with independent sub-Gaussian noise of variance proxy `v` (Gaussian noise of variance `v` is a
special case); the first tap `h_0 = κ` is known.

The estimator averages the records, deconvolves them into kernel values, centres at `r_c`, rescales by `Δ^{-m}`
and returns the `K`-atom measure with increasing nodes and nonzero weights matching the `2K` moments; by
`p1_prony_polynomial` this is exactly what Prony's method computes.

`p1_thm_prony_upper_bound`: there are `c₀, C > 0` depending only on the class (not on `Δ`, `N`, `v`, `β`) such
that, with `ε_N = √v N^{-1/2} Δ^{-(2K-1)}`, whenever `ε_N ≤ c₀ / √(log(4K/β))` the estimator exists, is unique,
and every weight is within `C √(log(4K/β)) ε_N` of the truth, with probability at least `1 - β`.
-/

namespace CurrentMM

open Finset MeasureTheory ProbabilityTheory
open scoped NNReal

/-! ### Noise -/

/-- Gaussian noise of variance `v` (the paper's setting) is sub-Gaussian with variance proxy `v`, so
`p1_thm_prony_upper_bound` applies to it. -/
theorem p1_gaussian_hasSubgaussianMGF (v : ℝ≥0) : HasSubgaussianMGF id v (gaussianReal 0 v) :=
  ⟨fun t => integrable_exp_mul_gaussianReal t, fun t => by rw [mgf_id_gaussianReal]; simp⟩

/-- **Sub-Gaussian tail of an averaged record.** -/
theorem p1_mean_noise_tail {Ω : Type*} [MeasurableSpace Ω] (P : Measure Ω) [IsProbabilityMeasure P]
    {N : ℕ} (hN : 0 < N) (ξ : Fin N → Ω → ℝ) (v : ℝ≥0) (hind : iIndepFun ξ P)
    (hsub : ∀ n, HasSubgaussianMGF (ξ n) v P) {ε : ℝ} (hε : 0 ≤ ε) :
    P.real {ω | ε ≤ |(∑ n, ξ n ω) / N|} ≤ 2 * Real.exp (-(N * ε ^ 2) / (2 * v)) := by
  have hNpos : (0 : ℝ) < N := by exact_mod_cast hN
  have hup := HasSubgaussianMGF.measure_sum_ge_le_of_iIndepFun hind (c := fun _ => v) (s := univ)
    (fun n _ => hsub n) (ε := N * ε) (by positivity)
  have hneg : iIndepFun (fun n => -ξ n) P := hind.comp (fun _ x => -x) (fun _ => measurable_neg)
  have hlo := HasSubgaussianMGF.measure_sum_ge_le_of_iIndepFun hneg (c := fun _ => v) (s := univ)
    (fun n _ => (hsub n).neg) (ε := N * ε) (by positivity)
  have hexp : ∀ c : ℝ≥0, c = ∑ _n ∈ (univ : Finset (Fin N)), v →
      Real.exp (-(N * ε) ^ 2 / (2 * c)) = Real.exp (-(N * ε ^ 2) / (2 * v)) := by
    intro c hc
    rw [hc]
    simp only [sum_const, card_univ, Fintype.card_fin, nsmul_eq_mul, NNReal.coe_mul, NNReal.coe_natCast]
    rcases eq_or_ne (v : ℝ) 0 with hv | hv
    · simp [hv]
    · congr 1; field_simp
  rw [hexp _ rfl] at hup hlo
  have hset : {ω | ε ≤ |(∑ n, ξ n ω) / N|} ⊆
      {ω | N * ε ≤ ∑ n ∈ univ, ξ n ω} ∪ {ω | N * ε ≤ ∑ n ∈ univ, (fun n => -ξ n) n ω} := by
    intro ω hω
    simp only [Set.mem_ofPred_eq, abs_div, abs_of_pos hNpos, le_div_iff₀ hNpos] at hω
    rcases le_abs.mp hω with h | h
    · left; simp only [Set.mem_ofPred_eq]; linarith
    · right
      simp only [Set.mem_ofPred_eq, Pi.neg_apply, sum_neg_distrib]
      linarith
  calc P.real {ω | ε ≤ |(∑ n, ξ n ω) / N|}
      ≤ P.real ({ω | N * ε ≤ ∑ n ∈ univ, ξ n ω} ∪ {ω | N * ε ≤ ∑ n ∈ univ, (fun n => -ξ n) n ω}) :=
        measureReal_mono hset
    _ ≤ _ := measureReal_union_le _ _
    _ ≤ Real.exp (-(N * ε ^ 2) / (2 * v)) + Real.exp (-(N * ε ^ 2) / (2 * v)) := add_le_add hup hlo
    _ = 2 * Real.exp (-(N * ε ^ 2) / (2 * v)) := by ring

/-- **Union bound over the `2K` taps.** With `e = √2 √(log(4K/β)) √v / √N`, some averaged tap misses by `e` or
more with probability at most `β`. -/
theorem p1_noise_union {Ω : Type*} [MeasurableSpace Ω] (P : Measure Ω) [IsProbabilityMeasure P]
    {N : ℕ} (hN : 0 < N) (ξ : Fin N → ℕ → Ω → ℝ) (v : ℝ≥0) (hv : 0 < v)
    (hind : ∀ t, iIndepFun (fun n => ξ n t) P) (hsub : ∀ n t, HasSubgaussianMGF (ξ n t) v P)
    {K : ℕ} (hK : 1 ≤ K) {β : ℝ} (hβ : 0 < β) (hβ1 : β < 1) :
    P.real {ω | ∃ t ∈ Icc 1 (2 * K),
      Real.sqrt 2 * Real.sqrt (Real.log (4 * K / β)) * Real.sqrt v / Real.sqrt N ≤ |(∑ n, ξ n t ω) / N|} ≤ β := by
  set lg := Real.log (4 * K / β) with hlg
  have hKr : (1 : ℝ) ≤ K := by exact_mod_cast hK
  have harg : 1 < 4 * K / β := by
    rw [lt_div_iff₀ hβ]; nlinarith
  have hlg0 : 0 < lg := Real.log_pos harg
  have hNpos : (0 : ℝ) < N := by exact_mod_cast hN
  have hvpos : (0 : ℝ) < v := by exact_mod_cast hv
  set e := Real.sqrt 2 * Real.sqrt lg * Real.sqrt v / Real.sqrt N with he
  have he0 : 0 ≤ e := by positivity
  have he2 : N * e ^ 2 = 2 * v * lg := by
    rw [he, div_pow, mul_pow, mul_pow, Real.sq_sqrt (by norm_num), Real.sq_sqrt hlg0.le,
      Real.sq_sqrt hvpos.le, Real.sq_sqrt hNpos.le]
    field_simp
  have hone : Real.exp (-(N * e ^ 2) / (2 * v)) = β / (4 * K) := by
    rw [he2, show -(2 * (v : ℝ) * lg) / (2 * v) = -lg by field_simp, Real.exp_neg, hlg,
      Real.exp_log (by positivity), inv_div]
  have hset : {ω | ∃ t ∈ Icc 1 (2 * K), e ≤ |(∑ n, ξ n t ω) / N|} =
      ⋃ t ∈ Icc 1 (2 * K), {ω | e ≤ |(∑ n, ξ n t ω) / N|} := by
    ext ω; simp
  rw [hset]
  refine (measureReal_biUnion_finset_le _ _).trans ?_
  calc ∑ t ∈ Icc 1 (2 * K), P.real {ω | e ≤ |(∑ n, ξ n t ω) / N|}
      ≤ ∑ _t ∈ Icc 1 (2 * K), 2 * (β / (4 * K)) := by
        refine sum_le_sum (fun t _ => ?_)
        rw [← hone]
        exact p1_mean_noise_tail P hN (fun n => ξ n t) v (hind t) (fun n => hsub n t) he0
    _ = β := by
        rw [sum_const, Nat.card_Icc, nsmul_eq_mul]
        push_cast
        field_simp
        ring

/-! ### Centring and rescaling -/

/-- Estimated rescaled moments: centre the deconvolved kernel at `r_c` and rescale by `Δ^{-m}`. -/
noncomputable def pronyMomentEstimate (K : ℕ) (a κ rc Δ : ℝ) (hhat : ℕ → ℝ) : Fin (2 * K) → ℝ :=
  fun m => (Δ ^ (m : ℕ))⁻¹ *
    ∑ j ∈ range ((m : ℕ) + 1), ((m : ℕ).choose j : ℝ) * (-rc) ^ ((m : ℕ) - j) * deconv a κ hhat j

/-- On the true kernel, centring and rescaling give the moments of the rescaled nodes. -/
theorem p1_centring_true {K : ℕ} (a κ rc Δ : ℝ) (hΔ : Δ ≠ 0) (h : ℕ → ℝ) (s ω : Fin K → ℝ)
    (hk : ∀ j, deconv a κ h j = ∑ i, ω i * (rc + Δ * s i) ^ j) :
    pronyMomentEstimate K a κ rc Δ h = momentMap K (s, ω) := by
  funext m
  simp only [pronyMomentEstimate, momentMap, hk]
  have hpow : ∀ i, ∑ j ∈ range ((m : ℕ) + 1), ((m : ℕ).choose j : ℝ) * (-rc) ^ ((m : ℕ) - j) *
      (ω i * (rc + Δ * s i) ^ j) = ω i * (Δ ^ (m : ℕ) * s i ^ (m : ℕ)) := by
    intro i
    have e := add_pow (rc + Δ * s i) (-rc) (m : ℕ)
    rw [show rc + Δ * s i + -rc = Δ * s i by ring, mul_pow] at e
    rw [e, mul_sum]
    refine sum_congr rfl (fun j _ => by ring)
  have hswap : ∑ j ∈ range ((m : ℕ) + 1), ((m : ℕ).choose j : ℝ) * (-rc) ^ ((m : ℕ) - j) *
      ∑ i, ω i * (rc + Δ * s i) ^ j = ∑ i, ω i * (Δ ^ (m : ℕ) * s i ^ (m : ℕ)) := by
    simp_rw [mul_sum]
    rw [sum_comm]
    exact sum_congr rfl (fun i _ => hpow i)
  rw [hswap, mul_sum]
  refine sum_congr rfl (fun i _ => ?_)
  field_simp

/-- Centring and rescaling amplify a kernel error `η` by at most `2^{2K} Δ^{-(2K-1)}`. -/
theorem p1_centring_perturb {K : ℕ} (a κ rc Δ : ℝ) (hrc : |rc| ≤ 1) (hΔ0 : 0 < Δ) (hΔ1 : Δ ≤ 1)
    (h h' : ℕ → ℝ) (η : ℝ) (hη0 : 0 ≤ η) (hη : ∀ j < 2 * K, |deconv a κ h' j - deconv a κ h j| ≤ η) :
    dist (pronyMomentEstimate K a κ rc Δ h') (pronyMomentEstimate K a κ rc Δ h) ≤
      2 ^ (2 * K) * η * (Δ ^ (2 * K - 1))⁻¹ := by
  refine (dist_pi_le_iff (by positivity)).mpr (fun m => ?_)
  have hm := m.isLt
  rw [Real.dist_eq]
  simp only [pronyMomentEstimate]
  rw [← mul_sub, ← sum_sub_distrib, abs_mul, abs_inv, abs_of_pos (pow_pos hΔ0 _)]
  have hsum : |∑ j ∈ range ((m : ℕ) + 1), (((m : ℕ).choose j : ℝ) * (-rc) ^ ((m : ℕ) - j) * deconv a κ h' j -
      ((m : ℕ).choose j : ℝ) * (-rc) ^ ((m : ℕ) - j) * deconv a κ h j)| ≤ 2 ^ (2 * K) * η := by
    refine (abs_sum_le_sum_abs _ _).trans ?_
    calc ∑ j ∈ range ((m : ℕ) + 1), |((m : ℕ).choose j : ℝ) * (-rc) ^ ((m : ℕ) - j) * deconv a κ h' j -
          ((m : ℕ).choose j : ℝ) * (-rc) ^ ((m : ℕ) - j) * deconv a κ h j|
        ≤ ∑ j ∈ range ((m : ℕ) + 1), 1 ^ j * |rc| ^ ((m : ℕ) - j) * ((m : ℕ).choose j : ℝ) * η := by
          refine sum_le_sum (fun j hj => ?_)
          rw [← mul_sub, abs_mul, abs_mul, abs_pow, abs_neg, Nat.abs_cast, one_pow, one_mul]
          have := hη j (by have := mem_range.mp hj; omega)
          calc ((m : ℕ).choose j : ℝ) * |rc| ^ ((m : ℕ) - j) * |deconv a κ h' j - deconv a κ h j|
              ≤ ((m : ℕ).choose j : ℝ) * |rc| ^ ((m : ℕ) - j) * η := by gcongr
            _ = |rc| ^ ((m : ℕ) - j) * ((m : ℕ).choose j : ℝ) * η := by ring
      _ = (1 + |rc|) ^ (m : ℕ) * η := by rw [add_pow, sum_mul]
      _ ≤ 2 ^ (2 * K) * η := by
          gcongr
          calc (1 + |rc|) ^ (m : ℕ) ≤ 2 ^ (m : ℕ) := by gcongr; linarith
            _ ≤ 2 ^ (2 * K) := pow_le_pow_right₀ (by norm_num) hm.le
  have hinv : (Δ ^ (m : ℕ))⁻¹ ≤ (Δ ^ (2 * K - 1))⁻¹ :=
    inv_anti₀ (pow_pos hΔ0 _) (pow_le_pow_of_le_one hΔ0.le hΔ1 (by omega))
  calc (Δ ^ (m : ℕ))⁻¹ * |_| ≤ (Δ ^ (2 * K - 1))⁻¹ * (2 ^ (2 * K) * η) := by
        gcongr
    _ = 2 ^ (2 * K) * η * (Δ ^ (2 * K - 1))⁻¹ := by ring

/-! ### The deterministic core -/

/-- Observed taps: `h_0 = κ` is known; later taps are the true response plus the averaged noise `ν`. -/
noncomputable def observedTaps (κ : ℝ) (h ν : ℕ → ℝ) : ℕ → ℝ := fun t => if t = 0 then κ else h t + ν t

/-- **Deterministic core of Theorem 5.4.** Constants `c₁, L, C` depending only on the class such that, if every
observed tap up to `2K` is within `e ≤ 1` of the truth and the induced moment error
`δ = 2^{2K} C e Δ^{-(2K-1)}` is at most `c₁`, then an ordered representation with nonzero weights matching the
estimated moments exists, it is unique, and its weights are within `L δ` of the true merged weights. -/
theorem p1_prony_deterministic {K : ℕ} (a κ : ℝ) (hκ : κ ≠ 0)
    (S : Set (Fin K → ℝ)) (hS : IsCompact S) (γ : ℝ) (hγ : 0 < γ)
    (hSsep : ∀ s ∈ S, ∀ i j, i < j → γ ≤ s j - s i) (hSbox : ∀ s ∈ S, ∀ i, |s i| ≤ 1)
    (ωmin ωmax : ℝ) (hωmin : 0 < ωmin) (hωle : ωmin ≤ ωmax) (rc : ℝ) (hrc : |rc| < 1) :
    ∃ c₁ > 0, ∃ L > 0, ∃ C ≥ 0, ∀ Δ : ℝ, 0 < Δ → Δ ≤ 1 - |rc| →
      ∀ s ∈ S, ∀ ω : Fin K → ℝ, (∀ i, ω i ∈ Set.Icc ωmin ωmax) →
      ∀ h : ℕ → ℝ, h 0 = κ →
      (∀ t, h (t + 1) = a * h t + κ * ∑ j ∈ range (t + 1), (∑ i, ω i * (rc + Δ * s i) ^ j) * h (t - j)) →
      ∀ (hhat : ℕ → ℝ) (e : ℝ), 0 ≤ e → e ≤ 1 → (∀ t ≤ 2 * K, |hhat t - h t| ≤ e) →
      2 ^ (2 * K) * (C * e) * (Δ ^ (2 * K - 1))⁻¹ ≤ c₁ →
      (∃ x : PronyParam K, StrictMono x.1 ∧ (∀ i, x.2 i ≠ 0) ∧
          momentMap K x = pronyMomentEstimate K a κ rc Δ hhat) ∧
      ∀ x : PronyParam K, StrictMono x.1 → (∀ i, x.2 i ≠ 0) →
          momentMap K x = pronyMomentEstimate K a κ rc Δ hhat →
          ∀ i, |x.2 i - ω i| ≤ L * (2 ^ (2 * K) * (C * e) * (Δ ^ (2 * K - 1))⁻¹) := by
  classical
  set Q : Set (PronyParam K) := S ×ˢ Set.pi Set.univ (fun _ => Set.Icc ωmin ωmax) with hQ
  have hQc : IsCompact Q := hS.prod (isCompact_univ_pi (fun _ => isCompact_Icc))
  have hmono : ∀ s ∈ S, StrictMono s := fun s hs i j hij => by
    have := hSsep s hs i j hij; linarith
  have hinjQ : ∀ x ∈ Q, Function.Injective (fderiv ℝ (momentMap K) x) := by
    rintro ⟨s, ω⟩ ⟨hs, hω⟩
    exact p1_momentMap_fderiv_injective (s, ω) (hmono s hs).injective
      (fun i => (lt_of_lt_of_le hωmin (hω i (Set.mem_univ i)).1).ne')
  have hdim : Module.finrank ℝ (PronyParam K) = Module.finrank ℝ (Fin (2 * K) → ℝ) := by
    simp [Module.finrank_prod, two_mul]
  obtain ⟨ρ₀, hρ₀, L, hL, hinv⟩ := p1_uniform_local_inverse (p1_momentMap_contDiff K) hdim hQc hinjQ
  set A : ℝ := K * ωmax with hAdef
  have hA : 0 ≤ A := mul_nonneg (Nat.cast_nonneg _) (hωmin.le.trans hωle)
  obtain ⟨B, hB0, hBnd⟩ := p1_response_bound a κ A hA (2 * K)
  obtain ⟨C, hC0, hCp⟩ := p1_deconv_perturb a κ A B hκ hA hB0 (2 * K) (2 * K)
  refine ⟨min ρ₀ (min (γ / (4 * L)) (ωmin / (2 * L))), by positivity, L, hL, C, hC0, ?_⟩
  intro Δ hΔ0 hΔ1 s hs ω hω h h0 hrec hhat e he0 he1 hclose hδ
  have hΔle1 : Δ ≤ 1 := hΔ1.trans (by linarith [abs_nonneg rc])
  set k : ℕ → ℝ := fun j => ∑ i, ω i * (rc + Δ * s i) ^ j with hk
  have hr : ∀ i, |rc + Δ * s i| ≤ 1 := by
    intro i
    calc |rc + Δ * s i| ≤ |rc| + |Δ * s i| := abs_add_le _ _
      _ = |rc| + Δ * |s i| := by rw [abs_mul, abs_of_pos hΔ0]
      _ ≤ |rc| + Δ * 1 := by gcongr; exact hSbox s hs i
      _ ≤ 1 := by linarith
  have hkA : ∀ j, |k j| ≤ A := by
    intro j
    refine (abs_sum_le_sum_abs _ _).trans ?_
    calc ∑ i, |ω i * (rc + Δ * s i) ^ j| ≤ ∑ _i : Fin K, ωmax := by
          refine sum_le_sum (fun i _ => ?_)
          rw [abs_mul, abs_pow, abs_of_pos (lt_of_lt_of_le hωmin (hω i).1)]
          calc ω i * |rc + Δ * s i| ^ j ≤ ωmax * 1 :=
                mul_le_mul (hω i).2 (pow_le_one₀ (abs_nonneg _) (hr i)) (pow_nonneg (abs_nonneg _) _)
                  (hωmin.le.trans hωle)
            _ = ωmax := mul_one _
      _ = A := by rw [sum_const, card_univ, Fintype.card_fin, nsmul_eq_mul]
  have hdec : ∀ j, deconv a κ h j = k j := p1_deconv_true a κ hκ k h h0 hrec
  have hhB : ∀ t ≤ 2 * K, |h t| ≤ B := hBnd k h h0 hrec hkA
  have hpert : ∀ t < 2 * K, |deconv a κ hhat t - deconv a κ h t| ≤ C * e := fun t ht =>
    hCp h hhat e he0 he1 hclose hhB (fun t _ => by rw [hdec]; exact hkA t) t ht ht
  set δ := 2 ^ (2 * K) * (C * e) * (Δ ^ (2 * K - 1))⁻¹ with hδdef
  have hdist : dist (pronyMomentEstimate K a κ rc Δ hhat) (momentMap K (s, ω)) ≤ δ := by
    rw [← p1_centring_true a κ rc Δ hΔ0.ne' h s ω hdec]
    exact p1_centring_perturb a κ rc Δ hrc.le hΔ0 hΔle1 h hhat (C * e) (by positivity) hpert
  have hx0 : (s, ω) ∈ Q := ⟨hs, fun i _ => hω i⟩
  obtain ⟨z, hz, hfz⟩ := hinv (s, ω) hx0 _ (hdist.trans (hδ.trans (min_le_left _ _)))
  have hzδ : dist z (s, ω) ≤ L * δ := hz.trans (mul_le_mul_of_nonneg_left hdist hL.le)
  have hδγ : δ ≤ γ / (4 * L) := hδ.trans ((min_le_right _ _).trans (min_le_left _ _))
  have hδω : δ ≤ ωmin / (2 * L) := hδ.trans ((min_le_right _ _).trans (min_le_right _ _))
  have hLγ : L * δ ≤ γ / 4 := by
    rw [le_div_iff₀ (by positivity : (0 : ℝ) < 4 * L)] at hδγ
    rw [le_div_iff₀ (by norm_num : (0 : ℝ) < 4)]; linarith
  have hLω : L * δ ≤ ωmin / 2 := by
    rw [le_div_iff₀ (by positivity : (0 : ℝ) < 2 * L)] at hδω
    rw [le_div_iff₀ (by norm_num : (0 : ℝ) < 2)]; linarith
  have hzδ' : max (dist z.1 s) (dist z.2 ω) ≤ L * δ := hzδ
  have hz1 : ∀ i, |z.1 i - s i| ≤ L * δ := fun i => by
    rw [← Real.dist_eq]
    exact (dist_le_pi_dist z.1 s i).trans ((le_max_left _ _).trans hzδ')
  have hz2 : ∀ i, |z.2 i - ω i| ≤ L * δ := fun i => by
    rw [← Real.dist_eq]
    exact (dist_le_pi_dist z.2 ω i).trans ((le_max_right _ _).trans hzδ')
  have hzmono : StrictMono z.1 := by
    intro i j hij
    have hsep := hSsep s hs i j hij
    have hi := abs_le.mp (hz1 i)
    have hj := abs_le.mp (hz1 j)
    linarith
  have hzpos : ∀ i, 0 < z.2 i := by
    intro i
    have hi := abs_le.mp (hz2 i)
    linarith [(hω i).1]
  refine ⟨⟨z, hzmono, fun i => (hzpos i).ne', hfz⟩, fun x hxm hxw hxf i => ?_⟩
  have hxz : x = z := p1_ordered_representation_unique x z hxm hzmono hxw (fun i => (hzpos i).ne')
    (hxf.trans hfz.symm)
  rw [hxz]
  exact hz2 i

/-! ### Theorem 5.4 -/

/-- **Theorem 5.4 (`prop:esprit`), every `K`.** On the class described in the module header there are
`c₀, C > 0`, depending only on the class, such that for every spacing `Δ`, every economy in the class, every
number `N` of reset experiments with independent sub-Gaussian noise of variance proxy `v`, and every `β ∈ (0,1)`:
if `ε_N = √v N^{-1/2} Δ^{-(2K-1)} ≤ c₀ / √(log(4K/β))`, then with probability at least `1 - β` the Prony estimate
(the ordered representation with nonzero weights matching the estimated moments) exists, is unique, and recovers
every merged weight to within `C √(log(4K/β)) ε_N`. -/
theorem p1_thm_prony_upper_bound {K : ℕ} (hK : 1 ≤ K) (a κ : ℝ) (hκ : κ ≠ 0)
    (S : Set (Fin K → ℝ)) (hS : IsCompact S) (γ : ℝ) (hγ : 0 < γ)
    (hSsep : ∀ s ∈ S, ∀ i j, i < j → γ ≤ s j - s i) (hSbox : ∀ s ∈ S, ∀ i, |s i| ≤ 1)
    (ωmin ωmax : ℝ) (hωmin : 0 < ωmin) (hωle : ωmin ≤ ωmax) (rc : ℝ) (hrc : |rc| < 1) :
    ∃ c₀ > 0, ∃ Cst > 0, ∀ Δ : ℝ, 0 < Δ → Δ ≤ 1 - |rc| →
      ∀ s ∈ S, ∀ ω : Fin K → ℝ, (∀ i, ω i ∈ Set.Icc ωmin ωmax) →
      ∀ h : ℕ → ℝ, h 0 = κ →
      (∀ t, h (t + 1) = a * h t + κ * ∑ j ∈ range (t + 1), (∑ i, ω i * (rc + Δ * s i) ^ j) * h (t - j)) →
      ∀ {Ω : Type*} [MeasurableSpace Ω] (P : Measure Ω) [IsProbabilityMeasure P]
        {N : ℕ} (_hN : 0 < N) (ξ : Fin N → ℕ → Ω → ℝ) (v : ℝ≥0), 0 < v →
        (∀ t, iIndepFun (fun n => ξ n t) P) → (∀ n t, HasSubgaussianMGF (ξ n t) v P) →
        ∀ β : ℝ, 0 < β → β < 1 →
        Real.sqrt v / Real.sqrt N * (Δ ^ (2 * K - 1))⁻¹ ≤ c₀ / Real.sqrt (Real.log (4 * K / β)) →
        P.real {ω' | ¬ ((∃ x : PronyParam K, StrictMono x.1 ∧ (∀ i, x.2 i ≠ 0) ∧
            momentMap K x = pronyMomentEstimate K a κ rc Δ
              (observedTaps κ h (fun t => (∑ n, ξ n t ω') / N))) ∧
          ∀ x : PronyParam K, StrictMono x.1 → (∀ i, x.2 i ≠ 0) →
            momentMap K x = pronyMomentEstimate K a κ rc Δ
              (observedTaps κ h (fun t => (∑ n, ξ n t ω') / N)) →
            ∀ i, |x.2 i - ω i| ≤ Cst * Real.sqrt (Real.log (4 * K / β)) *
              (Real.sqrt v / Real.sqrt N * (Δ ^ (2 * K - 1))⁻¹))} ≤ β := by
  obtain ⟨c₁, hc₁, L, hL, C, hC0, hdet⟩ :=
    p1_prony_deterministic a κ hκ S hS γ hγ hSsep hSbox ωmin ωmax hωmin hωle rc hrc
  set C1 : ℝ := 2 ^ (2 * K) * (C + 1) * Real.sqrt 2 with hC1
  have hC1pos : 0 < C1 := by positivity
  refine ⟨min (c₁ / C1) (1 / Real.sqrt 2), by positivity, L * C1, by positivity, ?_⟩
  intro Δ hΔ0 hΔ1 s hs ω hω h h0 hrec Ω _ P _ N hN ξ v hv hind hsub β hβ hβ1 hεN
  have hΔle1 : Δ ≤ 1 := hΔ1.trans (by linarith [abs_nonneg rc])
  set lg := Real.log (4 * K / β) with hlg
  have hKr : (1 : ℝ) ≤ K := by exact_mod_cast hK
  have hlg0 : 0 < lg := Real.log_pos (by rw [lt_div_iff₀ hβ]; nlinarith)
  set lam := Real.sqrt lg with hlam
  have hlam0 : 0 < lam := Real.sqrt_pos.mpr hlg0
  set D := Δ ^ (2 * K - 1) with hD
  have hD0 : 0 < D := pow_pos hΔ0 _
  have hDinv : 1 ≤ D⁻¹ := one_le_inv₀ hD0 |>.mpr (pow_le_one₀ hΔ0.le hΔle1)
  set εN := Real.sqrt v / Real.sqrt N * D⁻¹ with hεNdef
  set e := Real.sqrt 2 * lam * Real.sqrt v / Real.sqrt N with he
  have he0 : 0 ≤ e := by positivity
  have hlame : lam * εN ≤ min (c₁ / C1) (1 / Real.sqrt 2) := by
    have := hεN; rw [le_div_iff₀ hlam0] at this; linarith
  have he_le : e ≤ Real.sqrt 2 * (lam * εN) := by
    have hx : 0 ≤ Real.sqrt 2 * lam * (Real.sqrt v / Real.sqrt N) := by positivity
    calc e = Real.sqrt 2 * lam * (Real.sqrt v / Real.sqrt N) := by rw [he]; ring
      _ ≤ Real.sqrt 2 * lam * (Real.sqrt v / Real.sqrt N) * D⁻¹ := le_mul_of_one_le_right hx hDinv
      _ = Real.sqrt 2 * (lam * εN) := by rw [hεNdef]; ring
  have he1 : e ≤ 1 := by
    have hs2 : 0 < Real.sqrt 2 := by positivity
    calc e ≤ Real.sqrt 2 * (lam * εN) := he_le
      _ ≤ Real.sqrt 2 * (1 / Real.sqrt 2) := by gcongr; exact hlame.trans (min_le_right _ _)
      _ = 1 := by field_simp
  have hδeq : 2 ^ (2 * K) * (C * e) * D⁻¹ = 2 ^ (2 * K) * C * Real.sqrt 2 * (lam * εN) := by
    rw [he, hεNdef]; ring
  have hlame0 : 0 ≤ lam * εN := by positivity
  have hδle : 2 ^ (2 * K) * (C * e) * D⁻¹ ≤ C1 * (lam * εN) := by
    rw [hδeq, hC1]
    gcongr
    linarith
  have hδc : C1 * (lam * εN) ≤ c₁ := by
    have := hlame.trans (min_le_left _ _)
    rw [le_div_iff₀ hC1pos] at this; linarith
  refine le_trans (measureReal_mono ?_) (p1_noise_union P hN ξ v hv hind hsub hK hβ hβ1)
  intro ω' hω'
  by_contra hgood
  apply hω'
  simp only [Set.mem_ofPred_eq, not_exists, not_and, not_le] at hgood
  have hclose : ∀ t ≤ 2 * K, |observedTaps κ h (fun t => (∑ n, ξ n t ω') / N) t - h t| ≤ e := by
    intro t ht
    unfold observedTaps
    split_ifs with h0t
    · subst h0t; rw [h0, sub_self, abs_zero]; exact he0
    · rw [add_sub_cancel_left]
      exact (hgood t (mem_Icc.mpr ⟨by omega, ht⟩)).le
  obtain ⟨hex, huniq⟩ := hdet Δ hΔ0 hΔ1 s hs ω hω h h0 hrec _ e he0 he1 hclose (hδle.trans hδc)
  refine ⟨hex, fun x hxm hxw hxf i => (huniq x hxm hxw hxf i).trans ?_⟩
  calc L * (2 ^ (2 * K) * (C * e) * D⁻¹) ≤ L * (C1 * (lam * εN)) := mul_le_mul_of_nonneg_left hδle hL.le
    _ = L * C1 * lam * εN := by ring

end CurrentMM
