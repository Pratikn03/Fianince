#!/usr/bin/env python3
"""
Generate the dedicated Top-3 Finance Journal Submission Manuscript:
Machine_Markets_JF_Submission.tex -> Machine_Markets_JF_Submission.pdf
Target: 48-52 pages (12pt, 1.5 line spacing, 1in margins, abstract <= 100 words).
Addresses the single central question and three headline contributions.
Integrates the 10-study empirical chain with the flagship natural experiment.
"""
import subprocess
import shutil
import sys
from pathlib import Path
import pypdf

ROOT = Path(__file__).resolve().parent.parent
PAPER_DIR = ROOT / "paper"
TEX_NAME = "Machine_Markets_JF_Submission.tex"
PDF_NAME = "Machine_Markets_JF_Submission.pdf"

def build_pdf():
    print(f"Compiling {TEX_NAME} (Pass 1)...")
    res1 = subprocess.run(["pdflatex", "-interaction=nonstopmode", "-halt-on-error", TEX_NAME], cwd=PAPER_DIR, capture_output=True, text=True)
    if res1.returncode != 0:
        print("Pass 1 failed:")
        print(res1.stdout[-2000:])
        return False
        
    print(f"Compiling {TEX_NAME} (Pass 2)...")
    res2 = subprocess.run(["pdflatex", "-interaction=nonstopmode", "-halt-on-error", TEX_NAME], cwd=PAPER_DIR, capture_output=True, text=True)
    if res2.returncode != 0:
        print("Pass 2 failed:")
        print(res2.stdout[-2000:])
        return False
        
    reader = pypdf.PdfReader(str(PAPER_DIR / PDF_NAME))
    pages = len(reader.pages)
    print(f"SUCCESS: {PDF_NAME} compiled successfully: {pages} pages.")
    
    # Sync with root and submission bundle
    shutil.copy(PAPER_DIR / PDF_NAME, ROOT / PDF_NAME)
    (ROOT / "submission" / "SUBMISSION_BUNDLE").mkdir(parents=True, exist_ok=True)
    shutil.copy(PAPER_DIR / PDF_NAME, ROOT / "submission" / "SUBMISSION_BUNDLE" / PDF_NAME)
    print(f"Synchronized {PDF_NAME} to root and submission/SUBMISSION_BUNDLE/.")
    return True

if __name__ == "__main__":
    ok = build_pdf()
    sys.exit(0 if ok else 1)
