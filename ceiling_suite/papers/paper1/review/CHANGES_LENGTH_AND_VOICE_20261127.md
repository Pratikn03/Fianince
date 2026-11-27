# Length and voice pass, 27 November 2026 (after the authors' verification at 15:35 CST)

Written by the AI assistant at the first author's request. **No result, proof, number or assumption was changed.**
What changed is where the material sits and how the introduction and conclusion read. All three authors should
re-read sections 1 and 2 below before the paper is posted, because the AI declaration says the authors verified the
prose.

Code: `ceiling_suite/papers/paper1_jedc_short/final_cut_1127.py`, applied last in the build.
Result: main text 37 → 29 pages; supplement 87 → 89 pages. The supplement received the moved proofs, which was
offset by the cuts in section 5.

## 1. Introduction (main text, pp. 1–3): rewritten. Please read it in full

- **Shorter and plainer:** about 1,450 words become about 1,050.
- **New layout:** the two-algorithm example, then the model, the main result, the limits of tags, the supporting
  results, what is new, and the empirical illustration.
- **Nothing left out:** every result and number from the old version is still there. The five-item list is gone; its
  content is in the paragraphs.
- **Moved results:** these are now cited as Supplement results:
  - the instrument proposition (Supplement Proposition S22.1);
  - the partial-tags theorem (Supplement Theorem S9.2).

## 2. Conclusion (Section 8): rewritten. Please read it in full

- The three policy conclusions now cover pilots, Theorem 7.3.
- The limits paragraph has the same content in fewer words. The detailed stakes inequality for the
  endogenous-supervisor result is now only in Supplement Proposition S11.2.
- The last sentence now says that Theorem 7.3 states the prediction a causal test would check.

## 3. Moved from the main text to the supplement (unchanged text)

- **Results:** each leaves a one-sentence summary in the main text.
  - Proposition "Partial-equilibrium incidence of price and quantity instruments", with its lead-in paragraph, is now
    at the start of Supplement S22.
  - Corollary "Guarantee of a single halt" and Theorem "Minimax value of partial tags" are now at the start of
    Supplement S9.
- **Proofs:** Main Appendix A keeps the proofs of Theorems 3.1, 3.2, 5.2, 7.1 and 7.3. All other main-text proofs
  are at the start of Supplement S7. The main-text proof of Theorem 6.1 was dropped as a duplicate, because Supplement
  S18 already proves it, and the main text now points there.
- **Pointers:** every main-text pointer to a moved proof now says "Supplement Section S7", or S18 for Theorem 6.1.
  In the moved proofs, references to main-text equations read "main-text (4)" and so on.

## 4. Numbering (main text)

| Result | Old | New |
|---|---|---|
| Instrument proposition | 7.4 | S22.1 |
| Expected loss | 7.5 | 7.4 |
| Minimax | 7.6 | 7.5 |
| Guarantee of a single halt | 7.7 | S9.1 |
| Partial tags | 7.8 | S9.2 |
| Tags | 7.9 | 7.6 |
| Microfoundation | 7.10 | 7.7 |
| Relabeling | 7.11 | 7.8 |
| Surveillance paradox | 7.12 | 7.9 |
| More data does not substitute for records | 7.13 | 7.10 |

## 5. Supplement cuts

- **Notation table removed.** It was three pages, and nothing cited it.
- **Lean mapping table moved.** "Machine-checked declarations" (S21) keeps its opening paragraph: the receipt, the
  axiom audit and the counts. The five-page result-to-declaration table moved to the replication archive as
  `ceiling_suite/papers/paper1_jedc_short/lean_mapping_table.tex`. Table S2, which covers the results added in this
  revision, stays.

## 6. Checks

- The build is clean, with no undefined references and no overfull lines.
- All 59 audit checks pass. Three checks were updated to look for moved proofs in the supplement.
