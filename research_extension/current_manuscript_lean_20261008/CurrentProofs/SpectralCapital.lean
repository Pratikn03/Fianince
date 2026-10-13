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

theorem rayleigh_holder_total_loss_lower_bound {c lam_max loss_quad c_fee l1_min l1_norm : ℝ}
    (hlam : 0 < lam_max) (hquad : c ≤ lam_max * loss_quad)
    (hfee_nonneg : 0 ≤ c_fee) (hl1 : l1_min ≤ l1_norm) :
    c / lam_max + c_fee * l1_min ≤ loss_quad + c_fee * l1_norm := by
  have hq : c / lam_max ≤ loss_quad :=
    capital_lower_bound_of_information_ratio hlam hquad (le_refl c)
  have hf : c_fee * l1_min ≤ c_fee * l1_norm :=
    mul_le_mul_of_nonneg_left hl1 hfee_nonneg
  linarith

theorem lecam_two_point_moment_matched_cubic_gap (q tau eta_bar d_eta : ℝ)
    (hq : q ≠ 0) :
    let p_minus := (1 : ℝ) / 2 - tau / q
    let p_plus := (1 : ℝ) / 2 + tau / q
    let w0_1 := q * p_minus
    let w0_2 := q * p_plus
    let eta0_1 := eta_bar - p_plus * d_eta
    let eta0_2 := eta_bar + p_minus * d_eta
    let w1_1 := q * p_plus
    let w1_2 := q * p_minus
    let eta1_1 := eta_bar - p_minus * d_eta
    let eta1_2 := eta_bar + p_plus * d_eta
    (w1_1 * eta1_1 + w1_2 * eta1_2) - (w0_1 * eta0_1 + w0_2 * eta0_2) = 0 ∧
    (w1_1 * eta1_1 ^ 2 + w1_2 * eta1_2 ^ 2) - (w0_1 * eta0_1 ^ 2 + w0_2 * eta0_2 ^ 2) = 0 ∧
    (w1_1 * eta1_1 ^ 3 + w1_2 * eta1_2 ^ 3) - (w0_1 * eta0_1 ^ 3 + w0_2 * eta0_2 ^ 3) =
      4 * tau * p_minus * p_plus * d_eta ^ 3 := by
  dsimp only
  refine ⟨?_, ?_, ?_⟩
  · field_simp [hq]; ring
  · field_simp [hq]; ring
  · field_simp [hq]; ring

theorem kreiss_resolvent_guard_solvency_invariance {alpha gain_MC u_norm reserve B_maint drawdown : ℝ}
    (hres : 0 < reserve)
    (hdraw : drawdown ≤ alpha * gain_MC * u_norm)
    (hguard : alpha * gain_MC * u_norm + reserve ≤ B_maint) :
    drawdown < B_maint := by
  linarith

end
end CurrentMM

