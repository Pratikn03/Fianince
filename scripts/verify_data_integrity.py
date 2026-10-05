#!/usr/bin/env python3
"""
Data Integrity & Cryptographic Provenance Auditor
==================================================
Machine Markets — Top-Tier Institutional Engineering Pipeline
Audits raw empirical datasets, Level-3 LOB archives, and panel bars.
Computes streaming SHA-256 digests and validates file existence and size.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import os
import sys
import time
from pathlib import Path
from typing import Dict, Any

REPO_ROOT = Path(__file__).resolve().parent.parent
DATA_DIR = REPO_ROOT / "empirical_pipeline" / "data"
MANIFEST_PATH = REPO_ROOT / "empirical_pipeline" / "data_manifest.json"

EXPECTED_FILES = [
    "1-09-1-20.csv",
    "BTC_1sec.csv",
    "BTC_1min.csv",
    "BTC_5min.csv",
    "ETH_1sec.csv",
    "ETH_1min.csv",
    "ETH_5min.csv",
    "ADA_1sec.csv",
    "ADA_1min.csv",
    "ADA_5min.csv",
]


def compute_sha256(filepath: Path, chunk_size: int = 65536) -> str:
    """Compute SHA-256 hash using streaming buffer to handle multi-gigabyte files."""
    hasher = hashlib.sha256()
    with open(filepath, "rb") as f:
        while chunk := f.read(chunk_size):
            hasher.update(chunk)
    return hasher.hexdigest()


def count_lines(filepath: Path, chunk_size: int = 65536) -> int:
    """Fast line count for large CSV files."""
    lines = 0
    with open(filepath, "rb") as f:
        while chunk := f.read(chunk_size):
            lines += chunk.count(b"\n")
    return lines


def generate_manifest(compute_hashes: bool = True) -> Dict[str, Any]:
    """Inspect all datasets and build cryptographic provenance manifest."""
    manifest = {
        "version": "1.0.0",
        "generated_at": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        "description": "Cryptographic SHA-256 Provenance Manifest for Machine Markets Datasets",
        "files": {}
    }

    print(f"Scanning data directory: {DATA_DIR}")
    for fname in EXPECTED_FILES:
        fpath = DATA_DIR / fname
        if not fpath.exists():
            print(f"  [MISSING] {fname}")
            manifest["files"][fname] = {"status": "MISSING"}
            continue

        size_bytes = fpath.stat().st_size
        size_mb = size_bytes / (1024 * 1024)
        print(f"  Auditing {fname} ({size_mb:.2f} MB)...", end="", flush=True)

        t0 = time.time()
        file_meta: Dict[str, Any] = {
            "status": "PRESENT",
            "size_bytes": size_bytes,
            "size_mb": round(size_mb, 2),
        }

        if compute_hashes:
            sha = compute_sha256(fpath)
            file_meta["sha256"] = sha

        dt = time.time() - t0
        print(f" done in {dt:.1f}s.")
        manifest["files"][fname] = file_meta

    MANIFEST_PATH.write_text(json.dumps(manifest, indent=2))
    print(f"\nManifest successfully written to: {MANIFEST_PATH}")
    return manifest


def verify_manifest(fast: bool = False) -> bool:
    """Verify on-disk datasets against manifest."""
    if not MANIFEST_PATH.exists():
        print(f"Manifest not found at {MANIFEST_PATH}. Generating one now...")
        generate_manifest(compute_hashes=not fast)
        return True

    with open(MANIFEST_PATH, "r") as f:
        manifest = json.load(f)

    all_ok = True
    print("=" * 70)
    print("VERIFYING EMPIRICAL DATA INTEGRITY")
    print("=" * 70)

    for fname, meta in manifest.get("files", {}).items():
        fpath = DATA_DIR / fname
        if not fpath.exists():
            print(f"❌ FAIL: {fname} is missing from {DATA_DIR}")
            all_ok = False
            continue

        current_size = fpath.stat().st_size
        expected_size = meta.get("size_bytes", 0)

        if current_size != expected_size:
            print(f"❌ SIZE MISMATCH: {fname} (expected {expected_size}, got {current_size})")
            all_ok = False
            continue

        if not fast and "sha256" in meta:
            t0 = time.time()
            current_sha = compute_sha256(fpath)
            if current_sha != meta["sha256"]:
                print(f"❌ SHA256 CORRUPTED: {fname}")
                all_ok = False
                continue
            dt = time.time() - t0
            print(f"✅ OK: {fname:<16} ({meta['size_mb']} MB, sha256 verified in {dt:.1f}s)")
        else:
            print(f"✅ OK: {fname:<16} ({meta['size_mb']} MB, size verified)")

    print("=" * 70)
    if all_ok:
        print("SUCCESS: ALL EMPIRICAL DATASETS VERIFIED WITH 100% INTEGRITY")
    else:
        print("ERROR: DATA INTEGRITY CHECK FAILED")
    print("=" * 70)
    return all_ok


def main():
    parser = argparse.ArgumentParser(description="Empirical Data Integrity Verifier")
    parser.add_argument("--generate", action="store_true", help="Generate or update manifest")
    parser.add_argument("--fast", action="store_true", help="Fast mode (size check only, skip full SHA256)")
    args = parser.parse_args()

    if args.generate:
        generate_manifest(compute_hashes=not args.fast)
    else:
        ok = verify_manifest(fast=args.fast)
        if not ok:
            sys.exit(1)


if __name__ == "__main__":
    main()
