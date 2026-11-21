"""Certified (interval-arithmetic) verification of the pure-Nash conditions in Supplement Proposition prop:nashqc
for the example of Companion Proposition insidergame: a=0.3, kappa=0.5, r=0.6, theta=1, T=10, Sigma=sigma^2=1,
W=[-0.515, 0.515].

Arithmetic: Arb ball arithmetic (python-flint). Every quantity is computed on a ball containing a whole cell of
weights, so a bound computed for the ball holds for every weight in the cell. Checks:
  (A) concavity along the insider's best response: d^2 U_G/dw'^2 (w', zeta*(w)) < 0 for all w', w in W;
  (B) residual monotonicity: g'(w) < 0 for all w in W, where g(w) = dU_G/dw (w, zeta*(w));
  (C) boundary signs: g(-0.515) > 0 > g(0.515).
(A)-(C) give a unique pure equilibrium, interior to W (see the supplement text).
"""
import sys
import time
from flint import arb, arb_mat, ctx

ctx.prec = 80
a, kap, r, th, T = arb("0.3"), arb("0.5"), arb("0.6"), arb(1), 10
Sig, sig2 = arb(1), arb(1)
WBAR = arb("0.515")
ONE = arb_mat([[1] for _ in range(T)])
R = arb_mat([[r ** (i - j - 1) if i > j else arb(0) for j in range(T)] for i in range(T)])


def ball(lo, hi):
    lo, hi = arb(lo), arb(hi)
    return (lo + hi) / 2 + arb(0, ((hi - lo) / 2).upper() * 1.0000001)


def h_jets(w):
    h, h1, h2 = [kap], [arb(0)], [arb(0)]
    for t in range(1, T):
        S = sum((r ** (j - 1) * h[t - j] for j in range(1, t + 1)), arb(0))
        S1 = sum((r ** (j - 1) * h1[t - j] for j in range(1, t + 1)), arb(0))
        S2 = sum((r ** (j - 1) * h2[t - j] for j in range(1, t + 1)), arb(0))
        h.append(a * h[t - 1] + kap * w * S)
        h1.append(a * h1[t - 1] + kap * S + kap * w * S1)
        h2.append(a * h2[t - 1] + 2 * kap * S1 + kap * w * S2)
    return h, h1, h2


def lower(hh):
    return arb_mat([[hh[i - j] if i >= j else arb(0) for j in range(T)] for i in range(T)])


def tr(Mx):
    return sum((Mx[i, i] for i in range(T)), arb(0))


def scal(Mx):
    return Mx[0, 0]


def build(w):
    h, h1, h2 = h_jets(w)
    H, H1, H2 = lower(h), lower(h1), lower(h2)
    M = arb_mat([[th * kap if i == j else h[abs(i - j)] / 2 for j in range(T)] for i in range(T)])
    M1 = arb_mat([[arb(0) if i == j else h1[abs(i - j)] / 2 for j in range(T)] for i in range(T)])
    return H, H1, H2, M, M1


def zeta_star(w):
    H, H1, H2, M, M1 = build(w)
    z = M.solve(ONE) * arb("0.5")
    z1 = -(M.solve(M1 * z))
    return z, z1


def d2U(wp, z):
    """d^2/dw'^2 U_G(w', zeta) for a fixed schedule zeta (column arb_mat)."""
    H, H1, H2, _, _ = build(wp)
    G, G1, G2 = H * (1 / kap), H1 * (1 / kap), H2 * (1 / kap)
    Rt = R.transpose()
    zt = z.transpose()
    Iw = scal(ONE.transpose() * R * H1 * z) - scal(zt * (H1.transpose() * Rt * H + H.transpose() * Rt * H1) * z)
    Iww = scal(ONE.transpose() * R * H2 * z) - scal(
        zt * (H2.transpose() * Rt * H + 2 * H1.transpose() * Rt * H1 + H.transpose() * Rt * H2) * z)
    N1 = tr(R * (G1 * G.transpose() + G * G1.transpose()))
    N2 = tr(R * (G2 * G.transpose() + 2 * G1 * G1.transpose() + G * G2.transpose()))
    return 2 * (Sig * Iw - sig2 * N1) + wp * (Sig * Iww - sig2 * N2)


def g_and_gprime(w):
    H, H1, H2, M, M1 = build(w)
    z = M.solve(ONE) * arb("0.5")
    z1 = -(M.solve(M1 * z))
    G, G1 = H * (1 / kap), H1 * (1 / kap)
    G2 = H2 * (1 / kap)
    Rt = R.transpose()
    zt = z.transpose()
    P = H.transpose() * Rt * H
    Q = H1.transpose() * Rt * H + H.transpose() * Rt * H1
    Qw = H2.transpose() * Rt * H + 2 * H1.transpose() * Rt * H1 + H.transpose() * Rt * H2
    I = scal(ONE.transpose() * R * H * z) - scal(zt * P * z)
    Iw = scal(ONE.transpose() * R * H1 * z) - scal(zt * Q * z)
    Iww = scal(ONE.transpose() * R * H2 * z) - scal(zt * Qw * z)
    N = tr(R * G * G.transpose())
    N1 = tr(R * (G1 * G.transpose() + G * G1.transpose()))
    N2 = tr(R * (G2 * G.transpose() + 2 * G1 * G1.transpose() + G * G2.transpose()))
    g = (Sig * I - sig2 * N) + w * (Sig * Iw - sig2 * N1)
    gradI = H.transpose() * Rt * ONE - (P + P.transpose()) * z
    gradIw = H1.transpose() * Rt * ONE - (Q + Q.transpose()) * z
    dwdz = (gradI * Sig + gradIw * (Sig * w)).transpose() * z1
    gp = 2 * (Sig * Iw - sig2 * N1) + w * (Sig * Iww - sig2 * N2) + scal(dwdz)
    return g, gp


def cells(n):
    lo = -WBAR
    step = 2 * WBAR / n
    return [ball(lo + k * step, lo + (k + 1) * step) for k in range(n)]


def main(nB=400, nA=160):
    t0 = time.time()
    out = []
    # (C) boundary signs
    gl, _ = g_and_gprime(-WBAR)
    gr, _ = g_and_gprime(WBAR)
    okC = gl > 0 and gr < 0
    out.append(f"(C) g(-0.515) in {gl.str(6)}; g(0.515) in {gr.str(6)}: {'certified' if okC else 'NOT certified'}")
    # (B) residual monotonicity on W
    worst = None
    okB = True
    for c in cells(nB):
        _, gp = g_and_gprime(c)
        up = gp.upper() if hasattr(gp, 'upper') else gp
        if not (gp < 0):
            okB = False
        worst = up if worst is None or up > worst else worst
    out.append(f"(B) g'(w) < 0 on {nB} cells covering W; largest upper bound {arb(worst).str(5)}: "
               f"{'certified' if okB else 'NOT certified'}")
    # (A) concavity of U_G(., zeta*(w)) for every w, w' in W
    zs = [zeta_star(c)[0] for c in cells(nA)]
    worstA, okA = None, True
    for cp in cells(nA):
        for z in zs:
            v = d2U(cp, z)
            if not (v < 0):
                okA = False
            up = v.upper()
            worstA = up if worstA is None or up > worstA else worstA
    out.append(f"(A) d^2U_G/dw'^2 (w', zeta*(w)) < 0 on {nA}x{nA} cells covering W x W; largest upper bound "
               f"{arb(worstA).str(5)}: {'certified' if okA else 'NOT certified'}")
    out.append(f"time {time.time() - t0:.0f} s; precision {ctx.prec} bits")
    print("\n".join(out))
    return okA and okB and okC


if __name__ == "__main__":
    nB = int(sys.argv[1]) if len(sys.argv) > 1 else 400
    nA = int(sys.argv[2]) if len(sys.argv) > 2 else 160
    sys.exit(0 if main(nB, nA) else 1)
