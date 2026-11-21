import Mathlib

/-!
# Paper 1, 21 November 2026: Theorem `n:minimax` (uniform policies are minimax without tags)

Classes are indexed by a finite type `ι`. Class `d` contributes `H d` to the feedback budget. A label-based policy
scales the class carrying label `c` by `θ c`. The record does not reveal which class carries which label: under the
labelling `σ` the label `c` is carried by class `σ c`, and the budget after the policy is
`B θ σ = A + ∑ c, θ c * H (σ c)`.

* `perm_sum_const`: `∑ σ, H (σ c)` does not depend on `c`.
* `perm_average_budget`: averaged over all labellings, the budget is `A + θ̄ U` with `θ̄ = (∑ θ)/K`, `U = ∑ H`.
* `perm_average_policy`: averaged over all labellings, the relabeled policy is the uniform policy `θ̄`.
* `minimax_uniform_loss`: for a convex loss, the uniform policy's loss is at most the average, and so the worst,
  loss of `θ` over labellings.
* `minimax_uniform_cost`: for a convex cost invariant to relabeling, the uniform policy costs at most `θ`.
* `minimax_uniform`: the uniform policy weakly dominates `θ` against the worst labelling.
-/
namespace Paper1Revision10

open scoped BigOperators
open Finset

variable {ι : Type*} [Fintype ι] [DecidableEq ι]

/-- The budget after the label-based policy `θ` under the labelling `σ`. -/
def budget (A : ℝ) (H θ : ι → ℝ) (σ : Equiv.Perm ι) : ℝ := A + ∑ c, θ c * H (σ c)

/-- `∑_σ H (σ c)` is the same for every label `c`. -/
theorem perm_sum_const (H : ι → ℝ) (c c' : ι) :
    ∑ σ : Equiv.Perm ι, H (σ c) = ∑ σ : Equiv.Perm ι, H (σ c') := by
  refine (Fintype.sum_equiv (Equiv.mulRight (Equiv.swap c c')) _ _ ?_)
  intro σ
  simp [Equiv.Perm.mul_apply, Equiv.swap_apply_right]

/-- Hence `K · ∑_σ H (σ c) = |Perm| · U`. -/
theorem perm_sum_total (H : ι → ℝ) (c : ι) :
    (Fintype.card ι : ℝ) * ∑ σ : Equiv.Perm ι, H (σ c) =
      (Fintype.card (Equiv.Perm ι) : ℝ) * ∑ d, H d := by
  have h1 : ∑ d : ι, ∑ σ : Equiv.Perm ι, H (σ d) = (Fintype.card ι : ℝ) * ∑ σ : Equiv.Perm ι, H (σ c) := by
    rw [Finset.sum_congr rfl (fun d _ => perm_sum_const H d c)]
    simp [Finset.sum_const, nsmul_eq_mul]
  have h2 : ∑ d : ι, ∑ σ : Equiv.Perm ι, H (σ d) = ∑ σ : Equiv.Perm ι, ∑ d, H (σ d) := Finset.sum_comm
  have h3 : ∀ σ : Equiv.Perm ι, ∑ d, H (σ d) = ∑ d, H d := fun σ => Equiv.sum_comp σ H
  rw [Finset.sum_congr rfl (fun σ _ => h3 σ)] at h2
  simp only [Finset.sum_const, Finset.card_univ, nsmul_eq_mul] at h2
  linarith

variable [Nonempty ι]

/-- Averaged over all labellings, the budget is `A + θ̄ U`. -/
theorem perm_average_budget (A : ℝ) (H θ : ι → ℝ) :
    (Fintype.card (Equiv.Perm ι) : ℝ)⁻¹ * ∑ σ : Equiv.Perm ι, budget A H θ σ =
      A + (∑ c, θ c) / Fintype.card ι * ∑ d, H d := by
  have hK : (0 : ℝ) < Fintype.card ι := by exact_mod_cast Fintype.card_pos
  have hP : (0 : ℝ) < Fintype.card (Equiv.Perm ι) := by exact_mod_cast Fintype.card_pos
  obtain ⟨c0⟩ := (inferInstance : Nonempty ι)
  have hsum : ∀ c, ∑ σ : Equiv.Perm ι, H (σ c) =
      (Fintype.card (Equiv.Perm ι) : ℝ) * (∑ d, H d) / Fintype.card ι := by
    intro c
    rw [eq_div_iff hK.ne', mul_comm]
    exact perm_sum_total H c
  unfold budget
  rw [Finset.sum_add_distrib, Finset.sum_comm]
  simp only [Finset.sum_const, Finset.card_univ, nsmul_eq_mul]
  rw [Finset.sum_congr rfl (fun c _ => by rw [← Finset.mul_sum, hsum c])]
  rw [← Finset.sum_mul]
  field_simp

/-- Averaged over all labellings, the relabeled policy is the uniform policy. -/
theorem perm_average_policy (θ : ι → ℝ) (c : ι) :
    (Fintype.card (Equiv.Perm ι) : ℝ)⁻¹ * ∑ σ : Equiv.Perm ι, θ (σ c) = (∑ d, θ d) / Fintype.card ι := by
  have hK : (0 : ℝ) < Fintype.card ι := by exact_mod_cast Fintype.card_pos
  have hP : (0 : ℝ) < Fintype.card (Equiv.Perm ι) := by exact_mod_cast Fintype.card_pos
  have h := perm_sum_total θ c
  field_simp
  linarith

/-- A convex loss of the budget: the uniform policy's loss is at most the average loss of `θ` over labellings. -/
theorem minimax_uniform_loss (A : ℝ) (H θ : ι → ℝ) (L : ℝ → ℝ) (hL : ConvexOn ℝ Set.univ L) :
    L (A + (∑ c, θ c) / Fintype.card ι * ∑ d, H d) ≤
      (Fintype.card (Equiv.Perm ι) : ℝ)⁻¹ * ∑ σ : Equiv.Perm ι, L (budget A H θ σ) := by
  have hP : (0 : ℝ) < Fintype.card (Equiv.Perm ι) := by exact_mod_cast Fintype.card_pos
  have hw0 : ∀ σ ∈ (Finset.univ : Finset (Equiv.Perm ι)), (0 : ℝ) ≤ (Fintype.card (Equiv.Perm ι) : ℝ)⁻¹ :=
    fun _ _ => inv_nonneg.mpr hP.le
  have hw1 : ∑ σ ∈ (Finset.univ : Finset (Equiv.Perm ι)), (Fintype.card (Equiv.Perm ι) : ℝ)⁻¹ = 1 := by
    simp [Finset.sum_const, Finset.card_univ, nsmul_eq_mul, hP.ne']
  have hJ := hL.map_sum_le hw0 hw1 (fun σ _ => Set.mem_univ (budget A H θ σ))
  simp only [smul_eq_mul] at hJ
  rw [← Finset.mul_sum, ← Finset.mul_sum, perm_average_budget] at hJ
  exact hJ

/-- ... and so at most its worst loss. -/
theorem minimax_uniform_worst (A : ℝ) (H θ : ι → ℝ) (L : ℝ → ℝ) (hL : ConvexOn ℝ Set.univ L) :
    L (A + (∑ c, θ c) / Fintype.card ι * ∑ d, H d) ≤
      Finset.univ.sup' Finset.univ_nonempty (fun σ : Equiv.Perm ι => L (budget A H θ σ)) := by
  have hP : (0 : ℝ) < Fintype.card (Equiv.Perm ι) := by exact_mod_cast Fintype.card_pos
  refine le_trans (minimax_uniform_loss A H θ L hL) ?_
  set M := Finset.univ.sup' Finset.univ_nonempty (fun σ : Equiv.Perm ι => L (budget A H θ σ))
  have hle : ∑ σ : Equiv.Perm ι, L (budget A H θ σ) ≤ ∑ _σ : Equiv.Perm ι, M :=
    Finset.sum_le_sum (fun σ _ => Finset.le_sup' (fun σ : Equiv.Perm ι => L (budget A H θ σ)) (Finset.mem_univ σ))
  simp only [Finset.sum_const, Finset.card_univ, nsmul_eq_mul] at hle
  calc (Fintype.card (Equiv.Perm ι) : ℝ)⁻¹ * ∑ σ : Equiv.Perm ι, L (budget A H θ σ)
      ≤ (Fintype.card (Equiv.Perm ι) : ℝ)⁻¹ * ((Fintype.card (Equiv.Perm ι) : ℝ) * M) :=
        mul_le_mul_of_nonneg_left hle (inv_nonneg.mpr hP.le)
    _ = M := by field_simp

/-- A convex cost invariant to relabeling: the uniform policy costs at most `θ`. -/
theorem minimax_uniform_cost (θ : ι → ℝ) (C : (ι → ℝ) → ℝ) (hC : ConvexOn ℝ Set.univ C)
    (hinv : ∀ σ : Equiv.Perm ι, C (fun c => θ (σ c)) = C θ) :
    C (fun _ => (∑ d, θ d) / Fintype.card ι) ≤ C θ := by
  have hP : (0 : ℝ) < Fintype.card (Equiv.Perm ι) := by exact_mod_cast Fintype.card_pos
  have hw0 : ∀ σ ∈ (Finset.univ : Finset (Equiv.Perm ι)), (0 : ℝ) ≤ (Fintype.card (Equiv.Perm ι) : ℝ)⁻¹ :=
    fun _ _ => inv_nonneg.mpr hP.le
  have hw1 : ∑ σ ∈ (Finset.univ : Finset (Equiv.Perm ι)), (Fintype.card (Equiv.Perm ι) : ℝ)⁻¹ = 1 := by
    simp [Finset.sum_const, Finset.card_univ, nsmul_eq_mul, hP.ne']
  have hJ := hC.map_sum_le hw0 hw1 (fun σ _ => Set.mem_univ (fun c => θ (σ c)))
  have havg : (∑ σ : Equiv.Perm ι, (Fintype.card (Equiv.Perm ι) : ℝ)⁻¹ • (fun c => θ (σ c))) =
      fun _ => (∑ d, θ d) / Fintype.card ι := by
    funext c
    rw [Finset.sum_apply]
    simp only [Pi.smul_apply, smul_eq_mul]
    rw [← Finset.mul_sum, perm_average_policy θ c]
  rw [havg] at hJ
  calc C (fun _ => (∑ d, θ d) / Fintype.card ι)
      ≤ ∑ σ : Equiv.Perm ι, (Fintype.card (Equiv.Perm ι) : ℝ)⁻¹ • C (fun c => θ (σ c)) := hJ
    _ = ∑ _σ : Equiv.Perm ι, (Fintype.card (Equiv.Perm ι) : ℝ)⁻¹ * C θ := by
        refine Finset.sum_congr rfl (fun σ _ => ?_); rw [smul_eq_mul, hinv σ]
    _ = C θ := by simp [Finset.sum_const, Finset.card_univ, nsmul_eq_mul, hP.ne']

/-- **Theorem `n:minimax`.** Against the worst labelling, the uniform policy does at least as well as any
label-based policy: its loss plus cost is at most the worst loss of `θ` plus the cost of `θ`. -/
theorem minimax_uniform (A : ℝ) (H θ : ι → ℝ) (L : ℝ → ℝ) (hL : ConvexOn ℝ Set.univ L)
    (C : (ι → ℝ) → ℝ) (hC : ConvexOn ℝ Set.univ C) (hinv : ∀ σ : Equiv.Perm ι, C (fun c => θ (σ c)) = C θ) :
    L (A + (∑ c, θ c) / Fintype.card ι * ∑ d, H d) + C (fun _ => (∑ d, θ d) / Fintype.card ι) ≤
      Finset.univ.sup' Finset.univ_nonempty (fun σ : Equiv.Perm ι => L (budget A H θ σ)) + C θ :=
  add_le_add (minimax_uniform_worst A H θ L hL) (minimax_uniform_cost θ C hC hinv)

/-- The uniform policy's budget does not depend on the labelling. -/
theorem uniform_budget_label_free (A : ℝ) (H : ι → ℝ) (t : ℝ) (σ : Equiv.Perm ι) :
    budget A H (fun _ => t) σ = A + t * ∑ d, H d := by
  unfold budget
  rw [← Finset.mul_sum, Equiv.sum_comp σ H]

end Paper1Revision10
