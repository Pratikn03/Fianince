"""Package the completed revision and verify every archived file against its manifest.

Run from anywhere inside the full repository after the audit PDF is built.
No empirical study is executed by this command.
"""
from pathlib import Path
import hashlib
import json
import shutil
import zipfile

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent.parent
DELIVER = ROOT / 'pdf_delivered'
IGNORED_PARTS = {'.lake', '.venv', '__pycache__', '.pytest_cache', '.git'}
IGNORED_SUFFIXES = {'.pyc', '.pyo', '.aux', '.out', '.toc', '.fls', '.fdb_latexmk'}


def digest(data):
    return hashlib.sha256(data).hexdigest()


def included(path):
    rel = path.relative_to(HERE)
    return (path.is_file() and not set(rel.parts) & IGNORED_PARTS
            and path.suffix not in IGNORED_SUFFIXES and path.name != '.DS_Store'
            and path.name != 'MANIFEST.sha256')


def main():
    assert '{{VALIDATION}}' not in (HERE / 'Research_Audit.md').read_text()
    for name in ['Paper1_ssrn_complete.pdf', 'Paper1_ssrn_main.pdf',
                 'Paper1_ssrn_supplement.pdf', 'paper1b_companion.pdf',
                 'Paper1_Research_Audit.pdf']:
        source = DELIVER / name
        assert source.is_file(), f'Missing final deliverable: {source}'
        shutil.copy2(source, HERE / 'pdfs' / name)
    files = sorted(p for p in HERE.rglob('*') if included(p))
    checksums = {p.relative_to(HERE).as_posix(): digest(p.read_bytes()) for p in files}
    manifest = HERE / 'MANIFEST.sha256'
    manifest.write_text(''.join(f'{sha}  {name}\n' for name, sha in checksums.items()))
    archive = DELIVER / 'Paper1_Revision_Package.zip'
    with zipfile.ZipFile(archive, 'w', zipfile.ZIP_DEFLATED, compresslevel=9) as z:
        for p in [*files, manifest]:
            z.write(p, Path('Paper1_Publication_Revision') / p.relative_to(HERE))
    with zipfile.ZipFile(archive) as z:
        assert z.testzip() is None
        for name, sha in checksums.items():
            assert digest(z.read(f'Paper1_Publication_Revision/{name}')) == sha, name
    sha = digest(archive.read_bytes())
    archive.with_suffix('.zip.sha256').write_text(f'{sha}  {archive.name}\n')
    receipt = {'files_plus_manifest': len(files) + 1, 'zip_bytes': archive.stat().st_size,
               'zip_sha256': sha, 'crc_passed': True, 'all_manifest_hashes_passed': True}
    (DELIVER / 'Paper1_Package_Verification.json').write_text(json.dumps(receipt, indent=2) + '\n')
    print(json.dumps(receipt, indent=2))


if __name__ == '__main__':
    main()
