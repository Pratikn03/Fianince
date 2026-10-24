"""Worked examples for Chapter 4: how many reset experiments certify a question to accuracy epsilon.

For each question, memory bound and accuracy this computes, with sigma = 1, B = 1, alpha = 0.05:
  N_lower  the lower bound of Theorem thm:dich(iv): no interval certifies with fewer experiments;
  N_affine the number at which the affine interval of part (iv) certifies (an upper bound on N_cert);
  N_taylor the Taylor upper bound of part (i).
N_lower and N_affine come from the modulus: N = (2 z sigma / delta*)^2 where omega_L(delta*) = 2 epsilon,
with z = z_{1-alpha} for the lower bound and z_{1-alpha/2} for the affine interval. delta* is bracketed by
a primal certificate (pair of measures with omega above 2 epsilon) and a dual certificate (coefficient vector
with omega at most 2 epsilon), so each N is certified to lie in an interval of relative width about 1e-3.

--solve (cvxpy) computes and stores the certificates; --check (numpy) re-evaluates them with the same
rigorous primal/dual evaluation as check_modulus.py and writes or compares examples_table.tex.
"""
import argparse
import json
import math
from pathlib import Path
import sys

import numpy as np
from scipy.stats import norm

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import check_modulus as cm  # noqa: E402

OUT = HERE / "R_examples.json"
TABLE = HERE / "examples_table.tex"
ALPHA, SIGMA, B = 0.05, 1.0, 1.0
EPS = [0.1, 0.01]
Z_LO, Z_AFF = norm.ppf(1 - ALPHA), norm.ppf(1 - ALPHA / 2)


def taylor_N(name, rbar, eps):
    if name == "single_tap_m3":
        T, A = 4, 1.0
    else:
        beta = cm.QUESTIONS[name]["beta"]
        T = 1
        while B * (beta * rbar) ** T / (1 - beta * rbar) > eps / 2:
            T += 1
        A = sum(beta ** (2 * t) for t in range(T))
    return math.ceil(4 * Z_AFF ** 2 * SIGMA ** 2 * A / eps ** 2), T


def solve_pair(name, rbar, L, delta):
    import cvxpy as cp
    r = np.linspace(0, rbar, cm.GRID)
    V = r[None, :] ** np.arange(L)[:, None]
    gv = cm.g_eval(name, r)
    m1 = cp.Variable(cm.GRID, nonneg=True); m0 = cp.Variable(cm.GRID, nonneg=True)
    pr = cp.Problem(cp.Maximize(gv @ (m1 - m0)), [cp.sum(m1) <= B, cp.sum(m0) <= B, cp.norm(V @ (m1 - m0), 2) <= delta])
    pr.solve(solver="CLARABEL")
    w = m1.value - m0.value
    atoms = [[float(r[j]), float(w[j])] for j in range(cm.GRID) if abs(w[j]) > 1e-13]
    c = cp.Variable(L); sp = cp.Variable(nonneg=True); sm = cp.Variable(nonneg=True)
    h = gv - V.T @ c
    cp.Problem(cp.Minimize(delta * cp.norm(c, 2) + B * (sp + sm)), [h <= sp, -h <= sm]).solve(solver="CLARABEL")
    return atoms, [float(x) for x in c.value]


def solve():
    rows = []
    for rbar in cm.RBARS:
        L = cm.taps(rbar)
        for name in cm.QUESTIONS:
            for eps in EPS:
                target = 2 * eps
                atoms_big, c_big = solve_pair(name, rbar, L, 1e3)
                if cm.dual_upper(name, rbar, L, 1e3, np.array(c_big)) <= target:
                    # the question's range over the class is narrower than 2 eps: no data needed
                    rows.append({"rbar": rbar, "L": L, "question": name, "eps": eps, "trivial": True,
                                 "c_big": c_big})
                    print(name, rbar, eps, "trivial", flush=True)
                    continue
                lo, hi = 1e-7, 1e3
                for _ in range(60):
                    mid = math.sqrt(lo * hi)
                    atoms, c = solve_pair(name, rbar, L, mid)
                    if cm.dual_upper(name, rbar, L, mid, np.array(c)) <= target:
                        lo = mid
                    else:
                        hi = mid
                    if hi / lo < 1 + 5e-4:
                        break
                # certificates, widened by 0.2% on each side so that solver tolerance cannot blur them:
                # dual at lo (omega <= target), primal at hi (omega > target)
                lo, hi = lo * (1 - 2e-3), hi * (1 + 2e-3)
                _, c_lo = solve_pair(name, rbar, L, lo)
                atoms_hi, _ = solve_pair(name, rbar, L, hi)
                rows.append({"rbar": rbar, "L": L, "question": name, "eps": eps, "delta_lo": lo, "delta_hi": hi,
                             "c_lo": c_lo, "atoms_hi": atoms_hi, "widened": True})
                print(name, rbar, eps, lo, hi, flush=True)
    return {"rows": rows}


def evaluate(data):
    out = []
    for row in data["rows"]:
        name, rbar, L, eps = row["question"], row["rbar"], row["L"], row["eps"]
        nt, T = taylor_N(name, rbar, eps)
        if row.get("trivial"):
            # weak duality at any delta: omega(delta) <= dual value at delta = 1e3 bound needs delta <= 1e3;
            # the range bound B * psi(g - p_0) with c = 0 holds for every delta
            rng = B * cm.psi(cm.g_eval(name, np.linspace(0, rbar, cm.FINE_N)))
            assert rng <= 2 * eps
            out.append({"rbar": rbar, "question": name, "eps": eps, "N_lower_interval": (0.0, 0.0),
                        "N_affine_interval": (0.0, 0.0), "N_taylor": nt, "T_taylor": T})
            continue
        up = cm.dual_upper(name, rbar, L, row["delta_lo"], np.array(row["c_lo"]))
        low = cm.primal_lower(name, rbar, L, row["delta_hi"], row["atoms_hi"])
        assert up <= 2 * eps < low, (name, rbar, eps, up, low)
        # N with 2 z / sqrt(N) <= delta_lo suffices for the modulus condition; N with 2 z / sqrt(N) >= delta_hi fails
        n_lo = ((2 * Z_LO * SIGMA / row["delta_hi"]) ** 2, (2 * Z_LO * SIGMA / row["delta_lo"]) ** 2)
        n_aff = ((2 * Z_AFF * SIGMA / row["delta_hi"]) ** 2, (2 * Z_AFF * SIGMA / row["delta_lo"]) ** 2)
        out.append({"rbar": rbar, "question": name, "eps": eps, "N_lower_interval": n_lo,
                    "N_affine_interval": n_aff, "N_taylor": nt, "T_taylor": T})
    return out


def fmt(x, up=True):
    """Three significant figures, rounded outward: lower bounds down, upper bounds up."""
    if x == 0:
        return "0"
    e = max(int(math.floor(math.log10(x))) - 2, 0)
    v = (math.ceil if up else math.floor)(x / 10 ** e) * 10 ** e
    return f"{v:,.0f}".replace(",", "{,}")


def table(ev):
    label = {"total_feedback_Phi": "Total feedback $\\Phi$", "discounted_beta_0.8": "Discounted, $\\beta=0.8$",
             "single_tap_m3": "Single tap $k_3$"}
    lines = ["% generated by check_examples.py; do not edit", "\\newcommand{\\ExamplesRows}{%"]
    for e in ev:
        lines.append(f"{label[e['question']]} & ${e['rbar']}$ & ${e['eps']}$ & {fmt(e['N_lower_interval'][0], up=False)} & "
                     f"{fmt(e['N_affine_interval'][1])} & {fmt(e['N_taylor'])}\\\\")
    lines.append("}")
    return "\n".join(lines) + "\n"


def widen():
    """Recompute the certificates of a stored solve at deltas widened by 0.2% (same as solve() now does)."""
    data = json.loads(OUT.read_text())
    for row in data["rows"]:
        if row.get("trivial") or row.get("widened"):
            continue
        row["delta_lo"] *= 1 - 2e-3; row["delta_hi"] *= 1 + 2e-3
        _, row["c_lo"] = solve_pair(row["question"], row["rbar"], row["L"], row["delta_lo"])
        row["atoms_hi"], _ = solve_pair(row["question"], row["rbar"], row["L"], row["delta_hi"])
        row["widened"] = True
    OUT.write_text(json.dumps(data, indent=1) + "\n")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--solve", action="store_true")
    ap.add_argument("--widen", action="store_true")
    a = ap.parse_args()
    if a.widen:
        widen()
        TABLE.write_text(table(evaluate(json.loads(OUT.read_text()))))
    if a.solve:
        OUT.write_text(json.dumps(solve(), indent=1) + "\n")
        TABLE.write_text(table(evaluate(json.loads(OUT.read_text()))))
    ev = evaluate(json.loads(OUT.read_text()))
    assert TABLE.read_text() == table(ev), "examples table differs from the certificates"
    for e in ev:
        lo, aff = e["N_lower_interval"], e["N_affine_interval"]
        if lo[0] == 0:
            continue
        assert lo[1] / lo[0] < 1.01 and aff[1] / aff[0] < 1.01
        assert lo[0] <= aff[1]
    print(f"Worked examples: {len(ev)} cases certified — PASS")


if __name__ == "__main__":
    main()
