# Contribution challenge: teaching, accommodation, and deployment

Internal AI-assisted reading and synthesis, 2026-09-27 UTC. Not independent
human review or a complete literature/appendix review. The earlier sealed
comparison remains unchanged; this note adds two close predecessors.

## Scoped primary-source comparison

| Source/version | Reading performed by the literature reviewer | What overlaps; what remains different |
|---|---|---|
| Colliard–Foucault–Lovo, *Algorithmic Pricing and Liquidity in Securities Markets*, RFS hhag010, published 17 February 2026 | Complete main §§3.1–3.2, 6.1–6.2; complete supplement IA.5–IA.6, printed pp.15–21, including captions and footnotes; visual inspection of IA.6–IA.8. No numerical replication. | Own-profit feedback and selected-action updates are already present. IA.6 uses profit-sharing accommodation to influence later quoting. Its controller uses current rival quotes/Q-values and can intervene repeatedly. Our owner makes one ex-ante choice with fixed subsequent algorithms. |
| Camerer–Ho–Chong, *Sophisticated Experience-Weighted Attraction Learning and Strategic Teaching in Repeated Games*, JET 104(1), 137–188 (2002); NUS-hosted publisher proof dated 22 March 2002, internal pp.1–52 | Complete §2.1 (PDF pp.4–6); §2.2 opening (p.7); §4 introductory discussion and §4.1 (pp.25–31). Other empirical sections and AQRE appendix not reviewed. | Current play shaping subsequent learned behavior, including finite-horizon teaching, is established. Its trust-game implementation includes observational learning and repeated decisions; it is not our exact refresh menu. |
| Arslantas–Yuceel–Sayin, *Strategizing against Q-learners: A Control-theoretical Approach*, arXiv:2403.08906v3, 16 July 2024 | Complete §§I–II and Appendices A–C; selected §III recursions (9)–(10). No full-paper or numerical-replication claim. Main implementer separately checked §§I–II and selected §III. | Equation (2) updates only the chosen action from own payoff; strategic opponents alter those rewards through game actions. Softmax policies, ongoing control, observed joint actions and Q-state tracking differ. Our epsilon-greedy initialization discontinuity is not covered by their smooth-policy argument. |

Primary links: [CFL article and publisher supplement access](https://academic.oup.com/rfs/advance-article/doi/10.1093/rfs/hhag010/8489056);
[Camerer–Ho–Chong DOI](https://doi.org/10.1006/jeth.2002.2927),
[NUS-hosted proof](https://web2-bschool.nus.edu.sg/wp-content/uploads/media_rp/publications/FjC3x1466583103.pdf);
[Arslantas–Yuceel–Sayin v3](https://arxiv.org/html/2403.08906v3).
Publisher-signed temporary access links are not retained as durable citations.
No third-party article bytes are redistributed by this package.

## Verdict

The information/control restriction is real, but limited learner feedback must
not be confused with an uninformed owner: the owner knows the law, initial
tables and algorithm contract. In this example its single deployment decision
selects a first-period quote lottery; its second-period policy is the same under
both choices. This is a restricted prospective teaching intervention, not a
separate mechanism merely because it is implemented through refresh timing.

The useful exact result is the private/social ranking reversal after counting
customer surplus and cancelling transfers. The examined sections did not reveal
this exact refresh-and-welfare proposition. That observation is bounded by the
reading scope and is not a priority claim. The effect relies on a tied initial
shadow state and on the allocation consequences of a statically dominated ask.

## Permitted positioning

We give an exactly computed two-period example of reward-mediated strategic
accommodation under a restricted deployment menu. An informed owner chooses
early versus scheduled refresh once, with fixed downstream algorithms. At the
specified initial state, early refresh increases expected private profit and
reduces expected total surplus. Those two gross contrasts vanish when rival
learning is frozen. The example builds on strategic-teaching mechanisms; it
does not establish that a new mechanism has been discovered.

Do not claim: first learning externality; novelty from own-reward feedback or
finite horizon; corrupted reward estimates; universal welfare harm; trained-
population prevalence; operational systemic risk; or novelty certified by Lean.

## Next research gate

Before a large training study, determine whether a meaningful economic claim
survives non-tied initialization and a second, smooth learning rule, and whether
it yields a useful characterization rather than another teaching example.
Those changes need a separately specified model and falsifiable prediction.
The current counterexample must remain visible whichever direction is chosen.
