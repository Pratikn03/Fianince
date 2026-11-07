"""E2: manipulation rents when the dealer misjudges the aggregate feedback kernel.

Finite horizon T. Price changes s_t = p_t - p_{t-1}, p_0 = 0. Dealer: s_t = lam * (y_t - fhat_t), with
fhat_t its predicted feedback flow. Feedback error e_t = f_t - fhat_t = sum_m dk_m s_{t-1-m} = (D s)_t, D strictly lower
Toeplitz. Hence s = lam (I - lam D)^{-1} (x + z), p = C s with C the lower-triangular all-ones matrix.
Insider: deterministic schedule given v, x = b v. Expected profit E[sum_t (v - p_t) x_t] = S0 [1'b - b' A_D b],
A_D = lam C (I - lam D)^{-1}. With Q_D = (A_D + A_D')/2 positive definite: optimum b* = Q_D^{-1} 1 / 2,
value V(D) = S0/4 * 1' Q_D^{-1} 1. First order: V(D) - V(0) = -(S0/4) u' sym(lam^2 C D) u + O(|D|^2), u = Q_0^{-1} 1.
"""
import json
import numpy as np

def mats(T, lam, dk):
    C = np.tril(np.ones((T, T)))
    D = np.zeros((T, T))
    for t in range(T):
        for m in range(t):
            if m < len(dk):
                D[t, t - 1 - m] = dk[m]
    return C, D

def value(T, lam, dk, S0=1.0):
    C, D = mats(T, lam, dk)
    A = lam * C @ np.linalg.inv(np.eye(T) - lam * D)
    Q = (A + A.T) / 2
    ev = np.linalg.eigvalsh(Q)
    if ev.min() <= 0:
        return np.nan, ev.min()
    one = np.ones(T)
    return S0 / 4 * one @ np.linalg.solve(Q, one), ev.min()

def first_order(T, lam, dk, S0=1.0):
    C, D = mats(T, lam, dk)
    Q0 = lam * (C + C.T) / 2
    u = np.linalg.solve(Q0, np.ones(T))
    M = lam ** 2 * C @ D
    return -(S0 / 4) * u @ ((M + M.T) / 2) @ u

def main():
    T, lam = 10, 0.5
    out = {"T": T, "lambda": lam, "rows": []}
    V0, _ = value(T, lam, [0.0])
    for shape, base in [("positive feedback underestimated", [0.4 * 0.7 ** m for m in range(T)]),
                        ("positive feedback overestimated", [-0.4 * 0.7 ** m for m in range(T)])]:
        for eps in [0.4, 0.2, 0.1, 0.05, 0.025, 0.0125]:
            dk = [eps * b for b in base]
            V, emin = value(T, lam, dk)
            fo = first_order(T, lam, dk)
            out["rows"].append({"shape": shape, "eps": eps, "V0": V0, "V": V, "gain": V - V0, "first_order": fo,
                                "gain_over_eps": (V - V0) / eps, "min_eig_Q": emin})
            print(f"{shape:34s} eps={eps:7.4f} gain={V-V0:+.5f} first-order={fo:+.5f} gain/eps={(V-V0)/eps:+.4f}")
    json.dump(out, open("e2_rents_results.json", "w"), indent=1)

if __name__ == "__main__":
    main()
