import CurrentProofs.Paper1SaturatingSufficiency

/-!
# Paper 1 (core version): any linear population (Proposition 3.2) and deleveraging traders (Proposition 7.5)

* `p1_anylinear_flow_kernel`, `p1_anylinear_iff`, `p1_anylinear_invariance`: a population of linear traders with
  arbitrary kernels `κ_j` acts only through `k = Σ_j κ_j`. Two populations give the same aggregate flow for every
  signal on `t ≤ T` iff their kernels agree for `m < T`, and then every market path coincides on `t ≤ T`.
* `p1_delever_stress_invariance`: traders may follow *any* causal rule (hard limits, deleveraging, forced liquidation,
  path-dependent behaviour) provided that each trades linearly, `w_i m_i(t)`, as long as its state has stayed inside
  its band on every date up to `t`. Two such populations with the same kernel produce identical paths until the first
  date at which some trader of either population leaves its band.
-/

namespace CurrentMM

open Finset

/-- Aggregate flow of linear traders with arbitrary kernels `κ j`. -/
def linPopFlow {J : ℕ} (κ : Fin J → ℕ → ℝ) (s : ℕ → ℝ) (t : ℕ) : ℝ :=
  ∑ j, ∑ m ∈ range t, κ j m * s (t - 1 - m)

/-- The population's kernel `k_m = Σ_j κ_j(m)`. -/
def linPopKernel {J : ℕ} (κ : Fin J → ℕ → ℝ) (m : ℕ) : ℝ := ∑ j, κ j m

theorem p1_anylinear_flow_kernel {J : ℕ} (κ : Fin J → ℕ → ℝ) (s : ℕ → ℝ) (t : ℕ) :
    linPopFlow κ s t = ∑ m ∈ range t, linPopKernel κ m * s (t - 1 - m) := by
  unfold linPopFlow linPopKernel
  rw [Finset.sum_comm]
  exact sum_congr rfl fun m _ => by rw [sum_mul]

theorem p1_linPop_impulse {J : ℕ} (κ : Fin J → ℕ → ℝ) (m : ℕ) :
    linPopFlow κ (fun j => if j = 0 then (1 : ℝ) else 0) (m + 1) = linPopKernel κ m := by
  rw [p1_anylinear_flow_kernel, Finset.sum_eq_single m]
  · show linPopKernel κ m * (if m + 1 - 1 - m = 0 then (1 : ℝ) else 0) = linPopKernel κ m
    rw [if_pos (by omega), mul_one]
  · intro j hj hjm
    have hne : ¬ (m + 1 - 1 - j = 0) := by simp only [mem_range] at hj; omega
    show linPopKernel κ j * (if m + 1 - 1 - j = 0 then (1 : ℝ) else 0) = 0
    rw [if_neg hne, mul_zero]
  · intro hm
    exact absurd (mem_range.mpr (Nat.lt_succ_self m)) hm

/-- **Proposition 3.2(i).** Same aggregate flow for every signal on `t ≤ T` iff equal kernels for `m < T`. -/
theorem p1_anylinear_iff {J J' : ℕ} (κ : Fin J → ℕ → ℝ) (κ' : Fin J' → ℕ → ℝ) (T : ℕ) :
    (∀ s : ℕ → ℝ, ∀ t ≤ T, linPopFlow κ s t = linPopFlow κ' s t) ↔
      (∀ m < T, linPopKernel κ m = linPopKernel κ' m) := by
  constructor
  · intro h m hm
    have := h (fun j => if j = 0 then (1 : ℝ) else 0) (m + 1) hm
    rwa [p1_linPop_impulse, p1_linPop_impulse] at this
  · intro hk s t ht
    rw [p1_anylinear_flow_kernel, p1_anylinear_flow_kernel]
    refine sum_congr rfl fun m hm => ?_
    rw [hk m (by simp only [mem_range] at hm; omega)]

/-- **Proposition 3.2(ii), pathwise.** Equal kernels for `m < T` give identical paths on `t ≤ T`, for every causal
insider, dealer and signal rule. -/
theorem p1_anylinear_invariance {J J' : ℕ} (κ : Fin J → ℕ → ℝ) (κ' : Fin J' → ℕ → ℝ) (T : ℕ)
    (hk : ∀ m < T, linPopKernel κ m = linPopKernel κ' m) (v : ℝ) (z : ℕ → ℝ)
    (X : ℕ → ℝ → (ℕ → ℝ) → (ℕ → ℝ) → ℝ) (Pr : ℕ → (ℕ → ℝ) → (ℕ → ℝ) → ℝ) (S : ℕ → (ℕ → ℝ) → ℝ)
    (hc : EqCausal X Pr S) (ps ys ps' ys' : ℕ → ℝ)
    (h : FlowMarketPath (linPopFlow κ) v z X Pr S ps ys) (h' : FlowMarketPath (linPopFlow κ') v z X Pr S ps' ys') :
    ∀ t ≤ T, ps t = ps' t ∧ ys t = ys' t := by
  refine p1_flow_market_invariance (linPopFlow κ) (linPopFlow κ') T ?_ ((p1_anylinear_iff κ κ' T).2 hk)
    v z X Pr S hc ps ys ps' ys' h h'
  intro s s' t hst
  rw [p1_anylinear_flow_kernel, p1_anylinear_flow_kernel]
  refine sum_congr rfl fun m hm => ?_
  rw [hst (t - 1 - m) (by simp only [mem_range] at hm; omega)]

/-- A trader that may deleverage, liquidate or follow any path-dependent rule outside its band: its flow map `G` is
causal, and equals `w * m(t)` whenever its state has stayed in the band on every date up to `t`. -/
structure BandLinearTrader where
  w : ℝ
  r : ℝ
  l : ℝ
  G : (ℕ → ℝ) → ℕ → ℝ
  causal : ∀ s s' t, (∀ j < t, s j = s' j) → G s t = G s' t
  linear_in_band : ∀ s t, (∀ j ≤ t, |l * eqMem r s j| ≤ 1) → G s t = w * eqMem r s t

def bandPopFlow {K : ℕ} (P : Fin K → BandLinearTrader) (s : ℕ → ℝ) (t : ℕ) : ℝ := ∑ i, (P i).G s t

/-- **Proposition 7.5 (deleveraging traders), pathwise.** Two populations of band-linear traders with the same
kernel `Σ w_i r_i^m` (`m < T`) produce identical paths on `t ≤ T` provided that, along the first market's path, every
trader of both populations has stayed in its band on every date up to `T`. -/
theorem p1_delever_stress_invariance {K K' : ℕ} (P : Fin K → BandLinearTrader) (P' : Fin K' → BandLinearTrader)
    (T : ℕ)
    (hk : ∀ m < T, eqKernel (fun i => (P i).w) (fun i => (P i).r) m = eqKernel (fun i => (P' i).w) (fun i => (P' i).r) m)
    (v : ℝ) (z : ℕ → ℝ)
    (X : ℕ → ℝ → (ℕ → ℝ) → (ℕ → ℝ) → ℝ) (Pr : ℕ → (ℕ → ℝ) → (ℕ → ℝ) → ℝ) (S : ℕ → (ℕ → ℝ) → ℝ)
    (hc : EqCausal X Pr S) (ps ys ps' ys' : ℕ → ℝ)
    (h : FlowMarketPath (bandPopFlow P) v z X Pr S ps ys) (h' : FlowMarketPath (bandPopFlow P') v z X Pr S ps' ys')
    (hband : ∀ t ≤ T, (∀ i, |(P i).l * eqMem (P i).r (fun j => S j ps) t| ≤ 1) ∧
      (∀ i, |(P' i).l * eqMem (P' i).r (fun j => S j ps) t| ≤ 1)) :
    ∀ t ≤ T, ps t = ps' t ∧ ys t = ys' t := by
  intro t
  induction t using Nat.strong_induction_on with
  | _ t ih =>
    intro ht
    have hp : ∀ j < t, ps j = ps' j := fun j hj => (ih j hj (by omega)).1
    have hy : ∀ j < t, ys j = ys' j := fun j hj => (ih j hj (by omega)).2
    have hsig : ∀ j < t, S j ps = S j ps' := fun j hj =>
      hc.signal j ps ps' fun i hi => hp i (by omega)
    have hflow : bandPopFlow P (fun j => S j ps) t = bandPopFlow P' (fun j => S j ps') t := by
      have e1 : bandPopFlow P (fun j => S j ps) t = eqAggFlow (fun i => (P i).w) (fun i => (P i).r) (fun j => S j ps) t := by
        unfold bandPopFlow eqAggFlow
        exact sum_congr rfl fun i _ =>
          (P i).linear_in_band _ t fun j hj => (hband j (by omega)).1 i
      have e2 : bandPopFlow P' (fun j => S j ps') t = eqAggFlow (fun i => (P' i).w) (fun i => (P' i).r) (fun j => S j ps) t := by
        unfold bandPopFlow eqAggFlow
        refine sum_congr rfl fun i _ => ?_
        rw [(P' i).causal (fun j => S j ps') (fun j => S j ps) t fun j hj => (hsig j hj).symm]
        exact (P' i).linear_in_band _ t fun j hj => (hband j (by omega)).2 i
      rw [e1, e2]
      exact p1_eqAggFlow_of_kernel _ _ _ _ T hk _ t ht
    have hyt : ys t = ys' t := by
      rw [h.1 t, h'.1 t, hc.insider t v ps ps' ys ys' hp hy, hflow]
    refine ⟨?_, hyt⟩
    rw [h.2 t, h'.2 t]
    exact hc.dealer t ps ps' ys ys' hp fun j hj => by
      rcases Nat.lt_or_ge j t with hlt | hge
      · exact hy j hlt
      · rw [show j = t by omega]; exact hyt

end CurrentMM
