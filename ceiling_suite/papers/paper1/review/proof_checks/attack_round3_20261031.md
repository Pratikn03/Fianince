# Attack round 3 (31 October 2026): Theorems `thm:spectral` and `thm:rh`

The two main-text theorems that no earlier round covered. Attacker: Claude, with the round-1 prompt, on its own
earlier work. **Not independent review.**

## Theorem `thm:spectral` (spectral dissipation lower bound)

| Step | Claim | Verdict |
|---|---|---|
| (i) | `L_i(v) = ½ vᵀT_h v = (1/2π)∫ g_i |V|²`, `g_i = Re Ĥ_i − κ/2` | checked by hand: symmetric Toeplitz form with `h_0 = κ` gives `(1/2π)∫(2 Re Ĥ − κ)|V|²`, halved |
| (i) | `g_i > 0` | checked: `Re Ĥ ≥ Σ ω_ℓ/(1+λ_ℓ) > κ/2` for a positive mixture with `λ_ℓ < 1` (Lemma 2.3) |
| (ii) | Parseval and the Neyman–Pearson requirement `‖ΔHv‖ ≥ 2σ z_{1−α}` | checked (both error probabilities at most α) |
| (iii) | 61.14, 61.41, 64.48 | traced to `recompute_theory.py` → `R_P1_theory_constants.json` (earlier audit) |
| (iv) | `‖G_θ‖ ≤ M̄`, `‖G_θ⁻¹‖ ≤ 2` | checked: sections of analytic Toeplitz operators have norm ≤ sup of the symbol; `κ/Ĥ` analytic outside the disk by minimum phase (now formally checked in `Paper1MinPhase.lean`), `inf |Ĥ| ≥ inf Re Ĥ ≥ κ/2` |
| (iv) | covariance part `≤ ‖Σ₀−Σ₁‖_F²/(2cσ_eff⁴) ≤ C_w T δ⁴` | checked by hand, constant reproduced exactly: `‖Σ₀−Σ₁‖_F ≤ 2σ_w² M̄ ‖ΔG‖_F`, `‖ΔG‖_F² ≤ T K*²δ⁴/κ²`, `1/c = (σ_ν²+σ_w²M̄²)/σ_ν²` |
| (iv) | `λ − 1 − log λ ≤ (λ−1)²/λ` | checked (equality at 1; holds for all λ > 0) |

## Theorem `thm:rh` (finite-horizon Rayleigh–Hölder duality)

Every step checked by hand: generalized-eigenbasis expansion; `r²λ(θ)` equals the top-two information; the bound on
`D`; `r² ≥ L₀(1−γD)` (the constant γ reproduced exactly); Hölder with the sign vector; Cauchy–Schwarz with weights
`1−λ_j/λ(θ)` (positive because `λ_j ≤ λ_{L−3} < λ_{L−2} ≤ λ(θ)`); `√y ≥ y` on `[0,1]`; nonnegativity of the fee.
Minor point: when the top-two component vanishes (`r = 0`) θ is arbitrary and every inequality still holds.

Numerical check (`check_thm_rh.py` → `check_thm_rh_results.json`): the proof is pure linear algebra, so it was
tested on random positive definite `G`, positive semidefinite `M`, `c_req`, `c_fee` and horizons 5–11. 18,000
random feasible probes and 20,000 near-optimal probes (top-two direction plus small perturbations): **0
violations**; the smallest ratio of `L + c_fee‖v‖₁` to `C_RH` was 1.008, so the bound is close to tight.

## Result

No error found in either theorem; no change to the paper. With rounds 1–3, every main-text theorem has been
through at least one attack round or a Lean proof. Human review is still needed for `thm:general`,
`prop:passive`, `thm:spectral` and `thm:rh`.
