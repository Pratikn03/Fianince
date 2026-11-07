import CurrentProofs.Paper1SpectralH
import CurrentProofs.Paper1CRActual
import Mathlib.RingTheory.PowerSeries.Basic

/-!
# Paper 1, Theorem `thm:minphase`: the model links

Theorem `thm:minphase` is stated for the rational function `H = tfTop / tfBottom` and for economies whose poles lie
in the open unit disk. This file derives both from the market recursion itself (`cohortStep`, with linear
transition `cohortLinearTransition`). Throughout, the merged weights are `wᵢ = qᵢ ηᵢ` and the memory rates are
`rᵢ = 1 - ηᵢ`.

**Stability.** `p1_eigen_iff_bottom_root` proves that a complex number is an eigenvalue of the (complexified)
transition of the market state `(price, memories)` exactly when it is a zero of `tfBottom`. So "every eigenvalue of
the transition lies in the open unit disk", which is Schur stability of the state recursion, is the same as "every
pole of `H` lies in the open unit disk" (`p1_schur_stable_iff_poles_in_disk`). The eigenvector-to-pole direction uses
distinct rates and nonzero cohort sizes; it also handles the case where the eigenvalue equals a memory rate.

**Transfer function.** `p1_impulse_generating` proves the identity of formal power series
`(∑ₜ hₜ xᵗ) · B̃(x) = κ D̃(x)`, where `hₜ = actualCohortImpulse` is the recursion's price response to a unit trade,
`B̃(x) = x^{K+1} tfBottom(1/x)` and `κ D̃(x) = x^{K+1} tfTop(1/x)`. The two reflection identities are
`p1_tfBottomRev_eval` and `p1_tfTopRev_eval`. With `x = 1/z` this says `∑ₜ hₜ z⁻ᵗ = tfTop(z)/tfBottom(z)`.
-/

namespace CurrentMM

open Polynomial Complex ComplexConjugate Finset

local notation "φℂ" => (algebraMap ℝ ℂ)

/-! ### Stability: eigenvalues of the transition are the poles of `H` -/

/-- The market transition `(price, memories) ↦ (price', memories')` acting on complex vectors. -/
noncomputable def cohortTransC {n : ℕ} (a κ : ℝ) (q rate : Fin n → ℝ) (z : Option (Fin n) → ℂ) :
    Option (Fin n) → ℂ :=
  fun i => i.elim ((a : ℂ) * z none + κ * ∑ j, (q j : ℂ) * z (some j))
    (fun j => (1 - (rate j : ℂ)) * z (some j) + rate j * ((a : ℂ) * z none + κ * ∑ k, (q k : ℂ) * z (some k)))

/-- On real vectors it is the market's linear transition. -/
theorem p1_cohortTransC_real {n : ℕ} (a κ : ℝ) (q rate : Fin n → ℝ) (x : Option (Fin n) → ℝ) :
    cohortTransC a κ q rate (fun i => (x i : ℂ)) = fun i => ((cohortLinearTransition a κ q rate x i : ℝ) : ℂ) := by
  funext i
  cases i <;> simp [cohortTransC, cohortLinearTransition]

theorem p1_bottom_eval_C {K : ℕ} (a κ : ℝ) (w r : Fin K → ℝ) (ζ : ℂ) :
    ((tfBottom a κ w r).map φℂ).eval ζ =
      (ζ - a) * ∏ i, (ζ - r i) - κ * ∑ i, (w i : ℂ) * ζ * ∏ j ∈ univ.erase i, (ζ - r j) := by
  simp only [tfBottom, tfNum, tfDen, Polynomial.map_sub, Polynomial.map_mul, Polynomial.map_prod,
    Polynomial.map_sum, Polynomial.map_X, Polynomial.map_C, eval_sub, eval_mul, eval_prod, eval_finsetSum,
    eval_X, eval_C, Complex.coe_algebraMap]

/-- Off the memory rates, `tfBottom(ζ) = D(ζ) · (ζ - a - κ ∑ wᵢ ζ/(ζ - rᵢ))`. -/
theorem p1_bottom_factor {n : ℕ} (a κ : ℝ) (q rate : Fin n → ℝ) (ζ : ℂ)
    (hne : ∀ j, ζ ≠ 1 - (rate j : ℂ)) :
    ((tfBottom a κ (fun i => q i * rate i) (fun i => 1 - rate i)).map φℂ).eval ζ =
      (∏ j, (ζ - (1 - (rate j : ℂ)))) *
        ((ζ - a) - κ * ∑ i, (q i : ℂ) * rate i * ζ / (ζ - (1 - rate i))) := by
  have hpe : ∀ i, ∏ j ∈ univ.erase i, (ζ - (1 - (rate j : ℂ))) =
      (∏ j, (ζ - (1 - (rate j : ℂ)))) / (ζ - (1 - rate i)) := fun i => by
    rw [eq_div_iff (sub_ne_zero.mpr (hne i))]
    exact Finset.prod_erase_mul univ (fun j => ζ - (1 - (rate j : ℂ))) (mem_univ i)
  rw [p1_bottom_eval_C]
  simp only [Complex.ofReal_mul, Complex.ofReal_sub, Complex.ofReal_one, hpe]
  have hsum : ∑ i, (q i : ℂ) * rate i * ζ * ((∏ j, (ζ - (1 - (rate j : ℂ)))) / (ζ - (1 - rate i))) =
      (∏ j, (ζ - (1 - (rate j : ℂ)))) * ∑ i, (q i : ℂ) * rate i * ζ / (ζ - (1 - rate i)) := by
    rw [Finset.mul_sum]
    exact Finset.sum_congr rfl fun i _ => by ring
  rw [hsum]
  ring

/-- **Eigenvalues of the market transition are exactly the poles of `H`.** -/
theorem p1_eigen_iff_bottom_root {n : ℕ} (a κ : ℝ) (q rate : Fin n → ℝ) (ha : a ≠ 0) (hκ : κ ≠ 0)
    (h0 : ∀ i, 0 < rate i) (h1 : ∀ i, rate i < 1) (hq : ∀ i, q i ≠ 0) (hinj : Function.Injective rate)
    (ζ : ℂ) :
    (∃ z : Option (Fin n) → ℂ, z ≠ 0 ∧ cohortTransC a κ q rate z = ζ • z) ↔
      ((tfBottom a κ (fun i => q i * rate i) (fun i => 1 - rate i)).map φℂ).eval ζ = 0 := by
  have hρ0 : ∀ i, 0 < 1 - rate i := fun i => sub_pos.mpr (h1 i)
  have hρ1 : ∀ i, 1 - rate i < 1 := fun i => by linarith [h0 i]
  have hρinj : Function.Injective (fun i => 1 - rate i) := fun i j h => hinj (by simpa using h)
  have hw : ∀ i, q i * rate i ≠ 0 := fun i => mul_ne_zero (hq i) (h0 i).ne'
  have Z := p1_thm_minphase_zeros a κ (fun i => q i * rate i) (fun i => 1 - rate i) ha hκ hρinj hρ0 hρ1 hw
  have hBne : ∀ j, ((tfBottom a κ (fun i => q i * rate i) (fun i => 1 - rate i)).map φℂ).eval
      ((1 - rate j : ℝ) : ℂ) ≠ 0 := fun j => Z.2.1 _ ((Z.1 _).mpr (Or.inr ⟨j, rfl⟩))
  have hrC : ∀ j, (rate j : ℂ) ≠ 0 := fun j => by exact_mod_cast (h0 j).ne'
  constructor
  · rintro ⟨z, hz0, hz⟩
    have E0 : (a : ℂ) * z none + κ * ∑ j, (q j : ℂ) * z (some j) = ζ * z none := congrFun hz none
    have hY : ∀ j, (ζ - (1 - (rate j : ℂ))) * z (some j) = rate j * ζ * z none := by
      intro j
      have Ej : (1 - (rate j : ℂ)) * z (some j) +
          rate j * ((a : ℂ) * z none + κ * ∑ k, (q k : ℂ) * z (some k)) = ζ * z (some j) :=
        congrFun hz (some j)
      rw [E0] at Ej
      linear_combination -Ej
    by_cases hc : ∃ j, ζ = 1 - (rate j : ℂ)
    · exfalso
      obtain ⟨j, hj⟩ := hc
      have hζ0 : ζ ≠ 0 := by
        rw [hj]
        have : ((1 - rate j : ℝ) : ℂ) ≠ 0 := by exact_mod_cast (hρ0 j).ne'
        simpa [Complex.ofReal_sub] using this
      have hp : z none = 0 := by
        have h3 := hY j
        rw [hj, sub_self, zero_mul] at h3
        have hr : (rate j : ℂ) * (1 - rate j) ≠ 0 := by
          rw [← hj]; exact mul_ne_zero (hrC j) hζ0
        exact (mul_eq_zero.mp h3.symm).resolve_left hr
      have hyk : ∀ k, k ≠ j → z (some k) = 0 := by
        intro k hk
        have h3 := hY k
        rw [hp, mul_zero] at h3
        have hne : ζ - (1 - (rate k : ℂ)) ≠ 0 := by
          rw [hj, show (1 - (rate j : ℂ)) - (1 - rate k) = rate k - rate j by ring]
          exact sub_ne_zero.mpr (by exact_mod_cast fun h => hk (hinj h))
        exact (mul_eq_zero.mp h3).resolve_left hne
      have hyj : z (some j) = 0 := by
        have h3 := E0
        rw [hp, mul_zero, mul_zero, zero_add] at h3
        have hs : ∑ k, (q k : ℂ) * z (some k) = (q j : ℂ) * z (some j) :=
          Finset.sum_eq_single j (fun k _ hk => by rw [hyk k hk, mul_zero]) (by simp)
        rw [hs] at h3
        have hqj : (q j : ℂ) ≠ 0 := by exact_mod_cast hq j
        have hκC : (κ : ℂ) ≠ 0 := by exact_mod_cast hκ
        exact (mul_eq_zero.mp ((mul_eq_zero.mp h3).resolve_left hκC)).resolve_left hqj
      apply hz0
      funext i
      cases i with
      | none => exact hp
      | some k =>
        by_cases hk : k = j
        · rw [hk]; exact hyj
        · exact hyk k hk
    · push_neg at hc
      have hp : z none ≠ 0 := by
        intro hp0
        apply hz0
        funext i
        cases i with
        | none => exact hp0
        | some k =>
          have h3 := hY k
          rw [hp0, mul_zero] at h3
          exact (mul_eq_zero.mp h3).resolve_left (sub_ne_zero.mpr (hc k))
      have hy : ∀ k, z (some k) = rate k * ζ * z none / (ζ - (1 - rate k)) := fun k => by
        rw [eq_div_iff (sub_ne_zero.mpr (hc k)), mul_comm (z (some k))]
        exact hY k
      have hbr : (ζ - a) - κ * ∑ i, (q i : ℂ) * rate i * ζ / (ζ - (1 - rate i)) = 0 := by
        have h := E0
        simp only [hy] at h
        have hs : ∑ j, (q j : ℂ) * (rate j * ζ * z none / (ζ - (1 - rate j))) =
            z none * ∑ j, (q j : ℂ) * rate j * ζ / (ζ - (1 - rate j)) := by
          rw [Finset.mul_sum]
          exact Finset.sum_congr rfl fun j _ => by ring
        rw [hs] at h
        have h2 : z none * ((ζ - a) - κ * ∑ j, (q j : ℂ) * rate j * ζ / (ζ - (1 - rate j))) = 0 := by
          linear_combination -h
        exact (mul_eq_zero.mp h2).resolve_left hp
      rw [p1_bottom_factor a κ q rate ζ hc, hbr, mul_zero]
  · intro hB
    have hne : ∀ j, ζ ≠ 1 - (rate j : ℂ) := by
      intro j h
      apply hBne j
      have e : ((1 - rate j : ℝ) : ℂ) = ζ := by rw [h, Complex.ofReal_sub, Complex.ofReal_one]
      rw [e]
      exact hB
    have hD : (∏ j, (ζ - (1 - (rate j : ℂ)))) ≠ 0 :=
      prod_ne_zero_iff.mpr fun j _ => sub_ne_zero.mpr (hne j)
    have hbr : (ζ - a) - κ * ∑ i, (q i : ℂ) * rate i * ζ / (ζ - (1 - rate i)) = 0 := by
      have h := hB
      rw [p1_bottom_factor a κ q rate ζ hne] at h
      exact (mul_eq_zero.mp h).resolve_left hD
    have hP : (a : ℂ) * 1 + κ * ∑ j, (q j : ℂ) * ((rate j : ℂ) * ζ / (ζ - (1 - rate j))) = ζ := by
      have hs : ∑ j, (q j : ℂ) * ((rate j : ℂ) * ζ / (ζ - (1 - rate j))) =
          ∑ j, (q j : ℂ) * rate j * ζ / (ζ - (1 - rate j)) :=
        Finset.sum_congr rfl fun j _ => by ring
      rw [hs]
      linear_combination -hbr
    refine ⟨fun i => i.elim 1 (fun j => (rate j : ℂ) * ζ / (ζ - (1 - rate j))), ?_, ?_⟩
    · intro h
      have := congrFun h none
      simp at this
    · funext i
      cases i with
      | none =>
        show (a : ℂ) * 1 + κ * ∑ j, (q j : ℂ) * ((rate j : ℂ) * ζ / (ζ - (1 - rate j))) = ζ * 1
        rw [hP, mul_one]
      | some j =>
        show (1 - (rate j : ℂ)) * ((rate j : ℂ) * ζ / (ζ - (1 - rate j))) +
            rate j * ((a : ℂ) * 1 + κ * ∑ k, (q k : ℂ) * ((rate k : ℂ) * ζ / (ζ - (1 - rate k)))) =
          ζ * ((rate j : ℂ) * ζ / (ζ - (1 - rate j)))
        rw [hP]
        have hx : ζ - (1 - (rate j : ℂ)) ≠ 0 := sub_ne_zero.mpr (hne j)
        have hu : (rate j : ℂ) * ζ / (ζ - (1 - rate j)) * (ζ - (1 - (rate j : ℂ))) = rate j * ζ :=
          div_mul_cancel₀ _ hx
        linear_combination -hu

/-- **Schur stability of the state recursion is the pole condition of Theorem `thm:minphase`.** -/
theorem p1_schur_stable_iff_poles_in_disk {n : ℕ} (a κ : ℝ) (q rate : Fin n → ℝ) (ha : a ≠ 0) (hκ : κ ≠ 0)
    (h0 : ∀ i, 0 < rate i) (h1 : ∀ i, rate i < 1) (hq : ∀ i, q i ≠ 0) (hinj : Function.Injective rate) :
    (∀ ζ : ℂ, (∃ z : Option (Fin n) → ℂ, z ≠ 0 ∧ cohortTransC a κ q rate z = ζ • z) → ‖ζ‖ < 1) ↔
      (∀ ζ : ℂ, ((tfBottom a κ (fun i => q i * rate i) (fun i => 1 - rate i)).map φℂ).eval ζ = 0 → ‖ζ‖ < 1) := by
  constructor
  · intro h ζ hζ
    exact h ζ ((p1_eigen_iff_bottom_root a κ q rate ha hκ h0 h1 hq hinj ζ).mpr hζ)
  · intro h ζ hζ
    exact h ζ ((p1_eigen_iff_bottom_root a κ q rate ha hκ h0 h1 hq hinj ζ).mp hζ)

/-! ### The transfer function of the recursion -/

/-- `x^K D(1/x) = ∏ (1 - rᵢ x)`. -/
noncomputable def tfDenRev {K : ℕ} (r : Fin K → ℝ) : ℝ[X] := ∏ i, (1 - C (r i) * X)

/-- `x^K N(1/x) / x = ∑ wᵢ ∏_{j ≠ i} (1 - rⱼ x)`. -/
noncomputable def tfNumRev {K : ℕ} (w r : Fin K → ℝ) : ℝ[X] :=
  ∑ i, C (w i) * ∏ j ∈ univ.erase i, (1 - C (r j) * X)

/-- `x^{K+1} tfBottom(1/x)`. -/
noncomputable def tfBottomRev {K : ℕ} (a κ : ℝ) (w r : Fin K → ℝ) : ℝ[X] :=
  (1 - C a * X) * tfDenRev r - C κ * X * tfNumRev w r

/-- `x^{K+1} tfTop(1/x)`. -/
noncomputable def tfTopRev {K : ℕ} (κ : ℝ) (r : Fin K → ℝ) : ℝ[X] := C κ * tfDenRev r

theorem p1_prod_reflect {K : ℕ} (r : Fin K → ℝ) (x : ℂ) (hx : x ≠ 0) (s : Finset (Fin K)) :
    x ^ s.card * ∏ j ∈ s, (x⁻¹ - (r j : ℂ)) = ∏ j ∈ s, (1 - (r j : ℂ) * x) := by
  rw [← Finset.prod_const, ← Finset.prod_mul_distrib]
  exact Finset.prod_congr rfl fun j _ => by rw [mul_sub, mul_inv_cancel₀ hx]; ring

theorem p1_tfBottomRev_eval {K : ℕ} (a κ : ℝ) (w r : Fin K → ℝ) (x : ℂ) (hx : x ≠ 0) :
    ((tfBottomRev a κ w r).map φℂ).eval x = x ^ (K + 1) * ((tfBottom a κ w r).map φℂ).eval x⁻¹ := by
  have hL : ((tfBottomRev a κ w r).map φℂ).eval x =
      (1 - a * x) * ∏ i, (1 - (r i : ℂ) * x) - κ * x * ∑ i, (w i : ℂ) * ∏ j ∈ univ.erase i, (1 - (r j : ℂ) * x) := by
    simp only [tfBottomRev, tfNumRev, tfDenRev, Polynomial.map_sub, Polynomial.map_mul, Polynomial.map_prod,
      Polynomial.map_sum, Polynomial.map_one, Polynomial.map_X, Polynomial.map_C, eval_sub, eval_mul, eval_prod,
      eval_finsetSum, eval_one, eval_X, eval_C, Complex.coe_algebraMap]
  rw [hL, p1_bottom_eval_C]
  have hcard : ∀ i : Fin K, (univ.erase i).card + 1 = K := fun i => by
    rw [Finset.card_erase_add_one (mem_univ i), card_univ, Fintype.card_fin]
  have hP : x ^ K * ∏ j, (x⁻¹ - (r j : ℂ)) = ∏ j, (1 - (r j : ℂ) * x) := by
    have := p1_prod_reflect r x hx univ
    rwa [card_univ, Fintype.card_fin] at this
  have hhead : x ^ (K + 1) * ((x⁻¹ - a) * ∏ j, (x⁻¹ - (r j : ℂ))) = (1 - a * x) * ∏ j, (1 - (r j : ℂ) * x) := by
    rw [← hP]
    calc x ^ (K + 1) * ((x⁻¹ - a) * ∏ j, (x⁻¹ - (r j : ℂ)))
        = x ^ K * (∏ j, (x⁻¹ - (r j : ℂ))) * (x * x⁻¹) - a * x * (x ^ K * ∏ j, (x⁻¹ - (r j : ℂ))) := by ring
      _ = (1 - a * x) * (x ^ K * ∏ j, (x⁻¹ - (r j : ℂ))) := by rw [mul_inv_cancel₀ hx]; ring
  have hterm : ∀ i, x ^ (K + 1) * ((w i : ℂ) * x⁻¹ * ∏ j ∈ univ.erase i, (x⁻¹ - (r j : ℂ))) =
      x * ((w i : ℂ) * ∏ j ∈ univ.erase i, (1 - (r j : ℂ) * x)) := fun i => by
    rw [← p1_prod_reflect r x hx (univ.erase i)]
    have e : x ^ (K + 1) = x ^ (univ.erase i).card * x * x := by rw [← pow_succ, ← pow_succ, hcard i]
    rw [e]
    calc x ^ (univ.erase i).card * x * x * ((w i : ℂ) * x⁻¹ * ∏ j ∈ univ.erase i, (x⁻¹ - (r j : ℂ)))
        = x * ((w i : ℂ) * (x ^ (univ.erase i).card * ∏ j ∈ univ.erase i, (x⁻¹ - (r j : ℂ)))) * (x * x⁻¹) := by
          ring
      _ = _ := by rw [mul_inv_cancel₀ hx, mul_one]
  have hsum : x ^ (K + 1) * ∑ i, (w i : ℂ) * x⁻¹ * ∏ j ∈ univ.erase i, (x⁻¹ - (r j : ℂ)) =
      x * ∑ i, (w i : ℂ) * ∏ j ∈ univ.erase i, (1 - (r j : ℂ) * x) := by
    rw [Finset.mul_sum, Finset.mul_sum]
    exact Finset.sum_congr rfl fun i _ => hterm i
  linear_combination (-1 : ℂ) * hhead + (κ : ℂ) * hsum

theorem p1_tfTopRev_eval {K : ℕ} (κ : ℝ) (r : Fin K → ℝ) (x : ℂ) (hx : x ≠ 0) :
    ((tfTopRev κ r).map φℂ).eval x = x ^ (K + 1) * ((tfTop κ r).map φℂ).eval x⁻¹ := by
  have hP : x ^ K * ∏ j, (x⁻¹ - (r j : ℂ)) = ∏ j, (1 - (r j : ℂ) * x) := by
    have := p1_prod_reflect r x hx univ
    rwa [card_univ, Fintype.card_fin] at this
  simp only [tfTopRev, tfDenRev, tfTop, tfDen, Polynomial.map_sub, Polynomial.map_mul, Polynomial.map_prod,
    Polynomial.map_one, Polynomial.map_X, Polynomial.map_C, eval_sub, eval_mul, eval_prod, eval_one, eval_X,
    eval_C, Complex.coe_algebraMap]
  rw [← hP]
  calc (κ : ℂ) * (x ^ K * ∏ j, (x⁻¹ - (r j : ℂ)))
      = (κ : ℂ) * (x ^ K * ∏ j, (x⁻¹ - (r j : ℂ))) * (x * x⁻¹) := by rw [mul_inv_cancel₀ hx, mul_one]
    _ = x ^ (K + 1) * ((κ : ℂ) * x⁻¹ * ∏ j, (x⁻¹ - (r j : ℂ))) := by ring

/-- `∑ₘ rᵐ xᵐ · (1 - r x) = 1`. -/
theorem p1_geom_series_mul (r : ℝ) :
    PowerSeries.mk (fun m => r ^ m) * (1 - PowerSeries.C r * PowerSeries.X) = 1 := by
  ext m
  have e : PowerSeries.mk (fun m => r ^ m) * (1 - PowerSeries.C r * PowerSeries.X) =
      PowerSeries.mk (fun m => r ^ m) - PowerSeries.C r * (PowerSeries.X * PowerSeries.mk (fun m => r ^ m)) := by
    ring
  rw [e, map_sub, PowerSeries.coeff_C_mul, PowerSeries.coeff_mk, PowerSeries.coeff_one]
  rcases m with _ | m
  · simp
  · rw [PowerSeries.coeff_succ_X_mul, PowerSeries.coeff_mk, if_neg (Nat.succ_ne_zero m)]
    show r ^ (m + 1) - r * r ^ m = 0
    ring

theorem p1_coe_ps (p : ℝ[X]) : (p : PowerSeries ℝ) = Polynomial.coeToPowerSeries.ringHom p := rfl

/-- **The recursion's impulse response has transfer function `tfTop / tfBottom`.** As formal power series in
`x = 1/z`: `(∑ₜ hₜ xᵗ) · x^{K+1} tfBottom(1/x) = x^{K+1} tfTop(1/x)`. -/
theorem p1_impulse_generating {n : ℕ} (a κ : ℝ) (q rate : Fin n → ℝ) :
    PowerSeries.mk (actualCohortImpulse a κ q rate) *
        ((tfBottomRev a κ (fun i => q i * rate i) (fun i => 1 - rate i) : ℝ[X]) : PowerSeries ℝ) =
      ((tfTopRev κ (fun i => 1 - rate i) : ℝ[X]) : PowerSeries ℝ) := by
  -- the closed-loop recursion as a power-series identity
  have hrec : PowerSeries.mk (actualCohortImpulse a κ q rate) =
      PowerSeries.C κ + PowerSeries.X * (PowerSeries.C a * PowerSeries.mk (actualCohortImpulse a κ q rate) +
        PowerSeries.C κ * (PowerSeries.mk (cohortKernel q rate) * PowerSeries.mk (actualCohortImpulse a κ q rate))) := by
    ext m
    rcases m with _ | m
    · simp [p1_impulse_zero]
    · simp only [PowerSeries.coeff_mk, map_add, PowerSeries.coeff_succ_X_mul, PowerSeries.coeff_C_mul]
      rw [PowerSeries.coeff_mul, Finset.Nat.sum_antidiagonal_eq_sum_range_succ_mk]
      simp only [PowerSeries.coeff_mk]
      rw [PowerSeries.coeff_C, if_neg (Nat.succ_ne_zero m), zero_add]
      exact p1_impulse_closed_loop_recursion a κ q rate m
  -- the kernel's generating function times `D̃` is `Ñ`
  have hGs : PowerSeries.mk (cohortKernel q rate) =
      ∑ i, PowerSeries.C (q i * rate i) * PowerSeries.mk (fun m => (1 - rate i) ^ m) := by
    ext m
    simp only [cohortKernel, PowerSeries.coeff_mk, map_sum, PowerSeries.coeff_C_mul]
  have hD : ((tfDenRev (fun i => 1 - rate i) : ℝ[X]) : PowerSeries ℝ) =
      ∏ i, (1 - PowerSeries.C (1 - rate i) * PowerSeries.X) := by
    rw [p1_coe_ps]
    unfold tfDenRev
    simp only [map_prod, map_sub, map_one, map_mul, Polynomial.coeToPowerSeries.ringHom_apply, Polynomial.coe_C,
      Polynomial.coe_X]
  have hN : ((tfNumRev (fun i => q i * rate i) (fun i => 1 - rate i) : ℝ[X]) : PowerSeries ℝ) =
      ∑ i, PowerSeries.C (q i * rate i) * ∏ j ∈ univ.erase i, (1 - PowerSeries.C (1 - rate j) * PowerSeries.X) := by
    rw [p1_coe_ps]
    unfold tfNumRev
    simp only [map_sum, map_prod, map_sub, map_one, map_mul, Polynomial.coeToPowerSeries.ringHom_apply,
      Polynomial.coe_C, Polynomial.coe_X]
  have hG : PowerSeries.mk (cohortKernel q rate) * ((tfDenRev (fun i => 1 - rate i) : ℝ[X]) : PowerSeries ℝ) =
      ((tfNumRev (fun i => q i * rate i) (fun i => 1 - rate i) : ℝ[X]) : PowerSeries ℝ) := by
    rw [hGs, hD, hN, Finset.sum_mul]
    refine Finset.sum_congr rfl fun i _ => ?_
    have e : (1 - PowerSeries.C (1 - rate i) * PowerSeries.X) *
        ∏ j ∈ univ.erase i, (1 - PowerSeries.C (1 - rate j) * PowerSeries.X) =
        ∏ j, (1 - PowerSeries.C (1 - rate j) * PowerSeries.X) :=
      Finset.mul_prod_erase univ (fun j => 1 - PowerSeries.C (1 - rate j) * PowerSeries.X) (mem_univ i)
    rw [← e, ← mul_assoc, mul_assoc (PowerSeries.C (q i * rate i)), p1_geom_series_mul, mul_one]
  have hB : ((tfBottomRev a κ (fun i => q i * rate i) (fun i => 1 - rate i) : ℝ[X]) : PowerSeries ℝ) =
      (1 - PowerSeries.C a * PowerSeries.X) * ((tfDenRev (fun i => 1 - rate i) : ℝ[X]) : PowerSeries ℝ) -
        PowerSeries.C κ * PowerSeries.X *
          ((tfNumRev (fun i => q i * rate i) (fun i => 1 - rate i) : ℝ[X]) : PowerSeries ℝ) := by
    rw [p1_coe_ps]
    unfold tfBottomRev
    simp only [map_sub, map_one, map_mul, Polynomial.coeToPowerSeries.ringHom_apply, Polynomial.coe_C,
      Polynomial.coe_X]
  have hT : ((tfTopRev κ (fun i => 1 - rate i) : ℝ[X]) : PowerSeries ℝ) =
      PowerSeries.C κ * ((tfDenRev (fun i => 1 - rate i) : ℝ[X]) : PowerSeries ℝ) := by
    rw [p1_coe_ps]
    unfold tfTopRev
    simp only [map_mul, Polynomial.coeToPowerSeries.ringHom_apply, Polynomial.coe_C]
  rw [hB, hT]
  linear_combination ((tfDenRev (fun i => 1 - rate i) : ℝ[X]) : PowerSeries ℝ) * hrec +
    (PowerSeries.C κ * PowerSeries.X * PowerSeries.mk (actualCohortImpulse a κ q rate)) * hG

end CurrentMM
