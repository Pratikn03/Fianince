"""Checks for the third batch (core section app:openres, last five subsections).

C1 largest weights for every K: 30-digit computation of the gap for K = 2..61; exact (sympy) verification that the
   explicit bounds give Radau max > Gauss max for every K >= 62; monotonicity of the central-binomial sequences.
C2 insider against a strategic group: best-response iteration converges to a pure equilibrium.
C3 hard limits: least squares on a fixed two-ray design has error falling like N^-1/2.
C4 nonlinear learners: composition variance grows like (d eta)^-(4K-2) with equal leverage, flattens with distinct.
C5 cascade dynamics: rounds converge geometrically at rate kappa L'(delta*); slow capital deepens the fall.
Run: python3 open_checks3.py -> open_checks3_results.json"""
import json, math
import numpy as np
import mpmath as mp
import sympy as sp
from numpy.polynomial import legendre as Lg
from scipy.optimize import least_squares
from scipy.stats import norm

out = {}

# ---------- C1
mp.mp.dps = 30
def gauss_max(K):
    xs = [mp.findroot(lambda x: mp.legendre(K, x), mp.mpf(float(q))) for q in np.real(Lg.legroots([0] * K + [1]))]
    return max(2 / ((1 - x ** 2) * mp.diff(lambda y: mp.legendre(K, y), x) ** 2) for x in xs)
def radau_max(K):
    cc = [0] * (K + 1); cc[K - 1] = 1; cc[K] = 1
    rr = [q for q in np.sort(np.real(Lg.legroots(cc))) if q > -0.999999]
    f = lambda x: mp.legendre(K - 1, x) + mp.legendre(K, x)
    xs = [mp.findroot(f, mp.mpf(float(q))) for q in rr]
    return max([mp.mpf(2) / K ** 2] + [(1 - x) / (K ** 2 * mp.legendre(K - 1, x) ** 2) for x in xs])
gaps = {K: float(radau_max(K) - gauss_max(K)) for K in range(2, 62)}
out["C1_min_gap_K2_61"] = min(gaps.values()); out["C1_all_positive_K_le_61"] = all(v > 0 for v in gaps.values())
K, m = sp.symbols("K m", positive=True)
rat = ((2 * m + 1) / (2 * m + 2)) ** 2
q_inc = sp.factor(sp.together(rat * (m + sp.Rational(5, 4)) / (m + sp.Rational(1, 4)) - 1))
r_dec = sp.factor(sp.together(rat * (m + sp.Rational(5, 4) + 1 / (32 * (m + 1))) / (m + sp.Rational(1, 4) + 1 / (32 * m)) - 1))
out["C1_q_increasing"] = str(q_inc); out["C1_r_decreasing"] = str(r_dec)
maxroot = 0.0
for parity in (0, 1):
    d = 5 / (K - sp.Rational(1, 2)); Phi = (K + sp.Rational(1, 2)) ** 2 + 1 / (4 * (1 - d ** 2)); a = K ** 2 / Phi
    T = (1 - d ** 2) + a * (1 - d ** 2 - d ** 3) - d * ((1 - d ** 2) - a) - d * K / (K ** 2 + K + sp.Rational(1, 2))
    if parity == 0:
        Gup = (K + sp.Rational(1, 2) + 1 / (8 * K)) / (K ** 2 + K + sp.Rational(1, 2)); Fm = 2 / (K + sp.Rational(1, 2))
    else:
        Gup = (K - sp.Rational(1, 2) + 1 / (8 * (K - 1))) / K ** 2; Fm = 2 * K ** 2 / ((K - sp.Rational(1, 2)) * (K ** 2 + K + sp.Rational(1, 2)))
    n, dd = sp.fraction(sp.together(T / (K ** 2 * Fm) - Gup))
    sgn_num = sp.fraction(sp.together(a - (1 - d ** 2)))[0]
    roots = [float(x) for x in sp.Poly(sp.expand(n), K).real_roots()] + [float(x) for x in sp.Poly(sp.expand(dd), K).real_roots()] \
        + [float(x) for x in sp.Poly(sp.expand(sgn_num), K).real_roots()]
    maxroot = max(maxroot, max(roots))
    out[f"C1_D_positive_at_62_parity{parity}"] = bool(sp.N(n.subs(K, 62) / dd.subs(K, 62)) > 0)
out["C1_largest_real_root"] = maxroot
nearest = max(np.min(np.abs(np.real(Lg.legroots([0] * (k - 1) + [1, 1]))[np.real(Lg.legroots([0] * (k - 1) + [1, 1])) > -0.999999])) * (k - 0.5) for k in range(3, 301))
out["C1_nearest_node_times_K_minus_half_max"] = float(nearest)
bad = []
for Kk in range(8, 61):
    dk = 5 / (Kk - 0.5); Ph = (Kk + 0.5) ** 2 + 1 / (4 * (1 - dk * dk)); ak = Kk ** 2 / Ph
    Tk = (1 - dk * dk) + ak * (1 - dk * dk - dk ** 3) - dk * abs((1 - dk * dk) - ak) - dk * Kk / (Kk * Kk + Kk + .5)
    if Kk % 2 == 0: Gu = (Kk + .5 + 1 / (8 * Kk)) / (Kk * Kk + Kk + .5); Fk = 2 / (Kk + .5)
    else: Gu = (Kk - .5 + 1 / (8 * (Kk - 1))) / Kk ** 2; Fk = 2 * Kk * Kk / ((Kk - .5) * (Kk * Kk + Kk + .5))
    if not (float(gauss_max(Kk)) <= math.pi * Gu and float(radau_max(Kk)) >= math.pi * Tk / (Kk * Kk * Fk)): bad.append(Kk)
out["C1_explicit_bounds_hold_K8_60"] = not bad
out["C1_ok"] = bool(out["C1_explicit_bounds_hold_K8_60"] and out["C1_all_positive_K_le_61"] and maxroot < 62 and out["C1_D_positive_at_62_parity0"] and out["C1_D_positive_at_62_parity1"] and nearest < 5)

# ---------- C2
a2, kap2, theta, rg, T2, SD2, sig2 = 0.3, 0.5, 1.0, 0.6, 10, 1.0, 1.0
def resp(w):
    h = np.zeros(T2); g = np.zeros(T2)
    for arr, init in ((h, kap2), (g, 1.0)):
        mm = 0.0; xp = 0.0
        for t in range(T2):
            if t > 0: mm = rg * mm + xp
            arr[t] = a2 * xp + kap2 * w * mm + (init if t == 0 else 0.0); xp = arr[t]
    return h, g
cm = lambda v: np.array([[v[t - u] if u <= t else 0.0 for u in range(T2)] for t in range(T2)])
Mm = np.array([[rg ** (t - 1 - j) if j < t else 0.0 for j in range(T2)] for t in range(T2)])
def Ug(w, z):
    h, g = resp(w); H = cm(h); G = cm(g); xD = H @ z; fD = w * Mm @ xD
    return SD2 * (fD.sum() - fD @ xD) - sig2 * w * np.trace(Mm @ G @ G.T)
def Ui(w, z):
    H = cm(resp(w)[0]); return SD2 * (z.sum() - z @ H @ z + (1 - theta) * kap2 * z @ z)
def br_ins(w):
    H = cm(resp(w)[0]); M = (H + H.T) / 2 - (1 - theta) * kap2 * np.eye(T2); return 0.5 * np.linalg.solve(M, np.ones(T2))
wmax = (0.95 - a2) * (1 - rg) / kap2 * 0.99; wg = np.linspace(-wmax, wmax, 4001); w = 0.0
for it in range(100):
    z = br_ins(w); wn = wg[int(np.argmax([Ug(x, z) for x in wg]))]
    if abs(wn - w) < 1e-12: break
    w = wn
z = br_ins(w)
out["C2_iterations"] = it; out["C2_weight"] = float(w); out["C2_weight_max"] = float(wmax)
out["C2_insider_payoff"] = float(Ui(w, z)); out["C2_insider_payoff_no_group"] = float(Ui(0.0, br_ins(0.0)))
out["C2_group_payoff"] = float(Ug(w, z))
h0, g0 = resp(0.0); z0 = br_ins(0.0); x0 = cm(h0) @ z0; f0 = Mm @ x0
out["C2_entry_informed"] = float(SD2 * (f0.sum() - f0 @ x0)); out["C2_entry_noise"] = float(sig2 * np.trace(Mm @ cm(g0) @ cm(g0).T))
Ugrid = np.array([Ug(x, z) for x in wg[::20]]); out["C2_Ug_concave_on_grid"] = bool(np.diff(Ugrid, 2).max() < 0)
out["C2_ok"] = bool(out["C2_entry_informed"] > out["C2_entry_noise"] and out["C2_Ug_concave_on_grid"] and it < 99 and 0 < w < wmax and Ug(w, z) > 0)

# ---------- C3
rng = np.random.default_rng(3)
def flow(p, U):
    c1, c2, l1, l2, r1, r2 = p
    return c1 * np.clip(l1 * (r1 * U[:, 0] + U[:, 1]), -1, 1) + c2 * np.clip(l2 * (r2 * U[:, 0] + U[:, 1]), -1, 1)
p0 = np.array([1.0, 0.6, 2.0, 0.7, 0.3, 0.8])
ts = np.linspace(0.05, 3.0, 40)
U = np.vstack([np.c_[ts * 1.0, ts * 1.0], np.c_[ts * -0.6, ts * 1.0]])
y0 = flow(p0, U); errs = {}
for N in (100, 400, 1600, 6400):
    e = []
    for rep in range(150):
        y = y0 + rng.normal(0, 1, len(y0)) / math.sqrt(N)
        fit = least_squares(lambda p: flow(p, U) - y, p0 * (1 + 0.02 * rng.normal(size=6)))
        e.append(np.max(np.abs(fit.x - p0)))
    errs[N] = float(np.median(e))
out["C3_median_error"] = errs
out["C3_slope"] = float(np.polyfit(np.log(list(errs)), np.log(list(errs.values())), 1)[0])
out["C3_ok"] = bool(abs(out["C3_slope"] + 0.5) < 0.1)

# ---------- C4
a4, kap4 = 0.2, 0.5
def taps(th, A, T=40):
    w1, w2, l1, l2, r1, r2 = th
    c = np.array([w1 / l1, w2 / l2]); l = np.array([l1, l2]); r = np.array([r1, r2])
    x = np.zeros(T); mm = np.zeros(2); x[0] = kap4 * A
    for t in range(1, T):
        mm = r * mm + x[t - 1]; x[t] = a4 * x[t - 1] + kap4 * np.sum(c * np.tanh(l * mm))
    return x
def sigQ(th, As=(0.25, 0.5, 1.0, 1.5)):
    th = np.array(th, float); h = 1e-6; J = []
    for k in range(6):
        e = np.zeros(6); e[k] = h
        J.append(np.concatenate([(taps(th + e, A) - taps(th - e, A)) / (2 * h) for A in As]))
    J = np.array(J).T; I = J.T @ J; w1, w2 = th[0], th[1]
    g = np.zeros(6); g[0] = w2 / (w1 + w2) ** 2; g[1] = -w1 / (w1 + w2) ** 2
    return float(g @ np.linalg.solve(I, g))
des = [0.1, 0.05, 0.025, 0.0125]
out["C4_equal_leverage"] = [sigQ([0.15, 0.15, 1.0, 1.0, 0.5 - d_, 0.5 + d_]) for d_ in des]
out["C4_distinct_leverage"] = [sigQ([0.15, 0.15, 1.0, 2.0, 0.5 - d_, 0.5 + d_]) for d_ in des]
re_ = [out["C4_equal_leverage"][i + 1] / out["C4_equal_leverage"][i] for i in range(3)]
rd_ = [out["C4_distinct_leverage"][i + 1] / out["C4_distinct_leverage"][i] for i in range(3)]
out["C4_ratio_per_halving_equal"] = re_; out["C4_ratio_per_halving_distinct"] = rd_
out["C4_distinct_at_zero_separation"] = sigQ([0.15, 0.15, 1.0, 2.0, 0.5, 0.5])
try:
    sigQ([0.15, 0.15, 1.0, 1.0, 0.5, 0.5]); out["C4_equal_at_zero_singular"] = False
except np.linalg.LinAlgError:
    out["C4_equal_at_zero_singular"] = True
out["C4_ok"] = bool(out["C4_equal_at_zero_singular"] and np.isfinite(out["C4_distinct_at_zero_separation"]) and all(50 < x < 80 for x in re_) and rd_[0] > rd_[1] > rd_[2] and rd_[-1] < 4)

# ---------- C5
kap5, height = 0.5, 1.6
L = lambda dl: height * 0.1 * np.sqrt(2 * np.pi) * (norm.cdf((dl - 0.5) / 0.1) - norm.cdf(-5.0))
dL = lambda dl: height * np.exp(-0.5 * ((dl - 0.5) / 0.1) ** 2)
s = 0.42; dl = s; seq = [dl]
for _ in range(400):
    dl = s + kap5 * L(dl); seq.append(dl)
dstar = seq[-1]; errs5 = np.abs(np.array(seq[:60]) - dstar); idx = np.where(errs5 > 1e-11)[0]; idx = idx[idx >= 3]
rate = float(np.exp(np.polyfit(idx, np.log(errs5[idx]), 1)[0]))
out["C5_round_rate"] = rate; out["C5_kappa_Lprime"] = float(kap5 * dL(dstar))
gT = 0.4
def least_fp(k):
    d_ = s
    for _ in range(5000): d_ = s + k * L(d_)
    return d_
out["C5_fall_mechanical"] = float(dstar); out["C5_fall_slow_capital"] = float(least_fp(kap5 + gT))
out["C5_threshold_mechanical"] = float(kap5 * height); out["C5_threshold_slow_capital"] = float((kap5 + gT) * height)
out["C5_ok"] = bool(abs(rate - out["C5_kappa_Lprime"]) < 0.02 and out["C5_fall_slow_capital"] > out["C5_fall_mechanical"])

print(json.dumps(out, indent=1))
json.dump(out, open("open_checks3_results.json", "w"), indent=1)
