import CurrentProofs.CohortConvolution
import CurrentProofs.SequenceMargin
import CurrentProofs.ARKernels
import Mathlib.Analysis.Matrix.PosDef
import Mathlib.Analysis.SpecificLimits.Basic
import Mathlib.Algebra.Order.BigOperators.Ring.Finset
import Mathlib.Topology.Order.DenselyOrdered

namespace CurrentMM
noncomputable section
open scoped BigOperators Matrix

theorem diagonal_minus_rank_one_posDef {ι : Type*} [Fintype ι] [DecidableEq ι]
    (d u : ι → ℝ) (hd : ∀ i, 0 < d i) (hsmall : (∑ i, u i ^ 2 / d i) < 1) :
    (Matrix.diagonal d - Matrix.vecMulVec u u).PosDef := by
  have herm : (Matrix.vecMulVec u u).IsHermitian := by
    simpa using (Matrix.posSemidef_vecMulVec_self_star u).isHermitian
  apply Matrix.PosDef.of_dotProduct_mulVec_pos ((Matrix.isHermitian_diagonal d).sub herm)
  intro z hz
  let f : ι → ℝ := fun i => u i / Real.sqrt (d i)
  let g : ι → ℝ := fun i => Real.sqrt (d i) * z i
  have hsqrt (i : ι) : Real.sqrt (d i) ≠ 0 := ne_of_gt (Real.sqrt_pos.2 (hd i))
  have hfg : (∑ i, f i * g i) = ∑ i, u i * z i := by
    apply Finset.sum_congr rfl
    intro i hi
    dsimp [f, g]
    field_simp [hsqrt i]
  have hf : (∑ i, f i ^ 2) = ∑ i, u i ^ 2 / d i := by
    apply Finset.sum_congr rfl
    intro i hi
    simp [f, div_pow, Real.sq_sqrt (le_of_lt (hd i))]
  have hg : (∑ i, g i ^ 2) = ∑ i, d i * z i ^ 2 := by
    apply Finset.sum_congr rfl
    intro i hi
    simp [g, mul_pow, Real.sq_sqrt (le_of_lt (hd i))]
  have hcs := Finset.sum_mul_sq_le_sq_mul_sq Finset.univ f g
  rw [hfg, hf, hg] at hcs
  obtain ⟨j, hj⟩ := Function.ne_iff.mp hz
  have hQ : 0 < ∑ i, d i * z i ^ 2 := by
    apply Finset.sum_pos'
    · intro i hi
      exact mul_nonneg (le_of_lt (hd i)) (sq_nonneg _)
    · exact ⟨j, Finset.mem_univ j, mul_pos (hd j) (sq_pos_of_ne_zero hj)⟩
  have hquad : star z ⬝ᵥ ((Matrix.diagonal d - Matrix.vecMulVec u u) *ᵥ z) =
      (∑ i, d i * z i ^ 2) - (∑ i, u i * z i) ^ 2 := by
    have hv (i : ι) : (Matrix.vecMulVec u u *ᵥ z) i =
        u i * (∑ j, u j * z j) := by
      simp [Matrix.mulVec, Matrix.vecMulVec, dotProduct, Finset.mul_sum, mul_assoc]
    rw [Matrix.sub_mulVec, dotProduct_sub]
    simp only [star_trivial, dotProduct]
    simp_rw [Matrix.mulVec_diagonal, hv]
    have hdiag : (∑ i, z i * (d i * z i)) = ∑ i, d i * z i ^ 2 := by
      apply Finset.sum_congr rfl
      intro i hi
      ring
    have hprod : (∑ i, z i * (u i * ∑ j, u j * z j)) = (∑ i, u i * z i) ^ 2 := by
      rw [pow_two, Finset.sum_mul]
      apply Finset.sum_congr rfl
      intro i hi
      ring
    rw [hdiag, hprod]
  rw [hquad]
  nlinarith [mul_pos (sub_pos.2 hsmall) hQ]

def cohortSpectralScale {n : ℕ} (a impact : ℝ) (q rate : Fin n → ℝ) : Option (Fin n) → ℝ :=
  fun i => i.elim (Real.sqrt a) (fun j => Real.sqrt (impact * q j / rate j))

def cohortSpectralVector {n : ℕ} (a impact : ℝ) (q rate : Fin n → ℝ) : Option (Fin n) → ℝ :=
  fun i => i.elim (Real.sqrt a)
    (fun j => rate j * Real.sqrt (impact * q j / rate j))

def cohortSpectralResidual {n : ℕ} (rate : Fin n → ℝ) : Option (Fin n) → ℝ :=
  fun i => i.elim 0 (fun j => 1 - rate j)

def cohortSpectralMatrix {n : ℕ} (a impact : ℝ) (q rate : Fin n → ℝ) :
    Matrix (Option (Fin n)) (Option (Fin n)) ℝ :=
  Matrix.diagonal (cohortSpectralResidual rate) +
    Matrix.vecMulVec (cohortSpectralVector a impact q rate) (cohortSpectralVector a impact q rate)

theorem actual_spectral_matrix_positive {n : ℕ} (a impact : ℝ) (q rate : Fin n → ℝ)
    (hr : ∀ i, rate i ≤ 1) : (cohortSpectralMatrix a impact q rate).PosSemidef := by
  have hd : 0 ≤ cohortSpectralResidual rate := by
    intro i
    cases i with
    | none => simp [cohortSpectralResidual]
    | some j => simpa [cohortSpectralResidual] using hr j
  exact (Matrix.PosSemidef.diagonal hd).add
    (by simpa using Matrix.posSemidef_vecMulVec_self_star (cohortSpectralVector a impact q rate))

theorem actual_spectral_matrix_gap {n : ℕ} (a impact : ℝ) (q rate : Fin n → ℝ)
    (ha : 0 ≤ a) (hk : 0 ≤ impact) (hq : ∀ i, 0 ≤ q i)
    (hr : ∀ i, 0 < rate i) (hf : a + impact * ∑ i, q i < 1) :
    (1 - cohortSpectralMatrix a impact q rate).PosDef := by
  let d : Option (Fin n) → ℝ := fun i => i.elim 1 rate
  have hd : ∀ i, 0 < d i := by
    intro i
    cases i <;> simp [d, hr]
  have hs (i : Fin n) : (Real.sqrt (impact * q i / rate i)) ^ 2 =
      impact * q i / rate i := Real.sq_sqrt (div_nonneg (mul_nonneg hk (hq i)) (le_of_lt (hr i)))
  have hsum : (∑ i, cohortSpectralVector a impact q rate i ^ 2 / d i) =
      a + impact * ∑ i, q i := by
    simp only [Fintype.sum_option, cohortSpectralVector, Option.elim_none,
      Option.elim_some, d, div_one, Real.sq_sqrt ha]
    rw [Finset.mul_sum]
    congr 1
    apply Finset.sum_congr rfl
    intro i hi
    rw [mul_pow, hs]
    field_simp [ne_of_gt (hr i)]
    <;> ring
  have heq : (1 - cohortSpectralMatrix a impact q rate) =
      Matrix.diagonal d - Matrix.vecMulVec (cohortSpectralVector a impact q rate)
        (cohortSpectralVector a impact q rate) := by
    ext i j
    simp only [cohortSpectralMatrix, Matrix.sub_apply, Matrix.add_apply,
      Matrix.one_apply, Matrix.diagonal_apply]
    split_ifs with hij
    · subst j
      cases i <;> simp [d, cohortSpectralResidual] <;> ring
    · simp
  rw [heq]
  exact diagonal_minus_rank_one_posDef d _ hd (by rw [hsum]; exact hf)

theorem actual_spectral_weighted_dot {n : ℕ} (a impact : ℝ) (q rate : Fin n → ℝ)
    (z : Option (Fin n) → ℝ) (ha : 0 ≤ a) (hk : 0 ≤ impact)
    (hq : ∀ i, 0 ≤ q i) (hr : ∀ i, 0 < rate i) :
    (∑ i, cohortSpectralVector a impact q rate i *
      (cohortSpectralScale a impact q rate i * z i)) =
      a * z none + impact * ∑ j, q j * z (some j) := by
  have hs (j : Fin n) : rate j * (Real.sqrt (impact * q j / rate j)) ^ 2 = impact * q j := by
    rw [Real.sq_sqrt (div_nonneg (mul_nonneg hk (hq j)) (le_of_lt (hr j)))]
    exact mul_div_cancel₀ _ (ne_of_gt (hr j))
  simp only [Fintype.sum_option, cohortSpectralVector, cohortSpectralScale,
    Option.elim_none, Option.elim_some]
  have hprice : Real.sqrt a * (Real.sqrt a * z none) = a * z none := by
    calc
      _ = (Real.sqrt a) ^ 2 * z none := by ring
      _ = a * z none := by rw [Real.sq_sqrt ha]
  rw [hprice, Finset.mul_sum]
  congr 1
  apply Finset.sum_congr rfl
  intro j hj
  calc
    _ = (rate j * (Real.sqrt (impact * q j / rate j)) ^ 2) * z (some j) := by ring
    _ = _ := by rw [hs j]; ring

theorem actual_cohort_symmetric_intertwining {n : ℕ} (a impact : ℝ)
    (q rate : Fin n → ℝ) (z : Option (Fin n) → ℝ)
    (ha : 0 ≤ a) (hk : 0 ≤ impact) (hq : ∀ i, 0 ≤ q i) (hr : ∀ i, 0 < rate i) :
    (fun i => cohortSpectralScale a impact q rate i *
      cohortLinearTransition a impact q rate z i) =
    cohortSpectralMatrix a impact q rate *ᵥ
      (fun i => cohortSpectralScale a impact q rate i * z i) := by
  have hv (i : Option (Fin n)) : (Matrix.vecMulVec
      (cohortSpectralVector a impact q rate) (cohortSpectralVector a impact q rate) *ᵥ
      (fun j => cohortSpectralScale a impact q rate j * z j)) i =
      cohortSpectralVector a impact q rate i *
        (a * z none + impact * ∑ j, q j * z (some j)) := by
    calc
      _ = cohortSpectralVector a impact q rate i * (∑ j,
          cohortSpectralVector a impact q rate j *
            (cohortSpectralScale a impact q rate j * z j)) := by
        simp only [Matrix.mulVec, Matrix.vecMulVec, dotProduct]
        rw [Finset.mul_sum]
        apply Finset.sum_congr rfl
        intro j hj
        simp only [Matrix.of_apply]
        ring
      _ = _ := by rw [actual_spectral_weighted_dot a impact q rate z ha hk hq hr]
  funext i
  simp only [cohortSpectralMatrix, Matrix.add_mulVec, Pi.add_apply,
    Matrix.mulVec_diagonal, hv]
  cases i <;> simp [cohortLinearTransition, cohortSpectralScale,
    cohortSpectralResidual, cohortSpectralVector] <;> ring

theorem actual_spectral_input_vector {n : ℕ} (a impact : ℝ) (q rate : Fin n → ℝ) :
    (fun i => cohortSpectralScale a impact q rate i * cohortInputVector impact rate i) =
      impact • cohortSpectralVector a impact q rate := by
  funext i
  cases i <;> simp [cohortSpectralScale, cohortSpectralVector, cohortInputVector] <;> ring

theorem actual_spectral_first_column {n : ℕ} (a impact : ℝ) (q rate : Fin n → ℝ) :
    cohortSpectralMatrix a impact q rate *ᵥ Pi.single none 1 =
      Real.sqrt a • cohortSpectralVector a impact q rate := by
  ext i
  simp only [cohortSpectralMatrix, Matrix.add_mulVec, Pi.add_apply,
    Matrix.mulVec_diagonal, Matrix.mulVec_single_one]
  cases i <;> simp [cohortSpectralResidual, cohortSpectralVector, Matrix.vecMulVec] <;> ring

theorem actual_spectral_powers_intertwining {n : ℕ} (a impact : ℝ)
    (q rate : Fin n → ℝ) (z : Option (Fin n) → ℝ) (t : ℕ)
    (ha : 0 ≤ a) (hk : 0 ≤ impact) (hq : ∀ i, 0 ≤ q i) (hr : ∀ i, 0 < rate i) :
    (fun i => cohortSpectralScale a impact q rate i *
      ((cohortLinearTransition a impact q rate ^ t) z) i) =
    (cohortSpectralMatrix a impact q rate ^ t) *ᵥ
      (fun i => cohortSpectralScale a impact q rate i * z i) := by
  induction t with
  | zero => simp
  | succ t ih =>
    rw [pow_succ', pow_succ', ← Matrix.mulVec_mulVec]
    change (fun i => cohortSpectralScale a impact q rate i *
      cohortLinearTransition a impact q rate ((cohortLinearTransition a impact q rate ^ t) z) i) = _
    rw [actual_cohort_symmetric_intertwining a impact q rate _ ha hk hq hr, ih]

theorem hermitian_diagonal_power {ι : Type*} [Fintype ι] [DecidableEq ι]
    (A : Matrix ι ι ℝ) (hA : A.IsHermitian) (j : ι) (t : ℕ) :
    (A ^ t) j j = ∑ i, (hA.eigenvectorUnitary j i) ^ 2 * (hA.eigenvalues i) ^ t := by
  have hp : A ^ t = Unitary.conjStarAlgAut ℝ _ hA.eigenvectorUnitary
      (Matrix.diagonal (fun i => (hA.eigenvalues i) ^ t)) := by
    conv_lhs => rw [hA.spectral_theorem]
    rw [← map_pow, Matrix.diagonal_pow]
    rfl
  rw [hp, Unitary.conjStarAlgAut_apply]
  rw [Matrix.mul_apply]
  simp only [Matrix.mul_diagonal, Matrix.star_apply,
    star_trivial, Matrix.conjTranspose_apply]
  apply Finset.sum_congr rfl
  intro i hi
  ring

theorem positive_matrix_eigenvalues_below_one {ι : Type*} [Fintype ι] [DecidableEq ι]
    (A : Matrix ι ι ℝ) (hA : A.PosSemidef) (hgap : (1 - A).PosDef) (i : ι) :
    0 ≤ hA.isHermitian.eigenvalues i ∧ hA.isHermitian.eigenvalues i < 1 := by
  refine ⟨hA.eigenvalues_nonneg i, ?_⟩
  let v := hA.isHermitian.eigenvectorBasis i
  let z : ι → ℝ := fun j => v j
  have hn : ‖v‖ = 1 := hA.isHermitian.eigenvectorBasis.orthonormal.1 i
  have hz : z ≠ 0 := by
    intro heq
    have hv : v = 0 := by
      apply PiLp.ext
      intro j
      change z j = 0
      rw [heq]
      rfl
    rw [hv, norm_zero] at hn
    norm_num at hn
  have hdot : z ⬝ᵥ z = 1 := by
    have hh : inner ℝ v v = ‖v‖ ^ 2 := real_inner_self_eq_norm_sq v
    rw [EuclideanSpace.inner_eq_star_dotProduct] at hh
    simpa [z, hn, star_trivial] using hh
  have heig : A *ᵥ z = (hA.isHermitian.eigenvalues i) • z :=
    hA.isHermitian.mulVec_eigenvectorBasis i
  have hp := hgap.dotProduct_mulVec_pos hz
  rw [Matrix.sub_mulVec, Matrix.one_mulVec, dotProduct_sub, heig] at hp
  have hh : 0 < 1 - hA.isHermitian.eigenvalues i := by
    simpa [star_trivial, dotProduct_smul, hdot] using hp
  linarith

theorem actual_positive_anchor_impulse_moment {n : ℕ} (a impact : ℝ)
    (q rate : Fin n → ℝ) (t : ℕ) (ha : 0 < a) (hk : 0 ≤ impact)
    (hq : ∀ i, 0 ≤ q i) (hr : ∀ i, 0 < rate i) :
    actualCohortImpulse a impact q rate t = impact / a *
      (cohortSpectralMatrix a impact q rate ^ (t + 1)) none none := by
  let S := cohortSpectralMatrix a impact q rate
  let u := cohortSpectralVector a impact q rate
  have hpow := actual_spectral_powers_intertwining a impact q rate
    (cohortInputVector impact rate) t (le_of_lt ha) hk hq hr
  rw [actual_spectral_input_vector, Matrix.mulVec_smul] at hpow
  have hobs := congrFun hpow none
  change Real.sqrt a * actualCohortImpulse a impact q rate t =
    impact * (S ^ t *ᵥ u) none at hobs
  have hcolumn : (S ^ (t + 1)) none none = Real.sqrt a * (S ^ t *ᵥ u) none := by
    have hs := actual_spectral_first_column a impact q rate
    have hh : S ^ (t + 1) *ᵥ Pi.single none 1 =
        Real.sqrt a • (S ^ t *ᵥ u) := by
      rw [pow_succ, ← Matrix.mulVec_mulVec, hs, Matrix.mulVec_smul]
    have h := congrFun hh none
    simpa only [Matrix.mulVec_single_one, Matrix.col, Matrix.transpose_apply, Pi.smul_apply, smul_eq_mul] using h
  have hsq := Real.sq_sqrt (le_of_lt ha)
  rw [div_mul_eq_mul_div]
  apply (eq_div_iff (ne_of_gt ha)).2
  change actualCohortImpulse a impact q rate t * a =
    impact * (S ^ (t + 1)) none none
  rw [hcolumn]
  calc
    _ = actualCohortImpulse a impact q rate t * (Real.sqrt a) ^ 2 := by rw [hsq]
    _ = Real.sqrt a * (Real.sqrt a * actualCohortImpulse a impact q rate t) := by ring
    _ = _ := by rw [hobs]; ring

theorem actual_positive_anchor_impulse_mixture {n : ℕ} (a impact : ℝ)
    (q rate : Fin n → ℝ) (ha : 0 < a) (hk : 0 ≤ impact)
    (hq : ∀ i, 0 ≤ q i) (hr : ∀ i, 0 < rate i ∧ rate i ≤ 1)
    (hf : a + impact * ∑ i, q i < 1) :
    ∃ (lambda weights : Option (Fin n) → ℝ),
      (∀ i, 0 ≤ lambda i ∧ lambda i < 1) ∧ (∀ i, 0 ≤ weights i) ∧
      (∑ i, weights i) = impact ∧
      ∀ t, actualCohortImpulse a impact q rate t = ∑ i, weights i * lambda i ^ t := by
  let S := cohortSpectralMatrix a impact q rate
  have hpos := actual_spectral_matrix_positive a impact q rate (fun i => (hr i).2)
  let hS : S.IsHermitian := hpos.isHermitian
  let lambda := hS.eigenvalues
  let weights := fun i => impact / a * lambda i * (hS.eigenvectorUnitary none i) ^ 2
  have hl (i) : 0 ≤ lambda i ∧ lambda i < 1 :=
    positive_matrix_eigenvalues_below_one S hpos
      (actual_spectral_matrix_gap a impact q rate (le_of_lt ha) hk hq
        (fun i => (hr i).1) hf) i
  have hw (i) : 0 ≤ weights i := mul_nonneg
    (mul_nonneg (div_nonneg hk (le_of_lt ha)) (hl i).1) (sq_nonneg _)
  have hrep (t : ℕ) : actualCohortImpulse a impact q rate t =
      ∑ i, weights i * lambda i ^ t := by
    rw [actual_positive_anchor_impulse_moment a impact q rate t ha hk hq (fun i => (hr i).1)]
    rw [hermitian_diagonal_power S hS none (t + 1), Finset.mul_sum]
    apply Finset.sum_congr rfl
    intro i hi
    dsimp only [weights, lambda]
    rw [pow_succ]
    ring
  refine ⟨lambda, weights, hl, hw, ?_, hrep⟩
  have hzero := hrep 0
  simpa [actualCohortImpulse, cohortInputVector] using hzero.symm

theorem actual_positive_anchor_impulse_antitone {n : ℕ} (a impact : ℝ)
    (q rate : Fin n → ℝ) (ha : 0 < a) (hk : 0 ≤ impact)
    (hq : ∀ i, 0 ≤ q i) (hr : ∀ i, 0 < rate i ∧ rate i ≤ 1)
    (hf : a + impact * ∑ i, q i < 1) : Antitone (actualCohortImpulse a impact q rate) := by
  obtain ⟨lambda, weights, hl, hw, hsum, hrep⟩ :=
    actual_positive_anchor_impulse_mixture a impact q rate ha hk hq hr hf
  apply antitone_nat_of_succ_le
  intro t
  rw [hrep, hrep]
  apply Finset.sum_le_sum
  intro i hi
  rw [pow_succ]
  calc
    weights i * (lambda i ^ t * lambda i) = (weights i * lambda i ^ t) * lambda i := by ring
    _ ≤ weights i * lambda i ^ t := by
      have h := mul_le_mul_of_nonneg_left (le_of_lt (hl i).2)
        (mul_nonneg (hw i) (pow_nonneg (hl i).1 t))
      simpa using h

theorem actual_impulse_continuous_in_anchor {n : ℕ} (impact : ℝ)
    (q rate : Fin n → ℝ) (t : ℕ) : Continuous (fun a : ℝ => actualCohortImpulse a impact q rate t) := by
  have hc : ∀ t, Continuous (fun a : ℝ =>
      (autonomousState a impact q rate (pulse1 a impact q rate 1) t).price) ∧
      ∀ i, Continuous (fun a : ℝ =>
        (autonomousState a impact q rate (pulse1 a impact q rate 1) t).memory i) := by
    intro t
    induction t with
    | zero =>
      constructor
      · simpa [autonomousState, pulse1, cohortStep, zeroState] using
          (continuous_const : Continuous (fun _ : ℝ => impact))
      · intro i
        simpa [autonomousState, pulse1, cohortStep, zeroState] using
          (continuous_const : Continuous (fun _ : ℝ => rate i * impact))
    | succ t ih =>
      have hp : Continuous (fun a : ℝ =>
          a * (autonomousState a impact q rate (pulse1 a impact q rate 1) t).price +
          impact * ∑ i, q i * (autonomousState a impact q rate (pulse1 a impact q rate 1) t).memory i) := by
        exact (continuous_id.mul ih.1).add (continuous_const.mul
          (continuous_finsetSum Finset.univ (fun i _ => continuous_const.mul (ih.2 i))))
      have hp' : Continuous (fun a : ℝ =>
          (autonomousState a impact q rate (pulse1 a impact q rate 1) (t + 1)).price) := by
        simpa only [autonomousState, cohortStep, mul_zero, add_zero] using hp
      refine ⟨hp', ?_⟩
      intro i
      have hm : Continuous (fun a : ℝ =>
          (1 - rate i) * (autonomousState a impact q rate (pulse1 a impact q rate 1) t).memory i +
          rate i * (autonomousState a impact q rate (pulse1 a impact q rate 1) (t + 1)).price) :=
        (continuous_const.mul (ih.2 i)).add (continuous_const.mul hp')
      simpa only [autonomousState, cohortStep] using hm
  simpa only [actual_impulse_matches_physical_pulse] using (hc t).1

theorem actual_nonnegative_anchor_impulse_antitone {n : ℕ} (a impact : ℝ)
    (q rate : Fin n → ℝ) (ha : 0 ≤ a) (hk : 0 ≤ impact)
    (hq : ∀ i, 0 ≤ q i) (hr : ∀ i, 0 < rate i ∧ rate i ≤ 1)
    (hf : a + impact * ∑ i, q i < 1) : Antitone (actualCohortImpulse a impact q rate) := by
  rcases lt_or_eq_of_le ha with hapos | hzero
  · exact actual_positive_anchor_impulse_antitone a impact q rate hapos hk hq hr hf
  · subst a
    intro i j hij
    let eps : ℝ := 1 - impact * ∑ i, q i
    have heps : 0 < eps := by dsimp [eps]; linarith
    have hsub : Set.Ioo (0 : ℝ) eps ⊆
        {x | actualCohortImpulse x impact q rate j ≤ actualCohortImpulse x impact q rate i} := by
      intro x hx
      have hxstable : x + impact * ∑ i, q i < 1 := by
        have hh := hx.2
        dsimp [eps] at hh
        linarith
      exact actual_positive_anchor_impulse_antitone x impact q rate hx.1 hk hq hr hxstable hij
    have hclosed := isClosed_le (actual_impulse_continuous_in_anchor impact q rate j)
      (actual_impulse_continuous_in_anchor impact q rate i)
    have hcl := closure_minimal hsub hclosed
    apply hcl
    rw [closure_Ioo (ne_of_lt heps)]
    exact ⟨le_refl _, le_of_lt heps⟩

theorem physical_cohort_robust_quantity_allowance {n : ℕ} (a B P impact fee margin V : ℝ)
    (q rate : Fin n → ℝ) (ha : 0 ≤ a) (hk : 0 < impact) (hP : 0 < P)
    (hc : 0 ≤ fee) (hm : 0 < margin) (hB : 0 < B) (hV : 0 ≤ V)
    (hq : ∀ i, 0 ≤ q i) (hr : ∀ i, 0 < rate i ∧ rate i ≤ 1)
    (hf : a + impact * ∑ i, q i < 1) :
    robustNonnegativeSequenceMargin B P impact fee margin V (actualCohortImpulse a impact q rate) ↔
      V ≤ robustQuantityCap ((margin + 1 / 2) * impact) (fee + margin * P) B := by
  apply robust_nonnegative_quantity_allowance_iff B P impact fee margin V _ hk hP hc hm hB hV
  · exact actual_nonnegative_anchor_impulse_antitone a impact q rate ha (le_of_lt hk) hq hr hf
  · simp [actualCohortImpulse, cohortInputVector]

theorem actual_positive_anchor_execution_coercive {n : ℕ} (a impact : ℝ)
    (q rate : Fin n → ℝ) (ha : 0 < a) (hk : 0 < impact)
    (hq : ∀ i, 0 ≤ q i) (hr : ∀ i, 0 < rate i ∧ rate i ≤ 1)
    (hf : a + impact * ∑ i, q i < 1) :
    ∃ radius : ℝ, (0 ≤ radius ∧ radius < 1) ∧ ∀ T (v : Fin T → ℝ),
      impact * ((1 - radius) / (1 + radius)) / 2 * probeEnergy v ≤
        quadraticExecutionCost (actualCohortImpulse a impact q rate) v := by
  obtain ⟨lambda, weights, hl, hw, hmass, hrep⟩ :=
    actual_positive_anchor_impulse_mixture a impact q rate ha (le_of_lt hk) hq hr hf
  obtain ⟨i, hi, hmax⟩ := Finset.exists_max_image Finset.univ lambda ⟨none, Finset.mem_univ _⟩
  have heq : actualCohortImpulse a impact q rate = positiveMixtureKernel weights lambda :=
    funext hrep
  refine ⟨lambda i, hl i, ?_⟩
  intro T v
  rw [heq]
  exact mixture_execution_cost_coercive weights lambda v impact (lambda i) hw
    (fun j => ⟨(hl j).1, hmax j (Finset.mem_univ _)⟩) (hl i).2 hmass

theorem actual_positive_anchor_execution_cost_positive {n T : ℕ} (a impact : ℝ)
    (q rate : Fin n → ℝ) (v : Fin T → ℝ) (ha : 0 < a) (hk : 0 < impact)
    (hq : ∀ i, 0 ≤ q i) (hr : ∀ i, 0 < rate i ∧ rate i ≤ 1)
    (hf : a + impact * ∑ i, q i < 1) (hv : v ≠ fun _ => 0) :
    0 < quadraticExecutionCost (actualCohortImpulse a impact q rate) v := by
  obtain ⟨radius, hrad, hcoerce⟩ :=
    actual_positive_anchor_execution_coercive a impact q rate ha hk hq hr hf
  have hE := probe_energy_positive v hv
  have hrzero := hrad.1
  have hrone := hrad.2
  have hpos : 0 < impact * ((1 - radius) / (1 + radius)) / 2 * probeEnergy v := by positivity
  exact lt_of_lt_of_le hpos (hcoerce T v)

theorem actual_positive_anchor_trader_energy_bound {n : ℕ} (a impact : ℝ)
    (q rate : Fin n → ℝ) (ha : 0 < a) (hk : 0 < impact)
    (hq : ∀ i, 0 ≤ q i) (hr : ∀ i, 0 < rate i ∧ rate i ≤ 1)
    (hf : a + impact * ∑ i, q i < 1) :
    ∃ radius : ℝ, (0 ≤ radius ∧ radius < 1) ∧ ∀ T (v : Fin T → ℝ) (B P fee : ℝ),
      0 ≤ fee →
      0 ≤ equity (traderCashAfter B P impact fee (actualCohortImpulse a impact q rate) v)
        (∑ i, v i) P →
      probeEnergy v ≤ 2 * B / (impact * ((1 - radius) / (1 + radius))) := by
  obtain ⟨lambda, weights, hl, hw, hmass, hrep⟩ :=
    actual_positive_anchor_impulse_mixture a impact q rate ha (le_of_lt hk) hq hr hf
  obtain ⟨i, hi, hmax⟩ := Finset.exists_max_image Finset.univ lambda ⟨none, Finset.mem_univ _⟩
  have heq : actualCohortImpulse a impact q rate = positiveMixtureKernel weights lambda := funext hrep
  refine ⟨lambda i, hl i, ?_⟩
  intro T v B P fee hfee hsolvent
  rw [heq] at hsolvent
  exact mixture_trader_solvency_energy weights lambda v B P impact fee (lambda i) hw
    (fun j => ⟨(hl j).1, hmax j (Finset.mem_univ _)⟩) (hl i).1 (hl i).2 hmass hk hfee hsolvent

theorem actual_positive_anchor_impulse_dissipates {n : ℕ} (a impact : ℝ)
    (q rate : Fin n → ℝ) (ha : 0 < a) (hk : 0 ≤ impact)
    (hq : ∀ i, 0 ≤ q i) (hr : ∀ i, 0 < rate i ∧ rate i ≤ 1)
    (hf : a + impact * ∑ i, q i < 1) :
    Filter.Tendsto (actualCohortImpulse a impact q rate) Filter.atTop (nhds 0) := by
  obtain ⟨lambda, weights, hl, hw, hmass, hrep⟩ :=
    actual_positive_anchor_impulse_mixture a impact q rate ha hk hq hr hf
  have ht (i) : Filter.Tendsto (fun t : ℕ => weights i * lambda i ^ t)
      Filter.atTop (nhds (weights i * 0)) :=
    (tendsto_pow_atTop_nhds_zero_of_lt_one (hl i).1 (hl i).2).const_mul (weights i)
  have hfun : actualCohortImpulse a impact q rate = (fun t => ∑ i, weights i * lambda i ^ t) := funext hrep
  rw [hfun]
  simpa only [mul_zero, Finset.sum_const_zero] using tendsto_finsetSum Finset.univ (fun i _ => ht i)

end
end CurrentMM
