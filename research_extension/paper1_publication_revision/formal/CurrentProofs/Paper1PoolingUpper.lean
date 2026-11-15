import CurrentProofs.Paper1PronyUpper

/-!
# Paper 1: pooling markets, the upper bounds (local and global)

Core `thm:pool`(ii) and (iv). The same `K` algorithms (common memory nodes `s`) trade in `D` markets with weights
`W j i`. The rescaled moments of orders `0, …, l` in every market form the pooled moment map. This file proves:

* `p1_uniform_local_injectivity`: a `C¹` map whose derivative is injective on a compact set is uniformly
  bi-Lipschitz on balls of one radius around that set (no equal-dimension assumption: the pooled map has more
  equations than unknowns).
* `p1_min_distance_local`: the local minimum-distance estimator inherits the error of the data, times `2 / c`.
* `p1_global_lower_bound`, `p1_min_distance_global`: an injective immersion of a compact set is bi-Lipschitz onto
  its image, so the global minimum-distance estimator has the same order of error (part (iv)).
* `p1_pool_centring_perturb`: per-market centring and rescaling amplify kernel errors by `2^{l+1} Δ^{-l}`.
* `p1_pool_upper_local`, `p1_pool_upper_global`: the two upper bounds, with error
  `(2 / c) · 2^{l+1} · e · Δ^{-l}` in the parameters when every kernel tap of order at most `l` is within `e`.
  Condition (R) of the paper is the hypothesis that the derivative is injective; it is verified exactly for
  `K ≤ 8` by the modular rank computation, not in Lean.
* `p1_pool_injective_top`, `p1_pool_fderiv_injective_top`: at order `2K - 1` the pooled map is injective on ordered
  configurations with nonzero weights in one market and its derivative is injective at every such configuration;
  so `l_g ≤ 2K - 1` and pooling never needs more data than one market.
-/

namespace CurrentMM

open Set Metric Finset
open scoped NNReal

section General

variable {E F : Type*} [NormedAddCommGroup E] [NormedSpace ℝ E] [FiniteDimensional ℝ E]
  [NormedAddCommGroup F] [NormedSpace ℝ F] [FiniteDimensional ℝ F]

/-- **Uniform local injectivity.** If `f` is `C¹` and its derivative is injective on a compact set `Q`, there are
`r, c > 0` with `c ‖u - w‖ ≤ ‖f u - f w‖` for all `u, w` within `r` of a common point of `Q`. -/
theorem p1_uniform_local_injectivity {f : E → F} (hf : ContDiff ℝ 1 f) {Q : Set E} (hQ : IsCompact Q)
    (hinj : ∀ x ∈ Q, Function.Injective (fderiv ℝ f x)) :
    ∃ r > 0, ∃ c > 0, ∀ x ∈ Q, ∀ u ∈ closedBall x r, ∀ w ∈ closedBall x r,
      c * ‖u - w‖ ≤ ‖f u - f w‖ := by
  obtain ⟨m, hm, hlow⟩ := p1_uniform_lower_bound_fderiv hf hQ hinj
  have hK : IsCompact (cthickening 1 Q) := hQ.cthickening
  have huc : UniformContinuousOn (fderiv ℝ f) (cthickening 1 Q) :=
    hK.uniformContinuousOn_of_continuous (hf.continuous_fderiv one_ne_zero).continuousOn
  obtain ⟨δ, hδ, hδc⟩ := Metric.uniformContinuousOn_iff_le.mp huc (m / 2) (by positivity)
  set r := min δ 1 with hr
  have hr0 : 0 < r := lt_min hδ one_pos
  refine ⟨r, hr0, m / 2, by positivity, ?_⟩
  intro x hx u hu w hw
  have hball : closedBall x r ⊆ cthickening 1 Q :=
    (closedBall_subset_cthickening hx r).trans (cthickening_mono (min_le_right _ _) Q)
  have hxK : x ∈ cthickening 1 Q := hball (mem_closedBall_self hr0.le)
  set g : E → F := fun z => f z - fderiv ℝ f x z with hg
  have hgd : ∀ z, HasFDerivAt g (fderiv ℝ f z - fderiv ℝ f x) z := fun z =>
    ((hf.differentiable one_ne_zero) z).hasFDerivAt.sub (fderiv ℝ f x).hasFDerivAt
  have hbound : ∀ z ∈ closedBall x r, ‖fderiv ℝ g z‖ ≤ m / 2 := by
    intro z hz
    rw [(hgd z).fderiv]
    have := hδc z (hball hz) x hxK ((mem_closedBall.mp hz).trans (min_le_left _ _))
    rwa [dist_eq_norm] at this
  have hmv := (convex_closedBall x r).norm_image_sub_le_of_norm_fderiv_le
    (fun z _ => (hgd z).differentiableAt) hbound hw hu
  have e : g u - g w = f u - f w - fderiv ℝ f x (u - w) := by
    simp only [hg, map_sub]; abel
  rw [e] at hmv
  have hl := hlow x hx (u - w)
  have htri : ‖fderiv ℝ f x (u - w)‖ ≤ ‖f u - f w‖ + ‖f u - f w - fderiv ℝ f x (u - w)‖ := by
    have := norm_sub_le (f u - f w) (f u - f w - fderiv ℝ f x (u - w))
    simpa using this
  linarith

/-- **Local minimum-distance estimator.** With `r, c` as above, any `θ` within `r` of `x ∈ Q` that fits the data
`t̂` at least as well as `x` does is within `(2 / c) ‖t̂ - f x‖` of `x`. -/
theorem p1_min_distance_local {f : E → F} {r c : ℝ} (hc : 0 < c) {Q : Set E}
    (hloc : ∀ x ∈ Q, ∀ u ∈ closedBall x r, ∀ w ∈ closedBall x r, c * ‖u - w‖ ≤ ‖f u - f w‖)
    {x : E} (hx : x ∈ Q) (hr : 0 ≤ r) (that : F) {θ : E} (hθ : θ ∈ closedBall x r)
    (hfit : ‖f θ - that‖ ≤ ‖f x - that‖) :
    ‖θ - x‖ ≤ 2 / c * ‖that - f x‖ := by
  have h1 := hloc x hx θ hθ x (mem_closedBall_self hr)
  have h2 : ‖f θ - f x‖ ≤ 2 * ‖that - f x‖ := by
    calc ‖f θ - f x‖ = ‖(f θ - that) + (that - f x)‖ := by congr 1; abel
      _ ≤ ‖f θ - that‖ + ‖that - f x‖ := norm_add_le _ _
      _ ≤ ‖f x - that‖ + ‖that - f x‖ := by gcongr
      _ = 2 * ‖that - f x‖ := by rw [norm_sub_rev]; ring
  rw [div_mul_eq_mul_div, le_div_iff₀ hc]
  linarith

/-- A minimizer of the fit over a nonempty compact set exists. -/
theorem p1_min_distance_exists {f : E → F} (hf : Continuous f) {A : Set E} (hA : IsCompact A)
    (hne : A.Nonempty) (that : F) : ∃ θ ∈ A, ∀ z ∈ A, ‖f θ - that‖ ≤ ‖f z - that‖ := by
  obtain ⟨θ, hθ, hmin⟩ := hA.exists_isMinOn hne ((hf.sub continuous_const).norm.continuousOn)
  exact ⟨θ, hθ, fun z hz => isMinOn_iff.mp hmin z hz⟩

/-- **Global lower bound (core `thm:pool`(iv)).** An injective `C¹` map whose derivative is injective on a compact
set `Q` is bi-Lipschitz onto its image: `c ‖u - w‖ ≤ ‖f u - f w‖` for all `u, w ∈ Q`. -/
theorem p1_global_lower_bound {f : E → F} (hf : ContDiff ℝ 1 f) {Q : Set E} (hQ : IsCompact Q)
    (hinj : ∀ x ∈ Q, Function.Injective (fderiv ℝ f x)) (hInj : Set.InjOn f Q) :
    ∃ c > 0, ∀ u ∈ Q, ∀ w ∈ Q, c * ‖u - w‖ ≤ ‖f u - f w‖ := by
  obtain ⟨r, hr, cl, hcl, hloc⟩ := p1_uniform_local_injectivity hf hQ hinj
  obtain ⟨Dm, hDm⟩ := hQ.isBounded.subset_closedBall (0 : E)
  set A : Set (E × E) := (Q ×ˢ Q) ∩ {p | r ≤ ‖p.1 - p.2‖} with hA
  have hAc : IsCompact A :=
    (hQ.prod hQ).inter_right (isClosed_le continuous_const (continuous_fst.sub continuous_snd).norm)
  have hcont : Continuous fun p : E × E => ‖f p.1 - f p.2‖ :=
    ((hf.continuous.comp continuous_fst).sub (hf.continuous.comp continuous_snd)).norm
  set Dp : ℝ := 2 * max Dm 1 with hDp
  have hDp0 : 0 < Dp := by positivity
  have hdiam : ∀ u ∈ Q, ∀ w ∈ Q, ‖u - w‖ ≤ Dp := by
    intro u hu w hw
    have h1 := mem_closedBall_zero_iff.mp (hDm hu)
    have h2 := mem_closedBall_zero_iff.mp (hDm hw)
    calc ‖u - w‖ ≤ ‖u‖ + ‖w‖ := norm_sub_le _ _
      _ ≤ Dm + Dm := add_le_add h1 h2
      _ ≤ Dp := by rw [hDp]; linarith [le_max_left Dm 1]
  by_cases hne : A.Nonempty
  · obtain ⟨p, hp, hmin⟩ := hAc.exists_isMinOn hne hcont.continuousOn
    have hpne : p.1 ≠ p.2 := by
      intro h
      have := hp.2
      simp only [Set.mem_setOf_eq, h, sub_self, norm_zero] at this
      linarith
    have hv : 0 < ‖f p.1 - f p.2‖ := by
      rw [norm_pos_iff, sub_ne_zero]
      exact fun h => hpne (hInj hp.1.1 hp.1.2 h)
    refine ⟨min cl (‖f p.1 - f p.2‖ / Dp), lt_min hcl (by positivity), ?_⟩
    intro u hu w hw
    by_cases hfar : r ≤ ‖u - w‖
    · have hmem : (u, w) ∈ A := ⟨⟨hu, hw⟩, hfar⟩
      have hle := isMinOn_iff.mp hmin _ hmem
      calc min cl (‖f p.1 - f p.2‖ / Dp) * ‖u - w‖ ≤ ‖f p.1 - f p.2‖ / Dp * ‖u - w‖ := by
            gcongr; exact min_le_right _ _
        _ ≤ ‖f p.1 - f p.2‖ / Dp * Dp := by gcongr; exact hdiam u hu w hw
        _ = ‖f p.1 - f p.2‖ := by field_simp
        _ ≤ ‖f u - f w‖ := hle
    · push_neg at hfar
      have hwb : w ∈ closedBall u r := by
        rw [mem_closedBall, dist_eq_norm, norm_sub_rev]; exact hfar.le
      calc min cl (‖f p.1 - f p.2‖ / Dp) * ‖u - w‖ ≤ cl * ‖u - w‖ := by
            gcongr; exact min_le_left _ _
        _ ≤ ‖f u - f w‖ := hloc u hu u (mem_closedBall_self hr.le) w hwb
  · refine ⟨cl, hcl, fun u hu w hw => ?_⟩
    have hnear : ‖u - w‖ < r := by
      by_contra h
      push_neg at h
      exact hne ⟨(u, w), ⟨hu, hw⟩, h⟩
    have hwb : w ∈ closedBall u r := by
      rw [mem_closedBall, dist_eq_norm, norm_sub_rev]; exact hnear.le
    exact hloc u hu u (mem_closedBall_self hr.le) w hwb

/-- **Global minimum-distance estimator.** If `f` is bi-Lipschitz on `Q` with constant `c`, any `θ ∈ Q` that fits
the data at least as well as the truth `x ∈ Q` is within `(2 / c) ‖t̂ - f x‖` of `x`. -/
theorem p1_min_distance_global {f : E → F} {c : ℝ} (hc : 0 < c) {Q : Set E}
    (hlow : ∀ u ∈ Q, ∀ w ∈ Q, c * ‖u - w‖ ≤ ‖f u - f w‖) {x θ : E} (hx : x ∈ Q) (hθ : θ ∈ Q) (that : F)
    (hfit : ‖f θ - that‖ ≤ ‖f x - that‖) :
    ‖θ - x‖ ≤ 2 / c * ‖that - f x‖ := by
  have h1 := hlow θ hθ x hx
  have h2 : ‖f θ - f x‖ ≤ 2 * ‖that - f x‖ := by
    calc ‖f θ - f x‖ = ‖(f θ - that) + (that - f x)‖ := by congr 1; abel
      _ ≤ ‖f θ - that‖ + ‖that - f x‖ := norm_add_le _ _
      _ ≤ ‖f x - that‖ + ‖that - f x‖ := by gcongr
      _ = 2 * ‖that - f x‖ := by rw [norm_sub_rev]; ring
  rw [div_mul_eq_mul_div, le_div_iff₀ hc]
  linarith

end General

/-! ### The pooled moment map -/

/-- Configurations: common nodes and one weight vector per market. -/
abbrev PoolParam (K D : ℕ) := (Fin K → ℝ) × (Fin D → Fin K → ℝ)

/-- Rescaled moments of orders `0, …, l` in every market. -/
def pooledMomentMap (K D l : ℕ) (x : PoolParam K D) : Fin D → Fin (l + 1) → ℝ :=
  fun j p => ∑ i, x.2 j i * x.1 i ^ (p : ℕ)

theorem p1_pooledMomentMap_contDiff (K D l : ℕ) : ContDiff ℝ 1 (pooledMomentMap K D l) := by
  refine contDiff_pi.2 fun j => contDiff_pi.2 fun p => ?_
  show ContDiff ℝ 1 (fun x : PoolParam K D => ∑ i, x.2 j i * x.1 i ^ (p : ℕ))
  refine ContDiff.sum fun i _ => ?_
  exact (((contDiff_apply ℝ ℝ i).comp (contDiff_apply ℝ (Fin K → ℝ) j)).comp contDiff_snd).mul
    (((contDiff_apply ℝ ℝ i).comp contDiff_fst).pow _)

/-- The derivative of the pooled moment map. -/
theorem p1_pooledMomentMap_fderiv_apply (K D l : ℕ) (x v : PoolParam K D) (j : Fin D) (p : Fin (l + 1)) :
    fderiv ℝ (pooledMomentMap K D l) x v j p =
      ∑ i, (v.2 j i * x.1 i ^ (p : ℕ) + x.2 j i * ((p : ℕ) * x.1 i ^ ((p : ℕ) - 1)) * v.1 i) := by
  have hd : DifferentiableAt ℝ (pooledMomentMap K D l) x :=
    (p1_pooledMomentMap_contDiff K D l).differentiable one_ne_zero x
  have hline : HasDerivAt (fun t : ℝ => x + t • v) v 0 := by
    simpa using ((hasDerivAt_id (0 : ℝ)).smul_const v).const_add x
  have hl : HasFDerivAt (pooledMomentMap K D l) (fderiv ℝ (pooledMomentMap K D l) x) (x + (0 : ℝ) • v) := by
    rw [zero_smul, add_zero]; exact hd.hasFDerivAt
  have h1 : HasDerivAt (fun t : ℝ => pooledMomentMap K D l (x + t • v))
      (fderiv ℝ (pooledMomentMap K D l) x v) 0 :=
    HasFDerivAt.comp_hasDerivAt (l := pooledMomentMap K D l) (0 : ℝ) hl hline
  have h2 : HasDerivAt (fun t : ℝ => pooledMomentMap K D l (x + t • v) j p)
      (∑ i, (v.2 j i * x.1 i ^ (p : ℕ) + x.2 j i * ((p : ℕ) * x.1 i ^ ((p : ℕ) - 1)) * v.1 i)) 0 := by
    have hfun : (fun t : ℝ => pooledMomentMap K D l (x + t • v) j p) =
        fun t => ∑ i, (x.2 j i + t * v.2 j i) * (x.1 i + t * v.1 i) ^ (p : ℕ) := by
      funext t; simp [pooledMomentMap, smul_eq_mul]
    rw [hfun]
    refine HasDerivAt.fun_sum fun i _ => ?_
    have ha : HasDerivAt (fun t : ℝ => x.2 j i + t * v.2 j i) (v.2 j i) 0 := by
      simpa using ((hasDerivAt_id (0 : ℝ)).mul_const (v.2 j i)).const_add (x.2 j i)
    have hb : HasDerivAt (fun t : ℝ => x.1 i + t * v.1 i) (v.1 i) 0 := by
      simpa using ((hasDerivAt_id (0 : ℝ)).mul_const (v.1 i)).const_add (x.1 i)
    convert ha.mul (hb.pow (p : ℕ)) using 1
    simp; ring
  have h3 := hasDerivAt_pi.mp h1 j
  exact (hasDerivAt_pi.mp h3 p).unique h2

/-! ### Order `2K - 1`: one market identifies everything -/

/-- **Injectivity at order `2K - 1`.** Two configurations with strictly increasing nodes, nonzero weights in market
`0` and the same rescaled moments of orders `0, …, 2K - 1` in every market are equal. -/
theorem p1_pool_injective_top {K D' : ℕ} (x y : PoolParam K (D' + 1)) (hx : StrictMono x.1)
    (hy : StrictMono y.1) (hxw : ∀ i, x.2 0 i ≠ 0) (hyw : ∀ i, y.2 0 i ≠ 0)
    (h : pooledMomentMap K (D' + 1) (2 * K - 1) x = pooledMomentMap K (D' + 1) (2 * K - 1) y) : x = y := by
  rcases Nat.eq_zero_or_pos K with hK | hK
  · subst hK
    refine Prod.ext (funext fun i => i.elim0) (funext fun j => funext fun i => i.elim0)
  have hlen : 2 * K - 1 + 1 = 2 * K := by omega
  have hmom : ∀ j, ∀ m < 2 * K, ∑ i, x.2 j i * x.1 i ^ m = ∑ i, y.2 j i * y.1 i ^ m := by
    intro j m hm
    have := congrFun (congrFun h j) ⟨m, by omega⟩
    simpa [pooledMomentMap] using this
  have h0 : ((x.1, x.2 0) : PronyParam K) = (y.1, y.2 0) :=
    p1_ordered_representation_unique (x.1, x.2 0) (y.1, y.2 0) hx hy hxw hyw
      (funext fun m => by simpa [momentMap] using hmom 0 m m.isLt)
  have hs : x.1 = y.1 := (Prod.ext_iff.mp h0).1
  refine Prod.ext hs (funext fun j => ?_)
  -- the difference of the weights in market `j` annihilates the first `2K` powers of the common nodes
  have hzero : ∀ m < 2 * K, ∑ i, ((fun i => x.2 j i - y.2 j i) i * x.1 i ^ m +
      x.2 0 i * ((m : ℝ) * x.1 i ^ (m - 1)) * (0 : Fin K → ℝ) i) = 0 := by
    intro m hm
    have := hmom j m hm
    rw [← hs] at this
    simp only [Pi.zero_apply, mul_zero, add_zero, sub_mul, sum_sub_distrib]
    linarith
  obtain ⟨-, hd⟩ := p1_hermite_functional x.1 (x.2 0) 0 (fun i => x.2 j i - y.2 j i) hx.injective hxw hzero
  funext i
  have := congrFun hd i
  simp only [Pi.zero_apply] at this
  linarith

/-- **Immersion at order `2K - 1`.** The derivative of the pooled moment map of orders `0, …, 2K - 1` is injective at
every configuration with distinct nodes and nonzero weights in market `0`. -/
theorem p1_pool_fderiv_injective_top {K D' : ℕ} (x : PoolParam K (D' + 1)) (hs : Function.Injective x.1)
    (hw : ∀ i, x.2 0 i ≠ 0) : Function.Injective (fderiv ℝ (pooledMomentMap K (D' + 1) (2 * K - 1)) x) := by
  rcases Nat.eq_zero_or_pos K with hK | hK
  · subst hK
    intro u v _
    exact Prod.ext (funext fun i => i.elim0) (funext fun j => funext fun i => i.elim0)
  refine (injective_iff_map_eq_zero _).mpr (fun v hv => ?_)
  have hcomp : ∀ j, ∀ m < 2 * K,
      ∑ i, (v.2 j i * x.1 i ^ m + x.2 j i * ((m : ℝ) * x.1 i ^ (m - 1)) * v.1 i) = 0 := by
    intro j m hm
    have := congrFun (congrFun hv j) ⟨m, by omega⟩
    rw [p1_pooledMomentMap_fderiv_apply] at this
    simpa using this
  obtain ⟨hu, hd0⟩ := p1_hermite_functional x.1 (x.2 0) v.1 (v.2 0) hs hw (hcomp 0)
  refine Prod.ext hu (funext fun j => ?_)
  have hzero : ∀ m < 2 * K, ∑ i, (v.2 j i * x.1 i ^ m + x.2 0 i * ((m : ℝ) * x.1 i ^ (m - 1)) * (0 : Fin K → ℝ) i) = 0 := by
    intro m hm
    have := hcomp j m hm
    rw [hu] at this
    simpa using this
  obtain ⟨-, hd⟩ := p1_hermite_functional x.1 (x.2 0) 0 (v.2 j) hs hw hzero
  exact hd

/-! ### From kernel taps to rescaled moments, market by market -/

/-- Centre each market's kernel at `r_c` and rescale the `p`-th centred moment by `Δ^{-p}`. -/
noncomputable def pooledMomentEstimate (D l : ℕ) (rc Δ : ℝ) (k : Fin D → ℕ → ℝ) : Fin D → Fin (l + 1) → ℝ :=
  fun j p => (Δ ^ (p : ℕ))⁻¹ *
    ∑ t ∈ range ((p : ℕ) + 1), ((p : ℕ).choose t : ℝ) * (-rc) ^ ((p : ℕ) - t) * k j t

theorem p1_pool_centring_true {K D l : ℕ} (rc Δ : ℝ) (hΔ : Δ ≠ 0) (k : Fin D → ℕ → ℝ) (x : PoolParam K D)
    (hk : ∀ j t, k j t = ∑ i, x.2 j i * (rc + Δ * x.1 i) ^ t) :
    pooledMomentEstimate D l rc Δ k = pooledMomentMap K D l x := by
  funext j p
  simp only [pooledMomentEstimate, pooledMomentMap, hk]
  have hpow : ∀ i, ∑ t ∈ range ((p : ℕ) + 1), ((p : ℕ).choose t : ℝ) * (-rc) ^ ((p : ℕ) - t) *
      (x.2 j i * (rc + Δ * x.1 i) ^ t) = x.2 j i * (Δ ^ (p : ℕ) * x.1 i ^ (p : ℕ)) := by
    intro i
    have e := add_pow (rc + Δ * x.1 i) (-rc) (p : ℕ)
    rw [show rc + Δ * x.1 i + -rc = Δ * x.1 i by ring, mul_pow] at e
    rw [e, mul_sum]
    refine sum_congr rfl (fun t _ => by ring)
  have hswap : ∑ t ∈ range ((p : ℕ) + 1), ((p : ℕ).choose t : ℝ) * (-rc) ^ ((p : ℕ) - t) *
      ∑ i, x.2 j i * (rc + Δ * x.1 i) ^ t = ∑ i, x.2 j i * (Δ ^ (p : ℕ) * x.1 i ^ (p : ℕ)) := by
    simp_rw [mul_sum]
    rw [sum_comm]
    exact sum_congr rfl (fun i _ => hpow i)
  rw [hswap, mul_sum]
  refine sum_congr rfl (fun i _ => ?_)
  field_simp

theorem p1_pool_centring_perturb {D l : ℕ} (rc Δ : ℝ) (hrc : |rc| ≤ 1) (hΔ0 : 0 < Δ) (hΔ1 : Δ ≤ 1)
    (k k' : Fin D → ℕ → ℝ) (e : ℝ) (he0 : 0 ≤ e) (he : ∀ j, ∀ t ≤ l, |k' j t - k j t| ≤ e) :
    dist (pooledMomentEstimate D l rc Δ k') (pooledMomentEstimate D l rc Δ k) ≤
      2 ^ l * e * (Δ ^ l)⁻¹ := by
  refine (dist_pi_le_iff (by positivity)).mpr (fun j => (dist_pi_le_iff (by positivity)).mpr (fun p => ?_))
  have hp := p.isLt
  rw [Real.dist_eq]
  simp only [pooledMomentEstimate]
  rw [← mul_sub, ← sum_sub_distrib, abs_mul, abs_inv, abs_of_pos (pow_pos hΔ0 _)]
  have hsum : |∑ t ∈ range ((p : ℕ) + 1), (((p : ℕ).choose t : ℝ) * (-rc) ^ ((p : ℕ) - t) * k' j t -
      ((p : ℕ).choose t : ℝ) * (-rc) ^ ((p : ℕ) - t) * k j t)| ≤ 2 ^ l * e := by
    refine (abs_sum_le_sum_abs _ _).trans ?_
    calc ∑ t ∈ range ((p : ℕ) + 1), |((p : ℕ).choose t : ℝ) * (-rc) ^ ((p : ℕ) - t) * k' j t -
          ((p : ℕ).choose t : ℝ) * (-rc) ^ ((p : ℕ) - t) * k j t|
        ≤ ∑ t ∈ range ((p : ℕ) + 1), 1 ^ t * |rc| ^ ((p : ℕ) - t) * ((p : ℕ).choose t : ℝ) * e := by
          refine sum_le_sum (fun t ht => ?_)
          rw [← mul_sub, abs_mul, abs_mul, abs_pow, abs_neg, Nat.abs_cast, one_pow, one_mul]
          have := he j t (by have := mem_range.mp ht; omega)
          calc ((p : ℕ).choose t : ℝ) * |rc| ^ ((p : ℕ) - t) * |k' j t - k j t|
              ≤ ((p : ℕ).choose t : ℝ) * |rc| ^ ((p : ℕ) - t) * e := by gcongr
            _ = |rc| ^ ((p : ℕ) - t) * ((p : ℕ).choose t : ℝ) * e := by ring
      _ = (1 + |rc|) ^ (p : ℕ) * e := by rw [add_pow, sum_mul]
      _ ≤ 2 ^ l * e := by
          gcongr
          calc (1 + |rc|) ^ (p : ℕ) ≤ 2 ^ (p : ℕ) := by gcongr; linarith
            _ ≤ 2 ^ l := pow_le_pow_right₀ (by norm_num) (by omega)
  have hinv : (Δ ^ (p : ℕ))⁻¹ ≤ (Δ ^ l)⁻¹ :=
    inv_anti₀ (pow_pos hΔ0 _) (pow_le_pow_of_le_one hΔ0.le hΔ1 (by omega))
  calc (Δ ^ (p : ℕ))⁻¹ * |_| ≤ (Δ ^ l)⁻¹ * (2 ^ l * e) := by gcongr
    _ = 2 ^ l * e * (Δ ^ l)⁻¹ := by ring

/-! ### The two upper bounds -/

/-- **Pooling, local upper bound (core `thm:pool`(ii)).** Let `Q` be a compact set of configurations at which the
derivative of the pooled moment map of orders `0, …, l` is injective (condition (R)). There are `r, c > 0` such that,
for every spacing `Δ ∈ (0, 1]`, every true configuration `x ∈ Q` whose market kernels are
`k_j(t) = ∑_i W_{ji} (r_c + Δ s_i)^t`, and every estimate `k̂` within `e` of `k` at every lag `t ≤ l` in every
market, the minimum-distance estimate over the ball of radius `r` around `x` is within
`(2 / c) · 2^l · e · Δ^{-l}` of `x`. The exponent `l` is that of the paper. -/
theorem p1_pool_upper_local {K D l : ℕ} {Q : Set (PoolParam K D)} (hQ : IsCompact Q)
    (hR : ∀ x ∈ Q, Function.Injective (fderiv ℝ (pooledMomentMap K D l) x)) (rc : ℝ) (hrc : |rc| ≤ 1) :
    ∃ r > 0, ∃ c > 0, ∀ Δ : ℝ, 0 < Δ → Δ ≤ 1 → ∀ x ∈ Q, ∀ k khat : Fin D → ℕ → ℝ,
      (∀ j t, k j t = ∑ i, x.2 j i * (rc + Δ * x.1 i) ^ t) →
      ∀ e : ℝ, 0 ≤ e → (∀ j, ∀ t ≤ l, |khat j t - k j t| ≤ e) →
      ∃ θ ∈ closedBall x r,
        (∀ z ∈ closedBall x r, ‖pooledMomentMap K D l θ - pooledMomentEstimate D l rc Δ khat‖ ≤
          ‖pooledMomentMap K D l z - pooledMomentEstimate D l rc Δ khat‖) ∧
        ‖θ - x‖ ≤ 2 / c * (2 ^ l * e * (Δ ^ l)⁻¹) := by
  obtain ⟨r, hr, c, hc, hloc⟩ := p1_uniform_local_injectivity (p1_pooledMomentMap_contDiff K D l) hQ hR
  refine ⟨r, hr, c, hc, fun Δ hΔ0 hΔ1 x hx k khat hk e he0 he => ?_⟩
  set that := pooledMomentEstimate D l rc Δ khat
  obtain ⟨θ, hθ, hmin⟩ := p1_min_distance_exists (p1_pooledMomentMap_contDiff K D l).continuous
    (isCompact_closedBall x r) ⟨x, mem_closedBall_self hr.le⟩ that
  refine ⟨θ, hθ, hmin, ?_⟩
  have hfit := hmin x (mem_closedBall_self hr.le)
  have hest := p1_min_distance_local hc hloc hx hr.le that hθ hfit
  have htrue : pooledMomentMap K D l x = pooledMomentEstimate D l rc Δ k :=
    (p1_pool_centring_true rc Δ hΔ0.ne' k x hk).symm
  have hdat : ‖that - pooledMomentMap K D l x‖ ≤ 2 ^ l * e * (Δ ^ l)⁻¹ := by
    rw [htrue, ← dist_eq_norm]
    exact p1_pool_centring_perturb rc Δ hrc hΔ0 hΔ1 k khat e he0 he
  calc ‖θ - x‖ ≤ 2 / c * ‖that - pooledMomentMap K D l x‖ := hest
    _ ≤ 2 / c * (2 ^ l * e * (Δ ^ l)⁻¹) := by gcongr

/-- **Pooling, global upper bound (core `thm:pool`(iv)).** On a compact class `Q` of configurations on which the pooled
moment map of orders `0, …, l` is injective and an immersion, there is `c > 0` such that the minimum-distance
estimate over the whole class is within `(2 / c) · 2^l · e · Δ^{-l}` of the truth. At `l = 2K - 1` both hypotheses
hold on any compact class of ordered configurations with nonzero weights in one market
(`p1_pool_injective_top`, `p1_pool_fderiv_injective_top`). -/
theorem p1_pool_upper_global {K D l : ℕ} {Q : Set (PoolParam K D)} (hQ : IsCompact Q) (hQne : Q.Nonempty)
    (hR : ∀ x ∈ Q, Function.Injective (fderiv ℝ (pooledMomentMap K D l) x))
    (hInj : Set.InjOn (pooledMomentMap K D l) Q) (rc : ℝ) (hrc : |rc| ≤ 1) :
    ∃ c > 0, ∀ Δ : ℝ, 0 < Δ → Δ ≤ 1 → ∀ x ∈ Q, ∀ k khat : Fin D → ℕ → ℝ,
      (∀ j t, k j t = ∑ i, x.2 j i * (rc + Δ * x.1 i) ^ t) →
      ∀ e : ℝ, 0 ≤ e → (∀ j, ∀ t ≤ l, |khat j t - k j t| ≤ e) →
      ∃ θ ∈ Q,
        (∀ z ∈ Q, ‖pooledMomentMap K D l θ - pooledMomentEstimate D l rc Δ khat‖ ≤
          ‖pooledMomentMap K D l z - pooledMomentEstimate D l rc Δ khat‖) ∧
        ‖θ - x‖ ≤ 2 / c * (2 ^ l * e * (Δ ^ l)⁻¹) := by
  obtain ⟨c, hc, hlow⟩ := p1_global_lower_bound (p1_pooledMomentMap_contDiff K D l) hQ hR hInj
  refine ⟨c, hc, fun Δ hΔ0 hΔ1 x hx k khat hk e he0 he => ?_⟩
  set that := pooledMomentEstimate D l rc Δ khat
  obtain ⟨θ, hθ, hmin⟩ := p1_min_distance_exists (p1_pooledMomentMap_contDiff K D l).continuous hQ hQne that
  refine ⟨θ, hθ, hmin, ?_⟩
  have hest := p1_min_distance_global hc hlow hx hθ that (hmin x hx)
  have htrue : pooledMomentMap K D l x = pooledMomentEstimate D l rc Δ k :=
    (p1_pool_centring_true rc Δ hΔ0.ne' k x hk).symm
  have hdat : ‖that - pooledMomentMap K D l x‖ ≤ 2 ^ l * e * (Δ ^ l)⁻¹ := by
    rw [htrue, ← dist_eq_norm]
    exact p1_pool_centring_perturb rc Δ hrc hΔ0 hΔ1 k khat e he0 he
  calc ‖θ - x‖ ≤ 2 / c * ‖that - pooledMomentMap K D l x‖ := hest
    _ ≤ 2 / c * (2 ^ l * e * (Δ ^ l)⁻¹) := by gcongr

end CurrentMM
