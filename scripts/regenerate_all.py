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
    log("Compiling paper with pdflatex (2 passes)...")
    for i in (1, 2):
        code, out = run_cmd(["pdflatex", "-interaction=nonstopmode", "-halt-on-error", TEX], cwd=PAPER_DIR)
        if code != 0:
            log(f"Compilation failed on pass {i}:")
            print(out[-1500:])
            return False
    shutil.copy(PAPER_DIR / TEX.replace(".tex", ".pdf"), ROOT / TEX.replace(".tex", ".pdf"))
    log("PDF compiled and copied to repository root.")
    return True


def main():
    start = time.time()
    ok = build_results("--no-recompute" not in sys.argv)
    ok = build_ledger() and ok
    ok = run_tests() and ok
    if "--no-pdf" not in sys.argv:
        ok = compile_paper() and ok
    log(f"Done in {time.time() - start:.1f}s. Status: {'OK' if ok else 'FAILED'}")
    sys.exit(0 if ok else 1)


if __name__ == "__main__":
    main()
