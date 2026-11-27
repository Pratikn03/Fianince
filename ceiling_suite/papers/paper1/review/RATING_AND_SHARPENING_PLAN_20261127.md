# Paper 1 (JEDC version): rating before, now, after, and the sharpening plan (27 November 2026)

Written by an AI system that also made many of the revisions, so this is not independent review. The scores are
judgement, not measurement.

## The scale

- **70:** a JEDC referee would likely reject; the core is sound but either thin or not yet convincing.
- **80:** a typical paper JEDC accepts after one or two rounds.
- **90:** a strong field-journal paper that a top-three finance journal would take seriously.

My scores of 20–21 November ("about 86" for the journal version) were on a looser scale than this one. On this scale,
that version is about 73. I am replacing those numbers, not adding to them.

## Three ratings

| Version | Pages (main + supplement) | Score | Rough chance at JEDC |
|---|---|---|---|
| 22 November (after the first referee round) | 31 + 66 | **74** | 15–20% |
| Today, 27 November | 35 + 83 | **77** | 20–25% |
| After the text-only edits below | about 30 + 65 | **81** | about 30% |
| + H1 supportive (no earlier than 10 December) | | 84–86 | 35–45% |

**Why it rose from 74 to 77:**
- Named instruments with derived incidence answer Referee B's sharpest request.
- The batch-auction and tick results tie the theory to real market design.
- Taiwan now has robustness checks (first differences, limit days excluded, regime split) and leading-order wording.
- The AI declaration is now true through 26 November, which removes the likely desk-return trigger.
- The Lean checks are cleaner: derivative links are proved and weak results are labelled.

**What holds it at 77:**
- **An unlabelled rerun as the headline number.** Main Figure 3A and the Taiwan text report the holdout as 0.0410
  (p = 0.0019). That is a post hoc rerun with limit days masked. The registered result is 0.0426 (block-60 p = 0.0024),
  which the supplement keeps.
- **Overclaims in the abstract and text:** "calibrated from prices alone", "reflects TWAP/VWAP slicing", and
  "durable targeting requires owner-linked audit trails".
- **Length.** The paper grew instead of tightening: 21 → 25 results in the main text and 66 → 83 supplement pages.
  Referee A's complaint was that the contribution is thin; more results make it look thinner, not deeper.
- **Taiwan stakes.** Feedback contributes 0.0017 to a budget of 0.97, so the illustration shows the gap in a market
  where the gap does not matter.
- **Unfixed rows and an unconfirmed statement.** Three Table S2 rows cite arithmetic lemmas for claims they don't
  prove, and the CRediT statement is unconfirmed.

## Weak claims and sharper versions

| # | Where | Now | Problem | Sharper |
|---|---|---|---|---|
| 1 | Abstract | "market-wide feedback cuts can be calibrated from prices alone" | False as stated. It needs persistence, impact and a memory bound; the Taiwan section's own third qualification says so | "market-wide feedback cuts can be calibrated from the aggregate price response once persistence and impact are known" |
| 2 | Abstract | "durable targeting requires owner-linked audit trails" | Proposition 7.10 proves tags lose value as γ → 0; owner links help only "whenever beneficial-ownership links prevent cross-account routing", which is close to assuming the answer | "when relabeling is cheap, class tags lose their value, and only records linked to beneficial owners preserve targeting" |
| 3 | Abstract and §1 | Five separate results | No single statement of the contribution | Lead with one **separation theorem**: a uniform cut needs order ε⁻² observations, a targeted cut needs Δ^-(4K-2), and verified tags make it free of the spacing. Everything else then supports it |
| 4 | §1, result 1 | "does not vanish as the market approaches instability (Figure 1)" | Cites a figure for a proved fact | Cite Proposition S4.5 (uniform in ε); keep the figure as illustration |
| 5 | §1, result 5 | "Against any standard local-power test" | Theorem 7.11 fixes one test, as §8 admits | "Against a fixed-level test whose power depends on the divergence J = cNδ⁴" |
| 6 | §1, Taiwan paragraph | "4.7 × 10⁵ times more information" | Leaves out the grant (known κ, persistence and non-feedback law) and the leading-order caveat | Add "given the grant, at leading order" |
| 7 | §7.4, Figure 3A | "pooled holdout (0.0410)", p = 0.0019 | A post hoc rerun presented as the registered result | Report 0.0426 [0.0206, 0.0643] as registered; show 0.0410 as "post hoc, limit days masked" |
| 8 | §7.4 | "unconstrained distributed lags reflect day-1 TWAP/VWAP parent-order slicing reversal" | A guess stated as fact | "are consistent with day-1 reversal from sliced parent orders" |
| 9 | §7.4 | "Foreign predictability is positive" | True, but it invites the causal reading the supplement disclaims | Put the supplement's sentence in the main text: "we do not claim that tagged flow responds to price deviations" |
| 10 | Table S2 | Micro, minimum-tick and endogenous-supervisor rows | Cite assumed or arithmetic lemmas for claims they don't prove | As in LEAN_AUDIT_20261127.md |
| 11 | Declarations | CRediT: co-authors validated proofs, Lean files and empirics | Unconfirmed | State what each person actually did |
| 12 | Supplement text | "1,306 named declarations" | Stale | 1,310 |

## Edits that raise the level, in order

1. **Integrity (items 7, 10, 11, 12).** These add nothing positive but prevent a downgrade, and they must be done
   before SSRN, because SSRN versions stay public.
2. **One headline theorem (item 3).** Combine Theorem 5.3/Corollary 5.4, Theorem 7.5 and Theorem 7.8 into a stated
   separation result in Section 1 and the abstract. This addresses "thin" by making the contribution legible. No new
   mathematics is needed.
3. **Cut the main text to about 30 pages and about 12 numbered results.** Move to the supplement:
   - the monitoring games (Proposition 7.12);
   - the batch-auction and tick results;
   - the detail of Proposition 7.2.

   Keep a single sentence for each in Section 7.
4. **Sharpen the claims (items 1, 2, 4, 5, 6, 8, 9).**
5. **Show what is at stake.** Use the Section 5 / S17 parameterization to state in one table what a mistargeted
   halt costs in pricing-error variance when feedback is large. This answers "so what?" with the paper's own model.
6. **Taiwan with your rerun.** Use the new file to replace or confirm Table 3 and Figure 3. Frame the section
   around the information ratio and the targeted range [0, 0.0018] against the uniform range [0.0016, 0.0018].
   Do not lead with predictability.
7. **Supplement from 83 to about 65 pages.** Drop restated results and keep the proofs.
8. **After 10 December: H1.** It is the only item that adds evidence rather than presentation. SSRN can be
   revised when it is in.

## SSRN before JEDC

- **Elsevier's preprint policy.** Elsevier's general sharing policy allows a pre-review preprint to be posted. I could
  not confirm JEDC's own wording; check the Guide for Authors at submission and disclose the SSRN posting in the cover
  letter.
- **What to post:** one PDF with the main text followed by the supplement, built after edits 1–4. Edits 5–7 are
  better done first but can come in an SSRN revision.
- **Co-author consent.** SSRN lists every author publicly, so Prashant and Sujan should agree to the posting and to
  the CRediT wording first.
