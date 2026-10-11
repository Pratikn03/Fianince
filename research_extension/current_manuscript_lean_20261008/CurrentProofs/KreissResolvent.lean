import CurrentProofs.KreissRadius
import Mathlib.Analysis.SpecialFunctions.Exp

/-!
# Theorem 2.14, Part 2 (Kreiss lower bound) and the conditional bilateral radius

Complex `n × n` matrices with the Euclidean operator norm.  The Kreiss lower bound
`K(J) ≤ sup_t ‖J^t‖` is proved from the Neumann series.  Spijker's (1991) upper bound
`sup_t ‖J^t‖ ≤ e n K(J)` is a cited external theorem: it is NOT proved here and it is NOT an
axiom; the bilateral corollary takes it as the explicit hypothesis `hSpijker`.
-/

open scoped Matrix.Norms.L2Operator
open Matrix Filter Topology

namespace CurrentMM
noncomputable section

variable {n : ℕ}

lemma scaled_pow_norm_le (J : Matrix (Fin n) (Fin n) ℂ) (M : ℝ) (hM : ∀ t : ℕ, ‖J ^ t‖ ≤ M)
    (z : ℂ) (t : ℕ) : ‖(z⁻¹ • J) ^ t‖ ≤ M * ‖z‖⁻¹ ^ t := by
  rw [smul_pow, norm_smul, norm_pow, norm_inv, mul_comm]
  exact mul_le_mul_of_nonneg_right (hM t) (by positivity)

/-- The Neumann series `∑ (z⁻¹ J)^t` of a power-bounded matrix converges for `|z| > 1`. -/
theorem kreiss_neumann_hasSum (J : Matrix (Fin n) (Fin n) ℂ) (M : ℝ)
    (hM : ∀ t : ℕ, ‖J ^ t‖ ≤ M) (z : ℂ) (hz : 1 < ‖z‖) :
    HasSum (fun t : ℕ => (z⁻¹ • J) ^ t) (∑' t : ℕ, (z⁻¹ • J) ^ t) := by
  have hq0 : 0 ≤ ‖z‖⁻¹ := by positivity
  have hq1 : ‖z‖⁻¹ < 1 := inv_lt_one_of_one_lt₀ hz
  exact (Summable.of_norm_bounded ((summable_geometric_of_lt_one hq0 hq1).mul_left M)
    (scaled_pow_norm_le J M hM z)).hasSum

/-- Telescoping identities for the Neumann series: `(1 - x) S = 1` and `S (1 - x) = 1`
with `x = z⁻¹ J`. -/
theorem kreiss_neumann_inverse (J : Matrix (Fin n) (Fin n) ℂ) (M : ℝ)
    (hM : ∀ t : ℕ, ‖J ^ t‖ ≤ M) (z : ℂ) (hz : 1 < ‖z‖) :
    (1 - z⁻¹ • J) * (∑' t : ℕ, (z⁻¹ • J) ^ t) = 1 ∧
      (∑' t : ℕ, (z⁻¹ • J) ^ t) * (1 - z⁻¹ • J) = 1 := by
  set x := z⁻¹ • J with hx
  set S := ∑' t : ℕ, x ^ t with hS
  have hsum := kreiss_neumann_hasSum J M hM z hz
  have hpart : Tendsto (fun N : ℕ => ∑ i ∈ Finset.range N, x ^ i) atTop (𝓝 S) :=
    hsum.tendsto_sum_nat
  have hq0 : 0 ≤ ‖z‖⁻¹ := by positivity
  have hq1 : ‖z‖⁻¹ < 1 := inv_lt_one_of_one_lt₀ hz
  have hpow : Tendsto (fun N : ℕ => x ^ N) atTop (𝓝 0) := by
    apply squeeze_zero_norm (scaled_pow_norm_le J M hM z)
    simpa using (tendsto_pow_atTop_nhds_zero_of_lt_one hq0 hq1).const_mul M
  have hone : Tendsto (fun N : ℕ => (1 : Matrix (Fin n) (Fin n) ℂ) - x ^ N) atTop (𝓝 1) := by
    simpa using (tendsto_const_nhds (x := (1 : Matrix (Fin n) (Fin n) ℂ))).sub hpow
  constructor
  · have hlim : Tendsto (fun N : ℕ => (1 - x) * ∑ i ∈ Finset.range N, x ^ i) atTop
        (𝓝 ((1 - x) * S)) := hpart.const_mul (1 - x)
    simp only [mul_neg_geom_sum] at hlim
    exact tendsto_nhds_unique hlim hone
  · have hlim : Tendsto (fun N : ℕ => (∑ i ∈ Finset.range N, x ^ i) * (1 - x)) atTop
        (𝓝 (S * (1 - x))) := hpart.mul_const (1 - x)
    simp only [geom_sum_mul_neg] at hlim
    exact tendsto_nhds_unique hlim hone

lemma resolvent_factor (J : Matrix (Fin n) (Fin n) ℂ) (z : ℂ) (hz0 : z ≠ 0) :
    z • (1 : Matrix (Fin n) (Fin n) ℂ) - J = z • (1 - z⁻¹ • J) := by
  rw [smul_sub, smul_smul, mul_inv_cancel₀ hz0, one_smul]

/-- The resolvent of a power-bounded matrix outside the closed unit disk is the scaled
Neumann series, and `zI - J` is invertible. -/
theorem kreiss_resolvent_eq (J : Matrix (Fin n) (Fin n) ℂ) (M : ℝ)
    (hM : ∀ t : ℕ, ‖J ^ t‖ ≤ M) (z : ℂ) (hz : 1 < ‖z‖) :
    (z • (1 : Matrix (Fin n) (Fin n) ℂ) - J) * (z⁻¹ • ∑' t : ℕ, (z⁻¹ • J) ^ t) = 1 ∧
      (z⁻¹ • ∑' t : ℕ, (z⁻¹ • J) ^ t) * (z • (1 : Matrix (Fin n) (Fin n) ℂ) - J) = 1 ∧
      (z • (1 : Matrix (Fin n) (Fin n) ℂ) - J)⁻¹ = z⁻¹ • ∑' t : ℕ, (z⁻¹ • J) ^ t := by
  have hz0 : z ≠ 0 := by
    intro h
    rw [h, norm_zero] at hz
    linarith
  obtain ⟨h1, h2⟩ := kreiss_neumann_inverse J M hM z hz
  have hr : (z • (1 : Matrix (Fin n) (Fin n) ℂ) - J) * (z⁻¹ • ∑' t : ℕ, (z⁻¹ • J) ^ t) = 1 := by
    rw [resolvent_factor J z hz0, smul_mul_smul_comm, mul_inv_cancel₀ hz0, h1, one_smul]
  have hl : (z⁻¹ • ∑' t : ℕ, (z⁻¹ • J) ^ t) * (z • (1 : Matrix (Fin n) (Fin n) ℂ) - J) = 1 := by
    rw [resolvent_factor J z hz0, smul_mul_smul_comm, inv_mul_cancel₀ hz0, h2, one_smul]
  exact ⟨hr, hl, Matrix.inv_eq_right_inv hr⟩

theorem kreiss_resolvent_isUnit (J : Matrix (Fin n) (Fin n) ℂ) (M : ℝ)
    (hM : ∀ t : ℕ, ‖J ^ t‖ ≤ M) (z : ℂ) (hz : 1 < ‖z‖) :
    IsUnit (z • (1 : Matrix (Fin n) (Fin n) ℂ) - J) :=
  ⟨⟨_, _, (kreiss_resolvent_eq J M hM z hz).1, (kreiss_resolvent_eq J M hM z hz).2.1⟩, rfl⟩

/-- Kreiss lower bound at a point: `(|z| - 1) ‖(zI - J)⁻¹‖ ≤ M` whenever `‖J^t‖ ≤ M` for
all `t` and `|z| > 1`. -/
theorem kreiss_resolvent_lower_bound (J : Matrix (Fin n) (Fin n) ℂ) (M : ℝ)
    (hM : ∀ t : ℕ, ‖J ^ t‖ ≤ M) (z : ℂ) (hz : 1 < ‖z‖) :
    (‖z‖ - 1) * ‖(z • (1 : Matrix (Fin n) (Fin n) ℂ) - J)⁻¹‖ ≤ M := by
  have hq0 : 0 ≤ ‖z‖⁻¹ := by positivity
  have hq1 : ‖z‖⁻¹ < 1 := inv_lt_one_of_one_lt₀ hz
  have hzpos : 0 < ‖z‖ := by linarith
  rw [(kreiss_resolvent_eq J M hM z hz).2.2, norm_smul, norm_inv]
  have hS : ‖∑' t : ℕ, (z⁻¹ • J) ^ t‖ ≤ M * (1 - ‖z‖⁻¹)⁻¹ :=
    tsum_of_norm_bounded ((hasSum_geometric_of_lt_one hq0 hq1).mul_left M)
      (scaled_pow_norm_le J M hM z)
  have hden : 0 < 1 - ‖z‖⁻¹ := by linarith
  have hkey : (‖z‖ - 1) * ‖z‖⁻¹ * (1 - ‖z‖⁻¹)⁻¹ = 1 := by
    have h : 1 - ‖z‖⁻¹ = (‖z‖ - 1) * ‖z‖⁻¹ := by
      rw [sub_mul, mul_inv_cancel₀ hzpos.ne', one_mul]
    rw [h]
    exact mul_inv_cancel₀ (by rw [← h]; exact hden.ne')
  calc (‖z‖ - 1) * (‖z‖⁻¹ * ‖∑' t : ℕ, (z⁻¹ • J) ^ t‖)
      = ((‖z‖ - 1) * ‖z‖⁻¹) * ‖∑' t : ℕ, (z⁻¹ • J) ^ t‖ := by ring
    _ ≤ ((‖z‖ - 1) * ‖z‖⁻¹) * (M * (1 - ‖z‖⁻¹)⁻¹) :=
        mul_le_mul_of_nonneg_left hS (by
          have : 0 ≤ ‖z‖ - 1 := by linarith
          positivity)
    _ = M * ((‖z‖ - 1) * ‖z‖⁻¹ * (1 - ‖z‖⁻¹)⁻¹) := by ring
    _ = M := by rw [hkey, mul_one]

/-- Kreiss constant `K(J) = sup_{|z|>1} (|z| - 1) ‖(zI - J)⁻¹‖₂`. -/
def kreissConstant (J : Matrix (Fin n) (Fin n) ℂ) : ℝ :=
  ⨆ z : {z : ℂ // 1 < ‖z‖}, (‖(z : ℂ)‖ - 1) * ‖((z : ℂ) • (1 : Matrix (Fin n) (Fin n) ℂ) - J)⁻¹‖

/-- Power bound `M_I = sup_t ‖J^t‖₂`. -/
def powerBound (J : Matrix (Fin n) (Fin n) ℂ) : ℝ := ⨆ t : ℕ, ‖J ^ t‖

instance : Nonempty {z : ℂ // 1 < ‖z‖} := ⟨⟨2, by norm_num⟩⟩

/-- Kreiss lower bound `K(J) ≤ sup_t ‖J^t‖₂` for a power-bounded complex matrix. -/
theorem kreissConstant_le_powerBound (J : Matrix (Fin n) (Fin n) ℂ)
    (hbdd : BddAbove (Set.range fun t : ℕ => ‖J ^ t‖)) :
    kreissConstant J ≤ powerBound J :=
  ciSup_le fun z => kreiss_resolvent_lower_bound J (powerBound J)
    (fun t => le_ciSup hbdd t) z z.2

theorem kreiss_values_bddAbove (J : Matrix (Fin n) (Fin n) ℂ)
    (hbdd : BddAbove (Set.range fun t : ℕ => ‖J ^ t‖)) :
    BddAbove (Set.range fun z : {z : ℂ // 1 < ‖z‖} =>
      (‖(z : ℂ)‖ - 1) * ‖((z : ℂ) • (1 : Matrix (Fin n) (Fin n) ℂ) - J)⁻¹‖) := by
  refine ⟨powerBound J, ?_⟩
  rintro _ ⟨z, rfl⟩
  exact kreiss_resolvent_lower_bound J (powerBound J) (fun t => le_ciSup hbdd t) z z.2

theorem powerBound_pos (J : Matrix (Fin n) (Fin n) ℂ) (hn : 0 < n)
    (hbdd : BddAbove (Set.range fun t : ℕ => ‖J ^ t‖)) : 0 < powerBound J := by
  have : Nonempty (Fin n) := ⟨⟨0, hn⟩⟩
  have h0 : ‖J ^ 0‖ ≤ powerBound J := le_ciSup hbdd 0
  rw [pow_zero] at h0
  have : 0 < ‖(1 : Matrix (Fin n) (Fin n) ℂ)‖ := norm_pos_iff.mpr one_ne_zero
  linarith

theorem outputGain_one_eq_powerBound (J : Matrix (Fin n) (Fin n) ℂ) :
    outputGain (1 : Matrix (Fin n) (Fin n) ℂ) J = powerBound J := by
  simp [outputGain, powerBound]

/-- Conditional bilateral radius bound (Theorem 2.14, Part 2, display (eq:kreiss_bilateral_bound)).
Spijker's inequality is an explicit hypothesis `hSpijker` (cited external theorem, not proved,
not an axiom).  Under it, `K(J) > 0` and
`B / (e n K) ≤ r*_exact = B / M_I ≤ B / K`, where `r*_exact` is the exact full-state radius of
Part 1 (the largest admissible radius, `exact_safe_radius_isGreatest` with `C = I`). -/
theorem kreiss_bilateral_radius (J : Matrix (Fin n) (Fin n) ℂ) (hn : 0 < n) (B : ℝ) (hB : 0 < B)
    (hbdd : BddAbove (Set.range fun t : ℕ => ‖J ^ t‖))
    (hSpijker : powerBound J ≤ Real.exp 1 * n * kreissConstant J) :
    0 < kreissConstant J ∧
      B / (Real.exp 1 * n * kreissConstant J) ≤ B / powerBound J ∧
      B / powerBound J ≤ B / kreissConstant J ∧
      IsGreatest {r : ℝ | 0 ≤ r ∧ ∀ z : EuclideanSpace ℂ (Fin n), ‖z‖ ≤ r →
        ∀ t : ℕ, ‖l2Apply ((1 : Matrix (Fin n) (Fin n) ℂ) * J ^ t) z‖ ≤ B} (B / powerBound J) := by
  have hP := powerBound_pos J hn hbdd
  have hen : 0 < Real.exp 1 * n := mul_pos (Real.exp_pos 1) (by exact_mod_cast hn)
  have hK : 0 < kreissConstant J := by
    by_contra h
    rw [not_lt] at h
    have : Real.exp 1 * n * kreissConstant J ≤ 0 :=
      mul_nonpos_of_nonneg_of_nonpos hen.le h
    linarith
  have : Nonempty (Fin n) := ⟨⟨0, hn⟩⟩
  have hbdd1 : BddAbove (Set.range fun t : ℕ => ‖(1 : Matrix (Fin n) (Fin n) ℂ) * J ^ t‖) := by
    simpa using hbdd
  refine ⟨hK, div_le_div_of_nonneg_left hB.le hP hSpijker,
    div_le_div_of_nonneg_left hB.le hK (kreissConstant_le_powerBound J hbdd), ?_⟩
  have := exact_safe_radius_isGreatest (1 : Matrix (Fin n) (Fin n) ℂ) J B hbdd1 one_ne_zero hB
  rwa [outputGain_one_eq_powerBound] at this

end
end CurrentMM
