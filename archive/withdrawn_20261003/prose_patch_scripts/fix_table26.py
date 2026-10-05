import re

with open('paper/Machine_Markets_Final_Integrated_Paper.tex', 'r') as f:
    content = f.read()

# Change Table 26 tabularx definition to give more room to the Script column
old_table = r"\begin{tabularx}{\textwidth}{>{\raggedright\arraybackslash}p{.20\textwidth}>{\raggedright\arraybackslash}p{.18\textwidth}>{\raggedright\arraybackslash\ttfamily\footnotesize}X>{\raggedright\arraybackslash\ttfamily\footnotesize}p{.32\textwidth}}"
new_table = r"\begin{tabularx}{\textwidth}{>{\raggedright\arraybackslash}p{.17\textwidth}>{\raggedright\arraybackslash}p{.15\textwidth}>{\raggedright\arraybackslash\ttfamily\footnotesize}p{.38\textwidth}>{\raggedright\arraybackslash\ttfamily\footnotesize}X}"
content = content.replace(old_table, new_table)

with open('paper/Machine_Markets_Final_Integrated_Paper.tex', 'w') as f:
    f.write(content)
print("Table 26 updated.")
