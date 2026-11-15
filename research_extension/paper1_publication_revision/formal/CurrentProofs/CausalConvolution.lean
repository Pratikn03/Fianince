import CurrentProofs.ProbeGeometry
import Mathlib.Algebra.Order.BigOperators.Group.Finset

namespace CurrentMM
noncomputable section
open scoped BigOperators

def causalImpulseColumn {T : ℕ} (impulse : ℕ → ℝ) (s : Fin T) :
    EuclideanSpace ℝ (Fin T) :=
  WithLp.toLp 2 (fun t : Fin T => if s ≤ t then impulse (t.val - s.val) else 0)

def finiteImpulseVector (T : ℕ) (impulse : ℕ → ℝ) : EuclideanSpace ℝ (Fin T) :=
  WithLp.toLp 2 (fun t : Fin T => impulse t.val)

def causalImpulseConvolution {T : ℕ} (impulse : ℕ → ℝ) (v : Fin T → ℝ) :
    EuclideanSpace ℝ (Fin T) := ∑ s, v s • causalImpulseColumn impulse s

theorem causal_column_energy_bound {T : ℕ} (impulse : ℕ → ℝ) (s : Fin T) :
    ‖causalImpulseColumn impulse s‖ ^ 2 ≤ ‖finiteImpulseVector T impulse‖ ^ 2 := by
  rw [EuclideanSpace.real_norm_sq_eq, EuclideanSpace.real_norm_sq_eq]
  change (∑ t : Fin T, (if s ≤ t then impulse (t.val - s.val) else 0) ^ 2) ≤
    ∑ t : Fin T, impulse t.val ^ 2
  let active : Finset (Fin T) := Finset.univ.filter fun t => s ≤ t
  let shift : Fin T → Fin T := fun t =>
    ⟨t.val - s.val, lt_of_le_of_lt (Nat.sub_le t.val s.val) t.is_lt⟩
  have hinj : Set.InjOn shift (active : Set (Fin T)) := by
    intro t ht u hu heq
    have hst : s ≤ t := (Finset.mem_filter.mp ht).2
    have hsu : s ≤ u := (Finset.mem_filter.mp hu).2
    have hval : t.val - s.val = u.val - s.val := congrArg Fin.val heq
    apply Fin.ext
    change s.val ≤ t.val at hst
    change s.val ≤ u.val at hsu
    omega
  have hsum : (∑ t ∈ active, impulse (t.val - s.val) ^ 2) ≤
      ∑ t : Fin T, impulse t.val ^ 2 := by
    exact Finset.sum_le_sum_of_injOn shift hinj (Finset.subset_univ _)
      (fun t ht => le_refl _) (fun t ht hn => sq_nonneg _)
  have hfilter : (∑ t : Fin T, (if s ≤ t then impulse (t.val - s.val) else 0) ^ 2) =
      ∑ t ∈ active, impulse (t.val - s.val) ^ 2 := by
    simp [active, Finset.sum_filter, ite_pow]
  rw [hfilter]
  exact hsum

theorem causal_column_norm_bound {T : ℕ} (impulse : ℕ → ℝ) (s : Fin T) :
    ‖causalImpulseColumn impulse s‖ ≤ ‖finiteImpulseVector T impulse‖ :=
  (sq_le_sq₀ (norm_nonneg _) (norm_nonneg _)).mp (causal_column_energy_bound impulse s)

theorem causal_first_column {T : ℕ} (impulse : ℕ → ℝ) (hT : 0 < T) :
    causalImpulseColumn impulse ⟨0, hT⟩ = finiteImpulseVector T impulse := by
  ext t
  have hzero : (⟨0, hT⟩ : Fin T) ≤ t := by
    change 0 ≤ t.val
    exact Nat.zero_le _
  simp [causalImpulseColumn, finiteImpulseVector, hzero]

theorem actual_convolution_quantity_bound {T : ℕ} (impulse : ℕ → ℝ)
    (v : Fin T → ℝ) (V : ℝ) (hbudget : ∑ t, |v t| ≤ V) :
    ‖causalImpulseConvolution impulse v‖ ≤ V * ‖finiteImpulseVector T impulse‖ :=
  finite_column_quantity_bound _ v _ V (norm_nonneg _) (causal_column_norm_bound impulse) hbudget

theorem first_pulse_convolution_attains {T : ℕ} (impulse : ℕ → ℝ) (hT : 0 < T)
    (V : ℝ) (hV : 0 ≤ V) :
    let v : Fin T → ℝ := fun t => if t.val = 0 then V else 0
    (∑ t, |v t|) = V ∧
      ‖causalImpulseConvolution impulse v‖ = V * ‖finiteImpulseVector T impulse‖ := by
  have h := quantity_pulse_attains_column_bound (causalImpulseColumn impulse) ⟨0, hT⟩ V hV
  rw [causal_first_column impulse hT] at h
  simpa [causalImpulseConvolution, Fin.ext_iff] using h

theorem exact_lifetime_quantity_signal_optimum {T : ℕ} (impulse : ℕ → ℝ)
    (hT : 0 < T) (V : ℝ) (hV : 0 ≤ V) :
    IsGreatest ((fun v : Fin T → ℝ => ‖causalImpulseConvolution impulse v‖) ''
      {v | ∑ t, |v t| ≤ V}) (V * ‖finiteImpulseVector T impulse‖) := by
  have hpulse := first_pulse_convolution_attains impulse hT V hV
  refine ⟨?_, ?_⟩
  · exact ⟨fun t => if t.val = 0 then V else 0, hpulse.1.le, hpulse.2⟩
  · rintro value ⟨v, hv, rfl⟩
    exact actual_convolution_quantity_bound impulse v V hv

end
end CurrentMM
