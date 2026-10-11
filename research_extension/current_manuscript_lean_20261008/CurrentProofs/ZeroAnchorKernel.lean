import CurrentProofs.SpectralCohorts
import Mathlib.Topology.Instances.Real.Lemmas

namespace CurrentMM
noncomputable section
open scoped BigOperators Matrix

theorem hermitian_entry_power {ι : Type*} [Fintype ι] [DecidableEq ι]
    (A : Matrix ι ι ℝ) (hA : A.IsHermitian) (j k : ι) (t : ℕ) :
    (A ^ t) j k = ∑ i, hA.eigenvectorUnitary j i * hA.eigenvectorUnitary k i * hA.eigenvalues i ^ t := by
  have hp : A ^ t = Unitary.conjStarAlgAut ℝ _ hA.eigenvectorUnitary
      (Matrix.diagonal (fun i => hA.eigenvalues i ^ t)) := by
    conv_lhs => rw [hA.spectral_theorem]
    rw [← map_pow, Matrix.diagonal_pow]
    rfl
  rw [hp, Unitary.conjStarAlgAut_apply, Matrix.mul_apply]
  simp only [Matrix.mul_diagonal, Matrix.star_apply, star_trivial]
  apply Finset.sum_congr rfl
  intro i hi
  ring

theorem positive_matrix_powers_dissipate {ι : Type*} [Fintype ι] [DecidableEq ι]
    (A : Matrix ι ι ℝ) (hA : A.PosSemidef) (hgap : (1 - A).PosDef) (j k : ι) :
    Filter.Tendsto (fun t : ℕ => (A ^ t) j k) Filter.atTop (nhds 0) := by
  have hl := positive_matrix_eigenvalues_below_one A hA hgap
  have ht (i) : Filter.Tendsto (fun t : ℕ => hA.isHermitian.eigenvectorUnitary j i *
      hA.isHermitian.eigenvectorUnitary k i * hA.isHermitian.eigenvalues i ^ t)
      Filter.atTop (nhds 0) := by
    simpa using (tendsto_pow_atTop_nhds_zero_of_lt_one (hl i).1 (hl i).2).const_mul
      (hA.isHermitian.eigenvectorUnitary j i * hA.isHermitian.eigenvectorUnitary k i)
  have heq : (fun t : ℕ => (A ^ t) j k) = (fun t => ∑ i,
      hA.isHermitian.eigenvectorUnitary j i * hA.isHermitian.eigenvectorUnitary k i *
        hA.isHermitian.eigenvalues i ^ t) := funext (hermitian_entry_power A hA.isHermitian j k)
  rw [heq]
  simpa only [Finset.sum_const_zero] using tendsto_finsetSum Finset.univ (fun i _ => ht i)

theorem actual_zero_anchor_impulse_successor {n : ℕ} (impact : ℝ) (q rate : Fin n → ℝ)
    (t : ℕ) (hk : 0 ≤ impact) (hq : ∀ i, 0 ≤ q i) (hr : ∀ i, 0 < rate i) :
    actualCohortImpulse 0 impact q rate (t + 1) = impact * ∑ i, ∑ j,
      cohortSpectralVector 0 impact q rate i *
        (cohortSpectralMatrix 0 impact q rate ^ t) i j * cohortSpectralVector 0 impact q rate j := by
  let z := (cohortLinearTransition 0 impact q rate ^ t) (cohortInputVector impact rate)
  have hobs : (cohortLinearTransition 0 impact q rate z) none =
      ∑ i, cohortSpectralVector 0 impact q rate i * (cohortSpectralScale 0 impact q rate i * z i) := by
    simpa [cohortLinearTransition] using
      (actual_spectral_weighted_dot 0 impact q rate z (le_refl _) hk hq hr).symm
  have hp := actual_spectral_powers_intertwining 0 impact q rate (cohortInputVector impact rate)
    t (le_refl _) hk hq hr
  rw [actual_spectral_input_vector, Matrix.mulVec_smul] at hp
  rw [actualCohortImpulse, pow_succ', Module.End.mul_apply]
  change (cohortLinearTransition 0 impact q rate z) none = _
  rw [hobs]
  have hh := congrArg (fun w : Option (Fin n) → ℝ =>
    ∑ i, cohortSpectralVector 0 impact q rate i * w i) hp
  simpa only [Matrix.mulVec, dotProduct, Finset.mul_sum, Pi.smul_apply, smul_eq_mul,
    mul_assoc, mul_left_comm, mul_comm, z] using hh

theorem actual_zero_anchor_impulse_dissipates {n : ℕ} (impact : ℝ) (q rate : Fin n → ℝ)
    (hk : 0 ≤ impact) (hq : ∀ i, 0 ≤ q i) (hr : ∀ i, 0 < rate i ∧ rate i ≤ 1)
    (hf : impact * ∑ i, q i < 1) :
    Filter.Tendsto (actualCohortImpulse 0 impact q rate) Filter.atTop (nhds 0) := by
  let S := cohortSpectralMatrix 0 impact q rate
  let u := cohortSpectralVector 0 impact q rate
  have hpos := actual_spectral_matrix_positive 0 impact q rate (fun i => (hr i).2)
  have hgap := actual_spectral_matrix_gap 0 impact q rate (le_refl _) hk hq
    (fun i => (hr i).1) (by simpa using hf)
  have ht (i j) : Filter.Tendsto (fun t : ℕ => u i * (S ^ t) i j * u j)
      Filter.atTop (nhds 0) := by
    simpa using ((positive_matrix_powers_dissipate S hpos hgap i j).const_mul (u i)).mul_const (u j)
  have hrow (i) := tendsto_finsetSum Finset.univ (fun j _ => ht i j)
  have hall := (tendsto_finsetSum Finset.univ (fun i _ => hrow i)).const_mul impact
  apply (Filter.tendsto_add_atTop_iff_nat 1).1
  have heq : (fun t : ℕ => actualCohortImpulse 0 impact q rate (t + 1)) =
      (fun t => impact * ∑ i, ∑ j, u i * (S ^ t) i j * u j) :=
    funext (fun t => actual_zero_anchor_impulse_successor impact q rate t hk hq (fun i => (hr i).1))
  rw [heq]
  simpa only [Finset.sum_const_zero, mul_zero] using hall

def compactMixtureParameters {ι : Type*} [Fintype ι] (impact : ℝ) :
    Set ((ι → ℝ) × (ι → ℝ)) :=
  (Set.Icc 0 (fun _ => 1) ×ˢ Set.Icc 0 (fun _ => impact)) ∩ {p | ∑ i, p.2 i = impact}

def mixtureMomentMap {ι : Type*} [Fintype ι] (p : (ι → ℝ) × (ι → ℝ)) : ℕ → ℝ :=
  fun t => ∑ i, p.2 i * p.1 i ^ t

theorem mixture_parameter_set_compact {ι : Type*} [Fintype ι] (impact : ℝ) :
    IsCompact (compactMixtureParameters (ι := ι) impact) := by
  have hsum : Continuous (fun p : (ι → ℝ) × (ι → ℝ) => ∑ i, p.2 i) :=
    continuous_finsetSum Finset.univ (fun i _ => (continuous_apply i).comp continuous_snd)
  exact (isCompact_Icc.prod isCompact_Icc).inter_right (isClosed_eq hsum continuous_const)

theorem mixture_moment_map_continuous {ι : Type*} [Fintype ι] :
    Continuous (mixtureMomentMap (ι := ι)) := by
  apply continuous_pi
  intro t
  exact continuous_finsetSum Finset.univ (fun i _ =>
    ((continuous_apply i).comp continuous_snd).mul (((continuous_apply i).comp continuous_fst).pow t))

theorem actual_zero_anchor_weak_mixture {n : ℕ} (impact : ℝ) (q rate : Fin n → ℝ)
    (hk : 0 ≤ impact) (hq : ∀ i, 0 ≤ q i) (hr : ∀ i, 0 < rate i ∧ rate i ≤ 1)
    (hf : impact * ∑ i, q i < 1) :
    ∃ (lambda weights : Option (Fin n) → ℝ),
      (∀ i, 0 ≤ lambda i ∧ lambda i ≤ 1) ∧ (∀ i, 0 ≤ weights i) ∧
      (∑ i, weights i) = impact ∧
      ∀ t, actualCohortImpulse 0 impact q rate t = ∑ i, weights i * lambda i ^ t := by
  let parameters := compactMixtureParameters (ι := Option (Fin n)) impact
  let image := mixtureMomentMap '' parameters
  have hclosed : IsClosed image :=
    ((mixture_parameter_set_compact impact).image mixture_moment_map_continuous).isClosed
  have hanchor : Continuous (fun a : ℝ => actualCohortImpulse a impact q rate) :=
    continuous_pi (fun t => actual_impulse_continuous_in_anchor impact q rate t)
  let eps : ℝ := 1 - impact * ∑ i, q i
  have heps : 0 < eps := by dsimp [eps]; linarith
  have hsub : Set.Ioo (0 : ℝ) eps ⊆ {a | actualCohortImpulse a impact q rate ∈ image} := by
    intro a ha
    have hastable : a + impact * ∑ i, q i < 1 := by
      have hlt := ha.2
      dsimp [eps] at hlt
      linarith
    obtain ⟨lambda, weights, hl, hw, hmass, hrep⟩ :=
      actual_positive_anchor_impulse_mixture a impact q rate ha.1 hk hq hr hastable
    have hwupper (i) : weights i ≤ impact := by
      rw [← hmass]
      exact Finset.single_le_sum (fun j _ => hw j) (Finset.mem_univ _)
    refine ⟨(lambda, weights), ?_, ?_⟩
    · exact ⟨⟨⟨fun i => (hl i).1, fun i => le_of_lt (hl i).2⟩,
        ⟨hw, hwupper⟩⟩, hmass⟩
    · exact funext (fun t => (hrep t).symm)
  have hcl := closure_minimal hsub (hclosed.preimage hanchor)
  have hzero : (0 : ℝ) ∈ closure (Set.Ioo 0 eps) := by
    rw [closure_Ioo (ne_of_lt heps)]
    exact ⟨le_refl _, le_of_lt heps⟩
  obtain ⟨p, hp, heq⟩ := hcl hzero
  refine ⟨p.1, p.2, ?_, hp.1.2.1, hp.2, ?_⟩
  · intro i
    exact ⟨hp.1.1.1 i, hp.1.1.2 i⟩
  · intro t
    exact (congrFun heq t).symm

theorem actual_zero_anchor_impulse_mixture {n : ℕ} (impact : ℝ) (q rate : Fin n → ℝ)
    (hk : 0 ≤ impact) (hq : ∀ i, 0 ≤ q i) (hr : ∀ i, 0 < rate i ∧ rate i ≤ 1)
    (hf : impact * ∑ i, q i < 1) :
    ∃ (lambda weights : Option (Fin n) → ℝ),
      (∀ i, 0 ≤ lambda i ∧ lambda i < 1) ∧ (∀ i, 0 ≤ weights i) ∧
      (∑ i, weights i) = impact ∧
      ∀ t, actualCohortImpulse 0 impact q rate t = ∑ i, weights i * lambda i ^ t := by
  obtain ⟨lambda, weights, hl, hw, hmass, hrep⟩ := actual_zero_anchor_weak_mixture impact q rate hk hq hr hf
  have hlim := actual_zero_anchor_impulse_dissipates impact q rate hk hq hr hf
  have hweight (i) (hi : lambda i = 1) : weights i = 0 := by
    have hlower (t : ℕ) : weights i ≤ actualCohortImpulse 0 impact q rate t := by
      rw [hrep]
      have hs := Finset.single_le_sum (fun j _ => mul_nonneg (hw j) (pow_nonneg (hl j).1 t))
        (Finset.mem_univ i)
      simpa [hi] using hs
    have hn : weights i ≤ 0 := ge_of_tendsto hlim (Filter.Eventually.of_forall hlower)
    exact le_antisymm hn (hw i)
  let clipped : Option (Fin n) → ℝ := fun i => if lambda i < 1 then lambda i else 0
  refine ⟨clipped, weights, ?_, hw, hmass, ?_⟩
  · intro i
    unfold clipped
    split_ifs with hi
    · exact ⟨(hl i).1, hi⟩
    · norm_num
  · intro t
    rw [hrep]
    apply Finset.sum_congr rfl
    intro i hi
    unfold clipped
    split_ifs with hc
    · rfl
    · have hone : lambda i = 1 := by linarith [(hl i).2]
      rw [hweight i hone]
      simp

theorem actual_nonnegative_anchor_impulse_mixture {n : ℕ} (a impact : ℝ) (q rate : Fin n → ℝ)
    (ha : 0 ≤ a) (hk : 0 ≤ impact) (hq : ∀ i, 0 ≤ q i)
    (hr : ∀ i, 0 < rate i ∧ rate i ≤ 1) (hf : a + impact * ∑ i, q i < 1) :
    ∃ (lambda weights : Option (Fin n) → ℝ),
      (∀ i, 0 ≤ lambda i ∧ lambda i < 1) ∧ (∀ i, 0 ≤ weights i) ∧
      (∑ i, weights i) = impact ∧
      ∀ t, actualCohortImpulse a impact q rate t = ∑ i, weights i * lambda i ^ t := by
  rcases lt_or_eq_of_le ha with hapos | hzero
  · exact actual_positive_anchor_impulse_mixture a impact q rate hapos hk hq hr hf
  · subst a
    exact actual_zero_anchor_impulse_mixture impact q rate hk hq hr (by simpa using hf)

def iteratedPriceDifference (h : ℕ → ℝ) : ℕ → ℕ → ℝ
  | 0, t => h t
  | m + 1, t => iteratedPriceDifference h m t - iteratedPriceDifference h m (t + 1)

theorem actual_mixture_difference_formula {ι : Type*} [Fintype ι]
    (weights lambda : ι → ℝ) (m t : ℕ) :
    iteratedPriceDifference (positiveMixtureKernel weights lambda) m t =
      ∑ i, weights i * (1 - lambda i) ^ m * lambda i ^ t := by
  induction m generalizing t with
  | zero => simp [iteratedPriceDifference, positiveMixtureKernel]
  | succ m ih =>
    rw [iteratedPriceDifference, ih, ih, ← Finset.sum_sub_distrib]
    apply Finset.sum_congr rfl
    intro i hi
    rw [pow_succ, pow_succ]
    ring

theorem actual_physical_impulse_completely_monotone {n : ℕ} (a impact : ℝ)
    (q rate : Fin n → ℝ) (ha : 0 ≤ a) (hk : 0 ≤ impact) (hq : ∀ i, 0 ≤ q i)
    (hr : ∀ i, 0 < rate i ∧ rate i ≤ 1) (hf : a + impact * ∑ i, q i < 1) (m t : ℕ) :
    0 ≤ iteratedPriceDifference (actualCohortImpulse a impact q rate) m t := by
  obtain ⟨lambda, weights, hl, hw, hmass, hrep⟩ :=
    actual_nonnegative_anchor_impulse_mixture a impact q rate ha hk hq hr hf
  have heq : actualCohortImpulse a impact q rate = positiveMixtureKernel weights lambda := funext hrep
  rw [heq, actual_mixture_difference_formula]
  apply Finset.sum_nonneg
  intro i hi
  exact mul_nonneg (mul_nonneg (hw i) (pow_nonneg (by linarith [(hl i).2]) m))
    (pow_nonneg (hl i).1 t)

theorem actual_all_anchor_execution_coercive {n : ℕ} (a impact : ℝ)
    (q rate : Fin n → ℝ) (ha : 0 ≤ a) (hk : 0 < impact) (hq : ∀ i, 0 ≤ q i)
    (hr : ∀ i, 0 < rate i ∧ rate i ≤ 1) (hf : a + impact * ∑ i, q i < 1) :
    ∃ radius : ℝ, (0 ≤ radius ∧ radius < 1) ∧ ∀ T (v : Fin T → ℝ),
      impact * ((1 - radius) / (1 + radius)) / 2 * probeEnergy v ≤
        quadraticExecutionCost (actualCohortImpulse a impact q rate) v := by
  obtain ⟨lambda, weights, hl, hw, hmass, hrep⟩ :=
    actual_nonnegative_anchor_impulse_mixture a impact q rate ha (le_of_lt hk) hq hr hf
  obtain ⟨i, hi, hmax⟩ := Finset.exists_max_image Finset.univ lambda ⟨none, Finset.mem_univ _⟩
  have heq : actualCohortImpulse a impact q rate = positiveMixtureKernel weights lambda := funext hrep
  refine ⟨lambda i, hl i, ?_⟩
  intro T v
  rw [heq]
  exact mixture_execution_cost_coercive weights lambda v impact (lambda i) hw
    (fun j => ⟨(hl j).1, hmax j (Finset.mem_univ _)⟩) (hl i).2 hmass

theorem actual_all_anchor_execution_cost_positive {n T : ℕ} (a impact : ℝ)
    (q rate : Fin n → ℝ) (v : Fin T → ℝ) (ha : 0 ≤ a) (hk : 0 < impact)
    (hq : ∀ i, 0 ≤ q i) (hr : ∀ i, 0 < rate i ∧ rate i ≤ 1)
    (hf : a + impact * ∑ i, q i < 1) (hv : v ≠ fun _ => 0) :
    0 < quadraticExecutionCost (actualCohortImpulse a impact q rate) v := by
  obtain ⟨radius, hrad, hcoerce⟩ := actual_all_anchor_execution_coercive a impact q rate ha hk hq hr hf
  have hE := probe_energy_positive v hv
  have hrzero := hrad.1
  have hrone := hrad.2
  have hpos : 0 < impact * ((1 - radius) / (1 + radius)) / 2 * probeEnergy v := by positivity
  exact lt_of_lt_of_le hpos (hcoerce T v)

theorem actual_all_anchor_trader_energy_bound {n : ℕ} (a impact : ℝ)
    (q rate : Fin n → ℝ) (ha : 0 ≤ a) (hk : 0 < impact) (hq : ∀ i, 0 ≤ q i)
    (hr : ∀ i, 0 < rate i ∧ rate i ≤ 1) (hf : a + impact * ∑ i, q i < 1) :
    ∃ radius : ℝ, (0 ≤ radius ∧ radius < 1) ∧ ∀ T (v : Fin T → ℝ) (B P fee : ℝ),
      0 ≤ fee →
      0 ≤ equity (traderCashAfter B P impact fee (actualCohortImpulse a impact q rate) v)
        (∑ i, v i) P →
      probeEnergy v ≤ 2 * B / (impact * ((1 - radius) / (1 + radius))) := by
  obtain ⟨lambda, weights, hl, hw, hmass, hrep⟩ :=
    actual_nonnegative_anchor_impulse_mixture a impact q rate ha (le_of_lt hk) hq hr hf
  obtain ⟨i, hi, hmax⟩ := Finset.exists_max_image Finset.univ lambda ⟨none, Finset.mem_univ _⟩
  have heq : actualCohortImpulse a impact q rate = positiveMixtureKernel weights lambda := funext hrep
  refine ⟨lambda i, hl i, ?_⟩
  intro T v B P fee hfee hsolvent
  rw [heq] at hsolvent
  exact mixture_trader_solvency_energy weights lambda v B P impact fee (lambda i) hw
    (fun j => ⟨(hl j).1, hmax j (Finset.mem_univ _)⟩) (hl i).1 (hl i).2 hmass hk hfee hsolvent

end
end CurrentMM
