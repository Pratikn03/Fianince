"""Read-only numerical and manuscript alignment checks for the correction."""
from pathlib import Path
import argparse
import csv
import hashlib
import json
import re
import numpy as np
from research_extension.evidence_repair.render_artifacts import exact_witness
from research_extension.evidence_repair.run_learned_agents import mean_interval

ROOT = Path(__file__).resolve().parents[2]
OUT = ROOT/'research_extension/outputs/evidence_repair_20260926'


def verify_hashes(base, entries):
    for name, digest in entries.items():
        actual = hashlib.sha256((base/name).read_bytes()).hexdigest()
        if actual != digest:
            raise AssertionError(f'Hash mismatch: {base/name}')


def verify_seal(root, path):
    seal = json.loads(Path(path).read_text())
    if not seal.get('sha256'):
        raise AssertionError('Empty correction seal')
    verify_hashes(root, seal['sha256'])
    return {'status': 'passed', 'files_verified': len(seal['sha256']),
            'scope': seal['scope']}


def verify(root=ROOT):
    out = root/'research_extension/outputs/evidence_repair_20260926'
    manuscript = (root/'paper/Machine_Markets_Final_Integrated_Paper.tex').read_text()
    art = json.loads((out/'paper_artifacts.json').read_text())
    for key,value in art.items():
        if key.endswith('_tex') and value.strip() not in manuscript:
            raise AssertionError(f'Generated manuscript artifact differs: {key}')
    for idx,name in enumerate(('Stable','Unstable')):
        section = manuscript.split(f'% {name} model',1)[1].split('};',1)[0]
        values = [float(x) for x in re.findall(r'\(\d+, ([\d.]+)\)',section)]
        np.testing.assert_allclose(values, [float(x) for x in exact_witness()[idx]],atol=5e-5,rtol=0)
    primary = list(csv.DictReader((root/'studies/audited_constraints/results/linear_panels.csv').open()))
    counts = {k:sum(row[k]=='True' for row in primary) for k in ('covered','definite','wrong')}
    assert len(primary)==2880 and counts=={'covered':2758,'definite':745,'wrong':20}
    qdir=out/'learned_agents_v2'
    d=json.loads((qdir/'results.json').read_text())
    m=json.loads((qdir/'manifest.json').read_text())
    verify_hashes(root,m['source_hashes'])
    verify_hashes(qdir,m['output_hashes'])
    for p in d['policies']:
        for arm in ('q_frozen','q_active','frequency_calibrated'):
            runs=[r for r in d['raw_runs'] if r.get('policy_id')==p['policy_id'] and r['agent_type']==arm]
            assert len(runs)==10 and all(r['steps']==128 for r in runs)
            for key,number in p[arm].items():
                np.testing.assert_allclose(number,np.mean([r[key] for r in runs]),atol=1e-14,rtol=0)
        assert p['audit']['classification']=='NON_CERTIFIABLE_SUPPORT'
        assert p['response']['dq_dx'] is None
    for key in d['contrasts']:
        assert d['contrasts'][key]==mean_interval([p[key] for p in d['policies']])
    empdir=out/'empirical/final'
    em=json.loads((empdir/'manifest.json').read_text())
    for key in ('input_sha256','source_sha256'):
        verify_hashes(root,em[key])
    verify_hashes(empdir,em['output_sha256'])
    bc=json.loads((empdir/'binance_chronological_results.json').read_text())
    failed=sum(r['status']!='ok' for a in bc['asset_results'] for r in a['seed_runs'])
    assert failed==8
    gate=json.loads((out/'gate24/final/gate24_analysis_results.json').read_text())
    assert gate['meta']['status']=='PENDING_CALIBRATION'
    for item in gate['meta']['provenance']:
        verify_hashes(root,{item['path']:item['sha256']})
    for g in gate['gate4_calibrated_implementation'].values():
        radius=max(abs(np.linalg.eigvals(g['jacobian'])))
        assert abs(radius-g['spectral_radius'])<1e-13
        assert not g['execution_calibration_validated']
    return {'status':'passed','scope':'corrected artifacts and retained primary count; not every historical claim',
        'primary_panels':len(primary), 'primary_counts':counts,
        'corrective_training_populations':len(d['policies']), 'failed_binance_seeds_retained':failed,
        'external_review':False,'execution_calibration':False}


if __name__=='__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--seal', type=Path, help='Optional correction-specific hash manifest')
    args = parser.parse_args()
    result = verify()
    if args.seal:
        result['correction_seal'] = verify_seal(ROOT, args.seal)
    print(json.dumps(result,indent=2))
