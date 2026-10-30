# Paper 1 — guide for the human reviewers

*What Prices Reveal About Hidden Trader Populations, and What Identifying Them Costs* (`paper1_ssrn.pdf`).

The AI review (an adversarial line-by-line audit plus a second, fresh-context review that saw only the PDF) has
been done and its findings applied; see `internal_adversarial_review.md`. That review is **not independent**: it
used the same model that helped write the paper. Two kinds of human review remain, and they have different jobs.

| Review | Who | Required before | What it certifies |
|---|---|---|---|
| Team review | Pratik, Prashant, Sujan | SSRN posting | The authors understand and stand behind every step |
| Outside specialist review | one statistician or system-identification researcher; one finance/microstructure reader | Journal submission | The central proofs are correct and the contribution is not an immediate consequence of known results |

## Part 1. Team review (before SSRN)

**Materials.** `paper1_ssrn.pdf`; `review/proof_review_packets.md` (results, dependencies, steps, questions,
record table); `review/edge_case_search.json`, `review/phase7_checks.json`, `review/prop_choice_check.json`
(computations that support, but do not replace, the proofs).

**Assignments** (first reader / second reader):

| Area | Results | First | Second |
|---|---|---|---|
| A. Model timing and merged equivalence | (1)–(6), Lemmas micro and cm, Theorem merged | Pratik | Prashant |
| B. Quantity, losses and capital | quantity, Toeplitz lemma, cap, capital, spectral, adaptive, Rayleigh–Hölder | Prashant | Sujan |
| C. Unknown-mixture bounds | CRB, two-cohort, K-cohort, Prony upper bound, uniform W₁, moment pairs, general memory | Sujan | Prashant |
| D. Passive identification and testing | minimum phase, passive cost, passive known pair | Prashant | Pratik |
| E. Tagged information and disclosure choice | tagged flow, value of disclosure, disclosure choice | Sujan | Pratik |
| F. Whole argument | abstract, introduction, conclusion against the theorems | all three | all three |

**How to review a proof.**
1. Read the statement and write down, in your own words, every assumption it makes.
2. Read the proof one sentence at a time. For each sentence, mark: *follows* (you can say why), *follows with a
   computation* (do it on paper or in Python), *unclear*, or *wrong*.
3. Check that every assumption the proof uses is in the statement, and every assumption in the statement is used.
4. Check the words "for every", "uniformly", "exact order", "matching", "if and only if": each must be earned.
5. Try one boundary case by hand (equal rates, a zero weight, a = 0, η near 1).
6. Record the result in the packet's table: area, step, reviewer, page, status, note.
7. The second reader repeats steps 1–6 without looking at the first reader's notes, then the two compare.

**Rules.** An *unclear* step is not passed. A *wrong* step goes to Pratik, who opens an issue; the AI drafts the
correction; both readers re-check it. A gap in a central result (Theorems merged, quantity, cap/capital,
K-cohort, Prony upper bound, passive cost, tagged flow, value of disclosure) must be repaired, not just flagged;
a gap in a supporting result can be narrowed, labelled or removed.

**Done when** every central step is *follows* for both readers, and the abstract, tables and conclusion say
nothing that the theorems do not.

**Then, before posting** (Pratik): settle the byline in writing; confirm which AI-use statement is accurate;
confirm the companion-paper author list; get the journal's answer on SSRN preprints (or use arXiv).

## Part 2. Outside specialist review (before the journal)

**Who.** (1) A statistician or applied mathematician who works on mixture estimation, super-resolution or
system identification, for areas C and D. (2) A finance or market-microstructure researcher for the economic
model, the observer framing and the empirical interpretation. Neither should be a co-author. A professor at MNSU,
or a researcher already in contact with the project, can suggest names; ask for a written note, not just a chat.

**What to send.** The PDF, a one-page cover note (below), and the list of specific questions. Not the whole
repository; offer it.

**Cover note (draft).**
> We would be grateful for a critical reading of a working paper on what market prices reveal about hidden
> trader groups. The results we most need checked are Theorems [K-cohort], [Prony upper bound], [general
> memory] and [passive cost]. We are particularly unsure whether [question 1–3 below]. Any error you find, or a
> reference showing a result is already known, would help us most. A short written note is enough.

**Questions for the statistics reviewer.**
1. Is the K-cohort lower bound (Gauss vs Gauss–Radau quadrature) correct, and is the response-level order
   ‖h^A − h^B‖ ≍ (Δη)^{2K−1} justified from both sides?
2. Are the constants in the Prony upper bound uniform over the stated compact class? Is the result more than an
   adaptation of Katz, Diab and Batenkov (2023) and Batenkov et al. (2021) to real nodes?
3. Is the 1/log N minimax rate for completely monotone kernels new, or a corollary of known deconvolution or
   moment-method results (Fan 1991; Kong and Valiant 2017; Wu and Yang 2020)?
4. Is the nonasymptotic passive lower bound (Toeplitz KL bound) correct, and is the mixture rate known for
   Whittle/spectral observation?
5. Is the uniform W₁ rate without separation a correct use of the Wu–Yang moment comparison?

**Questions for the finance reviewer.**
1. Is the observer (supervisor, exchange or desk) and its three options (wait, probe, disclose) a sensible
   economic framing? What would a referee in microstructure object to?
2. Are the dollar comparisons with the Consolidated Audit Trail fair as stated (lower bounds for a probing
   observer, weekly renewal)?
3. Is reading CFTC and Binance class positions as "fitted persistence, not learning memory" the right level of
   claim? Would a flow-based test on CFTC data be worth registering?

**Recording.** Each reviewer's note goes in `review/external/` with the date. Every point gets a response row
(point, change made or reason not, page) in `review/response_register.md`.

## Part 3. What not to ask reviewers to do
- Do not ask them to re-run the code; offer the repository instead.
- Do not present the AI review as independent review in the paper, the cover letter or to the professors.
- Do not list reviewers as authors, or authors as independent reviewers.
