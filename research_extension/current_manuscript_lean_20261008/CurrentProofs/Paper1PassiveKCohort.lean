import CurrentProofs.Paper1PassiveCost
import CurrentProofs.Paper1MatchedPair
import Mathlib.Analysis.SpecificLimits.Normed

/-!
# Paper 1, Theorem 5.8 (iii): passive data for `K` cohorts cost `T = Ω((Δη)^{-(4K-2)})`

* `p1_binom_tail`: `∑_{j ≥ J} C(m,j) a^{m-j} b^j ≤ C(m,J) b^J (a+b)^{m-J}`;
* `p1_matched_kernel_gap`: populations with equal moments below order `J` have kernels within
  `2W C(m,J) d^J λ^{m-J}` at lag `m` (`λ = |c| + d`), and `0` below lag `J`;
* `p1_matched_kernel_gap_l1`: summed over all lags, at most `2W d^J / (1-λ)^{J+1}`, independent of the horizon
  (Mathlib's negative-binomial series);
* `p1_thm_passive_cost_every_K`: for the binomial moment-matched pair with `K = L + 1` cohorts each, passive
  observation of `T` prices after any warm-up needs `T ≥ 1 / (2 (1+s)² (C d^(2K-1))²)`.
-/

namespace CurrentMM

open MeasureTheory ProbabilityTheory InformationTheory Finset
open scoped ENNReal NNReal

theorem p1_binom_tail (a b : ℝ) (ha : 0 ≤ a) (hb : 0 ≤ b) (m J : ℕ) (hJ : J ≤ m) :
    ∑ j ∈ Ico J (m + 1), (m.choose j : ℝ) * a ^ (m - j) * b ^ j ≤
      (m.choose J : ℝ) * b ^ J * (a + b) ^ (m - J) := by
  have hterm : ∀ j ∈ Ico J (m + 1), (m.choose j : ℝ) * a ^ (m - j) * b ^ j ≤
      (m.choose J : ℝ) * b ^ J * (((m - J).choose (j - J) : ℝ) * a ^ (m - J - (j - J)) * b ^ (j - J)) := by
    intro j hj
    have hj' := mem_Ico.mp hj
    have hc : (m.choose j : ℝ) ≤ (m.choose J : ℝ) * ((m - J).choose (j - J) : ℝ) := by
      have h := Nat.choose_mul (n := m) (k := j) (s := J) hj'.1
      have h1 : (1 : ℕ) ≤ j.choose J := Nat.choose_pos hj'.1
      have : m.choose j ≤ m.choose J * (m - J).choose (j - J) := by
        rw [← h]; exact Nat.le_mul_of_pos_right _ h1
      exact_mod_cast this
    have e1 : m - J - (j - J) = m - j := by omega
    have e2 : b ^ j = b ^ J * b ^ (j - J) := by rw [← pow_add]; congr 1; omega
    rw [e1, e2]
    have : 0 ≤ a ^ (m - j) * (b ^ J * b ^ (j - J)) := by positivity
    nlinarith [mul_le_mul_of_nonneg_right hc this]
  refine (sum_le_sum hterm).trans (le_of_eq ?_)
  have hfac : ∑ j ∈ Ico J (m + 1), (m.choose J : ℝ) * b ^ J *
      (((m - J).choose (j - J) : ℝ) * a ^ (m - J - (j - J)) * b ^ (j - J)) =
      (m.choose J : ℝ) * b ^ J * ∑ j ∈ Ico J (m + 1),
        (((m - J).choose (j - J) : ℝ) * a ^ (m - J - (j - J)) * b ^ (j - J)) := (Finset.mul_sum _ _ _).symm
  rw [hfac]
  congr 1
  rw [sum_Ico_eq_sum_range, show m + 1 - J = (m - J) + 1 by omega, add_comm a b, add_pow]
  refine sum_congr rfl (fun i _ => ?_)
  rw [show J + i - J = i by omega]
  ring

theorem p1_population_kernel_expand {ι : Type*} [Fintype ι] (w s : ι → ℝ) (c d : ℝ) (m : ℕ) :
    ∑ i, w i * (c + d * s i) ^ m =
      ∑ k ∈ range (m + 1), (m.choose k : ℝ) * c ^ (m - k) * d ^ k * ∑ i, w i * s i ^ k := by
  simp_rw [add_comm c, add_pow, mul_sum]
  rw [sum_comm]
  refine sum_congr rfl (fun k _ => sum_congr rfl (fun i _ => ?_))
  rw [mul_pow]; ring

theorem p1_weighted_power_abs_le {ι : Type*} [Fintype ι] (u t : ι → ℝ) (hu : ∀ i, 0 ≤ u i)
    (ht : ∀ i, |t i| ≤ 1) (k : ℕ) : |∑ i, u i * t i ^ k| ≤ ∑ i, u i := by
  refine (abs_sum_le_sum_abs _ _).trans (sum_le_sum (fun i _ => ?_))
  rw [abs_mul, abs_of_nonneg (hu i), abs_pow]
  exact mul_le_of_le_one_right (hu i) (pow_le_one₀ (abs_nonneg _) (ht i))

/-- **Moment-matched kernels.** -/
theorem p1_matched_kernel_gap {ι κι : Type*} [Fintype ι] [Fintype κι] (w s : ι → ℝ) (w' s' : κι → ℝ)
    (c d W : ℝ) (J : ℕ) (hd : 0 ≤ d) (hw : ∀ i, 0 ≤ w i) (hw' : ∀ i, 0 ≤ w' i)
    (hW : ∑ i, w i ≤ W) (hW' : ∑ i, w' i ≤ W) (hs : ∀ i, |s i| ≤ 1) (hs' : ∀ i, |s' i| ≤ 1)
    (hmom : ∀ j, j < J → ∑ i, w i * s i ^ j = ∑ i, w' i * s' i ^ j) (m : ℕ) :
    |∑ i, w i * (c + d * s i) ^ m - ∑ i, w' i * (c + d * s' i) ^ m| ≤
      if J ≤ m then 2 * W * (m.choose J : ℝ) * d ^ J * (|c| + d) ^ (m - J) else 0 := by
  set ΔM : ℕ → ℝ := fun j => ∑ i, w i * s i ^ j - ∑ i, w' i * s' i ^ j with hΔM
  have hexp : ∑ i, w i * (c + d * s i) ^ m - ∑ i, w' i * (c + d * s' i) ^ m =
      ∑ k ∈ range (m + 1), (m.choose k : ℝ) * c ^ (m - k) * d ^ k * ΔM k := by
    rw [p1_population_kernel_expand, p1_population_kernel_expand, ← sum_sub_distrib]
    exact sum_congr rfl (fun k _ => by simp only [hΔM]; ring)
  have hΔ : ∀ k, |ΔM k| ≤ 2 * W := by
    intro k
    calc |ΔM k| ≤ |∑ i, w i * s i ^ k| + |∑ i, w' i * s' i ^ k| := abs_sub _ _
      _ ≤ W + W := add_le_add ((p1_weighted_power_abs_le w s hw hs k).trans hW) ((p1_weighted_power_abs_le w' s' hw' hs' k).trans hW')
      _ = 2 * W := by ring
  have hΔ0 : ∀ k, k < J → ΔM k = 0 := fun k hk => by simp only [hΔM]; rw [hmom k hk, sub_self]
  rw [hexp]
  have habs : |∑ k ∈ range (m + 1), (m.choose k : ℝ) * c ^ (m - k) * d ^ k * ΔM k| ≤
      ∑ k ∈ range (m + 1), (if J ≤ k then (m.choose k : ℝ) * |c| ^ (m - k) * d ^ k * (2 * W) else 0) := by
    refine (abs_sum_le_sum_abs _ _).trans (sum_le_sum (fun k _ => ?_))
    split_ifs with hk
    · rw [abs_mul, abs_mul, abs_mul, abs_pow, abs_pow, abs_of_nonneg hd, Nat.abs_cast]
      exact mul_le_mul_of_nonneg_left (hΔ k) (by positivity)
    · rw [hΔ0 k (by omega), mul_zero, abs_zero]
  refine habs.trans ?_
  split_ifs with hJm
  · rw [← sum_range_add_sum_Ico _ (show J ≤ m + 1 by omega)]
    have hz : ∑ k ∈ range J, (if J ≤ k then (m.choose k : ℝ) * |c| ^ (m - k) * d ^ k * (2 * W) else 0) = 0 :=
      sum_eq_zero (fun k hk => by rw [if_neg (by have := mem_range.mp hk; omega)])
    rw [hz, zero_add]
    have hs2 : ∑ k ∈ Ico J (m + 1), (if J ≤ k then (m.choose k : ℝ) * |c| ^ (m - k) * d ^ k * (2 * W) else 0) =
        2 * W * ∑ k ∈ Ico J (m + 1), (m.choose k : ℝ) * |c| ^ (m - k) * d ^ k := by
      rw [mul_sum]
      exact sum_congr rfl (fun k hk => by rw [if_pos (mem_Ico.mp hk).1]; ring)
    rw [hs2]
    have hW0 : 0 ≤ W := le_trans (sum_nonneg (fun i _ => hw i)) hW
    calc 2 * W * ∑ k ∈ Ico J (m + 1), (m.choose k : ℝ) * |c| ^ (m - k) * d ^ k
        ≤ 2 * W * ((m.choose J : ℝ) * d ^ J * (|c| + d) ^ (m - J)) :=
          mul_le_mul_of_nonneg_left (p1_binom_tail _ _ (abs_nonneg c) hd m J hJm) (by positivity)
      _ = 2 * W * (m.choose J : ℝ) * d ^ J * (|c| + d) ^ (m - J) := by ring
  · exact le_of_eq (sum_eq_zero (fun k hk => by rw [if_neg (by have := mem_range.mp hk; omega)]))

/-- **Summed over every lag**, the moment-matched kernels differ by at most `2W d^J / (1-λ)^{J+1}`. -/
theorem p1_matched_kernel_gap_l1 {ι κι : Type*} [Fintype ι] [Fintype κι] (w s : ι → ℝ) (w' s' : κι → ℝ)
    (c d W : ℝ) (J : ℕ) (hd : 0 ≤ d) (hcd : |c| + d < 1) (hw : ∀ i, 0 ≤ w i) (hw' : ∀ i, 0 ≤ w' i)
    (hW : ∑ i, w i ≤ W) (hW' : ∑ i, w' i ≤ W) (hs : ∀ i, |s i| ≤ 1) (hs' : ∀ i, |s' i| ≤ 1)
    (hmom : ∀ j, j < J → ∑ i, w i * s i ^ j = ∑ i, w' i * s' i ^ j) (N : ℕ) :
    ∑ m ∈ range N, |∑ i, w i * (c + d * s i) ^ m - ∑ i, w' i * (c + d * s' i) ^ m| ≤
      2 * W * d ^ J * (1 / (1 - (|c| + d)) ^ (J + 1)) := by
  set lam := |c| + d with hlam
  have hl0 : 0 ≤ lam := by positivity
  have hW0 : 0 ≤ W := le_trans (sum_nonneg (fun i _ => hw i)) hW
  have hpt := p1_matched_kernel_gap w s w' s' c d W J hd hw hw' hW hW' hs hs' hmom
  refine (sum_le_sum (fun m _ => hpt m)).trans ?_
  -- reindex the nonzero terms `m = n + J` and compare with the negative-binomial series
  have hsum := hasSum_choose_mul_geometric_of_norm_lt_one (𝕜 := ℝ) J
    (show ‖lam‖ < 1 by rw [Real.norm_eq_abs, abs_of_nonneg hl0]; exact hcd)
  have hnn : ∀ n, 0 ≤ ((n + J).choose J : ℝ) * lam ^ n := fun n => by positivity
  have hpart : ∀ M', ∑ n ∈ range M', ((n + J).choose J : ℝ) * lam ^ n ≤ 1 / (1 - lam) ^ (J + 1) :=
    fun M' => hsum.summable.sum_le_tsum _ (fun n _ => hnn n) |>.trans (le_of_eq hsum.tsum_eq)
  have hre : ∑ m ∈ range N, (if J ≤ m then 2 * W * (m.choose J : ℝ) * d ^ J * lam ^ (m - J) else 0) =
      2 * W * d ^ J * ∑ n ∈ range (N - J), ((n + J).choose J : ℝ) * lam ^ n := by
    by_cases hNJ : J ≤ N
    · rw [← sum_range_add_sum_Ico _ hNJ]
      have hz : ∑ m ∈ range J, (if J ≤ m then 2 * W * (m.choose J : ℝ) * d ^ J * lam ^ (m - J) else 0) = 0 :=
        sum_eq_zero (fun m hm => by rw [if_neg (by have := mem_range.mp hm; omega)])
      rw [hz, zero_add, sum_Ico_eq_sum_range, mul_sum]
      refine sum_congr rfl (fun n _ => ?_)
      rw [if_pos (by omega), show J + n - J = n by omega, add_comm J n]
      ring
    · rw [show N - J = 0 by omega, range_zero, sum_empty, mul_zero]
      exact sum_eq_zero (fun m hm => by rw [if_neg (by have := mem_range.mp hm; omega)])
  rw [hre]
  exact mul_le_mul_of_nonneg_left (hpart _) (by positivity)

theorem p1_geom_partial_le (x : ℝ) (hx0 : 0 ≤ x) (hx1 : x < 1) (N : ℕ) : ∑ m ∈ range N, x ^ m ≤ 1 / (1 - x) := by
  have h := mul_neg_geom_sum x N
  rw [le_div_iff₀ (by linarith), mul_comm, h]
  have : 0 ≤ x ^ N := pow_nonneg hx0 N
  linarith

/-- Kernel of a population at rates `c + d s_i` (`|s_i| ≤ 1`): `ℓ₁` partial sums at most `W / (1 - (c + d))`. -/
theorem p1_population_kernel_l1 {ι : Type*} [Fintype ι] (w s : ι → ℝ) (c d W : ℝ) (hc : 0 ≤ c) (hd : 0 ≤ d)
    (hcd : c + d < 1) (hw : ∀ i, 0 ≤ w i) (hW : ∑ i, w i ≤ W) (hs : ∀ i, |s i| ≤ 1) (N : ℕ) :
    ∑ m ∈ range N, |∑ i, w i * (c + d * s i) ^ m| ≤ W / (1 - (c + d)) := by
  have hr : ∀ i, |c + d * s i| ≤ c + d := fun i => by
    calc |c + d * s i| ≤ |c| + |d * s i| := abs_add_le _ _
      _ = c + d * |s i| := by rw [abs_of_nonneg hc, abs_mul, abs_of_nonneg hd]
      _ ≤ c + d * 1 := by gcongr; exact hs i
      _ = c + d := by ring
  calc ∑ m ∈ range N, |∑ i, w i * (c + d * s i) ^ m|
      ≤ ∑ m ∈ range N, ∑ i, w i * (c + d) ^ m := by
        refine sum_le_sum (fun m _ => (abs_sum_le_sum_abs _ _).trans (sum_le_sum (fun i _ => ?_)))
        rw [abs_mul, abs_of_nonneg (hw i), abs_pow]
        exact mul_le_mul_of_nonneg_left (pow_le_pow_left₀ (abs_nonneg _) (hr i) m) (hw i)
    _ = ∑ i, w i * ∑ m ∈ range N, (c + d) ^ m := by rw [sum_comm]; simp only [mul_sum]
    _ ≤ ∑ i, w i * (1 / (1 - (c + d))) := by
        gcongr with i
        · exact hw i
        · exact p1_geom_partial_le _ (by positivity) hcd N
    _ ≤ W / (1 - (c + d)) := by
        rw [← sum_mul, div_eq_mul_one_div W]
        exact mul_le_mul_of_nonneg_right hW (div_nonneg zero_le_one (by linarith))

/-- **Theorem 5.8 (iii), formal version, every `K = L + 1`.** The binomial moment-matched pair of
`p1_thm_kcohort_lower_bound_every_K` (rates `c + d s` with `s` on alternate grid nodes, merged weights
`W C(2L+1, k)/2^(2L)`), with `c, d ≥ 0`, `c + d < 1` and `|a| + κ W/(1 - (c+d)) ≤ s < 1`, observed passively for
`T` periods after any warm-up `M` from rest, i.i.d. `N(0, v)` innovations: any test with both error
probabilities at most `1/4` needs `1 ≤ 2 (1+s)² (κ E/(1-s)²)² T` with `E = 2 W d^(2K-1)/(1-(c+d))^(2K)`, i.e.
`T ≥ c' d^-(4K-2)`, uniformly in `M`. -/
theorem p1_thm_passive_cost_every_K (L : ℕ) (a κ c d W s : ℝ) (hκ : 0 < κ) (hc : 0 ≤ c) (hd : 0 ≤ d)
    (hcd : c + d < 1) (hW0 : 0 ≤ W) (hs : |a| + κ * (W / (1 - (c + d))) ≤ s) (hs1 : s < 1)
    (q rate q' rate' : Fin (L + 1) → ℝ)
    (hr : ∀ i : Fin (L + 1), 1 - rate i = c + d * gridNode L (2 * i + 1))
    (hr' : ∀ i : Fin (L + 1), 1 - rate' i = c + d * gridNode L (2 * i))
    (hq : ∀ i : Fin (L + 1), q i * rate i = W * ((2 * L + 1).choose (2 * i + 1) : ℝ) / 2 ^ (2 * L))
    (hq' : ∀ i : Fin (L + 1), q' i * rate' i = W * ((2 * L + 1).choose (2 * i) : ℝ) / 2 ^ (2 * L))
    (M T : ℕ) (v : ℝ≥0) (hv : v ≠ 0) (A : Set (Fin T → ℝ)) (hA : MeasurableSet A)
    (herr1 : (obsLaw M T v (fun j => actualCohortImpulse a κ q rate j / κ)).real A ≤ 1 / 4)
    (herr0 : (obsLaw M T v (fun j => actualCohortImpulse a κ q' rate' j / κ)).real Aᶜ ≤ 1 / 4) :
    1 ≤ 2 * (1 + s) ^ 2 *
      (κ * (2 * W * d ^ (2 * L + 1) * (1 / (1 - (c + d)) ^ (2 * L + 1 + 1))) / (1 - s) ^ 2) ^ 2 * T := by
  set w : Fin (L + 1) → ℝ := fun i => q i * rate i
  set w' : Fin (L + 1) → ℝ := fun i => q' i * rate' i
  set sn : Fin (L + 1) → ℝ := fun i => gridNode L (2 * i + 1)
  set sn' : Fin (L + 1) → ℝ := fun i => gridNode L (2 * i)
  have hpow : (0 : ℝ) < 2 ^ (2 * L) := by positivity
  obtain ⟨hodd, heven⟩ := p1_grid_half_weight L
  have hw : ∀ i, 0 ≤ w i := fun i => by simp only [w]; rw [hq i]; positivity
  have hw' : ∀ i, 0 ≤ w' i := fun i => by simp only [w']; rw [hq' i]; positivity
  have hsum : ∑ i, w i ≤ W := by
    simp only [w, hq]
    rw [Fin.sum_univ_eq_sum_range (fun i => W * ((2 * L + 1).choose (2 * i + 1) : ℝ) / 2 ^ (2 * L)),
      ← sum_div, ← mul_sum, hodd, mul_div_assoc, div_self hpow.ne', mul_one]
  have hsum' : ∑ i, w' i ≤ W := by
    simp only [w', hq']
    rw [Fin.sum_univ_eq_sum_range (fun i => W * ((2 * L + 1).choose (2 * i) : ℝ) / 2 ^ (2 * L)),
      ← sum_div, ← mul_sum, heven, mul_div_assoc, div_self hpow.ne', mul_one]
  have hsn : ∀ i, |sn i| ≤ 1 := fun i => p1_gridNode_abs_le L _ (by omega)
  have hsn' : ∀ i, |sn' i| ≤ 1 := fun i => p1_gridNode_abs_le L _ (by omega)
  have hmom : ∀ j, j < 2 * L + 1 → ∑ i, w i * sn i ^ j = ∑ i, w' i * sn' i ^ j := by
    intro j hj
    simp only [w, w', sn, sn', hq, hq']
    rw [Fin.sum_univ_eq_sum_range (fun i => W * ((2 * L + 1).choose (2 * i + 1) : ℝ) / 2 ^ (2 * L) *
        gridNode L (2 * i + 1) ^ j),
      Fin.sum_univ_eq_sum_range (fun i => W * ((2 * L + 1).choose (2 * i) : ℝ) / 2 ^ (2 * L) *
        gridNode L (2 * i) ^ j)]
    have hm := p1_grid_matched_moments L j hj
    have e : ∀ (f : ℕ → ℝ), ∑ i ∈ range (L + 1), W * f i / 2 ^ (2 * L) * gridNode L (2 * i + 1) ^ j =
        W / 2 ^ (2 * L) * ∑ i ∈ range (L + 1), f i * gridNode L (2 * i + 1) ^ j := by
      intro f; rw [mul_sum]; refine sum_congr rfl (fun i _ => by ring)
    have e' : ∀ (f : ℕ → ℝ), ∑ i ∈ range (L + 1), W * f i / 2 ^ (2 * L) * gridNode L (2 * i) ^ j =
        W / 2 ^ (2 * L) * ∑ i ∈ range (L + 1), f i * gridNode L (2 * i) ^ j := by
      intro f; rw [mul_sum]; refine sum_congr rfl (fun i _ => by ring)
    rw [e (fun i => ((2 * L + 1).choose (2 * i + 1) : ℝ)), e' (fun i => ((2 * L + 1).choose (2 * i) : ℝ)), hm]
  have hk : ∀ m, cohortKernel q rate m = ∑ i, w i * (c + d * sn i) ^ m := fun m => by
    simp only [cohortKernel, w, sn]
    exact sum_congr rfl (fun i _ => by rw [hr i])
  have hk' : ∀ m, cohortKernel q' rate' m = ∑ i, w' i * (c + d * sn' i) ^ m := fun m => by
    simp only [cohortKernel, w', sn']
    exact sum_congr rfl (fun i _ => by rw [hr' i])
  set K1 := W / (1 - (c + d)) with hK1def
  have hK1 : ∀ N, ∑ m ∈ range N, |cohortKernel q rate m| ≤ K1 := fun N => by
    simp only [hk]; exact p1_population_kernel_l1 w sn c d W hc hd hcd hw hsum hsn N
  have hK1' : ∀ N, ∑ m ∈ range N, |cohortKernel q' rate' m| ≤ K1 := fun N => by
    simp only [hk']; exact p1_population_kernel_l1 w' sn' c d W hc hd hcd hw' hsum' hsn' N
  have hcd' : |c| + d < 1 := by rw [abs_of_nonneg hc]; exact hcd
  set E := 2 * W * d ^ (2 * L + 1) * (1 / (1 - (c + d)) ^ (2 * L + 1 + 1)) with hEdef
  have hE : ∀ N, ∑ m ∈ range N, |cohortKernel q rate m - cohortKernel q' rate' m| ≤ E := fun N => by
    simp only [hk, hk']
    have := p1_matched_kernel_gap_l1 w sn w' sn' c d W (2 * L + 1) hd hcd' hw hw' hsum hsum' hsn hsn' hmom N
    rwa [abs_of_nonneg hc] at this
  have hstab : |a| + |κ| * K1 ≤ s := by rw [abs_of_pos hκ]; exact hs
  have hH1 := p1_response_l1 a κ K1 s (cohortKernel q' rate') _ (p1_impulse_zero a κ q' rate')
    (p1_impulse_closed_loop_recursion a κ q' rate') hK1' hstab hs1
  have hD := p1_response_diff_l1 a κ K1 s E (|κ| / (1 - s)) (cohortKernel q rate) (cohortKernel q' rate') _ _
    (p1_impulse_zero a κ _ _) (p1_impulse_zero a κ _ _)
    (p1_impulse_closed_loop_recursion a κ _ _) (p1_impulse_closed_loop_recursion a κ _ _)
    hK1 hstab hs1 hE hH1
  -- normalized responses and the passive record
  set g1 : ℕ → ℝ := fun j => actualCohortImpulse a κ q rate j / κ
  set g0 : ℕ → ℝ := fun j => actualCohortImpulse a κ q' rate' j / κ
  have hκ0 : κ ≠ 0 := hκ.ne'
  have hs1' : 0 < 1 - s := by linarith
  have hg0 : g0 0 = 1 := by simp [g0, p1_impulse_zero, hκ0]
  have hg1 : g1 0 = 1 := by simp [g1, p1_impulse_zero, hκ0]
  have hrec0 : ∀ t, g0 (t + 1) = a * g0 t + κ * ∑ j ∈ range (t + 1), cohortKernel q' rate' j * g0 (t - j) := by
    intro t
    simp only [g0]
    rw [p1_impulse_closed_loop_recursion, add_div, mul_sum, mul_sum, sum_div]
    congr 1
    · ring
    · exact sum_congr rfl (fun j _ => by field_simp)
  have hrg := p1_closed_loop_reciprocal a κ _ g0 hg0 hrec0
  have hDr := p1_clRecip_l1 a κ K1 (cohortKernel q' rate') hK1'
  set E1 := κ * E / (1 - s) ^ 2 with hE1def
  have hEg : ∀ N, ∑ m ∈ range N, |g1 m - g0 m| ≤ E1 := by
    intro N
    have e : ∀ m, |g1 m - g0 m| = |actualCohortImpulse a κ q rate m - actualCohortImpulse a κ q' rate' m| / κ := by
      intro m; simp only [g1, g0]; rw [← sub_div, abs_div, abs_of_pos hκ]
    simp only [e, ← sum_div]
    rw [div_le_iff₀ hκ]
    calc _ ≤ |κ| * E * (|κ| / (1 - s)) / (1 - s) := hD N
      _ = E1 * κ := by rw [abs_of_pos hκ, hE1def]; field_simp
  have hkl := p1_passive_record_kl M T v hv g0 g1 _ (1 + |a| + |κ| * K1) E1 hrg hg0 hg1 hDr hEg
  have hlow := p1_test_error_kl_lower_bound _ _ hA herr1 herr0
  have h14 := hlow.trans hkl
  rw [ENNReal.ofReal_le_ofReal_iff (by positivity)] at h14
  have hDs : 1 + |a| + |κ| * K1 ≤ 1 + s := by linarith
  have hK10 : 0 ≤ K1 := div_nonneg hW0 (by linarith)
  have hD0 : 0 ≤ 1 + |a| + |κ| * K1 := by positivity
  have hsq : (1 + |a| + |κ| * K1) ^ 2 ≤ (1 + s) ^ 2 := pow_le_pow_left₀ hD0 hDs 2
  have hT : (0 : ℝ) ≤ T := Nat.cast_nonneg T
  nlinarith [mul_le_mul_of_nonneg_right hsq (by positivity : (0 : ℝ) ≤ T * E1 ^ 2)]

end CurrentMM
