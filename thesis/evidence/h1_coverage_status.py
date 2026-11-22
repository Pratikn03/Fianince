"""H1 progress from coverage files only: how many UTC days so far meet the registered 95% live-connection rule.

Reads coverage (seconds of live connection per minute) from local collector folders and/or the `cov-*.json` assets of
the `h1-data` release, merges them by the maximum per minute (as h1_merge.py does), and prints each day's coverage.
It never opens trade files. A day counted here is necessary for H1's valid-day rule, not sufficient: the registered
rule also applies C3's price checks per coin, at opening.

The `cov-*.json` assets exist only from 20 November 2026. With --with-run-archives, the script also reads the coverage
files inside each run's `h1-<run>.tar.gz` asset, which go back to the first GitHub run on 15 November. It reads only
the archive members under `coverage/`; trade members are skipped without being extracted or parsed.
Usage:  python thesis/evidence/h1_coverage_status.py --from-release [--with-run-archives] [folder ...]
"""
import argparse
import io
import json
import os
import tarfile
import urllib.request
from pathlib import Path, PurePosixPath

REPO, TAG, COVER_MIN = "Pratikn03/Fianince", "h1-data", 0.95


def _get(url, accept="application/vnd.github+json"):
    headers = {"Accept": accept, "User-Agent": "h1-coverage"}
    if os.environ.get("GH_TOKEN"):
        headers["Authorization"] = f"Bearer {os.environ['GH_TOKEN']}"
    return urllib.request.urlopen(urllib.request.Request(url, headers=headers), timeout=60).read()


def from_release(with_run_archives=False):
    rel = json.loads(_get(f"https://api.github.com/repos/{REPO}/releases/tags/{TAG}"))
    for a in rel.get("assets", []):
        if a["name"].startswith("cov-") and a["name"].endswith(".json"):
            yield json.loads(_get(a["url"], accept="application/octet-stream"))
        elif with_run_archives and a["name"].startswith("h1-") and a["name"].endswith(".tar.gz"):
            yield coverage_members(_get(a["url"], accept="application/octet-stream"))


def coverage_members(raw):
    """{day: {minute: seconds}} from the coverage/*.json members of one run archive; other members are not read."""
    out = {}
    with tarfile.open(fileobj=io.BytesIO(raw), mode="r:gz") as tf:
        for m in tf:
            p = PurePosixPath(m.name)
            if m.isfile() and p.parent.name == "coverage" and p.suffix == ".json":
                out[p.stem] = json.load(tf.extractfile(m))
    return out


def from_folder(d):
    return {f.stem: json.loads(f.read_text()) for f in sorted(Path(d).glob("coverage/*.json"))}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("folders", nargs="*")
    ap.add_argument("--from-release", action="store_true")
    ap.add_argument("--with-run-archives", action="store_true")
    a = ap.parse_args()
    merged = {}
    sources = [from_folder(d) for d in a.folders] + (list(from_release(a.with_run_archives)) if a.from_release else [])
    for src in sources:
        for day, mins in src.items():
            m = merged.setdefault(day, {})
            for k, v in mins.items():
                m[k] = max(m.get(k, 0.0), v)
    ok = 0
    for day in sorted(merged):
        c = sum(merged[day].values()) / 86400
        ok += c >= COVER_MIN
        print(f"{day}  {100 * c:5.1f}%  {'meets 95%' if c >= COVER_MIN else ''}")
    print(f"{len(sources)} sources; {ok} of {len(merged)} days meet the 95% connection rule (H1 needs 30 per coin)")


if __name__ == "__main__":
    main()
