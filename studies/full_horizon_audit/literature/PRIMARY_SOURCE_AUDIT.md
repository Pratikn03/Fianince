# Primary-source and novelty audit

Audit date: 18 September 2026. This is a focused literature audit, not exhaustive proof of novelty. Bibliographic records, abstracts and selected accessible full texts were checked. No author was contacted; no endorsement or external expert review occurred. The source record below is intentionally explicit about review depth. Full copyrighted papers are not redistributed in this package.

## Closest predecessors

### 1. Data informativity
Henk J. van Waarde, Jaap Eising, Harry L. Trentelman, M. Kanat Camlibel. *Data informativity: a new perspective on data-driven analysis and control*. arXiv:1908.00468v3, 10 January 2020.

https://arxiv.org/abs/1908.00468
https://arxiv.org/html/1908.00468v2

Review: metadata and selected full-text definitions. The framework asks whether every system consistent with the data has a desired property. **Consequences:** the central distinction between a fitted model and a defensible system property is prior art. The present work must be framed as a specialized measurement problem, not a new general principle.

### 2. Positive identification
Mohammad Khosravi and Roy S. Smith. *Regularized Identification with Internal Positivity Side-Information*. SIAM Journal on Control and Optimization, 63(1), 26–56, 2025. DOI 10.1137/23M1556095.

https://epubs.siam.org/doi/10.1137/23M1556095
https://arxiv.org/abs/2111.00407
https://arxiv.org/html/2111.00407v1

Review: publication record and selected full preprint. Constrained RKHS identification incorporates internal positivity; a finite convex formulation is derived. **Consequences:** positivity-constrained identification is not new. The current NNLS and outer LP are transparent conventional comparisons, not reproductions of this entire method or evidence of superiority over it.

### 3. Steady-state gain and long-memory response
Mohammad Khosravi and Roy S. Smith. *Kernel-based Impulse Response Identification with Side-Information on Steady-State Gain*. Reviewed version: arXiv:2111.00409v2, 6 November 2022.

https://arxiv.org/abs/2111.00409
https://arxiv.org/html/2111.00409v2

Review: metadata and selected full text including the motivation on slowly decaying responses. The work directly connects identification with gain side information. **Consequences:** unseen response tails and gain restrictions are established identification concerns. The present rate-floor inequalities and observation-budget example need application-specific novelty assessment.

### 4. Convex moment bounds
Dimitris Bertsimas and Ioana Popescu. *Optimal Inequalities in Probability Theory: A Convex Optimization Approach*. SIAM Journal on Optimization, 15(3), 780–804, 2005. DOI 10.1137/S1052623401399903.

https://epubs.siam.org/doi/10.1137/S1052623401399903

Review: official abstract and bibliographic record, not a complete theorem-by-theorem comparison. **Consequences:** bounding a functional over positive measures subject to moment information is a classical convex approach. The specific LP outer relaxation is not a new general moment method.

### 5. Positive-system stability
Anders Rantzer. *Scalable Control of Positive Systems*. European Journal of Control, 24, 72–80, 2015. DOI 10.1016/j.ejcon.2015.04.004.

https://portal.research.lu.se/en/publications/scalable-control-of-positive-systems/

Review: university publication record and source context. **Consequences:** the threshold a + sum(q) < 1 specializes existing positive-system theory. The proof is supplied because it is short and central, not because the general stability principle is novel.

### 6. Stable-positive system identification
Jack Umenberger and Ian R. Manchester. *Scalable Identification of Stable Positive Systems*. IEEE CDC, 4630–4635, 2016. DOI 10.1109/CDC.2016.7798974.

https://user.it.uu.se/~jacum349/pdfs/pos16.pdf

Review: author-hosted paper, including its first-page assumptions and identification setup. **Consequences:** this is a different measured-state/parameterization setting. Fitting only stable systems is not an adequate test of whether an unknown closed loop is stable. No direct same-information performance claim is made against this paper.

### 7. Moment ill-posedness
Daniel Gerth, Bernd Hofmann, Christopher Hofmann, Stefan Kindermann. *The Hausdorff Moment Problem in the light of ill-posedness of type I*. arXiv:2104.06029, 2021.

https://arxiv.org/abs/2104.06029

Review: abstract and metadata only. **Consequences:** moment inversion ill-posedness is established. More detailed comparison is needed before asserting novelty of the exact construction.

### 8. Finite-sample identification
Samet Oymak and Necmiye Ozay. *Non-asymptotic Identification of LTI Systems from a Single Trajectory*. arXiv:1806.05722, revised 2019.

https://arxiv.org/abs/1806.05722

Review: metadata and abstract. **Consequences:** nonasymptotic identification already treats observation length and information conditions. The present controlled-response experiment is different and does not refute results under stronger excitation or assumptions.

Yassir Jedra and Alexandre Proutiere. *Sample Complexity Lower Bounds for Linear System Identification*. arXiv:1903.10343, 2019.

https://arxiv.org/abs/1903.10343

Review: metadata and abstract. **Consequences:** statistical lower bounds in system identification are an established research line; the simple Gaussian specialization is not the first observation-complexity argument.

### 9. Classical two-point testing
Yury Polyanskiy and Yihong Wu. *Dualizing Le Cam’s method for functional estimation, with applications to estimating the unseens*. arXiv:1902.05616, 2019.

https://arxiv.org/abs/1902.05616

Review: abstract and metadata. **Consequences:** two-point lower bounds and their connection to convexity are established. The Gaussian risk and abstention inequality are derived fully in the new manuscript, without claiming a new general testing principle.

### 10. Adaptive-agent finance and performative prediction
Christophre Georges and Javier Pereira. *Market Stability with Machine Learning Agents*. Journal of Economic Dynamics and Control, 122, 104032, 2021. DOI 10.1016/j.jedc.2020.104032.

Reviewed author preprint (April 18, 2019):
https://academics.hamilton.edu/economics/cgeorges/risk-ml-april-2019.pdf

Review: selected full preprint, including introductory mechanism and model discussion; not assumed identical to the final journal text. **Consequences:** adaptation changing the price-generating mechanism is not a new finance research gap.

Juan C. Perdomo, Tijana Zrnic, Celestine Mendler-Dünner, Moritz Hardt. *Performative Prediction*. Proceedings of Machine Learning Research, 119, 7599–7609, 2020.

https://proceedings.mlr.press/v119/perdomo20a.html

Review: official paper record and abstract. **Consequences:** decision-induced distribution feedback is established. The current fixed positive-memory system is not a new general performative-learning framework.

## Recent adjacent work, not a completed baseline reproduction

Yichen Zhou and Stephen Tu. *CLT-Optimal Parameter Error Bounds for Linear System Identification*. arXiv:2604.21270v1, April 23, 2026.

https://arxiv.org/abs/2604.21270

Review: abstract/metadata. Included to avoid treating pre-2020 identification as the current frontier. No superiority over this paper is claimed; its full statistical setting has not been replicated here.

## Numerical implementation sources

SciPy official documentation:
https://docs.scipy.org/doc/scipy/reference/generated/scipy.optimize.nnls.html
https://docs.scipy.org/doc/scipy/reference/optimize.linprog-highs-ds.html

Documentation was checked online. The executed version is SciPy 1.17.0, as recorded in the environment, regardless of what a newer online documentation version displays.

## Search limitations and practical conclusion

Some broad web searches returned irrelevant keyword matches, so direct primary URLs and exact titles were preferred. This can limit recall. The present audit establishes strong relevant predecessors; it does not establish absence of an equivalent specialization. The title and claim should remain narrow. A reviewer should search positive realization, truncated moments, system-property informativity, and functional testing in addition to finance.
