"""Data compatibility: what a finite window of price responses allows (Paper 2, Theorem thm:window; blueprint D6, D8, E05).

Sharp finite-window bounds on Phi = int f dM, f(r) = 1/(1-r), over measures on [0, rho] with given moments. Extremes are
attained at the principal representations (Markov-Krein; Krein and Nudel'man 1977, Thms IV.1.1, IV.6.1): max at the upper
representation (contains rho), min at the lower one. Computed in 60-digit arithmetic (mpmath), and then CERTIFIED: the
endpoints are re-derived as weak-duality bounds from polynomials whose sign condition is proved in outward-rounded interval
arithmetic, so the returned enclosure contains the exact interval whatever the floating-point error.
"""
import mpmath as mp
import numpy as np
from interval import IV
from model_contracts import summed_response

mp.mp.dps = 60



def gauss_from_moments(mom, m):
    """m-point Gauss rule for a positive functional with moments mom[0..2m-1] (Golub-Welsch via Hankel Cholesky)."""
    if m == 0:
        return [], []
    H = mp.matrix(m + 1, m + 1)
    for i in range(m + 1):
        for j in range(m + 1):
            H[i, j] = mom[i + j] if i + j < len(mom) else mp.mpf(0)
    # Cholesky of the leading m x m block plus the needed extra entries
    R = mp.matrix(m + 1, m + 1)
    for i in range(m + 1):
        for j in range(i, m + 1):
            s = H[i, j] - sum(R[k, i] * R[k, j] for k in range(i))
            if i == j:
                if j == m:
                    R[i, j] = mp.mpf(1); continue
                if s <= mp.mpf("1e-45") * (H[0, 0] if H[0, 0] > 0 else mp.mpf(1)):
                    raise ValueError("moment sequence not positive definite at order %d" % i)
                R[i, j] = mp.sqrt(s)
            else:
                R[i, j] = s / R[i, i]
    al = []; be = []
    for k in range(m):
        a_k = R[k, k + 1] / R[k, k] - (R[k - 1, k] / R[k - 1, k - 1] if k > 0 else 0)
        al.append(a_k)
        if k < m - 1:
            be.append(R[k + 1, k + 1] / R[k, k])
    Jm = mp.matrix(m, m)
    for k in range(m):
        Jm[k, k] = al[k]
        if k < m - 1:
            Jm[k, k + 1] = be[k]; Jm[k + 1, k] = be[k]
    E, Q = mp.eighe(Jm)
    nodes = [E[i] for i in range(m)]
    weights = [mom[0] * Q[0, i] ** 2 for i in range(m)]
    return nodes, weights


def principal(c, rho, which):
    """Upper ('upper', contains rho) or lower principal representation of moments c[0..d] on [0, rho]."""
    c = [mp.mpf(x) for x in c]; rho = mp.mpf(rho); d = len(c) - 1
    if which == "upper":
        if d % 2 == 0:
            m = d // 2
            nu = [rho * c[j] - c[j + 1] for j in range(2 * m)]
            x, v = gauss_from_moments(nu, m)
            at = [(xi, vi / (rho - xi)) for xi, vi in zip(x, v)]
            at.append((rho, c[0] - sum(w for _, w in at)))
        else:
            m = (d + 1) // 2
            nu = [rho * c[j + 1] - c[j + 2] for j in range(2 * m - 2)]
            x, v = gauss_from_moments(nu, m - 1)
            at = [(xi, vi / (xi * (rho - xi))) for xi, vi in zip(x, v)]
            s0 = c[0] - sum(w for _, w in at); s1 = c[1] - sum(w * xi for xi, w in at)
            w_rho = s1 / rho; at += [(mp.mpf(0), s0 - w_rho), (rho, w_rho)]
    else:
        if d % 2 == 0:
            m = d // 2
            nu = [c[j + 1] for j in range(2 * m)]
            x, v = gauss_from_moments(nu, m)
            at = [(xi, vi / xi) for xi, vi in zip(x, v)]
            at.append((mp.mpf(0), c[0] - sum(w for _, w in at)))
        else:
            m = (d + 1) // 2
            x, v = gauss_from_moments(c, m)
            at = list(zip(x, v))
    return at


def phi_bounds(c, rho):
    f = lambda r: 1 / (1 - r)
    lo = principal(c, rho, "lower"); up = principal(c, rho, "upper")
    return float(sum(w * f(x) for x, w in lo)), float(sum(w * f(x) for x, w in up)), lo, up


def check_rep(at, c, rho, tol=1e-30):
    ok_w = all(w >= -tol for _, w in at); ok_x = all(-tol <= x <= rho + tol for x, _ in at)
    err = max(abs(sum(w * x ** j for x, w in at) - mp.mpf(c[j])) for j in range(len(c)))
    return bool(ok_w and ok_x), float(err)


def best_approx_error_formula(n, rho):
    """E_n(1/(1-r); [0, rho]) = (2/rho) q^n/(x0^2-1), x0 = 2/rho - 1, q = x0 - sqrt(x0^2-1) (Chebyshev; Achieser 1956)."""
    x0 = 2.0 / rho - 1.0; q = x0 - (x0 ** 2 - 1) ** 0.5
    return (2.0 / rho) * q ** n / (x0 ** 2 - 1)


# ================================================================ certified endpoints (Lemma lem:certnum)



def hermite_coeffs(at, rbar, deg):
    """Monomial coefficients (mp) of the degree-`deg` polynomial interpolating f at the nodes of `at`, with derivative
    conditions at interior nodes (0 < x < rbar)."""
    f = lambda x: 1 / (1 - x); fp = lambda x: 1 / (1 - x) ** 2
    rows, rhs = [], []
    for x, _ in at:
        x = mp.mpf(x)
        rows.append([x ** j for j in range(deg + 1)]); rhs.append(f(x))
        if mp.mpf(0) + mp.mpf("1e-40") < x < mp.mpf(rbar) - mp.mpf("1e-40"):
            rows.append([j * x ** (j - 1) if j else mp.mpf(0) for j in range(deg + 1)]); rhs.append(fp(x))
    if len(rows) != deg + 1:
        raise ValueError(f"{len(rows)} interpolation conditions for degree {deg}")
    c = mp.lu_solve(mp.matrix(rows), mp.matrix(rhs))
    return [c[j] for j in range(deg + 1)]


def _horner_iv(coef, X):
    acc = IV(np.full_like(X.lo, coef[-1]))
    for c in coef[-2::-1]:
        acc = acc * X + c
    return acc


def _dhorner_iv(coef, X):
    d = [j * c for j, c in enumerate(coef)][1:]
    return _horner_iv(d, X) if d else IV(np.zeros_like(X.lo))


def verify_sign(coef, rbar, upper, slack, max_boxes=400000):
    """Prove G(x) = p(x) + slack - f(x) > 0 (upper) or G(x) = f(x) - p(x) + slack > 0 (lower) for all x in [0, rbar], with
    the mean-value form G(X) in G(m) + G'(X)(X - m) evaluated in outward-rounded interval arithmetic, and adaptive bisection."""
    sg = 1.0 if upper else -1.0
    boxes = [(0.0, float(np.nextafter(rbar, np.inf)))]
    n = 0
    while boxes:
        if n > max_boxes:
            return False, n
        lo = np.array([b[0] for b in boxes]); hi = np.array([b[1] for b in boxes])
        X = IV(lo, hi); M = IV(0.5 * (lo + hi)); n += len(boxes)
        Gm = (_horner_iv(coef, M) - 1.0 / (1.0 - M)) * sg + slack
        dG = (_dhorner_iv(coef, X) - 1.0 / (1.0 - X).sq()) * sg
        G = Gm + dG * (X - M)
        G0 = ((_horner_iv(coef, X) - 1.0 / (1.0 - X)) * sg + slack)          # natural form; keep the better lower bound
        bad = np.maximum(G.lo, G0.lo) <= 0
        if not np.any(bad):
            return True, n
        new = []
        for a, b in zip(lo[bad], hi[bad]):
            m = 0.5 * (a + b)
            if m <= a or m >= b:
                return False, n
            new += [(a, m), (m, b)]
        boxes = new
    return True, n


def certified_phi_bounds(k, rbar, rel_slack=1e-11):
    """Outward-valid [Phi_lo, Phi_hi] for all measures on [0, rbar] with moments k[0..n-1]. Returns a dict with the certified
    endpoints, the high-precision principal-representation values and the verification effort."""
    n = len(k); deg = n - 1
    kk = [mp.mpf(x) for x in k]
    out = {}
    for which, upper in (("upper", True), ("lower", False)):
        at = principal(kk, rbar, which)
        exact = sum(w / (1 - x) for x, w in at)
        coef_mp = hermite_coeffs(at, rbar, deg)
        coef = [float(c) for c in coef_mp]
        # slack: a relative margin, and at least what rounding the coefficients to doubles can cost
        slack = max(rel_slack * float(abs(exact) / kk[0]), 64 * np.finfo(float).eps * float(sum(abs(c) * rbar ** j for j, c in enumerate(coef_mp))))
        ok, nbox = verify_sign(coef, rbar, upper, slack)
        tries = 0
        while not ok and tries < 4:                     # widen the slack if rounding of the coefficients needs it
            slack *= 100; tries += 1
            ok, nb2 = verify_sign(coef, rbar, upper, slack); nbox += nb2
        if not ok:
            out[which] = {"certified": None, "exact_hp": float(exact), "boxes": nbox}
            continue
        Kv = IV.enclose(np.array([float(x) for x in k]))
        tot = IV(0.0)
        for j, c in enumerate(coef):
            tot = tot + IV(np.array(c)) * IV(Kv.lo[j], Kv.hi[j])
        if upper:
            bound = float(np.nextafter((tot + IV(slack) * IV(Kv.lo[0], Kv.hi[0])).hi, np.inf))
        else:
            bound = float(np.nextafter((tot - IV(slack) * IV(Kv.lo[0], Kv.hi[0])).lo, -np.inf))
        out[which] = {"certified": bound, "exact_hp": float(exact), "boxes": nbox, "slack": slack}
    return {"Phi_lo_cert": out["lower"]["certified"], "Phi_hi_cert": out["upper"]["certified"],
            "Phi_lo_hp": out["lower"]["exact_hp"], "Phi_hi_hp": out["upper"]["exact_hp"],
            "boxes_checked": out["lower"]["boxes"] + out["upper"]["boxes"]}


def _moments_mp(a, kappa, q, eta, n):
    """Moments k_0..k_{n-1} inverted in 60-digit arithmetic from the 60-digit state-space impulse response."""
    a_m, k_m = mp.mpf(a), mp.mpf(kappa)
    q_m = [mp.mpf(float(x)) for x in q]
    e_m = [mp.mpf(float(x)) for x in eta]
    x = k_m; y = [e * x for e in e_m]; h = [x]
    for _ in range(n):
        x = a_m * x + k_m * sum(qi * yi for qi, yi in zip(q_m, y))
        y = [(1 - e) * yi + e * x for e, yi in zip(e_m, y)]
        h.append(x)
    k = []
    for t in range(n):
        kt = (h[t + 1] - a_m * h[t] - k_m * sum(k[m] * h[t - m] for m in range(t))) / (k_m ** 2)
        k.append(kt)
    return k


def run_window_checks():
    """Theorem thm:window: an eight-cohort economy with memory bound 0.95, windows of several lengths."""
    rhoB = 0.95; aB, kaB = 0.4, 1.0
    rB = np.linspace(0.05, 0.93, 8); etaB = 1 - rB; qB = np.full(8, 0.42 / 8)
    TB = []
    for n in [3, 4, 6, 8, 10, 12, 16, 20]:
        c = _moments_mp(aB, kaB, qB, etaB, n)
        try:
            lo, up, L_, U_ = phi_bounds(c, rhoB)
        except ValueError:
            TB.append({"n": n, "note": "moment vector on the boundary: measure identified"}); continue
        w = up - lo; bnd = 2 * float(c[0]) * best_approx_error_formula(n - 1, rhoB)
        TB.append({"n": n, "Phi_lo": lo, "Phi_up": up, "Phi_true": float(qB.sum()),
                   "S_lo": summed_response(aB, kaB, lo), "S_up": summed_response(aB, kaB, up),
                   "width": w, "width_bound": bnd, "within_bound": w <= bnd * (1 + 1e-9)})
    div = []
    r_ = np.array([0.2, 0.5, 0.8]); w_ = np.array([0.3, 0.3, 0.2]); cc = [float(np.sum(w_ * r_ ** j)) for j in range(4)]
    for rho in [0.9, 0.99, 0.999, 0.9999]:
        div.append({"rho": rho, "Phi_up": phi_bounds(cc, rho)[1]})
    return {"market_B_rho_0.95": TB, "divergence_as_rho_to_1": div}



def run_certified_numerics():
    """E05: certified enclosures contain the 60-digit principal-representation values; report the overhead."""
    aB, kaB = 0.4, 1.0                       # the eight-cohort economy of run_window_checks (Section 5 example)
    rB = np.linspace(0.05, 0.93, 8); qB = np.full(8, 0.42 / 8)
    rows = []
    for n in [4, 6, 8, 10, 12]:
        k = _moments_mp(aB, kaB, qB, 1 - rB, n)
        c = certified_phi_bounds(k, 0.95)
        Shi = lambda P: summed_response(aB, kaB, P)
        rows.append({"n_moments": n, "lags_used": f"0-{n}", **c,
                     "contains": bool(c["Phi_lo_cert"] <= c["Phi_lo_hp"] and c["Phi_hi_cert"] >= c["Phi_hi_hp"]),
                     "rel_overhead": float(max(c["Phi_hi_cert"] - c["Phi_hi_hp"], c["Phi_lo_hp"] - c["Phi_lo_cert"]) / c["Phi_hi_hp"]),
                     "S_interval_cert": [Shi(c["Phi_lo_cert"]), Shi(c["Phi_hi_cert"])], "S_interval_hp": [Shi(c["Phi_lo_hp"]), Shi(c["Phi_hi_hp"])]})
    r_ = np.array([0.2, 0.5, 0.8]); w_ = np.array([0.3, 0.3, 0.2]); cc = [float(np.sum(w_ * r_ ** j)) for j in range(4)]
    for rho in [0.9, 0.99, 0.999]:
        c = certified_phi_bounds(cc, rho)
        rows.append({"three_cohort_rho": rho, **c, "contains": bool(c["Phi_lo_cert"] <= c["Phi_lo_hp"] and c["Phi_hi_cert"] >= c["Phi_hi_hp"])})
    return {"rows": rows, "pass": all(r["contains"] for r in rows)}
