import CurrentProofs.Paper1MergedModel
import CurrentProofs.Paper1Testing
import CurrentProofs.GaussianRecords
import Mathlib.Analysis.SpecificLimits.Basic
import Mathlib.Analysis.Convex.Mul
import Mathlib.Algebra.BigOperators.Intervals

/-!
# Paper 1, Theorem 3.1 (ii): separating a cohort from a symmetric split needs `T = Ω(δ^{-4})`

The paper's model with a single cohort at rate `η̄` (economy 0) against two cohorts at `η̄ ± δ` with the same
total weight `q` (economy `δ`). One experiment applies a deterministic probe `v` with average power at most `P`
over `T` periods from the reset state and records the `T` prices with independent `N(0, σ²)` noise.

* `p1_conv_l1_le`, `p1_response_l1`, `p1_response_diff_l1`: under `|a| + |κ| ‖k‖₁ ≤ s < 1` the closed-loop
  response is summable with `‖h‖₁ ≤ |κ|/(1-s)`, and two responses differ by at most `|κ| ‖Δk‖₁ ‖h'‖₁/(1-s)` in `ℓ₁`;
* `p1_split_kernel_gap`: the kernels of the two economies differ by at most `2 q δ²/ε³` in `ℓ₁` when all rates lie
  in `[ε, 1-ε]` (the first-order term cancels; second differences of geometric series);
* `p1_conv_energy`: a probe passed through a filter of `ℓ₁` norm `D` gains at most `D²` in energy;
* `p1_thm_merged_separation_power`: any test whose two error probabilities are at most `1/4` needs
  `T ≥ σ² / (2 C² P δ⁴)` with `C = 2 κ² q / (ε³ (1-s)²)`, the `Ω(δ^{-4})` bound of Theorem 3.1 (ii).
-/

namespace CurrentMM

open Finset MeasureTheory
open scoped NNReal

/-- Finite Cauchy-product bound. -/
theorem p1_conv_l1_le (a b : ℕ → ℝ) (n : ℕ) :
    ∑ t ∈ range n, ∑ j ∈ range (t + 1), |a j| * |b (t - j)| ≤
      (∑ j ∈ range n, |a j|) * (∑ u ∈ range n, |b u|) := by
  rw [sum_range_diag_flip n (fun j u => |a j| * |b u|), sum_mul]
  refine sum_le_sum (fun j _ => ?_)
  rw [← mul_sum]
  refine mul_le_mul_of_nonneg_left ?_ (abs_nonneg _)
  exact sum_le_sum_of_subset_of_nonneg (range_mono (Nat.sub_le n j)) (fun _ _ _ => abs_nonneg _)

/-- **Summable closed-loop response.** -/
theorem p1_response_l1 (a κ K1 s : ℝ) (k h : ℕ → ℝ) (h0 : h 0 = κ)
    (hrec : ∀ t, h (t + 1) = a * h t + κ * ∑ j ∈ range (t + 1), k j * h (t - j))
    (hK1 : ∀ n, ∑ m ∈ range n, |k m| ≤ K1) (hs : |a| + |κ| * K1 ≤ s) (hs1 : s < 1) :
    ∀ n, ∑ t ∈ range n, |h t| ≤ |κ| / (1 - s) := by
  have hK10 : 0 ≤ K1 := by simpa using hK1 0
  have hs0 : 0 ≤ s := le_trans (by positivity) hs
  have hstep : ∀ n, ∑ t ∈ range (n + 1), |h t| ≤ |κ| + s * ∑ t ∈ range n, |h t| := by
    intro n
    have hS0 : 0 ≤ ∑ t ∈ range n, |h t| := sum_nonneg fun _ _ => abs_nonneg _
    have hb : ∑ t ∈ range n, |h (t + 1)| ≤ (|a| + |κ| * K1) * ∑ t ∈ range n, |h t| := by
      calc ∑ t ∈ range n, |h (t + 1)|
          ≤ ∑ t ∈ range n, (|a| * |h t| + |κ| * ∑ j ∈ range (t + 1), |k j| * |h (t - j)|) := by
            refine sum_le_sum (fun t _ => ?_)
            rw [hrec t]
            refine (abs_add_le _ _).trans ?_
            rw [abs_mul, abs_mul]
            gcongr
            exact (abs_sum_le_sum_abs _ _).trans (le_of_eq (sum_congr rfl (fun j _ => abs_mul _ _)))
        _ = |a| * ∑ t ∈ range n, |h t| + |κ| * ∑ t ∈ range n, ∑ j ∈ range (t + 1), |k j| * |h (t - j)| := by
            rw [sum_add_distrib, mul_sum, mul_sum]
        _ ≤ |a| * ∑ t ∈ range n, |h t| + |κ| * (K1 * ∑ t ∈ range n, |h t|) := by
            gcongr
            exact (p1_conv_l1_le k h n).trans (mul_le_mul_of_nonneg_right (hK1 n) hS0)
        _ = (|a| + |κ| * K1) * ∑ t ∈ range n, |h t| := by ring
    rw [sum_range_succ', h0]
    nlinarith [mul_le_mul_of_nonneg_right hs hS0]
  intro n
  rcases n with _ | n
  · simp; positivity
  · have h1 := hstep n
    have hmono : ∑ t ∈ range n, |h t| ≤ ∑ t ∈ range (n + 1), |h t| := by
      rw [sum_range_succ]; linarith [abs_nonneg (h n)]
    rw [le_div_iff₀ (by linarith)]
    nlinarith [mul_le_mul_of_nonneg_left hmono hs0]

/-- **Two closed-loop responses differ in `ℓ₁` by at most `|κ| ‖Δk‖₁ ‖h'‖₁ / (1 - s)`.** -/
theorem p1_response_diff_l1 (a κ K1 s E H1 : ℝ) (k k' h h' : ℕ → ℝ) (h0 : h 0 = κ) (h0' : h' 0 = κ)
    (hrec : ∀ t, h (t + 1) = a * h t + κ * ∑ j ∈ range (t + 1), k j * h (t - j))
    (hrec' : ∀ t, h' (t + 1) = a * h' t + κ * ∑ j ∈ range (t + 1), k' j * h' (t - j))
    (hK1 : ∀ n, ∑ m ∈ range n, |k m| ≤ K1) (hs : |a| + |κ| * K1 ≤ s) (hs1 : s < 1)
    (hE : ∀ n, ∑ m ∈ range n, |k m - k' m| ≤ E) (hH1 : ∀ n, ∑ t ∈ range n, |h' t| ≤ H1) :
    ∀ n, ∑ t ∈ range n, |h t - h' t| ≤ |κ| * E * H1 / (1 - s) := by
  have hK10 : 0 ≤ K1 := by simpa using hK1 0
  have hE0 : 0 ≤ E := by simpa using hE 0
  have hH10 : 0 ≤ H1 := by simpa using hH1 0
  have hs0 : 0 ≤ s := le_trans (by positivity) hs
  set d : ℕ → ℝ := fun t => h t - h' t with hd
  have hdrec : ∀ t, d (t + 1) = a * d t + κ * ∑ j ∈ range (t + 1), k j * d (t - j) +
      κ * ∑ j ∈ range (t + 1), (k j - k' j) * h' (t - j) := by
    intro t
    simp only [hd, hrec t, hrec' t]
    simp only [mul_sub, sub_mul, sum_sub_distrib]
    ring
  have hstep : ∀ n, ∑ t ∈ range (n + 1), |d t| ≤ |κ| * E * H1 + s * ∑ t ∈ range n, |d t| := by
    intro n
    have hS0 : 0 ≤ ∑ t ∈ range n, |d t| := sum_nonneg fun _ _ => abs_nonneg _
    have hb : ∑ t ∈ range n, |d (t + 1)| ≤ (|a| + |κ| * K1) * ∑ t ∈ range n, |d t| + |κ| * (E * H1) := by
      calc ∑ t ∈ range n, |d (t + 1)|
          ≤ ∑ t ∈ range n, (|a| * |d t| + |κ| * ∑ j ∈ range (t + 1), |k j| * |d (t - j)| +
              |κ| * ∑ j ∈ range (t + 1), |k j - k' j| * |h' (t - j)|) := by
            refine sum_le_sum (fun t _ => ?_)
            rw [hdrec t]
            refine (abs_add_le _ _).trans ?_
            refine add_le_add ((abs_add_le _ _).trans ?_) ?_
            · rw [abs_mul, abs_mul]
              gcongr
              exact (abs_sum_le_sum_abs _ _).trans (le_of_eq (sum_congr rfl (fun j _ => abs_mul _ _)))
            · rw [abs_mul]
              gcongr
              exact (abs_sum_le_sum_abs _ _).trans (le_of_eq (sum_congr rfl (fun j _ => abs_mul _ _)))
        _ = |a| * ∑ t ∈ range n, |d t| + |κ| * ∑ t ∈ range n, ∑ j ∈ range (t + 1), |k j| * |d (t - j)| +
              |κ| * ∑ t ∈ range n, ∑ j ∈ range (t + 1), |k j - k' j| * |h' (t - j)| := by
            rw [sum_add_distrib, sum_add_distrib, mul_sum, mul_sum, mul_sum]
        _ ≤ |a| * ∑ t ∈ range n, |d t| + |κ| * (K1 * ∑ t ∈ range n, |d t|) + |κ| * (E * H1) := by
            gcongr
            · exact (p1_conv_l1_le k d n).trans (mul_le_mul_of_nonneg_right (hK1 n) hS0)
            · exact (p1_conv_l1_le (fun j => k j - k' j) h' n).trans
                (mul_le_mul (hE n) (hH1 n) (sum_nonneg fun _ _ => abs_nonneg _) hE0)
        _ = (|a| + |κ| * K1) * ∑ t ∈ range n, |d t| + |κ| * (E * H1) := by ring
    rw [sum_range_succ']
    have hd0 : d 0 = 0 := by simp [hd, h0, h0']
    rw [hd0, abs_zero, add_zero]
    nlinarith [mul_le_mul_of_nonneg_right hs hS0]
  intro n
  rcases n with _ | n
  · simp; positivity
  · have h1 := hstep n
    have hmono : ∑ t ∈ range n, |d t| ≤ ∑ t ∈ range (n + 1), |d t| := by
      rw [sum_range_succ]; linarith [abs_nonneg (d n)]
    rw [le_div_iff₀ (by linarith)]
    nlinarith [mul_le_mul_of_nonneg_left hmono hs0]

/-- Kernel of a single cohort of weight `c` at rate `η`: `ℓ₁` partial sums are at most `c`. -/
theorem p1_single_kernel_l1 (c η : ℝ) (hc : 0 ≤ c) (hη0 : 0 ≤ η) (hη1 : η ≤ 1) (n : ℕ) :
    ∑ m ∈ range n, |c * η * (1 - η) ^ m| ≤ c := by
  have hterm : ∀ m, |c * η * (1 - η) ^ m| = c * (η * (1 - η) ^ m) := fun m => by
    rw [abs_of_nonneg (by have := pow_nonneg (sub_nonneg.mpr hη1) m; positivity)]; ring
  have hg : ∑ m ∈ range n, η * (1 - η) ^ m = 1 - (1 - η) ^ n := by
    rw [← mul_sum]
    have := mul_neg_geom_sum (1 - η) n
    rwa [sub_sub_cancel] at this
  rw [sum_congr rfl (fun m _ => hterm m), ← mul_sum, hg]
  have : 0 ≤ (1 - η) ^ n := pow_nonneg (sub_nonneg.mpr hη1) n
  nlinarith

/-- Second difference of a power is nonnegative (convexity). -/
theorem p1_second_diff_pow_nonneg (x δ : ℝ) (hδ0 : 0 ≤ δ) (hxδ : 0 ≤ x - δ) (p : ℕ) :
    0 ≤ (x + δ) ^ p + (x - δ) ^ p - 2 * x ^ p := by
  have hδ : 0 ≤ x + δ := by linarith
  have h := (convexOn_pow p).2 (Set.mem_Ici.mpr hδ) (Set.mem_Ici.mpr hxδ)
    (by norm_num : (0 : ℝ) ≤ 1 / 2) (by norm_num : (0 : ℝ) ≤ 1 / 2) (by norm_num)
  simp only [smul_eq_mul] at h
  have e : 1 / 2 * (x + δ) + 1 / 2 * (x - δ) = x := by ring
  rw [e] at h
  linarith

/-- **The split's kernel is within `2 q δ²/ε³` of the single cohort's kernel in `ℓ₁`.** With `η̄ - δ ≥ ε` and
`η̄ + δ ≤ 1 - ε`, the first-order variation cancels. -/
theorem p1_split_kernel_gap (q ηbar δ ε : ℝ) (hq : 0 ≤ q) (hε : 0 < ε) (hδ : 0 ≤ δ)
    (hlo : ε ≤ ηbar - δ) (hhi : ηbar + δ ≤ 1 - ε) (n : ℕ) :
    ∑ m ∈ range n, |(q / 2 * (ηbar - δ) * (1 - (ηbar - δ)) ^ m + q / 2 * (ηbar + δ) * (1 - (ηbar + δ)) ^ m) -
      q * ηbar * (1 - ηbar) ^ m| ≤ 2 * q * δ ^ 2 / ε ^ 3 := by
  set r := 1 - ηbar with hr
  set D2 : ℕ → ℝ := fun p => (r + δ) ^ p + (r - δ) ^ p - 2 * r ^ p with hD2
  have hrδ : 0 ≤ r - δ := by rw [hr]; linarith
  have hD2nn : ∀ p, 0 ≤ D2 p := fun p => p1_second_diff_pow_nonneg r δ hδ hrδ p
  have hterm : ∀ m, (q / 2 * (ηbar - δ) * (1 - (ηbar - δ)) ^ m + q / 2 * (ηbar + δ) * (1 - (ηbar + δ)) ^ m) -
      q * ηbar * (1 - ηbar) ^ m = q / 2 * (D2 m - D2 (m + 1)) := by
    intro m
    simp only [hD2, hr, pow_succ]
    ring
  have habs : ∀ m, |(q / 2 * (ηbar - δ) * (1 - (ηbar - δ)) ^ m + q / 2 * (ηbar + δ) * (1 - (ηbar + δ)) ^ m) -
      q * ηbar * (1 - ηbar) ^ m| ≤ q / 2 * (D2 m + D2 (m + 1)) := by
    intro m
    rw [hterm m, abs_mul, abs_of_nonneg (by positivity : 0 ≤ q / 2)]
    gcongr
    refine (abs_sub _ _).trans (le_of_eq ?_)
    rw [abs_of_nonneg (hD2nn m), abs_of_nonneg (hD2nn (m + 1))]
  -- summability and the value of `∑' D2`
  have hp1 : 0 ≤ r + δ := by linarith
  have hp2 : r + δ < 1 := by rw [hr]; linarith
  have hm1 : r - δ < 1 := by linarith
  have hr0 : 0 ≤ r := by linarith
  have hr1 : r < 1 := by linarith
  have hs1 := summable_geometric_of_lt_one hp1 hp2
  have hs2 := summable_geometric_of_lt_one hrδ hm1
  have hs3 := (summable_geometric_of_lt_one hr0 hr1).mul_left 2
  have hsum : Summable D2 := (hs1.add hs2).sub hs3
  have htsum : ∑' p, D2 p = (1 - (r + δ))⁻¹ + (1 - (r - δ))⁻¹ - 2 * (1 - r)⁻¹ := by
    rw [show D2 = fun p => ((r + δ) ^ p + (r - δ) ^ p) - 2 * r ^ p from rfl,
      (hs1.add hs2).tsum_sub hs3, hs1.tsum_add hs2, tsum_mul_left, tsum_geometric_of_lt_one hp1 hp2,
      tsum_geometric_of_lt_one hrδ hm1, tsum_geometric_of_lt_one hr0 hr1]
  have hη : ε ≤ ηbar := by linarith
  have hval : (1 - (r + δ))⁻¹ + (1 - (r - δ))⁻¹ - 2 * (1 - r)⁻¹ ≤ 2 * δ ^ 2 / ε ^ 3 := by
    have e1 : 1 - (r + δ) = ηbar - δ := by rw [hr]; ring
    have e2 : 1 - (r - δ) = ηbar + δ := by rw [hr]; ring
    have e3 : 1 - r = ηbar := by rw [hr]; ring
    rw [e1, e2, e3]
    have ha : 0 < ηbar - δ := by linarith
    have hb : 0 < ηbar + δ := by linarith
    have hc : 0 < ηbar := by linarith
    have key : (ηbar - δ)⁻¹ + (ηbar + δ)⁻¹ - 2 * ηbar⁻¹ = 2 * δ ^ 2 / (ηbar * ((ηbar - δ) * (ηbar + δ))) := by
      field_simp; ring
    rw [key]
    have hden : ε ^ 3 ≤ ηbar * ((ηbar - δ) * (ηbar + δ)) := by
      have h1 : ε * ε ≤ (ηbar - δ) * (ηbar + δ) := mul_le_mul hlo (by linarith) hε.le ha.le
      calc ε ^ 3 = ε * (ε * ε) := by ring
        _ ≤ ηbar * ((ηbar - δ) * (ηbar + δ)) := mul_le_mul hη h1 (by positivity) hc.le
    exact div_le_div_of_nonneg_left (by positivity) (by positivity) hden
  have hA : ∑ m ∈ range n, D2 m ≤ 2 * δ ^ 2 / ε ^ 3 :=
    (hsum.sum_le_tsum _ (fun m _ => hD2nn m)).trans (htsum ▸ hval)
  have hB : ∑ m ∈ range n, D2 (m + 1) ≤ 2 * δ ^ 2 / ε ^ 3 := by
    have e : ∑ m ∈ range n, D2 (m + 1) = ∑ m ∈ range (n + 1), D2 m - D2 0 := by
      rw [sum_range_succ']; ring
    have h0 : D2 0 = 0 := by simp [hD2]; ring
    rw [e, h0, sub_zero]
    exact (hsum.sum_le_tsum _ (fun m _ => hD2nn m)).trans (htsum ▸ hval)
  calc _ ≤ ∑ m ∈ range n, q / 2 * (D2 m + D2 (m + 1)) := sum_le_sum (fun m _ => habs m)
    _ = q / 2 * (∑ m ∈ range n, D2 m + ∑ m ∈ range n, D2 (m + 1)) := by rw [← mul_sum, sum_add_distrib]
    _ ≤ q / 2 * (2 * δ ^ 2 / ε ^ 3 + 2 * δ ^ 2 / ε ^ 3) := by gcongr
    _ = 2 * q * δ ^ 2 / ε ^ 3 := by ring

/-- **Energy gain of a summable filter.** -/
theorem p1_conv_energy (d v : ℕ → ℝ) (D : ℝ) (hD : ∀ n, ∑ t ∈ range n, |d t| ≤ D) (T : ℕ) :
    ∑ t ∈ range T, (∑ u ∈ range (t + 1), v u * d (t - u)) ^ 2 ≤ D ^ 2 * ∑ t ∈ range T, v t ^ 2 := by
  have hD0 : 0 ≤ D := by simpa using hD 0
  have hpt : ∀ t, (∑ u ∈ range (t + 1), v u * d (t - u)) ^ 2 ≤
      D * ∑ u ∈ range (t + 1), |d (t - u)| * v u ^ 2 := by
    intro t
    have hcs := sum_mul_sq_le_sq_mul_sq (range (t + 1)) (fun u => Real.sqrt |d (t - u)|)
      (fun u => Real.sqrt |d (t - u)| * |v u|)
    have e1 : ∀ u, Real.sqrt |d (t - u)| * (Real.sqrt |d (t - u)| * |v u|) = |v u * d (t - u)| := by
      intro u
      rw [← mul_assoc, Real.mul_self_sqrt (abs_nonneg _), abs_mul, mul_comm]
    have e2 : ∀ u, Real.sqrt |d (t - u)| ^ 2 = |d (t - u)| := fun u => Real.sq_sqrt (abs_nonneg _)
    have e3 : ∀ u, (Real.sqrt |d (t - u)| * |v u|) ^ 2 = |d (t - u)| * v u ^ 2 := by
      intro u; rw [mul_pow, Real.sq_sqrt (abs_nonneg _), sq_abs]
    simp only [e1, e2, e3] at hcs
    have hrefl : ∑ u ∈ range (t + 1), |d (t - u)| ≤ D := by
      have := sum_range_reflect (fun j => |d j|) (t + 1)
      simp only [Nat.add_sub_cancel] at this
      rw [this]; exact hD (t + 1)
    calc (∑ u ∈ range (t + 1), v u * d (t - u)) ^ 2 = |∑ u ∈ range (t + 1), v u * d (t - u)| ^ 2 :=
          (sq_abs _).symm
      _ ≤ (∑ u ∈ range (t + 1), |v u * d (t - u)|) ^ 2 := by
          gcongr; exact abs_sum_le_sum_abs _ _
      _ ≤ (∑ u ∈ range (t + 1), |d (t - u)|) * ∑ u ∈ range (t + 1), |d (t - u)| * v u ^ 2 := hcs
      _ ≤ D * ∑ u ∈ range (t + 1), |d (t - u)| * v u ^ 2 := by
          gcongr
  calc ∑ t ∈ range T, (∑ u ∈ range (t + 1), v u * d (t - u)) ^ 2
      ≤ ∑ t ∈ range T, D * ∑ u ∈ range (t + 1), |d (t - u)| * v u ^ 2 := sum_le_sum (fun t _ => hpt t)
    _ = D * ∑ t ∈ range T, ∑ u ∈ range (t + 1), v u ^ 2 * |d (t - u)| := by
        rw [← mul_sum]; congr 1
        exact sum_congr rfl (fun t _ => sum_congr rfl (fun u _ => mul_comm _ _))
    _ = D * ∑ u ∈ range T, ∑ j ∈ range (T - u), v u ^ 2 * |d j| := by
        rw [sum_range_diag_flip T (fun u j => v u ^ 2 * |d j|)]
    _ ≤ D * ∑ u ∈ range T, v u ^ 2 * D := by
        gcongr with u hu
        rw [← mul_sum]
        exact mul_le_mul_of_nonneg_left (hD (T - u)) (sq_nonneg _)
    _ = D ^ 2 * ∑ t ∈ range T, v t ^ 2 := by rw [← sum_mul]; ring

/-- **Theorem 3.1 (ii), formal version.** A single cohort of weight `q` at rate `η̄` against two cohorts of weight
`q/2` at `η̄ ± δ`, all rates in `[ε, 1-ε]`, with `a ≥ 0`, `κ > 0` and `a + κ q ≤ s < 1` (uniform Schur stability of
this positive family). A deterministic probe `v` with `∑_{t<T} v_t² ≤ P T` is applied from the reset state and the
`T` prices `x_1, …, x_T` of the paper's state-space model are recorded with independent `N(0, σ²)` noise. If a
test `A` errs with probability at most `1/4` under each economy, then `σ² ≤ 2 C² P δ⁴ T` with
`C = 2 κ² q / (ε³ (1-s)²)`, that is `T ≥ σ² / (2 C² P δ⁴) = Ω(δ^{-4})`. -/
theorem p1_thm_merged_separation_power (a κ q ηbar δ ε s : ℝ) (ha : 0 ≤ a) (hκ : 0 < κ) (hq : 0 ≤ q)
    (hε : 0 < ε) (hδ : 0 < δ) (hlo : ε ≤ ηbar - δ) (hhi : ηbar + δ ≤ 1 - ε)
    (hs : a + κ * q ≤ s) (hs1 : s < 1)
    (T : ℕ) (v : ℕ → ℝ) (P : ℝ) (hP : ∑ t ∈ range T, v t ^ 2 ≤ P * T)
    (variance : ℝ≥0) (hv : variance ≠ 0)
    (A : Set (ObservationRecord T)) (hA : MeasurableSet A)
    (herrδ : (gaussianRecordLaw T (fun t => (controlledCohortRun a κ ![q / 2, q / 2] ![ηbar - δ, ηbar + δ] v
      (t.val + 1)).price) variance).real A ≤ 1 / 4)
    (herr0 : (gaussianRecordLaw T (fun t => (controlledCohortRun a κ ![q] ![ηbar] v
      (t.val + 1)).price) variance).real Aᶜ ≤ 1 / 4) :
    (variance : ℝ) ≤ 2 * (2 * κ ^ 2 * q / (ε ^ 3 * (1 - s) ^ 2)) ^ 2 * P * δ ^ 4 * T := by
  set qδ : Fin 2 → ℝ := ![q / 2, q / 2]
  set rδ : Fin 2 → ℝ := ![ηbar - δ, ηbar + δ]
  set q0 : Fin 1 → ℝ := ![q]
  set r0 : Fin 1 → ℝ := ![ηbar]
  set hδf := actualCohortImpulse a κ qδ rδ with hhδf
  set h0f := actualCohortImpulse a κ q0 r0 with hh0f
  have hkδ : ∀ m, cohortKernel qδ rδ m =
      q / 2 * (ηbar - δ) * (1 - (ηbar - δ)) ^ m + q / 2 * (ηbar + δ) * (1 - (ηbar + δ)) ^ m := by
    intro m; simp [cohortKernel, qδ, rδ, Fin.sum_univ_two]
  have hk0 : ∀ m, cohortKernel q0 r0 m = q * ηbar * (1 - ηbar) ^ m := by
    intro m; simp [cohortKernel, q0, r0]
  have hη0 : 0 ≤ ηbar - δ := by linarith
  have hKδ : ∀ n, ∑ m ∈ range n, |cohortKernel qδ rδ m| ≤ q := by
    intro n
    simp only [hkδ]
    calc ∑ m ∈ range n, |q / 2 * (ηbar - δ) * (1 - (ηbar - δ)) ^ m + q / 2 * (ηbar + δ) * (1 - (ηbar + δ)) ^ m|
        ≤ ∑ m ∈ range n, (|q / 2 * (ηbar - δ) * (1 - (ηbar - δ)) ^ m| +
            |q / 2 * (ηbar + δ) * (1 - (ηbar + δ)) ^ m|) := sum_le_sum (fun m _ => abs_add_le _ _)
      _ ≤ q / 2 + q / 2 := by
          rw [sum_add_distrib]
          exact add_le_add (p1_single_kernel_l1 _ _ (by positivity) hη0 (by linarith) n)
            (p1_single_kernel_l1 _ _ (by positivity) (by linarith) (by linarith) n)
      _ = q := by ring
  have hK0 : ∀ n, ∑ m ∈ range n, |cohortKernel q0 r0 m| ≤ q := by
    intro n; simp only [hk0]
    exact p1_single_kernel_l1 _ _ hq (by linarith) (by linarith) n
  have hstab : |a| + |κ| * q ≤ s := by rw [abs_of_nonneg ha, abs_of_pos hκ]; exact hs
  have hH1 := p1_response_l1 a κ q s (cohortKernel q0 r0) h0f (p1_impulse_zero a κ q0 r0)
    (p1_impulse_closed_loop_recursion a κ q0 r0) hK0 hstab hs1
  have hE : ∀ n, ∑ m ∈ range n, |cohortKernel qδ rδ m - cohortKernel q0 r0 m| ≤ 2 * q * δ ^ 2 / ε ^ 3 := by
    intro n; simp only [hkδ, hk0]
    exact p1_split_kernel_gap q ηbar δ ε hq hε hδ.le hlo hhi n
  have hD := p1_response_diff_l1 a κ q s (2 * q * δ ^ 2 / ε ^ 3) (|κ| / (1 - s)) (cohortKernel qδ rδ)
    (cohortKernel q0 r0) hδf h0f (p1_impulse_zero a κ qδ rδ) (p1_impulse_zero a κ q0 r0)
    (p1_impulse_closed_loop_recursion a κ qδ rδ) (p1_impulse_closed_loop_recursion a κ q0 r0)
    hKδ hstab hs1 hE hH1
  set C := 2 * κ ^ 2 * q / (ε ^ 3 * (1 - s) ^ 2) with hC
  have hs1' : 0 < 1 - s := by linarith
  have hDval : |κ| * (2 * q * δ ^ 2 / ε ^ 3) * (|κ| / (1 - s)) / (1 - s) = C * δ ^ 2 := by
    rw [abs_of_pos hκ, hC]; field_simp
  rw [hDval] at hD
  have hen := p1_conv_energy (fun t => hδf t - h0f t) v (C * δ ^ 2) hD T
  -- the KL divergence of the two records
  have hkl := p1_test_error_kl_lower_bound _ _ hA herrδ herr0
  rw [gaussian_record_equal_variance_kl _ _ variance hv] at hkl
  have hdiff : ∀ t : Fin T, (controlledCohortRun a κ qδ rδ v (t.val + 1)).price -
      (controlledCohortRun a κ q0 r0 v (t.val + 1)).price =
      ∑ u ∈ range (t.val + 1), v u * (hδf (t.val - u) - h0f (t.val - u)) := by
    intro t
    rw [actual_reset_price_convolution, actual_reset_price_convolution, ← sum_sub_distrib]
    exact sum_congr rfl (fun u _ => by rw [mul_sub])
  simp only [hdiff] at hkl
  rw [Fin.sum_univ_eq_sum_range (fun t => (∑ u ∈ range (t + 1), v u * (hδf (t - u) - h0f (t - u))) ^ 2) T]
    at hkl
  have hvpos : (0 : ℝ) < variance := lt_of_le_of_ne variance.2 (by exact_mod_cast hv.symm)
  have hX0 : 0 ≤ (∑ t ∈ range T, (∑ u ∈ range (t + 1), v u * (hδf (t - u) - h0f (t - u))) ^ 2) /
      (2 * (variance : ℝ)) := by positivity
  rw [ENNReal.ofReal_le_ofReal_iff hX0, le_div_iff₀ (by positivity)] at hkl
  have hPT : (C * δ ^ 2) ^ 2 * ∑ t ∈ range T, v t ^ 2 ≤ (C * δ ^ 2) ^ 2 * (P * T) :=
    mul_le_mul_of_nonneg_left hP (sq_nonneg _)
  nlinarith [hen, hPT]

end CurrentMM
