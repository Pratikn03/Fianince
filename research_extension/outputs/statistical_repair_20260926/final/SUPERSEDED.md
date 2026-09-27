# Superseded before completion

The grid, both sweeps, and the first clean-copy grid were stopped after review
found that the covariance-distance diagnostic could raise outside the fitter's
exception handler. This failure-path issue is now tested with an injected
singular covariance; it is not evidence of a failure among ordinary Wishart
draws. Existing partial panel files and protocols remain unchanged.

The accepted run destination is `../verified/`. The design, seeds and settings
remain unchanged. No results from this incomplete directory enter the paper.
