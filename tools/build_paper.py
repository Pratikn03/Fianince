#!/usr/bin/env python3
"""Compile the self-contained master manuscript without overwriting reference files.

Requires pdflatex with the packages listed in paper/README.md. No shell escape,
network requests, bibliography downloads or external figures are used.
"""
from __future__ import annotations
import argparse
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--root', type=Path, default=Path(__file__).resolve().parents[1])
    parser.add_argument('--output', type=Path, required=True, help='New PDF path; must not already exist.')
    args = parser.parse_args()
    source = args.root.resolve()/'paper'/'Machine_Markets_Final_Integrated_Paper.tex'
    destination = args.output.resolve()
    if destination.exists():
        parser.error('Output exists. Choose a new output path to protect the release.')
    compiler = shutil.which('pdflatex')
    if not compiler:
        parser.error('pdflatex not found. The prebuilt PDF is already in paper/.')
    if not source.is_file():
        parser.error(f'Missing source: {source}')
    with tempfile.TemporaryDirectory(prefix='machine_markets_tex_') as temp:
        for pass_number in range(1, 4):
            command=[compiler, '-interaction=nonstopmode', '-halt-on-error',
                     f'-output-directory={temp}', str(source)]
            run=subprocess.run(command, cwd=temp, capture_output=True, text=True, check=False)
            if run.returncode:
                print(f'LaTeX pass {pass_number} failed:\n{run.stdout}\n{run.stderr}', file=sys.stderr)
                return run.returncode
        generated=Path(temp)/source.with_suffix('.pdf').name
        destination.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(generated,destination)
    print(f'Built: {destination}')
    return 0


if __name__=='__main__':
    sys.exit(main())
