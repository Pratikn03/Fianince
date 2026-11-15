import CurrentProofs.Paper1GeneralLevel

/-!
# Paper 1: the partial-disclosure lower bound, with tagged flow records (core `thm:partial`(i))

The supervisor records, in each of `N` reset experiments, the price impulse response for `T` dates and the flow
impulse response of each of `M` tagged groups for `T` dates. A tagged group with merged weight `w` and memory rate
`r` has flow response `f_u = w ∑_{s ≤ u} r^(u-s) h_s`, a fixed linear map of the price response `h`.

* `p1_tagged_flow_gap`: if the price responses differ by at most `G` on the first `T` dates and `|r| ≤ 1`, a tagged
  flow response differs by at most `|w| T G` there.
* `p1_joint_mean_gap`: every coordinate of the joint record (prices, then the `M` tagged flows) differs by at most
  `G (1 + W_t T)`.
* `p1_partial_lower_bound_joint`: for any test with errors `α₀, β₀` on the joint records,
  `4σ²(1 - α₀ - β₀)² ≤ N (T + M T) (ε C_T (1 + W_t T))²`, where `ε` bounds the kernel gap. With the tagged groups
  common to both economies, the kernel gap is the untagged gap (`p1_partial_kernel_gap`), of order `Δη^(2K'-1)`
  for the `K'`-node matched pair (`p1_mg_kernel_gap_uniform`), so `N ≥ c Δη^-(4K'-2)`.
-/

namespace CurrentMM

open Finset MeasureTheory ProbabilityTheory InformationTheory Real
open scoped ENNReal NNReal

/-- Flow impulse response of a tagged group with merged weight `w` and memory rate `r`. -/
def taggedFlowImpulse (w r : ℝ) (h : ℕ → ℝ) (u : ℕ) : ℝ :=
  w * ∑ s ∈ range (u + 1), r ^ (u - s) * h s

theorem p1_tagged_flow_gap (w r G : ℝ) (h h' : ℕ → ℝ) (T : ℕ) (hr : |r| ≤ 1) (hG0 : 0 ≤ G)
    (hG : ∀ s, s < T → |h s - h' s| ≤ G) (u : ℕ) (hu : u < T) :
    |taggedFlowImpulse w r h u - taggedFlowImpulse w r h' u| ≤ |w| * (T * G) := by
  unfold taggedFlowImpulse
  rw [← mul_sub, ← sum_sub_distrib, abs_mul]
  apply mul_le_mul_of_nonneg_left _ (abs_nonneg w)
  calc |∑ s ∈ range (u + 1), (r ^ (u - s) * h s - r ^ (u - s) * h' s)|
      ≤ ∑ s ∈ range (u + 1), |r ^ (u - s) * h s - r ^ (u - s) * h' s| := abs_sum_le_sum_abs _ _
    _ ≤ ∑ s ∈ range (u + 1), G := by
        refine sum_le_sum (fun s hs => ?_)
        rw [← mul_sub, abs_mul, abs_pow]
        have hs' : s < T := lt_of_le_of_lt (Nat.lt_succ_iff.mp (mem_range.mp hs)) hu
        have h1 : |r| ^ (u - s) ≤ 1 := pow_le_one₀ (abs_nonneg r) hr
        calc |r| ^ (u - s) * |h s - h' s| ≤ 1 * G :=
              mul_le_mul h1 (hG s hs') (abs_nonneg _) zero_le_one
          _ = G := one_mul G
    _ = (u + 1) * G := by rw [sum_const, card_range, nsmul_eq_mul]; push_cast; ring
    _ ≤ T * G := by
        apply mul_le_mul_of_nonneg_right _ hG0
        exact_mod_cast hu

/-- Joint record mean: the price response on dates `0..T-1`, then tagged group `k`'s flow response on dates
`T + k T + u`, `u < T`. -/
def jointMean (T : ℕ) (h : ℕ → ℝ) (wt rt : ℕ → ℝ) (t : ℕ) : ℝ :=
  if t < T then h t else taggedFlowImpulse (wt ((t - T) / T)) (rt ((t - T) / T)) h ((t - T) % T)

theorem p1_joint_mean_gap (T M : ℕ) (h h' : ℕ → ℝ) (wt rt : ℕ → ℝ) (G Wt : ℝ) (hG0 : 0 ≤ G) (hW : 0 ≤ Wt)
    (hT : 0 < T) (hG : ∀ s, s < T → |h s - h' s| ≤ G)
    (hwt : ∀ k, k < M → |wt k| ≤ Wt) (hrt : ∀ k, k < M → |rt k| ≤ 1) (t : ℕ) (ht : t < T + M * T) :
    |jointMean T h wt rt t - jointMean T h' wt rt t| ≤ G * (1 + Wt * T) := by
  unfold jointMean
  by_cases h1 : t < T
  · simp only [h1, ite_true]
    have := hG t h1
    nlinarith [mul_nonneg hW (Nat.cast_nonneg T : (0 : ℝ) ≤ T), mul_nonneg hG0 (mul_nonneg hW (Nat.cast_nonneg T : (0 : ℝ) ≤ T))]
  · simp only [h1, ite_false]
    have hk : (t - T) / T < M := by
      rw [Nat.div_lt_iff_lt_mul hT]; omega
    have hu : (t - T) % T < T := Nat.mod_lt _ hT
    have hf := p1_tagged_flow_gap (wt ((t - T) / T)) (rt ((t - T) / T)) G h h' T (hrt _ hk) hG0 hG _ hu
    have hw := hwt _ hk
    calc _ ≤ |wt ((t - T) / T)| * (T * G) := hf
      _ ≤ Wt * (T * G) := mul_le_mul_of_nonneg_right hw (by positivity)
      _ ≤ G * (1 + Wt * T) := by nlinarith [mul_nonneg hW (Nat.cast_nonneg T : (0 : ℝ) ≤ T)]

/-- **Partial-disclosure lower bound on joint records.** -/
theorem p1_partial_lower_bound_joint (a κ B H ε Wt : ℝ) (k k' h h' : ℕ → ℝ) (N T M : ℕ)
    (wt rt : ℕ → ℝ) (variance : ℝ≥0) (hv : variance ≠ 0) (hT : 0 < T) (hWt : 0 ≤ Wt)
    (hB : 0 ≤ B) (hH : 0 ≤ H) (hε : 0 ≤ ε)
    (h0 : h 0 = κ) (h0' : h' 0 = κ)
    (hrec : ∀ t, h (t + 1) = a * h t + κ * ∑ j ∈ range (t + 1), k j * h (t - j))
    (hrec' : ∀ t, h' (t + 1) = a * h' t + κ * ∑ j ∈ range (t + 1), k' j * h' (t - j))
    (hkB : ∀ j, |k j| ≤ B) (hh' : ∀ s, s < T → |h' s| ≤ H)
    (hgap : ∀ j, j < T → |k j - k' j| ≤ ε)
    (hwt : ∀ i, i < M → |wt i| ≤ Wt) (hrt : ∀ i, i < M → |rt i| ≤ 1)
    (α₀ β₀ : ℝ) (hab : α₀ + β₀ ≤ 1) (A : Set (ObservationRecord (N * (T + M * T)))) (hA : MeasurableSet A)
    (herr0 : (gaussianRecordLaw (N * (T + M * T)) (p1RepeatedMean N (T + M * T) (jointMean T h wt rt))
      variance).real A ≤ α₀)
    (herr1 : (gaussianRecordLaw (N * (T + M * T)) (p1RepeatedMean N (T + M * T) (jointMean T h' wt rt))
      variance).real Aᶜ ≤ β₀) :
    4 * (variance : ℝ) * (1 - α₀ - β₀) ^ 2 ≤
      N * (T + M * T) * (ε * p1GapConst a |κ| B H T * (1 + Wt * T)) ^ 2 := by
  have hvpos : 0 < (variance : ℝ) := by positivity
  have htest := p1_test_error_kl_lower_bound_general _ _ hA α₀ β₀ hab herr0 herr1
  rw [p1_repeated_record_kl N (T + M * T) _ _ variance hv] at htest
  have hgapT := p1_impulse_gap_finite_horizon a κ B H ε k k' h h' T hB hH hε h0 h0' hrec hrec' hkB hh' hgap
  have hK0 : 0 ≤ |κ| := abs_nonneg κ
  set G := ε * p1GapConst a |κ| B H T with hGdef
  have hG0 : 0 ≤ G := mul_nonneg hε (p1GapConst_nonneg a |κ| B H hK0 hB hH T)
  have hCT : ∀ t, t < T → |h t - h' t| ≤ G := by
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
  have hpt : ∀ t, t < T + M * T → (jointMean T h wt rt t - jointMean T h' wt rt t) ^ 2 ≤ (G * (1 + Wt * T)) ^ 2 := by
    intro t ht
    have := p1_joint_mean_gap T M h h' wt rt G Wt hG0 hWt hT hCT hwt hrt t ht
    rw [← sq_abs]
    exact pow_le_pow_left₀ (abs_nonneg _) this 2
  have hsq : ∑ t ∈ range (T + M * T), (jointMean T h wt rt t - jointMean T h' wt rt t) ^ 2 ≤
      (T + M * T : ℕ) * (G * (1 + Wt * T)) ^ 2 := by
    calc _ ≤ ∑ t ∈ range (T + M * T), (G * (1 + Wt * T)) ^ 2 :=
          sum_le_sum (fun t ht => hpt t (mem_range.mp ht))
      _ = _ := by rw [sum_const, card_range, nsmul_eq_mul]
  have hle := (ENNReal.ofReal_le_ofReal_iff (by positivity)).mp htest
  rw [le_div_iff₀ (by positivity)] at hle
  have hN : (0 : ℝ) ≤ N := Nat.cast_nonneg N
  push_cast at hsq ⊢
  nlinarith [mul_le_mul_of_nonneg_left hsq hN]

/-- **Partial disclosure, matched untagged pair.** The two economies share a tagged kernel `kt` (any sequence) and
their untagged groups have node moments that agree below order `n` (for the `K'`-node pair, `n = 2K' - 1`). Then on
joint records `4σ²(1 - α₀ - β₀)² ≤ N (T + M T) ((2 W 2^T d^n) C_T (1 + W_t T))²`: the data needed grow like
`d^-(2n)`, set by the untagged groups alone. -/
theorem p1_partial_lower_bound_matched {ι ι' : Type*} (S : Finset ι) (S' : Finset ι')
    (w s : ι → ℝ) (w' s' : ι' → ℝ) (kt : ℕ → ℝ)
    (a κ B H c d W Wt : ℝ) (k k' h h' : ℕ → ℝ) (N T M n : ℕ)
    (wt rt : ℕ → ℝ) (variance : ℝ≥0) (hv : variance ≠ 0) (hT : 0 < T) (hWt : 0 ≤ Wt)
    (hB : 0 ≤ B) (hH : 0 ≤ H) (hc : 0 ≤ c) (hd : 0 ≤ d) (hcd : c + d ≤ 1)
    (hw : ∀ i ∈ S, 0 ≤ w i) (hw' : ∀ i ∈ S', 0 ≤ w' i)
    (hs : ∀ i ∈ S, |s i| ≤ 1) (hs' : ∀ i ∈ S', |s' i| ≤ 1)
    (hW : ∑ i ∈ S, w i ≤ W) (hW' : ∑ i ∈ S', w' i ≤ W)
    (hmom : ∀ j < n, mgMoment S w s j = mgMoment S' w' s' j)
    (hk : ∀ m, k m = kt m + mgKernel S w s c d m) (hk' : ∀ m, k' m = kt m + mgKernel S' w' s' c d m)
    (h0 : h 0 = κ) (h0' : h' 0 = κ)
    (hrec : ∀ t, h (t + 1) = a * h t + κ * ∑ j ∈ range (t + 1), k j * h (t - j))
    (hrec' : ∀ t, h' (t + 1) = a * h' t + κ * ∑ j ∈ range (t + 1), k' j * h' (t - j))
    (hkB : ∀ j, |k j| ≤ B) (hh' : ∀ s, s < T → |h' s| ≤ H)
    (hwt : ∀ i, i < M → |wt i| ≤ Wt) (hrt : ∀ i, i < M → |rt i| ≤ 1)
    (α₀ β₀ : ℝ) (hab : α₀ + β₀ ≤ 1) (A : Set (ObservationRecord (N * (T + M * T)))) (hA : MeasurableSet A)
    (herr0 : (gaussianRecordLaw (N * (T + M * T)) (p1RepeatedMean N (T + M * T) (jointMean T h wt rt))
      variance).real A ≤ α₀)
    (herr1 : (gaussianRecordLaw (N * (T + M * T)) (p1RepeatedMean N (T + M * T) (jointMean T h' wt rt))
      variance).real Aᶜ ≤ β₀) :
    4 * (variance : ℝ) * (1 - α₀ - β₀) ^ 2 ≤
      N * (T + M * T) * ((2 * W * 2 ^ T * d ^ n) * p1GapConst a |κ| B H T * (1 + Wt * T)) ^ 2 := by
  have hW0 : 0 ≤ W := le_trans (sum_nonneg hw) hW
  refine p1_partial_lower_bound_joint a κ B H (2 * W * 2 ^ T * d ^ n) Wt k k' h h' N T M wt rt variance hv hT hWt
    hB hH (by positivity) h0 h0' hrec hrec' hkB hh' (fun j hj => ?_) hwt hrt α₀ β₀ hab A hA herr0 herr1
  have hsplit : k j - k' j = mgKernel S w s c d j - mgKernel S' w' s' c d j := by rw [hk j, hk' j]; ring
  rw [hsplit]
  exact p1_mg_kernel_gap_uniform S S' w s w' s' c d W n T hc hd hcd hw hw' hs hs' hW hW' hmom j hj

end CurrentMM
