"""Regression tests for the portable checksum verifier, not scientific validation."""
import hashlib
from pathlib import Path
from verify_master import verify_manifest


def make_package(tmp_path: Path) -> Path:
    (tmp_path / 'data').mkdir()
    f = tmp_path / 'data' / 'example.txt'
    f.write_bytes(b'example scientific record\n')
    digest = hashlib.sha256(f.read_bytes()).hexdigest()
    (tmp_path / 'SHA256SUMS.txt').write_text(f'{digest}  data/example.txt\n')
    return tmp_path


def test_valid_file_matches(tmp_path):
    result = verify_manifest(make_package(tmp_path))
    assert result['passed'] and result['verified_files'] == 1


def test_changed_file_rejected(tmp_path):
    root = make_package(tmp_path)
    (root / 'data/example.txt').write_text('changed')
    result = verify_manifest(root)
    assert not result['passed'] and result['errors'][0]['kind'] == 'hash_mismatch'


def test_missing_file_rejected(tmp_path):
    root = make_package(tmp_path)
    (root / 'data/example.txt').unlink()
    result = verify_manifest(root)
    assert not result['passed'] and result['errors'][0]['kind'] == 'missing'


def test_path_escape_rejected(tmp_path):
    (tmp_path / 'SHA256SUMS.txt').write_text('0' * 64 + '  ../outside.txt\n')
    result = verify_manifest(tmp_path)
    assert not result['passed'] and result['errors'][0]['kind'] == 'unsafe_path'


def test_bad_line_rejected(tmp_path):
    (tmp_path / 'SHA256SUMS.txt').write_text('invalid checksum entry\n')
    result = verify_manifest(tmp_path)
    assert not result['passed'] and result['errors'][0]['kind'] == 'malformed_entry'


def test_unlisted_file_reported(tmp_path):
    root = make_package(tmp_path)
    (root / 'new_result.txt').write_text('new result')
    result = verify_manifest(root)
    assert result['passed'] and result['unlisted_files'] == ['new_result.txt']
