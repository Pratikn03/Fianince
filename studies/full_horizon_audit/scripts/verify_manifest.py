#!/usr/bin/env python3
"""Verify delivered file bytes against the bundled SHA-256 manifest."""
from pathlib import Path
import hashlib,json
ROOT=Path(__file__).resolve().parents[1]
count=0
for line in (ROOT/'SHA256SUMS.txt').read_text().splitlines():
 digest,relative=line.split('  ',1);p=(ROOT/relative).resolve()
 if not p.is_relative_to(ROOT.resolve()):raise ValueError('Manifest path escapes package')
 actual=hashlib.sha256(p.read_bytes()).hexdigest()
 if actual!=digest:raise SystemExit('Hash mismatch: '+relative)
 count+=1
print(json.dumps({'checked_files':count,'all_hashes_match':True}))
