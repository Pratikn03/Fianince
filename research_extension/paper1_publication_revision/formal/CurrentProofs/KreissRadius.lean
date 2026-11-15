import Mathlib.Analysis.CStarAlgebra.Matrix
import Mathlib.Analysis.SpecificLimits.Normed

/-!
# Theorem 2.14 (Conditional Loss Budget and Kreiss Bounds)

All matrix norms are the Euclidean (spectral) operator norms supplied by mathlib's scoped
instance `Matrix.Norms.L2Operator`; vectors live in `EuclideanSpace 𝕜 (Fin n)`.

* Part 1 (exact safe radius): `exact_safe_radius_sufficient`, `exact_safe_radius_necessary`,
  `exact_safe_radius_isGreatest`, `zero_output_no_radius_bound`.  The finiteness of
  `M_C = sup_t ‖C J^t‖` is an explicit `BddAbove` hypothesis (the manuscript derives it from
  `ρ(J) < 1` through Gelfand's formula, which is not reproduced here).
-/

open scoped Matrix.Norms.L2Operator
open Matrix Filter Topology

namespace CurrentMM
noncomputable section

variable {𝕜 : Type*} [RCLike 𝕜]

/-- Euclidean output `A z` of a matrix applied to a Euclidean vector. -/
def l2Apply {m n : ℕ} (A : Matrix (Fin m) (Fin n) 𝕜) (z : EuclideanSpace 𝕜 (Fin n)) :
    EuclideanSpace 𝕜 (Fin m) :=
  WithLp.toLp 2 (A *ᵥ WithLp.ofLp z)

/-- The continuous linear map attached to a matrix; its norm is the L2 operator norm. -/
def l2CLM {m n : ℕ} (A : Matrix (Fin m) (Fin n) 𝕜) :
    EuclideanSpace 𝕜 (Fin n) →L[𝕜] EuclideanSpace 𝕜 (Fin m) :=
  (toEuclideanLin (𝕜 := 𝕜) (m := Fin m) (n := Fin n)).trans LinearMap.toContinuousLinearMap A

lemma l2CLM_apply {m n : ℕ} (A : Matrix (Fin m) (Fin n) 𝕜) (z : EuclideanSpace 𝕜 (Fin n)) :
    l2CLM A z = l2Apply A z := rfl

lemma l2CLM_norm {m n : ℕ} (A : Matrix (Fin m) (Fin n) 𝕜) : ‖l2CLM A‖ = ‖A‖ := rfl

lemma norm_l2Apply_le {m n : ℕ} (A : Matrix (Fin m) (Fin n) 𝕜) (z : EuclideanSpace 𝕜 (Fin n)) :
    ‖l2Apply A z‖ ≤ ‖A‖ * ‖z‖ := by
  rw [← l2CLM_apply, ← l2CLM_norm]
  exact (l2CLM A).le_opNorm z

/-- Declared peak output gain `M_C = sup_{t ≥ 0} ‖C J^t‖₂`. -/
def outputGain {m n : ℕ} (C : Matrix (Fin m) (Fin n) 𝕜) (J : Matrix (Fin n) (Fin n) 𝕜) : ℝ :=
  ⨆ t : ℕ, ‖C * J ^ t‖

theorem outputGain_ge {m n : ℕ} (C : Matrix (Fin m) (Fin n) 𝕜) (J : Matrix (Fin n) (Fin n) 𝕜)
    (hbdd : BddAbove (Set.range fun t : ℕ => ‖C * J ^ t‖)) (t : ℕ) :
    ‖C * J ^ t‖ ≤ outputGain C J :=
  le_ciSup hbdd t

theorem outputGain_pos {m n : ℕ} (C : Matrix (Fin m) (Fin n) 𝕜) (J : Matrix (Fin n) (Fin n) 𝕜)
    (hbdd : BddAbove (Set.range fun t : ℕ => ‖C * J ^ t‖)) (hC : C ≠ 0) :
    0 < outputGain C J := by
  have h0 := outputGain_ge C J hbdd 0
  rw [pow_zero, Matrix.mul_one] at h0
  have : 0 < ‖C‖ := norm_pos_iff.mpr hC
  linarith

/-- Part 1, sufficiency: every initial state in the ball of radius `B / M_C` respects the
loss budget at every horizon. -/
theorem exact_safe_radius_sufficient {m n : ℕ} (C : Matrix (Fin m) (Fin n) 𝕜)
    (J : Matrix (Fin n) (Fin n) 𝕜) (B : ℝ)
    (hbdd : BddAbove (Set.range fun t : ℕ => ‖C * J ^ t‖)) (hC : C ≠ 0)
    (z : EuclideanSpace 𝕜 (Fin n)) (hz : ‖z‖ ≤ B / outputGain C J) (t : ℕ) :
    ‖l2Apply (C * J ^ t) z‖ ≤ B := by
  have hM := outputGain_pos C J hbdd hC
  calc ‖l2Apply (C * J ^ t) z‖ ≤ ‖C * J ^ t‖ * ‖z‖ := norm_l2Apply_le _ _
    _ ≤ outputGain C J * (B / outputGain C J) :=
        mul_le_mul (outputGain_ge C J hbdd t) hz (norm_nonneg _) hM.le
    _ = B := by field_simp

/-- Part 1, necessity: for every radius above `B / M_C` some initial state of exactly that
norm breaches the budget at some horizon. -/
theorem exact_safe_radius_necessary {m n : ℕ} (C : Matrix (Fin m) (Fin n) 𝕜)
    (J : Matrix (Fin n) (Fin n) 𝕜) (B : ℝ)
    (hbdd : BddAbove (Set.range fun t : ℕ => ‖C * J ^ t‖)) (hC : C ≠ 0) (hB : 0 < B)
    (r : ℝ) (hr : B / outputGain C J < r) :
    ∃ z : EuclideanSpace 𝕜 (Fin n), ‖z‖ = r ∧ ∃ t : ℕ, B < ‖l2Apply (C * J ^ t) z‖ := by
  have hM := outputGain_pos C J hbdd hC
  have hr0 : 0 < r := lt_trans (div_pos hB hM) hr
  have hBr : B / r < outputGain C J := by
    rw [div_lt_iff₀ hr0]
    rw [div_lt_iff₀ hM] at hr
    linarith [mul_comm r (outputGain C J)]
  obtain ⟨t, ht⟩ := exists_lt_of_lt_ciSup hBr
  obtain ⟨x, hx1, hx⟩ := (l2CLM (C * J ^ t)).exists_lt_apply_of_lt_opNorm ht
  rw [l2CLM_apply] at hx
  have hBr0 : 0 < B / r := div_pos hB hr0
  have hxpos : 0 < ‖x‖ := by
    rcases (norm_nonneg x).eq_or_lt with h | h
    · exfalso
      have hx0 : x = 0 := norm_eq_zero.mp h.symm
      subst hx0
      have : l2Apply (C * J ^ t) (0 : EuclideanSpace 𝕜 (Fin n)) = 0 := by
        rw [← l2CLM_apply, map_zero]
      rw [this, norm_zero] at hx
      linarith
    · exact h
  have hc : 0 < r / ‖x‖ := div_pos hr0 hxpos
  refine ⟨((r / ‖x‖ : ℝ) : 𝕜) • x, ?_, t, ?_⟩
  · rw [norm_smul, RCLike.norm_ofReal, abs_of_pos hc]
    field_simp
  · have hlin : l2Apply (C * J ^ t) (((r / ‖x‖ : ℝ) : 𝕜) • x) =
        ((r / ‖x‖ : ℝ) : 𝕜) • l2Apply (C * J ^ t) x := by
      rw [← l2CLM_apply, map_smul, l2CLM_apply]
    rw [hlin, norm_smul, RCLike.norm_ofReal, abs_of_pos hc, div_mul_eq_mul_div,
      lt_div_iff₀ hxpos]
    have h1 : B < r * ‖l2Apply (C * J ^ t) x‖ := by
      rw [div_lt_iff₀ hr0] at hx
      linarith [mul_comm r ‖l2Apply (C * J ^ t) x‖]
    nlinarith

/-- Part 1, exact radius: `B / M_C` is the largest radius `r` such that every initial state
with `‖z₀‖ ≤ r` satisfies `sup_t ‖C J^t z₀‖ ≤ B`. -/
theorem exact_safe_radius_isGreatest {m n : ℕ} (C : Matrix (Fin m) (Fin n) 𝕜)
    (J : Matrix (Fin n) (Fin n) 𝕜) (B : ℝ)
    (hbdd : BddAbove (Set.range fun t : ℕ => ‖C * J ^ t‖)) (hC : C ≠ 0) (hB : 0 < B) :
    IsGreatest {r : ℝ | 0 ≤ r ∧ ∀ z : EuclideanSpace 𝕜 (Fin n), ‖z‖ ≤ r →
        ∀ t : ℕ, ‖l2Apply (C * J ^ t) z‖ ≤ B} (B / outputGain C J) := by
  have hM := outputGain_pos C J hbdd hC
  refine ⟨⟨(div_pos hB hM).le, fun z hz t => exact_safe_radius_sufficient C J B hbdd hC z hz t⟩,
    ?_⟩
  rintro r ⟨-, hr⟩
  by_contra h
  rw [not_le] at h
  obtain ⟨z, hz, t, ht⟩ := exact_safe_radius_necessary C J B hbdd hC hB r h
  exact absurd (hr z hz.le t) (not_le.mpr ht)

/-- Part 1, the `C = 0` case: the criterion imposes no bound on the initial state. -/
theorem zero_output_no_radius_bound {m n : ℕ} (J : Matrix (Fin n) (Fin n) 𝕜) (B : ℝ)
    (hB : 0 ≤ B) (z : EuclideanSpace 𝕜 (Fin n)) (t : ℕ) :
    ‖l2Apply ((0 : Matrix (Fin m) (Fin n) 𝕜) * J ^ t) z‖ ≤ B := by
  have : l2Apply ((0 : Matrix (Fin m) (Fin n) 𝕜) * J ^ t) z = 0 := by
    simp [l2Apply]
  rw [this, norm_zero]
  exact hB

end
end CurrentMM
