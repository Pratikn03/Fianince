import CurrentProofs.Paper1PronyUpper
import Mathlib.Analysis.SpecialFunctions.Exp

/-!
# Paper 1: probing one running market (core `thm:running`)

The probe space is `Fin M → Bool` with the uniform law: probe `a` is the sign `±1` of coordinate `a` (independent fair
signs). The market's noise path `n` (its response to its unknown initial state and to news, plus observation noise) is
held fixed, which is the same as conditioning on it: the probes are independent of the market, so a bound for every
fixed noise path is a bound after averaging over it.

* `pE_walsh_mul`: Walsh products are orthonormal: `E[χ_S χ_R] = 1` if `S = R` and `0` otherwise.
* `p1_walsh_quadratic_bound`: for pair-products whose fibres have at most two elements and distinct single probes,
  `E (∑ c_x χ_{P x} + ∑ d_y ε_{q y})² ≤ 2 ∑ c_x² + ∑ d_y²`.
* `p1_running_tap_mse`: the cross-correlation estimate of tap `j` from `T` recorded prices of a running market that
  has been probed for `L ≥ j` periods before recording satisfies
  `E (ĥ_j - h_j)² ≤ (2 ∑_{i ≤ T+L} h_i² + (∑_t n_t²)/(A² T)) / T`, whatever the market's state when probing began.
* `p1_running_union`: Chebyshev and a union bound over the taps `0, …, J`.
-/

namespace CurrentMM

open Finset

/-- The sign of a bit. -/
def bsgn (b : Bool) : ℝ := if b then 1 else -1

lemma bsgn_mul_self (b : Bool) : bsgn b * bsgn b = 1 := by cases b <;> norm_num [bsgn]

lemma bsgn_not (b : Bool) : bsgn (!b) = -bsgn b := by cases b <;> norm_num [bsgn]

/-- Probe sign `a` on the probe space (fixed at `1` beyond the `M` probes sent). -/
def probe (M a : ℕ) (ω : Fin M → Bool) : ℝ := if h : a < M then bsgn (ω ⟨a, h⟩) else 1

lemma probe_mul_self (M a : ℕ) (ω : Fin M → Bool) : probe M a ω * probe M a ω = 1 := by
  unfold probe; split_ifs <;> simp [bsgn_mul_self]

/-- Walsh product of the probes in `S`. -/
def walsh (M : ℕ) (S : Finset ℕ) (ω : Fin M → Bool) : ℝ := ∏ a ∈ S, probe M a ω

/-- Expectation under independent fair signs. -/
noncomputable def pE (M : ℕ) (f : (Fin M → Bool) → ℝ) : ℝ := (∑ ω, f ω) / 2 ^ M

lemma pE_sum {ι : Type*} (M : ℕ) (s : Finset ι) (f : ι → (Fin M → Bool) → ℝ) :
    pE M (fun ω => ∑ i ∈ s, f i ω) = ∑ i ∈ s, pE M (f i) := by
  unfold pE; rw [Finset.sum_comm, Finset.sum_div]

lemma pE_add (M : ℕ) (f g : (Fin M → Bool) → ℝ) : pE M (fun ω => f ω + g ω) = pE M f + pE M g := by
  unfold pE; rw [Finset.sum_add_distrib, add_div]

lemma pE_const_mul (M : ℕ) (c : ℝ) (f : (Fin M → Bool) → ℝ) : pE M (fun ω => c * f ω) = c * pE M f := by
  unfold pE; rw [← Finset.mul_sum, mul_div_assoc]

lemma pE_one (M : ℕ) : pE M (fun _ => 1) = 1 := by
  unfold pE; simp

lemma pE_mono (M : ℕ) (f g : (Fin M → Bool) → ℝ) (h : ∀ ω, f ω ≤ g ω) : pE M f ≤ pE M g := by
  unfold pE; exact div_le_div_of_nonneg_right (Finset.sum_le_sum fun ω _ => h ω) (by positivity)

lemma walsh_mul (M : ℕ) (S R : Finset ℕ) (ω : Fin M → Bool) :
    walsh M S ω * walsh M R ω = walsh M (symmDiff S R) ω := by
  classical
  unfold walsh
  have hS : S = (S \ R) ∪ (S ∩ R) := (sdiff_union_inter S R).symm
  have hR : R = (R \ S) ∪ (S ∩ R) := by rw [inter_comm]; exact (sdiff_union_inter R S).symm
  have d1 : Disjoint (S \ R) (S ∩ R) := disjoint_sdiff_inter S R
  have d2 : Disjoint (R \ S) (S ∩ R) := by rw [inter_comm]; exact disjoint_sdiff_inter R S
  have d3 : Disjoint (S \ R) (R \ S) := by
    rw [Finset.disjoint_left]; intro x hx hx'
    exact (Finset.mem_sdiff.mp hx).2 (Finset.mem_sdiff.mp hx').1
  have hsd : symmDiff S R = (S \ R) ∪ (R \ S) := symmDiff_def S R
  have hsq : (∏ a ∈ S ∩ R, probe M a ω) * (∏ a ∈ S ∩ R, probe M a ω) = 1 := by
    rw [← Finset.prod_mul_distrib]; exact Finset.prod_eq_one fun a _ => probe_mul_self M a ω
  conv_lhs => rw [hS, Finset.prod_union d1]; arg 2; rw [hR, Finset.prod_union d2]
  rw [hsd, Finset.prod_union d3]
  calc ((∏ a ∈ S \ R, probe M a ω) * (∏ a ∈ S ∩ R, probe M a ω)) *
        ((∏ a ∈ R \ S, probe M a ω) * (∏ a ∈ S ∩ R, probe M a ω))
      = ((∏ a ∈ S \ R, probe M a ω) * (∏ a ∈ R \ S, probe M a ω)) *
        ((∏ a ∈ S ∩ R, probe M a ω) * (∏ a ∈ S ∩ R, probe M a ω)) := by ring
    _ = _ := by rw [hsq, mul_one]

/-- Flipping coordinate `a` of the probe space. -/
def flipAt {M : ℕ} (a : Fin M) : (Fin M → Bool) ≃ (Fin M → Bool) :=
  Function.Involutive.toPerm (fun ω => Function.update ω a (!ω a)) (fun ω => by
    funext b
    by_cases hb : b = a
    · subst hb; simp
    · simp [Function.update_of_ne hb])

lemma walsh_flip (M : ℕ) (S : Finset ℕ) (a : ℕ) (ha : a ∈ S) (haM : a < M) (ω : Fin M → Bool) :
    walsh M S (flipAt ⟨a, haM⟩ ω) = -walsh M S ω := by
  classical
  unfold walsh
  rw [← Finset.mul_prod_erase S _ ha, ← Finset.mul_prod_erase S _ ha]
  have h1 : probe M a (flipAt ⟨a, haM⟩ ω) = -probe M a ω := by
    simp [probe, haM, flipAt, Function.Involutive.toPerm, bsgn_not]
  have h2 : ∏ x ∈ S.erase a, probe M x (flipAt ⟨a, haM⟩ ω) = ∏ x ∈ S.erase a, probe M x ω := by
    refine Finset.prod_congr rfl fun b hb => ?_
    have hba : b ≠ a := Finset.ne_of_mem_erase hb
    unfold probe
    split_ifs with hbM
    · have : (⟨b, hbM⟩ : Fin M) ≠ ⟨a, haM⟩ := fun h => hba (Fin.mk.inj_iff.mp h)
      simp [flipAt, Function.Involutive.toPerm, Function.update_of_ne this]
    · rfl
  rw [h1, h2]; ring

/-- A nonempty Walsh product has mean zero. -/
lemma pE_walsh_nonempty (M : ℕ) (S : Finset ℕ) (hS : S ⊆ range M) (hne : S.Nonempty) :
    pE M (walsh M S) = 0 := by
  obtain ⟨a, ha⟩ := hne
  have haM : a < M := Finset.mem_range.mp (hS ha)
  have hsum : ∑ ω, walsh M S ω = -∑ ω, walsh M S ω := by
    rw [← Finset.sum_neg_distrib]
    exact (Equiv.sum_comp (flipAt ⟨a, haM⟩) (walsh M S)).symm.trans
      (Finset.sum_congr rfl fun ω _ => walsh_flip M S a ha haM ω)
  unfold pE
  have : ∑ ω, walsh M S ω = 0 := by linarith
  rw [this, zero_div]

/-- **Orthonormality of Walsh products.** -/
lemma pE_walsh_mul (M : ℕ) (S R : Finset ℕ) (hS : S ⊆ range M) (hR : R ⊆ range M) :
    pE M (fun ω => walsh M S ω * walsh M R ω) = if S = R then 1 else 0 := by
  classical
  simp_rw [walsh_mul]
  split_ifs with h
  · subst h
    simp only [symmDiff_self, Finset.bot_eq_empty]
    unfold walsh; simp only [Finset.prod_empty]; exact pE_one M
  · apply pE_walsh_nonempty
    · intro x hx
      rw [symmDiff_def, Finset.sup_eq_union, Finset.mem_union] at hx
      rcases hx with hx | hx
      · exact hS (Finset.mem_sdiff.mp hx).1
      · exact hR (Finset.mem_sdiff.mp hx).1
    · rw [Finset.nonempty_iff_ne_empty]
      intro he
      apply h
      have : symmDiff S R = ⊥ := he
      exact symmDiff_eq_bot.mp this

lemma walsh_singleton (M a : ℕ) (ω : Fin M → Bool) : walsh M {a} ω = probe M a ω := by
  simp [walsh]

/-- `∑_{x,x'} [P x = P x'] c_x c_{x'} ≤ 2 ∑ c_x²` when every fibre has at most two elements. -/
lemma p1_fibre_quadratic {α : Type*} [DecidableEq α] (X : Finset α) (P : α → Finset ℕ) (c : α → ℝ)
    (hfib : ∀ x ∈ X, (X.filter (fun x' => P x' = P x)).card ≤ 2) :
    ∑ x ∈ X, ∑ x' ∈ X, (if P x = P x' then c x * c x' else 0) ≤ 2 * ∑ x ∈ X, c x ^ 2 := by
  have hpt : ∀ x x', (if P x = P x' then c x * c x' else 0) ≤
      (if P x = P x' then c x ^ 2 / 2 else 0) + (if P x' = P x then c x' ^ 2 / 2 else 0) := by
    intro x x'
    by_cases h : P x = P x'
    · rw [if_pos h, if_pos h, if_pos h.symm]; nlinarith [sq_nonneg (c x - c x')]
    · rw [if_neg h, if_neg h, if_neg (Ne.symm h)]; norm_num
  have hcount : ∀ x ∈ X, ∑ x' ∈ X, (if P x = P x' then c x ^ 2 / 2 else 0) ≤ c x ^ 2 := by
    intro x hx
    rw [← Finset.sum_filter, Finset.sum_const, nsmul_eq_mul]
    have hc : ((X.filter (fun x' => P x = P x')).card : ℝ) ≤ 2 := by
      have : X.filter (fun x' => P x = P x') = X.filter (fun x' => P x' = P x) :=
        Finset.filter_congr fun x' _ => eq_comm
      rw [this]; exact_mod_cast hfib x hx
    nlinarith [sq_nonneg (c x)]
  calc ∑ x ∈ X, ∑ x' ∈ X, (if P x = P x' then c x * c x' else 0)
      ≤ ∑ x ∈ X, ∑ x' ∈ X, ((if P x = P x' then c x ^ 2 / 2 else 0) +
          (if P x' = P x then c x' ^ 2 / 2 else 0)) :=
        Finset.sum_le_sum fun x _ => Finset.sum_le_sum fun x' _ => hpt x x'
    _ = ∑ x ∈ X, ∑ x' ∈ X, (if P x = P x' then c x ^ 2 / 2 else 0) +
          ∑ x ∈ X, ∑ x' ∈ X, (if P x' = P x then c x' ^ 2 / 2 else 0) := by
        simp only [Finset.sum_add_distrib]
    _ = 2 * ∑ x ∈ X, ∑ x' ∈ X, (if P x = P x' then c x ^ 2 / 2 else 0) := by
        rw [Finset.sum_comm (s := X) (t := X) (f := fun x x' => if P x' = P x then c x' ^ 2 / 2 else 0)]
        ring
    _ ≤ 2 * ∑ x ∈ X, c x ^ 2 := by
        have := Finset.sum_le_sum hcount; linarith

/-- **The quadratic bound.** -/
theorem p1_walsh_quadratic_bound {α β : Type*} [DecidableEq α] (M : ℕ) (X : Finset α) (Y : Finset β)
    (P : α → Finset ℕ) (q : β → ℕ) (c : α → ℝ) (d : β → ℝ)
    (hP : ∀ x ∈ X, P x ⊆ range M) (hPcard : ∀ x ∈ X, (P x).card = 2)
    (hq : ∀ y ∈ Y, q y < M) (hqinj : Set.InjOn q Y)
    (hfib : ∀ x ∈ X, (X.filter (fun x' => P x' = P x)).card ≤ 2) :
    pE M (fun ω => (∑ x ∈ X, c x * walsh M (P x) ω + ∑ y ∈ Y, d y * probe M (q y) ω) ^ 2) ≤
      2 * ∑ x ∈ X, c x ^ 2 + ∑ y ∈ Y, d y ^ 2 := by
  classical
  have hqs : ∀ y ∈ Y, ({q y} : Finset ℕ) ⊆ range M := fun y hy => by
    simpa using hq y hy
  -- expand the square
  have hexp : ∀ ω, (∑ x ∈ X, c x * walsh M (P x) ω + ∑ y ∈ Y, d y * probe M (q y) ω) ^ 2 =
      ∑ x ∈ X, ∑ x' ∈ X, c x * c x' * (walsh M (P x) ω * walsh M (P x') ω) +
      2 * ∑ x ∈ X, ∑ y ∈ Y, c x * d y * (walsh M (P x) ω * walsh M {q y} ω) +
      ∑ y ∈ Y, ∑ y' ∈ Y, d y * d y' * (walsh M {q y} ω * walsh M {q y'} ω) := by
    intro ω
    simp only [walsh_singleton]
    set U := ∑ x ∈ X, c x * walsh M (P x) ω
    set V := ∑ y ∈ Y, d y * probe M (q y) ω
    have hUU : U * U = ∑ x ∈ X, ∑ x' ∈ X, c x * c x' * (walsh M (P x) ω * walsh M (P x') ω) := by
      simp only [U]; rw [Finset.sum_mul_sum]
      exact Finset.sum_congr rfl fun x _ => Finset.sum_congr rfl fun x' _ => by ring
    have hUV : U * V = ∑ x ∈ X, ∑ y ∈ Y, c x * d y * (walsh M (P x) ω * probe M (q y) ω) := by
      simp only [U, V]; rw [Finset.sum_mul_sum]
      exact Finset.sum_congr rfl fun x _ => Finset.sum_congr rfl fun y _ => by ring
    have hVV : V * V = ∑ y ∈ Y, ∑ y' ∈ Y, d y * d y' * (probe M (q y) ω * probe M (q y') ω) := by
      simp only [V]; rw [Finset.sum_mul_sum]
      exact Finset.sum_congr rfl fun y _ => Finset.sum_congr rfl fun y' _ => by ring
    rw [← hUU, ← hUV, ← hVV]; ring
  simp_rw [hexp]
  rw [pE_add, pE_add, pE_const_mul]
  simp only [pE_sum, pE_const_mul]
  have e1 : ∑ x ∈ X, ∑ x' ∈ X, c x * c x' * pE M (fun ω => walsh M (P x) ω * walsh M (P x') ω) =
      ∑ x ∈ X, ∑ x' ∈ X, (if P x = P x' then c x * c x' else 0) :=
    Finset.sum_congr rfl fun x hx => Finset.sum_congr rfl fun x' hx' => by
      rw [pE_walsh_mul M _ _ (hP x hx) (hP x' hx')]; split_ifs <;> simp
  have e2 : ∑ x ∈ X, ∑ y ∈ Y, c x * d y * pE M (fun ω => walsh M (P x) ω * walsh M {q y} ω) = 0 :=
    Finset.sum_eq_zero fun x hx => Finset.sum_eq_zero fun y hy => by
      rw [pE_walsh_mul M _ _ (hP x hx) (hqs y hy), if_neg, mul_zero]
      intro h; have := hPcard x hx; rw [h] at this; simp at this
  have e3 : ∑ y ∈ Y, ∑ y' ∈ Y, d y * d y' * pE M (fun ω => walsh M {q y} ω * walsh M {q y'} ω) =
      ∑ y ∈ Y, d y ^ 2 := by
    refine Finset.sum_congr rfl fun y hy => ?_
    rw [Finset.sum_eq_single y]
    · rw [pE_walsh_mul M _ _ (hqs y hy) (hqs y hy), if_pos rfl]; ring
    · intro y' hy' hne
      rw [pE_walsh_mul M _ _ (hqs y hy) (hqs y' hy'), if_neg, mul_zero]
      intro h
      exact hne (hqinj (Finset.mem_coe.mpr hy') (Finset.mem_coe.mpr hy) (Finset.singleton_inj.mp h).symm)
    · intro h; exact absurd hy h
  rw [e1, e2, e3, mul_zero, add_zero]
  linarith [p1_fibre_quadratic X P c hfib]

lemma p1_finset_pair_eq_iff (a b c d : ℕ) :
    ({a, b} : Finset ℕ) = {c, d} ↔ (a = c ∧ b = d) ∨ (a = d ∧ b = c) := by
  rw [← Finset.coe_inj, Finset.coe_pair, Finset.coe_pair]; exact Set.pair_eq_pair_iff

/-- Price recorded at observation `t` of a market probed with `±A` from `L` periods before the first record: the
response `h` to every probe sent so far, plus the noise path `n` (unknown initial state, news, observation noise). -/
noncomputable def runPrice (A : ℝ) (T L : ℕ) (h n : ℕ → ℝ) (t : ℕ) (ω : Fin (T + L) → Bool) : ℝ :=
  A * ∑ i ∈ range (t + L + 1), h i * probe (T + L) (t + L - i) ω + n t

/-- The cross-correlation estimate of tap `j`. -/
noncomputable def runTap (A : ℝ) (T L : ℕ) (h n : ℕ → ℝ) (j : ℕ) (ω : Fin (T + L) → Bool) : ℝ :=
  (∑ t ∈ range T, runPrice A T L h n t ω * probe (T + L) (t + L - j) ω) / (A * T)

/-- The index set of interfering probe pairs. -/
def runPairs (T L j : ℕ) : Finset (ℕ × ℕ) :=
  (range T ×ˢ range (T + L + 1)).filter (fun p => p.2 ≤ p.1 + L ∧ p.2 ≠ j)

lemma mem_runPairs (T L j : ℕ) (p : ℕ × ℕ) :
    p ∈ runPairs T L j ↔ p.1 ∈ range T ∧ p.2 ∈ (range (p.1 + L + 1)).erase j := by
  simp only [runPairs, Finset.mem_filter, Finset.mem_product, Finset.mem_range, Finset.mem_erase]
  constructor
  · rintro ⟨⟨h1, _⟩, h3, h4⟩; exact ⟨h1, h4, by omega⟩
  · rintro ⟨h1, h4, h3⟩; exact ⟨⟨h1, by omega⟩, by omega, h4⟩

/-- The estimation error is an average of pair products and single probes. -/
lemma p1_runTap_error (A : ℝ) (hA : A ≠ 0) (T L j : ℕ) (hT : 0 < T) (hjL : j ≤ L) (h n : ℕ → ℝ)
    (ω : Fin (T + L) → Bool) :
    runTap A T L h n j ω - h j = (1 / (T : ℝ)) *
      (∑ p ∈ runPairs T L j, h p.2 * walsh (T + L) {p.1 + L - p.2, p.1 + L - j} ω +
        ∑ t ∈ range T, (n t / A) * probe (T + L) (t + L - j) ω) := by
  have hTr : (T : ℝ) ≠ 0 := by exact_mod_cast hT.ne'
  have hinner : ∀ t, ∑ i ∈ range (t + L + 1), h i * probe (T + L) (t + L - i) ω * probe (T + L) (t + L - j) ω =
      h j + ∑ i ∈ (range (t + L + 1)).erase j, h i * walsh (T + L) {t + L - i, t + L - j} ω := by
    intro t
    have hj : j ∈ range (t + L + 1) := Finset.mem_range.mpr (by omega)
    rw [← Finset.add_sum_erase _ _ hj, mul_assoc, probe_mul_self, mul_one]
    congr 1
    refine Finset.sum_congr rfl fun i hi => ?_
    have hij : i ≠ j := Finset.ne_of_mem_erase hi
    have hi' : i < t + L + 1 := Finset.mem_range.mp (Finset.mem_of_mem_erase hi)
    have hne : t + L - i ≠ t + L - j := by omega
    rw [walsh, Finset.prod_pair hne]; ring
  have hsum : ∑ t ∈ range T, runPrice A T L h n t ω * probe (T + L) (t + L - j) ω =
      A * ((T : ℝ) * h j + ∑ t ∈ range T, ∑ i ∈ (range (t + L + 1)).erase j,
        h i * walsh (T + L) {t + L - i, t + L - j} ω) +
      ∑ t ∈ range T, n t * probe (T + L) (t + L - j) ω := by
    unfold runPrice
    simp_rw [add_mul, Finset.sum_add_distrib, mul_assoc, ← Finset.mul_sum, Finset.sum_mul]
    congr 1
    rw [mul_add]
    rw [Finset.sum_congr rfl fun t _ => by
      rw [show ∑ i ∈ range (t + L + 1), h i * probe (T + L) (t + L - i) ω * probe (T + L) (t + L - j) ω =
        _ from hinner t]]
    rw [Finset.sum_add_distrib, Finset.sum_const, Finset.card_range, nsmul_eq_mul]
    ring
  have hpairs : ∑ p ∈ runPairs T L j, h p.2 * walsh (T + L) {p.1 + L - p.2, p.1 + L - j} ω =
      ∑ t ∈ range T, ∑ i ∈ (range (t + L + 1)).erase j, h i * walsh (T + L) {t + L - i, t + L - j} ω :=
    Finset.sum_finset_product _ _ _ (mem_runPairs T L j)
  unfold runTap
  rw [hsum, hpairs]
  have hnA : ∑ t ∈ range T, n t / A * probe (T + L) (t + L - j) ω =
      (∑ t ∈ range T, n t * probe (T + L) (t + L - j) ω) / A := by
    rw [Finset.sum_div]; exact Finset.sum_congr rfl fun t _ => by ring
  rw [hnA]
  field_simp
  ring

/-- **Theorem `thm:running`(ii), the tap estimate.** For every noise path, the mean squared error of the
cross-correlation estimate of tap `j` over independent fair `±A` probes is at most
`(2 ∑_{i ≤ T+L} h_i² + (∑_t n_t²)/(A² T)) / T`. -/
theorem p1_running_tap_mse (A : ℝ) (hA : A ≠ 0) (T L j : ℕ) (hT : 0 < T) (hjL : j ≤ L) (h n : ℕ → ℝ) :
    pE (T + L) (fun ω => (runTap A T L h n j ω - h j) ^ 2) ≤
      (2 * ∑ i ∈ range (T + L + 1), h i ^ 2 + (∑ t ∈ range T, n t ^ 2) / (A ^ 2 * T)) / T := by
  classical
  have hTr : (0 : ℝ) < T := by exact_mod_cast hT
  set X := runPairs T L j
  set P : ℕ × ℕ → Finset ℕ := fun p => {p.1 + L - p.2, p.1 + L - j}
  have hP : ∀ p ∈ X, P p ⊆ range (T + L) := by
    intro p hp
    obtain ⟨h1, h2⟩ := (mem_runPairs T L j p).mp hp
    have h1' := Finset.mem_range.mp h1
    have h2' := Finset.mem_range.mp (Finset.mem_of_mem_erase h2)
    intro a ha
    simp only [P, Finset.mem_insert, Finset.mem_singleton] at ha
    rw [Finset.mem_range]; rcases ha with rfl | rfl <;> omega
  have hPcard : ∀ p ∈ X, (P p).card = 2 := by
    intro p hp
    obtain ⟨_, h2⟩ := (mem_runPairs T L j p).mp hp
    have hij := Finset.ne_of_mem_erase h2
    have h2' := Finset.mem_range.mp (Finset.mem_of_mem_erase h2)
    exact Finset.card_pair (by omega)
  have hfib : ∀ p ∈ X, (X.filter (fun p' => P p' = P p)).card ≤ 2 := by
    intro p hp
    obtain ⟨hp1, hp2⟩ := (mem_runPairs T L j p).mp hp
    have hpj := Finset.ne_of_mem_erase hp2
    have hpi := Finset.mem_range.mp (Finset.mem_of_mem_erase hp2)
    have key : ∀ p' ∈ X.filter (fun p' => P p' = P p),
        (p'.1 = p.1 ∧ p'.2 = p.2) ∨ (p'.1 ≠ p.1 ∧ p'.1 + L - j = p.1 + L - p.2 ∧ p'.1 + L - p'.2 = p.1 + L - j) := by
      intro p' hp'
      rw [Finset.mem_filter] at hp'
      obtain ⟨hp'X, hPP⟩ := hp'
      obtain ⟨_, hq2⟩ := (mem_runPairs T L j p').mp hp'X
      have hqj := Finset.ne_of_mem_erase hq2
      have hqi := Finset.mem_range.mp (Finset.mem_of_mem_erase hq2)
      simp only [P] at hPP
      rcases (p1_finset_pair_eq_iff _ _ _ _).mp hPP with ⟨e1, e2⟩ | ⟨e1, e2⟩
      · left; constructor <;> omega
      · by_cases hs : p'.1 = p.1
        · exfalso; omega
        · right; exact ⟨hs, by omega, by omega⟩
    calc (X.filter (fun p' => P p' = P p)).card ≤ (Finset.univ : Finset Bool).card := by
          apply Finset.card_le_card_of_injOn (fun p' => decide (p'.1 = p.1))
          · intro _ _; exact Finset.mem_coe.mpr (Finset.mem_univ _)
          · intro a ha b hb hab
            have ka := key a (Finset.mem_coe.mp ha)
            have kb := key b (Finset.mem_coe.mp hb)
            simp only at hab
            have ma := (mem_runPairs T L j a).mp (Finset.mem_filter.mp (Finset.mem_coe.mp ha)).1
            have mb := (mem_runPairs T L j b).mp (Finset.mem_filter.mp (Finset.mem_coe.mp hb)).1
            have mai := Finset.mem_range.mp (Finset.mem_of_mem_erase ma.2)
            have mbi := Finset.mem_range.mp (Finset.mem_of_mem_erase mb.2)
            rcases ka with ⟨a1, a2⟩ | ⟨a1, a2, a3⟩ <;> rcases kb with ⟨b1, b2⟩ | ⟨b1, b2, b3⟩
            · exact Prod.ext (a1.trans b1.symm) (a2.trans b2.symm)
            · exfalso; simp [a1, b1] at hab
            · exfalso; simp [a1, b1] at hab
            · have e1 : a.1 = b.1 := by omega
              exact Prod.ext e1 (by omega)
      _ = 2 := by simp
  have hq : ∀ t ∈ range T, t + L - j < T + L := fun t ht => by
    have := Finset.mem_range.mp ht; omega
  have hqinj : Set.InjOn (fun t => t + L - j) (range T : Finset ℕ) := by
    intro a _ b _ hab; simp only at hab; omega
  have hb := p1_walsh_quadratic_bound (T + L) X (range T) P (fun t => t + L - j) (fun p => h p.2)
    (fun t => n t / A) hP hPcard hq hqinj hfib
  have hpt : ∀ ω, (runTap A T L h n j ω - h j) ^ 2 = (1 / (T : ℝ)) ^ 2 *
      (∑ p ∈ X, h p.2 * walsh (T + L) (P p) ω + ∑ t ∈ range T, (n t / A) * probe (T + L) (t + L - j) ω) ^ 2 := by
    intro ω; rw [p1_runTap_error A hA T L j hT hjL h n ω, mul_pow]
  have hX : ∑ p ∈ X, h p.2 ^ 2 ≤ T * ∑ i ∈ range (T + L + 1), h i ^ 2 := by
    calc ∑ p ∈ X, h p.2 ^ 2 ≤ ∑ p ∈ range T ×ˢ range (T + L + 1), h p.2 ^ 2 :=
          Finset.sum_le_sum_of_subset_of_nonneg (Finset.filter_subset _ _) fun _ _ _ => sq_nonneg _
      _ = T * ∑ i ∈ range (T + L + 1), h i ^ 2 := by
          rw [Finset.sum_product]; simp only; rw [Finset.sum_const, Finset.card_range, nsmul_eq_mul]
  have hY : ∑ t ∈ range T, (n t / A) ^ 2 = (∑ t ∈ range T, n t ^ 2) / A ^ 2 := by
    rw [Finset.sum_div]; exact Finset.sum_congr rfl fun t _ => by rw [div_pow]
  simp_rw [hpt]
  rw [pE_const_mul]
  calc (1 / (T : ℝ)) ^ 2 * pE (T + L) (fun ω => (∑ p ∈ X, h p.2 * walsh (T + L) (P p) ω +
          ∑ t ∈ range T, (n t / A) * probe (T + L) (t + L - j) ω) ^ 2)
      ≤ (1 / (T : ℝ)) ^ 2 * (2 * ∑ p ∈ X, h p.2 ^ 2 + ∑ t ∈ range T, (n t / A) ^ 2) :=
        mul_le_mul_of_nonneg_left hb (by positivity)
    _ ≤ (1 / (T : ℝ)) ^ 2 * (2 * (T * ∑ i ∈ range (T + L + 1), h i ^ 2) + (∑ t ∈ range T, n t ^ 2) / A ^ 2) := by
        rw [hY]; gcongr
    _ = (2 * ∑ i ∈ range (T + L + 1), h i ^ 2 + (∑ t ∈ range T, n t ^ 2) / (A ^ 2 * T)) / T := by
        field_simp

open Classical in
/-- Probability of an event under independent fair signs. -/
noncomputable def pProb (M : ℕ) (E : (Fin M → Bool) → Prop) : ℝ :=
  ((Finset.univ.filter E).card : ℝ) / 2 ^ M

open Classical in
/-- Chebyshev (Markov on squares) on the probe space. -/
lemma p1_probe_chebyshev (M : ℕ) (f : (Fin M → Bool) → ℝ) (δ : ℝ) (hδ : 0 < δ) :
    pProb M (fun ω => δ < |f ω|) ≤ pE M (fun ω => f ω ^ 2) / δ ^ 2 := by
  unfold pProb pE
  have hc : ((Finset.univ.filter (fun ω => δ < |f ω|)).card : ℝ) ≤ ∑ ω, f ω ^ 2 / δ ^ 2 := by
    rw [Finset.card_eq_sum_ones, Nat.cast_sum, Nat.cast_one]
    calc ∑ ω ∈ Finset.univ.filter (fun ω => δ < |f ω|), (1 : ℝ)
        ≤ ∑ ω ∈ Finset.univ.filter (fun ω => δ < |f ω|), f ω ^ 2 / δ ^ 2 := by
          refine Finset.sum_le_sum fun ω hω => ?_
          have h1 := (Finset.mem_filter.mp hω).2
          rw [le_div_iff₀ (by positivity), one_mul]
          have : δ ^ 2 < |f ω| ^ 2 := by gcongr
          rw [sq_abs] at this; exact this.le
      _ ≤ ∑ ω, f ω ^ 2 / δ ^ 2 :=
          Finset.sum_le_sum_of_subset_of_nonneg (Finset.filter_subset _ _) fun _ _ _ => by positivity
  rw [← Finset.sum_div] at hc
  calc ((Finset.univ.filter (fun ω => δ < |f ω|)).card : ℝ) / 2 ^ M ≤ ((∑ ω, f ω ^ 2) / δ ^ 2) / 2 ^ M :=
        div_le_div_of_nonneg_right hc (by positivity)
    _ = _ := by simp only []; ring

open Classical in
/-- Union bound over finitely many events. -/
lemma p1_probe_union (M : ℕ) (J : Finset ℕ) (E : ℕ → (Fin M → Bool) → Prop) :
    pProb M (fun ω => ∃ j ∈ J, E j ω) ≤ ∑ j ∈ J, pProb M (E j) := by
  unfold pProb
  rw [← Finset.sum_div]
  apply div_le_div_of_nonneg_right _ (by positivity)
  have hsub : Finset.univ.filter (fun ω => ∃ j ∈ J, E j ω) ⊆ J.biUnion (fun j => Finset.univ.filter (E j)) := by
    intro ω hω; simp only [Finset.mem_filter, Finset.mem_univ, true_and] at hω
    simp only [Finset.mem_biUnion, Finset.mem_filter, Finset.mem_univ, true_and]; exact hω
  have hN := (Finset.card_le_card hsub).trans Finset.card_biUnion_le
  have hR : (((Finset.univ.filter (fun ω => ∃ j ∈ J, E j ω)).card : ℕ) : ℝ) ≤
      ∑ j ∈ J, (((Finset.univ.filter (E j)).card : ℕ) : ℝ) := by exact_mod_cast hN
  convert hR using 4

open Classical in
lemma p1_pProb_compl (M : ℕ) (E : (Fin M → Bool) → Prop) : pProb M (fun ω => ¬ E ω) = 1 - pProb M E := by
  unfold pProb
  have h := Finset.card_filter_add_card_filter_not (s := (Finset.univ : Finset (Fin M → Bool))) E
  have hc : (Finset.univ : Finset (Fin M → Bool)).card = 2 ^ M := by simp
  rw [hc] at h
  have h2 : (2 : ℝ) ^ M ≠ 0 := by positivity
  field_simp
  have : ((Finset.univ.filter (fun ω => ¬ E ω)).card : ℝ) = 2 ^ M - (Finset.univ.filter E).card := by
    have := congrArg (fun k : ℕ => (k : ℝ)) h; push_cast at this; linarith
  convert this using 4

open Classical in
lemma p1_pProb_mono (M : ℕ) (E F : (Fin M → Bool) → Prop) (h : ∀ ω, E ω → F ω) : pProb M E ≤ pProb M F := by
  unfold pProb
  apply div_le_div_of_nonneg_right _ (by positivity)
  exact_mod_cast Finset.card_le_card (fun ω hω => by simp only [Finset.mem_filter] at hω ⊢; exact ⟨hω.1, h ω hω.2⟩)

/-- **Theorem `thm:running`(ii): Prony's method in one running market.** In the setting of the matching upper
bound (`p1_prony_deterministic`), probe a running market with independent fair `±A` signs from `Lead ≥ 2K` periods
before the first of `T` records; the market's state when probing began and its news are arbitrary (they enter only
through the noise path `n`). With probability at least
`1 - ∑_{t ≤ 2K} (2 ∑_{i ≤ T+Lead} h_i² + (∑ n_t²)/(A² T)) / (T e²)` over the probes, Prony's method applied to the
estimated taps has a solution, and every solution recovers the weights to within `L (2^{2K} C e / Δ^{2K-1})`. -/
theorem p1_running_prony_upper {K : ℕ} (a κ : ℝ) (hκ : κ ≠ 0)
    (S : Set (Fin K → ℝ)) (hS : IsCompact S) (γ : ℝ) (hγ : 0 < γ)
    (hSsep : ∀ s ∈ S, ∀ i j, i < j → γ ≤ s j - s i) (hSbox : ∀ s ∈ S, ∀ i, |s i| ≤ 1)
    (ωmin ωmax : ℝ) (hωmin : 0 < ωmin) (hωle : ωmin ≤ ωmax) (rc : ℝ) (hrc : |rc| < 1) :
    ∃ c₁ > 0, ∃ L > 0, ∃ C ≥ 0, ∀ Δ : ℝ, 0 < Δ → Δ ≤ 1 - |rc| →
      ∀ s ∈ S, ∀ wt : Fin K → ℝ, (∀ i, wt i ∈ Set.Icc ωmin ωmax) →
      ∀ h : ℕ → ℝ, h 0 = κ →
      (∀ t, h (t + 1) = a * h t + κ * ∑ j ∈ range (t + 1), (∑ i, wt i * (rc + Δ * s i) ^ j) * h (t - j)) →
      ∀ (A : ℝ), A ≠ 0 → ∀ (T Lead : ℕ), 0 < T → 2 * K ≤ Lead → ∀ (n : ℕ → ℝ) (e : ℝ), 0 < e → e ≤ 1 →
      2 ^ (2 * K) * (C * e) * (Δ ^ (2 * K - 1))⁻¹ ≤ c₁ →
      1 - ∑ t ∈ range (2 * K + 1),
          (2 * ∑ i ∈ range (T + Lead + 1), h i ^ 2 + (∑ u ∈ range T, n u ^ 2) / (A ^ 2 * T)) / T / e ^ 2 ≤
        pProb (T + Lead) (fun ξ =>
          (∃ x : PronyParam K, StrictMono x.1 ∧ (∀ i, x.2 i ≠ 0) ∧
            momentMap K x = pronyMomentEstimate K a κ rc Δ (fun t => runTap A T Lead h n t ξ)) ∧
          ∀ x : PronyParam K, StrictMono x.1 → (∀ i, x.2 i ≠ 0) →
            momentMap K x = pronyMomentEstimate K a κ rc Δ (fun t => runTap A T Lead h n t ξ) →
            ∀ i, |x.2 i - wt i| ≤ L * (2 ^ (2 * K) * (C * e) * (Δ ^ (2 * K - 1))⁻¹)) := by
  classical
  obtain ⟨c₁, hc₁, L, hL, C, hC, hdet⟩ :=
    p1_prony_deterministic a κ hκ S hS γ hγ hSsep hSbox ωmin ωmax hωmin hωle rc hrc
  refine ⟨c₁, hc₁, L, hL, C, hC, ?_⟩
  intro Δ hΔ0 hΔ1 s hs wt hwt h h0 hrec A hA T Lead hT hLead n e he0 he1 hsmall
  set B : ℝ := (2 * ∑ i ∈ range (T + Lead + 1), h i ^ 2 + (∑ u ∈ range T, n u ^ 2) / (A ^ 2 * T)) / T
  -- bad event: some tap is off by more than e
  have hbad : pProb (T + Lead) (fun ξ => ∃ t ∈ range (2 * K + 1), e < |runTap A T Lead h n t ξ - h t|) ≤
      ∑ t ∈ range (2 * K + 1), B / e ^ 2 := by
    refine (p1_probe_union _ _ _).trans (Finset.sum_le_sum fun t ht => ?_)
    have htL : t ≤ Lead := by have := Finset.mem_range.mp ht; omega
    refine (p1_probe_chebyshev _ _ e he0).trans ?_
    exact div_le_div_of_nonneg_right (p1_running_tap_mse A hA T Lead t hT htL h n) (by positivity)
  have hgood : ∀ ξ, ¬ (∃ t ∈ range (2 * K + 1), e < |runTap A T Lead h n t ξ - h t|) →
      ((∃ x : PronyParam K, StrictMono x.1 ∧ (∀ i, x.2 i ≠ 0) ∧
          momentMap K x = pronyMomentEstimate K a κ rc Δ (fun t => runTap A T Lead h n t ξ)) ∧
        ∀ x : PronyParam K, StrictMono x.1 → (∀ i, x.2 i ≠ 0) →
          momentMap K x = pronyMomentEstimate K a κ rc Δ (fun t => runTap A T Lead h n t ξ) →
          ∀ i, |x.2 i - wt i| ≤ L * (2 ^ (2 * K) * (C * e) * (Δ ^ (2 * K - 1))⁻¹)) := by
    intro ξ hξ
    simp only [not_exists, not_and, not_lt] at hξ
    exact hdet Δ hΔ0 hΔ1 s hs wt hwt h h0 hrec (fun t => runTap A T Lead h n t ξ) e he0.le he1
      (fun t ht => hξ t (Finset.mem_range.mpr (by omega))) hsmall
  have hmono := p1_pProb_mono (T + Lead) _ _ hgood
  rw [p1_pProb_compl] at hmono
  have : ∑ t ∈ range (2 * K + 1),
      (2 * ∑ i ∈ range (T + Lead + 1), h i ^ 2 + (∑ u ∈ range T, n u ^ 2) / (A ^ 2 * T)) / T / e ^ 2 =
      ∑ t ∈ range (2 * K + 1), B / e ^ 2 := rfl
  rw [this]; linarith

end CurrentMM
