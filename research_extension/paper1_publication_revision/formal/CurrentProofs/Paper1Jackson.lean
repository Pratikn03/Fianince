import Mathlib.Analysis.SpecialFunctions.Trigonometric.Chebyshev.Basic
import Mathlib.Analysis.SpecialFunctions.Trigonometric.Bounds
import Mathlib.Analysis.SpecialFunctions.Complex.Log
import Mathlib.Algebra.Order.BigOperators.Ring.Finset
import Mathlib.Algebra.BigOperators.Field

/-!
# A Jackson-type theorem with explicit constants, by a discrete Fejér–Korovkin operator

Mathlib has no Jackson theorem. For Theorem 5.6 (ii) we need: every `L`-Lipschitz `g` on `[-1, 1]` is within
`L π / (n + 2)` of a polynomial of degree at most `n`, with control of the polynomial's coefficients.
The proof uses only finite sums:

* `p1_node_cos_sum`: on `M` equally spaced nodes `t_j = 2πj/M`, `∑_j cos(d(θ - t_j)) = M [d = 0]` for `|d| < M`
  (a geometric sum of roots of unity);
* `fkKer`: the Fejér–Korovkin kernel `K(u) = |∑_{k ≤ n} a_k e^{iku}|² / ∑ a_k²`, `a_k = sin(π(k+1)/(n+2))`, which is
  nonnegative (`p1_fkKer_nonneg`), has node mean `1` (`p1_fkKer_node_sum`) and node mean of `K(u)(1 - cos u)` equal
  to `1 - cos(π/(n+2)) ≤ π²/(2(n+2)²)` (`p1_fkKer_node_moment`, from the recurrence of the sines);
* `jop`: the positive operator `g ↦ (1/M) ∑_j g(cos t_j) (K(θ - t_j) + K(θ + t_j))/2`, `M = n + 2`;
  `p1_jop_error`: `|jop g θ - g(cos θ)| ≤ L π/(n+2)` (Cauchy–Schwarz on the nodes);
* `jpoly`: the same operator written as a combination of Chebyshev polynomials `T_{k-l}`, so a polynomial of degree
  `≤ n` with `jpoly.eval (cos θ) = jop g θ` (`p1_jpoly_eval_cos`, `p1_jpoly_natDegree`), and
  `p1_jackson`: `|jpoly.eval x - g x| ≤ L π/(n+2)` on `[-1, 1]`.
-/

namespace CurrentMM

open Finset Real Polynomial

/-! ### Quadrature on equally spaced nodes -/

theorem p1_sum_cos_arith (α β : ℝ) (M : ℕ) (hβ : Complex.exp ((β : ℂ) * Complex.I) ≠ 1)
    (hM : Complex.exp ((β : ℂ) * Complex.I) ^ M = 1) :
    ∑ j ∈ range M, cos (α + j * β) = 0 := by
  have h : ∑ j ∈ range M, Complex.exp (((α + j * β : ℝ) : ℂ) * Complex.I) = 0 := by
    have e : ∀ j : ℕ, Complex.exp (((α + j * β : ℝ) : ℂ) * Complex.I) =
        Complex.exp ((α : ℂ) * Complex.I) * Complex.exp ((β : ℂ) * Complex.I) ^ j := by
      intro j
      rw [← Complex.exp_nat_mul, ← Complex.exp_add]
      congr 1; push_cast; ring
    simp_rw [e, ← mul_sum, geom_sum_eq hβ, hM, sub_self, zero_div, mul_zero]
  have h2 := congrArg Complex.re h
  rw [Complex.re_sum] at h2
  simp only [Complex.exp_ofReal_mul_I_re, Complex.zero_re] at h2
  exact h2

/-- **Discrete orthogonality.** -/
theorem p1_node_cos_sum (M : ℕ) (d : ℤ) (hd : |d| < M) (θ : ℝ) :
    ∑ j ∈ range M, cos (d * (θ - 2 * π * j / M)) = if d = 0 then (M : ℝ) else 0 := by
  have hMz : (0 : ℤ) < M := lt_of_le_of_lt (abs_nonneg _) hd
  have hM : (0 : ℝ) < M := by exact_mod_cast hMz
  split_ifs with h0
  · subst h0; simp
  · have e : ∀ j : ℕ, (d : ℝ) * (θ - 2 * π * j / M) = d * θ + j * (-(2 * π * d / M)) := by
      intro j; field_simp; ring
    simp_rw [e]
    apply p1_sum_cos_arith
    · intro h
      obtain ⟨m, hm⟩ := Complex.exp_eq_one_iff.mp h
      have him := congrArg Complex.im hm
      simp at him
      have hre : -(d : ℝ) = m * M := by
        have hπ : π ≠ 0 := pi_pos.ne'
        field_simp at him
        nlinarith [pi_pos]
      have hz : -d = m * (M : ℤ) := by exact_mod_cast hre
      have hm0 : m ≠ 0 := by rintro rfl; simp at hz; exact h0 hz
      have h1 : 1 ≤ |m| := Int.one_le_abs hm0
      have habs := congrArg abs hz
      rw [abs_neg, abs_mul, abs_of_pos hMz] at habs
      nlinarith
    · rw [← Complex.exp_nat_mul]
      refine Complex.exp_eq_one_iff.mpr ⟨-d, ?_⟩
      have hMne : (M : ℂ) ≠ 0 := by exact_mod_cast hM.ne'
      push_cast
      field_simp

theorem p1_node_cos_sum_int (M : ℕ) (k l : ℕ) (c : ℤ) (hd : |(k : ℤ) - l + c| < M) (θ : ℝ) :
    ∑ j ∈ range M, cos (((k : ℝ) - l + c) * (θ - 2 * π * j / M)) =
      if (k : ℤ) - l + c = 0 then (M : ℝ) else 0 := by
  have := p1_node_cos_sum M ((k : ℤ) - l + c) hd θ
  push_cast at this
  exact this

/-! ### The Fejér–Korovkin kernel -/

/-- Coefficients `a_k = sin(π (k+1)/(n+2))`. -/
noncomputable def fkA (n k : ℕ) : ℝ := sin (π * (k + 1) / (n + 2))

/-- Normalization `S = ∑_{k ≤ n} a_k²`. -/
noncomputable def fkS (n : ℕ) : ℝ := ∑ k ∈ range (n + 1), fkA n k ^ 2

/-- The kernel `K(u) = ∑_{k,l ≤ n} a_k a_l cos((k - l) u) / S`. -/
noncomputable def fkKer (n : ℕ) (u : ℝ) : ℝ :=
  (∑ k ∈ range (n + 1), ∑ l ∈ range (n + 1), fkA n k * fkA n l * cos (((k : ℝ) - l) * u)) / fkS n

theorem p1_fkA_nonneg (n k : ℕ) (hk : k < n + 1) : 0 ≤ fkA n k := by
  unfold fkA
  apply sin_nonneg_of_nonneg_of_le_pi
  · positivity
  · rw [div_le_iff₀ (by positivity)]
    have : (k : ℝ) + 1 ≤ n + 2 := by
      have : (k : ℝ) < n + 1 := by exact_mod_cast hk
      linarith
    nlinarith [pi_pos]

theorem p1_fkS_pos (n : ℕ) : 0 < fkS n := by
  have h0 : 0 < fkA n 0 := by
    unfold fkA
    apply sin_pos_of_pos_of_lt_pi
    · positivity
    · rw [div_lt_iff₀ (by positivity)]; push_cast; nlinarith [pi_pos]
  calc 0 < fkA n 0 ^ 2 := by positivity
    _ ≤ fkS n := single_le_sum (f := fun k => fkA n k ^ 2) (fun _ _ => sq_nonneg _) (by simp)

theorem p1_fk_numerator_sq (n : ℕ) (u : ℝ) :
    ∑ k ∈ range (n + 1), ∑ l ∈ range (n + 1), fkA n k * fkA n l * cos (((k : ℝ) - l) * u) =
      (∑ k ∈ range (n + 1), fkA n k * cos (k * u)) ^ 2 + (∑ k ∈ range (n + 1), fkA n k * sin (k * u)) ^ 2 := by
  rw [sq, sq, sum_mul_sum, sum_mul_sum, ← sum_add_distrib]
  refine sum_congr rfl (fun k _ => ?_)
  rw [← sum_add_distrib]
  refine sum_congr rfl (fun l _ => ?_)
  rw [show ((k : ℝ) - l) * u = k * u - l * u by ring, cos_sub]
  ring

theorem p1_fkKer_nonneg (n : ℕ) (u : ℝ) : 0 ≤ fkKer n u := by
  unfold fkKer
  rw [p1_fk_numerator_sq]
  exact div_nonneg (by positivity) (p1_fkS_pos n).le

theorem p1_fkKer_neg (n : ℕ) (u : ℝ) : fkKer n (-u) = fkKer n u := by
  unfold fkKer
  congr 1
  refine sum_congr rfl (fun k _ => sum_congr rfl (fun l _ => ?_))
  rw [mul_neg, cos_neg]

/-- Node sums of `a_k a_l` against a Kronecker condition. -/
theorem p1_fk_diag (n : ℕ) :
    ∑ k ∈ range (n + 1), ∑ l ∈ range (n + 1), (if (k : ℤ) - l + 0 = 0 then fkA n k * fkA n l else 0) = fkS n := by
  unfold fkS
  refine sum_congr rfl (fun k hk => ?_)
  rw [sum_eq_single k]
  · simp [sq]
  · intro l _ hlk; rw [if_neg]; omega
  · intro hk'; exact absurd hk hk'

/-- `P = ∑_{k < n} a_k a_{k+1}`. -/
noncomputable def fkP (n : ℕ) : ℝ := ∑ k ∈ range n, fkA n k * fkA n (k + 1)

theorem p1_fk_offdiag_plus (n : ℕ) :
    ∑ k ∈ range (n + 1), ∑ l ∈ range (n + 1), (if (k : ℤ) - l + 1 = 0 then fkA n k * fkA n l else 0) = fkP n := by
  have e : ∀ k ∈ range (n + 1), ∑ l ∈ range (n + 1), (if (k : ℤ) - l + 1 = 0 then fkA n k * fkA n l else 0) =
      if k + 1 < n + 1 then fkA n k * fkA n (k + 1) else 0 := by
    intro k _
    split_ifs with hk1
    · rw [sum_eq_single (k + 1)]
      · rw [if_pos (by push_cast; ring)]
      · intro l _ hl; rw [if_neg]; omega
      · intro h; exact absurd (mem_range.mpr hk1) h
    · refine sum_eq_zero (fun l hl => ?_)
      rw [if_neg]; have := mem_range.mp hl; omega
  rw [sum_congr rfl e, sum_range_succ, if_neg (by omega), add_zero, fkP]
  exact sum_congr rfl (fun k hk => by rw [if_pos (by have := mem_range.mp hk; omega)])

theorem p1_fk_offdiag_minus (n : ℕ) :
    ∑ k ∈ range (n + 1), ∑ l ∈ range (n + 1), (if (k : ℤ) - l + -1 = 0 then fkA n k * fkA n l else 0) = fkP n := by
  rw [sum_comm]
  have e : ∀ l ∈ range (n + 1), ∑ k ∈ range (n + 1), (if (k : ℤ) - l + -1 = 0 then fkA n k * fkA n l else 0) =
      if l + 1 < n + 1 then fkA n l * fkA n (l + 1) else 0 := by
    intro l _
    split_ifs with hl1
    · rw [sum_eq_single (l + 1)]
      · rw [if_pos (by push_cast; ring), mul_comm]
      · intro k _ hk; rw [if_neg]; omega
      · intro h; exact absurd (mem_range.mpr hl1) h
    · refine sum_eq_zero (fun k hk => ?_)
      rw [if_neg]; have := mem_range.mp hk; omega
  rw [sum_congr rfl e, sum_range_succ, if_neg (by omega), add_zero, fkP]
  exact sum_congr rfl (fun k hk => by rw [if_pos (by have := mem_range.mp hk; omega)])

/-- The node sum of `cos(((k-l)+c) u_j)` paired with `a_k a_l`. -/
theorem p1_fk_node_pair (n M : ℕ) (c : ℤ) (hc : |c| ≤ 1) (hM : n + 1 < M) (θ : ℝ) :
    ∑ k ∈ range (n + 1), ∑ l ∈ range (n + 1),
        fkA n k * fkA n l * ∑ j ∈ range M, cos (((k : ℝ) - l + c) * (θ - 2 * π * j / M)) =
      M * ∑ k ∈ range (n + 1), ∑ l ∈ range (n + 1), (if (k : ℤ) - l + c = 0 then fkA n k * fkA n l else 0) := by
  rw [mul_sum]
  refine sum_congr rfl (fun k hk => ?_)
  rw [mul_sum]
  refine sum_congr rfl (fun l hl => ?_)
  have hk' := mem_range.mp hk; have hl' := mem_range.mp hl
  have hc' := abs_le.mp hc
  have hd : |(k : ℤ) - l + c| < M := abs_lt.mpr ⟨by omega, by omega⟩
  rw [p1_node_cos_sum_int M k l c hd θ]
  split_ifs <;> ring

/-- **Node mean of the kernel is `1`.** -/
theorem p1_fkKer_node_sum (n M : ℕ) (hM : n + 1 < M) (θ : ℝ) :
    ∑ j ∈ range M, fkKer n (θ - 2 * π * j / M) = M := by
  unfold fkKer
  rw [← sum_div, div_eq_iff (p1_fkS_pos n).ne']
  have e : ∑ j ∈ range M, ∑ k ∈ range (n + 1), ∑ l ∈ range (n + 1),
      fkA n k * fkA n l * cos (((k : ℝ) - l) * (θ - 2 * π * j / M)) =
      ∑ k ∈ range (n + 1), ∑ l ∈ range (n + 1),
        fkA n k * fkA n l * ∑ j ∈ range M, cos (((k : ℝ) - l + (0 : ℤ)) * (θ - 2 * π * j / M)) := by
    rw [sum_comm]
    refine sum_congr rfl (fun k _ => ?_)
    rw [sum_comm]
    refine sum_congr rfl (fun l _ => ?_)
    rw [mul_sum]; push_cast; simp only [add_zero]
  rw [e, p1_fk_node_pair n M 0 (by simp) hM θ, p1_fk_diag]

/-- The sines satisfy `a_{k-1} + a_{k+1} = 2 cos(π/(n+2)) a_k`, hence `P = cos(π/(n+2)) S`. -/
theorem p1_fkP_eq (n : ℕ) : fkP n = cos (π / (n + 2)) * fkS n := by
  set b : ℕ → ℝ := fun k => sin (π * k / (n + 2)) with hb
  have ha : ∀ k, fkA n k = b (k + 1) := fun k => by simp [fkA, b]
  have hrec : ∀ k, b k + b (k + 2) = 2 * cos (π / (n + 2)) * b (k + 1) := by
    intro k
    simp only [b]
    have e1 : π * (k : ℝ) / (n + 2) = π * ((k + 1 : ℕ) : ℝ) / (n + 2) - π / (n + 2) := by push_cast; ring
    have e2 : π * ((k + 2 : ℕ) : ℝ) / (n + 2) = π * ((k + 1 : ℕ) : ℝ) / (n + 2) + π / (n + 2) := by
      push_cast; ring
    rw [e1, e2, sin_sub, sin_add]; ring
  have hb0 : b 0 = 0 := by simp [b]
  have hbn : b (n + 2) = 0 := by
    simp only [b]; rw [show π * ((n + 2 : ℕ) : ℝ) / (n + 2) = π by push_cast; field_simp]; exact sin_pi
  have key : ∑ k ∈ range (n + 1), b (k + 1) * (b k + b (k + 2)) = 2 * cos (π / (n + 2)) * fkS n := by
    rw [fkS, mul_sum]
    refine sum_congr rfl (fun k _ => ?_)
    rw [hrec, ha]; ring
  have hsplit : ∑ k ∈ range (n + 1), b (k + 1) * (b k + b (k + 2)) = 2 * fkP n := by
    simp only [mul_add, sum_add_distrib]
    have h1 : ∑ k ∈ range (n + 1), b (k + 1) * b k = fkP n := by
      rw [sum_range_succ', hb0, mul_zero, add_zero, fkP]
      exact sum_congr rfl (fun k _ => by rw [ha, ha]; ring)
    have h2 : ∑ k ∈ range (n + 1), b (k + 1) * b (k + 2) = fkP n := by
      rw [sum_range_succ, hbn, mul_zero, add_zero, fkP]
      exact sum_congr rfl (fun k _ => by rw [ha, ha])
    rw [h1, h2]; ring
  linarith [key, hsplit]

theorem p1_cos_prod (d x : ℝ) :
    cos (d * x) * (1 - cos x) = cos ((d + 0) * x) - cos ((d + 1) * x) / 2 - cos ((d + -1) * x) / 2 := by
  rw [add_zero, add_mul, add_mul, one_mul, neg_one_mul, cos_add, ← sub_eq_add_neg, cos_sub]; ring

/-- **Second node moment.** `∑_j K(u_j) (1 - cos u_j) = M (1 - cos(π/(n+2)))`, `M ≥ n + 2`. -/
theorem p1_fkKer_node_moment (n M : ℕ) (hM : n + 1 < M) (θ : ℝ) :
    ∑ j ∈ range M, fkKer n (θ - 2 * π * j / M) * (1 - cos (θ - 2 * π * j / M)) =
      M * (1 - cos (π / (n + 2))) := by
  set u : ℕ → ℝ := fun j => θ - 2 * π * j / M with hu
  have hS := p1_fkS_pos n
  -- product-to-sum inside the kernel
  have hprod : ∀ j, fkKer n (u j) * (1 - cos (u j)) =
      (∑ k ∈ range (n + 1), ∑ l ∈ range (n + 1), fkA n k * fkA n l *
        (cos (((k : ℝ) - l + (0 : ℤ)) * u j) - cos (((k : ℝ) - l + (1 : ℤ)) * u j) / 2 -
          cos (((k : ℝ) - l + (-1 : ℤ)) * u j) / 2)) / fkS n := by
    intro j
    unfold fkKer
    rw [div_mul_eq_mul_div, sum_mul]
    congr 1
    refine sum_congr rfl (fun k _ => ?_)
    rw [sum_mul]
    refine sum_congr rfl (fun l _ => ?_)
    simp only [Int.cast_zero, Int.cast_one, Int.cast_neg]
    have := p1_cos_prod ((k : ℝ) - l) (u j)
    linear_combination (fkA n k * fkA n l) * this
  simp only [hu] at hprod
  simp_rw [hprod]
  rw [← sum_div, div_eq_iff hS.ne']
  have e : ∑ j ∈ range M, ∑ k ∈ range (n + 1), ∑ l ∈ range (n + 1), fkA n k * fkA n l *
      (cos (((k : ℝ) - l + (0 : ℤ)) * (θ - 2 * π * j / M)) - cos (((k : ℝ) - l + (1 : ℤ)) * (θ - 2 * π * j / M)) / 2 -
        cos (((k : ℝ) - l + (-1 : ℤ)) * (θ - 2 * π * j / M)) / 2) =
      ∑ k ∈ range (n + 1), ∑ l ∈ range (n + 1),
        (fkA n k * fkA n l * ∑ j ∈ range M, cos (((k : ℝ) - l + (0 : ℤ)) * (θ - 2 * π * j / M)) -
          (fkA n k * fkA n l * ∑ j ∈ range M, cos (((k : ℝ) - l + (1 : ℤ)) * (θ - 2 * π * j / M))) / 2 -
          (fkA n k * fkA n l * ∑ j ∈ range M, cos (((k : ℝ) - l + (-1 : ℤ)) * (θ - 2 * π * j / M))) / 2) := by
    rw [sum_comm]
    refine sum_congr rfl (fun k _ => ?_)
    rw [sum_comm]
    refine sum_congr rfl (fun l _ => ?_)
    rw [mul_sum, mul_sum, mul_sum, Finset.sum_div, Finset.sum_div, ← sum_sub_distrib, ← sum_sub_distrib]
    exact sum_congr rfl (fun j _ => by ring)
  have e2 : ∑ k ∈ range (n + 1), ∑ l ∈ range (n + 1),
        (fkA n k * fkA n l * ∑ j ∈ range M, cos (((k : ℝ) - l + (0 : ℤ)) * (θ - 2 * π * j / M)) -
          (fkA n k * fkA n l * ∑ j ∈ range M, cos (((k : ℝ) - l + (1 : ℤ)) * (θ - 2 * π * j / M))) / 2 -
          (fkA n k * fkA n l * ∑ j ∈ range M, cos (((k : ℝ) - l + (-1 : ℤ)) * (θ - 2 * π * j / M))) / 2) =
      ∑ k ∈ range (n + 1), ∑ l ∈ range (n + 1),
          fkA n k * fkA n l * ∑ j ∈ range M, cos (((k : ℝ) - l + (0 : ℤ)) * (θ - 2 * π * j / M)) -
        (∑ k ∈ range (n + 1), ∑ l ∈ range (n + 1),
          fkA n k * fkA n l * ∑ j ∈ range M, cos (((k : ℝ) - l + (1 : ℤ)) * (θ - 2 * π * j / M))) / 2 -
        (∑ k ∈ range (n + 1), ∑ l ∈ range (n + 1),
          fkA n k * fkA n l * ∑ j ∈ range M, cos (((k : ℝ) - l + (-1 : ℤ)) * (θ - 2 * π * j / M))) / 2 := by
    simp only [sum_sub_distrib, Finset.sum_div]
  rw [e, e2, p1_fk_node_pair n M 0 (by simp) hM θ, p1_fk_node_pair n M 1 (by simp) hM θ,
    p1_fk_node_pair n M (-1) (by simp) hM θ, p1_fk_diag, p1_fk_offdiag_plus, p1_fk_offdiag_minus, p1_fkP_eq]
  ring

theorem p1_one_sub_cos_le (n : ℕ) : 1 - cos (π / (n + 2)) ≤ (π / (n + 2)) ^ 2 / 2 := by
  have := one_sub_sq_div_two_le_cos (x := π / (n + 2))
  linarith

/-! ### The operator and the error bound -/

/-- `jop n g θ = (1/M) ∑_j g(cos t_j) (K(θ - t_j) + K(θ + t_j))/2` with `M = n + 2`, `t_j = 2πj/M`. -/
noncomputable def jop (n : ℕ) (g : ℝ → ℝ) (θ : ℝ) : ℝ :=
  (1 / (n + 2 : ℕ)) * ∑ j ∈ range (n + 2), g (cos (2 * π * j / (n + 2 : ℕ))) *
    ((fkKer n (θ - 2 * π * j / (n + 2 : ℕ)) + fkKer n (θ + 2 * π * j / (n + 2 : ℕ))) / 2)

/-- Weighted Cauchy–Schwarz: `(∑ w|s|)² ≤ (∑ w s²)(∑ w)` for `w ≥ 0`. -/
theorem p1_weighted_cs (M : ℕ) (w s : ℕ → ℝ) (hw : ∀ j, 0 ≤ w j) :
    (∑ j ∈ range M, w j * |s j|) ^ 2 ≤ (∑ j ∈ range M, w j * s j ^ 2) * ∑ j ∈ range M, w j :=
  sum_sq_le_sum_mul_sum_of_sq_le_mul _ (fun j _ => mul_nonneg (hw j) (sq_nonneg _)) (fun j _ => hw j)
    (fun j _ => le_of_eq (by rw [mul_pow, sq_abs]; ring))

theorem p1_fk_abs_sin_sum (n : ℕ) (θ : ℝ) :
    (∑ j ∈ range (n + 2), fkKer n (θ - 2 * π * j / (n + 2 : ℕ)) * |sin ((θ - 2 * π * j / (n + 2 : ℕ)) / 2)|) ^ 2 ≤
      ((n + 2 : ℕ) : ℝ) ^ 2 * ((π / (n + 2)) ^ 2 / 4) := by
  set M := n + 2
  have hcs := p1_weighted_cs M (fun j => fkKer n (θ - 2 * π * j / M)) (fun j => sin ((θ - 2 * π * j / M) / 2))
    (fun j => p1_fkKer_nonneg n _)
  have hsq : ∀ x : ℝ, sin (x / 2) ^ 2 = (1 - cos x) / 2 := by
    intro x
    rw [sin_sq_eq_half_sub, show 2 * (x / 2) = x by ring]; ring
  have hmom : ∑ j ∈ range M, fkKer n (θ - 2 * π * j / M) * sin ((θ - 2 * π * j / M) / 2) ^ 2 =
      M * (1 - cos (π / (n + 2))) / 2 := by
    simp_rw [hsq, mul_div_assoc']
    rw [← sum_div, p1_fkKer_node_moment n M (by omega) θ]
  refine hcs.trans ?_
  rw [hmom, p1_fkKer_node_sum n M (by omega) θ]
  have hM0 : (0 : ℝ) ≤ M := Nat.cast_nonneg M
  have hb := p1_one_sub_cos_le n
  have : M * (1 - cos (π / (n + 2))) / 2 * M = (M : ℝ) ^ 2 * ((1 - cos (π / (n + 2))) / 2) := by ring
  rw [this]
  exact mul_le_mul_of_nonneg_left (by linarith) (sq_nonneg _)

/-- **Error of the operator.** If `|g x - g y| ≤ L |x - y|` on `[-1, 1]`, then `|jop g θ - g (cos θ)| ≤ L π/(n+2)`. -/
theorem p1_jop_error (n : ℕ) (g : ℝ → ℝ) (L : ℝ) (hL : 0 ≤ L)
    (hg : ∀ x ∈ Set.Icc (-1 : ℝ) 1, ∀ y ∈ Set.Icc (-1 : ℝ) 1, |g x - g y| ≤ L * |x - y|) (θ : ℝ) :
    |jop n g θ - g (cos θ)| ≤ L * (π / (n + 2)) := by
  set M := n + 2 with hMdef
  have hMpos : (0 : ℝ) < M := by positivity
  set t : ℕ → ℝ := fun j => 2 * π * j / M with ht
  set Km : ℕ → ℝ := fun j => fkKer n (θ - t j)
  set Kp : ℕ → ℝ := fun j => fkKer n (θ + t j)
  have hKm : ∀ j, 0 ≤ Km j := fun j => p1_fkKer_nonneg n _
  have hKp : ∀ j, 0 ≤ Kp j := fun j => p1_fkKer_nonneg n _
  have hsumm : ∑ j ∈ range M, Km j = M := p1_fkKer_node_sum n M (by omega) θ
  have hsump : ∑ j ∈ range M, Kp j = M := by
    have := p1_fkKer_node_sum n M (by omega) (-θ)
    rw [← this]
    refine sum_congr rfl (fun j _ => ?_)
    simp only [Kp, t]; rw [← p1_fkKer_neg]; congr 1; ring
  have hcos : ∀ x : ℝ, cos x ∈ Set.Icc (-1 : ℝ) 1 := fun x => ⟨neg_one_le_cos x, cos_le_one x⟩
  -- write `g (cos θ)` as the same average
  have hs2 : ∑ j ∈ range M, (Km j + Kp j) / 2 = M := by
    rw [← Finset.sum_div, sum_add_distrib, hsumm, hsump]; ring
  have hrep : g (cos θ) = (1 / M) * ∑ j ∈ range M, g (cos θ) * ((Km j + Kp j) / 2) := by
    rw [← mul_sum, hs2]; field_simp
  have hdiff : jop n g θ - g (cos θ) =
      (1 / M) * ∑ j ∈ range M, (g (cos (t j)) - g (cos θ)) * ((Km j + Kp j) / 2) := by
    conv_lhs => rw [hrep, jop]
    simp only [← hMdef]
    rw [← mul_sub, ← sum_sub_distrib]
    congr 1
    exact sum_congr rfl (fun j _ => by simp only [Km, Kp, t]; ring)
  -- pointwise bounds
  have hpt : ∀ j, |(g (cos (t j)) - g (cos θ)) * ((Km j + Kp j) / 2)| ≤
      L * (Km j * |sin ((θ - t j) / 2)| + Kp j * |sin ((θ + t j) / 2)|) := by
    intro j
    have hgj := hg _ (hcos (t j)) _ (hcos θ)
    have hcc : cos (t j) - cos θ = -2 * sin ((t j + θ) / 2) * sin ((t j - θ) / 2) := cos_sub_cos _ _
    have hb1 : |cos (t j) - cos θ| ≤ 2 * |sin ((θ - t j) / 2)| := by
      rw [hcc, abs_mul, abs_mul, show (t j - θ) / 2 = -((θ - t j) / 2) by ring, sin_neg, abs_neg]
      have := abs_sin_le_one ((t j + θ) / 2)
      have h0 := abs_nonneg (sin ((θ - t j) / 2))
      norm_num; nlinarith
    have hb2 : |cos (t j) - cos θ| ≤ 2 * |sin ((θ + t j) / 2)| := by
      rw [hcc, abs_mul, abs_mul, show (t j + θ) / 2 = (θ + t j) / 2 by ring]
      have := abs_sin_le_one ((t j - θ) / 2)
      have h0 := abs_nonneg (sin ((θ + t j) / 2))
      norm_num; nlinarith
    rw [abs_mul, abs_of_nonneg (div_nonneg (add_nonneg (hKm j) (hKp j)) two_pos.le)]
    calc |g (cos (t j)) - g (cos θ)| * ((Km j + Kp j) / 2)
        = |g (cos (t j)) - g (cos θ)| * Km j / 2 + |g (cos (t j)) - g (cos θ)| * Kp j / 2 := by ring
      _ ≤ (L * (2 * |sin ((θ - t j) / 2)|)) * Km j / 2 + (L * (2 * |sin ((θ + t j) / 2)|)) * Kp j / 2 := by
          gcongr
          · exact hKm j
          · exact hgj.trans (mul_le_mul_of_nonneg_left hb1 hL)
          · exact hKp j
          · exact hgj.trans (mul_le_mul_of_nonneg_left hb2 hL)
      _ = L * (Km j * |sin ((θ - t j) / 2)| + Kp j * |sin ((θ + t j) / 2)|) := by ring
  set A := ∑ j ∈ range M, Km j * |sin ((θ - t j) / 2)|
  set B := ∑ j ∈ range M, Kp j * |sin ((θ + t j) / 2)|
  have hA : A ^ 2 ≤ (M : ℝ) ^ 2 * ((π / (n + 2)) ^ 2 / 4) := p1_fk_abs_sin_sum n θ
  have hB : B ^ 2 ≤ (M : ℝ) ^ 2 * ((π / (n + 2)) ^ 2 / 4) := by
    have h := p1_fk_abs_sin_sum n (-θ)
    have e : B = ∑ j ∈ range (n + 2), fkKer n (-θ - 2 * π * j / (n + 2 : ℕ)) *
        |sin ((-θ - 2 * π * j / (n + 2 : ℕ)) / 2)| := by
      refine sum_congr rfl (fun j _ => ?_)
      simp only [Kp, t]
      rw [← p1_fkKer_neg n (-θ - _), show -(-θ - 2 * π * j / ((n + 2 : ℕ) : ℝ)) = θ + 2 * π * j / ((n + 2 : ℕ) : ℝ)
        by ring, show (-θ - 2 * π * j / ((n + 2 : ℕ) : ℝ)) / 2 = -((θ + 2 * π * j / ((n + 2 : ℕ) : ℝ)) / 2) by ring,
        sin_neg, abs_neg]
    rw [e]; exact h
  have hA0 : 0 ≤ A := sum_nonneg (fun j _ => mul_nonneg (hKm j) (abs_nonneg _))
  have hB0 : 0 ≤ B := sum_nonneg (fun j _ => mul_nonneg (hKp j) (abs_nonneg _))
  have hX0 : 0 ≤ (M : ℝ) * (π / (n + 2)) / 2 := by positivity
  have hAle : A ≤ M * (π / (n + 2)) / 2 := by
    nlinarith [sq_nonneg (A - M * (π / (n + 2)) / 2), sq_nonneg (A + M * (π / (n + 2)) / 2)]
  have hBle : B ≤ M * (π / (n + 2)) / 2 := by
    nlinarith [sq_nonneg (B - M * (π / (n + 2)) / 2), sq_nonneg (B + M * (π / (n + 2)) / 2)]
  rw [hdiff, abs_mul, abs_of_pos (by positivity : (0 : ℝ) < 1 / M)]
  calc 1 / (M : ℝ) * |∑ j ∈ range M, (g (cos (t j)) - g (cos θ)) * ((Km j + Kp j) / 2)|
      ≤ 1 / M * ∑ j ∈ range M, L * (Km j * |sin ((θ - t j) / 2)| + Kp j * |sin ((θ + t j) / 2)|) :=
        mul_le_mul_of_nonneg_left ((abs_sum_le_sum_abs _ _).trans (sum_le_sum (fun j _ => hpt j))) (by positivity)
    _ = 1 / M * (L * (A + B)) := by rw [← mul_sum, sum_add_distrib]
    _ ≤ 1 / M * (L * (M * (π / (n + 2)))) := by gcongr; linarith
    _ = L * (π / (n + 2)) := by field_simp

end CurrentMM
