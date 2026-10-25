import Mathlib.Algebra.Order.BigOperators.Group.Finset
import Mathlib.Algebra.Order.BigOperators.Ring.Finset
import Mathlib.Basic.Real.Basic
import Mathlib.Tactic.Linarith
import Mathlib.Tactic.Ring
import Mathlib.Tactic.Positivity
import Mathlib.Tactic.FieldSimp

/-!
# Hidden slow feedback and the absolute-response certificate (thesis, Theorems `thm:hidden`, `thm:absresp`)

* `thesis_hidden_cs`: for `0 ≤ r ≤ 1`, `(∑_{m<n} r^m x_m)^2 ≤ n ∑_{m<n} x_m^2` (Cauchy--Schwarz step of `thm:hidden`).
* `thesis_hidden_kl`: `K ∑_{j<T} (j+1)^2 ≤ K T^3` for `K ≥ 0` (the divergence bound `(c+μ)^2 (1-r)^2 T^3 / (2c)`).
* `thesis_hidden_record`: if `2 (1-2α)^2 ≤ K T^3` with `K > 0`, then `2 (1-2α)^2 / K ≤ T^3` (the record-length bound).
* `thesis_hidden_unsafe_margin`: with `κ q₁ = c + μ`, the margin `c - κ q₁` equals `-μ`.
* `thesis_absresp_mono`: for `0 ≤ ρ < ρ'` and `H ≥ 2`, `∑_{j<H} ρ^j < ∑_{j<H} ρ'^j` (the absolute response of the
  memory-zero economy is strictly increasing, which gives the two-point lower bound of `thm:absresp`).
-/

namespace CurrentMM

open scoped BigOperators

theorem thesis_hidden_cs (n : ℕ) (r : ℝ) (x : ℕ → ℝ) (h0 : 0 ≤ r) (h1 : r ≤ 1) :
    (∑ m ∈ Finset.range n, r ^ m * x m) ^ 2 ≤ n * ∑ m ∈ Finset.range n, x m ^ 2 := by
  have cs := Finset.sum_mul_sq_le_sq_mul_sq (Finset.range n) (fun m => r ^ m) x
  have hr : ∑ m ∈ Finset.range n, (r ^ m) ^ 2 ≤ n := by
    have : ∀ m ∈ Finset.range n, (r ^ m) ^ 2 ≤ 1 := by
      intro m _
      have hp : r ^ m ≤ 1 := pow_le_one₀ h0 h1
      have hp0 : 0 ≤ r ^ m := pow_nonneg h0 m
      nlinarith
    calc ∑ m ∈ Finset.range n, (r ^ m) ^ 2 ≤ ∑ m ∈ Finset.range n, (1 : ℝ) := Finset.sum_le_sum this
      _ = n := by simp
  have hx : 0 ≤ ∑ m ∈ Finset.range n, x m ^ 2 := Finset.sum_nonneg (fun m _ => sq_nonneg (x m))
  calc (∑ m ∈ Finset.range n, r ^ m * x m) ^ 2
      ≤ (∑ m ∈ Finset.range n, (r ^ m) ^ 2) * ∑ m ∈ Finset.range n, x m ^ 2 := cs
    _ ≤ n * ∑ m ∈ Finset.range n, x m ^ 2 := mul_le_mul_of_nonneg_right hr hx

theorem thesis_hidden_kl (K : ℝ) (T : ℕ) (hK : 0 ≤ K) :
    K * ∑ j ∈ Finset.range T, ((j : ℝ) + 1) ^ 2 ≤ K * (T : ℝ) ^ 3 := by
  have h : ∑ j ∈ Finset.range T, ((j : ℝ) + 1) ^ 2 ≤ (T : ℝ) ^ 3 := by
    have hj : ∀ j ∈ Finset.range T, ((j : ℝ) + 1) ^ 2 ≤ (T : ℝ) ^ 2 := by
      intro j hj
      have hjT : (j : ℝ) + 1 ≤ T := by exact_mod_cast Finset.mem_range.mp hj
      have hj0 : (0 : ℝ) ≤ (j : ℝ) + 1 := by positivity
      nlinarith
    calc ∑ j ∈ Finset.range T, ((j : ℝ) + 1) ^ 2 ≤ ∑ j ∈ Finset.range T, (T : ℝ) ^ 2 := Finset.sum_le_sum hj
      _ = (T : ℝ) ^ 3 := by rw [Finset.sum_const, Finset.card_range, nsmul_eq_mul]; ring
  exact mul_le_mul_of_nonneg_left h hK

theorem thesis_hidden_record (α K T3 : ℝ) (hK : 0 < K) (h : 2 * (1 - 2 * α) ^ 2 ≤ K * T3) :
    2 * (1 - 2 * α) ^ 2 / K ≤ T3 := by
  rw [div_le_iff₀ hK]; linarith

theorem thesis_hidden_unsafe_margin (c μ κq : ℝ) (h : κq = c + μ) : c - κq = -μ := by
  rw [h]; ring

theorem thesis_absresp_mono (H : ℕ) (hH : 2 ≤ H) (ρ ρ' : ℝ) (h0 : 0 ≤ ρ) (h1 : ρ < ρ') :
    ∑ j ∈ Finset.range H, ρ ^ j < ∑ j ∈ Finset.range H, ρ' ^ j := by
  have hle : ∀ j ∈ Finset.range H, ρ ^ j ≤ ρ' ^ j := fun j _ => pow_le_pow_left₀ h0 h1.le j
  have hlt : ρ ^ 1 < ρ' ^ 1 := by simpa using h1
  exact Finset.sum_lt_sum hle ⟨1, Finset.mem_range.mpr (by omega), hlt⟩

end CurrentMM
