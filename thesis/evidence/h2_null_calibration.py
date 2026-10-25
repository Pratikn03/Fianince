import sys, json, tempfile, numpy as np
sys.path.insert(0, "/home/claude/fianince/thesis/evidence")
import h2_cascade as H2
seed = int(sys.argv[1])
with tempfile.TemporaryDirectory() as td:
    syms, dates = H2.H._synthetic(td, n_coins=21, n_days=31, rng=np.random.default_rng(seed))
    tables = {s: H2.coin_table(td, s, dates)[0] for s in syms}
    for s, t in tables.items(): t["coin"] = s
    e = H2.evaluate(tables)
    sc = e["per_coin"]
    print(json.dumps({"seed": seed, "P1": [e["P1"]["positive"], e["P1"]["negative"], round(e["P1"]["p"], 4)],
                      "D_pos": sum(v["score_margin_decline"] > 0 for v in sc.values()),
                      "P2": [round(e["P2"]["delta_r2_pts"], 3), [round(x, 3) for x in e["P2"]["ci_pts"]], round(e["P2"]["cw_p"], 3)]}))
