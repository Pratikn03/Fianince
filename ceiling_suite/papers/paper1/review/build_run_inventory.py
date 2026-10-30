"""Run inventory for Paper 1 (plan of 30 Oct, Phases 1 and 5).

Scans every result collection in the repository, records each JSON result file with its size, first commit
date, producing script (when a script names the file) and where it is cited, and classifies it for Paper 1:

  cited-P1        named in paper1.tex or in a Paper 1 row of EXPERIMENT_MANIFEST.csv
  P1-topic        not cited, but its name or folder matches a Paper 1 topic (candidate for reanalysis)
  P2-or-thesis    cited by Paper 2 or the thesis sources, or in a Paper 2 manifest row
  unclassified    none of the above; needs inspection before any use

Writes run_inventory.csv (one row per file) and run_inventory_summary.md (per collection). Read-only on results.
"""
import csv
import re
import subprocess
from collections import Counter, defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parents[4]          # repository root
OUT = Path(__file__).resolve().parent
COLLECTIONS = ["ceiling_suite/recomputed", "ceiling_suite/papers/recomputed", "ceiling_suite/theory",
               "ceiling_suite/p7res", "ceiling_suite/p10res", "ceiling_suite/p11res", "ceiling_suite/p12res",
               "ceiling_suite/p13res", "ceiling_suite/p14res", "ceiling_suite/p17res", "ceiling_suite/p18res",
               "ceiling_suite/outputs", "ceiling_suite/papers/hardening", "ceiling_suite/papers/results_archive", "thesis/evidence", "thesis/checks",
               "studies", "research_extension", "archive"]
P1_TOPIC = re.compile(r"(P1[_.-]|p1_|kcohort|esprit|passive|disclos|cot|tagged|learner|capital|crb|estimator|"
                      r"minimax|merged|theory_const|protocol|sprt|cat_|third_tap|monoton|sigma_obs|fresh_days|"
                      r"Z6|X9|C3_|C4_)", re.I)

def read(p):
    try:
        return Path(p).read_text(errors="ignore")
    except OSError:
        return ""

p1_tex = read(ROOT / "ceiling_suite/papers/paper1/paper1.tex")
p2_tex = read(ROOT / "ceiling_suite/papers/paper2/paper2.tex") + read(ROOT / "ceiling_suite/paper2/paper2.tex")
thesis_tex = "".join(read(p) for p in (ROOT / "thesis").glob("*.tex"))
p1_tex_flat = p1_tex.replace("\\_", "_").replace("\\allowbreak", "").replace(" ", "")
manifest = list(csv.DictReader(open(ROOT / "ceiling_suite/EXPERIMENT_MANIFEST.csv")))
man_out = {Path(r["output_path"]).name: r for r in manifest}

# A file counts as cited only if its stem is an identifier-like token of the source (texttt contents or
# underscore/digit identifiers), never because a common word such as "results" occurs in the prose.
def tokens(tex):
    flat = tex.replace("\\_", "_").replace("\\allowbreak", "").replace("\\ ", "")
    toks = set()
    for t in re.findall(r"\\texttt\{([^}]*)\}", flat):
        toks.update(x for x in re.split(r"[^A-Za-z0-9_.\-]+", t.replace(" ", "")) if x)
    toks.update(re.findall(r"\b[A-Za-z0-9]+(?:[_.-][A-Za-z0-9]+)+\b", flat))
    return {t[:-5] if t.endswith(".json") else t for t in toks if len(t) >= 4}

def cited(stem, toks):
    if stem in toks:
        return True
    return any(len(t) >= 5 and ("_" in t or "-" in t) and stem.startswith(t) for t in toks)

P1_TOKENS, P2_TOKENS, TH_TOKENS = tokens(p1_tex), tokens(p2_tex), tokens(thesis_tex)

# first-add commit date per path, from one git log pass
first_add = {}
log = subprocess.run(["git", "log", "--diff-filter=A", "--name-only", "--format=@@%ad", "--date=short"],
                     cwd=ROOT, capture_output=True, text=True).stdout
date = None
for line in log.splitlines():
    if line.startswith("@@"):
        date = line[2:]
    elif line.strip():
        first_add[line.strip()] = date            # log runs newest first, so the last write is the first add

# which script names a result file (by stem), searched once over all .py files
py_text = {p: read(p) for p in ROOT.rglob("*.py") if ".git" not in p.parts and "node_modules" not in p.parts}

def producer(stem):
    hits = [str(p.relative_to(ROOT)) for p, t in py_text.items() if stem in t]
    return ";".join(sorted(hits)[:3])

rows = []
for coll in COLLECTIONS:
    base = ROOT / coll
    if not base.is_dir():
        continue
    for f in sorted(base.rglob("*.json")):
        rel = str(f.relative_to(ROOT))
        stem = f.stem
        cited_p1 = cited(stem, P1_TOKENS) or f.name in man_out and man_out[f.name]["paper"] == "Paper 1"
        cited_p2 = cited(stem, P2_TOKENS) or f.name in man_out and man_out[f.name]["paper"] == "Paper 2"
        cited_th = cited(stem, TH_TOKENS)
        if cited_p1:
            cls = "cited-P1"
        elif P1_TOPIC.search(rel):
            cls = "P1-topic"
        elif cited_p2 or cited_th:
            cls = "P2-or-thesis"
        else:
            cls = "unclassified"
        rows.append({"collection": coll, "path": rel, "bytes": f.stat().st_size,
                     "first_commit": first_add.get(rel, ""), "class": cls,
                     "cited_paper1": int(cited_p1), "cited_paper2": int(cited_p2), "cited_thesis": int(cited_th),
                     "producer_script": producer(stem) if cls in ("cited-P1", "P1-topic") else ""})

with open(OUT / "run_inventory.csv", "w", newline="") as fh:
    w = csv.DictWriter(fh, fieldnames=list(rows[0]))
    w.writeheader()
    w.writerows(rows)

by = defaultdict(Counter)
for r in rows:
    by[r["collection"]][r["class"]] += 1
lines = ["# Run inventory summary (generated by build_run_inventory.py)", "",
         f"{len(rows)} JSON result files in {len(by)} collections.", "",
         "| Collection | Files | cited-P1 | P1-topic | P2-or-thesis | unclassified |", "|---|---|---|---|---|---|"]
for coll, c in by.items():
    lines.append(f"| `{coll}` | {sum(c.values())} | {c['cited-P1']} | {c['P1-topic']} | {c['P2-or-thesis']} | {c['unclassified']} |")
tot = Counter(r["class"] for r in rows)
lines += ["", f"Totals: {dict(tot)}", "",
          "## Paper 1 sources cited in the reproducibility appendix with no matching result file found", ""]
cited = set(re.findall(r"\\texttt\{([^}]*)\}", p1_tex[p1_tex.find("label{app:repro}"):]))
names = {Path(r["path"]).stem for r in rows}
for c in sorted(cited):
    s = c.replace("\\_", "_").replace("\\allowbreak", "").replace(" ", "")
    if s.endswith(".json"):
        s = s[:-5]
    if s.endswith(".py") or "." in s or "/" in s:
        continue
    if not any(s in n or n in s for n in names):
        lines.append(f"- `{s}`")
(OUT / "run_inventory_summary.md").write_text("\n".join(lines) + "\n")
print("\n".join(lines))
