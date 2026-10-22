import Mathlib.Analysis.Real.Sqrt
import Mathlib.Algebra.Order.BigOperators.Group.Finset
import Mathlib.Algebra.Order.Floor.Semiring
import Mathlib.Tactic

namespace CurrentMM

open scoped BigOperators

/-- A convex memory update preserves an absolute-value box. -/
theorem thesis_memory_box (r y x M : ℝ) (hr0 : 0 ≤ r) (hr1 : r ≤ 1)
    (hy : |y| ≤ M) (hx : |x| ≤ M) : |r*y + (1-r)*x| ≤ M := by
  calc
    |r*y + (1-r)*x| ≤ |r*y| + |(1-r)*x| := abs_add_le _ _
    _ = r*|y| + (1-r)*|x| := by
      rw [abs_mul, abs_mul, abs_of_nonneg hr0, abs_of_nonneg (by linarith : 0 ≤ 1-r)]
    _ ≤ r*M + (1-r)*M := add_le_add (mul_le_mul_of_nonneg_left hy hr0)
      (mul_le_mul_of_nonneg_left hx (by linarith))
    _ = M := by ring

/-- Sector bounds for finitely many possibly signed and nonlinear cohorts. -/
theorem thesis_sector_flow_bound {n : ℕ} (q Q s y v : Fin n → ℝ) (M : ℝ)
    (hQ : ∀ i, 0 ≤ Q i) (hs : ∀ i, 0 ≤ s i)
    (hq : ∀ i, |q i| ≤ Q i) (hy : ∀ i, |y i| ≤ M)
    (hv : ∀ i, |v i| ≤ s i * |y i|) :
    |∑ i, q i * v i| ≤ (∑ i, Q i * s i) * M := by
  calc
    |∑ i, q i * v i| ≤ ∑ i, |q i * v i| := Finset.abs_sum_le_sum_abs _ _
    _ ≤ ∑ i, Q i * (s i * M) := by
      apply Finset.sum_le_sum
      intro i _
      rw [abs_mul]
      exact mul_le_mul (hq i)
        (le_trans (hv i) (mul_le_mul_of_nonneg_left (hy i) (hs i)))
        (abs_nonneg _) (hQ i)
    _ = (∑ i, Q i * s i) * M := by simp_rw [← mul_assoc]; rw [Finset.sum_mul]

/-- Finite-horizon robust safety for signed, time-varying sector-bounded agents.
The memory index is shifted: y(t+1) incorporates x(t+1). -/
theorem thesis_sector_finite_box {n : ℕ} (H : ℕ) (a κ w M : ℝ)
    (Q s : Fin n → ℝ) (x : ℕ → ℝ) (y q v r : ℕ → Fin n → ℝ)
    (hκ : 0 ≤ κ) (hQ : ∀ i, 0 ≤ Q i) (hs : ∀ i, 0 ≤ s i)
    (hx0 : x 0 = 0) (hy0 : ∀ i, y 0 i = 0) (hM : 0 ≤ M)
    (hq : ∀ t, t < H → ∀ i, |q t i| ≤ Q i)
    (hv : ∀ t, t < H → ∀ i, |v t i| ≤ s i * |y t i|)
    (hr : ∀ t, t < H → ∀ i, 0 ≤ r t i ∧ r t i ≤ 1)
    (hstep : ∀ t, t < H → |x (t+1)| ≤ |a| * |x t| + κ * (|∑ i, q t i * v t i| + w))
    (hmem : ∀ t, t < H → ∀ i, y (t+1) i = r t i * y t i + (1-r t i) * x (t+1))
    (hclose : |a| * M + κ * ((∑ i, Q i * s i)*M + w) ≤ M) :
    ∀ t, t ≤ H → |x t| ≤ M ∧ ∀ i, |y t i| ≤ M := by
  intro t
  induction t with
  | zero =>
      intro _
      constructor
      · simpa [hx0] using hM
      · intro i; simpa [hy0 i] using hM
  | succ t ih =>
      intro ht
      have htH : t < H := by omega
      obtain ⟨hxt, hyt⟩ := ih (by omega)
      have hflow := thesis_sector_flow_bound (q t) Q s (y t) (v t) M hQ hs
        (hq t htH) hyt (hv t htH)
      have hnext : |x (t+1)| ≤ M := by
        calc
          |x (t+1)| ≤ |a| * |x t| + κ * (|∑ i, q t i * v t i| + w) := hstep t htH
          _ ≤ |a| * M + κ*((∑ i, Q i*s i)*M + w) :=
            add_le_add (mul_le_mul_of_nonneg_left hxt (abs_nonneg a))
              (mul_le_mul_of_nonneg_left (add_le_add hflow (le_refl w)) hκ)
          _ ≤ M := hclose
      refine ⟨hnext, ?_⟩
      intro i
      rw [hmem t htH i]
      exact thesis_memory_box _ _ _ M (hr t htH i).1 (hr t htH i).2 (hyt i) hnext

/-- The closed-form scalar bound supplies the invariant-box inequality. -/
theorem thesis_sector_radius (a κ Φ w : ℝ) (hgap : 0 < 1-|a|-κ*Φ) :
    |a| * (κ*w/(1-|a|-κ*Φ)) + κ*(Φ*(κ*w/(1-|a|-κ*Φ))+w)
      = κ*w/(1-|a|-κ*Φ) := by
  field_simp
  <;> ring

/-- Closed-form robust safety from the plant recurrence and bounded shocks. -/
theorem thesis_sector_safety {n : ℕ} (H : ℕ) (a κ w : ℝ)
    (Q s : Fin n → ℝ) (x noise : ℕ → ℝ) (y q v r : ℕ → Fin n → ℝ)
    (hκ : 0 ≤ κ) (hw : 0 ≤ w) (hQ : ∀ i, 0 ≤ Q i) (hs : ∀ i, 0 ≤ s i)
    (hx0 : x 0 = 0) (hy0 : ∀ i, y 0 i = 0)
    (hq : ∀ t, t < H → ∀ i, |q t i| ≤ Q i)
    (hv : ∀ t, t < H → ∀ i, |v t i| ≤ s i * |y t i|)
    (hr : ∀ t, t < H → ∀ i, 0 ≤ r t i ∧ r t i ≤ 1)
    (hnoise : ∀ t, t < H → |noise t| ≤ w)
    (hplant : ∀ t, t < H → x (t+1) = a*x t + κ*((∑ i, q t i*v t i) + noise t))
    (hmem : ∀ t, t < H → ∀ i, y (t+1) i = r t i*y t i + (1-r t i)*x (t+1))
    (hgap : 0 < 1-|a|-κ*(∑ i, Q i*s i)) :
    ∀ t, t ≤ H → |x t| ≤ κ*w/(1-|a|-κ*(∑ i, Q i*s i)) := by
  have hstep : ∀ t, t < H → |x (t+1)| ≤
      |a| * |x t| + κ*(|∑ i, q t i*v t i| + w) := by
    intro t ht
    rw [hplant t ht]
    calc
      |a*x t + κ*((∑ i, q t i*v t i) + noise t)| ≤
          |a*x t| + |κ*((∑ i, q t i*v t i) + noise t)| := abs_add_le _ _
      _ = |a| * |x t| + κ * |(∑ i, q t i*v t i) + noise t| := by
        rw [abs_mul, abs_mul, abs_of_nonneg hκ]
      _ ≤ |a| * |x t| + κ*(|∑ i, q t i*v t i| + w) := by
        have hsum : |(∑ i, q t i*v t i) + noise t| ≤ |∑ i, q t i*v t i| + w :=
          le_trans (abs_add_le _ _) (add_le_add (le_refl _) (hnoise t ht))
        exact add_le_add (le_refl _) (mul_le_mul_of_nonneg_left hsum hκ)
  have hM : 0 ≤ κ*w/(1-|a|-κ*(∑ i, Q i*s i)) :=
    div_nonneg (mul_nonneg hκ hw) (le_of_lt hgap)
  have hclose := le_of_eq (thesis_sector_radius a κ (∑ i, Q i*s i) w hgap)
  intro t ht
  exact (thesis_sector_finite_box H a κ w _ Q s x y q v r hκ hQ hs hx0 hy0 hM
    hq hv hr hstep hmem hclose t ht).1

/-- Bounded one-period changes imply a cumulative absolute-weight envelope. -/
theorem thesis_weight_drift (q : ℕ → ℝ) (q0 γ : ℝ)
    (h0 : |q 0| ≤ q0) (hd : ∀ t, |q (t+1)-q t| ≤ γ) :
    ∀ t, |q t| ≤ q0 + (t : ℝ)*γ := by
  intro t
  induction t with
  | zero => simpa using h0
  | succ t ih =>
      have htri : |q (t+1)| ≤ |q t| + |q (t+1)-q t| := by
        convert abs_add_le (q t) (q (t+1)-q t) using 1 <;> congr 1 <;> ring
      push_cast
      nlinarith [hd t]

/-- The lifetime inequality bounds the total sensitivity on its horizon.
The integer floor is represented by its defining lower inequality. -/
theorem thesis_lifetime_sensitivity {n : ℕ} (q0 γ s : Fin n → ℝ) (Φ : ℝ)
    (H : ℕ) (hs : ∀ i, 0 ≤ s i)
    (hγ : 0 ≤ ∑ i, γ i*s i)
    (hH : (H : ℝ)*(∑ i, γ i*s i) ≤ Φ-∑ i, q0 i*s i)
    (t : ℕ) (ht : t ≤ H) :
    ∑ i, (q0 i + (t : ℝ)*γ i)*s i ≤ Φ := by
  have htime : (t : ℝ) ≤ (H : ℝ) := by exact_mod_cast ht
  have hmul := mul_le_mul_of_nonneg_right htime hγ
  have hid : (∑ i, (q0 i + (t : ℝ)*γ i)*s i) =
      (∑ i, q0 i*s i) + (t : ℝ)*(∑ i, γ i*s i) := by
    simp_rw [add_mul, mul_assoc]
    rw [Finset.sum_add_distrib, Finset.mul_sum]
  rw [hid]
  linarith

/-- The natural-number floor gives the stated certificate horizon. -/
theorem thesis_lifetime_floor (margin D : ℝ) (hm : 0 ≤ margin) (hD : 0 < D) :
    (⌊margin/D⌋₊ : ℝ)*D ≤ margin := by
  have hf : (⌊margin/D⌋₊ : ℝ) ≤ margin/D := Nat.floor_le (div_nonneg hm (le_of_lt hD))
  exact (le_div_iff₀ hD).1 hf

/-- The complete weight envelope on the computed lifetime, including sensitivity. -/
theorem thesis_lifetime_envelope {n : ℕ} (q : ℕ → Fin n → ℝ)
    (q0 γ s : Fin n → ℝ) (Φ : ℝ)
    (h0 : ∀ i, |q 0 i| ≤ q0 i) (hd : ∀ t i, |q (t+1) i-q t i| ≤ γ i)
    (hγ : ∀ i, 0 ≤ γ i) (hs : ∀ i, 0 ≤ s i)
    (hm : ∑ i, q0 i*s i ≤ Φ) (hD : 0 < ∑ i, γ i*s i) :
    let H := ⌊(Φ-∑ i, q0 i*s i)/(∑ i, γ i*s i)⌋₊
    (∀ t, t ≤ H → ∀ i, |q t i| ≤ q0 i+(H : ℝ)*γ i) ∧
    (∑ i, (q0 i+(H : ℝ)*γ i)*s i) ≤ Φ := by
  dsimp only
  let H := ⌊(Φ-∑ i, q0 i*s i)/(∑ i, γ i*s i)⌋₊
  have hf : (H : ℝ)*(∑ i, γ i*s i) ≤ Φ-∑ i, q0 i*s i :=
    thesis_lifetime_floor _ _ (by linarith) hD
  constructor
  · intro t ht i
    have hqt := thesis_weight_drift (fun t => q t i) (q0 i) (γ i) (h0 i) (fun t => hd t i) t
    have htime : (t : ℝ) ≤ (H : ℝ) := by exact_mod_cast ht
    exact le_trans hqt (add_le_add (le_refl _) (mul_le_mul_of_nonneg_right htime (hγ i)))
  · exact thesis_lifetime_sensitivity q0 γ s Φ H hs (le_of_lt hD) hf H (le_refl _)

/-- The tail estimate on the integrand bounds its finite positive-measure sum. -/
theorem thesis_bias_from_tail {n : ℕ} (weight tail : Fin n → ℝ) (B u : ℝ)
    (hw : ∀ i, 0 ≤ weight i) (hu : 0 ≤ u)
    (hB : ∑ i, weight i ≤ B) (ht : ∀ i, |tail i| ≤ u) :
    |∑ i, weight i*tail i| ≤ B*u := by
  calc
    |∑ i, weight i*tail i| ≤ ∑ i, |weight i*tail i| := Finset.abs_sum_le_sum_abs _ _
    _ = ∑ i, weight i * |tail i| := by simp_rw [abs_mul, abs_of_nonneg (hw _)]
    _ ≤ ∑ i, weight i*u := Finset.sum_le_sum (fun i _ => mul_le_mul_of_nonneg_left (ht i) (hw i))
    _ = (∑ i, weight i)*u := (Finset.sum_mul _ _ _).symm
    _ ≤ B*u := mul_le_mul_of_nonneg_right hB hu

/-- Deterministic bias plus noise radius gives the target half-width. -/
theorem thesis_interval_half_width (bias radius ε : ℝ)
    (hb : bias ≤ ε/2) (hr : radius ≤ ε/2) : bias + radius ≤ ε := by linarith

/-- Variance-budget arithmetic; distributional coverage is external. -/
theorem thesis_variance_radius (z σ A N ε : ℝ)
    (hz : 0 ≤ z) (hσ : 0 ≤ σ) (hA : 0 ≤ A) (hN : 0 < N) (hε : 0 ≤ ε)
    (hbudget : 4*z^2*σ^2*A ≤ N*ε^2) : z*σ*Real.sqrt (A/N) ≤ ε/2 := by
  have hdiv : 0 ≤ A/N := div_nonneg hA (le_of_lt hN)
  have hsqr := Real.sq_sqrt hdiv
  have heq : (z*σ*Real.sqrt (A/N))^2 = z^2*σ^2*A/N := by rw [mul_pow, mul_pow, hsqr]; ring
  have hbound : z^2*σ^2*A/N ≤ ε^2/4 := by
    apply (div_le_iff₀ hN).2
    nlinarith
  have hpos : 0 ≤ z*σ*Real.sqrt (A/N) := by positivity
  nlinarith

end CurrentMM
