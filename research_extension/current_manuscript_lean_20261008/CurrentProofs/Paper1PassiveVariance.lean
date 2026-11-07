import Mathlib.Probability.Moments.Variance
import Mathlib.MeasureTheory.Integral.Prod
import Mathlib.MeasureTheory.Constructions.Pi
import Mathlib.Probability.Independence.Basic

/-!
# Paper 1, Proposition `prop:passive0` (S3.2): passive distinction with zero controlled quantity

One three-step reset block has innovations `w₁, w₂, w₃` (i.i.d. with law `μW`, mean `0`, variance `s`, fourth moment
`m₄`) and observation noise `ν₁, ν₃` (i.i.d. with law `μN`, mean `0`, variance `σ²`), all independent. The first and
third observations are `x̃₁ = w₁ + ν₁` and `x̃₃ = b₂ w₁ + b₁ w₂ + w₃ + ν₃`. Independence is encoded by the product law
`passiveBlockLaw μW μN` on `(ℝ × ℝ) × ((ℝ × ℝ) × ℝ)` with coordinates `((w₁, ν₁), ((w₂, w₃), ν₃))`, and the block
statistic is `Z = x̃₁ x̃₃` (`passiveZ`).

* `p1_passive0_mean`: `E Z = b₂ s` (so two economies whose `b₂` differ by `κqδ²` have block means differing by
  `Δ = κ q s δ²`).
* `p1_passive0_second_moment`: `E Z² = b₂²(m₄ + sσ²) + (s + σ²)(b₁² s + s + σ²)`.
* `p1_passive0_variance_le`: `Var Z ≤ R := (s + σ²)(s(1 + b₁² + b₂²) + σ²) + s² b₂²` whenever `m₄ ≤ 3s²`
  (uniform innovations have `m₄ = 9s²/5`).
* `p1_iid_chebyshev`: for `n` independent blocks (`Measure.pi`), `P(|∑ Zᵢ - n E Z| ≥ c) ≤ n Var Z / c²`.
* `p1_thm_passive0`: the midpoint test of the block average has both errors at most `α` once `n ≥ 4R/(αΔ²)`.

Moment hypotheses: all powers of the innovation and noise laws are integrable (true for bounded uniform innovations
and Gaussian noise); only moments up to order four enter the formulas.
-/

namespace CurrentMM

open MeasureTheory ProbabilityTheory Finset

/-- The `k`-th raw moment. -/
noncomputable def mom (μ : Measure ℝ) (k : ℕ) : ℝ := ∫ x, x ^ k ∂μ

theorem p1_mom_zero (μ : Measure ℝ) [IsProbabilityMeasure μ] : mom μ 0 = 1 := by
  simp [mom]

/-- The law of one passive reset block: `((w₁, ν₁), ((w₂, w₃), ν₃))`. -/
noncomputable abbrev passiveBlockLaw (μW μN : Measure ℝ) : Measure ((ℝ × ℝ) × ((ℝ × ℝ) × ℝ)) :=
  (μW.prod μN).prod ((μW.prod μW).prod μN)

/-- The block statistic `x̃₁ x̃₃`. -/
def passiveZ (b1 b2 : ℝ) (ω : (ℝ × ℝ) × ((ℝ × ℝ) × ℝ)) : ℝ :=
  (ω.1.1 + ω.1.2) * (b2 * ω.1.1 + b1 * ω.2.1.1 + ω.2.1.2 + ω.2.2)

/-- A monomial `w₁^i ν₁^j w₂^k w₃^l ν₃^m`. -/
def blockMono (e : ℕ × ℕ × ℕ × ℕ × ℕ) (ω : (ℝ × ℝ) × ((ℝ × ℝ) × ℝ)) : ℝ :=
  (ω.1.1 ^ e.1 * ω.1.2 ^ e.2.1) * (ω.2.1.1 ^ e.2.2.1 * ω.2.1.2 ^ e.2.2.2.1 * ω.2.2 ^ e.2.2.2.2)

/-- Its expectation under the block law. -/
noncomputable def blockMom (μW μN : Measure ℝ) (e : ℕ × ℕ × ℕ × ℕ × ℕ) : ℝ :=
  mom μW e.1 * mom μN e.2.1 * (mom μW e.2.2.1 * mom μW e.2.2.2.1 * mom μN e.2.2.2.2)

theorem p1_mono2 (μ ν : Measure ℝ) [SFinite μ] [SFinite ν] (i j : ℕ) :
    ∫ z : ℝ × ℝ, z.1 ^ i * z.2 ^ j ∂(μ.prod ν) = (∫ x, x ^ i ∂μ) * ∫ y, y ^ j ∂ν :=
  integral_prod_mul (fun x : ℝ => x ^ i) (fun y : ℝ => y ^ j)

theorem p1_mono3 (μ ν ρ : Measure ℝ) [SFinite μ] [SFinite ν] [SFinite ρ] (k l m : ℕ) :
    ∫ c : (ℝ × ℝ) × ℝ, c.1.1 ^ k * c.1.2 ^ l * c.2 ^ m ∂((μ.prod ν).prod ρ) =
      (∫ x, x ^ k ∂μ) * (∫ x, x ^ l ∂ν) * ∫ x, x ^ m ∂ρ := by
  rw [← p1_mono2 μ ν k l]
  exact integral_prod_mul (fun p : ℝ × ℝ => p.1 ^ k * p.2 ^ l) (fun y : ℝ => y ^ m)

section Block

variable {μW μN : Measure ℝ} [IsProbabilityMeasure μW] [IsProbabilityMeasure μN]

theorem p1_mono5 (i j k l m : ℕ) :
    ∫ ω, (ω.1.1 ^ i * ω.1.2 ^ j) * (ω.2.1.1 ^ k * ω.2.1.2 ^ l * ω.2.2 ^ m) ∂(passiveBlockLaw μW μN) =
      mom μW i * mom μN j * (mom μW k * mom μW l * mom μN m) := by
  unfold mom
  rw [← p1_mono2 μW μN i j, ← p1_mono3 μW μW μN k l m]
  exact integral_prod_mul (fun p : ℝ × ℝ => p.1 ^ i * p.2 ^ j)
    (fun c : (ℝ × ℝ) × ℝ => c.1.1 ^ k * c.1.2 ^ l * c.2 ^ m)

variable (hW : ∀ k : ℕ, Integrable (fun x : ℝ => x ^ k) μW)
  (hN : ∀ k : ℕ, Integrable (fun x : ℝ => x ^ k) μN)

include hW hN in
theorem p1_blockMono_integrable (e : ℕ × ℕ × ℕ × ℕ × ℕ) :
    Integrable (blockMono e) (passiveBlockLaw μW μN) :=
  ((hW e.1).mul_prod (hN e.2.1)).mul_prod (((hW e.2.2.1).mul_prod (hW e.2.2.2.1)).mul_prod (hN e.2.2.2.2))

include hW hN in
theorem p1_block_poly_integrable {n : ℕ} (c : Fin n → ℝ) (e : Fin n → ℕ × ℕ × ℕ × ℕ × ℕ) :
    Integrable (fun ω => ∑ t, c t * blockMono (e t) ω) (passiveBlockLaw μW μN) :=
  integrable_finsetSum _ fun t _ => (p1_blockMono_integrable hW hN (e t)).const_mul (c t)

include hW hN in
theorem p1_block_poly_integral {n : ℕ} (c : Fin n → ℝ) (e : Fin n → ℕ × ℕ × ℕ × ℕ × ℕ) :
    ∫ ω, ∑ t, c t * blockMono (e t) ω ∂(passiveBlockLaw μW μN) = ∑ t, c t * blockMom μW μN (e t) := by
  rw [integral_finsetSum _ fun t _ => (p1_blockMono_integrable hW hN (e t)).const_mul (c t)]
  refine Finset.sum_congr rfl fun t _ => ?_
  rw [integral_const_mul]
  exact congrArg (fun x => c t * x) (p1_mono5 (e t).1 (e t).2.1 (e t).2.2.1 (e t).2.2.2.1 (e t).2.2.2.2)

/-- `Z` as a polynomial in the block coordinates. -/
noncomputable def passiveZc (b1 b2 : ℝ) : Fin 8 → ℝ := ![b2, b2, b1, 1, 1, b1, 1, 1]

def passiveZe : Fin 8 → ℕ × ℕ × ℕ × ℕ × ℕ :=
  ![(2, 0, 0, 0, 0), (1, 1, 0, 0, 0), (1, 0, 1, 0, 0), (1, 0, 0, 1, 0), (1, 0, 0, 0, 1), (0, 1, 1, 0, 0),
    (0, 1, 0, 1, 0), (0, 1, 0, 0, 1)]

/-- `Z²` as a polynomial in the block coordinates. -/
noncomputable def passiveZ2c (b1 b2 : ℝ) : Fin 30 → ℝ :=
  ![b2 ^ 2, 2 * b2 ^ 2, 2 * b1 * b2, 2 * b2, 2 * b2, b2 ^ 2, 4 * b1 * b2, 4 * b2, 4 * b2, b1 ^ 2, 2 * b1,
    2 * b1, 1, 2, 1, 2 * b1 * b2, 2 * b2, 2 * b2, 2 * b1 ^ 2, 4 * b1, 4 * b1, 2, 4, 2, b1 ^ 2, 2 * b1,
    2 * b1, 1, 2, 1]

def passiveZ2e : Fin 30 → ℕ × ℕ × ℕ × ℕ × ℕ :=
  ![(4, 0, 0, 0, 0), (3, 1, 0, 0, 0), (3, 0, 1, 0, 0), (3, 0, 0, 1, 0), (3, 0, 0, 0, 1), (2, 2, 0, 0, 0),
    (2, 1, 1, 0, 0), (2, 1, 0, 1, 0), (2, 1, 0, 0, 1), (2, 0, 2, 0, 0), (2, 0, 1, 1, 0), (2, 0, 1, 0, 1),
    (2, 0, 0, 2, 0), (2, 0, 0, 1, 1), (2, 0, 0, 0, 2), (1, 2, 1, 0, 0), (1, 2, 0, 1, 0), (1, 2, 0, 0, 1),
    (1, 1, 2, 0, 0), (1, 1, 1, 1, 0), (1, 1, 1, 0, 1), (1, 1, 0, 2, 0), (1, 1, 0, 1, 1), (1, 1, 0, 0, 2),
    (0, 2, 2, 0, 0), (0, 2, 1, 1, 0), (0, 2, 1, 0, 1), (0, 2, 0, 2, 0), (0, 2, 0, 1, 1), (0, 2, 0, 0, 2)]

theorem p1_passiveZ_poly (b1 b2 : ℝ) (ω : (ℝ × ℝ) × ((ℝ × ℝ) × ℝ)) :
    passiveZ b1 b2 ω = ∑ t, passiveZc b1 b2 t * blockMono (passiveZe t) ω := by
  simp only [passiveZ, passiveZc, passiveZe, blockMono, Fin.sum_univ_succ, Fin.sum_univ_zero,
    Matrix.cons_val_zero, Matrix.cons_val_succ]
  ring

theorem p1_passiveZ2_poly (b1 b2 : ℝ) (ω : (ℝ × ℝ) × ((ℝ × ℝ) × ℝ)) :
    passiveZ b1 b2 ω ^ 2 = ∑ t, passiveZ2c b1 b2 t * blockMono (passiveZ2e t) ω := by
  simp only [passiveZ, passiveZ2c, passiveZ2e, blockMono, Fin.sum_univ_succ, Fin.sum_univ_zero,
    Matrix.cons_val_zero, Matrix.cons_val_succ]
  ring

theorem p1_passiveZ_measurable (b1 b2 : ℝ) : Measurable (passiveZ b1 b2) := by
  unfold passiveZ
  fun_prop

variable (s σ2 m4 : ℝ)
  (hW1 : ∫ x, x ∂μW = 0) (hW2 : ∫ x, x ^ 2 ∂μW = s) (hW4 : ∫ x, x ^ 4 ∂μW = m4)
  (hN1 : ∫ x, x ∂μN = 0) (hN2 : ∫ x, x ^ 2 ∂μN = σ2)

include hW1 in
theorem p1_momW1 : mom μW 1 = 0 := by simpa [mom] using hW1

include hN1 in
theorem p1_momN1 : mom μN 1 = 0 := by simpa [mom] using hN1

include hW hN hW1 hW2 hN1 in
/-- **`E[x̃₁ x̃₃] = b₂ s`.** -/
theorem p1_passive0_mean (b1 b2 : ℝ) : ∫ ω, passiveZ b1 b2 ω ∂(passiveBlockLaw μW μN) = b2 * s := by
  have e : ∫ ω, passiveZ b1 b2 ω ∂(passiveBlockLaw μW μN) =
      ∫ ω, ∑ t, passiveZc b1 b2 t * blockMono (passiveZe t) ω ∂(passiveBlockLaw μW μN) :=
    integral_congr_ae (ae_of_all _ (p1_passiveZ_poly b1 b2))
  rw [e, p1_block_poly_integral hW hN (passiveZc b1 b2) passiveZe]
  have e1 := p1_momW1 hW1
  have e2 := p1_momN1 hN1
  have e3 : mom μW 2 = s := hW2
  simp only [passiveZc, passiveZe, blockMom, Fin.sum_univ_succ, Fin.sum_univ_zero, Matrix.cons_val_zero,
    Matrix.cons_val_succ, e1, e2, e3, p1_mom_zero]
  ring

include hW hN hW1 hW2 hW4 hN1 hN2 in
/-- **`E[(x̃₁ x̃₃)²] = b₂²(m₄ + sσ²) + (s + σ²)(b₁² s + s + σ²)`.** -/
theorem p1_passive0_second_moment (b1 b2 : ℝ) :
    ∫ ω, passiveZ b1 b2 ω ^ 2 ∂(passiveBlockLaw μW μN) =
      b2 ^ 2 * (m4 + s * σ2) + (s + σ2) * (b1 ^ 2 * s + s + σ2) := by
  have e : ∫ ω, passiveZ b1 b2 ω ^ 2 ∂(passiveBlockLaw μW μN) =
      ∫ ω, ∑ t, passiveZ2c b1 b2 t * blockMono (passiveZ2e t) ω ∂(passiveBlockLaw μW μN) :=
    integral_congr_ae (ae_of_all _ (p1_passiveZ2_poly b1 b2))
  rw [e, p1_block_poly_integral hW hN (passiveZ2c b1 b2) passiveZ2e]
  have e1 := p1_momW1 hW1
  have e2 := p1_momN1 hN1
  have e3 : mom μW 2 = s := hW2
  have e4 : mom μW 4 = m4 := hW4
  have e5 : mom μN 2 = σ2 := hN2
  simp only [passiveZ2c, passiveZ2e, blockMom, Fin.sum_univ_succ, Fin.sum_univ_zero, Matrix.cons_val_zero,
    Matrix.cons_val_succ, e1, e2, e3, e4, e5, p1_mom_zero]
  ring

include hW hN in
theorem p1_passiveZ_memLp (b1 b2 : ℝ) : MemLp (passiveZ b1 b2) 2 (passiveBlockLaw μW μN) := by
  refine (memLp_two_iff_integrable_sq (p1_passiveZ_measurable b1 b2).aestronglyMeasurable).2 ?_
  have e : (fun ω => passiveZ b1 b2 ω ^ 2) = fun ω => ∑ t, passiveZ2c b1 b2 t * blockMono (passiveZ2e t) ω :=
    funext (p1_passiveZ2_poly b1 b2)
  rw [e]
  exact p1_block_poly_integrable hW hN _ _

include hW hN hW1 hW2 hW4 hN1 hN2 in
/-- **The block variance bound.** If `m₄ ≤ 3s²` then `Var(x̃₁ x̃₃) ≤ (s + σ²)(s(1 + b₁² + b₂²) + σ²) + s² b₂²`. -/
theorem p1_passive0_variance_le (b1 b2 : ℝ) (hm4 : m4 ≤ 3 * s ^ 2) :
    variance (passiveZ b1 b2) (passiveBlockLaw μW μN) ≤
      (s + σ2) * (s * (1 + b1 ^ 2 + b2 ^ 2) + σ2) + s ^ 2 * b2 ^ 2 := by
  rw [variance_eq_sub (p1_passiveZ_memLp hW hN b1 b2)]
  have h2 := p1_passive0_second_moment hW hN s σ2 m4 hW1 hW2 hW4 hN1 hN2 b1 b2
  have h1 := p1_passive0_mean hW hN s hW1 hW2 hN1 b1 b2
  have h2' : ∫ ω, (passiveZ b1 b2 ^ 2) ω ∂(passiveBlockLaw μW μN) =
      b2 ^ 2 * (m4 + s * σ2) + (s + σ2) * (b1 ^ 2 * s + s + σ2) := h2
  rw [h2', h1]
  nlinarith [sq_nonneg b2, mul_le_mul_of_nonneg_left hm4 (sq_nonneg b2)]

end Block

/-! ### Independent blocks and the midpoint test -/

/-- **Chebyshev for `n` i.i.d. blocks.** -/
theorem p1_iid_chebyshev {Ω : Type*} [MeasurableSpace Ω] (P : Measure Ω) [IsProbabilityMeasure P]
    (Z : Ω → ℝ) (hZm : Measurable Z) (hZ : MemLp Z 2 P) (n : ℕ) {c : ℝ} (hc : 0 < c) :
    (Measure.pi fun _ : Fin n => P) {ω | c ≤ |∑ i, Z (ω i) - n * ∫ x, Z x ∂P|} ≤
      ENNReal.ofReal (n * variance Z P / c ^ 2) := by
  have hS : MemLp (∑ i : Fin n, fun ω : Fin n → Ω => Z (ω i)) 2 (Measure.pi fun _ : Fin n => P) :=
    memLp_finsetSum' _ fun i _ => (show MemLp (fun ω : Fin n → Ω => Z (ω i)) 2 (Measure.pi fun _ : Fin n => P) from
      hZ.comp_measurePreserving (measurePreserving_eval (fun _ : Fin n => P) i))
  have hEi : ∀ i : Fin n, ∫ ω, Z (ω i) ∂(Measure.pi fun _ : Fin n => P) = ∫ x, Z x ∂P := by
    intro i
    have h := integral_map (μ := Measure.pi fun _ : Fin n => P)
      (measurePreserving_eval (fun _ : Fin n => P) i).measurable.aemeasurable
      (f := Z) hZm.aestronglyMeasurable
    rw [(measurePreserving_eval (fun _ : Fin n => P) i).map_eq] at h
    exact h.symm
  have hES : ∫ ω, (∑ i : Fin n, fun ω : Fin n → Ω => Z (ω i)) ω ∂(Measure.pi fun _ : Fin n => P) =
      n * ∫ x, Z x ∂P := by
    simp only [Finset.sum_apply]
    rw [integral_finsetSum _ fun i _ =>
      (show Integrable (fun ω : Fin n → Ω => Z (ω i)) (Measure.pi fun _ : Fin n => P) from
        (hZ.comp_measurePreserving (measurePreserving_eval (fun _ : Fin n => P) i)).integrable one_le_two)]
    simp only [hEi, Finset.sum_const, Finset.card_univ, Fintype.card_fin, nsmul_eq_mul]
  have hV : variance (∑ i : Fin n, fun ω : Fin n → Ω => Z (ω i)) (Measure.pi fun _ : Fin n => P) =
      n * variance Z P := by
    rw [variance_sum_pi (X := fun _ : Fin n => Z) (fun _ => hZ)]
    simp [Finset.sum_const, Finset.card_univ, Fintype.card_fin, nsmul_eq_mul]
  have h := meas_ge_le_variance_div_sq hS hc
  rw [hES, hV] at h
  have hset : {ω : Fin n → Ω | c ≤ |∑ i, Z (ω i) - n * ∫ x, Z x ∂P|} =
      {ω | c ≤ |(∑ i : Fin n, fun ω : Fin n → Ω => Z (ω i)) ω - n * ∫ x, Z x ∂P|} := by
    ext ω
    simp only [Set.mem_setOf_eq, Finset.sum_apply]
  rw [hset]
  exact h

/-- The arithmetic of the sample-size condition: `n ≥ 4R/(αΔ²)` and `V ≤ R` give `nV/(nΔ/2)² ≤ α`. -/
theorem p1_sample_size_arith (n V R α Δ : ℝ) (hn : 0 < n) (hα : 0 < α) (hΔ : 0 < Δ) (hV : V ≤ R)
    (hN : 4 * R / (α * Δ ^ 2) ≤ n) : n * V / (n * Δ / 2) ^ 2 ≤ α := by
  have hd : 0 < α * Δ ^ 2 := by positivity
  rw [div_le_iff₀ hd] at hN
  rw [div_le_iff₀ (by positivity)]
  have h1 : n * V ≤ n * R := mul_le_mul_of_nonneg_left hV hn.le
  have h2 : n * (4 * R) ≤ n * (n * (α * Δ ^ 2)) := mul_le_mul_of_nonneg_left hN hn.le
  have e : α * (n * Δ / 2) ^ 2 = n * (n * (α * Δ ^ 2)) / 4 := by ring
  rw [e]
  linarith

/-- **Lower-tail error of the midpoint test.** If the block mean is `μ`, the block variance is at most `R` and
`n ≥ 4R/(αΔ²)`, the block sum falls below `n(μ - Δ/2)` with probability at most `α`. -/
theorem p1_midpoint_lower {Ω : Type*} [MeasurableSpace Ω] (P : Measure Ω) [IsProbabilityMeasure P]
    (Z : Ω → ℝ) (hZm : Measurable Z) (hZ : MemLp Z 2 P) (μ Δ R α : ℝ) (hE : ∫ x, Z x ∂P = μ)
    (hV : variance Z P ≤ R) (hα : 0 < α) (hΔ : 0 < Δ) (n : ℕ) (hn : 0 < n) (hN : 4 * R / (α * Δ ^ 2) ≤ n) :
    (Measure.pi fun _ : Fin n => P) {ω | ∑ i, Z (ω i) < n * (μ - Δ / 2)} ≤ ENNReal.ofReal α := by
  have hn' : (0 : ℝ) < n := Nat.cast_pos.mpr hn
  have hc : (0 : ℝ) < n * Δ / 2 := by positivity
  refine le_trans (measure_mono ?_) ((p1_iid_chebyshev P Z hZm hZ n hc).trans
    (ENNReal.ofReal_le_ofReal (p1_sample_size_arith n _ R α Δ hn' hα hΔ hV hN)))
  intro ω hω
  simp only [Set.mem_setOf_eq] at hω ⊢
  rw [hE]
  refine le_abs.mpr (Or.inr ?_)
  nlinarith

/-- **Upper-tail error of the midpoint test.** Same hypotheses; the block sum reaches `n(μ + Δ/2)` with probability
at most `α`. -/
theorem p1_midpoint_upper {Ω : Type*} [MeasurableSpace Ω] (P : Measure Ω) [IsProbabilityMeasure P]
    (Z : Ω → ℝ) (hZm : Measurable Z) (hZ : MemLp Z 2 P) (μ Δ R α : ℝ) (hE : ∫ x, Z x ∂P = μ)
    (hV : variance Z P ≤ R) (hα : 0 < α) (hΔ : 0 < Δ) (n : ℕ) (hn : 0 < n) (hN : 4 * R / (α * Δ ^ 2) ≤ n) :
    (Measure.pi fun _ : Fin n => P) {ω | n * (μ + Δ / 2) ≤ ∑ i, Z (ω i)} ≤ ENNReal.ofReal α := by
  have hn' : (0 : ℝ) < n := Nat.cast_pos.mpr hn
  have hc : (0 : ℝ) < n * Δ / 2 := by positivity
  refine le_trans (measure_mono ?_) ((p1_iid_chebyshev P Z hZm hZ n hc).trans
    (ENNReal.ofReal_le_ofReal (p1_sample_size_arith n _ R α Δ hn' hα hΔ hV hN)))
  intro ω hω
  simp only [Set.mem_setOf_eq] at hω ⊢
  rw [hE]
  refine le_abs.mpr (Or.inl ?_)
  nlinarith

/-- **Proposition `prop:passive0`.** Two economies with the same `b₁` and `b₂` values `b₂₀ > b₂δ` (the single cohort
and the pair; `b₂₀ - b₂δ = κqδ²`), innovations with mean `0`, variance `s > 0` and fourth moment `m₄ ≤ 3s²`, and
centred observation noise of variance `σ²`. With `Δ = (b₂₀ - b₂δ)s` and `R` bounding both block-variance bounds, the
midpoint test on `n ≥ 4R/(αΔ²)` independent blocks (declare the pair when the average product is below
`(b₂₀ + b₂δ)s/2`) errs with probability at most `α` under each economy. No probe is traded. -/
theorem p1_thm_passive0 {μW μN : Measure ℝ} [IsProbabilityMeasure μW] [IsProbabilityMeasure μN]
    (hW : ∀ k : ℕ, Integrable (fun x : ℝ => x ^ k) μW) (hN : ∀ k : ℕ, Integrable (fun x : ℝ => x ^ k) μN)
    (s σ2 m4 : ℝ) (hW1 : ∫ x, x ∂μW = 0) (hW2 : ∫ x, x ^ 2 ∂μW = s) (hW4 : ∫ x, x ^ 4 ∂μW = m4)
    (hN1 : ∫ x, x ∂μN = 0) (hN2 : ∫ x, x ^ 2 ∂μN = σ2) (hm4 : m4 ≤ 3 * s ^ 2) (hs : 0 < s)
    (b1 b20 b2δ R α : ℝ) (hb : b2δ < b20)
    (hR0 : (s + σ2) * (s * (1 + b1 ^ 2 + b20 ^ 2) + σ2) + s ^ 2 * b20 ^ 2 ≤ R)
    (hR1 : (s + σ2) * (s * (1 + b1 ^ 2 + b2δ ^ 2) + σ2) + s ^ 2 * b2δ ^ 2 ≤ R) (hα : 0 < α)
    (n : ℕ) (hn : 0 < n) (hNn : 4 * R / (α * ((b20 - b2δ) * s) ^ 2) ≤ n) :
    (Measure.pi fun _ : Fin n => passiveBlockLaw μW μN)
        {ω | ∑ i, passiveZ b1 b20 (ω i) < n * ((b20 + b2δ) * s / 2)} ≤ ENNReal.ofReal α ∧
    (Measure.pi fun _ : Fin n => passiveBlockLaw μW μN)
        {ω | n * ((b20 + b2δ) * s / 2) ≤ ∑ i, passiveZ b1 b2δ (ω i)} ≤ ENNReal.ofReal α := by
  have hΔ : 0 < (b20 - b2δ) * s := mul_pos (sub_pos.mpr hb) hs
  have hmid0 : (b20 + b2δ) * s / 2 = b20 * s - (b20 - b2δ) * s / 2 := by ring
  have hmid1 : (b20 + b2δ) * s / 2 = b2δ * s + (b20 - b2δ) * s / 2 := by ring
  have h0 := p1_midpoint_lower (passiveBlockLaw μW μN) (passiveZ b1 b20)
    (p1_passiveZ_measurable b1 b20) (p1_passiveZ_memLp hW hN b1 b20)
    (b20 * s) ((b20 - b2δ) * s) R α (p1_passive0_mean hW hN s hW1 hW2 hN1 b1 b20)
    ((p1_passive0_variance_le hW hN s σ2 m4 hW1 hW2 hW4 hN1 hN2 b1 b20 hm4).trans hR0) hα hΔ n hn hNn
  have h1 := p1_midpoint_upper (passiveBlockLaw μW μN) (passiveZ b1 b2δ)
    (p1_passiveZ_measurable b1 b2δ) (p1_passiveZ_memLp hW hN b1 b2δ)
    (b2δ * s) ((b20 - b2δ) * s) R α (p1_passive0_mean hW hN s hW1 hW2 hN1 b1 b2δ)
    ((p1_passive0_variance_le hW hN s σ2 m4 hW1 hW2 hW4 hN1 hN2 b1 b2δ hm4).trans hR1) hα hΔ n hn hNn
  refine ⟨?_, ?_⟩
  · rw [hmid0]; exact h0
  · rw [hmid1]; exact h1

end CurrentMM
