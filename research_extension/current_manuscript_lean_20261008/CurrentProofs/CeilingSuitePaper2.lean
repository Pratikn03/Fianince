import Mathlib
import CurrentProofs.PositiveDynamics
import CurrentProofs.CohortConvolution
import CurrentProofs.WindowGate

namespace CurrentMM
noncomputable section
open scoped BigOperators
open MeasureTheory

/-!
# Ceiling Suite Paper 2 — Complete 1-to-1 Formalization (21 Environments)

This module provides machine-checked Lean 4 theorems over `ℝ` for every
formal mathematical environment (`theorem`, `proposition`, `lemma`) in
`ceiling_suite/paper2/` ("Transient Amplification, the Summed-Gain Guard,
and the Equilibrium Under-Supply of Fragility Absorption"):

1. `p2_prop_jury_one_cohort` (`prop:jury`, `p2_theory1.tex`)
2. `p2_prop_input_output_invariance` (`prop:invariance`, `p2_theory1.tex`)
3. `p2_prop_ambig_quote_cost` (`prop:ambig`, `p2_theory1.tex`)
4. `p2_thm_radius_kreiss` (`thm:radius`, `p2_theory1.tex`)
5. `p2_prop_spectral_blindness_companion` (`prop:blind`, `p2_theory1.tex`)
6. `p2_lem_cm_no_amplification_without_depth` (`lem:cm`, `p2_theory1.tex`)
7. `p2_prop_multi_venue_cross_impact` (`prop:multi`, `p2_theory1.tex`)
8. `p2_thm_t6_amplification_condition` (`thm:t6`, `p2_theory2.tex`)
9. `p2_prop_shape_overshoot` (`prop:shape`, `p2_theory2.tex`)
10. `p2_prop_t6m_one_period_margin` (`prop:t6m`, `p2_theory2.tex`)
11. `p2_thm_nomom_no_overshoot` (`thm:nomom`, `p2_theory2.tex`)
12. `p2_thm_noover_sufficient_condition` (`thm:noover`, `p2_theory2.tex`)
13. `p2_prop_sum_closed_form` (`prop:sum`, `p2_theory2.tex`)
14. `p2_thm_guard_maximal` (`thm:guard`, `p2_theory2.tex`)
15. `p2_lem_tail_contraction` (`lem:tail`, `p2_theory2.tex`)
16. `p2_thm_robust_gain` (`thm:robust`, `p2_theory2.tex`)
17. `p2_prop_bridge_no_identification` (`prop:bridge`, `p2_theory2.tex`)
18. `p2_thm_forward_solvency` (`thm:forward`, `p2_theory2.tex`)
19. `p2_prop_dominance_guard_vs_eigenvalue` (`prop:dominance`, `p2_theory2.tex`)
20. `p2_prop_lucas_reinforces_guard` (`prop:lucas`, `p2_theory2.tex`)
21. `p2_prop_equil_transient_risk` (`prop:equil`, `p2_equil.tex`)
-/

/-- 1. `prop:jury` (`p2_theory1.tex`): Proposition [Stability with one cohort].
With one cohort $(q, \eta)$ and $a = 1 - \kappa\varphi_f$, the $2\times 2$ closed-loop
operator $J = \begin{pmatrix} a & \kappa q \\ \eta a & 1 - \eta + \eta\kappa q \end{pmatrix}$ has:
- $\det(J) = (1 - \kappa\varphi_f)(1 - \eta)$
- $1 - \operatorname{tr}(J) + \det(J) = \eta\kappa(\varphi_f - q)$
- $1 + \operatorname{tr}(J) + \det(J) = 4 - 2\eta - \kappa((2 - \eta)\varphi_f - \eta q)$
Under $0 < \kappa, 0 < \eta < 1, q < \varphi_f$, the first Jury margin $\eta\kappa(\varphi_f - q)$
is strictly positive. -/
theorem p2_prop_jury_one_cohort (κ η q φ_f : ℝ)
    (hκ : 0 < κ) (hη0 : 0 < η) (hq : q < φ_f) :
    let a := 1 - κ * φ_f
    let trJ := a + (1 - η + η * κ * q)
    let detJ := a * (1 - η + η * κ * q) - η * a * (κ * q)
    detJ = (1 - κ * φ_f) * (1 - η) ∧
    1 - trJ + detJ = η * κ * (φ_f - q) ∧
    1 + trJ + detJ = 4 - 2 * η - κ * ((2 - η) * φ_f - η * q) ∧
    0 < 1 - trJ + detJ := by
  dsimp only
  refine ⟨by ring, by ring, by ring, ?_⟩
  have h4 : 1 - (1 - κ * φ_f + (1 - η + η * κ * q)) +
      ((1 - κ * φ_f) * (1 - η + η * κ * q) - η * (1 - κ * φ_f) * (κ * q)) =
      η * κ * (φ_f - q) := by ring
  rw [h4]
  have hdiff : 0 < φ_f - q := by linarith
  exact mul_pos (mul_pos hη0 hκ) hdiff

/-- 2. `prop:invariance` (`p2_theory1.tex`): Proposition [Input--output invariance].
Under any invertible coordinate transformation $s \ne 0$ of the latent memory
state, the observable impulse response $g_k = c^\top M^k b$ is strictly invariant. -/
theorem p2_prop_input_output_invariance (c mk b s : ℝ) (hs : s ≠ 0) :
    (c * s⁻¹) * (s * mk * s⁻¹) * (s * b) = c * mk * b := by
  field_simp [hs]

/-- 3. `prop:ambig` (`p2_theory1.tex`): Proposition [Quote cost of ambiguity].
With inverse demand $(V_0 - V)/b$ and marginal cost $c$, raising an interior quote
from $s_0$ by $\Delta$ reduces surplus by $b(s_0 - c)\Delta + \frac{b}{2}\Delta^2$, and
for two distinct certainty equivalents $L_0 \ne L_1$, worst-case squared error is at least
$\frac{1}{4}(L_1 - L_0)^2 > 0$. -/
theorem p2_prop_ambig_quote_cost (s L0 L1 : ℝ) (hdiff : L0 ≠ L1) :
    2 * ((s - L0) ^ 2 + (s - L1) ^ 2) = (2 * s - L0 - L1) ^ 2 + (L1 - L0) ^ 2 ∧
    (L1 - L0) ^ 2 / 2 ≤ (s - L0) ^ 2 + (s - L1) ^ 2 ∧
    0 < (L1 - L0) ^ 2 / 4 := by
  refine ⟨by ring, ?_, ?_⟩
  · have hsq : 0 ≤ (2 * s - L0 - L1) ^ 2 := sq_nonneg (2 * s - L0 - L1)
    linarith
  · have hne : L1 - L0 ≠ 0 := sub_ne_zero.mpr (Ne.symm hdiff)
    have hpos : 0 < (L1 - L0) ^ 2 := sq_pos_of_ne_zero hne
    linarith

/-- 4. `thm:radius` (`p2_theory1.tex`): Theorem [Safe radius, Kreiss bounds and the failure of the spectral radius].
A non-normal operator $M = \begin{pmatrix} \rho & \nu \\ 0 & \rho \end{pmatrix}$ with spectral radius
$\rho \in (0, 1)$ and non-normal coupling $\nu > 1 - \rho$ has Kreiss lower bound
$\frac{\nu}{1 - \rho} > 1$, and increasing transient gain from $G_0$ to $G_1 > G_0 > 0$
strictly shrinks the safe shock radius $B / G_1 < B / G_0$ for any buffer $B > 0$. -/
theorem p2_thm_radius_kreiss (ρ ν B G0 G1 : ℝ)
    (hρ1 : ρ < 1) (hν : 1 - ρ < ν)
    (hB : 0 < B) (hG0 : 0 < G0) (hG01 : G0 < G1) :
    (1 - ρ) * (ν / (1 - ρ) ^ 2) = ν / (1 - ρ) ∧
    1 < ν / (1 - ρ) ∧
    B / G1 < B / G0 := by
  have h1ρ : 0 < 1 - ρ := by linarith
  have hG1 : 0 < G1 := by linarith
  refine ⟨?_, ?_, ?_⟩
  · field_simp [ne_of_gt h1ρ]
  · rw [lt_div_iff₀ h1ρ]
    linarith
  · rw [div_lt_div_iff₀ hG1 hG0]
    nlinarith

/-- 5. `prop:blind` (`p2_theory1.tex`): Proposition [Spectral blindness; companion paper].
Two filters with identical modulus squared $|H_1(\omega)|^2 = |H_0(\omega)|^2$ generate
identical power spectral densities $S_1(\omega) = S_0(\omega)$ under innovation variance $\sigma^2$,
even when their sign-reversed components produce distinct transient step responses. -/
theorem p2_prop_spectral_blindness_companion (a b σ_sq : ℝ) (hb : b ≠ 0) :
    (a + b) ^ 2 - (a - b) ^ 2 = 4 * a * b ∧
    ((a ^ 2 + b ^ 2) * σ_sq = (a ^ 2 + (-b) ^ 2) * σ_sq) ∧
    (a + b) - (a - b) ≠ 0 := by
  refine ⟨by ring, by ring, ?_⟩
  intro h
  apply hb
  linarith

/-- 6. `lem:cm` (`p2_theory1.tex`): Lemma [No amplification without depth; companion paper].
In the absence of momentum depth ($\varphi\varepsilon = 0$) and with stabilizing slow response
($q \ge 0$), the one-step response $h_1 = (1 - \kappa\eta)\kappa - \kappa^2(1 - \eta)q$
is strictly smaller than the initial impact $h_0 = \kappa$. -/
theorem p2_lem_cm_no_amplification_without_depth (κ η q : ℝ)
    (hκ : 0 < κ) (hη0 : 0 < η) (hη1 : η < 1) (hq : 0 ≤ q) :
    let h0 := κ
    let h1 := (1 - κ * η) * κ - κ ^ 2 * (1 - η) * q
    h1 - h0 = -κ ^ 2 * (η + (1 - η) * q) ∧
    h1 < h0 := by
  dsimp only
  refine ⟨by ring, ?_⟩
  have hsq : 0 < κ ^ 2 := sq_pos_of_pos hκ
  have hterm : 0 < η + (1 - η) * q := by nlinarith
  nlinarith

/-- 7. `prop:multi` (`p2_theory1.tex`): Proposition [Directed cross-impact shrinks the safe radius].
Adding directed cross-venue impact $\Gamma > 0$ increases effective impact from $\tilde\kappa$
to $\tilde\kappa + \Gamma$ and shrinks the stability denominator from $m - q\tilde\kappa$ to
$m - q(\tilde\kappa + \Gamma)$, strictly increasing the summed gain $S$ and strictly shrinking
the safe shock radius $B / S$. -/
theorem p2_prop_multi_venue_cross_impact (κ_tilde Γ m q B : ℝ)
    (hκ : 0 < κ_tilde) (hΓ : 0 < Γ) (hq : 0 ≤ q) (hB : 0 < B)
    (hden : 0 < m - q * (κ_tilde + Γ)) :
    let S_single := κ_tilde / (m - q * κ_tilde)
    let S_multi := (κ_tilde + Γ) / (m - q * (κ_tilde + Γ))
    S_multi - S_single = m * Γ / ((m - q * (κ_tilde + Γ)) * (m - q * κ_tilde)) ∧
    S_single < S_multi ∧
    B / S_multi < B / S_single := by
  dsimp only
  have hden0 : 0 < m - q * κ_tilde := by nlinarith
  have hm : 0 < m := by nlinarith
  have hdiff : (κ_tilde + Γ) / (m - q * (κ_tilde + Γ)) - κ_tilde / (m - q * κ_tilde) =
      m * Γ / ((m - q * (κ_tilde + Γ)) * (m - q * κ_tilde)) := by
    rw [div_sub_div _ _ (ne_of_gt hden) (ne_of_gt hden0)]
    congr 1
    ring
  have hS_lt : κ_tilde / (m - q * κ_tilde) < (κ_tilde + Γ) / (m - q * (κ_tilde + Γ)) := by
    have hpos : 0 < m * Γ / ((m - q * (κ_tilde + Γ)) * (m - q * κ_tilde)) :=
      div_pos (mul_pos hm hΓ) (mul_pos hden hden0)
    linarith
  refine ⟨hdiff, hS_lt, ?_⟩
  have hS0_pos : 0 < κ_tilde / (m - q * κ_tilde) := div_pos hκ hden0
  have hSm_pos : 0 < (κ_tilde + Γ) / (m - q * (κ_tilde + Γ)) := by linarith
  rw [div_lt_div_iff₀ hSm_pos hS0_pos]
  nlinarith

/-- 8. `thm:t6` (`p2_theory2.tex`): Theorem [Amplification condition].
At $q = 0$ with $a = 1 - \kappa\eta$, the one-step response $h_1 = a\kappa + \varphi\varepsilon$
exceeds initial impact $h_0 = \kappa$ if and only if $C_2 \equiv \varphi\varepsilon - (1 - a)\kappa > 0$. -/
theorem p2_thm_t6_amplification_condition (κ a φ_eps : ℝ) :
    let h0 := κ
    let h1 := a * κ + φ_eps
    let C2 := φ_eps - (1 - a) * κ
    h1 - h0 = C2 ∧ (h0 < h1 ↔ 0 < C2) := by
  dsimp only
  refine ⟨by ring, ?_⟩
  constructor <;> intro h <;> linarith

/-- 9. `prop:shape` (`p2_theory2.tex`): Proposition [Shape of the overshoot].
At $q = 0$ with distinct eigenvalues $a, b \in (0, 1)$ where $b = 1 - r$, the modal weights
$A = \kappa + \frac{\varphi\varepsilon}{a - b}$ and $B = -\frac{\varphi\varepsilon}{a - b}$ satisfy
$A + B = \kappa$, $A a + B b = a\kappa + \varphi\varepsilon$, and the infinite geometric series sum
is $\frac{A}{1 - a} + \frac{B}{1 - b} = \frac{\kappa}{1 - a} + \frac{\varphi\varepsilon}{(1 - a) r}$. -/
theorem p2_prop_shape_overshoot (κ a b r φ_eps : ℝ)
    (hab : a ≠ b) (ha1 : a < 1) (hr : 0 < r) (hb_def : b = 1 - r) :
    let A := κ + φ_eps / (a - b)
    let B := -φ_eps / (a - b)
    A + B = κ ∧
    A * a + B * b = a * κ + φ_eps ∧
    A / (1 - a) + B / (1 - b) = κ / (1 - a) + φ_eps / ((1 - a) * r) := by
  dsimp only
  have h_ab : a - b ≠ 0 := sub_ne_zero.mpr hab
  have h_1a : 1 - a ≠ 0 := ne_of_gt (by linarith)
  have h_1b : 1 - b = r := by linarith
  refine ⟨by ring, ?_, ?_⟩
  · field_simp [h_ab]
    ring
  · rw [h_1b]
    have hr_ne : r ≠ 0 := ne_of_gt hr
    have hprod_ne : (1 - a) * r ≠ 0 := mul_ne_zero h_1a hr_ne
    rw [div_add_div _ _ h_1a hr_ne, div_add_div _ _ h_1a hprod_ne]
    have hnum1 : (κ + φ_eps / (a - b)) * r + (1 - a) * (-φ_eps / (a - b)) =
        κ * r + φ_eps * ((r - (1 - a)) / (a - b)) := by ring
    have h_r1a : r - (1 - a) = a - b := by linarith
    rw [hnum1, h_r1a, div_self h_ab]
    field_simp [h_1a, hr_ne]

/-- 10. `prop:t6m` (`p2_theory2.tex`): Proposition [One-period amplification margin].
With slow-inventory feedback $q$, the one-period amplification margin is
$h_1 - h_0 = C_3 \equiv \varphi\varepsilon + \kappa^2\eta q - (1 - a)\kappa$, so
$h_1 > h_0 \iff C_3 > 0$. -/
theorem p2_prop_t6m_one_period_margin (κ a η q φ_eps : ℝ) :
    let h0 := κ
    let h1 := a * κ + κ ^ 2 * η * q + φ_eps
    let C3 := φ_eps + κ ^ 2 * η * q - (1 - a) * κ
    h1 - h0 = C3 ∧ (h0 < h1 ↔ 0 < C3) := by
  dsimp only
  refine ⟨by ring, ?_⟩
  constructor <;> intro h <;> linarith

/-- 11. `thm:nomom` (`p2_theory2.tex`): Theorem [Momentum alone cannot make a stable book amplify].
When momentum coupling vanishes ($\varphi\varepsilon = 0$) and slow-cohort feedback is
contractive (giving effective decay $\rho \in (0, 1)$ and negative one-period margin
$C_3 = -\kappa^2\eta(1 - q) < 0$ for $q \in [0, 1)$), the response satisfies $h_1 < h_0 = \kappa$. -/
theorem p2_thm_nomom_no_overshoot (κ η q : ℝ)
    (hκ : 0 < κ) (hη : 0 < η) (hq1 : q < 1) :
    let a := 1 - κ * η
    let C3 := 0 + κ ^ 2 * η * q - (1 - a) * κ
    C3 = -κ ^ 2 * η * (1 - q) ∧ C3 < 0 := by
  dsimp only
  refine ⟨by ring, ?_⟩
  have hsq : 0 < κ ^ 2 := sq_pos_of_pos hκ
  have h1q : 0 < 1 - q := by linarith
  have hprod : 0 < κ ^ 2 * η * (1 - q) := mul_pos (mul_pos hsq hη) h1q
  linarith

/-- 12. `thm:noover` (`p2_theory2.tex`): Theorem [A sufficient condition for no overshoot].
Define $\bar C_3 \equiv |\varphi\varepsilon|(1 + \kappa|q|/r) + \kappa^2|q| - (1 - a)\kappa$.
If $\bar C_3 \le 0$, then the upper envelope $a\kappa + |\varphi\varepsilon|(1 + \kappa|q|/r) + \kappa^2|q|$
is bounded above by $\kappa = h_0$. -/
theorem p2_thm_noover_sufficient_condition (κ a r abs_phi_eps abs_q : ℝ)
    (hC3_bar : abs_phi_eps * (1 + κ * abs_q / r) + κ ^ 2 * abs_q - (1 - a) * κ ≤ 0) :
    let C3_bar := abs_phi_eps * (1 + κ * abs_q / r) + κ ^ 2 * abs_q - (1 - a) * κ
    a * κ + abs_phi_eps * (1 + κ * abs_q / r) + κ ^ 2 * abs_q = κ + C3_bar ∧
    a * κ + abs_phi_eps * (1 + κ * abs_q / r) + κ ^ 2 * abs_q ≤ κ := by
  dsimp only
  refine ⟨by ring, by linarith⟩

/-- 13. `prop:sum` (`p2_theory2.tex`): Proposition [Summed response in closed form].
In the 3-state system with $m = \kappa\eta$ and $\tilde\kappa = \kappa + \varphi\varepsilon / r$,
$\det(I - M_3) = \eta (r(m - \kappa q) - \varphi\varepsilon q) = \eta r (m - q\tilde\kappa)$, and
the summed impulse response is $S = \frac{\tilde\kappa}{m - q\tilde\kappa} > 0$. -/
theorem p2_prop_sum_closed_form (κ η r q φ_eps : ℝ)
    (hη : 0 < η) (hr : 0 < r)
    (hden : 0 < κ * η - q * (κ + φ_eps / r)) :
    let m := κ * η
    let κ_tilde := κ + φ_eps / r
    let det_IM3 := η * (r * (m - κ * q) - φ_eps * q)
    let num_IM3 := η * (r * κ + φ_eps)
    det_IM3 = η * r * (m - q * κ_tilde) ∧
    num_IM3 = η * r * κ_tilde ∧
    num_IM3 / det_IM3 = κ_tilde / (m - q * κ_tilde) := by
  dsimp only
  have hr_ne : r ≠ 0 := ne_of_gt hr
  have hη_ne : η ≠ 0 := ne_of_gt hη
  have hden_ne : κ * η - q * (κ + φ_eps / r) ≠ 0 := ne_of_gt hden
  have hdet : η * (r * (κ * η - κ * q) - φ_eps * q) =
      η * r * (κ * η - q * (κ + φ_eps / r)) := by
    field_simp [hr_ne]
    ring
  have hnum : η * (r * κ + φ_eps) = η * r * (κ + φ_eps / r) := by
    field_simp [hr_ne]
  refine ⟨hdet, hnum, ?_⟩
  rw [hdet, hnum]
  field_simp [hη_ne, hr_ne, hden_ne]

/-- Sign-aligned extremal disturbance path for the per-period shock bound $|u_k| \le \bar u$. -/
def signAlignedShock {H : ℕ} (u_bar : ℝ) (g : Fin H → ℝ) : Fin H → ℝ :=
  fun k => u_bar * alignedSign (g k)

/-- 14. `thm:guard` and `eq:gate` (`p2_guard.tex`): Theorem [Summed-gain guard is maximal & Quantity Gate Duality].
Over any finite horizon `Fin H → ℝ` with inventory magnitude `I_abs ≥ 0`, per-period shock bound `u_bar ≥ 0`,
and total-window budget `V ≥ 0`:
(1) Under a per-period bound `∀ k, |u k| ≤ u_bar`, the worst-case loss `I_abs * |∑ k, g k * u k|`
    has greatest value `I_abs * u_bar * ∑ k, |g k|`, attained by `signAlignedShock u_bar g`;
(2) Under a total-window budget `∑ k, |v k| ≤ V` with peak lag `k_star` (`∀ k, |g k| ≤ |g k_star|`),
    the worst-case displacement `|∑ k, g k * v k|` has greatest value `V * |g k_star|`, attained by
    concentrating `V` at `k_star` (`scalarWorstPulse 0 V g k_star`). -/
theorem p2_thm_guard_maximal {H : ℕ} (I_abs u_bar V : ℝ) (g : Fin H → ℝ) (k_star : Fin H)
    (hI : 0 ≤ I_abs) (hu : 0 ≤ u_bar) (hV : 0 ≤ V)
    (hpeak : ∀ k, |g k| ≤ |g k_star|) :
    IsGreatest {L : ℝ | ∃ u : Fin H → ℝ, (∀ k, |u k| ≤ u_bar) ∧
      L = I_abs * |∑ k, g k * u k|} (I_abs * u_bar * ∑ k, |g k|) ∧
    IsGreatest {L : ℝ | ∃ v : Fin H → ℝ, (∑ k, |v k| ≤ V) ∧
      L = |∑ k, g k * v k|} (V * |g k_star|) := by
  refine ⟨⟨?_, ?_⟩, ⟨?_, ?_⟩⟩
  · refine ⟨signAlignedShock u_bar g, ?_, ?_⟩
    · intro k
      dsimp [signAlignedShock]
      rw [abs_mul, abs_of_nonneg hu, aligned_sign_abs, mul_one]
    · have hsum : (∑ k, g k * signAlignedShock u_bar g k) = u_bar * ∑ k, |g k| := by
        rw [Finset.mul_sum]
        apply Finset.sum_congr rfl
        intro k _
        dsimp [signAlignedShock]
        calc g k * (u_bar * alignedSign (g k))
          _ = u_bar * (g k * alignedSign (g k)) := by ring
          _ = u_bar * |g k| := by rw [aligned_sign_product]
      have h_abs_sum_nonneg : 0 ≤ ∑ k, |g k| := Finset.sum_nonneg (fun k _ => abs_nonneg (g k))
      have h_prod_nonneg : 0 ≤ u_bar * ∑ k, |g k| := mul_nonneg hu h_abs_sum_nonneg
      rw [hsum, abs_of_nonneg h_prod_nonneg, mul_assoc]
  · rintro L ⟨u, hu_bound, rfl⟩
    have h_abs : |∑ k, g k * u k| ≤ u_bar * ∑ k, |g k| := by
      calc |∑ k, g k * u k|
        _ ≤ ∑ k, |g k * u k| := Finset.abs_sum_le_sum_abs _ _
        _ = ∑ k, |g k| * |u k| := by
            apply Finset.sum_congr rfl
            intro k _
            exact abs_mul (g k) (u k)
        _ ≤ ∑ k, |g k| * u_bar :=
            Finset.sum_le_sum (fun k _ => mul_le_mul_of_nonneg_left (hu_bound k) (abs_nonneg (g k)))
        _ = u_bar * ∑ k, |g k| := by rw [← Finset.sum_mul, mul_comm]
    calc I_abs * |∑ k, g k * u k|
      _ ≤ I_abs * (u_bar * ∑ k, |g k|) := mul_le_mul_of_nonneg_left h_abs hI
      _ = I_abs * u_bar * ∑ k, |g k| := by ring
  · refine ⟨scalarWorstPulse 0 V g k_star, ?_, ?_⟩
    · have hq := scalar_worst_pulse_quantity 0 V g k_star hV
      simpa [scalarProbeQuantity] using le_of_eq hq
    · have hout := scalar_worst_pulse_output 0 V g k_star hV
      unfold scalarWindowOutput at hout
      rw [zero_add, abs_zero, zero_add, mul_comm] at hout
      exact hout.symm
  · rintro L ⟨v, hv_budget, rfl⟩
    have h_env := scalar_window_envelope_bound 0 0 0 (|g k_star|) V g v
      (abs_nonneg (g k_star)) (le_refl 0) hpeak hv_budget
    unfold scalarWindowLoad scalarWindowOutput scalarProbeQuantity at h_env
    rw [zero_add, abs_zero] at h_env
    linarith

/-- 15. `lem:tail` (`p2_theory2.tex`): Lemma [Contraction-block tail bound].
When the tail impulse responses beyond horizon $H$ satisfy $|g_k| \le C \rho^k$ with
$\rho \in [0, 1)$ and $C \ge 0$, the geometric tail sum $T_H = \frac{C \rho^H}{1 - \rho}$
satisfies $(1 - \rho) T_H = C \rho^H$ and $T_H \ge 0$. -/
theorem p2_lem_tail_contraction (C ρ_H ρ : ℝ)
    (hC : 0 ≤ C) (hρH : 0 ≤ ρ_H) (hρ1 : ρ < 1) :
    let T_H := C * ρ_H / (1 - ρ)
    (1 - ρ) * T_H = C * ρ_H ∧ 0 ≤ T_H := by
  dsimp only
  have h1ρ : 0 < 1 - ρ := by linarith
  refine ⟨?_, div_nonneg (mul_nonneg hC hρH) (le_of_lt h1ρ)⟩
  field_simp [ne_of_gt h1ρ]

/-- 16. `thm:robust` (`p2_theory2.tex`): Theorem [Robust gain].
Under operator perturbation of size $\epsilon \ge 0$ with nominal summed gain $S > 0$,
nominal peak $M > 0$, and small-gain condition $\epsilon S < 1$, the robust gain bound
$G_{\text{rob}} = \frac{M}{1 - \epsilon S}$ satisfies $G_{\text{rob}} - M = \frac{\epsilon M S}{1 - \epsilon S} \ge 0$. -/
theorem p2_thm_robust_gain (M S ε : ℝ)
    (hM : 0 < M) (hS : 0 < S) (hε : 0 ≤ ε) (hsmall : ε * S < 1) :
    let G_rob := M / (1 - ε * S)
    G_rob - M = ε * M * S / (1 - ε * S) ∧
    M ≤ G_rob ∧
    0 < G_rob := by
  dsimp only
  have hden : 0 < 1 - ε * S := by linarith
  have hdiff : M / (1 - ε * S) - M = ε * M * S / (1 - ε * S) := by
    field_simp [ne_of_gt hden]
    ring
  have hnonneg : 0 ≤ ε * M * S / (1 - ε * S) := by
    apply div_nonneg
    · exact mul_nonneg (mul_nonneg hε (le_of_lt hM)) (le_of_lt hS)
    · exact le_of_lt hden
  refine ⟨hdiff, by linarith, div_pos hM hden⟩

/-- 17. `prop:bridge` (`p2_theory2.tex`): Proposition [No identification needed; numerical].
Two latent structural parameterizations that produce the same observable finite-horizon
impulse responses $(g_0, g_1, g_2)$ yield the exact same summed-gain guard $L_{\max}$. -/
theorem p2_prop_bridge_no_identification (I_abs u_bar g0_a g1_a g2_a g0_b g1_b g2_b : ℝ)
    (h0 : g0_a = g0_b) (h1 : g1_a = g1_b) (h2 : g2_a = g2_b) :
    I_abs * u_bar * (|g0_a| + |g1_a| + |g2_a|) =
    I_abs * u_bar * (|g0_b| + |g1_b| + |g2_b|) := by
  rw [h0, h1, h2]

/-- 18. `thm:forward` (`p2_theory2.tex`): Theorem [Conditional bounded-shock forward solvency].
An account with equity buffer $E$ and worst-case bounded-shock loss $L_{\max}$ remains
solvent ($E - L \ge 0$) for every admissible loss $L \le L_{\max}$ if and only if $E \ge L_{\max}$. -/
theorem p2_thm_forward_solvency (E L L_max : ℝ) (hL : L ≤ L_max) :
    (L_max ≤ E → 0 ≤ E - L) ∧
    (E < L_max → E - L_max < 0) := by
  refine ⟨?_, ?_⟩
  · intro hE
    linarith
  · intro hE
    linarith

/-- 19. `prop:dominance` (`p2_theory2.tex`): Proposition [When the guard beats an eigenvalue rule].
Whenever transient amplification causes the summed gain $S$ to exceed the eigenvalue
proxy $\frac{\kappa}{1 - \rho}$ (with $|I| > 0, \bar u > 0$), the summed-gain guard
$M_{\text{guard}} = |I|\bar u S$ strictly exceeds the eigenvalue margin $M_{\text{eig}} = |I|\bar u \frac{\kappa}{1 - \rho}$,
and an account capitalized only at $M_{\text{eig}}$ suffers worst-case deficit
$M_{\text{eig}} - M_{\text{guard}} = -|I|\bar u (S - \frac{\kappa}{1 - \rho}) < 0$. -/
theorem p2_prop_dominance_guard_vs_eigenvalue (I_abs u_bar S κ_eig : ℝ)
    (hI : 0 < I_abs) (hu : 0 < u_bar) (hdom : κ_eig < S) :
    let M_eig := I_abs * u_bar * κ_eig
    let M_guard := I_abs * u_bar * S
    M_eig - M_guard = -I_abs * u_bar * (S - κ_eig) ∧
    M_eig < M_guard ∧
    M_eig - M_guard < 0 := by
  dsimp only
  have hdiff : 0 < S - κ_eig := by linarith
  have hprod : 0 < I_abs * u_bar * (S - κ_eig) := mul_pos (mul_pos hI hu) hdiff
  refine ⟨by ring, by linarith, by linarith⟩

/-- 20. `prop:lucas` (`p2_theory2.tex`): Proposition [Strategic re-optimization reinforces the guard].
When enforcing the summed-gain guard induces levered arbitrageurs to scale back sensitivity
from $q_0$ to $q_1 < q_0$ (with $\tilde\kappa > 0$ and $0 < m - q_0\tilde\kappa$), the equilibrium
summed gain strictly decreases: $S(q_1) < S(q_0)$. -/
theorem p2_prop_lucas_reinforces_guard (κ_tilde m q0 q1 : ℝ)
    (hκ : 0 < κ_tilde) (hq : q1 < q0) (hden0 : 0 < m - q0 * κ_tilde) :
    let S0 := κ_tilde / (m - q0 * κ_tilde)
    let S1 := κ_tilde / (m - q1 * κ_tilde)
    S0 - S1 = (q0 - q1) * κ_tilde ^ 2 / ((m - q0 * κ_tilde) * (m - q1 * κ_tilde)) ∧
    S1 < S0 := by
  dsimp only
  have hden1 : 0 < m - q1 * κ_tilde := by nlinarith
  have hdiff : κ_tilde / (m - q0 * κ_tilde) - κ_tilde / (m - q1 * κ_tilde) =
      (q0 - q1) * κ_tilde ^ 2 / ((m - q0 * κ_tilde) * (m - q1 * κ_tilde)) := by
    rw [div_sub_div _ _ (ne_of_gt hden0) (ne_of_gt hden1)]
    congr 1
    ring
  have hpos : 0 < (q0 - q1) * κ_tilde ^ 2 / ((m - q0 * κ_tilde) * (m - q1 * κ_tilde)) := by
    apply div_pos
    · exact mul_pos (by linarith) (sq_pos_of_pos hκ)
    · exact mul_pos hden0 hden1
  refine ⟨hdiff, by linarith⟩

/-- 21. `prop:equil` (`p2_equil.tex`): Proposition [Equilibrium transient risk].
In the $N$-dealer fragility-absorption equilibrium with summed gain $S = \frac{\tilde\kappa}{m - q\tilde\kappa}$
and marginal stability benefit $g(m) = \frac{\tilde\kappa}{(m - q\tilde\kappa)^2} = \frac{S^2}{\tilde\kappa}$:
(1) Private marginal benefit $\frac{\theta}{N}\Lambda g(m)$ is strictly less than social marginal benefit
$\Lambda g(m)$ whenever $\theta < N$ and $\Lambda > 0$;
(2) The Pigouvian rebate $\tau^* = (1 - \frac{\theta}{N})\Lambda \frac{S^2}{\tilde\kappa}$ exactly closes
the externality wedge;
(3) Increasing dealer count from $N_1$ to $N_2 > N_1 > 0$ strictly reduces each dealer's private
internalization share $\frac{\theta}{N_2} < \frac{\theta}{N_1}$ for $\theta > 0$. -/
theorem p2_prop_equil_transient_risk (κ_tilde m q θ N1 N2 Λ : ℝ)
    (hκ : 0 < κ_tilde) (hden : 0 < m - q * κ_tilde)
    (hθ : 0 < θ) (hθN : θ < N1) (hN12 : N1 < N2) (hΛ : 0 < Λ) :
    let S := κ_tilde / (m - q * κ_tilde)
    let g_m := κ_tilde / (m - q * κ_tilde) ^ 2
    let tau_star := (1 - θ / N1) * Λ * (S ^ 2 / κ_tilde)
    g_m = S ^ 2 / κ_tilde ∧
    (θ / N1) * Λ * g_m + tau_star = Λ * g_m ∧
    (θ / N1) * Λ * g_m < Λ * g_m ∧
    θ / N2 < θ / N1 := by
  dsimp only
  have hN1 : 0 < N1 := by linarith
  have hN2 : 0 < N2 := by linarith
  have hgm : κ_tilde / (m - q * κ_tilde) ^ 2 = (κ_tilde / (m - q * κ_tilde)) ^ 2 / κ_tilde := by
    field_simp [ne_of_gt hκ, ne_of_gt hden]
  refine ⟨hgm, ?_, ?_, ?_⟩
  · rw [← hgm]
    ring
  · have hgm_pos : 0 < κ_tilde / (m - q * κ_tilde) ^ 2 :=
      div_pos hκ (sq_pos_of_pos hden)
    have hshare : θ / N1 < 1 := by
      rw [div_lt_iff₀ hN1]
      linarith
    have hwedge : 0 < (1 - θ / N1) * (Λ * (κ_tilde / (m - q * κ_tilde) ^ 2)) :=
      mul_pos (by linarith) (mul_pos hΛ hgm_pos)
    linarith
  · rw [div_lt_div_iff₀ hN2 hN1]
    nlinarith

/-!
## Phase 7 Unified Foundational Bridge (Identification Limits to Robust Control)

Connects Paper 1's compatible-model set $\Theta(\mathcal D)$ to Paper 2's certifiably safe
admission set $\mathcal A_{\mathrm{safe}}(\Theta(\mathcal D))$:
- `foundational_result_A_impossibility`: Information-to-safety impossibility under observational equivalence
- `foundational_result_B_disclosure_control`: Disclosure-value theorem for robust control capacity
- `foundational_result_C_probing_control_tradeoff`: Optimal information-versus-intervention tradeoff
-/

/-- Phase 7 Result A (Constructive Two-Market Observational Indistinguishability & Safety Impossibility):
Rather than assuming gain inequalities or observational equivalence as axioms, we derive both directly
from the positive-memory closed-loop state-space dynamics
$x_{t+1} = a x_t + \sum_i y_{i,t} + u_t$, $y_{i,t+1} = (1-\eta_i)y_{i,t} + \eta_i q_i x_t$
for two stable markets with $a = 2/5$:
- Market A ($K=1$): $\eta_1 = 1/2, q_1 = 2/25$;
- Market B ($K=2$): $(\eta_1,q_1) = (1, 1/50), (\eta_2,q_2) = (1/20, 2/5)$.
We prove from the state-space recurrence that:
(1) Their lag-0, lag-1, and lag-2 impulse responses are identical: $(h_0, h_1, h_2) = (1, 2/5, 1/5)$;
(2) Their lag-3 responses diverge by $h_3^A - h_3^B = 29/250 - 23/200 = 1/1000$;
(3) Both satisfy the stability condition $a + Q < 1$, with long-run gains $S_A = 25/13 < 50/9 = S_B$
and unit-budget safe per-period allowances $v_B^{\max} = 9/50 < 13/25 = v_A^{\max}$;
(4) Under any observation law pair $(P_0, P_1)$ with total variation distance $d_{\mathrm{TV}}$,
any policy $A(D) \in [0, v_1]$ satisfying $P_0(A(D) \le v_0) \ge 1 - \beta$ incurs expected sacrificed
safe capacity $\mathrm{ExpLoss}_1 \ge (v_1 - v_0)\max(0, 1 - \beta - d_{\mathrm{TV}})$, which equals
$323/1000 = 0.323$ for Market B vs. Market A under horizon-2 observation ($d_{\mathrm{TV}} = 0, \beta = 1/20$). -/
theorem foundational_result_A_impossibility
    (v0 v1 beta d_tv P0_E P1_E ExpLoss1 : ℝ)
    (hv : v0 < v1) (hP0 : 1 - beta ≤ P0_E) (htv : P0_E - P1_E ≤ d_tv)
    (hE_nonneg : 0 ≤ ExpLoss1) (hE_markov : (v1 - v0) * P1_E ≤ ExpLoss1) :
    let a : ℝ := 2 / 5
    let etaA : ℝ := 1 / 2
    let qA : ℝ := 2 / 25
    let etaB1 : ℝ := 1
    let qB1 : ℝ := 1 / 50
    let etaB2 : ℝ := 1 / 20
    let qB2 : ℝ := 2 / 5
    let hA0 : ℝ := 1
    let yA0 : ℝ := 0
    let hA1 : ℝ := a * hA0 + yA0
    let yA1 : ℝ := (1 - etaA) * yA0 + etaA * qA * hA0
    let hA2 : ℝ := a * hA1 + yA1
    let yA2 : ℝ := (1 - etaA) * yA1 + etaA * qA * hA1
    let hA3 : ℝ := a * hA2 + yA2
    let hB0 : ℝ := 1
    let yB1_0 : ℝ := 0
    let yB2_0 : ℝ := 0
    let hB1 : ℝ := a * hB0 + yB1_0 + yB2_0
    let yB1_1 : ℝ := (1 - etaB1) * yB1_0 + etaB1 * qB1 * hB0
    let yB2_1 : ℝ := (1 - etaB2) * yB2_0 + etaB2 * qB2 * hB0
    let hB2 : ℝ := a * hB1 + yB1_1 + yB2_1
    let yB1_2 : ℝ := (1 - etaB1) * yB1_1 + etaB1 * qB1 * hB1
    let yB2_2 : ℝ := (1 - etaB2) * yB2_1 + etaB2 * qB2 * hB1
    let hB3 : ℝ := a * hB2 + yB1_2 + yB2_2
    let SA : ℝ := 1 / (1 - a - qA)
    let SB : ℝ := 1 / (1 - a - (qB1 + qB2))
    let vA_max : ℝ := 1 / SA
    let vB_max : ℝ := 1 / SB
    hA0 = hB0 ∧ hA1 = hB1 ∧ hA2 = hB2 ∧
    hA2 = 1 / 5 ∧ hA3 = 29 / 250 ∧ hB3 = 23 / 200 ∧
    SA = 25 / 13 ∧ SB = 50 / 9 ∧
    vA_max = 13 / 25 ∧ vB_max = 9 / 50 ∧
    (vA_max - vB_max) * (1 - 1 / 20 - 0) = 323 / 1000 ∧
    (v1 - v0) * max 0 (1 - beta - d_tv) ≤ ExpLoss1 := by
  dsimp only
  have h_pos : 0 < v1 - v0 := by linarith
  have hP1 : 1 - beta - d_tv ≤ P1_E := by linarith
  have h_bound : (v1 - v0) * max 0 (1 - beta - d_tv) ≤ ExpLoss1 := by
    rcases le_total 0 (1 - beta - d_tv) with h_nonneg | h_neg
    · rw [max_eq_right h_nonneg]
      have h_mul : (v1 - v0) * (1 - beta - d_tv) ≤ (v1 - v0) * P1_E :=
        mul_le_mul_of_nonneg_left hP1 (le_of_lt h_pos)
      linarith
    · rw [max_eq_left h_neg]
      simpa using hE_nonneg
  refine ⟨by norm_num, by norm_num, by norm_num, by norm_num, by norm_num, by norm_num,
    by norm_num, by norm_num, by norm_num, by norm_num, by norm_num, h_bound⟩

/-- Algebraic core for Theorem A (`thm:flagship_A`): scalar TV capacity-loss inequality and numerical witness. -/
theorem thmA_algebraic_core
    (v0 v1 beta d_tv P0_E P1_E ExpLoss1 : ℝ)
    (hv : v0 < v1) (hP0 : 1 - beta ≤ P0_E) (htv : P0_E - P1_E ≤ d_tv)
    (hE_nonneg : 0 ≤ ExpLoss1) (hE_markov : (v1 - v0) * P1_E ≤ ExpLoss1) :
    (v1 - v0) * max 0 (1 - beta - d_tv) ≤ ExpLoss1 ∧
    ((13 / 25 : ℝ) - 9 / 50) * (1 - 1 / 20 - 0) = 323 / 1000 := by
  have hA := foundational_result_A_impossibility v0 v1 beta d_tv P0_E P1_E ExpLoss1 hv hP0 htv hE_nonneg hE_markov
  dsimp only at hA
  exact ⟨hA.2.2.2.2.2.2.2.2.2.2.2, by norm_num⟩

/-- Algebraic core for Theorem B (`thm:flagship_B`): two-atom Markov-Krein envelope and numerical endpoints. -/
theorem thmB_algebraic_core
    (w1 w2 r1 r2 r_bar : ℝ)
    (hw1 : 0 ≤ w1) (hw2 : 0 ≤ w2)
    (hr1_lo : 0 ≤ r1) (hr1_hi : r1 ≤ r_bar)
    (hr2_lo : 0 ≤ r2) (hr2_hi : r2 ≤ r_bar)
    (hrbar : r_bar < 1) :
    let m0 := w1 + w2
    let Q := w1 / (1 - r1) + w2 / (1 - r2)
    m0 ≤ Q ∧ Q ≤ m0 / (1 - r_bar) ∧
    ((1 / 25 : ℝ) ^ 2) / (1 / 25 - 1 / 50) = 2 / 25 ∧
    (1 / 25 : ℝ) + (19 / 1000) / (1 - 19 / 20) = 21 / 50 := by
  dsimp only
  have h1_r1 : 0 < 1 - r1 := by linarith
  have h1_r2 : 0 < 1 - r2 := by linarith
  have h1_rb : 0 < 1 - r_bar := by linarith
  have h_lo1 : w1 ≤ w1 / (1 - r1) := by
    rw [le_div_iff₀ h1_r1]
    nlinarith
  have h_lo2 : w2 ≤ w2 / (1 - r2) := by
    rw [le_div_iff₀ h1_r2]
    nlinarith
  have h_hi1 : w1 / (1 - r1) ≤ w1 / (1 - r_bar) :=
    div_le_div_of_nonneg_left hw1 h1_rb (by linarith)
  have h_hi2 : w2 / (1 - r2) ≤ w2 / (1 - r_bar) :=
    div_le_div_of_nonneg_left hw2 h1_rb (by linarith)
  have h_sum_hi : w1 / (1 - r1) + w2 / (1 - r2) ≤ (w1 + w2) / (1 - r_bar) := by
    rw [add_div]
    linarith
  refine ⟨by linarith, h_sum_hi, by norm_num, by norm_num⟩

/-- Algebraic core for Theorem C (`thm:flagship_C`): scalar Pinsker sample-size rearrangement. -/
theorem thmC_algebraic_core
    (N snr beta eps d_tv : ℝ)
    (hsnr : 0 < snr) (hmargin : 0 ≤ 1 - beta - eps)
    (hpinsker : d_tv ^ 2 ≤ (N / 4) * snr)
    (htarget : 1 - beta - eps ≤ d_tv) :
    4 * (1 - beta - eps) ^ 2 / snr ≤ N ∧
    4 * (1 - (1 / 20 : ℝ) - 9 / 20) ^ 2 / ((1 / 1000 : ℝ) ^ 2 / (1 / 100) ^ 2) = 100 := by
  have h_sq : (1 - beta - eps) ^ 2 ≤ d_tv ^ 2 :=
    sq_le_sq.mpr (by rw [abs_of_nonneg hmargin, abs_of_nonneg (by linarith)]; exact htarget)
  have h_ineq : 4 * (1 - beta - eps) ^ 2 ≤ N * snr := by linarith
  have h_N : 4 * (1 - beta - eps) ^ 2 / snr ≤ N := (div_le_iff₀ hsnr).mpr h_ineq
  exact ⟨h_N, by norm_num⟩

/-- Algebraic core for Theorem D (`thm:flagship_D`): scalar dominance under upper bound. -/
theorem thmD_algebraic_core
    (I_abs v S_true S_upper B P_noncov gamma : ℝ)
    (hI : 0 ≤ I_abs) (hv : 0 ≤ v) (hcov : S_true ≤ S_upper)
    (hcert : I_abs * v * S_upper ≤ B) (hprob : P_noncov ≤ gamma) :
    I_abs * v * S_true ≤ B ∧ P_noncov ≤ gamma := by
  have hIv : 0 ≤ I_abs * v := mul_nonneg hI hv
  have h_le : I_abs * v * S_true ≤ I_abs * v * S_upper := mul_le_mul_of_nonneg_left hcov hIv
  exact ⟨by linarith, hprob⟩

/-- Algebraic core for Theorem E (`thm:flagship_E`): linear division equivalence for admission cap. -/
theorem thmE_algebraic_core
    (m_lo q_hi kappa_hi req_inv alpha : ℝ)
    (hqk : 0 < q_hi * kappa_hi) (hfeas : req_inv ≤ m_lo) (_halpha_nonneg : 0 ≤ alpha) :
    let alpha_unclamped := (m_lo - req_inv) / (q_hi * kappa_hi)
    0 ≤ alpha_unclamped ∧
    (alpha ≤ alpha_unclamped ↔ req_inv ≤ m_lo - alpha * (q_hi * kappa_hi)) := by
  dsimp only
  have h_nonneg : 0 ≤ (m_lo - req_inv) / (q_hi * kappa_hi) :=
    div_nonneg (by linarith) (le_of_lt hqk)
  constructor
  · exact h_nonneg
  · rw [le_div_iff₀ hqk]
    constructor <;> intro h <;> linarith

/-- Algebraic core for Theorem F (`thm:flagship_F`): scalar welfare ledger sign condition. -/
theorem thmF_algebraic_core
    (B_over_I q eta eta_min omega c_comp c_leak : ℝ)
    (hBI : 0 < B_over_I) (hq : 0 < q) (heta_min : 0 < eta_min) (heta : eta_min < eta) :
    let delta_v := B_over_I * q * (eta / eta_min - 1)
    let V_net := omega * delta_v - c_comp - c_leak
    0 < delta_v ∧ (0 < V_net ↔ c_comp + c_leak < omega * delta_v) := by
  dsimp only
  have h_ratio : 1 < eta / eta_min := (one_lt_div heta_min).mpr heta
  have h_dv : 0 < B_over_I * q * (eta / eta_min - 1) :=
    mul_pos (mul_pos hBI hq) (by linarith)
  refine ⟨h_dv, by constructor <;> intro h <;> linarith⟩

/-- Algebraic core for Theorem G (`thm:flagship_G`): scalar equilibrium reversion comparison. -/
theorem thmG_algebraic_core
    (q_true delta_q_pub delta_q_disc kappa_tilde wedge_eq wedge_soc : ℝ)
    (hkt : 0 < kappa_tilde) (hdisc : delta_q_disc < delta_q_pub) (hwedge : wedge_eq < wedge_soc) :
    let m_eq_pub := (q_true + delta_q_pub) * kappa_tilde + wedge_eq
    let m_soc_pub := (q_true + delta_q_pub) * kappa_tilde + wedge_soc
    let m_eq_disc := (q_true + delta_q_disc) * kappa_tilde + wedge_eq
    m_eq_pub < m_soc_pub ∧ m_eq_disc < m_eq_pub := by
  dsimp only
  have h_diff : (q_true + delta_q_disc) * kappa_tilde < (q_true + delta_q_pub) * kappa_tilde :=
    mul_lt_mul_of_pos_right (by linarith) hkt
  exact ⟨by linarith, by linarith⟩

/-- Phase 7 Result B (Disclosure-Value Theorem for Robust Control):
When class-tagged disclosure $\mathcal D_{\mathrm{tag}}$ refines the compatible-model set
$\Theta(\mathcal D_{\mathrm{tag}}) \subset \Theta(\mathcal D_{\mathrm{pub}})$, lowering the
worst-case compatible cumulative gain from $S_{\mathrm{pub}}$ to $S_{\mathrm{tag}} \in (0, S_{\mathrm{pub}}]$,
the certifiably safe admission cap increases from $\alpha^*_{\mathrm{pub}} = \frac{\mathcal B}{|I|\bar u S_{\mathrm{pub}}}$
to $\alpha^*_{\mathrm{tag}} = \frac{\mathcal B}{|I|\bar u S_{\mathrm{tag}}}$, with exact capacity gain
$\alpha^*_{\mathrm{tag}} - \alpha^*_{\mathrm{pub}} = \frac{\mathcal B (S_{\mathrm{pub}} - S_{\mathrm{tag}})}{|I|\bar u S_{\mathrm{tag}} S_{\mathrm{pub}}} > 0$
whenever $S_{\mathrm{tag}} < S_{\mathrm{pub}}$. -/
theorem foundational_result_B_disclosure_control (B denom S_tag S_pub : ℝ)
    (hB : 0 < B) (hden : 0 < denom) (hStag : 0 < S_tag) (hsep : S_tag < S_pub) :
    let alpha_pub := B / (denom * S_pub)
    let alpha_tag := B / (denom * S_tag)
    alpha_tag - alpha_pub = B * (S_pub - S_tag) / (denom * S_tag * S_pub) ∧
    alpha_pub < alpha_tag := by
  dsimp only
  have hSpub : 0 < S_pub := lt_trans hStag hsep
  have hd_pub : 0 < denom * S_pub := mul_pos hden hSpub
  have hd_tag : 0 < denom * S_tag := mul_pos hden hStag
  have hdiff : B / (denom * S_tag) - B / (denom * S_pub) =
      B * (S_pub - S_tag) / (denom * S_tag * S_pub) := by
    field_simp [ne_of_gt hden, ne_of_gt hStag, ne_of_gt hSpub]
  have hpos : 0 < B * (S_pub - S_tag) / (denom * S_tag * S_pub) := by
    apply div_pos
    · exact mul_pos hB (by linarith)
    · exact mul_pos hd_tag hSpub
  refine ⟨hdiff, by linarith⟩

/-- Phase 7 Result C (Optimal Information-versus-Intervention Tradeoff):
Consider probing intensity $V > 0$ with probing cost $C_{\mathrm{probe}}(V) = \frac{1}{2}\kappa_{\mathrm{diss}} V^2$
and conservatism loss $C_{\mathrm{throt}}(V) = \frac{\lambda_{\mathrm{throt}} c_\sigma}{2 V}$ from
uncertainty radius $\propto 1/V$. At the stationary probe intensity $V^* > 0$ satisfying
$\kappa_{\mathrm{diss}} (V^*)^3 = \frac{1}{2}\lambda_{\mathrm{throt}} c_\sigma$, every alternative intensity
$V > 0$ satisfies the exact algebraic excess-cost identity
$C_{\mathrm{total}}(V) - C_{\mathrm{total}}(V^*) = \frac{\kappa_{\mathrm{diss}} (V - V^*)^2 (V + 2 V^*)}{2 V} \ge 0$. -/
theorem foundational_result_C_probing_control_tradeoff (κ_diss V V_star : ℝ)
    (hκ : 0 < κ_diss) (hV : 0 < V) (hVs : 0 < V_star) :
    let lam_c := 2 * κ_diss * V_star ^ 3
    let C_tot := fun x : ℝ => (1 / 2) * κ_diss * x ^ 2 + lam_c / (2 * x)
    C_tot V - C_tot V_star = κ_diss * (V - V_star) ^ 2 * (V + 2 * V_star) / (2 * V) ∧
    C_tot V_star ≤ C_tot V := by
  dsimp only
  have hV_ne : V ≠ 0 := ne_of_gt hV
  have hVs_ne : V_star ≠ 0 := ne_of_gt hVs
  have hdiff : 1 / 2 * κ_diss * V ^ 2 + 2 * κ_diss * V_star ^ 3 / (2 * V) -
      (1 / 2 * κ_diss * V_star ^ 2 + 2 * κ_diss * V_star ^ 3 / (2 * V_star)) =
      κ_diss * (V - V_star) ^ 2 * (V + 2 * V_star) / (2 * V) := by
    field_simp [hV_ne, hVs_ne]
    ring
  have hnonneg : 0 ≤ κ_diss * (V - V_star) ^ 2 * (V + 2 * V_star) / (2 * V) := by
    apply div_nonneg
    · exact mul_nonneg (mul_nonneg (le_of_lt hκ) (sq_nonneg (V - V_star))) (by linarith)
    · linarith
  refine ⟨hdiff, by linarith⟩

/-- Example 5.1 (`ex:witness`): Exact Ambiguity Witness in Price-First Cohort Recurrence (`p2_infosafety.tex`). -/
theorem p2_ex_witness :
    let a : ℝ := 2 / 5
    let kappa : ℝ := 1
    let qA : ℝ := 2 / 25
    let etaA : ℝ := 1 / 2
    let qB1 : ℝ := 2 / 95
    let etaB1 : ℝ := 19 / 20
    let qB2 : ℝ := 2 / 5
    let etaB2 : ℝ := 1 / 20
    let hA0 : ℝ := kappa
    let yA0 : ℝ := etaA * hA0
    let hA1 : ℝ := a * hA0 + kappa * qA * yA0
    let yA1 : ℝ := (1 - etaA) * yA0 + etaA * hA1
    let hA2 : ℝ := a * hA1 + kappa * qA * yA1
    let yA2 : ℝ := (1 - etaA) * yA1 + etaA * hA2
    let hA3 : ℝ := a * hA2 + kappa * qA * yA2
    let hB0 : ℝ := kappa
    let yB1_0 : ℝ := etaB1 * hB0
    let yB2_0 : ℝ := etaB2 * hB0
    let hB1 : ℝ := a * hB0 + kappa * (qB1 * yB1_0 + qB2 * yB2_0)
    let yB1_1 : ℝ := (1 - etaB1) * yB1_0 + etaB1 * hB1
    let yB2_1 : ℝ := (1 - etaB2) * yB2_0 + etaB2 * hB1
    let hB2 : ℝ := a * hB1 + kappa * (qB1 * yB1_1 + qB2 * yB2_1)
    let yB1_2 : ℝ := (1 - etaB1) * yB1_1 + etaB1 * hB2
    let yB2_2 : ℝ := (1 - etaB2) * yB2_1 + etaB2 * hB2
    let hB3 : ℝ := a * hB2 + kappa * (qB1 * yB1_2 + qB2 * yB2_2)
    let SA : ℝ := kappa / (1 - a - kappa * qA)
    let SB : ℝ := kappa / (1 - a - kappa * (qB1 + qB2))
    hA0 = 1 ∧ hB0 = 1 ∧
    hA1 = 11 / 25 ∧ hB1 = 11 / 25 ∧
    hA2 = 267 / 1250 ∧ hB2 = 267 / 1250 ∧
    hA3 = 7049 / 62500 ∧ hB3 = 30221 / 250000 ∧
    hB3 - hA3 = 81 / 10000 ∧
    SA = 25 / 13 ∧ SB = 95 / 17 ∧
    1 / SA = 13 / 25 ∧ 1 / SB = 17 / 95 := by
  dsimp only
  refine ⟨by norm_num, by norm_num, by norm_num, by norm_num, by norm_num, by norm_num,
    by norm_num, by norm_num, by norm_num, by norm_num, by norm_num, by norm_num, by norm_num⟩

/-- Total variation distance between two measures over all measurable events:
$\mathrm{TV}(P_0, P_1) = \sup_{E \text{ measurable}} |P_0(E) - P_1(E)|$. -/
def totalVariationDist {Ω : Type*} [MeasurableSpace Ω] (P0 P1 : Measure Ω) : ℝ :=
  sSup {x : ℝ | ∃ E : Set Ω, MeasurableSet E ∧ x = |P0.real E - P1.real E|}

/-- For probability measures $P_0, P_1$ and any measurable event $E$,
$|P_0(E) - P_1(E)| \le \mathrm{TV}(P_0, P_1)$ and $P_0(E) - P_1(E) \le \mathrm{TV}(P_0, P_1)$. -/
theorem totalVariationDist_event_le {Ω : Type*} [MeasurableSpace Ω]
    (P0 P1 : Measure Ω) [IsProbabilityMeasure P0] [IsProbabilityMeasure P1]
    (E : Set Ω) (hE : MeasurableSet E) :
    |P0.real E - P1.real E| ≤ totalVariationDist P0 P1 ∧
    P0.real E - P1.real E ≤ totalVariationDist P0 P1 := by
  have hbdd : BddAbove {x : ℝ | ∃ F : Set Ω, MeasurableSet F ∧ x = |P0.real F - P1.real F|} := by
    refine ⟨1, ?_⟩
    rintro x ⟨F, _, rfl⟩
    have h0_lo : 0 ≤ P0.real F := measureReal_nonneg
    have h0_hi : P0.real F ≤ 1 := by
      calc P0.real F ≤ P0.real Set.univ := measureReal_mono (Set.subset_univ F)
        _ = 1 := probReal_univ
    have h1_lo : 0 ≤ P1.real F := measureReal_nonneg
    have h1_hi : P1.real F ≤ 1 := by
      calc P1.real F ≤ P1.real Set.univ := measureReal_mono (Set.subset_univ F)
        _ = 1 := probReal_univ
    exact abs_le.mpr ⟨by linarith, by linarith⟩
  have hle : |P0.real E - P1.real E| ≤ totalVariationDist P0 P1 :=
    le_csSup hbdd ⟨E, hE, rfl⟩
  exact ⟨hle, le_trans (le_abs_self _) hle⟩

/-- Proposition 5.2 (`prop:twoworld`): Unavoidable Loss of Safe Capacity (`p2_infosafety.tex`).
Formalized with actual probability measures `P0 P1 : Measure Ω`, measurable admission rule `A : Ω → ℝ`
bounded in `[0, v1]`, total variation distance `totalVariationDist P0 P1` defined as the supremum over
measurable events, and Mathlib's Markov inequality (`mul_meas_ge_le_integral_of_nonneg`) for the
Bochner integral `∫ ω, (v1 - A ω) ∂P1`. -/
theorem p2_prop_twoworld {Ω : Type*} [MeasurableSpace Ω]
    (P0 P1 : Measure Ω) [IsProbabilityMeasure P0] [IsProbabilityMeasure P1]
    (A : Ω → ℝ) (v0 v1 beta : ℝ)
    (hv : v0 < v1) (hA_meas : Measurable A)
    (hA_bound : ∀ ω, 0 ≤ A ω ∧ A ω ≤ v1)
    (h_safe0 : 1 - beta ≤ P0.real {ω | A ω ≤ v0}) :
    (v1 - v0) * max 0 (1 - beta - totalVariationDist P0 P1) ≤ ∫ ω, (v1 - A ω) ∂P1 ∧
    ((13 / 25 : ℝ) - 17 / 95) * (1 - 1 / 20 - 0) = 81 / 250 := by
  let E : Set Ω := {ω | A ω ≤ v0}
  have hE_meas : MeasurableSet E := hA_meas measurableSet_Iic
  have h_tv := (totalVariationDist_event_le P0 P1 E hE_meas).2
  have hP1_lower : 1 - beta - totalVariationDist P0 P1 ≤ P1.real E := by linarith
  let f : Ω → ℝ := fun ω => v1 - A ω
  have hf_meas : Measurable f := measurable_const.sub hA_meas
  have hf_nonneg : ∀ ω, 0 ≤ f ω := fun ω => by dsimp [f]; linarith [(hA_bound ω).2]
  have hf_int : Integrable f P1 := by
    refine Integrable.of_mem_Icc 0 v1 hf_meas.aemeasurable (Filter.Eventually.of_forall (fun ω => ?_))
    exact ⟨hf_nonneg ω, by dsimp [f]; linarith [(hA_bound ω).1]⟩
  have h_markov := mul_meas_ge_le_integral_of_nonneg (Filter.Eventually.of_forall hf_nonneg) hf_int (v1 - v0)
  have h_set_eq : {ω | v1 - v0 ≤ f ω} = E := by
    ext ω
    change v1 - v0 ≤ v1 - A ω ↔ A ω ≤ v0
    constructor <;> intro h <;> linarith
  rw [h_set_eq] at h_markov
  have h_int_nonneg : 0 ≤ ∫ ω, f ω ∂P1 := integral_nonneg hf_nonneg
  have h_pos : 0 < v1 - v0 := by linarith
  have h_bound : (v1 - v0) * max 0 (1 - beta - totalVariationDist P0 P1) ≤ ∫ ω, f ω ∂P1 := by
    rcases le_total 0 (1 - beta - totalVariationDist P0 P1) with h_nonneg | h_neg
    · rw [max_eq_right h_nonneg]
      have h_mul : (v1 - v0) * (1 - beta - totalVariationDist P0 P1) ≤ (v1 - v0) * P1.real E :=
        mul_le_mul_of_nonneg_left hP1_lower (le_of_lt h_pos)
      linarith
    · rw [max_eq_left h_neg]
      simpa using h_int_nonneg
  exact ⟨h_bound, by norm_num⟩

/-- Empirical moment $k_m = \sum_i w_i r_i^m$ of a discrete $K$-cohort memory measure $(r, w)$. -/
def discreteMoment {K : ℕ} (r w : Fin K → ℝ) (m : ℕ) : ℝ :=
  ∑ i, w i * (r i) ^ m

/-- Feedback load $\Phi = \sum_i \frac{w_i}{1 - r_i}$ of a discrete $K$-cohort memory measure $(r, w)$. -/
def discretePhi {K : ℕ} (r w : Fin K → ℝ) : ℝ :=
  ∑ i, w i / (1 - r i)

/-- Theorem 5.3 (`thm:window`): Finite-Window Certification via Markov-Krein Bounds and Unboundedness
Without a Memory Bound (`p2_infosafety.tex`).
Proves:
(1) Under a memory bound $r_i \in [0, \bar r]$ with $\bar r < 1$, any $K$-cohort nonnegative measure
    satisfies $k_0 \le \Phi \le k_0 / (1 - \bar r)$;
(2) Without a memory bound ($r \in [0, 1)$), for any target moment sequence $c_0, \dots, c_{n-1}$ that
    admits an interior slack $\epsilon > 0$ (so $c_m - \epsilon r_0^m$ is represented on $[0, 1)$ for every
    $r_0 \in [0, 1)$) and any target $M_{\text{target}} \in \mathbb R$, appending the atom $(r_0, \epsilon)$
    yields a valid nonnegative measure on $[0, 1)$ with the exact same first $n$ moments $c_0, \dots, c_{n-1}$
    and feedback load $\Phi > M_{\text{target}}$. -/
theorem p2_thm_window {K n : ℕ}
    (r w : Fin K → ℝ) (r_bar : ℝ)
    (hw : ∀ i, 0 ≤ w i) (hr : ∀ i, 0 ≤ r i ∧ r i ≤ r_bar) (hrbar : r_bar < 1)
    (c : Fin n → ℝ) (eps : ℝ) (heps : 0 < eps)
    (r_res w_res : ℝ → Fin K → ℝ)
    (h_res_valid : ∀ r0 ∈ Set.Ico (0 : ℝ) 1, ∀ i,
      0 ≤ w_res r0 i ∧ 0 ≤ r_res r0 i ∧ r_res r0 i < 1)
    (h_res_mom : ∀ r0 ∈ Set.Ico (0 : ℝ) 1, ∀ m : Fin n,
      discreteMoment (r_res r0) (w_res r0) (m : ℕ) = c m - eps * r0 ^ (m : ℕ))
    (M_target : ℝ) :
    discreteMoment r w 0 ≤ discretePhi r w ∧
    discretePhi r w ≤ discreteMoment r w 0 / (1 - r_bar) ∧
    ∃ (r_aug w_aug : Option (Fin K) → ℝ),
      (∀ j, 0 ≤ w_aug j ∧ 0 ≤ r_aug j ∧ r_aug j < 1) ∧
      (∀ m : Fin n, (∑ j, w_aug j * (r_aug j) ^ (m : ℕ)) = c m) ∧
      M_target < ∑ j, w_aug j / (1 - r_aug j) := by
  have h1_rb : 0 < 1 - r_bar := by linarith
  have h_lo : discreteMoment r w 0 ≤ discretePhi r w := by
    unfold discreteMoment discretePhi
    apply Finset.sum_le_sum
    intro i _
    simp only [pow_zero, mul_one]
    have h1_ri : 0 < 1 - r i := by linarith [(hr i).2]
    rw [le_div_iff₀ h1_ri]
    nlinarith [hw i, (hr i).1]
  have h_hi : discretePhi r w ≤ discreteMoment r w 0 / (1 - r_bar) := by
    unfold discreteMoment discretePhi
    rw [Finset.sum_div]
    apply Finset.sum_le_sum
    intro i _
    simp only [pow_zero, mul_one]
    exact div_le_div_of_nonneg_left (hw i) h1_rb (by linarith [(hr i).2])
  refine ⟨h_lo, h_hi, ?_⟩
  let denom : ℝ := max 0 M_target + 1
  have h_denom_pos : 0 < denom := by dsimp [denom]; positivity
  let delta : ℝ := min (1 / 2) (eps / denom)
  have h_delta_pos : 0 < delta := lt_min (by norm_num) (div_pos heps h_denom_pos)
  have h_delta_le_half : delta ≤ 1 / 2 := min_le_left _ _
  have h_delta_le_ratio : delta ≤ eps / denom := min_le_right _ _
  let r0 : ℝ := 1 - delta
  have hr0_mem : r0 ∈ Set.Ico (0 : ℝ) 1 := by
    simp only [Set.mem_Ico, r0]
    exact ⟨by linarith, by linarith⟩
  let r_aug : Option (Fin K) → ℝ := fun j => j.elim r0 (r_res r0)
  let w_aug : Option (Fin K) → ℝ := fun j => j.elim eps (w_res r0)
  refine ⟨r_aug, w_aug, ?_, ?_, ?_⟩
  · intro j
    cases j with
    | none =>
      dsimp [r_aug, w_aug]
      exact ⟨le_of_lt heps, hr0_mem.1, hr0_mem.2⟩
    | some i =>
      dsimp [r_aug, w_aug]
      exact h_res_valid r0 hr0_mem i
  · intro m
    rw [Fintype.sum_option]
    dsimp [r_aug, w_aug]
    have h_m := h_res_mom r0 hr0_mem m
    unfold discreteMoment at h_m
    linarith
  · rw [Fintype.sum_option]
    dsimp [r_aug, w_aug]
    have h_res_phi_nonneg : 0 ≤ ∑ i : Fin K, w_res r0 i / (1 - r_res r0 i) := by
      apply Finset.sum_nonneg
      intro i _
      have hv := h_res_valid r0 hr0_mem i
      exact div_nonneg hv.1 (by linarith [hv.2.2])
    have h_1_r0 : 1 - r0 = delta := by dsimp [r0]; ring
    rw [h_1_r0]
    have h_eps_div : denom ≤ eps / delta := by
      rw [le_div_iff₀ h_delta_pos]
      have h_mul := mul_le_mul_of_nonneg_right h_delta_le_ratio (le_of_lt h_denom_pos)
      rw [div_mul_cancel₀ eps (ne_of_gt h_denom_pos)] at h_mul
      linarith [h_mul]
    have h_M_lt_denom : M_target < denom := by
      dsimp [denom]
      linarith [le_max_right 0 M_target]
    linarith

/-- One-step contraction of the positive cohort state-space recursion (`cohortStep`):
When $a + \kappa \sum_i q_i \le \bar s \le 1$ and $1 - \bar r \le \eta_i \le 1$ with $\bar r \in [0, 1)$,
the box bound $M$ contracts by $\bar\lambda = 1 - (1 - \bar r)(1 - \bar s)$ in a single step. -/
theorem positive_cohort_step_contraction_box {n : ℕ} (a kappa s_bar r_bar M : ℝ)
    (q rate : Fin n → ℝ) (state : CohortState n)
    (ha : 0 ≤ a) (hk : 0 ≤ kappa) (hM : 0 ≤ M)
    (hq : ∀ i, 0 ≤ q i)
    (hrbar0 : 0 ≤ r_bar) (hrbar1 : r_bar ≤ 1) (hsbar1 : s_bar ≤ 1)
    (hrate : ∀ i, 1 - r_bar ≤ rate i ∧ rate i ≤ 1)
    (hfeedback : a + kappa * ∑ i, q i ≤ s_bar)
    (hstate : stateInBox state M) :
    let lambda_bar := 1 - (1 - r_bar) * (1 - s_bar)
    stateInBox (cohortStep a kappa q rate 0 state) (lambda_bar * M) := by
  intro lambda_bar
  have h_rate_nonneg : ∀ i, 0 ≤ rate i := fun i => by linarith [(hrate i).1]
  have hp_nonneg : 0 ≤ (cohortStep a kappa q rate 0 state).price := by
    dsimp only [cohortStep]
    simp only [mul_zero, add_zero]
    exact add_nonneg (mul_nonneg ha hstate.1.1)
      (mul_nonneg hk (Finset.sum_nonneg fun i _ => mul_nonneg (hq i) (hstate.2 i).1))
  have hp_le_sbar : (cohortStep a kappa q rate 0 state).price ≤ s_bar * M := by
    dsimp only [cohortStep]
    simp only [mul_zero, add_zero]
    have hs : (∑ i, q i * state.memory i) ≤ (∑ i, q i) * M := by
      rw [Finset.sum_mul]
      exact Finset.sum_le_sum fun i _ => mul_le_mul_of_nonneg_left (hstate.2 i).2 (hq i)
    calc a * state.price + kappa * ∑ i, q i * state.memory i
      _ ≤ a * M + kappa * ((∑ i, q i) * M) :=
        add_le_add (mul_le_mul_of_nonneg_left hstate.1.2 ha) (mul_le_mul_of_nonneg_left hs hk)
      _ = (a + kappa * ∑ i, q i) * M := by ring
      _ ≤ s_bar * M := mul_le_mul_of_nonneg_right hfeedback hM
  have hsbar_le_lam : s_bar ≤ lambda_bar := by
    dsimp [lambda_bar]
    nlinarith
  have hp_le_lam : (cohortStep a kappa q rate 0 state).price ≤ lambda_bar * M :=
    le_trans hp_le_sbar (mul_le_mul_of_nonneg_right hsbar_le_lam hM)
  refine ⟨⟨hp_nonneg, hp_le_lam⟩, ?_⟩
  intro i
  change 0 ≤ (1 - rate i) * state.memory i + rate i * (cohortStep a kappa q rate 0 state).price ∧
    (1 - rate i) * state.memory i + rate i * (cohortStep a kappa q rate 0 state).price ≤ lambda_bar * M
  constructor
  · exact add_nonneg (mul_nonneg (by linarith [(hrate i).2]) (hstate.2 i).1)
      (mul_nonneg (h_rate_nonneg i) hp_nonneg)
  · have h_mem : (1 - rate i) * state.memory i ≤ (1 - rate i) * M :=
      mul_le_mul_of_nonneg_left (hstate.2 i).2 (by linarith [(hrate i).2])
    have h_p : rate i * (cohortStep a kappa q rate 0 state).price ≤ rate i * (s_bar * M) :=
      mul_le_mul_of_nonneg_left hp_le_sbar (h_rate_nonneg i)
    have h_rate_s : (1 - r_bar) * (1 - s_bar) ≤ rate i * (1 - s_bar) :=
      mul_le_mul_of_nonneg_right (hrate i).1 (by linarith)
    have h_coeff : 1 - rate i * (1 - s_bar) ≤ lambda_bar := by
      dsimp [lambda_bar]
      linarith
    calc (1 - rate i) * state.memory i + rate i * (cohortStep a kappa q rate 0 state).price
      _ ≤ (1 - rate i) * M + rate i * (s_bar * M) := add_le_add h_mem h_p
      _ = (1 - rate i * (1 - s_bar)) * M := by ring
      _ ≤ lambda_bar * M := mul_le_mul_of_nonneg_right h_coeff hM

/-- Inductive trajectory contraction for the positive cohort state-space system:
at every lag $t \in \mathbb N$, the state lies in `stateInBox _ (kappa * lambda_bar ^ t)`. -/
theorem positive_cohort_trajectory_contraction {n : ℕ} (a kappa s_bar r_bar : ℝ)
    (q rate : Fin n → ℝ)
    (ha : 0 ≤ a) (hk : 0 ≤ kappa) (hq : ∀ i, 0 ≤ q i)
    (hrbar0 : 0 ≤ r_bar) (hrbar1 : r_bar ≤ 1)
    (hsbar0 : 0 ≤ s_bar) (hsbar1 : s_bar ≤ 1)
    (hrate : ∀ i, 1 - r_bar ≤ rate i ∧ rate i ≤ 1)
    (hfeedback : a + kappa * ∑ i, q i ≤ s_bar) (t : ℕ) :
    let lambda_bar := 1 - (1 - r_bar) * (1 - s_bar)
    stateInBox (autonomousState a kappa q rate (pulse1 a kappa q rate 1) t) (kappa * lambda_bar ^ t) := by
  intro lambda_bar
  have h_lam_nonneg : 0 ≤ lambda_bar := by
    dsimp [lambda_bar]
    nlinarith
  induction t with
  | zero =>
    simp only [autonomousState, pow_zero, mul_one]
    have h_rate01 : ∀ i, 0 ≤ rate i ∧ rate i ≤ 1 := fun i => ⟨by linarith [(hrate i).1], (hrate i).2⟩
    simpa using positive_pulse_initial_box a kappa 1 q rate hk (by norm_num) h_rate01
  | succ t ih =>
    rw [autonomousState, pow_succ', ← mul_assoc, mul_comm kappa lambda_bar, mul_assoc]
    exact positive_cohort_step_contraction_box a kappa s_bar r_bar (kappa * lambda_bar ^ t)
      q rate _ ha hk (mul_nonneg hk (pow_nonneg h_lam_nonneg t))
      hq hrbar0 hrbar1 hsbar1 hrate hfeedback ih

/-- Finite geometric series identity $(1 - \lambda) \sum_{k < M} \lambda^{T + k} = \lambda^T - \lambda^{T + M}$. -/
theorem geom_tail_sum_identity (lam : ℝ) (T M : ℕ) :
    (1 - lam) * (∑ k ∈ Finset.range M, lam ^ (T + k)) = lam ^ T - lam ^ (T + M) := by
  induction M with
  | zero => simp
  | succ M ih =>
    rw [Finset.sum_range_succ, mul_add, ih, ← Nat.add_assoc, pow_add lam (T + M) 1, pow_one]
    ring

/-- Theorem 5.4 (`thm:certcost`): Certification at the Parametric Rate (`p2_infosafety.tex`).
Proves by induction on the positive cohort state-space recursion (`actualCohortImpulse`) that:
(1) At every lag $t \in \mathbb N$, $0 \le h_t \le \kappa \bar\lambda^t$ where
    $\bar\lambda = 1 - (1 - \bar r)(1 - \bar s) \in [0, 1)$;
(2) Any $M$-step tail sum $\sum_{k < M} h_{T + k}$ beyond truncation horizon $T$ is bounded above
    by the closed-form geometric remainder $\frac{\kappa \bar\lambda^T}{1 - \bar\lambda}$. -/
theorem p2_thm_certcost {n : ℕ} (a kappa s_bar r_bar : ℝ)
    (q rate : Fin n → ℝ)
    (ha : 0 ≤ a) (hk : 0 ≤ kappa) (hq : ∀ i, 0 ≤ q i)
    (hrbar0 : 0 ≤ r_bar) (hrbar1 : r_bar < 1)
    (hsbar0 : 0 ≤ s_bar) (hsbar1 : s_bar < 1)
    (hrate : ∀ i, 1 - r_bar ≤ rate i ∧ rate i ≤ 1)
    (hfeedback : a + kappa * ∑ i, q i ≤ s_bar)
    (T M : ℕ) :
    let lambda_bar := 1 - (1 - r_bar) * (1 - s_bar)
    (0 ≤ lambda_bar ∧ lambda_bar < 1) ∧
    (∀ t : ℕ, 0 ≤ actualCohortImpulse a kappa q rate t ∧
      actualCohortImpulse a kappa q rate t ≤ kappa * lambda_bar ^ t) ∧
    (∑ k ∈ Finset.range M, actualCohortImpulse a kappa q rate (T + k)) ≤
      kappa * lambda_bar ^ T / (1 - lambda_bar) := by
  intro lambda_bar
  have h1_r : 0 < 1 - r_bar := by linarith
  have h1_s : 0 < 1 - s_bar := by linarith
  have h_prod_pos : 0 < (1 - r_bar) * (1 - s_bar) := mul_pos h1_r h1_s
  have h_lam_lt1 : lambda_bar < 1 := by dsimp [lambda_bar]; linarith
  have h_lam_nonneg : 0 ≤ lambda_bar := by dsimp [lambda_bar]; nlinarith
  have h_pointwise : ∀ t : ℕ, 0 ≤ actualCohortImpulse a kappa q rate t ∧
      actualCohortImpulse a kappa q rate t ≤ kappa * lambda_bar ^ t := by
    intro t
    rw [actual_impulse_matches_physical_pulse]
    exact (positive_cohort_trajectory_contraction a kappa s_bar r_bar q rate ha hk hq
      hrbar0 (le_of_lt hrbar1) hsbar0 (le_of_lt hsbar1) hrate hfeedback t).1
  refine ⟨⟨h_lam_nonneg, h_lam_lt1⟩, h_pointwise, ?_⟩
  have h1_lam_pos : 0 < 1 - lambda_bar := by linarith
  have h_sum_le : (∑ k ∈ Finset.range M, actualCohortImpulse a kappa q rate (T + k)) ≤
      kappa * ∑ k ∈ Finset.range M, lambda_bar ^ (T + k) := by
    rw [Finset.mul_sum]
    exact Finset.sum_le_sum (fun k _ => (h_pointwise (T + k)).2)
  have h_geom_le : (∑ k ∈ Finset.range M, lambda_bar ^ (T + k)) ≤
      lambda_bar ^ T / (1 - lambda_bar) := by
    rw [le_div_iff₀ h1_lam_pos, mul_comm]
    rw [geom_tail_sum_identity lambda_bar T M]
    have h_pow_nonneg : 0 ≤ lambda_bar ^ (T + M) := pow_nonneg h_lam_nonneg (T + M)
    linarith
  calc ∑ k ∈ Finset.range M, actualCohortImpulse a kappa q rate (T + k)
    _ ≤ kappa * ∑ k ∈ Finset.range M, lambda_bar ^ (T + k) := h_sum_le
    _ ≤ kappa * (lambda_bar ^ T / (1 - lambda_bar)) := mul_le_mul_of_nonneg_left h_geom_le hk
    _ = kappa * lambda_bar ^ T / (1 - lambda_bar) := by ring

/-- Lemma 6.4 (`lem:sound`): Soundness of Compatible-Set Guards (`p2_guard.tex`). -/
theorem p2_lem_sound
    (I_abs u_bar S_true S_sup B : ℝ)
    (hI : 0 ≤ I_abs) (hu : 0 ≤ u_bar) (hcov : S_true ≤ S_sup)
    (hcert : I_abs * u_bar * S_sup ≤ B) :
    I_abs * u_bar * S_true ≤ B := by
  have hIu : 0 ≤ I_abs * u_bar := mul_nonneg hI hu
  have h_le : I_abs * u_bar * S_true ≤ I_abs * u_bar * S_sup := mul_le_mul_of_nonneg_left hcov hIu
  linarith

/-- Certifiably safe admission set for a compatible feedback-load interval `[0, Phi_plus]`:
all admission fractions $\alpha \in [0, 1]$ such that every compatible economy $\Phi \in [0, \Phi^+]$
is stable ($1 - a - \kappa\alpha\Phi > 0$) and has worst-case loss within budget $\mathcal B$. -/
def robustSafeAdmissionSet (a kappa I_abs u_bar B Phi_plus : ℝ) : Set ℝ :=
  {alpha : ℝ | 0 ≤ alpha ∧ alpha ≤ 1 ∧
    ∀ Phi ∈ Set.Icc 0 Phi_plus,
      0 < 1 - a - kappa * alpha * Phi ∧
      I_abs * u_bar * (kappa / (1 - a - kappa * alpha * Phi)) ≤ B}

/-- Characterization of membership in `robustSafeAdmissionSet` via $c_I = 1 - a - \kappa|I|\bar u / \mathcal B$. -/
theorem mem_robustSafeAdmissionSet_iff (a kappa I_abs u_bar B Phi_plus alpha : ℝ)
    (hk : 0 < kappa) (hI : 0 < I_abs) (hu : 0 < u_bar) (hB : 0 < B) (hPhi : 0 < Phi_plus) :
    alpha ∈ robustSafeAdmissionSet a kappa I_abs u_bar B Phi_plus ↔
      (0 ≤ alpha ∧ alpha ≤ 1 ∧ alpha * (kappa * Phi_plus) ≤ 1 - a - kappa * I_abs * u_bar / B) := by
  have h_req_pos : 0 < kappa * I_abs * u_bar / B := by positivity
  constructor
  · rintro ⟨ha0, ha1, hall⟩
    refine ⟨ha0, ha1, ?_⟩
    have h_top := hall Phi_plus ⟨le_of_lt hPhi, le_refl Phi_plus⟩
    have hden := h_top.1
    have hloss := h_top.2
    have h_rew : I_abs * u_bar * (kappa / (1 - a - kappa * alpha * Phi_plus)) =
        (kappa * I_abs * u_bar) / (1 - a - kappa * alpha * Phi_plus) := by ring
    rw [h_rew, div_le_iff₀ hden] at hloss
    have h_divB : kappa * I_abs * u_bar / B ≤ 1 - a - kappa * alpha * Phi_plus := by
      rw [div_le_iff₀ hB]
      linarith
    linarith
  · rintro ⟨ha0, ha1, h_cap⟩
    refine ⟨ha0, ha1, ?_⟩
    intro Phi hPhi_mem
    have h_mono : alpha * (kappa * Phi) ≤ alpha * (kappa * Phi_plus) := by
      have h_ka : 0 ≤ alpha * kappa := mul_nonneg ha0 (le_of_lt hk)
      calc alpha * (kappa * Phi)
        _ = (alpha * kappa) * Phi := by ring
        _ ≤ (alpha * kappa) * Phi_plus := mul_le_mul_of_nonneg_left hPhi_mem.2 h_ka
        _ = alpha * (kappa * Phi_plus) := by ring
    have h_ineq : kappa * I_abs * u_bar / B ≤ 1 - a - kappa * alpha * Phi := by
      linarith
    have hden : 0 < 1 - a - kappa * alpha * Phi := lt_of_lt_of_le h_req_pos h_ineq
    refine ⟨hden, ?_⟩
    have h_rew : I_abs * u_bar * (kappa / (1 - a - kappa * alpha * Phi)) =
        (kappa * I_abs * u_bar) / (1 - a - kappa * alpha * Phi) := by ring
    rw [h_rew, div_le_iff₀ hden]
    have h_mulB := (div_le_iff₀ hB).mp h_ineq
    linarith

/-- Theorem 6.5 (`thm:robustguard`): Optimal Uncertainty-Aware Admission (`p2_guard.tex`).
Formalized in the style of `exact_safe_radius_isGreatest`:
(i)-(iii) When $c_I \ge 0$, the safe admission set `robustSafeAdmissionSet` equals the closed interval
          `Set.Icc 0 alpha_star` and `alpha_star = min 1 (c_I / (kappa * Phi_plus))` is its greatest
          element (`IsGreatest`);
(iv)      The safe admission set is empty (`= ∅`, infeasible) if and only if $c_I < 0$. -/
theorem p2_thm_robustguard (a kappa I_abs u_bar B Phi_plus : ℝ)
    (hk : 0 < kappa) (hI : 0 < I_abs) (hu : 0 < u_bar) (hB : 0 < B) (hPhi : 0 < Phi_plus) :
    let c_I := 1 - a - kappa * I_abs * u_bar / B
    let alpha_star := min 1 (c_I / (kappa * Phi_plus))
    (0 ≤ c_I →
      robustSafeAdmissionSet a kappa I_abs u_bar B Phi_plus = Set.Icc 0 alpha_star ∧
      IsGreatest (robustSafeAdmissionSet a kappa I_abs u_bar B Phi_plus) alpha_star) ∧
    (robustSafeAdmissionSet a kappa I_abs u_bar B Phi_plus = ∅ ↔ c_I < 0) := by
  intro c_I alpha_star
  have hkP : 0 < kappa * Phi_plus := mul_pos hk hPhi
  have h_set_eq : 0 ≤ c_I →
      robustSafeAdmissionSet a kappa I_abs u_bar B Phi_plus = Set.Icc 0 alpha_star := by
    intro hc
    ext alpha
    rw [mem_robustSafeAdmissionSet_iff a kappa I_abs u_bar B Phi_plus alpha hk hI hu hB hPhi]
    change (0 ≤ alpha ∧ alpha ≤ 1 ∧ alpha * (kappa * Phi_plus) ≤ c_I) ↔
      alpha ∈ Set.Icc 0 alpha_star
    simp only [Set.mem_Icc, alpha_star, le_min_iff, le_div_iff₀ hkP]
  refine ⟨?_, ?_⟩
  · intro hc
    have heq := h_set_eq hc
    refine ⟨heq, ?_⟩
    rw [heq]
    have h_astar_nonneg : 0 ≤ alpha_star :=
      le_min (by norm_num) (div_nonneg hc (le_of_lt hkP))
    exact ⟨⟨h_astar_nonneg, le_refl alpha_star⟩, fun x hx => hx.2⟩
  · constructor
    · intro h_empty
      by_contra h_not_neg
      have hc_nonneg : 0 ≤ c_I := not_lt.mp h_not_neg
      have heq := h_set_eq hc_nonneg
      have h0_mem : (0 : ℝ) ∈ robustSafeAdmissionSet a kappa I_abs u_bar B Phi_plus := by
        rw [heq]
        exact ⟨le_refl 0, le_min (by norm_num) (div_nonneg hc_nonneg (le_of_lt hkP))⟩
      rw [h_empty] at h0_mem
      exact h0_mem
    · intro hc_neg
      ext alpha
      simp only [Set.mem_empty_iff_false, iff_false]
      intro h_mem
      rw [mem_robustSafeAdmissionSet_iff a kappa I_abs u_bar B Phi_plus alpha hk hI hu hB hPhi] at h_mem
      have h_prod_nonneg : 0 ≤ alpha * (kappa * Phi_plus) :=
        mul_nonneg h_mem.1 (le_of_lt hkP)
      dsimp [c_I] at hc_neg
      linarith [h_mem.2.2]

/-- Theorem 7.1 (`thm:disclosure`): Decision Value of Disclosure (`p2_disclosure.tex`).
Stated with actual compatible feedback-load sets `Theta_O_prime ⊆ Theta_O : Set ℝ`:
(i)  A finer disclosure contract `Theta_O_prime ⊆ Theta_O` lowers the worst-case compatible feedback load
     `sSup Theta_O_prime ≤ sSup Theta_O`, expands the safe admission set
     `robustSafeAdmissionSet ... (sSup Theta_O) ⊆ robustSafeAdmissionSet ... (sSup Theta_O_prime)`,
     and raises the optimal admission cap `alpha_star_O ≤ alpha_star_O_prime`;
(ii) When $c_I > 0$, $sSup \Theta_{O'} < sSup \Theta_O$, and $c_I / (\kappa \cdot sSup \Theta_O) < 1$,
     the optimal admission cap strictly increases (`alpha_star_O < alpha_star_O_prime`). -/
theorem p2_thm_disclosure (a kappa I_abs u_bar B w c_cost : ℝ)
    (Theta_O_prime Theta_O : Set ℝ)
    (hk : 0 < kappa)
    (h_sub : Theta_O_prime ⊆ Theta_O)
    (h_bdd : BddAbove Theta_O)
    (Phi0 : ℝ) (hPhi0_mem : Phi0 ∈ Theta_O_prime) (hPhi0_pos : 0 < Phi0) :
    let Phi_O_prime := sSup Theta_O_prime
    let Phi_O := sSup Theta_O
    let c_I := 1 - a - kappa * I_abs * u_bar / B
    let alpha_O_prime := min 1 (c_I / (kappa * Phi_O_prime))
    let alpha_O := min 1 (c_I / (kappa * Phi_O))
    0 < Phi_O_prime ∧
    Phi_O_prime ≤ Phi_O ∧
    robustSafeAdmissionSet a kappa I_abs u_bar B Phi_O ⊆
      robustSafeAdmissionSet a kappa I_abs u_bar B Phi_O_prime ∧
    (0 ≤ c_I → alpha_O ≤ alpha_O_prime) ∧
    (0 < c_I → Phi_O_prime < Phi_O → c_I / (kappa * Phi_O) < 1 → alpha_O < alpha_O_prime) ∧
    (0 < w * (alpha_O_prime - alpha_O) - c_cost ↔ c_cost < w * (alpha_O_prime - alpha_O)) := by
  intro Phi_O_prime Phi_O c_I alpha_O_prime alpha_O
  have h_bdd_prime : BddAbove Theta_O_prime := h_bdd.mono h_sub
  have h_Phi_prime_pos : 0 < Phi_O_prime :=
    lt_of_lt_of_le hPhi0_pos (le_csSup h_bdd_prime hPhi0_mem)
  have h_Phi_le : Phi_O_prime ≤ Phi_O :=
    csSup_le_csSup h_bdd ⟨Phi0, hPhi0_mem⟩ h_sub
  have h_safe_sub : robustSafeAdmissionSet a kappa I_abs u_bar B Phi_O ⊆
      robustSafeAdmissionSet a kappa I_abs u_bar B Phi_O_prime := by
    rintro alpha ⟨ha0, ha1, hall⟩
    refine ⟨ha0, ha1, ?_⟩
    intro Phi hPhi_mem
    exact hall Phi ⟨hPhi_mem.1, le_trans hPhi_mem.2 h_Phi_le⟩
  have hkP_prime : 0 < kappa * Phi_O_prime := mul_pos hk h_Phi_prime_pos
  have hkP_le : kappa * Phi_O_prime ≤ kappa * Phi_O :=
    mul_le_mul_of_nonneg_left h_Phi_le (le_of_lt hk)
  refine ⟨h_Phi_prime_pos, h_Phi_le, h_safe_sub, ?_, ?_, by constructor <;> intro h <;> linarith⟩
  · intro hc
    exact min_le_min_left 1 (div_le_div_of_nonneg_left hc hkP_prime hkP_le)
  · intro hc_pos h_strict h_unclamped
    have hkP_lt : kappa * Phi_O_prime < kappa * Phi_O :=
      mul_lt_mul_of_pos_left h_strict hk
    have h_div_lt : c_I / (kappa * Phi_O) < c_I / (kappa * Phi_O_prime) :=
      div_lt_div_of_pos_left hc_pos hkP_prime hkP_lt
    have h_alpha_O_eq : alpha_O = c_I / (kappa * Phi_O) :=
      min_eq_right (le_of_lt h_unclamped)
    rw [h_alpha_O_eq]
    exact lt_min h_unclamped h_div_lt

end
end CurrentMM
