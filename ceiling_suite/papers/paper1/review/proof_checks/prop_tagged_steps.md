# Worked example: checking the proof of Proposition 6.1 (tagged flow) step by step

Paper 1, Proposition `prop:tagged`. Proof in Appendix A (paragraph "Proposition 6.1"), one paragraph long.
Numerical checks: `check_prop_tagged.py` → `check_prop_tagged_results.json` (run 31 Oct 2026, about 1 minute).

There are four parts. Do the same four for every other proof.

---

## Part 1. The proof rewritten as numbered one-line steps

Model facts used: price equation `x_t = a x_{t-1} + κ Σ q_i y_{i,t-1} + ξ_t`, cohort equation
`y_{i,t} = (1-η_i) y_{i,t-1} + η_i x_t`, `r_i = 1-η_i`, `w_i = q_i η_i`. Instruments `Z_t = (x_{t-1}, x_t)`.

| Step | Claim (one line) | Uses | Numerical check | Result |
|---|---|---|---|---|
| S1 | Tagged flow obeys `u_{i,t} = r_i u_{i,t-1} + w_i x_t` exactly | cohort equation, `u_i = q_i y_i` | simulate 20,000 periods, residual | 2e-16 (exact) |
| S2 | Noisy flow obeys `ũ_t = r ũ_{t-1} + w x_t + e_t`, `e_t = ε_t - r ε_{t-1}` | S1, `ũ = u + ε` | same simulation, residual | 4e-16 (exact) |
| S3 | `E[Z_t e_t] = 0` | **assumption**: noise independent of prices | (follows from the assumption) | — |
| S4 | IV estimator is consistent if `Σ_i = E[Z_t (ũ_{t-1}, x_t)]` is nonsingular | S3, law of large numbers for a stationary ergodic process | (standard result) | — |
| S5 | `u_{t-1} = w Σ_s r^s x_{t-1-s}`, so `E[x_{t-1}u_{t-1}] = w A_0`, `E[x_t u_{t-1}] = w A_1` | S1, `0 ≤ r < 1` | 400,000-period simulation vs formula | error 0.06–0.09% |
| S6 | `γ_x(s) = Σ_ℓ c_ℓ λ_ℓ^s` with `c_ℓ ≥ 0` | Lemma 2.3 (`lem:cm`) | (follows from Lemma 2.3, which Lean checks) | — |
| S7 | `det Σ_i = w_i (γ_0 A_0 - γ_1 A_1)` | S5 (2×2 determinant) | simulated vs formula determinant | 0.153 vs 0.153; 0.213 vs 0.213 |
| S8 | `γ_0 A_0 - γ_1 A_1 = Σ_{ℓ,m} c_ℓ c_m (1-λ_ℓλ_m)/(1-rλ_m)`, each term ≥ 0 | S6, geometric sums | 20,000 random draws | worst relative error 1e-14 |
| S9 | `Σ Z_t e_t = Σ (Z_t - r Z_{t+1}) ε_t + O_P(1)` | S2, summation by parts | (algebra) | — |
| S10 | `m_t = (Z_t - rZ_{t+1}) ε_t` is a martingale difference with `E[m mᵀ] = Ω_i` | S9, noise i.i.d. and independent of prices | 300,000-period simulation vs formula | error 0.35% |
| S11 | `√T(β̂ - β) → N(0, Σ⁻¹ΩΣ⁻ᵀ)` | S4, S10, **martingale CLT (Billingsley–Ibragimov)**, Slutsky | (cited theorem) | — |
| S12 | `det Σ_i ≥ w_min (1 - λ̄²) γ_x(0)²`, uniformly in the spacing | S8, `λ_ℓ ≤ λ̄ < 1`, `0 ≤ r < 1` | 20,000 random draws | 0 violations |

## Part 2. What the step list exposed

1. **Gap in S7–S8 (fixed).** `det Σ_i = w_i × (positive number)` is **zero, not positive, when `w_i = 0`**. The
   proposition claimed `det Σ_i > 0` for a positive economy, which allows `q_i = 0`. Fix: the statement now
   requires `w_i > 0`.
2. **Gap in S12 (fixed).** The uniform bound needs the weights bounded below (`w_i ≥ w_min > 0`). "Uniformly stable
   family" does not say that. Fix: the statement now says the bound holds on families with merged weights bounded
   below.
3. **Unstated tool in S4.** Consistency uses the law of large numbers for a stationary ergodic process. That holds
   here, since prices are a stable linear filter of i.i.d. innovations, but the proof only invokes ergodicity at S10.
   Minor; worth one clause.
4. **Cited, not proved: S11.** The martingale central limit theorem is a textbook result (Billingsley 1961,
   Ibragimov 1963). It is not in Lean's library, which is why this proposition is "partly proved" in Lean. The
   reset-experiment version is fully proved in `Paper1Tagged.lean`.

## Part 3. Oral check with a co-author (10–15 minutes, no notes)

Ask the co-author to answer each question out loud. Write down any answer that hesitates; that step needs a clearer
line in the proof.

1. Why does the tagged flow involve only cohort `i`, and not the other cohorts' rates? (S1)
2. Where does the error term `e_t = ε_t - r ε_{t-1}` come from, and why is OLS biased but IV not? (S2–S3)
3. What is `A_0`, and why does `E[x_{t-1}u_{t-1}] = w A_0`? (S5)
4. Why is every term in the determinant sum nonnegative? What would make it zero? (S8, Part 2 item 1)
5. Why is `m_t` a martingale difference, and with respect to which information set? (S10)
6. Which step uses a theorem we did not prove ourselves? (S11)

## Part 4. AI attack prompt (use only to find leads, never as approval)

Paste the proposition, the proof and the step table into two or three different models with:

> Here is a proposition, its proof, and the proof broken into numbered steps S1–S12. Your job is to break it, not to
> approve it. For each step, either (a) give a concrete counterexample (parameter values where the claim fails), or
> (b) name an assumption the step uses that is not stated in the proposition, or (c) say "no problem found". Do not
> summarize the proof. Do not say it is correct overall.

Check every claimed counterexample yourself, with code, before believing it.

---

## Template for the next proof

```
# Checking the proof of <result> (<label>)
Proof location: <appendix paragraph>.  Checks: <script> -> <json>

## Part 1. Steps
| Step | Claim (one line) | Uses | Numerical check | Result |
| S1 | ... | ... | ... | ... |

## Part 2. What the step list exposed
1. ...

## Part 3. Oral-check questions
1. ...

## Part 4. AI attack prompt
(same prompt as above)
```
