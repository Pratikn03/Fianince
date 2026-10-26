# Reproducing the thesis review package

This package contains the current thesis draft PDF, its sources and figures, archived thesis evidence, the standalone margin-monitor package, and current Lean sources/receipts. It does not include the entire GitHub repository, raw exchange downloads, language-model weights or the original Colab environment. It is a review package, not an assertion of academic approval or complete independent proof review.

From the extracted package root, in a Python environment:

```sh
python -m pip install -r requirements-runtime.txt -r requirements-artifacts.txt pypdf
python -m pip install --no-deps ./margin_monitor
python scripts/package_thesis.py
python thesis/verify_thesis_numbers.py
python thesis/checks/check_b2_supplement.py --check
python scripts/verify_thesis_release.py --pdf
PYTHONPATH=margin_monitor pytest margin_monitor/tests -q
```

Install TeX Live with the recommended/extra LaTeX packages, recommended fonts, lmodern and xurl to rebuild:

```sh
sh thesis/build_thesis.sh
python scripts/verify_thesis_release.py --pdf
```

A fresh TeX installation may produce different PDF bytes while retaining content. The manifest checks the delivered bytes before rebuilding; rebuilding intentionally changes that file. Compare content and rendered pages rather than resealing an unexplained mismatch.

The 214 frozen experiment artifacts are verified independently of the package seal. None of the commands above opens an experiment or downloads new test data. B2's saved statistics can be recomputed, but its exact model revision was not recorded; inference replay is not established. Use the full repository and pinned toolchain for complete Lean build/provenance commands, which depend on additional manuscript paths.

See READINESS.md and PROOF_REVIEW.md in this folder for remaining research, provenance and human approval requirements.
