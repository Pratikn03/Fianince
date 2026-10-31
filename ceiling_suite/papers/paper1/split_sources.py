"""Keep the legacy split sources in step with paper1.tex.

paper1.tex is the single source of truth for Paper 1. Older tools still read the seven split files
(p1_front.tex ... p1_appendix.tex): build_versions.py (Paper1_QE), verify_paper_numbers.py and the Lean
label-mapping audit (verify_ceiling_suite_lean_proofs.py, which reads ceiling_suite/paper1/). This script
cuts paper1.tex at the same section boundaries the split files always used, so that concatenating the
split files reproduces paper1.tex byte for byte, and mirrors the result into ceiling_suite/paper1/.
Never edit the split files by hand; edit paper1.tex and run this script (build_p1.sh does it).
"""
from pathlib import Path

HERE = Path(__file__).resolve().parent
MIRROR = HERE.parents[1] / "paper1"          # ceiling_suite/paper1 (legacy copy read by the Lean audit)
NAMES = ["p1_front", "p1_ident", "p1_account", "p1_mixture", "p1_disclosure", "p1_empirics", "p1_appendix"]
CUTS = ["\\section{The identification boundary}", "\\section{Account-level capital}",
        "\\section{Unknown mixtures and passive data}", "\\section{What disclosure buys}",
        "\\section{Empirical feedback and its measurement}", "\\begin{thebibliography}"]


def main():
    src = (HERE / "paper1.tex").read_text()
    pos = [0]
    for c in CUTS:
        # section headings are unique; the bibliography cut is the first one (the finite-horizon note has its own)
        assert c.startswith("\\begin{thebibliography}") or src.count(c) == 1, f"boundary not unique: {c}"
        pos.append(src.index(c, pos[-1]))
    assert pos == sorted(pos), "section boundaries out of order"
    pos.append(len(src))
    parts = [src[pos[i]:pos[i + 1]] for i in range(len(NAMES))]
    assert "".join(parts) == src
    for d in (HERE, MIRROR):
        if not d.exists():
            continue
        for name, part in zip(NAMES, parts):
            (d / f"{name}.tex").write_text(part)
        if d != HERE:
            (d / "paper1.tex").write_text(src)
    print("split sources regenerated from paper1.tex (" + ", ".join(NAMES) + ")")


if __name__ == "__main__":
    main()
