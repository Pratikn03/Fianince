"""Paper 1, Theorem (general completely monotone memory): numerical checks.
(1) Best uniform approximation errors E_L(|x|) on [-1,1] by Remez (via sqrt(u) on [0,1]); c_* = inf_L L E_L.
(2) The alternation construction: two n-atom probability measures on [0,rho] matching moments 0..2n-2,
    W1 >= rho E_{2n-2}; exact W1 and kernel distance.
(3) The moment-LP estimator: error vs N, and the 1/log N rate."""
import json, numpy as np, mpmath as mp
from scipy.optimize import linprog
mp.mp.dps = 60

def remez_sqrt(m, iters=100):
    """Best uniform approximation of sqrt(u) on [0,1] by degree-m polynomials (Remez, double precision,
    Chebyshev basis). Returns E (as mpf), monomial coefficients (mpf, ascending), reference points, errors there."""
    from numpy.polynomial import chebyshev as C
    from math import comb
    t = np.linspace(0, 1, 200001); ug = t ** 2                    # dense near 0, where sqrt is singular
    ref = ((1 - np.cos(np.pi * np.arange(m + 2) / (m + 1))) / 2) ** 2
    for it in range(iters):
        X = 2 * ref - 1
        A = np.column_stack([C.chebvander(X, m), (-1.0) ** np.arange(m + 2)])
        sol = np.linalg.solve(A, np.sqrt(ref)); cc, E = sol[:-1], sol[-1]
        ev = np.sqrt(ug) - C.chebval(2 * ug - 1, cc)
        sg = np.sign(ev); sg[sg == 0] = 1
        cuts = np.flatnonzero(np.diff(sg)) + 1
        runs = np.split(np.arange(len(ug)), cuts)
        idx = [r[np.argmax(np.abs(ev[r]))] for r in runs]
        while len(idx) > m + 2:
            idx = idx[1:] if abs(ev[idx[0]]) < abs(ev[idx[-1]]) else idx[:-1]
        if len(idx) < m + 2:
            raise RuntimeError("alternation lost")
        spread = np.max(np.abs(ev[idx])) / np.min(np.abs(ev[idx])) - 1
        ref = ug[idx]
        if spread < 1e-9:
            break
    mono = C.cheb2poly(cc)
    pu = np.zeros(m + 1)
    for k, a in enumerate(mono):
        for j in range(k + 1):
            pu[j] += a * comb(k, j) * 2 ** j * (-1) ** (k - j)
    c = [mp.mpf(float(v)) for v in pu]
    errs = [mp.sqrt(mp.mpf(float(u))) - mp.polyval(c[::-1], mp.mpf(float(u))) for u in ref]
    return mp.mpf(float(abs(E))), c, [mp.mpf(float(u)) for u in ref], errs

def alternation_pair(n, rho):
    """n-atom probability measures on [0, rho] with equal moments of order 0..2n-2 (alternation construction)."""
    L = 2 * n - 2; m = n - 1
    E, c, ref, ev = remez_sqrt(m) if m >= 1 else (mp.mpf(1) / 2, [mp.mpf(1) / 2], [mp.mpf(0), mp.mpf(1)], [-mp.mpf(1) / 2, mp.mpf(1) / 2])
    xs = sorted(set([mp.mpf(0)] + [mp.sqrt(u) for u in ref if u > 0] + [-mp.sqrt(u) for u in ref if u > 0]))
    signs = [mp.sign(mp.fabs(x) - mp.polyval(c[::-1], x ** 2)) for x in xs]
    assert len(xs) == L + 3, (len(xs), L)
    assert all(signs[i] * signs[i + 1] < 0 for i in range(len(xs) - 1))
    pts = xs[:L + 2]; sg = signs[:L + 2]
    # divided-difference weights: w_i = 1 / prod_{j != i} (x_i - x_j), alternating in sign
    w = [1 / mp.fprod([pts[i] - pts[j] for j in range(L + 2) if j != i]) for i in range(L + 2)]
    # orient so that positive weights sit where |x| - p* = +E
    if mp.sign(w[0]) != sg[0]:
        w = [-v for v in w]
    pos = [(p, v) for p, v in zip(pts, w) if v > 0]; neg = [(p, -v) for p, v in zip(pts, w) if v < 0]
    Sp = mp.fsum(v for _, v in pos); Sn = mp.fsum(v for _, v in neg)
    to_r = lambda x: rho * (x + 1) / 2
    A = [(to_r(p), v / Sp) for p, v in pos]; B = [(to_r(p), v / Sn) for p, v in neg]
    return A, B, E

def moments(M, J):
    return [mp.fsum(v * r ** j for r, v in M) for j in range(J)]

def w1(A, B):
    pts = sorted(set([r for r, _ in A] + [r for r, _ in B]))
    FA = FB = mp.mpf(0); tot = mp.mpf(0)
    for i in range(len(pts) - 1):
        FA += mp.fsum(v for r, v in A if r == pts[i]); FB += mp.fsum(v for r, v in B if r == pts[i])
        tot += abs(FA - FB) * (pts[i + 1] - pts[i])
    return tot

def kernel_dist(A, B):
    # ||k^A - k^B||_2^2 = sum_m (sum_i a_i r_i^m - sum_j b_j s_j^m)^2 = closed form via 1/(1 - r s)
    allm = [(r, v) for r, v in A] + [(r, -v) for r, v in B]
    return mp.sqrt(mp.fsum(v1 * v2 / (1 - r1 * r2) for r1, v1 in allm for r2, v2 in allm))

out = {}
# (1) L E_L(|x|) for even L
LE = {}
for m in range(1, 16):
    E, c, ref, ev = remez_sqrt(m)
    LE[2 * m] = float(2 * m * E)
    if m <= 3 or m % 5 == 0:
        print(f"L={2*m:3d}  E_L(|x|)={float(E):.6e}  L*E_L={2*m*float(E):.6f}  equioscillation spread={float(max(abs(e) for e in ev)/min(abs(e) for e in ev)-1):.1e}")
out["L_times_E_L_abs"] = LE
out["c_star_numeric_min_over_L_2_to_30"] = min(LE.values())
print("min over L of L*E_L:", min(LE.values()), "| Bernstein constant 0.2801694990 (limit)")

# (2) alternation pairs on [0, rho]
pairs = {}
for rho in (0.9, 0.99):
    for n in (2, 3, 4, 6, 8, 10, 12):
        A, B, E = alternation_pair(n, rho)
        mA, mB = moments(A, 2 * n), moments(B, 2 * n)
        gap_low = max(abs(mA[j] - mB[j]) for j in range(2 * n - 1)); gap_top = abs(mA[2 * n - 1] - mB[2 * n - 1])
        W = w1(A, B); kd = kernel_dist(A, B)
        bound = 2 * rho ** (2 * n - 1) / (1 - rho)
        pairs[f"rho={rho},n={n}"] = {"atoms_A": len(A), "atoms_B": len(B), "max_moment_gap_orders_0_to_2n-2": float(gap_low),
                                     "moment_gap_order_2n-1": float(gap_top), "W1": float(W), "rho*E_{2n-2}": float(rho * E),
                                     "n*W1": float(n * W), "kernel_l2": float(kd), "kernel_bound_2rho^(2n-1)/(1-rho)": float(bound)}
        print(f"rho={rho} n={n:2d} atoms {len(A)},{len(B)} lowgap={float(gap_low):.1e} W1={float(W):.4f} >= rho*E={float(rho*E):.4f} "
              f"n*W1={float(n*W):.3f} kernel={float(kd):.3e} <= {float(bound):.3e}")
        assert len(A) == n and len(B) == n and W >= rho * E * (1 - 1e-20) and kd <= bound
out["pairs"] = pairs

# (3) moment-LP estimator: error vs N (kernel values observed with N(0, sigma^2/N) noise)
rng = np.random.default_rng(7)
rho = 0.9
grid = np.linspace(0, rho, 401)
# true merged measure: continuous (Beta(2,3) on [0, rho]), mass W = 0.1
from scipy.stats import beta as betad
dens = betad(2, 3).pdf(grid / rho); wt = dens / dens.sum() * 0.1
Lmax = 60
Mtrue = np.array([np.sum(wt * grid ** j) for j in range(Lmax + 1)])
def lp_fit(khat, L, grid):
    # min t s.t. |sum_g x_g r_g^j - khat_j| <= t, x >= 0 ; variables [x (G), t]
    G = len(grid); V = np.vstack([grid ** j for j in range(L + 1)])
    c = np.r_[np.zeros(G), 1.0]
    A_ub = np.block([[V, -np.ones((L + 1, 1))], [-V, -np.ones((L + 1, 1))]])
    b_ub = np.r_[khat[:L + 1], -khat[:L + 1]]
    res = linprog(c, A_ub=A_ub, b_ub=b_ub, bounds=[(0, None)] * G + [(0, None)], method="highs")
    return res.x[:G]
def kr(xa, xb, grid):
    # KR norm with f(0)=0, 1-Lipschitz on [0, rho]: = integral of |tail difference| on a 1-D grid
    d = xa - xb; tail = np.cumsum(d[::-1])[::-1]       # mass at or above each grid point
    return float(np.sum(np.abs(tail[1:]) * np.diff(grid)))
B_ = (1 + np.sqrt(2)) * (1 + 2 / rho)
est = {}
sigma = 1e-3
for logN in (4, 6, 8, 10, 12, 14, 16, 20, 24):
    N = 10.0 ** logN
    L = max(1, int(np.floor(np.log(N / sigma ** 2) / (4 * np.log(B_)))))
    L = min(L, 12)        # floating-point Vandermonde limit on a 401-point grid
    errs = []
    for rep in range(20):
        khat = Mtrue + rng.normal(0, sigma / np.sqrt(N), Mtrue.shape)
        x = lp_fit(khat, L, grid)
        errs.append(kr(x, wt, grid))
    est[logN] = {"L": L, "mean_KR_error": float(np.mean(errs)), "error_times_log(N/sigma^2)": float(np.mean(errs) * np.log(N / sigma ** 2))}
    print(f"N=1e{logN:2d} L={L:2d} KR error={np.mean(errs):.5f}  error*log(N/s^2)={np.mean(errs)*np.log(N/sigma**2):.4f}")
out["lp_estimator"] = {"rho": rho, "true": "Beta(2,3) on [0,rho], mass 0.1", "sigma": sigma, "B(rho)": B_, "by_log10N": est}
json.dump(out, open("/home/claude/theory/R_P1_general_minimax.json", "w"), indent=2)
print("written R_P1_general_minimax.json")
