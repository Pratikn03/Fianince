import CurrentProofs.Execution

namespace CurrentMM
noncomputable section
open scoped BigOperators

def arMoment {n : ℕ} (decay : ℝ) (v : Fin n → ℝ) : ℝ :=
  ∑ i, decay ^ i.val * v i

def arQuadratic {n : ℕ} (decay : ℝ) (v : Fin n → ℝ) : ℝ :=
  ∑ i, ∑ j, v i * v j * decay ^ (Nat.dist i.val j.val)

def reverseMomentEnergy : (n : ℕ) → ℝ → (Fin n → ℝ) → ℝ
  | 0, _, _ => 0
  | n + 1, decay, v => (arMoment decay v) ^ 2 +
      reverseMomentEnergy n decay (fun i => v i.succ)

def probeEnergy {n : ℕ} (v : Fin n → ℝ) : ℝ := ∑ i, v i ^ 2

theorem ar_moment_succ {n : ℕ} (decay : ℝ) (v : Fin (n + 1) → ℝ) :
    arMoment decay v = v 0 + decay * arMoment decay (fun i : Fin n => v i.succ) := by
  unfold arMoment
  rw [Fin.sum_univ_succ]
  simp only [Fin.val_zero, pow_zero, one_mul, Fin.val_succ, pow_succ]
  rw [Finset.mul_sum]
  congr 1
  apply Finset.sum_congr rfl
  intro i hi
  ring

theorem ar_quadratic_succ {n : ℕ} (decay : ℝ) (v : Fin (n + 1) → ℝ) :
    arQuadratic decay v = v 0 ^ 2 +
      2 * decay * v 0 * arMoment decay (fun i : Fin n => v i.succ) +
      arQuadratic decay (fun i : Fin n => v i.succ) := by
  have hleft : (∑ i : Fin n, v 0 * v i.succ * decay ^ (i.val + 1)) =
      decay * v 0 * arMoment decay (fun i : Fin n => v i.succ) := by
    unfold arMoment
    rw [Finset.mul_sum]
    apply Finset.sum_congr rfl
    intro i hi
    rw [pow_succ]
    ring
  have hright : (∑ i : Fin n, v i.succ * v 0 * decay ^ (i.val + 1)) =
      decay * v 0 * arMoment decay (fun i : Fin n => v i.succ) := by
    unfold arMoment
    rw [Finset.mul_sum]
    apply Finset.sum_congr rfl
    intro i hi
    rw [pow_succ]
    ring
  unfold arQuadratic
  rw [Fin.sum_univ_succ]
  simp_rw [Fin.sum_univ_succ]
  simp only [Fin.val_zero, Fin.val_succ, Nat.dist_self, pow_zero, mul_one,
    Nat.dist_zero_left, Nat.dist_zero_right, Nat.dist_succ_succ]
  rw [Finset.sum_add_distrib]
  rw [hleft, hright]
  ring

theorem ar_reverse_factorization {n : ℕ} (decay : ℝ) (v : Fin n → ℝ) :
    arQuadratic decay v = (1 - decay ^ 2) * reverseMomentEnergy n decay v +
      decay ^ 2 * (arMoment decay v) ^ 2 := by
  induction n with
  | zero => simp [arQuadratic, reverseMomentEnergy, arMoment]
  | succ n ih =>
      rw [ar_quadratic_succ, ih, reverseMomentEnergy, ar_moment_succ]
      ring

theorem reverse_moment_energy_nonnegative {n : ℕ} (decay : ℝ) (v : Fin n → ℝ) :
    0 ≤ reverseMomentEnergy n decay v := by
  induction n with
  | zero => rfl
  | succ n ih =>
      exact add_nonneg (sq_nonneg _) (ih _)

theorem ar_reverse_energy_bound {n : ℕ} (decay : ℝ) (v : Fin n → ℝ)
    (hdecay : 0 ≤ decay) :
    probeEnergy v ≤ (1 + decay) ^ 2 * reverseMomentEnergy n decay v -
      decay * (1 + decay) * (arMoment decay v) ^ 2 := by
  induction n with
  | zero => simp [probeEnergy, reverseMomentEnergy, arMoment]
  | succ n ih =>
      have htail := ih (fun i : Fin n => v i.succ)
      have hs : 0 ≤ decay *
          (arMoment decay v + arMoment decay (fun i : Fin n => v i.succ)) ^ 2 :=
        mul_nonneg hdecay (sq_nonneg _)
      rw [ar_moment_succ] at hs ⊢
      unfold probeEnergy
      rw [Fin.sum_univ_succ]
      rw [reverseMomentEnergy, ar_moment_succ]
      unfold probeEnergy at htail
      nlinarith

theorem ar_quadratic_coercive {n : ℕ} (decay : ℝ) (v : Fin n → ℝ)
    (hzero : 0 ≤ decay) (hone : decay ≤ 1) :
    (1 - decay) / (1 + decay) * probeEnergy v ≤ arQuadratic decay v := by
  have henergy := ar_reverse_energy_bound decay v hzero
  have hW := reverse_moment_energy_nonnegative decay v
  have hpenalty : 0 ≤ decay * (1 + decay) * (arMoment decay v) ^ 2 := by positivity
  have hE : probeEnergy v ≤ (1 + decay) ^ 2 * reverseMomentEnergy n decay v := by linarith
  have hQ : (1 - decay ^ 2) * reverseMomentEnergy n decay v ≤ arQuadratic decay v := by
    rw [ar_reverse_factorization]
    exact le_add_of_nonneg_right (by positivity)
  have hden : 0 < 1 + decay := by linarith
  rw [div_mul_eq_mul_div]
  apply (div_le_iff₀ hden).2
  calc
    (1 - decay) * probeEnergy v ≤
        (1 - decay) * ((1 + decay) ^ 2 * reverseMomentEnergy n decay v) :=
      mul_le_mul_of_nonneg_left hE (by linarith)
    _ = ((1 - decay ^ 2) * reverseMomentEnergy n decay v) * (1 + decay) := by ring
    _ ≤ arQuadratic decay v * (1 + decay) := mul_le_mul_of_nonneg_right hQ (le_of_lt hden)

theorem decay_coercivity_monotone (decay radius : ℝ)
    (hzero : 0 ≤ decay) (horder : decay ≤ radius) :
    (1 - radius) / (1 + radius) ≤ (1 - decay) / (1 + decay) := by
  have hrad : 0 ≤ radius := le_trans hzero horder
  apply (div_le_div_iff₀ (by positivity) (by positivity)).2
  nlinarith

def positiveMixtureKernel {ι : Type*} [Fintype ι] (weights rates : ι → ℝ)
    (lag : ℕ) : ℝ := ∑ l, weights l * rates l ^ lag

theorem mixture_execution_cost_identity {ι : Type*} [Fintype ι] {n : ℕ}
    (weights rates : ι → ℝ) (v : Fin n → ℝ) :
    quadraticExecutionCost (positiveMixtureKernel weights rates) v =
      (∑ l, weights l * arQuadratic (rates l) v) / 2 := by
  have hraw : (∑ i, ∑ j, v i * v j * positiveMixtureKernel weights rates
      (Nat.dist i.val j.val)) = ∑ l, weights l * arQuadratic (rates l) v := by
    calc
      _ = ∑ i, ∑ j, ∑ l, weights l * v i * v j * rates l ^ (Nat.dist i.val j.val) := by
        apply Finset.sum_congr rfl
        intro i hi
        apply Finset.sum_congr rfl
        intro j hj
        unfold positiveMixtureKernel
        rw [Finset.mul_sum]
        apply Finset.sum_congr rfl
        intro l hl
        ring
      _ = ∑ i, ∑ l, ∑ j, weights l * v i * v j * rates l ^ (Nat.dist i.val j.val) := by
        apply Finset.sum_congr rfl
        intro i hi
        rw [Finset.sum_comm]
      _ = ∑ l, ∑ i, ∑ j, weights l * v i * v j * rates l ^ (Nat.dist i.val j.val) := by
        rw [Finset.sum_comm]
      _ = _ := by
        apply Finset.sum_congr rfl
        intro l hl
        unfold arQuadratic
        rw [Finset.mul_sum]
        apply Finset.sum_congr rfl
        intro i hi
        rw [Finset.mul_sum]
        apply Finset.sum_congr rfl
        intro j hj
        ring
  unfold quadraticExecutionCost
  rw [hraw]

theorem probe_energy_nonnegative {n : ℕ} (v : Fin n → ℝ) : 0 ≤ probeEnergy v :=
  Finset.sum_nonneg fun i _ => sq_nonneg (v i)

theorem mixture_execution_cost_coercive {ι : Type*} [Fintype ι] {n : ℕ}
    (weights rates : ι → ℝ) (v : Fin n → ℝ) (impact radius : ℝ)
    (hw : ∀ l, 0 ≤ weights l) (hr : ∀ l, 0 ≤ rates l ∧ rates l ≤ radius)
    (hradius : radius < 1) (hmass : ∑ l, weights l = impact) :
    impact * ((1 - radius) / (1 + radius)) / 2 * probeEnergy v ≤
      quadraticExecutionCost (positiveMixtureKernel weights rates) v := by
  have hE := probe_energy_nonnegative v
  have hpoint : ∀ l, (1 - radius) / (1 + radius) * probeEnergy v ≤
      arQuadratic (rates l) v := by
    intro l
    calc
      _ ≤ (1 - rates l) / (1 + rates l) * probeEnergy v :=
        mul_le_mul_of_nonneg_right (decay_coercivity_monotone _ _ (hr l).1 (hr l).2) hE
      _ ≤ _ := ar_quadratic_coercive _ v (hr l).1 (by linarith [(hr l).2])
  have hsum : (∑ l, weights l) * ((1 - radius) / (1 + radius) * probeEnergy v) ≤
      ∑ l, weights l * arQuadratic (rates l) v := by
    rw [Finset.sum_mul]
    exact Finset.sum_le_sum fun l _ => mul_le_mul_of_nonneg_left (hpoint l) (hw l)
  rw [hmass] at hsum
  rw [mixture_execution_cost_identity]
  linarith

theorem probe_energy_positive {n : ℕ} (v : Fin n → ℝ) (hv : v ≠ fun _ => 0) :
    0 < probeEnergy v := by
  have hex : ∃ i, v i ≠ 0 := by
    by_contra hn
    push Not at hn
    exact hv (funext hn)
  rcases hex with ⟨i, hi⟩
  unfold probeEnergy
  exact Finset.sum_pos' (fun j _ => sq_nonneg (v j))
    ⟨i, Finset.mem_univ i, sq_pos_of_ne_zero hi⟩

theorem mixture_execution_cost_positive {ι : Type*} [Fintype ι] {n : ℕ}
    (weights rates : ι → ℝ) (v : Fin n → ℝ) (impact radius : ℝ)
    (hw : ∀ l, 0 ≤ weights l) (hr : ∀ l, 0 ≤ rates l ∧ rates l ≤ radius)
    (hzero : 0 ≤ radius) (hradius : radius < 1) (hmass : ∑ l, weights l = impact)
    (hk : 0 < impact) (hv : v ≠ fun _ => 0) :
    0 < quadraticExecutionCost (positiveMixtureKernel weights rates) v := by
  have hcoerce := mixture_execution_cost_coercive weights rates v impact radius hw hr hradius hmass
  have hE := probe_energy_positive v hv
  have hc : 0 < impact * ((1 - radius) / (1 + radius)) / 2 * probeEnergy v := by positivity
  exact lt_of_lt_of_le hc hcoerce

theorem mixture_trader_solvency_energy {ι : Type*} [Fintype ι] {n : ℕ}
    (weights rates : ι → ℝ) (v : Fin n → ℝ) (B P impact fee radius : ℝ)
    (hw : ∀ l, 0 ≤ weights l) (hr : ∀ l, 0 ≤ rates l ∧ rates l ≤ radius)
    (hzero : 0 ≤ radius) (hradius : radius < 1) (hmass : ∑ l, weights l = impact)
    (hk : 0 < impact) (hf : 0 ≤ fee)
    (hsolvent : 0 ≤ equity (traderCashAfter B P impact fee
      (positiveMixtureKernel weights rates) v) (∑ i, v i) P) :
    probeEnergy v ≤ 2 * B / (impact * ((1 - radius) / (1 + radius))) := by
  have hkernel : positiveMixtureKernel weights rates 0 = impact := by
    simpa [positiveMixtureKernel] using hmass
  rw [actual_trader_fundamental_equity B P impact fee _ v hkernel] at hsolvent
  have hcoerce := mixture_execution_cost_coercive weights rates v impact radius hw hr hradius hmass
  have hfees : 0 ≤ fee * ∑ i, |v i| := by positivity
  have hm : 0 < impact * ((1 - radius) / (1 + radius)) := by positivity
  exact solvent_trader_energy_bound B _ _ (probeEnergy v) _ hsolvent hfees hcoerce hm

end
end CurrentMM
