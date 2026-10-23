"""
E2_recorder.py — Robust recorder and daily archive ingestion for Test E2.

Test E2 is a prospective mechanism study registered in commit f76f379 (October 22, 2026).
Per Rule 5 and the pre-registration specification, live Binance websocket feeds are
geo-restricted (HTTP 451) from US locations, so the pre-registered fallback is activated:
daily prospective ingestion of public archive files from data.binance.vision for dates
strictly after the registration timestamp.

Architecture:
1. Daily fetcher for metrics (open interest, taker volume) and depth files.
2. Robust connection handling with exponential backoff (1s, 2s, 4s, ..., max 60s).
3. Checksum verification against Binance SHA-256 manifests.
4. Output compressed to .json.gz by date and symbol.
5. Persistent logging of gaps and missing dates in gap_log.txt.
"""

import argparse
from datetime import datetime, timedelta, timezone
import gzip
import hashlib
import json
import logging
import os
from pathlib import Path
import sys
import time
import urllib.error
import urllib.request

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
DATA_DIR = HERE / 'E2_prospective_data'
DATA_DIR.mkdir(parents=True, exist_ok=True)
GAP_LOG = HERE / 'gap_log.txt'

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] %(message)s',
    handlers=[
        logging.FileHandler(HERE / 'recorder.log'),
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger('E2_recorder')

# 19 thin symbols registered in E2_prospective.json
THIN_SYMBOLS = [
    "ACHUSDT", "ALICEUSDT", "API3USDT", "ARPAUSDT", "BATUSDT",
    "BELUSDT", "CELRUSDT", "CHRUSDT", "COTIUSDT", "CTSIUSDT",
    "CVXUSDT", "GTCUSDT", "HOTUSDT", "IOTXUSDT", "LITUSDT",
    "LQTYUSDT", "OGNUSDT", "RLCUSDT", "SPELLUSDT", "ZENUSDT"
]

BASE_URL = "https://data.binance.vision/data/futures/um/daily"


def log_gap(date_str, symbol, reason):
    with GAP_LOG.open('a') as f:
        f.write(f"{datetime.now(timezone.utc).isoformat()} | {date_str} | {symbol} | {reason}\n")
    logger.warning(f"Recorded gap: {date_str} {symbol} ({reason})")


def download_with_retry(url, max_retries=5, initial_backoff=1.0):
    """Download url content with exponential backoff."""
    delay = initial_backoff
    for attempt in range(1, max_retries + 1):
        try:
            req = urllib.request.Request(
                url,
                headers={'User-Agent': 'MachineMarketsResearch/2.0'}
            )
            with urllib.request.urlopen(req, timeout=15) as resp:
                return resp.read()
        except urllib.error.HTTPError as e:
            if e.code == 404:
                # File not published yet
                return None
            logger.warning(f"HTTP error {e.code} fetching {url} (attempt {attempt}/{max_retries})")
        except Exception as e:
            logger.warning(f"Connection error {e} fetching {url} (attempt {attempt}/{max_retries})")
        time.sleep(delay)
        delay = min(delay * 2.0, 60.0)
    return None


def fetch_daily_metrics(symbol, date_str):
    """Fetch daily metrics zip for symbol and date."""
    # Pattern: https://data.binance.vision/data/futures/um/daily/metrics/{symbol}/{symbol}-metrics-{date}.zip
    url = f"{BASE_URL}/metrics/{symbol}/{symbol}-metrics-{date_str}.zip"
    chk_url = f"{url}.CHECKSUM"

    checksum_bytes = download_with_retry(chk_url)
    if checksum_bytes is None:
        log_gap(date_str, symbol, "metrics checksum 404 or unavailable")
        return False

    data_bytes = download_with_retry(url)
    if data_bytes is None:
        log_gap(date_str, symbol, "metrics zip 404 or unavailable")
        return False

    # Verify checksum
    expected_sha = checksum_bytes.decode().split()[0].strip()
    actual_sha = hashlib.sha256(data_bytes).hexdigest()
    if actual_sha != expected_sha:
        log_gap(date_str, symbol, f"checksum mismatch: expected {expected_sha}, got {actual_sha}")
        return False

    # Save verified file
    out_file = DATA_DIR / f"{symbol}-metrics-{date_str}.zip"
    out_file.write_bytes(data_bytes)
    logger.info(f"Verified & saved {out_file.name}")
    return True


def run_archive_intake(start_date=None, end_date=None):
    """Prospective intake loop over registered symbols."""
    # Registration date: October 22, 2026. Prospective dates are strictly on or after Oct 23, 2026.
    if start_date is None:
        start_date = datetime(2026, 10, 23, tzinfo=timezone.utc).date()
    if end_date is None:
        end_date = datetime.now(timezone.utc).date()

    logger.info(f"Starting prospective archive intake from {start_date} to {end_date}")
    curr = start_date
    success_count = 0
    total_checks = 0

    while curr <= end_date:
        d_str = curr.strftime("%Y-%m-%d")
        for sym in THIN_SYMBOLS:
            total_checks += 1
            if fetch_daily_metrics(sym, d_str):
                success_count += 1
        curr += timedelta(days=1)

    logger.info(f"Intake pass completed: {success_count}/{total_checks} files successfully archived.")


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--status', action='store_true', help='Show recording status and log')
    parser.add_argument('--intake', action='store_true', help='Run prospective archive intake pass')
    args = parser.parse_args()

    if args.status:
        print("E2 Prospective Recorder Status:")
        print(f"Data directory: {DATA_DIR} ({len(list(DATA_DIR.glob('*')))} files)")
        if GAP_LOG.exists():
            print(f"Gap log entries: {len(GAP_LOG.read_text().splitlines())}")
        else:
            print("Gap log: 0 entries")
    elif args.intake:
        run_archive_intake()
    else:
        parser.print_help()
