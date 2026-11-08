import CurrentProofs.Paper1CRS71iii
import Mathlib.Algebra.Ring.GeomSum

/-!
# Paper 1, Proposition S7.1 (iii): a lower constant that does not depend on the horizon `T`

`p1_prop_S7_1_iii` gives `c_T d⁻⁶ ≤ [F_T⁻¹]₁₁ ≤ C d⁻⁶`. The upper constant `C = 5 C_b²` already does not depend on
`T`. The lower constant `c_T = 1/B_T` does, because the fixed-horizon majorants `p1TapM`, `p1TapG` grow with `T`.

This file removes the dependence on `T` under a **small-gain stability margin**: there are `ρ < θ < 1` with
`r₁, r₂ ≤ ρ` and

`|a| + κ_max (2 w_max) θ/(θ - ρ) ≤ θ`.

Under it:

* `p1_tap_abs_geom`: the taps decay geometrically, `|h_j| ≤ κ_max θ^j`.
* `p1_Q_geom`: the cubic factor of the kernel derivative decays, `|Q_m| ≤ θ₁^m/(2(θ₁ - ρ)³)` for every `θ₁ > ρ`.
* `p1_tapD_abs_geom`: the derivative of the taps along the weak direction satisfies `|g_j| ≤ F j θ^j`.
* `p1_S71iii_weak_norm_uniform`: `‖J_T v‖² ≤ B d⁶` with `B` free of `T`.
* `p1_prop_S7_1_iii_uniform`: `1/(B d⁶) ≤ [F_T⁻¹]₁₁ ≤ 5 C_b²/d⁶` for every `T ≥ 4`, with
  `B = p1UnifB κ_max ρ θ = 256 κ_max⁴ (1 + θ)²/((θ - ρ)⁸ (1 - θ)³ (3 + θ))`.

The margin is a sufficient condition (an ℓ¹ small-gain bound on the closed loop), not the sharp stability region.
-/

namespace CurrentMM

open Finset Matrix

/-! ### Geometric sums -/

theorem p1_geom_sum_le_inv (q : ℝ) (hq0 : 0 ≤ q) (hq1 : q < 1) (n : ℕ) :
    ∑ m ∈ range n, q ^ m ≤ 1 / (1 - q) := by
  rw [le_div_iff₀ (by linarith)]
  have h := mul_neg_geom_sum q n
  have hp : 0 ≤ q ^ n := pow_nonneg hq0 n
  calc (∑ m ∈ range n, q ^ m) * (1 - q) = (1 - q) * ∑ m ∈ range n, q ^ m := mul_comm _ _
    _ = 1 - q ^ n := h
    _ ≤ 1 := by linarith

/-- `Σ_{m ≤ j} ρ^m θ^{j-m} ≤ θ^{j+1}/(θ - ρ)` for `0 ≤ ρ < θ`. -/
theorem p1_conv_geom_le (ρ θ : ℝ) (hρ : 0 ≤ ρ) (hρθ : ρ < θ) (j : ℕ) :
    ∑ m ∈ range (j + 1), ρ ^ m * θ ^ (j - m) ≤ θ ^ (j + 1) / (θ - ρ) := by
  have hθ : 0 < θ := lt_of_le_of_lt hρ hρθ
  have hd : θ - ρ ≠ 0 := by linarith
  have hterm : ∀ m ∈ range (j + 1), ρ ^ m * θ ^ (j - m) = θ ^ j * (ρ / θ) ^ m := by
    intro m hm
    have hmj : m ≤ j := Nat.lt_succ_iff.mp (mem_range.mp hm)
    obtain ⟨n, rfl⟩ := Nat.exists_eq_add_of_le hmj
    rw [show m + n - m = n by omega, div_pow, pow_add]
    have : θ ^ m ≠ 0 := pow_ne_zero m hθ.ne'
    first
    | (field_simp; done)
    | (field_simp; ring)
  rw [sum_congr rfl hterm, ← mul_sum]
  have hq0 : 0 ≤ ρ / θ := div_nonneg hρ hθ.le
  have hq1 : ρ / θ < 1 := (div_lt_one hθ).mpr hρθ
  have hg := p1_geom_sum_le_inv (ρ / θ) hq0 hq1 (j + 1)
  calc θ ^ j * ∑ m ∈ range (j + 1), (ρ / θ) ^ m ≤ θ ^ j * (1 / (1 - ρ / θ)) :=
        mul_le_mul_of_nonneg_left hg (pow_nonneg hθ.le j)
    _ = θ ^ (j + 1) / (θ - ρ) := by
        have e : 1 - ρ / θ = (θ - ρ) / θ := by field_simp
        rw [e, pow_succ]
        field_simp

/-- **A first-order recursion with geometric forcing stays geometric.** -/
theorem p1_lin_rec_geom (y c f : ℕ → ℝ) (ρ θ X F : ℝ) (hρ : 0 ≤ ρ) (hθ : 0 ≤ θ)
    (hy : ∀ j, y (j + 1) = c j * y j + f j) (hc : ∀ j, |c j| ≤ ρ) (hf : ∀ j, |f j| ≤ F * θ ^ (j + 1))
    (h0 : |y 0| ≤ X) (hX : ρ * X + F * θ ≤ X * θ) : ∀ j, |y j| ≤ X * θ ^ j := by
  intro j
  induction j with
  | zero => simpa using h0
  | succ j ih =>
    rw [hy j]
    have hθj : 0 ≤ θ ^ j := pow_nonneg hθ j
    calc |c j * y j + f j| ≤ |c j| * |y j| + |f j| := by rw [← abs_mul]; exact abs_add_le _ _
      _ ≤ ρ * (X * θ ^ j) + F * θ ^ (j + 1) := add_le_add (mul_le_mul (hc j) ih (abs_nonneg _) hρ) (hf j)
      _ = θ ^ j * (ρ * X + F * θ) := by rw [pow_succ]; ring
      _ ≤ θ ^ j * (X * θ) := mul_le_mul_of_nonneg_left hX hθj
      _ = X * θ ^ (j + 1) := by rw [pow_succ]; ring

/-- `j θ^j ≤ θ'/(θ' - θ) θ'^j` for `0 ≤ θ < θ'`. -/
theorem p1_lin_geom (θ θ' : ℝ) (hθ : 0 ≤ θ) (hθθ' : θ < θ') (j : ℕ) :
    (j : ℝ) * θ ^ j ≤ θ' / (θ' - θ) * θ' ^ j := by
  have hθ' : 0 < θ' := lt_of_le_of_lt hθ hθθ'
  have hd : 0 < θ' - θ := by linarith
  refine le_trans (le_abs_self _) (p1_lin_rec_geom (fun j => (j : ℝ) * θ ^ j) (fun _ => θ) (fun j => θ ^ (j + 1))
    θ θ' (θ' / (θ' - θ)) 1 hθ hθ'.le ?_ ?_ ?_ ?_ ?_ j)
  · intro j; push_cast; ring
  · intro _; rw [abs_of_nonneg hθ]
  · intro j; rw [abs_of_nonneg (pow_nonneg hθ _), one_mul]; exact pow_le_pow_left₀ hθ hθθ'.le _
  · rw [Nat.cast_zero, zero_mul, abs_zero]; exact (div_pos hθ' hd).le
  · apply le_of_eq; field_simp; ring

/-! ### The cubic factor decays geometrically -/

theorem p1_P_geom (r1 ρ θ : ℝ) (hr : |r1| ≤ ρ) (hρ : 0 ≤ ρ) (hρθ : ρ < θ) (j : ℕ) :
    |((j : ℝ) + 1) * r1 ^ j| ≤ θ / (θ - ρ) * θ ^ j := by
  have hθ : 0 < θ := lt_of_le_of_lt hρ hρθ
  have hd : 0 < θ - ρ := by linarith
  refine p1_lin_rec_geom (fun j => ((j : ℝ) + 1) * r1 ^ j) (fun _ => r1) (fun j => r1 ^ (j + 1)) ρ θ (θ / (θ - ρ)) 1
    hρ hθ.le ?_ (fun _ => hr) ?_ ?_ ?_ j
  · intro j; push_cast; ring
  · intro j; rw [abs_pow, one_mul]; exact pow_le_pow_left₀ (abs_nonneg _) (le_trans hr hρθ.le) _
  · rw [Nat.cast_zero, zero_add, pow_zero, mul_one, abs_one, le_div_iff₀ hd]; linarith
  · apply le_of_eq; field_simp; ring

theorem p1_S_geom (r1 r2 ρ θ : ℝ) (h1 : |r1| ≤ ρ) (h2 : |r2| ≤ ρ) (hρ : 0 ≤ ρ) (hρθ : ρ < θ) (j : ℕ) :
    |p1S r1 r2 (j + 1)| ≤ θ / (θ - ρ) ^ 2 * θ ^ j := by
  have hθ : 0 < θ := lt_of_le_of_lt hρ hρθ
  have hd : 0 < θ - ρ := by linarith
  refine p1_lin_rec_geom (fun j => p1S r1 r2 (j + 1)) (fun _ => r2) (fun j => ((j : ℝ) + 1) * r1 ^ j) ρ θ
    (θ / (θ - ρ) ^ 2) (1 / (θ - ρ)) hρ hθ.le (fun j => rfl) (fun _ => h2) ?_ ?_ ?_ j
  · intro j
    refine le_trans (p1_P_geom r1 ρ θ h1 hρ hρθ j) (le_of_eq ?_)
    rw [pow_succ]
    first
    | (field_simp; done)
    | (field_simp; ring)
    | ring
  · show |p1S r1 r2 1| ≤ _
    rw [show p1S r1 r2 1 = 0 from rfl, abs_zero]
    exact div_nonneg hθ.le (sq_nonneg _)
  · apply le_of_eq; field_simp; ring

theorem p1_Q_geom2 (r1 r2 ρ θ : ℝ) (h1 : |r1| ≤ ρ) (h2 : |r2| ≤ ρ) (hρ : 0 ≤ ρ) (hρθ : ρ < θ) (j : ℕ) :
    |p1Q r1 r2 (j + 2)| ≤ θ ^ 2 / (2 * (θ - ρ) ^ 3) * θ ^ j := by
  have hθ : 0 < θ := lt_of_le_of_lt hρ hρθ
  have hd : 0 < θ - ρ := by linarith
  refine p1_lin_rec_geom (fun j => p1Q r1 r2 (j + 2)) (fun _ => r2) (fun j => p1S r1 r2 (j + 2) / 2) ρ θ
    (θ ^ 2 / (2 * (θ - ρ) ^ 3)) (θ / (2 * (θ - ρ) ^ 2)) hρ hθ.le (fun j => rfl) (fun _ => h2) ?_ ?_ ?_ j
  · intro j
    have hS := p1_S_geom r1 r2 ρ θ h1 h2 hρ hρθ (j + 1)
    show |p1S r1 r2 (j + 2) / 2| ≤ _
    rw [abs_div, abs_two]
    calc |p1S r1 r2 (j + 2)| / 2 ≤ θ / (θ - ρ) ^ 2 * θ ^ (j + 1) / 2 := div_le_div_of_nonneg_right hS (by norm_num)
      _ = θ / (2 * (θ - ρ) ^ 2) * θ ^ (j + 1) := by rw [mul_comm (2 : ℝ), ← div_div]; ring
  · show |p1Q r1 r2 (0 + 1 + 1)| ≤ _
    rw [show p1Q r1 r2 (0 + 1 + 1) = r2 * (r2 * p1Q r1 r2 0 + p1S r1 r2 0 / 2) + p1S r1 r2 (0 + 1) / 2 from rfl,
      show p1Q r1 r2 0 = 0 from rfl, show p1S r1 r2 0 = 0 from rfl, show p1S r1 r2 (0 + 1) = 0 from rfl]
    simp only [mul_zero, zero_div, add_zero, abs_zero]
    exact div_nonneg (sq_nonneg θ) (mul_pos two_pos (pow_pos hd 3)).le
  · apply le_of_eq; field_simp; ring

/-- **The kernel derivative's cubic factor decays.** `|Q_m| ≤ θ^m/(2(θ - ρ)³)` for `|r₁|, |r₂| ≤ ρ < θ`. -/
theorem p1_Q_geom (r1 r2 ρ θ : ℝ) (h1 : |r1| ≤ ρ) (h2 : |r2| ≤ ρ) (hρ : 0 ≤ ρ) (hρθ : ρ < θ) (m : ℕ) :
    |p1Q r1 r2 m| ≤ θ ^ m / (2 * (θ - ρ) ^ 3) := by
  have hθ : 0 < θ := lt_of_le_of_lt hρ hρθ
  have hd : 0 < θ - ρ := by linarith
  have hden : 0 < 2 * (θ - ρ) ^ 3 := mul_pos two_pos (pow_pos hd 3)
  rcases m with _ | _ | j
  · rw [show p1Q r1 r2 0 = 0 from rfl, abs_zero]
    exact div_nonneg (pow_nonneg hθ.le _) hden.le
  · show |p1Q r1 r2 (0 + 1)| ≤ θ ^ (0 + 1) / (2 * (θ - ρ) ^ 3)
    rw [show p1Q r1 r2 (0 + 1) = r2 * p1Q r1 r2 0 + p1S r1 r2 0 / 2 from rfl,
      show p1Q r1 r2 0 = 0 from rfl, show p1S r1 r2 0 = 0 from rfl]
    simp only [mul_zero, zero_div, add_zero, abs_zero]
    exact div_nonneg (pow_nonneg hθ.le _) hden.le
  · have h := p1_Q_geom2 r1 r2 ρ θ h1 h2 hρ hρθ j
    refine le_trans h (le_of_eq ?_)
    ring

/-! ### Geometric decay of the taps and of their derivative -/

theorem p1_K2_abs_geom (w1 w2 r1 r2 wm ρ : ℝ) (hw1 : 0 ≤ w1) (hw1' : w1 ≤ wm) (hw2 : 0 ≤ w2) (hw2' : w2 ≤ wm)
    (hr1 : 0 ≤ r1) (hr1' : r1 ≤ ρ) (hr2 : 0 ≤ r2) (hr2' : r2 ≤ ρ) (m : ℕ) :
    |p1K2 ![w1, w2, r1, r2] m| ≤ 2 * wm * ρ ^ m := by
  have e : p1K2 ![w1, w2, r1, r2] m = w1 * r1 ^ m + w2 * r2 ^ m := by simp [p1K2]
  rw [e]
  have p1 : r1 ^ m ≤ ρ ^ m := pow_le_pow_left₀ hr1 hr1' m
  have p2 : r2 ^ m ≤ ρ ^ m := pow_le_pow_left₀ hr2 hr2' m
  have b1 : 0 ≤ w1 * r1 ^ m := mul_nonneg hw1 (pow_nonneg hr1 m)
  have b2 : 0 ≤ w2 * r2 ^ m := mul_nonneg hw2 (pow_nonneg hr2 m)
  have c1 : w1 * r1 ^ m ≤ wm * ρ ^ m := mul_le_mul hw1' p1 (pow_nonneg hr1 m) (le_trans hw1 hw1')
  have c2 : w2 * r2 ^ m ≤ wm * ρ ^ m := mul_le_mul hw2' p2 (pow_nonneg hr2 m) (le_trans hw2 hw2')
  rw [abs_of_nonneg (add_nonneg b1 b2)]
  linarith

/-- **Taps decay geometrically under the small-gain margin.** -/
theorem p1_tap_abs_geom (a κ : ℝ) (k : ℕ → ℝ) (κm K ρ θ : ℝ) (hκ : |κ| ≤ κm) (hK : 0 ≤ K) (hρ : 0 ≤ ρ)
    (hρθ : ρ < θ) (hk : ∀ m, |k m| ≤ K * ρ ^ m) (hmar : |a| + κm * K * θ / (θ - ρ) ≤ θ) :
    ∀ j, |p1Tap a κ k j| ≤ κm * θ ^ j := by
  have hκm : 0 ≤ κm := le_trans (abs_nonneg κ) hκ
  have hθ : 0 < θ := lt_of_le_of_lt hρ hρθ
  intro j
  refine Nat.strong_induction_on j ?_
  intro j ih
  rcases j with _ | j
  · rw [p1_tap_zero, pow_zero, mul_one]; exact hκ
  · rw [p1_tap_succ]
    have hsum : |∑ m ∈ range (j + 1), k m * p1Tap a κ k (j - m)| ≤ K * κm * (θ ^ (j + 1) / (θ - ρ)) := by
      calc _ ≤ ∑ m ∈ range (j + 1), |k m * p1Tap a κ k (j - m)| := abs_sum_le_sum_abs _ _
        _ ≤ ∑ m ∈ range (j + 1), K * κm * (ρ ^ m * θ ^ (j - m)) := by
            refine sum_le_sum fun m _ => ?_
            rw [abs_mul]
            calc |k m| * |p1Tap a κ k (j - m)| ≤ (K * ρ ^ m) * (κm * θ ^ (j - m)) :=
                  mul_le_mul (hk m) (ih (j - m) (by omega)) (abs_nonneg _) (mul_nonneg hK (pow_nonneg hρ m))
              _ = K * κm * (ρ ^ m * θ ^ (j - m)) := by ring
        _ = K * κm * ∑ m ∈ range (j + 1), ρ ^ m * θ ^ (j - m) := by rw [mul_sum]
        _ ≤ K * κm * (θ ^ (j + 1) / (θ - ρ)) :=
            mul_le_mul_of_nonneg_left (p1_conv_geom_le ρ θ hρ hρθ j) (mul_nonneg hK hκm)
    have hh := ih j (Nat.lt_succ_self j)
    have hθj : 0 ≤ κm * θ ^ j := mul_nonneg hκm (pow_nonneg hθ.le j)
    calc |a * p1Tap a κ k j + κ * ∑ m ∈ range (j + 1), k m * p1Tap a κ k (j - m)|
        ≤ |a| * |p1Tap a κ k j| + |κ| * |∑ m ∈ range (j + 1), k m * p1Tap a κ k (j - m)| := by
          rw [← abs_mul, ← abs_mul]; exact abs_add_le _ _
      _ ≤ |a| * (κm * θ ^ j) + κm * (K * κm * (θ ^ (j + 1) / (θ - ρ))) :=
          add_le_add (mul_le_mul_of_nonneg_left hh (abs_nonneg a)) (mul_le_mul hκ hsum (abs_nonneg _) hκm)
      _ = κm * θ ^ j * (|a| + κm * K * θ / (θ - ρ)) := by rw [pow_succ]; ring
      _ ≤ κm * θ ^ j * θ := mul_le_mul_of_nonneg_left hmar hθj
      _ = κm * θ ^ (j + 1) := by rw [pow_succ]; ring

/-- **The derivative of the taps grows at most like `j θ^j`.** With `|k'_m| ≤ E θ₁^m`, `θ₁ < θ`. -/
theorem p1_tapD_abs_geom (a κ : ℝ) (k k' : ℕ → ℝ) (κm K ρ θ E θ1 : ℝ) (hκ : |κ| ≤ κm) (hK : 0 ≤ K)
    (hρ : 0 ≤ ρ) (hρθ : ρ < θ) (hθ1 : 0 ≤ θ1) (hθ1θ : θ1 < θ) (hE : 0 ≤ E)
    (hk : ∀ m, |k m| ≤ K * ρ ^ m) (hk' : ∀ m, |k' m| ≤ E * θ1 ^ m)
    (hmar : |a| + κm * K * θ / (θ - ρ) ≤ θ) :
    ∀ j, |p1TapD a κ k k' j| ≤ κm ^ 2 * E / (θ - θ1) * (j : ℝ) * θ ^ j := by
  have hκm : 0 ≤ κm := le_trans (abs_nonneg κ) hκ
  have hθ : 0 < θ := lt_of_le_of_lt hρ hρθ
  have hd1 : 0 < θ - θ1 := by linarith
  have htap := p1_tap_abs_geom a κ k κm K ρ θ hκ hK hρ hρθ hk hmar
  have hF0 : 0 ≤ κm ^ 2 * E / (θ - θ1) := div_nonneg (mul_nonneg (sq_nonneg _) hE) hd1.le
  intro j
  refine Nat.strong_induction_on j ?_
  intro j ih
  rcases j with _ | j
  · rw [p1_tapD_zero]; simp
  · rw [p1_tapD_succ]
    have hfor : ∑ m ∈ range (j + 1), |k' m * p1Tap a κ k (j - m)| ≤ E * κm * (θ ^ (j + 1) / (θ - θ1)) := by
      calc _ ≤ ∑ m ∈ range (j + 1), E * κm * (θ1 ^ m * θ ^ (j - m)) := by
            refine sum_le_sum fun m _ => ?_
            rw [abs_mul]
            calc |k' m| * |p1Tap a κ k (j - m)| ≤ (E * θ1 ^ m) * (κm * θ ^ (j - m)) :=
                  mul_le_mul (hk' m) (htap (j - m)) (abs_nonneg _) (mul_nonneg hE (pow_nonneg hθ1 m))
              _ = E * κm * (θ1 ^ m * θ ^ (j - m)) := by ring
        _ = E * κm * ∑ m ∈ range (j + 1), θ1 ^ m * θ ^ (j - m) := by rw [mul_sum]
        _ ≤ E * κm * (θ ^ (j + 1) / (θ - θ1)) :=
            mul_le_mul_of_nonneg_left (p1_conv_geom_le θ1 θ hθ1 hθ1θ j) (mul_nonneg hE hκm)
    have hfb : ∑ m ∈ range (j + 1), |k m * p1TapD a κ k k' (j - m)| ≤
        K * (κm ^ 2 * E / (θ - θ1) * (j : ℝ)) * (θ ^ (j + 1) / (θ - ρ)) := by
      calc _ ≤ ∑ m ∈ range (j + 1), K * (κm ^ 2 * E / (θ - θ1) * (j : ℝ)) * (ρ ^ m * θ ^ (j - m)) := by
            refine sum_le_sum fun m hm => ?_
            rw [abs_mul]
            have hc : ((j - m : ℕ) : ℝ) ≤ (j : ℝ) := by exact_mod_cast Nat.sub_le j m
            have hg := ih (j - m) (by omega)
            have hg' : |p1TapD a κ k k' (j - m)| ≤ κm ^ 2 * E / (θ - θ1) * (j : ℝ) * θ ^ (j - m) :=
              le_trans hg (mul_le_mul_of_nonneg_right (mul_le_mul_of_nonneg_left hc hF0) (pow_nonneg hθ.le _))
            calc |k m| * |p1TapD a κ k k' (j - m)| ≤
                  (K * ρ ^ m) * (κm ^ 2 * E / (θ - θ1) * (j : ℝ) * θ ^ (j - m)) :=
                  mul_le_mul (hk m) hg' (abs_nonneg _) (mul_nonneg hK (pow_nonneg hρ m))
              _ = K * (κm ^ 2 * E / (θ - θ1) * (j : ℝ)) * (ρ ^ m * θ ^ (j - m)) := by ring
        _ = K * (κm ^ 2 * E / (θ - θ1) * (j : ℝ)) * ∑ m ∈ range (j + 1), ρ ^ m * θ ^ (j - m) := by
            rw [mul_sum]
        _ ≤ K * (κm ^ 2 * E / (θ - θ1) * (j : ℝ)) * (θ ^ (j + 1) / (θ - ρ)) :=
            mul_le_mul_of_nonneg_left (p1_conv_geom_le ρ θ hρ hρθ j)
              (mul_nonneg hK (mul_nonneg hF0 (Nat.cast_nonneg j)))
    have hS : |∑ m ∈ range (j + 1), (k' m * p1Tap a κ k (j - m) + k m * p1TapD a κ k k' (j - m))| ≤
        E * κm * (θ ^ (j + 1) / (θ - θ1)) + K * (κm ^ 2 * E / (θ - θ1) * (j : ℝ)) * (θ ^ (j + 1) / (θ - ρ)) := by
      calc _ ≤ ∑ m ∈ range (j + 1), |k' m * p1Tap a κ k (j - m) + k m * p1TapD a κ k k' (j - m)| :=
            abs_sum_le_sum_abs _ _
        _ ≤ ∑ m ∈ range (j + 1), (|k' m * p1Tap a κ k (j - m)| + |k m * p1TapD a κ k k' (j - m)|) :=
            sum_le_sum fun m _ => abs_add_le _ _
        _ = ∑ m ∈ range (j + 1), |k' m * p1Tap a κ k (j - m)| +
            ∑ m ∈ range (j + 1), |k m * p1TapD a κ k k' (j - m)| := sum_add_distrib
        _ ≤ _ := add_le_add hfor hfb
    have hh := ih j (Nat.lt_succ_self j)
    have hθj : 0 ≤ κm ^ 2 * E / (θ - θ1) * (j : ℝ) * θ ^ j :=
      mul_nonneg (mul_nonneg hF0 (Nat.cast_nonneg j)) (pow_nonneg hθ.le j)
    have hS0 : 0 ≤ κm ^ 2 * E / (θ - θ1) * θ ^ (j + 1) := mul_nonneg hF0 (pow_nonneg hθ.le _)
    calc |a * p1TapD a κ k k' j +
          κ * ∑ m ∈ range (j + 1), (k' m * p1Tap a κ k (j - m) + k m * p1TapD a κ k k' (j - m))|
        ≤ |a| * |p1TapD a κ k k' j| +
          |κ| * |∑ m ∈ range (j + 1), (k' m * p1Tap a κ k (j - m) + k m * p1TapD a κ k k' (j - m))| := by
          rw [← abs_mul, ← abs_mul]; exact abs_add_le _ _
      _ ≤ |a| * (κm ^ 2 * E / (θ - θ1) * (j : ℝ) * θ ^ j) +
          κm * (E * κm * (θ ^ (j + 1) / (θ - θ1)) +
            K * (κm ^ 2 * E / (θ - θ1) * (j : ℝ)) * (θ ^ (j + 1) / (θ - ρ))) :=
          add_le_add (mul_le_mul_of_nonneg_left hh (abs_nonneg a)) (mul_le_mul hκ hS (abs_nonneg _) hκm)
      _ = κm ^ 2 * E / (θ - θ1) * (j : ℝ) * θ ^ j * (|a| + κm * K * θ / (θ - ρ)) +
          κm ^ 2 * E / (θ - θ1) * θ ^ (j + 1) := by rw [pow_succ]; ring
      _ ≤ κm ^ 2 * E / (θ - θ1) * (j : ℝ) * θ ^ j * θ + κm ^ 2 * E / (θ - θ1) * θ ^ (j + 1) :=
          add_le_add (mul_le_mul_of_nonneg_left hmar hθj) le_rfl
      _ = κm ^ 2 * E / (θ - θ1) * ((j + 1 : ℕ) : ℝ) * θ ^ (j + 1) := by push_cast; rw [pow_succ]; ring

/-! ### The weak direction, uniformly in `T` -/

/-- **`‖J_T v‖² ≤ B d⁶` with `B` independent of `T`.** -/
theorem p1_S71iii_weak_norm_uniform (a κ κm wm w1 w2 r1 r2 ρ θ1 θ θ' : ℝ) (T : ℕ) (hκ : |κ| ≤ κm)
    (hw1 : 0 < w1) (hw1' : w1 ≤ wm) (hw2 : 0 < w2) (hw2' : w2 ≤ wm) (hr1 : 0 ≤ r1) (hr12 : r1 ≤ r2)
    (hr2ρ : r2 ≤ ρ) (hρθ1 : ρ < θ1) (hθ1θ : θ1 < θ) (hθθ' : θ < θ') (hθ'1 : θ' < 1)
    (hmar : |a| + κm * (2 * wm) * θ / (θ - ρ) ≤ θ) :
    (p1TapJac a κ T ![w1, w2, r1, r2] *ᵥ ![1, -1, (r2 - r1) / (2 * w1), (r2 - r1) / (2 * w2)]) ⬝ᵥ
        (p1TapJac a κ T ![w1, w2, r1, r2] *ᵥ ![1, -1, (r2 - r1) / (2 * w1), (r2 - r1) / (2 * w2)]) ≤
      (κm ^ 2 * (1 / (2 * (θ1 - ρ) ^ 3)) / (θ - θ1) * (θ' / (θ' - θ))) ^ 2 / (1 - θ' ^ 2) * (r2 - r1) ^ 6 := by
  have hr2 : 0 ≤ r2 := le_trans hr1 hr12
  have hρ : 0 ≤ ρ := le_trans hr2 hr2ρ
  have hθ1 : 0 ≤ θ1 := by linarith
  have hθ : 0 ≤ θ := by linarith
  have hθ' : 0 < θ' := by linarith
  have hd : 0 ≤ r2 - r1 := by linarith
  have hd3 : 0 ≤ (r2 - r1) ^ 3 := pow_nonneg hd 3
  have hwm : 0 ≤ 2 * wm := by linarith
  have hκm : 0 ≤ κm := le_trans (abs_nonneg κ) hκ
  have hθ1ρ : 0 < θ1 - ρ := by linarith
  have hc0 : 0 ≤ 1 / (2 * (θ1 - ρ) ^ 3) := (div_pos one_pos (mul_pos two_pos (pow_pos hθ1ρ 3))).le
  obtain ⟨E, hE⟩ : ∃ E : ℝ, E = (r2 - r1) ^ 3 * (1 / (2 * (θ1 - ρ) ^ 3)) := ⟨_, rfl⟩
  have hE0 : 0 ≤ E := by rw [hE]; exact mul_nonneg hd3 hc0
  have habs1 : |r1| ≤ ρ := abs_le.mpr ⟨by linarith, by linarith⟩
  have habs2 : |r2| ≤ ρ := abs_le.mpr ⟨by linarith, hr2ρ⟩
  have hk : ∀ m, |p1K2 ![w1, w2, r1, r2] m| ≤ 2 * wm * ρ ^ m :=
    p1_K2_abs_geom w1 w2 r1 r2 wm ρ hw1.le hw1' hw2.le hw2' hr1 (le_trans hr12 hr2ρ) hr2 hr2ρ
  have hk' : ∀ m, |p1K2D ![w1, w2, r1, r2] ![1, -1, (r2 - r1) / (2 * w1), (r2 - r1) / (2 * w2)] m| ≤
      E * θ1 ^ m := by
    intro m
    rw [p1_K2D_weak w1 w2 r1 r2 hw1.ne' hw2.ne' m, abs_mul, abs_of_nonneg hd3, hE, mul_assoc]
    apply mul_le_mul_of_nonneg_left _ hd3
    calc |p1Q r1 r2 m| ≤ θ1 ^ m / (2 * (θ1 - ρ) ^ 3) := p1_Q_geom r1 r2 ρ θ1 habs1 habs2 hρ hρθ1 m
      _ = 1 / (2 * (θ1 - ρ) ^ 3) * θ1 ^ m := by ring
  have hg := p1_tapD_abs_geom a κ _ _ κm (2 * wm) ρ θ E θ1 hκ hwm hρ (by linarith) hθ1 hθ1θ hE0 hk hk' hmar
  have hF0 : 0 ≤ κm ^ 2 * E / (θ - θ1) := div_nonneg (mul_nonneg (sq_nonneg _) hE0) (by linarith)
  obtain ⟨X, hX⟩ : ∃ X : ℝ, X = θ' / (θ' - θ) := ⟨_, rfl⟩
  have hcomp : ∀ t : Fin (T + 1),
      |(p1TapJac a κ T ![w1, w2, r1, r2] *ᵥ ![1, -1, (r2 - r1) / (2 * w1), (r2 - r1) / (2 * w2)]) t| ≤
        κm ^ 2 * E / (θ - θ1) * X * θ' ^ (t : ℕ) := by
    intro t
    rw [p1_tapJac_mulVec]
    calc _ ≤ κm ^ 2 * E / (θ - θ1) * ((t : ℕ) : ℝ) * θ ^ (t : ℕ) := hg t.val
      _ = κm ^ 2 * E / (θ - θ1) * (((t : ℕ) : ℝ) * θ ^ (t : ℕ)) := by ring
      _ ≤ κm ^ 2 * E / (θ - θ1) * (X * θ' ^ (t : ℕ)) := by
          rw [hX]; exact mul_le_mul_of_nonneg_left (p1_lin_geom θ θ' hθ hθθ' t.val) hF0
      _ = κm ^ 2 * E / (θ - θ1) * X * θ' ^ (t : ℕ) := by ring
  have hq1 : θ' ^ 2 < 1 := by nlinarith
  calc _ = ∑ t : Fin (T + 1),
        (p1TapJac a κ T ![w1, w2, r1, r2] *ᵥ ![1, -1, (r2 - r1) / (2 * w1), (r2 - r1) / (2 * w2)]) t *
        (p1TapJac a κ T ![w1, w2, r1, r2] *ᵥ ![1, -1, (r2 - r1) / (2 * w1), (r2 - r1) / (2 * w2)]) t := rfl
    _ ≤ ∑ t : Fin (T + 1), (κm ^ 2 * E / (θ - θ1) * X) ^ 2 * (θ' ^ 2) ^ (t : ℕ) := by
        refine sum_le_sum fun t _ => ?_
        have h := mul_self_le_mul_self (abs_nonneg _) (hcomp t)
        rw [abs_mul_abs_self] at h
        refine le_trans h (le_of_eq ?_)
        first
        | ring
        | (rw [← pow_mul]; ring)
    _ = ∑ t ∈ range (T + 1), (κm ^ 2 * E / (θ - θ1) * X) ^ 2 * (θ' ^ 2) ^ t :=
        Fin.sum_univ_eq_sum_range (fun t => (κm ^ 2 * E / (θ - θ1) * X) ^ 2 * (θ' ^ 2) ^ t) (T + 1)
    _ = (κm ^ 2 * E / (θ - θ1) * X) ^ 2 * ∑ t ∈ range (T + 1), (θ' ^ 2) ^ t := by rw [mul_sum]
    _ ≤ (κm ^ 2 * E / (θ - θ1) * X) ^ 2 * (1 / (1 - θ' ^ 2)) :=
        mul_le_mul_of_nonneg_left (p1_geom_sum_le_inv _ (sq_nonneg _) hq1 _) (sq_nonneg _)
    _ = _ := by rw [hE, hX]; ring

/-! ### Assembly -/

/-- The `T`-free constant: `B = 256 κ_max⁴ (1 + θ)²/((θ - ρ)⁸ (1 - θ)³ (3 + θ))`. -/
noncomputable def p1UnifB (κm ρ θ : ℝ) : ℝ :=
  256 * κm ^ 4 * (1 + θ) ^ 2 / ((θ - ρ) ^ 8 * (1 - θ) ^ 3 * (3 + θ))

theorem p1_unifB_eq (κm ρ θ : ℝ) (hρθ : ρ < θ) (hθ1 : θ < 1) (hθ0 : 0 ≤ θ) :
    (κm ^ 2 * (1 / (2 * ((ρ + θ) / 2 - ρ) ^ 3)) / (θ - (ρ + θ) / 2) * ((1 + θ) / 2 / ((1 + θ) / 2 - θ))) ^ 2 /
      (1 - ((1 + θ) / 2) ^ 2) = p1UnifB κm ρ θ := by
  have hd : θ - ρ ≠ 0 := by linarith
  have h1 : 1 - θ ≠ 0 := by linarith
  have h3 : 3 + θ ≠ 0 := by linarith
  have e1 : (ρ + θ) / 2 - ρ = (θ - ρ) / 2 := by ring
  have e2 : θ - (ρ + θ) / 2 = (θ - ρ) / 2 := by ring
  have e3 : (1 + θ) / 2 - θ = (1 - θ) / 2 := by ring
  have e4 : 1 - ((1 + θ) / 2) ^ 2 = (1 - θ) * (3 + θ) / 4 := by ring
  rw [e1, e2, e3, e4, p1UnifB]
  field_simp
  ring

/-- **Proposition S7.1 (iii), uniformly in the horizon.** Under the small-gain margin
`|a| + κ_max (2 w_max) θ/(θ - ρ) ≤ θ` with `r₁, r₂ ≤ ρ < θ < 1`, for every `T ≥ 4`,
`1/(B d⁶) ≤ [F_T⁻¹]₁₁ ≤ 5 C_b²/d⁶`, where `B = p1UnifB κ_max ρ θ` and `C_b` do not depend on `T`. -/
theorem p1_prop_S7_1_iii_uniform (a κ κmin κm wm w1 w2 r1 r2 ρ θ : ℝ) (T : ℕ) (hT : 4 ≤ T) (hκmin : 0 < κmin)
    (hκ1 : κmin ≤ |κ|) (hκ2 : |κ| ≤ κm) (hw1 : 0 < w1) (hw1' : w1 ≤ wm) (hw2 : 0 < w2) (hw2' : w2 ≤ wm)
    (hr1 : 0 ≤ r1) (hr12 : r1 < r2) (hr2ρ : r2 ≤ ρ) (hρθ : ρ < θ) (hθ1 : θ < 1)
    (hmar : |a| + κm * (2 * wm) * θ / (θ - ρ) ≤ θ) :
    0 < p1UnifB κm ρ θ ∧
    1 / p1UnifB κm ρ θ / (r2 - r1) ^ 6 ≤
      ((p1TapJac a κ T ![w1, w2, r1, r2])ᵀ * p1TapJac a κ T ![w1, w2, r1, r2])⁻¹ 0 0 ∧
    ((p1TapJac a κ T ![w1, w2, r1, r2])ᵀ * p1TapJac a κ T ![w1, w2, r1, r2])⁻¹ 0 0 ≤
      5 * ((4 * ((1 + 2 * (|a| + κm * (2 * wm)) + (|a| + κm * (2 * wm)) ^ 2 + 2 * (κm * (2 * wm)) +
          2 * (|a| + κm * (2 * wm)) * (κm * (2 * wm))) * 6) / κmin ^ 2) *
        (4 * ((1 + 2 * (|a| + κm * (2 * wm)) + (|a| + κm * (2 * wm)) ^ 2 + 2 * (κm * (2 * wm)) +
          2 * (|a| + κm * (2 * wm)) * (κm * (2 * wm))) * 6) / κmin ^ 2)) / (r2 - r1) ^ 6 := by
  have hr2 : 0 ≤ r2 := by linarith
  have hρ : 0 ≤ ρ := by linarith
  have hθ0 : 0 ≤ θ := by linarith
  have hr2' : r2 ≤ 1 := by linarith
  have hκ0 : κ ≠ 0 := fun h => by rw [h, abs_zero] at hκ1; linarith
  have hκm : 0 < κm := by linarith
  have hd : r2 - r1 ≠ 0 := by linarith
  have hd6 : 0 < (r2 - r1) ^ 6 := pow_pos (by linarith) 6
  have hfix := p1_prop_S7_1_iii a κ κmin κm wm w1 w2 r1 r2 T hT hκmin hκ1 hκ2 hw1 hw1' hw2 hw2' hr1 hr12 hr2'
  have hB : 0 < p1UnifB κm ρ θ := by
    unfold p1UnifB
    apply div_pos
    · have : 0 < 1 + θ := by linarith
      positivity
    · exact mul_pos (mul_pos (pow_pos (by linarith) 8) (pow_pos (by linarith) 3)) (by linarith)
  refine ⟨hB, ?_, hfix.2.2.2⟩
  have hJ := hfix.1
  set J := p1TapJac a κ T ![w1, w2, r1, r2] with hJdef
  have hlow := p1_fisher_entry_lower J hJ 0 ![1, -1, (r2 - r1) / (2 * w1), (r2 - r1) / (2 * w2)]
  have hnorm := p1_S71iii_weak_norm_uniform a κ κm wm w1 w2 r1 r2 ρ ((ρ + θ) / 2) θ ((1 + θ) / 2) T hκ2
    hw1 hw1' hw2 hw2' hr1 hr12.le hr2ρ (by linarith) (by linarith) (by linarith) (by linarith) hmar
  rw [p1_unifB_eq κm ρ θ hρθ hθ1 hθ0] at hnorm
  have hF0 : 0 ≤ (Jᵀ * J)⁻¹ 0 0 := by
    rw [← p1_fisher_col_norm J hJ 0]; exact p1_dot_self_nonneg _
  have hv : (![1, -1, (r2 - r1) / (2 * w1), (r2 - r1) / (2 * w2)] : Fin 4 → ℝ) 0 ^ 2 = 1 := by simp
  rw [hv] at hlow
  rw [div_div, div_le_iff₀ (mul_pos hB hd6)]
  calc (1 : ℝ) ≤ (Jᵀ * J)⁻¹ 0 0 * ((J *ᵥ ![1, -1, (r2 - r1) / (2 * w1), (r2 - r1) / (2 * w2)]) ⬝ᵥ
        (J *ᵥ ![1, -1, (r2 - r1) / (2 * w1), (r2 - r1) / (2 * w2)])) := hlow
    _ ≤ (Jᵀ * J)⁻¹ 0 0 * (p1UnifB κm ρ θ * (r2 - r1) ^ 6) := mul_le_mul_of_nonneg_left hnorm hF0

end CurrentMM
