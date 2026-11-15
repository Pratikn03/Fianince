import Mathlib.Algebra.BigOperators.Fin
import Mathlib.Basic.Real.Basic
import Mathlib.Tactic.Linarith
import Mathlib.Tactic.Ring
import Mathlib.Tactic.FieldSimp

/-!
# Paper 1: partial disclosure (algebraic steps)

The partial-disclosure theorem (core `thm:partial`) says that when `m` of `K` groups are tagged, the cost of
composition is that of the `K' = K - m` untagged groups alone. These are its algebraic steps.

* `p1_partial_kernel_gap`: if the tagged groups are the same in two economies, the kernel gap is the gap of the
  untagged groups alone, at every lag.
* `p1_partial_residual_kernel`: subtracting the tagged groups' contribution from the kernel leaves exactly the
  untagged groups' kernel.
* `p1_partial_single_untagged`: with one untagged group, its weight and rate are read off the first two kernel
  values once the tagged groups are known: no separation, no `Δη`.
* `p1_partial_exponent_step`: removing one untagged group lowers the exponent `4K' - 2` by exactly 4.
-/

namespace CurrentMM

open Finset

/-- Kernel of a finite population: `k m = Σ_i w_i r_i^m`. -/
def popKernel {n : ℕ} (w r : Fin n → ℝ) (m : ℕ) : ℝ := ∑ i, w i * r i ^ m

/-- Same tagged groups: the kernel gap equals the untagged groups' gap, at every lag. -/
theorem p1_partial_kernel_gap {p q : ℕ} (wt rt : Fin p → ℝ) (wu ru wu' ru' : Fin q → ℝ) (m : ℕ) :
    (popKernel wt rt m + popKernel wu ru m) - (popKernel wt rt m + popKernel wu' ru' m) =
      popKernel wu ru m - popKernel wu' ru' m := by
  ring

/-- Subtracting the tagged contribution leaves the untagged kernel. -/
theorem p1_partial_residual_kernel {p q : ℕ} (wt rt : Fin p → ℝ) (wu ru : Fin q → ℝ) (k : ℕ → ℝ)
    (hk : ∀ m, k m = popKernel wt rt m + popKernel wu ru m) (m : ℕ) :
    k m - popKernel wt rt m = popKernel wu ru m := by
  rw [hk m]; ring

/-- One untagged group: its weight and rate are determined by the first two kernel values and the tagged groups. -/
theorem p1_partial_single_untagged {p : ℕ} (wt rt : Fin p → ℝ) (v s : ℝ) (k : ℕ → ℝ)
    (hk : ∀ m, k m = popKernel wt rt m + v * s ^ m) (hv : v ≠ 0) :
    v = k 0 - ∑ i, wt i ∧ s = (k 1 - ∑ i, wt i * rt i) / v := by
  have h0 := hk 0
  have h1 := hk 1
  simp only [popKernel, pow_zero, mul_one, pow_one] at h0 h1
  constructor
  · linarith
  · field_simp
    linarith

/-- Each untagged group removed lowers the exponent `4K' - 2` by four. -/
theorem p1_partial_exponent_step (K' : ℕ) (h : 2 ≤ K') :
    ((4 * K' - 2 : ℕ) : ℤ) - ((4 * (K' - 1) - 2 : ℕ) : ℤ) = 4 := by
  omega

end CurrentMM
