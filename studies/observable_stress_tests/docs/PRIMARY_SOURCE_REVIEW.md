# Targeted primary-source review — 18 September 2026

This is a targeted review, not a complete priority search. The original framework's reference list is retained, and the following identification/measurement precedents are made explicit. Claims in the integrated paper are restricted to the versions consulted.

| Primary source | Relevance | What this project must not claim |
|---|---|---|
| Kosut, Lau & Boyd (1992), Set-Membership Identification, https://web.stanford.edu/~boyd/papers/set_member_id.html | Models consistent with noisy input-output observations | Feasible-model sets are newly invented here |
| van Waarde et al., Data informativity, https://arxiv.org/abs/1908.00468 | A property may be determined without unique parameter identification | Property-directed inference is new as a general principle |
| Khosravi & Smith (2021 preprint), internal positivity, https://arxiv.org/abs/2111.00407 | Positive-realization constraints in response identification | Positivity side information is original to our diagnostic |
| Khosravi & Smith (2021 preprint), gain information, https://arxiv.org/abs/2111.00409 | Steady-state gain constraints and RKHS methods | Any gain-informed estimator is new; a stable-class fit can certify unstable models |
| Csaji, Campi & Weyer (2015), SPS, https://arxiv.org/abs/1807.08216 | Exact finite-sample regions under independent symmetric-noise assumptions | Gaussian t/Bonferroni intervals are the only rigorous finite-data identification route |
| Jedra & Proutiere (2019), https://arxiv.org/abs/1903.10343 | Model-specific identification sample-complexity bounds | Two-point testing or sample-complexity limitations are new general theory |
| Cont, Kukanov & Stoikov (2014), https://arxiv.org/abs/1011.6402 | Short-horizon order-flow imbalance / price relation and depth | Our signed-volume dealer simulation is empirically calibrated or identical to their order-book imbalance |
| Rantzer (2015), https://doi.org/10.1016/j.ejcon.2015.04.004 | Standard positive-system stability tools | A renamed spectral radius is a new stability law |
| Bertsimas & Popescu (2005), https://doi.org/10.1137/S1052623401399903 | Optimization over measures/moment information | Positive moment optimization is a new general framework |
| Byrd, Hybinette & Balch (2019), https://arxiv.org/abs/1904.12066 | Richer exchange simulation infrastructure | ABIDES was executed or validated in this release |

The new computational result is the full chain from exogenous filled pulses and measured prices through estimated correlated uncertainty to a conditional positive-model interval, with transparent performance and invalid-assumption failures. That chain is not itself proof of novel priority. The fixed-order price-observation bound is a model-specific application of Gaussian testing. External expert review and stronger equally informed baselines remain necessary.

Metadata correction: the full-horizon companion's subtitle is retained from its actual TeX. Khosravi references identify verified 2021 preprints instead of silently combining uncertain publication versions. Jedra's first name is Yassir. SPS's article is 2015 although its author manuscript was deposited in 2018. Live SciPy documentation is distinct from the actually executed SciPy 1.17.0.
