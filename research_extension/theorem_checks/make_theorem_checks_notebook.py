"""Builds Paper1_Theorem_Checks_Colab.ipynb: re-runs every numerical check of Paper 1 and builds the whole Lean
project with the Mathlib cache to produce the formal-verification receipt. No market data are read."""
import json
from pathlib import Path

BRANCH = "claude/paper1-integrity-and-sujan-fixes-20261106"
REPO = "https://github.com/Pratikn03/Fianince.git"

cells = [
 ("markdown", f"""# Paper 1: theorem checks and Lean receipt

This notebook reads **no market data**. It does two things.

1. **Numerical checks.** Re-runs every numerical check cited in the paper and prints PASS or FAIL against the value
   the paper states (16+ checks, about 15-25 minutes). The optional slow cell adds the global-fibre search and the
   two-market worst-case table (about 30-60 minutes more).
2. **Lean.** Installs Lean, downloads the Mathlib cache, builds all modules of the formalization and runs
   `verify_formalization.py`, which writes `formal_verification_receipt.json` (about 15-30 minutes). Download the
   receipt at the end and commit it.

Repository: `{REPO}`, branch `{BRANCH}`. Runtime: CPU is enough.

**The repository is private.** Before running, add a GitHub token with read access to it as a Colab Secret named
`GITHUB_TOKEN` (key icon in the left bar; switch on notebook access). The token is read from the secret and is never
printed. Do not paste it into a cell."""),
 ("code", f"""import os, subprocess
from google.colab import userdata
os.chdir("/content")
token = userdata.get("GITHUB_TOKEN")
url = "{REPO}".replace("https://", "https://x-access-token:" + token + "@")
if not os.path.isdir("repo"):
    r = subprocess.run(["git", "clone", "--depth", "1", "-b", "{BRANCH}", url, "repo"], capture_output=True, text=True)
    print((r.stdout + r.stderr).replace(token, "***"))
    assert r.returncode == 0, "clone failed: check the GITHUB_TOKEN secret and its access to the repository"
os.chdir("/content/repo")
subprocess.run(["git", "remote", "set-url", "origin", "{REPO}"])   # do not keep the token in .git/config
del token, url
!pip -q install mpmath scipy numpy sympy
!git log --oneline -1"""),
 ("code", """# 1. Numerical checks (fast part)
!python3 research_extension/theorem_checks/run_all_checks.py"""),
 ("code", """# 1b. Optional slow part: global fibres for pooling and the two-market worst case
# !python3 research_extension/theorem_checks/run_all_checks.py --slow"""),
 ("code", """# 2. Lean: toolchain and Mathlib cache
!curl -sSf https://raw.githubusercontent.com/leanprover/elan/master/elan-init.sh | sh -s -- -y --default-toolchain none
import os
os.environ["PATH"] = os.path.expanduser("~/.elan/bin") + ":" + os.environ["PATH"]
%cd research_extension/current_manuscript_lean_20261008
!lake exe cache get"""),
 ("code", """# 3. Build every module and write the receipt
!lake build 2>&1 | tail -5
!python3 verify_formalization.py
!python3 -c "import json; r=json.load(open('formal_verification_receipt.json')); print({k: r[k] for k in list(r)[:12]})\""""),
 ("code", """# 4. Download the receipt and the check results
from google.colab import files
files.download('formal_verification_receipt.json')
files.download('../theorem_checks/run_all_checks_results.json')"""),
]

nb = {"cells": [], "metadata": {"colab": {"provenance": []}, "kernelspec": {"display_name": "Python 3", "name": "python3"},
      "language_info": {"name": "python"}}, "nbformat": 4, "nbformat_minor": 0}
for kind, src in cells:
    c = {"cell_type": kind, "metadata": {}, "source": src}
    if kind == "code":
        c.update({"execution_count": None, "outputs": []})
    nb["cells"].append(c)
Path(__file__).with_name("Paper1_Theorem_Checks_Colab.ipynb").write_text(json.dumps(nb, indent=1))
print("wrote Paper1_Theorem_Checks_Colab.ipynb")
