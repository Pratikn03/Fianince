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
        which_lake = subprocess.run("which lake", shell=True, capture_output=True, text=True)
        if which_lake.returncode == 0:
            run_cmd("lake build", "Lean 4 formal verification build", cwd=str(lake_dir))
        else:
            print("ℹ️ lake not found in PATH; skipping Lean 4 build.")
    elif (root / "lakefile.lean").exists() or (root / "lakefile.toml").exists():
        run_cmd("lake build", "Root Lean 4 verification build", cwd=str(root))
    else:
        print("ℹ️ Skipping Lean 4 build (no lakefile found in standard paths).")

    # Step 3: Rebuilding LaTeX Manuscripts
    print("\n--- [3/5] Rebuilding Paper 1 Manuscripts ---")
    core_dir = root / "ceiling_suite/papers/paper1_core"
    if (core_dir / "build_core.py").exists():
        run_cmd("python3 build_core.py", "Paper 1 Core assembly", cwd=str(core_dir))

    pub_core_dir = root / "research_extension/paper1_publication_revision/source/ceiling_suite/papers/paper1_core"
    if (pub_core_dir / "build_core.py").exists():
        run_cmd("python3 build_core.py", "Publication revision Core assembly", cwd=str(pub_core_dir))

    note_dir = root / "ceiling_suite/papers/paper1_note"
    if (note_dir / "build_note.py").exists():
        run_cmd("python3 build_note.py", "Paper 1 Note assembly", cwd=str(note_dir))
    
    pub_note_dir = root / "research_extension/paper1_publication_revision/source/ceiling_suite/papers/paper1_note"
    if (pub_note_dir / "build_note.py").exists():
        run_cmd("python3 build_note.py", "Publication revision Note assembly", cwd=str(pub_note_dir))

    # Compile paper1_theory.tex if pdflatex is present
    which_pdf = subprocess.run("which pdflatex", shell=True, capture_output=True, text=True)
    if which_pdf.returncode == 0:
        for target in ["paper1_theory.tex", "paper1_note_submission.tex"]:
            if (note_dir / target).exists():
                print(f"📄 Compiling {target}...")
                subprocess.run(f"pdflatex -interaction=nonstopmode {target}", shell=True, cwd=str(note_dir))
        if (core_dir / "paper1_core.tex").exists():
            print(f"📄 Compiling paper1_core.tex...")
            subprocess.run("pdflatex -interaction=nonstopmode paper1_core.tex", shell=True, cwd=str(core_dir))
    else:
        print("ℹ️ pdflatex not found in PATH; skipping PDF rendering.")

    # Step 4: Git Status & Staging
    print("\n--- [4/5] Checking Git Status & Staging Changes ---")
    status_out = run_cmd("git status --short", "Checking git status", cwd=str(root))
    print(status_out)
    run_cmd("git add -A", "Staging all modified and new files", cwd=str(root))

    # Step 5: Commit & Push to Remote
    print("\n--- [5/5] Committing & Pushing to Remote Origin ---")
    commit_msg = "Antigravity sync: math open problems resolved (det J pooling, nonlinear Prony, Nash contraction, convex holding), Lean formalizations, repo-wide path cleanup"
    
    diff_check = subprocess.run("git diff --cached --quiet", shell=True, cwd=str(root))
    if diff_check.returncode != 0:
        run_cmd(f'git commit -m "{commit_msg}"', "Committing staged changes", cwd=str(root))
    else:
        print("ℹ️ No new changes staged to commit.")

    branch_res = subprocess.run("git branch --show-current", shell=True, capture_output=True, text=True, cwd=str(root))
    current_branch = branch_res.stdout.strip() or "main"
    
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
