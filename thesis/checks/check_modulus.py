"""Numerical certificates for the modulus of continuity of linear questions (Theorem thm:dich).

For a linear question F_g(M) = int g dM over the positive measures on [0, rbar] of mass at most B,
observed through L taps k_t = int r^t dM, the modulus is

    omega_L(delta) = sup{ F_g(M1) - F_g(M0) : ||k(M1) - k(M0)||_2 <= delta }
                   = min_c { delta ||c||_2 + B psi(g - p_c) },   p_c(r) = sum_t c_t r^t,

with psi(h) = (sup h)_+ + (-inf h)_+ (Theorem thm:dich, part (iv)).

--solve (needs cvxpy) solves the primal on a grid and the dual over coefficient vectors and writes
R_modulus.json, including the primal measures and the dual coefficient vectors.
--check (numpy only) re-evaluates the stored objects without any solver:
  * the stored primal measures are rescaled to be exactly feasible, so their value is a rigorous
    lower bound on omega (up to floating point);
  * the stored dual vector is evaluated on a grid ten times finer, plus a Lipschitz allowance for the
    gaps between grid points, so its value is a rigorous upper bound on omega (weak duality);
  * the bracket must be tight, omega/delta must stay bounded for the single tap and for the
    discounted question, and omega/delta must grow for the total feedback Phi while
    omega/(delta sqrt(log(1/delta))) stays within fixed bounds, as Corollary cor:rates states;
  * at delta = 0 the modulus equals 2 B E_L(g), the best uniform approximation error, checked at
    small depths L where both sides are resolvable in double precision.
These are numerical checks of proved statements, not evidence for them.
"""

import argparse
import hashlib
import json
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parent
OUT = HERE / "R_modulus.json"
B = 1.0
GRID = 600
FINE = 10
FINE_N = 200001
DELTAS = [1e-1, 1e-2, 1e-3, 1e-4, 1e-5]
RBARS = [0.5, 0.9]
QUESTIONS = {
    "total_feedback_Phi": {"g": "1/(1-r)", "beta": 1.0},
    "discounted_beta_0.8": {"g": "1/(1-0.8 r)", "beta": 0.8},
    "single_tap_m3": {"g": "r^3", "beta": None},
}


def g_eval(name, r):
    if name == "single_tap_m3":
        return r ** 3
    return 1.0 / (1.0 - QUESTIONS[name]["beta"] * r)


def g_second(name, rbar):
    """Bound on |g''| over [0, rbar]."""
    if name == "single_tap_m3":
        return 6 * rbar
    b = QUESTIONS[name]["beta"]
    return 2 * b * b / (1 - b * rbar) ** 3


def taps(rbar):
    return int(np.ceil(np.log(1e-12) / np.log(rbar)))


def psi(h):
    return max(float(h.max()), 0.0) + max(-float(h.min()), 0.0)


def dual_upper(name, rbar, L, delta, c):
    """Weak-duality upper bound delta||c|| + B psi(g - p_c) over the whole interval [0, rbar].

    psi is evaluated on a grid of FINE_N points; between grid points the maximum of a function with
    |h''| <= M exceeds the larger endpoint value by at most M spacing^2 / 8, which is added twice.
    """
    r = np.linspace(0, rbar, FINE_N)
    p = np.zeros_like(r)
    for coef in c[::-1]:          # Horner
        p = p * r + coef
    h = g_eval(name, r) - p
    t = np.arange(L)
    m2 = g_second(name, rbar) + float(np.sum(np.abs(c) * t * np.maximum(t - 1, 0) * rbar ** np.maximum(t - 2, 0)))
    slack = m2 * (rbar / (FINE_N - 1)) ** 2 / 8
    return delta * float(np.linalg.norm(c)) + B * (psi(h) + 2 * slack)


def primal_lower(name, rbar, L, delta, atoms):
    """Value of a stored pair (M1, M0), rescaled to be exactly feasible: a lower bound on omega."""
    r = np.array([a[0] for a in atoms]); w = np.array([a[1] for a in atoms])
    m1, m0 = np.clip(w, 0, None), np.clip(-w, 0, None)
    scale = min(1.0, B / max(m1.sum(), 1e-300), B / max(m0.sum(), 1e-300))
    V = r[None, :] ** np.arange(L)[:, None]
    norm = float(np.linalg.norm(V @ (m1 - m0)))
    if norm > 0:
        scale = min(scale, delta / norm)
    return scale * float(g_eval(name, r) @ (m1 - m0))


def solve():
    import cvxpy as cp
    rows = []
    for rbar in RBARS:
        L = taps(rbar)
        r = np.linspace(0, rbar, GRID)
        V = r[None, :] ** np.arange(L)[:, None]
        for name in QUESTIONS:
            gv = g_eval(name, r)
            for delta in DELTAS:
                m1 = cp.Variable(GRID, nonneg=True); m0 = cp.Variable(GRID, nonneg=True)
                pr = cp.Problem(cp.Maximize(gv @ (m1 - m0)),
                                [cp.sum(m1) <= B, cp.sum(m0) <= B, cp.norm(V @ (m1 - m0), 2) <= delta])
                pr.solve(solver="CLARABEL")
                w = m1.value - m0.value
                atoms = [[float(r[j]), float(w[j])] for j in range(GRID) if abs(w[j]) > 1e-13]
                c = cp.Variable(L); sp = cp.Variable(nonneg=True); sm = cp.Variable(nonneg=True)
                h = gv - V.T @ c
                du = cp.Problem(cp.Minimize(delta * cp.norm(c, 2) + B * (sp + sm)), [h <= sp, -h <= sm])
                du.solve(solver="CLARABEL")
                rows.append({"rbar": rbar, "L": L, "question": name, "delta": delta,
                             "primal_grid": float(pr.value), "dual_grid": float(du.value),
                             "atoms": atoms, "c": [float(x) for x in c.value]})
                print(f"rbar={rbar} {name:22s} delta={delta:.0e} primal={pr.value:.6g} dual={du.value:.6g}")
    return {"rows": rows}


def check(data):
    out = []
    for row in data["rows"]:
        name, rbar, L, delta = row["question"], row["rbar"], row["L"], row["delta"]
        lo = primal_lower(name, rbar, L, delta, row["atoms"])
        hi = dual_upper(name, rbar, L, delta, np.array(row["c"]))
        out.append({"rbar": rbar, "question": name, "delta": delta, "L": L,
                    "omega_lower": lo, "omega_upper": hi,
                    "relative_gap": (hi - lo) / hi if hi > 0 else 0.0,
                    "omega_over_delta": hi / delta if delta > 0 else None,
                    "omega_over_delta_sqrtlog": hi / (delta * np.sqrt(np.log(1 / delta))) if delta > 0 else None})
    res = {"brackets": out}
    pos = [o for o in out if o["delta"] > 0]
    res["max_relative_gap"] = max(o["relative_gap"] for o in pos)
    res["brackets_tight"] = bool(res["max_relative_gap"] < 5e-3)
    growth = {}
    for rbar in RBARS:
        for name in QUESTIONS:
            seq = [o for o in pos if o["rbar"] == rbar and o["question"] == name]
            seq.sort(key=lambda o: -o["delta"])
            od = [o["omega_over_delta"] for o in seq]
            ol = [o["omega_over_delta_sqrtlog"] for o in seq]
            growth[f"{name}@{rbar}"] = {"omega_over_delta": od, "omega_over_delta_sqrtlog": ol,
                                        "ratio_last_first": od[-1] / od[0]}
    res["growth"] = growth
    # parametric questions: omega/delta has converged (changes by under 1% over the last decade)
    res["parametric_bounded"] = bool(all(abs(growth[f"{n}@{rb}"]["omega_over_delta"][-1]
                                             / growth[f"{n}@{rb}"]["omega_over_delta"][-2] - 1) < 0.01
                                         for n in ("discounted_beta_0.8", "single_tap_m3") for rb in RBARS))
    # total feedback: omega/delta increases by more than 3% in every decade; omega/(delta sqrt log)
    # stays in [0.5, 6]
    res["Phi_grows"] = bool(all(np.all(np.array(growth[f"total_feedback_Phi@{rb}"]["omega_over_delta"][1:])
                                       / np.array(growth[f"total_feedback_Phi@{rb}"]["omega_over_delta"][:-1]) > 1.03)
                                for rb in RBARS))
    res["Phi_sqrtlog_band"] = bool(all(0.5 <= x <= 6 for rb in RBARS
                                       for x in growth[f"total_feedback_Phi@{rb}"]["omega_over_delta_sqrtlog"]))
    res["all_pass"] = bool(res["brackets_tight"] and res["parametric_bounded"] and res["Phi_grows"]
                           and res["Phi_sqrtlog_band"])
    return res


def zero_identity_check():
    """omega_L(0) = 2 B E_L(g) for small L: solve both sides on the fine grid (numpy + scipy only)."""
    from scipy.optimize import linprog
    rows = []
    for rbar in RBARS:
        r = np.linspace(0, rbar, 2000)
        for name in QUESTIONS:
            for L in (1, 2, 3):
                gv = g_eval(name, r)
                V = r[:, None] ** np.arange(L)[None, :]
                A = np.vstack([np.hstack([-V, -np.ones((len(r), 1))]), np.hstack([V, -np.ones((len(r), 1))])])
                e = linprog(np.r_[np.zeros(L), 1.0], A_ub=A, b_ub=np.concatenate([-gv, gv]),
                            bounds=[(None, None)] * L + [(0, None)], method="highs").x[-1]
                # primal at delta = 0: max g.(m1 - m0), V^T(m1 - m0) = 0, masses <= B
                n = len(r)
                Aeq = np.hstack([V.T, -V.T])
                Aub = np.vstack([np.r_[np.ones(n), np.zeros(n)], np.r_[np.zeros(n), np.ones(n)]])
                p = linprog(-np.r_[gv, -gv], A_ub=Aub, b_ub=[B, B], A_eq=Aeq, b_eq=np.zeros(L),
                            bounds=[(0, None)] * (2 * n), method="highs")
                rows.append({"rbar": rbar, "question": name, "L": L, "omega0": float(-p.fun), "two_B_E_L": 2 * B * e,
                             "match": bool(abs(-p.fun - 2 * B * e) < 1e-7 * max(1, 2 * B * e))})
    return rows


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--solve", action="store_true")
    ap.add_argument("--check", action="store_true")
    a = ap.parse_args()
    if a.solve:
        data = solve()
        data["schema"] = "modulus-v1"
        data["script_sha256"] = hashlib.sha256(Path(__file__).read_bytes()).hexdigest()
        res = check(data)
        res["zero_identity"] = zero_identity_check()
        res["zero_identity_pass"] = all(z["match"] for z in res["zero_identity"])
        data["check"] = res
        OUT.write_text(json.dumps(data, indent=1) + "\n")
    data = json.loads(OUT.read_text())
    res = check(data)
    res["zero_identity"] = zero_identity_check()
    res["zero_identity_pass"] = all(z["match"] for z in res["zero_identity"])
    stored = data["check"]
    for k in ("brackets_tight", "parametric_bounded", "Phi_grows", "Phi_sqrtlog_band", "all_pass", "zero_identity_pass"):
        assert res[k] == stored[k], (k, res[k], stored[k])
    assert res["all_pass"] and res["zero_identity_pass"], {k: res[k] for k in res if isinstance(res[k], bool)}
    for k, v in res["growth"].items():
        print(f"{k:32s} omega/delta: " + " ".join(f"{x:.3f}" for x in v["omega_over_delta"]))
    print(f"max relative bracket gap {res['max_relative_gap']:.2e}; omega_L(0)=2B E_L(g) on {len(res['zero_identity'])} cases")
    print("Modulus certificates: PASS")


if __name__ == "__main__":
    main()
