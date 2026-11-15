import Mathlib.Algebra.Order.BigOperators.Group.Finset
import Mathlib.Algebra.Order.BigOperators.Ring.Finset
import Mathlib.Basic.Real.Basic
import Mathlib.Tactic.Linarith
import Mathlib.Tactic.GCongr
import Mathlib.Tactic.Positivity

/-!
# Several assets with positive cross-impact (thesis, Proposition `prop:multiasset_positive`)

The state is a vector `x t : Fin d → ℝ`, cohorts are indexed by `Fin n`, and every
cohort has a componentwise memory state `y t i : Fin d → ℝ`.  Matrices are functions
`Fin d → Fin d → ℝ`.  The response of cohort `i` at time `t` is an arbitrary vector
`v t i` subject only to the componentwise sector bound `|v t i l| ≤ S i l * |y t i l|`,
so nonlinear and time-varying rules are covered.  Weights `Q t i` are time varying with
entrywise bounds `|Q t i j k| ≤ Qbar i j k`.

The comparison theorem shows that any non-negative supersolution `z` of
`A z + K (∑ᵢ Qbarᵢ Sᵢ z + wbar 𝟙) ≤ z` bounds every state and memory coordinate at every
time.  The resolvent vector `wbar (I - G)⁻¹ K 𝟙` of the thesis is such a supersolution;
the Neumann series that produces it and the limit that gives sharpness are written proofs.
The monotone-from-rest lemma below is the finite-time part of the sharpness argument.
-/

namespace CurrentMM

open scoped BigOperators

/-- A non-negative matrix applied to a vector bounded componentwise by `z`. -/
theorem thesis_ma_matvec_abs {d : ℕ} (A : Fin d → Fin d → ℝ) (u z : Fin d → ℝ)
    (hA : ∀ j k, 0 ≤ A j k) (hu : ∀ k, |u k| ≤ z k) (j : Fin d) :
    |∑ k, A j k * u k| ≤ ∑ k, A j k * z k := by
  calc
    |∑ k, A j k * u k| ≤ ∑ k, |A j k * u k| := Finset.abs_sum_le_sum_abs _ _
    _ ≤ ∑ k, A j k * z k := by
      apply Finset.sum_le_sum
      intro k _
      rw [abs_mul, abs_of_nonneg (hA j k)]
      exact mul_le_mul_of_nonneg_left (hu k) (hA j k)

/-- Aggregate flow of sector-bounded cohorts with entrywise bounded weights, one asset row. -/
theorem thesis_ma_flow_bound {d n : ℕ} (Q Qbar : Fin n → Fin d → Fin d → ℝ)
    (S : Fin n → Fin d → ℝ) (y v : Fin n → Fin d → ℝ) (z : Fin d → ℝ)
    (hQbar : ∀ i j l, 0 ≤ Qbar i j l) (hS : ∀ i l, 0 ≤ S i l)
    (hQ : ∀ i j l, |Q i j l| ≤ Qbar i j l) (hy : ∀ i l, |y i l| ≤ z l)
    (hv : ∀ i l, |v i l| ≤ S i l * |y i l|) (k : Fin d) :
    |∑ i, ∑ l, Q i k l * v i l| ≤ ∑ i, ∑ l, Qbar i k l * S i l * z l := by
  calc
    |∑ i, ∑ l, Q i k l * v i l| ≤ ∑ i, |∑ l, Q i k l * v i l| := Finset.abs_sum_le_sum_abs _ _
    _ ≤ ∑ i, ∑ l, |Q i k l * v i l| := by
      apply Finset.sum_le_sum
      intro i _
      exact Finset.abs_sum_le_sum_abs _ _
    _ ≤ ∑ i, ∑ l, Qbar i k l * S i l * z l := by
      apply Finset.sum_le_sum
      intro i _
      apply Finset.sum_le_sum
      intro l _
      rw [abs_mul, mul_assoc]
      exact mul_le_mul (hQ i k l)
        (le_trans (hv i l) (mul_le_mul_of_nonneg_left (hy i l) (hS i l)))
        (abs_nonneg _) (hQbar i k l)

/-- A convex memory update preserves a componentwise box. -/
theorem thesis_ma_memory_box (r y x m : ℝ) (hr0 : 0 ≤ r) (hr1 : r ≤ 1)
    (hy : |y| ≤ m) (hx : |x| ≤ m) : |r * y + (1 - r) * x| ≤ m := by
  calc
    |r * y + (1 - r) * x| ≤ |r * y| + |(1 - r) * x| := abs_add_le _ _
    _ = r * |y| + (1 - r) * |x| := by
      rw [abs_mul, abs_mul, abs_of_nonneg hr0, abs_of_nonneg (by linarith : 0 ≤ 1 - r)]
    _ ≤ r * m + (1 - r) * m :=
      add_le_add (mul_le_mul_of_nonneg_left hy hr0) (mul_le_mul_of_nonneg_left hx (by linarith))
    _ = m := by ring

/-- One step of the multi-asset plant keeps the state inside the supersolution box. -/
theorem thesis_ma_step {d n : ℕ} (A K : Fin d → Fin d → ℝ) (Q Qbar : Fin n → Fin d → Fin d → ℝ)
    (S : Fin n → Fin d → ℝ) (x : Fin d → ℝ) (y v : Fin n → Fin d → ℝ) (w z : Fin d → ℝ)
    (wbar : ℝ) (hA : ∀ j k, 0 ≤ A j k) (hK : ∀ j k, 0 ≤ K j k)
    (hQbar : ∀ i j l, 0 ≤ Qbar i j l) (hS : ∀ i l, 0 ≤ S i l)
    (hQ : ∀ i j l, |Q i j l| ≤ Qbar i j l) (hx : ∀ k, |x k| ≤ z k) (hy : ∀ i l, |y i l| ≤ z l)
    (hv : ∀ i l, |v i l| ≤ S i l * |y i l|) (hw : ∀ k, |w k| ≤ wbar)
    (hsuper : ∀ j, ∑ k, A j k * z k + ∑ k, K j k * ((∑ i, ∑ l, Qbar i k l * S i l * z l) + wbar) ≤ z j)
    (j : Fin d) :
    |∑ k, A j k * x k + ∑ k, K j k * ((∑ i, ∑ l, Q i k l * v i l) + w k)| ≤ z j := by
  have hflow : ∀ k, |(∑ i, ∑ l, Q i k l * v i l) + w k| ≤
      (∑ i, ∑ l, Qbar i k l * S i l * z l) + wbar := by
    intro k
    calc
      |(∑ i, ∑ l, Q i k l * v i l) + w k| ≤ |∑ i, ∑ l, Q i k l * v i l| + |w k| := abs_add_le _ _
      _ ≤ (∑ i, ∑ l, Qbar i k l * S i l * z l) + wbar :=
        add_le_add (thesis_ma_flow_bound Q Qbar S y v z hQbar hS hQ hy hv k) (hw k)
  calc
    |∑ k, A j k * x k + ∑ k, K j k * ((∑ i, ∑ l, Q i k l * v i l) + w k)|
        ≤ |∑ k, A j k * x k| + |∑ k, K j k * ((∑ i, ∑ l, Q i k l * v i l) + w k)| := abs_add_le _ _
    _ ≤ ∑ k, A j k * z k + ∑ k, K j k * ((∑ i, ∑ l, Qbar i k l * S i l * z l) + wbar) :=
      add_le_add (thesis_ma_matvec_abs A x z hA hx j) (thesis_ma_matvec_abs K _ _ hK hflow j)
    _ ≤ z j := hsuper j

/-- Positive cross-impact comparison: a non-negative supersolution bounds every state and every
memory coordinate at every time, for nonlinear, time-varying, sector-bounded cohorts. -/
theorem thesis_multiasset_comparison {d n : ℕ} (A K : Fin d → Fin d → ℝ)
    (Qbar : Fin n → Fin d → Fin d → ℝ) (S : Fin n → Fin d → ℝ) (wbar : ℝ) (z : Fin d → ℝ)
    (x : ℕ → Fin d → ℝ) (y v : ℕ → Fin n → Fin d → ℝ) (Q : ℕ → Fin n → Fin d → Fin d → ℝ)
    (R : ℕ → Fin n → Fin d → ℝ) (w : ℕ → Fin d → ℝ)
    (hA : ∀ j k, 0 ≤ A j k) (hK : ∀ j k, 0 ≤ K j k)
    (hQbar : ∀ i j l, 0 ≤ Qbar i j l) (hS : ∀ i l, 0 ≤ S i l)
    (hsuper : ∀ j, ∑ k, A j k * z k + ∑ k, K j k * ((∑ i, ∑ l, Qbar i k l * S i l * z l) + wbar) ≤ z j)
    (hx0 : ∀ j, |x 0 j| ≤ z j) (hy0 : ∀ i j, |y 0 i j| ≤ z j)
    (hQ : ∀ t i j l, |Q t i j l| ≤ Qbar i j l)
    (hv : ∀ t i l, |v t i l| ≤ S i l * |y t i l|)
    (hw : ∀ t k, |w t k| ≤ wbar)
    (hR : ∀ t i j, 0 ≤ R t i j ∧ R t i j ≤ 1)
    (hstep : ∀ t j, x (t + 1) j =
      ∑ k, A j k * x t k + ∑ k, K j k * ((∑ i, ∑ l, Q t i k l * v t i l) + w (t + 1) k))
    (hmem : ∀ t i j, y (t + 1) i j = R t i j * y t i j + (1 - R t i j) * x (t + 1) j) :
    ∀ t, (∀ j, |x t j| ≤ z j) ∧ ∀ i j, |y t i j| ≤ z j := by
  intro t
  induction t with
  | zero => exact ⟨hx0, hy0⟩
  | succ t ih =>
      obtain ⟨hxt, hyt⟩ := ih
      have hnext : ∀ j, |x (t + 1) j| ≤ z j := by
        intro j
        rw [hstep t j]
        exact thesis_ma_step A K (Q t) Qbar S (x t) (y t) (v t) (w (t + 1)) z wbar hA hK hQbar hS
          (hQ t) hxt hyt (hv t) (hw (t + 1)) hsuper j
      refine ⟨hnext, ?_⟩
      intro i j
      rw [hmem t i j]
      exact thesis_ma_memory_box _ _ _ _ (hR t i j).1 (hR t i j).2 (hyt i j) (hnext j)

/-- From rest, the economy at the bound is the start of a componentwise box: every coordinate of
`x t` is bounded by the corresponding coordinate of the supersolution, so the sup norm of the state
is bounded by the largest coordinate of `z`. -/
theorem thesis_multiasset_supnorm {d n : ℕ} (A K : Fin d → Fin d → ℝ)
    (Qbar : Fin n → Fin d → Fin d → ℝ) (S : Fin n → Fin d → ℝ) (wbar m : ℝ) (z : Fin d → ℝ)
    (x : ℕ → Fin d → ℝ) (y v : ℕ → Fin n → Fin d → ℝ) (Q : ℕ → Fin n → Fin d → Fin d → ℝ)
    (R : ℕ → Fin n → Fin d → ℝ) (w : ℕ → Fin d → ℝ)
    (hA : ∀ j k, 0 ≤ A j k) (hK : ∀ j k, 0 ≤ K j k)
    (hQbar : ∀ i j l, 0 ≤ Qbar i j l) (hS : ∀ i l, 0 ≤ S i l)
    (hsuper : ∀ j, ∑ k, A j k * z k + ∑ k, K j k * ((∑ i, ∑ l, Qbar i k l * S i l * z l) + wbar) ≤ z j)
    (hzm : ∀ j, z j ≤ m)
    (hx0 : ∀ j, x 0 j = 0) (hy0 : ∀ i j, y 0 i j = 0) (hz : ∀ j, 0 ≤ z j)
    (hQ : ∀ t i j l, |Q t i j l| ≤ Qbar i j l)
    (hv : ∀ t i l, |v t i l| ≤ S i l * |y t i l|)
    (hw : ∀ t k, |w t k| ≤ wbar)
    (hR : ∀ t i j, 0 ≤ R t i j ∧ R t i j ≤ 1)
    (hstep : ∀ t j, x (t + 1) j =
      ∑ k, A j k * x t k + ∑ k, K j k * ((∑ i, ∑ l, Q t i k l * v t i l) + w (t + 1) k))
    (hmem : ∀ t i j, y (t + 1) i j = R t i j * y t i j + (1 - R t i j) * x (t + 1) j) :
    ∀ t j, |x t j| ≤ m := by
  intro t j
  have h := thesis_multiasset_comparison A K Qbar S wbar z x y v Q R w hA hK hQbar hS hsuper
    (fun j => by rw [hx0 j, abs_zero]; exact hz j)
    (fun i j => by rw [hy0 i j, abs_zero]; exact hz j) hQ hv hw hR hstep hmem t
  exact le_trans (h.1 j) (hzm j)

/-- Finite-time part of sharpness: in the maximal positive linear economy
`x (t+1) = G x t + c` started at rest, with `G ≥ 0` and `c ≥ 0`, the state increases
componentwise and stays below every non-negative supersolution `G z + c ≤ z`. -/
theorem thesis_multiasset_linear_monotone {d : ℕ} (G : Fin d → Fin d → ℝ) (c z : Fin d → ℝ)
    (x : ℕ → Fin d → ℝ) (hG : ∀ j k, 0 ≤ G j k) (hc : ∀ j, 0 ≤ c j)
    (hsuper : ∀ j, ∑ k, G j k * z k + c j ≤ z j) (hz : ∀ j, 0 ≤ z j)
    (hx0 : ∀ j, x 0 j = 0) (hstep : ∀ t j, x (t + 1) j = ∑ k, G j k * x t k + c j) :
    ∀ t, (∀ j, x t j ≤ x (t + 1) j) ∧ (∀ j, 0 ≤ x t j) ∧ ∀ j, x t j ≤ z j := by
  intro t
  induction t with
  | zero =>
      refine ⟨?_, ?_, ?_⟩
      · intro j
        rw [hstep 0 j, hx0 j]
        have : ∀ k, G j k * x 0 k = 0 := fun k => by rw [hx0 k, mul_zero]
        rw [Finset.sum_congr rfl (fun k _ => this k), Finset.sum_const_zero, zero_add]
        exact hc j
      · intro j; rw [hx0 j]
      · intro j; rw [hx0 j]; exact hz j
  | succ t ih =>
      obtain ⟨hmono, hnn, hle⟩ := ih
      have hnn' : ∀ j, 0 ≤ x (t + 1) j := fun j => le_trans (hnn j) (hmono j)
      have hle' : ∀ j, x (t + 1) j ≤ z j := by
        intro j
        rw [hstep t j]
        calc
          ∑ k, G j k * x t k + c j ≤ ∑ k, G j k * z k + c j := by
            gcongr with k _
            exact hG j k
            exact hle k
          _ ≤ z j := hsuper j
      refine ⟨?_, hnn', hle'⟩
      intro j
      rw [hstep (t + 1) j, hstep t j]
      gcongr with k _
      exact hG j k
      exact hmono k

end CurrentMM
