import CurrentProofs.Paper1CRS71iiiEta

/-!
# Paper 1, Proposition S7.1 (iii) for the second weight coordinate

The same two-sided `(Δη)⁻⁶` bound holds for `[F_T⁻¹]₂₂`, the entry of `w₂`.
- Lower bound: the weak direction `v` of `Paper1CRS71iii` has second coordinate `-1`, so the same Cauchy–Schwarz step
  applies.
- Upper bound: the recovering row for `w₂` is the first row with the rates exchanged, `p1U r₂ r₁`
  (`p1_U_moment_swap`). It gives `b' = c(p1U r₂ r₁)/(r₁ - r₂)³` with `J_Tᵀ b' = e₂`.
-/

namespace CurrentMM

open Finset Matrix

theorem p1_U_moment_swap (w1 w2 r1 r2 : ℝ) (i : Fin 4) :
    ∑ m ∈ range 4, p1U r2 r1 m * p1K2D ![w1, w2, r1, r2] (Pi.single i 1) m =
      (Pi.single 1 ((r1 - r2) ^ 3) : Fin 4 → ℝ) i := by
  have u0 : p1U r2 r1 0 = r1 ^ 2 * (r1 - 3 * r2) := rfl
  have u1 : p1U r2 r1 1 = 6 * (r2 * r1) := rfl
  have u2 : p1U r2 r1 2 = -(3 * (r2 + r1)) := rfl
  have u3 : p1U r2 r1 3 = 2 := rfl
  fin_cases i <;>
  · conv_lhs => simp [sum_range_succ, p1K2D, Pi.single_apply, u0, u1, u2, u3]
    conv_rhs => simp [Pi.single_apply]
    ring

theorem p1_S71iii_recover_two (a κ w1 w2 r1 r2 : ℝ) (T : ℕ) (hT : 4 ≤ T) (hκ : κ ≠ 0) (hd : r1 - r2 ≠ 0) :
    (p1TapJac a κ T ![w1, w2, r1, r2])ᵀ *ᵥ
        (fun t : Fin (T + 1) => p1C a κ (p1K2 ![w1, w2, r1, r2]) (p1U r2 r1) t.val / (r1 - r2) ^ 3) =
      Pi.single 1 1 := by
  funext i
  have hd3 : (r1 - r2) ^ 3 ≠ 0 := pow_ne_zero 3 hd
  calc ((p1TapJac a κ T ![w1, w2, r1, r2])ᵀ *ᵥ
        (fun t : Fin (T + 1) => p1C a κ (p1K2 ![w1, w2, r1, r2]) (p1U r2 r1) t.val / (r1 - r2) ^ 3)) i
      = ∑ t : Fin (T + 1), (fun n : ℕ => p1C a κ (p1K2 ![w1, w2, r1, r2]) (p1U r2 r1) n *
          p1TapD a κ (p1K2 ![w1, w2, r1, r2]) (p1K2D ![w1, w2, r1, r2] (Pi.single i 1)) n / (r1 - r2) ^ 3) t.val := by
        simp only [Matrix.mulVec, dotProduct, Matrix.transpose_apply]
        refine sum_congr rfl fun t _ => ?_
        rw [p1_tapJac_entry]
        ring
    _ = ∑ n ∈ range 5, p1C a κ (p1K2 ![w1, w2, r1, r2]) (p1U r2 r1) n *
          p1TapD a κ (p1K2 ![w1, w2, r1, r2]) (p1K2D ![w1, w2, r1, r2] (Pi.single i 1)) n / (r1 - r2) ^ 3 :=
        p1_sum_fin_range5 T hT _ fun n hn => by simp [p1_C_ge a κ (p1K2 ![w1, w2, r1, r2]) (p1U r2 r1) n hn]
    _ = (∑ m ∈ range 4, p1U r2 r1 m * p1K2D ![w1, w2, r1, r2] (Pi.single i 1) m) / (r1 - r2) ^ 3 := by
        rw [← Finset.sum_div, p1_C_identity a κ hκ _ _ _ (p1_U_ge r2 r1)]
    _ = (Pi.single 1 1 : Fin 4 → ℝ) i := by
        rw [p1_U_moment_swap]
        fin_cases i <;> simp [Pi.single_apply, hd3]

theorem p1_S71iii_b_norm_two (a κ κmin κm wm w1 w2 r1 r2 : ℝ) (T : ℕ) (hT : 4 ≤ T) (hκmin : 0 < κmin)
    (hκ1 : κmin ≤ |κ|) (hκ2 : |κ| ≤ κm) (hw1 : 0 ≤ w1) (hw1' : w1 ≤ wm) (hw2 : 0 ≤ w2) (hw2' : w2 ≤ wm)
    (hr1 : 0 ≤ r1) (hr12 : r1 < r2) (hr2' : r2 ≤ 1) :
    (fun t : Fin (T + 1) => p1C a κ (p1K2 ![w1, w2, r1, r2]) (p1U r2 r1) t.val / (r1 - r2) ^ 3) ⬝ᵥ
        (fun t : Fin (T + 1) => p1C a κ (p1K2 ![w1, w2, r1, r2]) (p1U r2 r1) t.val / (r1 - r2) ^ 3) ≤
      5 * ((4 * ((1 + 2 * (|a| + κm * (2 * wm)) + (|a| + κm * (2 * wm)) ^ 2 + 2 * (κm * (2 * wm)) +
          2 * (|a| + κm * (2 * wm)) * (κm * (2 * wm))) * 6) / κmin ^ 2) *
        (4 * ((1 + 2 * (|a| + κm * (2 * wm)) + (|a| + κm * (2 * wm)) ^ 2 + 2 * (κm * (2 * wm)) +
          2 * (|a| + κm * (2 * wm)) * (κm * (2 * wm))) * 6) / κmin ^ 2)) / (r2 - r1) ^ 6 := by
  have hr2 : 0 ≤ r2 := by linarith
  have hr1' : r1 ≤ 1 := by linarith
  have hκm : 0 ≤ κm := le_trans (abs_nonneg κ) hκ2
  have hd6 : 0 < (r2 - r1) ^ 6 := pow_pos (by linarith) 6
  have hd6' : (r1 - r2) ^ 6 = (r2 - r1) ^ 6 := by ring
  set k := p1K2 ![w1, w2, r1, r2] with hkdef
  have hk : ∀ m, |k m| ≤ 2 * wm := p1_K2_abs_le w1 w2 r1 r2 wm hw1 hw1' hw2 hw2' hr1 hr1' hr2 hr2'
  have hκk : ∀ m, |κ * k m| ≤ κm * (2 * wm) := fun m => by
    rw [abs_mul]; exact mul_le_mul hκ2 (hk m) (abs_nonneg _) hκm
  have hα : |a + κ * k 0| ≤ |a| + κm * (2 * wm) := le_trans (abs_add_le _ _) (by linarith [hκk 0])
  have hE := p1_E_abs_le a κ k _ _ hα (hκk 1) (hκk 2)
  have hC := p1_C_abs_le a κ κmin k (p1U r2 r1) _ 6 hκmin hκ1 hE (p1_U_abs_le r2 r1 hr2 hr2' hr1 hr1')
  set Cb := 4 * ((1 + 2 * (|a| + κm * (2 * wm)) + (|a| + κm * (2 * wm)) ^ 2 + 2 * (κm * (2 * wm)) +
          2 * (|a| + κm * (2 * wm)) * (κm * (2 * wm))) * 6) / κmin ^ 2 with hCb
  have hterm : ∀ n, (p1C a κ k (p1U r2 r1) n / (r1 - r2) ^ 3) * (p1C a κ k (p1U r2 r1) n / (r1 - r2) ^ 3) ≤
      Cb * Cb / (r2 - r1) ^ 6 := by
    intro n
    have h1 : p1C a κ k (p1U r2 r1) n * p1C a κ k (p1U r2 r1) n ≤ Cb * Cb := by
      have h := mul_self_le_mul_self (abs_nonneg _) (hC n)
      rwa [abs_mul_abs_self] at h
    have e : (p1C a κ k (p1U r2 r1) n / (r1 - r2) ^ 3) * (p1C a κ k (p1U r2 r1) n / (r1 - r2) ^ 3) =
        p1C a κ k (p1U r2 r1) n * p1C a κ k (p1U r2 r1) n / (r2 - r1) ^ 6 := by
      rw [← hd6']; ring
    rw [e]
    exact div_le_div_of_nonneg_right h1 hd6.le
  calc _ = ∑ t : Fin (T + 1), (fun n : ℕ => (p1C a κ k (p1U r2 r1) n / (r1 - r2) ^ 3) *
        (p1C a κ k (p1U r2 r1) n / (r1 - r2) ^ 3)) t.val := rfl
    _ = ∑ n ∈ range 5, (p1C a κ k (p1U r2 r1) n / (r1 - r2) ^ 3) * (p1C a κ k (p1U r2 r1) n / (r1 - r2) ^ 3) :=
        p1_sum_fin_range5 T hT _ fun n hn => by simp [p1_C_ge a κ k (p1U r2 r1) n hn]
    _ ≤ ∑ _n ∈ range 5, Cb * Cb / (r2 - r1) ^ 6 := sum_le_sum fun n _ => hterm n
    _ = 5 * (Cb * Cb) / (r2 - r1) ^ 6 := by
        rw [sum_const, card_range, nsmul_eq_mul]; first | (push_cast; ring) | push_cast | norm_num

/-- **Proposition S7.1 (iii), entry of `w₂`.** -/
theorem p1_prop_S7_1_iii_two (a κ κmin κm wm w1 w2 r1 r2 : ℝ) (T : ℕ) (hT : 4 ≤ T) (hκmin : 0 < κmin)
    (hκ1 : κmin ≤ |κ|) (hκ2 : |κ| ≤ κm) (hw1 : 0 < w1) (hw1' : w1 ≤ wm) (hw2 : 0 < w2) (hw2' : w2 ≤ wm)
    (hr1 : 0 ≤ r1) (hr12 : r1 < r2) (hr2' : r2 ≤ 1) :
    1 / (((T : ℝ) + 1) * ((T : ℝ) ^ 3 * p1TapG |a| κm (2 * wm) T) ^ 2) / (r2 - r1) ^ 6 ≤
      ((p1TapJac a κ T ![w1, w2, r1, r2])ᵀ * p1TapJac a κ T ![w1, w2, r1, r2])⁻¹ 1 1 ∧
    ((p1TapJac a κ T ![w1, w2, r1, r2])ᵀ * p1TapJac a κ T ![w1, w2, r1, r2])⁻¹ 1 1 ≤
      5 * ((4 * ((1 + 2 * (|a| + κm * (2 * wm)) + (|a| + κm * (2 * wm)) ^ 2 + 2 * (κm * (2 * wm)) +
          2 * (|a| + κm * (2 * wm)) * (κm * (2 * wm))) * 6) / κmin ^ 2) *
        (4 * ((1 + 2 * (|a| + κm * (2 * wm)) + (|a| + κm * (2 * wm)) ^ 2 + 2 * (κm * (2 * wm)) +
          2 * (|a| + κm * (2 * wm)) * (κm * (2 * wm))) * 6) / κmin ^ 2)) / (r2 - r1) ^ 6 := by
  have hκ0 : κ ≠ 0 := fun h => by rw [h, abs_zero] at hκ1; linarith
  have hd : r2 - r1 ≠ 0 := by linarith
  have hd' : r1 - r2 ≠ 0 := by linarith
  have hd6 : 0 < (r2 - r1) ^ 6 := pow_pos (by linarith) 6
  have hJ := p1_S71iii_isUnit a κ w1 w2 r1 r2 T hT hκ0 hw1.ne' hw2.ne' hd
  obtain ⟨-, hBpos, -, -⟩ :=
    p1_prop_S7_1_iii a κ κmin κm wm w1 w2 r1 r2 T hT hκmin hκ1 hκ2 hw1 hw1' hw2 hw2' hr1 hr12 hr2'
  have hlow := p1_fisher_entry_lower _ hJ 1 ![1, -1, (r2 - r1) / (2 * w1), (r2 - r1) / (2 * w2)]
  have hnorm := p1_S71iii_weak_norm a κ κm wm w1 w2 r1 r2 T hκ2 hw1 hw1' hw2 hw2' hr1 hr12.le hr2'
  have hup := p1_fisher_entry_upper _ hJ 1 _ (p1_S71iii_recover_two a κ w1 w2 r1 r2 T hT hκ0 hd')
  have hb := p1_S71iii_b_norm_two a κ κmin κm wm w1 w2 r1 r2 T hT hκmin hκ1 hκ2 hw1.le hw1' hw2.le hw2' hr1 hr12
    hr2'
  have hv : (![1, -1, (r2 - r1) / (2 * w1), (r2 - r1) / (2 * w2)] : Fin 4 → ℝ) 1 ^ 2 = 1 := by simp
  rw [hv] at hlow
  generalize hB : ((T : ℝ) + 1) * ((T : ℝ) ^ 3 * p1TapG |a| κm (2 * wm) T) ^ 2 = B at hBpos hnorm ⊢
  generalize hJdef : p1TapJac a κ T ![w1, w2, r1, r2] = J at hJ hlow hnorm hup ⊢
  have hF0 : 0 ≤ (Jᵀ * J)⁻¹ 1 1 := by
    rw [← p1_fisher_col_norm J hJ 1]; exact p1_dot_self_nonneg _
  refine ⟨?_, le_trans hup hb⟩
  rw [div_div, div_le_iff₀ (mul_pos hBpos hd6)]
  calc (1 : ℝ) ≤ (Jᵀ * J)⁻¹ 1 1 * ((J *ᵥ ![1, -1, (r2 - r1) / (2 * w1), (r2 - r1) / (2 * w2)]) ⬝ᵥ
        (J *ᵥ ![1, -1, (r2 - r1) / (2 * w1), (r2 - r1) / (2 * w2)])) := hlow
    _ ≤ (Jᵀ * J)⁻¹ 1 1 * (B * (r2 - r1) ^ 6) := mul_le_mul_of_nonneg_left hnorm hF0

end CurrentMM
