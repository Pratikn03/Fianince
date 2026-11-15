import CurrentProofs.Paper1SaturatingSufficiency
import CurrentProofs.Paper1CoreExtensions
import Mathlib.Algebra.BigOperators.Fin
import Mathlib.Basic.Real.Basic
import Mathlib.Tactic.Linarith
import Mathlib.Tactic.Ring

/-!
# Paper 1 (core version), Section 7: Stress Identification and Cubic Separation

Formalizes core structural components of Section 7:
1. **Theorem 7.4, Step 1 (Probes steer the price & invert the flow map):**
   In the probing recursion `x(t) = a * x(t-1) + κ * (F(x_{<t}) + v(t))` with `κ ≠ 0`, any desired
   target sequence `x*` is steered exactly by setting
   `v(t) = (x*(t) - (if t = 0 then 0 else a * x*(t-1))) / κ - F(x*) t`.
   Conversely, observed prices uniquely identify the aggregate feedback flow `F`.
   Consequently, two populations that produce identical price responses under the same probe
   must have identical aggregate feedback flows.

2. **Theorem 7.4, Step 2 (Sufficiency of the Signed Capacity Measure for Odd Policies):**
   For any odd policy shape `ψ` (`ψ(-u) = -ψ(u)`), the saturating flow decomposes as
   `c * ψ(l * m) = (c * sgn(l)) * ψ(|l| * m)`.
   Thus two populations with the same signed capacity measure `μ~` produce identical aggregate
   flow on all price histories.

3. **Proposition 7.3, Part (ii) (Exact First-Tap Cubic Cancellation & Separation):**
   Under a cubic policy expansion `ψ_γ(u) = u - γ * u^3`, at tap 1 after a pulse `v_0 = A`,
   the linear terms cancel identically whenever the kernel weights match (`Σ c_i l_i = Σ c'_j l'_j`).
   The flow discrepancy is exactly `- γ * κ^3 * ΔM_3 * A^3`, and the price discrepancy is
   `- γ * κ^4 * ΔM_3 * A^3`, scaling strictly as `A^3`.
-/

namespace CurrentMM

open Finset

/-- The probing price recursion:
    `x 0 = κ * (F x 0 + v 0)`
    `x (t + 1) = a * x t + κ * (F x (t + 1) + v (t + 1))` -/
def ProbePricePath (a κ : ℝ) (F : (ℕ → ℝ) → ℕ → ℝ) (v : ℕ → ℝ) (x : ℕ → ℝ) : Prop :=
  (x 0 = κ * (F x 0 + v 0)) ∧ (∀ t, x (t + 1) = a * x t + κ * (F x (t + 1) + v (t + 1)))

/-- The steering probe that realizes a target price sequence `x*`. -/
noncomputable def steeringProbe (a κ : ℝ) (F : (ℕ → ℝ) → ℕ → ℝ) (x_star : ℕ → ℝ) : ℕ → ℝ :=
  fun t => match t with
  | 0 => x_star 0 / κ - F x_star 0
  | t + 1 => (x_star (t + 1) - a * x_star t) / κ - F x_star (t + 1)

/-- **Theorem 7.4 (Step 1a): Probes steer the price.**
For any `κ ≠ 0` and any target sequence `x*`, `steeringProbe` realizes `x*` exactly. -/
theorem p1_probe_steer_target (a κ : ℝ) (F : (ℕ → ℝ) → ℕ → ℝ) (x_star : ℕ → ℝ) (hκ : κ ≠ 0) :
    ProbePricePath a κ F (steeringProbe a κ F x_star) x_star := by
  constructor
  · unfold steeringProbe
    have hmul : κ * (x_star 0 / κ) = x_star 0 := mul_div_cancel₀ (x_star 0) hκ
    calc x_star 0 = κ * (x_star 0 / κ) := hmul.symm
         _ = κ * (F x_star 0 + (x_star 0 / κ - F x_star 0)) := by ring
  · intro t
    unfold steeringProbe
    have hmul : κ * ((x_star (t + 1) - a * x_star t) / κ) = x_star (t + 1) - a * x_star t :=
      mul_div_cancel₀ (x_star (t + 1) - a * x_star t) hκ
    calc x_star (t + 1) = a * x_star t + (x_star (t + 1) - a * x_star t) := by ring
         _ = a * x_star t + κ * ((x_star (t + 1) - a * x_star t) / κ) := by rw [hmul]
         _ = a * x_star t + κ * (F x_star (t + 1) + ((x_star (t + 1) - a * x_star t) / κ - F x_star (t + 1))) := by ring

/-- **Theorem 7.4 (Step 1b): Flow reconstruction from observed prices.**
Aggregate flow at each date is uniquely read back from price response `x` and executed probe `v`. -/
theorem p1_probe_flow_recovery (a κ : ℝ) (F : (ℕ → ℝ) → ℕ → ℝ) (v x : ℕ → ℝ)
    (hpath : ProbePricePath a κ F v x) (hκ : κ ≠ 0) :
    (F x 0 = x 0 / κ - v 0) ∧
    (∀ t, F x (t + 1) = (x (t + 1) - a * x t) / κ - v (t + 1)) := by
  constructor
  · have h0 := hpath.1
    have hdiv : x 0 / κ = F x 0 + v 0 := by
      rw [h0, mul_div_cancel_left₀ _ hκ]
    calc F x 0 = (F x 0 + v 0) - v 0 := by ring
         _ = x 0 / κ - v 0 := by rw [← hdiv]
  · intro t
    have ht := hpath.2 t
    have hsub : x (t + 1) - a * x t = κ * (F x (t + 1) + v (t + 1)) := by
      calc x (t + 1) - a * x t = (a * x t + κ * (F x (t + 1) + v (t + 1))) - a * x t := by rw [ht]
           _ = κ * (F x (t + 1) + v (t + 1)) := by ring
    have hdiv : (x (t + 1) - a * x t) / κ = F x (t + 1) + v (t + 1) := by
      rw [hsub, mul_div_cancel_left₀ _ hκ]
    calc F x (t + 1) = (F x (t + 1) + v (t + 1)) - v (t + 1) := by ring
         _ = (x (t + 1) - a * x t) / κ - v (t + 1) := by rw [← hdiv]

/-- **Theorem 7.4 (Step 1c): Identical price paths under the same probe force identical flows.**
If two markets with flow maps `F, F'` follow the same price path `x` under probe `v`, their
aggregate feedback flows `F x t` and `F' x t` are identical at every date `t`. -/
theorem p1_probe_flow_recovery_eq (a κ : ℝ) (F F' : (ℕ → ℝ) → ℕ → ℝ) (v x : ℕ → ℝ)
    (hpath : ProbePricePath a κ F v x) (hpath' : ProbePricePath a κ F' v x) (hκ : κ ≠ 0) :
    ∀ t, F x t = F' x t := by
  intro t
  cases t with
  | zero =>
    have h1 := (p1_probe_flow_recovery a κ F v x hpath hκ).1
    have h2 := (p1_probe_flow_recovery a κ F' v x hpath' hκ).1
    rw [h1, h2]
  | succ t =>
    have h1 := (p1_probe_flow_recovery a κ F v x hpath hκ).2 t
    have h2 := (p1_probe_flow_recovery a κ F' v x hpath' hκ).2 t
    rw [h1, h2]

/-- An odd policy shape satisfies `ψ(-u) = -ψ(u)`. -/
def IsOddPolicy (ψ : ℝ → ℝ) : Prop := ∀ u, ψ (-u) = -ψ u

/-- Sign of a real number in {-1, 0, 1}. -/
noncomputable def realSgn (x : ℝ) : ℝ :=
  if x > 0 then 1 else if x < 0 then -1 else 0

theorem realSgn_zero : realSgn 0 = 0 := by
  unfold realSgn; norm_num

theorem realSgn_pos {x : ℝ} (hx : x > 0) : realSgn x = 1 := by
  unfold realSgn; simp [hx]

theorem realSgn_neg {x : ℝ} (hx : x < 0) : realSgn x = -1 := by
  unfold realSgn
  have hnotpos : ¬(x > 0) := by linarith
  simp [hnotpos, hx]

/-- **Theorem 7.4 (Step 2a): Odd policy signed decomposition.**
For any odd policy, `c * ψ(l * m) = (c * sgn(l)) * ψ(|l| * m)`. -/
theorem p1_odd_policy_decomp (ψ : ℝ → ℝ) (hodd : IsOddPolicy ψ) (c l m : ℝ) :
    c * ψ (l * m) = (c * realSgn l) * ψ (|l| * m) := by
  rcases lt_trichotomy l 0 with hneg | hzero | hpos
  · rw [realSgn_neg hneg, abs_of_neg hneg]
    have hlm : l * m = -(-l * m) := by ring
    rw [hlm, hodd (-l * m)]
    ring
  · subst hzero
    rw [realSgn_zero, abs_zero]
    have h0 : (0 : ℝ) * m = 0 := by ring
    rw [h0]
    have hodd0 : ψ 0 = 0 := by
      have h := hodd 0
      have hneg0 : -(0 : ℝ) = 0 := neg_zero
      rw [hneg0] at h
      linarith
    rw [hodd0]
    ring
  · rw [realSgn_pos hpos, abs_of_pos hpos]
    ring

/-- **Theorem 7.4 (Step 2b): Signed capacity measure sufficiency.**
Two populations whose signed capacity measures `Σ_i c_i sgn(l_i) δ_{(r_i, |l_i|)}` agree on all test
functions produce identical aggregate flow for any price history and any odd policy `ψ`. -/
theorem p1_sat_signed_capacity_sufficiency {K K' : ℕ} (ψ : ℝ → ℝ) (hodd : IsOddPolicy ψ)
    (c l r : Fin K → ℝ) (c' l' r' : Fin K' → ℝ)
    (hμ : ∀ g : ℝ → ℝ → ℝ, ∑ i, (c i * realSgn (l i)) * g (r i) (|l i|) =
                           ∑ j, (c' j * realSgn (l' j)) * g (r' j) (|l' j|))
    (s : ℕ → ℝ) (t : ℕ) :
    satAggFlow ψ c l r s t = satAggFlow ψ c' l' r' s t := by
  unfold satAggFlow
  have h1 : ∑ i, c i * ψ (l i * eqMem (r i) s t) =
            ∑ i, (c i * realSgn (l i)) * ψ (|l i| * eqMem (r i) s t) := by
    refine sum_congr rfl fun i _ => p1_odd_policy_decomp ψ hodd (c i) (l i) (eqMem (r i) s t)
  have h2 : ∑ j, c' j * ψ (l' j * eqMem (r' j) s t) =
            ∑ j, (c' j * realSgn (l' j)) * ψ (|l' j| * eqMem (r' j) s t) := by
    refine sum_congr rfl fun j _ => p1_odd_policy_decomp ψ hodd (c' j) (l' j) (eqMem (r' j) s t)
  rw [h1, h2]
  exact hμ (fun ρ lam => ψ (lam * eqMem ρ s t))

/-- Cubic saturation policy shape: `ψ_γ(u) = u - γ * u^3`. -/
def cubicPolicy (γ : ℝ) (u : ℝ) : ℝ := u - γ * u^3

/-- First tap aggregate feedback flow after a pulse `v_0 = A` at date 0 (where `m_1 = κ * A`). -/
def cubicPulseTap1Flow {K : ℕ} (γ : ℝ) (c l : Fin K → ℝ) (κ A : ℝ) : ℝ :=
  ∑ i, c i * cubicPolicy γ (l i * (κ * A))

/-- **Proposition 7.3(ii): Exact Cubic Separation & Linear Cancellation.**
When two populations have matching linear kernel weights `Σ c_i l_i = Σ c'_j l'_j`, the linear
component of the first tap cancels identically, and the first-tap flow difference is strictly cubic
in probe amplitude `A`:
`F_1(P) - F_1(P') = - γ * κ^3 * (Σ c_i l_i^3 - Σ c'_j (l'_j)^3) * A^3`. -/
theorem p1_cubic_pulse_tap1_kernel_cancel {K K' : ℕ} (γ : ℝ)
    (c l : Fin K → ℝ) (c' l' : Fin K' → ℝ) (κ A : ℝ)
    (hk : ∑ i, c i * l i = ∑ j, c' j * l' j) :
    cubicPulseTap1Flow γ c l κ A - cubicPulseTap1Flow γ c' l' κ A =
      - γ * κ^3 * (∑ i, c i * (l i)^3 - ∑ j, c' j * (l' j)^3) * A^3 := by
  unfold cubicPulseTap1Flow cubicPolicy
  have h_term : ∀ {N : ℕ} (c_arr l_arr : Fin N → ℝ),
      ∑ i, c_arr i * (l_arr i * (κ * A) - γ * (l_arr i * (κ * A))^3) =
      (∑ i, c_arr i * l_arr i) * (κ * A) - γ * (κ * A)^3 * (∑ i, c_arr i * (l_arr i)^3) := by
    intro N c_arr l_arr
    have heq : (fun i : Fin N => c_arr i * (l_arr i * (κ * A) - γ * (l_arr i * (κ * A))^3)) =
               (fun i => (c_arr i * l_arr i) * (κ * A) - (γ * (κ * A)^3 * (c_arr i * (l_arr i)^3))) := by
      ext i; ring
    rw [heq, sum_sub_distrib, ← sum_mul, ← mul_sum]
  rw [h_term c l, h_term c' l', hk]
  ring

/-- **Proposition 7.3(ii), Price Gap Form:**
The resulting first-tap price response gap `x_1(P) - x_1(P') = κ * (F_1(P) - F_1(P'))`
scales as `A^3` with coefficient `- γ * κ^4 * ΔM_3`. -/
theorem p1_cubic_pulse_tap1_price_gap {K K' : ℕ} (γ : ℝ)
    (c l : Fin K → ℝ) (c' l' : Fin K' → ℝ) (κ A : ℝ)
    (hk : ∑ i, c i * l i = ∑ j, c' j * l' j) :
    κ * (cubicPulseTap1Flow γ c l κ A - cubicPulseTap1Flow γ c' l' κ A) =
      - γ * κ^4 * (∑ i, c i * (l i)^3 - ∑ j, c' j * (l' j)^3) * A^3 := by
  rw [p1_cubic_pulse_tap1_kernel_cancel γ c l c' l' κ A hk]
  ring

/-- **Two-atom case only** (the general case is `p1_clip_indep_dilations` and `p1_thm_stress_identification` in
`Paper1StressIdentificationGeneral.lean`). **Theorem 7.4 (Step 3a, 2x2 Vandermonde regular):**
For distinct positive scales `s₁² ≠ s₂²`, a 2-term vanishing moment system
`x + y = 0` and `x * s₁² + y * s₂² = 0` implies `x = 0` and `y = 0`. -/
theorem p1_vandermonde_2x2_invertible (x y s1_sq s2_sq : ℝ)
    (hdiff : s1_sq ≠ s2_sq)
    (h0 : x + y = 0)
    (h1 : x * s1_sq + y * s2_sq = 0) :
    x = 0 ∧ y = 0 := by
  have hy : y = -x := by linarith
  rw [hy] at h1
  have hfact : x * (s1_sq - s2_sq) = 0 := by
    calc x * (s1_sq - s2_sq) = x * s1_sq + (-x) * s2_sq := by ring
         _ = 0 := h1
  cases mul_eq_zero.mp hfact with
  | inl hx =>
    have hy0 : y = 0 := by linarith
    exact ⟨hx, hy0⟩
  | inr hsub =>
    exfalso
    exact hdiff (sub_eq_zero.mp hsub)

/-- **Theorem 7.4 (Step 3a, Distinct Scale Separation):**
In a 2-group odd Taylor series expansion, if two positive scales `s₁ ≠ s₂` satisfy
`d₁ * s₁ + d₂ * s₂ = 0` and `(d₁ * s₁) * s₁² + (d₂ * s₂) * s₂² = 0`, then
`d₁ = 0` and `d₂ = 0`. -/
theorem p1_vandermonde_2x2_weights_zero (d1 d2 s1 s2 : ℝ)
    (hs1_pos : s1 > 0) (hs2_pos : s2 > 0) (hdiff : s1 ≠ s2)
    (h0 : d1 * s1 + d2 * s2 = 0)
    (h1 : (d1 * s1) * s1^2 + (d2 * s2) * s2^2 = 0) :
    d1 = 0 ∧ d2 = 0 := by
  have hs_sq_diff : s1^2 ≠ s2^2 := by
    intro heq
    have hs1_eq_s2 : s1 = s2 := by
      have hs1_sq : s1^2 = s2^2 := heq
      have hs1_nonneg : 0 ≤ s1 := by linarith
      have hs2_nonneg : 0 ≤ s2 := by linarith
      have hs_diff : s1^2 - s2^2 = 0 := by linarith
      have hprod : (s1 - s2) * (s1 + s2) = 0 := by
        calc (s1 - s2) * (s1 + s2) = s1^2 - s2^2 := by ring
             _ = 0 := hs_diff
      cases mul_eq_zero.mp hprod with
      | inl hsub => linarith
      | inr hsum => linarith
    exact hdiff hs1_eq_s2
  have hxy := p1_vandermonde_2x2_invertible (d1 * s1) (d2 * s2) (s1^2) (s2^2) hs_sq_diff h0 h1
  have hd1 : d1 = 0 := by
    have hx := hxy.1
    cases mul_eq_zero.mp hx with
    | inl hd => exact hd
    | inr hs => linarith
  have hd2 : d2 = 0 := by
    have hy := hxy.2
    cases mul_eq_zero.mp hy with
    | inl hd => exact hd
    | inr hs => linarith
  exact ⟨hd1, hd2⟩

/-- Piecewise-linear ramp function `ramp(u) = max(0, u)`. -/
noncomputable def ramp (u : ℝ) : ℝ := max 0 u

theorem ramp_of_nonpos {u : ℝ} (hu : u ≤ 0) : ramp u = 0 := by
  unfold ramp; exact max_eq_left hu

theorem ramp_of_pos {u : ℝ} (hu : u ≥ 0) : ramp u = u := by
  unfold ramp; exact max_eq_right hu

/-- **Theorem 7.4 (Step 3b, Kink Slope Jump Recovery for Hard Limits):**
Consider two distinct saturation points `0 < u₁ < u₂`. If a piecewise-linear response
`g(u) = a₀ * u - d₁ * ramp(u - u₁) - d₂ * ramp(u - u₂)` vanishes for all `u ≥ 0`,
then the initial slope and each jump vanish: `a₀ = 0`, `d₁ = 0`, and `d₂ = 0`. -/
theorem p1_hard_limit_kink_recovery (a0 d1 d2 u1 u2 : ℝ)
    (hu1_pos : 0 < u1) (hu12 : u1 < u2)
    (hg : ∀ u ≥ 0, a0 * u - d1 * ramp (u - u1) - d2 * ramp (u - u2) = 0) :
    a0 = 0 ∧ d1 = 0 ∧ d2 = 0 := by
  have hu_half : 0 ≤ u1 / 2 := by linarith
  have hu_half_pos : u1 / 2 > 0 := by linarith
  have hu_half_lt1 : u1 / 2 - u1 ≤ 0 := by linarith
  have hu_half_lt2 : u1 / 2 - u2 ≤ 0 := by linarith
  have hg_half := hg (u1 / 2) hu_half
  rw [ramp_of_nonpos hu_half_lt1, ramp_of_nonpos hu_half_lt2] at hg_half
  have ha0 : a0 = 0 := by
    have h_simp : a0 * (u1 / 2) = 0 := by linarith
    cases mul_eq_zero.mp h_simp with
    | inl ha => exact ha
    | inr hu => linarith
  have hu_mid : (u1 + u2) / 2 ≥ 0 := by linarith
  have hu_mid_gt1 : (u1 + u2) / 2 - u1 ≥ 0 := by linarith
  have hu_mid_lt2 : (u1 + u2) / 2 - u2 ≤ 0 := by linarith
  have hg_mid := hg ((u1 + u2) / 2) hu_mid
  rw [ha0, zero_mul, zero_sub, ramp_of_pos hu_mid_gt1, ramp_of_nonpos hu_mid_lt2] at hg_mid
  have hd1 : d1 = 0 := by
    have h_zero : d1 * ((u1 + u2) / 2 - u1) = 0 := by linarith
    cases mul_eq_zero.mp h_zero with
    | inl hd => exact hd
    | inr hu => linarith
  have hu_end : u2 + 1 ≥ 0 := by linarith
  have hu_end_gt1 : u2 + 1 - u1 ≥ 0 := by linarith
  have hu_end_gt2 : u2 + 1 - u2 ≥ 0 := by linarith
  have hg_end := hg (u2 + 1) hu_end
  have hramp := ramp_of_pos hu_end_gt2
  have hd2 : d2 = 0 := by
    have h1 : a0 * (u2 + 1) - d1 * ramp (u2 + 1 - u1) - d2 * ramp (u2 + 1 - u2) = 0 := hg_end
    have hzero : a0 * (u2 + 1) = 0 := by rw [ha0, zero_mul]
    have hzero1 : d1 * ramp (u2 + 1 - u1) = 0 := by rw [hd1, zero_mul]
    have h1_sub : d2 * ramp (u2 + 1 - u2) = 0 := by
      linarith [h1, hzero, hzero1]
    have h_zero : d2 * (u2 + 1 - u2) = 0 := by
      rw [hramp] at h1_sub
      exact h1_sub
    cases mul_eq_zero.mp h_zero with
    | inl hd => exact hd
    | inr hu => linarith
  exact ⟨ha0, hd1, hd2⟩

/-- Inside the band `-1 ≤ y ≤ 1`, the hard limit `clip(y) = max(-1, min(1, y))` is the identity. -/
theorem p1_clip_in_band (y : ℝ) (hlo : -1 ≤ y) (hhi : y ≤ 1) :
    max (-1) (min 1 y) = y := by
  have hmin : min 1 y = y := min_eq_right hhi
  rw [hmin]
  exact max_eq_right hlo

/-- **A trade proportional to an exponentially updated forecast follows the same recursion.**
If `u = v / (κ + lam)` at each date and the forecast updates as `v' = (1 - η) v + η x`, then
`u' = (1 - η) u + (η / (κ + lam)) x`. This is algebra on the assumed equalities. It does not prove that the trade is
optimal: the rule `u = v / (κ + lam)` is the first-order condition of the one-period objective
`v u - ((κ + lam) / 2) u²`, which is assumed here, not derived. -/
theorem p1_proportional_trade_recursion (v vt1 u_star u_star_t1 xt η κ lam : ℝ)
    (_hcost : κ + lam > 0)
    (hu : u_star = v / (κ + lam))
    (hvt1 : vt1 = (1 - η) * v + η * xt)
    (hut1 : u_star_t1 = vt1 / (κ + lam)) :
    u_star_t1 = (1 - η) * u_star + (η / (κ + lam)) * xt := by
  rw [hut1, hvt1, hu]
  ring

end CurrentMM
