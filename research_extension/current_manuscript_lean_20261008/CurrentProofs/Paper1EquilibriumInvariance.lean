import Mathlib.Algebra.BigOperators.Fin
import Mathlib.Data.Real.Basic
import Mathlib.Data.Fin.VecNotation
import Mathlib.Tactic.IntervalCases
import Mathlib.Tactic.LinearCombination
import Mathlib.Tactic.Ring

/-!
# Paper 1, Theorem E1: equilibrium invariance under the merged measure

Feedback cohorts i update a memory state on a public price signal s, with `m_i(0) = 0` and
`m_i(t+1) = r_i m_i(t) + s(t)`, and trade `w_i m_i(t)`. In the paper's notation `wᵢ = qᵢηᵢ` and `rᵢ = 1 - ηᵢ`, so the
weights are the merged measure.

* `p1_eqAggFlow_kernel`: aggregate feedback flow is `Σ_{m<t} k_m s(t-1-m)`, with kernel `k_m = Σ_i w_i r_i^m`.
  Cohorts enter only through the moments of the merged measure.
* `p1_eqAggFlow_of_kernel`, `p1_kernel_of_eqAggFlow`: on a horizon `T`, two cohort configurations generate the same
  aggregate flow for every price signal **iff** their kernels agree on `m < T`.
* `p1_eq_market_invariance`: an arbitrary market around the cohorts has
  - a strategic insider: any causal rule of the value and the public history;
  - noise trades `z`;
  - a market maker: any causal pricing rule of prices and total order flow, so Kyle, inventory-averse or learning
    dealers are all covered;
  - a public signal: any causal statistic of prices.

  Two economies whose kernels agree on `m < T` have **identical** price and order-flow paths on `t ≤ T` for every
  strategy profile and every realization. Hence (`p1_eq_insider_profit_invariance`) identical insider profits and
  dealer inventories. Every strategy set and every payoff, as a function of the profile, coincide, so the two games
  have the same equilibria with the same outcomes.
* `p1_eq_group_level_differs`: the decomposition is not irrelevant to everyone. A Gauss pair and a Radau pair have
  equal kernels for `m < 3` (so they are equivalent on `T = 3`), yet their largest cohort weights are `1/2` and `3/4`.
-/

namespace CurrentMM

open Finset

/-- Memory state of one cohort on a public signal `s`. -/
def eqMem (r : ℝ) (s : ℕ → ℝ) : ℕ → ℝ
  | 0 => 0
  | t + 1 => r * eqMem r s t + s t

/-- Aggregate feedback flow at date `t`. -/
def eqAggFlow {K : ℕ} (w r : Fin K → ℝ) (s : ℕ → ℝ) (t : ℕ) : ℝ := ∑ i, w i * eqMem (r i) s t

/-- Kernel `k_m = Σ_i w_i r_i^m`, the moments of the merged measure. -/
def eqKernel {K : ℕ} (w r : Fin K → ℝ) (m : ℕ) : ℝ := ∑ i, w i * r i ^ m

theorem p1_eqMem_eq (r : ℝ) (s : ℕ → ℝ) (t : ℕ) :
    eqMem r s t = ∑ m ∈ range t, r ^ m * s (t - 1 - m) := by
  induction t with
  | zero => simp [eqMem]
  | succ t ih =>
    have h0 : eqMem r s (t + 1) = r * eqMem r s t + s t := rfl
    rw [h0, ih, Finset.sum_range_succ', mul_sum]
    have h1 : ∀ m ∈ range t, r * (r ^ m * s (t - 1 - m)) = r ^ (m + 1) * s (t + 1 - 1 - (m + 1)) := by
      intro m _
      rw [show t + 1 - 1 - (m + 1) = t - 1 - m by omega]
      ring
    rw [sum_congr rfl h1]
    simp

/-- **Aggregate feedback flow depends on the cohorts only through the kernel.** -/
theorem p1_eqAggFlow_kernel {K : ℕ} (w r : Fin K → ℝ) (s : ℕ → ℝ) (t : ℕ) :
    eqAggFlow w r s t = ∑ m ∈ range t, eqKernel w r m * s (t - 1 - m) := by
  unfold eqAggFlow eqKernel
  simp_rw [p1_eqMem_eq, mul_sum, sum_mul]
  rw [Finset.sum_comm]
  exact sum_congr rfl fun m _ => sum_congr rfl fun i _ => by ring

/-- Aggregate flow at `t` uses the signal only before `t`. -/
theorem p1_eqAggFlow_congr {K : ℕ} (w r : Fin K → ℝ) (s s' : ℕ → ℝ) (t : ℕ) (h : ∀ j < t, s j = s' j) :
    eqAggFlow w r s t = eqAggFlow w r s' t := by
  rw [p1_eqAggFlow_kernel, p1_eqAggFlow_kernel]
  refine sum_congr rfl fun m hm => ?_
  rw [h (t - 1 - m) (by simp only [mem_range] at hm; omega)]

/-- **Equal kernels on the horizon give equal aggregate flow for every signal.** -/
theorem p1_eqAggFlow_of_kernel {K K' : ℕ} (w r : Fin K → ℝ) (w' r' : Fin K' → ℝ) (T : ℕ)
    (hk : ∀ m < T, eqKernel w r m = eqKernel w' r' m) (s : ℕ → ℝ) (t : ℕ) (ht : t ≤ T) :
    eqAggFlow w r s t = eqAggFlow w' r' s t := by
  rw [p1_eqAggFlow_kernel, p1_eqAggFlow_kernel]
  refine sum_congr rfl fun m hm => ?_
  rw [hk m (by simp only [mem_range] at hm; omega)]

/-- The impulse signal `s = 1{j = 0}` reads off the kernel: the aggregate flow at `m + 1` is `k_m`. -/
theorem p1_eqAggFlow_impulse {K : ℕ} (w r : Fin K → ℝ) (m : ℕ) :
    eqAggFlow w r (fun j => if j = 0 then (1 : ℝ) else 0) (m + 1) = eqKernel w r m := by
  rw [p1_eqAggFlow_kernel, Finset.sum_eq_single m]
  · show eqKernel w r m * (if m + 1 - 1 - m = 0 then (1 : ℝ) else 0) = eqKernel w r m
    rw [if_pos (by omega), mul_one]
  · intro j hj hjm
    have hne : ¬ (m + 1 - 1 - j = 0) := by simp only [mem_range] at hj; omega
    show eqKernel w r j * (if m + 1 - 1 - j = 0 then (1 : ℝ) else 0) = 0
    rw [if_neg hne, mul_zero]
  · intro hm
    exact absurd (mem_range.mpr (Nat.lt_succ_self m)) hm

/-- **Converse: equal aggregate flow forces equal kernels.** -/
theorem p1_kernel_of_eqAggFlow {K K' : ℕ} (w r : Fin K → ℝ) (w' r' : Fin K' → ℝ) (T : ℕ)
    (h : ∀ s : ℕ → ℝ, ∀ t ≤ T, eqAggFlow w r s t = eqAggFlow w' r' s t) : ∀ m < T, eqKernel w r m = eqKernel w' r' m := by
  intro m hm
  have := h (fun j => if j = 0 then (1 : ℝ) else 0) (m + 1) hm
  rwa [p1_eqAggFlow_impulse, p1_eqAggFlow_impulse] at this

/-- A market around the feedback cohorts, in realized form. `ps` and `ys` are the price and total order-flow paths.
The insider rule `X`, the dealer's pricing rule `Pr` and the public signal `S` are arbitrary. -/
def EqMarketPath {K : ℕ} (w r : Fin K → ℝ) (v : ℝ) (z : ℕ → ℝ)
    (X : ℕ → ℝ → (ℕ → ℝ) → (ℕ → ℝ) → ℝ) (Pr : ℕ → (ℕ → ℝ) → (ℕ → ℝ) → ℝ) (S : ℕ → (ℕ → ℝ) → ℝ)
    (ps ys : ℕ → ℝ) : Prop :=
  (∀ t, ys t = X t v ps ys + z t + eqAggFlow w r (fun j => S j ps) t) ∧ (∀ t, ps t = Pr t ps ys)

/-- Causality of the rules. The insider at `t` sees prices and flow before `t`. The dealer at `t` sees prices before
`t` and flow up to `t`. The signal at `j` is a statistic of prices up to `j`. -/
structure EqCausal (X : ℕ → ℝ → (ℕ → ℝ) → (ℕ → ℝ) → ℝ) (Pr : ℕ → (ℕ → ℝ) → (ℕ → ℝ) → ℝ)
    (S : ℕ → (ℕ → ℝ) → ℝ) : Prop where
  insider : ∀ t v ps ps' ys ys', (∀ j < t, ps j = ps' j) → (∀ j < t, ys j = ys' j) → X t v ps ys = X t v ps' ys'
  dealer : ∀ t ps ps' ys ys', (∀ j < t, ps j = ps' j) → (∀ j ≤ t, ys j = ys' j) → Pr t ps ys = Pr t ps' ys'
  signal : ∀ j ps ps', (∀ i ≤ j, ps i = ps' i) → S j ps = S j ps'

/-- **Theorem E1 (pathwise).** Fix the insider rule, the noise path, the dealer's pricing rule and the public signal.
Two cohort configurations whose kernels agree for `m < T` produce identical price and order-flow paths on `t ≤ T`. -/
theorem p1_eq_market_invariance {K K' : ℕ} (w r : Fin K → ℝ) (w' r' : Fin K' → ℝ) (T : ℕ)
    (hk : ∀ m < T, eqKernel w r m = eqKernel w' r' m) (v : ℝ) (z : ℕ → ℝ)
    (X : ℕ → ℝ → (ℕ → ℝ) → (ℕ → ℝ) → ℝ) (Pr : ℕ → (ℕ → ℝ) → (ℕ → ℝ) → ℝ) (S : ℕ → (ℕ → ℝ) → ℝ)
    (hc : EqCausal X Pr S) (ps ys ps' ys' : ℕ → ℝ)
    (h : EqMarketPath w r v z X Pr S ps ys) (h' : EqMarketPath w' r' v z X Pr S ps' ys') :
    ∀ t ≤ T, ps t = ps' t ∧ ys t = ys' t := by
  intro t
  induction t using Nat.strong_induction_on with
  | _ t ih =>
    intro ht
    have hp : ∀ j < t, ps j = ps' j := fun j hj => (ih j hj (by omega)).1
    have hy : ∀ j < t, ys j = ys' j := fun j hj => (ih j hj (by omega)).2
    have hsig : ∀ j < t, S j ps = S j ps' := fun j hj =>
      hc.signal j ps ps' fun i hi => hp i (by omega)
    have hflow : eqAggFlow w r (fun j => S j ps) t = eqAggFlow w' r' (fun j => S j ps') t := by
      rw [p1_eqAggFlow_congr w r _ (fun j => S j ps') t hsig]
      exact p1_eqAggFlow_of_kernel w r w' r' T hk _ t ht
    have hyt : ys t = ys' t := by
      rw [h.1 t, h'.1 t, hc.insider t v ps ps' ys ys' hp hy, hflow]
    refine ⟨?_, hyt⟩
    rw [h.2 t, h'.2 t]
    exact hc.dealer t ps ps' ys ys' hp fun j hj => by
      rcases Nat.lt_or_ge j t with hlt | hge
      · exact hy j hlt
      · rw [show j = t by omega]; exact hyt

/-- **Corollary.** Realized insider profit `Σ_{t<T} (v - p_t) x_t` and the dealer's inventory `-Σ_{t<T} y_t` are
identical in the two economies, for every strategy profile and every realization. -/
theorem p1_eq_insider_profit_invariance {K K' : ℕ} (w r : Fin K → ℝ) (w' r' : Fin K' → ℝ) (T : ℕ)
    (hk : ∀ m < T, eqKernel w r m = eqKernel w' r' m) (v : ℝ) (z : ℕ → ℝ)
    (X : ℕ → ℝ → (ℕ → ℝ) → (ℕ → ℝ) → ℝ) (Pr : ℕ → (ℕ → ℝ) → (ℕ → ℝ) → ℝ) (S : ℕ → (ℕ → ℝ) → ℝ)
    (hc : EqCausal X Pr S) (ps ys ps' ys' : ℕ → ℝ)
    (h : EqMarketPath w r v z X Pr S ps ys) (h' : EqMarketPath w' r' v z X Pr S ps' ys') :
    (∑ t ∈ range T, (v - ps t) * X t v ps ys = ∑ t ∈ range T, (v - ps' t) * X t v ps' ys') ∧
    (-(∑ t ∈ range T, ys t) = -(∑ t ∈ range T, ys' t)) := by
  have E := p1_eq_market_invariance w r w' r' T hk v z X Pr S hc ps ys ps' ys' h h'
  refine ⟨sum_congr rfl fun t ht => ?_, by rw [sum_congr rfl fun t ht => (E t (by simp only [mem_range] at ht; omega)).2]⟩
  have htT : t < T := by simpa using ht
  have hp : ∀ j < t, ps j = ps' j := fun j hj => (E j (by omega)).1
  have hy : ∀ j < t, ys j = ys' j := fun j hj => (E j (by omega)).2
  rw [(E t htT.le).1, hc.insider t v ps ps' ys ys' hp hy]

/-! ### The decomposition still matters for group-level questions -/

/-- Gauss and Radau two-point configurations on rates `c + d s`, with Gauss nodes `±σ`, `σ² = 1/3`. -/
theorem p1_eq_gauss_radau_kernels (c d σ : ℝ) (hσ : σ ^ 2 = 1 / 3) :
    ∀ m < 3, eqKernel ![1 / 2, 1 / 2] ![c - d * σ, c + d * σ] m = eqKernel ![1 / 4, 3 / 4] ![c - d, c + d / 3] m := by
  intro m hm
  interval_cases m
  · first
    | (simp [eqKernel, Fin.sum_univ_two]; done)
    | (simp [eqKernel, Fin.sum_univ_two]; norm_num)
  · first
    | (simp [eqKernel, Fin.sum_univ_two]; done)
    | (simp [eqKernel, Fin.sum_univ_two]; ring)
  · simp only [eqKernel, Fin.sum_univ_two, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons]
    linear_combination d ^ 2 * hσ

/-- **The group-level decomposition is not invariant.** The two configurations are equivalent on horizon `T = 3` for
every insider rule, dealer rule and signal (`p1_eq_market_invariance`), yet their largest cohorts carry weights `1/2`
and `3/4`. A targeted action, such as halting the largest group, removes different shares of the response. -/
theorem p1_eq_group_level_differs (c d σ : ℝ) (hσ : σ ^ 2 = 1 / 3) :
    (∀ m < 3, eqKernel ![1 / 2, 1 / 2] ![c - d * σ, c + d * σ] m = eqKernel ![1 / 4, 3 / 4] ![c - d, c + d / 3] m) ∧
    (max (1 / 2 : ℝ) (1 / 2) = 1 / 2 ∧ max (1 / 4 : ℝ) (3 / 4) = 3 / 4) := by
  refine ⟨p1_eq_gauss_radau_kernels c d σ hσ, max_self _, max_eq_right (by norm_num)⟩

end CurrentMM
