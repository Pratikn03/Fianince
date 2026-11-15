import Mathlib.Algebra.BigOperators.Fin
import Mathlib.Algebra.Order.BigOperators.Group.Finset
import Mathlib.Data.Real.Basic
import Mathlib.Tactic.Ring
import Mathlib.Tactic.Linarith
import Mathlib.Tactic.Push
import Mathlib.Tactic.FieldSimp
import Mathlib.Tactic.Positivity
import Mathlib.Tactic.GCongr
import Mathlib.Algebra.Order.Field.Basic

/-!
# Paper 1, Theorem 5.4: from the price response to kernel values

`deconv a κ h` solves the closed-loop recursion `h_{t+1} = a h_t + κ ∑_{j ≤ t} k_j h_{t-j}` for the kernel values,
using the known first tap `h_0 = κ` (the only division is by `κ²`).

* `p1_deconv_true`: applied to a true response it returns the true kernel;
* `p1_response_bound`: responses whose kernel is bounded by `A` are bounded on any finite horizon, with a constant
  that depends only on `(a, κ, A)` and the horizon;
* `p1_deconv_perturb`: on a finite horizon, deconvolution is Lipschitz around any response with bounded taps and
  kernel, with a constant that depends only on `(a, κ, A, B)` and the horizon — not on the rate spacing.
-/

namespace CurrentMM

open Finset

/-- Kernel values recovered from a response by the closed-loop recursion with `h_0 = κ` known. -/
noncomputable def deconv (a κ : ℝ) (h : ℕ → ℝ) : ℕ → ℝ
  | t => (h (t + 1) - a * h t - κ * ∑ j : Fin t, deconv a κ h j * h (t - j)) / κ ^ 2
termination_by t => t
decreasing_by exact j.isLt

theorem p1_deconv_eq (a κ : ℝ) (h : ℕ → ℝ) (t : ℕ) :
    deconv a κ h t = (h (t + 1) - a * h t - κ * ∑ j ∈ range t, deconv a κ h j * h (t - j)) / κ ^ 2 := by
  rw [deconv, Fin.sum_univ_eq_sum_range (fun j => deconv a κ h j * h (t - j)) t]

/-- **Deconvolution returns the true kernel.** -/
theorem p1_deconv_true (a κ : ℝ) (hκ : κ ≠ 0) (k h : ℕ → ℝ) (h0 : h 0 = κ)
    (hrec : ∀ t, h (t + 1) = a * h t + κ * ∑ j ∈ range (t + 1), k j * h (t - j)) :
    ∀ t, deconv a κ h t = k t := by
  intro t
  induction t using Nat.strong_induction_on with
  | _ t ih =>
    have hs : ∑ j ∈ range t, deconv a κ h j * h (t - j) = ∑ j ∈ range t, k j * h (t - j) :=
      sum_congr rfl (fun j hj => by rw [ih j (mem_range.mp hj)])
    rw [p1_deconv_eq, hs, hrec t, sum_range_succ, Nat.sub_self, h0]
    field_simp
    ring

/-- **Responses are bounded on a finite horizon.** -/
theorem p1_response_bound (a κ A : ℝ) (hA : 0 ≤ A) (n : ℕ) :
    ∃ B ≥ 0, ∀ (k h : ℕ → ℝ), h 0 = κ →
      (∀ t, h (t + 1) = a * h t + κ * ∑ j ∈ range (t + 1), k j * h (t - j)) →
      (∀ j, |k j| ≤ A) → ∀ t ≤ n, |h t| ≤ B := by
  induction n with
  | zero =>
    refine ⟨|κ|, abs_nonneg _, fun k h h0 _ _ t ht => ?_⟩
    rw [Nat.le_zero.mp ht, h0]
  | succ n ih =>
    obtain ⟨B, hB0, hB⟩ := ih
    refine ⟨max B (|a| * B + |κ| * ((n + 1) * (A * B))), le_max_of_le_left hB0,
      fun k h h0 hrec hk t ht => ?_⟩
    rcases Nat.lt_or_ge t (n + 1) with htn | htn
    · exact (hB k h h0 hrec hk t (by omega)).trans (le_max_left _ _)
    · have htn' : t = n + 1 := by omega
      subst htn'
      refine le_trans ?_ (le_max_right _ _)
      rw [hrec n]
      have hsum : |∑ j ∈ range (n + 1), k j * h (n - j)| ≤ (n + 1) * (A * B) := by
        refine (abs_sum_le_sum_abs _ _).trans ?_
        calc ∑ j ∈ range (n + 1), |k j * h (n - j)| ≤ ∑ j ∈ range (n + 1), A * B := by
              refine sum_le_sum (fun j _ => ?_)
              rw [abs_mul]
              exact mul_le_mul (hk j) (hB k h h0 hrec hk _ (by omega)) (abs_nonneg _) hA
          _ = (n + 1) * (A * B) := by rw [sum_const, card_range, nsmul_eq_mul]; push_cast; ring
      calc |a * h n + κ * ∑ j ∈ range (n + 1), k j * h (n - j)|
          ≤ |a| * |h n| + |κ| * |∑ j ∈ range (n + 1), k j * h (n - j)| := by
            refine (abs_add_le _ _).trans ?_; rw [abs_mul, abs_mul]
        _ ≤ |a| * B + |κ| * ((n + 1) * (A * B)) := by
            gcongr
            exact hB k h h0 hrec hk n le_rfl

/-- **Deconvolution is Lipschitz on a finite horizon**, with a constant free of the rate spacing. If `h'` is
within `e ≤ 1` of `h` at every tap up to `T`, the taps of `h` are bounded by `B` and its kernel by `A`, then the
kernel values below `T` move by at most `C e`. -/
theorem p1_deconv_perturb (a κ A B : ℝ) (hκ : κ ≠ 0) (hA : 0 ≤ A) (hB : 0 ≤ B) (T : ℕ) (n : ℕ) :
    ∃ C ≥ 0, ∀ (h h' : ℕ → ℝ) (e : ℝ), 0 ≤ e → e ≤ 1 →
      (∀ t ≤ T, |h' t - h t| ≤ e) → (∀ t ≤ T, |h t| ≤ B) → (∀ t < T, |deconv a κ h t| ≤ A) →
      ∀ t < n, t < T → |deconv a κ h' t - deconv a κ h t| ≤ C * e := by
  induction n with
  | zero => exact ⟨0, le_rfl, fun _ _ _ _ _ _ _ _ t ht => absurd ht (Nat.not_lt_zero _)⟩
  | succ n ih =>
    obtain ⟨C, hC0, hC⟩ := ih
    set D := (1 + |a| + |κ| * (n * (C * (B + 1) + A))) / κ ^ 2 with hD
    have hκ2 : 0 < κ ^ 2 := by positivity
    have hD0 : 0 ≤ D := by positivity
    refine ⟨max C D, le_max_of_le_left hC0, fun h h' e he0 he1 hclose hbnd hk t ht htT => ?_⟩
    rcases Nat.lt_or_ge t n with htn | htn
    · exact (hC h h' e he0 he1 hclose hbnd hk t htn htT).trans
        (mul_le_mul_of_nonneg_right (le_max_left _ _) he0)
    · have htn' : t = n := by omega
      subst htn'
      refine le_trans ?_ (mul_le_mul_of_nonneg_right (le_max_right _ _) he0)
      rw [p1_deconv_eq, p1_deconv_eq]
      have hterm : ∀ j ∈ range t, |deconv a κ h' j * h' (t - j) - deconv a κ h j * h (t - j)| ≤
          (C * (B + 1) + A) * e := by
        intro j hj
        have hjt := mem_range.mp hj
        have hkj := hC h h' e he0 he1 hclose hbnd hk j hjt (by omega)
        have hhj := hclose (t - j) (by omega)
        have hhb := hbnd (t - j) (by omega)
        have hh'b : |h' (t - j)| ≤ B + 1 := by
          calc |h' (t - j)| = |(h' (t - j) - h (t - j)) + h (t - j)| := by ring_nf
            _ ≤ |h' (t - j) - h (t - j)| + |h (t - j)| := abs_add_le _ _
            _ ≤ 1 + B := add_le_add (hhj.trans he1) hhb
            _ = B + 1 := by ring
        have e1 : deconv a κ h' j * h' (t - j) - deconv a κ h j * h (t - j) =
            (deconv a κ h' j - deconv a κ h j) * h' (t - j) +
              deconv a κ h j * (h' (t - j) - h (t - j)) := by ring
        rw [e1]
        calc |(deconv a κ h' j - deconv a κ h j) * h' (t - j) + deconv a κ h j * (h' (t - j) - h (t - j))|
            ≤ |deconv a κ h' j - deconv a κ h j| * |h' (t - j)| +
                |deconv a κ h j| * |h' (t - j) - h (t - j)| := by
              refine (abs_add_le _ _).trans ?_; rw [abs_mul, abs_mul]
          _ ≤ (C * e) * (B + 1) + A * e := by
              gcongr
              · exact hk j (by omega)
          _ = (C * (B + 1) + A) * e := by ring
      have hsum : |∑ j ∈ range t, deconv a κ h' j * h' (t - j) - ∑ j ∈ range t, deconv a κ h j * h (t - j)|
          ≤ t * ((C * (B + 1) + A) * e) := by
        rw [← sum_sub_distrib]
        refine (abs_sum_le_sum_abs _ _).trans ?_
        refine (sum_le_sum hterm).trans ?_
        rw [sum_const, card_range, nsmul_eq_mul]
      have hnum : |(h' (t + 1) - a * h' t - κ * ∑ j ∈ range t, deconv a κ h' j * h' (t - j)) -
          (h (t + 1) - a * h t - κ * ∑ j ∈ range t, deconv a κ h j * h (t - j))| ≤
          (1 + |a| + |κ| * (t * (C * (B + 1) + A))) * e := by
        have e2 : (h' (t + 1) - a * h' t - κ * ∑ j ∈ range t, deconv a κ h' j * h' (t - j)) -
            (h (t + 1) - a * h t - κ * ∑ j ∈ range t, deconv a κ h j * h (t - j)) =
            (h' (t + 1) - h (t + 1)) - a * (h' t - h t) -
              κ * (∑ j ∈ range t, deconv a κ h' j * h' (t - j) -
                ∑ j ∈ range t, deconv a κ h j * h (t - j)) := by ring
        rw [e2]
        have h1 := hclose (t + 1) (by omega)
        have h2 := hclose t (by omega)
        calc |(h' (t + 1) - h (t + 1)) - a * (h' t - h t) -
              κ * (∑ j ∈ range t, deconv a κ h' j * h' (t - j) - ∑ j ∈ range t, deconv a κ h j * h (t - j))|
            ≤ |h' (t + 1) - h (t + 1)| + |a| * |h' t - h t| +
                |κ| * |∑ j ∈ range t, deconv a κ h' j * h' (t - j) -
                  ∑ j ∈ range t, deconv a κ h j * h (t - j)| := by
              refine (abs_sub _ _).trans ?_
              refine add_le_add ((abs_sub _ _).trans ?_) (by rw [abs_mul])
              rw [abs_mul]
          _ ≤ e + |a| * e + |κ| * (t * ((C * (B + 1) + A) * e)) := by gcongr
          _ = (1 + |a| + |κ| * (t * (C * (B + 1) + A))) * e := by ring
      rw [← sub_div, abs_div, abs_of_pos hκ2, div_le_iff₀ hκ2]
      calc _ ≤ (1 + |a| + |κ| * (t * (C * (B + 1) + A))) * e := hnum
        _ = D * e * κ ^ 2 := by rw [hD]; field_simp

end CurrentMM
