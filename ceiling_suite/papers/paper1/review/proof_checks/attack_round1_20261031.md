# Attack round 1 (31 October 2026): results that Lean does not cover

Attacker: Claude, using the prompt below on its own earlier work. **This is not independent review.** Run the same
prompt on at least two other models and compare.

Proofs attacked: Theorem 5.4 (`prop:esprit`, Prony upper bound), Theorem 5.6 (`thm:general`, general memory),
Theorem 5.8 (`prop:passive`, passive data), Theorem 6.2 (`thm:discvalue`, value of disclosure). Proposition 6.1
(`prop:tagged`) was done earlier the same day (`prop_tagged_steps.md`).

## Findings and what was done

| # | Result | Step | Finding | Kind | Action |
|---|---|---|---|---|---|
| 1 | Thm 5.4 | statement | Weights written `[ω_min, ω_max]` without naming them; the proof works with merged weights `w_i` | notation gap | Fixed: "merged weights `w_i ∈ [ω_min, ω_max]`" |
| 2 | Thm 5.4 | statement | "…accuracy and confidence, On any such class…" | typo | Fixed |
| 3 | Thm 5.4 | Jacobian step | Determinant `∏ω_i ∏(s_i - s_j)^4` of the moment map | checked numerically | 2,000 random draws, K = 2–4: agrees (worst relative error 0.15%, from ill-conditioning) |
| 4 | Thm 5.4 | tail + union bound | `P(E) ≥ 1-β` with radius `σN^-1/2 √(2 log(4K/β))` over `2K` taps | checked by hand | correct (each tap fails with probability ≤ β/(2K)) |
| 5 | Thm 5.4 | inverse function step | Uniform radius `ρ_0` and Lipschitz constant `L` on the compact class | checked by hand | standard (polynomial map, Jacobian bounded away from zero on a compact set); not formally verified |
| 6 | Thm 5.6 | upper bound, mass of `μ̂` | The LP solution's mass can exceed `W` by up to `2δ`; the bound uses `W + δ` after halving | checked by hand | consistent: `π ρ (2W + 2δ)/(4(L+1)) = π ρ (W+δ)/(2(L+1))` |
| 7 | Thm 5.6 | coefficient bound | Sum of monomial coefficients `≤ ρ B(ρ)^(L+1)` | checked by hand | holds because `B(ρ) ≥ 3.8` for `ρ ≤ 1`, which absorbs the factor 2 from Chebyshev coefficients |
| 8 | Thm 5.6 | lower bound | `‖h^A - h^B‖_2 ≤ C_h ‖k^A - k^B‖_2` with `C_h = κ²/(1-s)²` | checked by hand | correct (`ΔH = z H_A H_B ΔK` and `|H| ≤ κ/(1-s)` on the circle) |
| 9 | Thm 5.8 | resolvent step | `H_1/H_0 - 1 = z^-1 H_1 ΔG` | checked by hand | correct |
| 10 | Thm 5.8 | finite-T bound | KL of `T` observations `≤ C T ε²`, uniform in the separation | checked by hand | correct (Toeplitz eigenvalues in the range of the symbol, `‖A-I‖_F² ≤ T‖A-I‖²`) |
| 11 | Thm 5.8 | rate | Divergence shrinks as `(Δη)^(4K-2)` | checked numerically | Supplement Table S4: slopes 6.19–6.34, 10.27–10.40, 14.33–14.54 for K = 2, 3, 4 |
| 12 | Thm 6.2 | statement (i) | "Fixed accuracy" must be **below half the weight gap of the matched pair**; otherwise recovering the weights does not decide between the two economies and the price-only lower bound does not apply | **real gap** | Fixed: threshold stated in (i) |
| 13 | Thm 6.2 | upper bound | The tagged upper bound was only asymptotic (`O_P(N^-1/2)`) | weakness | Added the finite-sample Chebyshev version, which Lean checks (`p1_thm_tagged_recovery_all_classes`) |

Nothing found that changes a rate or a main conclusion. Item 12 was the one substantive gap.

## The prompt (ready to paste)

Paste this, followed by the theorem, its full proof, and (if you have it) the proof split into numbered steps:

```
You are a hostile referee. Your job is to BREAK the proof below, not to approve it.

Rules:
1. Split the proof into numbered one-line steps S1, S2, ... if it is not already split.
2. For EVERY step, give exactly one of:
   (a) COUNTEREXAMPLE: concrete parameter values where the step's claim is false, with the numbers;
   (b) HIDDEN ASSUMPTION: an assumption the step uses that the theorem statement does not state;
   (c) GAP: a claim that does not follow from the earlier steps and the stated assumptions, and what is missing;
   (d) CITED: the step relies on an outside theorem; name it and say whether its conditions are checked;
   (e) NO PROBLEM FOUND.
3. Check the statement itself: is any quantity undefined, any quantifier ambiguous ("for fixed accuracy", "uniformly"),
   any constant claimed to be independent of something it depends on?
4. Do not summarize the proof. Do not say the proof is correct, convincing or rigorous overall.
5. If you are not sure, say "not sure" and why. Do not invent problems to have something to say.
6. End with a table: step | verdict (a-e) | one-line reason.
```

Check every claimed counterexample yourself, with code, before believing it.
