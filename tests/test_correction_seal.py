import hashlib
import json
import pytest
from research_extension.evidence_repair.check_evidence import verify_seal


def test_correction_seal_detects_drift(tmp_path):
    source = tmp_path / 'source.py'
    source.write_text('original')
    seal = tmp_path / 'seal.json'
    seal.write_text(json.dumps({'scope': 'test', 'sha256': {
        'source.py': hashlib.sha256(source.read_bytes()).hexdigest()}}))
    assert verify_seal(tmp_path, seal)['files_verified'] == 1
    source.write_text('changed')
    with pytest.raises(AssertionError, match='Hash mismatch'):
        verify_seal(tmp_path, seal)


def test_correction_seal_cannot_pass_with_no_files(tmp_path):
    seal = tmp_path / 'seal.json'
    seal.write_text(json.dumps({'scope': 'test', 'sha256': {}}))
    with pytest.raises(AssertionError, match='Empty'):
        verify_seal(tmp_path, seal)
