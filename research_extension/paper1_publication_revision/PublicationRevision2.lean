import Mathlib

/-!
# Paper 1, 20 November 2026 revision: deterministic steps of the new results

Machine-checked steps of Theorems 5.5 (smooth-family lower bound), 5.7 (recovery within a shrinking
cluster), 6.1 (pairwise detection and forecast mismatch), 6.2 (forecast benchmark) and 6.3 (uniform
cumulative log-loss) of the 20 November 2026 manuscript, complementing `PublicationRevision.lean`.

NOT formalized here: the Gaussian Kullback--Leibler chain rule, Pinsker's inequality, Gaussian
concentration, the Ing--Wei expansion, the matrix determinant-trace inequality, and existence of the
Gauss and Gauss--Radau rules. Where a step uses one of them, it enters as an explicit hypothesis.
-/
namespace Paper1Revision2

open Finset Real

/-! ## Theorem 6.1: detection needs one unit of cumulative forecast loss -/

/-- If both error probabilities are below `1/4`, the total variation exceeds `1/2`
(the sum of the two errors is at least `1 - TV`). -/
theorem tv_gt_half_of_errors (α β tv : ℝ) (hα : α < 1/4) (hβ : β < 1/4)
    (htest : 1 - tv ≤ α + β) : 1/2 < tv := by linarith

/-- With `KL = Λ/2` (Gaussian chain rule) and Pinsker `KL ≥ 2 TV²`, total variation above `1/2`
forces `Λ > 1`. -/
theorem detection_needs_unit_loss (KL Λ tv : ℝ) (hKL : KL = Λ / 2)
    (hpinsker : 2 * tv ^ 2 ≤ KL) (htv : 1/2 < tv) : 1 < Λ := by
  have h1 : (1:ℝ)/4 < tv ^ 2 := by nlinarith
  nlinarith

/-- Test errors below `1/4` need `Λ > 1`. -/
theorem errors_need_unit_loss (α β tv KL Λ : ℝ) (hα : α < 1/4) (hβ : β < 1/4)
    (htest : 1 - tv ≤ α + β) (hKL : KL = Λ / 2) (hpinsker : 2 * tv ^ 2 ≤ KL) : 1 < Λ :=
  detection_needs_unit_loss KL Λ tv hKL hpinsker (tv_gt_half_of_errors α β tv hα hβ htest)

/-- Theorem 5.5(ii): a per-period loss bound `V ≤ c d` and `Λ > 1` give `T > 1/(c d)`. -/
theorem sample_size_lower_bound (T Λ c d : ℝ) (hc : 0 < c) (hd : 0 < d)
    (hΛ : Λ ≤ T * (c * d)) (h1 : 1 < Λ) : 1 / (c * d) < T := by
  have hcd : 0 < c * d := mul_pos hc hd
  rw [div_lt_iff₀ hcd]; linarith

/-- Theorem 6.1(iii): a Bayesian mixture with prior mass `w j⋆ > 0` on the true candidate loses at
most `log (1/w j⋆)` in log predictive likelihood, on every path. -/
theorem bayes_mixture_regret {n : ℕ} (w p : Fin n → ℝ) (j : Fin n)
    (hw : ∀ i, 0 ≤ w i) (hp : ∀ i, 0 < p i) (hwj : 0 < w j) :
    Real.log (p j) - Real.log (∑ i, w i * p i) ≤ Real.log (1 / w j) := by
  have hterm : w j * p j ≤ ∑ i, w i * p i :=
    Finset.single_le_sum (f := fun i => w i * p i)
      (fun i _ => mul_nonneg (hw i) (hp i).le) (Finset.mem_univ j)
  have hpos : 0 < w j * p j := mul_pos hwj (hp j)
  have hlog : Real.log (w j * p j) ≤ Real.log (∑ i, w i * p i) := Real.log_le_log hpos hterm
  rw [Real.log_mul hwj.ne' (hp j).ne', one_div, Real.log_inv] at *
  linarith

/-! ## Theorem 6.2(i): positions are functions of past prices, and the forecast uses the kernel -/

/-- A group's position with zero initial state, `y_t = r y_{t-1} + η x_t`. -/
def pos (r η : ℝ) (x : ℕ → ℝ) : ℕ → ℝ
  | 0 => η * x 0
  | t + 1 => r * pos r η x t + η * x (t + 1)

/-- Closed form: `y_t = Σ_{j ≤ t} η r^j x_{t-j}`. -/
theorem pos_closed (r η : ℝ) (x : ℕ → ℝ) (t : ℕ) :
    pos r η x t = ∑ j ∈ range (t + 1), η * r ^ j * x (t - j) := by
  induction t with
  | zero => simp [pos]
  | succ t ih =>
    rw [pos, ih, Finset.sum_range_succ' _ (t + 1)]
    simp only [pow_zero, mul_one, Nat.sub_zero]
    rw [Finset.mul_sum]
    congr 1
    apply Finset.sum_congr rfl
    intro j hj
    have : t + 1 - (j + 1) = t - j := by omega
    rw [this, pow_succ]; ring

/-- The weighted sum of positions is the kernel convolution of past prices, with
`k_m = Σ_i q_i η_i r_i^m`. -/
theorem positions_kernel {K : ℕ} (q r η : Fin K → ℝ) (x : ℕ → ℝ) (t : ℕ) :
    ∑ i, q i * pos (r i) (η i) x t =
      ∑ m ∈ range (t + 1), (∑ i, q i * η i * r i ^ m) * x (t - m) := by
  simp_rw [pos_closed, Finset.mul_sum, Finset.sum_mul]
  rw [Finset.sum_comm]
  apply Finset.sum_congr rfl; intro m _
  apply Finset.sum_congr rfl; intro i _
  ring

/-! ## Theorems 6.2(ii) and 6.3: the omitted autoregressive coefficients -/

/-- `Σ_{m < n} (1-r) r^{L+m} = r^L (1 - r^n) ≤ r^L` for `0 ≤ r ≤ 1`. -/
theorem geometric_tail (r : ℝ) (L n : ℕ) (h0 : 0 ≤ r) (h1 : r ≤ 1) :
    ∑ m ∈ range n, (1 - r) * r ^ (L + m) ≤ r ^ L := by
  have hsum : ∑ m ∈ range n, (1 - r) * r ^ (L + m) = r ^ L * (1 - r ^ n) := by
    induction n with
    | zero => simp
    | succ n ih => rw [Finset.sum_range_succ, ih, pow_add, pow_succ]; ring
  rw [hsum]
  have : 0 ≤ r ^ n := pow_nonneg h0 n
  have hL : 0 ≤ r ^ L := pow_nonneg h0 L
  nlinarith

/-- The omitted coefficients `κ Σ_i q_i r_i^L` are at most `S r̄^L`, where
`S = a + κ Σ_i q_i` is the feedback budget and `r̄` bounds every memory rate. -/
theorem tail_budget {K : ℕ} (q r : Fin K → ℝ) (a κ rbar : ℝ) (L : ℕ)
    (hq : ∀ i, 0 ≤ q i) (hr0 : ∀ i, 0 ≤ r i) (hr : ∀ i, r i ≤ rbar) (hrbar0 : 0 ≤ rbar)
    (ha : 0 ≤ a) (hκ : 0 ≤ κ) :
    κ * ∑ i, q i * r i ^ L ≤ (a + κ * ∑ i, q i) * rbar ^ L := by
  have hpow : ∀ i, r i ^ L ≤ rbar ^ L := fun i => pow_le_pow_left₀ (hr0 i) (hr i) L
  have hsum : ∑ i, q i * r i ^ L ≤ (∑ i, q i) * rbar ^ L := by
    rw [Finset.sum_mul]
    exact Finset.sum_le_sum fun i _ => mul_le_mul_of_nonneg_left (hpow i) (hq i)
  have hrbar : 0 ≤ rbar ^ L := pow_nonneg hrbar0 L
  nlinarith [mul_le_mul_of_nonneg_left hsum hκ, mul_nonneg ha hrbar]

/-- Choosing `L ≥ log T / (2 log (1/r̄))` makes the truncation term `T r̄^{2L}` at most one. -/
theorem order_choice (T rbar : ℝ) (L : ℕ) (hT : 0 < T) (h0 : 0 < rbar) (h1 : rbar < 1)
    (hL : Real.log T ≤ 2 * L * Real.log (1 / rbar)) : T * rbar ^ (2 * L) ≤ 1 := by
  have hlogr : Real.log rbar < 0 := Real.log_neg h0 h1
  have hp : 0 < rbar ^ (2 * L) := pow_pos h0 _
  have key : Real.log (T * rbar ^ (2 * L)) ≤ 0 := by
    rw [Real.log_mul hT.ne' hp.ne', Real.log_pow, one_div, Real.log_inv] at *
    push_cast at *
    linarith
  have hpos : 0 < T * rbar ^ (2 * L) := mul_pos hT hp
  have := Real.exp_log hpos
  calc T * rbar ^ (2 * L) = Real.exp (Real.log (T * rbar ^ (2 * L))) := this.symm
    _ ≤ Real.exp 0 := Real.exp_le_exp.mpr key
    _ = 1 := Real.exp_zero

/-- Theorem 6.3, the log-determinant step after diagonalization: for eigenvalues `λ_i ≥ 0`,
`Σ_i log (1 + λ_i) ≤ L log (1 + (Σ_i λ_i)/L)` (Jensen for the concave logarithm). -/
theorem sum_log_le {L : ℕ} (hL : 0 < L) (lam : Fin L → ℝ) (hlam : ∀ i, 0 ≤ lam i) :
    ∑ i, Real.log (1 + lam i) ≤ L * Real.log (1 + (∑ i, lam i) / L) := by
  have hLr : (0:ℝ) < L := by exact_mod_cast hL
  have hconc : ConcaveOn ℝ (Set.Ioi 0) Real.log := strictConcaveOn_log_Ioi.concaveOn
  have hw : ∀ i ∈ (univ : Finset (Fin L)), (0:ℝ) ≤ 1 / L := fun _ _ => by positivity
  have hw1 : ∑ i ∈ (univ : Finset (Fin L)), (1:ℝ) / L = 1 := by
    simp [Finset.card_univ, Fintype.card_fin]; field_simp
  have hmem : ∀ i ∈ (univ : Finset (Fin L)), 1 + lam i ∈ Set.Ioi (0:ℝ) := fun i _ => by
    simp only [Set.mem_Ioi]; linarith [hlam i]
  have hj := hconc.le_map_sum hw hw1 hmem
  simp only [smul_eq_mul] at hj
  have hrhs : ∑ i, 1 / (L:ℝ) * (1 + lam i) = 1 + (∑ i, lam i) / L := by
    rw [← Finset.mul_sum, Finset.sum_add_distrib]
    simp [Finset.card_univ, Fintype.card_fin]; field_simp
  rw [hrhs, ← Finset.mul_sum] at hj
  have := mul_le_mul_of_nonneg_left hj hLr.le
  rw [← mul_assoc, mul_one_div_cancel hLr.ne', one_mul] at this
  exact this

/-! ## Theorem 5.7: moments determine a signed atomic measure (Vandermonde step) -/

/-- If a signed measure with `m` distinct atoms has vanishing moments of orders `0, …, m-1`,
every weight is zero. Two `K`-atom populations with equal moments below order `2K` differ by such a
measure with at most `2K` atoms, which gives the injectivity used in Theorem 5.7. -/
theorem vandermonde_signed_zero {m : ℕ} (z c : Fin m → ℝ) (hz : Function.Injective z)
    (hmom : ∀ p : Fin m, ∑ j, c j * z j ^ (p : ℕ) = 0) : c = 0 := by
  have hdet : (Matrix.vandermonde z).det ≠ 0 := by
    rw [Matrix.det_vandermonde_ne_zero_iff]; exact hz
  apply Matrix.eq_zero_of_vecMul_eq_zero hdet
  funext p
  simp only [Matrix.vecMul, dotProduct, Matrix.vandermonde_apply, Pi.zero_apply]
  exact hmom p

end Paper1Revision2

#print axioms Paper1Revision2.tv_gt_half_of_errors
#print axioms Paper1Revision2.detection_needs_unit_loss
#print axioms Paper1Revision2.errors_need_unit_loss
#print axioms Paper1Revision2.sample_size_lower_bound
#print axioms Paper1Revision2.bayes_mixture_regret
#print axioms Paper1Revision2.pos_closed
#print axioms Paper1Revision2.positions_kernel
#print axioms Paper1Revision2.geometric_tail
#print axioms Paper1Revision2.tail_budget
#print axioms Paper1Revision2.order_choice
#print axioms Paper1Revision2.sum_log_le
#print axioms Paper1Revision2.vandermonde_signed_zero
