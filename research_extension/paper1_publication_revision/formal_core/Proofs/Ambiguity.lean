import Init.GrindInstances.Ring.Rat

namespace MachineMarkets

/-!
# Theorem 3.3: Exact Finite-Window Ambiguity Witness
Mechanized proof of the existence of a stable and an unstable market model
with identical parameters, identical response normalizations, and identical
price responses up to lag K+1 (t = 3), diverging strictly at lag t = 4.
-/

/-- Stable Model 0 parameters (Table 2). -/
def q0_1 : Rat := 0
def q0_2 : Rat := 12/65
def q0_3 : Rat := 0

/-- Unstable Model 1 parameters (Table 2). -/
def q1_1 : Rat := 54/1235
def q1_2 : Rat := 0
def q1_3 : Rat := 240/247

/-- Common learning rates for the three memory states. -/
def eta_1 : Rat := 1
def eta_2 : Rat := 1/2
def eta_3 : Rat := 1/20

/-- Market price persistence. -/
def a_market : Rat := 2/5

/-- Aggregate feedback mass Q = sum q_i. -/
def Q0 : Rat := q0_1 + q0_2 + q0_3
def Q1 : Rat := q1_1 + q1_2 + q1_3

/-- Model 0 is Schur stable: Q0 < 1 - a = 3/5. -/
theorem model0_is_stable : Q0 = 12/65 ∧ Q0 < 1 - a_market := by
  unfold Q0 q0_1 q0_2 q0_3 a_market
  decide +kernel

/-- Model 1 is strictly unstable: Q1 > 1 - a = 3/5. -/
theorem model1_is_unstable : Q1 = 66/65 ∧ Q1 > 1 - a_market := by
  unfold Q1 q1_1 q1_2 q1_3 a_market
  decide +kernel

/-- Open-loop memory impulse kernels: k_j = sum q_i * eta_i * (1 - eta_i)^j. -/
def k0_mod0 : Rat := q0_1 * eta_1 + q0_2 * eta_2 + q0_3 * eta_3
def k0_mod1 : Rat := q1_1 * eta_1 + q1_2 * eta_2 + q1_3 * eta_3

theorem kernel_lag0_identical : k0_mod0 = k0_mod1 ∧ k0_mod0 = 6/65 := by
  unfold k0_mod0 k0_mod1 q0_1 q0_2 q0_3 q1_1 q1_2 q1_3 eta_1 eta_2 eta_3
  decide +kernel

def k1_mod0 : Rat := q0_1 * eta_1 * (1 - eta_1) + q0_2 * eta_2 * (1 - eta_2) + q0_3 * eta_3 * (1 - eta_3)
def k1_mod1 : Rat := q1_1 * eta_1 * (1 - eta_1) + q1_2 * eta_2 * (1 - eta_2) + q1_3 * eta_3 * (1 - eta_3)

theorem kernel_lag1_identical : k1_mod0 = k1_mod1 ∧ k1_mod0 = 3/65 := by
  unfold k1_mod0 k1_mod1 q0_1 q0_2 q0_3 q1_1 q1_2 q1_3 eta_1 eta_2 eta_3
  decide +kernel

/-- At lag j = 2, the memory kernels diverge. -/
def k2_mod0 : Rat := q0_1 * eta_1 * (1 - eta_1)^2 + q0_2 * eta_2 * (1 - eta_2)^2 + q0_3 * eta_3 * (1 - eta_3)^2
def k2_mod1 : Rat := q1_1 * eta_1 * (1 - eta_1)^2 + q1_2 * eta_2 * (1 - eta_2)^2 + q1_3 * eta_3 * (1 - eta_3)^2

theorem kernel_lag2_diverges : k2_mod0 ≠ k2_mod1 := by
  unfold k2_mod0 k2_mod1 q0_1 q0_2 q0_3 q1_1 q1_2 q1_3 eta_1 eta_2 eta_3
  decide +kernel

/-- Closed-loop price impulse responses h_t:
    h_0 = 1, h_1 = a, h_{t+1} = a*h_t + sum_{j=0}^{t-1} k_j * h_{t-1-j}. -/
def h0 : Rat := 1
def h1 : Rat := a_market
def h2 : Rat := a_market * h1 + k0_mod0 * h0
def h3 : Rat := a_market * h2 + k0_mod0 * h1 + k1_mod0 * h0

theorem price_response_lag2_eval : h2 = 82/325 := by
  unfold h2 h1 h0 a_market k0_mod0 q0_1 q0_2 q0_3 eta_1 eta_2 eta_3
  decide +kernel

theorem price_response_lag3_eval : h3 = 23/125 := by
  unfold h3 h2 h1 h0 a_market k0_mod0 k1_mod0 q0_1 q0_2 q0_3 eta_1 eta_2 eta_3
  decide +kernel

/-- Divergence at lag t = 4: despite sharing identical price responses h0, h1, h2, h3,
    the stable and unstable models produce distinct price responses at t = 4. -/
def h4_mod0 : Rat := a_market * h3 + k0_mod0 * h2 + k1_mod0 * h1 + k2_mod0 * h0
def h4_mod1 : Rat := a_market * h3 + k0_mod1 * h2 + k1_mod1 * h1 + k2_mod1 * h0

theorem price_response_lag4_diverges : h4_mod0 ≠ h4_mod1 := by
  unfold h4_mod0 h4_mod1 h3 h2 h1 h0 a_market k0_mod0 k1_mod0 k2_mod0 k0_mod1 k1_mod1 k2_mod1
  unfold q0_1 q0_2 q0_3 q1_1 q1_2 q1_3 eta_1 eta_2 eta_3
  decide +kernel

theorem price_response_lag4_difference :
    h4_mod1 - h4_mod0 = 27 / 1300 := by
  unfold h4_mod0 h4_mod1 h3 h2 h1 h0 a_market k0_mod0 k1_mod0 k2_mod0 k0_mod1 k1_mod1 k2_mod1
  unfold q0_1 q0_2 q0_3 q1_1 q1_2 q1_3 eta_1 eta_2 eta_3
  decide +kernel

end MachineMarkets
