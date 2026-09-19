# Hidden Slow Learners — execution plan

**Goal:** Establish and reproduce one focused candidate contribution: finite price-response windows can be identical in stable and unstable adaptive-feedback markets; test what additional information permits honest stability certificates.

**Architecture:** A small linear market with heterogeneous exponential learning states, an exact-rational matched-market constructor, a separate agent-loop simulator, rate-aware feedback bounds, baseline estimators, and deterministic experiment scripts. This is a synthetic mechanism study, not a limit-order-book model or trained AI experiment.

**Tools:** Python 3.11+, NumPy, SciPy, pytest; Matplotlib only for figures; pdfLaTeX for the paper; python-docx for the handoff report.

## Constraints
- Preserve the supplied framework; place all new work in this separate directory.
- No invented financial data, trained agents, empirical partners, author identity, external replication, or scientific priority.
- Label positive-systems, moment-problem, and system-identification ingredients as established mathematics.
- Exact statements have proofs and rational checks. Stochastic results report all configured cases, abstentions, and errors.
- Test-only and report-only code must not determine simulated ground truth.
- A rate floor is external information, not inferred from a short price record.

## Tasks
1. **Specification and tests.** Define the positive model, moment matching, response indexing, and bound contract in `docs/RESEARCH_PROTOCOL.md`. Write tests before implementation for matrix/agent agreement, exact moment equality, opposite stability labels, deconvolution indexing, valid feedback intervals, invalid assumptions, and baseline recovery.
2. **Implement the model and construction.** `src/machine_markets/model.py` evaluates the joint transition, impulse responses, kernels, and spectral radius. `construction.py` uses `fractions.Fraction` to build positive measures with identical truncated moments. Remove zero-weight states and split positive states to match agent counts.
3. **Implement measurement and comparisons.** `inference.py` computes lower/upper feedback bounds, three-way decisions, single-rate extrapolation, and a conventional rank-selected matrix-pencil comparator. Never treat a grid approximation or point estimate as a statistical certificate.
4. **Run deterministic experiments.** `scripts/run_experiments.py` saves exact witnesses, matched-pair CSVs, repeated-shock controls, noisy measurement sufficient statistics, per-case outputs, ablations, environment details, and summaries. Design settings live in `configs/main.json` and are fixed before the full run.
5. **Cross-check separately.** `scripts/verify_exact.py` must use only Python standard-library rational arithmetic and must not import the primary package. Verify exact identities and characteristic stability signs. A second simulation route and a clean-directory rerun check the numerical implementation, not external independent scientific replication.
6. **Write the research report.** A self-contained LaTeX paper contains theory, full proofs, actual results, closest-work audit, limitations, and reproduction instructions. `docs/Research_Findings_and_Next_Steps.docx` states what was achieved and what remains.
7. **Release checks.** Run tests, execute a clean reproduction, compare numerical outputs, compile and visually inspect the paper and Word document, write checksums, and zip the project without caches or build debris.

## Acceptance criteria
- The exact construction matches kernel moments through K-1 and price impulses through K+1, not forever.
- Both markets start with the same zero state and share the price coefficient; no claim of identical stationary distributions.
- All constructed pairs have strictly opposite signs of a + sum(q) - 1.
- Rate-aware bounds cover the true feedback on their specified simultaneous measurement event.
- Baselines are labeled by data access; inconclusive cases are not dropped from denominators.
- Negative controls deliberately violate the rate-floor or positivity assumption and are not included in the valid-model success rate.
- Final claims distinguish an original-to-this-project result from globally established priority.
