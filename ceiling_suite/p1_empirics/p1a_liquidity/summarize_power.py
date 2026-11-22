"""Summarize power_sim_results.json into the tables of the draft specification (markdown)."""
import json
from pathlib import Path

R = json.loads(Path(__file__).with_name("power_sim_results.json").read_text())
rows = R["rows"]


def get(est, P, W, rho, psi, lam, piz, g, key):
    for r in rows:
        if (r["estimator"], r["pools"], r["weeks"], r["reliability"], r["psi"], r["lambda"], r["pi_Z"], r["gamma"]) == \
                (est, P, W, rho, psi, lam, piz, g):
            return r[key]
    raise KeyError


def pct(x):
    return f"{100 * x:.0f}%"


out = []
out.append("### Table A. The threats: how often each estimator wrongly rejects a true theory\n")
out.append("P(contrary | gamma = 0), 30 pools x 104 weeks, instrument strength 0.3; normal critical values, "
           "400 draws per cell.\n")
out.append("| Response reliability | Composition tied to response (psi) | Depth feeds composition (lambda) | OLS | IV |")
out.append("|---|---|---|---|---|")
for rho in (0.6, 0.8, 0.95):
    for psi in (0.0, 0.5):
        for lam in (0.0, 0.3):
            out.append(f"| {rho} | {psi} | {lam} | {pct(get('OLS', 30, 104, rho, psi, lam, 0.3, '0', 'contrary'))} | "
                       f"{pct(get('IV', 30, 104, rho, psi, lam, 0.3, '0', 'contrary'))} |")
out.append("")
out.append("### Table B. IV: power to support a true theory, and the size of the support claim\n")
out.append("Worst realistic case: psi = 0.5, lambda = 0.3. Cells: P(supportive | gamma = 0) / P(supportive | gamma = delta) / "
           "P(contrary | gamma = 2 delta). Normal critical values, 400 draws per cell (Monte Carlo standard error at most "
           "2.5 points).\n")
out.append("| Pools x weeks | Reliability | Instrument 0.15 | Instrument 0.3 | Instrument 0.6 |")
out.append("|---|---|---|---|---|")
for (P, W) in ((20, 52), (30, 104), (40, 104)):
    for rho in (0.6, 0.8, 0.95):
        cells = []
        for piz in (0.15, 0.3, 0.6):
            cells.append(f"{pct(get('IV', P, W, rho, 0.5, 0.3, piz, '0', 'supportive'))} / "
                         f"{pct(get('IV', P, W, rho, 0.5, 0.3, piz, 'delta', 'supportive'))} / "
                         f"{pct(get('IV', P, W, rho, 0.5, 0.3, piz, '2delta', 'contrary'))}")
        out.append(f"| {P} x {W} | {rho} | " + " | ".join(cells) + " |")
out.append("")
out.append("### Table C. IV first-stage strength (median cluster-robust F for composition)\n")
out.append("| Pools x weeks | Instrument 0.15 | Instrument 0.3 | Instrument 0.6 |")
out.append("|---|---|---|---|")
for (P, W) in ((20, 52), (30, 104), (40, 104)):
    out.append(f"| {P} x {W} | " + " | ".join(
        f"{get('IV', P, W, 0.8, 0.5, 0.3, piz, '0', 'median_first_stage_F'):.0f}" for piz in (0.15, 0.3, 0.6)) + " |")
mx_size = max(r["supportive"] for r in rows if r["estimator"] == "IV" and r["gamma"] == "delta")
mx_false = max(r["contrary"] for r in rows if r["estimator"] == "IV" and r["gamma"] == "0")
mx_false_ols = max(r["contrary"] for r in rows if r["estimator"] == "OLS" and r["gamma"] == "0")
out.append("")
out.append(f"Across all {len(rows) // 2 // 3} designs: the IV support claim's size at the boundary is at most {pct(mx_size)}; "
           f"IV's false-contrary rate at most {pct(mx_false)}; OLS's at most {pct(mx_false_ols)}.")
text = "\n".join(out)
Path(__file__).with_name("power_sim_summary.md").write_text(text + "\n")
print(text)
