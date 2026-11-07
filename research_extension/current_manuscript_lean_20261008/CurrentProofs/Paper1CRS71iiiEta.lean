import CurrentProofs.Paper1CRS71iii

/-!
# Paper 1, Proposition S7.1 (iii) in the paper's coordinates `θ = (w₁, w₂, η₁, η₂)`

Proposition `prop:crb` parametrizes the cohorts by merged weights and adjustment speeds `ηᵢ = 1 - rᵢ`.

* `p1EtaToR`: the affine change `(w, η) ↦ (w, 1 - η)`.
* `p1D`: its linear part, `diag(1, 1, -1, -1)`.
* `p1_tapEta_line_deriv`: along every line in `(w, η)` coordinates, the taps have derivative `(J_r D x)_t`. So
  `J_η = J_r D` is the observation Jacobian in the paper's coordinates, in exactly the form the Cramér–Rao theorem
  `p1_thm_gaussian_cramer_rao` uses.
* `p1_fisher_eta_entry`: `[(J_ηᵀJ_η)⁻¹]₁₁ = [(J_rᵀJ_r)⁻¹]₁₁`, and `J_ηᵀJ_η` is invertible when `J_rᵀJ_r` is.
* `p1_prop_S7_1_iii_eta`: the two-sided `(Δη)⁻⁶` bound for the weight entry, with `Δη = η₁ - η₂`.
-/

namespace CurrentMM

open Finset Matrix

/-- `(w, η) ↦ (w, r)` with `r = 1 - η`. -/
def p1EtaToR (θ : Fin 4 → ℝ) : Fin 4 → ℝ := fun i => if (i : ℕ) < 2 then θ i else 1 - θ i

/-- The linear part of `p1EtaToR`. -/
def p1D : Matrix (Fin 4) (Fin 4) ℝ := Matrix.diagonal fun i => if (i : ℕ) < 2 then (1 : ℝ) else -1

theorem p1_etaToR_line (θ x : Fin 4 → ℝ) (s : ℝ) :
    p1EtaToR (θ + s • x) = p1EtaToR θ + s • (p1D *ᵥ x) := by
  funext i
  simp only [Pi.add_apply, Pi.smul_apply, smul_eq_mul, p1EtaToR, p1D, Matrix.mulVec_diagonal]
  split_ifs <;> ring

/-- **`J_r D` is the Jacobian in `(w, η)` coordinates**, along every line. -/
theorem p1_tapEta_line_deriv (a κ : ℝ) (T : ℕ) (θ0 x : Fin 4 → ℝ) (t : Fin (T + 1)) :
    HasDerivAt (fun s : ℝ => p1TapW a κ (p1EtaToR (θ0 + s • x)) t.val)
      ((p1TapJac a κ T (p1EtaToR θ0) * p1D) *ᵥ x) t) 0 := by
  have e : (fun s : ℝ => p1TapW a κ (p1EtaToR (θ0 + s • x)) t.val) =
      fun s : ℝ => p1TapW a κ (p1EtaToR θ0 + s • (p1D *ᵥ x)) t.val := by
    funext s
    rw [p1_etaToR_line]
  rw [e, ← Matrix.mulVec_mulVec]
  exact p1_tapJac_line_deriv a κ T (p1EtaToR θ0) (p1D *ᵥ x) t

theorem p1_D_mul_D : p1D * p1D = 1 := by
  rw [p1D, Matrix.diagonal_mul_diagonal, ← Matrix.diagonal_one]
  congr 1
  funext i
  split_ifs <;> norm_num

theorem p1_D_transpose : p1Dᵀ = p1D := by
  rw [p1D, Matrix.diagonal_transpose]

theorem p1_D_det : p1D.det = 1 := by
  rw [p1D, Matrix.det_diagonal, Fin.prod_univ_four]
  first
  | (simp; done)
  | norm_num
  | decide

/-- **The weight entry does not depend on whether rates are written as `r` or `η`.** -/
theorem p1_fisher_eta_entry {n : ℕ} (J : Matrix (Fin n) (Fin 4) ℝ) (hJ : IsUnit (Jᵀ * J).det) :
    IsUnit ((J * p1D)ᵀ * (J * p1D)).det ∧ ((J * p1D)ᵀ * (J * p1D))⁻¹ 0 0 = (Jᵀ * J)⁻¹ 0 0 := by
  have e : (J * p1D)ᵀ * (J * p1D) = p1D * (Jᵀ * J) * p1D := by
    rw [Matrix.transpose_mul, p1_D_transpose]
    simp only [Matrix.mul_assoc]
  rw [e]
  generalize Jᵀ * J = F at hJ ⊢
  have hdet : (p1D * F * p1D).det = F.det := by
    rw [Matrix.det_mul, Matrix.det_mul, p1_D_det, one_mul, mul_one]
  have hinv : (p1D * F * p1D)⁻¹ = p1D * F⁻¹ * p1D := by
    apply Matrix.inv_eq_left_inv
    calc p1D * F⁻¹ * p1D * (p1D * F * p1D) = p1D * F⁻¹ * (p1D * p1D) * F * p1D := by
          simp only [Matrix.mul_assoc]
      _ = p1D * (F⁻¹ * F) * p1D := by
          rw [p1_D_mul_D, Matrix.mul_one]
          simp only [Matrix.mul_assoc]
      _ = 1 := by rw [Matrix.nonsing_inv_mul F hJ, Matrix.mul_one, p1_D_mul_D]
  refine ⟨by rw [hdet]; exact hJ, ?_⟩
  rw [hinv]
  simp [p1D, Matrix.mul_diagonal, Matrix.diagonal_mul]

theorem p1_etaToR_eval (w1 w2 e1 e2 : ℝ) : p1EtaToR ![w1, w2, e1, e2] = ![w1, w2, 1 - e1, 1 - e2] := by
  funext i
  fin_cases i <;> simp [p1EtaToR]

/-- **Proposition S7.1 (iii) in the paper's coordinates.** For `θ = (w₁, w₂, η₁, η₂)` with `0 ≤ η₂ < η₁ ≤ 1`, and
`J_η = J_r D` the Jacobian of the observed taps in these coordinates, the weight entry of `(J_ηᵀJ_η)⁻¹` lies between
`c (Δη)⁻⁶` and `C (Δη)⁻⁶`, where `Δη = η₁ - η₂` and `c, C` are the constants of `p1_prop_S7_1_iii`. -/
theorem p1_prop_S7_1_iii_eta (a κ κmin κm wm w1 w2 e1 e2 : ℝ) (T : ℕ) (hT : 4 ≤ T) (hκmin : 0 < κmin)
    (hκ1 : κmin ≤ |κ|) (hκ2 : |κ| ≤ κm) (hw1 : 0 < w1) (hw1' : w1 ≤ wm) (hw2 : 0 < w2) (hw2' : w2 ≤ wm)
    (he2 : 0 ≤ e2) (he21 : e2 < e1) (he1 : e1 ≤ 1) :
    IsUnit ((p1TapJac a κ T (p1EtaToR ![w1, w2, e1, e2]) * p1D)ᵀ *
      (p1TapJac a κ T (p1EtaToR ![w1, w2, e1, e2]) * p1D)).det ∧
    1 / (((T : ℝ) + 1) * ((T : ℝ) ^ 3 * p1TapG |a| κm (2 * wm) T) ^ 2) / (e1 - e2) ^ 6 ≤
      ((p1TapJac a κ T (p1EtaToR ![w1, w2, e1, e2]) * p1D)ᵀ *
        (p1TapJac a κ T (p1EtaToR ![w1, w2, e1, e2]) * p1D))⁻¹ 0 0 ∧
    ((p1TapJac a κ T (p1EtaToR ![w1, w2, e1, e2]) * p1D)ᵀ *
        (p1TapJac a κ T (p1EtaToR ![w1, w2, e1, e2]) * p1D))⁻¹ 0 0 ≤
      5 * ((4 * ((1 + 2 * (|a| + κm * (2 * wm)) + (|a| + κm * (2 * wm)) ^ 2 + 2 * (κm * (2 * wm)) +
          2 * (|a| + κm * (2 * wm)) * (κm * (2 * wm))) * 6) / κmin ^ 2) *
        (4 * ((1 + 2 * (|a| + κm * (2 * wm)) + (|a| + κm * (2 * wm)) ^ 2 + 2 * (κm * (2 * wm)) +
          2 * (|a| + κm * (2 * wm)) * (κm * (2 * wm))) * 6) / κmin ^ 2)) / (e1 - e2) ^ 6 := by
  rw [p1_etaToR_eval]
  have hd : (1 - e2) - (1 - e1) = e1 - e2 := by ring
  obtain ⟨hJ, -, hlo, hhi⟩ := p1_prop_S7_1_iii a κ κmin κm wm w1 w2 (1 - e1) (1 - e2) T hT hκmin hκ1 hκ2 hw1 hw1'
    hw2 hw2' (by linarith) (by linarith) (by linarith)
  rw [hd] at hlo hhi
  obtain ⟨hJη, hentry⟩ := p1_fisher_eta_entry _ hJ
  refine ⟨hJη, ?_, ?_⟩
  · rw [hentry]; exact hlo
  · rw [hentry]; exact hhi

end CurrentMM
