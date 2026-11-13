# Paper 1: plan for the open problems (13 November 2026)

Written by an AI system for the authors; judgement, not independent review. Status after pull request #7: B9, B10
and a B12 floor are proved. This file takes every remaining open item, checks what it really asks, and sorts it
by how far it can honestly be taken.

Two quick checks were run before writing the plan:

- **Rank condition (R).** A block witness (each market holds its own group of at most `⌈K/D⌉` algorithms) has a
  full-rank Jacobian for every `K ≤ 10` and `D ≤ K`.
- **Moment gap of the hard pair.** The exact formula `g_K = 2^(2K-2) K [(K-1)!]^4 / [(2K-1)!]^2` matches the gaps the
  paper reports (0.222, 0.0533, 0.0131 for K = 2, 3, 4), and `g_K ≈ π/4^K`.

## A. Solvable now (each a real theorem with a short proof; about a day each)

| # | Open item (where) | What is actually open | Key idea | Deliverable | Lean | Risk |
|---|---|---|---|---|---|---|
| A1 | Rank condition (R) for every K (B5; `thm:pool`(iii), certified only for K ≤ 8) | Generic validity of (R) for all K, D | (R) is a polynomial condition, so one witness configuration suffices. Witness: split the K algorithms into D nonempty groups of size ≤ ⌈K/D⌉ and give each market weight 1 on its own group, 0 elsewhere. The Jacobian is then block-diagonal by market, and each block is a confluent Vandermonde matrix (K simple nodes, the market's group doubled) with K + ⌈K/D⌉ rows ≥ columns, so it is injective by Hermite interpolation. | `thm:pool`(iii) for every K and D; the "verified for K ≤ 8" sentence becomes a theorem | Yes: reuse the Hermite injectivity lemma already in `Paper1PronyUpper` | Low. Checked numerically for K ≤ 10. Note that generic validity gives the exact order only on classes that avoid the exceptional set; the paper must keep that qualifier. |
| A2 | Near instability, finite samples (B2; `prop:nearcrit`, only numerical 97.8–99.8%) | A bound on the n-observation divergence that is uniform in the margin ε | Toeplitz sandwich. If `(1-δ) f₀ ≤ f₁ ≤ (1+δ) f₀` pointwise, then `(1-δ)T_n(f₀) ⪯ T_n(f₁) ⪯ (1+δ)T_n(f₀)` (quadratic forms are integrals of the symbol), so all eigenvalues of `T(f₀)⁻¹T(f₁)` lie in `[1-δ, 1+δ]` and `KL_n ≤ n(δ - log(1+δ))`-type bounds hold. The paper already proves `|f₁/f₀ - 1| ≤ 4ρ` uniformly in ε (Lean `p1_spectral_ratio_close`). | `KL_n ≤ C n ρ²` for every n, uniformly in ε; the numerical paragraph becomes a corollary | Partly: the scalar steps are in Lean; the matrix sandwich needs Mathlib's Loewner order (moderate) | Low |
| A3 | Constants in K (B11) | Why the constants grow so fast | Exact Radau error formula: the moment gap of the Gauss/Gauss–Radau pair is `g_K = 2^(2K-2)K[(K-1)!]^4/[(2K-1)!]^2 ~ π 4^(-K)`, so the lower bound reads `N ≥ c σ² g_K⁻² (Δη)^-(4K-2)`, with a constant growing like 16^K | A proposition with the exact gap and its asymptotics, replacing "constants deteriorate" | Exact rational check for K ≤ 200 in Python; the general formula cites the classical Radau error theorem | Low |
| A4 | Post-breach cascade (sat section, "After the first breach: an open question") | The conjectured threshold | Mechanical impact. After a shock s, the price drop δ solves `δ = s + κ L(δ)`, where L(δ) is the liquidation by traders within δ of their limits (increasing). If `κ sup L' < 1`, the map is a contraction, so the solution is unique and continuous in s. If `κ L'(δ₀) > 1` at some δ₀, there are shocks at which the minimal fixed point jumps (a cascade). This is the standard fire-sale fixed-point argument applied to the paper's limit model. | A theorem stating the threshold exactly, replacing the conjecture paragraph | Yes: contraction and monotone fixed points on ℝ | Low–medium: the model of who liquidates must match `prop:delever` |
| A5 | Long-lived strategic insider (B7) | How an insider who knows the value trades against the groups' memory | Two clean results. (a) With the paper's mechanical impact, the insider's problem is linear-quadratic control: solve by a Riccati recursion, show her optimal trades and profit depend on the population only through the kernel (so she cannot reveal composition either), and give her pump-and-dump gain from feedback. (b) With a Kyle market maker, flow that is a function of public prices carries no information, so the market maker nets it out, it has no price impact, and the insider's equilibrium is Kyle's. Feedback matters only through the impact assumption. | Proposition with (a) and (b) | (b) yes; (a) the Riccati algebra for a fixed horizon | Medium: (a) needs care on existence for long horizons |
| A6 | Deadband rules (part of B1: nonlinear rules have no upper bound) | Whether a nonlinear family can be identified | For soft-threshold (deadband) rules `ψ(u) = u − δ₀ sign(u)` beyond the band, large probes make the response linear up to `O(δ₀/A)`, so Prony on probe-scaled taps recovers composition with an extra bias `O(δ₀/A)`. This gives an upper bound for a nonlinear family, with an explicit probe size. | Proposition for the deadband family | Partly | Medium: must state exactly which nonlinear families it covers. The "dual-tone intermodulation" story in the deleted file is not needed and not claimed. |

## B. Harder (weeks; outcome uncertain)

| # | Item | Why harder | Plan |
|---|---|---|---|
| B-1 | Largest Gauss–Radau weight exceeds largest Gauss weight, every K (`prop:targetK` note; numerical K ≤ 200) | Needs asymptotics of Legendre quadrature weights with explicit error bounds, plus a finite check | Use the explicit weight formulas and known bounds on Legendre zeros; check K ≤ K₀ exactly; prove K > K₀ from the expansion `0.79/K²`. Value is low: `prop:targetK` already covers every K through the family R_c. |
| B-2 | Rates for higher nonlinear orders of saturating identification (`thm:satident`) | A nonlinear moment problem under stress probes | Expand the response in odd powers of the probe size, and bound each order like the cheap-questions modulus; attempt order 3 first. |
| B-3 | Rate for noisy stress identification (B3) | Needs a curvature (margin) condition and a uniform rate for the criterion | Margin plus a uniform deviation bound gives `O_P(N^-1/2)` at configurations with positive curvature. |

## C. Long-term or out of scope for this paper

| # | Item | Assessment |
|---|---|---|
| C-1 | Full rational-expectations equilibrium with forward-looking dealers and deleveraging traders | Research problem. A4 gives the mechanical-impact threshold; with forward-looking dealers the terminal price should be the minimal fixed point of A4, but the dynamics need a real equilibrium model. Keep as open. |
| C-2 | General learning traders (B8 beyond bounded sensitivity) | Sufficiency fails in general for history-dependent nonlinear learning. Keep `prop:observer` for its class and leave the rest open. |
| C-3 | Composition from pooling at the exact order on every class | Needs (R) everywhere on the class, not only generically; A1 covers generic validity only. |

## Order of work

1. A1 and A3 first: they convert two "verified numerically" statements into theorems and cost little.
2. A2, which closes B2.
3. A4 and A5, which close the two open economic questions referees will push on.
4. A6.
5. B-items only if time remains.

Each item ends with the paper text, a Lean module where feasible (no placeholder statements, axioms audited, and the
statement compared against the prose), a numerical check in `run_all_checks.py`, and a row in the author checklist.
Nothing is called machine-checked unless the Lean statement is the claim.

## Status, 13 November 2026 (evening)

A1–A6 are done: paper text in core `sup_tail.tex`, `supp_nearcrit.tex`, `supp_openres.tex` and `sat.tex`; Lean in
`Paper1RankCondition.lean` and `Paper1OpenResolved.lean` (standard axioms only); checks in
`research_extension/open_problems/open_checks.py` (all pass). B-1 to B-3 and C-1 to C-3 remain open.
