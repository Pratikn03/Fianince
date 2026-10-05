with open('paper/Machine_Markets_Final_Integrated_Paper.tex', 'r') as f:
    content = f.read()

old_header = r'\normalfont\textbf{Computational Environment} & \normalfont\textbf{Validation Target}'
new_header = r'\textbf{Script / Environment} & \textbf{Validation Target}'
content = content.replace(old_header, new_header)

with open('paper/Machine_Markets_Final_Integrated_Paper.tex', 'w') as f:
    f.write(content)
