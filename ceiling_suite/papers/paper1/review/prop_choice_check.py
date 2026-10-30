"""Numerical check of Proposition prop:choice (when an audit trail is chosen). Random parameters; for each case the
attribution-delay saving G on a fine grid is checked against parts (ii) and (iii). Writes prop_choice_check.json."""
import json
import numpy as np

rng = np.random.default_rng(20261030)
viol = {"zero_below_t": 0, "max_at_p": 0, "single_peaked_on_positive_part": 0, "unimodal_whole_domain_(original_wording)": 0, "negative_beyond": 0, "interval_iff_M": 0}
cases = 0
for _ in range(20000):
    K = int(rng.integers(2, 6)); Tbar = 10 ** rng.uniform(1, 5)
    cp = 10 ** rng.uniform(-8, -1); ct = 10 ** rng.uniform(-6, 0)
    dt, dp = (ct / Tbar) ** 0.5, (cp / Tbar) ** (1 / (4 * K - 2))
    if not dt < dp:
        continue                                   # proposition assumes Delta_t < Delta_p
    cases += 1
    d = np.geomspace(dt / 50, 1.0, 4000)
    Tp, Tt = cp * d ** (-(4 * K - 2)), ct * d ** (-2)
    G = np.minimum(Tbar, Tp) - np.minimum(Tbar, Tt)
    tol = 1e-9 * Tbar
    if np.any(np.abs(G[d <= dt]) > tol): viol["zero_below_t"] += 1
    Gstar = Tbar - ct * dp ** (-2)
    if abs(G.max() - Gstar) > 1e-3 * Tbar + 1e-6 and G.max() > Gstar + 1e-6: viol["max_at_p"] += 1
    # (ii) as corrected: G rises up to Delta_p, then falls until after it turns negative, and stays negative
    i = int(np.argmax(G)); dG = np.diff(G); pos = G[1:] > tol
    if np.any(dG[:i] < -tol) or np.any((dG[i:] > tol) & pos[i:]): viol["single_peaked_on_positive_part"] += 1
    if np.any(dG[i:] > tol): viol["unimodal_whole_domain_(original_wording)"] += 1
    dn = (cp / ct) ** (1 / (4 * K - 4))
    if np.any(G[d > dn * 1.0001] > tol): viol["negative_beyond"] += 1
    ell, F, c = 10 ** rng.uniform(-2, 2), 10 ** rng.uniform(0, 6), 10 ** rng.uniform(-2, 3)
    Mstar = F / (ell * Gstar - c) if ell * Gstar > c else np.inf
    for M in [Mstar * 0.5, Mstar * 2] if np.isfinite(Mstar) else [1e9]:
        nonempty = bool(np.any(F / M + c < ell * G))
        if nonempty != (M > Mstar) and abs(M / Mstar - 1) > 1e-6 if np.isfinite(Mstar) else nonempty:
            viol["interval_iff_M"] += 1
out = {"cases": cases, "violations": viol}
json.dump(out, open(__file__.replace(".py", ".json"), "w"), indent=1)
print(out)
