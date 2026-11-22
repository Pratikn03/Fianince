# Paper 1: Journal of Economic Dynamics and Control submission package (updated 22 November 2026)

Drafted by an AI system for the authors. The authors decide and edit before use.

## Files

| Use | File |
|---|---|
| Manuscript (upload as the main file) | `pdf_delivered/Paper1_JEDC_main.pdf`: 33 pages, 100-word abstract, title page with keywords and JEL codes, proofs of the main results in Appendix A |
| Online Supplement (upload as supplementary material) | `pdf_delivered/Paper1_JEDC_online_supplement.pdf`: 67 pages, every result in full, machine-check tables |
| Both in one file, for reading | `pdf_delivered/Paper1_JEDC_main_and_supplement.pdf` |
| SSRN posting | `pdf_delivered/Paper1_ssrn_complete.pdf`: 101 pages, the long version with the same corrections |
| Cited, not submitted | `pdf_delivered/Paper1_full_working_paper.pdf` (156 pages, Niroula et al., 2026d); the companion note (2026c); the earlier working paper of 5 November 2026 (2026a) |

**How to build:**
1. `ceiling_suite/papers/paper1_note/build_ssrn.py --pdf` builds the long versions.
2. `ceiling_suite/papers/paper1_jedc_short/build_short.py` then builds the manuscript and the supplement. They are
   linked so that "Supplement Theorem S…" references resolve. The build fails on any undefined reference or
   citation and on any overfull line.

## Before sending: the authors' own checks

1. **The first author reads the seven results that were added or corrected on 21–22 November 2026:**
   - Proposition 7.1(iii);
   - Proposition 7.1(iv), named instruments (added 22 November);
   - Theorem 7.3(ii);
   - Lemma 7.7;
   - Theorem 7.9;
   - Supplement Proposition S4.5;
   - Supplement Proposition S11.1.

   The manuscript says they "have not yet been checked by the authors". Do not submit while it says that. After
   checking, set `CORRECTIONS_CHECKED_BY_FIRST_AUTHOR = True` in `paper1_jedc_short/make_short.py` and in
   `t6/round9.py`, and rebuild.
2. **Author contributions (CRediT).** The manuscript says that Prashant Niroula and Sujan Khatiwada validated proofs,
   Lean files and empirical calculations. Change it to what each of them actually did.
3. **Both co-authors approve the final manuscript.** The statement "All authors approved the final manuscript" must
   be true.

## Before sending: the journal's rules

The JEDC guide for authors could not be opened from this session. Check it at
https://www.sciencedirect.com/journal/journal-of-economic-dynamics-and-control/publish/guide-for-authors for:
1. **Abstract limit.** The manuscript's abstract has 100 words.
2. **Highlights.** Elsevier asks for 3–5 bullets of at most 85 characters each, as a separate file (below).
3. **Format.** If the guide asks for double spacing or line numbers, they can be added.
4. **Blind review.** If the review is double-blind, the title page, the repository links and the self-citations
   must be anonymized. That version can be made.
5. **Declarations.** The manuscript has:
   - competing interests;
   - funding;
   - data and code availability;
   - author contributions;
   - related manuscripts;
   - Elsevier's declaration of generative AI.
6. **One journal at a time.** Do not send it anywhere else while JEDC has it.

## Highlights (separate file)

- Trader populations affect prices only through their aggregate feedback response
- Separating K trader types whose rules lie within Δ takes data of order Δ^-(4K-2)
- Without class tags, a uniform cut in feedback is minimax over labelings
- Restrictions by horizon can face the same barrier, though they need no tags
- Tags help only if relabeling is costly; untagged algorithms can crowd together

(Character counts: 79, 80, 71, 75, 78.)

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
> even in an inventory equilibrium. Learning anything finer is very expensive: in the worst case, separating K types
> whose rules lie within Δ of one another needs data of order Δ^-(4K-2).
>
> The consequences for supervision follow. Given the market's persistence and a bound on memory, a uniform cut in
> feedback can be set from prices. Without class tags it is minimax over the labelings the record allows, for any
> convex loss. A restriction by horizon, which needs no tags, can still face the full barrier. Tags help only if
> relabeling is costly. An untagged algorithm that best-responds to a fixed test crowds toward its neighbour, so the
> supervisor's information about it falls as the record grows. A calibration to Taiwan's exchange data, which tag
> daily flows by investor class, illustrates the barrier. A registered test there did not establish that the tagged
> responses are feedback, and the paper says so.
>
> The main text is self-contained, with proofs in its appendix. The Online Supplement states every result in full.
> The deterministic steps of the main results are machine-checked in Lean 4. All code, data sources and proofs are
> public at https://github.com/Pratikn03/Fianince. AI tools assisted with the research and the manuscript, as declared
> in the manuscript.
>
> The manuscript is not published or under consideration elsewhere; a version is posted on SSRN. It supersedes an
> earlier working paper of ours, dated 5 November 2026, which studied the same model and is cited in the manuscript.
> A companion note and a longer working-paper version with further supplementary results are cited and are not under
> review. A related working paper by two of the authors with other coauthors ("From Human Markets to Machine
> Markets") addresses a different question, the design of a pre-trade guard, and shares no results with this
> submission. The authors declare no competing interests.
>
> Sincerely,
> Pratik Niroula (corresponding author), on behalf of Prashant Niroula and Sujan Khatiwada

Remove "a version is posted on SSRN" if you submit before posting.
