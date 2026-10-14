#!/usr/bin/env python3
"""
Experiment 13: Account-Level Capital for Identification Probes (audit finding 4, Oct 11 85-page audit).

Replaces formula-only capital with an explicit trader account in the same price-first
closed-loop economy used by exp4/exp7:
    pre_t   = a x_t + kappa * sum_k w_k y_{k,t}                (price before our trade)
    exec_t  = P* + pre_t + kappa v_t / 2                       (average fill, linear book)
    cash   -= v_t exec_t + phi P* |v_t|;   inv += v_t
    x_{t+1} = pre_t + kappa v_t;  y_{k,t+1} = (1-eta_k) y_{k,t} + eta_k x_{t+1}
    mark_t = P* + x_{t+1};  equity_t = cash + inv * mark_t;  margin_t = mu |inv| mark_t
Required initial capital C0 = max_t (margin_t - equity_t), maximised over BOTH hypotheses
(the trader does not know which economy is true). Information: exact Gaussian KL of the
full price path, D = ||x^{H1} - x^{H0}||^2 / (2 sigma^2), including the unwind legs.

Questions answered:
  (1) Is the 12-pulse 'benchmark' (193.62) a real account requirement?
  (2) What do resets cost when the unwinds are executed and recorded?
  (3) Is the isolated-pulse design minimal among deterministic probes?
"""
import json
from pathlib import Path
import numpy as np
from scipy.linalg import eigh
from scipy.stats import norm

PARAMS = dict(kappa=0.8, q=0.2, a=0.5, eta=0.4, sigma=0.01, phi=0.0004, P=100.0, mu=0.005, V_eff=6.25)
Z = norm.ppf(0.95)
KL_TARGET = 2.0 * Z**2


def _cohorts(delta, split, p):
    if split:
        return np.array([p["eta"] - delta, p["eta"] + delta]), np.array([p["q"] / 2, p["q"] / 2])
    return np.array([p["eta"]]), np.array([p["q"]])


def price_path(v, delta, split, p=PARAMS):
    rates, w = _cohorts(delta, split, p)
    x, y = 0.0, np.zeros(len(rates))
    out = np.zeros(len(v))
    for t, vt in enumerate(v):
        x = p["a"] * x + p["kappa"] * (w @ y) + p["kappa"] * vt
        y = (1 - rates) * y + rates * x
        out[t] = x
    return out


def simulate_account(v, delta, split, p=PARAMS, fees=True):
    """Event-sourced account. Returns dict with C0, final P&L, ledger summary."""
    rates, w = _cohorts(delta, split, p)
    phi = p["phi"] if fees else 0.0
    x, y = 0.0, np.zeros(len(rates))
    cash, inv = 0.0, 0.0
    need, peak_margin, peak_inv, n_trades, gross = 0.0, 0.0, 0.0, 0, 0.0
    for vt in v:
        pre = p["a"] * x + p["kappa"] * (w @ y)
        if vt != 0.0:
            exec_p = p["P"] + pre + 0.5 * p["kappa"] * vt
            cash -= vt * exec_p + phi * p["P"] * abs(vt)
            inv += vt
            n_trades += 1
            gross += abs(vt)
        x = pre + p["kappa"] * vt
        y = (1 - rates) * y + rates * x
        mark = p["P"] + x
        equity = cash + inv * mark
        margin = p["mu"] * abs(inv) * mark
        need = max(need, margin - equity)
        peak_margin = max(peak_margin, margin)
        peak_inv = max(peak_inv, abs(inv))
    return dict(C0=float(need), final_pnl=float(cash + inv * (p["P"] + x)), end_inventory=float(inv),
                peak_margin=float(peak_margin), peak_inventory=float(peak_inv), n_trades=n_trades,
                gross_quantity=float(gross))


def kl(v, delta, p=PARAMS):
    d = price_path(v, delta, True, p) - price_path(v, delta, False, p)
    return float(d @ d / (2 * p["sigma"] ** 2))


def err(D):
    return float(norm.cdf(-np.sqrt(D / 2)))


def evaluate(v, delta, label, p=PARAMS):
    a0 = simulate_account(v, delta, False, p)
    a1 = simulate_account(v, delta, True, p)
    D = kl(v, delta, p)
    return dict(design=label, C0_required=max(a0["C0"], a1["C0"]), C0_H0=a0["C0"], C0_H1=a1["C0"],
                final_pnl_H0=a0["final_pnl"], final_pnl_H1=a1["final_pnl"], end_inventory=a0["end_inventory"],
                peak_margin=max(a0["peak_margin"], a1["peak_margin"]), peak_inventory=a0["peak_inventory"],
                n_trades=a0["n_trades"], gross_quantity=a0["gross_quantity"],
                max_abs_trade=float(np.max(np.abs(v))),
                max_price_displacement=float(np.max(np.abs(price_path(v, delta, False, p)))),
                KL=D, testing_error=err(D), meets_5pct=bool(err(D) <= 0.05 + 1e-9))


def pulse_train(signs, spacing, V, tail=60):
    v = np.zeros(len(signs) * spacing + tail)
    for j, s in enumerate(signs):
        v[j * spacing] = s * V
    return v


def executable_optimal(delta, L=120, tail=80, p=PARAMS):
    """Maximise KL per unit of fee-free executable round-trip cost (generalised eigenproblem)."""
    def rt_cost(u):
        vv = np.concatenate([u, [-np.sum(u)], np.zeros(tail)])
        return -simulate_account(vv, delta, False, p, fees=False)["final_pnl"]

    G = np.zeros((L, L))
    for i in range(L):
        e = np.zeros(L); e[i] = 1.0
        G[i, i] = rt_cost(e)
    for i in range(L):
        for j in range(i + 1, L):
            e = np.zeros(L); e[i] = 1.0; e[j] = 1.0
            G[i, j] = G[j, i] = 0.5 * (rt_cost(e) - G[i, i] - G[j, j])
    Lfull = L + 1 + tail
    D = np.zeros((Lfull, L))
    for j in range(L):
        u = np.zeros(L); u[j] = 1.0
        vv = np.concatenate([u, [-1.0], np.zeros(tail)])
        D[:, j] = price_path(vv, delta, True, p) - price_path(vv, delta, False, p)
    vals, vecs = eigh(D.T @ D, G)
    u = vecs[:, -1]
    u *= np.sqrt(2 * p["sigma"] ** 2 * KL_TARGET / (u @ D.T @ D @ u))
    v = np.concatenate([u, [-np.sum(u)], np.zeros(tail)])
    return v, float(np.linalg.eigvalsh(G)[0])


def theorem_2_9_lower_bound(delta, alpha=0.05, p=PARAMS):
    eps = min(p["eta"] - delta, 1 - (p["eta"] + delta))
    S = p["a"] + p["kappa"] * p["q"]
    r = 1 - eps * (1 - S)
    m = p["kappa"] * (1 - r) / (1 + r)
    Kst = 2 * p["kappa"] ** 2 * p["q"] / (eps ** 3 * (1 - S) ** 2)
    return float(2 * p["sigma"] ** 2 * m * (1 - 2 * alpha) ** 2 / (Kst ** 2 * delta ** 4))


def run_experiment(delta=0.05):
    p = PARAMS
    V = p["V_eff"]
    benchmark_formula = 12 * (0.5 * p["kappa"] * V**2 + p["phi"] * p["P"] * V) + p["mu"] * p["P"] * V
    designs = [
        evaluate(pulse_train([1] * 12, 20, V), delta, "12 buys, T=20 apart, never unwound"),
        evaluate(pulse_train([1, -1] * 6, 20, V), delta, "6 buy/sell round trips, every leg informative"),
        evaluate(pulse_train([1, -1] * 5, 20, V), delta, "5 buy/sell round trips, every leg informative"),
        evaluate(pulse_train([1, -1] * 12, 20, V), delta, "12 buys each unwound after 20 steps (24 legs)"),
    ]
    v_opt_120, min_eig = executable_optimal(delta, L=120)
    designs.append(evaluate(v_opt_120, delta, "executable-cost optimal deterministic probe (L=120)"))
    designs.append(evaluate(v_opt_120, delta, "generalized-eigenvector candidate probe (L=120)"))
    v_opt_160, _ = executable_optimal(delta, L=160)
    designs.append(evaluate(v_opt_160, delta, "generalized-eigenvector candidate probe (L=160)"))
    out = dict(
        delta=delta,
        parameters=p,
        formula_benchmark_12_pulses=float(benchmark_formula),
        margin_single_position=float(p["mu"] * p["P"] * V),
        margin_12_unwound_positions=float(p["mu"] * p["P"] * 12 * V),
        theorem_2_9_capital_lower_bound=theorem_2_9_lower_bound(delta),
        executable_cost_form_min_eigenvalue=min_eig,
        designs=designs,
    )
    Path("breakthrough_experiments/results_exp13_account_capital.json").write_text(json.dumps(out, indent=2))
    print(f"formula benchmark (12 one-leg pulses): {benchmark_formula:.2f} USDT")
    print(f"Theorem 2.9 lower bound: {out['theorem_2_9_capital_lower_bound']:.3e} USDT")
    for d in designs:
        print(f"  {d['design']:52s} C0={d['C0_required']:8.2f}  err={d['testing_error']:.4f}  "
              f"end inv={d['end_inventory']:6.2f}  peak margin={d['peak_margin']:6.2f}  max|v|={d['max_abs_trade']:.2f}")
    return out


if __name__ == "__main__":
    run_experiment()
