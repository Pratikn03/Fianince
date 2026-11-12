# Paper 1, theory version: Journal of Economic Dynamics and Control (draft, 12 November 2026)

Drafted by an AI system for the authors. The authors decide and edit before use.

## Why this version and this journal

- The theory is the paper's strongest part, and the two empirical tests (one supporting only a weaker reading, one
  inconclusive) count against it wherever evidence is graded. In this version the tests sit in the supplement
  with their registered readouts; the main text makes no empirical claim.
- JEDC publishes the literature the paper extends: heterogeneous feedback traders (Brock and Hommes, 1998, JEDC),
  aggregation and learning dynamics, and computational methods.
- New in this version: a calibration table (`calibration_table.py`) that turns the cost theorem into numbers. Two-group
  populations whose memories all have half-lives between 5 and 9 days need more than 4,000 years of daily prices to
  be told apart with both error probabilities at 5%, however close the market is to instability. When half-lives
  differ by a factor of three, a century can suffice; the table shows both, so a referee sees the dependence.
- Also new: the kernel stated as a minimal sufficient statistic; the remark that aggregate untagged flow adds nothing;
  lower bounds stated to hold a fortiori with unknown (a, kappa); positioning against the estimation of
  heterogeneous-agent models (Boswijk, Hommes and Manzan 2007; Franke and Westerhoff 2012; Lux and Zwinkels 2018);
  the full working paper cited as Niroula et al. (2026a) instead of "the full working paper".

Files: `Paper1_theory_main.pdf` (17 pages) and `Paper1_theory_supplement.pdf` (87 pages), built from
`paper1_theory.tex` by `build_note.py`.

## Journal requirements

The Elsevier guide for authors could not be loaded from this session. The points below follow Elsevier's
standard requirements and a third-party summary of the JEDC template. **Check them on the JEDC guide before
submitting.**
- Highlights: 3 to 5 bullets of at most 85 characters each, as a separate file (below).
- Abstract: the theory version has 147 words. If the guide sets 100, cut the sentence on position limits and the
  Lean sentence.
- Keywords and JEL codes: on the title page.
- Declarations: competing interests, funding, data availability, CRediT contributions, and Elsevier's
  "Declaration of generative AI and AI-assisted technologies" (all in the manuscript).
- Format at first submission: Elsevier economics journals generally accept any clear format at first submission;
  the 1.5-spaced PDF is used.

## Highlights (separate file)

- The feedback kernel is a minimal sufficient statistic of the trader population
- Prices identify the kernel and nothing finer, for any insider and dealer rule
- Learning composition costs data of order (Δη)^-(4K-2), even near instability
- Memories with half-lives of 5 to 9 days need 4,000+ years of daily prices to separate
- Tagging all but one memory class recovers composition at bounded cost

(Character counts: 78, 77, 76, 85, 69.)

## Cover letter (draft)

> Dear Editor,
>
> We submit "Observationally Equivalent Algorithms: What Prices Reveal About Trader Populations, and What
> Supervisors Need" for consideration at the *Journal of Economic Dynamics and Control*.
>
> The paper studies markets in which feedback traders, such as trend followers and trading algorithms, read recent
> prices and, by trading, move them, in the tradition of heterogeneous-agent models published in this journal. It
> asks what a market's price record reveals about its population of such traders. The answer is one object, the
> feedback kernel. Populations with the same kernel produce the same prices, order flows, insider profits and dealer
> inventories for any insider strategy and any causal dealer rule, so they share every equilibrium; and the kernel
> is all that prices identify.
>
> Learning anything finer is very expensive. Separating K groups whose memories lie within Δη takes data of order
> (Δη)^-(4K-2), whether the observer probes the market or waits, and the barrier does not lift as the market
> approaches instability. At illustrative parameters, two-group populations whose memories all have half-lives
> between 5 and 9 days need more than 4,000 years of daily prices to be told apart. With position limits, calm prices reveal the kernel and
> nothing more; only stress reveals how close traders are to their limits.
>
> These results sort the current choices of regulators in China, India, Japan and the European Union, which now
> require algorithmic orders to be identified: measures that treat the market as a whole can be set from prices,
> while measures aimed at particular algorithms need flow tagged by class.
>
> The core statements are machine-checked in Lean 4, and all code and proofs are public at
> https://github.com/Pratikn03/Fianince. AI tools assisted with the research and the manuscript, as declared; the
> authors have verified all proofs, formalizations and calculations. The manuscript is not published or under
> consideration elsewhere. A related working paper by two of the authors with other coauthors ("From Human Markets to
> Machine Markets") addresses a different question, the design of a pre-trade guard, and shares no results with this
> submission. The authors declare no competing interests.
>
> Sincerely,
> Pratik Niroula (corresponding author), on behalf of Prashant Niroula and Sujan Khatiwada

## Before sending

1. Confirm the requirements above on the JEDC guide for authors.
2. Add the corresponding author's postal address to the title page.
3. Confirm the declarations (competing interests; all authors approved the manuscript).
4. Run `python3 verify_formalization.py` on a machine with the Mathlib cache and commit the receipt.
5. Submit only one version at a time: if this goes to JEDC, the RFS version (`SUBMISSION_RFS.md`) is not sent.
