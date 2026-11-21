import Mathlib

/-!
# Paper 1, 21 November 2026: main-text decision results and the hiding proposition

Deterministic steps of results that were on paper only:

* Proposition `n:interv` (iii): a rule that acts with probability `p` where the action is safe acts with probability
  at least `p - δ` where it is unsafe, when the records are within total variation `δ` (`interv_tv`); and (ii): a
  rule's action probability depends on the population only through what the record law depends on (`interv_same`).
* Proposition `n:target` (i): a uniform scaling meets the ceiling exactly when `θ ≤ (s̄ - a)/(S - a)`, so the
  decision depends on the population only through `S` (`target_uniform_iff`, `target_uniform_same`).
* Corollary `n:decisionloss`: the two-point loss bound and the record length it forces
  (`decision_loss_tv`, `decision_loss_kl`, `decision_record_length`, `decision_tag_loss`).
* Corollary `n:sep`: the ratio of experiment counts and its divergence as memories collide (`sep_ratio`,
  `sep_unbounded`).
* Proposition `prop:hiding` (i)-(iii) (`hiding_sufficiency`, `hiding_cap`, `hiding_adopt`, `hiding_eventually`).
* Corollary `cor:robustuniform`: when the record cannot rule out relabelings, a halt of any one label is guaranteed
  to remove only the smallest class contribution, while a uniform cut removes exactly what the ceiling requires
  (`halt_guarantee`, `halt_guarantee_attained`, `uniform_exact`, `uniform_minimal_removal`).

Total variation, Pinsker's inequality and the Gaussian tail enter as hypotheses on real numbers.
-/
namespace Paper1Revision8

open scoped BigOperators
open Filter

/-! ### Proposition `n:interv` -/

/-- (iii) If `|P(act) - Q(act)| ≤ δ`, a rule acting with probability `p` under `P` acts with probability at least
`p - δ` under `Q`. -/
theorem interv_tv (pSafe pUnsafe δ : ℝ) (htv : |pSafe - pUnsafe| ≤ δ) : pSafe - δ ≤ pUnsafe := by
  have := neg_abs_le (pSafe - pUnsafe)
  have := le_abs_self (pSafe - pUnsafe)
  linarith

/-- (ii) If the record law depends on the population only through its flow map `F`, every rule's action
probability does too: two populations with the same flow map act with the same probability. -/
theorem interv_same {Pop Flow Law : Type*} (F : Pop → Flow) (law : Flow → Law) (act : Law → ℝ)
    (A B : Pop) (h : F A = F B) : act (law (F A)) = act (law (F B)) := by
  rw [h]

/-! ### Proposition `n:target` (i) -/

/-- Scaling all feedback by `θ` meets the ceiling `s̄` exactly when `θ ≤ (s̄ - a)/(S - a)` (for `S > a`). -/
theorem target_uniform_iff (a S sbar θ : ℝ) (hS : a < S) :
    a + θ * (S - a) ≤ sbar ↔ θ ≤ (sbar - a) / (S - a) := by
  have hpos : 0 < S - a := by linarith
  rw [le_div_iff₀ hpos]
  constructor <;> intro h <;> linarith

/-- The decision depends on the population only through `S`. -/
theorem target_uniform_same (a S S' sbar θ : ℝ) (h : S = S') :
    (a + θ * (S - a) ≤ sbar) ↔ (a + θ * (S' - a) ≤ sbar) := by
  rw [h]

/-! ### Corollary `n:decisionloss` -/

/-- Two-point loss bound. A rule halts with probability `p0` in economy 0 (loss `b` if it halts) and `p1` in
economy 1 (loss `c` if it does not); with `p1 - p0 ≤ TV`, the average loss is at least `min(b,c)(1 - TV)/2`. -/
theorem decision_loss_tv (b c p0 p1 tv : ℝ) (hb : 0 < b) (hc : 0 < c)
    (hp0 : 0 ≤ p0) (hp1 : p1 ≤ 1) (htv : p1 - p0 ≤ tv) :
    min b c / 2 * (1 - tv) ≤ (b * p0 + c * (1 - p1)) / 2 := by
  have hm1 : min b c ≤ b := min_le_left b c
  have hm2 : min b c ≤ c := min_le_right b c
  have hm0 : 0 ≤ min b c := le_min hb.le hc.le
  have h1 : min b c * p0 ≤ b * p0 := mul_le_mul_of_nonneg_right hm1 hp0
  have h2 : min b c * (1 - p1) ≤ c * (1 - p1) := mul_le_mul_of_nonneg_right hm2 (by linarith)
  have h3 : min b c * (1 - tv) ≤ min b c * (p0 + (1 - p1)) := mul_le_mul_of_nonneg_left (by linarith) hm0
  nlinarith

/-- With Pinsker, `TV ≤ √(KL/2)`, the bound in divergence form. -/
theorem decision_loss_kl (b c p0 p1 tv kl : ℝ) (hb : 0 < b) (hc : 0 < c)
    (hp0 : 0 ≤ p0) (hp1 : p1 ≤ 1) (htv : p1 - p0 ≤ tv) (hpin : tv ≤ Real.sqrt (kl / 2)) :
    min b c / 2 * (1 - Real.sqrt (kl / 2)) ≤ (b * p0 + c * (1 - p1)) / 2 := by
  have h := decision_loss_tv b c p0 p1 tv hb hc hp0 hp1 htv
  have hm0 : 0 ≤ min b c / 2 := by have := le_min hb.le hc.le; linarith
  have : min b c / 2 * (1 - Real.sqrt (kl / 2)) ≤ min b c / 2 * (1 - tv) :=
    mul_le_mul_of_nonneg_left (by linarith) hm0
  linarith

/-- Record length: if the loss is at most `ε min(b,c)` with `ε < 1/2` and `KL ≤ C T Δⁿ`, then
`T ≥ 2(1 - 2ε)²/(C Δⁿ)`. -/
theorem decision_record_length (b c R ε kl C T D : ℝ) (hb : 0 < b) (hc : 0 < c) (hε : ε < 1 / 2)
    (hCD : 0 < C * D) (hR : R ≤ ε * min b c)
    (hlow : min b c / 2 * (1 - Real.sqrt (kl / 2)) ≤ R) (hkl : kl ≤ C * T * D) :
    2 * (1 - 2 * ε) ^ 2 / (C * D) ≤ T := by
  have hm : 0 < min b c := lt_min hb hc
  have h1 : 1 - 2 * ε ≤ Real.sqrt (kl / 2) := by
    have : min b c / 2 * (1 - Real.sqrt (kl / 2)) ≤ ε * min b c := le_trans hlow hR
    nlinarith
  have h0 : 0 ≤ 1 - 2 * ε := by linarith
  have hsq : (1 - 2 * ε) ^ 2 ≤ kl / 2 := by
    have hk : 0 ≤ kl / 2 := by
      by_contra hneg
      push_neg at hneg
      have : Real.sqrt (kl / 2) = 0 := Real.sqrt_eq_zero'.mpr hneg.le
      nlinarith
    calc (1 - 2 * ε) ^ 2 ≤ Real.sqrt (kl / 2) ^ 2 := pow_le_pow_left₀ h0 h1 2
      _ = kl / 2 := Real.sq_sqrt hk
  rw [div_le_iff₀ hCD]
  nlinarith

/-- Tagged measurements: if each error probability is at most `exp(-x)/2`, the average loss is at most
`max(b,c) exp(-x)/2`. -/
theorem decision_tag_loss (b c e0 e1 x : ℝ) (hb : 0 < b) (hc : 0 < c) (he0 : 0 ≤ e0) (he1 : 0 ≤ e1)
    (h0 : e0 ≤ Real.exp (-x) / 2) (h1 : e1 ≤ Real.exp (-x) / 2) :
    (b * e0 + c * e1) / 2 ≤ max b c / 2 * Real.exp (-x) := by
  have hb' : b ≤ max b c := le_max_left b c
  have hc' : c ≤ max b c := le_max_right b c
  have hM : 0 ≤ max b c := le_trans hb.le hb'
  have : b * e0 + c * e1 ≤ max b c * e0 + max b c * e1 := by
    have := mul_le_mul_of_nonneg_right hb' he0
    have := mul_le_mul_of_nonneg_right hc' he1
    linarith
  have : max b c * (e0 + e1) ≤ max b c * Real.exp (-x) := mul_le_mul_of_nonneg_left (by linarith) hM
  nlinarith

/-! ### Corollary `n:sep` -/

/-- Ratio of experiment counts: `N_w ≥ c₁ Δ^{-n}` and `N_g ≤ c₂ / ε²` give `N_w / N_g ≥ (c₁/c₂) ε² Δ^{-n}`. -/
theorem sep_ratio (Nw Ng c1 c2 ε D : ℝ) (hc1 : 0 < c1) (hc2 : 0 < c2) (hε : 0 < ε) (hD : 0 < D)
    (hNg : 0 < Ng) (hw : c1 / D ≤ Nw) (hg : Ng ≤ c2 / ε ^ 2) :
    c1 / c2 * ε ^ 2 / D ≤ Nw / Ng := by
  rw [div_le_div_iff₀ hD hNg]
  have h1 : c1 / c2 * ε ^ 2 * Ng ≤ c1 / c2 * ε ^ 2 * (c2 / ε ^ 2) :=
    mul_le_mul_of_nonneg_left hg (by positivity)
  have h2 : c1 / c2 * ε ^ 2 * (c2 / ε ^ 2) = c1 := by field_simp
  have h3 : c1 ≤ Nw * D := by rwa [div_le_iff₀ hD] at hw
  linarith

/-- The ratio bound `c ε² Δ^{-n}` (written with `D = Δⁿ`) exceeds any level once `D` is small enough. -/
theorem sep_unbounded (c ε M : ℝ) (hc : 0 < c) (hε : 0 < ε) (hM : 0 < M) :
    ∃ D0 > 0, ∀ D, 0 < D → D < D0 → M < c * ε ^ 2 / D := by
  refine ⟨c * ε ^ 2 / M, by positivity, fun D hD hDD => ?_⟩
  rw [lt_div_iff₀ hD]
  rw [lt_div_iff₀ hM] at hDD
  linarith

/-! ### Proposition `prop:hiding` -/

/-- (i) If the targeting probability depends on the record only through its law and the law depends on the
population only through the kernel, a rule that reproduces the kernel of a population targeted with probability `α`
is targeted with probability `α`, whatever the probes, record length and rule. -/
theorem hiding_sufficiency {Rule Kernel Law : Type*} (kernel : Rule → Kernel) (law : Kernel → Law)
    (target : Law → ℝ) (ρ0 : Rule) (k0 : Kernel) (α : ℝ) (hk : kernel ρ0 = k0) (hα : target (law k0) = α) :
    target (law (kernel ρ0)) = α := by
  rw [hk, hα]

/-- (ii) A cost-minimizing rule is targeted with probability at most `α + (C₀ - C*)/P ≤ α + C₀/P`. -/
theorem hiding_cap (Cstar piStar C0 α P : ℝ) (hP : 0 < P) (hC : 0 ≤ Cstar)
    (hopt : Cstar + P * piStar ≤ C0 + P * α) :
    piStar ≤ α + (C0 - Cstar) / P ∧ α + (C0 - Cstar) / P ≤ α + C0 / P := by
  constructor
  · rw [← sub_le_iff_le_add', le_div_iff₀ hP]; linarith
  · have : (C0 - Cstar) / P ≤ C0 / P := div_le_div_of_nonneg_right (by linarith) hP.le
    linarith

/-- (iii) With its original rule (cost 0, targeting probability `π_T`) and `ρ0`, the group adopts `ρ0` whenever
`π_T > α + C₀/P`. -/
theorem hiding_adopt (piT C0 α P : ℝ) (hP : 0 < P) (h : α + C0 / P < piT) : C0 + P * α < 0 + P * piT := by
  have : C0 / P < piT - α := by linarith
  rw [div_lt_iff₀ hP] at this
  linarith

/-- (iii) If `π_T → 1` and `P(1 - α) > C₀`, the group hides for all large `T`. -/
theorem hiding_eventually (piT : ℕ → ℝ) (C0 α P : ℝ) (hP : 0 < P) (hlim : Tendsto piT atTop (nhds 1))
    (hstakes : C0 < P * (1 - α)) : ∀ᶠ T in atTop, α + C0 / P < piT T := by
  have hlt : α + C0 / P < 1 := by
    have : C0 / P < 1 - α := by rw [div_lt_iff₀ hP]; linarith
    linarith
  exact hlim.eventually (lt_mem_nhds hlt)

/-! ### Corollary `cor:robustuniform` -/

/-- Under relabeling, halting label `F` removes `H (σ F)`; for every relabeling this is at least the smallest
contribution. -/
theorem halt_guarantee {ι : Type*} [Fintype ι] [Nonempty ι] (H : ι → ℝ) (F : ι) (σ : Equiv.Perm ι) :
    Finset.univ.inf' Finset.univ_nonempty H ≤ H (σ F) :=
  Finset.inf'_le _ (Finset.mem_univ _)

/-- ... and some relabeling attains it, so the smallest contribution is exactly what a halt guarantees. -/
theorem halt_guarantee_attained {ι : Type*} [Fintype ι] [Nonempty ι] [DecidableEq ι] (H : ι → ℝ) (F : ι) :
    ∃ σ : Equiv.Perm ι, H (σ F) = Finset.univ.inf' Finset.univ_nonempty H := by
  obtain ⟨c, -, hc⟩ := Finset.exists_mem_eq_inf' Finset.univ_nonempty H
  exact ⟨Equiv.swap F c, by simp [hc]⟩

/-- A uniform cut to `θ = (s̄ - a)/(S - a)` brings the budget exactly to the ceiling, for every composition with
budget `S`. -/
theorem uniform_exact (a S sbar : ℝ) (hS : a < S) : a + (sbar - a) / (S - a) * (S - a) = sbar := by
  have : S - a ≠ 0 := by linarith
  field_simp
  ring

/-- No policy that meets the ceiling removes less feedback than `S - s̄`, which is what the uniform cut removes. -/
theorem uniform_minimal_removal (S sbar removed : ℝ) (hmeet : S - removed ≤ sbar) : S - sbar ≤ removed := by
  linarith

end Paper1Revision8
