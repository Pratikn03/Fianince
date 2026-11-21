# Paper 1: Journal of Economic Dynamics and Control submission package (21 November 2026)

Drafted by an AI system for the authors. The authors decide and edit before use.

## Files

| Use | File |
|---|---|
| Journal submission (manuscript with online supplement) | `pdf_delivered/Paper1_JEDC_submission.pdf`: 95 pages; 98-word abstract; title page with keywords and JEL codes |
| SSRN posting | `pdf_delivered/Paper1_ssrn_complete.pdf`: same content; 202-word abstract; working-paper date line |
| Optional, both | `pdf_delivered/Paper1_full_working_paper.pdf`: 150 pages, every result; cited as Niroula et al. (2026d) |

The two PDFs differ only in the abstract and the date line. Build: `ceiling_suite/papers/paper1_note/build_ssrn.py --pdf`
(journal front matter: `research_extension/paper1_publication_revision/t6/jedc_front.py`).

## Check before sending

The JEDC guide for authors could not be opened from this session, so check it at
https://www.sciencedirect.com/journal/journal-of-economic-dynamics-and-control/publish/guide-for-authors. Points to check:
1. **Abstract limit.** The manuscript's abstract has 98 words.
2. **Highlights.** Elsevier asks for 3–5 bullets of at most 85 characters each, as a separate file (below).
3. **Format.** Elsevier's "Your Paper Your Way" policy accepts any clear format at first submission, if it applies to
   JEDC. If the guide asks for double spacing or line numbers, I can add them.
4. **Blind review.** If the review is double-blind, the title page and repository links must be removed (I can make that
   version).
5. **Declarations.** The manuscript has competing interests, funding, data and code availability, author
   contributions, and Elsevier's declaration of generative AI. The guide may also ask for a separate competing-interests
   form.
6. **Corresponding author.** The postal address goes on the title page if the guide asks for it.
7. **One journal at a time.** Do not send it anywhere else while JEDC has it.

## Highlights (separate file)

- Trader populations affect prices only through their aggregate feedback response
- Separating K trader types whose rules lie within Δ takes data of order Δ^-(4K-2)
- Without class tags, a uniform cut in feedback is the minimax supervisory policy
- Tags help only if relabeling is costly; untagged surveillance can inform less
- In Taiwan, prices pin down a uniform cut but cannot attribute feedback to classes

(Character counts: 79, 80, 79, 77, 81.)

## Cover letter (draft)

> Dear Editor,
>
> We submit "Observationally Equivalent Algorithms: What Prices Reveal About Trader Populations, and What
> Supervisors Need" for consideration at the *Journal of Economic Dynamics and Control*.
>
> The paper studies markets in which feedback traders, such as trend followers and trading algorithms, read recent
> prices and, by trading, move them, in the tradition of heterogeneous-agent models published in this journal. It asks
> what a market's price record reveals about its population of such traders, and what a supervisor needs beyond it.
> The population affects prices, order flows and dealer inventories only through its aggregate feedback response,
> also in an inventory equilibrium, and learning anything finer is very expensive: separating K types whose rules lie
> within Δ of one another needs data of order Δ^-(4K-2).
>
> The consequences for supervision are sharp. A uniform cut in feedback can be set from prices, and without class
> tags it is the minimax policy for any convex loss; with partial tags the minimax policy is uniform within each
> tagged group, so the value of tags is exactly the gain from tailoring across groups. Tags help only if relabeling
> is costly, and without them more surveillance data can leave the supervisor less informed, because algorithms that
> fear targeting crowd together. Calibrated to Taiwan's exchange data, which tag daily flows by investor class, prices
> alone pin down the effect of a uniform cut but cannot attribute feedback to the classes.
>
> The deterministic steps of the main results are machine-checked in Lean 4, and all code, data sources and proofs are
> public at https://github.com/Pratikn03/Fianince. AI tools assisted with the research and the manuscript, as
> declared in the manuscript, which states which proofs each author verified. The manuscript is not published or
> under consideration elsewhere; a version is posted on SSRN. A companion note and a longer working-paper version
> with further supplementary results are cited in the manuscript and are not under review. A related working paper
> by two of the authors with other coauthors ("From Human Markets to Machine Markets") addresses a different
> question, the design of a pre-trade guard, and shares no results with this submission. The authors declare no
> competing interests.
>
> Sincerely,
> Pratik Niroula (corresponding author), on behalf of Prashant Niroula and Sujan Khatiwada

Remove "a version is posted on SSRN" if you submit before posting.
