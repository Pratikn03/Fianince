"""Deterministic A1 diagnostics; no empirical data or simulation is used.

Check a valid fixed-atom parametric obstruction and the proposed quadrature
construction separately. A fitted parametric slope is NOT evidence for the
open coefficient-energy lower bound. Run with --check to compare the committed
result instead of rewriting it. --require-full fails while A1 is unresolved.
"""

import argparse
import hashlib
import json
import math
from pathlib import Path

import numpy as np


def run():
    rbar, mass, sigma, alpha = 0.8, 1.0, 1.0, 0.1
    atom = rbar / 2
    epsilons = np.geomspace(1e-5, 1e-2, 9)
    cases = {
        "safety": lambda r: 1 / (1 - r),
        "single_tap": lambda r: r**3,
        "discounted": lambda r: 1 / (1 - 0.5 * r),
    }
    fixed_atom = {}
    for name, g in cases.items():
        value = float(g(atom))
        rows = []
        for eps in epsilons:
            # Same support, different masses: M0=(B/4)delta_r,
            # M1=(B/4+lambda)delta_r. All infinitely many taps are allowed.
            lam = 3 * float(eps) / abs(value)
            n_budget = sigma**2 * (1 - atom**2) / lam**2
            kl_infinite = n_budget * lam**2 / (2 * sigma**2 * (1 - atom**2))
            kl_finite = n_budget * lam**2 * sum(atom**(2*t) for t in range(64)) / (2*sigma**2)
            rows.append({
                "epsilon": float(eps), "mass_difference": lam,
                "functional_gap": lam * abs(value), "N_KL_budget": n_budget,
                "KL_infinite": kl_infinite, "KL_first_64": kl_finite,
                "admissible": bool(mass/4 + lam <= mass),
                "separated": bool(lam * abs(value) > 2 * eps),
            })
        slope = float(np.polyfit(np.log(epsilons), np.log([r["N_KL_budget"] for r in rows]), 1)[0])
        ok = all(r["admissible"] and r["separated"] and
                 abs(r["KL_infinite"] - 0.5) < 1e-12 and
                 r["KL_first_64"] <= 0.5 + 1e-12 for r in rows)
        fixed_atom[name] = {"rows": rows, "log_log_slope": slope,
                            "checks_pass": bool(ok and abs(slope + 2) < 1e-10)}

    # P_n + P_(n-1) has the left endpoint and the Radau interior nodes.
    # Solve moment equations for weights rather than use the old incorrect
    # Jacobi-weight conversion. Check exactness before interpreting a pair.
    quadrature = []
    for n in range(2, 7):
        gauss, wg = np.polynomial.legendre.leggauss(n)
        wg = wg / 2
        pn = np.polynomial.legendre.Legendre.basis(n)
        pm = np.polynomial.legendre.Legendre.basis(n-1)
        radau = np.real_if_close((pn + pm).roots(), tol=1000)
        if np.iscomplexobj(radau):
            raise ValueError("Radau nodes must be real")
        rhs = np.array([0 if j % 2 else 1/(j+1) for j in range(n)])
        wr = np.linalg.solve(np.vander(radau, N=n, increasing=True).T, rhs)
        exact_error = max(abs(float(wr @ radau**j) - (0 if j % 2 else 1/(j+1)))
                          for j in range(2*n-1))
        rg, rr = rbar*(gauss+1)/2, rbar*(radau+1)/2
        early = [mass/2 * float(wg @ rg**j - wr @ rr**j) for j in range(n)]
        gaps = {name: abs(mass/2 * float(wg @ g(rg) - wr @ g(rr))) for name, g in cases.items()}
        quadrature.append({
            "nodes_per_rule": n, "radau_exactness_error": exact_error,
            "weights_positive": bool(np.all(wr > 0)),
            "matched_tap_max_error": max(abs(x) for x in early),
            "functional_gaps": gaps,
            "checks_pass": bool(exact_error < 1e-10 and np.all(wr > 0)
                                 and max(abs(x) for x in early) < 1e-10),
        })
    # Analytic family g_m=(eps/B)[(1-r/rbar)^m+eta/(1-beta*r)].
    # Its eventual coefficients are strictly positive, but its range gives
    # a deterministic interval narrower than eps without observing anything.
    eta, beta, eps0 = 0.125, 0.5, 0.01
    remainder_bound = eta / (1-beta*rbar)
    counterexamples = []
    for m in [4, 8, 16, 32, 64, 128]:
        upper = eps0 * (1+remainder_bound)
        a1 = eps0 / mass * (-m/rbar + eta*beta)
        # For every T<=m the alternating binomial tail at rbar has
        # magnitude at least eps0*(1-remainder_bound); T=m+1 suffices.
        tail_lower = eps0 * (1-remainder_bound)
        terminal_tail = eps0 * eta * (beta*rbar)**(m+1) / (1-beta*rbar)
        identity_ok = all(sum((-1)**t * math.comb(m, t) for t in range(T, m+1))
                          == (-1)**T * math.comb(m-1, T-1) for T in range(1, m+1))
        counterexamples.append({
            "degree": m, "T_g": m+1, "binomial_identity_pass": identity_ok,
            "no_data_interval_half_width": upper/2,
            "early_tail_lower_bound": tail_lower,
            "tail_at_T_g": terminal_tail,
            "first_two_energy_over_epsilon_sq_lower_bound": a1*a1/eps0**2,
            "checks_pass": bool(identity_ok and upper/2 < eps0 and tail_lower > eps0/2
                                 and terminal_tail <= eps0/2),
        })
    passed = all(r["checks_pass"] for r in fixed_atom.values()) and all(r["checks_pass"] for r in quadrature) and all(r["checks_pass"] for r in counterexamples)
    return {
        "schema": "A1-deterministic-diagnostics-v1",
        "script_sha256": hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
        "parameters": {"B": mass, "rbar": rbar, "sigma": sigma, "alpha": alpha, "atom": atom},
        "fixed_atom": fixed_atom, "quadrature": quadrature,
        "uniform_counterexample": {"epsilon": eps0, "eta": eta, "beta": beta, "rows": counterexamples},
        "diagnostics_pass": passed,
        "matching_energy_lower_bound_established": False,
        "uniform_statement_refuted": True,
        "interpretation": "Only the fixed-atom epsilon^-2 obstruction is checked. The quadrature pair has zero early tap direction. No A_g(T) factor is proved. The uniform statement is refuted by a cancellation family; function-specific small-epsilon asymptotics are not settled. No Lean proof is supplied.",
    }


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--check", action="store_true")
    parser.add_argument("--require-full", action="store_true")
    args = parser.parse_args()
    result = run()
    output = Path(__file__).with_name("R_dich_lower.json")
    if args.check:
        stored = json.loads(output.read_text())
        # Numeric tolerance permits harmless platform-dependent eigensolver differences.
        def same(a, b):
            if isinstance(a, dict):
                return isinstance(b, dict) and a.keys() == b.keys() and all(same(a[k], b[k]) for k in a)
            if isinstance(a, list):
                return isinstance(b, list) and len(a) == len(b) and all(same(x, y) for x, y in zip(a, b))
            if isinstance(a, float):
                return isinstance(b, (int, float)) and bool(np.isclose(a, b, rtol=1e-10, atol=1e-12))
            return a == b
        if not same(result, stored):
            raise SystemExit("A1 result differs from deterministic recomputation")
    else:
        output.write_text(json.dumps(result, indent=2, allow_nan=False) + "\n")
    print("A1 deterministic diagnostics:", "PASS" if result["diagnostics_pass"] else "FAIL")
    print("A1 uniform statement: counterexample verified numerically; written proof not Lean-formalized")
    print("A1 repaired matching lower bound: OPEN (not validated)")
    return 0 if result["diagnostics_pass"] and not args.require_full else 1


if __name__ == "__main__":
    raise SystemExit(main())
