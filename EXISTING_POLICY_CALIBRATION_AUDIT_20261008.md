# Existing learned-policy and calibration audit

No new training was run. This examines the preserved `real_lob_rl_results.json` and its training/environment source.

The aggregate conclusion claiming R-squared at least0.99 for perturbation radii through0.25 is contradicted by its own outputs: the radius0.10 and0.25 values are approximately0.405 and0.544. At radius0.05, action spread is zero and the source substitutes1.0 for R-squared when the response is effectively constant. That value is not evidence of identified responsiveness.

The DQN audit fits a straight line to a discrete argmax policy over finite perturbation intervals. Such a fitted slope is not a verified Jacobian, and jumps at decision boundaries preclude inferring a uniform smooth response certificate. The actor-critic field is null in the saved result despite the full wrapper source describing both agents. This discrepancy requires actual run/checkpoint provenance.

The environment loads the first20,000 BTC feature rows, uses random episode starts and full-sample normalization, and contains no timestamp/segment checks in that loader. Its available-data branch does not read the January file, despite the result's two-dataset description. If BTC is absent, it silently generates a synthetic price path. The saved result therefore does not establish a two-market or untouched-holdout experiment.

Execution uses full trade quantity at midpoint plus half-spread plus a fixed linear impact coefficient. The loaded state has midpoint, spread and a normalized buys-minus-sells feature; it does not contain queue position, available depth, cancel/fill events or a ten-level OFI reconstruction. The cash/inventory update is an explicit hypothetical execution convention, not authenticated real queue fills. The constant impact coefficient and spread metadata require units and independent estimation.

No saved checkpoint/run-state chain was identified by the earlier bounded recovery sufficient to independently reproduce these policy-response outputs. The preserved aggregate JSON alone cannot regenerate trained weights or audit the stated certificate. New complex learning-agent experiments remain deferred by the user. Existing output contradictions and financial limitations are now explicit; this is a source/result audit, not completed policy replication or an operational safety result.

These conclusions supersede the broad production/calibration statements for this historical study. The current revised manuscript does not use it as empirical support for a learning Jacobian, market safety certificate or calibrated dealer performance.
