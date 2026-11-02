"""
Generate the 20 Raw Questions and Answers files for Paper 1.
- Exactly 20 questions, each under 50 words.
- No "who to focus", no filling spaces or gap boxes.
- Strictly Paper 1 ONLY.
"""

from pathlib import Path
import docx
from docx import Document
from docx.shared import Inches, Pt, RGBColor
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.oxml import parse_xml
from docx.oxml.ns import nsdecls
import shutil

ROOT = Path("/Users/pratik_n/Downloads/Machine_Markets_Master_Release")

# 20 Raw Questions (Each under 50 words, strictly Paper 1 only)
QUESTIONS_20 = [
    {
        "num": 1,
        "section": "Section 2 & Appendices A–B",
        "q": "How does closed-loop price feedback G(z) = κ H(z) / (1 + κ q H(z)) convert open-loop trader memory rates η_k into transmission zeros of the return process, and why does ARMA estimation on price returns Δp_t identify only the closed-loop eigenvalues rather than individual trader parameters?"
    },
    {
        "num": 2,
        "section": "Section 2 (Theorem 2.1)",
        "q": "What does Theorem 2.1 (Merged Measure Invariance) establish regarding the observational equivalence of distinct trader populations, and why can two markets with different cohort counts and memory distributions produce mathematically identical noise-free price trajectories on 2K+1 periods?"
    },
    {
        "num": 3,
        "section": "Section 3.1 & Appendix B (Theorem 3.1)",
        "q": "How does Theorem 3.1 use Le Cam's two-point method and a (2K-1)-order moment-matching perturbation to prove the Ω(σ² (Δη)^{-(4K-2)}) minimax sample size lower bound for distinguishing K trader cohorts with minimum memory spacing Δη?"
    },
    {
        "num": 4,
        "section": "Section 3.1 (Near-Colliding Rates)",
        "q": "Why does the identification lower bound scale as (Δη)^{-6} for K = 2 cohorts and (Δη)^{-10} for K = 3 cohorts, and what happens to the required observation count when two algorithmic desks narrow their memory difference from 0.10 to 0.01?"
    },
    {
        "num": 5,
        "section": "Section 3.2 & Algorithm 1",
        "q": "How does the Hankel matrix H_K constructed from impulse response taps factor as V_K D_K V_K^T, and how does Algorithm 1 (Prony-Hankel deconvolution) extract the annihilating polynomial whose roots yield the latent memory rates η^_k?"
    },
    {
        "num": 6,
        "section": "Section 3.2 (Proposition 3.3)",
        "q": "How does Proposition 3.3 prove the singular value lower bound σ_{2K}(H_K) ≥ c_K (Δη)^{2K-1} via Chebyshev moment inversion on nodes {η_k}, and why does this show the Hankel operator condition number scales as (Δη)^{-(2K-1)}?"
    },
    {
        "num": 7,
        "section": "Section 3.2 & Appendix B (Theorem 3.2)",
        "q": "How does Theorem 3.2 prove that Prony's method achieves the matching minimax upper rate O(σ² (Δη)^{-(4K-2)}), and why do alternative subspace methods like ESPRIT and Matrix Pencil suffer from the exact same singular value decay?"
    },
    {
        "num": 8,
        "section": "Section 4 & Appendix B (Lemma 4.2)",
        "q": "Why is the Toeplitz cost matrix T_G in Lemma 4.2 strictly positive definite for any non-zero round-trip probe sequence u_t, and what does this 'No Sure Gain' property mean for an active supervisor attempting exploratory trading?"
    },
    {
        "num": 9,
        "section": "Section 4 & Appendix C (Theorem 4.3)",
        "q": "Why does maintaining mark-to-market margin solvency under adverse price excursions force the supervisor's cash capital reserve to scale as B = Ω(δ^{-4}) in Theorem 4.3, multiplying required capital by 16 when precision is doubled?"
    },
    {
        "num": 10,
        "section": "Section 4 (Table 4: Disclosure in Dollars)",
        "q": "In Table 4 ('Disclosure in Dollars'), why does weekly active probing to distinguish two algorithmic cohorts in 10-Year Treasury and E-mini S&P futures cost $15M to $356M annually per market, rendering active exploration legally and institutionally impossible?"
    },
    {
        "num": 11,
        "section": "Section 4.4 & Section 5.8 (Theorem 5.8)",
        "q": "How does Theorem 5.8 use Whittle spectral divergence on [-π, π] to prove that passive price observation experiences an asymptotic rate collapse of O((Δη)^{4K-2}), proving that waiting for natural trades costs time at the same rate probing costs capital?"
    },
    {
        "num": 12,
        "section": "Section 4.5 & Table 6",
        "q": "In Section 4.5 and Table 6, how does exact multinomial empirical resampling on real fat-tailed 1-minute Bitcoin return shocks confirm the theoretical log-log slope exponents of -6.01 (K = 2) and -9.81 (K = 3) without Gaussian approximations?"
    },
    {
        "num": 13,
        "section": "Section 5.7 & Appendix C (Theorem 5.7)",
        "q": "What is a completely monotone memory kernel under Bernstein's Theorem, and why does Theorem 5.7 prove that identifying a continuous memory distribution collapses minimax accuracy to logarithmic w = Θ(1 / log(N / σ²)), requiring exponential sample sizes exp(Θ(1/w))?"
    },
    {
        "num": 14,
        "section": "Section 5.1–5.3 (Theorem 5.1)",
        "q": "How does Theorem 5.1 prove that observing class-tagged order flows (e.g. MiFID II RTS 24 algo_id tags) uncouples the estimation problem into K independent regressions, collapsing sample complexity to Θ(σ² (Δη)^{-2}) for rates and O(1) for portfolio weights?"
    },
    {
        "num": 15,
        "section": "Section 5.5 (Proposition 5.5)",
        "q": "What is the supervisory cost-benefit trade-off formalised in Proposition 5.5 between reporting compliance costs and active probing losses, and why is mandatory class disclosure most economically valuable in an intermediate band of memory spacings [Δη_min, Δη_max]?"
    },
    {
        "num": 16,
        "section": "Section 5.4 & Table 8 (Registered Replication)",
        "q": "In Table 8, what did the out-of-sample replication pre-registered under SHA-256 hash 591e71c9... across 12 CFTC futures markets find, and why did public DCOT reporting narrow parameter uncertainty intervals by 23x to 69x compared to price data?"
    },
    {
        "num": 17,
        "section": "Remark 2.2 & Supplement S6",
        "q": "How does Remark 2.2 solve the stock-flow reconciliation problem connecting high-frequency flow demand u_t to weekly reported COT position stocks S_t, and why does dynamic stability uniquely select the smaller root of the quadratic characteristic equation?"
    },
    {
        "num": 18,
        "section": "Section 5.5–5.6 & Table 9 (Scorecard)",
        "q": "In Table 9, why did pre-registered hypotheses N2 and N3 fail on 30 Binance perpetuals under Diebold-Mariano tests, and how does Within-Class Sign Cancellation explain why combining CTAs and basis arbitrageurs into coarse reporting buckets destroys aggregate flow signals?"
    },
    {
        "num": 19,
        "section": "Section 6 & Appendix B (Theorem 6.1)",
        "q": "How does Theorem 6.1 construct two markets sharing identical closed-loop eigenvalues and stationary variance where non-normal matrix coupling produces unbounded transient amplification (||G^t||_2 → ∞), and why does the Kreiss constant K(A) expose flash crash risks missed by VaR?"
    },
    {
        "num": 20,
        "section": "Section 7, Proposition 5.6 & Appendix F",
        "q": "Why does Appendix F prove an unlevered warehousing desk needs only scalar cumulative gain G = ∑ h_t at rate O(N^{-1/2}) without identifying cohorts, while targeted supervisory halts (Proposition 5.6) strictly require individual cohort deconvolution at rate (Δη)^{-(4K-2)}?"
    }
]

# 20 Comprehensive Model Answers
ANSWERS_20 = [
    # Q1
    (
        "Open-loop trader demand is H(z) = ∑_{k=1}^K w_k / (1 - η_k z^{-1}) = N(z) / D(z), where D(z) = ∏_{k=1}^K (1 - η_k z^{-1}) has degree K "
        "and N(z) = ∑_{k=1}^K w_k ∏_{j ≠ k} (1 - η_j z^{-1}) has degree K - 1. When aggregated through Kyle's price impact κ > 0 and dealer inventory "
        "damping q > 0, equilibrium price formation closes the feedback loop: G(z) = κ H(z) / (1 + κ q H(z)) = κ N(z) / [D(z) + κ q N(z)]. "
        "The open-loop memory rates η_k are roots of D(z). However, in the closed-loop return transfer function G(z), the roots of N(z) enter as "
        "transmission zeros, while the observable poles of price returns Δp_t are the roots of the closed-loop characteristic polynomial "
        "D_{cl}(z) = D(z) + κ q N(z). Fitting an ARMA model to transaction price returns Δp_t identifies only the K roots of D_{cl}(z). "
        "Because the market has 2K + 1 structural parameters (K memory rates, K - 1 independent weights, κ, and q), the system of equations "
        "is under-determined by K + 1 dimensions: infinitely many combinations of (w, η, κ, q) yield the exact same closed-loop price poles."
    ),
    # Q2
    (
        "Theorem 2.1 establishes that two trader populations represented by Radon measures μ_0 and μ_1 on [0, 1) generate identical noise-free "
        "price paths under any exogenous input sequence if and only if their open-loop rational transfer functions coincide: H_{μ_0}(z) = H_{μ_1}(z). "
        "Because H(z) is a rational function with numerator degree K - 1 and denominator degree K, two distinct rational functions of degree at most K "
        "coincide identically if and only if their impulse response moments h_t = ∫_0^1 η^t dμ(η) agree on the first 2K + 1 periods (t = 0, 1, ..., 2K). "
        "Economically, this proves that an observer recording transaction prices cannot determine whether price dynamics are generated by a small "
        "group of slow, persistent institutional algorithmic desks or a larger population of fast high-frequency market makers whose aggregate "
        "impulse response matches the first 2K + 1 moments."
    ),
    # Q3
    (
        "Theorem 3.1 constructs two candidate Radon measures μ_0 and μ_1 supported on [0, 1) separated by minimum spacing Δη = min_{j ≠ k} |η_j - η_k|. "
        "The signed perturbation measure dΔ(η) = dμ_1(η) - dμ_0(η) is constructed using Chebyshev-type polynomial weighting such that its first "
        "2K - 1 algebraic moments vanish identically: ∫_0^1 η^m dΔ(η) = 0 for m = 0, 1, ..., 2K - 1. Consequently, the price impulse response "
        "difference Δh_t = ∫_0^1 η^t dΔ(η) satisfies Δh_t = 0 for all t < 2K, and |Δh_t| ≤ C_K (Δη)^{2K-1} for t ≥ 2K. "
        "Under N independent experiments with Gaussian noise variance σ², the Kullback-Leibler divergence is "
        "D_KL(P_0^{\\otimes N} || P_1^{\\otimes N}) = (N / 2σ²) ∑_{t=2K}^∞ (Δh_t)² ≤ (C_K N / 2σ²) (Δη)^{4K-2}. "
        "By Le Cam's two-point testing lemma and Pinsker's inequality, achieving testing error below α requires "
        "||P_0^{\\otimes N} - P_1^{\\otimes N}||_TV ≥ 1 - 2α > 0, which directly forces N ≥ Ω(σ² (Δη)^{-(4K-2)})."
    ),
    # Q4
    (
        "The lower bound exponent 4K - 2 arises directly from the squaring of the (2K-1)-order leading non-vanishing moment in the KL divergence: "
        "(2K - 1) × 2 = 4K - 2. For K = 2 cohorts, 4(2) - 2 = 6, producing an explosion rate of (Δη)^{-6}. For K = 3 cohorts, 4(3) - 2 = 10, "
        "producing (Δη)^{-10}. If two trading algorithms narrow their memory difference from Δη = 0.10 to Δη = 0.01 (a 10-fold reduction):\n"
        "- For K = 2: (0.10 / 0.01)^6 = 10^6. The required observation count increases by one million times (e.g. from 10,000 to 10 billion trades).\n"
        "- For K = 3: (0.10 / 0.01)^{10} = 10^{10}. The required observation count increases by ten billion times!\n"
        "This proves that even slight clustering in algorithmic execution horizons creates an insurmountable statistical barrier in market time."
    ),
    # Q5
    (
        "Estimated impulse response taps h^_t = (1/N) ∑_{j=1}^N Y_t^{(j)} are arranged into the (2K × 2K) Hankel matrix [H_K]_{i,j} = h^_{i+j-2}. "
        "Because each tap is a mixture of geometric modes h_t = ∑_{k=1}^K w_k η_k^t, the noise-free matrix factors as H_K = V_K D_K V_K^T, where "
        "V_K is the (2K × K) Vandermonde matrix with columns v_k = [1, η_k, ..., η_k^{2K-1}]^T and D_K = diag(w_1, ..., w_K). "
        "Algorithm 1 solves the linear system H_K c = -h_{2K} to determine the coefficients of the annihilating polynomial "
        "P(z) = z^K + c_{K-1} z^{K-1} + ... + c_0. By construction, the roots of P(z) are exactly the latent trader memory rates {η_k}. "
        "Once roots are found, the portfolio weights w^_k are recovered by solving the linear Vandermonde system V_K w = h^_0."
    ),
    # Q6
    (
        "Proposition 3.3 establishes that σ_{2K}(H_K) ≥ c_K (Δη)^{2K-1}. The proof establishes a dual Chebyshev moment inequality: for any unit vector "
        "u ∈ R^{2K} with ||u||_2 = 1, the associated polynomial P_u(η) = ∑_{j=0}^{2K-1} u_j η^j satisfies u^T H_K u = ∑_{k=1}^K w_k P_u(η_k)². "
        "By Markov-Chebyshev extremal polynomial theory on K nodes separated by Δη, the minimum sum of squared polynomial values on these nodes "
        "scales as min_{||u||=1} ∑_k w_k P_u(η_k)² ≥ c_K (Δη)^{2(2K-1)}. Taking the square root yields σ_{2K}(H_K) ≥ c_K (Δη)^{2K-1}. "
        "Because the largest singular value σ_1(H_K) is O(1), the condition number κ(H_K) = σ_1 / σ_{2K} scales as (Δη)^{-(2K-1)}, proving that "
        "Hankel inversion becomes severely ill-conditioned as memory rates cluster."
    ),
    # Q7
    (
        "Theorem 3.2 proves that when impulse taps are corrupted by Gaussian noise with variance σ²/N, the spectral perturbation satisfies "
        "||δH_K||_2 ≤ O(σ N^{-1/2}). Solving H_K c = -h_{2K} propagates this noise into the coefficient vector as "
        "||δc||_2 ≤ ||δH||_2 / σ_{2K}(H_K) ≤ O(σ N^{-1/2} (Δη)^{-(2K-1)}). Inverting the roots of P(z) introduces an additional condition factor "
        "proportional to the reciprocal of root separation (1 / Δη), yielding root error |η^_k - η_k| ≤ O(σ N^{-1/2} (Δη)^{-2K}). "
        "Squaring this error to achieve target precision δ yields N = O(σ² δ^{-2} (Δη)^{-(4K-2)}), matching Theorem 3.1. "
        "Subspace methods (ESPRIT, Matrix Pencil) rely on the identical Vandermonde column space whose oblique projector has condition number "
        "κ(V) ≍ (Δη)^{-(2K-1)}, meaning all linear spectral deconvolution methods hit the exact same fundamental performance ceiling."
    ),
    # Q8
    (
        "Under transient price impact kernel G(t) and Kyle's lambda κ, an active probing sequence u_1, ..., u_T generates cumulative cash execution "
        "cost Cost(u) = ∑_{t=1}^T u_t (p_t - p_0) = (1/2) u^T T_G u + ∑ u_t ε_t, where [T_G]_{i,j} = G(|i - j|). Lemma 4.2 proves that for any "
        "physically realizable decaying impact kernel G(t) ≥ 0, the Toeplitz matrix T_G is strictly positive definite: u^T T_G u > 0 for all u ≠ 0. "
        "This establishes the 'No Sure Gain' principle: exploratory trading against a limit order book cannot be self-financing. An active supervisor "
        "cannot design a round-trip probe sequence that extracts information without paying a positive expected financial execution loss."
    ),
    # Q9
    (
        "To achieve parameter precision δ, Theorem 4.1 establishes that total probe volume must satisfy ||u||_2² = Ω(σ² κ^{-2} δ^{-2} (Δη)^{-(4K-2)}). "
        "To avoid market manipulation detection, the optimal probe sequence oscillates, generating cumulative inventory excursions ||x||_∞ ≍ δ^{-1}. "
        "The peak adverse mark-to-market drawdown scales as sup_t |x_t Δp_t| ≍ κ ||x||_∞ ||u||_∞ ≍ κ δ^{-2} ||u||_2² ≍ Ω(σ² δ^{-4} (Δη)^{-(4K-2)}). "
        "By exchange margin rules, the supervisor must maintain cash capital reserves B to absorb this peak drawdown without defaulting. "
        "Thus, cash capital scales as B = Ω(δ^{-4}). Doubling precision requires halving δ, which multiplies required capital by (1/2)^{-4} = 16."
    ),
    # Q10
    (
        "Table 4 applies the Ω(δ^{-4}) financial bound to calibrated institutional parameters for US 10-Year Treasury futures (ZN, κ = $12.50 / lot, "
        "σ = 0.85%) and E-mini S&P 500 futures (ES). To identify two algorithmic cohorts separated by Δη = 0.05 on a weekly schedule, the annual "
        "deadweight execution loss is $15.4 million for Treasuries and $356.2 million for E-mini S&P. For a regulatory agency (CFTC, SEC) monitoring "
        "dozens of futures markets, active price probing would require hundreds of millions of dollars in continuous trading capital and billions "
        "in margin reserves, which is legally, politically, and operationally impossible for public regulatory bodies."
    ),
    # Q11
    (
        "For stationary Gaussian returns Δp_t, the Whittle log-likelihood has asymptotic KL divergence rate "
        "lim_{T→∞} (1/T) D_KL = (1/4π) ∫_{-π}^π [ f_0(λ) / f_1(λ) - 1 - log(f_0(λ) / f_1(λ)) ] dλ. Because candidate measures match moments up to "
        "order 2K - 1, the open-loop transfer functions differ by only |H_0(e^{iλ}) - H_1(e^{iλ})| = O((Δη)^{2K-1}) across all frequencies λ ∈ [-π, π]. "
        "Propagating this through the closed-loop feedback denominator proves that the relative spectral ratio satisfies f_0(λ) / f_1(λ) = 1 + O((Δη)^{2K-1}) "
        "uniformly. The divergence integral collapses to O((Δη)^{4K-2}), requiring passive sample length T = Ω((Δη)^{-(4K-2)}). "
        "Ambient order flow noise is white; it lacks persistent excitation at the revealing resonant frequencies, proving passive data suffers the exact same barrier."
    ),
    # Q12
    (
        "Section 4.5 replaces Gaussian errors with real 1-minute return shocks sampled directly from Bitcoin perpetual futures (October 2026 data), "
        "which exhibit extreme excess kurtosis (> 12.4), heavy Pareto tails, and volatility clustering. Using exact multinomial empirical resampling "
        "across sample sizes N without normal approximations, Table 6 records the separation sample size across memory gaps Δη ∈ [0.05, 0.30]. "
        "Log-log regressions of log(N) on log(1 / Δη) yield fitted empirical slopes of -6.01 for K = 2 (theoretical -6.00) and -9.81 for K = 3 "
        "(theoretical -10.00). This confirms that empirical heavy tails do not degrade or alter the identification barrier; the moment-matching "
        "cancellation mechanism is algebraic and holds invariant under any zero-mean noise distribution."
    ),
    # Q13
    (
        "By Bernstein's Theorem, a completely monotone memory kernel k(t) satisfies (-1)^n k^{(n)}(t) ≥ 0 and admits an integral representation "
        "k(t) = ∫_0^1 η^t dF(η) for a continuous probability measure F on [0, 1). This represents a continuum of trading horizons (K = ∞). "
        "Recovering F(η) requires inverting the continuous Hausdorff moment sequence, which acts as a compact, infinitely smoothing Fredholm integral "
        "operator with exponentially decaying singular values σ_m ≍ exp(-c m). Inverting this compact operator under noise is exponentially ill-posed: "
        "by Donoho's theorem, distinguishing two distributions with Wasserstein distance w requires N ≥ exp(C / w) observations. "
        "Inverting this yields minimax accuracy w* = Θ(1 / log(N / σ²)), proving continuous memory distributions cannot be deconvolved from price data."
    ),
    # Q14
    (
        "Theorem 5.1 proves that observing class-tagged order flows y_t = [y_{1,t}, ..., y_{K,t}]^T (e.g. MiFID II RTS 24 algo_id tags) allows the "
        "supervisor to observe each cohort's open-loop response directly. Because cohort states evolve independently as "
        "x_{k,t} = η_k x_{k,t-1} + (1 - η_k) p_{t-1}, tagged disclosure uncouples the coupled non-linear feedback loop into K independent single-variable "
        "autoregressions. The sample complexity to estimate η_k with error δ drops to N_k = Θ(σ² δ^{-2} (1 - η_k²)^{-1}), yielding N* = Θ(σ² (Δη)^{-2}) "
        "for spacing Δη (the exponent collapses from 4K - 2 to 2). For portfolio weights w_k, sample complexity is O(σ² δ^{-2}), which is O(1) "
        "completely independent of memory spacing Δη."
    ),
    # Q15
    (
        "Proposition 5.5 formalizes the supervisor's choice rule: mandate class disclosure if and only if the fixed regulatory compliance cost C_{rep} "
        "is less than the market probing deadweight loss C_{probe}(Δη) ≍ κ σ² (Δη)^{-(4K-2)}. This establishes an intermediate economic band [Δη_min, Δη_max]:\n"
        "- When Δη > Δη_max, algorithms are widely separated; price-based identification is cheap, and disclosure is unnecessary.\n"
        "- When Δη < Δη_min, algorithms are virtually identical; distinguishing them provides negligible regulatory benefit.\n"
        "- In the critical band Δη ∈ [Δη_min, Δη_max], algorithms are distinct enough to create differential systemic risk, but close enough to make "
        "price-based deconvolution prohibitively expensive. Here, mandatory regulatory disclosure is socially indispensable."
    ),
    # Q16
    (
        "Under SHA-256 pre-registration hash 591e71c9... (31 October 2026), Table 8 replicates parameter estimation across 12 CFTC futures markets "
        "(gold, silver, copper, corn, soybeans, wheat, live cattle, coffee, sugar, cotton, Nasdaq-100, British pound). Across all 12 markets, "
        "empirical uncertainty intervals for trader memory η_k and weights w_k derived from weekly Disaggregated Commitments of Traders (DCOT) reports "
        "are 23.4x to 68.7x narrower than under price-only econometric inversion. In wheat and corn, the ratio reaches 64x; in gold and copper, 58x. "
        "The Data Equivalence Multiplier reveals that a single weekly public CFTC report delivers information equivalent to 14,200 to 89,500 active probes, "
        "confirming that regulatory disclosure dramatically outperforms price filtering."
    ),
    # Q17
    (
        "Remark 2.2 and Supplement S6 derive the Two-Root Stock-Flow Inventory Bridge to reconcile high-frequency flow demand u_t with weekly "
        "reported COT position stocks S_t. Because position stock is the accumulated integral of past net order flows subject to inventory damping, "
        "it satisfies the recurrence S_t = (1 - δ_s) S_{t-1} + ∑ w_k y_{k,t} + ξ_t. Inverting this relation to recover underlying flow demand from weekly "
        "stocks requires solving a quadratic characteristic equation in the damping parameter. The equation has two real roots: the larger root produces "
        "explosive non-stationary dynamics (|λ| > 1), while dynamic stability uniquely selects the smaller root (|λ| < 1), establishing exact algebraic "
        "consistency between high-frequency microstructure and low-frequency regulatory reports."
    ),
    # Q18
    (
        "In Table 9, hypotheses N2 (5-min price forecast of position ratios) and N3 (aggregate taker flow pinning down combined response Ψ) failed "
        "Diebold-Mariano tests on 29 and 25 of 30 Binance perpetual contracts (October 2026 data, SHA-256 72cbc8ba...). This failure demonstrates "
        "**Within-Class Sign Cancellation**: public reporting buckets (e.g. 'Top Traders' or 'Managed Money') combine opposing algorithmic strategies, "
        "such as trend-following CTAs (momentum, w_CTA > 0, η_CTA ≈ 0.9) and cash-futures basis arbitrageurs (mean-reverting, w_Arb < 0, η_Arb ≈ 0.1). "
        "Because their orders move in opposite directions, their flows destructively interfere: w_CTA y_{CTA,t} + w_Arb y_{Arb,t} ≈ 0. "
        "This proves that coarse public buckets fail and granular MiFID II RTS 24 algo_id tags are essential."
    ),
    # Q19
    (
        "Theorem 6.1 constructs two state-space systems: A_1 = diag(λ_1, λ_2) (normal, orthogonal eigenvectors) and A_2 = [λ_1, γ; 0, λ_2] (non-normal, "
        "coupling γ > 0). Both systems share identical closed-loop eigenvalues 0 < λ_2 < λ_1 < 1, identical one-step return variance, and identical "
        "stationary covariance under white noise. However, because A_2's eigenvectors are non-orthogonal, its transient matrix powers scale as "
        "[A_2^t]_{1,2} = γ (λ_1^t - λ_2^t) / (λ_1 - λ_2), which grows arbitrarily large as γ increases. By the Kreiss Matrix Theorem, peak excursion "
        "is bounded by the Kreiss constant K(A) = sup_{|z|>1} (|z|-1) ||(zI - A)^{-1}||. Traditional VaR and volatility metrics measure only stationary "
        "covariance; they are blind to non-normal transient amplification, failing to detect flash crash vulnerability."
    ),
    # Q20
    (
        "Appendix F (Theorem F.3) analyzes an unlevered warehousing desk with carry costs b I + d I² under a hard stress budget B. The optimal inventory "
        "position I(C_N, F) depends solely on the scalar cumulative impulse response G = ∑_{t<H} h_t. Estimating G converges at the ordinary parametric "
        "rate O(N^{-1/2}), completely free of cohort spacing Δη, cohort count K, or memory floors. Thus, cohort deconvolution is unnecessary for aggregate "
        "inventory warehousing. In contrast, targeted supervisory halts (Proposition 5.6) require identifying which specific cohort k is rogue or over-leveraged "
        "to selectively halt its access while keeping market-makers open. This strictly requires estimating individual parameters (w_k, η_k), "
        "confronting the full (Δη)^{-(4K-2)} barrier and proving targeted interventions require mandatory algo_id tags."
    )
]

def build_questions_doc():
    doc = Document()
    
    # Margin settings
    for s in doc.sections:
        s.top_margin = Inches(1.0); s.bottom_margin = Inches(1.0)
        s.left_margin = Inches(1.0); s.right_margin = Inches(1.0)
        
        # Header & Footer
        header = s.header; hp = header.paragraphs[0]; hp.alignment = WD_ALIGN_PARAGRAPH.RIGHT
        hrun = hp.add_run("Paper 1: Reading & Discussion Questions (20 Questions)")
        hrun.font.name = "Calibri"; hrun.font.size = Pt(8.5); hrun.font.color.rgb = RGBColor(120, 120, 120)
        
        footer = s.footer; fp = footer.paragraphs[0]; fp.alignment = WD_ALIGN_PARAGRAPH.CENTER
        frun = fp.add_run("What Prices Cannot Tell a Market Supervisor — Development Revision: 2 November 2026")
        frun.font.name = "Calibri"; frun.font.size = Pt(8.5); frun.font.color.rgb = RGBColor(120, 120, 120)

    # Title
    p_pre = doc.add_paragraph()
    p_pre.paragraph_format.space_before = Pt(24); p_pre.paragraph_format.space_after = Pt(4)
    r_pre = p_pre.add_run("CO-AUTHOR READING & DISCUSSION QUESTIONS")
    r_pre.font.name = "Calibri"; r_pre.font.size = Pt(12); r_pre.font.bold = True; r_pre.font.color.rgb = RGBColor(0, 119, 182)

    p_title = doc.add_paragraph()
    p_title.paragraph_format.space_before = Pt(0); p_title.paragraph_format.space_after = Pt(8)
    r_title = p_title.add_run("What Prices Cannot Tell a Market Supervisor:\nThe Cost of Identifying Trader Groups and the Value of Class Disclosure")
    r_title.font.name = "Calibri"; r_title.font.size = Pt(18); r_title.font.bold = True; r_title.font.color.rgb = RGBColor(11, 37, 69)

    p_sub = doc.add_paragraph()
    p_sub.paragraph_format.space_before = Pt(0); p_sub.paragraph_format.space_after = Pt(16)
    r_sub = p_sub.add_run(
        "20 Core Questions on Paper 1 (Development Revision: 2 November 2026)\n"
        "Lead Author: Pratik Niroula | Co-Authors: Sujan Khatiwada and Prashant Niroula"
    )
    r_sub.font.name = "Calibri"; r_sub.font.size = Pt(10.5); r_sub.font.italic = True; r_sub.font.color.rgb = RGBColor(19, 64, 116)

    # 20 Raw Questions
    for item in QUESTIONS_20:
        p = doc.add_paragraph()
        p.paragraph_format.space_before = Pt(8); p.paragraph_format.space_after = Pt(4)
        p.paragraph_format.line_spacing = 1.15
        
        r_num = p.add_run(f"Question {item['num']} ")
        r_num.font.name = "Calibri"; r_num.font.size = Pt(11); r_num.font.bold = True; r_num.font.color.rgb = RGBColor(11, 37, 69)
        
        r_sec = p.add_run(f"[{item['section']}]:\n")
        r_sec.font.name = "Calibri"; r_sec.font.size = Pt(9.5); r_sec.font.italic = True; r_sec.font.color.rgb = RGBColor(100, 116, 139)
        
        r_q = p.add_run(item['q'])
        r_q.font.name = "Calibri"; r_q.font.size = Pt(10.5); r_q.font.color.rgb = RGBColor(29, 45, 68)

    out_path = ROOT / "Paper1_Questions_Workbook.docx"
    doc.save(str(out_path))
    print(f"Saved 20 Raw Questions to: {out_path}")
    return out_path

def build_answers_doc():
    doc = Document()
    
    # Margin settings
    for s in doc.sections:
        s.top_margin = Inches(1.0); s.bottom_margin = Inches(1.0)
        s.left_margin = Inches(1.0); s.right_margin = Inches(1.0)
        
        header = s.header; hp = header.paragraphs[0]; hp.alignment = WD_ALIGN_PARAGRAPH.RIGHT
        hrun = hp.add_run("Paper 1: Reference Answers (20 Questions)")
        hrun.font.name = "Calibri"; hrun.font.size = Pt(8.5); hrun.font.color.rgb = RGBColor(120, 120, 120)
        
        footer = s.footer; fp = footer.paragraphs[0]; fp.alignment = WD_ALIGN_PARAGRAPH.CENTER
        frun = fp.add_run("What Prices Cannot Tell a Market Supervisor — Development Revision: 2 November 2026")
        frun.font.name = "Calibri"; frun.font.size = Pt(8.5); frun.font.color.rgb = RGBColor(120, 120, 120)

    # Title
    p_pre = doc.add_paragraph()
    p_pre.paragraph_format.space_before = Pt(24); p_pre.paragraph_format.space_after = Pt(4)
    r_pre = p_pre.add_run("REFERENCE SOLUTIONS & MODEL ANSWERS")
    r_pre.font.name = "Calibri"; r_pre.font.size = Pt(12); r_pre.font.bold = True; r_pre.font.color.rgb = RGBColor(0, 119, 182)

    p_title = doc.add_paragraph()
    p_title.paragraph_format.space_before = Pt(0); p_title.paragraph_format.space_after = Pt(8)
    r_title = p_title.add_run("What Prices Cannot Tell a Market Supervisor:\nThe Cost of Identifying Trader Groups and the Value of Class Disclosure")
    r_title.font.name = "Calibri"; r_title.font.size = Pt(18); r_title.font.bold = True; r_title.font.color.rgb = RGBColor(11, 37, 69)

    p_sub = doc.add_paragraph()
    p_sub.paragraph_format.space_before = Pt(0); p_sub.paragraph_format.space_after = Pt(16)
    r_sub = p_sub.add_run(
        "Complete Reference Answers for all 20 Reading Questions (Development Revision: 2 November 2026)\n"
        "Lead Author: Pratik Niroula | Co-Authors: Sujan Khatiwada and Prashant Niroula"
    )
    r_sub.font.name = "Calibri"; r_sub.font.size = Pt(10.5); r_sub.font.italic = True; r_sub.font.color.rgb = RGBColor(19, 64, 116)

    # 20 Questions + Answers
    for idx, item in enumerate(QUESTIONS_20):
        ans_text = ANSWERS_20[idx]
        
        p_q = doc.add_paragraph()
        p_q.paragraph_format.space_before = Pt(12); p_q.paragraph_format.space_after = Pt(2)
        p_q.paragraph_format.keep_with_next = True
        
        r_num = p_q.add_run(f"Question {item['num']} ")
        r_num.font.name = "Calibri"; r_num.font.size = Pt(11); r_num.font.bold = True; r_num.font.color.rgb = RGBColor(11, 37, 69)
        
        r_sec = p_q.add_run(f"[{item['section']}]:\n")
        r_sec.font.name = "Calibri"; r_sec.font.size = Pt(9.5); r_sec.font.italic = True; r_sec.font.color.rgb = RGBColor(100, 116, 139)
        
        r_q = p_q.add_run(item['q'])
        r_q.font.name = "Calibri"; r_q.font.size = Pt(10); r_q.font.bold = True; r_q.font.color.rgb = RGBColor(19, 64, 116)
        
        p_a = doc.add_paragraph()
        p_a.paragraph_format.space_before = Pt(2); p_a.paragraph_format.space_after = Pt(8)
        p_a.paragraph_format.line_spacing = 1.15
        
        r_a_hdr = p_a.add_run("Model Answer: ")
        r_a_hdr.font.name = "Calibri"; r_a_hdr.font.size = Pt(10); r_a_hdr.font.bold = True; r_a_hdr.font.color.rgb = RGBColor(0, 119, 182)
        
        r_a = p_a.add_run(ans_text)
        r_a.font.name = "Calibri"; r_a.font.size = Pt(9.5); r_a.font.color.rgb = RGBColor(29, 45, 68)

    out_path = ROOT / "Paper1_Answers_Solution_Manual.docx"
    doc.save(str(out_path))
    print(f"Saved 20 Answers to: {out_path}")
    return out_path

if __name__ == "__main__":
    q_file = build_questions_doc()
    a_file = build_answers_doc()
    
    # Mirror files
    dest_dirs = [
        ROOT / "ceiling_suite" / "papers" / "paper1",
        ROOT / "ceiling_suite" / "paper1",
        Path("/Users/pratik_n/.gemini/antigravity/brain/074febfe-ec2d-4a96-a621-f727c283f483")
    ]
    for d in dest_dirs:
        if d.exists():
            shutil.copy2(q_file, d / q_file.name)
            shutil.copy2(a_file, d / a_file.name)
            print(f"Mirrored to: {d}")
