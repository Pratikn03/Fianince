# Adversarial check of the derived instrument result

These are two simulated referee perspectives from one AI system. They are not independent peer review.

## Referee A — Statistics

| Claim examined | Disposition |
|---|---|
| Real analyticity gives parametric estimation | Rejected. The proof establishes the required Taylor coefficient bound on the unit disk for the quadratic charge. For scheduled revisions the same argument controls the analytic remainder. |
| An estimated incidence can be inserted into a tap estimator | Conditional pass. Real-interval consistency alone does not control the variance across tap coefficients. The proof adds a polynomial fit with bounded coefficient norm and conditions on an independent reference record. The rate uses known common preference inputs, bounded positive spectrum, geometric covariance decay, and increasing tap depth. |
| A small proportional tax is always parametric | Rejected. Even when no desk exits, the white-noise example has a pole at memory one. Over the full measure class the pole violates the coefficient criterion. |
| Crossing an exit or cap threshold creates a fixed gap | Rejected. Continuous clipping gives a kink. A rescaled quadrature pair has a first-order budget gap proportional to the spread. Match the affine part and place only the Radau endpoint on the constrained side. The same pair distinguishes the binary exit or binding decision. |
| The likelihood lower bound covers all accessible observations | Conditional pass. The reset bound is for the declared Gaussian contract and a common reference law. The result does not include observed post-policy holdings or a general joint market experiment. |

## Referee B — Economics

| Claim examined | Disposition |
|---|---|
| Traders can maximize true expected returns in a mean-reverting market | Rejected as a maintained premise. The objective uses perceived conditional returns and actual second moments from a reference series. Belief and risk parameters are common known inputs for the incidence claim. |
| A scheduled revision is a literal exchange minimum resting time | Rejected. The result is about positions or feedback targets held between revision dates. It supplies the response to a constant signal. Queue position, order cancellation, and execution are absent. Longer schedules can increase the response when reduced adjustment costs dominate. |
| An order-to-trade cap acts like a turnover cap | Rejected in this model. The theorem covers a per-desk constraint on expected turnover. A message-to-trade ratio requires an order model. |
| Dealer feedback is composition-free | Narrowed. The first-order primitive dealer coefficients on the stable zero-feedback branch depend on total feedback intensity. The effective feedback budget also depends on a second memory functional. At a nonzero baseline the derivative generally involves the transform evaluated at equilibrium. |
| Optimized memory preserves the parametric rate | Conditional only. A stable interior optimum and a known sensitivity function in the coefficient class are needed. With fixed desk mass, direct memory changes at fixed scale cancel from the primitive budget. |

The illustrative Taiwan calculation uses committed coefficients and a hypothetical white-noise reference. It is separate from P1M and P1M-A1. No empirical test is rerun.

The verification commands are:
- Python unit tests targeting only the six new synthetic test methods in test_instrument_incidence.py.
- Python instrument_incidence.py to reproduce instrument_incidence_diagnostics.json.
- Lean 4.34.1 on CurrentProofs/Paper1InstrumentIncidence.lean. This checks the five rational identities specified there.
- The canonical supplement build followed by the short JEDC build.
