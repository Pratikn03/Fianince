import re

with open('paper/Machine_Markets_Final_Integrated_Paper.tex', 'r') as f:
    content = f.read()

# Fix the Theorem labels in the Lean 4 section of Table 26
content = content.replace(r"Theorem~\ref{thm:spectral_radius}", r"Theorem~\ref{thm:positive}")
content = content.replace(r"Prop 5.1 \& Thm 5.2", r"Prop~\ref{prop:swapped_feedback} \& Thm~\ref{thm:separation}")
content = content.replace(r"Theorem 4.1 \& 4.2", r"Theorems~\ref{thm:observable_ci} \& \ref{thm:observable_stability}")

# And let's fix the intro bullet point which hardcodes theorem numbers, just to be safe
# But actually hardcoded numbers like "Theorems 2.3, 3.3, 4.1, 4.2, 5.2" in the intro/appendix E are okay if they match the PDF output.
# I'll just fix Table 26 because the '\ref' will automatically pull the correct numbers.

with open('paper/Machine_Markets_Final_Integrated_Paper.tex', 'w') as f:
    f.write(content)
