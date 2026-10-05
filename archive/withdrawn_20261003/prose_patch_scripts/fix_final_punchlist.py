import re

filepath = 'paper/Machine_Markets_Final_Integrated_Paper.tex'
with open(filepath, 'r') as f:
    content = f.read()

# Fix 1: Remove the rogue \appendix command on line 2174
content = re.sub(r'\\clearpage\s*\\appendix\s*\\section\{Computational Verification', r'\\clearpage\n\\section{Computational Verification', content)
# Just in case there's no clearpage before it:
content = re.sub(r'\\appendix\s*\\section\{Computational Verification', r'\\section{Computational Verification', content)

# Fix 2: Fix Table 25
table_preamble_old = r'\begin{tabularx}{\textwidth}{>{\raggedright\arraybackslash}p{.18\textwidth}>{\raggedright\arraybackslash}p{.20\textwidth}>{\raggedright\arraybackslash}X>{\raggedright\arraybackslash}p{.26\textwidth}}'
table_preamble_new = r'\begin{tabularx}{\textwidth}{>{\raggedright\arraybackslash}p{.20\textwidth}>{\raggedright\arraybackslash}p{.18\textwidth}>{\raggedright\arraybackslash\ttfamily\footnotesize}X>{\raggedright\arraybackslash\ttfamily\footnotesize}p{.32\textwidth}}'
content = content.replace(table_preamble_old, table_preamble_new)

# We need to remove the `{\small \path{...}}` wrapping because the columns 3 and 4 are now `\ttfamily\footnotesize` by default.
# But wait, \ttfamily doesn't line break well on underscores. The user suggested `\nolinkurl{}`.
# Let's replace `{\small \path{...}}` with `\nolinkurl{...}`

content = content.replace(r'{\small \path{tests/test_group_identification.py}}', r'\nolinkurl{tests/test_group_identification.py}')
content = content.replace(r'{\small \path{test_separation_conditions()}}', r'\nolinkurl{test_separation_conditions()}')

content = content.replace(r'{\small \path{reference_directory/run_checks.py}}', r'\nolinkurl{reference_directory/run_checks.py}')
content = content.replace(r'{\small \path{check_pbh_defect()}}', r'\nolinkurl{check_pbh_defect()}')

content = content.replace(r'{\small \path{mm_revision/tests/test_conic.py}}', r'\nolinkurl{mm_revision/tests/test_conic.py}')
content = content.replace(r'{\small \path{test_recurrence_lp_bounds()}}', r'\nolinkurl{test_recurrence_lp_bounds()}')
content = content.replace(r'{\small \path{test_conic_relaxation()}}', r'\nolinkurl{test_conic_relaxation()}')

content = content.replace(r'{\small \path{independent_verifier/verifier.py}}', r'\nolinkurl{independent_verifier/verifier.py}')

content = content.replace(r'{\small \path{tests/test_funded_mechanism.py}}', r'\nolinkurl{tests/test_funded_mechanism.py}')
content = content.replace(r'{\small \path{test_solvency_boundary()}}', r'\nolinkurl{test_solvency_boundary()}')

content = content.replace(r'{\small \path{tests/test_q_learning_transfer.py}}', r'\nolinkurl{tests/test_q_learning_transfer.py}')
content = content.replace(r'{\small \path{test_model_class_audit()}}', r'\nolinkurl{test_model_class_audit()}')

# Also fixing the header to not be ttfamily
header_old = r'\textbf{Computational Environment} & \textbf{Validation Target}'
header_new = r'\normalfont\textbf{Computational Environment} & \normalfont\textbf{Validation Target}'
content = content.replace(header_old, header_new)

with open(filepath, 'w') as f:
    f.write(content)
