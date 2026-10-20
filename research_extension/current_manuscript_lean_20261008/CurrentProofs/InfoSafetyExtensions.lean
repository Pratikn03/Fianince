import Mathlib

/-!
# Information-safety extensions of Paper 2 and the October 2026 hardening results (Papers 1 and 2)

Machine-checked cores of: Proposition `prop:twoworld`, the corrected quantity gate, Theorem `thm:robustguard`,
Proposition `prop:venue`, Theorem `thm:venuebb` (given the floating-point enclosure property as a hypothesis),
Lemma `lem:certnum` (weak duality; the Hermite sign condition is not formalized), Theorem `thm:certcost` (i)
(deterministic decay and tail), Theorem `thm:forward` (one step), Proposition `prop:hotelling` (iii) and
Proposition `prop:probe` (deterministic cores; the probability statements are not formalized), and the hardening results
listed in section `IS_Hardening`. Every declaration is prefixed `is_`. Coverage tags are in `COVERAGE.md`.
-/

namespace CurrentMM
open Finset

section IS_TwoWorld
/-!
# Proposition `prop:twoworld` (Paper 2): the two-world capacity-loss bound

Finite observation spaces. Data `ω` are drawn from `p0` (world 0, safe capacity `v0`) or from `p1` (world 1, safe capacity
`v1 ≥ v0`). A data-driven admission rule `A : Ω → ℝ` never exceeds `v1`. Total variation is DEFINED as the largest
discrepancy over events (not assumed); the Markov step is PROVED. If the rule admits more than `v0` in world 0 with
probability at most `β`, then in world 1 it gives up at least `(v1 - v0) (1 - β - TV)₊` in expectation. The bound is
attained when the two worlds produce the same data.
-/

open Finset



variable {Ω : Type*} [Fintype Ω] [DecidableEq Ω]

/-- Probability of an event under a weight function. -/
def is_prob (p : Ω → ℝ) (E : Finset Ω) : ℝ := ∑ ω ∈ E, p ω

/-- Expectation under a weight function. -/
def is_expect (p : Ω → ℝ) (f : Ω → ℝ) : ℝ := ∑ ω, p ω * f ω

/-- Total variation distance: the largest discrepancy between the two laws over all events. -/
noncomputable def is_tv (p0 p1 : Ω → ℝ) : ℝ :=
  (Finset.univ : Finset (Finset Ω)).sup' ⟨∅, Finset.mem_univ _⟩ (fun E => |is_prob p0 E - is_prob p1 E|)

lemma is_prob_sub_le_tv (p0 p1 : Ω → ℝ) (E : Finset Ω) : is_prob p0 E - is_prob p1 E ≤ is_tv p0 p1 :=
  (le_abs_self _).trans (Finset.le_sup' (fun E => |is_prob p0 E - is_prob p1 E|) (Finset.mem_univ E))

lemma is_prob_filter_add_not (p : Ω → ℝ) (P : Ω → Prop) [DecidablePred P] :
    is_prob p (univ.filter P) + is_prob p (univ.filter (fun ω => ¬ P ω)) = ∑ ω, p ω := by
  unfold is_prob
  exact Finset.sum_filter_add_sum_filter_not univ P p

/-- **Proposition `prop:twoworld`.** -/
theorem is_two_world_capacity_loss (p0 p1 : Ω → ℝ) (hp0 : ∑ ω, p0 ω = 1) (hp1 : ∀ ω, 0 ≤ p1 ω)
    (A : Ω → ℝ) (v0 v1 β : ℝ) (hv : v0 ≤ v1) (hA : ∀ ω, A ω ≤ v1)
    (hsafe : is_prob p0 (univ.filter (fun ω => v0 < A ω)) ≤ β) :
    (v1 - v0) * max 0 (1 - β - is_tv p0 p1) ≤ is_expect p1 (fun ω => v1 - A ω) := by
  classical
  set E := univ.filter (fun ω => ¬ (v0 < A ω)) with hE
  -- world 0 puts mass at least 1 - β on E
  have h0E : 1 - β ≤ is_prob p0 E := by
    have := is_prob_filter_add_not p0 (fun ω => v0 < A ω)
    linarith
  -- world 1 puts mass at least 1 - β - TV on E
  have h1E : 1 - β - is_tv p0 p1 ≤ is_prob p1 E := by
    have := is_prob_sub_le_tv p0 p1 E
    linarith
  -- Markov step: v1 - A ≥ 0 everywhere and ≥ v1 - v0 on E
  have hmarkov : (v1 - v0) * is_prob p1 E ≤ is_expect p1 (fun ω => v1 - A ω) := by
    unfold is_expect is_prob
    rw [Finset.mul_sum]
    calc ∑ ω ∈ E, (v1 - v0) * p1 ω ≤ ∑ ω ∈ E, p1 ω * (v1 - A ω) := by
            apply Finset.sum_le_sum
            intro ω hω
            have hle : A ω ≤ v0 := by
              simp only [hE, Finset.mem_filter, Finset.mem_univ, true_and, not_lt] at hω
              exact hω
            nlinarith [hp1 ω]
      _ ≤ ∑ ω, p1 ω * (v1 - A ω) := by
            apply Finset.sum_le_sum_of_subset_of_nonneg (Finset.subset_univ E)
            intro ω _ _
            exact mul_nonneg (hp1 ω) (by linarith [hA ω])
  have hexp_nn : 0 ≤ is_expect p1 (fun ω => v1 - A ω) := by
    unfold is_expect
    exact Finset.sum_nonneg (fun ω _ => mul_nonneg (hp1 ω) (by linarith [hA ω]))
  rcases le_total (1 - β - is_tv p0 p1) 0 with h | h
  · rw [max_eq_left h]; simpa using hexp_nn
  · rw [max_eq_right h]
    calc (v1 - v0) * (1 - β - is_tv p0 p1) ≤ (v1 - v0) * is_prob p1 E :=
          mul_le_mul_of_nonneg_left h1E (by linarith)
      _ ≤ _ := hmarkov

/-- **Attainment.** With identical data (`TV = 0`), the randomized rule that admits `v1` with probability `β` and `v0`
otherwise satisfies the safety constraint and loses exactly `(1 - β)(v1 - v0)`. -/
theorem is_two_world_attained (v0 v1 β : ℝ) (hβ0 : 0 ≤ β) (hβ1 : β ≤ 1) (hv : v0 < v1) :
    let p : Bool → ℝ := fun b => if b then β else 1 - β
    let A : Bool → ℝ := fun b => if b then v1 else v0
    is_tv p p = 0 ∧ is_prob p (univ.filter (fun ω => v0 < A ω)) = β ∧
      is_expect p (fun ω => v1 - A ω) = (v1 - v0) * max 0 (1 - β - is_tv p p) := by
  intro p A
  have htv : is_tv p p = 0 := by
    unfold is_tv
    apply le_antisymm
    · apply Finset.sup'_le; intro E _; simp
    · exact (abs_nonneg _).trans (Finset.le_sup' (fun E => |is_prob p E - is_prob p E|) (Finset.mem_univ ∅))
  refine ⟨htv, ?_, ?_⟩
  · have : univ.filter (fun ω : Bool => v0 < A ω) = {true} := by
      ext b; cases b <;> simp [A, hv, lt_irrefl]
    rw [this]; simp [is_prob, p]
  · rw [htv, sub_zero, max_eq_right (by linarith)]
    simp [is_expect, p, A, Fintype.sum_bool] <;> ring

end IS_TwoWorld

section IS_Gate
/-!
# The corrected quantity gate (Paper 2, Section 6.1; blueprint D1)

For a linear market with price impulse coefficients `g k` and a drift `d` from the current state, the worst price excursion
over shock paths with a per-period bound `|v k| ≤ V` is `|d| + V ∑ |g k|`, attained by aligning every shock's sign with the
drift; with a total budget `∑ |v k| ≤ W` (and no drift) it is `W max |g k|`, attained at a vertex. The peak gain
`max |g k|` is therefore the right allowance only for a single shock, not for repeated per-period trading.
-/

open Finset



variable {n : ℕ}

/-- Per-period bound: `|d + ∑ g v| ≤ |d| + V ∑ |g|` for every admissible path. -/
theorem is_per_period_upper (g v : Fin n → ℝ) (d V : ℝ) (hv : ∀ k, |v k| ≤ V) :
    |d + ∑ k, g k * v k| ≤ |d| + V * ∑ k, |g k| := by
  calc |d + ∑ k, g k * v k| ≤ |d| + |∑ k, g k * v k| := abs_add_le _ _
    _ ≤ |d| + ∑ k, |g k * v k| := by gcongr; exact Finset.abs_sum_le_sum_abs _ _
    _ ≤ |d| + V * ∑ k, |g k| := by
        rw [Finset.mul_sum]; gcongr with k
        rw [abs_mul, mul_comm V]
        exact mul_le_mul_of_nonneg_left (hv k) (abs_nonneg _)

/-- Sign of the drift (`1` when `d ≥ 0`). -/
noncomputable def is_driftSign (d : ℝ) : ℝ := if 0 ≤ d then 1 else -1

/-- The shock path that attains the per-period bound: each shock has the sign of `is_driftSign d * g k`. -/
noncomputable def is_alignedPath (g : Fin n → ℝ) (d V : ℝ) : Fin n → ℝ :=
  fun k => if 0 ≤ is_driftSign d * g k then V else -V

lemma is_aligned_term (g : Fin n → ℝ) (d V : ℝ) (k : Fin n) :
    g k * is_alignedPath g d V k = is_driftSign d * (V * |g k|) := by
  unfold is_alignedPath is_driftSign
  by_cases hd : 0 ≤ d
  · rw [if_pos hd, one_mul, one_mul]
    by_cases hg : 0 ≤ g k
    · rw [if_pos hg, abs_of_nonneg hg]; ring
    · rw [if_neg hg, abs_of_neg (not_le.mp hg)]; ring
  · rw [if_neg hd]
    by_cases hg : 0 ≤ -1 * g k
    · rw [if_pos hg, abs_of_nonpos (by linarith)]; ring
    · rw [if_neg hg, abs_of_pos (by linarith)]; ring

/-- **Attainment.** The aligned path is admissible and its excursion equals `|d| + V ∑ |g|`. -/
theorem is_per_period_attained (g : Fin n → ℝ) (d V : ℝ) (hV : 0 ≤ V) :
    (∀ k, |is_alignedPath g d V k| ≤ V) ∧
      |d + ∑ k, g k * is_alignedPath g d V k| = |d| + V * ∑ k, |g k| := by
  refine ⟨fun k => by unfold is_alignedPath; split_ifs <;> simp [abs_of_nonneg hV], ?_⟩
  have hsum : ∑ k, g k * is_alignedPath g d V k = is_driftSign d * (V * ∑ k, |g k|) := by
    rw [Finset.mul_sum, Finset.mul_sum]
    exact Finset.sum_congr rfl (fun k _ => by rw [is_aligned_term]; try ring)
  have hX : 0 ≤ V * ∑ k, |g k| := mul_nonneg hV (Finset.sum_nonneg (fun k _ => abs_nonneg _))
  rw [hsum]
  unfold is_driftSign
  by_cases hd : 0 ≤ d
  · rw [if_pos hd, one_mul, abs_of_nonneg (by linarith), abs_of_nonneg hd]
  · push_neg at hd
    rw [if_neg (not_le.mpr hd), abs_of_neg hd, abs_of_nonpos (by linarith)]; ring

/-- Total-budget bound: with `∑ |v k| ≤ W`, `|∑ g v| ≤ W · max |g|` (here `M` is any bound on every `|g k|`). -/
theorem is_budget_upper (g v : Fin n → ℝ) (W M : ℝ) (hM : ∀ k, |g k| ≤ M) (hW : ∑ k, |v k| ≤ W) (hM0 : 0 ≤ M) :
    |∑ k, g k * v k| ≤ W * M := by
  calc |∑ k, g k * v k| ≤ ∑ k, |g k * v k| := Finset.abs_sum_le_sum_abs _ _
    _ ≤ ∑ k, M * |v k| := by
        gcongr with k; rw [abs_mul]; exact mul_le_mul_of_nonneg_right (hM k) (abs_nonneg _)
    _ = M * ∑ k, |v k| := by rw [Finset.mul_sum]
    _ ≤ M * W := mul_le_mul_of_nonneg_left hW hM0
    _ = W * M := mul_comm _ _

/-- **Attainment at a vertex.** Putting the whole budget on the coefficient of largest magnitude attains `W |g j|`. -/
theorem is_budget_attained (g : Fin n → ℝ) (W : ℝ) (hW : 0 ≤ W) (j : Fin n) :
    let v : Fin n → ℝ := fun k => if k = j then W else 0
    (∑ k, |v k| = W) ∧ |∑ k, g k * v k| = W * |g j| := by
  intro v
  have habs : ∀ x, |(if x = j then W else 0)| = if x = j then W else 0 := fun x => by
    split_ifs <;> simp [abs_of_nonneg hW]
  constructor
  · simp [v, habs]
  · simp [v, abs_mul, abs_of_nonneg hW, mul_comm]

/-- **The peak gain understates the repeated-shock risk.** If two coefficients are nonzero, the per-period worst case
`V ∑ |g|` strictly exceeds the single-shock allowance `V max |g|` (stated with any coefficient `j`). -/
theorem is_peak_understates (g : Fin n → ℝ) (V : ℝ) (hV : 0 < V) (i j : Fin n) (hij : i ≠ j) (hi : g i ≠ 0) :
    V * |g j| < V * ∑ k, |g k| := by
  apply mul_lt_mul_of_pos_left _ hV
  have hsub : ({i, j} : Finset (Fin n)) ⊆ Finset.univ := Finset.subset_univ _
  have h2 : ∑ k ∈ ({i, j} : Finset (Fin n)), |g k| ≤ ∑ k, |g k| :=
    Finset.sum_le_sum_of_subset_of_nonneg hsub (fun k _ _ => abs_nonneg _)
  rw [Finset.sum_pair hij] at h2
  have : 0 < |g i| := abs_pos.mpr hi
  linarith

end IS_Gate

section IS_RobustGuard
/-!
# Theorem `thm:robustguard` (i)-(iv), Theorem `thm:disclosure` (i)-(ii) and Lemma `lem:is_sound` (Paper 2)

Cohort economy with price persistence `a`, impact `κ > 0`, feedback weight `Φ ≥ 0` and admission level `α`:
the summed response is `S(α, Φ) = κ / (1 - a - κ α Φ)`. With exposure `L = |I| ū > 0` and budget `B > 0`, a level is safe
when the denominator is positive and `L S ≤ B`; we write this without division as `0 < D ∧ L κ ≤ B D`.
The guard admits the levels that are safe for every `Φ ∈ [0, Φ⁺]`.
-/



/-- Denominator of the summed response. -/
def is_den (a κ α Φ : ℝ) : ℝ := 1 - a - κ * α * Φ

/-- A level is safe for one economy: stable and worst-case loss within budget (`L κ / D ≤ B`). -/
def is_Safe (a κ L B α Φ : ℝ) : Prop := 0 < is_den a κ α Φ ∧ L * κ ≤ B * is_den a κ α Φ

/-- The division form and the multiplicative form agree. -/
lemma is_safe_iff_div (a κ L B α Φ : ℝ) (hD : 0 < is_den a κ α Φ) (hB : 0 < B) :
    is_Safe a κ L B α Φ ↔ L * κ / is_den a κ α Φ ≤ B := by
  unfold is_Safe; rw [div_le_iff₀ hD]; constructor
  · rintro ⟨_, h⟩; linarith
  · intro h; exact ⟨hD, by linarith⟩

/-- Robustly safe: safe for every feedback weight in `[0, Φ⁺]`. -/
def is_RobustSafe (a κ L B Φp α : ℝ) : Prop := ∀ Φ ∈ Set.Icc (0 : ℝ) Φp, is_Safe a κ L B α Φ

/-- The capacity is_margin `c_I = 1 - a - κ L / B`. -/
noncomputable def is_cI (a κ L B : ℝ) : ℝ := 1 - a - κ * L / B

/-- For a nonnegative level, robust safety is exactly `κ α Φ⁺ ≤ c_I`. -/
lemma is_robustSafe_iff (a κ L B Φp α : ℝ) (hκ : 0 < κ) (hL : 0 < L) (hB : 0 < B) (hΦ : 0 ≤ Φp) (hα : 0 ≤ α) :
    is_RobustSafe a κ L B Φp α ↔ κ * α * Φp ≤ is_cI a κ L B := by
  unfold is_RobustSafe is_Safe is_den is_cI
  have hLκB : κ * L / B * B = L * κ := by field_simp
  constructor
  · intro h
    obtain ⟨_, h2⟩ := h Φp ⟨hΦ, le_refl _⟩
    have : κ * L / B ≤ 1 - a - κ * α * Φp := by
      rw [div_le_iff₀ hB]; linarith
    linarith
  · intro h Φ hΦ'
    have hmono : κ * α * Φ ≤ κ * α * Φp := mul_le_mul_of_nonneg_left hΦ'.2 (by positivity)
    have hpos : 0 < κ * L / B := by positivity
    refine ⟨by linarith, ?_⟩
    have : κ * L / B ≤ 1 - a - κ * α * Φ := by linarith
    have := mul_le_mul_of_nonneg_right this hB.le
    rw [hLκB] at this; linarith

/-- The guard level `α* = min 1 (c_I / (κ Φ⁺))`. -/
noncomputable def is_alphaStar (a κ L B Φp : ℝ) : ℝ := min 1 (is_cI a κ L B / (κ * Φp))

/-- **Theorem `thm:robustguard` (i) and (iii): closed form, interval and maximality.** If `c_I ≥ 0` the robustly safe levels
in `[0,1]` are exactly the interval `[0, α*]`; in particular `α*` is the greatest robustly safe level. -/
theorem is_robust_safe_set_eq (a κ L B Φp : ℝ) (hκ : 0 < κ) (hL : 0 < L) (hB : 0 < B) (hΦ : 0 < Φp)
    (hc : 0 ≤ is_cI a κ L B) :
    {α : ℝ | α ∈ Set.Icc (0 : ℝ) 1 ∧ is_RobustSafe a κ L B Φp α} = Set.Icc 0 (is_alphaStar a κ L B Φp) := by
  ext α
  simp only [Set.mem_setOf_eq, Set.mem_Icc, is_alphaStar, le_min_iff]
  constructor
  · rintro ⟨⟨h0, h1⟩, hs⟩
    refine ⟨h0, h1, ?_⟩
    rw [is_robustSafe_iff a κ L B Φp α hκ hL hB hΦ.le h0] at hs
    rw [le_div_iff₀ (by positivity)]; linarith
  · rintro ⟨h0, h1, h2⟩
    refine ⟨⟨h0, h1⟩, ?_⟩
    rw [is_robustSafe_iff a κ L B Φp α hκ hL hB hΦ.le h0]
    rw [le_div_iff₀ (by positivity)] at h2; linarith

theorem is_alphaStar_isGreatest (a κ L B Φp : ℝ) (hκ : 0 < κ) (hL : 0 < L) (hB : 0 < B) (hΦ : 0 < Φp)
    (hc : 0 ≤ is_cI a κ L B) :
    IsGreatest {α : ℝ | α ∈ Set.Icc (0 : ℝ) 1 ∧ is_RobustSafe a κ L B Φp α} (is_alphaStar a κ L B Φp) := by
  rw [is_robust_safe_set_eq a κ L B Φp hκ hL hB hΦ hc]
  refine ⟨⟨?_, le_refl _⟩, fun x hx => hx.2⟩
  unfold is_alphaStar; exact le_min zero_le_one (div_nonneg hc (by positivity))

/-- **Theorem `thm:robustguard` (iv): infeasibility.** If `c_I < 0`, no admission level in `[0,1]` is safe for any
economy with nonnegative feedback, including `α = 0`: the guard must halt. -/
theorem is_infeasible_of_cI_neg (a κ L B α Φ : ℝ) (hκ : 0 < κ) (hL : 0 < L) (hB : 0 < B) (hα : 0 ≤ α) (hΦ : 0 ≤ Φ)
    (hc : is_cI a κ L B < 0) : ¬ is_Safe a κ L B α Φ := by
  unfold is_Safe is_den
  unfold is_cI at hc
  rintro ⟨hD, h⟩
  have hfb : 0 ≤ κ * α * Φ := by positivity
  have : κ * L / B * B = L * κ := by field_simp
  have h3 : B * (1 - a - κ * α * Φ) ≤ B * (1 - a) := by nlinarith
  have h4 : B * (1 - a) < κ * L / B * B := by nlinarith
  linarith

/-- **Theorem `thm:robustguard` (ii) / Lemma `lem:is_sound`: soundness.** If the true feedback lies in `[0, Φ⁺]` (the event
that the certificate covers), every admitted level is safe for the true economy. -/
theorem is_sound (a κ L B Φp Φtrue α : ℝ) (hcov : Φtrue ∈ Set.Icc (0 : ℝ) Φp) (h : is_RobustSafe a κ L B Φp α) :
    is_Safe a κ L B α Φtrue := h Φtrue hcov

/-- **Theorem `thm:disclosure` (i): disclosure never lowers safe capacity.** A smaller certified bound admits more. -/
theorem is_disclosure_monotone (a κ L B Φtag Φpub α : ℝ) (hle : Φtag ≤ Φpub) (h : is_RobustSafe a κ L B Φpub α) :
    is_RobustSafe a κ L B Φtag α := fun Φ hΦ => h Φ ⟨hΦ.1, hΦ.2.trans hle⟩

/-- **Theorem `thm:disclosure` (ii): strictness.** When the public guard binds (`α*_pub < 1`, `c_I > 0`), excluding the
extremal economy (`Φ_tag < Φ_pub`) strictly raises capacity. -/
theorem is_disclosure_strict (a κ L B Φtag Φpub : ℝ) (hκ : 0 < κ) (hc : 0 < is_cI a κ L B) (h0 : 0 < Φtag)
    (hlt : Φtag < Φpub) (hbind : is_cI a κ L B / (κ * Φpub) < 1) :
    is_alphaStar a κ L B Φpub < is_alphaStar a κ L B Φtag := by
  unfold is_alphaStar
  rw [min_eq_right hbind.le]
  have h1 : is_cI a κ L B / (κ * Φpub) < is_cI a κ L B / (κ * Φtag) :=
    div_lt_div_of_pos_left hc (by positivity) (by nlinarith)
  exact lt_min hbind h1

/-- Abstract form of Theorem `thm:disclosure` (i): for any risk function, robust safety over a larger compatible set
implies robust safety over a smaller one. -/
theorem is_robust_safe_antitone {Θ U : Type*} (R : Θ → U → ℝ) (B : ℝ) (Θsmall Θbig : Set Θ) (hsub : Θsmall ⊆ Θbig)
    (u : U) (h : ∀ θ ∈ Θbig, R θ u ≤ B) : ∀ θ ∈ Θsmall, R θ u ≤ B := fun θ hθ => h θ (hsub hθ)

end IS_RobustGuard

section IS_Venue
/-!
# Proposition `prop:venue` (Paper 2, Section 6.6): admission that changes the dynamics

Admitting a fraction `α` adds feedback `α Φ`, deepens the book (impact `κ₀ / (1 + δ α)`) and speeds reversion
(`1 - a₀ + ρ α`). The summed response is `κ₀ / D α` with `D α = (1 + δ α)(1 - a₀ + ρ α) - κ₀ Φ α`, and a level is safe iff
`D α ≥ τ` with `τ = κ₀ L / B`, i.e. iff the is_margin `D α - κ₀ L / B ≥ 0`.
-/



/-- `D α`. -/
def is_Dv (κ0 a0 Φ δ ρ α : ℝ) : ℝ := (1 + δ * α) * (1 - a0 + ρ * α) - κ0 * Φ * α

/-- Safety is_margin `D α - κ₀ ℓ`, with `ℓ = L / B`. -/
def is_margin (κ0 a0 Φ δ ρ ℓ α : ℝ) : ℝ := is_Dv κ0 a0 Φ δ ρ α - κ0 * ℓ

/-- `D` is convex in `α` when `δ ρ ≥ 0`. -/
theorem is_Dv_convex (κ0 a0 Φ δ ρ x y t : ℝ) (hδρ : 0 ≤ δ * ρ) (ht0 : 0 ≤ t) (ht1 : t ≤ 1) :
    is_Dv κ0 a0 Φ δ ρ (t * x + (1 - t) * y) ≤ t * is_Dv κ0 a0 Φ δ ρ x + (1 - t) * is_Dv κ0 a0 Φ δ ρ y := by
  unfold is_Dv
  have key : t * ((1 + δ * x) * (1 - a0 + ρ * x) - κ0 * Φ * x) + (1 - t) * ((1 + δ * y) * (1 - a0 + ρ * y) - κ0 * Φ * y)
      - ((1 + δ * (t * x + (1 - t) * y)) * (1 - a0 + ρ * (t * x + (1 - t) * y)) - κ0 * Φ * (t * x + (1 - t) * y))
      = (δ * ρ) * (t * (1 - t)) * (x - y) ^ 2 := by ring
  have : 0 ≤ (δ * ρ) * (t * (1 - t)) * (x - y) ^ 2 := by
    apply mul_nonneg (mul_nonneg hδρ (mul_nonneg ht0 (by linarith))) (sq_nonneg _)
  linarith

/-- **Proposition `prop:venue` (i).** The unsafe levels form an interval: if two levels are unsafe, so is every level
between them. Hence the safe levels in `[0,1]` are `[0,1]` minus at most one interval. -/
theorem is_unsafe_between (κ0 a0 Φ δ ρ ℓ x y z : ℝ) (hδρ : 0 ≤ δ * ρ) (hxy : x ≤ y) (hyz : y ≤ z)
    (hx : is_margin κ0 a0 Φ δ ρ ℓ x < 0) (hz : is_margin κ0 a0 Φ δ ρ ℓ z < 0) : is_margin κ0 a0 Φ δ ρ ℓ y < 0 := by
  unfold is_margin at *
  rcases eq_or_lt_of_le (hxy.trans hyz) with hxz | hxz
  · have : y = x := le_antisymm (hxz ▸ hyz) hxy
    rw [this]; exact hx
  · set t := (z - y) / (z - x) with ht
    have hzx : 0 < z - x := by linarith
    have ht0 : 0 ≤ t := div_nonneg (by linarith) hzx.le
    have ht1 : t ≤ 1 := by rw [div_le_one hzx]; linarith
    have hy : y = t * x + (1 - t) * z := by
      rw [ht]; field_simp <;> ring
    have hc := is_Dv_convex κ0 a0 Φ δ ρ x z t hδρ ht0 ht1
    rw [← hy] at hc
    have hm := max_lt hx hz
    have h1 := mul_le_mul_of_nonneg_left
      (le_max_left (is_Dv κ0 a0 Φ δ ρ x - κ0 * ℓ) (is_Dv κ0 a0 Φ δ ρ z - κ0 * ℓ)) ht0
    have h2 := mul_le_mul_of_nonneg_left
      (le_max_right (is_Dv κ0 a0 Φ δ ρ x - κ0 * ℓ) (is_Dv κ0 a0 Φ δ ρ z - κ0 * ℓ)) (sub_nonneg.mpr ht1)
    nlinarith

/-- **Proposition `prop:venue` (ii).** For `α ≥ 0` the is_margin is smallest at the corner
`(κ₀⁺, a₀⁺, Φ⁺, δ⁻, ρ⁻)` of the parameter box, the same corner for every `α`. -/
theorem is_worst_corner (κ0 a0 Φ δ ρ κp ap Φp δm ρm ℓ α : ℝ) (hα : 0 ≤ α) (hℓ : 0 ≤ ℓ)
    (hκ : κ0 ≤ κp) (ha : a0 ≤ ap) (hΦ : Φ ≤ Φp) (hδ : δm ≤ δ) (hρ : ρm ≤ ρ)
    (hΦ0 : 0 ≤ Φ) (hκ0 : 0 ≤ κ0) (hδm : 0 ≤ δm) (hρm : 0 ≤ ρm) (hap : ap < 1) :
    is_margin κp ap Φp δm ρm ℓ α ≤ is_margin κ0 a0 Φ δ ρ ℓ α := by
  unfold is_margin is_Dv
  have h1 : (1 + δm * α) * (1 - ap + ρm * α) ≤ (1 + δ * α) * (1 - a0 + ρ * α) := by
    apply mul_le_mul
    · nlinarith
    · nlinarith
    · nlinarith
    · nlinarith
  have h2 : κ0 * Φ * α ≤ κp * Φp * α := by
    apply mul_le_mul_of_nonneg_right _ hα
    exact mul_le_mul hκ hΦ hΦ0 (hκ0.trans hκ)
  have h3 : κ0 * ℓ ≤ κp * ℓ := mul_le_mul_of_nonneg_right hκ hℓ
  linarith

/-- **Proposition `prop:venue` (iii), the example of Section 6.6.** At the worst corner of the box
`κ₀ ∈ [0.98, 1.02]`, `a₀ ∈ [0.58, 0.60]`, `Φ ∈ [2.3, 2.4]`, `δ ∈ [2.9, 3.1]`, `ρ ∈ [0.58, 0.62]` with `L/B = 0.37`,
the levels `0` and `1` are safe while `0.2` is not: the robust safe set is not an interval, so certifying the largest safe
level (`1`) and accepting every level below it would accept an unsafe level. -/
theorem is_venue_example :
    0 ≤ is_margin 1.02 0.60 2.4 2.9 0.58 0.37 0 ∧ is_margin 1.02 0.60 2.4 2.9 0.58 0.37 0.2 < 0 ∧
      0 ≤ is_margin 1.02 0.60 2.4 2.9 0.58 0.37 1 := by
  unfold is_margin is_Dv; norm_num

/-- The example's safe set has two components: every economy of the box is safe at `0` and `1`, and the worst one is
unsafe at `0.2`. -/
theorem is_venue_example_box (κ0 a0 Φ δ ρ : ℝ) (hκ : 0.98 ≤ κ0 ∧ κ0 ≤ 1.02) (ha : 0.58 ≤ a0 ∧ a0 ≤ 0.60)
    (hΦ : 2.3 ≤ Φ ∧ Φ ≤ 2.4) (hδ : 2.9 ≤ δ ∧ δ ≤ 3.1) (hρ : 0.58 ≤ ρ ∧ ρ ≤ 0.62) :
    0 ≤ is_margin κ0 a0 Φ δ ρ 0.37 0 ∧ 0 ≤ is_margin κ0 a0 Φ δ ρ 0.37 1 := by
  have c0 := is_worst_corner κ0 a0 Φ δ ρ 1.02 0.60 2.4 2.9 0.58 0.37 0 le_rfl (by norm_num) hκ.2 ha.2 hΦ.2 hδ.1 hρ.1
    (by linarith) (by linarith) (by norm_num) (by norm_num) (by norm_num)
  have c1 := is_worst_corner κ0 a0 Φ δ ρ 1.02 0.60 2.4 2.9 0.58 0.37 1 zero_le_one (by norm_num) hκ.2 ha.2 hΦ.2 hδ.1 hρ.1
    (by linarith) (by linarith) (by norm_num) (by norm_num) (by norm_num)
  obtain ⟨e0, -, e1⟩ := is_venue_example
  exact ⟨e0.trans c0, e1.trans c1⟩

end IS_Venue

section IS_VenueBB
/-!
# Theorem `thm:venuebb` (Paper 2, Section 6.6): what the branch-and-bound output certifies

The certified computation encloses the summed response `S α θ` over boxes of levels and parameters in interval arithmetic
with outward rounding. That enclosures contain the exact values is a property of IEEE floating point (Rump 2010) and is
taken here as the hypothesis `hencl`; everything that follows from it is proved:

* (i) a level box classified safe (upper enclosure within budget on every part of a cover of `Θ`) is safe for every
  economy in `Θ`; a box classified unsafe (lower enclosure above budget at one economy) is unsafe for that economy;
* (ii) the robust safe set is closed when each `S · θ` is continuous, so the largest safe level in `[0,1]` exists whenever
  some level is safe, and any certified-safe level is a lower bracket for it.
-/



variable {Θ : Type*}

/-- **(i) is_Safe classification is is_sound.** If `Θ` is covered by parts on each of which the enclosure's upper end is within
budget, every level in the box is safe for every economy. -/
theorem is_classify_safe_sound {ι : Type*} (S : ℝ → Θ → ℝ) (A : Set ℝ) (Θs : Set Θ) (part : ι → Set Θ) (U : ι → ℝ)
    (B : ℝ) (hcover : Θs ⊆ ⋃ i, part i) (hencl : ∀ i, ∀ α ∈ A, ∀ θ ∈ part i, S α θ ≤ U i) (hU : ∀ i, U i ≤ B) :
    ∀ α ∈ A, ∀ θ ∈ Θs, S α θ ≤ B := by
  intro α hα θ hθ
  obtain ⟨i, hi⟩ := Set.mem_iUnion.mp (hcover hθ)
  exact (hencl i α hα θ hi).trans (hU i)

/-- **(i) Unsafe classification is is_sound.** A lower enclosure above budget at one economy of `Θ` makes every level in the
box unsafe for that economy. -/
theorem is_classify_unsafe_sound (S : ℝ → Θ → ℝ) (A : Set ℝ) (Θs : Set Θ) (θj : Θ) (hθj : θj ∈ Θs) (L B : ℝ)
    (hencl : ∀ α ∈ A, L ≤ S α θj) (hL : B < L) : ∀ α ∈ A, ∃ θ ∈ Θs, B < S α θ :=
  fun α hα => ⟨θj, hθj, hL.trans_le (hencl α hα)⟩

/-- The robust safe set `{α | ∀ θ ∈ Θ, S α θ ≤ B}`. -/
def is_robustSafeSet (S : ℝ → Θ → ℝ) (Θs : Set Θ) (B : ℝ) : Set ℝ := {α | ∀ θ ∈ Θs, S α θ ≤ B}

/-- **(ii) Closedness.** -/
theorem is_robustSafeSet_closed (S : ℝ → Θ → ℝ) (Θs : Set Θ) (B : ℝ) (hcont : ∀ θ, Continuous fun α => S α θ) :
    IsClosed (is_robustSafeSet S Θs B) := by
  have : is_robustSafeSet S Θs B = ⋂ θ ∈ Θs, {α | S α θ ≤ B} := by
    ext α; simp [is_robustSafeSet]
  rw [this]
  exact isClosed_biInter (fun θ _ => isClosed_le (hcont θ) continuous_const)

/-- **(ii) Existence and bracketing of the largest safe level.** If some level in `[0,1]` is safe, a greatest safe level
in `[0,1]` exists, and every certified-safe level lies below it. -/
theorem is_largest_safe_exists (S : ℝ → Θ → ℝ) (Θs : Set Θ) (B : ℝ) (hcont : ∀ θ, Continuous fun α => S α θ)
    (hne : (Set.Icc (0 : ℝ) 1 ∩ is_robustSafeSet S Θs B).Nonempty) :
    ∃ αmax, IsGreatest (Set.Icc (0 : ℝ) 1 ∩ is_robustSafeSet S Θs B) αmax ∧
      ∀ α ∈ Set.Icc (0 : ℝ) 1 ∩ is_robustSafeSet S Θs B, α ≤ αmax := by
  have hK : IsCompact (Set.Icc (0 : ℝ) 1 ∩ is_robustSafeSet S Θs B) :=
    isCompact_Icc.inter_right (is_robustSafeSet_closed S Θs B hcont)
  obtain ⟨αmax, hmax⟩ := hK.exists_isGreatest hne
  exact ⟨αmax, hmax, hmax.2⟩

end IS_VenueBB

section IS_WeakDuality
/-!
# Lemma `lem:certnum` (Paper 2), weak-duality part

A positive cohort economy has a merged measure with finitely many atoms: weights `w i ≥ 0` at memory rates `x i ∈ [0, r̄]`.
The window identifies its moments `k j = ∑ w i x i ^ j` for `j < n`. For any polynomial `p(r) = ∑_{j<n} c j r ^ j`:
`∑ c j k j = ∑ w i p (x i)`. Hence if `p ≥ f` on `[0, r̄]`, every compatible economy has `Φ = ∑ w i f (x i) ≤ ∑ c j k j`,
and if `p ≤ f`, `Φ ≥ ∑ c j k j`. These are the bounds that the interval-arithmetic verification certifies.
-/

open Finset



variable {m n : ℕ}

/-- Moments of an atomic measure. -/
def is_moment (w x : Fin m → ℝ) (j : ℕ) : ℝ := ∑ i, w i * x i ^ j

/-- Polynomial with coefficients `c` (degree `< n`). -/
def is_poly (c : Fin n → ℝ) (r : ℝ) : ℝ := ∑ j, c j * r ^ (j : ℕ)

/-- `∑ c j k j = ∫ p dM` for an atomic measure (exchange of finite sums). -/
theorem is_coeff_moment_eq (w x : Fin m → ℝ) (c : Fin n → ℝ) :
    ∑ j, c j * is_moment w x j = ∑ i, w i * is_poly c (x i) := by
  unfold is_moment is_poly
  simp_rw [Finset.mul_sum]
  rw [Finset.sum_comm]
  refine Finset.sum_congr rfl (fun i _ => Finset.sum_congr rfl (fun j _ => by ring))

/-- **Upper bound.** If `p ≥ f` on the support, `Φ ≤ ∑ c j k j`. -/
theorem is_upper_bound (w x : Fin m → ℝ) (c : Fin n → ℝ) (f : ℝ → ℝ) (rbar : ℝ)
    (hw : ∀ i, 0 ≤ w i) (hx : ∀ i, x i ∈ Set.Icc (0 : ℝ) rbar) (hp : ∀ r ∈ Set.Icc (0 : ℝ) rbar, f r ≤ is_poly c r) :
    ∑ i, w i * f (x i) ≤ ∑ j, c j * is_moment w x j := by
  rw [is_coeff_moment_eq]
  exact Finset.sum_le_sum (fun i _ => mul_le_mul_of_nonneg_left (hp _ (hx i)) (hw i))

/-- **Lower bound.** If `p ≤ f` on the support, `∑ c j k j ≤ Φ`. -/
theorem is_lower_bound (w x : Fin m → ℝ) (c : Fin n → ℝ) (f : ℝ → ℝ) (rbar : ℝ)
    (hw : ∀ i, 0 ≤ w i) (hx : ∀ i, x i ∈ Set.Icc (0 : ℝ) rbar) (hp : ∀ r ∈ Set.Icc (0 : ℝ) rbar, is_poly c r ≤ f r) :
    ∑ j, c j * is_moment w x j ≤ ∑ i, w i * f (x i) := by
  rw [is_coeff_moment_eq]
  exact Finset.sum_le_sum (fun i _ => mul_le_mul_of_nonneg_left (hp _ (hx i)) (hw i))

/-- **Slack.** Adding `s` to the constant coefficient raises the bound by `s k₀`; this is how the certified computation
turns a strict sign condition into a valid bound for the rounded polynomial. -/
theorem is_slack_shift (w x : Fin m → ℝ) (c : Fin n → ℝ) (f : ℝ → ℝ) (rbar s : ℝ)
    (hw : ∀ i, 0 ≤ w i) (hx : ∀ i, x i ∈ Set.Icc (0 : ℝ) rbar) (hp : ∀ r ∈ Set.Icc (0 : ℝ) rbar, f r ≤ is_poly c r + s) :
    ∑ i, w i * f (x i) ≤ ∑ j, c j * is_moment w x j + s * is_moment w x 0 := by
  have h1 : ∑ i, w i * f (x i) ≤ ∑ i, w i * (is_poly c (x i) + s) :=
    Finset.sum_le_sum (fun i _ => mul_le_mul_of_nonneg_left (hp _ (hx i)) (hw i))
  have h2 : ∑ i, w i * (is_poly c (x i) + s) = ∑ i, w i * is_poly c (x i) + s * is_moment w x 0 := by
    unfold is_moment; simp only [pow_zero, mul_one, mul_add, Finset.sum_add_distrib, Finset.mul_sum]
    congr 1; exact Finset.sum_congr rfl (fun i _ => by ring)
  rw [h2, ← is_coeff_moment_eq] at h1; exact h1

end IS_WeakDuality

section IS_Decay
/-!
# Theorem `thm:certcost` (i), the deterministic part (Paper 2)

For a positive cohort economy the stacked operator `J` is entrywise nonnegative, its price row sums to `a + κ Φ ≤ s̄` and
cohort row `i` sums to `1 - η_i (1 - a - κ Φ) ≤ λ̄ = 1 - (1 - r̄)(1 - s̄)` when `η_i ≥ 1 - r̄`. Then every coordinate of
`J^t b` is at most `κ λ̄^t` when the input `b` has entries in `[0, κ]`, so `h_t ≤ κ λ̄^t` and the tail after `T` periods
is at most `κ λ̄^T / (1 - λ̄)`.
-/

open Finset



/-- Cohort row sum bound: `1 - η (1 - a - κ Φ) ≤ 1 - (1 - r̄)(1 - s̄)` when `η ≥ 1 - r̄` and `a + κ Φ ≤ s̄ ≤ 1`. -/
theorem is_cohort_row_bound (η a κΦ rbar sbar : ℝ) (hη : 1 - rbar ≤ η) (hs : a + κΦ ≤ sbar) (hs1 : sbar ≤ 1)
    (hr : rbar ≤ 1) : 1 - η * (1 - a - κΦ) ≤ 1 - (1 - rbar) * (1 - sbar) := by
  have h1 : 0 ≤ 1 - sbar := by linarith
  have h2 : 1 - sbar ≤ 1 - a - κΦ := by linarith
  have h3 : 0 ≤ 1 - rbar := by linarith
  nlinarith [mul_le_mul hη h2 h1 (h3.trans hη)]

/-- Price row sum bound: `a + κ Φ ≤ λ̄`. -/
theorem is_price_row_bound (a κΦ rbar sbar : ℝ) (hs : a + κΦ ≤ sbar) (hs1 : sbar ≤ 1) (hr0 : 0 ≤ rbar) :
    a + κΦ ≤ 1 - (1 - rbar) * (1 - sbar) := by nlinarith

variable {n : ℕ}

/-- One application of a nonnegative operator with row sums at most `λ` maps `[0, M]^n` into `[0, λ M]^n`. -/
theorem is_step_bound (J : Fin n → Fin n → ℝ) (v : Fin n → ℝ) (lam M : ℝ) (hJ : ∀ i j, 0 ≤ J i j)
    (hrow : ∀ i, ∑ j, J i j ≤ lam) (hv0 : ∀ j, 0 ≤ v j) (hvM : ∀ j, v j ≤ M) (hM : 0 ≤ M) (i : Fin n) :
    0 ≤ ∑ j, J i j * v j ∧ ∑ j, J i j * v j ≤ lam * M := by
  refine ⟨Finset.sum_nonneg (fun j _ => mul_nonneg (hJ i j) (hv0 j)), ?_⟩
  calc ∑ j, J i j * v j ≤ ∑ j, J i j * M := Finset.sum_le_sum (fun j _ => mul_le_mul_of_nonneg_left (hvM j) (hJ i j))
    _ = (∑ j, J i j) * M := by rw [Finset.sum_mul]
    _ ≤ lam * M := mul_le_mul_of_nonneg_right (hrow i) hM

/-- Iterates of the operator. -/
def is_iter (J : Fin n → Fin n → ℝ) (b : Fin n → ℝ) : ℕ → Fin n → ℝ
  | 0 => b
  | t + 1 => fun i => ∑ j, J i j * is_iter J b t j

/-- **Geometric decay.** Every coordinate of `J^t b` lies in `[0, κ λ^t]`. -/
theorem is_iter_bound (J : Fin n → Fin n → ℝ) (b : Fin n → ℝ) (lam κ : ℝ) (hJ : ∀ i j, 0 ≤ J i j)
    (hrow : ∀ i, ∑ j, J i j ≤ lam) (hlam : 0 ≤ lam) (hb0 : ∀ j, 0 ≤ b j) (hbκ : ∀ j, b j ≤ κ) (hκ : 0 ≤ κ) :
    ∀ t i, 0 ≤ is_iter J b t i ∧ is_iter J b t i ≤ κ * lam ^ t := by
  intro t
  induction t with
  | zero => intro i; simp [is_iter, hb0 i, hbκ i]
  | succ t ih =>
    intro i
    have h := is_step_bound J (is_iter J b t) lam (κ * lam ^ t) hJ hrow (fun j => (ih j).1) (fun j => (ih j).2)
      (by positivity) i
    refine ⟨h.1, ?_⟩
    calc is_iter J b (t + 1) i = ∑ j, J i j * is_iter J b t j := rfl
      _ ≤ lam * (κ * lam ^ t) := h.2
      _ = κ * lam ^ (t + 1) := by ring

/-- **Tail bound.** `∑_{s<m} κ λ^{T+s} ≤ κ λ^T / (1 - λ)` for `0 ≤ λ < 1`, every `m`. -/
theorem is_tail_bound (κ lam : ℝ) (T m : ℕ) (hκ : 0 ≤ κ) (h0 : 0 ≤ lam) (h1 : lam < 1) :
    ∑ s ∈ range m, κ * lam ^ (T + s) ≤ κ * lam ^ T / (1 - lam) := by
  have hgeom : ∀ k : ℕ, (∑ s ∈ range k, lam ^ s) * (1 - lam) = 1 - lam ^ k := by
    intro k
    induction k with
    | zero => simp
    | succ k ih => rw [Finset.sum_range_succ, add_mul, ih]; ring
  have hg : ∑ s ∈ range m, lam ^ s = (1 - lam ^ m) / (1 - lam) := by
    have hne2 : 1 - lam ≠ 0 := sub_ne_zero.mpr h1.ne'
    rw [eq_div_iff hne2]; exact hgeom m
  have hsum : ∑ s ∈ range m, κ * lam ^ (T + s) = κ * lam ^ T * ∑ s ∈ range m, lam ^ s := by
    rw [Finset.mul_sum]; exact Finset.sum_congr rfl (fun s _ => by ring)
  rw [hsum, hg, mul_div_assoc']
  apply div_le_div_of_nonneg_right _ (by linarith)
  have : 0 ≤ lam ^ m := pow_nonneg h0 m
  nlinarith [mul_nonneg (mul_nonneg hκ (pow_nonneg h0 T)) this]

end IS_Decay

section IS_BalanceSheet
/-!
# Theorem `thm:forward` (Paper 2), one step with no drift

A dealer holds cash `K` and inventory `I` at mark `p`; equity is `K + I p`, maintenance is_margin `max 0 (μ |I| p - c₀)` and
the remaining is_buffer their difference. If hedge and fill costs `Ch, Cf` are paid and the price moves by `dp` with
`|dp| ≤ U`, the guard inequality `|I| (1 + μ) U + Ch + Cf + R ≤ is_buffer` keeps the is_buffer above the reserve `R`.
The Section 6 is_scenario (`E₀ = 10,000`, `I₀ = -2,000` at `100`, `μ = 0.005`, is_buffer `9,050`, reserve `950`) is checked:
the admissible shock is `8,100 / 2,010`, a move of `4.02` keeps the reserve and a move of `4.05` breaches it.
-/



/-- Remaining is_buffer `E - MM`. -/
noncomputable def is_buffer (K I p μ c0 : ℝ) : ℝ := K + I * p - max 0 (μ * |I| * p - c0)

/-- **Theorem `thm:forward` (one step, `z = 0`).** -/
theorem is_buffer_after_step (K I p dp μ c0 U Ch Cf R : ℝ) (hμ : 0 ≤ μ) (hdp : |dp| ≤ U)
    (hguard : |I| * (1 + μ) * U + Ch + Cf + R ≤ is_buffer K I p μ c0) :
    R ≤ is_buffer (K - Ch - Cf) I (p + dp) μ c0 := by
  unfold is_buffer at *
  have hmove : -(|I| * |dp|) ≤ I * dp := by
    have := abs_mul I dp; have := neg_abs_le (I * dp); nlinarith [abs_nonneg I, abs_nonneg dp]
  have hmm : max 0 (μ * |I| * (p + dp) - c0) ≤ max 0 (μ * |I| * p - c0) + μ * |I| * |dp| := by
    have h1 : μ * |I| * dp ≤ μ * |I| * |dp| := mul_le_mul_of_nonneg_left (le_abs_self dp) (by positivity)
    apply max_le
    · exact add_nonneg (le_max_left _ _) (by positivity)
    · have := le_max_right 0 (μ * |I| * p - c0); nlinarith
  have hU : |I| * |dp| ≤ |I| * U := mul_le_mul_of_nonneg_left hdp (abs_nonneg I)
  have hU2 : μ * |I| * |dp| ≤ μ * |I| * U := by
    have := mul_le_mul_of_nonneg_left hdp (mul_nonneg hμ (abs_nonneg I)); linarith
  nlinarith

/-- The admissible shock at `α = 0` with no drift. -/
noncomputable def is_admissibleShock (Brem R I μ : ℝ) : ℝ := (Brem - R) / (|I| * (1 + μ))

/-- **The Section 6 is_scenario.** -/
theorem is_scenario :
    is_buffer (10000 + 2000 * 100) (-2000) 100 0.005 50 = 9050 ∧
      is_admissibleShock 9050 950 (-2000) 0.005 = 8100 / 2010 ∧
      950 ≤ is_buffer (10000 + 2000 * 100) (-2000) (100 + 4.02) 0.005 50 ∧
      is_buffer (10000 + 2000 * 100) (-2000) (100 + 4.05) 0.005 50 < 950 := by
  unfold is_buffer is_admissibleShock
  refine ⟨?_, ?_, ?_, ?_⟩ <;> norm_num [abs_of_neg, max_def]

end IS_BalanceSheet

section IS_Stat
/-!
# Deterministic cores of Proposition `prop:hotelling` (iii) and Proposition `prop:probe` (Paper 2)

* `prop:hotelling` (iii): with nonnegatively correlated taps (correlation `φ^|i-j|`, `φ ≥ 0`), the variance of the summed
  window, `σ² 1ᵀR1`, is at least the `T σ²` that the (O1) certificate assumes, so its is_margin `z σ √(T/N)` is at most the
  is_margin `z σ √(1ᵀR1/N)` that exact coverage needs. (That the second is_margin covers exactly `1 - γ` is Student/normal
  theory and is not formalized.)
* `prop:probe`: on the time-uniform event `|X̄ₙ - S_T| < rₙ` for every `n` (which Ville's inequality makes probability at
  least `1 - γ`; not formalized), the sequential rule never decides wrongly, whatever its stopping time.
-/

open Finset



/-- Sum of the AR(1) correlation matrix entries. -/
def is_corrSum (φ : ℝ) (T : ℕ) : ℝ := ∑ i ∈ range T, ∑ j ∈ range T, φ ^ (max i j - min i j)

/-- `1ᵀR1 ≥ T` when `φ ≥ 0`. -/
theorem is_corrSum_ge (φ : ℝ) (hφ : 0 ≤ φ) (T : ℕ) : (T : ℝ) ≤ is_corrSum φ T := by
  unfold is_corrSum
  have : ∀ i ∈ range T, (1 : ℝ) ≤ ∑ j ∈ range T, φ ^ (max i j - min i j) := by
    intro i hi
    have h := Finset.single_le_sum (f := fun j => φ ^ (max i j - min i j)) (fun j _ => pow_nonneg hφ _) hi
    simpa using h
  calc (T : ℝ) = ∑ i ∈ range T, (1 : ℝ) := by simp
    _ ≤ _ := Finset.sum_le_sum this

/-- **`prop:hotelling` (iii), deterministic core.** The (O1) is_margin `z σ √(T/N)` is at most the is_margin `z σ √(1ᵀR1/N)`
that exact coverage needs; stated for any nonnegative square roots `s₁² = T/N` and `s₂² = 1ᵀR1/N`. -/
theorem is_o1_margin_too_small (φ z σ N s1 s2 : ℝ) (T : ℕ) (hφ : 0 ≤ φ) (hz : 0 ≤ z) (hσ : 0 ≤ σ) (hN : 0 < N)
    (hs1 : 0 ≤ s1) (hs2 : 0 ≤ s2) (h1 : s1 ^ 2 = T / N) (h2 : s2 ^ 2 = is_corrSum φ T / N) :
    z * σ * s1 ≤ z * σ * s2 := by
  apply mul_le_mul_of_nonneg_left _ (mul_nonneg hz hσ)
  have hle : s1 ^ 2 ≤ s2 ^ 2 := by
    rw [h1, h2]; exact div_le_div_of_nonneg_right (is_corrSum_ge φ hφ T) hN.le
  nlinarith [sq_nonneg (s1 - s2), sq_nonneg (s1 + s2)]

/-- **`prop:probe`, deterministic core: no wrong decision on the time-uniform event.** If at every `n` the running mean is
within `r n` of `S_T`, and the true risk exceeds `S_T` by at most the tail bound, then whenever the rule stops to accept
(`X̄ + r + tail ≤ s_B`) the true risk is within budget, and whenever it stops to refuse (`X̄ - r > s_B`) the true risk
exceeds the budget — at every `n`, hence at any stopping time. -/
theorem is_sequential_rule_correct (xbar r : ℕ → ℝ) (ST S tail sB : ℝ) (hcs : ∀ n, |xbar n - ST| < r n)
    (htail : ST ≤ S ∧ S ≤ ST + tail) (n : ℕ) :
    (xbar n + r n + tail ≤ sB → S ≤ sB) ∧ (sB < xbar n - r n → sB < S) := by
  have h := abs_lt.mp (hcs n)
  constructor
  · intro hstop; linarith [htail.2, h.1]
  · intro hstop; linarith [htail.1, h.2]

end IS_Stat

section IS_Hardening
/-!
# October 2026 hardening results (Papers 1 and 2): the algebraic and order-theoretic cores

* Paper 1, Theorem `thm:rh`: the scalar chain behind the explicit Rayleigh--Hölder bound.
* Paper 1, Proposition `prop:tagged`: positivity of the IV Jacobian determinant.
* Paper 2, Theorem `thm:peak` (ii): the confluent peak lag is the stationary point of `a^(k-1) (aκ + φε k)`;
  (iv): the momentum-only residues lie in `[0, 1]`.
* Paper 2, Theorem `thm:sum`: the summed-response equations have the closed-form solution `κ̃ / (m - q κ̃)`.
* Paper 2, Theorem `thm:disclosure` (v): intersecting two upper bounds admits at least as much as either.
* Paper 2, Proposition `prop:equil` (v): equilibrium depth is increasing in the number of dealers and below the planner's.

Statements that need probability or analysis beyond these cores (the renewal coupling of `prop:lucas` (ii), the
Gaussian divergence bounds of `thm:spectral` (iv), the delta method) are not formalized here.
-/

open Finset



/-! ## Paper 1, Theorem `thm:rh` -/

/-- From `r² ≥ L₀ (1 - γ D)` and `r ≥ 0`, `r ≥ √L₀ · (1 - γ D)₊` when `γ D ≥ 0`; `s` is any nonnegative square root of
`L₀`. -/
theorem is_rh_radius_bound (r L0 s γ D : ℝ) (hr : 0 ≤ r) (hs : 0 ≤ s) (hsL : s ^ 2 = L0) (hγD : 0 ≤ γ * D)
    (h : L0 * (1 - γ * D) ≤ r ^ 2) : s * max 0 (1 - γ * D) ≤ r := by
  rcases le_total (1 - γ * D) 0 with hneg | hpos
  · rw [max_eq_left hneg, mul_zero]; exact hr
  · rw [max_eq_right hpos]
    set y := 1 - γ * D with hy
    have hy1 : y ≤ 1 := by rw [hy]; linarith
    have hL0 : 0 ≤ L0 := by rw [← hsL]; positivity
    have hsq : (s * y) ^ 2 ≤ r ^ 2 := by
      rw [mul_pow, hsL]
      have : y ^ 2 ≤ y := by nlinarith
      nlinarith [mul_le_mul_of_nonneg_left this hL0]
    have hl : 0 ≤ s * y := mul_nonneg hs hpos
    nlinarith [sq_nonneg (s * y - r), sq_nonneg (s * y + r)]

/-- **The explicit Rayleigh--Hölder chain.** With loss `L₀ + x²`, a fee that is nonnegative and at least
`c ‖Ed‖₁ r - x √W`, and `r ≥ √L₀ (1 - γ x²)₊`, loss plus fee is at least
`L₀ + x² + max 0 (F (1 - γ x²)₊ - √W x)` with `F = c ‖Ed‖₁ √L₀` (`s = √L₀`, `sW = √W`). -/
theorem is_rh_chain (L0 x r fee cE s sW γ : ℝ) (hcE : 0 ≤ cE) (hfee0 : 0 ≤ fee)
    (hfee : cE * r - x * sW ≤ fee) (hr : s * max 0 (1 - γ * x ^ 2) ≤ r) :
    L0 + x ^ 2 + max 0 (cE * s * max 0 (1 - γ * x ^ 2) - sW * x) ≤ L0 + x ^ 2 + fee := by
  have h1 : cE * s * max 0 (1 - γ * x ^ 2) ≤ cE * r := by
    rw [mul_assoc]; exact mul_le_mul_of_nonneg_left hr hcE
  have h2 : max 0 (cE * s * max 0 (1 - γ * x ^ 2) - sW * x) ≤ fee :=
    max_le hfee0 (by linarith)
  linarith

/-! ## Paper 1, Proposition `prop:tagged` -/

/-- **IV Jacobian determinant is positive.** With nonnegative autocovariance weights `c`, modes in `[0,1)`, memory rate
`r ∈ [0,1)`, positive merged weight `w` and at least one positive weight, `w ∑ₗ ∑ₘ cₗ cₘ (1 - λₗλₘ)/(1 - r λₘ) > 0`. -/
theorem is_iv_det_pos {n : ℕ} (c lam : Fin n → ℝ) (w r : ℝ) (hw : 0 < w) (hr0 : 0 ≤ r) (hr1 : r < 1)
    (hc : ∀ l, 0 ≤ c l) (hl0 : ∀ l, 0 ≤ lam l) (hl1 : ∀ l, lam l < 1) (hpos : ∃ l, 0 < c l) :
    0 < w * ∑ l, ∑ m, c l * c m * (1 - lam l * lam m) / (1 - r * lam m) := by
  have hden : ∀ m, 0 < 1 - r * lam m := fun m => by nlinarith [hl0 m, hl1 m]
  have hnum : ∀ l m, 0 ≤ 1 - lam l * lam m := fun l m => by nlinarith [hl0 l, hl1 l, hl0 m, hl1 m]
  have hterm : ∀ l m, 0 ≤ c l * c m * (1 - lam l * lam m) / (1 - r * lam m) := fun l m =>
    div_nonneg (mul_nonneg (mul_nonneg (hc l) (hc m)) (hnum l m)) (hden m).le
  obtain ⟨l0, hl0pos⟩ := hpos
  have hdiag : 0 < c l0 * c l0 * (1 - lam l0 * lam l0) / (1 - r * lam l0) := by
    have : 0 < 1 - lam l0 * lam l0 := by nlinarith [hl0 l0, hl1 l0]
    exact div_pos (mul_pos (mul_pos hl0pos hl0pos) this) (hden l0)
  apply mul_pos hw
  apply Finset.sum_pos' (fun l _ => Finset.sum_nonneg (fun m _ => hterm l m))
  refine ⟨l0, Finset.mem_univ _, ?_⟩
  exact Finset.sum_pos' (fun m _ => hterm l0 m) ⟨l0, Finset.mem_univ _, hdiag⟩

/-! ## Paper 2, Theorem `thm:peak` -/

/-- **(ii), confluent peak lag.** With `L = log (1/a) > 0`, so `log a = -L`, the derivative factor
`(aκ + φε k) log a + φε` of `a^(k-1)(aκ + φε k)` vanishes at `k* = 1/L - aκ/(φε)`. -/
theorem is_confluent_stationary (a κ φε L : ℝ) (hL : 0 < L) (hφε : 0 < φε) :
    (a * κ + φε * (1 / L - a * κ / φε)) * (-L) + φε = 0 := by
  field_simp
  ring

/-- **(iv), momentum-only residues.** If `λ₂ ≤ m₁₁ ≤ λ₁` and `λ₂ < λ₁`, the residue share
`(m₁₁ - λ₂)/(λ₁ - λ₂)` and its complement lie in `[0,1]`. -/
theorem is_momentum_residues (l1 l2 m11 : ℝ) (h21 : l2 < l1) (hlo : l2 ≤ m11) (hhi : m11 ≤ l1) :
    0 ≤ (m11 - l2) / (l1 - l2) ∧ (m11 - l2) / (l1 - l2) ≤ 1 ∧ 0 ≤ 1 - (m11 - l2) / (l1 - l2) := by
  have hd : 0 < l1 - l2 := by linarith
  have h1 : (m11 - l2) / (l1 - l2) ≤ 1 := by rw [div_le_one hd]; linarith
  exact ⟨div_nonneg (by linarith) hd.le, h1, by linarith⟩

/-! ## Paper 2, Theorem `thm:sum` -/

/-- **Closed-form summed response.** If the summed price `X`, depth `D` and momentum `F` responses satisfy the stationary
sum equations of the three-state model, then `X = κ̃ / (m - q κ̃)` with `κ̃ = κ + φε/r`, `m = 1 - a`. -/
theorem is_summed_response_closed_form (a κ φ ε r η q X D F : ℝ) (hr : r ≠ 0) (hη : η ≠ 0)
    (hden : 1 - a - q * (κ + φ * ε / r) ≠ 0)
    (hX : X = κ + a * X + φ * D + κ * F) (hD : D = ε + (1 - r) * D + ε * F) (hF : F = (1 - η) * F + η * q * X) :
    X = (κ + φ * ε / r) / (1 - a - q * (κ + φ * ε / r)) := by
  have hF' : F = q * X := by
    have : η * F = η * (q * X) := by linarith
    exact mul_left_cancel₀ hη this
  have hD' : D = ε * (1 + q * X) / r := by
    field_simp; rw [hF'] at hD; linarith
  rw [eq_div_iff hden]
  rw [hD', hF'] at hX
  field_simp at hX ⊢
  linarith

/-! ## Paper 2, Theorem `thm:disclosure` (v) -/

/-- **Intersecting two certificates.** The guard level computed from the smaller of two upper bounds on `Φ` is at least
the level computed from either one. -/
theorem is_intersection_admits_more (a κ L B P1 P2 : ℝ) (hκ : 0 < κ) (h1 : 0 < P1) (h2 : 0 < P2)
    (hc : 0 ≤ is_cI a κ L B) :
    is_alphaStar a κ L B P1 ≤ is_alphaStar a κ L B (min P1 P2) ∧ is_alphaStar a κ L B P2 ≤ is_alphaStar a κ L B (min P1 P2) := by
  have hm : 0 < min P1 P2 := lt_min h1 h2
  have key : ∀ P, 0 < P → min P1 P2 ≤ P → is_alphaStar a κ L B P ≤ is_alphaStar a κ L B (min P1 P2) := by
    intro P hP hle
    unfold is_alphaStar
    apply min_le_min_left
    apply div_le_div_of_nonneg_left hc (by positivity)
    exact mul_le_mul_of_nonneg_left hle hκ.le
  exact ⟨key P1 h1 (min_le_left _ _), key P2 h2 (min_le_right _ _)⟩

/-! ## Paper 2, Proposition `prop:equil` (v) -/

/-- `D ↦ D - A/D²` is strictly increasing on `D > 0` when `A ≥ 0`, so its level sets are single points and larger
right-hand sides have larger solutions. -/
theorem is_depth_solution_increasing (A b1 b2 D1 D2 : ℝ) (hA : 0 ≤ A) (hD1 : 0 < D1) (hD2 : 0 < D2)
    (h1 : D1 - A / D1 ^ 2 = b1) (h2 : D2 - A / D2 ^ 2 = b2) (hb : b1 < b2) : D1 < D2 := by
  by_contra h
  push_neg at h
  have hsq : D2 ^ 2 ≤ D1 ^ 2 := by nlinarith
  have : A / D1 ^ 2 ≤ A / D2 ^ 2 := div_le_div_of_nonneg_left hA (by positivity) hsq
  linarith

/-- **Equilibrium depth is below the planner's.** If `D_eq - θX/D_eq² = b` and `D_sp - N X/D_sp² = b` with
`X > 0` and `θ < N`, then `D_eq < D_sp`. -/
theorem is_depth_eq_lt_sp (θ N X b Deq Dsp : ℝ) (hX : 0 < X) (hθ : 0 ≤ θ) (hθN : θ < N) (hDeq : 0 < Deq) (hDsp : 0 < Dsp)
    (heq : Deq - θ * X / Deq ^ 2 = b) (hsp : Dsp - N * X / Dsp ^ 2 = b) : Deq < Dsp := by
  have hgap : θ * X / Dsp ^ 2 < N * X / Dsp ^ 2 := by
    apply div_lt_div_of_pos_right _ (by positivity); nlinarith
  apply is_depth_solution_increasing (θ * X) b (Dsp - θ * X / Dsp ^ 2) Deq Dsp (by positivity) hDeq hDsp heq rfl
  linarith

/-- **The depth rebate is identified.** With `S = Γ/D` and `κ̃ = 1/D`, the marginal external benefit `Γ/D²` equals
`S κ̃`. -/
theorem is_depth_rebate_identified (Γ D : ℝ) (hD : D ≠ 0) : Γ / D ^ 2 = (Γ / D) * (1 / D) := by
  field_simp

end IS_Hardening

end CurrentMM
