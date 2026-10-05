#!/usr/bin/env python3
"""
scripts/regenerate_all.py
=========================
Rebuild every generated table from code, run the full test suite, and
compile the paper.

  1. scripts/build_results.py --recompute  (real-data estimates, Monte Carlo
     validation, funded-dealer simulation -> results/provenance/*.json ->
     paper/generated/*.tex)
  2. pytest tests/
  3. pdflatex (2 passes)

No table text is hard-coded here: every generated number comes from a JSON
written by code.  (The previous version wrote fixed table strings; see
archive/withdrawn_20261003/README.md.)

Usage:
  python3.11 scripts/regenerate_all.py [--no-recompute] [--no-pdf]
"""
import shutil
import subprocess
import sys
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
PAPER_DIR = ROOT / "paper"
TEX = "Machine_Markets_Final_Integrated_Paper.tex"


def log(msg: str):
    print(f"[{time.strftime('%H:%M:%S')}] {msg}", flush=True)


def run_cmd(cmd: list, cwd: Path = ROOT) -> tuple[int, str]:
    res = subprocess.run(cmd, cwd=str(cwd), capture_output=True, text=True, errors="replace")
    return res.returncode, res.stdout + res.stderr


def build_results(recompute: bool) -> bool:
    log("Building results and generated tables...")
    cmd = [sys.executable, "scripts/build_results.py"] + (["--recompute"] if recompute else [])
    code, out = run_cmd(cmd)
    print(out[-2000:])
    return code == 0


def verify_bridge() -> bool:
    log("Verifying theorem-to-code bridge and Lean formalizations...")
    code, out = run_cmd([sys.executable, "scripts/verify_theorem_code_bridge.py"])
    print(out[-1500:])
    return code == 0


def build_ledger() -> bool:
    log("Checking provenance ledger and writing generated ledger tables...")
    code, out = run_cmd([sys.executable, "scripts/provenance_ledger.py"])
    print(out[-1500:])
    return code == 0


def run_tests() -> bool:
    log("Running full test suite...")
    code, out = run_cmd([sys.executable, "-m", "pytest", "tests/", "-q", "--tb=short"])
    print(out[-1500:])
    return code == 0


def compile_paper() -> bool:
    log("Compiling main paper with pdflatex (2 passes)...")
    for i in (1, 2):
        code, out = run_cmd(["pdflatex", "-interaction=nonstopmode", "-halt-on-error", TEX], cwd=PAPER_DIR)
        if code != 0:
            log(f"Main paper compilation failed on pass {i}:")
            print(out[-1500:])
            return False
    shutil.copy(PAPER_DIR / TEX.replace(".tex", ".pdf"), ROOT / TEX.replace(".tex", ".pdf"))

    log("Compiling mathematical supplement with pdflatex (2 passes)...")
    supp_tex = "Machine_Markets_Mathematical_Supplement.tex"
    for i in (1, 2):
        code, out = run_cmd(["pdflatex", "-interaction=nonstopmode", "-halt-on-error", supp_tex], cwd=PAPER_DIR)
        if code != 0:
            log(f"Supplement compilation failed on pass {i}:")
            print(out[-1500:])
            return False

    log("Uniting into combined master volume...")
    code, out = run_cmd([
        "pdfunite",
        str(PAPER_DIR / TEX.replace(".tex", ".pdf")),
        str(PAPER_DIR / supp_tex.replace(".tex", ".pdf")),
        str(ROOT / "Machine_Markets_Combined_Master.pdf"),
    ])
    if code != 0:
        log("pdfunite failed:")
        print(out[-1500:])
        return False
    shutil.copy(ROOT / "Machine_Markets_Combined_Master.pdf", PAPER_DIR / "Machine_Markets_Combined_Master.pdf")
    log("Main paper, supplement, and combined master PDF all built successfully.")
    return True


def generate_figures() -> bool:
    log("Generating publication-grade empirical visualizations...")
    code, out = run_cmd([sys.executable, "scripts/generate_empirical_figures.py"])
    print(out[-1500:])
    return code == 0


def main():
    start = time.time()
    ok = build_results("--no-recompute" not in sys.argv)
    ok = generate_figures() and ok
    ok = verify_bridge() and ok
    ok = build_ledger() and ok
    ok = run_tests() and ok
    if "--no-pdf" not in sys.argv:
        ok = compile_paper() and ok
    log(f"Done in {time.time() - start:.1f}s. Status: {'OK' if ok else 'FAILED'}")
    sys.exit(0 if ok else 1)


if __name__ == "__main__":
    main()
