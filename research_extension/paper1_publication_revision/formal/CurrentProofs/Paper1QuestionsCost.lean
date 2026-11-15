import Mathlib.Analysis.SpecificLimits.Basic
import Mathlib.Analysis.Real.Sqrt
import Mathlib.Topology.Algebra.InfiniteSum.Order
import Mathlib.Tactic.Positivity
import Mathlib.Tactic.GCongr
import Mathlib.Tactic.FieldSimp

/-!
# Paper 1: which questions prices answer cheaply (core `thm:questions`, `prop:parametric`)

Populations are finite: nodes `r i ∈ [0, r̄]`, weights `w i ≥ 0` of total at most `W̄`. The kernel taps are
`k t = ∑ w i (r i)^t` and a linear question is `F_g = ∑ w i g (r i)`.

* `p1_question_taps_identity`: `∑ w i p_c (r i) = ∑_{t<L} c t k t`, the bridge from questions to taps.
* `p1_question_weak_duality`: the modulus is at most `W̄ (R⁺ + R⁻) + ‖c‖ ‖Δk‖` for every coefficient vector `c`
  (the upper half of the dual form in part (iv)).
* `p1_question_truncation_error`: the error of the affine estimate `∑ c t k̂ t` is at most the bias
  `W̄ sup |g - p_c|` plus the noise `|∑ c t ε t|` (part (i)).
* `p1_parametric_tail`: for `g = ∑ a t r^t` with `∑ a t² ≤ A²`, the tail after `L` terms is at most
  `A r^L / √(1 - r²)`.
* `p1_parametric_modulus`: hence the modulus is at most `δ A + 2 W̄ A r̄^L / √(1 - r̄²)` (the "if" direction of
  `prop:parametric`, which gives the parametric cost with depth `L` of order `log(1/ε)`).
* `p1_geometric_energy`, `p1_long_memory_impossible`: part (iii). Without a memory bound, if `|g r| √(1 - r)` is
  unbounded near one, then for every `N` and every accuracy there is a one-group population whose taps carry
  divergence at most `1/2` from those of the empty population, while the two answers differ by more than `2ε`.
The lower half of the dual form (Sion's minimax theorem) and the converse of `prop:parametric` (weak compactness in
`ℓ²`) are not formalized.
-/

namespace CurrentMM

open Finset Filter Topology

/-- A population's first-moment identity: integrating a polynomial gives a combination of taps. -/
theorem p1_question_taps_identity {n : ℕ} (w r : Fin n → ℝ) (c : ℕ → ℝ) (L : ℕ) :
    ∑ i, w i * ∑ t ∈ range L, c t * r i ^ t = ∑ t ∈ range L, c t * ∑ i, w i * r i ^ t := by
  simp_rw [mul_sum]
  rw [sum_comm]
  exact sum_congr rfl (fun t _ => sum_congr rfl (fun i _ => by ring))

/-- Integrating a function bounded above by `H` against weights of total at most `W̄`. -/
theorem p1_weighted_upper {n : ℕ} (w r : Fin n → ℝ) (hw : ∀ i, 0 ≤ w i) (W : ℝ) (hW : ∑ i, w i ≤ W)
    (h : ℝ → ℝ) (H : ℝ) (hH : ∀ i, h (r i) ≤ H) : ∑ i, w i * h (r i) ≤ W * max H 0 := by
  calc ∑ i, w i * h (r i) ≤ ∑ i, w i * max H 0 :=
        sum_le_sum fun i _ => mul_le_mul_of_nonneg_left ((hH i).trans (le_max_left _ _)) (hw i)
    _ = (∑ i, w i) * max H 0 := by rw [sum_mul]
    _ ≤ W * max H 0 := mul_le_mul_of_nonneg_right hW (le_max_right _ _)

/-- **Weak duality (core `thm:questions`(iv), upper half).** For two populations in the class and any coefficient
vector `c`, with `h = g - p_c` bounded by `H⁺` above and `H⁻` below on the nodes,
`F_g(P₁) - F_g(P₀) ≤ W̄ (H⁺)₊ + W̄ (-H⁻)₊ + ‖c‖₂ ‖k(P₁) - k(P₀)‖₂` over the first `L` taps. -/
theorem p1_question_weak_duality {n₀ n₁ : ℕ} (w₀ r₀ : Fin n₀ → ℝ) (w₁ r₁ : Fin n₁ → ℝ)
    (hw₀ : ∀ i, 0 ≤ w₀ i) (hw₁ : ∀ i, 0 ≤ w₁ i) (W : ℝ) (hW₀ : ∑ i, w₀ i ≤ W) (hW₁ : ∑ i, w₁ i ≤ W)
    (g : ℝ → ℝ) (c : ℕ → ℝ) (L : ℕ) (Hp Hm : ℝ)
    (hp₁ : ∀ i, g (r₁ i) - ∑ t ∈ range L, c t * r₁ i ^ t ≤ Hp)
    (hm₀ : ∀ i, Hm ≤ g (r₀ i) - ∑ t ∈ range L, c t * r₀ i ^ t) :
    ∑ i, w₁ i * g (r₁ i) - ∑ i, w₀ i * g (r₀ i) ≤
      W * max Hp 0 + W * max (-Hm) 0 +
        √(∑ t ∈ range L, c t ^ 2) *
          √(∑ t ∈ range L, (∑ i, w₁ i * r₁ i ^ t - ∑ i, w₀ i * r₀ i ^ t) ^ 2) := by
  set h : ℝ → ℝ := fun x => g x - ∑ t ∈ range L, c t * x ^ t with hh
  have e₁ : ∑ i, w₁ i * g (r₁ i) = ∑ i, w₁ i * h (r₁ i) + ∑ t ∈ range L, c t * ∑ i, w₁ i * r₁ i ^ t := by
    rw [← p1_question_taps_identity, ← sum_add_distrib]
    exact sum_congr rfl (fun i _ => by simp only [hh]; ring)
  have e₀ : ∑ i, w₀ i * g (r₀ i) = ∑ i, w₀ i * h (r₀ i) + ∑ t ∈ range L, c t * ∑ i, w₀ i * r₀ i ^ t := by
    rw [← p1_question_taps_identity, ← sum_add_distrib]
    exact sum_congr rfl (fun i _ => by simp only [hh]; ring)
  have b₁ : ∑ i, w₁ i * h (r₁ i) ≤ W * max Hp 0 := p1_weighted_upper w₁ r₁ hw₁ W hW₁ h Hp hp₁
  have b₀ : -∑ i, w₀ i * h (r₀ i) ≤ W * max (-Hm) 0 := by
    have := p1_weighted_upper w₀ r₀ hw₀ W hW₀ (fun x => -h x) (-Hm) (fun i => by
      have := hm₀ i; simp only [hh] at this ⊢; linarith)
    simpa [mul_neg, sum_neg_distrib] using this
  have bc : ∑ t ∈ range L, c t * (∑ i, w₁ i * r₁ i ^ t - ∑ i, w₀ i * r₀ i ^ t) ≤
      √(∑ t ∈ range L, c t ^ 2) * √(∑ t ∈ range L, (∑ i, w₁ i * r₁ i ^ t - ∑ i, w₀ i * r₀ i ^ t) ^ 2) :=
    Real.sum_mul_le_sqrt_mul_sqrt _ _ _
  have ediff : ∑ t ∈ range L, c t * ∑ i, w₁ i * r₁ i ^ t - ∑ t ∈ range L, c t * ∑ i, w₀ i * r₀ i ^ t =
      ∑ t ∈ range L, c t * (∑ i, w₁ i * r₁ i ^ t - ∑ i, w₀ i * r₀ i ^ t) := by
    rw [← sum_sub_distrib]; exact sum_congr rfl (fun t _ => by ring)
  rw [e₁, e₀]
  linarith

/-- **The affine estimate (core `thm:questions`(i)).** If `|g - p_c| ≤ τ` on the nodes of a population of total
weight at most `W̄`, and the observed taps are `k t + ε t`, then the estimate `∑_{t<L} c t (k t + ε t)` is within
`W̄ τ + |∑ c t ε t|` of `F_g`. -/
theorem p1_question_truncation_error {n : ℕ} (w r : Fin n → ℝ) (hw : ∀ i, 0 ≤ w i) (W : ℝ)
    (hW : ∑ i, w i ≤ W) (g : ℝ → ℝ) (c ε : ℕ → ℝ) (L : ℕ) (τ : ℝ) (hτnn : 0 ≤ τ)
    (hτ : ∀ i, |g (r i) - ∑ t ∈ range L, c t * r i ^ t| ≤ τ) :
    |∑ t ∈ range L, c t * (∑ i, w i * r i ^ t + ε t) - ∑ i, w i * g (r i)| ≤
      W * τ + |∑ t ∈ range L, c t * ε t| := by
  have e : ∑ t ∈ range L, c t * (∑ i, w i * r i ^ t + ε t) - ∑ i, w i * g (r i) =
      -(∑ i, w i * (g (r i) - ∑ t ∈ range L, c t * r i ^ t)) + ∑ t ∈ range L, c t * ε t := by
    have := p1_question_taps_identity w r c L
    simp only [mul_add, sum_add_distrib, mul_sub, sum_sub_distrib]
    linarith
  rw [e]
  refine (abs_add_le _ _).trans (add_le_add ?_ le_rfl)
  rw [abs_neg]
  refine (abs_sum_le_sum_abs _ _).trans ?_
  calc ∑ i, |w i * (g (r i) - ∑ t ∈ range L, c t * r i ^ t)| ≤ ∑ i, w i * τ := by
        refine sum_le_sum fun i _ => ?_
        rw [abs_mul, abs_of_nonneg (hw i)]
        exact mul_le_mul_of_nonneg_left (hτ i) (hw i)
    _ = (∑ i, w i) * τ := by rw [sum_mul]
    _ ≤ W * τ := mul_le_mul_of_nonneg_right hW hτnn

/-! ### Square-summable coefficients: the parametric direction -/

/-- `∑_{t<T} (c r^t)² ≤ c² / (1 - r²)` for `0 ≤ r < 1`. -/
theorem p1_geometric_energy (c r : ℝ) (hr0 : 0 ≤ r) (hr1 : r < 1) (T : ℕ) :
    ∑ t ∈ range T, (c * r ^ t) ^ 2 ≤ c ^ 2 / (1 - r ^ 2) := by
  have hq0 : 0 ≤ r ^ 2 := sq_nonneg r
  have hq1 : r ^ 2 < 1 := by nlinarith
  have e : ∑ t ∈ range T, (c * r ^ t) ^ 2 = c ^ 2 * ∑ t ∈ range T, (r ^ 2) ^ t := by
    rw [mul_sum]; exact sum_congr rfl (fun t _ => by ring)
  have hg : ∑ t ∈ range T, (r ^ 2) ^ t ≤ (1 - r ^ 2)⁻¹ := by
    have hm := geom_sum_mul (r ^ 2) T
    have hpT : 0 ≤ (r ^ 2) ^ T := pow_nonneg hq0 T
    rw [inv_eq_one_div, le_div_iff₀ (by linarith)]
    nlinarith [hm, hpT]
  rw [e, div_eq_mul_inv]
  exact mul_le_mul_of_nonneg_left hg (sq_nonneg c)

/-- **The tail of a square-summable power series.** If `∑_{t<M} a t² ≤ A²` for every `M` and
`∑ a t r^t = g` with `0 ≤ r < 1`, then `|g - ∑_{t<L} a t r^t| ≤ A r^L / √(1 - r²)`. -/
theorem p1_parametric_tail (a : ℕ → ℝ) (A : ℝ) (hA0 : 0 ≤ A) (hA : ∀ M, ∑ t ∈ range M, a t ^ 2 ≤ A ^ 2)
    (r : ℝ) (hr0 : 0 ≤ r) (hr1 : r < 1) (gr : ℝ) (hg : HasSum (fun t => a t * r ^ t) gr) (L : ℕ) :
    |gr - ∑ t ∈ range L, a t * r ^ t| ≤ A * r ^ L / √(1 - r ^ 2) := by
  have hq : 0 < 1 - r ^ 2 := by nlinarith
  have hpart : ∀ M, L ≤ M → |∑ t ∈ range M, a t * r ^ t - ∑ t ∈ range L, a t * r ^ t| ≤
      A * r ^ L / √(1 - r ^ 2) := by
    intro M hM
    have e : ∑ t ∈ range M, a t * r ^ t - ∑ t ∈ range L, a t * r ^ t = ∑ t ∈ Ico L M, a t * r ^ t := by
      rw [← sum_range_add_sum_Ico _ hM]; ring
    rw [e]
    have hcs := Real.sum_mul_le_sqrt_mul_sqrt (Ico L M) (fun t => |a t|) (fun t => r ^ t)
    have h1 : |∑ t ∈ Ico L M, a t * r ^ t| ≤ ∑ t ∈ Ico L M, |a t| * r ^ t := by
      refine (abs_sum_le_sum_abs _ _).trans (le_of_eq (sum_congr rfl fun t _ => ?_))
      rw [abs_mul, abs_of_nonneg (pow_nonneg hr0 t)]
    have h2 : ∑ t ∈ Ico L M, |a t| ^ 2 ≤ A ^ 2 := by
      calc ∑ t ∈ Ico L M, |a t| ^ 2 = ∑ t ∈ Ico L M, a t ^ 2 := by simp [sq_abs]
        _ ≤ ∑ t ∈ range M, a t ^ 2 := by
            refine sum_le_sum_of_subset_of_nonneg (fun t ht => ?_) (fun _ _ _ => sq_nonneg _)
            exact mem_range.mpr (mem_Ico.mp ht).2
        _ ≤ A ^ 2 := hA M
    have h3 : ∑ t ∈ Ico L M, (r ^ t) ^ 2 ≤ (r ^ L) ^ 2 / (1 - r ^ 2) := by
      have e3 : ∑ t ∈ Ico L M, (r ^ t) ^ 2 = ∑ u ∈ range (M - L), (r ^ L * r ^ u) ^ 2 := by
        rw [sum_Ico_eq_sum_range]
        exact sum_congr rfl (fun u _ => by rw [pow_add])
      rw [e3]
      exact p1_geometric_energy (r ^ L) r hr0 hr1 (M - L)
    calc |∑ t ∈ Ico L M, a t * r ^ t| ≤ ∑ t ∈ Ico L M, |a t| * r ^ t := h1
      _ ≤ √(∑ t ∈ Ico L M, |a t| ^ 2) * √(∑ t ∈ Ico L M, (r ^ t) ^ 2) := hcs
      _ ≤ √(A ^ 2) * √((r ^ L) ^ 2 / (1 - r ^ 2)) := by gcongr
      _ = A * r ^ L / √(1 - r ^ 2) := by
          rw [Real.sqrt_sq hA0, Real.sqrt_div' _ hq.le, Real.sqrt_sq (pow_nonneg hr0 L)]
          ring
  have hlim : Tendsto (fun M => |∑ t ∈ range M, a t * r ^ t - ∑ t ∈ range L, a t * r ^ t|) atTop
      (𝓝 |gr - ∑ t ∈ range L, a t * r ^ t|) :=
    ((hg.tendsto_sum_nat).sub_const _).abs
  exact le_of_tendsto hlim (eventually_atTop.mpr ⟨L, hpart⟩)

/-- **The parametric direction of core `prop:parametric`.** If `g = ∑ a t r^t` on `[0, r̄]` with
`∑ a t² ≤ A²`, then for any two populations in the class whose first `L` taps differ by at most `δ` in `ℓ²`,
the answers differ by at most `δ A + 2 W̄ A r̄^L / √(1 - r̄²)`. Choosing `L` of order `log(1/δ) / log(1/r̄)` makes
this `O(δ)`, the parametric modulus, whatever the number of groups and the spacing of their memories. -/
theorem p1_parametric_modulus (a : ℕ → ℝ) (A : ℝ) (hA0 : 0 ≤ A) (hA : ∀ M, ∑ t ∈ range M, a t ^ 2 ≤ A ^ 2)
    (rbar : ℝ) (hrb0 : 0 ≤ rbar) (hrb1 : rbar < 1) (g : ℝ → ℝ)
    (hg : ∀ x, 0 ≤ x → x ≤ rbar → HasSum (fun t => a t * x ^ t) (g x))
    {n₀ n₁ : ℕ} (w₀ r₀ : Fin n₀ → ℝ) (w₁ r₁ : Fin n₁ → ℝ)
    (hw₀ : ∀ i, 0 ≤ w₀ i) (hw₁ : ∀ i, 0 ≤ w₁ i) (W : ℝ) (hWnn : 0 ≤ W) (hW₀ : ∑ i, w₀ i ≤ W)
    (hW₁ : ∑ i, w₁ i ≤ W) (hr₀ : ∀ i, 0 ≤ r₀ i ∧ r₀ i ≤ rbar) (hr₁ : ∀ i, 0 ≤ r₁ i ∧ r₁ i ≤ rbar) (L : ℕ) (δ : ℝ)
    (hδ : √(∑ t ∈ range L, (∑ i, w₁ i * r₁ i ^ t - ∑ i, w₀ i * r₀ i ^ t) ^ 2) ≤ δ) :
    ∑ i, w₁ i * g (r₁ i) - ∑ i, w₀ i * g (r₀ i) ≤ δ * A + 2 * W * (A * rbar ^ L / √(1 - rbar ^ 2)) := by
  set B : ℝ := A * rbar ^ L / √(1 - rbar ^ 2) with hB
  have hqb : 0 < 1 - rbar ^ 2 := by nlinarith
  have hB0 : 0 ≤ B := by positivity
  have htail : ∀ x, 0 ≤ x → x ≤ rbar → |g x - ∑ t ∈ range L, a t * x ^ t| ≤ B := by
    intro x hx0 hx1
    refine (p1_parametric_tail a A hA0 hA x hx0 (hx1.trans_lt hrb1) (g x) (hg x hx0 hx1) L).trans ?_
    have hq : 0 < 1 - x ^ 2 := by nlinarith
    have hsq : √(1 - rbar ^ 2) ≤ √(1 - x ^ 2) := Real.sqrt_le_sqrt (by nlinarith)
    calc A * x ^ L / √(1 - x ^ 2) ≤ A * rbar ^ L / √(1 - x ^ 2) := by gcongr
      _ ≤ A * rbar ^ L / √(1 - rbar ^ 2) := by
          apply div_le_div_of_nonneg_left (by positivity) (Real.sqrt_pos.mpr hqb) hsq
  have hd := p1_question_weak_duality w₀ r₀ w₁ r₁ hw₀ hw₁ W hW₀ hW₁ g a L B (-B)
    (fun i => (le_abs_self _).trans (htail _ (hr₁ i).1 (hr₁ i).2))
    (fun i => by have := htail _ (hr₀ i).1 (hr₀ i).2; rw [abs_le] at this; linarith [this.1])
  have hcA : √(∑ t ∈ range L, a t ^ 2) ≤ A := by
    calc √(∑ t ∈ range L, a t ^ 2) ≤ √(A ^ 2) := Real.sqrt_le_sqrt (hA L)
      _ = A := Real.sqrt_sq hA0
  have hmax1 : max B 0 = B := max_eq_left hB0
  have hmax2 : max (- -B) 0 = B := by rw [neg_neg]; exact max_eq_left hB0
  rw [hmax1, hmax2] at hd
  have hprod : √(∑ t ∈ range L, a t ^ 2) *
      √(∑ t ∈ range L, (∑ i, w₁ i * r₁ i ^ t - ∑ i, w₀ i * r₀ i ^ t) ^ 2) ≤ A * δ :=
    mul_le_mul hcA hδ (Real.sqrt_nonneg _) hA0
  linarith

/-! ### Long memory -/

/-- **Long memory makes some questions impossible (core `thm:questions`(iii)).** Suppose `|g r| √(1 - r)` is
unbounded near one: for every `B` and every `ρ < 1` some `r ∈ (ρ, 1)` has `B < |g r| √(1 - r)`. Then for every
number `N` of experiments, every noise level `σ`, every weight bound `W̄ > 0` and every accuracy `ε`, there is a
one-group population of weight `c ∈ (0, W̄]` at some memory `r ∈ [0, 1)` such that its taps carry Gaussian
divergence `N ∑_t (c r^t)² / (2σ²) ≤ 1/2` from those of the empty population at every horizon, while the two answers
differ by more than `2ε`. By Pinsker's inequality the two data laws are then within total variation `1/2`, so no
procedure certifies `F_g` to accuracy `ε` at a level above `3/4`. -/
theorem p1_long_memory_impossible (g : ℝ → ℝ)
    (hunb : ∀ B ρ : ℝ, ρ < 1 → ∃ r, ρ < r ∧ r < 1 ∧ B < |g r| * √(1 - r))
    (N : ℕ) (hN : 0 < N) (σ : ℝ) (hσ : 0 < σ) (W : ℝ) (hW : 0 < W) (ε : ℝ) :
    ∃ r c : ℝ, 0 ≤ r ∧ r < 1 ∧ 0 < c ∧ c ≤ W ∧
      (∀ T, (N : ℝ) * (∑ t ∈ range T, (c * r ^ t) ^ 2) / (2 * σ ^ 2) ≤ 1 / 2) ∧
      2 * ε < |c * g r - 0| := by
  have hNr : (0 : ℝ) < N := by exact_mod_cast hN
  set ρ : ℝ := max 0 (1 - W ^ 2 * N / (2 * σ ^ 2)) with hρ
  have hpos : 0 < W ^ 2 * N / (2 * σ ^ 2) := by positivity
  have hρ1 : ρ < 1 := max_lt one_pos (by linarith)
  obtain ⟨r, hρr, hr1, hB⟩ := hunb (2 * |ε| * √N / σ) ρ hρ1
  have hr0 : 0 ≤ r := (le_max_left _ _).trans hρr.le
  have hq : 0 < 1 - r ^ 2 := by nlinarith
  set c : ℝ := σ * √((1 - r ^ 2) / N) with hc
  have hc0 : 0 < c := by
    have : 0 < (1 - r ^ 2) / N := div_pos hq hNr
    positivity
  have hcsq : c ^ 2 = σ ^ 2 * (1 - r ^ 2) / N := by
    rw [hc, mul_pow, Real.sq_sqrt (div_pos hq hNr).le]
    ring
  refine ⟨r, c, hr0, hr1, hc0, ?_, ?_, ?_⟩
  · -- c ≤ W because 1 - r² ≤ 2 (1 - r) < W² N / σ²
    have h1 : 1 - W ^ 2 * N / (2 * σ ^ 2) < r := lt_of_le_of_lt (le_max_right _ _) hρr
    have h2 : 1 - r ^ 2 ≤ 2 * (1 - r) := by nlinarith
    have h3 : c ^ 2 ≤ W ^ 2 := by
      rw [hcsq, div_le_iff₀ hNr]
      have : 2 * (1 - r) < W ^ 2 * N / σ ^ 2 := by
        have := h1
        rw [sub_lt_iff_lt_add] at this
        have e : W ^ 2 * N / (2 * σ ^ 2) * 2 = W ^ 2 * N / σ ^ 2 := by field_simp
        nlinarith
      have hσ2 : 0 < σ ^ 2 := by positivity
      rw [lt_div_iff₀ hσ2] at this
      nlinarith
    nlinarith [h3, hc0, hW]
  · intro T
    have hE := p1_geometric_energy c r hr0 hr1 T
    have hσ2 : 0 < 2 * σ ^ 2 := by positivity
    calc (N : ℝ) * (∑ t ∈ range T, (c * r ^ t) ^ 2) / (2 * σ ^ 2)
        ≤ (N : ℝ) * (c ^ 2 / (1 - r ^ 2)) / (2 * σ ^ 2) := by gcongr
      _ = 1 / 2 := by rw [hcsq]; field_simp
  · rw [sub_zero, abs_mul, abs_of_pos hc0]
    -- c ≥ σ √((1 - r)/N), so c |g r| ≥ (σ / √N) |g r| √(1 - r) > (σ / √N) (2 |ε| √N / σ) = 2 |ε|
    have hsN : 0 < √(N : ℝ) := Real.sqrt_pos.mpr hNr
    have hc_ge : σ / √N * √(1 - r) ≤ c := by
      rw [hc, Real.sqrt_div' _ hNr.le]
      have : √(1 - r) ≤ √(1 - r ^ 2) := Real.sqrt_le_sqrt (by nlinarith)
      calc σ / √N * √(1 - r) = σ * (√(1 - r) / √N) := by ring
        _ ≤ σ * (√(1 - r ^ 2) / √N) := by gcongr
    have hpos : 0 < σ / √N := div_pos hσ hsN
    have key : σ / √N * (2 * |ε| * √N / σ) < σ / √N * (|g r| * √(1 - r)) :=
      mul_lt_mul_of_pos_left hB hpos
    have e : σ / √N * (2 * |ε| * √N / σ) = 2 * |ε| := by field_simp
    rw [e] at key
    calc 2 * ε ≤ 2 * |ε| := by linarith [le_abs_self ε]
      _ < σ / √N * (|g r| * √(1 - r)) := key
      _ = (σ / √N * √(1 - r)) * |g r| := by ring
      _ ≤ c * |g r| := mul_le_mul_of_nonneg_right hc_ge (abs_nonneg _)

end CurrentMM
