#!/usr/bin/env python3
"""
Experiment 14: Exact Minimum Capital for Identification Probes and the Value of Adaptivity.

Closes the open gate left by exp13 (the pulse class is not optimal; Theorem 2.9's constant is
not tight) with two results that hold for the SAME price-first economy and ledger as exp13.

Model (exp13): price x = H_i * v (causal LTI, impulse response h^i, h_0 = kappa), fills at
P + pre_t + kappa v_t / 2, observations y_t = x_t + eps_t, eps_t iid N(0, sigma^2).

Identity (verified numerically below). For every finitely supported trade sequence v that ends
flat (sum v = 0) the fee-free ledger loss under hypothesis i is the Toeplitz quadratic form
    L_i(v) = sum_{s<t} h^i_{t-s} v_t v_s + (kappa/2) sum_t v_t^2
           = (1/2pi) int g_i(w) |V(w)|^2 dw,      g_i(w) = Re H_i(e^{iw}) - kappa/2.
Information over ANY observation window is at most (1/2pi) int |dH(w)|^2 |V(w)|^2 dw.

Theorem A (deterministic probes). If g_i > 0 (no round-trip arbitrage), every eventually-flat
deterministic probe reaching symmetric error alpha has
    L_i(v) >= 4 sigma^2 z_{1-alpha}^2 * inf_w g_i(w) / |dH(w)|^2 =: C_i^*,
and C_i^* is the infimum (approached by windowed sinusoids at the minimising frequency).

Theorem B (adaptive / sequential probes). For any non-anticipating, possibly randomised policy
with a stopping time and errors alpha (under H0) and beta (under H1), closing flat,
    E_0[L_0(v)] >= 2 sigma^2 kl(alpha, 1-beta) * inf_w g_0(w)/|dH(w)|^2,
so adaptivity can reduce expected quadratic loss by at most the factor kl(alpha,1-beta)/(2 z^2)
(0.4898 at alpha=beta=0.05). Proof: chain rule for KL with adapted inputs, Parseval path by
path, and the data-processing inequality for the decision event.

Fees: with per-trade cap |v_t| <= V_eff, ||v||_1 >= ||v||_2^2 / V_eff and
||v||_2^2 >= KL-energy / sup|dH|^2, giving an additive fee lower bound.
"""
import json
import sys
from pathlib import Path

import numpy as np
from scipy.optimize import minimize, minimize_scalar
from scipy.stats import norm

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from breakthrough_experiments.exp13_account_capital import (  # noqa: E402
    PARAMS, evaluate, executable_optimal, kl as exp13_kl, simulate_account, theorem_2_9_lower_bound,
    price_path,
)

ALPHA = 0.05
Z = norm.ppf(1 - ALPHA)
T_IMPULSE = 4000


def impulse(delta, split, p=PARAMS, T=T_IMPULSE):
    v = np.zeros(T)
    v[0] = 1.0
    return price_path(v, delta, split, p)


def transfer(h, om):
    k = np.arange(len(h))
    return np.exp(-1j * np.outer(om, k)) @ h


def binary_kl(a, b):
    return a * np.log(a / b) + (1 - a) * np.log((1 - a) / (1 - b))


def spectral_quantities(delta, p=PARAMS, n_grid=8001):
    h0, h1 = impulse(delta, False, p), impulse(delta, True, p)
    dh = h1 - h0

    def parts(om):
        om = np.atleast_1d(om)
        H0, H1, dH = transfer(h0, om), transfer(h1, om), transfer(dh, om)
        return H0.real - p["kappa"] / 2, H1.real - p["kappa"] / 2, np.abs(dH) ** 2

    grid = np.linspace(1e-4, np.pi, n_grid)
    g0, g1, d2 = parts(grid)
    out = dict(min_g0=float(g0.min()), min_g1=float(g1.min()))
    for name, gi in (("0", g0), ("1", g1)):
        i = int(np.argmin(gi / d2))
        lo, hi = grid[max(i - 1, 0)], grid[min(i + 1, n_grid - 1)]
        idx = 0 if name == "0" else 1
        res = minimize_scalar(lambda w: float(parts(w)[idx][0] / parts(w)[2][0]), bounds=(lo, hi),
                              method="bounded", options=dict(xatol=1e-10))
        out[f"inf_ratio_{name}"] = float(res.fun)
        out[f"omega_star_{name}"] = float(res.x)
    j = int(np.argmax(d2))
    out["sup_dH2"] = float(d2[j])
    out["omega_dHmax"] = float(grid[j])
    return out


def theorem_bounds(delta, p=PARAMS, alpha=ALPHA, beta=ALPHA):
    s = spectral_quantities(delta, p)
    c = 4 * p["sigma"] ** 2 * Z ** 2                        # required ||dx||^2, deterministic
    klb = binary_kl(alpha, 1 - beta)
    c_adapt = 2 * p["sigma"] ** 2 * klb                      # required E||dx||^2, any policy
    fee = p["phi"] * p["P"]
    fee_det = fee * max(np.sqrt(c / s["sup_dH2"]), c / (s["sup_dH2"] * p["V_eff"]))
    fee_adapt = fee * c_adapt / (s["sup_dH2"] * p["V_eff"])
    quad_det = max(c * s["inf_ratio_0"], c * s["inf_ratio_1"])
    quad_adapt0 = c_adapt * s["inf_ratio_0"]
    return dict(delta=delta, spectral=s, required_dx2_deterministic=c, binary_kl=float(klb),
                adaptive_factor=float(klb / (2 * Z ** 2)),
                quad_loss_lower_bound_deterministic=float(quad_det),
                fee_lower_bound_deterministic=float(fee_det),
                capital_lower_bound_deterministic=float(quad_det + fee_det),
                quad_loss_lower_bound_adaptive_expected_H0=float(quad_adapt0),
                fee_lower_bound_adaptive_expected=float(fee_adapt),
                capital_lower_bound_adaptive_expected=float(quad_adapt0 + fee_adapt),
                delta4_times_quad_bound=float(delta ** 4 * quad_det),
                theorem_2_9_bound=theorem_2_9_lower_bound(delta, p=p))


def toeplitz_identity_check(delta=0.05, n=25, seed=0, p=PARAMS):
    """Ledger fee-free loss of random flat probes vs the Toeplitz quadratic form (Theorem identity)."""
    rng = np.random.default_rng(seed)
    h0 = impulse(delta, False, p, T=400)
    worst = 0.0
    for _ in range(n):
        L = int(rng.integers(5, 60))
        v = rng.normal(size=L)
        v[-1] -= v.sum()
        vv = np.concatenate([v, np.zeros(300)])
        ledger = -simulate_account(vv, delta, False, p, fees=False)["final_pnl"]
        M = np.empty((L, L))
        for t in range(L):
            for s_ in range(L):
                M[t, s_] = p["kappa"] / 2 if t == s_ else 0.5 * h0[abs(t - s_)]
        worst = max(worst, abs(ledger - v @ M @ v) / max(1.0, abs(ledger)))
    return float(worst)


def _matrices(delta, L, tail, p=PARAMS):
    """G (fee-free flat round-trip cost, H0 and H1) and M = D^T D on free coordinates u in R^L."""
    h0 = impulse(delta, False, p, T=L + 1 + tail)
    h1 = impulse(delta, True, p, T=L + 1 + tail)
    n = L + 1
    E = np.zeros((n, L)); E[:L, :L] = np.eye(L); E[L, :] = -1.0      # v = E u, flat by construction

    def toe(h):
        M = np.empty((n, n))
        for t in range(n):
            for s_ in range(n):
                M[t, s_] = p["kappa"] / 2 if t == s_ else 0.5 * h[abs(t - s_)]
        return E.T @ M @ E

    Tn = n + tail
    conv = np.zeros((Tn, n))
    dh = h1 - h0
    for j in range(n):
        conv[j:, j] = dh[:Tn - j]
    D = conv @ E
    return toe(h0), toe(h1), D.T @ D, E


def optimise_design(delta, L, tail=80, p=PARAMS):
    """Minimise smooth proxy max(G0,G1)-loss + fees s.t. KL >= target, then evaluate in the ledger."""
    G0, G1, M, E = _matrices(delta, L, tail, p)
    c = 4 * p["sigma"] ** 2 * Z ** 2
    # eigen design from the Toeplitz form (identical to the ledger form, see toeplitz_identity_check)
    from scipy.linalg import eigh
    _, vecs = eigh(M, G0)
    u0 = vecs[:, -1] * np.sqrt(c / (vecs[:, -1] @ M @ vecs[:, -1]))
    v0 = np.concatenate([E @ u0, np.zeros(tail)])
    fee = p["phi"] * p["P"]
    eps = 1e-6

    def f(u):
        v = E @ u
        return u @ G0 @ u + fee * np.sum(np.sqrt(v * v + eps))

    def fgrad(u):
        v = E @ u
        return 2 * G0 @ u + fee * E.T @ (v / np.sqrt(v * v + eps))

    cons = [dict(type="ineq", fun=lambda u: u @ M @ u - c, jac=lambda u: 2 * M @ u),
            dict(type="ineq", fun=lambda u: p["V_eff"] ** 2 - (E @ u) ** 2,
                 jac=lambda u: -2 * (E @ u)[:, None] * E)]
    res = minimize(f, u0, jac=fgrad, constraints=cons, method="SLSQP",
                   options=dict(maxiter=400, ftol=1e-10))
    u = res.x if res.success or f(res.x) < f(u0) else u0
    u = u * np.sqrt(c / (u @ M @ u)) if u @ M @ u < c else u     # restore exact feasibility
    v = np.concatenate([E @ u, np.zeros(tail)])
    ev_opt = evaluate(v, delta, f"optimised probe L={L}", p)
    ev_eig = evaluate(v0, delta, f"eigen probe L={L}", p)
    return ev_opt, ev_eig


def best_feasible_design(delta, Ls=None, p=PARAMS, displacement_cap=5.0):
    if Ls is None:
        Ls = (40, 60, 90, 120, 160, 220) + ((320, 450) if delta < 0.04 else ())
    best = None
    rows = []
    for L in Ls:
        for ev in optimise_design(delta, L, p=p):
            ok = (ev["meets_5pct"] and ev["max_abs_trade"] <= p["V_eff"] + 1e-9
                  and ev["max_price_displacement"] <= displacement_cap + 1e-9 and abs(ev["end_inventory"]) < 1e-8)
            ev["feasible"] = bool(ok)
            rows.append(ev)
            if ok and (best is None or ev["C0_required"] < best["C0_required"]):
                best = ev
    return best, rows


def sequential_probe_mc(delta=0.05, n_blocks_max=40, block_frac=0.1, L=40, tail=40, n_paths=20000,
                        alpha=ALPHA, beta=ALPHA, seed=1, p=PARAMS):
    """Wald SPRT over repeated flat blocks; exact LLR on the full observed path; ledger losses."""
    vb, _ = executable_optimal(delta, L=L, tail=tail, p=p)
    vb = vb * np.sqrt(block_frac)                       # each block carries ~block_frac of the KL target
    B = len(vb)
    v = np.tile(vb, n_blocks_max)
    x0, x1 = price_path(v, delta, False, p), price_path(v, delta, True, p)
    dx = x1 - x0
    ends = np.arange(1, n_blocks_max + 1) * B
    loss0 = np.array([-simulate_account(np.concatenate([v[:e], np.zeros(200)]), delta, False, p)["final_pnl"]
                      for e in ends])
    loss1 = np.array([-simulate_account(np.concatenate([v[:e], np.zeros(200)]), delta, True, p)["final_pnl"]
                      for e in ends])
    loss0_q = np.array([-simulate_account(np.concatenate([v[:e], np.zeros(200)]), delta, False, p,
                                          fees=False)["final_pnl"] for e in ends])
    energy = np.cumsum(dx ** 2)[ends - 1]               # ||dx||^2 observed up to each block end
    up, lo = np.log((1 - beta) / alpha), np.log(beta / (1 - alpha))   # LLR = log p1/p0
    rng = np.random.default_rng(seed)
    s2 = p["sigma"] ** 2
    out = {}
    for name, truth in (("H0", x0), ("H1", x1)):
        decide1 = np.zeros(n_paths, bool)
        nstop = np.full(n_paths, n_blocks_max)
        chunk = 2000
        for c0 in range(0, n_paths, chunk):
            m = min(chunk, n_paths - c0)
            y = truth[None, :] + p["sigma"] * rng.standard_normal((m, len(v)))
            inc = ((y - x0) ** 2 - (y - x1) ** 2) / (2 * s2)
            llr = np.cumsum(inc, axis=1)[:, ends - 1]
            hit_up, hit_lo = llr >= up, llr <= lo
            first = np.where((hit_up | hit_lo).any(1), np.argmax(hit_up | hit_lo, axis=1), n_blocks_max - 1)
            nstop[c0:c0 + m] = first + 1
            decide1[c0:c0 + m] = llr[np.arange(m), first] >= 0
        k = nstop - 1
        L_use = loss0 if name == "H0" else loss1
        out[name] = dict(error=float(decide1.mean() if name == "H0" else 1 - decide1.mean()),
                         mean_blocks=float(nstop.mean()), mean_loss=float(L_use[k].mean()),
                         p99_loss=float(np.quantile(L_use[k], 0.99)), max_loss=float(L_use[k].max()),
                         mean_info_energy=float(energy[k].mean()),
                         mean_quad_loss_H0=float(loss0_q[k].mean()) if name == "H0" else None)
    a_hat, b_hat = out["H0"]["error"], out["H1"]["error"]
    kl_needed = binary_kl(max(a_hat, 1e-6), 1 - max(b_hat, 1e-6)) if a_hat + b_hat < 1 else 0.0
    out["chain_rule_check"] = dict(E0_KL=out["H0"]["mean_info_energy"] / (2 * s2), kl_alpha_beta=float(kl_needed),
                                   holds=bool(out["H0"]["mean_info_energy"] / (2 * s2) >= kl_needed - 1e-9))
    out["deterministic_blocks_needed"] = int(np.argmax(energy >= 4 * s2 * Z ** 2) + 1)
    out["deterministic_loss"] = float(loss0[out["deterministic_blocks_needed"] - 1])
    out["block_frac"] = block_frac
    return out


def run_experiment():
    p = PARAMS
    deltas = [0.02, 0.03, 0.05, 0.08, 0.10, 0.15]
    identity_err = toeplitz_identity_check()
    sweep = []
    for d in deltas:
        b = theorem_bounds(d, p)
        best, _ = best_feasible_design(d, p=p)
        b["best_feasible_design"] = best
        b["upper_bound_capital"] = best["C0_required"] if best else None
        b["gap_ratio_upper_over_lower"] = (best["C0_required"] / b["capital_lower_bound_deterministic"]) if best else None
        sweep.append(b)
        print(f"delta={d:.2f}  LB_det={b['capital_lower_bound_deterministic']:.3f}  "
              f"UB={b['upper_bound_capital'] if best else float('nan'):.3f}  LB_adapt={b['capital_lower_bound_adaptive_expected']:.3f}"
              f"  d^4*LBquad={b['delta4_times_quad_bound']:.3e}  Thm2.9={b['theorem_2_9_bound']:.2e}  "
              f"omega*={b['spectral']['omega_star_0']:.4f}")
    _, rows05 = best_feasible_design(0.05, p=p)
    seq = sequential_probe_mc(0.05)
    print("sequential:", json.dumps(seq, indent=1))
    out = dict(parameters=p, alpha=ALPHA, toeplitz_identity_max_rel_error=identity_err, sweep=sweep,
               designs_delta_0_05=rows05, sequential_mc_delta_0_05=seq)
    Path(ROOT / "breakthrough_experiments/results_exp14_capital_frontier_exact.json").write_text(
        json.dumps(out, indent=2, default=float))
    print(f"Toeplitz identity max rel. error: {identity_err:.2e}")
    return out


if __name__ == "__main__":
    run_experiment()
