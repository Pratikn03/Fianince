import Mathlib

/-!
# Paper 1, 22 November 2026: deterministic steps of the proofs added to Appendix A

The revision of 22 November 2026 moved the proofs of Theorems `n:questions` and `n:shape`, Proposition
`n:target`(ii) and (iv), Corollary `n:decisionloss` and Theorem `n:disc` into Appendix A. This file checks their
deterministic steps. The probabilistic steps (Gaussian coverage, total variation, Pinsker's inequality, the minimax
exchange, compactness) are on paper and are not claimed here.

* `tax_reduction`, `resting_reduction`: the budget reductions of Proposition `n:target`(iv).
* `no_common_zero`: consecutive members of a three-term recurrence with nonzero coefficients never vanish together
  (used in the proof of Proposition `n:target`(ii): a quadrature node cannot recur as the parameter varies).
* `node_no_recur`: a point that is a node for two parameter values is a common zero of `p_K` and `p_{K-1}`.
* `weight_from_lagrange`: an exact rule integrates the squared Lagrange polynomial to the node's weight.
* `halfwidth_modulus`: the half-width of the affine certificate in Theorem `n:questions`(i).
* `impossible_divergence`: the divergence of the comparison in Theorem `n:questions`(iii).
* `decision_loss_min`: the two-point loss bound of Corollary `n:decisionloss`.
* `absorption`: the absorption step of Theorem `n:shape`.
* `tagged_inversion`: the tagged class-flow coordinates determine weight and memory (Theorem `n:disc`).

Written with AI assistance.
-/

open Finset BigOperators

namespace PublicationRevision13

/-- Proposition `n:target`(iv)(a): removing the share `λ (1 - r_i)` of each activity `q_i` lowers total activity by
`λ` times the first kernel tap `k_0 = Σ q_i (1 - r_i)`. -/
theorem tax_reduction {ι : Type*} (s : Finset ι) (q r : ι → ℝ) (lam : ℝ) :
    ∑ i ∈ s, q i * (lam * (1 - r i)) = lam * ∑ i ∈ s, q i * (1 - r i) := by
  rw [Finset.mul_sum]; refine Finset.sum_congr rfl (fun i _ => by ring)

/-- Proposition `n:target`(iv)(b): removing the share `1 - r_i^h` lowers total activity by the sum of the first `h`
kernel taps `k_m = Σ q_i (1 - r_i) r_i^m`. -/
theorem resting_reduction {ι : Type*} (s : Finset ι) (q r : ι → ℝ) (h : ℕ) :
    ∑ i ∈ s, q i * (1 - r i ^ h) = ∑ m ∈ range h, ∑ i ∈ s, q i * (1 - r i) * r i ^ m := by
  rw [Finset.sum_comm]
  refine Finset.sum_congr rfl (fun i _ => ?_)
  have hg : (∑ m ∈ range h, r i ^ m) * (1 - r i) = 1 - r i ^ h := by
    have := geom_sum_mul (r i) h
    linarith [this]
  rw [← hg, Finset.sum_mul, Finset.mul_sum]
  refine Finset.sum_congr rfl (fun m _ => by ring)

/-- Proposition `n:target`(ii): if `v (k+2) = α k * v (k+1) - γ k * v k` with every `γ k ≠ 0` and `v 0 ≠ 0`, then no two
consecutive terms vanish. Applied to `v k = p_k(s)` for orthogonal polynomials, consecutive polynomials have no common
zero. -/
theorem no_common_zero (v α γ : ℕ → ℝ) (h0 : v 0 ≠ 0) (hγ : ∀ k, γ k ≠ 0)
    (hrec : ∀ k, v (k + 2) = α k * v (k + 1) - γ k * v k) : ∀ k, ¬ (v k = 0 ∧ v (k + 1) = 0) := by
  intro k
  induction k with
  | zero => exact fun h => h0 h.1
  | succ n ih =>
    rintro ⟨h1, h2⟩
    have : γ n * v n = 0 := by have := hrec n; rw [h1, h2] at this; linarith
    rcases mul_eq_zero.mp this with hg | hv
    · exact hγ n hg
    · exact ih ⟨hv, h1⟩

/-- Proposition `n:target`(ii): a point that is a zero of `p_K - c p_{K-1}` for two different values of `c` is a common
zero of `p_K` and `p_{K-1}`; so, by `no_common_zero`, nodes do not recur. -/
theorem node_no_recur (pK pK1 c c' : ℝ) (hc : c ≠ c') (h1 : pK - c * pK1 = 0) (h2 : pK - c' * pK1 = 0) :
    pK1 = 0 ∧ pK = 0 := by
  have h3 : (c' - c) * pK1 = 0 := by linarith
  have hp : pK1 = 0 := by
    rcases mul_eq_zero.mp h3 with h | h
    · exact absurd (by linarith : c = c') hc
    · exact h
  exact ⟨hp, by rw [hp] at h1; linarith⟩

/-- Proposition `n:target`(ii): a rule with weights `w` that integrates `ℓ^2` exactly, where `ℓ` is the Lagrange
polynomial of node `i` (value one at node `i`, zero at the others), gives `∫ ℓ^2 = w i`. -/
theorem weight_from_lagrange {n : ℕ} (w ell : Fin n → ℝ) (i : Fin n) (hi : ell i = 1)
    (hj : ∀ j, j ≠ i → ell j = 0) : ∑ j, w j * ell j ^ 2 = w i := by
  rw [Finset.sum_eq_single i]
  · rw [hi]; ring
  · intro j _ hji; rw [hj j hji]; ring
  · intro h; exact absurd (Finset.mem_univ i) h

/-- Theorem `n:questions`(i), sufficiency: with worst-case bias `W R / 2` and noise half-width `z σ ‖c‖ / √N`, the
half-width is half the modulus objective `δ ‖c‖ + W R` at `δ = 2 z σ / √N`. -/
theorem halfwidth_modulus (W R z σ cn N : ℝ) (hN : 0 < N) :
    W * R / 2 + z * σ * cn / Real.sqrt N = ((2 * z * σ / Real.sqrt N) * cn + W * R) / 2 := by
  have : 0 < Real.sqrt N := Real.sqrt_pos.mpr hN
  field_simp; ring

/-- Theorem `n:questions`(iii): the point mass `c δ_r` with `c = d σ √((1 - r^2)/N)` has taps `c r^m` with squared norm
`c^2 / (1 - r^2)`, so the divergence of the averaged record, `N ‖k‖^2 / (2 σ^2)`, equals `d^2 / 2` for every `r`. -/
theorem impossible_divergence (d σ r N : ℝ) (hσ : 0 < σ) (hN : 0 < N) (hr0 : 0 ≤ r) (hr1 : r < 1) :
    let c := d * σ * Real.sqrt ((1 - r ^ 2) / N)
    N * (c ^ 2 / (1 - r ^ 2)) / (2 * σ ^ 2) = d ^ 2 / 2 := by
  intro c
  have h1 : 0 < 1 - r ^ 2 := by nlinarith
  have hs : Real.sqrt ((1 - r ^ 2) / N) ^ 2 = (1 - r ^ 2) / N := Real.sq_sqrt (by positivity)
  have hc : c ^ 2 = d ^ 2 * σ ^ 2 * ((1 - r ^ 2) / N) := by
    show (d * σ * Real.sqrt ((1 - r ^ 2) / N)) ^ 2 = _
    rw [mul_pow, mul_pow, hs]
  rw [hc]; field_simp

/-- Corollary `n:decisionloss`: the two-point loss is at least `min(b, c)` times half the sum of the two error
probabilities. -/
theorem decision_loss_min (b c p q : ℝ) (hp : 0 ≤ p) (hq : 0 ≤ q) :
    min b c * (p + q) / 2 ≤ (b * p + c * q) / 2 := by
  have h1 : min b c * p ≤ b * p := mul_le_mul_of_nonneg_right (min_le_left b c) hp
  have h2 : min b c * q ≤ c * q := mul_le_mul_of_nonneg_right (min_le_right b c) hq
  linarith

/-- Theorem `n:shape`, absorption: a main term at least `a Δ^(n) x` and a remainder at most `M Δ^(n+1) x` leave at least
`(a/2) Δ^n x` once `Δ ≤ a / (2M)`. -/
theorem absorption (a M Δ x : ℝ) (n : ℕ) (ha : 0 < a) (hM : 0 < M) (hΔ : 0 < Δ) (hx : 0 ≤ x)
    (hsmall : Δ ≤ a / (2 * M)) : a / 2 * Δ ^ n * x ≤ a * Δ ^ n * x - M * Δ ^ (n + 1) * x := by
  have hD : 0 ≤ Δ ^ n * x := mul_nonneg (pow_nonneg hΔ.le n) hx
  have hMΔ : M * Δ ≤ a / 2 := by
    have := mul_le_mul_of_nonneg_left hsmall hM.le
    calc M * Δ ≤ M * (a / (2 * M)) := this
      _ = a / 2 := by field_simp
  have : M * Δ ^ (n + 1) * x = (M * Δ) * (Δ ^ n * x) := by ring
  rw [this]
  have := mul_le_mul_of_nonneg_right hMΔ hD
  nlinarith [this]

/-- Theorem `n:disc`: the first two tagged class-flow coordinates `u₁ = w h₀` and `u₂ = w (h₁ + r h₀)` determine the
weight and the memory when `h₀ ≠ 0` and `w ≠ 0`. -/
theorem tagged_inversion (w r h0 h1 u1 u2 : ℝ) (hh : h0 ≠ 0) (hw : w ≠ 0) (e1 : u1 = w * h0)
    (e2 : u2 = w * (h1 + r * h0)) : w = u1 / h0 ∧ r = (u2 / w - h1) / h0 := by
  constructor
  · rw [e1]; field_simp
  · rw [e2]; field_simp; ring

end PublicationRevision13
