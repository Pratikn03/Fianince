"""Merge H1 collector output from several collectors (Colab sessions on Drive, GitHub Actions runs) into one folder.

Not part of Test H1's registered pipeline (thesis/evidence/h1_hyperliquid.py is unchanged and keeps its hash): this only
moves recorded files, with the same rules the collector itself applies on restart.
* Hourly trade files trades/<coin>/<date>/<HH>.csv.gz are concatenated and deduplicated by (time, tid).
* Coverage files coverage/<date>.json take the maximum per minute across collectors, never the sum.
* H1_universe.json must be identical everywhere; a mismatch stops the merge.
GitHub Actions runs publish their output as assets of the release `h1-data` (h1-<run id>.tar.gz); `pull_release` downloads
the assets not yet merged and merges them. The trade files are not opened beyond concatenation and deduplication.
Usage (Colab): h1_merge.pull_release(OUT)        Local test: python h1_merge.py --selftest
"""
import argparse
import io
import json
import tarfile
import tempfile
import urllib.request
from pathlib import Path

import pandas as pd

REPO = "Pratikn03/Fianince"
RELEASE_TAG = "h1-data"
COLS = ["time", "side", "px", "sz", "buyer", "seller", "tid"]


def merge_dir(src, dst):
    """Merge one collector folder `src` into `dst`. Returns (trade files merged, coverage days merged)."""
    src, dst = Path(src), Path(dst); dst.mkdir(parents=True, exist_ok=True)
    us, ud = src / "H1_universe.json", dst / "H1_universe.json"
    if us.exists():
        if ud.exists():
            a, b = json.loads(us.read_text())["symbols"], json.loads(ud.read_text())["symbols"]
            if a != b:
                raise RuntimeError(f"universe mismatch between {src} and {dst}; not merging")
        else:
            ud.write_text(us.read_text())
    nt = 0
    for f in sorted((src / "trades").glob("*/*/*.csv.gz")):
        rel = f.relative_to(src); g = dst / rel; g.parent.mkdir(parents=True, exist_ok=True)
        new = pd.read_csv(f)
        if g.exists():
            new = pd.concat([pd.read_csv(g), new])
        new = new.drop_duplicates(["time", "tid"]).sort_values("time")
        tmp = g.with_suffix(".tmp"); new.to_csv(tmp, index=False, compression="gzip"); tmp.replace(g); nt += 1
    nc = 0
    for f in sorted((src / "coverage").glob("*.json")):
        g = dst / "coverage" / f.name; g.parent.mkdir(parents=True, exist_ok=True)
        old = json.loads(g.read_text()) if g.exists() else {}
        for k, v in json.loads(f.read_text()).items():
            old[k] = max(old.get(k, 0.0), v)
        g.write_text(json.dumps(old)); nc += 1
    return nt, nc


def _get(url, accept="application/vnd.github+json"):
    req = urllib.request.Request(url, headers={"Accept": accept, "User-Agent": "h1-merge"})
    return urllib.request.urlopen(req, timeout=120).read()


def release_assets(repo=REPO, tag=RELEASE_TAG):
    try:
        rel = json.loads(_get(f"https://api.github.com/repos/{repo}/releases/tags/{tag}"))
    except urllib.error.HTTPError as err:
        if err.code == 404:
            return []
        raise
    return [(a["name"], a["browser_download_url"]) for a in rel.get("assets", []) if a["name"].endswith(".tar.gz")]


def _safe_extract(raw, dest):
    with tarfile.open(fileobj=io.BytesIO(raw), mode="r:gz") as t:
        for m in t.getmembers():
            p = (Path(dest) / m.name).resolve()
            if not str(p).startswith(str(Path(dest).resolve())) or not (m.isfile() or m.isdir()):
                raise RuntimeError(f"unsafe member {m.name}")
        try:
            t.extractall(dest, filter="data")
        except TypeError:                                 # Python < 3.12
            t.extractall(dest)


def pull_release(out_dir, repo=REPO, tag=RELEASE_TAG, fetch=None):
    """Download release assets not merged yet and merge them into out_dir."""
    out = Path(out_dir); done_f = out / "_merged_assets.json"
    done = set(json.loads(done_f.read_text())) if done_f.exists() else set()
    assets = release_assets(repo, tag) if fetch is None else fetch()
    new = [(n, u) for n, u in assets if n not in done]
    print(f"{len(assets)} assets on the release, {len(new)} not merged yet")
    for name, url in new:
        raw = _get(url, accept="application/octet-stream") if isinstance(url, str) else url()
        with tempfile.TemporaryDirectory() as td:
            _safe_extract(raw, td)
            root = next((p.parent for p in Path(td).rglob("H1_universe.json")), Path(td))
            nt, nc = merge_dir(root, out)
        done.add(name); done_f.write_text(json.dumps(sorted(done)))
        print(f"  merged {name}: {nt} hourly trade files, {nc} coverage days")
    return len(new)


def selftest():
    def write(d, rows, cov, syms=("A", "B")):
        d = Path(d); (d / "trades/A/2026-11-01").mkdir(parents=True, exist_ok=True); (d / "coverage").mkdir(exist_ok=True)
        (d / "H1_universe.json").write_text(json.dumps({"symbols": list(syms)}))
        pd.DataFrame(rows, columns=COLS).to_csv(d / "trades/A/2026-11-01/10.csv.gz", index=False, compression="gzip")
        (d / "coverage/2026-11-01.json").write_text(json.dumps(cov))
    with tempfile.TemporaryDirectory() as a, tempfile.TemporaryDirectory() as b, tempfile.TemporaryDirectory() as out:
        write(a, [[1, "B", 1.0, 1.0, "x", "y", 7], [2, "A", 1.0, 1.0, "y", "x", 8]], {"60": 30.0, "120": 60.0})
        write(b, [[2, "A", 1.0, 1.0, "y", "x", 8], [3, "B", 1.0, 2.0, "x", "z", 9]], {"60": 60.0, "180": 45.0})
        merge_dir(a, out); merge_dir(b, out); merge_dir(b, out)
        t = pd.read_csv(Path(out) / "trades/A/2026-11-01/10.csv.gz")
        assert list(t.tid) == [7, 8, 9]
        cov = json.loads((Path(out) / "coverage/2026-11-01.json").read_text())
        assert cov == {"60": 60.0, "120": 60.0, "180": 45.0}
        bad = tempfile.mkdtemp(); write(bad, [], {}, syms=("C",))
        try:
            merge_dir(bad, out); raise SystemExit("universe mismatch not caught")
        except RuntimeError:
            pass
        # release path with an in-memory tarball
        buf = io.BytesIO()
        with tarfile.open(fileobj=buf, mode="w:gz") as tf:
            tf.add(b, arcname="h1_out")
        n = pull_release(out, fetch=lambda: [("h1-1.tar.gz", lambda: buf.getvalue())])
        assert n == 1 and pull_release(out, fetch=lambda: [("h1-1.tar.gz", lambda: buf.getvalue())]) == 0
        evil = io.BytesIO()
        with tarfile.open(fileobj=evil, mode="w:gz") as tf:
            info = tarfile.TarInfo("../escape.txt"); info.size = 1; tf.addfile(info, io.BytesIO(b"x"))
        try:
            pull_release(out, fetch=lambda: [("h1-2.tar.gz", lambda: evil.getvalue())]); raise SystemExit("unsafe tar accepted")
        except RuntimeError:
            pass
    print("selftest: PASS")


if __name__ == "__main__":
    ap = argparse.ArgumentParser(); ap.add_argument("--selftest", action="store_true")
    if ap.parse_args().selftest:
        selftest()
