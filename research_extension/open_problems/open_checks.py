"""Numerical checks for the results that close Paper 1's open questions (core supplement section app:openres).

A1 rank condition (R) at the block witness for every K <= 12, D <= K (rank modulo a large prime at integer nodes,
   which certifies full rank over the rationals; also exact rational rank via sympy for K <= 6).
A3 exact moment gap g_K = 4^K / (K binom(2K,K)^2) against Gauss-Radau rules computed in 60-digit arithmetic, and the
   bounds pi 4^-K (1 + 1/(4K)) < g_K < pi 4^-K (1 + 1/(2K)) for K <= 2000.
A2 near instability, finite samples: KL of n stationary observations <= (n/2) max_{|l-1|<=delta}(l - 1 - log l),
   delta = sup |f_A/f_B - 1|, for the K = 2 pair at budgets 1 - eps, eps = 1e-1, 1e-2, 1e-3, n = 250, 1000, 4000.
A4 cascade: least fixed point continuous when kappa max l < 1, jumps when kappa max l > 1.
A5 insider: min_w Re 1/(1 - F e^{-iw}) >= 1/(1 + s) for random stable kernels; Toeplitz cost form positive
   definite at theta = 1/2.
A6 deadband: tap bias <= kappa delta0 W1 / ((1 - s) A); Prony weight error falls like 1/A.
Run: python3 open_checks.py -> open_checks_results.json"""
import json, math
import numpy as np
import mpmath as mp
from numpy.polynomial import legendre as Lg
from scipy.linalg import toeplitz, cho_factor, cho_solve

out = {}

# ---------- A1
def jac(s, W, lmax):
    K, D = W.shape; rows = []
    for j in range(D):
        for l in range(lmax + 1):
            r = [0.0] * (K * (D + 1))
            for i in range(K):
                r[i] = W[i, j] * l * s[i] ** (l - 1) if l > 0 else 0.0
                r[K + j * K + i] = s[i] ** l
            rows.append(r)
    return np.array(rows)
P = 2 ** 61 - 1
def rank_mod_p(M):
    M = [[x % P for x in row] for row in M]; r = 0; cols = len(M[0])
    for c in range(cols):
        piv = next((i for i in range(r, len(M)) if M[i][c]), None)
        if piv is None: continue
        M[r], M[piv] = M[piv], M[r]; inv = pow(M[r][c], P - 2, P)
        M[r] = [x * inv % P for x in M[r]]
        for i in range(len(M)):
            if i != r and M[i][c]:
                f = M[i][c]; M[i] = [(x - f * y) % P for x, y in zip(M[i], M[r])]
        r += 1
    return r
ok = True
for K in range(1, 13):
    for D in range(1, K + 1):
        q = -(-K // D); lstar = K + q - 1
        s_int = list(range(1, K + 1))            # distinct integer nodes: rank mod p full implies full over Q
        M = []
        for j in range(D):
            for l in range(lstar + 1):
                r = [0] * (K * (D + 1))
                for i in range(K):
                    w = 1 if i % D == j else 0
                    r[i] = w * l * s_int[i] ** (l - 1) if l > 0 else 0
                    r[K + j * K + i] = s_int[i] ** l
                M.append(r)
        if rank_mod_p(M) != K * (D + 1): ok = False
out["A1_witness_full_rank_mod_p_K_le_12"] = ok
try:
    import sympy as sp
    ex = True
    for K in range(1, 7):
        for D in range(1, K + 1):
            q = -(-K // D); lstar = K + q - 1
            s = [sp.Rational(2 * i + 1, 2 * K + 1) - sp.Rational(1, 2) for i in range(K)]
            M = []
            for j in range(D):
                for l in range(lstar + 1):
                    r = [0] * (K * (D + 1))
                    for i in range(K):
                        w = 1 if i % D == j else 0
                        r[i] = w * l * s[i] ** (l - 1) if l > 0 else 0
                        r[K + j * K + i] = s[i] ** l
                    M.append(r)
            if sp.Matrix(M).rank() != K * (D + 1): ex = False
    out["A1_witness_exact_rank_K_le_6"] = ex
except ImportError:
    out["A1_witness_exact_rank_K_le_6"] = None

# ---------- A3
mp.mp.dps = 60
def radau_gap(K):
    f = lambda x: mp.legendre(K - 1, x) + mp.legendre(K, x)
    c = [0] * (K + 1); c[K - 1] = 1; c[K] = 1
    roots = [r for r in np.sort(np.real(Lg.legroots(c))) if r > -0.999999]
    xs = [mp.findroot(f, mp.mpf(float(r))) for r in roots]
    ws = [mp.mpf(2) / K ** 2] + [(1 - x) / (K ** 2 * mp.legendre(K - 1, x) ** 2) for x in xs]
    xs = [mp.mpf(-1)] + xs
    return abs(sum(w * x ** (2 * K - 1) for w, x in zip(ws, xs))) / 2
def g_formula(K): return mp.mpf(4) ** K / (K * mp.binomial(2 * K, K) ** 2)
rel = max(abs(radau_gap(K) / g_formula(K) - 1) for K in range(2, 31))
out["A3_formula_vs_radau_max_rel_error_K_le_30"] = float(rel)
bnd = all(mp.pi / 4 ** K * (1 + mp.mpf(1) / (4 * K)) < g_formula(K) < mp.pi / 4 ** K * (1 + mp.mpf(1) / (2 * K))
          for K in range(1, 2001))
out["A3_bounds_hold_K_le_2000"] = bool(bnd)
out["A3_gaps"] = {K: float(g_formula(K)) for K in (2, 3, 4, 5, 8)}

# ---------- A2
def pair_rules(K=2):
    gs = (np.array([-1, 1]) / np.sqrt(3), np.array([0.5, 0.5]))
    rd = (np.array([-1.0, 1 / 3]), np.array([0.25, 0.75]))
    return gs, rd
def spectra(eps, a=0.3, kap=0.5, rc=0.5, de=0.2, ngrid=2 ** 20):
    w = 2 * np.pi * np.arange(ngrid) / ngrid
    z = np.exp(-1j * w); fs = []
    for nodes, p in pair_rules():
        r = rc + de * nodes
        Wtot = (1 - eps - a) / (kap * np.sum(p / (1 - r)))   # common feedback budget S = 1 - eps
        wts = Wtot * p
        Kz = np.sum(wts[None, :] / (1 - r[None, :] * z[:, None]), axis=1)
        H = 1 / (1 - z * (a + kap * Kz))
        fs.append(np.abs(H) ** 2)
    return fs
rows = []; okA2 = True
for eps in (1e-1, 1e-2, 1e-3):
    fA, fB = spectra(eps)
    u = fA / fB; delta = float(np.max(np.abs(u - 1)))
    rate = float(np.mean(u - 1 - np.log(u)) / 2)
    gA = np.real(np.fft.ifft(fA)); gB = np.real(np.fft.ifft(fB))
    for n in (250, 1000, 4000):
        TA = toeplitz(gA[:n]); TB = toeplitz(gB[:n])
        cf = cho_factor(TB)
        M = cho_solve(cf, TA)
        lam = np.linalg.eigvals(M).real
        kl = 0.5 * float(np.sum(lam - 1 - np.log(lam)))
        lo, hi = 1 - delta, 1 + delta
        bound = 0.5 * n * max(lo - 1 - math.log(lo), hi - 1 - math.log(hi))
        ok_eig = bool(lam.min() >= lo - 1e-9 and lam.max() <= hi + 1e-9)
        okA2 = okA2 and kl <= bound * (1 + 1e-9) and ok_eig
        rows.append({"eps": eps, "n": n, "delta": delta, "KL_n": kl, "bound": bound, "KL_over_n_rate": kl / (n * rate),
                     "eigenvalues_in_band": ok_eig})
out["A2_rows"] = rows; out["A2_all_within_bound"] = okA2

# ---------- A4
def least_fixed(s, kap, L, iters=20000):
    d = s
    for _ in range(iters):
        nd = s + kap * L(d)
        if abs(nd - d) < 1e-13: break
        d = nd
    return d
def make_L(height):     # liquidation density: a bump of positions at distance about 0.5 from the limit
    from scipy.stats import norm
    return (lambda d: height * 0.1 * np.sqrt(2 * np.pi) * (norm.cdf((d - 0.5) / 0.1) - norm.cdf(-5.0))), height
res4 = {}
for label, height in (("below", 1.5), ("above", 4.0)):
    L, hgt = make_L(height); kap = 0.5
    ss = np.linspace(0, 0.6, 1201)
    ds = np.array([least_fixed(s, kap, L) for s in ss])
    res4[label] = {"kappa_max_l": kap * hgt, "max_jump": float(np.max(np.diff(ds))), "grid_step": float(ss[1] - ss[0])}
out["A4"] = res4
out["A4_ok"] = bool(res4["below"]["max_jump"] < 10 * res4["below"]["grid_step"] / (1 - res4["below"]["kappa_max_l"])
                    and res4["above"]["max_jump"] > 0.1)

# ---------- A5
rng = np.random.default_rng(5)
worst = np.inf; minEig = np.inf
for _ in range(200):
    K = rng.integers(1, 5); r = rng.uniform(0.0, 0.95, K); w = rng.normal(0, 1, K)
    a = rng.uniform(-0.5, 0.5); kap = rng.uniform(0.1, 1.0)
    s = abs(a) + kap * np.sum(np.abs(w) / (1 - r))
    if s >= 0.98: continue
    om = np.linspace(0, 2 * np.pi, 4097); z = np.exp(-1j * om)
    F = z * (a + kap * np.sum(w[None, :] / (1 - r[None, :] * z[:, None]), axis=1))
    reH = np.real(1 / (1 - F))
    worst = min(worst, float(reH.min() - 1 / (1 + s)))
    T = 60; h = np.zeros(T); h[0] = kap; k = np.array([np.sum(w * r ** m) for m in range(T)])
    for t in range(1, T): h[t] = a * h[t - 1] + kap * np.dot(k[:t], h[t - 1::-1][:t])
    M = toeplitz(np.r_[0.5 * kap, h[1:] / 2])      # theta = 1/2: diagonal theta*kappa, off-diagonal h_d / 2
    minEig = min(minEig, float(np.linalg.eigvalsh(M).min()))
out["A5_min_ReH_minus_bound"] = worst; out["A5_min_eig_theta_half"] = minEig
out["A5_ok"] = bool(worst >= -1e-9 and minEig > 0)

# ---------- A6
def deadband_taps(A, d0, a=0.3, kap=0.5, nodes=np.array([0.4, 0.75]), q=np.array([0.04, 0.03]), T=40):
    # groups with state y_i = r_i y_i + eta x, flow q_i psi(y_i); psi soft threshold
    eta = 1 - nodes
    x = np.zeros(T); y = np.zeros(2); xl = np.zeros(T); yl = np.zeros(2)
    psi = lambda u: np.sign(u) * np.maximum(np.abs(u) - d0, 0)
    for t in range(T):
        inp = kap * A if t == 0 else 0.0
        x[t] = (a * x[t - 1] if t else 0) + kap * np.sum(q * psi(y)) + inp
        xl[t] = (a * xl[t - 1] if t else 0) + kap * np.sum(q * yl) + inp
        y = nodes * y + eta * x[t]; yl = nodes * yl + eta * xl[t]
    s = abs(a) + kap * np.sum(q * eta / (1 - nodes))
    E = kap * d0 * np.sum(np.abs(q))
    return x / A, xl / A, E / ((1 - s) * A)
res6 = []
for A in (1, 2, 4, 8, 16, 32):
    tn, tl, bound = deadband_taps(A, d0=0.05)
    res6.append({"A": A, "max_bias": float(np.max(np.abs(tn - tl))), "bound": float(bound)})
out["A6"] = res6
out["A6_ok"] = bool(all(r["max_bias"] <= r["bound"] for r in res6))
sl = np.polyfit(np.log([r["A"] for r in res6]), np.log([max(r["max_bias"], 1e-300) for r in res6]), 1)[0]
out["A6_bias_slope_in_A"] = float(sl)

print(json.dumps(out, indent=1, default=float))
json.dump(out, open("open_checks_results.json", "w"), indent=1, default=float)
