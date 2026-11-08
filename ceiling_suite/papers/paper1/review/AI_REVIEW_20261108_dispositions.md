# External AI-assisted referee report (8 November 2026): dispositions

The author pasted a referee-style report on the 134-page combined PDF and the proof packet. Its verdict was "fail in
current form" and an overall score of 5/10. It was produced by an AI system, so it does **not** count as independent
review.

Each finding was checked against the source before any change.

| # | Finding | Checked | Verdict | Fix |
|---|---|---|---|---|
| 1 | The blind-inversion steps in S3.3 and S25 transform `h` to `g_t = h_{t+1} − a h_t` and take zeros. The transform cancels the zeros at the rates. | Algebra redone: `Σ g_t z^{−t} = κ k̂(z) H(z)`. For one cohort this is `κ²wz²/((z−a)(z−r)−κwz)`, with no zero at `r`. The code (`breakthrough_experiments/exp2_unknown_mixture.py::blind_transfer_function_inversion`) realizes `H` itself (`h_0` direct term, `h_1, …` Markov parameters) and takes `H`'s zeros, which is correct. | **Confirmed.** A text error; the code was right. | Both passages rewritten to match the code. The text now warns that transforming the sequence cancels the zeros, and names the kernel-recursion alternative. |
| 2 | Theorem 6.1, its proof and packet Claim 8 used `T ≥ 2K` taps `h_0..h_{T−1}`, but the first differing tap is `h_{2K}`. | Confirmed. The error was introduced on 8 Nov when the analyticity sketch was replaced. | **Confirmed.** | The theorem now requires `T ≥ 2K+1`. The proof says that with `T ≤ 2K` the records coincide, and that the impossibility bound holds for every `T`. Theorem 6.2 now requires taps `h_0..h_{2K}`. Packet corrected. The Lean theorems use only the upper order and are unaffected. |
| 3 | "If the rates are known, weights need only order `σ²(Δη)^{−2}`" is false for general `K`. | Confirmed with the `(1,−2,1)` direction for `K = 3`: it preserves moments 0 and 1 and changes moment 2 by `2Δ²`. | **Confirmed.** | The `(Δη)^{−2}` claim is restricted to two weights. For general `K` the text gives a lower-order requirement of `(Δη)^{−2(K−1)}`, with the construction. |
| 4 | The converse in Theorem 4.5(ii) fails for a fixed signal rule (for example `S ≡ 0`). | Confirmed. The Lean statement (`Paper1EquilibriumInvariance.lean`) already quantifies over all signal sequences. | **Confirmed** (paper wording only). | The converse is now stated for every signal sequence, and the `S ≡ 0` caveat is in the statement and the proof. |
| 5 | The Table S26 note says "every entry is a lower bound", which contradicts the paragraph above it. | Confirmed. | **Confirmed.** | Note and caption now say the entries are hypothetical arithmetic, not lower bounds. The main text and Figure 1(c) already carried this qualification. Removing panel (c) is left to the author. |
| 6 | S8: "sequential probing can lower the expected loss by a factor of up to 0.49". | Confirmed. The 0.49 is a ratio of two lower-bound constants. Theorem S9.3's own text already said so. | **Confirmed.** | Rewritten as a ratio of lower bounds that shows no achieved saving. |
| 7 | Theorem S9.2(iii): the bracket `[61.41, 64.48]` is called exact, but its lower end is a grid minimum. | Confirmed. | **Confirmed.** | Labelled numerical. The text explains that a grid minimum can lie above the infimum and that the lower end is not certified. The summary table is marked the same way. |
| — | Packet Claim 1: Gauss–Radau gap nonzero for every `K`. | The reviewer's argument with `P(s) = (s+1)∏(s−s_j)²` was checked. | **Adopted** | Added to the paper's proof and to the packet, credited as suggested by an AI-assisted review. |
| — | The abstract's "also with a strategic insider" overstates Theorem 4.6. | Confirmed. | **Confirmed.** | Now "a strategic insider whose information is short-lived". |
| — | Packet: uniform stability margin and `T = ∞`; Claim 12 precise form. | — | **Adopted** | Questions and precise form added to the packet. |

## Not acted on (author decisions or new work)

- Narrowing the paper around the two-group supervisory result. This is a strategic choice.
- Removing Figure 1(c) and the conversion from the introduction.
- Comparing the information channels on the same estimand, and using verified class-flow data or an experimental market.
- Certifying the 61.41 lower endpoint by interval arithmetic.
- Rebuilding Lean independently. The reviewer did not do it; continuous integration is blocked by billing.

## Assessment of the score

The reviewer scored overall correctness at 4–5. Findings 1–7 are real and each is fixed. None touches the central
exponent, the matching upper bound, the passive bounds or the machine-checked statements.

The empirical criticism is not changed by these fixes and remains the main weakness: the class reports and the prices
estimate different objects.
