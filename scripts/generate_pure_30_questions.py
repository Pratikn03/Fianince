"""
Generate PURE 30 Questions and Answers files:
- Only the 30 questions, numbered 1 to 30.
- NO 'where to read', NO 'key objects', NO 'how to give answer'.
- NO author names (no Sujan, no Prashant).
- NO empty boxes, NO fill-in gaps.
- Strictly Paper 1 only.
"""

from pathlib import Path
import docx
from docx import Document
from docx.shared import Inches, Pt, RGBColor
from docx.enum.text import WD_ALIGN_PARAGRAPH
import shutil

ROOT = Path("/Users/pratik_n/Downloads/Machine_Markets_Master_Release")

# Pure 30 Questions
QUESTIONS_30_PURE = [
    (
        1,
        "How does closed-loop price feedback G(z) = κ H(z) / (1 + κ q H(z)) convert open-loop trader memory rates η_k into "
        "transmission zeros of the return process, and why does ARMA estimation on price returns Δp_t identify only closed-loop "
        "eigenvalues rather than individual trader parameters (w_k, η_k, κ, q)?"
    ),
    (
        2,
        "What are the degrees of the open-loop numerator N(z), denominator D(z), and closed-loop characteristic polynomial D_{cl}(z), "
        "and why do the roots of D_{cl}(z) strictly interlace with open-loop memory rates {η_k} on [0, 1)?"
    ),
    (
        3,
        "Why does matching the observable roots of the closed-loop characteristic polynomial D_{cl}(z) from price time-series "
        "yield an unidentifiable (K+1)-dimensional manifold of observationally equivalent market configurations?"
    ),
    (
        4,
        "Under what exact mathematical conditions does Theorem 2.1 (Merged Measure Invariance) establish that two distinct trader "
        "populations produce identical noise-free equilibrium price paths over 2K+1 periods?"
    ),
    (
        5,
        "How does the Two-Root Stock-Flow Inventory Bridge formally connect high-frequency trader flow demand u_t to weekly reported "
        "COT position stocks S_t, and why does dynamic stability uniquely select the smaller root of the quadratic characteristic equation?"
    ),
    (
        6,
        "Why does estimating baseline market parameters (a, κ, p*) at the standard parametric rate O_p(T^{-1/2}) preserve the condition "
        "number and asymptotic deconvolution rate of Prony's algorithm without rate degradation?"
    ),
    (
        7,
        "How does the Le Cam two-point construction in Theorem 3.1 use a (2K-1)-order moment-matched Chebyshev perturbation measure "
        "dΔ(η) to force the leading 2K-1 impulse response difference taps to vanish identically?"
    ),
    (
        8,
        "Why does the Taylor series expansion of the Kullback-Leibler divergence between two moment-matched Gaussian price processes "
        "collapse to order O(N σ^{-2} (Δη)^{4K-2})?"
    ),
    (
        9,
        "How does Pinsker's inequality combine with Le Cam's two-point lemma to establish the minimax sample size lower bound "
        "N* = Ω(σ² (Δη)^{-(4K-2)}) for any arbitrary testing error level α ∈ (0, 1/2)?"
    ),
    (
        10,
        "Why does the identification sample complexity lower bound scale as (Δη)^{-6} for K = 2 cohorts and (Δη)^{-10} for K = 3 cohorts, "
        "and what happens to the required observation count when memory spacing narrows tenfold?"
    ),
    (
        11,
        "How does Algorithm 1 (Prony-Hankel Deconvolution) extract the annihilating polynomial from the (2K × 2K) Hankel matrix H_K "
        "to recover latent memory rates η^_k and portfolio weights w^_k?"
    ),
    (
        12,
        "How does Proposition 3.3 prove the singular value lower bound σ_{2K}(H_K) ≥ c_K (Δη)^{2K-1} via Chebyshev extremal polynomials, "
        "and why does this establish that the Hankel condition number scales as (Δη)^{-(2K-1)}?"
    ),
    (
        13,
        "How does Theorem 3.2 prove that Gaussian tap noise propagates through polynomial root inversion to achieve the matching minimax "
        "upper rate O(σ² (Δη)^{-(4K-2)})?"
    ),
    (
        14,
        "Why do alternative subspace deconvolution methods (ESPRIT and Matrix Pencil) suffer from the exact same condition number decay "
        "κ(V_K) ≍ (Δη)^{-(2K-1)} as Prony's method?"
    ),
    (
        15,
        "Why is the Toeplitz execution cost matrix T_G associated with transient price impact strictly positive definite for any non-zero "
        "round-trip order sequence, and what does this 'No Sure Gain' property mean for active market probing?"
    ),
    (
        16,
        "How does the Fisher information matrix of an active probing sequence establish the cumulative order energy lower bound "
        "||u||_2² = Ω(σ² κ^{-2} δ^{-2} (Δη)^{-(4K-2)})?"
    ),
    (
        17,
        "Why does maintaining mark-to-market margin solvency under peak adverse inventory excursions force an active supervisor's cash "
        "capital reserves to scale as B = Ω(δ^{-4})?"
    ),
    (
        18,
        "In the institutional calibration of Treasury and S&P futures, why does weekly active probing to distinguish two algorithmic cohorts "
        "impose annual execution losses of $15M to $356M per market?"
    ),
    (
        19,
        "How does Theorem 5.8 use Whittle spectral divergence on [-π, π] to prove that passive price observation experiences an asymptotic "
        "information rate collapse of O((Δη)^{4K-2})?"
    ),
    (
        20,
        "Why does exact multinomial empirical resampling on real fat-tailed 1-minute Bitcoin return shocks confirm the theoretical slope "
        "exponents of -6.01 (K = 2) and -9.81 (K = 3) without Gaussian approximations?"
    ),
    (
        21,
        "What is a completely monotone memory kernel under Bernstein's Theorem, and why does Theorem 5.7 prove that identifying a continuous "
        "memory distribution collapses minimax accuracy to logarithmic w = Θ(1 / log(N / σ²))?"
    ),
    (
        22,
        "How does Theorem 5.1 prove that observing class-tagged order flows uncouples the estimation problem into K independent regressions, "
        "collapsing sample complexity to Θ(σ² (Δη)^{-2}) for rates and O(1) for weights?"
    ),
    (
        23,
        "What is the supervisory cost-benefit trade-off formalised in Proposition 5.5 between reporting compliance costs and active probing losses, "
        "and why is mandatory disclosure socially optimal only within a critical intermediate band of memory spacings?"
    ),
    (
        24,
        "How do weekly Disaggregated Commitments of Traders (DCOT) position reports narrow parameter uncertainty intervals compared to price "
        "inversion across major futures markets?"
    ),
    (
        25,
        "In the pre-registered 12-market CFTC replication (SHA-256 591e71c9...), why did public regulatory disclosure narrow parameter uncertainty "
        "intervals by 23x to 69x, and what is the institutional significance of the Data Equivalence Multiplier?"
    ),
    (
        26,
        "In the 22-test empirical scorecard, what were the exact criteria for the 11 passing tests and 10 failed tests, and why does pre-registering "
        "negative results protect research against publication bias?"
    ),
    (
        27,
        "How does Within-Class Sign Cancellation explain why combining trend-following CTAs and cash-futures basis arbitrageurs into coarse public "
        "reporting buckets causes aggregate order flow signals to cancel toward zero?"
    ),
    (
        28,
        "How does Theorem 6.1 construct two state-space markets sharing identical closed-loop eigenvalues and stationary variance where non-normal "
        "matrix coupling produces unbounded peak transient gain (||G^t||_2 → ∞)?"
    ),
    (
        29,
        "How does the Kreiss Matrix Theorem K(A) ≤ sup_t ||A^t||_2 ≤ e · n · K(A) govern transient price amplification, and why do traditional "
        "Value-at-Risk models fail to detect impending flash crashes?"
    ),
    (
        30,
        "Why does an unlevered warehousing desk with a stress budget require only the scalar cumulative gain G = ∑ h_t at rate O(N^{-1/2}), while "
        "targeted supervisory halts strictly require individual cohort deconvolution at rate (Δη)^{-(4K-2)}?"
    )
]

# Pure 30 Answers
ANSWERS_30_PURE = [
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
    (
        "In Lemma 2.1 and Lemma 2.2, D(z) has degree K with roots at {η_1, ..., η_K}, and N(z) has degree K - 1. Because weights w_k > 0 sum to 1, "
        "N(z) is a convex combination of degree K - 1 polynomials. By the Gauss-Lucas theorem and Markov interlacing properties, "
        "the K - 1 roots of N(z), denoted {z_1, ..., z_{K-1}}, strictly interlace with {η_k} on the real interval (0, 1): "
        "η_1 < z_1 < η_2 < z_2 < ... < z_{K-1} < η_K. In the return transfer function G(z) = κ N(z) / D_{cl}(z), the roots of N(z) are transmission zeros. "
        "The observable poles of price returns are the roots of D_{cl}(z) = D(z) + κ q N(z). Because κ q > 0 and N(z) interlaces with D(z), "
        "the roots of D_{cl}(z), denoted {λ_1, ..., λ_K}, also strictly interlace with {η_k} on [0, 1). This interlacing guarantees that all closed-loop "
        "poles remain real and strictly inside the unit circle |λ_i| < 1, ensuring asymptotic stability while completely masking the open-loop poles {η_k}."
    ),
    (
        "An econometrician observing transaction price changes Δp_t fits an ARMA(K, K-1) model. The estimated autoregressive polynomial "
        "recovers the K roots {λ_1, ..., λ_K} of the closed-loop denominator D_{cl}(z) = D(z) + κ q N(z). This provides exactly K scalar equations: "
        "e_m(λ_1, ..., λ_K) = e_m(roots(D + κ q N)) for m = 1, ..., K, where e_m is the m-th elementary symmetric polynomial. "
        "However, the underlying market model contains 2K + 1 structural parameters: K memory persistence rates {η_1, ..., η_K}, K - 1 independent "
        "portfolio weights {w_1, ..., w_{K-1}}, Kyle's lambda impact κ, and dealer inventory damping q. Because 2K + 1 > K for all K ≥ 1, "
        "the mapping from observable closed-loop return poles to open-loop trader parameters is severely under-determined. The fibers of this mapping "
        "form a smooth, connected (K+1)-dimensional manifold of parameter configurations (w, η, κ, q) that produce mathematically identical return processes."
    ),
    (
        "Let μ_0 and μ_1 be two Radon probability measures on [0, 1) representing two trader populations. Noise-free price paths coincide under all "
        "exogenous input sequences if and only if their closed-loop transfer functions coincide: G_{μ_0}(z) = G_{μ_1}(z). Since G(z) is a strictly "
        "monotonic fractional linear transformation G = κ H / (1 + κ q H), G_{μ_0} = G_{μ_1} if and only if H_{μ_0}(z) = H_{μ_1}(z) identically in z. "
        "Each H_μ(z) is a rational function with numerator degree at most K - 1 and denominator degree at most K, so H_{μ_0}(z) - H_{μ_1}(z) = "
        "P(z) / (D_0(z) D_1(z)) where P(z) is a polynomial of degree at most 2K - 1. A rational function of degree 2K vanishes identically if and only "
        "if its first 2K + 1 Markov impulse response moments h_t = ∫_0^1 η^t dμ(η) agree for t = 0, 1, ..., 2K. "
        "Thus, two economies produce identical price paths if and only if their first 2K + 1 moments match, proving that prices cannot distinguish "
        "between 2 slow institutional trend-followers and 5 high-frequency market-makers."
    ),
    (
        "High-frequency market microstructure models operate on order flow demand u_t, whereas regulatory disclosures (CFTC DCOT reports) publish "
        "weekly position stocks S_t. Stock S_t is the cumulative sum of past flows damped by inventory depreciation: S_t = (1 - δ_s) S_{t-1} + u_t^W + ξ_t, "
        "where u_t^W is weekly aggregated flow and δ_s ∈ (0, 1) is weekly position decay. Substituting the state expectation dynamics into stock "
        "accumulation yields a second-order linear recurrence in position stock: S_{t+1} - (1 + a_s - κ_s) S_t + a_s S_{t-1} = ε_t^S. Inverting this "
        "relation to recover trader flow parameters requires finding the roots of the characteristic polynomial P(λ) = λ² - (1 + a_s - κ_s) λ + a_s = 0. "
        "The discriminant is strictly positive, yielding two real roots: λ_{1,2} = [(1 + a_s - κ_s) ± √((1 + a_s - κ_s)² - 4 a_s)] / 2. Dynamic stability "
        "strictly requires |λ| < 1. The larger root violates stability (λ_1 > 1, producing explosive non-stationary inventories), uniquely selecting "
        "the smaller root λ_2 < 1 and establishing algebraic consistency."
    ),
    (
        "In practice, baseline parameters θ_0 = (a, κ, p*) are estimated from high-frequency price data yielding θ^_T = θ_0 + O_p(T^{-1/2}). "
        "Corollary 2.3 proves that the deconvolution of trader memory parameters {η_k} is asymptotically stable under this plug-in estimation. "
        "Let H^_K(θ^_T) be the Hankel matrix formed using estimated baseline parameters. The perturbation satisfies "
        "||H^_K(θ^_T) - H_K(θ_0)||_2 ≤ C_θ ||θ^_T - θ_0||_2 + O_p(σ N^{-1/2}) = O_p(T^{-1/2}) + O_p(σ N^{-1/2}). Because baseline parameters converge "
        "at the fast parametric rate T^{-1/2}, their estimation error is dominated by the ill-conditioned Hankel singular value decay "
        "σ_{2K}(H_K) ≍ (Δη)^{2K-1}. Consequently, plug-in estimation preserves the exact minimax deconvolution rate O(σ² (Δη)^{-(4K-2)}) without rate penalty."
    ),
    (
        "Let the base trader population μ_0 have K cohorts with memory rates η_1 < ... < η_K separated by minimum spacing Δη. "
        "We construct the perturbed economy μ_1 by setting dμ_1(η) = dμ_0(η) + dΔ(η), where dΔ(η) is a signed Radon measure supported on "
        "[η_1 - Δη/2, η_K + Δη/2]. By the theory of Chebyshev moment spaces on compact intervals, there exists a non-zero signed measure Δ "
        "whose first 2K - 1 algebraic moments vanish identically: ∫_0^1 η^m dΔ(η) = 0 for all m = 0, 1, ..., 2K - 1, while its (2K)-th moment is non-zero: "
        "∫_0^1 η^{2K} dΔ(η) = c_K (Δη)^{2K}. The price impulse response difference between the two economies is Δh_t = ∫_0^1 η^t dΔ(η). "
        "Because Δ matches moments up to order 2K - 1, Δh_t = 0 identically for all lags t = 0, 1, ..., 2K - 1. The first diverging lag is t = 2K, "
        "where |Δh_{2K}| = c_K (Δη)^{2K-1}."
    ),
    (
        "Under N independent reset experiments with Gaussian observation noise of variance σ², the log-likelihood ratio between product measures "
        "P_0^{\\otimes N} and P_1^{\\otimes N} yields the Kullback-Leibler divergence: D_KL(P_0^{\\otimes N} || P_1^{\\otimes N}) = (N / 2σ²) ∑_{t=0}^∞ (Δh_t)². "
        "Because Δh_t = 0 for all t < 2K and |Δh_t| ≤ C_K (Δη)^{2K-1} for t ≥ 2K, the entire summation vanishes up to lag 2K - 1: "
        "∑_{t=0}^∞ (Δh_t)² = ∑_{t=2K}^∞ (Δh_t)² ≤ C_K (Δη)^{2(2K-1)} = C_K (Δη)^{4K-2}. Substituting this into the KL divergence yields "
        "D_KL(P_0^{\\otimes N} || P_1^{\\otimes N}) ≤ (C_K N / 2σ²) (Δη)^{4K-2}. By Pinsker's inequality, the total variation distance satisfies "
        "||P_0^{\\otimes N} - P_1^{\\otimes N}||_TV ≤ √( (1/2) D_KL ) ≤ √(C_K N / 4σ²) (Δη)^{2K-1}."
    ),
    (
        "By Le Cam's two-point testing lemma, the minimax risk of testing between P_0 and P_1 with test level α ∈ (0, 1/2) satisfies "
        "inf_ψ max(P_0(ψ ≠ 0), P_1(ψ ≠ 1)) ≥ 1/2 - (1/2) ||P_0^{\\otimes N} - P_1^{\\otimes N}||_TV. For this minimax error probability to fall strictly "
        "below α, we require ||P_0^{\\otimes N} - P_1^{\\otimes N}||_TV ≥ 1 - 2α > 0. Substituting our upper bound on total variation gives: "
        "(C_K N / 4σ²) (Δη)^{4K-2} ≥ (1 - 2α)². Solving for sample size N directly yields: "
        "N ≥ (4(1 - 2α)² / C_K) σ² (Δη)^{-(4K-2)} = Ω(σ² (Δη)^{-(4K-2)}). "
        "Because the two configurations μ_0 and μ_1 belong to the declared class of K-cohort economies, no estimator—whether linear or non-linear, "
        "parametric or non-parametric, biased or unbiased—can achieve error probability below α using fewer than N* observations."
    ),
    (
        "The scaling exponent 4K - 2 dictates an extreme sensitivity to cohort count K. For K = 2 cohorts, the exponent is 4(2) - 2 = 6; for K = 3, "
        "it is 4(3) - 2 = 10. Consider two algorithmic desks narrowing their rebalancing horizon difference from Δη = 0.10 to Δη = 0.01:\n"
        "- For K = 2: (0.10 / 0.01)^6 = 10^6. The required observation count increases by one million times (from 1,000 trades to 1 billion trades).\n"
        "- For K = 3: (0.10 / 0.01)^{10} = 10^{10}. The required observation count increases by ten billion times (from 1,000 to 10 trillion trades)!\n"
        "In modern automated markets where algorithmic desks operate at sub-second speeds with closely overlapping horizons (Δη < 0.01), "
        "recovering latent cohort parameters requires sample sizes that exceed decades or centuries of trading data, rendering deconvolution impossible."
    ),
    (
        "Algorithm 1 takes estimated impulse response taps h^_t = (1/N) ∑_{j=1}^N Y_t^{(j)} for t = 0, ..., 4K - 1. We construct the (2K × 2K) "
        "Hankel matrix [H_K]_{i,j} = h^_{i+j-2}. In the noise-free limit, H_K factors as H_K = V_K D_K V_K^T, where V_K is the (2K × K) Vandermonde "
        "matrix with columns v_k = [1, η_k, ..., η_k^{2K-1}]^T and D_K = diag(w_1, ..., w_K). To recover the nodes {η_k}, we solve the linear system "
        "H_K c = -h_{2K} for the annihilating polynomial coefficient vector c = [c_0, c_1, ..., c_{K-1}]^T. The roots of P(z) = z^K + ∑_{j=0}^{K-1} c_j z^j "
        "are the estimated memory rates η^_1, ..., η^_K. Finally, portfolio weights w^_k are obtained by solving the linear least-squares Vandermonde "
        "system V_K w = h^_0, completing the closed-form reconstruction."
    ),
    (
        "Proposition 3.3 proves that σ_{2K}(H_K) ≥ c_K (Δη)^{2K-1}. The proof establishes a dual variational formulation: for any unit vector "
        "u ∈ R^{2K} (||u||_2 = 1), the polynomial P_u(η) = ∑_{j=0}^{2K-1} u_j η^j satisfies u^T H_K u = ∑_{k=1}^K w_k P_u(η_k)². "
        "By Markov-Chebyshev extremal polynomial theory on K nodes {η_1, ..., η_K} with minimum spacing Δη, any polynomial of degree 2K - 1 that has "
        "unit L² coefficient norm must satisfy ∑_{k=1}^K w_k P_u(η_k)² ≥ c_K (Δη)^{2(2K-1)}. Taking the square root gives the singular value bound "
        "σ_{2K}(H_K) ≥ c_K (Δη)^{2K-1}. Because σ_1(H_K) ≤ ∑ w_k = 1, the condition number κ(H_K) = σ_1 / σ_{2K} scales precisely as (Δη)^{-(2K-1)}, "
        "proving that Hankel matrix inversion is intrinsically ill-conditioned."
    ),
    (
        "Theorem 3.2 proves that Algorithm 1 achieves the lower bound rate. With Gaussian tap noise of variance σ²/N, the spectral perturbation is "
        "||δH_K||_2 ≤ C √(K / N) σ with high probability. Solving H_K c = -h_{2K} propagates noise into polynomial coefficients as "
        "||δc||_2 ≤ ||δH_K||_2 / σ_{2K}(H_K) ≤ C σ N^{-1/2} (Δη)^{-(2K-1)}. By Wilkinson's polynomial root perturbation theorem, the displacement of "
        "the roots {η_k} is bounded by |η^_k - η_k| ≤ C ||δc||_2 / |P'(η_k)|. Because |P'(η_k)| = ∏_{j ≠ k} |η_k - η_j| ≥ c (Δη)^{K-1}, the root error "
        "scales as |η^_k - η_k| ≤ O(σ N^{-1/2} (Δη)^{-2K}). Setting target accuracy δ and solving for N gives N = O(σ² δ^{-2} (Δη)^{-(4K-2)}), "
        "matching Theorem 3.1 up to constant factors."
    ),
    (
        "Subspace identification methods (such as ESPRIT or Matrix Pencil) bypass polynomial root-finding by computing generalized eigenvalues "
        "of shifted Hankel submatrices: H_{K,1} v = λ H_{K,0} v. However, the column spaces of both H_{K,0} and H_{K,1} are identical to the range "
        "of the Vandermonde matrix V_K. The oblique projector onto this subspace has condition number κ(V_K) = σ_1(V_K) / σ_K(V_K) ≍ (Δη)^{-(2K-1)}. "
        "Inverting this subspace projection to isolate individual generalized eigenvalues amplifies tap noise by the exact same factor (Δη)^{-(2K-1)}. "
        "Thus, ESPRIT, Matrix Pencil, and Prony's method all suffer from identical condition number scaling, confirming the barrier is physical, not algorithmic."
    ),
    (
        "An active probing sequence u_1, ..., u_T injected into a limit order book with Kyle depth κ and transient impact kernel G(t) generates "
        "cumulative execution loss Cost(u) = ∑_{t=1}^T u_t (p_t - p_0) = (1/2) u^T T_G u + ∑ u_t ε_t, where [T_G]_{i,j} = G(|i - j|). "
        "Lemma 4.2 proves that for any non-increasing, convex price impact kernel G(t) > 0, the symmetric Toeplitz matrix T_G is strictly positive "
        "definite: u^T T_G u > 0 for all u ≠ 0. By Bochner's theorem, G(|t|) is the Fourier transform of a positive spectral measure with full support. "
        "Consequently, exploratory market probing is never self-financing: an active supervisor cannot extract information from order books "
        "without paying a positive expected deadweight execution cost ('No Sure Gain')."
    ),
    (
        "To distinguish two candidate trader populations μ_0 and μ_1 separated by Δη with target precision δ, the active probe sequence u_1, ..., u_T "
        "must excite the latent memory modes. The output price response difference is Δp_t = ∑_{s=1}^t ΔG(t - s) u_s. The Fisher information "
        "accumulated by the probe sequence is I_u = (1 / σ²) ∑_{t=1}^T (Δp_t)² = (1 / σ²) u^T (ΔT_G)^T (ΔT_G) u. "
        "Because ΔG(t) vanishes for the first 2K - 1 lags and scales as (Δη)^{2K-1} thereafter, the spectral norm of ΔT_G satisfies "
        "||ΔT_G||_2 ≤ C κ (Δη)^{2K-1}. To achieve information content I_u ≥ δ^{-2}, the probe order volume must satisfy "
        "||u||_2² = ∑_{t=1}^T u_t² ≥ Ω(σ² κ^{-2} δ^{-2} (Δη)^{-(4K-2)}). Probing volume scales inversely with the (4K-2)-th power of spacing."
    ),
    (
        "An active probing supervisor must maintain mark-to-market margin solvency with clearinghouse capital reserves B. To avoid directional price "
        "trends, the optimal probe sequence oscillates, yielding cumulative inventory x_t = ∑_{s=1}^t u_s with peak excursion ||x||_∞ ≍ δ^{-1}. "
        "The supervisor's mark-to-market loss at period t is Loss_t = x_t (p_t - p_0) - Cost_t. Adverse price excursions scale as "
        "sup_t |x_t Δp_t| ≍ κ ||x||_∞ ||u||_∞ ≍ κ δ^{-2} ||u||_2² ≍ Ω(σ² δ^{-4} (Δη)^{-(4K-2)}). "
        "To guarantee solvency with probability 1 - α, cash margin capital must satisfy B = Ω(δ^{-4}). "
        "Because capital scales with the fourth power of precision: doubling accuracy requires a 16-fold increase in margin capital, imposing a massive financial barrier."
    ),
    (
        "Table 4 grounds this financial lower bound in institutional parameters for US 10-Year Treasury futures (ZN, depth κ = $12.50 / lot, daily σ = 0.85%) "
        "and E-mini S&P 500 futures (ES). To identify two algorithmic cohorts separated by Δη = 0.05 on a weekly re-estimation schedule, the required active "
        "order volume generates an annual execution loss of $15.4 million in 10-Year Treasuries and $356.2 million in E-mini S&P 500 futures! "
        "For a regulatory agency tasked with market surveillance across dozens of futures contracts, active price probing would consume hundreds of "
        "millions of dollars in cash execution losses and tie up billions in margin collateral, proving active probing is economically and legally impossible."
    ),
    (
        "For stationary Gaussian price returns Δp_t under white noise flow shocks ε_t with variance σ_ε², the spectral density is "
        "f_θ(λ) = (σ_ε² / 2π) |G_θ(e^{iλ})|² on [-π, π]. The asymptotic Kullback-Leibler divergence rate under the Whittle log-likelihood is "
        "lim_{T→∞} (1/T) D_KL = (1/4π) ∫_{-π}^π [ f_0(λ) / f_1(λ) - 1 - log(f_0(λ) / f_1(λ)) ] dλ. Because candidate measures match moments up to order "
        "2K - 1, the open-loop transfer functions differ by only |H_0(e^{iλ}) - H_1(e^{iλ})| = O((Δη)^{2K-1}) uniformly across all frequencies λ. "
        "Propagating through the closed-loop denominator gives f_0(λ) / f_1(λ) = 1 + O((Δη)^{2K-1}). The divergence integral collapses to O((Δη)^{4K-2}), "
        "proving passive observation requires sample length T = Ω((Δη)^{-(4K-2)}) because ambient white noise lacks persistent excitation."
    ),
    (
        "Section 4.5 and Table 6 stress-test Theorem 3.1 against real, heavy-tailed 1-minute Bitcoin perpetual return shocks (October 2026 data). "
        "Real crypto price changes exhibit extreme excess kurtosis (> 12.4), fat Pareto tails, and volatility clustering. Rather than approximating "
        "noise with a normal distribution, we implement exact multinomial empirical resampling across sample sizes N. Across memory gaps "
        "Δη ∈ [0.05, 0.30], log-log regressions of log(N) on log(1 / Δη) yield fitted empirical slopes of -6.01 for K = 2 (theoretical -6.00) and -9.81 "
        "for K = 3 (theoretical -10.00). This confirms that empirical heavy tails do not destroy the identification barrier: the moment-matching "
        "cancellation mechanism is algebraic and holds invariant under any zero-mean noise distribution."
    ),
    (
        "By Bernstein's Theorem, a completely monotone memory kernel k(t) satisfies (-1)^n k^{(n)}(t) ≥ 0 and admits an integral representation "
        "k(t) = ∫_0^1 η^t dF(η) for a continuous measure F on [0, 1), representing a continuum of trading horizons (K = ∞). Recovering F(η) requires "
        "inverting the continuous Hausdorff moment sequence, which acts as a compact, infinitely smoothing Fredholm integral operator with exponential "
        "singular value decay σ_m ≍ exp(-c m). Inverting this compact operator under noise is exponentially ill-posed: by Donoho's theorem, distinguishing "
        "two continuous distributions with Wasserstein distance w requires N ≥ exp(C / w) observations. Minimax accuracy collapses to logarithmic "
        "w = Θ(1 / log(N / σ²)), proving continuous memory distributions cannot be deconvolved from price data."
    ),
    (
        "Theorem 5.1 proves that observing class-tagged order flows y_t = [y_{1,t}, ..., y_{K,t}]^T (e.g. MiFID II RTS 24 algo_id tags) completely uncouples "
        "the estimation problem. Because each cohort state evolves independently as x_{k,t} = η_k x_{k,t-1} + (1 - η_k) p_{t-1}, observing y_{k,t} allows "
        "the supervisor to run K separate single-variable autoregressions of y_{k,t} on p_{t-1}, completely bypassing the feedback denominator D_{cl}(z). "
        "Sample complexity for memory rates collapses from Θ(σ² (Δη)^{-(4K-2)}) to Θ(σ² (Δη)^{-2}) (the exponent collapses from 4K - 2 to 2). "
        "For portfolio weights w_k, sample complexity is O(σ² δ^{-2}), which is O(1) completely independent of memory spacing Δη."
    ),
    (
        "Proposition 5.5 formalizes the supervisor's choice rule: mandate class disclosure if and only if fixed regulatory reporting cost C_rep is less "
        "than active probing deadweight loss C_probe(Δη) ≍ κ σ² (Δη)^{-(4K-2)}. This establishes an intermediate economic band [Δη_min, Δη_max]:\n"
        "- When Δη > Δη_max, algorithms are widely separated; price-based estimation is cheap, and disclosure is unnecessary.\n"
        "- When Δη < Δη_min, algorithms are virtually identical; distinguishing them provides negligible regulatory benefit.\n"
        "- In the critical band Δη ∈ [Δη_min, Δη_max], algorithms are distinct enough to create differential systemic risk, but close enough to make "
        "price-based deconvolution prohibitively expensive. Here, mandatory regulatory disclosure is socially indispensable."
    ),
    (
        "Table 7 evaluates parameter estimation across 8 primary CFTC futures markets (E-mini S&P, 10Y Treasuries, Crude Oil, Euro FX, Corn, etc.). "
        "Weekly Disaggregated Commitments of Traders (DCOT) position reports categorize market open interest into Managed Money (hedge funds), "
        "Swap Dealers, and Commercial Hedgers. By mapping these categories into structural model cohorts, the paper estimates memory persistence η_k "
        "and market shares w_k. Across all 8 markets, parameter uncertainty intervals derived from public CFTC disclosure were 25x to 55x narrower "
        "than what econometric inversion on daily price data could achieve, confirming the empirical value of regulatory reporting."
    ),
    (
        "Under SHA-256 pre-registration hash 591e71c9... (registered 31 October 2026), Table 8 replicates parameter estimation across 12 additional "
        "CFTC futures markets (gold, silver, copper, corn, soybeans, wheat, live cattle, coffee, sugar, cotton, Nasdaq-100, British pound). Across all 12 "
        "markets, empirical uncertainty intervals for trader memory η_k and weights w_k derived from weekly DCOT reports are 23.4x to 68.7x narrower "
        "than under price-only econometric inversion. In wheat and corn, the ratio reaches 64x; in gold and copper, 58x. The Data Equivalence Multiplier "
        "reveals that a single weekly public CFTC report delivers information equivalent to 14,200 to 89,500 active market probes."
    ),
    (
        "Table 9 presents the complete pre-registered 22-test scorecard across the empirical evaluation suite: exactly 11 tests passed at the 5% level, "
        "10 failed, and 1 was unsupported due to exchange data limits. The 11 passing tests confirm the CFTC position interval narrowing, exact "
        "multinomial Bitcoin noise scaling, and Prony-Hankel inversion. The 10 failures concentrate in high-frequency crypto perpetuals (hypotheses N2 and N3). "
        "By reporting every pre-registered test failure transparently, the paper eliminates publication bias and proves that coarse public buckets fail, "
        "strengthening the argument for granular algorithmic tags."
    ),
    (
        "In Table 9, hypotheses N2 (price forecasting position ratios) and N3 (taker flow pinning down combined response Ψ) failed Diebold-Mariano tests "
        "on 29 and 25 of 30 Binance perpetual contracts (October 2026 data, SHA-256 72cbc8ba...). This failure demonstrates **Within-Class Sign Cancellation**: "
        "public reporting buckets (e.g. 'Top Traders' or 'Managed Money') combine opposing algorithmic strategies, such as trend-following CTAs "
        "(momentum, w_CTA > 0, η_CTA ≈ 0.9) and cash-futures basis arbitrageurs (mean-reverting, w_Arb < 0, η_Arb ≈ 0.1). Because their orders move in "
        "opposite directions, their flows destructively interfere: w_CTA y_{CTA,t} + w_Arb y_{Arb,t} ≈ 0. Coarse public buckets wash out predictive signals, "
        "proving that regulators must mandate granular MiFID II RTS 24 algo_id tags."
    ),
    (
        "Theorem 6.1 constructs two state-space systems: A_1 = diag(λ_1, λ_2) (normal, orthogonal eigenvectors) and A_2 = [λ_1, γ; 0, λ_2] (non-normal, "
        "coupling γ > 0). Both systems share identical closed-loop eigenvalues 0 < λ_2 < λ_1 < 1, identical one-step return variance, and identical "
        "stationary covariance under white noise. However, because A_2's eigenvectors are non-orthogonal, its transient matrix powers scale as "
        "[A_2^t]_{1,2} = γ (λ_1^t - λ_2^t) / (λ_1 - λ_2), which grows arbitrarily large as γ increases. Peak transient gain sup_t ||A_2^t||_2 grows without "
        "bound as γ → ∞, proving that eigenvalue stability and low stationary variance fail to protect a market from violent transient amplification."
    ),
    (
        "The ε-pseudospectrum σ_ε(A) = {z ∈ C : ||(zI - A)^{-1}||_2 > ε^{-1}} quantifies transient sensitivity. While true eigenvalues of A_2 lie "
        "strictly inside the unit disk at λ_1, λ_2 < 1, the non-normal resolvent blows up in the complex plane, causing pseudospectral contours to protrude "
        "far outside the unit circle |z| > 1. By the Kreiss Matrix Theorem, peak transient excursion satisfies K(A) ≤ sup_t ||A^t||_2 ≤ e · n · K(A), "
        "where K(A) = sup_{|z|>1} (|z|-1) ||(zI - A)^{-1}||. Figure 7 shows two markets with identical 5-period half-lives and 1.2% volatility: "
        "Market 1 decays smoothly, while Market 2 experiences a 40x transient loss spike. Traditional VaR measures only stationary variance, remaining blind to flash crash risks."
    ),
    (
        "Appendix F (Theorem F.3) analyzes an unlevered warehousing desk with carry costs b I + d I² under a hard stress budget B. The optimal inventory "
        "position I(C_N, F) depends solely on the scalar cumulative impulse response G = ∑_{t<H} h_t. Estimating G converges at the ordinary parametric "
        "rate O(N^{-1/2}), completely free of cohort spacing Δη, cohort count K, or memory floors. Thus, cohort deconvolution is unnecessary for aggregate "
        "inventory warehousing. In contrast, targeted supervisory halts (Proposition 5.6 / S23) require identifying which specific cohort k is rogue or over-leveraged "
        "to selectively halt its access while keeping market-makers open. This strictly requires estimating individual parameters (w_k, η_k), "
        "confronting the full (Δη)^{-(4K-2)} barrier and proving targeted interventions require mandatory algo_id tags."
    )
]

def build_pure_questions_file():
    doc = Document()
    
    # Page Margins
    for s in doc.sections:
        s.top_margin = Inches(1.0); s.bottom_margin = Inches(1.0)
        s.left_margin = Inches(1.0); s.right_margin = Inches(1.0)
        
        header = s.header; hp = header.paragraphs[0]; hp.alignment = WD_ALIGN_PARAGRAPH.RIGHT
        hrun = hp.add_run("Paper 1: Research Questions (30 Questions)")
        hrun.font.name = "Calibri"; hrun.font.size = Pt(8.5); hrun.font.color.rgb = RGBColor(120, 120, 120)
        
        footer = s.footer; fp = footer.paragraphs[0]; fp.alignment = WD_ALIGN_PARAGRAPH.CENTER
        frun = fp.add_run("What Prices Cannot Tell a Market Supervisor")
        frun.font.name = "Calibri"; frun.font.size = Pt(8.5); frun.font.color.rgb = RGBColor(120, 120, 120)

    # Document Header Title
    p_title = doc.add_paragraph()
    p_title.paragraph_format.space_before = Pt(12); p_title.paragraph_format.space_after = Pt(14)
    r_title = p_title.add_run("Paper 1: 30 Research Questions\nWhat Prices Cannot Tell a Market Supervisor")
    r_title.font.name = "Calibri"; r_title.font.size = Pt(18); r_title.font.bold = True; r_title.font.color.rgb = RGBColor(11, 37, 69)

    # The 30 Questions - clean, pure, numbered
    for num, q_text in QUESTIONS_30_PURE:
        p = doc.add_paragraph()
        p.paragraph_format.space_before = Pt(8); p.paragraph_format.space_after = Pt(6)
        p.paragraph_format.line_spacing = 1.15
        
        r_num = p.add_run(f"{num}. ")
        r_num.font.name = "Calibri"; r_num.font.size = Pt(11); r_num.font.bold = True; r_num.font.color.rgb = RGBColor(11, 37, 69)
        
        r_text = p.add_run(q_text)
        r_text.font.name = "Calibri"; r_text.font.size = Pt(10.5); r_text.font.color.rgb = RGBColor(29, 45, 68)

    out_path = ROOT / "Paper1_Questions_Workbook.docx"
    doc.save(str(out_path))
    print(f"Saved Pure Questions to: {out_path}")
    return out_path

def build_pure_answers_file():
    doc = Document()
    
    # Page Margins
    for s in doc.sections:
        s.top_margin = Inches(1.0); s.bottom_margin = Inches(1.0)
        s.left_margin = Inches(1.0); s.right_margin = Inches(1.0)
        
        header = s.header; hp = header.paragraphs[0]; hp.alignment = WD_ALIGN_PARAGRAPH.RIGHT
        hrun = hp.add_run("Paper 1: Reference Answers (30 Questions)")
        hrun.font.name = "Calibri"; hrun.font.size = Pt(8.5); hrun.font.color.rgb = RGBColor(120, 120, 120)
        
        footer = s.footer; fp = footer.paragraphs[0]; fp.alignment = WD_ALIGN_PARAGRAPH.CENTER
        frun = fp.add_run("What Prices Cannot Tell a Market Supervisor")
        frun.font.name = "Calibri"; frun.font.size = Pt(8.5); frun.font.color.rgb = RGBColor(120, 120, 120)

    # Document Header Title
    p_title = doc.add_paragraph()
    p_title.paragraph_format.space_before = Pt(12); p_title.paragraph_format.space_after = Pt(14)
    r_title = p_title.add_run("Paper 1: Reference Answers for 30 Questions\nWhat Prices Cannot Tell a Market Supervisor")
    r_title.font.name = "Calibri"; r_title.font.size = Pt(18); r_title.font.bold = True; r_title.font.color.rgb = RGBColor(11, 37, 69)

    # The 30 Questions + Answers
    for idx, (num, q_text) in enumerate(QUESTIONS_30_PURE):
        ans_text = ANSWERS_30_PURE[idx]
        
        p_q = doc.add_paragraph()
        p_q.paragraph_format.space_before = Pt(12); p_q.paragraph_format.space_after = Pt(2)
        p_q.paragraph_format.keep_with_next = True
        
        r_num = p_q.add_run(f"{num}. ")
        r_num.font.name = "Calibri"; r_num.font.size = Pt(11); r_num.font.bold = True; r_num.font.color.rgb = RGBColor(11, 37, 69)
        
        r_q = p_q.add_run(q_text)
        r_q.font.name = "Calibri"; r_q.font.size = Pt(10); r_q.font.bold = True; r_q.font.color.rgb = RGBColor(19, 64, 116)
        
        p_a = doc.add_paragraph()
        p_a.paragraph_format.space_before = Pt(2); p_a.paragraph_format.space_after = Pt(8)
        p_a.paragraph_format.line_spacing = 1.15
        
        r_a_hdr = p_a.add_run("Answer: ")
        r_a_hdr.font.name = "Calibri"; r_a_hdr.font.size = Pt(10); r_a_hdr.font.bold = True; r_a_hdr.font.color.rgb = RGBColor(0, 119, 182)
        
        r_a = p_a.add_run(ans_text)
        r_a.font.name = "Calibri"; r_a.font.size = Pt(9.5); r_a.font.color.rgb = RGBColor(29, 45, 68)

    out_path = ROOT / "Paper1_Answers_Solution_Manual.docx"
    doc.save(str(out_path))
    print(f"Saved Pure Answers to: {out_path}")
    return out_path

if __name__ == "__main__":
    q_file = build_pure_questions_file()
    a_file = build_pure_answers_file()
    
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
    print("Clean build complete!")
