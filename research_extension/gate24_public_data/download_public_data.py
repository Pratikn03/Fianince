#!/usr/bin/env python3
"""
Gate 2–4 Public Data Downloader — Machine Markets
===================================================
Downloads public data from Binance Vision (data.binance.vision) and
Binance public REST API (data-api.binance.vision) with no authentication.

Data sources (all publicly available, no API key required):
  1. Binance Vision monthly klines (1m OHLCV) — BTC, ETH, SOL Jan–Mar 2025
  2. Binance Vision monthly aggTrades — BTC, ETH, SOL Jan 2025
  3. Live order-book depth snapshots — BTC, ETH, SOL (real-time, 1000 levels)

Local hashes establish byte identity only. Official checksum verification requires
a matching provider checksum. Live REST snapshots are not historical bookDepth,
and public data alone does not validate execution, fills or dealer capacity.
Use --offline to audit cached files without accessing the network.
"""
from __future__ import annotations
import hashlib
import argparse
from datetime import datetime, timezone
import json
import time
import urllib.request
from urllib.parse import urlparse
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[2]
RAW = ROOT / "research_extension" / "data" / "raw" / "binance" / "spot"
OUT = ROOT / "research_extension" / "outputs" / "evidence_repair_20260926" / "gate24"

KLINES_BASE   = "https://data.binance.vision/data/spot/monthly/klines"
TRADES_BASE   = "https://data.binance.vision/data/spot/monthly/aggTrades"
DEPTH_BASE    = "https://data-api.binance.vision/api/v3/depth"

# Symbols and months to download
KLINES_SPEC = [
    ("BTCUSDT", "1m", ["2025-01", "2025-02", "2025-03"]),
    ("ETHUSDT", "1m", ["2025-01", "2025-02", "2025-03"]),
    ("SOLUSDT", "1m", ["2025-01", "2025-02", "2025-03"]),
    ("DOGEUSDT","1m", ["2025-01", "2025-02"]),
    ("ADAUSDT", "1m", ["2025-01", "2025-02"]),
]

AGTRADES_SPEC = [
    ("BTCUSDT",  ["2025-01", "2025-02"]),
    ("ETHUSDT",  ["2025-01", "2025-02"]),
    ("SOLUSDT",  ["2025-01", "2025-02"]),
]

DEPTH_SYMBOLS = ["BTCUSDT", "ETHUSDT", "SOLUSDT", "DOGEUSDT", "ADAUSDT"]
DEPTH_LIMIT = 1000   # finite REST snapshot; not the complete historical book

MANIFEST: list[dict[str, Any]] = []


# ─────────────────────────────── Helpers ────────────────────────────────────

def sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def checksum_matches(data: bytes, checksum_text: str, filename: str) -> bool:
    """Require both the SHA-256 and the exact archive name in a sidecar."""
    records = [line.split() for line in checksum_text.strip().splitlines()]
    return any(len(row) == 2 and row[0].lower() == sha256_bytes(data)
               and row[1].lstrip("*") == filename for row in records)


def audit_cached_file(path: Path, url: str = "") -> dict[str, Any]:
    """Read local evidence only; never trust an old manifest's verified flag."""
    data = path.read_bytes()
    live = "depth" in path.name or "/api/v3/depth" in url
    sidecar = path.with_name(path.name + ".CHECKSUM")
    verified = False
    state = "not_applicable_live_rest" if live else "missing_official_sidecar"
    if not live and sidecar.exists():
        try:
            verified = checksum_matches(data, sidecar.read_text(), path.name)
        except UnicodeError:
            verified = False
        state = "matched_cached_official_sidecar" if verified else "mismatch_or_invalid_sidecar"
    return {
        "path": str(path.relative_to(ROOT)) if path.is_relative_to(ROOT) else str(path),
        "url": url, "bytes": len(data), "sha256": sha256_bytes(data),
        "local_sha256_computed": True, "checksum_verified": verified,
        "official_checksum_status": state,
        "checksum_sidecar": str(sidecar) if sidecar.exists() and not live else None,
        "checksum_sidecar_sha256": sha256_bytes(sidecar.read_bytes()) if sidecar.exists() and not live else None,
        "source_kind": "live_rest_snapshot" if live else "historical_archive",
        "historical_book_depth": False,
        "capture_timestamp": None if live else "see archive rows",
        "verification_basis": "local cached evidence; no provider contacted",
    }


def download(url: str, retries: int = 3, delay: float = 2.0) -> bytes:
    for attempt in range(retries):
        try:
            print(f"  Fetching {url}", flush=True)
            req = urllib.request.Request(url, headers={"User-Agent": "machine-markets-research/1.0"})
            with urllib.request.urlopen(req, timeout=90) as resp:
                return resp.read()
        except Exception as exc:
            print(f"    Attempt {attempt+1}/{retries} failed: {exc}", flush=True)
            if attempt < retries - 1:
                time.sleep(delay * (attempt + 1))
    raise RuntimeError(f"All {retries} attempts failed for {url}")


def verify_checksum_file(data: bytes, checksum_url: str, cache_path: Path | None = None) -> bool:
    """Download the official .CHECKSUM file and verify SHA-256."""
    try:
        checksum = download(checksum_url)
        filename = Path(urlparse(checksum_url).path).name.removesuffix(".CHECKSUM")
        if checksum_matches(data, checksum.decode(), filename):
            if cache_path is not None and not cache_path.exists():
                with cache_path.open("xb") as handle:
                    handle.write(checksum)
            print(f"    ✓ Official checksum verified", flush=True)
            return True
        print("    CHECKSUM MISMATCH or invalid archive name", flush=True)
        return False
    except Exception as exc:
        print(f"    ⚠ Could not fetch official checksum ({exc}), logging local SHA-256 only", flush=True)
        return False


def save_and_record(path: Path, data: bytes, url: str, verified: bool):
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("xb") as handle:
        handle.write(data)
    digest = sha256_bytes(data)
    MANIFEST.append({
        "path": str(path.relative_to(ROOT)) if path.is_relative_to(ROOT) else str(path),
        "url": url,
        "bytes": len(data),
        "sha256": digest,
        "local_sha256_computed": True,
        "checksum_verified": bool(verified and "/api/v3/depth" not in url),
        "source_kind": "live_rest_snapshot" if "/api/v3/depth" in url else "historical_archive",
        "historical_book_depth": False,
    })
    print(f"    Saved {path.name}  ({len(data):,} bytes  sha256={digest[:16]}…)", flush=True)


# ───────────────────────────── Klines ────────────────────────────────────────

def download_klines():
    print("\n=== [1/3] Downloading Klines (1-minute OHLCV) ===", flush=True)
    for symbol, interval, months in KLINES_SPEC:
        for month in months:
            fname = f"{symbol}-{interval}-{month}.zip"
            dest  = RAW / "klines" / fname
            if dest.exists():
                print(f"  [skip existing] {fname}", flush=True)
                MANIFEST.append(audit_cached_file(dest, f"{KLINES_BASE}/{symbol}/{interval}/{fname}"))
                continue
            url  = f"{KLINES_BASE}/{symbol}/{interval}/{fname}"
            chk_url = url + ".CHECKSUM"
            data = download(url)
            dest.parent.mkdir(parents=True, exist_ok=True)
            ok = verify_checksum_file(data, chk_url, dest.with_name(fname + ".CHECKSUM"))
            save_and_record(dest, data, url, ok)
            time.sleep(0.5)


# ─────────────────────────── AggTrades ───────────────────────────────────────

def download_aggtrades():
    print("\n=== [2/3] Downloading AggTrades ===", flush=True)
    for symbol, months in AGTRADES_SPEC:
        for month in months:
            fname = f"{symbol}-aggTrades-{month}.zip"
            dest  = RAW / "aggTrades" / fname
            if dest.exists():
                print(f"  [skip existing] {fname}", flush=True)
                MANIFEST.append(audit_cached_file(dest, f"{TRADES_BASE}/{symbol}/{fname}"))
                continue
            url  = f"{TRADES_BASE}/{symbol}/{fname}"
            chk_url = url + ".CHECKSUM"
            data = download(url)
            dest.parent.mkdir(parents=True, exist_ok=True)
            ok = verify_checksum_file(data, chk_url, dest.with_name(fname + ".CHECKSUM"))
            save_and_record(dest, data, url, ok)
            time.sleep(0.5)


# ─────────────────────────── LOB Depth ───────────────────────────────────────

def download_depth():
    print("\n=== [3/3] Downloading LOB Depth Snapshots (1000 levels) ===", flush=True)
    for symbol in DEPTH_SYMBOLS:
        fname = f"{symbol}-depth-{DEPTH_LIMIT}.json"
        dest  = RAW / "depth_snapshots" / fname
        url   = f"{DEPTH_BASE}?symbol={symbol}&limit={DEPTH_LIMIT}"
        if dest.exists():
            MANIFEST.append(audit_cached_file(dest, url))
            continue
        data  = download(url)
        save_and_record(dest, data, url, False)
        time.sleep(0.3)


# ──────────────────────────── Manifest ───────────────────────────────────────

def write_manifest(output_dir: Path = OUT):
    manifest = {
        "schema": "machine-markets-gate24-acquisition-3",
        "recorded_at_utc": datetime.now(timezone.utc).isoformat(),
        "purpose": "Public market proxy inputs; execution calibration remains pending.",
        "provider": "Binance Public Data (data.binance.vision + data-api.binance.vision)",
        "license_note": "Public market data. Confirm current Binance terms before redistribution or publication.",
        "files": MANIFEST,
    }
    dest = output_dir / "data_acquisition_manifest.json"
    dest.parent.mkdir(parents=True, exist_ok=True)
    with dest.open("x") as handle:
        handle.write(json.dumps(manifest, indent=2) + "\n")
    print(f"\nManifest written: {dest}", flush=True)
    print(f"  Total files: {len(MANIFEST)}")
    total_bytes = sum(f.get("bytes", 0) for f in MANIFEST)
    print(f"  Total data:  {total_bytes/1e6:.1f} MB")


# ─────────────────────────────── Main ────────────────────────────────────────

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--offline", action="store_true")
    parser.add_argument("--output-dir", type=Path, default=OUT)
    args = parser.parse_args()
    if (args.output_dir / "data_acquisition_manifest.json").exists():
        parser.error("Refusing to overwrite existing evidence")
    print("=" * 70)
    print("MACHINE MARKETS — Gate 2–4 Public Data Acquisition")
    print("Source: data.binance.vision (public, no authentication required)")
    print("=" * 70)
    if args.offline:
        for path in sorted(RAW.rglob("*")):
            if path.is_file() and path.suffix in {".zip", ".json"}:
                MANIFEST.append(audit_cached_file(path))
    else:
        download_klines()
        download_aggtrades()
        download_depth()
    write_manifest(args.output_dir)
    print("\n✓ ACQUISITION COMPLETE")
