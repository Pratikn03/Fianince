# Paper 1: target journal, format and cover letter (draft, 12 November 2026)

Drafted by an AI system for the authors. The authors decide where to submit and edit the letter before use.

## Journal choice

**First choice: The Review of Financial Studies (RFS).**

Why it fits:
- The paper is a finance theory paper with a policy question (what supervisors can learn from prices about
  algorithmic traders). RFS publishes market-microstructure theory with regulatory implications.
- The note format (13-page main text, long Internet Appendix with proofs and machine checks) matches how RFS
  handles long theory papers.
- RFS requires public code at publication; the repository already holds all code, Lean proofs, specifications and
  result files.

What RFS requires at submission (checked 12 November 2026, journal instructions and SFS submission page):
- Abstract of at most 100 words, or the submission is returned. **Done:** the note's abstract is exactly 100 words.
- Double-spaced manuscript, or it is returned. **Done:** `paper1_note_submission.tex` is the double-spaced build
  (`Paper1_note_submission_main.pdf`, 17 pages; `Paper1_note_submission_supplement.pdf`, 55 pages).
- Title page with title, authors, affiliations and the corresponding author's contact details. **To add:** a
  corresponding-author line (address and telephone), which only the authors can supply.
- Submission fee: USD 400 (SFS members) or 460 (non-members) for authors in high-income economies; the
  middle- and low-income rates apply only when all coauthors qualify.
- Working-paper posting is allowed before acceptance.

**Second choice: Journal of Financial Markets.** Microstructure audience, theory welcome, and the regulatory
question is central to its readership. Use if RFS declines.

**Not recommended now: Quantitative Economics.** Its instructions require proofs of key results in a
self-contained main paper, a supplemental appendix of at most 25 pages, 1.25-inch margins and at most 32 lines
per page. The current design (short main text, 55-page supplement with the proofs) does not meet these rules
without a full restructuring.

## Cover letter (draft)

> Dear Editor,
>
> We submit "Observationally Equivalent Algorithms: What Prices Reveal About Trader Populations, and What
> Supervisors Need" for consideration at *The Review of Financial Studies*.
>
> Regulators in China, India, Japan and the European Union now require algorithmic orders to be identified, while
> the SEC withdrew its proposal on predictive data analytics in 2025. Behind these choices is a question the paper
> answers: what does a market's price record reveal about its population of feedback traders, and for which
> supervisory decisions is that enough?
>
> The answer is one object, the feedback kernel. Two trader populations with the same kernel produce the same
> prices, order flows, insider profits and dealer inventories for any insider strategy and any causal dealer rule,
> so they have the same equilibria; and the kernel is all that prices identify. Learning composition, such as
> which group is largest, costs data of order (Δη)^-(4K-2) for K groups whose memories lie within Δη, by
> probing or by passive observation, and the barrier does not lift as the market approaches instability.
> Market-wide supervisory actions therefore need only the kernel; actions aimed at one group need flow tagged by
> class, which is what the new identification regimes collect. With position limits, calm prices reveal the
> kernel and nothing more.
>
> We report two registered tests, each run once with its wording fixed in advance. On Taiwan's tagged
> exchange flows, prices improve forecasts of foreign investors' flow as the registered criterion requires, but a
> pre-specified check attributes the gain to prices revealing past flow rather than to feedback. A test of the
> position-limit prediction on Binance perpetual futures is inconclusive. We report both as they came out.
>
> The core statements are machine-checked in Lean 4. All code, proofs, specifications and result files are public
> at https://github.com/Pratikn03/Fianince. AI tools assisted with the research and the manuscript, as disclosed
> on the title page; the authors have verified all proofs, formalizations and calculations.
>
> The manuscript is not published or under consideration elsewhere. A related working paper by two of the authors
> with other coauthors ("From Human Markets to Machine Markets") addresses a different question, the
> design of a pre-trade guard, and shares no results with this submission. The authors declare no competing
> interests.
>
> Sincerely,
> Pratik Niroula (corresponding author), on behalf of Prashant Niroula and Sujan Khatiwada

## Before sending

1. Add the corresponding author's postal address and telephone to the title page.
2. Confirm the declarations (author contributions, funding, competing interests) in the manuscript.
3. Re-run `python3 verify_formalization.py` on a machine with the Mathlib cache and commit the new receipt.
4. Pay the fee and submit `Paper1_note_submission_main.pdf` with `Paper1_note_submission_supplement.pdf` as the
   Internet Appendix.
