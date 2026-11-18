# Antigravity Automation & Push Framework

**Repository:** `Fianince` / `Machine Markets`  
**Target:** Automated Pipeline Execution (Lean 4 Verification $\rightarrow$ Numerical Script Validation $\rightarrow$ LaTeX Compilation $\rightarrow$ Git Synchronization $\rightarrow$ Remote Push)

---

## 1. Prerequisites & Environment Conditions

Before executing the master pipeline, verify that the following local environments are active:
* **Python 3.10+:** With `numpy`, `scipy`, `pandas` installed.
* **Lean 4 Environment:** `elan` and `lake` are installed and active on the system PATH.
* **LaTeX Environment:** `pdflatex`, `bibtex`, and standard AMS/Natbib packages available.
* **Git Remote:** Authenticated with SSH or personal access token to `origin/main`.

---

## 2. Master Automation Script (`antigravity_push.py`)

The script below automates the entire end-to-end verification, compilation, staging, and remote push process. It is saved in the repository root as `antigravity_push.py`.

```python
#!/usr/bin/env python3
"""
Antigravity Master Push & Verification Pipeline
Automates Lean 4 verification, Python calibration validation, LaTeX builds, git staging, and push.
"""

import subprocess
import sys
import os
from pathlib import Path

def run_cmd(command, error_message, cwd=None):
    print(f"🚀 Running: {command} (in {cwd or '.'})")
    result = subprocess.run(command, shell=True, capture_output=True, text=True, cwd=cwd)
    if result.returncode != 0:
        print(f"❌ Error during: {error_message}")
        print("STDOUT:", result.stdout)
        print("STDERR:", result.stderr)
        sys.exit(1)
    print(f"✅ Success: {error_message}")
    return result.stdout

def main():
    print("==================================================")
    print("✨ INITIALIZING ANTIGRAVITY WORKFLOW PIPELINE ✨")
    print("==================================================")
    root = Path(__file__).resolve().parent

    # Step 1: Python Institutional Calibration Check (Subsection 3.3)
    print("\n--- [1/5] Validating Institutional Dollar Calibration ---")
    calib_script = root / "studies/paper1_uplift_20261105/dollar_calibration_s12.py"
    if calib_script.exists():
        run_cmd(f"python3 {calib_script}", "Dollar calibration verification", cwd=str(root))
    else:
        print(f"⚠️ Warning: {calib_script} not found, skipping.")

    # Step 2: Lean 4 Formal Verification
    print("\n--- [2/5] Running Lean 4 Formal Verification ---")
    lake_dir = root / "research_extension/current_manuscript_lean_20261008"
    if (lake_dir / "lakefile.lean").exists() or (lake_dir / "lakefile.toml").exists():
        run_cmd("lake build", "Lean 4 formal verification build", cwd=str(lake_dir))
    elif (root / "lakefile.lean").exists() or (root / "lakefile.toml").exists():
        run_cmd("lake build", "Root Lean 4 verification build", cwd=str(root))
    else:
        print("ℹ️ Skipping Lean 4 build (no lakefile found in standard paths).")

    # Step 3: Rebuilding LaTeX Manuscripts
    print("\n--- [3/5] Rebuilding Paper 1 Manuscripts ---")
    note_dir = root / "ceiling_suite/papers/paper1_note"
    if (note_dir / "build_note.py").exists():
        run_cmd("python3 build_note.py", "Paper 1 Note assembly", cwd=str(note_dir))
    
    # Compile paper1_theory.tex if pdflatex is present
    which_pdf = subprocess.run("which pdflatex", shell=True, capture_output=True, text=True)
    if which_pdf.returncode == 0:
        for target in ["paper1_theory.tex", "paper1_note.tex"]:
            if (note_dir / target).exists():
                print(f"📄 Compiling {target}...")
                run_cmd(f"pdflatex -interaction=nonstopmode {target}", f"pdflatex pass 1 for {target}", cwd=str(note_dir))
                run_cmd(f"pdflatex -interaction=nonstopmode {target}", f"pdflatex pass 2 for {target}", cwd=str(note_dir))
    else:
        print("ℹ️ pdflatex not found in PATH; skipping PDF rendering.")

    # Step 4: Git Status & Staging
    print("\n--- [4/5] Checking Git Status & Staging Changes ---")
    status_out = run_cmd("git status --short", "Checking git status", cwd=str(root))
    print(status_out)
    run_cmd("git add -A", "Staging all modified and new files", cwd=str(root))

    # Step 5: Commit & Push to Remote
    print("\n--- [5/5] Committing & Pushing to Remote Origin ---")
    commit_msg = "Antigravity sync: dollar calibration S12, prospective protocol framing, and stripped internal paths"
    
    # Check if there are changes to commit
    diff_check = subprocess.run("git diff --cached --quiet", shell=True, cwd=str(root))
    if diff_check.returncode != 0:
        run_cmd(f'git commit -m "{commit_msg}"', "Committing staged changes", cwd=str(root))
    else:
        print("ℹ️ No new changes staged to commit.")

    # Get active branch name
    branch_res = subprocess.run("git branch --show-current", shell=True, capture_output=True, text=True, cwd=str(root))
    current_branch = branch_res.stdout.strip() or "main"
    
    # Push to origin
    push_out = subprocess.run(f"git push origin {current_branch}", shell=True, capture_output=True, text=True, cwd=str(root))
    if push_out.returncode == 0:
        print(f"✅ Successfully pushed to origin/{current_branch}")
    else:
        print("⚠️ Push notice (check credentials or connection):")
        print(push_out.stderr)

    print("\n==================================================")
    print("🌟 ANTIGRAVITY PIPELINE COMPLETED! 🌟")
    print("==================================================")

if __name__ == "__main__":
    main()
```

---

## 3. Terminal Execution Instructions

To execute the entire pipeline with one command from your terminal:

```bash
python3 antigravity_push.py
```

### Direct CLI Commands (Manual Fallback):

If you prefer to run individual stages manually:

1. **Run Dollar Calibration & Verification:**
   ```bash
   python3 studies/paper1_uplift_20261105/dollar_calibration_s12.py
   ```

2. **Re-assemble Paper 1 Note & Theory TeX Sources:**
   ```bash
   cd ceiling_suite/papers/paper1_note && python3 build_note.py && cd ../../..
   ```

3. **Stage, Commit, and Push:**
   ```bash
   git add studies/paper1_uplift_20261105/
   git add ceiling_suite/papers/paper1_core/
   git add ceiling_suite/papers/paper1_note/
   git add research_extension/paper1_publication_revision/
   git commit -m "Complete Subsection 3.1-3.3: dollar calibration S12, prospective window framing, and path cleanup"
   git push origin main
   ```
