# Author check: Theorems 5.2 and 7.1 (added 27 November 2026)

Once you have checked both theorems, set `AUTHORS_CHECKED_1127 = True` in
`ceiling_suite/papers/paper1_jedc_short/sharpen_1127.py` and rebuild. The AI declaration then covers 21–27 November.
Until then, it says that these two theorems are being checked.

## Theorem 5.2 (one passive price record attains the rates). Proof: Appendix A

1. **The AR(∞) form.** Substitute y_{i,t−1} = η_i Σ_j r_i^j x_{t−1−j} into equation (1) with v ≡ 0. This gives
   x_t − a x_{t−1} = κ Σ_j k_j x_{t−1−j} + ε_t, where k_j = Σ_i w_i r_i^j.
2. **Spectral bounds.** Every coefficient is ≥ 0 and they sum to S ≤ 1 − m. So on the unit circle
   m ≤ |A| ≤ 2, the spectral density lies in [σ²/(8π), σ²/(2π m²)], and the eigenvalues of Γ lie in [σ²/4, σ²/m²].
   (A Toeplitz matrix's eigenvalues lie between 2π times the minimum and maximum of the density.)
3. **(a) The Gram matrix.** By the Gaussian fourth-moment formula, Var(Γ̂_ij) ≤ (2/T) Σ_u γ(u)². By Parseval,
   Σ_u γ(u)² = 2π ∫ f² ≤ σ⁴/m⁴. Chebyshev's inequality on the Frobenius norm then gives the event
   ‖Γ̂ − Γ‖ ≤ σ²/8.
4. **(b) The innovation term.** ε_t is independent of everything earlier, so the cross terms vanish and
   E‖T⁻¹ Σ X_t ε_t‖² = L γ(0) σ² / T.
5. **(c) The truncation term.** By Cauchy–Schwarz, E‖T⁻¹ Σ X_t ϱ_t‖ ≤ √L γ(0) ρ_L, and
   ρ_L ≤ κ W̄ r̄^L / (1 − r̄).
6. **Combining (a)–(c).** On the intersection of the events, the error is at most
   8√L[(m√(Tβ))⁻¹ + ρ_L/(m²β)]. σ cancels.
7. **(i) The budget.** |Ŝ − S| ≤ √L × (coefficient error) + ρ_L, with L of order log(1/(εβ)).
8. **(ii) Composition.** Combine the tap bound with the deterministic Prony step from the proof of Theorem 5.1(iii):
   the tap error is amplified by (Δη)^-(2K−1). This gives T of order ε⁻²β⁻¹(Δη)^-(4K−2) log(1/(εβΔη)).

What to check most carefully: step 2 assumes a ≥ 0 and positive weights, and step 3 assumes Gaussian news.

## Theorem 7.1 (the supervisory separation). Proof: Appendix A

- **(i)**
  - Proposition 7.2(i) gives dependence on S only.
  - The tap-measurement rate uses a four-line argument: a truncation tail below ε/(2κ), and the Gaussian tail of a
    sum of L tap averages.
  - The passive version is Theorem 5.2(i).
  - Minimax optimality is Theorem 7.5(i).
- **(ii)** Proposition 7.2(ii) covers halting the largest group, with memories in r_c + Δη[−1, 1]. Proposition
  7.2(iii) covers the horizon cutoff, with memories in [r̂ − Δη, r̂ + 2Δη]. Both intervals have length at most 3Δη.
- **(iii)** Theorem 7.8, over its families.

What to check: in (i), the noise bound N ≥ 8κ²σ²L log(2/β)/ε² comes from P(|Z| > t) ≤ 2e^{−t²/2}.

## Numerical check

`ceiling_suite/p1_theory/passive_upper_check.py`, with results in `passive_upper_check_results.json`.
