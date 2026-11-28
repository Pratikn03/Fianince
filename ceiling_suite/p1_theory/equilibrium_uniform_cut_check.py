"""Numerical check of the equilibrium uniform-cut results (Theorem eq-cut, revision of 28 November 2026).

Model (main text, Section 4): dealer primitives (abar, A, sF2, sX2); primitive merged measure M = sum_i w_i delta_{r_i}.
  S_M(D)     = sum_i w_i / (D - r_i)                     (Stieltjes transform)
  kappa_-(D) = D [ (D - abar) - sqrt((D - abar)^2 - 4 A^2 sF2 sX2) ] / (2 A sX2)   (low-impact dealer root)
  F(D; th)   = D - 1 + th kappa_-(D) S_M(D)              (equilibrium condition after scaling all feedback by th)
Reduced form at a root D: a* = abar/D, kappa* = kappa/D, w~_i = th w_i (D - abar)/(D - r_i).
Claims checked:
  (a) S*(D) := a* + kappa* sum_i w~_i/(1 - r_i) equals Phi(D) = 1 - (1 - abar/D) S_M(1)/S_M(D)  (th cancels);
  (b) the first autoregressive coefficient phi_0 = a* + kappa* sum_i w~_i equals 1 + abar - D;
  (c) on a root with dF/dD > 0 (principal branch) a cut lowers S*; on a root with dF/dD < 0 it raises S*;
  (d) for moment-matched pairs (K-point Gauss vs Gauss-Radau) the post-cut S* gap on the principal branch is
      O(deta^(2K-1));
  (e) estimator from one passive pricing-error record: long autoregression -> phi_hat, D_hat = 1 + abar - phi_hat_0,
      reconstruct S_M on [D_hat, 1], solve the post-cut principal root, report |S*_hat - S*|; error falls with T and
      does not grow as the spacing shrinks.
Writes equilibrium_uniform_cut_check_results.json next to this file.
"""
import json
from pathlib import Path

import numpy as np
from numpy.polynomial.legendre import leggauss

OUT = Path(__file__).with_name('equilibrium_uniform_cut_check_results.json')


def kappa_minus(D, abar, A, sF2, sX2):
    disc = (D - abar) ** 2 - 4 * A ** 2 * sF2 * sX2
    if disc < 0:
        return np.nan
    return D * ((D - abar) - np.sqrt(disc)) / (2 * A * sX2)


def SM(D, w, r):
    return float(np.sum(w / (D - r)))


def F(D, th, w, r, prim):
    return D - 1 + th * kappa_minus(D, *prim) * SM(D, w, r)


def roots(th, w, r, prim, n=20001):
    abar, A, sF2, sX2 = prim
    lo = max(abar + 2 * A * np.sqrt(sF2 * sX2), r.max()) + 1e-9
    grid = np.linspace(lo, 1.0, n)
    vals = np.array([F(d, th, w, r, prim) for d in grid])
    out = []
    for i in range(n - 1):
        if np.isfinite(vals[i]) and np.isfinite(vals[i + 1]) and vals[i] * vals[i + 1] < 0:
            a, b = grid[i], grid[i + 1]
            for _ in range(200):
                m = 0.5 * (a + b)
                if F(a, th, w, r, prim) * F(m, th, w, r, prim) <= 0:
                    b = m
                else:
                    a = m
            d = 0.5 * (a + b)
            h = 1e-7
            slope = (F(d + h, th, w, r, prim) - F(d - h, th, w, r, prim)) / (2 * h)
            out.append((d, slope))
    if abs(F(1.0, th, w, r, prim)) < 1e-14:
        out.append((1.0, np.nan))
    return out


def reduced(D, th, w, r, prim):
    abar = prim[0]
    kap = kappa_minus(D, *prim)
    a_s, k_s = abar / D, kap / D
    wt = th * w * (D - abar) / (D - r)
    S_direct = a_s + k_s * np.sum(wt / (1 - r))
    Phi = 1 - (1 - abar / D) * SM(1.0, w, r) / SM(D, w, r)
    phi0 = a_s + k_s * np.sum(wt)
    return dict(D=D, kappa=kap, a_star=a_s, kappa_star=k_s, wt=wt, S_direct=S_direct, Phi=Phi, phi0=phi0,
                phi0_identity=1 + abar - D)


def gauss_pair(K, rc, deta, W_eff, D, abar):
    """Primitive weights of the K-point Gauss and left Gauss-Radau economies whose EFFECTIVE measures at root D are
    the scaled quadrature rules with total effective weight W_eff (the construction of Supplement Theorem S3.2(iv))."""
    sg, wg = leggauss(K)
    wg = wg / 2
    # left Gauss-Radau: node -1 plus the zeros of (P_{K-1}+P_K)/(1+s)
    from numpy.polynomial import legendre as L
    c = np.zeros(K + 1); c[K - 1] = 1; c[K] = 1
    allz = np.sort(np.real(L.legroots(c)))
    sr = allz
    V = np.vander(sr, K, increasing=True).T
    mom = np.array([(1 - (-1) ** (j + 1)) / (2 * (j + 1)) for j in range(K)])
    wr = np.linalg.solve(V, mom)
    out = []
    for s, ww in ((sg, wg), (sr, wr)):
        rr = rc + deta * s
        wt = W_eff * ww
        w = wt * (D - rr) / (D - abar)
        out.append((w, rr))
    return out


def ar_coeffs(D, th, w, r, prim, L):
    red = reduced(D, th, w, r, prim)
    j = np.arange(L)
    k = (red['wt'][None, :] * r[None, :] ** j[:, None]).sum(1)
    phi = red['kappa_star'] * k
    phi[0] += red['a_star']
    return phi, red


def SM_from_phi(z, phi, D, prim):
    """S_M(z) reconstructed from AR coefficients phi_0..phi_{L-1}, the root D and the dealer primitives."""
    abar = prim[0]
    kap = kappa_minus(D, *prim)
    a_s, k_s = abar / D, kap / D
    j = np.arange(len(phi))
    Psi = np.sum(phi * z ** (-(j + 1.0)))
    k0 = (phi[0] - a_s) / k_s
    SMt = (Psi - a_s / z) / k_s
    return (k0 + (D - z) * SMt) / (D - abar)


def post_cut_from_phi(phi, prim, th):
    abar = prim[0]
    D = 1 + abar - phi[0]
    f = lambda d: d - 1 + th * kappa_minus(d, *prim) * SM_from_phi(d, phi, D, prim)
    grid = np.linspace(D, 1.0, 4001)
    vals = np.array([f(d) for d in grid])
    idx = [i for i in range(len(grid) - 1) if np.isfinite(vals[i]) and vals[i] * vals[i + 1] < 0]
    if not idx:
        return np.nan, np.nan, D
    i = idx[-1]                                   # principal branch: the largest root below one
    a, b = grid[i], grid[i + 1]
    for _ in range(100):
        m = 0.5 * (a + b)
        if f(a) * f(m) <= 0:
            b = m
        else:
            a = m
    Dt = 0.5 * (a + b)
    S = 1 - (1 - abar / Dt) * SM_from_phi(1.0, phi, D, prim) / SM_from_phi(Dt, phi, D, prim)
    return S, Dt, D


def simulate_ar(phi, T, rng, burn=2000, sigma=1.0):
    from scipy.signal import lfilter
    e = sigma * rng.standard_normal(T + burn)
    x = lfilter([1.0], np.concatenate([[1.0], -np.asarray(phi)]), e)
    return x[burn:]


def long_ar(x, L):
    T = len(x) - L
    X = np.column_stack([x[L - 1 - j:L - 1 - j + T] for j in range(L)])
    y = x[L:L + T]
    return np.linalg.lstsq(X, y, rcond=None)[0]


def main():
    res = {}
    prim = (0.4, 0.16 / 0.85, 1.0, 0.25)          # abar, A, sF2, sX2: Supplement Theorem S3.2(iv) realization
    # (a)-(c) on the S3.2(iv) realization
    (wG, rG), (wR, rR) = gauss_pair(2, 0.6, 0.1, 0.2, 0.8, 0.4)
    rows = []
    for name, w, r in (('Gauss', wG, rG), ('Gauss-Radau', wR, rR)):
        for D, slope in roots(1.0, w, r, prim):
            red = reduced(D, 1.0, w, r, prim)
            post = [(d, s) for d, s in roots(0.5, w, r, prim)]
            # follow the branch: nearest post-cut root with the same slope sign
            same = [p for p in post if np.sign(p[1]) == np.sign(slope)]
            Dp = min(same, key=lambda p: abs(p[0] - D))[0] if same else np.nan
            redp = reduced(Dp, 0.5, w, r, prim) if np.isfinite(Dp) else None
            rows.append(dict(economy=name, D=D, dF_dD=slope, S_star=red['S_direct'],
                             Phi_minus_direct=red['Phi'] - red['S_direct'], phi0_minus_identity=red['phi0'] - red['phi0_identity'],
                             D_after_half_cut=Dp, S_star_after_half_cut=(redp['S_direct'] if redp else None),
                             fixed_a_kappa_prediction=red['a_star'] + 0.5 * (red['S_direct'] - red['a_star'])))
    res['S3_2_iv_realization'] = rows
    # (d) moment-matched post-cut gaps on the principal branch, K = 2 and 3
    gaps = {}
    for K in (2, 3):
        g = []
        for deta in (0.1, 0.05, 0.025, 0.0125):
            (wG, rG), (wR, rR) = gauss_pair(K, 0.6, deta, 0.2, 0.8, 0.4)
            Sp = []
            for w, r in ((wG, rG), (wR, rR)):
                rts = roots(0.5, w, r, prim)
                D = max(d for d, s in rts if s > 0)
                Sp.append(reduced(D, 0.5, w, r, prim)['S_direct'])
            g.append((deta, abs(Sp[0] - Sp[1])))
        sl = np.polyfit(np.log([a for a, _ in g]), np.log([b for _, b in g]), 1)[0]
        gaps[f'K{K}'] = dict(gaps=g, slope=sl)
    res['moment_matched_post_cut_gaps'] = gaps
    # (e) estimator from one passive record (principal branch), simulation
    rng = np.random.default_rng(20261128)
    sim = []
    for deta in (0.1, 0.05, 0.025):
        (wG, rG), _ = gauss_pair(2, 0.6, deta, 0.2, 0.8, 0.4)
        rts = roots(1.0, wG, rG, prim)
        D = max(d for d, s in rts if s > 0)
        Lsim = 80
        phi, red = ar_coeffs(D, 1.0, wG, rG, prim, Lsim)
        S_true, Dt_true, _ = post_cut_from_phi(phi, prim, 0.5)
        rts_half = roots(0.5, wG, rG, prim)
        S_true_direct = reduced(max(d for d, s in rts_half if s > 0), 0.5, wG, rG, prim)['S_direct']
        for T in (2000, 8000, 32000):
            errs = []
            for rep in range(40):
                x = simulate_ar(phi, T, rng)
                Lfit = int(np.ceil(np.log(T) / (2 * np.log(1 / rG.max()))))
                ph = long_ar(x, Lfit)
                S_hat, _, _ = post_cut_from_phi(ph, prim, 0.5)
                errs.append(abs(S_hat - S_true_direct))
            sim.append(dict(deta=deta, T=T, L=Lfit, median_abs_error=float(np.median(errs)),
                            truth=S_true_direct, truth_from_exact_phi=S_true, D_pre=D))
    res['passive_estimator_simulation'] = sim
    for deta in (0.1, 0.05, 0.025):
        e = [(s['T'], s['median_abs_error']) for s in sim if s['deta'] == deta]
        res.setdefault('error_slope_in_logT', {})[str(deta)] = np.polyfit(np.log([a for a, _ in e]), np.log([b for _, b in e]), 1)[0]
    OUT.write_text(json.dumps(res, indent=1, default=float))
    print(json.dumps(res, indent=1, default=float))


if __name__ == '__main__':
    main()


def same_precut_example():
    """(f) Two populations with identical pre-cut equilibrium objects (D, kappa, a*, kappa*, S*) that differ after a
    50% uniform cut. Primitives of Supplement Section S8 (abar=0.6, A=0.2, sF2=1, sX2=0.25). Population 1: one group at
    r=0.7 with weight 0.02. Population 2: groups at r=0.0 and r=0.93 whose weights match S_M at the pre-cut root D and
    at 1, so D and S* coincide (Theorem eq-cut(i))."""
    prim = (0.6, 0.2, 1.0, 0.25)
    w1, r1 = np.array([0.02]), np.array([0.7])
    D = max(d for d, s in roots(1.0, w1, r1, prim) if s > 0)
    r2 = np.array([0.0, 0.93])
    # solve w2 from S_M2(D) = S_M1(D), S_M2(1) = S_M1(1)
    Amat = np.array([[1 / (D - r2[0]), 1 / (D - r2[1])], [1 / (1 - r2[0]), 1 / (1 - r2[1])]])
    w2 = np.linalg.solve(Amat, np.array([SM(D, w1, r1), SM(1.0, w1, r1)]))
    out = dict(D=D, w2=w2.tolist())
    for name, w, r in (('one group at 0.7', w1, r1), ('groups at 0.0 and 0.93', w2, r2)):
        pre = reduced(max(d for d, s in roots(1.0, w, r, prim) if s > 0), 1.0, w, r, prim)
        Dp = max(d for d, s in roots(0.5, w, r, prim) if s > 0)
        post = reduced(Dp, 0.5, w, r, prim)
        out[name] = dict(D_pre=pre['D'], kappa=pre['kappa'], a_star=pre['a_star'], kappa_star=pre['kappa_star'],
                         S_pre=pre['S_direct'], D_post=Dp, S_post=post['S_direct'])
    a, b = out['one group at 0.7'], out['groups at 0.0 and 0.93']
    out['post_gap'] = abs(a['S_post'] - b['S_post'])
    out['pre_feedback_part'] = a['S_pre'] - a['a_star']
    out['gap_share_of_feedback_part'] = out['post_gap'] / out['pre_feedback_part']
    return out


if __name__ == '__main__' and 'same' in __import__('sys').argv[1:]:
    ex = same_precut_example()
    res = json.loads(OUT.read_text())
    res['same_precut_example'] = ex
    OUT.write_text(json.dumps(res, indent=1, default=float))
    print(json.dumps(ex, indent=1, default=float))
