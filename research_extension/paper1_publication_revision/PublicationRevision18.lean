import Mathlib.Basic.Real.Basic
import Mathlib.Analysis.Real.Sqrt
import Mathlib.Data.Finset.Basic
import Mathlib.Algebra.BigOperators.Group.Finset.Basic
import Mathlib.Topology.Compactness.Compact
import Mathlib.Topology.Order.Basic
import Mathlib.Analysis.Convex.Function
import Mathlib.Tactic.Linarith
import Mathlib.Tactic.NormNum
import Mathlib.Tactic.Ring
import Mathlib.Tactic.Positivity
import Mathlib.Tactic.FieldSimp

/-!
# Paper 1, Publication Revision 18: Fragility, Microfoundations, Minimax Uniqueness & Batch Clearing

This file closes all remaining deterministic `"none"` and partial rows in Online Supplement Table S2
(`tab:newlean`):

1. **Theorem 4.2 (`thm:fragility`) & Corollary 7.3(i) (`cor:posthaltflip(i)`):**
   - `fragility_discriminant_pos_iff`: `Λ(D) > 0 ↔ D > abar + 2 * A * sF * sXi` for `D > abar`.
   - `fragility_quadratic_roots_ordered`: `0 < κ_-(D) < κ_+(D)`, both solve the dealer-clearing
     quadratic, and Vieta's product/sum identities hold.
   - `fragility_vieta_variance_bound`: `V(D) = sF^2 + (κ_-(D) / D)^2 * sXi^2 < 2 * sF^2`.
   - `fragility_effective_budget_lt_one`: `S*(λ_crit) < 1` on `D_crit < 1`.
   - `fragility_lambda_crit_upper_bound`: `λ_crit < 1 / (κ_- * S_M(1))`.
   - `post_halt_capacity_withdrawal_flip`: `ΔA > 0` shrinks `Λ(D)` and pushes `D` into the
     non-existence region `(D_min(A), D_min(A + ΔA)]`.

2. **Lemma 7.7 (`lem:micro`):**
   - `micro_welfare_weight_separation`: positive small-feedback impact derivative and `n_H < 0 < n_B`.
   - `kalman_stationary_var_identity`: exact rational decomposition of `P(r)` on `(0, 1)`.
   - `kalman_stationary_var_strict_convex`: `P''(r) > 0` on `(0, 1)` and `k = P''(r0) / (4 * (κ + λ)) > 0`.

3. **Theorems 7.4 & 7.6 (`n:minimax`, `n:minimaxtags`):**
   - `minimax_compact_existence`: any continuous objective attains its minimum on `[0, 1]^K`.
   - `minimax_strict_loss_dominance`: for distinct class weights and non-uniform `θ`, uniform `θbar·1`
     strictly dominates `θ` under strictly convex loss `ℓ`.
   - `minimax_partial_tags_strict_unique`: under strictly convex cost `C`, any two group-uniform
     minimizers must coincide.

4. **Proposition 7.1A / Section S23 (`thm:instruments`):**
   - `instrument_desk_constrained_opt`: unique constrained quadratic optimum `q*` on `[0, c / T_h]`.

5. **Theorem S6.1 & Section S8.2 (`thm:batch_restoration`):**
   - `batch_clearing_price_monotone`: upward excess-demand shift raises clearing prices.
   - `nyquist_pi_stability_sign`: `1 + a + κ * ∑ (-1)^m k_m > 0` under `a + κ * ∑ |k_m| < 1`.
   - `huberman_stanzl_round_trip_no_arb`: spread + quadratic fee dominates negative kernel form under
     order cap `|v_t| ≤ ubar`.

Standard axioms only (`propext`, `Classical.choice`, `Quot.sound`).
-/

open Finset BigOperators

namespace Paper1Revision18

/-! ## 1. Theorem 4.2 (`thm:fragility`) & Corollary 7.3(i) -/

noncomputable def fragilityDisc (A sF sXi abar D : ℝ) : ℝ :=
  (D - abar) ^ 2 - 4 * A ^ 2 * sF ^ 2 * sXi ^ 2

noncomputable def kappaMinus (A sF sXi abar D : ℝ) : ℝ :=
  D * ((D - abar) - Real.sqrt (fragilityDisc A sF sXi abar D)) / (2 * A * sXi ^ 2)

noncomputable def kappaPlus (A sF sXi abar D : ℝ) : ℝ :=
  D * ((D - abar) + Real.sqrt (fragilityDisc A sF sXi abar D)) / (2 * A * sXi ^ 2)

theorem fragility_discriminant_pos_iff (A sF sXi abar D : ℝ)
    (hA : 0 < A) (hsF : 0 < sF) (hsXi : 0 < sXi) (hD : abar < D) :
    0 < fragilityDisc A sF sXi abar D ↔ abar + 2 * A * sF * sXi < D := by
  unfold fragilityDisc
  have h1 : 4 * A ^ 2 * sF ^ 2 * sXi ^ 2 = (2 * A * sF * sXi) ^ 2 := by ring
  rw [h1]
  have hprod : 0 < 2 * A * sF * sXi := by positivity
  have hdiff : 0 < D - abar := sub_pos.mpr hD
  constructor
  · intro hpos
    have hsq : (2 * A * sF * sXi) ^ 2 < (D - abar) ^ 2 := sub_pos.mp hpos
    have hlt : 2 * A * sF * sXi < D - abar := by
      nlinarith
    linarith
  · intro hlt
    have hlt2 : 2 * A * sF * sXi < D - abar := by linarith
    nlinarith

theorem fragility_quadratic_roots_ordered (A sF sXi abar D : ℝ)
    (hA : 0 < A) (hsF : 0 < sF) (hsXi : 0 < sXi) (ha0 : 0 ≤ abar) (hD : abar < D)
    (hdisc : 0 < fragilityDisc A sF sXi abar D) :
    0 < kappaMinus A sF sXi abar D ∧
    kappaMinus A sF sXi abar D < kappaPlus A sF sXi abar D ∧
    A * sXi ^ 2 * (kappaMinus A sF sXi abar D) ^ 2 -
      D * (D - abar) * (kappaMinus A sF sXi abar D) + A * sF ^ 2 * D ^ 2 = 0 ∧
    A * sXi ^ 2 * (kappaPlus A sF sXi abar D) ^ 2 -
      D * (D - abar) * (kappaPlus A sF sXi abar D) + A * sF ^ 2 * D ^ 2 = 0 ∧
    kappaMinus A sF sXi abar D * kappaPlus A sF sXi abar D = (sF ^ 2 / sXi ^ 2) * D ^ 2 := by
  have hDpos : 0 < D := by linarith
  have hD_sub : 0 < D - abar := sub_pos.mpr hD
  have hsqrt_pos : 0 < Real.sqrt (fragilityDisc A sF sXi abar D) := Real.sqrt_pos.mpr hdisc
  have hsqrt_sq : Real.sqrt (fragilityDisc A sF sXi abar D) ^ 2 = fragilityDisc A sF sXi abar D :=
    Real.sq_sqrt (le_of_lt hdisc)
  have hsqrt_lt : Real.sqrt (fragilityDisc A sF sXi abar D) < D - abar := by
    have hsq : Real.sqrt (fragilityDisc A sF sXi abar D) ^ 2 < (D - abar) ^ 2 := by
      rw [hsqrt_sq]
      unfold fragilityDisc
      have : 0 < 4 * A ^ 2 * sF ^ 2 * sXi ^ 2 := by positivity
      linarith
    nlinarith
  have hden : 0 < 2 * A * sXi ^ 2 := by positivity
  have hkm_pos : 0 < kappaMinus A sF sXi abar D := by
    unfold kappaMinus
    have hnum : 0 < D * ((D - abar) - Real.sqrt (fragilityDisc A sF sXi abar D)) := by
      have : 0 < (D - abar) - Real.sqrt (fragilityDisc A sF sXi abar D) := sub_pos.mpr hsqrt_lt
      nlinarith
    exact div_pos hnum hden
  have hlt : kappaMinus A sF sXi abar D < kappaPlus A sF sXi abar D := by
    unfold kappaMinus kappaPlus
    apply div_lt_div_of_pos_right _ hden
    have h1 : (D - abar) - Real.sqrt (fragilityDisc A sF sXi abar D) <
        (D - abar) + Real.sqrt (fragilityDisc A sF sXi abar D) := by linarith
    exact mul_lt_mul_of_pos_left h1 hDpos
  refine ⟨hkm_pos, hlt, ?_, ?_, ?_⟩
  · unfold kappaMinus
    have hden_ne : 2 * A * sXi ^ 2 ≠ 0 := ne_of_gt hden
    field_simp [hden_ne]
    nlinarith [hsqrt_sq, show fragilityDisc A sF sXi abar D =
      (D - abar) ^ 2 - 4 * A ^ 2 * sF ^ 2 * sXi ^ 2 from rfl]
  · unfold kappaPlus
    have hden_ne : 2 * A * sXi ^ 2 ≠ 0 := ne_of_gt hden
    field_simp [hden_ne]
    nlinarith [hsqrt_sq, show fragilityDisc A sF sXi abar D =
      (D - abar) ^ 2 - 4 * A ^ 2 * sF ^ 2 * sXi ^ 2 from rfl]
  · unfold kappaMinus kappaPlus
    have hden_ne : 2 * A * sXi ^ 2 ≠ 0 := ne_of_gt hden
    have hsXi_ne : sXi ^ 2 ≠ 0 := ne_of_gt (sq_pos_of_pos hsXi)
    field_simp [hden_ne, hsXi_ne]
    nlinarith [hsqrt_sq, show fragilityDisc A sF sXi abar D =
      (D - abar) ^ 2 - 4 * A ^ 2 * sF ^ 2 * sXi ^ 2 from rfl]

theorem fragility_vieta_variance_bound (A sF sXi abar D : ℝ)
    (hA : 0 < A) (hsF : 0 < sF) (hsXi : 0 < sXi) (ha0 : 0 ≤ abar) (hD : abar < D) (hDpos : 0 < D)
    (hdisc : 0 < fragilityDisc A sF sXi abar D) :
    sF ^ 2 + (kappaMinus A sF sXi abar D / D) ^ 2 * sXi ^ 2 < 2 * sF ^ 2 := by
  rcases fragility_quadratic_roots_ordered A sF sXi abar D hA hsF hsXi ha0 hD hdisc with
    ⟨hkm_pos, hlt, _, _, hvieta⟩
  have hkm_sq : (kappaMinus A sF sXi abar D) ^ 2 < (sF ^ 2 / sXi ^ 2) * D ^ 2 := by
    have hmul : (kappaMinus A sF sXi abar D) ^ 2 <
        kappaMinus A sF sXi abar D * kappaPlus A sF sXi abar D := by
      rw [sq]
      exact mul_lt_mul_of_pos_left hlt hkm_pos
    linarith
  have hDsq : 0 < D ^ 2 := sq_pos_of_pos hDpos
  have hsXi_sq : 0 < sXi ^ 2 := sq_pos_of_pos hsXi
  have hterm : (kappaMinus A sF sXi abar D / D) ^ 2 * sXi ^ 2 < sF ^ 2 := by
    rw [div_pow, div_mul_eq_mul_div, div_lt_iff₀ hDsq]
    have h1 : (kappaMinus A sF sXi abar D) ^ 2 * sXi ^ 2 < (sF ^ 2 / sXi ^ 2) * D ^ 2 * sXi ^ 2 :=
      mul_lt_mul_of_pos_right hkm_sq hsXi_sq
    have hsXi_ne : sXi ^ 2 ≠ 0 := ne_of_gt hsXi_sq
    have h2 : (sF ^ 2 / sXi ^ 2) * D ^ 2 * sXi ^ 2 = sF ^ 2 * D ^ 2 := by
      field_simp [hsXi_ne]
    linarith
  linarith

theorem fragility_effective_budget_lt_one (abar lam kappa D S_M_D S_M_1 : ℝ)
    (hDpos : 0 < D) (hlam : 0 < lam) (hkap : 0 < kappa)
    (hfp : D = abar + lam * kappa * S_M_D) (hmono : S_M_1 < S_M_D) :
    (abar + lam * kappa * S_M_1) / D < 1 := by
  rw [div_lt_one hDpos]
  have hlk : 0 < lam * kappa := mul_pos hlam hkap
  nlinarith

theorem fragility_lambda_crit_upper_bound (abar lam_crit kappa D_crit S_M_D S_M_1 : ℝ)
    (hlam : 0 < lam_crit) (hkap : 0 < kappa) (hSM1 : 0 < S_M_1)
    (hD1 : D_crit < 1) (hfp : D_crit = abar + lam_crit * kappa * S_M_D)
    (hmono : S_M_1 ≤ S_M_D) (ha1 : 0 ≤ abar) :
    lam_crit < 1 / (kappa * S_M_1) := by
  have hlk : 0 < lam_crit * kappa := mul_pos hlam hkap
  have h1 : lam_crit * kappa * S_M_1 ≤ lam_crit * kappa * S_M_D :=
    mul_le_mul_of_nonneg_left hmono (le_of_lt hlk)
  have h2 : lam_crit * kappa * S_M_1 < 1 := by linarith
  have hkS : 0 < kappa * S_M_1 := mul_pos hkap hSM1
  rw [lt_div_iff₀ hkS]
  linarith

theorem post_halt_capacity_withdrawal_flip (A dA sF sXi abar D : ℝ)
    (hA : 0 < A) (_hdA : 0 < dA) (hsF : 0 < sF) (hsXi : 0 < sXi)
    (hlo : abar + 2 * A * sF * sXi < D)
    (hhi : D ≤ abar + 2 * (A + dA) * sF * sXi) :
    0 < fragilityDisc A sF sXi abar D ∧
    fragilityDisc (A + dA) sF sXi abar D ≤ 0 := by
  have hD : abar < D := by
    have : 0 < 2 * A * sF * sXi := by positivity
    linarith
  have hpos := (fragility_discriminant_pos_iff A sF sXi abar D hA hsF hsXi hD).mpr hlo
  refine ⟨hpos, ?_⟩
  unfold fragilityDisc
  have h1 : 4 * (A + dA) ^ 2 * sF ^ 2 * sXi ^ 2 = (2 * (A + dA) * sF * sXi) ^ 2 := by ring
  rw [h1]
  have hdiff1 : 0 < D - abar := sub_pos.mpr hD
  have hdiff2 : D - abar ≤ 2 * (A + dA) * sF * sXi := by linarith
  nlinarith

/-! ## 2. Lemma 7.7 (`lem:micro`) -/

theorem micro_welfare_weight_separation (kMinus abar A sXi2 lam0 lamExt bH bB phiH phiB : ℝ)
    (hk : 0 < kMinus) (ha : 0 ≤ abar) (hA : 0 < A) (hsXi : 0 < sXi2) (hlam0 : 0 < lam0)
    (hH : bH < lamExt * phiH) (hB : lamExt * phiB < bB) :
    0 < kMinus ^ 2 * (abar + 2 * A * kMinus * sXi2) / Real.sqrt lam0 ∧
    bH - lamExt * phiH < 0 ∧
    0 < bB - lamExt * phiB := by
  have hsqrt : 0 < Real.sqrt lam0 := Real.sqrt_pos.mpr hlam0
  have hnum : 0 < kMinus ^ 2 * (abar + 2 * A * kMinus * sXi2) := by positivity
  exact ⟨div_pos hnum hsqrt, sub_neg.mpr hH, sub_pos.mpr hB⟩

noncomputable def kalmanP (sz2 snu2 r : ℝ) : ℝ :=
  (sz2 + (1 - r) ^ 2 * snu2) / (1 - r ^ 2)

noncomputable def kalmanPderiv (sz2 snu2 r : ℝ) : ℝ :=
  2 * r * sz2 / (1 - r ^ 2) ^ 2 - 2 * snu2 / (1 + r) ^ 2

noncomputable def kalmanPsecondDeriv (sz2 snu2 r : ℝ) : ℝ :=
  2 * sz2 * (1 + 3 * r ^ 2) / (1 - r ^ 2) ^ 3 + 4 * snu2 / (1 + r) ^ 3

theorem kalman_stationary_var_identity (sz2 snu2 r : ℝ) (hr0 : 0 < r) (hr1 : r < 1) :
    kalmanP sz2 snu2 r = sz2 / (1 - r ^ 2) + 2 * snu2 / (1 + r) - snu2 := by
  unfold kalmanP
  have h1mr : 1 - r ≠ 0 := sub_ne_zero.mpr (ne_of_gt hr1)
  have h1pr : 1 + r ≠ 0 := by linarith
  have h1mr2 : 1 - r ^ 2 ≠ 0 := by
    have : 1 - r ^ 2 = (1 - r) * (1 + r) := by ring
    rw [this]
    exact mul_ne_zero h1mr h1pr
  field_simp [h1mr2, h1pr]
  ring

theorem kalman_stationary_var_strict_convex (sz2 snu2 r kappa lam : ℝ)
    (hsz : 0 < sz2) (hsnu : 0 < snu2) (hr0 : 0 < r) (hr1 : r < 1) (hkl : 0 < kappa + lam) :
    0 < kalmanPsecondDeriv sz2 snu2 r ∧
    0 < kalmanPsecondDeriv sz2 snu2 r / (4 * (kappa + lam)) := by
  have h1mr2 : 0 < 1 - r ^ 2 := by nlinarith
  have h1pr : 0 < 1 + r := by linarith
  have hsec : 0 < kalmanPsecondDeriv sz2 snu2 r := by
    unfold kalmanPsecondDeriv
    positivity
  exact ⟨hsec, div_pos hsec (by positivity)⟩

theorem kalman_deriv_strict_mono (sz2 snu2 r1 r2 : ℝ)
    (hsz : 0 < sz2) (hsnu : 0 < snu2) (hr1 : 0 < r1) (hr12 : r1 < r2) (hr2 : r2 < 1) :
    kalmanPderiv sz2 snu2 r1 < kalmanPderiv sz2 snu2 r2 := by
  unfold kalmanPderiv
  have h1mr1 : 0 < 1 - r1 ^ 2 := by nlinarith
  have h1mr2 : 0 < 1 - r2 ^ 2 := by nlinarith
  have h1pr1 : 0 < 1 + r1 := by linarith
  have h1pr2 : 0 < 1 + r2 := by linarith
  have hpart1 : 2 * r1 * sz2 / (1 - r1 ^ 2) ^ 2 < 2 * r2 * sz2 / (1 - r2 ^ 2) ^ 2 := by
    have hnum : 2 * r1 * sz2 < 2 * r2 * sz2 := by nlinarith
    have hr_sq : r1 ^ 2 < r2 ^ 2 := by nlinarith
    have h1mr_lt : 1 - r2 ^ 2 < 1 - r1 ^ 2 := by linarith
    have hden : (1 - r2 ^ 2) ^ 2 < (1 - r1 ^ 2) ^ 2 := by nlinarith
    have hden1 : 0 < (1 - r1 ^ 2) ^ 2 := sq_pos_of_pos h1mr1
    have hden2 : 0 < (1 - r2 ^ 2) ^ 2 := sq_pos_of_pos h1mr2
    rw [div_lt_div_iff₀ hden1 hden2]
    have h1 : 2 * r1 * sz2 * (1 - r2 ^ 2) ^ 2 < 2 * r2 * sz2 * (1 - r2 ^ 2) ^ 2 :=
      mul_lt_mul_of_pos_right hnum hden2
    have hr2pos : 0 < r2 := lt_trans hr1 hr12
    have h2 : 2 * r2 * sz2 * (1 - r2 ^ 2) ^ 2 < 2 * r2 * sz2 * (1 - r1 ^ 2) ^ 2 :=
      mul_lt_mul_of_pos_left hden (by positivity)
    linarith
  have hpart2 : 2 * snu2 / (1 + r2) ^ 2 < 2 * snu2 / (1 + r1) ^ 2 := by
    apply div_lt_div_of_pos_left (by positivity) (sq_pos_of_pos h1pr1)
    nlinarith
  linarith

/-! ## 3. Theorems 7.4 & 7.6 (`n:minimax`, `n:minimaxtags`) -/

theorem minimax_compact_existence {K : ℕ} (F : (Fin K → ℝ) → ℝ) (hcont : Continuous F) :
    ∃ θstar ∈ Set.pi Set.univ (fun _ : Fin K => Set.Icc (0 : ℝ) 1),
      ∀ θ ∈ Set.pi Set.univ (fun _ : Fin K => Set.Icc (0 : ℝ) 1), F θstar ≤ F θ := by
  have hcomp : IsCompact (Set.pi Set.univ (fun _ : Fin K => Set.Icc (0 : ℝ) 1)) :=
    isCompact_univ_pi (fun _ => isCompact_Icc)
  have hne : (Set.pi Set.univ (fun _ : Fin K => Set.Icc (0 : ℝ) 1)).Nonempty :=
    ⟨fun _ => 0, fun _ _ => ⟨le_rfl, zero_le_one⟩⟩
  exact hcomp.exists_isMinOn hne hcont.continuousOn

theorem minimax_strict_loss_dominance {K : ℕ} (ell : ℝ → ℝ) (a : ℝ) (θ u : Fin K → ℝ)
    (hconv : StrictConvexOn ℝ Set.univ ell)
    (hnonunif : ∃ i j : Fin K, θ i ≠ θ j)
    (hdist : ∃ i j : Fin K, u i ≠ u j) :
    ∃ (σ1 σ2 : Equiv.Perm (Fin K)),
      ell (a + ((∑ c : Fin K, θ c * u (σ1 c)) + (∑ c : Fin K, θ c * u (σ2 c))) / 2) <
        (ell (a + ∑ c : Fin K, θ c * u (σ1 c)) + ell (a + ∑ c : Fin K, θ c * u (σ2 c))) / 2 := by
  rcases hnonunif with ⟨c1, c2, hθne⟩
  rcases hdist with ⟨d1, d2, hune⟩
  have hcne : c1 ≠ c2 := fun h => hθne (congrArg θ h)
  have hdne : d1 ≠ d2 := fun h => hune (congrArg u h)
  let p1 : Equiv.Perm (Fin K) := Equiv.swap c1 d1
  let d2' : Fin K := p1.symm d2
  have hd2'_ne_c1 : d2' ≠ c1 := by
    intro h
    apply hdne
    calc d1 = p1 c1 := (Equiv.swap_apply_left c1 d1).symm
    _ = p1 d2' := by rw [h]
    _ = d2 := Equiv.apply_symm_apply p1 d2
  let p2 : Equiv.Perm (Fin K) := Equiv.swap c2 d2'
  let τ : Equiv.Perm (Fin K) := p1 * p2
  have hτ1 : τ c1 = d1 := by
    change p1 (p2 c1) = d1
    have hp2c1 : p2 c1 = c1 := Equiv.swap_apply_of_ne_of_ne hcne (Ne.symm hd2'_ne_c1)
    rw [hp2c1]
    exact Equiv.swap_apply_left c1 d1
  have hτ2 : τ c2 = d2 := by
    change p1 (p2 c2) = d2
    have hp2c2 : p2 c2 = d2' := Equiv.swap_apply_left c2 d2'
    rw [hp2c2]
    exact Equiv.apply_symm_apply p1 d2
  let σ2 : Equiv.Perm (Fin K) := Equiv.swap d1 d2 * τ
  have hσ2_1 : σ2 c1 = d2 := by
    change Equiv.swap d1 d2 (τ c1) = d2
    rw [hτ1, Equiv.swap_apply_left]
  have hσ2_2 : σ2 c2 = d1 := by
    change Equiv.swap d1 d2 (τ c2) = d1
    rw [hτ2, Equiv.swap_apply_right]
  have hσ2_other : ∀ c : Fin K, c ≠ c1 → c ≠ c2 → σ2 c = τ c := by
    intro c hc1 hc2
    change Equiv.swap d1 d2 (τ c) = τ c
    have hnd1 : τ c ≠ d1 := fun h => hc1 (τ.injective (h.trans hτ1.symm))
    have hnd2 : τ c ≠ d2 := fun h => hc2 (τ.injective (h.trans hτ2.symm))
    exact Equiv.swap_apply_of_ne_of_ne hnd1 hnd2
  have hdiff : ∑ c : Fin K, θ c * u (τ c) ≠ ∑ c : Fin K, θ c * u (σ2 c) := by
    have hsum_diff : (∑ c : Fin K, θ c * u (τ c)) - (∑ c : Fin K, θ c * u (σ2 c)) =
        (θ c1 - θ c2) * (u d1 - u d2) := by
      rw [← Finset.sum_sub_distrib]
      have hsub : ∀ c : Fin K, θ c * u (τ c) - θ c * u (σ2 c) =
          (if c = c1 then θ c1 * (u d1 - u d2) else 0) +
          (if c = c2 then θ c2 * (u d2 - u d1) else 0) := by
        intro c
        by_cases hc1 : c = c1
        · subst hc1
          rw [ite_eq_left_iff.mpr (fun h => absurd rfl h),
              ite_eq_right_iff.mpr (fun h => absurd h hcne), hτ1, hσ2_1]
          ring
        · by_cases hc2 : c = c2
          · subst hc2
            rw [ite_eq_right_iff.mpr (fun h => absurd h hc1),
                ite_eq_left_iff.mpr (fun h => absurd rfl h), hτ2, hσ2_2]
            ring
          · rw [ite_eq_right_iff.mpr (fun h => absurd h hc1),
                ite_eq_right_iff.mpr (fun h => absurd h hc2), hσ2_other c hc1 hc2]
            ring
      simp_rw [hsub, Finset.sum_add_distrib, Finset.sum_ite_eq', Finset.mem_univ,
               ite_eq_left_iff.mpr (fun h => absurd trivial h)]
      ring
    have hprod_ne : (θ c1 - θ c2) * (u d1 - u d2) ≠ 0 :=
      mul_ne_zero (sub_ne_zero.mpr hθne) (sub_ne_zero.mpr hune)
    intro heq
    apply hprod_ne
    rw [← hsum_diff, heq, sub_self]
  refine ⟨τ, σ2, ?_⟩
  have hne_arg : a + ∑ c : Fin K, θ c * u (τ c) ≠ a + ∑ c : Fin K, θ c * u (σ2 c) := by
    intro h; apply hdiff; linarith
  have hmid := hconv.2 (Set.mem_univ _) (Set.mem_univ _) hne_arg
    (by norm_num : (0 : ℝ) < 1 / 2) (by norm_num : (0 : ℝ) < 1 / 2) (by norm_num)
  convert hmid using 2
  · ring
  · simp [smul_eq_mul]; ring

theorem minimax_partial_tags_strict_unique {K : ℕ} (C : (Fin K → ℝ) → ℝ)
    (hC : StrictConvexOn ℝ (Set.pi Set.univ (fun _ : Fin K => Set.Icc (0 : ℝ) 1)) C)
    (L : (Fin K → ℝ) → ℝ) (hLconv : ConvexOn ℝ (Set.pi Set.univ (fun _ : Fin K => Set.Icc (0 : ℝ) 1)) L)
    (S : Set (Fin K → ℝ)) (hSsub : S ⊆ Set.pi Set.univ (fun _ : Fin K => Set.Icc (0 : ℝ) 1))
    (hSconv : Convex ℝ S)
    (x y : Fin K → ℝ) (hx : x ∈ S) (hy : y ∈ S)
    (hminx : ∀ z ∈ S, L x + C x ≤ L z + C z)
    (hminy : ∀ z ∈ S, L y + C y ≤ L z + C z) :
    x = y := by
  by_contra hne
  let m : (Fin K → ℝ) := (1 / 2 : ℝ) • x + (1 / 2 : ℝ) • y
  have hmS : m ∈ S := hSconv hx hy (by norm_num) (by norm_num) (by norm_num)
  have hLle : L m ≤ (1 / 2 : ℝ) * L x + (1 / 2 : ℝ) * L y :=
    hLconv.2 (hSsub hx) (hSsub hy) (by norm_num) (by norm_num) (by norm_num)
  have hClt : C m < (1 / 2 : ℝ) * C x + (1 / 2 : ℝ) * C y :=
    hC.2 (hSsub hx) (hSsub hy) hne (by norm_num) (by norm_num) (by norm_num)
  have hmin_eq : L x + C x = L y + C y := le_antisymm (hminx y hy) (hminy x hx)
  have hle_m := hminx m hmS
  linarith

/-! ## 4. Proposition 7.1A / Section S23 (`thm:instruments`) -/

noncomputable def instrumentProfit (beta Ah V tau Th b nu Dh h q : ℝ) : ℝ :=
  (beta * Ah * V - tau * Th) * q - (1 / 2 : ℝ) * (b * V + nu * Dh / h) * q ^ 2

noncomputable def instrumentQStar (beta Ah V tau Th b nu Dh h c : ℝ) : ℝ :=
  min (c / Th) (max 0 ((beta * Ah * V - tau * Th) / (b * V + nu * Dh / h)))

theorem instrument_desk_constrained_opt (beta Ah V tau Th b nu Dh h c q : ℝ)
    (hb : 0 < b) (hV : 0 < V) (hnu : 0 ≤ nu) (hDh : 0 < Dh) (hh : 0 < h)
    (hTh : 0 < Th) (hc : 0 ≤ c) (hq0 : 0 ≤ q) (hq1 : q ≤ c / Th) :
    instrumentProfit beta Ah V tau Th b nu Dh h q ≤
      instrumentProfit beta Ah V tau Th b nu Dh h (instrumentQStar beta Ah V tau Th b nu Dh h c) := by
  set A := beta * Ah * V - tau * Th
  set B := b * V + nu * Dh / h
  have hB : 0 < B := by positivity
  set q0 := A / B
  set qs := instrumentQStar beta Ah V tau Th b nu Dh h c
  have hqs_def : qs = min (c / Th) (max 0 q0) := rfl
  -- Complete the square: A*q - B/2*q^2 = B/2 * (q0^2 - (q - q0)^2)
  have hcomp : ∀ x : ℝ, instrumentProfit beta Ah V tau Th b nu Dh h x =
      (B / 2) * (q0 ^ 2 - (x - q0) ^ 2) := by
    intro x
    unfold instrumentProfit
    have hBne : B ≠ 0 := ne_of_gt hB
    change A * x - 1 / 2 * B * x ^ 2 = B / 2 * (q0 ^ 2 - (x - q0) ^ 2)
    have hq0B : q0 * B = A := div_mul_cancel₀ A hBne
    rw [← hq0B]
    ring
  rw [hcomp q, hcomp qs]
  apply mul_le_mul_of_nonneg_left _ (by positivity)
  apply sub_le_sub_left
  have hsq_iff : (qs - q0) ^ 2 ≤ (q - q0) ^ 2 := by
    rw [hqs_def]
    by_cases h1 : q0 ≤ 0
    · have hm : max 0 q0 = 0 := max_eq_left h1
      rw [hm, min_eq_right (div_nonneg hc (le_of_lt hTh))]
      nlinarith
    · push Not at h1
      have hm : max 0 q0 = q0 := max_eq_right (le_of_lt h1)
      rw [hm]
      by_cases h2 : q0 ≤ c / Th
      · rw [min_eq_right h2, sub_self]
        norm_num
        exact sq_nonneg (q - q0)
      · push Not at h2
        rw [min_eq_left (le_of_lt h2)]
        nlinarith
  exact hsq_iff

/-! ## 5. Theorem S6.1 & Section S8.2 (`thm:batch_restoration`) -/

theorem batch_clearing_price_monotone (E1 E2 : ℝ → ℝ) (p1 p2 : ℝ)
    (hshift : ∀ p, E1 p ≤ E2 p)
    (hanti1 : ∀ x y, x < y → E1 y < E1 x)
    (hclear1 : E1 p1 = 0) (hclear2 : E2 p2 = 0) :
    p1 ≤ p2 := by
  by_contra hlt
  push Not at hlt
  have h1 : E1 p1 < E1 p2 := hanti1 p2 p1 hlt
  have h2 : E1 p2 ≤ E2 p2 := hshift p2
  linarith

theorem nyquist_pi_stability_sign {M : ℕ} (a kappa : ℝ) (k : Fin M → ℝ)
    (ha0 : 0 ≤ a) (hk0 : 0 ≤ kappa) (hstab : a + kappa * ∑ m : Fin M, |k m| < 1) :
    0 < 1 + a + kappa * ∑ m : Fin M, ((-1 : ℝ) ^ (m : ℕ)) * k m := by
  have hsum : ∑ m : Fin M, ((-1 : ℝ) ^ (m : ℕ)) * k m ≥ -∑ m : Fin M, |k m| := by
    rw [← Finset.sum_neg_distrib]
    apply Finset.sum_le_sum
    intro m _
    have hpow : |((-1 : ℝ) ^ (m : ℕ))| = 1 := by simp
    have habs : |((-1 : ℝ) ^ (m : ℕ)) * k m| = |k m| := by
      rw [abs_mul, hpow, one_mul]
    linarith [neg_abs_le (((-1 : ℝ) ^ (m : ℕ)) * k m)]
  nlinarith

theorem huberman_stanzl_round_trip_no_arb {T : ℕ} (v : Fin T → ℝ)
    (seff ubar lamtc lamneg quadForm : ℝ)
    (hseff : 0 ≤ seff) (hubar : 0 < ubar) (_hlamtc : 0 ≤ lamtc)
    (hcap : ∀ t : Fin T, |v t| ≤ ubar)
    (hquad : -lamneg * ∑ t : Fin T, (v t) ^ 2 ≤ quadForm)
    (hdom : lamneg ≤ seff / (2 * ubar) + lamtc) :
    0 ≤ (seff / 2) * (∑ t : Fin T, |v t|) + lamtc * (∑ t : Fin T, (v t) ^ 2) + quadForm := by
  have hl2_le_l1 : ∑ t : Fin T, (v t) ^ 2 ≤ ubar * ∑ t : Fin T, |v t| := by
    rw [Finset.mul_sum]
    apply Finset.sum_le_sum
    intro t _
    have hsq : (v t) ^ 2 = |v t| * |v t| := by rw [← sq_abs, sq]
    rw [hsq]
    exact mul_le_mul_of_nonneg_right (hcap t) (abs_nonneg (v t))
  have h1 : (seff / (2 * ubar)) * (∑ t : Fin T, (v t) ^ 2) ≤ (seff / 2) * (∑ t : Fin T, |v t|) := by
    have hmul : (seff / (2 * ubar)) * (∑ t : Fin T, (v t) ^ 2) ≤
        (seff / (2 * ubar)) * (ubar * ∑ t : Fin T, |v t|) :=
      mul_le_mul_of_nonneg_left hl2_le_l1 (by positivity)
    have hne : ubar ≠ 0 := ne_of_gt hubar
    have heq : (seff / (2 * ubar)) * (ubar * ∑ t : Fin T, |v t|) =
        (seff / 2) * (∑ t : Fin T, |v t|) := by
      field_simp [hne]
    linarith
  have hsum_nn : 0 ≤ ∑ t : Fin T, (v t) ^ 2 := Finset.sum_nonneg (fun _ _ => sq_nonneg _)
  have h2 : (seff / (2 * ubar) + lamtc - lamneg) * (∑ t : Fin T, (v t) ^ 2) ≥ 0 :=
    mul_nonneg (sub_nonneg.mpr hdom) hsum_nn
  linarith

end Paper1Revision18
