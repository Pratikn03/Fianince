"""Checks for (a) noisy stress identification (core prop:noisystress) and (b) identification of any population
(core thm:anypop(ii)).

(a) Two tanh traders (capacity c, memory r, leverage l). Probing recursion x_t = a x_{t-1} + kappa (f_t + v_t),
f_t = sum_i c_i tanh(l_i m_{i,t}), m_{i,t} = sum_{j<t} r_i^(t-1-j) x_j. Probes of several sizes; each response
observed with N(0, sigma^2) noise, averaged over N runs. Minimum-distance estimate of (c, r, l) from many starts.
Consistency: the error of the signed capacity measure (here the parameters up to relabelling) shrinks as N grows.
(b) A nonlinear switching population (two strategies, share updated by past profits) and a different one; the
steering probe of the proof makes the first market follow any target path, and subtracting the price equations
recovers the flow map exactly; populations with different flow maps give different responses to that probe.
Run: python3 mc_stress_and_general.py -> mc_stress_and_general_results.json
"""
import json, itertools
import numpy as np
from scipy.optimize import least_squares

A, KAP, T = 0.3, 0.5, 12
rng = np.random.default_rng(11)
PROBES = [np.r_[v, np.zeros(T - 1)] for v in (0.5, 1.0, 2.0, 4.0, 8.0)] + [np.r_[np.zeros(3), v, np.zeros(T - 4)] for v in (1.0, 4.0)]


def respond(theta, v):
    c, r, l = theta[0:2], theta[2:4], theta[4:6]
    x = np.zeros(T); m = np.zeros(2)
    for t in range(T):
        f = np.sum(c * np.tanh(l * m))
        x[t] = (A * x[t - 1] if t else 0.0) + KAP * (f + v[t])
        m = r * m + x[t]
    return x


def stack(theta):
    return np.concatenate([respond(theta, v) for v in PROBES])


def estimate(obs, starts=40):
    """Global minimum-distance estimate: random starts plus one start near the truth (a search aid only: the
    reported minimizer is the lowest-cost point found, wherever it is)."""
    lo = np.array([0.05, 0.05, 0.0, 0.0, -3, -3]); hi = np.array([2, 2, 0.95, 0.95, 3, 3]); best = None
    inits = [rng.uniform(lo, hi) for _ in range(starts)] + [np.clip(theta0 + 0.05 * rng.standard_normal(6), lo, hi)]
    for z0 in inits:
        r = least_squares(lambda z: stack(z) - obs, z0, bounds=(lo, hi), xtol=1e-14, ftol=1e-14, gtol=1e-14)
        if best is None or r.cost < best.cost:
            best = r
    return best.x


def err(th, th0):
    perms = [th, np.r_[th[1], th[0], th[3], th[2], th[5], th[4]]]
    return min(np.max(np.abs(p - th0)) for p in perms)


theta0 = np.array([0.8, 0.5, 0.3, 0.7, 1.5, -1.0])     # a trend follower and a contrarian
clean = stack(theta0); SIG = 0.05
res_a = []
for N in (1, 16, 256, 4096, 65536):
    e = []
    for _ in range(6):
        obs = clean + SIG / np.sqrt(N) * rng.standard_normal(clean.size)
        e.append(err(estimate(obs), theta0))
    res_a.append({"N": N, "median_param_error": float(np.median(e))})
    print(f"noisy stress identification: N={N:5d} median parameter error {np.median(e):.4f}", flush=True)


# (b) any population
def switching_flow(x, t, beta):
    """Two strategies (trend, contrarian) with shares updated by past profits: a causal nonlinear flow map."""
    if t == 0:
        return 0.0
    tr = np.tanh(x[t - 1]); co = -0.5 * np.tanh(x[t - 1])
    prof_tr = sum(np.tanh(x[s - 1]) * (x[s] - x[s - 1]) for s in range(1, t)); prof_co = -0.5 * sum(np.tanh(x[s - 1]) * (x[s] - x[s - 1]) for s in range(1, t))
    w = 1 / (1 + np.exp(-beta * (prof_tr - prof_co)))
    return 0.3 * (w * tr + (1 - w) * co)


def steer(F, target):
    v = np.zeros(T)
    for t in range(T):
        v[t] = (target[t] - (A * target[t - 1] if t else 0.0)) / KAP - F(target, t)
    return v


def run(F, v):
    x = np.zeros(T)
    for t in range(T):
        x[t] = (A * x[t - 1] if t else 0.0) + KAP * (F(x, t) + v[t])
    return x


target = rng.normal(0, 1, T)
F1 = lambda x, t: switching_flow(x, t, 2.0)
F2 = lambda x, t: switching_flow(x, t, 5.0)
v = steer(F1, target)
x1 = run(F1, v); x2 = run(F2, v)
recovered = np.array([(x1[t] - (A * x1[t - 1] if t else 0)) / KAP - v[t] for t in range(T)])
true_flow = np.array([F1(target, t) for t in range(T)])
res_b = {"steer_hits_target_maxerr": float(np.max(np.abs(x1 - target))),
         "flow_recovered_maxerr": float(np.max(np.abs(recovered - true_flow))),
         "other_population_deviates_maxdiff": float(np.max(np.abs(x2 - target)))}
print("any population:", res_b)
json.dump({"noisy_stress": res_a, "any_population": res_b}, open("mc_stress_and_general_results.json", "w"), indent=1)
