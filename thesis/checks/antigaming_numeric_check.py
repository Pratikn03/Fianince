"""Numerical check of Section "Agents who game the monitor" (Theorem thm:nogaming, Proposition prop:throttle).

1. The pooled estimator of Theorem thm:pooled under four behaviours (200 replications each, T = 5000):
   baseline; exogenous noise injection (manipulative flow independent of the past, sd 3); an added contrarian agent
   whose memory is inside the estimator's 12 lags; an added slow momentum agent whose memory (rate 0.995) lies far
   beyond them. The theorem says the first three are estimated without bias (the estimate moves only when the true
   margin moves) and the last is not.
2. A game of five agents choosing momentum intensity under a continuous throttle alpha = g(M) with a buffer M_min:
   best-response iteration to a pure equilibrium, verified on a grid, compared with the same game without a throttle.
Writes antigaming_numeric_check.json and antigaming_numbers.tex.
"""
import json
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parent
A, KAPPA, L, T, REPS, SEED = 0.9, 0.5, 12, 5000, 200, 20261025


def kernel(weight, r, n):
    """Geometric kernel with total weight `weight`, memory rate r, truncated at n taps (rescaled to keep the weight)."""
    k = (1 - r) * r ** np.arange(n)
    return weight * k / k.sum()


def simulate(rng, k_main, noise_sd=0.0, k_contra=None, slow=None):
    """x_{t+1} = a x_t + kappa f_{t+1} + eps; f_{t+1} = sum_m k_m x_{t-m} + w + nu + slow agent."""
    n = len(k_main); x = np.zeros(T + n + 1); f = np.zeros(T + n + 1); ys = 0.0
    kk = k_main.copy()
    if k_contra is not None:
        kk[:len(k_contra)] += k_contra
    for t in range(n, T + n):
        flow = kk @ x[t - np.arange(n)] + rng.normal() + noise_sd * rng.normal()
        if slow is not None:
            q, r = slow
            ys = r * ys + (1 - r) * x[t]
            flow += q * ys
        f[t + 1] = flow
        x[t + 1] = A * x[t] + KAPPA * flow + 0.5 * rng.normal()
    return x[n:], f[n:]


def pooled(x, f):
    t = np.arange(L, len(x) - 1)
    Xp = np.column_stack([f[t + 1], x[t], np.ones(len(t))]); yp = x[t + 1] - x[t]
    kap, beta, _ = np.linalg.lstsq(Xp, yp, rcond=None)[0]
    Xk = np.column_stack([x[t - m] for m in range(L)] + [np.ones(len(t))]); yk = f[t + 1]
    k = np.linalg.lstsq(Xk, yk, rcond=None)[0][:L]
    return -beta - kap * k.sum()


def part1():
    rng = np.random.default_rng(SEED)
    k_main = kernel(0.12, 0.5, L)                                     # M = 1 - 0.9 - 0.5 * 0.12 = 0.04
    cases = {"baseline": dict(), "noise_injection": dict(noise_sd=3.0),
             "contrarian_inside_memory": dict(k_contra=kernel(-0.04, 0.6, L)),
             "slow_momentum_beyond_memory": dict(slow=(0.06, 0.995))}
    truth = {"baseline": 1 - A - KAPPA * 0.12, "noise_injection": 1 - A - KAPPA * 0.12,
             "contrarian_inside_memory": 1 - A - KAPPA * (0.12 - 0.04), "slow_momentum_beyond_memory": 1 - A - KAPPA * (0.12 + 0.06)}
    out = {}
    for name, kw in cases.items():
        est = np.array([pooled(*simulate(rng, k_main, **kw)) for _ in range(REPS)])
        out[name] = {"true_M": float(truth[name]), "mean_estimate": float(est.mean()), "sd_estimate": float(est.std(ddof=1)),
                     "bias": float(est.mean() - truth[name])}
    return out


def part2():
    n, a, kap, Mmin, Mmax = 5, 0.9, 0.5, 0.02, 0.10
    b = np.array([0.30, 0.25, 0.20, 0.15, 0.10]); e = 1.0
    g = lambda M: float(np.clip((M - Mmin) / (Mmax - Mmin), 0.0, 1.0))

    def alpha_of(Q):                                                   # unique fixed point alpha = g(1 - a - kap*alpha*Q)
        lo, hi = 0.0, 1.0
        for _ in range(80):
            mid = (lo + hi) / 2
            if mid - g(1 - a - kap * mid * Q) > 0:
                hi = mid
            else:
                lo = mid
        return (lo + hi) / 2

    grid = np.linspace(0, 0.5, 2001)
    util = lambda i, qi, qo: alpha_of(qi + qo) * (b[i] * qi - e * qi ** 2 / 2)
    q = b / e * 0.5
    for _ in range(200):
        new = q.copy()
        for i in range(n):
            qo = q.sum() - q[i]
            new[i] = grid[np.argmax([util(i, v, qo) for v in grid])]
        if np.max(np.abs(new - q)) < 1e-9:
            break
        q = 0.5 * q + 0.5 * new
    gains = [max(util(i, v, q.sum() - q[i]) for v in grid) - util(i, q[i], q.sum() - q[i]) for i in range(n)]
    al = alpha_of(q.sum()); M = 1 - a - kap * al * q.sum()
    q0 = b / e; M0 = 1 - a - kap * q0.sum()
    return {"agents": n, "M_min": Mmin, "M_max": Mmax, "equilibrium_q": q.tolist(), "alpha": al, "Q": float(q.sum()),
            "M_equilibrium": float(M), "max_grid_gain_from_deviation": float(max(gains)),
            "no_throttle_Q": float(q0.sum()), "no_throttle_M": float(M0)}


def main():
    res = {"part1_pooled_under_gaming": part1(), "part2_throttle_equilibrium": part2(),
           "settings": {"a": A, "kappa": KAPPA, "lags": L, "T": T, "replications": REPS, "seed": SEED}}
    (HERE / "antigaming_numeric_check.json").write_text(json.dumps(res, indent=1) + "\n")
    (HERE / "antigaming_numbers.tex").write_text(numbers_tex(res))
    print(json.dumps(res, indent=1))


def numbers_tex(res):
    """The macros printed in the thesis, from the result file (the verifier regenerates them and compares)."""
    p1, p2 = res["part1_pooled_under_gaming"], res["part2_throttle_equilibrium"]
    tex = ["% generated by antigaming_numeric_check.py; do not edit",
           "\\newcommand{\\AGbaseTrue}{%.3f}\\newcommand{\\AGbaseEst}{%.3f}" % (p1["baseline"]["true_M"], p1["baseline"]["mean_estimate"]),
           "\\newcommand{\\AGnoiseEst}{%.3f}\\newcommand{\\AGnoiseSdRatio}{%.1f}" % (
               p1["noise_injection"]["mean_estimate"], p1["noise_injection"]["sd_estimate"] / p1["baseline"]["sd_estimate"]),
           "\\newcommand{\\AGcontraTrue}{%.3f}\\newcommand{\\AGcontraEst}{%.3f}" % (
               p1["contrarian_inside_memory"]["true_M"], p1["contrarian_inside_memory"]["mean_estimate"]),
           "\\newcommand{\\AGslowTrue}{%.3f}\\newcommand{\\AGslowEst}{%.3f}" % (
               p1["slow_momentum_beyond_memory"]["true_M"], p1["slow_momentum_beyond_memory"]["mean_estimate"]),
           "\\newcommand{\\AGthrM}{%.3f}\\newcommand{\\AGthrAlpha}{%.2f}\\newcommand{\\AGthrGain}{%.1e}" % (
               p2["M_equilibrium"], p2["alpha"], p2["max_grid_gain_from_deviation"]),
           "\\newcommand{\\AGnoThrM}{%.3f}" % p2["no_throttle_M"]]
    return "\n".join(tex) + "\n"


if __name__ == "__main__":
    main()
