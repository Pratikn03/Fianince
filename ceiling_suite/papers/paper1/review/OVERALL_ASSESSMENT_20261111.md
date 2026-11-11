# Paper 1, Paper 2 and the thesis: what the work is worth and where the ceiling is (11 November 2026)

Written by an AI system (Claude) at the author's request. It is one reader's judgment, not independent review and
not a measurement. Scores use the 100-point scale of the outside review pasted on 10 November.

## 1. The three documents state one idea

**"Certify, don't identify."** A supervisor does not need to know who is trading to keep a market safe, and
finding out who is trading is expensive.

| Document | Its half of the idea | Strongest results |
|---|---|---|
| Paper 1 (core version) | The negative half. Prices reveal the trader groups only through one object, the kernel. Recovering the groups costs data of order (spacing)^-(4K-2). Targeted supervision needs the groups; class-tagged disclosure removes the cost | Sufficiency (Theorem 3.1); cost with a matching upper bound (Theorems 5.1, 5.2); disclosure value (Theorem 6.3); saturating traders (Section 7) |
| Paper 2 | The positive half. Transient loss depends on the traders through one number, the summed price response. That number is certified with about σ²ε⁻²·log(1/ε) experiments whatever the spacing, and a guard on it is the largest safe rule | Closed-form summed response; certification at the parametric rate; maximal guard; 15 of 25 registered tests pass |
| Thesis, chapter 4 | The general statement. Every question about hidden traders is a functional of the merged measure, and its cost is the value of a polynomial approximation problem. A question is cheap exactly when its kernel has square-summable power-series coefficients. Safety sits on the boundary and costs exactly one logarithm. The safety certificate cannot be gamed except by making the market safer | Theorems 4.4.1 to 4.4.3 (cost of any linear question), Theorem 4.16.1 (gaming), Proposition 5.2.1 (monoculture) |

## 2. What Paper 1 is worth on its own

- **Now: about 60.** After the audit fixes it has no known false claim, its main theorems are machine-checked, and
  its credit to earlier work is accurate.
- **Ceiling: about 70 to 72**, a solid field journal. Reaching it needs a human proof check, a much shorter paper
  and, if it comes out that way, a supportive stress-test result.
- **Why it stops there.** Each main result applies known mathematics to a market: aggregation and mixture theory
  (the kernel and the cost exponent) and a 1992 uniqueness theorem for neural networks (Section 7). The market
  setting is new; the mathematics is not. The data test proxies, not the tagged trades the theorems describe.

## 3. Where the higher ceiling is

The unified paper, built on thesis chapter 4, is the strongest thing this body of work supports:

- one question ("what can a supervisor learn from prices, and what does each question cost?");
- one classification theorem with an exact boundary;
- Paper 1's results as the expensive side and Paper 2's as the cheap side;
- the gaming result as the reason the cheap side is also the robust side.

**Estimate: high 70s, possibly low 80s, if the chapter-4 proofs survive a human check.** It is still not 90: the
thesis itself (section 4.17) says the cost classification applies the known theory of estimating functionals.

**This is the author's decision, and I did not act on it.** Merging changes which paper holds which result and who
its authors are (Paper 2 has five authors; chapter 4 is the candidate's own work). The standing instruction is to
keep Paper 2's cost-separation results out of Paper 1.

## 4. What a 90+ paper would need

One of these, none of which exists yet:
- a result the mixture and functional-estimation literatures do not contain;
- account-level or algorithm-level data that test the theorems directly;
- a new economic quantity in place of the imported exponents.

The idea I floated on 11 November (surveillance pushes traders to a common memory, which makes the market
fragile) does **not** survive the author's own theorems: in the thesis normalization the stability margin depends
only on total feedback weight, not on memories (thesis equation (4.2); Paper 2, Proposition IA.22.4(ii)). Hiding by changing memory
therefore leaves the long-run margin unchanged. What does hold is weaker and is now Proposition 6.4 of the core
paper.

## 5. What was added to Paper 1 on 11 November

| Item | Status |
|---|---|
| The targeted halt for every K. The outside review named this as one of two gaps | Proved on paper (Lemma S5.3, Proposition S5.4). The counting step is machine-checked; the rest is not. Checked numerically for K = 2 to 14. The comparison for the Gauss and Gauss-Radau pair itself is still open |
| Hiding caps targeting (Proposition 6.4) | Proved on paper; it is a short revealed-preference inequality resting on the sufficiency theorem. One group only; no equilibrium among groups |
| The IV argument (Proposition 6.2), the other gap the review named | Already proved on paper. It needs a human reader, not more text |
| Cutting to a ten-page note | Not done. It is the largest remaining step toward the ceiling and needs the author's go-ahead |

These additions do not change the ceiling. They close a stated gap and add one economic caveat. The main text is
now 37 pages, which works against the paper.

## 6. Recommended order

1. Decide between a short Paper 1 note and the unified paper as the main submission.
2. Get a mathematician to check the proofs of whichever is chosen.
3. Run the registered stress test once and report it as it comes out.
4. Treat a 90+ paper as a new project, started from a new question.
