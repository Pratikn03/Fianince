"""Acquire exchange public inputs, never label them as private account records."""
from pathlib import Path
import urllib.request
import hashlib
import json
import zipfile
import datetime

HERE = Path(__file__).resolve().parent
DATA = Path('/Volumes/T9/machine_markets_data/account_calibration_20261009')
BASE = 'https://data.binance.vision/data/futures/um/monthly/'
SPECS = [('fundingRate', 'BTCUSDT/BTCUSDT-fundingRate-2023-01.zip'),
         ('markPriceKlines', 'BTCUSDT/1m/BTCUSDT-1m-2023-01.zip'),
         ('indexPriceKlines', 'BTCUSDT/1m/BTCUSDT-1m-2023-01.zip')]

def fetch(url):
    req = urllib.request.Request(url, headers={'User-Agent': 'MachineMarketsResearch/1.0'})
    with urllib.request.urlopen(req, timeout=30) as r:
        return r.read()

def main():
    DATA.mkdir(parents=True, exist_ok=True)
    records = []
    for kind, key in SPECS:
        url = BASE + kind + '/' + key
        path = DATA / (kind + '_' + Path(key).name)
        checksum = fetch(url + '.CHECKSUM')
        digest = checksum.decode().split()[0]
        if not path.exists():
            payload = fetch(url)
            assert hashlib.sha256(payload).hexdigest() == digest
            path.write_bytes(payload)
        assert hashlib.sha256(path.read_bytes()).hexdigest() == digest
        (DATA / (path.name + '.CHECKSUM')).write_bytes(checksum)
        members = []
        with zipfile.ZipFile(path) as z:
            assert z.testzip() is None
            for name in z.namelist():
                payload = z.read(name)
                members.append(dict(name=name, bytes=len(payload), sha256=hashlib.sha256(payload).hexdigest()))
        records.append(dict(kind=kind, url=url, checksum_url=url+'.CHECKSUM', path=str(path),
            bytes=path.stat().st_size, sha256=digest, checksum_verified=True, zip_crc_verified=True, members=members))
        print(kind, path.stat().st_size, 'CHECKSUM_AND_CRC_PASS', flush=True)
    receipt = dict(retrieved_at_utc=datetime.datetime.now(datetime.timezone.utc).isoformat(),
        target='Provider-declared Binance BTCUSDT USD-M perpetual; January9-20,2023', files=records,
        private_account_records=False, scope='Public funding/mark/index series; no fills, positions, wallet or tier authentication.')
    (HERE / 'public_account_input_acquisition.json').write_text(json.dumps(receipt, indent=2)+'\n')

if __name__ == '__main__':
    main()
