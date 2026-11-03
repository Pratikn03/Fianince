"""
Generate the 30 Master Questions and Answers files for Paper 1:
- Exactly 30 deep, thorough questions.
- Merged 'What to focus on:' for each question (combining mathematical derivation, control dynamics, microstructure, and empirics into ONE).
- ZERO mentions of 'Focus for Sujan' or 'Focus for Prashant'.
- ZERO empty boxes or fill-in gaps.
- Strictly Paper 1 ONLY.
"""

from pathlib import Path
import docx
from docx import Document
from docx.shared import Inches, Pt, RGBColor
from docx.enum.text import WD_ALIGN_PARAGRAPH
import shutil

ROOT = Path("/Users/pratik_n/Downloads/Machine_Markets_Master_Release")

# 30 Master Questions with Merged 'What to focus on:'
MASTER_30 = [
    {
        "num": 1,
        "title": "State-Space Model & Closed-Loop Transfer Function Derivation",
        "q": (
            "In Section 2, the limit order book is populated by K trader cohorts with memory filters x_{k,t} = η_k x_{k,t-1} + (1 - η_k) p_{t-1}, "
            "weights w_k > 0 (∑ w_k = 1), Kyle depth impact κ > 0, and dealer inventory damping q > 0. "
            "Derive the exact discrete-time state-space realization (A, B, C, D) of the coupled system, show how closing the price loop yields "
            "the closed-loop transfer function G(z) = κ H(z) / (1 + κ q H(z)) where H(z) = ∑ w_k / (1 - η_k z^{-1}), and explain the algebraic "
            "mechanism by which the feedback denominator alters the system eigenvalues."
        ),
        "focus": (
            "The step-by-step state-space realization (A, B, C, D), how price feedback couples internal trader expectations, "
            "the transformation from open-loop plant H(z) to closed-loop G(z), and why feedback control dynamics make it impossible "
            "for a market supervisor to observe individual trader learning rates directly from equilibrium prices."
        )
    },
    {
        "num": 2,
        "title": "Open-Loop Transmission Zeros vs. Closed-Loop Return Poles",
        "q": (
            "Prove Lemma 2.1 and Lemma 2.2 regarding the degrees and root structures of N(z), D(z), and D_{cl}(z) = D(z) + κ q N(z). "
            "Why do the individual trader memory parameters η_k enter as roots of D(z) and transmission zeros of the price return response, "
            "rather than uncoupled observable poles? Explain why the roots of D_{cl}(z) interlace with {η_k} on the real interval [0, 1), and "
            "what this interlacing implies for closed-loop stability."
        ),
        "focus": (
            "The Gauss-Lucas theorem and Markov root interlacing on [0, 1), why trader memory rates η_k enter as transmission zeros "
            "of return response rather than observable poles, and how closed-loop feedback guarantees asymptotic stability while masking "
            "latent algorithmic memory modes."
        )
    },
    {
        "num": 3,
        "title": "The Econometric Under-Determination of Price Time-Series",
        "q": (
            "Explain mathematically why standard econometric time-series estimation (such as ARMA or ARIMA modeling) on equilibrium price returns "
            "Δp_t fails to identify the underlying trader parameters. Specifically, show that matching the K observable roots of the closed-loop "
            "characteristic polynomial D_{cl}(z) yields only K scalar equations for 2K + 1 structural unknowns (w, η, κ, q), proving the existence "
            "of an unidentifiable (K+1)-dimensional manifold of observationally equivalent market configurations."
        ),
        "focus": (
            "The algebraic dimension deficit (matching K roots of D_{cl}(z) versus 2K+1 structural unknowns (w, η, κ, q)), why ARMA/ARIMA "
            "price regressions cannot separate market depth from trader speed, and the geometry of the resulting (K+1)-dimensional manifold "
            "of observationally equivalent market configurations."
        )
    },
    {
        "num": 4,
        "title": "Theorem 2.1: Merged Measure Invariance and Moment Equivalence",
        "q": (
            "Provide the complete proof of Theorem 2.1 (Merged Measure Invariance). Show that two distinct trader populations represented by Radon "
            "measures μ_0 and μ_1 produce identical noise-free equilibrium price paths under all exogenous inputs if and only if their rational "
            "transfer functions H_{μ_0}(z) and H_{μ_1}(z) coincide. Prove why this equality holds if and only if their impulse response moments "
            "agree for the first 2K + 1 periods (t = 0, 1, ..., 2K), and explain why this permits two slow institutional desks to perfectly mimic five fast HFTs."
        ),
        "focus": (
            "The rational function uniqueness theorem, why matching 2K+1 Markov moments h_t is necessary and sufficient for two different trader "
            "populations to produce identical noise-free price paths, and the market implication that two slow institutional algorithmic desks "
            "can perfectly mimic five fast HFT market makers."
        )
    },
    {
        "num": 5,
        "title": "Remark 2.2: The Two-Root Stock-Flow Inventory Bridge",
        "q": (
            "Reconstruct Remark 2.2 and Supplement S6: How does the paper formally bridge high-frequency trader flow demand u_t to weekly reported "
            "Commitments of Traders (COT) position stocks S_t? Derive the quadratic recurrence connecting net weekly position changes ΔS_t to flow "
            "demand, show why inverting this relationship requires solving a quadratic characteristic equation, and prove that dynamic stability "
            "uniquely selects the smaller root (|λ| < 1) while rejecting the explosive root."
        ),
        "focus": (
            "The discrete-time second-order recurrence connecting high-frequency flow demand u_t to weekly reported COT position stocks S_t, "
            "the quadratic characteristic equation, and why dynamic stability strictly selects the smaller root (|λ| < 1) while rejecting the explosive root (|λ| > 1)."
        )
    },
    {
        "num": 6,
        "title": "Corollary 2.3: Plug-In Estimation Stability of Market Parameters",
        "q": (
            "Analyze Corollary 2.3 and Supplement S7: In practical market deconvolution, the structural parameters (persistence a, Kyle's depth κ, "
            "and fundamental value p*) must be estimated via plug-in estimators (a^, κ^, p^*). Prove that when these parameters are estimated at the "
            "standard parametric rate O_p(T^{-1/2}), the condition number and asymptotic rate of Prony-Hankel deconvolution are preserved without "
            "rate degradation."
        ),
        "focus": (
            "The asymptotic perturbation analysis when structural parameters (a, κ, p*) are estimated via plug-in estimators at rate O_p(T^{-1/2}), "
            "and why this fast parametric convergence ensures that baseline estimation error does not degrade the slower Hankel deconvolution rate."
        )
    },
    {
        "num": 7,
        "title": "Theorem 3.1: Le Cam Two-Point Construction & Moment-Matched Perturbation",
        "q": (
            "Reconstruct the foundation of Theorem 3.1: How are the two candidate Radon measures μ_0 and μ_1 constructed over K cohorts with minimum "
            "memory spacing Δη = min_{j ≠ k} |η_j - η_k|? Detail the mathematical construction of the signed perturbation measure dΔ(η) using "
            "Chebyshev-type polynomial weighting, and prove that matching the first 2K - 1 algebraic moments forces the leading 2K - 1 impulse response "
            "difference taps to vanish identically: Δh_t = 0 for t = 0, 1, ..., 2K - 1."
        ),
        "focus": (
            "The Le Cam two-point testing framework, the construction of the signed perturbation measure dΔ(η) using Chebyshev-type polynomial "
            "weighting on nodes {η_k}, and the algebraic proof that matching 2K-1 moments forces the leading 2K-1 impulse response difference "
            "taps to vanish identically (Δh_t = 0 for t < 2K)."
        )
    },
    {
        "num": 8,
        "title": "Kullback-Leibler Divergence Taylor Remainder and Total Variation Bound",
        "q": (
            "In the proof of Theorem 3.1, show how the Kullback-Leibler divergence between product measures P_0^{\\otimes N} and P_1^{\\otimes N} under "
            "Gaussian noise variance σ² expands as D_KL = (N / 2σ²) ∑_{t=2K}^∞ (Δh_t)². Prove that this summation collapses to order "
            "O(N σ^{-2} (Δη)^{4K-2}), and apply Pinsker's inequality to establish the total variation distance bound "
            "||P_0^{\\otimes N} - P_1^{\\otimes N}||_TV ≤ √(C_K N / 4σ²) (Δη)^{2K-1}."
        ),
        "focus": (
            "The expansion of the Kullback-Leibler divergence D_KL(P_0^{\\otimes N} || P_1^{\\otimes N}) = (N / 2σ²) ∑_{t=2K}^∞ (Δh_t)², "
            "the proof that this sum collapses to order O(N σ^{-2} (Δη)^{4K-2}), and the application of Pinsker's inequality to bound total variation "
            "distance by O(√(N / σ²) (Δη)^{2K-1})."
        )
    },
    {
        "num": 9,
        "title": "Deduction of the Ω(σ²(Δη)^{-(4K-2)}) Minimax Lower Bound for General α",
        "q": (
            "Complete the proof of Theorem 3.1 for an arbitrary testing error level α ∈ (0, 1/2). Using Le Cam's testing inequality "
            "inf_ψ max(P_0(ψ ≠ 0), P_1(ψ ≠ 1)) ≥ 1/2 - (1/2) ||P_0^{\\otimes N} - P_1^{\\otimes N}||_TV, derive the exact lower bound "
            "N* ≥ (4(1 - 2α)² / C_K) σ² (Δη)^{-(4K-2)} = Ω(σ² (Δη)^{-(4K-2)}). Explain why this bound applies uniformly to all estimators "
            "(biased or unbiased, linear or non-linear)."
        ),
        "focus": (
            "The application of Le Cam's testing inequality for arbitrary testing error levels α ∈ (0, 1/2), the algebraic derivation of "
            "N* ≥ (4(1-2α)² / C_K) σ² (Δη)^{-(4K-2)}, and why this minimax lower bound applies uniformly to all possible estimation algorithms regardless of bias or linearity."
        )
    },
    {
        "num": 10,
        "title": "The Cohort Exponent Scaling Law: (Δη)^{-6} vs. (Δη)^{-10}",
        "q": (
            "Analyze the economic and computational consequences of the scaling exponent 4K - 2. Calculate the exact sample size explosion when "
            "two trading algorithms narrow their memory spacing from Δη = 0.10 to Δη = 0.01 for K = 2 cohorts (a factor of 10^6) versus K = 3 cohorts "
            "(a factor of 10^{10}). What does this exponent imply about the feasibility of deconvolving high-frequency trading algorithms operating "
            "at millisecond time scales?"
        ),
        "focus": (
            "The origin of the 4K-2 exponent, the exact sample size calculations showing a 10^6 explosion for K=2 and a 10^{10} explosion for K=3 "
            "when spacing narrows from 0.10 to 0.01, and why this mathematical barrier makes it impossible for regulators to separate high-frequency "
            "algorithms operating across overlapping millisecond horizons."
        )
    },
    {
        "num": 11,
        "title": "Algorithm 1: Prony-Hankel Deconvolution Architecture",
        "q": (
            "Detail the algorithmic architecture of Algorithm 1 (Prony-Hankel Deconvolution). Starting from estimated impulse response taps h^_t, "
            "show how the (2K × 2K) Hankel matrix H_K is formed, how solving H_K c = -h_{2K} determines the annihilating polynomial coefficients, "
            "how rooting P(z) yields the memory rates η^_k, and how the portfolio weights w^_k are recovered via linear Vandermonde inversion."
        ),
        "focus": (
            "The step-by-step matrix algebra of Algorithm 1, forming the (2K × 2K) Hankel matrix H_K from estimated taps, solving the linear system "
            "H_K c = -h_{2K} for the annihilating polynomial coefficients, extracting roots to recover memory rates η^_k, and performing Vandermonde "
            "least-squares inversion to recover portfolio weights w^_k."
        )
    },
    {
        "num": 12,
        "title": "Proposition 3.3: Hankel Singular Value Lower Bound via Chebyshev Moments",
        "q": (
            "Reconstruct the proof of Proposition 3.3: Prove that the smallest singular value of the Hankel matrix satisfies "
            "σ_{2K}(H_K) ≥ c_K (Δη)^{2K-1}. How does the proof construct a dual variational problem using Chebyshev extremal polynomials on the "
            "discrete node set {η_1, ..., η_K}, and why does this establish that the Hankel condition number κ(H_K) scales precisely as (Δη)^{-(2K-1)}?"
        ),
        "focus": (
            "The dual Chebyshev extremal polynomial variational problem on nodes {η_1, ..., η_K}, the rigorous proof that "
            "σ_{2K}(H_K) ≥ c_K (Δη)^{2K-1}, and how this establishes that the Hankel condition number κ(H_K) scales strictly as (Δη)^{-(2K-1)}."
        )
    },
    {
        "num": 13,
        "title": "Theorem 3.2: Matching Minimax Upper Bound & Noise Perturbation Propagation",
        "q": (
            "Prove Theorem 3.2: When estimated taps are corrupted by Gaussian noise with variance σ²/N, show how the Hankel perturbation "
            "||δH_K||_2 ≤ O(σ N^{-1/2}) propagates into the coefficient vector as ||δc||_2 ≤ O(σ N^{-1/2} (Δη)^{-(2K-1)}). Show that root inversion "
            "adds a factor of (Δη)^{-1}, yielding root error |η^_k - η_k| ≤ O(σ N^{-1/2} (Δη)^{-2K}) and establishing sample complexity "
            "O(σ² δ^{-2} (Δη)^{-(4K-2)}), matching Theorem 3.1."
        ),
        "focus": (
            "The perturbation propagation from tap noise ||δH||_2 ≤ O(σ N^{-1/2}) into annihilating polynomial coefficients "
            "||δc||_2 ≤ O(σ N^{-1/2} (Δη)^{-(2K-1)}) and root displacements |η^_k - η_k| ≤ O(σ N^{-1/2} (Δη)^{-2K}), proving that Prony's method "
            "achieves the matching minimax upper rate O(σ² (Δη)^{-(4K-2)})."
        )
    },
    {
        "num": 14,
        "title": "Subspace Estimator Invariance: ESPRIT and Matrix Pencil Conditioning",
        "q": (
            "Explain why alternative subspace identification methods (such as ESPRIT or Matrix Pencil) cannot overcome the (Δη)^{-(4K-2)} barrier. "
            "Show that because ESPRIT projects onto the range of the Vandermonde matrix V_K, its oblique subspace projector has condition number "
            "κ(V_K) ≍ (Δη)^{-(2K-1)}, proving that all linear deconvolution methods suffer from the exact same fundamental conditioning ceiling."
        ),
        "focus": (
            "The geometry of shifted Hankel subspaces, why the oblique projection operator onto the Vandermonde column space has condition number "
            "κ(V_K) ≍ (Δη)^{-(2K-1)}, and why ESPRIT, Matrix Pencil, and Prony all share the exact same fundamental conditioning ceiling."
        )
    },
    {
        "num": 15,
        "title": "Lemma 4.2: Positive Definite Toeplitz Cost Matrix and 'No Sure Gain'",
        "q": (
            "Prove Lemma 4.2: For any physically realizable, decaying price impact impulse response G(t) ≥ 0, show that the Toeplitz execution "
            "cost matrix T_G with entries [T_G]_{i,j} = G(|i - j|) is strictly positive definite: u^T T_G u > 0 for all u ≠ 0. Explain the economic "
            "meaning of the 'No Sure Gain' principle: why can exploratory market probing never be self-financing?"
        ),
        "focus": (
            "The derivation of quadratic cash execution loss Cost(u) = (1/2) u^T T_G u + ∑ u_t ε_t, the proof of strict positive definiteness "
            "of T_G for decaying impact kernels via Bochner's theorem, and the economic 'No Sure Gain' principle proving that exploratory market probing "
            "always incurs an expected financial loss."
        )
    },
    {
        "num": 16,
        "title": "Theorem 4.1: The Cumulative Probing Order Volume Lower Bound",
        "q": (
            "Reconstruct the proof of Theorem 4.1: Show that to achieve parameter identification accuracy δ under Kyle's price impact κ, the supervisor's "
            "total cumulative probe order energy must satisfy ||u||_2² = ∑_{t=1}^T u_t² = Ω(σ² κ^{-2} δ^{-2} (Δη)^{-(4K-2)}). How does the Fisher "
            "information matrix of the active probe sequence bound the required order volume from below?"
        ),
        "focus": (
            "The Fisher information accumulation of an active probe sequence under Kyle depth κ, the spectral norm bound "
            "||ΔT_G||_2 ≤ C κ (Δη)^{2K-1}, and the proof that total cumulative probe volume must satisfy ||u||_2² = Ω(σ² κ^{-2} δ^{-2} (Δη)^{-(4K-2)})."
        )
    },
    {
        "num": 17,
        "title": "Theorem 4.3: Account-Level Margin Solvency and the Ω(δ^{-4}) Capital Barrier",
        "q": (
            "Prove Theorem 4.3: To avoid detection, an active probe sequence must oscillate, generating peak cumulative inventory excursions of "
            "order ||x||_∞ ≍ δ^{-1}. Prove that the peak adverse mark-to-market drawdown scales as sup_t |x_t Δp_t| ≍ Ω(σ² δ^{-4} (Δη)^{-(4K-2)}). "
            "Why does exchange margin solvency force the supervisor's cash capital reserve B to scale as Ω(δ^{-4}), and why does doubling precision "
            "multiply required capital by 16?"
        ),
        "focus": (
            "The peak cumulative inventory excursion ||x||_∞ ≍ δ^{-1} generated by oscillatory probing, the peak mark-to-market adverse drawdown "
            "scaling as Ω(σ² δ^{-4} (Δη)^{-(4K-2)}), and why clearinghouse margin solvency forces cash capital reserves to scale as B = Ω(δ^{-4}) "
            "(a 16-fold increase for a 2-fold precision improvement)."
        )
    },
    {
        "num": 18,
        "title": "Table 4 Calibration: 'Disclosure in Dollars' in Treasury & S&P Futures",
        "q": (
            "Examine the institutional calibration in Table 4 ('Disclosure in Dollars'). Using calibrated parameters for US 10-Year Treasury futures "
            "(ZN) and E-mini S&P 500 futures (ES), explain why re-estimating two algorithmic cohorts separated by Δη = 0.05 on a weekly basis requires "
            "$15.4M to $356.2M in annual deadweight execution loss per market. Why does this make active regulatory probing institutional suicide?"
        ),
        "focus": (
            "The institutional parameters for 10-Year Treasury futures (ZN) and E-mini S&P 500 futures (ES), the calibration showing $15.4M to $356.2M "
            "in annual deadweight execution loss per market for weekly re-estimation, and why public regulatory agencies cannot legally or operationally fund proprietary probing."
        )
    },
    {
        "num": 19,
        "title": "Theorem 5.8: Passive Whittle Spectral Divergence Asymptotic Rate Collapse",
        "q": (
            "Reconstruct the proof of Theorem 5.8: For stationary Gaussian price returns Δp_t with spectral density f_θ(λ), formulate the Whittle "
            "log-likelihood and write the asymptotic KL divergence rate integral over [-π, π]. Prove that moment matching forces "
            "f_0(λ) / f_1(λ) = 1 + O((Δη)^{2K-1}) uniformly, causing the divergence rate to collapse to O((Δη)^{4K-2}) and proving that passive "
            "tick data collection costs time at the exact same polynomial rate probing costs capital."
        ),
        "focus": (
            "The return spectral density f_θ(λ) on [-π, π], the Whittle log-likelihood asymptotic divergence rate integral, the proof that "
            "f_0(λ) / f_1(λ) = 1 + O((Δη)^{2K-1}) uniformly, and why ambient white noise lacks persistent excitation, causing passive observation to collapse at rate O((Δη)^{4K-2})."
        )
    },
    {
        "num": 20,
        "title": "Section 4.5 & Table 6: Exact Multinomial Resampling with Real Bitcoin Shocks",
        "q": (
            "Detail the empirical methodology of Section 4.5 and Table 6: How was exact multinomial resampling conducted using real 1-minute Bitcoin "
            "perpetual return shocks without normal approximations? Why did empirical excess kurtosis (> 12.4) and heavy tails preserve the exact "
            "theoretical log-log slope exponents of -6.01 for K = 2 and -9.81 for K = 3 in Figure 5?"
        ),
        "focus": (
            "The empirical resampling methodology using real 1-minute Bitcoin perpetual return shocks without normal approximations, the impact of "
            "Pareto heavy tails and excess kurtosis (> 12.4), and why the empirical log-log slopes of -6.01 (K=2) and -9.81 (K=3) confirm the algebraic "
            "robustness of the moment-matching lower bound."
        )
    },
    {
        "num": 21,
        "title": "Theorem 5.7: Completely Monotone Memory and Minimax Logarithmic Collapse",
        "q": (
            "Prove Theorem 5.7: When the trader population has a continuous memory distribution governed by a completely monotone kernel "
            "k(t) = ∫_0^1 η^t dF(η) (K = ∞), show how the Hausdorff moment sequence maps to a compact Fredholm integral operator with exponential "
            "singular value decay σ_m ≍ exp(-c m). Apply Donoho's functional estimation theorem to prove that minimax estimation error collapses "
            "from polynomial to logarithmic w = Θ(1 / log(N / σ²)), requiring exponential data N ≥ exp(C / w)."
        ),
        "focus": (
            "Bernstein's theorem for completely monotone kernels k(t) = ∫_0^1 η^t dF(η), the mapping of the continuous Hausdorff moment sequence "
            "to a compact Fredholm integral operator with exponential singular value decay σ_m ≍ exp(-c m), and Donoho's theorem proving that minimax "
            "accuracy collapses to logarithmic w = Θ(1 / log(N / σ²))."
        )
    },
    {
        "num": 22,
        "title": "Theorem 5.1: Class-Tagged Disclosure and Decoupled Single-Pole Regressions",
        "q": (
            "Provide the complete proof of Theorem 5.1: Show how observing class-tagged order flows y_{k,t} (e.g. MiFID II RTS 24 algo_id tags) "
            "decouples the coupled feedback loop into K independent single-variable autoregressions. Prove that the sample complexity to estimate "
            "memory rates collapses from Θ(σ² (Δη)^{-(4K-2)}) to Θ(σ² (Δη)^{-2}), and prove that estimating portfolio weights w_k becomes O(1) "
            "completely independent of memory spacing Δη."
        ),
        "focus": (
            "How observing class-tagged order flows y_{k,t} (MiFID II RTS 24 algo_id tags) decouples the coupled feedback loop into K independent "
            "regressions, why memory rate sample complexity collapses from Θ(σ² (Δη)^{-(4K-2)}) to Θ(σ² (Δη)^{-2}), and why estimating portfolio "
            "weights w_k becomes O(1) completely independent of spacing Δη."
        )
    },
    {
        "num": 23,
        "title": "Proposition 5.5: The Supervisory Choice Rule & Critical Information Band",
        "q": (
            "Analyze Proposition 5.5 (The Supervisory Choice Rule): Formulate the regulator's cost-benefit trade-off between fixed compliance "
            "reporting costs C_rep and active probing losses C_probe(Δη) ≍ κ σ² (Δη)^{-(4K-2)}. Prove the existence of the critical intermediate "
            "band [Δη_min, Δη_max] where mandatory disclosure is socially optimal, and explain why disclosure is unnecessary outside this band."
        ),
        "focus": (
            "The supervisory trade-off between fixed compliance costs C_rep and probing deadweight loss C_probe(Δη) ≍ κ σ² (Δη)^{-(4K-2)}, "
            "the analytical derivation of the critical intermediate band [Δη_min, Δη_max], and why mandatory disclosure is socially indispensable within this band."
        )
    },
    {
        "num": 24,
        "title": "Table 7: Primary Empirical Findings Across 8 CFTC Futures Markets",
        "q": (
            "Review the empirical methodology and results in Table 7 for the primary 8 CFTC futures markets (E-mini S&P, 10Y Treasuries, Crude Oil, "
            "Euro FX, Corn, etc.). How were trader category positions (Managed Money, Swap Dealers, Commercial Hedgers) mapped into model cohorts, and "
            "what was the magnitude of parameter uncertainty reduction achieved by public COT data compared to price inversion?"
        ),
        "focus": (
            "The mapping of CFTC Disaggregated Commitments of Traders (DCOT) categories (Managed Money, Swap Dealers, Commercial Hedgers) into structural "
            "model cohorts, and the empirical finding that public COT reports reduce parameter uncertainty intervals by 25x to 55x compared to price data "
            "alone across equity, bond, energy, and currency futures."
        )
    },
    {
        "num": 25,
        "title": "Table 8: The Pre-Registered 12-Market Replication Protocol (SHA-256)",
        "q": (
            "Detail the out-of-sample replication in Table 8 across 12 additional CFTC markets pre-registered under SHA-256 hash 591e71c9... "
            "(registered 31 October 2026). Summarize the empirical findings across gold, silver, copper, grains, softs, and FX: Why were position "
            "intervals 23x to 69x narrower under COT reporting, and what is the institutional meaning of the Data Equivalence Multiplier (up to 89,500 probes)?"
        ),
        "focus": (
            "The pre-registered protocol under SHA-256 hash 591e71c9... (registered 31 October 2026), the out-of-sample replication across 12 commodity "
            "and financial futures markets yielding 23.4x to 68.7x narrower uncertainty intervals, and the institutional interpretation of the Data "
            "Equivalence Multiplier (up to 89,500 active probes per weekly report)."
        )
    },
    {
        "num": 26,
        "title": "Table 9: The Full 22-Test Pre-Specified Scorecard Audit",
        "q": (
            "Examine the complete 22-test audited scorecard in Table 9. Detail the exact criteria for the 11 passing tests, the 10 failed tests, and "
            "the 1 unsupported test. Explain why the 10 failures concentrate in high-frequency crypto perpetuals, and discuss why pre-registering "
            "and reporting negative results establishes scientific integrity against publication bias."
        ),
        "focus": (
            "The audit of the 22 pre-specified econometric tests (11 passes, 10 failures, 1 unsupported), why failures concentrate in high-frequency "
            "crypto perpetuals under Diebold-Mariano tests, and how transparently reporting pre-registered negative results protects empirical research "
            "against publication bias."
        )
    },
    {
        "num": 27,
        "title": "Within-Class Sign Cancellation: The Fallacy of Coarse Reporting Buckets",
        "q": (
            "Explain the mathematical and institutional mechanism of **Within-Class Sign Cancellation**: When a regulator aggregates trend-following "
            "CTAs (momentum, w_CTA > 0, η_CTA ≈ 0.9) and cash-futures basis arbitrageurs (mean-reverting, w_Arb < 0, η_Arb ≈ 0.1) into a single "
            "'Leveraged Funds' bucket, prove mathematically why w_CTA y_CTA + w_Arb y_Arb ≈ 0, destroying aggregate predictive flow signals and "
            "proving the necessity of granular MiFID II RTS 24 algo_id tags."
        ),
        "focus": (
            "The destructive interference mechanism w_CTA y_CTA + w_Arb y_Arb ≈ 0 when trend-following CTAs (momentum, η ≈ 0.9) and cash-futures basis "
            "arbitrageurs (mean-reverting, η ≈ 0.1) are grouped into coarse public categories like 'Leveraged Funds', and why this proves the necessity "
            "of granular algo_id tags."
        )
    },
    {
        "num": 28,
        "title": "Theorem 6.1: The Spectral Blind Spot & Matrix Non-Normality",
        "q": (
            "Provide the complete mathematical proof of Theorem 6.1: Construct systems A_1 = diag(λ_1, λ_2) and A_2 = [λ_1, γ; 0, λ_2] sharing "
            "identical stable eigenvalues 0 < λ_2 < λ_1 < 1, identical one-step return variance, and identical stationary price variance under white noise. "
            "Prove that because A_2 is non-normal (A_2 A_2^T ≠ A_2^T A_2), its peak transient gain scales as sup_t ||A_2^t||_2 ≍ γ / (λ_1 - λ_2), "
            "growing without bound as coupling γ increases."
        ),
        "focus": (
            "The construction of systems A_1 = diag(λ_1, λ_2) and A_2 = [λ_1, γ; 0, λ_2] with identical closed-loop eigenvalues and stationary variance, "
            "how non-orthogonal eigenvectors permit transient matrix powers to scale as [A_2^t]_{1,2} = γ (λ_1^t - λ_2^t) / (λ_1 - λ_2), and why "
            "peak transient gain grows without bound as coupling γ → ∞."
        )
    },
    {
        "num": 29,
        "title": "Pseudospectra, the Kreiss Matrix Theorem, and Flash Crash Mechanics",
        "q": (
            "Define the ε-pseudospectrum σ_ε(A) and the Kreiss constant K(A) = sup_{|z|>1} (|z|-1) ||(zI - A)^{-1}||. State the Kreiss Matrix "
            "Theorem K(A) ≤ sup_t ||A^t||_2 ≤ e · n · K(A), and explain Figure 7: Why do traditional risk metrics like Value-at-Risk (VaR) and volatility "
            "fail to detect non-normal transient risk, allowing markets with identical half-lives to produce catastrophic 40x flash crash excursions?"
        ),
        "focus": (
            "The ε-pseudospectrum σ_ε(A) and Kreiss constant K(A), the Kreiss Matrix Theorem bounds K(A) ≤ sup_t ||A^t||_2 ≤ e · n · K(A), and why "
            "traditional Value-at-Risk and stationary volatility models are mathematically blind to non-normal transient amplification, failing to detect "
            "impending flash crashes (Figure 7)."
        )
    },
    {
        "num": 30,
        "title": "Appendix F & Proposition 5.6: Aggregate Warehousing vs. Targeted Algorithmic Halts",
        "q": (
            "Synthesize the fundamental policy duality in Paper 1: Reconstruct Theorem F.3 (Appendix F) showing an unlevered warehousing desk with "
            "stress budget B needs only scalar cumulative gain G = ∑_{t<H} h_t at rate O(N^{-1/2}) without cohort deconvolution. Contrast this with "
            "Proposition 5.6 / S23 (Targeted Algorithmic Halts): Why does selectively halting a rogue algorithmic cohort strictly require identifying "
            "individual parameters (w_k, η_k) at the severe (Δη)^{-(4K-2)} rate, proving targeted interventions require mandatory algo_id tags?"
        ),
        "focus": (
            "The fundamental policy duality: why an unlevered warehousing desk with a stress budget needs only the scalar cumulative gain G = ∑ h_t "
            "at rate O(N^{-1/2}) without cohort deconvolution, whereas targeted supervisory halts (Proposition 5.6) strictly require deconvolving "
            "individual parameters (w_k, η_k) at the severe (Δη)^{-(4K-2)} rate, proving targeted interventions require mandatory audit trail tags."
        )
    }
]

def build_questions_doc():
    doc = Document()
    
    # Page Margins
    for s in doc.sections:
        s.top_margin = Inches(1.0); s.bottom_margin = Inches(1.0)
        s.left_margin = Inches(1.0); s.right_margin = Inches(1.0)
        
        header = s.header; hp = header.paragraphs[0]; hp.alignment = WD_ALIGN_PARAGRAPH.RIGHT
        hrun = hp.add_run("Paper 1: Master Research Questions (30 Questions)")
        hrun.font.name = "Calibri"; hrun.font.size = Pt(8.5); hrun.font.color.rgb = RGBColor(120, 120, 120)
        
        footer = s.footer; fp = footer.paragraphs[0]; fp.alignment = WD_ALIGN_PARAGRAPH.CENTER
        frun = fp.add_run("What Prices Cannot Tell a Market Supervisor")
        frun.font.name = "Calibri"; frun.font.size = Pt(8.5); frun.font.color.rgb = RGBColor(120, 120, 120)

    # Document Header Title
    p_title = doc.add_paragraph()
    p_title.paragraph_format.space_before = Pt(12); p_title.paragraph_format.space_after = Pt(14)
    r_title = p_title.add_run("Paper 1: 30 Master Research Questions\nWhat Prices Cannot Tell a Market Supervisor")
    r_title.font.name = "Calibri"; r_title.font.size = Pt(18); r_title.font.bold = True; r_title.font.color.rgb = RGBColor(11, 37, 69)

    # The 30 Questions with Merged 'What to focus on:'
    for item in MASTER_30:
        p_q = doc.add_paragraph()
        p_q.paragraph_format.space_before = Pt(10); p_q.paragraph_format.space_after = Pt(2)
        p_q.paragraph_format.line_spacing = 1.15
        p_q.paragraph_format.keep_with_next = True
        
        r_num = p_q.add_run(f"Question {item['num']}: {item['title']}\n")
        r_num.font.name = "Calibri"; r_num.font.size = Pt(11); r_num.font.bold = True; r_num.font.color.rgb = RGBColor(11, 37, 69)
        
        r_text = p_q.add_run(item['q'])
        r_text.font.name = "Calibri"; r_text.font.size = Pt(10); r_text.font.color.rgb = RGBColor(29, 45, 68)
        
        p_f = doc.add_paragraph()
        p_f.paragraph_format.space_before = Pt(2); p_f.paragraph_format.space_after = Pt(8)
        p_f.paragraph_format.line_spacing = 1.15
        
        r_fh = p_f.add_run("What to focus on: ")
        r_fh.font.name = "Calibri"; r_fh.font.size = Pt(9.5); r_fh.font.bold = True; r_fh.font.color.rgb = RGBColor(0, 119, 182)
        
        r_ft = p_f.add_run(item['focus'])
        r_ft.font.name = "Calibri"; r_ft.font.size = Pt(9.5); r_ft.font.italic = True; r_ft.font.color.rgb = RGBColor(70, 70, 70)

    out_path = ROOT / "Paper1_Questions_Workbook.docx"
    doc.save(str(out_path))
    print(f"Saved Master Questions to: {out_path}")
    return out_path

def build_answers_doc():
    doc = Document()
    
    # Page Margins
    for s in doc.sections:
        s.top_margin = Inches(1.0); s.bottom_margin = Inches(1.0)
        s.left_margin = Inches(1.0); s.right_margin = Inches(1.0)
        
        header = s.header; hp = header.paragraphs[0]; hp.alignment = WD_ALIGN_PARAGRAPH.RIGHT
        hrun = hp.add_run("Paper 1: Master Reference Answers (30 Questions)")
        hrun.font.name = "Calibri"; hrun.font.size = Pt(8.5); hrun.font.color.rgb = RGBColor(120, 120, 120)
        
        footer = s.footer; fp = footer.paragraphs[0]; fp.alignment = WD_ALIGN_PARAGRAPH.CENTER
        frun = fp.add_run("What Prices Cannot Tell a Market Supervisor")
        frun.font.name = "Calibri"; frun.font.size = Pt(8.5); frun.font.color.rgb = RGBColor(120, 120, 120)

    # Document Header Title
    p_title = doc.add_paragraph()
    p_title.paragraph_format.space_before = Pt(12); p_title.paragraph_format.space_after = Pt(14)
    r_title = p_title.add_run("Paper 1: Reference Answers for 30 Questions\nWhat Prices Cannot Tell a Market Supervisor")
    r_title.font.name = "Calibri"; r_title.font.size = Pt(18); r_title.font.bold = True; r_title.font.color.rgb = RGBColor(11, 37, 69)

    # The 30 Questions + Focus + Answers
    for idx, item in enumerate(MASTER_30):
        from generate_pure_30_questions import ANSWERS_30_PURE
        ans_text = ANSWERS_30_PURE[idx]
        
        p_q = doc.add_paragraph()
        p_q.paragraph_format.space_before = Pt(12); p_q.paragraph_format.space_after = Pt(2)
        p_q.paragraph_format.keep_with_next = True
        
        r_num = p_q.add_run(f"Question {item['num']}: {item['title']}\n")
        r_num.font.name = "Calibri"; r_num.font.size = Pt(11); r_num.font.bold = True; r_num.font.color.rgb = RGBColor(11, 37, 69)
        
        r_q = p_q.add_run(item['q'])
        r_q.font.name = "Calibri"; r_q.font.size = Pt(10); r_q.font.color.rgb = RGBColor(19, 64, 116)
        
        p_f = doc.add_paragraph()
        p_f.paragraph_format.space_before = Pt(2); p_f.paragraph_format.space_after = Pt(4)
        p_f.paragraph_format.keep_with_next = True
        
        r_fh = p_f.add_run("What to focus on: ")
        r_fh.font.name = "Calibri"; r_fh.font.size = Pt(9.5); r_fh.font.bold = True; r_fh.font.color.rgb = RGBColor(0, 119, 182)
        
        r_ft = p_f.add_run(item['focus'])
        r_ft.font.name = "Calibri"; r_ft.font.size = Pt(9.5); r_ft.font.italic = True; r_ft.font.color.rgb = RGBColor(70, 70, 70)
        
        p_a = doc.add_paragraph()
        p_a.paragraph_format.space_before = Pt(2); p_a.paragraph_format.space_after = Pt(8)
        p_a.paragraph_format.line_spacing = 1.15
        
        r_a_hdr = p_a.add_run("Answer:\n")
        r_a_hdr.font.name = "Calibri"; r_a_hdr.font.size = Pt(10); r_a_hdr.font.bold = True; r_a_hdr.font.color.rgb = RGBColor(11, 37, 69)
        
        r_a = p_a.add_run(ans_text)
        r_a.font.name = "Calibri"; r_a.font.size = Pt(9.5); r_a.font.color.rgb = RGBColor(29, 45, 68)

    out_path = ROOT / "Paper1_Answers_Solution_Manual.docx"
    doc.save(str(out_path))
    print(f"Saved Master Answers to: {out_path}")
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
    print("Master build complete!")
