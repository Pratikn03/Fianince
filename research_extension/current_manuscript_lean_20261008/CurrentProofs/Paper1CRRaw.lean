import CurrentProofs.Paper1CRActual

/-!
# Paper 1, Proposition S7.1 (i) on the raw records

The averaged record is not assumed to be the experiment. The raw data of `N` reset probes of size `V` are `N · T`
independent Gaussian observations with variance `σ_p²`; observation `(k, t)` (probe `k`, tap `t`) has mean `V h_t(θ)`.
Its Jacobian is `V` times `N` stacked copies of `J`, so its Gram matrix is `N V² JᵀJ`
(`p1_rawJac_gram`). The Cramér–Rao bound for every square-integrable, locally unbiased statistic of the **raw**
records is therefore `Var ≥ σ_p² [(JᵀJ)⁻¹]_kk / (N V²) = σ_h² [(JᵀJ)⁻¹]_kk`, the paper's bound with
`σ_h = σ_p/(V √N)` (`p1_thm_cramer_rao_raw`), and for the actual closed-loop response (`p1_thm_cramer_rao_raw_actual`).
-/

namespace CurrentMM

open MeasureTheory ProbabilityTheory Filter Topology Matrix Finset
open scoped ENNReal NNReal

/-- Mean of the raw record: coordinate `(k, t)` is `V h_t(θ)`. -/
noncomputable def rawMean {p T : ℕ} (N : ℕ) (V : ℝ) (μh : (Fin p → ℝ) → (Fin T → ℝ)) (θ : Fin p → ℝ) :
    Fin (N * T) → ℝ :=
  fun idx => V * μh θ (finProdFinEquiv.symm idx).2

/-- Jacobian of the raw record. -/
noncomputable def rawJac {p T : ℕ} (N : ℕ) (V : ℝ) (J : Matrix (Fin T) (Fin p) ℝ) :
    Matrix (Fin (N * T)) (Fin p) ℝ :=
  fun idx j => V * J (finProdFinEquiv.symm idx).2 j

theorem p1_rawJac_gram {p T : ℕ} (N : ℕ) (V : ℝ) (J : Matrix (Fin T) (Fin p) ℝ) :
    (rawJac N V J)ᵀ * rawJac N V J = ((N : ℝ) * V ^ 2) • (Jᵀ * J) := by
  ext j l
  simp only [Matrix.mul_apply, Matrix.transpose_apply, rawJac, Matrix.smul_apply, smul_eq_mul]
  rw [← (finProdFinEquiv (m := N) (n := T)).sum_comp]
  simp only [Equiv.symm_apply_apply, Fintype.sum_prod_type, Finset.sum_const, Finset.card_univ,
    Fintype.card_fin, nsmul_eq_mul, Finset.mul_sum]
  exact Finset.sum_congr rfl fun t _ => by ring

theorem p1_rawMean_line_deriv {p T : ℕ} (N : ℕ) (V : ℝ) (μh : (Fin p → ℝ) → (Fin T → ℝ)) (θ0 : Fin p → ℝ)
    (J : Matrix (Fin T) (Fin p) ℝ)
    (hd : ∀ (a : Fin p → ℝ) (i : Fin T), HasDerivAt (fun s : ℝ => μh (θ0 + s • a) i) ((J *ᵥ a) i) 0)
    (a : Fin p → ℝ) (idx : Fin (N * T)) :
    HasDerivAt (fun s : ℝ => rawMean N V μh (θ0 + s • a) idx) ((rawJac N V J *ᵥ a) idx) 0 := by
  refine ((hd a (finProdFinEquiv.symm idx).2).const_mul V).congr_deriv ?_
  simp only [Matrix.mulVec, dotProduct, rawJac, Finset.mul_sum, mul_assoc]

/-- **Cramér–Rao on the raw records.** -/
theorem p1_thm_cramer_rao_raw {p T : ℕ} (N : ℕ) (hN : 0 < N) (V : ℝ) (hV : V ≠ 0)
    (μh : (Fin p → ℝ) → (Fin T → ℝ)) (θ0 : Fin p → ℝ) (J : Matrix (Fin T) (Fin p) ℝ)
    (hJ : IsUnit (Jᵀ * J).det) (v : ℝ≥0) (hv : v ≠ 0) (S : ObservationRecord (N * T) → ℝ)
    (hS : MemLp S 2 (gaussianRecordLaw (N * T) (rawMean N V μh θ0) v)) (k : Fin p)
    (hU : ∀ᶠ θ in 𝓝 θ0, ∫ x, S x ∂(gaussianRecordLaw (N * T) (rawMean N V μh θ) v) = θ k)
    (hd : ∀ (a : Fin p → ℝ) (i : Fin T), HasDerivAt (fun s : ℝ => μh (θ0 + s • a) i) ((J *ᵥ a) i) 0) :
    (v : ℝ) / (N * V ^ 2) * (Jᵀ * J)⁻¹ k k ≤ variance S (gaussianRecordLaw (N * T) (rawMean N V μh θ0) v) := by
  have hc : (N : ℝ) * V ^ 2 ≠ 0 := mul_ne_zero (Nat.cast_ne_zero.mpr hN.ne') (pow_ne_zero 2 hV)
  have hG := p1_rawJac_gram N V J
  have hJr : IsUnit ((rawJac N V J)ᵀ * rawJac N V J).det := by
    rw [hG, det_smul]
    exact ((isUnit_iff_ne_zero.mpr hc).pow _).mul hJ
  have h := p1_thm_gaussian_cramer_rao (rawMean N V μh) θ0 (rawJac N V J) hJr v hv S hS k hU
    (p1_rawMean_line_deriv N V μh θ0 J hd)
  rw [hG] at h
  haveI : Invertible ((N : ℝ) * V ^ 2) := invertibleOfNonzero hc
  rw [Matrix.inv_smul _ hJ, Matrix.smul_apply, smul_eq_mul, invOf_eq_inv] at h
  calc (v : ℝ) / (N * V ^ 2) * (Jᵀ * J)⁻¹ k k = (v : ℝ) * (((N : ℝ) * V ^ 2)⁻¹ * (Jᵀ * J)⁻¹ k k) := by ring
    _ ≤ _ := h

/-- **Proposition S7.1 (i), raw records, actual model.** `N` reset probes of size `V` with observation variance
`σ_p² = v`: every square-integrable statistic of all `N T` raw observations that is unbiased for `θ_k` near `θ₀`
has `Var ≥ σ_p² [(JᵀJ)⁻¹]_kk / (N V²)`, with `J` the Jacobian of the actual unit response. -/
theorem p1_thm_cramer_rao_raw_actual {n : ℕ} (a κ : ℝ) (T N : ℕ) (hN : 0 < N) (V : ℝ) (hV : V ≠ 0)
    (θ0 : Fin (n + n) → ℝ) (hJ : IsUnit ((p1ProbeJac a κ 1 T θ0)ᵀ * p1ProbeJac a κ 1 T θ0).det)
    (v : ℝ≥0) (hv : v ≠ 0) (S : ObservationRecord (N * T) → ℝ)
    (hS : MemLp S 2 (gaussianRecordLaw (N * T) (rawMean N V (p1ProbeMean a κ 1 T) θ0) v)) (k : Fin (n + n))
    (hU : ∀ᶠ θ in 𝓝 θ0,
      ∫ x, S x ∂(gaussianRecordLaw (N * T) (rawMean N V (p1ProbeMean a κ 1 T) θ) v) = θ k) :
    (v : ℝ) / (N * V ^ 2) * ((p1ProbeJac a κ 1 T θ0)ᵀ * p1ProbeJac a κ 1 T θ0)⁻¹ k k ≤
      variance S (gaussianRecordLaw (N * T) (rawMean N V (p1ProbeMean a κ 1 T) θ0) v) :=
  p1_thm_cramer_rao_raw N hN V hV (p1ProbeMean a κ 1 T) θ0 (p1ProbeJac a κ 1 T θ0) hJ v hv S hS k hU
    (fun d t => p1_probeMean_line_deriv a κ 1 T θ0 d t)

end CurrentMM
