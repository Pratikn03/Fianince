# Foundational Literature Novelty and Predecessor Positioning Matrix

**Manuscript Title:** *From Human Markets to Machine Markets: Feedback Stability, Auditable Memory, and Financial Constraints*  
**Date:** October 2026  
**Audited Status:** Verified 1-to-1 against Table 2 (`tab:lineage`) and Manuscript Proofs  

---

## 1. Executive Novelty Framework

This document maps the five foundational mathematical, systems-theoretic, and statistical disciplines underpinning the manuscript's core theorems (M1--M6, NL1, CC1, GE1). For each discipline, we summarize:
1. Authoritative classical predecessors (with seminal citations and publication years).
2. Direct application to Limit Order Book (LOB) closed-loop feedback identification.
3. The specific market-microstructure increment established in this paper.

---

## 2. Structured Lineage and Novelty Matrix

| Topic & Theorem | Authoritative Classical Predecessors | Baseline Applicability to LOBs | Specific Market Increment in This Paper |
| :--- | :--- | :--- | :--- |
| **1. Minimal Realization & PBH Eigenspace Defect**<br>*(Theorem M1 & Prop 5.1)* | **Kalman (1960, 1963)**: Linear dynamical systems.<br>**Gilbert (1963)**: Controllability and observability.<br>**Ho & Kálmán (1966)**: Minimal Markov parameter realization.<br>**Hautus (1969)**: PBH rank test for observability. | Classical realization theory constructs minimal state-space realizations from impulse response transfer functions, but assumes unconstrained linear time-invariant inputs without strategic market-making agent feedback. | **Exact Swapped-Feedback Equivalence Classes:** Proves that in economies with common-rate adapting cohorts, aggregate price-flow dynamics exhibit an exact $(n-1)$-dimensional Popov--Belevitch--Hautus unobservable eigenspace defect ($Cv = 0, Jv = (1-\eta)v$). Proves that passive order flow surveillance cannot attribute feedback to individual algorithmic cohorts, and establishes minimal active probing rank conditions ($n-1$ independent pulses) to break symmetry. |
| **2. Minimax Mixture Deconvolution**<br>*(Theorem M2)* | **Le Cam (1973)**: Dimensionality restrictions.<br>**Chen (1995)**: Finite mixture component estimation rates.<br>**Heinrich & Kahn (2018)**: Minimax bounds for exponential mixtures.<br>**Wu & Yang (2020)**: Optimal estimation via denoised moments. | Establishes statistical lower bounds on separating overlapping Gaussian or exponential mixtures in independent identically distributed (i.i.d.) observations. Does not model closed-loop dynamic market feedback or endogenous quote fading. | **Sample Complexity Lower Bound ($\delta^{-4}$):** Extends Le Cam's two-point method to closed-loop discrete LOB recursions, proving that detecting cohort memory rate discrepancies of magnitude $\delta$ requires a sample complexity lower bound scaling as $\Omega(\delta^{-4} / (A^2 \lambda^2))$ under probe amplitude $A$ and book depth $\lambda$. |
| **3. Selective Classification & Mandatory Abstention**<br>*(Theorem M3 & Thm 9.2)* | **Chow (1970)**: Recognition error and reject tradeoff.<br>**Herbei & Wegkamp (2006)**: Risk-controlled classification with reject option.<br>**Geifman & El-Yaniv (2017)**: Selective classification in neural networks. | Formulates classification with an abstention option where the predictor outputs $\bot$ when posterior confidence is below a fixed threshold, bounding conditional error on the coverage set. | **Two-World Microstructure Abstention Spiral:** Proves that any error-controlled stability classifier must abstain on an explicit finite-sample neighborhood around the critical spectral boundary $S=1$. Furthermore, reveals the endogenous market pathology: algorithmic abstention (quote cancellation) evaporates book depth, mechanically inflating loop gain into supercritical collapse ($S > 1.0$). |
| **4. Set-Membership & Conic Bounding**<br>*(Theorem M4 & Thm 7.1)* | **Hausdorff (1921)**: Moment sequences.<br>**Perlman (1969)**: Cone-restricted testing.<br>**Milanese & Vicino (1991)**: Set-membership identification.<br>**Calafiore & Campi (2005)**: Uncertain convex programs. | Bounding parameter sets compatible with bounded observation noise via convex optimization, ellipsoids, and Linear Matrix Inequalities (LMIs). | **Covariance-Aware Conic Relaxation:** Solves the non-convex bilinear feedback identification problem via second-order cone programming (SOCP) with McCormick bilinear product lifting. Formulates a size-valid hypothesis test over completely monotone positive-memory kernels, verified on empirical NASDAQ Nordic L2 data. |
| **5. Nonnormal Kreiss Matrix Solvency**<br>*(Theorem M5, M6, NL1)* | **Kreiss (1962)**: Difference equation stability.<br>**Spijker (1991)**: LeVeque--Trefethen Kreiss conjecture proof.<br>**Trefethen & Embree (2005)**: Spectra and Pseudospectra. | Kreiss Matrix Theorem bounds transient nonnormal matrix power amplification $\sup_{k} \|J^k\| \le e \cdot n \cdot \mathcal{K}(J)$ using the pseudospectral resolvent norm. | **Exact Worst-Case Institutional Solvency Radius:** Proves that spectral radius stability ($\rho(J) < 1$) fails to prevent institutional dealer default due to nonnormal amplification. Derives the closed-form safe inventory radius $r^* = B / (\mathcal{K}(J) \cdot P)$, proves that non-linear square-root impact (Theorem NL1) preserves this bound conservatively, and proves that cross-asset impact (Theorem M6) inflates $\mathcal{K}$ by $16.9\%$, contracting the solvency boundary by $14.43\%$. |

---

## 3. Predecessor Positioning Summary

The contributions of this manuscript do not rely on unverified claims of "discovering" control theory or statistical learning primitives. Rather, the work establishes **rigorous, provably sound mechanisms translating foundational theorems into the unique closed-loop realities of electronic financial markets**:
- **From static estimation to dynamic closed loops:** Where classical econometrics treats prices as passive time series, we explicitly model the reflexive coupling between quotes, fills, and price adjustments.
- **From asymptotic limits to certified finite-data boundaries:** We replace asymptotic $t$-statistics with finite-sample second-order cone certificates and exact Lean 4 formal verifications.
- **From single-asset isolation to multi-clearinghouse systemic networks:** We extend local dealer inventory control to multi-asset cross-impact (Theorem M6) and interconnected clearinghouse contagion (Theorem CC1).
