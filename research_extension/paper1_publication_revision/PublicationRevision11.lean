import Mathlib

/-!
# Paper 1, 21 November 2026: Theorem `n:minimaxtags` (tags and minimax policies)

Classes `ι` carry verified tags `τ : ι → T`. The record identifies each class's tagged group but cannot rule out
relabelings inside a group: the labellings consistent with it are the permutations that keep every class in its
group (`tagPerms τ`). Class `d` contributes `H d` to the feedback budget; a label policy `θ` gives the budget
`A + ∑ c, θ c * H (σ c)` under the labelling `σ`.

* `tag_sum_const`: inside a group, `∑_{σ} H (σ c)` does not depend on `c`.
* `tag_count`: `|grp c| · ∑_{σ} H (σ c) = |tagPerms| · ∑_{d ∈ grp c} H d`.
* `tag_average_budget`: averaged over consistent labellings, the budget is `A + ∑ c, θ c · (mean of H over grp c)`.
* `group_policy_budget`: the group-average policy has exactly that budget under every consistent labelling.
* `tag_minimax`: for a convex loss and a convex cost invariant under consistent relabelings, the group-average policy
  weakly dominates `θ` against the worst consistent labelling.
With one group (no tags) this is `n:minimax`; with every class its own group, every policy is a group policy.
-/
namespace Paper1Revision11

open scoped BigOperators
open Finset

variable {ι T : Type*} [Fintype ι] [DecidableEq ι] [DecidableEq T]

/-- Labellings the tags cannot rule out: those that keep every class in its tagged group. -/
def tagPerms (τ : ι → T) : Finset (Equiv.Perm ι) :=
  univ.filter (fun σ => ∀ c, τ (σ c) = τ c)

/-- The tagged group of `c`. -/
def grp (τ : ι → T) (c : ι) : Finset ι := univ.filter (fun d => τ d = τ c)

theorem mem_tagPerms (τ : ι → T) (σ : Equiv.Perm ι) : σ ∈ tagPerms τ ↔ ∀ c, τ (σ c) = τ c := by
  simp [tagPerms]

theorem one_mem_tagPerms (τ : ι → T) : (1 : Equiv.Perm ι) ∈ tagPerms τ := by
  simp [tagPerms]

theorem tagPerms_nonempty (τ : ι → T) : (tagPerms τ).Nonempty := ⟨1, one_mem_tagPerms τ⟩

theorem mul_mem_tagPerms (τ : ι → T) {σ ρ : Equiv.Perm ι} (hσ : σ ∈ tagPerms τ) (hρ : ρ ∈ tagPerms τ) :
    σ * ρ ∈ tagPerms τ := by
  rw [mem_tagPerms] at *
  intro c
  rw [Equiv.Perm.mul_apply, hσ, hρ]

theorem inv_mem_tagPerms (τ : ι → T) {σ : Equiv.Perm ι} (hσ : σ ∈ tagPerms τ) : σ⁻¹ ∈ tagPerms τ := by
  rw [mem_tagPerms] at *
  intro c
  have h := hσ (σ⁻¹ c)
  rw [show σ (σ⁻¹ c) = c from by simp] at h
  exact h.symm

theorem swap_mem_tagPerms (τ : ι → T) {c c' : ι} (h : τ c = τ c') : Equiv.swap c c' ∈ tagPerms τ := by
  rw [mem_tagPerms]
  intro x
  rcases eq_or_ne x c with rfl | hx
  · rw [Equiv.swap_apply_left]; exact h.symm
  rcases eq_or_ne x c' with rfl | hx'
  · rw [Equiv.swap_apply_right]; exact h
  · rw [Equiv.swap_apply_of_ne_of_ne hx hx']

theorem mem_grp (τ : ι → T) (c d : ι) : d ∈ grp τ c ↔ τ d = τ c := by
  simp [grp]

theorem self_mem_grp (τ : ι → T) (c : ι) : c ∈ grp τ c := by
  simp [grp]

theorem grp_card_pos (τ : ι → T) (c : ι) : (0 : ℝ) < (grp τ c).card := by
  exact_mod_cast Finset.card_pos.mpr ⟨c, self_mem_grp τ c⟩

theorem grp_eq_of_tag (τ : ι → T) {c c' : ι} (h : τ c = τ c') : grp τ c = grp τ c' := by
  ext d; simp [grp, h]

/-- Inside a tagged group, `∑_σ H (σ c)` does not depend on `c`. -/
theorem tag_sum_const (τ : ι → T) (H : ι → ℝ) {c c' : ι} (h : τ c = τ c') :
    ∑ σ ∈ tagPerms τ, H (σ c) = ∑ σ ∈ tagPerms τ, H (σ c') := by
  have hs := swap_mem_tagPerms τ h
  refine Finset.sum_nbij' (fun σ => σ * Equiv.swap c c') (fun σ => σ * Equiv.swap c c')
    (fun σ hσ => mul_mem_tagPerms τ hσ hs) (fun σ hσ => mul_mem_tagPerms τ hσ hs)
    (fun σ _ => by simp [mul_assoc]) (fun σ _ => by simp [mul_assoc]) ?_
  intro σ _
  simp [Equiv.Perm.mul_apply, Equiv.swap_apply_right]

/-- A consistent labelling permutes each group, so the group sum is unchanged. -/
theorem grp_sum_perm (τ : ι → T) (H : ι → ℝ) (c : ι) {σ : Equiv.Perm ι} (hσ : σ ∈ tagPerms τ) :
    ∑ d ∈ grp τ c, H (σ d) = ∑ d ∈ grp τ c, H d := by
  have hσ' := inv_mem_tagPerms τ hσ
  rw [mem_tagPerms] at hσ hσ'
  refine Finset.sum_nbij' (fun d => σ d) (fun d => σ⁻¹ d) ?_ ?_ ?_ ?_ ?_
  · intro d hd; rw [mem_grp] at *; rw [hσ]; exact hd
  · intro d hd; rw [mem_grp] at *; rw [hσ']; exact hd
  · intro d _; simp
  · intro d _; simp
  · intro d _; rfl

/-- Counting: `|grp c| · ∑_σ H (σ c) = |tagPerms| · ∑_{d ∈ grp c} H d`. -/
theorem tag_count (τ : ι → T) (H : ι → ℝ) (c : ι) :
    ((grp τ c).card : ℝ) * ∑ σ ∈ tagPerms τ, H (σ c) =
      ((tagPerms τ).card : ℝ) * ∑ d ∈ grp τ c, H d := by
  have h1 : ∑ d ∈ grp τ c, ∑ σ ∈ tagPerms τ, H (σ d) = ((grp τ c).card : ℝ) * ∑ σ ∈ tagPerms τ, H (σ c) := by
    rw [Finset.sum_congr rfl (fun d hd => tag_sum_const τ H ((mem_grp τ c d).mp hd))]
    simp [Finset.sum_const, nsmul_eq_mul]
  have h2 : ∑ d ∈ grp τ c, ∑ σ ∈ tagPerms τ, H (σ d) = ((tagPerms τ).card : ℝ) * ∑ d ∈ grp τ c, H d := by
    rw [Finset.sum_comm]
    rw [Finset.sum_congr rfl (fun σ hσ => grp_sum_perm τ H c hσ)]
    simp [Finset.sum_const, nsmul_eq_mul]
  linarith

/-- The group mean of `f` at `c`. -/
noncomputable def gmean (τ : ι → T) (f : ι → ℝ) (c : ι) : ℝ := (∑ d ∈ grp τ c, f d) / (grp τ c).card

theorem tag_average_point (τ : ι → T) (H : ι → ℝ) (c : ι) :
    ((tagPerms τ).card : ℝ)⁻¹ * ∑ σ ∈ tagPerms τ, H (σ c) = gmean τ H c := by
  have hS : (0 : ℝ) < (tagPerms τ).card := by exact_mod_cast Finset.card_pos.mpr (tagPerms_nonempty τ)
  have hG := grp_card_pos τ c
  have h := tag_count τ H c
  unfold gmean
  field_simp
  linarith

/-- The budget of a label policy under a labelling. -/
def budget (A : ℝ) (H θ : ι → ℝ) (σ : Equiv.Perm ι) : ℝ := A + ∑ c, θ c * H (σ c)

/-- Averaged over consistent labellings, the budget is `A + ∑ c, θ c · gmean H c`. -/
theorem tag_average_budget (τ : ι → T) (A : ℝ) (H θ : ι → ℝ) :
    ((tagPerms τ).card : ℝ)⁻¹ * ∑ σ ∈ tagPerms τ, budget A H θ σ = A + ∑ c, θ c * gmean τ H c := by
  have hS : (0 : ℝ) < (tagPerms τ).card := by exact_mod_cast Finset.card_pos.mpr (tagPerms_nonempty τ)
  unfold budget
  rw [Finset.sum_add_distrib, Finset.sum_const, nsmul_eq_mul, Finset.sum_comm, mul_add]
  congr 1
  · field_simp
  · rw [Finset.mul_sum]
    refine Finset.sum_congr rfl (fun c _ => ?_)
    rw [← Finset.mul_sum, ← tag_average_point τ H c]
    ring

theorem gmean_perm (τ : ι → T) (f : ι → ℝ) {σ : Equiv.Perm ι} (hσ : σ ∈ tagPerms τ) (c : ι) :
    gmean τ f (σ c) = gmean τ f c := by
  rw [mem_tagPerms] at hσ
  unfold gmean
  rw [grp_eq_of_tag τ (hσ c)]

/-- The pair sum behind the symmetry `∑_c gmean θ c · H c = ∑_c θ c · gmean H c`. -/
theorem gmean_swap (τ : ι → T) (f g : ι → ℝ) :
    ∑ c, gmean τ f c * g c = ∑ c, f c * gmean τ g c := by
  unfold gmean
  have key : ∀ c, (∑ d ∈ grp τ c, f d) / (grp τ c).card * g c =
      ∑ d, if τ d = τ c then f d * g c / (grp τ c).card else 0 := by
    intro c
    rw [← Finset.sum_filter]
    rw [Finset.sum_div, Finset.sum_mul]
    refine Finset.sum_congr rfl (fun d _ => ?_)
    ring
  have key2 : ∀ c, f c * ((∑ d ∈ grp τ c, g d) / (grp τ c).card) =
      ∑ d, if τ d = τ c then f c * g d / (grp τ c).card else 0 := by
    intro c
    rw [← Finset.sum_filter]
    rw [Finset.sum_div, Finset.mul_sum]
    refine Finset.sum_congr rfl (fun d _ => ?_)
    ring
  rw [Finset.sum_congr rfl (fun c _ => key c), Finset.sum_congr rfl (fun c _ => key2 c), Finset.sum_comm]
  refine Finset.sum_congr rfl (fun c _ => Finset.sum_congr rfl (fun d _ => ?_))
  by_cases h : τ c = τ d
  · rw [if_pos h, if_pos h.symm, grp_eq_of_tag τ h]
  · rw [if_neg h, if_neg (Ne.symm h)]

/-- The group-average policy has the averaged budget under every consistent labelling: it does not depend on the
labelling. -/
theorem group_policy_budget (τ : ι → T) (A : ℝ) (H θ : ι → ℝ) {σ : Equiv.Perm ι} (hσ : σ ∈ tagPerms τ) :
    budget A H (gmean τ θ) σ = A + ∑ c, θ c * gmean τ H c := by
  unfold budget
  congr 1
  have h1 : ∑ c, gmean τ θ c * H (σ c) = ∑ e, gmean τ θ (σ⁻¹ e) * H e := by
    rw [← Equiv.sum_comp σ (fun e => gmean τ θ (σ⁻¹ e) * H e)]
    simp
  have h2 : ∀ e, gmean τ θ (σ⁻¹ e) = gmean τ θ e := by
    intro e
    have := gmean_perm τ θ (inv_mem_tagPerms τ hσ) e
    exact this
  rw [h1, Finset.sum_congr rfl (fun e _ => by rw [h2 e])]
  exact gmean_swap τ θ H

/-- Jensen for the loss: the group-average policy's loss is at most the average, and so the worst, loss of `θ`
over consistent labellings. -/
theorem tag_minimax_loss (τ : ι → T) (A : ℝ) (H θ : ι → ℝ) (L : ℝ → ℝ) (hL : ConvexOn ℝ Set.univ L) :
    L (A + ∑ c, θ c * gmean τ H c) ≤
      (tagPerms τ).sup' (tagPerms_nonempty τ) (fun σ => L (budget A H θ σ)) := by
  have hS : (0 : ℝ) < (tagPerms τ).card := by exact_mod_cast Finset.card_pos.mpr (tagPerms_nonempty τ)
  have hw0 : ∀ σ ∈ tagPerms τ, (0 : ℝ) ≤ ((tagPerms τ).card : ℝ)⁻¹ := fun _ _ => inv_nonneg.mpr hS.le
  have hw1 : ∑ σ ∈ tagPerms τ, ((tagPerms τ).card : ℝ)⁻¹ = 1 := by
    rw [Finset.sum_const, nsmul_eq_mul]; field_simp
  have hJ := hL.map_sum_le hw0 hw1 (fun σ _ => Set.mem_univ (budget A H θ σ))
  simp only [smul_eq_mul] at hJ
  rw [← Finset.mul_sum, ← Finset.mul_sum, tag_average_budget] at hJ
  refine le_trans hJ ?_
  set M := (tagPerms τ).sup' (tagPerms_nonempty τ) (fun σ => L (budget A H θ σ))
  have hle : ∑ σ ∈ tagPerms τ, L (budget A H θ σ) ≤ ∑ _σ ∈ tagPerms τ, M :=
    Finset.sum_le_sum (fun σ hσ => Finset.le_sup' (fun σ => L (budget A H θ σ)) hσ)
  rw [Finset.sum_const, nsmul_eq_mul] at hle
  calc ((tagPerms τ).card : ℝ)⁻¹ * ∑ σ ∈ tagPerms τ, L (budget A H θ σ)
      ≤ ((tagPerms τ).card : ℝ)⁻¹ * (((tagPerms τ).card : ℝ) * M) :=
        mul_le_mul_of_nonneg_left hle (inv_nonneg.mpr hS.le)
    _ = M := by field_simp

/-- Jensen for the cost: a convex cost invariant under consistent relabelings is at most `C θ` at the group-average
policy. -/
theorem tag_minimax_cost (τ : ι → T) (θ : ι → ℝ) (C : (ι → ℝ) → ℝ) (hC : ConvexOn ℝ Set.univ C)
    (hinv : ∀ σ ∈ tagPerms τ, C (fun c => θ (σ c)) = C θ) :
    C (gmean τ θ) ≤ C θ := by
  have hS : (0 : ℝ) < (tagPerms τ).card := by exact_mod_cast Finset.card_pos.mpr (tagPerms_nonempty τ)
  have hw0 : ∀ σ ∈ tagPerms τ, (0 : ℝ) ≤ ((tagPerms τ).card : ℝ)⁻¹ := fun _ _ => inv_nonneg.mpr hS.le
  have hw1 : ∑ σ ∈ tagPerms τ, ((tagPerms τ).card : ℝ)⁻¹ = 1 := by
    rw [Finset.sum_const, nsmul_eq_mul]; field_simp
  have hJ := hC.map_sum_le hw0 hw1 (fun σ _ => Set.mem_univ (fun c => θ (σ c)))
  have havg : (∑ σ ∈ tagPerms τ, ((tagPerms τ).card : ℝ)⁻¹ • (fun c => θ (σ c))) = gmean τ θ := by
    funext c
    rw [Finset.sum_apply]
    simp only [Pi.smul_apply, smul_eq_mul]
    rw [← Finset.mul_sum, tag_average_point τ θ c]
  rw [havg] at hJ
  calc C (gmean τ θ)
      ≤ ∑ σ ∈ tagPerms τ, ((tagPerms τ).card : ℝ)⁻¹ • C (fun c => θ (σ c)) := hJ
    _ = ∑ _σ ∈ tagPerms τ, ((tagPerms τ).card : ℝ)⁻¹ * C θ := by
        refine Finset.sum_congr rfl (fun σ hσ => ?_); rw [smul_eq_mul, hinv σ hσ]
    _ = C θ := by rw [Finset.sum_const, nsmul_eq_mul]; field_simp

/-- **Theorem `n:minimaxtags`.** Against the worst labelling consistent with the tags, the group-average policy
does at least as well as any label policy, for a convex loss and a convex cost invariant under consistent
relabelings. -/
theorem tag_minimax (τ : ι → T) (A : ℝ) (H θ : ι → ℝ) (L : ℝ → ℝ) (hL : ConvexOn ℝ Set.univ L)
    (C : (ι → ℝ) → ℝ) (hC : ConvexOn ℝ Set.univ C)
    (hinv : ∀ σ ∈ tagPerms τ, C (fun c => θ (σ c)) = C θ) :
    (tagPerms τ).sup' (tagPerms_nonempty τ) (fun σ => L (budget A H (gmean τ θ) σ)) + C (gmean τ θ) ≤
      (tagPerms τ).sup' (tagPerms_nonempty τ) (fun σ => L (budget A H θ σ)) + C θ := by
  have hconst : (tagPerms τ).sup' (tagPerms_nonempty τ) (fun σ => L (budget A H (gmean τ θ) σ)) =
      L (A + ∑ c, θ c * gmean τ H c) := by
    apply le_antisymm
    · exact Finset.sup'_le _ _ (fun σ hσ => by rw [group_policy_budget τ A H θ hσ])
    · have := Finset.le_sup' (fun σ => L (budget A H (gmean τ θ) σ)) (one_mem_tagPerms τ)
      rw [group_policy_budget τ A H θ (one_mem_tagPerms τ)] at this
      exact this
  rw [hconst]
  exact add_le_add (tag_minimax_loss τ A H θ L hL) (tag_minimax_cost τ θ C hC hinv)

/-- The value of tags is nonnegative: optimizing over group policies is optimizing over a larger set than over
uniform policies, because a uniform policy is a group policy. -/
theorem value_of_tags_nonneg (vUniform vGroup : ℝ) (R : ℝ → ℝ) (S U : Set ℝ) (hsub : U ⊆ S)
    (hG : IsLeast (R '' S) vGroup) (hU : IsLeast (R '' U) vUniform) : 0 ≤ vUniform - vGroup := by
  obtain ⟨⟨u, huU, rfl⟩, _⟩ := hU
  have : R u ∈ R '' S := ⟨u, hsub huU, rfl⟩
  have := hG.2 this
  linarith

end Paper1Revision11
