"""Run Test H1's registered collector on your own computer, alongside the GitHub Actions chain.

Why: H1 counts a day only if the connection was live for at least 95% of it. A second collector fills the gaps of the
first; h1_merge.py takes the maximum coverage per minute across collectors and deduplicates trades by trade id, so two
collectors can only help. This script calls the registered collector (h1_hyperliquid.collect) unchanged, with the
registered universe (H1_universe.json, drawn 2026-10-25). It never draws a new universe and never opens trade contents.

Usage, from a clone of the repository:
    pip install websockets numpy pandas scipy
    python thesis/evidence/h1_local_collector.py                 # collects into ./h1_local until you stop it (Ctrl-C)
    python thesis/evidence/h1_local_collector.py --upload        # also uploads a snapshot to the h1-data release
                                                                 # every 6 hours (needs `gh auth login` once)
Keep the computer awake: macOS `caffeinate -dimsu python ...`; Windows: Settings > Power > Sleep: Never;
Linux: `systemd-inhibit python ...`. A short sleep only loses those minutes; the GitHub collector covers them.
"""
import argparse
import asyncio
import json
import shutil
import subprocess
import sys
import tarfile
import time
from datetime import datetime, timezone
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
UNIVERSE = HERE / "H1_universe.json"


def prepare(out):
    out.mkdir(parents=True, exist_ok=True)
    reg = json.loads(UNIVERSE.read_text())
    mine = out / "H1_universe.json"
    if mine.exists():
        if json.loads(mine.read_text())["symbols"] != reg["symbols"]:
            raise SystemExit(f"{mine} differs from the registered universe; use an empty folder")
    else:
        shutil.copy(UNIVERSE, mine)
    return reg["symbols"]


def coverage_report(out):
    rows = []
    for f in sorted((out / "coverage").glob("*.json"))[-3:]:
        c = sum(json.loads(f.read_text()).values()) / 86400
        rows.append(f"{f.stem} {100 * c:5.1f}%")
    return "; ".join(rows) or "no coverage yet"


def upload(out):
    stamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M")
    name = f"h1-local-{stamp}.tar.gz"
    with tarfile.open(name, "w:gz") as t:
        t.add(out, arcname="h1_out")
    r = subprocess.run(["gh", "release", "upload", "h1-data", name, "-R", "Pratikn03/Fianince"],
                       capture_output=True, text=True)
    Path(name).unlink(missing_ok=True)
    print(f"upload {name}: {'ok' if r.returncode == 0 else r.stderr.strip()[:200]}", flush=True)


def main():
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--out", default="h1_local", help="output folder (default ./h1_local)")
    ap.add_argument("--upload", action="store_true", help="upload a snapshot to the h1-data release every 6 hours")
    ap.add_argument("--hours", type=float, default=6.0, help="length of one collection block")
    args = ap.parse_args()
    out = Path(args.out).resolve()
    syms = prepare(out)
    try:
        import websockets  # noqa: F401
    except ImportError:
        raise SystemExit("missing package: run  pip install websockets numpy pandas scipy")
    import h1_hyperliquid as C  # the registered collector, unchanged
    print(f"H1 local collector: {len(syms)} coins, output {out}", flush=True)
    while True:
        try:
            asyncio.run(C.collect(str(out), hours=args.hours, symbols=syms))
        except KeyboardInterrupt:
            print("stopped by user", flush=True)
            break
        except Exception as err:  # network loss, sleep, etc.: wait and restart
            print("collector stopped:", repr(err)[:200], "- restarting in 30 s", flush=True)
            time.sleep(30)
        print("coverage:", coverage_report(out), flush=True)
        if args.upload:
            upload(out)


if __name__ == "__main__":
    main()
