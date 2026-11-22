import Mathlib

/-!
# Paper 1, 22 November 2026: Theorem `n:minimax`(ii), strict dominance and uniqueness

`PublicationRevision10.lean` checks part (i) of the theorem: averaged over relabelings, the uniform policy does at
least as well as any label-based policy `θ`. This file checks part (ii) for a cost that is strictly convex on a convex,
relabeling-invariant set `S` of policies (for example `[0,1]^K`). The files are standalone, so the definitions and
lemmas of `PublicationRevision10.lean` that are needed are restated here unchanged.

* `minimax_uniform_cost_on`, `minimax_uniform_on`: part (i) for a cost convex only on `S`.
* `minimax_uniform_cost_strict`: a non-uniform policy costs strictly more than its uniform average.
* `minimax_uniform_strict`: against the worst labelling, the uniform average does strictly better than a non-uniform
  policy.
* `minimax_policy_uniform`: every minimax policy is uniform.
* `diag_strict`: along uniform policies the minimax objective is strictly convex.
* `minimax_unique`: the minimax policy is unique (and uniform).

This file was written with AI assistance. It replaces the file `PublicationRevision12_EndToEnd.lean` received on
22 November 2026, which did not compile (five errors) and whose lemma `kl_chain_rule_finite` assumed its conclusion.
-/
namespace Paper1Revision12

open scoped BigOperators
open Finset

variable {ι : Type*} [Fintype ι] [DecidableEq ι]

/-- The budget after the label-based policy `θ` under the labelling `σ` (as in `PublicationRevision10.lean`). -/
def budget (A : ℝ) (H θ : ι → ℝ) (σ : Equiv.Perm ι) : ℝ := A + ∑ c, θ c * H (σ c)

theorem perm_sum_const (H : ι → ℝ) (c c' : ι) :
    ∑ σ : Equiv.Perm ι, H (σ c) = ∑ σ : Equiv.Perm ι, H (σ c') := by
  refine (Fintype.sum_equiv (Equiv.mulRight (Equiv.swap c c')) _ _ ?_)
  intro σ
  simp [Equiv.Perm.mul_apply, Equiv.swap_apply_right]

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

theorem perm_average_policy (θ : ι → ℝ) (c : ι) :
    (Fintype.card (Equiv.Perm ι) : ℝ)⁻¹ * ∑ σ : Equiv.Perm ι, θ (σ c) = (∑ d, θ d) / Fintype.card ι := by
  have hK : (0 : ℝ) < Fintype.card ι := by exact_mod_cast Fintype.card_pos
  have hP : (0 : ℝ) < Fintype.card (Equiv.Perm ι) := by exact_mod_cast Fintype.card_pos
  have h := perm_sum_total θ c
  field_simp
  linarith

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

theorem uniform_budget_label_free (A : ℝ) (H : ι → ℝ) (t : ℝ) (σ : Equiv.Perm ι) :
    budget A H (fun _ => t) σ = A + t * ∑ d, H d := by
  unfold budget
  rw [← Finset.mul_sum, Equiv.sum_comp σ H]

/-! ## New: strict dominance and uniqueness -/

/-- The uniform average of a policy. -/
noncomputable def avg (θ : ι → ℝ) : ι → ℝ := fun _ => (∑ d, θ d) / Fintype.card ι

theorem avg_eq_sum_smul (θ : ι → ℝ) :
    (∑ σ : Equiv.Perm ι, (Fintype.card (Equiv.Perm ι) : ℝ)⁻¹ • (fun c => θ (σ c))) = avg θ := by
  funext c
  rw [Finset.sum_apply]
  simp only [Pi.smul_apply, smul_eq_mul]
  rw [← Finset.mul_sum, perm_average_policy θ c]
  rfl

/-- The uniform average of a policy in a convex, relabeling-invariant set lies in the set. -/
theorem avg_mem (S : Set (ι → ℝ)) (hS : Convex ℝ S) (θ : ι → ℝ)
    (hθ : ∀ σ : Equiv.Perm ι, (fun c => θ (σ c)) ∈ S) : avg θ ∈ S := by
  have hP : (0 : ℝ) < Fintype.card (Equiv.Perm ι) := by exact_mod_cast Fintype.card_pos
  have hw0 : ∀ σ ∈ (Finset.univ : Finset (Equiv.Perm ι)), (0 : ℝ) ≤ (Fintype.card (Equiv.Perm ι) : ℝ)⁻¹ :=
    fun _ _ => inv_nonneg.mpr hP.le
  have hw1 : ∑ σ ∈ (Finset.univ : Finset (Equiv.Perm ι)), (Fintype.card (Equiv.Perm ι) : ℝ)⁻¹ = 1 := by
    simp [Finset.sum_const, Finset.card_univ, nsmul_eq_mul, hP.ne']
  have h := hS.sum_mem hw0 hw1 (fun σ _ => hθ σ)
  rw [avg_eq_sum_smul] at h
  exact h

/-- Part (i) on a set of policies: a cost convex on `S` (for example `[0,1]^K`, where `PublicationRevision10.lean`
needs convexity on all of `ℝ^K`) and invariant to relabeling costs at most `C θ` at the uniform average. -/
theorem minimax_uniform_cost_on (S : Set (ι → ℝ)) (θ : ι → ℝ) (C : (ι → ℝ) → ℝ)
    (hC : ConvexOn ℝ S C) (hS : ∀ σ : Equiv.Perm ι, (fun c => θ (σ c)) ∈ S)
    (hinv : ∀ σ : Equiv.Perm ι, C (fun c => θ (σ c)) = C θ) :
    C (avg θ) ≤ C θ := by
  have hP : (0 : ℝ) < Fintype.card (Equiv.Perm ι) := by exact_mod_cast Fintype.card_pos
  have hw0 : ∀ σ ∈ (Finset.univ : Finset (Equiv.Perm ι)), (0 : ℝ) ≤ (Fintype.card (Equiv.Perm ι) : ℝ)⁻¹ :=
    fun _ _ => inv_nonneg.mpr hP.le
  have hw1 : ∑ σ ∈ (Finset.univ : Finset (Equiv.Perm ι)), (Fintype.card (Equiv.Perm ι) : ℝ)⁻¹ = 1 := by
    simp [Finset.sum_const, Finset.card_univ, nsmul_eq_mul, hP.ne']
  have hle := hC.map_sum_le hw0 hw1 (fun σ _ => hS σ)
  rw [avg_eq_sum_smul] at hle
  calc C (avg θ) ≤ ∑ σ : Equiv.Perm ι, (Fintype.card (Equiv.Perm ι) : ℝ)⁻¹ • C (fun c => θ (σ c)) := hle
    _ = C θ := by
        simp only [smul_eq_mul, hinv]
        rw [← Finset.sum_mul, hw1, one_mul]

/-- **Theorem `n:minimax`(i) on a set of policies.** With a convex loss and a cost convex on `S` and unchanged by
relabeling, the uniform average does at least as well as `θ` against the worst labelling. -/
theorem minimax_uniform_on (S : Set (ι → ℝ)) (A : ℝ) (H θ : ι → ℝ) (L : ℝ → ℝ)
    (hL : ConvexOn ℝ Set.univ L) (C : (ι → ℝ) → ℝ) (hC : ConvexOn ℝ S C)
    (hS : ∀ σ : Equiv.Perm ι, (fun c => θ (σ c)) ∈ S)
    (hinv : ∀ σ : Equiv.Perm ι, C (fun c => θ (σ c)) = C θ) :
    L (A + (∑ c, θ c) / Fintype.card ι * ∑ d, H d) + C (avg θ) ≤
      Finset.univ.sup' Finset.univ_nonempty (fun σ : Equiv.Perm ι => L (budget A H θ σ)) + C θ :=
  add_le_add (minimax_uniform_worst A H θ L hL) (minimax_uniform_cost_on S θ C hC hS hinv)

/-- A cost strictly convex on `S` and invariant to relabeling: a non-uniform policy costs strictly more than its
uniform average. -/
theorem minimax_uniform_cost_strict (S : Set (ι → ℝ)) (θ : ι → ℝ) (C : (ι → ℝ) → ℝ)
    (hC : StrictConvexOn ℝ S C) (hS : ∀ σ : Equiv.Perm ι, (fun c => θ (σ c)) ∈ S)
    (hinv : ∀ σ : Equiv.Perm ι, C (fun c => θ (σ c)) = C θ) (hnu : ∃ c c', θ c ≠ θ c') :
    C (avg θ) < C θ := by
  obtain ⟨c, c', hne⟩ := hnu
  have hP : (0 : ℝ) < Fintype.card (Equiv.Perm ι) := by exact_mod_cast Fintype.card_pos
  have hw0 : ∀ σ ∈ (Finset.univ : Finset (Equiv.Perm ι)), (0 : ℝ) < (Fintype.card (Equiv.Perm ι) : ℝ)⁻¹ :=
    fun _ _ => inv_pos.mpr hP
  have hw1 : ∑ σ ∈ (Finset.univ : Finset (Equiv.Perm ι)), (Fintype.card (Equiv.Perm ι) : ℝ)⁻¹ = 1 := by
    simp [Finset.sum_const, Finset.card_univ, nsmul_eq_mul, hP.ne']
  have hdiff : (fun x => θ ((Equiv.refl ι) x)) ≠ (fun x => θ ((Equiv.swap c c') x)) := by
    intro h
    have h' := congrFun h c
    simp only [Equiv.refl_apply, Equiv.swap_apply_left] at h'
    exact hne h'
  have hlt := hC.map_sum_lt hw0 hw1 (fun σ _ => hS σ)
    ⟨Equiv.refl ι, Finset.mem_univ _, Equiv.swap c c', Finset.mem_univ _, hdiff⟩
  rw [avg_eq_sum_smul] at hlt
  calc C (avg θ) < ∑ σ : Equiv.Perm ι, (Fintype.card (Equiv.Perm ι) : ℝ)⁻¹ • C (fun c => θ (σ c)) := hlt
    _ = C θ := by
        simp only [smul_eq_mul, hinv]
        rw [← Finset.sum_mul, hw1, one_mul]

/-- Theorem `n:minimax`(ii), strict part: against the worst labelling, the uniform average of a non-uniform policy
does strictly better than the policy. -/
theorem minimax_uniform_strict (S : Set (ι → ℝ)) (A : ℝ) (H θ : ι → ℝ) (L : ℝ → ℝ)
    (hL : ConvexOn ℝ Set.univ L) (C : (ι → ℝ) → ℝ) (hC : StrictConvexOn ℝ S C)
    (hS : ∀ σ : Equiv.Perm ι, (fun c => θ (σ c)) ∈ S)
    (hinv : ∀ σ : Equiv.Perm ι, C (fun c => θ (σ c)) = C θ) (hnu : ∃ c c', θ c ≠ θ c') :
    L (A + (∑ c, θ c) / Fintype.card ι * ∑ d, H d) + C (avg θ) <
      Finset.univ.sup' Finset.univ_nonempty (fun σ : Equiv.Perm ι => L (budget A H θ σ)) + C θ :=
  add_lt_add_of_le_of_lt (minimax_uniform_worst A H θ L hL) (minimax_uniform_cost_strict S θ C hC hS hinv hnu)

/-- The minimax objective: the worst loss over labellings plus the cost. -/
noncomputable def objective (A : ℝ) (H : ι → ℝ) (L : ℝ → ℝ) (C : (ι → ℝ) → ℝ) (θ : ι → ℝ) : ℝ :=
  Finset.univ.sup' Finset.univ_nonempty (fun σ : Equiv.Perm ι => L (budget A H θ σ)) + C θ

theorem objective_uniform (A : ℝ) (H : ι → ℝ) (L : ℝ → ℝ) (C : (ι → ℝ) → ℝ) (t : ℝ) :
    objective A H L C (fun _ => t) = L (A + t * ∑ d, H d) + C (fun _ => t) := by
  unfold objective
  simp only [uniform_budget_label_free]
  rw [Finset.sup'_const]

theorem objective_avg (A : ℝ) (H : ι → ℝ) (L : ℝ → ℝ) (C : (ι → ℝ) → ℝ) (θ : ι → ℝ) :
    objective A H L C (avg θ) = L (A + (∑ c, θ c) / Fintype.card ι * ∑ d, H d) + C (avg θ) := by
  unfold avg
  exact objective_uniform A H L C _

/-- Every minimax policy over a convex, relabeling-invariant set is uniform. -/
theorem minimax_policy_uniform (S : Set (ι → ℝ)) (hSconv : Convex ℝ S) (A : ℝ) (H : ι → ℝ) (L : ℝ → ℝ)
    (C : (ι → ℝ) → ℝ) (hL : ConvexOn ℝ Set.univ L) (hC : StrictConvexOn ℝ S C)
    (hSperm : ∀ θ ∈ S, ∀ σ : Equiv.Perm ι, (fun c => θ (σ c)) ∈ S)
    (hinv : ∀ θ : ι → ℝ, ∀ σ : Equiv.Perm ι, C (fun c => θ (σ c)) = C θ)
    (θ : ι → ℝ) (hθ : θ ∈ S) (hopt : ∀ φ ∈ S, objective A H L C θ ≤ objective A H L C φ) :
    ∀ c c', θ c = θ c' := by
  by_contra h
  simp only [not_forall] at h
  obtain ⟨c, c', hne⟩ := h
  have hlt := minimax_uniform_strict S A H θ L hL C hC (hSperm θ hθ) (hinv θ) ⟨c, c', hne⟩
  have h1 := hopt (avg θ) (avg_mem S hSconv θ (hSperm θ hθ))
  rw [objective_avg] at h1
  unfold objective at h1
  linarith

/-- Along uniform policies the minimax objective is strictly convex. -/
theorem diag_strict (S : Set (ι → ℝ)) (hSconv : Convex ℝ S) (A : ℝ) (H : ι → ℝ) (L : ℝ → ℝ)
    (C : (ι → ℝ) → ℝ) (hL : ConvexOn ℝ Set.univ L) (hC : StrictConvexOn ℝ S C) :
    StrictConvexOn ℝ {t : ℝ | (fun _ : ι => t) ∈ S} (fun t => L (A + t * ∑ d, H d) + C (fun _ => t)) := by
  obtain ⟨c0⟩ := (inferInstance : Nonempty ι)
  refine ⟨?_, ?_⟩
  · intro x hx y hy a b ha hb hab
    have hx' : (fun _ : ι => x) ∈ S := hx
    have hy' : (fun _ : ι => y) ∈ S := hy
    have h := hSconv hx' hy' ha hb hab
    have e : (a • (fun _ : ι => x) + b • (fun _ : ι => y)) = (fun _ : ι => a • x + b • y) := by
      funext c
      simp
    show (fun _ : ι => a • x + b • y) ∈ S
    rw [← e]
    exact h
  · intro x hx y hy hxy a b ha hb hab
    have hx' : (fun _ : ι => x) ∈ S := hx
    have hy' : (fun _ : ι => y) ∈ S := hy
    have hne : (fun _ : ι => x) ≠ (fun _ : ι => y) := fun h => hxy (congrFun h c0)
    have hCs := hC.2 hx' hy' hne ha hb hab
    have e : (a • (fun _ : ι => x) + b • (fun _ : ι => y)) = (fun _ : ι => a • x + b • y) := by
      funext c
      simp
    rw [e] at hCs
    have hLc := hL.2 (Set.mem_univ (A + x * ∑ d, H d)) (Set.mem_univ (A + y * ∑ d, H d)) ha.le hb.le hab
    have e2 : a • (A + x * ∑ d, H d) + b • (A + y * ∑ d, H d) = A + (a • x + b • y) * ∑ d, H d := by
      simp only [smul_eq_mul]
      linear_combination A * hab
    rw [e2] at hLc
    show L (A + (a • x + b • y) * ∑ d, H d) + C (fun _ => a • x + b • y) <
      a • (L (A + x * ∑ d, H d) + C (fun _ => x)) + b • (L (A + y * ∑ d, H d) + C (fun _ => y))
    simp only [smul_eq_mul] at hCs hLc ⊢
    calc L (A + (a * x + b * y) * ∑ d, H d) + C (fun _ => a * x + b * y)
        < (a * L (A + x * ∑ d, H d) + b * L (A + y * ∑ d, H d)) + (a * C (fun _ => x) + b * C (fun _ => y)) :=
          add_lt_add_of_le_of_lt hLc hCs
      _ = a * (L (A + x * ∑ d, H d) + C (fun _ => x)) + b * (L (A + y * ∑ d, H d) + C (fun _ => y)) := by ring

/-- A strictly convex function on a set of reals has at most one minimizer there. -/
theorem strict_min_unique {T : Set ℝ} {g : ℝ → ℝ} (hg : StrictConvexOn ℝ T g) {t₁ t₂ : ℝ}
    (h1 : t₁ ∈ T) (h2 : t₂ ∈ T) (hopt1 : ∀ t ∈ T, g t₁ ≤ g t) (hopt2 : ∀ t ∈ T, g t₂ ≤ g t) : t₁ = t₂ := by
  by_contra hne
  have hm : (1 / 2 : ℝ) • t₁ + (1 / 2 : ℝ) • t₂ ∈ T := hg.1 h1 h2 (by norm_num) (by norm_num) (by norm_num)
  have hlt := hg.2 h1 h2 hne (by norm_num : (0 : ℝ) < 1 / 2) (by norm_num : (0 : ℝ) < 1 / 2) (by norm_num)
  have a1 := hopt1 _ hm
  have a2 := hopt1 t₂ h2
  have a3 := hopt2 t₁ h1
  simp only [smul_eq_mul] at hlt a1
  linarith

/-- **Theorem `n:minimax`(ii).** With a convex loss and a cost that is strictly convex on a convex,
relabeling-invariant set of policies and unchanged by relabeling, any two minimax policies in the set coincide, and
they are uniform. -/
theorem minimax_unique (S : Set (ι → ℝ)) (hSconv : Convex ℝ S) (A : ℝ) (H : ι → ℝ) (L : ℝ → ℝ)
    (C : (ι → ℝ) → ℝ) (hL : ConvexOn ℝ Set.univ L) (hC : StrictConvexOn ℝ S C)
    (hSperm : ∀ θ ∈ S, ∀ σ : Equiv.Perm ι, (fun c => θ (σ c)) ∈ S)
    (hinv : ∀ θ : ι → ℝ, ∀ σ : Equiv.Perm ι, C (fun c => θ (σ c)) = C θ)
    (θ₁ θ₂ : ι → ℝ) (h1 : θ₁ ∈ S) (h2 : θ₂ ∈ S)
    (hopt1 : ∀ φ ∈ S, objective A H L C θ₁ ≤ objective A H L C φ)
    (hopt2 : ∀ φ ∈ S, objective A H L C θ₂ ≤ objective A H L C φ) :
    θ₁ = θ₂ := by
  obtain ⟨c0⟩ := (inferInstance : Nonempty ι)
  have hu1 := minimax_policy_uniform S hSconv A H L C hL hC hSperm hinv θ₁ h1 hopt1
  have hu2 := minimax_policy_uniform S hSconv A H L C hL hC hSperm hinv θ₂ h2 hopt2
  obtain ⟨t₁, rfl⟩ : ∃ t : ℝ, θ₁ = fun _ => t := ⟨θ₁ c0, funext fun c => hu1 c c0⟩
  obtain ⟨t₂, rfl⟩ : ∃ t : ℝ, θ₂ = fun _ => t := ⟨θ₂ c0, funext fun c => hu2 c c0⟩
  have hopt1' : ∀ t ∈ {t : ℝ | (fun _ : ι => t) ∈ S},
      (fun t => L (A + t * ∑ d, H d) + C (fun _ => t)) t₁ ≤ (fun t => L (A + t * ∑ d, H d) + C (fun _ => t)) t := by
    intro t ht
    have h := hopt1 (fun _ => t) ht
    rw [objective_uniform, objective_uniform] at h
    exact h
  have hopt2' : ∀ t ∈ {t : ℝ | (fun _ : ι => t) ∈ S},
      (fun t => L (A + t * ∑ d, H d) + C (fun _ => t)) t₂ ≤ (fun t => L (A + t * ∑ d, H d) + C (fun _ => t)) t := by
    intro t ht
    have h := hopt2 (fun _ => t) ht
    rw [objective_uniform, objective_uniform] at h
    exact h
  have h1' : t₁ ∈ {t : ℝ | (fun _ : ι => t) ∈ S} := h1
  have h2' : t₂ ∈ {t : ℝ | (fun _ : ι => t) ∈ S} := h2
  have ht := strict_min_unique (diag_strict S hSconv A H L C hL hC) h1' h2' hopt1' hopt2'
  rw [ht]

end Paper1Revision12
