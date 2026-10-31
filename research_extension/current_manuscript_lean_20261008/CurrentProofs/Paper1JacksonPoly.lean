import CurrentProofs.Paper1Jackson
import Mathlib.Algebra.Order.Chebyshev

/-!
# The Jackson operator as a polynomial, and its coefficients after rescaling to `[0, ρ]`

* `jpoly n g = ∑_{k,l ≤ n} c_{kl} T_{k-l}`: `p1_jpoly_eval_cos` (it evaluates to `jop n g θ` at `cos θ`),
  `p1_jpoly_natDegree` (degree `≤ n`) and `p1_jackson` (`|jpoly.eval x - g x| ≤ L π/(n+2)` on `[-1, 1]`);
* `cl1 N p = ∑_{i < N} |coeff_i p|` and its calculus;
* `p1_cl1_chebyshev_comp`: `∑ |coeff (T_m ∘ (αX + β))| ≤ ((|α| + |β|)(1 + √2))^m` when `|α| + |β| ≥ 1`;
* `p1_jpoly_comp_cl1`: if `|g| ≤ G` on `[-1, 1]`, the coefficients of `jpoly n g ∘ (αX + β)` have absolute sum at most
  `G (n+1) ((|α| + |β|)(1 + √2))^n`.
-/

namespace CurrentMM

open Finset Real Polynomial Polynomial.Chebyshev

/-! ### Polynomial form -/

noncomputable def jcoef (n : ℕ) (g : ℝ → ℝ) (k l : ℕ) : ℝ :=
  fkA n k * fkA n l / (fkS n * (n + 2 : ℕ)) *
    ∑ j ∈ range (n + 2), g (cos (2 * π * j / (n + 2 : ℕ))) * cos (((k : ℝ) - l) * (2 * π * j / (n + 2 : ℕ)))

noncomputable def jpoly (n : ℕ) (g : ℝ → ℝ) : ℝ[X] :=
  ∑ k ∈ range (n + 1), ∑ l ∈ range (n + 1), C (jcoef n g k l) * T ℝ ((k : ℤ) - l)

theorem p1_fkKer_pm (n : ℕ) (θ t : ℝ) :
    (fkKer n (θ - t) + fkKer n (θ + t)) / 2 =
      (∑ k ∈ range (n + 1), ∑ l ∈ range (n + 1),
        fkA n k * fkA n l * (cos (((k : ℝ) - l) * θ) * cos (((k : ℝ) - l) * t))) / fkS n := by
  unfold fkKer
  rw [← add_div, div_div, mul_comm (fkS n) 2, ← div_div]
  congr 1
  rw [← sum_add_distrib, Finset.sum_div]
  refine sum_congr rfl (fun k _ => ?_)
  rw [← sum_add_distrib, Finset.sum_div]
  refine sum_congr rfl (fun l _ => ?_)
  rw [mul_sub, mul_add, cos_sub, cos_add]; ring

theorem p1_jpoly_eval_cos (n : ℕ) (g : ℝ → ℝ) (θ : ℝ) : (jpoly n g).eval (cos θ) = jop n g θ := by
  set M : ℝ := ((n + 2 : ℕ) : ℝ) with hM
  set F : ℕ → ℕ → ℕ → ℝ := fun j k l => fkA n k * fkA n l / (fkS n * M) *
    (g (cos (2 * π * j / M)) * cos (((k : ℝ) - l) * (2 * π * j / M))) * cos (((k : ℝ) - l) * θ) with hF
  have hS := (p1_fkS_pos n).ne'
  have hM0 : M ≠ 0 := by rw [hM]; positivity
  have hA : (jpoly n g).eval (cos θ) = ∑ j ∈ range (n + 2), ∑ k ∈ range (n + 1), ∑ l ∈ range (n + 1), F j k l := by
    unfold jpoly
    simp only [eval_finset_sum, eval_mul, eval_C, T_real_cos]
    calc ∑ k ∈ range (n + 1), ∑ l ∈ range (n + 1), jcoef n g k l * cos ((((k : ℤ) - l : ℤ) : ℝ) * θ)
        = ∑ k ∈ range (n + 1), ∑ l ∈ range (n + 1), ∑ j ∈ range (n + 2), F j k l := by
          refine sum_congr rfl (fun k _ => sum_congr rfl (fun l _ => ?_))
          unfold jcoef
          rw [mul_sum, sum_mul]
          refine sum_congr rfl (fun j _ => ?_)
          simp only [hF, hM]; push_cast; ring
      _ = ∑ k ∈ range (n + 1), ∑ j ∈ range (n + 2), ∑ l ∈ range (n + 1), F j k l :=
          sum_congr rfl (fun k _ => sum_comm)
      _ = ∑ j ∈ range (n + 2), ∑ k ∈ range (n + 1), ∑ l ∈ range (n + 1), F j k l := sum_comm
  rw [hA]
  unfold jop
  rw [mul_sum]
  refine sum_congr rfl (fun j _ => ?_)
  rw [p1_fkKer_pm, Finset.sum_div, mul_sum, mul_sum]
  refine sum_congr rfl (fun k _ => ?_)
  rw [Finset.sum_div, mul_sum, mul_sum]
  refine sum_congr rfl (fun l _ => ?_)
  simp only [hF]
  rw [← hM]
  field_simp

theorem p1_natAbs_sub_le (n k l : ℕ) (hk : k < n + 1) (hl : l < n + 1) : ((k : ℤ) - l).natAbs ≤ n := by
  omega

theorem p1_jpoly_natDegree (n : ℕ) (g : ℝ → ℝ) : (jpoly n g).natDegree ≤ n := by
  unfold jpoly
  refine natDegree_sum_le_of_forall_le _ _ (fun k hk => natDegree_sum_le_of_forall_le _ _ (fun l hl => ?_))
  refine (natDegree_C_mul_le _ _).trans ?_
  rw [natDegree_T]
  exact p1_natAbs_sub_le n k l (mem_range.mp hk) (mem_range.mp hl)

/-- **Jackson-type theorem, explicit.** An `L`-Lipschitz function on `[-1, 1]` is within `L π/(n+2)` of the
polynomial `jpoly n g` of degree at most `n`. -/
theorem p1_jackson (n : ℕ) (g : ℝ → ℝ) (L : ℝ) (hL : 0 ≤ L)
    (hg : ∀ x ∈ Set.Icc (-1 : ℝ) 1, ∀ y ∈ Set.Icc (-1 : ℝ) 1, |g x - g y| ≤ L * |x - y|)
    (x : ℝ) (hx : x ∈ Set.Icc (-1 : ℝ) 1) : |(jpoly n g).eval x - g x| ≤ L * (π / (n + 2)) := by
  have h := p1_jop_error n g L hL hg (arccos x)
  rw [cos_arccos hx.1 hx.2] at h
  rw [← cos_arccos hx.1 hx.2, p1_jpoly_eval_cos, cos_arccos hx.1 hx.2]
  exact h

/-! ### Absolute coefficient sums -/

noncomputable def cl1 (N : ℕ) (p : ℝ[X]) : ℝ := ∑ i ∈ range N, |p.coeff i|

theorem p1_cl1_nonneg (N : ℕ) (p : ℝ[X]) : 0 ≤ cl1 N p := sum_nonneg (fun _ _ => abs_nonneg _)

theorem p1_cl1_add (N : ℕ) (p q : ℝ[X]) : cl1 N (p + q) ≤ cl1 N p + cl1 N q := by
  unfold cl1; rw [← sum_add_distrib]
  exact sum_le_sum (fun i _ => by rw [coeff_add]; exact abs_add_le _ _)

theorem p1_cl1_sub (N : ℕ) (p q : ℝ[X]) : cl1 N (p - q) ≤ cl1 N p + cl1 N q := by
  unfold cl1; rw [← sum_add_distrib]
  exact sum_le_sum (fun i _ => by rw [coeff_sub]; exact abs_sub _ _)

theorem p1_cl1_C_mul (N : ℕ) (c : ℝ) (p : ℝ[X]) : cl1 N (C c * p) = |c| * cl1 N p := by
  unfold cl1; rw [mul_sum]
  exact sum_congr rfl (fun i _ => by rw [coeff_C_mul, abs_mul])

theorem p1_cl1_sum {ι : Type*} (s : Finset ι) (N : ℕ) (p : ι → ℝ[X]) :
    cl1 N (∑ i ∈ s, p i) ≤ ∑ i ∈ s, cl1 N (p i) := by
  unfold cl1; rw [sum_comm]
  exact sum_le_sum (fun m _ => by rw [finset_sum_coeff]; exact abs_sum_le_sum_abs _ _)

theorem p1_cl1_extend (N N' : ℕ) (p : ℝ[X]) (hp : p.natDegree < N) (h : N ≤ N') : cl1 N' p = cl1 N p := by
  unfold cl1
  rw [← sum_range_add_sum_Ico _ h]
  have : ∑ i ∈ Ico N N', |p.coeff i| = 0 :=
    sum_eq_zero (fun i hi => by rw [coeff_eq_zero_of_natDegree_lt (by have := (mem_Ico.mp hi).1; omega), abs_zero])
  rw [this, add_zero]

theorem p1_cl1_X_mul (N : ℕ) (p : ℝ[X]) (hp : p.natDegree < N) : cl1 (N + 1) (X * p) = cl1 N p := by
  unfold cl1
  rw [sum_range_succ', coeff_X_mul_zero, abs_zero, add_zero]
  refine sum_congr rfl (fun i _ => ?_)
  rw [coeff_X_mul]

/-- `cl1` of a product with a linear polynomial `αX + β`. -/
theorem p1_cl1_linear_mul (N : ℕ) (α β : ℝ) (p : ℝ[X]) (hp : p.natDegree < N) :
    cl1 (N + 1) ((C α * X + C β) * p) ≤ (|α| + |β|) * cl1 N p := by
  have e : (C α * X + C β) * p = C α * (X * p) + C β * p := by ring
  rw [e]
  refine (p1_cl1_add _ _ _).trans ?_
  rw [p1_cl1_C_mul, p1_cl1_C_mul, p1_cl1_X_mul N p hp, p1_cl1_extend N (N + 1) p hp (by omega)]
  ring_nf; exact le_refl _

/-! ### Chebyshev polynomials of a linear argument -/

theorem p1_cheb_comp_natDegree (α β : ℝ) (m : ℕ) : ((T ℝ m).comp (C α * X + C β)).natDegree ≤ m := by
  refine (natDegree_comp_le).trans ?_
  have h1 : (C α * X + C β).natDegree ≤ 1 := natDegree_linear_le
  have hT : (T ℝ (m : ℤ)).natDegree = m := by rw [natDegree_T]; simp
  rw [hT]
  nlinarith

theorem p1_cheb_comp_rec (α β : ℝ) (m : ℕ) :
    (T ℝ ((m + 2 : ℕ) : ℤ)).comp (C α * X + C β) =
      C 2 * ((C α * X + C β) * (T ℝ ((m + 1 : ℕ) : ℤ)).comp (C α * X + C β)) -
        (T ℝ (m : ℤ)).comp (C α * X + C β) := by
  have h := T_add_two ℝ (m : ℤ)
  push_cast
  rw [h, sub_comp, mul_comp, mul_comp, X_comp, ofNat_comp]
  have h2 : (Polynomial.C (2 : ℝ)) = ((2 : ℕ) : ℝ[X]) := by rw [← Polynomial.C_eq_natCast]; norm_num
  rw [h2]
  ring

/-- **Coefficient growth.** With `γ = |α| + |β| ≥ 1` and `λ = 1 + √2`, `cl1 (m+1) (T_m ∘ (αX+β)) ≤ (γλ)^m`. -/
theorem p1_cl1_chebyshev_comp (α β : ℝ) (hγ : 1 ≤ |α| + |β|) (m : ℕ) :
    cl1 (m + 1) ((T ℝ m).comp (C α * X + C β)) ≤ ((|α| + |β|) * (1 + Real.sqrt 2)) ^ m := by
  set γ := |α| + |β| with hγdef
  set lam := 1 + Real.sqrt 2 with hlam
  have hs2 : Real.sqrt 2 ^ 2 = 2 := Real.sq_sqrt (by norm_num)
  have hs0 : 0 ≤ Real.sqrt 2 := Real.sqrt_nonneg 2
  have hl1 : 1 ≤ lam := by rw [hlam]; linarith
  have hlsq : lam ^ 2 = 2 * lam + 1 := by rw [hlam]; nlinarith
  set U : ℕ → ℝ[X] := fun m => (T ℝ m).comp (C α * X + C β) with hU
  have hdeg : ∀ m, (U m).natDegree < m + 1 := fun m => Nat.lt_succ_of_le (p1_cheb_comp_natDegree α β m)
  have key : ∀ m, cl1 (m + 1) (U m) ≤ (γ * lam) ^ m ∧ cl1 (m + 2) (U (m + 1)) ≤ (γ * lam) ^ (m + 1) := by
    intro m
    induction m with
    | zero =>
      constructor
      · simp only [U, Nat.cast_zero, T_zero, one_comp, pow_zero]
        unfold cl1; simp
      · simp only [U, Nat.cast_one, T_one, X_comp, zero_add, pow_one]
        unfold cl1
        simp [sum_range_succ, coeff_C, coeff_X]
        have : γ ≤ γ * lam := le_mul_of_one_le_right (by positivity) hl1
        linarith [hγdef]
    | succ m ih =>
      refine ⟨ih.2, ?_⟩
      have hrec := p1_cheb_comp_rec α β m
      have hb : cl1 (m + 3) (U (m + 2)) ≤ 2 * (γ * cl1 (m + 2) (U (m + 1))) + cl1 (m + 1) (U m) := by
        simp only [U] at hrec ⊢
        rw [hrec]
        refine (p1_cl1_sub _ _ _).trans ?_
        rw [p1_cl1_C_mul, abs_two]
        have h1 := p1_cl1_linear_mul (m + 2) α β ((T ℝ ((m + 1 : ℕ) : ℤ)).comp (C α * X + C β)) (hdeg (m + 1))
        have h2 := p1_cl1_extend (m + 1) (m + 3) ((T ℝ (m : ℤ)).comp (C α * X + C β)) (hdeg m) (by omega)
        rw [h2]
        nlinarith
      have hγ0 : 0 ≤ γ := by positivity
      have hp : 0 ≤ (γ * lam) ^ m := by positivity
      calc cl1 (m + 1 + 2) (U (m + 1 + 1)) ≤ 2 * (γ * cl1 (m + 2) (U (m + 1))) + cl1 (m + 1) (U m) := hb
        _ ≤ 2 * (γ * (γ * lam) ^ (m + 1)) + (γ * lam) ^ m := by
            have := ih.2; have := ih.1; nlinarith
        _ ≤ (γ * lam) ^ (m + 1 + 1) := by
            have e1 : (γ * lam) ^ (m + 1 + 1) = (γ * lam) ^ m * (γ ^ 2 * lam ^ 2) := by ring
            have e2 : 2 * (γ * (γ * lam) ^ (m + 1)) + (γ * lam) ^ m = (γ * lam) ^ m * (2 * γ ^ 2 * lam + 1) := by ring
            rw [e1, e2, hlsq]
            have : 1 ≤ γ ^ 2 := by nlinarith
            nlinarith
  exact (key m).1

/-! ### Coefficients of the rescaled Jackson polynomial -/

theorem p1_jcoef_abs_le (n : ℕ) (g : ℝ → ℝ) (G : ℝ) (hg : ∀ x ∈ Set.Icc (-1 : ℝ) 1, |g x| ≤ G) (k l : ℕ)
    (hk : k < n + 1) (hl : l < n + 1) : |jcoef n g k l| ≤ fkA n k * fkA n l / fkS n * G := by
  unfold jcoef
  have hS := p1_fkS_pos n
  have hM : (0 : ℝ) < (n + 2 : ℕ) := by positivity
  have hak := p1_fkA_nonneg n k hk
  have hal := p1_fkA_nonneg n l hl
  have hsum : |∑ j ∈ range (n + 2), g (cos (2 * π * j / (n + 2 : ℕ))) * cos (((k : ℝ) - l) * (2 * π * j / (n + 2 : ℕ)))|
      ≤ (n + 2 : ℕ) * G := by
    refine (abs_sum_le_sum_abs _ _).trans ?_
    calc ∑ j ∈ range (n + 2), |g (cos (2 * π * j / (n + 2 : ℕ))) * cos (((k : ℝ) - l) * (2 * π * j / (n + 2 : ℕ)))|
        ≤ ∑ _j ∈ range (n + 2), G := by
          refine sum_le_sum (fun j _ => ?_)
          rw [abs_mul]
          have h1 := hg (cos (2 * π * j / (n + 2 : ℕ))) ⟨neg_one_le_cos _, cos_le_one _⟩
          have h2 := abs_cos_le_one (((k : ℝ) - l) * (2 * π * j / (n + 2 : ℕ)))
          nlinarith [abs_nonneg (g (cos (2 * π * j / (n + 2 : ℕ)))), abs_nonneg (cos (((k : ℝ) - l) * (2 * π * j / (n + 2 : ℕ))))]
      _ = (n + 2 : ℕ) * G := by rw [sum_const, card_range, nsmul_eq_mul]
  rw [abs_mul, abs_of_nonneg (by positivity)]
  calc fkA n k * fkA n l / (fkS n * (n + 2 : ℕ)) * |_| ≤ fkA n k * fkA n l / (fkS n * (n + 2 : ℕ)) * ((n + 2 : ℕ) * G) :=
        mul_le_mul_of_nonneg_left hsum (by positivity)
    _ = fkA n k * fkA n l / fkS n * G := by field_simp

theorem p1_fkA_sum_sq_le (n : ℕ) :
    ∑ k ∈ range (n + 1), ∑ l ∈ range (n + 1), fkA n k * fkA n l / fkS n ≤ n + 1 := by
  have hS := p1_fkS_pos n
  have e : ∑ k ∈ range (n + 1), ∑ l ∈ range (n + 1), fkA n k * fkA n l / fkS n =
      (∑ k ∈ range (n + 1), fkA n k) ^ 2 / fkS n := by
    rw [sq, sum_mul_sum, Finset.sum_div]
    exact sum_congr rfl (fun k _ => by rw [Finset.sum_div])
  rw [e, div_le_iff₀ hS]
  have := sq_sum_le_card_mul_sum_sq (s := range (n + 1)) (f := fkA n)
  simp only [card_range] at this
  unfold fkS; push_cast at this ⊢; linarith

/-- **Coefficients of the rescaled polynomial.** If `|g| ≤ G` on `[-1, 1]` and `γ = |α| + |β| ≥ 1`, then
`∑_{i ≤ n} |coeff_i (jpoly n g ∘ (αX + β))| ≤ G (n+1) (γ(1+√2))^n`. -/
theorem p1_jpoly_comp_cl1 (n : ℕ) (g : ℝ → ℝ) (G : ℝ) (hG : 0 ≤ G) (hg : ∀ x ∈ Set.Icc (-1 : ℝ) 1, |g x| ≤ G)
    (α β : ℝ) (hγ : 1 ≤ |α| + |β|) :
    cl1 (n + 1) ((jpoly n g).comp (C α * X + C β)) ≤ G * (n + 1) * ((|α| + |β|) * (1 + Real.sqrt 2)) ^ n := by
  set B := (|α| + |β|) * (1 + Real.sqrt 2) with hB
  have hB1 : 1 ≤ B := by
    have : 1 ≤ 1 + Real.sqrt 2 := by linarith [Real.sqrt_nonneg 2]
    nlinarith
  unfold jpoly
  rw [Polynomial.sum_comp]
  refine (p1_cl1_sum _ _ _).trans ?_
  have hterm : ∀ k ∈ range (n + 1), ∀ l ∈ range (n + 1),
      cl1 (n + 1) ((C (jcoef n g k l) * T ℝ ((k : ℤ) - l)).comp (C α * X + C β)) ≤
        fkA n k * fkA n l / fkS n * G * B ^ n := by
    intro k hk l hl
    have hk' := mem_range.mp hk; have hl' := mem_range.mp hl
    set d := ((k : ℤ) - l).natAbs with hd
    have hdn : d ≤ n := p1_natAbs_sub_le n k l hk' hl'
    rw [mul_comp, C_comp, p1_cl1_C_mul, ← T_natAbs]
    have hdeg := p1_cheb_comp_natDegree α β d
    rw [p1_cl1_extend (d + 1) (n + 1) _ (Nat.lt_succ_of_le hdeg) (by omega)]
    have hc := p1_cl1_chebyshev_comp α β hγ d
    have hpow : B ^ d ≤ B ^ n := pow_le_pow_right₀ hB1 hdn
    have hj := p1_jcoef_abs_le n g G hg k l hk' hl'
    have h0 : 0 ≤ fkA n k * fkA n l / fkS n * G := by
      have := p1_fkA_nonneg n k hk'; have := p1_fkA_nonneg n l hl'; have := p1_fkS_pos n; positivity
    calc |jcoef n g k l| * cl1 (d + 1) ((T ℝ d).comp (C α * X + C β))
        ≤ (fkA n k * fkA n l / fkS n * G) * B ^ n :=
          mul_le_mul hj (hc.trans hpow) (p1_cl1_nonneg _ _) h0
      _ = fkA n k * fkA n l / fkS n * G * B ^ n := by ring
  calc ∑ k ∈ range (n + 1), cl1 (n + 1) ((∑ l ∈ range (n + 1), C (jcoef n g k l) * T ℝ ((k : ℤ) - l)).comp (C α * X + C β))
      ≤ ∑ k ∈ range (n + 1), ∑ l ∈ range (n + 1), fkA n k * fkA n l / fkS n * G * B ^ n := by
        refine sum_le_sum (fun k hk => ?_)
        rw [Polynomial.sum_comp]
        exact (p1_cl1_sum _ _ _).trans (sum_le_sum (fun l hl => hterm k hk l hl))
    _ = (∑ k ∈ range (n + 1), ∑ l ∈ range (n + 1), fkA n k * fkA n l / fkS n) * (G * B ^ n) := by
        rw [sum_mul]; exact sum_congr rfl (fun k _ => by rw [sum_mul]; exact sum_congr rfl (fun l _ => by ring))
    _ ≤ (n + 1) * (G * B ^ n) := mul_le_mul_of_nonneg_right (p1_fkA_sum_sq_le n) (by positivity)
    _ = G * (n + 1) * B ^ n := by ring

end CurrentMM
