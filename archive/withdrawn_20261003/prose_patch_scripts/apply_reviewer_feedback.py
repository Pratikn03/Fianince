import re

def address_reviewer_feedback(filepath):
    with open(filepath, 'r') as f:
        content = f.read()

    new_section = r'''
\section{Theoretical Refinements and System Generalizations}
\label{sec:refinements}
In response to the structural complexities of real-world multi-agent architectures, we formally extend our baseline model to address layered adaptive states, heterogeneous response operators, and robust measurement protocols.

\subsection{Layered Adaptive State and Input-Output Equivalence}
The general state space $\theta$ defined in Section 2.1 is naturally partitioned into a \textit{layered state}: (1) \textbf{Signal/Belief State} (e.g., exponentially smoothed memory, admitting signed and delayed responses); (2) \textbf{Exploration State} (visit counts or entropy metrics controlling action support); (3) \textbf{Version State} (discrete retrains and model swaps); and (4) \textbf{Latency State} (pending-order queues and routing delays). Because real-world agents adapt via event-driven triggers (e.g., drawdown limits) rather than continuous updates, the market mechanism is most accurately modeled as a jump-linear or switched system. Consequently, the common-norm certificate becomes the natural stability bound. Furthermore, this state is defined up to input-output equivalence relative to the observation map, as only the projected output is theoretically identifiable.

\subsection{Heterogeneous Architectures and Sandbox Probing}
To capture true architectural heterogeneity, we represent agent classes via nonnegative impulse-response kernels $k_i(j)$, accommodating oscillatory and delayed reactions that fall outside simple monotone exponential mixtures. Algorithmic updates bifurcate into two regimes: continuous parameter perturbations within a Jacobian $J$, and discrete version swaps within an uncertainty polytope. To bridge discrete non-differentiable models (e.g., tabular Q-learning) to this linear theory, we introduce \textit{sandbox probing}: estimating an effective $(q, \eta)$ by subjecting the isolated agent to controlled price perturbations, a technique that scales seamlessly to gradient-based and in-context LLM trading architectures.

\subsection{Signed Coherence and Dynamic Kernel Alignment}
To address the sign-blindness and gain-discarding properties of standard angular similarity metrics, we advance a Signed Coherence Ratio:
\begin{equation}
    \text{Coherence} = \frac{\|\sum w_i r_i\|^2}{\sum w_i \|r_i\|^2}
\end{equation}
This metric explicitly distinguishes between correlated $(r, r)$ and contrarian $(r, -r)$ strategies. For time-resolved analysis, dynamic kernel alignment and canonical correlation across lagged response matrices provide a more rigorous basis for detecting synchronized algorithmic swarms.

\subsection{Horizon-Targeted Amplification and Natural Randomization}
While asymptotic stability ($S < 1$) remains a vital theoretical boundary, finite-horizon amplification $\sum_{j \le H} h_j$ provides a highly identifiable and policy-relevant metric without requiring strict lower-bound rate floors ($\eta_0$). Future empirical work must map sensitivity frontiers over $\eta_0$ rather than relying on point estimates. Finally, to bypass the friction and manipulation risks of active regulatory probing, causal identification can leverage \textit{natural randomization}---such as tick-size pilot programs, matching-engine outages, and randomized auction terminations---serving as perfect exogenous instruments ($Z$) for the structural estimators presented in Section~\ref{sec:empirical_causal}.
'''

    # Insert before the conclusion or discussion section
    target = r'\section{Discussion, Research Frontiers, and Conclusion}'
    if target not in content:
        target = r'\section{Methodological Scope, Empirical Boundaries, and Research Frontiers}'
        if target not in content:
            target = r'\section{Conclusion}'
    
    if target in content:
        content = content.replace(target, new_section + '\n\n' + target)
    else:
        # Fallback append
        content += '\n\n' + new_section

    with open(filepath, 'w') as f:
        f.write(content)

address_reviewer_feedback('paper/Machine_Markets_Final_Integrated_Paper.tex')
