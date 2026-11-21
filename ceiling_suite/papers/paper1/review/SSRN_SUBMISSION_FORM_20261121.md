# SSRN submission form: Paper 1 (copy and paste)

Prepared 21 November 2026 by an AI system for the authors.

## Before you submit (all three must be true)
1. Every row of `AUTHOR_PROOF_CHECK_NEW_RESULTS_20261120.md` has an author checker and an outcome.
2. Pratik, Prashant and Sujan have each approved this version for posting.
3. In `research_extension/paper1_publication_revision/build_revision.py` set `AUTHOR_CHECK_DONE = True` and
   `ALL_AUTHORS_APPROVED = True`, then run `python ceiling_suite/papers/paper1_note/build_ssrn.py --pdf`.
   This removes exactly two sentences (the "being checked" sentence and "approval ... is pending"); the build was
   tested with both flags on 21 November and changes nothing else.

## File
`pdf_delivered/Paper1_ssrn_complete.pdf` (main text and supplement, 137 pages).

## Title
Observationally Equivalent Algorithms: What Prices Reveal About Trader Populations, and What Supervisors Need

## Authors (in this order)
Pratik Niroula (Minnesota State University, Mankato); Prashant Niroula (Tribhuvan University);
Sujan Khatiwada (Minnesota State University, Mankato). Submitter: Pratik Niroula.

## Abstract
Algorithmic traders read prices and, by trading, move them. We ask what a market's public record reveals about its
population of such traders, and for which supervisory actions that is enough. When traders respond to a common public
signal, the population enters prices, order flows, insider profits and dealer inventories only through its aggregate
feedback response, and this remains true when price impact and persistence arise from competitive dealers who bear
inventory risk. Learning anything finer is expensive. Under regularity conditions, telling apart K trader types whose
rules lie within Δ of one another takes at least of order Δ^-(4K-2) observations for any smooth family of rules, and
for linear memory rules satisfying a rank condition this order is attained. The difficulty has an exact source: with
Gaussian news, what a record reveals about which of two populations is trading equals the cumulative forecast loss
from confusing them. A uniform cut in feedback can therefore be set from prices, while restricting one class of
traders can be safe in one population and unsafe in another with nearly the same record. Tagging all but one memory
class removes the spacing penalty for recovering class weights. Registered empirical tests are pending; core steps
are checked in Lean 4.

## Keywords
algorithmic trading, feedback trading, aggregate response, identification, supervision, disclosure

## JEL classification
C32, D83, G14, G18

## Network and subject
Financial Economics Network (FEN): Capital Markets: Market Microstructure; also Econometrics: Econometric Modeling.

## Notes
- The abstract cites a companion note (Niroula et al., 2026c, `paper1b_companion.pdf`). Post it on SSRN too, or
  readers following "C1.1" references will have nothing to open.
- After posting, revisions are uploaded to the same SSRN record ("Revise" in the SSRN author dashboard).
