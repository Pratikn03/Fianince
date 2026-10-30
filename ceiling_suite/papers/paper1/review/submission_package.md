# Paper 1 — SSRN checklist and Quantitative Finance package (Phases 12–13)

## SSRN (full preprint, `paper1_ssrn.pdf`)
Requirements per SSRN's author help (free account; English title and abstract; date; each author's name,
affiliation and email; copyright permission if applicable; PDF showing all authors and affiliations).

| Item | Status | Owner |
|---|---|---|
| Title: *What Prices Reveal About Hidden Trader Populations, and What Identifying Them Costs* | Done | — |
| Abstract (paper's abstract, ~260 words) | Done | — |
| Keywords: identification, trader heterogeneity, market microstructure, system identification, minimax sample complexity, value of disclosure, audit trails | Draft | Pratik approves |
| JEL: C14, C32, C58, D83, G14, G18 | Draft (G18 added for regulation) | Pratik approves |
| Suggested networks: FEN (Capital Markets: Market Microstructure); ERN (Econometric Modeling) | Draft | Pratik |
| Byline and affiliations | **Blocked**: both authors listed; single-author only with Prashant's written agreement | Pratik |
| Companion-paper citation byline (two vs five authors) | **Blocked** | Pratik |
| AI-use statement (two different versions exist) | **Blocked**: authors must confirm which is accurate | Pratik |
| Preprint allowed by target journal | **Blocked**: ask the QF editorial office whether SSRN counts as a non-commercial server; otherwise post on arXiv | Pratik |
| Code link (public repository) | Done in SSRN build | — |
| Final post/hold | **Hold** until the four blocked items close | — |

## Quantitative Finance
- **Fit.** QF publishes quantitative work on financial markets, including agent-based modelling, financial
  econometrics and market microstructure (scope checked 30 October). Paper 1's estimation-limit result speaks
  directly to the agent-based estimation literature, which is the strongest argument for fit.
- **Not verified here:** current length limits, abstract limit, reference style and whether review is
  double-blind. The T&F author-instructions page could not be reached from this session; check it before
  building the submission version. The anonymous build (`make_wfa.py`, output `paper1_wfa.pdf`) is ready if
  review is double-blind.
- **Version to submit:** a focused 35–45 page manuscript (to build after the expert review), with the full
  preprint as the online appendix.

### Cover letter (draft; fill in after the blocked items close)

Dear Editors,

We submit "What Prices Reveal About Hidden Trader Populations, and What Identifying Them Costs" for
consideration in *Quantitative Finance*.

Empirical work routinely estimates models in which heterogeneous trader populations feed back into prices, and the
parameters that separate the populations are often estimated imprecisely. We show why, and at what cost. In a
linear closed-loop market, prices and anonymous order flow identify a single merged summary of the trader groups.
Groups with different memories are identified in principle, but separating K of them takes a number of
experiments, or of passive observations, of exact order (Δη)^−(4K−2) in their memory spacing; without the
exponential form, accuracy improves only as 1/log N. In a market these sample costs become executed quantity and
trading capital, which we bound from both sides with explicit constants. Records tagged by trader class remove
the dependence on spacing, and we characterise when an observer should buy them. Registered tests on the CFTC's
trader-class reports and on Binance's class ratios check the main observable prediction.

The rates for mixtures are known; our contribution is their closed-loop, passive and financial form and the value
of disclosure. A preprint is available at [SSRN/arXiv link]; code and registered specifications are public.
The manuscript is not under consideration elsewhere.

[Authors, affiliations]
