# P5 — AI-assisted internal review: senior faculty first impression, writing, length and integrity
**Basis:** 124-page manuscript PDF plus a public repository landing-page check. Not a human professor, independent model, admissions assessment or audit of author identities. Page references below are **printed manuscript pages** (PDF page = printed + 3 after the front matter). This report is an internal stress test, not an endorsement.

## A. Verdict
**I would not forward the PDF to a faculty colleague in its current form.** My five-minute impression is that a promising, intelligible central question has been buried under a campaign to demonstrate everything: exact identification, finite-mixture rates, passive inference, probe quantity, capital, class-tagging, registered CFTC/Binance tests, spectral instability, feedback indicators, policy choice, and a separate decision paper in an appendix. The front matter is much better about limitations than many working papers, but the dense 124-page construction, dollar-scale comparisons and repeatedly advertised 8/8 and 29/29 counts make it hard to tell the *single validated* contribution from known tools and experiments that failed. Most readers deciding whether to reply to an unsolicited paper will not make it to page 60. Publication on SSRN carries the authors' names: I would demand a cleaner 115-page archive build and a much shorter 10–15-page faculty-reading version.

## B. SSRN readiness
**5.5/10 now; 8/10 after the high-priority fixes.** For a professor's invitation to collaborate, a 10-page rigorous summary plus the full reproducibility appendix would send a better signal than the current stand-alone 124-page manuscript.

## C. Issue register
### FATAL
No proven fabrication, false author affiliation or deliberately misleading AI statement was established from the PDF. Authorship, data access and computation are **not externally verified**. **The one genuine integrity gate** is that both authors must personally confirm (i) authorship and consent, (ii) they can explain and stand behind proofs and code, and (iii) the AI description truthfully covers all tools and work. If any of those is false, **do not post** until resolved.

### MAJOR
1. **The title sounds more structural than the evidence — title page (PDF p. 1), front matter. VERIFIED text, interpretation SUSPECT.** Quote: “What Prices Reveal About Hidden Trader Populations, and What Identifying Them Costs.” The real theorem concerns a particular linear feedback observation contract, and the data concern fitted position persistence. **Fix:** consider “Identification and Measurement Costs of Hidden Feedback Cohorts in a Linear Market” (or retain current title with an abstract first sentence that says *linear reduced-form model* immediately).

2. **Abstract is overloaded — front matter PDF pp. 1–2. VERIFIED.** Quote: “On classes rich enough to contain the hardest configurations, separating K unknown groups whose memories differ by ∆η takes Θ((∆η)^−(4K−2)) independent experiments”. The same abstract then asks readers to assimilate passive bounds, tagged sample-factor savings, $15m–$356m annual losses, CFTC 8/8, Binance 29/29, near-unit roots and failed forecasts. **Fix:** use the ≤200-word replacement below; move dollar figure and multi-market counts to text/figures.

3. **First two introduction pages give too many contributions — printed pp. 1–3, §1. VERIFIED.** Quote: “Correctly tagged records remove the barrier.” Then much of the *real empirical* effect is obtained from observed position stocks, not the model's flow tag. **Fix:** contribution list limited to 3 items: (i) precise merged-measure observation equivalence; (ii) information and capital cost under specified contracts; (iii) attribution-data value and what the empirical proxies can/cannot test. List the negative evidence prominently.

4. **Paper is stitched together — printed pp. 3–12, §§1–1.1; pp. 59–61, §§7–8. VERIFIED structure.** Quote: “Two further results complete the picture” introducing transient loss and feedback indices. Those are two *additional papers* that weaken the narrative of this paper; Appendix I then adds another full decision theorem. **Fix:** move the spectral-blindness theorem and the feedback-index empirical programme to separate companion supplements/papers, retaining one paragraph of motivation if necessary. Keep only a succinct Appendix I decision-contrast corollary in this paper.

5. **Most powerful negative result is displaced from the main contribution — printed p. 4, §1; pp. 57–59, §6.4. VERIFIED from manuscript.** Quote: “Our pre-registered real-data test of the identification boundary failed its criterion on one of its three parts.” The central test had 5/30 precise aggregate-response cases, not just a procedural caveat. **Fix:** make the abstract say “The empirical proxies do not validate the structural rates; the registered merged-response and return-forecast tests did not meet their criteria.” The precise pass/fail criteria should appear in the summary table, not only §6.4.

6. **Numbers risk appearing more authoritative than they are — printed pp. 1–2, §1; p. 48 §6.2; p. 61 §8. VERIFIED as hypothetical.** Quote: “would lose at least $15 million to $356 million a year per market.” This assumes weekly repeated deterministic experiments, illustrative structural parameters and a noise proxy; it is not a forecast of any real desk's cost or regulator's benefit. **Fix:** move to a numerical illustration with an explicit subtitle `hypothetical outside-trader benchmark; not a welfare estimate` and do not foreground it in the abstract or conclusion.

7. **'Registered' is not the same as an external preregistration — PDF p. 3, Reproducibility. VERIFIED wording; timeline unverified.** Quote: “each specification reached the public repository in the same push as its results.” The manuscript does state “not registration with an independent registry,” which is correct and should be preserved. **Fix:** use “author-declared pre-data specification, committed alongside results; no independent preregistration” at first mention. An independent timestamp is absent on the evidence supplied.

8. **AI statement needs author verification — printed p. 63, Disclosures. VERIFIED present; truth NOT VERIFIED.** Quote: “The authors used Claude (Anthropic), an AI assistant, to write and debug analysis code, run checks of derivations and numerical results, and draft and edit text.” This is a substantive statement; if ChatGPT, other AI models or AI review contributed materially, update it to **all actually used tools** and distinguish AI-assisted internal checking from independent proof verification. **Fix:** both authors approve a one-paragraph activity-based AI declaration, plus a human responsibility statement; keep a private author contribution log.

9. **Public GitHub link is real but too broad — PDF p. 2, Code and data; printed pp. 117–121, Appendix J. VERIFIED link exists; clean reproduction NOT VERIFIED.** Quote: “All code, registered test specifications and result files are public at https://github.com/Pratikn03/Fianince.” The URL resolves, but the public repository is multi-project and full of prior drafts; locating a frozen one-command Paper 1 replication is burdensome. **Fix:** link a specific release/tag/commit and `paper1/README` with an exact environment, a manifest and table-to-script map. Keep historical work, but do not make reviewers navigate it to decide whether you are serious.

10. **Money, social cost and policy occupy too much front matter — printed pp. 2–3, §1. VERIFIED.** Quote: “an economies-of-scale argument for market-wide regimes such as CAT.” This is a conditional fixed-cost proposition rather than a benefit assessment of CAT. **Fix:** omit CAT acronym from the abstract; use a cautious conditional one-paragraph policy translation after all contracts are stated.

11. **Internal notebook and run language remains in the manuscript, though mostly in Appendix J — printed pp. 117–121. VERIFIED.** Quote: “‘Part N’ below and in table notes refers to notebook N”. The internal source map is excellent to maintain externally, but not main academic exposition. **Fix:** Appendix J becomes a public `REPRODUCIBILITY.md` supplement; in main text replace `Part 11 / R6` with a stable result ID and link.

12. **Page count exaggerates the presumed contribution — printed p. 12, §1.1 and main-to-appendix transition. VERIFIED.** Quote: “Our contribution is to connect them into a quantitative chain from memory resolution, through probing resources, to money.” This is a potentially defensible synthesis, but three large technical subprogrammes plus three empirical programmes demand a navigation layer and cannot be left to the reader. **Fix:** a one-page visual contract map and a short guide; trim side programmes. For faculty outreach send a separately authored 10–15-page synopsis.

13. **A warning in the manuscript deserves promotion — printed p. 62, §8. VERIFIED.** Quote: “Neither registered test finds that class data improve return forecasts.” That limits what a financial economist could infer. **Fix:** state this in the first page's abstract and in the conclusion's first paragraph without hedging.

14. **Coauthor and companion reference may be inconsistent — printed p. 33 and printed p. 61, citations. SUSPECT.** Quote: “the companion paper … (Niroula et al., 2026).” This paper's title lists two Niroula authors; the reader needs the complete *companion* author list and a stable citation if that work exists. **Fix:** verify authors of the companion individually, match the bibliography (which may still be a working paper) and avoid implying a third contributor or a finished result based only on “et al.”

15. **Front-matter future date — PDF p. 1. VERIFIED.** Quote: “November 2026.” The check occurs on 30 October 2026. A November-dated draft in October is not misconduct, but an unsolicited professor receiving it now may wonder whether the file was back/forward dated. **Fix:** use “October 30, 2026” or a real November release date after publication; never imply a release already occurred.

### MINOR
16. **Small grammatical leak — printed p. 6, §1.1. VERIFIED.** Quote: “and van Waarde et al. (2020) characterize”. **Fix:** “Van Waarde et al. (2020) characterize…” starting a new sentence.
17. **Internal numerics in prose — printed p. 22, §4.1. VERIFIED.** Quote: “The identity … is verified to machine precision for δ ∈ {0.02, 0.05, 0.10}”. **Fix:** “Direct substitution gives the identity; code checks it at the documented parameter points.”
18. **Dense run-source appendix — printed pp. 117–121. VERIFIED.** Quote: “Result identifiers such as X6 or U6 name the JSON file”. **Fix:** make these hyperlink targets in a release manifest and cut them from the PDF.

## Five-minute test: replacement abstract (under 200 words)
> Can market prices distinguish traders who react to past prices at different speeds? We study a linear market in which several groups update positions using exponential-memory signals and their combined orders affect prices. Under known price persistence and impact, observed price responses identify a merged distribution of trading weights and memory rates, but cannot distinguish groups with identical rates. Groups with nearby rates are identifiable in principle but difficult to estimate. We derive lower bounds on the experiments needed to distinguish them and, on specified parameter classes, matching estimators. We then translate one controlled experiment into executed quantity, trading capital and hypothetical trading losses. Class-tagged flow removes the singular estimation problem under an idealized observation contract. Public futures and crypto class-position data give narrower estimates of *position persistence* than the corresponding price-based fits, but do not identify the structural learning memories assumed by the model. Some predeclared structural diagnostics and return-forecast tests failed. The contribution is a conditional framework for comparing how much different observations reveal—not a cost-benefit estimate of existing audit trails or a general market equilibrium theory.

## Thirty-minute test: architecture
**One paper or several?** At least three. The defensible spine is merged-measure equivalence → sharp information barrier → costed observation contracts → limitations of the empirical proxies. The non-normal spectral-risk theorem and feedback-index measurement study pull away from that spine, and the finite-horizon decision Appendix I is a different result about aggregate learning without cohort identification. Keep those separately navigable and narrow the main claim.

## Professionalism and integrity checklist
| Item | Status in supplied PDF | Exact repair |
|---|---|---|
| Names/author affiliation/email | **PRESENT** (PDF p.1) | Obtain both authors' signed approval of exact affiliation/role |
| Date | **PRESENT, future-dated** (November 2026) | Replace with actual preprint/revision date |
| Keywords and JEL | **PRESENT** (PDF p.2) | No urgent fix |
| Acknowledgments | **MISSING** (no heading found) | Add truthful short acknowledgement, or “The authors thank no external reviewers”; only name Dr. Bhavsar with prior permission |
| Funding | **MISSING as explicit statement** | Add “The authors received no specific funding for this research” **only if true** |
| Conflict of interest | **PRESENT but partial** (printed p.63: “The authors declare no relevant financial interests.”) | Expand to complete competing-interest statement **only if true**; the user's preflight saying absent is too categorical |
| Data/code URL | **PRESENT; publicly resolves** (PDF p.2) | Pin repository to commit/release and add a minimal end-to-end reproduction |
| AI use | **PRESENT; adequacy conditional** (printed p.63) | Both authors verify coverage of actually used systems and tasks; AI-assisted internal review is not independent review |
| Companion-paper authors | **UNCERTAIN** | Check entire bibliography, cover, actual companion author list; update “Niroula et al.” appropriately |
| Self-citations | **PRESENT, some broad** | Cite only an actual accessible version; do not outsource unproved claims to it |
| “Registered” | **PROBLEMATIC unless qualified** (PDF p.3) | Use author's described narrower label, no external registration claim |
| “Verified” | **PROBLEMATIC when computation is substituted for proof** (PDF p.3 and Appendix J) | Say numerically recomputed; separate code checks and mathematical proof |
| Internal run identifiers | **PRESENT in Appendix J**, mostly removed from main text | Move Appendix J online; use release/manifests |

## Ten sentences most likely to irritate a faculty reader: quotation → exact rewrite
These are literal passages from the PDF (typesetting may split lines); issue is clarity/overclaim, not a claim that each sentence is false.

| # | Printed page / section | Original | Better replacement |
|---:|---|---|---|
| 1 |1, §1|“The question has become pressing as trading passes to learning algorithms and AI agents.”|“As algorithmic strategies become more common, it is useful to ask which strategy parameters public observations can recover.”|
| 2 |2, §1|“For an observer that learns by trading, the barrier is large in money.”|“At the illustrative parameters, the model gives a large trading-loss lower bound for a specified probing contract.”|
| 3 |3, §1|“Correctly tagged records remove the barrier.”|“Under the idealized per-cohort flow contract, tagging removes the near-collision divergence in estimation variance.”|
| 4 |3, §1|“Why would a supervisor pay for disclosure?”|“Disclosure matters for a supervisor only if the required decision depends on cohort-level attribution.”|
| 5 |3, §1|“In a simple decision model, an audit trail is worth its cost only for algorithms close enough that prices cannot attribute them within the supervisory cycle but separated enough that tagged records can.”|“In the specified fixed-cost delay model, disclosure is optimal over an intermediate range of separation values.”|
| 6 |3, §1|“Two further results complete the picture.”|“Two supplementary analyses address spectral risk and feedback measurement; neither is required for the principal identification theorem.”|
| 7 |12, §1.1|“Our contribution is to connect them into a quantitative chain from memory resolution, through probing resources, to money, with matching orders, explicit constants and a supervisory interpretation, and then to measure the relevant quantities in data.”|“We combine known mixture-conditioning methods with a closed-loop observation model and a specified financial probing account; empirical position data provide reduced-form illustrations.”|
| 8 |35, §5.4|“The order in ∆η does not depend on that choice.”|“The exponent is unchanged for bounded-energy designs under the specified Gaussian reset-experiment contract.”|
| 9 |40, §5.5|“The few-groups model of the previous results is therefore the optimistic case.”|“The fixed-K model admits polynomial rates under separation; the unrestricted completely monotone mixing class has only logarithmic accuracy in the stated W1 loss.”|
| 10 |59, §7|“This gives a quantitative argument for audit-trail regimes that record the participant class of each order, and a quantitative argument against relying on periodic statements for the same purpose.”|“In our attribution experiment, correctly tagged flow is much more informative than the particular periodic-statement observations considered here.”|

## D. Concrete 124 → ~115 PDF-page cut plan
1. Move **Appendix J (PDF pp. 120–124): save 5 pages**; provide a stable web replication manifest.
2. Move **Appendix B (PDF p. 83): save 1 page**; references use glossary link.
3. Move the **three densest pages of Appendix D optimization tables/derivation-independent calibration printouts** to the same supplement: **approximately 3 pages** without deleting theorem/proof logic.
**Total: 9 pages ⇒ approximately 115 PDF pages**, conditional on retypesetting. A better editorial cut would also move **Appendix H's feedback-index paper** out entirely and reinvest space in a comprehensible methods/evidence map. The latter might yield *fewer than* 115 pages, which is not a problem.

**What a later ~40-page journal version keeps:** 3-page introduction; 4-page model; 4-page identification; 8-page sharp statistical and financial contracts; 6-page tagged-measurement/decision analysis; 8-page disciplined evidence and failures; 2-page scope/conclusion; remaining pages for a concise proof roadmap, tables and references. Full proof appendix online.

## PhD/collaboration signal
**Positive, but at present mixed.** An undergraduate tackling difficult identification ideas, publishing code and openly reporting negative forecasts is worth a serious second look. The counter-signal is the very large volume of theorem statements, computations, jargon, and institution-wide conclusions without an independent proof sign-off: a professor may infer that the authors cannot distinguish a verified contribution from an ambitious research notebook. Three improvements would most change that inference: **(i)** a tight three-claim 10-page reading note; **(ii)** a documented, externally checked audit of the proofs and one clean-table replication; **(iii)** an explicit one-paragraph financial decision for which attribution rather than aggregate estimation matters, or a candid statement that this economic link remains open.

## E. Three questions to email the authors
1. Which **single original claim** would you defend without the empirical panels, and can you explain it in 200 words to a finance PhD student?
2. Which exact proofs and figures have been checked by someone who **did not write the AI-assisted code or initial derivation**, and what is that person's documented check?
3. Will you send me a 10-page version first, with the failed structural/forecast tests described as clearly as the positive results?

## F. Forward to a colleague?
**No, not the current 124-page version.** The one change that would most improve my answer is a 10–15-page, evidence-graded faculty synopsis attached to a restructured, reproducible full paper, with the mathematical proofs independently checked before distribution.
