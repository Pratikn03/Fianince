# Validation and remaining obligations

The final source was run in Linux/Python 3.12.14 with the exact pinned numerical
versions. All 27 targeted tests passed. The deep runner completed 288 generated
economies and 20,736 dependent policy/cost rows with seed 20261030. The entire
notebook's six code cells then completed in headless mode with seed 20261101,
including checksums, report display calls and the final ZIP/download fallback.
An actual Google Colab session was not used for this validation. Installation
was skipped because the exact numerical versions were already installed; the
verified pinned Lean compiler was reused. Notebook UI/Drive authentication and
browser download must still be exercised in Colab.

Lean 4.19.0 checked seven concrete arithmetic inequalities with no reported
axioms. It did not check the general market theorem, Gaussian analytic tail
argument, translation from arithmetic to economics, or literature priority.
The local host needed a recorded executable-path compatibility shim; this
did not modify Lean's proof kernel or generated proof source.

Checkpoint recovery was exercised with worker count changed from 4 to 2; all
288 saved statistics archives retained identical SHA256 hashes. A separate
quick run with deliberately invalid market metadata failed as intended and
still returned a valid ZIP containing its failure log. The unit-test quote
fixture is explicitly synthetic and does not count as real-market evidence.

The user's preceding returned cost-study ZIP was also verified: all 21 manifest
entries matched and the three core source files matched the published study.
That receipt is distinct from the two local advanced research runs.

The broad generated design did not support a claim that paid information always
improves the decision. The local deep run contains 7,622 negative-advantage rows;
these rows share readings and are not independent observations. Correlated
noise, mean bias, drift, low service premiums and high information fees matter.
See the scenario summaries and full return ZIP rather than pooling invalid
rules into a safe-performance claim. No actual quote data were supplied, so the
market stage is NOT_RUN. Zero Holm rejections among declared-valid checks is
an audit outcome, not a substitute for proof.

Next obligations: review the theorem with a specialist; test whether the
combined result is an immediate corollary of existing theory; use documented
event data held out from design; distinguish the observable response score
from the structural gain; improve the information-acquisition decision before
making general economic-value claims; obtain an independent implementation.
The existing manuscripts retain their status until these results are reviewed
and integrated with appropriate scope. No publication rating is established.
