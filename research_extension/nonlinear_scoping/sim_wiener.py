"""Scoping check (8 Nov 2026): feedback traders with exponential memory and a saturating policy.
Agent i: memory rate r_i, capacity c_i > 0, leverage l_i = q_i*eta_i/c_i; flow at t is c_i*psi(l_i*z_{i,t-1}),
z_{i,t} = r_i z_{i,t-1} + x_t. Price: x_t = a x_{t-1} + kappa*(sum_i flow_i,t + v_t) + w_t.
Candidate sufficient object: nu = sum_i c_i delta_(r_i, l_i). Linear (small-signal) limit sees only
M1(r) = sum c_i l_i at each r."""
import numpy as np, json
a, kappa = 0.5, 0.8
def run(pop, v, w, psi):
    T = len(v); x = np.zeros(T); z = np.zeros(len(pop))
    r = np.array([p[0] for p in pop]); c = np.array([p[1] for p in pop]); l = np.array([p[2] for p in pop])
    xp = 0.0
    for t in range(T):
        flow = np.sum(c * psi(l * z)) if t > 0 else 0.0
        x[t] = a * xp + kappa * (flow + v[t]) + w[t]
        z = r * z + x[t]; xp = x[t]
    return x
tanh = np.tanh
clip = lambda u: np.clip(u, -1, 1)
out = {}
# 1. sufficiency: same nu, different agent split
A = [(0.7, 1.0, 0.1)]   # linear feedback budget S = a + kappa*M1/(1-r) = 0.767 < 1 (stable)
A_split = [(0.7, 0.5, 0.1), (0.7, 0.5, 0.1)]
rng = np.random.default_rng(1); w = 0.3 * rng.standard_normal(400); v = 0.5 * rng.standard_normal(400)
out["same_nu_max_gap"] = float(np.max(np.abs(run(A, v, w, tanh) - run(A_split, v, w, tanh))))
# 2. same M1 (sum c*l = 0.1 at r=0.7), different leverage distribution
B = [(0.7, 0.25, 0.2), (0.7, 1.0, 0.05)]
M3 = lambda P: sum(c * l**3 for _, c, l in P)
out["M1"] = [sum(c * l for _, c, l in P) for P in (A, B)]; out["M3"] = [M3(A), M3(B)]
pred = kappa**4 * (-1/3) * (M3(A) - M3(B))       # predicted leading gap in x_1 per A^3 for a pulse
rows = []
for amp in [0.05, 0.1, 0.2, 0.4, 0.8]:
    v = np.zeros(30); v[0] = amp; w0 = np.zeros(30)
    d = run(A, v, w0, tanh) - run(B, v, w0, tanh)
    rows.append({"amp": amp, "gap_x1_over_amp3": float(d[1] / amp**3), "max_gap_over_amp3": float(np.max(np.abs(d)) / amp**3)})
out["pulse_tanh"] = rows; out["predicted_gap_x1_over_amp3"] = pred
# 3. hard limits: same M1, different capacities; identical until someone hits a limit
rows = []
for amp in [1.0, 2.0, 4.0, 6.0, 8.0, 12.0]:
    v = np.zeros(30); v[0] = amp; w0 = np.zeros(30)
    d = run(A, v, w0, clip) - run(B, v, w0, clip)
    rows.append({"amp": amp, "max_gap": float(np.max(np.abs(d)))})
out["pulse_clip"] = rows
# limits: B's first agent (l=0.2) saturates once |z| >= 5
# 4. passive: excess kurtosis of prices under Gaussian innovations (tanh)
def kurt(x): x = x - x.mean(); return float(np.mean(x**4) / np.mean(x**2)**2 - 3)
rows = []
for sig in [0.5, 1.0, 2.0, 4.0, 8.0]:
    rng = np.random.default_rng(7); T = 400000
    w = sig * rng.standard_normal(T); v0 = np.zeros(T)
    rows.append({"sigma": sig, "kurt_A": kurt(run(A, v0, w, tanh)[1000:]), "kurt_B": kurt(run(B, v0, w, tanh)[1000:])})
out["passive_kurtosis"] = rows
json.dump(out, open("sim_wiener_results.json", "w"), indent=1)
print(json.dumps(out, indent=1))
