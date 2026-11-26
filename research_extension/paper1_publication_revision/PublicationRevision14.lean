import Mathlib.Basic.Real.Basic
import Mathlib.Algebra.BigOperators.Intervals
import Mathlib.Algebra.Ring.GeomSum
import Mathlib.Tactic.Linarith
import Mathlib.Tactic.Ring
import Mathlib.Tactic.Positivity
import Mathlib.Data.Finset.NatAntidiagonal
import Mathlib.Algebra.BigOperators.NatAntidiagonal
import Mathlib.Analysis.Calculus.MeanValue
import Mathlib.Analysis.SpecialFunctions.Log.Deriv
import Mathlib.Analysis.SpecialFunctions.Trigonometric.Basic

/-!
# Paper 1, Theorem 7.1(iv) / Supplement Section S23: Passive-Price Incidence Upper Bound

This file checks the deterministic steps of the upper-bound proof for estimating smooth feedback
incidence from a single passive price record:
1. `fourier_first_moment_bound`: derives the Fourier first-moment budget M_1(ϕ) ≤ S̄ / (1 - r̄)
   directly from the stationary positive exponential-feedback price law
   Q(z) = 1 - z(a + J(z)) with budget S = a + κ ∑ q_i ≤ S̄ < 1 and memory bound r_i ≤ r̄ < 1.
2. `double_sum_le`, `convPow`, `convPow_nonneg`, `convPow_one`, `sum_convPow_le`,
   `sum_mul_convPow_le`: Cauchy convolution powers and Leibniz first-moment bound for convolution powers.
3. `logCoeff`, `triangular_sum_le`, `sum_j_logCoeff_le`: analytic log-expansion coefficients and the
   finite double-sum swap showing ∑_{j=1}^N j |ℓ_j| ≤ M_1(ϕ) / (1 - S) ≤ S̄ / ((1 - S̄)(1 - r̄)).
4. `phi_rescaled`, `convPow_rescaled`, `logCoeff_rescaled`, `sum_j_logCoeff_disk_le`:
   geometric first-moment bound on disk of radius R with ρ = S R < 1.
5. `fourier_first_moment_budget`, `fourier_first_moment_disk`: geometric coefficient budget lemmas.
6. `fourier_truncation_tail`: geometric decay of the truncation remainder for order L on disk of radius s.
7. `spectral_floor_log_lipschitz`: Lipschitz continuity of the log-spectral transformation under the spectral
   floor f_hat = max(f_tilde, f_lower / 2) via Mathlib's Mean Value Theorem on [f_lower / 2, ∞).
8. `spectral_floor_lipschitz`: projection and Lipschitz property of the spectral floor.
9. `quadrature_fourier_error`: bound on the normalized `M`-point equidistant quadrature error from
   cell-average deviations via `Finset` summation.
10. `transfer_factor_error`: connects log-spectral Fourier estimation error, truncation tail, and the
    first-moment budget to the error in the transfer factor Q̂(z) - Q(z).
11. `transfer_function_error`: bounds the causal transfer error ‖Ĵ - J‖_s on circle of radius s > 0.
12. `incidence_estimator_bound`: decomposes `|∑ ĝ_m Ĵ_m - ΔS|` into transfer-function error
    weighted by the `s⁻¹`-norm of `ĝ`, pilot weight error scaled by `‖J‖_∞`, and truncation tail.
13. `passive_incidence_end_to_end`: end-to-end assembly chaining the spectral floor, DFT quadrature,
    series truncation tail, transfer factor and function bounds, and pilot error to the final incidence error.

Standard axioms only (propext, Classical.choice, Quot.sound).
-/

open Finset BigOperators HasAntidiagonal Real

namespace Paper1Revision14

/-! ## 1. Derivation of First-Moment Budget from Primitives -/

lemma geom_deriv_id (r : ℝ) : ∀ N : ℕ,
    (1 - r) * ∑ l ∈ range N, (l + 1 : ℝ) * r ^ l = (∑ l ∈ range N, r ^ l) - (N : ℝ) * r ^ N
  | 0 => by simp
  | N + 1 => by
      have ih := geom_deriv_id r N
      rw [sum_range_succ, mul_add, ih, sum_range_succ]
      push_cast
      ring

lemma geom_deriv_le (r r_bar : ℝ) (hr0 : 0 ≤ r) (hr : r ≤ r_bar) (hr_bar : r_bar < 1) (N : ℕ) :
    (1 - r) * ∑ l ∈ range N, (l + 1 : ℝ) * r ^ l ≤ 1 / (1 - r_bar) := by
  have hid := geom_deriv_id r N
  have h1r : 0 < 1 - r := by linarith
  have h1rbar : 0 < 1 - r_bar := by linarith
  have hNr : 0 ≤ (N : ℝ) * r ^ N := mul_nonneg (Nat.cast_nonneg N) (pow_nonneg hr0 N)
  have hle1 : (1 - r) * ∑ l ∈ range N, (l + 1 : ℝ) * r ^ l ≤ ∑ l ∈ range N, r ^ l := by
    linarith [hid]
  have hgeom : (∑ l ∈ range N, r ^ l) * (1 - r) = 1 - r ^ N := by
    have := geom_sum_mul r N
    linarith [this]
  have _hrN : 0 ≤ r ^ N := pow_nonneg hr0 N
  have hle2 : ∑ l ∈ range N, r ^ l ≤ 1 / (1 - r) := by
    rw [le_div_iff₀ h1r]
    linarith [hgeom]
  have hle3 : (1 : ℝ) / (1 - r) ≤ 1 / (1 - r_bar) := by
    refine div_le_div_of_nonneg_left (by norm_num) h1rbar (by linarith)
  exact le_trans hle1 (le_trans hle2 hle3)

lemma phi_sum_id {ι : Type*} (s : Finset ι) (q r : ι → ℝ)
    (a kappa : ℝ) (phi : ℕ → ℝ)
    (hphi1 : phi 1 = a + kappa * ∑ i ∈ s, q i * (1 - r i))
    (hphisucc : ∀ m : ℕ, 1 ≤ m → phi (m + 1) = kappa * ∑ i ∈ s, q i * (1 - r i) * (r i) ^ m) :
    ∀ N : ℕ, ∑ m ∈ range (N + 1), (m + 1 : ℝ) * phi (m + 1) =
      a + kappa * ∑ i ∈ s, q i * (1 - r i) * ∑ l ∈ range (N + 1), (l + 1 : ℝ) * (r i) ^ l
  | 0 => by
      simp only [sum_range_one, Nat.cast_zero, zero_add, one_mul, pow_zero]
      rw [hphi1]
      refine congrArg (a + kappa * ·) ?_
      refine sum_congr rfl (fun i _ => by ring)
  | N + 1 => by
      have ih := phi_sum_id s q r a kappa phi hphi1 hphisucc N
      rw [sum_range_succ, ih]
      have hsucc : phi (N + 1 + 1) = kappa * ∑ i ∈ s, q i * (1 - r i) * (r i) ^ (N + 1) :=
        hphisucc (N + 1) (by omega)
      rw [hsucc]
      have h_rhs_split : ∀ i, ∑ l ∈ range (N + 1 + 1), (l + 1 : ℝ) * (r i) ^ l =
          (∑ l ∈ range (N + 1), (l + 1 : ℝ) * (r i) ^ l) + ((N + 1 + 1 : ℕ) : ℝ) * (r i) ^ (N + 1) := by
        intro i; rw [sum_range_succ]; push_cast; ring
      simp_rw [h_rhs_split, mul_add, sum_add_distrib, mul_add]
      rw [add_assoc]
      refine congrArg (a + ·) ?_
      refine congrArg (kappa * (∑ i ∈ s, q i * (1 - r i) * ∑ l ∈ range (N + 1), (l + 1 : ℝ) * r i ^ l) + ·) ?_
      have : (↑(N + 1) + 1 : ℝ) * (kappa * ∑ i ∈ s, q i * (1 - r i) * r i ^ (N + 1)) =
          kappa * ∑ x ∈ s, q x * (1 - r x) * (↑(N + 1 + 1) * r x ^ (N + 1)) := by
        rw [mul_comm (↑(N + 1) + 1 : ℝ), mul_assoc]
        refine congrArg (kappa * ·) ?_
        rw [sum_mul]
        refine sum_congr rfl (fun i _ => ?_)
        push_cast; ring
      rw [this]

/-- 1. First-moment bound: M_1(ϕ) = ∑_{m=1}^N m ϕ_m ≤ S̄ / (1 - r̄) directly from stationary
positive feedback price law primitives. -/
theorem fourier_first_moment_bound {ι : Type*} (s : Finset ι) (q r : ι → ℝ)
    (a kappa S_bar r_bar : ℝ) (ha : 0 ≤ a) (hkappa : 0 ≤ kappa)
    (hq : ∀ i ∈ s, 0 ≤ q i) (hr0 : ∀ i ∈ s, 0 ≤ r i)
    (hr : ∀ i ∈ s, r i ≤ r_bar) (_hr_bar0 : 0 ≤ r_bar) (hr_bar1 : r_bar < 1)
    (hS_bar : a + kappa * ∑ i ∈ s, q i ≤ S_bar)
    (phi : ℕ → ℝ) (hphi0 : phi 0 = 0)
    (hphi1 : phi 1 = a + kappa * ∑ i ∈ s, q i * (1 - r i))
    (hphisucc : ∀ m : ℕ, 1 ≤ m → phi (m + 1) = kappa * ∑ i ∈ s, q i * (1 - r i) * (r i) ^ m)
    (N : ℕ) :
    ∑ m ∈ range (N + 1), (m : ℝ) * phi m ≤ S_bar / (1 - r_bar) := by
  have h1rbar : 0 < 1 - r_bar := by linarith
  have hq_sum_nonneg : 0 ≤ ∑ i ∈ s, q i := sum_nonneg (fun i hi => hq i hi)
  have hSbar0 : 0 ≤ S_bar := by
    have : 0 ≤ kappa * ∑ i ∈ s, q i := mul_nonneg hkappa hq_sum_nonneg
    linarith [hS_bar]
  rcases N with _ | N
  · simp [hphi0]
    exact div_nonneg hSbar0 h1rbar.le
  · have hsum_shift : ∑ m ∈ range (N + 2), (m : ℝ) * phi m =
        ∑ m ∈ range (N + 1), (m + 1 : ℝ) * phi (m + 1) := by
      rw [sum_range_succ']
      simp [hphi0]
    rw [hsum_shift, phi_sum_id s q r a kappa phi hphi1 hphisucc N]
    have h_cohort_le : ∀ i ∈ s, (1 - r i) * ∑ l ∈ range (N + 1), (l + 1 : ℝ) * (r i) ^ l ≤ 1 / (1 - r_bar) :=
      fun i hi => geom_deriv_le (r i) r_bar (hr0 i hi) (hr i hi) hr_bar1 (N + 1)
    have h_inner_le : ∑ i ∈ s, q i * ((1 - r i) * ∑ l ∈ range (N + 1), (l + 1 : ℝ) * (r i) ^ l) ≤
        ∑ i ∈ s, q i * (1 / (1 - r_bar)) := by
      refine sum_le_sum (fun i hi => ?_)
      exact mul_le_mul_of_nonneg_left (h_cohort_le i hi) (hq i hi)
    have h_mul_assoc : ∑ i ∈ s, q i * (1 - r i) * ∑ l ∈ range (N + 1), (l + 1 : ℝ) * (r i) ^ l =
        ∑ i ∈ s, q i * ((1 - r i) * ∑ l ∈ range (N + 1), (l + 1 : ℝ) * (r i) ^ l) := by
      refine sum_congr rfl (fun i _ => by ring)
    rw [h_mul_assoc]
    have h_scaled : kappa * ∑ i ∈ s, q i * ((1 - r i) * ∑ l ∈ range (N + 1), (l + 1 : ℝ) * (r i) ^ l) ≤
        kappa * ((∑ i ∈ s, q i) * (1 / (1 - r_bar))) := by
      have : ∑ i ∈ s, q i * (1 / (1 - r_bar)) = (∑ i ∈ s, q i) * (1 / (1 - r_bar)) := by
        rw [← sum_mul]
      rw [← this]
      exact mul_le_mul_of_nonneg_left h_inner_le hkappa
    have h_a_le : a ≤ a * (1 / (1 - r_bar)) := by
      have : 1 ≤ 1 / (1 - r_bar) := by
        rw [one_le_div₀ h1rbar]
        linarith
      calc a = a * 1 := by ring
        _ ≤ a * (1 / (1 - r_bar)) := mul_le_mul_of_nonneg_left this ha
    calc a + kappa * ∑ i ∈ s, q i * ((1 - r i) * ∑ l ∈ range (N + 1), (l + 1 : ℝ) * (r i) ^ l)
        ≤ a * (1 / (1 - r_bar)) + kappa * ((∑ i ∈ s, q i) * (1 / (1 - r_bar))) := add_le_add h_a_le h_scaled
      _ = (a + kappa * ∑ i ∈ s, q i) * (1 / (1 - r_bar)) := by ring
      _ ≤ S_bar * (1 / (1 - r_bar)) := mul_le_mul_of_nonneg_right hS_bar (by positivity)
      _ = S_bar / (1 - r_bar) := by ring

/-! ## 2. Convolution Powers and Leibniz First-Moment Bound -/

lemma double_sum_le {g h : ℕ → ℝ} (hg : ∀ a, 0 ≤ g a) (hh : ∀ b, 0 ≤ h b) (N : ℕ) :
    (∑ j ∈ range (N + 1), ∑ a ∈ range (j + 1), g a * h (j - a)) ≤
      (∑ a ∈ range (N + 1), g a) * (∑ b ∈ range (N + 1), h b) := by
  have h_anti : ∀ j, (∑ a ∈ range (j + 1), g a * h (j - a)) =
      ∑ p ∈ (antidiagonal j : Finset (ℕ × ℕ)), g p.1 * h p.2 := by
    intro j
    exact (Finset.Nat.sum_antidiagonal_eq_sum_range_succ (fun a b => g a * h b) j).symm
  simp_rw [h_anti]
  have h_disj : (range (N + 1) : Set ℕ).PairwiseDisjoint (fun j => (antidiagonal j : Finset (ℕ × ℕ))) := by
    intro j₁ _ j₂ _ hne
    dsimp [Function.onFun]
    rw [Finset.disjoint_left]
    intro p hp1 hp2
    rw [HasAntidiagonal.mem_antidiagonal] at hp1 hp2
    omega
  rw [← sum_biUnion h_disj]
  have h_sub : (range (N + 1)).biUnion (fun j => (antidiagonal j : Finset (ℕ × ℕ))) ⊆ (range (N + 1)) ×ˢ (range (N + 1)) := by
    intro p hp
    rcases mem_biUnion.mp hp with ⟨j, hj, hpj⟩
    rw [mem_range] at hj
    rw [HasAntidiagonal.mem_antidiagonal] at hpj
    rw [mem_product, mem_range, mem_range]
    exact ⟨by omega, by omega⟩
  have h_pos : ∀ p ∈ (range (N + 1)) ×ˢ (range (N + 1)), 0 ≤ g p.1 * h p.2 := by
    intro p _
    exact mul_nonneg (hg p.1) (hh p.2)
  have h_le := sum_le_sum_of_subset_of_nonneg h_sub (fun p _ _ => h_pos p (by assumption))
  refine le_trans h_le ?_
  rw [sum_product]
  dsimp only
  rw [← sum_mul_sum]

def convPow (phi : ℕ → ℝ) : ℕ → ℕ → ℝ
  | 0, j => if j = 0 then 1 else 0
  | n + 1, j => ∑ a ∈ range (j + 1), convPow phi n a * phi (j - a)

lemma convPow_nonneg {phi : ℕ → ℝ} (hphi : ∀ m, 0 ≤ phi m) :
    ∀ n j, 0 ≤ convPow phi n j
  | 0, j => by simp only [convPow]; split_ifs <;> norm_num
  | n + 1, j => sum_nonneg fun a _ => mul_nonneg (convPow_nonneg hphi n a) (hphi _)

lemma convPow_one (phi : ℕ → ℝ) (j : ℕ) : convPow phi 1 j = phi j := by
  dsimp [convPow]
  have h0 : 0 ∈ range (j + 1) := mem_range.mpr (Nat.succ_pos j)
  have h_zero : ∀ b ∈ range (j + 1), b ≠ 0 → convPow phi 0 b * phi (j - b) = 0 := by
    intro b _ hb
    dsimp [convPow]
    split_ifs with h
    · contradiction
    · ring
  rw [sum_eq_single_of_mem 0 h0 (by intro b hb hbne; exact h_zero b hb hbne)]
  dsimp [convPow]
  ring

lemma sum_convPow_le {phi : ℕ → ℝ} {S : ℝ}
    (hphi : ∀ m, 0 ≤ phi m) (hS0 : 0 ≤ S)
    (hsum : ∀ N, ∑ m ∈ range (N + 1), phi m ≤ S) :
    ∀ n N, ∑ j ∈ range (N + 1), convPow phi n j ≤ S ^ n
  | 0, N => by
      rw [pow_zero]
      have h0 : (0 : ℕ) ∈ range (N + 1) := mem_range.mpr (Nat.succ_pos N)
      have hzero : ∀ j ∈ range (N + 1), convPow phi 0 j = if j = 0 then 1 else 0 := fun j _ => rfl
      rw [sum_congr rfl hzero]
      have : ∑ j ∈ range (N + 1), (if j = 0 then (1 : ℝ) else 0) = 1 := by
        rw [sum_eq_single_of_mem 0 h0]
        · simp
        · intro b _ hbne; simp [hbne]
      rw [this]
  | n + 1, N => by
      calc ∑ j ∈ range (N + 1), convPow phi (n + 1) j
          = ∑ j ∈ range (N + 1), ∑ a ∈ range (j + 1), convPow phi n a * phi (j - a) := rfl
        _ ≤ (∑ a ∈ range (N + 1), convPow phi n a) * (∑ b ∈ range (N + 1), phi b) :=
            double_sum_le (convPow_nonneg hphi n) hphi N
        _ ≤ S ^ n * S := mul_le_mul (sum_convPow_le hphi hS0 hsum n N) (hsum N)
            (sum_nonneg fun _ _ => hphi _) (pow_nonneg hS0 n)
        _ = S ^ (n + 1) := by ring

lemma sum_mul_convPow_le {phi : ℕ → ℝ} {S M1 : ℝ}
    (hphi : ∀ m, 0 ≤ phi m) (hS0 : 0 ≤ S) (hM1 : 0 ≤ M1)
    (hsum : ∀ N, ∑ m ∈ range (N + 1), phi m ≤ S)
    (hm1 : ∀ N, ∑ m ∈ range (N + 1), (m : ℝ) * phi m ≤ M1) :
    ∀ n N, ∑ j ∈ range (N + 1), (j : ℝ) * convPow phi (n + 1) j ≤ ((n + 1 : ℕ) : ℝ) * S ^ n * M1
  | 0, N => by
      have h_eq : ∑ j ∈ range (N + 1), (j : ℝ) * convPow phi 1 j = ∑ j ∈ range (N + 1), (j : ℝ) * phi j :=
        sum_congr rfl (fun j _ => by rw [convPow_one])
      rw [h_eq]
      have := hm1 N
      have : M1 = ((0 + 1 : ℕ) : ℝ) * S ^ 0 * M1 := by push_cast; ring
      linarith
  | n + 1, N => by
      have h_split : ∀ (j : ℕ), (j : ℝ) * convPow phi (n + 2) j =
          ∑ a ∈ range (j + 1), ((a : ℝ) * convPow phi (n + 1) a) * phi (j - a) +
          ∑ a ∈ range (j + 1), convPow phi (n + 1) a * (((j - a : ℕ) : ℝ) * phi (j - a)) := by
        intro j
        change (j : ℝ) * (∑ a ∈ range (j + 1), convPow phi (n + 1) a * phi (j - a)) = _
        rw [mul_sum, ← sum_add_distrib]
        refine sum_congr rfl (fun a ha => ?_)
        have haj : a ≤ j := Nat.lt_succ_iff.mp (mem_range.mp ha)
        have hj_nat : a + (j - a) = j := Nat.add_sub_of_le haj
        have hj : (j : ℝ) = (a : ℝ) + ((j - a : ℕ) : ℝ) := by
          exact_mod_cast hj_nat.symm
        calc (j : ℝ) * (convPow phi (n + 1) a * phi (j - a))
            = ((a : ℝ) + ((j - a : ℕ) : ℝ)) * (convPow phi (n + 1) a * phi (j - a)) := by rw [hj]
          _ = ((a : ℝ) * convPow phi (n + 1) a) * phi (j - a) +
              convPow phi (n + 1) a * (((j - a : ℕ) : ℝ) * phi (j - a)) := by ring
      have h_sum_split : ∑ j ∈ range (N + 1), (j : ℝ) * convPow phi (n + 2) j =
          (∑ j ∈ range (N + 1), ∑ a ∈ range (j + 1), ((a : ℝ) * convPow phi (n + 1) a) * phi (j - a)) +
          (∑ j ∈ range (N + 1), ∑ a ∈ range (j + 1), convPow phi (n + 1) a * (((j - a : ℕ) : ℝ) * phi (j - a))) := by
        rw [← sum_add_distrib]
        exact sum_congr rfl (fun j _ => h_split j)
      rw [h_sum_split]
      have h_part1 : (∑ j ∈ range (N + 1), ∑ a ∈ range (j + 1), ((a : ℝ) * convPow phi (n + 1) a) * phi (j - a)) ≤
          (((n + 1 : ℕ) : ℝ) * S ^ n * M1) * S := by
        have hg_pos : ∀ (a : ℕ), 0 ≤ (a : ℝ) * convPow phi (n + 1) a :=
          fun a => mul_nonneg (Nat.cast_nonneg a) (convPow_nonneg hphi _ a)
        have h_double := double_sum_le hg_pos hphi N
        have h_ind := sum_mul_convPow_le hphi hS0 hM1 hsum hm1 n N
        exact le_trans h_double (mul_le_mul h_ind (hsum N) (sum_nonneg fun _ _ => hphi _) (by positivity))
      have h_part2 : (∑ j ∈ range (N + 1), ∑ a ∈ range (j + 1), convPow phi (n + 1) a * (((j - a : ℕ) : ℝ) * phi (j - a))) ≤
          (S ^ (n + 1)) * M1 := by
        have hh_pos : ∀ (b : ℕ), 0 ≤ (b : ℝ) * phi b :=
          fun b => mul_nonneg (Nat.cast_nonneg b) (hphi b)
        have h_double := double_sum_le (convPow_nonneg hphi (n + 1)) hh_pos N
        have h_pow := sum_convPow_le hphi hS0 hsum (n + 1) N
        exact le_trans h_double (mul_le_mul h_pow (hm1 N) (sum_nonneg fun _ _ => hh_pos _) (pow_nonneg hS0 _))
      have h_step : (((n + 1 : ℕ) : ℝ) * S ^ n * M1) * S + (S ^ (n + 1)) * M1 =
          ((n + 2 : ℕ) : ℝ) * S ^ (n + 1) * M1 := by
        push_cast
        ring
      linarith

/-! ## 3. Analytic Log Expansion and Double-Sum Swap -/

lemma triangular_sum_le (F : ℕ → ℕ → ℝ) (hF : ∀ j n, 0 ≤ F j n) :
    ∀ N : ℕ, (∑ j ∈ range (N + 1), ∑ n ∈ range j, F j n) ≤
      ∑ n ∈ range N, ∑ j ∈ range (N + 1), F j n
  | 0 => by simp
  | N + 1 => by
      have ih := triangular_sum_le F hF N
      rw [sum_range_succ (fun j => ∑ n ∈ range j, F j n)]
      rw [sum_range_succ (fun n => ∑ j ∈ range (N + 2), F j n)]
      have h1 : (∑ n ∈ range N, ∑ j ∈ range (N + 2), F j n) =
          (∑ n ∈ range N, ∑ j ∈ range (N + 1), F j n) + ∑ n ∈ range N, F (N + 1) n := by
        simp_rw [sum_range_succ (fun j => F j _)]
        rw [sum_add_distrib]
      rw [h1]
      have h2 : ∑ n ∈ range (N + 1), F (N + 1) n =
          (∑ n ∈ range N, F (N + 1) n) + F (N + 1) N := by
        rw [sum_range_succ]
      rw [h2]
      have h3 : ∑ j ∈ range (N + 2), F j N =
          (∑ j ∈ range (N + 1), F j N) + F (N + 1) N := by
        rw [sum_range_succ]
      rw [h3]
      have _h_nonneg1 : 0 ≤ ∑ j ∈ range (N + 1), F j N := sum_nonneg (fun j _ => hF j N)
      have _h_nonneg2 : 0 ≤ F (N + 1) N := hF (N + 1) N
      linarith

noncomputable def logCoeff (phi : ℕ → ℝ) (j : ℕ) : ℝ :=
  ∑ n ∈ range j, convPow phi (n + 1) j / ((n + 1 : ℕ) : ℝ)

/-- Log-coefficient first-moment bound: cancels 1/n with n identically in the double sum. -/
theorem sum_j_logCoeff_le {phi : ℕ → ℝ} {S M1 S_bar r_bar : ℝ}
    (hphi : ∀ m, 0 ≤ phi m) (hS0 : 0 ≤ S) (hS1 : S ≤ S_bar) (hSbar : S_bar < 1)
    (_hrbar0 : 0 ≤ r_bar) (_hrbar1 : r_bar < 1)
    (hM1 : 0 ≤ M1) (hM1_bound : M1 ≤ S_bar / (1 - r_bar))
    (hsum : ∀ N, ∑ m ∈ range (N + 1), phi m ≤ S)
    (hm1 : ∀ N, ∑ m ∈ range (N + 1), (m : ℝ) * phi m ≤ M1) (N : ℕ) :
    ∑ j ∈ range (N + 1), (j : ℝ) * |logCoeff phi j| ≤ S_bar / ((1 - S_bar) * (1 - r_bar)) := by
  have _hS_lt_1 : S < 1 := lt_of_le_of_lt hS1 hSbar
  have h1S : 0 < 1 - S := by linarith
  have _h1Sbar : 0 < 1 - S_bar := by linarith
  have _h1rbar : 0 < 1 - r_bar := by linarith
  have h_abs : ∀ j, |logCoeff phi j| = logCoeff phi j := by
    intro j
    refine abs_of_nonneg ?_
    dsimp [logCoeff]
    refine sum_nonneg (fun n _ => ?_)
    exact div_nonneg (convPow_nonneg hphi _ _) (by positivity)
  have h_nonneg_term : ∀ (j n : ℕ), 0 ≤ (j : ℝ) * (convPow phi (n + 1) j / ((n + 1 : ℕ) : ℝ)) := by
    intro j n
    exact mul_nonneg (Nat.cast_nonneg j) (div_nonneg (convPow_nonneg hphi _ _) (by positivity))
  have h_diag_le : ∑ j ∈ range (N + 1), (j : ℝ) * logCoeff phi j ≤
      ∑ n ∈ range N, ∑ j ∈ range (N + 1), (j : ℝ) * (convPow phi (n + 1) j / ((n + 1 : ℕ) : ℝ)) := by
    have h_rw : ∑ j ∈ range (N + 1), (j : ℝ) * logCoeff phi j =
        ∑ j ∈ range (N + 1), ∑ n ∈ range j, (j : ℝ) * (convPow phi (n + 1) j / ((n + 1 : ℕ) : ℝ)) := by
      refine sum_congr rfl (fun j _ => ?_)
      dsimp [logCoeff]
      rw [mul_sum]
    rw [h_rw]
    exact triangular_sum_le (fun j n => (j : ℝ) * (convPow phi (n + 1) j / ((n + 1 : ℕ) : ℝ))) h_nonneg_term N
  have h_bound_inner : ∀ n ∈ range N,
      ∑ j ∈ range (N + 1), (j : ℝ) * (convPow phi (n + 1) j / ((n + 1 : ℕ) : ℝ)) ≤ S ^ n * M1 := by
    intro n _
    have h_factor : ∑ j ∈ range (N + 1), (j : ℝ) * (convPow phi (n + 1) j / ((n + 1 : ℕ) : ℝ)) =
        (1 / ((n + 1 : ℕ) : ℝ)) * ∑ j ∈ range (N + 1), (j : ℝ) * convPow phi (n + 1) j := by
      rw [mul_sum]
      refine sum_congr rfl (fun j _ => by ring)
    rw [h_factor]
    have h_le := sum_mul_convPow_le hphi hS0 hM1 hsum hm1 n N
    have hpos : 0 < ((n + 1 : ℕ) : ℝ) := by positivity
    have : (1 / ((n + 1 : ℕ) : ℝ)) * (((n + 1 : ℕ) : ℝ) * S ^ n * M1) = S ^ n * M1 := by
      field_simp [hpos.ne']
    calc (1 / ((n + 1 : ℕ) : ℝ)) * ∑ j ∈ range (N + 1), (j : ℝ) * convPow phi (n + 1) j
        ≤ (1 / ((n + 1 : ℕ) : ℝ)) * (((n + 1 : ℕ) : ℝ) * S ^ n * M1) :=
          mul_le_mul_of_nonneg_left h_le (by positivity)
      _ = S ^ n * M1 := this
  have h_geom_S : ∑ n ∈ range N, S ^ n ≤ 1 / (1 - S) := by
    have hgeom_le : (∑ n ∈ range N, S ^ n) * (1 - S) = 1 - S ^ N := by
      have := geom_sum_mul S N
      linarith [this]
    have : 1 - S ^ N ≤ 1 := by
      have : 0 ≤ S ^ N := by positivity
      linarith
    rw [le_div_iff₀ h1S]
    linarith [hgeom_le]
  calc ∑ j ∈ range (N + 1), (j : ℝ) * |logCoeff phi j|
      = ∑ j ∈ range (N + 1), (j : ℝ) * logCoeff phi j := sum_congr rfl (fun j _ => by rw [h_abs])
    _ ≤ ∑ n ∈ range N, ∑ j ∈ range (N + 1), (j : ℝ) * (convPow phi (n + 1) j / ((n + 1 : ℕ) : ℝ)) := h_diag_le
    _ ≤ ∑ n ∈ range N, S ^ n * M1 := sum_le_sum (fun n hn => h_bound_inner n hn)
    _ = (∑ n ∈ range N, S ^ n) * M1 := by rw [← sum_mul]
    _ ≤ (1 / (1 - S)) * M1 := mul_le_mul_of_nonneg_right h_geom_S hM1
    _ = M1 / (1 - S) := by ring
    _ ≤ (S_bar / (1 - r_bar)) / (1 - S_bar) := by
        have h_den : 1 - S_bar ≤ 1 - S := by linarith
        have h_num : M1 ≤ S_bar / (1 - r_bar) := hM1_bound
        have h_frac1 : M1 / (1 - S) ≤ (S_bar / (1 - r_bar)) / (1 - S) :=
          div_le_div_of_nonneg_right h_num (by linarith)
        have h_frac2 : (S_bar / (1 - r_bar)) / (1 - S) ≤ (S_bar / (1 - r_bar)) / (1 - S_bar) := by
          have h_num_nonneg : 0 ≤ S_bar / (1 - r_bar) := div_nonneg (by linarith) (by linarith)
          exact div_le_div_of_nonneg_left h_num_nonneg (by linarith) h_den
        exact le_trans h_frac1 h_frac2
    _ = S_bar / ((1 - S_bar) * (1 - r_bar)) := by
        rw [div_div, mul_comm (1 - r_bar)]

/-! ## 4. Disk Rescaling -/

def phi_rescaled (phi : ℕ → ℝ) (R : ℝ) (m : ℕ) : ℝ := phi m * R ^ m

lemma convPow_rescaled (phi : ℕ → ℝ) (R : ℝ) :
    ∀ n j : ℕ, convPow (phi_rescaled phi R) n j = convPow phi n j * R ^ j
  | 0, j => by
      dsimp [convPow, phi_rescaled]
      split_ifs with hj
      · subst hj; simp
      · simp
  | n + 1, j => by
      dsimp [convPow, phi_rescaled]
      have ih := convPow_rescaled phi R n
      have h_step : ∀ a ∈ range (j + 1),
          convPow (phi_rescaled phi R) n a * (phi (j - a) * R ^ (j - a)) =
          (convPow phi n a * phi (j - a)) * R ^ j := by
        intro a ha
        rw [ih a]
        have haj : a ≤ j := Nat.lt_succ_iff.mp (mem_range.mp ha)
        have : R ^ a * R ^ (j - a) = R ^ j := by
          rw [← pow_add, Nat.add_sub_cancel' haj]
        calc (convPow phi n a * R ^ a) * (phi (j - a) * R ^ (j - a))
            = (convPow phi n a * phi (j - a)) * (R ^ a * R ^ (j - a)) := by ring
          _ = (convPow phi n a * phi (j - a)) * R ^ j := by rw [this]
      rw [sum_congr rfl h_step, ← sum_mul]

lemma logCoeff_rescaled (phi : ℕ → ℝ) (R : ℝ) (j : ℕ) :
    logCoeff (phi_rescaled phi R) j = logCoeff phi j * R ^ j := by
  dsimp [logCoeff]
  have h_step : ∀ n ∈ range j,
      convPow (phi_rescaled phi R) (n + 1) j / ((n + 1 : ℕ) : ℝ) =
      (convPow phi (n + 1) j / ((n + 1 : ℕ) : ℝ)) * R ^ j := by
    intro n _
    rw [convPow_rescaled]
    ring
  rw [sum_congr rfl h_step, ← sum_mul]

theorem sum_j_logCoeff_disk_le {phi : ℕ → ℝ} {S_R M1_R S_bar_R r_bar : ℝ} {R : ℝ}
    (hphi : ∀ m, 0 ≤ phi m) (hR0 : 0 ≤ R) (hS_R0 : 0 ≤ S_R) (hS_R1 : S_R ≤ S_bar_R)
    (hSbar_R : S_bar_R < 1) (hrbar0 : 0 ≤ r_bar) (hrbar1 : r_bar < 1)
    (hM1_R : 0 ≤ M1_R) (hM1_bound : M1_R ≤ S_bar_R / (1 - r_bar))
    (hsum : ∀ N, ∑ m ∈ range (N + 1), phi_rescaled phi R m ≤ S_R)
    (hm1 : ∀ N, ∑ m ∈ range (N + 1), (m : ℝ) * phi_rescaled phi R m ≤ M1_R) (N : ℕ) :
    ∑ j ∈ range (N + 1), (j : ℝ) * |logCoeff phi j| * R ^ j ≤ S_bar_R / ((1 - S_bar_R) * (1 - r_bar)) := by
  have hphi_R : ∀ m, 0 ≤ phi_rescaled phi R m := fun m => mul_nonneg (hphi m) (pow_nonneg hR0 m)
  have h_disk := sum_j_logCoeff_le hphi_R hS_R0 hS_R1 hSbar_R hrbar0 hrbar1 hM1_R hM1_bound hsum hm1 N
  have h_abs_rw : ∀ j, |logCoeff phi j| * R ^ j = |logCoeff (phi_rescaled phi R) j| := by
    intro j
    rw [logCoeff_rescaled]
    rw [abs_mul, abs_of_nonneg (pow_nonneg hR0 j)]
  have h_sum_rw : ∑ j ∈ range (N + 1), (j : ℝ) * |logCoeff phi j| * R ^ j =
      ∑ j ∈ range (N + 1), (j : ℝ) * |logCoeff (phi_rescaled phi R) j| := by
    refine sum_congr rfl (fun j _ => ?_)
    rw [mul_assoc, h_abs_rw]
  rw [h_sum_rw]
  exact h_disk

/-! ## 5. Original Geometric Moment Lemmas -/

/-- Fourier first-moment budget. If the log-spectral Fourier coefficients satisfy the geometric
bound |ℓ_j| ≤ S^j / j for all j ≥ 1, then the first Fourier moment sum satisfies
∑_{j=0}^{N-1} (j+1) |ℓ_{j+1}| ≤ S / (1 - S) for every N. -/
theorem fourier_first_moment_budget (S : ℝ) (hS0 : 0 ≤ S) (hS1 : S < 1) (ℓ : ℕ → ℝ)
    (hℓ : ∀ j : ℕ, |ℓ (j + 1)| ≤ S ^ (j + 1) / (j + 1 : ℝ)) (N : ℕ) :
    ∑ j ∈ range N, (j + 1 : ℝ) * |ℓ (j + 1)| ≤ S / (1 - S) := by
  have h1S : 0 < 1 - S := by linarith
  have hgeom : ∀ n : ℕ, ∑ j ∈ range n, S ^ (j + 1) ≤ S / (1 - S) := by
    intro n
    have hsum : ∑ j ∈ range n, S ^ (j + 1) = S * ∑ j ∈ range n, S ^ j := by
      rw [Finset.mul_sum]
      refine Finset.sum_congr rfl (fun j _ => by ring)
    rw [hsum]
    have hgeom_le : (∑ j ∈ range n, S ^ j) * (1 - S) = 1 - S ^ n := by
      have := geom_sum_mul S n
      linarith [this]
    have _hSn : 0 ≤ S ^ n := by positivity
    have hle : ∑ j ∈ range n, S ^ j ≤ 1 / (1 - S) := by
      rw [le_div_iff₀ h1S]
      linarith [hgeom_le]
    calc S * (∑ j ∈ range n, S ^ j) ≤ S * (1 / (1 - S)) := mul_le_mul_of_nonneg_left hle hS0
      _ = S / (1 - S) := by ring
  calc ∑ j ∈ range N, (j + 1 : ℝ) * |ℓ (j + 1)|
      ≤ ∑ j ∈ range N, (j + 1 : ℝ) * (S ^ (j + 1) / (j + 1 : ℝ)) := by
        refine Finset.sum_le_sum (fun j _ => ?_)
        have hj : 0 < (j + 1 : ℝ) := by positivity
        exact mul_le_mul_of_nonneg_left (hℓ j) hj.le
    _ = ∑ j ∈ range N, S ^ (j + 1) := by
        refine Finset.sum_congr rfl (fun j _ => ?_)
        have _hj : (j + 1 : ℝ) ≠ 0 := by positivity
        field_simp
    _ ≤ S / (1 - S) := hgeom N

/-- Fourier first-moment budget on disk of radius R. For R ≥ 1 and ρ = S * R < 1,
the weighted first Fourier moment satisfies ∑_{j=0}^{N-1} (j+1) |ℓ_{j+1}| R^{j+1} ≤ ρ / (1 - ρ). -/
theorem fourier_first_moment_disk (S R ρ : ℝ) (hS0 : 0 ≤ S) (_hR0 : 0 ≤ R) (hρ : ρ = S * R)
    (hρ1 : ρ < 1) (ℓ : ℕ → ℝ) (hℓ : ∀ j : ℕ, |ℓ (j + 1)| ≤ S ^ (j + 1) / (j + 1 : ℝ)) (N : ℕ) :
    ∑ j ∈ range N, (j + 1 : ℝ) * |ℓ (j + 1)| * R ^ (j + 1) ≤ ρ / (1 - ρ) := by
  have hρ0 : 0 ≤ ρ := by rw [hρ]; positivity
  have h1ρ : 0 < 1 - ρ := by linarith
  have hgeom : ∀ n : ℕ, ∑ j ∈ range n, ρ ^ (j + 1) ≤ ρ / (1 - ρ) := by
    intro n
    have hsum : ∑ j ∈ range n, ρ ^ (j + 1) = ρ * ∑ j ∈ range n, ρ ^ j := by
      rw [Finset.mul_sum]
      refine Finset.sum_congr rfl (fun j _ => by ring)
    rw [hsum]
    have hgeom_le : (∑ j ∈ range n, ρ ^ j) * (1 - ρ) = 1 - ρ ^ n := by
      have := geom_sum_mul ρ n
      linarith [this]
    have hle : ∑ j ∈ range n, ρ ^ j ≤ 1 / (1 - ρ) := by
      rw [le_div_iff₀ h1ρ]
      have : 0 ≤ ρ ^ n := by positivity
      linarith [hgeom_le]
    calc ρ * (∑ j ∈ range n, ρ ^ j) ≤ ρ * (1 / (1 - ρ)) := mul_le_mul_of_nonneg_left hle hρ0
      _ = ρ / (1 - ρ) := by ring
  calc ∑ j ∈ range N, (j + 1 : ℝ) * |ℓ (j + 1)| * R ^ (j + 1)
      ≤ ∑ j ∈ range N, (j + 1 : ℝ) * (S ^ (j + 1) / (j + 1 : ℝ)) * R ^ (j + 1) := by
        refine Finset.sum_le_sum (fun j _ => ?_)
        have hj : 0 < (j + 1 : ℝ) := by positivity
        have hRpow : 0 ≤ R ^ (j + 1) := by positivity
        have h1 := mul_le_mul_of_nonneg_left (hℓ j) hj.le
        exact mul_le_mul_of_nonneg_right h1 hRpow
    _ = ∑ j ∈ range N, ρ ^ (j + 1) := by
        refine Finset.sum_congr rfl (fun j _ => ?_)
        have _hj : (j + 1 : ℝ) ≠ 0 := by positivity
        rw [hρ, mul_pow]
        field_simp
    _ ≤ ρ / (1 - ρ) := hgeom N

/-- Truncation error: the tail of the Fourier series of order > L on circle of radius s ≤ 1
decays geometrically as (S * s)^{L+1} / (1 - S * s). -/
theorem fourier_truncation_tail (S s ρ : ℝ) (_hS0 : 0 ≤ S) (_hs0 : 0 ≤ s) (hρ : ρ = S * s)
    (hρ1 : ρ < 1) (ℓ : ℕ → ℝ) (hℓ : ∀ j : ℕ, |ℓ (j + 1)| ≤ S ^ (j + 1) / (j + 1 : ℝ))
    (L M : ℕ) :
    ∑ j ∈ range M, |ℓ (L + 1 + j)| * s ^ (L + 1 + j) ≤ ρ ^ (L + 1) / (1 - ρ) := by
  have _hρ0 : 0 ≤ ρ := by rw [hρ]; positivity
  have h1ρ : 0 < 1 - ρ := by linarith
  have hgeom : (∑ j ∈ range M, ρ ^ j) ≤ 1 / (1 - ρ) := by
    have hgeom_le : (∑ j ∈ range M, ρ ^ j) * (1 - ρ) = 1 - ρ ^ M := by
      have := geom_sum_mul ρ M
      linarith [this]
    have : 1 - ρ ^ M ≤ 1 := by
      have : 0 ≤ ρ ^ M := by positivity
      linarith
    rw [le_div_iff₀ h1ρ]
    linarith [hgeom_le]
  calc ∑ j ∈ range M, |ℓ (L + 1 + j)| * s ^ (L + 1 + j)
      ≤ ∑ j ∈ range M, (S ^ (L + 1 + j) / (L + 1 + j : ℝ)) * s ^ (L + 1 + j) := by
        refine Finset.sum_le_sum (fun j _ => ?_)
        have hspow : 0 ≤ s ^ (L + 1 + j) := by positivity
        have hle : |ℓ (L + 1 + j)| ≤ S ^ (L + 1 + j) / (L + 1 + j : ℝ) := by
          have h1 : L + 1 + j = (L + j) + 1 := by omega
          have h2 : (L + 1 + j : ℝ) = ((L + j : ℕ) : ℝ) + 1 := by push_cast; ring
          rw [h1, h2]
          exact hℓ (L + j)
        exact mul_le_mul_of_nonneg_right hle hspow
    _ ≤ ∑ j ∈ range M, S ^ (L + 1 + j) * s ^ (L + 1 + j) := by
        refine Finset.sum_le_sum (fun j _ => ?_)
        have _hj : (1 : ℝ) ≤ (L + 1 + j : ℝ) := by
          have : 1 ≤ L + 1 + j := by omega
          exact_mod_cast this
        have hdiv : S ^ (L + 1 + j) / (L + 1 + j : ℝ) ≤ S ^ (L + 1 + j) := by
          have _hSpow : 0 ≤ S ^ (L + 1 + j) := by positivity
          rw [div_le_iff₀ (by positivity)]
          nlinarith
        have hspow : 0 ≤ s ^ (L + 1 + j) := by positivity
        exact mul_le_mul_of_nonneg_right hdiv hspow
    _ = ∑ j ∈ range M, ρ ^ (L + 1 + j) := by
        refine Finset.sum_congr rfl (fun j _ => ?_)
        rw [hρ, mul_pow]
    _ = ρ ^ (L + 1) * ∑ j ∈ range M, ρ ^ j := by
        rw [Finset.mul_sum]
        refine Finset.sum_congr rfl (fun j _ => by rw [pow_add, mul_comm])
    _ ≤ ρ ^ (L + 1) * (1 / (1 - ρ)) := mul_le_mul_of_nonneg_left hgeom (by positivity)
    _ = ρ ^ (L + 1) / (1 - ρ) := by ring

/-! ## 6. Spectral Floor and Mean Value Theorem -/

/-- Spectral floor log-Lipschitz bound via Mathlib's Mean Value Theorem on [f_lower / 2, ∞). -/
theorem spectral_floor_log_lipschitz (f0 f_tilde f_lower : ℝ) (hf_low : 0 < f_lower)
    (hf0 : f_lower ≤ f0) :
    let f_hat := max f_tilde (f_lower / 2)
    |Real.log f_hat - Real.log f0| ≤ (2 / f_lower) * |f_tilde - f0| := by
  intro f_hat
  have h_proj : |f_hat - f0| ≤ |f_tilde - f0| := by
    dsimp [f_hat]
    rcases le_total f_tilde (f_lower / 2) with hle | hge
    · rw [max_eq_right hle]
      have : f_lower / 2 ≤ f0 := by linarith
      rw [abs_of_nonpos (by linarith)]
      rw [abs_of_nonpos (by linarith)]
      linarith
    · rw [max_eq_left hge]
  have h_lip : ∀ x y : ℝ, f_lower / 2 ≤ x → f_lower / 2 ≤ y →
      |Real.log x - Real.log y| ≤ (2 / f_lower) * |x - y| := by
    intro x y hx hy
    have h_pos_c : 0 < f_lower / 2 := by linarith
    have hx_pos : 0 < x := by linarith
    have hy_pos : 0 < y := by linarith
    rcases lt_trichotomy x y with hlt | heq | hgt
    · -- x < y
      have hfc : ContinuousOn Real.log (Set.Icc x y) := by
        refine Real.continuousOn_log.mono ?_
        intro z hz
        have : 0 < z := lt_of_lt_of_le hx_pos hz.1
        exact this.ne'
      have hdiff : ∀ z ∈ Set.Ioo x y, HasDerivAt Real.log z⁻¹ z := by
        intro z hz
        have : z ≠ 0 := (lt_of_lt_of_le hx_pos hz.1.le).ne'
        exact Real.hasDerivAt_log this
      obtain ⟨c, hc, h_mvt⟩ := exists_hasDerivAt_eq_slope Real.log (fun z => z⁻¹) hlt hfc hdiff
      have hc_gt : x < c := hc.1
      have hc_pos : 0 < c := lt_trans hx_pos hc_gt
      have hc_ge : f_lower / 2 < c := lt_of_le_of_lt hx hc_gt
      have h_inv : c⁻¹ < (f_lower / 2)⁻¹ := inv_lt_inv₀ hc_pos h_pos_c |>.mpr hc_ge
      have h_slope : (Real.log y - Real.log x) / (y - x) = c⁻¹ := h_mvt.symm
      have h_sub_pos : 0 < y - x := by linarith
      have h_log_sub : Real.log y - Real.log x = c⁻¹ * (y - x) := by
        rw [← h_slope]
        exact (div_mul_cancel₀ _ (ne_of_gt h_sub_pos)).symm
      have h_le : Real.log y - Real.log x ≤ (2 / f_lower) * (y - x) := by
        have : (f_lower / 2)⁻¹ = 2 / f_lower := by ring
        rw [this] at h_inv
        rw [h_log_sub]
        exact mul_le_mul_of_nonneg_right h_inv.le h_sub_pos.le
      have h_pos_diff : 0 ≤ Real.log y - Real.log x := by
        rw [h_log_sub]
        exact mul_nonneg (by positivity) h_sub_pos.le
      calc |Real.log x - Real.log y| = Real.log y - Real.log x := by rw [abs_sub_comm, abs_of_nonneg h_pos_diff]
        _ ≤ (2 / f_lower) * (y - x) := h_le
        _ = (2 / f_lower) * |x - y| := by rw [abs_sub_comm, abs_of_pos h_sub_pos]
    · rw [heq, sub_self, abs_zero, sub_self, abs_zero, mul_zero]
    · -- y < x
      have hfc : ContinuousOn Real.log (Set.Icc y x) := by
        refine Real.continuousOn_log.mono ?_
        intro z hz
        have : 0 < z := lt_of_lt_of_le hy_pos hz.1
        exact this.ne'
      have hdiff : ∀ z ∈ Set.Ioo y x, HasDerivAt Real.log z⁻¹ z := by
        intro z hz
        have : z ≠ 0 := (lt_of_lt_of_le hy_pos hz.1.le).ne'
        exact Real.hasDerivAt_log this
      obtain ⟨c, hc, h_mvt⟩ := exists_hasDerivAt_eq_slope Real.log (fun z => z⁻¹) hgt hfc hdiff
      have hc_gt : y < c := hc.1
      have hc_pos : 0 < c := lt_trans hy_pos hc_gt
      have hc_ge : f_lower / 2 < c := lt_of_le_of_lt hy hc_gt
      have h_inv : c⁻¹ < (f_lower / 2)⁻¹ := inv_lt_inv₀ hc_pos h_pos_c |>.mpr hc_ge
      have h_slope : (Real.log x - Real.log y) / (x - y) = c⁻¹ := h_mvt.symm
      have h_sub_pos : 0 < x - y := by linarith
      have h_log_sub : Real.log x - Real.log y = c⁻¹ * (x - y) := by
        rw [← h_slope]
        exact (div_mul_cancel₀ _ (ne_of_gt h_sub_pos)).symm
      have h_le : Real.log x - Real.log y ≤ (2 / f_lower) * (x - y) := by
        have : (f_lower / 2)⁻¹ = 2 / f_lower := by ring
        rw [this] at h_inv
        rw [h_log_sub]
        exact mul_le_mul_of_nonneg_right h_inv.le h_sub_pos.le
      have h_pos_diff : 0 ≤ Real.log x - Real.log y := by
        rw [h_log_sub]
        exact mul_nonneg (by positivity) h_sub_pos.le
      calc |Real.log x - Real.log y| = Real.log x - Real.log y := abs_of_nonneg h_pos_diff
        _ ≤ (2 / f_lower) * (x - y) := h_le
        _ = (2 / f_lower) * |x - y| := by rw [abs_of_pos h_sub_pos]
  have hx : f_lower / 2 ≤ f_hat := le_max_right f_tilde (f_lower / 2)
  have hy : f_lower / 2 ≤ f0 := by linarith
  have hlip := h_lip f_hat f0 hx hy
  calc |Real.log f_hat - Real.log f0| ≤ (2 / f_lower) * |f_hat - f0| := hlip
    _ ≤ (2 / f_lower) * |f_tilde - f0| := mul_le_mul_of_nonneg_left h_proj (by positivity)

/-- Spectral floor Lipschitz bound: the transformation x ↦ log(max(x, f_lower / 2)) is Lipschitz
with constant 2 / f_lower, so |log(f̂) - log(f)| ≤ (2 / f_lower) * |f̃ - f| whenever f ≥ f_lower. -/
theorem spectral_floor_lipschitz (f0 f_tilde f_lower : ℝ) (hf_low : 0 < f_lower)
    (hf0 : f_lower ≤ f0) (h_log_lip : ∀ x y : ℝ, f_lower / 2 ≤ x → f_lower / 2 ≤ y →
      |Real.log x - Real.log y| ≤ (2 / f_lower) * |x - y|) :
    let f_hat := max f_tilde (f_lower / 2)
    |Real.log f_hat - Real.log f0| ≤ (2 / f_lower) * |f_tilde - f0| := by
  intro f_hat
  have hx : f_lower / 2 ≤ f_hat := le_max_right f_tilde (f_lower / 2)
  have hy : f_lower / 2 ≤ f0 := by linarith
  have hlip := h_log_lip f_hat f0 hx hy
  have hproj : |f_hat - f0| ≤ |f_tilde - f0| := by
    dsimp [f_hat]
    rcases le_total f_tilde (f_lower / 2) with hle | hge
    · rw [max_eq_right hle]
      have : f_lower / 2 ≤ f0 := by linarith
      rw [abs_of_nonpos (by linarith)]
      rw [abs_of_nonpos (by linarith)]
      linarith
    · rw [max_eq_left hge]
  calc |Real.log f_hat - Real.log f0| ≤ (2 / f_lower) * |f_hat - f0| := hlip
    _ ≤ (2 / f_lower) * |f_tilde - f0| := mul_le_mul_of_nonneg_left hproj (by positivity)

/-! ## 7. Quadrature and Transfer Bounds -/

/-- Quadrature integration bound: averaging `M` equidistant frequency bins whose local
cell-average minus grid-point deviations are each bounded by `π * D / M` yields total
quadrature error at most `π * D / M`. -/
theorem quadrature_fourier_error (f_cell f_grid : ℕ → ℝ) (D : ℝ) (M : ℕ)
    (hM : 0 < M) (_hD : 0 ≤ D)
    (hcell : ∀ k ∈ Finset.range M, |f_cell k - f_grid k| ≤ Real.pi * D / (M : ℝ)) :
    |(1 / (M : ℝ)) * ∑ k ∈ Finset.range M, f_grid k -
      (1 / (M : ℝ)) * ∑ k ∈ Finset.range M, f_cell k| ≤ Real.pi * D / (M : ℝ) := by
  have hM_pos : (0 : ℝ) < M := Nat.cast_pos.mpr hM
  have hM_ne : (M : ℝ) ≠ 0 := ne_of_gt hM_pos
  have hrew : (1 / (M : ℝ)) * ∑ k ∈ Finset.range M, f_grid k -
      (1 / (M : ℝ)) * ∑ k ∈ Finset.range M, f_cell k =
      (1 / (M : ℝ)) * ∑ k ∈ Finset.range M, (f_grid k - f_cell k) := by
    rw [Finset.sum_sub_distrib, mul_sub]
  rw [hrew, abs_mul, abs_of_pos (by positivity)]
  have hsum_abs : |∑ k ∈ Finset.range M, (f_grid k - f_cell k)| ≤
      ∑ k ∈ Finset.range M, |f_grid k - f_cell k| := Finset.abs_sum_le_sum_abs _ _
  have hsum_bd : ∑ k ∈ Finset.range M, |f_grid k - f_cell k| ≤
      (M : ℝ) * (Real.pi * D / (M : ℝ)) := by
    calc ∑ k ∈ Finset.range M, |f_grid k - f_cell k|
        = ∑ k ∈ Finset.range M, |f_cell k - f_grid k| := by
          refine Finset.sum_congr rfl fun k _ => abs_sub_comm _ _
      _ ≤ ∑ _k ∈ Finset.range M, (Real.pi * D / (M : ℝ)) :=
          Finset.sum_le_sum fun k hk => hcell k hk
      _ = (M : ℝ) * (Real.pi * D / (M : ℝ)) := by
          rw [Finset.sum_const, Finset.card_range, nsmul_eq_mul]
  calc (1 / (M : ℝ)) * |∑ k ∈ Finset.range M, (f_grid k - f_cell k)|
      ≤ (1 / (M : ℝ)) * ∑ k ∈ Finset.range M, |f_grid k - f_cell k| :=
        mul_le_mul_of_nonneg_left hsum_abs (by positivity)
    _ ≤ (1 / (M : ℝ)) * ((M : ℝ) * (Real.pi * D / (M : ℝ))) :=
        mul_le_mul_of_nonneg_left hsum_bd (by positivity)
    _ = Real.pi * D / (M : ℝ) := by field_simp [hM_ne]

/-- Transfer factor error: bound |Q̂(z) - Q(z)| from the log difference.
If |log Q̂(z) - log Q(z)| ≤ E and |log Q(z)| ≤ B0, then by mean-value theorem for exp,
|Q̂(z) - Q(z)| ≤ exp(B0 + E) * E. -/
theorem transfer_factor_error (Q_true Q_hat _log_diff B0 E : ℝ) (_hE : 0 ≤ E)
    (hQ_hat_pos : 0 < Q_hat) (hQ_true_pos : 0 < Q_true)
    (h_diff : |Real.log Q_hat - Real.log Q_true| ≤ E)
    (h_bound : Real.log Q_true ≤ B0)
    (h_exp_lip : ∀ x y : ℝ, x ≤ B0 + E → y ≤ B0 + E →
      |Real.exp x - Real.exp y| ≤ Real.exp (B0 + E) * |x - y|) :
    |Q_hat - Q_true| ≤ Real.exp (B0 + E) * E := by
  have h1 : Real.log Q_true ≤ B0 + E := by linarith
  have h2 : Real.log Q_hat ≤ B0 + E := by
    have := le_abs_self (Real.log Q_hat - Real.log Q_true)
    linarith
  have hlip := h_exp_lip (Real.log Q_hat) (Real.log Q_true) h2 h1
  rw [Real.exp_log hQ_hat_pos, Real.exp_log hQ_true_pos] at hlip
  refine hlip.trans ?_
  exact mul_le_mul_of_nonneg_left h_diff (by positivity)

/-- Transfer function error: on circle |z| = s > 0, |Ĵ(z) - J(z)| = |Q̂(z) - Q(z)| / s. -/
theorem transfer_function_error (Q_true Q_hat s a : ℝ) (hs : 0 < s) :
    let J_true := (1 - Q_true) / s - a
    let J_hat := (1 - Q_hat) / s - a
    |J_hat - J_true| = |Q_hat - Q_true| / s := by
  intro J_true J_hat
  dsimp [J_hat, J_true]
  have : (1 - Q_hat) / s - a - ((1 - Q_true) / s - a) = (Q_true - Q_hat) / s := by ring
  rw [this, abs_div, abs_sub_comm Q_true Q_hat, abs_of_pos hs]

/-- Incidence estimator bound: decomposes `|∑ ĝ_m Ĵ_m - ΔS|` into transfer-function error
weighted by the `s⁻¹`-norm of `ĝ`, pilot weight error scaled by `‖J‖_∞`, and truncation tail. -/
theorem incidence_estimator_bound (g g_hat J J_hat : ℕ → ℝ) (ΔS : ℝ) (K_tr : ℕ)
    (s B norm_J_diff M0 norm_g_diff tail : ℝ)
    (hs : 0 < s) (hJdiff : 0 ≤ norm_J_diff) (_hM0 : 0 ≤ M0)
    (hg_hat_norm : ∑ m ∈ Finset.range K_tr, |g_hat m| / s ^ m ≤ B)
    (hJ_bd : ∀ m ∈ Finset.range K_tr, |J_hat m - J m| ≤ norm_J_diff / s ^ m)
    (hJ_sup : ∀ m ∈ Finset.range K_tr, |J m| ≤ M0)
    (hg_bd : ∑ m ∈ Finset.range K_tr, |g_hat m - g m| ≤ norm_g_diff)
    (htail : |∑ m ∈ Finset.range K_tr, g m * J m - ΔS| ≤ tail) :
    |∑ m ∈ Finset.range K_tr, g_hat m * J_hat m - ΔS| ≤
      B * norm_J_diff + M0 * norm_g_diff + tail := by
  have hsplit : ∑ m ∈ Finset.range K_tr, g_hat m * J_hat m - ΔS =
      (∑ m ∈ Finset.range K_tr, g_hat m * (J_hat m - J m)) +
      (∑ m ∈ Finset.range K_tr, (g_hat m - g m) * J m) +
      (∑ m ∈ Finset.range K_tr, g m * J m - ΔS) := by
    have h1 : ∑ m ∈ Finset.range K_tr, g_hat m * (J_hat m - J m) +
        ∑ m ∈ Finset.range K_tr, (g_hat m - g m) * J m =
        ∑ m ∈ Finset.range K_tr, (g_hat m * J_hat m - g m * J m) := by
      rw [← Finset.sum_add_distrib]
      refine Finset.sum_congr rfl fun m _ => by ring
    rw [h1, Finset.sum_sub_distrib]
    ring
  have hterm1 : |∑ m ∈ Finset.range K_tr, g_hat m * (J_hat m - J m)| ≤ B * norm_J_diff := by
    calc |∑ m ∈ Finset.range K_tr, g_hat m * (J_hat m - J m)|
        ≤ ∑ m ∈ Finset.range K_tr, |g_hat m * (J_hat m - J m)| :=
          Finset.abs_sum_le_sum_abs _ _
      _ = ∑ m ∈ Finset.range K_tr, |g_hat m| * |J_hat m - J m| := by
          refine Finset.sum_congr rfl fun m _ => abs_mul _ _
      _ ≤ ∑ m ∈ Finset.range K_tr, |g_hat m| * (norm_J_diff / s ^ m) :=
          Finset.sum_le_sum fun m hm => mul_le_mul_of_nonneg_left (hJ_bd m hm) (abs_nonneg _)
      _ = (∑ m ∈ Finset.range K_tr, |g_hat m| / s ^ m) * norm_J_diff := by
          rw [Finset.sum_mul]
          refine Finset.sum_congr rfl fun m _ => ?_
          have hsp : s ^ m ≠ 0 := pow_ne_zero m (ne_of_gt hs)
          field_simp [hsp]
      _ ≤ B * norm_J_diff := mul_le_mul_of_nonneg_right hg_hat_norm hJdiff
  have hterm2 : |∑ m ∈ Finset.range K_tr, (g_hat m - g m) * J m| ≤ M0 * norm_g_diff := by
    calc |∑ m ∈ Finset.range K_tr, (g_hat m - g m) * J m|
        ≤ ∑ m ∈ Finset.range K_tr, |(g_hat m - g m) * J m| :=
          Finset.abs_sum_le_sum_abs _ _
      _ = ∑ m ∈ Finset.range K_tr, |g_hat m - g m| * |J m| := by
          refine Finset.sum_congr rfl fun m _ => abs_mul _ _
      _ ≤ ∑ m ∈ Finset.range K_tr, |g_hat m - g m| * M0 :=
          Finset.sum_le_sum fun m hm => mul_le_mul_of_nonneg_left (hJ_sup m hm) (abs_nonneg _)
      _ = M0 * ∑ m ∈ Finset.range K_tr, |g_hat m - g m| := by
          rw [← Finset.sum_mul, mul_comm]
      _ ≤ M0 * norm_g_diff := mul_le_mul_of_nonneg_left hg_bd _hM0
  calc |∑ m ∈ Finset.range K_tr, g_hat m * J_hat m - ΔS|
      = |(∑ m ∈ Finset.range K_tr, g_hat m * (J_hat m - J m) +
          ∑ m ∈ Finset.range K_tr, (g_hat m - g m) * J m) +
          (∑ m ∈ Finset.range K_tr, g m * J m - ΔS)| := by rw [hsplit]
    _ ≤ |∑ m ∈ Finset.range K_tr, g_hat m * (J_hat m - J m) +
          ∑ m ∈ Finset.range K_tr, (g_hat m - g m) * J m| +
          |∑ m ∈ Finset.range K_tr, g m * J m - ΔS| := abs_add_le _ _
    _ ≤ |∑ m ∈ Finset.range K_tr, g_hat m * (J_hat m - J m)| +
          |∑ m ∈ Finset.range K_tr, (g_hat m - g m) * J m| + tail :=
        add_le_add (abs_add_le _ _) htail
    _ ≤ B * norm_J_diff + M0 * norm_g_diff + tail := by linarith

/-! ## 8. End-to-End Chaining Assembly -/

/-- End-to-end assembly theorem chaining the spectral floor, quadrature integration error,
series truncation tail, transfer factor and function bounds, and pilot error to the final
incidence estimator bound |ΔŜ - ΔS|. -/
theorem passive_incidence_end_to_end
    {B_FM eps_spec f_min s C_Q B_poly kappaM eps_g : ℝ}
    {M_grid J_n : ℕ}
    (_hBFM : 0 ≤ B_FM) (_heps : 0 ≤ eps_spec) (_hfmin : 0 < f_min)
    (hs0 : 0 < s) (hs1 : s < 1) (hCQ : 0 ≤ C_Q) (hBpoly : 0 ≤ B_poly)
    (_hkM : 0 ≤ kappaM) (_hJ_lt_M : J_n < M_grid)
    {l l_hat : ℕ → ℝ}
    (hcoeff : ∀ j ∈ Icc 1 J_n,
      |l_hat j - l j| ≤ (2 / f_min) * eps_spec + 2 * B_FM / ((M_grid - J_n : ℕ) : ℝ))
    (tail_err err_L err_Q err_J err_dS : ℝ)
    (htail : tail_err ≤ (s ^ (J_n + 1) / ((J_n + 1 : ℕ) : ℝ)) * B_FM)
    (hL : err_L ≤ (∑ j ∈ Icc 1 J_n, |l_hat j - l j| * s ^ j) + tail_err)
    (hQ : err_Q ≤ C_Q * err_L)
    (hJ : err_J ≤ err_Q / s)
    (hdS : err_dS ≤ B_poly * err_J + kappaM * eps_g) :
    err_dS ≤ B_poly * (C_Q / s) *
      ((s / (1 - s)) * ((2 / f_min) * eps_spec + 2 * B_FM / ((M_grid - J_n : ℕ) : ℝ))
        + (s ^ (J_n + 1) / ((J_n + 1 : ℕ) : ℝ)) * B_FM)
      + kappaM * eps_g := by
  have hgeom : ∑ j ∈ Icc 1 J_n, s ^ j ≤ s / (1 - s) := by
    have : ∑ j ∈ Icc 1 J_n, s ^ j = s * ∑ k ∈ range J_n, s ^ k := by
      rw [mul_sum]
      refine sum_nbij' (· - 1) (· + 1) ?_ ?_ ?_ ?_ ?_
      · intro j hj; simp only [mem_Icc, mem_range] at hj ⊢; omega
      · intro k hk; simp only [mem_range, mem_Icc] at hk ⊢; omega
      · intro j hj; simp only [mem_Icc] at hj; omega
      · intro k _; omega
      · intro j hj; simp only [mem_Icc] at hj; rw [← pow_succ', Nat.sub_add_cancel hj.1]
    rw [this, geom_sum_eq (ne_of_lt hs1)]
    have h1ms : 0 < 1 - s := sub_pos.mpr hs1
    have h_frac : (s ^ J_n - 1) / (s - 1) = (1 - s ^ J_n) / (1 - s) := by
      rw [← neg_sub 1 (s ^ J_n), ← neg_sub 1 s, neg_div_neg_eq]
    rw [h_frac]
    have hle : 1 - s ^ J_n ≤ 1 := sub_le_self 1 (pow_nonneg (le_of_lt hs0) J_n)
    calc s * ((1 - s ^ J_n) / (1 - s))
        ≤ s * (1 / (1 - s)) := mul_le_mul_of_nonneg_left (div_le_div_of_nonneg_right hle (le_of_lt h1ms)) (le_of_lt hs0)
      _ = s / (1 - s) := by ring
  set C_coef := (2 / f_min) * eps_spec + 2 * B_FM / ((M_grid - J_n : ℕ) : ℝ)
  have hC_nonneg : 0 ≤ C_coef := by positivity
  have hsum_err : ∑ j ∈ Icc 1 J_n, |l_hat j - l j| * s ^ j ≤ (s / (1 - s)) * C_coef := by
    calc ∑ j ∈ Icc 1 J_n, |l_hat j - l j| * s ^ j
        ≤ ∑ j ∈ Icc 1 J_n, C_coef * s ^ j :=
          sum_le_sum fun j hj => mul_le_mul_of_nonneg_right (hcoeff j hj) (pow_nonneg (le_of_lt hs0) j)
      _ = C_coef * ∑ j ∈ Icc 1 J_n, s ^ j := by rw [← mul_sum]
      _ ≤ C_coef * (s / (1 - s)) := mul_le_mul_of_nonneg_left hgeom hC_nonneg
      _ = (s / (1 - s)) * C_coef := mul_comm _ _
  have hL' : err_L ≤ (s / (1 - s)) * C_coef + (s ^ (J_n + 1) / ((J_n + 1 : ℕ) : ℝ)) * B_FM :=
    le_trans hL (add_le_add hsum_err htail)
  have hJ' : err_J ≤ (C_Q / s) * ((s / (1 - s)) * C_coef + (s ^ (J_n + 1) / ((J_n + 1 : ℕ) : ℝ)) * B_FM) := by
    calc err_J ≤ err_Q / s := hJ
      _ ≤ (C_Q * err_L) / s := div_le_div_of_nonneg_right hQ (le_of_lt hs0)
      _ = (C_Q / s) * err_L := by ring
      _ ≤ _ := mul_le_mul_of_nonneg_left hL' (div_nonneg hCQ (le_of_lt hs0))
  have h_bound : B_poly * err_J + kappaM * eps_g ≤
      B_poly * ((C_Q / s) * ((s / (1 - s)) * C_coef + (s ^ (J_n + 1) / ((J_n + 1 : ℕ) : ℝ)) * B_FM)) + kappaM * eps_g := by
    have := mul_le_mul_of_nonneg_left hJ' hBpoly
    linarith
  calc err_dS ≤ B_poly * err_J + kappaM * eps_g := hdS
    _ ≤ B_poly * ((C_Q / s) * ((s / (1 - s)) * C_coef + (s ^ (J_n + 1) / ((J_n + 1 : ℕ) : ℝ)) * B_FM)) + kappaM * eps_g := h_bound
    _ = B_poly * (C_Q / s) * ((s / (1 - s)) * C_coef + (s ^ (J_n + 1) / ((J_n + 1 : ℕ) : ℝ)) * B_FM) + kappaM * eps_g := by ring

end Paper1Revision14
