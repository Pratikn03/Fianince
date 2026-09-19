# Focused literature and novelty audit

Search date: 18 September 2026. This is a focused primary-source audit, not a systematic review or proof of priority. No paywall was bypassed. Titles, versions, abstracts, and selected accessible full texts were checked. An absence of a search hit is not evidence of global novelty.

## Closest predecessors

1. **Georges, C., and Pereira, J. (2021). Market stability with machine learning agents.** Journal of Economic Dynamics and Control 122, 104032. DOI: 10.1016/j.jedc.2020.104032. Author-hosted April 2019 preprint: https://academics.hamilton.edu/economics/cgeorges/risk-ml-april-2019.pdf
   - Already studies adaptive/asynchronous forecasting and market instability. “Adaptive agents alter their own price-generating environment” is not a new research gap.
   - The current study instead asks which hidden feedback structures finite response observations can distinguish. The 2019 accessible preprint was read; it must not be represented as the final 2021 text.

2. **Perdomo, J. C., Zrnic, T., Mendler-Dünner, C., and Hardt, M. (2020). Performative Prediction.** PMLR 119, 7599–7609. https://proceedings.mlr.press/v119/perdomo20a.html
   - Establishes the performative prediction framework. Market–model feedback is therefore not new simply because it receives a finance label.
   - Our target is a restricted input–output identifiability and stability-classification question, not a new performative-equilibrium concept.

3. **Oymak, S., and Ozay, N. (2019 preprint version). Non-asymptotic Identification of LTI Systems from a Single Trajectory.** arXiv:1806.05722v2. https://arxiv.org/abs/1806.05722v2
   - Studies finite-sample estimation of Markov parameters and realization of linear systems. The broad need for sufficient horizon, system-order information, excitation, and conditioning is established.
   - The current finite-window pair construction does not contradict recovery of a known finite-order observable system with sufficient data. The implemented matrix pencil is a simple conventional comparator, not a reproduction of that entire paper.

4. **Rantzer, A. (2015). Scalable Control of Positive Systems.** European Journal of Control 24, 72–80. DOI: 10.1016/j.ejcon.2015.04.004. https://portal.research.lu.se/en/publications/scalable-control-of-positive-systems/
   - Positivity simplifies stability and gain analysis. The a+sum(q)<1 criterion is a model specialization, not a newly discovered stability principle.
   - The manuscript supplies a direct proof so the exact assumptions can be audited.

5. **Umenberger, J., and Manchester, I. R. (2016). Scalable Identification of Stable Positive Systems.** CDC, 4630–4635. DOI: 10.1109/CDC.2016.7798974. Author full text: https://user.it.uu.se/~jacum349/pdfs/pos16.pdf
   - Positivity-constrained system identification already has a substantial literature. This work parameterizes stable positive systems and bounds simulation error.
   - Our problem allows both stable and unstable candidates and asks when data separate them; an estimator constrained to stability cannot establish that an unknown true market is stable merely by returning a stable fit.

6. **Fritzsche, B., Kirstein, B., and Mädler, C. (2020). A Schur-Nevanlinna type algorithm for the truncated matricial Hausdorff moment problem.** arXiv:2005.03365. https://arxiv.org/abs/2005.03365
   - The solution set of a truncated moment problem is classical mathematical territory. The signed barycentric measure construction uses standard polynomial interpolation identities.
   - The strongest plausible contribution is the explicit adaptive-market witness, its interpretation, and a measurement contract with an auditable benchmark—not a claim to have invented moment non-identifiability.

7. **Farina, G., and Perdomo, J. C. (2026). The Stability of Online Algorithms in Performative Prediction.** arXiv:2602.24207v2. https://arxiv.org/abs/2602.24207v2
   - Recent work directly addresses stability of online algorithms under decision feedback. Only the cited preprint version is identified.
   - Algorithmic regret/equilibrium stability and the present positive market state-space condition are different objects; they should not be conflated.

8. **Financial Stability Board (2024). The Financial Stability Implications of Artificial Intelligence.** https://www.fsb.org/2024/11/the-financial-stability-implications-of-artificial-intelligence/
   - Supplies institutional motivation for studying AI-related correlated behavior and information gaps. It does not validate this model, diagnostic, or any practical deployment claim.

## Additional relevant leads requiring deeper comparison before submission

- Regularized Identification with Internal Positivity Side-Information (M. Khosravi; final SIAM article 2025, DOI 10.1137/23M1556095). This could supply stronger nonparametric identification comparators.
- A Schur/Nevanlinna or convex moment-feasibility method could tighten the current geometric bounds. The current bounds are not claimed optimal for all observed moments.
- Georges–Pereira, classic heterogeneous-belief models, and conventional liquidity feedback should be addressed with finance-specific experiments before interpreting the result as uniquely an AI effect.

## Search families used

“adaptive financial agents system identification randomized learning freeze intervention”; “adaptive expectations financial market feedback stability asynchronous updating”; “market learning Markov parameters”; “financial feedback system identification perturbation”; “Ho Kalman Markov parameters”; “slow modes finite system identification stability”; “positive systems DC gain stability feedback”; “truncated moment identification linear systems”; “market stability moment learning rates”; “Scalable Identification of Stable Positive Systems”.

## Novelty verdict

**A specific, reproducible candidate contribution has been developed; global priority is unresolved.** The mathematical ingredients are established. Before claiming an original journal contribution, a finance/control reviewer should check whether the exact finite-horizon stable/unstable construction and the rate-aware identification contract already appear in positive realization, moment-problem, or heterogeneous-agent finance research. If they do, reposition this as a replication/translation benchmark or derive a genuinely new economic or statistical extension rather than rename known theory.
