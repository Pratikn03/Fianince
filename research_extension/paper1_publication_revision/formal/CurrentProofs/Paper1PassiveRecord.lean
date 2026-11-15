import CurrentProofs.Paper1GaussianTriangular
import CurrentProofs.Paper1MergedSeparation

/-!
# Paper 1, Theorem 5.8: the passive record and its divergence

A market driven by i.i.d. innovations has run for `M` periods before the observer starts, and the observer records
the next `T` prices. With response `g` to an innovation (`g 0 = 1`), the recording matrix maps the `M + T`
innovations to the record (past innovations, then observed prices); it is lower triangular with unit diagonal.

* `p1_recording_factor`: if `r` is the reciprocal series of `g₀` (`r * g₀ = δ`), then `A₀ B = A₁` for an explicit
  unit lower-triangular `B = 1 + E` (no matrix inverse needed);
* `p1_recording_frobenius`: `‖E‖_F² ≤ ‖r‖₁² T ‖g₁ - g₀‖₁²`, **independent of the warm-up length `M`**;
* `p1_passive_record_kl`: hence the divergence of the observed prices is at most `½ ‖r‖₁² T ‖g₁ - g₀‖₁²`.
-/

namespace CurrentMM

open MeasureTheory ProbabilityTheory InformationTheory Finset Matrix
open scoped ENNReal NNReal

/-- Recording rule on time indices: past innovations are recorded as they are; later prices are `∑ g(τ-σ) ξ_σ`. -/
noncomputable def recN (M : ℕ) (g : ℕ → ℝ) (τ σ : ℕ) : ℝ :=
  if τ < M then (if τ = σ then 1 else 0) else (if σ ≤ τ then g (τ - σ) else 0)

/-- The correction term of `B = 1 + E`. -/
noncomputable def corrN (M : ℕ) (r dg : ℕ → ℝ) (τ σ : ℕ) : ℝ :=
  if τ < M then 0 else ∑ u ∈ Ico M (τ + 1), r (τ - u) * dg (u - σ)

/-- Recording matrix. -/
noncomputable def recMat (M T : ℕ) (g : ℕ → ℝ) : Matrix (Fin (M + T)) (Fin (M + T)) ℝ :=
  fun τ σ => recN M g τ σ

/-- The matrix `B = 1 + E`. -/
noncomputable def corrMat (M T : ℕ) (r dg : ℕ → ℝ) : Matrix (Fin (M + T)) (Fin (M + T)) ℝ :=
  fun τ σ => (if τ = σ then 1 else 0) + corrN M r dg τ σ

/-- The reciprocal-series identity, convolution form. -/
def IsReciprocal (r g : ℕ → ℝ) : Prop := ∀ m, ∑ j ∈ range (m + 1), r j * g (m - j) = if m = 0 then 1 else 0

theorem p1_inner_conv (r g : ℕ → ℝ) (hrg : IsReciprocal r g) (u τ : ℕ) (hu : u ≤ τ) :
    ∑ ρ ∈ Ico u (τ + 1), g (τ - ρ) * r (ρ - u) = if τ = u then 1 else 0 := by
  rw [sum_Ico_eq_sum_range]
  have e : τ + 1 - u = (τ - u) + 1 := by omega
  rw [e]
  have h2 : ∀ k ∈ range ((τ - u) + 1), g (τ - (u + k)) * r (u + k - u) = r k * g ((τ - u) - k) := by
    intro k hk
    have : τ - (u + k) = (τ - u) - k := by omega
    rw [this, Nat.add_sub_cancel_left, mul_comm]
  rw [sum_congr rfl h2, hrg (τ - u)]
  by_cases h : τ = u
  · subst h; simp
  · have : τ - u ≠ 0 := by omega
    simp [h, this]

/-- **The factorization `A₀ B = A₁`**, entrywise on time indices below `n`. -/
theorem p1_recording_factor_N (M n : ℕ) (g0 g1 r : ℕ → ℝ) (hrg : IsReciprocal r g0)
    (hg0 : g0 0 = 1) (hg1 : g1 0 = 1) (τ σ : ℕ) (hτ : τ < n) (hσ : σ < n) :
    ∑ ρ ∈ range n, recN M g0 τ ρ * ((if ρ = σ then 1 else 0) + corrN M r (fun j => g1 j - g0 j) ρ σ) =
      recN M g1 τ σ := by
  simp only [mul_add, sum_add_distrib, mul_ite, mul_one, mul_zero, sum_ite_eq', mem_range, hσ, ite_true]
  by_cases hτM : τ < M
  · -- a recorded past innovation: the row is a unit vector
    have hz : ∀ ρ ∈ range n, recN M g0 τ ρ * corrN M r (fun j => g1 j - g0 j) ρ σ =
        if ρ = τ then corrN M r (fun j => g1 j - g0 j) τ σ else 0 := by
      intro ρ _
      by_cases h : ρ = τ
      · subst h; simp [recN, hτM]
      · simp [recN, hτM, Ne.symm h, h]
    rw [sum_congr rfl hz, sum_ite_eq' (range n) τ, if_pos (mem_range.mpr hτ)]
    simp [recN, corrN, hτM]
  · push Not at hτM
    -- only `M ≤ ρ ≤ τ` contributes to the second sum
    have hsupp : ∑ ρ ∈ range n, recN M g0 τ ρ * corrN M r (fun j => g1 j - g0 j) ρ σ =
        ∑ ρ ∈ Ico M (τ + 1), g0 (τ - ρ) * ∑ u ∈ Ico M (ρ + 1), r (ρ - u) * (g1 (u - σ) - g0 (u - σ)) := by
      rw [← sum_subset (s₁ := Ico M (τ + 1)) (s₂ := range n)]
      · refine sum_congr rfl (fun ρ hρ => ?_)
        have hρ' := mem_Ico.mp hρ
        simp [recN, corrN, Nat.not_lt.mpr hτM, Nat.not_lt.mpr hρ'.1, Nat.le_of_lt_succ hρ'.2]
      · intro ρ hρ; exact mem_range.mpr (by have := mem_Ico.mp hρ; omega)
      · intro ρ _ hρ
        rw [mem_Ico, not_and_or] at hρ
        rcases hρ with h | h
        · simp [corrN, Nat.lt_of_not_le h]
        · simp [recN, Nat.not_lt.mpr hτM, show ¬ ρ ≤ τ by omega]
    rw [hsupp]
    -- swap the order of summation
    have hswap : ∑ ρ ∈ Ico M (τ + 1), g0 (τ - ρ) * ∑ u ∈ Ico M (ρ + 1), r (ρ - u) * (g1 (u - σ) - g0 (u - σ)) =
        ∑ u ∈ Ico M (τ + 1), (g1 (u - σ) - g0 (u - σ)) * ∑ ρ ∈ Ico u (τ + 1), g0 (τ - ρ) * r (ρ - u) := by
      simp only [mul_sum]
      rw [sum_comm' (t' := Ico M (τ + 1)) (s' := fun u => Ico u (τ + 1))]
      · exact sum_congr rfl (fun u _ => sum_congr rfl (fun ρ _ => by ring))
      · intro ρ u
        simp only [mem_Ico]
        omega
    rw [hswap]
    have hin : ∀ u ∈ Ico M (τ + 1), (g1 (u - σ) - g0 (u - σ)) * ∑ ρ ∈ Ico u (τ + 1), g0 (τ - ρ) * r (ρ - u) =
        if u = τ then g1 (τ - σ) - g0 (τ - σ) else 0 := by
      intro u hu
      rw [p1_inner_conv r g0 hrg u τ (by have := mem_Ico.mp hu; omega)]
      by_cases h : u = τ
      · subst h; simp
      · simp [Ne.symm h, h]
    rw [sum_congr rfl hin, sum_ite_eq' (Ico M (τ + 1)) τ, if_pos (mem_Ico.mpr ⟨hτM, by omega⟩)]
    simp only [recN, Nat.not_lt.mpr hτM, if_false]
    by_cases hστ : σ ≤ τ
    · simp [hστ]
    · have : τ - σ = 0 := by omega
      simp [hστ, this, hg0, hg1]

/-- Matrix form of the factorization. -/
theorem p1_recording_factor (M T : ℕ) (g0 g1 r : ℕ → ℝ) (hrg : IsReciprocal r g0)
    (hg0 : g0 0 = 1) (hg1 : g1 0 = 1) :
    recMat M T g0 * corrMat M T r (fun j => g1 j - g0 j) = recMat M T g1 := by
  ext τ σ
  simp only [Matrix.mul_apply, recMat, corrMat]
  have e : ∀ j : Fin (M + T), (if j = σ then (1 : ℝ) else 0) = if (j : ℕ) = (σ : ℕ) then 1 else 0 :=
    fun j => by simp [Fin.ext_iff]
  simp only [e]
  rw [Fin.sum_univ_eq_sum_range (fun ρ => recN M g0 τ ρ * ((if ρ = (σ : ℕ) then 1 else 0) +
    corrN M r (fun j => g1 j - g0 j) ρ σ)) (M + T)]
  exact p1_recording_factor_N M (M + T) g0 g1 r hrg hg0 hg1 τ σ τ.isLt σ.isLt

theorem p1_corrN_upper_zero (M : ℕ) (r dg : ℕ → ℝ) (hdg0 : dg 0 = 0) (τ σ : ℕ) (h : τ ≤ σ) :
    corrN M r dg τ σ = 0 := by
  unfold corrN
  split_ifs
  · rfl
  · refine sum_eq_zero (fun u hu => ?_)
    have : u - σ = 0 := by have := mem_Ico.mp hu; omega
    rw [this, hdg0, mul_zero]

theorem p1_corrMat_lower (M T : ℕ) (r dg : ℕ → ℝ) (hdg0 : dg 0 = 0) :
    (corrMat M T r dg).IsLowerTriangular := by
  intro τ σ h
  have hτσ : τ < σ := by simpa using h
  simp only [corrMat, if_neg (ne_of_lt hτσ), zero_add]
  exact p1_corrN_upper_zero M r dg hdg0 τ σ (le_of_lt (by exact_mod_cast hτσ))

theorem p1_corrMat_diag (M T : ℕ) (r dg : ℕ → ℝ) (hdg0 : dg 0 = 0) (τ : Fin (M + T)) :
    corrMat M T r dg τ τ = 1 := by
  simp [corrMat, p1_corrN_upper_zero M r dg hdg0 τ τ le_rfl]

theorem p1_sq_sum_le_sq_abs_sum (s : Finset ℕ) (a : ℕ → ℝ) : ∑ j ∈ s, a j ^ 2 ≤ (∑ j ∈ s, |a j|) ^ 2 := by
  have h : ∀ j ∈ s, a j ^ 2 ≤ |a j| * ∑ i ∈ s, |a i| := by
    intro j hj
    rw [← sq_abs]
    exact pow_two (|a j|) ▸ mul_le_mul_of_nonneg_left
      (single_le_sum (f := fun i => |a i|) (fun i _ => abs_nonneg _) hj) (abs_nonneg _)
  calc ∑ j ∈ s, a j ^ 2 ≤ ∑ j ∈ s, |a j| * ∑ i ∈ s, |a i| := sum_le_sum h
    _ = (∑ j ∈ s, |a j|) ^ 2 := by rw [← sum_mul, sq]

/-- **Frobenius bound, independent of the warm-up length `M`.** -/
theorem p1_recording_frobenius_N (M T : ℕ) (r dg : ℕ → ℝ) (D E1 : ℝ) (hdg0 : dg 0 = 0)
    (hD : ∀ N, ∑ m ∈ range N, |r m| ≤ D) (hE : ∀ N, ∑ m ∈ range N, |dg m| ≤ E1) :
    ∑ σ ∈ range (M + T), ∑ τ ∈ range (M + T), corrN M r dg τ σ ^ 2 ≤ D ^ 2 * T * E1 ^ 2 := by
  have hD0 : 0 ≤ D := by simpa using hD 0
  have hcol : ∀ σ, ∑ τ ∈ range (M + T), corrN M r dg τ σ ^ 2 ≤ D ^ 2 * ∑ t ∈ range T, dg (M + t - σ) ^ 2 := by
    intro σ
    rw [sum_range_add]
    have hz : ∑ τ ∈ range M, corrN M r dg τ σ ^ 2 = 0 :=
      sum_eq_zero (fun τ hτ => by simp [corrN, mem_range.mp hτ])
    rw [hz, zero_add]
    have hrow : ∀ t, corrN M r dg (M + t) σ = ∑ k ∈ range (t + 1), dg (M + k - σ) * r (t - k) := by
      intro t
      simp only [corrN, show ¬ (M + t < M) by omega, if_false]
      rw [sum_Ico_eq_sum_range, show M + t + 1 - M = t + 1 by omega]
      refine sum_congr rfl (fun k _ => ?_)
      rw [show M + t - (M + k) = t - k by omega, mul_comm]
    simp only [hrow]
    exact p1_conv_energy r (fun k => dg (M + k - σ)) D hD T
  have hshift : ∀ t ∈ range T, ∑ σ ∈ range (M + T), dg (M + t - σ) ^ 2 ≤ E1 ^ 2 := by
    intro t ht
    have htT := mem_range.mp ht
    have hsplit : ∑ σ ∈ range (M + T), dg (M + t - σ) ^ 2 = ∑ σ ∈ range (M + t + 1), dg (M + t - σ) ^ 2 := by
      symm
      refine sum_subset (fun σ hσ => mem_range.mpr (by have := mem_range.mp hσ; omega)) (fun σ hσ hσ' => ?_)
      have : M + t - σ = 0 := by
        have h1 : ¬ σ < M + t + 1 := fun h => hσ' (mem_range.mpr h)
        omega
      rw [this, hdg0]; ring
    rw [hsplit]
    have hrefl := sum_range_reflect (fun j => dg j ^ 2) (M + t + 1)
    simp only [Nat.add_sub_cancel] at hrefl
    rw [hrefl]
    have hE0 : 0 ≤ E1 := by simpa using hE 0
    calc ∑ j ∈ range (M + t + 1), dg j ^ 2 ≤ (∑ j ∈ range (M + t + 1), |dg j|) ^ 2 :=
          p1_sq_sum_le_sq_abs_sum _ _
      _ ≤ E1 ^ 2 := pow_le_pow_left₀ (sum_nonneg (fun _ _ => abs_nonneg _)) (hE _) 2
  calc ∑ σ ∈ range (M + T), ∑ τ ∈ range (M + T), corrN M r dg τ σ ^ 2
      ≤ ∑ σ ∈ range (M + T), D ^ 2 * ∑ t ∈ range T, dg (M + t - σ) ^ 2 := sum_le_sum (fun σ _ => hcol σ)
    _ = D ^ 2 * ∑ t ∈ range T, ∑ σ ∈ range (M + T), dg (M + t - σ) ^ 2 := by
        rw [← mul_sum, sum_comm]
    _ ≤ D ^ 2 * ∑ _t ∈ range T, E1 ^ 2 := by
        gcongr with t ht
        exact hshift t ht
    _ = D ^ 2 * T * E1 ^ 2 := by rw [sum_const, card_range, nsmul_eq_mul]; ring

end CurrentMM
