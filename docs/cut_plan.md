# Cut plan: Paper 1, Paper 2 and the thesis

Prepared 25 October 2026, to be applied in one pass **after** the professors' feedback on the current versions has been
merged (their comments refer to the versions they read). Nothing here has been applied yet.

The principle (from the mock referee report, point 7): each paper is built around one theorem and one piece of evidence;
everything else moves to an online appendix or to the thesis, where it stays citable.

## Paper 1 (now 97 pages working / 80 pages QE) → about 40 pages main text

Main text, about 110k characters of LaTeX source (now about 174k before the appendix):

| Keep in the main text | Source now | Change |
|---|---|---|
| Introduction | `p1_front.tex` | Lead with the two-Kalman-desk worked example (referee minor point); related literature cut to one page; contributions as three numbered results |
| Model and microfoundations | `p1_front.tex` | Keep; the discussion of assumptions shortened to the reset contract (referee point 3: say early that the theorems describe a probing supervisor) |
| The identification boundary: merged equivalence | `p1_ident.tex` | Keep, with "merged measure" defined in words first (referee minor point) |
| Probing resources: quantity, capital, worked example | `p1_ident.tex` | Keep quantity and the capital order; execution-cost and counterparty subsections to the appendix |
| Primitives and tied intensities (Propositions primitives, tied) | `p1_ident.tex` | Keep: they answer referee point 2 |
| Many unknown cohorts: the (Δη)^-(4K-2) barrier; general memory 1/log N; passive cost | `p1_mixture.tex` | Keep the three statements with short proofs in the appendix |
| What disclosure buys: value of tagging; disclosure in real data | `p1_disclosure.tex` | Keep, rewritten around the registered evidence: E1v2 P2 (30/30), D1 P2, C2 P3 (29/29 at a matched horizon), the narrowed claim (persistence, not memory), and the jackknife caveat |
| Implications; conclusion | `p1_empirics.tex` | Keep, shortened |

Move to the online appendix (still in the PDF supplement, still cited):

| Move | Source now | Why |
|---|---|---|
| Account-level capital (whole section) | `p1_account.tex` | Strong but secondary to the barrier; referee point 6 sensitivity table goes with it |
| Why naive pole fitting fails; Cramér–Rao benchmark; near-colliding uniform rate | `p1_mixture.tex` | Technical support for the barrier |
| Robustness to nonlinear and adaptive rules | `p1_mixture.tex` | One paragraph remains in the main text |
| A spectral blind spot | `p1_disclosure.tex` | Separate result, not needed for the main line |
| Empirical feedback and its measurement (clock alignment, order splitting, 30 markets, fee events) | `p1_empirics.tex` | Measurement section of its own; better as a companion note |
| CFTC trader-class reports | `p1_disclosure.tex` | One paragraph remains; weekly data versus intraday memories (referee point 5) explained there |
| Lean declarations | throughout | One sentence in the introduction; the rest in the replication package (referee minor point) |

Also: numbers to two or three significant figures (referee minor point).

## Paper 2 (now 131 pages working / 115 pages JF) → about 45 pages main text

Main line: the summed response is the safety statistic; it is certified at cost exactly one logarithm; the guard built on
it is the largest safe admission rule; evidence = the pre-registered thin-book forecasting results. Move to the online
appendix: the information-safety extensions already reproduced in the thesis (Chapter 4), the equilibrium material, the
mechanism tests that failed (kept as a table with references), and the bootstrap diagnostics. State G1 (the guard does
not beat a volatility limit at matched exposure) in the main text.

## Thesis (now 217 pages) → about 130 pages main text plus appendices

1. Page 1 states one claim: safety can be certified from far less information than it takes to identify the agents, and
   with enough public data the safety question is answered in markets whose agents stay unidentified.
2. Chapter 1 shortened to 10 pages; the status table moves to Appendix A.
3. Chapters 2 and 3 become the cut Papers 1 and 2 (their supplements move to appendices).
4. Chapter 4 keeps: the framework, the dichotomy (Theorem dich, Proposition parametric, Theorem philog), passive
   certification (Theorem passivecert) and Corollary loopmargin, natural experiments and overshoot, contrarian agents.
   Robust/nonlinear safety, learning agents and strategic agents move to an appendix chapter.
5. Chapter 5 keeps the registered-tests table and one paragraph per test; pilots move to an appendix.
6. The flagship exhibit (the learning curve: decided vs identified share against sample size, and the risk prediction,
   from Test F1 if registered and run) goes in Chapter 1 and Chapter 5.
