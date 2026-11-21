import Mathlib

/-!
# Paper 1, 21 November 2026: the barrier in a real market (measurement P1M)

Deterministic steps behind the Taiwan measurement (protocol `P1M_measurement_protocol.md`).

* A class with rule `w r^m` (`|r| < 1`) contributes `κ w / (1 - r)` to the feedback budget, so halting it lowers the
  budget by exactly that amount (`halt_geometric`, `budget_of_rules`, `halt_effect`).
* Relabeling the classes leaves the aggregate kernel, and hence the price process, unchanged, but moves the halt
  effect of a given label to another class (`relabel_kernel`, `relabel_halt`).
* A uniform cut depends on the aggregate kernel alone (`uniform_cut_kernel`, `uniform_cut_effect`).
* The Whittle integrand is nonnegative and vanishes only where the spectra agree; with a common non-feedback spectrum
  the spectral ratio is the ratio of the `|A|²` (`whittle_integrand_nonneg`, `whittle_integrand_pos`,
  `spectral_ratio`).
* Pinsker turns a divergence budget into indistinguishability, and a power target into a minimum record length
  (`pinsker_indistinguishable`, `pinsker_record_length`).

Whittle's formula for the divergence rate and Pinsker's inequality enter as hypotheses on real numbers.
-/
namespace Paper1Revision7

open scoped BigOperators

/-- A geometric kernel `κ w r^m` sums to `κ w / (1 - r)`. -/
theorem halt_geometric (κ w r : ℝ) (hr : |r| < 1) :
    ∑' m : ℕ, κ * w * r ^ m = κ * w / (1 - r) := by
  rw [tsum_mul_left, tsum_geometric_of_abs_lt_one hr, div_eq_mul_inv]

/-- The feedback part of the budget of a population of classes with rules `w_c r_c^m` is `Σ_c κ w_c / (1 - r_c)`. -/
theorem budget_of_rules {ι : Type*} [Fintype ι] (κ : ℝ) (w r : ι → ℝ) (hr : ∀ c, |r c| < 1) :
    ∑' m : ℕ, κ * ∑ c, w c * r c ^ m = ∑ c, κ * w c / (1 - r c) := by
  have hs : ∀ c ∈ (Finset.univ : Finset ι), Summable (fun m : ℕ => κ * w c * r c ^ m) :=
    fun c _ => (summable_geometric_of_abs_lt_one (hr c)).mul_left (κ * w c)
  calc ∑' m : ℕ, κ * ∑ c, w c * r c ^ m = ∑' m : ℕ, ∑ c, κ * w c * r c ^ m := by
        congr 1; funext m; rw [Finset.mul_sum]; congr 1; funext c; ring
    _ = ∑ c, ∑' m : ℕ, κ * w c * r c ^ m := Summable.tsum_finsetSum hs
    _ = ∑ c, κ * w c / (1 - r c) := by
        congr 1; funext c; exact halt_geometric κ (w c) (r c) (hr c)

/-- Halting class `F` removes exactly its contribution: the budget falls by `h F`. -/
theorem halt_effect {ι : Type*} [Fintype ι] [DecidableEq ι] (A : ℝ) (h : ι → ℝ) (F : ι) :
    (A + ∑ c, h c) - (A + ∑ c ∈ Finset.univ.erase F, h c) = h F := by
  have := Finset.add_sum_erase (Finset.univ : Finset ι) h (Finset.mem_univ F)
  linarith

/-- Relabeling the classes leaves the aggregate kernel unchanged at every lag. -/
theorem relabel_kernel {ι : Type*} [Fintype ι] (σ : Equiv.Perm ι) (w r : ι → ℝ) (m : ℕ) :
    ∑ c, w (σ c) * r (σ c) ^ m = ∑ c, w c * r c ^ m :=
  Equiv.sum_comp σ (fun c => w c * r c ^ m)

/-- In the relabeled population the class labelled `F` carries the rule of class `σ F`, so halting it removes
`κ w(σ F)/(1 - r(σ F))`, while the aggregate kernel (and every uniform cut) is unchanged. -/
theorem relabel_halt {ι : Type*} [Fintype ι] (σ : Equiv.Perm ι) (κ : ℝ) (w r : ι → ℝ) (F : ι) :
    (∀ m : ℕ, ∑ c, w (σ c) * r (σ c) ^ m = ∑ c, w c * r c ^ m) ∧
    κ * (w ∘ σ) F / (1 - (r ∘ σ) F) = κ * w (σ F) / (1 - r (σ F)) :=
  ⟨fun m => relabel_kernel σ w r m, rfl⟩

/-- A uniform cut by `l` scales the aggregate kernel, whatever the composition behind it. -/
theorem uniform_cut_kernel {ι ι' : Type*} [Fintype ι] [Fintype ι'] (l : ℝ) (w r : ι → ℝ) (w' r' : ι' → ℝ)
    (heq : ∀ m : ℕ, ∑ c, w c * r c ^ m = ∑ c, w' c * r' c ^ m) (m : ℕ) :
    ∑ c, (l * w c) * r c ^ m = ∑ c, (l * w' c) * r' c ^ m := by
  have h1 : ∑ c, (l * w c) * r c ^ m = l * ∑ c, w c * r c ^ m := by
    rw [Finset.mul_sum]; congr 1; funext c; ring
  have h2 : ∑ c, (l * w' c) * r' c ^ m = l * ∑ c, w' c * r' c ^ m := by
    rw [Finset.mul_sum]; congr 1; funext c; ring
  rw [h1, h2, heq m]

/-- Two compositions with the same aggregate kernel have the same uniform-cut effect `(1 - l) κ Σ_m k_m`. -/
theorem uniform_cut_effect {ι ι' : Type*} [Fintype ι] [Fintype ι'] (κ l : ℝ) (w r : ι → ℝ) (w' r' : ι' → ℝ)
    (heq : ∀ m : ℕ, ∑ c, w c * r c ^ m = ∑ c, w' c * r' c ^ m) :
    (1 - l) * ∑' m : ℕ, κ * ∑ c, w c * r c ^ m = (1 - l) * ∑' m : ℕ, κ * ∑ c, w' c * r' c ^ m := by
  congr 2; funext m; rw [heq m]

/-- The Whittle integrand `R - 1 - log R` is nonnegative. -/
theorem whittle_integrand_nonneg (R : ℝ) (hR : 0 < R) : 0 ≤ R - 1 - Real.log R := by
  have := Real.log_le_sub_one_of_pos hR
  linarith

/-- ... and positive wherever the two spectra differ. -/
theorem whittle_integrand_pos (R : ℝ) (hR : 0 < R) (h1 : R ≠ 1) : 0 < R - 1 - Real.log R := by
  have := Real.log_lt_sub_one_of_pos hR h1
  linarith

/-- With a common non-feedback spectrum `g`, the ratio of the spectral densities `g/|A|²` and `g/|A'|²` is
`|A'|²/|A|²`: the divergence rate depends on the composition only through `A`. -/
theorem spectral_ratio (g a a' : ℝ) (hg : g ≠ 0) (ha : a ≠ 0) (ha' : a' ≠ 0) :
    (g / a) / (g / a') = a' / a := by
  field_simp

/-- Indistinguishability: if the record's divergence `n · rate` is at most `J0`, then (given Pinsker,
`TV ≤ √(KL/2)`, and `power - size ≤ TV`) no test has power more than `√(J0/2)` above its size. -/
theorem pinsker_indistinguishable (power size tv n rate J0 : ℝ)
    (htv : power - size ≤ tv) (hpin : tv ≤ Real.sqrt (n * rate / 2)) (hJ : n * rate ≤ J0) :
    power - size ≤ Real.sqrt (J0 / 2) := by
  have : Real.sqrt (n * rate / 2) ≤ Real.sqrt (J0 / 2) := Real.sqrt_le_sqrt (by linarith)
  linarith

/-- Minimum record length: a test whose power exceeds its size by `δ > 0` needs `n ≥ 2 δ² / rate`. -/
theorem pinsker_record_length (power size tv n rate δ : ℝ) (hδ : 0 < δ) (hrate : 0 < rate)
    (hpow : δ ≤ power - size) (htv : power - size ≤ tv) (hpin : tv ≤ Real.sqrt (n * rate / 2)) :
    2 * δ ^ 2 / rate ≤ n := by
  have hle : δ ≤ Real.sqrt (n * rate / 2) := by linarith
  have hsq : δ ^ 2 ≤ n * rate / 2 := by
    have h0 : 0 ≤ δ := hδ.le
    have hs : 0 ≤ Real.sqrt (n * rate / 2) := Real.sqrt_nonneg _
    have hnr : 0 ≤ n * rate / 2 := by
      by_contra hneg
      push_neg at hneg
      have : Real.sqrt (n * rate / 2) = 0 := Real.sqrt_eq_zero'.mpr hneg.le
      linarith
    calc δ ^ 2 ≤ Real.sqrt (n * rate / 2) ^ 2 := pow_le_pow_left₀ h0 hle 2
      _ = n * rate / 2 := Real.sq_sqrt hnr
  rw [div_le_iff₀ hrate]
  linarith

/-- Pooling `N` independent stocks divides the record length each stock must supply by `N`. -/
theorem pooled_length (nOne N : ℝ) (hN : 0 < N) : nOne / N * N = nOne := by
  field_simp

end Paper1Revision7
