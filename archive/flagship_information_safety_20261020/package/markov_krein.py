"""Theorem B: sharp finite-window bounds on Phi = int f dM, f(r) = 1/(1-r), over measures on [0, rho] with given moments.
Extremes are attained at the principal representations (Markov-Krein; Krein and Nudel'man 1977, Thms IV.1.1, IV.6.1):
max at the upper representation (contains rho), min at the lower one. Computed in high precision (mpmath)."""
import mpmath as mp

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
                if s <= 0:
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
