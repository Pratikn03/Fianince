import CurrentProofs.Paper1StressIdentification
import Mathlib.Data.Set.Finite.Basic
import Mathlib.Order.Interval.Set.Infinite
import Mathlib.Data.Finset.Max
import Mathlib.Tactic.LinearCombination
import Mathlib.Tactic.Positivity

/-!
# Paper 1 (core version), Theorem 7.4 in general form

A policy shape `ψ` has **independent dilations** (`IndepDilations ψ`) if, for any finite set of distinct positive
scales, `Σ_s w_s ψ(s u) = 0` for every `u` forces every weight to vanish.

* `p1_thm_stress_identification`: for any odd shape with independent dilations, any number of traders in each
  population, memory rates `≥ 0` and nonzero leverages, the following are equivalent:
  - every (probe, price path) pair of the first market is a (probe, price path) pair of the second;
  - the two signed capacity measures `Σ_i c_i sgn(l_i) δ_(r_i, |l_i|)` agree, tested against every function of
    memory and leverage.
* `p1_clip_indep_dilations`: the hard limit `clip(u) = max(-1, min(1, u))` has independent dilations, for any
  number of scales (each scale adds a kink at `1/s`; the largest scale is removed first).
* `p1_thm_stress_identification_hard_limit`: the theorem for the hard limit, with no hypothesis left on the shape.

* `p1_cubic_not_indep_dilations`: a cubic shape `u - γ u³` does **not** have independent dilations, so the property
  is a real restriction.

`tanh` has independent dilations too: see `Paper1StressIdentificationTanh.lean`.

What "identical responses" means here. `ProbePricePath a κ F v x` says that `x` is the price path of the market
with flow map `F` under probe `v`. The first statement above says the second market reproduces every such pair.
Uniqueness of the path given the probe is not used.
-/

namespace CurrentMM

open Finset

/-- Independent dilations: distinct positive scales of `ψ` are linearly independent as functions of `u`. -/
def IndepDilations (ψ : ℝ → ℝ) : Prop :=
  ∀ (T : Finset ℝ) (w : ℝ → ℝ), (∀ s ∈ T, 0 < s) →
    (∀ u : ℝ, ∑ s ∈ T, w s * ψ (s * u) = 0) → ∀ s ∈ T, w s = 0

/-- A direction `θ > 0` along which distinct atoms `(memory, leverage)` have distinct scales
`leverage * (memory * θ + 1)`. -/
theorem p1_exists_separating_direction (A : Finset (ℝ × ℝ)) (hA : ∀ a ∈ A, 0 < a.2) :
    ∃ θ : ℝ, 0 < θ ∧ ∀ a ∈ A, ∀ b ∈ A, a.2 * (a.1 * θ + 1) = b.2 * (b.1 * θ + 1) → a = b := by
  obtain ⟨θ, hθpos, hθB⟩ := (Set.Ioi_infinite (0 : ℝ)).exists_notMem_finset
    ((A ×ˢ A).image (fun p : (ℝ × ℝ) × (ℝ × ℝ) => (p.2.2 - p.1.2) / (p.1.2 * p.1.1 - p.2.2 * p.2.1)))
  refine ⟨θ, hθpos, ?_⟩
  intro a ha b hb hab
  have key : (a.2 * a.1 - b.2 * b.1) * θ = b.2 - a.2 := by linear_combination hab
  by_cases hc : a.2 * a.1 - b.2 * b.1 = 0
  · have h2 : a.2 = b.2 := by
      rw [hc, zero_mul] at key
      linarith
    have hb2 : 0 < b.2 := hA b hb
    have h1 : a.1 = b.1 := by
      have hz : b.2 * (a.1 - b.1) = 0 := by
        rw [h2] at hc
        linear_combination hc
      rcases mul_eq_zero.mp hz with h | h
      · exact absurd h hb2.ne'
      · linarith
    exact Prod.ext h1 h2
  · exfalso
    apply hθB
    have hθ : θ = (b.2 - a.2) / (a.2 * a.1 - b.2 * b.1) := by
      rw [eq_div_iff hc]
      linear_combination key
    exact mem_image.mpr ⟨(a, b), mem_product.mpr ⟨ha, hb⟩, hθ.symm⟩

/-- Grouping a sum over traders by atom `(memory, leverage)`. -/
theorem p1_sum_fiberwise_atoms {ι : Type} [Fintype ι] (d ρ lam : ι → ℝ) (f : ℝ × ℝ → ℝ) :
    ∑ k, d k * f (ρ k, lam k) =
      ∑ a ∈ univ.image (fun k => (ρ k, lam k)),
        (∑ k ∈ univ.filter (fun k => (ρ k, lam k) = a), d k) * f a := by
  refine (Finset.sum_fiberwise_of_maps_to (s := univ) (t := univ.image (fun k => (ρ k, lam k)))
    (g := fun k => (ρ k, lam k)) (fun x _ => mem_image_of_mem _ (mem_univ x))
    (fun k => d k * f (ρ k, lam k))).symm.trans ?_
  refine sum_congr rfl fun a _ => ?_
  rw [sum_mul]
  refine sum_congr rfl fun k hk => ?_
  rw [(mem_filter.mp hk).2]

/-- Weights on distinct atoms vanish if the two-date flow map vanishes in every direction. -/
theorem p1_atoms_zero_of_dilations (ψ : ℝ → ℝ) (hψ : IndepDilations ψ) (A : Finset (ℝ × ℝ)) (W : ℝ × ℝ → ℝ)
    (hA1 : ∀ a ∈ A, 0 ≤ a.1) (hA2 : ∀ a ∈ A, 0 < a.2)
    (h : ∀ θ u : ℝ, ∑ a ∈ A, W a * ψ (a.2 * (a.1 * θ + 1) * u) = 0) :
    ∀ a ∈ A, W a = 0 := by
  obtain ⟨θ, hθ, hinj⟩ := p1_exists_separating_direction A hA2
  have hSpos : ∀ a ∈ A, 0 < a.2 * (a.1 * θ + 1) := fun a ha =>
    mul_pos (hA2 a ha) (add_pos_of_nonneg_of_pos (mul_nonneg (hA1 a ha) hθ.le) one_pos)
  have hw : ∀ a ∈ A,
      (∑ b ∈ A, if b.2 * (b.1 * θ + 1) = a.2 * (a.1 * θ + 1) then W b else 0) = W a := by
    intro a ha
    rw [Finset.sum_eq_single a]
    · rw [if_pos rfl]
    · intro b hb hba
      rw [if_neg]
      intro hEq
      exact hba (hinj b hb a ha hEq)
    · intro hna
      exact absurd ha hna
  have key := hψ (A.image fun a : ℝ × ℝ => a.2 * (a.1 * θ + 1))
    (fun s => ∑ b ∈ A, if b.2 * (b.1 * θ + 1) = s then W b else 0)
    (by
      intro s hs
      obtain ⟨a, ha, rfl⟩ := mem_image.mp hs
      exact hSpos a ha)
    (by
      intro u
      show ∑ s ∈ A.image (fun a : ℝ × ℝ => a.2 * (a.1 * θ + 1)),
        (∑ b ∈ A, if b.2 * (b.1 * θ + 1) = s then W b else 0) * ψ (s * u) = 0
      rw [Finset.sum_image (fun a ha b hb hab => hinj a ha b hb hab)]
      exact (sum_congr rfl fun a ha => by rw [hw a ha]).trans (h θ u))
  intro a ha
  have h0 : (∑ b ∈ A, if b.2 * (b.1 * θ + 1) = a.2 * (a.1 * θ + 1) then W b else 0) = 0 :=
    key _ (mem_image_of_mem _ ha)
  rw [hw a ha] at h0
  exact h0

/-- **Core identification step.** A signed population whose two-date flow map vanishes in every direction has zero
net weight on every atom, so it integrates every function of (memory, leverage) to zero. -/
theorem p1_dilation_identification {ι : Type} [Fintype ι] (ψ : ℝ → ℝ) (hψ : IndepDilations ψ)
    (d ρ lam : ι → ℝ) (hρ : ∀ k, 0 ≤ ρ k) (hlam : ∀ k, 0 < lam k)
    (h : ∀ θ u : ℝ, ∑ k, d k * ψ (lam k * (ρ k * θ + 1) * u) = 0) (g : ℝ → ℝ → ℝ) :
    ∑ k, d k * g (ρ k) (lam k) = 0 := by
  have hz := p1_atoms_zero_of_dilations ψ hψ (univ.image fun k => (ρ k, lam k))
    (fun a => ∑ k ∈ univ.filter (fun k => (ρ k, lam k) = a), d k)
    (by
      intro a ha
      obtain ⟨k, -, rfl⟩ := mem_image.mp ha
      exact hρ k)
    (by
      intro a ha
      obtain ⟨k, -, rfl⟩ := mem_image.mp ha
      exact hlam k)
    (by
      intro θ u
      exact (p1_sum_fiberwise_atoms d ρ lam (fun a => ψ (a.2 * (a.1 * θ + 1) * u))).symm.trans (h θ u))
  refine (p1_sum_fiberwise_atoms d ρ lam (fun a => g a.1 a.2)).trans ?_
  refine sum_eq_zero fun a ha => ?_
  have e : (∑ k ∈ univ.filter (fun k => (ρ k, lam k) = a), d k) = 0 := hz a ha
  rw [e, zero_mul]

/-- **Theorem 7.4, general form.** For an odd shape with independent dilations, the second market reproduces every
(probe, price path) pair of the first if and only if the signed capacity measures agree. -/
theorem p1_thm_stress_identification {K K' : ℕ} (ψ : ℝ → ℝ) (hodd : IsOddPolicy ψ) (hind : IndepDilations ψ)
    (a κ : ℝ) (hκ : κ ≠ 0) (c l r : Fin K → ℝ) (c' l' r' : Fin K' → ℝ)
    (hr : ∀ i, 0 ≤ r i) (hr' : ∀ j, 0 ≤ r' j) (hl : ∀ i, l i ≠ 0) (hl' : ∀ j, l' j ≠ 0) :
    (∀ v x, ProbePricePath a κ (satAggFlow ψ c l r) v x → ProbePricePath a κ (satAggFlow ψ c' l' r') v x) ↔
      (∀ g : ℝ → ℝ → ℝ, ∑ i, (c i * realSgn (l i)) * g (r i) (|l i|) =
        ∑ j, (c' j * realSgn (l' j)) * g (r' j) (|l' j|)) := by
  constructor
  · intro H g
    -- flows agree on every path
    have hFF : ∀ (x : ℕ → ℝ) (t : ℕ), satAggFlow ψ c l r x t = satAggFlow ψ c' l' r' x t := by
      intro x
      have hp := p1_probe_steer_target a κ (satAggFlow ψ c l r) x hκ
      exact p1_probe_flow_recovery_eq a κ _ _ _ x hp (H _ x hp) hκ
    -- the two-date flow map of the signed difference vanishes
    have hvanish : ∀ θ u : ℝ, ∑ k : Fin K ⊕ Fin K',
        Sum.elim (fun i => c i * realSgn (l i)) (fun j => -(c' j * realSgn (l' j))) k *
          ψ (Sum.elim (fun i => |l i|) (fun j => |l' j|) k * (Sum.elim r r' k * θ + 1) * u) = 0 := by
      intro θ u
      have hs0 : (fun j : ℕ => if j = 0 then θ * u else u) 0 = θ * u := if_pos rfl
      have hs1 : (fun j : ℕ => if j = 0 then θ * u else u) 1 = u := if_neg Nat.one_ne_zero
      have e : ∀ ρ : ℝ, eqMem ρ (fun j : ℕ => if j = 0 then θ * u else u) 2 = (ρ * θ + 1) * u := by
        intro ρ
        have h2 : eqMem ρ (fun j : ℕ => if j = 0 then θ * u else u) 2 =
            ρ * (ρ * 0 + (fun j : ℕ => if j = 0 then θ * u else u) 0) +
              (fun j : ℕ => if j = 0 then θ * u else u) 1 := rfl
        rw [h2, hs0, hs1]
        ring
      have hflow := hFF (fun j : ℕ => if j = 0 then θ * u else u) 2
      unfold satAggFlow at hflow
      simp only [e] at hflow
      have t1 : ∀ i, c i * realSgn (l i) * ψ (|l i| * (r i * θ + 1) * u) =
          c i * ψ (l i * ((r i * θ + 1) * u)) := fun i => by
        rw [mul_assoc (|l i|) (r i * θ + 1) u]
        exact (p1_odd_policy_decomp ψ hodd (c i) (l i) ((r i * θ + 1) * u)).symm
      have t2 : ∀ j, -(c' j * realSgn (l' j)) * ψ (|l' j| * (r' j * θ + 1) * u) =
          -(c' j * ψ (l' j * ((r' j * θ + 1) * u))) := fun j => by
        rw [neg_mul, mul_assoc (|l' j|) (r' j * θ + 1) u]
        exact congrArg Neg.neg (p1_odd_policy_decomp ψ hodd (c' j) (l' j) ((r' j * θ + 1) * u)).symm
      rw [Fintype.sum_sum_type]
      simp only [Sum.elim_inl, Sum.elim_inr]
      rw [sum_congr rfl (fun i _ => t1 i), sum_congr rfl (fun j _ => t2 j), sum_neg_distrib, hflow]
      exact add_neg_cancel _
    have Z := p1_dilation_identification ψ hind
      (Sum.elim (fun i => c i * realSgn (l i)) (fun j => -(c' j * realSgn (l' j))))
      (Sum.elim r r') (Sum.elim (fun i => |l i|) (fun j => |l' j|))
      (fun k => match k with
        | Sum.inl i => hr i
        | Sum.inr j => hr' j)
      (fun k => match k with
        | Sum.inl i => abs_pos.mpr (hl i)
        | Sum.inr j => abs_pos.mpr (hl' j))
      hvanish g
    rw [Fintype.sum_sum_type] at Z
    simp only [Sum.elim_inl, Sum.elim_inr, neg_mul, sum_neg_distrib] at Z
    linarith
  · intro hμ v x hp
    have hF : ∀ t, satAggFlow ψ c' l' r' x t = satAggFlow ψ c l r x t := fun t =>
      (p1_sat_signed_capacity_sufficiency ψ hodd c l r c' l' r' hμ x t).symm
    unfold ProbePricePath at hp ⊢
    refine ⟨?_, fun t => ?_⟩
    · rw [hF 0]
      exact hp.1
    · rw [hF (t + 1)]
      exact hp.2 t

/-- The hard limit. -/
noncomputable def clipPolicy (u : ℝ) : ℝ := max (-1) (min 1 u)

theorem clipPolicy_of_band {y : ℝ} (hlo : -1 ≤ y) (hhi : y ≤ 1) : clipPolicy y = y :=
  p1_clip_in_band y hlo hhi

theorem clipPolicy_of_ge {y : ℝ} (h : 1 ≤ y) : clipPolicy y = 1 := by
  unfold clipPolicy
  rw [min_eq_left h]
  exact max_eq_right (by norm_num)

theorem clipPolicy_of_le {y : ℝ} (h : y ≤ -1) : clipPolicy y = -1 := by
  unfold clipPolicy
  rw [min_eq_right (by linarith)]
  exact max_eq_left h

/-- The hard limit is odd. -/
theorem p1_clipPolicy_odd : IsOddPolicy clipPolicy := by
  intro u
  rcases le_total u (-1) with h1 | h1
  · rw [clipPolicy_of_le h1, clipPolicy_of_ge (by linarith)]
    norm_num
  · rcases le_total u 1 with h2 | h2
    · rw [clipPolicy_of_band h1 h2, clipPolicy_of_band (by linarith) (by linarith)]
    · rw [clipPolicy_of_ge h2, clipPolicy_of_le (by linarith)]

/-- **The hard limit has independent dilations**, for any number of scales. -/
theorem p1_clip_indep_dilations : IndepDilations clipPolicy := by
  intro T
  induction T using Finset.induction_on_max with
  | empty =>
    intro w _ _ s hs
    exact absurd hs (Finset.notMem_empty s)
  | insert a S ha ih =>
    intro w hpos hsum s hs
    have ha_pos : 0 < a := hpos a (mem_insert_self a S)
    have haS : a ∉ S := fun h => lt_irrefl a (ha a h)
    have hSpos : ∀ x ∈ S, 0 < x := fun x hx => hpos x (mem_insert_of_mem hx)
    have hwa : w a = 0 := by
      have ha1 : 1 / a * a = 1 := by rw [one_div, inv_mul_cancel₀ ha_pos.ne']
      have hA := hsum (1 / a)
      rw [sum_insert haS] at hA
      have e1 : clipPolicy (a * (1 / a)) = 1 := by
        rw [mul_one_div_cancel ha_pos.ne']
        exact clipPolicy_of_ge le_rfl
      have e2 : ∀ x ∈ S, w x * clipPolicy (x * (1 / a)) = w x * x * (1 / a) := by
        intro x hx
        have hxa : x < a := ha x hx
        have hx0 : 0 < x := hSpos x hx
        have hb : x * (1 / a) ≤ 1 := by
          rw [mul_one_div, div_le_one ha_pos]
          exact hxa.le
        have hb0 : 0 ≤ x * (1 / a) := mul_nonneg hx0.le (by positivity)
        rw [clipPolicy_of_band (by linarith) hb]
        ring
      rw [e1, sum_congr rfl e2, ← sum_mul, mul_one] at hA
      rcases S.eq_empty_or_nonempty with hS | hS
      · rw [hS, sum_empty, zero_mul, add_zero] at hA
        exact hA
      · have hmS : S.max' hS ∈ S := S.max'_mem hS
        have hm_pos : 0 < S.max' hS := hSpos _ hmS
        have hma : S.max' hS < a := ha _ hmS
        have hm1 : 1 / S.max' hS * S.max' hS = 1 := by rw [one_div, inv_mul_cancel₀ hm_pos.ne']
        have hB := hsum (1 / S.max' hS)
        rw [sum_insert haS] at hB
        have f1 : clipPolicy (a * (1 / S.max' hS)) = 1 := by
          refine clipPolicy_of_ge ?_
          rw [mul_one_div, le_div_iff₀ hm_pos]
          linarith
        have f2 : ∀ x ∈ S, w x * clipPolicy (x * (1 / S.max' hS)) = w x * x * (1 / S.max' hS) := by
          intro x hx
          have hxm : x ≤ S.max' hS := S.le_max' x hx
          have hx0 : 0 < x := hSpos x hx
          have hb : x * (1 / S.max' hS) ≤ 1 := by
            rw [mul_one_div, div_le_one hm_pos]
            exact hxm
          have hb0 : 0 ≤ x * (1 / S.max' hS) := mul_nonneg hx0.le (by positivity)
          rw [clipPolicy_of_band (by linarith) hb]
          ring
        rw [f1, sum_congr rfl f2, ← sum_mul, mul_one] at hB
        have hSsum : (∑ x ∈ S, w x * x) = -(w a) * a := by
          linear_combination a * hA - (∑ x ∈ S, w x * x) * ha1
        rw [hSsum] at hB
        have hprod : w a * (S.max' hS - a) = 0 := by
          linear_combination (S.max' hS) * hB + (w a * a) * hm1
        rcases mul_eq_zero.mp hprod with h | h
        · exact h
        · exfalso
          linarith
    rcases mem_insert.mp hs with rfl | hsS
    · exact hwa
    · refine ih w hSpos (fun u => ?_) s hsS
      have h := hsum u
      rw [sum_insert haS, hwa, zero_mul, zero_add] at h
      exact h

/-- **Theorem 7.4 for the hard limit**, any number of traders. -/
theorem p1_thm_stress_identification_hard_limit {K K' : ℕ} (a κ : ℝ) (hκ : κ ≠ 0)
    (c l r : Fin K → ℝ) (c' l' r' : Fin K' → ℝ)
    (hr : ∀ i, 0 ≤ r i) (hr' : ∀ j, 0 ≤ r' j) (hl : ∀ i, l i ≠ 0) (hl' : ∀ j, l' j ≠ 0) :
    (∀ v x, ProbePricePath a κ (satAggFlow clipPolicy c l r) v x →
        ProbePricePath a κ (satAggFlow clipPolicy c' l' r') v x) ↔
      (∀ g : ℝ → ℝ → ℝ, ∑ i, (c i * realSgn (l i)) * g (r i) (|l i|) =
        ∑ j, (c' j * realSgn (l' j)) * g (r' j) (|l' j|)) :=
  p1_thm_stress_identification clipPolicy p1_clipPolicy_odd p1_clip_indep_dilations a κ hκ c l r c' l' r'
    hr hr' hl hl'

/-- **The property can fail.** For the cubic shape `u - γ u³`, the scales `1, 2, 3` with weights `5, -4, 1` give
`Σ w_s ψ(s u) = 0` for every `u`. So a cubic policy does not have independent dilations: beyond the first and third
leverage moments, probes cannot separate such traders. -/
theorem p1_cubic_not_indep_dilations (γ : ℝ) : ¬ IndepDilations (cubicPolicy γ) := by
  intro h
  have hz := h {1, 2, 3} (fun s => if s = 1 then 5 else if s = 2 then -4 else 1)
    (by
      intro s hs
      simp only [mem_insert, mem_singleton] at hs
      rcases hs with rfl | rfl | rfl <;> norm_num)
    (by
      intro u
      rw [sum_insert (by norm_num), sum_insert (by norm_num), sum_singleton]
      unfold cubicPolicy
      norm_num
      ring)
    1 (by simp)
  norm_num at hz

end CurrentMM
