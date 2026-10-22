"""Software I/O checks only: synthetic fixtures, never a market-data test."""
import gzip
import hashlib
import importlib.util
import json
from pathlib import Path
import pytest

PATH = Path(__file__).resolve().parents[1]/'thesis/evidence/E2_recorder.py'
spec = importlib.util.spec_from_file_location('thesis_e2_recorder', PATH)
module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(module)


def test_daily_rotation_closes_checksummed_chunks(tmp_path):
    writer = module.DailyWriter(tmp_path)
    writer.write('{"synthetic_fixture":true}', '2026-01-01T23:59:59+00:00')
    writer.write('{"synthetic_fixture":true}', '2026-01-02T00:00:00+00:00')
    writer.close()
    chunks = [json.loads(x) for x in (tmp_path/'chunks_manifest.jsonl').read_text().splitlines()]
    assert len(chunks) == 2
    assert {Path(x['path']).parts[0] for x in chunks} == {'2026-01-01','2026-01-02'}
    for row in chunks:
        path = tmp_path/row['path']
        assert hashlib.sha256(path.read_bytes()).hexdigest() == row['sha256']
        with gzip.open(path,'rt') as f:
            records = [json.loads(x) for x in f]
        assert len(records) == row['rows'] == 1
        assert records[0]['payload']['synthetic_fixture'] is True


def test_reconnect_chunks_do_not_overwrite_prior_data(tmp_path):
    for _ in range(2):
        writer = module.DailyWriter(tmp_path)
        writer.write('{"synthetic_fixture":true}', '2026-01-01T12:00:00+00:00')
        writer.close()
    chunks = [json.loads(x) for x in (tmp_path/'chunks_manifest.jsonl').read_text().splitlines()]
    assert len({x['path'] for x in chunks}) == 2
    assert all((tmp_path/x['path']).is_file() for x in chunks)


def test_bad_payload_is_not_a_zero_liquidation_observation(tmp_path):
    writer = module.DailyWriter(tmp_path)
    with pytest.raises(json.JSONDecodeError):
        writer.write('not-json', '2026-01-01T12:00:00+00:00')
    writer.close()
    rows = [json.loads(x) for x in (tmp_path/'chunks_manifest.jsonl').read_text().splitlines()]
    assert rows[0]['rows'] == 0
