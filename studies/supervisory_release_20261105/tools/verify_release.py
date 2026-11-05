"""Build/audit typed declarations and bind the receipt to the active Paper 1 sources.

This records verification evidence; it never certifies full semantic coverage,
novelty, market assumptions, independent review, or journal acceptance.
"""
from pathlib import Path
import argparse
import datetime
import hashlib
import json
import os
import re
import subprocess


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--project', type=Path, required=True)
    parser.add_argument('--repo', type=Path, required=True)
    args = parser.parse_args()
    project = args.project.resolve()
    root = args.repo.resolve()
    entries = []
    for path in sorted((project / 'CurrentProofs').glob('*.lean')):
        source = path.read_text()
        if re.search(r'^\s*(axiom|constant)\s', source, re.M):
            raise AssertionError(path)
        if re.search(r'\b(sorry|admit|native_decide)\b', source):
            raise AssertionError(path)
        for match in re.finditer(r'^theorem\s+([A-Za-z0-9_]+)', source, re.M):
            entries.append({'name': 'CurrentMM.' + match[1], 'source': str(path.relative_to(project)), 'line': source[:match.start()].count('\n') + 1})
    audit = (project / 'AxiomAudit.lean').read_text()
    start = audit.index('  let names : Array Name := #[')
    end = audit.index('  let mut allConstantCount', start)
    audit = audit[:start] + '  let names : Array Name := #[\n  ' + ',\n  '.join('`' + row['name'] for row in entries) + ']\n' + audit[end:]
    audit_path = project / 'Paper1ReleaseAudit.lean'
    audit_path.write_text(audit)
    for command, name in [(['lake', 'build'], 'paper1_release_build.log'), (['lake', 'env', 'lean', 'Paper1ReleaseAudit.lean'], 'paper1_release_axioms.log')]:
        with (project / name).open('w') as handle:
            try:
                subprocess.run(command, cwd=project, env=os.environ.copy(), stdout=handle, stderr=subprocess.STDOUT, check=True, timeout=1800)
            except subprocess.CalledProcessError:
                handle.flush()
                print((project / name).read_text()[-20000:])
                raise
    rows = [json.loads(line) for line in (project / 'paper1_release_axioms.log').read_text().splitlines() if line.startswith('{"')]
    named = [row for row in rows if row['kind'] == 'named_theorem']
    summaries = [row for row in rows if row['kind'] == 'audit_summary']
    assert len(summaries) == 1
    assert {row['name'] for row in named} == {row['name'] for row in entries}
    allowed = {'propext', 'Classical.choice', 'Quot.sound'}
    assert all(set(row['axioms']) <= allowed for row in named)
    new_files = {'CurrentProofs/Paper1GaussRadau.lean', 'CurrentProofs/Paper1SupervisoryDecision.lean',
                 'CurrentProofs/Paper1FlowDecision.lean', 'CurrentProofs/Paper1ClaimRepairs.lean'}
    new_names = {entry['name'] for entry in entries if entry['source'] in new_files}
    new_types = [row for row in named if row['name'] in new_names]
    mathlib = subprocess.check_output(['git', '-C', str(project / '.lake/packages/mathlib'), 'rev-parse', 'HEAD'], text=True).strip()
    assert mathlib == 'd13f23b723b8a846827a245b89c10fc7d3f11612'
    manuscript_paths = [root / 'ceiling_suite/papers/paper1' / name for name in ['paper1.tex', 'paper1_ssrn.tex', 'p1_front.tex', 'p1_disclosure.tex', 'p1_appendix.tex']]
    manuscript_paths += sorted((root / 'ceiling_suite/papers/paper1/dev_register').glob('*.tex'))
    manuscript_paths += sorted((root / 'ceiling_suite/papers/paper1/figs').glob('*.pdf'))
    receipt = {'status': 'FULL_PROJECT_BUILD_AND_STRICT_AXIOM_AUDIT_PASS', 'timestamp_utc': datetime.datetime.now(datetime.timezone.utc).isoformat(), 'lean_version': subprocess.check_output(['lake', 'env', 'lean', '--version'], cwd=project, text=True).strip(), 'mathlib_commit': mathlib, 'named_declarations': len(named), 'project_constants_scanned': summaries[0]['project_constants_scanned'], 'new_release_theorems': len(new_types), 'new_theorem_types': new_types, 'observed_axioms': sorted(set().union(*(set(row['axioms']) for row in named))), 'manuscript_source_sha256': {str(p.relative_to(root)): sha(p) for p in manuscript_paths}, 'formal_source_sha256': {str(p.relative_to(project)): sha(p) for p in sorted((project / 'CurrentProofs').glob('*.lean'))}, 'root_imports_sha256': sha(project / 'CurrentProofs.lean'), 'audit_source_sha256': sha(audit_path), 'audit_log_sha256': sha(project / 'paper1_release_axioms.log'), 'verification_script_sha256': sha(Path(__file__)), 'full_manuscript_formalization_complete': False, 'semantic_scope': ['Exact K=2 Gauss/Radau witness moments, intensity gap, aggregate gap and finite-Gaussian-record lower bound.', 'Actual product-Gaussian unsafe-halt event bound for a conservative Chebyshev gate.', 'Robust threshold/fallback and fixed-menu economic acquisition algebra.', 'Tagged-flow inversion, interval clipping, intensity intervals, selected-halt soundness and a Gaussian probability composition conditional on rule soundness.', 'Conditional pricing sensitivity, finite-share account count and camouflage profit/cost algebra; economic premises are maintained assumptions.'], 'limits': ['The all-K supervisory weight-gap construction is not supplied.', 'The normal-quantile numerical gate is not the conservative gate formalized here.', 'Scalar budget readings are an assumed measurement contract, not class-position or tagged-flow identification.', 'The direct-flow contract assumes reset observations, known impact, stable verified labels and a declared persistence class; full executable-rule correspondence remains open.', 'Inherited manuscript mappings are not automatically semantically re-audited.', 'Market calibration, independent proof review and novelty are not certified.']}
    (project / 'paper1_release_receipt.json').write_text(json.dumps(receipt, indent=2) + '\n')
    (project / 'paper1_release_axioms.jsonl').write_text('\n'.join(json.dumps(row) for row in rows) + '\n')
    print(json.dumps({key: receipt[key] for key in ['status', 'named_declarations', 'project_constants_scanned', 'new_release_theorems', 'full_manuscript_formalization_complete']}, indent=2))


if __name__ == '__main__':
    main()

