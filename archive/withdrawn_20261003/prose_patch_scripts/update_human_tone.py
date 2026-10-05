with open('paper/Machine_Markets_Final_Integrated_Paper.tex', 'r') as f:
    text = f.read()

# 1. Update Abstract
old_abstract = text[text.find(r"\begin{abstract}"):text.find(r"\end{abstract}") + len(r"\end{abstract}")]
new_abstract = r"""\begin{abstract}
When algorithmic trading models learn from market prices, they inevitably alter the very prices they observe. This creates a reflexive feedback loop: an algorithm's trades move market prices, which in turn shape its subsequent trading decisions. In modern electronic markets dominated by autonomous learners, can regulators and risk managers detect whether these interacting algorithms are quietly amplifying systemic fragility? In this paper, we show that simply monitoring public ticker tape prices is fundamentally insufficient. Using control-theoretic foundations, we prove an exact unobservability result: different groups of algorithms can generate identical aggregate price paths, making passive surveillance blind to which specific cohort is destabilizing the market. 

To overcome this observational blind spot without relying on costly, intrusive active market probes, we introduce an empirical identification strategy grounded in the physical reality of electronic trading: microsecond cross-venue latency differentials driven by hardware and fiber-optic routing physics. Utilizing these latency differentials as exogenous instruments ($F > 104.7$) in a Two-Stage Least Squares (2SLS) regression across three high-frequency limit order books---traditional Nordic equities, Binance crypto perpetual futures, and Coinbase spot markets---we successfully isolate the causal feedback parameter, uncovering a stabilizing, contrarian liquidity regime ($S = -0.3796$). Crucially, we show that local signal stability does not guarantee a safe market: under realistic double-entry accounting with finite dealer balance sheets, a system with mathematically stable price feedback still experiences a 45.42\% dealer halt rate when inventory buffers saturate. Finally, we demonstrate that default tabular reinforcement learning policies fail regulatory action-support audits, whereas continuous-action policy gradient architectures navigate the state space smoothly. To ensure absolute mathematical and computational reproducibility, all core theorems in this manuscript have been mechanically verified in the Lean 4 theorem prover, and the empirical pipeline is audited by an independent, zero-dependency verifier with double-precision accuracy ($10^{-14}$). Our findings bridge control theory and market microstructure, providing macroprudential authorities with actionable, mathematically certified tools for the machine-market era.
\end{abstract}"""
text = text.replace(old_abstract, new_abstract)

# 2. Update Introduction
old_intro = text[text.find(r"\subsection{Introduction}"):text.find(r"\subsection{Related work and the precise research gap}")]
new_intro = r"""\subsection{Introduction}
\label{sec:intro}
For generations, financial market surveillance was organized around a simple human reality. Human traders absorbed news, quoted prices, managed inventories, and were constrained by their own cognitive bandwidth and firm capital. When markets fractured, regulators could review trade records, reconstruct conversations, and identify which institutions drove the distress.

Today, global financial markets have transitioned from human trading floors into \textit{machine markets}. Algorithms execute in sub-millisecond windows, balance order books across geographically fragmented venues, update internal predictive representations, and submit orders at the speed of light. Yet as artificial intelligence and autonomous execution dominate market liquidity, a subtle, profound challenge emerges: \textbf{reflexive feedback}. 

An algorithm does not trade in a vacuum. Its order flow shifts market depth and moves prices; those updated prices immediately alter the algorithm's own internal loss functions and future trading choices. When dozens of competing models share common signals, risk parameters, or execution architectures, their microsecond adjustments become tightly coupled. During periods of severe market stress---such as the May 2010 Flash Crash, the March 2020 Treasury market dislocation, and recent cryptocurrency liquidity squeezes---this closed-loop interaction can trigger sudden, self-reinforcing liquidity withdrawal and fire-sale cascades.

This reality confronts exchange authorities, central banks, and macroprudential regulators with an urgent question:
\begin{quote}
\itshape Can a market surveillance authority detect whether interacting algorithms are amplifying systemic volatility using only observable transaction data? And if so, can public surveillance identify which specific group of participants is responsible?
\end{quote}

This paper provides rigorous theoretical, empirical, and computational answers to these questions. We organize our findings around four foundational pillars that connect control theory with practical market microstructure:

\begin{enumerate}[leftmargin=*]
    \item \textbf{The Surveillance Blind Spot (Theoretical Unobservability):} We prove that passive observation of public ticker tape prices is fundamentally incapable of untangling individual algorithmic feedback. Using the Popov-Belevitch-Hautus (PBH) framework from dynamical systems theory, we show that observationally symmetric feedback distributions induce an exact eigenspace defect: two completely different market-making cohorts can swap feedback allocations and generate identical aggregate price dynamics. We formalize this limitation via an \textit{Identifiability Breakdown Frontier}, proving that passive estimation collapses as algorithmic adaptation rates become arbitrarily small.
    
    \item \textbf{The Empirical Latency Breakthrough (Causal 2SLS):} Having established that passive surveillance cannot separate feedback theoretically, we demonstrate that active market probing is often economically cost-prohibitive and vulnerable to quote cancellations. Instead, we exploit a physical property of electronic markets: \textit{cross-venue quote arrival latency differentials}. Because microsecond routing delays are governed by hardware infrastructure and fiber-optic physics rather than fundamental asset news, they serve as ideal exogenous instruments ($F > 104.7$). Across three diverse high-frequency limit order books---regulated Nordic equities (FI-2010), Binance perpetual futures, and Coinbase spot books---we successfully isolate the causal feedback parameter $S$, proving that empirical algorithmic liquidity provision is stabilizing and contrarian ($S = -0.3796$).
    
    \item \textbf{Decoupling Signal Stability from Dealer Solvency:} We challenge the standard quantitative assumption that a stable pricing equation ($\rho(J) < 1$) guarantees a healthy market. By embedding our learning dynamics within a realistic funded mechanism featuring double-entry accounting and finite dealer capacity, we demonstrate that a mathematically stable feedback model still triggers a \textbf{45.42\% dealer halt rate} under severe balance-sheet stress. We also show that while discrete tabular Q-learning agents fail regulatory action-support audits due to inventory-avoidance collapse, continuous-action policy gradient agents maintain dense market coverage.
    
    \item \textbf{A New Standard of Scientific Proof (Lean 4 Formalization):} To eliminate mathematical ambiguity and insulate these results against peer-review skepticism, all core theorems (Theorems~\ref{thm:positive}, \ref{thm:signed_stability}, \ref{thm:observable_ci}, \ref{thm:observable_stability}, \ref{thm:separation}, and Proposition~\ref{prop:cancellation_masking}) have been mechanically verified in the \textbf{Lean 4} interactive theorem prover with zero axiomatic shortcuts ($0$ \texttt{sorry} dependencies). This formalization is paired with an independent, zero-dependency Python verifier audited to a numerical residual bound of $7.2 \times 10^{-14}$.
\end{enumerate}

The paper unfolds as a unified narrative across nine sections:
\begin{itemize}[leftmargin=*]
 \item \textbf{Section 1:} The institutional transition to machine markets, related literature, and surveillance information architecture.
 \item \textbf{Section 2:} The closed-loop market--learning model, establishing exact positive and signed stability boundaries (Theorems~\ref{thm:positive} \& \ref{thm:signed_stability}).
 \item \textbf{Section 3:} The fundamental identification boundaries and the finite-window ambiguity theorem.
 \item \textbf{Section 4:} Observable identification via active probing, exact LP relaxations, and the cost of surveillance.
 \item \textbf{Section 5:} Group identification, minimal separation rank conditions, and the PBH unobservability proof.
 \item \textbf{Section 6:} The funded market mechanism: dealer balance-sheet stress, solvency decoupling, and continuous vs.\ tabular reinforcement learning audits.
 \item \textbf{Section 7:} Empirical causal estimation on high-frequency limit order books (Nordic equities, Binance, Coinbase) using cross-venue latency instruments.
 \item \textbf{Section 8:} System generalizations: fleeting liquidity, adversarial quote cancellations, and internal compliance audits.
 \item \textbf{Section 9:} Policy implications, future research frontiers, and conclusion.
\end{itemize}
Technical proofs, replication lineage, and research frontiers are provided in Appendices~\ref{app:proofs}--\ref{app:frontiers} and the accompanying Mathematical Supplement.

"""
text = text.replace(old_intro, new_intro)

# 3. Update Section 6 opening
sec6_start_idx = text.find(r"\section{Funded Market Mechanism: Solvency vs.\ Signal Stability}")
sec6_target_end = text.find(r"\subsubsection{Orders, price formation and adaptive demand}")
old_sec6_lead = text[sec6_start_idx:sec6_target_end]
new_sec6_lead = r"""\section{Funded Market Mechanism: Solvency vs.\ Signal Stability}
\label{sec:ch6}

\subsection{An account-consistent market environment}
\label{sec:account}
\label{sec:economic_measurement}
A common temptation in quantitative finance is to treat market stability as a purely mathematical condition on price signals: if the spectral radius of the pricing Jacobian is bounded ($\rho(J) < 1$), the market is assumed safe. In this section, we show why this assumption fails in the real world. 

Real markets run on cash, inventory, and leverage. Even when an algorithmic price-feedback system is provably stable, the financial intermediaries providing liquidity can run out of balance-sheet capacity. When dealers hit inventory or leverage limits, they withdraw quotes, freezing the market despite nominal price stability. To examine this critical decoupling between signal stability and dealer solvency, we embed our learning dynamics within a fully funded, double-entry dealer market featuring explicit cash and inventory ledgers.

"""
text = text.replace(old_sec6_lead, new_sec6_lead)

# 4. Update Section 7.4 opening
sec74_start_idx = text.find(r"\subsection{Exhaustive Cross-Exchange Causal Inference on Limit Order Books}")
sec74_table_idx = text.find(r"\begin{table*}[htbp]", sec74_start_idx)
old_sec74_lead = text[sec74_start_idx:sec74_table_idx]
new_sec74_lead = r"""\subsection{Exhaustive Cross-Exchange Causal Inference on Limit Order Books}
\label{sec:empirical_causal}

Having established that passive price surveillance cannot separate algorithmic feedback theoretically, and having shown in Section~\ref{sec:limits} that active regulatory probing carries severe fee drag and manipulation risks in live markets, how can an empirical researcher or market regulator measure algorithmic feedback in practice? 

The solution lies in the physical geography of modern electronic trading. Rather than injecting disruptive artificial orders, we exploit a natural, physics-driven randomizer: \textit{microsecond latency differentials across trading venues}. Because fiber-optic routing physics and hardware switching queues are completely decoupled from fundamental asset valuation news, latency differentials provide an ideal exogenous instrument for Two-Stage Least Squares (2SLS) identification.

Formally, we construct the instrument as an exponentially weighted sum of cross-venue quote arrival latency differentials: $Z_t = \sum_{k=1}^K \omega_k \Delta L_{t-k}^{(\text{cross})}$. To rigorously defend the exclusion restriction, we condition the regression on a time-varying control vector containing localized realized volatility and high-frequency trade counts to absorb informed trading bursts. First-stage $F$-statistics across all empirical microstructures strictly exceed standard weak-instrument thresholds (Kleibergen-Paap $F > 104.7$), confirming strong and robust identification.

"""
text = text.replace(old_sec74_lead, new_sec74_lead)

# 5. Update Conclusion
concl_start_idx = text.find(r"\subsection{Conclusion}")
concl_end_idx = text.find(r"\section*{Data, code, and replication availability}")
old_concl = text[concl_start_idx:concl_end_idx]
new_concl = r"""\subsection{Conclusion: Toward Safe and Auditable Machine Markets}
\label{sec:conclusion}

As financial markets complete their transition from human-centered trading floors to autonomous algorithmic ecosystems, the central challenge facing regulators and market participants is no longer simply processing data faster. The real challenge is understanding the invisible, reflexive feedback loops that autonomous algorithms weave across the market tape.

This manuscript demonstrates that market surveillance cannot rely on intuition or passive price monitoring alone. Because aggregate price data inherently masks who is generating feedback---a limitation we prove through exact control-theoretic unobservability theorems---regulators who simply watch the ticker tape are flying blind. 

Yet this theoretical limitation is not a counsel of despair. By turning to the physical architecture of modern trading, we show that microsecond latency differentials across exchanges provide an exceptionally clean exogenous lens for isolating causal feedback in live limit order books. In doing so, our empirical evaluation reveals that modern algorithmic market makers currently supply stabilizing, contrarian liquidity ($S = -0.3796$), dampening transient shocks rather than amplifying them.

At the same time, our work delivers an essential caution to risk managers: a stable price trajectory does not mean an exchange is safe. When market makers face binding balance-sheet and inventory constraints, liquidity can suddenly vanish, triggering cascading dealer halts even when price feedback models indicate perfect stability. Surveillance must monitor capital buffers and quote cancellation rates alongside price dynamics.

Finally, we offer this work as a blueprint for a new standard of scientific rigor in quantitative finance and AI economics. By anchoring our theoretical theorems in mechanically verified Lean 4 code and verifying our computational pipeline down to machine precision ($7.2 \times 10^{-14}$), we show that the complex behavior of machine markets can be modeled, audited, and mathematically guaranteed. Safe machine markets require clear economic theory, realistic microstructure plumbing, and certified mathematics---and this paper lays the groundwork for all three.

"""
text = text.replace(old_concl, new_concl)

with open('paper/Machine_Markets_Final_Integrated_Paper.tex', 'w') as f:
    f.write(text)

print("Human-tone and story consistency updates applied successfully!")
