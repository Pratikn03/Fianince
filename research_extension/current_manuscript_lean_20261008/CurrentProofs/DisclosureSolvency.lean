import CurrentProofs.PositiveDynamics

namespace CurrentMM
noncomputable section
open scoped BigOperators

theorem counterparty_pulse_margin_all_times {n : ℕ}
    (a impact A cost margin P B : ℝ) (q rate : Fin n → ℝ)
    (ha : 0 ≤ a) (hk : 0 ≤ impact) (hA : 0 ≤ A) (hq : ∀ i, 0 ≤ q i)
    (hrate : ∀ i, 0 ≤ rate i ∧ rate i ≤ 1)
    (hfeedback : a + impact * ∑ i, q i ≤ 1) (hm : 0 ≤ margin)
    (hbudget : (margin + 1 / 2) * impact * A ^ 2 + (cost + margin * P) * A ≤ B)
    (t : ℕ) :
    let mark := P + (autonomousState a impact q rate (pulse1 a impact q rate A) t).price
    margin * |-A| * mark ≤
      equity (B + A * averageFill P impact A - cost * A) (-A) mark := by
  dsimp only
  have hp := physical_positive_pulse_peak a impact A q rate ha hk hA hq hrate hfeedback t
  rw [abs_neg, abs_of_nonneg hA]
  unfold equity averageFill
  have hmult := mul_le_mul_of_nonneg_left hp.2
    (show 0 ≤ (1 + margin) * A by positivity)
  nlinarith

theorem counterparty_pulse_cap_guarantees_margin {n : ℕ}
    (a impact A cost margin P B : ℝ) (q rate : Fin n → ℝ)
    (ha : 0 ≤ a) (hk : 0 < impact) (hA : 0 ≤ A) (hc : 0 ≤ cost)
    (hm : 0 < margin) (hP : 0 < P) (hB : 0 < B) (hq : ∀ i, 0 ≤ q i)
    (hrate : ∀ i, 0 ≤ rate i ∧ rate i ≤ 1)
    (hfeedback : a + impact * ∑ i, q i ≤ 1)
    (hcap : A ≤ robustQuantityCap ((margin + 1 / 2) * impact) (cost + margin * P) B)
    (t : ℕ) :
    let mark := P + (autonomousState a impact q rate (pulse1 a impact q rate A) t).price
    margin * |-A| * mark ≤
      equity (B + A * averageFill P impact A - cost * A) (-A) mark := by
  have hbudget := (robust_quantity_cap_iff ((margin + 1 / 2) * impact)
    (cost + margin * P) B A (by positivity) (by positivity) hB hA).2 hcap
  exact counterparty_pulse_margin_all_times a impact A cost margin P B q rate ha hk.le hA
    hq hrate hfeedback hm.le hbudget t

theorem arbitrarily_small_solvent_exact_disclosure
    (B P a impact cost q rate delta margin radius : ℝ)
    (hB : 0 < B) (hP : 0 < P) (ha : 0 ≤ a) (hk : 0 < impact) (hc : 0 ≤ cost)
    (hq : 0 < q) (hm : 0 < margin) (hr : 0 < radius) (hd : delta ≠ 0)
    (hfeedback : a + impact * q ≤ 1) (hsingle : 0 ≤ rate ∧ rate ≤ 1)
    (hsplit : ∀ i : Fin 2, 0 ≤ pairRates rate delta i ∧ pairRates rate delta i ≤ 1) :
    ∃ A : ℝ, 0 < A ∧ A ≤ radius ∧
      (∀ t : ℕ,
        let mark := P + (autonomousState a impact (fun _ : Fin 1 => q)
          (fun _ => rate) (pulse1 a impact (fun _ : Fin 1 => q) (fun _ => rate) A) t).price
        margin * |-A| * mark ≤
          equity (B + A * averageFill P impact A - cost * A) (-A) mark) ∧
      (∀ t : ℕ,
        let mark := P + (autonomousState a impact (fun _ : Fin 2 => q / 2)
          (pairRates rate delta)
          (pulse1 a impact (fun _ : Fin 2 => q / 2) (pairRates rate delta) A) t).price
        margin * |-A| * mark ≤
          equity (B + A * averageFill P impact A - cost * A) (-A) mark) ∧
      let e0 := counterpartyThirdEquity B P a impact cost A
        (fun _ : Fin 1 => q) (fun _ => rate)
      let e1 := counterpartyThirdEquity B P a impact cost A
        (fun _ : Fin 2 => q / 2) (pairRates rate delta)
      exactEquityDecision e0 e0 = false ∧ exactEquityDecision e0 e1 = true := by
  obtain ⟨A, hA, hAr, hAc, htest⟩ := arbitrarily_small_equity_distinguishing_pulse
    B P a impact cost q rate delta margin radius hB hP hk hc hq hd hm hr
  refine ⟨A, hA, hAr, ?_, ?_, htest⟩
  · intro t
    exact counterparty_pulse_cap_guarantees_margin a impact A cost margin P B
      (fun _ : Fin 1 => q) (fun _ => rate) ha hk hA.le hc hm hP hB
      (fun _ => hq.le) (fun _ => hsingle) (by simpa using hfeedback) hAc t
  · intro t
    exact counterparty_pulse_cap_guarantees_margin a impact A cost margin P B
      (fun _ : Fin 2 => q / 2) (pairRates rate delta) ha hk hA.le hc hm hP hB
      (fun _ => by positivity) hsplit
      (by convert hfeedback using 1 <;> simp only [Fin.sum_univ_two] <;> ring) hAc t

end
end CurrentMM
