import CurrentProofs.Paper1EquilibriumInvariance

/-!
# Paper 1 (core version), Section 7: saturating feedback traders

Trader `i` has memory rate `r i`, capacity `c i` and leverage `l i`. Its memory state is `eqMem (r i) s t`, the state of
`Paper1EquilibriumInvariance`, and its flow is `c i * ψ (l i * eqMem (r i) s t)`. The policy shape `ψ` is any
function; a *band-linear* shape satisfies `ψ u = u` for `|u| ≤ 1` (a position limit at `|u| = 1` is the case
`ψ = clip`).

* `p1_sat_sufficiency`: two populations that define the same capacity-weighted measure `ν = Σ c_i δ_(r_i, l_i)` (tested
  against every function of memory and leverage) produce identical price and order-flow paths at every date, for every
  insider rule, dealer rule and public signal.
* `p1_satAggFlow_linear_of_band`: while every trader is inside its band, aggregate flow equals the linear flow of the
  merged weights `c_i l_i`.
* `p1_sat_stress_invariance`: two band-linear populations with the same kernel `Σ c_i l_i r_i^m` (`m < T`) produce
  identical paths on `t ≤ T` whenever, along the path, no trader of either population leaves its band. So no
  record that ends before the first exceedance distinguishes them.
-/

namespace CurrentMM

open Finset

/-- Aggregate flow of saturating traders. -/
def satAggFlow {K : ℕ} (ψ : ℝ → ℝ) (c l r : Fin K → ℝ) (s : ℕ → ℝ) (t : ℕ) : ℝ :=
  ∑ i, c i * ψ (l i * eqMem (r i) s t)

/-- A market around a general causal aggregate-flow map `F`, in realized form (as `EqMarketPath`). -/
def FlowMarketPath (F : (ℕ → ℝ) → ℕ → ℝ) (v : ℝ) (z : ℕ → ℝ)
    (X : ℕ → ℝ → (ℕ → ℝ) → (ℕ → ℝ) → ℝ) (Pr : ℕ → (ℕ → ℝ) → (ℕ → ℝ) → ℝ) (S : ℕ → (ℕ → ℝ) → ℝ)
    (ps ys : ℕ → ℝ) : Prop :=
  (∀ t, ys t = X t v ps ys + z t + F (fun j => S j ps) t) ∧ (∀ t, ps t = Pr t ps ys)

/-- The memory state at `t` uses the signal only before `t`. -/
theorem p1_eqMem_congr (r : ℝ) (s s' : ℕ → ℝ) (t : ℕ) (h : ∀ j < t, s j = s' j) :
    eqMem r s t = eqMem r s' t := by
  rw [p1_eqMem_eq, p1_eqMem_eq]
  refine sum_congr rfl fun m hm => ?_
  rw [h (t - 1 - m) (by simp only [mem_range] at hm; omega)]

theorem p1_satAggFlow_congr {K : ℕ} (ψ : ℝ → ℝ) (c l r : Fin K → ℝ) (s s' : ℕ → ℝ) (t : ℕ)
    (h : ∀ j < t, s j = s' j) : satAggFlow ψ c l r s t = satAggFlow ψ c l r s' t := by
  unfold satAggFlow
  exact sum_congr rfl fun i _ => by rw [p1_eqMem_congr (r i) s s' t h]

/-- Generic invariance: two causal flow maps that agree, for every signal, on dates `t ≤ T` give identical paths on
`t ≤ T`. -/
theorem p1_flow_market_invariance (F F' : (ℕ → ℝ) → ℕ → ℝ) (T : ℕ)
    (hcausal : ∀ s s' t, (∀ j < t, s j = s' j) → F s t = F s' t)
    (hF : ∀ s, ∀ t ≤ T, F s t = F' s t) (v : ℝ) (z : ℕ → ℝ)
    (X : ℕ → ℝ → (ℕ → ℝ) → (ℕ → ℝ) → ℝ) (Pr : ℕ → (ℕ → ℝ) → (ℕ → ℝ) → ℝ) (S : ℕ → (ℕ → ℝ) → ℝ)
    (hc : EqCausal X Pr S) (ps ys ps' ys' : ℕ → ℝ)
    (h : FlowMarketPath F v z X Pr S ps ys) (h' : FlowMarketPath F' v z X Pr S ps' ys') :
    ∀ t ≤ T, ps t = ps' t ∧ ys t = ys' t := by
  intro t
  induction t using Nat.strong_induction_on with
  | _ t ih =>
    intro ht
    have hp : ∀ j < t, ps j = ps' j := fun j hj => (ih j hj (by omega)).1
    have hy : ∀ j < t, ys j = ys' j := fun j hj => (ih j hj (by omega)).2
    have hsig : ∀ j < t, S j ps = S j ps' := fun j hj =>
      hc.signal j ps ps' fun i hi => hp i (by omega)
    have hflow : F (fun j => S j ps) t = F' (fun j => S j ps') t := by
      rw [hcausal (fun j => S j ps) (fun j => S j ps') t hsig]
      exact hF _ t ht
    have hyt : ys t = ys' t := by
      rw [h.1 t, h'.1 t, hc.insider t v ps ps' ys ys' hp hy, hflow]
    refine ⟨?_, hyt⟩
    rw [h.2 t, h'.2 t]
    exact hc.dealer t ps ps' ys ys' hp fun j hj => by
      rcases Nat.lt_or_ge j t with hlt | hge
      · exact hy j hlt
      · rw [show j = t by omega]; exact hyt

/-- **Sufficiency of `ν` (Theorem 7.1, pathwise).** If the two capacity-weighted measures on (memory, leverage)
agree, i.e. `Σ_i c_i g(r_i, l_i) = Σ_j c'_j g(r'_j, l'_j)` for every function `g`, the two markets have identical
price and order-flow paths at every date, for every insider rule, dealer rule and signal. -/
theorem p1_sat_sufficiency {K K' : ℕ} (ψ : ℝ → ℝ) (c l r : Fin K → ℝ) (c' l' r' : Fin K' → ℝ)
    (hν : ∀ g : ℝ → ℝ → ℝ, ∑ i, c i * g (r i) (l i) = ∑ j, c' j * g (r' j) (l' j)) (v : ℝ) (z : ℕ → ℝ)
    (X : ℕ → ℝ → (ℕ → ℝ) → (ℕ → ℝ) → ℝ) (Pr : ℕ → (ℕ → ℝ) → (ℕ → ℝ) → ℝ) (S : ℕ → (ℕ → ℝ) → ℝ)
    (hc : EqCausal X Pr S) (ps ys ps' ys' : ℕ → ℝ)
    (h : FlowMarketPath (satAggFlow ψ c l r) v z X Pr S ps ys)
    (h' : FlowMarketPath (satAggFlow ψ c' l' r') v z X Pr S ps' ys') :
    ∀ t, ps t = ps' t ∧ ys t = ys' t := by
  intro t
  refine p1_flow_market_invariance (satAggFlow ψ c l r) (satAggFlow ψ c' l' r') t
    (fun s s' t hst => p1_satAggFlow_congr ψ c l r s s' t hst) (fun s t' _ => ?_) v z X Pr S hc ps ys ps' ys' h h' t le_rfl
  exact hν (fun ρ lam => ψ (lam * eqMem ρ s t'))

/-- Inside the band, saturating flow is the linear flow of the merged weights `c_i l_i`. -/
theorem p1_satAggFlow_linear_of_band {K : ℕ} (ψ : ℝ → ℝ) (hψ : ∀ u, |u| ≤ 1 → ψ u = u)
    (c l r : Fin K → ℝ) (s : ℕ → ℝ) (t : ℕ) (hb : ∀ i, |l i * eqMem (r i) s t| ≤ 1) :
    satAggFlow ψ c l r s t = eqAggFlow (fun i => c i * l i) r s t := by
  unfold satAggFlow eqAggFlow
  exact sum_congr rfl fun i _ => by rw [hψ _ (hb i)]; ring

/-- **No information without stress (Theorem 7.2(i), pathwise).** Two band-linear populations (possibly with
different shapes `ψ`, `ψ'`) whose merged kernels agree for `m < T` produce identical price and order-flow paths on
`t ≤ T`, provided that along the path of the first market no trader of either population leaves its band on those
dates. -/
theorem p1_sat_stress_invariance {K K' : ℕ} (ψ ψ' : ℝ → ℝ) (hψ : ∀ u, |u| ≤ 1 → ψ u = u)
    (hψ' : ∀ u, |u| ≤ 1 → ψ' u = u) (c l r : Fin K → ℝ) (c' l' r' : Fin K' → ℝ) (T : ℕ)
    (hk : ∀ m < T, eqKernel (fun i => c i * l i) r m = eqKernel (fun j => c' j * l' j) r' m)
    (v : ℝ) (z : ℕ → ℝ)
    (X : ℕ → ℝ → (ℕ → ℝ) → (ℕ → ℝ) → ℝ) (Pr : ℕ → (ℕ → ℝ) → (ℕ → ℝ) → ℝ) (S : ℕ → (ℕ → ℝ) → ℝ)
    (hc : EqCausal X Pr S) (ps ys ps' ys' : ℕ → ℝ)
    (h : FlowMarketPath (satAggFlow ψ c l r) v z X Pr S ps ys)
    (h' : FlowMarketPath (satAggFlow ψ' c' l' r') v z X Pr S ps' ys')
    (hband : ∀ t ≤ T, (∀ i, |l i * eqMem (r i) (fun j => S j ps) t| ≤ 1) ∧
      (∀ j, |l' j * eqMem (r' j) (fun j => S j ps) t| ≤ 1)) :
    ∀ t ≤ T, ps t = ps' t ∧ ys t = ys' t := by
  intro t
  induction t using Nat.strong_induction_on with
  | _ t ih =>
    intro ht
    have hp : ∀ j < t, ps j = ps' j := fun j hj => (ih j hj (by omega)).1
    have hy : ∀ j < t, ys j = ys' j := fun j hj => (ih j hj (by omega)).2
    have hsig : ∀ j < t, S j ps = S j ps' := fun j hj =>
      hc.signal j ps ps' fun i hi => hp i (by omega)
    have hflow : satAggFlow ψ c l r (fun j => S j ps) t = satAggFlow ψ' c' l' r' (fun j => S j ps') t := by
      rw [← p1_satAggFlow_congr ψ' c' l' r' (fun j => S j ps) (fun j => S j ps') t hsig,
        p1_satAggFlow_linear_of_band ψ hψ c l r _ t (hband t ht).1,
        p1_satAggFlow_linear_of_band ψ' hψ' c' l' r' _ t (hband t ht).2]
      exact p1_eqAggFlow_of_kernel _ r _ r' T hk _ t ht
    have hyt : ys t = ys' t := by
      rw [h.1 t, h'.1 t, hc.insider t v ps ps' ys ys' hp hy, hflow]
    refine ⟨?_, hyt⟩
    rw [h.2 t, h'.2 t]
    exact hc.dealer t ps ps' ys ys' hp fun j hj => by
      rcases Nat.lt_or_ge j t with hlt | hge
      · exact hy j hlt
      · rw [show j = t by omega]; exact hyt

/-- **Corollary.** Up to the first exceedance, a band-linear market follows the *linear* market with the same merged
weights exactly. So the exceedance date can be computed on the linear market (`ψ' = id`). -/
theorem p1_sat_follows_linear {K : ℕ} (ψ : ℝ → ℝ) (hψ : ∀ u, |u| ≤ 1 → ψ u = u)
    (c l r : Fin K → ℝ) (T : ℕ) (v : ℝ) (z : ℕ → ℝ)
    (X : ℕ → ℝ → (ℕ → ℝ) → (ℕ → ℝ) → ℝ) (Pr : ℕ → (ℕ → ℝ) → (ℕ → ℝ) → ℝ) (S : ℕ → (ℕ → ℝ) → ℝ)
    (hc : EqCausal X Pr S) (ps ys ps' ys' : ℕ → ℝ)
    (h : FlowMarketPath (satAggFlow ψ c l r) v z X Pr S ps ys)
    (h' : FlowMarketPath (satAggFlow id c l r) v z X Pr S ps' ys')
    (hband : ∀ t ≤ T, ∀ i, |l i * eqMem (r i) (fun j => S j ps) t| ≤ 1) :
    ∀ t ≤ T, ps t = ps' t ∧ ys t = ys' t :=
  p1_sat_stress_invariance ψ id hψ (fun _ _ => rfl) c l r c l r T (fun _ _ => rfl) v z X Pr S hc ps ys ps' ys' h h'
    fun t ht => ⟨hband t ht, hband t ht⟩

/-- **Capacities differ at the band edge.** The simplest
witness. Populations `{(c = 1, l = 1/10)}` and `{(1/4, 1/5), (1, 1/20)}` at the same memory have the same merged weight
`1/10`, so they are equivalent until stress (`p1_sat_stress_invariance`), yet their total capacities, the largest
aggregate flow they can deliver under a hard limit, are `1` and `5/4`. -/
theorem p1_sat_capacity_differs :
    (1 : ℝ) * (1 / 10) = (1 / 4) * (1 / 5) + 1 * (1 / 20) ∧ (1 : ℝ) ≠ 1 / 4 + 1 := by
  constructor <;> norm_num

end CurrentMM
