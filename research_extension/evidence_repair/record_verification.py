"""Record fresh checks and a separately scoped correction seal; never overwrite."""
from pathlib import Path
import argparse
import hashlib
import json
import platform
import subprocess
import sys
from datetime import datetime, timezone

ROOT = Path(__file__).resolve().parents[2]
OUT = Path('research_extension/outputs/evidence_repair_20260926')


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def compare_clean(clean):
    pairs = [('learned_agents_v2/results.json', 'clean_reproduction/results.json'),
             ('empirical/final/coinbase_audit.json', 'empirical/clean-reproduction/coinbase_audit.json'),
             ('empirical/final/binance_chronological_results.json', 'empirical/clean-reproduction/binance_chronological_results.json')]
    matches = {}
    for original, reproduced in pairs:
        left, right = ROOT/OUT/original, clean/OUT/reproduced
        assert left.read_bytes() == right.read_bytes(), original
        matches[original] = {'identical_bytes': True, 'sha256': digest(left)}
    a = json.loads((ROOT/OUT/'gate24/final/gate24_analysis_results.json').read_text())
    b = json.loads((clean/OUT/'gate24/clean-reproduction/gate24_analysis_results.json').read_text())
    for key in ('gate2_authenticated_boundary', 'gate3_costed_observations'):
        assert a[key] == b[key], key
    for name, old in a['gate4_calibrated_implementation'].items():
        new = b['gate4_calibrated_implementation'][name]
        for key in old:
            if key not in ('verdict', 'capacity_sensitivity'):
                assert old[key] == new[key], (name, key)
        # A reporting-only schema change exposes co-varying capital/noise.
        for scale, values in old['capacity_sensitivity'].items():
            current = new['joint_scale_diagnostic']['scales'][scale]
            for key, value in values.items():
                assert value == current[key], (name, scale, key)
            assert abs(current['noise_std_base'] - .05*current['capacity_units']) < 1e-13
    matches['gate24'] = {'numerical_match': True, 'byte_match': False,
        'differences': 'joint-scale schema/disclosure, source hashes, absolute sidecar path',
        'clean_result_sha256': digest(clean/OUT/'gate24/clean-reproduction/gate24_analysis_results.json')}
    paper = ROOT/'paper/Machine_Markets_Final_Integrated_Paper.pdf'
    rebuilt = clean/'tmp/clean_rebuilt_paper.pdf'
    original_text = subprocess.check_output(['pdftotext', '-layout', str(paper), '-'])
    rebuilt_text = subprocess.check_output(['pdftotext', '-layout', str(rebuilt), '-'])
    assert original_text == rebuilt_text, 'Clean-copy PDF text differs'
    matches['main_pdf'] = {'extracted_layout_text_identical': True,
        'text_sha256': hashlib.sha256(original_text).hexdigest(),
        'scope': 'Text/layout extraction comparison, not byte-identical PDF metadata or pixel equality'}
    return matches


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--clean-root', required=True, type=Path)
    parser.add_argument('--output-dir', required=True, type=Path)
    args = parser.parse_args()
    dest = args.output_dir.resolve()
    dest.relative_to(ROOT)
    if dest.exists():
        parser.error('Refusing to overwrite verification evidence')
    dest.mkdir(parents=True)
    receipts = []

    def run(name, command, cwd=ROOT, expected=0):
        process = subprocess.run(command, cwd=cwd, capture_output=True, text=True)
        log = dest/f'{name}.txt'
        log.write_text(process.stdout + '\n' + process.stderr)
        receipts.append({'name': name, 'command': command, 'cwd': str(cwd),
                         'exit_code': process.returncode, 'expected_exit': expected,
                         'log': str(log.relative_to(ROOT))})
        if process.returncode != expected:
            raise RuntimeError(f'{name} failed; inspect {log}')
        return process.stdout

    pytest_args = [sys.executable, '-m', 'pytest', '-q', 'tests',
                   'research_extension/tests', 'reference_directory/test_mathematical_supplement.py']
    run('pytest', pytest_args)
    run('pytest_clean', pytest_args, args.clean_root.resolve())
    run('native', [sys.executable, 'tools/run_all_tests.py', '--log-dir', str(dest/'native')])
    run('algebra', [sys.executable, 'reference_directory/run_checks.py'])
    alignment = json.loads(run('evidence_alignment', [sys.executable, '-m', 'research_extension.evidence_repair.check_evidence']))
    run('diff_check', ['git', 'diff', '--check'])
    run('historical_strict_seal', [sys.executable, 'tools/verify_master.py', '--strict'], expected=1)
    matches = compare_clean(args.clean_root.resolve())
    native = json.loads((dest/'native/test_report.json').read_text())
    main_ref = run('main_ref', ['git', 'rev-parse', 'main']).strip()
    assert main_ref == '1ec937cc512a12f8a36e887c20ce721bf675d87e'
    pdfs = {}
    for stem in ('Machine_Markets_Final_Integrated_Paper', 'Machine_Markets_Mathematical_Supplement'):
        path = ROOT/'paper'/f'{stem}.pdf'
        info = run(f'{stem}_pdfinfo', ['pdfinfo', str(path)])
        pages = int(next(line.split(':', 1)[1] for line in info.splitlines() if line.startswith('Pages:')))
        pdfs[stem] = {'pages': pages, 'pdf_sha256': digest(path),
                      'tex_sha256': digest(path.with_suffix('.tex'))}
    receipt = {'created_utc': datetime.now(timezone.utc).isoformat(),
        'python': platform.python_version(), 'branch': run('branch', ['git', 'branch', '--show-current']).strip(),
        'starting_and_main_commit': main_ref, 'commands': receipts,
        'native_scientific_tests': native['scientific_tests'], 'native_release_tests': native['release_tool_tests'],
        'clean_copy': str(args.clean_root.resolve()), 'reproduction': matches,
        'corrected_evidence': alignment, 'documents': pdfs,
        'historical_strict_seal': 'FAILS; old seal unchanged, not a certificate for the revised checkout',
        'human_independent_review': False, 'real_execution_calibration': False,
        'scope': 'Corrective implementation, regenerated studies, main/supplement build and listed-file integrity; not every historical claim'}
    (dest/'verification.json').write_text(json.dumps(receipt, indent=2)+'\n')

    paths = set()
    def add_tree(directory):
        paths.update(p for p in directory.rglob('*') if p.is_file()
                     and '__pycache__' not in p.parts and p.suffix != '.pyc')
    for name in ('Machine_Markets_Final_Integrated_Paper', 'Machine_Markets_Mathematical_Supplement'):
        paths.update(ROOT/'paper'/f'{name}.{suffix}' for suffix in ('tex', 'pdf'))
    for directory in ('research_extension/evidence_repair', 'research_extension/mm_revision',
                      'research_extension/learned_agents', 'tests'):
        for path in (ROOT/directory).rglob('*'):
            if path.is_file() and path.suffix in ('.py', '.md', '.json'):
                paths.add(path)
    for directory in ('learned_agents_v2', 'empirical/final'):
        add_tree(ROOT/OUT/directory)
    for file in ('gate24/gate24_summary.json', 'gate24/final/gate24_analysis_results.json', 'paper_artifacts.json'):
        paths.add(ROOT/OUT/file)
    for file in ('research_extension/binance_multi_epoch_study.py',
                 'research_extension/gate24_public_data/gate24_analysis.py',
                 'research_extension/gate24_public_data/download_public_data.py',
                 'studies/audited_constraints/src/inference.py',
                 'studies/audited_constraints/results/linear_panels.csv',
                 'studies/audited_constraints/results/linear_summary.json'):
        paths.add(ROOT/file)
    add_tree(dest)
    manifest = {'created_utc': receipt['created_utc'],
        'scope': 'Explicitly listed correction source, tests, paper source/PDF, result and verification files; not unlisted files or external authenticity',
        'sha256': {str(p.relative_to(ROOT)): digest(p) for p in sorted(paths)}}
    (dest/'correction_manifest.json').write_text(json.dumps(manifest, indent=2)+'\n')
    print(json.dumps({'status': 'recorded', 'files_sealed': len(paths),
                      'verification': str(dest/'verification.json'), 'documents': pdfs}, indent=2))


if __name__ == '__main__':
    main()
