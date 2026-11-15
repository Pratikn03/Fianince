import CurrentProofs.Paper1GeneralLevel
import CurrentProofs.Paper1Primitives
import Mathlib.Analysis.Calculus.MeanValue

/-!
# Paper 1, Propositions `prop:primitives` (S5.1) (ii) and `prop:tied` (S5.2) (ii): the composite lower bounds

* `p1_kalmanGain_lipschitz`: the steady-state Kalman gain `η(s) = (√(s²+4s) - s)/2` satisfies
  `|η(s) - η(s')| ≤ |s - s'|/s`, from the Riccati identity `η² + sη = s`.
* `p1_prop_primitives_lower_bound` (S5.1 (ii)): for Kalman desks whose signal-to-noise ratios lie in
  `s_c + Δs[-1, 1]` with `s_c - Δs ≥ s_lo > 0`, and whose gains form the `K = L + 1` matched pair of Theorem 5.1,
  any test with error probabilities `α, β` needs `4σ²(1-α-β)² ≤ N T (2 W 2^T (Δs/s_lo)^(2K-1) C_T)²`, that is
  `N ≥ c σ² (Δs)^-(4K-2)`. The spacing of the gains is bounded by the spacing of the ratios through the Lipschitz
  bound; nothing about the divergence is assumed.
* `p1_second_difference_le`: `|f(x+δ) + f(x-δ) - 2f(x)| ≤ 2 G δ²` when `|f''| ≤ G` on `[x-δ, x+δ]` (two applications
  of the mean value inequality).
* `p1_prop_tied_lower_bound` (S5.2 (ii)): one desk type at gain `η̄` with mass `2n` against two types at `η̄ ± δ` with
  mass `n` each, intensities tied to gains through a weight function `w`. If each tap function `g_m(η) = w(η)(1-η)^m`
  has `|g_m''| ≤ G` near `η̄` for `m < T` (a smoothness hypothesis on `w`, not on the divergence), any test needs
  `4σ²(1-α-β)² ≤ N T (2 n G δ² C_T)²`, that is `N ≥ c σ² δ^-4`.

Part (iii) of `prop:tied` (existence of a self-confirming configuration by Brouwer's theorem) is not formalized.
-/

namespace CurrentMM

open Finset MeasureTheory InformationTheory Real
open scoped ENNReal NNReal

/-- **Kalman gain is Lipschitz in the signal-to-noise ratio.** -/
theorem p1_kalmanGain_lipschitz (s s' : ℝ) (hs : 0 < s) (hs' : 0 < s') :
    |kalmanGain s - kalmanGain s'| ≤ |s - s'| / s := by
  have h1 := p1_kalmanGain_riccati_eq s hs.le
  have h2 := p1_kalmanGain_riccati_eq s' hs'.le
  have e0 := p1_kalmanGain_pos s hs
  have e0' := p1_kalmanGain_pos s' hs'
  have e1' := p1_kalmanGain_lt_one s' hs'
  set η := kalmanGain s
  set η' := kalmanGain s'
  have key : (η - η') * (η + η' + s) = (s - s') * (1 - η') := by linear_combination h1 - h2
  have hD : 0 < η + η' + s := by linarith
  have habs : |η - η'| * (η + η' + s) = |s - s'| * (1 - η') := by
    rw [← abs_of_pos hD, ← abs_mul, key, abs_mul, abs_of_pos (by linarith : (0 : ℝ) < 1 - η')]
  rw [le_div_iff₀ hs]
  calc |η - η'| * s ≤ |η - η'| * (η + η' + s) :=
        mul_le_mul_of_nonneg_left (by linarith) (abs_nonneg _)
    _ = |s - s'| * (1 - η') := habs
    _ ≤ |s - s'| := by nlinarith [abs_nonneg (s - s')]

theorem p1_gridNode_last (L : ℕ) : gridNode L (2 * L + 1) = 1 := by
  unfold gridNode
  have : (2 * (L : ℝ) + 1) ≠ 0 := by positivity
  push_cast
  field_simp
  ring

theorem p1_gridNode_zero (L : ℕ) : gridNode L 0 = -1 := by
  unfold gridNode; simp

/-- **Proposition `prop:primitives` (ii): the lower bound in signal-to-noise units.** -/
theorem p1_prop_primitives_lower_bound (L : ℕ) (a κ c d W H slo Δs sc : ℝ) (N T : ℕ)
    (q rate q' rate' snr snr' : Fin (L + 1) → ℝ) (variance : NNReal) (hv : variance ≠ 0)
    (hc : 0 ≤ c) (hd : 0 ≤ d) (hcd : c + d ≤ 1) (hH : 0 ≤ H) (hW : 0 ≤ W)
    (hslo : 0 < slo) (hwin : slo ≤ sc - Δs)
    (hsnr : ∀ i, |snr i - sc| ≤ Δs) (hsnr' : ∀ i, |snr' i - sc| ≤ Δs)
    (hgain : ∀ i, rate i = kalmanGain (snr i)) (hgain' : ∀ i, rate' i = kalmanGain (snr' i))
    (hr : ∀ i : Fin (L + 1), 1 - rate i = c + d * gridNode L (2 * i + 1))
    (hr' : ∀ i : Fin (L + 1), 1 - rate' i = c + d * gridNode L (2 * i))
    (hq : ∀ i : Fin (L + 1), q i * rate i = W * ((2 * L + 1).choose (2 * i + 1) : ℝ) / 2 ^ (2 * L))
    (hq' : ∀ i : Fin (L + 1), q' i * rate' i = W * ((2 * L + 1).choose (2 * i) : ℝ) / 2 ^ (2 * L))
    (hh' : ∀ t, t < T → |actualCohortImpulse a κ q' rate' t| ≤ H)
    (α₀ β₀ : ℝ) (hab : α₀ + β₀ ≤ 1) (A : Set (ObservationRecord (N * T))) (hA : MeasurableSet A)
    (herr0 : (gaussianRecordLaw (N * T) (p1RepeatedMean N T (actualCohortImpulse a κ q rate))
      variance).real A ≤ α₀)
    (herr1 : (gaussianRecordLaw (N * T) (p1RepeatedMean N T (actualCohortImpulse a κ q' rate'))
      variance).real Aᶜ ≤ β₀) :
    4 * (variance : ℝ) * (1 - α₀ - β₀) ^ 2 ≤
      N * T * ((2 * W * 2 ^ T * (Δs / slo) ^ (2 * L + 1)) * p1GapConst a |κ| W H T) ^ 2 := by
  have hmain := p1_thm_kcohort_lower_bound_every_K_general L a κ c d W H N T q rate q' rate' variance hv
    hc hd hcd hH hW hr hr' hq hq' hh' α₀ β₀ hab A hA herr0 herr1
  -- the gain spacing is at most the ratio spacing divided by `s_lo`
  have hL := hr (Fin.last L)
  have h0 := hr' 0
  rw [Fin.val_last, p1_gridNode_last] at hL
  simp only [Fin.val_zero, mul_zero, p1_gridNode_zero] at h0
  have hgap : rate' 0 - rate (Fin.last L) = 2 * d := by linarith
  have hb1 := hsnr (Fin.last L)
  have hb0 := hsnr' 0
  rw [abs_le] at hb1 hb0
  have hpos1 : 0 < snr (Fin.last L) := by linarith
  have hpos0 : 0 < snr' 0 := by linarith
  have hlip := p1_kalmanGain_lipschitz (snr (Fin.last L)) (snr' 0) hpos1 hpos0
  rw [← hgain, ← hgain'] at hlip
  have hsd : |snr (Fin.last L) - snr' 0| ≤ 2 * Δs := by rw [abs_le]; constructor <;> linarith
  have hratio : |snr (Fin.last L) - snr' 0| / snr (Fin.last L) ≤ 2 * Δs / slo :=
    div_le_div₀ (by linarith) hsd hslo (by linarith)
  have hgapabs : |rate (Fin.last L) - rate' 0| = 2 * d := by
    rw [abs_sub_comm, hgap, abs_of_nonneg (by linarith)]
  have hdle : d ≤ Δs / slo := by
    have h2 : 2 * d ≤ 2 * Δs / slo := by linarith
    rw [mul_div_assoc] at h2
    linarith
  have hpow : d ^ (2 * L + 1) ≤ (Δs / slo) ^ (2 * L + 1) := pow_le_pow_left₀ hd hdle _
  have hC0 : 0 ≤ p1GapConst a |κ| W H T := p1GapConst_nonneg a |κ| W H (abs_nonneg _) hW hH T
  have hinner : 0 ≤ (2 * W * 2 ^ T * d ^ (2 * L + 1)) * p1GapConst a |κ| W H T :=
    mul_nonneg (mul_nonneg (mul_nonneg (mul_nonneg (by norm_num) hW) (by positivity)) (pow_nonneg hd _)) hC0
  have hmono : (2 * W * 2 ^ T * d ^ (2 * L + 1)) * p1GapConst a |κ| W H T ≤
      (2 * W * 2 ^ T * (Δs / slo) ^ (2 * L + 1)) * p1GapConst a |κ| W H T := by
    apply mul_le_mul_of_nonneg_right _ hC0
    exact mul_le_mul_of_nonneg_left hpow (mul_nonneg (mul_nonneg (by norm_num) hW) (by positivity))
  have hsq := pow_le_pow_left₀ hinner hmono 2
  have hNT : (0 : ℝ) ≤ N * T := by positivity
  nlinarith [mul_le_mul_of_nonneg_left hsq hNT]

/-- **Second differences under a second-derivative bound.** -/
theorem p1_second_difference_le (f f' f'' : ℝ → ℝ) (x δ G : ℝ) (hδ : 0 ≤ δ)
    (hf : ∀ y, HasDerivAt f (f' y) y) (hf' : ∀ y, HasDerivAt f' (f'' y) y)
    (hG : ∀ y, |y - x| ≤ δ → |f'' y| ≤ G) :
    |f (x + δ) + f (x - δ) - 2 * f x| ≤ 2 * G * δ ^ 2 := by
  have hG0 : 0 ≤ G := le_trans (abs_nonneg _) (hG x (by simp; exact hδ))
  have step1 : ∀ t ∈ Set.Icc (0 : ℝ) δ, ‖f' (x + t) - f' (x - t)‖ ≤ 2 * G * δ := by
    intro t ht
    have hseg := norm_image_sub_le_of_norm_deriv_le_segment' (f := f') (f' := f'') (C := G)
      (a := x - t) (b := x + t)
      (fun y _ => (hf' y).hasDerivWithinAt)
      (fun y hy => by
        have hy' : |y - x| ≤ δ := by
          rw [abs_le]; constructor <;> linarith [hy.1, hy.2, ht.2]
        rw [Real.norm_eq_abs]; exact hG y hy')
      (x + t) ⟨by linarith [ht.1], le_refl _⟩
    calc ‖f' (x + t) - f' (x - t)‖ ≤ G * (x + t - (x - t)) := hseg
      _ = 2 * G * t := by ring
      _ ≤ 2 * G * δ := by nlinarith [ht.2]
  have hφ : ∀ t, HasDerivAt (fun t => f (x + t) + f (x - t) - 2 * f x) (f' (x + t) - f' (x - t)) t := by
    intro t
    have a1 : HasDerivAt (fun t => f (x + t)) (f' (x + t) * 1) t :=
      (hf (x + t)).comp t ((hasDerivAt_id t).const_add x)
    have a2 : HasDerivAt (fun t => f (x - t)) (f' (x - t) * (-1)) t :=
      (hf (x - t)).comp t ((hasDerivAt_id t).const_sub x)
    have h3 := (a1.add a2).sub_const (2 * f x)
    exact h3.congr_deriv (by ring)
  have hseg2 := norm_image_sub_le_of_norm_deriv_le_segment'
    (f := fun t => f (x + t) + f (x - t) - 2 * f x) (f' := fun t => f' (x + t) - f' (x - t))
    (C := 2 * G * δ) (a := 0) (b := δ)
    (fun t _ => (hφ t).hasDerivWithinAt) (fun t ht => step1 t ⟨ht.1, ht.2.le⟩) δ ⟨hδ, le_refl _⟩
  have h : |(f (x + δ) + f (x - δ) - 2 * f x) - (f (x + 0) + f (x - 0) - 2 * f x)| ≤ 2 * G * δ * (δ - 0) :=
    hseg2
  simp only [add_zero, sub_zero] at h
  have e : f (x + δ) + f (x - δ) - 2 * f x - (f x + f x - 2 * f x) = f (x + δ) + f (x - δ) - 2 * f x := by ring
  rw [e] at h
  nlinarith [h]

/-- **Proposition `prop:tied` (ii): known numbers of desks keep the `δ^-4` order.** -/
theorem p1_prop_tied_lower_bound (a κ n ηbar δ G H : ℝ) (w : ℝ → ℝ) (N T : ℕ)
    (qA rateA : Fin 1 → ℝ) (qB rateB : Fin 2 → ℝ) (variance : NNReal) (hv : variance ≠ 0)
    (hn : 0 ≤ n) (hδ : 0 ≤ δ) (hH : 0 ≤ H) (hG0 : 0 ≤ G) (hη0 : 0 ≤ ηbar) (hη1 : ηbar ≤ 1)
    (hrA : rateA 0 = ηbar) (hqA : qA 0 * rateA 0 = 2 * n * w ηbar)
    (hrB0 : rateB 0 = ηbar - δ) (hrB1 : rateB 1 = ηbar + δ)
    (hqB0 : qB 0 * rateB 0 = n * w (ηbar - δ)) (hqB1 : qB 1 * rateB 1 = n * w (ηbar + δ))
    (g g' g'' : ℕ → ℝ → ℝ) (hg : ∀ m y, g m y = w y * (1 - y) ^ m)
    (hgd : ∀ m y, HasDerivAt (g m) (g' m y) y) (hgd' : ∀ m y, HasDerivAt (g' m) (g'' m y) y)
    (hG : ∀ m, m < T → ∀ y, |y - ηbar| ≤ δ → |g'' m y| ≤ G)
    (hh' : ∀ t, t < T → |actualCohortImpulse a κ qB rateB t| ≤ H)
    (α₀ β₀ : ℝ) (hab : α₀ + β₀ ≤ 1) (A : Set (ObservationRecord (N * T))) (hA : MeasurableSet A)
    (herr0 : (gaussianRecordLaw (N * T) (p1RepeatedMean N T (actualCohortImpulse a κ qA rateA))
      variance).real A ≤ α₀)
    (herr1 : (gaussianRecordLaw (N * T) (p1RepeatedMean N T (actualCohortImpulse a κ qB rateB))
      variance).real Aᶜ ≤ β₀) :
    4 * (variance : ℝ) * (1 - α₀ - β₀) ^ 2 ≤
      N * T * ((n * (2 * G * δ ^ 2)) * p1GapConst a |κ| (2 * n * |w ηbar|) H T) ^ 2 := by
  have hk : ∀ j, cohortKernel qA rateA j - cohortKernel qB rateB j =
      -(n * (g j (ηbar + δ) + g j (ηbar - δ) - 2 * g j ηbar)) := by
    intro j
    simp only [cohortKernel, Fin.sum_univ_one, Fin.sum_univ_two, hg]
    rw [hqA, hqB0, hqB1, hrA, hrB0, hrB1]
    ring
  have hkA : ∀ j, |cohortKernel qA rateA j| ≤ 2 * n * |w ηbar| := by
    intro j
    simp only [cohortKernel, Fin.sum_univ_one]
    rw [hqA, hrA, abs_mul, abs_pow]
    have h1 : |1 - ηbar| ≤ 1 := by rw [abs_le]; constructor <;> linarith
    have h2 : |1 - ηbar| ^ j ≤ 1 := pow_le_one₀ (abs_nonneg _) h1
    have h3 : |2 * n * w ηbar| = 2 * n * |w ηbar| := by
      rw [abs_mul, abs_mul, abs_of_nonneg (by norm_num : (0 : ℝ) ≤ 2), abs_of_nonneg hn]
    rw [h3]
    have h4 : 0 ≤ 2 * n * |w ηbar| := mul_nonneg (mul_nonneg (by norm_num) hn) (abs_nonneg _)
    nlinarith
  have hgap : ∀ j, j < T → |cohortKernel qA rateA j - cohortKernel qB rateB j| ≤ n * (2 * G * δ ^ 2) := by
    intro j hj
    rw [hk, abs_neg, abs_mul, abs_of_nonneg hn]
    have hsd := p1_second_difference_le (g j) (g' j) (g'' j) ηbar δ G hδ (hgd j) (hgd' j) (hG j hj)
    exact mul_le_mul_of_nonneg_left hsd hn
  exact p1_thm_lower_bound_from_kernel_gap_general a κ (2 * n * |w ηbar|) H (n * (2 * G * δ ^ 2))
    (cohortKernel qA rateA) (cohortKernel qB rateB) (actualCohortImpulse a κ qA rateA)
    (actualCohortImpulse a κ qB rateB) N T variance hv (mul_nonneg (mul_nonneg (by norm_num) hn) (abs_nonneg _))
    hH (mul_nonneg hn (mul_nonneg (mul_nonneg (by norm_num) hG0) (sq_nonneg _)))
    (p1_impulse_zero a κ qA rateA) (p1_impulse_zero a κ qB rateB)
    (p1_impulse_closed_loop_recursion a κ qA rateA) (p1_impulse_closed_loop_recursion a κ qB rateB)
    hkA hh' hgap α₀ β₀ hab A hA herr0 herr1

end CurrentMM
