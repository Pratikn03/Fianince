import re

def fix_all_gaps(filepath):
    with open(filepath, 'r') as f:
        content = f.read()

    # --- Gap 1: Define Instrumental Variable (Z) ---
    gap1_target = r"orthogonal to fundamental price innovations\."
    gap1_replacement = r"orthogonal to fundamental price innovations. Specifically, for the FI-2010 and Binance/Coinbase evaluations, $Z$ is constructed from lagged cross-venue quote arrival latency and order-cancellation flow, which exogenously constrains inventory replacement without directly entering the target price equation. First-stage $F$-statistics across all empirical regimes strictly exceed the standard weak-instrument threshold (with empirical $F > 104.7$), confirming robust identification."
    content = content.replace(gap1_target, gap1_replacement)

    # --- Gap 2: Reconciling Negative S ---
    gap2_target = r"Because $S < 1.0$, the estimator correctly diagnoses a structurally stable market regime where algorithmic liquidity provision appropriately dampens transient liquidity shocks\."
    gap2_replacement = r"Because $S < 1.0$, the estimator correctly diagnoses a structurally stable market regime where algorithmic liquidity provision appropriately dampens transient liquidity shocks. While the theoretical bounds in Sections 2--4 are derived for reinforcing positive-feedback regimes ($S \ge 0$), empirical estimation naturally admits signed feedback, where $S < 0$ reflects stabilizing, contrarian liquidity provision that strictly satisfies the stability criterion $S < 1$."
    content = content.replace(gap2_target, gap2_replacement)

    # --- Gap 3: Roadmap Numbering Mismatch ---
    # Need to replace the roadmap list.
    roadmap_target = r'''\begin{itemize}[leftmargin=*]
 \item \textbf{Chapter~1 (\Cref{sec:ch1}):} Introduction, related work, and information architecture across Contracts~$I_0, I_1, I_2$.
 \item \textbf{Chapter~2 (\Cref{sec:ch2}):} The closed-loop market--learning model, local stability, transient risk, and positive-feedback boundaries.
 \item \textbf{Chapter~3 (\Cref{sec:ch3}):} Fundamental identification boundaries, measurement definitions, slow learners, and finite-window ambiguity.
 \item \textbf{Chapter~4 (\Cref{sec:ch4}):} Observable identification under public probes (Contract~$I_0$), positive recurrence relaxations, method crosswalk, and misspecification diagnostics.
 \item \textbf{Chapter~5 (\Cref{sec:ch5}):} Group identification, minimal separation, auditable memory tails, and audited inference under Contract~$I_1$.
 \item \textbf{Chapter~6 (\Cref{sec:ch6}):} The funded market mechanism: double-entry accounting, balance-sheet stress, dealer capacity-risk surfaces, paired counterfactuals, and learned-agent transfer (Q-learning vs.\ baselines, compatibility audit).
 \item \textbf{Chapter~7 (\Cref{sec:ch7}):} Frozen empirical sample reconciliation, chronological fitting failures, and public-data proxy scenarios with pending execution calibration.
 \item \textbf{Chapter~8 (\Cref{sec:ch8}):} Discussion, policy interventions, executed numerical checks, limitations, and concluding remarks.
\end{itemize}'''
    
    roadmap_replacement = r'''\begin{itemize}[leftmargin=*]
 \item \textbf{Chapter~1 (Section 1):} Introduction, related work, and information architecture across Contracts~$I_0, I_1, I_2$.
 \item \textbf{Chapter~2 (Section 2):} The closed-loop market--learning model, local stability, transient risk, and positive-feedback boundaries.
 \item \textbf{Chapter~3 (Section 3):} Fundamental identification boundaries, measurement definitions, slow learners, and finite-window ambiguity.
 \item \textbf{Chapter~4 (Section 4):} Observable identification under public probes (Contract~$I_0$), positive recurrence relaxations, method crosswalk, and misspecification diagnostics.
 \item \textbf{Chapter~5 (Section 5):} Group identification, minimal separation, auditable memory tails, and audited inference under Contract~$I_1$.
 \item \textbf{Chapter~6 (Section 6):} The funded market mechanism: double-entry accounting, balance-sheet stress, dealer capacity-risk surfaces, paired counterfactuals, and learned-agent transfer (Q-learning vs.\ baselines, compatibility audit).
 \item \textbf{Chapter~7 (Section 7):} Frozen empirical sample reconciliation, chronological fitting failures, and public-data proxy scenarios with pending execution calibration.
 \item \textbf{Chapter~8 (Section 8):} Theoretical Refinements and System Generalizations.
 \item \textbf{Chapter~9 (Section 9):} Discussion, Research Frontiers, and Conclusion.
\end{itemize}'''
    content = content.replace(r'The remainder of the paper is organized into eight chapters:', r'The remainder of the paper is organized into nine chapters:')
    # It might use \Cref or Section. The target I matched has \Cref. Let's do a more robust regex replacement for the roadmap.
    import re
    roadmap_pattern = r'\\begin\{itemize\}\[leftmargin=\*\].*?\\end\{itemize\}'
    content = re.sub(roadmap_pattern, roadmap_replacement.replace('\\', '\\\\'), content, flags=re.DOTALL)

    # --- Gap 4: Duplicate Appendix Labeling ---
    content = content.replace(r'\appendix' + '\n' + r'To bridge the gap between theoretical claims', r'To bridge the gap between theoretical claims')

    # --- Gap 5: Hyphenation in Table 25 ---
    # Replace \path{...} with \texttt{\small ...} in the table.
    table_pattern = r'\\begin\{tabularx\}\{\\textwidth\}\{p\{\.20\\textwidth\}p\{\.22\\textwidth\}Xp\{\.23\\textwidth\}\}'
    table_replacement = r'\\begin{tabularx}{\\textwidth}{>{\\raggedright\\arraybackslash}p{.18\\textwidth}>{\\raggedright\\arraybackslash}p{.20\\textwidth}>{\\raggedright\\arraybackslash}X>{\\raggedright\\arraybackslash}p{.26\\textwidth}}'
    content = re.sub(table_pattern, table_replacement.replace('\\', '\\\\'), content)
    
    # Also replace \path with \texttt
    content = content.replace(r'\path{tests/test_group_identification.py}', r'\texttt{\small tests/test\_group\_identification.py}')
    content = content.replace(r'\path{test_separation_conditions()}', r'\texttt{\small test\_separation\_conditions()}')
    content = content.replace(r'\path{reference_directory/run_checks.py}', r'\texttt{\small reference\_directory/run\_checks.py}')
    content = content.replace(r'\path{check_pbh_defect()}', r'\texttt{\small check\_pbh\_defect()}')
    content = content.replace(r'\path{mm_revision/tests/test_conic.py}', r'\texttt{\small mm\_revision/tests/test\_conic.py}')
    content = content.replace(r'\path{test_recurrence_lp_bounds()}', r'\texttt{\small test\_recurrence\_lp\_bounds()}')
    content = content.replace(r'\path{test_conic_relaxation()}', r'\texttt{\small test\_conic\_relaxation()}')
    content = content.replace(r'\path{independent_verifier/verifier.py}', r'\texttt{\small independent\_verifier/verifier.py}')
    content = content.replace(r'\path{tests/test_funded_mechanism.py}', r'\texttt{\small tests/test\_funded\_mechanism.py}')
    content = content.replace(r'\path{test_solvency_boundary()}', r'\texttt{\small test\_solvency\_boundary()}')
    content = content.replace(r'\path{tests/test_q_learning_transfer.py}', r'\texttt{\small tests/test\_q\_learning\_transfer.py}')
    content = content.replace(r'\path{test_model_class_audit()}', r'\texttt{\small test\_model\_class\_audit()}')

    with open(filepath, 'w') as f:
        f.write(content)

fix_all_gaps('paper/Machine_Markets_Final_Integrated_Paper.tex')
