"""Prospective sampled-liquidation recorder. Recording requires a pushed spec.

--check-access performs a headers-only WebSocket handshake and closes without
reading or saving market messages. It is an operational accessibility check.
No proxy, historical backfill or automatic regional fallback is used.
Recording needs websockets==15.0.1; it is deliberately not started by this file.
"""
import argparse
import asyncio
from datetime import datetime, timezone
import gzip
import hashlib
import importlib.metadata
import json
from pathlib import Path
import secrets
import shutil
import socket
import ssl
import subprocess
import time
import base64

ROOT = Path(__file__).resolve().parents[2]
HOST = 'fstream.binance.com'
STREAM_PATH = '/market/ws/!forceOrder@arr'
ENDPOINT = 'wss://'+HOST+STREAM_PATH


def utc():
    return datetime.now(timezone.utc).isoformat()


def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def check_access(output):
    # Read HTTP headers one byte at a time: do not open a market-message set.
    key = base64.b64encode(secrets.token_bytes(16)).decode()
    request = (f'GET {STREAM_PATH} HTTP/1.1\r\nHost: {HOST}\r\n'
               'Upgrade: websocket\r\nConnection: Upgrade\r\n'
               f'Sec-WebSocket-Key: {key}\r\nSec-WebSocket-Version: 13\r\n\r\n')
    result = {'checked_utc':utc(), 'endpoint':ENDPOINT, 'probe_source_sha256':sha(__file__), 'market_messages_read':0,
              'proxy_used':False, 'interpretation':'Operational reachability only; not permission to trade and not study evidence.'}
    try:
        with socket.create_connection((HOST,443),timeout=12) as raw:
            with ssl.create_default_context().wrap_socket(raw,server_hostname=HOST) as s:
                s.sendall(request.encode('ascii')); headers = bytearray()
                while not headers.endswith(b'\r\n\r\n') and len(headers)<16384:
                    b = s.recv(1)
                    if not b: break
                    headers.extend(b)
        status = bytes(headers).split(b'\r\n',1)[0].decode('ascii',errors='replace')
        result.update(http_status_line=status, handshake_accepted=' 101 ' in status)
    except (OSError,ssl.SSLError) as e:
        result.update(handshake_accepted=False, error=type(e).__name__+': '+str(e))
    output.parent.mkdir(parents=True,exist_ok=True)
    output.write_text(json.dumps(result,indent=2)+'\n')
    print(json.dumps(result,indent=2))
    return 0 if result['handshake_accepted'] else 1


class DailyWriter:
    def __init__(self, output):
        self.output = Path(output); self.output.mkdir(parents=True,exist_ok=True)
        self.day = None; self.file = None; self.path = None; self.rows = 0

    def log(self, event):
        with (self.output/'connections_and_gaps.jsonl').open('a') as f:
            f.write(json.dumps({'utc':utc(),**event})+'\n')

    def close(self):
        if self.file is not None:
            self.file.close()
            with (self.output/'chunks_manifest.jsonl').open('a') as f:
                f.write(json.dumps({'path':str(self.path.relative_to(self.output)),
                                    'sha256':sha(self.path),'rows':self.rows})+'\n')
            self.file = None

    def write(self, raw, received):
        day = received[:10]
        if day != self.day or self.file is None:
            self.close(); self.day = day
            directory = self.output/day; directory.mkdir(exist_ok=True)
            self.path = directory/('forceOrder-'+secrets.token_hex(8)+'.jsonl.gz')
            self.file = gzip.open(self.path,'xt',encoding='utf-8'); self.rows = 0
        payload = json.loads(raw)  # retain the exchange payload; no zero imputation
        self.file.write(json.dumps({'received_utc':received,'payload':payload})+'\n')
        self.file.flush(); self.rows += 1


def registration_gate(spec_path, counter_path):
    spec_path = spec_path.resolve(); counter_path = counter_path.resolve()
    spec = json.loads(spec_path.read_text())
    assert spec['mode'] == 'prospective_sampled_liquidations'
    for key in ('hypotheses','data','dates','primaries','pass_rules','correction','code_version'):
        assert key in spec, 'incomplete registration: '+key
    assert spec['minimum_recording_months'] >= 3
    assert spec['endpoint'] == ENDPOINT, 'register the documented routed endpoint'
    assert sha(__file__) == spec['recorder_sha256'], 'recorder changed after registration'
    assert sha(spec_path) == spec_path.with_suffix('.sha256').read_text().strip()
    relative = spec_path.relative_to(ROOT)
    assert spec_path.read_bytes() == subprocess.check_output(['git','show',f'HEAD:{relative}'],cwd=ROOT)
    subprocess.run(['git','fetch','origin',spec['remote_branch']],cwd=ROOT,check=True,capture_output=True)
    commit = subprocess.check_output(['git','log','-1','--format=%H','--',str(relative)],cwd=ROOT,text=True).strip()
    subprocess.run(['git','merge-base','--is-ancestor',commit,'origin/'+spec['remote_branch']],cwd=ROOT,check=True)
    counter = json.loads(counter_path.read_text())
    if counter['opens'] == 0:
        counter_path.write_text(json.dumps({'opens':1,'started_utc':utc(),
                                           'spec_sha256':sha(spec_path),'registration_commit':commit},indent=2)+'\n')
    else:
        assert counter['opens'] == 1 and counter['spec_sha256'] == sha(spec_path), 'different or reopened study'
    return spec


async def record_stream(args):
    # Import only on a deliberately authorized recording run.
    if importlib.metadata.version('websockets') != '15.0.1':
        raise RuntimeError('Use the pinned recorder requirements in a dedicated environment')
    from websockets.asyncio.client import connect
    from websockets.exceptions import InvalidStatus
    args.output.mkdir(parents=True,exist_ok=True)
    if shutil.disk_usage(args.output).free < 2*1024**3:
        raise RuntimeError('Recording requires at least 2 GiB free')
    spec = registration_gate(args.spec,args.counter)
    assert spec['mode'] == 'prospective_sampled_liquidations'
    writer = DailyWriter(args.output)
    deadline = time.monotonic()+args.hours*3600
    disconnected = utc(); delay = 1
    try:
        while time.monotonic()<deadline:
            had_connection = False
            try:
                async with connect(ENDPOINT,proxy=None,open_timeout=12,close_timeout=10,
                                   ping_interval=20,ping_timeout=20,max_size=2**20) as ws:
                    had_connection = True
                    writer.log({'event':'connected','disconnected_since':disconnected,
                                'gap_end_utc':utc(),'ping_detection_uncertainty_seconds':40})
                    delay = 1
                    while time.monotonic()<deadline:
                        if shutil.disk_usage(args.output).free < 2*1024**3:
                            raise RuntimeError('Storage guard: recording stopped')
                        try:
                            message = await asyncio.wait_for(ws.recv(),timeout=30)
                        except asyncio.TimeoutError:
                            writer.log({'event':'connected_no_message','note':'No message is not a zero-liquidation observation.'})
                            continue
                        writer.write(message,utc())
            except RuntimeError:
                raise
            except InvalidStatus as e:
                if e.response.status_code in (401,403,451):
                    writer.log({'event':'access_denied','http_status':e.response.status_code})
                    raise RuntimeError('Access denied: stop and use a separately registered lawful fallback') from e
                writer.log({'event':'http_rejected','http_status':e.response.status_code})
                await asyncio.sleep(min(60,max(0,deadline-time.monotonic())))
            except Exception as e:
                if had_connection: disconnected = utc()
                writer.close()
                writer.log({'event':'disconnected','error_type':type(e).__name__,
                            'retry_seconds':delay})
                await asyncio.sleep(min(delay,max(0,deadline-time.monotonic())))
                delay = min(delay*2,60)
    finally:
        writer.close(); writer.log({'event':'recorder_stopped'})


async def record(args):
    lock = args.counter.with_suffix('.recording.lock')
    # One collector per registered counter, even across different output paths.
    with lock.open('x'):
        try:
            await record_stream(args)
        finally:
            lock.unlink(missing_ok=True)


def main():
    p = argparse.ArgumentParser(description=__doc__)
    modes = p.add_mutually_exclusive_group(required=True)
    modes.add_argument('--check-access',type=Path)
    modes.add_argument('--record',action='store_true')
    p.add_argument('--spec',type=Path);p.add_argument('--counter',type=Path)
    p.add_argument('--output',type=Path);p.add_argument('--hours',type=float,default=24)
    a = p.parse_args()
    if a.check_access and not a.record: return check_access(a.check_access)
    if not (a.record and a.spec and a.counter and a.output and a.hours>0):
        p.error('recording needs --record --spec --counter --output and positive --hours')
    asyncio.run(record(a)); return 0


if __name__=='__main__':
    raise SystemExit(main())
