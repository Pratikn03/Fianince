"""Refresh source mirrors and generated TeX, without changing historical PDFs.

Authoritative input: ceiling_suite/papers/paper{1,2}/p{1,2}_*.tex.
Run from any directory. Rebuild PDFs separately after reviewing the source diff.
"""
from pathlib import Path
import shutil
import subprocess
import sys

ROOT=Path(__file__).resolve().parents[2]
ORDER={1:['front','ident','account','mixture','disclosure','empirics','appendix'],
       2:['front','theory1','t6','infosafety','guard','disclosure','equil','evidence','thin','istests','close','appendix']}
for num,parts in ORDER.items():
    canonical=ROOT/f'ceiling_suite/papers/paper{num}'
    mirror=ROOT/f'ceiling_suite/paper{num}'
    for name in canonical.glob(f'p{num}_*.tex'):
        shutil.copyfile(name,mirror/name.name)
    assembled=''.join((canonical/f'p{num}_{part}.tex').read_text() for part in parts)
    for folder in [canonical,mirror]:(folder/f'paper{num}.tex').write_text(assembled)
subprocess.run([sys.executable,str(ROOT/'ceiling_suite/papers/versions/build_versions.py'),'--source-only'],check=True)
subprocess.run([sys.executable,str(ROOT/'thesis/make_chapters.py')],check=True)
print('Refreshed modular mirrors, working/journal TeX and thesis chapters; PDFs remain snapshots.')
