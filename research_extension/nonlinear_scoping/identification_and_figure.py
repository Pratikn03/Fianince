"""Core version, Section 7: (1) populations with the same signed measure mu~ = sum c_i sgn(l_i) delta_(r_i,|l_i|)
give identical responses to every probe (tanh and clip); (2) the date-2 flow map Phi_theta(u) of a clipped population
has kinks at u = 1/|s_i|, s_i = l_i (r_i theta + 1), whose slope jumps return c_i sgn(l_i): recovery from noiseless
probes; (3) the two-layer figure."""
import numpy as np, json
import matplotlib; matplotlib.use("Agg"); import matplotlib.pyplot as plt
a, kappa = 0.5, 0.8
tanh = np.tanh; clip = lambda u: np.clip(u, -1, 1)
def run(pop, v, psi):
    T = len(v); x = np.zeros(T); r = np.array([p[0] for p in pop]); c = np.array([p[1] for p in pop]); l = np.array([p[2] for p in pop])
    m = np.zeros(len(pop)); xp = 0.0
    for t in range(T):
        flow = np.sum(c * psi(l * m))
        x[t] = a * xp + kappa * (flow + v[t]); m = r * m + x[t]; xp = x[t]
    return x
out = {}
# (1) same mu~: trend follower + contrarian at the same (r,|l|) vs one trader
P1 = [(0.7, 2.0, 0.1), (0.7, 1.0, -0.1)]; P2 = [(0.7, 1.0, 0.1)]
rng = np.random.default_rng(3); gaps = {}
for name, psi in (("tanh", tanh), ("clip", clip)):
    g = 0.0
    for _ in range(50):
        v = rng.normal(0, 10, 40); g = max(g, float(np.max(np.abs(run(P1, v, psi) - run(P2, v, psi)))))
    gaps[name] = g
out["same_mu_tilde_max_gap_large_random_probes"] = gaps
# (2) recovery of mu~ from the date-2 flow map (clip), theta = 0.5
P = [(0.7, 1.0, 0.1)]; Pp = [(0.7, 0.25, 0.2), (0.7, 1.0, 0.05)]
theta = 0.5
def phi(pop, u):
    # realise x0 = theta*u, x1 = u with probes, read F_2 = (x_2 - a x_1)/kappa - v_2 with v_2 = 0
    v0 = theta * u / kappa
    m = np.array([0.0] * len(pop)); r = np.array([p[0] for p in pop]); c = np.array([p[1] for p in pop]); l = np.array([p[2] for p in pop])
    x0 = kappa * v0; m = r * m + x0
    F1 = np.sum(c * clip(l * m)); v1 = (u - a * x0) / kappa - F1; x1 = a * x0 + kappa * (F1 + v1)
    m = r * m + x1
    return float(np.sum(c * clip(l * m)))
us = np.linspace(0, 20, 20001); vals = np.array([phi(Pp, u) for u in us])
slope = np.gradient(vals, us); jumps = np.where(np.abs(np.diff(slope)) > 1e-3)[0]
kinks = []
for j in jumps:
    if not kinks or us[j] - kinks[-1][0] > 0.05:
        uk = float(us[j]); d = 0.05
        sl = (phi(Pp, uk - d) - phi(Pp, uk - 2 * d)) / d; sr = (phi(Pp, uk + 2 * d) - phi(Pp, uk + d)) / d
        kinks.append((uk, sr - sl))
rec = [{"kink_u": k, "s": 1 / k, "c_sgn_l_recovered": -d / (1 / k)} for k, d in kinks]
out["recovery_clip_theta_0.5"] = {"true": [{"r": 0.7, "|l|": 0.2, "c_sgn_l": 0.25}, {"r": 0.7, "|l|": 0.05, "c_sgn_l": 1.0}],
                                   "kinks": rec, "note": "s = |l|(r*theta+1) = 0.27 and 0.0675; kinks at 3.704 and 14.815"}
# (3) figure: calm vs stress (clip), and information vs probe size (tanh vs clip)
fig, ax = plt.subplots(1, 3, figsize=(12, 3.4))
T = 25; t = np.arange(T)
for A, k in ((1.0, 0), (12.0, 1)):
    v = np.zeros(T); v[0] = A
    ax[k].plot(t, run(P, v, clip), "-", color="#1f4e79", lw=2, label="population P")
    ax[k].plot(t, run(Pp, v, clip), "--", color="#c0504d", lw=2, label="population P'")
    ax[k].set_xlabel("periods after the probe"); ax[k].set_ylabel("price deviation")
ax[0].set_title("(a) Calm: probe of size 1\nidentical responses"); ax[1].set_title("(b) Stress: probe of size 12\nlimits bind, responses separate")
ax[0].legend(frameon=False, fontsize=8)
As = np.logspace(-1.5, 1.3, 60); info = {"tanh": [], "clip": []}
for A in As:
    v = np.zeros(30); v[0] = A
    info["tanh"].append(np.sum((run(P, v, tanh) - run(Pp, v, tanh))**2) / 2)
    info["clip"].append(np.sum((run(P, v, clip) - run(Pp, v, clip))**2) / 2)
ax[2].loglog(As, np.maximum(info["tanh"], 1e-30), color="#1f4e79", lw=2, label="smooth limits (tanh)")
cl = np.array(info["clip"]); ax[2].loglog(As[cl > 0], cl[cl > 0], color="#c0504d", lw=2, label="hard limits")
ax[2].axvline(As[cl > 0][0], color="#c0504d", ls=":", lw=1)
ax[2].set_ylim(1e-14, 1e1); ax[2].set_xlabel("probe size"); ax[2].set_ylabel("information per probe (KL, unit noise)")
ax[2].set_title("(c) What a probe reveals\nabout leverage"); ax[2].legend(frameon=False, fontsize=8)
for x_ in ax: x_.spines[["top", "right"]].set_visible(False)
fig.tight_layout(); fig.savefig("/home/claude/fianince/ceiling_suite/papers/paper1_core/figs_core/fig_twolayer.pdf"); fig.savefig("fig_twolayer.png", dpi=110)
lt = np.log(np.array(info["tanh"])[:20]); la = np.log(As[:20]); out["tanh_info_slope_small_A"] = float(np.polyfit(la, lt, 1)[0])
out["clip_first_informative_probe"] = float(As[cl > 0][0])
json.dump(out, open("identification_results.json", "w"), indent=1)
print(json.dumps(out, indent=1))
