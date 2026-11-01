import CurrentProofs.Paper1LowerBound
import Mathlib.Algebra.BigOperators.Field

/-!
# Paper 1, Proposition `prop:target`: supervisory separation

The closed-loop persistence of the cohort economy is `S = a + κ ∑ q_i`, with intensity `q_i = w_i / η_i` for merged
weight `w_i = q_i η_i` and memory rate `r_i = 1 - η_i`.

* `p1_market_wide_measure`: a market-wide measure that scales every intensity by `θ` meets the threshold `s̄` if and
  only if `θ ≤ (s̄ - a)/(S - a)`, so its size depends on the economy only through `S`;
* `p1_persistence_merged`: `S = a + κ ∑ w_i / (1 - r_i)`, a function of the merged measure;
* `p1_resolvent_expand`: `1/(u - d s) = ∑_{m<J} d^m s^m / u^(m+1) + d^J s^J / (u^J (u - d s))`;
* `p1_persistence_gap`: populations at rates `c + d s` whose moments agree below order `J` have summed intensities
  within `2 W d^J / (u^J (u - d))`, `u = 1 - c` — for every `K`, the market-wide size is the same up to
  `O((Δη)^(2K-1))`;
* `p1_prop_target_two_cohorts`: for the explicit two-cohort matched pair, if `d ≤ u/5` there is a nonempty interval of
  thresholds at which halting the larger group restores stability in economy `A`, while halting either group fails
  in economy `B`; and any rule that makes this decision correctly with probability at least `3/4` in both
  economies from `N` reset experiments of `T` taps needs `σ² ≤ 2NT((2W 2^T d³) C_T)²`, i.e. `N = Ω(d^-6)`.
-/

namespace CurrentMM

open Finset MeasureTheory ProbabilityTheory
open scoped ENNReal NNReal

/-- **Market-wide measure.** -/
theorem p1_market_wide_measure (a S sbar θ : ℝ) (hS : a < S) :
    a + θ * (S - a) ≤ sbar ↔ θ ≤ (sbar - a) / (S - a) := by
  rw [le_div_iff₀ (by linarith)]; constructor <;> intro h <;> linarith

/-- The persistence depends on the economy only through the merged measure. -/
theorem p1_persistence_merged {n : ℕ} (a κ : ℝ) (q rate : Fin n → ℝ) (hr : ∀ i, rate i ≠ 0) :
    a + κ * ∑ i, q i = a + κ * ∑ i, (q i * rate i) / rate i := by
  congr 2
  exact sum_congr rfl (fun i _ => by field_simp [hr i])

theorem p1_resolvent_expand (u d s : ℝ) (hu : u ≠ 0) (hv : u - d * s ≠ 0) (J : ℕ) :
    1 / (u - d * s) = ∑ m ∈ range J, d ^ m * s ^ m / u ^ (m + 1) + d ^ J * s ^ J / (u ^ J * (u - d * s)) := by
  induction J with
  | zero => simp
  | succ J ih =>
    rw [ih, sum_range_succ]
    have hJ : u ^ J ≠ 0 := pow_ne_zero _ hu
    field_simp
    ring

theorem p1_resolvent_sum_split {τ : Type*} [Fintype τ] (v t : τ → ℝ) (u d : ℝ) (J : ℕ) (hu : 0 < u)
    (hd : 0 ≤ d) (hdu : d < u) (ht : ∀ i, |t i| ≤ 1) :
    ∑ i, v i / (u - d * t i) = ∑ m ∈ range J, d ^ m / u ^ (m + 1) * ∑ i, v i * t i ^ m +
      d ^ J / u ^ J * ∑ i, v i * t i ^ J / (u - d * t i) := by
  have hpos : ∀ i, 0 < u - d * t i := fun i => by
    have : d * t i ≤ d := by nlinarith [abs_le.mp (ht i)]
    linarith
  have e : ∀ i, v i / (u - d * t i) = v i * (1 / (u - d * t i)) := fun i => by ring
  simp_rw [e, fun i => p1_resolvent_expand u d (t i) hu.ne' (hpos i).ne' J, mul_add, sum_add_distrib, mul_sum]
  congr 1
  · rw [sum_comm]
    exact sum_congr rfl (fun m _ => sum_congr rfl (fun i _ => by ring))
  · exact sum_congr rfl (fun i _ => by field_simp)

theorem p1_resolvent_remainder_le {τ : Type*} [Fintype τ] (v t : τ → ℝ) (u d W : ℝ) (J : ℕ)
    (hd : 0 ≤ d) (hdu : d < u) (hv : ∀ i, 0 ≤ v i) (ht : ∀ i, |t i| ≤ 1) (hvW : ∑ i, v i ≤ W) :
    |∑ i, v i * t i ^ J / (u - d * t i)| ≤ W / (u - d) := by
  have hud : 0 < u - d := by linarith
  have hpos : ∀ i, u - d ≤ u - d * t i := fun i => by
    have : d * t i ≤ d := by nlinarith [abs_le.mp (ht i)]
    linarith
  refine (abs_sum_le_sum_abs _ _).trans ?_
  calc ∑ i, |v i * t i ^ J / (u - d * t i)| ≤ ∑ i, v i / (u - d) := by
        refine sum_le_sum (fun i _ => ?_)
        have hden : 0 < u - d * t i := lt_of_lt_of_le hud (hpos i)
        rw [abs_div, abs_mul, abs_of_nonneg (hv i), abs_of_pos hden, abs_pow]
        have h1 : |t i| ^ J ≤ 1 := pow_le_one₀ (abs_nonneg _) (ht i)
        calc v i * |t i| ^ J / (u - d * t i) ≤ v i * 1 / (u - d * t i) := by
              have := hv i; gcongr
          _ ≤ v i / (u - d) := by rw [mul_one]; exact div_le_div_of_nonneg_left (hv i) hud (hpos i)
    _ = (∑ i, v i) / (u - d) := by rw [Finset.sum_div]
    _ ≤ W / (u - d) := div_le_div_of_nonneg_right hvW hud.le

/-- **Summed intensities of moment-matched populations.** -/
theorem p1_persistence_gap {ι κι : Type*} [Fintype ι] [Fintype κι] (w s : ι → ℝ) (w' s' : κι → ℝ)
    (u d W : ℝ) (J : ℕ) (hd : 0 ≤ d) (hdu : d < u) (hw : ∀ i, 0 ≤ w i) (hw' : ∀ i, 0 ≤ w' i)
    (hW : ∑ i, w i ≤ W) (hW' : ∑ i, w' i ≤ W) (hs : ∀ i, |s i| ≤ 1) (hs' : ∀ i, |s' i| ≤ 1)
    (hmom : ∀ j, j < J → ∑ i, w i * s i ^ j = ∑ i, w' i * s' i ^ j) :
    |∑ i, w i / (u - d * s i) - ∑ i, w' i / (u - d * s' i)| ≤ 2 * W * d ^ J / (u ^ J * (u - d)) := by
  have hu : 0 < u := lt_of_le_of_lt hd hdu
  have hud : 0 < u - d := by linarith
  rw [p1_resolvent_sum_split w s u d J hu hd hdu hs, p1_resolvent_sum_split w' s' u d J hu hd hdu hs']
  have hcancel : ∑ m ∈ range J, d ^ m / u ^ (m + 1) * ∑ i, w i * s i ^ m =
      ∑ m ∈ range J, d ^ m / u ^ (m + 1) * ∑ i, w' i * s' i ^ m :=
    sum_congr rfl (fun m hm => by rw [hmom m (mem_range.mp hm)])
  rw [hcancel, add_sub_add_left_eq_sub, ← mul_sub, abs_mul, abs_of_nonneg (by positivity)]
  have h1 := p1_resolvent_remainder_le w s u d W J hd hdu hw hs hW
  have h2 := p1_resolvent_remainder_le w' s' u d W J hd hdu hw' hs' hW'
  calc d ^ J / u ^ J * |∑ i, w i * s i ^ J / (u - d * s i) - ∑ i, w' i * s' i ^ J / (u - d * s' i)|
      ≤ d ^ J / u ^ J * (W / (u - d) + W / (u - d)) := by
        gcongr
        exact (abs_sub _ _).trans (add_le_add h1 h2)
    _ = 2 * W * d ^ J / (u ^ J * (u - d)) := by field_simp; ring

/-- **Proposition `prop:target`, formal version for two cohorts.** Economy `A` has merged weights `W(1/4, 3/4)` at
memory rates `c + d(-1, 1/3)`, economy `B` has `W(4/7, 3/7)` at `c + d(-1/2, 2/3)` (equal moments of orders
`0, 1, 2`); `u = 1 - c`, `0 < d ≤ u/5`, `κ, W > 0`. Then (i) the market-wide persistences differ by at most
`2κW d³/(u³(u-d))`; (ii) for every threshold `s̄` with
`S_A - κ q_2^A ≤ s̄ < S_A - κ q_2^A + 3κW/(28u) - 2κW d³/(u³(u-d))` (a nonempty interval), halting the larger group
restores `S ≤ s̄` in `A`, while halting either group leaves `S > s̄` in `B`; (iii) any decision rule from `N` reset
experiments of `T` taps that answers "halting one group is enough" correctly with probability at least `3/4` in both
economies forces `σ² ≤ 2NT((2W 2^T d³) C_T)²`. -/
theorem p1_prop_target_two_cohorts (a κ c d W H : ℝ) (hκ : 0 < κ) (hW : 0 < W) (hc : 0 ≤ c) (hd : 0 < d)
    (hdu : d ≤ (1 - c) / 5) (hH : 0 ≤ H)
    (q rate q' rate' : Fin 2 → ℝ)
    (hr : ∀ i, 1 - rate i = c + d * ![-1, 1 / 3] i) (hr' : ∀ i, 1 - rate' i = c + d * ![-1 / 2, 2 / 3] i)
    (hq : ∀ i, q i * rate i = W * ![1 / 4, 3 / 4] i) (hq' : ∀ i, q' i * rate' i = W * ![4 / 7, 3 / 7] i) :
    let u := 1 - c
    let SA := a + κ * ∑ i, q i
    let SB := a + κ * ∑ i, q' i
    q 0 ≤ q 1 ∧
    |SA - SB| ≤ κ * (2 * W * d ^ 3 / (u ^ 3 * (u - d))) ∧
    (SA - κ * q 1 + 3 * κ * W / (28 * u) - κ * (2 * W * d ^ 3 / (u ^ 3 * (u - d))) > SA - κ * q 1) ∧
    (∀ sbar, SA - κ * q 1 ≤ sbar →
        sbar < SA - κ * q 1 + 3 * κ * W / (28 * u) - κ * (2 * W * d ^ 3 / (u ^ 3 * (u - d))) →
        SA - κ * q 1 ≤ sbar ∧ ∀ j, SB - κ * q' j > sbar) ∧
    (∀ (N T : ℕ) (variance : ℝ≥0), variance ≠ 0 →
      (∀ t, t < T → |actualCohortImpulse a κ q' rate' t| ≤ H) →
      ∀ (A : Set (ObservationRecord (N * T))), MeasurableSet A →
      (gaussianRecordLaw (N * T) (p1RepeatedMean N T (actualCohortImpulse a κ q rate)) variance).real A ≤ 1 / 4 →
      (gaussianRecordLaw (N * T) (p1RepeatedMean N T (actualCohortImpulse a κ q' rate')) variance).real Aᶜ ≤ 1 / 4 →
      (variance : ℝ) ≤ 2 * N * T * ((2 * W * 2 ^ T * d ^ 3) * p1GapConst a |κ| W H T) ^ 2) := by
  intro u SA SB
  have hu : 0 < u := by simp only [u]; linarith
  have hdu' : d ≤ u / 5 := hdu
  have hud : 0 < u - d := by linarith
  -- the rates (η) and intensities
  have hη : ∀ i, rate i = u - d * ![-1, 1 / 3] i := fun i => by simp only [u]; linarith [hr i]
  have hη' : ∀ i, rate' i = u - d * ![-1 / 2, 2 / 3] i := fun i => by simp only [u]; linarith [hr' i]
  have hηpos : ∀ i, 0 < rate i := fun i => by
    rw [hη i]; fin_cases i <;> simp <;> nlinarith
  have hηpos' : ∀ i, 0 < rate' i := fun i => by
    rw [hη' i]; fin_cases i <;> simp <;> nlinarith
  have hqi : ∀ i, q i = W * ![1 / 4, 3 / 4] i / (u - d * ![-1, 1 / 3] i) := fun i => by
    rw [← hq i, ← hη i]; field_simp [(hηpos i).ne']
  have hqi' : ∀ i, q' i = W * ![4 / 7, 3 / 7] i / (u - d * ![-1 / 2, 2 / 3] i) := fun i => by
    rw [← hq' i, ← hη' i]; field_simp [(hηpos' i).ne']
  -- (i) persistence gap
  have hgap : |∑ i, q i - ∑ i, q' i| ≤ 2 * W * d ^ 3 / (u ^ 3 * (u - d)) := by
    simp_rw [hqi, hqi']
    refine p1_persistence_gap (fun i : Fin 2 => W * ![1 / 4, 3 / 4] i) ![-1, 1 / 3]
      (fun i : Fin 2 => W * ![4 / 7, 3 / 7] i) ![-1 / 2, 2 / 3] u d W 3 hd.le (by linarith)
      (fun i => by fin_cases i <;> simp <;> positivity) (fun i => by fin_cases i <;> simp <;> positivity)
      (by simp [Fin.sum_univ_two]; linarith) (by simp [Fin.sum_univ_two]; linarith)
      (fun i => by fin_cases i <;> norm_num [abs_le]) (fun i => by fin_cases i <;> norm_num [abs_le]) ?_
    intro j hj
    have := p1_twocohort_matched_pair W j hj
    simpa [mgMoment] using this
  have hSgap : |SA - SB| ≤ κ * (2 * W * d ^ 3 / (u ^ 3 * (u - d))) := by
    have e : SA - SB = κ * (∑ i, q i - ∑ i, q' i) := by simp only [SA, SB]; ring
    rw [e, abs_mul, abs_of_pos hκ]
    exact mul_le_mul_of_nonneg_left hgap hκ.le
  -- intensity comparison: q_2^A ≥ 3W/(4u), q_j^B ≤ 9W/(14u)
  have hqA : 3 * W / (4 * u) ≤ q 1 := by
    rw [hqi 1]; simp
    rw [div_le_div_iff₀ (by positivity) (by nlinarith)]
    nlinarith
  have hqB : ∀ j, q' j ≤ 9 * W / (14 * u) := by
    intro j; rw [hqi' j]
    fin_cases j <;> simp
    · rw [div_le_div_iff₀ (by nlinarith) (by positivity)]; nlinarith
    · rw [div_le_div_iff₀ (by nlinarith) (by positivity)]; nlinarith
  -- the margin is positive for d ≤ u/5
  have hsmall : 2 * W * d ^ 3 / (u ^ 3 * (u - d)) < 3 * W / (28 * u) := by
    rw [div_lt_div_iff₀ (by positivity) (by positivity)]
    have hd3 : d ^ 3 ≤ (u / 5) ^ 3 := pow_le_pow_left₀ hd.le hdu' 3
    have hud4 : 4 * u / 5 ≤ u - d := by linarith
    have : 3 * W * (u ^ 3 * (4 * u / 5)) ≤ 3 * W * (u ^ 3 * (u - d)) := by gcongr
    nlinarith [pow_pos hu 4, pow_pos hu 3, mul_pos hW (pow_pos hu 4)]
  have hq0 : q 0 ≤ q 1 := by
    have h0 : q 0 ≤ W / (4 * u) := by
      rw [hqi 0]; simp
      rw [div_le_div_iff₀ (by nlinarith) (by positivity)]; nlinarith
    have : W / (4 * u) ≤ 3 * W / (4 * u) := by
      apply div_le_div_of_nonneg_right _ (by positivity); linarith
    linarith
  refine ⟨hq0, hSgap, ?_, ?_, ?_⟩
  · have : κ * (2 * W * d ^ 3 / (u ^ 3 * (u - d))) < 3 * κ * W / (28 * u) := by
      have := mul_lt_mul_of_pos_left hsmall hκ
      calc κ * (2 * W * d ^ 3 / (u ^ 3 * (u - d))) < κ * (3 * W / (28 * u)) := this
        _ = 3 * κ * W / (28 * u) := by ring
    linarith
  · intro sbar hlo hhi
    refine ⟨hlo, fun j => ?_⟩
    have h1 : SB ≥ SA - κ * (2 * W * d ^ 3 / (u ^ 3 * (u - d))) := by
      have := (abs_le.mp hSgap).2; linarith
    have h2 : κ * q' j ≤ κ * q 1 - 3 * κ * W / (28 * u) := by
      have hj := hqB j
      have : 9 * W / (14 * u) = 3 * W / (4 * u) - 3 * W / (28 * u) := by field_simp; ring
      rw [this] at hj
      have := mul_le_mul_of_nonneg_left (show q' j ≤ q 1 - 3 * W / (28 * u) by linarith) hκ.le
      calc κ * q' j ≤ κ * (q 1 - 3 * W / (28 * u)) := this
        _ = κ * q 1 - 3 * κ * W / (28 * u) := by ring
    linarith
  · intro N T variance hv hh' A hA herr0 herr1
    exact p1_thm_twocohort_lower_bound_formal a κ c d W H N T q rate q' rate' variance hv hc hd.le
      (by linarith) hH hW.le hr hr' hq hq' hh' A hA herr0 herr1

end CurrentMM
