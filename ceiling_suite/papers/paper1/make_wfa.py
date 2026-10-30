"""Build the anonymous WFA 2027 submission of Paper 1 from paper1.tex (the working draft stays unchanged).

Keeps the paper itself (abstract through Appendix D) and removes what is not part of a submission: the dated research
status paragraph, the development-revision and information-decision blocks, the finite-horizon extension and the
returned-experiment work register (all retained in paper1.tex and in studies/). Anonymises the title page, running
header and the self-citation of the companion paper. Output: paper1_wfa.tex -> paper1_wfa.pdf.
"""
import re
import subprocess
from pathlib import Path

HERE = Path(__file__).resolve().parent
src = (HERE / "paper1.tex").read_text()

core, _, _ = src.partition("% BEGIN ECONOMIC REVIEW 20261029")
assert "\\section{Reproducibility: source of every number}" in core and "returned_results" not in core
core = re.sub(r"% BEGIN ADVANCED FRONT STATUS 20261030.*?% END ADVANCED FRONT STATUS 20261030\n", "", core, flags=re.S)
core = re.sub(r"\\author\{.*?\}\}\n", r"\\author{}\n", core, count=1, flags=re.S)
core = core.replace("\\date{Development revision, 30 October 2026}", "\\date{November 2026}")
core = core.replace("\\fancyhead[L]{\\small Niroula and Niroula}", "\\fancyhead[L]{\\small Anonymous submission}")
core = re.sub(r"\\bibitem\[Niroula et~al\.\(2026\)\]\{niroula2026b\}.*?\n",
              "\\\\bibitem[Anonymous(2026)]{niroula2026b} Anonymous (2026). Companion paper on transient amplification and "
              "pre-trade guards in closed-loop markets. Working paper, withheld for anonymous review.\n", core, count=1)
core = core.replace("The historical simulation results retain their original execution records; this revision reruns the "
                    "named advanced experiment only. ", "")
out = core.rstrip() + "\n\n\\end{document}\n"
for word in ("Niroula", "Pratik", "Prashant", "Mankato", "Tribhuvan", "mnsu", "Pratikn03", "fianince"):
    assert word.lower() not in out.lower().replace("niroula2026b", ""), f"identifying text left: {word}"
(HERE / "paper1_wfa.tex").write_text(out)
for _ in range(2):
    subprocess.run(["pdflatex", "-interaction=nonstopmode", "-halt-on-error", "paper1_wfa.tex"], cwd=HERE,
                   check=True, stdout=subprocess.DEVNULL)
print("built paper1_wfa.pdf")
