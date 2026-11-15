import CurrentProofs.Paper1StressIdentificationGeneral
import Mathlib.Analysis.SpecialFunctions.Exp
import Mathlib.Analysis.Complex.Trigonometric
import Mathlib.Topology.Algebra.Monoid
import Mathlib.Topology.Algebra.GroupWithZero
import Mathlib.Order.Filter.AtTopBot.Field

/-!
# Paper 1 (core version), Theorem 7.4 for the smooth limit `tanh`

* `p1_tanh_indep_dilations`: `tanh` has independent dilations, for any number of scales. The proof uses large
  arguments: `1 - tanh y = 2 e^{-2y} / (1 + e^{-2y})`, so the smallest scale has the slowest-decaying tail and can be
  isolated by multiplying by `e^{2 a u}` and letting `u → ∞`.
* `p1_thm_stress_identification_tanh`: Theorem 7.4 for `tanh`, any number of traders.

This uses probes of every size. The statement that responses to arbitrarily *small* probes already identify the
measure (part (i) of the theorem in the paper) is not formalized here.
-/

namespace CurrentMM

open Filter Topology

/-- `1 - tanh y = 2 e^{-2y} / (1 + e^{-2y})`. -/
theorem p1_one_sub_tanh (y : ℝ) :
    1 - Real.tanh y = 2 * Real.exp (-(2 * y)) / (1 + Real.exp (-(2 * y))) := by
  have hp : 0 < Real.exp y := Real.exp_pos y
  have hq : 0 < Real.exp (-y) := Real.exp_pos (-y)
  have hpq : Real.exp y * Real.exp (-y) = 1 := by
    rw [← Real.exp_add, add_neg_cancel, Real.exp_zero]
  have hqq : Real.exp (-(2 * y)) = Real.exp (-y) * Real.exp (-y) := by
    rw [← Real.exp_add]
    congr 1
    ring
  have h2 : Real.exp y + Real.exp (-y) ≠ 0 := by positivity
  have h1 : 1 + Real.exp (-y) * Real.exp (-y) ≠ 0 := by positivity
  rw [Real.tanh_eq, hqq, one_sub_div h2, div_eq_div_iff h2 h1]
  linear_combination (-2 * Real.exp (-y)) * hpq

theorem p1_tendsto_exp_neg_mul (c : ℝ) (hc : 0 < c) :
    Tendsto (fun u : ℝ => Real.exp (-(c * u))) atTop (𝓝 0) :=
  Real.tendsto_exp_neg_atTop_nhds_zero.comp (tendsto_id.const_mul_atTop hc)

theorem p1_tendsto_one_sub_tanh (x : ℝ) (hx : 0 < x) :
    Tendsto (fun u : ℝ => 1 - Real.tanh (x * u)) atTop (𝓝 0) := by
  have hE : Tendsto (fun u : ℝ => Real.exp (-(2 * (x * u)))) atTop (𝓝 0) :=
    (p1_tendsto_exp_neg_mul (2 * x) (by positivity)).congr (fun u => by rw [mul_assoc])
  have h : Tendsto (fun u : ℝ => 2 * Real.exp (-(2 * (x * u))) / (1 + Real.exp (-(2 * (x * u)))))
      atTop (𝓝 (2 * 0 / (1 + 0))) :=
    (hE.const_mul 2).div (tendsto_const_nhds.add hE) (by norm_num)
  have e : (2 : ℝ) * 0 / (1 + 0) = 0 := by norm_num
  rw [e] at h
  exact h.congr (fun u => (p1_one_sub_tanh (x * u)).symm)

theorem p1_tendsto_scaled_self (a : ℝ) (ha : 0 < a) :
    Tendsto (fun u : ℝ => Real.exp (2 * a * u) * (1 - Real.tanh (a * u))) atTop (𝓝 2) := by
  have hD : Tendsto (fun u : ℝ => Real.exp (-(2 * (a * u)))) atTop (𝓝 0) :=
    (p1_tendsto_exp_neg_mul (2 * a) (by positivity)).congr (fun u => by rw [mul_assoc])
  have h : Tendsto (fun u : ℝ => (2 : ℝ) / (1 + Real.exp (-(2 * (a * u))))) atTop (𝓝 (2 / (1 + 0))) :=
    tendsto_const_nhds.div (tendsto_const_nhds.add hD) (by norm_num)
  have e : (2 : ℝ) / (1 + 0) = 2 := by norm_num
  rw [e] at h
  refine h.congr (fun u => ?_)
  have hexp : Real.exp (2 * a * u) * Real.exp (-(2 * (a * u))) = 1 := by
    rw [← Real.exp_add, show 2 * a * u + -(2 * (a * u)) = 0 by ring, Real.exp_zero]
  rw [p1_one_sub_tanh,
    show Real.exp (2 * a * u) * (2 * Real.exp (-(2 * (a * u))) / (1 + Real.exp (-(2 * (a * u))))) =
      2 * (Real.exp (2 * a * u) * Real.exp (-(2 * (a * u)))) / (1 + Real.exp (-(2 * (a * u)))) by ring,
    hexp, mul_one]

theorem p1_tendsto_scaled_other (a x : ℝ) (ha : 0 < a) (hax : a < x) :
    Tendsto (fun u : ℝ => Real.exp (2 * a * u) * (1 - Real.tanh (x * u))) atTop (𝓝 0) := by
  have hN : Tendsto (fun u : ℝ => Real.exp (-(2 * (x - a) * u))) atTop (𝓝 0) :=
    p1_tendsto_exp_neg_mul (2 * (x - a)) (by linarith)
  have hD : Tendsto (fun u : ℝ => Real.exp (-(2 * (x * u)))) atTop (𝓝 0) :=
    (p1_tendsto_exp_neg_mul (2 * x) (by linarith)).congr (fun u => by rw [mul_assoc])
  have h : Tendsto (fun u : ℝ => 2 * Real.exp (-(2 * (x - a) * u)) / (1 + Real.exp (-(2 * (x * u)))))
      atTop (𝓝 (2 * 0 / (1 + 0))) :=
    (hN.const_mul 2).div (tendsto_const_nhds.add hD) (by norm_num)
  have e : (2 : ℝ) * 0 / (1 + 0) = 0 := by norm_num
  rw [e] at h
  refine h.congr (fun u => ?_)
  have hexp : Real.exp (2 * a * u) * Real.exp (-(2 * (x * u))) = Real.exp (-(2 * (x - a) * u)) := by
    rw [← Real.exp_add]
    congr 1
    ring
  rw [p1_one_sub_tanh, ← hexp]
  ring

/-- **`tanh` has independent dilations**, for any number of scales. -/
theorem p1_tanh_indep_dilations : IndepDilations Real.tanh := by
  intro T
  induction T using Finset.induction_on_min with
  | empty =>
    intro w _ _ s hs
    exact absurd hs (Finset.notMem_empty s)
  | insert a S ha ih =>
    intro w hpos hsum s hs
    have ha_pos : 0 < a := hpos a (Finset.mem_insert_self a S)
    have haS : a ∉ S := fun h => lt_irrefl a (ha a h)
    have hSpos : ∀ x ∈ S, 0 < x := fun x hx => hpos x (Finset.mem_insert_of_mem hx)
    -- the tail sum is constant in `u`
    have hG : ∀ u : ℝ, w a * (1 - Real.tanh (a * u)) + ∑ x ∈ S, w x * (1 - Real.tanh (x * u)) =
        w a + ∑ x ∈ S, w x := by
      intro u
      have h := hsum u
      rw [Finset.sum_insert haS] at h
      have e : ∑ x ∈ S, w x * (1 - Real.tanh (x * u)) =
          ∑ x ∈ S, w x - ∑ x ∈ S, w x * Real.tanh (x * u) := by
        rw [← Finset.sum_sub_distrib]
        exact Finset.sum_congr rfl fun x _ => by ring
      rw [e]
      linear_combination (-1 : ℝ) * h
    -- it tends to 0, so the constant is 0
    have hlim0 : Tendsto
        (fun u : ℝ => w a * (1 - Real.tanh (a * u)) + ∑ x ∈ S, w x * (1 - Real.tanh (x * u)))
        atTop (𝓝 (w a * 0 + ∑ x ∈ S, w x * 0)) :=
      ((p1_tendsto_one_sub_tanh a ha_pos).const_mul (w a)).add
        (tendsto_finsetSum S fun x hx => (p1_tendsto_one_sub_tanh x (hSpos x hx)).const_mul (w x))
    have hC : w a + ∑ x ∈ S, w x = 0 := by
      have hconst : Tendsto
          (fun u : ℝ => w a * (1 - Real.tanh (a * u)) + ∑ x ∈ S, w x * (1 - Real.tanh (x * u)))
          atTop (𝓝 (w a + ∑ x ∈ S, w x)) :=
        tendsto_const_nhds.congr (fun u => (hG u).symm)
      have h := tendsto_nhds_unique hconst hlim0
      simp only [mul_zero, Finset.sum_const_zero, add_zero] at h
      exact h
    -- multiply by `e^{2 a u}`: the smallest scale survives
    have hH : ∀ u : ℝ, w a * (Real.exp (2 * a * u) * (1 - Real.tanh (a * u))) +
        ∑ x ∈ S, w x * (Real.exp (2 * a * u) * (1 - Real.tanh (x * u))) = 0 := by
      intro u
      have h := hG u
      rw [hC] at h
      have e : w a * (Real.exp (2 * a * u) * (1 - Real.tanh (a * u))) +
          ∑ x ∈ S, w x * (Real.exp (2 * a * u) * (1 - Real.tanh (x * u))) =
          Real.exp (2 * a * u) *
            (w a * (1 - Real.tanh (a * u)) + ∑ x ∈ S, w x * (1 - Real.tanh (x * u))) := by
        rw [mul_add, Finset.mul_sum]
        congr 1
        · ring
        · exact Finset.sum_congr rfl fun x _ => by ring
      rw [e, h, mul_zero]
    have hlim2 : Tendsto
        (fun u : ℝ => w a * (Real.exp (2 * a * u) * (1 - Real.tanh (a * u))) +
          ∑ x ∈ S, w x * (Real.exp (2 * a * u) * (1 - Real.tanh (x * u))))
        atTop (𝓝 (w a * 2 + ∑ x ∈ S, w x * 0)) :=
      ((p1_tendsto_scaled_self a ha_pos).const_mul (w a)).add
        (tendsto_finsetSum S fun x hx =>
          (p1_tendsto_scaled_other a x ha_pos (ha x hx)).const_mul (w x))
    have hwa : w a = 0 := by
      have hzero : Tendsto
          (fun u : ℝ => w a * (Real.exp (2 * a * u) * (1 - Real.tanh (a * u))) +
            ∑ x ∈ S, w x * (Real.exp (2 * a * u) * (1 - Real.tanh (x * u))))
          atTop (𝓝 0) :=
        tendsto_const_nhds.congr (fun u => (hH u).symm)
      have h := tendsto_nhds_unique hzero hlim2
      simp only [mul_zero, Finset.sum_const_zero, add_zero] at h
      linarith
    rcases Finset.mem_insert.mp hs with rfl | hsS
    · exact hwa
    · refine ih w hSpos (fun u => ?_) s hsS
      have h := hsum u
      rw [Finset.sum_insert haS, hwa, zero_mul, zero_add] at h
      exact h

/-- `tanh` is odd. -/
theorem p1_tanh_odd : IsOddPolicy Real.tanh := fun u => Real.tanh_neg u

/-- **Theorem 7.4 for `tanh`**, any number of traders, probes of every size. -/
theorem p1_thm_stress_identification_tanh {K K' : ℕ} (a κ : ℝ) (hκ : κ ≠ 0)
    (c l r : Fin K → ℝ) (c' l' r' : Fin K' → ℝ)
    (hr : ∀ i, 0 ≤ r i) (hr' : ∀ j, 0 ≤ r' j) (hl : ∀ i, l i ≠ 0) (hl' : ∀ j, l' j ≠ 0) :
    (∀ v x, ProbePricePath a κ (satAggFlow Real.tanh c l r) v x →
        ProbePricePath a κ (satAggFlow Real.tanh c' l' r') v x) ↔
      (∀ g : ℝ → ℝ → ℝ, ∑ i, (c i * realSgn (l i)) * g (r i) (|l i|) =
        ∑ j, (c' j * realSgn (l' j)) * g (r' j) (|l' j|)) :=
  p1_thm_stress_identification Real.tanh p1_tanh_odd p1_tanh_indep_dilations a κ hκ c l r c' l' r'
    hr hr' hl hl'

end CurrentMM
