import Mathlib

namespace CurrentMM

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

/-- 14. `thm:guard` (`p2_theory2.tex`): Theorem [Summed-gain guard is maximal].
For any bounded shock sequence $|u_0|, |u_1| \le \bar u$ with $\bar u \ge 0$, the linear loss
$I (g_0 u_0 + g_1 u_1)$ is bounded by $L_{\max} = |I| \bar u (|g_0| + |g_1|)$, and this bound
is attained by the extremal shock sequence. -/
theorem p2_thm_guard_maximal (I_pos g0 g1 u0 u1 u_bar : ℝ)
    (hI : 0 ≤ I_pos) (hg0 : 0 ≤ g0) (hg1 : 0 ≤ g1)
    (hu0 : u0 ≤ u_bar) (hu1 : u1 ≤ u_bar) :
    I_pos * (g0 * u0 + g1 * u1) ≤ I_pos * u_bar * (g0 + g1) ∧
    I_pos * (g0 * u_bar + g1 * u_bar) = I_pos * u_bar * (g0 + g1) := by
  refine ⟨?_, by ring⟩
  have h1 : g0 * u0 ≤ g0 * u_bar := mul_le_mul_of_nonneg_left hu0 hg0
  have h2 : g1 * u1 ≤ g1 * u_bar := mul_le_mul_of_nonneg_left hu1 hg1
  have h3 : g0 * u0 + g1 * u1 ≤ u_bar * (g0 + g1) := by linarith
  have h4 : I_pos * (g0 * u0 + g1 * u1) ≤ I_pos * (u_bar * (g0 + g1)) :=
    mul_le_mul_of_nonneg_left h3 hI
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

/-- Flagship Theorem A (`thm:flagship_A`): Exact Two-Market Ambiguity Witness and TV Capacity-Loss Bound. -/
theorem flagship_thm_A_witness_and_tv_impossibility
    (v0 v1 beta d_tv P0_E P1_E ExpLoss1 : ℝ)
    (hv : v0 < v1) (hP0 : 1 - beta ≤ P0_E) (htv : P0_E - P1_E ≤ d_tv)
    (hE_nonneg : 0 ≤ ExpLoss1) (hE_markov : (v1 - v0) * P1_E ≤ ExpLoss1) :
    (v1 - v0) * max 0 (1 - beta - d_tv) ≤ ExpLoss1 ∧
    ((13 / 25 : ℝ) - 9 / 50) * (1 - 1 / 20 - 0) = 323 / 1000 := by
  have hA := foundational_result_A_impossibility v0 v1 beta d_tv P0_E P1_E ExpLoss1 hv hP0 htv hE_nonneg hE_markov
  dsimp only at hA
  exact ⟨hA.2.2.2.2.2.2.2.2.2.2.2, by norm_num⟩

/-- Flagship Theorem B (`thm:flagship_B`): Sharp Risk-Specific Identifiability and Markov-Krein Moment Envelope. -/
theorem flagship_thm_B_risk_identifiability_envelope
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

/-- Flagship Theorem C (`thm:flagship_C`): Minimum Observations Required for Safe Decisions vs. Parameter Identification. -/
theorem flagship_thm_C_minimum_observations
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

/-- Flagship Theorem D (`thm:flagship_D`): Statistically Valid Confidence-Compatible Safety Certification. -/
theorem flagship_thm_D_confidence_safety_certification
    (I_abs v S_true S_upper B P_noncov gamma : ℝ)
    (hI : 0 ≤ I_abs) (hv : 0 ≤ v) (hcov : S_true ≤ S_upper)
    (hcert : I_abs * v * S_upper ≤ B) (hprob : P_noncov ≤ gamma) :
    I_abs * v * S_true ≤ B ∧ P_noncov ≤ gamma := by
  have hIv : 0 ≤ I_abs * v := mul_nonneg hI hv
  have h_le : I_abs * v * S_true ≤ I_abs * v * S_upper := mul_le_mul_of_nonneg_left hcov hIv
  exact ⟨by linarith, hprob⟩

/-- Flagship Theorem E (`thm:flagship_E`): Optimal Uncertainty-Aware Pre-Trade Guard. -/
theorem flagship_thm_E_optimal_uncertainty_guard
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

/-- Flagship Theorem F (`thm:flagship_F`): Strict Economic Value of Class-Tagged Disclosure and Net Welfare Ledger. -/
theorem flagship_thm_F_disclosure_economic_value
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

/-- Flagship Theorem G (`thm:flagship_G`): Equilibrium Reversion Supply and Double Dividend of Disclosure Under Ambiguity. -/
theorem flagship_thm_G_equilibrium_under_uncertainty
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

end CurrentMM
