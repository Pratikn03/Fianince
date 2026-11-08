import Mathlib.Analysis.Calculus.InverseFunctionTheorem.FDeriv
import Mathlib.Analysis.Calculus.FDeriv.Mul
import Mathlib.Analysis.Calculus.FDeriv.Prod
import Mathlib.Analysis.Calculus.Deriv.Comp
import Mathlib.Topology.Algebra.Module.FiniteDimension
import Mathlib.Tactic.FieldSimp
import Mathlib.Tactic.LinearCombination
import Mathlib.Tactic.Ring

/-!
# Paper 1, Theorem 4.1(iv): small feedback, by the inverse function theorem

Feedback of size `ε` along a fixed cohort profile: `G_ε(D) = ε g(D)`, with `g` strictly differentiable at `D = 1`
(for the paper's cohorts, `g(D) = Σ c_i/(D - r_i)` with `r_i ≠ 1`). The equilibrium system of Theorem 4.1, with the
dealer equation multiplied by `D`, is

`Φ_ε(κ, D) = (D + ε κ g(D) - 1, κ (D - ā) D - A (σ_F² D² + κ² σ_ξ²)) = 0`.

At `ε = 0` it has the zero `(κ₀, 1)` whenever `κ₀ (1 - ā) = A (σ_F² + κ₀² σ_ξ²)` (part (ii)). If
`s = (1 - ā) - 2 A κ₀ σ_ξ² ≠ 0` (for the low root, `s = √Δ > 0`), then:

* `p1_inventory_small_feedback`: there is a neighbourhood `U` of `(κ₀, 1)` and a solution path `ε ↦ (κ(ε), D(ε))`,
  with `(κ(0), D(0)) = (κ₀, 1)`, such that for all small `ε` the path solves `Φ_ε = 0` inside `U`, it is the **only**
  solution in `U`, and it is differentiable at `0` with
  `D'(0) = -κ₀ g(1)` and `κ'(0) = κ₀² (ā + 2 A κ₀ σ_ξ²) g(1) / s`,
  which are the first-order formulas of Theorem 4.1(iv) with `G(1) = ε g(1)`.

The proof applies Mathlib's inverse function theorem (`HasStrictFDerivAt.toOpenPartialHomeomorph`, `localInverse`) to
`Ψ(ε, κ, D) = (ε, Φ_ε(κ, D))`, whose derivative at `(0, κ₀, 1)` is triangular with determinant `s`.
-/

namespace CurrentMM

open Filter Topology

/-- The derivative of `Ψ` at `(0, κ₀, 1)`, as a linear equivalence. -/
noncomputable def p1IFTLin (c1 s c : ℝ) (hs : s ≠ 0) : (ℝ × ℝ × ℝ) ≃ₗ[ℝ] (ℝ × ℝ × ℝ) where
  toFun v := (v.1, c1 * v.1 + v.2.2, s * v.2.1 + c * v.2.2)
  invFun y := (y.1, (y.2.2 - c * (y.2.1 - c1 * y.1)) / s, y.2.1 - c1 * y.1)
  map_add' x y := by ext <;> simp <;> ring_nf
  map_smul' r x := by ext <;> simp <;> ring_nf
  left_inv v := by
    obtain ⟨a, b, d⟩ := v
    ext <;> simp <;> field_simp <;> ring
  right_inv y := by
    obtain ⟨a, b, d⟩ := y
    ext <;> simp <;> field_simp <;> ring

/-- The map `Ψ(ε, κ, D) = (ε, Φ_ε(κ, D))`. -/
def p1IFTPsi (A sF2 sX2 ab : ℝ) (g : ℝ → ℝ) (p : ℝ × ℝ × ℝ) : ℝ × ℝ × ℝ :=
  (p.1, p.2.2 + p.1 * p.2.1 * g p.2.2 - 1,
    p.2.1 * (p.2.2 - ab) * p.2.2 - A * (sF2 * (p.2.2 * p.2.2) + p.2.1 * p.2.1 * sX2))

theorem p1_IFT_hasStrictFDerivAt (A sF2 sX2 ab k0 : ℝ) (g : ℝ → ℝ) (g' : ℝ) (hg : HasStrictDerivAt g g' 1)
    (hs : (1 - ab) - 2 * A * k0 * sX2 ≠ 0) :
    HasStrictFDerivAt (p1IFTPsi A sF2 sX2 ab g)
      (((p1IFTLin (k0 * g 1) ((1 - ab) - 2 * A * k0 * sX2) (k0 * (2 - ab) - 2 * A * sF2) hs).toContinuousLinearEquiv :
        (ℝ × ℝ × ℝ) ≃L[ℝ] (ℝ × ℝ × ℝ)) : (ℝ × ℝ × ℝ) →L[ℝ] (ℝ × ℝ × ℝ)) ((0 : ℝ), k0, (1 : ℝ)) := by
  set a : ℝ × ℝ × ℝ := ((0 : ℝ), k0, (1 : ℝ))
  have hE : HasStrictFDerivAt (fun p : ℝ × ℝ × ℝ => p.1) (ContinuousLinearMap.fst ℝ ℝ (ℝ × ℝ)) a :=
    hasStrictFDerivAt_fst
  have hK : HasStrictFDerivAt (fun p : ℝ × ℝ × ℝ => p.2.1)
      ((ContinuousLinearMap.fst ℝ ℝ ℝ).comp (ContinuousLinearMap.snd ℝ ℝ (ℝ × ℝ))) a :=
    hasStrictFDerivAt_fst.comp a hasStrictFDerivAt_snd
  have hD : HasStrictFDerivAt (fun p : ℝ × ℝ × ℝ => p.2.2)
      ((ContinuousLinearMap.snd ℝ ℝ ℝ).comp (ContinuousLinearMap.snd ℝ ℝ (ℝ × ℝ))) a :=
    hasStrictFDerivAt_snd.comp a hasStrictFDerivAt_snd
  have hgD : HasStrictFDerivAt (fun p : ℝ × ℝ × ℝ => g p.2.2)
      (g' • ((ContinuousLinearMap.snd ℝ ℝ ℝ).comp (ContinuousLinearMap.snd ℝ ℝ (ℝ × ℝ)))) a := by
    have := hg.comp_hasStrictFDerivAt a hD
    simpa [Function.comp_def, a] using this
  have h1 := ((hD.add ((hE.mul hK).mul hgD)).sub_const 1)
  have h2 := ((hK.mul (hD.sub_const ab)).mul hD).sub
    ((((hD.mul hD).const_mul sF2).add ((hK.mul hK).mul_const sX2)).const_mul A)
  have h := hE.prodMk (h1.prodMk h2)
  refine h.congr_fderiv ?_
  ext ⟨e, k, d⟩ <;> simp [a, p1IFTLin] <;> ring

/-- **Theorem 4.1(iv), small feedback.** Existence, local uniqueness and the first-order formulas. -/
theorem p1_inventory_small_feedback (A sF2 sX2 ab k0 : ℝ) (g : ℝ → ℝ) (g' : ℝ) (hg : HasStrictDerivAt g g' 1)
    (hroot : A * (sF2 + k0 ^ 2 * sX2) = k0 * (1 - ab)) (hs : (1 - ab) - 2 * A * k0 * sX2 ≠ 0) :
    ∃ U ∈ 𝓝 (k0, (1 : ℝ)), ∃ sol : ℝ → ℝ × ℝ,
      sol 0 = (k0, 1) ∧
      (∀ᶠ ε in 𝓝 (0 : ℝ), sol ε ∈ U ∧
        (sol ε).2 + ε * (sol ε).1 * g (sol ε).2 - 1 = 0 ∧
        (sol ε).1 * ((sol ε).2 - ab) * (sol ε).2 - A * (sF2 * (sol ε).2 ^ 2 + (sol ε).1 ^ 2 * sX2) = 0 ∧
        ∀ q ∈ U, q.2 + ε * q.1 * g q.2 - 1 = 0 →
          q.1 * (q.2 - ab) * q.2 - A * (sF2 * q.2 ^ 2 + q.1 ^ 2 * sX2) = 0 → q = sol ε) ∧
      HasDerivAt (fun ε => (sol ε).2) (-(k0 * g 1)) 0 ∧
      HasDerivAt (fun ε => (sol ε).1) (k0 ^ 2 * (ab + 2 * A * k0 * sX2) * g 1 / ((1 - ab) - 2 * A * k0 * sX2)) 0 := by
  set s := (1 - ab) - 2 * A * k0 * sX2 with hsdef
  set L := p1IFTLin (k0 * g 1) s (k0 * (2 - ab) - 2 * A * sF2) hs
  have hf := p1_IFT_hasStrictFDerivAt A sF2 sX2 ab k0 g g' hg hs
  set Ψ := p1IFTPsi A sF2 sX2 ab g
  set a : ℝ × ℝ × ℝ := ((0 : ℝ), k0, (1 : ℝ))
  have hΨa : Ψ a = (0, 0, 0) := by
    show ((0 : ℝ), (1 : ℝ) + 0 * k0 * g 1 - 1, k0 * (1 - ab) * 1 - A * (sF2 * (1 * 1) + k0 * k0 * sX2)) = (0, 0, 0)
    rw [show (1 : ℝ) + 0 * k0 * g 1 - 1 = 0 by ring,
      show k0 * (1 - ab) * 1 - A * (sF2 * (1 * 1) + k0 * k0 * sX2) = 0 by linear_combination (-1 : ℝ) * hroot]
  have hinv0 : hf.localInverse Ψ _ a (Ψ a) = a := hf.localInverse_apply_image
  set ι : ℝ → ℝ × ℝ × ℝ := fun ε => (ε, 0, 0)
  have hι0 : ι 0 = Ψ a := by rw [hΨa]
  have hιc : Filter.Tendsto ι (𝓝 0) (𝓝 (Ψ a)) := by
    rw [← hι0]; exact (Continuous.prodMk continuous_id continuous_const).tendsto 0
  have hιd : HasStrictFDerivAt ι ((ContinuousLinearMap.id ℝ ℝ).prod 0) (0 : ℝ) :=
    (hasStrictFDerivAt_id (0 : ℝ)).prodMk (hasStrictFDerivAt_const ((0 : ℝ), (0 : ℝ)) 0)
  have hinvd : HasStrictFDerivAt (hf.localInverse Ψ _ a)
      ((L.toContinuousLinearEquiv.symm : (ℝ × ℝ × ℝ) ≃L[ℝ] (ℝ × ℝ × ℝ)) : (ℝ × ℝ × ℝ) →L[ℝ] (ℝ × ℝ × ℝ)) (ι 0) := by
    rw [hι0]; exact hf.to_localInverse
  have hcomp := (hinvd.comp (0 : ℝ) hιd).hasFDerivAt
  have hv : ((L.toContinuousLinearEquiv.symm : (ℝ × ℝ × ℝ) ≃L[ℝ] (ℝ × ℝ × ℝ)) : (ℝ × ℝ × ℝ) →L[ℝ] (ℝ × ℝ × ℝ)).comp
      ((ContinuousLinearMap.id ℝ ℝ).prod 0) 1 = L.symm (1, 0, 0) := rfl
  have hderiv : HasDerivAt (fun ε => hf.localInverse Ψ _ a (ι ε)) (L.symm (1, 0, 0)) 0 := by
    have := hcomp.hasDerivAt; rw [hv] at this; exact this
  have hsym : L.symm (1, 0, 0) = (1, (0 - (k0 * (2 - ab) - 2 * A * sF2) * (0 - k0 * g 1 * 1)) / s, 0 - k0 * g 1 * 1) := rfl
  -- left inverse on a neighbourhood of `a`, which contains a product neighbourhood
  have hleft := hf.eventually_left_inverse
  obtain ⟨W, hW, hWleft⟩ : ∃ W ∈ 𝓝 a, ∀ x ∈ W, hf.localInverse Ψ _ a (Ψ x) = x :=
    ⟨_, hleft, fun x hx => hx⟩
  rw [show a = ((0 : ℝ), (k0, (1 : ℝ))) from rfl, nhds_prod_eq, Filter.mem_prod_iff] at hW
  obtain ⟨I, hI, U, hU, hIU⟩ := hW
  refine ⟨U, hU, fun ε => (hf.localInverse Ψ _ a (ι ε)).2, ?_, ?_, ?_, ?_⟩
  · show (hf.localInverse Ψ _ a (ι 0)).2 = (k0, 1)
    rw [hι0, hinv0]
  · have hright : ∀ᶠ ε in 𝓝 (0 : ℝ), Ψ (hf.localInverse Ψ _ a (ι ε)) = ι ε :=
      hιc.eventually hf.eventually_right_inverse
    have htend : Filter.Tendsto (fun ε => hf.localInverse Ψ _ a (ι ε)) (𝓝 0) (𝓝 a) := by
      have := hf.localInverse_tendsto.comp hιc
      exact this
    have hnear : ∀ᶠ ε in 𝓝 (0 : ℝ), hf.localInverse Ψ _ a (ι ε) ∈ I ×ˢ U := by
      have hmem : I ×ˢ U ∈ 𝓝 a := by
        rw [show a = ((0 : ℝ), (k0, (1 : ℝ))) from rfl, nhds_prod_eq]; exact Filter.prod_mem_prod hI hU
      exact htend.eventually hmem
    have hI0 : ∀ᶠ ε in 𝓝 (0 : ℝ), ε ∈ I := hI
    filter_upwards [hright, hnear, hI0] with ε hR hN hε
    have hfst : (hf.localInverse Ψ _ a (ι ε)).1 = ε := by
      have := congrArg Prod.fst hR; simpa [Ψ, ι, p1IFTPsi] using this
    have hc1 := congrArg (fun z => z.2.1) hR
    have hc2 := congrArg (fun z => z.2.2) hR
    simp only [Ψ, ι, p1IFTPsi] at hc1 hc2
    rw [hfst] at hc1
    refine ⟨(Set.mem_prod.mp hN).2, hc1, by linear_combination hc2, ?_⟩
    intro q hq e1 e2
    have hq' : (ε, q) ∈ W := hIU (Set.mk_mem_prod hε hq)
    have hΨq : Ψ (ε, q) = ι ε := by
      show (ε, q.2 + ε * q.1 * g q.2 - 1, q.1 * (q.2 - ab) * q.2 - A * (sF2 * (q.2 * q.2) + q.1 * q.1 * sX2)) =
        (ε, (0 : ℝ), (0 : ℝ))
      rw [e1, show q.1 * (q.2 - ab) * q.2 - A * (sF2 * (q.2 * q.2) + q.1 * q.1 * sX2) = 0 by
        linear_combination e2]
    have h1 := hWleft _ hq'
    rw [hΨq] at h1
    rw [h1]
  · have := (hasFDerivAt_snd.comp (0 : ℝ) (hasFDerivAt_snd.comp (0 : ℝ) hderiv.hasFDerivAt)).hasDerivAt
    rw [hsym] at this
    convert this using 1
    · rfl
    · simp only [ContinuousLinearMap.comp_apply, ContinuousLinearMap.toSpanSingleton_apply, one_smul,
        ContinuousLinearMap.coe_fst', ContinuousLinearMap.coe_snd']
      ring
  · have := (hasFDerivAt_fst.comp (0 : ℝ) (hasFDerivAt_snd.comp (0 : ℝ) hderiv.hasFDerivAt)).hasDerivAt
    rw [hsym] at this
    have hc : (k0 * (2 - ab) - 2 * A * sF2) = k0 * (ab + 2 * A * k0 * sX2) := by
      linear_combination (-2 : ℝ) * hroot
    convert this using 1
    · rfl
    · simp only [ContinuousLinearMap.comp_apply, ContinuousLinearMap.toSpanSingleton_apply, one_smul,
        ContinuousLinearMap.coe_fst', ContinuousLinearMap.coe_snd']
      rw [hc]
      ring

end CurrentMM
