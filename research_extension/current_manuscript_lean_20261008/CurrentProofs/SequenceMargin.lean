import CurrentProofs.CohortConvolution
import CurrentProofs.Execution

namespace CurrentMM
noncomputable section
open scoped BigOperators

def cohortStateLE {n : ℕ} (x y : CohortState n) : Prop :=
  x.price ≤ y.price ∧ ∀ i, x.memory i ≤ y.memory i

theorem positive_cohort_step_monotone {n : ℕ} (a impact : ℝ)
    (q rate : Fin n → ℝ) (x y : CohortState n)
    (ha : 0 ≤ a) (hk : 0 ≤ impact) (hq : ∀ i, 0 ≤ q i)
    (hr : ∀ i, 0 ≤ rate i ∧ rate i ≤ 1) (hxy : cohortStateLE x y) :
    cohortStateLE (cohortStep a impact q rate 0 x) (cohortStep a impact q rate 0 y) := by
  have hp : (cohortStep a impact q rate 0 x).price ≤
      (cohortStep a impact q rate 0 y).price := by
    dsimp [cohortStep]
    exact add_le_add (add_le_add (mul_le_mul_of_nonneg_left hxy.1 ha)
      (mul_le_mul_of_nonneg_left
        (Finset.sum_le_sum fun i _ => mul_le_mul_of_nonneg_left (hxy.2 i) (hq i)) hk))
      (le_refl _)
  refine ⟨hp, ?_⟩
  intro i
  exact add_le_add (mul_le_mul_of_nonneg_left (hxy.2 i) (by linarith [(hr i).2]))
    (mul_le_mul_of_nonneg_left hp (hr i).1)

def cumulativeQuantity {n : ℕ} (v : Fin n → ℝ) : ℝ := ∑ i, v i
def sequenceFinalDisplacement {n : ℕ} (h : ℕ → ℝ) (v : Fin n → ℝ) : ℝ :=
  ∑ i, v i * h (n - 1 - i.val)
def sequenceDealerCash {n : ℕ} (B P impact fee : ℝ) (h : ℕ → ℝ)
    (v : Fin n → ℝ) : ℝ :=
  B + ∑ i, v i * (P + baselineDisplacement h v i + impact * v i / 2)
    - fee * cumulativeQuantity v
def sequenceDealerEquity {n : ℕ} (B P impact fee : ℝ) (h : ℕ → ℝ)
    (v : Fin n → ℝ) : ℝ :=
  equity (sequenceDealerCash B P impact fee h v) (-cumulativeQuantity v)
    (P + sequenceFinalDisplacement h v)
def adverseMarkEntry (n : ℕ) (h : ℕ → ℝ) (i j : Fin n) : ℝ :=
  (h (n - 1 - i.val) + h (n - 1 - j.val) - h (Nat.dist i.val j.val)) / 2

theorem actual_sequence_dealer_equity {n : ℕ} (B P impact fee : ℝ)
    (h : ℕ → ℝ) (v : Fin n → ℝ) (h0 : h 0 = impact) :
    sequenceDealerEquity B P impact fee h v = B + quadraticExecutionCost h v
      - cumulativeQuantity v * sequenceFinalDisplacement h v - fee * cumulativeQuantity v := by
  have hs : (∑ i, v i * (P + baselineDisplacement h v i + impact * v i / 2)) =
      cumulativeQuantity v * P + (∑ i, v i * baselineDisplacement h v i) +
        impact / 2 * ∑ i, v i ^ 2 := by
    simp_rw [mul_add, Finset.sum_add_distrib]
    unfold cumulativeQuantity
    rw [Finset.sum_mul]
    congr 1
    rw [Finset.mul_sum]
    apply Finset.sum_congr rfl
    intro i hi
    ring
  rw [quadratic_execution_cost_triangular, h0]
  unfold sequenceDealerEquity equity sequenceDealerCash
  rw [hs]
  ring

theorem adverse_mark_entry_upper_bound (n : ℕ) (h : ℕ → ℝ) (impact : ℝ)
    (hmono : Antitone h) (h0 : h 0 = impact) (i j : Fin n) :
    adverseMarkEntry n h i j ≤ impact / 2 := by
  have hb (k : ℕ) : h k ≤ impact := by simpa [h0] using hmono (Nat.zero_le k)
  rcases le_total i.val j.val with hij | hji
  · have hd : Nat.dist i.val j.val ≤ n - 1 - i.val := by
      rw [Nat.dist_eq_sub_of_le hij]
      have := j.is_lt
      omega
    have hc := hmono hd
    unfold adverseMarkEntry
    linarith [hb (n - 1 - j.val)]
  · have hd : Nat.dist i.val j.val ≤ n - 1 - j.val := by
      rw [Nat.dist_eq_sub_of_le_right hji]
      have := i.is_lt
      omega
    have hc := hmono hd
    unfold adverseMarkEntry
    linarith [hb (n - 1 - i.val)]

theorem sequence_adverse_quadratic_identity {n : ℕ} (h : ℕ → ℝ)
    (v : Fin n → ℝ) :
    cumulativeQuantity v * sequenceFinalDisplacement h v - quadraticExecutionCost h v =
      ∑ i, ∑ j, v i * v j * adverseMarkEntry n h i j := by
  have hleft : (∑ i, ∑ j, v i * v j * h (n - 1 - i.val)) =
      cumulativeQuantity v * sequenceFinalDisplacement h v := by
    have hi (i : Fin n) : (∑ j, v i * v j * h (n - 1 - i.val)) =
        (v i * h (n - 1 - i.val)) * cumulativeQuantity v := by
      unfold cumulativeQuantity
      rw [Finset.mul_sum]
      apply Finset.sum_congr rfl
      intro j hj
      ring
    simp_rw [hi]
    rw [← Finset.sum_mul]
    change sequenceFinalDisplacement h v * cumulativeQuantity v = _
    ring
  have hright : (∑ i, ∑ j, v i * v j * h (n - 1 - j.val)) =
      cumulativeQuantity v * sequenceFinalDisplacement h v := by
    rw [Finset.sum_comm]
    convert hleft using 1
    apply Finset.sum_congr rfl
    intro i hi
    apply Finset.sum_congr rfl
    intro j hj
    ring
  simp_rw [adverseMarkEntry, mul_div, mul_sub, mul_add]
  simp_rw [← Finset.sum_div, Finset.sum_sub_distrib, Finset.sum_add_distrib]
  rw [hleft, hright]
  unfold quadraticExecutionCost
  ring

theorem nonnegative_sequence_adverse_mark_bound {n : ℕ} (h : ℕ → ℝ)
    (impact : ℝ) (v : Fin n → ℝ) (hv : ∀ i, 0 ≤ v i)
    (hmono : Antitone h) (h0 : h 0 = impact) :
    cumulativeQuantity v * sequenceFinalDisplacement h v - quadraticExecutionCost h v ≤
      impact / 2 * (cumulativeQuantity v) ^ 2 := by
  rw [sequence_adverse_quadratic_identity]
  calc
    _ ≤ ∑ i, ∑ j, v i * v j * (impact / 2) := by
      apply Finset.sum_le_sum
      intro i hi
      apply Finset.sum_le_sum
      intro j hj
      exact mul_le_mul_of_nonneg_left
        (adverse_mark_entry_upper_bound n h impact hmono h0 i j)
        (mul_nonneg (hv i) (hv j))
    _ = _ := by
      simp only [cumulativeQuantity, pow_two, Finset.sum_mul, Finset.mul_sum]
      apply Finset.sum_congr rfl
      intro i hi
      apply Finset.sum_congr rfl
      intro j hj
      ring

theorem nonnegative_sequence_displacement_bound {n : ℕ} (h : ℕ → ℝ)
    (impact : ℝ) (v : Fin n → ℝ) (hv : ∀ i, 0 ≤ v i)
    (hmono : Antitone h) (h0 : h 0 = impact) :
    sequenceFinalDisplacement h v ≤ impact * cumulativeQuantity v := by
  unfold sequenceFinalDisplacement cumulativeQuantity
  rw [Finset.mul_sum]
  apply Finset.sum_le_sum
  intro i hi
  have hb : h (n - 1 - i.val) ≤ impact := by simpa [h0] using hmono (Nat.zero_le _)
  nlinarith [mul_le_mul_of_nonneg_left hb (hv i)]

theorem nonnegative_sequence_margin {n : ℕ} (B P impact fee margin V : ℝ)
    (h : ℕ → ℝ) (v : Fin n → ℝ) (hv : ∀ i, 0 ≤ v i)
    (hk : 0 ≤ impact) (hP : 0 ≤ P) (hc : 0 ≤ fee) (hm : 0 ≤ margin)
    (hmono : Antitone h) (h0 : h 0 = impact)
    (hbudget : cumulativeQuantity v ≤ V)
    (hcapital : (margin + 1 / 2) * impact * V ^ 2 + (fee + margin * P) * V ≤ B) :
    margin * |-(cumulativeQuantity v)| * (P + sequenceFinalDisplacement h v) ≤
      sequenceDealerEquity B P impact fee h v := by
  have hU : 0 ≤ cumulativeQuantity v := Finset.sum_nonneg fun i _ => hv i
  have hV : 0 ≤ V := le_trans hU hbudget
  have hsq : (cumulativeQuantity v) ^ 2 ≤ V ^ 2 := by nlinarith
  have ha := nonnegative_sequence_adverse_mark_bound h impact v hv hmono h0
  have hx := nonnegative_sequence_displacement_bound h impact v hv hmono h0
  have hb := mul_le_mul_of_nonneg_left hx (mul_nonneg hm hU)
  have hq := mul_le_mul_of_nonneg_left hsq
    (show 0 ≤ (margin + 1 / 2) * impact by positivity)
  have hl := mul_le_mul_of_nonneg_left hbudget
    (show 0 ≤ fee + margin * P by positivity)
  rw [abs_neg, abs_of_nonneg hU, actual_sequence_dealer_equity B P impact fee h v h0]
  nlinarith

def robustNonnegativeSequenceMargin (B P impact fee margin V : ℝ)
    (h : ℕ → ℝ) : Prop :=
  ∀ n (v : Fin n → ℝ), (∀ i, 0 ≤ v i) → cumulativeQuantity v ≤ V →
    margin * |-(cumulativeQuantity v)| * (P + sequenceFinalDisplacement h v) ≤
      sequenceDealerEquity B P impact fee h v

theorem single_sequence_pulse_account (B P impact fee V : ℝ) (h : ℕ → ℝ)
    (h0 : h 0 = impact) :
    sequenceDealerEquity B P impact fee h (fun _ : Fin 1 => V) =
      B - impact * V ^ 2 / 2 - fee * V := by
  simp [sequenceDealerEquity, sequenceDealerCash, cumulativeQuantity,
    sequenceFinalDisplacement, baselineDisplacement, equity, h0]
  ring

theorem robust_nonnegative_sequence_margin_iff (B P impact fee margin V : ℝ)
    (h : ℕ → ℝ) (hk : 0 ≤ impact) (hP : 0 ≤ P) (hc : 0 ≤ fee)
    (hm : 0 ≤ margin) (hV : 0 ≤ V) (hmono : Antitone h) (h0 : h 0 = impact) :
    robustNonnegativeSequenceMargin B P impact fee margin V h ↔
      (margin + 1 / 2) * impact * V ^ 2 + (fee + margin * P) * V ≤ B := by
  constructor
  · intro hall
    have hs := hall 1 (fun _ => V) (fun _ => hV)
      (by simp [cumulativeQuantity])
    rw [single_sequence_pulse_account B P impact fee V h h0] at hs
    simp only [cumulativeQuantity, sequenceFinalDisplacement, Fin.sum_univ_one,
      Fin.val_zero, Nat.sub_self, Nat.sub_zero, h0, abs_neg, abs_of_nonneg hV] at hs
    nlinarith
  · intro hcap n v hv hbudget
    exact nonnegative_sequence_margin B P impact fee margin V h v hv hk hP hc hm
      hmono h0 hbudget hcap

theorem robust_nonnegative_quantity_allowance_iff (B P impact fee margin V : ℝ)
    (h : ℕ → ℝ) (hk : 0 < impact) (hP : 0 < P) (hc : 0 ≤ fee)
    (hm : 0 < margin) (hB : 0 < B) (hV : 0 ≤ V)
    (hmono : Antitone h) (h0 : h 0 = impact) :
    robustNonnegativeSequenceMargin B P impact fee margin V h ↔
      V ≤ robustQuantityCap ((margin + 1 / 2) * impact) (fee + margin * P) B := by
  rw [robust_nonnegative_sequence_margin_iff B P impact fee margin V h
    (le_of_lt hk) (le_of_lt hP) hc (le_of_lt hm) hV hmono h0]
  exact robust_quantity_cap_iff _ _ _ _ (by positivity) (by positivity) hB hV

def partialLastFill {n : ℕ} (v : Fin (n + 1) → ℝ) (fraction : ℝ) : Fin (n + 1) → ℝ :=
  fun i => if i = Fin.last n then fraction * v i else v i

theorem partial_last_fill_quantity_bound {n : ℕ} (v : Fin (n + 1) → ℝ)
    (fraction : ℝ) (hv : ∀ i, 0 ≤ v i) (hf : 0 ≤ fraction ∧ fraction ≤ 1) :
    (∀ i, 0 ≤ partialLastFill v fraction i) ∧
      cumulativeQuantity (partialLastFill v fraction) ≤ cumulativeQuantity v := by
  constructor
  · intro i
    unfold partialLastFill
    split_ifs
    · exact mul_nonneg hf.1 (hv i)
    · exact hv i
  · unfold cumulativeQuantity
    apply Finset.sum_le_sum
    intro i hi
    unfold partialLastFill
    split_ifs
    · nlinarith [mul_le_mul_of_nonneg_right hf.2 (hv i)]
    · rfl

theorem intermediate_linear_fill_margin {n : ℕ} (B P impact fee margin V : ℝ)
    (h : ℕ → ℝ) (v : Fin (n + 1) → ℝ) (fraction : ℝ)
    (hv : ∀ i, 0 ≤ v i) (hf : 0 ≤ fraction ∧ fraction ≤ 1)
    (hk : 0 ≤ impact) (hP : 0 ≤ P) (hc : 0 ≤ fee) (hm : 0 ≤ margin)
    (hmono : Antitone h) (h0 : h 0 = impact) (hbudget : cumulativeQuantity v ≤ V)
    (hcapital : (margin + 1 / 2) * impact * V ^ 2 + (fee + margin * P) * V ≤ B) :
    margin * |-(cumulativeQuantity (partialLastFill v fraction))| *
        (P + sequenceFinalDisplacement h (partialLastFill v fraction)) ≤
      sequenceDealerEquity B P impact fee h (partialLastFill v fraction) := by
  have hp := partial_last_fill_quantity_bound v fraction hv hf
  exact nonnegative_sequence_margin B P impact fee margin V h _ hp.1 hk hP hc hm
    hmono h0 (le_trans hp.2 hbudget) hcapital

end
end CurrentMM
