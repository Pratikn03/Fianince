import Mathlib.Analysis.SpecialFunctions.Sqrt
import Mathlib.Analysis.SpecialFunctions.Pow.Real
import Mathlib.Algebra.BigOperators.Group.Finset.Basic
import Mathlib.Algebra.Order.BigOperators.Group.Finset
import Mathlib.Tactic.FieldSimp
import Mathlib.Tactic.Positivity
import Mathlib.Tactic.Linarith
import Mathlib.Tactic.Ring
import Mathlib.Algebra.BigOperators.Field
import Mathlib.Algebra.Order.Field.Basic

/-! Paper 1, revision 19 (27 November 2026): deterministic steps of Theorem 7.12 (more data does not substitute
for records). The value-of-information inequality is checked for finite record spaces; the probabilistic steps
(Pinsker's inequality, the crowding bound of Theorem 7.11(ii)) are taken as hypotheses and proved on paper. -/

namespace Paper1Revision19

open Finset

/-- Value of information is at most total variation times the full-information gain, on a finite record space.
`a = min(p0, p1)`, `d0 = p0 - a`, `d1 = p1 - a` (each of mass `t`, the total variation), `w0, w1` the welfare of
the policy chosen at each record in states 0 and 1, `Wn` the best no-information welfare. -/
theorem voi_le_tv_mul_gain {ι : Type*} (s : Finset ι) (a d0 d1 w0 w1 : ι → ℝ) (t Wn W0 W1 : ℝ)
    (ha : ∀ i ∈ s, 0 ≤ a i) (hd0 : ∀ i ∈ s, 0 ≤ d0 i) (hd1 : ∀ i ∈ s, 0 ≤ d1 i)
    (hsa : ∑ i ∈ s, a i = 1 - t) (hs0 : ∑ i ∈ s, d0 i = t) (hs1 : ∑ i ∈ s, d1 i = t)
    (hw0 : ∀ i ∈ s, w0 i ≤ W0) (hw1 : ∀ i ∈ s, w1 i ≤ W1)
    (hwn : ∀ i ∈ s, (w0 i + w1 i) / 2 ≤ Wn) :
    (∑ i ∈ s, (a i + d0 i) * w0 i + ∑ i ∈ s, (a i + d1 i) * w1 i) / 2
      ≤ Wn + t * ((W0 + W1) / 2 - Wn) := by
  have h1 : ∑ i ∈ s, a i * ((w0 i + w1 i) / 2) ≤ ∑ i ∈ s, a i * Wn :=
    Finset.sum_le_sum fun i hi => mul_le_mul_of_nonneg_left (hwn i hi) (ha i hi)
  have h2 : ∑ i ∈ s, d0 i * w0 i ≤ ∑ i ∈ s, d0 i * W0 :=
    Finset.sum_le_sum fun i hi => mul_le_mul_of_nonneg_left (hw0 i hi) (hd0 i hi)
  have h3 : ∑ i ∈ s, d1 i * w1 i ≤ ∑ i ∈ s, d1 i * W1 :=
    Finset.sum_le_sum fun i hi => mul_le_mul_of_nonneg_left (hw1 i hi) (hd1 i hi)
  have e1 : ∑ i ∈ s, a i * Wn = (1 - t) * Wn := by rw [← Finset.sum_mul, hsa]
  have e2 : ∑ i ∈ s, d0 i * W0 = t * W0 := by rw [← Finset.sum_mul, hs0]
  have e3 : ∑ i ∈ s, d1 i * W1 = t * W1 := by rw [← Finset.sum_mul, hs1]
  have key : (∑ i ∈ s, (a i + d0 i) * w0 i + ∑ i ∈ s, (a i + d1 i) * w1 i) / 2
      = ∑ i ∈ s, a i * ((w0 i + w1 i) / 2) + (∑ i ∈ s, d0 i * w0 i) / 2 + (∑ i ∈ s, d1 i * w1 i) / 2 := by
    have : ∑ i ∈ s, a i * ((w0 i + w1 i) / 2)
        = (∑ i ∈ s, a i * w0 i + ∑ i ∈ s, a i * w1 i) / 2 := by
      rw [← Finset.sum_add_distrib, Finset.sum_div]
      refine Finset.sum_congr rfl fun i _ => by ring
    rw [this]
    simp only [add_mul, Finset.sum_add_distrib]
    ring
  rw [key]
  nlinarith [h1, h2, h3, e1, e2, e3]

/-- Benchmark `n = 4`: the crowding bound `δ*² ≤ 4k²δ₀²/(L²β²cN)` of Theorem 7.11(ii) gives the divergence bound
`J* = cNδ*⁴ ≤ 16k⁴δ₀⁴/(L⁴β⁴cN)`. -/
theorem crowding_divergence_bound (c N d k δ0 L β : ℝ) (hc : 0 < c) (hN : 0 < N) (hL : 0 < L) (hβ : 0 < β)
    (h : d ^ 2 ≤ 4 * k ^ 2 * δ0 ^ 2 / (L ^ 2 * β ^ 2 * c * N)) :
    c * N * d ^ 4 ≤ 16 * k ^ 4 * δ0 ^ 4 / (L ^ 4 * β ^ 4 * c * N) := by
  have h0 : 0 ≤ d ^ 2 := sq_nonneg d
  have hsq : (d ^ 2) ^ 2 ≤ (4 * k ^ 2 * δ0 ^ 2 / (L ^ 2 * β ^ 2 * c * N)) ^ 2 := pow_le_pow_left₀ h0 h 2
  have hcN : 0 < c * N := mul_pos hc hN
  have hd4 : d ^ 4 = (d ^ 2) ^ 2 := by ring
  rw [hd4]
  calc c * N * (d ^ 2) ^ 2 ≤ c * N * (4 * k ^ 2 * δ0 ^ 2 / (L ^ 2 * β ^ 2 * c * N)) ^ 2 :=
        mul_le_mul_of_nonneg_left hsq hcN.le
    _ = 16 * k ^ 4 * δ0 ^ 4 / (L ^ 4 * β ^ 4 * c * N) := by
        field_simp
        ring

/-- The Pinsker step in closed form: if `J ≤ 16k⁴δ₀⁴/(L⁴β⁴cN)` then `√(J/2) ≤ 2√2 k²δ₀²/(L²β²√(cN))`. -/
theorem tv_bound_from_divergence (c N J k δ0 L β : ℝ) (hc : 0 < c) (hN : 0 < N) (hL : 0 < L) (hβ : 0 < β)
    (hJ : J ≤ 16 * k ^ 4 * δ0 ^ 4 / (L ^ 4 * β ^ 4 * c * N)) :
    Real.sqrt (J / 2) ≤ 2 * Real.sqrt 2 * k ^ 2 * δ0 ^ 2 / (L ^ 2 * β ^ 2 * Real.sqrt (c * N)) := by
  have hcN : 0 < c * N := mul_pos hc hN
  have hs : 0 < Real.sqrt (c * N) := Real.sqrt_pos.mpr hcN
  have hR : 0 ≤ 2 * Real.sqrt 2 * k ^ 2 * δ0 ^ 2 / (L ^ 2 * β ^ 2 * Real.sqrt (c * N)) := by positivity
  rw [Real.sqrt_le_left]
  swap
  · exact hR
  · have h2 : Real.sqrt 2 ^ 2 = 2 := Real.sq_sqrt (by norm_num)
    have hcs : Real.sqrt (c * N) ^ 2 = c * N := Real.sq_sqrt hcN.le
    have hsq : (2 * Real.sqrt 2 * k ^ 2 * δ0 ^ 2 / (L ^ 2 * β ^ 2 * Real.sqrt (c * N))) ^ 2
        = 8 * k ^ 4 * δ0 ^ 4 / (L ^ 4 * β ^ 4 * (c * N)) := by
      rw [div_pow, mul_pow, mul_pow, mul_pow, mul_pow, mul_pow, h2, hcs]
      ring
    rw [hsq]
    have : J / 2 ≤ 16 * k ^ 4 * δ0 ^ 4 / (L ^ 4 * β ^ 4 * c * N) / 2 := by linarith
    calc J / 2 ≤ 16 * k ^ 4 * δ0 ^ 4 / (L ^ 4 * β ^ 4 * c * N) / 2 := this
      _ = 8 * k ^ 4 * δ0 ^ 4 / (L ^ 4 * β ^ 4 * (c * N)) := by ring

/-- Record choice: if `N > A²V²/(c(V−F)²)` with `A, c > 0` and `F < V`, then `A V/√(cN) < V − F`, so a trail
costing `F` beats every price-record targeting whose value is bounded by `A V/√(cN)`. -/
theorem trail_beats_prices (A V F c N : ℝ) (hA : 0 < A) (hc : 0 < c) (hFV : F < V) (hV : 0 < V)
    (hN : A ^ 2 * V ^ 2 / (c * (V - F) ^ 2) < N) :
    A * V / Real.sqrt (c * N) < V - F := by
  have hVF : 0 < V - F := by linarith
  have hpos : 0 < A ^ 2 * V ^ 2 / (c * (V - F) ^ 2) := by positivity
  have hN0 : 0 < N := lt_trans hpos hN
  have hcN : 0 < c * N := mul_pos hc hN0
  have hs : 0 < Real.sqrt (c * N) := Real.sqrt_pos.mpr hcN
  have hlt : A * V / (V - F) < Real.sqrt (c * N) := by
    rw [Real.lt_sqrt (by positivity)]
    have : (A * V / (V - F)) ^ 2 = c * (A ^ 2 * V ^ 2 / (c * (V - F) ^ 2)) := by
      field_simp
    rw [this]
    exact mul_lt_mul_of_pos_left hN hc
  rw [div_lt_iff₀ hs]
  calc A * V = A * V / (V - F) * (V - F) := by field_simp
    _ < Real.sqrt (c * N) * (V - F) := mul_lt_mul_of_pos_right hlt hVF
    _ = (V - F) * Real.sqrt (c * N) := by ring

end Paper1Revision19
