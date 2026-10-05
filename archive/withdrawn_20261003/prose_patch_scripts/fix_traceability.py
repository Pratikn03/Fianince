import re

with open('paper/Machine_Markets_Final_Integrated_Paper.tex', 'r') as f:
    content = f.read()

# Update Table 26 by inserting Lean 4 rows before the bottomrule
old_table_end = r"""Q-Learning Abstention & Section~\ref{sec:q_learning_transfer} & \nolinkurl{tests/test_q_learning_transfer.py} & \nolinkurl{test_model_class_audit()} \\
\bottomrule"""

new_table_end = r"""Q-Learning Abstention & Section~\ref{sec:q_learning_transfer} & \nolinkurl{tests/test_q_learning_transfer.py} & \nolinkurl{test_model_class_audit()} \\
\midrule
\multicolumn{4}{l}{\textbf{Lean 4 Mechanized Proofs (Exact Arithmetic via \texttt{Init.Grind})}} \\
\midrule
Positive-Feedback Boundary & Theorem~\ref{thm:spectral_radius} & \nolinkurl{lean_proofs/Proofs/Stability.lean} & \nolinkurl{theorem charPoly_at_one_identity} \\
PBH Rank Defect & Prop 5.1 \& Thm 5.2 & \nolinkurl{lean_proofs/Proofs/PBHDefect.lean} & \nolinkurl{theorem pbh_eigenvector_x} \\
Observable Bounds & Theorem 4.1 \& 4.2 & \nolinkurl{lean_proofs/Proofs/Bounds.lean} & \nolinkurl{theorem exact_outer_bound} \\
\bottomrule"""

content = content.replace(old_table_end, new_table_end)

with open('paper/Machine_Markets_Final_Integrated_Paper.tex', 'w') as f:
    f.write(content)
