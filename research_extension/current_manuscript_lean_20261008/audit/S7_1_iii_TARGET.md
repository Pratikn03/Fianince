# Proposition S7.1 (iii): frozen target (Phase 1)

## Statement to be machine-checked

Fix the following.

- K = 2 cohorts.
- Known anchor `a` and impact `κ`, with `κ_min ≤ |κ| ≤ κ_max` and `κ_min > 0`.
- A fixed horizon `T ≥ 4`.

**Parameter.** `θ = (w₁, w₂, r₁, r₂)`, made of merged weights and memory rates.
- These are related to the model's cohort sizes and adjustment speeds by `wᵢ = qᵢηᵢ` and `rᵢ = 1 - ηᵢ`.
- The change `η ↦ r` is linear, with Jacobian `diag(1, 1, -1, -1)` on `(w, η)`. It does not change the weight entries
  of the inverse Fisher matrix.
- The kernel is `k_m = w₁r₁^m + w₂r₂^m`, and its generating function is `K(λ) = ∑ k_m λ^m = w₁/(1-r₁λ) + w₂/(1-r₂λ)`.

**Admissible family.** It is fixed by constants `w_min > 0`, `w_max`, `0 < r_lo ≤ r_hi ≤ ρ < 1`, `s < 1` and
`d₀ > 0`, and is the set of all `θ` such that:
- `w_min ≤ wᵢ ≤ w_max`;
- `r_lo ≤ r₁ < r₂ ≤ r_hi`, with spacing `d = r₂ - r₁ ∈ (0, d₀)`;
- the stability margin `|a| + |κ|(w₁ + w₂)/(1 - ρ) ≤ s < 1` holds.

**Observations.** The taps `h₀, …, h_T` of the closed-loop impulse response (`actualCohortImpulse`, or `p1ProbeMean`
with `V = 1`).
- They have independent Gaussian errors of common variance `σ_h²`, so the Fisher matrix is `σ_h⁻² F_T` with
  `F_T = J_TᵀJ_T`.
- `J_T` is the `(T+1) × 4` Jacobian of `(h₀, …, h_T)` with respect to `θ`.
- `h₀ = κ` does not depend on `θ`.
- The taps `h₁, …, h₄` determine `k₀, …, k₃`.

**Target.** There are `c, C > 0` and `d₁ ∈ (0, d₀]` such that, for every admissible `θ` with `0 < d < d₁`:
`c d⁻⁶ ≤ [F_T⁻¹]_{11} ≤ C d⁻⁶`.
- `c` and `C` may depend on `T`, `a`, `κ_min`, `κ_max`, `w_min`, `w_max`, `r_lo`, `r_hi`, `ρ` and `s`.
- They do not depend on `d`, nor on the centre `(r₁ + r₂)/2` within `[r_lo, r_hi]`.

**Kept separate from the target:**
1. The Cramér–Rao variance inequality (proved: `p1_thm_gaussian_cramer_rao`, `p1_thm_cramer_rao_raw_actual`).
2. Confidence intervals and attainability (Theorem `prop:esprit`).

## Route

| Phase | Content |
|---|---|
| 3 (this file's companion `Paper1CRScaling.lean`) | Cubic cancellation: along `v = (1, -1, d/(2w₁), d/(2w₂))`, `DK[v] = d³λ³ / (2(1-r₁λ)²(1-r₂λ)²)`. Moment form: `Dk_m[v] = 0` for `m ≤ 2` and `Dk₃[v] = d³/2`. Nonvanishing and bound `‖DK[v]‖ ≤ d³/(2(1-ρ)⁴)` on the closed disk. |
| 4 | `H = κ/(1 - aλ - κλK)`, so `DH[v] = λH²DK[v]`. `|H| ≤ M = |κ|/(1-s)` on the closed disk, from the stability margin. |
| 5 | Fixed-horizon route: the taps' directional derivatives are the coefficients of `DH[v]`. Bound `‖J_T v‖² ≤ B² d⁶`, with `B` depending on `T`. |
| 6 | Cauchy–Schwarz in the `F_T` inner product, `(e₁ᵀv)² ≤ [F_T⁻¹]_{11} vᵀF_Tv` with `v₁ = 1`. Gives the lower bound `[F_T⁻¹]_{11} ≥ B⁻² d⁻⁶`. |
| 7 | Upper bound. Construct `b` with `J_Tᵀb = e₁` and `‖b‖ ≤ L C₀ d⁻³`, from the map taps → moments and the confluent-Vandermonde inverse row. |
| 8 | Assemble and audit. |

## Status (7 November 2026)

Phases 3–8 are complete and pass CI run 42347257874 (commit 7059b69) under the strict axiom audit. The delivered theorem needs no stability margin and no small-spacing threshold: it holds for every `0 ≤ r₁ < r₂ ≤ 1`. The constants depend on `T`, `|a|`, `κ_min`, `κ_max` and `w_max`. `w_min` is needed only for `wᵢ ≠ 0`. The Phase 4 bound is proved but unused by the fixed-`T` route.
