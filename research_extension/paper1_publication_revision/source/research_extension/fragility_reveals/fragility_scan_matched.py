"""Same scan, but economy B's persistence is shifted so that both economies have EXACTLY the same feedback budget S.
Any information left is about composition, not about the distance to instability."""
import json, numpy as np
from fragility_scan import rules, response
def run(K, rc=0.5, dEta=0.1, W=0.3, kappa=0.5):
    (xg, wg), (xr, wr) = rules(K)
    rA, wA = rc + dEta * xg, W * wg; rB, wB = rc + dEta * xr, W * wr
    out = []
    for gap in [0.2, 0.1, 0.05, 0.025, 0.0125, 0.00625, 0.003125]:
        aA = 1 - gap - kappa * np.sum(wA / (1 - rA)); aB = 1 - gap - kappa * np.sum(wB / (1 - rB))
        n = int(60 / gap) + 400
        hA = response(aA, kappa, rA, wA, n); hB = response(aB, kappa, rB, wB, n)
        act = float(np.sum((hA - hB) ** 2))
        m = 1 << int(np.ceil(np.log2(8 * n)))
        ratio = np.abs(np.fft.rfft(hA, m)) ** 2 / np.abs(np.fft.rfft(hB, m)) ** 2
        kl = float(np.mean(ratio - 1 - np.log(ratio)) / 2)
        out.append({"1-S": gap, "aB-aA": aB - aA, "active_sq_norm": act, "passive_kl_rate": kl})
    g = np.log([o["1-S"] for o in out])
    fa = np.polyfit(g[-4:], np.log([o["active_sq_norm"] for o in out][-4:]), 1)[0]
    fp = np.polyfit(g[-4:], np.log([o["passive_kl_rate"] for o in out][-4:]), 1)[0]
    return out, fa, fp
res = {}
for K in (2, 3):
    out, fa, fp = run(K)
    res[K] = {"rows": out, "active_exponent": fa, "passive_exponent": fp}
    print(f"K={K} (same S): active info ~ (1-S)^{fa:.2f}   passive KL rate ~ (1-S)^{fp:.2f}")
    for o in out: print("   1-S=%.5f  active=%.3e  passiveKL=%.3e" % (o["1-S"], o["active_sq_norm"], o["passive_kl_rate"]))
json.dump(res, open("fragility_scan_matched_results.json", "w"), indent=1)
