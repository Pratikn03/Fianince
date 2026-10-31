import CurrentProofs.CohortConvolution
import CurrentProofs.Paper1Identification

/-!
# Paper 1, Theorem `thm:merged` (i) for the model itself

`actualCohortImpulse a κ q η j` is the price component of `J^j b` for the paper's state-space model
(`cohortLinearTransition`, `cohortInputVector`). This file shows that it satisfies the scalar closed-loop recursion
`h₀ = κ`, `h_{j+1} = a h_j + κ ∑_{m ≤ j} k_m h_{j-m}` with kernel `k_m = ∑_i q_i η_i (1 - η_i)^m`, and combines this
with `Paper1Identification.lean`: for known `a` and `κ ≠ 0`, two cohort economies have the same price impulse
response if and only if they have the same merged measure (the same total weight `q_i η_i` at every memory rate
`1 - η_i`). The McMillan-degree count of the theorem is not formalized.
-/

namespace CurrentMM

open Finset

/-- Feedback kernel of a cohort economy, `k_m = ∑_i q_i η_i (1 - η_i)^m`. -/
def cohortKernel {n : ℕ} (q rate : Fin n → ℝ) (m : ℕ) : ℝ :=
  ∑ i, q i * rate i * (1 - rate i) ^ m

/-- Memory state of cohort `i`, `j` periods after a unit probe from the reset state. -/
def cohortImpulseMemory {n : ℕ} (a impact : ℝ) (q rate : Fin n → ℝ) (i : Fin n) (j : ℕ) : ℝ :=
  ((cohortLinearTransition a impact q rate ^ j) (cohortInputVector impact rate)) (some i)

theorem p1_impulse_zero {n : ℕ} (a impact : ℝ) (q rate : Fin n → ℝ) :
    actualCohortImpulse a impact q rate 0 = impact := by
  simp [actualCohortImpulse, cohortInputVector]

theorem p1_impulse_memory_zero {n : ℕ} (a impact : ℝ) (q rate : Fin n → ℝ) (i : Fin n) :
    cohortImpulseMemory a impact q rate i 0 = rate i * impact := by
  simp [cohortImpulseMemory, cohortInputVector]

/-- One step of the price: `h_{j+1} = a h_j + κ ∑_i q_i y_{i,j}`. -/
theorem p1_impulse_price_step {n : ℕ} (a impact : ℝ) (q rate : Fin n → ℝ) (j : ℕ) :
    actualCohortImpulse a impact q rate (j + 1) =
      a * actualCohortImpulse a impact q rate j +
        impact * ∑ i, q i * cohortImpulseMemory a impact q rate i j := by
  simp only [actualCohortImpulse, cohortImpulseMemory, pow_succ', Module.End.mul_apply]
  rfl

/-- One step of a memory state: `y_{i,j+1} = (1 - η_i) y_{i,j} + η_i h_{j+1}`. -/
theorem p1_impulse_memory_step {n : ℕ} (a impact : ℝ) (q rate : Fin n → ℝ) (i : Fin n) (j : ℕ) :
    cohortImpulseMemory a impact q rate i (j + 1) =
      (1 - rate i) * cohortImpulseMemory a impact q rate i j +
        rate i * actualCohortImpulse a impact q rate (j + 1) := by
  rw [p1_impulse_price_step]
  simp only [cohortImpulseMemory, actualCohortImpulse, pow_succ', Module.End.mul_apply]
  rfl

/-- Memory states are exponentially weighted sums of past prices. -/
theorem p1_impulse_memory_closed {n : ℕ} (a impact : ℝ) (q rate : Fin n → ℝ) (i : Fin n) (j : ℕ) :
    cohortImpulseMemory a impact q rate i j =
      ∑ s ∈ range (j + 1), rate i * (1 - rate i) ^ (j - s) * actualCohortImpulse a impact q rate s := by
  induction j with
  | zero => simp [p1_impulse_memory_zero, p1_impulse_zero]
  | succ j ih =>
    rw [p1_impulse_memory_step, ih, sum_range_succ (n := j + 1), mul_sum]
    congr 1
    · refine sum_congr rfl (fun s hs => ?_)
      have hs' : s ≤ j := Nat.lt_succ_iff.mp (mem_range.mp hs)
      have e : j + 1 - s = (j - s) + 1 := by omega
      rw [e, pow_succ]; ring
    · simp

/-- **The model's price response obeys the closed-loop recursion with the cohort kernel.** -/
theorem p1_impulse_closed_loop_recursion {n : ℕ} (a impact : ℝ) (q rate : Fin n → ℝ) (j : ℕ) :
    actualCohortImpulse a impact q rate (j + 1) =
      a * actualCohortImpulse a impact q rate j +
        impact * ∑ m ∈ range (j + 1), cohortKernel q rate m * actualCohortImpulse a impact q rate (j - m) := by
  rw [p1_impulse_price_step]
  congr 2
  simp only [p1_impulse_memory_closed, mul_sum, cohortKernel, sum_mul]
  rw [sum_comm]
  rw [← sum_range_reflect (fun s => ∑ i, q i * (rate i * (1 - rate i) ^ (j - s) *
      actualCohortImpulse a impact q rate s)) (j + 1)]
  refine sum_congr rfl (fun m hm => ?_)
  have hm' : m ≤ j := Nat.lt_succ_iff.mp (mem_range.mp hm)
  have e1 : j + 1 - 1 - m = j - m := by omega
  have e2 : j - (j - m) = m := by omega
  rw [e1, e2]
  refine sum_congr rfl (fun i _ => by ring)

/-- **`thm:merged` (i), model form.** With known `a` and `κ ≠ 0`, two cohort economies with the same price impulse
response have the same merged weight `∑_{i : 1 - η_i = ρ} q_i η_i` at every memory rate `ρ`. -/
theorem p1_thm_merged_model_identification {n n' : ℕ} (a impact : ℝ) (himpact : impact ≠ 0)
    (q rate : Fin n → ℝ) (q' rate' : Fin n' → ℝ)
    (hsame : ∀ j, actualCohortImpulse a impact q rate j = actualCohortImpulse a impact q' rate' j) :
    ∀ ρ, mergedWeight univ (fun i => 1 - rate i) (fun i => q i * rate i) ρ =
      mergedWeight univ (fun i => 1 - rate' i) (fun i => q' i * rate' i) ρ := by
  have hk := p1_thm_merged_deconvolution a impact himpact (cohortKernel q rate) (cohortKernel q' rate')
    (actualCohortImpulse a impact q rate) (p1_impulse_zero a impact q rate)
    (p1_impulse_closed_loop_recursion a impact q rate)
    (fun t => by
      rw [hsame (t + 1), p1_impulse_closed_loop_recursion a impact q' rate' t, ← hsame t]
      congr 2
      refine sum_congr rfl (fun m _ => by rw [hsame (t - m)]))
  apply p1_thm_merged_measure_identified
  intro m
  have := hk m
  simpa [cohortKernel] using this

/-- **`thm:merged` (i), converse.** Economies with the same kernel (in particular the same merged measure) have the
same price impulse response. -/
theorem p1_thm_merged_model_converse {n n' : ℕ} (a impact : ℝ)
    (q rate : Fin n → ℝ) (q' rate' : Fin n' → ℝ)
    (hk : ∀ m, cohortKernel q rate m = cohortKernel q' rate' m) :
    ∀ j, actualCohortImpulse a impact q rate j = actualCohortImpulse a impact q' rate' j :=
  p1_thm_merged_kernel_from_measure a impact (cohortKernel q rate) _ _
    (p1_impulse_zero a impact q rate) (p1_impulse_zero a impact q' rate')
    (p1_impulse_closed_loop_recursion a impact q rate)
    (fun t => by rw [p1_impulse_closed_loop_recursion a impact q' rate' t]; simp only [hk])

end CurrentMM
