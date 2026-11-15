import CurrentProofs.Paper1PronyUpper

/-!
# Paper 1: partial disclosure, the upper bound (deterministic core)

Core `thm:partial`(ii): with `m` tagged groups and `K` untagged ones, subtract the estimated tagged contribution from
the estimated kernel and run Prony's method with `K` nodes on the residual. This file proves the deterministic core:
if the kernel taps are estimated within `e_k` and each tagged weight and rate within `e_w` and `e_r`, then the residual
centred and rescaled moments are within `δ = 2^{2K} η Δ^{-(2K-1)}` of the untagged moments, with
`η = e_k + m (e_w + W_t · 2K · e_r)`, and, once `δ` is below a constant of the class, an ordered representation
matching the residual moments exists, is unique, and recovers every untagged weight to within `L δ`.
The probabilistic statement follows by combining this with the sub-Gaussian tail bounds of `Paper1PronyUpper.lean`
for the kernel taps and the `O_P(N^{-1/2})` errors of the tagged estimates.
-/

namespace CurrentMM

open Finset

/-- Centre a kernel sequence at `r_c` and rescale the `m`-th centred moment by `Δ^{-m}`. -/
noncomputable def kernelMomentEstimate (K : ℕ) (rc Δ : ℝ) (k : ℕ → ℝ) : Fin (2 * K) → ℝ :=
  fun m => (Δ ^ (m : ℕ))⁻¹ *
    ∑ j ∈ range ((m : ℕ) + 1), ((m : ℕ).choose j : ℝ) * (-rc) ^ ((m : ℕ) - j) * k j

/-- On a true `K`-node kernel, centring and rescaling give the moments of the rescaled nodes. -/
theorem p1_kernel_centring_true {K : ℕ} (rc Δ : ℝ) (hΔ : Δ ≠ 0) (k : ℕ → ℝ) (s ω : Fin K → ℝ)
    (hk : ∀ j, k j = ∑ i, ω i * (rc + Δ * s i) ^ j) :
    kernelMomentEstimate K rc Δ k = momentMap K (s, ω) := by
  funext m
  simp only [kernelMomentEstimate, momentMap, hk]
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
theorem p1_kernel_centring_perturb {K : ℕ} (rc Δ : ℝ) (hrc : |rc| ≤ 1) (hΔ0 : 0 < Δ) (hΔ1 : Δ ≤ 1)
    (k k' : ℕ → ℝ) (η : ℝ) (hη0 : 0 ≤ η) (hη : ∀ j < 2 * K, |k' j - k j| ≤ η) :
    dist (kernelMomentEstimate K rc Δ k') (kernelMomentEstimate K rc Δ k) ≤
      2 ^ (2 * K) * η * (Δ ^ (2 * K - 1))⁻¹ := by
  refine (dist_pi_le_iff (by positivity)).mpr (fun m => ?_)
  have hm := m.isLt
  rw [Real.dist_eq]
  simp only [kernelMomentEstimate]
  rw [← mul_sub, ← sum_sub_distrib, abs_mul, abs_inv, abs_of_pos (pow_pos hΔ0 _)]
  have hsum : |∑ j ∈ range ((m : ℕ) + 1), (((m : ℕ).choose j : ℝ) * (-rc) ^ ((m : ℕ) - j) * k' j -
      ((m : ℕ).choose j : ℝ) * (-rc) ^ ((m : ℕ) - j) * k j)| ≤ 2 ^ (2 * K) * η := by
    refine (abs_sum_le_sum_abs _ _).trans ?_
    calc ∑ j ∈ range ((m : ℕ) + 1), |((m : ℕ).choose j : ℝ) * (-rc) ^ ((m : ℕ) - j) * k' j -
          ((m : ℕ).choose j : ℝ) * (-rc) ^ ((m : ℕ) - j) * k j|
        ≤ ∑ j ∈ range ((m : ℕ) + 1), 1 ^ j * |rc| ^ ((m : ℕ) - j) * ((m : ℕ).choose j : ℝ) * η := by
          refine sum_le_sum (fun j hj => ?_)
          rw [← mul_sub, abs_mul, abs_mul, abs_pow, abs_neg, Nat.abs_cast, one_pow, one_mul]
          have := hη j (by have := mem_range.mp hj; omega)
          calc ((m : ℕ).choose j : ℝ) * |rc| ^ ((m : ℕ) - j) * |k' j - k j|
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

/-- One tagged term: `|w' r'^j - w r^j| ≤ |w' - w| + |w| j |r' - r|` for rates of modulus at most one. -/
theorem p1_tag_term_perturb (w w' r r' : ℝ) (hr : |r| ≤ 1) (hr' : |r'| ≤ 1) (j : ℕ) :
    |w' * r' ^ j - w * r ^ j| ≤ |w' - w| + |w| * j * |r' - r| := by
  have e : w' * r' ^ j - w * r ^ j = (w' - w) * r' ^ j + w * (r' ^ j - r ^ j) := by ring
  rw [e]
  refine (abs_add_le _ _).trans (add_le_add ?_ ?_)
  · rw [abs_mul, abs_pow]
    calc |w' - w| * |r'| ^ j ≤ |w' - w| * 1 := by gcongr; exact pow_le_one₀ (abs_nonneg _) hr'
      _ = |w' - w| := mul_one _
  · rw [abs_mul]
    have hp := abs_pow_sub_pow_le (a := r') (b := r) (n := j)
    have hmax : max |r'| |r| ^ (j - 1) ≤ 1 := pow_le_one₀ (le_max_of_le_left (abs_nonneg _)) (max_le hr' hr)
    have h2 : |r' ^ j - r ^ j| ≤ |r' - r| * j := by
      calc |r' ^ j - r ^ j| ≤ |r' - r| * j * max |r'| |r| ^ (j - 1) := hp
        _ ≤ |r' - r| * j * 1 := by gcongr
        _ = |r' - r| * j := mul_one _
    calc |w| * |r' ^ j - r ^ j| ≤ |w| * (|r' - r| * j) := by gcongr
      _ = |w| * j * |r' - r| := by ring

/-- The residual kernel (estimated kernel minus estimated tagged terms) is within
`η = e_k + m (e_w + W_t · 2K · e_r)` of the untagged kernel at every lag below `2K`. -/
theorem p1_residual_kernel_close {K m : ℕ} (wt rt wt' rt' : Fin m → ℝ) (Wt : ℝ)
    (hWt : ∀ i, |wt i| ≤ Wt) (hrt : ∀ i, |rt i| ≤ 1) (hrt' : ∀ i, |rt' i| ≤ 1)
    (ku k khat : ℕ → ℝ) (hk : ∀ j, k j = (∑ i, wt i * rt i ^ j) + ku j)
    (ek ew er : ℝ) (her : 0 ≤ er)
    (hkhat : ∀ j < 2 * K, |khat j - k j| ≤ ek) (hw : ∀ i, |wt' i - wt i| ≤ ew)
    (hr : ∀ i, |rt' i - rt i| ≤ er) :
    ∀ j < 2 * K, |(khat j - ∑ i, wt' i * rt' i ^ j) - ku j| ≤ ek + m * (ew + Wt * (2 * K) * er) := by
  intro j hj
  have e : (khat j - ∑ i, wt' i * rt' i ^ j) - ku j =
      (khat j - k j) - ∑ i, (wt' i * rt' i ^ j - wt i * rt i ^ j) := by
    rw [hk j, sum_sub_distrib]; ring
  rw [e]
  refine (abs_sub _ _).trans (add_le_add (hkhat j hj) ?_)
  refine (abs_sum_le_sum_abs _ _).trans ?_
  have hjK : (j : ℝ) ≤ 2 * K := by exact_mod_cast hj.le
  calc ∑ i, |wt' i * rt' i ^ j - wt i * rt i ^ j| ≤ ∑ _i : Fin m, (ew + Wt * (2 * K) * er) := by
        refine sum_le_sum (fun i _ => ?_)
        refine (p1_tag_term_perturb _ _ _ _ (hrt i) (hrt' i) j).trans (add_le_add (hw i) ?_)
        have hW0 : 0 ≤ Wt := (abs_nonneg _).trans (hWt i)
        have hb : |wt i| * j * |rt' i - rt i| ≤ Wt * (2 * K) * er := by
          gcongr
          · exact hWt i
          · exact hr i
        exact hb
    _ = m * (ew + Wt * (2 * K) * er) := by
        rw [sum_const, card_univ, Fintype.card_fin, nsmul_eq_mul]

/-- **Partial disclosure, upper bound: deterministic core (core `thm:partial`(ii)).** On a class of `K` untagged
groups with rescaled nodes in a compact `γ`-separated set `S ⊆ [-1,1]^K` and weights in `[ω_min, ω_max]`, there are
constants `c₁, L > 0` such that for any `m` tagged groups with weights bounded by `W_t` and rates of modulus at most
one: if the kernel taps are estimated within `e_k`, the tagged weights within `e_w` and the tagged rates within
`e_r`, and `δ = 2^{2K} η Δ^{-(2K-1)} ≤ c₁` with `η = e_k + m (e_w + W_t · 2K · e_r)`, then an ordered
representation with nonzero weights matching the residual moments exists, it is unique, and it recovers every
untagged weight to within `L δ`. The tagged groups enter only through `η`. -/
theorem p1_partial_upper_deterministic {K m : ℕ}
    (S : Set (Fin K → ℝ)) (hS : IsCompact S) (γ : ℝ) (hγ : 0 < γ)
    (hSsep : ∀ s ∈ S, ∀ i j, i < j → γ ≤ s j - s i) (hSbox : ∀ s ∈ S, ∀ i, |s i| ≤ 1)
    (ωmin ωmax : ℝ) (hωmin : 0 < ωmin) (hωle : ωmin ≤ ωmax) (rc : ℝ) (hrc : |rc| < 1) :
    ∃ c₁ > 0, ∃ L > 0, ∀ Δ : ℝ, 0 < Δ → Δ ≤ 1 - |rc| →
      ∀ s ∈ S, ∀ ω : Fin K → ℝ, (∀ i, ω i ∈ Set.Icc ωmin ωmax) →
      ∀ (wt rt wt' rt' : Fin m → ℝ) (Wt : ℝ), (∀ i, |wt i| ≤ Wt) → (∀ i, |rt i| ≤ 1) → (∀ i, |rt' i| ≤ 1) →
      ∀ (k khat : ℕ → ℝ), (∀ j, k j = (∑ i, wt i * rt i ^ j) + ∑ i, ω i * (rc + Δ * s i) ^ j) →
      ∀ (ek ew er : ℝ), 0 ≤ ek → 0 ≤ ew → 0 ≤ er →
      (∀ j < 2 * K, |khat j - k j| ≤ ek) → (∀ i, |wt' i - wt i| ≤ ew) → (∀ i, |rt' i - rt i| ≤ er) →
      2 ^ (2 * K) * (ek + m * (ew + Wt * (2 * K) * er)) * (Δ ^ (2 * K - 1))⁻¹ ≤ c₁ →
      (∃ x : PronyParam K, StrictMono x.1 ∧ (∀ i, x.2 i ≠ 0) ∧
          momentMap K x = kernelMomentEstimate K rc Δ (fun j => khat j - ∑ i, wt' i * rt' i ^ j)) ∧
      ∀ x : PronyParam K, StrictMono x.1 → (∀ i, x.2 i ≠ 0) →
          momentMap K x = kernelMomentEstimate K rc Δ (fun j => khat j - ∑ i, wt' i * rt' i ^ j) →
          ∀ i, |x.2 i - ω i| ≤
            L * (2 ^ (2 * K) * (ek + m * (ew + Wt * (2 * K) * er)) * (Δ ^ (2 * K - 1))⁻¹) := by
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
  refine ⟨min ρ₀ (min (γ / (4 * L)) (ωmin / (2 * L))), by positivity, L, hL, ?_⟩
  intro Δ hΔ0 hΔ1 s hs ω hω wt rt wt' rt' Wt hWt hrt hrt' k khat hk ek ew er hek hew her hkhat hw hr hδ
  have hΔle1 : Δ ≤ 1 := hΔ1.trans (by linarith [abs_nonneg rc])
  set η := ek + m * (ew + Wt * (2 * K) * er) with hηdef
  have hW0 : 0 ≤ Wt ∨ m = 0 := by
    rcases Nat.eq_zero_or_pos m with h | h
    · exact Or.inr h
    · exact Or.inl ((abs_nonneg _).trans (hWt ⟨0, h⟩))
  have hη0 : 0 ≤ η := by
    rcases hW0 with h | h
    · positivity
    · simp [hηdef, h, hek]
  set ku : ℕ → ℝ := fun j => ∑ i, ω i * (rc + Δ * s i) ^ j with hku
  have hres := p1_residual_kernel_close (K := K) wt rt wt' rt' Wt hWt hrt hrt' ku k khat hk ek ew er her hkhat hw hr
  set δ := 2 ^ (2 * K) * η * (Δ ^ (2 * K - 1))⁻¹ with hδdef
  have hdist : dist (kernelMomentEstimate K rc Δ (fun j => khat j - ∑ i, wt' i * rt' i ^ j))
      (momentMap K (s, ω)) ≤ δ := by
    rw [← p1_kernel_centring_true rc Δ hΔ0.ne' ku s ω (fun j => rfl)]
    exact p1_kernel_centring_perturb rc Δ hrc.le hΔ0 hΔle1 ku _ η hη0 hres
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

end CurrentMM
