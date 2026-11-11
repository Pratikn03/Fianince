import Mathlib.Basic.Real.Basic
import Mathlib.Data.Set.Finite.Basic
import Mathlib.Data.Finset.Lattice.Fold
import Mathlib.Tactic.Push
import Mathlib.Tactic.Choose

/-!
# Paper 1: the targeted halt for every K (counting step)

Supplement, "The targeted halt for every K". The paper proves on paper that
* the weights of a `K`-node rule that is exact to degree `2K-2` are the values of one function
  `lam` at its nodes,
* a point is a node of at most one rule of the family, and
* `lam` has finite level sets (its reciprocal is a non-constant polynomial).

This file checks only the counting step that follows: for an infinite family of pairwise disjoint
node sets and a function with finite level sets, the largest value over the node set is not the
same for every member of the family. The three analytic facts above are hypotheses here.
-/

namespace CurrentMM

/-- An infinite family of pairwise disjoint finite node sets, and a function with finite level
sets: two members of the family have different largest values. -/
theorem p1_largest_value_not_constant {ι : Type*} (I : Set ι) (hI : I.Infinite)
    (N : ι → Finset ℝ) (hne : ∀ c ∈ I, (N c).Nonempty)
    (hdisj : ∀ c ∈ I, ∀ d ∈ I, c ≠ d → Disjoint (N c) (N d))
    (f : ℝ → ℝ) (hfin : ∀ v : ℝ, {s : ℝ | f s = v}.Finite) :
    ∃ c ∈ I, ∃ d ∈ I, ∃ (hc : (N c).Nonempty) (hd : (N d).Nonempty),
      (N c).sup' hc f ≠ (N d).sup' hd f := by
  by_contra hcon
  push Not at hcon
  obtain ⟨c0, hc0⟩ := hI.nonempty
  have key : ∀ c ∈ I, ∃ s ∈ N c, f s = (N c0).sup' (hne c0 hc0) f := by
    intro c hc
    obtain ⟨s, hs, hsv⟩ := Finset.exists_mem_eq_sup' (hne c hc) f
    exact ⟨s, hs, by rw [← hsv]; exact hcon c hc c0 hc0 (hne c hc) (hne c0 hc0)⟩
  choose! g hg using key
  have hmaps : Set.MapsTo g I {s | f s = (N c0).sup' (hne c0 hc0) f} := fun c hc => (hg c hc).2
  have hinj : Set.InjOn g I := by
    intro c hc d hd hcd
    by_contra hcd'
    have hnot := Finset.disjoint_left.mp (hdisj c hc d hd hcd') (hg c hc).1
    exact hnot (hcd ▸ (hg d hd).1)
  exact hI (Set.Finite.of_injOn hmaps hinj (hfin _))

/-- The same statement for the largest weight of quadrature rules: `w c i = lam (node c i)` for
every node, so the largest weight of rule `c` is the largest value of `lam` over its nodes. -/
theorem p1_largest_weight_not_constant {ι : Type*} (I : Set ι) (hI : I.Infinite)
    (N : ι → Finset ℝ) (hne : ∀ c ∈ I, (N c).Nonempty)
    (hdisj : ∀ c ∈ I, ∀ d ∈ I, c ≠ d → Disjoint (N c) (N d))
    (lam : ℝ → ℝ) (hfin : ∀ v : ℝ, {s : ℝ | lam s = v}.Finite)
    (w : ι → ℝ → ℝ) (hw : ∀ c ∈ I, ∀ s ∈ N c, w c s = lam s) :
    ∃ c ∈ I, ∃ d ∈ I, ∃ (hc : (N c).Nonempty) (hd : (N d).Nonempty),
      (N c).sup' hc (w c) ≠ (N d).sup' hd (w d) := by
  obtain ⟨c, hc, d, hd, hcn, hdn, hneq⟩ := p1_largest_value_not_constant I hI N hne hdisj lam hfin
  refine ⟨c, hc, d, hd, hcn, hdn, ?_⟩
  have e1 : (N c).sup' hcn (w c) = (N c).sup' hcn lam := Finset.sup'_congr hcn rfl (hw c hc)
  have e2 : (N d).sup' hdn (w d) = (N d).sup' hdn lam := Finset.sup'_congr hdn rfl (hw d hd)
  rw [e1, e2]; exact hneq

end CurrentMM
