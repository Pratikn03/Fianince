import CurrentProofs.KreissRadius

/-!
# Theorem 2.14, Part 3 (fixed spectrum, vanishing exact radius)

`J_θ = !![ρ, θ; 0, ρ]`, `C = !![1, 0]`, with the Euclidean operator norm.
-/

open scoped Matrix.Norms.L2Operator
open Matrix Filter Topology

namespace CurrentMM
noncomputable section

/-- The defective fixed-spectrum family `J_θ`. -/
def defectiveJ (ρ θ : ℝ) : Matrix (Fin 2) (Fin 2) ℝ := !![ρ, θ; 0, ρ]

/-- The observation operator `C = [1, 0]`. -/
def firstCoordOutput : Matrix (Fin 1) (Fin 2) ℝ := !![1, 0]

theorem defectiveJ_charpoly_det (ρ θ s : ℝ) :
    (s • (1 : Matrix (Fin 2) (Fin 2) ℝ) - defectiveJ ρ θ).det = (s - ρ) ^ 2 := by
  simp [defectiveJ, Matrix.det_fin_two]
  ring

theorem defectiveJ_commutator (ρ θ : ℝ) :
    defectiveJ ρ θ * (defectiveJ ρ θ)ᵀ - (defectiveJ ρ θ)ᵀ * defectiveJ ρ θ =
      !![θ ^ 2, 0; 0, -θ ^ 2] := by
  have hT : (defectiveJ ρ θ)ᵀ = !![ρ, 0; θ, ρ] := by
    ext i j
    fin_cases i <;> fin_cases j <;> rfl
  rw [hT, defectiveJ, Matrix.mul_fin_two, Matrix.mul_fin_two]
  ext i j
  fin_cases i <;> fin_cases j <;> simp <;> ring

theorem defectiveJ_not_normal (ρ θ : ℝ) (hθ : θ ≠ 0) :
    defectiveJ ρ θ * (defectiveJ ρ θ)ᵀ ≠ (defectiveJ ρ θ)ᵀ * defectiveJ ρ θ := by
  intro h
  have h2 := defectiveJ_commutator ρ θ
  rw [h, sub_self] at h2
  have h00 := congrFun (congrFun h2 0) 0
  have hsq : θ ^ 2 = 0 := by simpa using h00.symm
  exact hθ (pow_eq_zero_iff two_ne_zero |>.mp hsq)

theorem defectiveJ_pow_succ (ρ θ : ℝ) (t : ℕ) :
    defectiveJ ρ θ ^ (t + 1) =
      !![ρ ^ (t + 1), ((t : ℝ) + 1) * θ * ρ ^ t; 0, ρ ^ (t + 1)] := by
  induction t with
  | zero =>
    ext i j
    fin_cases i <;> fin_cases j <;> simp [defectiveJ]
  | succ k ih =>
    rw [pow_succ, ih]
    ext i j
    fin_cases i <;> fin_cases j <;>
      simp [defectiveJ, Matrix.mul_apply, Fin.sum_univ_two] <;> ring

/-- Closed form of the powers in the manuscript's notation, `t ≥ 1`. -/
theorem defectiveJ_pow (ρ θ : ℝ) (t : ℕ) (ht : 1 ≤ t) :
    defectiveJ ρ θ ^ t = !![ρ ^ t, (t : ℝ) * θ * ρ ^ (t - 1); 0, ρ ^ t] := by
  obtain ⟨k, rfl⟩ : ∃ k, t = k + 1 := ⟨t - 1, by omega⟩
  rw [defectiveJ_pow_succ]
  simp

theorem firstCoordOutput_mul_pow_succ (ρ θ : ℝ) (t : ℕ) :
    firstCoordOutput * defectiveJ ρ θ ^ (t + 1) =
      !![ρ ^ (t + 1), ((t : ℝ) + 1) * θ * ρ ^ t] := by
  rw [defectiveJ_pow_succ]
  ext i j
  fin_cases i
  fin_cases j <;> simp [firstCoordOutput, Matrix.mul_apply, Fin.sum_univ_two]

/-- Euclidean operator norm of a `1 × 2` row. -/
theorem row_l2_opNorm (a b : ℝ) :
    ‖(!![a, b] : Matrix (Fin 1) (Fin 2) ℝ)‖ = √(a ^ 2 + b ^ 2) := by
  set A : Matrix (Fin 1) (Fin 2) ℝ := !![a, b] with hA
  have happly : ∀ z : EuclideanSpace ℝ (Fin 2),
      ‖l2Apply A z‖ = √((a * z 0 + b * z 1) ^ 2) := by
    intro z
    rw [EuclideanSpace.norm_eq]
    simp [l2Apply, hA, dotProduct, Fin.sum_univ_two]
  have hz : ∀ z : EuclideanSpace ℝ (Fin 2), ‖z‖ = √(z 0 ^ 2 + z 1 ^ 2) := by
    intro z
    rw [EuclideanSpace.norm_eq]
    simp [Fin.sum_univ_two]
  apply le_antisymm
  · rw [← l2CLM_norm]
    refine ContinuousLinearMap.opNorm_le_bound _ (Real.sqrt_nonneg _) fun z => ?_
    rw [l2CLM_apply, happly, hz, ← Real.sqrt_mul (by positivity)]
    apply Real.sqrt_le_sqrt
    nlinarith [sq_nonneg (a * z 1 - b * z 0)]
  · set s := √(a ^ 2 + b ^ 2) with hs
    have hs0 : 0 ≤ s := Real.sqrt_nonneg _
    have hss : s * s = a ^ 2 + b ^ 2 := Real.mul_self_sqrt (by positivity)
    rcases hs0.eq_or_lt with h0 | hpos
    · rw [← h0]; exact norm_nonneg _
    · let x : EuclideanSpace ℝ (Fin 2) := WithLp.toLp 2 ![a, b]
      have hx : ‖x‖ = s := by
        rw [hz]
        simp [x, hs]
      have hAx : ‖l2Apply A x‖ = s * s := by
        have hx01 : a * x 0 + b * x 1 = a ^ 2 + b ^ 2 := by
          simp [x]
          ring
        rw [happly, hx01, Real.sqrt_sq (by positivity), hss]
      have key := norm_l2Apply_le A x
      rw [hAx, hx] at key
      nlinarith

theorem firstCoordOutput_norm : ‖firstCoordOutput‖ = 1 := by
  have : firstCoordOutput = !![(1 : ℝ), 0] := rfl
  rw [this, row_l2_opNorm]
  simp

/-- `M_C(J_θ)` is finite: the peak-gain supremum is bounded above. -/
theorem defective_outputGain_bddAbove (ρ θ : ℝ) (hρ0 : 0 < ρ) (hρ1 : ρ < 1) (hθ : 0 ≤ θ) :
    BddAbove (Set.range fun t : ℕ => ‖firstCoordOutput * defectiveJ ρ θ ^ t‖) := by
  obtain ⟨K, hK⟩ := (tendsto_self_mul_const_pow_of_lt_one hρ0.le hρ1).bddAbove_range
  have hK' : ∀ n : ℕ, (n : ℝ) * ρ ^ n ≤ K := fun n => hK ⟨n, rfl⟩
  have hK0 : 0 ≤ K := by simpa using hK' 0
  refine ⟨1 + θ * (K / ρ), ?_⟩
  rintro _ ⟨t, rfl⟩
  have hnn : 0 ≤ θ * (K / ρ) := mul_nonneg hθ (div_nonneg hK0 hρ0.le)
  cases t with
  | zero =>
    simp only [pow_zero, Matrix.mul_one, firstCoordOutput_norm]
    linarith
  | succ k =>
    simp only []
    rw [firstCoordOutput_mul_pow_succ, row_l2_opNorm]
    have hp0 : 0 ≤ ρ ^ (k + 1) := by positivity
    have hp1 : ρ ^ (k + 1) ≤ 1 := pow_le_one₀ hρ0.le hρ1.le
    have hq0 : 0 ≤ ((k : ℝ) + 1) * θ * ρ ^ k := by positivity
    have hq1 : ((k : ℝ) + 1) * ρ ^ k ≤ K / ρ := by
      rw [le_div_iff₀ hρ0]
      have := hK' (k + 1)
      push_cast at this
      calc ((k : ℝ) + 1) * ρ ^ k * ρ = ((k : ℝ) + 1) * ρ ^ (k + 1) := by ring
        _ ≤ K := this
    have hq2 : ((k : ℝ) + 1) * θ * ρ ^ k ≤ θ * (K / ρ) := by
      calc ((k : ℝ) + 1) * θ * ρ ^ k = θ * (((k : ℝ) + 1) * ρ ^ k) := by ring
        _ ≤ θ * (K / ρ) := mul_le_mul_of_nonneg_left hq1 hθ
    rw [Real.sqrt_le_left (by linarith)]
    nlinarith

/-- `‖C J_θ‖ = √(ρ² + θ²)`. -/
theorem firstCoordOutput_mul_defectiveJ_norm (ρ θ : ℝ) :
    ‖firstCoordOutput * defectiveJ ρ θ‖ = √(ρ ^ 2 + θ ^ 2) := by
  have h := firstCoordOutput_mul_pow_succ ρ θ 0
  simp only [zero_add, pow_one, Nat.cast_zero, one_mul, pow_zero, mul_one] at h
  rw [h, row_l2_opNorm]

/-- `M_C(J_θ) ≥ √(ρ² + θ²) ≥ θ`. -/
theorem defective_outputGain_ge (ρ θ : ℝ) (hρ0 : 0 < ρ) (hρ1 : ρ < 1) (hθ : 0 ≤ θ) :
    √(ρ ^ 2 + θ ^ 2) ≤ outputGain firstCoordOutput (defectiveJ ρ θ) ∧
      θ ≤ outputGain firstCoordOutput (defectiveJ ρ θ) := by
  have h1 := outputGain_ge firstCoordOutput (defectiveJ ρ θ)
    (defective_outputGain_bddAbove ρ θ hρ0 hρ1 hθ) 1
  rw [pow_one, firstCoordOutput_mul_defectiveJ_norm] at h1
  refine ⟨h1, le_trans ?_ h1⟩
  rw [Real.le_sqrt hθ (by positivity)]
  nlinarith [sq_nonneg ρ]

theorem defective_exact_radius_le (ρ θ B : ℝ) (hρ0 : 0 < ρ) (hρ1 : ρ < 1) (hθ : 0 < θ)
    (hB : 0 < B) :
    B / outputGain firstCoordOutput (defectiveJ ρ θ) ≤ B / θ :=
  div_le_div_of_nonneg_left hB.le hθ (defective_outputGain_ge ρ θ hρ0 hρ1 hθ.le).2

/-- Part 3: with the spectrum fixed at `ρ`, the exact safe radius `B / M_C(J_θ)` tends to `0`
as `θ → ∞`, for every buffer `B > 0`. -/
theorem defective_exact_radius_tendsto_zero (ρ B : ℝ) (hρ0 : 0 < ρ) (hρ1 : ρ < 1)
    (hB : 0 < B) :
    Tendsto (fun θ : ℝ => B / outputGain firstCoordOutput (defectiveJ ρ θ)) atTop (𝓝 0) := by
  have hup : Tendsto (fun θ : ℝ => B / θ) atTop (𝓝 0) :=
    tendsto_const_nhds.div_atTop tendsto_id
  apply tendsto_of_tendsto_of_tendsto_of_le_of_le' tendsto_const_nhds hup
  · filter_upwards [eventually_gt_atTop 0] with θ hθ
    have hM := (defective_outputGain_ge ρ θ hρ0 hρ1 hθ.le).2
    exact div_nonneg hB.le (by linarith)
  · filter_upwards [eventually_gt_atTop 0] with θ hθ
    exact defective_exact_radius_le ρ θ B hρ0 hρ1 hθ hB

end
end CurrentMM
