import CurrentProofs.Paper1TaggedRates
import CurrentProofs.Paper1SupervisoryDecision

/-! An operational tagged-flow bridge. These are conditional model statements,
not a claim that public position stocks are tagged order flows. -/
namespace CurrentMM
open Finset MeasureTheory ProbabilityTheory
open scoped ENNReal NNReal

theorem p1_flow_ratio_interval
    (f0 f1 h f0lo f0hi f1lo f1hi hlo hhi κ : ℝ)
    (hk : 0 < κ) (hf0lo : 0 < f0lo) (hf1lo : 0 ≤ f1lo)
    (h0lo : f0lo ≤ f0) (h0hi : f0 ≤ f0hi)
    (h1lo : f1lo ≤ f1) (h1hi : f1 ≤ f1hi)
    (hhlo : hlo ≤ h) (hhhi : h ≤ hhi) :
    f1lo / f0hi - hhi / κ ≤ f1 / f0 - h / κ ∧
      f1 / f0 - h / κ ≤ f1hi / f0lo - hlo / κ := by
  have hf0 : 0 < f0 := lt_of_lt_of_le hf0lo h0lo
  have hf0hi : 0 < f0hi := lt_of_lt_of_le hf0 h0hi
  have hf1 : 0 ≤ f1 := le_trans hf1lo h1lo
  have hf1hi : 0 ≤ f1hi := le_trans hf1 h1hi
  have lower : f1lo / f0hi ≤ f1 / f0 := by
    apply (div_le_div_iff₀ hf0hi hf0).2
    nlinarith [mul_nonneg (sub_nonneg.mpr h1lo) hf0.le,
      mul_nonneg hf1 (sub_nonneg.mpr h0hi)]
  have upper : f1 / f0 ≤ f1hi / f0lo := by
    apply (div_le_div_iff₀ hf0 hf0lo).2
    nlinarith [mul_nonneg (sub_nonneg.mpr h1hi) hf0lo.le,
      mul_nonneg hf1hi (sub_nonneg.mpr h0lo)]
  have hl := div_le_div_of_nonneg_right hhlo hk.le
  have hh := div_le_div_of_nonneg_right hhhi hk.le
  constructor <;> linarith

theorem p1_flow_intensity_interval
    (w r wlo whi rlo rhi : ℝ) (hwlo : 0 ≤ wlo)
    (hwl : wlo ≤ w) (hwu : w ≤ whi) (hrl : rlo ≤ r)
    (hru : r ≤ rhi) (hri : rhi < 1) :
    wlo / (1-rlo) ≤ w / (1-r) ∧ w / (1-r) ≤ whi / (1-rhi) := by
  have hw : 0 ≤ w := le_trans hwlo hwl
  have hwhi : 0 ≤ whi := le_trans hw hwu
  have hd : 0 < 1-r := by linarith
  have hdl : 0 < 1-rlo := by linarith
  have hdu : 0 < 1-rhi := by linarith
  constructor
  · apply (div_le_div_iff₀ hdl hd).2
    nlinarith [mul_nonneg (sub_nonneg.mpr hwl) hdl.le,
      mul_nonneg hwlo (sub_nonneg.mpr hrl)]
  · apply (div_le_div_iff₀ hd hdu).2
    nlinarith [mul_nonneg (sub_nonneg.mpr hwu) hdu.le,
      mul_nonneg hw (sub_nonneg.mpr hru)]

/-- On simultaneous interval coverage, selecting any class whose remaining
upper budget meets the ceiling is safe under the declared response allowance. -/
theorem p1_flow_selected_halt_sound {K : ℕ}
    (q upper : Fin K → ℝ) (i : Fin K) (a κ drift allowance cap : ℝ)
    (hk : 0 ≤ κ) (hq : ∀ j, q j ≤ upper j) (hd : drift ≤ allowance)
    (hGate : a + κ * (∑ j ∈ univ.erase i, upper j) + allowance ≤ cap) :
    a + κ * (∑ j ∈ univ.erase i, q j) + drift ≤ cap := by
  have hs : (∑ j ∈ univ.erase i, q j) ≤ ∑ j ∈ univ.erase i, upper j :=
    sum_le_sum (fun j _ => hq j)
  have hm := mul_le_mul_of_nonneg_left hs hk
  linarith

/-- Actual simultaneous Gaussian mean bound for J disclosed channels. Combined
with the preceding deterministic inclusions, this supplies the observation error
budget. Interpreting the channels as flow0/flow1/price requires the reset model. -/
theorem p1_flow_joint_mean_bound {J : ℕ} (N : ℕ) (hN : 0 < N)
    (mean : Fin J → ℝ) (v : ℝ≥0) (e : ℝ) (he : 0 < e) :
    (Measure.pi fun j : Fin J => Measure.pi fun _ : Fin N => gaussianReal (mean j) v)
      (⋃ j : Fin J, {x : Fin J → Fin N → ℝ | e ≤ |(∑ n, x j n) / N - mean j|}) ≤
        J * ENNReal.ofReal (v / (N * e ^ 2)) := by
  simpa [p1_impulse_memory_zero] using
    (p1_thm_tagged_recovery_all_classes N hN 0 1 (by norm_num) mean (fun _ => 1) v e he)

end CurrentMM
