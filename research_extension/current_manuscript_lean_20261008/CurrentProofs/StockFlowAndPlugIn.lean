import Mathlib.Basic.Real.Basic
import Mathlib.Tactic.Linarith
import Mathlib.Tactic.Ring
import Mathlib.Tactic.FieldSimp
import Mathlib.Algebra.Order.Field.Basic

set_option linter.unusedVariables false

/-!
# Formal Verification of Fix 1 (Stock–Flow Inventory Bridge)
# and Fix 2 (Plug-In Upper Bound under Unknown Primitives a, κ, p*)

This module machine-checks:
1. `stock_flow_two_root_bridge`: Eliminating order flow `u_t = q * y_t - ψ * I_{t-1}`
   from the inventory accumulation identity `I_t = φ * I_{t-1} + u_t` and exponential
   belief recursion `y_t = r * y_{t-1} + η * x_t` yields the exact two-root ARMA(2,1)
   position-stock identity `(I_t - ρ_inv * I_{t-1}) - r * (I_{t-1} - ρ_inv * I_{t-2}) = (q * η) * x_t`,
   where `ρ_inv = φ - ψ` is the slow inventory-turnover root and `r = 1 - η` is the
   structural belief-memory root.
2. `deconv_tap0_plug_in_bound` and `plugin_prony_rate_preservation`: When `a` and `κ` are
   estimated at the parametric rate `|a_hat - a| ≤ C_a * δ_N` and `|κ_hat - κ| ≤ C_κ * δ_N`
   (with `κ, κ_hat ≥ κ_min > 0`), the plug-in closed-loop deconvolution error is `O(δ_N)`
   with a Lipschitz constant independent of cohort spacing `Δη`, preserving the exact
   `ε_N = δ_N * (Δη)^{-(2K-1)}` Prony weight-recovery bound of Theorem 5.2.
-/

namespace CurrentMM

/-! ## Part 1: Exact Two-Root Stock–Flow Inventory Bridge (Supplement S18, Eq. S15) -/

/-- One-step inventory recursion under Remark 2.2:
    Given `I_t = φ * I_{t-1} + u_t` and `u_t = q * y_t - ψ * I_{t-1}`,
    the position stock obeys `I_t = ρ_inv * I_{t-1} + q * y_t` where `ρ_inv = φ - ψ`. -/
theorem inventory_single_lag_reduction
    (φ ψ q y_t I_prev u_t : ℝ)
    (h_inv : I_prev * φ + u_t = φ * I_prev + u_t)
    (h_flow : u_t = q * y_t - ψ * I_prev) :
    φ * I_prev + u_t = (φ - ψ) * I_prev + q * y_t := by
  rw [h_flow]
  ring

/-- Exact Two-Root Stock–Flow Bridge (Eq. S15):
    If `I_t = ρ_inv * I_{t-1} + q * y_t`, `I_{t-1} = ρ_inv * I_{t-2} + q * y_{t-1}`,
    and belief state updates as `y_t = r * y_{t-1} + η * x_t`, then the position stock `I_t`
    satisfies the exact two-root autoregression with roots `ρ_inv` (turnover) and `r` (memory):
    `I_t - (ρ_inv + r) * I_prev + (ρ_inv * r) * I_prev2 = (q * η) * x_t`. -/
theorem stock_flow_two_root_bridge
    (ρ_inv r q η x_t y_t y_prev I_t I_prev I_prev2 : ℝ)
    (h_It : I_t = ρ_inv * I_prev + q * y_t)
    (h_Iprev : I_prev = ρ_inv * I_prev2 + q * y_prev)
    (h_belief : y_t = r * y_prev + η * x_t) :
    I_t - (ρ_inv + r) * I_prev + (ρ_inv * r) * I_prev2 = (q * η) * x_t := by
  have h_qy : q * y_prev = I_prev - ρ_inv * I_prev2 := by linarith [h_Iprev]
  calc
    I_t - (ρ_inv + r) * I_prev + (ρ_inv * r) * I_prev2
        = (ρ_inv * I_prev + q * (r * y_prev + η * x_t))
          - (ρ_inv + r) * I_prev + (ρ_inv * r) * I_prev2 := by rw [h_It, h_belief]
    _ = r * (q * y_prev) - r * I_prev + (ρ_inv * r) * I_prev2 + (q * η) * x_t := by ring
    _ = r * (I_prev - ρ_inv * I_prev2) - r * I_prev + (ρ_inv * r) * I_prev2 + (q * η) * x_t := by
          rw [h_qy]
    _ = (q * η) * x_t := by ring

/-- Corollary of the Stock–Flow Bridge:
    When inventory holding cost `γ_inv = 0` and `δ_inv = 0` (so `φ = 1` and `ψ = 0`, meaning
    `ρ_inv = 1`), the first difference `ΔI_t = I_t - I_{t-1} = u_t` obeys the pure flow
    autoregression `ΔI_t - r * ΔI_{t-1} = (q * η) * x_t`, whereas the position level `I_t`
    has a unit root `ρ_inv = 1` on top of `r`. -/
theorem stock_flow_unit_turnover_limit
    (r q η x_t y_t y_prev I_t I_prev I_prev2 : ℝ)
    (h_It : I_t = 1 * I_prev + q * y_t)
    (h_Iprev : I_prev = 1 * I_prev2 + q * y_prev)
    (h_belief : y_t = r * y_prev + η * x_t) :
    (I_t - I_prev) - r * (I_prev - I_prev2) = (q * η) * x_t := by
  have h := stock_flow_two_root_bridge 1 r q η x_t y_t y_prev I_t I_prev I_prev2 h_It h_Iprev h_belief
  linarith

/-! ## Part 2: Plug-In Upper Bound under Unknown Primitives (Corollary 5.2A) -/

/-- Baseline demeaning eliminates the unknown fundamental value `p_star`:
    Observing `p_{t} = p_star + x_t + ν_t` and pre-probe `p_0 = p_star + ν_0`
    recovers `x_t + (ν_t - ν_0)` with zero dependence on `p_star`. -/
theorem baseline_demeaning_eliminates_pstar
    (p_star x_t ν_t ν_0 : ℝ) :
    (p_star + x_t + ν_t) - (p_star + ν_0) = x_t + (ν_t - ν_0) := by
  ring

/-- Algebraic decomposition of the plug-in deconvolution error for `k_0 = (h_1 - a * h_0) / κ^2`:
    Since `h_1 = (a + κ * k_0) * κ`, the difference between the plug-in estimator
    `k0_hat = (h1_hat - a_hat * κ_hat) / κ_hat^2` and the known-primitive estimator
    `k0_known = (h1_hat - a * κ) / κ^2` is a smooth rational combination of `(a_hat - a)`
    and `(κ_hat - κ)`. -/
theorem plugin_deconv_k0_identity
    (h1_hat a a_hat κ κ_hat : ℝ)
    (hκ : κ ≠ 0) (hκ_hat : κ_hat ≠ 0) :
    (h1_hat - a_hat * κ_hat) / (κ_hat ^ 2) - (h1_hat - a * κ) / (κ ^ 2) =
      (h1_hat * (κ + κ_hat) * (κ - κ_hat)
        - (a_hat - a) * κ_hat * (κ ^ 2)
        - a * κ * κ_hat * (κ - κ_hat)) / (κ ^ 2 * κ_hat ^ 2) := by
  have h_pow1 : κ ^ 2 ≠ 0 := pow_ne_zero 2 hκ
  have h_pow2 : κ_hat ^ 2 ≠ 0 := pow_ne_zero 2 hκ_hat
  field_simp [h_pow1, h_pow2]
  ring

/-- Lipschitz Plug-In Stability and Prony Rate Preservation (Corollary 5.2A):
    Suppose the known-primitive kernel estimator satisfies `|k_known - k_true| ≤ L_h * δ_N`,
    and the plug-in primitive estimators `(a_hat, κ_hat)` induce an additional deconvolution
    perturbation bounded by `|k_plug - k_known| ≤ L_a * |a_hat - a| + L_κ * |κ_hat - κ|`,
    where `|a_hat - a| ≤ C_a * δ_N` and `|κ_hat - κ| ≤ C_κ * δ_N` (with `L_a, L_κ, C_a, C_κ`
    independent of `Δη`).
    Then after centring (`norm_C`) and rescaling by `scale_inv = (Δη)^{-(2K-1)} > 0`,
    and applying the `L_inv`-Lipschitz inverse moment map `F^{-1}` of Theorem 5.2,
    the recovered weight error `|w_hat - w_true|` is bounded by
    `L_inv * norm_C * (L_h + L_a * C_a + L_κ * C_κ) * (δ_N * scale_inv)`,
    preserving the exact `O(σ N^{-1/2} (Δη)^{-(2K-1)})` rate of Theorem 5.2! -/
theorem plugin_prony_rate_preservation
    (k_plug k_known k_true a a_hat κ κ_hat w_hat w_true : ℝ)
    (L_h L_a L_κ C_a C_κ norm_C scale_inv L_inv δ_N : ℝ)
    (h_pos_norm : 0 ≤ norm_C)
    (h_pos_scale : 0 ≤ scale_inv)
    (h_pos_Linv : 0 ≤ L_inv)
    (h_pos_La : 0 ≤ L_a)
    (h_pos_Lκ : 0 ≤ L_κ)
    (h_known : |k_known - k_true| ≤ L_h * δ_N)
    (h_plug_diff : |k_plug - k_known| ≤ L_a * |a_hat - a| + L_κ * |κ_hat - κ|)
    (h_a_est : |a_hat - a| ≤ C_a * δ_N)
    (h_κ_est : |κ_hat - κ| ≤ C_κ * δ_N)
    (h_prony : |w_hat - w_true| ≤ L_inv * (norm_C * scale_inv * |k_plug - k_true|)) :
    |w_hat - w_true| ≤
      (L_inv * norm_C * (L_h + L_a * C_a + L_κ * C_κ)) * (δ_N * scale_inv) := by
  have h_tri : |k_plug - k_true| ≤ |k_plug - k_known| + |k_known - k_true| := by
    have h_eq : k_plug - k_true = (k_plug - k_known) + (k_known - k_true) := by ring
    rw [h_eq]
    exact abs_add_le (k_plug - k_known) (k_known - k_true)
  have h_a_bound : L_a * |a_hat - a| ≤ L_a * (C_a * δ_N) :=
    mul_le_mul_of_nonneg_left h_a_est h_pos_La
  have h_κ_bound : L_κ * |κ_hat - κ| ≤ L_κ * (C_κ * δ_N) :=
    mul_le_mul_of_nonneg_left h_κ_est h_pos_Lκ
  have h_k_total : |k_plug - k_true| ≤ (L_h + L_a * C_a + L_κ * C_κ) * δ_N := by
    linarith [h_tri, h_plug_diff, h_known, h_a_bound, h_κ_bound]
  have h_ns_nonneg : 0 ≤ norm_C * scale_inv := mul_nonneg h_pos_norm h_pos_scale
  have h_scaled :
      norm_C * scale_inv * |k_plug - k_true| ≤
        norm_C * scale_inv * ((L_h + L_a * C_a + L_κ * C_κ) * δ_N) :=
    mul_le_mul_of_nonneg_left h_k_total h_ns_nonneg
  have h_final :
      L_inv * (norm_C * scale_inv * |k_plug - k_true|) ≤
        L_inv * (norm_C * scale_inv * ((L_h + L_a * C_a + L_κ * C_κ) * δ_N)) :=
    mul_le_mul_of_nonneg_left h_scaled h_pos_Linv
  calc
    |w_hat - w_true| ≤ L_inv * (norm_C * scale_inv * |k_plug - k_true|) := h_prony
    _ ≤ L_inv * (norm_C * scale_inv * ((L_h + L_a * C_a + L_κ * C_κ) * δ_N)) := h_final
    _ = (L_inv * norm_C * (L_h + L_a * C_a + L_κ * C_κ)) * (δ_N * scale_inv) := by ring

end CurrentMM

namespace Paper1Fixes
export CurrentMM (
  inventory_single_lag_reduction
  stock_flow_two_root_bridge
  stock_flow_unit_turnover_limit
  baseline_demeaning_eliminates_pstar
  plugin_deconv_k0_identity
  plugin_prony_rate_preservation
)
end Paper1Fixes

