# Input/output gate review — October 8, 2026

The current source's displayed-depth gate lacked a unit-consistent input map and incorrectly bounded a full latent-state norm by its price component. It also used leveraged notional as loss budget and did not carry exposure between windows. Its asserted operational guarantee is replaced by an explicit conditional finite-window quantity/output contract.

The replacement uses signed executed quantity, input operator H, monetary output C, carried initial state, execution-cost envelope, other-risk reserve and declared horizon. The sharp cap under the stated criterion is the minimum timewise remaining budget divided by the relevant maximum Markov coefficient plus execution cost. The formula separates an exceeded background, a zero input gain, and a finite quantity cap. It applies to total absolute quantity, not message counts.

Ten independent tests verify: linear-program worst-case envelopes, sharp cap, repeated-window reset failure, state-coordinate invariance, omitted-component failure of the price proxy, zero-gain/background cases, and physical quantity-unit conversions. These prove named computations and illustrate the formal proofs, not actual financial calibration or regulatory compliance.

The same pass rebuilt the recorded-series table from BTC, ETH and ADA inputs. Its prior SOL label, raw-return literals and narrow HAC-labelled intervals were inconsistent with the named output chain. The new54 cells match an independent reconstruction of weighted date means and Student-reference intervals from saved segment estimates. Cache hashes match result receipts; provider/licence and serial-inference gates remain separate.

## Regulatory source boundary

SEC staff guidance and the adopting release confirm that Rule15c3-5 includes pre-trade credit/capital and erroneous-order controls. Staff guidance is not itself the rule. The paper's model is a possible design input, not a compliance certificate:

- https://www.sec.gov/rules/final/2010/34-63241.pdf
- https://www.sec.gov/rules-regulations/staff-guidance/trading-markets-frequently-asked-questions/divisionsmarketregfaq-0

The EUR-Lex RTS6 text returned a verification page in this session. Search-index snippets locate Article15 controls, but a full current legal-text review was not completed. No new EU compliance conclusion is asserted.

## Open requirements

The reserve, financial output, execution input, fills, capital and state estimation, noise/model-error coverage and cost/margin updating must be authenticated. The maintained-model rejection remains relevant. A single-window cap cannot be restarted as though previous exposure vanished. All eight scientific acceptance criteria remain in `ACCEPTANCE_MATRIX_20261008.md`; the whole empirical/theorem ledger and specialist review remain unfinished.

A further exact cohort-splitting check compares models of different state dimensions with identical reset price responses. Their calibrated monetary input gains and finite caps agree. This clarifies that cohort ambiguity does not make every financial functional unknowable; unknown exposure/input maps, nonreset states and nonlinear marks remain distinct information requirements.

The positive one-asset cohort model now explicitly distinguishes protocols: a known monetary price-only output has total-quantity impulse peak |λ|κ, whereas its sustained-input gain is |λ|κ/(1−S). An exact impact example lowers all-state initial-shock magnification while increasing execution-input risk. Independent forward simulation and matrix inversion verify the protocol contrast. This resolves the named interpretation gap within that model, not actual financial calibration or novelty.
