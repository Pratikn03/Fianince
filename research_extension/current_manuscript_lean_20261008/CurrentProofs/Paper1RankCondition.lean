import CurrentProofs.Paper1PoolingUpper

/-!
# Paper 1: the rank condition (R) of `thm:pool` for every `K` and `D`

* `p1_hermite_partial`: if `p ↦ ∑_i (d_i p(s_i) + e_i p'(s_i))`, with `e` supported on a set `G` of nodes, kills every
  monomial of degree below `N ≥ K + |G|`, then `d = e = 0` (Hermite interpolation with mixed multiplicities).
* `p1_rank_condition_witness`: at the configuration in which market `j` has weight `1` on the algorithms of a group
  `G_j` and `0` elsewhere, with distinct nodes and `K + |G_j| ≤ l + 1` for every market, the differential of the
  pooled moment map up to order `l` is injective. With groups of size at most `⌈K/D⌉` (for example `g(i) = i mod D`)
  this is order `l* = K + ⌈K/D⌉ - 1`, so condition (R) holds at one configuration for every `K` and `D`, hence
  outside a proper algebraic set (the paper's genericity step).
* `p1_mod_groups_small`: the groups `g(i) = i mod D` have at most `⌈K/D⌉` members.
-/

namespace CurrentMM

open Finset Polynomial

/-- **Hermite interpolation with mixed multiplicities.** -/
theorem p1_hermite_partial {K : ℕ} (s d e : Fin K → ℝ) (G : Finset (Fin K)) (hs : Function.Injective s)
    (he : ∀ i, i ∉ G → e i = 0) (N : ℕ) (hN : K + G.card ≤ N)
    (h : ∀ m : ℕ, m < N → ∑ i, (d i * s i ^ m + e i * ((m : ℝ) * s i ^ (m - 1))) = 0) :
    e = 0 ∧ d = 0 := by
  classical
  set Λ : ℝ[X] → ℝ := fun p => ∑ i, (d i * p.eval (s i) + e i * (derivative p).eval (s i)) with hΛdef
  set T : ℕ → ℝ := fun m => ∑ i, (d i * s i ^ m + e i * ((m : ℝ) * s i ^ (m - 1))) with hTdef
  have hgen : ∀ (n : ℕ) (c : ℕ → ℝ), Λ (∑ m ∈ range n, C (c m) * X ^ m) = ∑ m ∈ range n, c m * T m := by
    intro n c
    simp only [hΛdef, hTdef, eval_finsetSum, derivative_sum, derivative_C_mul_X_pow, eval_C_mul, eval_pow,
      eval_X, mul_sum, ← sum_add_distrib]
    rw [sum_comm]
    refine sum_congr rfl (fun m _ => sum_congr rfl (fun i _ => by ring))
  have hΛ : ∀ p : ℝ[X], p.natDegree < N → Λ p = 0 := by
    intro p hp
    have e0 := hgen (p.natDegree + 1) p.coeff
    rw [← p.as_sum_range_C_mul_X_pow] at e0
    rw [e0]
    refine sum_eq_zero (fun m hm => ?_)
    rw [show T m = 0 from h m (by have := mem_range.mp hm; omega), mul_zero]
  set mult : Fin K → ℕ := fun j => if j ∈ G then 2 else 1 with hmult
  set q : Fin K → ℝ[X] := fun i => ∏ j ∈ univ.erase i, (X - C (s j)) ^ mult j with hqdef
  have hq_eval_ne : ∀ i, (q i).eval (s i) ≠ 0 := by
    intro i
    simp only [hqdef, eval_prod, eval_pow, eval_sub, eval_X, eval_C]
    refine prod_ne_zero_iff.mpr (fun j hj => pow_ne_zero _ (sub_ne_zero.mpr ?_))
    intro hij; exact (mem_erase.mp hj).1 (hs hij).symm
  have hq_split : ∀ i j, j ≠ i → ∃ r : ℝ[X], q i = (X - C (s j)) ^ mult j * r := by
    intro i j hji
    exact ⟨_, (mul_prod_erase (univ.erase i) (fun k => (X - C (s k)) ^ mult k)
      (mem_erase.mpr ⟨hji, mem_univ j⟩)).symm⟩
  have htot : ∑ j : Fin K, mult j = K + G.card := by
    have : ∀ j, mult j = 1 + (if j ∈ G then 1 else 0) := fun j => by
      simp only [hmult]; split_ifs <;> rfl
    simp only [this, sum_add_distrib, sum_const, card_univ, Fintype.card_fin, smul_eq_mul, mul_one]
    rw [sum_boole]; simp
  have hq_deg : ∀ i, (q i).natDegree + mult i ≤ K + G.card := by
    intro i
    have h1 : (q i).natDegree ≤ ∑ j ∈ univ.erase i, mult j := by
      refine (natDegree_prod_le _ _).trans (sum_le_sum fun j _ => ?_)
      refine natDegree_pow_le.trans ?_
      rw [natDegree_X_sub_C, mul_one]
    have h2 := sum_erase_add (univ : Finset (Fin K)) mult (mem_univ i)
    omega
  have hmult1 : ∀ i, 1 ≤ mult i := fun i => by simp only [hmult]; split_ifs <;> omega
  -- vanishing at the other nodes
  have hvan : ∀ (i j : Fin K) (r : ℝ[X]), j ≠ i →
      d j * ((q i) * r).eval (s j) + e j * (derivative ((q i) * r)).eval (s j) = 0 := by
    intro i j r hji
    obtain ⟨r', hr'⟩ := hq_split i j hji
    by_cases hj : j ∈ G
    · have hm : mult j = 2 := by simp [hmult, hj]
      rw [hr', hm, mul_assoc]
      obtain ⟨e0, e1⟩ := p1_double_root (s j) (r' * r)
      rw [e0, e1]; ring
    · rw [he j hj, zero_mul, add_zero]
      have hm : mult j = 1 := by simp [hmult, hj]
      rw [hr', hm, pow_one]; simp
  have hK : ∀ i : Fin K, 1 ≤ K := fun i => by have := i.isLt; omega
  -- step 1: `e = 0`
  have hE : ∀ i, e i = 0 := by
    intro i
    by_cases hi : i ∈ G
    · have hdeg : (q i * (X - C (s i))).natDegree < N := by
        refine (natDegree_mul_le).trans_lt ?_
        rw [natDegree_X_sub_C]
        have := hq_deg i; have hm : mult i = 2 := by simp [hmult, hi]
        omega
      have h0 := hΛ _ hdeg
      have hval : Λ (q i * (X - C (s i))) = e i * (q i).eval (s i) := by
        simp only [hΛdef]
        rw [sum_eq_single i]
        · simp [derivative_mul]
        · intro j _ hji; exact hvan i j _ hji
        · intro h'; exact absurd (mem_univ i) h'
      rw [hval] at h0
      rcases mul_eq_zero.mp h0 with h1 | h1
      · exact h1
      · exact absurd h1 (hq_eval_ne i)
    · exact he i hi
  -- step 2: `d = 0`
  have hD : ∀ i, d i = 0 := by
    intro i
    have hdeg : (q i * 1).natDegree < N := by
      rw [mul_one]; have := hq_deg i; have := hmult1 i; omega
    have h0 := hΛ _ hdeg
    have hval : Λ (q i * 1) = d i * (q i).eval (s i) := by
      simp only [hΛdef]
      rw [sum_eq_single i]
      · simp [hE i]
      · intro j _ hji; exact hvan i j 1 hji
      · intro h'; exact absurd (mem_univ i) h'
    rw [hval] at h0
    rcases mul_eq_zero.mp h0 with h1 | h1
    · exact h1
    · exact absurd h1 (hq_eval_ne i)
  exact ⟨funext hE, funext hD⟩

/-- The witness configuration: market `j` puts weight `1` on the algorithms `i` with `g i = j`. -/
def rankWitness {K D : ℕ} (s : Fin K → ℝ) (g : Fin K → Fin D) : PoolParam K D :=
  (s, fun j i => if g i = j then 1 else 0)

/-- **Condition (R) at the witness.** If every market's group satisfies `K + |G_j| ≤ l + 1`, the differential of
the pooled moment map up to order `l` is injective at the witness. -/
theorem p1_rank_condition_witness {K D : ℕ} (s : Fin K → ℝ) (hs : Function.Injective s) (g : Fin K → Fin D)
    (l : ℕ) (hl : ∀ j : Fin D, K + (univ.filter (fun i => g i = j)).card ≤ l + 1) :
    Function.Injective (fderiv ℝ (pooledMomentMap K D l) (rankWitness s g)) := by
  classical
  refine (injective_iff_map_eq_zero _).mpr (fun v hv => ?_)
  have hcomp : ∀ j : Fin D, ∀ m < l + 1, ∑ i, (v.2 j i * s i ^ m +
      (if g i = j then v.1 i else 0) * ((m : ℝ) * s i ^ (m - 1))) = 0 := by
    intro j m hm
    have := congrFun (congrFun hv j) ⟨m, hm⟩
    rw [p1_pooledMomentMap_fderiv_apply] at this
    simp only [rankWitness, Pi.zero_apply] at this
    have e : ∑ i, (v.2 j i * s i ^ m + (if g i = j then v.1 i else 0) * ((m : ℝ) * s i ^ (m - 1))) =
        ∑ i, (v.2 j i * s i ^ m + (if g i = j then 1 else 0) * ((m : ℝ) * s i ^ (m - 1)) * v.1 i) :=
      sum_congr rfl fun i _ => by split_ifs <;> ring
    rw [e]; exact this
  have hj : ∀ j : Fin D, (fun i => if g i = j then v.1 i else 0) = 0 ∧ v.2 j = 0 := fun j =>
    p1_hermite_partial s (v.2 j) (fun i => if g i = j then v.1 i else 0)
      (univ.filter (fun i => g i = j)) hs
      (fun i hi => by simp only [mem_filter, mem_univ, true_and] at hi; simp [hi])
      (l + 1) (hl j) (hcomp j)
  refine Prod.ext (funext fun i => ?_) (funext fun j => (hj j).2)
  have := congrFun (hj (g i)).1 i
  simpa using this

/-- **The groups `i mod D` are small.** Each has at most `⌈K/D⌉ = (K + D - 1)/D` members. -/
theorem p1_mod_groups_small (K D : ℕ) (hD : 0 < D) (j : Fin D) :
    (univ.filter (fun i : Fin K => i.val % D = j.val)).card ≤ (K + D - 1) / D := by
  classical
  have hinj : Set.InjOn (fun i : Fin K => i.val / D) (univ.filter (fun i : Fin K => i.val % D = j.val) : Finset (Fin K)) := by
    intro a ha b hb hab
    simp only [coe_filter, mem_univ, true_and, Set.mem_setOf_eq] at ha hb
    simp only at hab
    apply Fin.ext
    rw [← Nat.div_add_mod a.val D, ← Nat.div_add_mod b.val D, hab, ha, hb]
  have hmap : ∀ i ∈ univ.filter (fun i : Fin K => i.val % D = j.val), (fun i : Fin K => i.val / D) i ∈
      range ((K + D - 1) / D) := by
    intro i _
    simp only [mem_range]
    have hi := i.isLt
    have hK : K + D - 1 = (K - 1) + D := by omega
    rw [hK, Nat.add_div_right _ hD]
    exact Nat.lt_succ_of_le (Nat.div_le_div_right (by omega))
  calc _ ≤ (range ((K + D - 1) / D)).card := card_le_card_of_injOn _ hmap hinj
    _ = (K + D - 1) / D := card_range _

/-- **Condition (R) holds at a configuration for every `K` and `D`**, at order `l* = K + ⌈K/D⌉ - 1`. -/
theorem p1_rank_condition_every_K (K D : ℕ) (hD : 0 < D) (s : Fin K → ℝ) (hs : Function.Injective s) :
    Function.Injective (fderiv ℝ (pooledMomentMap K D (K + (K + D - 1) / D - 1))
      (rankWitness s (fun i => (⟨i.val % D, Nat.mod_lt _ hD⟩ : Fin D)))) := by
  apply p1_rank_condition_witness s hs
  intro j
  have h := p1_mod_groups_small K D hD j
  have e : (univ.filter (fun i : Fin K => (⟨i.val % D, Nat.mod_lt _ hD⟩ : Fin D) = j)) =
      univ.filter (fun i : Fin K => i.val % D = j.val) := by
    ext i; simp [Fin.ext_iff]
  rw [e]
  omega

end CurrentMM
