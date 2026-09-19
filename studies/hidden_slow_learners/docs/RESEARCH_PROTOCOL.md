# Research protocol — fixed before the main numerical run

Date: 18 September 2026. This is a time-stamped local protocol, not an externally registered preregistration. Analytic construction and small arithmetic exploration preceded it.

## Question
Can a finite observation horizon identify the sign of adaptive-market stability when heterogeneous learning rates and the number of hidden learning modes are not known?

## Model
x[t+1] = a*x[t] + sum(y[i,t]) + epsilon[t+1]
y[i,t+1] = (1-eta[i])*y[i,t] + eta[i]*q[i]*x[t]
with 0 <= a < 1, q[i] >= 0, and 0 < eta[i] <= 1. A y-state is the price-pressure contribution of one simple adaptive forecasting agent. It is not a trained LLM or RL policy. The model has no inventories, funding constraints, spreads, or endogenous depth.

The return kernel is k[j] = sum(q[i]*eta[i]*(1-eta[i])**j). Total feedback Q = sum(q[i]); the fixed linear system is Schur stable exactly when a+Q<1. Equality is the boundary. No universal market-crisis interpretation is attached to this condition.

## Exact construction
For K+1 distinct rational persistence nodes r_i in [0,1), use w_i = 1/product_{l!=i}(r_i-r_l). Positive and negative parts have identical moments j=0,...,K-1. Divide their masses by 1-r_i and use a common scale placing a+Q_minus below one and a+Q_plus above one. This matches price impulse coefficients h[0],...,h[K+1]. The next coefficient need not match.

The theorem concerns unrestricted hidden order at a fixed horizon. It does not contradict identification of a known finite-order observable/controllable linear system with sufficient data.

## Experiments
A. Matched pairs: K in {1,2,3,4,6,8,12}, a in {0.2,0.4,0.6,0.8}, slow-node persistence in {0.9,0.99,0.999,0.9999}. Other nodes lie evenly from 0 to 0.75. No unsuccessful case is excluded.
B. A readable exact witness: a=2/5 and persistence nodes {0,1/2,19/20}. Show equal early impulses, later divergence, frozen-learning control, and standard moment-estimator behavior.
C. Rate-aware recovery: 108 eight-state configurations combining a in {0.2,0.5,0.8}, valid eta floor in {0.002,0.02,0.1}, slow-feedback share in {0,0.3,0.7}, and Q/(1-a) in {0.6,0.9,1.1,1.4}. Measure kernels at horizons {4,16,64,256}; use 100 independent observation-noise repetitions and two noise levels. Confidence applies jointly across all four horizons.
D. Negative controls: an overoptimistic learning-rate floor, a signed-feedback case, and use of a short-window homogeneous approximation on the heterogeneous exact witness. These are failure demonstrations, not evidence that the valid theorem failed.

## Measurement contract
The noisy experiment observes controlled loop-open kernel measurements, not raw stock returns. In a shadow replay, apply a unit price input at time zero, hold later market inputs at zero, allow learning memories to decay, and record their aggregate price-pressure output. This requires trusted simulator/institution access and a fixed linear mapping from decisions to pressure. Ordinary market observations do not supply this automatically.

Each observed tap mean has independent Gaussian noise with standard error sigma/sqrt(N), N=128. Two relative per-replicate sigma levels are {0.002,0.02} times (1-a). We draw the distribution-equivalent sample means rather than pretend to execute N full market episodes. Save first 32 tap means plus the four partial sums and terminal taps: these are the exact numerical inputs used by all reported estimators. All noise can be regenerated from recorded seeds.

## Bounds and statistical contract
For H observed taps, S_H=sum_{j=0}^{H-1}k_j, r_max=1-eta_floor:
S_H <= Q <= min(S_H/(1-r_max**H), S_H + r_max/eta_floor*k[H-1]).
Known Gaussian errors give simultaneous Bonferroni intervals for the eight statistics (four sums and four terminal taps), with total alpha=0.05. Feed their lower/upper endpoints into the monotone bounds. A certificate is stable, unstable, inconclusive, or measurement/model conflict. Equality never receives a strict label. There is no Bayesian or frequentist interpretation outside this observation model and its valid rate floor.

## Baselines and outcomes
Compare finite-sum truncation, one-rate extrapolation, conventional rank-selected matrix-pencil reconstruction, no-rate-floor bounds, rate-aware bounds, and an oracle Q. Record decided fraction, unconditional incorrect-label rate, wrong-stable rate among truly unstable cases, wrong-unstable rate among truly stable cases, and error among decisions. Oracle has hidden-state access; point estimators are not certificates. Matrix-pencil and rate-aware methods receive the same valid rate floor and initial kernel data within their stated horizons.

Primary mathematical endpoint: exact indistinguishability with opposite stability. Primary stochastic endpoint: incorrect confident decisions and decision coverage of rate-aware bounds. The noisy baselines are descriptive comparisons, not a claim of universal algorithmic superiority. No p-value is needed for exact identities. Monte Carlo confidence intervals describe fixed-panel simulation proportions, not population effects in real financial markets.
