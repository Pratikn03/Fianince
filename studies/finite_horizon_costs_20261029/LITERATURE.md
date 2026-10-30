# Closest research and the limit of the novelty claim

Primary sources checked on 29 October 2026 (client date). This is a targeted
comparison, not an exhaustive priority search or independent specialist review.
No claim that nobody has established an equivalent result is justified yet.

| Source | Already established | Candidate distinction requiring review |
| --- | --- | --- |
| van Waarde, Eising, Trentelman, Camlibel (2020), Data Informativity, IEEE TAC 65:4753-4768, https://www.math.rug.nl/~trentelman/psfiles/Data-driven.pdf | Compatible systems can support some analysis/control tasks without unique identification; other tasks require it. | Our finite-horizon statistical guarantee and explicit inventory-service profit/capital accounting instantiate, rather than originate, this distinction. |
| Wagenmaker, Simchowitz, Jamieson (2021), Task-Optimal Exploration, ICML, https://proceedings.mlr.press/v139/wagenmaker21a/wagenmaker21a.pdf | Task-dependent lower bounds, exploration and decision performance; task-guided exploration can outperform uniform identification. | Their main smooth decision setup assumes local differentiability of loss and optimizer. Our clipped hard-budget decision has regime boundaries and a singular latent-cohort inverse problem. This observation does not prove non-overlap with their general theory. |
| Donoho (1994), Statistical Estimation and Optimal Recovery, Annals of Statistics 22:238-270, https://web.stanford.edu/dept/statistics/cgi-bin/donoho/wp-content/uploads/2018/08/SEOR.pdf | Gaussian linear-functional estimation, affine minimax risk and modulus-of-continuity methods. | Our tap-sum estimator is ordinary Gaussian projection. There is NO new-estimator claim and the projection baseline is exactly equal. |
| Heinrich and Kahn (2018), Strong Identifiability and Optimal Minimax Rates for Finite Mixture Estimation, Annals of Statistics 46:2844-2870, https://imstat.org/publications/aos/aos_46_6a/aos_46_6a.pdf | Slow mixture recovery near coalescing components; nonuniform pointwise and local minimax rates differ. | Our explicit two-cohort Gaussian-response pair is calculated directly. Its moment-matching mechanism is classical and related to Paper 1; its novelty is not asserted. |
| Tu, Boczar, Recht (2018), Minimax Lower Bounds for H-infinity-Norm Estimation, https://arxiv.org/abs/1809.10855 | FIR norm estimation need not be easier than FIR model identification under their query model. | We compare finite positive-response functionals with LATENT cohort weights, not with the FIR response vector. These are different inverse problems, not contradictory findings. |
| Blackwell (1953), Equivalent Comparisons of Experiments, Annals of Mathematical Statistics 24:265-272, doi:10.1214/aoms/1177729032 | Classical comparison of experiments and decision-relative information. Primary publication reference cross-checked through the Blackwell collected-works bibliography: https://celebratio.org/Blackwell_DH/article/255/ | Positive value after a fee is not automatic. Our result supplies an explicit sufficient dollar inequality for one financial contract, not a new general value-of-information theorem. |

The candidate contribution is the combined finite-horizon result: no adaptation-
rate floor for the direct finite-horizon certificate; an explicit net financial
value bound with information fees consuming the same stress budget; a priced
separation from a two-cohort weight-recovery task; and the tradeoff between
measurement error and paid information. The cube-root upper tradeoff follows
by elementary optimization. It is not asserted minimax optimal or unique.

Before a priority claim, review constrained statistical decision theory,
cost-sensitive experimental design, partial identification, and financial
inventory/risk-budgeting results with a specialist. In particular ask whether
the combined theorem is merely a straightforward financial corollary. The
existing draft already contains a broader claimed certification/identification
separation; this appendix makes a smaller financial result explicit and checked,
rather than treating the earlier broad claim as independently verified.
