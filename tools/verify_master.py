#!/usr/bin/env python3
"""Verify every distributed file against SHA256SUMS.txt (standard library only).

Hash agreement detects accidental changes; it does not authenticate an untrusted
issuer, establish scientific validity, or replace outside replication.
"""
from __future__ import annotations
import argparse
import hashlib
import json
from pathlib import Path, PurePosixPath
import re
import sys


def file_sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open('rb') as f:
        for block in iter(lambda: f.read(1024 * 1024), b''):
            h.update(block)
    return h.hexdigest()


def verify_manifest(root: Path) -> dict:
    root = Path(root).resolve()
    errors: list[dict] = []
    tracked: set[str] = set()
    verified = 0
    manifest = root / 'SHA256SUMS.txt'
    if not manifest.is_file():
        return {'passed': False, 'verified_files': 0, 'errors': [
            {'kind': 'missing_manifest', 'path': 'SHA256SUMS.txt'}], 'unlisted_files': []}
    for number, line in enumerate(manifest.read_text(encoding='utf-8').splitlines(), 1):
        if not line.strip():
            continue
        match = re.fullmatch(r'([0-9a-fA-F]{64})  (.+)', line)
        if match is None:
            errors.append({'kind': 'malformed_entry', 'line': number})
            continue
        expected, relative = match.groups()
        p = PurePosixPath(relative)
        if p.is_absolute() or '..' in p.parts or '\\' in relative or ':' in relative:
            errors.append({'kind': 'unsafe_path', 'path': relative})
            continue
        path = root.joinpath(*p.parts)
        if not path.resolve().is_relative_to(root) or path.is_symlink():
            errors.append({'kind': 'unsafe_path', 'path': relative})
            continue
        if relative in tracked:
            errors.append({'kind': 'duplicate_entry', 'path': relative})
            continue
        tracked.add(relative)
        if not path.is_file():
            errors.append({'kind': 'missing', 'path': relative})
            continue
        actual = file_sha256(path)
        if actual != expected.lower():
            errors.append({'kind': 'hash_mismatch', 'path': relative,
                           'expected': expected.lower(), 'actual': actual})
        else:
            verified += 1
    existing = {p.relative_to(root).as_posix() for p in root.rglob('*') if p.is_file()}
    unlisted = sorted(existing - tracked - {'SHA256SUMS.txt'})
    return {'passed': not errors, 'verified_files': verified,
            'errors': errors, 'unlisted_files': unlisted}


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--root', type=Path, default=Path(__file__).resolve().parents[1])
    parser.add_argument('--strict', action='store_true', help='Also fail for unlisted files.')
    args = parser.parse_args()
    result = verify_manifest(args.root)
    if args.strict and result['unlisted_files']:
        result['passed'] = False
    print(json.dumps(result, indent=2))
    return 0 if result['passed'] else 1


if __name__ == '__main__':
    sys.exit(main())
