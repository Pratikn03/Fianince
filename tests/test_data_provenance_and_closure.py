"""Test data provenance integrity and exact interval closure.

Verifies SHA-256 checksums for empirical data files and validates that
duplicated-render zeroing restores exact 1-minute interval closure.
"""
from __future__ import annotations

import hashlib
from pathlib import Path

import numpy as np
import pandas as pd
import pytest

DATA_DIR = Path(__file__).resolve().parents[1] / "empirical_pipeline" / "data"

CHECKSUMS = {
    "BTC_1sec.csv": "a6b46071b1804e6181a1fb3eca9df70c13afa58195f18cb469d9682b86a0c85b",
    "ETH_1sec.csv": "908f10a56bb265a56d9c913ab72ad363c8016aa81870eb467c4807885f17dcac",
    "ADA_1sec.csv": "ec8fbc1925f14c589f717f3cf497584ad56384e0daeba34c541c33f583c998aa",
    "BTC_1min.csv": "1a4bf5d19f0f9b41f93a7fadacb44f015f8f7eb3212995b77bd70182d99afa93",
    "ETH_1min.csv": "c2a26ac19017b7d205e1f4a51adfc68112f9509e11f9f65130844bf1fe33fe83",
    "ADA_1min.csv": "d1126b9d06a7eb1a452016c2c634f04afd5017f78ed70f3ff7b0135df81d36b3",
    "1-09-1-20.csv": "5d3f14a2d252a884e3c9b81a6f3767c7161296ecc8fdd1280c7d46a1cea19847",
}


@pytest.mark.parametrize("fname, expected_hash", CHECKSUMS.items())
def test_data_sha256(fname: str, expected_hash: str):
    fpath = DATA_DIR / fname
    if not fpath.exists():
        pytest.skip(f"Data file {fname} not present in checkout")
    h = hashlib.sha256()
    with open(fpath, "rb") as f:
        while chunk := f.read(1024 * 1024):
            h.update(chunk)
    assert h.hexdigest() == expected_hash, f"Checksum mismatch for {fname}"


def test_interval_closure_first_100_minutes():
    """Verify that summing 1-sec flow over (T-60, T] matches 1-min file exactly when deduped."""
    if not (DATA_DIR / "BTC_1sec.csv").exists() or not (DATA_DIR / "BTC_1min.csv").exists():
        pytest.skip("BTC_1sec.csv or BTC_1min.csv not present in checkout")
    s = pd.read_csv(DATA_DIR / "BTC_1sec.csv", nrows=10000,
                    usecols=["system_time", "midpoint", "spread", "buys", "sells",
                             "bids_notional_0", "asks_notional_0", "bids_distance_0", "asks_distance_0"])
    m = pd.read_csv(DATA_DIR / "BTC_1min.csv", nrows=100, usecols=["system_time", "buys", "sells"])

    keycols = ["midpoint", "spread", "buys", "sells", "bids_notional_0", "asks_notional_0",
               "bids_distance_0", "asks_distance_0"]
    same = (s[keycols].shift(1) == s[keycols]).all(axis=1)

    ts_s = pd.to_datetime(s["system_time"], utc=True)
    sec_s = ((ts_s - pd.Timestamp("1970-01-01", tz="UTC")) // pd.Timedelta("1s")).to_numpy()
    flow_dedup = np.where(same, 0.0, s["buys"].to_numpy())

    ts_m = pd.to_datetime(m["system_time"], utc=True)
    sec_m = ((ts_m - pd.Timestamp("1970-01-01", tz="UTC")) // pd.Timedelta("1s")).to_numpy()

    pos = pd.Series(np.arange(len(sec_s)), index=sec_s)
    pos = pos[~pos.index.duplicated()]
    cs = np.concatenate([[0.0], np.cumsum(flow_dedup)])

    exact_matches = 0
    tested = 0
    for T, expected_buy in zip(sec_m[2:50], m["buys"].to_numpy()[2:50]):
        if (T - 59) in pos.index and T in pos.index:
            i0, i1 = pos[T - 59], pos[T]
            if i1 - i0 == 59:
                tot = cs[i1 + 1] - cs[i0]
                if expected_buy > 0:
                    tested += 1
                    if abs(tot - expected_buy) / expected_buy < 1e-6:
                        exact_matches += 1

    assert tested >= 20, f"Insufficient contiguous blocks tested: {tested}"
    assert exact_matches == tested, f"Deduped flow did not match 1-min file: {exact_matches}/{tested}"
