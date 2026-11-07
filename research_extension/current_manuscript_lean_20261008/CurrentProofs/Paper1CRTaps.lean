import CurrentProofs.Paper1CRActual
import CurrentProofs.Paper1CRScaling
import CurrentProofs.Paper1FisherBounds

/-!
# Paper 1, Proposition S7.1 (iii), Phase 5: the observed taps and their Jacobian

The observed record is the closed-loop price response `h₀, …, h_T` to a unit probe from rest. By
`p1_impulse_closed_loop_recursion` it is determined by the feedback kernel `k`:
`h₀ = κ`, `h_{j+1} = a h_j + κ ∑_{m ≤ j} k_m h_{j-m}`. This file works with that recursion directly.

* `p1Tap`, `p1_actual_eq_tap`: the recursion, and the identity `actualCohortImpulse = p1Tap (cohortKernel)`.
* `p1K2`, `p1TapW`, `p1_actual_two_eq_tapW`: for two cohorts, the taps as functions of
  `θ = (w₁, w₂, r₁, r₂)` with `wᵢ = qᵢηᵢ` and `rᵢ = 1 - ηᵢ`. They equal the model's actual taps.
* `p1TapJac`: the `(T+1) × 4` Jacobian of `θ ↦ (h₀, …, h_T)`, defined by Fréchet derivatives.
* `p1TapD`, `p1_tap_hasDerivAt`: differentiating the recursion along a curve of kernels.
* `p1_tapJac_mulVec`: `(J x)_t = p1TapD (k(θ₀)) (Dk[x]) t`, so the Jacobian applied to a direction is computed from
  the kernel's directional derivative `Dk[x] = p1K2D θ₀ x`.
* `p1TapM`, `p1TapG`, `p1_tap_abs_le`, `p1_tapD_abs_le`: on a fixed horizon, explicit majorants. If `|k_m| ≤ K₀` and
  `|Dk_m| ≤ E` for `m < N`, then `|h_s| ≤ M_j` and `|(Dh)_s| ≤ E G_j` for `s ≤ j ≤ N`, where `M` and `G` depend only on
  `|a|`, a bound on `|κ|`, `K₀` and `j`.
-/

namespace CurrentMM

open Finset Matrix

/-- Taps of the closed-loop response with feedback kernel `k`. -/
noncomputable def p1Tap (a κ : ℝ) (k : ℕ → ℝ) : ℕ → ℝ
  | 0 => κ
  | j + 1 => a * p1Tap a κ k j + κ * ∑ m ∈ range (j + 1), k m * p1Tap a κ k (j - m)
termination_by j => j
decreasing_by all_goals first | omega | (simp_wf; omega)

theorem p1_tap_zero (a κ : ℝ) (k : ℕ → ℝ) : p1Tap a κ k 0 = κ := by
  first
  | rw [p1Tap]
  | simp only [p1Tap]
  | exact p1Tap.eq_1 ..

theorem p1_tap_succ (a κ : ℝ) (k : ℕ → ℝ) (j : ℕ) :
    p1Tap a κ k (j + 1) = a * p1Tap a κ k j + κ * ∑ m ∈ range (j + 1), k m * p1Tap a κ k (j - m) := by
  first
  | rw [p1Tap]
  | exact p1Tap.eq_2 ..
  | simp only [p1Tap]

/-- **The model's taps are the recursion's taps.** -/
theorem p1_actual_eq_tap {n : ℕ} (a κ : ℝ) (q rate : Fin n → ℝ) (j : ℕ) :
    actualCohortImpulse a κ q rate j = p1Tap a κ (cohortKernel q rate) j := by
  refine Nat.strong_induction_on j ?_
  intro j ih
  rcases j with _ | j
  · rw [p1_impulse_zero, p1_tap_zero]
  · rw [p1_impulse_closed_loop_recursion, p1_tap_succ, ih j (Nat.lt_succ_self j)]
    congr 2
    exact sum_congr rfl fun m _ => by rw [ih (j - m) (by omega)]

/-- Two-cohort kernel in the coordinates `θ = (w₁, w₂, r₁, r₂)`. -/
def p1K2 (θ : Fin 4 → ℝ) (m : ℕ) : ℝ := θ 0 * θ 2 ^ m + θ 1 * θ 3 ^ m

theorem p1_cohortKernel_two (q rate : Fin 2 → ℝ) (m : ℕ) :
    cohortKernel q rate m = p1K2 ![q 0 * rate 0, q 1 * rate 1, 1 - rate 0, 1 - rate 1] m := by
  first
  | (simp [cohortKernel, p1K2, Fin.sum_univ_two]; done)
  | (simp [cohortKernel, p1K2, Fin.sum_univ_two]; ring)

/-- The taps as functions of `θ = (w₁, w₂, r₁, r₂)`. -/
noncomputable def p1TapW (a κ : ℝ) (θ : Fin 4 → ℝ) (j : ℕ) : ℝ := p1Tap a κ (p1K2 θ) j

/-- **For two cohorts, `p1TapW` is the model's actual price response**, at `wᵢ = qᵢηᵢ`, `rᵢ = 1 - ηᵢ`. -/
theorem p1_actual_two_eq_tapW (a κ : ℝ) (q rate : Fin 2 → ℝ) (j : ℕ) :
    actualCohortImpulse a κ q rate j = p1TapW a κ ![q 0 * rate 0, q 1 * rate 1, 1 - rate 0, 1 - rate 1] j := by
  rw [p1_actual_eq_tap]
  have e : cohortKernel q rate = p1K2 ![q 0 * rate 0, q 1 * rate 1, 1 - rate 0, 1 - rate 1] :=
    funext (p1_cohortKernel_two q rate)
  rw [e]
  rfl

theorem p1_K2_differentiable (m : ℕ) : Differentiable ℝ (fun θ : Fin 4 → ℝ => p1K2 θ m) := by
  unfold p1K2
  fun_prop

theorem p1_tapW_differentiable (a κ : ℝ) (j : ℕ) :
    Differentiable ℝ (fun θ : Fin 4 → ℝ => p1TapW a κ θ j) := by
  refine Nat.strong_induction_on j ?_
  intro j ih
  rcases j with _ | j
  · have e : (fun θ : Fin 4 → ℝ => p1TapW a κ θ 0) = fun _ => κ := by
      funext θ; exact p1_tap_zero a κ _
    rw [e]
    exact differentiable_const κ
  · have e : (fun θ : Fin 4 → ℝ => p1TapW a κ θ (j + 1)) =
        fun θ => a * p1TapW a κ θ j + κ * ∑ m ∈ range (j + 1), p1K2 θ m * p1TapW a κ θ (j - m) := by
      funext θ; exact p1_tap_succ a κ _ j
    rw [e]
    refine ((ih j (Nat.lt_succ_self j)).const_mul a).add (Differentiable.const_mul ?_ κ)
    exact Differentiable.fun_sum fun m _ => (p1_K2_differentiable m).mul (ih (j - m) (by omega))

/-- **The observation Jacobian**: `J_{t i} = ∂h_t/∂θ_i` at `θ₀`, for `t = 0, …, T`. -/
noncomputable def p1TapJac (a κ : ℝ) (T : ℕ) (θ0 : Fin 4 → ℝ) : Matrix (Fin (T + 1)) (Fin 4) ℝ :=
  fun t i => fderiv ℝ (fun θ => p1TapW a κ θ t.val) θ0 (Pi.single i 1)

theorem p1_tapJac_line_deriv (a κ : ℝ) (T : ℕ) (θ0 x : Fin 4 → ℝ) (t : Fin (T + 1)) :
    HasDerivAt (fun s : ℝ => p1TapW a κ (θ0 + s • x) t.val) ((p1TapJac a κ T θ0 *ᵥ x) t) 0 := by
  have hL := ((p1_tapW_differentiable a κ t.val) θ0).hasFDerivAt
  have hγ : HasDerivAt (fun s : ℝ => θ0 + s • x) ((1 : ℝ) • x) 0 :=
    ((hasDerivAt_id' (0 : ℝ)).smul_const x).const_add θ0
  have hc := hL.comp_hasDerivAt_of_eq (x := (0 : ℝ)) hγ (by simp)
  refine hc.congr_deriv ?_
  rw [one_smul]
  conv_lhs => rw [pi_eq_sum_univ' x]
  rw [map_sum]
  simp only [map_smul, smul_eq_mul, Matrix.mulVec, dotProduct, p1TapJac]
  exact Finset.sum_congr rfl fun j _ => mul_comm _ _

/-- Directional derivative of the kernel. -/
noncomputable def p1K2D (θ0 x : Fin 4 → ℝ) (m : ℕ) : ℝ :=
  x 0 * θ0 2 ^ m + θ0 0 * ((m : ℝ) * θ0 2 ^ (m - 1) * x 2) +
    (x 1 * θ0 3 ^ m + θ0 1 * ((m : ℝ) * θ0 3 ^ (m - 1) * x 3))

theorem p1_K2_line_deriv (θ0 x : Fin 4 → ℝ) (m : ℕ) :
    HasDerivAt (fun s : ℝ => p1K2 (θ0 + s • x) m) (p1K2D θ0 x m) 0 := by
  have e : (fun s : ℝ => p1K2 (θ0 + s • x) m) =
      fun s => (θ0 0 + s * x 0) * (θ0 2 + s * x 2) ^ m + (θ0 1 + s * x 1) * (θ0 3 + s * x 3) ^ m := by
    funext s; simp [p1K2]
  rw [e]
  have l : ∀ i, HasDerivAt (fun s : ℝ => θ0 i + s * x i) (1 * x i) 0 := fun i =>
    HasDerivAt.const_add (θ0 i) (HasDerivAt.mul_const (hasDerivAt_id' (0 : ℝ)) (x i))
  have h := HasDerivAt.fun_add (HasDerivAt.fun_mul (l 0) (HasDerivAt.fun_pow (l 2) m))
    (HasDerivAt.fun_mul (l 1) (HasDerivAt.fun_pow (l 3) m))
  refine h.congr_deriv ?_
  simp only [zero_mul, add_zero, p1K2D]
  ring

/-- Derivative of the taps along a curve of kernels. -/
noncomputable def p1TapD (a κ : ℝ) (k k' : ℕ → ℝ) : ℕ → ℝ
  | 0 => 0
  | j + 1 => a * p1TapD a κ k k' j +
      κ * ∑ m ∈ range (j + 1), (k' m * p1Tap a κ k (j - m) + k m * p1TapD a κ k k' (j - m))
termination_by j => j
decreasing_by all_goals first | omega | (simp_wf; omega)

theorem p1_tapD_zero (a κ : ℝ) (k k' : ℕ → ℝ) : p1TapD a κ k k' 0 = 0 := by
  first
  | rw [p1TapD]
  | simp only [p1TapD]
  | exact p1TapD.eq_1 ..

theorem p1_tapD_succ (a κ : ℝ) (k k' : ℕ → ℝ) (j : ℕ) :
    p1TapD a κ k k' (j + 1) = a * p1TapD a κ k k' j +
      κ * ∑ m ∈ range (j + 1), (k' m * p1Tap a κ k (j - m) + k m * p1TapD a κ k k' (j - m)) := by
  first
  | rw [p1TapD]
  | exact p1TapD.eq_2 ..
  | simp only [p1TapD]

/-- **Differentiating the recursion.** -/
theorem p1_tap_hasDerivAt (a κ : ℝ) (k : ℝ → ℕ → ℝ) (k' : ℕ → ℝ)
    (hk : ∀ m, HasDerivAt (fun s => k s m) (k' m) 0) (j : ℕ) :
    HasDerivAt (fun s => p1Tap a κ (k s) j) (p1TapD a κ (k 0) k' j) 0 := by
  refine Nat.strong_induction_on j ?_
  intro j ih
  rcases j with _ | j
  · have e : (fun s => p1Tap a κ (k s) 0) = fun _ => κ := by
      funext s; exact p1_tap_zero a κ _
    rw [e, p1_tapD_zero]
    exact hasDerivAt_const 0 κ
  · have e : (fun s => p1Tap a κ (k s) (j + 1)) =
        fun s => a * p1Tap a κ (k s) j + κ * ∑ m ∈ range (j + 1), k s m * p1Tap a κ (k s) (j - m) := by
      funext s; exact p1_tap_succ a κ _ j
    rw [e, p1_tapD_succ]
    refine HasDerivAt.fun_add (HasDerivAt.const_mul a (ih j (Nat.lt_succ_self j))) (HasDerivAt.const_mul κ ?_)
    exact HasDerivAt.fun_sum fun m _ => HasDerivAt.fun_mul (hk m) (ih (j - m) (by omega))

/-- **The Jacobian applied to a direction is the derivative of the recursion.** -/
theorem p1_tapJac_mulVec (a κ : ℝ) (T : ℕ) (θ0 x : Fin 4 → ℝ) (t : Fin (T + 1)) :
    (p1TapJac a κ T θ0 *ᵥ x) t = p1TapD a κ (p1K2 θ0) (p1K2D θ0 x) t.val := by
  have h1 := p1_tapJac_line_deriv a κ T θ0 x t
  have h2 := p1_tap_hasDerivAt a κ (fun s => p1K2 (θ0 + s • x)) (p1K2D θ0 x)
    (fun m => p1_K2_line_deriv θ0 x m) t.val
  have e : θ0 + (0 : ℝ) • x = θ0 := by simp
  simp only [e] at h2
  exact h1.unique h2

/-! ### Fixed-horizon majorants -/

/-- Majorant for the taps. -/
noncomputable def p1TapM (A κm K0 : ℝ) : ℕ → ℝ
  | 0 => κm
  | j + 1 => (1 + A + κm * K0 * (j + 1)) * p1TapM A κm K0 j

/-- Majorant for the derivative of the taps, per unit of kernel derivative. -/
noncomputable def p1TapG (A κm K0 : ℝ) : ℕ → ℝ
  | 0 => 0
  | j + 1 => (1 + A + κm * K0 * (j + 1)) * p1TapG A κm K0 j + κm * (j + 1) * p1TapM A κm K0 j

theorem p1_tapM_nonneg (A κm K0 : ℝ) (hA : 0 ≤ A) (hκ : 0 ≤ κm) (hK : 0 ≤ K0) :
    ∀ j, 0 ≤ p1TapM A κm K0 j
  | 0 => hκ
  | j + 1 => by
    have ih := p1_tapM_nonneg A κm K0 hA hκ hK j
    have hj : (0 : ℝ) ≤ (j : ℝ) + 1 := by positivity
    have hq : 0 ≤ κm * K0 * ((j : ℝ) + 1) := mul_nonneg (mul_nonneg hκ hK) hj
    show 0 ≤ (1 + A + κm * K0 * ((j : ℝ) + 1)) * p1TapM A κm K0 j
    exact mul_nonneg (by linarith) ih

theorem p1_tapG_nonneg (A κm K0 : ℝ) (hA : 0 ≤ A) (hκ : 0 ≤ κm) (hK : 0 ≤ K0) :
    ∀ j, 0 ≤ p1TapG A κm K0 j
  | 0 => le_refl 0
  | j + 1 => by
    have ih := p1_tapG_nonneg A κm K0 hA hκ hK j
    have hM := p1_tapM_nonneg A κm K0 hA hκ hK j
    have hj : (0 : ℝ) ≤ (j : ℝ) + 1 := by positivity
    have hq : 0 ≤ κm * K0 * ((j : ℝ) + 1) := mul_nonneg (mul_nonneg hκ hK) hj
    show 0 ≤ (1 + A + κm * K0 * ((j : ℝ) + 1)) * p1TapG A κm K0 j + κm * ((j : ℝ) + 1) * p1TapM A κm K0 j
    exact add_nonneg (mul_nonneg (by linarith) ih) (mul_nonneg (mul_nonneg hκ hj) hM)

/-- **Tap bound on a fixed horizon.** -/
theorem p1_tap_abs_le (a κ : ℝ) (k : ℕ → ℝ) (κm K0 : ℝ) (hκ : |κ| ≤ κm) (hK0 : 0 ≤ K0)
    (hk : ∀ m, |k m| ≤ K0) : ∀ j, ∀ s, s ≤ j → |p1Tap a κ k s| ≤ p1TapM |a| κm K0 j := by
  have hκm : 0 ≤ κm := le_trans (abs_nonneg κ) hκ
  intro j
  induction j with
  | zero =>
    intro s hs
    have h0 : s = 0 := by omega
    subst h0
    rw [p1_tap_zero]
    exact hκ
  | succ j ih =>
    intro s hs
    have hM := p1_tapM_nonneg |a| κm K0 (abs_nonneg a) hκm hK0 j
    have hstep : p1TapM |a| κm K0 (j + 1) = (1 + |a| + κm * K0 * ((j : ℝ) + 1)) * p1TapM |a| κm K0 j := rfl
    have hj1 : (0 : ℝ) ≤ (j : ℝ) + 1 := by positivity
    have hq : 0 ≤ κm * K0 * ((j : ℝ) + 1) := mul_nonneg (mul_nonneg hκm hK0) hj1
    rcases Nat.lt_or_ge s (j + 1) with hlt | hge
    · calc |p1Tap a κ k s| ≤ p1TapM |a| κm K0 j := ih s (by omega)
        _ ≤ p1TapM |a| κm K0 (j + 1) := by
          rw [hstep]; nlinarith [mul_nonneg (abs_nonneg a) hM, mul_nonneg hq hM]
    · have hsj : s = j + 1 := by omega
      subst hsj
      rw [p1_tap_succ, hstep]
      have hsum : |∑ m ∈ range (j + 1), k m * p1Tap a κ k (j - m)| ≤
          ((j : ℝ) + 1) * (K0 * p1TapM |a| κm K0 j) := by
        calc _ ≤ ∑ m ∈ range (j + 1), |k m * p1Tap a κ k (j - m)| := abs_sum_le_sum_abs _ _
          _ ≤ ∑ m ∈ range (j + 1), K0 * p1TapM |a| κm K0 j := by
              refine sum_le_sum fun m _ => ?_
              rw [abs_mul]
              exact mul_le_mul (hk m) (ih (j - m) (by omega)) (abs_nonneg _) hK0
          _ = ((j : ℝ) + 1) * (K0 * p1TapM |a| κm K0 j) := by
              rw [sum_const, card_range, nsmul_eq_mul]; first | (push_cast; ring) | push_cast | norm_num
      have hh := ih j le_rfl
      have hs0 : 0 ≤ ((j : ℝ) + 1) * (K0 * p1TapM |a| κm K0 j) := mul_nonneg hj1 (mul_nonneg hK0 hM)
      calc |a * p1Tap a κ k j + κ * ∑ m ∈ range (j + 1), k m * p1Tap a κ k (j - m)|
          ≤ |a| * |p1Tap a κ k j| + |κ| * |∑ m ∈ range (j + 1), k m * p1Tap a κ k (j - m)| := by
            rw [← abs_mul, ← abs_mul]; exact abs_add_le _ _
        _ ≤ |a| * p1TapM |a| κm K0 j + κm * (((j : ℝ) + 1) * (K0 * p1TapM |a| κm K0 j)) :=
            add_le_add (mul_le_mul_of_nonneg_left hh (abs_nonneg a)) (mul_le_mul hκ hsum (abs_nonneg _) hκm)
        _ ≤ (1 + |a| + κm * K0 * ((j : ℝ) + 1)) * p1TapM |a| κm K0 j := by nlinarith [hM]

/-- **Bound on the derivative of the taps on a fixed horizon.** -/
theorem p1_tapD_abs_le (a κ : ℝ) (k k' : ℕ → ℝ) (κm K0 E : ℝ) (N : ℕ) (hκ : |κ| ≤ κm) (hK0 : 0 ≤ K0)
    (hE : 0 ≤ E) (hk : ∀ m, |k m| ≤ K0) (hk' : ∀ m, m < N → |k' m| ≤ E) :
    ∀ j, j ≤ N → ∀ s, s ≤ j → |p1TapD a κ k k' s| ≤ E * p1TapG |a| κm K0 j := by
  have hκm : 0 ≤ κm := le_trans (abs_nonneg κ) hκ
  have htap := p1_tap_abs_le a κ k κm K0 hκ hK0 hk
  intro j
  induction j with
  | zero =>
    intro _ s hs
    have h0 : s = 0 := by omega
    subst h0
    rw [p1_tapD_zero]
    simp [p1TapG]
  | succ j ih =>
    intro hjN s hs
    have ih' := ih (by omega)
    have hM := p1_tapM_nonneg |a| κm K0 (abs_nonneg a) hκm hK0 j
    have hG := p1_tapG_nonneg |a| κm K0 (abs_nonneg a) hκm hK0 j
    have hstep : p1TapG |a| κm K0 (j + 1) = (1 + |a| + κm * K0 * ((j : ℝ) + 1)) * p1TapG |a| κm K0 j +
        κm * ((j : ℝ) + 1) * p1TapM |a| κm K0 j := rfl
    have hj1 : (0 : ℝ) ≤ (j : ℝ) + 1 := by positivity
    have hq : 0 ≤ κm * K0 * ((j : ℝ) + 1) := mul_nonneg (mul_nonneg hκm hK0) hj1
    have hEG : 0 ≤ E * p1TapG |a| κm K0 j := mul_nonneg hE hG
    have hEM : 0 ≤ E * p1TapM |a| κm K0 j := mul_nonneg hE hM
    rcases Nat.lt_or_ge s (j + 1) with hlt | hge
    · calc |p1TapD a κ k k' s| ≤ E * p1TapG |a| κm K0 j := ih' s (by omega)
        _ ≤ E * p1TapG |a| κm K0 (j + 1) := by
          rw [hstep]
          apply mul_le_mul_of_nonneg_left _ hE
          nlinarith [mul_nonneg (abs_nonneg a) hG, mul_nonneg hq hG, mul_nonneg (mul_nonneg hκm hj1) hM]
    · have hsj : s = j + 1 := by omega
      subst hsj
      rw [p1_tapD_succ, hstep]
      have hterm : ∀ m ∈ range (j + 1), |k' m * p1Tap a κ k (j - m) + k m * p1TapD a κ k k' (j - m)| ≤
          E * p1TapM |a| κm K0 j + K0 * (E * p1TapG |a| κm K0 j) := by
        intro m hm
        have hmj : m ≤ j := Nat.lt_succ_iff.mp (mem_range.mp hm)
        calc _ ≤ |k' m * p1Tap a κ k (j - m)| + |k m * p1TapD a κ k k' (j - m)| := abs_add_le _ _
          _ = |k' m| * |p1Tap a κ k (j - m)| + |k m| * |p1TapD a κ k k' (j - m)| := by
              rw [abs_mul, abs_mul]
          _ ≤ E * p1TapM |a| κm K0 j + K0 * (E * p1TapG |a| κm K0 j) :=
              add_le_add (mul_le_mul (hk' m (by omega)) (htap j (j - m) (by omega)) (abs_nonneg _) hE)
                (mul_le_mul (hk m) (ih' (j - m) (by omega)) (abs_nonneg _) hK0)
      have hsum : |∑ m ∈ range (j + 1), (k' m * p1Tap a κ k (j - m) + k m * p1TapD a κ k k' (j - m))| ≤
          ((j : ℝ) + 1) * (E * p1TapM |a| κm K0 j + K0 * (E * p1TapG |a| κm K0 j)) := by
        calc _ ≤ ∑ m ∈ range (j + 1), |k' m * p1Tap a κ k (j - m) + k m * p1TapD a κ k k' (j - m)| :=
              abs_sum_le_sum_abs _ _
          _ ≤ ∑ m ∈ range (j + 1), (E * p1TapM |a| κm K0 j + K0 * (E * p1TapG |a| κm K0 j)) :=
              sum_le_sum hterm
          _ = ((j : ℝ) + 1) * (E * p1TapM |a| κm K0 j + K0 * (E * p1TapG |a| κm K0 j)) := by
              rw [sum_const, card_range, nsmul_eq_mul]; first | (push_cast; ring) | push_cast | norm_num
      have hh := ih' j le_rfl
      have hs0 : 0 ≤ ((j : ℝ) + 1) * (E * p1TapM |a| κm K0 j + K0 * (E * p1TapG |a| κm K0 j)) :=
        mul_nonneg hj1 (add_nonneg hEM (mul_nonneg hK0 hEG))
      calc |a * p1TapD a κ k k' j +
            κ * ∑ m ∈ range (j + 1), (k' m * p1Tap a κ k (j - m) + k m * p1TapD a κ k k' (j - m))|
          ≤ |a| * |p1TapD a κ k k' j| +
            |κ| * |∑ m ∈ range (j + 1), (k' m * p1Tap a κ k (j - m) + k m * p1TapD a κ k k' (j - m))| := by
            rw [← abs_mul, ← abs_mul]; exact abs_add_le _ _
        _ ≤ |a| * (E * p1TapG |a| κm K0 j) +
            κm * (((j : ℝ) + 1) * (E * p1TapM |a| κm K0 j + K0 * (E * p1TapG |a| κm K0 j))) :=
            add_le_add (mul_le_mul_of_nonneg_left hh (abs_nonneg a)) (mul_le_mul hκ hsum (abs_nonneg _) hκm)
        _ ≤ E * ((1 + |a| + κm * K0 * ((j : ℝ) + 1)) * p1TapG |a| κm K0 j +
            κm * ((j : ℝ) + 1) * p1TapM |a| κm K0 j) := by nlinarith [hEG]

end CurrentMM
