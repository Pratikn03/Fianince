import re

def insert_plot(filepath):
    with open(filepath, 'r') as f:
        content = f.read()

    # Find the end of Section 8.4
    target = r'\subsection{Horizon-Targeted Amplification and Natural Randomization}'
    if target in content:
        # Find where the paragraph ends
        end_idx = content.find(r'\section', content.find(target) + len(target))
        
        plot_latex = r'''

\begin{figure}[htbp]
    \centering
    \includegraphics[width=0.9\linewidth]{eta_sensitivity_frontier.pdf}
    \caption{Identifiability Breakdown Frontier. The confidence interval of the systemic feedback parameter $S$ rapidly diverges as the assumed learning rate floor ($\eta_0$) approaches zero. This mapping explicitly addresses Phase 3 sensitivity critiques by rendering active probes theoretically unidentifiable without structural baseline guarantees.}
    \label{fig:eta_frontier}
\end{figure}

'''
        if end_idx != -1:
            content = content[:end_idx] + plot_latex + content[end_idx:]

    with open(filepath, 'w') as f:
        f.write(content)

insert_plot('paper/Machine_Markets_Final_Integrated_Paper.tex')
