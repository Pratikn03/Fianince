import re

with open('paper/Machine_Markets_Final_Integrated_Paper.tex', 'r') as f:
    content = f.read()

old_sandbox = r"we introduce \textit{sandbox probing}: estimating an effective $(q, \eta)$ by subjecting the isolated agent to controlled price perturbations, a technique that scales seamlessly to gradient-based and in-context LLM trading architectures."
new_sandbox = r"we introduce \textit{sandbox probing}. Rather than suggesting external regulators inject probes into live markets, sandbox probing functions as an internal compliance audit---a stress-testing requirement that algorithmic trading firms must execute and certify in their own isolated development environments before deploying the model to live exchanges. This technique scales seamlessly to gradient-based and in-context LLM trading architectures."

content = content.replace(old_sandbox, new_sandbox)

with open('paper/Machine_Markets_Final_Integrated_Paper.tex', 'w') as f:
    f.write(content)
