import re

def fix_longtable(filepath):
    with open(filepath, 'r') as f:
        content = f.read()

    # We will replace the whole longtable with a table* + tabularx
    
    old_start = r'\begin{longtable}{>{\raggedright\arraybackslash}p{0.24\textwidth}>{\raggedright\arraybackslash}p{0.69\textwidth}}'
    new_start = r'''\begin{table*}[htbp]
\centering\small
\caption{Methodological scope and open research frontiers.}\label{tab:research_gates}
\begin{tabularx}{\textwidth}{>{\raggedright\arraybackslash}p{0.24\textwidth}X}'''

    content = content.replace(old_start, new_start)
    
    # We must also remove the \caption inside the old longtable, and the headers
    old_headers = r'''\caption{Methodological scope and open research frontiers.}\label{tab:research_gates}\\
\toprule
Research Dimension & Current Scientific Verification and Open Frontiers \\
\midrule
\endfirsthead
\toprule Research Dimension & Current Scientific Verification and Open Frontiers \\ \midrule
\endhead'''
    
    new_headers = r'''\toprule
\textbf{Research Dimension} & \textbf{Current Scientific Verification and Open Frontiers} \\
\midrule'''
    
    content = content.replace(old_headers, new_headers)
    
    old_end = r'\end{longtable}'
    new_end = r'''\end{tabularx}
\end{table*}'''
    
    content = content.replace(old_end, new_end)

    with open(filepath, 'w') as f:
        f.write(content)

fix_longtable('paper/Machine_Markets_Final_Integrated_Paper.tex')
