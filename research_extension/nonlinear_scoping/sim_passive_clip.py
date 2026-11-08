"""Check of Theorem 7.2(iii) (core version): band-linear (clipped) traders under Gaussian innovations.
Same kernel, different capacities. Records coincide until the first band exceedance on the linear path; the
exceedance probability by T must lie below the bound T*(n+n')*exp(-1/(2*theta^2))."""
import numpy as np, json
a, kappa = 0.5, 0.8
P = [(0.7, 1.0, 0.1)]                    # (r, c, l)
Q = [(0.7, 0.25, 0.2), (0.7, 1.0, 0.05)]
G = P + Q
k_abs = sum(c * abs(l) / (1 - r) for r, c, l in P)   # sum_m |k_m| (common kernel, positive weights)
S_abs = a + kappa * k_abs
def first_exceed(sig, T, rng):
    x_prev = 0.0; m = np.zeros(len(G)); r = np.array([g[0] for g in G]); l = np.array([g[2] for g in G])
    for t in range(T):
        if np.any(np.abs(l * m) > 1): return t
        flow = sum(c * li * mi for (ri, c, li), mi in zip(P, m[:1]))   # linear flow (= P's flow inside bands)
        x = a * x_prev + kappa * flow + sig * rng.standard_normal()
        m = r * m + x; x_prev = x
    return None
def s_exact(sig, r, L=4000):
    # sd of m_t(r) in the linear market from rest, sup over t: sigma * ||phi_r * g||_2, g = response of x to w
    g = np.zeros(L); x_prev = 0.0; mm = 0.0; mem = []
    for t in range(L):
        x = a * x_prev + kappa * P[0][1] * P[0][2] * mm + (1.0 if t == 0 else 0.0)
        mm = r * mm + x; x_prev = x; g[t] = x
    m = np.zeros(L); acc = 0.0
    for t in range(L):
        m[t] = acc; acc = r * acc + g[t]
    return sig * np.sqrt(np.sum(m**2))
out = []
T = 1000
for sig in [0.12, 0.15, 0.18, 0.21, 0.25, 0.3, 0.35, 0.4, 0.5]:
    rng = np.random.default_rng(11); reps = 400
    hits = sum(first_exceed(sig, T, rng) is not None for _ in range(reps))
    s_r = s_exact(sig, 0.7)
    theta = max(abs(l) for _, _, l in G) * s_r
    bound = T * len(G) * np.exp(-1 / (2 * theta**2))
    s_crude = sig / ((1 - 0.7) * (1 - S_abs))
    out.append({"sigma_w": sig, "P_exceed_by_T_sim": hits / reps, "bound_exact_sd": float(min(bound, 1.0)),
                "theta_exact": float(theta), "sd_exact": float(s_r), "sd_crude_bound": float(s_crude)})
json.dump({"S_abs": S_abs, "T": T, "rows": out}, open("sim_passive_clip_results.json", "w"), indent=1)
print(json.dumps(out, indent=1))
