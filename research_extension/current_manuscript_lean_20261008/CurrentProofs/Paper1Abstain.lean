import CurrentProofs.Paper1GaussianTriangular
import CurrentProofs.Paper1Pinsker
import Mathlib.InformationTheory.KullbackLeibler.DataProcessing

/-!
# Paper 1, Theorem `thm:abstain` (finite-window abstention), end to end

The scalar autoregression `x_t = s x_{t-1} + w_t`, `x_0 = 0`, `w_t ~ N(0, σ²)` i.i.d., observed for `t = 1, …, T`, has
path law `P_s = (L_s)_* N(0, σ² I)` with `L_s` the lower-triangular matrix of entries `s^(i-j)`.

* `p1_arA_mul_arL`: `A_{s₁} L_{s₀}` (with `A_s = 1 - s·shift`) has entries `L_{s₀}(i,j) - s₁ L_{s₀}(i-1,j)`; for
  `s₁ = s₀` it is the identity.
* `p1_ar_path_kl_le`: `KL(P_{s₀} ‖ P_{s₁}) ≤ (s₁ - s₀)² M T(T-1)/4` whenever `s₀^(2k) ≤ M` for `k < T`. The proof maps
  both laws by `A_{s₁}` (data processing, then back by `L_{s₁}`), so the divergence is that of a unit-triangular image
  of i.i.d. Gaussians (`Paper1GaussianTriangular.lean`).
* `p1_thm_abstain`: for every rule with three measurable outcomes (stable, unstable, abstain) whose errors are at
  most `α` on each side of `s = 1`, every `s` in `B_T = (1 - c₀/T, 1 + c₀/T)` has
  `P_s(abstain) ≥ 1 - 2α - c₀ e^{c₀}/(2√2)`. This is the paper's statement, with Pinsker's inequality proved in
  `Paper1Pinsker.lean`.
* `p1_thm_abstain_binary`: for binary rules the worst error over `s ∈ (0, 2)` is at least `1/2 - ε` for every
  `ε > 0`.

Rules are deterministic (measurable sets of paths); a randomized rule is not covered here.
-/

namespace CurrentMM

open MeasureTheory ProbabilityTheory InformationTheory Real Finset Matrix
open scoped ENNReal NNReal

/-- The AR(1) solution matrix: `x_i = ∑_{j ≤ i} s^(i-j) w_j`. -/
noncomputable def arL (n : ℕ) (s : ℝ) : Matrix (Fin n) (Fin n) ℝ :=
  fun i j => if j ≤ i then s ^ (i.val - j.val) else 0

/-- The AR(1) innovation matrix: `w_i = x_i - s x_{i-1}`. -/
noncomputable def arA (n : ℕ) (s : ℝ) : Matrix (Fin n) (Fin n) ℝ :=
  fun i j => if i = j then 1 else if i.val = j.val + 1 then -s else 0

/-- Law of the AR(1) path `x_1, …, x_n` from `x_0 = 0` with innovation variance `v`. -/
noncomputable def arPathLaw (n : ℕ) (s : ℝ) (v : ℝ≥0) : Measure (Fin n → ℝ) :=
  (iidGauss n v).map (arL n s).mulVec

instance (n : ℕ) (s : ℝ) (v : ℝ≥0) : IsProbabilityMeasure (arPathLaw n s v) := by
  unfold arPathLaw
  exact isProbabilityMeasure_map (p1_measurable_mulVec _).aemeasurable

/-- Entries of `A_{s₁} L_{s₀}`. -/
theorem p1_arA_mul_arL (n : ℕ) (s1 s0 : ℝ) (i j : Fin n) :
    (arA n s1 * arL n s0) i j =
      arL n s0 i j - (if 0 < i.val then s1 * arL n s0 ⟨i.val - 1, by have := i.isLt; omega⟩ j else 0) := by
  rw [Matrix.mul_apply]
  have hsplit : ∀ k : Fin n, arA n s1 i k * arL n s0 k j =
      (if i = k then arL n s0 k j else 0) - (if i.val = k.val + 1 then s1 * arL n s0 k j else 0) := by
    intro k
    unfold arA
    by_cases h1 : i = k
    · subst h1; simp
    · by_cases h2 : i.val = k.val + 1
      · simp [h1, h2]
      · simp [h1, h2]
  simp only [hsplit, Finset.sum_sub_distrib, Finset.sum_ite_eq, Finset.mem_univ, ↓reduceIte]
  congr 1
  split_ifs with h
  · rw [Finset.sum_eq_single ⟨i.val - 1, by have := i.isLt; omega⟩]
    · rw [if_pos (show i.val = i.val - 1 + 1 by omega)]
    · intro b _ hb
      have : ¬ (i.val = b.val + 1) := by
        intro hc; apply hb; exact Fin.ext (show b.val = i.val - 1 by omega)
      rw [if_neg this]
    · intro hb; exact absurd (Finset.mem_univ _) hb
  · refine Finset.sum_eq_zero (fun k _ => ?_)
    have : ¬ (i.val = k.val + 1) := by omega
    rw [if_neg this]

/-- `A_s L_s = 1`. -/
/-- Entries of `A_{s₁} L_{s₀} - 1`: `(s₀ - s₁) s₀^(i-1-j)` below the diagonal, `0` elsewhere. -/
theorem p1_arB_sub_one_aux (n : ℕ) (s1 s0 : ℝ) (i j : Fin n) :
    (arA n s1 * arL n s0 - 1) i j = if j < i then (s0 - s1) * s0 ^ (i.val - 1 - j.val) else 0 := by
  rw [Matrix.sub_apply, p1_arA_mul_arL, Matrix.one_apply]
  unfold arL
  by_cases hlt : j < i
  · have hpos : 0 < i.val := lt_of_le_of_lt (Nat.zero_le _) (Fin.lt_def.mp hlt)
    have hji : j ≤ i := le_of_lt hlt
    have hj1 : j ≤ (⟨i.val - 1, by have := i.isLt; omega⟩ : Fin n) := by
      rw [Fin.le_def]; simp; have := Fin.lt_def.mp hlt; omega
    have hne : i ≠ j := fun h => (ne_of_lt hlt) h.symm
    have he : i.val - j.val = (i.val - 1 - j.val) + 1 := by have := Fin.lt_def.mp hlt; omega
    rw [if_pos hji, if_pos hpos, if_pos hj1, if_neg hne, if_pos hlt]
    simp only [Fin.val_mk]
    rw [he, pow_succ]; ring
  · rw [if_neg hlt]
    by_cases heq : i = j
    · subst heq
      by_cases hpos : 0 < i.val
      · have hnle : ¬ (i ≤ (⟨i.val - 1, by have := i.isLt; omega⟩ : Fin n)) := by rw [Fin.le_def]; simp; omega
        simp [hpos, hnle]
      · simp [hpos]
    · have hji : ¬ j ≤ i := by
        intro h; rcases lt_or_eq_of_le h with h' | h'
        · exact hlt h'
        · exact heq h'.symm
      by_cases hpos : 0 < i.val
      · have hnle : ¬ (j ≤ (⟨i.val - 1, by have := i.isLt; omega⟩ : Fin n)) := by
          rw [Fin.le_def]; simp; rw [Fin.le_def] at hji; omega
        simp [hji, hpos, hnle, heq]
      · simp [hji, hpos, heq]

theorem p1_arA_mul_arL_self (n : ℕ) (s : ℝ) : arA n s * arL n s = 1 := by
  ext i j
  have h := p1_arB_sub_one_aux n s s i j
  rw [Matrix.sub_apply] at h
  have e : (if j < i then (s - s) * s ^ (i.val - 1 - j.val) else 0) = 0 := by split_ifs <;> ring
  rw [e] at h
  linarith

theorem p1_arB_lower (n : ℕ) (s1 s0 : ℝ) : (arA n s1 * arL n s0).IsLowerTriangular := by
  intro i j hij'
  have hij : i < j := by simpa using hij'
  have h := p1_arB_sub_one_aux n s1 s0 i j
  have hnlt : ¬ j < i := fun h' => lt_asymm hij h'
  rw [if_neg hnlt, Matrix.sub_apply, Matrix.one_apply, if_neg (ne_of_lt hij)] at h
  simpa using h

theorem p1_arB_diag (n : ℕ) (s1 s0 : ℝ) (i : Fin n) : (arA n s1 * arL n s0) i i = 1 := by
  have h := p1_arB_sub_one_aux n s1 s0 i i
  rw [if_neg (lt_irrefl i), Matrix.sub_apply, Matrix.one_apply, if_pos rfl] at h
  linarith

/-- `∑_{i<n} i = n(n-1)/2`, as reals. -/
theorem p1_sum_range_cast_id (n : ℕ) : (∑ i ∈ range n, (i : ℝ)) * 2 = n * (n - 1) := by
  induction n with
  | zero => simp
  | succ k ih => rw [sum_range_succ, add_mul, ih]; push_cast; ring

/-- **Path divergence of two autoregressions.** If `s₀^(2k) ≤ M` for `k < n`, then
`KL(P_{s₀} ‖ P_{s₁}) ≤ (s₁ - s₀)² M n(n-1)/4`. -/
theorem p1_ar_path_kl_le (n : ℕ) (s0 s1 M : ℝ) (v : ℝ≥0) (hv : v ≠ 0) (hM0 : 0 ≤ M)
    (hM : ∀ k, k < n → s0 ^ (2 * k) ≤ M) :
    klDiv (arPathLaw n s0 v) (arPathLaw n s1 v) ≤
      ENNReal.ofReal ((s1 - s0) ^ 2 * M * (n * (n - 1)) / 4) := by
  set ν := iidGauss n v
  have hmA := p1_measurable_mulVec (arA n s1)
  have hmL0 := p1_measurable_mulVec (arL n s0)
  have hmL1 := p1_measurable_mulVec (arL n s1)
  -- map both laws by `A_{s₁}` and back by `L_{s₁}`
  have hLA : arL n s1 * arA n s1 = 1 := mul_eq_one_comm.mp (p1_arA_mul_arL_self n s1)
  have hback : ∀ μ : Measure (Fin n → ℝ), (μ.map (arA n s1).mulVec).map (arL n s1).mulVec = μ := by
    intro μ
    rw [Measure.map_map hmL1 hmA]
    have : (arL n s1).mulVec ∘ (arA n s1).mulVec = id := by
      funext x; simp [Function.comp, Matrix.mulVec_mulVec, hLA]
    rw [this, Measure.map_id]
  have hstep : klDiv (arPathLaw n s0 v) (arPathLaw n s1 v) ≤
      klDiv ((arPathLaw n s0 v).map (arA n s1).mulVec) ((arPathLaw n s1 v).map (arA n s1).mulVec) := by
    have h := klDiv_map_le ((arPathLaw n s0 v).map (arA n s1).mulVec)
      ((arPathLaw n s1 v).map (arA n s1).mulVec) hmL1
    rwa [hback, hback] at h
  have h0 : (arPathLaw n s0 v).map (arA n s1).mulVec = ν.map (arA n s1 * arL n s0).mulVec := by
    unfold arPathLaw
    rw [Measure.map_map hmA hmL0]
    congr 1; funext x; simp [Function.comp, Matrix.mulVec_mulVec]
  have h1 : (arPathLaw n s1 v).map (arA n s1).mulVec = ν := by
    unfold arPathLaw
    rw [Measure.map_map hmA hmL1]
    have : (arA n s1).mulVec ∘ (arL n s1).mulVec = id := by
      funext x; simp [Function.comp, Matrix.mulVec_mulVec, p1_arA_mul_arL_self]
    rw [this, Measure.map_id]
  rw [h0, h1, p1_kl_triangular_gaussian v hv _ (p1_arB_lower n s1 s0) (p1_arB_diag n s1 s0)] at hstep
  refine hstep.trans (ENNReal.ofReal_le_ofReal ?_)
  -- the sum of squares
  have hentry : ∀ i j : Fin n, (arA n s1 * arL n s0 - 1) i j ^ 2 ≤ if j < i then (s1 - s0) ^ 2 * M else 0 := by
    intro i j
    rw [p1_arB_sub_one_aux]
    split_ifs with h
    · have hk : i.val - 1 - j.val < n := by omega
      have := hM _ hk
      rw [mul_pow, ← pow_mul, mul_comm 2 (i.val - 1 - j.val)]
      have e : (s0 - s1) ^ 2 = (s1 - s0) ^ 2 := by ring
      rw [e, mul_comm (i.val - 1 - j.val) 2]
      exact mul_le_mul_of_nonneg_left this (sq_nonneg _)
    · simp
  have hrow : ∀ i : Fin n, ∑ j : Fin n, (if j < i then (s1 - s0) ^ 2 * M else 0) = (s1 - s0) ^ 2 * M * i.val := by
    intro i
    rw [← Finset.sum_filter, Finset.sum_const, nsmul_eq_mul]
    have hf : (Finset.univ.filter (fun j : Fin n => j < i)) = Finset.Iio i := by ext j; simp
    rw [hf, Fin.card_Iio]; ring
  have htot : ∑ i : Fin n, (s1 - s0) ^ 2 * M * (i.val : ℝ) = (s1 - s0) ^ 2 * M * (n * (n - 1)) / 2 := by
    rw [← Finset.mul_sum, Fin.sum_univ_eq_sum_range (fun i => (i : ℝ)) n]
    have := p1_sum_range_cast_id n
    field_simp
    linarith
  have hsum : ∑ i, ∑ j, (arA n s1 * arL n s0 - 1) i j ^ 2 ≤ (s1 - s0) ^ 2 * M * (n * (n - 1)) / 2 := by
    calc ∑ i, ∑ j, (arA n s1 * arL n s0 - 1) i j ^ 2
        ≤ ∑ i : Fin n, ∑ j : Fin n, (if j < i then (s1 - s0) ^ 2 * M else 0) :=
          Finset.sum_le_sum (fun i _ => Finset.sum_le_sum (fun j _ => hentry i j))
      _ = ∑ i : Fin n, (s1 - s0) ^ 2 * M * (i.val : ℝ) := Finset.sum_congr rfl (fun i _ => hrow i)
      _ = _ := htot
  linarith

/-- `(1 + c/T)^(2k) ≤ e^{2c}` for `k ≤ T`. -/
theorem p1_pow_le_exp (T k : ℕ) (hT : 0 < T) (hk : k ≤ T) (c : ℝ) (hc : 0 ≤ c) (s : ℝ) (hs0 : 0 ≤ s)
    (hs : s ≤ 1 + c / T) : s ^ (2 * k) ≤ exp (2 * c) := by
  have hTpos : (0 : ℝ) < T := by exact_mod_cast hT
  have h1 : s ≤ exp (c / T) := le_trans hs (by have := add_one_le_exp (c / T); linarith)
  have h2 : s ^ (2 * k) ≤ exp (c / T) ^ (2 * k) := pow_le_pow_left₀ hs0 h1 _
  have h3 : exp (c / T) ^ (2 * k) = exp (2 * k * (c / T)) := by
    rw [← exp_nat_mul]; push_cast; ring_nf
  have h4 : 2 * (k : ℝ) * (c / T) ≤ 2 * c := by
    have hkT : (k : ℝ) ≤ T := by exact_mod_cast hk
    rw [mul_div_assoc']
    rw [div_le_iff₀ hTpos]
    nlinarith
  rw [h3] at h2
  exact h2.trans (exp_le_exp.mpr h4)

/-- KL bound on the window `B_T`: for `0 ≤ s₀ ≤ 1 + c₀/T` and `|s₁ - s₀| ≤ c₀/T`,
`KL(P_{s₀} ‖ P_{s₁}) ≤ c₀² e^{2c₀}/4`. -/
theorem p1_ar_window_kl (T : ℕ) (hT : 0 < T) (c0 : ℝ) (hc0 : 0 ≤ c0) (s0 s1 : ℝ) (hs0 : 0 ≤ s0)
    (hs0' : s0 ≤ 1 + c0 / T) (hgap : |s1 - s0| ≤ c0 / T) (v : ℝ≥0) (hv : v ≠ 0) :
    klDiv (arPathLaw T s0 v) (arPathLaw T s1 v) ≤ ENNReal.ofReal (c0 ^ 2 * exp (2 * c0) / 4) := by
  have hTpos : (0 : ℝ) < T := by exact_mod_cast hT
  refine (p1_ar_path_kl_le T s0 s1 (exp (2 * c0)) v hv (exp_pos _).le
    (fun k hk => p1_pow_le_exp T k hT hk.le c0 hc0 s0 hs0 hs0')).trans (ENNReal.ofReal_le_ofReal ?_)
  have hsq : (s1 - s0) ^ 2 ≤ (c0 / T) ^ 2 := by
    rw [← sq_abs]; exact pow_le_pow_left₀ (abs_nonneg _) hgap 2
  have hTT : (T : ℝ) * (T - 1) ≤ T ^ 2 := by nlinarith
  have hTT0 : 0 ≤ (T : ℝ) * (T - 1) := by
    have : (1 : ℝ) ≤ T := by exact_mod_cast hT
    nlinarith
  have he : 0 ≤ exp (2 * c0) := (exp_pos _).le
  calc (s1 - s0) ^ 2 * exp (2 * c0) * (T * (T - 1)) / 4
      ≤ (c0 / T) ^ 2 * exp (2 * c0) * (T ^ 2) / 4 := by gcongr
    _ = c0 ^ 2 * exp (2 * c0) / 4 := by field_simp

/-- Pinsker for one event with a real divergence budget. -/
theorem p1_event_gap_le {α : Type*} [MeasurableSpace α] (P Q : Measure α) [IsProbabilityMeasure P]
    [IsProbabilityMeasure Q] {A : Set α} (hA : MeasurableSet A) (c : ℝ) (hc : 0 ≤ c)
    (hkl : klDiv P Q ≤ ENNReal.ofReal c) : |P.real A - Q.real A| ≤ sqrt (c / 2) := by
  have hpin := (p1_set_pinsker P Q hA).trans hkl
  rw [ENNReal.ofReal_le_ofReal_iff hc] at hpin
  rw [← sqrt_sq_eq_abs]
  exact sqrt_le_sqrt (by linarith)

theorem p1_sqrt_window (c0 : ℝ) (hc0 : 0 ≤ c0) :
    sqrt (c0 ^ 2 * exp (2 * c0) / 4 / 2) = c0 * exp c0 / (2 * sqrt 2) := by
  have h2 : (0 : ℝ) < sqrt 2 := by positivity
  have e : c0 ^ 2 * exp (2 * c0) / 4 / 2 = (c0 * exp c0 / (2 * sqrt 2)) ^ 2 := by
    rw [div_pow, mul_pow, mul_pow, sq_sqrt (by norm_num : (0 : ℝ) ≤ 2), ← exp_nat_mul]
    push_cast; ring_nf
  rw [e, sqrt_sq (by positivity)]

/-- **Theorem `thm:abstain`, formal.** Let a rule have measurable, disjoint outcome sets `Stab` and `Unst` (the rest
is abstention), with `P_s(Unst) ≤ α` for every `s ∈ (0, 1)` and `P_s(Stab) ≤ α` for every `s ∈ [1, 2)`. Then for
`0 < c₀ < 1` and every `s` with `|s - 1| < c₀/T`, `P_s(abstain) ≥ 1 - 2α - c₀ e^{c₀}/(2√2)`. -/
theorem p1_thm_abstain (T : ℕ) (hT : 0 < T) (v : ℝ≥0) (hv : v ≠ 0) (α c0 : ℝ) (hc0 : 0 < c0) (hc01 : c0 < 1)
    (Stab Unst : Set (Fin T → ℝ)) (hS : MeasurableSet Stab) (hU : MeasurableSet Unst) (hdisj : Disjoint Stab Unst)
    (herrU : ∀ s, 0 < s → s < 1 → (arPathLaw T s v).real Unst ≤ α)
    (herrS : ∀ s, 1 ≤ s → s < 2 → (arPathLaw T s v).real Stab ≤ α)
    (s : ℝ) (hs1 : 1 - c0 / T < s) (hs2 : s < 1 + c0 / T) :
    1 - 2 * α - c0 * exp c0 / (2 * sqrt 2) ≤ (arPathLaw T s v).real (Stab ∪ Unst)ᶜ := by
  have hTpos : (0 : ℝ) < T := by exact_mod_cast hT
  have hT1 : (1 : ℝ) ≤ T := by exact_mod_cast hT
  have hcT : c0 / T ≤ c0 := div_le_self hc0.le hT1
  have hcT0 : 0 < c0 / T := div_pos hc0 hTpos
  have habst : (arPathLaw T s v).real (Stab ∪ Unst)ᶜ =
      1 - (arPathLaw T s v).real Stab - (arPathLaw T s v).real Unst := by
    rw [measureReal_compl (hS.union hU), measureReal_union hdisj hU]; simp; ring
  rw [habst]
  have hw := p1_sqrt_window c0 hc0.le
  rcases lt_or_ge s 1 with hlt | hge
  · -- pair `s` with `s + c₀/T ≥ 1`
    set s' := s + c0 / T
    have hkl := p1_ar_window_kl T hT c0 hc0.le s s' (by linarith) (by linarith)
      (by rw [show s' - s = c0 / T by ring, abs_of_pos hcT0]) v hv
    have hgap := p1_event_gap_le _ _ hS _ (by positivity) hkl
    rw [hw] at hgap
    have h1 := herrU s (by linarith) hlt
    have h2 := herrS s' (by linarith) (by linarith)
    have := le_abs_self ((arPathLaw T s v).real Stab - (arPathLaw T s' v).real Stab)
    linarith
  · -- pair `s` with `s - c₀/T < 1`
    set s' := s - c0 / T
    have hkl := p1_ar_window_kl T hT c0 hc0.le s s' (by linarith) hs2.le
      (by rw [show s' - s = -(c0 / T) by ring, abs_neg, abs_of_pos hcT0]) v hv
    have hgap := p1_event_gap_le _ _ hU _ (by positivity) hkl
    rw [hw] at hgap
    have h1 := herrS s hge (by linarith)
    have h2 := herrU s' (by linarith) (by linarith)
    have := le_abs_self ((arPathLaw T s v).real Unst - (arPathLaw T s' v).real Unst)
    linarith

/-- **Theorem `thm:abstain`, binary rules.** For a binary rule (`Stab = Unstᶜ`) and every `ε > 0` there are
`s₀ ∈ (0, 1)` and `s₁ ∈ [1, 2)` with `max(P_{s₀}(Unst), P_{s₁}(Stab)) ≥ 1/2 - ε`; so the worst-case error over
`s ∈ (0, 2)` is at least `1/2`. -/
theorem p1_thm_abstain_binary (T : ℕ) (hT : 0 < T) (v : ℝ≥0) (hv : v ≠ 0) (Unst : Set (Fin T → ℝ))
    (hU : MeasurableSet Unst) (ε : ℝ) (hε : 0 < ε) :
    ∃ s0 s1 : ℝ, 0 < s0 ∧ s0 < 1 ∧ 1 ≤ s1 ∧ s1 < 2 ∧
      1 / 2 - ε ≤ max ((arPathLaw T s0 v).real Unst) ((arPathLaw T s1 v).real Unstᶜ) := by
  have hTpos : (0 : ℝ) < T := by exact_mod_cast hT
  have hT1 : (1 : ℝ) ≤ T := by exact_mod_cast hT
  set c0 := min (1 / 2) ε with hc0def
  have hc0 : 0 < c0 := lt_min (by norm_num) hε
  have hc0h : c0 ≤ 1 / 2 := min_le_left _ _
  have hc0e : c0 ≤ ε := min_le_right _ _
  have hcT0 : 0 < c0 / T := div_pos hc0 hTpos
  have hcT : c0 / T ≤ c0 := div_le_self hc0.le hT1
  refine ⟨1 - c0 / (2 * T), 1 + c0 / (2 * T), ?_, ?_, ?_, ?_, ?_⟩
  · have : c0 / (2 * T) ≤ c0 / 2 := by
      apply div_le_div_of_nonneg_left hc0.le (by norm_num) (by linarith)
    linarith
  · have : 0 < c0 / (2 * T) := by positivity
    linarith
  · have : 0 < c0 / (2 * T) := by positivity
    linarith
  · have : c0 / (2 * T) ≤ c0 / 2 := by
      apply div_le_div_of_nonneg_left hc0.le (by norm_num) (by linarith)
    linarith
  · have hgap : |(1 + c0 / (2 * T)) - (1 - c0 / (2 * T))| ≤ c0 / T := by
      rw [show (1 + c0 / (2 * T)) - (1 - c0 / (2 * T)) = c0 / T by field_simp; ring, abs_of_pos hcT0]
    have hkl := p1_ar_window_kl T hT c0 hc0.le (1 - c0 / (2 * T)) (1 + c0 / (2 * T))
      (by have : c0 / (2 * T) ≤ c0 / 2 := div_le_div_of_nonneg_left hc0.le (by norm_num) (by linarith)
          linarith)
      (by have : 0 < c0 / (2 * T) := by positivity
          have : 0 < c0 / T := hcT0
          linarith) hgap v hv
    have hwe := p1_worst_error_ge _ _ hU _ (by positivity) hkl
    rw [p1_sqrt_window c0 hc0.le] at hwe
    -- `c₀ e^{c₀}/(2√2) ≤ 2ε` since `c₀ ≤ ε`, `e^{c₀} ≤ e^{1/2} < 2` and `√2 ≥ 1`
    have hexp : exp c0 ≤ 2 := by
      have h1 : exp c0 ≤ exp (1 / 2) := exp_le_exp.mpr hc0h
      have h2 : exp (1 / 2 : ℝ) < 2 := by
        have := Real.exp_one_lt_d9
        have h3 : exp (1 / 2 : ℝ) ^ 2 = exp 1 := by rw [← exp_nat_mul]; norm_num
        nlinarith [exp_pos (1 / 2 : ℝ)]
      linarith
    have hs2 : 1 ≤ sqrt 2 := by rw [show (1 : ℝ) = sqrt 1 by simp]; exact sqrt_le_sqrt (by norm_num)
    have hb : c0 * exp c0 / (2 * sqrt 2) ≤ 2 * ε := by
      rw [div_le_iff₀ (by positivity)]
      nlinarith [exp_pos c0]
    linarith

end CurrentMM
