import CurrentProofs.Paper1CRTaps

/-!
# Paper 1, Proposition S7.1 (iii): the weight entry of the inverse Fisher matrix grows as `(Δη)⁻⁶`

Setting (frozen in `audit/S7_1_iii_TARGET.md`):
- Two cohorts. Known anchor `a` and impact `κ`, with `κ_min ≤ |κ| ≤ κ_max`.
- Parameter `θ = (w₁, w₂, r₁, r₂)` with `wᵢ = qᵢηᵢ` and `rᵢ = 1 - ηᵢ`. Here `0 < wᵢ ≤ w_max` and `0 ≤ r₁ < r₂ ≤ 1`.
- Observed taps `h₀, …, h_T` of the actual closed-loop response (`p1_actual_two_eq_tapW`), on a fixed horizon `T ≥ 4`.
- Gaussian errors with covariance `σ_h² I`, so the Fisher matrix is `σ_h⁻² F_T` with `F_T = J_TᵀJ_T`.
- `J_T = p1TapJac a κ T θ`.

Write `d = r₂ - r₁ = η₁ - η₂`.

* `p1_S71iii_isUnit`: `F_T` is invertible.
* `p1_S71iii_lower`: `1 ≤ [F_T⁻¹]₁₁ d⁶ B_T`, with `B_T = (T+1)(T³ G_T)²` and `G_T = p1TapG |a| κ_max (2 w_max) T`.
* `p1_S71iii_upper`: `[F_T⁻¹]₁₁ d⁶ ≤ 5 C_b²`, with `C_b = 24 Z / κ_min²`, where `Z` is built from `|a|`, `κ_max` and
  `w_max`.
* `p1_prop_S7_1_iii`: the two together. `c d⁻⁶ ≤ [F_T⁻¹]₁₁ ≤ C d⁻⁶`, where `c = 1/B_T > 0` and `C = 5 C_b²` depend on
  `T`, `|a|`, `κ_min`, `κ_max` and `w_max`, and not on `d` or on the rates' location.

Since `η = 1 - r` is an affine change of the last two coordinates with Jacobian `diag(1, 1, -1, -1)`, the weight
entry is the same in `(w, η)` coordinates.

The route has two parts.
- Lower bound (Phases 3, 5, 6). Along `v = (1, -1, d/(2w₁), d/(2w₂))` the kernel derivative is `d³ Q_m`, with
  `|Q_m| ≤ m³` (`p1_K2D_weak`, `p1_Q_abs_le`). The finite recursion then gives `‖J v‖² ≤ B_T d⁶`, and Cauchy–Schwarz
  in the Fisher geometry (`p1_fisher_entry_lower`) does the rest.
- Upper bound (Phase 7). The row `u = (r₂²(r₂ - 3r₁), 6r₁r₂, -3(r₁+r₂), 2)` inverts the confluent Vandermonde
  Jacobian of `(k₀, …, k₃)`, `Σ uₘ ∂kₘ/∂θᵢ = d³ δ_{i1}` (`p1_U_moment`). The triangular map from taps to moments is
  inverted by the explicit coefficients `p1C` (`p1_C_identity`). The resulting `b = c/d³`, supported on `h₁, …, h₄`,
  satisfies `Jᵀ b = e₁`, so `[F⁻¹]₁₁ ≤ ‖b‖²` (`p1_fisher_entry_upper`).

The fixed-horizon route does not use the stability margin or the frequency-domain bound of `Paper1CRScalingH`. Those
would be needed for constants independent of `T`, which are not claimed. The Cramér–Rao inequality
(`p1_thm_gaussian_cramer_rao`) and attainability are separate results.
-/

namespace CurrentMM

open Finset Matrix

theorem p1_abs_sub_le (x y : ℝ) : |x - y| ≤ |x| + |y| := by
  have h := abs_add_le x (-y)
  rwa [abs_neg, ← sub_eq_add_neg] at h

/-! ### The cubic factor of the kernel derivative, for every moment -/

/-- `S_{m}` with `r₂^m - r₁^m - m r₁^{m-1} d = d² S_m`. -/
noncomputable def p1S (r1 r2 : ℝ) : ℕ → ℝ
  | 0 => 0
  | 1 => 0
  | m + 2 => r2 * p1S r1 r2 (m + 1) + ((m : ℝ) + 1) * r1 ^ m

/-- `Q_m` with `r₁^m - r₂^m + (d/2) m (r₁^{m-1} + r₂^{m-1}) = d³ Q_m`. -/
noncomputable def p1Q (r1 r2 : ℝ) : ℕ → ℝ
  | 0 => 0
  | m + 1 => r2 * p1Q r1 r2 m + p1S r1 r2 m / 2

theorem p1_S_taylor (r1 r2 : ℝ) (m : ℕ) :
    r2 ^ (m + 1) - r1 ^ (m + 1) - ((m : ℝ) + 1) * r1 ^ m * (r2 - r1) = (r2 - r1) ^ 2 * p1S r1 r2 (m + 1) := by
  induction m with
  | zero =>
    first
    | (simp [p1S]; done)
    | (simp [p1S]; ring)
  | succ m ih =>
    rw [show p1S r1 r2 (m + 1 + 1) = r2 * p1S r1 r2 (m + 1) + ((m : ℝ) + 1) * r1 ^ m from rfl]
    push_cast
    linear_combination r2 * ih

/-- **The cubic cancellation for every moment.** -/
theorem p1_Q_cubic (r1 r2 : ℝ) (m : ℕ) :
    r1 ^ (m + 1) - r2 ^ (m + 1) + (r2 - r1) / 2 * ((m : ℝ) + 1) * (r1 ^ m + r2 ^ m) =
      (r2 - r1) ^ 3 * p1Q r1 r2 (m + 1) := by
  induction m with
  | zero =>
    first
    | (simp [p1Q, p1S]; done)
    | (simp [p1Q, p1S]; ring)
  | succ m ih =>
    have hR := p1_S_taylor r1 r2 m
    rw [show p1Q r1 r2 (m + 1 + 1) = r2 * p1Q r1 r2 (m + 1) + p1S r1 r2 (m + 1) / 2 from rfl]
    push_cast
    linear_combination r2 * ih + (r2 - r1) / 2 * hR

theorem p1_S_abs_le (r1 r2 : ℝ) (h1 : |r1| ≤ 1) (h2 : |r2| ≤ 1) : ∀ m, |p1S r1 r2 m| ≤ (m : ℝ) ^ 2 := by
  have aux : ∀ m : ℕ, |p1S r1 r2 (m + 1)| ≤ ((m : ℝ) + 1) ^ 2 := by
    intro m
    induction m with
    | zero => simp [p1S]
    | succ m ih =>
      rw [show p1S r1 r2 (m + 1 + 1) = r2 * p1S r1 r2 (m + 1) + ((m : ℝ) + 1) * r1 ^ m from rfl]
      have hm : (0 : ℝ) ≤ (m : ℝ) + 1 := by positivity
      have hp : |r1| ^ m ≤ 1 := pow_le_one₀ (abs_nonneg _) h1
      calc |r2 * p1S r1 r2 (m + 1) + ((m : ℝ) + 1) * r1 ^ m|
          ≤ |r2 * p1S r1 r2 (m + 1)| + |((m : ℝ) + 1) * r1 ^ m| := abs_add_le _ _
        _ = |r2| * |p1S r1 r2 (m + 1)| + ((m : ℝ) + 1) * |r1| ^ m := by
            rw [abs_mul, abs_mul, abs_pow, abs_of_nonneg hm]
        _ ≤ 1 * ((m : ℝ) + 1) ^ 2 + ((m : ℝ) + 1) * 1 :=
            add_le_add (mul_le_mul h2 ih (abs_nonneg _) zero_le_one) (mul_le_mul_of_nonneg_left hp hm)
        _ ≤ (((m + 1 : ℕ) : ℝ) + 1) ^ 2 := by push_cast; nlinarith [(Nat.cast_nonneg m : (0 : ℝ) ≤ m)]
  intro m
  rcases m with _ | m
  · simp [p1S]
  · have := aux m
    push_cast
    exact this

theorem p1_Q_abs_le (r1 r2 : ℝ) (h1 : |r1| ≤ 1) (h2 : |r2| ≤ 1) : ∀ m, |p1Q r1 r2 m| ≤ (m : ℝ) ^ 3 := by
  have hS := p1_S_abs_le r1 r2 h1 h2
  intro m
  induction m with
  | zero => simp [p1Q]
  | succ m ih =>
    rw [show p1Q r1 r2 (m + 1) = r2 * p1Q r1 r2 m + p1S r1 r2 m / 2 from rfl]
    have hm : (0 : ℝ) ≤ (m : ℝ) := Nat.cast_nonneg m
    calc |r2 * p1Q r1 r2 m + p1S r1 r2 m / 2| ≤ |r2 * p1Q r1 r2 m| + |p1S r1 r2 m / 2| := abs_add_le _ _
      _ = |r2| * |p1Q r1 r2 m| + |p1S r1 r2 m| / 2 := by rw [abs_mul, abs_div, abs_two]
      _ ≤ 1 * (m : ℝ) ^ 3 + (m : ℝ) ^ 2 / 2 :=
          add_le_add (mul_le_mul h2 ih (abs_nonneg _) zero_le_one) (div_le_div_of_nonneg_right (hS m) (by norm_num))
      _ ≤ ((m + 1 : ℕ) : ℝ) ^ 3 := by push_cast; nlinarith [mul_nonneg hm hm, mul_nonneg (mul_nonneg hm hm) hm]

/-- **Phase 3 connected to the parameter map.** Along `v = (1, -1, d/(2w₁), d/(2w₂))`, the derivative of every kernel
moment is `d³ Q_m`. -/
theorem p1_K2D_weak (w1 w2 r1 r2 : ℝ) (hw1 : w1 ≠ 0) (hw2 : w2 ≠ 0) (m : ℕ) :
    p1K2D ![w1, w2, r1, r2] ![1, -1, (r2 - r1) / (2 * w1), (r2 - r1) / (2 * w2)] m =
      (r2 - r1) ^ 3 * p1Q r1 r2 m := by
  rcases m with _ | m
  · first
    | (simp [p1K2D, p1Q]; done)
    | (simp [p1K2D, p1Q]; ring)
  · rw [← p1_Q_cubic r1 r2 m]
    conv_lhs => simp [p1K2D]
    first
    | (field_simp; ring)
    | field_simp
    | ring

/-! ### Constants of the admissible family -/

theorem p1_K2_abs_le (w1 w2 r1 r2 wm : ℝ) (hw1 : 0 ≤ w1) (hw1' : w1 ≤ wm) (hw2 : 0 ≤ w2) (hw2' : w2 ≤ wm)
    (hr1 : 0 ≤ r1) (hr1' : r1 ≤ 1) (hr2 : 0 ≤ r2) (hr2' : r2 ≤ 1) (m : ℕ) :
    |p1K2 ![w1, w2, r1, r2] m| ≤ 2 * wm := by
  have e : p1K2 ![w1, w2, r1, r2] m = w1 * r1 ^ m + w2 * r2 ^ m := by simp [p1K2]
  rw [e]
  have a1 : w1 * r1 ^ m ≤ w1 := mul_le_of_le_one_right hw1 (pow_le_one₀ hr1 hr1')
  have a2 : w2 * r2 ^ m ≤ w2 := mul_le_of_le_one_right hw2 (pow_le_one₀ hr2 hr2')
  have b1 : 0 ≤ w1 * r1 ^ m := mul_nonneg hw1 (pow_nonneg hr1 m)
  have b2 : 0 ≤ w2 * r2 ^ m := mul_nonneg hw2 (pow_nonneg hr2 m)
  rw [abs_of_nonneg (add_nonneg b1 b2)]
  linarith

/-! ### The weak direction: `‖J v‖² ≤ B_T d⁶` -/

/-- **Phase 5.** The observed responses move by `O(d³)` along `v`. -/
theorem p1_S71iii_weak_norm (a κ κm wm w1 w2 r1 r2 : ℝ) (T : ℕ) (hκ : |κ| ≤ κm) (hw1 : 0 < w1)
    (hw1' : w1 ≤ wm) (hw2 : 0 < w2) (hw2' : w2 ≤ wm) (hr1 : 0 ≤ r1) (hr12 : r1 ≤ r2) (hr2' : r2 ≤ 1) :
    (p1TapJac a κ T ![w1, w2, r1, r2] *ᵥ ![1, -1, (r2 - r1) / (2 * w1), (r2 - r1) / (2 * w2)]) ⬝ᵥ
        (p1TapJac a κ T ![w1, w2, r1, r2] *ᵥ ![1, -1, (r2 - r1) / (2 * w1), (r2 - r1) / (2 * w2)]) ≤
      ((T : ℝ) + 1) * ((T : ℝ) ^ 3 * p1TapG |a| κm (2 * wm) T) ^ 2 * (r2 - r1) ^ 6 := by
  have hr2 : 0 ≤ r2 := le_trans hr1 hr12
  have hr1' : r1 ≤ 1 := le_trans hr12 hr2'
  have hd : 0 ≤ r2 - r1 := by linarith
  have hd3 : 0 ≤ (r2 - r1) ^ 3 := pow_nonneg hd 3
  have hwm : 0 ≤ 2 * wm := by linarith
  have habs1 : |r1| ≤ 1 := abs_le.mpr ⟨by linarith, hr1'⟩
  have habs2 : |r2| ≤ 1 := abs_le.mpr ⟨by linarith, hr2'⟩
  set E : ℝ := (r2 - r1) ^ 3 * (T : ℝ) ^ 3 with hE
  have hE0 : 0 ≤ E := mul_nonneg hd3 (by positivity)
  have hk : ∀ m, |p1K2 ![w1, w2, r1, r2] m| ≤ 2 * wm :=
    p1_K2_abs_le w1 w2 r1 r2 wm hw1.le hw1' hw2.le hw2' hr1 hr1' hr2 hr2'
  have hk' : ∀ m, m < T → |p1K2D ![w1, w2, r1, r2] ![1, -1, (r2 - r1) / (2 * w1), (r2 - r1) / (2 * w2)] m| ≤ E := by
    intro m hm
    rw [p1_K2D_weak w1 w2 r1 r2 hw1.ne' hw2.ne' m, abs_mul, abs_of_nonneg hd3, hE]
    apply mul_le_mul_of_nonneg_left _ hd3
    calc |p1Q r1 r2 m| ≤ (m : ℝ) ^ 3 := p1_Q_abs_le r1 r2 habs1 habs2 m
      _ ≤ (T : ℝ) ^ 3 := by
        have : (m : ℝ) ≤ T := by exact_mod_cast hm.le
        exact pow_le_pow_left₀ (Nat.cast_nonneg m) this 3
  have hbound := p1_tapD_abs_le a κ _ _ κm (2 * wm) E T hκ hwm hE0 hk hk' T le_rfl
  have hcomp : ∀ t : Fin (T + 1),
      |(p1TapJac a κ T ![w1, w2, r1, r2] *ᵥ ![1, -1, (r2 - r1) / (2 * w1), (r2 - r1) / (2 * w2)]) t| ≤
        E * p1TapG |a| κm (2 * wm) T := by
    intro t
    rw [p1_tapJac_mulVec]
    exact hbound t.val (Nat.lt_succ_iff.mp t.isLt)
  have hG0 : 0 ≤ E * p1TapG |a| κm (2 * wm) T :=
    le_trans (abs_nonneg _) (hcomp 0)
  calc _ = ∑ t : Fin (T + 1),
        (p1TapJac a κ T ![w1, w2, r1, r2] *ᵥ ![1, -1, (r2 - r1) / (2 * w1), (r2 - r1) / (2 * w2)]) t *
        (p1TapJac a κ T ![w1, w2, r1, r2] *ᵥ ![1, -1, (r2 - r1) / (2 * w1), (r2 - r1) / (2 * w2)]) t := rfl
    _ ≤ ∑ _t : Fin (T + 1), (E * p1TapG |a| κm (2 * wm) T) * (E * p1TapG |a| κm (2 * wm) T) := by
        refine sum_le_sum fun t _ => ?_
        have h := mul_self_le_mul_self (abs_nonneg _) (hcomp t)
        rwa [abs_mul_abs_self] at h
    _ = ((T : ℝ) + 1) * ((E * p1TapG |a| κm (2 * wm) T) * (E * p1TapG |a| κm (2 * wm) T)) := by
        rw [sum_const, card_univ, Fintype.card_fin, nsmul_eq_mul]; first | (push_cast; ring) | push_cast | norm_num
    _ = ((T : ℝ) + 1) * ((T : ℝ) ^ 3 * p1TapG |a| κm (2 * wm) T) ^ 2 * (r2 - r1) ^ 6 := by
        rw [hE]; ring

/-! ### The recovering combination: `Jᵀ b = e₁` -/

/-- The inverse row of the moment Jacobian, `Σ uₘ ∂kₘ/∂θᵢ = d³ δ_{i1}`. -/
noncomputable def p1U (r1 r2 : ℝ) : ℕ → ℝ
  | 0 => r2 ^ 2 * (r2 - 3 * r1)
  | 1 => 6 * (r1 * r2)
  | 2 => -(3 * (r1 + r2))
  | 3 => 2
  | _ => 0

/-- The inverse of the taps-to-moments triangle, as a Toeplitz series. -/
noncomputable def p1E (a κ : ℝ) (k : ℕ → ℝ) : ℕ → ℝ
  | 0 => 1
  | 1 => -(2 * (a + κ * k 0))
  | 2 => (a + κ * k 0) ^ 2 - 2 * (κ * k 1)
  | 3 => 2 * ((a + κ * k 0) * (κ * k 1)) - 2 * (κ * k 2)
  | _ => 0

/-- Coefficients of the taps `h₁, …, h₄` in the recovering combination. -/
noncomputable def p1C (a κ : ℝ) (k u : ℕ → ℝ) (t : ℕ) : ℝ :=
  if 1 ≤ t ∧ t ≤ 4 then (∑ j ∈ range 4, p1E a κ k j * u (t - 1 + j)) / κ ^ 2 else 0

theorem p1_U_ge (r1 r2 : ℝ) (j : ℕ) (hj : 4 ≤ j) : p1U r1 r2 j = 0 := by
  obtain ⟨i, rfl⟩ : ∃ i, j = i + 4 := ⟨j - 4, by omega⟩
  first
  | rfl
  | simp [p1U]

theorem p1_C_ge (a κ : ℝ) (k u : ℕ → ℝ) (t : ℕ) (ht : 5 ≤ t) : p1C a κ k u t = 0 := by
  unfold p1C
  rw [if_neg (by omega)]

theorem p1_C_zero (a κ : ℝ) (k u : ℕ → ℝ) : p1C a κ k u 0 = 0 := by
  unfold p1C
  rw [if_neg (by omega)]

/-- **Inverting the taps-to-moments triangle.** For every kernel derivative `k'` and every `u` supported on
`{0, 1, 2, 3}`, `Σ_{t ≤ 4} c_t (Dh)_t = Σ_{m ≤ 3} uₘ k'ₘ`. -/
theorem p1_C_identity (a κ : ℝ) (hκ : κ ≠ 0) (k k' u : ℕ → ℝ) (hu : ∀ j, 4 ≤ j → u j = 0) :
    ∑ t ∈ range 5, p1C a κ k u t * p1TapD a κ k k' t = ∑ m ∈ range 4, u m * k' m := by
  have h4 := hu 4 le_rfl
  have h5 := hu 5 (by norm_num)
  have h6 := hu 6 (by norm_num)
  have hc0 : p1C a κ k u 0 = 0 := p1_C_zero a κ k u
  have hc1 : p1C a κ k u 1 =
      (p1E a κ k 0 * u 0 + p1E a κ k 1 * u 1 + p1E a κ k 2 * u 2 + p1E a κ k 3 * u 3) / κ ^ 2 := by
    unfold p1C; rw [if_pos (by norm_num)]; simp [sum_range_succ]
  have hc2 : p1C a κ k u 2 =
      (p1E a κ k 0 * u 1 + p1E a κ k 1 * u 2 + p1E a κ k 2 * u 3 + p1E a κ k 3 * u 4) / κ ^ 2 := by
    unfold p1C; rw [if_pos (by norm_num)]; simp [sum_range_succ]
  have hc3 : p1C a κ k u 3 =
      (p1E a κ k 0 * u 2 + p1E a κ k 1 * u 3 + p1E a κ k 2 * u 4 + p1E a κ k 3 * u 5) / κ ^ 2 := by
    unfold p1C; rw [if_pos (by norm_num)]; simp [sum_range_succ]
  have hc4 : p1C a κ k u 4 =
      (p1E a κ k 0 * u 3 + p1E a κ k 1 * u 4 + p1E a κ k 2 * u 5 + p1E a κ k 3 * u 6) / κ ^ 2 := by
    unfold p1C; rw [if_pos (by norm_num)]; simp [sum_range_succ]
  have e0 : p1E a κ k 0 = 1 := rfl
  have e1 : p1E a κ k 1 = -(2 * (a + κ * k 0)) := rfl
  have e2 : p1E a κ k 2 = (a + κ * k 0) ^ 2 - 2 * (κ * k 1) := rfl
  have e3 : p1E a κ k 3 = 2 * ((a + κ * k 0) * (κ * k 1)) - 2 * (κ * k 2) := rfl
  simp only [sum_range_succ, sum_range_zero, zero_add, hc0, hc1, hc2, hc3, hc4, h4, h5, h6, e0, e1, e2, e3,
    p1_tapD_zero, p1_tapD_succ, p1_tap_zero, p1_tap_succ, Nat.reduceSub, Nat.reduceAdd]
  field_simp
  ring

/-- **The confluent-Vandermonde row in weight coordinates.** -/
theorem p1_U_moment (w1 w2 r1 r2 : ℝ) (i : Fin 4) :
    ∑ m ∈ range 4, p1U r1 r2 m * p1K2D ![w1, w2, r1, r2] (Pi.single i 1) m =
      (Pi.single 0 ((r2 - r1) ^ 3) : Fin 4 → ℝ) i := by
  have u0 : p1U r1 r2 0 = r2 ^ 2 * (r2 - 3 * r1) := rfl
  have u1 : p1U r1 r2 1 = 6 * (r1 * r2) := rfl
  have u2 : p1U r1 r2 2 = -(3 * (r1 + r2)) := rfl
  have u3 : p1U r1 r2 3 = 2 := rfl
  fin_cases i <;>
  · conv_lhs => simp [sum_range_succ, p1K2D, Pi.single_apply, u0, u1, u2, u3]
    conv_rhs => simp [Pi.single_apply]
    ring

theorem p1_sum_fin_range5 (T : ℕ) (hT : 4 ≤ T) (f : ℕ → ℝ) (hf : ∀ n, 5 ≤ n → f n = 0) :
    ∑ t : Fin (T + 1), f t.val = ∑ n ∈ range 5, f n := by
  rw [Fin.sum_univ_eq_sum_range (fun n => f n) (T + 1)]
  symm
  apply Finset.sum_subset
  · intro n hn
    simp only [mem_range] at hn ⊢
    omega
  · intro n _ hn
    simp only [mem_range, not_lt] at hn
    exact hf n hn

theorem p1_tapJac_entry (a κ : ℝ) (T : ℕ) (θ0 : Fin 4 → ℝ) (t : Fin (T + 1)) (i : Fin 4) :
    p1TapJac a κ T θ0 t i = p1TapD a κ (p1K2 θ0) (p1K2D θ0 (Pi.single i 1)) t.val := by
  have h := p1_tapJac_mulVec a κ T θ0 (Pi.single i 1) t
  rw [Matrix.mulVec_single_one, Matrix.col_apply] at h
  exact h

/-- **Phase 7.** The explicit `b = c/d³` on the taps `h₁, …, h₄` satisfies `Jᵀ b = e₁`. -/
theorem p1_S71iii_recover (a κ w1 w2 r1 r2 : ℝ) (T : ℕ) (hT : 4 ≤ T) (hκ : κ ≠ 0) (hd : r2 - r1 ≠ 0) :
    (p1TapJac a κ T ![w1, w2, r1, r2])ᵀ *ᵥ
        (fun t : Fin (T + 1) => p1C a κ (p1K2 ![w1, w2, r1, r2]) (p1U r1 r2) t.val / (r2 - r1) ^ 3) =
      Pi.single 0 1 := by
  funext i
  have hd3 : (r2 - r1) ^ 3 ≠ 0 := pow_ne_zero 3 hd
  calc ((p1TapJac a κ T ![w1, w2, r1, r2])ᵀ *ᵥ
        (fun t : Fin (T + 1) => p1C a κ (p1K2 ![w1, w2, r1, r2]) (p1U r1 r2) t.val / (r2 - r1) ^ 3)) i
      = ∑ t : Fin (T + 1), (fun n : ℕ => p1C a κ (p1K2 ![w1, w2, r1, r2]) (p1U r1 r2) n *
          p1TapD a κ (p1K2 ![w1, w2, r1, r2]) (p1K2D ![w1, w2, r1, r2] (Pi.single i 1)) n / (r2 - r1) ^ 3) t.val := by
        simp only [Matrix.mulVec, dotProduct, Matrix.transpose_apply]
        refine sum_congr rfl fun t _ => ?_
        rw [p1_tapJac_entry]
        ring
    _ = ∑ n ∈ range 5, p1C a κ (p1K2 ![w1, w2, r1, r2]) (p1U r1 r2) n *
          p1TapD a κ (p1K2 ![w1, w2, r1, r2]) (p1K2D ![w1, w2, r1, r2] (Pi.single i 1)) n / (r2 - r1) ^ 3 :=
        p1_sum_fin_range5 T hT (fun n : ℕ => p1C a κ (p1K2 ![w1, w2, r1, r2]) (p1U r1 r2) n *
          p1TapD a κ (p1K2 ![w1, w2, r1, r2]) (p1K2D ![w1, w2, r1, r2] (Pi.single i 1)) n / (r2 - r1) ^ 3)
          fun n hn => by simp only [p1_C_ge a κ (p1K2 ![w1, w2, r1, r2]) (p1U r1 r2) n hn, zero_mul, zero_div]
    _ = (∑ m ∈ range 4, p1U r1 r2 m * p1K2D ![w1, w2, r1, r2] (Pi.single i 1) m) / (r2 - r1) ^ 3 := by
        rw [← Finset.sum_div, p1_C_identity a κ hκ _ _ _ (p1_U_ge r1 r2)]
    _ = (Pi.single 0 1 : Fin 4 → ℝ) i := by
        rw [p1_U_moment]
        fin_cases i <;> simp [Pi.single_apply, hd3]

/-! ### Invertibility -/

theorem p1_S71iii_injective (a κ w1 w2 r1 r2 : ℝ) (T : ℕ) (hT : 4 ≤ T) (hκ : κ ≠ 0) (hw1 : w1 ≠ 0)
    (hw2 : w2 ≠ 0) (hd : r2 - r1 ≠ 0) (x : Fin 4 → ℝ) (hx : p1TapJac a κ T ![w1, w2, r1, r2] *ᵥ x = 0) :
    x = 0 := by
  have hg : ∀ t, t ≤ T → p1TapD a κ (p1K2 ![w1, w2, r1, r2]) (p1K2D ![w1, w2, r1, r2] x) t = 0 := by
    intro t ht
    have h := congrFun hx ⟨t, Nat.lt_succ_of_le ht⟩
    rw [p1_tapJac_mulVec] at h
    simpa using h
  have hkm : ∀ m, m < 4 → p1K2D ![w1, w2, r1, r2] x m = 0 := by
    intro m hm
    have hid := p1_C_identity a κ hκ (p1K2 ![w1, w2, r1, r2]) (p1K2D ![w1, w2, r1, r2] x)
      (fun j => if j = m then 1 else 0) (fun j hj => if_neg (by omega))
    have e1 : ∑ t ∈ range 5, p1C a κ (p1K2 ![w1, w2, r1, r2]) (fun j => if j = m then 1 else 0) t *
        p1TapD a κ (p1K2 ![w1, w2, r1, r2]) (p1K2D ![w1, w2, r1, r2] x) t = 0 :=
      Finset.sum_eq_zero fun t ht => by
        rw [hg t (by simp only [mem_range] at ht; omega), mul_zero]
    have e2 : ∑ j ∈ range 4, (if j = m then (1 : ℝ) else 0) * p1K2D ![w1, w2, r1, r2] x j =
        p1K2D ![w1, w2, r1, r2] x m := by
      rw [Finset.sum_eq_single m]
      · simp
      · intro j _ hj; simp [hj]
      · intro hm'; exact absurd (mem_range.mpr hm) hm'
    rw [e1, e2] at hid
    exact hid.symm
  have k0 := hkm 0 (by norm_num)
  have k1 := hkm 1 (by norm_num)
  have k2 := hkm 2 (by norm_num)
  have k3 := hkm 3 (by norm_num)
  simp [p1K2D] at k0 k1 k2 k3
  have x0 : (r2 - r1) ^ 3 * x 0 = 0 := by
    linear_combination (r2 ^ 2 * (r2 - 3 * r1)) * k0 + (6 * r1 * r2) * k1 + (-(3 * (r1 + r2))) * k2 + 2 * k3
  have x1 : (r1 - r2) ^ 3 * x 1 = 0 := by
    linear_combination (r1 ^ 2 * (r1 - 3 * r2)) * k0 + (6 * r1 * r2) * k1 + (-(3 * (r1 + r2))) * k2 + 2 * k3
  have x2 : w1 * (r1 - r2) ^ 2 * x 2 = 0 := by
    linear_combination (-(r1 * r2 ^ 2)) * k0 + (r2 * (2 * r1 + r2)) * k1 + (-(r1 + 2 * r2)) * k2 + k3
  have x3 : w2 * (r1 - r2) ^ 2 * x 3 = 0 := by
    linear_combination (-(r1 ^ 2 * r2)) * k0 + (r1 * (r1 + 2 * r2)) * k1 + (-(2 * r1 + r2)) * k2 + k3
  have hd' : r1 - r2 ≠ 0 := fun h => hd (by linarith)
  have y0 : x 0 = 0 := (mul_eq_zero.mp x0).resolve_left (pow_ne_zero 3 hd)
  have y1 : x 1 = 0 := (mul_eq_zero.mp x1).resolve_left (pow_ne_zero 3 hd')
  have y2 : x 2 = 0 := (mul_eq_zero.mp x2).resolve_left (mul_ne_zero hw1 (pow_ne_zero 2 hd'))
  have y3 : x 3 = 0 := (mul_eq_zero.mp x3).resolve_left (mul_ne_zero hw2 (pow_ne_zero 2 hd'))
  funext i
  fin_cases i <;> simp [y0, y1, y2, y3]

/-- **`F_T = J_TᵀJ_T` is invertible.** -/
theorem p1_S71iii_isUnit (a κ w1 w2 r1 r2 : ℝ) (T : ℕ) (hT : 4 ≤ T) (hκ : κ ≠ 0) (hw1 : w1 ≠ 0)
    (hw2 : w2 ≠ 0) (hd : r2 - r1 ≠ 0) :
    IsUnit ((p1TapJac a κ T ![w1, w2, r1, r2])ᵀ * p1TapJac a κ T ![w1, w2, r1, r2]).det :=
  p1_gram_isUnit _ (p1_S71iii_injective a κ w1 w2 r1 r2 T hT hκ hw1 hw2 hd)

/-! ### Bounds on the recovering combination -/

theorem p1_U_abs_le (r1 r2 : ℝ) (hr1 : 0 ≤ r1) (hr1' : r1 ≤ 1) (hr2 : 0 ≤ r2) (hr2' : r2 ≤ 1) :
    ∀ j, |p1U r1 r2 j| ≤ 6 := by
  intro j
  rcases j with _ | _ | _ | _ | j
  · show |r2 ^ 2 * (r2 - 3 * r1)| ≤ 6
    rw [abs_mul, abs_of_nonneg (sq_nonneg r2)]
    have h1 : r2 ^ 2 ≤ 1 := pow_le_one₀ hr2 hr2'
    have h2 : |r2 - 3 * r1| ≤ 3 := abs_le.mpr ⟨by linarith, by linarith⟩
    have h3 := mul_le_mul h1 h2 (abs_nonneg _) zero_le_one
    linarith
  · show |6 * (r1 * r2)| ≤ 6
    have h0 : 0 ≤ r1 * r2 := mul_nonneg hr1 hr2
    have h1 : r1 * r2 ≤ 1 := mul_le_one₀ hr1' hr2 hr2'
    rw [abs_of_nonneg (by linarith)]
    linarith
  · show |-(3 * (r1 + r2))| ≤ 6
    rw [abs_neg, abs_of_nonneg (by linarith)]
    linarith
  · show |(2 : ℝ)| ≤ 6
    norm_num
  · rw [p1_U_ge r1 r2 _ (by omega)]
    norm_num

theorem p1_E_abs_le (a κ : ℝ) (k : ℕ → ℝ) (P Q : ℝ) (hα : |a + κ * k 0| ≤ P) (h1 : |κ * k 1| ≤ Q)
    (h2 : |κ * k 2| ≤ Q) : ∀ j, |p1E a κ k j| ≤ 1 + 2 * P + P ^ 2 + 2 * Q + 2 * P * Q := by
  have hP : 0 ≤ P := le_trans (abs_nonneg _) hα
  have hQ : 0 ≤ Q := le_trans (abs_nonneg _) h1
  have hPQ : 0 ≤ P * Q := mul_nonneg hP hQ
  have hP2 : 0 ≤ P ^ 2 := sq_nonneg P
  intro j
  rcases j with _ | _ | _ | _ | j
  · show |(1 : ℝ)| ≤ _
    rw [abs_one]; linarith
  · show |-(2 * (a + κ * k 0))| ≤ _
    rw [abs_neg, abs_mul, abs_two]; linarith
  · show |(a + κ * k 0) ^ 2 - 2 * (κ * k 1)| ≤ _
    have t1 : |(a + κ * k 0) ^ 2| ≤ P ^ 2 := by
      rw [abs_pow]; exact pow_le_pow_left₀ (abs_nonneg _) hα 2
    have t2 : |2 * (κ * k 1)| ≤ 2 * Q := by rw [abs_mul, abs_two]; linarith
    have t3 := p1_abs_sub_le ((a + κ * k 0) ^ 2) (2 * (κ * k 1))
    linarith
  · show |2 * ((a + κ * k 0) * (κ * k 1)) - 2 * (κ * k 2)| ≤ _
    have t1 : |2 * ((a + κ * k 0) * (κ * k 1))| ≤ 2 * (P * Q) := by
      rw [abs_mul, abs_two, abs_mul]
      have := mul_le_mul hα h1 (abs_nonneg _) hP
      linarith
    have t2 : |2 * (κ * k 2)| ≤ 2 * Q := by rw [abs_mul, abs_two]; linarith
    have t3 := p1_abs_sub_le (2 * ((a + κ * k 0) * (κ * k 1))) (2 * (κ * k 2))
    linarith
  · show |p1E a κ k (j + 4)| ≤ _
    rw [show p1E a κ k (j + 4) = 0 from rfl, abs_zero]
    linarith

theorem p1_C_abs_le (a κ κmin : ℝ) (k u : ℕ → ℝ) (Z U : ℝ) (hκmin : 0 < κmin) (hκ : κmin ≤ |κ|)
    (hE : ∀ j, |p1E a κ k j| ≤ Z) (hU : ∀ j, |u j| ≤ U) : ∀ t, |p1C a κ k u t| ≤ 4 * (Z * U) / κmin ^ 2 := by
  have hZ : 0 ≤ Z := le_trans (abs_nonneg _) (hE 0)
  have hU0 : 0 ≤ U := le_trans (abs_nonneg _) (hU 0)
  have hZU : 0 ≤ 4 * (Z * U) := mul_nonneg (by norm_num) (mul_nonneg hZ hU0)
  have hk2 : κmin ^ 2 ≤ |κ| ^ 2 := pow_le_pow_left₀ hκmin.le hκ 2
  have hκ2 : 0 < κmin ^ 2 := pow_pos hκmin 2
  intro t
  unfold p1C
  split_ifs with h
  · rw [abs_div, abs_pow]
    have hs : |∑ j ∈ range 4, p1E a κ k j * u (t - 1 + j)| ≤ 4 * (Z * U) := by
      calc _ ≤ ∑ j ∈ range 4, |p1E a κ k j * u (t - 1 + j)| := abs_sum_le_sum_abs _ _
        _ ≤ ∑ _j ∈ range 4, Z * U := by
            refine sum_le_sum fun j _ => ?_
            rw [abs_mul]
            exact mul_le_mul (hE j) (hU _) (abs_nonneg _) hZ
        _ = 4 * (Z * U) := by rw [sum_const, card_range, nsmul_eq_mul]; first | (push_cast; ring) | push_cast | norm_num
    calc |∑ j ∈ range 4, p1E a κ k j * u (t - 1 + j)| / |κ| ^ 2 ≤ 4 * (Z * U) / |κ| ^ 2 :=
          div_le_div_of_nonneg_right hs (by positivity)
      _ ≤ 4 * (Z * U) / κmin ^ 2 := div_le_div_of_nonneg_left hZU hκ2 hk2
  · rw [abs_zero]
    exact div_nonneg hZU hκ2.le

/-- **Phase 7, bound.** `‖b‖² ≤ 5 C_b² / d⁶`. -/
theorem p1_S71iii_b_norm (a κ κmin κm wm w1 w2 r1 r2 : ℝ) (T : ℕ) (hT : 4 ≤ T) (hκmin : 0 < κmin)
    (hκ1 : κmin ≤ |κ|) (hκ2 : |κ| ≤ κm) (hw1 : 0 ≤ w1) (hw1' : w1 ≤ wm) (hw2 : 0 ≤ w2) (hw2' : w2 ≤ wm)
    (hr1 : 0 ≤ r1) (hr12 : r1 < r2) (hr2' : r2 ≤ 1) :
    (fun t : Fin (T + 1) => p1C a κ (p1K2 ![w1, w2, r1, r2]) (p1U r1 r2) t.val / (r2 - r1) ^ 3) ⬝ᵥ
        (fun t : Fin (T + 1) => p1C a κ (p1K2 ![w1, w2, r1, r2]) (p1U r1 r2) t.val / (r2 - r1) ^ 3) ≤
      5 * ((4 * ((1 + 2 * (|a| + κm * (2 * wm)) + (|a| + κm * (2 * wm)) ^ 2 + 2 * (κm * (2 * wm)) +
          2 * (|a| + κm * (2 * wm)) * (κm * (2 * wm))) * 6) / κmin ^ 2) *
        (4 * ((1 + 2 * (|a| + κm * (2 * wm)) + (|a| + κm * (2 * wm)) ^ 2 + 2 * (κm * (2 * wm)) +
          2 * (|a| + κm * (2 * wm)) * (κm * (2 * wm))) * 6) / κmin ^ 2)) / (r2 - r1) ^ 6 := by
  have hr2 : 0 ≤ r2 := by linarith
  have hr1' : r1 ≤ 1 := by linarith
  have hκm : 0 ≤ κm := le_trans (abs_nonneg κ) hκ2
  have hwm : 0 ≤ 2 * wm := by linarith
  have hd : 0 < r2 - r1 := by linarith
  have hd6 : 0 < (r2 - r1) ^ 6 := pow_pos hd 6
  set k := p1K2 ![w1, w2, r1, r2] with hkdef
  have hk : ∀ m, |k m| ≤ 2 * wm := p1_K2_abs_le w1 w2 r1 r2 wm hw1 hw1' hw2 hw2' hr1 hr1' hr2 hr2'
  have hκk : ∀ m, |κ * k m| ≤ κm * (2 * wm) := fun m => by
    rw [abs_mul]; exact mul_le_mul hκ2 (hk m) (abs_nonneg _) hκm
  have hα : |a + κ * k 0| ≤ |a| + κm * (2 * wm) := le_trans (abs_add_le _ _) (by linarith [hκk 0])
  have hE := p1_E_abs_le a κ k _ _ hα (hκk 1) (hκk 2)
  have hC := p1_C_abs_le a κ κmin k (p1U r1 r2) _ 6 hκmin hκ1 hE (p1_U_abs_le r1 r2 hr1 hr1' hr2 hr2')
  set Cb := 4 * ((1 + 2 * (|a| + κm * (2 * wm)) + (|a| + κm * (2 * wm)) ^ 2 + 2 * (κm * (2 * wm)) +
          2 * (|a| + κm * (2 * wm)) * (κm * (2 * wm))) * 6) / κmin ^ 2 with hCb
  have hterm : ∀ n, (p1C a κ k (p1U r1 r2) n / (r2 - r1) ^ 3) * (p1C a κ k (p1U r1 r2) n / (r2 - r1) ^ 3) ≤
      Cb * Cb / (r2 - r1) ^ 6 := by
    intro n
    have h1 : p1C a κ k (p1U r1 r2) n * p1C a κ k (p1U r1 r2) n ≤ Cb * Cb := by
      have h := mul_self_le_mul_self (abs_nonneg _) (hC n)
      rwa [abs_mul_abs_self] at h
    have e : (p1C a κ k (p1U r1 r2) n / (r2 - r1) ^ 3) * (p1C a κ k (p1U r1 r2) n / (r2 - r1) ^ 3) =
        p1C a κ k (p1U r1 r2) n * p1C a κ k (p1U r1 r2) n / (r2 - r1) ^ 6 := by
      (rw [div_mul_div_comm, ← pow_add]) <;> norm_num
    rw [e]
    exact div_le_div_of_nonneg_right h1 hd6.le
  calc _ = ∑ t : Fin (T + 1), (fun n : ℕ => (p1C a κ k (p1U r1 r2) n / (r2 - r1) ^ 3) *
        (p1C a κ k (p1U r1 r2) n / (r2 - r1) ^ 3)) t.val := rfl
    _ = ∑ n ∈ range 5, (p1C a κ k (p1U r1 r2) n / (r2 - r1) ^ 3) * (p1C a κ k (p1U r1 r2) n / (r2 - r1) ^ 3) :=
        p1_sum_fin_range5 T hT (fun n : ℕ => (p1C a κ k (p1U r1 r2) n / (r2 - r1) ^ 3) * (p1C a κ k (p1U r1 r2) n / (r2 - r1) ^ 3))
          fun n hn => by simp only [p1_C_ge a κ k (p1U r1 r2) n hn, zero_div, mul_zero]
    _ ≤ ∑ _n ∈ range 5, Cb * Cb / (r2 - r1) ^ 6 := sum_le_sum fun n _ => hterm n
    _ = 5 * (Cb * Cb) / (r2 - r1) ^ 6 := by rw [sum_const, card_range, nsmul_eq_mul]; first | (push_cast; ring) | push_cast | norm_num

/-! ### Assembly -/

/-- **Lower bound (Phase 6).** `1 ≤ [F_T⁻¹]₁₁ d⁶ B_T`. -/
theorem p1_S71iii_lower (a κ κm wm w1 w2 r1 r2 : ℝ) (T : ℕ) (hT : 4 ≤ T) (hκ0 : κ ≠ 0) (hκ : |κ| ≤ κm)
    (hw1 : 0 < w1) (hw1' : w1 ≤ wm) (hw2 : 0 < w2) (hw2' : w2 ≤ wm) (hr1 : 0 ≤ r1) (hr12 : r1 < r2)
    (hr2' : r2 ≤ 1) :
    1 ≤ ((p1TapJac a κ T ![w1, w2, r1, r2])ᵀ * p1TapJac a κ T ![w1, w2, r1, r2])⁻¹ 0 0 * (r2 - r1) ^ 6 *
      (((T : ℝ) + 1) * ((T : ℝ) ^ 3 * p1TapG |a| κm (2 * wm) T) ^ 2) := by
  have hd : r2 - r1 ≠ 0 := by linarith
  set J := p1TapJac a κ T ![w1, w2, r1, r2] with hJdef
  have hJ := p1_S71iii_isUnit a κ w1 w2 r1 r2 T hT hκ0 hw1.ne' hw2.ne' hd
  have hlow := p1_fisher_entry_lower J hJ 0 ![1, -1, (r2 - r1) / (2 * w1), (r2 - r1) / (2 * w2)]
  have hnorm := p1_S71iii_weak_norm a κ κm wm w1 w2 r1 r2 T hκ hw1 hw1' hw2 hw2' hr1 hr12.le hr2'
  have hF0 : 0 ≤ (Jᵀ * J)⁻¹ 0 0 := by
    rw [← p1_fisher_col_norm J hJ 0]; exact p1_dot_self_nonneg _
  have hv : (![1, -1, (r2 - r1) / (2 * w1), (r2 - r1) / (2 * w2)] : Fin 4 → ℝ) 0 ^ 2 = 1 := by simp
  rw [hv] at hlow
  calc (1 : ℝ) ≤ (Jᵀ * J)⁻¹ 0 0 * ((J *ᵥ ![1, -1, (r2 - r1) / (2 * w1), (r2 - r1) / (2 * w2)]) ⬝ᵥ
        (J *ᵥ ![1, -1, (r2 - r1) / (2 * w1), (r2 - r1) / (2 * w2)])) := hlow
    _ ≤ (Jᵀ * J)⁻¹ 0 0 * (((T : ℝ) + 1) * ((T : ℝ) ^ 3 * p1TapG |a| κm (2 * wm) T) ^ 2 * (r2 - r1) ^ 6) :=
        mul_le_mul_of_nonneg_left hnorm hF0
    _ = (Jᵀ * J)⁻¹ 0 0 * (r2 - r1) ^ 6 * (((T : ℝ) + 1) * ((T : ℝ) ^ 3 * p1TapG |a| κm (2 * wm) T) ^ 2) := by
        ring

/-- **Upper bound (Phase 7).** `[F_T⁻¹]₁₁ d⁶ ≤ 5 C_b²`. -/
theorem p1_S71iii_upper (a κ κmin κm wm w1 w2 r1 r2 : ℝ) (T : ℕ) (hT : 4 ≤ T) (hκmin : 0 < κmin)
    (hκ1 : κmin ≤ |κ|) (hκ2 : |κ| ≤ κm) (hw1 : 0 < w1) (hw1' : w1 ≤ wm) (hw2 : 0 < w2) (hw2' : w2 ≤ wm)
    (hr1 : 0 ≤ r1) (hr12 : r1 < r2) (hr2' : r2 ≤ 1) :
    ((p1TapJac a κ T ![w1, w2, r1, r2])ᵀ * p1TapJac a κ T ![w1, w2, r1, r2])⁻¹ 0 0 * (r2 - r1) ^ 6 ≤
      5 * ((4 * ((1 + 2 * (|a| + κm * (2 * wm)) + (|a| + κm * (2 * wm)) ^ 2 + 2 * (κm * (2 * wm)) +
          2 * (|a| + κm * (2 * wm)) * (κm * (2 * wm))) * 6) / κmin ^ 2) *
        (4 * ((1 + 2 * (|a| + κm * (2 * wm)) + (|a| + κm * (2 * wm)) ^ 2 + 2 * (κm * (2 * wm)) +
          2 * (|a| + κm * (2 * wm)) * (κm * (2 * wm))) * 6) / κmin ^ 2)) := by
  have hκ0 : κ ≠ 0 := fun h => by rw [h, abs_zero] at hκ1; linarith
  have hd : r2 - r1 ≠ 0 := by linarith
  have hd6 : 0 < (r2 - r1) ^ 6 := pow_pos (by linarith) 6
  set J := p1TapJac a κ T ![w1, w2, r1, r2] with hJdef
  have hJ := p1_S71iii_isUnit a κ w1 w2 r1 r2 T hT hκ0 hw1.ne' hw2.ne' hd
  have hup := p1_fisher_entry_upper J hJ 0 _ (p1_S71iii_recover a κ w1 w2 r1 r2 T hT hκ0 hd)
  have hb := p1_S71iii_b_norm a κ κmin κm wm w1 w2 r1 r2 T hT hκmin hκ1 hκ2 hw1.le hw1' hw2.le hw2' hr1 hr12 hr2'
  have h := le_trans hup hb
  rw [le_div_iff₀ hd6] at h
  exact h

/-- **Proposition S7.1 (iii).** For the two-cohort family with known `a`, `κ_min ≤ |κ| ≤ κ_max`, `0 < wᵢ ≤ w_max`,
`0 ≤ r₁ < r₂ ≤ 1`, and observed taps `h₀, …, h_T` with `T ≥ 4`, the weight entry of the inverse Fisher matrix
`F_T = J_TᵀJ_T` of the actual closed-loop response satisfies `c d⁻⁶ ≤ [F_T⁻¹]₁₁ ≤ C d⁻⁶`, with `d = r₂ - r₁` and
`c, C > 0` depending only on `T`, `|a|`, `κ_min`, `κ_max` and `w_max`. -/
theorem p1_prop_S7_1_iii (a κ κmin κm wm w1 w2 r1 r2 : ℝ) (T : ℕ) (hT : 4 ≤ T) (hκmin : 0 < κmin)
    (hκ1 : κmin ≤ |κ|) (hκ2 : |κ| ≤ κm) (hw1 : 0 < w1) (hw1' : w1 ≤ wm) (hw2 : 0 < w2) (hw2' : w2 ≤ wm)
    (hr1 : 0 ≤ r1) (hr12 : r1 < r2) (hr2' : r2 ≤ 1) :
    IsUnit ((p1TapJac a κ T ![w1, w2, r1, r2])ᵀ * p1TapJac a κ T ![w1, w2, r1, r2]).det ∧
    0 < ((T : ℝ) + 1) * ((T : ℝ) ^ 3 * p1TapG |a| κm (2 * wm) T) ^ 2 ∧
    1 / (((T : ℝ) + 1) * ((T : ℝ) ^ 3 * p1TapG |a| κm (2 * wm) T) ^ 2) / (r2 - r1) ^ 6 ≤
      ((p1TapJac a κ T ![w1, w2, r1, r2])ᵀ * p1TapJac a κ T ![w1, w2, r1, r2])⁻¹ 0 0 ∧
    ((p1TapJac a κ T ![w1, w2, r1, r2])ᵀ * p1TapJac a κ T ![w1, w2, r1, r2])⁻¹ 0 0 ≤
      5 * ((4 * ((1 + 2 * (|a| + κm * (2 * wm)) + (|a| + κm * (2 * wm)) ^ 2 + 2 * (κm * (2 * wm)) +
          2 * (|a| + κm * (2 * wm)) * (κm * (2 * wm))) * 6) / κmin ^ 2) *
        (4 * ((1 + 2 * (|a| + κm * (2 * wm)) + (|a| + κm * (2 * wm)) ^ 2 + 2 * (κm * (2 * wm)) +
          2 * (|a| + κm * (2 * wm)) * (κm * (2 * wm))) * 6) / κmin ^ 2)) / (r2 - r1) ^ 6 := by
  have hκ0 : κ ≠ 0 := fun h => by rw [h, abs_zero] at hκ1; linarith
  have hd : r2 - r1 ≠ 0 := by linarith
  have hd6 : 0 < (r2 - r1) ^ 6 := pow_pos (by linarith) 6
  have hJ := p1_S71iii_isUnit a κ w1 w2 r1 r2 T hT hκ0 hw1.ne' hw2.ne' hd
  have hlow := p1_S71iii_lower a κ κm wm w1 w2 r1 r2 T hT hκ0 hκ2 hw1 hw1' hw2 hw2' hr1 hr12 hr2'
  have hup := p1_S71iii_upper a κ κmin κm wm w1 w2 r1 r2 T hT hκmin hκ1 hκ2 hw1 hw1' hw2 hw2' hr1 hr12 hr2'
  generalize hB : ((T : ℝ) + 1) * ((T : ℝ) ^ 3 * p1TapG |a| κm (2 * wm) T) ^ 2 = B at hlow ⊢
  generalize hJdef : p1TapJac a κ T ![w1, w2, r1, r2] = J at hJ hlow hup ⊢
  have hF0 : 0 ≤ (Jᵀ * J)⁻¹ 0 0 := by
    rw [← p1_fisher_col_norm J hJ 0]; exact p1_dot_self_nonneg _
  have hX0 : 0 ≤ (Jᵀ * J)⁻¹ 0 0 * (r2 - r1) ^ 6 := mul_nonneg hF0 hd6.le
  have hBpos : 0 < B := by
    by_contra hneg
    push_neg at hneg
    have : (Jᵀ * J)⁻¹ 0 0 * (r2 - r1) ^ 6 * B ≤ 0 := mul_nonpos_of_nonneg_of_nonpos hX0 hneg
    linarith
  refine ⟨hJ, hBpos, ?_, ?_⟩
  · rw [div_div, div_le_iff₀ (mul_pos hBpos hd6)]
    have e : (Jᵀ * J)⁻¹ 0 0 * (B * (r2 - r1) ^ 6) = (Jᵀ * J)⁻¹ 0 0 * (r2 - r1) ^ 6 * B := by ring
    rw [e]
    exact hlow
  · rw [le_div_iff₀ hd6]
    exact hup

end CurrentMM
