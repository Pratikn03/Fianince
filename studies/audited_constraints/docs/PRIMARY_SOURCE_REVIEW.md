# Targeted primary-source review, 18 September 2026

This supplements, rather than silently rewrites, the v0.4 review. It is not exhaustive novelty clearance.

1. van Waarde, Eising, Trentelman and Camlibel. Data informativity: a new perspective on data-driven analysis and control. arXiv:1908.00468, revised 2020. https://arxiv.org/abs/1908.00468
   Establishes why property certification and full model identification are different questions. Our separation is not a new general informativity principle.
2. Khosravi and Smith. Regularized Identification with Internal Positivity Side-Information. arXiv:2111.00407, 2021. https://arxiv.org/abs/2111.00407
   Prior positivity-side-information identification; no claim that positivity constraints originate here.
3. Manchester. Input Design for System Identification via Convex Relaxation. arXiv:1009.5614, 2010. https://arxiv.org/abs/1009.5614
   Input amplitude/power constraints and information design are established. Endpoint diversification here is an explicit tested design, not a new optimal design theorem.
4. Clopper and Pearson. The Use of Confidence or Fiducial Limits Illustrated in the Case of the Binomial. Biometrika 26(4), 404–413, 1934. doi:10.1093/biomet/26.4.404. https://academic.oup.com/biomet/article/26/4/404/291538
   Source of the exact binomial interval. We use it for a predeclared finite-horizon event, not a new confidence-interval method.
5. Abi Jaber, De Carvalho and Pham. Trading with propagators and constraints: applications to optimal execution and battery storage. arXiv:2409.12098, 2024. https://arxiv.org/abs/2409.12098
   Prior explicit constraints in financial trading models; their optimizer is not implemented in this release.
6. Byrd, Hybinette and Balch. ABIDES: Towards High-Fidelity Market Simulation for AI Research. arXiv:1904.12066, 2019. https://arxiv.org/abs/1904.12066
   Independent simulator candidate, not a platform we used or externally validated on.
7. SciPy binomtest official documentation. https://docs.scipy.org/doc/scipy/reference/generated/scipy.stats.binomtest.html
   Separate exact-interval API used in the internal verification. Pinning in requirements.txt records the local version, not the current web version.

The geometric/norm tail arguments and Gaussian regression pivot are standard mathematics, proved explicitly in the manuscript. The proposed contribution is the auditable information chain, its budget-dependent experimental consequences, and its failure at the boundary between signal feedback and account feedback. External specialists must still assess priority and significance.
