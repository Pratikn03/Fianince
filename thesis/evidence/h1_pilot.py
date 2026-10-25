"""EXPLORATORY pilot for Test H1 (not a registered test; nothing here is confirmatory evidence).

Purpose: an early, labelled-exploratory look at whether real Hyperliquid accounts are distinguishable by memory, and a
check that H1's registered pipeline runs on real data, WITHOUT touching H1's data. The pilot records different coins
(the 10 highest-volume Hyperliquid perpetuals that are not in H1's universe; H1 used ranks 11-40 at its start), in a separate Drive folder, and
asserts that no pilot coin is in H1_universe.json. Only the universe file of H1 is read, never its trades.

It uses h1_hyperliquid's registered functions unchanged; the only differences, fixed here before any pilot data exist:
at least 5 valid days per coin (H1: 30) and 80% connection coverage per day (H1: 95%), because a one-week pilot cannot
meet H1's thresholds. A pilot pass or failure does not change H1, whose design is frozen.
"""
import json
from pathlib import Path

import h1_hyperliquid as H

PILOT_RANKS = (0, 10)          # ranks 1..10 by 24-hour notional volume
PILOT_MIN_DAYS, PILOT_COVER = 5, 0.80


def draw_pilot_universe(out_dir, h1_universe_path, fetch=H.http_post):
    """Pilot coins: the 10 highest-volume ASCII alphanumeric, not delisted perpetuals not in H1's universe. Saved once."""
    out = Path(out_dir); out.mkdir(parents=True, exist_ok=True)
    p = out / "H1_pilot_universe.json"
    if p.exists():
        return json.loads(p.read_text())["symbols"]
    h1 = set(json.loads(Path(h1_universe_path).read_text())["symbols"])
    meta, ctxs = fetch({"type": "metaAndAssetCtxs"})
    rows = []
    for a, c in zip(meta["universe"], ctxs):
        name = a["name"]
        if a.get("isDelisted") or not name.isascii() or not name.isalnum():
            continue
        rows.append((float(c.get("dayNtlVlm") or 0), name))
    rows.sort(reverse=True)
    chosen = [n for _, n in rows if n not in h1][:PILOT_RANKS[1] - PILOT_RANKS[0]]
    assert not set(chosen) & h1
    p.write_text(json.dumps({"rule": "EXPLORATORY pilot: the 10 highest-volume perpetuals not in H1_universe.json",
                             "symbols": chosen, "h1_universe_checked": sorted(h1)}, indent=1) + "\n")
    return chosen


def analyse(out_dir, today=None):
    """H1's per-coin evaluation on the pilot coins with the pilot's thresholds; writes H1_pilot_results.json."""
    old = (H.MIN_DAYS, H.COVER_MIN, H.MIN_COINS)
    H.MIN_DAYS, H.COVER_MIN, H.MIN_COINS = PILOT_MIN_DAYS, PILOT_COVER, 1
    try:
        syms = json.loads((Path(out_dir) / "H1_pilot_universe.json").read_text())["symbols"]
        today = today or H.datetime.now(H.timezone.utc).strftime("%Y-%m-%d")
        dates = [d for d in H.collected_dates(out_dir) if d < today]
        per = {}
        for j, s in enumerate(syms):
            try:
                per[s] = H.coin_eval(out_dir, s, dates, j)
            except Exception as err:                       # a pipeline failure on real data is a finding of the pilot
                per[s] = {"excluded": f"pipeline error: {err!r}"[:300], "n_days": None}
            v = per[s]
            print(f"  {s}: valid={v.get('n_days', len(v.get('valid_days', [])))} tag={v.get('tag_identified')} "
                  f"price={v.get('identified')} margin={v.get('sign')} {v.get('excluded', '')}", flush=True)
        ev = H.evaluate(per)
    finally:
        H.MIN_DAYS, H.COVER_MIN, H.MIN_COINS = old
    res = {"kind": "EXPLORATORY PILOT for H1 - not a registered test, not confirmatory",
           "thresholds": {"min_valid_days": PILOT_MIN_DAYS, "coverage": PILOT_COVER, "coins": "10 highest-volume not in H1"},
           "collected_days": dates, "symbols": syms, "per_coin": per, "evaluation": ev}
    (Path(out_dir) / "H1_pilot_results.json").write_text(json.dumps(res, indent=1, default=float) + "\n")
    print(json.dumps({k: v for k, v in ev.items() if k != "secondary"}, indent=1, default=float))
    return res
