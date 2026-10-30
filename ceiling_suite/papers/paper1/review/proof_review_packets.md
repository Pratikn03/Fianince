# Paper 1 — proof-review packets (plan of 30 Oct, Phase 3)

One packet per area. Each lists the results, what they depend on, the steps to check line by line, and the
questions most likely to expose a gap. Reviewers record each step as **checked / objection / corrected / open** in
the table at the end, with the page of `paper1_ssrn.pdf` they read.

**Independence.** This is a team review. Prashant is a listed author and the team wrote the paper with AI help,
so this review does not count as independent; a journal submission still needs an outside specialist for areas
C and D. Computations support the review (identities, counterexamples, boundary cases) but do not replace it.

## Dependency map

```
model (1)-(6) ─► lem:cm (positive geometry) ─┬─► thm:quantity ─► thm:cap, thm:capital (with lem:toeplitz)
                                             ├─► thm:spectral (lem:toeplitz) ─► thm:adaptive, thm:rh
                                             ├─► prop:tagged (autocovariances ≥ 0) ─► thm:discvalue
                                             └─► thm:kcohort (|H| bounded below for the lower order)
model ─► thm:merged ─► thm:minphase ─► prop:passive (+ moment constructions of thm:twocohort, thm:kcohort)
thm:kcohort + prop:esprit (Prony on the extracted kernel) ─► minimax order ─► thm:discvalue, CAT dollars
lem:altpair ─► thm:general ;  passive and tagged orders ─► prop:choice (as modelling inputs)
```

## A. Model timing and merged equivalence — first Pratik, second Prashant
Results: equations (1)–(6), `lem:micro`, `lem:cm`, `thm:merged`, `rem:scope`.
Steps: (1) derive H(z) = κz/(z − a − κG(z)) from (1)–(2) with price-first timing; (2) check G(z) = Σ wᵢ z/(z − rᵢ)
with wᵢ = qᵢηᵢ; (3) the "if and only if" in (i), including cohorts at the same rate and signed weights that cancel;
(4) the no-cancellation argument and the McMillan degree for a > 0 and a = 0; (5) the ΔG formula and the bound
|ΔG| ≤ 2qδ²/ε³ in (ii); (6) the resolvent identity H_δ − H₀ = z⁻¹H_δH₀ΔG (corrected on 30 Oct).
Questions: Does "identical price responses for every probe" reduce to equal impulse responses? What happens at
η = 1 and at rᵢ = 0? Is the symmetrisation in `lem:cm` valid when a = 0 (continuity argument)?
Supporting computations: `review/phase7_checks.json` (exact equivalence 3e−17, signed weights included),
`R2-T5_merged_invariance`.

## B. Quantity, losses and capital — first Prashant, second Sujan
Results: `thm:quantity`, `lem:toeplitz`, `thm:cap`, `prop:disclosure`, `thm:capital`, `thm:spectral`,
`thm:adaptive`, `thm:rh`, `cor:garch`.
Steps: (1) d₂ = −κ²qδ² from k₀ equal and Δk₁ = −qδ²; (2) the exact error Φ(−V‖d_T‖/2σ) and why a first-period
pulse attains it; (3) the cash ledger behind ½vᵀT_hv; (4) in `thm:cap`, every entry of A_t is at most κ/2;
(5) the coercivity constant m = κ(1 − r)/(1 + r) and the Pinsker step in `thm:capital`; (6) the Toeplitz symbol
equals 2Re H − κ, so L(v) = (1/2π)∫g|V|²; (7) optional stopping in `thm:adaptive`.
Questions: Is the margin constraint applied at every mark, including after the last trade? Does `thm:adaptive`
need E[τ] < ∞ or only τ < ∞ a.s.? Where does flatness (Σv = 0) enter, and is it needed for the lower bound?
Are capital required, round-trip loss and annualised loss used consistently (Section `sec:observer`)?

## C. Unknown-mixture bounds — first Sujan, second Prashant (outside specialist needed)
Results: `prop:crb`, `thm:twocohort`, `thm:kcohort`, `prop:esprit`, `thm:uniformw1`, `lem:altpair`, `thm:general`.
Steps: (1) Gauss and Gauss–Radau rules agree on moments 0…2K−2 and differ at 2K−1; (2) kernel differences are
O((Δη)^{2K−1}) with a nonzero leading term, and the response difference is of the same order from both sides
(needs 1/H bounded on the circle); (3) Le Cam with N Gaussian experiments; (4) in `prop:esprit`, the h → k map is
Lipschitz independently of Δη, the confluent Vandermonde determinant, and uniform inverse-function constants on
the compact class; (5) the class must contain the Gauss–Radau pair for the orders to match; (6) `lem:altpair`
equioscillation construction; (7) `thm:general` lower and upper bounds, including the choice of L.
Questions: In `thm:kcohort`, what accuracy does "error probability below 1/4" refer to? Is `thm:uniformw1`
(no Lean mapping) a correct use of the Wu–Yang moment comparison? Is the 1/log N result an immediate corollary
of known deconvolution or moment-method results (novelty question)?
Supporting computations: Radau gaps (Table), Le Cam slopes K = 2–4, Prony slopes K = 2–5, estimator comparison.

## D. Passive identification and testing — first Prashant, second Pratik (outside specialist needed)
Results: `thm:minphase`, `prop:passive`, `prop:passive0`.
Steps: (1) zeros of H are the memory rates and lie inside the disk; uniqueness of the minimum-phase factor;
(2) u = ϱ − 1 = 2Re(z⁻¹H₁ΔG) + O(|ΔG|²) and sup|u| = O(ε) uniformly; (3) c(ω) is not identically zero
(the corrected exterior-analytic argument); (4) the new nonasymptotic bound KL_T ≤ C·T·ε² (Toeplitz eigenvalues
within the symbol's range; spectra bounded above and away from zero on the compact family); (5) Bretagnolle–Huber.
Questions: Is "bounded away from zero, uniformly on the family" justified for every member (no zeros on the circle)?
Is the statement now consistently lower-bound only throughout the paper? Does `prop:passive0` (Chebyshev) use the
right product variance for uniform innovations?

## E. Tagged information and disclosure choice — first Sujan, second Pratik
Results: `prop:tagged`, `thm:discvalue`, `prop:choice`.
Steps: (1) the tagged recursion ũ = rũ₋₁ + wx + e with MA(1) error, instrument validity; (2) det Σᵢ formula and
positivity; (3) long-run variance Ωᵢ; (4) in `thm:discvalue`, N_t ≍ σ_f² for fixed accuracy and σ_f²(Δη)^−2 for
rates resolved to a fraction of their spacing; (5) `prop:choice` case analysis (statement corrected on 30 Oct:
G rises to Δη_p, falls while positive, is negative beyond (c_p/c_t)^{1/(4K−4)} and rises toward zero from below).
Questions: Is the IV estimator's precision really independent of spacing for the *rates* as well as the weights?
Are T_p and T_t in `prop:choice` legitimately taken from the passive and tagged orders (constants c_p, c_t)?
Supporting computation: `review/prop_choice_check.json` (19,814 cases).

## F. Central argument as a whole — all three
Does each sentence of the abstract follow from a stated result under stated assumptions? Are dollar figures
confined to the probing observer? Are fitted persistences kept apart from learning memory? Is every number traced
in the reproducibility map?

## Review record

| Area | Step | Reviewer | Page | Status | Note |
|---|---|---|---|---|---|
| A | 1 | | | | |
