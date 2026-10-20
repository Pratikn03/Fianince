import numpy as np, json
out = {}
def M3(a, phi, eps, r, eta, q, k):
    # state (x, d, f); flow f_t=(1-eta)f_{t-1}+eta q x_{t-1} enters x and d alongside u
    # x_t = a x + phi d + k(u + f_t);  d_t = (1-r) d + eps (u + f_t); f_t = (1-eta) f + eta q x
    A = np.array([[a, phi, 0], [0, 1 - r, 0], [0, 0, 0.0]])
    # write with f_t substituted: f_t = (1-eta) f_{t-1} + eta q x_{t-1}
    Fx = np.array([eta * q, 0, 1 - eta])
    M = np.zeros((3, 3)); M[0] = A[0] + k * Fx; M[1] = A[1] + eps * Fx; M[2] = Fx
    return M
def resp(M, k, eps, n=400):
    b = np.array([k, eps, 0.0]); v = b.copy(); h = []
    for _ in range(n): h.append(v[0]); v = M @ v
    return np.array(h)
# counterexample 1 of rem:counter
p = dict(a=0.98526, phi=0.7409, eps=0.01183, r=0.03436, eta=0.5092, q=0.01127, k=1.0)
M = M3(**p); h = resp(M, p["k"], p["eps"])
lam, V = np.linalg.eig(M); b = np.array([1.0, p["eps"], 0]); coef = np.linalg.solve(V, b); res = (V[0, :] * coef)
order = np.argsort(-np.abs(lam))
out["counter1"] = {"C3": p["phi"]*p["eps"]+p["k"]**2*p["eta"]*p["q"]-(1-p["a"])*p["k"], "peak_lag": int(h.argmax()), "peak": float(h.max()),
                   "h1_minus_h0": float(h[1]-h[0]), "eigs": [float(np.real(lam[i])) for i in order], "residues": [float(np.real(res[i])) for i in order],
                   "imag_max": float(np.abs(lam.imag).max())}
# momentum only (phi*eps=0): residues nonnegative?
rng = np.random.default_rng(3); neg = 0; tot = 0
for _ in range(20000):
    a = rng.uniform(0, .99); k = rng.uniform(.1, 2); eta = rng.uniform(.01, .99); q = rng.uniform(0, 1)
    M = np.array([[a + k * eta * q, k * (1 - eta)], [eta * q, 1 - eta]])
    if np.abs(np.linalg.eigvals(M)).max() >= 1: continue
    lam, V = np.linalg.eig(M); c = V[0, :] * np.linalg.solve(V, np.array([1.0, 0])); tot += 1
    neg += (np.real(c) < -1e-12).any()
out["momentum_only_negative_residue_cases"] = [int(neg), tot]
# confluent peak lag
cf = []
for _ in range(20000):
    a = rng.uniform(.3, .995); k = 1.0; pe = rng.uniform((1 - a) * k * 1.0001, 3)
    h = np.array([k * a ** j + pe * j * a ** (j - 1) if j > 0 else k for j in range(4000)])
    ks = 1 / np.log(1 / a) - a * k / pe
    pk = int(h.argmax()); cf.append(pk in (max(np.floor(ks), 1), max(np.ceil(ks), 1)))
out["confluent_peak_in_bracket"] = [int(sum(cf)), len(cf)]
# continuity: general k* -> confluent as b -> a
a, k, pe = 0.9, 1.0, 0.2
for bb in (0.9 + 1e-3, 0.9 + 1e-5):
    B = pe / (bb - a); A = k - B
    out[f"kstar_b={bb}"] = float(np.log(-A * np.log(a) / (B * np.log(bb))) / np.log(bb / a))
out["kstar_confluent"] = 1 / np.log(1 / a) - a * k / pe
print(json.dumps(out, indent=1)); json.dump(out, open("R_P2_sec4_checks.json", "w"), indent=1)
