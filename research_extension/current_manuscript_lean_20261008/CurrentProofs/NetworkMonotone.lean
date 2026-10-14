import CurrentProofs.KreissRadius

/-!
# Proposition 2.16 (Cross-Impact Kreiss Inflation), the exact-radius part

Entrywise order on real matrices, ordered nonnegative powers, monotonicity of the Euclidean
operator norm on entrywise-ordered nonnegative matrices, monotone peak output gain
`M_C(J) = sup_t ‖C J^t‖₂` and exact-radius contraction `B / M_C(J_multi) ≤ B / M_C(J_diag)`,
together with the entrywise monotonicity of the multi-asset Jacobian (eq:multi_jacobian) in the
cross-impact matrix `K`.

The Kreiss-constant comparison `K(J_multi) ≥ K(J_diag)` and the conservative-radius contraction
of the proposition are NOT covered in this module.
-/

open scoped Matrix.Norms.L2Operator
open Matrix

namespace CurrentMM
noncomputable section

variable {ι κ μ : Type*} [Fintype ι] [Fintype κ] [Fintype μ]
  [DecidableEq ι] [DecidableEq κ] [DecidableEq μ]

/-- Entrywise nonnegativity `0 ≤ P`. -/
def EntryNonneg (P : Matrix ι κ ℝ) : Prop := ∀ i j, 0 ≤ P i j

/-- Entrywise order `P ≤ Q`. -/
def EntryLE (P Q : Matrix ι κ ℝ) : Prop := ∀ i j, P i j ≤ Q i j

omit [Fintype ι] [Fintype μ] [DecidableEq ι] [DecidableEq κ] [DecidableEq μ] in
theorem entry_mul_mono {P P' : Matrix ι κ ℝ} {Q Q' : Matrix κ μ ℝ}
    (hP : EntryNonneg P) (hPP : EntryLE P P') (hQ : EntryNonneg Q) (hQQ : EntryLE Q Q') :
    EntryNonneg (P * Q) ∧ EntryLE (P * Q) (P' * Q') := by
  refine ⟨fun i j => ?_, fun i j => ?_⟩
  · rw [Matrix.mul_apply]
    exact Finset.sum_nonneg fun k _ => mul_nonneg (hP i k) (hQ k j)
  · rw [Matrix.mul_apply, Matrix.mul_apply]
    exact Finset.sum_le_sum fun k _ =>
      mul_le_mul (hPP i k) (hQQ k j) (hQ k j) (le_trans (hP i k) (hPP i k))

omit [Fintype ι] in
theorem entry_one_nonneg : EntryNonneg (1 : Matrix ι ι ℝ) := fun i j => by
  rw [Matrix.one_apply]
  split_ifs <;> norm_num

/-- Ordered nonnegative powers: `0 ≤ A ≤ A'` entrywise implies `0 ≤ A^t ≤ A'^t` entrywise. -/
theorem entry_pow_mono {A A' : Matrix ι ι ℝ} (hA : EntryNonneg A) (hAA : EntryLE A A') (t : ℕ) :
    EntryNonneg (A ^ t) ∧ EntryLE (A ^ t) (A' ^ t) := by
  induction t with
  | zero =>
    simp only [pow_zero]
    exact ⟨entry_one_nonneg, fun i j => le_rfl⟩
  | succ k ih =>
    rw [pow_succ, pow_succ]
    exact entry_mul_mono ih.1 ih.2 hA hAA

/-- Euclidean operator-norm comparison under an entrywise modulus bound by a nonnegative real
matrix: if `‖P i j‖ ≤ q i j` then `‖P‖₂ ≤ ‖q‖₂` (with `q` viewed over `𝕜`). -/
theorem l2_opNorm_le_of_entry_bound {𝕜 : Type*} [RCLike 𝕜] (P : Matrix ι κ 𝕜)
    (q : Matrix ι κ ℝ) (hq : ∀ i j, 0 ≤ q i j) (hPq : ∀ i j, ‖P i j‖ ≤ q i j) :
    ‖P‖ ≤ ‖q.map (algebraMap ℝ 𝕜)‖ := by
  set Q := q.map (algebraMap ℝ 𝕜) with hQdef
  let LP := (toEuclideanLin (𝕜 := 𝕜) (m := ι) (n := κ)).trans LinearMap.toContinuousLinearMap P
  let LQ := (toEuclideanLin (𝕜 := 𝕜) (m := ι) (n := κ)).trans LinearMap.toContinuousLinearMap Q
  change ‖LP‖ ≤ ‖LQ‖
  refine ContinuousLinearMap.opNorm_le_bound _ (norm_nonneg _) fun x => ?_
  let y : EuclideanSpace 𝕜 κ := WithLp.toLp 2 (fun j => ((‖x j‖ : ℝ) : 𝕜))
  have hy : ‖y‖ = ‖x‖ := by
    rw [EuclideanSpace.norm_eq, EuclideanSpace.norm_eq]
    simp [y]
  have hentry : ∀ i, ‖(LP x) i‖ ≤ ‖(LQ y) i‖ := by
    intro i
    have h1 : (LP x) i = ∑ j, P i j * x j := by
      simp [LP, Matrix.mulVec, dotProduct]
    have h2 : (LQ y) i = ((∑ j, q i j * ‖x j‖ : ℝ) : 𝕜) := by
      simp [LQ, Q, y, Matrix.mulVec, dotProduct]
    rw [h1, h2, RCLike.norm_ofReal,
      abs_of_nonneg (Finset.sum_nonneg fun j _ => mul_nonneg (hq i j) (norm_nonneg _))]
    calc ‖∑ j, P i j * x j‖ ≤ ∑ j, ‖P i j * x j‖ := norm_sum_le _ _
      _ = ∑ j, ‖P i j‖ * ‖x j‖ := by simp only [norm_mul]
      _ ≤ ∑ j, q i j * ‖x j‖ :=
          Finset.sum_le_sum fun j _ => mul_le_mul_of_nonneg_right (hPq i j) (norm_nonneg _)
  have hnorm : ‖LP x‖ ≤ ‖LQ y‖ := by
    rw [EuclideanSpace.norm_eq, EuclideanSpace.norm_eq]
    exact Real.sqrt_le_sqrt
      (Finset.sum_le_sum fun i _ => pow_le_pow_left₀ (norm_nonneg _) (hentry i) 2)
  calc ‖LP x‖ ≤ ‖LQ y‖ := hnorm
    _ ≤ ‖LQ‖ * ‖y‖ := LQ.le_opNorm y
    _ = ‖LQ‖ * ‖x‖ := by rw [hy]

/-- Ordered Euclidean operator norms: `0 ≤ P ≤ Q` entrywise implies `‖P‖₂ ≤ ‖Q‖₂`. -/
theorem l2_opNorm_mono_of_entry {P Q : Matrix ι κ ℝ} (hP : EntryNonneg P) (hPQ : EntryLE P Q) :
    ‖P‖ ≤ ‖Q‖ := by
  have h := l2_opNorm_le_of_entry_bound P Q (fun i j => le_trans (hP i j) (hPQ i j))
    (fun i j => by rw [Real.norm_eq_abs, abs_of_nonneg (hP i j)]; exact hPQ i j)
  have hmap : Q.map (algebraMap ℝ ℝ) = Q := by
    ext i j
    simp
  rwa [hmap] at h

/-- Ordered output magnification at every horizon, for a fixed nonnegative output `C`. -/
theorem output_norm_mono {C : Matrix ι κ ℝ} {J J' : Matrix κ κ ℝ} (hC : EntryNonneg C)
    (hJ : EntryNonneg J) (hJJ : EntryLE J J') (t : ℕ) :
    ‖C * J ^ t‖ ≤ ‖C * J' ^ t‖ := by
  obtain ⟨h1, h2⟩ := entry_pow_mono hJ hJJ t
  obtain ⟨h3, h4⟩ := entry_mul_mono hC (fun i j => le_rfl) h1 h2
  exact l2_opNorm_mono_of_entry h3 h4

/-- Ordered output trajectories for nonnegative initial states. -/
theorem output_vector_mono {C : Matrix ι κ ℝ} {J J' : Matrix κ κ ℝ} (hC : EntryNonneg C)
    (hJ : EntryNonneg J) (hJJ : EntryLE J J') (z : κ → ℝ) (hz : ∀ j, 0 ≤ z j) (t : ℕ) (i : ι) :
    0 ≤ ((C * J ^ t) *ᵥ z) i ∧ ((C * J ^ t) *ᵥ z) i ≤ ((C * J' ^ t) *ᵥ z) i := by
  obtain ⟨h1, h2⟩ := entry_pow_mono hJ hJJ t
  obtain ⟨h3, h4⟩ := entry_mul_mono hC (fun i j => le_rfl) h1 h2
  simp only [Matrix.mulVec, dotProduct]
  exact ⟨Finset.sum_nonneg fun j _ => mul_nonneg (h3 i j) (hz j),
    Finset.sum_le_sum fun j _ => mul_le_mul_of_nonneg_right (h4 i j) (hz j)⟩

/-- Monotone peak output gain: `M_C(J) ≤ M_C(J')` (and finiteness transfers downward). -/
theorem peak_gain_mono {C : Matrix ι κ ℝ} {J J' : Matrix κ κ ℝ} (hC : EntryNonneg C)
    (hJ : EntryNonneg J) (hJJ : EntryLE J J')
    (hbdd' : BddAbove (Set.range fun t : ℕ => ‖C * J' ^ t‖)) :
    BddAbove (Set.range fun t : ℕ => ‖C * J ^ t‖) ∧
      (⨆ t : ℕ, ‖C * J ^ t‖) ≤ ⨆ t : ℕ, ‖C * J' ^ t‖ := by
  refine ⟨?_, ciSup_mono hbdd' fun t => output_norm_mono hC hJ hJJ t⟩
  obtain ⟨b, hb⟩ := hbdd'
  refine ⟨b, ?_⟩
  rintro _ ⟨t, rfl⟩
  exact le_trans (output_norm_mono hC hJ hJJ t) (hb ⟨t, rfl⟩)

/-- Exact-radius contraction: `B / M_C(J') ≤ B / M_C(J)` for `0 ≤ J ≤ J'`, `C ≥ 0`, `C ≠ 0`. -/
theorem exact_radius_contraction {C : Matrix ι κ ℝ} {J J' : Matrix κ κ ℝ} (hC : EntryNonneg C)
    (hCne : C ≠ 0) (hJ : EntryNonneg J) (hJJ : EntryLE J J') (B : ℝ) (hB : 0 < B)
    (hbdd' : BddAbove (Set.range fun t : ℕ => ‖C * J' ^ t‖)) :
    B / (⨆ t : ℕ, ‖C * J' ^ t‖) ≤ B / (⨆ t : ℕ, ‖C * J ^ t‖) := by
  obtain ⟨hbdd, hmono⟩ := peak_gain_mono hC hJ hJJ hbdd'
  have h0 : ‖C * J ^ 0‖ ≤ ⨆ t : ℕ, ‖C * J ^ t‖ := le_ciSup hbdd 0
  rw [pow_zero, Matrix.mul_one] at h0
  have hpos : 0 < ⨆ t : ℕ, ‖C * J ^ t‖ := lt_of_lt_of_le (norm_pos_iff.mpr hCne) h0
  exact div_le_div_of_nonneg_left hB.le hpos hmono

/-- The same comparison stated with the `outputGain` of Theorem 2.14. -/
theorem outputGain_mono {m n : ℕ} {C : Matrix (Fin m) (Fin n) ℝ} {J J' : Matrix (Fin n) (Fin n) ℝ}
    (hC : EntryNonneg C) (hJ : EntryNonneg J) (hJJ : EntryLE J J')
    (hbdd' : BddAbove (Set.range fun t : ℕ => ‖C * J' ^ t‖)) :
    outputGain C J ≤ outputGain C J' :=
  (peak_gain_mono hC hJ hJJ hbdd').2

/-- Multi-asset closed-loop Jacobian (eq:multi_jacobian) with `A = diag a`, `H = diag η`,
`Q = diag q` and cross-impact matrix `K`. -/
def multiJacobian {d : ℕ} (a η q : Fin d → ℝ) (K : Matrix (Fin d) (Fin d) ℝ) :
    Matrix (Fin d ⊕ Fin d) (Fin d ⊕ Fin d) ℝ :=
  Matrix.fromBlocks (diagonal a) (K * diagonal q) (diagonal η * diagonal a)
    (1 - diagonal η + diagonal η * K * diagonal q)

/-- The multi-asset Jacobian is entrywise nonnegative and entrywise nondecreasing in the
cross-impact matrix, for `a ≥ 0`, `0 ≤ η ≤ 1`, `q ≥ 0` and `0 ≤ K ≤ K'`. -/
theorem multiJacobian_entry_mono {d : ℕ} (a η q : Fin d → ℝ) (K K' : Matrix (Fin d) (Fin d) ℝ)
    (ha : ∀ i, 0 ≤ a i) (hη0 : ∀ i, 0 ≤ η i) (hη1 : ∀ i, η i ≤ 1) (hq : ∀ i, 0 ≤ q i)
    (hK : EntryNonneg K) (hKK : EntryLE K K') :
    EntryNonneg (multiJacobian a η q K) ∧
      EntryLE (multiJacobian a η q K) (multiJacobian a η q K') := by
  constructor
  · rintro (i | i) (j | j)
    · simp only [multiJacobian, fromBlocks_apply₁₁, diagonal_apply]
      split_ifs <;> simp [ha]
    · simp only [multiJacobian, fromBlocks_apply₁₂, mul_diagonal]
      exact mul_nonneg (hK i j) (hq j)
    · simp only [multiJacobian, fromBlocks_apply₂₁, diagonal_mul_diagonal, diagonal_apply]
      split_ifs
      · exact mul_nonneg (hη0 i) (ha i)
      · exact le_rfl
    · simp only [multiJacobian, fromBlocks_apply₂₂, Matrix.add_apply, Matrix.sub_apply, one_apply,
        diagonal_apply, mul_diagonal, diagonal_mul]
      have : 0 ≤ η i * K i j * q j := mul_nonneg (mul_nonneg (hη0 i) (hK i j)) (hq j)
      split_ifs <;> linarith [hη1 i]
  · rintro (i | i) (j | j)
    · simp [multiJacobian]
    · simp only [multiJacobian, fromBlocks_apply₁₂, mul_diagonal]
      exact mul_le_mul_of_nonneg_right (hKK i j) (hq j)
    · simp [multiJacobian]
    · simp only [multiJacobian, fromBlocks_apply₂₂, Matrix.add_apply, Matrix.sub_apply, one_apply,
        diagonal_apply, mul_diagonal, diagonal_mul]
      have : η i * K i j * q j ≤ η i * K' i j * q j :=
        mul_le_mul_of_nonneg_right (mul_le_mul_of_nonneg_left (hKK i j) (hη0 i)) (hq j)
      linarith

/-- Proposition 2.16, exact-radius part, for the multi-asset Jacobian: for a decoupled impact
matrix `K_diag` and a coupled one `K_multi` with `0 ≤ K_diag ≤ K_multi` entrywise (e.g.
`K_diag` = `K_multi` with the `K₂₁` block zeroed), fixed nonnegative output `C ≠ 0` and finite
coupled peak gain, the peak gain is ordered at every horizon and in supremum, and the exact safe
radius contracts. -/
theorem cross_impact_exact_radius_contraction {d : ℕ} {ο : Type*} [Fintype ο] [DecidableEq ο]
    (a η q : Fin d → ℝ) (Kdiag Kmulti : Matrix (Fin d) (Fin d) ℝ)
    (ha : ∀ i, 0 ≤ a i) (hη0 : ∀ i, 0 ≤ η i) (hη1 : ∀ i, η i ≤ 1) (hq : ∀ i, 0 ≤ q i)
    (hK : EntryNonneg Kdiag) (hKK : EntryLE Kdiag Kmulti)
    (C : Matrix ο (Fin d ⊕ Fin d) ℝ) (hC : EntryNonneg C) (hCne : C ≠ 0) (B : ℝ) (hB : 0 < B)
    (hbdd : BddAbove (Set.range fun t : ℕ => ‖C * multiJacobian a η q Kmulti ^ t‖)) :
    (∀ t : ℕ, ‖C * multiJacobian a η q Kdiag ^ t‖ ≤ ‖C * multiJacobian a η q Kmulti ^ t‖) ∧
      (⨆ t : ℕ, ‖C * multiJacobian a η q Kdiag ^ t‖) ≤
        (⨆ t : ℕ, ‖C * multiJacobian a η q Kmulti ^ t‖) ∧
      B / (⨆ t : ℕ, ‖C * multiJacobian a η q Kmulti ^ t‖) ≤
        B / (⨆ t : ℕ, ‖C * multiJacobian a η q Kdiag ^ t‖) := by
  obtain ⟨hJ, hJJ⟩ := multiJacobian_entry_mono a η q Kdiag Kmulti ha hη0 hη1 hq hK hKK
  exact ⟨output_norm_mono hC hJ hJJ, (peak_gain_mono hC hJ hJJ hbdd).2,
    exact_radius_contraction hC hCne hJ hJJ B hB hbdd⟩

/-- Partial real-radius Neumann resolvent `R_N(r, A) = ∑_{t < N} r^{-(t+1)} A^t`. -/
def neumannPartialResolvent (N : ℕ) (r : ℝ) (A : Matrix ι ι ℝ) : Matrix ι ι ℝ :=
  ∑ t ∈ Finset.range N, (r ^ (t + 1))⁻¹ • (A ^ t)

/-- Proposition 2.16: Entrywise nonnegativity and monotonicity of the real-radius Neumann resolvent series. -/
theorem neumann_partial_entry_mono {A A' : Matrix ι ι ℝ} (hA : EntryNonneg A) (hAA : EntryLE A A')
    (N : ℕ) (r : ℝ) (hr : 0 < r) :
    EntryNonneg (neumannPartialResolvent N r A) ∧
      EntryLE (neumannPartialResolvent N r A) (neumannPartialResolvent N r A') := by
  refine ⟨fun i j => ?_, fun i j => ?_⟩
  · simp only [neumannPartialResolvent, Matrix.sum_apply, Matrix.smul_apply, smul_eq_mul]
    exact Finset.sum_nonneg fun t _ =>
      mul_nonneg (inv_nonneg.mpr (pow_nonneg hr.le _)) ((entry_pow_mono hA hAA t).1 i j)
  · simp only [neumannPartialResolvent, Matrix.sum_apply, Matrix.smul_apply, smul_eq_mul]
    exact Finset.sum_le_sum fun t _ =>
      mul_le_mul_of_nonneg_left ((entry_pow_mono hA hAA t).2 i j)
        (inv_nonneg.mpr (pow_nonneg hr.le _))

/-- Proposition 2.16: Euclidean operator-norm monotonicity of the real-radius Neumann resolvent and Kreiss weight `(r - 1) ‖R_N(r, A)‖₂`. -/
theorem neumann_partial_opNorm_mono {A A' : Matrix ι ι ℝ} (hA : EntryNonneg A) (hAA : EntryLE A A')
    (N : ℕ) (r : ℝ) (hr1 : 1 < r) :
    ‖neumannPartialResolvent N r A‖ ≤ ‖neumannPartialResolvent N r A'‖ ∧
      (r - 1) * ‖neumannPartialResolvent N r A‖ ≤ (r - 1) * ‖neumannPartialResolvent N r A'‖ := by
  have hr : 0 < r := by linarith
  obtain ⟨h1, h2⟩ := neumann_partial_entry_mono hA hAA N r hr
  have hnorm := l2_opNorm_mono_of_entry h1 h2
  exact ⟨hnorm, mul_le_mul_of_nonneg_left hnorm (by linarith)⟩

/-- Proposition 2.16: Conservative safe radius contraction `B / (c_dim * K_multi) ≤ B / (c_dim * K_diag)` when `0 < K_diag ≤ K_multi`. -/
theorem cross_impact_conservative_radius_contraction
    (B c_dim K_diag K_multi : ℝ) (hB : 0 < B) (hc : 0 < c_dim)
    (hKd : 0 < K_diag) (hK : K_diag ≤ K_multi) :
    B / (c_dim * K_multi) ≤ B / (c_dim * K_diag) := by
  apply div_le_div_of_nonneg_left hB.le (mul_pos hc hKd)
  exact mul_le_mul_of_nonneg_left hK hc.le

end
end CurrentMM

