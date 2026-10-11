import CurrentProofs.CohortAlgebra
import CurrentProofs.Accounts
import Mathlib.Algebra.BigOperators.Fin
import Mathlib.Data.Fin.VecNotation

namespace CurrentMM

noncomputable section
open scoped BigOperators

structure CohortState (n : ℕ) where
  price : ℝ
  memory : Fin n → ℝ

def zeroState (n : ℕ) : CohortState n := ⟨0, fun _ => 0⟩

def cohortStep {n : ℕ} (a impact : ℝ) (q rate : Fin n → ℝ)
    (quantity : ℝ) (state : CohortState n) : CohortState n :=
  let p := a * state.price + impact * (∑ i, q i * state.memory i) + impact * quantity
  ⟨p, fun i => (1 - rate i) * state.memory i + rate i * p⟩

def pulse1 {n : ℕ} (a impact : ℝ) (q rate : Fin n → ℝ) (A : ℝ) : CohortState n :=
  cohortStep a impact q rate A (zeroState n)
def pulse2 {n : ℕ} (a impact : ℝ) (q rate : Fin n → ℝ) (A : ℝ) : CohortState n :=
  cohortStep a impact q rate 0 (pulse1 a impact q rate A)
def pulse3 {n : ℕ} (a impact : ℝ) (q rate : Fin n → ℝ) (A : ℝ) : CohortState n :=
  cohortStep a impact q rate 0 (pulse2 a impact q rate A)

theorem physical_first_pulse_price {n : ℕ} (a impact : ℝ)
    (q rate : Fin n → ℝ) (A : ℝ) :
    (pulse1 a impact q rate A).price = impact * A := by
  simp [pulse1, cohortStep, zeroState]

theorem physical_first_pulse_memory {n : ℕ} (a impact : ℝ)
    (q rate : Fin n → ℝ) (A : ℝ) (i : Fin n) :
    (pulse1 a impact q rate A).memory i = rate i * (impact * A) := by
  simp [pulse1, cohortStep, zeroState]

theorem physical_single_second_price (a impact q rate A : ℝ) :
    (pulse2 a impact (fun _ : Fin 1 => q) (fun _ => rate) A).price =
      A * singlePriceTap1 a impact q rate := by
  simp [pulse2, pulse1, cohortStep, zeroState, singlePriceTap1]
  ring

theorem physical_single_third_price (a impact q rate A : ℝ) :
    (pulse3 a impact (fun _ : Fin 1 => q) (fun _ => rate) A).price =
      A * singlePriceTap2 a impact q rate := by
  simp [pulse3, pulse2, pulse1, cohortStep, zeroState, singlePriceTap2, singlePriceTap1]
  ring

def pairRates (rate delta : ℝ) : Fin 2 → ℝ := ![rate - delta, rate + delta]

theorem physical_split_second_price (a impact q rate delta A : ℝ) :
    (pulse2 a impact (fun _ : Fin 2 => q / 2) (pairRates rate delta) A).price =
      A * splitPriceTap1 a impact q rate delta := by
  simp [pulse2, pulse1, cohortStep, zeroState, pairRates, splitPriceTap1,
    Fin.sum_univ_two]
  ring

theorem physical_split_third_price (a impact q rate delta A : ℝ) :
    (pulse3 a impact (fun _ : Fin 2 => q / 2) (pairRates rate delta) A).price =
      A * splitPriceTap2 a impact q rate delta := by
  simp [pulse3, pulse2, pulse1, cohortStep, zeroState, pairRates,
    splitPriceTap2, splitPriceTap1, Fin.sum_univ_two]
  ring

theorem physical_third_observation_separation (a impact q rate delta A : ℝ) :
    (pulse3 a impact (fun _ : Fin 2 => q / 2) (pairRates rate delta) A).price -
      (pulse3 a impact (fun _ : Fin 1 => q) (fun _ => rate) A).price =
      -A * impact ^ 2 * q * delta ^ 2 := by
  rw [physical_split_third_price, physical_single_third_price]
  calc
    A * splitPriceTap2 a impact q rate delta - A * singlePriceTap2 a impact q rate =
        A * (splitPriceTap2 a impact q rate delta - singlePriceTap2 a impact q rate) := by ring
    _ = -A * impact ^ 2 * q * delta ^ 2 := by
      rw [symmetric_third_tap_difference]
      ring

def counterpartyThirdEquity {n : ℕ} (B P a impact cost A : ℝ)
    (q rate : Fin n → ℝ) : ℝ :=
  equity (B + A * averageFill P impact A - cost * A) (-A)
    (P + (pulse3 a impact q rate A).price)

theorem exact_equity_disclosure_from_recursion (B P a impact cost q rate delta A : ℝ) :
    counterpartyThirdEquity B P a impact cost A (fun _ : Fin 2 => q / 2)
        (pairRates rate delta) -
      counterpartyThirdEquity B P a impact cost A (fun _ : Fin 1 => q) (fun _ => rate) =
      A ^ 2 * impact ^ 2 * q * delta ^ 2 := by
  unfold counterpartyThirdEquity equity
  have h := physical_third_observation_separation a impact q rate delta A
  calc
    _ = -A * ((pulse3 a impact (fun _ : Fin 2 => q / 2)
        (pairRates rate delta) A).price -
        (pulse3 a impact (fun _ : Fin 1 => q) (fun _ => rate) A).price) := by ring
    _ = _ := by rw [h]; ring

theorem exact_equity_marks_distinct (B P a impact cost q rate delta A : ℝ)
    (hA : 0 < A) (hk : 0 < impact) (hq : 0 < q) (hd : delta ≠ 0) :
    counterpartyThirdEquity B P a impact cost A (fun _ : Fin 2 => q / 2)
        (pairRates rate delta) ≠
      counterpartyThirdEquity B P a impact cost A (fun _ : Fin 1 => q) (fun _ => rate) := by
  have h := exact_equity_disclosure_from_recursion B P a impact cost q rate delta A
  have hp : 0 < A ^ 2 * impact ^ 2 * q * delta ^ 2 := by positivity
  intro heq
  rw [heq] at h
  linarith

def exactEquityDecision (singleEquity observation : ℝ) : Bool :=
  decide (singleEquity < observation)

theorem exact_equity_decision_correct (B P a impact cost q rate delta A : ℝ)
    (hA : 0 < A) (hk : 0 < impact) (hq : 0 < q) (hd : delta ≠ 0) :
    let e0 := counterpartyThirdEquity B P a impact cost A
      (fun _ : Fin 1 => q) (fun _ => rate)
    let e1 := counterpartyThirdEquity B P a impact cost A
      (fun _ : Fin 2 => q / 2) (pairRates rate delta)
    exactEquityDecision e0 e0 = false ∧ exactEquityDecision e0 e1 = true := by
  dsimp only
  have h := exact_equity_disclosure_from_recursion B P a impact cost q rate delta A
  have hp : 0 < A ^ 2 * impact ^ 2 * q * delta ^ 2 := by positivity
  have hlt : counterpartyThirdEquity B P a impact cost A
      (fun _ : Fin 1 => q) (fun _ => rate) <
      counterpartyThirdEquity B P a impact cost A
      (fun _ : Fin 2 => q / 2) (pairRates rate delta) := by linarith
  simp [exactEquityDecision, hlt]

theorem arbitrarily_small_equity_distinguishing_pulse
    (B P a impact cost q rate delta margin radius : ℝ)
    (hB : 0 < B) (hP : 0 < P) (hk : 0 < impact) (hc : 0 ≤ cost)
    (hq : 0 < q) (hd : delta ≠ 0) (hm : 0 < margin) (hr : 0 < radius) :
    ∃ A : ℝ, 0 < A ∧ A ≤ radius ∧
      A ≤ robustQuantityCap ((margin + 1 / 2) * impact) (cost + margin * P) B ∧
      let e0 := counterpartyThirdEquity B P a impact cost A
        (fun _ : Fin 1 => q) (fun _ => rate)
      let e1 := counterpartyThirdEquity B P a impact cost A
        (fun _ : Fin 2 => q / 2) (pairRates rate delta)
      exactEquityDecision e0 e0 = false ∧ exactEquityDecision e0 e1 = true := by
  let cap := robustQuantityCap ((margin + 1 / 2) * impact) (cost + margin * P) B
  have hcap : 0 < cap := robust_quantity_cap_pos _ _ B (by positivity) (by positivity) hB
  let A := min radius cap / 2
  have hA : 0 < A := by dsimp [A]; positivity
  have hAr : A ≤ radius := by dsimp [A]; linarith [min_le_left radius cap]
  have hAc : A ≤ cap := by dsimp [A]; linarith [min_le_right radius cap]
  exact ⟨A, hA, hAr, hAc, exact_equity_decision_correct B P a impact cost q rate delta A
    hA hk hq hd⟩

end
end CurrentMM
