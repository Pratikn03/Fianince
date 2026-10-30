# Internal referee report on Paper 1 (Phase 11)

*What Prices Reveal About Hidden Trader Populations, and What Identifying Them Costs*, revision of 30 October 2026.
Written as a skeptical referee would, by the authors' AI assistant. It does not replace independent review.

## Summary of the submission
Linear closed-loop market; K trader groups with exponential memory. Prices identify the merged measure M only.
Separating groups costs Θ((Δη)^−(4K−2)) experiments (matching bounds), the same order passively, 1/log N without
the exponential form; for a known pair, quantity δ^−2 and capital δ^−4. Class-tagged records save (Δη)^−(4K−4);
a stylised decision model says when they are bought. Registered tests on CFTC and Binance class data.

## Major comments
1. **Novelty of the rates.** The K-group exponent is the known mixture/super-resolution rate (the paper says so;
   Wu–Yang's n^−1/(4k−2) is the same object). The closed loop enters through a smooth invertible map once a and κ
   are known, so it does not change the rate. *Resolution in this revision:* the text now says the closed loop
   decides which method is valid, not the rate. The contribution must rest on (i) the passive equivalence via
   minimum phase, (ii) the conversion of samples into executed quantity and capital, (iii) the value of class
   records, and (iv) the general-memory logarithmic rate. A specialist should confirm (iv) is not an immediate
   corollary of known deconvolution or moment results. **Status: open (needs outside expert).**
2. **Known primitives and reset experiments.** The lower bounds assume known a, κ and noise law, and N independent
   experiments from a reset state. Markets do not reset. The paper now states that unknown primitives only
   enlarge the candidate set (lower bounds survive) and that its upper bounds assume them known. A referee will
   still ask how far stationary, non-reset data are from the reset model; the passive theorem answers part of this.
   **Status: addressed in text; a short simulation with non-reset data would strengthen it (optional).**
3. **Economic model.** Trader rules are exogenous (filtering and learning microfoundations only), groups do not
   react to being observed, and probes execute against a linear book. The new observer subsection fixes the
   institution, options, timing and money concepts. The referee will still see no equilibrium. **Status: stated as
   a limitation; acceptable for QF, a weakness for a top finance journal.**
4. **The CAT comparison.** CAT serves many purposes beyond attribution; probing loss is a lower bound on the cost of
   learning from prices, renewed weekly by assumption. The paper says both. Keep the comparison as an illustration,
   not a cost–benefit verdict. **Status: addressed.**
5. **Empirical link.** Class data are positions, not tagged flow; returns stand in for the pricing error; the
   registered Binance test failed one criterion; the CFTC trend-following hypothesis failed; class-data gains in
   state tracking are persistence. The new "what the data can and cannot test" paragraph states the scope.
   A referee may ask for a test closer to the theorem: the tagged-flow IV on weekly CFTC class flows.
   **Status: optional new analysis; must be registered before data are touched.**
6. **Length and focus.** The full preprint runs to about 110 pages. A QF submission should be about 35–45 pages:
   model, identification, costs, disclosure and its value, CFTC test; everything else to an online appendix.
   **Status: open (Phase 13 build).**

## Minor comments (fixed in this revision unless noted)
- Resolvent identity missing the factor z^−1 in three places (moduli unchanged; the non-vanishing argument in the
  passive theorem restated correctly). Fixed; numerical check in `review/phase7_checks.json`.
- Results map row on the CAT budget contradicted its own table. Fixed.
- Theorem `thm:merged`(ii) used K for a family constant. Renamed C_F.
- "Theorems" referring to a lemma. Fixed. Labels `thm:capital` (a lemma) and `prop:passive` (a theorem) are
  internal and invisible; left.
- Abstract and introduction said prices reveal "nothing finer" and that finer distinctions are "possible", mixing
  non-identification with finite-sample difficulty. Rewritten to keep the three concepts apart.
- The definition of an "experiment" in the K-group bound was implicit. A paragraph now defines it and shows the
  order is the same for any probe energy.

## Recommendation (as a QF referee)
Major revision. The theory is careful and the honesty about failed tests is a strength. Acceptance depends on
comment 1 surviving an expert's reading and on a focused, shorter manuscript.
