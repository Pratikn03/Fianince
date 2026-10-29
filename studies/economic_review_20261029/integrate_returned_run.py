"""Validate the returned exploratory run and integrate an explicit development appendix.

No registered result is overwritten. This script expects the 29 October result
archive and verifies its exported hashes and the analytical source snapshot.
"""
from pathlib import Path
import argparse
import hashlib
import io
import json
import subprocess
import zipfile

import pandas as pd

ROOT = Path(__file__).resolve().parents[2]
HERE = Path(__file__).resolve().parent
START = "% BEGIN ECONOMIC REVIEW 20261029"
END = "% END ECONOMIC REVIEW 20261029"


def digest(b):
    return hashlib.sha256(b).hexdigest()


def replace_once(path, old, new):
    text = path.read_text()
    if new in text:
        return
    if old not in text:
        raise ValueError(f"Expected source text missing: {path}: {old[:60]}")
    path.write_text(text.replace(old, new, 1))


def inject(path, fragment, before):
    text = path.read_text()
    if START in text:
        first = text.index(START)
        last = text.index(END, first) + len(END)
        text = text[:first] + text[last:]
    index = text.rindex(before)
    text = text[:index] + START + "\n" + fragment + "\n" + END + "\n\n" + text[index:]
    path.write_text(text)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("archive", type=Path)
    args = parser.parse_args()
    destination = HERE / "results/colab_return_20261029"
    destination.mkdir(parents=True, exist_ok=True)
    data = args.archive.read_bytes()
    with zipfile.ZipFile(io.BytesIO(data)) as archive:
        if sum(i.file_size for i in archive.infolist()) > 100_000_000:
            raise ValueError("Unexpected archive size")
        for item in archive.infolist():
            if Path(item.filename).is_absolute() or ".." in Path(item.filename).parts:
                raise ValueError("Unsafe archive member")
        runs = json.loads(archive.read("runs_summary.json"))
        if len(runs) != 1 or runs[0]["mode"] != "full":
            raise ValueError("Expected exactly the returned full run")
        folder = runs[0]["folder"]
        meta = json.loads(archive.read(folder + "/manifest.json"))
        if meta["status"] != "completed" or meta["configuration"]["csv"] is not None:
            raise ValueError("Unexpected run state or data contract")
        if meta["source_commit"] != "19805d7ec6265691166456407902d63215747e51":
            raise ValueError("Unexpected source commit")
        verified = []
        for name, expected in meta["exported_file_sha256"].items():
            body = archive.read(folder + "/" + name)
            if digest(body) != expected:
                raise ValueError("Hash mismatch: " + name)
            verified.append(name)
        # Analytical modules must match both the returned code and the reviewed tree.
        for name in ["__init__.py", "models.py", "experiments.py", "run.py"]:
            body = archive.read("experiment_code/" + name)
            reviewed = (HERE / name).read_bytes()
            if digest(body) != meta["source_hashes"][name] or body != reviewed:
                raise ValueError("Analytical source mismatch: " + name)
        frames = {}
        for name in verified:
            body = archive.read(folder + "/" + name)
            (destination / name).write_bytes(body)
            if name.endswith(".csv"):
                frames[name] = pd.read_csv(io.BytesIO(body))
        (destination / "manifest.json").write_text(json.dumps(meta, indent=2) + "\n")
    verification = dict(archive_sha256=digest(data), verified_exported_files=verified,
                        source_commit=meta["source_commit"], analytical_sources_match=True,
                        interpretation="same-code seeded execution reproduction, not an independent experiment",
                        not_run=meta["not_run"], csv_row_counts={k:len(v) for k,v in frames.items()})
    (destination / "verification.json").write_text(json.dumps(verification, indent=2) + "\n")
    coverage = frames["E6_coverage.csv"]
    labels = {"iid_gaussian":"Independent Gaussian", "serially_correlated_tap_errors":"Correlated tap errors",
              "heavy_tailed_t3":"Heavy-tailed readings", "biased_readings":"Biased readings",
              "hidden_slow_memory":"Unseen slow memory"}
    rows = []
    for _, row in coverage.iterrows():
        rows.append(f"{labels[row.setting]} & {100*row.coverage:.1f}\\% & "
                    f"[{100*row.mc_ci_low:.1f}, {100*row.mc_ci_high:.1f}] & "
                    + ("yes" if row.guarantee_applicable else "no") + r"\\")
    note = r"""\section*{Development revision and validation status: 29 October 2026}
This is a working draft for author and specialist review. The revision corrects
hidden-state drift accounting, distinguishes cumulative displacement from peak
mark-to-market loss, and restricts claims to their stated model and observation
contracts. It does not declare every theorem independently verified or every
research objective complete.

\paragraph{Returned execution record.} The author returned a completed full-mode
notebook archive using source commit \texttt{19805d7e}, seed 20261029,
Python 3.13.18 and NumPy 2.1.3. All 11 exported-file hashes and the four analytical
source modules were checked. The run completed E1, E2, E3, E4 and E6; its log
reports 18 targeted tests passing. This is an execution reproduction of the same
seeded code, not independent scientific validation. No real-market CSV was
provided, and the GPU, known-source-feedback and prospective studies were not run.

\paragraph{What the checks establish.} E1 cross-checks the corrected drift identity
against a resolvent and exercises a sufficient invariant-box guard. E2 demonstrates
filter-induced persistence under martingale nulls. E3 compares known alternatives
with equal aggregate risk; it is an illustrative witness, not a uniform rate
theorem. E4 matches baseline capacity on training episodes and reports test
capacity differences; the guard and volatility control both have zero observed
budget breaches in the three bounded-shock synthetic regimes. This does not
establish universal guard superiority or economic welfare.

\paragraph{Coverage and the observation contract.} E6 uses 1,000 replications,
32 reset responses and 512 taps. The nominal 95\% interval assumes independent
Gaussian tap errors and a valid memory envelope. The intervals in the table
measure Monte Carlo uncertainty about coverage, not financial risk.
\begin{center}\small
\begin{tabular}{lrrc}
\toprule
Setting & Coverage & MC 95\% interval & Contract holds\\
\midrule
""" + "\n".join(rows) + r"""
\bottomrule
\end{tabular}
\end{center}
Failures under correlated errors, biased readings and a false memory floor expose
the contract's limits. The heavy-tail outcome in this configuration is not a
general robustness result. All outcomes, including negative ones, are retained.

\paragraph{Remaining obligations.} Independent review of the load-bearing
identification and certification proofs, continuous numerical extrema, economic
primitives, the public-observation bridge and policy counterfactuals remains
necessary. The current two-paper name-map audit finds 54 of 57 formal environments
with existing declaration mappings, three unmapped statements and seven revised
statements requiring semantic review. A label mapping is not a new Lean proof.
The experiment design and full results are retained under
\texttt{studies/economic\_review\_20261029/}.
"""
    note = note.replace("All 11 exported-file hashes", f"All {len(verified)} exported-file hashes")
    (HERE / "manuscript_revision_note.tex").write_text(note.rstrip() + "\n")
    papers = ROOT / "ceiling_suite/papers"
    for paper in [1, 2]:
        inject(papers / f"paper{paper}/p{paper}_appendix.tex", note, r"\end{document}")
        replace_once(papers / f"paper{paper}/p{paper}_front.tex",
                     "Revised preprint, October 2026", "Development revision, 29 October 2026")
    inject(papers / "flagship/identify_certify.tex", note, r"\end{document}")
    replace_once(papers / "flagship/identify_certify.tex", "Working draft, October 2026.",
                 "Development revision, 29 October 2026.")
    thesis_note = note.replace(r"\section*{Development revision and validation status: 29 October 2026}",
                              r"\chapter{Development revision and validation status}")
    inject(ROOT / "thesis/thesis.tex", thesis_note, r"\chapter*{Bibliography for Chapters~1, 4 and 5}")
    replace_once(ROOT / "thesis/thesis.tex", "Thesis blueprint, October 2026",
                 "Thesis working draft, revised 29 October 2026")
    # Layout-only changes: break long inline mathematics at display boundaries.
    f = papers / "paper1/p1_ident.tex"
    replace_once(f, r"through the measure $\sum_iq_i\,\eta(s_i)\,\delta_{1-\eta(s_i)}$. Desks",
                 "through the measure\n\\[\n\\sum_iq_i\\,\\eta(s_i)\\,\\delta_{1-\\eta(s_i)}.\n\\]\nDesks")
    f = ROOT / "thesis/ch4_paper3.tex"
    for old, new in [
        (r"The averages $\bar k=(\bar k_0,\dots,\bar k_{L-1})$ are sufficient and distributed as $N(k_L(M),(\sigma^2/N)I_L)$, so",
         "The averages are sufficient, with distribution\n\\[\n\\bar k=(\\bar k_0,\\dots,\\bar k_{L-1})\\sim N(k_L(M),(\\sigma^2/N)I_L).\n\\]\nThus"),
        (r"is $2\Phi_{\mathcal N}(\sqrt N\|\Delta k\|_2/(2\sigma))-1$, with",
         "is\n\\[\n2\\Phi_{\\mathcal N}(\\sqrt N\\|\\Delta k\\|_2/(2\\sigma))-1,\n\\]\nwith"),
        (r"every procedure, $\sup_{r<1}\Pr_{\mathcal E_r}(\text{certify safe})\ge\Pr_{\mathcal E_0}(\text{certify safe})$. A procedure",
         "every procedure,\n\\[\n\\sup_{r<1}\\Pr_{\\mathcal E_r}(\\text{certify safe})\\ge\\Pr_{\\mathcal E_0}(\\text{certify safe}).\n\\]\nA procedure"),
        (r"\emph{Size, uniformly.} $\lim_{T\to\infty}\sup\Pr(\text{certify safe})=\alpha$, the supremum",
         "\\emph{Size, uniformly.}\n\\[\n\\lim_{T\\to\\infty}\\sup\\Pr(\\text{certify safe})=\\alpha,\n\\]\nwhere the supremum"),
        (r"\begin{tabular}{lccccccc}", r"\setlength{\tabcolsep}{2pt}" + "\n" + r"\begin{tabular}{lccccccc}"),
    ]:
        replace_once(f, old, new)
    replace_once(ROOT / "thesis/thesis.tex", r"\emergencystretch=2em", r"\emergencystretch=6em" + "\n" + r"\Urlmuskip=0mu plus 2mu\relax")
    subprocess.run(["python", str(HERE / "refresh_sources.py")], cwd=ROOT, check=True)
    print(json.dumps(verification, indent=2))


if __name__ == "__main__":
    main()
