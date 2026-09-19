# Checklist for an outside researcher

This file describes work still needed externally. None of these outside-review steps is claimed completed by this release.

## First verification pass

1. Check `SHA256SUMS.txt` before changing files. Preserve an untouched copy.
2. Inspect the information contract: estimators may use the response prefix, known noise standard error, valid floor and known direct persistence for normalization. Reject any hidden use of true component rates, weights, count or labels.
3. Run the tests, exact verifier, confidence-event audit and clean reproduction command from README. Confirm that all 86,400 non-timing result rows agree. Different numerical environments may require diagnosis; do not merely increase tolerance to hide label changes.
4. Review all four wrong LP labels in `confidence_event_audit.json`, all conflicts and the paired decisions that were lost. Do not score only the selected successful cases.
5. Rebuild the numerical bounds using an independently chosen optimization implementation, not just another HiGHS algorithm. Validate continuum coverage rather than assuming a finite point grid is safe.

## Mathematical review

- Verify the positive-system threshold and the boundaries at zero weights and equality.
- Verify finite-window matching without interpreting equal repeated-state counts as fixed minimal order.
- Verify the continuum-bin outer inclusion and the Gaussian simultaneous-event bookkeeping.
- Distinguish unconditional family error, conditional error among decisions, interval coverage and decision coverage.
- Check the fixed-two-state Gaussian distance and coverage bound, including the fixed-noise infinite-horizon limit.
- Search for equivalent theorems or examples in the primary-source list and its references. Treat an equivalent predecessor as prior art, not a reason to rename the same construction.

## Out-of-sample research pass

- Generate independently chosen mixtures and noise seeds without tuning the tested procedure on their truth labels.
- Include near-boundary gains, broader state counts, tiny positive floors, and verified misspecification controls.
- Compare to a full continuous positive-moment or appropriate kernel-based confidence method with an equal information contract.
- Develop a feasible response-measurement protocol in an economically grounded simulator. Derive noise dependence instead of assuming the current iid tap model.
- Report the negative transfer cases for signed, switching and nonlinear dynamics. No confidence guarantee applies automatically outside the model.

## Decision for a submission

A positive decision requires an exact original application-level statement beyond existing informativity/moment/testing results, or convincing new measurement methodology with meaningful validation. A negative decision should narrow the work to a transparent benchmark, teaching example, or component of a larger study. Neither outcome justifies an unsupported global-paradigm claim.
