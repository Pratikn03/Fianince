#!/usr/bin/env python3
"""
Generate referee-proof two-panel Table 12 for Machine_Markets_JF_Submission.tex
directly from results/provenance/solvency_feedback.json.
Panel A: Baseline Leverage (L = 10, phi = 0.05)
Panel B: Expanded Leverage (L = 20, phi = 0.05)
"""
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
IN_FILE = ROOT / "results" / "provenance" / "solvency_feedback.json"
OUT_FILE = ROOT / "paper" / "generated" / "solvency_feedback_2panel.tex"

def main():
    with open(IN_FILE) as f:
        d = json.load(f)

    # Moments by S
    moments = d["moments"]
    
    # Cells by (L, phi, S, mode)
    cells_map = {}
    for c in d["cells"]:
        key = (c["L"], c["phi"], c["S"], c["mode"])
        cells_map[key] = c

    s_grid = [0.5, 0.6, 0.7, 0.8, 0.9, 0.95]

    lines = []
    lines.append(r"\begin{tabular}{rrrllll}\toprule")
    lines.append(r"$S$ & $\mathrm{var}(f)$ & LRV$(f)$ & Feedback & B1 (var) & B2 (var, AC1) & B3 (var, LRV)\\\midrule")

    # Panel A: L = 10, phi = 0.05
    lines.append(r"\multicolumn{7}{l}{\textit{Panel A: Baseline Leverage limit $L=10$, inventory control $\phi=0.05$}}\\")
    for s in s_grid:
        s_str = str(s)
        var_f = moments[s_str]["var"]
        lrv_f = moments[s_str]["lrv"]
        
        fb = cells_map.get((10.0, 0.05, s, "feedback"), {})
        b1 = cells_map.get((10.0, 0.05, s, "B1"), {})
        b2 = cells_map.get((10.0, 0.05, s, "B2"), {})
        b3 = cells_map.get((10.0, 0.05, s, "B3"), {})

        fb_str = f"{fb['rate']*100:.1f}\\% [{fb['ci95_exact'][0]*100:.1f}, {fb['ci95_exact'][1]*100:.1f}]"
        b1_str = f"{b1['rate']*100:.1f}\\% [{b1['ci95_exact'][0]*100:.1f}, {b1['ci95_exact'][1]*100:.1f}]"
        b2_str = f"{b2['rate']*100:.1f}\\% [{b2['ci95_exact'][0]*100:.1f}, {b2['ci95_exact'][1]*100:.1f}]"
        b3_str = f"{b3['rate']*100:.1f}\\% [{b3['ci95_exact'][0]*100:.1f}, {b3['ci95_exact'][1]*100:.1f}]"

        lines.append(f"{s:.2f} & {var_f:.2f} & {lrv_f:.1f} & {fb_str} & {b1_str} & {b2_str} & {b3_str}\\\\")

    lines.append(r"\midrule")
    # Panel B: L = 20, phi = 0.05
    lines.append(r"\multicolumn{7}{l}{\textit{Panel B: Expanded Leverage limit $L=20$, inventory control $\phi=0.05$}}\\")
    for s in s_grid:
        s_str = str(s)
        var_f = moments[s_str]["var"]
        lrv_f = moments[s_str]["lrv"]
        
        fb = cells_map.get((20.0, 0.05, s, "feedback"), {})
        b1 = cells_map.get((20.0, 0.05, s, "B1"), {})
        b2 = cells_map.get((20.0, 0.05, s, "B2"), {})
        b3 = cells_map.get((20.0, 0.05, s, "B3"), {})

        fb_str = f"{fb['rate']*100:.1f}\\% [{fb['ci95_exact'][0]*100:.1f}, {fb['ci95_exact'][1]*100:.1f}]"
        b1_str = f"{b1['rate']*100:.1f}\\% [{b1['ci95_exact'][0]*100:.1f}, {b1['ci95_exact'][1]*100:.1f}]"
        b2_str = f"{b2['rate']*100:.1f}\\% [{b2['ci95_exact'][0]*100:.1f}, {b2['ci95_exact'][1]*100:.1f}]"
        b3_str = f"{b3['rate']*100:.1f}\\% [{b3['ci95_exact'][0]*100:.1f}, {b3['ci95_exact'][1]*100:.1f}]"

        lines.append(f"{s:.2f} & {var_f:.2f} & {lrv_f:.1f} & {fb_str} & {b1_str} & {b2_str} & {b3_str}\\\\")

    lines.append(r"\bottomrule\end{tabular}")
    lines.append("")

    with open(OUT_FILE, "w") as f:
        f.write("\n".join(lines))
    print(f"Successfully wrote {OUT_FILE}")

if __name__ == "__main__":
    main()
