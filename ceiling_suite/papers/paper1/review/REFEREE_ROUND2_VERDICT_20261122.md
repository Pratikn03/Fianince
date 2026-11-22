# Second-round verdict on the revised JEDC version (22 November 2026)

**What this is.** This is a judgement of the revised 31-page main text and its 66-page Online Supplement. Each of the
two earlier referees is imagined reading the revision. It was written by the same AI system that made the revisions,
so it is **not** independent review.

## Verdicts

| | Referee A (statistics and theory) | Referee B (economics and policy) |
|---|---|---|
| First round | Reject | Reject |
| Second round, most likely | Major revision or reject, about even | Major revision, somewhat more likely than reject |
| Errors left in the mathematics | None found | None found |
| Main reason it could still fail | The contribution is thin: the rate is borrowed, the decision theory is elementary, and the paradox is a best response | Taiwan does not identify feedback, and the instrument classification is only begun |

**Editor.** Two reports split between major revision and reject usually lead to a reject at a journal with JEDC's
acceptance rate, unless one referee is clearly positive. The revision makes "major revision" a realistic outcome. It
does not make acceptance likely.

**Rough chance of eventual acceptance at JEDC:**
- this version, after the authors have checked the new results: about 15–25%;
- the first-round version: about 5%.

These numbers are judgement, not measurement.

## What changed the verdicts

1. **Both errors are corrected, and the corrections are checked numerically.**
   - The surveillance paradox now uses exponent 4 against a composite null, so the rate is N^(-1).
   - The near-instability result now uses a pair that the paper's observer cannot tell apart by persistence.
2. **The paper is now an article, not a programme.**
   - The main text is 31 pages and its economic results are proved in Appendix A.
   - It no longer cites working papers for anything it uses, apart from two side remarks.
3. **The overclaims are gone.**
   - The paradox is called a best response.
   - Minimax is "over labelings".
   - The audit trail's value is stated as an assumption.
   - The Taiwan cut is "given the grant".
   - The Lean claims say exactly what is checked.
4. **Proposition 7.1(iii) is new and answers Referee B's sharpest point.** A restriction by horizon needs no tags,
   and composition still decides whether it meets a ceiling, at the record length of Theorem 5.1.

## What a second-round referee would still write

1. **The contribution is incremental (A).** What is new is the equilibrium mapping (Theorems 4.1 and 4.4), the
   cheap-question characterization (Theorem 5.2), the relabeling game, the corrected paradox and Proposition
   7.1(iii). Each is modest, and A will say so.
2. **Taiwan (A and B).** Two of the three points are now answered. Both analyses were run under protocol P1M-A1, fixed before the runs.
   - **The targeted range.** It was recomputed on the theory's positive class, with memories up to 0.10 apart. Prices still leave foreign feedback anywhere from 0 to 0.0018, nearly all of the total, while the uniform cut stays in [0.0016, 0.0018].
   - **The tagged interval.** It survives a decoupled specification: 0.0013 [0.0011, 0.0015] against 0.0014.
   - **Not answered.** The registered test still does not establish feedback, and the signal is small.
3. **Instruments (B).** B asked for a classification of real instruments by incidence. The paper now has the
   framework and one sharp case, the horizon restriction, but not named instruments.
4. **Running markets (A).** The upper bounds still use the reset contract. There is no passive upper bound.
5. **The AI declaration.** The manuscript says that six results were added or corrected with AI assistance on 21–22
   November 2026 and have not yet been checked by the authors. An editor who reads that will likely return the
   paper. **Do not submit until the first author has read them and the declaration says so.** The six results are:
   - Proposition 7.1(iii);
   - Theorem 7.3(ii);
   - Lemma 7.7;
   - Theorem 7.9;
   - Supplement Proposition S4.5;
   - Supplement Proposition S11.1.

## What would raise the chance most, in order

1. **The first author checks the six results.** Then set `CORRECTIONS_CHECKED_BY_FIRST_AUTHOR = True` in
   `ceiling_suite/papers/paper1_jedc_short/make_short.py` and in
   `research_extension/paper1_publication_revision/t6/round9.py`, and rebuild.
2. **Make the CRediT statement true.** It must state what each co-author actually did. It currently says that
   Prashant Niroula and Sujan Khatiwada validated proofs, Lean files and calculations.
3. **Done on 22 November: the two Taiwan analyses** (sign-restricted weights; a decoupled specification). Both support
   the text.
4. **Done on 22 November: named instruments, Proposition 7.1(iv).** A turnover tax lowers the budget by κλk₀ and a
   minimum resting time with smooth incidence by κ Σ_{m<h} k_m; both are certified at the parametric rate without a
   memory bound, while a hard horizon cutoff is part (iii). The incidences are stated, not derived, and order-to-trade
   limits are not covered. It is a seventh result for the first author to check.
5. **Let the paper rest for a week before submitting.** Results dated the day before submission invite the
   comment that the paper has not stabilized.
