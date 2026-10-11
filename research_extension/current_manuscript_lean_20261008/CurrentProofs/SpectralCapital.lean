import Mathlib.MeasureTheory.Integral.Bochner.Basic
import Mathlib.Algebra.Order.BigOperators.Group.Finset

/-!
# Spectral capital transfer steps (exp14, Theorems IA.1 and IA.2)

Kernel-checked algebraic steps used by the exact minimum-capital results:

* `capital_lower_bound_of_information_ratio`: if information is at most `rho` times the
  execution loss and the test requires information `c`, the loss is at least `c / rho`
  (deterministic probes, Theorem IA.1).
* `expected_loss_lower_bound_of_information_ratio`: the same transfer in expectation for
  adapted/randomised policies (Theorem IA.2), given the pathwise ratio bound.
* `sq_sum_le_cap_mul_abs_sum`: with a per-trade cap `|v_i| ≤ V`, quantity energy is at most
  `V` times gross quantity, which yields the fee lower bound.

Not formalized here (remaining obligations): the Parseval/Toeplitz inequality that supplies
the pathwise ratio `rho = sup |dH|^2 / g`, the KL chain rule with adapted inputs, and the
binary data-processing inequality `KL ≥ kl(alpha, 1 - beta)`.
-/

namespace CurrentMM
noncomputable section
open MeasureTheory

theorem capital_lower_bound_of_information_ratio {info loss rho c : ℝ}
    (hrho : 0 < rho) (hratio : info ≤ rho * loss) (hreq : c ≤ info) :
    c / rho ≤ loss := by
  rw [div_le_iff₀ hrho]
  linarith [mul_comm rho loss]

theorem expected_loss_lower_bound_of_information_ratio {Ω : Type*} [MeasurableSpace Ω]
    (μ : Measure Ω) {X Y : Ω → ℝ} {rho c : ℝ} (hrho : 0 < rho)
    (hX : Integrable X μ) (hY : Integrable Y μ)
    (hratio : ∀ᵐ ω ∂μ, X ω ≤ rho * Y ω) (hreq : c ≤ ∫ ω, X ω ∂μ) :
    c / rho ≤ ∫ ω, Y ω ∂μ := by
  have h1 : ∫ ω, X ω ∂μ ≤ ∫ ω, rho * Y ω ∂μ :=
    integral_mono_ae hX (hY.const_mul rho) hratio
  rw [integral_const_mul] at h1
  exact capital_lower_bound_of_information_ratio hrho h1 hreq

theorem sq_sum_le_cap_mul_abs_sum {n : ℕ} (v : Fin n → ℝ) {V : ℝ}
    (hcap : ∀ i, |v i| ≤ V) :
    ∑ i, v i ^ 2 ≤ V * ∑ i, |v i| := by
  rw [Finset.mul_sum]
  apply Finset.sum_le_sum
  intro i _
  have hsq : v i ^ 2 = |v i| * |v i| := by
    rw [← sq_abs]
    ring
  rw [hsq]
  exact mul_le_mul_of_nonneg_right (hcap i) (abs_nonneg _)

end
end CurrentMM
