with open('paper/Machine_Markets_Final_Integrated_Paper.tex', 'r') as f:
    content = f.read()

target = r"dampens transient liquidity shocks."
replacement = r"dampens transient liquidity shocks. While the theoretical bounds in Sections 2--4 are derived for reinforcing positive-feedback regimes ($S \ge 0$), empirical estimation naturally admits signed feedback, where $S < 0$ reflects stabilizing, contrarian liquidity provision that strictly satisfies the stability criterion $S < 1$."

if target in content:
    content = content.replace(target, replacement)
    print("Successfully replaced Negative S.")
else:
    print("Could not find Negative S target.")

with open('paper/Machine_Markets_Final_Integrated_Paper.tex', 'w') as f:
    f.write(content)
