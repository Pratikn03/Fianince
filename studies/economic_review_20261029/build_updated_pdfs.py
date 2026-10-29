"""Compile six current PDF variants into a requested output directory."""
from pathlib import Path
import argparse
from concurrent.futures import ThreadPoolExecutor
import json
import re
import shutil
import subprocess

ROOT = Path(__file__).resolve().parents[2]
JOBS = [
    ("Paper1", "ceiling_suite/papers/paper1", "paper1.tex"),
    ("Paper2", "ceiling_suite/papers/paper2", "paper2.tex"),
    ("Thesis", "thesis", "thesis.tex"),
    ("Identify_or_Certify", "ceiling_suite/papers/flagship", "identify_certify.tex"),
    ("Paper1_QE", "ceiling_suite/papers/versions", "Paper1_QE.tex"),
    ("Paper2_JF", "ceiling_suite/papers/versions", "Paper2_JF.tex"),
]


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--out", type=Path, required=True)
    args = parser.parse_args()
    out = args.out.resolve()
    out.mkdir(parents=True, exist_ok=True)
    builds = out / "build_logs"
    builds.mkdir(exist_ok=True)
    def build(job):
        name, folder, source = job
        dest = builds / name
        dest.mkdir(exist_ok=True)
        target = out / f"{name}_Updated_20261029.pdf"
        target.unlink(missing_ok=True)
        # Do not accept stale PDFs or partially written auxiliary files from a failed build.
        for suffix in [".aux", ".out", ".toc", ".log", ".pdf"]:
            (dest / Path(source).with_suffix(suffix)).unlink(missing_ok=True)
        for _ in range(3):
            proc = subprocess.run(["pdflatex", "-recorder", "-halt-on-error", "-interaction=nonstopmode",
                                   "-output-directory", str(dest), source], cwd=ROOT/folder,
                                  text=True, capture_output=True, timeout=180)
            if proc.returncode:
                break
        log = proc.stdout
        result = dict(name=name, source=f"{folder}/{source}", returncode=proc.returncode,
                      undefined=[s for s in log.splitlines() if "undefined" in s.lower()],
                      overfull=re.findall(r"Overfull[^\n]*(?:\n[^\n]*)?", log),
                      oversized_floats=[s for s in log.splitlines() if "Float too large" in s],
                      errors=[s for s in log.splitlines() if s.startswith("!")])
        if proc.returncode == 0:
            shutil.copyfile(dest/Path(source).with_suffix(".pdf"),target)
            result["pdf"] = str(target)
        else:
            result["tail"] = log[-1800:]
        print(json.dumps(result),flush=True)
        return result
    with ThreadPoolExecutor(max_workers=3) as pool:
        results = list(pool.map(build,JOBS))
    (out/"build_verification.json").write_text(json.dumps(results,indent=2)+"\n")
    if any(r["returncode"] or r["undefined"] or r["overfull"] or r["oversized_floats"] for r in results):
        raise SystemExit("Inspect remaining build issues before delivery.")


if __name__ == "__main__":
    main()
