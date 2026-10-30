# What the additional confidence rules actually establish

Each reset supplies a response vector of length H. The risk policies use its
sum X_e. Storing the mean, standard deviation and block-median of these sums
preserves the sufficient statistics for the implemented policies. Gaussian
projection of a complete response vector has exactly the simulated scalar
distribution; this compression does not give the identification test fewer
tap observations. The separate identification audit uses the full-vector
Gaussian distance from the existing explicit hard pair.

For independent Gaussian resets of arbitrary within-vector covariance,
(mean(X)-G)/(sample_sd(X)/sqrt(N)) has Student's t law with N-1 degrees of
freedom. The projected upper interval is therefore valid without estimating
the whole H x H covariance matrix. This is the standard t interval, not a new
theorem or estimator. If a declared bound Var(X)<=v is available, the Gaussian
margin z*sqrt(v/N) is also valid. A false variance bound invalidates it.

For independent reset totals with mean G and Var(X)<=v, take odd
k>=8*log(1/gamma) disjoint blocks, m=floor(N/k) readings each. Chebyshev gives
P(|block_mean-G|>2*sqrt(v/m))<=1/4. If the median differs by more than that
radius, at least half the independent blocks are bad. Hoeffding's inequality
bounds this probability by exp(-k/8)<=gamma. Thus median+2*sqrt(v/m) is a
valid upper bound. If N<k, the implementation buys no certificate from this
argument and falls back to the declared prior gain bound, still charging
already purchased observations. It does not pretend an estimated variance
is a proved variance bound. The finite-variance t3 case is defined at the
reset-total level and is outside the original Gaussian tap contract.

The clipping and cost-aware position map are unchanged. These statistical
extensions do not address biased means, dependence BETWEEN resets, behaviour
change, signed response kernels, missing initial states or observational
identification from an exchange tape.

Primary references: Lugosi and Mendelson (2019), Mean Estimation and Regression
under Heavy-Tailed Distributions--a Survey, https://arxiv.org/abs/1906.04280;
Cont, Kukanov and Stoikov (2014), The Price Impact of Order Book Events,
https://arxiv.org/abs/1011.6402, for the optional event-level OFI definition.
