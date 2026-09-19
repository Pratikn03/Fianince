#!/usr/bin/env python3
"""Verify the release's file-integrity manifest using only the standard library."""
import hashlib
from pathlib import Path
import sys
ROOT=Path(__file__).resolve().parents[1]

def main():
    manifest=ROOT/'MANIFEST.sha256'
    if not manifest.exists():
        raise SystemExit('MANIFEST.sha256 is missing')
    bad=[];n=0
    for line in manifest.read_text().splitlines():
        digest,relative=line.split('  ',1)
        path=(ROOT/relative).resolve()
        if not path.is_relative_to(ROOT.resolve()):
            raise SystemExit('Manifest path escapes release root')
        if not path.is_file() or hashlib.sha256(path.read_bytes()).hexdigest()!=digest:
            bad.append(relative)
        n+=1
    print(f'{"FAIL" if bad else "PASS"}: {n} manifest entries checked')
    for name in bad:print(name)
    return bool(bad)

if __name__=='__main__':sys.exit(main())
