"""
Generate the 30 Deep, Detailed Questions and Model Answers for Paper 1.
- Exactly 30 deep, thorough questions covering every section, theorem, lemma, table, and appendix of Paper 1.
- No "who to focus" (both Sujan and Prashant read and do the full work).
- No empty gaps or fill-in boxes.
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

# 30 Deep, Detailed Questions covering every aspect of Paper 1
QUESTIONS_30 = [
    {
        "num": 1,
        "title": "State-Space Model & Closed-Loop Transfer Function Derivation",
        "section": "Section 2: Model and Motivating Examples (pages 5–8), Appendix A",
        "key_objects": "Equations (1)–(8), State vector x_t, Demand u_t, Impact κ, Inventory damping q, Transfer functions H(z) and G(z)",
        "q": (
            "In Section 2, the limit order book is populated by K trader cohorts with memory filters x_{k,t} = η_k x_{k,t-1} + (1 - η_k) p_{t-1}, "
            "weights w_k > 0 (∑ w_k = 1), Kyle depth impact κ > 0, and dealer inventory damping q > 0. "
            "Derive the exact discrete-time state-space realization (A, B, C, D) of the coupled system, show how closing the price loop yields "
            "the closed-loop transfer function G(z) = κ H(z) / (1 + κ q H(z)) where H(z) = ∑ w_k / (1 - η_k z^{-1}), and explain the algebraic "
            "mechanism by which the feedback denominator alters the system eigenvalues."
        )
    },
    {
        "num": 2,
        "title": "Open-Loop Transmission Zeros vs. Closed-Loop Return Poles",
        "section": "Section 2: Lemma 2.1 & Lemma 2.2 (pages 8–10), Appendix B",
        "key_objects": "Numerator N(z), Denominator D(z), Closed-loop characteristic polynomial D_{cl}(z), Interlacing roots",
        "q": (
            "Prove Lemma 2.1 and Lemma 2.2 regarding the degrees and root structures of N(z), D(z), and D_{cl}(z) = D(z) + κ q N(z). "
            "Why do the individual trader memory parameters η_k enter as roots of D(z) and transmission zeros of the price return response, "
            "rather than uncoupled observable poles? Explain why the roots of D_{cl}(z) interlace with {η_k} on the real interval [0, 1), and "
            "what this interlacing implies for closed-loop stability."
        )
    },
    {
        "num": 3,
        "title": "The Econometric Under-Determination of Price Time-Series",
        "section": "Section 2: Identification Limits (pages 10–12), Appendix B",
        "key_objects": "ARMA(K, K-1) representation, Observable price pole matching, Parameter manifold",
        "q": (
            "Explain mathematically why standard econometric time-series estimation (such as ARMA or ARIMA modeling) on equilibrium price returns "
            "Δp_t fails to identify the underlying trader parameters. Specifically, show that matching the K observable roots of the closed-loop "
            "characteristic polynomial D_{cl}(z) yields only K scalar equations for 2K + 1 structural unknowns (w, η, κ, q), proving the existence "
            "of an unidentifiable (K+1)-dimensional manifold of observationally equivalent market configurations."
        )
    },
    {
        "num": 4,
        "title": "Theorem 2.1: Merged Measure Invariance and Moment Equivalence",
        "section": "Section 2: Theorem 2.1 (pages 11–12), Appendix B",
        "key_objects": "Theorem 2.1, Radon probability measures μ_0 and μ_1, Markov moments h_t, 2K+1 equality",
        "q": (
            "Provide the complete proof of Theorem 2.1 (Merged Measure Invariance). Show that two distinct trader populations represented by Radon "
            "measures μ_0 and μ_1 produce identical noise-free equilibrium price paths under all exogenous inputs if and only if their rational "
            "transfer functions H_{μ_0}(z) and H_{μ_1}(z) coincide. Prove why this equality holds if and only if their impulse response moments "
            "agree for the first 2K + 1 periods (t = 0, 1, ..., 2K), and explain why this permits two slow institutional desks to perfectly mimic five fast HFTs."
        )
    },
    {
        "num": 5,
        "title": "Remark 2.2: The Two-Root Stock-Flow Inventory Bridge",
        "section": "Section 2: Remark 2.2 (page 12), Supplement S6",
        "key_objects": "Remark 2.2, Order flow demand u_t, Weekly COT stocks S_t, Quadratic characteristic equation",
        "q": (
            "Reconstruct Remark 2.2 and Supplement S6: How does the paper formally bridge high-frequency trader flow demand u_t to weekly reported "
            "Commitments of Traders (COT) position stocks S_t? Derive the quadratic recurrence connecting net weekly position changes ΔS_t to flow "
            "demand, show why inverting this relationship requires solving a quadratic characteristic equation, and prove that dynamic stability "
            "uniquely selects the smaller root (|λ| < 1) while rejecting the explosive root."
        )
    },
    {
        "num": 6,
        "title": "Corollary 2.3: Plug-In Estimation Stability of Market Parameters",
        "section": "Section 2: Corollary 2.3 (page 12), Supplement S7",
        "key_objects": "Corollary 2.3, Plug-in estimators (a^, κ^, p^*), Parametric rate √T, Prony stability preservation",
        "q": (
            "Analyze Corollary 2.3 and Supplement S7: In practical market deconvolution, the structural parameters (persistence a, Kyle's depth κ, "
            "and fundamental value p*) must be estimated via plug-in estimators (a^, κ^, p^*). Prove that when these parameters are estimated at the "
            "standard parametric rate O_p(T^{-1/2}), the condition number and asymptotic rate of Prony-Hankel deconvolution are preserved without "
            "rate degradation."
        )
    },
    {
        "num": 7,
        "title": "Theorem 3.1: Le Cam Two-Point Construction & Moment-Matched Perturbation",
        "section": "Section 3.1: Theorem 3.1 (pages 13–16), Appendix B",
        "key_objects": "Theorem 3.1, Le Cam's two-point lemma, Signed perturbation measure dΔ(η), Order 2K-1 moment matching",
        "q": (
            "Reconstruct the foundation of Theorem 3.1: How are the two candidate Radon measures μ_0 and μ_1 constructed over K cohorts with minimum "
            "memory spacing Δη = min_{j ≠ k} |η_j - η_k|? Detail the mathematical construction of the signed perturbation measure dΔ(η) using "
            "Chebyshev-type polynomial weighting, and prove that matching the first 2K - 1 algebraic moments forces the leading 2K - 1 impulse response "
            "difference taps to vanish identically: Δh_t = 0 for t = 0, 1, ..., 2K - 1."
        )
    },
    {
        "num": 8,
        "title": "Kullback-Leibler Divergence Taylor Remainder and Total Variation Bound",
        "section": "Section 3.1: Proof of Theorem 3.1 (pages 16–18), Appendix B",
        "key_objects": "Gaussian product measures, D_KL expansion, Leading non-vanishing term, Pinsker's inequality",
        "q": (
            "In the proof of Theorem 3.1, show how the Kullback-Leibler divergence between product measures P_0^{\\otimes N} and P_1^{\\otimes N} under "
            "Gaussian noise variance σ² expands as D_KL = (N / 2σ²) ∑_{t=2K}^∞ (Δh_t)². Prove that this summation collapses to order "
            "O(N σ^{-2} (Δη)^{4K-2}), and apply Pinsker's inequality to establish the total variation distance bound "
            "||P_0^{\\otimes N} - P_1^{\\otimes N}||_TV ≤ √(C_K N / 4σ²) (Δη)^{2K-1}."
        )
    },
    {
        "num": 9,
        "title": "Deduction of the Ω(σ²(Δη)^{-(4K-2)}) Minimax Lower Bound for General α",
        "section": "Section 3.1: Theorem 3.1 (pages 17–18), Appendix B",
        "key_objects": "General testing level α ∈ (0, 1/2), Minimax risk lower bound, Sample size N*",
        "q": (
            "Complete the proof of Theorem 3.1 for an arbitrary testing error level α ∈ (0, 1/2). Using Le Cam's testing inequality "
            "inf_ψ max(P_0(ψ ≠ 0), P_1(ψ ≠ 1)) ≥ 1/2 - (1/2) ||P_0^{\\otimes N} - P_1^{\\otimes N}||_TV, derive the exact lower bound "
            "N* ≥ (4(1 - 2α)² / C_K) σ² (Δη)^{-(4K-2)} = Ω(σ² (Δη)^{-(4K-2)}). Explain why this bound applies uniformly to all estimators "
            "(biased or unbiased, linear or non-linear)."
        )
    },
    {
        "num": 10,
        "title": "The Cohort Exponent Scaling Law: (Δη)^{-6} vs. (Δη)^{-10}",
        "section": "Section 3.1: Discussion and Table 2 (pages 18–19)",
        "key_objects": "Exponent 4K - 2, K = 2 scaling (Δη)^{-6}, K = 3 scaling (Δη)^{-10}, Numerical sensitivity",
        "q": (
            "Analyze the economic and computational consequences of the scaling exponent 4K - 2. Calculate the exact sample size explosion when "
            "two trading algorithms narrow their memory spacing from Δη = 0.10 to Δη = 0.01 for K = 2 cohorts (a factor of 10^6) versus K = 3 cohorts "
            "(a factor of 10^{10}). What does this exponent imply about the feasibility of deconvolving high-frequency trading algorithms operating "
            "at millisecond time scales?"
        )
    },
    {
        "num": 11,
        "title": "Algorithm 1: Prony-Hankel Deconvolution Architecture",
        "section": "Section 3.2: Algorithm 1 (pages 19–21), Appendix B",
        "key_objects": "Algorithm 1, Hankel matrix H_K, Annihilating polynomial P(z), Vandermonde weight recovery",
        "q": (
            "Detail the algorithmic architecture of Algorithm 1 (Prony-Hankel Deconvolution). Starting from estimated impulse response taps h^_t, "
            "show how the (2K × 2K) Hankel matrix H_K is formed, how solving H_K c = -h_{2K} determines the annihilating polynomial coefficients, "
            "how rooting P(z) yields the memory rates η^_k, and how the portfolio weights w^_k are recovered via linear Vandermonde inversion."
        )
    },
    {
        "num": 12,
        "title": "Proposition 3.3: Hankel Singular Value Lower Bound via Chebyshev Moments",
        "section": "Section 3.2: Proposition 3.3 (pages 21–23), Appendix B",
        "key_objects": "Proposition 3.3, Smallest singular value σ_{2K}(H_K), Chebyshev extremal polynomials, Node spacing Δη",
        "q": (
            "Reconstruct the proof of Proposition 3.3: Prove that the smallest singular value of the Hankel matrix satisfies "
            "σ_{2K}(H_K) ≥ c_K (Δη)^{2K-1}. How does the proof construct a dual variational problem using Chebyshev extremal polynomials on the "
            "discrete node set {η_1, ..., η_K}, and why does this establish that the Hankel condition number κ(H_K) scales precisely as (Δη)^{-(2K-1)}?"
        )
    },
    {
        "num": 13,
        "title": "Theorem 3.2: Matching Minimax Upper Bound & Noise Perturbation Propagation",
        "section": "Section 3.2: Theorem 3.2 (pages 23–24), Appendix B",
        "key_objects": "Theorem 3.2, Wedin sin Θ theorem, Wilkinson root perturbation, Upper rate O(σ²(Δη)^{-(4K-2)})",
        "q": (
            "Prove Theorem 3.2: When estimated taps are corrupted by Gaussian noise with variance σ²/N, show how the Hankel perturbation "
            "||δH_K||_2 ≤ O(σ N^{-1/2}) propagates into the coefficient vector as ||δc||_2 ≤ O(σ N^{-1/2} (Δη)^{-(2K-1)}). Show that root inversion "
            "adds a factor of (Δη)^{-1}, yielding root error |η^_k - η_k| ≤ O(σ N^{-1/2} (Δη)^{-2K}) and establishing sample complexity "
            "O(σ² δ^{-2} (Δη)^{-(4K-2)}), matching Theorem 3.1."
        )
    },
    {
        "num": 14,
        "title": "Subspace Estimator Invariance: ESPRIT and Matrix Pencil Conditioning",
        "section": "Section 3.2: Subspace Comparison (pages 24–25), Appendix B",
        "key_objects": "ESPRIT, Matrix Pencil, Shifted Hankel matrices, Oblique projector condition number κ(V)",
        "q": (
            "Explain why alternative subspace identification methods (such as ESPRIT or Matrix Pencil) cannot overcome the (Δη)^{-(4K-2)} barrier. "
            "Show that because ESPRIT projects onto the range of the Vandermonde matrix V_K, its oblique subspace projector has condition number "
            "κ(V_K) ≍ (Δη)^{-(2K-1)}, proving that all linear deconvolution methods suffer from the exact same fundamental conditioning ceiling."
        )
    },
    {
        "num": 15,
        "title": "Lemma 4.2: Positive Definite Toeplitz Cost Matrix and 'No Sure Gain'",
        "section": "Section 4: Account-Level Capital (pages 25–27), Appendix B",
        "key_objects": "Lemma 4.2, Probing sequence u_t, Toeplitz matrix T_G, Positive definiteness, No Sure Gain",
        "q": (
            "Prove Lemma 4.2: For any physically realizable, decaying price impact impulse response G(t) ≥ 0, show that the Toeplitz execution "
            "cost matrix T_G with entries [T_G]_{i,j} = G(|i - j|) is strictly positive definite: u^T T_G u > 0 for all u ≠ 0. Explain the economic "
            "meaning of the 'No Sure Gain' principle: why can exploratory market probing never be self-financing?"
        )
    },
    {
        "num": 16,
        "title": "Theorem 4.1: The Cumulative Probing Order Volume Lower Bound",
        "section": "Section 4: Theorem 4.1 (pages 27–28), Appendix B",
        "key_objects": "Theorem 4.1, Fisher information of probe sequence, L² energy ||u||_2², Bound Ω(σ² κ^{-2} δ^{-2} (Δη)^{-(4K-2)})",
        "q": (
            "Reconstruct the proof of Theorem 4.1: Show that to achieve parameter identification accuracy δ under Kyle's price impact κ, the supervisor's "
            "total cumulative probe order energy must satisfy ||u||_2² = ∑_{t=1}^T u_t² = Ω(σ² κ^{-2} δ^{-2} (Δη)^{-(4K-2)}). How does the Fisher "
            "information matrix of the active probe sequence bound the required order volume from below?"
        )
    },
    {
        "num": 17,
        "title": "Theorem 4.3: Account-Level Margin Solvency and the Ω(δ^{-4}) Capital Barrier",
        "section": "Section 4: Theorem 4.3 (pages 28–30), Appendix C",
        "key_objects": "Theorem 4.3, Margin budget B, Peak inventory ||x||_∞ ≍ δ^{-1}, Mark-to-market drawdown, Bound Ω(δ^{-4})",
        "q": (
            "Prove Theorem 4.3: To avoid detection, an active probe sequence must oscillate, generating peak cumulative inventory excursions of "
            "order ||x||_∞ ≍ δ^{-1}. Prove that the peak adverse mark-to-market drawdown scales as sup_t |x_t Δp_t| ≍ Ω(σ² δ^{-4} (Δη)^{-(4K-2)}). "
            "Why does exchange margin solvency force the supervisor's cash capital reserve B to scale as Ω(δ^{-4}), and why does doubling precision "
            "multiply required capital by 16?"
        )
    },
    {
        "num": 18,
        "title": "Table 4 Calibration: 'Disclosure in Dollars' in Treasury & S&P Futures",
        "section": "Section 4: Table 4 (page 30)",
        "key_objects": "Table 4, 10-Year Treasury (ZN), E-mini S&P (ES), Kyle's depth κ, Annual cost $15M to $356M",
        "q": (
            "Examine the institutional calibration in Table 4 ('Disclosure in Dollars'). Using calibrated parameters for US 10-Year Treasury futures "
            "(ZN) and E-mini S&P 500 futures (ES), explain why re-estimating two algorithmic cohorts separated by Δη = 0.05 on a weekly basis requires "
            "$15.4M to $356.2M in annual deadweight execution loss per market. Why does this make active regulatory probing institutional suicide?"
        )
    },
    {
        "num": 19,
        "title": "Theorem 5.8: Passive Whittle Spectral Divergence Asymptotic Rate Collapse",
        "section": "Section 4.4 & Section 5.8: Theorem 5.8 (pages 31–33, 65–70), Appendix B",
        "key_objects": "Theorem 5.8, Return spectral density f_θ(λ), Whittle log-likelihood, L² relative divergence rate O((Δη)^{4K-2})",
        "q": (
            "Reconstruct the proof of Theorem 5.8: For stationary Gaussian price returns Δp_t with spectral density f_θ(λ), formulate the Whittle "
            "log-likelihood and write the asymptotic KL divergence rate integral over [-π, π]. Prove that moment matching forces "
            "f_0(λ) / f_1(λ) = 1 + O((Δη)^{2K-1}) uniformly, causing the divergence rate to collapse to O((Δη)^{4K-2}) and proving that passive "
            "tick data collection costs time at the exact same polynomial rate probing costs capital."
        )
    },
    {
        "num": 20,
        "title": "Section 4.5 & Table 6: Exact Multinomial Resampling with Real Bitcoin Shocks",
        "section": "Section 4.5: Real Noise Injection (pages 34–38), Table 6, Figure 5",
        "key_objects": "Table 6, Real 1-minute Bitcoin return shocks, Pareto heavy tails, Kurtosis > 12.4, Fitted slopes -6.01 and -9.81",
        "q": (
            "Detail the empirical methodology of Section 4.5 and Table 6: How was exact multinomial resampling conducted using real 1-minute Bitcoin "
            "perpetual return shocks without normal approximations? Why did empirical excess kurtosis (> 12.4) and heavy tails preserve the exact "
            "theoretical log-log slope exponents of -6.01 for K = 2 and -9.81 for K = 3 in Figure 5?"
        )
    },
    {
        "num": 21,
        "title": "Theorem 5.7: Completely Monotone Memory and Minimax Logarithmic Collapse",
        "section": "Section 5.7: Continuous Memory (pages 60–64), Appendix C, Theorem 5.7",
        "key_objects": "Theorem 5.7, Bernstein's Theorem, Completely monotone kernels, Hausdorff moment problem, Rate 1/log(N/σ²)",
        "q": (
            "Prove Theorem 5.7: When the trader population has a continuous memory distribution governed by a completely monotone kernel "
            "k(t) = ∫_0^1 η^t dF(η) (K = ∞), show how the Hausdorff moment sequence maps to a compact Fredholm integral operator with exponential "
            "singular value decay σ_m ≍ exp(-c m). Apply Donoho's functional estimation theorem to prove that minimax estimation error collapses "
            "from polynomial to logarithmic w = Θ(1 / log(N / σ²)), requiring exponential data N ≥ exp(C / w)."
        )
    },
    {
        "num": 22,
        "title": "Theorem 5.1: Class-Tagged Disclosure and Decoupled Single-Pole Regressions",
        "section": "Section 5.1–5.3: What Disclosure Buys (pages 39–43), Appendix C, Theorem 5.1",
        "key_objects": "Theorem 5.1, Class-tagged order flow vector y_t, Decoupled estimation, Rate Θ(σ²(Δη)^{-2}), Weight rate O(1)",
        "q": (
            "Provide the complete proof of Theorem 5.1: Show how observing class-tagged order flows y_{k,t} (e.g. MiFID II RTS 24 algo_id tags) "
            "decouples the coupled feedback loop into K independent single-variable autoregressions. Prove that the sample complexity to estimate "
            "memory rates collapses from Θ(σ² (Δη)^{-(4K-2)}) to Θ(σ² (Δη)^{-2}), and prove that estimating portfolio weights w_k becomes O(1) "
            "completely independent of memory spacing Δη."
        )
    },
    {
        "num": 23,
        "title": "Proposition 5.5: The Supervisory Choice Rule & Critical Information Band",
        "section": "Section 5.5: When Disclosure is Worth Acquiring (pages 44–46), Proposition 5.5",
        "key_objects": "Proposition 5.5, Reporting cost C_rep, Probing deadweight loss C_probe(Δη), Critical band [Δη_min, Δη_max]",
        "q": (
            "Analyze Proposition 5.5 (The Supervisory Choice Rule): Formulate the regulator's cost-benefit trade-off between fixed compliance "
            "reporting costs C_rep and active probing losses C_probe(Δη) ≍ κ σ² (Δη)^{-(4K-2)}. Prove the existence of the critical intermediate "
            "band [Δη_min, Δη_max] where mandatory disclosure is socially optimal, and explain why disclosure is unnecessary outside this band."
        )
    },
    {
        "num": 24,
        "title": "Table 7: Primary Empirical Findings Across 8 CFTC Futures Markets",
        "section": "Section 5.4: Mandated Reporting (pages 47–49), Table 7",
        "key_objects": "Table 7, Primary 8 CFTC markets, Disaggregated COT reports, Managed Money vs. Swap Dealers, Uncertainty intervals",
        "q": (
            "Review the empirical methodology and results in Table 7 for the primary 8 CFTC futures markets (E-mini S&P, 10Y Treasuries, Crude Oil, "
            "Euro FX, etc.). How were trader category positions (Managed Money, Swap Dealers, Commercial Hedgers) mapped into model cohorts, and "
            "what was the magnitude of parameter uncertainty reduction achieved by public COT data compared to price inversion?"
        )
    },
    {
        "num": 25,
        "title": "Table 8: The Pre-Registered 12-Market Replication Protocol (SHA-256)",
        "section": "Section 5.4: Out-of-Sample Replication (pages 49–51), Table 8",
        "key_objects": "Table 8, Pre-registration hash 591e71c9... (31 Oct 2026), 12 replication markets, 23x to 69x narrowing, Data Equivalence Multiplier",
        "q": (
            "Detail the out-of-sample replication in Table 8 across 12 additional CFTC markets pre-registered under SHA-256 hash 591e71c9... "
            "(registered 31 October 2026). Summarize the empirical findings across gold, silver, copper, grains, softs, and FX: Why were position "
            "intervals 23x to 69x narrower under COT reporting, and what is the institutional meaning of the Data Equivalence Multiplier (up to 89,500 probes)?"
        )
    },
    {
        "num": 26,
        "title": "Table 9: The Full 22-Test Pre-Specified Scorecard Audit",
        "section": "Section 5.5–5.6: Scorecard Audit (pages 51–54), Table 9, Table S7",
        "key_objects": "Table 9, 22-test scorecard (11 passed, 10 failed, 1 unsupported), Binance perpetuals tests, Clark-West tests",
        "q": (
            "Examine the complete 22-test audited scorecard in Table 9. Detail the exact criteria for the 11 passing tests, the 10 failed tests, and "
            "the 1 unsupported test. Explain why the 10 failures concentrate in high-frequency crypto perpetuals, and discuss why pre-registering "
            "and reporting negative results establishes scientific integrity against publication bias."
        )
    },
    {
        "num": 27,
        "title": "Within-Class Sign Cancellation: The Fallacy of Coarse Reporting Buckets",
        "section": "Section 5.6: Within-Class Sign Cancellation (pages 53–54), Supplement S8",
        "key_objects": "Hypotheses N2 & N3, Diebold-Mariano failures (29/30 & 25/30), Trend-following CTAs vs. Basis Arbitrageurs, Destructive interference",
        "q": (
            "Explain the mathematical and institutional mechanism of **Within-Class Sign Cancellation**: When a regulator aggregates trend-following "
            "CTAs (momentum, w_CTA > 0, η_CTA ≈ 0.9) and cash-futures basis arbitrageurs (mean-reverting, w_Arb < 0, η_Arb ≈ 0.1) into a single "
            "'Leveraged Funds' bucket, prove mathematically why w_CTA y_CTA + w_Arb y_Arb ≈ 0, destroying aggregate predictive flow signals and "
            "proving the necessity of granular MiFID II RTS 24 algo_id tags."
        )
    },
    {
        "num": 28,
        "title": "Theorem 6.1: The Spectral Blind Spot & Matrix Non-Normality",
        "section": "Section 6: A Spectral Blind Spot (pages 55–58), Appendix B, Theorem 6.1",
        "key_objects": "Theorem 6.1, Normal system A_1, Non-normal system A_2, Off-diagonal coupling γ, Matched eigenvalues and stationary variance",
        "q": (
            "Provide the complete mathematical proof of Theorem 6.1: Construct systems A_1 = diag(λ_1, λ_2) and A_2 = [λ_1, γ; 0, λ_2] sharing "
            "identical stable eigenvalues 0 < λ_2 < λ_1 < 1, identical one-step return variance, and identical stationary price variance under white noise. "
            "Prove that because A_2 is non-normal (A_2 A_2^T ≠ A_2^T A_2), its peak transient gain scales as sup_t ||A_2^t||_2 ≍ γ / (λ_1 - λ_2), "
            "growing without bound as coupling γ increases."
        )
    },
    {
        "num": 29,
        "title": "Pseudospectra, the Kreiss Matrix Theorem, and Flash Crash Mechanics",
        "section": "Section 6: Pseudospectra (pages 58–59), Figure 7, Kreiss Matrix Theorem",
        "key_objects": "Pseudospectrum σ_ε(A), Kreiss constant K(A), Resolvent norm ||(zI - A)^{-1}||, Flash crash transient amplification",
        "q": (
            "Define the ε-pseudospectrum σ_ε(A) and the Kreiss constant K(A) = sup_{|z|>1} (|z|-1) ||(zI - A)^{-1}||. State the Kreiss Matrix "
            "Theorem K(A) ≤ sup_t ||A^t||_2 ≤ e · n · K(A), and explain Figure 7: Why do traditional risk metrics like Value-at-Risk (VaR) and volatility "
            "fail to detect non-normal transient risk, allowing markets with identical half-lives to produce catastrophic 40x flash crash excursions?"
        )
    },
    {
        "num": 30,
        "title": "Appendix F & Proposition 5.6: Aggregate Warehousing vs. Targeted Algorithmic Halts",
        "section": "Section 7 (pages 65–72), Proposition 5.6, Appendix F (paper1_finite_horizon_supplement.pdf)",
        "key_objects": "Theorem F.3, Unlevered warehousing desk, Stress budget B, Scalar cumulative gain G = ∑ h_t, Proposition 5.6 targeted halts",
        "q": (
            "Synthesize the fundamental policy duality in Paper 1: Reconstruct Theorem F.3 (Appendix F) showing an unlevered warehousing desk with "
            "stress budget B needs only scalar cumulative gain G = ∑_{t<H} h_t at rate O(N^{-1/2}) without cohort deconvolution. Contrast this with "
            "Proposition 5.6 / S23 (Targeted Algorithmic Halts): Why does selectively halting a rogue algorithmic cohort strictly require identifying "
            "individual parameters (w_k, η_k) at the severe (Δη)^{-(4K-2)} rate, proving targeted interventions require mandatory algo_id tags?"
        )
    }
]

# 30 Comprehensive Model Answers matching the 30 questions
ANSWERS_30 = [
    # A1
    (
        "1. State-Space Realization & Closed-Loop Transfer Function:\n"
        "Let x_t = [x_{1,t}, ..., x_{K,t}]^T be the vector of trader cohort expectation states, and p~_t = p_t - p* be price deviation. "
        "The state evolution is x_{t+1} = A x_t + B p~_t, where A = diag(η_1, ..., η_K) and B = [1 - η_1, ..., 1 - η_K]^T. "
        "Aggregate trader flow demand is u_t = ∑_{k=1}^K w_k (p* - x_{k,t}) = -w^T x_t, where w = [w_1, ..., w_K]^T with ∑ w_k = 1. "
        "Market clearing with Kyle's lambda impact κ > 0 and dealer inventory damping q > 0 gives p_t = p_{t-1} + κ u_t - κ q p~_{t-1}. "
        "In deviations, p~_t = (1 - κ q) p~_{t-1} - κ w^T x_t. Closing the feedback loop yields the autonomous system matrix "
        "A_{cl} = A - κ B w^T (I + κ q w^T B)^{-1}. Taking Z-transforms, open-loop demand is H(z) = ∑_{k=1}^K w_k / (1 - η_k z^{-1}) = N(z) / D(z), "
        "where D(z) = ∏_{k=1}^K (1 - η_k z^{-1}) and N(z) = ∑_{k=1}^K w_k ∏_{j ≠ k} (1 - η_j z^{-1}). "
        "Embedding H(z) in the price formation equation gives the closed-loop transfer function mapping exogenous flow shocks to equilibrium returns: "
        "G(z) = κ H(z) / (1 + κ q H(z)) = κ N(z) / [D(z) + κ q N(z)]. Closed-loop feedback shifts the open-loop poles {η_k} into the roots of D_{cl}(z)."
    ),
    # A2
    (
        "2. Polynomial Degrees and Interlacing of Transmission Zeros:\n"
        "In Lemma 2.1 and Lemma 2.2, D(z) has degree K with roots at {η_1, ..., η_K}, and N(z) has degree K - 1. Because weights w_k > 0 sum to 1, "
        "N(z) is a convex combination of degree K - 1 polynomials. By the classical Gauss-Lucas theorem and Markov interlacing properties, "
        "the K - 1 roots of N(z), denoted {z_1, ..., z_{K-1}}, strictly interlace with {η_k} on the real interval (0, 1): "
        "η_1 < z_1 < η_2 < z_2 < ... < z_{K-1} < η_K. In the return transfer function G(z) = κ N(z) / D_{cl}(z), the roots of N(z) are transmission zeros. "
        "The observable poles of price returns are the roots of D_{cl}(z) = D(z) + κ q N(z). Because κ q > 0 and N(z) interlaces with D(z), "
        "the roots of D_{cl}(z), denoted {λ_1, ..., λ_K}, also strictly interlace with {η_k} on [0, 1). This interlacing guarantees that all closed-loop "
        "poles remain real and strictly inside the unit circle |λ_i| < 1, ensuring asymptotic stability while completely masking the open-loop poles {η_k}."
    ),
    # A3
    (
        "3. Econometric Under-Determination of Price Time-Series:\n"
        "An econometrician observing transaction price changes Δp_t fits an ARMA(K, K-1) or ARIMA model. The estimated autoregressive polynomial "
        "recovers the K roots {λ_1, ..., λ_K} of the closed-loop denominator D_{cl}(z) = D(z) + κ q N(z). This provides exactly K scalar equations: "
        "e_m(λ_1, ..., λ_K) = e_m(roots(D + κ q N)) for m = 1, ..., K, where e_m is the m-th elementary symmetric polynomial. "
        "However, the underlying market model contains 2K + 1 structural parameters: K memory persistence rates {η_1, ..., η_K}, K - 1 independent "
        "portfolio weights {w_1, ..., w_{K-1}}, Kyle's lambda impact κ, and dealer inventory damping q. Because 2K + 1 > K for all K ≥ 1, "
        "the mapping from observable closed-loop return poles to open-loop trader parameters is severely under-determined. The fibers of this mapping "
        "form a smooth, connected (K+1)-dimensional manifold of parameter configurations (w, η, κ, q) that produce mathematically identical return processes."
    ),
    # A4
    (
        "4. Proof of Theorem 2.1 (Merged Measure Invariance):\n"
        "Let μ_0 and μ_1 be two Radon probability measures on [0, 1) representing two trader populations. Noise-free price paths coincide under all "
        "exogenous input sequences if and only if their closed-loop transfer functions coincide: G_{μ_0}(z) = G_{μ_1}(z). Since G(z) is a strictly "
        "monotonic fractional linear transformation G = κ H / (1 + κ q H), G_{μ_0} = G_{μ_1} if and only if H_{μ_0}(z) = H_{μ_1}(z) identically in z. "
        "Each H_μ(z) is a rational function with numerator degree at most K - 1 and denominator degree at most K, so H_{μ_0}(z) - H_{μ_1}(z) = "
        "P(z) / (D_0(z) D_1(z)) where P(z) is a polynomial of degree at most 2K - 1. A rational function of degree 2K vanishes identically if and only "
        "if its first 2K + 1 Markov impulse response moments h_t = ∫_0^1 η^t dμ(η) agree for t = 0, 1, ..., 2K. "
        "Thus, two economies produce identical price paths if and only if their first 2K + 1 moments match, proving that prices cannot distinguish "
        "between 2 slow institutional trend-followers and 5 high-frequency market-makers."
    ),
    # A5
    (
        "5. Reconstructing Remark 2.2: The Two-Root Stock-Flow Inventory Bridge:\n"
        "High-frequency market microstructure models operate on order flow demand u_t, whereas regulatory disclosures (CFTC DCOT reports) publish "
        "weekly position stocks S_t. Stock S_t is the cumulative sum of past flows damped by inventory depreciation: S_t = (1 - δ_s) S_{t-1} + u_t^W + ξ_t, "
        "where u_t^W = ∑_{j=0}^{W-1} u_{t-j} is weekly aggregated flow and δ_s ∈ (0, 1) is weekly position decay. "
        "Substituting the state expectation dynamics into stock accumulation yields a second-order linear recurrence in position stock: "
        "S_{t+1} - (1 + a_s - κ_s) S_t + a_s S_{t-1} = ε_t^S. Inverting this relation to recover trader flow parameters requires finding the roots "
        "of the characteristic polynomial P(λ) = λ² - (1 + a_s - κ_s) λ + a_s = 0. The discriminant is strictly positive, yielding two real roots: "
        "λ_{1,2} = [(1 + a_s - κ_s) ± √((1 + a_s - κ_s)² - 4 a_s)] / 2. Dynamic stability strictly requires |λ| < 1. The larger root violates stability "
        "(λ_1 > 1, producing explosive non-stationary inventories), uniquely selecting the smaller root λ_2 < 1 and establishing algebraic consistency."
    ),
    # A6
    (
        "6. Corollary 2.3: Plug-In Estimation Stability:\n"
        "In practice, the structural baseline parameters θ_0 = (a, κ, p*) are estimated from high-frequency price data using standard estimators "
        "yielding θ^_T = θ_0 + O_p(T^{-1/2}). Corollary 2.3 proves that the deconvolution of trader memory parameters {η_k} is asymptotically stable "
        "under this plug-in estimation. Let H^_K(θ^_T) be the Hankel matrix formed using estimated baseline parameters. The perturbation satisfies "
        "||H^_K(θ^_T) - H_K(θ_0)||_2 ≤ ||H^_K(θ^_T) - H^_K(θ_0)||_2 + ||H^_K(θ_0) - H_K(θ_0)||_2 ≤ C_θ ||θ^_T - θ_0||_2 + O_p(σ N^{-1/2}) = "
        "O_p(T^{-1/2}) + O_p(σ N^{-1/2}). Because baseline parameters converge at the fast parametric rate T^{-1/2}, their estimation error is "
        "dominated by the ill-conditioned Hankel singular value decay σ_{2K}(H_K) ≍ (Δη)^{2K-1}. Consequently, plug-in estimation preserves "
        "the exact minimax deconvolution rate O(σ² (Δη)^{-(4K-2)}) without rate penalty."
    ),
    # A7
    (
        "7. Theorem 3.1: Le Cam Two-Point Construction & Moment Matching:\n"
        "Let the base trader population μ_0 have K cohorts with memory rates η_1 < ... < η_K separated by minimum spacing Δη. "
        "We construct the perturbed economy μ_1 by setting dμ_1(η) = dμ_0(η) + dΔ(η), where dΔ(η) is a signed Radon measure supported on "
        "[η_1 - Δη/2, η_K + Δη/2]. By the classical theory of Chebyshev moment spaces on compact intervals, there exists a non-zero signed measure Δ "
        "whose first 2K - 1 algebraic moments vanish identically: ∫_0^1 η^m dΔ(η) = 0 for all m = 0, 1, ..., 2K - 1, while its (2K)-th moment is non-zero: "
        "∫_0^1 η^{2K} dΔ(η) = c_K (Δη)^{2K}. The price impulse response difference between the two economies is Δh_t = ∫_0^1 η^t dΔ(η). "
        "Because Δ matches moments up to order 2K - 1, Δh_t = 0 identically for all lags t = 0, 1, ..., 2K - 1. The first diverging lag is t = 2K, "
        "where |Δh_{2K}| = c_K (Δη)^{2K-1}."
    ),
    # A8
    (
        "8. Kullback-Leibler Divergence Expansion & Total Variation Bound:\n"
        "Under N independent reset experiments with Gaussian observation noise of variance σ², the log-likelihood ratio between product measures "
        "P_0^{\\otimes N} and P_1^{\\otimes N} yields the Kullback-Leibler divergence: D_KL(P_0^{\\otimes N} || P_1^{\\otimes N}) = (N / 2σ²) ∑_{t=0}^∞ (Δh_t)². "
        "Because Δh_t = 0 for all t < 2K and |Δh_t| ≤ C_K (Δη)^{2K-1} for t ≥ 2K, the entire summation vanishes up to lag 2K - 1: "
        "∑_{t=0}^∞ (Δh_t)² = ∑_{t=2K}^∞ (Δh_t)² ≤ C_K (Δη)^{2(2K-1)} = C_K (Δη)^{4K-2}. Substituting this into the KL divergence yields "
        "D_KL(P_0^{\\otimes N} || P_1^{\\otimes N}) ≤ (C_K N / 2σ²) (Δη)^{4K-2}. By Pinsker's inequality, the total variation distance satisfies "
        "||P_0^{\\otimes N} - P_1^{\\otimes N}||_TV ≤ √( (1/2) D_KL ) ≤ √(C_K N / 4σ²) (Δη)^{2K-1}."
    ),
    # A9
    (
        "9. Deduction of the Minimax Lower Bound for General α ∈ (0, 1/2):\n"
        "By Le Cam's two-point testing lemma, the minimax risk of testing between P_0 and P_1 with test level α ∈ (0, 1/2) satisfies "
        "inf_ψ max(P_0(ψ ≠ 0), P_1(ψ ≠ 1)) ≥ 1/2 - (1/2) ||P_0^{\\otimes N} - P_1^{\\otimes N}||_TV. For this minimax error probability to fall strictly "
        "below α, we require ||P_0^{\\otimes N} - P_1^{\\otimes N}||_TV ≥ 1 - 2α > 0. Substituting our upper bound on total variation gives: "
        "(C_K N / 4σ²) (Δη)^{4K-2} ≥ (1 - 2α)². Solving for sample size N directly yields: "
        "N ≥ (4(1 - 2α)² / C_K) σ² (Δη)^{-(4K-2)} = Ω(σ² (Δη)^{-(4K-2)}). "
        "Because the two configurations μ_0 and μ_1 belong to the declared class of K-cohort economies, no estimator—whether linear or non-linear, "
        "parametric or non-parametric, biased or unbiased—can achieve error probability below α using fewer than N* observations."
    ),
    # A10
    (
        "10. The Cohort Scaling Exponent: (Δη)^{-6} vs. (Δη)^{-10}:\n"
        "The scaling exponent 4K - 2 dictates an extreme sensitivity to cohort count K. For K = 2 cohorts, the exponent is 4(2) - 2 = 6; for K = 3, "
        "it is 4(3) - 2 = 10. Consider two algorithmic desks narrowing their rebalancing horizon difference from Δη = 0.10 to Δη = 0.01:\n"
        "- For K = 2: (0.10 / 0.01)^6 = 10^6. The required observation count increases by one million times (from 1,000 trades to 1 billion trades).\n"
        "- For K = 3: (0.10 / 0.01)^{10} = 10^{10}. The required observation count increases by ten billion times (from 1,000 to 10 trillion trades)!\n"
        "In modern automated markets where algorithmic desks operate at sub-second speeds with closely overlapping horizons (Δη < 0.01), "
        "recovering latent cohort parameters requires sample sizes that exceed decades or centuries of trading data, rendering deconvolution impossible."
    ),
    # A11
    (
        "11. Algorithm 1: Prony-Hankel Deconvolution Architecture:\n"
        "Algorithm 1 takes estimated impulse response taps h^_t = (1/N) ∑_{j=1}^N Y_t^{(j)} for t = 0, ..., 4K - 1. We construct the (2K × 2K) "
        "Hankel matrix [H_K]_{i,j} = h^_{i+j-2}. In the noise-free limit, H_K factors as H_K = V_K D_K V_K^T, where V_K is the (2K × K) Vandermonde "
        "matrix with columns v_k = [1, η_k, ..., η_k^{2K-1}]^T and D_K = diag(w_1, ..., w_K). To recover the nodes {η_k}, we solve the linear system "
        "H_K c = -h_{2K} for the annihilating polynomial coefficient vector c = [c_0, c_1, ..., c_{K-1}]^T. The roots of P(z) = z^K + ∑_{j=0}^{K-1} c_j z^j "
        "are the estimated memory rates η^_1, ..., η^_K. Finally, portfolio weights w^_k are obtained by solving the linear least-squares Vandermonde "
        "system V_K w = h^_0, completing the closed-form reconstruction."
    ),
    # A12
    (
        "12. Proposition 3.3: Hankel Singular Value Lower Bound via Chebyshev Moments:\n"
        "Proposition 3.3 proves that σ_{2K}(H_K) ≥ c_K (Δη)^{2K-1}. The proof establishes a dual variational formulation: for any unit vector "
        "u ∈ R^{2K} (||u||_2 = 1), the polynomial P_u(η) = ∑_{j=0}^{2K-1} u_j η^j satisfies u^T H_K u = ∑_{k=1}^K w_k P_u(η_k)². "
        "By Markov-Chebyshev extremal polynomial theory on K nodes {η_1, ..., η_K} with minimum spacing Δη, any polynomial of degree 2K - 1 that has "
        "unit L² coefficient norm must satisfy ∑_{k=1}^K w_k P_u(η_k)² ≥ c_K (Δη)^{2(2K-1)}. Taking the square root gives the singular value bound "
        "σ_{2K}(H_K) ≥ c_K (Δη)^{2K-1}. Because σ_1(H_K) ≤ ∑ w_k = 1, the condition number κ(H_K) = σ_1 / σ_{2K} scales precisely as (Δη)^{-(2K-1)}, "
        "proving that Hankel matrix inversion is intrinsically ill-conditioned."
    ),
    # A13
    (
        "13. Theorem 3.2: Matching Minimax Upper Bound:\n"
        "Theorem 3.2 proves that Algorithm 1 achieves the lower bound rate. With Gaussian tap noise of variance σ²/N, the spectral perturbation is "
        "||δH_K||_2 ≤ C √(K / N) σ with high probability. Solving H_K c = -h_{2K} propagates noise into polynomial coefficients as "
        "||δc||_2 ≤ ||δH_K||_2 / σ_{2K}(H_K) ≤ C σ N^{-1/2} (Δη)^{-(2K-1)}. By Wilkinson's polynomial root perturbation theorem, the displacement of "
        "the roots {η_k} is bounded by |η^_k - η_k| ≤ C ||δc||_2 / |P'(η_k)|. Because |P'(η_k)| = ∏_{j ≠ k} |η_k - η_j| ≥ c (Δη)^{K-1}, the root error "
        "scales as |η^_k - η_k| ≤ O(σ N^{-1/2} (Δη)^{-2K}). Setting target accuracy δ and solving for N gives N = O(σ² δ^{-2} (Δη)^{-(4K-2)}), "
        "matching Theorem 3.1 up to constant factors."
    ),
    # A14
    (
        "14. Subspace Estimator Invariance (ESPRIT and Matrix Pencil):\n"
        "Subspace identification methods (such as ESPRIT or Matrix Pencil) bypass polynomial root-finding by computing generalized eigenvalues "
        "of shifted Hankel submatrices: H_{K,1} v = λ H_{K,0} v. However, the column spaces of both H_{K,0} and H_{K,1} are identical to the range "
        "of the Vandermonde matrix V_K. The oblique projector onto this subspace has condition number κ(V_K) = σ_1(V_K) / σ_K(V_K) ≍ (Δη)^{-(2K-1)}. "
        "Inverting this subspace projection to isolate individual generalized eigenvalues amplifies tap noise by the exact same factor (Δη)^{-(2K-1)}. "
        "Thus, ESPRIT, Matrix Pencil, and Prony's method all suffer from identical condition number scaling, confirming the barrier is physical, not algorithmic."
    ),
    # A15
    (
        "15. Lemma 4.2: Positive Definite Toeplitz Execution Cost Matrix:\n"
        "An active probing sequence u_1, ..., u_T injected into a limit order book with Kyle depth κ and transient impact kernel G(t) generates "
        "cumulative execution loss Cost(u) = ∑_{t=1}^T u_t (p_t - p_0) = (1/2) u^T T_G u + ∑ u_t ε_t, where [T_G]_{i,j} = G(|i - j|). "
        "Lemma 4.2 proves that for any non-increasing, convex price impact kernel G(t) > 0, the symmetric Toeplitz matrix T_G is strictly positive "
        "definite: u^T T_G u > 0 for all u ≠ 0. By Bochner's theorem, G(|t|) is the Fourier transform of a positive spectral measure with full support. "
        "Consequently, exploratory market probing is never self-financing: an active supervisor cannot extract information from order books "
        "without paying a positive expected deadweight execution cost ('No Sure Gain')."
    ),
    # A16
    (
        "16. Theorem 4.1: Cumulative Probing Order Volume Lower Bound:\n"
        "To distinguish two candidate trader populations μ_0 and μ_1 separated by Δη with target precision δ, the active probe sequence u_1, ..., u_T "
        "must excite the latent memory modes. The output price response difference is Δp_t = ∑_{s=1}^t ΔG(t - s) u_s. The Fisher information "
        "accumulated by the probe sequence is I_u = (1 / σ²) ∑_{t=1}^T (Δp_t)² = (1 / σ²) u^T (ΔT_G)^T (ΔT_G) u. "
        "Because ΔG(t) vanishes for the first 2K - 1 lags and scales as (Δη)^{2K-1} thereafter, the spectral norm of ΔT_G satisfies "
        "||ΔT_G||_2 ≤ C κ (Δη)^{2K-1}. To achieve information content I_u ≥ δ^{-2}, the probe order volume must satisfy "
        "||u||_2² = ∑_{t=1}^T u_t² ≥ Ω(σ² κ^{-2} δ^{-2} (Δη)^{-(4K-2)}). Probing volume scales inversely with the (4K-2)-th power of spacing."
    ),
    # A17
    (
        "17. Theorem 4.3: Account-Level Margin Solvency and the Ω(δ^{-4}) Capital Barrier:\n"
        "An active probing supervisor must maintain mark-to-market margin solvency with clearinghouse capital reserves B. To avoid directional price "
        "trends, the optimal probe sequence oscillates, yielding cumulative inventory x_t = ∑_{s=1}^t u_s with peak excursion ||x||_∞ ≍ δ^{-1}. "
        "The supervisor's mark-to-market loss at period t is Loss_t = x_t (p_t - p_0) - Cost_t. Adverse price excursions scale as "
        "sup_t |x_t Δp_t| ≍ κ ||x||_∞ ||u||_∞ ≍ κ δ^{-2} ||u||_2² ≍ Ω(σ² δ^{-4} (Δη)^{-(4K-2)}). "
        "To guarantee solvency with probability 1 - α, cash margin capital must satisfy B = Ω(δ^{-4}). "
        "Because capital scales with the fourth power of precision: doubling accuracy requires a 16-fold increase in margin capital, imposing a massive financial barrier."
    ),
    # A18
    (
        "18. Table 4 Calibration: 'Disclosure in Dollars':\n"
        "Table 4 grounds this financial lower bound in institutional parameters for US 10-Year Treasury futures (ZN, depth κ = $12.50 / lot, daily σ = 0.85%) "
        "and E-mini S&P 500 futures (ES). To identify two algorithmic cohorts separated by Δη = 0.05 on a weekly re-estimation schedule, the required active "
        "order volume generates an annual execution loss of $15.4 million in 10-Year Treasuries and $356.2 million in E-mini S&P 500 futures! "
        "For a regulatory agency tasked with market surveillance across dozens of futures contracts, active price probing would consume hundreds of "
        "millions of dollars in cash execution losses and tie up billions in margin collateral, proving active probing is economically and legally impossible."
    ),
    # A19
    (
        "19. Theorem 5.8: Passive Whittle Spectral Divergence Rate Collapse:\n"
        "For stationary Gaussian price returns Δp_t under white noise flow shocks ε_t with variance σ_ε², the spectral density is "
        "f_θ(λ) = (σ_ε² / 2π) |G_θ(e^{iλ})|² on [-π, π]. The asymptotic Kullback-Leibler divergence rate under the Whittle log-likelihood is "
        "lim_{T→∞} (1/T) D_KL = (1/4π) ∫_{-π}^π [ f_0(λ) / f_1(λ) - 1 - log(f_0(λ) / f_1(λ)) ] dλ. Because candidate measures match moments up to order "
        "2K - 1, the open-loop transfer functions differ by only |H_0(e^{iλ}) - H_1(e^{iλ})| = O((Δη)^{2K-1}) uniformly across all frequencies λ. "
        "Propagating through the closed-loop denominator gives f_0(λ) / f_1(λ) = 1 + O((Δη)^{2K-1}). The divergence integral collapses to O((Δη)^{4K-2}), "
        "proving passive observation requires sample length T = Ω((Δη)^{-(4K-2)}) because ambient white noise lacks persistent excitation."
    ),
    # A20
    (
        "20. Section 4.5 & Table 6: Exact Multinomial Resampling with Real Bitcoin Shocks:\n"
        "Section 4.5 and Table 6 stress-test Theorem 3.1 against real, heavy-tailed 1-minute Bitcoin perpetual return shocks (October 2026 data). "
        "Real crypto price changes exhibit extreme excess kurtosis (> 12.4), fat Pareto tails, and volatility clustering. Rather than approximating "
        "noise with a normal distribution, we implement exact multinomial empirical resampling across sample sizes N. Across memory gaps "
        "Δη ∈ [0.05, 0.30], log-log regressions of log(N) on log(1 / Δη) yield fitted empirical slopes of -6.01 for K = 2 (theoretical -6.00) and -9.81 "
        "for K = 3 (theoretical -10.00). This confirms that empirical heavy tails do not destroy the identification barrier: the moment-matching "
        "cancellation mechanism is algebraic and holds invariant under any zero-mean noise distribution."
    ),
    # A21
    (
        "21. Theorem 5.7: Completely Monotone Memory & Minimax Logarithmic Collapse:\n"
        "By Bernstein's Theorem, a completely monotone memory kernel k(t) satisfies (-1)^n k^{(n)}(t) ≥ 0 and admits an integral representation "
        "k(t) = ∫_0^1 η^t dF(η) for a continuous measure F on [0, 1), representing a continuum of trading horizons (K = ∞). Recovering F(η) requires "
        "inverting the continuous Hausdorff moment sequence, which acts as a compact, infinitely smoothing Fredholm integral operator with exponential "
        "singular value decay σ_m ≍ exp(-c m). Inverting this compact operator under noise is exponentially ill-posed: by Donoho's theorem, distinguishing "
        "two continuous distributions with Wasserstein distance w requires N ≥ exp(C / w) observations. Minimax accuracy collapses to logarithmic "
        "w = Θ(1 / log(N / σ²)), proving continuous memory distributions cannot be deconvolved from price data."
    ),
    # A22
    (
        "22. Theorem 5.1: Class-Tagged Disclosure and Decoupled Single-Pole Regressions:\n"
        "Theorem 5.1 proves that observing class-tagged order flows y_t = [y_{1,t}, ..., y_{K,t}]^T (e.g. MiFID II RTS 24 algo_id tags) completely uncouples "
        "the estimation problem. Because each cohort state evolves independently as x_{k,t} = η_k x_{k,t-1} + (1 - η_k) p_{t-1}, observing y_{k,t} allows "
        "the supervisor to run K separate single-variable autoregressions of y_{k,t} on p_{t-1}, completely bypassing the feedback denominator D_{cl}(z). "
        "Sample complexity for memory rates collapses from Θ(σ² (Δη)^{-(4K-2)}) to Θ(σ² (Δη)^{-2}) (the exponent collapses from 4K - 2 to 2). "
        "For portfolio weights w_k, sample complexity is O(σ² δ^{-2}), which is O(1) completely independent of memory spacing Δη."
    ),
    # A23
    (
        "23. Proposition 5.5: The Supervisory Choice Rule & Critical Information Band:\n"
        "Proposition 5.5 formalizes the supervisor's choice rule: mandate class disclosure if and only if fixed regulatory reporting cost C_rep is less "
        "than active probing deadweight loss C_probe(Δη) ≍ κ σ² (Δη)^{-(4K-2)}. This establishes an intermediate economic band [Δη_min, Δη_max]:\n"
        "- When Δη > Δη_max, algorithms are widely separated; price-based estimation is cheap, and disclosure is unnecessary.\n"
        "- When Δη < Δη_min, algorithms are virtually identical; distinguishing them provides negligible regulatory benefit.\n"
        "- In the critical band Δη ∈ [Δη_min, Δη_max], algorithms are distinct enough to create differential systemic risk, but close enough to make "
        "price-based deconvolution prohibitively expensive. Here, mandatory regulatory disclosure is socially indispensable."
    ),
    # A24
    (
        "24. Table 7: Primary Empirical Findings Across 8 CFTC Futures Markets:\n"
        "Table 7 evaluates parameter estimation across 8 primary CFTC futures markets (E-mini S&P, 10Y Treasuries, Crude Oil, Euro FX, Corn, etc.). "
        "Weekly Disaggregated Commitments of Traders (DCOT) position reports categorize market open interest into Managed Money (hedge funds), "
        "Swap Dealers, and Commercial Hedgers. By mapping these categories into structural model cohorts, the paper estimates memory persistence η_k "
        "and market shares w_k. Across all 8 markets, parameter uncertainty intervals derived from public CFTC disclosure were 25x to 55x narrower "
        "than what econometric inversion on daily price data could achieve, confirming the empirical value of regulatory reporting."
    ),
    # A25
    (
        "25. Table 8: The Pre-Registered 12-Market Replication Protocol (SHA-256):\n"
        "Under SHA-256 pre-registration hash 591e71c9... (registered 31 October 2026), Table 8 replicates parameter estimation across 12 additional "
        "CFTC futures markets (gold, silver, copper, corn, soybeans, wheat, live cattle, coffee, sugar, cotton, Nasdaq-100, British pound). Across all 12 "
        "markets, empirical uncertainty intervals for trader memory η_k and weights w_k derived from weekly DCOT reports are 23.4x to 68.7x narrower "
        "than under price-only econometric inversion. In wheat and corn, the ratio reaches 64x; in gold and copper, 58x. The Data Equivalence Multiplier "
        "reveals that a single weekly public CFTC report delivers information equivalent to 14,200 to 89,500 active market probes."
    ),
    # A26
    (
        "26. Table 9: The Full 22-Test Pre-Specified Scorecard Audit:\n"
        "Table 9 presents the complete pre-registered 22-test scorecard across the empirical evaluation suite: exactly 11 tests passed at the 5% level, "
        "10 failed, and 1 was unsupported due to exchange data limits. The 11 passing tests confirm the CFTC position interval narrowing, exact "
        "multinomial Bitcoin noise scaling, and Prony-Hankel inversion. The 10 failures concentrate in high-frequency crypto perpetuals (hypotheses N2 and N3). "
        "By reporting every pre-registered test failure transparently, the paper eliminates publication bias and proves that coarse public buckets fail, "
        "strengthening the argument for granular algorithmic tags."
    ),
    # A27
    (
        "27. Within-Class Sign Cancellation: The Fallacy of Coarse Reporting Buckets:\n"
        "In Table 9, hypotheses N2 (price forecasting position ratios) and N3 (taker flow pinning down combined response Ψ) failed Diebold-Mariano tests "
        "on 29 and 25 of 30 Binance perpetual contracts (October 2026 data, SHA-256 72cbc8ba...). This failure demonstrates **Within-Class Sign Cancellation**: "
        "public reporting buckets (e.g. 'Top Traders' or 'Managed Money') combine opposing algorithmic strategies, such as trend-following CTAs "
        "(momentum, w_CTA > 0, η_CTA ≈ 0.9) and cash-futures basis arbitrageurs (mean-reverting, w_Arb < 0, η_Arb ≈ 0.1). Because their orders move in "
        "opposite directions, their flows destructively interfere: w_CTA y_{CTA,t} + w_Arb y_{Arb,t} ≈ 0. Coarse public buckets wash out predictive signals, "
        "proving that regulators must mandate granular MiFID II RTS 24 algo_id tags."
    ),
    # A28
    (
        "28. Theorem 6.1: The Spectral Blind Spot & Matrix Non-Normality:\n"
        "Theorem 6.1 constructs two state-space systems: A_1 = diag(λ_1, λ_2) (normal, orthogonal eigenvectors) and A_2 = [λ_1, γ; 0, λ_2] (non-normal, "
        "coupling γ > 0). Both systems share identical closed-loop eigenvalues 0 < λ_2 < λ_1 < 1, identical one-step return variance, and identical "
        "stationary covariance under white noise. However, because A_2's eigenvectors are non-orthogonal, its transient matrix powers scale as "
        "[A_2^t]_{1,2} = γ (λ_1^t - λ_2^t) / (λ_1 - λ_2), which grows arbitrarily large as γ increases. Peak transient gain sup_t ||A_2^t||_2 grows without "
        "bound as γ → ∞, proving that eigenvalue stability and low stationary variance fail to protect a market from violent transient amplification."
    ),
    # A29
    (
        "29. Pseudospectra, the Kreiss Matrix Theorem, and Flash Crash Mechanics:\n"
        "The ε-pseudospectrum σ_ε(A) = {z ∈ C : ||(zI - A)^{-1}||_2 > ε^{-1}} quantifies transient sensitivity. While true eigenvalues of A_2 lie "
        "strictly inside the unit disk at λ_1, λ_2 < 1, the non-normal resolvent blows up in the complex plane, causing pseudospectral contours to protrude "
        "far outside the unit circle |z| > 1. By the Kreiss Matrix Theorem, peak transient excursion satisfies K(A) ≤ sup_t ||A^t||_2 ≤ e · n · K(A), "
        "where K(A) = sup_{|z|>1} (|z|-1) ||(zI - A)^{-1}||. Figure 7 shows two markets with identical 5-period half-lives and 1.2% volatility: "
        "Market 1 decays smoothly, while Market 2 experiences a 40x transient loss spike. Traditional VaR measures only stationary variance, remaining blind to flash crash risks."
    ),
    # A30
    (
        "30. Appendix F & Proposition 5.6: Aggregate Warehousing vs. Targeted Algorithmic Halts:\n"
        "Appendix F (Theorem F.3) analyzes an unlevered warehousing desk with carry costs b I + d I² under a hard stress budget B. The optimal inventory "
        "position I(C_N, F) depends solely on the scalar cumulative impulse response G = ∑_{t<H} h_t. Estimating G converges at the ordinary parametric "
        "rate O(N^{-1/2}), completely free of cohort spacing Δη, cohort count K, or memory floors. Thus, cohort deconvolution is unnecessary for aggregate "
        "inventory warehousing. In contrast, targeted supervisory halts (Proposition 5.6 / S23) require identifying which specific cohort k is rogue or over-leveraged "
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
        
        header = s.header; hp = header.paragraphs[0]; hp.alignment = WD_ALIGN_PARAGRAPH.RIGHT
        hrun = hp.add_run("Paper 1: Master Reading & Analysis Guide (30 Questions)")
        hrun.font.name = "Calibri"; hrun.font.size = Pt(8.5); hrun.font.color.rgb = RGBColor(120, 120, 120)
        
        footer = s.footer; fp = footer.paragraphs[0]; fp.alignment = WD_ALIGN_PARAGRAPH.CENTER
        frun = fp.add_run("What Prices Cannot Tell a Market Supervisor — Development Revision: 2 November 2026")
        frun.font.name = "Calibri"; frun.font.size = Pt(8.5); frun.font.color.rgb = RGBColor(120, 120, 120)

    # Title
    p_pre = doc.add_paragraph()
    p_pre.paragraph_format.space_before = Pt(24); p_pre.paragraph_format.space_after = Pt(4)
    r_pre = p_pre.add_run("PAPER 1: COMPREHENSIVE CO-AUTHOR READING & ANALYSIS GUIDE")
    r_pre.font.name = "Calibri"; r_pre.font.size = Pt(12); r_pre.font.bold = True; r_pre.font.color.rgb = RGBColor(0, 119, 182)

    p_title = doc.add_paragraph()
    p_title.paragraph_format.space_before = Pt(0); p_title.paragraph_format.space_after = Pt(8)
    r_title = p_title.add_run("What Prices Cannot Tell a Market Supervisor:\nThe Cost of Identifying Trader Groups and the Value of Class Disclosure")
    r_title.font.name = "Calibri"; r_title.font.size = Pt(18); r_title.font.bold = True; r_title.font.color.rgb = RGBColor(11, 37, 69)

    p_sub = doc.add_paragraph()
    p_sub.paragraph_format.space_before = Pt(0); p_sub.paragraph_format.space_after = Pt(14)
    r_sub = p_sub.add_run(
        "30 Deep, Exhaustive Technical Questions Covering Every Theorem, Lemma, Empirical Test, and Appendix\n"
        "Development Revision: 2 November 2026 (Strictly Paper 1 Only) | Lead Author: Pratik Niroula"
    )
    r_sub.font.name = "Calibri"; r_sub.font.size = Pt(10.5); r_sub.font.italic = True; r_sub.font.color.rgb = RGBColor(19, 64, 116)

    # Note
    p_note = doc.add_paragraph()
    p_note.paragraph_format.space_before = Pt(0); p_note.paragraph_format.space_after = Pt(14)
    r_nb = p_note.add_run("To Co-Authors (Sujan Khatiwada and Prashant Niroula): ")
    r_nb.font.name = "Calibri"; r_nb.font.size = Pt(9.5); r_nb.font.bold = True; r_nb.font.color.rgb = RGBColor(11, 37, 69)
    r_nt = p_note.add_run(
        "This master reading guide contains 30 comprehensive, deep questions covering our latest Paper 1 draft. "
        "Because you have our earlier draft, these questions systematically cover every newly added mathematical proof, "
        "the registered 12-market CFTC replication (Table 8), the October 2026 Binance perpetuals scorecard (Table 9), "
        "exact multinomial Bitcoin noise resampling (Table 6), the two-root stock-flow bridge, the finite-horizon inventory note (Appendix F), "
        "and our 787 Lean 4 machine-verified theorems. Both co-authors must read every section thoroughly and complete the full analysis."
    )
    r_nt.font.name = "Calibri"; r_nt.font.size = Pt(9.5); r_nt.font.color.rgb = RGBColor(70, 70, 70)

    # 30 Questions
    for item in QUESTIONS_30:
        p = doc.add_paragraph()
        p.paragraph_format.space_before = Pt(8); p.paragraph_format.space_after = Pt(4)
        p.paragraph_format.line_spacing = 1.15
        
        r_num = p.add_run(f"Question {item['num']}: {item['title']}\n")
        r_num.font.name = "Calibri"; r_num.font.size = Pt(11); r_num.font.bold = True; r_num.font.color.rgb = RGBColor(11, 37, 69)
        
        r_sec = p.add_run(f"Reading: {item['section']} | Key Objects: {item['key_objects']}\n")
        r_sec.font.name = "Calibri"; r_sec.font.size = Pt(9); r_sec.font.italic = True; r_sec.font.color.rgb = RGBColor(100, 116, 139)
        
        r_q = p.add_run(item['q'])
        r_q.font.name = "Calibri"; r_q.font.size = Pt(10); r_q.font.color.rgb = RGBColor(29, 45, 68)

    out_path = ROOT / "Paper1_Questions_Workbook.docx"
    doc.save(str(out_path))
    print(f"Saved 30 Questions to: {out_path}")
    return out_path

def build_answers_doc():
    doc = Document()
    
    # Margin settings
    for s in doc.sections:
        s.top_margin = Inches(1.0); s.bottom_margin = Inches(1.0)
        s.left_margin = Inches(1.0); s.right_margin = Inches(1.0)
        
        header = s.header; hp = header.paragraphs[0]; hp.alignment = WD_ALIGN_PARAGRAPH.RIGHT
        hrun = hp.add_run("Paper 1: Master Reference Answers (30 Questions)")
        hrun.font.name = "Calibri"; hrun.font.size = Pt(8.5); hrun.font.color.rgb = RGBColor(120, 120, 120)
        
        footer = s.footer; fp = footer.paragraphs[0]; fp.alignment = WD_ALIGN_PARAGRAPH.CENTER
        frun = fp.add_run("What Prices Cannot Tell a Market Supervisor — Development Revision: 2 November 2026")
        frun.font.name = "Calibri"; frun.font.size = Pt(8.5); frun.font.color.rgb = RGBColor(120, 120, 120)

    # Title
    p_pre = doc.add_paragraph()
    p_pre.paragraph_format.space_before = Pt(24); p_pre.paragraph_format.space_after = Pt(4)
    r_pre = p_pre.add_run("PAPER 1: MASTER REFERENCE ANSWERS & MODEL SOLUTIONS")
    r_pre.font.name = "Calibri"; r_pre.font.size = Pt(12); r_pre.font.bold = True; r_pre.font.color.rgb = RGBColor(0, 119, 182)

    p_title = doc.add_paragraph()
    p_title.paragraph_format.space_before = Pt(0); p_title.paragraph_format.space_after = Pt(8)
    r_title = p_title.add_run("What Prices Cannot Tell a Market Supervisor:\nThe Cost of Identifying Trader Groups and the Value of Class Disclosure")
    r_title.font.name = "Calibri"; r_title.font.size = Pt(18); r_title.font.bold = True; r_title.font.color.rgb = RGBColor(11, 37, 69)

    p_sub = doc.add_paragraph()
    p_sub.paragraph_format.space_before = Pt(0); p_sub.paragraph_format.space_after = Pt(14)
    r_sub = p_sub.add_run(
        "Exhaustive, Publication-Grade Reference Solutions for all 30 Questions (Development Revision: 2 November 2026)\n"
        "Lead Author: Pratik Niroula | Co-Authors: Sujan Khatiwada and Prashant Niroula"
    )
    r_sub.font.name = "Calibri"; r_sub.font.size = Pt(10.5); r_sub.font.italic = True; r_sub.font.color.rgb = RGBColor(19, 64, 116)

    # 30 Questions + Answers
    for idx, item in enumerate(QUESTIONS_30):
        ans_text = ANSWERS_30[idx]
        
        p_q = doc.add_paragraph()
        p_q.paragraph_format.space_before = Pt(12); p_q.paragraph_format.space_after = Pt(2)
        p_q.paragraph_format.keep_with_next = True
        
        r_num = p_q.add_run(f"Question {item['num']}: {item['title']}\n")
        r_num.font.name = "Calibri"; r_num.font.size = Pt(11); r_num.font.bold = True; r_num.font.color.rgb = RGBColor(11, 37, 69)
        
        r_sec = p_q.add_run(f"Reading: {item['section']} | Key Objects: {item['key_objects']}\n")
        r_sec.font.name = "Calibri"; r_sec.font.size = Pt(9); r_sec.font.italic = True; r_sec.font.color.rgb = RGBColor(100, 116, 139)
        
        r_q = p_q.add_run(f"Question: {item['q']}")
        r_q.font.name = "Calibri"; r_q.font.size = Pt(9.5); r_q.font.bold = True; r_q.font.color.rgb = RGBColor(19, 64, 116)
        
        p_a = doc.add_paragraph()
        p_a.paragraph_format.space_before = Pt(2); p_a.paragraph_format.space_after = Pt(8)
        p_a.paragraph_format.line_spacing = 1.15
        
        r_a_hdr = p_a.add_run("Model Answer & Walkthrough:\n")
        r_a_hdr.font.name = "Calibri"; r_a_hdr.font.size = Pt(10); r_a_hdr.font.bold = True; r_a_hdr.font.color.rgb = RGBColor(0, 119, 182)
        
        r_a = p_a.add_run(ans_text)
        r_a.font.name = "Calibri"; r_a.font.size = Pt(9.5); r_a.font.color.rgb = RGBColor(29, 45, 68)

    out_path = ROOT / "Paper1_Answers_Solution_Manual.docx"
    doc.save(str(out_path))
    print(f"Saved 30 Answers to: {out_path}")
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
    print("All 30 questions and answers successfully built and mirrored!")
