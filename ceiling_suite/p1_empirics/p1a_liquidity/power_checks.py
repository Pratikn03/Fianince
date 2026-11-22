"""P1A (draft): two follow-up checks on the power simulation (power_sim.py). No data is read.

1. Small-sample critical values. In power_sim.py, the support claim's size at its boundary (gamma = delta) averaged
   5.8% across the strong-instrument designs with at least 30 pools, against a nominal 5%. This check reruns those
   designs with 2,000 draws per cell. It compares normal critical values with t critical values on P - 1 degrees of
   freedom, P being the number of pool clusters, and reports what the correction costs in power.
2. The equivalence margin. Power and size when the smallest composition effect of interest is delta = 0.10 instead of
   0.05, with t critical values.

Run: python power_checks.py   (writes power_checks_results.json and power_checks_summary.md; a few minutes)
"""
import itertools
import json
import time
from pathlib import Path

import numpy as np
from scipy import stats

import power_sim as ps

SEED = 20261123          # a different stream from power_sim.py (20261122)
REPS = 2000


def rule(b, se, delta, z_tost, z_ctrl):
    """The draft decision rule with given critical values."""
    beta, gamma = b
    sb, sg = se
    if gamma - z_tost * sg > delta or gamma + z_tost * sg < -delta:
        return "contrary"
    if abs(beta) > z_ctrl * sb and gamma - z_tost * sg > -delta and gamma + z_tost * sg < delta:
        return "supportive"
    return "inconclusive"


def crit(P):
    return {"normal": (ps.Z90, 1.959963984540054),
            "t": (float(stats.t.ppf(0.95, P - 1)), float(stats.t.ppf(0.975, P - 1)))}


def cell(rng, P, W, rho, psi, lam, piz, gamma, delta):
    draws = []
    for _ in range(REPS):
        D, R1, R2, C, Z = ps.simulate(rng, P, W, rho, psi, lam, gamma, piz)
        b, se, _ = ps.iv(D, R1, R2, C, Z)
        draws.append((b, se))
    out = {}
    for name, (zt, zc) in crit(P).items():
        verdicts = [rule(b, se, delta, zt, zc) for b, se in draws]
        out[name] = {v: verdicts.count(v) / REPS for v in ("supportive", "contrary", "inconclusive")}
    return out


def main():
    rng = np.random.default_rng(SEED)
    t0 = time.time()
    rows = []
    d = ps.DELTA
    # 1a. size at the boundary, strong instrument, every threat combination
    for (P, W), rho, (psi, lam) in itertools.product([(30, 104), (40, 104)], ps.RELIAB,
                                                      [(0.0, 0.0), (0.0, 0.3), (0.5, 0.0), (0.5, 0.3)]):
        rows.append({"check": "size", "pools": P, "weeks": W, "reliability": rho, "psi": psi, "lambda": lam,
                     "pi_Z": 0.6, "delta": d, "gamma": d, **cell(rng, P, W, rho, psi, lam, 0.6, d, d)})
        print(f"size {P}x{W} rho={rho} psi={psi} lam={lam} ({time.time() - t0:.0f}s)", flush=True)
    # 1b. what the correction costs: power at gamma = 0 and at gamma = 2 delta, worst realistic case
    for (P, W), rho, piz, g in itertools.product([(30, 104), (40, 104)], ps.RELIAB, (0.3, 0.6), (0.0, 2 * d)):
        rows.append({"check": "cost", "pools": P, "weeks": W, "reliability": rho, "psi": 0.5, "lambda": 0.3,
                     "pi_Z": piz, "delta": d, "gamma": g, **cell(rng, P, W, rho, 0.5, 0.3, piz, g, d)})
        print(f"cost {P}x{W} rho={rho} piZ={piz} gamma={g} ({time.time() - t0:.0f}s)", flush=True)
    # 2. the margin delta = 0.10, t critical values, reliability 0.8, worst realistic case
    d2 = 0.10
    for (P, W), piz, g in itertools.product(ps.DESIGNS, ps.PI_ZS, (0.0, d2, 2 * d2)):
        rows.append({"check": "margin", "pools": P, "weeks": W, "reliability": 0.8, "psi": 0.5, "lambda": 0.3,
                     "pi_Z": piz, "delta": d2, "gamma": g, **cell(rng, P, W, 0.8, 0.5, 0.3, piz, g, d2)})
        print(f"margin {P}x{W} piZ={piz} gamma={g} ({time.time() - t0:.0f}s)", flush=True)
    out = {"seed": SEED, "reps": REPS, "t_critical_values": {P: crit(P)["t"] for P, _ in ps.DESIGNS},
           "rows": rows, "seconds": time.time() - t0}
    Path(__file__).with_name("power_checks_results.json").write_text(json.dumps(out, indent=1))
    summarize(out)
    print("wrote power_checks_results.json and power_checks_summary.md")


def summarize(out):
    rows = out["rows"]

    def get(check, **k):
        for r in rows:
            if r["check"] == check and all(abs(r[a] - v) < 1e-12 for a, v in k.items()):
                return r
        raise KeyError(k)

    def pct(x):
        return f"{100 * x:.1f}%"

    mcse = np.sqrt(0.05 * 0.95 / out["reps"])
    s = []
    s.append("### Table D. Size of the support claim at its boundary: normal against t critical values\n")
    s.append(f"P(supportive | gamma = delta = 0.05), instrument strength 0.6, {out['reps']:,} draws per cell "
             f"(Monte Carlo standard error {100 * mcse:.1f} points at 5%). Cells: normal / t(P - 1).\n")
    s.append("| Pools x weeks | Reliability | psi 0, lambda 0 | psi 0, lambda 0.3 | psi 0.5, lambda 0 | psi 0.5, lambda 0.3 |")
    s.append("|---|---|---|---|---|---|")
    for (P, W) in ((30, 104), (40, 104)):
        for rho in ps.RELIAB:
            cells = []
            for psi, lam in ((0.0, 0.0), (0.0, 0.3), (0.5, 0.0), (0.5, 0.3)):
                r = get("size", pools=P, weeks=W, reliability=rho, psi=psi, **{"lambda": lam})
                cells.append(f"{pct(r['normal']['supportive'])} / {pct(r['t']['supportive'])}")
            s.append(f"| {P} x {W} | {rho} | " + " | ".join(cells) + " |")
    sz = [r for r in rows if r["check"] == "size"]
    s.append("")
    s.append(f"Average over the {len(sz)} cells: normal {pct(np.mean([r['normal']['supportive'] for r in sz]))}, "
             f"t {pct(np.mean([r['t']['supportive'] for r in sz]))}. Largest cell: normal "
             f"{pct(max(r['normal']['supportive'] for r in sz))}, t {pct(max(r['t']['supportive'] for r in sz))}.\n")
    s.append("### Table E. What the t correction costs (psi = 0.5, lambda = 0.3)\n")
    s.append("Cells: normal / t(P - 1). Power to support a true theory, P(supportive | gamma = 0), and to reject a false "
             "one, P(contrary | gamma = 2 delta = 0.10).\n")
    s.append("| Pools x weeks | Reliability | Support, instrument 0.3 | Support, instrument 0.6 | Reject, instrument 0.3 | Reject, instrument 0.6 |")
    s.append("|---|---|---|---|---|---|")
    for (P, W) in ((30, 104), (40, 104)):
        for rho in ps.RELIAB:
            cells = []
            for g, key in ((0.0, "supportive"), (0.10, "contrary")):
                for piz in (0.3, 0.6):
                    r = get("cost", pools=P, weeks=W, reliability=rho, pi_Z=piz, gamma=g)
                    cells.append(f"{pct(r['normal'][key])} / {pct(r['t'][key])}")
            s.append(f"| {P} x {W} | {rho} | " + " | ".join(cells) + " |")
    s.append("")
    s.append("### Table F. A wider margin: delta = 0.10 (t critical values; reliability 0.8; psi = 0.5, lambda = 0.3)\n")
    s.append("Cells: P(supportive | gamma = 0) / P(supportive | gamma = 0.10) / P(contrary | gamma = 0.20).\n")
    s.append("| Pools x weeks | Instrument 0.15 | Instrument 0.3 | Instrument 0.6 |")
    s.append("|---|---|---|---|")
    for (P, W) in ps.DESIGNS:
        cells = []
        for piz in ps.PI_ZS:
            a = get("margin", pools=P, weeks=W, pi_Z=piz, gamma=0.0)["t"]["supportive"]
            b = get("margin", pools=P, weeks=W, pi_Z=piz, gamma=0.10)["t"]["supportive"]
            c = get("margin", pools=P, weeks=W, pi_Z=piz, gamma=0.20)["t"]["contrary"]
            cells.append(f"{pct(a)} / {pct(b)} / {pct(c)}")
        s.append(f"| {P} x {W} | " + " | ".join(cells) + " |")
    text = "\n".join(s)
    Path(__file__).with_name("power_checks_summary.md").write_text(text + "\n")
    print(text)


if __name__ == "__main__":
    main()
