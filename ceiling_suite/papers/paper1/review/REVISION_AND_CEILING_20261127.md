# Paper 1 (JEDC version): revision of 27 November 2026 and the honest ceiling

Written by an AI system that made the revision, so this is not independent review. The scores are judgement, not
measurement. The scale is the one defined in `RATING_AND_SHARPENING_PLAN_20261127.md`:
- 70: likely JEDC reject;
- 80: a typical JEDC accept;
- 90: a strong field-journal paper that a top-three finance journal would take seriously.

## What changed today (read these before the declaration covers them)

All changes are in `ceiling_suite/papers/paper1_jedc_short/sharpen_1127.py`, applied at the end of the build. No
registered test was rerun or redefined, and no data were read.

1. **Abstract** rewritten around the separation.
   - Removed: "calibrated from prices alone" and "durable targeting requires owner-linked audit trails".
   - Added: "once persistence and impact are known".
2. **New Theorem 7.1 (The supervisory separation)** heads Section 7.
   - (i) A uniform cut depends only on the budget S. S is estimated from kernel-tap records at a rate free of K and of
     memory spacing, and uniform scaling is minimax without tags.
   - (ii) Targeted halts, by size or by horizon, need N ≥ cσ²(Δη)^-(4K-2).
   - (iii) Verified tags make weight recovery free of spacing.
   - Proof (Appendix A): part (i)'s rate is a new, self-contained four-line argument (truncation tail plus Gaussian
     tail). The rest cites Proposition 7.2(i)–(iii), Theorem 7.5(i) and Theorem 7.8.
   - **This is the only new mathematics. Please check part (i)'s proof.**
3. **Introduction**
   - A "central result" paragraph now comes first.
   - Item 1 cites the near-instability proposition, not the figure.
   - Item 4 says that owner-linked records keep their value only if they make routing visible, and that this is
     assumed, not proved.
   - Item 5 states the class of tests: power at least of order √J.
   - The Taiwan paragraph states the grant and "at leading order".
4. **Uniform-cut paragraph (Section 7.2)** now names the measurement model it uses (direct kernel taps). It says, as
   Supplement Section S10 already did, that price-only impulse records need separate growing-depth bounds.
5. **Taiwan**
   - The holdout is reported as registered: D = 0.0426 [0.0206, 0.0643], block-60 p = 0.0024; 2022 = 0.0141,
     2023 = −0.0158; reverse-causality placebo −0.0065.
   - The limit-masked rerun (0.0410) and the March-2020 split are labelled "not registered".
   - "We do not claim that tagged flow in Taiwan responds causally to price deviations" is now in the main text.
   - "Reflect TWAP/VWAP slicing" becomes "consistent with (but not shown to be)".
6. **Figure 3A** now shows the registered rows first and the post hoc rows in a separate colour, each labelled. The
   registered numbers are read from `p1_empirics/results/p1t_holdout_registered_A4.json`, which
   `extract_p1t_registered.py` extracts from the printed output of the 8 November run.
7. **Moved to the supplement**, with their proofs; one sentence each stays in the main text:
   - the tick-grid theorem (now S24.1);
   - the post-halt corollary (S8.4);
   - the endogenous-supervisor proposition (S11.2).

   The main text now has 23 numbered results, down from 25.
8. **Table S2**
   - The micro row says the sign separation is a hypothesis.
   - The Kalman row cites the new derivative lemmas.
   - The supervisor row says the Nash argument is on paper.
   - The tick-grid row calls the zero-divergence lemmas arithmetic.
   - The passive-incidence row cites the proved exponential step.
   - The declaration count is now 1,310.
9. **Tests.** `test_jedc_audit_runner.py` is updated to the new layout; all 59 checks pass. The build is clean: no
   undefined references and no overfull boxes.

**Not changed, and needed from the authors before SSRN:**
- **The declaration still covers 21–26 November.** Once you have read the items above, change it to 21–27 November.
- **The CRediT statement** still says that Prashant and Sujan validated the proofs, Lean files and empirics. It must
  say what they actually did.
- **Co-author consent:** both co-authors should agree to an SSRN posting, which lists them publicly.

**Not done:**
- **Supplement trim.** The supplement is 86 pages, because it now holds the three moved results. Its first six
  sections restate the main text, but the main text cites into them, so cutting them needs a reference-by-reference
  pass.
- **Taiwan rerun.** This waits for your new file.

## Ratings

| Version | Score |
|---|---|
| Early October drafts | 60–65 |
| 22 November | 74 |
| This morning, 27 November | 77 |
| **After today's revision** | **79** |
| + Taiwan rerun, supplement trim, author confirmations | 80–81 (about the ceiling for editing alone, 82) |
| + H1 supportive (opens no earlier than 10 December) | 84–85 |
| + the two items below | 89–92, uncertain |

## Why editing alone stops near 82

Referees will judge three things, and editing has now done what it can for each:
- **Correctness.** No errors are known, and the overclaims are gone.
- **Clarity.** Theorem 7.1 now states the contribution.
- **Honesty about the evidence.** Taiwan is labelled as a calibration, and registered and post hoc numbers are
  separated.

What still holds the score down is substance, not presentation:
1. **Referee A's point stands.** The Δ^-(4K-2) rate is borrowed from mixtures and super-resolution, and the decision
   theory is elementary. Theorem 7.1 makes the paper's own contribution clear, but it is a combination of existing
   results.
2. **No evidence tests the separation itself.** Taiwan shows that the information gap is large where the stakes are
   small: feedback is 0.0017 of a 0.97 budget. Nothing yet shows that a targeted rule chosen from prices goes wrong
   in a real market.

## What a 90+ version needs

Two additions, neither of which editing can supply.

**A. A causal test of the separation (about +4 to +5 if supportive).**
- **The event.** Find an exogenous, documented restriction on one trader class. Candidate events were searched on
  21–22 November (task "Draft specification and simulation for the chosen event" is still open).
- **The registered prediction.** Before reading the data, register that the restriction's effect on aggregate
  persistence is predicted by the class's tagged contribution, and not by any price-only estimate. Then run it once.
- **What a supportive result shows.** The separation would then be tested, not just calibrated. It would also answer
  Referee B.

**B. One theorem a referee would call new (about +2 to +3).** Either of these would do:
- **A passive upper bound in a running market.** Match Δ^-(4K-2) from one stationary record, without the reset
  contract. This is Referee A's open item 4, and it is the most natural statistical extension.
- **An equilibrium of disclosure design.** The supervisor chooses tags and tests while traders choose memories and
  accounts, and the welfare-optimal audit trail is characterized. This would turn Proposition 7.10 and Theorem 7.11
  into one result.

**Chances.** Doing A or B well is a matter of months, not days. My judgement of the chance of 90+ within that time is
about 10–15%. It is not zero, because A is a single clean test once an event is found. A supportive H1 alone reaches
about 85, not 90.

## Recommended order

1. **Authors:** read the changes above. Then confirm CRediT and the co-authors' consent, and extend the declaration
   to 27 November.
2. **Post the 79–81 version on SSRN now.** That gives a dated public version. SSRN versions can be replaced.
3. **Run H1 when it opens** (10 December or later), then revise SSRN.
4. **Choose between A and B** as the next project. A gains more if a clean event exists.
