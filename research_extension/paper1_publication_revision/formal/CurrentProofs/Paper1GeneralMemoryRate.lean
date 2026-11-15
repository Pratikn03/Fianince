import CurrentProofs.Paper1GeneralMemoryUpper
import Mathlib.Analysis.SpecialFunctions.Pow.Asymptotics

/-!
# Paper 1, Theorem 5.6 (ii): the `1 / log(N/σ²)` rate

* `p1_gm_rate_core` (real analysis): with `D = B(1+b)` and `L = ⌊log x / (8 log D)⌋`, the finite-sample bound of
  `p1_thm_general_memory_upper` is at most `16 π ρ W log D / log x` for all large `x = N/σ²`;
* `p1_thm_general_memory_rate`: hence there is `x₀`, depending only on `(a, κ, ρ, s, W, β)`, such that for
  `N/v ≥ x₀`, with probability at least `1 - β`, every measure fitting the first `L + 1` deconvolved kernel values
  at least as well as the truth (up to `η ≤ A e`) is within `16 π ρ W log D / log(N/v)` of the true memory measure
  in every 1-Lipschitz test function vanishing at `0`. With the lower bound of `Paper1GeneralMemoryLower.lean`,
  the minimax accuracy is of exact order `1 / log(N/σ²)`.
-/

namespace CurrentMM

open MeasureTheory ProbabilityTheory Finset Real Filter
open scoped ENNReal NNReal

theorem p1_sqrt_log_le (z : ℝ) (hz : 0 < z) : Real.sqrt (Real.log z) ≤ 1 + z := by
  have h1 : Real.log z ≤ (1 + z) ^ 2 := by
    have := Real.log_le_sub_one_of_pos hz
    nlinarith
  calc Real.sqrt (Real.log z) ≤ Real.sqrt ((1 + z) ^ 2) := Real.sqrt_le_sqrt h1
    _ = 1 + z := Real.sqrt_sq (by linarith)

set_option maxHeartbeats 1000000 in
/-- **Rate, real-analysis core.** -/
theorem p1_gm_rate_core (A b B W ρ β : ℝ) (hA : 0 < A) (hb : 0 ≤ b) (hB : 1 ≤ B) (hW : 0 < W) (hρ : 0 < ρ)
    (hβ : 0 < β) (hℓ : 1 / 8 ≤ Real.log (B * (1 + b))) :
    ∃ x0 : ℝ, ∀ x ≥ x0, ∀ L : ℕ, L = ⌊Real.log x / (8 * Real.log (B * (1 + b)))⌋₊ → ∀ η : ℝ, 0 ≤ η →
      η ≤ A * (Real.sqrt 2 * Real.sqrt (Real.log (4 * ((L + 1 : ℕ) : ℝ) / β)) / Real.sqrt x) →
      Real.sqrt 2 * Real.sqrt (Real.log (4 * ((L + 1 : ℕ) : ℝ) / β)) / Real.sqrt x ≤ 1 ∧
      ρ * π / (2 * (L + 2)) * (2 * W + 2 * (A * (Real.sqrt 2 * Real.sqrt (Real.log (4 * ((L + 1 : ℕ) : ℝ) / β)) /
          Real.sqrt x) * (1 + b) ^ L) + η) +
        ρ * (L + 1) * B ^ L * (2 * (A * (Real.sqrt 2 * Real.sqrt (Real.log (4 * ((L + 1 : ℕ) : ℝ) / β)) /
          Real.sqrt x) * (1 + b) ^ L) + η) ≤
      16 * π * ρ * W * Real.log (B * (1 + b)) / Real.log x := by
  set D := B * (1 + b) with hD
  set ℓ := Real.log D with hℓdef
  have hℓ0 : 0 < ℓ := by linarith
  have hD1 : 1 ≤ D := by rw [hD]; nlinarith
  have hπ : 0 < π := pi_pos
  set c2 := Real.sqrt 2 * (1 + 8 / β) with hc2
  have hc20 : 0 < c2 := by positivity
  set K := max (max (3 * A * c2 / W) (6 * A * c2 / (4 * π * W * ℓ))) c2 with hK
  have hK0 : 0 ≤ K := le_trans hc20.le (le_max_right _ _)
  have ev0 : ∀ᶠ x in atTop, (0 : ℝ) < x := eventually_gt_atTop 0
  have ev1 : ∀ᶠ x in atTop, (1 : ℝ) ≤ Real.log x := Real.tendsto_log_atTop.eventually_ge_atTop 1
  have ev2 : ∀ᶠ x in atTop, ‖Real.log x‖ ≤ 1 * ‖x ^ (1 / 16 : ℝ)‖ :=
    (isLittleO_log_rpow_atTop (by norm_num : (0 : ℝ) < 1 / 16)).bound one_pos
  have ev3 : ∀ᶠ x in atTop, K + 1 ≤ x ^ (1 / 16 : ℝ) :=
    (tendsto_rpow_atTop (by norm_num : (0 : ℝ) < 1 / 16)).eventually_ge_atTop _
  obtain ⟨x0, hx0⟩ := eventually_atTop.mp (ev0.and (ev1.and (ev2.and ev3)))
  refine ⟨x0, fun x hx L hL η hη0 hη => ?_⟩
  obtain ⟨hxpos, hlog1, hlog2, hy⟩ := hx0 x hx
  set y := x ^ (1 / 16 : ℝ) with hydef
  have hy0 : 0 < y := rpow_pos_of_pos hxpos _
  have hy1 : 1 ≤ y := by linarith
  have hlx : Real.log x ≤ y := by
    rw [Real.norm_eq_abs, Real.norm_eq_abs, abs_of_pos hy0, one_mul] at hlog2
    exact (le_abs_self _).trans hlog2
  have hlogpos : 0 < Real.log x := by linarith
  have hy3 : K ≤ y ^ 3 := by
    have : y ≤ y ^ 3 := le_self_pow₀ hy1 (by norm_num)
    linarith
  -- √x = y^8
  have hsqrt : Real.sqrt x = y ^ 8 := by
    rw [Real.sqrt_eq_rpow, hydef, ← Real.rpow_natCast, ← Real.rpow_mul hxpos.le]; norm_num
  -- the choice of L
  have harg : 0 ≤ Real.log x / (8 * ℓ) := by positivity
  have hLle : (L : ℝ) ≤ Real.log x / (8 * ℓ) := by rw [hL]; exact Nat.floor_le harg
  have hLgt : Real.log x / (8 * ℓ) < L + 1 := by rw [hL]; exact Nat.lt_floor_add_one _
  have hL1 : (L : ℝ) + 1 ≤ 2 * Real.log x := by
    have : Real.log x / (8 * ℓ) ≤ Real.log x := div_le_self hlogpos.le (by linarith)
    linarith
  have hDL : D ^ L ≤ y ^ 2 := by
    have hlogy : Real.log y = Real.log x / 16 := by rw [hydef, Real.log_rpow hxpos]; ring
    have e1 : D ^ L = Real.exp (L * ℓ) := by rw [hℓdef, ← Real.log_pow, Real.exp_log (by positivity)]
    have e2 : y ^ 2 = Real.exp (2 * Real.log y) := by
      rw [show (2 : ℝ) * Real.log y = Real.log (y ^ 2) by rw [Real.log_pow]; norm_num, Real.exp_log (by positivity)]
    rw [e1, e2, Real.exp_le_exp, hlogy]
    have := (le_div_iff₀ (by positivity : (0 : ℝ) < 8 * ℓ)).mp hLle
    nlinarith
  have hDL1 : 1 ≤ D ^ L := one_le_pow₀ hD1
  -- the noise term
  set e := Real.sqrt 2 * Real.sqrt (Real.log (4 * ((L + 1 : ℕ) : ℝ) / β)) / Real.sqrt x with he
  have hz : 0 < 4 * ((L + 1 : ℕ) : ℝ) / β := by positivity
  have hsl : Real.sqrt (Real.log (4 * ((L + 1 : ℕ) : ℝ) / β)) ≤ (1 + 8 / β) * Real.log x := by
    refine (p1_sqrt_log_le _ hz).trans ?_
    have hzb : 4 * ((L + 1 : ℕ) : ℝ) / β ≤ 8 * Real.log x / β := by
      push_cast; rw [div_le_div_iff_of_pos_right hβ]; linarith
    have : 8 * Real.log x / β = 8 / β * Real.log x := by ring
    nlinarith [div_pos (by norm_num : (0:ℝ) < 8) hβ]
  have he0 : 0 ≤ e := by rw [he]; positivity
  have heb : e ≤ c2 * Real.log x / y ^ 8 := by
    rw [he, hsqrt, hc2]
    apply div_le_div_of_nonneg_right _ (by positivity)
    rw [mul_assoc]
    exact mul_le_mul_of_nonneg_left hsl (Real.sqrt_nonneg 2)
  set Q := e * D ^ L with hQ
  have hQ0 : 0 ≤ Q := by positivity
  have hy8 : 0 < y ^ 8 := by positivity
  have hQb : Q ≤ c2 / y ^ 3 := by
    calc Q ≤ c2 * Real.log x / y ^ 8 * y ^ 2 := mul_le_mul heb hDL (by positivity) (by positivity)
      _ ≤ c2 * y / y ^ 8 * y ^ 2 := by gcongr
      _ = c2 / y ^ 5 := by field_simp
      _ ≤ c2 / y ^ 3 := by
          apply div_le_div_of_nonneg_left hc20.le (by positivity)
          exact pow_le_pow_right₀ hy1 (by norm_num)
  have hQ2 : Real.log x ^ 2 * Q ≤ c2 / y ^ 3 := by
    calc Real.log x ^ 2 * Q ≤ Real.log x ^ 2 * (c2 * Real.log x / y ^ 8 * y ^ 2) :=
          mul_le_mul_of_nonneg_left (mul_le_mul heb hDL (by positivity) (by positivity)) (by positivity)
      _ ≤ y ^ 2 * (c2 * y / y ^ 8 * y ^ 2) := by gcongr
      _ = c2 / y ^ 3 := by field_simp
  have hy3pos : 0 < y ^ 3 := by positivity
  have hcy : c2 / y ^ 3 ≤ 1 := by rw [div_le_one hy3pos]; exact le_trans (le_max_right _ _) hy3
  have h3AQ : 3 * A * Q ≤ W := by
    have h1 : 3 * A * c2 / W ≤ y ^ 3 := le_trans (le_trans (le_max_left _ _) (le_max_left _ _)) hy3
    have : 3 * A * Q ≤ 3 * A * (c2 / y ^ 3) := by gcongr
    rw [div_le_iff₀ hW] at h1
    have h2 : 3 * A * (c2 / y ^ 3) ≤ W := by rw [mul_div_assoc', div_le_iff₀ hy3pos]; linarith
    linarith
  have h6AQ : 6 * A * (Real.log x ^ 2 * Q) ≤ 4 * π * W * ℓ := by
    have h1 : 6 * A * c2 / (4 * π * W * ℓ) ≤ y ^ 3 := le_trans (le_trans (le_max_right _ _) (le_max_left _ _)) hy3
    rw [div_le_iff₀ (by positivity)] at h1
    have : 6 * A * (Real.log x ^ 2 * Q) ≤ 6 * A * (c2 / y ^ 3) := by gcongr
    have h2 : 6 * A * (c2 / y ^ 3) ≤ 4 * π * W * ℓ := by rw [mul_div_assoc', div_le_iff₀ hy3pos]; linarith
    linarith
  -- e ≤ 1
  have he1 : e ≤ 1 := by
    have : e ≤ Q := le_mul_of_one_le_right he0 hDL1
    linarith
  refine ⟨he1, ?_⟩
  -- the bound
  have hbL : (1 + b) ^ L ≤ D ^ L := pow_le_pow_left₀ (by linarith) (by rw [hD]; nlinarith) L
  have hbL1 : 1 ≤ (1 + b) ^ L := one_le_pow₀ (by linarith)
  set δ := A * e * (1 + b) ^ L with hδ
  have hδQ : δ ≤ A * Q := by rw [hδ, hQ, mul_assoc]; exact mul_le_mul_of_nonneg_left (mul_le_mul_of_nonneg_left hbL he0) hA.le
  have hηQ : η ≤ A * e * (1 + b) ^ L := by
    have : A * e ≤ A * e * (1 + b) ^ L := le_mul_of_one_le_right (by positivity) hbL1
    linarith
  have hsum : 2 * δ + η ≤ 3 * (A * e * (1 + b) ^ L) := by rw [hδ]; linarith
  have hBDQ : B ^ L * (3 * (A * e * (1 + b) ^ L)) = 3 * A * Q := by
    rw [hQ, hD, mul_pow]; ring
  -- first term
  have hL2 : Real.log x / (8 * ℓ) ≤ (L : ℝ) + 2 := by linarith
  have hT1 : ρ * π / (2 * (L + 2)) * (2 * W + 2 * δ + η) ≤ 12 * π * ρ * W * ℓ / Real.log x := by
    have h1 : 2 * W + 2 * δ + η ≤ 3 * W := by
      have : 2 * δ + η ≤ 3 * A * Q := by linarith [hsum, hδQ]
      linarith
    have h2 : ρ * π / (2 * ((L : ℝ) + 2)) ≤ ρ * π * (8 * ℓ) / (2 * Real.log x) := by
      rw [div_le_div_iff₀ (by positivity) (by positivity)]
      have := (div_le_iff₀ (by positivity : (0 : ℝ) < 8 * ℓ)).mp hL2
      nlinarith [mul_pos hρ hπ]
    calc ρ * π / (2 * ((L : ℝ) + 2)) * (2 * W + 2 * δ + η) ≤ ρ * π * (8 * ℓ) / (2 * Real.log x) * (3 * W) :=
          mul_le_mul h2 h1 (by positivity) (by positivity)
      _ = 12 * π * ρ * W * ℓ / Real.log x := by field_simp; ring
  -- second term
  have hT2 : ρ * (L + 1) * B ^ L * (2 * δ + η) ≤ 4 * π * ρ * W * ℓ / Real.log x := by
    have hBL0 : 0 ≤ B ^ L := by positivity
    have h1 : ρ * (L + 1) * B ^ L * (2 * δ + η) ≤ ρ * (L + 1) * (3 * A * Q) := by
      rw [← hBDQ, mul_assoc (ρ * ((L : ℝ) + 1))]
      exact mul_le_mul_of_nonneg_left (mul_le_mul_of_nonneg_left hsum hBL0) (by positivity)
    have h2 : ρ * ((L : ℝ) + 1) * (3 * A * Q) ≤ ρ * (2 * Real.log x) * (3 * A * Q) := by gcongr
    have h3 : ρ * (2 * Real.log x) * (3 * A * Q) ≤ 4 * π * ρ * W * ℓ / Real.log x := by
      rw [le_div_iff₀ hlogpos]
      nlinarith [mul_le_mul_of_nonneg_left h6AQ hρ.le]
    linarith
  have : 16 * π * ρ * W * ℓ / Real.log x = 12 * π * ρ * W * ℓ / Real.log x + 4 * π * ρ * W * ℓ / Real.log x := by
    field_simp; ring
  rw [this]
  exact add_le_add hT1 hT2

/-- **Theorem 5.6 (ii), formal, rate form.** Under the hypotheses of `p1_thm_general_memory_upper`, with mass
`W > 0`, `A = (1 + |a| + |κ| W/(1-ρ))/κ²`, `b = |κ|(|κ|/(1-s) + 1)/κ²`, `B = (2/ρ + 1)(1 + √2)` and `D = B (1 + b)`:
there is `x₀`, depending only on `(a, κ, ρ, s, W, β)`, such that whenever `N/v ≥ x₀`, using `L + 1` moments with
`L = ⌊log(N/v)/(8 log D)⌋`, with probability at least `1 - β` every finite measure `ν` on `[0, ρ]` that fits the
deconvolved kernel values at least as well as `μ` (up to `η ≤ A e`) satisfies
`|∫ f dν - ∫ f dμ| ≤ 16 π ρ W log D / log(N/v)` for every `f` that is 1-Lipschitz on `[0, ρ]` with `f(0) = 0`. -/
theorem p1_thm_general_memory_rate (a κ ρ s : ℝ) (hκ : κ ≠ 0) (hρ0 : 0 < ρ) (hρ1 : ρ < 1)
    (μ : Measure ℝ) [IsFiniteMeasure μ] (hμ : μ (Set.Icc 0 ρ)ᶜ = 0) (hW : 0 < μ.real Set.univ)
    (hs : |a| + |κ| * (μ.real Set.univ / (1 - ρ)) ≤ s) (hs1 : s < 1)
    (h : ℕ → ℝ) (h0 : h 0 = κ)
    (hrec : ∀ t, h (t + 1) = a * h t + κ * ∑ j ∈ range (t + 1), (∫ r, r ^ j ∂μ) * h (t - j))
    (β : ℝ) (hβ : 0 < β) (hβ1 : β < 1) :
    ∃ x0 : ℝ, ∀ {Ω : Type*} [MeasurableSpace Ω] (P : Measure Ω) [IsProbabilityMeasure P]
      {N : ℕ} (_hN : 0 < N) (ξ : Fin N → ℕ → Ω → ℝ) (v : ℝ≥0), 0 < v →
      (∀ t, iIndepFun (fun n => ξ n t) P) → (∀ n t, HasSubgaussianMGF (ξ n t) v P) →
      x0 ≤ (N : ℝ) / v →
      ∀ L : ℕ, L = ⌊Real.log ((N : ℝ) / v) /
          (8 * Real.log ((2 / ρ + 1) * (1 + Real.sqrt 2) * (1 + |κ| * (|κ| / (1 - s) + 1) / κ ^ 2)))⌋₊ →
      ∀ η : ℝ, 0 ≤ η → η ≤ (1 + |a| + |κ| * (μ.real Set.univ / (1 - ρ))) / κ ^ 2 * gmNoise L β v N →
      P.real {ω | ¬ ∀ ν : Measure ℝ, IsFiniteMeasure ν → ν (Set.Icc 0 ρ)ᶜ = 0 →
          (∀ i < L + 1, |∫ r, r ^ i ∂ν - deconv a κ (observedTaps κ h (fun t => (∑ n, ξ n t ω) / N)) i| ≤
            (range (L + 1)).sup' nonempty_range_add_one
              (fun i => |∫ r, r ^ i ∂μ - deconv a κ (observedTaps κ h (fun t => (∑ n, ξ n t ω) / N)) i|) + η) →
          ∀ f : ℝ → ℝ, LipschitzOnWith 1 f (Set.Icc 0 ρ) → f 0 = 0 →
            |∫ r, f r ∂ν - ∫ r, f r ∂μ| ≤
              16 * π * ρ * μ.real Set.univ *
                Real.log ((2 / ρ + 1) * (1 + Real.sqrt 2) * (1 + |κ| * (|κ| / (1 - s) + 1) / κ ^ 2)) /
                  Real.log ((N : ℝ) / v)} ≤ β := by
  set W := μ.real Set.univ with hWdef
  set A := (1 + |a| + |κ| * (W / (1 - ρ))) / κ ^ 2 with hAdef
  set b := |κ| * (|κ| / (1 - s) + 1) / κ ^ 2 with hbdef
  set B := (2 / ρ + 1) * (1 + Real.sqrt 2) with hBdef
  have h1s : 0 < 1 - s := by linarith
  have h1ρ : 0 < 1 - ρ := by linarith
  have hA : 0 < A := by rw [hAdef]; positivity
  have hb : 0 ≤ b := by rw [hbdef]; positivity
  have hs2 : 0 ≤ Real.sqrt 2 := Real.sqrt_nonneg 2
  have hB2 : 2 ≤ B := by
    rw [hBdef]
    have h0' : 0 < 2 / ρ := by positivity
    have h1 : 1 ≤ 2 / ρ + 1 := by linarith
    have h2 : 2 ≤ 1 + Real.sqrt 2 := by
      have : 1 ≤ Real.sqrt 2 := by rw [show (1 : ℝ) = Real.sqrt 1 by simp]; exact Real.sqrt_le_sqrt (by norm_num)
      linarith
    nlinarith
  have hB : 1 ≤ B := by linarith
  have hℓ : 1 / 8 ≤ Real.log (B * (1 + b)) := by
    have hD2 : 2 ≤ B * (1 + b) := by nlinarith
    have := Real.log_le_log (by norm_num) hD2
    have := Real.log_two_gt_d9
    linarith
  obtain ⟨x0, hcore⟩ := p1_gm_rate_core A b B W ρ β hA hb hB hW hρ0 hβ hℓ
  refine ⟨x0, fun {Ω} _ P _ {N} hN ξ v hv hind hsub hx L hL η hη0 hη => ?_⟩
  have hvpos : (0 : ℝ) < v := by exact_mod_cast hv
  have hNpos : (0 : ℝ) < N := by exact_mod_cast hN
  have hnoise : gmNoise L β v N =
      Real.sqrt 2 * Real.sqrt (Real.log (4 * ((L + 1 : ℕ) : ℝ) / β)) / Real.sqrt ((N : ℝ) / v) := by
    rw [gmNoise, Real.sqrt_div hNpos.le]
    have h1 : 0 < Real.sqrt (v : ℝ) := Real.sqrt_pos.mpr hvpos
    have h2 : 0 < Real.sqrt (N : ℝ) := Real.sqrt_pos.mpr hNpos
    field_simp
  have hLB : L = ⌊Real.log ((N : ℝ) / v) / (8 * Real.log (B * (1 + b)))⌋₊ := by
    rw [hL, hBdef, hbdef]
  rw [hnoise] at hη
  obtain ⟨he1, hbound⟩ := hcore ((N : ℝ) / v) hx L hLB η hη0 hη
  rw [← hnoise] at he1 hbound
  have hup := p1_thm_general_memory_upper a κ ρ s hκ hρ0 hρ1 μ hμ hs hs1 h h0 hrec L η hη0 P hN ξ v hv hind hsub
    β hβ hβ1 he1
  refine le_trans (measureReal_mono ?_) hup
  intro ω hω
  simp only [Set.mem_setOf_eq] at hω ⊢
  intro hall
  apply hω
  intro ν hνf hν hfit f hf hf0
  refine (hall ν hνf hν hfit f hf hf0).trans ?_
  have hgm : gmBound ρ W L (gmDelta a κ ρ s W L (gmNoise L β v N)) η =
      ρ * π / (2 * (L + 2)) * (2 * W + 2 * (A * gmNoise L β v N * (1 + b) ^ L) + η) +
        ρ * (L + 1) * B ^ L * (2 * (A * gmNoise L β v N * (1 + b) ^ L) + η) := by
    rw [gmBound, gmDelta]
  rw [hgm]
  have e : 16 * π * ρ * W * Real.log ((2 / ρ + 1) * (1 + Real.sqrt 2) * (1 + |κ| * (|κ| / (1 - s) + 1) / κ ^ 2)) /
      Real.log ((N : ℝ) / v) = 16 * π * ρ * W * Real.log (B * (1 + b)) / Real.log ((N : ℝ) / v) := by
    rw [hBdef, hbdef]
  rw [e]
  exact hbound

end CurrentMM
