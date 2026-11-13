import CurrentProofs.Paper1NearCritical
import Mathlib.Analysis.Complex.Basic
import Mathlib.Topology.Order.MonotoneConvergence

/-!
# Paper 1: questions left open, resolved (`prop:nearcritn`, `thm:cascade`, `prop:insider`, `prop:deadband`)

* `p1_nearcrit_finite_sample`: if every eigenvalue `λ_k` of `T_n(f_B)⁻¹ T_n(f_A)` lies within `4ρ` of one, with
  `ρ ≤ 1/8`, the divergence `½ ∑ (λ_k - 1 - log λ_k)` of `n` observations is at most `16 n ρ²`, the per-observation
  bound times `n`, uniformly in the margin to instability (the Toeplitz sandwich that puts the eigenvalues there is on
  paper).
* Cascade after a breach: `p1_cascade_iterate_le_fixed` (the liquidation rounds stay below every fixed point),
  `p1_cascade_rounds_converge` (they converge to the least fixed point), `p1_cascade_contraction` (if `κ Lip(L) < 1`
  the fixed point is unique and moves by at most `|s - s'| / (1 - κ Lip L)`), `p1_cascade_jump` (if `δ - κ L(δ)`
  falls below an earlier value, any shock above that value pushes every fixed point past the fall).
* Insider: `p1_re_inv_one_sub_ge` (`Re 1/(1 - w) ≥ 1/(1 + s)` for `‖w‖ ≤ s < 1`), `p1_no_manipulation_symbol`
  (the symbol of the execution-cost form is at least `κ(1/(1+s) - (1-θ)) > 0` for `θ ≥ 1/2`),
  `p1_netting_prefix` (flow that is a function of earlier flow is netted out: total and net order flow determine each
  other date by date).
* Deadband traders: `p1_deadband_bias` (a bounded deviation from linear rules, fed through the stable closed loop,
  moves prices by at most `E/(1 - s)`).
-/

namespace CurrentMM

open Finset Filter Topology

/-! ### Near instability: finite samples -/

/-- **`prop:nearcritn`, the eigenvalue step.** -/
theorem p1_nearcrit_finite_sample {n : ℕ} (lam : Fin n → ℝ) (ρ : ℝ) (hρ0 : 0 ≤ ρ) (hρ : ρ ≤ 1 / 8)
    (hlam : ∀ k, |lam k - 1| ≤ 4 * ρ) :
    (1 / 2) * ∑ k, (lam k - 1 - Real.log (lam k)) ≤ 16 * n * ρ ^ 2 := by
  have hpt : ∀ k, lam k - 1 - Real.log (lam k) ≤ 2 * (4 * ρ) ^ 2 := by
    intro k
    have hhalf : |lam k - 1| ≤ 1 / 2 := (hlam k).trans (by linarith)
    have h1 := p1_kl_integrand_le (lam k) hhalf
    have h2 : (lam k - 1) ^ 2 ≤ (4 * ρ) ^ 2 := by
      have := hlam k
      have h0 : 0 ≤ |lam k - 1| := abs_nonneg _
      calc (lam k - 1) ^ 2 = |lam k - 1| ^ 2 := (sq_abs _).symm
        _ ≤ (4 * ρ) ^ 2 := by gcongr
    linarith
  calc (1 / 2) * ∑ k, (lam k - 1 - Real.log (lam k)) ≤ (1 / 2) * ∑ _k : Fin n, 2 * (4 * ρ) ^ 2 := by
        gcongr with k; exact hpt k
    _ = 16 * n * ρ ^ 2 := by
        rw [Finset.sum_const, Finset.card_univ, Fintype.card_fin, nsmul_eq_mul]; ring

/-! ### The cascade after a breach -/

/-- Liquidation rounds: `δ₀ = s`, `δ_{n+1} = s + κ L(δ_n)`. -/
noncomputable def cascadeRound (s κ : ℝ) (L : ℝ → ℝ) : ℕ → ℝ
  | 0 => s
  | n + 1 => s + κ * L (cascadeRound s κ L n)

/-- The rounds increase. -/
theorem p1_cascade_mono (s κ : ℝ) (hκ : 0 ≤ κ) (L : ℝ → ℝ) (hL : Monotone L) (hL0 : ∀ x, 0 ≤ L x) :
    Monotone (cascadeRound s κ L) := by
  apply monotone_nat_of_le_succ
  intro n
  induction n with
  | zero => simp only [cascadeRound]; have := hL0 s; nlinarith
  | succ n ih =>
      simp only [cascadeRound] at ih ⊢
      have := hL ih
      nlinarith

/-- **The rounds stay below every fixed point** (with the shock at most the fixed point). -/
theorem p1_cascade_iterate_le_fixed (s κ : ℝ) (hκ : 0 ≤ κ) (L : ℝ → ℝ) (hL : Monotone L)
    (δ : ℝ) (hfix : δ = s + κ * L δ) (hs : s ≤ δ) : ∀ n, cascadeRound s κ L n ≤ δ := by
  intro n
  induction n with
  | zero => exact hs
  | succ n ih =>
      simp only [cascadeRound]
      have := hL ih
      rw [hfix]; nlinarith

/-- **The rounds converge to the least fixed point** when `L` is continuous and bounded. -/
theorem p1_cascade_rounds_converge (s κ : ℝ) (hκ : 0 ≤ κ) (L : ℝ → ℝ) (hL : Monotone L)
    (hL0 : ∀ x, 0 ≤ L x) (Q : ℝ) (hLQ : ∀ x, L x ≤ Q) (hLc : Continuous L) :
    ∃ δ, Tendsto (cascadeRound s κ L) atTop (𝓝 δ) ∧ δ = s + κ * L δ ∧
      ∀ δ' : ℝ, δ' = s + κ * L δ' → s ≤ δ' → δ ≤ δ' := by
  have hmono := p1_cascade_mono s κ hκ L hL hL0
  have hbdd : BddAbove (Set.range (cascadeRound s κ L)) := by
    refine ⟨s + κ * Q, ?_⟩
    rintro _ ⟨n, rfl⟩
    cases n with
    | zero => simp only [cascadeRound]; have := hL0 0; have := hLQ 0; nlinarith
    | succ n => simp only [cascadeRound]; have := hLQ (cascadeRound s κ L n); nlinarith
  set δ := ⨆ n, cascadeRound s κ L n
  have hlim : Tendsto (cascadeRound s κ L) atTop (𝓝 δ) := tendsto_atTop_ciSup hmono hbdd
  have hsucc : Tendsto (fun n => cascadeRound s κ L (n + 1)) atTop (𝓝 δ) := hlim.comp (tendsto_add_atTop_nat 1)
  have hrhs : Tendsto (fun n => s + κ * L (cascadeRound s κ L n)) atTop (𝓝 (s + κ * L δ)) :=
    tendsto_const_nhds.add (tendsto_const_nhds.mul ((hLc.tendsto δ).comp hlim))
  have hfix : δ = s + κ * L δ := tendsto_nhds_unique hsucc (by simpa [cascadeRound] using hrhs)
  refine ⟨δ, hlim, hfix, fun δ' hδ' hs => ?_⟩
  exact ciSup_le fun n => p1_cascade_iterate_le_fixed s κ hκ L hL δ' hδ' hs n

/-- **Below the threshold: uniqueness and continuity.** If `κ Lip(L) < 1`, fixed points for shocks `s, s'` satisfy
`|δ - δ'| ≤ |s - s'| / (1 - κ Lip L)`; in particular the fixed point is unique. -/
theorem p1_cascade_contraction (κ ℓ : ℝ) (hκ : 0 ≤ κ) (hℓ : κ * ℓ < 1) (L : ℝ → ℝ)
    (hLip : ∀ x y, |L x - L y| ≤ ℓ * |x - y|) (s s' δ δ' : ℝ)
    (h : δ = s + κ * L δ) (h' : δ' = s' + κ * L δ') :
    |δ - δ'| ≤ |s - s'| / (1 - κ * ℓ) := by
  have hpos : 0 < 1 - κ * ℓ := by linarith
  rw [le_div_iff₀ hpos]
  have e : δ - δ' = (s - s') + κ * (L δ - L δ') := by linarith
  have h1 : |δ - δ'| ≤ |s - s'| + κ * (ℓ * |δ - δ'|) := by
    calc |δ - δ'| = |s - s' + κ * (L δ - L δ')| := by rw [e]
      _ ≤ |s - s'| + |κ * (L δ - L δ')| := abs_add_le _ _
      _ = |s - s'| + κ * |L δ - L δ'| := by rw [abs_mul, abs_of_nonneg hκ]
      _ ≤ |s - s'| + κ * (ℓ * |δ - δ'|) := by gcongr; exact hLip _ _
  nlinarith

/-- **Above the threshold: the jump.** Let `ψ(δ) = δ - κ L(δ)`. If `ψ ≤ ψ(δ₁)` on `[0, δ₀]`, then for every shock
`s > ψ(δ₁)` every nonnegative fixed point exceeds `δ₀`, while the shock `ψ(δ₁)` has the fixed point `δ₁`. -/
theorem p1_cascade_jump (κ : ℝ) (L : ℝ → ℝ) (δ₀ δ₁ : ℝ)
    (hmax : ∀ δ, 0 ≤ δ → δ ≤ δ₀ → δ - κ * L δ ≤ δ₁ - κ * L δ₁) :
    (δ₁ = (δ₁ - κ * L δ₁) + κ * L δ₁) ∧
    ∀ s, δ₁ - κ * L δ₁ < s → ∀ δ, 0 ≤ δ → δ = s + κ * L δ → δ₀ < δ := by
  refine ⟨by ring, fun s hs δ hδ0 hfix => ?_⟩
  by_contra hle
  have := hmax δ hδ0 (not_lt.mp hle)
  linarith

/-! ### The long-lived insider -/

/-- `Re (1/(1 - w)) ≥ 1/(1 + s)` whenever `‖w‖ ≤ s < 1`. -/
theorem p1_re_inv_one_sub_ge (w : ℂ) (s : ℝ) (hw : ‖w‖ ≤ s) (hs : s < 1) :
    1 / (1 + s) ≤ (1 / (1 - w)).re := by
  have hs0 : 0 ≤ s := (norm_nonneg w).trans hw
  have hre : -s ≤ w.re := by
    have := Complex.abs_re_le_norm w
    have := abs_le.mp (this.trans hw); linarith
  have hnorm2 : w.re ^ 2 + w.im ^ 2 ≤ s ^ 2 := by
    have h1 : ‖w‖ ^ 2 = w.re ^ 2 + w.im ^ 2 := by
      rw [Complex.sq_norm, Complex.normSq_apply]; ring
    rw [← h1]; gcongr
  have hden : 0 < (1 - w.re) ^ 2 + w.im ^ 2 := by
    have : 0 < 1 - w.re := by
      have := Complex.re_le_norm w; linarith
    positivity
  have hval : (1 / (1 - w)).re = (1 - w.re) / ((1 - w.re) ^ 2 + w.im ^ 2) := by
    rw [one_div, Complex.inv_re, Complex.normSq_apply]
    simp only [Complex.sub_re, Complex.one_re, Complex.sub_im, Complex.one_im]
    congr 1; ring
  rw [hval, div_le_div_iff₀ (by linarith) hden]
  nlinarith

/-- **No manipulation in a stable market.** With execution at the pre-trade price plus `θ κ z`, the symbol of the
expected execution-cost form is `κ Re Ĥ(ω)/κ - (1 - θ) κ`; under `‖e^{-iω}(a + κ G(ω))‖ ≤ s < 1` it is at least
`κ (1/(1+s) - (1 - θ))`, which is positive for every `θ ≥ 1/2`. -/
theorem p1_no_manipulation_symbol (κ θ s : ℝ) (hκ : 0 < κ) (hθ : 1 / 2 ≤ θ) (hs0 : 0 ≤ s) (hs : s < 1)
    (w : ℂ) (hw : ‖w‖ ≤ s) :
    κ * (1 / (1 + s) - (1 - θ)) ≤ κ * (1 / (1 - w)).re - (1 - θ) * κ ∧ 0 < κ * (1 / (1 + s) - (1 - θ)) := by
  have h := p1_re_inv_one_sub_ge w s hw hs
  constructor
  · nlinarith
  · apply mul_pos hκ
    have : 1 / 2 < 1 / (1 + s) := by
      rw [div_lt_div_iff₀ (by norm_num) (by linarith)]; linarith
    linarith

/-- **Netting public flow (Kyle market maker).** If the feedback flow at date `t` is a function of the total flow
before `t`, then two total-flow histories whose net flows (total minus feedback) agree up to `t` agree up to `t`:
total and net order flow determine each other date by date, so a market maker who conditions on either has the same
information, and the feedback flow has no price impact. -/
theorem p1_netting_prefix (φ : ℕ → (ℕ → ℝ) → ℝ)
    (hφ : ∀ t (y y' : ℕ → ℝ), (∀ u < t, y u = y' u) → φ t y = φ t y') (y y' : ℕ → ℝ) (t : ℕ)
    (hnet : ∀ u ≤ t, y u - φ u y = y' u - φ u y') : ∀ u ≤ t, y u = y' u := by
  intro u hu
  induction u using Nat.strong_induction_on with
  | _ u ih =>
    have hprev : ∀ v < u, y v = y' v := fun v hv => ih v hv (by omega)
    have hφu := hφ u y y' hprev
    have := hnet u hu
    linarith

/-! ### Deadband traders -/

/-- **The bias of a bounded deviation from linear rules.** If `d_t = a d_{t-1} + κ ∑_{m<t} k_m d_{t-1-m} + e_t`
(`d_{-1} = 0`), with `|e_t| ≤ E` and `|a| + |κ| ∑_{m<t} |k_m| ≤ s < 1` for every `t`, then `|d_t| ≤ E/(1 - s)`. -/
theorem p1_deadband_bias (a κ s E : ℝ) (hs : s < 1) (hE : 0 ≤ E) (k d e : ℕ → ℝ)
    (hstab : ∀ t, |a| + |κ| * ∑ m ∈ range t, |k m| ≤ s) (he : ∀ t, |e t| ≤ E)
    (h0 : d 0 = e 0)
    (hrec : ∀ t, d (t + 1) = a * d t + κ * ∑ m ∈ range (t + 1), k m * d (t - m) + e (t + 1)) :
    ∀ t, |d t| ≤ E / (1 - s) := by
  have hpos : 0 < 1 - s := by linarith
  set M := E / (1 - s) with hM
  have hM0 : 0 ≤ M := div_nonneg hE hpos.le
  have hsM : s * M + E = M := by rw [hM]; field_simp; ring
  intro t
  induction t using Nat.strong_induction_on with
  | _ t ih =>
    cases t with
    | zero =>
        rw [h0]
        have hs0 : 0 ≤ s := (add_nonneg (abs_nonneg a) (mul_nonneg (abs_nonneg κ)
          (sum_nonneg fun _ _ => abs_nonneg _))).trans (hstab 0)
        calc |e 0| ≤ E := he 0
          _ ≤ M := by nlinarith
    | succ t =>
        rw [hrec t]
        have hd : ∀ u ≤ t, |d u| ≤ M := fun u hu => ih u (by omega)
        have hsum : |∑ m ∈ range (t + 1), k m * d (t - m)| ≤ (∑ m ∈ range (t + 1), |k m|) * M := by
          calc |∑ m ∈ range (t + 1), k m * d (t - m)| ≤ ∑ m ∈ range (t + 1), |k m * d (t - m)| :=
                abs_sum_le_sum_abs _ _
            _ ≤ ∑ m ∈ range (t + 1), |k m| * M := by
                refine sum_le_sum fun m _ => ?_
                rw [abs_mul]; exact mul_le_mul_of_nonneg_left (hd _ (by omega)) (abs_nonneg _)
            _ = (∑ m ∈ range (t + 1), |k m|) * M := by rw [sum_mul]
        have hst := hstab (t + 1)
        calc |a * d t + κ * ∑ m ∈ range (t + 1), k m * d (t - m) + e (t + 1)|
            ≤ |a| * |d t| + |κ| * |∑ m ∈ range (t + 1), k m * d (t - m)| + |e (t + 1)| := by
              calc _ ≤ |a * d t + κ * ∑ m ∈ range (t + 1), k m * d (t - m)| + |e (t + 1)| := abs_add_le _ _
                _ ≤ |a * d t| + |κ * ∑ m ∈ range (t + 1), k m * d (t - m)| + |e (t + 1)| := by
                    gcongr; exact abs_add_le _ _
                _ = _ := by rw [abs_mul, abs_mul]
          _ ≤ |a| * M + |κ| * ((∑ m ∈ range (t + 1), |k m|) * M) + E := by
              gcongr
              · exact hd t le_rfl
              · exact he _
          _ = (|a| + |κ| * ∑ m ∈ range (t + 1), |k m|) * M + E := by ring
          _ ≤ s * M + E := by gcongr
          _ = M := hsM

/-- **Forward-looking dealers: several equilibria above the threshold (`prop:reecascade`).** Let
`ψ(δ) = δ - κ L(δ)` be continuous with `ψ(0) ≤ s`, `ψ(δ₁) > s` and `ψ(δ₀) < s` for `0 ≤ δ₁ < δ₀`, and
`ψ(δ₂) ≥ s` for some `δ₂ ≥ δ₀`. Then the equilibrium condition `ψ(δ) = s` has solutions in `[0, δ₁]`, in
`[δ₁, δ₀]` and in `[δ₀, δ₂]`: three equilibria, of which the first two differ and the last two differ. -/
theorem p1_cascade_three_equilibria (ψ : ℝ → ℝ) (hψ : Continuous ψ) (s δ₀ δ₁ δ₂ : ℝ)
    (h01 : 0 ≤ δ₁) (h10 : δ₁ < δ₀) (h02 : δ₀ ≤ δ₂)
    (hz : ψ 0 ≤ s) (h1 : s < ψ δ₁) (h0 : ψ δ₀ < s) (h2 : s ≤ ψ δ₂) :
    ∃ a b c, a ∈ Set.Icc 0 δ₁ ∧ b ∈ Set.Icc δ₁ δ₀ ∧ c ∈ Set.Icc δ₀ δ₂ ∧ ψ a = s ∧ ψ b = s ∧ ψ c = s ∧
      a < b ∧ b < c := by
  obtain ⟨a, ha, hav⟩ := intermediate_value_Icc h01 hψ.continuousOn ⟨hz, h1.le⟩
  obtain ⟨b, hb, hbv⟩ := intermediate_value_Icc' h10.le hψ.continuousOn ⟨h0.le, h1.le⟩
  obtain ⟨c, hc, hcv⟩ := intermediate_value_Icc h02 hψ.continuousOn ⟨h0.le, h2⟩
  refine ⟨a, b, c, ha, hb, hc, hav, hbv, hcv, ?_, ?_⟩
  · rcases lt_or_eq_of_le ha.2 with h | h
    · exact lt_of_lt_of_le h hb.1
    · exfalso; rw [h] at hav; linarith
  · rcases lt_or_eq_of_le hb.2 with h | h
    · exact lt_of_lt_of_le h hc.1
    · exfalso; rw [h] at hbv; linarith

end CurrentMM
