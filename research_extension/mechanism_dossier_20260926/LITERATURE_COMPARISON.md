# Closest-work challenge, not novelty clearance

Reading date: 2026-09-26 local project date. This is a claim-driven bounded
review. The coverage column distinguishes reading an abstract from examining
a mechanism or appendix. No full systematic review is claimed. Sources remain
at their authorized publisher/author locations; third-party PDFs are not
redistributed in this dossier.

## Comparison matrix

| Primary source and version | What is already established or examined there | Exact relation to our finite example | Reading completed in this pass; unresolved work |
|---|---|---|---|
| [Colliard, Foucault and Lovo, *Algorithmic Pricing and Liquidity in Securities Markets*, RFS hhag010, 2026](https://academic.oup.com/rfs/advance-article/doi/10.1093/rfs/hhag010/8489056) | Learning market makers; endogenous algorithm parameters; an informed dealer's accommodation of a learning rival | Our high-quote experience changes the rival's later policy: strong teaching/accommodation overlap. Our owner makes one ex-ante early/wait choice, without conditioning on the rival's current realized quote; welfare is exactly computed over two periods. Those restrictions do not by themselves establish novelty. | Parallel reviewer read IA.6 prose pp.17-19 and captions through p.21; accommodation rule p.18, Figure IA.8 p.21; selected main §§6.1-6.2. Not the complete article or supplement; plotted curves not independently reproduced. Full equivalence/priority assessment pending. |
| [Brown and MacKay, *Competition in Pricing Algorithms*, AEJ: Microeconomics 15(2), 109-156, 2023](https://alexandermackay.org/files/Competition%20in%20Pricing%20Algorithms%20%28Published%29.pdf) | Pricing frequency, commitment, endogenous technology adoption and softened competition | A release menu is narrower than their technology/algorithm choices. Our sampled reward update and matched learning-off contrast identify a different formal experiment; a generic adoption incentive difference is not new. | Introduction; §II.E pp.133-134; Appendix A text pp.150-152; Proposition 4 statement/proof p.138. Remaining model proofs, Appendix B and online appendices not completely reviewed. |
| [Hansen, Misra and Pai, *Frontiers: Algorithmic Collusion: Supra-competitive Prices via Independent Algorithms*, Marketing Science 40(1), 1-12, 2021](https://pubsonline.informs.org/doi/10.1287/mksc.2020.1276) | Misspecified learners can run correlated price experiments, affecting inferred price sensitivity | Our example does not estimate a demand slope and does not establish misspecified inference or correlated experimentation. Shared outcomes are not enough to claim the same statistical channel. | Official abstract and bibliographic record only. Full derivation and supplement pending. |
| [Conjeaud, Abel and Kalogeratos, *Algorithmic collusion under asynchronous price updating*, arXiv:2608.01406v1, submitted 2 August 2026](https://arxiv.org/abs/2608.01406v1) | Q-learning price setters with Poisson update clocks; simulated collusion depends on timing and information | Our single early/scheduled refresh decision is not their continuous-time update experiment. We cannot claim asynchronous pricing is an unstudied topic. | Official metadata and abstract only; main specification and appendices pending. |
| [Perdomo, Zrnic, Mendler-Dunner and Hardt, *Performative Prediction*, ICML/PMLR 119, 7599-7609, 2020](https://proceedings.mlr.press/v119/perdomo20a.html) | Decisions affect future data distributions; retraining stability and performance conditions | Our outcome is dealer/customer allocation and welfare, not predictive-risk optimality. Endogenous learning data alone is not a new contribution. | Official abstract and record only in this pass; relevant proofs and supplement pending. |
| [Wang, Yau and Wai, *Network Effects in Performative Prediction Games*, ICML/PMLR 202, 36514-36540, 2023](https://proceedings.mlr.press/v202/wang23ap.html) | Multiplex multi-agent performative games, equilibrium and network effects | A later group-network extension must compare with this work. Two coupled layers and endogenous data do not establish novelty by combination. | Official abstract and record only; model, proofs and appendices pending. |
| [Zhao and Sayed, *Asynchronous Adaptation and Learning over Networks—Part I: Modeling and Stability Analysis*, arXiv:1312.5434v3, revised 16 December 2014](https://arxiv.org/abs/1312.5434v3) | Asynchronous cooperative adaptation and mean-square stability | Relevant mathematical background; **not** a paper about algorithmic pricing. It cannot substitute for the Conjeaud comparison. | Official abstract and metadata; main paper and appendices not read in this pass. |
| [Glosten and Milgrom, *Bid, ask and transaction prices in a specialist market with heterogeneously informed traders*, JFE 14(1), 71-100, 1985](https://doi.org/10.1016/0304-405X(85)90044-3) | Adverse selection, information in transactions, and dealer spreads | The finite ask-only two-dealer model is a different contract, not a replication of their specialist equilibrium. We report asks, not a bid-ask spread. | Official bibliographic/abstract check only in this pass; complete foundational reading remains a separate requirement. |

## Corrections to the historical source registry

The preserved research-worktree `studies/learning_spillovers_v12/literature.json`
has at least four inaccurate titles/classifications:

1. CFL's supplied DOI resolves to *Algorithmic Pricing and Liquidity in
   Securities Markets*, not *Algorithmic Trading and Market Quality*.
2. The Hansen-Misra-Pai DOI is the specific *Frontiers* paper above, not
   *Algorithmic Collusion: A Research Agenda*.
3. arXiv:1312.5434 is Zhao-Sayed network adaptation, not asynchronous pricing.
4. The Wang-Yau-Wai title is *Network Effects in Performative Prediction Games*,
   not *Networked Prediction Games*.

This dossier supplies corrected records without silently editing the old
registry or altering its historical reading claims. Those corrections should
be incorporated explicitly when a future manuscript revision is authorized.

## What can be said now

The result is an exactly calculable, restricted example of reward-mediated
strategic accommodation with a private/social deployment difference. The
current distinction is finite-horizon tractability, limited deployment choice,
explicit welfare and matched interventions. Whether those differences yield a
substantive new contribution is unresolved. The discovery does not establish
damaged estimate accuracy, general synchronized-agent fragility, or a novel
teaching mechanism.

## Next novelty decision

The immediate comparison is to CFL IA.6: determine whether our information and
one-shot commitment restrictions remove a premise essential to their mechanism,
and whether the resulting welfare characterization is economically useful beyond
a special case. Compare the cost threshold with Brown-MacKay's adoption logic.
Do this before expensive training. If the distinction is only another numerical
example of known accommodation, retain it as a benchmark and narrow the proposed
headline contribution. Independent human priority review remains pending.
