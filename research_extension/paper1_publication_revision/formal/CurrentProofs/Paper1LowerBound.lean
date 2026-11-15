import CurrentProofs.Paper1MergedModel
import CurrentProofs.Paper1MomentGap
import CurrentProofs.Paper1Testing
import Mathlib.Data.Nat.Choose.Bounds

/-!
# Paper 1, Theorem `thm:kcohort`: the lower bound end to end (finite horizon)

Chain proved here:
1. `p1_impulse_gap_finite_horizon`: kernels that differ by at most `ε` on `[0, T)` give price responses that differ
   by at most `ε · C_T` on `[0, T)` (closed loop, explicit constant `C_T`).
2. `p1_repeated_record_kl`: `N` independent reset experiments, each observing `T` taps with Gaussian noise of
   variance `σ²`, have divergence `N ∑_t (h_t - h'_t)² / (2σ²)`.
3. `p1_thm_lower_bound_from_kernel_gap`: with the testing step (`Paper1Testing.lean`), any test with both error
   probabilities at most `1/4` needs `σ² ≤ 2 N T (ε C_T)²`.
4. `p1_thm_kcohort_lower_bound_formal`: for cohort economies with memory rates `c + d s_i` whose weighted node
   moments agree below order `n`, `ε = 2 W 2^T d^n`, so `N ≥ σ² / (8 T W² 4^T C_T² d^(2n))`; with `n = 2K - 1`
   this is the `(Δη)^-(4K-2)` lower bound.
5. `p1_thm_twocohort_lower_bound_formal`: for `K = 2` the matched pair is exhibited explicitly (nodes `-1, 1/3` with
   weights `1/4, 3/4` against `-1/2, 2/3` with weights `4/7, 3/7`: equal moments of order 0, 1, 2), so the
   `(Δη)^-6` lower bound holds with no hypothesis on moment matching.
The constant depends on the observation horizon `T`; existence of a matched pair for general `K` (Gauss and
Gauss–Radau rules) remains a hypothesis.
-/

namespace CurrentMM

open Finset MeasureTheory InformationTheory
open scoped ENNReal NNReal

/-- Growth constant of the closed-loop error propagation. -/
noncomputable def p1GapConst (a K0 B H : ℝ) : ℕ → ℝ
  | 0 => 0
  | t + 1 => (1 + |a| + K0 * B * (t + 1)) * p1GapConst a K0 B H t + K0 * H * (t + 1)

theorem p1GapConst_nonneg (a K0 B H : ℝ) (hK0 : 0 ≤ K0) (hB : 0 ≤ B) (hH : 0 ≤ H) :
    ∀ t, 0 ≤ p1GapConst a K0 B H t := by
  intro t
  induction t with
  | zero => simp [p1GapConst]
  | succ t ih =>
    simp only [p1GapConst]
    have : 0 ≤ 1 + |a| + K0 * B * ((t : ℝ) + 1) := by positivity
    positivity

theorem p1GapConst_mono (a K0 B H : ℝ) (hK0 : 0 ≤ K0) (hB : 0 ≤ B) (hH : 0 ≤ H) (t : ℕ) :
    p1GapConst a K0 B H t ≤ p1GapConst a K0 B H (t + 1) := by
  have h0 := p1GapConst_nonneg a K0 B H hK0 hB hH t
  simp only [p1GapConst]
  have h1 : 0 ≤ |a| + K0 * B * ((t : ℝ) + 1) := by positivity
  have h2 : 0 ≤ K0 * H * ((t : ℝ) + 1) := by positivity
  nlinarith

/-- **Kernel gap ⇒ price-response gap**, on a finite horizon. -/
theorem p1_impulse_gap_finite_horizon (a κ B H ε : ℝ) (k k' h h' : ℕ → ℝ) (T : ℕ)
    (hB : 0 ≤ B) (hH : 0 ≤ H) (hε : 0 ≤ ε)
    (h0 : h 0 = κ) (h0' : h' 0 = κ)
    (hrec : ∀ t, h (t + 1) = a * h t + κ * ∑ j ∈ range (t + 1), k j * h (t - j))
    (hrec' : ∀ t, h' (t + 1) = a * h' t + κ * ∑ j ∈ range (t + 1), k' j * h' (t - j))
    (hkB : ∀ j, |k j| ≤ B) (hh' : ∀ s, s < T → |h' s| ≤ H)
    (hgap : ∀ j, j < T → |k j - k' j| ≤ ε) :
    ∀ t, t < T → |h t - h' t| ≤ ε * p1GapConst a |κ| B H t := by
  have hK0 : 0 ≤ |κ| := abs_nonneg κ
  have key : ∀ t, t < T → ∀ s, s ≤ t → |h s - h' s| ≤ ε * p1GapConst a |κ| B H t := by
    intro t
    induction t with
    | zero =>
      intro _ s hs
      have : s = 0 := by omega
      subst this
      simp [h0, h0', p1GapConst]
    | succ t ih =>
      intro htT s hs
      have ih' := ih (by omega)
      have hmono := p1GapConst_mono a |κ| B H hK0 hB hH t
      have hC0 := p1GapConst_nonneg a |κ| B H hK0 hB hH t
      rcases Nat.lt_or_ge s (t + 1) with hlt | hge
      · exact le_trans (ih' s (by omega)) (mul_le_mul_of_nonneg_left hmono hε)
      · have hst : s = t + 1 := by omega
        subst hst
        -- one step of the closed loop
        have hterm : ∀ j ∈ range (t + 1),
            |k j * h (t - j) - k' j * h' (t - j)| ≤ B * (ε * p1GapConst a |κ| B H t) + ε * H := by
          intro j hj
          have hj' : j ≤ t := Nat.lt_succ_iff.mp (mem_range.mp hj)
          have e : k j * h (t - j) - k' j * h' (t - j) =
              k j * (h (t - j) - h' (t - j)) + (k j - k' j) * h' (t - j) := by ring
          rw [e]
          have hD := ih' (t - j) (by omega)
          have hg := hgap j (by omega)
          have hhb := hh' (t - j) (by omega)
          calc |k j * (h (t - j) - h' (t - j)) + (k j - k' j) * h' (t - j)|
              ≤ |k j * (h (t - j) - h' (t - j))| + |(k j - k' j) * h' (t - j)| := abs_add_le _ _
            _ = |k j| * |h (t - j) - h' (t - j)| + |k j - k' j| * |h' (t - j)| := by
                rw [abs_mul, abs_mul]
            _ ≤ B * (ε * p1GapConst a |κ| B H t) + ε * H := by
                gcongr
                · exact hkB j
        have hsum : |∑ j ∈ range (t + 1), (k j * h (t - j) - k' j * h' (t - j))| ≤
            ((t : ℝ) + 1) * (B * (ε * p1GapConst a |κ| B H t) + ε * H) := by
          calc |∑ j ∈ range (t + 1), (k j * h (t - j) - k' j * h' (t - j))|
              ≤ ∑ j ∈ range (t + 1), |k j * h (t - j) - k' j * h' (t - j)| := abs_sum_le_sum_abs _ _
            _ ≤ ∑ j ∈ range (t + 1), (B * (ε * p1GapConst a |κ| B H t) + ε * H) := sum_le_sum hterm
            _ = ((t : ℝ) + 1) * (B * (ε * p1GapConst a |κ| B H t) + ε * H) := by
                rw [sum_const, card_range, nsmul_eq_mul]; push_cast; ring
        have hdiff : h (t + 1) - h' (t + 1) = a * (h t - h' t) +
            κ * ∑ j ∈ range (t + 1), (k j * h (t - j) - k' j * h' (t - j)) := by
          rw [hrec, hrec', sum_sub_distrib]; ring
        have hDt := ih' t le_rfl
        rw [hdiff]
        calc |a * (h t - h' t) + κ * ∑ j ∈ range (t + 1), (k j * h (t - j) - k' j * h' (t - j))|
            ≤ |a| * |h t - h' t| + |κ| * |∑ j ∈ range (t + 1), (k j * h (t - j) - k' j * h' (t - j))| := by
              rw [← abs_mul, ← abs_mul]; exact abs_add_le _ _
          _ ≤ |a| * (ε * p1GapConst a |κ| B H t) +
                |κ| * (((t : ℝ) + 1) * (B * (ε * p1GapConst a |κ| B H t) + ε * H)) := by
              gcongr
          _ ≤ ε * p1GapConst a |κ| B H (t + 1) := by
              simp only [p1GapConst]
              have hεC : 0 ≤ ε * p1GapConst a |κ| B H t := mul_nonneg hε hC0
              nlinarith [hεC]
  exact fun t ht => key t ht t le_rfl

/-- Mean vector of `N` independent reset experiments that each record taps `0, …, T-1`. -/
noncomputable def p1RepeatedMean (N T : ℕ) (h : ℕ → ℝ) : Fin (N * T) → ℝ :=
  fun i => h ((finProdFinEquiv.symm i).2 : ℕ)

/-- Divergence of `N` independent `T`-tap experiments. -/
theorem p1_repeated_record_kl (N T : ℕ) (h h' : ℕ → ℝ) (variance : ℝ≥0) (hv : variance ≠ 0) :
    klDiv (gaussianRecordLaw (N * T) (p1RepeatedMean N T h) variance)
        (gaussianRecordLaw (N * T) (p1RepeatedMean N T h') variance) =
      ENNReal.ofReal ((N : ℝ) * (∑ t ∈ range T, (h t - h' t) ^ 2) / (2 * (variance : ℝ))) := by
  rw [gaussian_record_equal_variance_kl _ _ variance hv]
  congr 2
  unfold p1RepeatedMean
  rw [← Fintype.sum_equiv finProdFinEquiv (fun p : Fin N × Fin T => (h (p.2 : ℕ) - h' (p.2 : ℕ)) ^ 2) _
    (fun p => by simp)]
  rw [Fintype.sum_prod_type]
  simp only [sum_const, card_univ, Fintype.card_fin, nsmul_eq_mul]
  rw [Fin.sum_univ_eq_sum_range (fun t => (h t - h' t) ^ 2)]

/-- **Testing lower bound from a kernel gap.** If the two economies' kernels differ by at most `ε` on `[0, T)`,
then any test from `N` experiments with both error probabilities at most `1/4` satisfies `σ² ≤ 2 N T (ε C_T)²`. -/
theorem p1_thm_lower_bound_from_kernel_gap (a κ B H ε : ℝ) (k k' h h' : ℕ → ℝ) (N T : ℕ)
    (variance : ℝ≥0) (hv : variance ≠ 0)
    (hB : 0 ≤ B) (hH : 0 ≤ H) (hε : 0 ≤ ε)
    (h0 : h 0 = κ) (h0' : h' 0 = κ)
    (hrec : ∀ t, h (t + 1) = a * h t + κ * ∑ j ∈ range (t + 1), k j * h (t - j))
    (hrec' : ∀ t, h' (t + 1) = a * h' t + κ * ∑ j ∈ range (t + 1), k' j * h' (t - j))
    (hkB : ∀ j, |k j| ≤ B) (hh' : ∀ s, s < T → |h' s| ≤ H)
    (hgap : ∀ j, j < T → |k j - k' j| ≤ ε)
    (A : Set (ObservationRecord (N * T))) (hA : MeasurableSet A)
    (herr0 : (gaussianRecordLaw (N * T) (p1RepeatedMean N T h) variance).real A ≤ 1 / 4)
    (herr1 : (gaussianRecordLaw (N * T) (p1RepeatedMean N T h') variance).real Aᶜ ≤ 1 / 4) :
    (variance : ℝ) ≤ 2 * N * T * (ε * p1GapConst a |κ| B H T) ^ 2 := by
  have hvpos : 0 < (variance : ℝ) := by positivity
  have htest := p1_test_error_kl_lower_bound _ _ hA herr0 herr1
  rw [p1_repeated_record_kl N T h h' variance hv] at htest
  have hgapT := p1_impulse_gap_finite_horizon a κ B H ε k k' h h' T hB hH hε h0 h0' hrec hrec' hkB hh' hgap
  have hK0 : 0 ≤ |κ| := abs_nonneg κ
  have hCT : ∀ t, t < T → |h t - h' t| ≤ ε * p1GapConst a |κ| B H T := by
    intro t ht
    have hmono : ∀ u v, u ≤ v → p1GapConst a |κ| B H u ≤ p1GapConst a |κ| B H v := by
      intro u v huv
      induction v with
      | zero => have : u = 0 := by omega
                subst this; exact le_rfl
      | succ v ihv =>
        rcases Nat.lt_or_ge u (v + 1) with h1 | h1
        · exact le_trans (ihv (by omega)) (p1GapConst_mono a |κ| B H hK0 hB hH v)
        · have : u = v + 1 := by omega
          subst this; exact le_rfl
    exact le_trans (hgapT t ht) (mul_le_mul_of_nonneg_left (hmono t T ht.le) hε)
  have hsq : ∑ t ∈ range T, (h t - h' t) ^ 2 ≤ T * (ε * p1GapConst a |κ| B H T) ^ 2 := by
    calc ∑ t ∈ range T, (h t - h' t) ^ 2 ≤ ∑ t ∈ range T, (ε * p1GapConst a |κ| B H T) ^ 2 := by
          refine sum_le_sum (fun t ht => ?_)
          have := hCT t (mem_range.mp ht)
          rw [← sq_abs]
          exact pow_le_pow_left₀ (abs_nonneg _) this 2
      _ = T * (ε * p1GapConst a |κ| B H T) ^ 2 := by rw [sum_const, card_range, nsmul_eq_mul]
  have hle := (ENNReal.ofReal_le_ofReal_iff (by positivity)).mp htest
  rw [le_div_iff₀ (by positivity)] at hle
  have hN : (0 : ℝ) ≤ N := Nat.cast_nonneg N
  nlinarith [mul_le_mul_of_nonneg_left hsq hN]

/-- Kernel bound for a cohort population with memory rates in `[-1, 1]` and total absolute weight `W`. -/
theorem p1_mg_kernel_abs_le {ι : Type*} (S : Finset ι) (w s : ι → ℝ) (c d W : ℝ) (m : ℕ)
    (hc : 0 ≤ c) (hd : 0 ≤ d) (hcd : c + d ≤ 1)
    (hw : ∀ i ∈ S, 0 ≤ w i) (hs : ∀ i ∈ S, |s i| ≤ 1) (hW : ∑ i ∈ S, w i ≤ W) :
    |mgKernel S w s c d m| ≤ W := by
  unfold mgKernel
  calc |∑ i ∈ S, w i * (c + d * s i) ^ m| ≤ ∑ i ∈ S, |w i * (c + d * s i) ^ m| := abs_sum_le_sum_abs _ _
    _ ≤ ∑ i ∈ S, w i := by
        refine sum_le_sum (fun i hi => ?_)
        rw [abs_mul, abs_of_nonneg (hw i hi), abs_pow]
        have hb : |c + d * s i| ≤ 1 := by
          have := hs i hi
          rw [abs_le] at this ⊢
          constructor <;> nlinarith
        have h1 : |c + d * s i| ^ m ≤ 1 := pow_le_one₀ (abs_nonneg _) hb
        nlinarith [hw i hi]
    _ ≤ W := hW

/-- Kernel gap for moment-matched populations, uniformly on `[0, T)`: `|Δk_m| ≤ 2 W 2^T d^n`. -/
theorem p1_mg_kernel_gap_uniform {ι κ : Type*} (S : Finset ι) (T' : Finset κ)
    (w s : ι → ℝ) (w' s' : κ → ℝ) (c d W : ℝ) (n T : ℕ)
    (hc : 0 ≤ c) (hd : 0 ≤ d) (hcd : c + d ≤ 1)
    (hw : ∀ i ∈ S, 0 ≤ w i) (hw' : ∀ i ∈ T', 0 ≤ w' i)
    (hs : ∀ i ∈ S, |s i| ≤ 1) (hs' : ∀ i ∈ T', |s' i| ≤ 1)
    (hW : ∑ i ∈ S, w i ≤ W) (hW' : ∑ i ∈ T', w' i ≤ W)
    (hmom : ∀ j < n, mgMoment S w s j = mgMoment T' w' s' j) :
    ∀ m, m < T → |mgKernel S w s c d m - mgKernel T' w' s' c d m| ≤ 2 * W * 2 ^ T * d ^ n := by
  intro m hm
  have hW0 : 0 ≤ W := le_trans (sum_nonneg hw) hW
  rcases Nat.lt_or_ge m n with hmn | hnm
  · rw [p1_thm_kcohort_kernel_low_orders_equal S T' w s w' s' c d n m hmom hmn, sub_self, abs_zero]
    positivity
  · refine le_trans (p1_thm_kcohort_kernel_moment_gap S T' w s w' s' c d W n m hc hd hw hw' hs hs' hW hW'
      hmom hnm) ?_
    have hch : (m.choose n : ℝ) ≤ 2 ^ T := by
      have h1 : m.choose n ≤ 2 ^ m := Nat.choose_le_two_pow m n
      have h2 : 2 ^ m ≤ 2 ^ T := Nat.pow_le_pow_right (by norm_num) hm.le
      exact_mod_cast le_trans h1 h2
    have hpow : (c + d) ^ (m - n) ≤ 1 := pow_le_one₀ (by positivity) hcd
    have hdn : 0 ≤ d ^ n := pow_nonneg hd n
    calc 2 * W * ((m.choose n : ℝ) * d ^ n * (c + d) ^ (m - n))
        ≤ 2 * W * (2 ^ T * d ^ n * 1) := by gcongr
      _ = 2 * W * 2 ^ T * d ^ n := by ring

/-- The cohort kernel written in the moment-gap coordinates. -/
theorem p1_cohortKernel_eq_mgKernel {n : ℕ} (q rate s : Fin n → ℝ) (c d : ℝ)
    (hr : ∀ i, 1 - rate i = c + d * s i) (m : ℕ) :
    cohortKernel q rate m = mgKernel univ (fun i => q i * rate i) s c d m := by
  unfold cohortKernel mgKernel
  refine sum_congr rfl (fun i _ => ?_)
  rw [hr i]

/-- **`thm:kcohort`, formal finite-horizon version.** Two cohort economies with known `a`, `κ`, memory rates
`1 - η_i = c + d s_i` (`|s_i| ≤ 1`), nonnegative merged weights `q_i η_i` of total at most `W`, and weighted node
moments that agree below order `n`. If the second economy's price response is bounded by `H` on `[0, T)`, any test
from `N` reset experiments of `T` taps with noise variance `σ²` and both errors at most `1/4` satisfies
`σ² ≤ 8 N T W² 4^T C_T² d^(2n)`, i.e. `N ≥ σ² d^-(2n) / (8 T W² 4^T C_T²)`. -/
theorem p1_thm_kcohort_lower_bound_formal {n0 n1 : ℕ} (a κ c d W H : ℝ) (nmatch N T : ℕ)
    (q rate s : Fin n0 → ℝ) (q' rate' s' : Fin n1 → ℝ) (variance : ℝ≥0) (hv : variance ≠ 0)
    (hc : 0 ≤ c) (hd : 0 ≤ d) (hcd : c + d ≤ 1) (hH : 0 ≤ H)
    (hr : ∀ i, 1 - rate i = c + d * s i) (hr' : ∀ i, 1 - rate' i = c + d * s' i)
    (hs : ∀ i, |s i| ≤ 1) (hs' : ∀ i, |s' i| ≤ 1)
    (hw : ∀ i, 0 ≤ q i * rate i) (hw' : ∀ i, 0 ≤ q' i * rate' i)
    (hW : ∑ i, q i * rate i ≤ W) (hW' : ∑ i, q' i * rate' i ≤ W)
    (hmom : ∀ j < nmatch, mgMoment univ (fun i => q i * rate i) s j =
      mgMoment univ (fun i => q' i * rate' i) s' j)
    (hh' : ∀ t, t < T → |actualCohortImpulse a κ q' rate' t| ≤ H)
    (A : Set (ObservationRecord (N * T))) (hA : MeasurableSet A)
    (herr0 : (gaussianRecordLaw (N * T) (p1RepeatedMean N T (actualCohortImpulse a κ q rate))
      variance).real A ≤ 1 / 4)
    (herr1 : (gaussianRecordLaw (N * T) (p1RepeatedMean N T (actualCohortImpulse a κ q' rate'))
      variance).real Aᶜ ≤ 1 / 4) :
    (variance : ℝ) ≤ 2 * N * T * ((2 * W * 2 ^ T * d ^ nmatch) * p1GapConst a |κ| W H T) ^ 2 := by
  have hW0 : 0 ≤ W := le_trans (sum_nonneg (fun i _ => hw i)) hW
  refine p1_thm_lower_bound_from_kernel_gap a κ W H (2 * W * 2 ^ T * d ^ nmatch)
    (cohortKernel q rate) (cohortKernel q' rate') (actualCohortImpulse a κ q rate)
    (actualCohortImpulse a κ q' rate') N T variance hv hW0 hH (by positivity)
    (p1_impulse_zero a κ q rate) (p1_impulse_zero a κ q' rate')
    (p1_impulse_closed_loop_recursion a κ q rate) (p1_impulse_closed_loop_recursion a κ q' rate')
    (fun j => by
      rw [p1_cohortKernel_eq_mgKernel q rate s c d hr]
      exact p1_mg_kernel_abs_le univ _ s c d W j hc hd hcd (fun i _ => hw i) (fun i _ => hs i) hW)
    hh' (fun j hj => by
      rw [p1_cohortKernel_eq_mgKernel q rate s c d hr, p1_cohortKernel_eq_mgKernel q' rate' s' c d hr']
      exact p1_mg_kernel_gap_uniform univ univ _ s _ s' c d W nmatch T hc hd hcd (fun i _ => hw i)
        (fun i _ => hw' i) (fun i _ => hs i) (fun i _ => hs' i) hW hW' hmom j hj)
    A hA herr0 herr1

/-- Two-cohort matched pair: nodes `(-1, 1/3)` with weights `(1/4, 3/4)` and nodes `(-1/2, 2/3)` with weights
`(4/7, 3/7)` have equal moments of orders `0, 1, 2` (and different third moments, `-2/9` against `1/18`). -/
theorem p1_twocohort_matched_pair (W : ℝ) :
    ∀ j < 3, mgMoment univ (fun i : Fin 2 => W * ![1 / 4, 3 / 4] i) ![-1, 1 / 3] j =
      mgMoment univ (fun i : Fin 2 => W * ![4 / 7, 3 / 7] i) ![-1 / 2, 2 / 3] j := by
  intro j hj
  interval_cases j <;> simp [mgMoment, Fin.sum_univ_two] <;> ring

theorem p1_twocohort_third_moments_differ (W : ℝ) (hW : W ≠ 0) :
    mgMoment univ (fun i : Fin 2 => W * ![1 / 4, 3 / 4] i) ![-1, 1 / 3] 3 ≠
      mgMoment univ (fun i : Fin 2 => W * ![4 / 7, 3 / 7] i) ![-1 / 2, 2 / 3] 3 := by
  simp only [mgMoment, Fin.sum_univ_two]
  norm_num
  intro h
  apply hW
  linarith

/-- **`thm:twocohort` / `thm:kcohort` for `K = 2`, with no matching hypothesis.** For the explicit pair above,
placed at memory rates `c + d s` with merged weights `W · (weights)`, every test from `N` reset experiments of `T`
taps with both errors at most `1/4` satisfies `σ² ≤ 8 N T W² 4^T C_T² d^6`, so `N ≥ σ² d^-6 / (8 T W² 4^T C_T²)`. -/
theorem p1_thm_twocohort_lower_bound_formal (a κ c d W H : ℝ) (N T : ℕ)
    (q rate q' rate' : Fin 2 → ℝ) (variance : ℝ≥0) (hv : variance ≠ 0)
    (hc : 0 ≤ c) (hd : 0 ≤ d) (hcd : c + d ≤ 1) (hH : 0 ≤ H) (hW : 0 ≤ W)
    (hr : ∀ i, 1 - rate i = c + d * ![-1, 1 / 3] i) (hr' : ∀ i, 1 - rate' i = c + d * ![-1 / 2, 2 / 3] i)
    (hq : ∀ i, q i * rate i = W * ![1 / 4, 3 / 4] i) (hq' : ∀ i, q' i * rate' i = W * ![4 / 7, 3 / 7] i)
    (hh' : ∀ t, t < T → |actualCohortImpulse a κ q' rate' t| ≤ H)
    (A : Set (ObservationRecord (N * T))) (hA : MeasurableSet A)
    (herr0 : (gaussianRecordLaw (N * T) (p1RepeatedMean N T (actualCohortImpulse a κ q rate))
      variance).real A ≤ 1 / 4)
    (herr1 : (gaussianRecordLaw (N * T) (p1RepeatedMean N T (actualCohortImpulse a κ q' rate'))
      variance).real Aᶜ ≤ 1 / 4) :
    (variance : ℝ) ≤ 2 * N * T * ((2 * W * 2 ^ T * d ^ 3) * p1GapConst a |κ| W H T) ^ 2 := by
  have hw : ∀ i, 0 ≤ q i * rate i := fun i => by
    rw [hq i]; fin_cases i <;> simp <;> positivity
  have hw' : ∀ i, 0 ≤ q' i * rate' i := fun i => by
    rw [hq' i]; fin_cases i <;> simp <;> positivity
  have hsum : ∑ i, q i * rate i ≤ W := by
    simp only [hq, Fin.sum_univ_two]; norm_num; linarith
  have hsum' : ∑ i, q' i * rate' i ≤ W := by
    simp only [hq', Fin.sum_univ_two]; norm_num; linarith
  refine p1_thm_kcohort_lower_bound_formal a κ c d W H 3 N T q rate ![-1, 1 / 3] q' rate'
    ![-1 / 2, 2 / 3] variance hv hc hd hcd hH hr hr'
    (fun i => by fin_cases i <;> norm_num [abs_le])
    (fun i => by fin_cases i <;> norm_num [abs_le]) hw hw' hsum hsum'
    (fun j hj => by
      have e1 : (fun i => q i * rate i) = (fun i : Fin 2 => W * ![1 / 4, 3 / 4] i) := funext hq
      have e2 : (fun i => q' i * rate' i) = (fun i : Fin 2 => W * ![4 / 7, 3 / 7] i) := funext hq'
      rw [e1, e2]; exact p1_twocohort_matched_pair W j hj)
    hh' A hA herr0 herr1

end CurrentMM
