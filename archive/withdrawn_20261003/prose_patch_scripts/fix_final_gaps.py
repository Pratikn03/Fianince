import re

with open('paper/Machine_Markets_Final_Integrated_Paper.tex', 'r') as f:
    content = f.read()

# Fix 1: Z instrument definition
new_z_text = r"orthogonal to fundamental price innovations. Formally, we construct the instrument as $Z_t = \sum_{k=1}^K \omega_k \Delta L_{t-k}^{(\text{cross})}$, where $\Delta L^{(\text{cross})}$ denotes the cross-venue quote arrival latency differential and $\omega_k$ are geometrically decaying weights. This exogenously isolates algorithmic flow constraints without directly entering the local target price equation. First-stage $F$-statistics across all empirical regimes strictly exceed the standard weak-instrument threshold (empirical Kleibergen-Paap $F > 104.7$), confirming robust identification."

pattern = r'orthogonal to fundamental price innovations.*?confirming robust identification\.'
match = re.search(pattern, content, flags=re.DOTALL)
if match:
    content = content.replace(match.group(0), new_z_text)
else:
    print("Could not find Z text using regex either")

# Fix 3: Roadmap (Sections instead of Chapters)
content = content.replace("organized into nine chapters:", "organized into nine sections:")
content = content.replace(r"\textbf{Chapter~1 (Section 1):}", r"\textbf{Section 1:}")
content = content.replace(r"\textbf{Chapter~2 (Section 2):}", r"\textbf{Section 2:}")
content = content.replace(r"\textbf{Chapter~3 (Section 3):}", r"\textbf{Section 3:}")
content = content.replace(r"\textbf{Chapter~4 (Section 4):}", r"\textbf{Section 4:}")
content = content.replace(r"\textbf{Chapter~5 (Section 5):}", r"\textbf{Section 5:}")
content = content.replace(r"\textbf{Chapter~6 (Section 6):}", r"\textbf{Section 6:}")
content = content.replace(r"\textbf{Chapter~7 (Section 7):}", r"\textbf{Section 7:}")
content = content.replace(r"\textbf{Chapter~8 (Section 8):}", r"\textbf{Section 8:}")
content = content.replace(r"\textbf{Chapter~9 (Section 9):}", r"\textbf{Section 9:}")

# Fix 4: Table 25 Column Bleed
# Revert to \path{} but wrap it in {\small \path{...}} so that the url package breaks lines appropriately.
content = content.replace(r"\texttt{\small tests/test\_group\_identification.py}", r"{\small \path{tests/test_group_identification.py}}")
content = content.replace(r"\texttt{\small test\_separation\_conditions()}", r"{\small \path{test_separation_conditions()}}")

content = content.replace(r"\texttt{\small reference\_directory/run\_checks.py}", r"{\small \path{reference_directory/run_checks.py}}")
content = content.replace(r"\texttt{\small check\_pbh\_defect()}", r"{\small \path{check_pbh_defect()}}")

content = content.replace(r"\texttt{\small mm\_revision/tests/test\_conic.py}", r"{\small \path{mm_revision/tests/test_conic.py}}")
content = content.replace(r"\texttt{\small test\_recurrence\_lp\_bounds()}", r"{\small \path{test_recurrence_lp_bounds()}}")
content = content.replace(r"\texttt{\small test\_conic\_relaxation()}", r"{\small \path{test_conic_relaxation()}}")

content = content.replace(r"\texttt{\small independent\_verifier/verifier.py}", r"{\small \path{independent_verifier/verifier.py}}")

content = content.replace(r"\texttt{\small tests/test\_funded\_mechanism.py}", r"{\small \path{tests/test_funded_mechanism.py}}")
content = content.replace(r"\texttt{\small test\_solvency\_boundary()}", r"{\small \path{test_solvency_boundary()}}")

content = content.replace(r"\texttt{\small tests/test\_q\_learning\_transfer.py}", r"{\small \path{tests/test_q_learning_transfer.py}}")
content = content.replace(r"\texttt{\small test\_model\_class\_audit()}", r"{\small \path{test_model_class_audit()}}")

with open('paper/Machine_Markets_Final_Integrated_Paper.tex', 'w') as f:
    f.write(content)

print("Done")
